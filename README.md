# PET — Prime Exponent Tree

PET è un modello canonico per rappresentare ogni intero `N >= 2` come un albero ricorsivo basato sulla fattorizzazione prima e sulla struttura degli esponenti.

## Idea

Ogni intero `N >= 2` si scrive in modo unico come:

```
N = p1^e1 * p2^e2 * ... * pk^ek
```

dove i `p_i` sono numeri primi distinti in ordine crescente e gli `e_i >= 1`.

PET applica la stessa idea ricorsivamente agli esponenti:
- i primi stanno nei nodi
- gli esponenti stanno nei sottoalberi
- l'esponente `1` è rappresentato da una foglia terminale (`null` in JSON)

## Proprietà
- **canonico** — un solo PET per ogni intero
- **esatto** — il PET rappresenta esattamente il numero
- **invertibile** — dal PET si ricostruisce l'intero senza perdita
- **validabile** — forme non canoniche vengono rifiutate esplicitamente
- **serializzabile** — il PET si salva e si scambia come JSON

## Esempio

```
12 = 2^2 * 3^1

PET(12) = [(2, [(2, •)]), (3, •)]
```

## Formato JSON canonico

Ogni nodo PET ha esattamente questa forma:

```json
{
  "p": <primo>,
  "e": null | [ ... ]
}
```

- `p` è la base prima
- `e` è `null` quando l'esponente è `1`, oppure un altro PET quando l'esponente è `>= 2`

Un documento JSON PET è una lista non vuota di nodi, con primi in ordine strettamente crescente a ogni livello.

Esempio — `12 = 2^2 * 3`:

```json
[
  {
    "p": 2,
    "e": [
      {
        "p": 2,
        "e": null
      }
    ]
  },
  {
    "p": 3,
    "e": null
  }
]
```

Il formato JSON è **canonico e machine-facing**. La funzione `render()` produce invece un output **human-facing** non destinato allo scambio di dati.

## Installazione

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Uso rapido

```bash
pet encode 72
pet encode --json 72
pet metrics 256
pet metrics --json 256
pet render FILE.json
pet decode FILE.json
pet validate FILE.json
```

## Struttura del progetto

```bash
src/pet.py                        — implementazione PET
tests/test_pet.py                 — test di roundtrip
tests/test_invalid_pet.py         — test su input invalidi
tests/test_metrics.py             — test sulle metriche strutturali
tests/test_cli_metrics.py         — test CLI metriche
tests/test_cli_metrics_json.py    — test CLI metriche JSON
docs/SPEC.md                      — specifica formale
docs/VISION.md                    — visione concettuale
docs/examples/basic_examples.txt  — esempi base
```

## Test

```bash
make test
```

## Metriche strutturali

PET espone metriche sulla forma dell'albero:
- `node_count` — numero totale di nodi
- `leaf_count` — numero di foglie (esponenti `1`)
- `height` — profondità ricorsiva massima
- `max_branching` — massimo numero di nodi a un singolo livello
- `branch_profile` — nodi per livello
- `recursive_mass` — nodi appartenenti a sottoalberi esponenziali
