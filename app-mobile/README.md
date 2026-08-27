# 🎙️ TCF Oral — l'appli du vieux téléphone

Une appli Android pour le Honor 9, qui ne sert qu'à **une** chose : je touche la
tâche, elle m'enregistre le temps exact de l'examen et elle s'arrête toute seule.
Pas d'internet, pas de compte, pas de pub. Rien à toucher pendant que je parle.

| Tâche | Préparation | Temps de parole |
|---|---|---|
| 1. Présentation personnelle | — | 2 min |
| 2. Interaction (je pose les questions) | 2 min | 3 min 30 |
| 3. Argumentation | — | 4 min 30 |

Les bips me disent où j'en suis sans regarder : **2 bips** = je parle · 1 bip à
**1 min** · 2 bips à **30 s** · 5 tics les 5 dernières secondes · **bip long** =
c'est fini, ça a déjà coupé.

L'écran reste allumé tout seul. Si un appel ou une notification m'interrompt,
l'appli **garde** ce qui est déjà enregistré — seul le bouton « Annuler » efface.

Les fichiers vont dans **`TCF_oral/`** sur le téléphone :
`tache-2_2026-08-12_14h30.m4a`.

## Installer (une seule fois)

Sur le Honor 9, activer le débogage USB :

1. Paramètres → À propos du téléphone → toucher **7 fois** « Numéro de build »
2. Paramètres → Système → Options de développement → **Débogage USB**
3. Brancher le câble → sur le téléphone « Autoriser le débogage USB ? » → **OK**
   (cocher « Toujours autoriser »)

Puis, sur le PC :

```bash
bash ~/tcf_oral_app/installer.sh
```

Au premier lancement, l'appli demande le **micro** et le **stockage** : accepter.
C'est la seule fois.

> Sans câble : envoyer `TCF-Oral.apk` par Bluetooth et le toucher sur le
> téléphone (il faudra autoriser « installer des applications inconnues »).

## Récupérer mes enregistrements

Téléphone branché en USB :

```bash
bash ~/tcf_oral_app/recuperer.sh          # copie ce qui est nouveau
bash ~/tcf_oral_app/recuperer.sh --vider  # copie puis vide le téléphone
```

Ça les dépose dans `~/tcf_simulateur/mes_audios/`, donc **http://localhost:8777**
→ 🎧 Mes enregistrements → « Écrire ce que j'ai dit » (Whisper) → « Évaluer ».
Le Bluetooth n'est plus nécessaire.

## Changer les temps

Dans `src/com/katherine/tcforal/Principale.java`, tout en haut :

```java
private static final int[] PREP  = { 0, 120, 0 };     // secondes de préparation
private static final int[] DUREE = { 120, 210, 270 }; // secondes de parole
```

Puis `bash construire.sh` et `bash installer.sh`.

## Comment c'est fabriqué

Pas de Gradle, pas d'Android Studio : `aapt2` + `javac` + `d8` + `apksigner`,
outils dans `~/android-min/` (build-tools 33.0.2, plateforme Android 9 = API 28,
`platform-tools` pour adb). Le code tient en deux fichiers, sans aucune
bibliothèque extérieure.

- `src/…/Principale.java` — l'appli entière (écrans, chrono, micro, bips)
- `src/…/Anneau.java` — l'anneau qui se remplit
- `construire.sh` — fabrique et signe `TCF-Oral.apk`
- `cle.keystore` — ma clé de signature (mot de passe `android`) : **la garder**,
  sinon une future version ne pourra pas s'installer par-dessus l'ancienne.

## Et si l'appli ne marche pas ?

`chrono_oral.html` (dans `~/tcf_simulateur/`) fait la même chose sans appli :
c'est une page web hors ligne qui donne les bips, mais elle n'enregistre pas —
c'est le dictaphone du téléphone qui s'en charge.
