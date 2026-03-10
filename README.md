# PET — Prime Exponent Tree
PET è un modello canonico per rappresentare ogni intero `N >= 2` come un albero ricorsivo basato sulla fattorizzazione prima e sulla struttura degli esponenti.

## Idea
Ogni intero `N >= 2` si scrive in modo unico come: N = prod(p_i ^ e_i)

dove i `p_i` sono numeri primi distinti e gli `e_i >= 1`.

PET prende questa fattorizzazione e applica la stessa idea ricorsivamente agli esponenti.

In pratica:
- i primi stanno nei nodi
- gli esponenti stanno nei sottoalberi
- l'esponente `1` è rappresentato da una foglia terminale

## Obiettivo
PET vuole essere:
- esatto
- invertibile
- canonico
- ricorsivo
- analizzabile strutturalmente

## Esempio
12 = 2^2 * 3^1

PET(12) =
[
  (2, [(2, •)]),
  (3, •)
]

## Proprietà chiave
Non devono esistere due forme PET distinte per lo stesso numero.
La rappresentazione deve essere unica.

## Struttura del progetto
- `README.md` — panoramica del progetto
- `Makefile` — comandi rapidi per test e demo
- `src/pet.py` — implementazione PET
- `tests/test_pet.py` — test di roundtrip
- `tests/test_invalid_pet.py` — test su input PET invalidi
- `docs/SPEC.md` — specifica formale
- `docs/VISION.md` — visione concettuale del progetto
- `docs/examples/basic_examples.txt` — esempi base

## Uso rapido
```bash
python3 src/pet.py 72
python3 src/pet.py --json 136
python3 src/pet.py --render pet136.json
python3 src/pet.py --decode pet136.json
python3 src/pet.py --validate pet136.json
```

## Formato JSON canonico
PET usa una rappresentazione JSON canonica basata su una lista di nodi.

Ogni nodo ha esattamente questa forma:
```json
{
  "p": <primo>,
  "e": null | [ ... ]
}
```

Dove:
p è la base prima
e è:

- null quando l'esponente è 1
- un altro PET (ricorsivamente) quando l'esponente è >= 2

Un documento JSON PET è quindi una lista non vuota di nodi, con primi in ordine strettamente crescente a ogni livello.

Esempio: 12 = 2^2 * 3

PET interno:
[(2, [(2, None)]), (3, None)]

JSON canonico:
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

## Note
- Il formato JSON è strutturale, non una sintassi aritmetica.
- È canonico: interi equivalenti devono produrre la stessa struttura PET.
- Il sottoalbero dell'esponente è a sua volta un PET che codifica l'esponente.
- Forme JSON invalide vengono rifiutate da from_jsonable(...), --decode e --validate.
