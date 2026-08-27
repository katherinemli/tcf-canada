# 📝 Simulateur TCF — Expression écrite **et orale**

Simulateur d'examen 100% hors ligne, juste pour moi — avec évaluation par IA gratuite.

- **✍️ Écrit** — 3 tâches, 60 minutes.
- **🎙️ Oral** — 3 tâches, 12 minutes, avec enregistrement de ma voix.

Les deux sont dans la même page : les onglets **Écrit / Oral** sont sur l'accueil.

## Deux façons de l'utiliser

**A) S'entraîner (hors ligne, sans rien lancer)**
Double-clic sur `index.html`. Tu fais l'examen, tu vois tes réponses à la fin. Tu peux « 📋 Copier pour ChatGPT » et coller le texte dans n'importe quelle IA.

**B) Avec l'évaluation automatique par Claude (bouton « 🤖 Évaluer »)**

Le serveur tourne **tout seul en arrière-plan** (service systemd, voir plus bas) :
il démarre à l'ouverture de la session, sans terminal.

1. Ouvre **http://localhost:8777** (pas le double-clic)
2. Fais l'examen → clique **« 🤖 Évaluer avec Claude »** → la note et les conseils s'affichent (~30-60 s)

## Le serveur en arrière-plan (service)

Installé dans `~/.config/systemd/user/tcf-simulateur.service`. Il n'y a **rien à
lancer à la main** : il démarre tout seul et repart si jamais il plante.

| Je veux… | Commande |
|---|---|
| Voir s'il tourne | `systemctl --user status tcf-simulateur` |
| L'arrêter | `systemctl --user stop tcf-simulateur` |
| Le relancer | `systemctl --user restart tcf-simulateur` |
| Voir le journal | `journalctl --user -u tcf-simulateur -f` |
| Ne plus le démarrer au login | `systemctl --user disable --now tcf-simulateur` |

Il n'écoute que sur `127.0.0.1` : rien n'est accessible depuis l'extérieur.
Pour qu'il tourne **même sans être connectée** (facultatif) :
`sudo loginctl enable-linger katherine`

L'évaluation passe par **ton Claude Code** (`claude -p`) : pas de clé API, pas de coût en plus.
Si Claude n'a plus de tokens du jour, l'app te le dit et te propose de **copier le texte pour ChatGPT** — tu n'es jamais bloquée.

## 🎙️ Expression orale

⚠️ **L'oral ne marche QUE par http://localhost:8777.** Par double-clic sur le
fichier, le navigateur interdit le micro — c'est une règle de sécurité, il n'y a
rien à réparer.

### Le déroulé (12 min, comme le vrai examen)

| Tâche | Préparation | Temps de parole |
|---|---|---|
| 1. Présentation personnelle | aucune | 2 min |
| 2. Interaction (c'est **moi** qui pose les questions) | 2 min | 3 min 30 |
| 3. Argumentation (mon point de vue) | aucune | 4 min 30 |

Chaque tâche : je vois le sujet → je clique **Commencer** → un anneau décompte
le temps → je parle → l'enregistrement s'arrête tout seul. Je peux **refaire une
tâche** autant de fois que je veux avant de passer à la suivante.

### 🎧 Mon casque Bluetooth (important !)

Un casque Bluetooth ne peut pas faire les deux à la fois :

- **mode musique (A2DP)** : beau son, **mais le micro n'existe pas** ;
- **mode micro (HFP)** : le micro marche, mais le son devient « téléphone ».

Sur l'onglet Oral, un bandeau me dit dans quel mode je suis, avec un bouton pour
basculer. **Sans ça, aucun micro n'apparaît et on ne comprend pas pourquoi.**
Après l'entraînement, un autre bouton remet le mode musique.

> Le micro intégré de l'ordinateur, lui, marche toujours — et il est souvent
> meilleur que celui d'un casque Bluetooth en mode HFP.

### Réécouter, faire écrire, faire corriger

Après l'examen (bouton **🎧 Mes enregistrements**) :

1. **Je me réécoute** — le lecteur est là, c'est le plus utile.
2. **« Écrire ce que j'ai dit »** — Whisper transcrit sur **mon** ordinateur :
   gratuit, hors ligne, illimité. Compte ~30-90 s par enregistrement.
   Le résultat est gardé, on ne recalcule jamais deux fois.
3. **« 🤖 Évaluer avec Claude »** — note sur 20, niveau CECR, points forts,
   axes d'amélioration et une version corrigée de ce que j'ai dit.
   Claude sait que c'est une transcription : il ne juge **ni** l'orthographe
   **ni** la ponctuation, seulement ce qui s'entend.

Le **débit** (mots/minute) est affiché : 120-150 = fluide, moins de 80 = hésitant.

### Enregistrer avec autre chose (téléphone, dictaphone)

Sur la page des enregistrements, **📁 Importer un fichier audio** accepte
n'importe quel format (`.m4a`, `.3gp`, `.amr`, `.mp3`…) : le serveur le remet
tout seul au bon format. Pratique si le micro du PC est mauvais — le micro d'un
téléphone est presque toujours meilleur.

### Transcription plus rapide (facultatif)

Whisper tourne en local et ne coûte rien. Si je préfère AssemblyAI (plus rapide,
mais ça consomme le crédit du compte), je colle ma clé dans un fichier
`cle_assemblyai.txt` à côté de `index.html` — **une seule ligne, juste la clé** :

```
ma_cle_assemblyai_ici
```

Puis `systemctl --user restart tcf-simulateur`. Le serveur la prend tout seul,
et **si elle ne marche plus (crédit épuisé, pas d'Internet), il repasse sur
Whisper sans rien demander**. Pour revenir à Whisper : supprimer le fichier.

## Fichiers

- `index.html` — toute l'application (Vue 3, un seul fichier)
- `questions.js` — **les questions de l'écrit (remplir ici !)**
- `questions_oral.js` — **les sujets de l'oral (remplir ici !)**
- `serveur_eval.py` — le petit serveur d'évaluation (option B)
- `transcrire.py` — appelle Whisper pour écrire ce que j'ai dit
- `.venv-whisper/` — Whisper et ses dépendances, à part du reste
- `vue.global.prod.js` — Vue en local, ne pas toucher
- `mes_reponses/` — mes examens écrits (un `.md` par combinaison)
- `mes_audios/` — mes enregistrements (`.webm`) et leur transcription (`.txt`)

## Ajouter des questions (phase deux)

Ouvrir `questions.js`, copier un bloc `{ ... }` de combinaison, changer les textes.

> **Je ne vois pas les nouvelles questions ?** C'est le cache du navigateur.
> Fais un **rechargement forcé** : `Ctrl + Maj + R` (ou `Ctrl + F5`).
> Le serveur envoie maintenant `Cache-Control: no-store`, donc ça ne devrait
> plus arriver — mais la toute première fois il faut casser l'ancien cache.

Chaque combinaison = 3 tâches :

1. **Message court** (60-120 mots) — `sujet`
2. **Narration / Blog** (120-150 mots) — `sujet`
3. **Argumentation** (120-180 mots) — `sujet` (le thème) + `documents` (les 2 points de vue)

## Ce que ça fait

- Chrono 60 min (rouge quand il reste moins de 5 min), fin automatique à 00:00
- Compteur de mots + barres de progression par tâche
- Boutons de caractères spéciaux (é è ç œ …) qui s'insèrent au curseur
- Bouton « Masquer » pour cacher le sujet
- Sauvegarde automatique : si je ferme par accident, je peux reprendre
- À la fin : mes textes avec bouton « Copier » pour chaque tâche
- Sur l'accueil : **📚 Mes réponses** — **tous** mes examens terminés, du plus récent
  au plus ancien, avec la note et le niveau. Ils viennent de deux endroits, réunis
  dans une seule liste :
  - les examens faits **dans l'app** (gardés par le navigateur) ;
  - les fichiers `.md` du dossier `mes_reponses/` (visibles seulement avec le
    serveur lancé).

  Si un même examen existe des deux côtés, il n'apparaît qu'une fois (version de
  l'app). Chaque carte permet de relire son bulletin, de l'effacer, ou de refaire
  l'examen en mode facile / extrême.
- **Chaque examen terminé est aussi écrit dans `mes_reponses/`** (avec le serveur
  lancé) : `combinaison-3_2026-07-23.md`, avec la note, les textes et les conseils.
  On peut donc les relire, les imprimer ou les sauvegarder sans ouvrir l'app.
  À l'ouverture de l'accueil, les examens qui n'ont pas encore leur fichier sont
  rattrapés automatiquement. Effacer un examen efface aussi son fichier.
