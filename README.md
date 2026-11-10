# voci_sintetizzatore

Voci sintetiche italiane generate in locale con [Qwen3-TTS](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base) (Apache-2.0), per video di istruzioni e audio di testi. Ogni voce sta in `voci/<nome>/`: `riferimento.wav` (la clip che fissa il timbro, così resta uguale in ogni frase), `riferimento.txt` (il suo testo), `descrizione.txt` (com'è stata creata e a cosa è adatta). Le voci non appartengono a nessuno: sono create da una descrizione testuale con Qwen3-TTS VoiceDesign.

## Voci
| Nome | Adatta a |
|---|---|
| `a1` | video di istruzioni; per i libri è lenta (`--tempo 1.15-1.25`) |

## Installazione
```
python3 -m venv ~/tts-venv
~/tts-venv/bin/pip install --extra-index-url https://download.pytorch.org/whl/cpu torch torchaudio qwen-tts
```
Su Google Colab con GPU basta `pip install qwen-tts`. Il modello (circa 4 GB) si scarica al primo uso.

## Uso
- Scene di un video (un file `sN.txt` per scena → `sN.mp3` + `sN.srt`):
  `python voce_qwen.py [--voce a1] [--tempo 0.85] [--device cuda:0] s1.txt s2.txt`
- Testo a blocchi (JSON con una lista di stringhe → `.wav` + `.json` con inizio e fine di ogni blocco):
  `python sintetizza_pagina.py [--voce a1] [--tempo 1.2] [--device cuda:0] blocchi.json uscita`

## Velocità misurate
| Macchina | Rapporto calcolo/audio |
|---|---|
| Colab, GPU Tesla T4 | 2,1× |
| Intel i9-10900K, 10 thread | 5,8-7× |
| AMD Ryzen AI 7 PRO 450, fp32 | 10,9× |

## Su Google Colab
```
!git clone -q https://github.com/fabriziofarinelligf/voci_sintetizzatore.git
!pip install -q qwen-tts
!python voci_sintetizzatore/sintetizza_pagina.py --device cuda:0 blocchi.json uscita
```

## Regole
Non clonare con questi script la voce di una persona reale senza il suo consenso. Nei contenuti per l'esterno dichiara che la voce è sintetica.
