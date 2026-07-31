import json
import shutil
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
def test_missing_method_role_is_rejected(tmp_path: Path, role: str) -> None:
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
