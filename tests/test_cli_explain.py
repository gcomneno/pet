#!/usr/bin/env python3
import json
import subprocess
import sys


def test_cli_explain_pathwise_max_nodes_text_truncates():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "explain",
            "3600",
            "--pathwise-depth",
            "2",
            "--max-nodes",
            "8",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "pathwise neighborhood (depth=2, max_nodes=8):" in result.stdout
    assert "depth 1:" in result.stdout
    assert "depth 2:" in result.stdout
    assert "  [truncated by --max-nodes]" in result.stdout


def test_cli_explain_pathwise_dot_shows_truncated_note():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "explain",
            "3600",
            "--pathwise-depth",
            "2",
            "--max-nodes",
            "8",
            "--dot",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout.startswith("digraph pet_explain {")
    assert '  truncated_note [shape=note,label="truncated by --max-nodes"];' in result.stdout


def test_cli_explain_rejects_zero_max_nodes():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "explain",
            "3600",
            "--max-nodes",
            "0",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "ERROR: --max-nodes must be >= 1" in result.stderr


def test_cli_explain_rejects_json_and_dot_together():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "explain",
            "59347",
            "--dot",
            "--json",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "ERROR: --json and --dot cannot be used together" in result.stderr

def test_cli_explain_pathwise_dot_without_truncation():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "explain",
            "59347",
            "--pathwise-depth",
            "2",
            "--dot",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout.startswith("digraph pet_explain {")
    assert "truncated_note" not in result.stdout
    assert "n_59347 [" in result.stdout
    assert "style=bold" in result.stdout
    assert "N=59347" in result.stdout
    assert 'n_59347 -> n_3491 [label="DROP(p=17)"];' in result.stdout
    assert 'n_59347 -> n_118694 [label="NEW(x2)"];' in result.stdout
    assert 'n_59347 -> n_1008899 [label="INC(p=17,e=1)"];' in result.stdout

def test_cli_explain_json():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "explain",
            "72",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)

    assert data["n"] == 72
    assert data["pathwise_depth"] == 1
    assert data["factorization_str"] == "2^3 * 3^2"
    assert data["generator"] == 36
    assert data["already_minimal"] is False
    assert data["child_generators"] == [2, 2]
    assert data["max_nodes"] is None

    assert set(data["moves"].keys()) == {"new", "drop", "inc", "dec"}
    assert data["moves"]["new"]["target_n"] == 360
    assert data["moves"]["new"]["target_generator"] == 180
    assert data["moves"]["drop"] is None
    assert [row["target_n"] for row in data["moves"]["inc"]] == [216, 144]
    assert [row["target_n"] for row in data["moves"]["dec"]] == [24, 36]

    assert data["pathwise_neighborhood"] == {"levels": [], "truncated": False}

