from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from hashlib import sha256
from pathlib import Path

import pytest

from ims_deadlock.article_core import (
    ArticleCase,
    ArticleTransition,
    build_article_cases,
    derive_replication_seed,
    load_article_scope,
    run_article_closure,
    simulate_article_case,
    solve_article_case,
    validate_article_case,
    write_article_closure_evidence,
)
from ims_deadlock.g6b_canonical_json import JsonObject, JsonValue

REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_IDS = (
    "g6b_article_bridge_competing_local_completion_v1",
    "g6b_cu_nc_dglobal_only_with_dlocal_v1",
    "g6b_cu_nc_local_bypass_completes_v1",
    "g6b_cu_pc_dglobal_only_v1",
    "g6b_cu_pc_dlocal_a2b_single_kernel_v1",
    "g6b_cu_pc_dlocal_lts_multi_kernel_v1",
)
SEALED_CASE_INPUT_SHA256 = {
    "g6b_cu_nc_dglobal_only_with_dlocal_v1": (
        "52921e95d072d8fa377a459b5c99e6653aab2efdbd14325c642eb6472af14ccd"
    ),
    "g6b_cu_nc_local_bypass_completes_v1": (
        "93eb24cf7439ca5aad29ef255b3c5e0e352295757eb96bed3a9c443b93b7d2a2"
    ),
    "g6b_cu_pc_dglobal_only_v1": (
        "0745d483b45dd0049cfa143e8ec224cadbe6e090f6d54a0f4fe5a2d3de11964c"
    ),
    "g6b_cu_pc_dlocal_a2b_single_kernel_v1": (
        "c869a580df13a4644a56d8b791a6c30568d457ba2724558f09375baf40e61481"
    ),
    "g6b_cu_pc_dlocal_lts_multi_kernel_v1": (
        "ac6a1c529f22b924974562e9aee2223f878135224b2b1a9673aaa4f9558487c2"
    ),
}
ESTIMANDS = (
    "theta_global_before_success",
    "theta_local_before_success",
    "theta_selected_bad_before_success",
)


def _case_by_id() -> dict[str, ArticleCase]:
    return {case.case_id: case for case in build_article_cases(REPO_ROOT)}


def _json_object(value: JsonValue) -> JsonObject:
    assert isinstance(value, dict)
    return value


def _json_list(value: JsonValue) -> list[JsonValue]:
    assert isinstance(value, list)
    return value


def test_scope_lock_is_frozen_self_hashed_and_bounded() -> None:
    scope = load_article_scope(REPO_ROOT)
    des_contract = _json_object(scope["des_contract"])
    original_denominator = _json_object(scope["original_sealed_denominator"])
    sealed_identity = _json_object(scope["sealed_bundle_identity"])
    normalization_identity = _json_object(scope["retired_normalization_identity"])

    assert tuple(_json_list(scope["article_core_case_ids"])) == CASE_IDS
    assert scope["scope_lock_sha256"] == (
        "86ec7b80c888c7758d326a9de7793b0f0f65f4740ecf0303e1b17d2d14344660"
    )
    assert scope["no_failed_case_substitution"] is True
    assert scope["study_role"] == "scoped_constructive_theory_article_not_confirmation"
    assert original_denominator["case_unit_count"] == 13
    assert des_contract == {
        "absolute_error_tolerance": "0.028340",
        "comparison_cell_count": 18,
        "familywise_delta": "0.05",
        "master_seed": 2026080601,
        "planned_replicates_per_case": 4096,
        "seed_derivation_rule": "sha256(master_seed:replication_index)",
    }
    assert sealed_identity["manifest_self_sha256"] == (
        "36622495237f2c22677190b3858d275ea8285d0ee8fc1ed004f8c03e8543a68c"
    )
    assert normalization_identity["eligible_record_count"] == 119
    assert normalization_identity["typed_refusal_count"] == 62


def test_five_reused_cases_are_bound_to_the_sealed_source_bytes() -> None:
    cases = build_article_cases(REPO_ROOT)

    assert tuple(case.case_id for case in cases) == CASE_IDS
    for case in cases:
        if case.case_id not in SEALED_CASE_INPUT_SHA256:
            assert case.source_role == "predeclared_article_bridge"
            continue
        expected = SEALED_CASE_INPUT_SHA256[case.case_id]
        assert case.source_sha256 == expected
        assert case.source_path is not None
        assert (
            sha256((REPO_ROOT / case.source_path).read_bytes()).hexdigest() == expected
        )


def test_theory_obligations_close_on_matched_cases_not_one_universal_method() -> None:
    cases = _case_by_id()

    global_only = validate_article_case(cases["g6b_cu_pc_dglobal_only_v1"])
    assert global_only.admission_route == "time_zero_global"
    assert global_only.d_global_states == ("s_initial",)
    assert global_only.d_local_states == ()

    a2b = validate_article_case(cases["g6b_cu_pc_dlocal_a2b_single_kernel_v1"])
    assert a2b.admission_route == "A2b_request_closed"
    assert a2b.d_local_states == ("s_initial",)
    assert a2b.checks["a2b_request_closed_proof"] is True

    lts = validate_article_case(cases["g6b_cu_pc_dlocal_lts_multi_kernel_v1"])
    assert lts.admission_route == "complete_LTS_nonreachability"
    assert lts.d_local_states == ("dlocal_ab", "dlocal_cd")
    assert lts.checks["complete_lts"] is True
    assert lts.checks["dlocal_cannot_reach_completion"] is True
    assert lts.plant_transition_count > lts.stopped_transition_count

    bypass = validate_article_case(cases["g6b_cu_nc_local_bypass_completes_v1"])
    assert bypass.admission_route == "boundary_control_not_admitted"
    assert bypass.local_candidate_states == ("s_local_candidate",)
    assert bypass.d_local_states == ()
    assert bypass.completion_reachable_by_candidate == {"s_local_candidate": True}

    precedence = validate_article_case(cases["g6b_cu_nc_dglobal_only_with_dlocal_v1"])
    assert precedence.d_global_states == ("s_initial",)
    assert precedence.local_candidate_states == ("s_initial",)
    assert precedence.d_local_states == ()
    assert precedence.checks["global_precedence_no_double_count"] is True


def test_validator_rejects_overlap_missing_a2b_proof_and_lts_escape() -> None:
    cases = _case_by_id()
    bridge = cases["g6b_article_bridge_competing_local_completion_v1"]
    with pytest.raises(ValueError, match="pairwise disjoint"):
        validate_article_case(
            replace(bridge, d_global_states=bridge.d_local_states),
        )

    a2b = cases["g6b_cu_pc_dlocal_a2b_single_kernel_v1"]
    with pytest.raises(ValueError, match="A2b proof"):
        validate_article_case(replace(a2b, a2b_verified_states=frozenset()))

    lts = cases["g6b_cu_pc_dlocal_lts_multi_kernel_v1"]
    escaped = replace(
        lts,
        transitions=lts.transitions
        + (
            ArticleTransition(
                source="post_hit",
                event="t_illegal_escape",
                target="f_complete",
                rate=Decimal("1"),
            ),
        ),
    )
    with pytest.raises(ValueError, match="completion reachable"):
        validate_article_case(escaped)


def test_validator_rejects_bad_rates_and_unselected_closed_classes() -> None:
    bridge = _case_by_id()["g6b_article_bridge_competing_local_completion_v1"]
    bad_rate = replace(
        bridge,
        transitions=(replace(bridge.transitions[0], rate=Decimal("0")),)
        + bridge.transitions[1:],
    )
    with pytest.raises(ValueError, match="positive finite"):
        validate_article_case(bad_rate)

    trapped = replace(
        bridge,
        states=bridge.states + ("trap_a", "trap_b"),
        transitions=bridge.transitions
        + (
            ArticleTransition("s0", "enter_trap", "trap_a", Decimal("1")),
            ArticleTransition("trap_a", "cycle_ab", "trap_b", Decimal("1")),
            ArticleTransition("trap_b", "cycle_ba", "trap_a", Decimal("1")),
        ),
    )
    with pytest.raises(ValueError, match="selected absorbing class"):
        validate_article_case(trapped)


def test_exact_solution_matches_all_six_predeclared_case_semantics() -> None:
    exact = {
        case.case_id: solve_article_case(case).probabilities
        for case in build_article_cases(REPO_ROOT)
    }

    assert exact["g6b_cu_pc_dglobal_only_v1"] == {
        ESTIMANDS[0]: Decimal("1"),
        ESTIMANDS[1]: Decimal("0"),
        ESTIMANDS[2]: Decimal("1"),
    }
    assert exact["g6b_cu_pc_dlocal_a2b_single_kernel_v1"] == {
        ESTIMANDS[0]: Decimal("0"),
        ESTIMANDS[1]: Decimal("1"),
        ESTIMANDS[2]: Decimal("1"),
    }
    assert exact["g6b_cu_pc_dlocal_lts_multi_kernel_v1"] == {
        ESTIMANDS[0]: Decimal("0"),
        ESTIMANDS[1]: Decimal("1"),
        ESTIMANDS[2]: Decimal("1"),
    }
    assert exact["g6b_cu_nc_local_bypass_completes_v1"] == {
        ESTIMANDS[0]: Decimal("0"),
        ESTIMANDS[1]: Decimal("0"),
        ESTIMANDS[2]: Decimal("0"),
    }
    assert exact["g6b_cu_nc_dglobal_only_with_dlocal_v1"] == {
        ESTIMANDS[0]: Decimal("1"),
        ESTIMANDS[1]: Decimal("0"),
        ESTIMANDS[2]: Decimal("1"),
    }
    bridge = exact["g6b_article_bridge_competing_local_completion_v1"]
    assert bridge[ESTIMANDS[0]] == Decimal("0")
    assert bridge[ESTIMANDS[1]] == pytest.approx(Decimal(1) / Decimal(3))
    assert bridge[ESTIMANDS[2]] == pytest.approx(Decimal(1) / Decimal(3))


def test_des_is_reproducible_multiclass_and_has_no_retry_surface() -> None:
    bridge = _case_by_id()["g6b_article_bridge_competing_local_completion_v1"]

    expected_seed = int.from_bytes(
        sha256(b"2026080601:0").digest(),
        byteorder="big",
    )
    assert derive_replication_seed(2026080601, 0) == expected_seed

    first = simulate_article_case(
        bridge,
        sample_count=256,
        master_seed=2026080601,
    )
    second = simulate_article_case(
        bridge,
        sample_count=256,
        master_seed=2026080601,
    )
    assert first == second
    assert sum(first.counts.values()) == 256
    assert set(first.counts) == {"D_global", "D_local", "F"}
    assert first.stream_manifest["seed_derivation"] == (
        "sha256(master_seed:replication_index)"
    )
    assert "retry" not in first.stream_manifest


def test_full_in_memory_closure_mechanically_selects_tier_a() -> None:
    result = run_article_closure(REPO_ROOT)

    assert result.case_ids == CASE_IDS
    assert result.comparison_cell_count == 18
    assert result.all_cells_compatible is True
    assert result.claim_tier == "tier_a_dual_route_closure"
    assert result.original_g6b_gate == "OPEN_PENDING"


def test_evidence_writer_is_write_once_and_manifest_is_last(tmp_path: Path) -> None:
    output_root = tmp_path / "minimal_closure_v1"

    result = write_article_closure_evidence(REPO_ROOT, output_root=output_root)

    assert result.claim_tier == "tier_a_dual_route_closure"
    assert sorted(path.name for path in output_root.iterdir()) == [
        "article_case_certificates.json",
        "article_closure_manifest.json",
        "article_closure_report.json",
        "des_results.json",
        "exact_results.json",
    ]
    manifest_mtime = (output_root / "article_closure_manifest.json").stat().st_mtime_ns
    assert manifest_mtime == max(
        path.stat().st_mtime_ns for path in output_root.iterdir()
    )

    with pytest.raises(FileExistsError, match="write-once"):
        write_article_closure_evidence(REPO_ROOT, output_root=output_root)
