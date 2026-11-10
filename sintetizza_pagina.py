"""Testo a blocchi letto con una voce del repo, frase per frase, con pausa secondo la punteggiatura (sintetizza.py + monta.py in un colpo).
Uso: python sintetizza_pagina.py [--voce a1] [--tempo 1.1[,1.2]] [--pause 0.3,0.65,0.75] [--normalizza] [--lavoro DIR] [--device cuda:0 | --threads 10] BLOCCHI.json USCITA
BLOCCHI.json = lista di stringhe. Per ogni tempo scrive USCITA[-tNNN].wav e .json {voce, tempo, durata, blocchi: [[inizio, fine], ...]}.
--pause = dopo due punti, dopo fine frase (. ; ! ?), dopo fine blocco (titoli, didascalie). Default: Gemini per virgola e frase, 0,75 a fine blocco scelto da Fabrizio.
--normalizza = numeri in lettere e sigle lettera per lettera (normalizza.py); poi si applica regole.json.
--tempo > 1 accelera senza cambiare il timbro (ffmpeg atempo); i tempi dei blocchi sono già divisi per il tempo.
--lavoro = cartella con le frasi e il manifest (default USCITA-frasi), da usare per il giro con revisione Gemini."""
import argparse, json, os, time
from sintetizza import frasi_pagina, sintetizza
from monta import monta
ap = argparse.ArgumentParser(); ap.add_argument("--voce", default="a1"); ap.add_argument("--tempo", default="1.0"); ap.add_argument("--pause", default="0.3,0.65,0.75"); ap.add_argument("--normalizza", action="store_true")
ap.add_argument("--lavoro"); ap.add_argument("--device", default="cpu"); ap.add_argument("--threads", type=int, default=0); ap.add_argument("blocchi"); ap.add_argument("uscita")
a = ap.parse_args(); t0 = time.time(); testi = json.load(open(a.blocchi)); lavoro = a.lavoro or a.uscita + "-frasi"
sintetizza(lavoro, {"voce": a.voce, "tempo": a.tempo, "pause": a.pause, "normalizza": a.normalizza,
                    "pagina": os.path.splitext(os.path.basename(a.blocchi))[0], "n_blocchi": len(testi), "frasi": frasi_pagina(testi, a.pause, a.normalizza)},
           device=a.device, threads=a.threads)
monta(lavoro, a.uscita)
print(f"FINE: calcolo {time.time()-t0:.0f}s", flush=True)
