import json
import subprocess
import sys


def _run_cli(*args: str) -> str:
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def test_cli_plan_best_bidirectional_examples():
    out1 = _run_cli("plan-best", "12", "245", "--max-depth", "10")
    assert "A = 12" in out1
    assert "B = 245" in out1
    assert "steps =" in out1
    assert "245" in out1

    out2 = _run_cli("plan-best", "245", "12", "--max-depth", "10")
    assert "A = 245" in out2
    assert "B = 12" in out2
    assert "steps =" in out2
    assert "12" in out2


def test_cli_plan_best_json_smoke():
    out = _run_cli("plan-best", "12", "75", "--max-depth", "8", "--json")
    payload = json.loads(out)

    assert payload["start"] == 12
    assert payload["target"] == 75
    assert payload["max_depth"] == 8
    assert payload["max_visited"] == 20000
    assert payload["found"] is True
    assert payload["steps"] is not None
    assert payload["path"][0]["source_n"] == 12
    assert payload["path"][-1]["target_n"] == 75




def test_cli_plan_best_reaches_large_canonical_target_minimally():
    out = _run_cli("plan-best", "12", "907200", "--max-depth", "14", "--max-visited", "50000")
    assert "A = 12" in out
    assert "B = 907200" in out
    assert "steps = 10" in out
    assert "12 --NEW(p=5)--> 60" in out
    assert "181440 --INC(p=5,e=1)--> 907200" in out



def test_cli_plan_best_reaches_canonical_large_target_very_fast_shape_free():
    out = _run_cli(
        "plan-best",
        "12",
        "174272757120000",
        "--max-depth",
        "24",
        "--max-visited",
        "50000",
    )
    assert "A = 12" in out
    assert "B = 174272757120000" in out
    assert "steps = 24" in out
    assert "12 --NEW(p=5)--> 60" in out
    assert "15842977920000 --INC(p=11,e=1)--> 174272757120000" in out

def test_cli_plan_best_is_deterministic():
    args = ("plan-best", "12", "245", "--max-depth", "10")
    outs = [_run_cli(*args) for _ in range(4)]
    assert all(out == outs[0] for out in outs[1:])

def test_internal_plan_best_path_is_stable_across_repeated_calls():
    import pet.cli as cli

    paths = [
        cli._plan_path_best_first(12, 245, max_depth=10, max_visited=50000)
        for _ in range(4)
    ]
    assert paths[0] is not None
    assert all(path == paths[0] for path in paths[1:])


def test_cli_plan_best_json_path_is_stable():
    args = ("plan-best", "12", "245", "--max-depth", "10", "--json")
    payloads = [json.loads(_run_cli(*args)) for _ in range(4)]

    assert payloads[0]["found"] is True
    assert payloads[0]["path"]
    assert all(payload["path"] == payloads[0]["path"] for payload in payloads[1:])
