#!/usr/bin/env python3
"""
Construit la banque de questions dédupliquée à partir de tous les tests
d'ÉcouteTCF, puis télécharge le média de chaque question unique.

Le site sert 2535 questions orales réparties en 65 tests, mais il n'y a que
837 questions distinctes : chacune revient environ 3 fois. On indexe donc par
`id` de question, et le média est nommé d'après cet id — un fichier par
question, jamais deux fois la même.

Usage:
    export ECOUTETCF_TOKEN='<auth_token>'
    python3 construire_banque.py            # oral, deux pistes audio
    python3 construire_banque.py --type E   # écrit
    python3 construire_banque.py --metadonnees-seulement
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = "https://www.ecoutetcf.com"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

RACINE = Path(__file__).resolve().parent
BANQUE = RACINE / "banque"
CACHE = BANQUE / "_cache"


def token():
    t = os.environ.get("ECOUTETCF_TOKEN", "").strip()
    if not t:
        sys.exit("ECOUTETCF_TOKEN manquant. export ECOUTETCF_TOKEN='<auth_token>'")
    return t


TOK = None


def get(url, json_=True):
    r = urllib.request.Request(url, headers={
        "User-Agent": UA, "Cookie": f"auth_token={TOK}",
        "Accept": "*/*", "Referer": BASE + "/"})
    with urllib.request.urlopen(r, timeout=90) as f:
        d = f.read()
    return json.loads(d) if json_ else d


def media(chemin):
    return get(BASE + "/api/media?path=" + urllib.parse.quote(chemin, safe=""),
               json_=False)


# ------------------------------------------------------------ catalogue
def catalogue():
    c = get(BASE + "/api/tests")
    return c["data"] if isinstance(c, dict) else c


def charger_test(t):
    """Un test, depuis le cache si possible (les métadonnées bougent peu)."""
    lid = t["legacyId"]
    f = CACHE / f"{lid}.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    m = re.match(r"(\d+)-(\d+)-([OE])$", lid)
    if not m:
        return None
    d = get(f"{BASE}/api/tests/by-data?suite={int(m.group(1))}"
            f"&type={m.group(3)}&number={int(m.group(2))}")
    f.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    time.sleep(0.1)
    return d


# ------------------------------------------------------------ programme
def main():
    global TOK
    p = argparse.ArgumentParser()
    p.add_argument("--type", choices=["O", "E"], default="O")
    p.add_argument("--metadonnees-seulement", action="store_true",
                   help="ne pas télécharger l'audio ni les images")
    p.add_argument("--sans-ameliore", action="store_true",
                   help="ne pas télécharger la piste premium")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()
    TOK = token()

    CACHE.mkdir(parents=True, exist_ok=True)
    cat = [t for t in catalogue() if t.get("type") == args.type]
    print(f"{len(cat)} tests de type {args.type}")

    tests = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        for i, d in enumerate(ex.map(charger_test, cat), 1):
            if d and d.get("success"):
                tests.append(d["data"])
            if i % 20 == 0 or i == len(cat):
                print(f"  métadonnées {i}/{len(cat)}")

    # ---- déduplication par id de question -------------------------------
    banque = {}
    vu_dans = {}
    for d in tests:
        for rang, q in enumerate(d["questions"], 1):
            vu_dans.setdefault(q["id"], []).append(f"{d['legacyId']}#{rang}")
            if q["id"] not in banque:
                banque[q["id"]] = q

    servies = sum(len(d["questions"]) for d in tests)
    print(f"\n{servies} questions servies → {len(banque)} uniques "
          f"({servies/max(len(banque),1):.1f}x de répétition)")

    ordre = sorted(banque.values(), key=lambda q: (q.get("complexity") or 0, q["id"]))

    # ---- média -----------------------------------------------------------
    dossiers = ["audio", "images"] + ([] if args.sans_ameliore else ["audio_ameliore"])
    for d in dossiers:
        (BANQUE / d).mkdir(parents=True, exist_ok=True)

    def telecharger(q):
        res = {"audio": None, "audioAmeliore": None, "image": None}
        ap, ip = q.get("audioPath"), q.get("imagePath")
        taches = []
        if ap:
            ext = Path(ap).suffix or ".mp3"
            taches.append(("audio", f"audio/{q['id']}{ext}", ap))
            if not args.sans_ameliore:
                taches.append(("audioAmeliore",
                               f"audio_ameliore/{q['id']}{ext}", f"premium/{ap}"))
        if ip:
            ext = ".webp" if ip.endswith(".webp") else (Path(ip).suffix or ".jpg")
            taches.append(("image", f"images/{q['id']}{ext}", ip))
        for cle, rel, src in taches:
            f = BANQUE / rel
            if not args.force and f.exists() and f.stat().st_size > 0:
                res[cle] = rel
                continue
            for essai in range(3):
                try:
                    f.write_bytes(media(src))
                    res[cle] = rel
                    break
                except Exception as e:                        # noqa: BLE001
                    if essai == 2:
                        print(f"  ÉCHEC q{q['id']} {cle} : {e}")
                    else:
                        time.sleep(1.5 * (essai + 1))
        return q["id"], res

    medias = {}
    if not args.metadonnees_seulement:
        avec = [q for q in ordre if q.get("audioPath") or q.get("imagePath")]
        print(f"téléchargement du média de {len(avec)} questions…")
        with ThreadPoolExecutor(max_workers=4) as ex:
            for i, (qid, res) in enumerate(ex.map(telecharger, avec), 1):
                medias[qid] = res
                if i % 25 == 0 or i == len(avec):
                    taille = sum(f.stat().st_size for d in dossiers
                                 for f in (BANQUE / d).iterdir()) / 1e6
                    print(f"  {i}/{len(avec)}  ({taille:.0f} Mo)")

    # ---- fichier de la banque -------------------------------------------
    sortie = []
    for q in ordre:
        m = medias.get(q["id"], {})
        sortie.append({
            "id": q["id"],
            "titre": q.get("title"),
            "consigne": q.get("task"),
            "niveau": q.get("complexity"),
            "options": q.get("options") or [],
            "reponse": q.get("correctAnswer"),
            "transcription": q.get("transcription"),
            "segments": q.get("transcriptionSegments"),
            "description": q.get("description"),
            "theme": q.get("topic"),
            "motsCles": q.get("keywords"),
            "emoji": q.get("emoji"),
            "memo": q.get("answerMemo"),
            "audio": m.get("audio"),
            "audioAmeliore": m.get("audioAmeliore"),
            "image": m.get("image"),
            "vuDans": vu_dans.get(q["id"], []),
        })

    f = BANQUE / f"questions_{args.type}.json"
    f.write_text(json.dumps({
        "type": args.type,
        "total": len(sortie),
        "testsSources": len(tests),
        "questionsServies": servies,
        "questions": sortie,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    par_niveau = {}
    for q in sortie:
        par_niveau[q["niveau"]] = par_niveau.get(q["niveau"], 0) + 1
    print("\npar niveau : " + "  ".join(
        f"n{k}={v}" for k, v in sorted(par_niveau.items(), key=lambda x: (x[0] or 0))))
    print(f"OK → {f}")


if __name__ == "__main__":
    main()
