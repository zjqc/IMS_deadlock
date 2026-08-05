from __future__ import annotations

import hashlib
import inspect
import json
import sys
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from typing import Any, cast

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ims_deadlock import g6b_retired_normalizer as normalizer
from ims_deadlock import g6b_schema_contracts as contracts
from ims_deadlock.g4_instances import (
    ADVERSARIAL_GENERATOR_ID,
    BIDIRECTIONAL_GENERATOR_ID,
    MEDIUM_ISLAND_GENERATOR_ID,
    AdversarialBoundaryParameters,
    BidirectionalGridCell,
    MediumIslandParameters,
    build_adversarial_boundary_case,
    build_bidirectional_island_case,
    build_medium_island_case,
)
from ims_deadlock.g6b_canonical_json import (
    canonical_bytes_v2,
    canonical_sha256_v2,
    finalized_self_hash,
    loads_v2,
)
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
from ims_deadlock.g6b_schema_contracts import (
    SchemaContractError,
    validate_normalizer_static_source,
)

JsonObject = dict[str, Any]

_G4_CASE_PATH = "cases/confirmation/g4/cases/G4_IMS_PARAMETER_GRID.json"
_G4_MANIFEST_PATH = "cases/confirmation/g4/case_manifest.json"
_RAW_ONLY_PATH = "cases/confirmation/g4/baseline_applicability.json"
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
_ROW_FAMILY_ROOT = (
    Path(__file__).resolve().parents[1]
    / "cases"
    / "discovery"
    / "g6b"
    / "row_families"
    / "structural_discovery_v1"
)
_RETIRED_AUTHORITY_SCHEMA = (
    _ROW_FAMILY_ROOT / "retired_authority_fingerprint_schema.json"
)


def _load_retired_schema_definition() -> JsonObject:
    return cast(
        JsonObject,
        json.loads(_RETIRED_AUTHORITY_SCHEMA.read_text(encoding="utf-8")),
    )


def _selector_rows() -> list[JsonObject]:
    return deepcopy(_load_retired_schema_definition()["allowed_json_fields_by_source"])


def _canonical_json_bytes(value: JsonObject) -> bytes:
    return canonical_bytes_v2(value)


def _json_bytes(text: str) -> bytes:
    return text.encode("utf-8")


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _read_json(path: Path) -> JsonObject:
    value = loads_v2(str(path.read_bytes(), "utf-8"))
    assert isinstance(value, dict)
    return value


def _normalization_root(tmp_path: Path) -> Path:
    root = tmp_path / contracts.NORMALIZATION_ALLOWED_OUTPUT_ROOT_PATH
    root.parent.mkdir(parents=True, exist_ok=True)
    return root


def _git_sha1(label: str) -> str:
    return hashlib.sha1(canonical_bytes_v2({"synthetic_git_object": label})).hexdigest()


def _synthetic_hash(label: str) -> str:
    return canonical_sha256_v2({"synthetic_label": label})


def _projection_for_dimension(dimension: str) -> JsonObject:
    payloads: dict[str, JsonObject] = {
        "case_content_sha256": {
            "projection_schema_version": "v1",
            "input_mode": "model_generated_lts",
            "input_semantics_version": "v1",
            "state_snapshot_sha256": "a" * 64,
            "route_signature_sha256": "b" * 64,
            "parameter_tuple_sha256": "c" * 64,
            "rate_manifest_content_sha256": "d" * 64,
            "policy_declaration_content_sha256": "e" * 64,
            "selected_target_declaration_sha256": "f" * 64,
            "control_declaration_sha256": "0" * 64,
        },
        "state_snapshot_sha256": {
            "projection_schema_version": "v1",
            "input_mode": "model_generated_lts",
            "state_payload_schema_version": "state-v1",
            "state_payload": {"states": ["s0"]},
        },
        "route_signature_sha256": {
            "projection_schema_version": "v1",
            "input_mode": "model_generated_lts",
            "route_semantics_version": "route-v1",
            "typed_resource_roles": [],
            "typed_route_graph": [],
            "transition_kinds": [],
            "resource_demand_structure": [],
            "mode_transition_structure": [],
        },
        "parameter_tuple_sha256": {
            "projection_schema_version": "v1",
            "parameter_semantics_version": "params-v1",
            "structural_parameter_entries": [],
            "numeric_parameter_entries": [],
            "state_bound": 1,
            "rate_manifest_content_sha256": "d" * 64,
            "policy_declaration_content_sha256": "e" * 64,
        },
        "random_stream_manifest_sha256": {
            "projection_schema_version": "v1",
            "applicability_status": "not_applicable_by_protocol",
            "method_role": "exact_companion",
            "reason_code": "exact_method_has_no_random_stream",
        },
        "sealed_prediction_sha256": {
            "projection_schema_version": "v1",
            "research_question": "question",
            "directional_hypotheses": [],
            "falsifiers": [],
            "mandatory_control_roles": [],
            "planned_method_roles": ["des_companion", "exact_companion"],
            "scoring_rule": {"scoring_rule_id": "rule-a"},
            "claim_boundary": {"study_role": "discovery_only"},
        },
        "metric_schema_sha256": {
            "projection_schema_version": "v1",
            "estimand_schema_version": "v2",
            "metric_entries": [],
            "aggregation_rules": [],
            "censoring_rules": [],
            "failure_rules": [],
            "scoring_rules": [],
            "comparability_scope": "same_target_companion_group",
        },
    }
    return dict(payloads[dimension])


def _subject_id_for_dimension(dimension: str) -> str:
    subject_kind = contracts.DIMENSION_SUBJECTS[dimension]
    if subject_kind == "case_unit":
        return "G4_IMS_PARAMETER_GRID"
    if subject_kind == "method_observation":
        return "retired-method-observation-test"
    if subject_kind == "method_companion_group":
        return "retired-method-companion-group-test"
    raise AssertionError(f"unhandled subject kind: {subject_kind}")


def _authorization_record() -> JsonObject:
    schema = _load_retired_schema_definition()
    record: JsonObject = {
        "schema_version": "ims-deadlock/g6b-retired-normalization-authorization/v1",
        "authorization_id": "retired-normalization-test-auth",
        "capability": "retired_authority_fingerprint_normalization",
        "authorized": True,
        "source_head": _git_sha1("normalization-source-head"),
        "source_tree_hash": _git_sha1("normalization-source-tree"),
        "authority_ids": list(schema["retired_authority_ids"]),
        "expected_file_manifest_hash": _synthetic_hash("expected-file-manifest"),
        "allowed_source_paths": list(
            contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY
        ),
        "allowed_json_fields_by_source": deepcopy(
            schema["allowed_json_fields_by_source"]
        ),
        "allowed_historical_builder_symbols": [],
        "normalizer_code_sha256": _synthetic_hash("normalizer-code"),
        "allowed_operations": list(contracts.NORMALIZATION_ALLOWED_OPERATIONS),
        "allowed_project_imports": list(
            contracts.NORMALIZATION_ALLOWED_PROJECT_IMPORTS
        ),
        "forbidden_imports": list(contracts.NORMALIZATION_FORBIDDEN_IMPORTS),
        "forbidden_calls": list(contracts.NORMALIZATION_FORBIDDEN_CALLS),
        "allowed_output_schema": dict(contracts.NORMALIZATION_ALLOWED_OUTPUT_SCHEMA),
        "allowed_output_root": {
            "repo_relative_posix_path": (
                contracts.NORMALIZATION_ALLOWED_OUTPUT_ROOT_PATH
            ),
            "contains_only_governance_outputs": True,
        },
        "review_artifact_hash": _synthetic_hash("review-artifact"),
        "issued_at_utc": "2030-01-01T00:00:00Z",
        "invalidated_by_identity_drift": False,
        "authorization_sha256": None,
    }
    record["authorization_sha256"] = finalized_self_hash(
        record,
        "authorization_sha256",
    )
    return record


def _authority_id_for_retired_path(path: str) -> str:
    if path.startswith("cases/confirmation/g4/"):
        return "G4_FREEZE"
    if path.startswith("evidence/g5/"):
        return "G5_EXECUTION"
    return "G6_R_REPLAY_R3"


def _allowed_projection_uses_for_path(path: str) -> list[str]:
    uses: set[str] = set()

    def expanded_patterns(pattern: str) -> list[str]:
        if "{case_id}" in pattern:
            return [
                pattern.replace("{case_id}", case_id)
                for case_id in contracts.G4_MANIFEST_CASE_IDS
            ]
        if "{" in pattern:
            prefix, remainder = pattern.split("{", 1)
            alternatives, suffix = remainder.split("}", 1)
            return [
                f"{prefix}{alternative}{suffix}"
                for alternative in alternatives.split(",")
            ]
        return [pattern]

    for row in _selector_rows():
        if path in expanded_patterns(row["source_path_pattern"]):
            uses.add(row["allowed_use"])
    return sorted(uses) or ["source_hash_validation"]


def _retired_source_hashes() -> dict[str, str]:
    return {
        path: canonical_sha256_v2({"synthetic_source_path": path})
        for path in contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY
    }


def _authority_lock_record(authority_id: str = _LOCK_AUTHORITY_ID) -> JsonObject:
    record: JsonObject = {
        "authority_id": authority_id,
        "origin_remote": "retired-authority-logical-origin",
        "origin_commit_or_null": _git_sha1(f"{authority_id}:origin-commit"),
        "origin_tree_hash_or_null": _git_sha1(f"{authority_id}:origin-tree"),
        "origin_lock_artifact_ref": (
            "cases/discovery/g6b/row_families/structural_discovery_v1/"
            f"governance/retired_authority_locks/{authority_id}.json"
        ),
        "origin_artifact_inventory_hash": _synthetic_hash(
            f"{authority_id}:artifact-inventory"
        ),
        "current_merged_copy_tree_hash": _synthetic_hash(
            f"{authority_id}:merged-copy-tree"
        ),
        "identity_verification_status": (
            "verified_merged_copy_against_historical_hashes"
        ),
        "authority_lock_record_sha256": None,
    }
    record["authority_lock_record_sha256"] = finalized_self_hash(
        record,
        "authority_lock_record_sha256",
    )
    return record


def _authority_lock_records() -> dict[str, JsonObject]:
    schema = _load_retired_schema_definition()
    return {
        authority_id: _authority_lock_record(authority_id)
        for authority_id in schema["retired_authority_ids"]
    }


def _authority_lock_hashes(
    lock_records: dict[str, JsonObject] | None = None,
) -> dict[str, str]:
    records = _authority_lock_records() if lock_records is None else lock_records
    return {
        authority_id: record["authority_lock_record_sha256"]
        for authority_id, record in records.items()
    }


def _authority_source_record(
    path: str = _G4_CASE_PATH,
    *,
    authority_lock_record_sha256: str | None = None,
) -> JsonObject:
    authority_id = _authority_id_for_retired_path(path)
    lock_hash = (
        _authority_lock_record(authority_id)["authority_lock_record_sha256"]
        if authority_lock_record_sha256 is None
        else authority_lock_record_sha256
    )
    raw_hash = canonical_sha256_v2({"synthetic_source_path": path})
    return {
        "authority_id": authority_id,
        "authority_stage": authority_id,
        "authority_lock_record_sha256": lock_hash,
        "repo_relative_path": path,
        "raw_byte_sha256": raw_hash,
        "declared_historical_hash_or_null": raw_hash,
        "declared_hash_algorithm_or_null": "sha256",
        "declared_hash_verified": True,
        "allowed_projection_uses": _allowed_projection_uses_for_path(path),
        "contains_outcome_fields": path == "evidence/g5/G5_RESULT_SUMMARY.json",
    }


def _authority_source_records(locks: dict[str, JsonObject]) -> dict[str, JsonObject]:
    return {
        path: _authority_source_record(
            path,
            authority_lock_record_sha256=locks[_authority_id_for_retired_path(path)][
                "authority_lock_record_sha256"
            ],
        )
        for path in contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY
    }


def _normalization_source_refs_for_dimension(dimension: str) -> list[JsonObject]:
    g4_case = _G4_CASE_PATH
    refs_by_dimension: dict[str, list[JsonObject]] = {
        "case_content_sha256": [
            {
                "authority_id": "G4_FREEZE",
                "repo_relative_posix_path": g4_case,
                "json_pointer_or_null": "/input_payload",
                "source_role": "case_content_projection",
            }
        ],
        "state_snapshot_sha256": [
            {
                "authority_id": "G4_FREEZE",
                "repo_relative_posix_path": g4_case,
                "json_pointer_or_null": "/input_payload",
                "source_role": "case_content_projection",
            }
        ],
        "route_signature_sha256": [
            {
                "authority_id": "G4_FREEZE",
                "repo_relative_posix_path": g4_case,
                "json_pointer_or_null": "/input_payload",
                "source_role": "case_content_projection",
            }
        ],
        "parameter_tuple_sha256": [
            {
                "authority_id": "G4_FREEZE",
                "repo_relative_posix_path": g4_case,
                "json_pointer_or_null": "/input_payload",
                "source_role": "case_content_projection",
            }
        ],
        "random_stream_manifest_sha256": [
            {
                "authority_id": "G4_FREEZE",
                "repo_relative_posix_path": (
                    "cases/confirmation/g4/random_stream_manifest.json"
                ),
                "json_pointer_or_null": "/streams_by_case",
                "source_role": "random_stream_projection",
            }
        ],
        "sealed_prediction_sha256": [
            {
                "authority_id": "G4_FREEZE",
                "repo_relative_posix_path": "cases/confirmation/g4/predictions.json",
                "json_pointer_or_null": "/predictions",
                "source_role": "prediction_projection",
            }
        ],
        "metric_schema_sha256": [
            {
                "authority_id": "G4_FREEZE",
                "repo_relative_posix_path": (
                    "cases/confirmation/g4/metrics_schema.json"
                ),
                "json_pointer_or_null": "/metrics",
                "source_role": "metric_projection",
            }
        ],
    }
    return refs_by_dimension[dimension]


def _source_hashes_for_refs(refs: list[JsonObject]) -> dict[str, str]:
    retired_hashes = _retired_source_hashes()
    return {
        ref["repo_relative_posix_path"]: retired_hashes[ref["repo_relative_posix_path"]]
        for ref in refs
    }


def _fingerprint_record(record_id: str = _FINGERPRINT_ID) -> JsonObject:
    dimension = "case_content_sha256"
    projection = _projection_for_dimension(dimension)
    projection_hash = canonical_sha256_v2(projection)
    refs = _normalization_source_refs_for_dimension(dimension)
    record: JsonObject = {
        "record_schema_version": "ims-deadlock/g6b-fingerprint-record/v1",
        "record_id": record_id,
        "dimension": dimension,
        "projection_kind": contracts.DIMENSION_PROJECTION_KINDS[dimension],
        "subject_type": contracts.DIMENSION_SUBJECTS[dimension],
        "subject_id": _subject_id_for_dimension(dimension),
        "owner_object_id": _subject_id_for_dimension(dimension),
        "projection_schema_version": projection["projection_schema_version"],
        "comparison_projection_ref_or_null": f"synthetic://projection/{dimension}",
        "comparison_projection_sha256_or_null": projection_hash,
        "canonicalization_version": contracts.G6B_CANONICAL_JSON_VERSION,
        "source_authority_id": "G4_FREEZE",
        "source_stage": "G4_FREEZE",
        "source_method_role_or_null": None,
        "source_run_role_or_null": None,
        "source_artifact_refs": refs,
        "source_artifact_byte_hashes": _source_hashes_for_refs(refs),
        "normalizer_version": "retired-authority-normalizer-test-v1",
        "dimension_status": "derived_by_versioned_normalizer",
        "lineage_id": "pending-lineage",
        "inherited_from_record_id_or_null": None,
        "duplicate_lineage_of_record_id_or_null": None,
        "depends_on_dimensions": sorted(contracts.DIMENSION_DEPENDS_ON[dimension]),
        "correlated_with_dimensions": sorted(
            contracts.DIMENSION_CORRELATED_WITH[dimension]
        ),
        "comparison_policy": contracts.DIMENSION_POLICIES[dimension],
        "applicability_reason_code_or_null": None,
        "record_provenance_sha256": None,
    }
    lineage_preimage = {
        "origin_authority_id": record["source_authority_id"],
        "origin_subject_type": record["subject_type"],
        "origin_subject_id": record["subject_id"],
        "origin_dimension": record["dimension"],
        "origin_comparison_projection_sha256_or_null": record[
            "comparison_projection_sha256_or_null"
        ],
        "origin_source_artifact_byte_hashes": record["source_artifact_byte_hashes"],
    }
    record["lineage_id"] = f"sha256:{canonical_sha256_v2(lineage_preimage)}"
    record["record_provenance_sha256"] = finalized_self_hash(
        record,
        "record_provenance_sha256",
    )
    return record


def _fingerprint_records() -> dict[str, JsonObject]:
    return {_FINGERPRINT_ID: _fingerprint_record(_FINGERPRINT_ID)}


def _manifest_record(
    *,
    authorization_sha256: str,
    authority_lock_hash: str | None = None,
    source_record_hash: str | None = None,
    fingerprint_hash: str | None = None,
) -> JsonObject:
    locks = _authority_lock_records()
    sources = _authority_source_records(locks)
    fingerprints = _fingerprint_records()
    if authority_lock_hash is not None:
        locks[_LOCK_AUTHORITY_ID]["authority_lock_record_sha256"] = authority_lock_hash
    if source_record_hash is not None:
        sources[_G4_CASE_PATH] = _authority_source_record(
            _G4_CASE_PATH,
            authority_lock_record_sha256=locks[_LOCK_AUTHORITY_ID][
                "authority_lock_record_sha256"
            ],
        )
    if fingerprint_hash is not None:
        fingerprints[_FINGERPRINT_ID]["record_provenance_sha256"] = fingerprint_hash
    unique_lineage_map = {
        record["lineage_id"]: sorted(
            other["record_id"]
            for other in fingerprints.values()
            if other["lineage_id"] == record["lineage_id"]
        )
        for record in sorted(fingerprints.values(), key=lambda item: item["lineage_id"])
    }
    dimension_status_counts = {
        status: sum(
            1
            for record in fingerprints.values()
            if record["dimension_status"] == status
        )
        for status in contracts.DIMENSION_STATUS_VALUES
    }
    comparison_eligibility = {
        record_id: {
            "eligible_for_overlap_comparison": (
                record["dimension_status"] != "unreconstructable_refuse"
            ),
            "refusal_reason_code_or_null": (
                "retired_projection_unreconstructable"
                if record["dimension_status"] == "unreconstructable_refuse"
                else None
            ),
        }
        for record_id, record in fingerprints.items()
    }
    manifest: JsonObject = {
        "schema_version": "ims-deadlock/g6b-retired-normalization-manifest/v1",
        "manifest_id": "retired-normalization-manifest-test",
        "source_remote": "retired-authority-logical-origin",
        "source_head": _git_sha1("normalization-manifest-source-head"),
        "source_tree_hash": _git_sha1("normalization-manifest-source-tree"),
        "source_dirty_state": "clean",
        "authority_ids": list(
            _load_retired_schema_definition()["retired_authority_ids"]
        ),
        "expected_file_manifest": dict(sorted(_retired_source_hashes().items())),
        "verified_file_byte_hashes": dict(sorted(_retired_source_hashes().items())),
        "frozen_hash_validation_results": {
            path: {
                "declared_sha256": digest,
                "observed_sha256": digest,
                "status": "match",
            }
            for path, digest in sorted(_retired_source_hashes().items())
        },
        "historical_canonicalization_versions": {
            authority_id: contracts.G6B_CANONICAL_JSON_VERSION for authority_id in locks
        },
        "projection_canonicalization_version": contracts.G6B_CANONICAL_JSON_VERSION,
        "normalizer_version": "retired-authority-normalizer-test-v1",
        "normalizer_code_sha256": _synthetic_hash("normalizer-code"),
        "normalization_authorization_sha256": authorization_sha256,
        "authority_lock_record_hashes": {
            authority_id: record["authority_lock_record_sha256"]
            for authority_id, record in locks.items()
        },
        "authority_source_record_hashes": dict(
            sorted(
                (path, canonical_sha256_v2(record)) for path, record in sources.items()
            )
        ),
        "fingerprint_record_hashes": {
            record_id: record["record_provenance_sha256"]
            for record_id, record in sorted(fingerprints.items())
        },
        "unique_lineage_map": unique_lineage_map,
        "dimension_status_counts": dimension_status_counts,
        "missing_source_records": [],
        "unreconstructable_records": [],
        "comparison_eligibility": dict(sorted(comparison_eligibility.items())),
        "created_at_utc": "2030-01-01T00:00:00Z",
        "manifest_sha256": None,
    }
    manifest["manifest_sha256"] = finalized_self_hash(manifest, "manifest_sha256")
    return manifest


def _write_manifest_inputs(
    tmp_path: Path,
    *,
    omit_lock: str | None = None,
    omit_source: str | None = None,
    omit_fingerprint: str | None = None,
) -> tuple[Path, JsonObject]:
    root = _normalization_root(tmp_path)
    authorization_sha = write_normalization_authorization(
        root,
        _canonical_json_bytes(_authorization_record()),
    )
    locks = _authority_lock_records()
    for authority_id, record in locks.items():
        if authority_id != omit_lock:
            write_authority_lock_record(root, authority_id, record)
    sources = _authority_source_records(locks)
    for path, record in sources.items():
        if path != omit_source:
            write_authority_source_record(root, path, record)
    for record_id, record in _fingerprint_records().items():
        if record_id != omit_fingerprint:
            write_fingerprint_record(root, record_id, record)
    return root, _manifest_record(authorization_sha256=authorization_sha)


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
        ("/case_id", "lineage_link", "G4_IMS_PARAMETER_GRID"),
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
    source_payloads = {
        path: f"synthetic-source:{path}".encode()
        for path in authorization["allowed_source_paths"]
    }
    for path, raw in source_payloads.items():
        destination = tmp_path / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
    source_hashes = {
        path: hashlib.sha256(raw).hexdigest() for path, raw in source_payloads.items()
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
    root = _normalization_root(tmp_path)
    authorization_bytes = _canonical_json_bytes(_authorization_record())
    written_sha = write_normalization_authorization(root, authorization_bytes)
    destination = root / "normalization_authorization.json"
    assert root.is_dir()
    assert destination.read_bytes() == authorization_bytes
    assert written_sha == hashlib.sha256(authorization_bytes).hexdigest()
    with pytest.raises(SchemaContractError, match="preexisting"):
        write_normalization_authorization(root, authorization_bytes)


def test_writers_reject_root_without_exact_authorized_relative_suffix(
    tmp_path: Path,
) -> None:
    authorization_bytes = _canonical_json_bytes(_authorization_record())
    arbitrary_root = tmp_path / "arbitrary"
    with pytest.raises(SchemaContractError, match="output_root_contract_drift"):
        write_normalization_authorization(arbitrary_root, authorization_bytes)
    assert not arbitrary_root.exists()

    arbitrary_root.mkdir()
    (arbitrary_root / "normalization_authorization.json").write_bytes(
        authorization_bytes
    )
    with pytest.raises(SchemaContractError, match="output_root_contract_drift"):
        write_authority_lock_record(
            arbitrary_root,
            _LOCK_AUTHORITY_ID,
            _authority_lock_record(),
        )


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
    root = _normalization_root(tmp_path)
    write_normalization_authorization(
        root,
        _canonical_json_bytes(_authorization_record()),
    )
    written_sha = writer(root, record)
    destination = root / expected_relative
    assert destination.is_file(), writer_name
    assert destination.read_bytes() == canonical_bytes_v2(record)
    assert hashlib.sha256(destination.read_bytes()).hexdigest()
    if writer_name == "authority_lock":
        assert written_sha == record["authority_lock_record_sha256"]
    elif writer_name == "fingerprint":
        assert written_sha == record["record_provenance_sha256"]
    else:
        assert written_sha == hashlib.sha256(destination.read_bytes()).hexdigest()
    with pytest.raises(SchemaContractError, match="preexisting"):
        writer(root, record)


def test_writers_reject_absolute_parent_misnamed_and_preexisting_paths(
    tmp_path: Path,
) -> None:
    root = _normalization_root(tmp_path)
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
    root = _normalization_root(tmp_path)
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


def test_authorization_writer_rejects_symlinked_root_ancestor(
    tmp_path: Path,
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    linked_repo = tmp_path / "linked-repo"
    try:
        linked_repo.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable on this platform: {exc}")
    root = linked_repo / contracts.NORMALIZATION_ALLOWED_OUTPUT_ROOT_PATH
    with pytest.raises(SchemaContractError, match="symlink"):
        write_normalization_authorization(
            root,
            _canonical_json_bytes(_authorization_record()),
        )
    assert not (outside / contracts.NORMALIZATION_ALLOWED_OUTPUT_ROOT_PATH).exists()


def test_manifest_writer_is_last_and_verifies_referenced_record_bytes(
    tmp_path: Path,
) -> None:
    root = _normalization_root(tmp_path)
    authorization_bytes = _canonical_json_bytes(_authorization_record())
    authorization_sha = write_normalization_authorization(root, authorization_bytes)
    locks = _authority_lock_records()
    written_lock_hashes = {
        authority_id: write_authority_lock_record(root, authority_id, record)
        for authority_id, record in locks.items()
    }
    assert written_lock_hashes == {
        authority_id: record["authority_lock_record_sha256"]
        for authority_id, record in locks.items()
    }
    sources = _authority_source_records(locks)
    written_source_hashes = {
        path: write_authority_source_record(root, path, record)
        for path, record in sources.items()
    }
    assert written_source_hashes == {
        path: canonical_sha256_v2(record) for path, record in sources.items()
    }
    fingerprint_sha = write_fingerprint_record(
        root,
        _FINGERPRINT_ID,
        _fingerprint_record(),
    )
    assert fingerprint_sha == _fingerprint_record()["record_provenance_sha256"]
    manifest = _manifest_record(authorization_sha256=authorization_sha)
    assert manifest["authority_lock_record_hashes"] == written_lock_hashes
    assert manifest["authority_source_record_hashes"] == written_source_hashes
    assert manifest["fingerprint_record_hashes"] == {_FINGERPRINT_ID: fingerprint_sha}
    destination = root / "normalization_manifest.json"
    assert not destination.exists()
    manifest_sha = write_normalization_manifest(root, manifest)
    assert destination.read_bytes() == canonical_bytes_v2(manifest)
    assert manifest_sha == hashlib.sha256(destination.read_bytes()).hexdigest()
    with pytest.raises(SchemaContractError, match="preexisting"):
        write_normalization_manifest(root, manifest)


def test_manifest_writer_rejects_rehashed_malformed_source_record(
    tmp_path: Path,
) -> None:
    root = _normalization_root(tmp_path)
    authorization_sha = write_normalization_authorization(
        root,
        _canonical_json_bytes(_authorization_record()),
    )
    locks = _authority_lock_records()
    for authority_id, record in locks.items():
        write_authority_lock_record(root, authority_id, record)
    sources = _authority_source_records(locks)
    malformed_path = sorted(sources)[0]
    malformed = dict(sources[malformed_path])
    malformed["unexpected"] = "must-refuse"
    written_source_hashes: dict[str, str] = {}
    for path, record in sources.items():
        written_source_hashes[path] = write_authority_source_record(
            root,
            path,
            malformed if path == malformed_path else record,
        )
    write_fingerprint_record(root, _FINGERPRINT_ID, _fingerprint_record())
    manifest = _manifest_record(authorization_sha256=authorization_sha)
    manifest["authority_source_record_hashes"] = written_source_hashes
    manifest["manifest_sha256"] = None
    manifest["manifest_sha256"] = finalized_self_hash(manifest, "manifest_sha256")
    with pytest.raises(SchemaContractError):
        write_normalization_manifest(root, manifest)
    assert not (root / "normalization_manifest.json").exists()


def test_manifest_writer_refuses_before_all_records_exist(tmp_path: Path) -> None:
    root = _normalization_root(tmp_path)
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
    root = _normalization_root(tmp_path)
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


def test_public_surface_all_and_signatures_are_closed() -> None:
    assert normalizer.__all__ == (
        "select_allowed_value",
        "build_authority_lock_records",
        "build_authority_source_records",
        "build_retired_fingerprint_records",
        "write_normalization_authorization",
        "write_authority_lock_record",
        "write_authority_source_record",
        "write_fingerprint_record",
        "write_normalization_manifest",
        "run_normalization",
        "main",
    )
    signatures = {
        name: str(inspect.signature(getattr(normalizer, name)))
        for name in normalizer.__all__
    }
    assert signatures == {
        "select_allowed_value": (
            "(source_bytes: 'bytes', *, pointer: 'str', "
            "selector_rows: 'Sequence[Mapping[str, JsonValue]]', "
            "requested_use: 'str') -> 'JsonValue'"
        ),
        "build_authority_lock_records": (
            "(repo_root: 'Path', authorization: 'Mapping[str, JsonValue]', "
            "source_hashes: 'Mapping[str, str]') -> 'dict[str, JsonObject]'"
        ),
        "build_authority_source_records": (
            "(repo_root: 'Path', authorization: 'Mapping[str, JsonValue]', "
            "authority_locks: 'Mapping[str, Mapping[str, JsonValue]]') -> "
            "'dict[str, JsonObject]'"
        ),
        "build_retired_fingerprint_records": (
            "(repo_root: 'Path', authorization: 'Mapping[str, JsonValue]', "
            "authority_locks: 'Mapping[str, Mapping[str, JsonValue]]', "
            "source_records: 'Mapping[str, Mapping[str, JsonValue]]') -> "
            "'dict[str, JsonObject]'"
        ),
        "write_normalization_authorization": (
            "(authorized_root: 'Path', authorization_bytes: 'bytes') -> 'str'"
        ),
        "write_authority_lock_record": (
            "(authorized_root: 'Path', authority_id: 'str', "
            "record: 'Mapping[str, JsonValue]') -> 'str'"
        ),
        "write_authority_source_record": (
            "(authorized_root: 'Path', repo_relative_source_path: 'str', "
            "record: 'Mapping[str, JsonValue]') -> 'str'"
        ),
        "write_fingerprint_record": (
            "(authorized_root: 'Path', record_id: 'str', "
            "record: 'Mapping[str, JsonValue]') -> 'str'"
        ),
        "write_normalization_manifest": (
            "(authorized_root: 'Path', manifest: 'Mapping[str, JsonValue]') -> 'str'"
        ),
        "run_normalization": (
            "(repo_root: 'Path', authorization_path: 'Path', output_root: 'Path') "
            "-> 'JsonObject'"
        ),
        "main": "(argv: 'Sequence[str] | None' = None) -> 'int'",
    }


def test_authorization_writer_rejects_noncanonical_bytes_before_root_creation(
    tmp_path: Path,
) -> None:
    root = _normalization_root(tmp_path)
    noncanonical = json.dumps(_authorization_record(), indent=2).encode("utf-8")
    with pytest.raises(SchemaContractError, match="noncanonical_authorization"):
        write_normalization_authorization(root, noncanonical)
    assert not root.exists()


def test_source_reader_rejects_escape_symlink_and_hash_mismatch_before_parse(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    source_path = repo / _G4_CASE_PATH
    source_path.parent.mkdir(parents=True)
    source_path.write_bytes(b"{not-json")
    outside = tmp_path / "outside.json"
    outside.write_bytes(b'{"ok":true}')
    link = repo / "link.json"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable on this platform: {exc}")
    with pytest.raises(SchemaContractError, match="source_outside_retired_inventory"):
        normalizer._read_authorized_source_bytes(
            repo,
            "../outside.json",
            {str(Path("../outside.json")): _SHA_A},
        )
    with pytest.raises(SchemaContractError, match="symlink"):
        normalizer._read_authorized_source_bytes(
            repo,
            "link.json",
            {"link.json": hashlib.sha256(outside.read_bytes()).hexdigest()},
        )
    with pytest.raises(SchemaContractError, match="retired_authority_hash_mismatch"):
        normalizer._read_authorized_source_bytes(
            repo,
            _G4_CASE_PATH,
            {_G4_CASE_PATH: _SHA_A},
        )


def test_raw_bytes_only_reader_does_not_parse_hash_matched_invalid_json(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    source_path = repo / _RAW_ONLY_PATH
    source_path.parent.mkdir(parents=True)
    raw = b"{not-json"
    source_path.write_bytes(raw)
    assert (
        normalizer._read_authorized_source_bytes(
            repo,
            _RAW_ONLY_PATH,
            {_RAW_ONLY_PATH: hashlib.sha256(raw).hexdigest()},
        )
        == raw
    )


def test_output_root_helper_requires_exact_contained_authorized_path(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    expected = repo / contracts.NORMALIZATION_ALLOWED_OUTPUT_ROOT_PATH
    expected.parent.mkdir(parents=True)
    authorization = _authorization_record()
    normalizer._verify_output_root(repo, expected, authorization)
    with pytest.raises(SchemaContractError, match="output_root_contract_drift"):
        normalizer._verify_output_root(repo, repo / "sibling-root", authorization)
    escaped = dict(authorization)
    escaped["allowed_output_root"] = {
        "repo_relative_posix_path": "../escape",
        "contains_only_governance_outputs": True,
    }
    with pytest.raises(SchemaContractError, match="output_root_contract_drift"):
        normalizer._verify_output_root(repo, tmp_path / "escape", escaped)
    absolute = dict(authorization)
    absolute["allowed_output_root"] = {
        "repo_relative_posix_path": str(tmp_path / "absolute"),
        "contains_only_governance_outputs": True,
    }
    with pytest.raises(SchemaContractError, match="output_root_contract_drift"):
        normalizer._verify_output_root(repo, tmp_path / "absolute", absolute)
    outside = tmp_path / "outside"
    outside.mkdir()
    symlink_root = repo / contracts.NORMALIZATION_ALLOWED_OUTPUT_ROOT_PATH
    try:
        symlink_root.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable on this platform: {exc}")
    with pytest.raises(SchemaContractError, match="symlink"):
        normalizer._verify_output_root(repo, symlink_root, authorization)


def test_manifest_writer_rereads_actual_record_bytes_before_finalizing(
    tmp_path: Path,
) -> None:
    root = _normalization_root(tmp_path)
    authorization_sha = write_normalization_authorization(
        root,
        _canonical_json_bytes(_authorization_record()),
    )
    locks = _authority_lock_records()
    for authority_id, record in locks.items():
        write_authority_lock_record(root, authority_id, record)
    sources = _authority_source_records(locks)
    for path, record in sources.items():
        write_authority_source_record(root, path, record)
    write_fingerprint_record(root, _FINGERPRINT_ID, _fingerprint_record())
    tampered = dict(locks[_LOCK_AUTHORITY_ID])
    tampered["origin_remote"] = "tampered"
    (root / "authority_locks" / f"{_LOCK_AUTHORITY_ID}.json").write_bytes(
        canonical_bytes_v2(tampered)
    )
    with pytest.raises(SchemaContractError, match="manifest_last"):
        write_normalization_manifest(
            root,
            _manifest_record(authorization_sha256=authorization_sha),
        )


@pytest.mark.parametrize(
    "omissions",
    [
        {"omit_lock": "G4_FREEZE"},
        {"omit_source": _G4_CASE_PATH},
        {"omit_fingerprint": _FINGERPRINT_ID},
    ],
)
def test_manifest_writer_requires_exact_directory_key_closure(
    tmp_path: Path,
    omissions: dict[str, str],
) -> None:
    missing_root, missing_manifest = _write_manifest_inputs(
        tmp_path / "missing", **omissions
    )
    with pytest.raises(SchemaContractError, match="manifest_last"):
        write_normalization_manifest(missing_root, missing_manifest)


def test_unreconstructable_fingerprint_projection_is_subject_free() -> None:
    fingerprints = build_retired_fingerprint_records(
        Path("synthetic"),
        _authorization_record(),
        _authority_lock_records(),
        _authority_source_records(_authority_lock_records()),
    )
    for record in fingerprints.values():
        assert record["dimension_status"] == "unreconstructable_refuse"
        assert record["comparison_projection_sha256_or_null"] is None
        assert record["comparison_projection_ref_or_null"] is None
        assert "_for_test_" not in "".join(record)


_TASK6_G4_KIND_BY_CASE = {
    "G4_ADVERSARIAL_BOUNDARY": "adversarial_snapshot",
    "G4_B05_SUPERVISOR_COMPARATOR": "adapted_candidate_monitor_cover",
    "G4_CRP_OUTSIDE_S4PR": "crp_evidence_audit",
    "G4_CRP_S4PR_AGREE": "crp_evidence_audit",
    "G4_CRP_UNREACHABLE_CANDIDATE": "crp_evidence_audit",
    "G4_IMS_PARAMETER_GRID": "bidirectional_island_grid",
    "G4_L30_RESOURCE_BASELINE": "supplied_l30_inequalities",
    "G4_MEDIUM_ISLAND_REBUILD": "medium_island_rebuild",
    "G4_RECORDER_TARGET_QUANTIFICATION": "fixed_recorder_target",
}

_TASK6_FORBIDDEN_OUTCOME_NAMES = (
    "actual_overlap_result",
    "completion_probability",
    "deadlock_probability",
    "mean_absorption_time",
    "metric_observations",
    "outcome_observation",
    "post_outcome_rationale",
    "score",
    "stderr_raw_sha256",
    "stdout",
    "theorem_prediction_status_observed",
)

_TASK6_SUBJECT_PROJECTION_KEYS = (
    "subject_id",
    "owner_object_id",
    "repo_relative_path",
    "display_name",
    "author",
    "timestamp",
)

_TASK6_RETIRED_SUBJECT_TYPE_BY_DIMENSION = {
    "case_content_sha256": "retired_case",
    "state_snapshot_sha256": "retired_case",
    "route_signature_sha256": "retired_case",
    "parameter_tuple_sha256": "retired_case",
    "random_stream_manifest_sha256": "retired_method_observation",
    "output_root_reservation_sha256": "retired_method_observation",
    "sealed_prediction_sha256": "retired_case",
    "metric_schema_sha256": "retired_method_companion_group",
}
_TASK6_HAS_RECONSTRUCTABLE_PROJECTION: JsonObject = {
    "projection_assertion": "has_reconstructable_projection"
}


def _task6_case_path(case_id: str) -> str:
    return f"cases/confirmation/g4/cases/{case_id}.json"


def _task6_grid_cell() -> JsonObject:
    return {
        "cell_id": "ims_cell_01",
        "machine_capacity": 1,
        "buffer_capacity": 1,
        "agv_count": 1,
        "forward_wip": 1,
        "reverse_wip": 1,
        "service_rate": 1,
        "transfer_rate": 1,
        "release_rate": 1,
        "state_bound": 8,
    }


def _task6_medium_parameters() -> JsonObject:
    return {
        "instance_id": "medium_a",
        "machine_capacity": 1,
        "buffer_capacity": 1,
        "agv_count": 1,
        "route_wip": {"ABG": 1, "AG": 1, "BAG": 1},
        "service_rate": 1,
        "transfer_rate": 1,
        "release_rate": 1,
        "state_bound": 16,
    }


def _task6_adversarial_parameters() -> JsonObject:
    return {
        "instance_id": "boundary_a",
        "fixture_capacity": 2,
        "cart_capacity": 1,
        "reservation_capacity": 1,
        "decision_rate": 1,
        "state_bound": 8,
    }


def _task6_finite_lts() -> JsonObject:
    return {
        "states": ["s0", "s1", "s2"],
        "initial_state": "s0",
        "marked_states": ["s2"],
        "transitions": [
            {"source": "s0", "event": "complete", "target": "s1", "controllable": True},
            {"source": "s1", "event": "finish", "target": "s2", "controllable": True},
        ],
    }


def _task6_protocol_input(case_id: str, kind: str) -> JsonObject:
    del case_id
    if kind == "bidirectional_island_grid":
        return {
            "generator_id": BIDIRECTIONAL_GENERATOR_ID,
            "cells": [_task6_grid_cell()],
        }
    if kind == "medium_island_rebuild":
        return {
            "generator_id": MEDIUM_ISLAND_GENERATOR_ID,
            "parameters": _task6_medium_parameters(),
        }
    if kind == "adversarial_snapshot":
        return {
            "generator_id": ADVERSARIAL_GENERATOR_ID,
            "parameters": _task6_adversarial_parameters(),
        }
    if kind == "supplied_l30_inequalities":
        return {
            "capacities": {"p1": 3, "p2": 2},
            "inequalities": [
                {"name": "l30-bound-a", "coefficients": {"p1": 1, "p2": -1}, "rhs": 1}
            ],
            "finite_capacity_s3pr_ens3pr": True,
            "inequality_provenance": "synthetic-l30-proof",
        }
    if kind == "adapted_candidate_monitor_cover":
        return {
            "finite_lts": _task6_finite_lts(),
            "state_bound": 3,
            "legal_states": ["s0"],
            "first_met_bad_states": ["s1"],
            "candidate_monitors": [
                {
                    "monitor_id": "monitor-cover-a",
                    "covered_bad_states": ["s1"],
                    "excluded_legal_states": [],
                }
            ],
        }
    if kind == "fixed_recorder_target":
        return {
            "finite_lts": _task6_finite_lts(),
            "state_bound": 3,
            "target_state": "s1",
            "recorder_events": ["complete"],
            "fixed_counts": {"complete": 1},
        }
    if kind == "crp_evidence_audit":
        return {
            "finite_lts": _task6_finite_lts(),
            "state_bound": 3,
            "crp_profile": {
                "s4pr_applicable": False,
                "embedding": None,
                "embedding_sha256": None,
                "crp_pairs": [["activity-a", "p1"]],
                "translated_target_state": None,
                "external_prefix_claimed": None,
                "outside_s4pr_reasons": ["synthetic_boundary"],
            },
            "partial_deadlock_bridge": None,
            "outside_scope_generator": None,
        }
    raise AssertionError(kind)


def _task6_input_payload(
    case_id: str,
    *,
    protocol_kind: str | None = None,
) -> JsonObject:
    kind = _TASK6_G4_KIND_BY_CASE[case_id] if protocol_kind is None else protocol_kind
    return {
        "protocol_kind": kind,
        "protocol_input": _task6_protocol_input(case_id, kind),
    }


def _task6_demand_rows(demands: object) -> list[JsonObject]:
    return [
        {"resource_role": demand.resource_id, "amount": demand.units}
        for demand in sorted(
            cast(Any, demands),
            key=lambda item: (item.resource_id, item.units),
        )
    ]


def _task6_generated_built_case(
    protocol_kind: str,
    protocol_input: JsonObject,
    selected_subunit: JsonObject | None,
) -> Any:
    if protocol_kind == "bidirectional_island_grid":
        cell = (
            cast(JsonObject, protocol_input["cells"][0])
            if selected_subunit is None
            else selected_subunit
        )
        return build_bidirectional_island_case(BidirectionalGridCell(**cast(Any, cell)))
    if protocol_kind == "medium_island_rebuild":
        parameters = dict(cast(JsonObject, protocol_input["parameters"]))
        parameters["route_wip"] = tuple(
            sorted(cast(dict[str, int], parameters["route_wip"]).items())
        )
        return build_medium_island_case(MediumIslandParameters(**cast(Any, parameters)))
    if protocol_kind == "adversarial_snapshot":
        return build_adversarial_boundary_case(
            AdversarialBoundaryParameters(
                **cast(Any, cast(JsonObject, protocol_input["parameters"]))
            )
        )
    raise AssertionError(protocol_kind)


def _task6_state_payload_from_built(built: Any) -> JsonObject:
    state = built.spec.initial_state
    return {
        "stable": state.stable,
        "complete": state.complete,
        "event_calendar_empty": state.event_calendar_empty,
        "holds": [
            {
                "job_role": hold.job_id,
                "resource_role": hold.resource_id,
                "amount": hold.units,
            }
            for hold in sorted(
                state.holds,
                key=lambda item: (item.job_id, item.resource_id, item.units),
            )
        ],
        "requests": [
            {
                "job_role": job_id,
                "alternatives": [
                    _task6_demand_rows(alternative.demands)
                    for alternative in alternatives
                ],
            }
            for job_id, alternatives in sorted(state.requests.items())
        ],
        "mode_by_job": [
            {"job_role": job_id, "value": mode}
            for job_id, mode in sorted(state.mode_by_job.items())
        ],
        "stage_by_job": [
            {"job_role": job_id, "value": stage}
            for job_id, stage in sorted(state.stage_by_job.items())
        ],
    }


def _task6_transition_event_kind(transition: Any) -> str:
    value = transition.kind
    return cast(str, value.value if hasattr(value, "value") else value)


def _task6_route_graph_from_transitions(transitions: list[Any]) -> list[JsonObject]:
    graph: list[JsonObject] = []
    for job_id in sorted({transition.job_id for transition in transitions}):
        ordered: list[str] = []
        for transition in sorted(
            (item for item in transitions if item.job_id == job_id),
            key=lambda item: item.name,
        ):
            for stage in (transition.source_mode, transition.target_mode):
                if stage not in ordered:
                    ordered.append(stage)
        graph.append({"route_role": job_id, "ordered_stage_roles": ordered})
    return graph


def _task6_capacity_parameter_name(protocol_kind: str, resource_id: str) -> str:
    if protocol_kind in {"bidirectional_island_grid", "medium_island_rebuild"}:
        if resource_id == "agv":
            return "agv_count"
        if "buffer" in resource_id or resource_id.endswith("_out"):
            return "buffer_capacity"
        return "machine_capacity"
    if protocol_kind == "adversarial_snapshot":
        if resource_id.startswith("cart_"):
            return "cart_capacity"
        if resource_id.startswith("fixture_"):
            return "fixture_capacity"
        if resource_id.startswith("reserve_"):
            return "reservation_capacity"
        if resource_id == "inspection":
            return "inspection_capacity"
    raise AssertionError(f"unmapped resource {protocol_kind}:{resource_id}")


def _task6_route_projection_from_built(
    protocol_kind: str,
    built: Any,
) -> JsonObject:
    transitions = sorted(built.spec.transitions, key=lambda item: item.name)
    return {
        "projection_schema_version": "g4_generator_route_projection/v1",
        "input_mode": "model_generated_lts",
        "route_semantics_version": "g6b-retired-route-section-7.4/v1",
        "typed_resource_roles": [
            {
                "resource_role": resource.id,
                "resource_kind": resource.kind,
                "capacity_parameter_name": _task6_capacity_parameter_name(
                    protocol_kind,
                    resource.id,
                ),
            }
            for resource in sorted(
                built.spec.model.resources.values(),
                key=lambda item: item.id,
            )
        ],
        "typed_route_graph": _task6_route_graph_from_transitions(transitions),
        "transition_kinds": [
            {
                "transition_role": transition.name,
                "event_kind": _task6_transition_event_kind(transition),
                "source_mode": transition.source_mode,
                "target_mode": transition.target_mode,
            }
            for transition in transitions
        ],
        "resource_demand_structure": [
            {
                "transition_role": transition.name,
                "acquire_demands": _task6_demand_rows(transition.acquire),
                "release_demands": _task6_demand_rows(transition.release),
            }
            for transition in transitions
        ],
        "mode_transition_structure": [
            {
                "job_role": transition.job_id,
                "source_stage": transition.source_mode,
                "event_kind": _task6_transition_event_kind(transition),
                "target_stage": transition.target_mode,
            }
            for transition in transitions
        ],
    }


def _task6_route_projection_from_finite_lts(finite_lts: JsonObject) -> JsonObject:
    transitions = cast(list[JsonObject], finite_lts["transitions"])
    return {
        "projection_schema_version": "g4_explicit_route_projection/v1",
        "input_mode": "explicit_finite_lts_input",
        "route_semantics_version": "g6b-retired-route-section-7.4/v1",
        "typed_resource_roles": [],
        "typed_route_graph": [
            {
                "route_role": "finite_lts",
                "ordered_stage_roles": list(cast(list[str], finite_lts["states"])),
            }
        ],
        "transition_kinds": [
            {
                "transition_role": transition["event"],
                "event_kind": transition["event"],
                "source_mode": transition["source"],
                "target_mode": transition["target"],
            }
            for transition in transitions
        ],
        "resource_demand_structure": [
            {
                "transition_role": transition["event"],
                "acquire_demands": [],
                "release_demands": [],
            }
            for transition in transitions
        ],
        "mode_transition_structure": [
            {
                "job_role": "finite_lts",
                "source_stage": transition["source"],
                "event_kind": transition["event"],
                "target_stage": transition["target"],
            }
            for transition in transitions
        ],
    }


def _task6_decimal(value: object) -> str:
    return str(value)


def _task6_allowed_parent_context(
    protocol_kind: str,
    parent_context: JsonObject | None,
) -> JsonObject:
    if parent_context is None:
        return {}
    allowed_by_kind = {
        "bidirectional_island_grid": {"generator_id"},
        "supplied_l30_inequalities": {
            "capacities",
            "finite_capacity_s3pr_ens3pr",
            "inequality_provenance",
        },
        "adapted_candidate_monitor_cover": {
            "finite_lts",
            "legal_states",
            "first_met_bad_states",
            "state_bound",
        },
    }
    allowed = allowed_by_kind.get(protocol_kind, set())
    return {
        key: parent_context[key] for key in sorted(parent_context) if key in allowed
    }


def _task6_parameter_entries(
    protocol_kind: str,
    protocol_input: JsonObject,
    selected_subunit: JsonObject | None,
    parent_context: JsonObject,
) -> tuple[list[JsonObject], list[JsonObject], int]:
    structural: list[JsonObject] = []
    numeric: list[JsonObject] = []

    def add_structural(name: str, value_type: str, value: object) -> None:
        structural.append({"name": name, "value_type": value_type, "value": value})

    def add_numeric(name: str, value_type: str, value: object) -> None:
        numeric.append({"name": name, "value_type": value_type, "value": value})

    if protocol_kind == "bidirectional_island_grid":
        cell = (
            cast(JsonObject, protocol_input["cells"][0])
            if selected_subunit is None
            else selected_subunit
        )
        add_structural("cell_id", "string", cell["cell_id"])
        if "generator_id" in parent_context:
            add_structural("generator_id", "string", parent_context["generator_id"])
        for name in (
            "agv_count",
            "buffer_capacity",
            "forward_wip",
            "machine_capacity",
            "reverse_wip",
            "state_bound",
        ):
            add_numeric(name, "integer", cell[name])
        for name in ("release_rate", "service_rate", "transfer_rate"):
            add_numeric(name, "canonical_decimal_string", _task6_decimal(cell[name]))
        state_bound = cast(int, cell["state_bound"])
    elif protocol_kind == "supplied_l30_inequalities":
        inequality = (
            cast(list[JsonObject], protocol_input["inequalities"])[0]
            if selected_subunit is None
            else selected_subunit
        )
        capacities = cast(
            JsonObject,
            parent_context.get("capacities", protocol_input.get("capacities", {})),
        )
        add_structural("inequality_name", "string", inequality["name"])
        add_structural(
            "inequality_coefficients",
            "ordered_tuple",
            [
                [name, value]
                for name, value in sorted(
                    cast(JsonObject, inequality["coefficients"]).items()
                )
            ],
        )
        add_structural(
            "finite_capacity_s3pr_ens3pr",
            "boolean",
            parent_context.get(
                "finite_capacity_s3pr_ens3pr",
                protocol_input.get("finite_capacity_s3pr_ens3pr"),
            ),
        )
        add_structural(
            "inequality_provenance",
            "string",
            parent_context.get(
                "inequality_provenance",
                protocol_input.get("inequality_provenance"),
            ),
        )
        add_numeric("inequality_rhs", "integer", inequality["rhs"])
        for name, value in sorted(capacities.items()):
            add_numeric(f"capacity_{name}", "integer", value)
        state_bound = 0
    elif protocol_kind == "adapted_candidate_monitor_cover":
        monitor = (
            cast(list[JsonObject], protocol_input["candidate_monitors"])[0]
            if selected_subunit is None
            else selected_subunit
        )
        finite_lts = parent_context.get("finite_lts", protocol_input["finite_lts"])
        legal_states = parent_context.get(
            "legal_states",
            protocol_input["legal_states"],
        )
        bad_states = parent_context.get(
            "first_met_bad_states",
            protocol_input["first_met_bad_states"],
        )
        add_structural("monitor_id", "string", monitor["monitor_id"])
        add_structural(
            "covered_bad_states",
            "ordered_tuple",
            sorted(cast(list[str], monitor["covered_bad_states"])),
        )
        add_structural(
            "excluded_legal_states",
            "ordered_tuple",
            sorted(cast(list[str], monitor["excluded_legal_states"])),
        )
        add_structural("finite_lts_sha256", "sha256", canonical_sha256_v2(finite_lts))
        add_structural(
            "legal_states_sha256",
            "sha256",
            canonical_sha256_v2(legal_states),
        )
        add_structural(
            "first_met_bad_states_sha256",
            "sha256",
            canonical_sha256_v2(bad_states),
        )
        state_bound = cast(
            int,
            parent_context.get("state_bound", protocol_input["state_bound"]),
        )
        add_numeric("state_bound", "integer", state_bound)
    elif protocol_kind == "medium_island_rebuild":
        parameters = cast(JsonObject, protocol_input["parameters"])
        add_structural("instance_id", "string", parameters["instance_id"])
        add_structural(
            "route_wip",
            "ordered_tuple",
            [
                [route_id, count]
                for route_id, count in sorted(
                    cast(dict[str, int], parameters["route_wip"]).items()
                )
            ],
        )
        for name in (
            "agv_count",
            "buffer_capacity",
            "machine_capacity",
            "state_bound",
        ):
            add_numeric(name, "integer", parameters[name])
        for name in ("release_rate", "service_rate", "transfer_rate"):
            add_numeric(
                name,
                "canonical_decimal_string",
                _task6_decimal(parameters[name]),
            )
        state_bound = cast(int, parameters["state_bound"])
    elif protocol_kind == "adversarial_snapshot":
        parameters = cast(JsonObject, protocol_input["parameters"])
        add_structural("instance_id", "string", parameters["instance_id"])
        for name in (
            "cart_capacity",
            "fixture_capacity",
            "inspection_capacity",
            "reservation_capacity",
            "state_bound",
        ):
            add_numeric(
                name,
                "integer",
                1 if name == "inspection_capacity" else parameters[name],
            )
        add_numeric(
            "decision_rate",
            "canonical_decimal_string",
            _task6_decimal(parameters["decision_rate"]),
        )
        state_bound = cast(int, parameters["state_bound"])
    else:
        state_bound = cast(int, protocol_input.get("state_bound", 0))
        add_numeric("state_bound", "integer", state_bound)

    return (
        sorted(structural, key=lambda item: cast(str, item["name"])),
        sorted(numeric, key=lambda item: cast(str, item["name"])),
        state_bound,
    )


def _task6_projection_payload(
    dimension: str,
    *,
    protocol_kind: str = "bidirectional_island_grid",
    case_id: str = "G4_IMS_PARAMETER_GRID",
    selected_subunit: JsonObject | None = None,
    parent_context: JsonObject | None = None,
) -> JsonObject:
    input_payload = _task6_input_payload(case_id, protocol_kind=protocol_kind)
    protocol_input = cast(JsonObject, input_payload["protocol_input"])
    context = _task6_allowed_parent_context(protocol_kind, parent_context)
    finite_lts = cast(JsonObject, protocol_input.get("finite_lts", {"transitions": []}))
    built = (
        _task6_generated_built_case(protocol_kind, protocol_input, selected_subunit)
        if protocol_kind
        in {
            "adversarial_snapshot",
            "bidirectional_island_grid",
            "medium_island_rebuild",
        }
        else None
    )
    structural_entries, numeric_entries, state_bound = _task6_parameter_entries(
        protocol_kind,
        protocol_input,
        selected_subunit,
        context,
    )
    explicit_state_projection: JsonObject = {
        "projection_schema_version": "g4_explicit_state_projection/v1",
        "input_mode": "finite_lts_explicit",
        "state_payload_schema_version": "g6b-retired-state-section-7.4/v1",
        "state_payload": protocol_input.get("finite_lts"),
    }
    generated_state_projection: JsonObject = {
        "projection_schema_version": "g4_generated_state_projection/v1",
        "input_mode": "model_generated_lts",
        "state_payload_schema_version": "g6b-retired-state-section-7.4/v1",
        "state_payload": (
            {} if built is None else _task6_state_payload_from_built(built)
        ),
    }
    explicit_route_projection = (
        _task6_route_projection_from_finite_lts(finite_lts)
        if "states" in finite_lts
        else {}
    )
    generated_route_projection = (
        explicit_route_projection
        if built is None
        else _task6_route_projection_from_built(protocol_kind, built)
    )
    if protocol_kind in {
        "adapted_candidate_monitor_cover",
        "crp_evidence_audit",
        "fixed_recorder_target",
    }:
        state_projection = explicit_state_projection
        route_projection = explicit_route_projection
    else:
        state_projection = generated_state_projection
        route_projection = generated_route_projection
    parameter_projection: JsonObject = {
        "projection_schema_version": "g4_parameter_projection/v1",
        "parameter_semantics_version": "g6b-retired-parameter-section-7.4/v1",
        "structural_parameter_entries": structural_entries,
        "numeric_parameter_entries": numeric_entries,
        "state_bound": state_bound,
        "rate_manifest_content_sha256": canonical_sha256_v2({}),
        "policy_declaration_content_sha256": canonical_sha256_v2({}),
    }
    projection_by_dimension: dict[str, JsonObject] = {
        "state_snapshot_sha256": state_projection,
        "route_signature_sha256": route_projection,
        "parameter_tuple_sha256": parameter_projection,
        "case_content_sha256": {
            "projection_schema_version": "g4_case_content_projection/v1",
            "input_mode": "retired_protocol_input",
            "input_semantics_version": "g6b-retired-input-section-7.4/v1",
            "state_snapshot_sha256": canonical_sha256_v2(state_projection),
            "route_signature_sha256": canonical_sha256_v2(route_projection),
            "parameter_tuple_sha256": canonical_sha256_v2(parameter_projection),
            "rate_manifest_content_sha256": canonical_sha256_v2({}),
            "policy_declaration_content_sha256": canonical_sha256_v2({}),
            "selected_target_declaration_sha256": canonical_sha256_v2({}),
            "control_declaration_sha256": canonical_sha256_v2({}),
        },
        "random_stream_manifest_sha256": {
            "projection_schema_version": "g4_stream_projection/v1",
            "applicability_status": "not_applicable_by_protocol",
            "method_role": "exact_companion",
            "reason_code": "exact_method_has_no_random_stream",
        },
        "sealed_prediction_sha256": {
            "projection_schema_version": "g4_prediction_projection/v1",
            "research_question": "Can the selected structural condition hold?",
            "directional_hypotheses": [
                {
                    "hypothesis_role": "primary_reachability",
                    "statement": "D_local is reachable",
                    "direction": "greater_than_zero",
                    "estimand_id": "g6b_estimand_theta_global_before_success_v1",
                    "scope_code": "selected_target",
                    "falsifier_roles": ["no_selected_target_reachability"],
                }
            ],
            "falsifiers": [
                {
                    "falsifier_role": "no_selected_target_reachability",
                    "condition_code": "D_local_not_reachable",
                    "affected_hypothesis_roles": ["primary_reachability"],
                }
            ],
            "mandatory_control_roles": ["exact_companion"],
            "planned_method_roles": ["exact_companion", "des_companion"],
            "scoring_rule": {
                "scoring_rule_id": "bounded_discovery_v1",
                "required_input_roles": ["exact_companion", "des_companion"],
                "decision_table_sha256": _synthetic_hash("prediction-decision-table"),
                "failure_handling_code": "fail_closed",
            },
            "claim_boundary": {
                "study_role": "discovery_only",
                "confirmation_use": "retired_authority_fingerprint_only",
                "estimand_scope_code": "selected_target",
                "population_scope_code": "synthetic_retired_g4",
                "forbidden_upgrade_codes": ["no_outcome_upgrade", "no_universal_claim"],
            },
        },
        "metric_schema_sha256": {
            "projection_schema_version": "g4_metric_projection/v1",
            "estimand_schema_version": "task6/estimand/v1",
            "metric_entries": [
                {
                    "metric_id": "theta_global",
                    "estimand_id": "g6b_estimand_theta_global_before_success_v1",
                    "unit": "probability",
                    "domain": "selected_target",
                    "direction": "lower_is_better",
                    "aggregation_rule_id": "mean",
                    "censoring_rule_id": "none",
                    "failure_rule_id": "refuse_on_missing",
                    "scoring_rule_id": "bounded_discovery_v1",
                    "applicability_rule": "G4_IMS_PARAMETER_GRID",
                }
            ],
            "aggregation_rules": [{"rule_id": "mean", "operator": "mean"}],
            "censoring_rules": [{"rule_id": "none", "operator": "none"}],
            "failure_rules": [
                {"rule_id": "refuse_on_missing", "operator": "fail_closed"}
            ],
            "scoring_rules": [
                {"rule_id": "bounded_discovery_v1", "operator": "descriptive"}
            ],
            "comparability_scope": "same_target_companion_group",
        },
    }
    projection = dict(projection_by_dimension[dimension])
    return projection


def _task6_output_root_projection(*, authority: str) -> JsonObject:
    if authority == "G5_EXECUTION":
        legacy_root = "artifacts/g5-execution/raw"
        suffix = "primary"
    elif authority == "G6_R_REPLAY_R3":
        legacy_root = "artifacts/g6-historical-replay/R3"
        suffix = "R3"
    else:
        raise AssertionError(authority)
    bundle_id = "synthetic_retired_bundle"
    case_unit_id = "G4_IMS_PARAMETER_GRID"
    method_observation_id = (
        f"{authority.lower()}_g4_ims_parameter_grid_{suffix.lower()}"
    )
    record: JsonObject = {
        "projection_schema_version": "task6/output-root/v1",
        "bundle_id": bundle_id,
        "case_unit_id": case_unit_id,
        "method_observation_id": method_observation_id,
        "run_role": suffix,
        "logical_root_id": f"{authority}:{legacy_root}",
        "repo_relative_posix_path": (
            "artifacts/g6b/quantitative/"
            f"{bundle_id}/{case_unit_id}/{method_observation_id}/{suffix}"
        ),
        "reserved": True,
        "materialized": False,
        "reservation_sha256": None,
    }
    record["reservation_sha256"] = finalized_self_hash(record, "reservation_sha256")
    return record


def _task6_source_payload(path: str) -> JsonObject:
    payload: JsonObject = {"schema_version": "task6-synthetic-retired-source/v1"}
    if path.startswith("cases/confirmation/g4/cases/"):
        case_id = Path(path).stem
        kind = _TASK6_G4_KIND_BY_CASE[case_id]
        payload["case_id"] = case_id
        payload["expected_outputs_schema"] = {
            "schema_version": "task6/expected-outputs/v1",
            "declared_outputs": [],
        }
        payload["input_payload"] = _task6_input_payload(case_id, protocol_kind=kind)
    elif path.endswith("random_stream_manifest.json"):
        payload["streams_by_case"] = {
            case_id: _task6_projection_payload("random_stream_manifest_sha256")
            for case_id in contracts.G4_MANIFEST_CASE_IDS
        }
    elif path.endswith("predictions.json"):
        payload["predictions"] = {
            case_id: _task6_projection_payload("sealed_prediction_sha256")
            for case_id in contracts.G4_MANIFEST_CASE_IDS
        }
    elif path.endswith("metrics_schema.json"):
        payload["metrics"] = _task6_projection_payload("metric_schema_sha256")
    elif path == "evidence/g5/G5_EXECUTION_LOCK.json":
        payload["execution_schedule"] = {
            "case_runs": [
                {"case_id": "G4_IMS_PARAMETER_GRID", "run_label": "primary"},
                {"case_id": "G4_MEDIUM_ISLAND_REBUILD", "run_label": "primary"},
            ]
        }
        payload["output_roots"] = {
            "raw_output_root_relative": "artifacts/g5-execution/raw",
            "must_not_exist_before_execution": True,
            "pre_execution_probe": "absent",
            "must_be_outside_frozen_bundle": True,
            "frozen_bundle_root_relative": "cases/confirmation/g4",
        }
    elif path == "evidence/g6/G6_HISTORICAL_REPLAY_LOCK_R3.json":
        payload["case_ids"] = ["G4_IMS_PARAMETER_GRID", "G4_MEDIUM_ISLAND_REBUILD"]
        payload["run_labels"] = ["R3"]
        payload["output_root"] = "D:\\historical\\artifacts\\g6-historical-replay\\R3"
        payload["execution_schedule"] = {
            "case_runs": [
                {"case_id": "G4_IMS_PARAMETER_GRID", "run_label": "R3"},
                {"case_id": "G4_MEDIUM_ISLAND_REBUILD", "run_label": "R3"},
            ]
        }
    elif path == "evidence/g6/G6_HISTORICAL_REPLAY_R3_RAW_HASH_MANIFEST.json":
        payload["output_root"] = "D:\\historical\\artifacts\\g6-historical-replay\\R3"
    return payload


def _task6_synthetic_repo(
    tmp_path: Path,
    *,
    overrides: dict[str, Callable[[JsonObject], None]] | None = None,
) -> tuple[Path, dict[str, JsonObject]]:
    locks = _authority_lock_records()
    repo = tmp_path / "task6-synthetic-repo"
    source_records: dict[str, JsonObject] = {}
    assert len(contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY) == 27
    for path in contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY:
        payload = _task6_source_payload(path)
        if overrides is not None and path in overrides:
            overrides[path](payload)
        raw = canonical_bytes_v2(payload)
        destination = repo / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        record = _authority_source_record(
            path,
            authority_lock_record_sha256=locks[_authority_id_for_retired_path(path)][
                "authority_lock_record_sha256"
            ],
        )
        raw_hash = hashlib.sha256(raw).hexdigest()
        record["raw_byte_sha256"] = raw_hash
        record["declared_historical_hash_or_null"] = raw_hash
        record["declared_hash_algorithm_or_null"] = "sha256"
        record["declared_hash_verified"] = True
        source_records[path] = record
    return repo, source_records


def _task6_records(
    tmp_path: Path,
    *,
    overrides: dict[str, Callable[[JsonObject], None]] | None = None,
) -> dict[str, JsonObject]:
    repo, source_records = _task6_synthetic_repo(tmp_path, overrides=overrides)
    return build_retired_fingerprint_records(
        repo,
        _authorization_record(),
        _authority_lock_records(),
        source_records,
    )


def _task6_single_record(
    records: dict[str, JsonObject],
    *,
    authority: str,
    subject_id: str,
    dimension: str,
) -> JsonObject:
    matches = [
        record
        for record in records.values()
        if record["source_authority_id"] == authority
        and record["subject_id"] == subject_id
        and record["dimension"] == dimension
    ]
    assert len(matches) == 1
    return matches[0]


def _task6_assert_record_matches_projection(
    record: JsonObject,
    projection: JsonObject | None,
) -> None:
    assert set(record) == set(contracts.FINGERPRINT_RECORD_REQUIRED_FIELDS)
    expected_subject_type = _TASK6_RETIRED_SUBJECT_TYPE_BY_DIMENSION[
        cast(str, record["dimension"])
    ]
    if record["subject_type"] == "retired_case_subunit":
        assert cast(str, record["dimension"]) in {
            "case_content_sha256",
            "state_snapshot_sha256",
            "route_signature_sha256",
            "parameter_tuple_sha256",
            "sealed_prediction_sha256",
        }
    else:
        assert record["subject_type"] == expected_subject_type
    if projection is None:
        assert record["comparison_projection_sha256_or_null"] is None
        assert record["comparison_projection_ref_or_null"] is None
        return
    if projection == _TASK6_HAS_RECONSTRUCTABLE_PROJECTION:
        assert isinstance(record["comparison_projection_sha256_or_null"], str)
        assert isinstance(record["comparison_projection_ref_or_null"], str)
        return
    assert not (set(projection) & set(_TASK6_SUBJECT_PROJECTION_KEYS))
    assert "_for_test_" not in "".join(record)
    assert record["comparison_projection_sha256_or_null"] == canonical_sha256_v2(
        projection
    )


def _task6_g4_subject_id_for_dimension(dimension: str) -> str:
    if _TASK6_RETIRED_SUBJECT_TYPE_BY_DIMENSION[dimension] == "retired_case":
        return "G4_IMS_PARAMETER_GRID"
    if dimension == "metric_schema_sha256":
        return "G4_IMS_PARAMETER_GRID:exact_des_companion_group"
    return "G4_IMS_PARAMETER_GRID:exact_companion"


def _task6_g4_source_refs_for_dimension(dimension: str) -> list[JsonObject]:
    if dimension == "case_content_sha256":
        return [
            {
                "authority_id": "G4_FREEZE",
                "repo_relative_posix_path": _task6_case_path("G4_IMS_PARAMETER_GRID"),
                "json_pointer_or_null": "/input_payload",
                "source_role": "case_content_projection",
            },
            {
                "authority_id": "G4_FREEZE",
                "repo_relative_posix_path": _task6_case_path("G4_IMS_PARAMETER_GRID"),
                "json_pointer_or_null": "/expected_outputs_schema",
                "source_role": "case_content_projection",
            },
        ]
    if dimension == "random_stream_manifest_sha256":
        return [
            {
                "authority_id": "G4_FREEZE",
                "repo_relative_posix_path": (
                    "cases/confirmation/g4/random_stream_manifest.json"
                ),
                "json_pointer_or_null": "/streams_by_case/G4_IMS_PARAMETER_GRID",
                "source_role": "random_stream_projection",
            }
        ]
    if dimension == "sealed_prediction_sha256":
        return [
            {
                "authority_id": "G4_FREEZE",
                "repo_relative_posix_path": "cases/confirmation/g4/predictions.json",
                "json_pointer_or_null": "/predictions",
                "source_role": "prediction_projection",
            }
        ]
    if dimension == "metric_schema_sha256":
        return [
            {
                "authority_id": "G4_FREEZE",
                "repo_relative_posix_path": (
                    "cases/confirmation/g4/metrics_schema.json"
                ),
                "json_pointer_or_null": "/metrics",
                "source_role": "metric_projection",
            }
        ]
    raise AssertionError(dimension)


def _task6_required_record(
    records: dict[str, JsonObject],
    *,
    authority: str,
    subject_id: str,
    dimension: str,
) -> JsonObject:
    return _task6_single_record(
        records,
        authority=authority,
        subject_id=subject_id,
        dimension=dimension,
    )


def _task6_expect_refusal(
    tmp_path: Path,
    overrides: dict[str, Callable[[JsonObject], None]],
    *,
    expected_record_id: str | None = None,
) -> None:
    try:
        records = _task6_records(tmp_path, overrides=overrides)
    except SchemaContractError:
        return
    if expected_record_id is None:
        refused = [
            record
            for record in records.values()
            if record["dimension_status"] == "unreconstructable_refuse"
        ]
        assert refused
        return
    assert records[expected_record_id]["dimension_status"] == "unreconstructable_refuse"


def test_task6_synthetic_repo_uses_exact_27_file_inventory_and_protocol_fields(
    tmp_path: Path,
) -> None:
    repo, source_records = _task6_synthetic_repo(tmp_path)
    case_payload = _read_json(repo / _task6_case_path("G4_IMS_PARAMETER_GRID"))
    input_payload = cast(JsonObject, case_payload["input_payload"])

    assert tuple(source_records) == contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY
    assert set(input_payload) == {"protocol_kind", "protocol_input"}
    assert input_payload["protocol_kind"] == "bidirectional_island_grid"
    assert set(cast(JsonObject, input_payload["protocol_input"])) == {
        "generator_id",
        "cells",
    }
    serialized = canonical_bytes_v2(case_payload).decode()
    assert "state_seed" not in serialized
    assert "route_template" not in serialized
    assert "fingerprint" + "_payloads" not in serialized
    assert "protocol" + "_discriminator" not in serialized


def test_task6_generated_protocol_inputs_match_g4_input_builders() -> None:
    grid_input = _task6_protocol_input(
        "G4_IMS_PARAMETER_GRID",
        "bidirectional_island_grid",
    )
    medium_input = _task6_protocol_input(
        "G4_MEDIUM_ISLAND_REBUILD",
        "medium_island_rebuild",
    )
    adversarial_input = _task6_protocol_input(
        "G4_ADVERSARIAL_BOUNDARY",
        "adversarial_snapshot",
    )

    assert set(grid_input) == {"generator_id", "cells"}
    assert grid_input["generator_id"] == BIDIRECTIONAL_GENERATOR_ID
    assert set(cast(list[JsonObject], grid_input["cells"])[0]) == {
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
    grid_cell = cast(list[JsonObject], grid_input["cells"])[0]
    grid_case = build_bidirectional_island_case(
        BidirectionalGridCell(**cast(Any, grid_cell))
    )
    assert grid_case.generator_id == BIDIRECTIONAL_GENERATOR_ID

    assert set(medium_input) == {"generator_id", "parameters"}
    assert medium_input["generator_id"] == MEDIUM_ISLAND_GENERATOR_ID
    medium_parameters = dict(cast(JsonObject, medium_input["parameters"]))
    assert set(medium_parameters) == {
        "instance_id",
        "machine_capacity",
        "buffer_capacity",
        "agv_count",
        "route_wip",
        "service_rate",
        "transfer_rate",
        "release_rate",
        "state_bound",
    }
    medium_parameters["route_wip"] = tuple(
        sorted(cast(dict[str, int], medium_parameters["route_wip"]).items())
    )
    medium_case = build_medium_island_case(
        MediumIslandParameters(**cast(Any, medium_parameters))
    )
    assert medium_case.generator_id == MEDIUM_ISLAND_GENERATOR_ID

    assert set(adversarial_input) == {"generator_id", "parameters"}
    assert adversarial_input["generator_id"] == ADVERSARIAL_GENERATOR_ID
    assert set(cast(JsonObject, adversarial_input["parameters"])) == {
        "instance_id",
        "fixture_capacity",
        "cart_capacity",
        "reservation_capacity",
        "decision_rate",
        "state_bound",
    }
    adversarial_case = build_adversarial_boundary_case(
        AdversarialBoundaryParameters(
            **cast(Any, cast(JsonObject, adversarial_input["parameters"]))
        )
    )
    assert adversarial_case.generator_id == ADVERSARIAL_GENERATOR_ID


@pytest.mark.parametrize(
    "dimension",
    [
        "case_content_sha256",
        "state_snapshot_sha256",
        "route_signature_sha256",
        "parameter_tuple_sha256",
        "random_stream_manifest_sha256",
        "sealed_prediction_sha256",
        "metric_schema_sha256",
    ],
)
def test_task6_expected_section_7_4_projection_payloads_validate(
    dimension: str,
) -> None:
    contracts.validate_subject_free_projection(
        dimension,
        _task6_projection_payload(dimension),
    )


def test_task6_expected_output_root_payload_validates() -> None:
    contracts.validate_output_root_reservation(
        _task6_output_root_projection(authority="G6_R_REPLAY_R3")
    )


@pytest.mark.parametrize(
    ("case_id", "protocol_kind"),
    tuple(sorted(_TASK6_G4_KIND_BY_CASE.items())),
)
def test_task6_discriminator_covers_all_nine_g4_protocol_kinds(
    tmp_path: Path,
    case_id: str,
    protocol_kind: str,
) -> None:
    repo, _ = _task6_synthetic_repo(tmp_path)
    case_bytes = (repo / _task6_case_path(case_id)).read_bytes()

    observed = cast(Any, normalizer)._discriminate_g4_kind(
        case_id,
        case_bytes,
        [
            row
            for row in _selector_rows()
            if row["source_path_pattern"]
            == "cases/confirmation/g4/cases/{case_id}.json"
        ],
    )

    assert observed == protocol_kind


@pytest.mark.parametrize(
    ("case_id", "protocol_kind", "subject_id", "selector", "unique_key", "context"),
    [
        (
            "G4_IMS_PARAMETER_GRID",
            "bidirectional_island_grid",
            "G4_IMS_PARAMETER_GRID:cell_id:ims_cell_01",
            "/input_payload/protocol_input/cells/*",
            "cell_id",
            ("generator_id",),
        ),
        (
            "G4_L30_RESOURCE_BASELINE",
            "supplied_l30_inequalities",
            "G4_L30_RESOURCE_BASELINE:name:l30-bound-a",
            "/input_payload/protocol_input/inequalities/*",
            "name",
            ("capacities", "finite_capacity_s3pr_ens3pr", "inequality_provenance"),
        ),
        (
            "G4_B05_SUPERVISOR_COMPARATOR",
            "adapted_candidate_monitor_cover",
            "G4_B05_SUPERVISOR_COMPARATOR:monitor_id:monitor-cover-a",
            "/input_payload/protocol_input/candidate_monitors/*",
            "monitor_id",
            ("finite_lts", "legal_states", "first_met_bad_states", "state_bound"),
        ),
    ],
)
def test_task6_composite_subjects_keep_exact_parent_context(
    tmp_path: Path,
    case_id: str,
    protocol_kind: str,
    subject_id: str,
    selector: str,
    unique_key: str,
    context: tuple[str, ...],
) -> None:
    repo, _ = _task6_synthetic_repo(tmp_path)
    case_bytes = (repo / _task6_case_path(case_id)).read_bytes()
    rows = [
        row
        for row in _selector_rows()
        if row["source_path_pattern"] == "cases/confirmation/g4/cases/{case_id}.json"
    ]

    subjects = cast(Any, normalizer)._g4_subjects(
        case_id,
        protocol_kind,
        case_bytes,
        rows,
    )
    subject = next(item for item in subjects if item["subject_id"] == subject_id)
    composite_record: JsonObject = {
        "parent_case_id": case_id,
        "owner_object_id": subject["owner_object_id"],
        "protocol_kind": protocol_kind,
        "selector": subject["selector_pointer_or_null"],
        "unique_key": unique_key,
        "subunit_id_component": subject_id.rsplit(":", 1)[1],
        "parent_context_fields": subject["parent_context_fields"],
        "canonical_payload_sha256": _synthetic_hash(subject_id),
    }

    assert subject["selector_pointer_or_null"] == selector
    assert tuple(subject["parent_context_fields"]) == context
    contracts.validate_composite_subunit_record(composite_record)


@pytest.mark.parametrize(
    ("case_id", "dimension", "projection", "status"),
    [
        (
            "G4_B05_SUPERVISOR_COMPARATOR",
            "state_snapshot_sha256",
            _task6_projection_payload(
                "state_snapshot_sha256",
                protocol_kind="adapted_candidate_monitor_cover",
            ),
            "derived_by_versioned_normalizer",
        ),
        (
            "G4_RECORDER_TARGET_QUANTIFICATION",
            "route_signature_sha256",
            _TASK6_HAS_RECONSTRUCTABLE_PROJECTION,
            "derived_by_versioned_normalizer",
        ),
        (
            "G4_IMS_PARAMETER_GRID",
            "state_snapshot_sha256",
            None,
            "unreconstructable_refuse",
        ),
        (
            "G4_IMS_PARAMETER_GRID",
            "route_signature_sha256",
            None,
            "unreconstructable_refuse",
        ),
        (
            "G4_MEDIUM_ISLAND_REBUILD",
            "route_signature_sha256",
            _TASK6_HAS_RECONSTRUCTABLE_PROJECTION,
            "derived_by_versioned_normalizer",
        ),
        (
            "G4_L30_RESOURCE_BASELINE",
            "state_snapshot_sha256",
            None,
            "not_applicable_retired_stage",
        ),
        (
            "G4_L30_RESOURCE_BASELINE",
            "route_signature_sha256",
            None,
            "not_applicable_retired_stage",
        ),
    ],
)
def test_task6_g4_state_and_route_rows_cover_explicit_generated_and_l30_absence(
    tmp_path: Path,
    case_id: str,
    dimension: str,
    projection: JsonObject | None,
    status: str,
) -> None:
    record = _task6_required_record(
        _task6_records(tmp_path),
        authority="G4_FREEZE",
        subject_id=case_id,
        dimension=dimension,
    )

    assert record["dimension_status"] == status
    _task6_assert_record_matches_projection(record, projection)


@pytest.mark.parametrize(
    ("subject_id", "dimension", "projection", "status"),
    [
        (
            "G4_IMS_PARAMETER_GRID:cell_id:ims_cell_01",
            "case_content_sha256",
            _TASK6_HAS_RECONSTRUCTABLE_PROJECTION,
            "derived_by_versioned_normalizer",
        ),
        (
            "G4_IMS_PARAMETER_GRID:cell_id:ims_cell_01",
            "parameter_tuple_sha256",
            _TASK6_HAS_RECONSTRUCTABLE_PROJECTION,
            "derived_by_versioned_normalizer",
        ),
        (
            "G4_IMS_PARAMETER_GRID:cell_id:ims_cell_01",
            "sealed_prediction_sha256",
            None,
            "unreconstructable_refuse",
        ),
        (
            "G4_L30_RESOURCE_BASELINE:name:l30-bound-a",
            "parameter_tuple_sha256",
            _TASK6_HAS_RECONSTRUCTABLE_PROJECTION,
            "derived_by_versioned_normalizer",
        ),
        (
            "G4_B05_SUPERVISOR_COMPARATOR:monitor_id:monitor-cover-a",
            "parameter_tuple_sha256",
            _TASK6_HAS_RECONSTRUCTABLE_PROJECTION,
            "derived_by_versioned_normalizer",
        ),
        (
            "G4_L30_RESOURCE_BASELINE:name:l30-bound-a",
            "sealed_prediction_sha256",
            None,
            "not_applicable_retired_stage",
        ),
        (
            "G4_B05_SUPERVISOR_COMPARATOR:monitor_id:monitor-cover-a",
            "sealed_prediction_sha256",
            None,
            "not_applicable_retired_stage",
        ),
    ],
)
def test_task6_subunit_case_parameter_and_prediction_rows_are_explicit(
    tmp_path: Path,
    subject_id: str,
    dimension: str,
    projection: JsonObject | None,
    status: str,
) -> None:
    record = _task6_required_record(
        _task6_records(tmp_path),
        authority="G4_FREEZE",
        subject_id=subject_id,
        dimension=dimension,
    )

    assert record["dimension_status"] == status
    _task6_assert_record_matches_projection(record, projection)


@pytest.mark.parametrize(
    (
        "case_id",
        "protocol_kind",
        "selected_subunit",
        "parent_context",
        "allowed_change",
        "selected_change",
    ),
    [
        (
            "G4_IMS_PARAMETER_GRID",
            "bidirectional_island_grid",
            _task6_grid_cell(),
            {"generator_id": BIDIRECTIONAL_GENERATOR_ID},
            {"generator_id": "changed_generator_id"},
            {"machine_capacity": 2},
        ),
        (
            "G4_L30_RESOURCE_BASELINE",
            "supplied_l30_inequalities",
            {"name": "l30-bound-a", "coefficients": {"p1": 1, "p2": -1}, "rhs": 1},
            {
                "capacities": {"p1": 3, "p2": 2},
                "finite_capacity_s3pr_ens3pr": True,
                "inequality_provenance": "synthetic-l30-proof",
            },
            {"capacities": {"p1": 4, "p2": 2}},
            {"rhs": 2},
        ),
        (
            "G4_B05_SUPERVISOR_COMPARATOR",
            "adapted_candidate_monitor_cover",
            {
                "monitor_id": "monitor-cover-a",
                "covered_bad_states": ["s1"],
                "excluded_legal_states": [],
            },
            {
                "finite_lts": _task6_finite_lts(),
                "legal_states": ["s0"],
                "first_met_bad_states": ["s1"],
                "state_bound": 3,
            },
            {"state_bound": 4},
            {"covered_bad_states": ["s1", "s2"]},
        ),
    ],
)
def test_task6_subunit_parameter_projection_uses_only_allowed_parent_context(
    case_id: str,
    protocol_kind: str,
    selected_subunit: JsonObject,
    parent_context: JsonObject,
    allowed_change: JsonObject,
    selected_change: JsonObject,
) -> None:
    base = _task6_projection_payload(
        "parameter_tuple_sha256",
        case_id=case_id,
        protocol_kind=protocol_kind,
        selected_subunit=selected_subunit,
        parent_context=parent_context,
    )
    ignored_sibling = _task6_projection_payload(
        "parameter_tuple_sha256",
        case_id=case_id,
        protocol_kind=protocol_kind,
        selected_subunit=selected_subunit,
        parent_context={**parent_context, "ignored_sibling": {"changed": True}},
    )
    changed_context = _task6_projection_payload(
        "parameter_tuple_sha256",
        case_id=case_id,
        protocol_kind=protocol_kind,
        selected_subunit=selected_subunit,
        parent_context={**parent_context, **allowed_change},
    )
    changed_selected = _task6_projection_payload(
        "parameter_tuple_sha256",
        case_id=case_id,
        protocol_kind=protocol_kind,
        selected_subunit={**selected_subunit, **selected_change},
        parent_context=parent_context,
    )

    assert canonical_sha256_v2(base) == canonical_sha256_v2(ignored_sibling)
    assert canonical_sha256_v2(base) != canonical_sha256_v2(changed_context)
    assert canonical_sha256_v2(base) != canonical_sha256_v2(changed_selected)


def test_task6_sealed_prediction_uses_section_7_4_nested_records() -> None:
    projection = _task6_projection_payload("sealed_prediction_sha256")
    hypothesis = cast(list[JsonObject], projection["directional_hypotheses"])[0]
    falsifier = cast(list[JsonObject], projection["falsifiers"])[0]

    assert set(hypothesis) == {
        "hypothesis_role",
        "statement",
        "direction",
        "estimand_id",
        "scope_code",
        "falsifier_roles",
    }
    assert set(falsifier) == {
        "falsifier_role",
        "condition_code",
        "affected_hypothesis_roles",
    }
    assert set(cast(JsonObject, projection["scoring_rule"])) == {
        "scoring_rule_id",
        "required_input_roles",
        "decision_table_sha256",
        "failure_handling_code",
    }
    assert set(cast(JsonObject, projection["claim_boundary"])) == {
        "study_role",
        "confirmation_use",
        "estimand_scope_code",
        "population_scope_code",
        "forbidden_upgrade_codes",
    }
    assert all(isinstance(item, dict) for item in projection["directional_hypotheses"])
    assert all(isinstance(item, dict) for item in projection["falsifiers"])


@pytest.mark.parametrize(
    ("raw", "canonical"),
    [
        ("1.2300", "1.23"),
        ("1.2300e+2", "123"),
        ("0.0000100", "0.00001"),
        ("000123.4500", "123.45"),
        ("42", "42"),
        (
            "12345678901234567890.1234567890123456789000",
            "12345678901234567890.1234567890123456789",
        ),
    ],
)
def test_task6_exact_decimal_edges_are_canonicalized_without_float_rounding(
    raw: str,
    canonical: str,
) -> None:
    parsed = cast(Any, normalizer).parse_historical_decimal_exactly(
        canonical_bytes_v2({"decimal": raw})
    )

    assert parsed == {"decimal": canonical}


@pytest.mark.parametrize("raw", ["-0", "-0.000", "1.2.3", "not-a-decimal"])
def test_task6_invalid_or_negative_zero_decimals_refuse(raw: str) -> None:
    with pytest.raises(SchemaContractError):
        cast(Any, normalizer).parse_historical_decimal_exactly(
            canonical_bytes_v2({"decimal": raw})
        )


@pytest.mark.parametrize(
    ("case_id", "mutate"),
    [
        (
            "G4_IMS_PARAMETER_GRID",
            lambda payload: cast(
                JsonObject, cast(JsonObject, payload["input_payload"])["protocol_input"]
            ).update({"cells": []}),
        ),
        (
            "G4_IMS_PARAMETER_GRID",
            lambda payload: cast(
                JsonObject, cast(JsonObject, payload["input_payload"])["protocol_input"]
            ).update(
                {
                    "cells": [
                        _task6_grid_cell(),
                        _task6_grid_cell(),
                    ]
                }
            ),
        ),
        (
            "G4_L30_RESOURCE_BASELINE",
            lambda payload: cast(
                JsonObject, cast(JsonObject, payload["input_payload"])["protocol_input"]
            ).update({"inequalities": []}),
        ),
        (
            "G4_B05_SUPERVISOR_COMPARATOR",
            lambda payload: cast(
                JsonObject, cast(JsonObject, payload["input_payload"])["protocol_input"]
            ).update({"candidate_monitors": []}),
        ),
    ],
)
def test_task6_zero_or_multiple_composite_selector_matches_refuse(
    tmp_path: Path,
    case_id: str,
    mutate: Callable[[JsonObject], None],
) -> None:
    _task6_expect_refusal(
        tmp_path,
        {_task6_case_path(case_id): mutate},
    )


@pytest.mark.parametrize(
    "mutate",
    [
        lambda payload: cast(
            JsonObject, cast(JsonObject, payload["input_payload"])["protocol_input"]
        ).update(
            {"cells": [{k: v for k, v in _task6_grid_cell().items() if k != "cell_id"}]}
        ),
        lambda payload: cast(
            JsonObject, cast(JsonObject, payload["input_payload"])["protocol_input"]
        ).update(
            {
                "cells": [
                    _task6_grid_cell(),
                    {**_task6_grid_cell(), "machine_capacity": 2},
                ]
            }
        ),
    ],
)
def test_task6_malformed_or_duplicate_composite_selector_fails_closed(
    tmp_path: Path,
    mutate: Callable[[JsonObject], None],
) -> None:
    repo, _ = _task6_synthetic_repo(
        tmp_path,
        overrides={_task6_case_path("G4_IMS_PARAMETER_GRID"): mutate},
    )
    case_bytes = (repo / _task6_case_path("G4_IMS_PARAMETER_GRID")).read_bytes()
    rows = [
        row
        for row in _selector_rows()
        if row["source_path_pattern"] == "cases/confirmation/g4/cases/{case_id}.json"
    ]

    try:
        subjects = cast(Any, normalizer)._g4_subjects(
            "G4_IMS_PARAMETER_GRID",
            "bidirectional_island_grid",
            case_bytes,
            rows,
        )
    except SchemaContractError:
        return
    assert not any(
        "unreconstructable-subunit" in cast(str, subject["subject_id"])
        for subject in subjects
    )
    pytest.fail("malformed or duplicate composite selector must fail closed")


@pytest.mark.parametrize(
    "case_id",
    [
        "G4_ADVERSARIAL_BOUNDARY",
        "G4_IMS_PARAMETER_GRID",
        "G4_MEDIUM_ISLAND_REBUILD",
    ],
)
def test_task6_unknown_generated_generator_id_fails_closed(
    tmp_path: Path,
    case_id: str,
) -> None:
    def mutate(payload: JsonObject) -> None:
        protocol_input = cast(
            JsonObject,
            cast(JsonObject, payload["input_payload"])["protocol_input"],
        )
        protocol_input["generator_id"] = "unknown_generator_v1"

    try:
        records = _task6_records(
            tmp_path,
            overrides={_task6_case_path(case_id): mutate},
        )
    except SchemaContractError:
        return
    generator_dependent = [
        record
        for record in records.values()
        if record["source_authority_id"] == "G4_FREEZE"
        and record["dimension"]
        in {
            "case_content_sha256",
            "state_snapshot_sha256",
            "route_signature_sha256",
            "parameter_tuple_sha256",
        }
        and (
            record["subject_id"] == case_id
            or record["owner_object_id"] == case_id
            or cast(str, record["subject_id"]).startswith(f"{case_id}:")
        )
    ]

    assert generator_dependent
    assert all(
        record["dimension_status"] == "unreconstructable_refuse"
        for record in generator_dependent
    )
    assert (
        _task6_single_record(
            records,
            authority="G4_FREEZE",
            subject_id=f"{case_id}:exact_companion",
            dimension="random_stream_manifest_sha256",
        )["dimension_status"]
        == "direct_stored"
    )
    assert (
        _task6_single_record(
            records,
            authority="G4_FREEZE",
            subject_id=case_id,
            dimension="sealed_prediction_sha256",
        )["dimension_status"]
        == "derived_by_versioned_normalizer"
    )
    assert (
        _task6_single_record(
            records,
            authority="G4_FREEZE",
            subject_id=f"{case_id}:exact_des_companion_group",
            dimension="metric_schema_sha256",
        )["dimension_status"]
        == "derived_by_versioned_normalizer"
    )
    assert (
        _task6_single_record(
            records,
            authority="G4_FREEZE",
            subject_id=f"{case_id}:exact_companion",
            dimension="output_root_reservation_sha256",
        )["dimension_status"]
        == "not_applicable_retired_stage"
    )


@pytest.mark.parametrize(
    "dimension",
    [
        "case_content_sha256",
        "random_stream_manifest_sha256",
        "sealed_prediction_sha256",
        "metric_schema_sha256",
    ],
)
def test_task6_g4_producer_rows_use_exact_source_keys_status_and_hashes(
    tmp_path: Path,
    dimension: str,
) -> None:
    records = _task6_records(tmp_path)
    record = _task6_single_record(
        records,
        authority="G4_FREEZE",
        subject_id=_task6_g4_subject_id_for_dimension(dimension),
        dimension=dimension,
    )
    projection = _task6_projection_payload(dimension)

    if dimension == "case_content_sha256":
        assert record["dimension_status"] == "unreconstructable_refuse"
        _task6_assert_record_matches_projection(record, None)
        return

    assert record["dimension_status"] == (
        "direct_stored"
        if dimension == "random_stream_manifest_sha256"
        else "derived_by_versioned_normalizer"
    )
    assert record["source_artifact_refs"] == _task6_g4_source_refs_for_dimension(
        dimension
    )
    assert set(record["source_artifact_byte_hashes"]) == {
        ref["repo_relative_posix_path"]
        for ref in _task6_g4_source_refs_for_dimension(dimension)
    }
    _task6_assert_record_matches_projection(record, projection)


def test_task6_g4_output_root_is_explicit_retired_stage_refusal(
    tmp_path: Path,
) -> None:
    record = _task6_single_record(
        _task6_records(tmp_path),
        authority="G4_FREEZE",
        subject_id="G4_IMS_PARAMETER_GRID:exact_companion",
        dimension="output_root_reservation_sha256",
    )

    assert record["dimension_status"] == "not_applicable_retired_stage"
    assert record["applicability_reason_code_or_null"] == "not_applicable_retired_stage"
    _task6_assert_record_matches_projection(record, None)


def test_task6_g5_output_root_projection_uses_only_lock_schedule_and_raw_root(
    tmp_path: Path,
) -> None:
    record = _task6_single_record(
        _task6_records(tmp_path),
        authority="G5_EXECUTION",
        subject_id="G5_EXECUTION:G4_IMS_PARAMETER_GRID:primary",
        dimension="output_root_reservation_sha256",
    )

    assert record["source_artifact_refs"] == [
        {
            "authority_id": "G5_EXECUTION",
            "repo_relative_posix_path": "evidence/g5/G5_EXECUTION_LOCK.json",
            "json_pointer_or_null": "/output_roots/raw_output_root_relative",
            "source_role": "output_root_containment_projection",
        },
        {
            "authority_id": "G5_EXECUTION",
            "repo_relative_posix_path": "evidence/g5/G5_EXECUTION_LOCK.json",
            "json_pointer_or_null": "/execution_schedule",
            "source_role": "method_stage_projection",
        },
    ]
    _task6_assert_record_matches_projection(
        record,
        _task6_output_root_projection(authority="G5_EXECUTION"),
    )


@pytest.mark.parametrize(
    "raw_root",
    [
        "/absolute/not-allowed",
        "../escape",
        "artifacts/g5-execution/../raw",
        "artifacts/g5-execution/raw\\windows",
    ],
)
def test_task6_g5_output_root_path_containment_refuses(
    tmp_path: Path,
    raw_root: str,
) -> None:
    def mutate(payload: JsonObject) -> None:
        cast(JsonObject, payload["output_roots"])["raw_output_root_relative"] = raw_root

    _task6_expect_refusal(
        tmp_path,
        {"evidence/g5/G5_EXECUTION_LOCK.json": mutate},
    )


def test_task6_g6r_output_root_requires_lock_raw_equality_and_unique_r3_suffix(
    tmp_path: Path,
) -> None:
    record = _task6_single_record(
        _task6_records(tmp_path),
        authority="G6_R_REPLAY_R3",
        subject_id="G6_R_REPLAY_R3:G4_IMS_PARAMETER_GRID:R3",
        dimension="output_root_reservation_sha256",
    )

    assert record["source_artifact_refs"] == [
        {
            "authority_id": "G6_R_REPLAY_R3",
            "repo_relative_posix_path": "evidence/g6/G6_HISTORICAL_REPLAY_LOCK_R3.json",
            "json_pointer_or_null": "/output_root",
            "source_role": "output_root_containment_projection",
        },
        {
            "authority_id": "G6_R_REPLAY_R3",
            "repo_relative_posix_path": (
                "evidence/g6/G6_HISTORICAL_REPLAY_R3_RAW_HASH_MANIFEST.json"
            ),
            "json_pointer_or_null": "/output_root",
            "source_role": "output_root_source_equality_validation",
        },
    ]
    assert record["source_run_role_or_null"] == "R3"
    assert record["source_run_role_or_null"] != "r3"
    _task6_assert_record_matches_projection(
        record,
        _task6_output_root_projection(authority="G6_R_REPLAY_R3"),
    )


@pytest.mark.parametrize(
    ("lock_root", "raw_root"),
    [
        (
            "D:\\historical\\artifacts\\g6-historical-replay\\R3",
            "D:\\historical\\artifacts\\g6-historical-replay\\R4",
        ),
        (
            "D:\\historical\\no-marker\\R3",
            "D:\\historical\\no-marker\\R3",
        ),
        (
            (
                "D:\\historical\\artifacts\\g6-historical-replay\\R3\\"
                "artifacts\\g6-historical-replay\\R3"
            ),
            (
                "D:\\historical\\artifacts\\g6-historical-replay\\R3\\"
                "artifacts\\g6-historical-replay\\R3"
            ),
        ),
        (
            "D:\\historical\\Artifacts\\g6-historical-replay\\R3",
            "D:\\historical\\Artifacts\\g6-historical-replay\\R3",
        ),
    ],
)
def test_task6_g6r_root_mismatch_missing_repeated_or_case_drift_refuses(
    tmp_path: Path,
    lock_root: str,
    raw_root: str,
) -> None:
    def mutate_lock(payload: JsonObject) -> None:
        payload["output_root"] = lock_root

    def mutate_raw(payload: JsonObject) -> None:
        payload["output_root"] = raw_root

    _task6_expect_refusal(
        tmp_path,
        {
            "evidence/g6/G6_HISTORICAL_REPLAY_LOCK_R3.json": mutate_lock,
            "evidence/g6/G6_HISTORICAL_REPLAY_R3_RAW_HASH_MANIFEST.json": mutate_raw,
        },
    )


@pytest.mark.parametrize(
    ("authority", "subject_id", "dimension", "ancestor_authority", "ancestor_id"),
    [
        (
            "G5_EXECUTION",
            "G5_EXECUTION:G4_MEDIUM_ISLAND_REBUILD:case_content_sha256",
            "case_content_sha256",
            "G4_FREEZE",
            "G4_MEDIUM_ISLAND_REBUILD",
        ),
        (
            "G5_EXECUTION",
            "G5_EXECUTION:G4_IMS_PARAMETER_GRID:random_stream_manifest_sha256",
            "random_stream_manifest_sha256",
            "G4_FREEZE",
            "G4_IMS_PARAMETER_GRID:exact_companion",
        ),
        (
            "G5_EXECUTION",
            "G5_EXECUTION:G4_IMS_PARAMETER_GRID:metric_schema_sha256",
            "metric_schema_sha256",
            "G4_FREEZE",
            "G4_IMS_PARAMETER_GRID:exact_des_companion_group",
        ),
        (
            "G6_R_REPLAY_R3",
            "G6_R_REPLAY_R3:G4_MEDIUM_ISLAND_REBUILD:case_content_sha256",
            "case_content_sha256",
            "G5_EXECUTION",
            "G5_EXECUTION:G4_MEDIUM_ISLAND_REBUILD:case_content_sha256",
        ),
        (
            "G6_R_REPLAY_R3",
            "G6_R_REPLAY_R3:G4_IMS_PARAMETER_GRID:random_stream_manifest_sha256",
            "random_stream_manifest_sha256",
            "G5_EXECUTION",
            "G5_EXECUTION:G4_IMS_PARAMETER_GRID:random_stream_manifest_sha256",
        ),
    ],
)
def test_task6_g5_and_g6r_inheritance_preserves_each_subject_class(
    tmp_path: Path,
    authority: str,
    subject_id: str,
    dimension: str,
    ancestor_authority: str,
    ancestor_id: str,
) -> None:
    records = _task6_records(tmp_path)
    inherited = _task6_required_record(
        records,
        authority=authority,
        subject_id=subject_id,
        dimension=dimension,
    )
    ancestor = _task6_required_record(
        records,
        authority=ancestor_authority,
        subject_id=ancestor_id,
        dimension=dimension,
    )

    assert inherited["dimension_status"] == "inherited_from_authority"
    assert inherited["lineage_id"] == ancestor["lineage_id"]
    assert inherited["inherited_from_record_id_or_null"] == ancestor["record_id"]
    assert inherited["duplicate_lineage_of_record_id_or_null"] is None


@pytest.mark.parametrize(
    ("authority", "subject_id"),
    [
        ("G5_EXECUTION", "G5_EXECUTION:G4_IMS_PARAMETER_GRID:case_content_sha256"),
        ("G6_R_REPLAY_R3", "G6_R_REPLAY_R3:G4_IMS_PARAMETER_GRID:case_content_sha256"),
    ],
)
def test_task6_grid_downstream_case_content_remains_unreconstructable(
    tmp_path: Path,
    authority: str,
    subject_id: str,
) -> None:
    records = _task6_records(tmp_path)
    g4_grid = _task6_required_record(
        records,
        authority="G4_FREEZE",
        subject_id="G4_IMS_PARAMETER_GRID",
        dimension="case_content_sha256",
    )
    downstream = [
        record
        for record in records.values()
        if record["source_authority_id"] == authority
        and record["subject_id"] == subject_id
        and record["dimension"] == "case_content_sha256"
    ]

    assert g4_grid["dimension_status"] == "unreconstructable_refuse"
    assert not downstream


def test_task6_g6r_metric_overlay_retains_g4_metric_lineage_input(
    tmp_path: Path,
) -> None:
    records = _task6_records(tmp_path)
    g4_metric = _task6_required_record(
        records,
        authority="G4_FREEZE",
        subject_id="G4_IMS_PARAMETER_GRID:exact_des_companion_group",
        dimension="metric_schema_sha256",
    )
    overlay = _task6_required_record(
        records,
        authority="G6_R_REPLAY_R3",
        subject_id="G6_R_REPLAY_R3:G4_IMS_PARAMETER_GRID:exact_des_companion_group",
        dimension="metric_schema_sha256",
    )

    assert overlay["dimension_status"] == "derived_by_versioned_normalizer"
    assert overlay["source_artifact_refs"] == [
        *cast(list[JsonObject], g4_metric["source_artifact_refs"]),
        {
            "authority_id": "G6_R_REPLAY_R3",
            "repo_relative_posix_path": "evidence/g6/G6_HISTORICAL_REPLAY_LOCK_R3.json",
            "json_pointer_or_null": "/default_estimand_spec",
            "source_role": "metric_projection",
        },
        {
            "authority_id": "G6_R_REPLAY_R3",
            "repo_relative_posix_path": "evidence/g6/G6_HISTORICAL_REPLAY_LOCK_R3.json",
            "json_pointer_or_null": "/default_estimand_spec_sha256",
            "source_role": "metric_projection",
        },
    ]
    assert g4_metric["lineage_id"] in cast(str, overlay["lineage_id"])


def test_task6_inherited_records_preserve_six_field_origin_lineage(
    tmp_path: Path,
) -> None:
    records = _task6_records(tmp_path)
    origin = _task6_single_record(
        records,
        authority="G4_FREEZE",
        subject_id="G4_MEDIUM_ISLAND_REBUILD",
        dimension="case_content_sha256",
    )
    inherited = _task6_single_record(
        records,
        authority="G5_EXECUTION",
        subject_id="G5_EXECUTION:G4_MEDIUM_ISLAND_REBUILD:case_content_sha256",
        dimension="case_content_sha256",
    )
    preimage: JsonObject = {
        "origin_authority_id": "G4_FREEZE",
        "origin_subject_type": "retired_case",
        "origin_subject_id": "G4_MEDIUM_ISLAND_REBUILD",
        "origin_dimension": "case_content_sha256",
        "origin_comparison_projection_sha256_or_null": origin[
            "comparison_projection_sha256_or_null"
        ],
        "origin_source_artifact_byte_hashes": origin["source_artifact_byte_hashes"],
    }

    assert origin["lineage_id"] == f"sha256:{canonical_sha256_v2(preimage)}"
    assert inherited["dimension_status"] == "inherited_from_authority"
    assert inherited["lineage_id"] == origin["lineage_id"]
    assert inherited["inherited_from_record_id_or_null"] == origin["record_id"]
    assert inherited["duplicate_lineage_of_record_id_or_null"] is None


def test_task6_unique_lineage_accounting_allows_zero_or_more_duplicate_aliases(
    tmp_path: Path,
) -> None:
    records = _task6_records(tmp_path)
    unique_lineage_map = {
        lineage_id: sorted(
            record["record_id"]
            for record in records.values()
            if record["lineage_id"] == lineage_id
        )
        for lineage_id in sorted(
            {cast(str, record["lineage_id"]) for record in records.values()}
        )
    }
    canonical_lineages = {
        record["lineage_id"]
        for record in records.values()
        if record["duplicate_lineage_of_record_id_or_null"] is None
    }
    dimension_status_counts = {
        status: sum(
            1 for record in records.values() if record["dimension_status"] == status
        )
        for status in contracts.DIMENSION_STATUS_VALUES
    }
    aliases = [
        record
        for record in records.values()
        if record["duplicate_lineage_of_record_id_or_null"] is not None
    ]

    assert sum(dimension_status_counts.values()) == len(records)
    assert len(unique_lineage_map) == len(canonical_lineages)
    for alias in aliases:
        origin_id = cast(str, alias["duplicate_lineage_of_record_id_or_null"])
        origin = records[origin_id]
        assert alias["dimension"] == origin["dimension"]
        assert alias["lineage_id"] == origin["lineage_id"]
        assert alias["record_id"] in unique_lineage_map[cast(str, origin["lineage_id"])]
        assert origin_id in unique_lineage_map[cast(str, origin["lineage_id"])]
        same_lineage = [
            record
            for record in records.values()
            if record["lineage_id"] == origin["lineage_id"]
            and record["duplicate_lineage_of_record_id_or_null"] is None
        ]
        assert len(same_lineage) == 1


def test_task6_duplicate_lineage_marking_skips_inherited_records() -> None:
    records: dict[str, JsonObject] = {
        "origin-a": {
            "record_id": "origin-a",
            "lineage_id": "sha256:" + "a" * 64,
            "dimension": "case_content_sha256",
            "inherited_from_record_id_or_null": None,
            "duplicate_lineage_of_record_id_or_null": None,
            "record_provenance_sha256": None,
        },
        "origin-b": {
            "record_id": "origin-b",
            "lineage_id": "sha256:" + "a" * 64,
            "dimension": "case_content_sha256",
            "inherited_from_record_id_or_null": None,
            "duplicate_lineage_of_record_id_or_null": None,
            "record_provenance_sha256": None,
        },
        "inherited-c": {
            "record_id": "inherited-c",
            "lineage_id": "sha256:" + "a" * 64,
            "dimension": "case_content_sha256",
            "inherited_from_record_id_or_null": "origin-a",
            "duplicate_lineage_of_record_id_or_null": None,
            "record_provenance_sha256": None,
        },
    }

    normalizer._mark_duplicate_lineages(records)

    assert records["origin-a"]["duplicate_lineage_of_record_id_or_null"] is None
    assert records["origin-b"]["duplicate_lineage_of_record_id_or_null"] == "origin-a"
    assert records["inherited-c"]["duplicate_lineage_of_record_id_or_null"] is None


@pytest.mark.parametrize(
    ("path", "mutate"),
    [
        (
            _task6_case_path("G4_IMS_PARAMETER_GRID"),
            lambda payload: cast(
                JsonObject, cast(JsonObject, payload["input_payload"])["protocol_input"]
            ).pop("generator_id"),
        ),
        (
            _task6_case_path("G4_IMS_PARAMETER_GRID"),
            lambda payload: cast(
                JsonObject, cast(JsonObject, payload["input_payload"])["protocol_input"]
            ).update(
                {
                    "cells": [
                        _task6_grid_cell(),
                        {**_task6_grid_cell(), "buffer_capacity": 2},
                    ]
                }
            ),
        ),
        (
            "cases/confirmation/g4/predictions.json",
            lambda payload: cast(JsonObject, payload["predictions"]).pop(
                "G4_IMS_PARAMETER_GRID"
            ),
        ),
        (
            "cases/confirmation/g4/random_stream_manifest.json",
            lambda payload: cast(JsonObject, payload["streams_by_case"]).pop(
                "G4_IMS_PARAMETER_GRID"
            ),
        ),
    ],
)
def test_task6_missing_or_ambiguous_required_inputs_refuse(
    tmp_path: Path,
    path: str,
    mutate: Callable[[JsonObject], None],
) -> None:
    _task6_expect_refusal(tmp_path, {path: mutate})


def test_task6_selector_matrix_isolates_source_paths_and_allowed_uses(
    tmp_path: Path,
) -> None:
    repo, _ = _task6_synthetic_repo(tmp_path)
    g4_case = (repo / _task6_case_path("G4_IMS_PARAMETER_GRID")).read_bytes()
    g5_result = (repo / "evidence/g5/G5_RESULT_SUMMARY.json").read_bytes()
    selector_rows = _selector_rows()

    selected = select_allowed_value(
        g4_case,
        pointer="/input_payload/protocol_input/generator_id",
        selector_rows=[
            row
            for row in selector_rows
            if row["source_path_pattern"]
            == "cases/confirmation/g4/cases/{case_id}.json"
        ],
        requested_use="case_content_projection",
    )
    assert selected == BIDIRECTIONAL_GENERATOR_ID
    with pytest.raises(SchemaContractError, match="source_field_read_violation"):
        select_allowed_value(
            g4_case,
            pointer="/input_payload/protocol_input/generator_id",
            selector_rows=[
                row
                for row in selector_rows
                if row["source_path_pattern"]
                == "cases/confirmation/g4/predictions.json"
            ],
            requested_use="case_content_projection",
        )
    with pytest.raises(SchemaContractError, match="source_field_read_violation"):
        select_allowed_value(
            g5_result,
            pointer="/completion_probability",
            selector_rows=[
                row
                for row in selector_rows
                if row["source_path_pattern"] == "evidence/g5/G5_RESULT_SUMMARY.json"
            ],
            requested_use="case_content_projection",
        )


def test_task6_forbidden_outcome_strings_never_enter_source_or_records(
    tmp_path: Path,
) -> None:
    source = inspect.getsource(normalizer)
    records = _task6_records(tmp_path)
    serialized = canonical_bytes_v2(cast(JsonObject, {"records": records})).decode(
        "utf-8"
    )

    for forbidden in _TASK6_FORBIDDEN_OUTCOME_NAMES:
        assert forbidden not in source
        assert forbidden not in serialized
