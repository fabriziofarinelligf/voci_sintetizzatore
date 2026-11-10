"""Giro completo con TTS e Gemini finti: python tests/test_giro.py (o pytest)."""
import hashlib, json, os, subprocess, sys, tempfile
import soundfile as sf

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCCHI = ["Il PMP ha 35 domande: leggile tutte.", "Il project manager pianifica. Poi controlla il lavoro!", '"Plan the work, work the plan."']

def run(*args, ok=True):
    r = subprocess.run([sys.executable, *args], cwd=REPO, capture_output=True, text=True, env=ENV)
    assert (r.returncode == 0) == ok, f"{args}: {r.returncode}\n{r.stdout}\n{r.stderr}"
    return r.stdout + r.stderr

def js(p, dati=None):
    if dati is None: return json.load(open(p))
    json.dump(dati, open(p, "w"))

def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

def test_giro():
    global ENV
    d = tempfile.mkdtemp(); L = os.path.join(d, "pag"); ENV = dict(os.environ, VOCI_FAKE_TTS="1", VOCI_REGOLE_DIR=d)
    js(os.path.join(d, "p40.json"), BLOCCHI)

    # sintetizza: ids, testo letto, pause
    run("sintetizza.py", "--normalizza", "--tempo", "1.1", os.path.join(d, "p40.json"), L)
    m = js(f"{L}/manifest.json"); ff = m["frasi"]
    assert [f["id"] for f in ff] == [1, 2, 3, 4, 5] and [f["blocco"] for f in ff] == [0, 0, 1, 1, 2]
    assert ff[0]["testo_letto"] == "Il pi emme pi ha trentacinque domande:" and ff[0]["testo_originale"] == "Il PMP ha 35 domande:"
    assert [f["pausa_dopo"] for f in ff] == [0.3, 0.75, 0.65, 0.75, 0.75] and m["pagina"] == "p40"
    assert all(os.path.exists(f"{L}/frasi/{i:03d}.wav") for i in range(1, 6))

    # monta: tempi dei blocchi coerenti con la durata, frasi nell'audio finale
    run("monta.py", L)
    app, m = js(f"{L}/pagina.json"), js(f"{L}/manifest.json")
    assert set(app) == {"voce", "tempo", "pause", "normalizza", "durata", "blocchi"} and app["tempo"] == 1.1
    b = app["blocchi"]; assert len(b) == 3 and b[0][0] == 0 and all(b[i][1] == b[i + 1][0] for i in range(2)) and b[-1][1] == app["durata"]
    durata_wav = sf.info(f"{L}/pagina.wav").duration
    assert abs(durata_wav - (app["durata"] + 0.75 / 1.1)) < 0.05, (durata_wav, app["durata"])
    assert abs(m["frasi"][-1]["fine"] - app["durata"]) < 0.02 and m["frasi"][2]["inizio"] == b[1][0] and m["montaggio"]["tempo"] == 1.1

    # revisione finta: un problema per azione, uno lieve, uno con frase inesistente
    P = lambda i, az, v="", g=2: {"frase_id": i, "parola": "x", "problema": f"p{i}{az}", "gravita": g, "azione": az, "valore": v}
    voti = {k: 7 for k in ("naturalezza", "ritmo", "intonazione", "pause", "pronuncia_it", "pronuncia_en", "ascolto_lungo")}
    js(f"{d}/r1.json", {"voti": voti, "problemi": [P(1, "rigenera"), P(3, "riscrivi", "Il progect manager pianifica.", 3), P(5, "inglese"),
        P(4, "pausa", "3"), P(2, "errore_testo", "Leggile tutte e 3."), P(4, "rigenera", g=1), P(99, "rigenera")]})
    run("revisione.py", "--risposta-finta", f"{d}/r1.json", L)
    r1 = js(f"{L}/revisione-1.json"); assert len(r1["problemi"]) == 6 and r1["scartati"] == 1

    # correggi: ogni azione, gravità 1 ignorata, comando --solo
    out = run("correggi.py", L, f"{L}/revisione-1.json")
    assert f"--solo 1,2,3,5 {L}" in out, out
    ff = js(f"{L}/manifest.json")["frasi"]
    assert ff[0]["seme"] == 43 and ff[2]["testo_letto"] == "Il progect manager pianifica." and ff[4]["lingua"] == "English"
    assert ff[3]["pausa_dopo"] == 1.5 and ff[3]["seme"] == 42 and ff[1]["testo_letto"] == "Leggile tutte e tre."
    assert "frase 2: «leggile tutte.» → «Leggile tutte e 3.»" in open(f"{L}/errori-testo.md").read()
    mod = js(f"{L}/modifiche-1.json"); assert len(mod) == 5
    assert {"frase_id": 2, "campo": "testo_letto", "prima": "leggile tutte.", "dopo": "Leggile tutte e tre.", "azione": "errore_testo",
            "parola": "x", "problema": "p2errore_testo"} in mod

    # --solo riscrive solo le frasi indicate
    prima = {i: md5(f"{L}/frasi/{i:03d}.wav") for i in range(1, 6)}
    run("sintetizza.py", "--solo", "1,2,3,5", L)
    dopo = {i: md5(f"{L}/frasi/{i:03d}.wav") for i in range(1, 6)}
    assert [i for i in prima if prima[i] != dopo[i]] == [1, 2, 3, 5], (prima, dopo)
    run("monta.py", L)
    assert js(f"{L}/pagina.json")["blocchi"][-1][1] == js(f"{L}/pagina.json")["durata"]

    # verifica: 1 e 3 risolte, 5 no -> una sola candidata (sostituzione project -> progect)
    js(f"{d}/v1.json", {"esiti": [{"frase_id": 1, "risolto": True, "nota": ""}, {"frase_id": 3, "risolto": True, "nota": ""},
                                  {"frase_id": 5, "risolto": False, "nota": "Plan ancora italiano"}, {"frase_id": 4, "risolto": True, "nota": ""}]})
    run("revisione.py", "--verifica", "--risposta-finta", f"{d}/v1.json", L)
    v = js(f"{L}/verifica-1.json"); assert v["frasi"] == [1, 2, 3, 5] and len(v["esiti"]) == 3
    prop = js(f"{d}/regole-proposte.json")
    assert [(c["tipo"], c["da"], c["a"]) for c in prop] == [("sostituzione", "project", "progect")] and prop[0]["pagina"] == "p40"
    assert not os.path.exists(f"{d}/regole.json")  # niente approvazione automatica

    # candidata inglese a mano (come da una verifica risolta), poi lista / approva / scarta
    js(f"{d}/regole-proposte.json", prop + [{"tipo": "inglese", "motivo": "citazione", "pagina": "p40", "esempio": BLOCCHI[2], "fonte": "test"},
                                             {"tipo": "sostituzione", "da": "a", "a": "b", "motivo": "m", "pagina": "p40", "esempio": "e", "fonte": "test"}])
    assert "3 candidate" in run("regole.py", "lista")
    run("regole.py", "scarta", "3"); run("regole.py", "approva", "1"); run("regole.py", "approva", "1"); run("regole.py", "approva", "5", ok=False)
    r = js(f"{d}/regole.json")
    assert r["inglese_tra_virgolette"] and [(s["da"], s["a"]) for s in r["sostituzioni"]] == [("project", "progect")] and js(f"{d}/regole-proposte.json") == []

    # le regole approvate valgono nella sintesi successiva
    L2 = os.path.join(d, "pag2"); run("sintetizza.py", "--normalizza", os.path.join(d, "p40.json"), L2)
    ff = js(f"{L2}/manifest.json")["frasi"]
    assert ff[2]["testo_letto"] == "Il progect manager pianifica." and ff[4]["lingua"] == "English" and ff[4]["testo_letto"] == BLOCCHI[2]

    # secondo giro ammesso, terzo rifiutato
    js(f"{d}/r2.json", {"voti": voti, "problemi": [P(2, "pausa", "0.1")]})
    run("revisione.py", "--risposta-finta", f"{d}/r2.json", L)
    assert "basta monta.py" in run("correggi.py", L, f"{L}/revisione-2.json")
    assert js(f"{L}/manifest.json")["frasi"][1]["pausa_dopo"] == 0.2
    assert "il giro 3 non si fa" in run("correggi.py", L, f"{L}/revisione-2.json", ok=False)

    # report e vecchio comando unico
    rep = run("report.py", L)
    assert "giro 1: 6 problemi" in rep and "2/4 frasi risolte" in rep and "errori nel testo del manuale: 1" in rep, rep
    run("sintetizza_pagina.py", "--tempo", "1.0,1.2", os.path.join(d, "p40.json"), os.path.join(d, "vecchio"))
    assert all(os.path.exists(os.path.join(d, f"vecchio-t{t}.{e}")) for t in ("100", "120") for e in ("wav", "json"))
    print(rep)

if __name__ == "__main__":
    test_giro(); print("OK")
