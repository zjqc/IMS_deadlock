from __future__ import annotations

# ruff: noqa: I001

import hashlib
import json
import sys
import ast
from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal, cast

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from ims_deadlock import g6b_schema_contracts as contracts
from ims_deadlock.g6b_canonical_json import (
    canonical_bytes_v2,
    canonical_sha256_v2,
    finalized_self_hash,
    loads_v2,
)
from ims_deadlock.g6b_schema_contracts import (
    ALLOWED_FILE_ROLES,
    ALLOWED_OPERATIONS,
    ALLOWED_OUTPUT_SCHEMA_IDS,
    ALLOWED_PREFLIGHT_PROJECT_IMPORTS,
    ALLOWED_PREFLIGHT_WRITER_SYMBOLS,
    BUNDLE_STATES,
    CAPABILITY_FIELDS,
    CAPABILITY_NAMES,
    COMPARISON_POLICIES,
    COMPARISON_STATUS_VALUES,
    FINGERPRINT_DIMENSIONS,
    PROJECTION_KINDS,
    QUANTITATIVE_PLACEHOLDER_CODES,
    SchemaContractError,
    validate_command_manifest,
    validate_declared_terminal_partition,
    validate_dimension_comparison_record,
    validate_exact_keys,
    validate_file_role_cardinality,
    validate_fingerprint_record,
    validate_g4_manifest_freeze_reconciliation,
    validate_normalizer_static_source,
    validate_output_root_reservation,
    validate_refusal_codes,
    validate_retired_authority_lineage_reproduction,
    validate_retired_authority_source_inventory,
    validate_source_pointer_use,
    validate_subject_free_projection,
    validate_typed_capabilities,
)

JsonObject = dict[str, Any]

_TEST_BUNDLE_ID = "bundle-test"
_TEST_CASE_UNIT_ID = "case-test"
_TEST_METHOD_OBSERVATION_ID = "method-test"
_TEST_METHOD_COMPANION_GROUP_ID = "metric-group-test"
_TEST_RUN_ROLE = "primary"
_TEST_LOGICAL_ROOT_ID = "opaque-root-test"
_TEST_OUTPUT_ROOT = (
    "artifacts/g6b/quantitative/"
    f"{_TEST_BUNDLE_ID}/{_TEST_CASE_UNIT_ID}/"
    f"{_TEST_METHOD_OBSERVATION_ID}/{_TEST_RUN_ROLE}"
)
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
_ALLOWED_G6B_ESTIMAND_IDS = (
    "g6b_estimand_theta_global_before_success_v1",
    "g6b_estimand_theta_local_before_success_v1",
    "g6b_estimand_theta_selected_bad_before_success_v1",
)


def _subject_id_for_dimension(dimension: str) -> str:
    subject_kind = contracts.DIMENSION_SUBJECTS[dimension]
    if subject_kind == "case_unit":
        return _TEST_CASE_UNIT_ID
    if subject_kind == "method_observation":
        return _TEST_METHOD_OBSERVATION_ID
    if subject_kind == "method_companion_group":
        return _TEST_METHOD_COMPANION_GROUP_ID
    raise AssertionError(f"unhandled subject kind: {subject_kind}")


def _source_artifact_refs() -> list[JsonObject]:
    return [
        {
            "authority_id": "authority-test",
            "repo_relative_posix_path": "sealed/g6b/case-input-test.json",
            "json_pointer_or_null": "/case_units/0",
            "source_role": "case_content_projection",
        },
        {
            "authority_id": "authority-test",
            "repo_relative_posix_path": "sealed/g6b/method-scope-test.json",
            "json_pointer_or_null": "/method_observations/0",
            "source_role": "method_stage_projection",
        },
    ]


def _source_byte_hashes(refs: list[JsonObject]) -> dict[str, str]:
    return {
        ref["repo_relative_posix_path"]: f"{index}" * 64
        for index, ref in enumerate(
            sorted(refs, key=lambda item: item["repo_relative_posix_path"]),
            start=1,
        )
    }


def valid_fingerprint_record(*, dimension: str) -> JsonObject:
    projection = _projection_for_dimension(dimension)
    projection_hash = canonical_sha256_v2(projection)
    source_refs = _source_artifact_refs()
    record: JsonObject = {
        "record_schema_version": "ims-deadlock/g6b-fingerprint-record/v1",
        "record_id": f"fingerprint-test-{dimension}",
        "dimension": dimension,
        "projection_kind": contracts.DIMENSION_PROJECTION_KINDS[dimension],
        "subject_type": contracts.DIMENSION_SUBJECTS[dimension],
        "subject_id": _subject_id_for_dimension(dimension),
        "owner_object_id": _subject_id_for_dimension(dimension),
        "projection_schema_version": projection["projection_schema_version"],
        "comparison_projection_ref_or_null": (f"synthetic://projection/{dimension}"),
        "comparison_projection_sha256_or_null": projection_hash,
        "canonicalization_version": contracts.G6B_CANONICAL_JSON_VERSION,
        "source_authority_id": "authority-test",
        "source_stage": "CASE_INPUTS_SEALED_NO_EXECUTION",
        "source_method_role_or_null": (
            "exact_companion"
            if contracts.DIMENSION_SUBJECTS[dimension] != "case_unit"
            else None
        ),
        "source_run_role_or_null": _TEST_RUN_ROLE,
        "source_artifact_refs": source_refs,
        "source_artifact_byte_hashes": _source_byte_hashes(source_refs),
        "normalizer_version": "test-normalizer-v1",
        "dimension_status": "direct_stored",
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


def valid_output_root_reservation() -> JsonObject:
    record: JsonObject = {
        "projection_schema_version": (
            "ims-deadlock/g6b-output-root-reservation-projection/v1"
        ),
        "bundle_id": _TEST_BUNDLE_ID,
        "case_unit_id": _TEST_CASE_UNIT_ID,
        "method_observation_id": _TEST_METHOD_OBSERVATION_ID,
        "run_role": _TEST_RUN_ROLE,
        "logical_root_id": _TEST_LOGICAL_ROOT_ID,
        "repo_relative_posix_path": _TEST_OUTPUT_ROOT,
        "reserved": True,
        "materialized": False,
        "reservation_sha256": None,
    }
    record["reservation_sha256"] = finalized_self_hash(
        record,
        "reservation_sha256",
    )
    return record


def _with_rehashed(record: JsonObject, self_hash_field: str) -> JsonObject:
    updated = dict(record)
    updated[self_hash_field] = None
    updated[self_hash_field] = finalized_self_hash(updated, self_hash_field)
    return updated


def _projection_for_record(record: JsonObject) -> JsonObject:
    return _projection_for_dimension(record["dimension"])


def _valid_dimension_comparison_record(
    *,
    dimension: str = "case_content_sha256",
    status: str = "pass_distinct",
) -> JsonObject:
    left_projection = _projection_for_dimension(dimension)
    right_projection = dict(left_projection)
    right_projection["projection_schema_version"] = left_projection[
        "projection_schema_version"
    ]
    if dimension == "case_content_sha256":
        right_projection["control_declaration_sha256"] = "9" * 64
    elif dimension == "state_snapshot_sha256":
        right_projection["state_payload"] = {"states": ["s1"]}
    elif dimension == "random_stream_manifest_sha256":
        right_projection = {
            "projection_schema_version": "v1",
            "applicability_status": "applicable",
            "method_role": "des_companion",
            "prng_family": "Philox",
            "prng_version": "v1",
            "seed_root_commitment": "a" * 64,
            "seed_derivation_rule": "rule-v1",
            "substream_allocation": [{"stream_id": "stream-a"}],
            "replicate_plan": {"planned_replicates": 1},
            "sampling_plan": {"draw_budget_per_replication": 1},
        }
    elif dimension == "output_root_reservation_sha256":
        right_projection["logical_root_id"] = "opaque-root-alt"
        right_projection["repo_relative_posix_path"] = (
            "artifacts/g6b/quantitative/"
            f"{_TEST_BUNDLE_ID}/{_TEST_CASE_UNIT_ID}/"
            f"{_TEST_METHOD_OBSERVATION_ID}/secondary"
        )
    elif dimension == "metric_schema_sha256":
        right_projection["comparability_scope"] = "authorized_companion_group"
    elif dimension == "sealed_prediction_sha256":
        right_projection["claim_boundary"] = {"study_role": "confirmation_only"}
    else:
        right_projection["projection_schema_version"] = "v1"
    record: JsonObject = {
        "comparison_id": f"comparison-test-{dimension}",
        "bundle_id": _TEST_BUNDLE_ID,
        "new_fingerprint_record_hash": "1" * 64,
        "retired_fingerprint_record_hash": "2" * 64,
        "dimension": dimension,
        "projection_kind": contracts.DIMENSION_PROJECTION_KINDS[dimension],
        "new_subject_type": contracts.DIMENSION_SUBJECTS[dimension],
        "new_subject_id": _subject_id_for_dimension(dimension),
        "retired_authority_id": "retired-authority-test",
        "retired_lineage_id": f"retired-lineage-test-{dimension}",
        "new_comparison_projection_sha256_or_null": canonical_sha256_v2(
            left_projection
        ),
        "retired_comparison_projection_sha256_or_null": canonical_sha256_v2(
            right_projection
        ),
        "comparison_policy": contracts.DIMENSION_POLICIES[dimension],
        "comparison_status": status,
        "semantic_lineage_audit_ref_or_null": (
            "synthetic://lineage-audit"
            if dimension in contracts.SEMANTIC_COMPARISON_DIMENSIONS
            else None
        ),
        "reuse_authorization_ref_or_null": (
            "synthetic://metric-authorization"
            if dimension == "metric_schema_sha256" and status == "controlled_reuse_pass"
            else None
        ),
        "refusal_reason_code_or_null": None,
        "comparison_record_sha256": None,
    }
    record["comparison_record_sha256"] = finalized_self_hash(
        record,
        "comparison_record_sha256",
    )
    return record


def _with_rehashed_comparison(record: JsonObject) -> JsonObject:
    return _with_rehashed(record, "comparison_record_sha256")


def _with_null_projection(record: JsonObject, *, status: str) -> JsonObject:
    updated = dict(record)
    updated["dimension_status"] = status
    updated["comparison_projection_ref_or_null"] = None
    updated["comparison_projection_sha256_or_null"] = None
    return _with_rehashed(updated, "record_provenance_sha256")


def _validate_dimension_comparison_positive(record: JsonObject) -> None:
    dimension = record["dimension"]
    if dimension in contracts.SEMANTIC_COMPARISON_DIMENSIONS:
        validate_dimension_comparison_record(
            record,
            semantic_lineage_audit_passed=True,
        )
        return
    if dimension == "random_stream_manifest_sha256":
        branch: Literal["exact", "stochastic"] = (
            "exact"
            if record["comparison_status"] == "not_applicable_by_protocol_pass"
            else "stochastic"
        )
        validate_dimension_comparison_record(
            record,
            random_stream_branch=branch,
            disjoint_substream_proof_passed=branch == "stochastic",
        )
        return
    if dimension == "metric_schema_sha256":
        validate_dimension_comparison_record(record, metric_reuse_authorized=True)
        return
    validate_dimension_comparison_record(record)


def valid_normalization_authorization() -> JsonObject:
    schema = _load_retired_schema_definition()
    record: JsonObject = {
        "schema_version": "ims-deadlock/g6b-retired-normalization-authorization/v1",
        "authorization_id": "normalization-authorization-test",
        "capability": "retired_authority_fingerprint_normalization",
        "authorized": True,
        "source_head": _git_sha1("normalization-source-head"),
        "source_tree_hash": _git_sha1("normalization-source-tree"),
        "authority_ids": list(schema["retired_authority_ids"]),
        "expected_file_manifest_hash": "3" * 64,
        "allowed_source_paths": list(
            contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY
        ),
        "allowed_json_fields_by_source": deepcopy(
            schema["allowed_json_fields_by_source"]
        ),
        "allowed_historical_builder_symbols": [],
        "normalizer_code_sha256": "4" * 64,
        "allowed_operations": list(contracts.NORMALIZATION_ALLOWED_OPERATIONS),
        "allowed_project_imports": list(
            contracts.NORMALIZATION_ALLOWED_PROJECT_IMPORTS
        ),
        "forbidden_imports": list(contracts.NORMALIZATION_FORBIDDEN_IMPORTS),
        "forbidden_calls": list(contracts.NORMALIZATION_FORBIDDEN_CALLS),
        "allowed_output_schema": {
            "schema_id": "ims-deadlock/g6b-retired-normalization-records/v1",
            "schema_version": "v1",
        },
        "allowed_output_root": {
            "repo_relative_posix_path": _approved_normalization_governance_root(),
            "contains_only_governance_outputs": True,
        },
        "review_artifact_hash": "5" * 64,
        "issued_at_utc": "2030-01-01T00:00:00Z",
        "invalidated_by_identity_drift": False,
        "authorization_sha256": None,
    }
    record["authorization_sha256"] = finalized_self_hash(
        record,
        "authorization_sha256",
    )
    return record


def _load_retired_schema_definition() -> JsonObject:
    return cast(
        JsonObject,
        json.loads(_RETIRED_AUTHORITY_SCHEMA.read_text(encoding="utf-8")),
    )


def _retired_source_inventory() -> list[JsonObject]:
    def authority_id(path: str) -> str:
        if path.startswith("cases/confirmation/g4/"):
            return "G4_FREEZE"
        if path.startswith("evidence/g5/"):
            return "G5_EXECUTION"
        return "G6_R_REPLAY_R3"

    return [
        {
            "authority_id": authority_id(path),
            "source_id": f"source-{index:02d}",
            "repo_relative_posix_path": path,
            "declared_sha256": canonical_sha256_v2({"synthetic_source_path": path}),
            "verification_status": "verified",
            "lineage_status": "direct_stored",
            "local_only": False,
        }
        for index, path in enumerate(
            contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY
        )
    ]


def _retired_source_hashes() -> dict[str, str]:
    return {
        row["repo_relative_posix_path"]: row["declared_sha256"]
        for row in _retired_source_inventory()
    }


def valid_authority_lock_record(authority_id: str) -> JsonObject:
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

    for row in _retired_selector_rows():
        if path in expanded_patterns(row["source_path_pattern"]):
            uses.add(row["allowed_use"])
    return sorted(uses) or ["source_hash_validation"]


def valid_authority_source_record(
    path: str,
    *,
    authority_lock_record_sha256: str | None = None,
) -> JsonObject:
    authority_id = _authority_id_for_retired_path(path)
    lock_hash = (
        valid_authority_lock_record(authority_id)["authority_lock_record_sha256"]
        if authority_lock_record_sha256 is None
        else authority_lock_record_sha256
    )
    return {
        "authority_id": authority_id,
        "authority_stage": authority_id,
        "authority_lock_record_sha256": lock_hash,
        "repo_relative_path": path,
        "raw_byte_sha256": canonical_sha256_v2({"synthetic_source_path": path}),
        "declared_historical_hash_or_null": canonical_sha256_v2(
            {"synthetic_source_path": path}
        ),
        "declared_hash_algorithm_or_null": "sha256",
        "declared_hash_verified": True,
        "allowed_projection_uses": _allowed_projection_uses_for_path(path),
        "contains_outcome_fields": path == "evidence/g5/G5_RESULT_SUMMARY.json",
    }


def _retired_authority_lock_records() -> dict[str, JsonObject]:
    schema = _load_retired_schema_definition()
    return {
        authority_id: valid_authority_lock_record(authority_id)
        for authority_id in schema["retired_authority_ids"]
    }


def _retired_authority_source_records(
    lock_records: Mapping[str, JsonObject],
) -> dict[str, JsonObject]:
    return {
        path: valid_authority_source_record(
            path,
            authority_lock_record_sha256=lock_records[
                _authority_id_for_retired_path(path)
            ]["authority_lock_record_sha256"],
        )
        for path in contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY
    }


def _authority_lock_hashes(
    lock_records: Mapping[str, JsonObject],
) -> dict[str, str]:
    return {
        authority_id: record["authority_lock_record_sha256"]
        for authority_id, record in lock_records.items()
    }


def _relineage_fingerprint_record(record: JsonObject) -> JsonObject:
    updated = dict(record)
    lineage_preimage = {
        "origin_authority_id": updated["source_authority_id"],
        "origin_subject_type": updated["subject_type"],
        "origin_subject_id": updated["subject_id"],
        "origin_dimension": updated["dimension"],
        "origin_comparison_projection_sha256_or_null": updated[
            "comparison_projection_sha256_or_null"
        ],
        "origin_source_artifact_byte_hashes": updated["source_artifact_byte_hashes"],
    }
    updated["lineage_id"] = f"sha256:{canonical_sha256_v2(lineage_preimage)}"
    return _with_rehashed(updated, "record_provenance_sha256")


def _first_g4_case_source_path() -> str:
    return next(
        path
        for path in contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY
        if path.startswith("cases/confirmation/g4/cases/") and path.endswith(".json")
    )


def _normalization_source_refs_for_dimension(dimension: str) -> list[JsonObject]:
    g4_case = _first_g4_case_source_path()
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
        "output_root_reservation_sha256": [
            {
                "authority_id": "G4_FREEZE",
                "repo_relative_posix_path": "cases/confirmation/g4/FREEZE_ENTRY.json",
                "json_pointer_or_null": "/freeze_id",
                "source_role": "authority_identity",
            }
        ],
    }
    return refs_by_dimension[dimension]


def _source_hashes_for_refs(refs: Sequence[JsonObject]) -> dict[str, str]:
    retired_hashes = _retired_source_hashes()
    return {
        ref["repo_relative_posix_path"]: retired_hashes[ref["repo_relative_posix_path"]]
        for ref in refs
    }


def _normalization_fingerprint_records() -> dict[str, JsonObject]:
    records: dict[str, JsonObject] = {}
    for dimension in contracts.FINGERPRINT_DIMENSIONS:
        record = valid_fingerprint_record(dimension=dimension)
        record["record_id"] = f"g4-freeze-{dimension}"
        record["source_authority_id"] = "G4_FREEZE"
        source_refs = _normalization_source_refs_for_dimension(dimension)
        record["source_artifact_refs"] = source_refs
        record["source_artifact_byte_hashes"] = _source_hashes_for_refs(source_refs)
        if dimension == "output_root_reservation_sha256":
            record["dimension_status"] = "not_applicable_retired_stage"
            record["comparison_projection_ref_or_null"] = None
            record["comparison_projection_sha256_or_null"] = None
        record = _relineage_fingerprint_record(record)
        projection = (
            None
            if dimension == "output_root_reservation_sha256"
            else (_projection_for_record(record))
        )
        validate_fingerprint_record(record, projection)
        records[record["record_id"]] = record
    return records


def valid_normalization_manifest(
    *,
    authority_locks: Mapping[str, JsonObject] | None = None,
    authority_sources: Mapping[str, JsonObject] | None = None,
    fingerprint_records: Mapping[str, JsonObject] | None = None,
) -> JsonObject:
    locks = (
        _retired_authority_lock_records()
        if authority_locks is None
        else dict(authority_locks)
    )
    sources = (
        _retired_authority_source_records(locks)
        if authority_sources is None
        else dict(authority_sources)
    )
    fingerprints = (
        _normalization_fingerprint_records()
        if fingerprint_records is None
        else dict(fingerprint_records)
    )
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
        "manifest_id": "normalization-manifest-test",
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
        "normalization_authorization_sha256": _synthetic_hash(
            "normalization-authorization"
        ),
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
        "unreconstructable_records": sorted(
            record_id
            for record_id, record in fingerprints.items()
            if record["dimension_status"] == "unreconstructable_refuse"
        ),
        "comparison_eligibility": dict(sorted(comparison_eligibility.items())),
        "created_at_utc": "2030-01-01T00:00:00Z",
        "manifest_sha256": None,
    }
    manifest["manifest_sha256"] = finalized_self_hash(manifest, "manifest_sha256")
    return manifest


def _retired_selector_rows() -> list[JsonObject]:
    return deepcopy(_load_retired_schema_definition()["allowed_json_fields_by_source"])


def _approved_normalization_governance_root() -> str:
    return (
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "governance/g6b_retired_authority_normalization_v1"
    )


def _alternate_normalization_governance_root() -> str:
    return (
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "governance/alternate_retired_authority_normalization_v1"
    )


def _validate_valid_normalization_authorization(
    authorization: Mapping[str, Any],
) -> None:
    schema = _load_retired_schema_definition()
    contracts.validate_normalization_authorization(
        authorization,
        expected_schema_inventory_patterns=(
            contracts.EXPECTED_RETIRED_SOURCE_INVENTORY
        ),
        expected_concrete_source_paths=(
            contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY
        ),
        expected_selector_matrix=schema["allowed_json_fields_by_source"],
        expected_git_object_format="sha1",
        expected_source_head=cast(str, authorization.get("source_head", "")),
        expected_source_tree_hash=cast(str, authorization.get("source_tree_hash", "")),
        expected_file_manifest_hash=cast(
            str,
            authorization.get("expected_file_manifest_hash", ""),
        ),
        expected_normalizer_code_sha256=cast(
            str,
            authorization.get("normalizer_code_sha256", ""),
        ),
        expected_review_artifact_hash=cast(
            str,
            authorization.get("review_artifact_hash", ""),
        ),
        expected_output_root=_approved_normalization_governance_root(),
    )


def _git_sha1(label: str) -> str:
    return hashlib.sha1(canonical_bytes_v2({"synthetic_git_object": label})).hexdigest()


def _retired_lineage_metadata() -> JsonObject:
    return {
        "dimension_statuses": [
            "direct_stored",
            "derived_by_versioned_normalizer",
            "inherited_from_authority",
            "not_applicable_by_protocol",
            "not_applicable_retired_stage",
            "unreconstructable_refuse",
        ],
        "comparison_statuses": [
            "pass_distinct",
            "controlled_reuse_pass",
            "disjoint_stream_pass",
            "not_applicable_by_protocol_pass",
            "containment_separation_pass",
            "inherited_compared",
            "normalizer_error",
        ],
        "origin_rows": [
            {
                "origin": "G4_FREEZE",
                "lineage_id": f"sha256:{'1' * 64}",
                "duplicate_of_or_null": None,
                "counts_as_evidence": True,
            },
            {
                "origin": "G5_EXECUTION",
                "lineage_id": f"sha256:{'1' * 64}",
                "duplicate_of_or_null": f"sha256:{'1' * 64}",
                "counts_as_evidence": False,
            },
            {
                "origin": "G6_R_REPLAY_R3",
                "lineage_id": f"sha256:{'1' * 64}",
                "duplicate_of_or_null": f"sha256:{'1' * 64}",
                "counts_as_evidence": False,
            },
        ],
    }


def _normalizer_source(import_line: str = "from hashlib import sha256") -> str:
    return (
        f"{import_line}\n"
        "def normalize(source_bytes):\n"
        "    row = {'source_sha256': sha256(source_bytes).hexdigest()}\n"
        "    return row"
    )


def _g4_manifest_freeze_rows() -> list[JsonObject]:
    return [
        {
            "case_id": case_id,
            "repo_relative_posix_path": (f"cases/confirmation/g4/cases/{case_id}.json"),
            "declared_sha256": canonical_sha256_v2({"synthetic_g4_case_id": case_id}),
        }
        for case_id in contracts.G4_MANIFEST_CASE_IDS
    ]


def _subunit_record(
    protocol_kind: str,
    parent_id: str,
    component: str,
) -> JsonObject:
    selector, unique_key, parent_context = contracts.COMPOSITE_SUBUNIT_CONTRACTS[
        protocol_kind
    ]
    return {
        "parent_case_id": parent_id,
        "owner_object_id": parent_id,
        "protocol_kind": protocol_kind,
        "selector": selector,
        "unique_key": unique_key,
        "subunit_id_component": component,
        "parent_context_fields": list(parent_context),
        "canonical_payload_sha256": canonical_sha256_v2(
            {
                "parent_case_id": parent_id,
                "protocol_kind": protocol_kind,
                "subunit_id_component": component,
            }
        ),
    }


def _synthetic_hash(label: str) -> str:
    return canonical_sha256_v2({"synthetic_label": label})


def _overlap_subject_status(
    subject_type: str,
    subject_id: str,
    *,
    admission_status: str,
) -> JsonObject:
    refused = admission_status == "refused"
    required_dimensions = {
        "case_unit": (
            "case_content_sha256",
            "state_snapshot_sha256",
            "route_signature_sha256",
            "parameter_tuple_sha256",
            "sealed_prediction_sha256",
        ),
        "method_observation": (
            "random_stream_manifest_sha256",
            "output_root_reservation_sha256",
        ),
        "method_companion_group": ("metric_schema_sha256",),
    }[subject_type]
    return {
        "subject_type": subject_type,
        "subject_id": subject_id,
        "required_fingerprint_record_hashes": sorted(
            _synthetic_hash(f"fingerprint:{subject_id}:{dimension}")
            for dimension in required_dimensions
        ),
        "required_comparison_record_hashes": sorted(
            _synthetic_hash(f"comparison:{subject_id}:{dimension}")
            for dimension in required_dimensions
        ),
        "required_lineage_audit_hashes": (
            []
            if subject_type == "method_companion_group"
            else sorted(
                _synthetic_hash(f"lineage-audit:{subject_id}:{dimension}")
                for dimension in required_dimensions
            )
        ),
        "required_reuse_record_hashes": (
            [_synthetic_hash(f"reuse:{subject_id}")]
            if subject_type == "method_companion_group"
            else []
        ),
        "admission_status": admission_status,
        "refusal_reason_codes": ["overlap_hit"] if refused else [],
        "ledger_entry_ids": [f"ledger:{subject_id}"] if refused else [],
    }


def _overlap_report_fixture(*, method_refused: bool = False) -> JsonObject:
    case_status = "refused" if method_refused else "admitted"
    method_status = "refused" if method_refused else "admitted"
    per_case = {
        "case-a": _overlap_subject_status(
            "case_unit",
            "case-a",
            admission_status=case_status,
        )
    }
    per_method = {
        "method-a": _overlap_subject_status(
            "method_observation",
            "method-a",
            admission_status=method_status,
        )
    }
    per_group = {
        "metric-group-a": _overlap_subject_status(
            "method_companion_group",
            "metric-group-a",
            admission_status="admitted",
        )
    }
    subject_records = [*per_case.values(), *per_method.values(), *per_group.values()]
    report: JsonObject = {
        "schema_version": "ims-deadlock/g6b-input-overlap-report/v1",
        "report_id": "overlap-report-test",
        "bundle_id": _TEST_BUNDLE_ID,
        "input_overlap_authority_lock_sha256": _synthetic_hash("overlap-lock"),
        "sealed_bundle_manifest_sha256": _synthetic_hash("sealed-bundle"),
        "normalization_manifest_sha256": _synthetic_hash("normalization"),
        "declared_case_unit_ids": ["case-a"],
        "declared_method_observation_ids": ["method-a"],
        "declared_method_companion_group_ids": ["metric-group-a"],
        "new_fingerprint_record_hashes": {
            f"{record['subject_id']}:{index}": digest
            for record in subject_records
            for index, digest in enumerate(record["required_fingerprint_record_hashes"])
        },
        "retired_fingerprint_record_hashes": {
            "retired-lineage-a": _synthetic_hash("retired-lineage-a")
        },
        "comparison_record_hashes": {
            f"{record['subject_id']}:{index}": digest
            for record in subject_records
            for index, digest in enumerate(record["required_comparison_record_hashes"])
        },
        "semantic_lineage_audit_hashes": {
            f"{record['subject_id']}:{index}": digest
            for record in subject_records
            for index, digest in enumerate(record["required_lineage_audit_hashes"])
        },
        "metric_schema_reuse_record_hashes": {
            record["subject_id"]: record["required_reuse_record_hashes"][0]
            for record in subject_records
            if record["required_reuse_record_hashes"]
        },
        "per_case_status": per_case,
        "per_method_status": per_method,
        "per_companion_group_status": per_group,
        "unique_retired_lineage_count": 1,
        "inherited_record_count": 0,
        "duplicate_lineage_record_count": 0,
        "planned_case_count": 1,
        "passed_case_count": 0 if method_refused else 1,
        "refused_case_count": 1 if method_refused else 0,
        "pending_case_count": 0,
        "planned_method_count": 1,
        "passed_method_count": 0 if method_refused else 1,
        "refused_method_count": 1 if method_refused else 0,
        "pending_method_count": 0,
        "planned_companion_group_count": 1,
        "passed_companion_group_count": 1,
        "refused_companion_group_count": 0,
        "pending_companion_group_count": 0,
        "admission_policy_version": "ims-deadlock/g6b-overlap-admission/v1",
        "report_status": (
            "complete_with_refusals" if method_refused else "complete_all_admitted"
        ),
        "ledger_head_hash": _synthetic_hash("ledger-head"),
        "report_sha256": None,
    }
    report["report_sha256"] = finalized_self_hash(report, "report_sha256")
    return report


def _overlap_fingerprint_dimensions(report: JsonObject) -> dict[str, str]:
    dimensions_by_subject_type = {
        "case_unit": (
            "case_content_sha256",
            "state_snapshot_sha256",
            "route_signature_sha256",
            "parameter_tuple_sha256",
            "sealed_prediction_sha256",
        ),
        "method_observation": (
            "random_stream_manifest_sha256",
            "output_root_reservation_sha256",
        ),
        "method_companion_group": ("metric_schema_sha256",),
    }
    result: dict[str, str] = {}
    for field in (
        "per_case_status",
        "per_method_status",
        "per_companion_group_status",
    ):
        for status in report[field].values():
            for dimension in dimensions_by_subject_type[status["subject_type"]]:
                digest = _synthetic_hash(
                    f"fingerprint:{status['subject_id']}:{dimension}"
                )
                assert digest in status["required_fingerprint_record_hashes"]
                result[digest] = dimension
    return result


def _manifest_retention_fixture() -> JsonObject:
    return {
        "declared_object_ids": ["case-a", "method-a", "method-superseded"],
        "refused_object_ids": ["case-a"],
        "superseded_object_ids": ["method-superseded"],
        "later_manifest_object_ids": ["case-a", "method-a", "method-superseded"],
    }


def _preflight_source_fixture(import_line: str = "from pathlib import Path") -> str:
    return (
        f"{import_line}\n"
        "def validate_preflight(record):\n"
        "    return {'artifact_sha256': record['artifact_sha256']}"
    )


def _preflight_result_fixture() -> JsonObject:
    certificate_payload: JsonObject = {
        "S_T": ["state-a"],
        "unselected_closed_sccs": [],
        "reverse_basin": ["state-a"],
    }
    return {
        "schema_version": "ims-deadlock/g6b-target-certification-case-result/v1",
        "bundle_id": _TEST_BUNDLE_ID,
        "case_unit_id": "case-a",
        "input_identity_hashes": {
            field: _synthetic_hash(field)
            for field in (
                "case_content_sha256",
                "state_snapshot_sha256",
                "route_signature_sha256",
                "parameter_tuple_sha256",
                "sealed_prediction_sha256",
                "fingerprint_record_hashes_sha256",
            )
        },
        "runtime_lock_sha256": _synthetic_hash("preflight-runtime-lock"),
        "authorization_sha256": _synthetic_hash("preflight-authorization"),
        "result_status": "certified",
        "completeness_status": "complete_nontruncated_verified",
        "state_count": 4,
        "transition_count": 5,
        "selected_target_identity": {
            "target_schema_version": "target-v1",
            "selected_bad_classes": ["D_global", "D_local"],
            "success_class": "F",
            "exact_stopping_rule": "first-hit",
            "des_stopping_rule": "first-hit",
            "policy_analysis_class": "declared-policy",
            "declaration_sha256": _synthetic_hash("target-declaration"),
        },
        "state_space_hash": _synthetic_hash("state-space"),
        "partition_hash": _synthetic_hash("partition"),
        "rate_manifest_hash": _synthetic_hash("rate-manifest"),
        "positive_rate_graph_hash": _synthetic_hash("positive-rate-graph"),
        "policy_filter_hash": _synthetic_hash("policy-filter"),
        "absorption_domain_hash": _synthetic_hash("absorption-domain"),
        "estimand_id": "theta-local-first-hit-v1",
        "certificate_version": "ims-deadlock/g6b-target-certificate/v1",
        "certificate_status": "certified",
        "certificate_payload_or_null": certificate_payload,
        "certificate_payload_sha256_or_null": canonical_sha256_v2(certificate_payload),
        "refusal_reason_codes": [],
        "refusal_details": [],
        "command_transcript_sha256": _synthetic_hash("command-transcript"),
        "stderr_sha256": _synthetic_hash("stderr"),
        "exit_code": 0,
        "filesystem_before_manifest_sha256": _synthetic_hash("fs-before"),
        "filesystem_after_manifest_sha256": _synthetic_hash("fs-after"),
        "ledger_entry_ids": [],
    }


def _certified_record_fixture() -> JsonObject:
    return _preflight_result_fixture()


def _same_target_pair_fixture() -> JsonObject:
    record: JsonObject = {
        "schema_version": "ims-deadlock/g6b-same-target-lock/v1",
        "same_target_lock_id": "same-target-lock-test",
        "bundle_id": _TEST_BUNDLE_ID,
        "case_unit_id": "case-a",
        "method_companion_group_id": "metric-group-a",
        "exact_method_observation_id": "exact-method-a",
        "des_method_observation_id": "des-method-a",
        "selected_bad_classes": ["D_global", "D_local"],
        "success_class": "F",
        "target_schema_version": "target-v1",
        "estimand_schema_version": "estimand-v1",
        "state_space_hash": _synthetic_hash("same-target:state-space"),
        "partition_hash": _synthetic_hash("same-target:partition"),
        "rate_manifest_hash": _synthetic_hash("same-target:rate"),
        "positive_rate_graph_hash": _synthetic_hash("same-target:positive-rate"),
        "policy_filter_hash": _synthetic_hash("same-target:policy"),
        "absorption_domain_hash": _synthetic_hash("same-target:domain"),
        "certificate_artifact_hash": _synthetic_hash("same-target:certificate"),
        "estimand_id": "theta-local-first-hit-v1",
        "exact_stopping_rule_hash": _synthetic_hash("same-target:exact-stop"),
        "des_stopping_rule_hash": _synthetic_hash("same-target:des-stop"),
        "metric_schema_sha256": _synthetic_hash("same-target:metric"),
        "metric_reuse_authorization_hash": _synthetic_hash("same-target:reuse"),
        "exact_random_stream_manifest_sha256": _synthetic_hash("same-target:exact-rng"),
        "des_random_stream_manifest_sha256": _synthetic_hash("same-target:des-rng"),
        "exact_output_root_reservation_sha256": _synthetic_hash(
            "same-target:exact-root"
        ),
        "des_output_root_reservation_sha256": _synthetic_hash("same-target:des-root"),
        "lock_created_at_utc": "2030-01-01T00:00:00Z",
        "same_target_lock_sha256": None,
    }
    record["same_target_lock_sha256"] = finalized_self_hash(
        record,
        "same_target_lock_sha256",
    )
    return record


def _quantitative_scope_fixture() -> JsonObject:
    return {
        "case_unit_ids": ["case-a"],
        "method_observation_ids": ["des-method-a", "exact-method-a"],
        "certificate_hashes": {"case-a": _synthetic_hash("quant:certificate")},
        "same_target_lock_hashes": {"case-a": _synthetic_hash("quant:same-target")},
        "output_root_reservations": {
            "des-method-a": _synthetic_hash("quant:des-root"),
            "exact-method-a": _synthetic_hash("quant:exact-root"),
        },
    }


def _quantitative_authorization_fixture() -> JsonObject:
    scope = _quantitative_scope_fixture()
    command_manifest, _command_records = _valid_quantitative_command_manifest(scope)
    record: JsonObject = {
        "schema_version": "ims-deadlock/g6b-quantitative-authorization/v1",
        "authorization_id": "quant-auth-test",
        "capability": "quantitative_execution",
        "authorized": True,
        "bundle_id": _TEST_BUNDLE_ID,
        "authorized_scope": scope,
        "sealed_bundle_manifest_hash": _synthetic_hash("quant:sealed-bundle"),
        "target_certification_batch_manifest_hash": _synthetic_hash(
            "quant:preflight-batch"
        ),
        "runtime_lock_sha256": _synthetic_hash("quant:runtime-lock"),
        "allowed_command_manifest_hash": command_manifest["manifest_sha256"],
        "allowed_commands": sorted(command_manifest["command_record_hashes"].values()),
        "run_roles": ["primary"],
        "resource_budget": {
            "max_wall_clock_seconds": 60,
            "max_cpu_seconds": 60,
            "max_memory_bytes": 1024,
            "max_storage_bytes": 1024,
            "max_cases": 1,
            "max_concurrent_methods": 1,
            "max_retries": 0,
            "max_replicates_per_method": 1,
        },
        "output_root_policy": {
            "root_template": "artifacts/g6b/quantitative/synthetic",
            "reservation_required": True,
            "unmaterialized_before_launch": True,
            "one_writer_per_method_run": True,
            "fallback_path_prohibited": True,
            "absolute_path_prohibited": True,
            "tracked_inventory_required": True,
            "no_cross_method_writes": True,
        },
        "stop_conditions": ["all_authorized_methods_terminal-v1"],
        "review_artifact_hash": _synthetic_hash("quant:review"),
        "issued_at_utc": "2030-01-01T00:00:00Z",
        "invalidated_by_identity_drift": False,
        "authorization_sha256": None,
    }
    record["authorization_sha256"] = finalized_self_hash(
        record,
        "authorization_sha256",
    )
    return record


def _failure_evidence_hashes() -> list[str]:
    return [
        _synthetic_hash("failure-evidence"),
        _synthetic_hash("refusal-evidence"),
        _synthetic_hash("negative-control-evidence"),
        _synthetic_hash("boundary-evidence"),
    ]


def test_spec_17_3_12_schema_retired_inventory_fail_closed() -> None:
    schema = _load_retired_schema_definition()
    inventory = _retired_source_inventory()
    expected_hashes = _retired_source_hashes()
    authorization = valid_normalization_authorization()
    _validate_valid_normalization_authorization(authorization)
    validate_retired_authority_source_inventory(
        inventory,
        schema_definition=schema,
        expected_hashes=expected_hashes,
    )

    for field, value, code in (
        ("source_id", None, "missing_retired_authority"),
        ("declared_sha256", "stale", "invalid_hash_digest"),
        ("declared_sha256", "9" * 64, "retired_authority_hash_mismatch"),
        ("local_only", True, "missing_retired_authority"),
        ("verification_status", "unverified", "missing_retired_authority"),
    ):
        mutated = [dict(row) for row in inventory]
        if value is None:
            mutated[0].pop(field)
        else:
            mutated[0][field] = value
        with pytest.raises(SchemaContractError, match=code):
            validate_retired_authority_source_inventory(
                mutated,
                schema_definition=schema,
                expected_hashes=expected_hashes,
            )

    wrong_authority = deepcopy(inventory)
    wrong_authority[0]["authority_id"] = "G5_EXECUTION"
    with pytest.raises(SchemaContractError, match="missing_retired_authority"):
        validate_retired_authority_source_inventory(
            wrong_authority,
            schema_definition=schema,
            expected_hashes=expected_hashes,
        )


def test_spec_17_3_13_schema_inherited_g4_records_keep_one_lineage_and_count() -> None:
    origin = valid_fingerprint_record(dimension="case_content_sha256")
    inherited_g5 = deepcopy(origin)
    inherited_g5["record_id"] = "fingerprint-g5-inherited"
    inherited_g5["source_authority_id"] = "G5_EXECUTION"
    inherited_g5["dimension_status"] = "inherited_from_authority"
    inherited_g5["inherited_from_record_id_or_null"] = origin["record_id"]
    inherited_g5["record_provenance_sha256"] = None
    inherited_g5["record_provenance_sha256"] = finalized_self_hash(
        inherited_g5,
        "record_provenance_sha256",
    )
    inherited_g6r = deepcopy(inherited_g5)
    inherited_g6r["record_id"] = "fingerprint-g6r-inherited"
    inherited_g6r["source_authority_id"] = "G6_R_REPLAY_R3"
    inherited_g6r["inherited_from_record_id_or_null"] = inherited_g5["record_id"]
    inherited_g6r["record_provenance_sha256"] = None
    inherited_g6r["record_provenance_sha256"] = finalized_self_hash(
        inherited_g6r,
        "record_provenance_sha256",
    )

    contracts.validate_lineage_deduplication(
        [origin, inherited_g5, inherited_g6r],
        declared_unique_lineage_count=1,
    )
    inherited_g6r["lineage_id"] = f"sha256:{'9' * 64}"

    with pytest.raises(SchemaContractError, match="duplicate_lineage_miscount"):
        contracts.validate_lineage_deduplication(
            [origin, inherited_g5, inherited_g6r],
            declared_unique_lineage_count=1,
        )


def test_spec_17_3_14_schema_lineage_statuses_remain_distinct() -> None:
    metadata = _retired_lineage_metadata()
    validate_retired_authority_lineage_reproduction(metadata)
    metadata["dimension_statuses"].remove("unreconstructable_refuse")

    with pytest.raises(
        SchemaContractError, match="retired_projection_unreconstructable"
    ):
        validate_retired_authority_lineage_reproduction(metadata)

    metadata = _retired_lineage_metadata()
    metadata["origin_rows"][0]["origin"] = "not-an-authority"
    with pytest.raises(SchemaContractError, match="semantic_lineage_ambiguous"):
        validate_retired_authority_lineage_reproduction(metadata)

    metadata = _retired_lineage_metadata()
    metadata["origin_rows"][0]["lineage_id"] = "not-sha256"
    with pytest.raises(SchemaContractError, match="invalid_hash_digest"):
        validate_retired_authority_lineage_reproduction(metadata)


def test_spec_17_3_15_schema_normalizer_allowlist_guard() -> None:
    validate_normalizer_static_source(_normalizer_source())

    for source, code in (
        (
            _normalizer_source("import ims_deadlock.g4_protocol"),
            "capability_import_violation",
        ),
        (
            _normalizer_source() + "\n    __import__('ims_deadlock.g4_protocol')",
            "capability_import_violation",
        ),
        (
            _normalizer_source() + "\n    run_after_freeze()",
            "capability_call_violation",
        ),
        (
            _normalizer_source() + "\n    row['completion_probability'] = 1",
            "source_field_read_violation",
        ),
        (
            _normalizer_source() + "\n    open('outputs/result.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source("from pathlib import Path")
            + "\n    Path('outputs/result.json').write_text('bad')",
            "retired_normalizer_error",
        ),
        (_normalizer_source("import subprocess"), "capability_import_violation"),
        (_normalizer_source("import socket"), "capability_import_violation"),
        (
            _normalizer_source("import os") + "\nos.system('forbidden')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\n__builtins__['open']('outside.json', 'w')",
            "capability_call_violation",
        ),
    ):
        with pytest.raises(SchemaContractError, match=code):
            validate_normalizer_static_source(source)


@pytest.mark.parametrize(
    ("source", "code"),
    [
        (
            _normalizer_source() + "\nwriter = open\nwriter('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source("import os")
            + "\nrunner = os.system\nrunner('forbidden')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\nimp = __import__\nimp('subprocess')",
            "capability_import_violation",
        ),
        (
            _normalizer_source()
            + "\nwriter: object = open\nwriter('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source("import os")
            + "\nrunner = os.system\nalias = runner\nalias('forbidden')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\ndef _probe():\n    if (imp := __import__):\n"
            "        imp('subprocess')",
            "capability_import_violation",
        ),
        (
            _normalizer_source()
            + "\nwriter = __builtins__['open']\nwriter('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\ndef run(writer=open):\n"
            "    writer('outside.json', 'w')\n"
            "run()",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\ndef run(writer):\n"
            "    writer('outside.json', 'w')\n"
            "run(open)",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\nrun = open\nrun('outside.json', 'w')\nrun = len",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source("import functools")
            + "\nwriter = functools.partial(open, 'outside.json', 'w')\n"
            "writer()",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\nwriter = [open][0]\nwriter('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source()
            + "\nwriter = {'x': open}['x']\nwriter('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\ndef make():\n"
            "    return open\n"
            "writer = make()\n"
            "writer('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\ndef make():\n"
            "    return open\n"
            "def run(writer):\n"
            "    writer('outside.json', 'w')\n"
            "run(make())",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\nwriter = open if True else len\n"
            "writer('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\nclass C:\n"
            "    writer = open\n"
            "C.writer('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source("from ims_deadlock.engine import *") + "\nsimulate({})",
            "capability_import_violation",
        ),
        (
            _normalizer_source() + "\nopen.__call__('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source("import ims_deadlock.engine as eng")
            + "\neng.simulate.__call__({})",
            "capability_import_violation",
        ),
        (
            _normalizer_source("import builtins")
            + "\nbuiltins.__import__('subprocess')",
            "capability_import_violation",
        ),
        (
            _normalizer_source("import builtins") + "\nbuiltins.eval('1 + 1')",
            "capability_call_violation",
        ),
        (
            _normalizer_source("import builtins") + "\nbuiltins.exec('x = 1')",
            "capability_call_violation",
        ),
        (
            _normalizer_source("import builtins") + "\nbuiltins.getattr(object(), 'x')",
            "capability_call_violation",
        ),
        (
            _normalizer_source("import builtins")
            + "\nbuiltins.setattr(object(), 'x', 1)",
            "capability_call_violation",
        ),
        (
            _normalizer_source() + "\ndef make():\n"
            "    return open, len\n"
            "writer, other = make()\n"
            "writer('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\nfor writer in [open]:\n"
            "    writer('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source()
            + "\n[writer('outside.json', 'w') for writer in [open]]",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\nmatch open:\n"
            "    case writer:\n"
            "        writer('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\ndef make_cm():\n"
            "    return object()\n"
            "with make_cm() as writer:\n"
            "    writer('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source()
            + "\nwriter, other = ((open, len) if True else (len, len))\n"
            "writer('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\nfor writer in ([open] if True else [len]):\n"
            "    writer('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\nfirst, *middle, writer = (len, len, len, open)\n"
            "writer('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source("import os") + "\nclass Holder:\n"
            "    tool = os\n"
            "Holder.tool.system('forbidden')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source("import os") + "\nclass Holder:\n"
            "    pass\n"
            "holder = Holder()\n"
            "holder.tool = os\n"
            "holder.tool.system('forbidden')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source("import os") + "\nclass B:\n"
            "    tool = os\n"
            "A = B\n"
            "A.tool.system('forbidden')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\n*writer, = [open]\nwriter('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source()
            + "\nlist(map(lambda writer: writer('outside.json', 'w'), [len]))",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\ndef make():\n"
            "    return [open]\n"
            "items = make()\n"
            "for writer in items:\n"
            "    writer('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\ndef make():\n"
            "    return open, len\n"
            "pair = make()\n"
            "writer, other = pair\n"
            "writer('outside.json', 'w')",
            "retired_normalizer_error",
        ),
        (
            _normalizer_source() + "\ndef make():\n"
            "    return open, len\n"
            "pair = make()\n"
            "*writer, = pair\n"
            "writer('outside.json', 'w')",
            "retired_normalizer_error",
        ),
    ],
)
def test_normalizer_guard_rejects_local_callable_alias_bypasses(
    source: str,
    code: str,
) -> None:
    with pytest.raises(SchemaContractError, match=code):
        validate_normalizer_static_source(source)


def test_spec_17_3_37_schema_g4_manifest_freeze_sets_reconcile_exactly() -> None:
    rows = _g4_manifest_freeze_rows()
    freeze_hashes = {row["case_id"]: row["declared_sha256"] for row in rows}
    validate_g4_manifest_freeze_reconciliation(
        rows,
        included_case_ids=contracts.G4_MANIFEST_CASE_IDS,
        freeze_case_hashes=freeze_hashes,
    )

    for mutate, code in (
        (lambda value: value[:-1], "missing_retired_authority"),
        (
            lambda value: [
                *value,
                {
                    "case_id": "G4_UNDECLARED_EXTRA",
                    "repo_relative_posix_path": (
                        "cases/confirmation/g4/cases/G4_UNDECLARED_EXTRA.json"
                    ),
                    "declared_sha256": "0" * 64,
                },
            ],
            "unexpected_key",
        ),
        (lambda value: [*value, dict(value[0])], "set_array_duplicate"),
        (
            lambda value: [
                {**value[0], "case_id": contracts.G4_MANIFEST_CASE_IDS[1]},
                *value[1:],
            ],
            "retired_authority_hash_mismatch",
        ),
        (
            lambda value: [
                {
                    **value[0],
                    "repo_relative_posix_path": (
                        f"cases/other/{contracts.G4_MANIFEST_CASE_IDS[0]}.json"
                    ),
                },
                *value[1:],
            ],
            "repo_relative_path_violation",
        ),
    ):
        with pytest.raises(SchemaContractError, match=code):
            validate_g4_manifest_freeze_reconciliation(
                mutate(rows),
                included_case_ids=contracts.G4_MANIFEST_CASE_IDS,
                freeze_case_hashes=freeze_hashes,
            )


def test_spec_17_3_38_schema_subunits_reject_renamed_enclosing_ids() -> None:
    records = [
        _subunit_record("bidirectional_island_grid", "grid-parent", "cell-a"),
        _subunit_record("supplied_l30_inequalities", "l30-parent", "ineq-a"),
        _subunit_record(
            "adapted_candidate_monitor_cover",
            "b05-parent",
            "monitor-a",
        ),
    ]
    for record in records:
        contracts.validate_composite_subunit_record(record)

    renamed = deepcopy(records[0])
    renamed["parent_case_id"] = "renamed-grid-parent"
    with pytest.raises(SchemaContractError, match="semantic_lineage_ambiguous"):
        contracts.validate_composite_subunit_record(renamed)

    comparison = _valid_dimension_comparison_record(dimension="case_content_sha256")
    comparison["retired_lineage_id"] = "renamed-copy-parent"
    comparison["retired_comparison_projection_sha256_or_null"] = comparison[
        "new_comparison_projection_sha256_or_null"
    ]
    comparison = _with_rehashed_comparison(comparison)

    with pytest.raises(SchemaContractError, match="overlap_hit"):
        validate_dimension_comparison_record(
            comparison,
            semantic_lineage_audit_passed=True,
        )


def test_spec_18_schema_retired_sources_reproduce_without_outcome_reads() -> None:
    schema = _load_retired_schema_definition()
    inventory = _retired_source_inventory()
    selectors = _retired_selector_rows()
    metadata = _retired_lineage_metadata()

    assert "expected_source_inventory" in schema
    assert len(inventory) == 27
    assert all("{case_id}" not in row["repo_relative_posix_path"] for row in inventory)
    assert len(selectors) == 31
    expected_hashes = _retired_source_hashes()
    validate_retired_authority_source_inventory(
        inventory,
        schema_definition=schema,
        expected_hashes=expected_hashes,
    )
    validate_retired_authority_lineage_reproduction(metadata)
    validate_retired_authority_source_inventory(
        inventory,
        selector_rows=selectors,
        schema_definition=schema,
        expected_hashes=expected_hashes,
    )

    for row in selectors:
        source_path = row["source_path_pattern"]
        if "{case_id}" in source_path:
            source_path = source_path.replace(
                "{case_id}",
                contracts.G4_MANIFEST_CASE_IDS[0],
            )
        elif "{" in source_path:
            prefix, remainder = source_path.split("{", 1)
            alternatives, suffix = remainder.split("}", 1)
            source_path = f"{prefix}{alternatives.split(',', 1)[0]}{suffix}"
        if row["selector_kind"] == "raw_bytes_only":
            pointer = None
        else:
            pointer = row["selectors"][0].replace("*", "0")
        validate_source_pointer_use(
            source_path,
            pointer,
            row["allowed_use"],
            selectors,
        )

    g4_case_row = next(
        row
        for row in selectors
        if row["source_path_pattern"].endswith("cases/{case_id}.json")
        and row["allowed_use"] == "lineage_link"
    )
    validate_source_pointer_use(
        "cases/confirmation/g4/cases/G4_IMS_PARAMETER_GRID.json",
        g4_case_row["selectors"][0],
        "lineage_link",
        selectors,
    )
    g6_raw_row = next(
        row
        for row in selectors
        if row["source_path_pattern"].startswith("evidence/g6/{")
    )
    validate_source_pointer_use(
        "evidence/g6/G6_HISTORICAL_REPLAY_R3_REPORT.json",
        None,
        g6_raw_row["allowed_use"],
        selectors,
    )

    compressed_inventory = deepcopy(inventory)
    compressed_inventory[2]["repo_relative_posix_path"] = (
        "cases/confirmation/g4/cases/{case_id}.json"
    )
    compressed_hashes = {
        row["repo_relative_posix_path"]: row["declared_sha256"]
        for row in compressed_inventory
    }
    with pytest.raises(
        SchemaContractError,
        match="retired_authority_hash_mismatch|missing_retired_authority",
    ):
        validate_retired_authority_source_inventory(
            compressed_inventory,
            schema_definition=schema,
            expected_hashes=compressed_hashes,
        )

    for status in ("unreconstructable", "normalizer_error"):
        comparison = _valid_dimension_comparison_record(
            dimension="case_content_sha256",
            status=status,
        )
        comparison["refusal_reason_code_or_null"] = (
            "retired_projection_unreconstructable"
            if status == "unreconstructable"
            else "retired_normalizer_error"
        )
        comparison = _with_rehashed_comparison(comparison)
        validate_dimension_comparison_record(comparison)
        comparison["comparison_status"] = "pass_distinct"
        comparison["refusal_reason_code_or_null"] = None
        comparison = _with_rehashed_comparison(comparison)
        with pytest.raises(SchemaContractError, match="semantic_lineage_ambiguous"):
            validate_dimension_comparison_record(comparison)


def test_spec_17_3_21_schema_method_refusal_propagates_to_case() -> None:
    report = _overlap_report_fixture(method_refused=True)
    dimensions = _overlap_fingerprint_dimensions(report)
    contracts.validate_input_overlap_report(
        report,
        method_owner_case_ids={"method-a": "case-a"},
        fingerprint_dimensions_by_hash=dimensions,
    )
    report["per_case_status"]["case-a"]["admission_status"] = "admitted"
    report["per_case_status"]["case-a"]["refusal_reason_codes"] = []
    report["per_case_status"]["case-a"]["ledger_entry_ids"] = []
    report["passed_case_count"] = 1
    report["refused_case_count"] = 0
    report = _with_rehashed(report, "report_sha256")

    with pytest.raises(SchemaContractError, match="method_refusal_case_mismatch"):
        contracts.validate_input_overlap_report(
            report,
            method_owner_case_ids={"method-a": "case-a"},
            fingerprint_dimensions_by_hash=dimensions,
        )


def test_spec_17_3_22_schema_overlap_report_covers_every_object_and_dimension() -> None:
    report = _overlap_report_fixture()
    dimensions = _overlap_fingerprint_dimensions(report)
    contracts.validate_input_overlap_report(
        report,
        method_owner_case_ids={"method-a": "case-a"},
        fingerprint_dimensions_by_hash=dimensions,
    )
    dimensions.pop(
        next(
            digest
            for digest, value in dimensions.items()
            if value == FINGERPRINT_DIMENSIONS[-1]
        )
    )

    with pytest.raises(SchemaContractError, match="overlap_dimension_coverage"):
        contracts.validate_input_overlap_report(
            report,
            method_owner_case_ids={"method-a": "case-a"},
            fingerprint_dimensions_by_hash=dimensions,
        )


def test_overlap_report_rejects_non_sha_hash_map_values() -> None:
    report = _overlap_report_fixture()
    dimensions = _overlap_fingerprint_dimensions(report)
    report["retired_fingerprint_record_hashes"] = {"retired-lineage-a": "not-a-sha"}
    report = _with_rehashed(report, "report_sha256")
    with pytest.raises(SchemaContractError, match="invalid_hash_digest"):
        contracts.validate_input_overlap_report(
            report,
            method_owner_case_ids={"method-a": "case-a"},
            fingerprint_dimensions_by_hash=dimensions,
        )


def test_overlap_dimensions_cannot_be_reassigned_to_wrong_subject_types() -> None:
    report = _overlap_report_fixture()
    dimensions = _overlap_fingerprint_dimensions(report)
    case_digest = report["per_case_status"]["case-a"][
        "required_fingerprint_record_hashes"
    ][0]
    method_digest = report["per_method_status"]["method-a"][
        "required_fingerprint_record_hashes"
    ][0]
    dimensions[case_digest], dimensions[method_digest] = (
        dimensions[method_digest],
        dimensions[case_digest],
    )
    with pytest.raises(SchemaContractError, match="overlap_dimension_coverage"):
        contracts.validate_input_overlap_report(
            report,
            method_owner_case_ids={"method-a": "case-a"},
            fingerprint_dimensions_by_hash=dimensions,
        )


def test_spec_17_3_23_schema_refused_and_superseded_objects_remain_in_manifests() -> (
    None
):
    manifest = _manifest_retention_fixture()
    contracts.validate_manifest_retention(manifest)
    manifest["later_manifest_object_ids"].remove("method-superseded")

    with pytest.raises(SchemaContractError, match="manifest_retention_gap"):
        contracts.validate_manifest_retention(manifest)


def test_spec_17_3_24_schema_forbidden_keys_reject_recursively() -> None:
    payload = _preflight_result_fixture()
    contracts.validate_preflight_result_payload(payload)
    payload["certificate_payload_or_null"]["nested"] = {
        "audit": [{"science_summary": "forbidden"}]
    }

    with pytest.raises(SchemaContractError, match="outcome_leakage"):
        contracts.validate_preflight_result_payload(payload)


def test_spec_17_3_27_schema_preflight_allowlist_guard() -> None:
    contracts.validate_preflight_static_source(_preflight_source_fixture())

    for source, code in (
        (
            (
                "from ims_deadlock.engine import simulate as run\n"
                "def validate_preflight(record):\n"
                "    return run(record)"
            ),
            "capability_call_violation",
        ),
        (
            (
                "from ims_deadlock.g6b_target_artifacts import write_unlisted_record\n"
                "def validate_preflight(record):\n"
                "    return write_unlisted_record(record)"
            ),
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture("import ims_deadlock.g5_scoring"),
            "capability_import_violation",
        ),
        (
            _preflight_source_fixture("import subprocess"),
            "capability_import_violation",
        ),
        (
            _preflight_source_fixture() + "\nopen('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\n__builtins__['__import__']('subprocess')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\n__builtins__['open']('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            (
                "from pathlib import Path\n"
                "def validate_preflight(record):\n"
                "    return Path('outside.json').open('w')"
            ),
            "capability_call_violation",
        ),
        (
            (
                "import io\n"
                "def validate_preflight(record):\n"
                "    return io.open('outside.json', 'w')"
            ),
            "capability_call_violation",
        ),
    ):
        with pytest.raises(SchemaContractError, match=code):
            contracts.validate_preflight_static_source(source)


@pytest.mark.parametrize(
    ("source", "code"),
    [
        (
            _preflight_source_fixture()
            + "\nwriter = open\nwriter('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture("import os")
            + "\nrunner = os.system\nrunner('forbidden')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\nimp = __import__\nimp('subprocess')",
            "capability_import_violation",
        ),
        (
            _preflight_source_fixture()
            + "\nwriter: object = open\nwriter('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture("import os")
            + "\nrunner = os.system\nalias = runner\nalias('forbidden')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture()
            + "\ndef _probe():\n    if (imp := __import__):\n"
            "        imp('subprocess')",
            "capability_import_violation",
        ),
        (
            _preflight_source_fixture()
            + "\nwriter = __builtins__['open']\nwriter('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\ndef run(writer=open):\n"
            "    writer('outside.json', 'w')\n"
            "run()",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\ndef run(writer):\n"
            "    writer('outside.json', 'w')\n"
            "run(open)",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture("import ims_deadlock.engine as eng")
            + "\nrun = eng.simulate\n"
            "run({})\n"
            "run = len",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture("import functools")
            + "\nwriter = functools.partial(open, 'outside.json', 'w')\n"
            "writer()",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture()
            + "\nwriter = [open][0]\nwriter('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture()
            + "\nwriter = {'x': open}['x']\nwriter('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\ndef make():\n"
            "    return open\n"
            "writer = make()\n"
            "writer('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\ndef make():\n"
            "    return open\n"
            "def run(writer):\n"
            "    writer('outside.json', 'w')\n"
            "run(make())",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\nwriter = open if True else len\n"
            "writer('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\nclass C:\n"
            "    writer = open\n"
            "C.writer('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture("from ims_deadlock.engine import *")
            + "\nsimulate({})",
            "capability_import_violation",
        ),
        (
            _preflight_source_fixture() + "\nopen.__call__('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture("import ims_deadlock.engine as eng")
            + "\neng.simulate.__call__({})",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture("import builtins")
            + "\nbuiltins.__import__('subprocess')",
            "capability_import_violation",
        ),
        (
            _preflight_source_fixture("import builtins") + "\nbuiltins.eval('1 + 1')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture("import builtins") + "\nbuiltins.exec('x = 1')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture("import builtins")
            + "\nbuiltins.getattr(object(), 'x')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture("import builtins")
            + "\nbuiltins.setattr(object(), 'x', 1)",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\ndef make():\n"
            "    return open, len\n"
            "writer, other = make()\n"
            "writer('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\nfor writer in [open]:\n"
            "    writer('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture()
            + "\n[writer('outside.json', 'w') for writer in [open]]",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\nmatch open:\n"
            "    case writer:\n"
            "        writer('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\ndef make_cm():\n"
            "    return object()\n"
            "with make_cm() as writer:\n"
            "    writer('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture()
            + "\nwriter, other = ((open, len) if True else (len, len))\n"
            "writer('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture()
            + "\nfor writer in ([open] if True else [len]):\n"
            "    writer('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture()
            + "\nfirst, *middle, writer = (len, len, len, open)\n"
            "writer('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture("import os") + "\nclass Holder:\n"
            "    tool = os\n"
            "Holder.tool.system('forbidden')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture("import os") + "\nclass Holder:\n"
            "    pass\n"
            "holder = Holder()\n"
            "holder.tool = os\n"
            "holder.tool.system('forbidden')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture("import os") + "\nclass B:\n"
            "    tool = os\n"
            "A = B\n"
            "A.tool.system('forbidden')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture("import ims_deadlock.engine as eng")
            + "\n*rest, = [eng.simulate]\n"
            "list(map(lambda f: f({}), rest))",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture()
            + "\nlist(map(lambda writer: writer('outside.json', 'w'), [len]))",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\ndef make():\n"
            "    return [open]\n"
            "items = make()\n"
            "for writer in items:\n"
            "    writer('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\ndef make():\n"
            "    return open, len\n"
            "pair = make()\n"
            "writer, other = pair\n"
            "writer('outside.json', 'w')",
            "capability_call_violation",
        ),
        (
            _preflight_source_fixture() + "\ndef make():\n"
            "    return open, len\n"
            "pair = make()\n"
            "*writer, = pair\n"
            "writer('outside.json', 'w')",
            "capability_call_violation",
        ),
    ],
)
def test_preflight_guard_rejects_local_callable_alias_bypasses(
    source: str,
    code: str,
) -> None:
    with pytest.raises(SchemaContractError, match=code):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_allows_safe_record_get_method_call() -> None:
    source = (
        "def normalize(record):\n"
        "    value = record.get('source_sha256', '')\n"
        "    return {'source_sha256': value}\n"
    )
    validate_normalizer_static_source(source)


def test_preflight_guard_allows_safe_record_get_method_call() -> None:
    source = (
        "def validate_preflight(record):\n"
        "    value = record.get('artifact_sha256', '')\n"
        "    return {'artifact_sha256': value}\n"
    )
    contracts.validate_preflight_static_source(source)


def test_normalizer_guard_allows_safe_intermediate_data_call_argument() -> None:
    source = (
        "from hashlib import sha256\n"
        "def normalize(source_bytes):\n"
        "    digest_input = source_bytes.strip()\n"
        "    return {'source_sha256': sha256(digest_input).hexdigest()}\n"
    )
    validate_normalizer_static_source(source)


def test_preflight_guard_allows_safe_intermediate_data_call_argument() -> None:
    source = (
        "def validate_preflight(record):\n"
        "    copied = record.copy()\n"
        "    field_count = len(copied)\n"
        "    return {'artifact_sha256': record['artifact_sha256'], 'n': field_count}\n"
    )
    contracts.validate_preflight_static_source(source)


def test_normalizer_guard_allows_safe_parameter_data_method_extraction() -> None:
    source = (
        "def normalize(record):\n"
        "    getter = record.get\n"
        "    return {'source_sha256': getter('source_sha256', '')}\n"
    )
    validate_normalizer_static_source(source)


def test_preflight_guard_allows_safe_parameter_data_method_extraction() -> None:
    source = (
        "def validate_preflight(record):\n"
        "    getter = record.get\n"
        "    return {'artifact_sha256': getter('artifact_sha256', '')}\n"
    )
    contracts.validate_preflight_static_source(source)


def test_normalizer_guard_allows_safe_path_call_result_methods() -> None:
    source = (
        "from pathlib import Path\n"
        "def normalize(record):\n"
        "    path = Path(record['path'])\n"
        "    text = path.read_text(encoding='utf-8') if path.exists() else ''\n"
        "    return {'source_sha256': text}\n"
    )
    validate_normalizer_static_source(source)


def test_preflight_guard_allows_safe_path_call_result_methods() -> None:
    source = (
        "from pathlib import Path\n"
        "def validate_preflight(record):\n"
        "    path = Path(record['path'])\n"
        "    text = path.read_text(encoding='utf-8') if path.exists() else ''\n"
        "    return {'artifact_sha256': text}\n"
    )
    contracts.validate_preflight_static_source(source)


def test_normalizer_guard_allows_safe_hash_call_result_method() -> None:
    source = (
        "from hashlib import sha256\n"
        "def normalize(source_bytes):\n"
        "    digest = sha256(source_bytes)\n"
        "    return {'source_sha256': digest.hexdigest()}\n"
    )
    validate_normalizer_static_source(source)


def test_preflight_guard_allows_safe_hash_call_result_method() -> None:
    source = (
        "from hashlib import sha256\n"
        "def validate_preflight(record):\n"
        "    digest = sha256(b'artifact')\n"
        "    return {'artifact_sha256': digest.hexdigest()}\n"
    )
    contracts.validate_preflight_static_source(source)


def test_normalizer_guard_allows_safe_json_call_result_method() -> None:
    source = (
        "import json\n"
        "def normalize(source_text):\n"
        "    document = json.loads(source_text)\n"
        "    return {'source_sha256': document.get('source_sha256', '')}\n"
    )
    validate_normalizer_static_source(source)


def test_preflight_guard_allows_safe_json_call_result_method() -> None:
    source = (
        "import json\n"
        "def validate_preflight(record):\n"
        "    document = json.loads(record['payload'])\n"
        "    return {'artifact_sha256': document.get('artifact_sha256', '')}\n"
    )
    contracts.validate_preflight_static_source(source)


def test_normalizer_guard_allows_safe_record_copy_call_result_method() -> None:
    source = (
        "def normalize(record):\n"
        "    copied = record.copy()\n"
        "    return {'source_sha256': copied.get('source_sha256', '')}\n"
    )
    validate_normalizer_static_source(source)


def test_preflight_guard_allows_safe_record_copy_call_result_method() -> None:
    source = (
        "def validate_preflight(record):\n"
        "    copied = record.copy()\n"
        "    return {'artifact_sha256': copied.get('artifact_sha256', '')}\n"
    )
    contracts.validate_preflight_static_source(source)


@pytest.mark.parametrize(
    "suffix",
    [
        "path.write_text('forbidden')",
        "path.open('w')",
    ],
)
def test_normalizer_guard_rejects_path_call_result_writes(suffix: str) -> None:
    source = (
        "from pathlib import Path\n"
        "def normalize(record):\n"
        "    path = Path(record['path'])\n"
        f"    {suffix}\n"
        "    return {'source_sha256': ''}\n"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


@pytest.mark.parametrize(
    "suffix",
    [
        "path.write_text('forbidden')",
        "path.open('w')",
    ],
)
def test_preflight_guard_rejects_path_call_result_writes(suffix: str) -> None:
    source = (
        "from pathlib import Path\n"
        "def validate_preflight(record):\n"
        "    path = Path(record['path'])\n"
        f"    {suffix}\n"
        "    return {'artifact_sha256': record['artifact_sha256']}\n"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


@pytest.mark.parametrize(
    "source",
    [
        (
            "from hashlib import sha256\n"
            "def normalize(source_bytes):\n"
            "    digest = sha256(source_bytes)\n"
            "    digest.update(b'x')\n"
            "    return {'source_sha256': ''}\n"
        ),
        (
            "import json\n"
            "def normalize(source_text):\n"
            "    document = json.loads(source_text)\n"
            "    document.items()\n"
            "    return {'source_sha256': ''}\n"
        ),
        (
            "def normalize(record):\n"
            "    copied = record.copy()\n"
            "    copied.items()\n"
            "    return {'source_sha256': ''}\n"
        ),
    ],
)
def test_normalizer_guard_rejects_unlisted_safe_call_result_methods(
    source: str,
) -> None:
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


@pytest.mark.parametrize(
    "source",
    [
        (
            "from hashlib import sha256\n"
            "def validate_preflight(record):\n"
            "    digest = sha256(b'artifact')\n"
            "    digest.update(b'x')\n"
            "    return {'artifact_sha256': ''}\n"
        ),
        (
            "import json\n"
            "def validate_preflight(record):\n"
            "    document = json.loads(record['payload'])\n"
            "    document.items()\n"
            "    return {'artifact_sha256': ''}\n"
        ),
        (
            "def validate_preflight(record):\n"
            "    copied = record.copy()\n"
            "    copied.items()\n"
            "    return {'artifact_sha256': ''}\n"
        ),
    ],
)
def test_preflight_guard_rejects_unlisted_safe_call_result_methods(
    source: str,
) -> None:
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


@pytest.mark.parametrize(
    "source",
    [
        (
            "from hashlib import sha256\n"
            "def normalize(source_bytes):\n"
            "    sha256(source_bytes).update(b'x')\n"
            "    return {'source_sha256': ''}\n"
        ),
        (
            "import json\n"
            "def normalize(source_text):\n"
            "    json.loads(source_text).items()\n"
            "    return {'source_sha256': ''}\n"
        ),
        (
            "def normalize(record):\n"
            "    record.copy().items()\n"
            "    return {'source_sha256': ''}\n"
        ),
    ],
)
def test_normalizer_guard_rejects_direct_unlisted_safe_call_result_methods(
    source: str,
) -> None:
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


@pytest.mark.parametrize(
    "source",
    [
        (
            "from hashlib import sha256\n"
            "def validate_preflight(record):\n"
            "    sha256(b'artifact').update(b'x')\n"
            "    return {'artifact_sha256': ''}\n"
        ),
        (
            "import json\n"
            "def validate_preflight(record):\n"
            "    json.loads(record['payload']).items()\n"
            "    return {'artifact_sha256': ''}\n"
        ),
        (
            "def validate_preflight(record):\n"
            "    record.copy().items()\n"
            "    return {'artifact_sha256': ''}\n"
        ),
    ],
)
def test_preflight_guard_rejects_direct_unlisted_safe_call_result_methods(
    source: str,
) -> None:
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_allows_direct_listed_safe_call_result_methods() -> None:
    source = (
        "from hashlib import sha256\n"
        "from pathlib import Path\n"
        "import json\n"
        "def normalize(record):\n"
        "    text = Path(record['path']).read_text() "
        "if Path(record['path']).exists() else ''\n"
        '    value = json.loads(\'{"source_sha256": "abc"}\')'
        ".get('source_sha256', '')\n"
        "    digest = sha256(b'artifact').hexdigest()\n"
        "    return {'source_sha256': digest or value or text}\n"
    )
    validate_normalizer_static_source(source)


def test_normalizer_guard_allows_exact_retired_normalizer_surface() -> None:
    source = (
        "from pathlib import Path\n"
        "from ims_deadlock.g6b_schema_contracts import SchemaContractError\n"
        "from ims_deadlock.g6b_schema_contracts import "
        "validate_normalization_authorization\n"
        "from ims_deadlock.g6b_schema_contracts import validate_authority_lock_record\n"
        "from ims_deadlock.g6b_schema_contracts import "
        "validate_authority_source_record\n"
        "from ims_deadlock.g6b_schema_contracts import validate_fingerprint_record\n"
        "from ims_deadlock.g6b_schema_contracts import "
        "validate_normalization_manifest\n"
        "def write_normalization_authorization(path, payload):\n"
        "    target = Path(path).resolve()\n"
        "    if target.exists() and target.is_file() and not target.is_symlink():\n"
        "        target.read_bytes()\n"
        "        target.read_text()\n"
        "        target.relative_to(Path('governance').resolve())\n"
        "    target.mkdir()\n"
        "    validate_normalization_authorization(payload)\n"
        "    target.write_bytes(b'{}')\n"
        "    target.replace(Path(path))\n"
        "def write_authority_lock_record(path, payload):\n"
        "    read_authority_bytes()\n"
        "    parse_allowed_json_pointers()\n"
        "    verify_source_hashes()\n"
        "    parse_historical_decimal_exactly()\n"
        "    apply_static_input_projection()\n"
        "    canonicalize_projection_v2()\n"
        "    compute_sha256()\n"
        "    write_normalization_authorization()\n"
        "    write_authority_lock_record()\n"
        "    write_authority_source_record()\n"
        "    write_fingerprint_record()\n"
        "    write_normalization_manifest()\n"
        "    validate_authority_lock_record(payload)\n"
        "    Path(path).write_bytes(b'{}')\n"
        "def write_authority_source_record(path, payload):\n"
        "    validate_authority_source_record(payload)\n"
        "    Path(path).write_bytes(b'{}')\n"
        "def write_fingerprint_record(path, payload):\n"
        "    try:\n"
        "        validate_fingerprint_record(payload, None)\n"
        "    except SchemaContractError:\n"
        "        raise\n"
        "    Path(path).write_bytes(b'{}')\n"
        "def write_normalization_manifest(path, payload):\n"
        "    validate_normalization_manifest(payload)\n"
        "    Path(path).write_bytes(b'{}')\n"
    )
    validate_normalizer_static_source(source)


@pytest.mark.parametrize(
    "body",
    [
        "def normalize(path):\n    Path(path).write_bytes(b'bad')\n",
        (
            "def write_fingerprint_record(path):\n"
            "    def nested():\n"
            "        Path(path).write_bytes(b'bad')\n"
            "    nested()\n"
        ),
        (
            "def write_fingerprint_record(path):\n"
            "    writer = Path(path).write_bytes\n"
            "    writer(b'bad')\n"
        ),
    ],
)
def test_normalizer_guard_rejects_writer_outside_top_level_writer_boundary(
    body: str,
) -> None:
    source = "from pathlib import Path\n" + body
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


@pytest.mark.parametrize("method", ["iterdir", "glob", "unlink", "write_text", "open"])
def test_normalizer_guard_rejects_unlisted_path_methods(method: str) -> None:
    source = (
        f"from pathlib import Path\ndef normalize(path):\n    Path(path).{method}()\n"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_normalizer_guard_rejects_governance_import_and_unlisted_schema_call() -> None:
    for source, code in (
        ("import ims_deadlock.g6b_governance\n", "capability_import_violation"),
        (
            (
                "from ims_deadlock.g6b_schema_contracts import SchemaContractError\n"
                "def normalize(record):\n"
                "    SchemaContractError('bad')\n"
            ),
            "retired_normalizer_error",
        ),
        (
            (
                "from ims_deadlock.g6b_schema_contracts import validate_exact_keys\n"
                "def normalize(record):\n"
                "    validate_exact_keys(record, set(), label='x')\n"
            ),
            "retired_normalizer_error",
        ),
    ):
        with pytest.raises(SchemaContractError, match=code):
            validate_normalizer_static_source(source)


def test_normalizer_guard_rejects_retired_operation_order_drift() -> None:
    source = (
        "def normalize():\n"
        "    read_authority_bytes()\n"
        "    parse_allowed_json_pointers()\n"
        "    parse_historical_decimal_exactly()\n"
        "    verify_source_hashes()\n"
        "    apply_static_input_projection()\n"
        "    canonicalize_projection_v2()\n"
        "    compute_sha256()\n"
        "    write_normalization_authorization()\n"
        "    write_authority_lock_record()\n"
        "    write_authority_source_record()\n"
        "    write_fingerprint_record()\n"
        "    write_normalization_manifest()\n"
    )
    with pytest.raises(SchemaContractError, match="operation_contract_drift"):
        validate_normalizer_static_source(source)


def test_normalization_allowed_project_imports_remain_exact_corrigendum_tuple() -> None:
    assert contracts.NORMALIZATION_ALLOWED_PROJECT_IMPORTS == (
        "ims_deadlock.g6b_retired_normalizer",
        "ims_deadlock.g6b_canonical_json",
        "ims_deadlock.g6b_schema_contracts",
        "ims_deadlock.g6b_governance",
    )


def test_schema_contracts_import_closure_only_uses_canonical_json() -> None:
    source_path = Path(contracts.__file__).resolve()
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    project_imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            project_imports.update(
                alias.name
                for alias in node.names
                if alias.name.startswith("ims_deadlock")
            )
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            if node.module == "ims_deadlock":
                project_imports.update(
                    f"ims_deadlock.{alias.name}"
                    for alias in node.names
                    if alias.name != "*"
                )
            elif node.module.startswith("ims_deadlock"):
                project_imports.add(node.module)
    assert project_imports == {"ims_deadlock.g6b_canonical_json"}


def test_preflight_guard_allows_direct_listed_safe_call_result_methods() -> None:
    source = (
        "from hashlib import sha256\n"
        "from pathlib import Path\n"
        "import json\n"
        "def validate_preflight(record):\n"
        "    text = Path(record['path']).read_text() "
        "if Path(record['path']).exists() else ''\n"
        "    value = json.loads(record['payload']).get('artifact_sha256', '')\n"
        "    copied = record.copy().get('artifact_sha256', '')\n"
        "    digest = sha256(b'artifact').hexdigest()\n"
        "    return {'artifact_sha256': digest or value or copied or text}\n"
    )
    contracts.validate_preflight_static_source(source)


@pytest.mark.parametrize("member", ["system", "popen", "spawnv"])
def test_normalizer_guard_rejects_user_reserved_safe_sentinel_members(
    member: str,
) -> None:
    args = "(0, 'forbidden', [])" if member == "spawnv" else "('forbidden')"
    source = (
        "def normalize(record):\n"
        f"    __g6b_safe_path_object__.{member}{args}\n"
        "    return {'source_sha256': ''}\n"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


@pytest.mark.parametrize("member", ["system", "popen", "spawnv"])
def test_preflight_guard_rejects_user_reserved_safe_sentinel_members(
    member: str,
) -> None:
    args = "(0, 'forbidden', [])" if member == "spawnv" else "('forbidden')"
    source = (
        "def validate_preflight(record):\n"
        f"    __g6b_safe_path_object__.{member}{args}\n"
        "    return {'artifact_sha256': record['artifact_sha256']}\n"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_user_reserved_safe_sentinel_alias() -> None:
    source = (
        "def normalize(record):\n"
        "    forged = __g6b_safe_path_object__\n"
        "    forged.system('forbidden')\n"
        "    return {'source_sha256': ''}\n"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_user_reserved_safe_sentinel_alias() -> None:
    source = (
        "def validate_preflight(record):\n"
        "    forged = __g6b_safe_path_object__\n"
        "    forged.system('forbidden')\n"
        "    return {'artifact_sha256': record['artifact_sha256']}\n"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_parameter_member_higher_order_dispatch() -> None:
    source = (
        _normalizer_source("import os")
        + "\nlist(map(lambda runner: runner.system('forbidden'), [os]))"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_parameter_member_higher_order_dispatch() -> None:
    source = (
        _preflight_source_fixture("import os")
        + "\nlist(map(lambda runner: runner.system('forbidden'), [os]))"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_parameter_member_extraction() -> None:
    source = (
        _normalizer_source("import os") + "\ndef run(runner):\n"
        "    method = runner.system\n"
        "    method('forbidden')\n"
        "run(os)"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_parameter_member_extraction() -> None:
    source = (
        _preflight_source_fixture("import os") + "\ndef run(runner):\n"
        "    method = runner.system\n"
        "    method('forbidden')\n"
        "run(os)"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_parameter_member_extraction_via_function_alias() -> (
    None
):
    source = (
        _normalizer_source("import os") + "\ndef run(runner):\n"
        "    method = runner.system\n"
        "    method('forbidden')\n"
        "alias = run\n"
        "list(map(alias, [os]))"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_parameter_member_extraction_via_function_alias() -> (
    None
):
    source = (
        _preflight_source_fixture("import os") + "\ndef run(runner):\n"
        "    method = runner.system\n"
        "    method('forbidden')\n"
        "alias = run\n"
        "list(map(alias, [os]))"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_call_returned_module_member_dispatch() -> None:
    source = (
        _normalizer_source("import os") + "\ndef make():\n"
        "    return os\n"
        "make().system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_call_returned_module_member_dispatch() -> None:
    source = (
        _preflight_source_fixture("import os") + "\ndef make():\n"
        "    return os\n"
        "make().system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_call_returned_module_member_extraction() -> None:
    source = (
        _normalizer_source("import os") + "\ndef make():\n"
        "    return os\n"
        "fn = make().system\n"
        "fn('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_call_returned_module_member_extraction() -> None:
    source = (
        _preflight_source_fixture("import os") + "\ndef make():\n"
        "    return os\n"
        "fn = make().system\n"
        "fn('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_call_returned_sensitive_callable() -> None:
    source = (
        _normalizer_source("import os") + "\ndef make():\n"
        "    return os.system\n"
        "fn = make()\n"
        "fn('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_call_returned_sensitive_callable() -> None:
    source = (
        _preflight_source_fixture("import os") + "\ndef make():\n"
        "    return os.system\n"
        "fn = make()\n"
        "fn('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_transitive_call_returned_module_member_dispatch() -> (
    None
):
    source = (
        _normalizer_source("import os") + "\ndef make():\n"
        "    return os\n"
        "def relay():\n"
        "    return make()\n"
        "relay().system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_transitive_call_returned_module_member_dispatch() -> (
    None
):
    source = (
        _preflight_source_fixture("import os") + "\ndef make():\n"
        "    return os\n"
        "def relay():\n"
        "    return make()\n"
        "relay().system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_transitive_call_returned_member_extraction() -> None:
    source = (
        _normalizer_source("import os") + "\ndef make():\n"
        "    return os\n"
        "def relay():\n"
        "    return make()\n"
        "fn = relay().system\n"
        "fn('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_transitive_call_returned_member_extraction() -> None:
    source = (
        _preflight_source_fixture("import os") + "\ndef make():\n"
        "    return os\n"
        "def relay():\n"
        "    return make()\n"
        "fn = relay().system\n"
        "fn('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_call_returned_module_unknown_member_chain() -> None:
    source = (
        _normalizer_source("import os") + "\ndef make():\n"
        "    return os\n"
        "make().path.system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_call_returned_module_unknown_member_chain() -> None:
    source = (
        _preflight_source_fixture("import os") + "\ndef make():\n"
        "    return os\n"
        "make().path.system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_return_call_cycle_member_dispatch() -> None:
    source = (
        _normalizer_source() + "\ndef make():\n"
        "    return relay()\n"
        "def relay():\n"
        "    return make()\n"
        "relay().system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_return_call_cycle_member_dispatch() -> None:
    source = (
        _preflight_source_fixture() + "\ndef make():\n"
        "    return relay()\n"
        "def relay():\n"
        "    return make()\n"
        "relay().system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_return_call_cycle_member_extraction() -> None:
    source = (
        _normalizer_source() + "\ndef make():\n"
        "    return relay()\n"
        "def relay():\n"
        "    return make()\n"
        "fn = relay().system\n"
        "fn('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_return_call_cycle_member_extraction() -> None:
    source = (
        _preflight_source_fixture() + "\ndef make():\n"
        "    return relay()\n"
        "def relay():\n"
        "    return make()\n"
        "fn = relay().system\n"
        "fn('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_conditional_return_call_cycle() -> None:
    source = (
        _normalizer_source() + "\ndef make(flag):\n"
        "    return relay() if flag else relay()\n"
        "def relay():\n"
        "    return make(True)\n"
        "relay().system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_conditional_return_call_cycle() -> None:
    source = (
        _preflight_source_fixture() + "\ndef make(flag):\n"
        "    return relay() if flag else relay()\n"
        "def relay():\n"
        "    return make(True)\n"
        "relay().system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_dynamic_subscript_return_member_dispatch() -> None:
    source = (
        _normalizer_source("import os") + "\ndef make(index):\n"
        "    return [os][index]\n"
        "make(0).system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_dynamic_subscript_return_member_dispatch() -> None:
    source = (
        _preflight_source_fixture("import os") + "\ndef make(index):\n"
        "    return [os][index]\n"
        "make(0).system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_dynamic_subscript_return_member_extraction() -> None:
    source = (
        _normalizer_source("import os") + "\ndef make(index):\n"
        "    return [os][index]\n"
        "fn = make(0).system\n"
        "fn('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_dynamic_subscript_return_member_extraction() -> None:
    source = (
        _preflight_source_fixture("import os") + "\ndef make(index):\n"
        "    return [os][index]\n"
        "fn = make(0).system\n"
        "fn('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


@pytest.mark.parametrize(
    "suffix",
    [
        (
            "class C:\n"
            "    def make(self):\n"
            "        return os\n"
            "C().make().system('forbidden')"
        ),
        (
            "class C:\n"
            "    @staticmethod\n"
            "    def make():\n"
            "        return os\n"
            "C.make().system('forbidden')"
        ),
        (
            "class C:\n"
            "    @classmethod\n"
            "    def make(cls):\n"
            "        return os\n"
            "C.make().system('forbidden')"
        ),
        (
            "class C:\n"
            "    @property\n"
            "    def tool(self):\n"
            "        return os\n"
            "C().tool.system('forbidden')"
        ),
        (
            "class Outer:\n"
            "    class C:\n"
            "        def make(self):\n"
            "            return os\n"
            "Outer.C().make().system('forbidden')"
        ),
    ],
)
def test_normalizer_guard_rejects_class_member_return_bypasses(suffix: str) -> None:
    source = _normalizer_source("import os") + "\n" + suffix
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


@pytest.mark.parametrize(
    "suffix",
    [
        (
            "class C:\n"
            "    def make(self):\n"
            "        return os\n"
            "C().make().system('forbidden')"
        ),
        (
            "class C:\n"
            "    @staticmethod\n"
            "    def make():\n"
            "        return os\n"
            "C.make().system('forbidden')"
        ),
        (
            "class C:\n"
            "    @classmethod\n"
            "    def make(cls):\n"
            "        return os\n"
            "C.make().system('forbidden')"
        ),
        (
            "class C:\n"
            "    @property\n"
            "    def tool(self):\n"
            "        return os\n"
            "C().tool.system('forbidden')"
        ),
        (
            "class Outer:\n"
            "    class C:\n"
            "        def make(self):\n"
            "            return os\n"
            "Outer.C().make().system('forbidden')"
        ),
    ],
)
def test_preflight_guard_rejects_class_member_return_bypasses(suffix: str) -> None:
    source = _preflight_source_fixture("import os") + "\n" + suffix
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


@pytest.mark.parametrize("module_name", ["posix", "nt"])
def test_normalizer_guard_rejects_platform_side_effect_imports(
    module_name: str,
) -> None:
    source = _normalizer_source(f"import {module_name}") + (
        f"\n{module_name}.system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_import_violation"):
        validate_normalizer_static_source(source)


@pytest.mark.parametrize("module_name", ["posix", "nt"])
def test_preflight_guard_rejects_platform_side_effect_imports(module_name: str) -> None:
    source = _preflight_source_fixture(f"import {module_name}") + (
        f"\n{module_name}.system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_import_violation"):
        contracts.validate_preflight_static_source(source)


@pytest.mark.parametrize("module_name", ["posix", "nt"])
def test_normalizer_guard_rejects_platform_side_effect_import_aliases(
    module_name: str,
) -> None:
    source = _normalizer_source(f"import {module_name} as platform_mod") + (
        "\nplatform_mod.system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_import_violation"):
        validate_normalizer_static_source(source)


@pytest.mark.parametrize("module_name", ["posix", "nt"])
def test_preflight_guard_rejects_platform_side_effect_import_aliases(
    module_name: str,
) -> None:
    source = _preflight_source_fixture(f"import {module_name} as platform_mod") + (
        "\nplatform_mod.system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_import_violation"):
        contracts.validate_preflight_static_source(source)


@pytest.mark.parametrize("module_name", ["posix", "nt"])
def test_normalizer_guard_rejects_returned_platform_side_effect_modules(
    module_name: str,
) -> None:
    source = _normalizer_source(f"import {module_name}") + (
        f"\ndef make():\n    return {module_name}\nmake().system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_import_violation"):
        validate_normalizer_static_source(source)


@pytest.mark.parametrize("module_name", ["posix", "nt"])
def test_preflight_guard_rejects_returned_platform_side_effect_modules(
    module_name: str,
) -> None:
    source = _preflight_source_fixture(f"import {module_name}") + (
        f"\ndef make():\n    return {module_name}\nmake().system('forbidden')"
    )
    with pytest.raises(SchemaContractError, match="capability_import_violation"):
        contracts.validate_preflight_static_source(source)


@pytest.mark.parametrize(
    "suffix",
    [
        "items = [os]\ntool = items[idx]\ntool.system('forbidden')",
        "items = {'tool': os}\ntool = items[key]\ntool.system('forbidden')",
        (
            "items = [os]\ntool = items[0] if True else items[0]\n"
            "tool.system('forbidden')"
        ),
        (
            "def make():\n"
            "    return [os]\n"
            "items = make()\n"
            "tool = items[0]\n"
            "tool.system('forbidden')"
        ),
        "items = [os]\ntool = items[idx]\ntool.popen('forbidden')",
        "items = [os]\ntool = items[idx]\ntool.spawnv(0, 'forbidden', [])",
    ],
)
def test_normalizer_guard_rejects_container_alias_member_dispatch(
    suffix: str,
) -> None:
    source = _normalizer_source("import os") + "\nidx = 0\nkey = 'tool'\n" + suffix
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


@pytest.mark.parametrize(
    "suffix",
    [
        "items = [os]\ntool = items[idx]\ntool.system('forbidden')",
        "items = {'tool': os}\ntool = items[key]\ntool.system('forbidden')",
        (
            "items = [os]\ntool = items[0] if True else items[0]\n"
            "tool.system('forbidden')"
        ),
        (
            "def make():\n"
            "    return [os]\n"
            "items = make()\n"
            "tool = items[0]\n"
            "tool.system('forbidden')"
        ),
        "items = [os]\ntool = items[idx]\ntool.popen('forbidden')",
        "items = [os]\ntool = items[idx]\ntool.spawnv(0, 'forbidden', [])",
    ],
)
def test_preflight_guard_rejects_container_alias_member_dispatch(
    suffix: str,
) -> None:
    source = (
        _preflight_source_fixture("import os") + "\nidx = 0\nkey = 'tool'\n" + suffix
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


def test_normalizer_guard_rejects_container_alias_member_extraction() -> None:
    source = (
        _normalizer_source("import os")
        + "\nidx = 0\nitems = [os]\ntool = items[idx]\nfn = tool.system\nfn('x')"
    )
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


def test_preflight_guard_rejects_container_alias_member_extraction() -> None:
    source = (
        _preflight_source_fixture("import os")
        + "\nidx = 0\nitems = [os]\ntool = items[idx]\nfn = tool.system\nfn('x')"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


@pytest.mark.parametrize(
    "suffix",
    [
        "items = [os]\nfn = items[0].system\nfn('forbidden')",
        "items = [os]\nfn = items[idx].system\nfn('forbidden')",
        "items = [[os]]\nfn = items[0][0].system\nfn('forbidden')",
    ],
)
def test_normalizer_guard_rejects_subscript_member_extraction(
    suffix: str,
) -> None:
    source = _normalizer_source("import os") + "\nidx = 0\n" + suffix
    with pytest.raises(SchemaContractError, match="retired_normalizer_error"):
        validate_normalizer_static_source(source)


@pytest.mark.parametrize(
    "suffix",
    [
        "items = [os]\nfn = items[0].system\nfn('forbidden')",
        "items = [os]\nfn = items[idx].system\nfn('forbidden')",
        "items = [[os]]\nfn = items[0][0].system\nfn('forbidden')",
    ],
)
def test_preflight_guard_rejects_subscript_member_extraction(
    suffix: str,
) -> None:
    source = _preflight_source_fixture("import os") + "\nidx = 0\n" + suffix
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


@pytest.mark.parametrize("name", ["methodcaller", "attrgetter"])
def test_normalizer_guard_rejects_operator_dynamic_member_dispatch(name: str) -> None:
    source = _normalizer_source("import operator") + f"\noperator.{name}('system')"
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        validate_normalizer_static_source(source)


@pytest.mark.parametrize("name", ["methodcaller", "attrgetter"])
def test_preflight_guard_rejects_operator_dynamic_member_dispatch(name: str) -> None:
    source = (
        _preflight_source_fixture("import operator") + f"\noperator.{name}('system')"
    )
    with pytest.raises(SchemaContractError, match="capability_call_violation"):
        contracts.validate_preflight_static_source(source)


@pytest.mark.parametrize(
    "field",
    [
        "authorized",
        "authorization_id",
        "method_observation_id",
        "exact_output",
        "des_output",
        "metric_value",
        "current_runtime_lock",
    ],
)
def test_recursive_forbidden_field_union_rejects_overlap_keys(field: str) -> None:
    with pytest.raises(SchemaContractError, match="recursive_forbidden_field"):
        contracts.validate_recursive_forbidden_fields({"nested": {field: "forbidden"}})


def test_spec_17_3_28_schema_preflight_results_reject_quantitative_fields() -> None:
    payload = _preflight_result_fixture()
    contracts.validate_preflight_result_payload(payload)
    payload["certificate_payload_or_null"]["nested"] = {
        "audit": [{"deadlock_probability": "0.1"}]
    }

    with pytest.raises(SchemaContractError, match="outcome_leakage"):
        contracts.validate_preflight_result_payload(payload)


def test_spec_17_3_31_schema_certified_records_require_runtime_hashes() -> None:
    record = _certified_record_fixture()
    contracts.validate_certified_record_runtime_evidence(record)
    record.pop("estimand_id")

    with pytest.raises(SchemaContractError, match="missing_key"):
        contracts.validate_certified_record_runtime_evidence(record)


def test_spec_17_3_32_schema_exact_des_same_case_target_certificate_domain_metric() -> (
    None
):
    pair = _same_target_pair_fixture()
    contracts.validate_same_target_lock(pair)
    pair["des_method_observation_id"] = pair["exact_method_observation_id"]
    pair = _with_rehashed(pair, "same_target_lock_sha256")

    with pytest.raises(SchemaContractError, match="exact_des_target_mismatch"):
        contracts.validate_same_target_lock(pair)


def test_spec_17_3_33_schema_failed_control_blocks_quant_authorization() -> None:
    authorization = _quantitative_authorization_fixture()
    command_manifest, command_records = _valid_quantitative_command_manifest(
        authorization["authorized_scope"]
    )
    controls = {"negative-control-a": True}
    contracts.validate_quantitative_authorization(
        authorization,
        mandatory_control_statuses=controls,
        required_mandatory_control_ids=["negative-control-a"],
        command_manifest=command_manifest,
        command_records=command_records,
    )
    controls["negative-control-a"] = False

    with pytest.raises(SchemaContractError, match="failed_negative_control"):
        contracts.validate_quantitative_authorization(
            authorization,
            mandatory_control_statuses=controls,
            required_mandatory_control_ids=["negative-control-a"],
            command_manifest=command_manifest,
            command_records=command_records,
        )


def test_spec_17_3_35_schema_failure_refusal_evidence_append_only() -> None:
    schema = json.loads(
        (_ROW_FAMILY_ROOT / "failure_ledger.json").read_text(encoding="utf-8")
    )
    assert schema["schema_version"] == "ims-deadlock/g6b-row-family-failure-ledger/v2"
    assert schema["append_only"] is True
    assert schema["entries"] == []
    assert schema["empty_entries_meaning"] == (
        "no authorized current row-family attempt has occurred"
    )
    assert schema["empty_entries_do_not_mean_no_historical_failures"] is True
    expected_codes = set().union(*schema["refusal_reason_code_groups"].values())
    assert schema["required_future_reason_codes"] == sorted(expected_codes)

    current = _failure_evidence_hashes()
    prior = current[:2]
    contracts.validate_append_only_failure_evidence_hashes(
        current,
        prior_entry_hashes=prior,
    )

    with pytest.raises(SchemaContractError, match="append_only_ledger_rewrite"):
        contracts.validate_append_only_failure_evidence_hashes(
            current[1:],
            prior_entry_hashes=prior,
        )


def test_normalization_authorization_rejects_legacy_bypass_shape() -> None:
    legacy: JsonObject = {
        "schema_version": "ims-deadlock/g6b-retired-normalization-authorization/v1",
        "authorization_id": "legacy-bypass",
        "bundle_id": _TEST_BUNDLE_ID,
        "capability": "retired_authority_fingerprint_normalization",
        "scope": "SCHEMA_REPRESENTABILITY_ONLY",
        "authorized": True,
        "retired_authority_ids": ["G4", "G5", "G6_R"],
        "source_inventory_sha256": "1" * 64,
        "selector_matrix_sha256": "2" * 64,
        "normalizer_source_sha256": "3" * 64,
        "authorization_sha256": None,
    }
    legacy["authorization_sha256"] = finalized_self_hash(
        legacy,
        "authorization_sha256",
    )

    with pytest.raises(SchemaContractError, match="missing_key"):
        _validate_valid_normalization_authorization(legacy)


@pytest.mark.parametrize("authorized", [False, 1, "true"])
def test_normalization_authorization_requires_explicit_true(
    authorized: object,
) -> None:
    record = valid_normalization_authorization()
    record["authorized"] = authorized
    record = _with_rehashed(record, "authorization_sha256")

    with pytest.raises(
        SchemaContractError,
        match="unauthorized_retired_normalization_attempt",
    ):
        _validate_valid_normalization_authorization(record)


def test_normalization_authorization_rejects_identity_drift() -> None:
    record = valid_normalization_authorization()
    record["invalidated_by_identity_drift"] = True
    record = _with_rehashed(record, "authorization_sha256")

    with pytest.raises(SchemaContractError, match="runtime_identity_drift"):
        _validate_valid_normalization_authorization(record)


def test_authority_lock_record_closes_identity_and_projection_lock() -> None:
    record = valid_authority_lock_record("G4_FREEZE")
    contracts.validate_authority_lock_record(record)

    missing = dict(record)
    missing.pop("origin_tree_hash_or_null")
    with pytest.raises(SchemaContractError, match="missing_key"):
        contracts.validate_authority_lock_record(missing)

    extra = dict(record)
    extra["legacy_projection_summary"] = "not-closed"
    with pytest.raises(SchemaContractError, match="unexpected_key"):
        contracts.validate_authority_lock_record(extra)

    illegal = _with_rehashed(
        {**record, "authority_id": "G6B_CURRENT_DISCOVERY"},
        "authority_lock_record_sha256",
    )
    with pytest.raises(SchemaContractError, match="illegal_retired_authority"):
        contracts.validate_authority_lock_record(illegal)

    unverified = _with_rehashed(
        {**record, "identity_verification_status": "unverified_refuse"},
        "authority_lock_record_sha256",
    )
    contracts.validate_authority_lock_record(unverified)

    historical = _with_rehashed(
        {**record, "identity_verification_status": "verified_historical_identity"},
        "authority_lock_record_sha256",
    )
    contracts.validate_authority_lock_record(historical)


def test_authority_source_record_binds_exact_27_sources_and_projection_use() -> None:
    schema = _load_retired_schema_definition()
    lock = valid_authority_lock_record("G4_FREEZE")
    source = valid_authority_source_record(
        contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY[0],
        authority_lock_record_sha256=lock["authority_lock_record_sha256"],
    )
    contracts.validate_authority_source_record(
        source,
        authority_lock_hashes=_authority_lock_hashes({"G4_FREEZE": lock}),
        expected_source_hashes=_retired_source_hashes(),
        selector_rows=schema["allowed_json_fields_by_source"],
    )

    outside = dict(source)
    outside["repo_relative_path"] = (
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "governance/unapproved-output.json"
    )
    with pytest.raises(SchemaContractError, match="source_outside_retired_inventory"):
        contracts.validate_authority_source_record(
            outside,
            authority_lock_hashes=_authority_lock_hashes({"G4_FREEZE": lock}),
            expected_source_hashes=_retired_source_hashes(),
            selector_rows=schema["allowed_json_fields_by_source"],
        )

    use_violation = dict(source)
    use_violation["allowed_projection_uses"] = []
    with pytest.raises(SchemaContractError, match="source_projection_use_violation"):
        contracts.validate_authority_source_record(
            use_violation,
            authority_lock_hashes=_authority_lock_hashes({"G4_FREEZE": lock}),
            expected_source_hashes=_retired_source_hashes(),
            selector_rows=schema["allowed_json_fields_by_source"],
        )

    undeclared = dict(source)
    undeclared["declared_historical_hash_or_null"] = None
    undeclared["declared_hash_algorithm_or_null"] = None
    undeclared["declared_hash_verified"] = False
    contracts.validate_authority_source_record(
        undeclared,
        authority_lock_hashes=_authority_lock_hashes({"G4_FREEZE": lock}),
        expected_source_hashes=_retired_source_hashes(),
        selector_rows=schema["allowed_json_fields_by_source"],
    )

    unverified_lock = _with_rehashed(
        {**lock, "identity_verification_status": "unverified_refuse"},
        "authority_lock_record_sha256",
    )
    unverified_projection = valid_authority_source_record(
        contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY[0],
        authority_lock_record_sha256=unverified_lock["authority_lock_record_sha256"],
    )
    with pytest.raises(SchemaContractError, match="unverified_projection_refusal"):
        contracts.validate_authority_source_record(
            unverified_projection,
            authority_lock_hashes=_authority_lock_hashes({"G4_FREEZE": lock}),
            expected_source_hashes=_retired_source_hashes(),
            selector_rows=schema["allowed_json_fields_by_source"],
        )

    g5_lock = valid_authority_lock_record("G5_EXECUTION")
    outcome_source = valid_authority_source_record(
        "evidence/g5/G5_RESULT_SUMMARY.json",
        authority_lock_record_sha256=g5_lock["authority_lock_record_sha256"],
    )
    assert outcome_source["contains_outcome_fields"] is True
    assert outcome_source["allowed_projection_uses"] == ["source_hash_validation"]
    contracts.validate_authority_source_record(
        outcome_source,
        authority_lock_hashes=_authority_lock_hashes({"G5_EXECUTION": g5_lock}),
        expected_source_hashes=_retired_source_hashes(),
        selector_rows=schema["allowed_json_fields_by_source"],
    )

    outcome_projection = dict(outcome_source)
    outcome_projection["allowed_projection_uses"] = [
        "case_content_projection",
        "source_hash_validation",
    ]
    with pytest.raises(SchemaContractError, match="source_outcome_field_violation"):
        contracts.validate_authority_source_record(
            outcome_projection,
            authority_lock_hashes=_authority_lock_hashes({"G5_EXECUTION": g5_lock}),
            expected_source_hashes=_retired_source_hashes(),
            selector_rows=schema["allowed_json_fields_by_source"],
        )


def test_normalization_manifest_closes_maps_refs_and_failure_eligibility() -> None:
    locks = _retired_authority_lock_records()
    sources = _retired_authority_source_records(locks)
    fingerprints = _normalization_fingerprint_records()
    manifest = valid_normalization_manifest(
        authority_locks=locks,
        authority_sources=sources,
        fingerprint_records=fingerprints,
    )
    contracts.validate_normalization_manifest(
        manifest,
        authority_lock_records=locks,
        authority_source_records=sources,
        fingerprint_records=fingerprints,
    )

    missing = dict(manifest)
    missing.pop("authority_source_record_hashes")
    with pytest.raises(SchemaContractError, match="missing_key"):
        contracts.validate_normalization_manifest(
            missing,
            authority_lock_records=locks,
            authority_source_records=sources,
            fingerprint_records=fingerprints,
        )

    extra = dict(manifest)
    extra["legacy_summary"] = {"eligible_count": 24}
    with pytest.raises(SchemaContractError, match="unexpected_key"):
        contracts.validate_normalization_manifest(
            extra,
            authority_lock_records=locks,
            authority_source_records=sources,
            fingerprint_records=fingerprints,
        )

    unsorted_hash_map = deepcopy(manifest)
    unsorted_hash_map["authority_source_record_hashes"] = dict(
        reversed(list(manifest["authority_source_record_hashes"].items()))
    )
    unsorted_hash_map = _with_rehashed(unsorted_hash_map, "manifest_sha256")
    with pytest.raises(SchemaContractError, match="hash_map_not_sorted"):
        contracts.validate_normalization_manifest(
            unsorted_hash_map,
            authority_lock_records=locks,
            authority_source_records=sources,
            fingerprint_records=fingerprints,
        )

    duplicate_lineage = deepcopy(manifest)
    first_lineage = next(iter(duplicate_lineage["unique_lineage_map"]))
    duplicate_lineage["unique_lineage_map"][first_lineage].append(
        duplicate_lineage["unique_lineage_map"][first_lineage][0]
    )
    duplicate_lineage = _with_rehashed(duplicate_lineage, "manifest_sha256")
    with pytest.raises(SchemaContractError, match="duplicate_lineage_miscount"):
        contracts.validate_normalization_manifest(
            duplicate_lineage,
            authority_lock_records=locks,
            authority_source_records=sources,
            fingerprint_records=fingerprints,
        )

    absent_ref = deepcopy(manifest)
    absent_ref["authority_lock_record_hashes"].pop("G4_FREEZE")
    absent_ref = _with_rehashed(absent_ref, "manifest_sha256")
    with pytest.raises(SchemaContractError, match="absent_authority_lock_ref"):
        contracts.validate_normalization_manifest(
            absent_ref,
            authority_lock_records=locks,
            authority_source_records=sources,
            fingerprint_records=fingerprints,
        )

    mismatched_ref = deepcopy(manifest)
    first_source = next(iter(mismatched_ref["authority_source_record_hashes"]))
    mismatched_ref["authority_source_record_hashes"][first_source] = "9" * 64
    mismatched_ref = _with_rehashed(mismatched_ref, "manifest_sha256")
    with pytest.raises(SchemaContractError, match="authority_source_ref_mismatch"):
        contracts.validate_normalization_manifest(
            mismatched_ref,
            authority_lock_records=locks,
            authority_source_records=sources,
            fingerprint_records=fingerprints,
        )

    failed_record = next(iter(fingerprints.values()))
    failed_record["dimension_status"] = "unreconstructable_refuse"
    failed_record["comparison_projection_ref_or_null"] = None
    failed_record["comparison_projection_sha256_or_null"] = None
    failed_record = _with_rehashed(failed_record, "record_provenance_sha256")
    failed_fingerprints = {**fingerprints, failed_record["record_id"]: failed_record}
    upgraded = valid_normalization_manifest(
        authority_locks=locks,
        authority_sources=sources,
        fingerprint_records=failed_fingerprints,
    )
    upgraded["comparison_eligibility"][failed_record["record_id"]] = {
        "eligible_for_overlap_comparison": True,
        "refusal_reason_code_or_null": None,
    }
    upgraded = _with_rehashed(upgraded, "manifest_sha256")
    with pytest.raises(SchemaContractError, match="unreconstructable_not_eligible"):
        contracts.validate_normalization_manifest(
            upgraded,
            authority_lock_records=locks,
            authority_source_records=sources,
            fingerprint_records=failed_fingerprints,
        )


def test_normalization_manifest_rejects_tampered_authority_lock_content() -> None:
    locks = _retired_authority_lock_records()
    sources = _retired_authority_source_records(locks)
    fingerprints = _normalization_fingerprint_records()
    manifest = valid_normalization_manifest(
        authority_locks=locks,
        authority_sources=sources,
        fingerprint_records=fingerprints,
    )
    tampered_locks = deepcopy(locks)
    tampered_locks["G4_FREEZE"]["origin_remote"] = "stale-tampered-origin"

    with pytest.raises(SchemaContractError, match="self_hash_mismatch"):
        contracts.validate_normalization_manifest(
            manifest,
            authority_lock_records=tampered_locks,
            authority_source_records=sources,
            fingerprint_records=fingerprints,
        )


def test_normalization_manifest_rejects_tampered_fingerprint_content() -> None:
    locks = _retired_authority_lock_records()
    sources = _retired_authority_source_records(locks)
    fingerprints = _normalization_fingerprint_records()
    manifest = valid_normalization_manifest(
        authority_locks=locks,
        authority_sources=sources,
        fingerprint_records=fingerprints,
    )
    tampered_fingerprints = deepcopy(fingerprints)
    first_record_id = next(iter(tampered_fingerprints))
    tampered_fingerprints[first_record_id]["normalizer_version"] = (
        "stale-tampered-normalizer"
    )

    with pytest.raises(SchemaContractError, match="self_hash_mismatch"):
        contracts.validate_normalization_manifest(
            manifest,
            authority_lock_records=locks,
            authority_source_records=sources,
            fingerprint_records=tampered_fingerprints,
        )


def test_normalization_manifest_requires_empty_missing_source_records() -> None:
    locks = _retired_authority_lock_records()
    sources = _retired_authority_source_records(locks)
    fingerprints = _normalization_fingerprint_records()
    manifest = valid_normalization_manifest(
        authority_locks=locks,
        authority_sources=sources,
        fingerprint_records=fingerprints,
    )
    manifest["missing_source_records"] = ["arbitrary-non-closed-record"]
    manifest = _with_rehashed(manifest, "manifest_sha256")

    with pytest.raises(SchemaContractError, match="missing_source_records_not_empty"):
        contracts.validate_normalization_manifest(
            manifest,
            authority_lock_records=locks,
            authority_source_records=sources,
            fingerprint_records=fingerprints,
        )


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("invalidated_by_identity_drift", True, "runtime_identity_drift"),
        (
            "allowed_output_root",
            {
                "repo_relative_posix_path": "governance/g6b/legacy-normalization",
                "contains_only_governance_outputs": True,
            },
            "output_root_contract_drift",
        ),
        ("source_head", "0" * 40, "source_identity_drift"),
        ("source_tree_hash", "1" * 40, "source_identity_drift"),
        ("expected_file_manifest_hash", "8" * 64, "file_manifest_drift"),
        ("normalizer_code_sha256", "2" * 64, "normalizer_code_drift"),
        ("review_artifact_hash", "3" * 64, "review_artifact_drift"),
    ],
)
def test_normalization_authorization_binds_exact_source_code_review_and_root(
    field: str,
    value: object,
    code: str,
) -> None:
    schema = _load_retired_schema_definition()
    authorization = valid_normalization_authorization()
    contracts.validate_normalization_authorization(
        authorization,
        expected_schema_inventory_patterns=contracts.EXPECTED_RETIRED_SOURCE_INVENTORY,
        expected_concrete_source_paths=(
            contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY
        ),
        expected_selector_matrix=schema["allowed_json_fields_by_source"],
        expected_git_object_format="sha1",
        expected_source_head=authorization["source_head"],
        expected_source_tree_hash=authorization["source_tree_hash"],
        expected_file_manifest_hash=authorization["expected_file_manifest_hash"],
        expected_normalizer_code_sha256=authorization["normalizer_code_sha256"],
        expected_review_artifact_hash=authorization["review_artifact_hash"],
        expected_output_root=_approved_normalization_governance_root(),
    )

    drifted = deepcopy(authorization)
    drifted[field] = value
    drifted = _with_rehashed(drifted, "authorization_sha256")
    with pytest.raises(SchemaContractError, match=code):
        contracts.validate_normalization_authorization(
            drifted,
            expected_schema_inventory_patterns=(
                contracts.EXPECTED_RETIRED_SOURCE_INVENTORY
            ),
            expected_concrete_source_paths=(
                contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY
            ),
            expected_selector_matrix=schema["allowed_json_fields_by_source"],
            expected_git_object_format="sha1",
            expected_source_head=authorization["source_head"],
            expected_source_tree_hash=authorization["source_tree_hash"],
            expected_file_manifest_hash=authorization["expected_file_manifest_hash"],
            expected_normalizer_code_sha256=authorization["normalizer_code_sha256"],
            expected_review_artifact_hash=authorization["review_artifact_hash"],
            expected_output_root=_approved_normalization_governance_root(),
        )


def test_normalization_authorization_rejects_alternate_caller_output_root() -> None:
    schema = _load_retired_schema_definition()
    authorization = valid_normalization_authorization()
    alternate_root = _alternate_normalization_governance_root()
    authorization["allowed_output_root"] = {
        "repo_relative_posix_path": alternate_root,
        "contains_only_governance_outputs": True,
    }
    authorization = _with_rehashed(authorization, "authorization_sha256")

    with pytest.raises(SchemaContractError, match="output_root_contract_drift"):
        contracts.validate_normalization_authorization(
            authorization,
            expected_schema_inventory_patterns=contracts.EXPECTED_RETIRED_SOURCE_INVENTORY,
            expected_concrete_source_paths=(
                contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY
            ),
            expected_selector_matrix=schema["allowed_json_fields_by_source"],
            expected_git_object_format="sha1",
            expected_source_head=authorization["source_head"],
            expected_source_tree_hash=authorization["source_tree_hash"],
            expected_file_manifest_hash=authorization["expected_file_manifest_hash"],
            expected_normalizer_code_sha256=authorization["normalizer_code_sha256"],
            expected_review_artifact_hash=authorization["review_artifact_hash"],
            expected_output_root=alternate_root,
        )


@pytest.mark.parametrize(
    "field",
    [
        "same_target_lock_id",
        "case_unit_id",
        "certificate_artifact_hash",
        "absorption_domain_hash",
        "metric_schema_sha256",
        "same_target_lock_sha256",
    ],
)
def test_same_target_lock_rejects_missing_required_envelope_fields(field: str) -> None:
    record = _same_target_pair_fixture()
    record.pop(field)

    with pytest.raises(SchemaContractError, match="missing_key"):
        contracts.validate_same_target_lock(record)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("schema_version", "evil/v999", "schema_version_drift"),
        ("lock_created_at_utc", "not-a-timestamp", "timestamp_format_violation"),
    ],
)
def test_same_target_lock_rejects_version_and_timestamp_drift(
    field: str,
    value: str,
    code: str,
) -> None:
    record = _same_target_pair_fixture()
    record[field] = value
    record = _with_rehashed(record, "same_target_lock_sha256")
    with pytest.raises(SchemaContractError, match=code):
        contracts.validate_same_target_lock(record)


def test_quantitative_authorization_rejects_minimal_and_scope_map_drift() -> None:
    command_manifest, command_records = _valid_quantitative_command_manifest()
    with pytest.raises(SchemaContractError, match="missing_key"):
        contracts.validate_quantitative_authorization(
            {
                "authorized": True,
                "mandatory_control_statuses": {"negative-control-a": True},
            },
            mandatory_control_statuses={"negative-control-a": True},
            required_mandatory_control_ids=["negative-control-a"],
            command_manifest=command_manifest,
            command_records=command_records,
        )


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("schema_version", "evil/v999", "schema_version_drift"),
        ("issued_at_utc", "not-a-timestamp", "timestamp_format_violation"),
    ],
)
def test_quantitative_authorization_rejects_version_and_timestamp_drift(
    field: str,
    value: str,
    code: str,
) -> None:
    record = _quantitative_authorization_fixture()
    command_manifest, command_records = _valid_quantitative_command_manifest(
        record["authorized_scope"]
    )
    record[field] = value
    record = _with_rehashed(record, "authorization_sha256")
    with pytest.raises(SchemaContractError, match=code):
        contracts.validate_quantitative_authorization(
            record,
            mandatory_control_statuses={"negative-control-a": True},
            required_mandatory_control_ids=["negative-control-a"],
            command_manifest=command_manifest,
            command_records=command_records,
        )


def test_quantitative_authorization_binds_exact_command_manifest_hashes() -> None:
    record = _quantitative_authorization_fixture()
    command_manifest, command_records = _valid_quantitative_command_manifest(
        record["authorized_scope"]
    )
    record["allowed_commands"] = ["f" * 64]
    record = _with_rehashed(record, "authorization_sha256")
    with pytest.raises(SchemaContractError, match="command_hash_map_mismatch"):
        contracts.validate_quantitative_authorization(
            record,
            mandatory_control_statuses={"negative-control-a": True},
            required_mandatory_control_ids=["negative-control-a"],
            command_manifest=command_manifest,
            command_records=command_records,
        )

    record = _quantitative_authorization_fixture()
    record["authorized_scope"]["same_target_lock_hashes"] = {}
    record = _with_rehashed(record, "authorization_sha256")
    with pytest.raises(SchemaContractError, match="hash_map_empty"):
        contracts.validate_quantitative_authorization(
            record,
            mandatory_control_statuses={"negative-control-a": True},
            required_mandatory_control_ids=["negative-control-a"],
            command_manifest=command_manifest,
            command_records=command_records,
        )


def test_append_only_ledger_rejects_locally_rehashed_history_rewrite() -> None:
    prior = _failure_evidence_hashes()[:1]
    rewritten = [
        _synthetic_hash("locally-rehashed-relabelled-evidence"),
        *_failure_evidence_hashes()[1:],
    ]

    with pytest.raises(SchemaContractError, match="append_only_ledger_rewrite"):
        contracts.validate_append_only_failure_evidence_hashes(
            rewritten,
            prior_entry_hashes=prior,
        )


@pytest.mark.parametrize(
    "field",
    sorted(contracts.PREFLIGHT_RECURSIVE_PROHIBITED_FIELDS),
)
def test_preflight_result_rejects_every_recursive_prohibited_field(field: str) -> None:
    payload = _preflight_result_fixture()
    payload["certificate_payload_or_null"]["nested"] = {field: "forbidden"}

    with pytest.raises(SchemaContractError, match="outcome_leakage"):
        contracts.validate_preflight_result_payload(payload)


def test_spec_17_3_06_fingerprint_record_accepts_exact_dimension_relations() -> None:
    for dimension in FINGERPRINT_DIMENSIONS:
        record = valid_fingerprint_record(dimension=dimension)

        validate_fingerprint_record(record, _projection_for_record(record))


def test_spec_17_3_06_fingerprint_record_rejects_subject_relation_drift() -> None:
    record = valid_fingerprint_record(dimension="case_content_sha256")
    record["subject_type"] = "method_observation"
    record = _with_rehashed(record, "record_provenance_sha256")

    with pytest.raises(SchemaContractError, match="subject_type_mismatch"):
        validate_fingerprint_record(record, _projection_for_record(record))


def test_spec_17_3_06_fingerprint_record_rejects_projection_kind_drift() -> None:
    record = valid_fingerprint_record(dimension="metric_schema_sha256")
    record["projection_kind"] = "semantic_content"
    record = _with_rehashed(record, "record_provenance_sha256")

    with pytest.raises(SchemaContractError, match="projection_kind_mismatch"):
        validate_fingerprint_record(record, _projection_for_record(record))


def test_spec_17_3_06_fingerprint_record_rejects_policy_drift() -> None:
    record = valid_fingerprint_record(dimension="output_root_reservation_sha256")
    record["comparison_policy"] = "strict_semantic_distinctness"
    record = _with_rehashed(record, "record_provenance_sha256")

    with pytest.raises(SchemaContractError, match="comparison_policy_mismatch"):
        validate_fingerprint_record(record, _projection_for_record(record))


def test_not_applicable_by_protocol_fingerprint_rejects_null_projection() -> None:
    record = _with_null_projection(
        valid_fingerprint_record(dimension="random_stream_manifest_sha256"),
        status="not_applicable_by_protocol",
    )

    with pytest.raises(SchemaContractError, match="missing_source"):
        validate_fingerprint_record(record, None)


@pytest.mark.parametrize(
    "status",
    ["not_applicable_retired_stage", "unreconstructable_refuse"],
)
def test_retired_or_unreconstructable_fingerprint_allows_null_projection(
    status: str,
) -> None:
    record = _with_null_projection(
        valid_fingerprint_record(dimension="sealed_prediction_sha256"),
        status=status,
    )

    validate_fingerprint_record(record, None)


@pytest.mark.parametrize(
    "field",
    [
        "record_schema_version",
        "record_id",
        "dimension",
        "projection_kind",
        "subject_type",
        "subject_id",
        "owner_object_id",
        "projection_schema_version",
        "comparison_projection_ref_or_null",
        "comparison_projection_sha256_or_null",
        "canonicalization_version",
        "source_authority_id",
        "source_stage",
        "source_method_role_or_null",
        "source_run_role_or_null",
        "source_artifact_refs",
        "source_artifact_byte_hashes",
        "normalizer_version",
        "dimension_status",
        "lineage_id",
        "inherited_from_record_id_or_null",
        "duplicate_lineage_of_record_id_or_null",
        "depends_on_dimensions",
        "correlated_with_dimensions",
        "comparison_policy",
        "applicability_reason_code_or_null",
        "record_provenance_sha256",
    ],
)
def test_spec_17_3_07_fingerprint_record_rejects_missing_envelope_field(
    field: str,
) -> None:
    record = valid_fingerprint_record(dimension="case_content_sha256")
    record.pop(field)

    with pytest.raises(SchemaContractError, match="missing_key"):
        validate_fingerprint_record(
            record,
            _projection_for_dimension("case_content_sha256"),
        )


def test_spec_17_3_07_fingerprint_record_rejects_injected_envelope_field() -> None:
    record = valid_fingerprint_record(dimension="case_content_sha256")
    record["injected_governance_override"] = False
    record = _with_rehashed(record, "record_provenance_sha256")

    with pytest.raises(SchemaContractError, match="unexpected_key"):
        validate_fingerprint_record(record, _projection_for_record(record))


def test_spec_17_3_07_schema_governance_only_projection_hash_invariance() -> None:
    record = _valid_dimension_comparison_record(dimension="sealed_prediction_sha256")
    _validate_dimension_comparison_positive(record)
    record["retired_fingerprint_record_hash"] = "9" * 64
    record["retired_comparison_projection_sha256_or_null"] = record[
        "new_comparison_projection_sha256_or_null"
    ]
    record = _with_rehashed_comparison(record)

    with pytest.raises(SchemaContractError, match="overlap_hit"):
        validate_dimension_comparison_record(
            record,
            semantic_lineage_audit_passed=True,
        )


def test_spec_17_3_08_schema_renamed_content_predictions_refuse() -> None:
    record = _valid_dimension_comparison_record(dimension="sealed_prediction_sha256")
    _validate_dimension_comparison_positive(record)
    record["retired_authority_id"] = "retired-authority-renamed"
    record["retired_lineage_id"] = "fixture-paraphrased-same-projection"
    record["retired_comparison_projection_sha256_or_null"] = record[
        "new_comparison_projection_sha256_or_null"
    ]
    record = _with_rehashed_comparison(record)

    with pytest.raises(SchemaContractError, match="overlap_hit"):
        validate_dimension_comparison_record(
            record,
            semantic_lineage_audit_passed=True,
        )


def test_spec_17_3_09_schema_content_mutations_keep_correlations() -> None:
    record = _valid_dimension_comparison_record(dimension="case_content_sha256")
    _validate_dimension_comparison_positive(record)

    with pytest.raises(SchemaContractError, match="semantic_lineage_ambiguous"):
        validate_dimension_comparison_record(record)


def test_spec_17_3_10_schema_state_snapshot_parent_link_free() -> None:
    record = _valid_dimension_comparison_record(dimension="state_snapshot_sha256")
    _validate_dimension_comparison_positive(record)
    record["comparison_policy"] = "provenance_containment_only"
    record = _with_rehashed_comparison(record)

    with pytest.raises(SchemaContractError, match="comparison_policy_mismatch"):
        validate_dimension_comparison_record(record)


def test_spec_17_3_16_schema_not_applicable_projection_pass_is_protocol_only() -> None:
    record = _valid_dimension_comparison_record(
        dimension="random_stream_manifest_sha256",
        status="not_applicable_by_protocol_pass",
    )
    record["retired_comparison_projection_sha256_or_null"] = record[
        "new_comparison_projection_sha256_or_null"
    ]
    record = _with_rehashed_comparison(record)
    validate_dimension_comparison_record(record, random_stream_branch="exact")
    record["dimension"] = "case_content_sha256"
    record["projection_kind"] = contracts.DIMENSION_PROJECTION_KINDS[
        "case_content_sha256"
    ]
    record["new_subject_type"] = contracts.DIMENSION_SUBJECTS["case_content_sha256"]
    record["comparison_policy"] = contracts.DIMENSION_POLICIES["case_content_sha256"]
    record["semantic_lineage_audit_ref_or_null"] = "synthetic://lineage-audit"
    record = _with_rehashed_comparison(record)

    with pytest.raises(SchemaContractError, match="comparison_status_not_allowed"):
        validate_dimension_comparison_record(
            record,
            semantic_lineage_audit_passed=True,
        )


def test_spec_17_3_17_schema_stochastic_streams_require_disjoint_substream_proof() -> (
    None
):
    record = _valid_dimension_comparison_record(
        dimension="random_stream_manifest_sha256",
        status="disjoint_stream_pass",
    )
    validate_dimension_comparison_record(
        record,
        random_stream_branch="stochastic",
        disjoint_substream_proof_passed=True,
    )

    with pytest.raises(
        SchemaContractError,
        match="random_stream_disjointness_unproved",
    ):
        validate_dimension_comparison_record(
            record,
            random_stream_branch="stochastic",
            disjoint_substream_proof_passed=False,
        )


def test_exact_not_applicable_projection_hashes_must_match() -> None:
    record = _valid_dimension_comparison_record(
        dimension="random_stream_manifest_sha256",
        status="not_applicable_by_protocol_pass",
    )

    with pytest.raises(
        SchemaContractError,
        match="not_applicable_projection_mismatch",
    ):
        validate_dimension_comparison_record(record, random_stream_branch="exact")


def test_stochastic_hash_equality_cannot_substitute_for_disjointness() -> None:
    record = _valid_dimension_comparison_record(
        dimension="random_stream_manifest_sha256",
        status="disjoint_stream_pass",
    )
    record["retired_comparison_projection_sha256_or_null"] = record[
        "new_comparison_projection_sha256_or_null"
    ]
    record = _with_rehashed_comparison(record)

    with pytest.raises(SchemaContractError, match="random_stream_overlap"):
        validate_dimension_comparison_record(
            record,
            random_stream_branch="stochastic",
            disjoint_substream_proof_passed=True,
        )


def test_spec_17_3_18_schema_output_root_reservations_are_inert() -> None:
    record = _valid_dimension_comparison_record(
        dimension="output_root_reservation_sha256",
        status="containment_separation_pass",
    )
    validate_dimension_comparison_record(record)
    record["comparison_status"] = "pass_distinct"
    record = _with_rehashed_comparison(record)

    with pytest.raises(SchemaContractError, match="comparison_status_not_allowed"):
        validate_dimension_comparison_record(record)


def test_output_root_hash_equality_cannot_prove_containment_separation() -> None:
    record = _valid_dimension_comparison_record(
        dimension="output_root_reservation_sha256",
        status="containment_separation_pass",
    )
    record["retired_comparison_projection_sha256_or_null"] = record[
        "new_comparison_projection_sha256_or_null"
    ]
    record = _with_rehashed_comparison(record)

    with pytest.raises(
        SchemaContractError,
        match="output_root_reuse_or_materialized",
    ):
        validate_dimension_comparison_record(record)


def test_dimension_comparison_refusal_codes_are_overlap_gate_scoped() -> None:
    record = _valid_dimension_comparison_record(
        dimension="case_content_sha256",
        status="overlap_hit",
    )
    record["refusal_reason_code_or_null"] = "state_bound_truncation"
    record = _with_rehashed_comparison(record)

    with pytest.raises(SchemaContractError, match="wrong_gate_refusal_code"):
        validate_dimension_comparison_record(record)


def test_spec_17_3_19_schema_root_projection_boundaries() -> None:
    retired_fingerprint = _with_null_projection(
        valid_fingerprint_record(dimension="output_root_reservation_sha256"),
        status="not_applicable_retired_stage",
    )
    validate_fingerprint_record(retired_fingerprint, None)
    direct_fingerprint = _with_null_projection(
        valid_fingerprint_record(dimension="output_root_reservation_sha256"),
        status="direct_stored",
    )
    with pytest.raises(SchemaContractError, match="missing_source"):
        validate_fingerprint_record(direct_fingerprint, None)

    reservation = valid_output_root_reservation()
    validate_output_root_reservation(reservation)
    injected_absolute_path = dict(reservation)
    injected_absolute_path["absolute_path"] = "/tmp/forbidden"
    injected_absolute_path = _with_rehashed(
        injected_absolute_path,
        "reservation_sha256",
    )
    with pytest.raises(SchemaContractError, match="unexpected_key"):
        validate_output_root_reservation(injected_absolute_path)

    injected_result_content = dict(reservation)
    injected_result_content["result_content_sha256"] = "9" * 64
    injected_result_content = _with_rehashed(
        injected_result_content,
        "reservation_sha256",
    )
    with pytest.raises(SchemaContractError, match="unexpected_key"):
        validate_output_root_reservation(injected_result_content)


def test_spec_17_3_20_schema_metric_reuse_requires_companion_auth() -> None:
    record = _valid_dimension_comparison_record(
        dimension="metric_schema_sha256",
        status="controlled_reuse_pass",
    )
    validate_dimension_comparison_record(record, metric_reuse_authorized=True)
    record["reuse_authorization_ref_or_null"] = None
    record = _with_rehashed_comparison(record)

    with pytest.raises(
        SchemaContractError,
        match="metric_reuse_unauthorized",
    ):
        validate_dimension_comparison_record(record, metric_reuse_authorized=True)


def test_spec_17_3_09_fingerprint_record_rejects_dependency_drift() -> None:
    record = valid_fingerprint_record(dimension="case_content_sha256")
    record["depends_on_dimensions"] = ["output_root_reservation_sha256"]
    record = _with_rehashed(record, "record_provenance_sha256")

    with pytest.raises(SchemaContractError, match="dimension_relation_mismatch"):
        validate_fingerprint_record(record, _projection_for_record(record))


def test_spec_17_3_09_fingerprint_record_rejects_correlation_drift() -> None:
    record = valid_fingerprint_record(dimension="case_content_sha256")
    record["correlated_with_dimensions"] = ["route_signature_sha256"]
    record = _with_rehashed(record, "record_provenance_sha256")

    with pytest.raises(SchemaContractError, match="dimension_relation_mismatch"):
        validate_fingerprint_record(record, _projection_for_record(record))


def test_spec_17_3_10_fingerprint_record_rejects_subject_contaminated_projection() -> (
    None
):
    record = valid_fingerprint_record(dimension="case_content_sha256")
    projection = _projection_for_dimension("case_content_sha256")
    projection["author"] = "reviewer"
    record["comparison_projection_sha256_or_null"] = canonical_sha256_v2(projection)
    record = _with_rehashed(record, "record_provenance_sha256")

    with pytest.raises(
        SchemaContractError,
        match="subject_id_contaminated_projection",
    ):
        validate_fingerprint_record(record, projection)


def test_spec_17_3_16_fingerprint_record_rejects_source_ref_closure_gap() -> None:
    record = valid_fingerprint_record(dimension="case_content_sha256")
    record["source_artifact_byte_hashes"].pop("sealed/g6b/method-scope-test.json")
    record = _with_rehashed(record, "record_provenance_sha256")

    with pytest.raises(
        SchemaContractError,
        match="source_artifact_hash_map_mismatch",
    ):
        validate_fingerprint_record(record, _projection_for_record(record))


def test_spec_17_3_16_fingerprint_record_rejects_unsorted_source_ref_ids() -> None:
    record = valid_fingerprint_record(dimension="case_content_sha256")
    record["source_artifact_refs"] = list(reversed(record["source_artifact_refs"]))
    record = _with_rehashed(record, "record_provenance_sha256")

    with pytest.raises(SchemaContractError, match="source_artifact_ref_not_sorted"):
        validate_fingerprint_record(record, _projection_for_record(record))


def test_spec_17_3_16_fingerprint_record_rejects_duplicate_source_ref_ids() -> None:
    record = valid_fingerprint_record(dimension="case_content_sha256")
    record["source_artifact_refs"][1] = dict(record["source_artifact_refs"][0])
    record["source_artifact_byte_hashes"] = _source_byte_hashes(
        record["source_artifact_refs"]
    )
    record = _with_rehashed(record, "record_provenance_sha256")

    with pytest.raises(SchemaContractError, match="source_artifact_ref_duplicate"):
        validate_fingerprint_record(record, _projection_for_record(record))


def test_spec_17_3_16_fingerprint_record_rejects_absolute_source_ref_path() -> None:
    record = valid_fingerprint_record(dimension="case_content_sha256")
    record["source_artifact_refs"][0]["repo_relative_posix_path"] = (
        "/sealed/g6b/case-input-test.json"
    )
    record["source_artifact_byte_hashes"] = _source_byte_hashes(
        record["source_artifact_refs"]
    )
    record = _with_rehashed(record, "record_provenance_sha256")

    with pytest.raises(SchemaContractError, match="repo_relative_path_violation"):
        validate_fingerprint_record(record, _projection_for_record(record))


def test_spec_17_3_16_fingerprint_record_rejects_source_ref_hash_mismatch() -> None:
    record = valid_fingerprint_record(dimension="case_content_sha256")
    record["source_artifact_byte_hashes"]["sealed/g6b/case-input-test.json"] = "Z" * 64
    record = _with_rehashed(record, "record_provenance_sha256")

    with pytest.raises(SchemaContractError, match="invalid_hash_digest"):
        validate_fingerprint_record(record, _projection_for_record(record))


def test_spec_17_3_17_fingerprint_record_rejects_projection_argument_drift() -> None:
    record = valid_fingerprint_record(dimension="case_content_sha256")
    projection = _projection_for_record(record)
    projection["input_mode"] = "drifted"

    with pytest.raises(
        SchemaContractError,
        match="comparison_projection_hash_mismatch",
    ):
        validate_fingerprint_record(record, projection)


def test_spec_17_3_17_fingerprint_record_rejects_projection_hash_drift() -> None:
    record = valid_fingerprint_record(dimension="case_content_sha256")
    record["comparison_projection_sha256_or_null"] = "9" * 64
    record = _with_rehashed(record, "record_provenance_sha256")

    with pytest.raises(
        SchemaContractError,
        match="comparison_projection_hash_mismatch",
    ):
        validate_fingerprint_record(record, _projection_for_record(record))


def test_spec_17_3_18_fingerprint_record_rejects_self_hash_drift() -> None:
    record = valid_fingerprint_record(dimension="case_content_sha256")
    record["subject_id"] = "case-forged"

    with pytest.raises(SchemaContractError, match="self_hash_mismatch"):
        validate_fingerprint_record(record, _projection_for_record(record))


def test_spec_17_3_19_output_root_reservation_accepts_deterministic_path() -> None:
    validate_output_root_reservation(valid_output_root_reservation())


def test_spec_17_3_19_output_root_reservation_rejects_path_drift() -> None:
    record = valid_output_root_reservation()
    record["repo_relative_posix_path"] = (
        "artifacts/g6b/quantitative/bundle-test/case-test/method-test/retry"
    )
    record = _with_rehashed(record, "reservation_sha256")

    with pytest.raises(SchemaContractError, match="output_root_path"):
        validate_output_root_reservation(record)


def test_spec_17_3_19_output_root_reservation_rejects_unreserved_root() -> None:
    record = valid_output_root_reservation()
    record["reserved"] = False
    record = _with_rehashed(record, "reservation_sha256")

    with pytest.raises(SchemaContractError, match="output_root_not_reserved"):
        validate_output_root_reservation(record)


def test_spec_17_3_19_output_root_reservation_rejects_materialized_root() -> None:
    record = valid_output_root_reservation()
    record["materialized"] = True
    record = _with_rehashed(record, "reservation_sha256")

    with pytest.raises(SchemaContractError, match="output_root_materialized"):
        validate_output_root_reservation(record)


def test_spec_17_3_19_output_root_reservation_rejects_absolute_path() -> None:
    record = valid_output_root_reservation()
    record["repo_relative_posix_path"] = f"/{_TEST_OUTPUT_ROOT}"
    record = _with_rehashed(record, "reservation_sha256")

    with pytest.raises(SchemaContractError, match="repo_relative_path_violation"):
        validate_output_root_reservation(record)


def test_spec_17_3_19_output_root_reservation_rejects_fallback_path() -> None:
    record = valid_output_root_reservation()
    record["repo_relative_posix_path"] = "artifacts/g6b/quantitative/fallback"
    record = _with_rehashed(record, "reservation_sha256")

    with pytest.raises(SchemaContractError, match="output_root_path"):
        validate_output_root_reservation(record)


def test_spec_17_3_19_output_root_reservation_rejects_pre_existing_flag() -> None:
    record = valid_output_root_reservation()
    record["pre_existing"] = False
    record = _with_rehashed(record, "reservation_sha256")

    with pytest.raises(SchemaContractError, match="unexpected_key"):
        validate_output_root_reservation(record)


def test_spec_17_3_19_output_root_reservation_rejects_injected_key() -> None:
    record = valid_output_root_reservation()
    record["absolute_path"] = "/tmp/g6b"
    record = _with_rehashed(record, "reservation_sha256")

    with pytest.raises(SchemaContractError, match="unexpected_key"):
        validate_output_root_reservation(record)


def test_spec_17_3_19_output_root_reservation_rejects_self_hash_drift() -> None:
    record = valid_output_root_reservation()
    record["reservation_sha256"] = "9" * 64

    with pytest.raises(SchemaContractError, match="self_hash_mismatch"):
        validate_output_root_reservation(record)


def _valid_command_record(command_id: str = "cmd-preflight") -> JsonObject:
    record: JsonObject = {
        "command_id": command_id,
        "capability": "target_certification_preflight",
        "executable_sha256": "0" * 64,
        "entrypoint": "ims_deadlock.g6b_target_preflight.main",
        "argv_tokens": [
            {"token_kind": "literal", "value": "g6b-target-preflight"},
            {"token_kind": "placeholder", "placeholder_code": "repo_source_root"},
        ],
        "working_directory_repo_relative": ".",
        "environment_variable_allowlist": {
            "PYTHONDONTWRITEBYTECODE": {"token_kind": "literal", "value": "1"},
            "PYTHONPATH": {
                "token_kind": "placeholder",
                "placeholder_code": "repo_source_root",
            },
        },
        "stdin_policy": "closed",
        "authorized_case_unit_ids": ["case-a"],
        "authorized_preflight_root_hash": "1" * 64,
        "command_record_sha256": None,
    }
    record["command_record_sha256"] = finalized_self_hash(
        record,
        "command_record_sha256",
    )
    return record


def _valid_command_manifest() -> tuple[JsonObject, dict[str, JsonObject]]:
    command = _valid_command_record()
    manifest: JsonObject = {
        "schema_version": ("ims-deadlock/g6b-preflight-allowed-command-manifest/v1"),
        "manifest_id": "manifest-a",
        "capability": "target_certification_preflight",
        "source_head": "a" * 40,
        "source_tree_hash": "b" * 40,
        "sealed_bundle_manifest_hash": "3" * 64,
        "input_overlap_report_sha256": "4" * 64,
        "preflight_evidence_root_reservation_sha256": "5" * 64,
        "declared_command_ids": ["cmd-preflight"],
        "command_record_hashes": {"cmd-preflight": command["command_record_sha256"]},
        "command_count": 1,
        "placeholder_vocabulary": list(contracts.PREFLIGHT_PLACEHOLDER_CODES),
        "environment_variable_name_allowlist": [
            "PYTHONDONTWRITEBYTECODE",
            "PYTHONPATH",
        ],
        "wildcard_scope_allowed": False,
        "created_at_utc": "2026-08-01T00:00:00Z",
        "manifest_sha256": None,
    }
    manifest["manifest_sha256"] = finalized_self_hash(manifest, "manifest_sha256")
    return manifest, {"cmd-preflight": command}


def _valid_preflight_authorization() -> tuple[
    JsonObject, JsonObject, dict[str, JsonObject]
]:
    manifest, command_records = _valid_command_manifest()
    evidence_root: JsonObject = {
        "root_schema_version": "ims-deadlock/g6b-preflight-evidence-root/v1",
        "bundle_id": _TEST_BUNDLE_ID,
        "repo_relative_posix_path": (
            f"evidence/g6b/target_certification/{_TEST_BUNDLE_ID}"
        ),
        "state": "reserved_not_materialized",
        "allowed_file_roles": list(ALLOWED_FILE_ROLES),
        "reservation_sha256": None,
    }
    evidence_root["reservation_sha256"] = finalized_self_hash(
        evidence_root,
        "reservation_sha256",
    )
    command_records["cmd-preflight"]["authorized_preflight_root_hash"] = evidence_root[
        "reservation_sha256"
    ]
    command_records["cmd-preflight"] = _with_rehashed(
        command_records["cmd-preflight"],
        "command_record_sha256",
    )
    manifest["command_record_hashes"]["cmd-preflight"] = command_records[
        "cmd-preflight"
    ]["command_record_sha256"]
    manifest["preflight_evidence_root_reservation_sha256"] = evidence_root[
        "reservation_sha256"
    ]
    manifest = _with_rehashed(manifest, "manifest_sha256")
    record: JsonObject = {
        "schema_version": "ims-deadlock/g6b-preflight-authorization/v1",
        "authorization_id": "preflight-authorization-test",
        "capability": "target_certification_preflight",
        "authorized": True,
        "bundle_id": _TEST_BUNDLE_ID,
        "case_unit_ids": ["case-a"],
        "sealed_bundle_manifest_hash": manifest["sealed_bundle_manifest_hash"],
        "runtime_lock_sha256": "6" * 64,
        "allowed_entrypoint": "ims_deadlock.g6b_target_preflight.main",
        "allowed_command_manifest_hash": manifest["manifest_sha256"],
        "allowed_operations": list(ALLOWED_OPERATIONS),
        "allowed_output_schemas": list(ALLOWED_OUTPUT_SCHEMA_IDS),
        "forbidden_calls": list(contracts.PREFLIGHT_FORBIDDEN_CALLS),
        "forbidden_side_effects": list(contracts.PREFLIGHT_FORBIDDEN_SIDE_EFFECTS),
        "resource_budget": {
            "max_wall_clock_seconds": "60",
            "max_cpu_seconds": "60",
            "max_memory_bytes": 1024,
            "max_storage_bytes": 1024,
            "max_states_per_case": 100,
            "max_transitions_per_case": 1000,
            "max_cases": 1,
            "max_workers": 1,
        },
        "stop_conditions": [
            "all_declared_cases_terminal-v1",
            "capability_leak-v1",
            "identity_drift-v1",
            "resource_budget_exceeded-v1",
            "unexpected_file-v1",
        ],
        "preflight_evidence_root": evidence_root,
        "review_artifact_hash": "7" * 64,
        "issued_at_utc": "2030-01-01T00:00:00Z",
        "invalidated_by_identity_drift": False,
        "authorization_sha256": None,
    }
    record["authorization_sha256"] = finalized_self_hash(
        record,
        "authorization_sha256",
    )
    return record, manifest, command_records


def _reseal_preflight_root_links(
    record: JsonObject,
    manifest: JsonObject,
    command_records: dict[str, JsonObject],
) -> None:
    evidence_root = record["preflight_evidence_root"]
    evidence_root["reservation_sha256"] = None
    evidence_root["reservation_sha256"] = finalized_self_hash(
        evidence_root,
        "reservation_sha256",
    )
    command_record = command_records["cmd-preflight"]
    command_record["authorized_preflight_root_hash"] = evidence_root[
        "reservation_sha256"
    ]
    command_records["cmd-preflight"] = _with_rehashed(
        command_record,
        "command_record_sha256",
    )
    manifest["command_record_hashes"]["cmd-preflight"] = command_records[
        "cmd-preflight"
    ]["command_record_sha256"]
    manifest["preflight_evidence_root_reservation_sha256"] = evidence_root[
        "reservation_sha256"
    ]
    manifest.update(_with_rehashed(manifest, "manifest_sha256"))
    record["allowed_command_manifest_hash"] = manifest["manifest_sha256"]
    record.update(_with_rehashed(record, "authorization_sha256"))


def _valid_quantitative_command_record(
    command_id: str = "cmd-quantitative",
    scope: JsonObject | None = None,
) -> JsonObject:
    authorized_scope = _quantitative_scope_fixture() if scope is None else scope
    record: JsonObject = {
        "command_id": command_id,
        "capability": "quantitative_execution",
        "executable_sha256": "0" * 64,
        "entrypoint": "ims_deadlock.g6b_quantitative_runner.main",
        "argv_tokens": [
            {"token_kind": "literal", "value": "g6b-quantitative"},
            {
                "token_kind": "placeholder",
                "placeholder_code": "method_scope_manifest",
            },
        ],
        "working_directory_repo_relative": ".",
        "environment_variable_allowlist": {
            "PYTHONDONTWRITEBYTECODE": {"token_kind": "literal", "value": "1"},
            "PYTHONPATH": {
                "token_kind": "placeholder",
                "placeholder_code": "repo_source_root",
            },
        },
        "stdin_policy": "closed",
        "authorized_case_unit_ids": ["case-a"],
        "authorized_method_observation_ids": list(
            authorized_scope["method_observation_ids"]
        ),
        "authorized_run_roles": ["primary"],
        "authorized_output_root_reservation_hashes": dict(
            authorized_scope["output_root_reservations"]
        ),
        "command_record_sha256": None,
    }
    record["command_record_sha256"] = finalized_self_hash(
        record,
        "command_record_sha256",
    )
    return record


def _valid_quantitative_command_manifest(
    scope: JsonObject | None = None,
) -> tuple[JsonObject, dict[str, JsonObject]]:
    authorized_scope = _quantitative_scope_fixture() if scope is None else scope
    command = _valid_quantitative_command_record(scope=authorized_scope)
    manifest: JsonObject = {
        "schema_version": ("ims-deadlock/g6b-quantitative-allowed-command-manifest/v1"),
        "manifest_id": "manifest-q",
        "capability": "quantitative_execution",
        "source_head": "a" * 40,
        "source_tree_hash": "b" * 40,
        "sealed_bundle_manifest_hash": _synthetic_hash("quant:sealed-bundle"),
        "target_certification_batch_manifest_hash": _synthetic_hash(
            "quant:preflight-batch"
        ),
        "authorized_scope_sha256": canonical_sha256_v2(authorized_scope),
        "same_target_lock_hashes": dict(authorized_scope["same_target_lock_hashes"]),
        "output_root_reservation_hashes": dict(
            authorized_scope["output_root_reservations"]
        ),
        "declared_command_ids": ["cmd-quantitative"],
        "command_record_hashes": {"cmd-quantitative": command["command_record_sha256"]},
        "command_count": 1,
        "placeholder_vocabulary": list(contracts.QUANTITATIVE_PLACEHOLDER_CODES),
        "environment_variable_name_allowlist": [
            "PYTHONDONTWRITEBYTECODE",
            "PYTHONPATH",
        ],
        "wildcard_scope_allowed": False,
        "created_at_utc": "2026-08-01T00:00:00Z",
        "manifest_sha256": None,
    }
    manifest["manifest_sha256"] = finalized_self_hash(manifest, "manifest_sha256")
    return manifest, {"cmd-quantitative": command}


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
        "output_root_reservation_sha256": {
            "projection_schema_version": "v1",
            "bundle_id": "bundle-a",
            "case_unit_id": "case-a",
            "method_observation_id": "method-a",
            "run_role": "primary",
            "logical_root_id": "root-a",
            "repo_relative_posix_path": (
                "artifacts/g6b/quantitative/bundle-a/case-a/method-a/primary"
            ),
            "reserved": True,
            "materialized": False,
            "reservation_sha256": None,
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


def test_public_constants_freeze_exact_spec_vocabularies() -> None:
    assert CAPABILITY_NAMES == (
        "case_construction",
        "retired_authority_fingerprint_normalization",
        "target_certification_preflight",
        "quantitative_execution",
    )
    assert CAPABILITY_FIELDS == (
        "case_construction_authorized",
        "retired_authority_fingerprint_normalization_authorized",
        "target_certification_preflight_authorized",
        "quantitative_execution_authorized",
    )
    assert FINGERPRINT_DIMENSIONS == (
        "case_content_sha256",
        "state_snapshot_sha256",
        "route_signature_sha256",
        "parameter_tuple_sha256",
        "random_stream_manifest_sha256",
        "output_root_reservation_sha256",
        "sealed_prediction_sha256",
        "metric_schema_sha256",
    )
    assert PROJECTION_KINDS == (
        "controlled_schema",
        "provenance_containment",
        "random_process",
        "semantic_content",
    )
    assert COMPARISON_POLICIES == (
        "controlled_schema_reuse",
        "disjoint_random_substreams",
        "provenance_containment_only",
        "strict_semantic_distinctness",
    )
    assert BUNDLE_STATES == (
        "SPEC_DRAFTED",
        "ROW_FAMILY_BUNDLE_IMPLEMENTED",
        "DATA_ONLY_VALIDATION_PASSED",
        "ADVERSARIAL_ROW_FAMILY_REVIEW_PASSED",
        "CASE_CONSTRUCTION_PLAN_APPROVED",
        "CASE_INPUTS_SEALED_NO_EXECUTION",
        "RETIRED_AUTHORITY_NORMALIZATION_AUTHORIZATION_RECORDED",
        "RETIRED_AUTHORITY_NORMALIZATION_COMPLETE",
        "INPUT_OVERLAP_AUDIT_COMPLETE",
        "TARGET_CERTIFICATION_RUNTIME_LOCK_RECORDED",
        "TARGET_CERTIFICATION_PREFLIGHT_AUTHORIZATION_RECORDED",
        "TARGET_CERTIFICATION_PREFLIGHT_COMPLETE",
        "QUANTITATIVE_RUNTIME_LOCK_COMPLETE",
        "QUANTITATIVE_EXECUTION_AUTHORIZATION_RECORDED",
        "QUANTITATIVE_EXECUTION_RECORDED",
        "BUNDLE_CLOSED_WITH_FAILURES",
        "BUNDLE_ELIGIBLE_FOR_BOUNDARY_REVIEW",
    )
    assert contracts.CASE_UNIT_STATES == (
        "CASE_UNIT_PLANNED",
        "CASE_UNIT_SEALED_NO_EXECUTION",
        "CASE_UNIT_OVERLAP_PASSED",
        "CASE_UNIT_OVERLAP_REFUSED",
        "CASE_UNIT_TARGET_PREFLIGHT_AUTHORIZED",
        "CASE_UNIT_TARGET_CERTIFIED",
        "CASE_UNIT_TARGET_REFUSED",
        "CASE_UNIT_RUNTIME_LOCKED",
        "CASE_UNIT_QUANT_AUTHORIZED",
        "CASE_UNIT_EXECUTED",
        "CASE_UNIT_RETAINED_REFUSED",
        "CASE_UNIT_REVISED_SUPERSEDED",
    )
    assert contracts.METHOD_OBSERVATION_STATES == (
        "METHOD_PLANNED",
        "METHOD_SEALED_NO_OUTPUT",
        "METHOD_TARGET_MATCH_VERIFIED",
        "METHOD_TARGET_MISMATCH_REFUSED",
        "METHOD_RUNTIME_READY",
        "METHOD_AUTHORIZED",
        "METHOD_EXECUTED",
        "METHOD_RETAINED_REFUSED",
        "METHOD_REVISED_SUPERSEDED",
    )
    assert contracts.DIMENSION_STATUS_VALUES == (
        "direct_stored",
        "derived_by_versioned_normalizer",
        "inherited_from_authority",
        "not_applicable_by_protocol",
        "not_applicable_retired_stage",
        "unreconstructable_refuse",
    )
    assert COMPARISON_STATUS_VALUES == (
        "pass_distinct",
        "overlap_hit",
        "controlled_reuse_pass",
        "disjoint_stream_pass",
        "not_applicable_by_protocol_pass",
        "containment_separation_pass",
        "inherited_compared",
        "missing_source",
        "unreconstructable",
        "normalizer_error",
        "semantic_lineage_ambiguous",
    )
    assert contracts.PREFLIGHT_PLACEHOLDER_CODES == (
        "case_scope_manifest",
        "preflight_authorization",
        "preflight_evidence_root",
        "python_runtime",
        "repo_source_root",
        "sealed_bundle_manifest",
    )
    assert contracts.ALLOWED_ENVIRONMENT_VARIABLE_NAMES == (
        "PYTHONDONTWRITEBYTECODE",
        "PYTHONPATH",
    )
    assert contracts.SELECTOR_KINDS == (
        "exact_pointer_set",
        "prefix_set",
        "element_pointer_pattern_set",
        "raw_bytes_only",
    )
    assert contracts.ALLOWED_USE_VALUES == (
        "authority_identity",
        "source_hash_validation",
        "case_content_projection",
        "prediction_projection",
        "metric_projection",
        "random_stream_projection",
        "lineage_link",
        "method_stage_projection",
        "output_root_source_equality_validation",
        "output_root_containment_projection",
    )
    assert contracts.PREFLIGHT_COMMAND_MANIFEST_REQUIRED_FIELDS == (
        "schema_version",
        "manifest_id",
        "capability",
        "source_head",
        "source_tree_hash",
        "sealed_bundle_manifest_hash",
        "input_overlap_report_sha256",
        "preflight_evidence_root_reservation_sha256",
        "declared_command_ids",
        "command_record_hashes",
        "command_count",
        "placeholder_vocabulary",
        "environment_variable_name_allowlist",
        "wildcard_scope_allowed",
        "created_at_utc",
        "manifest_sha256",
    )
    assert contracts.PREFLIGHT_COMMAND_RECORD_REQUIRED_FIELDS == (
        "command_id",
        "capability",
        "executable_sha256",
        "entrypoint",
        "argv_tokens",
        "working_directory_repo_relative",
        "environment_variable_allowlist",
        "stdin_policy",
        "authorized_case_unit_ids",
        "authorized_preflight_root_hash",
        "command_record_sha256",
    )
    assert contracts.QUANTITATIVE_COMMAND_MANIFEST_REQUIRED_FIELDS == (
        "schema_version",
        "manifest_id",
        "capability",
        "source_head",
        "source_tree_hash",
        "sealed_bundle_manifest_hash",
        "target_certification_batch_manifest_hash",
        "authorized_scope_sha256",
        "same_target_lock_hashes",
        "output_root_reservation_hashes",
        "declared_command_ids",
        "command_record_hashes",
        "command_count",
        "placeholder_vocabulary",
        "environment_variable_name_allowlist",
        "wildcard_scope_allowed",
        "created_at_utc",
        "manifest_sha256",
    )
    assert contracts.QUANTITATIVE_COMMAND_RECORD_REQUIRED_FIELDS == (
        "command_id",
        "capability",
        "executable_sha256",
        "entrypoint",
        "argv_tokens",
        "working_directory_repo_relative",
        "environment_variable_allowlist",
        "stdin_policy",
        "authorized_case_unit_ids",
        "authorized_method_observation_ids",
        "authorized_run_roles",
        "authorized_output_root_reservation_hashes",
        "command_record_sha256",
    )


def test_preflight_and_quantitative_constants_use_exact_spec_arrays() -> None:
    assert ALLOWED_OPERATIONS == (
        "load_sealed_case_input",
        "verify_input_hashes",
        "enumerate_complete_bounded_stable_lts",
        "verify_lts_provenance",
        "partition_typed_terminal_stopping_classes",
        "verify_rate_manifest",
        "verify_policy_declaration",
        "verify_selected_target_identity",
        "certify_global_absorption_domain",
        "emit_target_certificate_or_refusal",
        "emit_command_capture",
        "emit_filesystem_and_hash_manifests",
        "append_preflight_failure_ledger",
        "validate_preflight_artifacts_data_only",
    )
    assert ALLOWED_OUTPUT_SCHEMA_IDS == (
        "ims-deadlock/g6b-command-capture/v1",
        "ims-deadlock/g6b-filesystem-manifest/v1",
        "ims-deadlock/g6b-hash-manifest/v1",
        "ims-deadlock/g6b-preflight-failure-ledger-entry/v1",
        "ims-deadlock/g6b-target-certificate/v1",
        "ims-deadlock/g6b-target-certification-batch-manifest/v1",
        "ims-deadlock/g6b-target-certification-case-result/v1",
        "ims-deadlock/g6b-target-refusal/v1",
    )
    assert ALLOWED_FILE_ROLES == (
        "batch_manifest",
        "command_transcript",
        "exit_code_capture",
        "failure_ledger_entry",
        "filesystem_after_manifest",
        "filesystem_before_manifest",
        "hash_manifest",
        "per_case_result",
        "stderr_capture",
        "target_certificate",
        "target_refusal",
    )
    assert contracts.FILE_ROLE_TO_SCHEMA_ID == MappingProxyType(
        {
            "batch_manifest": (
                "ims-deadlock/g6b-target-certification-batch-manifest/v1"
            ),
            "command_transcript": "ims-deadlock/g6b-command-capture/v1",
            "exit_code_capture": "ims-deadlock/g6b-command-capture/v1",
            "failure_ledger_entry": (
                "ims-deadlock/g6b-preflight-failure-ledger-entry/v1"
            ),
            "filesystem_after_manifest": "ims-deadlock/g6b-filesystem-manifest/v1",
            "filesystem_before_manifest": "ims-deadlock/g6b-filesystem-manifest/v1",
            "hash_manifest": "ims-deadlock/g6b-hash-manifest/v1",
            "per_case_result": ("ims-deadlock/g6b-target-certification-case-result/v1"),
            "stderr_capture": "ims-deadlock/g6b-command-capture/v1",
            "target_certificate": "ims-deadlock/g6b-target-certificate/v1",
            "target_refusal": "ims-deadlock/g6b-target-refusal/v1",
        }
    )
    assert ALLOWED_PREFLIGHT_PROJECT_IMPORTS == (
        "ims_deadlock.g6b_target_preflight",
        "ims_deadlock.g6b_target_artifacts",
        "ims_deadlock.g6b_input_loader",
        "ims_deadlock.g6b_lts",
        "ims_deadlock.g6b_target_certificate",
        "ims_deadlock.g6b_canonical_json",
        "ims_deadlock.g6b_governance",
        "ims_deadlock.model",
        "ims_deadlock.engine",
        "ims_deadlock.certificates",
    )
    assert ALLOWED_PREFLIGHT_WRITER_SYMBOLS == (
        "ims_deadlock.g6b_target_artifacts.write_certificate_record",
        "ims_deadlock.g6b_target_artifacts.write_refusal_record",
        "ims_deadlock.g6b_target_artifacts.write_batch_manifest",
        "ims_deadlock.g6b_target_artifacts.write_capture_record",
        "ims_deadlock.g6b_target_artifacts.write_filesystem_manifest",
        "ims_deadlock.g6b_target_artifacts.write_hash_manifest",
        "ims_deadlock.g6b_target_artifacts.append_failure_ledger",
    )
    assert contracts.PREFLIGHT_FORBIDDEN_CALLS == (
        "ims_deadlock.g4_instances.derive_absorbing_ctmc",
        "ims_deadlock.ctmc.AbsorbingCTMC.solve",
        "ims_deadlock.engine.simulate",
        "ims_deadlock.g4_protocol.run_after_freeze",
        "ims_deadlock.g4_protocol.main",
        "ims_deadlock.g5_scoring.score_case",
        "ims_deadlock.g5_scoring.score_run",
        "ims_deadlock.g5_scoring.main",
        "ims_deadlock.historical_replay.main",
    )
    assert contracts.PREFLIGHT_FORBIDDEN_RESULT_FIELDS == (
        "committor",
        "completion_probability",
        "deadlock_probability",
        "mean_absorption_time",
        "sensitivity",
        "doob_h",
        "des_trajectory",
        "des_estimate",
        "metric_observations",
        "theorem_support",
        "theorem_falsification",
        "scientific_score",
        "science_summary",
        "quantitative_output_root",
    )
    assert contracts.PREFLIGHT_FORBIDDEN_SIDE_EFFECTS == (
        "write_outside_preflight_root",
        "materialize_quantitative_root",
        "write_python_bytecode",
        "mutate_retired_evidence",
        "mutate_sealed_input",
        "invoke_network",
        "invoke_subprocess_outside_manifest",
        "advance_quantitative_state",
        "write_scientific_summary",
    )
    assert contracts.PREFLIGHT_FORBIDDEN_IMPORTS == (
        "ims_deadlock.cases",
        "ims_deadlock.ctmc",
        "ims_deadlock.g4_instances",
        "ims_deadlock.g4_protocol",
        "ims_deadlock.g5_scoring",
        "ims_deadlock.historical_replay",
        "ims_deadlock.confirmation",
        "ims_deadlock.cli",
    )
    assert QUANTITATIVE_PLACEHOLDER_CODES == (
        "case_input",
        "method_scope_manifest",
        "output_root",
        "python_runtime",
        "quantitative_authorization",
        "repo_source_root",
        "sealed_bundle_manifest",
        "target_certificate_manifest",
    )
    assert contracts.CROSS_GATE_REFUSAL_CODES == (
        "batch_incomplete",
        "canonicalization_violation",
        "missing_hash",
        "outcome_leakage",
        "runtime_identity_drift",
        "sealed_input_drift",
        "self_hash_mismatch",
    )
    assert contracts.CONSTRUCTION_REFUSAL_CODES == (
        "output_root_reuse_or_materialized",
        "subject_id_contaminated_projection",
        "unauthorized_case_creation_attempt",
        "unclassified_scientific_input",
    )
    assert contracts.NORMALIZATION_REFUSAL_CODES == (
        "capability_call_violation",
        "capability_import_violation",
        "duplicate_lineage_miscount",
        "missing_normalization_authorization",
        "missing_retired_authority",
        "retired_authority_hash_mismatch",
        "retired_normalizer_error",
        "retired_projection_unreconstructable",
        "source_field_read_violation",
        "unauthorized_retired_normalization_attempt",
    )
    assert contracts.OVERLAP_REFUSAL_CODES == (
        "metric_reuse_unauthorized",
        "overlap_hit",
        "output_root_reuse_or_materialized",
        "prediction_semantic_reuse",
        "random_stream_disjointness_unproved",
        "random_stream_overlap",
        "rename_or_cosmetic_shift_detected",
        "semantic_identity_reuse",
        "semantic_lineage_ambiguous",
        "subject_id_contaminated_projection",
        "unclassified_scientific_input",
    )
    assert contracts.PREFLIGHT_REFUSAL_CODES == (
        "capability_call_violation",
        "capability_import_violation",
        "certificate_schema_violation",
        "command_scope_violation",
        "filesystem_scope_violation",
        "incomplete_stable_lts",
        "non_almost_sure_absorption_domain",
        "policy_filter_drift",
        "rate_manifest_drift",
        "selected_target_drift",
        "state_bound_truncation",
        "unauthorized_target_certification_attempt",
        "unavailable_transition_branch",
        "unexpected_preflight_side_effect",
        "unverified_lts_provenance",
    )
    assert contracts.QUANTITATIVE_REFUSAL_CODES == (
        "exact_des_target_mismatch",
        "failed_negative_control",
        "output_root_reuse_or_materialized",
        "quantitative_scope_violation",
        "retry_stop_policy_violation",
        "same_target_lock_stale",
        "unauthorized_quantitative_execution_attempt",
    )


def test_public_maps_are_mappingproxy_backed() -> None:
    maps = (
        contracts.DIMENSION_SUBJECTS,
        contracts.DIMENSION_PROJECTION_KINDS,
        contracts.DIMENSION_POLICIES,
        contracts.FILE_ROLE_TO_SCHEMA_ID,
        contracts.REFUSAL_CODE_GROUPS,
    )
    for mapping in maps:
        assert isinstance(mapping, MappingProxyType)


def test_spec_17_3_06_schema_fingerprint_projection_relations() -> None:
    for dimension in FINGERPRINT_DIMENSIONS:
        validate_subject_free_projection(
            dimension, _projection_for_dimension(dimension)
        )
        missing_payload = _projection_for_dimension(dimension)
        missing_payload.pop(next(iter(missing_payload)))
        with pytest.raises(SchemaContractError, match="missing_key"):
            validate_subject_free_projection(dimension, missing_payload)
        extra_payload = _projection_for_dimension(dimension)
        extra_payload["unknown_scientific_input"] = "not classified"
        with pytest.raises(
            SchemaContractError,
            match="unclassified_scientific_input|subject_id_contaminated_projection",
        ):
            validate_subject_free_projection(dimension, extra_payload)


def test_case_construction_estimand_scope_allows_only_two_predeclared_roles() -> None:
    sealed_prediction = _projection_for_dimension("sealed_prediction_sha256")
    sealed_prediction["directional_hypotheses"] = [
        {
            "hypothesis_role": f"hypothesis-{index}",
            "statement": "predeclared discovery-only hypothesis",
            "direction": "case_specific_predeclared",
            "estimand_id": estimand_id,
            "scope_code": "single_case_discovery_only",
            "falsifier_roles": [],
        }
        for index, estimand_id in enumerate(_ALLOWED_G6B_ESTIMAND_IDS)
    ]
    validate_subject_free_projection("sealed_prediction_sha256", sealed_prediction)

    metric_schema = _projection_for_dimension("metric_schema_sha256")
    metric_schema["metric_entries"] = [
        {
            "metric_id": f"metric-{index}",
            "estimand_id": estimand_id,
            "unit": "probability",
            "domain": "closed_unit_interval",
            "direction": "case_specific_predeclared",
            "aggregation_rule_id": "aggregation-v1",
            "censoring_rule_id": "censoring-v1",
            "failure_rule_id": "failure-v1",
            "scoring_rule_id": "scoring-v1",
            "applicability_rule": "target_certified_and_same_target_locked_v1",
        }
        for index, estimand_id in enumerate(_ALLOWED_G6B_ESTIMAND_IDS)
    ]
    validate_subject_free_projection("metric_schema_sha256", metric_schema)


@pytest.mark.parametrize(
    ("dimension", "mutate"),
    [
        pytest.param(
            "sealed_prediction_sha256",
            lambda payload: payload.update(
                {"estimand_id": _ALLOWED_G6B_ESTIMAND_IDS[0]}
            ),
            id="root",
        ),
        pytest.param(
            "sealed_prediction_sha256",
            lambda payload: payload["falsifiers"].append(
                {
                    "falsifier_role": "f1",
                    "estimand_id": _ALLOWED_G6B_ESTIMAND_IDS[0],
                }
            ),
            id="sibling",
        ),
        pytest.param(
            "sealed_prediction_sha256",
            lambda payload: payload["directional_hypotheses"].append(
                {
                    "hypothesis_role": "h1",
                    "result": {"estimand_id": _ALLOWED_G6B_ESTIMAND_IDS[0]},
                }
            ),
            id="nested_result",
        ),
        pytest.param(
            "random_stream_manifest_sha256",
            lambda payload: payload.update(
                {"estimand_id": _ALLOWED_G6B_ESTIMAND_IDS[0]}
            ),
            id="runtime_projection",
        ),
        pytest.param(
            "case_content_sha256",
            lambda payload: payload.update(
                {"certificate": {"estimand_id": _ALLOWED_G6B_ESTIMAND_IDS[0]}}
            ),
            id="certificate_projection",
        ),
        pytest.param(
            "metric_schema_sha256",
            lambda payload: payload.setdefault("aggregation_rules", []).append(
                {
                    "rule_id": "agg",
                    "details": {"estimand_id": _ALLOWED_G6B_ESTIMAND_IDS[0]},
                }
            ),
            id="arbitrary_nested",
        ),
        pytest.param(
            "metric_schema_sha256",
            lambda payload: payload.setdefault("metric_entries", []).append(
                {"metric_id": "m1", "estimand_id": "theta-post-outcome-drift"}
            ),
            id="wrong_value_code",
        ),
    ],
)
def test_case_construction_estimand_scope_rejects_forbidden_placements(
    dimension: str, mutate: Any
) -> None:
    payload = _projection_for_dimension(dimension)
    mutate(payload)

    with pytest.raises(SchemaContractError, match="estimand_id_scope_violation"):
        validate_subject_free_projection(dimension, payload)


@pytest.mark.parametrize(
    ("dimension", "mutate"),
    [
        pytest.param(
            "sealed_prediction_sha256",
            lambda payload, value: payload["directional_hypotheses"].append(
                {
                    "hypothesis_role": "hypothesis-invalid-type",
                    "statement": "predeclared discovery-only hypothesis",
                    "direction": "case_specific_predeclared",
                    "estimand_id": value,
                    "scope_code": "single_case_discovery_only",
                    "falsifier_roles": [],
                }
            ),
            id="directional_hypothesis",
        ),
        pytest.param(
            "metric_schema_sha256",
            lambda payload, value: payload["metric_entries"].append(
                {
                    "metric_id": "metric-invalid-type",
                    "estimand_id": value,
                    "unit": "probability",
                    "domain": "closed_unit_interval",
                    "direction": "case_specific_predeclared",
                    "aggregation_rule_id": "aggregation-v1",
                    "censoring_rule_id": "censoring-v1",
                    "failure_rule_id": "failure-v1",
                    "scoring_rule_id": "scoring-v1",
                    "applicability_rule": "target_certified_and_same_target_locked_v1",
                }
            ),
            id="metric_entry",
        ),
    ],
)
@pytest.mark.parametrize(
    "estimand_id",
    [
        pytest.param([], id="list"),
        pytest.param({}, id="dict"),
        pytest.param(1, id="int"),
        pytest.param(None, id="null"),
        pytest.param(True, id="bool"),
        pytest.param(1.25, id="float"),
        pytest.param("theta-post-outcome-drift", id="wrong_string"),
    ],
)
def test_case_construction_estimand_scope_rejects_non_string_value_codes(
    dimension: str, mutate: Any, estimand_id: Any
) -> None:
    payload = _projection_for_dimension(dimension)
    mutate(payload, estimand_id)

    with pytest.raises(SchemaContractError, match="estimand_id_scope_violation"):
        validate_subject_free_projection(dimension, payload)


def test_random_stream_projection_accepts_exact_stochastic_branch_only() -> None:
    validate_subject_free_projection(
        "random_stream_manifest_sha256",
        _projection_for_dimension("random_stream_manifest_sha256"),
    )
    validate_subject_free_projection(
        "random_stream_manifest_sha256",
        {
            "projection_schema_version": "v1",
            "applicability_status": "applicable",
            "method_role": "des_companion",
            "prng_family": "Philox",
            "prng_version": "v1",
            "seed_root_commitment": "a" * 64,
            "seed_derivation_rule": "rule-v1",
            "substream_allocation": [],
            "replicate_plan": {"planned_replicates": 1},
            "sampling_plan": {"draw_budget_per_replication": 1},
        },
    )
    invalid_exact = _projection_for_dimension("random_stream_manifest_sha256")
    invalid_exact["method_role"] = "des_companion"
    invalid_exact["applicability_status"] = "applicable"
    with pytest.raises(SchemaContractError, match="random_stream_branch_mismatch"):
        validate_subject_free_projection("random_stream_manifest_sha256", invalid_exact)
    invalid_stochastic: JsonObject = {
        "projection_schema_version": "v1",
        "applicability_status": "not_applicable_by_protocol",
        "method_role": "exact_companion",
        "prng_family": "Philox",
        "prng_version": "v1",
        "seed_root_commitment": "a" * 64,
        "seed_derivation_rule": "rule-v1",
        "substream_allocation": [],
        "replicate_plan": {"planned_replicates": 1},
        "sampling_plan": {"draw_budget_per_replication": 1},
    }
    with pytest.raises(SchemaContractError, match="random_stream_branch_mismatch"):
        validate_subject_free_projection(
            "random_stream_manifest_sha256",
            invalid_stochastic,
        )
    invalid_stochastic_value: JsonObject = {
        "projection_schema_version": "v1",
        "applicability_status": "banana",
        "method_role": "other",
        "prng_family": "Philox",
        "prng_version": "v1",
        "seed_root_commitment": "a" * 64,
        "seed_derivation_rule": "rule-v1",
        "substream_allocation": [],
        "replicate_plan": {"planned_replicates": 1},
        "sampling_plan": {"draw_budget_per_replication": 1},
    }
    with pytest.raises(SchemaContractError, match="random_stream_branch_mismatch"):
        validate_subject_free_projection(
            "random_stream_manifest_sha256",
            invalid_stochastic_value,
        )


def test_output_root_projection_allows_only_its_specified_coordinates() -> None:
    projection = _projection_for_dimension("output_root_reservation_sha256")
    validate_subject_free_projection("output_root_reservation_sha256", projection)
    projection["author"] = "reviewer"
    with pytest.raises(SchemaContractError, match="unclassified_scientific_input"):
        validate_subject_free_projection("output_root_reservation_sha256", projection)


def test_subject_free_projection_rejects_nested_governance_contamination() -> None:
    projection = _projection_for_dimension("sealed_prediction_sha256")
    projection["scoring_rule"]["author"] = "reviewer"
    with pytest.raises(SchemaContractError, match="subject_id_contaminated_projection"):
        validate_subject_free_projection("sealed_prediction_sha256", projection)


@pytest.mark.parametrize(
    "contaminant",
    [
        "bundle_id",
        "case_unit_id",
        "method_observation_id",
        "method_companion_group_id",
        "filename",
        "repo_path",
        "repo_relative_path",
        "display_name",
        "author",
        "timestamp",
        "review_id",
        "g6b_provenance_label",
    ],
)
def test_subject_free_projection_rejects_governance_contamination(
    contaminant: str,
) -> None:
    projection = _projection_for_dimension("case_content_sha256")
    projection[contaminant] = "contaminated"
    with pytest.raises(SchemaContractError, match="subject_id_contaminated_projection"):
        validate_subject_free_projection("case_content_sha256", projection)


def test_exact_des_and_declared_subject_maps_are_accounted_once() -> None:
    validate_declared_terminal_partition(
        ["case-a"],
        {"certified": ["case-a"], "refused": [], "pending": []},
        {"certified": 1, "refused": 0, "pending": 0},
    )
    with pytest.raises(SchemaContractError, match="terminal_partition_incomplete"):
        validate_declared_terminal_partition(
            ["case-a"],
            {
                "certified": ["case-a-des", "case-a-exact"],
                "refused": [],
                "pending": [],
            },
            {"certified": 2, "refused": 0, "pending": 0},
        )
    validate_exact_keys(
        {"method-a": "hash-a", "method-b": "hash-b"},
        {"method-a", "method-b"},
        label="method_record_hashes",
    )
    with pytest.raises(SchemaContractError, match="missing_key"):
        validate_exact_keys(
            {"method-a": "hash-a"},
            {"method-a", "method-b"},
            label="method_record_hashes",
        )
    validate_exact_keys(
        {"group-a": "hash-a"},
        {"group-a"},
        label="companion_group_record_hashes",
    )
    with pytest.raises(SchemaContractError, match="unexpected_key"):
        validate_exact_keys(
            {"group-a": "hash-a", "group-b": "hash-b"},
            {"group-a"},
            label="companion_group_record_hashes",
        )


def test_spec_17_3_11_schema_unknown_scientific_inputs_refuse() -> None:
    projection: JsonObject = {
        "projection_schema_version": "v1",
        "input_mode": "model_generated_lts",
        "state_payload_schema_version": "state-v1",
        "state_payload": {"states": ["s0"]},
    }
    validate_subject_free_projection("state_snapshot_sha256", projection)
    projection["state_space_hash"] = "a" * 64
    with pytest.raises(SchemaContractError, match="state_space_hash_substitution"):
        validate_subject_free_projection("state_snapshot_sha256", projection)


def test_spec_17_3_25_schema_runtime_locks_have_no_downstream_authorization() -> None:
    validate_exact_keys(
        {
            "schema_version": "v1",
            "runtime_lock_id": "lock-a",
            "source_head": "a" * 40,
        },
        {"schema_version", "runtime_lock_id", "source_head"},
        label="preflight_runtime_lock",
    )
    with pytest.raises(SchemaContractError, match="unexpected_key"):
        validate_exact_keys(
            {
                "schema_version": "v1",
                "runtime_lock_id": "lock-a",
                "source_head": "a" * 40,
                "authorization_sha256": "b" * 64,
            },
            {"schema_version", "runtime_lock_id", "source_head"},
            label="preflight_runtime_lock",
        )


def test_spec_17_3_26_schema_preflight_authorization_exact_scope_and_commands() -> None:
    manifest, records = _valid_command_manifest()
    validate_command_manifest(
        manifest,
        records,
        capability="target_certification_preflight",
    )
    manifest["schema_version"] = "ims-deadlock/g6b-preflight-command/v0"
    with pytest.raises(SchemaContractError, match="schema_version_drift"):
        validate_command_manifest(
            manifest,
            records,
            capability="target_certification_preflight",
        )
    manifest, records = _valid_command_manifest()
    manifest["declared_command_ids"] = ["cmd-a", "cmd-b"]
    manifest["command_record_hashes"] = {"cmd-a": "2" * 64, "cmd-b": "3" * 64}
    manifest["command_count"] = 2
    with pytest.raises(SchemaContractError, match="preflight_command_count"):
        validate_command_manifest(
            manifest,
            {
                "cmd-a": _valid_command_record("cmd-a"),
                "cmd-b": _valid_command_record("cmd-b"),
            },
            capability="target_certification_preflight",
        )
    manifest, records = _valid_command_manifest()
    manifest["command_count"] = True
    with pytest.raises(SchemaContractError, match="command_count_type"):
        validate_command_manifest(
            manifest,
            records,
            capability="target_certification_preflight",
        )
    manifest, records = _valid_command_manifest()
    records["cmd-preflight"]["argv_tokens"].append(
        {"token_kind": "literal", "value": "case-*"}
    )
    with pytest.raises(SchemaContractError, match="wildcard_scope"):
        validate_command_manifest(
            manifest,
            records,
            capability="target_certification_preflight",
        )
    manifest, records = _valid_command_manifest()
    records["cmd-preflight"]["argv_tokens"].append(
        {"token_kind": "literal", "value": "cmd > out"}
    )
    with pytest.raises(SchemaContractError, match="shell_syntax"):
        validate_command_manifest(
            manifest,
            records,
            capability="target_certification_preflight",
        )
    for token, code in (
        ("case-?", "wildcard_scope"),
        ("case-[ab]", "wildcard_scope"),
        ("cmd; rm x", "shell_syntax"),
        ("cmd & bg", "shell_syntax"),
    ):
        manifest, records = _valid_command_manifest()
        records["cmd-preflight"]["argv_tokens"].append(
            {"token_kind": "literal", "value": token}
        )
        with pytest.raises(SchemaContractError, match=code):
            validate_command_manifest(
                manifest,
                records,
                capability="target_certification_preflight",
            )
    manifest, records = _valid_command_manifest()
    records["cmd-preflight"]["environment_variable_allowlist"][
        "PYTHONDONTWRITEBYTECODE"
    ] = {"token_kind": "literal", "value": "0"}
    with pytest.raises(SchemaContractError, match="environment_resolution_drift"):
        validate_command_manifest(
            manifest,
            records,
            capability="target_certification_preflight",
        )
    manifest, records = _valid_command_manifest()
    records["cmd-preflight"]["environment_variable_allowlist"]["PYTHONPATH"] = {
        "token_kind": "literal",
        "value": "src",
    }
    with pytest.raises(SchemaContractError, match="environment_resolution_drift"):
        validate_command_manifest(
            manifest,
            records,
            capability="target_certification_preflight",
        )
    for bad_token in ("case-*", "case-prefix/", "$(python)", "`python`"):
        manifest, records = _valid_command_manifest()
        records["cmd-preflight"]["argv_tokens"].append(
            {"token_kind": "literal", "value": bad_token}
        )
        expected = (
            "wildcard_scope"
            if bad_token in {"case-*", "case-prefix/"}
            else ("shell_syntax")
        )
        with pytest.raises(SchemaContractError, match=expected):
            validate_command_manifest(
                manifest,
                records,
                capability="target_certification_preflight",
            )


def test_spec_17_3_29_schema_every_preflight_case_is_terminal_or_incomplete() -> None:
    validate_file_role_cardinality(
        batch_status="incomplete_refused",
        certified_count=1,
        refused_count=0,
        failure_ledger_entry_count=1,
        file_roles=[
            "batch_manifest",
            "command_transcript",
            "exit_code_capture",
            "filesystem_after_manifest",
            "filesystem_before_manifest",
            "hash_manifest",
            "per_case_result",
            "stderr_capture",
            "target_certificate",
            "failure_ledger_entry",
        ],
    )
    with pytest.raises(SchemaContractError, match="target_refusal_cardinality"):
        validate_file_role_cardinality(
            batch_status="complete_with_refusals",
            certified_count=1,
            refused_count=1,
            failure_ledger_entry_count=1,
            file_roles=[
                "batch_manifest",
                "command_transcript",
                "exit_code_capture",
                "filesystem_after_manifest",
                "filesystem_before_manifest",
                "hash_manifest",
                "per_case_result",
                "per_case_result",
                "stderr_capture",
                "target_certificate",
                "failure_ledger_entry",
            ],
        )
    validate_file_role_cardinality(
        batch_status="complete_with_refusals",
        certified_count=1,
        refused_count=1,
        failure_ledger_entry_count=1,
        file_roles=[
            "batch_manifest",
            "command_transcript",
            "exit_code_capture",
            "filesystem_after_manifest",
            "filesystem_before_manifest",
            "hash_manifest",
            "per_case_result",
            "per_case_result",
            "stderr_capture",
            "target_certificate",
            "target_refusal",
            "failure_ledger_entry",
        ],
    )
    with pytest.raises(SchemaContractError, match="target_certificate_cardinality"):
        validate_file_role_cardinality(
            batch_status="complete_all_certified",
            certified_count=1,
            refused_count=0,
            failure_ledger_entry_count=0,
            file_roles=[
                "batch_manifest",
                "command_transcript",
                "exit_code_capture",
                "filesystem_after_manifest",
                "filesystem_before_manifest",
                "hash_manifest",
                "per_case_result",
                "stderr_capture",
            ],
        )
    with pytest.raises(SchemaContractError, match="file_role_count_type"):
        validate_file_role_cardinality(
            batch_status="complete_all_certified",
            certified_count=True,
            refused_count=0,
            failure_ledger_entry_count=0,
            file_roles=[
                "batch_manifest",
                "command_transcript",
                "exit_code_capture",
                "filesystem_after_manifest",
                "filesystem_before_manifest",
                "hash_manifest",
                "stderr_capture",
            ],
        )
    with pytest.raises(SchemaContractError, match="file_role_count_type"):
        validate_file_role_cardinality(
            batch_status="complete_all_certified",
            certified_count=0,
            refused_count=-1,
            failure_ledger_entry_count=0,
            file_roles=[
                "batch_manifest",
                "command_transcript",
                "exit_code_capture",
                "filesystem_after_manifest",
                "filesystem_before_manifest",
                "hash_manifest",
                "stderr_capture",
            ],
        )


def test_spec_17_3_30_schema_terminal_partition_counts_reconcile() -> None:
    validate_declared_terminal_partition(
        ["case-a", "case-b"],
        {"certified": ["case-a"], "refused": ["case-b"], "pending": []},
        {"certified": 1, "refused": 1, "pending": 0},
    )
    with pytest.raises(SchemaContractError, match="terminal_partition_overlap"):
        validate_declared_terminal_partition(
            ["case-a", "case-b"],
            {"certified": ["case-a"], "refused": ["case-a"], "pending": []},
            {"certified": 1, "refused": 1, "pending": 0},
        )
    with pytest.raises(SchemaContractError, match="terminal_partition_incomplete"):
        validate_declared_terminal_partition(
            ["case-a", "case-b"],
            {"certified": ["case-a"], "refused": [], "pending": []},
            {"certified": 1, "refused": 0, "pending": 0},
        )
    with pytest.raises(SchemaContractError, match="terminal_count_mismatch"):
        validate_declared_terminal_partition(
            ["case-a", "case-b"],
            {"certified": ["case-a"], "refused": ["case-b"], "pending": []},
            {"certified": 2, "refused": 1, "pending": 0},
        )
    with pytest.raises(SchemaContractError, match="terminal_count_type"):
        validate_declared_terminal_partition(
            ["case-a"],
            {"certified": ["case-a"], "refused": [], "pending": []},
            {"certified": True, "refused": 0, "pending": 0},
        )
    with pytest.raises(SchemaContractError, match="set_array_duplicate"):
        validate_declared_terminal_partition(
            ["case-a", "case-a"],
            {"certified": ["case-a"], "refused": [], "pending": []},
            {"certified": 1, "refused": 0, "pending": 0},
        )
    with pytest.raises(SchemaContractError, match="set_array_duplicate"):
        validate_declared_terminal_partition(
            ["case-a"],
            {"certified": ["case-a", "case-a"], "refused": [], "pending": []},
            {"certified": 2, "refused": 0, "pending": 0},
        )


def test_spec_17_3_34_schema_quantitative_scope_rejects_implicit_expansion() -> None:
    manifest, records = _valid_quantitative_command_manifest()
    validate_command_manifest(manifest, records, capability="quantitative_execution")
    manifest["schema_version"] = "ims-deadlock/g6b-quantitative-command/v0"
    with pytest.raises(SchemaContractError, match="schema_version_drift"):
        validate_command_manifest(
            manifest, records, capability="quantitative_execution"
        )
    manifest, records = _valid_quantitative_command_manifest()
    manifest["declared_command_ids"] = []
    manifest["command_record_hashes"] = {}
    manifest["command_count"] = 0
    with pytest.raises(SchemaContractError, match="command_id_set_mismatch"):
        validate_command_manifest(manifest, {}, capability="quantitative_execution")
    manifest, records = _valid_quantitative_command_manifest()
    records["cmd-quantitative"]["authorized_case_unit_ids"] = ["case-a", "case-*"]
    with pytest.raises(SchemaContractError, match="wildcard_scope"):
        validate_command_manifest(
            manifest,
            records,
            capability="quantitative_execution",
        )


def test_quantitative_command_manifest_reconciles_scope_hash_maps() -> None:
    manifest, records = _valid_quantitative_command_manifest()
    validate_command_manifest(manifest, records, capability="quantitative_execution")

    manifest, records = _valid_quantitative_command_manifest()
    manifest["output_root_reservation_hashes"] = {"method-*": "1" * 64}
    with pytest.raises(SchemaContractError, match="hash_map_key_scope"):
        validate_command_manifest(
            manifest, records, capability="quantitative_execution"
        )

    manifest, records = _valid_quantitative_command_manifest()
    records["cmd-quantitative"]["authorized_output_root_reservation_hashes"] = {}
    with pytest.raises(SchemaContractError, match="hash_map_empty"):
        validate_command_manifest(
            manifest, records, capability="quantitative_execution"
        )

    manifest, records = _valid_quantitative_command_manifest()
    records["cmd-quantitative"]["authorized_output_root_reservation_hashes"] = {
        "method-a": "9" * 64
    }
    records["cmd-quantitative"] = _with_rehashed(
        records["cmd-quantitative"],
        "command_record_sha256",
    )
    manifest["command_record_hashes"]["cmd-quantitative"] = records["cmd-quantitative"][
        "command_record_sha256"
    ]
    manifest = _with_rehashed(manifest, "manifest_sha256")
    with pytest.raises(SchemaContractError, match="output_root_hash_map_mismatch"):
        validate_command_manifest(
            manifest, records, capability="quantitative_execution"
        )

    manifest, records = _valid_quantitative_command_manifest()
    manifest["same_target_lock_hashes"] = {"case-b": "6" * 64}
    with pytest.raises(SchemaContractError, match="same_target_hash_map_mismatch"):
        validate_command_manifest(
            manifest, records, capability="quantitative_execution"
        )


def test_spec_17_3_39_schema_source_dimension_uses_exact_producer_row() -> None:
    matrix: list[JsonObject] = [
        {
            "source_path_pattern": "evidence/g5/G5_EXECUTION_LOCK.json",
            "selector_kind": "exact_pointer_set",
            "selectors": ["/output_roots/raw_output_root_relative"],
            "allowed_use": "output_root_containment_projection",
        }
    ]
    validate_source_pointer_use(
        "evidence/g5/G5_EXECUTION_LOCK.json",
        "/output_roots/raw_output_root_relative",
        "output_root_containment_projection",
        matrix,
    )
    with pytest.raises(SchemaContractError, match="source_pointer_use_not_allowed"):
        validate_source_pointer_use(
            "evidence/g5/G5_EXECUTION_LOCK.json",
            "/output_roots/guessed_from_filename",
            "output_root_containment_projection",
            matrix,
        )


def test_spec_17_3_40_schema_source_selector_grants_one_use_only() -> None:
    matrix: list[JsonObject] = [
        {
            "source_path_pattern": "evidence/g5/G5_RESULT_SUMMARY.json",
            "selector_kind": "raw_bytes_only",
            "selectors": [],
            "allowed_use": "source_hash_validation",
        },
        {
            "source_path_pattern": "evidence/g5/G5_EXECUTION_LOCK.json",
            "selector_kind": "exact_pointer_set",
            "selectors": ["/output_roots/raw_output_root_relative"],
            "allowed_use": "output_root_containment_projection",
        },
    ]
    validate_source_pointer_use(
        "evidence/g5/G5_RESULT_SUMMARY.json",
        None,
        "source_hash_validation",
        matrix,
    )
    with pytest.raises(SchemaContractError, match="raw_bytes_only_json_parse"):
        validate_source_pointer_use(
            "evidence/g5/G5_RESULT_SUMMARY.json",
            "/result",
            "source_hash_validation",
            matrix,
        )
    with pytest.raises(SchemaContractError, match="source_pointer_use_not_allowed"):
        validate_source_pointer_use(
            "evidence/g5/G5_EXECUTION_LOCK.json",
            "/output_roots/raw_output_root_relative",
            "source_hash_validation",
            matrix,
        )
    union_matrix: list[JsonObject] = [
        {
            "source_path_pattern": "evidence/g5/G5_EXECUTION_LOCK.json",
            "selector_kind": "exact_pointer_set",
            "selectors": ["/output_roots/raw_output_root_relative"],
            "allowed_use": "output_root_containment_projection",
        },
        {
            "source_path_pattern": "evidence/g5/G5_EXECUTION_LOCK.json",
            "selector_kind": "exact_pointer_set",
            "selectors": ["/schema_version"],
            "allowed_use": "source_hash_validation",
        },
    ]
    with pytest.raises(SchemaContractError, match="source_pointer_use_not_allowed"):
        validate_source_pointer_use(
            "evidence/g5/G5_EXECUTION_LOCK.json",
            "/output_roots/raw_output_root_relative",
            "source_hash_validation",
            union_matrix,
        )
    element_matrix: list[JsonObject] = [
        {
            "source_path_pattern": "cases/confirmation/g4/case_manifest.json",
            "selector_kind": "element_pointer_pattern_set",
            "selectors": ["/cases/*/path"],
            "allowed_use": "authority_identity",
        }
    ]
    validate_source_pointer_use(
        "cases/confirmation/g4/case_manifest.json",
        "/cases/3/path",
        "authority_identity",
        element_matrix,
    )
    bad_row_matrix: list[JsonObject] = [
        {
            "source_path_pattern": "cases/confirmation/g4/case_manifest.json",
            "selector_kind": "wildcard",
            "selectors": ["/cases/*/path"],
            "allowed_use": "authority_identity",
        }
    ]
    with pytest.raises(SchemaContractError, match="unknown_selector_kind"):
        validate_source_pointer_use(
            "cases/confirmation/g4/case_manifest.json",
            "/cases/3/path",
            "authority_identity",
            bad_row_matrix,
        )
    bad_use_matrix: list[JsonObject] = [
        {
            "source_path_pattern": "cases/confirmation/g4/case_manifest.json",
            "selector_kind": "element_pointer_pattern_set",
            "selectors": ["/cases/*/path"],
            "allowed_use": "comparison_projection",
        }
    ]
    with pytest.raises(SchemaContractError, match="unknown_allowed_use"):
        validate_source_pointer_use(
            "cases/confirmation/g4/case_manifest.json",
            "/cases/3/path",
            "comparison_projection",
            bad_use_matrix,
        )
    repeated_selector_matrix: list[JsonObject] = [
        {
            "source_path_pattern": "cases/confirmation/g4/case_manifest.json",
            "selector_kind": "element_pointer_pattern_set",
            "selectors": ["/cases/*/path"],
            "allowed_use": "authority_identity",
        },
        {
            "source_path_pattern": "cases/confirmation/g4/case_manifest.json",
            "selector_kind": "element_pointer_pattern_set",
            "selectors": ["/cases/*/path"],
            "allowed_use": "lineage_link",
        },
    ]
    validate_source_pointer_use(
        "cases/confirmation/g4/case_manifest.json",
        "/cases/3/path",
        "authority_identity",
        repeated_selector_matrix,
    )
    validate_source_pointer_use(
        "cases/confirmation/g4/case_manifest.json",
        "/cases/3/path",
        "lineage_link",
        repeated_selector_matrix,
    )


def test_spec_17_3_41_schema_barrier_a_rejects_operation_and_role_drift() -> None:
    manifest, records = _valid_command_manifest()
    validate_command_manifest(
        manifest,
        records,
        capability="target_certification_preflight",
    )
    manifest["placeholder_vocabulary"] = ["repo_source_root"]
    with pytest.raises(SchemaContractError, match="placeholder_vocabulary_drift"):
        validate_command_manifest(
            manifest,
            records,
            capability="target_certification_preflight",
        )
    manifest, records = _valid_command_manifest()
    manifest["allowed_operations"] = ("load_input",)
    with pytest.raises(SchemaContractError, match="unexpected_key"):
        validate_command_manifest(
            manifest,
            records,
            capability="target_certification_preflight",
        )
    with pytest.raises(SchemaContractError, match="operation_contract_drift"):
        contracts._validate_exact_sequence(
            ["load_input", *contracts.ALLOWED_OPERATIONS[1:]],
            contracts.ALLOWED_OPERATIONS,
            label="allowed_operations",
        )
    reordered_operations = list(contracts.ALLOWED_OPERATIONS)
    reordered_operations[0], reordered_operations[1] = (
        reordered_operations[1],
        reordered_operations[0],
    )
    with pytest.raises(SchemaContractError, match="operation_contract_drift"):
        contracts._validate_exact_sequence(
            reordered_operations,
            contracts.ALLOWED_OPERATIONS,
            label="allowed_operations",
        )
    with pytest.raises(SchemaContractError, match="output_schema_id_drift"):
        contracts._validate_exact_sequence(
            [
                *contracts.ALLOWED_OUTPUT_SCHEMA_IDS[:-1],
                "ims-deadlock/g6b-unknown/v1",
            ],
            contracts.ALLOWED_OUTPUT_SCHEMA_IDS,
            label="allowed_output_schema_ids",
        )
    wrong_schema_map = dict(contracts.FILE_ROLE_TO_SCHEMA_ID)
    wrong_schema_map["target_certificate"] = "ims-deadlock/g6b-command-capture/v1"
    with pytest.raises(SchemaContractError, match="role_schema_mapping_drift"):
        contracts._validate_exact_mapping(
            wrong_schema_map,
            contracts.FILE_ROLE_TO_SCHEMA_ID,
            label="file_role_to_schema_id",
        )
    with pytest.raises(SchemaContractError, match="unknown_file_role"):
        validate_file_role_cardinality(
            batch_status="complete_all_certified",
            certified_count=1,
            refused_count=0,
            failure_ledger_entry_count=0,
            file_roles=[
                "batch_manifest",
                "command_transcript",
                "exit_code_capture",
                "filesystem_after_manifest",
                "filesystem_before_manifest",
                "hash_manifest",
                "per_case_result",
                "stderr_capture",
                "target_certificate",
                "extra_role",
            ],
        )
    with pytest.raises(SchemaContractError, match="target_certificate_cardinality"):
        validate_file_role_cardinality(
            batch_status="complete_all_certified",
            certified_count=1,
            refused_count=0,
            failure_ledger_entry_count=0,
            file_roles=[
                "batch_manifest",
                "command_transcript",
                "exit_code_capture",
                "filesystem_after_manifest",
                "filesystem_before_manifest",
                "hash_manifest",
                "per_case_result",
                "stderr_capture",
                "target_certificate",
                "target_certificate",
            ],
        )
    validate_exact_keys(
        contracts.FILE_ROLE_TO_SCHEMA_ID,
        contracts.ALLOWED_FILE_ROLES,
        label="file_role_to_schema_id",
    )
    wrong_role_map = dict(contracts.FILE_ROLE_TO_SCHEMA_ID)
    wrong_role_map["extra_role"] = "ims-deadlock/g6b-command-capture/v1"
    with pytest.raises(SchemaContractError, match="unexpected_key"):
        validate_exact_keys(
            wrong_role_map,
            contracts.ALLOWED_FILE_ROLES,
            label="file_role_to_schema_id",
        )


def test_spec_17_3_42_schema_refusal_code_unions_are_gate_specific() -> None:
    validate_refusal_codes("construction", ["unclassified_scientific_input"])
    validate_refusal_codes(
        "normalization_overlap",
        ["retired_projection_unreconstructable", "overlap_hit"],
    )
    validate_refusal_codes(
        "preflight",
        ["batch_incomplete", "unauthorized_target_certification_attempt"],
    )
    validate_refusal_codes("quantitative", ["exact_des_target_mismatch"])
    validate_refusal_codes(
        "ledger",
        ["self_hash_mismatch", "overlap_hit", "failed_negative_control"],
    )
    with pytest.raises(SchemaContractError, match="wrong_gate_refusal_code"):
        validate_refusal_codes("construction", ["certificate_schema_violation"])
    with pytest.raises(SchemaContractError, match="wrong_gate_refusal_code"):
        validate_refusal_codes("normalization_overlap", ["state_bound_truncation"])
    with pytest.raises(SchemaContractError, match="wrong_gate_refusal_code"):
        validate_refusal_codes("preflight", ["quantitative_scope_violation"])
    with pytest.raises(SchemaContractError, match="wrong_gate_refusal_code"):
        validate_refusal_codes("quantitative", ["overlap_hit"])
    with pytest.raises(SchemaContractError, match="unknown_refusal_code"):
        validate_refusal_codes("ledger", ["free_form_refusal"])


def test_spec_17_3_43_schema_overlap_lock_rejects_admin_identity_drift() -> None:
    validate_exact_keys(
        {
            "logical_worktree_id": "g6b-final-review",
            "worktree_kind": "linked",
            "gitdir_file_sha256_or_null": None,
            "common_dir_identity_sha256": "a" * 64,
            "worktree_admin_identity_sha256": "b" * 64,
            "checked_out_tree_hash": "c" * 40,
        },
        contracts.SOURCE_WORKTREE_IDENTITY_REQUIRED_FIELDS,
        label="source_worktree_identity",
    )
    with pytest.raises(SchemaContractError, match="missing_key"):
        validate_exact_keys(
            {
                "logical_worktree_id": "g6b-final-review",
                "worktree_kind": "linked",
                "gitdir_file_sha256_or_null": None,
                "common_dir_identity_sha256": "a" * 64,
                "checked_out_tree_hash": "c" * 40,
            },
            contracts.SOURCE_WORKTREE_IDENTITY_REQUIRED_FIELDS,
            label="source_worktree_identity",
        )
    assert contracts.OVERLAP_LOCK_REQUIRED_FIELDS == (
        "schema_version",
        "lock_id",
        "source_remote",
        "source_branch",
        "source_head",
        "source_tree_hash",
        "source_dirty_state",
        "source_worktree_identity",
        "sealed_bundle_manifest_hash",
        "normalization_authorization_sha256",
        "normalization_manifest_sha256",
        "authority_lock_record_hashes",
        "unique_lineage_map_sha256",
        "comparison_command_manifest_sha256",
        "validator_code_hashes",
        "canonicalization_versions",
        "normalizer_version",
        "planned_case_unit_ids",
        "planned_method_observation_ids",
        "planned_method_companion_group_ids",
        "ledger_head_hash",
        "created_at_utc",
        "lock_sha256",
    )
    assert contracts.OVERLAP_LOCK_WORKTREE_KIND == "linked"
    assert contracts.OVERLAP_LOCK_DIRTY_STATE == "clean"


def test_spec_17_3_44_schema_command_manifest_hash_maps_and_placeholders() -> None:
    manifest, records = _valid_command_manifest()
    validate_command_manifest(
        manifest,
        records,
        capability="target_certification_preflight",
    )
    manifest["runtime_lock_sha256"] = "7" * 64
    with pytest.raises(SchemaContractError, match="downstream_reference"):
        validate_command_manifest(
            manifest,
            records,
            capability="target_certification_preflight",
        )
    manifest, records = _valid_command_manifest()
    manifest["authorization_sha256"] = "8" * 64
    with pytest.raises(SchemaContractError, match="downstream_reference"):
        validate_command_manifest(
            manifest,
            records,
            capability="target_certification_preflight",
        )
    manifest, records = _valid_command_manifest()
    records["cmd-preflight"]["argv_tokens"][1] = {
        "token_kind": "placeholder",
        "placeholder_code": "runtime_lock",
    }
    with pytest.raises(SchemaContractError, match="unknown_placeholder"):
        validate_command_manifest(
            manifest,
            records,
            capability="target_certification_preflight",
        )
    manifest, records = _valid_command_manifest()
    records["cmd-preflight"]["environment_variable_allowlist"]["HOME"] = {
        "token_kind": "literal",
        "value": ".",
    }
    with pytest.raises(SchemaContractError, match="environment_allowlist_mismatch"):
        validate_command_manifest(
            manifest,
            records,
            capability="target_certification_preflight",
        )
    manifest, records = _valid_command_manifest()
    manifest["command_record_hashes"]["cmd-preflight"] = "not-a-sha"
    records["cmd-preflight"]["command_record_sha256"] = "not-a-sha"
    with pytest.raises(SchemaContractError, match="invalid_hash_digest"):
        validate_command_manifest(
            manifest,
            records,
            capability="target_certification_preflight",
        )


def _validate_preflight_authorization_fixture(
    record: JsonObject,
    manifest: JsonObject,
    command_records: dict[str, JsonObject],
) -> None:
    contracts.validate_preflight_authorization(
        record,
        expected_bundle_id=_TEST_BUNDLE_ID,
        expected_case_unit_ids=["case-a"],
        expected_sealed_bundle_manifest_hash=manifest["sealed_bundle_manifest_hash"],
        expected_runtime_lock_sha256="6" * 64,
        command_manifest=manifest,
        command_records=command_records,
    )


def test_preflight_authorization_validates_exact_schema_and_scope() -> None:
    schema = json.loads(
        (_ROW_FAMILY_ROOT / "target_certification_schema.json").read_text(
            encoding="utf-8"
        )
    )
    record, manifest, command_records = _valid_preflight_authorization()

    assert schema["preflight_authorization_required_fields"] == list(
        contracts.PREFLIGHT_AUTHORIZATION_REQUIRED_FIELDS
    )
    _validate_preflight_authorization_fixture(record, manifest, command_records)


def test_preflight_authorization_rejects_missing_required_field() -> None:
    record, manifest, command_records = _valid_preflight_authorization()
    record.pop("allowed_entrypoint")
    record = _with_rehashed(record, "authorization_sha256")

    with pytest.raises(SchemaContractError, match="missing_key"):
        _validate_preflight_authorization_fixture(record, manifest, command_records)


@pytest.mark.parametrize("authorized", [False, 1, "true"])
def test_preflight_authorization_requires_explicit_true(authorized: object) -> None:
    record, manifest, command_records = _valid_preflight_authorization()
    record["authorized"] = authorized
    record = _with_rehashed(record, "authorization_sha256")

    with pytest.raises(
        SchemaContractError,
        match="unauthorized_target_certification_attempt",
    ):
        _validate_preflight_authorization_fixture(record, manifest, command_records)


def test_preflight_authorization_rejects_stale_command_manifest() -> None:
    record, manifest, command_records = _valid_preflight_authorization()
    record["allowed_command_manifest_hash"] = "8" * 64
    record = _with_rehashed(record, "authorization_sha256")

    with pytest.raises(SchemaContractError, match="command_scope_violation"):
        _validate_preflight_authorization_fixture(record, manifest, command_records)


def test_preflight_authorization_rejects_identity_drift() -> None:
    record, manifest, command_records = _valid_preflight_authorization()
    record["invalidated_by_identity_drift"] = True
    record = _with_rehashed(record, "authorization_sha256")

    with pytest.raises(SchemaContractError, match="runtime_identity_drift"):
        _validate_preflight_authorization_fixture(record, manifest, command_records)


def test_preflight_authorization_rejects_reordered_operations() -> None:
    record, manifest, command_records = _valid_preflight_authorization()
    record["allowed_operations"] = list(reversed(record["allowed_operations"]))
    record = _with_rehashed(record, "authorization_sha256")

    with pytest.raises(SchemaContractError, match="operation_contract_drift"):
        _validate_preflight_authorization_fixture(record, manifest, command_records)


def test_preflight_authorization_rejects_scope_widening() -> None:
    record, manifest, command_records = _valid_preflight_authorization()
    record["case_unit_ids"] = ["case-a", "case-b"]
    record = _with_rehashed(record, "authorization_sha256")

    with pytest.raises(SchemaContractError, match="command_scope_violation"):
        _validate_preflight_authorization_fixture(record, manifest, command_records)


def test_preflight_authorization_rejects_materialized_or_mismatched_evidence_root() -> (
    None
):
    record, manifest, command_records = _valid_preflight_authorization()
    record["preflight_evidence_root"]["state"] = (
        "materialized_by_target_certification_only"
    )
    record["preflight_evidence_root"] = _with_rehashed(
        record["preflight_evidence_root"],
        "reservation_sha256",
    )
    record = _with_rehashed(record, "authorization_sha256")

    with pytest.raises(
        SchemaContractError,
        match="unexpected_preflight_side_effect",
    ):
        _validate_preflight_authorization_fixture(record, manifest, command_records)


@pytest.mark.parametrize(
    "repo_relative_posix_path",
    [
        "artifacts/g6b/quantitative/bundle-test/case-a/method-a/primary",
        "cases/discovery/g6b/row_families/structural_discovery_v1/case_units/case-a",
        "governance/g6b/bundle-test",
        "evidence/g6b/fallback/bundle-test",
    ],
)
def test_preflight_authorization_rejects_noncanonical_evidence_root(
    repo_relative_posix_path: str,
) -> None:
    record, manifest, command_records = _valid_preflight_authorization()
    record["preflight_evidence_root"]["repo_relative_posix_path"] = (
        repo_relative_posix_path
    )
    _reseal_preflight_root_links(record, manifest, command_records)

    with pytest.raises(
        SchemaContractError,
        match="unexpected_preflight_side_effect",
    ):
        _validate_preflight_authorization_fixture(record, manifest, command_records)


def test_preflight_authorization_rejects_stale_evidence_root_schema() -> None:
    record, manifest, command_records = _valid_preflight_authorization()
    record["preflight_evidence_root"]["root_schema_version"] = (
        "ims-deadlock/g6b-preflight-evidence-root/v0"
    )
    _reseal_preflight_root_links(record, manifest, command_records)

    with pytest.raises(SchemaContractError, match="schema_version_drift"):
        _validate_preflight_authorization_fixture(record, manifest, command_records)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("max_wall_clock_seconds", 60),
        ("max_cpu_seconds", "0"),
        ("max_memory_bytes", 0),
        ("max_workers", True),
    ],
)
def test_preflight_authorization_rejects_invalid_resource_budget(
    field: str,
    value: object,
) -> None:
    record, manifest, command_records = _valid_preflight_authorization()
    record["resource_budget"][field] = value
    record = _with_rehashed(record, "authorization_sha256")

    with pytest.raises(SchemaContractError, match="command_scope_violation"):
        _validate_preflight_authorization_fixture(record, manifest, command_records)


def test_typed_capability_mutations_are_fail_closed() -> None:
    validate_typed_capabilities(dict.fromkeys(CAPABILITY_FIELDS, False))
    with pytest.raises(SchemaContractError, match="missing_key"):
        validate_typed_capabilities(
            {
                "case_construction_authorized": False,
                "retired_authority_fingerprint_normalization_authorized": False,
                "target_certification_preflight_authorized": False,
            }
        )
    with pytest.raises(SchemaContractError, match="capability_true"):
        validate_typed_capabilities(
            {
                "case_construction_authorized": True,
                "retired_authority_fingerprint_normalization_authorized": False,
                "target_certification_preflight_authorized": False,
                "quantitative_execution_authorized": False,
            }
        )
    with pytest.raises(SchemaContractError, match="unexpected_key"):
        validate_typed_capabilities(
            {
                "case_construction_authorized": False,
                "retired_authority_fingerprint_normalization_authorized": False,
                "target_certification_preflight_authorized": False,
                "quantitative_execution_authorized": False,
                "scientific_execution_authorized": False,
            }
        )


_CASE_CONSTRUCTION_SCHEMA_V3_TOP_LEVEL_KEYS = (
    "schema_version",
    "study_role",
    "confirmation_use",
    "schema_role",
    "current_capability_reference",
    "prerequisite_bundle_state",
    "canonicalization_contract",
    "self_hash_finalization_contract",
    "estimand_id_scope_contract",
    "governance_instance_root_template",
    "case_unit_root_template",
    "construction_authorization_required_fields",
    "sealed_bundle_manifest_required_fields",
    "case_unit_required_fields",
    "method_observation_required_fields",
    "method_companion_group_required_fields",
    "semantic_lineage_declaration_required_fields",
    "metric_schema_sharing_record_required_fields",
    "fingerprint_record_required_fields",
    "fingerprint_subject_map",
    "fingerprint_payload_schemas",
    "materialization_file_contracts",
    "construction_log_contract",
    "construction_ledger_contract",
    "source_identity_contract",
    "transient_path_contract",
    "des_seed_contract",
    "dimension_dependence_contract",
    "allowed_input_modes",
    "output_root_reservation_contract",
    "nested_field_contracts",
    "recursive_prohibited_fields",
    "prohibited_instance_fields",
    "refusal_code_vocabulary_version",
    "refusal_reason_codes",
    "schema_does_not_authorize_case_creation",
)
_CASE_CONSTRUCTION_V3_RELATIVE_PATHS = (
    "case_input.json",
    "declarations/control_declaration.json",
    "declarations/policy_declaration.json",
    "declarations/rate_manifest.json",
    "declarations/selected_target_declaration.json",
    "fingerprints/case_content_sha256.json",
    "fingerprints/metric_schema_sha256.json",
    "fingerprints/output_root_reservation_sha256_des.json",
    "fingerprints/output_root_reservation_sha256_exact.json",
    "fingerprints/parameter_tuple_sha256.json",
    "fingerprints/random_stream_manifest_sha256_des.json",
    "fingerprints/random_stream_manifest_sha256_exact.json",
    "fingerprints/route_signature_sha256.json",
    "fingerprints/sealed_prediction_sha256.json",
    "fingerprints/state_snapshot_sha256.json",
    "method_companion_group.json",
    "method_observations/des.json",
    "method_observations/exact.json",
    "metric_schema.json",
    "metric_schema_sharing.json",
    "projections/case_content.json",
    "projections/output_root_reservation_des.json",
    "projections/output_root_reservation_exact.json",
    "projections/parameter_tuple.json",
    "projections/random_stream_manifest_des.json",
    "projections/random_stream_manifest_exact.json",
    "projections/route_signature.json",
    "projections/state_snapshot.json",
    "sealed_prediction.json",
    "semantic_lineage_declaration.json",
)
_CASE_ARTIFACT_PATH_REQUIRED_KEYS_V3 = (
    "case_input",
    "case_content_projection",
    "state_snapshot",
    "route_signature",
    "parameter_tuple",
    "rate_manifest",
    "policy_declaration",
    "selected_target_declaration",
    "control_declaration",
    "sealed_prediction",
    "semantic_lineage_declaration",
    "method_observations",
    "random_stream_manifests",
    "output_root_reservations",
    "metric_schema",
    "metric_schema_sharing",
    "fingerprint_records",
)
_RUN4_SELECTED_TARGET_SEMANTIC_FIELDS = (
    "target_schema_version",
    "selected_bad_classes",
    "success_class",
    "exact_stopping_rule",
    "des_stopping_rule",
    "policy_analysis_class",
)


def _case_construction_schema() -> JsonObject:
    return cast(
        JsonObject,
        json.loads((_ROW_FAMILY_ROOT / "case_construction_schema.json").read_text()),
    )


def test_case_construction_schema_v3_top_level_contract_is_exact() -> None:
    schema = _case_construction_schema()

    assert schema["schema_version"] == "ims-deadlock/g6b-case-construction-schema/v3"
    assert tuple(schema) == _CASE_CONSTRUCTION_SCHEMA_V3_TOP_LEVEL_KEYS
    assert tuple(contracts.CASE_CONSTRUCTION_SCHEMA_TOP_LEVEL_KEYS) == (
        _CASE_CONSTRUCTION_SCHEMA_V3_TOP_LEVEL_KEYS
    )
    assert "metric_schema_reuse_record_required_fields" not in schema
    for required_key in (
        "materialization_file_contracts",
        "construction_log_contract",
        "construction_ledger_contract",
        "source_identity_contract",
        "transient_path_contract",
        "des_seed_contract",
        "metric_schema_sharing_record_required_fields",
    ):
        assert required_key in schema


@pytest.mark.parametrize("relative_path", _CASE_CONSTRUCTION_V3_RELATIVE_PATHS)
def test_case_construction_v3_materialization_contracts_are_closed(
    relative_path: str,
) -> None:
    schema = _case_construction_schema()
    contract = schema["materialization_file_contracts"][relative_path]
    code_contract = contracts.CASE_MATERIALIZATION_FILE_CONTRACTS[relative_path]

    assert schema["materialization_file_contracts"] == dict(
        contracts.CASE_MATERIALIZATION_FILE_CONTRACTS
    )
    assert contract == code_contract
    assert contract["schema_version_field_value"].startswith("ims-deadlock/g6b-")
    assert contract["hash_meaning"] in {
        "final_canonical_file_bytes_sha256",
        "null_placeholder_self_hash",
    }
    if (
        relative_path.startswith("projections/")
        or relative_path == "metric_schema.json"
    ):
        assert contract["projection_subject"] in {
            "case_unit",
            "method_observation",
            "method_companion_group",
        }
    if relative_path.startswith("fingerprints/"):
        assert (
            contract["direct_stored_fingerprint_target"]
            in _CASE_CONSTRUCTION_V3_RELATIVE_PATHS
        )


def test_case_construction_v3_inventory_and_manifest_hash_closure() -> None:
    schema = _case_construction_schema()

    assert tuple(
        schema["nested_field_contracts"]["case_artifact_paths_required_keys"]
    ) == (_CASE_ARTIFACT_PATH_REQUIRED_KEYS_V3)
    assert tuple(contracts.CASE_ARTIFACT_PATHS_REQUIRED_KEYS) == (
        _CASE_ARTIFACT_PATH_REQUIRED_KEYS_V3
    )
    assert len(schema["materialization_file_contracts"]) == 30
    assert "metric_schema_reuse.json" not in schema["materialization_file_contracts"]
    for required_projection in (
        "projections/case_content.json",
        "projections/output_root_reservation_des.json",
        "projections/output_root_reservation_exact.json",
        "projections/random_stream_manifest_des.json",
        "projections/random_stream_manifest_exact.json",
    ):
        assert required_projection in schema["materialization_file_contracts"]
    assert schema["sealed_bundle_manifest_required_fields"][-6:] == [
        "construction_log_sha256",
        "construction_ledger_head_sha256",
        "metric_schema_sharing_record_hashes",
        "case_file_count",
        "governance_file_count",
        "total_file_count",
    ]
    assert schema["nested_field_contracts"]["sealed_manifest_v2_count_contract"] == {
        "case_file_count": 390,
        "governance_file_count": 4,
        "total_file_count": 394,
    }
    assert schema["nested_field_contracts"]["manifest_sharing_hash_contract"] == {
        "metric_schema_sharing_record_hashes": "final_canonical_file_bytes_sha256",
        "sharing_record_sha256": "separate_null_placeholder_self_hash",
    }


def test_run4_selected_target_shared_payload_is_six_semantic_fields() -> None:
    schema = _case_construction_schema()
    shared_contract = schema["fingerprint_payload_schemas"]["case_content_sha256"][
        "nested_field_contracts"
    ]["selected_target_declaration"]
    file_contract = schema["materialization_file_contracts"][
        "declarations/selected_target_declaration.json"
    ]

    assert tuple(shared_contract["required_fields"]) == (
        _RUN4_SELECTED_TARGET_SEMANTIC_FIELDS
    )
    assert tuple(contracts.SELECTED_TARGET_DECLARATION_REQUIRED_FIELDS) == (
        _RUN4_SELECTED_TARGET_SEMANTIC_FIELDS
    )
    assert "schema_version" not in shared_contract["required_fields"]
    assert file_contract["schema_version_field_name"] == "schema_version"
    assert file_contract["schema_version_field_value"] == (
        "ims-deadlock/g6b-selected-target-declaration/v1"
    )


def test_run4_selected_target_materialization_exact_keys_union_file_schema() -> None:
    record: JsonObject = {
        "schema_version": "ims-deadlock/g6b-selected-target-declaration/v1",
        "target_schema_version": "ims-deadlock/g6-terminal-stopping-partition/v3",
        "selected_bad_classes": ["D_global", "D_local"],
        "success_class": "F",
        "exact_stopping_rule": "first_hit_D_global_or_D_local_or_F_v1",
        "des_stopping_rule": "first_hit_D_global_or_D_local_or_F_or_censor_budget_v1",
        "policy_analysis_class": "P_policy",
    }

    contracts.validate_materialization_record_exact_keys(
        "declarations/selected_target_declaration.json",
        record,
    )
    for mutation in ("missing_schema_version", "extra_key"):
        broken = dict(record)
        if mutation == "missing_schema_version":
            broken.pop("schema_version")
        else:
            broken["unexpected_extra_member"] = "must_be_rejected"
        with pytest.raises(
            SchemaContractError, match="materialization_required_fields"
        ):
            contracts.validate_materialization_record_exact_keys(
                "declarations/selected_target_declaration.json",
                broken,
            )


def _resolve_dotted_contract(schema: Mapping[str, Any], dotted_path: str) -> object:
    current: object = schema
    for part in dotted_path.split("."):
        assert isinstance(current, Mapping), dotted_path
        current = current[part]
    return current


def test_r4_case_construction_v3_top_level_authorization_fields_are_exact() -> None:
    schema = _case_construction_schema()

    assert tuple(schema["construction_authorization_required_fields"]) == (
        contracts.CONSTRUCTION_AUTHORIZATION_V2_REQUIRED_FIELDS
    )
    assert (
        "review_artifact_hash"
        not in schema["construction_authorization_required_fields"]
    )


def test_r4_case_construction_v3_all_required_field_contracts_are_resolvable() -> None:
    schema = _case_construction_schema()

    for relative_path, contract in schema["materialization_file_contracts"].items():
        resolved = _resolve_dotted_contract(
            schema,
            contract["required_fields_contract"],
        )
        assert isinstance(resolved, (list, dict)), relative_path

    for suffix in ("des", "exact"):
        assert schema["materialization_file_contracts"][
            f"projections/output_root_reservation_{suffix}.json"
        ]["required_fields_contract"] == (
            "nested_field_contracts.output_root_reservation_instance_required_fields"
        )


def test_case_construction_v3_log_ledger_source_transient_and_sharing_constants() -> (
    None
):
    schema = _case_construction_schema()

    assert tuple(schema["construction_log_contract"]["required_fields"]) == (
        contracts.CONSTRUCTION_LOG_REQUIRED_FIELDS
    )
    assert tuple(schema["construction_ledger_contract"]["entry_required_fields"]) == (
        contracts.CONSTRUCTION_LEDGER_ENTRY_REQUIRED_FIELDS
    )
    assert schema["construction_ledger_contract"]["event_transitions"] == {
        "EMPTY": ["PREWRITE_REFUSED", "WRITE_STARTED"],
        "PREWRITE_REFUSED": ["PREWRITE_REFUSED", "WRITE_STARTED"],
        "WRITE_STARTED": ["FILE_CREATED", "INTERRUPTED_PARTIAL"],
        "FILE_CREATED": ["FILE_CREATED", "READY_TO_SEAL", "INTERRUPTED_PARTIAL"],
        "READY_TO_SEAL": ["INTERRUPTED_PARTIAL"],
    }
    assert tuple(
        schema["source_identity_contract"]["authorization_v2_required_fields"]
    ) == (contracts.CONSTRUCTION_AUTHORIZATION_V2_REQUIRED_FIELDS)
    assert tuple(
        schema["source_identity_contract"]["authorized_source_file_paths"]
    ) == (contracts.CONSTRUCTION_AUTHORIZATION_SOURCE_FILE_PATHS)
    assert schema["transient_path_contract"]["covered_final_path_count"] == 393
    assert (
        schema["transient_path_contract"]["sealed_success_requires_all_absent"] is True
    )
    assert tuple(schema["metric_schema_sharing_record_required_fields"]) == (
        contracts.METRIC_SCHEMA_SHARING_RECORD_REQUIRED_FIELDS
    )
    assert schema["nested_field_contracts"]["metric_schema_sharing_contract"][
        "sharing_reason_code"
    ] == ("same_preregistered_estimand_metric_and_scoring_contract")
    assert schema["nested_field_contracts"]["metric_schema_sharing_contract"][
        "review_artifact_hash"
    ] == ("da6da7c2e513e11761e439f8b43ef6260556c912d3e730f94f15eae088d90ea0")


def test_case_construction_v3_seed_derivation_has_golden_vectors() -> None:
    seed_root = contracts.derive_des_seed_root_hex(
        approved_plan_artifact_hash="81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7",
        case_recipe_registry_sha256="1" * 64,
        plan_review_artifact_hash="da6da7c2e513e11761e439f8b43ef6260556c912d3e730f94f15eae088d90ea0",
        source_head="26515fe4da5c02d4700a54a3882d3767ace88af8",
        source_tree_hash="9b3f36e9943ed48db4d74057ef16991859ded8fd",
    )
    commitment = contracts.derive_des_seed_root_commitment(seed_root)

    assert (
        seed_root == "65434dbc332dda84d7b7b25950473ea1273af8a17ffa941e063940cef004f999"
    )
    assert (
        commitment == "3d982bd054d17c6ece6600fc7ae7db14f1d3472ae590a4c4ae470bd1de625763"
    )
    assert (
        contracts.derive_des_philox_key_hex(
            seed_root_hex=seed_root,
            case_content_sha256="2" * 64,
            replicate_index=0,
        )
        == "9f06a4cb91cf40941294c9a15482b7ace96b32f52c5ce3231ea9a99c09203710"
    )
    assert (
        contracts.derive_des_derivation_label_sha256(
            case_content_sha256="2" * 64,
            seed_root_commitment=commitment,
        )
        == "a7b1ceb7c0ddf26ec86ce651dfe66a5facd6c19bdde702b20944b1ce98eaf66d"
    )


def _ledger_entry(
    event_code: str, index: int, prior: str | None, **updates: Any
) -> JsonObject:
    entry: JsonObject = {
        "schema_version": "ims-deadlock/g6b-construction-ledger-entry/v1",
        "bundle_id": "g6b_discovery_case_construction_v1",
        "attempt_id": "g6b_discovery_case_construction_v1_unauthorized",
        "entry_index": index,
        "event_code": event_code,
        "prior_entry_sha256_or_null": prior,
        "construction_authorization_sha256_or_null": None,
        "source_head_or_null": None,
        "source_tree_hash_or_null": None,
        "candidate_log_sha256_or_null": None,
        "created_file_hashes": {},
        "observed_partial_file_hashes": {},
        "refusal_reason_codes": [],
        "causal_entry_sha256_or_null": None,
        "interrupted_fragments": [],
        "entry_sha256": None,
    }
    entry.update(updates)
    entry["entry_sha256"] = finalized_self_hash(entry, "entry_sha256")
    return entry


def _ledger_frame(entry: JsonObject) -> bytes:
    return b"\x1e" + canonical_bytes_v2(entry) + b"\x0a"


def _fragment_records_for_test(fragments: Sequence[bytes]) -> list[JsonObject]:
    return [
        {
            "fragment_index": index,
            "fragment_sha256": hashlib.sha256(fragment).hexdigest(),
            "fragment_byte_count": len(fragment),
        }
        for index, fragment in enumerate(fragments)
    ]


def test_construction_ledger_accepts_recorded_fragments() -> None:
    first = _ledger_entry("WRITE_STARTED", 0, None)
    fragment = b'\x1e{"schema_version":"ims-deadlock/g6b-construction-ledger-entry/v1"'
    fragment_hash = hashlib.sha256(fragment).hexdigest()
    recovery = _ledger_entry(
        "INTERRUPTED_PARTIAL",
        1,
        first["entry_sha256"],
        observed_partial_file_hashes={
            "case_units/case-01/.g6b-tmp-token-case_input.json": "3" * 64
        },
        refusal_reason_codes=["ledger_append_interrupted"],
        causal_entry_sha256_or_null=first["entry_sha256"],
        interrupted_fragments=[
            {
                "fragment_index": 0,
                "fragment_sha256": fragment_hash,
                "fragment_byte_count": len(fragment),
            }
        ],
    )
    raw = _ledger_frame(first) + fragment + _ledger_frame(recovery)

    result = contracts.validate_construction_ledger_bytes(raw)

    assert result.entry_count == 2
    assert result.interrupted_fragment_count == 1
    assert result.ledger_head_sha256 == recovery["entry_sha256"]
    with pytest.raises(ValueError):
        loads_v2(raw.decode("utf-8"))


@pytest.mark.parametrize(
    "fragments",
    [
        [b'\x1e{"partial":'],
        [b'\x1e{"partial":', b'\x1e{"another":true'],
    ],
)
def test_construction_ledger_prewrite_binds_empty_prefix_torn_fragments(
    fragments: list[bytes],
) -> None:
    prewrite = _ledger_entry(
        "PREWRITE_REFUSED",
        0,
        None,
        refusal_reason_codes=[
            "ledger_append_interrupted",
            "unauthorized_case_creation_attempt",
        ],
        interrupted_fragments=_fragment_records_for_test(fragments),
    )
    raw = b"".join(fragments) + _ledger_frame(prewrite)

    result = contracts.validate_construction_ledger_bytes(raw)

    assert result.entry_count == 1
    assert result.interrupted_fragment_count == len(fragments)
    assert result.ledger_head_sha256 == prewrite["entry_sha256"]


@pytest.mark.parametrize(
    "fragments",
    [
        [b'\x1e{"partial":'],
        [b'\x1e{"partial":', b'\x1e{"another":true'],
    ],
)
def test_construction_ledger_prewrite_binds_after_prewrite_torn_fragments(
    fragments: list[bytes],
) -> None:
    first = _ledger_entry(
        "PREWRITE_REFUSED",
        0,
        None,
        refusal_reason_codes=["unauthorized_case_creation_attempt"],
    )
    recovery = _ledger_entry(
        "PREWRITE_REFUSED",
        1,
        first["entry_sha256"],
        refusal_reason_codes=[
            "ledger_append_interrupted",
            "unauthorized_case_creation_attempt",
        ],
        interrupted_fragments=_fragment_records_for_test(fragments),
    )
    raw = _ledger_frame(first) + b"".join(fragments) + _ledger_frame(recovery)

    result = contracts.validate_construction_ledger_bytes(raw)

    assert result.entry_count == 2
    assert result.interrupted_fragment_count == len(fragments)
    assert result.ledger_head_sha256 == recovery["entry_sha256"]


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("fragment_order", "interrupted_fragment"),
        ("fragment_hash", "interrupted_fragment_unrecorded"),
        ("fragment_byte_count", "interrupted_fragment_unrecorded"),
        ("missing_reason", "interrupted_fragment_unrecorded"),
    ],
)
def test_construction_ledger_prewrite_fragment_binding_mutations_fail(
    mutation: str, expected: str
) -> None:
    fragments = [b'\x1e{"partial":', b'\x1e{"another":true']
    records = _fragment_records_for_test(fragments)
    reasons = ["ledger_append_interrupted", "unauthorized_case_creation_attempt"]
    if mutation == "fragment_order":
        records = [records[1], records[0]]
    elif mutation == "fragment_hash":
        records[0] = {**records[0], "fragment_sha256": "0" * 64}
    elif mutation == "fragment_byte_count":
        records[0] = {**records[0], "fragment_byte_count": 1}
    elif mutation == "missing_reason":
        reasons = ["unauthorized_case_creation_attempt"]
    prewrite = _ledger_entry(
        "PREWRITE_REFUSED",
        0,
        None,
        refusal_reason_codes=reasons,
        interrupted_fragments=records,
    )
    raw = b"".join(fragments) + _ledger_frame(prewrite)

    with pytest.raises(SchemaContractError, match=expected):
        contracts.validate_construction_ledger_bytes(raw)


def test_validate_construction_ledger_bytes_rejects_unrecorded_fragment() -> None:
    first = _ledger_entry("WRITE_STARTED", 0, None)
    fragment = b'\x1e{"schema_version":"ims-deadlock/g6b-construction-ledger-entry/v1"'
    recovery = _ledger_entry(
        "INTERRUPTED_PARTIAL",
        1,
        first["entry_sha256"],
        refusal_reason_codes=["ledger_append_interrupted"],
        causal_entry_sha256_or_null=first["entry_sha256"],
    )

    with pytest.raises(SchemaContractError, match="interrupted_fragment_unrecorded"):
        contracts.validate_construction_ledger_bytes(
            _ledger_frame(first) + fragment + _ledger_frame(recovery)
        )


def test_construction_v3_keeps_retired_reuse_only_in_overlap_schemas() -> None:
    schema = _case_construction_schema()
    overlap = json.loads((_ROW_FAMILY_ROOT / "overlap_report_schema.json").read_text())
    retired = json.loads(
        (_ROW_FAMILY_ROOT / "retired_authority_fingerprint_schema.json").read_text()
    )

    assert "metric_schema_reuse_record_required_fields" not in schema
    assert tuple(schema["metric_schema_sharing_record_required_fields"]) == (
        contracts.METRIC_SCHEMA_SHARING_RECORD_REQUIRED_FIELDS
    )
    assert tuple(overlap["metric_schema_reuse_record_required_fields"]) == (
        contracts.METRIC_SCHEMA_REUSE_RECORD_REQUIRED_FIELDS
    )
    assert tuple(retired["metric_schema_reuse_record_required_fields"]) == (
        contracts.METRIC_SCHEMA_REUSE_RECORD_REQUIRED_FIELDS
    )
    assert (
        schema["refusal_code_vocabulary_version"] == "ims-deadlock/g6b-refusal-codes/v2"
    )
    for added_code in (
        "ledger_append_interrupted",
        "partial_bundle_terminal",
        "post_seal_ledger_mutation",
        "projection_file_missing",
        "source_identity_phase_violation",
        "unexpected_transient_path",
    ):
        assert added_code in schema["refusal_reason_codes"]


def test_construction_v3_refusal_vocabulary_is_versioned_and_gate_specific() -> None:
    contracts.validate_refusal_codes(
        "construction_v3",
        contracts.CASE_CONSTRUCTION_V3_REFUSAL_REASON_CODES,
    )
    contracts.validate_refusal_codes(
        "construction", contracts.CONSTRUCTION_REFUSAL_CODES
    )

    for code in (
        "ledger_append_interrupted",
        "partial_bundle_terminal",
        "post_seal_ledger_mutation",
    ):
        with pytest.raises(SchemaContractError, match="wrong_gate_refusal_code"):
            contracts.validate_refusal_codes("construction", [code])
        with pytest.raises(SchemaContractError, match="wrong_gate_refusal_code"):
            contracts.validate_refusal_codes("preflight", [code])
    with pytest.raises(SchemaContractError, match="unknown_refusal_code"):
        contracts.validate_refusal_codes("construction_v3", ["invented_refusal"])


@pytest.mark.parametrize(
    "event_code",
    ["WRITE_STARTED", "FILE_CREATED"],
)
def test_construction_ledger_rejects_unsealed_terminal_write_states(
    event_code: str,
) -> None:
    first = _ledger_entry("WRITE_STARTED", 0, None)
    entries = [_ledger_frame(first)]
    if event_code == "FILE_CREATED":
        created = _ledger_entry(
            "FILE_CREATED",
            1,
            first["entry_sha256"],
            created_file_hashes={"case_units/case-01/case_input.json": "4" * 64},
        )
        entries.append(_ledger_frame(created))

    with pytest.raises(SchemaContractError, match="partial_bundle_terminal"):
        contracts.validate_construction_ledger_bytes(b"".join(entries))


def test_construction_ledger_ready_to_seal_requires_exact_391_hashes() -> None:
    first = _ledger_entry("WRITE_STARTED", 0, None)
    created = _ledger_entry(
        "FILE_CREATED",
        1,
        first["entry_sha256"],
        created_file_hashes={"case_units/case-000/case_input.json": "4" * 64},
    )
    too_short = {
        f"case_units/case-{index:03d}/case_input.json": "5" * 64 for index in range(390)
    }
    ready = _ledger_entry(
        "READY_TO_SEAL", 2, created["entry_sha256"], created_file_hashes=too_short
    )

    with pytest.raises(SchemaContractError, match="ready_to_seal_file_count_mismatch"):
        contracts.validate_construction_ledger_bytes(
            _ledger_frame(first) + _ledger_frame(created) + _ledger_frame(ready)
        )

    prior_created: list[JsonObject] = [created]
    prior = created
    complete = {"case_units/case-000/case_input.json": "4" * 64}
    for index in range(1, 391):
        path = f"case_units/case-{index:03d}/case_input.json"
        prior = _ledger_entry(
            "FILE_CREATED",
            index + 1,
            prior["entry_sha256"],
            created_file_hashes={path: "5" * 64},
        )
        prior_created.append(prior)
        complete[path] = "5" * 64
    ready = _ledger_entry(
        "READY_TO_SEAL", 392, prior["entry_sha256"], created_file_hashes=complete
    )

    result = contracts.validate_construction_ledger_bytes(
        b"".join(
            [
                _ledger_frame(first),
                *map(_ledger_frame, prior_created),
                _ledger_frame(ready),
            ]
        )
    )

    assert result.ledger_head_sha256 == ready["entry_sha256"]


def test_construction_ledger_prewrite_refused_requires_refusal_only() -> None:
    refused = _ledger_entry("PREWRITE_REFUSED", 0, None)

    with pytest.raises(SchemaContractError, match="refusal_reason_required"):
        contracts.validate_construction_ledger_bytes(_ledger_frame(refused))

    refused = _ledger_entry(
        "PREWRITE_REFUSED",
        0,
        None,
        refusal_reason_codes=["missing_hash"],
        created_file_hashes={"case_units/case-01/case_input.json": "4" * 64},
    )
    with pytest.raises(SchemaContractError, match="created_file_hashes_unexpected"):
        contracts.validate_construction_ledger_bytes(_ledger_frame(refused))


def test_construction_ledger_interrupted_partial_requires_terminal_observations() -> (
    None
):
    first = _ledger_entry("WRITE_STARTED", 0, None)
    interrupted = _ledger_entry(
        "INTERRUPTED_PARTIAL",
        1,
        first["entry_sha256"],
        refusal_reason_codes=["ledger_append_interrupted"],
        causal_entry_sha256_or_null=first["entry_sha256"],
    )

    with pytest.raises(SchemaContractError, match="partial_observation_required"):
        contracts.validate_construction_ledger_bytes(
            _ledger_frame(first) + _ledger_frame(interrupted)
        )

    interrupted = _ledger_entry(
        "INTERRUPTED_PARTIAL",
        1,
        first["entry_sha256"],
        observed_partial_file_hashes={
            "case_units/case-01/.g6b-tmp-token-case_input.json": "3" * 64
        },
        refusal_reason_codes=["ledger_append_interrupted"],
    )
    with pytest.raises(SchemaContractError, match="causal_entry_required"):
        contracts.validate_construction_ledger_bytes(
            _ledger_frame(first) + _ledger_frame(interrupted)
        )


@pytest.mark.parametrize("replicate_index", [-1, 4096, True, "0"])
def test_des_philox_key_rejects_invalid_replicate_indices(replicate_index: Any) -> None:
    with pytest.raises(SchemaContractError, match="invalid_replicate_index"):
        contracts.derive_des_philox_key_hex(
            seed_root_hex="1" * 64,
            case_content_sha256="2" * 64,
            replicate_index=replicate_index,
        )


def test_des_philox_key_accepts_replicate_domain_boundaries() -> None:
    for replicate_index in (0, 4095):
        digest = contracts.derive_des_philox_key_hex(
            seed_root_hex="1" * 64,
            case_content_sha256="2" * 64,
            replicate_index=replicate_index,
        )
        assert len(digest) == 64


def _file_created_entry(
    index: int,
    prior: JsonObject,
    path: str,
    digest: str,
) -> JsonObject:
    return _ledger_entry(
        "FILE_CREATED",
        index,
        prior["entry_sha256"],
        created_file_hashes={path: digest},
    )


def _ready_entry(index: int, prior: JsonObject, created: dict[str, str]) -> JsonObject:
    return _ledger_entry(
        "READY_TO_SEAL",
        index,
        prior["entry_sha256"],
        created_file_hashes=created,
    )


def _ledger_with_two_file_creates(
    *,
    second_path: str,
    second_digest: str,
) -> bytes:
    first = _ledger_entry("WRITE_STARTED", 0, None)
    created_0 = _file_created_entry(
        1,
        first,
        "case_units/case-000/case_input.json",
        "4" * 64,
    )
    created_1 = _file_created_entry(2, created_0, second_path, second_digest)
    return _ledger_frame(first) + _ledger_frame(created_0) + _ledger_frame(created_1)


@pytest.mark.parametrize("second_digest", ["4" * 64, "5" * 64])
def test_construction_ledger_rejects_repeated_file_created_path(
    second_digest: str,
) -> None:
    raw = _ledger_with_two_file_creates(
        second_path="case_units/case-000/case_input.json",
        second_digest=second_digest,
    )

    with pytest.raises(SchemaContractError, match="file_created_path_repeated"):
        contracts.validate_construction_ledger_bytes(raw)


def test_construction_ledger_ready_rejects_prior_hash_drift() -> None:
    first = _ledger_entry("WRITE_STARTED", 0, None)
    prior_created: list[JsonObject] = []
    prior = first
    cumulative: dict[str, str] = {}
    for index in range(391):
        path = f"case_units/case-{index:03d}/case_input.json"
        digest = "4" * 64 if index == 0 else "5" * 64
        prior = _file_created_entry(index + 1, prior, path, digest)
        prior_created.append(prior)
        cumulative[path] = digest
    cumulative["case_units/case-000/case_input.json"] = "5" * 64
    ready = _ready_entry(392, prior, cumulative)

    with pytest.raises(
        SchemaContractError, match="ready_to_seal_created_hashes_mismatch"
    ):
        contracts.validate_construction_ledger_bytes(
            b"".join(
                [
                    _ledger_frame(first),
                    *map(_ledger_frame, prior_created),
                    _ledger_frame(ready),
                ]
            )
        )


def test_construction_ledger_ready_rejects_missing_prior_path_even_with_391_count() -> (
    None
):
    first = _ledger_entry("WRITE_STARTED", 0, None)
    prior_created: list[JsonObject] = []
    prior = first
    cumulative: dict[str, str] = {}
    for index in range(391):
        path = f"case_units/case-{index:03d}/case_input.json"
        prior = _file_created_entry(index + 1, prior, path, "5" * 64)
        prior_created.append(prior)
        cumulative[path] = "5" * 64
    cumulative.pop("case_units/case-000/case_input.json")
    cumulative["case_units/case-999/case_input.json"] = "5" * 64
    ready = _ready_entry(392, prior, cumulative)

    with pytest.raises(
        SchemaContractError, match="ready_to_seal_created_hashes_mismatch"
    ):
        contracts.validate_construction_ledger_bytes(
            b"".join(
                [
                    _ledger_frame(first),
                    *map(_ledger_frame, prior_created),
                    _ledger_frame(ready),
                ]
            )
        )


def test_construction_ledger_ready_accepts_exact_cumulative_391_created_files() -> None:
    first = _ledger_entry("WRITE_STARTED", 0, None)
    prior_created: list[JsonObject] = []
    prior = first
    cumulative: dict[str, str] = {}
    for index in range(391):
        path = f"case_units/case-{index:03d}/case_input.json"
        digest = f"{index % 10}" * 64
        prior = _file_created_entry(index + 1, prior, path, digest)
        prior_created.append(prior)
        cumulative[path] = digest
    ready = _ready_entry(392, prior, cumulative)

    result = contracts.validate_construction_ledger_bytes(
        b"".join(
            [
                _ledger_frame(first),
                *map(_ledger_frame, prior_created),
                _ledger_frame(ready),
            ]
        )
    )

    assert result.ledger_head_sha256 == ready["entry_sha256"]


def test_construction_ledger_ready_rejects_before_391_cumulative_files() -> None:
    first = _ledger_entry("WRITE_STARTED", 0, None)
    created = _file_created_entry(
        1,
        first,
        "case_units/case-000/case_input.json",
        "4" * 64,
    )
    ready_map = {
        f"case_units/case-{index:03d}/case_input.json": "5" * 64 for index in range(391)
    }
    ready_map["case_units/case-000/case_input.json"] = "4" * 64
    ready = _ready_entry(2, created, ready_map)

    with pytest.raises(
        SchemaContractError, match="ready_to_seal_created_history_incomplete"
    ):
        contracts.validate_construction_ledger_bytes(
            _ledger_frame(first) + _ledger_frame(created) + _ledger_frame(ready)
        )
