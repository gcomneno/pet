# Stato dell’arte attuale di `gcomneno/pet` al 28 Marzo 2026 ore 19:50

## 1. Stato del repo

Il repo è in una fase buona:

* architettura stabile, senza refactor gratuiti
* CLI pubblica ormai con sostanza reale
* test verdi
* parte research che ha iniziato a produrre **leggi strutturali candidate**, non solo osservazioni sparse

### Test suite

* stato attuale: **129 passed**

---

# 2. Cosa c’è oggi di concreto nel prodotto

## CLI pubblica disponibile

Comandi attivi:

* `encode`
* `decode`
* `render`
* `validate`
* `generator`
* `signature`
* `compare`
* `classify`
* `metrics`
* `xmetrics`
* `scan`
* `atlas`
* `shape-generators`
* `query`

## Query pubbliche

`pet query` espone:

* `filter`
* `group-count`
* `same-shape`

## Feature di prodotto ormai sostanziali

### `pet generator N`

Restituisce il **rappresentante minimo canonico** della shape PET di `N`.

### `pet signature N`

Nuova capability davvero utile.
Mostra la **signature canonica della shape**, calcolata sul generatore minimo, con:

* `generator`
* `already_minimal`
* `child_generators`
* `signature`
* shape renderizzata

Questa feature ha valore reale perché distingue collisioni che `metrics` non distingue.

### `pet compare N1 N2`

Espone:

* `distance`
* `structural_distance`
* `same_shape`

### `pet classify N`

Espone predicati qualitativi già utili.

### `pet metrics` / `pet xmetrics`

Le metriche canoniche e quelle research-facing sono ormai ben separate.

---

# 3. Stato architetturale

La struttura desiderata è rimasta sana:

* `core.py` → logica PET, metriche base, generatori minimi, signature
* `cli.py` → parser e dispatch
* `io.py` → parsing/rendering/serializzazione
* `metrics.py` → metriche estese / classificazioni
* `algebra.py` → distanze / helper strutturali
* `query.py` → query su dataset
* `scan.py` → scansioni JSONL
* `atlas.py` → analisi aggregate

Quindi: **nessun bisogno attuale di riaprire modularizzazioni profonde**.

---

# 4. Cosa è emerso davvero sul piano research

Qui c’è la parte più interessante.

## A. Il generatore minimo non è solo “il più piccolo della classe”

La scoperta forte è questa:

il `generator` sembra essere una **codifica canonica ricorsiva della shape PET minima**.

In pratica:

* **encode strutturale**: shape completa → generatore minimo
* **decode strutturale**: generatore minimo → shape completa

### Evidenza bounded già verificata

Su shape osservate fino a `1,000,000`:

* unique shapes checked: **78**
* encode mismatches: **0**
* decode mismatches: **0**

Questa è già roba seria.

---

## B. `branch_profile` non è la struttura vera

Ormai questo è chiuso:

* `branch_profile` è utile
* ma è una **proiezione lossy**
* ha collisioni reali

Hai visto profili come:

* `[2,2]`
* `[3,3,1]`

che corrispondono a shape complete diverse e generatori diversi.

### Punto importante

La legge forte **non** vive sul `branch_profile`.
Vive sulla **shape completa** / signature canonica.

---

## C. Il profilo è una somma shiftata dei profili dei figli

Su `2..1,000,000` hai verificato:

* checked records: **999999**
* mismatches: **0**

Quindi il `branch_profile` del nodo padre è la **somma shiftata livello per livello dei profili dei figli**.

Tradotto brutalmente:

* il profilo è un’ombra additiva della struttura
* e per questo collassa informazione

---

# 5. Scoperta più grossa: algebra locale dei generatori

Qui hai scavato davvero bene.

## Linguaggio giusto

Non più:

* profili
* metriche aggregate
* silhouette

ma:

* **generatori canonici dei figli**
* composizione locale del nodo
* rewrite ricorsivo

## Operatore locale candidato

Se i figli canonici del nodo hanno generatori:

[
g_1 \ge g_2 \ge \dots \ge g_k \ge 1
]

allora il nodo è costruito da:

[
\Omega(g_1,\dots,g_k)=\prod_{i=1}^{k} p_i^{g_i}
]

dove `p_i` è l’i-esimo primo.

Questa è ormai la forma giusta della costruzione locale.

---

## Fattorizzazione locale del nodo

Hai verificato senza mismatch, sulle 78 shape uniche osservate:

[
\Omega(g_1,\dots,g_k)
=====================

\operatorname{primorial}(k)\cdot \prod_{i=1}^{k} p_i^{g_i-1}
]

### Lettura

Ogni nodo si scompone in:

* **guscio di arità** = `primorial(k)`
* **payload strutturale** = `∏ p_i^(g_i-1)`

Le foglie (`g_i = 1`) spariscono dal payload e restano solo nel guscio.

---

## Prima mossa locale robusta: add-leaf law

Aggiungere una foglia al root fa:

[
\Omega(g_1,\dots,g_k,1)=\Omega(g_1,\dots,g_k)\cdot p_{k+1}
]

### Evidenza bounded

* checked transitions: **53**
* mismatches: **0**

Questa è una vera operazione strutturale.

---

## Seconda mossa locale robusta: positional rewrite law

Se cambi i figli da

[
(g_1,\dots,g_k)
\to
(g'_1,\dots,g'_k)
]

senza alterare l’ordine canonico, allora il fattore moltiplicativo è:

[
\frac{\Omega(g'_1,\dots,g'_k)}{\Omega(g_1,\dots,g_k)}
=====================================================

\prod_{i=1}^{k} p_i^{g'_i-g_i}
]

### Evidenza bounded

* checked comparisons: **80**
* mismatches: **0**

Questa è la prima forma davvero credibile di **algebra locale di rewrite posizionale**.

---

# 6. Famiglie strutturali emerse

Le vecchie famiglie osservate restano valide, ma ora sono state assorbite in una lettura più generale.

## Famiglie classiche già viste

* `[k]` → `primorial(k)`
* `[k,1]`
* `[k,2]`
* `[k,m]`
* `[k,m,1]`

## Generalizzazione migliore

Ora la famiglia giusta è:

* **prefisso fisso di generatori canonici dei figli**
* più un numero variabile di foglie

Per un prefisso fisso `prefix = [g1, ..., gm]`, il generatore segue:

[
G_{prefix}(k)=\operatorname{primorial}(k)\cdot \prod_{i=1}^{m} p_i^{g_i-1}
]

Questa generalizzazione è molto più forte delle vecchie formule per `[k]`, `[k,1]`, `[k,2]`.

---

# 7. Nuovo linguaggio di lavoro

Hai approvato il rename giusto:

* `child_costs` → **`child_generators`**

Ed è corretto: non sono “costi” astratti, sono proprio i **generatori canonici dei sottorami figli**.

## Notazione simbolica emersa

È comparsa anche una forma simbolica utile:

* `2 = <1>`
* `6 = <1,1>`
* `12 = <<1>,1>`
* `36 = <<1>,<1>>`
* `192 = <<1,1>,1>`
* `184320 = <<<1>,1>,<1>,1>`

Questa notazione è buona come **linguaggio interno di lavoro**, non ancora da promuovere per forza nel CLI pubblico.

---

# 8. Tooling aggiunto

Qui hai fatto bene a non buttare via tutto come script usa-e-getta.

## Tool ora utili davvero

In `tools/` hai ormai strumenti con senso:

* `profile_signature_collisions.py`
* `profile_signature_dump.py`
* `generator_expr.py`
* `generator_tree_dump.py`

### Valore reale

Servono per:

* trovare collisioni
* ispezionare signature distinte
* visualizzare la decomposizione ricorsiva dei generatori
* ragionare sull’algebra locale

Questi non sono più “scriptini da chat”.
Sono strumentazione analitica reale.

---

# 9. Documentazione aggiornata

## Pubblica

* `docs/CLI.md` aggiornato con `signature`

## Research

Hai fissato due note importanti:

* `pet-generator-structural-encoding-note.md`
* `pet-local-generator-algebra-note.md`

Questa è stata una mossa giusta: prima fissare la scoperta, poi eventualmente trasformarla in altro.

---

# 10. Stato release

Qui il punto è semplice:

## Release pubblica più recente

* `v0.1.3`

## Su `main` ci sono già varie cose sostanziali non ancora taggate

* `query same-shape`
* `generator`
* `signature`
* note research nuove
* tooling analitico nuovo

### Lettura onesta

Una futura `v0.1.4` avrebbe **materiale vero**.
Però **non è obbligatorio taggare subito**.

La cosa giusta è decidere in base a questo:

* c’è già un blocco utente-facing coerente?
* oppure vuoi ancora chiudere un ultimo giro di sostanza?

---

# 11. Cosa è solido vs cosa è ancora aperto

## Solido, bounded

* generatore come codifica canonica della shape minima
* decode del generatore minimo verso la shape
* `branch_profile` come proiezione lossy
* collisioni reali dei profili
* operatore locale `Ω`
* fattorizzazione locale
* add-leaf law
* rewrite posizionale

## Aperto

* dimostrazione generale della **minimalità globale**
* teoria generale di quando l’ordine canonico resta invariato sotto rewrite
* formalizzazione più adulta dell’algebra locale
* decisione se alcune idee research devono diventare feature pubbliche o restare tooling/nota

---

# 12. Lettura strategica finale

In questo momento il progetto **non è più solo una CLI simpatica per giocare col PET**.

Sta diventando questo:

## Lato prodotto

Una CLI piccola ma concreta per:

* osservare shape
* confrontarle
* canonizzarle
* ispezionarle

## Lato research

Un laboratorio dove sta emergendo una **codifica canonica ricorsiva** e una **algebra locale dei generatori**.

E questa è sostanza vera.

---

# 13. Mossa successiva sensata

Se vuoi la mia lettura secca:

## Opzione A — chiudere un blocco da release

Se vuoi valore prodotto, ormai puoi iniziare a pensare a una `v0.1.4` sensata.

## Opzione B — fare ancora un giro di sostanza

Il giro più promettente è:

* non tornare sui `branch_profile`
* continuare sull’**algebra locale**
* cercare 1–2 mosse strutturali elementari in più oltre:

  * add-leaf
  * rewrite posizionale

Tra le due, io adesso sarei più tentato da **un ultimo giro piccolo sull’algebra locale**, poi release.

Se vuoi, il passo successivo lo possiamo scegliere adesso in modo chirurgico: **“verso v0.1.4”** oppure **“ultimo esperimento algebraico ad alto valore”**.
