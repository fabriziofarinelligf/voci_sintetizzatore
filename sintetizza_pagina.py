"""Testo a blocchi letto con una voce del repo, frase per frase, con pausa secondo la punteggiatura.
Uso: python sintetizza_pagina.py [--voce a1] [--tempo 1.1[,1.2]] [--pause 0.3,0.65,0.75] [--normalizza] [--device cuda:0 | --threads 10] BLOCCHI.json USCITA
BLOCCHI.json = lista di stringhe. Per ogni tempo scrive USCITA[-tNNN].wav e .json {voce, tempo, durata, blocchi: [[inizio, fine], ...]}.
--pause = dopo due punti, dopo fine frase (. ; ! ?), dopo fine blocco (titoli, didascalie). Default: Gemini per virgola e frase, 0,75 a fine blocco scelto da Fabrizio.
--normalizza = numeri in lettere e sigle lettera per lettera (normalizza.py).
--tempo > 1 accelera senza cambiare il timbro (ffmpeg atempo); i tempi dei blocchi sono già divisi per il tempo."""
import argparse, json, os, re, subprocess, tempfile, time, numpy as np, soundfile as sf, torch
from qwen_tts import Qwen3TTSModel
ap = argparse.ArgumentParser(); ap.add_argument("--voce", default="a1"); ap.add_argument("--tempo", default="1.0"); ap.add_argument("--pause", default="0.3,0.65,0.75"); ap.add_argument("--normalizza", action="store_true")
ap.add_argument("--device", default="cpu"); ap.add_argument("--threads", type=int, default=0); ap.add_argument("blocchi"); ap.add_argument("uscita")
a = ap.parse_args()
QUI = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(QUI, "voci", a.voce)
import sys; sys.path.insert(0, QUI)
if a.device == "cpu": torch.set_num_threads(a.threads or max(1, (os.cpu_count() or 2) // 2))
testi = json.load(open(a.blocchi)); FRASE = re.compile(r"(?<=[.;:!?])\s+")
P_DUEPUNTI, P_FRASE, P_BLOCCO = (float(x) for x in a.pause.split(","))
TEMPI = [float(x) for x in a.tempo.split(",")]
if a.normalizza:
    from normalizza import normalizza
    testi = [normalizza(t) for t in testi]
m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map=a.device, dtype=torch.float32)
p = m.create_voice_clone_prompt(ref_audio=f"{V}/riferimento.wav", ref_text=open(f"{V}/riferimento.txt").read().strip())
pezzi, tempi, t, t0, sr = [], [], 0.0, time.time(), 24000
for b, testo in enumerate(testi):
    tempi.append(t); ff = [f for f in FRASE.split(testo) if f.strip()]
    for k, f in enumerate(ff):
        torch.manual_seed(42)
        w, sr = m.generate_voice_clone(text=f, language="Italian", voice_clone_prompt=p)
        w = np.trim_zeros(w[0], "fb"); pausa = np.zeros(int((P_BLOCCO if k == len(ff) - 1 else P_DUEPUNTI if f.rstrip().endswith(":") else P_FRASE) * sr), dtype=w.dtype)
        pezzi += [w, pausa]; t += (len(w) + len(pausa)) / sr
    print(f"blocco {b+1}/{len(testi)} — audio {t:.0f}s, calcolo {time.time()-t0:.0f}s", flush=True)
audio = np.concatenate(pezzi)
for tempo in TEMPI:
    uscita = a.uscita if len(TEMPI) == 1 else f"{a.uscita}-t{round(tempo * 100):03d}"
    if tempo == 1.0:
        sf.write(uscita + ".wav", audio, sr)
    else:
        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            sf.write(tmp.name, audio, sr)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp.name, "-af", f"atempo={tempo}", uscita + ".wav"], check=True)
    fine = (t - P_BLOCCO) / tempo
    json.dump({"voce": a.voce, "tempo": tempo, "pause": a.pause, "normalizza": a.normalizza, "durata": round(fine, 2),
               "blocchi": [[round(x / tempo, 2), round(y / tempo, 2)] for x, y in zip(tempi, tempi[1:] + [t - P_BLOCCO])]},
              open(uscita + ".json", "w"))
    print(f"{uscita}: {fine:.0f}s audio", flush=True)
print(f"FINE: calcolo {time.time()-t0:.0f}s", flush=True)
