# voci_sintetizzatore

Voci sintetiche italiane generate in locale con [Qwen3-TTS](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base) (Apache-2.0), per video di istruzioni e audio di testi. Ogni voce sta in `voci/<nome>/`: `riferimento.wav` (la clip che fissa il timbro, così resta uguale in ogni frase), `riferimento.txt` (il suo testo), `descrizione.txt` (com'è stata creata e a cosa è adatta). Le voci non appartengono a nessuno: sono create da una descrizione testuale con Qwen3-TTS VoiceDesign.

## Voci
| Nome | Adatta a |
|---|---|
| `a1` | video di istruzioni; per i libri è lenta (`--tempo 1.1-1.2`) |
| `a2` | lettura di testi di studio (descrizione didattica suggerita da Gemini) |

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
  (lascia le frasi e il manifest in `uscita-frasi/`, o in `--lavoro DIR`, pronte per il giro con revisione)

## Voce nuova
`python crea_voce.py NOME "DESCRIZIONE IN INGLESE" [--seme 42] [--device cuda:0]` crea `voci/NOME/` con VoiceDesign.

## Opzioni di lettura
- `--pause 0.3,0.65,0.75`: secondi dopo i due punti, a fine frase, a fine blocco.
- `--normalizza`: numeri in lettere e sigle lettera per lettera (`normalizza.py`, serve `pip install num2words`).
- `--tempo 1.1,1.2`: una o più velocità dallo stesso audio.

## Giro con revisione Gemini
Gemini ascolta la pagina e segnala solo le frasi che non vanno (numero della frase, parola esatta, un'azione); si rifanno solo quelle. Sintesi e revisione possono stare su macchine diverse: si sposta la cartella di lavoro (`LAVORO`), `monta.py` non usa il modello e gira anche senza GPU.

1. `python sintetizza.py --normalizza --tempo 1.1 --voce a2 pagina40.json LAVORO` (macchina con il modello): `LAVORO/frasi/NNN.wav` + `LAVORO/manifest.json`
2. `python monta.py LAVORO`: `LAVORO/pagina.wav` + `LAVORO/pagina.json` (formato dell'app) e i secondi di ogni frase nel manifest
3. `GEMINI_API_KEY=... python revisione.py LAVORO`: `LAVORO/revisione-1.json` (voti e problemi)
4. `python correggi.py LAVORO LAVORO/revisione-1.json`: applica i problemi di gravità 2-3, scrive `modifiche-1.json` e stampa il comando del passo 5; gli errori del manuale vanno anche in `errori-testo.md`
5. `python sintetizza.py --solo 3,7,12 LAVORO` (macchina con il modello)
6. `python monta.py LAVORO`
7. `python revisione.py --verifica LAVORO`: Gemini riascolta solo le frasi cambiate, `verifica-1.json`; le correzioni risolte diventano regole candidate
8. `python report.py LAVORO`: riepilogo in italiano

Al massimo due giri di correzione per pagina (`correggi.py` rifiuta il terzo); il secondo riparte dal passo 3 e scrive `revisione-2.json`.
Azioni: `rigenera` (stesso testo, seme + 1), `riscrivi` (testo letto nuovo), `inglese` (frase letta in inglese), `pausa` (secondi dopo la frase, 0,2-1,5), `errore_testo` (refuso del manuale: annotato in `errori-testo.md` e riletto col testo corretto, dopo `--normalizza` e regole).

`regole.json` raccoglie quello che il giro ha imparato e vale in ogni sintesi nuova, dopo `--normalizza`: `sostituzioni` (parola o gruppo di parole intero `da` → `a`) e `inglese_tra_virgolette` (una frase che è tutta una citazione tra virgolette dritte o “ ” si legge in inglese, senza normalizza). Le candidate stanno in `regole-proposte.json`: `python regole.py lista`, poi `approva N` o `scarta N`; nessuna si approva da sola.

Prova senza modello e senza Gemini: `VOCI_FAKE_TTS=1` (tono al posto della voce) e `revisione.py --risposta-finta R.json`; il giro intero è in `python tests/test_giro.py`.

## Velocità misurate
| Macchina | Rapporto calcolo/audio |
|---|---|
| Colab, GPU Tesla T4 | 2,1× |
| Intel i9-10900K, 10 thread | 5,8-7× |
| AMD Ryzen AI 7 PRO 450, fp32 | 10,9× |

## Su Google Colab
```
!git clone -q https://github.com/fabriziofarinelligf/voci_sintetizzatore.git
!pip install -q qwen-tts num2words
!python voci_sintetizzatore/sintetizza_pagina.py --device cuda:0 --normalizza --tempo 1.1 blocchi.json uscita
```

## Su Kaggle (2 GPU T4, dal portatile)
`kaggle_lancia.py` usa la CLI `~/.local/bin/kaggle` (token in `~/.kaggle/access_token`) e il kernel privato `fabriziofarinelli/voci-pagine`, una versione nuova a ogni invio. Lo script generato clona il repo al commit locale, quindi prima serve `git push`.
1. `python kaggle_lancia.py invia --voce a2 --normalizza --tempo 1.1 p42.json p43.json ...`: divide le pagine in due code, una per GPU, e stampa la stima delle ore; rifiuta un lotto oltre 10 h (la sessione Kaggle ne dura al massimo 12). `--prova` scrive la cartella con script e metadata e li stampa, senza inviare.
2. `python kaggle_lancia.py attendi [--ogni 60] [--max-ore 9]`: controlla lo stato finché è COMPLETE o fallito.
3. `python kaggle_lancia.py scarica DEST`: scarica `DEST/<pagina>-lavoro/` (frasi e manifest) e il `.log`, e per ogni pagina conta le frasi del manifest e i wav.
4. In locale, per ogni pagina, il giro dal passo 2: `python monta.py DEST/p42-lavoro`, poi revisione e correzioni; le frasi da rifare (`--solo`) si rifanno in locale o con un nuovo invio.

Prova dello script generato senza Kaggle: `VOCI_FAKE_TTS=1 VOCI_KAGGLE_BASE=DIR VOCI_REPO=. python CARTELLA_PROVA/voci_pagine.py`.

## Regole
Non clonare con questi script la voce di una persona reale senza il suo consenso. Nei contenuti per l'esterno dichiara che la voce è sintetica.
