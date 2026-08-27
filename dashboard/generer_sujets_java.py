#!/usr/bin/env python3
"""Recopie les sujets d'expression orale PARTOUT où ils servent.

sujets_oraux.json est la SEULE source. Tout le reste en est une copie
fabriquée par ce script — il n'y a donc jamais deux banques différentes :

    sujets_oraux.json
      ├─→ ~/tcf_oral_app/.../Sujets.java   (le téléphone, hors ligne)
      ├─→ questions_oral.js                (le simulateur du PC)
      ├─→ oral_mobile.html                 (copie de secours embarquée)
      └─→ site/index.html                  (la page publiée)

À lancer après avoir ajouté ou corrigé un sujet dans sujets_oraux.json :

    python3 generer_sujets_java.py
    bash ~/tcf_oral_app/construire.sh     # puis réinstaller l'APK
"""
import json
import os
import re

DOSSIER = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(DOSSIER, "sujets_oraux.json")
JAVA = os.path.expanduser("~/tcf_oral_app/src/com/katherine/tcforal/Sujets.java")
JS = os.path.join(DOSSIER, "questions_oral.js")
MOBILE = os.path.join(DOSSIER, "oral_mobile.html")
SITE = os.path.join(DOSSIER, "site", "index.html")


def texte_js(s):
    """Une chaîne source sûre — sans jamais toucher aux mots eux-mêmes."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# ---------------------------------------------------------------- le téléphone
def ecrire_java(t2, t3, source):
    def tableau(nom, liste):
        lignes = [f"    static final String[] {nom} = {{"]
        lignes += ["        " + texte_js(s) + "," for s in liste]
        lignes.append("    };")
        return "\n".join(lignes)

    src = f'''package com.katherine.tcforal;

/**
 * Les sujets d'expression orale, DANS le téléphone.
 *
 * Généré depuis tcf_simulateur/sujets_oraux.json (source : {source}).
 * Le téléphone n'a plus besoin de l'ordinateur pour tirer une question : il a
 * tout ici. La tâche 2 et la tâche 3 se tirent séparément, {len(t2)} et {len(t3)}
 * énoncés, soit {len(t2) * len(t3)} combinaisons possibles.
 *
 * Pour régénérer après avoir ajouté des sujets :
 *   python3 ~/tcf_simulateur/generer_sujets_java.py
 */
final class Sujets {{

    private Sujets() {{}}

{tableau("TACHE2", t2)}

{tableau("TACHE3", t3)}

    static int combinaisons() {{ return TACHE2.length * TACHE3.length; }}
}}
'''
    with open(JAVA, "w", encoding="utf-8") as f:
        f.write(src)


# ------------------------------------------------- le simulateur du PC (paires)
def paires(t2, t3):
    """Les pages du PC proposent une LISTE de combinaisons numérotées.

    On apparie donc énoncé n° i de la tâche 2 avec énoncé n° i de la tâche 3 :
    autant de combinaisons que d'énoncés, chacune tirée du même banc que le
    téléphone. (Le téléphone, lui, mélange librement les deux tâches.)
    """
    n = min(len(t2), len(t3))
    return [(t2[i], t3[i]) for i in range(n)]


def ecrire_js(t2, t3):
    src = open(JS, encoding="utf-8").read()
    combos = []
    for n, (a, b) in enumerate(paires(t2, t3), 1):
        combos.append(f'''  // ---------------------------------------------------------
  {{
    id: "oral-{n}",
    titre: "Oral — Combinaison {n}",
    sousTitre: "3 tâches",
    taches: [
      {{
        type: "Présentation personnelle",
        description: O_PRESENTATION,
        prep: 0,
        duree: 120,
        sujet: "Bonjour, présentez-vous. Parlez-moi de vous pendant deux minutes.",
        points: POINTS_PRESENTATION,
        aide: AIDE_PRESENTATION,
      }},
      {{
        type: "Interaction orale",
        description: O_INTERACTION,
        prep: 120,
        duree: 210,
        sujet:
          {texte_js(a)},
        aide: AIDE_INTERACTION,
      }},
      {{
        type: "Argumentation",
        description: O_ARGUMENTATION,
        prep: 0,
        duree: 270,
        sujet:
          {texte_js(b)},
        aide: AIDE_ARGUMENTATION,
      }},
    ],
  }},
''')
    neuf = ("window.QUESTIONS_ORAL = [\n"
            "  // ⚠️ Bloc fabriqué par generer_sujets_java.py depuis\n"
            "  //    sujets_oraux.json — ne pas le corriger à la main :\n"
            "  //    corrige le JSON, puis relance le script.\n"
            + "\n".join(combos) + "];")
    src = re.sub(r"window\.QUESTIONS_ORAL = \[.*?\n\];",
                 lambda m: neuf, src, count=1, flags=re.S)
    open(JS, "w", encoding="utf-8").write(src)


# ------------------------------------------------------ les deux pages web
def ecrire_page(chemin, nom_tableau, t2, t3):
    src = open(chemin, encoding="utf-8").read()
    lignes = [f"const {nom_tableau} = ["]
    lignes.append("  // ⚠️ Fabriqué par generer_sujets_java.py depuis sujets_oraux.json.")
    for a, b in paires(t2, t3):
        lignes.append("  [" + texte_js(a) + ",")
        lignes.append("   " + texte_js(b) + "],")
    lignes.append("];")
    neuf = "\n".join(lignes)
    motif = r"const " + nom_tableau + r" = \[.*?\n\];"
    src, n = re.subn(motif, lambda m: neuf, src, count=1, flags=re.S)
    if n == 0:
        raise SystemExit(f"⚠️  {os.path.basename(chemin)} : « const {nom_tableau} = [ … ]; » introuvable")
    open(chemin, "w", encoding="utf-8").write(src)


def main():
    with open(SOURCE, encoding="utf-8") as f:
        d = json.load(f)
    t2, t3 = d["tache2"], d["tache3"]

    ecrire_java(t2, t3, d.get("source", ""))
    ecrire_js(t2, t3)
    ecrire_page(MOBILE, "SECOURS", t2, t3)
    ecrire_page(SITE, "SUJETS", t2, t3)

    print(f"✅ {len(t2)} énoncés de tâche 2 · {len(t3)} de tâche 3 "
          f"= {len(t2) * len(t3)} combinaisons dans le téléphone")
    print(f"   {len(paires(t2, t3))} combinaisons numérotées dans les pages du PC")
    for p in (JAVA, JS, MOBILE, SITE):
        print("   ·", p.replace(os.path.expanduser("~"), "~"))
    print("\n   Pense à recompiler :  bash ~/tcf_oral_app/construire.sh")


if __name__ == "__main__":
    main()
