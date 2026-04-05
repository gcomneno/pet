# PartialPET v0

## 1. Obiettivo

Scopo della ricerca:

> avere uno strumento di sintesi strutturale per input giganteschi, quando la fattorizzazione completa è impossibile.

Ipotesi di lavoro:

> una PET parziale può essere più concreta e realistica della fattorizzazione completa, purché rappresenti informazione strutturale certificata, monotona e budgetata.

---

## 2. Definizione di lavoro

Una **PartialPET** non è una PET incompleta “a caso”.

È:

> una rappresentazione canonica di informazione strutturale certificata sulla PET esatta ignota di un intero.

Versione root-level v0:

- `known_root_children`
- `known_root_generator_lower_bound`
- `residual_status`
- `root_generator_lower_bound`
- `exact_root_anatomy`
- `exact_root_children` solo se la chiusura è esatta

Semantica:

- la PET esatta vera deve essere compatibile con la `PartialPET`
- con più budget, la `PartialPET` deve solo raffinarsi

---

## 3. Regime sperimentale

Per osservare davvero la `PartialPET` abbiamo dovuto disattivare le maniere forti del probe:

- `allow_pollard_rho = False`
- `allow_small_residual_exact = False`

Motivo:

- altrimenti il probe chiude troppo presto
- e non si vede lo stato parziale intermedio

Quindi il test non misura la capacità di chiudere, ma la qualità della conoscenza strutturale parziale.

---

## 4. Witness sperimentali

## Witness 1

Numero:

`15808432 = 2^4 * 991 * 997`

Setup parziale:

- `schedule = [2]`
- no rho
- no small-residual-exact

Risultato parziale:

- `exact_root_anatomy = False`
- `known_root_children = [[[[]]]]`
- `known_root_generator_lower_bound = 16`
- `residual_status = composite-non-prime-power`
- `root_generator_lower_bound = 240`

Verità finale:

- `exact_root_children = [[], [], [[[]]]]`
- `exact_root_generator = 240`

Osservazione:

- il probe recupera già un ramo vero (`2^4`)
- il lower bound strutturale coincide già col generator finale esatto

---

## Witness 2

Numero:

`142275888 = 2^4 * 3^2 * 991 * 997`

Setup parziale:

- `schedule = [3]`
- no rho
- no small-residual-exact

Risultato parziale:

- `exact_root_anatomy = False`
- `known_root_children = [[[]], [[[]]]]`
- `known_root_generator_lower_bound = 144`
- `residual_status = composite-non-prime-power`
- `root_generator_lower_bound = 5040`

Verità finale:

- `exact_root_children = [[], [], [[]], [[[]]]]`
- `exact_root_generator = 5040`

Osservazione:

- il probe recupera due rami veri (`3^2`, `2^4`)
- anche qui il lower bound strutturale è già esatto

---

## Witness 3

Numero:

`3556897200 = 2^4 * 3^2 * 5^2 * 991 * 997`

Setup parziale:

- `schedule = [5]`
- no rho
- no small-residual-exact

Risultato parziale:

- `exact_root_anatomy = False`
- `known_root_children = [[[]], [[]], [[[]]]]`
- `known_root_generator_lower_bound = 3600`
- `residual_status = composite-non-prime-power`
- `root_generator_lower_bound = 277200`

Verità finale:

- `exact_root_children = [[], [], [[]], [[]], [[[]]]]`
- `exact_root_generator = 277200`

Osservazione:

- il probe recupera tre rami veri
- il lower bound strutturale coincide ancora col generator finale esatto

---

## 5. Cosa mostrano questi witness

Mostrano che esistono famiglie non banali in cui una `PartialPET` budgetata:

- resta aperta
- contiene rami veri della root
- mantiene soundness
- produce un `root_generator_lower_bound` già molto forte
- in questi witness, coincide addirittura col generator finale esatto

Quindi la `PartialPET` non collassa subito in informazione banale.

---

## 6. Cosa NON mostrano

Non mostrano che:

- la `PartialPET` sostituisce la fattorizzazione in generale
- il `root_generator_lower_bound` sarà spesso esatto
- il metodo scala automaticamente ai numeroni monster
- il probe attuale sia già la teoria finale

In particolare, questi witness sono favorevoli perché il residuo finale è un CNPP semiprimo, quindi il lower bound “almeno 2 figli” è già molto informativo.

---

## 7. Conclusione provvisoria

Conclusione minima, ma seria:

> la PartialPET è un oggetto sperimentalmente non vuoto e non banale.

Più precisamente:

> esistono casi in cui, con budget debole e senza chiusure aggressive, il probe produce una sintesi strutturale parziale corretta e utile prima della fattorizzazione completa.

Questo giustifica il passo successivo:

- formalizzare meglio la `PartialPET`
- separare esatto / lower bound / hint / certificato
- cercare famiglie dove il residuo non sia solo “semiprimo travestito”

---

## 8. Prossimi passi

Ordine sano:

1. consolidare questa nota
2. definire formalmente la relazione di raffinamento tra due `PartialPET`
3. cercare witness non basati solo su `known prime-powers × semiprime`
4. capire quando il `root_generator_lower_bound` è esatto e quando no

---

---

## 9. Relazione di raffinamento tra due PartialPET

### 9.1 Intuizione

Se `P₂` raffina `P₁`, allora `P₂` è **più informativa** di `P₁`:

- lascia meno possibilità aperte
- conserva tutta l'informazione certa già presente in `P₁`
- restringe, senza contraddirli, i vincoli strutturali residui

Useremo la notazione:

> `P₂ ⊑ P₁`

per indicare che `P₂` raffina `P₁`.

---

### 9.2 Definizione semantica ideale

Per ogni `PartialPET` `P`, sia `Compat(P)` l'insieme delle PET esatte compatibili con `P`.

Allora la definizione concettualmente corretta è:

> `P₂ ⊑ P₁` se e solo se `Compat(P₂) ⊆ Compat(P₁)`.

Questa è la definizione ideale, ma nel v0 non costruiamo ancora esplicitamente l'insieme `Compat(P)`.
Per questo introduciamo una versione **operativa e conservativa** della relazione di raffinamento.

---

### 9.3 Forma root-level di una PartialPET v0

Nel v0 consideriamo una `PartialPET` root-level come un oggetto della forma:

- `K = known_root_children`
- `kg = known_root_generator_lower_bound`
- `σ = residual_status`
- `rg = root_generator_lower_bound`
- `exact = exact_root_anatomy`
- `E = exact_root_children` (solo se `exact = True`)

dove:

- `K` è la lista canonica dei rami root già certi
- `kg` è il lower bound dovuto ai soli rami noti
- `σ` è la classe strutturale del residuo
- `rg` è il lower bound totale sulla root
- `exact` indica se la root anatomy è già esatta
- `E` è la root anatomy esatta, quando disponibile

---

### 9.4 Inclusione multiseto dei rami noti

Poiché i root children possono ripetersi, useremo l'inclusione **come multiseto**.

Scriviamo:

> `K₁ ⊆m K₂`

per dire che ogni ramo presente in `K₁` compare anche in `K₂` con molteplicità almeno uguale.

Allo stesso modo, se `E` è una root anatomy esatta e `K ⊆m E`, allora `E \\ K` indica il contributo residuo esatto ottenuto togliendo da `E` i rami già noti in `K`.

---

### 9.5 Relazione di raffinamento operativa v0

Diremo che `P₂ ⊑v0 P₁` se valgono tutte le condizioni seguenti.

#### (R1) I rami noti possono solo aumentare

> `K₁ ⊆m K₂`

Un raffinamento non può dimenticare rami già certificati.

#### (R2) I lower bound non possono diminuire

> `kg₂ ≥ kg₁`  
> `rg₂ ≥ rg₁`

Una `PartialPET` più informativa non può avere bound strutturali più deboli.

#### (R3) Se `P₁` è già esatta, il raffinamento deve coincidere

Se `exact₁ = True`, allora deve valere:

- `exact₂ = True`
- `E₂ = E₁`

Una root anatomy già esatta non può essere ulteriormente raffinabile in modo non banale.

#### (R4) Se entrambe sono non esatte, lo stato residuo può solo restare uguale o diventare più specifico

Se `exact₁ = False` e `exact₂ = False`, allora `σ₂` deve essere uguale a `σ₁` oppure più specifico.

Nel v0 formalizziamo esplicitamente solo il seguente caso di specializzazione:

> `perfect-power-composite-base ⊑ composite-non-prime-power`

cioè ogni `perfect-power-composite-base` è un caso particolare di `composite-non-prime-power`.

#### (R5) Se `P₂` è esatta e `P₁` no, l'esatto deve essere compatibile con il grezzo

Se `exact₁ = False` e `exact₂ = True`, allora:

1. i rami noti di `P₁` devono comparire nella root anatomy esatta di `P₂`

   > `K₁ ⊆m E₂`

2. il contributo residuo esatto

   > `R = E₂ \\ K₁`

   deve rispettare i vincoli strutturali grezzi di `σ₁`

Nel v0 imponiamo le seguenti compatibilità minime:

- se `σ₁ = unit`, allora `R = []`
- se `σ₁ = prime-by-sympy`, allora `R = [[]]`
- se `σ₁ = prime-power-by-sympy`, allora `|R| = 1`
- se `σ₁ = composite-non-prime-power`, allora `|R| ≥ 2`
- se `σ₁ = perfect-power-composite-base`, allora nel v0 imponiamo solo `|R| ≥ 2`

Quest'ultimo caso è volutamente debole: la sua semantica strutturale fine non è ancora formalizzata nel v0.

---

### 9.6 Interpretazione

La relazione `⊑v0` è un **preordine conservativo**:

una `PartialPET` raffina un'altra quando:

- conserva tutti i rami certi già noti
- non abbassa nessun lower bound
- non contraddice lo stato residuo precedente
- e, se arriva a una chiusura esatta, realizza una root anatomy compatibile con i vincoli grezzi precedenti

In altre parole, `⊑v0` è una nozione di **aumento monotono di conoscenza strutturale**.

---

### 9.7 Esempio sui witness

Nel witness 1, la `PartialPET` parziale è:

- `K = [[[[]]]]`
- `σ = composite-non-prime-power`
- `rg = 240`
- `exact = False`

La verità finale è:

- `E = [[], [], [[[]]]]`
- `exact = True`

Verifica:

- `[[[[]]]] ⊆m [[], [], [[[]]]]`
- il contributo residuo esatto è `R = [[], []]`
- quindi `|R| = 2`
- questo è compatibile con `composite-non-prime-power`
- inoltre il lower bound totale `240` coincide con il generator esatto finale

Quindi la PET esatta finale raffina correttamente la `PartialPET` parziale osservata a budget basso.

---

### 9.8 Uso previsto

La relazione di raffinamento serve soprattutto a formulare la proprietà di monotonicità attesa del probe:

> con budget crescente, la `PartialPET` prodotta dovrebbe raffinare quella ottenuta con budget minore

cioè, idealmente:

> `P_budget_alto ⊑v0 P_budget_basso`

Questa è la legge naturale da verificare sperimentalmente nel seguito.

---

### 9.9 Limiti del v0

La relazione `⊑v0` è utile ma ancora grezza.

Non cattura ancora bene:

- la struttura interna del residuo
- il caso `perfect-power-composite-base`
- il confronto fine tra due stati non esatti strutturalmente diversi
- il raffinamento ricorsivo sotto la root

Per questo va intesa come:

> relazione di raffinamento root-level v0

e non come teoria finale delle `PartialPET`.

---

### 9.10 Conclusione

Nel v0, il raffinamento tra due `PartialPET` viene inteso come restringimento monotono dell'insieme delle PET esatte compatibili, realizzato in modo operativo tramite:

- crescita dei rami noti
- crescita dei lower bound
- compatibilità dello stato residuo
- coerenza della chiusura esatta con i vincoli parziali precedenti

---

---

## 10. Test di monotonicità del probe

### 10.1 Obiettivo

Una volta definita la relazione di raffinamento `⊑v0`, il comportamento naturale atteso del probe è il seguente:

> a parità di input, aumentando il budget, la `PartialPET` prodotta dovrebbe raffinare — o almeno non contraddire — quella ottenuta con budget minore.

In forma ideale:

> `P_budget_alto ⊑v0 P_budget_basso`

Questa è la proprietà di monotonicità che il probe dovrebbe soddisfare nel regime in cui stiamo osservando davvero stati parziali, cioè senza chiusure aggressive.

---

### 10.2 Regime sperimentale consigliato

Per osservare la monotonicità della conoscenza strutturale parziale, il regime sperimentale raccomandato è:

- `allow_pollard_rho = False`
- `allow_small_residual_exact = False`

Motivo:

- `pollard_rho` può trasformare uno stato grezzo in uno stato quasi chiuso con un singolo split fortunato
- `small_residual_exact` può far sparire lo stato parziale finale proprio quando diventa più interessante osservarlo

Questi due meccanismi non sono sbagliati, ma tendono a mascherare il comportamento intrinseco della `PartialPET` come oggetto di conoscenza parziale.

---

### 10.3 Forma del test

Dato un intero `n` e una famiglia crescente di schedule, per esempio:

- `[2]`
- `[3]`
- `[5]`
- `[10]`

si costruiscono le corrispondenti `PartialPET`:

- `P₂`
- `P₃`
- `P₅`
- `P₁₀`

e si verifica, per ogni coppia consecutiva, che valga:

- `P₃ ⊑v0 P₂`
- `P₅ ⊑v0 P₃`
- `P₁₀ ⊑v0 P₅`

In alternativa, si può verificare direttamente la catena completa:

> `P_budget_max ⊑v0 ... ⊑v0 P_budget_min`

---

### 10.4 Condizioni osservabili minime

Nel v0, anche senza implementare ancora un comparatore completo `refines(P2, P1)`, la monotonicità può essere osservata tramite alcune condizioni minime:

#### (M1) I rami noti non devono sparire

Passando a un budget più alto, `known_root_children` deve:

- restare uguale
- oppure crescere come multiseto

Mai perdere rami già certificati.

#### (M2) I lower bound non devono diminuire

Passando a un budget più alto:

- `known_root_generator_lower_bound` non deve diminuire
- `root_generator_lower_bound` non deve diminuire

#### (M3) La chiusura esatta non può contraddire lo stato precedente

Se a budget basso si osserva una `PartialPET` non esatta e a budget alto si osserva una root anatomy esatta, allora:

- i rami noti precedenti devono comparire nell'esatto finale
- il contributo residuo esatto deve essere compatibile con il `residual_status` precedente

#### (M4) Lo stato residuo non deve diventare meno informativo

Nel v0, questo significa almeno che:

- non si deve passare da uno stato più specifico a uno più grezzo senza giustificazione
- in particolare, non si dovrebbe osservare una regressione strutturale manifesta

---

### 10.5 Witness attuali come casi di monotonicità

I tre witness attuali forniscono già esempi favorevoli di comportamento monotono:

- con budget debole si osserva una `PartialPET` aperta ma informativa
- con budget alto si osserva la PET esatta finale
- la PET esatta finale raffina la `PartialPET` parziale nel senso di `⊑v0`

In particolare, in tutti e tre i witness osservati finora:

- i rami noti parziali compaiono integralmente nella root anatomy finale
- il `root_generator_lower_bound` parziale coincide con il generator esatto finale

Questo rende i witness attuali particolarmente adatti come primi casi positivi di monotonicità.

---

### 10.6 Cosa sarebbe una violazione seria

Nel v0, costituirebbero segnali di allarme forti:

- perdita di rami già noti passando a budget maggiore
- diminuzione di `known_root_generator_lower_bound`
- diminuzione di `root_generator_lower_bound`
- chiusura esatta finale incompatibile con i rami noti parziali precedenti
- chiusura esatta finale incompatibile con il `residual_status` precedentemente osservato

Una qualsiasi di queste condizioni indicherebbe che il probe non si sta comportando come un costruttore monotono di conoscenza strutturale.

---

### 10.7 Limiti dei test di monotonicità nel v0

Nel v0, i test di monotonicità restano ancora limitati da due fattori:

1. la semantica del residuo è ancora troppo grezza, soprattutto per i casi `composite-non-prime-power`
2. non esiste ancora una formalizzazione ricorsiva completa della `PartialPET`

Quindi i test di monotonicità del v0 non vanno letti come prova finale di correttezza teorica, ma come:

> controllo operativo della coerenza del probe come generatore di conoscenza parziale.

---

### 10.8 Prossimo passo naturale

Una volta consolidati i witness e la relazione `⊑v0`, il passo successivo naturale è:

> implementare un comparatore operativo `refines_v0(P2, P1)`

da usare direttamente nei test automatici.

Questo permetterebbe di trasformare la monotonicità da principio informale a proprietà verificata sistematicamente su famiglie di input e schedule crescenti.
