"""Pronuncia IPA delle parole inglesi da Wiktionary (api.dictionaryapi.dev, gratis, senza chiave): britannica prima.
Uso: python fonetica.py parola [parola...]   (Google Traduttore non si può interrogare in automatico: captcha.)"""
import json, sys, urllib.parse, urllib.request

def ipa(parola):
    url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + urllib.parse.quote(parola.lower())
    req = urllib.request.Request(url, headers={"User-Agent": "voci-sintetizzatore"})  # senza User-Agent risponde 403
    try: dati = json.load(urllib.request.urlopen(req, timeout=15))
    except Exception: return []
    out = []
    for e in dati:
        for p in e.get("phonetics", []):
            if p.get("text") and p["text"] not in [t for t, _ in out]:
                a = p.get("audio", ""); out.append((p["text"], "UK" if "-uk" in a else "US" if "-us" in a else ""))
    return sorted(out, key=lambda x: x[1] != "UK")

if __name__ == "__main__":
    for w in sys.argv[1:]:
        r = ipa(w); print(f"{w}: " + ("; ".join(f"{t} {k}".strip() for t, k in r) if r else "non trovata"))
