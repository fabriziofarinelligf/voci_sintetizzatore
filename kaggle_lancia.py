"""Pagine sintetizzate su Kaggle (2 GPU Tesla T4), tutto dal portatile con la CLI kaggle.
Uso: python kaggle_lancia.py invia [--prova] [--voce a2] [--tempo 1.1] [--pause 0.3,0.65,0.75] [--normalizza] p42.json p43.json ...
     python kaggle_lancia.py attendi [--ogni 60] [--max-ore 9]
     python kaggle_lancia.py scarica DEST
invia: nuova versione del kernel fabriziofarinelli/voci-pagine; lo script generato clona il repo al commit locale (va pushato prima),
divide le pagine in due code, una per GPU, e lascia /kaggle/working/<pagina>-lavoro/ (frasi + manifest, poi monta.py in locale).
--prova: scrive la cartella e stampa script e metadata senza inviare. Lo script generato gira anche in locale:
VOCI_FAKE_TTS=1 VOCI_KAGGLE_BASE=DIR VOCI_REPO=. python DIR_PROVA/voci_pagine.py
Sessione Kaggle max 12 h: invia rifiuta un lotto stimato oltre 10 h (2,3 s di calcolo per secondo di audio, 0,09 s di audio per carattere)."""
import argparse, glob, json, os, subprocess, sys, tempfile, time

QUI = os.path.dirname(os.path.abspath(__file__))
KAGGLE, KERNEL = os.path.expanduser("~/.local/bin/kaggle"), os.environ.get("VOCI_KERNEL", "fabriziofarinelli/voci-pagine")  # più sessioni: VOCI_KERNEL=fabriziofarinelli/voci-pagine-2
REPO_URL = "https://github.com/fabriziofarinelligf/voci_sintetizzatore.git"
S_CALCOLO, S_AUDIO, MAX_ORE, CARICA = 2.3, 0.09, 10, 120  # CARICA: s per pagina a caricare il modello (stima)

SCRIPT = r'''import json, os, subprocess, sys, tempfile, threading
BASE = os.environ.get("VOCI_KAGGLE_BASE", "/kaggle/working")
PAGINE, CODE, OPZIONI, COMMIT = {pagine}, {code}, {opzioni}, {commit!r}
REPO = os.environ.get("VOCI_REPO")
if not REPO:
    REPO = "/tmp/voci_sintetizzatore"
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "qwen-tts", "num2words"], check=True)
    subprocess.run(["git", "clone", "-q", {url!r}, REPO], check=True)
    subprocess.run(["git", "-C", REPO, "checkout", "-q", COMMIT], check=True)
SRC = tempfile.mkdtemp()
for nome, blocchi in PAGINE.items():
    json.dump(blocchi, open(os.path.join(SRC, nome + ".json"), "w"), ensure_ascii=False)
falliti = []
def coda(gpu, nomi):
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(gpu))
    for nome in nomi:
        print(f"GPU {{gpu}}: inizio {{nome}}", flush=True)
        r = subprocess.run([sys.executable, os.path.join(REPO, "sintetizza.py"), *OPZIONI, "--device", "cuda:0",
                            os.path.join(SRC, nome + ".json"), os.path.join(BASE, nome + "-lavoro")], env=env)
        print(f"GPU {{gpu}}: fine {{nome}} (codice {{r.returncode}})", flush=True)
        if r.returncode: falliti.append(nome)
tt = [threading.Thread(target=coda, args=(g, nomi)) for g, nomi in enumerate(CODE)]
for t in tt: t.start()
for t in tt: t.join()
print("pagine fallite:", falliti or "nessuna", flush=True)
sys.exit(1 if falliti else 0)
'''

def stima(blocchi):
    return CARICA + S_CALCOLO * S_AUDIO * sum(len(b) for b in blocchi)

def invia(a):
    pagine = {os.path.splitext(os.path.basename(p))[0]: json.load(open(p)) for p in a.pagine}
    if len(pagine) != len(a.pagine): sys.exit("due pagine con lo stesso nome di file")
    code, ore = [[], []], [0.0, 0.0]
    for nome in sorted(pagine, key=lambda n: -stima(pagine[n])):  # la pagina più lunga nella coda più scarica
        g = ore.index(min(ore)); code[g].append(nome); ore[g] += stima(pagine[nome]) / 3600
    print(f"stima: GPU 0 {ore[0]:.1f} h ({', '.join(code[0])}), GPU 1 {ore[1]:.1f} h ({', '.join(code[1])})")
    if max(ore) > MAX_ORE: sys.exit(f"lotto troppo lungo per una sessione Kaggle (limite {MAX_ORE} h): togli pagine")
    commit = subprocess.run(["git", "-C", QUI, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    if subprocess.run(["git", "-C", QUI, "merge-base", "--is-ancestor", "HEAD", "origin/main"]).returncode:
        print(f"ATTENZIONE: il commit {commit[:7]} non risulta su origin/main: Kaggle non potrà clonarlo, fai git push prima")
    opz = ["--voce", a.voce, "--tempo", a.tempo, "--pause", a.pause] + ["--normalizza"] * a.normalizza
    d = tempfile.mkdtemp(prefix="kaggle-voci-")
    open(os.path.join(d, "voci_pagine.py"), "w").write(SCRIPT.format(pagine=json.dumps(pagine, ensure_ascii=False), code=code, opzioni=opz, commit=commit, url=REPO_URL))
    meta = {"id": KERNEL, "title": KERNEL.split("/")[1], "code_file": "voci_pagine.py", "language": "python", "kernel_type": "script",
            "is_private": True, "enable_gpu": True, "enable_internet": True, "dataset_sources": [], "competition_sources": [], "kernel_sources": []}
    json.dump(meta, open(os.path.join(d, "kernel-metadata.json"), "w"), indent=1)
    if a.prova:
        print(f"cartella: {d}\n--- kernel-metadata.json\n{json.dumps(meta, indent=1)}\n--- voci_pagine.py\n" + open(os.path.join(d, "voci_pagine.py")).read())
        return
    subprocess.run([KAGGLE, "kernels", "push", "-p", d], check=True)
    print(f"inviato; poi: python kaggle_lancia.py attendi")

def attendi(a):
    fine = time.time() + a.max_ore * 3600
    while time.time() < fine:
        r = subprocess.run([KAGGLE, "kernels", "status", KERNEL], capture_output=True, text=True); s = (r.stdout + r.stderr).strip()
        print(time.strftime("%H:%M"), s, flush=True)
        if "COMPLETE" in s.upper(): return
        if r.returncode or any(x in s.upper() for x in ("ERROR", "CANCEL")): sys.exit("kernel fallito: guarda il .log con scarica")
        time.sleep(a.ogni)
    sys.exit(f"ancora non finito dopo {a.max_ore} h")

def scarica(a):
    subprocess.run([KAGGLE, "kernels", "output", KERNEL, "-p", a.dest], check=True)
    controlla(a.dest)

def controlla(dest):
    lavori = sorted(glob.glob(os.path.join(dest, "*-lavoro", "manifest.json")))
    for mf in lavori:
        l = os.path.dirname(mf); n = len(json.load(open(mf))["frasi"]); w = len(glob.glob(os.path.join(l, "frasi", "*.wav")))
        print(f"{l}: {w}/{n} frasi" + ("" if w == n else "  INCOMPLETA: rifai le mancanti con sintetizza.py --solo"))
    if not lavori: print(f"nessuna cartella *-lavoro in {dest}")
    return lavori

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    i = sp.add_parser("invia"); i.add_argument("--prova", action="store_true"); i.add_argument("--voce", default="a2"); i.add_argument("--tempo", default="1.0")
    i.add_argument("--pause", default="0.3,0.65,0.75"); i.add_argument("--normalizza", action="store_true"); i.add_argument("pagine", nargs="+")
    w = sp.add_parser("attendi"); w.add_argument("--ogni", type=int, default=60); w.add_argument("--max-ore", type=float, default=9)
    s = sp.add_parser("scarica"); s.add_argument("dest")
    a = ap.parse_args(); {"invia": invia, "attendi": attendi, "scarica": scarica}[a.cmd](a)
