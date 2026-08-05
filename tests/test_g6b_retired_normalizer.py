from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, cast

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
from ims_deadlock import g6b_schema_contracts as contracts
from ims_deadlock.g6b_canonical_json import (
    canonical_bytes_v2,
    canonical_sha256_v2,
    finalized_self_hash,
    loads_v2,
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
    value = loads_v2(path.read_bytes())
    assert isinstance(value, dict)
    return value


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
