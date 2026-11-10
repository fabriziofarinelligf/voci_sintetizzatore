"""Fase 4 del giro: applica al manifest i problemi di gravità 2 o 3 di una revisione. Al massimo 2 giri di correzione per pagina.
Uso: python correggi.py LAVORO LAVORO/revisione-N.json
rigenera -> seme + 1; riscrivi -> testo_letto = valore; inglese -> lingua English; pausa -> pausa_dopo = valore (0,2-1,5 s);
errore_testo -> riga in LAVORO/errori-testo.md, audio invariato. Scrive LAVORO/modifiche-N.json e stampa il comando sintetizza --solo."""
import glob, json, os, sys

MAX_GIRI = 2

def correggi(lavoro, revisione):
    n = len(glob.glob(os.path.join(lavoro, "modifiche-*.json"))) + 1
    if n > MAX_GIRI: sys.exit(f"pagina già corretta {MAX_GIRI} volte: il giro {n} non si fa, guarda i problemi rimasti a mano")
    mf = os.path.join(lavoro, "manifest.json"); m = json.load(open(mf)); per_id = {f["id"]: f for f in m["frasi"]}
    mod, rigenerate, errori = [], set(), []
    for p in json.load(open(revisione))["problemi"]:
        f = per_id.get(p["frase_id"])
        if not f or p["gravita"] < 2: continue
        a, v = p["azione"], p["valore"]
        if a == "errore_testo":
            errori.append(f"- pagina {m['pagina']}, frase {f['id']}: «{f['testo_originale']}» → «{v}» ({p['problema']})\n"); continue
        if a == "rigenera":
            if f["id"] in rigenerate: continue
            rigenerate.add(f["id"]); campo, nuovo = "seme", f["seme"] + 1
        elif a == "riscrivi": campo, nuovo = "testo_letto", v
        elif a == "inglese": campo, nuovo = "lingua", "English"
        elif a == "pausa":
            try: campo, nuovo = "pausa_dopo", min(1.5, max(0.2, float(v.replace(",", "."))))
            except ValueError: print(f"frase {f['id']}: pausa non numerica {v!r}, ignorata"); continue
        else: continue
        if f[campo] == nuovo: continue
        mod.append({"frase_id": f["id"], "campo": campo, "prima": f[campo], "dopo": nuovo, "azione": a, "parola": p["parola"], "problema": p["problema"]})
        f[campo] = nuovo
    if errori: open(os.path.join(lavoro, "errori-testo.md"), "a").writelines(errori)
    json.dump(m, open(mf, "w"), ensure_ascii=False, indent=1)
    json.dump(mod, open(os.path.join(lavoro, f"modifiche-{n}.json"), "w"), ensure_ascii=False, indent=1)
    solo = sorted({x["frase_id"] for x in mod if x["campo"] != "pausa_dopo"})
    print(f"giro {n}: {len(mod)} modifiche, {len(errori)} errori di testo in errori-testo.md")
    print(f"python sintetizza.py --solo {','.join(map(str, solo))} {lavoro}" if solo else "nessuna frase da risintetizzare: basta monta.py")
    return solo

if __name__ == "__main__":
    if len(sys.argv) != 3: sys.exit(__doc__)
    correggi(*sys.argv[1:])
