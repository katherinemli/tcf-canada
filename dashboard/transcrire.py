#!/usr/bin/env python3
# ============================================================
# Transcription d'un enregistrement audio — 100 % hors ligne, gratuit.
#
# Utilise faster-whisper (le modèle tourne sur TON ordinateur : aucune
# clé API, aucun envoi sur Internet, aucun coût).
#
# Ce fichier n'est PAS lancé directement : c'est serveur_eval.py qui
# l'appelle, avec le python du dossier .venv-whisper/ (voir PYTHON_WHISPER).
#
# À la main, pour tester :
#     .venv-whisper/bin/python transcrire.py mes_audios/mon_fichier.webm
#
# Sortie : un objet JSON sur la sortie standard.
#     {"ok": true, "texte": "...", "mots": 87, "duree": 118.4, "debit": 44}
# ============================================================

import json
import os
import sys

# Modèle Whisper. « small » est le bon compromis pour le français sur un
# processeur : ~500 Mo, et environ 30 à 60 s pour un enregistrement de 4 min.
#   - « base »  : 3× plus rapide, mais confond beaucoup de mots ;
#   - « medium »: nettement meilleur, mais 3× plus lent et 1,5 Go.
# Modifiable sans toucher au code : TCF_MODELE_WHISPER=medium
MODELE = os.environ.get("TCF_MODELE_WHISPER", "small")


def transcrire(chemin):
    """Transcrit un fichier audio en français et renvoie le texte + des mesures.

    Le débit (mots par minute) est renvoyé parce que c'est un vrai critère
    du TCF : un débit très bas trahit les hésitations. Repère utile :
    120-150 mots/min = fluide, moins de 80 = hésitant.
    """
    from faster_whisper import WhisperModel

    # int8 = calcul en entiers : 3 à 4× plus rapide sur processeur, avec
    # une perte de qualité imperceptible pour de la parole.
    modele = WhisperModel(MODELE, device="cpu", compute_type="int8")

    segments, info = modele.transcribe(
        chemin,
        language="fr",
        beam_size=5,
        # Coupe les silences : sans ça, Whisper invente du texte pendant les
        # blancs (« Sous-titres réalisés par… ») — fréquent quand on hésite.
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
    )

    morceaux = [s.text.strip() for s in segments]
    texte = " ".join(m for m in morceaux if m).strip()
    mots = len(texte.split()) if texte else 0
    duree = float(info.duration or 0)
    debit = round(mots / (duree / 60)) if duree > 0 else 0

    return {"ok": True, "texte": texte, "mots": mots,
            "duree": round(duree, 1), "debit": debit}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "message": "Fichier audio manquant."}))
        return 1
    chemin = sys.argv[1]
    if not os.path.isfile(chemin):
        print(json.dumps({"ok": False, "message": f"Fichier introuvable : {chemin}"}))
        return 1
    try:
        resultat = transcrire(chemin)
    except Exception as e:  # modèle absent, audio illisible, mémoire…
        resultat = {"ok": False, "message": f"Transcription impossible : {e}"}
    print(json.dumps(resultat, ensure_ascii=False))
    return 0 if resultat.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
