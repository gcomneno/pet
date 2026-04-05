from tools.partial_signature_probe import build_report


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
