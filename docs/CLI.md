# PET CLI Guide

Questa guida raccoglie l'uso pratico del command-line interface di PET.

Il CLI è pensato come punto di accesso operativo per:

- encoding e decoding di interi in formato PET
- ispezione della struttura di un intero
- confronto tra strutture PET
- generazione di dataset JSONL
- interrogazione di dataset PET per metriche
- analisi bounded su dataset PET

Per la visione generale del progetto, vedere `VISION.md`.
Per lo stato epistemico del progetto, vedere `STATUS.md`.
Per il formato e i contratti del dataset, vedere `SPEC.md`.

## Installazione rapida

Installazione locale in editable mode:

```bash
pip install -e .
```

Verifica rapida:

```bash
pet --help
```

## Comandi disponibili

| Comando | Scopo |
|---|---|
| `pet encode N` | codifica un intero `N` nel formato PET |
| `pet decode FILE.json` | decodifica un PET JSON e ricostruisce l'intero |
| `pet render FILE.json` | stampa una vista ad albero leggibile del PET |
| `pet validate FILE.json` | valida un PET JSON canonico |
| `pet generator N` | stampa il più piccolo intero con la stessa shape PET di `N` |
| `pet compare N1 N2` | confronta due interi tramite distanza PET e distanza strutturale |
| `pet classify N` | classifica un intero con predicati strutturali derivati dal PET |
| `pet metrics N` | stampa le metriche strutturali canoniche |
| `pet xmetrics N` | stampa metriche estese / research |
| `pet scan START END --jsonl OUT.jsonl` | genera un dataset PET JSONL |
| `pet query ...` | filtra o raggruppa un dataset PET JSONL per metriche |
| `pet atlas DATASET.jsonl` | produce statistiche atlas-style su un dataset |
| `pet shape-generators DATASET.jsonl` | mostra i primi generatori delle shape strutturali |

## Primo percorso consigliato

Se vuoi capire PET senza perderti nei report, fai questo ordine:

1. `encode`
2. `metrics`
3. `classify`
4. `generator`
5. `compare`
6. `scan`
7. `query`
8. `atlas`

È il percorso più corto tra “ho capito il comando” e “sto già osservando struttura”.

## Esempi pratici

### 1. Codificare un intero

```bash
pet encode 72
```

Versione solo JSON:

```bash
pet encode 72 --json
```

Uso tipico:

- vedere la forma PET di un intero
- ottenere una rappresentazione serializzabile

### 2. Misurare le metriche canoniche

```bash
pet metrics 72
```

Versione JSON:

```bash
pet metrics 72 --json
```

Le metriche canoniche includono:

- `node_count`
- `leaf_count`
- `height`
- `max_branching`
- `branch_profile`
- `recursive_mass`
- `average_leaf_depth`
- `leaf_depth_variance`

### 3. Esporre metriche estese / research

```bash
pet xmetrics 72
```

Versione JSON:

```bash
pet xmetrics 72 --json
```

Questo comando aggiunge, oltre alle metriche canoniche, misure esplorative come:

- `verticality_ratio`
- `structural_asymmetry`
- `subtree_mixing_score`
- `has_root_mixed_simple_pattern`

Nota: `xmetrics` è utile per ricerca esplorativa, non solo per uso operativo minimale.

### 4. Classificare un intero

```bash
pet classify 72
```

Versione JSON:

```bash
pet classify 72 --json
```

Questo comando espone predicati strutturali già derivati dal PET, per esempio:

- `is_linear`
- `is_level_uniform`
- `is_expanding`
- `is_squarefree`
- `leaf_ratio`
- `profile_shape`

È il comando più leggibile quando vuoi una sintesi qualitativa della struttura.

### 5. Trovare il generatore minimo di una shape

```bash
pet generator 7776
pet generator 1024
pet generator 4620
```

Questo comando restituisce il più piccolo intero che ha la stessa
shape strutturale PET di `N`.

Esempi tipici:

- `7776 -> 36`
- `1024 -> 64`
- `4620 -> 4620`

È utile quando vuoi separare la taglia numerica dalla forma strutturale.

### 6. Confrontare due interi

```bash
pet compare 12 18
```

Versione JSON:

```bash
pet compare 12 18 --json
```

Output concettuale:

- `distance` misura la distanza PET completa
- `structural_distance` ignora i valori primi e confronta solo la shape
- `same_shape = true` significa shape strutturale identica

Questo è spesso il comando più utile per rispondere alla domanda:
“questi due interi sono strutturalmente uguali o solo numericamente diversi?”

### 7. Validare e renderizzare un PET JSON

Partendo da un file JSON:

```bash
pet validate sample.json
pet render sample.json
pet decode sample.json
```

Uso tipico:

- verificare che un file PET sia canonico
- visualizzarne la struttura
- ricostruire l'intero rappresentato

### 8. Generare una scan bounded

```bash
pet scan 2 10000 --jsonl docs/reports/data/scan-2-10000.jsonl
```

Questo produce un dataset JSONL con:

- `n`
- `pet`
- `metrics`
- metadata di schema / formato

Per i contratti del dataset, vedere `SPEC.md`.

### 9. Interrogare una scan con query

Dopo aver generato un dataset JSONL, puoi filtrarlo o raggrupparlo
direttamente da terminale.

Filtrare per predicati semplici:

```bash
pet query filter docs/reports/data/scan-2-10000.jsonl --where "height=2" --where "max_branching>=2" --limit 10
```

Raggruppare per una metrica:

```bash
pet query group-count docs/reports/data/scan-2-10000.jsonl --field branch_profile
```

Campi attualmente supportati:

- `height`
- `max_branching`
- `node_count`
- `recursive_mass`
- `branch_profile`
- `average_leaf_depth`
- `leaf_depth_variance`

Operatori supportati in `--where`:

- `=`
- `>=`
- `<=`

Nota pratica:

- `branch_profile` supporta solo `=`
- esempio valido: `--where "branch_profile=[2,1]"`

Trovare gli interi con la stessa shape strutturale di un dato `N`:

```bash
pet query same-shape docs/reports/data/scan-2-10000.jsonl 72
pet query same-shape docs/reports/data/scan-2-10000.jsonl 72 --limit 10
```

Questo comando confronta la shape PET ignorando i valori primi
e restituisce i record del dataset che hanno la stessa struttura di `N`.

### 10. Analizzare una scan con atlas

```bash
pet atlas docs/reports/data/scan-2-10000.jsonl
```

Questo comando serve per osservare:

- numero di shape distinte
- distribuzioni aggregate
- segnali strutturali bounded sul dataset

### 11. Ispezionare i generatori di shape

```bash
pet shape-generators docs/reports/data/scan-2-10000.jsonl --metrics
```

Questo comando stampa i primi interi che generano nuove shape strutturali
e, opzionalmente, alcune metriche associate.

## Workflow minimo da terminale

Un workflow corto ma utile può essere questo:

```bash
pet encode 72 --json
pet metrics 72
pet classify 72
pet generator 7776
pet compare 12 18
pet scan 2 10000 --jsonl docs/reports/data/scan-2-10000.jsonl
pet query filter docs/reports/data/scan-2-10000.jsonl --where "height=2" --limit 5
pet atlas docs/reports/data/scan-2-10000.jsonl
```

## Quando usare cosa

- Usa `metrics` quando vuoi misure canoniche e stabili.
- Usa `xmetrics` quando vuoi anche misure research-facing.
- Usa `classify` quando vuoi una lettura qualitativa rapida.
- Usa `generator` quando vuoi ridurre un intero al rappresentante minimo della sua shape.
- Usa `compare` quando vuoi confrontare due interi come struttura.
- Usa `scan` per generare un dataset osservabile.
- Usa `query` per cercare casi strutturali specifici dentro una scan.
- Usa `atlas` quando vuoi una vista aggregata del dataset.

## Cosa aspettarsi dal CLI

Il CLI di PET non è pensato come shell “magica”.
È un'interfaccia operativa piccola, leggibile e composabile.

Le affermazioni forti del progetto non devono vivere nel CLI:

- la parte epistemica sta in `STATUS.md`
- la parte formale sta in `SPEC.md`
- la parte empirica bounded sta nei report sotto `docs/reports/`

## Documenti collegati

- `README.md`
- `VISION.md`
- `STATUS.md`
- `SPEC.md`
- `CHANGELOG.md`
- `docs/reports/README.md`
