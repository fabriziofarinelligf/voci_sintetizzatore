"""Regole di lettura imparate dalle revisioni: regole.json (in uso) e regole-proposte.json (candidate da approvare).
Uso: python regole.py lista | approva N | scarta N
Le candidate arrivano da revisione.py --verifica (correzioni riscrivi/inglese risolte); nessuna si approva da sola.
VOCI_REGOLE_DIR cambia la cartella dei due file (default: la radice del repo)."""
import json, os, re, sys

def percorso(nome):
    return os.path.join(os.environ.get("VOCI_REGOLE_DIR") or os.path.dirname(os.path.abspath(__file__)), nome)

def leggi(nome, vuoto):
    try:
        return json.load(open(percorso(nome)))
    except FileNotFoundError:
        return vuoto

def scrivi(nome, dati):
    json.dump(dati, open(percorso(nome), "w"), ensure_ascii=False, indent=1)

def regole():
    return leggi("regole.json", {"sostituzioni": [], "inglese_tra_virgolette": False})

CITAZIONE = re.compile(r'^\s*["“”][^"“”]+["“”][.;:!?]*\s*$')

def applica(testo, r):
    for s in r["sostituzioni"]:  # parola o gruppo di parole intero, maiuscole comprese
        testo = re.sub(rf"(?<!\w){re.escape(s['da'])}(?!\w)", lambda m: s["a"], testo)
    return testo

def prepara(testo, lingua, normalizza, r):
    """Testo che la voce legge: normalizza.py (non per l'inglese), poi le sostituzioni di regole.json."""
    if normalizza and lingua != "English":
        from normalizza import normalizza as norm
        testo = norm(testo)
    return applica(testo, r)

def inglese(testo, r):
    return r["inglese_tra_virgolette"] and bool(CITAZIONE.match(testo))

if __name__ == "__main__":
    proposte = leggi("regole-proposte.json", [])
    if sys.argv[1:2] == ["lista"]:
        for i, c in enumerate(proposte, 1):
            cosa = f"«{c['da']}» → «{c['a']}»" if c["tipo"] == "sostituzione" else "citazioni tra virgolette lette in inglese"
            print(f"{i}. {cosa} — {c['motivo']} (pagina {c['pagina']}, es. «{c['esempio']}»)")
        print(f"{len(proposte)} candidate" if proposte else "nessuna candidata")
    elif sys.argv[1:2] in (["approva"], ["scarta"]) and len(sys.argv) == 3:
        n = int(sys.argv[2])
        if not 1 <= n <= len(proposte):
            sys.exit(f"candidata {n} inesistente (sono {len(proposte)})")
        c = proposte.pop(n - 1)
        if sys.argv[1] == "approva":
            r = regole()
            if c["tipo"] == "sostituzione":
                r["sostituzioni"].append({k: c[k] for k in ("da", "a", "motivo", "fonte")})
            else:
                r["inglese_tra_virgolette"] = True
            scrivi("regole.json", r)
        scrivi("regole-proposte.json", proposte)
        print(f"{'approvata' if sys.argv[1] == 'approva' else 'scartata'}: {c['tipo']} {c.get('da', '')!r} → {c.get('a', '')!r}")
    else:
        sys.exit(__doc__)
