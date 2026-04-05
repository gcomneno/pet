from tools.partial_signature_probe import build_report, refines_v0


def test_partial_pet_witness_on_2pow4_times_balanced_semiprime() -> None:
    n = 15808432

    partial = build_report(
        n,
        [2],
        allow_pollard_rho=False,
        allow_small_residual_exact=False,
    )
    truth = build_report(n, [1000, 10000, 100000])

    assert partial["exact_root_anatomy"] is False
    assert partial["known_root_children"] == [[[[]]]]
    assert partial["known_root_generator_lower_bound"] == 16
    assert partial["residual_info"]["status"] == "composite-non-prime-power"
    assert partial["root_generator_lower_bound"] == 240

    assert truth["exact_root_children"] == [[], [], [[[]]]]
    assert truth["exact_root_generator"] == 240

    assert partial["root_generator_lower_bound"] == truth["exact_root_generator"]
    assert all(
        child in truth["exact_root_children"]
        for child in partial["known_root_children"]
    )


def test_partial_pet_witness_on_2pow4_3sq_times_balanced_semiprime() -> None:
    n = 142275888

    partial = build_report(
        n,
        [3],
        allow_pollard_rho=False,
        allow_small_residual_exact=False,
    )
    truth = build_report(n, [1000, 10000, 100000])

    assert partial["exact_root_anatomy"] is False
    assert partial["known_root_children"] == [[[]], [[[]]]]
    assert partial["known_root_generator_lower_bound"] == 144
    assert partial["residual_info"]["status"] == "composite-non-prime-power"
    assert partial["root_generator_lower_bound"] == 5040

    assert truth["exact_root_children"] == [[], [], [[]], [[[]]]]
    assert truth["exact_root_generator"] == 5040

    assert partial["root_generator_lower_bound"] == truth["exact_root_generator"]
    assert all(
        child in truth["exact_root_children"]
        for child in partial["known_root_children"]
    )


def test_partial_pet_witness_on_2pow4_3sq_5sq_times_balanced_semiprime() -> None:
    n = 3556897200

    partial = build_report(
        n,
        [5],
        allow_pollard_rho=False,
        allow_small_residual_exact=False,
    )
    truth = build_report(n, [1000, 10000, 100000])

    assert partial["exact_root_anatomy"] is False
    assert partial["known_root_children"] == [[[]], [[]], [[[]]]]
    assert partial["known_root_generator_lower_bound"] == 3600
    assert partial["residual_info"]["status"] == "composite-non-prime-power"
    assert partial["root_generator_lower_bound"] == 277200

    assert truth["exact_root_children"] == [[], [], [[]], [[]], [[[]]]]
    assert truth["exact_root_generator"] == 277200

    assert partial["root_generator_lower_bound"] == truth["exact_root_generator"]
    assert all(
        child in truth["exact_root_children"]
        for child in partial["known_root_children"]
    )


def test_refines_v0_monotonicity_on_partial_pet_witnesses() -> None:
    cases = [
        (15808432, [2], [1000, 10000, 100000]),
        (142275888, [3], [1000, 10000, 100000]),
        (3556897200, [5], [1000, 10000, 100000]),
    ]

    for n, low_schedule, high_schedule in cases:
        low = build_report(
            n,
            low_schedule,
            allow_pollard_rho=False,
            allow_small_residual_exact=False,
        )
        high = build_report(
            n,
            high_schedule,
            allow_pollard_rho=False,
            allow_small_residual_exact=False,
        )

        assert refines_v0(high, low) is True
        assert refines_v0(low, high) is False
        assert refines_v0(low, low) is True
        assert refines_v0(high, high) is True


def test_refines_v0_monotonicity_across_partial_only_budgets() -> None:
    cases = [
        (15808432, [[1], [2]]),
        (142275888, [[1], [2], [3]]),
        (3556897200, [[1], [2], [3], [5]]),
    ]

    for n, schedules in cases:
        reports = [
            build_report(
                n,
                schedule,
                allow_pollard_rho=False,
                allow_small_residual_exact=False,
            )
            for schedule in schedules
        ]

        assert all(report["exact_root_anatomy"] is False for report in reports)

        for prev, curr in zip(reports, reports[1:]):
            assert refines_v0(curr, prev) is True
            assert refines_v0(prev, curr) is False


def test_refines_v0_accepts_residual_status_specialization_witness() -> None:
    n = 2 * (91 ** 2)

    b1 = build_report(
        n,
        [1],
        allow_pollard_rho=False,
        allow_small_residual_exact=False,
    )
    b2 = build_report(
        n,
        [2],
        allow_pollard_rho=False,
        allow_small_residual_exact=False,
    )
    b100 = build_report(
        n,
        [100],
        allow_pollard_rho=False,
        allow_small_residual_exact=False,
    )

    assert b1["exact_root_anatomy"] is False
    assert b1["known_root_children"] == []
    assert b1["residual_info"]["status"] == "composite-non-prime-power"
    assert b1["root_generator_lower_bound"] == 6

    assert b2["exact_root_anatomy"] is False
    assert b2["known_root_children"] == [[]]
    assert b2["known_root_generator_lower_bound"] == 2
    assert b2["residual_info"]["status"] == "perfect-power-composite-base"
    assert b2["root_generator_lower_bound"] == 30

    assert b100["exact_root_anatomy"] is True
    assert b100["exact_root_children"] == [[], [[]], [[]]]
    assert b100["exact_root_generator"] == 180

    assert refines_v0(b2, b1) is True
    assert refines_v0(b1, b2) is False
    assert refines_v0(b100, b2) is True


def test_non_exact_partial_pet_uses_only_open_residual_statuses() -> None:
    cases = [
        (15808432, [1]),
        (15808432, [2]),
        (142275888, [1]),
        (142275888, [2]),
        (142275888, [3]),
        (3556897200, [1]),
        (3556897200, [2]),
        (3556897200, [3]),
        (3556897200, [5]),
        (2 * (91 ** 2), [1]),
        (2 * (91 ** 2), [2]),
    ]

    allowed_open_statuses = {
        "composite-non-prime-power",
        "perfect-power-composite-base",
    }

    for n, schedule in cases:
        report = build_report(
            n,
            schedule,
            allow_pollard_rho=False,
            allow_small_residual_exact=False,
        )

        if report["exact_root_anatomy"] is False:
            assert report["residual_info"]["status"] in allowed_open_statuses


def test_refines_v0_monotonicity_holds_for_all_budget_pairs() -> None:
    cases = [
        (15808432, [[1], [2]]),
        (142275888, [[1], [2], [3]]),
        (3556897200, [[1], [2], [3], [5]]),
        (2 * (91 ** 2), [[1], [2], [100]]),
    ]

    for n, schedules in cases:
        reports = [
            build_report(
                n,
                schedule,
                allow_pollard_rho=False,
                allow_small_residual_exact=False,
            )
            for schedule in schedules
        ]

        for i, earlier in enumerate(reports):
            for later in reports[i + 1:]:
                assert refines_v0(later, earlier) is True
                assert refines_v0(earlier, later) is False


def test_refines_v0_witness_families_repeat_on_multiple_semiprimes() -> None:
    cases = [
        (166448, [[1], [2]]),
        (172912, [[1], [2]]),
        (1498032, [[1], [2], [3]]),
        (1556208, [[1], [2], [3]]),
        (37450800, [[1], [2], [3], [5]]),
        (38905200, [[1], [2], [3], [5]]),
    ]

    for n, schedules in cases:
        reports = [
            build_report(
                n,
                schedule,
                allow_pollard_rho=False,
                allow_small_residual_exact=False,
            )
            for schedule in schedules
        ]

        assert all(report["exact_root_anatomy"] is False for report in reports)

        for i, earlier in enumerate(reports):
            for later in reports[i + 1:]:
                assert refines_v0(later, earlier) is True
                assert refines_v0(earlier, later) is False


def test_refines_v0_r4_family_repeats_on_multiple_squared_semiprimes() -> None:
    cases = [
        (2 * (101 * 103) ** 2),
        (2 * (101 * 107) ** 2),
        (2 * (101 * 109) ** 2),
        (2 * (101 * 113) ** 2),
        (2 * (101 * 127) ** 2),
    ]

    for n in cases:
        b1 = build_report(
            n,
            [1],
            allow_pollard_rho=False,
            allow_small_residual_exact=False,
        )
        b2 = build_report(
            n,
            [2],
            allow_pollard_rho=False,
            allow_small_residual_exact=False,
        )
        b1000 = build_report(
            n,
            [1000],
            allow_pollard_rho=False,
            allow_small_residual_exact=False,
        )

        assert b1["exact_root_anatomy"] is False
        assert b1["residual_info"]["status"] == "composite-non-prime-power"

        assert b2["exact_root_anatomy"] is False
        assert b2["known_root_children"] == [[]]
        assert b2["known_root_generator_lower_bound"] == 2
        assert b2["residual_info"]["status"] == "perfect-power-composite-base"
        assert b2["root_generator_lower_bound"] == 30

        assert b1000["exact_root_anatomy"] is True
        assert b1000["exact_root_children"] == [[], [[]], [[]]]
        assert b1000["exact_root_generator"] == 180

        assert refines_v0(b2, b1) is True
        assert refines_v0(b1, b2) is False
        assert refines_v0(b1000, b2) is True
        assert refines_v0(b2, b1000) is False


def test_refines_v0_strong_gap_witness_with_nonempty_known_children() -> None:
    n = 104030

    b1 = build_report(
        n,
        [1],
        allow_pollard_rho=False,
        allow_small_residual_exact=False,
    )
    b2 = build_report(
        n,
        [2],
        allow_pollard_rho=False,
        allow_small_residual_exact=False,
    )
    b5 = build_report(
        n,
        [5],
        allow_pollard_rho=False,
        allow_small_residual_exact=False,
    )
    truth = build_report(
        n,
        [1000, 10000, 100000],
        allow_pollard_rho=False,
        allow_small_residual_exact=False,
    )

    assert b1["exact_root_anatomy"] is False
    assert b1["known_root_children"] == []
    assert b1["residual_info"]["status"] == "composite-non-prime-power"
    assert b1["root_generator_lower_bound"] == 6

    assert b2["exact_root_anatomy"] is False
    assert b2["known_root_children"] == [[]]
    assert b2["known_root_generator_lower_bound"] == 2
    assert b2["residual_info"]["status"] == "composite-non-prime-power"
    assert b2["root_generator_lower_bound"] == 30

    assert b5["exact_root_anatomy"] is False
    assert b5["known_root_children"] == [[], []]
    assert b5["known_root_generator_lower_bound"] == 6
    assert b5["residual_info"]["status"] == "composite-non-prime-power"
    assert b5["root_generator_lower_bound"] == 210

    assert truth["exact_root_anatomy"] is True
    assert truth["exact_root_children"] == [[], [], [], []]
    assert truth["exact_root_generator"] == 210

    assert b2["known_root_children"] != []
    assert b2["root_generator_lower_bound"] < truth["exact_root_generator"]

    assert refines_v0(b2, b1) is True
    assert refines_v0(b1, b2) is False
    assert refines_v0(b5, b2) is True
    assert refines_v0(b2, b5) is False
    assert refines_v0(truth, b5) is True
    assert refines_v0(b5, truth) is False

