#!/usr/bin/env python3
# ENVOYER UN FICHIER DU PC VERS LE TÉLÉPHONE (le trajet inverse de l'appli)
#
#   python3 envoyer_au_telephone.py mes_simulation_expression_oral/tache-3_....m4a
#   python3 envoyer_au_telephone.py fichier1.m4a fichier2.m4a --minutes 30
#
# Sur le téléphone : WiFi « TCF-PC », puis Safari → http://10.42.0.1:8777
#
# POURQUOI CE SCRIPT ET PAS « python3 -m http.server » :
#   • http.server publierait TOUT le dossier au téléphone. Ici, seuls les
#     fichiers écrits sur la ligne de commande existent — le reste est un 404,
#     même si on devine le nom.
#   • On n'écoute que sur 10.42.0.1 (l'antenne du point d'accès). Le réseau de
#     l'entreprise, lui, n'a même pas de porte à laquelle frapper.
#   • Port 8777 : hotspot.sh n'ouvre que celui-là. Un autre port serait bloqué
#     par le pare-feu, et l'ouvrir voudrait dire une porte de plus à surveiller.
#   • Il s'éteint tout seul, comme le point d'accès : on ne peut pas l'oublier.

import http.server
import html
import os
import socket
import sys
import threading
import urllib.parse

IP = "10.42.0.1"          # l'antenne du point d'accès, et elle seule
PORT = 8777               # le seul port que le pare-feu laisse passer

def analyser_arguments(args):
    """Sépare les chemins de l'option --minutes."""
    minutes, chemins = 15, []
    i = 0
    while i < len(args):
        if args[i] in ("--minutes", "-m") and i + 1 < len(args):
            minutes = int(args[i + 1]); i += 2
        else:
            chemins.append(args[i]); i += 1
    return chemins, minutes


def faire_gestionnaire(catalogue):
    """catalogue : {nom affiché → chemin absolu}. Rien d'autre n'est servi."""

    class Gestionnaire(http.server.BaseHTTPRequestHandler):

        def do_GET(self):
            # Le téléphone a une adresse en 10.42.x ; tout le reste est refusé.
            if not self.client_address[0].startswith("10.42."):
                self.send_error(403, "Reserve au point d'acces")
                return

            chemin = urllib.parse.unquote(self.path.split("?")[0])
            if chemin == "/":
                self.page_accueil()
            elif chemin.lstrip("/") in catalogue:
                self.envoyer_fichier(chemin.lstrip("/"))
            else:
                self.send_error(404, "Fichier non propose")

        def page_accueil(self):
            # Une page volontairement grosse : on la touche du doigt, à bout de
            # bras, sur un écran de téléphone.
            liens = "".join(
                f'<a href="/{urllib.parse.quote(n)}">⬇︎ {html.escape(n)}'
                f'<span>{os.path.getsize(catalogue[n]) // 1024} Ko</span></a>'
                for n in catalogue)
            page = f"""<!doctype html><html lang="fr"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fichiers du PC</title><style>
body{{font-family:-apple-system,sans-serif;margin:0;padding:24px;
background:#f6f6f8;color:#111}}
h1{{font-size:1.2rem;margin:0 0 4px}}
p{{color:#666;font-size:.9rem;margin:0 0 20px}}
a{{display:flex;justify-content:space-between;align-items:center;gap:12px;
background:#fff;border-radius:14px;padding:18px 20px;margin-bottom:12px;
text-decoration:none;color:#0a58ca;font-size:1.05rem;font-weight:600;
box-shadow:0 1px 3px rgba(0,0,0,.08)}}
span{{color:#888;font-weight:400;font-size:.85rem;white-space:nowrap}}
</style><h1>Fichiers envoyés par le PC</h1>
<p>Touche un fichier → « Télécharger » → il arrive dans l'app <b>Fichiers</b>,
dossier <b>Téléchargements</b>.</p>{liens}</html>"""
            corps = page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(corps)))
            self.end_headers()
            self.wfile.write(corps)

        def envoyer_fichier(self, nom):
            chemin = catalogue[nom]
            taille = os.path.getsize(chemin)
            self.send_response(200)
            # « attachment » : sans ça, Safari ouvre le son dans son lecteur au
            # lieu de le ranger dans Fichiers — et il n'en reste rien après.
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition",
                             f'attachment; filename="{nom}"')
            self.send_header("Content-Length", str(taille))
            self.end_headers()
            with open(chemin, "rb") as f:
                while bloc := f.read(64 * 1024):
                    self.wfile.write(bloc)
            print(f"   ✅ {nom} envoyé à {self.client_address[0]}", flush=True)
            # Le port 8777 est aussi celui de serveur_eval.py : on le rend dès
            # que le fichier est parti. Les 20 secondes laissent le temps de
            # toucher un second fichier, ou de refaire un essai qui a raté.
            # 10.42.0.1, c'est le PC qui s'appelle lui-même pour vérifier que
            # le serveur répond : un essai n'est pas une livraison.
            if self.client_address[0] != IP:
                fin = threading.Timer(20, self.server.shutdown)
                fin.daemon = True
                fin.start()

        def log_message(self, *a):
            pass  # on n'affiche que ce qui compte : les fichiers partis

    return Gestionnaire


def main():
    chemins, minutes = analyser_arguments(sys.argv[1:])
    if not chemins:
        print(__doc__ or "Usage : python3 envoyer_au_telephone.py <fichier…>")
        sys.exit(1)

    catalogue = {}
    for c in chemins:
        c = os.path.abspath(os.path.expanduser(c))
        if not os.path.isfile(c):
            print(f"❌ Introuvable : {c}"); sys.exit(1)
        catalogue[os.path.basename(c)] = c

    try:
        serveur = http.server.ThreadingHTTPServer(
            (IP, PORT), faire_gestionnaire(catalogue))
    except OSError as e:
        if e.errno == 98:      # port déjà pris
            print(f"❌ Le port {PORT} est déjà utilisé — c'est sans doute\n"
                  f"   serveur_eval.py. Arrête-le, puis relance ce script.")
        elif e.errno == 99:    # adresse absente
            print(f"❌ {IP} n'existe pas : le point d'accès est éteint.\n"
                  f"   Lance d'abord :  bash ~/tcf_oral_app/hotspot.sh")
        else:
            print(f"❌ {e}")
        sys.exit(1)

    print(f"📤 Prêt. Sur le téléphone (WiFi « TCF-PC ») ouvre Safari :")
    print(f"      http://{IP}:{PORT}")
    for n in catalogue:
        print(f"   • {n}")
    print(f"   ⏱  S'arrête tout seul dans {minutes} min (ou Ctrl-C).")

    extinction = threading.Timer(minutes * 60, serveur.shutdown)
    extinction.daemon = True   # sinon il retient le processus, et le port avec
    extinction.start()
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        pass
    print("📴 Serveur d'envoi arrêté.")


if __name__ == "__main__":
    main()
