"""Fase 1 del giro: una pagina (JSON lista di blocchi) letta frase per frase, un wav per frase in LAVORO/frasi/.
Uso: python sintetizza.py [--voce a1] [--tempo 1.1] [--pause 0.3,0.65,0.75] [--normalizza] [--pagina NOME] [--device cuda:0 | --threads 10] BLOCCHI.json LAVORO
     python sintetizza.py --solo 3,7,12 [--device ...] LAVORO   (rifà solo quelle frasi dai campi del manifest: testo_letto, lingua, seme)
Scrive LAVORO/manifest.json {voce, tempo, pause, normalizza, pagina, n_blocchi, frasi: [{id, blocco, testo_originale, testo_letto, lingua, seme, pausa_dopo, wav, durata}]}.
testo_letto = testo dopo normalizza.py e regole.json. VOCI_FAKE_TTS=1: niente modello, un tono lungo quanto il testo (per i test)."""
import argparse, json, os, re, sys, time, numpy as np, soundfile as sf
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import regole as R

FRASE = re.compile(r"(?<=[.;:!?])\s+")

def frasi_pagina(blocchi, pause, normalizza=False):
    """Divide i blocchi in frasi e prepara il testo da leggere (senza sintesi)."""
    p_duepunti, p_frase, p_blocco = (float(x) for x in pause.split(","))
    r = R.regole(); out = []
    if normalizza:
        from normalizza import normalizza as norm
    for b, testo in enumerate(blocchi):
        ff = [f for f in FRASE.split(testo) if f.strip()]
        for k, f in enumerate(ff):
            en = R.inglese(f, r)
            letto = R.applica(norm(f) if normalizza and not en else f, r)
            out.append({"id": len(out) + 1, "blocco": b, "testo_originale": f, "testo_letto": letto,
                        "lingua": "English" if en else "Italian", "seme": 42,
                        "pausa_dopo": p_blocco if k == len(ff) - 1 else p_duepunti if f.rstrip().endswith(":") else p_frase})
    return out

def motore(voce, device="cpu", threads=0):
    """Funzione testo, lingua, seme -> (campioni float32, sr)."""
    if os.environ.get("VOCI_FAKE_TTS") == "1":
        def finto(testo, lingua, seme):
            sr = 24000; t = np.arange(int(0.05 * len(testo) * sr)) / sr
            return (0.3 * np.sin(2 * np.pi * (200 + seme % 50 + (lingua == "English") * 100) * t)).astype(np.float32), sr
        return finto
    import torch
    from qwen_tts import Qwen3TTSModel
    if device == "cpu": torch.set_num_threads(threads or max(1, (os.cpu_count() or 2) // 2))
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map=device, dtype=torch.float32)
    V = os.path.join(QUI, "voci", voce)
    p = m.create_voice_clone_prompt(ref_audio=f"{V}/riferimento.wav", ref_text=open(f"{V}/riferimento.txt").read().strip())
    def vero(testo, lingua, seme):
        torch.manual_seed(seme)
        w, sr = m.generate_voice_clone(text=testo, language=lingua, voice_clone_prompt=p)
        return w[0], sr
    return vero

def sintetizza(lavoro, manifest=None, solo=None, device="cpu", threads=0):
    """Con manifest nuovo sintetizza tutte le frasi; con solo=[id] rifà quelle del manifest esistente."""
    mf = os.path.join(lavoro, "manifest.json")
    if manifest is None: manifest = json.load(open(mf))
    os.makedirs(os.path.join(lavoro, "frasi"), exist_ok=True)
    ids = {f["id"] for f in manifest["frasi"]}
    if solo and not set(solo) <= ids: sys.exit(f"frasi inesistenti: {sorted(set(solo) - ids)}")
    genera, t0 = motore(manifest["voce"], device, threads), time.time()
    for f in manifest["frasi"]:
        if solo and f["id"] not in solo: continue
        w, sr = genera(f["testo_letto"], f["lingua"], f["seme"])
        w = np.trim_zeros(w, "fb"); f["wav"] = f"frasi/{f['id']:03d}.wav"; f["durata"] = round(len(w) / sr, 3)
        sf.write(os.path.join(lavoro, f["wav"]), w, sr, subtype="FLOAT")
        print(f"frase {f['id']}/{len(manifest['frasi'])} — {f['durata']:.1f}s, calcolo {time.time()-t0:.0f}s", flush=True)
        json.dump(manifest, open(mf, "w"), ensure_ascii=False, indent=1)  # salva a ogni frase: un giro interrotto riparte con --solo
    return manifest

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--voce", default="a1"); ap.add_argument("--tempo", default="1.0"); ap.add_argument("--pause", default="0.3,0.65,0.75")
    ap.add_argument("--normalizza", action="store_true"); ap.add_argument("--pagina"); ap.add_argument("--solo")
    ap.add_argument("--device", default="cpu"); ap.add_argument("--threads", type=int, default=0); ap.add_argument("percorsi", nargs="+")
    a = ap.parse_args()
    if a.solo:
        if len(a.percorsi) != 1: ap.error("con --solo serve solo LAVORO")
        sintetizza(a.percorsi[0], solo=[int(x) for x in a.solo.split(",")], device=a.device, threads=a.threads)
    else:
        if len(a.percorsi) != 2: ap.error("servono BLOCCHI.json LAVORO")
        blocchi, lavoro = a.percorsi; testi = json.load(open(blocchi))
        sintetizza(lavoro, {"voce": a.voce, "tempo": a.tempo, "pause": a.pause, "normalizza": a.normalizza,
                            "pagina": a.pagina or os.path.splitext(os.path.basename(blocchi))[0], "n_blocchi": len(testi),
                            "frasi": frasi_pagina(testi, a.pause, a.normalizza)}, device=a.device, threads=a.threads)
