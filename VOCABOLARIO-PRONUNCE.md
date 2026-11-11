# Vocabolario delle pronunce

Parole che la voce sintetica diceva male, con il modo in cui vanno scritte perché le dica giuste.
Si forma da solo: Gemini, ascoltando una pagina, segnala una parola pronunciata male e propone come riscriverla;
la frase viene riletta e Gemini, riascoltandola, conferma che il problema è risolto; a quel punto
`python regole.py conferma-pronunce` la mette in `regole.json` e da lì vale prima della sintesi di tutte le pagine successive.

Per toglierne una: `python regole.py rimuovi PAROLA` (riscrive anche questa pagina).
Questo file si rigenera con `python regole.py vocabolario`: non modificarlo a mano.

Ancora nessuna parola.
