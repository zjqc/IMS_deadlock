from ims_deadlock.ctmc import AbsorbingCTMC


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

