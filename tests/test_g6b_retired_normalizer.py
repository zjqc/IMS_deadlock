from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ims_deadlock.g6b_retired_normalizer import (
    build_authority_lock_records,
    build_authority_source_records,
    build_retired_fingerprint_records,
    main,
    run_normalization,
    select_allowed_value,
    write_authority_lock_record,
    write_authority_source_record,
    write_fingerprint_record,
    write_normalization_authorization,
    write_normalization_manifest,
)

from ims_deadlock import g6b_retired_normalizer as normalizer
from ims_deadlock.g6b_canonical_json import canonical_bytes_v2, loads_v2
from ims_deadlock.g6b_schema_contracts import (
    SchemaContractError,
    validate_normalizer_static_source,
)

JsonObject = dict[str, Any]

_G4_CASE_PATH = "cases/discovery/g4/cases/G4_IMS_PARAMETER_GRID.json"
_G4_MANIFEST_PATH = "cases/discovery/g4/case_manifest.json"
_RAW_ONLY_PATH = "cases/discovery/g4/baseline_applicability.json"
_LOCK_AUTHORITY_ID = "G4_FREEZE"
_FINGERPRINT_ID = "fingerprint-record-test"
_SOURCE_ROOT = (
    "cases/discovery/g6b/row_families/structural_discovery_v1/"
    "governance/g6b_retired_authority_normalization_v1"
)
_SHA_A = "a" * 64
_SHA_B = "b" * 64
_SHA_C = "c" * 64
_GIT_A = "1" * 40
_GIT_B = "2" * 40


def _selector_rows() -> list[JsonObject]:
    return [
        {
            "source_path_pattern": _G4_CASE_PATH,
            "selector_kind": "exact_pointer_set",
            "selectors": ["/schema_version", "/case_id"],
            "allowed_use": "authority_identity",
        },
        {
            "source_path_pattern": _G4_CASE_PATH,
            "selector_kind": "prefix_set",
            "selectors": ["/input_payload"],
            "allowed_use": "case_content_projection",
        },
        {
            "source_path_pattern": _G4_MANIFEST_PATH,
            "selector_kind": "element_pointer_pattern_set",
            "selectors": ["/cases/*/case_id", "/cases/*/path"],
            "allowed_use": "lineage_link",
        },
        {
            "source_path_pattern": _G4_CASE_PATH,
            "selector_kind": "exact_pointer_set",
            "selectors": ["/locked_hashes/result"],
            "allowed_use": "source_hash_validation",
        },
        {
            "source_path_pattern": _RAW_ONLY_PATH,
            "selector_kind": "raw_bytes_only",
            "selectors": [],
            "allowed_use": "source_hash_validation",
        },
    ]


def _canonical_json_bytes(value: JsonObject) -> bytes:
    return canonical_bytes_v2(value)


def _json_bytes(text: str) -> bytes:
    return text.encode("utf-8")


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _read_json(path: Path) -> JsonObject:
    value = loads_v2(path.read_bytes())
    assert isinstance(value, dict)
    return value


def _authorization_record() -> JsonObject:
    return {
        "schema_version": "ims-deadlock/g6b-retired-normalization-authorization/v1",
        "authorization_id": "retired-normalization-test-auth",
        "capability": "retired_authority_fingerprint_normalization",
        "authorized": True,
        "source_head": _GIT_A,
        "source_tree_hash": _GIT_B,
        "authority_ids": ["G4_FREEZE", "G5_EXECUTION", "G6_R_REPLAY_R3"],
        "expected_file_manifest_hash": _SHA_A,
        "allowed_source_paths": [_G4_CASE_PATH, _G4_MANIFEST_PATH, _RAW_ONLY_PATH],
        "allowed_json_fields_by_source": _selector_rows(),
        "allowed_historical_builder_symbols": [],
        "normalizer_code_sha256": _SHA_B,
        "allowed_operations": [
            "read_authority_bytes",
            "parse_allowed_json_pointers",
            "verify_source_hashes",
            "parse_historical_decimal_exactly",
            "apply_static_input_projection",
            "canonicalize_projection_v2",
            "compute_sha256",
            "write_normalization_manifest",
            "write_fingerprint_record",
        ],
        "allowed_project_imports": [
            "ims_deadlock.g6b_retired_normalizer",
            "ims_deadlock.g6b_canonical_json",
            "ims_deadlock.g6b_schema_contracts",
        ],
        "forbidden_imports": [
            "ims_deadlock.analysis",
            "ims_deadlock.cases",
            "ims_deadlock.ctmc",
            "ims_deadlock.engine",
            "ims_deadlock.g4_instances",
            "ims_deadlock.g4_protocol",
            "ims_deadlock.g5_scoring",
            "ims_deadlock.historical_replay",
            "ims_deadlock.terminal_classes",
            "os",
            "subprocess",
            "socket",
            "requests",
            "urllib",
        ],
        "forbidden_calls": ["open", "exec", "eval", "compile", "__import__"],
        "allowed_output_schema": {
            "schema_id": "ims-deadlock/g6b-retired-normalization-records/v1",
            "schema_version": "v1",
        },
        "allowed_output_root": _SOURCE_ROOT,
        "review_artifact_hash": _SHA_C,
        "issued_at_utc": "2026-08-05T00:00:00Z",
        "invalidated_by_identity_drift": False,
        "authorization_sha256": None,
    }


def _authority_lock_record(authority_id: str = _LOCK_AUTHORITY_ID) -> JsonObject:
    return {
        "authority_id": authority_id,
        "origin_remote": "origin",
        "origin_commit_or_null": _GIT_A,
        "origin_tree_hash_or_null": _GIT_B,
        "origin_lock_artifact_ref": "cases/discovery/g4/FREEZE_ENTRY.json",
        "origin_artifact_inventory_hash": _SHA_A,
        "current_merged_copy_tree_hash": _SHA_B,
        "identity_verification_status": (
            "verified_merged_copy_against_historical_hashes"
        ),
        "authority_lock_record_sha256": None,
    }


def _authority_source_record(path: str = _G4_CASE_PATH) -> JsonObject:
    return {
        "authority_id": "G4_FREEZE",
        "authority_stage": "G4_FREEZE",
        "authority_lock_record_sha256": _SHA_A,
        "repo_relative_path": path,
        "raw_byte_sha256": _SHA_B,
        "declared_historical_hash_or_null": _SHA_B,
        "declared_hash_algorithm_or_null": "sha256",
        "declared_hash_verified": True,
        "allowed_projection_uses": [
            "authority_identity",
            "case_content_projection",
            "source_hash_validation",
        ],
        "contains_outcome_fields": False,
    }


def _fingerprint_record(record_id: str = _FINGERPRINT_ID) -> JsonObject:
    return {
        "schema_version": "ims-deadlock/g6b-retired-fingerprint-record/v1",
        "record_id": record_id,
        "authority_id": "G4_FREEZE",
        "subject_type": "retired_case",
        "subject_id": "G4_IMS_PARAMETER_GRID",
        "owner_subject_id_or_null": None,
        "dimension": "case_content_sha256",
        "dimension_status": "derived_by_versioned_normalizer",
        "source_dimension": "derived_by_versioned_normalizer",
        "projection_kind_or_null": "g4_case_content_projection/v1",
        "projection": {"case_id": "G4_IMS_PARAMETER_GRID"},
        "projection_sha256_or_null": _SHA_A,
        "comparison_projection_sha256_or_null": _SHA_A,
        "record_provenance_sha256": _SHA_B,
        "lineage_id": "G4_FREEZE:G4_IMS_PARAMETER_GRID:case_content_sha256",
        "inherited_from_record_id_or_null": None,
        "duplicate_lineage_of_record_id_or_null": None,
        "source_record_refs": [_G4_CASE_PATH],
        "retired_normalizer_version": "g6b-retired-normalizer-v1",
        "created_at_utc": "2026-08-05T00:00:00Z",
        "fingerprint_record_sha256": None,
    }


def _manifest_record(
    *,
    authorization_sha256: str,
    authority_lock_hash: str,
    source_record_hash: str,
    fingerprint_hash: str,
) -> JsonObject:
    source_hashes = {
        _G4_CASE_PATH: _SHA_B,
        _G4_MANIFEST_PATH: _SHA_C,
        _RAW_ONLY_PATH: _SHA_A,
    }
    return {
        "schema_version": "ims-deadlock/g6b-retired-normalization-manifest/v1",
        "manifest_id": "retired-normalization-manifest-test",
        "source_remote": "origin",
        "source_head": _GIT_A,
        "source_tree_hash": _GIT_B,
        "source_dirty_state": "clean",
        "authority_ids": ["G4_FREEZE", "G5_EXECUTION", "G6_R_REPLAY_R3"],
        "expected_file_manifest": dict(sorted(source_hashes.items())),
        "verified_file_byte_hashes": dict(sorted(source_hashes.items())),
        "frozen_hash_validation_results": [],
        "historical_canonicalization_versions": {
            "G4_FREEZE": "ims-deadlock/g6b-canonical-json/v2",
            "G5_EXECUTION": "ims-deadlock/g6b-canonical-json/v2",
            "G6_R_REPLAY_R3": "ims-deadlock/g6b-canonical-json/v2",
        },
        "projection_canonicalization_version": "ims-deadlock/g6b-canonical-json/v2",
        "normalizer_version": "g6b-retired-normalizer-v1",
        "normalizer_code_sha256": _SHA_B,
        "normalization_authorization_sha256": authorization_sha256,
        "authority_lock_record_hashes": {"G4_FREEZE": authority_lock_hash},
        "authority_source_record_hashes": {_G4_CASE_PATH: source_record_hash},
        "fingerprint_record_hashes": {_FINGERPRINT_ID: fingerprint_hash},
        "unique_lineage_map": {
            "G4_FREEZE:G4_IMS_PARAMETER_GRID:case_content_sha256": [_FINGERPRINT_ID]
        },
        "dimension_status_counts": {
            "case_content_sha256": {
                "derived_by_versioned_normalizer": 1,
                "direct_stored": 0,
                "inherited_from_authority": 0,
                "not_applicable_by_protocol": 0,
                "not_applicable_retired_stage": 0,
                "unreconstructable_refuse": 0,
            }
        },
        "missing_source_records": [],
        "unreconstructable_records": [],
        "comparison_eligibility": True,
        "created_at_utc": "2026-08-05T00:00:00Z",
        "manifest_sha256": None,
    }


@pytest.mark.parametrize(
    ("source_bytes", "pointer", "match"),
    [
        (_json_bytes('{"case_id":"a","case_id":"b"}'), "/case_id", "duplicate"),
        (
            _json_bytes('{"input_payload":{"name":"e\\u0301"}}'),
            "/input_payload/name",
            "non_nfc",
        ),
        (
            _json_bytes('{"input_payload":{"value":1.25}}'),
            "/input_payload/value",
            "float",
        ),
    ],
)
def test_selector_rejects_duplicate_members_non_nfc_and_forbidden_floats(
    source_bytes: bytes,
    pointer: str,
    match: str,
) -> None:
    with pytest.raises(SchemaContractError, match=match):
        select_allowed_value(
            source_bytes,
            pointer=pointer,
            selector_rows=_selector_rows(),
            requested_use="case_content_projection",
        )


def test_selector_preserves_historical_decimal_string_without_float_coercion() -> None:
    source = _canonical_json_bytes(
        {
            "case_id": "G4_IMS_PARAMETER_GRID",
            "input_payload": {"historical_decimal": "1.2300"},
        }
    )
    selected = select_allowed_value(
        source,
        pointer="/input_payload/historical_decimal",
        selector_rows=_selector_rows(),
        requested_use="case_content_projection",
    )
    assert selected == "1.2300"
    assert type(selected) is str
    with pytest.raises(SchemaContractError, match="json_pointer_contract"):
        select_allowed_value(
            source,
            pointer="/input_payload/missing",
            selector_rows=_selector_rows(),
            requested_use="case_content_projection",
        )


@pytest.mark.parametrize(
    ("pointer", "requested_use", "expected"),
    [
        ("/case_id", "authority_identity", "G4_IMS_PARAMETER_GRID"),
        (
            "/input_payload/protocol_input/cells",
            "case_content_projection",
            [{"cell_id": "cell-a", "value": "kept"}],
        ),
        ("/cases/0/case_id", "lineage_link", "G4_IMS_PARAMETER_GRID"),
    ],
)
def test_selector_accepts_exact_prefix_and_element_pointer_permissions(
    pointer: str,
    requested_use: str,
    expected: object,
) -> None:
    source = _canonical_json_bytes(
        {
            "schema_version": "synthetic/v1",
            "case_id": "G4_IMS_PARAMETER_GRID",
            "input_payload": {
                "protocol_input": {"cells": [{"cell_id": "cell-a", "value": "kept"}]}
            },
            "cases": [
                {
                    "case_id": "G4_IMS_PARAMETER_GRID",
                    "path": _G4_CASE_PATH,
                }
            ],
        }
    )
    assert (
        select_allowed_value(
            source,
            pointer=pointer,
            selector_rows=_selector_rows(),
            requested_use=requested_use,
        )
        == expected
    )


def test_selector_rejects_hash_validation_field_as_projection() -> None:
    source = _canonical_json_bytes({"locked_hashes": {"result": _SHA_A}})
    with pytest.raises(SchemaContractError, match="source_field_read_violation"):
        select_allowed_value(
            source,
            pointer="/locked_hashes/result",
            selector_rows=_selector_rows(),
            requested_use="case_content_projection",
        )


def test_selector_raw_bytes_only_never_parses_json_values() -> None:
    with pytest.raises(SchemaContractError, match="raw_bytes_only_json_parse"):
        select_allowed_value(
            b'{"schema_version":"synthetic/v1"}',
            pointer="/schema_version",
            selector_rows=[
                {
                    "source_path_pattern": _RAW_ONLY_PATH,
                    "selector_kind": "raw_bytes_only",
                    "selectors": [],
                    "allowed_use": "source_hash_validation",
                }
            ],
            requested_use="source_hash_validation",
        )


def test_selector_use_is_singular_and_unlisted_pointer_refuses() -> None:
    source = _canonical_json_bytes(
        {
            "case_id": "G4_IMS_PARAMETER_GRID",
            "input_payload": {"protocol_input": {"generator_id": "g4-grid"}},
        }
    )
    with pytest.raises(SchemaContractError, match="source_field_read_violation"):
        select_allowed_value(
            source,
            pointer="/input_payload/protocol_input/generator_id",
            selector_rows=_selector_rows(),
            requested_use="authority_identity",
        )
    with pytest.raises(SchemaContractError, match="source_field_read_violation"):
        select_allowed_value(
            source,
            pointer="/not_listed",
            selector_rows=_selector_rows(),
            requested_use="case_content_projection",
        )


def test_public_builders_are_pure_and_do_not_create_outputs(tmp_path: Path) -> None:
    authorization = _authorization_record()
    source_hashes = {
        _G4_CASE_PATH: _SHA_B,
        _G4_MANIFEST_PATH: _SHA_C,
        _RAW_ONLY_PATH: _SHA_A,
    }
    before = sorted(tmp_path.rglob("*"))
    authority_locks = build_authority_lock_records(
        tmp_path,
        authorization,
        source_hashes,
    )
    source_records = build_authority_source_records(
        tmp_path,
        authorization,
        authority_locks,
    )
    fingerprint_records = build_retired_fingerprint_records(
        tmp_path,
        authorization,
        authority_locks,
        source_records,
    )
    assert sorted(tmp_path.rglob("*")) == before
    assert set(authority_locks) == {"G4_FREEZE", "G5_EXECUTION", "G6_R_REPLAY_R3"}
    assert set(source_records) == set(source_hashes)
    assert fingerprint_records


def test_authorization_writer_creates_absent_root_and_preserves_exact_bytes(
    tmp_path: Path,
) -> None:
    root = tmp_path / "authorized" / "normalization"
    authorization_bytes = _canonical_json_bytes(_authorization_record())
    written_sha = write_normalization_authorization(root, authorization_bytes)
    destination = root / "normalization_authorization.json"
    assert root.is_dir()
    assert destination.read_bytes() == authorization_bytes
    assert written_sha == hashlib.sha256(authorization_bytes).hexdigest()
    with pytest.raises(SchemaContractError, match="preexisting"):
        write_normalization_authorization(root, authorization_bytes)


@pytest.mark.parametrize(
    ("writer_name", "writer", "record", "expected_relative"),
    [
        (
            "authority_lock",
            lambda root, record: write_authority_lock_record(
                root, _LOCK_AUTHORITY_ID, record
            ),
            _authority_lock_record(),
            Path("authority_locks") / f"{_LOCK_AUTHORITY_ID}.json",
        ),
        (
            "authority_source",
            lambda root, record: write_authority_source_record(
                root, _G4_CASE_PATH, record
            ),
            _authority_source_record(),
            Path("source_records") / f"{_hash_text(_G4_CASE_PATH)}.json",
        ),
        (
            "fingerprint",
            lambda root, record: write_fingerprint_record(
                root,
                _FINGERPRINT_ID,
                record,
            ),
            _fingerprint_record(),
            Path("fingerprints") / f"{_hash_text(_FINGERPRINT_ID)}.json",
        ),
    ],
)
def test_record_writers_use_only_fixed_roles_and_canonical_paths(
    tmp_path: Path,
    writer_name: str,
    writer: Any,
    record: JsonObject,
    expected_relative: Path,
) -> None:
    root = tmp_path / "authorized"
    write_normalization_authorization(
        root,
        _canonical_json_bytes(_authorization_record()),
    )
    written_sha = writer(root, record)
    destination = root / expected_relative
    assert destination.is_file(), writer_name
    assert destination.read_bytes() == canonical_bytes_v2(record)
    assert written_sha == hashlib.sha256(destination.read_bytes()).hexdigest()
    with pytest.raises(SchemaContractError, match="preexisting"):
        writer(root, record)


def test_writers_reject_absolute_parent_misnamed_and_preexisting_paths(
    tmp_path: Path,
) -> None:
    root = tmp_path / "authorized"
    write_normalization_authorization(
        root,
        _canonical_json_bytes(_authorization_record()),
    )
    with pytest.raises(SchemaContractError, match="illegal_retired_authority"):
        write_authority_lock_record(
            root,
            "G4_FREEZE/../escape",
            _authority_lock_record("G4_FREEZE/../escape"),
        )
    with pytest.raises(SchemaContractError, match="source_outside_retired_inventory"):
        write_authority_source_record(
            root,
            "/absolute/source.json",
            _authority_source_record("/absolute/source.json"),
        )
    with pytest.raises(SchemaContractError, match="source_outside_retired_inventory"):
        write_authority_source_record(
            root,
            "../source.json",
            _authority_source_record("../source.json"),
        )
    with pytest.raises(SchemaContractError, match="record_id"):
        write_fingerprint_record(
            root,
            "../fingerprint-record-test",
            _fingerprint_record("../fingerprint-record-test"),
        )


def test_writers_reject_symlink_dependent_destinations(tmp_path: Path) -> None:
    root = tmp_path / "authorized"
    outside = tmp_path / "outside"
    outside.mkdir()
    write_normalization_authorization(
        root,
        _canonical_json_bytes(_authorization_record()),
    )
    source_dir = root / "source_records"
    source_dir.mkdir()
    source_dir.rmdir()
    try:
        source_dir.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable on this platform: {exc}")
    with pytest.raises(SchemaContractError, match="symlink"):
        write_authority_source_record(root, _G4_CASE_PATH, _authority_source_record())


def test_manifest_writer_is_last_and_verifies_referenced_record_bytes(
    tmp_path: Path,
) -> None:
    root = tmp_path / "authorized"
    authorization_bytes = _canonical_json_bytes(_authorization_record())
    authorization_sha = write_normalization_authorization(root, authorization_bytes)
    lock_sha = write_authority_lock_record(
        root,
        _LOCK_AUTHORITY_ID,
        _authority_lock_record(),
    )
    source_sha = write_authority_source_record(
        root,
        _G4_CASE_PATH,
        _authority_source_record(),
    )
    fingerprint_sha = write_fingerprint_record(
        root,
        _FINGERPRINT_ID,
        _fingerprint_record(),
    )
    manifest = _manifest_record(
        authorization_sha256=authorization_sha,
        authority_lock_hash=lock_sha,
        source_record_hash=source_sha,
        fingerprint_hash=fingerprint_sha,
    )
    manifest_sha = write_normalization_manifest(root, manifest)
    destination = root / "normalization_manifest.json"
    assert destination.read_bytes() == canonical_bytes_v2(manifest)
    assert manifest_sha == hashlib.sha256(destination.read_bytes()).hexdigest()
    with pytest.raises(SchemaContractError, match="preexisting"):
        write_normalization_manifest(root, manifest)


def test_manifest_writer_refuses_before_all_records_exist(tmp_path: Path) -> None:
    root = tmp_path / "authorized"
    authorization_bytes = _canonical_json_bytes(_authorization_record())
    authorization_sha = write_normalization_authorization(root, authorization_bytes)
    lock_sha = write_authority_lock_record(
        root,
        _LOCK_AUTHORITY_ID,
        _authority_lock_record(),
    )
    source_sha = write_authority_source_record(
        root,
        _G4_CASE_PATH,
        _authority_source_record(),
    )
    manifest = _manifest_record(
        authorization_sha256=authorization_sha,
        authority_lock_hash=lock_sha,
        source_record_hash=source_sha,
        fingerprint_hash=_SHA_C,
    )
    with pytest.raises(SchemaContractError, match="manifest_last"):
        write_normalization_manifest(root, manifest)
    assert root.exists()
    assert not (root / "normalization_manifest.json").exists()
    with pytest.raises(SchemaContractError, match="incomplete"):
        run_normalization(tmp_path, root / "normalization_authorization.json", root)


def test_incomplete_root_is_preserved_and_cannot_be_reused_or_retried(
    tmp_path: Path,
) -> None:
    root = tmp_path / "authorized"
    authorization_path = tmp_path / "normalization_authorization.json"
    authorization_path.write_bytes(_canonical_json_bytes(_authorization_record()))
    write_normalization_authorization(root, authorization_path.read_bytes())
    write_authority_lock_record(root, _LOCK_AUTHORITY_ID, _authority_lock_record())
    write_authority_source_record(root, _G4_CASE_PATH, _authority_source_record())
    assert root.exists()
    assert not (root / "normalization_manifest.json").exists()
    with pytest.raises(SchemaContractError, match="incomplete"):
        run_normalization(
            tmp_path,
            authorization_path,
            root,
        )


def test_main_uses_fixed_argument_surface_without_extra_commands(
    tmp_path: Path,
) -> None:
    with pytest.raises(SystemExit):
        main(["--unknown-option"])
    assert not list(tmp_path.rglob("*"))


def test_actual_normalizer_source_passes_static_capability_guard() -> None:
    source = Path(normalizer.__file__).read_text(encoding="utf-8")
    validate_normalizer_static_source(source)
