"""Testo a blocchi letto con una voce del repo, frase per frase con pause fisse (0,35 s fra frasi, 0,5 s fra blocchi).
Uso: python sintetizza_pagina.py [--voce a1] [--tempo 1.2] [--device cuda:0 | --threads 10] BLOCCHI.json USCITA
BLOCCHI.json = lista di stringhe. Scrive USCITA.wav e USCITA.json {voce, tempo, durata, blocchi: [[inizio, fine], ...]}.
--tempo > 1 accelera senza cambiare il timbro (ffmpeg atempo); i tempi dei blocchi sono già divisi per il tempo."""
import argparse, json, os, re, subprocess, tempfile, time, numpy as np, soundfile as sf, torch
from qwen_tts import Qwen3TTSModel
ap = argparse.ArgumentParser(); ap.add_argument("--voce", default="a1"); ap.add_argument("--tempo", type=float, default=1.0)
ap.add_argument("--device", default="cpu"); ap.add_argument("--threads", type=int, default=0); ap.add_argument("blocchi"); ap.add_argument("uscita")
a = ap.parse_args()
QUI = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(QUI, "voci", a.voce)
if a.device == "cpu": torch.set_num_threads(a.threads or max(1, (os.cpu_count() or 2) // 2))
testi = json.load(open(a.blocchi)); FRASE = re.compile(r"(?<=[.;:!?])\s+"); P_FRASE, P_BLOCCO = 0.35, 0.5
m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map=a.device, dtype=torch.float32)
p = m.create_voice_clone_prompt(ref_audio=f"{V}/riferimento.wav", ref_text=open(f"{V}/riferimento.txt").read().strip())
pezzi, tempi, t, t0, sr = [], [], 0.0, time.time(), 24000
for b, testo in enumerate(testi):
    tempi.append(t); ff = [f for f in FRASE.split(testo) if f.strip()]
    for k, f in enumerate(ff):
        torch.manual_seed(42)
        w, sr = m.generate_voice_clone(text=f, language="Italian", voice_clone_prompt=p)
        w = np.trim_zeros(w[0], "fb"); pausa = np.zeros(int((P_BLOCCO if k == len(ff) - 1 else P_FRASE) * sr), dtype=w.dtype)
        pezzi += [w, pausa]; t += (len(w) + len(pausa)) / sr
    print(f"blocco {b+1}/{len(testi)} — audio {t / a.tempo:.0f}s, calcolo {time.time()-t0:.0f}s", flush=True)
audio = np.concatenate(pezzi)
if a.tempo == 1.0:
    sf.write(a.uscita + ".wav", audio, sr)
else:
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        sf.write(tmp.name, audio, sr)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp.name, "-af", f"atempo={a.tempo}", a.uscita + ".wav"], check=True)
fine = (t - P_BLOCCO) / a.tempo
json.dump({"voce": a.voce, "tempo": a.tempo, "durata": round(fine, 2),
           "blocchi": [[round(x / a.tempo, 2), round(y / a.tempo, 2)] for x, y in zip(tempi, tempi[1:] + [t - P_BLOCCO])]},
          open(a.uscita + ".json", "w"))
print(f"FINE: {fine:.0f}s audio in {time.time()-t0:.0f}s ({(time.time()-t0)/fine:.2f}x)", flush=True)
