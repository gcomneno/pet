# PET --- Prime Exponent Tree

[![CI](https://github.com/gcomneno/pet/actions/workflows/ci.yml/badge.svg)](https://github.com/gcomneno/pet/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/gcomneno/pet)](https://github.com/gcomneno/pet/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

**PET (Prime Exponent Tree)** è un modello strutturale per rappresentare
la fattorizzazione degli interi come **alberi ricorsivi basati sugli
esponenti primi**.

L'idea centrale è separare due aspetti degli interi:

- il **valore numerico**
- la **struttura moltiplicativa**

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

```bash
pip install -e .
```

Esempi:

```bash
pet encode 72
pet metrics 256
pet query filter docs/reports/data/scan-2-1000000.jsonl --where "height=2" --limit 5
```

Generare un dataset:

```bash
pet scan 2 1000000 --jsonl docs/reports/data/scan-2-1000000.jsonl
```

------------------------------------------------------------------------

# Motivazione

La fattorizzazione prima descrive gli interi come prodotti di primi:

N = ∏ p_i^{e_i}

Nel modello PET:

- ogni **fattore primo** genera un nodo
- gli **esponenti** vengono rappresentati ricorsivamente come alberi
    PET

Questo produce una rappresentazione:

- **canonica**
- **invertibile**
- **lossless**

------------------------------------------------------------------------

# Reproducible reports and workflows

Il progetto ora tiene i risultati empirici bounded in report dedicati,
invece di lasciare nel README numeri e claim destinati a diventare stantii.

Entry point attuali:

- `docs/SPEC.md` — formato, schema, metriche e contratti di comportamento
- `docs/STATUS.md` — cosa è definito, provato, empirico o ancora aperto
- `CHANGELOG.md` — cronologia sintetica delle release pubbliche
- `docs/CLI.md` — guida pratica del command-line interface
- `docs/reports/canonical-workflow.md` — workflow canonico del PET lab: dataset, summary, report e classificazione
- `docs/reports/README.md` — indice SSOT di report, dataset e comandi di rigenerazione
- `docs/reports/artifact-policy.md` — policy attuale su artifact commitati, locali e rigenerabili
- `docs/reports/tooling-classification.md` — classificazione tra tooling stabile, secondario ed esplorativo
- `docs/reports/contributor-operator.md` — guida corta per contributor/operator del PET lab
- `docs/reports/metrics-2-10000.md` — prima baseline riproducibile delle metriche
- `docs/reports/atlas-2-100000.md` — empirical atlas report per `2..100000`
- `docs/reports/atlas-2-1000000.md` — empirical atlas report per `2..1000000`
- `docs/reports/signatures-catalog-2-1000000.md` — primo catalogo di signature strutturali
- `docs/reports/families-benchmark-disjoint.md` — benchmark su famiglie classiche disgiunte
- `docs/reports/observation-pipeline.md` — vocabolario per observation, bounded empirical pattern, conjecture ed established statement

------------------------------------------------------------------------

# Riprodurre una bounded scan

Generare un dataset JSONL:

```bash
pet scan 2 1000000 --jsonl docs/reports/data/scan-2-1000000.jsonl
```

Interrogare una scan per metriche:

```bash
pet query filter docs/reports/data/scan-2-1000000.jsonl --where "height=2" --limit 10
pet query group-count docs/reports/data/scan-2-1000000.jsonl --field branch_profile
```

Riassumere una scan in stile atlas:

```bash
python tools/atlas_summary.py docs/reports/data/scan-2-1000000.jsonl
```

Ispezionare i generatori di shape con metriche:

```bash
python3 -m src.pet.cli shape-generators docs/reports/data/scan-2-1000000.jsonl --metrics
```

Eseguire il benchmark tra famiglie classiche:

```bash
python tools/cluster_families_disjoint.py
```

------------------------------------------------------------------------

# Note

Le conclusioni forti non devono vivere nel README.

Il README deve servire soprattutto come:

- punto di ingresso rapido
- guida minima d'uso
- mappa dei documenti stabili
- accesso ai workflow riproducibili

Le osservazioni bounded, i benchmark e i cataloghi strutturali stanno nei
report dedicati sotto `docs/reports/`.

------------------------------------------------------------------------
