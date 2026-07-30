import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from ims_deadlock.g6b_protocol import validate_g6b_protocol_bundle

_DOCUMENT_TOP_LEVEL_KEYS = {
    "protocol.json": "protocol_id",
    "estimand_schema.json": "future_required_hashes",
    "independence_schema.json": "dimensions",
    "negative_controls.json": "controls",
    "failure_ledger.json": "append_only",
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

_EXPECTED_NEGATIVE_CONTROLS = [
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


def _copy_bundle(tmp_path: Path) -> Path:
    source_root = Path.cwd()
    repo_root = tmp_path / "repo"
    target = repo_root / "cases/discovery/g6b"
    source = source_root / "cases/discovery/g6b"
    shutil.copytree(source, target)
    for relative_path in [*_ARTIFACT_PATHS, *_HISTORICAL_AUTHORITIES]:
        if relative_path in _REMOTE_ONLY_HISTORICAL_AUTHORITIES:
            continue
        source_path = source_root / relative_path
        assert source_path.is_file(), relative_path
        target_path = repo_root / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
    return target


def _load(bundle: Path, filename: str) -> dict[str, Any]:
    with (bundle / filename).open(encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def _write(bundle: Path, filename: str, data: dict[str, Any]) -> None:
    with (bundle / filename).open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")


def _assert_invalid(bundle: Path, expected: str) -> None:
    validation = validate_g6b_protocol_bundle(bundle)
    assert validation.valid is False
    assert any(expected in error for error in validation.errors), validation.errors


def test_canonical_g6b_bundle_is_valid_and_execution_disabled() -> None:
    validation = validate_g6b_protocol_bundle(Path("cases/discovery/g6b"))

    assert validation.valid is True
    assert validation.errors == ()
    assert validation.scientific_execution_authorized is False
    assert validation.adversarial_review_status == "PENDING"
    assert set(validation.bundle_hashes) == {
        "protocol.json",
        "estimand_schema.json",
        "independence_schema.json",
        "negative_controls.json",
        "failure_ledger.json",
    }


def test_duplicate_json_key_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = (bundle / "protocol.json").read_text(encoding="utf-8")
    duplicate = protocol.replace(
        '"schema_version": "ims-deadlock/g6b-discovery-protocol/v1",',
        (
            '"schema_version": "ims-deadlock/g6b-discovery-protocol/v1",\n'
            '  "schema_version": "ims-deadlock/g6b-discovery-protocol/v1",'
        ),
        1,
    )
    (bundle / "protocol.json").write_text(duplicate, encoding="utf-8")

    _assert_invalid(bundle, "duplicate JSON key")


def test_copied_bundle_outside_canonical_layout_fails_closed(tmp_path: Path) -> None:
    bundle = tmp_path / "floating_g6b"
    shutil.copytree(Path("cases/discovery/g6b"), bundle)

    _assert_invalid(bundle, "bundle root must be <repo>/cases/discovery/g6b")


def test_extra_json_document_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    _write(bundle, "extra.json", {"schema_version": "unexpected"})

    _assert_invalid(bundle, "unexpected JSON documents: ['extra.json']")


@pytest.mark.parametrize("filename", sorted(_DOCUMENT_TOP_LEVEL_KEYS))
def test_missing_required_document_is_reported_deterministically(
    tmp_path: Path, filename: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    (bundle / filename).unlink()

    _assert_invalid(bundle, f"missing JSON documents: ['{filename}']")


@pytest.mark.parametrize("filename", sorted(_DOCUMENT_TOP_LEVEL_KEYS))
def test_non_object_root_is_rejected_for_each_document(
    tmp_path: Path, filename: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    (bundle / filename).write_text("[]\n", encoding="utf-8")

    _assert_invalid(bundle, f"{filename}: root must be a JSON object")


@pytest.mark.parametrize("filename", sorted(_DOCUMENT_TOP_LEVEL_KEYS))
def test_unknown_top_level_key_is_rejected_for_each_document(
    tmp_path: Path, filename: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    document = _load(bundle, filename)
    document["unexpected"] = "not allowed"
    _write(bundle, filename, document)

    _assert_invalid(bundle, f"{filename}: unexpected keys")


@pytest.mark.parametrize(
    ("filename", "key_to_remove"),
    sorted(_DOCUMENT_TOP_LEVEL_KEYS.items()),
)
def test_missing_top_level_key_is_rejected_for_each_document(
    tmp_path: Path, filename: str, key_to_remove: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    document = _load(bundle, filename)
    document.pop(key_to_remove)
    _write(bundle, filename, document)

    _assert_invalid(bundle, f"{filename}: missing keys")


@pytest.mark.parametrize("filename", sorted(_DOCUMENT_TOP_LEVEL_KEYS))
def test_duplicate_json_key_is_rejected_for_each_document(
    tmp_path: Path, filename: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    raw = (bundle / filename).read_text(encoding="utf-8")
    duplicate = raw.replace(
        '"schema_version":',
        '"schema_version": "duplicate-shadow",\n  "schema_version":',
        1,
    )
    (bundle / filename).write_text(duplicate, encoding="utf-8")

    _assert_invalid(bundle, f"{filename}: duplicate JSON key")


def test_unsupported_schema_version_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    protocol["schema_version"] = "ims-deadlock/g6b-discovery-protocol/v2"
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: unsupported schema_version")


def test_missing_independence_dimension_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "independence_schema.json")
    dimensions = schema["dimensions"]
    assert isinstance(dimensions, list)
    dimensions.remove("metric_schema_sha256")
    _write(bundle, "independence_schema.json", schema)

    _assert_invalid(bundle, "independence_schema.json: dimensions")


def test_wrong_d_local_ontology_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "estimand_schema.json")
    ontology = schema["ontology"]
    assert isinstance(ontology, dict)
    d_local = ontology["D_local"]
    assert isinstance(d_local, dict)
    d_local["ontology"] = "terminal_scc"
    _write(bundle, "estimand_schema.json", schema)

    _assert_invalid(bundle, "estimand_schema.json: D_local ontology")


def test_exact_des_consistency_drift_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "estimand_schema.json")
    consistency = schema["exact_des_consistency"]
    assert isinstance(consistency, dict)
    consistency["same_selected_bad_labels_required"] = False
    _write(bundle, "estimand_schema.json", schema)

    _assert_invalid(bundle, "estimand_schema.json: exact_des_consistency")


def test_missing_negative_control_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    controls = _load(bundle, "negative_controls.json")
    control_list = controls["controls"]
    assert isinstance(control_list, list)
    control_list.pop()
    _write(bundle, "negative_controls.json", controls)

    _assert_invalid(bundle, "negative_controls.json: controls")


@pytest.mark.parametrize("index", range(len(_EXPECTED_NEGATIVE_CONTROLS)))
@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("expected_classification", "DRIFTED_CLASSIFICATION"),
        ("expected_refusal", "drifted_refusal"),
    ],
)
def test_negative_control_semantic_drift_is_rejected(
    tmp_path: Path, index: int, field: str, replacement: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    controls = _load(bundle, "negative_controls.json")
    control_list = controls["controls"]
    assert control_list == _EXPECTED_NEGATIVE_CONTROLS
    assert isinstance(control_list, list)
    control = control_list[index]
    assert isinstance(control, dict)
    control[field] = replacement
    _write(bundle, "negative_controls.json", controls)

    _assert_invalid(bundle, "negative_controls.json: controls")


def test_absolute_unapproved_historical_path_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    authorities = protocol["tracked_historical_authorities"]
    assert isinstance(authorities, list)
    authorities[0] = "/tmp/FREEZE_ENTRY.json"
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: tracked_historical_authorities")


def test_execution_true_while_review_pending_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    protocol["scientific_execution_authorized"] = True
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: scientific execution")


def test_append_only_false_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    ledger = _load(bundle, "failure_ledger.json")
    ledger["append_only"] = False
    _write(bundle, "failure_ledger.json", ledger)

    _assert_invalid(bundle, "failure_ledger.json: append_only")


def test_artifact_path_ambiguity_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    paths = protocol["artifact_paths"]
    assert isinstance(paths, list)
    paths[0] = "docs/cases/../cases/G6_B_DISCOVERY_PROTOCOL.md"
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: artifact_paths")
