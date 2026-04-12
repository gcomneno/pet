import json
import subprocess
import sys


def _run_cli(*args: str) -> str:
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def test_branch_plan_human_matches_plan_exactly():
    args = ("12", "245", "--max-depth", "10")
    out_plan = _run_cli("plan", *args)
    out_branch = _run_cli("branch-plan", *args)
    assert out_branch == out_plan


def test_branch_plan_json_matches_plan_exactly():
    args = ("12", "245", "--max-depth", "10", "--json")
    payload_plan = json.loads(_run_cli("plan", *args))
    payload_branch = json.loads(_run_cli("branch-plan", *args))
    assert payload_branch == payload_plan


def test_branch_plan_is_deterministic():
    args = ("branch-plan", "12", "245", "--max-depth", "10")
    outs = [_run_cli(*args) for _ in range(4)]
    assert all(out == outs[0] for out in outs[1:])
