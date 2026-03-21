#!/usr/bin/env python3
import subprocess
import sys


def test_cluster_families_disjoint_runs_and_prints_key_sections():
    result = subprocess.run(
        [sys.executable, "tools/cluster_families_disjoint.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout

    assert "PET — Clustering famiglie aritmetiche (DISGIUNTE)" in out
    assert "Priorità: Perfect > Primorials > Hamming > HighlyComposite" in out
    assert "SOVRAPPOSIZIONI — elementi rimossi per disgiunzione" in out
    assert "Perfect" in out
    assert "Primorials" in out
    assert "Hamming" in out
    assert "HighlyComposite" in out
    assert "Distanze INTER-famiglia — distance" in out
    assert "Distanze INTER-famiglia — structural_distance" in out
    assert "Separabilità (distance):" in out
    assert "Separabilità (structural_distance):" in out
    assert "Fine analisi." in out
