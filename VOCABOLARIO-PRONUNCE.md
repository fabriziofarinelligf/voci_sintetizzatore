# Vocabolario delle pronunce

Parole che la voce sintetica diceva male, con il modo in cui vanno scritte perché le dica giuste.
Si forma da solo: Gemini, ascoltando una pagina, segnala una parola pronunciata male e propone come riscriverla;
la frase viene riletta e Gemini, riascoltandola, conferma che il problema è risolto; a quel punto
`python regole.py conferma-pronunce` la mette in `regole.json` e da lì vale prima della sintesi di tutte le pagine successive.

Per toglierne una: `python regole.py rimuovi PAROLA` (riscrive anche questa pagina).
Questo file si rigenera con `python regole.py vocabolario`: non modificarlo a mano.

| Parola | Scritta per la voce | Perché | Prima pagina |
|---|---|---|---|
| "done" | "dan" | La parola inglese 'done' viene letta all'italiana ('dóne') anziché con la corretta pronuncia inglese. | p45 |
| (6ª | (sesta | Il simbolo ordinale viene letto in modo errato come 'sei scor a edizione' | p102a |
| (8ª | (ottava | Il numero ordinale '8ª' viene letto erroneamente come 'ottona' invece di 'ottava'. | p91 |
| (nella Pimbok otto: | (nel PMBOK 8: | La frase si interrompe bruscamente sui due punti prima della parentesi, lasciando l'intonazione sospesa e creando una pausa spezzata rispetto alla frase successiva. | p43 |
| (X3.tre). | (Ics tre punto tre). | La lettera X viene pronunciata erroneamente 'icsi'. | p52c |
| 12ª | dodicesima | L'abbreviazione ordinale '12ª' viene espansa in modo anomalo e incomprensibile ('dodi fin due' anziché 'dodicesima'). | p45 |
| 12ª ed., | dodicesima edizione, | L'abbreviazione viene letta in modo scorretto come 'dodici e ed'. | p52c |
| 20XX. | duemilaicsics. | La sigla segnaposto viene pronunciata in modo confuso e scorretto come 'venti la prix six'. | p83 |
| agile, | agile. | La virgola fonde il titolo della rubrica con la frase successiva, creando una pausa innaturale tra 'ambienti' e 'agile'. | p87 |
| custodi, Significa | custodi: significa | La maiuscola dopo la virgola fa fare una pausa innaturale e un cambio di tono errato. | p386 |
| deliverable | delìverabl | Pronuncia errata con accento tronco sulla sillaba finale ('deliverabèl') | p42 |
| dell'e ci o | dell'ECO | L'acronimo ECO viene sillabato lettera per lettera invece di essere letto come parola unica 'eco'. | p379 |
| delìverabl | deliverable | La parola inglese 'deliverables' è scritta in modo fonetico errato 'delìverabl' e risulta pronunciata male. | p387 |
| dieci punto zero | 10.000 | Ha letto 'dieci punto zero dollari' anziché 'diecimila dollari'. | p82 |
| diviso undici diviso | novembre | La data espressa con gli slash 17/11/2025 viene letta letteralmente come 'diciassette diviso undici diviso duemilaventicinque'. | p52b |
| domini | domìnii | Accento sbagliato: 'dòmini' invece di 'domìni' | lezioni |
| Domini | Domìnii | Accento sbagliato: 'dòmini' invece di 'domìni' | lezioni |
| driven | drìven | Accento sulla prima sillaba (Google: ˈdriv(ə)n); scelta 'drìven' a orecchio | lezioni |
| e ci o | ECO | L'acronimo ECO viene scandito come 'e ci o' anziché letto come 'eco'. | p379 |
| elaboration | ilèboreiscion | Pronuncia errata del termine inglese elaboration, accentato all'italiana/francese sulla sillaba finale. | p179 |
| Executing | Exekyuting | Pronuncia inglese gravemente storpiata, pronunciata come 'exkitig'. | p91 |
| faticano | fatìcano | Accento sdrucciolo: fatìcano, non faticàno | lezioni |
| Group | Grup | Group si legge con la u lunga (Google: ɡro͞op) | lezioni |
| group | grup | Group si legge con la u lunga (Google: ɡro͞op) | lezioni |
| Groups | Grups | Group si legge con la u lunga (Google: ɡro͞op) | lezioni |
| groups | grups | Group si legge con la u lunga (Google: ɡro͞op) | lezioni |
| Guide (8ª | Gaid (ottava | Pronuncia errata del termine inglese Guide come 'ghid' invece di 'gaid'. | p84 |
| High-Level, | High-Level | La virgola separa il modificatore dal sostantivo creando una pausa anomala nel titolo. | p179 |
| i Due; | due; | Lettura anomala 'i Due' per indicare il numero romano II | p380 |
| i i i | terzo | Il numero romano III viene letto lettera per lettera 'i i i' anziché 'terzo' | p380 |
| i i i, | terzo, | I numeri romani III vengono letti come 'i i i' anziché 'tre' o 'terzo' | p382 |
| i i"). | secondo"). | Il numero romano II viene letto come singole lettere 'i i' | p380 |
| i i; | Due; | Il numero romano II viene letto lettera per lettera 'i i' anziché come numerale ordinale/cardinale 'due' o 'two'. | p105 |
| intermedi) | intermèdi) | Accento errato sulla vocale, pronunciato come 'intermedì-i' anziché 'intermèdi' | p86 |
| issue | isciu | Pronuncia errata del termine inglese ('isciò' invece di 'ìsciu') | p42 |
| Issue | Issiu | Pronuncia errata del termine inglese, pronunciato 'isio' anziché 'ish-ue'/'issiu' | p89 |
| iteration | iterèiscen | Inglese britannico (Wiktionary ɪtəɹˈeɪʃən); scelta 'iterèiscen' a orecchio | lezioni |
| Iteration | Iterèiscen | Come iteration, maiuscola | lezioni |
| iterations | iterèiscens | Come iteration, plurale | lezioni |
| Key | Kii | La parola inglese 'Key' viene letta come 'Chi' anziché con la corretta pronuncia inglese. | p52 |
| l'11ª | l'undicesima | Allucinazione nella lettura del testo: legge 'Blondeta' anziché 'l'undicesima'. | p91 |
| L'11ª | l'undicesima | Letto erroneamente come 'undipre' invece di 'undicesima'. | p54 |
| l'a ti di di | l'ATDD | L'acronimo ATDD viene scandito lettera per lettera in modo innaturale. | p181 |
| l'i a | l'intelligenza artificiale | La sequenza 'l'i a' viene fusa foneticamente e accentata come l'avverbio 'lì a'. | p52c |
| l'i a: | l'IA: | L'acronimo IA viene letto staccato come 'i a' invece di essere pronunciato in modo naturale. | p52b |
| Medium, | Medium | La virgola spezza il binomio Medium Feature con una pausa innaturale. | p179 |
| Nell'11ª | Nell'undicesima | Il numero ordinale '11ª' viene letto erroneamente come 'unditro' anziché 'undicesima'. | p56 |
| Nell'e ci o | nell'ECO di | La sigla dell'ECO è trascritta come 'e ci o' e letta come singole lettere staccate in modo poco naturale. | p387 |
| Pensaci, | Pensaci. | La lettera maiuscola 'I' dopo la virgola provoca un'intonazione errata e spezzata. | p386 |
| pi di u | pi-di-ù | La sintesi vocale legge 'pi di un' anziché 'pi di u'. | p432 |
| pi emme bi o cappa | pi em bòk | PMBOK dopo --normalizza: letto lettera per lettera, va detto 'pi em bok' | lezioni |
| pi emme i | PMI | L'acronimo PMI viene letto scandendo 'pi emme i' in maniera staccata. | p181 |
| pi emme o. | pi-emme-o. | Pausa marcata prima di 'o' a chiusura di frase, con caduta d'intonazione sconnessa ('del pi emme... o'). | p58a |
| Pimbok | P.M.B.O.K. | Acronimo letto 'Pimbok' anziché scansito o pronunciato correttamente | p382 |
| Practices | Praktis | La parola inglese viene pronunciata in modo errato come 'practi-es'. | p105 |
| Principles | Prinsipls | Pronuncia errata del termine inglese, reso come 'principlis'. | p105 |
| Process | Pròses | Pronuncia inglese britannica: accento sulla prima sillaba (Google: ˈpräˌses) | lezioni |
| process | pròses | Pronuncia inglese britannica: accento sulla prima sillaba (Google: ˈpräˌses) | lezioni |
| quattrocento punto zero | 400.000 | Ha letto 'quattrocento punto zero dollari' anziché 'quattrocentomila dollari'. | p82 |
| rmcls.com/agile-process-chart-game-v11. | r m c l s punto com barra agile process chart game v undici. | La lettura dell'URL risulta poco fluida e la dizione dell'inglese è troppo italianizzata. | p48 |
| rmcls.com/game/process-chart-game-v12); | erre emme ci elle esse punto com slash game slash process chart game v dodici); | L'URL viene letto scorrettamente con 's' al posto degli slash e 'dodici' storpiato in 'dodigi'. | p44 |
| scope. | scoup. | Termine inglese pronunciato all'italiana ('scop') anziché con dittongo corretto ('scoup'). | p54 |
| simple | sìmpol | La parola inglese 'simple' viene letta all'italiana ('sìmple') anziché con fonetica inglese. | p56 |
| Small, Story (iuser | Small Story (user | La virgola interrompe la continuità del titolo Small Story. | p179 |
| spostano | spòstano | Accento errato sulla penultima sillaba: pronunciato 'spostàno' anziché 'spòstano'. | p87 |
| T1. | T uno. | Letto come 'Te un' anziché 'T uno' | p102a |
| T2 | T due | La sigla 'T2' viene pronunciata in modo bizzarro come 'ti dui' anziché 'ti due'. | p56 |
| T6 | T sei | Il numero 6 viene letto come 'seis' anziché 'sei' o 'six' | p59 |
| T6). | Ti sei). | Pronuncia errata della sigla 'T6', letta nuovamente 'ti seis'. | p60 |
| user | iuser | La parola 'user' viene letta con la 'u' all'italiana ('ùser') invece della pronuncia corretta 'iùser', diversamente da come fatto nelle altre frasi. | p45 |
| value | vèliu | Accento sulla prima sillaba (Google: ˈvalyo͞o) | lezioni |
| Value | Vèliu | Accento sulla prima sillaba (Google: ˈvalyo͞o) | lezioni |
| X2 | X due | Pronunciato in modo tronco e anomalo come 'iks du'. | p58a |
| X3.tre | Ics tre punto tre | La lettera X viene pronunciata erroneamente 'icsi'. | p52c |
