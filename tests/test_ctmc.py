from math import isclose

import pytest

from ims_deadlock.ctmc import (
    LINEAR_RESIDUAL_ABSOLUTE_TOLERANCE,
    PROBABILITY_ABSOLUTE_TOLERANCE,
    AbsorbingCTMC,
    _solve_linear,
    linear_residual_is_numerically_valid,
    probability_bounds_match_values,
    probability_interval_is_numerically_valid,
    probability_values_are_numerically_valid,
)


def test_probability_interval_contract_accepts_roundoff_not_real_violations() -> None:
    assert PROBABILITY_ABSOLUTE_TOLERANCE == 1e-10
    assert probability_interval_is_numerically_valid(-0.0, 1.0000000000000002)
    assert probability_interval_is_numerically_valid(-5e-11, 1.0 + 5e-11)

    assert not probability_interval_is_numerically_valid(-1e-6, 1.0)
    assert not probability_interval_is_numerically_valid(0.0, 1.0 + 1e-6)
    assert not probability_interval_is_numerically_valid(0.75, 0.25)
    assert not probability_interval_is_numerically_valid(True, 1.0)
    assert not probability_interval_is_numerically_valid(0.0, float("inf"))


def test_probability_vector_bounds_and_residual_contracts_are_independent() -> None:
    values = (0.25, 1.0000000000000002, -0.0)

    assert probability_values_are_numerically_valid(values)
    assert probability_bounds_match_values(values, -0.0, 1.0000000000000002)
    assert probability_bounds_match_values(values, 0.0, 1.0)
    assert not probability_bounds_match_values(values, 0.0, 0.75)
    assert not probability_values_are_numerically_valid((0.25, 1.000001))
    assert not probability_values_are_numerically_valid(())

    assert LINEAR_RESIDUAL_ABSOLUTE_TOLERANCE == 1e-10
    assert linear_residual_is_numerically_valid(3.2e-15)
    assert not linear_residual_is_numerically_valid(1e-6)
    assert not linear_residual_is_numerically_valid(True)


def test_absorbing_ctmc_solves_deadlock_committor_and_mean_time() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0",),
        completion_rates={("s0", "done"): 3.0},
        deadlock_rates={("s0", "dead"): 1.0},
        transient_rates={},
    )

    result = ctmc.solve()

    assert result.deadlock_probability["s0"] == 0.25
    assert result.mean_absorption_time["s0"] == 0.25
    assert result.generator_provenance == "explicit_user_supplied"
    assert result.case_derived is False
    assert result.committor_residual_inf_norm == 0.0
    assert result.mean_time_residual_inf_norm == 0.0
    assert result.probability_bounds_valid is True


def test_absorbing_ctmc_solves_valid_slow_one_state_chain() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0",),
        completion_rates={("s0", "done"): 1e-13},
        deadlock_rates={("s0", "dead"): 1e-13},
        transient_rates={},
    )

    result = ctmc.solve()

    assert result.deadlock_probability["s0"] == pytest.approx(0.5)
    assert result.mean_absorption_time["s0"] == pytest.approx(5e12)
    assert result.committor_residual_inf_norm == pytest.approx(0.0)
    assert result.mean_time_residual_inf_norm == pytest.approx(0.0)


def test_absorbing_ctmc_computes_deadlock_rate_sensitivity_and_doob_generator() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0",),
        completion_rates={("s0", "done"): 3.0},
        deadlock_rates={("s0", "dead"): 1.0},
        transient_rates={},
    )

    sensitivity = ctmc.sensitivity(
        derivative_deadlock_rates={("s0", "dead"): 1.0},
    )
    conditioned = ctmc.deadlock_conditioned_generator()

    assert sensitivity.deadlock_probability_derivative["s0"] == pytest.approx(0.1875)
    assert sensitivity.mean_absorption_time_derivative["s0"] == pytest.approx(-0.0625)
    assert sensitivity.committor_derivative_residual_inf_norm == pytest.approx(0.0)
    assert sensitivity.mean_time_derivative_residual_inf_norm == pytest.approx(0.0)
    assert conditioned.transient_states == ("s0",)
    assert conditioned.transient_rates == {}
    assert conditioned.deadlock_rates[("s0", "dead")] == pytest.approx(4.0)
    assert conditioned.completion_rates[("s0", "done")] == 0.0
    assert conditioned.row_sum_residual_inf_norm == pytest.approx(0.0)
    assert conditioned.domain["conditioning_event"] == "deadlock_absorption"
    assert conditioned.domain["positive_h_transient_states"] == ("s0",)


def test_two_state_ctmc_reports_residuals_and_probability_bounds() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0", "s1"),
        completion_rates={("s0", "done"): 2.0, ("s1", "done"): 1.0},
        deadlock_rates={("s0", "dead"): 1.0, ("s1", "dead"): 3.0},
        transient_rates={("s0", "s1"): 1.0, ("s1", "s0"): 2.0},
    )

    result = ctmc.solve()

    assert result.deadlock_probability["s0"] == pytest.approx(9.0 / 22.0)
    assert result.deadlock_probability["s1"] == pytest.approx(7.0 / 11.0)
    assert result.mean_absorption_time["s0"] == pytest.approx(7.0 / 22.0)
    assert result.mean_absorption_time["s1"] == pytest.approx(3.0 / 11.0)
    assert result.committor_residual_inf_norm <= 1e-12
    assert result.mean_time_residual_inf_norm <= 1e-12
    assert result.probability_bounds is not None
    assert result.probability_bounds["min"] == pytest.approx(9.0 / 22.0)
    assert result.probability_bounds["max"] == pytest.approx(7.0 / 11.0)
    assert result.probability_bounds_valid is True


def test_ctmc_rejects_duplicate_transient_state_ids() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0", "s0"),
        completion_rates={},
        deadlock_rates={("s0", "dead"): 1.0},
        transient_rates={},
    )

    try:
        ctmc.solve()
    except ValueError as exc:
        assert "duplicate transient state" in str(exc)
    else:  # pragma: no cover - exercised only when validation is broken
        raise AssertionError("expected duplicate transient state validation failure")


def test_ctmc_rejects_unknown_transition_endpoint() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0",),
        completion_rates={},
        deadlock_rates={},
        transient_rates={("s0", "missing"): 1.0},
    )

    try:
        ctmc.solve()
    except ValueError as exc:
        assert "unknown transient target" in str(exc)
    else:  # pragma: no cover - exercised only when validation is broken
        raise AssertionError("expected unknown target validation failure")


def test_ctmc_rejects_non_finite_rates() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0",),
        completion_rates={},
        deadlock_rates={("s0", "dead"): float("nan")},
        transient_rates={},
    )

    try:
        ctmc.solve()
    except ValueError as exc:
        assert "finite" in str(exc)
    else:  # pragma: no cover - exercised only when validation is broken
        raise AssertionError("expected non-finite rate validation failure")


def test_ctmc_rejects_absorbing_target_that_is_transient() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0", "s1"),
        completion_rates={("s0", "s1"): 1.0},
        deadlock_rates={},
        transient_rates={},
    )

    try:
        ctmc.solve()
    except ValueError as exc:
        assert "completion target 's1' conflicts with transient state" in str(exc)
    else:  # pragma: no cover - exercised only when validation is broken
        raise AssertionError("expected absorbing/transient partition failure")


def test_ctmc_rejects_completion_deadlock_absorbing_label_overlap() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0",),
        completion_rates={("s0", "absorbed"): 1.0},
        deadlock_rates={("s0", "absorbed"): 1.0},
        transient_rates={},
    )

    try:
        ctmc.solve()
    except ValueError as exc:
        assert (
            "absorbing label 'absorbed' appears in both completion and deadlock"
            in str(exc)
        )
    else:  # pragma: no cover - exercised only when validation is broken
        raise AssertionError("expected completion/deadlock partition failure")


def test_ctmc_rejects_zero_outgoing_rate_state() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0",),
        completion_rates={},
        deadlock_rates={},
        transient_rates={},
    )

    with pytest.raises(ValueError, match="positive total outgoing"):
        ctmc.solve()


def test_linear_solver_preserves_true_singular_detection() -> None:
    with pytest.raises(ValueError, match="singular CTMC transient generator"):
        _solve_linear([[0.0]], [1.0])


def test_ctmc_rejects_state_without_reachable_absorption() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0", "s1", "s2"),
        completion_rates={("s0", "done"): 1.0},
        deadlock_rates={},
        transient_rates={("s1", "s2"): 1.0, ("s2", "s1"): 1.0},
    )

    with pytest.raises(ValueError, match="reachable absorbing"):
        ctmc.solve()


def test_ctmc_rejects_explicit_self_transition_rate() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0",),
        completion_rates={("s0", "done"): 1.0},
        deadlock_rates={},
        transient_rates={("s0", "s0"): 1.0},
    )

    with pytest.raises(ValueError, match="self transitions"):
        ctmc.solve()


def test_ctmc_rejects_invalid_derivative_endpoint() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0",),
        completion_rates={("s0", "done"): 3.0},
        deadlock_rates={("s0", "dead"): 1.0},
        transient_rates={},
    )

    with pytest.raises(ValueError, match="unknown derivative deadlock target"):
        ctmc.sensitivity(derivative_deadlock_rates={("s0", "other_dead"): 1.0})


def test_doob_generator_excludes_zero_deadlock_probability_transients() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0", "s1"),
        completion_rates={("s0", "done"): 1.0},
        deadlock_rates={("s1", "dead"): 1.0},
        transient_rates={("s0", "s1"): 0.0},
    )

    conditioned = ctmc.deadlock_conditioned_generator()

    assert conditioned.transient_states == ("s1",)
    assert conditioned.excluded_transient_states == ("s0",)
    assert isclose(conditioned.deadlock_rates[("s1", "dead")], 1.0)


def test_doob_generator_keeps_rare_mathematically_positive_deadlock_state() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("rare",),
        completion_rates={("rare", "done"): 1.0},
        deadlock_rates={("rare", "dead"): 1e-15},
        transient_rates={},
    )

    conditioned = ctmc.deadlock_conditioned_generator()

    assert conditioned.transient_states == ("rare",)
    assert conditioned.excluded_transient_states == ()
    assert conditioned.domain["positive_h_transient_states"] == ("rare",)
    assert conditioned.deadlock_rates[("rare", "dead")] == pytest.approx(1.0)
