import pytest

from ims_deadlock.ctmc import AbsorbingCTMC
from ims_deadlock.stochastic import estimate_competing_absorption


def test_gillespie_estimator_is_reproducible_and_reports_manifest_and_ci() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0",),
        completion_rates={("s0", "done"): 3.0},
        deadlock_rates={("s0", "dead"): 1.0},
        transient_rates={},
    )

    first = estimate_competing_absorption(
        ctmc,
        initial_state="s0",
        sample_count=100,
        master_seed=12345,
    )
    second = estimate_competing_absorption(
        ctmc,
        initial_state="s0",
        sample_count=100,
        master_seed=12345,
    )

    assert first == second
    assert first.sample_count == 100
    assert 0.0 <= first.deadlock_estimate <= 1.0
    assert first.wilson_95_ci[0] <= first.deadlock_estimate <= first.wilson_95_ci[1]
    assert first.mean_absorption_time > 0.0
    assert first.case_derived is False
    assert first.generator_provenance == "explicit_user_supplied"
    assert first.stream_manifest["master_seed"] == 12345
    assert first.stream_manifest["sample_count"] == 100
    assert (
        first.stream_manifest["seed_derivation"]
        == "sha256(master_seed:replication_index)"
    )
    assert first.stream_manifest["replication_seed_digest"]


def test_gillespie_interval_covers_matching_exact_committor_fixture() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0",),
        completion_rates={("s0", "done"): 3.0},
        deadlock_rates={("s0", "dead"): 1.0},
        transient_rates={},
    )
    exact = ctmc.solve().deadlock_probability["s0"]

    estimate = estimate_competing_absorption(
        ctmc,
        initial_state="s0",
        sample_count=1000,
        master_seed=12345,
    )

    assert exact == 0.25
    assert estimate.wilson_95_ci[0] <= exact <= estimate.wilson_95_ci[1]


def test_gillespie_estimator_handles_two_state_chain() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0", "s1"),
        completion_rates={("s1", "done"): 2.0},
        deadlock_rates={("s0", "dead"): 1.0},
        transient_rates={("s0", "s1"): 3.0},
    )

    result = estimate_competing_absorption(
        ctmc,
        initial_state="s0",
        sample_count=200,
        master_seed=7,
    )

    assert result.sample_count == 200
    assert 0.0 < result.deadlock_estimate < 1.0
    assert result.mean_absorption_time > 0.0


def test_gillespie_estimator_rejects_invalid_inputs() -> None:
    ctmc = AbsorbingCTMC(
        transient_states=("s0",),
        completion_rates={("s0", "done"): 1.0},
        deadlock_rates={},
        transient_rates={},
    )

    with pytest.raises(ValueError, match="sample_count"):
        estimate_competing_absorption(
            ctmc,
            initial_state="s0",
            sample_count=0,
            master_seed=1,
        )

    with pytest.raises(ValueError, match="unknown initial_state"):
        estimate_competing_absorption(
            ctmc,
            initial_state="missing",
            sample_count=1,
            master_seed=1,
        )
