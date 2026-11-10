"""Riepilogo del giro con revisione Gemini, una pagina per cartella.
Uso: python report.py LAVORO [LAVORO ...]"""
import glob, json, os, sys

def carica(lavoro, nome):
    return {int(p.rsplit("-", 1)[1][:-5]): json.load(open(p)) for p in glob.glob(os.path.join(lavoro, f"{nome}-*.json"))}

def report(lavoro):
    rev, mod, ver = carica(lavoro, "revisione"), carica(lavoro, "modifiche"), carica(lavoro, "verifica")
    pagina = json.load(open(os.path.join(lavoro, "manifest.json")))["pagina"]
    righe = [f"Pagina {pagina} ({lavoro})"]
    if not rev: return righe + ["  nessuna revisione"]
    chiavi = list(rev[1]["voti"])
    for n in sorted(rev):
        righe.append(f"  voti revisione {n} ({rev[n]['modello']}): " + ", ".join(f"{k} {rev[n]['voti'][k]:g}" for k in chiavi))
    for n in sorted(rev):
        pp = rev[n]["problemi"]; gravi = [p for p in pp if p["gravita"] >= 2]
        righe.append(f"  giro {n}: {len(pp)} problemi trovati, {len(gravi)} di gravità 2-3, {len(mod.get(n, []))} modifiche applicate")
        if n in ver:
            esiti = {e["frase_id"]: e for e in ver[n]["esiti"]}
            risolte = [i for i in ver[n]["frasi"] if esiti.get(i, {}).get("risolto")]
            aperte = [i for i in ver[n]["frasi"] if i not in risolte]
            righe.append(f"    verifica: {len(risolte)}/{len(ver[n]['frasi'])} frasi risolte" + (f"; non risolte: " + "; ".join(
                f"{i} ({esiti[i]['nota'] if i in esiti else 'nessun esito'})" for i in aperte) if aperte else ""))
        elif n in mod:
            righe.append("    verifica non ancora fatta")
    err = os.path.join(lavoro, "errori-testo.md")
    errori = open(err).read().splitlines() if os.path.exists(err) else []
    righe.append(f"  errori nel testo del manuale: {len(errori)}" + "".join(f"\n    {e}" for e in errori))
    return righe

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    for l in sys.argv[1:]: print("\n".join(report(l)))
