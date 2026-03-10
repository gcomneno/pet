# PET Vision

## Overview

PET, **Prime Exponent Tree**, nasce come un modo canonico e ricorsivo per rappresentare gli interi positivi `N >= 2` attraverso la loro fattorizzazione prima e la struttura interna dei loro esponenti.

L’idea centrale è semplice:
- ogni intero si fattorizza in primi
- ogni esponente viene a sua volta rappresentato con la stessa logica
- il risultato è un albero canonico
- la rappresentazione è esatta, invertibile e serializzabile

PET non vuole sostituire l’aritmetica classica.
Vuole invece offrire una **nuova prospettiva strutturale** sugli interi.

---

## Visione generale

PET può essere visto come un progetto a **tre livelli distinti**:
1. **PET-Base**
2. **PET-Metrics**
3. **PET-Algebra**

Questa separazione è importante per evitare confusione tra:
- rappresentazione canonica
- misurazione della struttura
- operazioni nuove sugli alberi

---

## 1. PET-Base
PET-Base è il nucleo rigoroso del progetto.

Qui PET è definito come:
- forma normale canonica degli interi `N >= 2`
- basata sulla fattorizzazione prima unica
- ricorsiva sugli esponenti
- invertibile tramite `decode`
- validabile
- serializzabile in JSON

### Obiettivo
Rispondere alla domanda:
> Qual è la rappresentazione PET canonica di questo intero?

### Proprietà fondamentali
- **canonicità**: un solo PET per ogni intero
- **esattezza**: il PET rappresenta esattamente il numero
- **invertibilità**: dal PET si ricostruisce l’intero
- **serializzabilità**: il PET può essere salvato e scambiato come dato strutturato

### Ruolo
PET-Base è la grammatica fondamentale del progetto.
È il livello che deve restare il più possibile stabile, semplice e rigoroso.

---

## 2. PET-Metrics
PET-Metrics studia la forma dei PET canonici.

Una volta rappresentato un intero come albero, diventa naturale chiedersi:
- quanto è profondo?
- quanto è ramificato?
- quanto è largo o stretto?
- quanto è simmetrico?
- quanto è complesso strutturalmente?

### Obiettivo
Usare PET come **lente morfologica** sugli interi.

### Esempi di metriche iniziali
- `height`
- `node_count`
- `leaf_count`
- `max_branching`
- `verticality_ratio`

### Esempi di metriche più promettenti
- profilo di ramificazione per livello
- massa esponenziale ricorsiva
- asimmetria strutturale

### Ruolo
Questo livello è il primo vero banco di prova del valore di PET.

Se le metriche PET mostrano pattern non banali, allora PET smette di essere solo una codifica elegante e diventa uno strumento per classificare e confrontare interi in modo nuovo.

---

## 3. PET-Algebra
PET-Algebra è il livello più sperimentale.

Qui non ci si limita a rappresentare o misurare alberi, ma si esplorano **operazioni strutturali** sui PET.

### Esempi di direzioni possibili
- composizione di PET
- innesto di un PET su foglie di un altro
- sostituzione di sottoalberi
- confronto strutturale
- distanze tra PET
- trasformazioni canoniche e non canoniche

### Obiettivo
Studiare i PET come oggetti matematici attivi, non solo come rappresentazioni statiche.

### Nota importante
PET-Algebra non deve alterare PET-Base.

La rappresentazione canonica di un intero deve restare separata dalle operazioni sperimentali sugli alberi.
Per questo motivo gli innesti e le composizioni non fanno parte del PET canonico di base, ma di un livello successivo.

---

## Perché PET può avere valore
PET non sembra, almeno per ora, una soluzione a un grande problema classico già noto.

Il suo valore potenziale sta altrove:
- offrire una **forma normale ricorsiva canonica**
- rendere visibile la **morfologia esponenziale** degli interi
- permettere la definizione di **invarianti strutturali**
- generare **nuove domande** sugli interi
- aprire la strada a una possibile **algebra strutturale degli alberi PET**

In questo senso, PET non è una nuova teoria dei numeri nel senso tradizionale, ma potrebbe diventare una **piattaforma per studiare la forma degli interi**.

---

## Roadmap concettuale

### Fase A — consolidare PET-Base
- definizione formale
- formato JSON canonico
- encode/decode
- validazione robusta

### Fase B — esplorare PET-Metrics
- definire metriche
- confrontare famiglie di numeri
- cercare pattern non banali

### Fase C — sperimentare PET-Algebra
- innesti
- composizioni
- distanze
- trasformazioni di alberi

---

## Conclusione
PET è una **buona infrastruttura concettuale**:
- rigorosa nel nucleo
- promettente nelle metriche
- aperta a sviluppi algebrici
