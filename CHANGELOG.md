# Changelog

Tutte le modifiche rilevanti di questo progetto saranno documentate qui.

Il formato si ispira a Keep a Changelog.
Versioning corrente: `0.y.z`.

## [Unreleased]

### Changed
- Nessuna modifica documentata al momento.

## [0.1.1] - 2026-03-27

### Added
- GitHub Actions CI con esecuzione automatica della test suite su Python 3.10, 3.11 e 3.12.
- Licenza MIT.
- Badge nel README per CI, release, licenza e supporto Python.
- Nuovo modulo `pet.io` per serializzazione JSON, parsing e rendering PET.

### Changed
- Metadata packaging modernizzati in `pyproject.toml`.
- Gli script esplorativi ora usano per default il dataset canonico `docs/reports/data/scan-2-1000000.jsonl`, con override da riga di comando.
- La CLI è stata spostata fuori da `core.py` nel modulo dedicato `pet.cli`.
- `core.py` è stato alleggerito separando meglio logica PET, I/O e interfaccia CLI.

### Removed
- Rimosso dal CLI il comando `shapes-growth`, esposto ma non realmente implementato nel package.

## [0.1.0] - 2026-03-27

### Added
- Prima release pubblica del progetto PET.
- CLI iniziale per encode, decode, render, validate, metrics, scan, atlas e shape-generators.
- Test suite automatizzata per core, metriche, scan, report contracts e tooling essenziale.
- Documentazione iniziale del progetto, incluse `VISION.md`, `STATUS.md`, `SPEC.md` e report bounded sotto `docs/reports/`.

### Notes
- `v0.1.0` rappresenta la prima baseline pubblica del repository prima del successivo hardening di packaging, CI e modularizzazione.

