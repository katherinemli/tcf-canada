#!/usr/bin/env python3
# ============================================================
# Serveur local d'évaluation TCF — utilise TON Claude Code (claude -p).
# Pas de clé API, pas de coût en plus : ça passe par ton abonnement.
#
# LANCER :   python3 serveur_eval.py
# OUVRIR :   http://localhost:8777
# ARRÊTER :  Ctrl+C
#
# Si Claude n'a plus de tokens du jour, l'app te le dit et tu peux
# attendre — tes réponses restent gardées.
# ============================================================

import hmac
import json
import os
import re
import subprocess
import time
import urllib.parse
import http.server
import socketserver

PORT = 8777
DOSSIER = os.path.dirname(os.path.abspath(__file__))

# Le serveur écoute sur toutes les interfaces (pour que le téléphone puisse
# envoyer ses enregistrements), MAIS il ne répond qu'à l'ordinateur lui-même
# et aux appareils du point d'accès WiFi (sous-réseau 10.42.x, protégé par mot
# de passe). Tout le reste — dont le réseau institutionnel — reçoit un 403.
IP_LOCALES = ("127.0.0.1", "::1", "::ffff:127.0.0.1")
PREFIXE_HOTSPOT = "10.42."
# Depuis le hotspot, le téléphone n'a le droit de faire QUE ça (moindre
# privilège) : déposer un enregistrement, demander ce qui est déjà arrivé, et
# déposer son carnet. Rien d'autre — aucun fichier du projet, même muni de la
# clé. /oral/liste sert au bouton « Envoyer au PC » (le téléphone compare les
# noms pour n'envoyer que ce qui manque) ; /oral/journal apporte les questions
# travaillées, puisque c'est le téléphone qui les tire maintenant.
CHEMINS_TELEPHONE = ("/oral/envoyer", "/oral/liste", "/oral/journal",
                     "/oral/apk", "/apk")
# L'APK elle-même se télécharge par ce même port : le pare-feu du point d'accès
# n'ouvre que celui-ci, et ouvrir un second port juste pour les mises à jour
# serait une porte de plus à surveiller.
#
# Deux adresses pour la même chose. La courte existe parce qu'on la tape sur un
# clavier de téléphone, à bout de bras :
#   http://10.42.0.1:8777/apk?c=<code court>          ← à taper
#   http://10.42.0.1:8777/oral/apk?cle=<la clé>       ← complète
# Le code court ne déverrouille QUE le téléchargement de l'APK : il ne permet
# ni de déposer un audio, ni de lire quoi que ce soit d'autre.
FICHIER_APK = os.path.expanduser("~/tcf_oral_app/TCF-Oral.apk")
CODE_APK = "tcf"
# Clé secrète connue seulement de MON appli. Un appareil du hotspot doit la
# présenter (?cle=… ou en-tête X-Cle) : ainsi, même quelqu'un qui aurait le mot
# de passe WiFi ne peut rien envoyer sans elle. La même valeur est dans l'APK.
CLE_TELEPHONE = "T7f2Ka9pQx4Lm3Zr"
DOSSIER_REPONSES = os.path.join(DOSSIER, "mes_reponses")
DELAI_MAX = 300  # secondes avant d'abandonner un appel à Claude

# ---------- Expression orale ----------
DOSSIER_AUDIOS = os.path.join(DOSSIER, "mes_audios")
# Whisper vit dans son propre environnement pour ne rien casser ailleurs.
# Créé une fois par :  python3 -m venv .venv-whisper
#                      .venv-whisper/bin/pip install faster-whisper
PYTHON_WHISPER = os.path.join(DOSSIER, ".venv-whisper", "bin", "python")
SCRIPT_TRANSCRIPTION = os.path.join(DOSSIER, "transcrire.py")
DELAI_TRANSCRIPTION = 900  # 15 min : le modèle tourne sur le processeur
# Facultatif : si ce fichier existe, on transcrit avec AssemblyAI (plus rapide)
# au lieu de Whisper. Une seule ligne : la clé, rien d'autre.
FICHIER_CLE_ASSEMBLYAI = os.path.join(DOSSIER, "cle_assemblyai.txt")
TAILLE_AUDIO_MAX = 60 * 1024 * 1024  # 60 Mo — bien au-delà de 5 min d'Opus
# Ce que le navigateur produit, plus ce qu'on peut importer d'ailleurs
# (téléphone Android, dictaphone, etc.).
FORMATS_AUDIO = (".webm", ".ogg", ".opus", ".wav", ".mp4", ".m4a",
                 ".mp3", ".aac", ".flac", ".3gp", ".amr")

# ---------- Compréhension orale ----------
# Une simulation terminée = un fichier JSON ici. On garde les identifiants des
# questions posées : c'est ce qui permet de ne jamais te reproposer un audio
# déjà entendu (voir questions_vues).
DOSSIER_CO = os.path.join(DOSSIER, "mes_simulations_co")

# Enregistrements d'expression orale envoyés depuis le téléphone (page /envoyer).
DOSSIER_SIM_ORAL = os.path.join(DOSSIER, "mes_simulation_expression_oral")


MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def nombre(txt):
    """« 8,3 » → 8.3 et « 9 » → 9. Renvoie None si ce n'est pas un nombre.

    Les notes viennent de l'IA : elles sont parfois entières (9/20), parfois
    à virgule (8,3/20). On garde les deux.
    """
    try:
        v = float(str(txt).replace(",", "."))
    except (TypeError, ValueError):
        return None
    return int(v) if v.is_integer() else v


def texte_note(n):
    """L'inverse : 8.3 → « 8,3 », 9 → « 9 » (comme l'affichage de la page)."""
    v = nombre(n)
    if v is None:
        return ""
    return str(v) if isinstance(v, int) else f"{v:.1f}".replace(".", ",")


def date_du_nom(nom):
    """Récupère une date lisible depuis un nom « ..._2026-07-23.md ».

    Sert de repli quand le fichier ne contient pas « soumis le <date> ».
    """
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", nom)
    if not m:
        return ""
    annee, mm, jj = m.group(1), int(m.group(2)), int(m.group(3))
    if 1 <= mm <= 12:
        return f"{int(jj)} {MOIS[mm - 1]} {annee}"
    return ""


def lire_fiche_brut(contenu, nom):
    """Lit le format « export brut » (feature examen) et le rend compatible.

    Format attendu :
        Mon examen TCF — Combinaison 3
        === Tâche 1 : Message court (134 mots) ===
        Sujet : ...
        Document 1 : ...        (facultatif)
        Ma réponse :
        <le texte>
    Ce format n'a ni score ni retour : la page « bulletin » s'adapte toute
    seule quand ces parties sont vides.
    """
    fiche = {
        "fichier": nom, "titre": os.path.splitext(nom)[0], "date": date_du_nom(nom),
        "noteGlobale": None, "niveau": "", "nclc": "", "temps": "",
        "taches": [], "retour": [],
    }

    m = re.search(r"^Mon examen TCF\s*—\s*(.+)$", contenu, re.M)
    if m:
        fiche["titre"] = m.group(1).strip()

    entetes = list(re.finditer(
        r"^===\s*Tâche\s*(\d+)\s*:\s*([^(]+?)\s*\((\d+)\s*mots\)\s*===\s*$",
        contenu, re.M))
    for i, e in enumerate(entetes):
        fin = entetes[i + 1].start() if i + 1 < len(entetes) else len(contenu)
        corps = contenu[e.end():fin]
        sujet = ""
        ms = re.search(r"^Sujet\s*:\s*(.+)$", corps, re.M)
        if ms:
            sujet = ms.group(1).strip()
        texte = ""
        mr = re.search(r"^Ma réponse\s*:\s*$", corps, re.M)
        if mr:
            texte = corps[mr.end():].strip()
        fiche["taches"].append({
            "numero": int(e.group(1)),
            "type": e.group(2).strip(),
            "mots": int(e.group(3)),
            "sujet": sujet,
            "texte": texte,
            "note": None,
            "niveau": "",
        })
    return fiche


def lire_fiche(contenu, nom):
    """Transforme un examen archivé en données pour la page « bulletin ».

    Comprend DEUX formats (les deux features) :
      1. le format « bulletin » (évalué), ci-dessous ;
      2. le format « export brut » (voir lire_fiche_brut).
    On essaie le format bulletin ; s'il ne trouve aucune tâche, on bascule
    sur le format brut. Ainsi toutes les combinaisons s'affichent.

    Format bulletin attendu (voir mes_reponses/) :
        # <titre> — soumis le <date>
        **Score du site :** 8/20 · Niveau A2 (NCLC 4) · Temps 54:21
        - Tâche 1 (Message court) : 9/20 — A2
        ## Tâche 1 — Message court (114 mots)
        <le texte>
        ## Mon retour — les leviers
    Si une partie manque, on la laisse vide : la page s'adapte.
    """
    fiche = {
        "fichier": nom, "titre": os.path.splitext(nom)[0], "date": "",
        "noteGlobale": None, "niveau": "", "nclc": "", "temps": "",
        "taches": [], "retour": [],
    }

    m = re.search(r"^#\s+(.+)$", contenu, re.M)
    if m:
        titre = m.group(1).strip()
        fiche["titre"] = titre
        sep = re.split(r"\s+—\s+soumis le\s+", titre, maxsplit=1)
        if len(sep) == 2:
            fiche["titre"], fiche["date"] = sep[0].strip(), sep[1].strip()

    m = re.search(r"Score du site\s*:?\*{0,2}\s*([\d,.]+)/20\s*·\s*Niveau\s+([^(·]+)"
                  r"(?:\(([^)]*)\))?\s*(?:·\s*Temps\s*([\d:]+))?", contenu)
    if m:
        fiche["noteGlobale"] = nombre(m.group(1))
        fiche["niveau"] = m.group(2).strip()
        fiche["nclc"] = (m.group(3) or "").strip()
        fiche["temps"] = (m.group(4) or "").strip()

    # Notes par tâche, listées sous le score global.
    notes = {}
    for num, note, niveau in re.findall(
            r"^-\s*Tâche\s*(\d+)[^:]*:\s*([\d,.]+)/20\s*—\s*(.+)$", contenu, re.M):
        notes[int(num)] = {"note": nombre(note), "niveau": niveau.strip()}

    # Une section « ## Tâche N — Type (X mots) [— « sujet »] » par tâche.
    entetes = list(re.finditer(
        r"^##\s*Tâche\s*(\d+)\s*—\s*([^(]+?)\s*\((\d+)\s*mots\)"
        r"(?:\s*—\s*«\s*(.+?)\s*»)?\s*$", contenu, re.M))
    for i, e in enumerate(entetes):
        fin = entetes[i + 1].start() if i + 1 < len(entetes) else len(contenu)
        corps = contenu[e.end():fin]
        corps = re.split(r"^##\s", corps, maxsplit=1, flags=re.M)[0]
        corps = re.sub(r"^\s*---\s*$", "", corps, flags=re.M)
        numero = int(e.group(1))
        fiche["taches"].append({
            "numero": numero,
            "type": e.group(2).strip(),
            "mots": int(e.group(3)),
            "sujet": (e.group(4) or "").strip(),
            "texte": corps.strip(),
            "note": notes.get(numero, {}).get("note"),
            "niveau": notes.get(numero, {}).get("niveau", ""),
        })

    m = re.search(r"^##\s*Mon retour.*$", contenu, re.M)
    if m:
        fiche["retour"] = lire_retour(contenu[m.end():])

    # Aucune tâche au format bulletin ? C'est sûrement l'autre feature
    # (export brut) : on le lit avec l'autre lecteur.
    if not fiche["taches"]:
        return lire_fiche_brut(contenu, nom)
    return fiche


def sans_gras(texte):
    """Enlève le **gras** markdown : la page a déjà ses propres styles."""
    return re.sub(r"\*\*(.+?)\*\*", r"\1", texte).strip()


def lire_retour(bloc):
    """Découpe « Mon retour » en sections { titre, points[] }.

    Format : « 1. **Titre** » puis des sous-puces « - point ».
    Une puce sans section précédente est rattachée à une section sans titre.
    """
    sections = []
    for ligne in bloc.splitlines():
        ligne = ligne.rstrip()
        if not ligne.strip():
            continue
        titre = re.match(r"^\s*\d+\.\s*(.+)$", ligne)
        point = re.match(r"^\s*[-•*]\s*(.+)$", ligne)
        if titre:
            sections.append({"titre": sans_gras(titre.group(1)), "points": []})
        elif point:
            if not sections:
                sections.append({"titre": "", "points": []})
            sections[-1]["points"].append(sans_gras(point.group(1)))
        else:
            sections.append({"titre": sans_gras(ligne), "points": []})
    return sections


def lister_reponses():
    """Les examens archivés dans mes_reponses/, du plus récent au plus ancien.

    Les fichiers sont petits : on renvoie directement leur contenu, ce qui
    évite un deuxième aller-retour quand on clique sur un examen.
    """
    if not os.path.isdir(DOSSIER_REPONSES):
        return []
    fiches = []
    for nom in os.listdir(DOSSIER_REPONSES):
        if not nom.endswith((".md", ".txt")):
            continue
        chemin = os.path.join(DOSSIER_REPONSES, nom)
        try:
            with open(chemin, encoding="utf-8") as f:
                contenu = f.read()
        except OSError:
            continue
        fiche = lire_fiche(contenu, nom)
        fiche["modifie"] = os.path.getmtime(chemin)
        fiches.append(fiche)
    fiches.sort(key=lambda f: f["modifie"], reverse=True)
    return fiches


def supprimer_reponse(nom):
    """Supprime un fichier archivé de mes_reponses/ (nom de fichier seul).

    On refuse tout chemin qui sortirait du dossier (sécurité).
    """
    if not nom or "/" in nom or "\\" in nom or nom.startswith("."):
        return {"ok": False, "message": "Nom de fichier invalide."}
    chemin = os.path.join(DOSSIER_REPONSES, nom)
    if os.path.dirname(os.path.abspath(chemin)) != os.path.abspath(DOSSIER_REPONSES):
        return {"ok": False, "message": "Nom de fichier invalide."}
    try:
        os.remove(chemin)
    except FileNotFoundError:
        return {"ok": True}  # déjà absent : on considère que c'est bon
    except OSError as e:
        return {"ok": False, "message": f"Suppression impossible : {e}"}
    return {"ok": True}


def ecrire_fiche(data):
    """Fabrique le texte d'un fichier mes_reponses/*.md (format « bulletin »).

    C'est l'inverse exact de lire_fiche : ce qui est écrit ici doit pouvoir être
    relu là-bas. Les deux sont voisins pour qu'on pense à les changer ensemble.
    """
    titre = (data.get("titre") or "Examen TCF").strip()
    date = (data.get("date") or "").strip()
    bilan = data.get("bilan") or {}
    taches = data.get("taches") or []

    lignes = [f"# {titre} — soumis le {date}" if date else f"# {titre}", ""]

    # Ligne de score : seulement si l'examen a été évalué.
    note = texte_note(bilan.get("noteGlobale"))
    if note:
        entete = f"**Score du site :** {note}/20"
        if bilan.get("niveau"):
            entete += f" · Niveau {bilan['niveau']}"
            if bilan.get("nclc"):
                entete += f" ({bilan['nclc']})"
        if data.get("temps"):
            entete += f" · Temps {data['temps']}"
        lignes.append(entete)
        for i, t in enumerate(bilan.get("taches") or []):
            n = texte_note(t.get("note"))
            if not n:
                continue
            type_ = taches[i].get("type", "") if i < len(taches) else ""
            lignes.append(f"- Tâche {i + 1} ({type_}) : {n}/20 — {t.get('niveau', '')}")
        lignes.append("")

    for i, t in enumerate(taches):
        titre_tache = f"## Tâche {i + 1} — {t.get('type', '')} ({t.get('mots', 0)} mots)"
        if t.get("sujet"):
            titre_tache += f" — « {t['sujet']} »"
        lignes += [titre_tache, "", (t.get("texte") or "").strip() or "(vide)", ""]

    # « Mon retour » : les leviers globaux, puis le détail par tâche.
    sections = []
    leviers = [l for l in (bilan.get("leviers") or []) if l]
    if leviers:
        sections.append(("Mes 2 leviers pour progresser", leviers))
    for i, t in enumerate(bilan.get("taches") or []):
        points = [f"✅ {p}" for p in (t.get("positifs") or [])]
        points += [f"⚠️ {p}" for p in (t.get("ameliorations") or [])]
        if points:
            type_ = taches[i].get("type", "") if i < len(taches) else ""
            sections.append((f"Tâche {i + 1} — {type_}", points))
    if sections:
        lignes += ["## Mon retour — les leviers", ""]
        for n, (titre_section, points) in enumerate(sections, start=1):
            lignes.append(f"{n}. **{titre_section}**")
            lignes += [f"- {p}" for p in points]
            lignes.append("")

    return "\n".join(lignes).rstrip() + "\n"


def enregistrer_reponse(data):
    """Archive un examen dans mes_reponses/<id>_<AAAA-MM-JJ>.md.

    Appelé par la page à chaque examen terminé (et au chargement, pour rattraper
    ceux qui n'existaient que dans le navigateur). Un seul fichier par
    combinaison : si on refait le même examen, l'ancien fichier est remplacé.
    """
    ident = (data.get("id") or "").strip()
    jour = (data.get("jour") or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", ident):
        return {"ok": False, "message": "Identifiant d'examen invalide."}
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", jour):
        return {"ok": False, "message": "Date invalide."}

    nom = f"{ident}_{jour}.md"
    try:
        os.makedirs(DOSSIER_REPONSES, exist_ok=True)
        with open(os.path.join(DOSSIER_REPONSES, nom), "w", encoding="utf-8") as f:
            f.write(ecrire_fiche(data))
        # Un examen refait un autre jour laisserait un doublon : on nettoie.
        for autre in os.listdir(DOSSIER_REPONSES):
            if autre != nom and autre.startswith(ident + "_"):
                os.remove(os.path.join(DOSSIER_REPONSES, autre))
    except OSError as e:
        return {"ok": False, "message": f"Enregistrement impossible : {e}"}
    return {"ok": True, "fichier": nom}


# ============================================================
# EXPRESSION ORALE — enregistrements audio et transcription
#
# Le navigateur enregistre (MediaRecorder) et envoie le son ici ; on le
# pose simplement sur le disque, dans mes_audios/. La transcription est
# faite à la demande par Whisper, en local : rien ne sort de l'ordinateur.
# Chaque enregistrement « toto.webm » a un jumeau « toto.txt » qui garde
# sa transcription — on ne la recalcule donc jamais deux fois.
# ============================================================

def chemin_audio(nom):
    """Vérifie un nom d'enregistrement et renvoie son chemin complet.

    Renvoie None si le nom pourrait sortir du dossier mes_audios/
    (« ../ », chemin absolu, extension inconnue…).
    """
    if not nom or "/" in nom or "\\" in nom or nom.startswith("."):
        return None
    if not nom.lower().endswith(FORMATS_AUDIO):
        return None
    if not re.fullmatch(r"[A-Za-z0-9._-]+", nom):
        return None
    chemin = os.path.join(DOSSIER_AUDIOS, nom)
    if os.path.dirname(os.path.abspath(chemin)) != os.path.abspath(DOSSIER_AUDIOS):
        return None
    return chemin


def chemin_transcription(chemin):
    """« mes_audios/oral-1_tache-2.webm » → « mes_audios/oral-1_tache-2.txt »."""
    return os.path.splitext(chemin)[0] + ".txt"


def reparer_duree(chemin):
    """Réécrit l'en-tête du fichier pour y inscrire sa durée.

    Le navigateur enregistre « en direct » : au moment où il écrit le début
    du fichier, il ne sait pas encore combien de temps ça va durer — il ne
    met donc aucune durée. Résultat : la barre de lecture est inutilisable,
    on ne peut pas se déplacer dans son propre enregistrement.
    ffmpeg recopie le son tel quel (« -c copy » : aucun réencodage, aucune
    perte) et en profite pour écrire la durée, qu'il connaît maintenant.

    Sans ffmpeg, on garde le fichier d'origine : il s'écoute très bien,
    la barre est juste moins pratique. Rien de grave, donc rien à signaler.
    """
    racine, ext = os.path.splitext(chemin)
    temporaire = racine + ".enreparation" + ext
    try:
        proc = subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", chemin, "-c", "copy", temporaire],
            capture_output=True, timeout=120)
        if proc.returncode == 0 and os.path.getsize(temporaire) > 0:
            os.replace(temporaire, chemin)
            return
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    try:
        os.remove(temporaire)
    except OSError:
        pass


def convertir_en_opus(chemin):
    """Reconvertit un fichier importé en webm/opus, lisible par le navigateur.

    Un enregistrement fait sur un téléphone arrive en .m4a, .amr, .3gp…
    Certains de ces formats, le navigateur ne sait pas les lire : on
    obtiendrait un lecteur muet. On les remet donc tous dans le même
    format que celui produit par l'app. Renvoie le nouveau chemin, ou
    l'ancien si ffmpeg n'est pas là (au pire, le lecteur restera muet
    mais la transcription, elle, marchera quand même).
    """
    cible = os.path.splitext(chemin)[0] + ".webm"
    if os.path.abspath(cible) == os.path.abspath(chemin):
        reparer_duree(chemin)
        return chemin
    try:
        proc = subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", chemin,
             "-vn", "-c:a", "libopus", "-b:a", "48k", "-ac", "1", cible],
            capture_output=True, timeout=300)
        if proc.returncode == 0 and os.path.getsize(cible) > 0:
            os.remove(chemin)
            return cible
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    try:
        os.remove(cible)
    except OSError:
        pass
    return chemin


def enregistrer_audio(nom, donnees, convertir=False):
    """Écrit un enregistrement dans mes_audios/.

    Deux origines possibles : le micro de la page (convertir=False, le son
    est déjà au bon format) ou un fichier importé depuis un téléphone
    (convertir=True, il faut le remettre au format du navigateur).

    Refaire une tâche remplace l'ancien fichier du même jour ; un autre
    jour donne un autre nom, ce qui permet de réécouter ses progrès.
    L'ancienne transcription est supprimée : elle ne correspond plus.
    """
    chemin = chemin_audio(nom)
    if not chemin:
        return {"ok": False, "message": "Nom d'enregistrement invalide."}
    if not donnees:
        return {"ok": False, "message": "Enregistrement vide — le micro n'a rien capté."}
    try:
        os.makedirs(DOSSIER_AUDIOS, exist_ok=True)
        with open(chemin, "wb") as f:
            f.write(donnees)
        ancienne = chemin_transcription(chemin)
        if os.path.exists(ancienne):
            os.remove(ancienne)
    except OSError as e:
        return {"ok": False, "message": f"Enregistrement impossible : {e}"}

    if convertir:
        chemin = convertir_en_opus(chemin)   # peut changer l'extension
    else:
        reparer_duree(chemin)
    return {"ok": True, "fichier": os.path.basename(chemin),
            "octets": os.path.getsize(chemin)}


def lister_audios():
    """Tous les enregistrements de mes_audios/, du plus récent au plus ancien.

    On joint la transcription quand elle existe déjà, pour que la page
    puisse l'afficher tout de suite sans relancer Whisper.
    """
    if not os.path.isdir(DOSSIER_AUDIOS):
        return []
    fiches = []
    for nom in sorted(os.listdir(DOSSIER_AUDIOS)):
        if not nom.lower().endswith(FORMATS_AUDIO):
            continue
        chemin = os.path.join(DOSSIER_AUDIOS, nom)
        fiche = {"fichier": nom, "octets": os.path.getsize(chemin),
                 "modifie": os.path.getmtime(chemin), "texte": "", "mots": 0,
                 "duree": 0, "debit": 0}
        txt = chemin_transcription(chemin)
        if os.path.exists(txt):
            try:
                with open(txt, encoding="utf-8") as f:
                    fiche.update(json.load(f))
            except (OSError, json.JSONDecodeError):
                pass
        fiches.append(fiche)
    fiches.sort(key=lambda f: f["modifie"], reverse=True)
    return fiches


def supprimer_audio(nom):
    """Efface un enregistrement et sa transcription."""
    chemin = chemin_audio(nom)
    if not chemin:
        return {"ok": False, "message": "Nom d'enregistrement invalide."}
    for c in (chemin, chemin_transcription(chemin)):
        try:
            os.remove(c)
        except FileNotFoundError:
            pass  # déjà absent : très bien
        except OSError as e:
            return {"ok": False, "message": f"Suppression impossible : {e}"}
    return {"ok": True}


def cle_assemblyai():
    """La clé AssemblyAI, si tu en as posé une. Sinon None (→ Whisper).

    Deux façons de la donner, au choix :
      • le fichier cle_assemblyai.txt à côté de ce script (une seule ligne) ;
      • la variable d'environnement ASSEMBLYAI_API_KEY.
    """
    cle = (os.environ.get("ASSEMBLYAI_API_KEY") or "").strip()
    if cle:
        return cle
    try:
        with open(FICHIER_CLE_ASSEMBLYAI, encoding="utf-8") as f:
            return f.read().strip() or None
    except OSError:
        return None


def transcrire_assemblyai(chemin, cle):
    """Transcrit via AssemblyAI : envoi du fichier, puis attente du résultat.

    Plus rapide que Whisper (le calcul se fait chez eux), mais ça consomme
    le crédit gratuit du compte. En cas de pépin on renvoie ok:False et
    l'appelant repasse sur Whisper : on n'est jamais bloquée.
    """
    import urllib.request
    import urllib.error
    import time

    base = "https://api.assemblyai.com/v2"
    entetes = {"authorization": cle}

    def appel(url, donnees=None, json_=False):
        corps, sup = None, dict(entetes)
        if donnees is not None:
            corps = json.dumps(donnees).encode() if json_ else donnees
            sup["content-type"] = "application/json" if json_ else "application/octet-stream"
        req = urllib.request.Request(url, data=corps, headers=sup)
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())

    try:
        with open(chemin, "rb") as f:
            envoi = appel(f"{base}/upload", f.read())
        travail = appel(f"{base}/transcript",
                        {"audio_url": envoi["upload_url"], "language_code": "fr"}, json_=True)

        # On attend que ce soit prêt (quelques secondes en général).
        limite = time.time() + 600
        while time.time() < limite:
            etat = appel(f"{base}/transcript/{travail['id']}")
            if etat.get("status") == "completed":
                break
            if etat.get("status") == "error":
                return {"ok": False, "message": "AssemblyAI : " + str(etat.get("error"))}
            time.sleep(3)
        else:
            return {"ok": False, "message": "AssemblyAI a mis trop de temps."}
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:200]
        return {"ok": False, "message": f"AssemblyAI a refusé ({e.code}) : {detail}"}
    except (urllib.error.URLError, OSError, KeyError, ValueError) as e:
        return {"ok": False, "message": f"AssemblyAI injoignable : {e}"}

    texte = (etat.get("text") or "").strip()
    duree = float(etat.get("audio_duration") or 0)
    mots = len(texte.split()) if texte else 0
    return {"ok": True, "texte": texte, "mots": mots, "duree": round(duree, 1),
            "debit": round(mots / (duree / 60)) if duree > 0 else 0,
            "moteur": "AssemblyAI"}


def transcrire_whisper(chemin, nom):
    """Transcrit avec Whisper, sur cet ordinateur : gratuit et hors ligne."""
    if not os.path.exists(PYTHON_WHISPER):
        return {"ok": False, "message":
                "Whisper n'est pas installé. Dans le dossier tcf_simulateur, tape :\n"
                "    python3 -m venv .venv-whisper\n"
                "    .venv-whisper/bin/pip install faster-whisper"}

    print(f"→ Transcription de {nom} par Whisper… (patiente ~30-90 s)")
    try:
        proc = subprocess.run(
            [PYTHON_WHISPER, SCRIPT_TRANSCRIPTION, chemin],
            capture_output=True, text=True, timeout=DELAI_TRANSCRIPTION, cwd=DOSSIER,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "message": "⏳ La transcription a mis trop de temps."}

    try:
        res = json.loads(proc.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        detail = (proc.stderr or proc.stdout).strip()[-300:]
        return {"ok": False, "message": f"Transcription illisible.\n\n{detail}"}
    res["moteur"] = "Whisper"
    return res


def transcrire_audio(nom, refaire=False):
    """Écrit ce qui a été dit dans un enregistrement.

    On prend AssemblyAI si une clé est posée (c'est plus rapide), sinon
    Whisper en local. Si AssemblyAI échoue — clé périmée, plus de crédit,
    pas d'Internet — on bascule sur Whisper sans rien demander.

    Le résultat est gardé dans un fichier .txt à côté de l'audio : on ne
    refait le calcul que si on le demande explicitement (refaire=True).
    """
    chemin = chemin_audio(nom)
    if not chemin:
        return {"ok": False, "message": "Nom d'enregistrement invalide."}
    if not os.path.isfile(chemin):
        return {"ok": False, "message": "Enregistrement introuvable."}

    cache = chemin_transcription(chemin)
    if not refaire and os.path.exists(cache):
        try:
            with open(cache, encoding="utf-8") as f:
                garde = json.load(f)
            garde["ok"] = True
            return garde
        except (OSError, json.JSONDecodeError):
            pass  # cache abîmé : on recalcule

    res = None
    cle = cle_assemblyai()
    if cle:
        print(f"→ Transcription de {nom} par AssemblyAI…")
        res = transcrire_assemblyai(chemin, cle)
        if not res.get("ok"):
            print(f"   AssemblyAI n'a pas marché ({res.get('message')}) — on repasse sur Whisper.")
            res = None
    if res is None:
        res = transcrire_whisper(chemin, nom)

    if res.get("ok"):
        try:
            with open(cache, "w", encoding="utf-8") as f:
                json.dump({k: res[k] for k in ("texte", "mots", "duree", "debit", "moteur")
                           if k in res}, f, ensure_ascii=False)
        except OSError:
            pass  # tant pis, on retranscrira la prochaine fois
    return res


# ---------- Réception des enregistrements d'expression orale ----------
FORMATS_ORAL = FORMATS_AUDIO + (".mp3", ".m4a", ".aac", ".wav")


def enregistrer_oral(nom, donnees, sujet=0):
    """Reçoit un fichier audio du téléphone et le range dans le dossier des
    simulations d'expression orale. Le nom vient du téléphone : on le nettoie
    pour qu'il ne puisse pas sortir du dossier.

    `sujet` est le numéro du sujet affiché sur le téléphone au moment de
    l'enregistrement : c'est lui qui relie l'audio à l'énoncé travaillé."""
    if not donnees:
        return {"ok": False, "message": "Fichier vide."}
    if len(donnees) > TAILLE_AUDIO_MAX:
        return {"ok": False, "message": "Fichier trop volumineux."}
    nom = os.path.basename(nom or "").strip()
    nom = re.sub(r"[^A-Za-z0-9._-]", "_", nom)
    if not nom or nom.startswith("."):
        nom = "oral_" + time.strftime("%Y%m%d_%H%M%S") + ".m4a"
    if not nom.lower().endswith(FORMATS_ORAL):
        nom += ".m4a"
    try:
        os.makedirs(DOSSIER_SIM_ORAL, exist_ok=True)
        chemin = os.path.join(DOSSIER_SIM_ORAL, nom)
        # ne pas écraser : si le nom existe déjà, on suffixe -2, -3, …
        base, ext = os.path.splitext(chemin)
        i = 2
        while os.path.exists(chemin):
            chemin = f"{base}-{i}{ext}"
            i += 1
        with open(chemin, "wb") as f:
            f.write(donnees)
    except OSError as e:
        return {"ok": False, "message": f"Enregistrement impossible : {e}"}
    final = os.path.basename(chemin)
    if sujet:
        noter_sujet(final, sujet)
    return {"ok": True, "fichier": final, "taille": len(donnees), "sujet": sujet}


# ---------- Quel enregistrement va avec quel sujet ----------
# Le téléphone connaît le sujet affiché pendant qu'il enregistre ; il l'envoie
# avec le fichier. On le note ici, une ligne par audio — c'est le seul lien
# entre l'énoncé tiré sur l'ordinateur et la voix enregistrée dehors.
FICHIER_REGISTRE_ORAL = os.path.join(DOSSIER_SIM_ORAL, "registre.json")


def _registre_brut():
    try:
        with open(FICHIER_REGISTRE_ORAL, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def noter_sujet(fichier, sujet):
    """Associe un fichier reçu au sujet travaillé."""
    reg = _registre_brut()
    reg[fichier] = {"sujet": int(sujet), "recu": time.strftime("%Y-%m-%d %H:%M")}
    try:
        os.makedirs(DOSSIER_SIM_ORAL, exist_ok=True)
        with open(FICHIER_REGISTRE_ORAL, "w", encoding="utf-8") as f:
            json.dump(reg, f, ensure_ascii=False, indent=1)
    except OSError:
        pass          # le fichier audio est sauvé, c'est le principal


def _horodatage_du_nom(nom):
    """« tache-2_2026-08-17_13h56.m4a » → (2, '2026-08-17 13:56'). Le téléphone
    met la date dans le nom : c'est ce qui permet de rattraper les audios reçus
    avant que ce registre existe."""
    m = re.match(r"tache-(\d+)_(\d{4}-\d{2}-\d{2})_(\d{2})h(\d{2})", nom)
    if not m:
        return None, ""
    return int(m.group(1)), f"{m.group(2)} {m.group(3)}:{m.group(4)}"


def duree_audio(chemin):
    """Durée en secondes, ou 0. Sert à voir d'un coup d'œil si la tâche est
    complète ou si elle a été coupée."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", chemin],
            capture_output=True, text=True, timeout=10)
        return int(float(out.stdout.strip()))
    except (OSError, ValueError, subprocess.SubprocessError):
        return 0


FICHIER_JOURNAL_TEL = os.path.join(DOSSIER_SIM_ORAL, "journal_telephone.json")


def enregistrer_journal(donnees):
    """Reçoit le carnet du téléphone : quelle question va avec quel audio.

    Depuis que le téléphone tire lui-même les questions, c'est lui qui sait.
    L'ordinateur n'est plus qu'un tableau de bord : il range ce carnet et
    l'affiche. On le remplace entièrement à chaque envoi — le téléphone est la
    source de vérité, pas nous.
    """
    try:
        carnet = json.loads(donnees.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"ok": False, "message": "Carnet illisible."}
    if not isinstance(carnet, dict):
        return {"ok": False, "message": "Carnet invalide."}
    try:
        os.makedirs(DOSSIER_SIM_ORAL, exist_ok=True)
        with open(FICHIER_JOURNAL_TEL, "w", encoding="utf-8") as f:
            json.dump(carnet, f, ensure_ascii=False, indent=1)
    except OSError as e:
        return {"ok": False, "message": f"Enregistrement impossible : {e}"}
    return {"ok": True, "entrees": len(carnet)}


def _journal_telephone():
    try:
        with open(FICHIER_JOURNAL_TEL, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def registre_oral():
    """Les enregistrements avec leur question, pour le tableau de bord.

    La question vient du carnet du téléphone (`journal_telephone.json`) : c'est
    lui qui tire les sujets, donc lui qui sait. Pour les audios plus anciens,
    on retombe sur l'ancien registre local, puis sur une déduction par l'heure.
    """
    if not os.path.isdir(DOSSIER_SIM_ORAL):
        return []
    reg = _registre_brut()
    carnet = _journal_telephone()
    livrees = prompts_eo_livres()
    # (date de livraison, numéro), du plus récent au plus ancien
    jalons = sorted(((r.get("date", ""), r.get("n", 0)) for r in livrees),
                    reverse=True)

    out = []
    for nom in os.listdir(DOSSIER_SIM_ORAL):
        if not nom.lower().endswith(FORMATS_ORAL):
            continue
        chemin = os.path.join(DOSSIER_SIM_ORAL, nom)
        tache, quand = _horodatage_du_nom(nom)
        t2 = t3 = ""
        entree = carnet.get(nom)
        if entree:                          # le carnet du téléphone : il sait tout
            sujet = entree.get("sujet", 0)
            source = "téléphone"
            t2, t3 = entree.get("t2", ""), entree.get("t3", "")
            tache = entree.get("tache", tache)
            quand = entree.get("date", quand)
        elif reg.get(nom):                  # ancien registre, numéro seulement
            sujet, source = reg[nom].get("sujet", 0), "téléphone"
        else:                               # dernier sujet tiré avant cet audio
            sujet = next((n for d, n in jalons if quand and d and d <= quand), 0)
            source = "déduit" if sujet else ""
        # à défaut, les textes de l'ancienne liste du PC
        if not t3 and sujet:
            vieux = next((r for r in livrees if r.get("n") == sujet), None)
            if vieux:
                t2, t3 = vieux.get("t2", ""), vieux.get("t3", "")
        out.append({"nom": nom, "tache": tache, "quand": quand,
                    "sujet": sujet, "source": source, "t2": t2, "t3": t3,
                    "taille": os.path.getsize(chemin),
                    "duree": duree_audio(chemin)})
    out.sort(key=lambda f: (f["quand"], f["nom"]), reverse=True)
    return out


def lister_oral():
    """Les fichiers déjà reçus, du plus récent au plus ancien."""
    if not os.path.isdir(DOSSIER_SIM_ORAL):
        return []
    out = []
    for nom in os.listdir(DOSSIER_SIM_ORAL):
        if nom.lower().endswith(FORMATS_ORAL):
            chemin = os.path.join(DOSSIER_SIM_ORAL, nom)
            out.append({"nom": nom, "taille": os.path.getsize(chemin),
                        "modifie": os.path.getmtime(chemin)})
    out.sort(key=lambda f: f["modifie"], reverse=True)
    return out


# ---------- Prompts d'expression orale déjà livrés ----------
# On mémorise les combinaisons (Tâche 2 × Tâche 3) déjà données pour toujours en
# proposer une nouvelle, sans que Katherine ait à choisir quoi que ce soit.
FICHIER_PROMPTS_EO = os.path.join(DOSSIER, "mes_prompts_oraux.json")


def prompts_eo_livres():
    """Liste des prompts déjà livrés, du plus ancien au plus récent. Chaque
    entrée garde les textes des tâches pour que l'historique soit lisible même
    si la liste des sujets change."""
    try:
        with open(FICHIER_PROMPTS_EO, encoding="utf-8") as f:
            return json.load(f).get("livrees", [])
    except (OSError, json.JSONDecodeError):
        return []


def livrer_prompt_eo(rec):
    """Enregistre une combinaison livrée (Tâche 2 × Tâche 3), sans doublon."""
    if not isinstance(rec, dict) or "t2i" not in rec or "t3i" not in rec:
        return {"ok": False, "message": "Combinaison invalide."}
    livrees = prompts_eo_livres()
    cle = (rec.get("t2i"), rec.get("t3i"))
    if any((r.get("t2i"), r.get("t3i")) == cle for r in livrees):
        return {"ok": True, "total": len(livrees)}      # déjà noté
    rec["date"] = time.strftime("%Y-%m-%d %H:%M")
    rec["n"] = len(livrees) + 1
    livrees.append(rec)
    try:
        with open(FICHIER_PROMPTS_EO, "w", encoding="utf-8") as f:
            json.dump({"livrees": livrees}, f, ensure_ascii=False, indent=1)
    except OSError as e:
        return {"ok": False, "message": f"Enregistrement impossible : {e}"}
    return {"ok": True, "total": len(livrees)}


def reset_prompts_eo():
    try:
        if os.path.exists(FICHIER_PROMPTS_EO):
            os.remove(FICHIER_PROMPTS_EO)
    except OSError as e:
        return {"ok": False, "message": str(e)}
    return {"ok": True}


# Note : le téléphone tirait autrefois sa question ici (`/oral/sujet`). Il la
# tire maintenant tout seul, hors ligne — l'ordinateur ne fait plus que
# recevoir et afficher. La fonction a été retirée avec la route.


# ---------- Historique des simulations de compréhension orale ----------
def lister_simulations_co():
    """Les simulations archivées dans mes_simulations_co/, plus récentes d'abord.

    Comme pour les fiches d'expression écrite, les fichiers sont petits : on
    renvoie tout le contenu d'un coup plutôt que de faire un aller-retour par
    simulation.
    """
    if not os.path.isdir(DOSSIER_CO):
        return []
    fiches = []
    for nom in sorted(os.listdir(DOSSIER_CO)):
        if not nom.endswith(".json"):
            continue
        chemin = os.path.join(DOSSIER_CO, nom)
        try:
            with open(chemin, encoding="utf-8") as f:
                fiche = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        fiche["fichier"] = nom
        fiche["modifie"] = os.path.getmtime(chemin)
        fiches.append(fiche)
    fiches.sort(key=lambda f: f["modifie"], reverse=True)
    return fiches


def questions_vues():
    """Les identifiants de toutes les questions déjà posées, avec leur score.

    Renvoie {id: {"fois": n, "juste": n}} — « fois » sert à ne plus les tirer,
    « juste » à repérer celles qu'on rate systématiquement.
    """
    vues = {}
    for fiche in lister_simulations_co():
        for r in fiche.get("questions", []):
            qid = r.get("id")
            if qid is None:
                continue
            e = vues.setdefault(str(qid), {"fois": 0, "juste": 0})
            e["fois"] += 1
            if r.get("juste"):
                e["juste"] += 1
    return vues


def enregistrer_simulation_co(data):
    """Archive une simulation terminée dans mes_simulations_co/.

    Le nom du fichier porte la date et l'heure : deux simulations le même jour
    ne s'écrasent donc pas.
    """
    questions = data.get("questions")
    if not isinstance(questions, list) or not questions:
        return {"ok": False, "message": "Aucune question à enregistrer."}

    os.makedirs(DOSSIER_CO, exist_ok=True)
    horodatage = time.strftime("%Y%m%d_%H%M%S")
    fiche = {
        "date": data.get("date") or time.strftime("%Y-%m-%d %H:%M"),
        "source": data.get("source") or "banque",
        "score": data.get("score"),
        "total": data.get("total"),
        "duree": data.get("duree"),
        "piste": data.get("piste"),
        "pause": data.get("pause"),
        "questions": [{
            "id": r.get("id"),
            "niveau": r.get("niveau"),
            "titre": r.get("titre"),
            "choix": r.get("choix"),
            "reponse": r.get("reponse"),
            "juste": bool(r.get("juste")),
        } for r in questions],
    }
    nom = f"co_{horodatage}.json"
    try:
        with open(os.path.join(DOSSIER_CO, nom), "w", encoding="utf-8") as f:
            json.dump(fiche, f, ensure_ascii=False, indent=1)
    except OSError as e:
        return {"ok": False, "message": f"Enregistrement impossible : {e}"}
    return {"ok": True, "fichier": nom}


def supprimer_simulation_co(nom):
    """Supprime une simulation archivée (nom de fichier seul, pas de chemin)."""
    if not nom or "/" in nom or "\\" in nom or nom.startswith("."):
        return {"ok": False, "message": "Nom de fichier invalide."}
    chemin = os.path.join(DOSSIER_CO, nom)
    if os.path.dirname(os.path.abspath(chemin)) != os.path.abspath(DOSSIER_CO):
        return {"ok": False, "message": "Nom de fichier invalide."}
    try:
        os.remove(chemin)
    except FileNotFoundError:
        return {"ok": True}  # déjà absent : on considère que c'est bon
    except OSError as e:
        return {"ok": False, "message": f"Suppression impossible : {e}"}
    return {"ok": True}


# ---------- Micro du casque Bluetooth ----------
# Un casque Bluetooth ne peut pas faire les deux à la fois : soit il joue en
# haute qualité (A2DP) et son micro n'existe pas, soit il passe en mode
# « téléphone » (HFP) et le micro apparaît, mais le son devient moins bon.
# La page propose donc de basculer, parce que sans ça l'enregistrement
# échoue sans qu'on comprenne pourquoi.
PROFILS_MICRO = {"micro": "handsfree_head_unit", "musique": "a2dp_sink"}


def carte_bluetooth():
    """Le nom de la carte Bluetooth branchée, ou None s'il n'y en a pas."""
    try:
        proc = subprocess.run(["pactl", "list", "short", "cards"],
                              capture_output=True, text=True, timeout=10)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    for ligne in proc.stdout.splitlines():
        for champ in ligne.split():
            if champ.startswith("bluez_card."):
                return champ
    return None


def etat_micro():
    """Dit si un casque Bluetooth est là et s'il est en mode micro."""
    carte = carte_bluetooth()
    if not carte:
        # Pas de Bluetooth : le micro intégré de l'ordinateur fera l'affaire.
        return {"ok": True, "bluetooth": False, "micro": False, "carte": ""}
    try:
        proc = subprocess.run(["pactl", "list", "cards"],
                              capture_output=True, text=True, timeout=10)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {"ok": True, "bluetooth": True, "micro": False, "carte": carte}
    bloc = proc.stdout.split(f"Name: {carte}", 1)[-1].split("bluez_card.", 1)[0]
    m = re.search(r"Active Profile:\s*(\S+)", bloc)
    actif = m.group(1) if m else ""
    return {"ok": True, "bluetooth": True, "carte": carte, "profil": actif,
            "micro": actif == PROFILS_MICRO["micro"]}


def basculer_micro(mode):
    """Passe le casque en mode « micro » (HFP) ou « musique » (A2DP)."""
    profil = PROFILS_MICRO.get(mode)
    if not profil:
        return {"ok": False, "message": "Mode inconnu (attendu : micro ou musique)."}
    carte = carte_bluetooth()
    if not carte:
        return {"ok": False, "message": "Aucun casque Bluetooth détecté."}
    try:
        proc = subprocess.run(["pactl", "set-card-profile", carte, profil],
                              capture_output=True, text=True, timeout=15)
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return {"ok": False, "message": f"Changement impossible : {e}"}
    if proc.returncode != 0:
        return {"ok": False, "message": proc.stderr.strip()[:200] or "Changement refusé."}
    return etat_micro()


def construire_prompt(data):
    """Fabrique la consigne d'évaluation à partir des réponses de l'examen."""
    lignes = [
        "Tu es examinateur du TCF Canada (épreuve d'expression écrite).",
        "Évalue les 3 réponses ci-dessous comme à l'examen réel.",
        "",
        "Barème : chaque tâche est notée sur 20, avec un niveau CECR (A1 à C2).",
        "Critères : respect de la consigne, structure, grammaire et conjugaison,",
        "vocabulaire, cohérence, et nombre de mots.",
        "",
        "Pour CHAQUE tâche, donne dans cet ordre :",
        "  • Note : X/20 (niveau CECR)",
        "  • ✅ Points positifs : 2 à 4 points",
        "  • ⚠️ Axes d'amélioration : 2 à 4 points concrets, avec des exemples tirés du texte",
        "",
        "Puis un bilan global :",
        "  • 🎯 Note globale : X/20 et niveau estimé",
        "  • 💡 Les 2 leviers les plus importants pour progresser",
        "",
        "Ton : encourageant et bienveillant, comme un prof qui motive — mais honnête.",
        "Écris en français clair, en texte simple (pas de markdown lourd), avec des",
        "emojis pour repérer les sections. Sépare bien les 3 tâches.",
        "",
        "═══════════════════════════════════════",
        f"EXAMEN : {data.get('titre', 'Examen TCF')}",
        "═══════════════════════════════════════",
    ]
    for t in data.get("taches", []):
        lignes.append("")
        lignes.append(f"--- Tâche {t.get('numero')} : {t.get('type')} "
                      f"({t.get('motsMin')}-{t.get('motsMax')} mots recommandés) ---")
        lignes.append(f"Consigne : {t.get('sujet', '')}")
        for j, doc in enumerate(t.get("documents") or [], start=1):
            lignes.append(f"Document {j} : {doc}")
        reponse = (t.get("reponse") or "").strip()
        lignes.append(f"Réponse du candidat ({t.get('mots', 0)} mots) :")
        lignes.append('"""')
        lignes.append(reponse if reponse else "(vide)")
        lignes.append('"""')
    return "\n".join(lignes)


def message_indispo(detail=""):
    base = ("⏳ Claude n'est pas disponible pour le moment "
            "(peut-être plus de tokens pour aujourd'hui).\n"
            "Tes réponses sont gardées — réessaie plus tard.")
    return base + (f"\n\n(détail : {detail})" if detail else "")


def evaluer(data):
    """Appelle claude -p et renvoie {ok, evaluation} ou {ok:False, message}.

    Le front-end envoie déjà 'prompt' (source unique du texte d'évaluation) ;
    s'il est absent, on le reconstruit ici. En cas d'échec, le front-end propose
    de copier ce même prompt pour le coller dans ChatGPT.
    """
    prompt = data.get("prompt") or construire_prompt(data)
    try:
        proc = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json"],
            capture_output=True, text=True, timeout=DELAI_MAX, cwd=DOSSIER,
        )
    except FileNotFoundError:
        return {"ok": False, "message": "La commande 'claude' est introuvable. "
                "Vérifie que Claude Code est installé."}
    except subprocess.TimeoutExpired:
        return {"ok": False, "message": "⏳ Claude a mis trop de temps. Réessaie."}

    if proc.returncode != 0:
        return {"ok": False, "message": message_indispo(proc.stderr.strip()[:300])}

    try:
        res = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "message": message_indispo("réponse illisible")}

    if res.get("is_error"):
        return {"ok": False, "message": message_indispo(res.get("api_error_status") or "")}

    texte = (res.get("result") or "").strip()
    if not texte:
        return {"ok": False, "message": message_indispo("réponse vide")}
    return {"ok": True, "evaluation": texte}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=DOSSIER, **k)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def end_headers(self):
        # Sans ça, le navigateur garde une vieille copie de questions.js en
        # cache : on ajoute des combinaisons dans le fichier, mais l'accueil
        # continue d'afficher l'ancienne liste.
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def log_message(self, fmt, *args):
        # Ne jamais écrire la clé secrète (ni ?cle= ni l'en-tête) dans les logs.
        texte = re.sub(r"\bc(?:le)?=[^&\s\"]+", "cle=***", fmt % args)
        super().log_message("%s", texte)

    def _client_autorise(self):
        """Verrous en couches : l'ordinateur lui-même passe toujours ; un appareil
        du hotspot n'est accepté que (1) sur le seul endpoint de dépôt, (2) avec
        la clé secrète. Tout le reste — dont le réseau institutionnel — est refusé.
        """
        ip = self.client_address[0]
        if ip in IP_LOCALES:
            return True
        if not ip.startswith(PREFIXE_HOTSPOT):
            return False
        chemin = urllib.parse.urlparse(self.path).path.rstrip("/")
        if chemin not in CHEMINS_TELEPHONE:      # moindre privilège
            return False
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        # Adresse courte du téléchargement : un code bref suffit, parce qu'on le
        # tape sur un téléphone. Il n'ouvre QUE ça — impossible de déposer un
        # fichier ou de lire autre chose avec.
        if chemin == "/apk":
            return hmac.compare_digest(params.get("c", [""])[0], CODE_APK)
        fournie = self.headers.get("X-Cle") or params.get("cle", [""])[0]
        # comparaison à temps constant (pas d'indice par le temps de réponse)
        return hmac.compare_digest(fournie, CLE_TELEPHONE)

    def _envoyer_apk(self):
        """Sert l'APK au téléphone, par le seul port que le pare-feu laisse
        passer. Le navigateur du téléphone la télécharge, on la touche, et
        Android propose « Mettre à jour »."""
        try:
            with open(FICHIER_APK, "rb") as f:
                donnees = f.read()
        except OSError:
            self.send_error(404, "APK introuvable — lance construire.sh")
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.android.package-archive")
        self.send_header("Content-Length", str(len(donnees)))
        self.send_header("Content-Disposition", 'attachment; filename="TCF-Oral.apk"')
        self.end_headers()
        self.wfile.write(donnees)

    def do_GET(self):
        if not self._client_autorise():
            self.send_error(403, "Acces reserve au reseau local")
            return
        chemin = urllib.parse.urlparse(self.path).path.rstrip("/")
        if chemin == "/historique":
            self._json({"ok": True, "reponses": lister_reponses()})
            return
        if chemin == "/audios":
            self._json({"ok": True, "audios": lister_audios()})
            return
        if chemin == "/micro":
            self._json(etat_micro())
            return
        if chemin == "/co/historique":
            self._json({"ok": True, "simulations": lister_simulations_co()})
            return
        if chemin == "/co/vues":
            self._json({"ok": True, "vues": questions_vues()})
            return
        if chemin == "/eo/livrees":
            self._json({"ok": True, "livrees": prompts_eo_livres()})
            return
        if chemin == "/oral/liste":
            self._json({"ok": True, "fichiers": lister_oral()})
            return
        if chemin in ("/oral/apk", "/apk"):
            self._envoyer_apk()
            return
        if chemin == "/oral/registre":
            self._json({"ok": True, "enregistrements": registre_oral()})
            return
        # La racine sert désormais le tableau de bord qui réunit tous les
        # simulateurs. L'expression écrite reste accessible via /index.html.
        if chemin in ("", "/"):
            self.path = "/accueil.html"
        super().do_GET()

    def do_POST(self):
        if not self._client_autorise():
            self.send_error(403, "Acces reserve au reseau local")
            return
        url = urllib.parse.urlparse(self.path)
        chemin = url.path.rstrip("/")
        longueur = int(self.headers.get("Content-Length", 0))

        # L'audio arrive en binaire brut (et non en JSON) : c'est plus léger
        # et le navigateur peut envoyer le blob du MediaRecorder tel quel.
        if chemin == "/audio":
            if longueur > TAILLE_AUDIO_MAX:
                self._json({"ok": False, "message": "Enregistrement trop volumineux."})
                return
            params = urllib.parse.parse_qs(url.query)
            self._json(enregistrer_audio(
                params.get("nom", [""])[0],
                self.rfile.read(longueur) if longueur else b"",
                convertir=params.get("convertir", [""])[0] == "1"))
            return

        # Le carnet du téléphone : quelle question va avec quel enregistrement.
        if chemin == "/oral/journal":
            if longueur > 2_000_000:
                self._json({"ok": False, "message": "Carnet trop volumineux."})
                return
            self._json(enregistrer_journal(self.rfile.read(longueur) if longueur else b"{}"))
            return

        # Un enregistrement d'expression orale envoyé depuis le téléphone.
        if chemin == "/oral/envoyer":
            if longueur > TAILLE_AUDIO_MAX:
                self._json({"ok": False, "message": "Fichier trop volumineux."})
                return
            params = urllib.parse.parse_qs(url.query)
            try:
                sujet = int(params.get("sujet", ["0"])[0])
            except ValueError:
                sujet = 0
            self._json(enregistrer_oral(
                params.get("nom", [""])[0],
                self.rfile.read(longueur) if longueur else b"",
                sujet=sujet))
            return

        if chemin not in ("/evaluer", "/supprimer", "/enregistrer",
                          "/transcrire", "/supprimer_audio", "/micro",
                          "/co/enregistrer", "/co/supprimer",
                          "/eo/livrer", "/eo/reset"):
            self.send_error(404)
            return
        corps = self.rfile.read(longueur) if longueur else b"{}"
        try:
            data = json.loads(corps)
        except json.JSONDecodeError:
            self._json({"ok": False, "message": "Données invalides."})
            return
        if chemin == "/supprimer":
            self._json(supprimer_reponse(data.get("fichier", "")))
            return
        if chemin == "/enregistrer":
            self._json(enregistrer_reponse(data))
            return
        if chemin == "/transcrire":
            self._json(transcrire_audio(data.get("fichier", ""), data.get("refaire", False)))
            return
        if chemin == "/supprimer_audio":
            self._json(supprimer_audio(data.get("fichier", "")))
            return
        if chemin == "/micro":
            self._json(basculer_micro(data.get("mode", "")))
            return
        if chemin == "/eo/livrer":
            self._json(livrer_prompt_eo(data))
            return
        if chemin == "/eo/reset":
            self._json(reset_prompts_eo())
            return
        if chemin == "/co/enregistrer":
            self._json(enregistrer_simulation_co(data))
            return
        if chemin == "/co/supprimer":
            self._json(supprimer_simulation_co(data.get("fichier", "")))
            return
        print("→ Évaluation demandée, appel à Claude… (patiente ~30-60 s)")
        self._json(evaluer(data))

    def _json(self, obj):
        corps = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors()
        self.send_header("Content-Length", str(len(corps)))
        self.end_headers()
        self.wfile.write(corps)


class Serveur(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def adresse_hotspot():
    """L'IP de l'ordinateur sur le point d'accès WiFi (10.42.x), si actif."""
    try:
        for ligne in subprocess.run(["ip", "-4", "-o", "addr"],
                                     capture_output=True, text=True).stdout.splitlines():
            for mot in ligne.split():
                if mot.startswith(PREFIXE_HOTSPOT):
                    return mot.split("/")[0]
    except Exception:                                    # noqa: BLE001
        pass
    return None


if __name__ == "__main__":
    try:
        # 0.0.0.0 : on écoute partout, mais _client_autorise() ne laisse passer
        # que l'ordinateur et le hotspot (voir plus haut).
        with Serveur(("0.0.0.0", PORT), Handler) as httpd:
            print("=" * 50)
            print("  Simulateur TCF — serveur d'évaluation Claude")
            print("=" * 50)
            print(f"  ✅ Sur cet ordinateur : http://localhost:{PORT}")
            hs = adresse_hotspot()
            if hs:
                print(f"  📱 Depuis le téléphone (WiFi du PC) : http://{hs}:{PORT}")
            else:
                print("  📱 Pour recevoir le téléphone : lance le point d'accès")
                print("     (bash ~/tcf_oral_app/hotspot.sh), puis rebranche ce serveur.")
            print("  🔒 Seuls cet ordinateur et le WiFi du PC sont acceptés.")
            print("  ⏹  Pour arrêter : Ctrl+C")
            print("=" * 50)
            httpd.serve_forever()
    except OSError as e:
        print(f"❌ Impossible de démarrer sur le port {PORT} : {e}")
        print("   (Le serveur est peut-être déjà lancé dans une autre fenêtre.)")
    except KeyboardInterrupt:
        print("\n👋 Serveur arrêté. À bientôt !")
