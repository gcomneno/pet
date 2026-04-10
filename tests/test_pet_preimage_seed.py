
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.partial_explain import build_partial_explain


def test_preimage_seed_separates_certified_constraints_from_hypothesis():
    from tools.pet_preimage_seed import build_seed

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=1)

    assert seed["schema"] == "pet-preimage-seed-v0"
    assert seed["source_n"] == 84739348317483740132
    assert seed["source_schedule"] == [10]

    certified = seed["certified_constraints"]
    assert certified["exact_root_anatomy"] is False
    assert certified["known_root_children"] == [[], [[]]]
    assert certified["known_root_generator_lower_bound"] == 12
    assert certified["root_generator_lower_bound"] == 420
    assert certified["residual_status"] == "composite-non-prime-power"

    hypo = seed["hypothesized_candidate"]
    assert hypo["rank"] == 1
    assert hypo["candidate_kind"] == "minimal-leaf-completion"
    assert hypo["candidate_root_generator"] == 420
    assert hypo["candidate_root_children"] == [[], [], [], [[]]]

    state = seed["seed_state"]
    assert state["start_n"] == 1
    assert state["seed_n"] == 420
    assert state["matches_candidate_root_generator"] is True
    assert state["candidate_root_generator"] == 420

    gap = seed["certified_vs_hypothesis_gap"]
    assert gap["exact_root_anatomy_certified"] is False
    assert gap["candidate_extends_known_children"] is True
    assert gap["candidate_equals_known_children"] is False
    assert gap["known_children_count"] == 2
    assert gap["candidate_children_count"] == 4
    assert gap["modeled_children_count"] == 2
    assert gap["root_generator_gap"] == 0

    policy = seed["search_policy"]
    assert policy["allowed_forward_ops"] == ["NEW", "INC"]
    assert policy["forbidden_ops"] == ["DROP", "DEC"]


def test_preimage_seed_cli_json(tmp_path):
    report = build_partial_explain(84739348317483740132, [10])
    report_path = tmp_path / "partial_explain.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, "tools/pet_preimage_seed.py", str(report_path), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)

    assert data["schema"] == "pet-preimage-seed-v0"
    assert data["hypothesized_candidate"]["candidate_kind"] == "minimal-leaf-completion"
    assert data["seed_state"]["seed_n"] == 420
    assert data["search_policy"]["allowed_forward_ops"] == ["NEW", "INC"]


def test_preimage_seed_exact_root_anatomy_case():
    from tools.pet_preimage_seed import build_seed

    data = build_partial_explain(8473934831, [10])
    seed = build_seed(data, rank=1)

    certified = seed["certified_constraints"]
    assert certified["exact_root_anatomy"] is True
    assert certified["known_root_children"] == []
    assert certified["known_root_generator_lower_bound"] == 1
    assert certified["root_generator_lower_bound"] == 2

    hypo = seed["hypothesized_candidate"]
    assert hypo["candidate_kind"] == "exact-root-anatomy"
    assert hypo["candidate_root_generator"] == 2
    assert hypo["candidate_root_children"] == [[]]

    state = seed["seed_state"]
    assert state["seed_n"] == 2
    assert state["matches_candidate_root_generator"] is True

    gap = seed["certified_vs_hypothesis_gap"]
    assert gap["exact_root_anatomy_certified"] is True
    assert gap["candidate_extends_known_children"] is True
    assert gap["candidate_equals_known_children"] is False
    assert gap["known_children_count"] == 0
    assert gap["candidate_children_count"] == 1
    assert gap["modeled_children_count"] == 1
    assert gap["root_generator_gap"] == 0

    policy = seed["search_policy"]
    assert policy["allowed_forward_ops"] == ["NEW", "INC"]
    assert policy["forbidden_ops"] == ["DROP", "DEC"]


def test_expand_seed_once_from_minimal_candidate():
    from tools.pet_preimage_seed import build_seed, expand_seed_once

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=1)
    rows = expand_seed_once(seed)

    assert [row["label"] for row in rows] == [
        "NEW(x11)",
        "INC(p=3,e=1)",
        "INC(p=2,e=2)",
    ]
    assert [row["target_n"] for row in rows] == [4620, 1260, 840]
    assert [row["op"] for row in rows] == ["NEW", "INC", "INC"]
    assert all(row["source_n"] == 420 for row in rows)


def test_preimage_seed_rank_2_prime_power_style_candidate():
    from tools.pet_preimage_seed import build_seed, expand_seed_once

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=2)

    hypo = seed["hypothesized_candidate"]
    assert hypo["rank"] == 2
    assert hypo["candidate_kind"] == "prime-power-style-completion"
    assert hypo["candidate_root_generator"] == 5040
    assert hypo["candidate_root_children"] == [[], [], [[]], [[[]]]]

    state = seed["seed_state"]
    assert state["seed_n"] == 5040
    assert state["matches_candidate_root_generator"] is True

    gap = seed["certified_vs_hypothesis_gap"]
    assert gap["exact_root_anatomy_certified"] is False
    assert gap["candidate_extends_known_children"] is True
    assert gap["candidate_equals_known_children"] is False
    assert gap["known_children_count"] == 2
    assert gap["candidate_children_count"] == 4
    assert gap["modeled_children_count"] == 2
    assert gap["root_generator_gap"] == 4620

    rows = expand_seed_once(seed)
    assert [row["label"] for row in rows] == [
        "NEW(x11)",
        "INC(p=5,e=1)",
        "INC(p=3,e=2)",
        "INC(p=2,e=4)",
    ]
    assert [row["target_n"] for row in rows] == [55440, 25200, 15120, 10080]
    assert all(row["source_n"] == 5040 for row in rows)


def test_expand_seed_layer_dedups_by_target_n():
    from tools.pet_preimage_seed import build_seed, expand_seed_layer

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=1)

    layer = expand_seed_layer([seed, seed])

    assert [row["label"] for row in layer] == [
        "NEW(x11)",
        "INC(p=3,e=1)",
        "INC(p=2,e=2)",
    ]
    assert [row["target_n"] for row in layer] == [4620, 1260, 840]
    assert [row["op"] for row in layer] == ["NEW", "INC", "INC"]

    assert all(row["source_n"] == 420 for row in layer)
    assert all(row["source_count"] == 2 for row in layer)
    assert all(row["source_ns"] == [420] for row in layer)


def test_expand_seed_layer_respects_max_target_n():
    from tools.pet_preimage_seed import build_seed, expand_seed_layer

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=1)

    layer = expand_seed_layer([seed, seed], max_target_n=2000)

    assert [row["label"] for row in layer] == [
        "INC(p=3,e=1)",
        "INC(p=2,e=2)",
    ]
    assert [row["target_n"] for row in layer] == [1260, 840]
    assert [row["op"] for row in layer] == ["INC", "INC"]
    assert all(row["source_n"] == 420 for row in layer)
    assert all(row["source_count"] == 2 for row in layer)
    assert all(row["source_ns"] == [420] for row in layer)


def test_advance_seed_from_layer_row_builds_search_node():
    from tools.pet_preimage_seed import build_seed, expand_seed_once, advance_seed

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=1)
    row = expand_seed_once(seed)[1]  # INC(p=3,e=1) -> 1260

    node = advance_seed(seed, row)

    assert node["schema"] == "pet-preimage-search-node-v0"
    assert node["source_n"] == 84739348317483740132
    assert node["root_seed_n"] == 420
    assert node["parent_n"] == 420
    assert node["current_n"] == 1260
    assert node["current_generator"] == row["target_generator"]
    assert node["depth"] == 1
    assert node["last_op"] == "INC"
    assert node["last_label"] == "INC(p=3,e=1)"
    assert node["path"] == ["INC(p=3,e=1)"]
    assert node["search_policy"]["allowed_forward_ops"] == ["NEW", "INC"]
    assert node["certified_constraints"]["root_generator_lower_bound"] == 420


def test_advance_node_builds_depth_2_search_node():
    from tools.pet_preimage_seed import (
        build_seed,
        expand_seed_once,
        advance_seed,
        expand_node_once,
        advance_node,
    )

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=1)

    row1 = expand_seed_once(seed)[1]  # INC(p=3,e=1) -> 1260
    node1 = advance_seed(seed, row1)

    rows2 = expand_node_once(node1)
    assert [row["label"] for row in rows2] == [
        "NEW(x11)",
        "INC(p=5,e=1)",
        "INC(p=2,e=2)",
    ]
    assert [row["target_n"] for row in rows2] == [13860, 6300, 2520]

    node2 = advance_node(node1, rows2[0])

    assert node2["schema"] == "pet-preimage-search-node-v0"
    assert node2["source_n"] == 84739348317483740132
    assert node2["root_seed_n"] == 420
    assert node2["parent_n"] == 1260
    assert node2["current_n"] == 13860
    assert node2["current_generator"] == rows2[0]["target_generator"]
    assert node2["depth"] == 2
    assert node2["last_op"] == "NEW"
    assert node2["last_label"] == "NEW(x11)"
    assert node2["path"] == ["INC(p=3,e=1)", "NEW(x11)"]
    assert node2["search_policy"]["allowed_forward_ops"] == ["NEW", "INC"]
    assert node2["certified_constraints"]["root_generator_lower_bound"] == 420


def test_expand_node_layer_dedups_depth_2_targets_and_respects_cap():
    from tools.pet_preimage_seed import (
        build_seed,
        expand_seed_once,
        advance_seed,
        expand_node_layer,
    )

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=1)

    row_a = expand_seed_once(seed)[0]  # NEW(x11) -> 4620
    row_b = expand_seed_once(seed)[1]  # INC(p=3,e=1) -> 1260

    node_a = advance_seed(seed, row_a)
    node_b = advance_seed(seed, row_b)

    layer = expand_node_layer([node_a, node_b], max_target_n=20000)

    assert [row["target_n"] for row in layer] == [13860, 9240, 6300, 2520]
    assert [row["op"] for row in layer] == ["INC", "INC", "INC", "INC"]

    row_13860 = layer[0]
    assert row_13860["label"] == "INC(p=3,e=1)"
    assert row_13860["source_count"] == 2
    assert row_13860["source_ns"] == [1260, 4620]

    row_6300 = next(row for row in layer if row["target_n"] == 6300)
    assert row_6300["label"] == "INC(p=5,e=1)"
    assert row_6300["source_count"] == 1
    assert row_6300["source_ns"] == [1260]


def test_expand_node_layer_keeps_parent_entries_for_deduped_targets():
    from tools.pet_preimage_seed import (
        build_seed,
        expand_seed_once,
        advance_seed,
        expand_node_layer,
    )

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=1)

    row_a = expand_seed_once(seed)[0]  # NEW(x11) -> 4620
    row_b = expand_seed_once(seed)[1]  # INC(p=3,e=1) -> 1260

    node_a = advance_seed(seed, row_a)
    node_b = advance_seed(seed, row_b)

    layer = expand_node_layer([node_a, node_b], max_target_n=20000)

    row_13860 = next(row for row in layer if row["target_n"] == 13860)

    assert row_13860["source_count"] == 2
    assert row_13860["source_ns"] == [1260, 4620]

    parent_entries = row_13860["parent_entries"]
    assert len(parent_entries) == 2

    assert parent_entries[0] == {
        "parent_n": 4620,
        "parent_depth": 1,
        "parent_path": ["NEW(x11)"],
        "via_label": "INC(p=3,e=1)",
    }
    assert parent_entries[1] == {
        "parent_n": 1260,
        "parent_depth": 1,
        "parent_path": ["INC(p=3,e=1)"],
        "via_label": "NEW(x11)",
    }


def test_advance_layer_row_uses_selected_parent_entry():
    from tools.pet_preimage_seed import (
        build_seed,
        expand_seed_once,
        advance_seed,
        expand_node_layer,
        advance_layer_row,
    )

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=1)

    row_a = expand_seed_once(seed)[0]  # NEW(x11) -> 4620
    row_b = expand_seed_once(seed)[1]  # INC(p=3,e=1) -> 1260

    node_a = advance_seed(seed, row_a)
    node_b = advance_seed(seed, row_b)

    layer = expand_node_layer([node_a, node_b], max_target_n=20000)
    row_13860 = next(row for row in layer if row["target_n"] == 13860)

    node_from_first_parent = advance_layer_row(seed, row_13860, parent_index=0)
    assert node_from_first_parent["schema"] == "pet-preimage-search-node-v0"
    assert node_from_first_parent["source_n"] == 84739348317483740132
    assert node_from_first_parent["root_seed_n"] == 420
    assert node_from_first_parent["parent_n"] == 4620
    assert node_from_first_parent["current_n"] == 13860
    assert node_from_first_parent["depth"] == 2
    assert node_from_first_parent["last_op"] == "INC"
    assert node_from_first_parent["last_label"] == "INC(p=3,e=1)"
    assert node_from_first_parent["path"] == ["NEW(x11)", "INC(p=3,e=1)"]

    node_from_second_parent = advance_layer_row(seed, row_13860, parent_index=1)
    assert node_from_second_parent["parent_n"] == 1260
    assert node_from_second_parent["current_n"] == 13860
    assert node_from_second_parent["depth"] == 2
    assert node_from_second_parent["last_op"] == "NEW"
    assert node_from_second_parent["last_label"] == "NEW(x11)"
    assert node_from_second_parent["path"] == ["INC(p=3,e=1)", "NEW(x11)"]


def test_advance_node_layer_rows_materializes_all_parent_paths():
    from tools.pet_preimage_seed import (
        build_seed,
        expand_seed_once,
        advance_seed,
        expand_node_layer,
        advance_node_layer_rows,
    )

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=1)

    row_a = expand_seed_once(seed)[0]  # NEW(x11) -> 4620
    row_b = expand_seed_once(seed)[1]  # INC(p=3,e=1) -> 1260

    node_a = advance_seed(seed, row_a)
    node_b = advance_seed(seed, row_b)

    layer = expand_node_layer([node_a, node_b], max_target_n=20000)
    nodes2 = advance_node_layer_rows(seed, layer)

    assert [node["current_n"] for node in nodes2] == [13860, 13860, 9240, 6300, 2520]
    assert [node["depth"] for node in nodes2] == [2, 2, 2, 2, 2]
    assert [node["path"] for node in nodes2] == [
        ["NEW(x11)", "INC(p=3,e=1)"],
        ["INC(p=3,e=1)", "NEW(x11)"],
        ["NEW(x11)", "INC(p=2,e=2)"],
        ["INC(p=3,e=1)", "INC(p=5,e=1)"],
        ["INC(p=3,e=1)", "INC(p=2,e=2)"],
    ]


def test_search_step_expands_and_materializes_next_frontier():
    from tools.pet_preimage_seed import (
        build_seed,
        expand_seed_once,
        advance_seed,
        search_step,
    )

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=1)

    row_a = expand_seed_once(seed)[0]  # NEW(x11) -> 4620
    row_b = expand_seed_once(seed)[1]  # INC(p=3,e=1) -> 1260

    node_a = advance_seed(seed, row_a)
    node_b = advance_seed(seed, row_b)

    nodes2 = search_step(seed, [node_a, node_b], max_target_n=20000)

    assert [node["current_n"] for node in nodes2] == [13860, 13860, 9240, 6300, 2520]
    assert [node["depth"] for node in nodes2] == [2, 2, 2, 2, 2]
    assert [node["path"] for node in nodes2] == [
        ["NEW(x11)", "INC(p=3,e=1)"],
        ["INC(p=3,e=1)", "NEW(x11)"],
        ["NEW(x11)", "INC(p=2,e=2)"],
        ["INC(p=3,e=1)", "INC(p=5,e=1)"],
        ["INC(p=3,e=1)", "INC(p=2,e=2)"],
    ]


def test_search_step_depth_3_with_cap_keeps_frontier_controlled():
    from tools.pet_preimage_seed import (
        build_seed,
        expand_seed_once,
        advance_seed,
        search_step,
    )

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=1)

    row_a = expand_seed_once(seed)[0]  # NEW(x11) -> 4620
    row_b = expand_seed_once(seed)[1]  # INC(p=3,e=1) -> 1260

    node_a = advance_seed(seed, row_a)
    node_b = advance_seed(seed, row_b)

    nodes2 = search_step(seed, [node_a, node_b], max_target_n=20000)
    nodes3 = search_step(seed, nodes2, max_target_n=50000)

    assert len(nodes3) > 0
    assert all(node["depth"] == 3 for node in nodes3)
    assert all(node["current_n"] <= 50000 for node in nodes3)
    assert all(node["path"][:2] in [
        ["NEW(x11)", "INC(p=3,e=1)"],
        ["INC(p=3,e=1)", "NEW(x11)"],
        ["NEW(x11)", "INC(p=2,e=2)"],
        ["INC(p=3,e=1)", "INC(p=5,e=1)"],
        ["INC(p=3,e=1)", "INC(p=2,e=2)"],
    ] for node in nodes3)


def test_prune_nodes_by_current_n_keeps_one_canonical_path_per_state():
    from tools.pet_preimage_seed import (
        build_seed,
        expand_seed_once,
        advance_seed,
        search_step,
        prune_nodes_by_current_n,
    )

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=1)

    row_a = expand_seed_once(seed)[0]  # NEW(x11) -> 4620
    row_b = expand_seed_once(seed)[1]  # INC(p=3,e=1) -> 1260

    node_a = advance_seed(seed, row_a)
    node_b = advance_seed(seed, row_b)

    nodes2 = search_step(seed, [node_a, node_b], max_target_n=20000)
    pruned2 = prune_nodes_by_current_n(nodes2)

    assert [node["current_n"] for node in pruned2] == [13860, 9240, 6300, 2520]
    assert [node["path"] for node in pruned2] == [
        ["INC(p=3,e=1)", "NEW(x11)"],
        ["NEW(x11)", "INC(p=2,e=2)"],
        ["INC(p=3,e=1)", "INC(p=5,e=1)"],
        ["INC(p=3,e=1)", "INC(p=2,e=2)"],
    ]


def test_search_step_pruned_removes_duplicate_current_n_without_losing_states():
    from tools.pet_preimage_seed import (
        build_seed,
        expand_seed_once,
        advance_seed,
        search_step,
        search_step_pruned,
    )

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=1)

    row_a = expand_seed_once(seed)[0]  # NEW(x11) -> 4620
    row_b = expand_seed_once(seed)[1]  # INC(p=3,e=1) -> 1260

    node_a = advance_seed(seed, row_a)
    node_b = advance_seed(seed, row_b)

    raw2 = search_step(seed, [node_a, node_b], max_target_n=20000)
    pruned2 = search_step_pruned(seed, [node_a, node_b], max_target_n=20000)

    assert len(raw2) == 5
    assert len(pruned2) == 4
    assert sorted({node["current_n"] for node in raw2}) == [2520, 6300, 9240, 13860]
    assert [node["current_n"] for node in pruned2] == [13860, 9240, 6300, 2520]


def test_search_step_pruned_respects_max_new_in_path():
    from tools.pet_preimage_seed import (
        build_seed,
        expand_seed_once,
        advance_seed,
        search_step_pruned,
    )

    data = build_partial_explain(84739348317483740132, [10])
    seed = build_seed(data, rank=1)

    row_a = expand_seed_once(seed)[0]  # NEW(x11) -> 4620
    row_b = expand_seed_once(seed)[1]  # INC(p=3,e=1) -> 1260

    frontier = [
        advance_seed(seed, row_a),
        advance_seed(seed, row_b),
    ]

    for _ in range(2, 7):
        frontier = search_step_pruned(
            seed,
            frontier,
            max_target_n=15_000_000,
            max_new_in_path=2,
        )

    assert len(frontier) == 26
    assert all(sum(1 for step in node["path"] if step.startswith("NEW(")) <= 2 for node in frontier)

    current_ns = sorted(node["current_n"] for node in frontier)
    assert 8168160 not in current_ns
    assert 12252240 not in current_ns
    assert 960960 in current_ns
    assert 12612600 in current_ns


def test_constraint_report_for_n_distinguishes_exact_and_open_same_seed():
    from tools.pet_preimage_seed import build_seed, constraint_report_for_n

    exact_data = build_partial_explain(4452484, [10])
    open_data = build_partial_explain(84739348317483740132, [10])

    exact_seed = build_seed(exact_data, rank=1)
    open_seed = build_seed(open_data, rank=1)

    r_exact_420 = constraint_report_for_n(exact_seed, 420)
    r_open_420 = constraint_report_for_n(open_seed, 420)

    assert r_exact_420["current_root_children"] == [[], [], [], [[]]]
    assert r_exact_420["known_children_covered"] is True
    assert r_exact_420["extra_children_over_known"] == 0
    assert r_exact_420["exact_root_match"] is True

    assert r_open_420["current_root_children"] == [[], [], [], [[]]]
    assert r_open_420["known_children_covered"] is True
    assert r_open_420["extra_children_over_known"] == 2
    assert r_open_420["exact_root_match"] is None

    r_exact_13860 = constraint_report_for_n(exact_seed, 13860)
    r_open_13860 = constraint_report_for_n(open_seed, 13860)

    assert r_exact_13860["current_root_children"] == [[], [], [], [[]], [[]]]
    assert r_open_13860["current_root_children"] == [[], [], [], [[]], [[]]]

    assert r_exact_13860["known_children_covered"] is True
    assert r_open_13860["known_children_covered"] is True

    assert r_exact_13860["extra_children_over_known"] == 1
    assert r_open_13860["extra_children_over_known"] == 3

    assert r_exact_13860["exact_root_match"] is False
    assert r_open_13860["exact_root_match"] is None


def test_search_step_pruned_can_require_known_children_covered():
    from tools.pet_preimage_seed import (
        build_seed,
        expand_seed_once,
        advance_seed,
        search_step_pruned,
    )

    exact_data = build_partial_explain(4452484, [10])
    open_data = build_partial_explain(84739348317483740132, [10])

    exact_seed = build_seed(exact_data, rank=1)
    open_seed = build_seed(open_data, rank=1)

    def run(seed):
        frontier = [advance_seed(seed, row) for row in expand_seed_once(seed)]
        for _ in range(2, 7):
            frontier = search_step_pruned(
                seed,
                frontier,
                max_target_n=15_000_000,
                max_new_in_path=2,
                require_known_children_covered=True,
            )
        return frontier

    exact_frontier = run(exact_seed)
    open_frontier = run(open_seed)

    assert len(exact_frontier) == 6
    assert len(open_frontier) == 19

    exact_ns = sorted(node["current_n"] for node in exact_frontier)
    open_ns = sorted(node["current_n"] for node in open_frontier)

    assert exact_ns == [221760, 332640, 1441440, 2162160, 3603600, 5405400]
    assert open_ns[:8] == [40320, 60480, 90720, 100800, 151200, 221760, 226800, 332640]
