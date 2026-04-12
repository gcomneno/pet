import json
import subprocess
import sys


def _run_cli(*args: str) -> str:
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def test_cli_plan_bidirectional_examples():
    out1 = _run_cli("plan", "12", "75", "--max-depth", "8")
    assert "A = 12" in out1
    assert "B = 75" in out1
    assert "steps = 6" in out1
    assert "12 --NEW(p=5)--> 60" in out1
    assert "150 --DROP(p=2)--> 75" in out1

    out2 = _run_cli("plan", "75", "12", "--max-depth", "8")
    assert "A = 75" in out2
    assert "B = 12" in out2
    assert "steps = 6" in out2
    assert "75 --NEW(p=2)--> 150" in out2
    assert "4 --NEW(p=3)--> 12" in out2


def test_cli_plan_json_smoke():
    out = _run_cli("plan", "12", "245", "--max-depth", "10", "--json")
    payload = json.loads(out)

    assert payload["start"] == 12
    assert payload["target"] == 245
    assert payload["max_depth"] == 10
    assert payload["found"] is True
    assert payload["steps"] == 8
    assert payload["path"][0]["source_n"] == 12
    assert payload["path"][-1]["target_n"] == 245






def test_internal_planners_do_not_require_generators(monkeypatch):
    import pet.cli as cli

    def _boom(_n):
        raise AssertionError("shape_signature_dict should not be called by planners")

    monkeypatch.setattr(cli, "shape_signature_dict", _boom)

    path1 = cli._plan_path(12, 75, max_depth=8)
    assert path1 is not None
    assert path1[-1]["target_n"] == 75

    path2 = cli._plan_path_best_first(12, 245, max_depth=10, max_visited=50000)
    assert path2 is not None
    assert path2[-1]["target_n"] == 245

def test_cli_plan_is_deterministic():
    args = ("plan", "12", "245", "--max-depth", "10")
    outs = [_run_cli(*args) for _ in range(4)]
    assert all(out == outs[0] for out in outs[1:])

def test_cli_plan_no_path_with_tight_depth():
    out = _run_cli("plan", "12", "245", "--max-depth", "3")
    assert "A = 12" in out
    assert "B = 245" in out
    assert "NO PATH FOUND" in out

def test_internal_plan_neighbor_order_is_canonical():
    import pet.cli as cli

    rows = sorted(
        cli._plan_neighbors(12),
        key=lambda row: (cli._plan_move_rank(row["label"]), row["target_n"], row["label"]),
    )

    assert [(row["label"], row["target_n"]) for row in rows] == [
        ("NEW(p=5)", 60),
        ("DROP(p=3)", 4),
        ("INC(p=2,e=2)", 24),
        ("INC(p=3,e=1)", 36),
        ("DEC(p=2,e=2)", 6),
    ]


def test_internal_plan_path_is_stable_across_repeated_calls():
    import pet.cli as cli

    paths = [cli._plan_path(12, 245, max_depth=10) for _ in range(4)]
    assert paths[0] is not None
    assert all(path == paths[0] for path in paths[1:])


def test_cli_plan_json_path_is_stable():
    args = ("plan", "12", "245", "--max-depth", "10", "--json")
    payloads = [json.loads(_run_cli(*args)) for _ in range(4)]

    assert payloads[0]["found"] is True
    assert payloads[0]["path"]
    assert all(payload["path"] == payloads[0]["path"] for payload in payloads[1:])
