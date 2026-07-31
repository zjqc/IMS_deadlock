import json
from pathlib import Path
from typing import Any, cast

import pytest

from ims_deadlock.confirmation import ConfirmationCase, load_confirmation_case
from ims_deadlock.g4_instances import (
    AdversarialBoundaryParameters,
    BidirectionalGridCell,
    BuiltG4Case,
    MediumIslandParameters,
    build_adversarial_boundary_case,
    build_bidirectional_island_case,
    build_medium_island_case,
    derive_absorbing_ctmc,
)
from ims_deadlock.g4_protocol import (
    B05Protocol,
    CRPPartialDeadlockBridge,
    CRPProtocol,
    FrozenStreamPlan,
    GridProtocol,
    MediumProtocol,
    RecorderProtocol,
    _execute_protocol,
    parse_g4_protocol_case,
    run_after_freeze,
    validate_g4_protocol_case,
)
from ims_deadlock.terminal_classes import (
    G6_CTM_GENERATOR_PROVENANCE,
    TerminalPartitionError,
    VersionedEstimandSpec,
)


def _finite_lts_payload() -> dict[str, object]:
    return {
        "states": ["s0", "s1", "s_dead", "s_done"],
        "initial_state": "s0",
        "marked_states": ["s_done"],
        "transitions": [
            {
                "source": "s0",
                "event": "load_left",
                "target": "s1",
                "controllable": True,
            },
            {
                "source": "s1",
                "event": "block_pair",
                "target": "s_dead",
                "controllable": False,
            },
            {
                "source": "s1",
                "event": "finish",
                "target": "s_done",
                "controllable": False,
            },
        ],
    }


def _confirmation_case(
    case_id: str,
    family: str,
    protocol_kind: str,
    protocol_input: dict[str, object],
) -> ConfirmationCase:
    return ConfirmationCase(
        case_id=case_id,
        family="G4",
        held_out=True,
        status="PREREGISTERED",
        protocol="g4_confirmation_freeze_v1",
        contamination={},
        input_payload={
            "schema_version": "ims-deadlock/g4-protocol-input/v1",
            "g4_family": family,
            "protocol_kind": protocol_kind,
            "protocol_input": protocol_input,
        },
        expected_outputs_schema={"required_fields": ["classification"]},
    )


def _snapshot_payload() -> dict[str, object]:
    return {
        "schema_version": "ims-deadlock/case/v1",
        "case_id": "G4_DEV_SNAPSHOT",
        "title": "development-only target snapshot",
        "status": "DEVELOPMENT",
        "model": {
            "id": "g4-dev-snapshot",
            "resources": [
                {"id": "r_left", "capacity": 1, "kind": "machine"},
                {"id": "r_right", "capacity": 1, "kind": "machine"},
            ],
            "jobs": ["j_left", "j_right"],
        },
        "initial_state": {
            "id": "dead",
            "holds": [
                {"job_id": "j_left", "resource_id": "r_left", "units": 1},
                {"job_id": "j_right", "resource_id": "r_right", "units": 1},
            ],
            "requests": {
                "j_left": [[{"resource_id": "r_right", "units": 1}]],
                "j_right": [[{"resource_id": "r_left", "units": 1}]],
            },
            "completed_jobs": [],
            "stable": True,
            "complete": False,
            "event_calendar_empty": True,
            "mode_by_job": {
                "j_left": "blocked",
                "j_right": "blocked",
            },
            "stage_by_job": {
                "j_left": "blocked",
                "j_right": "blocked",
            },
        },
        "transitions": [],
        "calendar": [],
        "notes": ["development fixture"],
    }


def test_parse_crp_protocol_binds_exact_comparator_and_bridge_inputs() -> None:
    embedding = {
        "places": ["p_left", "p_right"],
        "resource_places": ["p_r_left", "p_r_right"],
        "transitions": ["t_left", "t_right"],
    }
    case = _confirmation_case(
        "G4_DEV_CRP",
        "G4-CRP-S4PR-AGREE",
        "crp_evidence_audit",
        {
            "finite_lts": _finite_lts_payload(),
            "state_bound": 32,
            "crp_profile": {
                "s4pr_applicable": True,
                "embedding": embedding,
                "embedding_sha256": _canonical_sha(embedding),
                "crp_pairs": [
                    ["p_left", "p_r_right"],
                    ["p_right", "p_r_left"],
                ],
                "translated_target_state": "s_dead",
                "external_prefix_claimed": True,
                "outside_s4pr_reasons": [],
            },
            "partial_deadlock_bridge": {
                "target_state": "s_dead",
                "target_snapshot": _snapshot_payload(),
                "crp_resource_to_ims_resource": {
                    "p_r_left": "r_left",
                    "p_r_right": "r_right",
                },
                "comparison_rule": "exact_resource_set_equality",
            },
            "outside_scope_generator": None,
        },
    )

    parsed = parse_g4_protocol_case(case)

    assert isinstance(parsed, CRPProtocol)
    assert parsed.lts.transitions[0] == ("s0", "load_left", "s1", True)
    assert parsed.profile.external_prefix_claimed is True
    assert parsed.bridge is not None
    assert parsed.bridge.target_snapshot.model.id == "g4-dev-snapshot"


def test_crp_bridge_uses_local_certificate_family_for_g4_agree_target() -> None:
    case = load_confirmation_case("G4_CRP_S4PR_AGREE", "g4")
    protocol = parse_g4_protocol_case(case)

    result = _execute_protocol(protocol, stream_plan=None)

    assert result["classification"] == "partial_deadlock_bridge_agreement"
    audit = result["evidence_profile_audit"]
    assert isinstance(audit, dict)
    assert audit["independent_witness"] == [
        "admit_left",
        "admit_right",
        "left_service_complete",
        "right_service_complete",
    ]
    bridge = result["partial_deadlock_bridge"]
    assert isinstance(bridge, dict)
    assert bridge["certificate_available"] is True
    assert bridge["certificate_resources"] == ["cell_x", "cell_y"]
    assert bridge["mapped_crp_resources"] == ["cell_x", "cell_y"]
    assert bridge["matching_kernel_count"] == 1
    assert bridge["certificate_family"] == [
        {
            "kernel_jobs": ["left_job", "right_job"],
            "kernel_resources": ["cell_x", "cell_y"],
        }
    ]
    selected_kernel = bridge["selected_matching_kernel"]
    assert isinstance(selected_kernel, dict)
    assert selected_kernel["kernel_resources"] == [
        "cell_x",
        "cell_y",
    ]
    certificate = bridge["certificate"]
    assert isinstance(certificate, dict)
    assert certificate["scope"] == "local"
    assert bridge["agrees"] is True


def test_crp_bridge_reports_nonmatching_local_family_without_false_agreement() -> None:
    case = load_confirmation_case("G4_CRP_S4PR_AGREE", "g4")
    protocol = parse_g4_protocol_case(case)
    assert isinstance(protocol, CRPProtocol)
    assert protocol.bridge is not None
    nonmatching_bridge = CRPPartialDeadlockBridge(
        target_state=protocol.bridge.target_state,
        target_snapshot=protocol.bridge.target_snapshot,
        crp_resource_to_ims_resource=(("p_r_x", "cell_x"), ("p_r_y", "free_fixture")),
        comparison_rule=protocol.bridge.comparison_rule,
    )
    nonmatching_protocol = CRPProtocol(
        case_id=protocol.case_id,
        family=protocol.family,
        lts=protocol.lts,
        state_bound=protocol.state_bound,
        profile=protocol.profile,
        bridge=nonmatching_bridge,
        outside_scope_parameters=protocol.outside_scope_parameters,
    )

    result = _execute_protocol(nonmatching_protocol, stream_plan=None)

    assert result["classification"] == "partial_deadlock_bridge_disagreement"
    bridge = result["partial_deadlock_bridge"]
    assert isinstance(bridge, dict)
    assert bridge["certificate_available"] is True
    assert bridge["matching_kernel_count"] == 0
    assert bridge["selected_matching_kernel"] is None
    assert bridge["mapped_crp_resources"] == ["cell_x", "free_fixture"]
    assert bridge["agrees"] is False


def test_protocol_rejects_legacy_lts_fields_and_missing_controllability() -> None:
    case = _confirmation_case(
        "G4_DEV_RECORDER",
        "G4-RECORDER-TARGET-QUANTIFICATION",
        "fixed_recorder_target",
        {
            "finite_lts": {
                "states": ["s0", "s1"],
                "initial_state": "s0",
                "marked_states": ["s1"],
                "transitions": [{"from": "s0", "event": "go", "to": "s1"}],
            },
            "state_bound": 4,
            "target_state": "s1",
            "recorder_events": ["go"],
            "fixed_counts": {"go": 1},
        },
    )

    with pytest.raises(ValueError, match="finite_lts transition keys"):
        parse_g4_protocol_case(case)


def test_parse_recorder_and_b05_protocols_use_exact_api_field_names() -> None:
    recorder = _confirmation_case(
        "G4_DEV_RECORDER",
        "G4-RECORDER-TARGET-QUANTIFICATION",
        "fixed_recorder_target",
        {
            "finite_lts": _finite_lts_payload(),
            "state_bound": 32,
            "target_state": "s_done",
            "recorder_events": ["finish"],
            "fixed_counts": {"finish": 1},
        },
    )
    b05 = _confirmation_case(
        "G4_DEV_B05",
        "G4-B05-SUPERVISOR-COMPARATOR",
        "adapted_candidate_monitor_cover",
        {
            "finite_lts": _finite_lts_payload(),
            "state_bound": 32,
            "legal_states": ["s0", "s1", "s_done"],
            "first_met_bad_states": ["s_dead"],
            "candidate_monitors": [
                {
                    "monitor_id": "m1",
                    "covered_bad_states": ["s_dead"],
                    "excluded_legal_states": [],
                }
            ],
        },
    )

    parsed_recorder = parse_g4_protocol_case(recorder)
    parsed_b05 = parse_g4_protocol_case(b05)

    assert isinstance(parsed_recorder, RecorderProtocol)
    assert parsed_recorder.fixed_counts == {"finish": 1}
    assert isinstance(parsed_b05, B05Protocol)
    assert parsed_b05.candidates[0].covered_bad_states == ("s_dead",)

    legacy_value = b05.input_payload["protocol_input"]
    assert isinstance(legacy_value, dict)
    legacy = dict(legacy_value)
    legacy["candidate_monitors"] = [
        {
            "monitor_id": "m1",
            "covers_bad_states": ["s_dead"],
            "excluded_legal_states": [],
        }
    ]
    with pytest.raises(ValueError, match="candidate monitor keys"):
        parse_g4_protocol_case(
            _confirmation_case(
                "G4_DEV_B05",
                "G4-B05-SUPERVISOR-COMPARATOR",
                "adapted_candidate_monitor_cover",
                legacy,
            )
        )


def test_b05_protocol_rejects_states_outside_the_declared_lts() -> None:
    protocol_input = {
        "finite_lts": _finite_lts_payload(),
        "state_bound": 32,
        "legal_states": ["s0", "NOT_IN_LTS"],
        "first_met_bad_states": ["s_dead"],
        "candidate_monitors": [
            {
                "monitor_id": "m1",
                "covered_bad_states": ["s_dead"],
                "excluded_legal_states": [],
            }
        ],
    }

    with pytest.raises(ValueError, match="legal_states references unknown LTS state"):
        parse_g4_protocol_case(
            _confirmation_case(
                "G4_DEV_B05",
                "G4-B05-SUPERVISOR-COMPARATOR",
                "adapted_candidate_monitor_cover",
                protocol_input,
            )
        )

    protocol_input["legal_states"] = ["s0"]
    protocol_input["candidate_monitors"] = [
        {
            "monitor_id": "m1",
            "covered_bad_states": ["BAD_NOT_IN_LTS"],
            "excluded_legal_states": [],
        }
    ]
    with pytest.raises(
        ValueError,
        match="covered_bad_states references unknown LTS state",
    ):
        parse_g4_protocol_case(
            _confirmation_case(
                "G4_DEV_B05",
                "G4-B05-SUPERVISOR-COMPARATOR",
                "adapted_candidate_monitor_cover",
                protocol_input,
            )
        )


def test_grid_protocol_freezes_capacity_wip_routes_agv_rates_and_cells() -> None:
    case = _confirmation_case(
        "G4_DEV_GRID",
        "G4-IMS-PARAMETER-GRID",
        "bidirectional_island_grid",
        {
            "generator_id": "bidirectional_bas_v1",
            "cells": [
                {
                    "cell_id": "DEV_CELL",
                    "machine_capacity": 1,
                    "buffer_capacity": 2,
                    "agv_count": 1,
                    "forward_wip": 2,
                    "reverse_wip": 1,
                    "service_rate": 1.25,
                    "transfer_rate": 0.75,
                    "release_rate": 0.5,
                    "state_bound": 512,
                }
            ],
        },
    )

    parsed = parse_g4_protocol_case(case)

    assert isinstance(parsed, GridProtocol)
    assert parsed.cells[0].total_wip == 3
    assert parsed.cells[0].route_mix == (2, 1)
    assert parsed.cells[0].agv_count == 1
    assert parsed.cells[0].event_rates == {
        "release": 0.5,
        "service": 1.25,
        "transfer": 0.75,
    }


def test_development_builders_are_deterministic_and_preserve_frozen_dimensions() -> (
    None
):
    grid_cell = BidirectionalGridCell(
        cell_id="DEV_GRID",
        machine_capacity=1,
        buffer_capacity=2,
        agv_count=1,
        forward_wip=1,
        reverse_wip=1,
        service_rate=1.0,
        transfer_rate=0.8,
        release_rate=0.4,
        state_bound=256,
    )
    medium = MediumIslandParameters(
        instance_id="DEV_MEDIUM",
        machine_capacity=1,
        buffer_capacity=2,
        agv_count=1,
        route_wip=(("ABG", 1), ("BAG", 1), ("AG", 1)),
        service_rate=1.0,
        transfer_rate=0.7,
        release_rate=0.3,
        state_bound=2048,
    )

    first_grid = build_bidirectional_island_case(grid_cell)
    second_grid = build_bidirectional_island_case(grid_cell)
    built_medium = build_medium_island_case(medium)

    assert first_grid.spec.to_json_dict() == second_grid.spec.to_json_dict()
    assert first_grid.event_rates == second_grid.event_rates
    assert first_grid.spec.model.resources["agv"].capacity == 1
    assert len(first_grid.spec.model.jobs) == grid_cell.total_wip
    assert set(built_medium.spec.model.jobs) == {"ABG_01", "AG_01", "BAG_01"}
    assert built_medium.spec.model.resources["agv"].capacity == 1


def test_development_grid_derives_case_bound_absorbing_ctmc() -> None:
    cell = BidirectionalGridCell(
        cell_id="DEV_CTM",
        machine_capacity=1,
        buffer_capacity=1,
        agv_count=1,
        forward_wip=1,
        reverse_wip=0,
        service_rate=1.0,
        transfer_rate=0.8,
        release_rate=0.4,
        state_bound=128,
    )
    built = build_bidirectional_island_case(cell)

    derived = derive_absorbing_ctmc(built)
    exact = derived.ctmc.solve()

    assert derived.ctmc.case_derived is True
    assert derived.initial_state in derived.ctmc.transient_states
    assert derived.completion_state_ids
    assert not derived.truncated
    assert exact.probability_bounds_valid is True
    assert derived.ctmc.generator_provenance == G6_CTM_GENERATOR_PROVENANCE
    assert derived.terminal_classification is not None
    assert derived.estimand is not None
    assert "hashes" in derived.estimand


def test_g03_balanced_tight_derives_with_local_first_hit_estimand() -> None:
    case = load_confirmation_case("G4_IMS_PARAMETER_GRID", "g4")
    protocol = parse_g4_protocol_case(case)
    assert isinstance(protocol, GridProtocol)
    cell = next(item for item in protocol.cells if item.cell_id == "G03_BALANCED_TIGHT")
    built = build_bidirectional_island_case(cell)

    derived = derive_absorbing_ctmc(built)
    solved = derived.ctmc.solve()

    assert derived.local_deadlock_state_ids
    assert set(derived.deadlock_state_ids) == set(derived.local_deadlock_state_ids)
    assert solved.probability_bounds_valid is True


def test_medium_protocol_payload_includes_terminal_classification_and_estimand() -> (
    None
):
    case = load_confirmation_case("G4_MEDIUM_ISLAND_REBUILD", "g4")
    protocol = parse_g4_protocol_case(case)
    assert isinstance(protocol, MediumProtocol)

    result = _execute_protocol(
        protocol,
        stream_plan=FrozenStreamPlan(master_seeds=(11,), sample_count=8),
    )

    assert "terminal_classification" in result
    classification = result["terminal_classification"]
    assert isinstance(classification, dict)
    assert classification["classification_version"] == (
        "ims-deadlock/g6-terminal-stopping-partition/v3"
    )
    classes = cast(dict[str, object], classification["classes"])
    assert "P_policy" not in classes
    assert "S_T" not in classes
    assert classification["policy_analysis_classes"] == {"P_policy": []}
    derived_state_sets = cast(dict[str, object], classification["derived_state_sets"])
    assert set(derived_state_sets) >= {"S_reach", "S_T"}
    provenance = cast(dict[str, object], classification["lts_provenance_audit"])
    assert provenance["method"] == (
        "deterministic_reenumeration_from_stable_initial_v1"
    )
    assert provenance["verified"] is True
    assert cast(int, provenance["state_count"]) > 0
    assert cast(int, provenance["plant_arc_count"]) > 0
    estimand = result["estimand"]
    assert isinstance(estimand, dict)
    assert estimand["selected_bad_classes"] == ["D_global", "D_local"]
    hashes = cast(dict[str, object], estimand["hashes"])
    assert "estimand_id" in hashes
    des_crosscheck = cast(dict[str, object], result["des_crosscheck"])
    assert des_crosscheck["replicate_stream_count"] == 1


def test_d_global_only_estimand_refuses_model_with_local_core() -> None:
    case = load_confirmation_case("G4_IMS_PARAMETER_GRID", "g4")
    protocol = parse_g4_protocol_case(case)
    assert isinstance(protocol, GridProtocol)
    cell = next(item for item in protocol.cells if item.cell_id == "G03_BALANCED_TIGHT")

    with pytest.raises(TerminalPartitionError) as excinfo:
        derive_absorbing_ctmc(
            build_bidirectional_island_case(cell),
            estimand_spec=VersionedEstimandSpec(selected_bad_classes=("D_global",)),
        )

    assert excinfo.value.code == "d_global_only_estimand_refuses_local_core"
    assert excinfo.value.details["selected_bad_classes"] == ["D_global"]


def test_ctmc_derivation_refuses_a_truncated_generated_lts() -> None:
    cell = BidirectionalGridCell(
        cell_id="DEV_TRUNCATED",
        machine_capacity=1,
        buffer_capacity=1,
        agv_count=1,
        forward_wip=1,
        reverse_wip=1,
        service_rate=1.0,
        transfer_rate=0.8,
        release_rate=0.4,
        state_bound=1,
    )

    with pytest.raises(ValueError, match="exceeds the frozen state_bound"):
        derive_absorbing_ctmc(build_bidirectional_island_case(cell))


def test_ctmc_derivation_refuses_an_absorbing_initial_state() -> None:
    parameters = AdversarialBoundaryParameters(
        instance_id="DEV_INITIAL_ABSORPTION",
        fixture_capacity=2,
        cart_capacity=1,
        reservation_capacity=1,
        decision_rate=0.5,
        state_bound=64,
    )

    with pytest.raises(ValueError, match="requires a transient initial state"):
        derive_absorbing_ctmc(build_adversarial_boundary_case(parameters))


def test_ctmc_derivation_refuses_a_missing_frozen_event_rate() -> None:
    cell = BidirectionalGridCell(
        cell_id="DEV_MISSING_RATE",
        machine_capacity=1,
        buffer_capacity=1,
        agv_count=1,
        forward_wip=1,
        reverse_wip=0,
        service_rate=1.0,
        transfer_rate=0.8,
        release_rate=0.4,
        state_bound=128,
    )
    built = build_bidirectional_island_case(cell)
    missing_rates = BuiltG4Case(
        spec=built.spec,
        event_rates={},
        state_bound=built.state_bound,
        generator_id=built.generator_id,
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        derive_absorbing_ctmc(missing_rates)

    assert excinfo.value.code == "missing_event_rate"


def test_adversarial_generator_materializes_or_and_capacity_and_reservations() -> None:
    parameters = AdversarialBoundaryParameters(
        instance_id="DEV_BOUNDARY",
        fixture_capacity=2,
        cart_capacity=1,
        reservation_capacity=1,
        decision_rate=0.5,
        state_bound=64,
    )

    built = build_adversarial_boundary_case(parameters)
    requests = built.spec.initial_state.requests

    assert len(requests["left"]) == 2
    assert all(len(alternative.demands) == 2 for alternative in requests["left"])
    assert built.spec.model.resources["fixture_a"].capacity == 2
    assert built.spec.model.resources["cart_left"].kind == "agv"
    assert built.spec.model.resources["reserve_a"].kind == "reservation"
    assert {
        transition.target_mode
        for transition in built.spec.transitions
        if transition.job_id == "left"
    } == {"left_branch_cross", "left_branch_inspection"}


def test_structural_validation_does_not_call_scientific_entrypoints(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _confirmation_case(
        "G4_DEV_RECORDER",
        "G4-RECORDER-TARGET-QUANTIFICATION",
        "fixed_recorder_target",
        {
            "finite_lts": _finite_lts_payload(),
            "state_bound": 32,
            "target_state": "s_done",
            "recorder_events": ["finish"],
            "fixed_counts": {"finish": 1},
        },
    )

    def forbidden(*_args: object, **_kwargs: object) -> Any:
        raise AssertionError("structural validation executed held-out science")

    monkeypatch.setattr(
        "ims_deadlock.g4_comparators.fixed_recorder_target_reachability",
        forbidden,
    )
    monkeypatch.setattr("ims_deadlock.analysis.enumerate_stable_lts", forbidden)
    monkeypatch.setattr("ims_deadlock.analysis.analyze_case", forbidden)

    validate_g4_protocol_case(case)


def test_post_freeze_dispatch_refuses_an_unsealed_bundle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "cases" / "confirmation" / "g4"
    root.mkdir(parents=True)

    def forbidden(*_args: object, **_kwargs: object) -> Any:
        raise AssertionError("unsealed dispatch reached scientific execution")

    monkeypatch.setattr("ims_deadlock.analysis.analyze_case", forbidden)
    monkeypatch.setattr("ims_deadlock.analysis.enumerate_stable_lts", forbidden)
    monkeypatch.setattr(
        "ims_deadlock.g4_comparators.audit_crp_evidence",
        forbidden,
    )

    with pytest.raises(RuntimeError, match="requires a valid freeze seal"):
        run_after_freeze(root, "G4_DEV")


def _canonical_sha(payload: object) -> str:
    import hashlib

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
