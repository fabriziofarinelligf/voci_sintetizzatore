"""Fase 2 del giro: unisce le frasi di LAVORO con le loro pause e scrive l'audio della pagina. Senza modello TTS (numpy, soundfile, ffmpeg).
Uso: python monta.py [--tempo 1.1[,1.2]] LAVORO [USCITA]   (USCITA default LAVORO/pagina; tempo default quello del manifest)
Per ogni tempo scrive USCITA[-tNNN].wav e .json {voce, tempo, pause, normalizza, durata, blocchi: [[inizio, fine], ...]} (formato letto dall'app).
Nel manifest salva inizio e fine di ogni frase nell'audio finale del primo tempo, e "montaggio": {tempo, wav} per revisione.py."""
import argparse, json, os, subprocess, tempfile, numpy as np, soundfile as sf

def monta(lavoro, uscita=None, tempo=None):
    mf = os.path.join(lavoro, "manifest.json"); m = json.load(open(mf))
    uscita = uscita or os.path.join(lavoro, "pagina"); TEMPI = [float(x) for x in (tempo or m["tempo"]).split(",")]
    pezzi, inizi_blocco, t, sr = [], [], 0.0, 24000
    for b in range(m["n_blocchi"]):
        inizi_blocco.append(t)
        for f in (f for f in m["frasi"] if f["blocco"] == b):
            w, sr = sf.read(os.path.join(lavoro, f["wav"]), dtype="float32")
            pausa = np.zeros(int(f["pausa_dopo"] * sr), dtype=np.float32)
            f["_inizio"], f["_fine"] = t, t + len(w) / sr
            pezzi += [w, pausa]; t += (len(w) + len(pausa)) / sr
    audio, fine_ultimo = np.concatenate(pezzi), t - m["frasi"][-1]["pausa_dopo"]
    scritti = []
    for tempo in TEMPI:
        u = uscita if len(TEMPI) == 1 else f"{uscita}-t{round(tempo * 100):03d}"
        if tempo == 1.0:
            sf.write(u + ".wav", audio, sr)
        else:
            with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
                sf.write(tmp.name, audio, sr)
                subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp.name, "-af", f"atempo={tempo}", u + ".wav"], check=True)
        json.dump({"voce": m["voce"], "tempo": tempo, "pause": m["pause"], "normalizza": m["normalizza"], "durata": round(fine_ultimo / tempo, 2),
                   "blocchi": [[round(x / tempo, 2), round(y / tempo, 2)] for x, y in zip(inizi_blocco, inizi_blocco[1:] + [fine_ultimo])]},
                  open(u + ".json", "w"))
        print(f"{u}: {fine_ultimo / tempo:.0f}s audio", flush=True); scritti.append(u + ".wav")
    for f in m["frasi"]:
        f["inizio"], f["fine"] = round(f.pop("_inizio") / TEMPI[0], 2), round(f.pop("_fine") / TEMPI[0], 2)
    m["montaggio"] = {"tempo": TEMPI[0], "wav": os.path.relpath(scritti[0], lavoro)}
    json.dump(m, open(mf, "w"), ensure_ascii=False, indent=1)
    return scritti

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--tempo"); ap.add_argument("lavoro"); ap.add_argument("uscita", nargs="?")
    a = ap.parse_args(); monta(a.lavoro, a.uscita, a.tempo)
