#!/usr/bin/env python3
"""
Télécharge le matériel d'un test ÉcouteTCF (audio + images + questions)
pour un usage personnel hors ligne.

Usage:
    export ECOUTETCF_TOKEN='<auth_token cookie>'
    python3 telecharger_tcf.py 148 O 1
    python3 telecharger_tcf.py 148 O 1 --premium      # audio "Amélioré"

Sortie: tests/<suite>-<number>-<type>/
    test.json      questions normalisées
    audio/qN.mp3
    images/qN.webp
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://www.ecoutetcf.com"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

RACINE = Path(__file__).resolve().parent


def token():
    t = os.environ.get("ECOUTETCF_TOKEN", "").strip()
    if not t:
        sys.exit("ECOUTETCF_TOKEN manquant. export ECOUTETCF_TOKEN='<auth_token>'")
    return t


def get(url, tok):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Cookie": f"auth_token={tok}",
        "Accept": "*/*",
        "Referer": BASE + "/",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def media(chemin, tok):
    """Le endpoint /api/media renvoie un 307 vers une URL R2 signée."""
    url = BASE + "/api/media?path=" + urllib.parse.quote(chemin, safe="")
    return get(url, tok)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("suite", type=int)
    p.add_argument("type", choices=["O", "E"], help="O = oral, E = écrit")
    p.add_argument("number", type=int)
    p.add_argument("--premium", action="store_true",
                   help="télécharger aussi la piste audio améliorée")
    p.add_argument("--force", action="store_true",
                   help="retélécharger les fichiers déjà présents")
    args = p.parse_args()

    tok = token()
    slug = f"{args.suite}-{args.number}-{args.type}"
    dest = RACINE / "tests" / slug
    (dest / "audio").mkdir(parents=True, exist_ok=True)
    (dest / "images").mkdir(parents=True, exist_ok=True)
    if args.premium:
        (dest / "audio_ameliore").mkdir(parents=True, exist_ok=True)

    url = (f"{BASE}/api/tests/by-data?suite={args.suite}"
           f"&type={args.type}&number={args.number}")
    brut = json.loads(get(url, tok))
    if not brut.get("success"):
        sys.exit(f"Réponse inattendue: {brut}")
    data = brut["data"]
    questions = data["questions"]
    print(f"Test {slug} — {len(questions)} questions")

    (dest / "api_brut.json").write_text(
        json.dumps(brut, ensure_ascii=False, indent=2), encoding="utf-8")

    sortie = []
    for i, q in enumerate(questions, start=1):
        item = {
            "n": i,
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
            "audio": None,
            "audioAmeliore": None,
            "image": None,
        }

        ap = q.get("audioPath")
        if ap:
            ext = Path(ap).suffix or ".mp3"
            pistes = [("audio", ap)]
            if args.premium:
                pistes.append(("audio_ameliore", f"premium/{ap}"))
            for dossier, src in pistes:
                rel = f"{dossier}/q{i}{ext}"
                f = dest / rel
                if args.force or not f.exists() or f.stat().st_size == 0:
                    try:
                        f.write_bytes(media(src, tok))
                    except Exception as e:                   # noqa: BLE001
                        print(f"  q{i} {dossier} ÉCHEC ({e})")
                        rel = None
                    time.sleep(0.15)
                item["audio" if dossier == "audio" else "audioAmeliore"] = rel

        ip = q.get("imagePath")
        if ip:
            ext = ".webp" if ip.endswith(".webp") else Path(ip).suffix
            rel = f"images/q{i}{ext}"
            f = dest / rel
            if args.force or not f.exists() or f.stat().st_size == 0:
                try:
                    f.write_bytes(media(ip, tok))
                except Exception as e:                       # noqa: BLE001
                    print(f"  q{i} image ÉCHEC ({e})")
                    rel = None
                time.sleep(0.15)
            item["image"] = rel

        sortie.append(item)
        print(f"  q{i:>2} niveau {item['niveau']} "
              f"{'♪' if item['audio'] else ' '}"
              f"{'▣' if item['image'] else ' '}  {item['titre']}")

    (dest / "test.json").write_text(json.dumps({
        "slug": slug,
        "suite": args.suite,
        "type": args.type,
        "number": args.number,
        "premium": args.premium,
        "questions": sortie,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nOK → {dest}")


if __name__ == "__main__":
    main()
