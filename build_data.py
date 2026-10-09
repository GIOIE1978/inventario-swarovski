"""Converte data/righe.txt (righe fatture Swarovski) in data.json per la web app."""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent

# Codici colore/effetto Swarovski -> nome esteso (da catalogo).
# "verify": True = nome da confermare sul catalogo.
COLORI = {
    "CRY": ("Crystal", False),
    "CRY AB": ("Crystal AB", False),
    "CRY BB P": ("Crystal Bermuda Blue P", False),
    "CRY L163I": ("Crystal Sky Ignite", False),
    "CRY L180L": ("Crystal L180L", True),
    "CRY L181L": ("Crystal L181L", True),
    "CRY L182L": ("Crystal L182L", True),
    "JET": ("Jet", False),
    "AQUA": ("Aquamarine", False),
    "AMET": ("Amethyst", False),
    "LAME": ("Light Amethyst", False),
    "EMER": ("Emerald", False),
    "SAPH": ("Sapphire", False),
    "ROSE": ("Rose", False),
    "LROS": ("Light Rose", False),
    "SIAM": ("Siam", False),
    "LSIA": ("Light Siam", False),
    "SCAR": ("Scarlet", False),
    "LTQU": ("Light Turquoise", False),
    "TANZ": ("Tanzanite", False),
    "PERI": ("Peridot", False),
    "LCTO": ("Light Colorado Topaz", False),
    "GTOP": ("Golden Topaz", False),
    "DKOR": ("DKOR", True),
    "RC08": ("RC08", True),
    "RC09": ("RC09", True),
}
EFFETTI = {"SHIM": "Shimmer"}


def misura(tok):
    """'MM 100' -> 'MM 10', 'SS 39' -> 'SS 39', '180X130' -> '18x13 mm'."""
    if tok[0] == "MM":
        v = int(tok[1]) / 10
        return f"MM {v:g}"
    if tok[0] == "SS":
        return f"SS {tok[1]}"
    a, b = tok[0].split("X")
    return f"{int(a) / 10:g}x{int(b) / 10:g} mm"


def parse_descr(d):
    # es. "A 4460 MM 100 CRY L163I G2"
    t = d.split()
    assert t[0] == "A", d
    articolo = t[1]
    if t[2] in ("MM", "SS"):
        size, rest = misura(t[2:4]), t[4:]
    else:
        size, rest = misura([t[2]]), t[3:]
    rest = rest[:-1]  # qualità/confezione (G2, G7, GU, GZ)
    foiled = bool(rest) and rest[-1] == "F"
    if foiled:
        rest = rest[:-1]
    effetto = None
    if rest and rest[-1] in EFFETTI:
        effetto = EFFETTI[rest.pop()]
    sigla = " ".join(rest)
    nome, verify = COLORI.get(sigla, (sigla, True))
    colore = nome + (f" {effetto}" if effetto else "")
    return articolo, size, sigla, colore, foiled, verify


def main():
    righe = []
    for line in (ROOT / "data/righe.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        fatt, data, cod, descr, qta, tot = line.split("|")
        dd, mm, yy = data.split("-")
        righe.append(
            dict(fattura=fatt, data=f"{yy}-{mm}-{dd}", codice=cod, descr=descr,
                 qta=int(qta), costo=round(float(tot) / int(qta), 2), _tot=float(tot))
        )

    art = defaultdict(list)
    for r in righe:
        art[r["codice"]].append(r)

    articoli = []
    for cod, rs in art.items():
        rs.sort(key=lambda r: r["data"])
        a, size, sigla, colore, foiled, verify = parse_descr(rs[-1]["descr"])
        qta = sum(r["qta"] for r in rs)
        medio = sum(r["_tot"] for r in rs) / qta
        articoli.append(dict(
            codice=cod, articolo=a, misura=size, sigla=sigla, colore=colore,
            foiled=foiled, verifica=verify, descrOriginale=rs[-1]["descr"],
            qta=qta, costoUltimo=rs[-1]["costo"], costoMedio=round(medio, 2),
            costoMin=min(r["costo"] for r in rs), costoMax=max(r["costo"] for r in rs),
            acquisti=[dict(fattura=r["fattura"], data=r["data"], qta=r["qta"], costo=r["costo"]) for r in rs],
        ))
    articoli.sort(key=lambda x: (int(x["articolo"]), x["misura"], x["colore"]))

    fatture = sorted({(r["fattura"], r["data"]) for r in righe}, key=lambda x: x[1])
    out = dict(
        generato="2026-10-09",
        fornitore="Swarovski Int.le d'Italia Srl",
        numFatture=len(fatture),
        articoli=articoli,
    )
    (ROOT / "data.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"{len(righe)} righe, {len(fatture)} fatture, {len(articoli)} articoli, {sum(a['qta'] for a in articoli)} pezzi")
    for a in articoli:
        if a["verifica"]:
            print("da verificare:", a["codice"], a["descrOriginale"])


if __name__ == "__main__":
    main()
