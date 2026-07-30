"""Strict structural adapters and post-freeze dispatch for G4 confirmation.

Structural parsing in this module is intentionally data-only.  It constructs
typed inputs but never enumerates a state space, evaluates a comparator,
classifies a deadlock, solves a CTMC, or simulates a trajectory.  Scientific
dispatch is separated behind ``run_after_freeze`` and refuses an unsealed
bundle.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias, cast

from ims_deadlock.cases import CaseSpec, case_spec_from_json
from ims_deadlock.confirmation import (
    ConfirmationCase,
    list_confirmation_case_ids,
    load_confirmation_case,
)
from ims_deadlock.ctmc import AbsorbingCTMC
from ims_deadlock.engine import FiniteLTS
from ims_deadlock.g4_comparators import (
    CandidateMonitor,
    CRPEvidenceProfile,
    IntegerLinearInequality,
)
from ims_deadlock.g4_instances import (
    ADVERSARIAL_GENERATOR_ID,
    BIDIRECTIONAL_GENERATOR_ID,
    MEDIUM_ISLAND_GENERATOR_ID,
    AdversarialBoundaryParameters,
    BidirectionalGridCell,
    MediumIslandParameters,
)

G4_PROTOCOL_SCHEMA_VERSION = "ims-deadlock/g4-protocol-input/v1"
G4_PROTOCOL_VALIDATION_VERSION = "ims-deadlock/g4-protocol-validation/v1"
G4_PROTOCOL_RESULT_VERSION = "ims-deadlock/g4-protocol-result/v1"

_FAMILY_TO_KIND = {
    "G4-ADVERSARIAL-BOUNDARY": "adversarial_snapshot",
    "G4-B05-SUPERVISOR-COMPARATOR": "adapted_candidate_monitor_cover",
    "G4-CRP-OUTSIDE-S4PR": "crp_evidence_audit",
    "G4-CRP-S4PR-AGREE": "crp_evidence_audit",
    "G4-CRP-UNREACHABLE-CANDIDATE": "crp_evidence_audit",
    "G4-IMS-PARAMETER-GRID": "bidirectional_island_grid",
    "G4-L30-RESOURCE-BASELINE": "supplied_l30_inequalities",
    "G4-MEDIUM-ISLAND-REBUILD": "medium_island_rebuild",
    "G4-RECORDER-TARGET-QUANTIFICATION": "fixed_recorder_target",
}


@dataclass(frozen=True)
class CRPPartialDeadlockBridge:
    """Frozen map from a CRP target to an exact IMS target snapshot."""

    target_state: str
    target_snapshot: CaseSpec
    crp_resource_to_ims_resource: tuple[tuple[str, str], ...]
    comparison_rule: str


@dataclass(frozen=True)
class CRPProtocol:
    case_id: str
    family: str
    lts: FiniteLTS
    state_bound: int
    profile: CRPEvidenceProfile
    bridge: CRPPartialDeadlockBridge | None
    outside_scope_parameters: AdversarialBoundaryParameters | None


@dataclass(frozen=True)
class RecorderProtocol:
    case_id: str
    family: str
    lts: FiniteLTS
    state_bound: int
    target_state: str
    recorder_events: tuple[str, ...]
    fixed_counts: dict[str, int]


@dataclass(frozen=True)
class L30Protocol:
    case_id: str
    family: str
    capacities: dict[str, int]
    inequalities: tuple[IntegerLinearInequality, ...]
    finite_capacity_s3pr_ens3pr: bool
    inequality_provenance: str


@dataclass(frozen=True)
class B05Protocol:
    case_id: str
    family: str
    lts: FiniteLTS
    state_bound: int
    legal_states: tuple[str, ...]
    first_met_bad_states: tuple[str, ...]
    candidates: tuple[CandidateMonitor, ...]


@dataclass(frozen=True)
class GridProtocol:
    case_id: str
    family: str
    generator_id: str
    cells: tuple[BidirectionalGridCell, ...]


@dataclass(frozen=True)
class MediumProtocol:
    case_id: str
    family: str
    generator_id: str
    parameters: MediumIslandParameters


@dataclass(frozen=True)
class AdversarialProtocol:
    case_id: str
    family: str
    generator_id: str
    parameters: AdversarialBoundaryParameters


@dataclass(frozen=True)
class FrozenStreamPlan:
    master_seeds: tuple[int, ...]
    sample_count: int


G4Protocol: TypeAlias = (
    CRPProtocol
    | RecorderProtocol
    | L30Protocol
    | B05Protocol
    | GridProtocol
    | MediumProtocol
    | AdversarialProtocol
)


def parse_g4_protocol_case(case: ConfirmationCase) -> G4Protocol:
    """Parse one confirmation case into exact typed inputs without analysis."""

    return parse_g4_protocol_input(
        case.input_payload,
        case_id=case.case_id,
        expected_family=None,
    )


def validate_g4_protocol_case(case: ConfirmationCase) -> None:
    """Validate one typed protocol without executing scientific entrypoints."""

    parse_g4_protocol_case(case)


def parse_g4_protocol_input(
    input_payload: Mapping[str, object],
    *,
    case_id: str,
    expected_family: str | None,
) -> G4Protocol:
    """Parse a raw ``input_payload`` as used by the freeze checker."""

    payload = _mapping(input_payload, "input_payload")
    _require_exact_keys(
        payload,
        {
            "schema_version",
            "g4_family",
            "protocol_kind",
            "protocol_input",
        },
        "input_payload",
    )
    if payload["schema_version"] != G4_PROTOCOL_SCHEMA_VERSION:
        raise ValueError("unsupported G4 protocol input schema_version")
    family = _string(payload["g4_family"], "g4_family")
    if expected_family is not None and family != expected_family:
        raise ValueError("G4 protocol family does not match case manifest family")
    expected_kind = _FAMILY_TO_KIND.get(family)
    if expected_kind is None:
        raise ValueError(f"unsupported G4 protocol family {family!r}")
    protocol_kind = _string(payload["protocol_kind"], "protocol_kind")
    if protocol_kind != expected_kind:
        raise ValueError(
            f"G4 family {family!r} requires protocol_kind {expected_kind!r}"
        )
    protocol_input = _mapping(payload["protocol_input"], "protocol_input")

    if protocol_kind == "crp_evidence_audit":
        return _parse_crp(case_id, family, protocol_input)
    if protocol_kind == "fixed_recorder_target":
        return _parse_recorder(case_id, family, protocol_input)
    if protocol_kind == "supplied_l30_inequalities":
        return _parse_l30(case_id, family, protocol_input)
    if protocol_kind == "adapted_candidate_monitor_cover":
        return _parse_b05(case_id, family, protocol_input)
    if protocol_kind == "bidirectional_island_grid":
        return _parse_grid(case_id, family, protocol_input)
    if protocol_kind == "medium_island_rebuild":
        return _parse_medium(case_id, family, protocol_input)
    if protocol_kind == "adversarial_snapshot":
        return _parse_adversarial(case_id, family, protocol_input)
    raise AssertionError("validated protocol kind is not dispatched")


def validate_bundle_protocols(bundle_root: Path) -> dict[str, object]:
    """Structurally parse every G4 case in a bundle; never execute it."""

    root = bundle_root.resolve()
    cases_root = _cases_root_from_bundle(root)
    case_ids = list_confirmation_case_ids("g4", root=cases_root)
    for case_id in case_ids:
        validate_g4_protocol_case(
            load_confirmation_case(case_id, "g4", root=cases_root)
        )
    return {
        "schema_version": G4_PROTOCOL_VALIDATION_VERSION,
        "validation_mode": "structural_only_no_scientific_execution",
        "case_ids": list(case_ids),
        "case_count": len(case_ids),
        "valid": True,
    }


def run_after_freeze(bundle_root: Path, case_id: str) -> dict[str, object]:
    """Run one case only after the complete G4 seal validates."""

    from ims_deadlock.g4_freeze import check_g4_freeze

    root = bundle_root.resolve()
    freeze = check_g4_freeze(root)
    if freeze.status != "FROZEN":
        raise RuntimeError("G4 scientific execution requires a valid freeze seal")
    cases_root = _cases_root_from_bundle(root)
    case = load_confirmation_case(case_id, "g4", root=cases_root)
    protocol = parse_g4_protocol_case(case)
    stream_plan = _load_stream_plan(root, case_id)
    return _execute_protocol(protocol, stream_plan=stream_plan)


def main(argv: list[str] | None = None) -> int:
    """Internal structural validator and post-freeze dispatcher."""

    parser = argparse.ArgumentParser(prog="python -m ims_deadlock.g4_protocol")
    parser.add_argument("--root", type=Path, required=True)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--case")
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("case_id")
    args = parser.parse_args(argv)

    if args.command == "validate":
        if args.case is None:
            payload = validate_bundle_protocols(args.root)
        else:
            cases_root = _cases_root_from_bundle(args.root.resolve())
            case = load_confirmation_case(args.case, "g4", root=cases_root)
            protocol = parse_g4_protocol_case(case)
            payload = {
                "schema_version": G4_PROTOCOL_VALIDATION_VERSION,
                "validation_mode": "structural_only_no_scientific_execution",
                "case_ids": [protocol.case_id],
                "case_count": 1,
                "valid": True,
            }
    else:
        payload = run_after_freeze(args.root, args.case_id)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


def _parse_crp(
    case_id: str,
    family: str,
    payload: Mapping[str, Any],
) -> CRPProtocol:
    _require_exact_keys(
        payload,
        {
            "finite_lts",
            "state_bound",
            "crp_profile",
            "partial_deadlock_bridge",
            "outside_scope_generator",
        },
        "CRP protocol_input",
    )
    lts = _parse_finite_lts(payload["finite_lts"])
    state_bound = _state_bound(payload["state_bound"], lts)
    profile_payload = _mapping(payload["crp_profile"], "crp_profile")
    _require_exact_keys(
        profile_payload,
        {
            "s4pr_applicable",
            "embedding",
            "embedding_sha256",
            "crp_pairs",
            "translated_target_state",
            "external_prefix_claimed",
            "outside_s4pr_reasons",
        },
        "crp_profile",
    )
    applicable = _boolean(profile_payload["s4pr_applicable"], "s4pr_applicable")
    embedding_value = profile_payload["embedding"]
    embedding_hash = _optional_sha256(
        profile_payload["embedding_sha256"], "embedding_sha256"
    )
    if applicable:
        embedding = _mapping(embedding_value, "embedding")
        if not embedding:
            raise ValueError("applicable CRP profile requires a nonempty embedding")
        actual_hash = _canonical_json_sha256(embedding)
        if embedding_hash != actual_hash:
            raise ValueError("CRP embedding_sha256 does not match embedding")
    else:
        if embedding_value is not None or embedding_hash is not None:
            raise ValueError("outside-S4PR CRP profile must not supply an embedding")

    profile = CRPEvidenceProfile(
        s4pr_applicable=applicable,
        embedding_sha256=embedding_hash,
        crp_pairs=_string_pairs(profile_payload["crp_pairs"], "crp_pairs"),
        translated_target_state=_optional_string(
            profile_payload["translated_target_state"],
            "translated_target_state",
        ),
        external_prefix_claimed=_optional_boolean(
            profile_payload["external_prefix_claimed"],
            "external_prefix_claimed",
        ),
        outside_s4pr_reasons=_string_tuple(
            profile_payload["outside_s4pr_reasons"],
            "outside_s4pr_reasons",
        ),
    )
    bridge_value = payload["partial_deadlock_bridge"]
    bridge = (
        None
        if bridge_value is None
        else _parse_crp_bridge(
            bridge_value,
            lts=lts,
            profile=profile,
        )
    )
    if family == "G4-CRP-S4PR-AGREE" and bridge is None:
        raise ValueError("CRP agreement family requires a partial-deadlock bridge")
    if family != "G4-CRP-S4PR-AGREE" and bridge is not None:
        raise ValueError("only the CRP agreement family may supply a bridge")
    outside_scope_value = payload["outside_scope_generator"]
    outside_scope_parameters = (
        None
        if outside_scope_value is None
        else _parse_adversarial_generator(outside_scope_value)
    )
    if family == "G4-CRP-OUTSIDE-S4PR" and outside_scope_parameters is None:
        raise ValueError("outside-S4PR family requires an exact boundary generator")
    if family != "G4-CRP-OUTSIDE-S4PR" and outside_scope_parameters is not None:
        raise ValueError("only outside-S4PR may supply a boundary generator")
    return CRPProtocol(
        case_id=case_id,
        family=family,
        lts=lts,
        state_bound=state_bound,
        profile=profile,
        bridge=bridge,
        outside_scope_parameters=outside_scope_parameters,
    )


def _parse_crp_bridge(
    value: object,
    *,
    lts: FiniteLTS,
    profile: CRPEvidenceProfile,
) -> CRPPartialDeadlockBridge:
    payload = _mapping(value, "partial_deadlock_bridge")
    _require_exact_keys(
        payload,
        {
            "target_state",
            "target_snapshot",
            "crp_resource_to_ims_resource",
            "comparison_rule",
        },
        "partial_deadlock_bridge",
    )
    target_state = _string(payload["target_state"], "bridge target_state")
    if target_state not in lts.states:
        raise ValueError("bridge target_state must belong to finite_lts")
    if target_state != profile.translated_target_state:
        raise ValueError("bridge target_state must equal translated_target_state")
    snapshot = case_spec_from_json(
        _mapping(payload["target_snapshot"], "target_snapshot")
    )
    resource_map_payload = _mapping(
        payload["crp_resource_to_ims_resource"],
        "crp_resource_to_ims_resource",
    )
    resource_map = tuple(
        sorted(
            (
                _string(source, "CRP resource place"),
                _string(target, "IMS resource id"),
            )
            for source, target in resource_map_payload.items()
        )
    )
    if not resource_map:
        raise ValueError("partial-deadlock bridge requires a resource map")
    mapped_targets = tuple(target for _source, target in resource_map)
    if len(set(mapped_targets)) != len(mapped_targets):
        raise ValueError("partial-deadlock IMS resource targets must be unique")
    if not set(mapped_targets) <= set(snapshot.model.resources):
        raise ValueError("partial-deadlock bridge references unknown IMS resource")
    crp_resources = {resource for _activity, resource in profile.crp_pairs}
    if {source for source, _target in resource_map} != crp_resources:
        raise ValueError("partial-deadlock bridge must map every supplied CRP resource")
    comparison_rule = _string(payload["comparison_rule"], "comparison_rule")
    if comparison_rule != "exact_resource_set_equality":
        raise ValueError("unsupported partial-deadlock comparison_rule")
    return CRPPartialDeadlockBridge(
        target_state=target_state,
        target_snapshot=snapshot,
        crp_resource_to_ims_resource=resource_map,
        comparison_rule=comparison_rule,
    )


def _parse_recorder(
    case_id: str,
    family: str,
    payload: Mapping[str, Any],
) -> RecorderProtocol:
    _require_exact_keys(
        payload,
        {
            "finite_lts",
            "state_bound",
            "target_state",
            "recorder_events",
            "fixed_counts",
        },
        "recorder protocol_input",
    )
    lts = _parse_finite_lts(payload["finite_lts"])
    target_state = _string(payload["target_state"], "target_state")
    if target_state not in lts.states:
        raise ValueError("recorder target_state must belong to finite_lts")
    recorder_events = _string_tuple(payload["recorder_events"], "recorder_events")
    fixed_payload = _mapping(payload["fixed_counts"], "fixed_counts")
    fixed_counts = {
        _string(event, "fixed_counts event"): _nonnegative_int(
            count, f"fixed_counts[{event}]"
        )
        for event, count in fixed_payload.items()
    }
    if set(fixed_counts) != set(recorder_events):
        raise ValueError("fixed_counts keys must exactly match recorder_events")
    return RecorderProtocol(
        case_id=case_id,
        family=family,
        lts=lts,
        state_bound=_state_bound(payload["state_bound"], lts),
        target_state=target_state,
        recorder_events=recorder_events,
        fixed_counts=dict(sorted(fixed_counts.items())),
    )


def _parse_l30(
    case_id: str,
    family: str,
    payload: Mapping[str, Any],
) -> L30Protocol:
    _require_exact_keys(
        payload,
        {
            "capacities",
            "inequalities",
            "finite_capacity_s3pr_ens3pr",
            "inequality_provenance",
        },
        "L30 protocol_input",
    )
    capacities_payload = _mapping(payload["capacities"], "capacities")
    capacities = {
        _string(name, "capacity variable"): _nonnegative_int(
            value, f"capacities[{name}]"
        )
        for name, value in capacities_payload.items()
    }
    if not capacities:
        raise ValueError("L30 capacities must be nonempty")
    inequality_rows = _list(payload["inequalities"], "inequalities")
    inequalities: list[IntegerLinearInequality] = []
    for index, item in enumerate(inequality_rows):
        row = _mapping(item, f"inequality row {index}")
        _require_exact_keys(
            row,
            {"name", "coefficients", "rhs"},
            f"inequality row {index}",
        )
        inequalities.append(
            IntegerLinearInequality(
                name=_string(row["name"], f"inequality row {index} name"),
                coefficients=_integer_pairs(
                    row["coefficients"],
                    f"inequality row {index} coefficients",
                ),
                rhs=_integer(row["rhs"], f"inequality row {index} rhs"),
            )
        )
    return L30Protocol(
        case_id=case_id,
        family=family,
        capacities=dict(sorted(capacities.items())),
        inequalities=tuple(inequalities),
        finite_capacity_s3pr_ens3pr=_boolean(
            payload["finite_capacity_s3pr_ens3pr"],
            "finite_capacity_s3pr_ens3pr",
        ),
        inequality_provenance=_string(
            payload["inequality_provenance"],
            "inequality_provenance",
        ),
    )


def _parse_b05(
    case_id: str,
    family: str,
    payload: Mapping[str, Any],
) -> B05Protocol:
    _require_exact_keys(
        payload,
        {
            "finite_lts",
            "state_bound",
            "legal_states",
            "first_met_bad_states",
            "candidate_monitors",
        },
        "B05 protocol_input",
    )
    lts = _parse_finite_lts(payload["finite_lts"])
    lts_states = set(lts.states)
    legal_states = _string_tuple(payload["legal_states"], "legal_states")
    first_met_bad_states = _string_tuple(
        payload["first_met_bad_states"], "first_met_bad_states"
    )
    _require_state_subset("legal_states", legal_states, lts_states)
    _require_state_subset(
        "first_met_bad_states",
        first_met_bad_states,
        lts_states,
    )
    overlap = sorted(set(legal_states) & set(first_met_bad_states))
    if overlap:
        raise ValueError(f"legal and bad states overlap at {overlap[0]!r}")
    candidates: list[CandidateMonitor] = []
    for index, item in enumerate(_list(payload["candidate_monitors"], "candidates")):
        row = _mapping(item, f"candidate monitor {index}")
        _require_exact_keys(
            row,
            {
                "monitor_id",
                "covered_bad_states",
                "excluded_legal_states",
            },
            "candidate monitor keys",
        )
        covered_bad_states = _string_tuple(
            row["covered_bad_states"], "covered_bad_states"
        )
        excluded_legal_states = _string_tuple(
            row["excluded_legal_states"], "excluded_legal_states"
        )
        _require_state_subset(
            "covered_bad_states",
            covered_bad_states,
            lts_states,
        )
        _require_state_subset(
            "excluded_legal_states",
            excluded_legal_states,
            lts_states,
        )
        unknown_bad = sorted(set(covered_bad_states) - set(first_met_bad_states))
        if unknown_bad:
            raise ValueError(
                "covered_bad_states contains state outside first_met_bad_states: "
                f"{unknown_bad[0]!r}"
            )
        unknown_legal = sorted(set(excluded_legal_states) - set(legal_states))
        if unknown_legal:
            raise ValueError(
                "excluded_legal_states contains state outside legal_states: "
                f"{unknown_legal[0]!r}"
            )
        candidates.append(
            CandidateMonitor(
                monitor_id=_string(row["monitor_id"], "monitor_id"),
                covered_bad_states=covered_bad_states,
                excluded_legal_states=excluded_legal_states,
            )
        )
    if len({candidate.monitor_id for candidate in candidates}) != len(candidates):
        raise ValueError("candidate monitor ids must be unique")
    return B05Protocol(
        case_id=case_id,
        family=family,
        lts=lts,
        state_bound=_state_bound(payload["state_bound"], lts),
        legal_states=legal_states,
        first_met_bad_states=first_met_bad_states,
        candidates=tuple(candidates),
    )


def _parse_grid(
    case_id: str,
    family: str,
    payload: Mapping[str, Any],
) -> GridProtocol:
    _require_exact_keys(
        payload,
        {"generator_id", "cells"},
        "grid protocol_input",
    )
    generator_id = _string(payload["generator_id"], "generator_id")
    if generator_id != BIDIRECTIONAL_GENERATOR_ID:
        raise ValueError("unsupported bidirectional grid generator_id")
    cells = tuple(
        _grid_cell(item, index)
        for index, item in enumerate(_list(payload["cells"], "grid cells"))
    )
    if not cells:
        raise ValueError("G4 grid must contain at least one exact cell")
    if len({cell.cell_id for cell in cells}) != len(cells):
        raise ValueError("G4 grid cell IDs must be unique")
    return GridProtocol(
        case_id=case_id,
        family=family,
        generator_id=generator_id,
        cells=tuple(sorted(cells, key=lambda item: item.cell_id)),
    )


def _grid_cell(value: object, index: int) -> BidirectionalGridCell:
    payload = _mapping(value, f"grid cell {index}")
    keys = {
        "cell_id",
        "machine_capacity",
        "buffer_capacity",
        "agv_count",
        "forward_wip",
        "reverse_wip",
        "service_rate",
        "transfer_rate",
        "release_rate",
        "state_bound",
    }
    _require_exact_keys(payload, keys, f"grid cell {index}")
    return BidirectionalGridCell(
        cell_id=_string(payload["cell_id"], f"grid cell {index} cell_id"),
        machine_capacity=_positive_int(payload["machine_capacity"], "machine_capacity"),
        buffer_capacity=_positive_int(payload["buffer_capacity"], "buffer_capacity"),
        agv_count=_positive_int(payload["agv_count"], "agv_count"),
        forward_wip=_nonnegative_int(payload["forward_wip"], "forward_wip"),
        reverse_wip=_nonnegative_int(payload["reverse_wip"], "reverse_wip"),
        service_rate=_positive_float(payload["service_rate"], "service_rate"),
        transfer_rate=_positive_float(payload["transfer_rate"], "transfer_rate"),
        release_rate=_positive_float(payload["release_rate"], "release_rate"),
        state_bound=_positive_int(payload["state_bound"], "state_bound"),
    )


def _parse_medium(
    case_id: str,
    family: str,
    payload: Mapping[str, Any],
) -> MediumProtocol:
    _require_exact_keys(
        payload,
        {"generator_id", "parameters"},
        "medium protocol_input",
    )
    generator_id = _string(payload["generator_id"], "generator_id")
    if generator_id != MEDIUM_ISLAND_GENERATOR_ID:
        raise ValueError("unsupported medium generator_id")
    parameters_payload = _mapping(payload["parameters"], "medium parameters")
    _require_exact_keys(
        parameters_payload,
        {
            "instance_id",
            "machine_capacity",
            "buffer_capacity",
            "agv_count",
            "route_wip",
            "service_rate",
            "transfer_rate",
            "release_rate",
            "state_bound",
        },
        "medium parameters",
    )
    route_wip_payload = _mapping(parameters_payload["route_wip"], "route_wip")
    parameters = MediumIslandParameters(
        instance_id=_string(parameters_payload["instance_id"], "instance_id"),
        machine_capacity=_positive_int(
            parameters_payload["machine_capacity"], "machine_capacity"
        ),
        buffer_capacity=_positive_int(
            parameters_payload["buffer_capacity"], "buffer_capacity"
        ),
        agv_count=_positive_int(parameters_payload["agv_count"], "agv_count"),
        route_wip=tuple(
            sorted(
                (
                    _string(route_id, "route_wip route ID"),
                    _nonnegative_int(count, f"route_wip[{route_id}]"),
                )
                for route_id, count in route_wip_payload.items()
            )
        ),
        service_rate=_positive_float(
            parameters_payload["service_rate"], "service_rate"
        ),
        transfer_rate=_positive_float(
            parameters_payload["transfer_rate"], "transfer_rate"
        ),
        release_rate=_positive_float(
            parameters_payload["release_rate"], "release_rate"
        ),
        state_bound=_positive_int(parameters_payload["state_bound"], "state_bound"),
    )
    return MediumProtocol(
        case_id=case_id,
        family=family,
        generator_id=generator_id,
        parameters=parameters,
    )


def _parse_adversarial(
    case_id: str,
    family: str,
    payload: Mapping[str, Any],
) -> AdversarialProtocol:
    parameters = _parse_adversarial_generator(payload)
    return AdversarialProtocol(
        case_id=case_id,
        family=family,
        generator_id=ADVERSARIAL_GENERATOR_ID,
        parameters=parameters,
    )


def _parse_adversarial_generator(
    payload: object,
) -> AdversarialBoundaryParameters:
    payload = _mapping(payload, "adversarial generator")
    _require_exact_keys(
        payload,
        {"generator_id", "parameters"},
        "adversarial protocol_input",
    )
    generator_id = _string(payload["generator_id"], "generator_id")
    if generator_id != ADVERSARIAL_GENERATOR_ID:
        raise ValueError("unsupported adversarial generator_id")
    parameters_payload = _mapping(
        payload["parameters"],
        "adversarial parameters",
    )
    _require_exact_keys(
        parameters_payload,
        {
            "instance_id",
            "fixture_capacity",
            "cart_capacity",
            "reservation_capacity",
            "decision_rate",
            "state_bound",
        },
        "adversarial parameters",
    )
    parameters = AdversarialBoundaryParameters(
        instance_id=_string(parameters_payload["instance_id"], "instance_id"),
        fixture_capacity=_positive_int(
            parameters_payload["fixture_capacity"],
            "fixture_capacity",
        ),
        cart_capacity=_positive_int(
            parameters_payload["cart_capacity"],
            "cart_capacity",
        ),
        reservation_capacity=_positive_int(
            parameters_payload["reservation_capacity"],
            "reservation_capacity",
        ),
        decision_rate=_positive_float(
            parameters_payload["decision_rate"],
            "decision_rate",
        ),
        state_bound=_positive_int(
            parameters_payload["state_bound"],
            "state_bound",
        ),
    )
    return parameters


def _parse_finite_lts(value: object) -> FiniteLTS:
    payload = _mapping(value, "finite_lts")
    _require_exact_keys(
        payload,
        {"states", "initial_state", "marked_states", "transitions"},
        "finite_lts",
    )
    states = _string_tuple(payload["states"], "finite_lts states")
    if len(set(states)) != len(states):
        raise ValueError("finite_lts states must be unique")
    initial_state = _string(payload["initial_state"], "finite_lts initial_state")
    if initial_state not in states:
        raise ValueError("finite_lts initial_state must belong to states")
    marked_states = _string_tuple(payload["marked_states"], "finite_lts marked_states")
    if len(set(marked_states)) != len(marked_states):
        raise ValueError("finite_lts marked_states must be unique")
    if not set(marked_states) <= set(states):
        raise ValueError("finite_lts marked_states must belong to states")
    transitions: list[tuple[str, str, str, bool]] = []
    for index, item in enumerate(_list(payload["transitions"], "transitions")):
        row = _mapping(item, f"finite_lts transition {index}")
        _require_exact_keys(
            row,
            {"source", "event", "target", "controllable"},
            "finite_lts transition keys",
        )
        source = _string(row["source"], f"transition {index} source")
        event = _string(row["event"], f"transition {index} event")
        target = _string(row["target"], f"transition {index} target")
        controllable = _boolean(row["controllable"], f"transition {index} controllable")
        if source not in states or target not in states:
            raise ValueError("finite_lts transition endpoint is outside states")
        transitions.append((source, event, target, controllable))
    if len(set(transitions)) != len(transitions):
        raise ValueError("finite_lts transitions must be unique")
    return FiniteLTS(
        states=states,
        initial_state=initial_state,
        marked_states=marked_states,
        transitions=tuple(transitions),
    )


def _state_bound(value: object, lts: FiniteLTS) -> int:
    bound = _positive_int(value, "state_bound")
    if len(lts.states) > bound:
        raise ValueError("finite_lts state count exceeds state_bound")
    return bound


def _execute_protocol(
    protocol: G4Protocol,
    *,
    stream_plan: FrozenStreamPlan | None,
) -> dict[str, object]:
    from ims_deadlock.analysis import analyze_case
    from ims_deadlock.certificates import enumerate_local_blocking_certificates
    from ims_deadlock.engine import exact_max_nonblocking_supervisor
    from ims_deadlock.g4_comparators import (
        adapted_candidate_monitor_cover,
        audit_crp_evidence,
        evaluate_supplied_l30_inequalities,
        fixed_recorder_target_reachability,
    )
    from ims_deadlock.g4_instances import (
        build_adversarial_boundary_case,
        build_bidirectional_island_case,
        build_medium_island_case,
        derive_absorbing_ctmc,
    )
    from ims_deadlock.stochastic import estimate_competing_absorption

    payload: dict[str, object]
    classification: str
    if isinstance(protocol, CRPProtocol):
        audit = audit_crp_evidence(protocol.lts, protocol.profile)
        payload = {"evidence_profile_audit": audit.to_json_dict()}
        classification = audit.classification
        if protocol.bridge is not None:
            bridge = protocol.bridge
            certificate_family = enumerate_local_blocking_certificates(
                bridge.target_snapshot.model,
                bridge.target_snapshot.initial_state,
                bridge.target_snapshot.transitions,
            )
            mapped_resources = {
                target for _source, target in bridge.crp_resource_to_ims_resource
            }
            matching_kernels = tuple(
                certificate
                for certificate in certificate_family
                if set(certificate.kernel_resources) == mapped_resources
            )
            selected_kernel = matching_kernels[0] if matching_kernels else None
            selected_resources = (
                set(selected_kernel.kernel_resources)
                if selected_kernel is not None
                else set()
            )
            bridge_agrees = (
                audit.classification == "agreement" and selected_kernel is not None
            )
            classification = (
                "partial_deadlock_bridge_agreement"
                if bridge_agrees
                else "partial_deadlock_bridge_disagreement"
            )
            payload["partial_deadlock_bridge"] = {
                "comparison_rule": bridge.comparison_rule,
                "certificate_available": bool(certificate_family),
                "certificate": (
                    selected_kernel.to_json_dict()
                    if selected_kernel is not None
                    else None
                ),
                "certificate_resources": sorted(selected_resources),
                "mapped_crp_resources": sorted(mapped_resources),
                "certificate_family": [
                    _certificate_family_summary(certificate)
                    for certificate in certificate_family
                ],
                "matching_kernel_count": len(matching_kernels),
                "selected_matching_kernel": (
                    _certificate_family_summary(selected_kernel)
                    if selected_kernel is not None
                    else None
                ),
                "agrees": bridge_agrees,
            }
        if protocol.outside_scope_parameters is not None:
            boundary = build_adversarial_boundary_case(
                protocol.outside_scope_parameters
            )
            payload["outside_scope_boundary"] = {
                "generator_id": boundary.generator_id,
                "analysis": analyze_case(
                    boundary.spec,
                    max_states=boundary.state_bound,
                ),
            }
    elif isinstance(protocol, RecorderProtocol):
        recorder_observation = fixed_recorder_target_reachability(
            protocol.lts,
            target_state=protocol.target_state,
            recorder_events=protocol.recorder_events,
            fixed_counts=protocol.fixed_counts,
        )
        classification = "fixed_recorder_target_audit"
        payload = recorder_observation.to_json_dict()
    elif isinstance(protocol, L30Protocol):
        l30_observation = evaluate_supplied_l30_inequalities(
            protocol.capacities,
            protocol.inequalities,
            finite_capacity_s3pr_ens3pr=(protocol.finite_capacity_s3pr_ens3pr),
            inequality_provenance=protocol.inequality_provenance,
        )
        classification = l30_observation.classification
        payload = l30_observation.to_json_dict()
    elif isinstance(protocol, B05Protocol):
        cover_observation = adapted_candidate_monitor_cover(
            legal_states=protocol.legal_states,
            first_met_bad_states=protocol.first_met_bad_states,
            candidates=protocol.candidates,
        )
        exact_supervisor = exact_max_nonblocking_supervisor(
            protocol.lts,
            forbidden_states=protocol.first_met_bad_states,
        )
        classification = cover_observation.classification
        payload = {
            **cover_observation.to_json_dict(),
            "exact_supervisor_baseline": {
                "safe_states": list(exact_supervisor.safe_states),
                "coaccessible_states": list(exact_supervisor.coaccessible_states),
                "disabled_state_events": [
                    list(item) for item in exact_supervisor.disabled_state_events
                ],
                "initial_state_feasible": exact_supervisor.initial_state_feasible,
            },
        }
    elif isinstance(protocol, GridProtocol):
        rows = []
        for cell in protocol.cells:
            built = build_bidirectional_island_case(cell)
            derived = derive_absorbing_ctmc(built)
            rows.append(
                {
                    "cell_id": cell.cell_id,
                    "analysis": analyze_case(
                        built.spec,
                        max_states=built.state_bound,
                    ),
                    "ctmc_initial_state": derived.initial_state,
                    "terminal_classification": _terminal_classification_payload(
                        derived
                    ),
                    "estimand": derived.estimand,
                    "quantitative": derived.ctmc.solve().to_json_dict(),
                    "des_crosscheck": _des_crosscheck(
                        derived.ctmc,
                        initial_state=derived.initial_state,
                        stream_plan=stream_plan,
                        estimator=estimate_competing_absorption,
                    ),
                }
            )
        classification = "grid_executed"
        payload = {"cells": rows}
    elif isinstance(protocol, MediumProtocol):
        built = build_medium_island_case(protocol.parameters)
        derived = derive_absorbing_ctmc(built)
        classification = "medium_instance_executed"
        payload = {
            "analysis": analyze_case(built.spec, max_states=built.state_bound),
            "ctmc_initial_state": derived.initial_state,
            "terminal_classification": _terminal_classification_payload(derived),
            "estimand": derived.estimand,
            "quantitative": derived.ctmc.solve().to_json_dict(),
            "des_crosscheck": _des_crosscheck(
                derived.ctmc,
                initial_state=derived.initial_state,
                stream_plan=stream_plan,
                estimator=estimate_competing_absorption,
            ),
        }
    elif isinstance(protocol, AdversarialProtocol):
        built = build_adversarial_boundary_case(protocol.parameters)
        classification = "adversarial_boundary_executed"
        payload = {
            "analysis": analyze_case(
                built.spec,
                max_states=built.state_bound,
            )
        }
    else:
        raise AssertionError("unknown G4 protocol object")
    return {
        "schema_version": G4_PROTOCOL_RESULT_VERSION,
        "case_id": protocol.case_id,
        "family": protocol.family,
        "classification": classification,
        **payload,
    }


def _terminal_classification_payload(derived: Any) -> dict[str, object]:
    partition = derived.terminal_classification
    if partition is None:
        raise ValueError("derived G4 CTMC is missing terminal classification")
    return cast("dict[str, object]", partition.to_json_dict())


def _certificate_family_summary(certificate: Any) -> dict[str, object]:
    return {
        "kernel_jobs": sorted(certificate.kernel_jobs),
        "kernel_resources": sorted(certificate.kernel_resources),
    }


def _des_crosscheck(
    ctmc: AbsorbingCTMC,
    *,
    initial_state: str,
    stream_plan: FrozenStreamPlan | None,
    estimator: Any,
) -> dict[str, object]:
    if stream_plan is None:
        raise ValueError("stochastic G4 protocol requires a frozen stream plan")
    rows = []
    for seed in stream_plan.master_seeds:
        observation = estimator(
            ctmc,
            initial_state=initial_state,
            sample_count=stream_plan.sample_count,
            master_seed=seed,
        )
        rows.append(
            {
                "master_seed": seed,
                "sample_count": observation.sample_count,
                "deadlock_count": observation.deadlock_count,
                "deadlock_estimate": observation.deadlock_estimate,
                "wilson_95_ci": list(observation.wilson_95_ci),
                "mean_absorption_time": observation.mean_absorption_time,
                "stream_manifest": observation.stream_manifest,
            }
        )
    return {
        "replicate_stream_count": len(rows),
        "rows": rows,
    }


def _load_stream_plan(
    bundle_root: Path,
    case_id: str,
) -> FrozenStreamPlan | None:
    path = bundle_root / "random_stream_manifest.json"
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    root = _mapping(payload, "random stream manifest")
    streams = _mapping(root.get("streams_by_case"), "streams_by_case")
    row = _mapping(streams.get(case_id), f"stream plan for {case_id}")
    applicable = _boolean(row.get("applicable"), "stream applicable")
    if not applicable:
        return None
    _require_exact_keys(
        row,
        {"applicable", "derivation", "master_seeds", "replicates"},
        f"stream plan for {case_id}",
    )
    if row["derivation"] != "sha256(master_seed:replication_index)":
        raise ValueError("unsupported frozen stream derivation")
    seeds = tuple(
        _nonnegative_int(seed, "master_seed")
        for seed in _list(row["master_seeds"], "master_seeds")
    )
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("master_seeds must be a nonempty unique list")
    return FrozenStreamPlan(
        master_seeds=seeds,
        sample_count=_positive_int(row["replicates"], "replicates"),
    )


def _cases_root_from_bundle(bundle_root: Path) -> Path:
    if bundle_root.name.lower() != "g4":
        raise ValueError("G4 bundle root must end in the g4 directory")
    if bundle_root.parent.name.lower() != "confirmation":
        raise ValueError("G4 bundle root must be under cases/confirmation")
    return bundle_root.parent.parent


def _canonical_json_sha256(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a JSON array")
    return value


def _require_exact_keys(
    payload: Mapping[str, Any],
    keys: set[str],
    label: str,
) -> None:
    actual = set(payload)
    if actual != keys:
        missing = sorted(keys - actual)
        extra = sorted(actual - keys)
        raise ValueError(f"{label} keys mismatch; missing={missing}; extra={extra}")


def _require_state_subset(
    label: str,
    values: tuple[str, ...],
    lts_states: set[str],
) -> None:
    unknown = sorted(set(values) - lts_states)
    if unknown:
        raise ValueError(f"{label} references unknown LTS state {unknown[0]!r}")


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a nonempty string")
    return value


def _optional_string(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _string(value, label)


def _boolean(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a JSON boolean")
    return value


def _optional_boolean(value: object, label: str) -> bool | None:
    if value is None:
        return None
    return _boolean(value, label)


def _integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    return value


def _positive_int(value: object, label: str) -> int:
    result = _integer(value, label)
    if result <= 0:
        raise ValueError(f"{label} must be positive")
    return result


def _nonnegative_int(value: object, label: str) -> int:
    result = _integer(value, label)
    if result < 0:
        raise ValueError(f"{label} must be nonnegative")
    return result


def _positive_float(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    result = float(value)
    if result <= 0.0 or result == float("inf") or result != result:
        raise ValueError(f"{label} must be a positive finite number")
    return result


def _string_tuple(value: object, label: str) -> tuple[str, ...]:
    values = tuple(_string(item, f"{label} item") for item in _list(value, label))
    if len(set(values)) != len(values):
        raise ValueError(f"{label} must contain unique strings")
    return values


def _string_pairs(value: object, label: str) -> tuple[tuple[str, str], ...]:
    pairs: list[tuple[str, str]] = []
    for index, item in enumerate(_list(value, label)):
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError(f"{label} row {index} must contain exactly two strings")
        pairs.append(
            (
                _string(item[0], f"{label} row {index} left"),
                _string(item[1], f"{label} row {index} right"),
            )
        )
    return tuple(pairs)


def _integer_pairs(value: object, label: str) -> tuple[tuple[str, int], ...]:
    pairs: list[tuple[str, int]] = []
    for index, item in enumerate(_list(value, label)):
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError(f"{label} row {index} must contain name and coefficient")
        pairs.append(
            (
                _string(item[0], f"{label} row {index} variable"),
                _integer(item[1], f"{label} row {index} coefficient"),
            )
        )
    return tuple(pairs)


def _optional_sha256(value: object, label: str) -> str | None:
    if value is None:
        return None
    digest = _string(value, label)
    if (
        len(digest) != 64
        or digest.lower() != digest
        or any(character not in "0123456789abcdef" for character in digest)
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")
    return digest


if __name__ == "__main__":
    raise SystemExit(main())
