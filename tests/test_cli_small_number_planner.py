from collections import deque

from pet.cli import _explain_moves


def _neighbors(n: int):
    moves = _explain_moves(n)

    new = moves.get("new")
    if new is not None:
        yield new["target_n"], f"NEW(p={new['prime']})"

    drop = moves.get("drop")
    if drop is not None:
        yield drop["target_n"], f"DROP(p={drop['representative_prime']})"

    for row in moves.get("inc", []):
        yield row["target_n"], f"INC(p={row['representative_prime']},e={row['exponent']})"

    for row in moves.get("dec", []):
        yield row["target_n"], f"DEC(p={row['representative_prime']},e={row['exponent']})"


def _bfs_path(start: int, target: int, max_depth: int):
    q = deque([(start, [])])
    seen = {start}

    while q:
        n, path = q.popleft()
        if n == target:
            return path

        if len(path) >= max_depth:
            continue

        for nxt, label in _neighbors(n):
            if nxt in seen:
                continue
            seen.add(nxt)
            q.append((nxt, path + [(n, label, nxt)]))

    return None


def _assert_path(start: int, target: int, max_depth: int, expected_steps: int):
    path = _bfs_path(start, target, max_depth=max_depth)
    assert path is not None, f"nessun cammino trovato da {start} a {target} entro depth={max_depth}"
    assert len(path) == expected_steps, (
        f"cammino inatteso da {start} a {target}: "
        f"steps={len(path)} atteso={expected_steps}"
    )

    cur = start
    for src, _label, dst in path:
        assert src == cur
        cur = dst
    assert cur == target


def test_small_planner_bidirectional_examples():
    _assert_path(12, 75, max_depth=8, expected_steps=6)
    _assert_path(75, 12, max_depth=8, expected_steps=6)
    _assert_path(12, 245, max_depth=10, expected_steps=8)
    _assert_path(245, 12, max_depth=10, expected_steps=6)
