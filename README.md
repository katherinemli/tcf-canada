# 🇨🇦 TCF Canada — mon entraînement complet

Ce dépôt réunit les deux moitiés de ma préparation au TCF Canada
(examen : **27 septembre 2026**) : un tableau de bord sur le PC et une appli
Android sur un vieux téléphone. Tout fonctionne **hors ligne**, sans compte et
sans clé API payante.

```
tcf-canada/
├── dashboard/     Tableau de bord PC — compréhension orale, expression écrite,
│                  banque de questions, serveur d'évaluation local
└── app-mobile/    Appli Android — expression orale, chronomètre + enregistrement
```

## Comment les deux morceaux travaillent ensemble

Le **téléphone** est le maître de l'expression orale : il tire le sujet au sort
hors ligne et il enregistre ma voix au temps exact de l'examen. Le **PC** ne sert
qu'à recevoir les enregistrements et à les analyser.

```
   ┌──────────────┐   hotspot WiFi du PC, port 8777    ┌─────────────┐
   │  app-mobile  │ ─────── « Envoyer au PC » ───────▶ │  dashboard  │
   │  (Honor 9)   │ ◀────── « Récupérer le sujet » ─── │    (PC)     │
   └──────────────┘                                    └─────────────┘
```

Le hotspot est cloisonné (le téléphone ne voit que le port 8777, il ne traverse
pas le PC vers le réseau) et s'éteint tout seul au bout de 20 minutes.

## Démarrer

| Je veux… | Commande |
|---|---|
| Le tableau de bord | ouvrir <http://localhost:8777> (service systemd, voir `dashboard/README.md`) |
| M'entraîner à l'oral | l'appli sur le téléphone, rien à lancer |
| Ouvrir le hotspot | `bash app-mobile/hotspot.sh` |
| Recompiler l'APK | `bash app-mobile/construire.sh` |

Les détails sont dans **[`dashboard/README.md`](dashboard/README.md)** et
**[`app-mobile/README.md`](app-mobile/README.md)**.

## Ce dépôt contient le code, pas les données

Les sujets et les audios viennent de sites tiers : ils ne m'appartiennent pas et
ne sont donc **pas publiés**. À la place, chaque fichier de données a un jumeau
`*.exemple.*` qui contient **un seul élément**, pour montrer le format exact.

| Fichier publié | Ce qu'il montre | Le vrai fichier (local) |
|---|---|---|
| `dashboard/questions.exemple.js` | 1 combinaison d'expression écrite | `questions.js` — 11 combinaisons |
| `dashboard/questions_oral.exemple.js` | 1 combinaison d'expression orale | `questions_oral.js` |
| `dashboard/sujets_oraux.exemple.json` | 1 sujet par tâche | `sujets_oraux.json` — 30 + 30 |
| `dashboard/banque/exemple/` | 1 question + son mp3 + son image | `banque/` — 991 questions, ~1,3 Go |
| `app-mobile/…/Sujets.exemple.java` | 1 sujet par tâche | `Sujets.java` — 900 combinaisons |

Pour faire tourner le projet, on copie l'exemple sans le suffixe
(`cp questions.exemple.js questions.js`) et on le remplit — ou on laisse les
scripts `telecharger_tcf.py` / `construire_banque.py` / `integrer_fuck.py`
reconstruire la banque (jeton d'accès en variable d'environnement).

Sont aussi exclus, et pour de bonnes raisons :

- **Mes données perso** — mes enregistrements vocaux, mes copies d'expression
  écrite, mes résultats de simulation.
- **`cle.keystore`** — la clé de signature de l'APK.
- **Le mot de passe du hotspot** — lu depuis `~/.tcf-hotspot-mdp`, à créer une
  fois : `printf '%s' 'mon-mot-de-passe' > ~/.tcf-hotspot-mdp && chmod 600 ~/.tcf-hotspot-mdp`

## Prérequis

Python 3, `nmcli` (NetworkManager) pour le hotspot, `adb` pour installer l'APK,
et le JDK + build-tools Android pour la recompiler.
