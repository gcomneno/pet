from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, shape_generator
from tools.pathwise_one_step_probe import (
    get_subtree,
    apply_rw,
    is_locally_canonical,
    all_paths_including_root,
)
from tools.prune_absorption_check import child_generators, nearest_candidates
from tools.pathwise_first_bad_ancestor_probe import classify_pathwise_rewrite


def test_bounded_one_step_scan_has_root_failures_but_no_embedded_ancestor_yet():
    limit = 2000
    pool = [1] + sorted({shape_generator(n) for n in range(2, limit + 1)})

    failure_kinds = []

    for h in pool[1:]:
        tree0 = encode(h)

        for path in all_paths_including_root(tree0):
            node = tree0 if path == () else get_subtree(tree0, path)
            gs = child_generators(node)

            for child_idx in range(len(gs)):
                for new_g in nearest_candidates(gs, child_idx, pool):
                    if new_g <= gs[child_idx]:
                        continue

                    tree1 = apply_rw(tree0, path, child_idx, new_g)
                    local1 = tree1 if path == () else get_subtree(tree1, path)

                    if not is_locally_canonical(local1):
                        continue

                    info = classify_pathwise_rewrite(tree0, tree1, path)
                    if info["failure_kind"] is not None:
                        failure_kinds.append(info["failure_kind"])

    assert "root" in failure_kinds
    assert "embedded_ancestor" not in failure_kinds
