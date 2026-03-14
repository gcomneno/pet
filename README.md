# PET --- Prime Exponent Tree

**PET (Prime Exponent Tree)** è un modello strutturale per rappresentare
la fattorizzazione degli interi come **alberi ricorsivi basati sugli
esponenti primi**.

L'idea centrale è separare due aspetti degli interi:

-   il **valore numerico**
-   la **struttura moltiplicativa**

Questo permette di studiare la **geometria strutturale della
fattorizzazione degli interi**.

------------------------------------------------------------------------

# Esempio

    12 = 2² × 3

PET(12):

    •
    ├─2
    │  •
    │  └─2
    └─3

------------------------------------------------------------------------

# Quick start

Installazione locale:

``` bash
pip install -e .
```

Esempi:

``` bash
pet encode 72
pet metrics 256
```

Generare un dataset:

``` bash
pet scan 2 1000000 --jsonl artifacts/pet_1M.jsonl
```

------------------------------------------------------------------------

# Motivazione

La fattorizzazione prima descrive gli interi come prodotti di primi:

N = ∏ p_i\^{e_i}

Nel modello PET:

-   ogni **fattore primo** genera un nodo
-   gli **esponenti** vengono rappresentati ricorsivamente come alberi
    PET

Questo produce una rappresentazione:

-   **canonica**
-   **invertibile**
-   **lossless**

------------------------------------------------------------------------

# Risultati principali

Analizzando tutti gli interi fino a 10\^6 emergono proprietà
sorprendentemente semplici.

## Numero di shape strutturali

-   interi analizzati: **999.999**
-   shape distinte: **78**

Lo spazio delle strutture moltiplicative risulta **fortemente
compresso**.

------------------------------------------------------------------------

## Shape dominanti

Le shape più frequenti osservate sono:

-   p
-   pq
-   pqr
-   pqrs
-   p²q
-   p²qr
-   p²qrs

Le **7 shape più comuni coprono circa l'87% degli interi**.

------------------------------------------------------------------------

## Profondità PET

Distribuzione osservata:

  height   percentuale
  -------- -------------
  1        60.79%
  2        34.80%
  3        4.41%
  ≥4       \~0%

Quindi:

**95.6% degli interi hanno profondità ≤ 2.**

------------------------------------------------------------------------

## Distribuzione di ω(n)

ω(n) = numero di fattori primi distinti.

  ω(n)   percentuale
  ------ -------------
  1      7.87%
  2      28.87%
  3      37.97%
  4      20.80%
  5      4.25%
  ≥6     \<1%

Il picco si trova a:

ω(n) = 3

coerente con il **teorema di Hardy--Ramanujan**.

------------------------------------------------------------------------

## Entropia strutturale

Definiamo:

H = - Σ pᵢ log(pᵢ)

Per N ≤ 10⁶:

H ≈ 2.35

Numero effettivo di shape:

exp(H) ≈ 10.5

Interpretazione:

gli interi si comportano come se esistessero **circa 10 strutture
dominanti**.

------------------------------------------------------------------------

# Crescita delle strutture

Misurazioni empiriche:

  N     H(N)
  ----- ------
  10⁴   2.18
  10⁵   2.28
  10⁶   2.35

Suggerendo la relazione:

H(N) \~ log log N

Numero di shape:

  N     shape
  ----- -----------------
  10³   \~29
  10⁴   \~63
  10⁵   \~123
  10⁶   \~230 (stimato)

Ipotesi empirica:

S(N) ≈ (log N)²

------------------------------------------------------------------------

# Collegamenti teorici

I fenomeni osservati sono compatibili con risultati noti della teoria
dei numeri probabilistica:

-   Hardy--Ramanujan theorem
-   Erdős--Kac theorem
-   Kubilius probabilistic model

Il modello PET fornisce una **rappresentazione strutturale esplicita**
di questi fenomeni.

------------------------------------------------------------------------

# Riprodurre gli esperimenti

Generare dataset:

``` bash
pet scan 2 1000000 --jsonl artifacts/pet_1M.jsonl
```

Analisi:

``` bash
python tools/shape_entropy.py artifacts/pet_1M.jsonl
python tools/height_distribution.py artifacts/pet_1M.jsonl
python tools/omega_distribution.py artifacts/pet_1M.jsonl
```

------------------------------------------------------------------------

# Struttura del progetto

    src/pet
        core.py           # rappresentazione PET
        metrics.py        # metriche strutturali
        algebra.py        # operazioni sugli alberi
        scan.py           # generazione dataset
        atlas.py          # catalogo shape
        cli.py            # interfaccia CLI

------------------------------------------------------------------------

# Paper

docs/paper/pet_paper.tex

Il paper descrive:

-   definizione formale del modello PET
-   metriche strutturali
-   analisi empirica fino a 10\^6
-   implicazioni per la teoria dei numeri probabilistica.

------------------------------------------------------------------------

# Licenza

MIT
