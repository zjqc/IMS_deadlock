from __future__ import annotations

import json
from pathlib import Path

import pytest

from ims_deadlock.tase_hardening import (
    ARTICLE_CORE_SCOPE_LOCK_SHA256,
    H2_CELLS,
    H2_TYPES,
    H3_STATE_CAP,
    H3_TIME_CAP_S,
    SCOPE_ID,
    ComputeProbe,
    IdentityCollision,
    QuantitativeExecutionRefused,
    WorkerProtocolError,
    authorization_flags,
    build_h2_plants,
    build_h3_rows,
    build_h4_islands,
    build_shard_plan,
    evaluate_h1,
    evaluate_h2_plant,
    materialize_discovery_bundle,
    pin_blas_thread_env,
    plan_workers,
    pool_square,
    reduce_shards,
    refuse_quantitative_execution,
    reject_forbidden_identity,
    run_process_pool,
    validate_wave,
)
from ims_deadlock.tase_hardening_run import (
    APPROVED_QUANT_AUTH_SHA256,
    hoeffding_tolerance,
    require_quantitative_authorization,
)

APPROVED_SPEC = "5f4e0a3d58bdf4a090322d1537dd8b4a3125e75845e146a15a02760aab5be8b2"
APPROVED_PLAN = "ee99c64ad56fcabaa74f5dc1c87c3cdb4b3ebe4e200a271b4498c8681d6b6cb4"
APPROVED_REVIEW = "e418a81b5d30708ca894fd009238782c02987ecf6e9d82d549521161c0bc2c83"


def test_scope_id_and_all_authorization_flags_are_false() -> None:
    flags = authorization_flags()
    assert SCOPE_ID == "tase_hardening_v1"
    assert flags == {
        "case_construction_authorized": False,
        "overlap_audit_authorized": False,
        "target_certification_preflight_authorized": False,
        "quantitative_execution_authorized": False,
        "theory_revision_authorized": False,
    }


def test_article_core_scope_lock_hash_is_rejected() -> None:
    with pytest.raises(IdentityCollision):
        reject_forbidden_identity(ARTICLE_CORE_SCOPE_LOCK_SHA256)


def test_unrelated_hash_is_not_a_collision() -> None:
    reject_forbidden_identity("0" * 64)


def test_quantitative_entry_is_refused() -> None:
    with pytest.raises(QuantitativeExecutionRefused):
        refuse_quantitative_execution()


def test_worker_plan_defaults_to_32_on_this_box() -> None:
    probe = ComputeProbe(logical_cpus=56, free_ram_gib=48.0, other_python_jobs=0)
    assert plan_workers(probe, family="H3") == 32
    fat = ComputeProbe(logical_cpus=56, free_ram_gib=80.0, other_python_jobs=0)
    assert plan_workers(fat, family="H3") == 48


def test_worker_plan_clamps_on_low_memory() -> None:
    probe = ComputeProbe(logical_cpus=56, free_ram_gib=12.0, other_python_jobs=0)
    assert plan_workers(probe, family="H3") == 4


def test_workers_one_refused_when_machine_is_large() -> None:
    probe = ComputeProbe(logical_cpus=56, free_ram_gib=64.0, other_python_jobs=0)
    with pytest.raises(WorkerProtocolError):
        validate_wave(
            wave="P1",
            workers=1,
            probe=probe,
            primary_repro_overlap=False,
            reducer_count=1,
        )


def test_blas_threads_pin_when_workers_at_least_eight() -> None:
    env = pin_blas_thread_env(workers=32)
    assert env["OMP_NUM_THREADS"] == "1"
    assert env["MKL_NUM_THREADS"] == "1"
    assert env["OPENBLAS_NUM_THREADS"] == "1"
    assert env["NUMEXPR_NUM_THREADS"] == "1"


def test_primary_repro_overlap_and_two_reducers_are_refused() -> None:
    probe = ComputeProbe(logical_cpus=56, free_ram_gib=64.0, other_python_jobs=0)
    with pytest.raises(WorkerProtocolError):
        validate_wave(
            wave="R1",
            workers=32,
            probe=probe,
            primary_repro_overlap=True,
            reducer_count=1,
        )
    with pytest.raises(WorkerProtocolError):
        validate_wave(
            wave="Z",
            workers=32,
            probe=probe,
            primary_repro_overlap=False,
            reducer_count=2,
        )


def test_h1_cl1_refuses_deterministic_kappa() -> None:
    result = evaluate_h1("H1_CE_CL1_nonconfluent_closure")
    assert result["outcome"] == "refuse_deterministic_kappa"
    assert result["stable_successor_count"] == 2


def test_h1_bixd2_optional_drain_does_not_prove_deadlock_free() -> None:
    result = evaluate_h1("H1_CE_BIXD2_optional_drain")
    assert result["optional_drain_present"] is True
    assert result["ring_deadlock_reachable"] is True
    assert result["structural_deadlock_free"] is False


def test_h1_int1_cut_creates_a_new_kernel() -> None:
    result = evaluate_h1("H1_CE_INT1_new_core_after_cut")
    assert result["original_kernel"]
    assert result["intervened_kernel"]
    assert result["original_kernel"] != result["intervened_kernel"]


def test_h1_p3_nonchain_is_not_applicable() -> None:
    result = evaluate_h1("H1_P3_nonchain_refuse")
    assert result["p3_verdict"] == "not_applicable"
    assert result["chain_decomposable"] is False
    assert result["has_covering_kernel"] is True


def test_h2_has_thirty_two_plants_and_four_methods() -> None:
    plants = build_h2_plants()
    assert len(plants) == 32
    assert len(H2_TYPES) == 8
    assert len(H2_CELLS) == 4
    report = evaluate_h2_plant(plants[0])
    assert set(report["methods"]) == {
        "machine_cycle_scc",
        "closed_core",
        "sip1_or_refuse",
        "lts_truth",
    }
    for key in (
        "false_positive",
        "false_negative",
        "refusal_count",
        "certificate_size",
        "runtime_s",
        "peak_state_count",
    ):
        assert key in report


def test_h3_product_and_caps() -> None:
    rows = build_h3_rows()
    assert len(rows) == 576
    assert H3_STATE_CAP == 100_000
    assert H3_TIME_CAP_S == 300
    over_states = {"n_jobs": 2, "n_resources": 2, "capacity": 1, "state_count": 100_001}
    over_time = {"n_jobs": 2, "n_resources": 2, "capacity": 1, "elapsed_s": 301}
    from ims_deadlock.tase_hardening import classify_h3_row

    assert classify_h3_row(over_states) == "refused"
    assert classify_h3_row(over_time) == "refused"


def test_h4_islands_are_synthetic_digital_twins() -> None:
    islands = build_h4_islands()
    assert {island.role for island in islands} == {"base", "intervention"}
    for island in islands:
        assert island.label == "synthetic digital-twin"
        assert "agv" in {resource.kind for resource in island.model.resources.values()}
        modes = [transition.target_mode for transition in island.transitions]
        assert any("blocked_unload" in mode for mode in modes)


def test_h4_v3_base_is_local_hit_and_intervention_is_not() -> None:
    from ims_deadlock.analysis import enumerate_stable_lts
    from ims_deadlock.certificates import (
        find_deadlock_certificate,
        find_local_blocking_certificate,
    )
    from ims_deadlock.model import validate_model_state
    from ims_deadlock.tase_hardening import build_h4_v3_islands

    islands = {island.role: island for island in build_h4_v3_islands()}
    base = islands["base"]
    intervened = islands["intervention"]
    assert (
        find_deadlock_certificate(base.model, base.initial_state, base.transitions)
        is None
    )
    local = find_local_blocking_certificate(
        base.model, base.initial_state, base.transitions
    )
    assert local is not None
    assert set(local.kernel_jobs) == {"A", "B"}
    assert (
        find_local_blocking_certificate(
            intervened.model, intervened.initial_state, intervened.transitions
        )
        is None
    )
    for island in islands.values():
        lts = enumerate_stable_lts(
            island.model, island.initial_state, island.transitions, max_states=4096
        )
        assert lts.truncated is False
        for record in lts.states:
            assert validate_model_state(island.model, record.state).valid


def test_h4_lts_never_completes_while_holding() -> None:
    from ims_deadlock.analysis import enumerate_stable_lts
    from ims_deadlock.model import validate_model_state

    for island in build_h4_islands():
        lts = enumerate_stable_lts(
            island.model,
            island.initial_state,
            island.transitions,
            max_states=4096,
        )
        assert lts.truncated is False
        assert lts.states
        for record in lts.states:
            report = validate_model_state(island.model, record.state)
            assert report.valid, (island.role, record.state_id, report.issues)
            if record.state.complete:
                assert record.state.holds == ()


def test_shard_plan_and_reducer_are_disjoint() -> None:
    units = tuple(f"u{i}" for i in range(10))
    plan = build_shard_plan(units, workers=4)
    assert len(plan) == 4
    flat = [item for shard in plan for item in shard]
    assert sorted(flat) == sorted(units)
    assert len(set(flat)) == 10


def test_process_pool_runs_tiny_independent_units() -> None:
    results = run_process_pool((1, 2, 3, 4), pool_square, workers=2)
    assert sorted(results) == [1, 4, 9, 16]


def test_reduce_shards_requires_complete_set(tmp_path: Path) -> None:
    shard_dir = tmp_path / "shards"
    shard_dir.mkdir()
    (shard_dir / "u1__w0.json").write_text(json.dumps({"id": "u1"}), encoding="utf-8")
    with pytest.raises(WorkerProtocolError):
        reduce_shards(shard_dir, expected_ids=("u1", "u2"))


def test_hoeffding_tolerance_is_tighter_than_article_core() -> None:
    assert hoeffding_tolerance() < 0.01
    assert hoeffding_tolerance() > 0.005


def test_quantitative_auth_rejects_wrong_bytes(tmp_path: Path) -> None:
    auth = tmp_path / (
        "cases/discovery/tase_hardening_v1/quantitative_authorization.json"
    )
    auth.parent.mkdir(parents=True)
    auth.write_text("{}", encoding="utf-8")
    with pytest.raises(WorkerProtocolError):
        require_quantitative_authorization(tmp_path)
    assert APPROVED_QUANT_AUTH_SHA256.startswith("090c7551")


def test_materialize_writes_h1_and_h4_without_science(tmp_path: Path) -> None:
    written = materialize_discovery_bundle(tmp_path)
    assert (tmp_path / "authorization.json").is_file()
    payload = json.loads((tmp_path / "authorization.json").read_text(encoding="utf-8"))
    assert payload["quantitative_execution_authorized"] is False
    assert any(path.name.startswith("H1_") for path in written)
    assert any("h4" in str(path) for path in written)
