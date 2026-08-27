#!/bin/bash
# Point d'accès WiFi du PC pour recevoir les enregistrements du téléphone.
#
#   bash hotspot.sh          → l'allume, l'isole, et s'éteint seul après 20 min
#   bash hotspot.sh 45       → pareil, mais 45 minutes
#   bash hotspot.sh stop     → l'éteint tout de suite et retire l'isolement
#
# SÉCURITÉ (PC de l'entreprise) :
#   • WPA2 avec mot de passe — ce n'est PAS un réseau ouvert.
#   • Le téléphone ne peut atteindre QU'UN SEUL port du PC : 8777 (le serveur
#     TCF, lui-même protégé par une clé). SSH, Samba, et tout le reste des
#     services de l'entreprise lui sont fermés — même s'il connaissait le mot
#     de passe WiFi. C'est le verrou important : le mot de passe WiFi protège
#     la porte, ces règles-ci vident la pièce derrière.
#   • Il ne peut pas non plus TRAVERSER le PC vers le réseau de l'entreprise.
#   • Il s'éteint tout seul : on ne peut pas l'oublier allumé.
#
# Les règles visent le sous-réseau 10.42.x, pas l'antenne : si l'antenne sert
# plus tard de WiFi normal, d'anciennes règles oubliées ne gênent rien.

SSID="TCF-PC"
# Mot de passe WPA2 : jamais écrit dans ce fichier (dépôt public).
# Il est lu depuis ~/.tcf-hotspot-mdp (chmod 600) ou la variable TCF_HOTSPOT_MDP.
MDP="${TCF_HOTSPOT_MDP:-}"
if [ -z "$MDP" ] && [ -f "$HOME/.tcf-hotspot-mdp" ]; then
    MDP=$(tr -d '\r\n' < "$HOME/.tcf-hotspot-mdp")
fi
if [ ${#MDP} -lt 8 ]; then
    echo "Mot de passe du hotspot manquant (≥ 8 caractères). Crée-le une fois :" >&2
    echo "  printf '%s' 'ton-mot-de-passe' > ~/.tcf-hotspot-mdp && chmod 600 ~/.tcf-hotspot-mdp" >&2
    exit 1
fi
ANTENNE="wlxe84e06ac9c70"     # antenne WiFi USB (Realtek RTL8821CU)
RESEAU="10.42.0.0/24"
PORT=8777                     # le SEUL port ouvert au téléphone
MINUTES="${1:-20}"            # extinction automatique

# Retrouve l'antenne même si le nom change.
if ! nmcli -t -f DEVICE,TYPE device 2>/dev/null | grep -q "^$ANTENNE:wifi"; then
    AUTRE=$(nmcli -t -f DEVICE,TYPE device 2>/dev/null | awk -F: '$2=="wifi"{print $1; exit}')
    [ -n "$AUTRE" ] && ANTENNE="$AUTRE"
fi

# Les règles d'isolement. Deux précisions qui comptent :
#
#  • « -i $ANTENNE » : sans ça, la règle attrape aussi l'ordinateur qui se parle
#    à lui-même via 10.42.0.1 (le trafic passe par « lo »), et le PC ne peut plus
#    joindre son propre serveur. C'est arrivé — le ping échouait sur sa propre IP.
#  • « -s $RESEAU » : ainsi, le jour où cette antenne sert de WiFi normal, une
#    règle oubliée ne bloque rien (la source ne sera plus en 10.42.x).
#
# L'ordre compte : les ACCEPT doivent passer AVANT le DROP final, donc on les
# insère en dernier (-I place toujours en tête).
REGLES_INPUT=(
    "-i $ANTENNE -s $RESEAU -j DROP"                        # tout est fermé…
    "-i $ANTENNE -s $RESEAU -p udp --dport 53 -j ACCEPT"    # …sauf le DNS
    "-i $ANTENNE -s $RESEAU -p udp --dport 67 -j ACCEPT"    # …sauf le bail DHCP
    "-i $ANTENNE -s $RESEAU -p tcp --dport $PORT -j ACCEPT" # …sauf le serveur TCF
)
REGLES_FORWARD=(
    "-s $RESEAU -j DROP"                          # le téléphone ne traverse pas
    "-d $RESEAU -j DROP"                          # et rien ne vient vers lui
)

# Règles des versions précédentes du script : on les retire aussi, sinon elles
# restent en place et continuent de bloquer.
ANCIENNES_INPUT=(
    "-s $RESEAU -j DROP"
    "-s $RESEAU -p udp --dport 53 -j ACCEPT"
    "-s $RESEAU -p udp --dport 67 -j ACCEPT"
    "-s $RESEAU -p tcp --dport $PORT -j ACCEPT"
)

# Retire d'éventuelles anciennes règles (pour ne pas les empiler).
nettoyer_pare_feu() {
    for R in "${REGLES_INPUT[@]}" "${ANCIENNES_INPUT[@]}"; do
        while sudo iptables -C INPUT $R 2>/dev/null; do
            sudo iptables -D INPUT $R; done
    done
    for R in "${REGLES_FORWARD[@]}"; do
        while sudo iptables -C FORWARD $R 2>/dev/null; do
            sudo iptables -D FORWARD $R; done
    done
    # anciennes règles par interface, des versions précédentes du script
    while sudo iptables -C FORWARD -i "$ANTENNE" -j DROP 2>/dev/null; do
        sudo iptables -D FORWARD -i "$ANTENNE" -j DROP; done
    while sudo iptables -C FORWARD -o "$ANTENNE" -j DROP 2>/dev/null; do
        sudo iptables -D FORWARD -o "$ANTENNE" -j DROP; done
}

if [ "$1" = "stop" ]; then
    nettoyer_pare_feu 2>/dev/null
    nmcli connection down Hotspot >/dev/null 2>&1
    nmcli connection delete Hotspot >/dev/null 2>&1
    echo "📴 Point d'accès éteint, isolement retiré."
    exit 0
fi

nmcli radio wifi on
if nmcli device wifi hotspot ifname "$ANTENNE" ssid "$SSID" password "$MDP" 2>&1 | grep -qi error; then
    echo "❌ Impossible d'allumer le point d'accès sur $ANTENNE."
    exit 1
fi

# --- Isolement ---------------------------------------------------------------
# Deux verrous : le téléphone ne traverse pas le PC (FORWARD), et il ne voit
# qu'un seul port DU PC (INPUT). Sans le second, un intrus qui aurait le mot de
# passe WiFi arriverait sur SSH et Samba d'un ordinateur d'entreprise.
echo "🔒 Isolement du réseau (mot de passe sudo demandé une fois)…"
nettoyer_pare_feu
ISOLE="oui"
for R in "${REGLES_FORWARD[@]}"; do
    sudo iptables -I FORWARD $R || ISOLE="NON"
done
for R in "${REGLES_INPUT[@]}"; do
    sudo iptables -I INPUT $R || ISOLE="NON"
done

IP=$(ip -4 -o addr show "$ANTENNE" 2>/dev/null | awk '{print $4}' | cut -d/ -f1)
[ -z "$IP" ] && IP="10.42.0.1"
echo
echo "📶 Point d'accès allumé (WPA2, réseau fermé)."
echo "   • Téléphone → WiFi : $SSID   ·   mot de passe : $MDP"
echo "   • L'appli envoie vers http://$IP:$PORT — rien à toucher."
if [ "$ISOLE" = "oui" ]; then
    echo "   • 🔒 Le téléphone n'atteint QUE le port $PORT de ce PC."
    echo "        SSH, Samba et les services de l'entreprise lui sont fermés."
else
    echo "   • ⚠️  Isolement NON appliqué (sudo refusé). Éteins le point d'accès"
    echo "         et relance avec ton mot de passe — sans ces règles, le WiFi"
    echo "         donne accès à SSH et Samba de ce PC."
fi

# --- Extinction automatique ---------------------------------------------------
# Le vrai risque n'est pas l'intrus : c'est d'oublier le point d'accès allumé
# toute la nuit. On coupe l'émission tout seul. Les règles de pare-feu, elles,
# ne visent que 10.42.x : les laisser en place ne gêne rien.
( sleep $((MINUTES * 60))
  nmcli connection down Hotspot >/dev/null 2>&1
  nmcli connection delete Hotspot >/dev/null 2>&1 ) >/dev/null 2>&1 &
disown 2>/dev/null

echo "   • ⏱  S'éteint tout seul dans $MINUTES minutes (bash hotspot.sh 45 pour plus)."
echo "   • Éteindre maintenant : bash hotspot.sh stop"
