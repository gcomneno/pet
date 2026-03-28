from __future__ import annotations

import json
import subprocess
import sys



def run_pet(*args: str) -> dict:
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )
    return json.loads(out)



def test_signature_json_for_36() -> None:
    data = run_pet("signature", "36", "--json")

    assert data["n"] == 36
    assert data["generator"] == 36
    assert data["already_minimal"] is True
    assert data["child_generators"] == [2, 2]
    assert data["signature"] == [[[]], [[]]]



def test_signature_json_for_192() -> None:
    data = run_pet("signature", "192", "--json")

    assert data["n"] == 192
    assert data["generator"] == 192
    assert data["already_minimal"] is True
    assert data["child_generators"] == [6, 1]
    assert data["signature"] == [[], [[], []]]



def test_signature_json_for_7776_uses_canonical_generator() -> None:
    data = run_pet("signature", "7776", "--json")

    assert data["n"] == 7776
    assert data["generator"] == 36
    assert data["already_minimal"] is False
    assert data["child_generators"] == [2, 2]
    assert data["signature"] == [[[]], [[]]]
