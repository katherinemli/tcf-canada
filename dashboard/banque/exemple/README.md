# Un exemple de la banque

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
