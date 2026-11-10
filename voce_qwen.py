"""Voci Qwen3-TTS al posto di edge-tts: per ogni sN.txt scrive sN.mp3 e sN.srt accanto.
Uso:  python voce_qwen.py [--voce a1] [--tempo 0.85] [--device cuda:0] [--threads N] s1.txt [s2.txt ...]
- La voce resta la stessa fra le scene perché ogni frase usa la clip voci/<NOME>/riferimento.wav (+ .txt con il suo testo) come riferimento (modello Base).
- Voci in voci/<nome>/ (descrizione.txt dice a cosa è adatta). Su CPU circa 6-10x la durata del parlato, su GPU T4 circa 2x.
- I sottotitoli: una riga per frase, tempi dalla durata reale di ogni frase sintetizzata.
- --tempo < 1 rallenta senza cambiare il timbro (ffmpeg atempo): 0.85 equivale al --rate=-15% usato con Giuseppe."""
import argparse, os, re, subprocess, tempfile, numpy as np, soundfile as sf, torch
from qwen_tts import Qwen3TTSModel

QUI = os.path.dirname(os.path.abspath(__file__))
PAUSA = 0.35  # secondi di silenzio fra le frasi

def frasi(testo):
    return [f.strip() for f in re.split(r"(?<=[.!?…])\s+", " ".join(testo.split())) if f.strip()]

def ts(s):
    ms = int(round(s * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); sec, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"

ap = argparse.ArgumentParser(); ap.add_argument("--voce", default="a1"); ap.add_argument("--device", default="cpu"); ap.add_argument("--dtype", default="float32"); ap.add_argument("--threads", type=int, default=0); ap.add_argument("--tempo", type=float, default=1.0); ap.add_argument("scene", nargs="+")
a = ap.parse_args()
REF_WAV = os.path.join(QUI, "voci", a.voce, "riferimento.wav")
REF_TXT = open(os.path.join(QUI, "voci", a.voce, "riferimento.txt")).read().strip()
torch.set_num_threads(a.threads or max(1, (os.cpu_count() or 2) // 2))  # un thread per core fisico è più veloce
m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map=a.device, dtype=getattr(torch, a.dtype))
prompt = m.create_voice_clone_prompt(ref_audio=REF_WAV, ref_text=REF_TXT)
for path in a.scene:
    base = os.path.splitext(path)[0]; pezzi, srt, t = [], [], 0.0
    for i, f in enumerate(frasi(open(path).read()), 1):
        torch.manual_seed(42)
        wavs, sr = m.generate_voice_clone(text=f, language="Italian", voice_clone_prompt=prompt)
        w = wavs[0]; d = len(w) / sr / a.tempo
        srt.append(f"{i}\n{ts(t)} --> {ts(t + d)}\n{f}\n"); t += d + PAUSA / a.tempo
        pezzi += [w, np.zeros(int(PAUSA * sr), dtype=w.dtype)]
        print(f"{path} frase {i}: {d:.1f}s", flush=True)
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        sf.write(tmp.name, np.concatenate(pezzi[:-1]), sr)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp.name, "-af", f"atempo={a.tempo}", "-b:a", "128k", base + ".mp3"], check=True)
    open(base + ".srt", "w").write("\n".join(srt))
    print("scritti", base + ".mp3", base + ".srt", flush=True)
