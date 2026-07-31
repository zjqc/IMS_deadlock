import json
import shutil
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pytest

from ims_deadlock.g6b_row_family_protocol import (
    validate_g6b_row_family_bundle,
)

BUNDLE = Path("cases/discovery/g6b/row_families/structural_discovery_v1")
_NAMES = (
    "row_family_protocol.json",
    "identity_schema.json",
    "row_family_matrix.json",
    "reuse_matrix.json",
    "overlap_report_schema.json",
    "runtime_lock_schema.json",
    "review_state.json",
    "failure_ledger.json",
)
_RETIRED_DIMENSIONS = (
    "case_content_sha256",
    "state_snapshot_sha256",
    "route_signature_sha256",
    "parameter_tuple_sha256",
    "random_stream_manifest_sha256",
    "output_root",
    "sealed_prediction_sha256",
    "metric_schema_sha256",
)
_FUTURE_CONFIRMATION_DIMENSIONS = (
    "case_content_sha256",
    "state_snapshot_sha256",
    "route_signature_sha256",
    "parameter_tuple_sha256",
    "random_stream_manifest_sha256",
    "output_root",
    "sealed_prediction_sha256",
)
_CONFIRMATION_METRIC_FLAGS = (
    "explicitly_preregistered",
    "same_target_comparability",
    "not_derived_from_outcomes",
)
_AUTHORITY_LOCK_REQUIRED_FIELDS = (
    "target_path",
    "target_branch",
    "target_head",
    "target_dirty_state",
    "upstream_ahead_behind",
    "worktree_identity",
    "repo_remote_url",
    "source_tree_hash",
    "sealed_case_artifact_hashes",
    "retired_authority_paths_and_hashes",
)
_RUNTIME_LOCK_REQUIRED_FIELDS = (
    "python_executable",
    "python_version",
    "package_lock_or_environment_hash",
    "validation_commands",
    "validation_results",
    "runtime_lock_created_at_utc",
    "science_execution_authorized_by_artifact",
    "pythondontwritebytecode_or_cache_policy",
    "output_root_policy",
)
_EXPECTED_OVERLAP_REPORT_SCHEMA = {
    "schema_version": "ims-deadlock/g6b-row-family-overlap-schema/v1",
    "study_role": "discovery_only",
    "confirmation_use": "prohibited",
    "scientific_execution_authorized": False,
    "case_creation_authorized": False,
    "report_role": "schema_only",
    "actual_overlap_checked": False,
    "actual_overlap_report_available": False,
    "schema_only_overlap_report_cannot_authorize_execution": True,
    "missing_actual_overlap_report_blocks_execution": True,
    "retired_authorities": ["G4", "G5", "G6_R"],
    "retired_dimensions": list(_RETIRED_DIMENSIONS),
    "future_confirmation_dimensions": list(_FUTURE_CONFIRMATION_DIMENSIONS),
    "future_confirmation_metric_reuse": {
        _CONFIRMATION_METRIC_FLAGS[0]: True,
        _CONFIRMATION_METRIC_FLAGS[1]: True,
        _CONFIRMATION_METRIC_FLAGS[2]: True,
    },
    "required_lock_before_actual_report": "overlap_authority_lock",
    "remote_only_G5_authority_paths": [
        "evidence/g5/G5_RAW_HASH_MANIFEST.json",
        "evidence/g5/G5_RESULT_SUMMARY.json",
    ],
    "local_absence_is_nonoverlap_evidence": False,
    "later_actual_report_required_fields": [
        "locked_target_identity",
        "retired_authority_hashes",
        "discovery_case_unit_hashes",
        "per_dimension_results",
        "per_unit_results",
        "refusal_entries",
    ],
}
_EXPECTED_RUNTIME_LOCK_SCHEMA = {
    "schema_version": "ims-deadlock/g6b-row-family-runtime-lock-schema/v1",
    "study_role": "discovery_only",
    "confirmation_use": "prohibited",
    "scientific_execution_authorized": False,
    "case_creation_authorized": False,
    "overlap_authority_lock": {
        "status": "required_later",
        "authorizes_execution": False,
        "required_fields": list(_AUTHORITY_LOCK_REQUIRED_FIELDS),
    },
    "execution_runtime_lock": {
        "status": "required_later",
        "allowed_only_after": "ACTUAL_OVERLAP_REPORT_PASSED",
        "authorizes_execution": False,
        "required_fields": list(_RUNTIME_LOCK_REQUIRED_FIELDS),
    },
}
_TASK5_MATRIX_ERROR = "row_family_matrix.json: document must match"


def _matrix() -> dict[str, Any]:
    return _load(BUNDLE, "row_family_matrix.json")


def _control_field_cases() -> Iterable[Any]:
    controls = _matrix()["negative_control_families"]
    field_paths = (
        ("structural_family_id",),
        ("required_negative_control_id",),
        ("hypothesis_attacked",),
        ("admission_route_allowed",),
        ("expected_classification",),
        ("expected_refusal",),
        ("expected_refusal_or_classification",),
        ("expected_refusal_or_classification", "classification"),
        ("expected_refusal_or_classification", "refusal"),
        ("not_support_if_failed",),
        ("supports_hypothesis_if_failed",),
        ("case_creation_authorized",),
        ("observed_outcome",),
    )
    for control_index, control in enumerate(controls):
        control_id = control["required_negative_control_id"]
        for field_path in field_paths:
            path_id = "_".join(field_path)
            yield pytest.param(
                control_index,
                field_path,
                id=f"control_{control_id}_{path_id}",
            )


def _probe_removal_cases() -> Iterable[Any]:
    for probe in _matrix()["discovery_probes"]:
        yield pytest.param(probe["role"], id=f"probe_remove_{probe['role']}")


def _probe_falsifier_cases() -> Iterable[Any]:
    for probe in _matrix()["discovery_probes"]:
        for falsifier in probe["falsifiers"]:
            yield pytest.param(
                probe["role"],
                falsifier,
                id=f"probe_remove_{probe['role']}_{falsifier}",
            )


def _probe_outcome_neutrality_cases() -> Iterable[Any]:
    fields = (
        "favorable_outcome_frozen",
        "case_creation_authorized",
        "observed_outcome",
    )
    for probe in _matrix()["discovery_probes"]:
        for field in fields:
            yield pytest.param(
                probe["role"],
                field,
                id=f"probe_outcome_neutral_{probe['role']}_{field}",
            )


def _drift_value(value: Any) -> Any:
    if isinstance(value, str):
        return "TASK5_DETERMINISTIC_DRIFT"
    if isinstance(value, bool):
        return not value
    if value is None:
        return "TASK5_NON_NULL_OBSERVED_OUTCOME"
    if isinstance(value, dict):
        return {
            "classification": "TASK5_DETERMINISTIC_DRIFT",
            "refusal": "TASK5_DETERMINISTIC_DRIFT",
        }
    if isinstance(value, list):
        return ["TASK5_DETERMINISTIC_DRIFT"]
    raise AssertionError(f"unsupported drift value: {value!r}")


def _set_path(document: dict[str, Any], path: tuple[str, ...]) -> None:
    target = document
    for key in path[:-1]:
        target = target[key]
        assert isinstance(target, dict)
    target[path[-1]] = _drift_value(target[path[-1]])


def _row_family_matrix_from(bundle: Path) -> dict[str, Any]:
    return _load(bundle, "row_family_matrix.json")


def _copy_bundle(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    target = repo / "cases/discovery/g6b/row_families/structural_discovery_v1"
    shutil.copytree(BUNDLE, target)
    design = Path("docs/superpowers/specs/2026-07-31-g6b-row-family-design.md")
    copied_design = repo / design
    copied_design.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(design, copied_design)
    return target


def _load(bundle: Path, name: str) -> dict[str, Any]:
    loaded = json.loads((bundle / name).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _write(bundle: Path, name: str, value: dict[str, Any]) -> None:
    (bundle / name).write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _assert_invalid(bundle: Path, text: str) -> None:
    result = validate_g6b_row_family_bundle(bundle)
    assert result.valid is False
    assert any(text in error for error in result.errors), result.errors


def _mutate_list(value: list[str], item: str, operation: str) -> list[str]:
    mutated = list(value)
    index = mutated.index(item)
    if operation == "remove":
        mutated.pop(index)
    elif operation == "duplicate":
        mutated.insert(index, item)
    elif operation == "replace":
        mutated[index] = "UNEXPECTED_TASK4_SENTINEL"
    else:  # pragma: no cover - parameterization guard
        raise AssertionError(operation)
    return mutated


def test_canonical_bundle_loads_disabled_before_semantic_validation() -> None:
    result = validate_g6b_row_family_bundle(BUNDLE)

    assert result.valid is False
    assert result.errors == ("semantic validation incomplete",)
    assert result.scientific_execution_authorized is False
    assert result.case_creation_authorized is False
    assert result.adversarial_review_status == "PENDING"
    assert result.review_state == "ROW_FAMILY_BUNDLE_IMPLEMENTED"
    assert set(result.bundle_hashes) == {
        "row_family_protocol.json",
        "identity_schema.json",
        "row_family_matrix.json",
        "reuse_matrix.json",
        "overlap_report_schema.json",
        "runtime_lock_schema.json",
        "review_state.json",
        "failure_ledger.json",
    }


def test_overlap_and_runtime_lock_canonical_objects_are_immutable() -> None:
    overlap = _load(BUNDLE, "overlap_report_schema.json")
    runtime = _load(BUNDLE, "runtime_lock_schema.json")

    assert overlap == _EXPECTED_OVERLAP_REPORT_SCHEMA
    assert runtime == _EXPECTED_RUNTIME_LOCK_SCHEMA
    assert overlap["actual_overlap_checked"] is False
    assert overlap["actual_overlap_report_available"] is False
    assert overlap["schema_only_overlap_report_cannot_authorize_execution"] is True
    assert overlap["missing_actual_overlap_report_blocks_execution"] is True
    assert overlap["local_absence_is_nonoverlap_evidence"] is False
    assert overlap["remote_only_G5_authority_paths"] == [
        "evidence/g5/G5_RAW_HASH_MANIFEST.json",
        "evidence/g5/G5_RESULT_SUMMARY.json",
    ]
    assert overlap["retired_authorities"] == ["G4", "G5", "G6_R"]
    assert overlap["later_actual_report_required_fields"] == [
        "locked_target_identity",
        "retired_authority_hashes",
        "discovery_case_unit_hashes",
        "per_dimension_results",
        "per_unit_results",
        "refusal_entries",
    ]
    assert runtime["overlap_authority_lock"]["authorizes_execution"] is False
    assert runtime["execution_runtime_lock"]["authorizes_execution"] is False


@pytest.mark.parametrize("name", _NAMES)
def test_missing_document_is_rejected(tmp_path: Path, name: str) -> None:
    bundle = _copy_bundle(tmp_path)
    (bundle / name).unlink()
    _assert_invalid(bundle, f"missing JSON documents: ['{name}']")


def test_copied_noncanonical_root_is_rejected(tmp_path: Path) -> None:
    floating = tmp_path / "floating"
    shutil.copytree(BUNDLE, floating)
    _assert_invalid(
        floating,
        "bundle root must be <repo>/cases/discovery/g6b/row_families/"
        "structural_discovery_v1",
    )


@pytest.mark.parametrize(
    "field", ["scientific_execution_authorized", "case_creation_authorized"]
)
def test_true_authorization_is_rejected(tmp_path: Path, field: str) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, "row_family_protocol.json")
    value[field] = True
    _write(bundle, "row_family_protocol.json", value)
    _assert_invalid(bundle, f"{field} must be false")


@pytest.mark.parametrize("name", _NAMES)
def test_non_object_root_is_rejected(tmp_path: Path, name: str) -> None:
    bundle = _copy_bundle(tmp_path)
    (bundle / name).write_text("[]\n", encoding="utf-8")
    _assert_invalid(bundle, f"{name}: root must be a JSON object")


@pytest.mark.parametrize("name", _NAMES)
def test_duplicate_key_is_rejected(tmp_path: Path, name: str) -> None:
    bundle = _copy_bundle(tmp_path)
    raw = (bundle / name).read_text(encoding="utf-8")
    duplicate = raw.replace(
        '"schema_version":',
        '"schema_version": "shadow",\n  "schema_version":',
        1,
    )
    (bundle / name).write_text(duplicate, encoding="utf-8")
    _assert_invalid(bundle, f"{name}: duplicate JSON key")


def test_extra_nested_json_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    _write(bundle, "extra.json", {"schema_version": "unexpected"})
    _assert_invalid(bundle, "unexpected JSON documents: ['extra.json']")


@pytest.mark.parametrize("operation", ["remove", "duplicate", "replace"])
@pytest.mark.parametrize("retired_dimension", _RETIRED_DIMENSIONS)
def test_retired_overlap_dimension_contract_drift_is_rejected(
    tmp_path: Path, retired_dimension: str, operation: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    overlap = _load(bundle, "overlap_report_schema.json")
    overlap["retired_dimensions"] = _mutate_list(
        overlap["retired_dimensions"], retired_dimension, operation
    )
    _write(bundle, "overlap_report_schema.json", overlap)
    _assert_invalid(bundle, "overlap_report_schema.json: document must match")


@pytest.mark.parametrize("operation", ["remove", "duplicate", "replace"])
@pytest.mark.parametrize("confirmation_dimension", _FUTURE_CONFIRMATION_DIMENSIONS)
def test_confirmation_overlap_dimension_contract_drift_is_rejected(
    tmp_path: Path, confirmation_dimension: str, operation: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    overlap = _load(bundle, "overlap_report_schema.json")
    overlap["future_confirmation_dimensions"] = _mutate_list(
        overlap["future_confirmation_dimensions"], confirmation_dimension, operation
    )
    _write(bundle, "overlap_report_schema.json", overlap)
    _assert_invalid(bundle, "overlap_report_schema.json: document must match")


@pytest.mark.parametrize("confirmation_flag", _CONFIRMATION_METRIC_FLAGS)
def test_confirmation_metric_reuse_false_is_rejected(
    tmp_path: Path, confirmation_flag: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    overlap = _load(bundle, "overlap_report_schema.json")
    metric_reuse = overlap["future_confirmation_metric_reuse"]
    assert isinstance(metric_reuse, dict)
    metric_reuse[confirmation_flag] = False
    _write(bundle, "overlap_report_schema.json", overlap)
    _assert_invalid(bundle, "overlap_report_schema.json: document must match")


@pytest.mark.parametrize("confirmation_flag", _CONFIRMATION_METRIC_FLAGS)
def test_confirmation_metric_reuse_key_removal_is_rejected(
    tmp_path: Path, confirmation_flag: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    overlap = _load(bundle, "overlap_report_schema.json")
    metric_reuse = overlap["future_confirmation_metric_reuse"]
    assert isinstance(metric_reuse, dict)
    metric_reuse.pop(confirmation_flag)
    _write(bundle, "overlap_report_schema.json", overlap)
    _assert_invalid(bundle, "overlap_report_schema.json: document must match")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("actual_overlap_checked", True),
        ("actual_overlap_report_available", True),
    ],
)
def test_overlap_actual_report_state_drift_is_rejected(
    tmp_path: Path, field: str, value: bool
) -> None:
    bundle = _copy_bundle(tmp_path)
    overlap = _load(bundle, "overlap_report_schema.json")
    overlap[field] = value
    _write(bundle, "overlap_report_schema.json", overlap)
    _assert_invalid(bundle, "overlap_report_schema.json: document must match")


@pytest.mark.parametrize("operation", ["remove", "duplicate", "replace"])
@pytest.mark.parametrize("authority_lock_field", _AUTHORITY_LOCK_REQUIRED_FIELDS)
def test_authority_lock_required_field_contract_drift_is_rejected(
    tmp_path: Path, authority_lock_field: str, operation: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    runtime = _load(bundle, "runtime_lock_schema.json")
    authority_lock = runtime["overlap_authority_lock"]
    assert isinstance(authority_lock, dict)
    authority_lock["required_fields"] = _mutate_list(
        authority_lock["required_fields"], authority_lock_field, operation
    )
    _write(bundle, "runtime_lock_schema.json", runtime)
    _assert_invalid(bundle, "runtime_lock_schema.json: document must match")


@pytest.mark.parametrize("operation", ["remove", "duplicate", "replace"])
@pytest.mark.parametrize("runtime_lock_field", _RUNTIME_LOCK_REQUIRED_FIELDS)
def test_runtime_lock_required_field_contract_drift_is_rejected(
    tmp_path: Path, runtime_lock_field: str, operation: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    runtime = _load(bundle, "runtime_lock_schema.json")
    runtime_lock = runtime["execution_runtime_lock"]
    assert isinstance(runtime_lock, dict)
    runtime_lock["required_fields"] = _mutate_list(
        runtime_lock["required_fields"], runtime_lock_field, operation
    )
    _write(bundle, "runtime_lock_schema.json", runtime)
    _assert_invalid(bundle, "runtime_lock_schema.json: document must match")


def test_authority_lock_status_drift_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    runtime = _load(bundle, "runtime_lock_schema.json")
    authority_lock = runtime["overlap_authority_lock"]
    assert isinstance(authority_lock, dict)
    authority_lock["status"] = "ready_now"
    _write(bundle, "runtime_lock_schema.json", runtime)
    _assert_invalid(bundle, "runtime_lock_schema.json: document must match")


def test_runtime_lock_status_drift_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    runtime = _load(bundle, "runtime_lock_schema.json")
    runtime_lock = runtime["execution_runtime_lock"]
    assert isinstance(runtime_lock, dict)
    runtime_lock["status"] = "ready_now"
    _write(bundle, "runtime_lock_schema.json", runtime)
    _assert_invalid(bundle, "runtime_lock_schema.json: document must match")


def test_runtime_lock_allowed_only_after_drift_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    runtime = _load(bundle, "runtime_lock_schema.json")
    runtime_lock = runtime["execution_runtime_lock"]
    assert isinstance(runtime_lock, dict)
    runtime_lock["allowed_only_after"] = "SCHEMA_ONLY_REPORT_PRESENT"
    _write(bundle, "runtime_lock_schema.json", runtime)
    _assert_invalid(bundle, "runtime_lock_schema.json: document must match")


def test_foundation_top_level_json_set_remains_exact_five() -> None:
    root = Path("cases/discovery/g6b")
    assert sorted(path.name for path in root.glob("*.json") if path.is_file()) == [
        "estimand_schema.json",
        "failure_ledger.json",
        "independence_schema.json",
        "negative_controls.json",
        "protocol.json",
    ]


def test_unknown_protocol_key_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, "row_family_protocol.json")
    value["unexpected"] = "not allowed"
    _write(bundle, "row_family_protocol.json", value)
    _assert_invalid(bundle, "row_family_protocol.json: document must match")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("adversarial_review_status", "APPROVED"),
        ("bundle_role", "execution_ready"),
    ],
)
def test_protocol_status_drift_is_rejected(
    tmp_path: Path, field: str, value: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "row_family_protocol.json")
    protocol[field] = value
    _write(bundle, "row_family_protocol.json", protocol)
    _assert_invalid(bundle, "row_family_protocol.json: document must match")


@pytest.mark.parametrize(
    "field",
    ["case_creation", "enumeration", "ctmc", "des", "output_inspection"],
)
def test_execution_boundary_drift_is_rejected(tmp_path: Path, field: str) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "row_family_protocol.json")
    boundary = protocol["execution_boundary"]
    assert isinstance(boundary, dict)
    boundary[field] = "authorized"
    _write(bundle, "row_family_protocol.json", protocol)
    _assert_invalid(bundle, "row_family_protocol.json: document must match")


@pytest.mark.parametrize(
    "level", ["family_id", "case_unit_id", "method_observation_id"]
)
def test_missing_identity_level_is_rejected(tmp_path: Path, level: str) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, "identity_schema.json")
    value["identity_levels"].remove(level)
    _write(bundle, "identity_schema.json", value)
    _assert_invalid(bundle, "identity_levels must match")


@pytest.mark.parametrize(
    "key", ["dimension", "applicability_status", "artifact_role", "sha256_or_null"]
)
def test_missing_fingerprint_record_key_is_rejected(tmp_path: Path, key: str) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, "identity_schema.json")
    value["fingerprint_record_keys"].remove(key)
    _write(bundle, "identity_schema.json", value)
    _assert_invalid(bundle, "fingerprint_record_keys must match")


@pytest.mark.parametrize(
    "role",
    [
        "exact_companion",
        "des_companion",
        "schema_only_refusal",
        "review_only_placeholder",
    ],
)
def test_missing_reuse_method_role_is_rejected(tmp_path: Path, role: str) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, "identity_schema.json")
    value["method_roles"].remove(role)
    _write(bundle, "identity_schema.json", value)
    _assert_invalid(bundle, "method_roles must match")


@pytest.mark.parametrize(
    ("field", "canonical"),
    [
        ("allowed", True),
        ("must_be_case_unit_specific", True),
        ("shared_global_sentinel_prohibited", True),
        ("proves_provenance_only", True),
        ("proves_stochastic_independence", False),
    ],
)
def test_no_stochastic_method_manifest_truth_value_is_rejected(
    tmp_path: Path, field: str, canonical: bool
) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, "identity_schema.json")
    manifest = value["no_stochastic_method_manifest"]
    assert isinstance(manifest, dict)
    manifest[field] = not canonical
    _write(bundle, "identity_schema.json", value)
    _assert_invalid(bundle, "no_stochastic_method_manifest must match")


def test_independent_method_observations_are_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, "identity_schema.json")
    value["method_observations_are_independent_cases"] = True
    _write(bundle, "identity_schema.json", value)
    _assert_invalid(
        bundle,
        "method_observations_are_independent_cases must be false",
    )


@pytest.mark.parametrize(
    "relation_id",
    [
        "exact_des_companion",
        "controlled_family_variant",
        "negative_control_pair",
        "method_schema_reuse",
        "retired_authority_overlap",
    ],
)
def test_missing_reuse_relation_id_is_rejected(
    tmp_path: Path, relation_id: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, "reuse_matrix.json")
    value["relations"] = [
        relation for relation in value["relations"] if relation["id"] != relation_id
    ]
    _write(bundle, "reuse_matrix.json", value)
    _assert_invalid(bundle, "reuse relation ids must match")


@pytest.mark.parametrize(("control_index", "field_path"), list(_control_field_cases()))
def test_control_matrix_field_drift_is_rejected(
    tmp_path: Path, control_index: int, field_path: tuple[str, ...]
) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    controls = matrix["negative_control_families"]
    assert isinstance(controls, list)
    control = controls[control_index]
    assert isinstance(control, dict)
    _set_path(control, field_path)
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


@pytest.mark.parametrize("probe_role", list(_probe_removal_cases()))
def test_probe_matrix_role_removal_is_rejected(tmp_path: Path, probe_role: str) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    matrix["discovery_probes"] = [
        probe for probe in matrix["discovery_probes"] if probe["role"] != probe_role
    ]
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


@pytest.mark.parametrize(("probe_role", "falsifier"), list(_probe_falsifier_cases()))
def test_probe_matrix_falsifier_removal_is_rejected(
    tmp_path: Path, probe_role: str, falsifier: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    for probe in matrix["discovery_probes"]:
        if probe["role"] == probe_role:
            probe["falsifiers"].remove(falsifier)
            break
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


@pytest.mark.parametrize(
    ("probe_role", "field"), list(_probe_outcome_neutrality_cases())
)
def test_probe_matrix_outcome_neutrality_drift_is_rejected(
    tmp_path: Path, probe_role: str, field: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    for probe in matrix["discovery_probes"]:
        if probe["role"] == probe_role:
            probe[field] = _drift_value(probe[field])
            break
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


def test_ontology_matrix_terminal_scc_definition_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    matrix["ontology_contract"]["D_local_definition"] = "terminal_scc_deadlock"
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


@pytest.mark.parametrize(
    "route",
    [
        "A2b_proof",
        "complete_LTS_completion_nonreachability_audit",
    ],
    ids=[
        "admission_remove_A2b_proof",
        "admission_remove_complete_LTS_completion_nonreachability_audit",
    ],
)
def test_admission_matrix_route_removal_is_rejected(tmp_path: Path, route: str) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    matrix["ontology_contract"]["D_local_admission_routes"].remove(route)
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


def test_admission_matrix_accepted_a2b_route_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    routes = matrix["ontology_contract"]["D_local_admission_routes"]
    routes[routes.index("A2b_proof")] = "accepted_A2b_proof"
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


@pytest.mark.parametrize(
    "mutation",
    [
        pytest.param("same_case_unit_id_false", id="exact_des_same_case_unit_id_false"),
        pytest.param("drop_bad_label", id="exact_des_drop_bad_label"),
        pytest.param("mutate_bad_label", id="exact_des_mutate_bad_label"),
        pytest.param("swap_bad_labels", id="exact_des_swap_bad_labels"),
        pytest.param("success_label", id="exact_des_success_label"),
        pytest.param(
            "same_versioned_target_false",
            id="exact_des_same_versioned_target_false",
        ),
        pytest.param(
            "method_observations_independent_true",
            id="exact_des_method_observations_independent_true",
        ),
    ],
)
def test_exact_des_matrix_pairing_drift_is_rejected(
    tmp_path: Path, mutation: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    pairing = matrix["exact_des_pairing"]
    if mutation == "same_case_unit_id_false":
        pairing["same_case_unit_id"] = False
    elif mutation == "drop_bad_label":
        pairing["same_selected_bad_labels"].remove("D_global")
    elif mutation == "mutate_bad_label":
        pairing["same_selected_bad_labels"][1] = "D_local_drift"
    elif mutation == "swap_bad_labels":
        pairing["same_selected_bad_labels"] = ["D_local", "D_global"]
    elif mutation == "success_label":
        pairing["same_selected_success_label"] = "SUCCESS"
    elif mutation == "same_versioned_target_false":
        pairing["same_versioned_target"] = False
    elif mutation == "method_observations_independent_true":
        pairing["method_observations_are_independent_cases"] = True
    else:  # pragma: no cover - parameterization guard
        raise AssertionError(mutation)
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


@pytest.mark.parametrize(
    "field",
    [
        "theorem_prediction_status",
        "metric_applicability",
        "metric_observations",
        "execution_status",
        "reproducibility_status",
    ],
    ids=[
        "scoring_theorem_prediction_status",
        "scoring_metric_applicability",
        "scoring_metric_observations",
        "scoring_execution_status",
        "scoring_reproducibility_status",
    ],
)
def test_scoring_matrix_field_drift_is_rejected(tmp_path: Path, field: str) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    scoring = matrix["initial_scoring_state"]
    scoring[field] = _drift_value(scoring[field])
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


def test_scoring_matrix_bad_copy_not_executed_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    scoring = matrix["initial_scoring_state"]
    for field in scoring:
        scoring[field] = "not_executed"
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)
