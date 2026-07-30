"""Data-only structural validation for the G6-B discovery protocol bundle."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

G6B_PROTOCOL_SCHEMA_VERSION = "ims-deadlock/g6b-discovery-protocol/v1"
G6B_ESTIMAND_SCHEMA_VERSION = "ims-deadlock/g6b-estimand-schema/v1"
G6B_INDEPENDENCE_SCHEMA_VERSION = "ims-deadlock/g6b-independence-schema/v1"
G6B_NEGATIVE_CONTROLS_VERSION = "ims-deadlock/g6b-negative-controls/v1"
G6B_FAILURE_LEDGER_VERSION = "ims-deadlock/g6b-failure-ledger/v1"

_DOCUMENTS = (
    "protocol.json",
    "estimand_schema.json",
    "independence_schema.json",
    "negative_controls.json",
    "failure_ledger.json",
)
JsonObject: TypeAlias = dict[str, Any]
_PROTOCOL_KEYS = {
    "schema_version",
    "protocol_id",
    "study_role",
    "confirmation_use",
    "scientific_execution_authorized",
    "adversarial_review_status",
    "artifact_paths",
    "tracked_historical_authorities",
    "execution_boundary",
    "orthogonal_scoring_layers",
}
_COMMON_KEYS = {
    "schema_version",
    "study_role",
    "confirmation_use",
    "scientific_execution_authorized",
}
_ARTIFACT_PATHS = [
    "docs/cases/G6_B_DISCOVERY_PROTOCOL.md",
    "cases/discovery/g6b/estimand_schema.json",
    "cases/discovery/g6b/independence_schema.json",
    "cases/discovery/g6b/negative_controls.json",
    "cases/discovery/g6b/failure_ledger.json",
]
_HISTORICAL_AUTHORITIES = [
    "cases/confirmation/g4/FREEZE_ENTRY.json",
    "cases/confirmation/g4/case_manifest.json",
    "cases/confirmation/g4/random_stream_manifest.json",
    "cases/confirmation/g4/predictions.json",
    "cases/confirmation/g4/metrics_schema.json",
    "evidence/g5/G5_EXECUTION_LOCK.json",
    "evidence/g5/G5_RAW_HASH_MANIFEST.json",
    "evidence/g5/G5_RESULT_SUMMARY.json",
    "evidence/g5/G5_SCORING_ERRATUM.json",
    "evidence/g6/G6_HISTORICAL_REPLAY_FAILURE_LEDGER.json",
    "evidence/g6/G6_HISTORICAL_REPLAY_R3_REPORT.json",
]
_REMOTE_ONLY_HISTORICAL_AUTHORITIES = {
    "evidence/g5/G5_RAW_HASH_MANIFEST.json",
    "evidence/g5/G5_RESULT_SUMMARY.json",
}
_OBJECTIVE_CLASSES = [
    "D_global",
    "D_local",
    "F",
    "R_livelock",
    "R_terminal",
    "P_policy",
    "S_T",
]
_FUTURE_HASHES = [
    "state_space_hash",
    "partition_hash",
    "rate_manifest_hash",
    "stopping_rule_hash",
    "des_stopping_rule_hash",
    "estimand_id",
]
_DIMENSIONS = [
    "case_content_sha256",
    "state_snapshot_sha256",
    "route_signature_sha256",
    "parameter_tuple_sha256",
    "random_stream_manifest_sha256",
    "output_root",
    "sealed_prediction_sha256",
    "metric_schema_sha256",
]
_FUTURE_CONFIRMATION_DIMENSIONS = [
    "case_content_sha256",
    "state_snapshot_sha256",
    "route_signature_sha256",
    "parameter_tuple_sha256",
    "random_stream_manifest_sha256",
    "output_root",
    "sealed_prediction_sha256",
]
_SCORING_LAYERS = [
    "theorem_prediction_status",
    "metric_applicability",
    "metric_observations",
    "execution_status",
    "reproducibility_status",
]
_NEGATIVE_CONTROL_IDS = [
    "NC_LOCAL_BYPASS_COMPLETES",
    "NC_UNSELECTED_LIVELOCK",
    "NC_CALENDAR_EMPTY_TERMINAL",
    "NC_POLICY_ONLY_STALL",
    "NC_OR_OF_AND_FEASIBLE_BRANCH",
    "NC_AGV_RESERVATION_BOUNDARY",
    "NC_DGLOBAL_ONLY_WITH_DLOCAL",
]
_NEGATIVE_CONTROLS = [
    {
        "id": "NC_LOCAL_BYPASS_COMPLETES",
        "expected_classification": "D_local_not_admitted",
        "expected_refusal": "reachable_completion_bypass",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_UNSELECTED_LIVELOCK",
        "expected_classification": "R_livelock",
        "expected_refusal": "not_selected_bad_class",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_CALENDAR_EMPTY_TERMINAL",
        "expected_classification": "R_terminal",
        "expected_refusal": "not_resource_deadlock",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_POLICY_ONLY_STALL",
        "expected_classification": "P_policy",
        "expected_refusal": "policy_only_not_plant_partition",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_OR_OF_AND_FEASIBLE_BRANCH",
        "expected_classification": "D_local_not_admitted",
        "expected_refusal": "feasible_branch_exists",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_AGV_RESERVATION_BOUNDARY",
        "expected_classification": "boundary_or_new_versioned_target_required",
        "expected_refusal": "semantic_boundary_changed",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_DGLOBAL_ONLY_WITH_DLOCAL",
        "expected_classification": "D_global",
        "expected_refusal": "no_double_count_through_D_local",
        "not_support_if_failed": True,
    },
]


@dataclass(frozen=True)
class G6BProtocolValidation:
    valid: bool
    errors: tuple[str, ...]
    scientific_execution_authorized: bool
    adversarial_review_status: str
    bundle_hashes: dict[str, str]


def validate_g6b_protocol_bundle(root: Path) -> G6BProtocolValidation:
    """Validate the G6-B protocol foundation without scientific execution."""

    bundle_root = root.resolve()
    documents: dict[str, JsonObject] = {}
    bundle_hashes: dict[str, str] = {}
    errors: list[str] = []
    actual_json_names = sorted(
        path.name for path in bundle_root.glob("*.json") if path.is_file()
    )
    expected_names = set(_DOCUMENTS)
    actual_names = set(actual_json_names)
    missing_names = sorted(expected_names - actual_names)
    unexpected_names = sorted(actual_names - expected_names)
    if missing_names:
        errors.append(f"missing JSON documents: {missing_names}")
    if unexpected_names:
        errors.append(f"unexpected JSON documents: {unexpected_names}")

    for name in _DOCUMENTS:
        if name in missing_names:
            continue
        path = bundle_root / name
        try:
            document = _load_json_object(path)
        except ValueError as exc:
            errors.append(f"{name}: {exc}")
            continue
        documents[name] = document
        bundle_hashes[name] = _canonical_sha256(document)

    if set(documents) == set(_DOCUMENTS):
        repo_root = _repo_root_for(bundle_root)
        if repo_root is None:
            errors.append("bundle root must be <repo>/cases/discovery/g6b")
            repo_root = bundle_root
        _validate_protocol(documents["protocol.json"], repo_root, errors)
        _validate_estimand(documents["estimand_schema.json"], errors)
        _validate_independence(documents["independence_schema.json"], errors)
        _validate_negative_controls(documents["negative_controls.json"], errors)
        _validate_failure_ledger(documents["failure_ledger.json"], errors)

    protocol = documents.get("protocol.json", {})
    scientific_execution_authorized = any(
        document.get("scientific_execution_authorized") is True
        for document in documents.values()
    )
    return G6BProtocolValidation(
        valid=not errors,
        errors=tuple(errors),
        scientific_execution_authorized=scientific_execution_authorized,
        adversarial_review_status=str(protocol.get("adversarial_review_status", "")),
        bundle_hashes=bundle_hashes,
    )


def _validate_protocol(
    document: JsonObject, repo_root: Path, errors: list[str]
) -> None:
    _exact_keys(document, _PROTOCOL_KEYS, "protocol.json", errors)
    _common_contract(
        document,
        "protocol.json",
        G6B_PROTOCOL_SCHEMA_VERSION,
        errors,
    )
    _expect(
        document.get("protocol_id"),
        "G6-B-DISCOVERY-PROTOCOL-FOUNDATION",
        "protocol.json: protocol_id",
        errors,
    )
    _expect(
        document.get("adversarial_review_status"),
        "PENDING",
        "protocol.json: adversarial_review_status",
        errors,
    )
    if document.get("scientific_execution_authorized") is True:
        errors.append(
            "protocol.json: scientific execution true while review is PENDING"
        )
    _expect_path_list(
        document.get("artifact_paths"),
        _ARTIFACT_PATHS,
        "protocol.json: artifact_paths",
        repo_root,
        required_existing=set(_ARTIFACT_PATHS),
        errors=errors,
    )
    _expect_path_list(
        document.get("tracked_historical_authorities"),
        _HISTORICAL_AUTHORITIES,
        "protocol.json: tracked_historical_authorities",
        repo_root,
        required_existing=(
            set(_HISTORICAL_AUTHORITIES) - _REMOTE_ONLY_HISTORICAL_AUTHORITIES
        ),
        errors=errors,
    )
    _expect(
        document.get("execution_boundary"),
        {
            "creates_cases": False,
            "authorizes_enumeration": False,
            "authorizes_ctmc_solve": False,
            "authorizes_des_run": False,
            "requires_adversarial_review_before_scientific_execution": True,
        },
        "protocol.json: execution_boundary",
        errors,
    )
    _expect(
        document.get("orthogonal_scoring_layers"),
        {
            "required_layers": _SCORING_LAYERS,
            "metric_failure_changes_theorem_status": False,
            "exception": "only_if_frozen_falsifier_explicitly_references_metric",
        },
        "protocol.json: orthogonal_scoring_layers",
        errors,
    )


def _validate_estimand(document: JsonObject, errors: list[str]) -> None:
    _exact_keys(
        document,
        _COMMON_KEYS | {"future_required_hashes", "ontology", "exact_des_consistency"},
        "estimand_schema.json",
        errors,
    )
    _common_contract(
        document,
        "estimand_schema.json",
        G6B_ESTIMAND_SCHEMA_VERSION,
        errors,
    )
    _expect(
        document.get("future_required_hashes"),
        _FUTURE_HASHES,
        "estimand_schema.json: future_required_hashes",
        errors,
    )
    ontology = document.get("ontology")
    if not isinstance(ontology, dict):
        errors.append("estimand_schema.json: ontology must be an object")
    else:
        _expect(
            ontology,
            {
                "objective_classes": _OBJECTIVE_CLASSES,
                "D_local": {
                    "ontology": "first_hit_bad_set_not_terminal_scc",
                    "definition": (
                        "verified first-hit bad set selected by the G6-B "
                        "estimand, not a plant terminal SCC"
                    ),
                    "admission": [
                        "A2b_proof",
                        "complete_LTS_completion_nonreachability_audit",
                    ],
                },
                "success_class": "F",
                "selected_bad_classes": ["D_global", "D_local"],
                "selected_success_class": "F",
            },
            "estimand_schema.json: D_local ontology",
            errors,
        )
    _expect(
        document.get("exact_des_consistency"),
        {
            "same_target_required": True,
            "same_selected_bad_labels_required": True,
            "same_selected_success_label_required": True,
            "same_versioned_target_required": True,
        },
        "estimand_schema.json: exact_des_consistency",
        errors,
    )


def _validate_independence(document: JsonObject, errors: list[str]) -> None:
    _exact_keys(
        document,
        _COMMON_KEYS
        | {
            "canonical_hash_normalization",
            "zero_overlap_required",
            "zero_overlap_required_scope",
            "dimensions",
            "retired_authorities",
            "comparison_scopes",
            "prohibitions",
        },
        "independence_schema.json",
        errors,
    )
    _common_contract(
        document,
        "independence_schema.json",
        G6B_INDEPENDENCE_SCHEMA_VERSION,
        errors,
    )
    _expect(
        document.get("canonical_hash_normalization"),
        {
            "format": "canonical_json_sha256",
            "encoding": "utf-8",
            "sort_keys": True,
            "separators": [",", ":"],
            "duplicate_keys_allowed": False,
        },
        "independence_schema.json: canonical_hash_normalization",
        errors,
    )
    _expect(
        document.get("zero_overlap_required"), True, "independence_schema.json", errors
    )
    _expect(
        document.get("zero_overlap_required_scope"),
        "discovery_vs_retired",
        "independence_schema.json: zero_overlap_required_scope",
        errors,
    )
    _expect(
        document.get("dimensions"),
        _DIMENSIONS,
        "independence_schema.json: dimensions",
        errors,
    )
    _expect(
        document.get("retired_authorities"),
        {
            "G4": "historical_authority_only",
            "G5": "historical_authority_only",
            "G6_R": "historical_replay_authority_only",
        },
        "independence_schema.json: retired_authorities",
        errors,
    )
    _expect(
        document.get("comparison_scopes"),
        {
            "discovery_vs_retired": {
                "description": (
                    "Every G6-B discovery row is compared against retired "
                    "G4/G5/G6-R authorities."
                ),
                "compare_against": ["G4", "G5", "G6_R"],
                "zero_overlap_required": True,
                "zero_overlap_dimensions": _DIMENSIONS,
                "metric_schema_sha256_reuse": (
                    "prohibited_against_retired_authorities"
                ),
                "sealed_prediction_sha256_reuse": (
                    "prohibited_against_retired_authorities"
                ),
            },
            "discovery_internal": {
                "description": (
                    "This schema does not impose unconditional zero overlap "
                    "across all admitted G6-B discovery rows."
                ),
                "zero_overlap_required": False,
                "row_family_protocol_required": True,
                "metric_schema_sha256_reuse": (
                    "not_refused_by_this_schema_without_row_family_rule"
                ),
                "sealed_prediction_sha256_reuse": (
                    "not_refused_by_this_schema_without_row_family_rule"
                ),
            },
            "future_confirmation_vs_retired_and_discovery": {
                "description": (
                    "Future G6 confirmation rows must be independent from "
                    "retired authorities and G6-B discovery case "
                    "identity/provenance."
                ),
                "compare_against": ["G4", "G5", "G6_R", "G6_B_discovery"],
                "zero_overlap_required": True,
                "zero_overlap_dimensions": _FUTURE_CONFIRMATION_DIMENSIONS,
                "metric_schema_sha256": {
                    "zero_overlap_required": False,
                    "reuse_allowed_only_if": [
                        "explicitly_preregistered",
                        "same_target_comparability",
                        "not_derived_from_outcomes",
                    ],
                },
            },
        },
        "independence_schema.json: comparison_scopes",
        errors,
    )
    _expect(
        document.get("prohibitions"),
        {
            "rename_shift": "prohibited",
            "parameter_shift_from_retired_authority": "prohibited",
            "case_snapshot_reuse": "prohibited",
            "random_stream_reuse": "prohibited",
            "output_root_reuse": "prohibited",
            "confirmation_use": "prohibited",
        },
        "independence_schema.json: prohibitions",
        errors,
    )


def _validate_negative_controls(document: JsonObject, errors: list[str]) -> None:
    _exact_keys(
        document,
        _COMMON_KEYS | {"controls"},
        "negative_controls.json",
        errors,
    )
    _common_contract(
        document,
        "negative_controls.json",
        G6B_NEGATIVE_CONTROLS_VERSION,
        errors,
    )
    controls = document.get("controls")
    if controls != _NEGATIVE_CONTROLS:
        errors.append("negative_controls.json: controls drifted")
    if not isinstance(controls, list) or len(controls) != len(_NEGATIVE_CONTROLS):
        errors.append("negative_controls.json: controls must be the exact controls")
        return
    for expected_id, control in zip(_NEGATIVE_CONTROL_IDS, controls, strict=True):
        if not isinstance(control, dict):
            errors.append("negative_controls.json: controls entries must be objects")
            continue
        if set(control) != {
            "id",
            "expected_classification",
            "expected_refusal",
            "not_support_if_failed",
        }:
            errors.append("negative_controls.json: controls entry keys drifted")
        if control.get("id") != expected_id:
            errors.append("negative_controls.json: controls IDs drifted")
        if control.get("not_support_if_failed") is not True:
            errors.append("negative_controls.json: controls must not support if failed")
        if not isinstance(control.get("expected_classification"), str):
            errors.append("negative_controls.json: expected_classification required")
        if not isinstance(control.get("expected_refusal"), str):
            errors.append("negative_controls.json: expected_refusal required")


def _validate_failure_ledger(document: JsonObject, errors: list[str]) -> None:
    _exact_keys(
        document,
        _COMMON_KEYS | {"append_only", "entries", "empty_entries_meaning"},
        "failure_ledger.json",
        errors,
    )
    _common_contract(
        document,
        "failure_ledger.json",
        G6B_FAILURE_LEDGER_VERSION,
        errors,
    )
    _expect(
        document.get("append_only"), True, "failure_ledger.json: append_only", errors
    )
    _expect(document.get("entries"), [], "failure_ledger.json: entries", errors)
    _expect(
        document.get("empty_entries_meaning"),
        (
            "no discovery attempt has been admitted under this protocol; "
            "this does not mean no failures exist"
        ),
        "failure_ledger.json: empty_entries_meaning",
        errors,
    )


def _common_contract(
    document: JsonObject,
    label: str,
    schema_version: str,
    errors: list[str],
) -> None:
    if document.get("schema_version") != schema_version:
        errors.append(f"{label}: unsupported schema_version")
    _expect(
        document.get("study_role"), "discovery_only", f"{label}: study_role", errors
    )
    _expect(
        document.get("confirmation_use"),
        "prohibited",
        f"{label}: confirmation_use",
        errors,
    )
    _expect(
        document.get("scientific_execution_authorized"),
        False,
        f"{label}: scientific_execution_authorized",
        errors,
    )


def _exact_keys(
    document: JsonObject,
    expected_keys: set[str],
    label: str,
    errors: list[str],
) -> None:
    actual = set(document)
    missing = sorted(expected_keys - actual)
    unexpected = sorted(actual - expected_keys)
    if missing:
        errors.append(f"{label}: missing keys {missing}")
    if unexpected:
        errors.append(f"{label}: unexpected keys {unexpected}")


def _expect(actual: Any, expected: Any, label: str, errors: list[str]) -> None:
    if actual != expected:
        errors.append(f"{label} drifted")


def _expect_path_list(
    actual: Any,
    expected: list[str],
    label: str,
    repo_root: Path,
    *,
    required_existing: set[str],
    errors: list[str],
) -> None:
    if actual != expected:
        errors.append(f"{label} drifted")
    if not isinstance(actual, list) or not all(
        isinstance(path, str) for path in actual
    ):
        errors.append(f"{label} must be a list of strings")
        return
    if len(set(actual)) != len(actual):
        errors.append(f"{label} contains duplicate paths")
    for path in actual:
        if not _is_unambiguous_repo_relative_path(path):
            errors.append(f"{label} contains unsafe or ambiguous path {path!r}")
            continue
        if path in required_existing and not (repo_root / path).is_file():
            errors.append(f"{label} missing local artifact {path!r}")


def _is_unambiguous_repo_relative_path(path: str) -> bool:
    candidate = Path(path)
    if candidate.is_absolute() or "\\" in path or path.startswith("~"):
        return False
    if path == "" or path != candidate.as_posix():
        return False
    return all(part not in {"", ".", ".."} for part in candidate.parts)


def _repo_root_for(bundle_root: Path) -> Path | None:
    if (
        len(bundle_root.parents) >= 3
        and bundle_root.name == "g6b"
        and bundle_root.parent.name == "discovery"
        and bundle_root.parent.parent.name == "cases"
    ):
        return bundle_root.parents[2]
    return None


def _load_json_object(path: Path) -> JsonObject:
    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> JsonObject:
        seen: set[str] = set()
        result: JsonObject = {}
        for key, value in pairs:
            if key in seen:
                raise ValueError(f"duplicate JSON key {key!r}")
            seen.add(key)
            result[key] = value
        return result

    try:
        with path.open(encoding="utf-8") as handle:
            document = json.load(handle, object_pairs_hook=reject_duplicate_keys)
    except OSError as exc:
        raise ValueError(f"cannot read document: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError("root must be a JSON object")
    return document


def _canonical_sha256(document: JsonObject) -> str:
    canonical = json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
