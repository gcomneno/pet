# SPEC — Prime Exponent Tree (PET)

## Dominio

PET è definito sugli interi `N >= 2`.

## Definizione informale

Ogni intero `N >= 2` viene rappresentato tramite la sua
fattorizzazione prima ordinata. Ogni esponente viene poi
rappresentato ricorsivamente con lo stesso schema.

## Sintassi

Usiamo:

- `•` per rappresentare l'esponente `1`
- una lista di coppie `(p, E)` per rappresentare un albero PET
- `p` è sempre un numero primo
- `E` è o `•` oppure un altro PET

## Forma canonica

Un PET è canonico se e solo se:

1. tutti i fattori al primo livello sono numeri primi
2. i primi sono ordinati strettamente in senso crescente
3. ogni primo compare una sola volta per livello
4. l'esponente `1` è rappresentato solo da `•`
5. ogni esponente `e >= 2` è rappresentato come `PET(e)`
6. non sono ammesse forme alternative equivalenti

## Semantica

Il valore di `•` è:

`value(•) = 1`

Il valore di un PET:

`value([(p1, E1), ..., (pk, Ek)]) = prod(p_i ^ value(E_i))`

## Proprietà richieste

### Completezza
Ogni intero `N >= 2` deve avere una rappresentazione PET.

### Esattezza
Se `T = PET(N)`, allora `value(T) = N`.

### Canonicità
Se `PET(N1) = PET(N2)`, allora `N1 = N2`.

### Unicità della forma normale
Se `N1 = N2`, allora `PET(N1) = PET(N2)`.

## Costruzione canonica

Dato `N >= 2`:

1. fattorizza `N` in primi:
   `N = prod(p_i ^ e_i)`
2. ordina i primi in senso crescente
3. per ogni esponente:
   - se `e_i = 1`, usa `•`
   - se `e_i >= 2`, usa `PET(e_i)`

## Esempi

### PET(2)

[(2, •)]

### PET(12)

[
  (2, [(2, •)]),
  (3, •)
]

### PET(72)

[
  (2, [(3, •)]),
  (3, [(2, •)])
]

## Invarianti strutturali

Gli invarianti seguenti sono proprietà della **forma dell'albero PET**, non del valore numerico.
Sono stati verificati empiricamente fino a N = 10000.

### Invariante 1 — Linearità

Le seguenti condizioni sono equivalenti:

- `is_linear(tree)` è vero
- `max_branching(tree) == 1`
- `leaf_count(tree) == 1`

Un PET lineare è una catena pura: ogni livello ha esattamente un nodo.

Esempi: `2, 3, 4, 8, 16, 32, 81, 256` — ma non `64 = 2^(2·3)`.

### Invariante 2 — Uniformità per livello

Le seguenti condizioni sono equivalenti:

- `is_level_uniform(tree)` è vero
- `structural_asymmetry(tree) == 0.0`
- tutti i valori di `branch_profile(tree)` sono uguali

Un PET uniforme ha lo stesso numero di nodi a ogni livello.
`is_linear` è il caso speciale con `max_branching == 1`.

Esempi uniformi non lineari: `36 = 2^2·3^2` con profilo `[2,2]`, `72 = 2^3·3^2` con profilo `[2,2]`.

### Invariante 3 — Squarefreeness

Le seguenti condizioni sono equivalenti:

- `is_squarefree(tree)` è vero
- `recursive_mass(tree) == 0`
- tutti i nodi sono al livello radice (nessun sottoalbero esponenziale)

Un PET squarefree è un albero piatto: tutti gli esponenti della fattorizzazione sono `1`.

Esempi: `2, 3, 6, 30, 42` — ma non `4 = 2^2`, `12 = 2^2·3`.

### Invariante 4 — Espansione

Le seguenti condizioni sono equivalenti:

- `is_expanding(tree)` è vero
- `branch_profile(tree)[-1] > branch_profile(tree)[0]`
- almeno un esponente nella fattorizzazione è composto con due o più fattori primi distinti

Un PET espandente si allarga scendendo — proprietà rara (12 casi su 10000).

Esempi: `64 = 2^6` (esponente `6=2·3`), `576 = 2^6·3^2`, `729 = 3^6`.

### Relazioni tra invarianti

- `is_linear` implica `is_level_uniform` (ma non viceversa)
- `is_squarefree` e `is_linear` sono indipendenti (es. `6` è squarefree ma non lineare; `4` è lineare ma non squarefree)
- `is_expanding` è incompatibile con `is_linear` (un albero espandente non può essere una catena)
- `is_squarefree` è incompatibile con `is_expanding` (se tutti gli esponenti sono `1`, nessun sottoalbero può ramificarsi)

### Nota

Questi invarianti emergono dalla struttura ricorsiva di PET e non hanno
un corrispondente diretto nella fattorizzazione prima classica.

## Metriche analitiche (pet_metrics)

Le seguenti metriche sono definite in `src/pet_metrics.py` e operano su PET canonici validi.

### Metriche scalari

- `verticality_ratio(tree)` — rapporto `height / node_count`. Vale `1.0` per catene pure, tende a `0` per alberi piatti.
- `structural_asymmetry(tree)` — deviazione standard del `branch_profile`. Vale `0.0` per alberi uniformi per livello.
- `recursive_mass(tree)` — numero di nodi appartenenti a sottoalberi esponenziali (già in PET-Base).
- `leaf_ratio(tree)` — rapporto `leaf_count / node_count` come `Fraction` esatta. Appartiene a un insieme sparso e discreto di valori razionali.

### Classificatori booleani

- `is_linear(tree)` — `True` se il PET è una catena pura (`max_branching == 1`).
- `is_level_uniform(tree)` — `True` se tutti i livelli hanno lo stesso numero di nodi.
- `is_squarefree(tree)` — `True` se `recursive_mass == 0` (tutti gli esponenti sono `1`).
- `is_expanding(tree)` — `True` se l'ultimo livello ha più nodi del primo (proprietà rara).

### Classificatore morfologico

`profile_shape(tree)` restituisce una stringa che descrive la forma del profilo:
- `'point'` — albero di altezza 1 (numero squarefree o primo)
- `'linear'` — catena pura, tutti i livelli con un solo nodo
- `'normal'` — forma tipica, profilo non crescente
- `'expanding'` — ultimo livello più largo del primo (raro: ~12 casi su 10000)
- `'bell'` — picco interno al profilo, né al primo né all'ultimo livello (rarissimo: ~6 casi su 100000)

### Osservazioni sui valori di leaf_ratio

Il rapporto `leaf_count / node_count` appartiene a un insieme sparso e discreto.
Famiglie identificate fino a N = 500000:

- `1/k` — catene di altezza `k` (profilo `[1,1,...,1]`)
- `k/(k+1)` — profilo `[k,1]`, converge a `1`
- `k/(2k+1)` — profilo `[k,k,1]`, converge a `1/2`

## Famiglie di leaf_ratio

Il rapporto `leaf_count / node_count` appartiene a un insieme sparso e discreto di frazioni razionali.
Le famiglie identificate seguono la forma generale `k / (p·k + 1)` dove `p >= 0`.

### Famiglie accessibili (primi esempi raggiungibili)

| p | formula | esempi di ratio | primo esempio | profilo tipico |
|---|---|---|---|---|
| 0 | `k/1` = `1` | `1` | N=2 | `[k]` |
| 1 | `k/(k+1)` | `1/2, 2/3, 3/4, ...` | N=4 | `[k, 1]` |
| 2 | `k/(2k+1)` | `1/3, 2/5, 3/7, ...` | N=16 | `[k, k, 1]` |
| 3 | `k/(3k+1)` | `1/4, 2/7, ...` | N=65536 | `[k, k, k, 1]` |

### Famiglie inaccessibili (primi esempi astronomici)

Per `p >= 4`, le famiglie `k/(pk+1)` esistono teoricamente ma i loro primi esempi
richiedono numeri della forma `2^(2^(2^...))` con profondità crescente —
irraggiungibili per esplorazione diretta.

Il primo esempio per `p=3, k=1` è già `N = 65536 = 2^16`.
Il primo esempio per `p=4, k=1` richiederebbe `2^(2^(2^(2^(2^2)))) = 2^(2^65536)`,
un numero con decine di migliaia di cifre.

### Famiglie ibride

Oltre alla serie principale, esistono ratio che non seguono la forma `k/(pk+1)`:

| ratio | profilo | primo esempio |
|---|---|---|
| `3/8` | `[3, 3, 2]` | N=32400 |
| `5/9` | `[5, 3, 1]` | N=277200 |
| `4/7` | `[4, 2, 1]` | N=5040 |
| `3/5` | `[3, 2]` | N=180 |
| `5/8` | `[5, 2, 1]` | N=55440 |
| `5/7` | `[5, 2]` | N=13860 |

Questi ratio emergono da strutture miste in cui i livelli non sono uniformi.
La loro classificazione completa è ancora aperta.

### Nota
La scarsità dei ratio accessibili è una conseguenza diretta della struttura ricorsiva di PET: ogni nuovo livello di profondità richiede esponenti che sono a loro volta numeri strutturalmente complessi, il cui primo esempio cresce in modo superesponenziale.

## Confronto con famiglie aritmetiche note

Le metriche PET sono state calcolate su quattro famiglie aritmetiche classiche per valutare il potere discriminante di PET rispetto alla teoria dei numeri tradizionale.

### Primorials (2, 6, 30, 210, 2310, ...)

Firma PET perfettamente uniforme:
- `shape = point` per tutti
- `height = 1`, `asym = 0.0`, `ratio = 1`

Questo riflette il fatto che i primorials sono squarefree per costruzione (prodotto di primi distinti con esponente 1).
PET li identifica istantaneamente, ma questo è equivalente al già noto criterio squarefree.

### Numeri di Hamming (5-smooth)

Nessuna firma PET coerente — mescola `point`, `linear`, `normal`.
PET non li separa come famiglia distinta.

### Numeri altamente composti

Quasi tutti `shape = normal`, con `asym` e `ratio` crescenti all'aumentare di N.
PET cattura la complessità strutturale crescente ma non li discrimina nettamente.

### Numeri perfetti

Troppo pochi per concludere (solo 4 noti e calcolabili).
Nessuna firma PET comune identificata.

### Conclusione

PET separa nettamente solo i Primorials — ma questo coincide con la proprietà squarefree già nota. Per le altre famiglie, PET descrive la morfologia ma non offre discriminazione aggiuntiva rispetto alla fattorizzazione classica.

Il valore di PET resta negli invarianti strutturali scoperti e nella rappresentazione ricorsiva canonica. PET-Algebra potrebbe essere il livello dove emerge potere classificatorio genuinamente nuovo.

## PET-Algebra

PET-Algebra studia le operazioni strutturali sui PET canonici.
Tutte le operazioni producono PET canonici che rappresentano interi.
Il codice vive in `src/pet_algebra.py`.

### Operazione: graft

`graft(tree, scion)` sostituisce ogni foglia (`None`) di `tree` con `scion`.

Ogni nodo di `tree` il cui esponente è `None` (esponente = 1) riceve
`scion` come nuovo sottoalbero esponenziale.

**Esempio:**
```
PET(6)  = [(2,•),(3,•)]
PET(2)  = [(2,•)]
graft(PET(6), PET(2)) = [(2,[(2,•)]),(3,[(2,•)])] = PET(36)
```

### Proprietà algebriche di graft

| Proprietà | Risultato |
|---|---|
| Commutatività | ✗ |
| Associatività | ✓ |
| Elemento identità | ✗ |
| Elemento assorbente | ✗ |
| Idempotenza | ✗ |

`graft` è un'operazione **non commutativa ma associativa**.

### Teorema 1 — graft su squarefree

Per ogni intero `n` squarefree e ogni intero `k >= 2`:

> `decode(graft(PET(n), PET(k))) = n^k`

Innestare `PET(k)` su un PET squarefree equivale a elevare `n` alla potenza `k`.

### Teorema 2 — autoinnesto su squarefree

Per ogni intero `n` squarefree:

> `decode(graft(PET(n), PET(n))) = n^n`

L'autoinnesto di un PET squarefree produce `n^n`.

### Corollario del Teorema 2 — graft iterato

Definiamo il graft iterato `g^k(n)` come:
- `g^0(n) = n`
- `g^k(n) = graft(g^(k-1)(n), PET(n))`

Per ogni `n` squarefree:

> `decode(g^k(n)) = n^(n^(n^...))` — torre di potenze di altezza `k+1`

Esempi per `n=2`:
- `g^0(2) = 2`
- `g^1(2) = 4 = 2^2`
- `g^2(2) = 16 = 2^(2^2)`

### Teorema 3 — graft ricorsivo (caso generale)

Per ogni `n >= 2` e `k >= 2`:

> `decode(graft(PET(n), PET(k))) = prod(p_i ^ f(e_i, k))`

dove `f(e, k) = k` se `e = 1`, altrimenti `f(e, k) = decode(graft(PET(e), PET(k)))`.

In altre parole: `graft(PET(n), PET(k))` eleva ricorsivamente ogni esponente
nella fattorizzazione di `n` alla potenza `k`.

I Teoremi 1 e 2 sono casi speciali:
- quando `n` è squarefree, tutti gli esponenti sono `1` → `f(1,k) = k` → `decode = n^k`
- quando `k = n` squarefree → `decode = n^n`

### Nota

Per `n` non squarefree il risultato di `graft` è sempre un intero valido, ma la corrispondenza con `n^k` o `n^n` non vale in generale.
La struttura algebrica per i non-squarefree è ancora aperta.

### Operazione: distance

`distance(a, b)` misura la distanza strutturale tra due PET in termini di **coincidenza di primi**.

- primi presenti in un solo albero contribuiscono con il loro intero node count
- primi presenti in entrambi contribuiscono con la distanza ricorsiva tra i sottoalberi esponenziali
- due foglie (`None`) hanno distanza `0`
- `distance(a, a) = 0` per ogni PET

### Operazione: structural_distance

`structural_distance(a, b)` misura la distanza tra due PET ignorando i valori dei primi — confronta solo la **forma** dell'albero.

- due PET hanno `structural_distance = 0` se e solo se sono isomorfi come alberi ordinati
- `PET(4) = [(2,[(2,•)])]` e `PET(9) = [(3,[(2,•)])]` hanno `structural_distance = 0`

### Relazione tra le due distanze

Le due metriche sono complementari — nessuna sussume l'altra:

| caso | distance | structural_distance |
|---|---|---|
| PET(2) vs PET(3) | 2 | 0 |
| PET(4) vs PET(9) | 4 | 0 |
| PET(12) vs PET(18) | 2 | 0 |
| PET(2) vs PET(30) | 2 | 2 |
| PET(4) vs PET(12) | 1 | 3 |

`distance` cattura la somiglianza aritmetica (quali primi condividono),
`structural_distance` cattura la somiglianza morfologica (che forma hanno).
