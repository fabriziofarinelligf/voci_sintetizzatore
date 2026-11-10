"""Crea una voce nuova con Qwen3-TTS VoiceDesign e la salva in voci/<nome>/ (riferimento.wav, riferimento.txt, descrizione.txt).
Uso: python crea_voce.py NOME "DESCRIZIONE IN INGLESE" [--testo "frase di riferimento"] [--seme 42] [--device cuda:0]
La clip fissa il timbro: poi voce_qwen.py e sintetizza_pagina.py la usano con il modello Base."""
import argparse, os, soundfile as sf, torch
from qwen_tts import Qwen3TTSModel
ap = argparse.ArgumentParser(); ap.add_argument("nome"); ap.add_argument("descrizione")
ap.add_argument("--testo", default="In questo capitolo vediamo come si pianifica un progetto, passo dopo passo, con esempi pratici e qualche domanda d'esame.")
ap.add_argument("--seme", type=int, default=42); ap.add_argument("--device", default="cpu"); ap.add_argument("--uso", default="")
a = ap.parse_args()
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voci", a.nome); os.makedirs(d, exist_ok=True)
m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", device_map=a.device, dtype=torch.float32)
torch.manual_seed(a.seme)
w, sr = m.generate_voice_design(text=a.testo, instruct=a.descrizione, language="Italian")
sf.write(f"{d}/riferimento.wav", w[0], sr)
open(f"{d}/riferimento.txt", "w").write(a.testo + "\n")
open(f"{d}/descrizione.txt", "w").write(f'Creata con Qwen3-TTS VoiceDesign, seme {a.seme}. Descrizione: "{a.descrizione}"\n' + (f"Adatta a: {a.uso}\n" if a.uso else ""))
print(f"voce {a.nome}: {len(w[0])/sr:.1f} s di riferimento in {d}")
