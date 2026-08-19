from __future__ import annotations

from ims_deadlock.engine import enabled_transition
from ims_deadlock.tase_hardening import (
    ARTICLE_CORE_SCOPE_LOCK_SHA256,
    build_h4_v3_islands,
    build_h5_subjects,
    evaluate_h5_subject,
)
from ims_deadlock.tase_hardening_run import hoeffding_tolerance, solve_h4_exact
from ims_deadlock.tase_height import (
    H6_A_ID,
    H6_B_ID,
    H6_SPEC_SHA256,
    H7_BASE_MODEL_ID,
    H7_INT_MODEL_ID,
    H7_LOCAL_HIT_WORD,
    H7_SPEC_SHA256,
    H8_SPEC_SHA256,
    build_h6_a_plant,
    build_h6_b_plant,
    build_h7_island,
    build_h7_islands,
    eval_h7_barrier,
    evaluate_h6_subject,
    evaluate_h8_supervisor,
    fire_word,
    h7_as_height_plant,
    h7_local_hit_enabled,
    verify_embedding_certificate,
)


def test_spec_hashes_are_locked() -> None:
    assert len(H6_SPEC_SHA256) == 64
    assert len(H7_SPEC_SHA256) == 64
    assert len(H8_SPEC_SHA256) == 64
    assert H6_SPEC_SHA256 != ARTICLE_CORE_SCOPE_LOCK_SHA256


def test_h6_a_certificate_verifies() -> None:
    cert = verify_embedding_certificate(build_h6_a_plant())
    assert cert["verified"] is True
    assert all(cert["clauses"].values())
    assert cert["field4_reason"] is None


def test_h6_a_four_fields_and_agreement() -> None:
    row = evaluate_h6_subject(build_h6_a_plant(), claimed_prefix=("invented",))
    assert row["id"] == H6_A_ID
    assert row["fields"]["reachable"] is True
    assert row["fields"]["local_family_available"] is True
    assert row["fields"]["matching_kernel_count"] >= 1
    assert row["fields"]["s4pr_overlap"] is True
    assert row["bridge_agreement"] is True
    assert row["sba_ran"] is False
    assert row["crp_equations_ran"] is False
    assert row["g4_g5_identity_reused"] is False
    assert row["certificate"]["reachability"]["bfs_witness"] != ["invented"]


def test_h6_b_field4_refused_as_distortion() -> None:
    cert = verify_embedding_certificate(build_h6_b_plant())
    assert cert["verified"] is False
    assert cert["clauses"]["E5"] is False
    assert cert["field4_reason"] == "declared_distortion_agv_token"
    row = evaluate_h6_subject(build_h6_b_plant())
    assert row["id"] == H6_B_ID
    assert row["fields"]["s4pr_overlap"] is False
    assert row["bridge_agreement"] is False
    assert row["field4_reason"] == "declared_distortion_agv_token"


def test_h5_still_refuses_field4() -> None:
    rows = [evaluate_h5_subject(subject) for subject in build_h5_subjects()]
    assert len(rows) == 6
    assert {row["field4_reason"] for row in rows} == {"no_independent_s4pr_embedding"}
    assert all(row["bridge_agreement"] is False for row in rows)


def test_h7_initial_is_transient_and_word_hits_local() -> None:
    island = build_h7_island("base")
    assert island.model.id == H7_BASE_MODEL_ID
    assert build_h7_island("intervention").model.id == H7_INT_MODEL_ID
    plant = h7_as_height_plant(island)
    enabled = {
        item.name
        for item in plant.transitions
        if enabled_transition(plant.model, plant.initial_state, item)
    }
    assert {"A-start-m1", "B-start-v", "C-service-1"} <= enabled
    assert h7_local_hit_enabled() is True
    state = fire_word(plant, H7_LOCAL_HIT_WORD)
    assert any(hold.job_id == "A" and hold.resource_id == "M1" for hold in state.holds)
    assert any(hold.job_id == "B" and hold.resource_id == "V" for hold in state.holds)
    assert any(hold.job_id == "C" and hold.resource_id == "M2" for hold in state.holds)


def test_h7_barrier_certified_not_absorbing_has_local_outgoing() -> None:
    barrier = eval_h7_barrier("base")
    assert barrier["barrier_a"] == "certified"
    assert barrier["refusal_code"] is None
    assert barrier["initial_class"] == "transient"
    assert len(barrier["d_local"]) >= 1
    assert barrier["local_with_outgoing"] >= 1


def test_h7_exact_positive_time_and_intervention_delta() -> None:
    base = eval_h7_barrier("base")
    intervention = eval_h7_barrier("intervention")
    exact_base = solve_h4_exact(base)
    exact_int = solve_h4_exact(intervention)
    assert exact_base["status"] == "exact"
    assert exact_int["status"] == "exact"
    assert exact_base["probabilities"]["theta_l"] > 0.0
    assert exact_base["mean_stopped_time"] >= 0.25
    eps = hoeffding_tolerance()
    delta_theta = abs(
        exact_base["probabilities"]["theta_b"] - exact_int["probabilities"]["theta_b"]
    )
    delta_m = abs(exact_base["mean_stopped_time"] - exact_int["mean_stopped_time"])
    assert delta_theta > eps or delta_m > eps


def test_h4_v3_untouched_identity() -> None:
    base, intervention = build_h4_v3_islands()
    assert base.model.id == "h4-island-v3-base"
    assert intervention.model.id == "h4-island-v3-intervention"
    h7_ids = {island.model.id for island in build_h7_islands()}
    assert "h4-island-v3-base" not in h7_ids


def test_h8_supervisor_on_h7_base() -> None:
    island = build_h7_island("base")
    barrier = eval_h7_barrier("base")
    row = evaluate_h8_supervisor(barrier, island)
    plant_exact = solve_h4_exact(barrier)
    assert row["status"] == "computed"
    assert row["n_states"] == barrier["state_count"]
    assert row["n_disabled_state_events"] >= 0
    assert row["h8_plant"] == "H7_v4_base"
    assert row["initial_state_feasible"] is True
    supervised = row["supervised_exact"]
    assert supervised is not None
    assert supervised["status"] == "exact"
    assert (
        supervised["probabilities"]["theta_b"]
        <= plant_exact["probabilities"]["theta_b"] + 1e-12
    )
    for _state, event in row["disabled_state_events"]:
        spec = next(item for item in island.transitions if item.name == event)
        assert spec.controllable is True
