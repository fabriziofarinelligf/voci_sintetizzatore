"""Regole di lettura imparate dalle revisioni: regole.json (in uso) e regole-proposte.json (candidate da approvare).
Uso: python regole.py lista | approva N | scarta N | conferma-pronunce
Le candidate arrivano da revisione.py --verifica (correzioni riscrivi/inglese risolte). conferma-pronunce approva da sola ogni sostituzione
con la prova della verifica (risolto true), se non contrasta con una regola esistente e da/a sono sensati; il resto resta da decidere a mano.
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
    for s in sorted(r["sostituzioni"], key=lambda s: -len(s["da"])):  # parola o gruppo intero, maiuscole comprese; prima i più lunghi
        testo = re.sub(rf"(?<!\w){re.escape(s['da'])}(?!\w)", lambda m: s["a"], testo)
    return testo

def prepara(testo, lingua, normalizza, r):
    """Testo che la voce legge: normalizza.py (non per l'inglese), poi le sostituzioni di regole.json."""
    if normalizza and lingua != "English":
        from normalizza import normalizza as norm
        testo = norm(testo)
    return applica(testo, r)

CAMPI = ("da", "a", "motivo", "fonte", "pagina", "parola")

def scarto(c, r):
    """Perché una candidata sostituzione non si approva da sola (None = si approva)."""
    if c.get("risolto") is not True: return "senza prova di verifica risolta"
    da, a = c.get("da", "").strip(), c.get("a", "").strip()
    if not 1 <= len(da.split()) <= 4: return "«da» deve avere da 1 a 4 parole"
    if not a or a == da: return "«a» vuoto o uguale a «da»"
    if any(s["da"] == da and s["a"] != a for s in r["sostituzioni"]): return "contrasta con una regola esistente"

def conferma_pronunce(proposte):
    r, resta = regole(), []
    for c in proposte:
        if c["tipo"] != "sostituzione": resta.append(c); continue
        perche = scarto(c, r)
        if perche:
            print(f"saltata: «{c.get('da', '')}» → «{c.get('a', '')}» ({perche})"); resta.append(c)
        elif any(s["da"] == c["da"] for s in r["sostituzioni"]):
            print(f"già in uso: «{c['da']}» → «{c['a']}»")
        else:
            r["sostituzioni"].append({k: c.get(k, "") for k in CAMPI}); print(f"approvata: «{c['da']}» → «{c['a']}» ({c['motivo']})")
    scrivi("regole.json", r); scrivi("regole-proposte.json", resta)
    print(f"{len(proposte) - len(resta)} tolte dalle candidate, {len(resta)} restano (python regole.py lista)")

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
                r["sostituzioni"].append({k: c.get(k, "") for k in CAMPI})
            else:
                r["inglese_tra_virgolette"] = True
            scrivi("regole.json", r)
        scrivi("regole-proposte.json", proposte)
        print(f"{'approvata' if sys.argv[1] == 'approva' else 'scartata'}: {c['tipo']} {c.get('da', '')!r} → {c.get('a', '')!r}")
    elif sys.argv[1:] == ["conferma-pronunce"]:
        conferma_pronunce(proposte)
    else:
        sys.exit(__doc__)
