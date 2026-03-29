import json
import subprocess
import sys


def build_scan(tmp_path, start: int, end: int):
    jsonl_path = tmp_path / "scan.jsonl"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "scan",
            str(start),
            str(end),
            "--jsonl",
            str(jsonl_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return jsonl_path


def test_cli_query_filter_height_and_branching(tmp_path):
    jsonl_path = build_scan(tmp_path, 2, 30)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "query",
            "filter",
            str(jsonl_path),
            "--where",
            "height=2",
            "--where",
            "max_branching>=2",
            "--limit",
            "5",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = [json.loads(line) for line in result.stdout.splitlines()]
    assert [row["n"] for row in rows] == [12, 18, 20, 24, 28]


def test_cli_query_group_count_branch_profile(tmp_path):
    jsonl_path = build_scan(tmp_path, 2, 12)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "query",
            "group-count",
            str(jsonl_path),
            "--field",
            "branch_profile",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    expected = ["[1]\t5", "[1, 1]\t3", "[2]\t2", "[2, 1]\t1"]

    assert [
        " ".join(line.split()) for line in result.stdout.strip().splitlines()
    ] == [
        " ".join(line.split()) for line in expected
    ]


def test_cli_query_rejects_branch_profile_ordering_operator(tmp_path):
    jsonl_path = build_scan(tmp_path, 2, 30)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "query",
            "filter",
            str(jsonl_path),
            "--where",
            "branch_profile>=[2,1]",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "branch_profile only supports '='" in result.stderr

def test_cli_query_same_shape(tmp_path):
    jsonl_path = build_scan(tmp_path, 2, 30)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "query",
            "same-shape",
            str(jsonl_path),
            "12",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = [json.loads(line) for line in result.stdout.splitlines()]
    assert [row["n"] for row in rows] == [12, 18, 20, 24, 28]


def test_cli_query_same_shape_limit(tmp_path):
    jsonl_path = build_scan(tmp_path, 2, 30)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "query",
            "same-shape",
            str(jsonl_path),
            "12",
            "--limit",
            "3",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = [json.loads(line) for line in result.stdout.splitlines()]
    assert [row["n"] for row in rows] == [12, 18, 20]


def test_cli_query_filter_generator(tmp_path):
    jsonl_path = build_scan(tmp_path, 2, 40)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "query",
            "filter",
            str(jsonl_path),
            "--where",
            "generator=12",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = [json.loads(line) for line in result.stdout.splitlines()]
    assert [row["n"] for row in rows] == [12, 18, 20, 24, 28, 40]


def test_cli_query_group_count_generator(tmp_path):
    jsonl_path = build_scan(tmp_path, 2, 12)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "query",
            "group-count",
            str(jsonl_path),
            "--field",
            "generator",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    expected = ["2\t5", "4\t3", "6\t2", "12\t1"]

    assert [
        " ".join(line.split()) for line in result.stdout.strip().splitlines()
    ] == [
        " ".join(line.split()) for line in expected
    ]
