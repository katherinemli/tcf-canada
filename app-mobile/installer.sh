#!/bin/bash
# Installe TCF-Oral.apk sur le Honor 9 branché en USB.
#   bash installer.sh
cd "$(dirname "$0")"
ADB=~/android-min/platform-tools/adb

if [ ! -f TCF-Oral.apk ]; then
    echo "Pas d'APK — je le fabrique d'abord…"; bash construire.sh || exit 1
fi

echo "🔌 Je cherche le téléphone…"
$ADB start-server >/dev/null 2>&1
$ADB wait-for-device &
ATTENTE=$!
sleep 10 && kill $ATTENTE 2>/dev/null &
wait $ATTENTE 2>/dev/null

if [ -z "$($ADB devices | grep -w device)" ]; then
    cat <<'FIN'
❌ Je ne vois pas le téléphone.

Sur le Honor 9, une seule fois :
  1. Paramètres → À propos du téléphone → toucher 7 fois « Numéro de build »
  2. Paramètres → Système → Options de développement → activer « Débogage USB »
  3. Rebrancher le câble, et sur le téléphone : « Autoriser le débogage USB ? » → OK
     (cocher « Toujours autoriser »)

Si le téléphone est en mode « Charge seulement », passer en « Transfert de fichiers ».
FIN
    exit 1
fi

echo "📲 Installation…"
$ADB install -r TCF-Oral.apk && echo "✅ C'est installé — l'icône « TCF Oral » est sur le téléphone."
