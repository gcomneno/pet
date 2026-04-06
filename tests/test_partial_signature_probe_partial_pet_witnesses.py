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


def test_refines_v0_strong_gap_family_repeats_on_multiple_semiprimes() -> None:
    cases = [
        104030,
        108070,
        110090,
        114130,
        128270,
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

        assert b2["root_generator_lower_bound"] < truth["exact_root_generator"]

        assert refines_v0(b2, b1) is True
        assert refines_v0(b1, b2) is False
        assert refines_v0(b5, b2) is True
        assert refines_v0(b2, b5) is False
        assert refines_v0(truth, b5) is True
        assert refines_v0(b5, truth) is False


def test_refines_v0_long_strong_gap_witness_chain() -> None:
    n = 312090

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
    b3 = build_report(
        n,
        [3],
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
    assert b1["root_generator_lower_bound"] == 6

    assert b2["exact_root_anatomy"] is False
    assert b2["known_root_children"] == [[]]
    assert b2["known_root_generator_lower_bound"] == 2
    assert b2["residual_info"]["status"] == "composite-non-prime-power"
    assert b2["root_generator_lower_bound"] == 30

    assert b3["exact_root_anatomy"] is False
    assert b3["known_root_children"] == [[], []]
    assert b3["known_root_generator_lower_bound"] == 6
    assert b3["residual_info"]["status"] == "composite-non-prime-power"
    assert b3["root_generator_lower_bound"] == 210

    assert b5["exact_root_anatomy"] is False
    assert b5["known_root_children"] == [[], [], []]
    assert b5["known_root_generator_lower_bound"] == 30
    assert b5["residual_info"]["status"] == "composite-non-prime-power"
    assert b5["root_generator_lower_bound"] == 2310

    assert truth["exact_root_anatomy"] is True
    assert truth["exact_root_children"] == [[], [], [], [], []]
    assert truth["exact_root_generator"] == 2310

    assert b2["known_root_children"] != []
    assert b3["known_root_children"] != []
    assert b2["root_generator_lower_bound"] < truth["exact_root_generator"]
    assert b3["root_generator_lower_bound"] < truth["exact_root_generator"]
    assert b5["root_generator_lower_bound"] == truth["exact_root_generator"]

    assert refines_v0(b2, b1) is True
    assert refines_v0(b1, b2) is False
    assert refines_v0(b3, b2) is True
    assert refines_v0(b2, b3) is False
    assert refines_v0(b5, b3) is True
    assert refines_v0(b3, b5) is False
    assert refines_v0(truth, b5) is True
    assert refines_v0(b5, truth) is False


def test_refines_v0_long_strong_gap_family_repeats_on_multiple_semiprimes() -> None:
    cases = [
        312090,
        324210,
        330270,
        342390,
        392430,
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
        b3 = build_report(
            n,
            [3],
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
        assert b1["root_generator_lower_bound"] == 6

        assert b2["exact_root_anatomy"] is False
        assert b2["known_root_children"] == [[]]
        assert b2["known_root_generator_lower_bound"] == 2
        assert b2["residual_info"]["status"] == "composite-non-prime-power"
        assert b2["root_generator_lower_bound"] == 30

        assert b3["exact_root_anatomy"] is False
        assert b3["known_root_children"] == [[], []]
        assert b3["known_root_generator_lower_bound"] == 6
        assert b3["residual_info"]["status"] == "composite-non-prime-power"
        assert b3["root_generator_lower_bound"] == 210

        assert b5["exact_root_anatomy"] is False
        assert b5["known_root_children"] == [[], [], []]
        assert b5["known_root_generator_lower_bound"] == 30
        assert b5["residual_info"]["status"] == "composite-non-prime-power"
        assert b5["root_generator_lower_bound"] == 2310

        assert truth["exact_root_anatomy"] is True
        assert truth["exact_root_children"] == [[], [], [], [], []]
        assert truth["exact_root_generator"] == 2310

        assert b2["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert b3["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert b5["root_generator_lower_bound"] == truth["exact_root_generator"]

        assert refines_v0(b2, b1) is True
        assert refines_v0(b1, b2) is False
        assert refines_v0(b3, b2) is True
        assert refines_v0(b2, b3) is False
        assert refines_v0(b5, b3) is True
        assert refines_v0(b3, b5) is False
        assert refines_v0(truth, b5) is True
        assert refines_v0(b5, truth) is False


def test_refines_v0_long_strong_gap_pattern_extends_across_squarefree_triples() -> None:
    cases = [
        (312090, [2], [3], [5]),
        (436926, [2], [3], [7]),
        (686598, [2], [3], [11]),
        (728210, [2], [5], [7]),
        (1144330, [2], [5], [11]),
        (1602062, [2], [7], [11]),
        (1092315, [3], [5], [7]),
        (1716495, [3], [5], [11]),
        (2403093, [3], [7], [11]),
        (4005155, [5], [7], [11]),
    ]

    for n, s1, s2, s3 in cases:
        b1 = build_report(
            n,
            [1],
            allow_pollard_rho=False,
            allow_small_residual_exact=False,
        )
        p1 = build_report(
            n,
            s1,
            allow_pollard_rho=False,
            allow_small_residual_exact=False,
        )
        p2 = build_report(
            n,
            s2,
            allow_pollard_rho=False,
            allow_small_residual_exact=False,
        )
        p3 = build_report(
            n,
            s3,
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
        assert b1["root_generator_lower_bound"] == 6

        assert p1["exact_root_anatomy"] is False
        assert p1["known_root_children"] == [[]]
        assert p1["known_root_generator_lower_bound"] == 2
        assert p1["residual_info"]["status"] == "composite-non-prime-power"
        assert p1["root_generator_lower_bound"] == 30

        assert p2["exact_root_anatomy"] is False
        assert p2["known_root_children"] == [[], []]
        assert p2["known_root_generator_lower_bound"] == 6
        assert p2["residual_info"]["status"] == "composite-non-prime-power"
        assert p2["root_generator_lower_bound"] == 210

        assert p3["exact_root_anatomy"] is False
        assert p3["known_root_children"] == [[], [], []]
        assert p3["known_root_generator_lower_bound"] == 30
        assert p3["residual_info"]["status"] == "composite-non-prime-power"
        assert p3["root_generator_lower_bound"] == 2310

        assert truth["exact_root_anatomy"] is True
        assert truth["exact_root_children"] == [[], [], [], [], []]
        assert truth["exact_root_generator"] == 2310

        assert p1["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p2["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p3["root_generator_lower_bound"] == truth["exact_root_generator"]

        assert refines_v0(p1, b1) is True
        assert refines_v0(b1, p1) is False
        assert refines_v0(p2, p1) is True
        assert refines_v0(p1, p2) is False
        assert refines_v0(p3, p2) is True
        assert refines_v0(p2, p3) is False
        assert refines_v0(truth, p3) is True
        assert refines_v0(p3, truth) is False



def test_refines_v0_long_strong_gap_pattern_persists_across_squarefree_triples_and_semiprime_tails() -> None:
    from contextlib import redirect_stdout
    from io import StringIO
    from itertools import combinations

    def quiet_build(n: int, schedule: list[int]):
        buf = StringIO()
        with redirect_stdout(buf):
            return build_report(
                n,
                schedule,
                allow_pollard_rho=False,
                allow_small_residual_exact=False,
            )

    bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    tails = [(101, 103), (107, 109), (127, 131), (137, 139)]

    for a, b, c in combinations(bases, 3):
        for p, q in tails:
            n = a * b * c * p * q

            b1 = quiet_build(n, [1])
            p1 = quiet_build(n, [a])
            p2 = quiet_build(n, [b])
            p3 = quiet_build(n, [c])
            truth = quiet_build(n, [1000, 10000, 100000])

            assert b1["exact_root_anatomy"] is False
            assert b1["known_root_children"] == []
            assert b1["root_generator_lower_bound"] == 6

            assert p1["exact_root_anatomy"] is False
            assert p1["known_root_children"] == [[]]
            assert p1["known_root_generator_lower_bound"] == 2
            assert p1["residual_info"]["status"] == "composite-non-prime-power"
            assert p1["root_generator_lower_bound"] == 30

            assert p2["exact_root_anatomy"] is False
            assert p2["known_root_children"] == [[], []]
            assert p2["known_root_generator_lower_bound"] == 6
            assert p2["residual_info"]["status"] == "composite-non-prime-power"
            assert p2["root_generator_lower_bound"] == 210

            assert p3["exact_root_anatomy"] is False
            assert p3["known_root_children"] == [[], [], []]
            assert p3["known_root_generator_lower_bound"] == 30
            assert p3["residual_info"]["status"] == "composite-non-prime-power"
            assert p3["root_generator_lower_bound"] == 2310

            assert truth["exact_root_anatomy"] is True
            assert truth["exact_root_children"] == [[], [], [], [], []]
            assert truth["exact_root_generator"] == 2310

            assert p1["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p2["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p3["root_generator_lower_bound"] == truth["exact_root_generator"]

            assert refines_v0(p1, b1) is True
            assert refines_v0(b1, p1) is False
            assert refines_v0(p2, p1) is True
            assert refines_v0(p1, p2) is False
            assert refines_v0(p3, p2) is True
            assert refines_v0(p2, p3) is False
            assert refines_v0(truth, p3) is True
            assert refines_v0(p3, truth) is False


def test_refines_v0_four_step_long_strong_gap_pattern_persists_across_squarefree_quadruples_and_semiprime_tails() -> None:
    from contextlib import redirect_stdout
    from io import StringIO
    from itertools import combinations

    def quiet_build(n: int, schedule: list[int]):
        buf = StringIO()
        with redirect_stdout(buf):
            return build_report(
                n,
                schedule,
                allow_pollard_rho=False,
                allow_small_residual_exact=False,
            )

    bases = [2, 3, 5, 7, 11, 13, 17]
    tails = [(101, 103), (107, 109), (127, 131), (137, 139)]

    for a, b, c, d in combinations(bases, 4):
        for p, q in tails:
            n = a * b * c * d * p * q

            b1 = quiet_build(n, [1])
            p1 = quiet_build(n, [a])
            p2 = quiet_build(n, [b])
            p3 = quiet_build(n, [c])
            p4 = quiet_build(n, [d])
            truth = quiet_build(n, [1000, 10000, 100000])

            assert b1["exact_root_anatomy"] is False
            assert b1["known_root_children"] == []
            assert b1["root_generator_lower_bound"] == 6

            assert p1["exact_root_anatomy"] is False
            assert p1["known_root_children"] == [[]]
            assert p1["known_root_generator_lower_bound"] == 2
            assert p1["residual_info"]["status"] == "composite-non-prime-power"
            assert p1["root_generator_lower_bound"] == 30

            assert p2["exact_root_anatomy"] is False
            assert p2["known_root_children"] == [[], []]
            assert p2["known_root_generator_lower_bound"] == 6
            assert p2["residual_info"]["status"] == "composite-non-prime-power"
            assert p2["root_generator_lower_bound"] == 210

            assert p3["exact_root_anatomy"] is False
            assert p3["known_root_children"] == [[], [], []]
            assert p3["known_root_generator_lower_bound"] == 30
            assert p3["residual_info"]["status"] == "composite-non-prime-power"
            assert p3["root_generator_lower_bound"] == 2310

            assert p4["exact_root_anatomy"] is False
            assert p4["known_root_children"] == [[], [], [], []]
            assert p4["known_root_generator_lower_bound"] == 210
            assert p4["residual_info"]["status"] == "composite-non-prime-power"
            assert p4["root_generator_lower_bound"] == 30030

            assert truth["exact_root_anatomy"] is True
            assert truth["exact_root_children"] == [[], [], [], [], [], []]
            assert truth["exact_root_generator"] == 30030

            assert p1["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p2["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p3["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p4["root_generator_lower_bound"] == truth["exact_root_generator"]

            assert refines_v0(p1, b1) is True
            assert refines_v0(b1, p1) is False
            assert refines_v0(p2, p1) is True
            assert refines_v0(p1, p2) is False
            assert refines_v0(p3, p2) is True
            assert refines_v0(p2, p3) is False
            assert refines_v0(p4, p3) is True
            assert refines_v0(p3, p4) is False
            assert refines_v0(truth, p4) is True
            assert refines_v0(p4, truth) is False


def test_refines_v0_five_step_long_strong_gap_pattern_persists_across_squarefree_quintuples_and_semiprime_tails() -> None:
    from contextlib import redirect_stdout
    from io import StringIO
    from itertools import combinations

    def quiet_build(n: int, schedule: list[int]):
        buf = StringIO()
        with redirect_stdout(buf):
            return build_report(
                n,
                schedule,
                allow_pollard_rho=False,
                allow_small_residual_exact=False,
            )

    bases = [2, 3, 5, 7, 11, 13, 17]
    tails = [(101, 103), (107, 109), (127, 131), (137, 139)]

    for a, b, c, d, e in combinations(bases, 5):
        for p, q in tails:
            n = a * b * c * d * e * p * q

            b1 = quiet_build(n, [1])
            p1 = quiet_build(n, [a])
            p2 = quiet_build(n, [b])
            p3 = quiet_build(n, [c])
            p4 = quiet_build(n, [d])
            p5 = quiet_build(n, [e])
            truth = quiet_build(n, [1000, 10000, 100000])

            assert b1["exact_root_anatomy"] is False
            assert b1["known_root_children"] == []
            assert b1["root_generator_lower_bound"] == 6

            assert p1["exact_root_anatomy"] is False
            assert p1["known_root_children"] == [[]]
            assert p1["known_root_generator_lower_bound"] == 2
            assert p1["residual_info"]["status"] == "composite-non-prime-power"
            assert p1["root_generator_lower_bound"] == 30

            assert p2["exact_root_anatomy"] is False
            assert p2["known_root_children"] == [[], []]
            assert p2["known_root_generator_lower_bound"] == 6
            assert p2["residual_info"]["status"] == "composite-non-prime-power"
            assert p2["root_generator_lower_bound"] == 210

            assert p3["exact_root_anatomy"] is False
            assert p3["known_root_children"] == [[], [], []]
            assert p3["known_root_generator_lower_bound"] == 30
            assert p3["residual_info"]["status"] == "composite-non-prime-power"
            assert p3["root_generator_lower_bound"] == 2310

            assert p4["exact_root_anatomy"] is False
            assert p4["known_root_children"] == [[], [], [], []]
            assert p4["known_root_generator_lower_bound"] == 210
            assert p4["residual_info"]["status"] == "composite-non-prime-power"
            assert p4["root_generator_lower_bound"] == 30030

            assert p5["exact_root_anatomy"] is False
            assert p5["known_root_children"] == [[], [], [], [], []]
            assert p5["known_root_generator_lower_bound"] == 2310
            assert p5["residual_info"]["status"] == "composite-non-prime-power"
            assert p5["root_generator_lower_bound"] == 510510

            assert truth["exact_root_anatomy"] is True
            assert truth["exact_root_children"] == [[], [], [], [], [], [], []]
            assert truth["exact_root_generator"] == 510510

            assert p1["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p2["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p3["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p4["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p5["root_generator_lower_bound"] == truth["exact_root_generator"]

            assert refines_v0(p1, b1) is True
            assert refines_v0(b1, p1) is False
            assert refines_v0(p2, p1) is True
            assert refines_v0(p1, p2) is False
            assert refines_v0(p3, p2) is True
            assert refines_v0(p2, p3) is False
            assert refines_v0(p4, p3) is True
            assert refines_v0(p3, p4) is False
            assert refines_v0(p5, p4) is True
            assert refines_v0(p4, p5) is False
            assert refines_v0(truth, p5) is True
            assert refines_v0(p5, truth) is False


def test_refines_v0_six_step_long_strong_gap_pattern_persists_across_squarefree_sextuples_and_semiprime_tails() -> None:
    from contextlib import redirect_stdout
    from io import StringIO
    from itertools import combinations

    def quiet_build(n: int, schedule: list[int]):
        buf = StringIO()
        with redirect_stdout(buf):
            return build_report(
                n,
                schedule,
                allow_pollard_rho=False,
                allow_small_residual_exact=False,
            )

    bases = [2, 3, 5, 7, 11, 13, 17]
    tails = [(19, 23), (19, 29), (23, 29), (23, 31)]

    for a, b, c, d, e, f in combinations(bases, 6):
        for p, q in tails:
            n = a * b * c * d * e * f * p * q

            b1 = quiet_build(n, [1])
            p1 = quiet_build(n, [a])
            p2 = quiet_build(n, [b])
            p3 = quiet_build(n, [c])
            p4 = quiet_build(n, [d])
            p5 = quiet_build(n, [e])
            p6 = quiet_build(n, [f])
            truth = quiet_build(n, [1000, 10000, 100000])

            assert b1["exact_root_anatomy"] is False
            assert b1["known_root_children"] == []
            assert b1["root_generator_lower_bound"] == 6

            assert p1["exact_root_anatomy"] is False
            assert p1["known_root_children"] == [[]]
            assert p1["known_root_generator_lower_bound"] == 2
            assert p1["residual_info"]["status"] == "composite-non-prime-power"
            assert p1["root_generator_lower_bound"] == 30

            assert p2["exact_root_anatomy"] is False
            assert p2["known_root_children"] == [[], []]
            assert p2["known_root_generator_lower_bound"] == 6
            assert p2["residual_info"]["status"] == "composite-non-prime-power"
            assert p2["root_generator_lower_bound"] == 210

            assert p3["exact_root_anatomy"] is False
            assert p3["known_root_children"] == [[], [], []]
            assert p3["known_root_generator_lower_bound"] == 30
            assert p3["residual_info"]["status"] == "composite-non-prime-power"
            assert p3["root_generator_lower_bound"] == 2310

            assert p4["exact_root_anatomy"] is False
            assert p4["known_root_children"] == [[], [], [], []]
            assert p4["known_root_generator_lower_bound"] == 210
            assert p4["residual_info"]["status"] == "composite-non-prime-power"
            assert p4["root_generator_lower_bound"] == 30030

            assert p5["exact_root_anatomy"] is False
            assert p5["known_root_children"] == [[], [], [], [], []]
            assert p5["known_root_generator_lower_bound"] == 2310
            assert p5["residual_info"]["status"] == "composite-non-prime-power"
            assert p5["root_generator_lower_bound"] == 510510

            assert p6["exact_root_anatomy"] is False
            assert p6["known_root_children"] == [[], [], [], [], [], []]
            assert p6["known_root_generator_lower_bound"] == 30030
            assert p6["residual_info"]["status"] == "composite-non-prime-power"
            assert p6["root_generator_lower_bound"] == 9699690

            assert truth["exact_root_anatomy"] is True
            assert truth["exact_root_children"] == [[], [], [], [], [], [], [], []]
            assert truth["exact_root_generator"] == 9699690

            assert p1["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p2["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p3["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p4["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p5["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p6["root_generator_lower_bound"] == truth["exact_root_generator"]

            assert refines_v0(p1, b1) is True
            assert refines_v0(b1, p1) is False
            assert refines_v0(p2, p1) is True
            assert refines_v0(p1, p2) is False
            assert refines_v0(p3, p2) is True
            assert refines_v0(p2, p3) is False
            assert refines_v0(p4, p3) is True
            assert refines_v0(p3, p4) is False
            assert refines_v0(p5, p4) is True
            assert refines_v0(p4, p5) is False
            assert refines_v0(p6, p5) is True
            assert refines_v0(p5, p6) is False
            assert refines_v0(truth, p6) is True
            assert refines_v0(p6, truth) is False


def test_refines_v0_seven_step_long_strong_gap_pattern_persists_across_squarefree_septuples_and_semiprime_tails() -> None:
    from contextlib import redirect_stdout
    from io import StringIO
    from itertools import combinations

    def quiet_build(n: int, schedule: list[int]):
        buf = StringIO()
        with redirect_stdout(buf):
            return build_report(
                n,
                schedule,
                allow_pollard_rho=False,
                allow_small_residual_exact=False,
            )

    bases = [2, 3, 5, 7, 11, 13, 17, 19]
    tails = [(23, 29), (23, 31), (29, 31)]

    for a, b, c, d, e, f, g in combinations(bases, 7):
        for p, q in tails:
            n = a * b * c * d * e * f * g * p * q

            b1 = quiet_build(n, [1])
            p1 = quiet_build(n, [a])
            p2 = quiet_build(n, [b])
            p3 = quiet_build(n, [c])
            p4 = quiet_build(n, [d])
            p5 = quiet_build(n, [e])
            p6 = quiet_build(n, [f])
            p7 = quiet_build(n, [g])
            truth = quiet_build(n, [1000, 10000, 100000])

            assert b1["exact_root_anatomy"] is False
            assert b1["known_root_children"] == []
            assert b1["root_generator_lower_bound"] == 6

            assert p1["exact_root_anatomy"] is False
            assert p1["known_root_children"] == [[]]
            assert p1["known_root_generator_lower_bound"] == 2
            assert p1["residual_info"]["status"] == "composite-non-prime-power"
            assert p1["root_generator_lower_bound"] == 30

            assert p2["exact_root_anatomy"] is False
            assert p2["known_root_children"] == [[], []]
            assert p2["known_root_generator_lower_bound"] == 6
            assert p2["residual_info"]["status"] == "composite-non-prime-power"
            assert p2["root_generator_lower_bound"] == 210

            assert p3["exact_root_anatomy"] is False
            assert p3["known_root_children"] == [[], [], []]
            assert p3["known_root_generator_lower_bound"] == 30
            assert p3["residual_info"]["status"] == "composite-non-prime-power"
            assert p3["root_generator_lower_bound"] == 2310

            assert p4["exact_root_anatomy"] is False
            assert p4["known_root_children"] == [[], [], [], []]
            assert p4["known_root_generator_lower_bound"] == 210
            assert p4["residual_info"]["status"] == "composite-non-prime-power"
            assert p4["root_generator_lower_bound"] == 30030

            assert p5["exact_root_anatomy"] is False
            assert p5["known_root_children"] == [[], [], [], [], []]
            assert p5["known_root_generator_lower_bound"] == 2310
            assert p5["residual_info"]["status"] == "composite-non-prime-power"
            assert p5["root_generator_lower_bound"] == 510510

            assert p6["exact_root_anatomy"] is False
            assert p6["known_root_children"] == [[], [], [], [], [], []]
            assert p6["known_root_generator_lower_bound"] == 30030
            assert p6["residual_info"]["status"] == "composite-non-prime-power"
            assert p6["root_generator_lower_bound"] == 9699690

            assert p7["exact_root_anatomy"] is False
            assert p7["known_root_children"] == [[], [], [], [], [], [], []]
            assert p7["known_root_generator_lower_bound"] == 510510
            assert p7["residual_info"]["status"] == "composite-non-prime-power"
            assert p7["root_generator_lower_bound"] == 223092870

            assert truth["exact_root_anatomy"] is True
            assert truth["exact_root_children"] == [[], [], [], [], [], [], [], [], []]
            assert truth["exact_root_generator"] == 223092870

            assert p1["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p2["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p3["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p4["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p5["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p6["root_generator_lower_bound"] < truth["exact_root_generator"]
            assert p7["root_generator_lower_bound"] == truth["exact_root_generator"]

            assert refines_v0(p1, b1) is True
            assert refines_v0(b1, p1) is False
            assert refines_v0(p2, p1) is True
            assert refines_v0(p1, p2) is False
            assert refines_v0(p3, p2) is True
            assert refines_v0(p2, p3) is False
            assert refines_v0(p4, p3) is True
            assert refines_v0(p3, p4) is False
            assert refines_v0(p5, p4) is True
            assert refines_v0(p4, p5) is False
            assert refines_v0(p6, p5) is True
            assert refines_v0(p5, p6) is False
            assert refines_v0(p7, p6) is True
            assert refines_v0(p6, p7) is False
            assert refines_v0(truth, p7) is True
            assert refines_v0(p7, truth) is False


def test_refines_v0_eight_step_long_strong_gap_pattern_holds_for_fixed_octuple_and_semiprime_tails() -> None:
    from contextlib import redirect_stdout
    from io import StringIO

    def quiet_build(n: int, schedule: list[int]):
        buf = StringIO()
        with redirect_stdout(buf):
            return build_report(
                n,
                schedule,
                allow_pollard_rho=False,
                allow_small_residual_exact=False,
            )

    a, b, c, d, e, f, g, h = [2, 3, 5, 7, 11, 13, 17, 19]
    tails = [(23, 29), (23, 31), (29, 31)]

    for p, q in tails:
        n = a * b * c * d * e * f * g * h * p * q

        b1 = quiet_build(n, [1])
        p1 = quiet_build(n, [a])
        p2 = quiet_build(n, [b])
        p3 = quiet_build(n, [c])
        p4 = quiet_build(n, [d])
        p5 = quiet_build(n, [e])
        p6 = quiet_build(n, [f])
        p7 = quiet_build(n, [g])
        p8 = quiet_build(n, [h])
        truth = quiet_build(n, [1000, 10000, 100000])

        assert b1["exact_root_anatomy"] is False
        assert b1["known_root_children"] == []
        assert b1["root_generator_lower_bound"] == 6

        assert p1["exact_root_anatomy"] is False
        assert p1["known_root_children"] == [[]]
        assert p1["known_root_generator_lower_bound"] == 2
        assert p1["residual_info"]["status"] == "composite-non-prime-power"
        assert p1["root_generator_lower_bound"] == 30

        assert p2["exact_root_anatomy"] is False
        assert p2["known_root_children"] == [[], []]
        assert p2["known_root_generator_lower_bound"] == 6
        assert p2["residual_info"]["status"] == "composite-non-prime-power"
        assert p2["root_generator_lower_bound"] == 210

        assert p3["exact_root_anatomy"] is False
        assert p3["known_root_children"] == [[], [], []]
        assert p3["known_root_generator_lower_bound"] == 30
        assert p3["residual_info"]["status"] == "composite-non-prime-power"
        assert p3["root_generator_lower_bound"] == 2310

        assert p4["exact_root_anatomy"] is False
        assert p4["known_root_children"] == [[], [], [], []]
        assert p4["known_root_generator_lower_bound"] == 210
        assert p4["residual_info"]["status"] == "composite-non-prime-power"
        assert p4["root_generator_lower_bound"] == 30030

        assert p5["exact_root_anatomy"] is False
        assert p5["known_root_children"] == [[], [], [], [], []]
        assert p5["known_root_generator_lower_bound"] == 2310
        assert p5["residual_info"]["status"] == "composite-non-prime-power"
        assert p5["root_generator_lower_bound"] == 510510

        assert p6["exact_root_anatomy"] is False
        assert p6["known_root_children"] == [[], [], [], [], [], []]
        assert p6["known_root_generator_lower_bound"] == 30030
        assert p6["residual_info"]["status"] == "composite-non-prime-power"
        assert p6["root_generator_lower_bound"] == 9699690

        assert p7["exact_root_anatomy"] is False
        assert p7["known_root_children"] == [[], [], [], [], [], [], []]
        assert p7["known_root_generator_lower_bound"] == 510510
        assert p7["residual_info"]["status"] == "composite-non-prime-power"
        assert p7["root_generator_lower_bound"] == 223092870

        assert p8["exact_root_anatomy"] is False
        assert p8["known_root_children"] == [[], [], [], [], [], [], [], []]
        assert p8["known_root_generator_lower_bound"] == 9699690
        assert p8["residual_info"]["status"] == "composite-non-prime-power"
        assert p8["root_generator_lower_bound"] == 6469693230

        assert truth["exact_root_anatomy"] is True
        assert truth["exact_root_children"] == [[], [], [], [], [], [], [], [], [], []]
        assert truth["exact_root_generator"] == 6469693230

        assert p1["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p2["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p3["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p4["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p5["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p6["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p7["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p8["root_generator_lower_bound"] == truth["exact_root_generator"]

        assert refines_v0(p1, b1) is True
        assert refines_v0(b1, p1) is False
        assert refines_v0(p2, p1) is True
        assert refines_v0(p1, p2) is False
        assert refines_v0(p3, p2) is True
        assert refines_v0(p2, p3) is False
        assert refines_v0(p4, p3) is True
        assert refines_v0(p3, p4) is False
        assert refines_v0(p5, p4) is True
        assert refines_v0(p4, p5) is False
        assert refines_v0(p6, p5) is True
        assert refines_v0(p5, p6) is False
        assert refines_v0(p7, p6) is True
        assert refines_v0(p6, p7) is False
        assert refines_v0(p8, p7) is True
        assert refines_v0(p7, p8) is False
        assert refines_v0(truth, p8) is True
        assert refines_v0(p8, truth) is False


def test_refines_v0_nine_step_long_strong_gap_pattern_holds_for_fixed_nonuple_and_semiprime_tails() -> None:
    from contextlib import redirect_stdout
    from io import StringIO

    def quiet_build(n: int, schedule: list[int]):
        buf = StringIO()
        with redirect_stdout(buf):
            return build_report(
                n,
                schedule,
                allow_pollard_rho=False,
                allow_small_residual_exact=False,
            )

    a, b, c, d, e, f, g, h, i = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    tails = [(29, 31), (29, 37), (31, 37)]

    for p, q in tails:
        n = a * b * c * d * e * f * g * h * i * p * q

        b1 = quiet_build(n, [1])
        p1 = quiet_build(n, [a])
        p2 = quiet_build(n, [b])
        p3 = quiet_build(n, [c])
        p4 = quiet_build(n, [d])
        p5 = quiet_build(n, [e])
        p6 = quiet_build(n, [f])
        p7 = quiet_build(n, [g])
        p8 = quiet_build(n, [h])
        p9 = quiet_build(n, [i])
        truth = quiet_build(n, [1000, 10000, 100000])

        assert b1["exact_root_anatomy"] is False
        assert b1["known_root_children"] == []
        assert b1["root_generator_lower_bound"] == 6

        assert p1["exact_root_anatomy"] is False
        assert p1["known_root_children"] == [[]]
        assert p1["known_root_generator_lower_bound"] == 2
        assert p1["residual_info"]["status"] == "composite-non-prime-power"
        assert p1["root_generator_lower_bound"] == 30

        assert p2["exact_root_anatomy"] is False
        assert p2["known_root_children"] == [[], []]
        assert p2["known_root_generator_lower_bound"] == 6
        assert p2["residual_info"]["status"] == "composite-non-prime-power"
        assert p2["root_generator_lower_bound"] == 210

        assert p3["exact_root_anatomy"] is False
        assert p3["known_root_children"] == [[], [], []]
        assert p3["known_root_generator_lower_bound"] == 30
        assert p3["residual_info"]["status"] == "composite-non-prime-power"
        assert p3["root_generator_lower_bound"] == 2310

        assert p4["exact_root_anatomy"] is False
        assert p4["known_root_children"] == [[], [], [], []]
        assert p4["known_root_generator_lower_bound"] == 210
        assert p4["residual_info"]["status"] == "composite-non-prime-power"
        assert p4["root_generator_lower_bound"] == 30030

        assert p5["exact_root_anatomy"] is False
        assert p5["known_root_children"] == [[], [], [], [], []]
        assert p5["known_root_generator_lower_bound"] == 2310
        assert p5["residual_info"]["status"] == "composite-non-prime-power"
        assert p5["root_generator_lower_bound"] == 510510

        assert p6["exact_root_anatomy"] is False
        assert p6["known_root_children"] == [[], [], [], [], [], []]
        assert p6["known_root_generator_lower_bound"] == 30030
        assert p6["residual_info"]["status"] == "composite-non-prime-power"
        assert p6["root_generator_lower_bound"] == 9699690

        assert p7["exact_root_anatomy"] is False
        assert p7["known_root_children"] == [[], [], [], [], [], [], []]
        assert p7["known_root_generator_lower_bound"] == 510510
        assert p7["residual_info"]["status"] == "composite-non-prime-power"
        assert p7["root_generator_lower_bound"] == 223092870

        assert p8["exact_root_anatomy"] is False
        assert p8["known_root_children"] == [[], [], [], [], [], [], [], []]
        assert p8["known_root_generator_lower_bound"] == 9699690
        assert p8["residual_info"]["status"] == "composite-non-prime-power"
        assert p8["root_generator_lower_bound"] == 6469693230

        assert p9["exact_root_anatomy"] is False
        assert p9["known_root_children"] == [[], [], [], [], [], [], [], [], []]
        assert p9["known_root_generator_lower_bound"] == 223092870
        assert p9["residual_info"]["status"] == "composite-non-prime-power"
        assert p9["root_generator_lower_bound"] == 200560490130

        assert truth["exact_root_anatomy"] is True
        assert truth["exact_root_children"] == [[], [], [], [], [], [], [], [], [], [], []]
        assert truth["exact_root_generator"] == 200560490130

        assert p1["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p2["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p3["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p4["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p5["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p6["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p7["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p8["root_generator_lower_bound"] < truth["exact_root_generator"]
        assert p9["root_generator_lower_bound"] == truth["exact_root_generator"]

        assert refines_v0(p1, b1) is True
        assert refines_v0(b1, p1) is False
        assert refines_v0(p2, p1) is True
        assert refines_v0(p1, p2) is False
        assert refines_v0(p3, p2) is True
        assert refines_v0(p2, p3) is False
        assert refines_v0(p4, p3) is True
        assert refines_v0(p3, p4) is False
        assert refines_v0(p5, p4) is True
        assert refines_v0(p4, p5) is False
        assert refines_v0(p6, p5) is True
        assert refines_v0(p5, p6) is False
        assert refines_v0(p7, p6) is True
        assert refines_v0(p6, p7) is False
        assert refines_v0(p8, p7) is True
        assert refines_v0(p7, p8) is False
        assert refines_v0(p9, p8) is True
        assert refines_v0(p8, p9) is False
        assert refines_v0(truth, p9) is True
        assert refines_v0(p9, truth) is False


def test_refines_v0_primorial_law_holds_on_deep_squarefree_chain() -> None:
    from contextlib import redirect_stdout
    from io import StringIO
    from math import prod

    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    n = prod(primes)

    def primorial(k: int) -> int:
        return prod(primes[:k])

    def quiet_build(schedule: list[int]):
        buf = StringIO()
        with redirect_stdout(buf):
            return build_report(
                n,
                schedule,
                allow_pollard_rho=False,
                allow_small_residual_exact=False,
            )

    chain = [
        ([1], 0),
        ([2], 1),
        ([3], 2),
        ([5], 3),
        ([7], 4),
        ([11], 5),
        ([13], 6),
        ([17], 7),
        ([19], 8),
        ([23], 9),
    ]

    reports = []
    for schedule, depth in chain:
        report = quiet_build(schedule)
        reports.append(report)

        expected_children = [] if depth == 0 else [[] for _ in range(depth)]

        assert report["exact_root_anatomy"] is False
        assert report["known_root_children"] == expected_children
        assert report["root_generator_lower_bound"] == primorial(depth + 2)

        if depth >= 1:
            assert report["known_root_generator_lower_bound"] == primorial(depth)
            assert report["residual_info"]["status"] == "composite-non-prime-power"

    for later, earlier in zip(reports[1:], reports[:-1]):
        assert refines_v0(later, earlier) is True
        assert refines_v0(earlier, later) is False

    truth = quiet_build([1000, 10000, 100000])

    assert truth["exact_root_anatomy"] is True
    assert truth["exact_root_children"] == [[] for _ in range(11)]
    assert truth["exact_root_generator"] == primorial(11)

    assert refines_v0(truth, reports[-1]) is True
    assert refines_v0(reports[-1], truth) is False


def test_refines_v0_structural_open_witness_with_nonleaf_known_child() -> None:
    n = 4452484  # 2^2 * 101 * 103 * 107

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
    b101 = build_report(
        n,
        [101],
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
    assert b1["root_generator_lower_bound"] == 6

    assert b2["exact_root_anatomy"] is False
    assert b2["known_root_children"] == [[[]]]
    assert b2["known_root_generator_lower_bound"] == 4
    assert b2["residual_info"]["status"] == "composite-non-prime-power"
    assert b2["root_generator_lower_bound"] == 60

    assert b101["exact_root_anatomy"] is False
    assert b101["known_root_children"] == [[], [[]]]
    assert b101["known_root_generator_lower_bound"] == 12
    assert b101["residual_info"]["status"] == "composite-non-prime-power"
    assert b101["root_generator_lower_bound"] == 420

    assert truth["exact_root_anatomy"] is True
    assert truth["exact_root_children"] == [[], [], [], [[]]]
    assert truth["exact_root_generator"] == 420

    assert b2["root_generator_lower_bound"] < truth["exact_root_generator"]
    assert b101["root_generator_lower_bound"] == truth["exact_root_generator"]

    assert refines_v0(b2, b1) is True
    assert refines_v0(b1, b2) is False
    assert refines_v0(b101, b2) is True
    assert refines_v0(b2, b101) is False
    assert refines_v0(truth, b101) is True
    assert refines_v0(b101, truth) is False


def test_refines_v0_structural_open_nonleaf_witness_family_repeats() -> None:
    cases = [
        (4452484, 101),
        (4535708, 101),
        (4702156, 101),
        (4711852, 101),
        (4884764, 101),
        (4976068, 101),
        (4805156, 103),
        (4981492, 103),
        (5074604, 103),
        (5271676, 107),
    ]

    for n, first_tail in cases:
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
        bq = build_report(
            n,
            [first_tail],
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
        assert b1["root_generator_lower_bound"] == 6

        assert b2["exact_root_anatomy"] is False
        assert b2["known_root_children"] == [[[]]]
        assert b2["known_root_generator_lower_bound"] == 4
        assert b2["residual_info"]["status"] == "composite-non-prime-power"
        assert b2["root_generator_lower_bound"] == 60

        assert bq["exact_root_anatomy"] is False
        assert bq["known_root_children"] == [[], [[]]]
        assert bq["known_root_generator_lower_bound"] == 12
        assert bq["residual_info"]["status"] == "composite-non-prime-power"
        assert bq["root_generator_lower_bound"] == 420

        assert truth["exact_root_anatomy"] is True
        assert truth["exact_root_children"] == [[], [], [], [[]]]
        assert truth["exact_root_generator"] == 420

        assert refines_v0(b2, b1) is True
        assert refines_v0(b1, b2) is False
        assert refines_v0(bq, b2) is True
        assert refines_v0(b2, bq) is False
        assert refines_v0(truth, bq) is True
        assert refines_v0(bq, truth) is False


def test_refines_v0_structural_open_nonleaf_deeper_family_repeats() -> None:
    cases = [
        (54841245428, 101, 103, 107),
        (61635736012, 101, 103, 107),
        (63897597884, 101, 103, 107),
        (65091945508, 101, 103, 109),
        (67619788052, 101, 107, 109),
        (68958793756, 103, 107, 109),
    ]

    for n, q, r, s in cases:
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
        bq = build_report(
            n,
            [q],
            allow_pollard_rho=False,
            allow_small_residual_exact=False,
        )
        br = build_report(
            n,
            [r],
            allow_pollard_rho=False,
            allow_small_residual_exact=False,
        )
        bs = build_report(
            n,
            [s],
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
        assert b1["root_generator_lower_bound"] == 6

        assert b2["exact_root_anatomy"] is False
        assert b2["known_root_children"] == [[[]]]
        assert b2["known_root_generator_lower_bound"] == 4
        assert b2["residual_info"]["status"] == "composite-non-prime-power"
        assert b2["root_generator_lower_bound"] == 60

        assert bq["exact_root_anatomy"] is False
        assert bq["known_root_children"] == [[], [[]]]
        assert bq["known_root_generator_lower_bound"] == 12
        assert bq["residual_info"]["status"] == "composite-non-prime-power"
        assert bq["root_generator_lower_bound"] == 420

        assert br["exact_root_anatomy"] is False
        assert br["known_root_children"] == [[], [], [[]]]
        assert br["known_root_generator_lower_bound"] == 60
        assert br["residual_info"]["status"] == "composite-non-prime-power"
        assert br["root_generator_lower_bound"] == 4620

        assert bs["exact_root_anatomy"] is False
        assert bs["known_root_children"] == [[], [], [], [[]]]
        assert bs["known_root_generator_lower_bound"] == 420
        assert bs["residual_info"]["status"] == "composite-non-prime-power"
        assert bs["root_generator_lower_bound"] == 60060

        assert truth["exact_root_anatomy"] is True
        assert truth["exact_root_children"] == [[], [], [], [], [], [[]]]
        assert truth["exact_root_generator"] == 60060

        assert refines_v0(b2, b1) is True
        assert refines_v0(b1, b2) is False
        assert refines_v0(bq, b2) is True
        assert refines_v0(b2, bq) is False
        assert refines_v0(br, bq) is True
        assert refines_v0(bq, br) is False
        assert refines_v0(bs, br) is True
        assert refines_v0(br, bs) is False
        assert refines_v0(truth, bs) is True
        assert refines_v0(bs, truth) is False


def test_refines_v0_structural_open_witness_with_two_nonleaf_known_children() -> None:
    n = 40072356  # 2^2 * 3^2 * 101 * 103 * 107

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
    b3 = build_report(
        n,
        [3],
        allow_pollard_rho=False,
        allow_small_residual_exact=False,
    )
    b101 = build_report(
        n,
        [101],
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
    assert b1["root_generator_lower_bound"] == 6

    assert b2["exact_root_anatomy"] is False
    assert b2["known_root_children"] == [[[]]]
    assert b2["known_root_generator_lower_bound"] == 4
    assert b2["residual_info"]["status"] == "composite-non-prime-power"
    assert b2["root_generator_lower_bound"] == 60

    assert b3["exact_root_anatomy"] is False
    assert b3["known_root_children"] == [[[]], [[]]]
    assert b3["known_root_generator_lower_bound"] == 36
    assert b3["residual_info"]["status"] == "composite-non-prime-power"
    assert b3["root_generator_lower_bound"] == 1260

    assert b101["exact_root_anatomy"] is False
    assert b101["known_root_children"] == [[], [[]], [[]]]
    assert b101["known_root_generator_lower_bound"] == 180
    assert b101["residual_info"]["status"] == "composite-non-prime-power"
    assert b101["root_generator_lower_bound"] == 13860

    assert truth["exact_root_anatomy"] is True
    assert truth["exact_root_children"] == [[], [], [], [[]], [[]]]
    assert truth["exact_root_generator"] == 13860

    assert b2["root_generator_lower_bound"] < truth["exact_root_generator"]
    assert b3["root_generator_lower_bound"] < truth["exact_root_generator"]
    assert b101["root_generator_lower_bound"] == truth["exact_root_generator"]

    assert refines_v0(b2, b1) is True
    assert refines_v0(b1, b2) is False
    assert refines_v0(b3, b2) is True
    assert refines_v0(b2, b3) is False
    assert refines_v0(b101, b3) is True
    assert refines_v0(b3, b101) is False
    assert refines_v0(truth, b101) is True
    assert refines_v0(b101, truth) is False
