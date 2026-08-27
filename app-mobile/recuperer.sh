#!/bin/bash
# Rapatrie les enregistrements du téléphone dans tcf_simulateur/mes_audios/,
# là où Whisper et l'évaluation savent déjà les lire.
#
#   bash recuperer.sh           → copie ce qui est nouveau
#   bash recuperer.sh --vider   → copie, puis efface du téléphone
cd "$(dirname "$0")"
ADB=~/android-min/platform-tools/adb
SOURCE=/sdcard/TCF_oral
CIBLE=~/tcf_simulateur/mes_audios
TAMPON=$(mktemp -d)
trap 'rm -rf "$TAMPON"' EXIT

if [ -z "$($ADB devices | grep -w device)" ]; then
    echo "❌ Téléphone non branché (ou débogage USB pas activé) — voir installer.sh"
    exit 1
fi

mkdir -p "$CIBLE"
$ADB pull -a "$SOURCE" "$TAMPON" >/dev/null 2>&1 || { echo "❌ Rien à récupérer dans $SOURCE"; exit 1; }

nouveaux=0
for f in "$TAMPON"/TCF_oral/*.m4a; do
    [ -e "$f" ] || continue
    nom=$(basename "$f")
    if [ -e "$CIBLE/$nom" ]; then continue; fi
    cp -p "$f" "$CIBLE/$nom"
    echo "  ↓ $nom  ($(du -h "$CIBLE/$nom" | cut -f1))"
    nouveaux=$((nouveaux + 1))
done

echo "✅ $nouveaux nouvel(s) enregistrement(s) dans mes_audios/"
[ $nouveaux -gt 0 ] && echo "   → http://localhost:8777 · 🎧 Mes enregistrements · « Écrire ce que j'ai dit »"

if [ "$1" = "--vider" ] && [ $nouveaux -ge 0 ]; then
    $ADB shell "rm -f $SOURCE/*.m4a"
    echo "🧹 Téléphone vidé."
fi
