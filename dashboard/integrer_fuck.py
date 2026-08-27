#!/usr/bin/env python3
"""
Intègre les questions de fuck-tcf.xyz dans banque/questions_O.json, en évitant
les doublons avec ecoutetcf.

Déduplication : similarité de Jaccard sur l'ensemble des mots de la
transcription (robuste à la ponctuation, aux élisions et à l'ordre). Au-dessus
du seuil, on considère que c'est la même question et on ne la télécharge pas.

Le métadonnées Firestore sont déjà dans banque/_cache/fuck_firestore_brut.json.
L'audio est public (Firebase Storage ou WordPress) : aucun token nécessaire.
"""
import json, re, subprocess, unicodedata, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BANQUE = Path("/home/katherine/tcf_simulateur/banque")
BRUT = BANQUE / "_cache" / "fuck_firestore_brut.json"
SEUIL = 0.75                     # Jaccard ≥ 0.75 → doublon
CEFR_NUM = {"A1":1, "A2":2, "B1":3, "B2":4, "C1":5, "C2":6}
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"


def mots(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return frozenset(re.sub(r"[^a-z0-9]", " ", s.lower()).split())


def jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / (len(a) + len(b) - inter)


def main():
    banc = json.load(open(BANQUE / "questions_O.json"))
    ec = banc["questions"]
    ft = json.load(open(BRUT))["questions"]

    # index ecoutetcf : ensembles de mots, groupés par longueur pour accélérer
    ec_sets = [mots(" ".join(q.get("transcription") or [])) for q in ec]
    ec_sets = [s for s in ec_sets if s]
    dejaVus = {q["id"] for q in ec}

    def est_doublon(sig):
        # blocage : on ne compare qu'aux transcriptions de taille voisine
        n = len(sig)
        for s in ec_sets:
            if abs(len(s) - n) > n * 0.5:
                continue
            if jaccard(sig, s) >= SEUIL:
                return True
        return False

    # candidats fuck-tcf : audio + transcript + options exploitables
    nouveaux = []
    dupes = 0
    for qid, q in ft.items():
        if not q.get("audio_url") or not q.get("transcript"):
            continue
        opts = q.get("question_options") or []
        if len(opts) < 2:
            continue
        if est_doublon(mots(q["transcript"])):
            dupes += 1
            continue
        nouveaux.append((qid, q))

    print(f"fuck-tcf jouables : {dupes + len(nouveaux)}  "
          f"(doublons {dupes}, NOUVELLES {len(nouveaux)})")

    (BANQUE / "audio").mkdir(exist_ok=True)
    (BANQUE / "images").mkdir(exist_ok=True)

    def convertir(item):
        qid, q = item
        court = qid.split("-")[0]
        bid = "ft-" + court
        # options triées A,B,C,D
        opts = sorted(q["question_options"], key=lambda o: o.get("option_key", ""))
        options, rep = [], 0
        for i, o in enumerate(opts):
            lettre = o.get("option_key") or chr(65 + i)
            options.append(f"{lettre}. {o.get('text','').strip()}")
            if o.get("is_correct"):
                rep = i
        titre = ", ".join(q.get("keywords") or []) or \
            " ".join((q.get("transcript") or "").split()[:6])
        charge = sum(len(re.sub(r"^[A-D]\.\s*", "", o).strip()) for o in options)

        # téléchargement audio
        rel = f"audio/{bid}.mp3"
        f = BANQUE / rel
        duree = 0.0
        if not f.exists() or f.stat().st_size == 0:
            try:
                req = urllib.request.Request(q["audio_url"], headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=90) as r:
                    f.write_bytes(r.read())
            except Exception as e:                        # noqa: BLE001
                print(f"  audio ÉCHEC {bid}: {e}")
                return None
        try:
            duree = round(float(subprocess.check_output(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "csv=p=0", str(f)], text=True).strip()), 1)
        except Exception:
            pass

        return {
            "id": bid,
            "titre": titre[:80],
            "consigne": "Écoutez le document, puis choisissez la bonne réponse.",
            "niveau": CEFR_NUM.get(q.get("level"), 3),
            "options": options,
            "reponse": rep,
            "transcription": [q.get("transcript", "")],
            "segments": None,
            "description": None,
            "theme": None,
            "motsCles": q.get("keywords") or [],
            "emoji": None,
            "memo": q.get("key_sentence_orig"),
            "audio": rel,
            "audioAmeliore": None,
            "image": None,
            "duree": duree,
            "charge": charge,
            "source": "fuck-tcf",
        }

    ajoutes = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for i, r in enumerate(ex.map(convertir, nouveaux), 1):
            if r:
                ajoutes.append(r)
            if i % 40 == 0 or i == len(nouveaux):
                mo = sum(f.stat().st_size for f in (BANQUE / "audio").iterdir()) / 1e6
                print(f"  {i}/{len(nouveaux)}  ({mo:.0f} Mo au total)")

    # fusion
    ec.extend(ajoutes)
    banc["total"] = len(ec)
    banc["sources"] = "ecoutetcf + fuck-tcf"
    json.dump(banc, open(BANQUE / "questions_O.json", "w"),
              ensure_ascii=False, indent=1)

    import collections
    parNiv = collections.Counter(q["niveau"] for q in ec)
    print(f"\nbanque fusionnée : {len(ec)} questions uniques")
    print("par niveau : " + "  ".join(
        f"n{k}={parNiv[k]}" for k in sorted(parNiv)))


if __name__ == "__main__":
    main()
