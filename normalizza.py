"""Testo pronto per la sintesi: numeri in lettere e sigle lettera per lettera (consigli di Gemini, 2026-11-10).
normalizza("Figura 2.8 del PMP, pagina 35") -> "Figura due punto otto del pi emme pi, pagina trentacinque"."""
import re
from num2words import num2words

LETTERE = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "a bi ci di e effe gi acca i ilunga cappa elle emme enne o pi cu erre esse ti u vu doppiavu ics ipsilon zeta".split()))
LETTERE["J"], LETTERE["W"] = "i lunga", "doppia vu"

def _numero(m):
    intero, dec = m.group(1), m.group(2)
    parole = num2words(int(intero), lang="it")
    if dec:  # 2.8 -> due punto otto; 2.10 -> due punto dieci (numerazione di figure e paragrafi)
        parole += " punto " + num2words(int(dec), lang="it")
    return parole

def _sigla(m):
    return " ".join(LETTERE[c] for c in m.group(0) if c in LETTERE)

def normalizza(testo):
    testo = re.sub(r"\b([A-Z])&([A-Z])\b", lambda m: f"{LETTERE[m.group(1)]} e {LETTERE[m.group(2)]}", testo)  # M&C
    testo = re.sub(r"\b([A-Z])(\d+)(?:\.(\d+))?\b", lambda m: LETTERE[m.group(1)] + " " + _numero(re.match(r"(\d+)(?:\.(\d+))?", m.group(0)[1:])), testo)  # X3.3, T6
    testo = re.sub(r"\b(\d+)(?:[.,](\d+))?\b", _numero, testo)
    testo = re.sub(r"\b[A-Z]{2,5}\b", _sigla, testo)  # PMP, ECO; parole intere in maiuscolo di 2-5 lettere
    return testo

if __name__ == "__main__":
    import sys
    print(normalizza(" ".join(sys.argv[1:])))
