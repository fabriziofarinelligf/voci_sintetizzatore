"""Fase 3 del giro: Gemini ascolta la pagina montata e segnala solo i problemi sentiti, frase per frase.
Uso: python revisione.py [--risposta-finta R.json] LAVORO             -> LAVORO/revisione-N.json (N = giro)
     python revisione.py --verifica [--risposta-finta R.json] LAVORO  -> ascolta solo le frasi cambiate dall'ultima correzione, LAVORO/verifica-N.json
Chiave in GEMINI_API_KEY (mai stampata). Modelli in ordine: gemini-3.8-flash, gemini-3.5-flash, gemini-2.5-flash; 503 -> riprova dopo 30 e 90 s, poi modello
successivo; 429 -> si ferma. Dopo --verifica le correzioni riscrivi/inglese risolte diventano candidate in regole-proposte.json (regole.py lista)."""
import argparse, difflib, glob, json, os, subprocess, sys, tempfile, time, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import regole as R

MODELLI, ATTESE = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-2.5-flash"], [0, 30, 90]
AZIONI = ["rigenera", "riscrivi", "inglese", "pausa", "errore_testo"]
N_, S_, I_, B_ = ({"type": t} for t in ("NUMBER", "STRING", "INTEGER", "BOOLEAN"))
SCHEMA = {"type": "OBJECT", "required": ["voti", "problemi"], "properties": {
    "voti": {"type": "OBJECT", "properties": {k: N_ for k in ("naturalezza", "ritmo", "intonazione", "pause", "pronuncia_it", "pronuncia_en", "ascolto_lungo")},
             "required": ["naturalezza", "ritmo", "intonazione", "pause", "pronuncia_it", "pronuncia_en", "ascolto_lungo"]},
    "problemi": {"type": "ARRAY", "items": {"type": "OBJECT", "required": ["frase_id", "parola", "problema", "gravita", "azione", "valore"], "properties": {
        "frase_id": I_, "parola": S_, "problema": S_, "gravita": {"type": "INTEGER", "minimum": 1, "maximum": 3},
        "azione": {"type": "STRING", "format": "enum", "enum": AZIONI}, "valore": S_}}}}}
SCHEMA_VERIFICA = {"type": "OBJECT", "required": ["esiti"], "properties": {"esiti": {"type": "ARRAY", "items": {
    "type": "OBJECT", "required": ["frase_id", "risolto", "nota"], "properties": {"frase_id": I_, "risolto": B_, "nota": S_}}}}}

PROMPT = """Sei un direttore del doppiaggio di audiolibri italiani. Ascolta l'audio allegato: è la lettura con voce sintetica di una pagina di un manuale di studio.
Qui sotto c'è l'elenco numerato delle frasi, con il secondo in cui inizia ognuna e il testo esatto che la voce ha letto.

{frasi}

Regole:
- Segnala SOLO problemi che senti davvero nell'audio. Se una frase va bene, non nominarla.
- Ogni problema indica frase_id (il numero della frase) e la parola esatta in cui si sente.
- Vietati i consigli generici (per esempio "migliorare l'intonazione in generale"): ogni voce è un difetto preciso in una frase precisa.
- gravita: 1 = appena percettibile, 2 = disturba l'ascolto, 3 = errore evidente.
- azione, una sola per problema:
  rigenera = inceppo, artefatto o prosodia strana: rileggere lo stesso testo (valore vuoto);
  riscrivi = valore è il testo nuovo da far leggere per l'intera frase (per esempio un punto in più, una parola scritta come si pronuncia);
  inglese = la frase è una citazione in inglese: va letta con la lingua inglese (valore vuoto);
  pausa = valore è la nuova pausa dopo la frase, in secondi (per esempio "0.9");
  errore_testo = è sbagliato il testo del manuale stesso (refuso, parola mancante): valore è il testo corretto dell'intera frase, come va scritto nel manuale; si annota e la voce lo rilegge.
- voti da 1 a 10 sull'intera pagina."""

PROMPT_VERIFICA = """Sei un direttore del doppiaggio di audiolibri italiani. Nell'audio allegato ci sono solo alcune frasi di una pagina, rilette dopo una correzione; ognuna è preceduta da 0,6 secondi di silenzio.
Per ogni frase c'è il numero, il secondo di inizio nella clip, il testo letto e il problema che era stato segnalato:

{frasi}

Per ogni frase rispondi con frase_id, risolto (true se il problema segnalato non si sente più e non ne è comparso un altro) e una nota breve e precisa (la parola che ancora non va, se c'è)."""

def mp3(wav, tempo, uscita):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-af", f"atempo={tempo}", "-ac", "1", "-b:a", "64k", uscita], check=True)

def chiedi(audio_mp3, prompt, schema):
    from google import genai
    from google.genai import types, errors
    if not os.environ.get("GEMINI_API_KEY"): sys.exit("manca GEMINI_API_KEY nell'ambiente")
    # google-genai 3.x usa l'API v1, che rifiuta response_schema ("JSON mode is not enabled for api version v1"): serve v1beta
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=types.HttpOptions(api_version="v1beta"))
    parti = [types.Part.from_bytes(data=open(audio_mp3, "rb").read(), mime_type="audio/mp3"), prompt]
    cfg = types.GenerateContentConfig(response_mime_type="application/json", response_schema=schema)
    for modello in MODELLI:
        for attesa in ATTESE:
            time.sleep(attesa)
            try:
                r = client.models.generate_content(model=modello, contents=parti, config=cfg)
                return modello, json.loads(r.text)
            except errors.APIError as e:
                if e.code == 429: sys.exit(f"{modello}: quota esaurita (429), riprova più tardi")
                print(f"{modello}: errore {e.code} {e.status}: {e.message}", flush=True)
                if e.code != 503: break  # modello inesistente o altro: si passa al successivo
    sys.exit("nessun modello Gemini ha risposto")

def risposta(finta, mp3_, prompt, schema):
    return ("finta", json.load(open(finta))) if finta else chiedi(mp3_, prompt, schema)

def giro(lavoro, prefisso):
    return len(glob.glob(os.path.join(lavoro, f"{prefisso}-*.json")))

def revisione(lavoro, finta=None):
    m = json.load(open(os.path.join(lavoro, "manifest.json"))); ids = {f["id"] for f in m["frasi"]}
    elenco = "\n".join(f"{f['id']}. [{f['inizio']:.1f} s] {f['testo_letto']}" for f in m["frasi"])
    with tempfile.TemporaryDirectory() as d:
        # il wav montato ha già il tempo applicato: l'mp3 non lo ricambia
        mp3(os.path.join(lavoro, m["montaggio"]["wav"]), 1.0, os.path.join(d, "p.mp3"))
        modello, r = risposta(finta, os.path.join(d, "p.mp3"), PROMPT.format(frasi=elenco), SCHEMA)
    validi = [p for p in r["problemi"] if p.get("frase_id") in ids and p.get("azione") in AZIONI]
    n = giro(lavoro, "revisione") + 1; out = os.path.join(lavoro, f"revisione-{n}.json")
    json.dump({"modello": modello, "voti": r["voti"], "problemi": validi, "scartati": len(r["problemi"]) - len(validi)},
              open(out, "w"), ensure_ascii=False, indent=1)
    print(f"{out}: {len(validi)} problemi ({len(r['problemi']) - len(validi)} scartati per frase_id inesistente)")
    return out

def verifica(lavoro, finta=None):
    n = giro(lavoro, "modifiche")
    if not n: sys.exit("nessuna correzione da verificare (manca modifiche-N.json)")
    m = json.load(open(os.path.join(lavoro, "manifest.json"))); per_id = {f["id"]: f for f in m["frasi"]}
    mod = json.load(open(os.path.join(lavoro, f"modifiche-{n}.json")))
    cambiate = sorted({x["frase_id"] for x in mod if x["campo"] in ("seme", "testo_letto", "lingua")})
    if not cambiate: sys.exit("l'ultima correzione non ha cambiato l'audio di nessuna frase")
    pezzi, righe, t, sr = [], [], 0.0, 24000
    for i in cambiate:
        w, sr = sf.read(os.path.join(lavoro, per_id[i]["wav"]), dtype="float32")
        pezzi += [np.zeros(int(0.6 * sr), dtype=np.float32), w]; t += 0.6
        problema = "; ".join(f"{x['parola']}: {x['problema']}" for x in mod if x["frase_id"] == i)
        righe.append(f"{i}. [{t / m['montaggio']['tempo']:.1f} s] {per_id[i]['testo_letto']} (problema: {problema})"); t += len(w) / sr
    with tempfile.TemporaryDirectory() as d:
        sf.write(os.path.join(d, "c.wav"), np.concatenate(pezzi), sr); mp3(os.path.join(d, "c.wav"), m["montaggio"]["tempo"], os.path.join(d, "c.mp3"))
        modello, r = risposta(finta, os.path.join(d, "c.mp3"), PROMPT_VERIFICA.format(frasi="\n".join(righe)), SCHEMA_VERIFICA)
    esiti = [e for e in r["esiti"] if e.get("frase_id") in cambiate]
    out = os.path.join(lavoro, f"verifica-{n}.json")
    json.dump({"modello": modello, "frasi": cambiate, "esiti": esiti}, open(out, "w"), ensure_ascii=False, indent=1)
    risolte = {e["frase_id"] for e in esiti if e["risolto"]}
    print(f"{out}: {len(risolte)}/{len(cambiate)} risolte")
    proponi(m, mod, risolte, f"{os.path.basename(os.path.normpath(lavoro))} verifica-{n}")
    return out

def proponi(m, mod, risolte, fonte):
    """Le correzioni riscrivi/inglese risolte diventano regole candidate; le approva una persona o l'agente con regole.py."""
    proposte, per_id, nuove = R.leggi("regole-proposte.json", []), {f["id"]: f for f in m["frasi"]}, 0
    for x in mod:
        if x["frase_id"] not in risolte or x["azione"] not in ("riscrivi", "inglese"): continue
        c = {"tipo": "inglese", "motivo": x["problema"], "pagina": m["pagina"], "esempio": per_id[x["frase_id"]]["testo_originale"], "fonte": fonte}
        if x["azione"] == "riscrivi":  # solo il tratto di parole che cambia, così la regola vale anche in altre frasi
            p, d = x["prima"].split(), x["dopo"].split()
            ops = [o for o in difflib.SequenceMatcher(a=p, b=d, autojunk=False).get_opcodes() if o[0] != "equal"]
            if not ops: continue
            i1, i2, j1, j2 = ops[0][1], ops[-1][2], ops[0][3], ops[-1][4]
            if i1 == i2:  # inserimento puro: aggancia la parola vicina
                if not p: continue
                if i1: i1, j1 = i1 - 1, j1 - 1
                else: i2, j2 = 1, j2 + 1
            c.update(tipo="sostituzione", da=" ".join(p[i1:i2]), a=" ".join(d[j1:j2]))
        if not any(q.get("da") == c.get("da") and q["tipo"] == c["tipo"] and q.get("a") == c.get("a") for q in proposte):
            proposte.append(c); nuove += 1
    R.scrivi("regole-proposte.json", proposte)
    print(f"{nuove} regole candidate nuove (python regole.py lista)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--verifica", action="store_true"); ap.add_argument("--risposta-finta"); ap.add_argument("lavoro")
    a = ap.parse_args()
    (verifica if a.verifica else revisione)(a.lavoro, a.risposta_finta)
