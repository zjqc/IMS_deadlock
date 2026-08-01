from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal, cast

import pytest

from ims_deadlock import g6b_schema_contracts as contracts
from ims_deadlock.g6b_canonical_json import canonical_sha256_v2, finalized_self_hash
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
    validate_normalization_authorization,
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
        "source_head": "1" * 64,
        "source_tree_hash": "2" * 64,
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
            "repo_relative_posix_path": "governance/g6b/normalization-test",
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


def _retired_selector_rows() -> list[JsonObject]:
    return deepcopy(_load_retired_schema_definition()["allowed_json_fields_by_source"])


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
    validate_normalization_authorization(
        authorization,
        expected_inventory=schema["expected_source_inventory"],
        expected_selector_matrix=schema["allowed_json_fields_by_source"],
    )
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


def test_spec_17_3_38_schema_deterministic_parent_owned_subunits_reject_renamed_enclosing_ids() -> (  # noqa: E501
    None
):
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


def test_spec_18_schema_retired_authority_declared_sources_and_lineage_statuses_are_reproduced_without_outcome_reads() -> (  # noqa: E501
    None
):
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


def test_spec_17_3_31_schema_certified_records_require_runtime_hashes_and_estimand_id() -> (  # noqa: E501
    None
):
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


def test_spec_17_3_33_schema_failed_mandatory_control_blocks_quantitative_authorization() -> (  # noqa: E501
    None
):
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


def test_spec_17_3_35_schema_failure_refusal_negative_boundary_evidence_append_only() -> (  # noqa: E501
    None
):
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
    schema = _load_retired_schema_definition()
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
        validate_normalization_authorization(
            legacy,
            expected_inventory=schema["expected_source_inventory"],
            expected_selector_matrix=schema["allowed_json_fields_by_source"],
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


def test_spec_17_3_08_schema_renamed_retired_content_and_paraphrased_predictions_refuse() -> (  # noqa: E501
    None
):
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


def test_spec_17_3_09_schema_scientific_content_mutations_keep_correlations_dependent() -> (  # noqa: E501
    None
):
    record = _valid_dimension_comparison_record(dimension="case_content_sha256")
    _validate_dimension_comparison_positive(record)

    with pytest.raises(SchemaContractError, match="semantic_lineage_ambiguous"):
        validate_dimension_comparison_record(record)


def test_spec_17_3_10_schema_state_snapshot_is_pre_enumeration_parent_linked_subject_free() -> (  # noqa: E501
    None
):
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


def test_spec_17_3_20_schema_metric_reuse_requires_exact_companion_group_authorization() -> (  # noqa: E501
    None
):
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
