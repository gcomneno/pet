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
