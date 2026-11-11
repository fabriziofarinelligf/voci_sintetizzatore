# Vocabolario delle pronunce

Parole che la voce sintetica diceva male, con il modo in cui vanno scritte perché le dica giuste.
Si forma da solo: Gemini, ascoltando una pagina, segnala una parola pronunciata male e propone come riscriverla;
la frase viene riletta e Gemini, riascoltandola, conferma che il problema è risolto; a quel punto
`python regole.py conferma-pronunce` la mette in `regole.json` e da lì vale prima della sintesi di tutte le pagine successive.

Per toglierne una: `python regole.py rimuovi PAROLA` (riscrive anche questa pagina).
Questo file si rigenera con `python regole.py vocabolario`: non modificarlo a mano.

| Parola | Scritta per la voce | Perché | Prima pagina |
|---|---|---|---|
| 12ª ed., | dodicesima edizione, | L'abbreviazione viene letta in modo scorretto come 'dodici e ed'. | p52c |
| deliverable | delìverabl | Pronuncia errata con accento tronco sulla sillaba finale ('deliverabèl') | p42 |
| issue | isciu | Pronuncia errata del termine inglese ('isciò' invece di 'ìsciu') | p42 |
| l'i a | l'intelligenza artificiale | La sequenza 'l'i a' viene fusa foneticamente e accentata come l'avverbio 'lì a'. | p52c |
| pi emme o. | pi-emme-o. | Pausa marcata prima di 'o' a chiusura di frase, con caduta d'intonazione sconnessa ('del pi emme... o'). | p58a |
| T6 | T sei | Il numero 6 viene letto come 'seis' anziché 'sei' o 'six' | p59 |
| X2 | X due | Pronunciato in modo tronco e anomalo come 'iks du'. | p58a |
| X3.tre | Ics tre punto tre | La lettera X viene pronunciata erroneamente 'icsi'. | p52c |
