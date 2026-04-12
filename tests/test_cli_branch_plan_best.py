import json
import subprocess
import sys


def _run_cli(*args: str) -> str:
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def test_branch_plan_best_human_matches_plan_best_exactly():
    args = ("12", "245", "--max-depth", "10")
    out_plan = _run_cli("plan-best", *args)
    out_branch = _run_cli("branch-plan-best", *args)
    assert out_branch == out_plan


def test_branch_plan_best_json_matches_plan_best_exactly():
    args = ("12", "245", "--max-depth", "10", "--json")
    payload_plan = json.loads(_run_cli("plan-best", *args))
    payload_branch = json.loads(_run_cli("branch-plan-best", *args))
    assert payload_branch == payload_plan


def test_branch_plan_best_is_deterministic_on_large_canonical_target():
    args = (
        "branch-plan-best",
        "12",
        "174272757120000",
        "--max-depth",
        "24",
        "--max-visited",
        "50000",
    )
    outs = [_run_cli(*args) for _ in range(4)]
    assert all(out == outs[0] for out in outs[1:])
    assert "steps = 24" in outs[0]
    assert "12 --NEW(p=5)--> 60" in outs[0]
    assert "15842977920000 --INC(p=11,e=1)--> 174272757120000" in outs[0]
