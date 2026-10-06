# Un exemple de la banque

**[Français](#français) · [English](#english)**

---

## Français

Ce dossier contient **une seule** question, avec son audio et son image, pour
montrer le format que produisent `construire_banque.py` et `integrer_fuck.py`.

```
questions_O.exemple.json   la question (énoncé, options, réponse, transcription
                           alignée mot à mot avec des timecodes)
40.mp3                     l'audio correspondant
40.webp                    l'image correspondante
```

La banque réelle — 991 questions et ~1,3 Go d'audio — **n'est pas dans ce
dépôt** : ce sont des contenus qui appartiennent aux sites d'où ils viennent.
Les scripts la reconstruisent, un jeton d'accès est à fournir en variable
d'environnement (voir `../../README.md`).

Le champ `segments` est produit par Whisper (`transcrire.py`) : il permet de
surligner la transcription en même temps que l'audio joue.

---

## English

This folder contains **a single** question, with its audio and image, to show
the format produced by `construire_banque.py` and `integrer_fuck.py`.

```
questions_O.exemple.json   the question (prompt, options, answer, transcript
                           aligned word by word with timecodes)
40.mp3                     the matching audio
40.webp                    the matching image
```

The real bank — 991 questions and ~1.3 GB of audio — **is not in this
repository**: that content belongs to the sites it comes from. The scripts
rebuild it; an access token must be provided as an environment variable (see
`../../README.md`).

The `segments` field is produced by Whisper (`transcrire.py`): it highlights the
transcript in sync with the audio as it plays.
