# PET — Prime Exponent Tree

PET è un modello canonico per rappresentare ogni intero `N >= 2`
come un albero ricorsivo basato sulla fattorizzazione prima
e sulla struttura degli esponenti.

## Idea

Ogni intero `N >= 2` si scrive in modo unico come:

N = prod(p_i ^ e_i)

dove i `p_i` sono numeri primi distinti e gli `e_i >= 1`.

PET prende questa fattorizzazione e applica la stessa idea
ricorsivamente agli esponenti.

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

## File del progetto

- `README.md` — panoramica del progetto
- `SPEC.md` — specifica formale
- `VISION.md` — visione "filosofica"
- `pet.py` — implementazione iniziale
- `examples/` — esempi
