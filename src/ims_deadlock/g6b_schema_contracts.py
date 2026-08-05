"""Pure closed-vocabulary validators for G6-B schema contracts."""

from __future__ import annotations

import ast
import re
from collections import Counter
from collections.abc import Collection, Mapping, Sequence
from datetime import datetime
from types import MappingProxyType
from typing import Literal, TypeAlias

from ims_deadlock import g6b_canonical_json

JsonValue: TypeAlias = (
    None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
)
JsonPath: TypeAlias = tuple[str | int, ...]
_UNKNOWN_CALLABLE_ALIAS = "__g6b_unknown_callable__"
_SAFE_PATH_OBJECT_ALIAS = "__g6b_safe_path_object__"
_SAFE_HASH_OBJECT_ALIAS = "__g6b_safe_hash_object__"
_SAFE_JSON_OBJECT_ALIAS = "__g6b_safe_json_object__"
_SAFE_MAPPING_OBJECT_ALIAS = "__g6b_safe_mapping_object__"
_SAFE_PARAMETER_DATA_METHODS = frozenset(
    {
        ("record", "copy"),
        ("record", "get"),
        ("source_bytes", "strip"),
    }
)
_SAFE_CALL_RESULT_OBJECTS: Mapping[str, str] = {
    "pathlib.Path": _SAFE_PATH_OBJECT_ALIAS,
    "Path": _SAFE_PATH_OBJECT_ALIAS,
    "hashlib.sha256": _SAFE_HASH_OBJECT_ALIAS,
    "sha256": _SAFE_HASH_OBJECT_ALIAS,
    "json.loads": _SAFE_JSON_OBJECT_ALIAS,
    "json.load": _SAFE_JSON_OBJECT_ALIAS,
    "record.copy": _SAFE_MAPPING_OBJECT_ALIAS,
}
_SAFE_OBJECT_METHODS: Mapping[str, frozenset[str]] = {
    _SAFE_PATH_OBJECT_ALIAS: frozenset({"exists", "read_text"}),
    _SAFE_HASH_OBJECT_ALIAS: frozenset({"hexdigest"}),
    _SAFE_JSON_OBJECT_ALIAS: frozenset({"get"}),
    _SAFE_MAPPING_OBJECT_ALIAS: frozenset({"get"}),
}
_RESERVED_SAFE_ALIAS_NAMES = frozenset(_SAFE_OBJECT_METHODS)


class SchemaContractError(ValueError):
    """A fail-closed schema-contract refusal with a stable code."""

    code: str

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        super().__init__(code if not detail else f"{code}: {detail}")


CAPABILITY_NAMES = (
    "case_construction",
    "retired_authority_fingerprint_normalization",
    "target_certification_preflight",
    "quantitative_execution",
)
CAPABILITY_FIELDS = (
    "case_construction_authorized",
    "retired_authority_fingerprint_normalization_authorized",
    "target_certification_preflight_authorized",
    "quantitative_execution_authorized",
)
FINGERPRINT_DIMENSIONS = (
    "case_content_sha256",
    "state_snapshot_sha256",
    "route_signature_sha256",
    "parameter_tuple_sha256",
    "random_stream_manifest_sha256",
    "output_root_reservation_sha256",
    "sealed_prediction_sha256",
    "metric_schema_sha256",
)
PROJECTION_KINDS = (
    "controlled_schema",
    "provenance_containment",
    "random_process",
    "semantic_content",
)
COMPARISON_POLICIES = (
    "controlled_schema_reuse",
    "disjoint_random_substreams",
    "provenance_containment_only",
    "strict_semantic_distinctness",
)
DIMENSION_SUBJECTS = MappingProxyType(
    {
        "case_content_sha256": "case_unit",
        "state_snapshot_sha256": "case_unit",
        "route_signature_sha256": "case_unit",
        "parameter_tuple_sha256": "case_unit",
        "random_stream_manifest_sha256": "method_observation",
        "output_root_reservation_sha256": "method_observation",
        "sealed_prediction_sha256": "case_unit",
        "metric_schema_sha256": "method_companion_group",
    }
)
DIMENSION_PROJECTION_KINDS = MappingProxyType(
    {
        "case_content_sha256": "semantic_content",
        "state_snapshot_sha256": "semantic_content",
        "route_signature_sha256": "semantic_content",
        "parameter_tuple_sha256": "semantic_content",
        "random_stream_manifest_sha256": "random_process",
        "output_root_reservation_sha256": "provenance_containment",
        "sealed_prediction_sha256": "semantic_content",
        "metric_schema_sha256": "controlled_schema",
    }
)
DIMENSION_POLICIES = MappingProxyType(
    {
        "case_content_sha256": "strict_semantic_distinctness",
        "state_snapshot_sha256": "strict_semantic_distinctness",
        "route_signature_sha256": "strict_semantic_distinctness",
        "parameter_tuple_sha256": "strict_semantic_distinctness",
        "random_stream_manifest_sha256": "disjoint_random_substreams",
        "output_root_reservation_sha256": "provenance_containment_only",
        "sealed_prediction_sha256": "strict_semantic_distinctness",
        "metric_schema_sha256": "controlled_schema_reuse",
    }
)
FINGERPRINT_RECORD_REQUIRED_FIELDS = (
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
)
SOURCE_ARTIFACT_REF_REQUIRED_FIELDS = (
    "authority_id",
    "repo_relative_posix_path",
    "json_pointer_or_null",
    "source_role",
)
OUTPUT_ROOT_RESERVATION_REQUIRED_FIELDS = (
    "projection_schema_version",
    "bundle_id",
    "case_unit_id",
    "method_observation_id",
    "run_role",
    "logical_root_id",
    "repo_relative_posix_path",
    "reserved",
    "materialized",
    "reservation_sha256",
)
DIMENSION_COMPARISON_RECORD_REQUIRED_FIELDS = (
    "comparison_id",
    "bundle_id",
    "new_fingerprint_record_hash",
    "retired_fingerprint_record_hash",
    "dimension",
    "projection_kind",
    "new_subject_type",
    "new_subject_id",
    "retired_authority_id",
    "retired_lineage_id",
    "new_comparison_projection_sha256_or_null",
    "retired_comparison_projection_sha256_or_null",
    "comparison_policy",
    "comparison_status",
    "semantic_lineage_audit_ref_or_null",
    "reuse_authorization_ref_or_null",
    "refusal_reason_code_or_null",
    "comparison_record_sha256",
)
NORMALIZATION_AUTHORIZATION_REQUIRED_FIELDS = (
    "schema_version",
    "authorization_id",
    "capability",
    "authorized",
    "source_head",
    "source_tree_hash",
    "authority_ids",
    "expected_file_manifest_hash",
    "allowed_source_paths",
    "allowed_json_fields_by_source",
    "allowed_historical_builder_symbols",
    "normalizer_code_sha256",
    "allowed_operations",
    "allowed_project_imports",
    "forbidden_imports",
    "forbidden_calls",
    "allowed_output_schema",
    "allowed_output_root",
    "review_artifact_hash",
    "issued_at_utc",
    "invalidated_by_identity_drift",
    "authorization_sha256",
)
PREFLIGHT_AUTHORIZATION_REQUIRED_FIELDS = (
    "schema_version",
    "authorization_id",
    "capability",
    "authorized",
    "bundle_id",
    "case_unit_ids",
    "sealed_bundle_manifest_hash",
    "runtime_lock_sha256",
    "allowed_entrypoint",
    "allowed_command_manifest_hash",
    "allowed_operations",
    "allowed_output_schemas",
    "forbidden_calls",
    "forbidden_side_effects",
    "resource_budget",
    "stop_conditions",
    "preflight_evidence_root",
    "review_artifact_hash",
    "issued_at_utc",
    "invalidated_by_identity_drift",
    "authorization_sha256",
)
G6B_CANONICAL_JSON_VERSION = "ims-deadlock/g6b-canonical-json/v2"
LOWER_SHA256_HEX_DIGITS = frozenset("0123456789abcdef")
G6B_ALLOWED_ESTIMAND_IDS = frozenset(
    {
        "g6b_estimand_theta_global_before_success_v1",
        "g6b_estimand_theta_local_before_success_v1",
        "g6b_estimand_theta_selected_bad_before_success_v1",
    }
)
G6B_ESTIMAND_ID_SCOPE_CONTRACT: Mapping[str, object] = MappingProxyType(
    {
        "additional_allowed_paths": False,
        "allowed_predeclared_paths": (
            MappingProxyType(
                {
                    "allowed_use": (
                        "predeclared_directional_hypothesis_identifier_only"
                    ),
                    "json_pointer_pattern": "/directional_hypotheses/*/estimand_id",
                    "projection_role": "sealed_prediction_sha256",
                }
            ),
            MappingProxyType(
                {
                    "allowed_use": "predeclared_metric_identifier_only",
                    "json_pointer_pattern": "/metric_entries/*/estimand_id",
                    "projection_role": "metric_schema_sha256",
                }
            ),
        ),
        "allowed_value_codes": tuple(sorted(G6B_ALLOWED_ESTIMAND_IDS)),
        "default_policy": "recursive_prohibition",
        "runtime_certificate_observation_or_result_use": "prohibited",
    }
)
RETIRED_AUTHORITY_IDS = ("G4_FREEZE", "G5_EXECUTION", "G6_R_REPLAY_R3")
EXPECTED_RETIRED_SOURCE_INVENTORY = (
    "cases/confirmation/g4/FREEZE_ENTRY.json",
    "cases/confirmation/g4/case_manifest.json",
    "cases/confirmation/g4/cases/{case_id}.json",
    "cases/confirmation/g4/baseline_applicability.json",
    "cases/confirmation/g4/exclusions.json",
    "cases/confirmation/g4/experiment_scripts_manifest.json",
    "cases/confirmation/g4/metrics_schema.json",
    "cases/confirmation/g4/predictions.json",
    "cases/confirmation/g4/random_stream_manifest.json",
    "cases/confirmation/g4/runtime_lock.json",
    "cases/confirmation/g4/theory_manifest.json",
    "evidence/g5/G5_EXECUTION_LOCK.json",
    "evidence/g5/G5_RAW_HASH_MANIFEST.json",
    "evidence/g5/G5_RESULT_SUMMARY.json",
    "evidence/g5/G5_SCORING_ERRATUM.json",
    "evidence/g6/G6_HISTORICAL_REPLAY_LOCK_R3.json",
    "evidence/g6/G6_HISTORICAL_REPLAY_FAILURE_LEDGER.json",
    "evidence/g6/G6_HISTORICAL_REPLAY_R3_RAW_HASH_MANIFEST.json",
    "evidence/g6/G6_HISTORICAL_REPLAY_R3_REPORT.json",
)
G4_MANIFEST_CASE_IDS = (
    "G4_ADVERSARIAL_BOUNDARY",
    "G4_B05_SUPERVISOR_COMPARATOR",
    "G4_CRP_OUTSIDE_S4PR",
    "G4_CRP_S4PR_AGREE",
    "G4_CRP_UNREACHABLE_CANDIDATE",
    "G4_IMS_PARAMETER_GRID",
    "G4_L30_RESOURCE_BASELINE",
    "G4_MEDIUM_ISLAND_REBUILD",
    "G4_RECORDER_TARGET_QUANTIFICATION",
)
EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY = (
    EXPECTED_RETIRED_SOURCE_INVENTORY[0],
    EXPECTED_RETIRED_SOURCE_INVENTORY[1],
    *(
        f"cases/confirmation/g4/cases/{case_id}.json"
        for case_id in G4_MANIFEST_CASE_IDS
    ),
    *EXPECTED_RETIRED_SOURCE_INVENTORY[3:],
)
NORMALIZATION_ALLOWED_OPERATIONS = (
    "read_authority_bytes",
    "parse_allowed_json_pointers",
    "verify_source_hashes",
    "parse_historical_decimal_exactly",
    "apply_static_input_projection",
    "canonicalize_projection_v2",
    "compute_sha256",
    "write_normalization_manifest",
    "write_fingerprint_record",
)
NORMALIZATION_ALLOWED_PROJECT_IMPORTS = (
    "ims_deadlock.g6b_retired_normalizer",
    "ims_deadlock.g6b_canonical_json",
    "ims_deadlock.g6b_governance",
)
ALLOWED_NORMALIZER_WRITER_SYMBOLS = (
    "ims_deadlock.g6b_retired_normalizer.write_fingerprint_record",
    "ims_deadlock.g6b_retired_normalizer.write_normalization_manifest",
)
NORMALIZATION_FORBIDDEN_IMPORTS = (
    "ims_deadlock.analysis",
    "ims_deadlock.cases",
    "ims_deadlock.ctmc",
    "ims_deadlock.engine",
    "ims_deadlock.g4_instances",
    "ims_deadlock.g4_protocol",
    "ims_deadlock.g5_scoring",
    "ims_deadlock.historical_replay",
    "ims_deadlock.terminal_classes",
    "ims_deadlock.confirmation",
    "ims_deadlock.cli",
)
NORMALIZATION_FORBIDDEN_CALLS = (
    "enumerate_stable_lts",
    "partition_stable_lts",
    "certify_absorption_domain",
    "derive_absorbing_ctmc",
    "AbsorbingCTMC.solve",
    "engine.simulate",
    "g4_protocol.run_after_freeze",
    "g4_protocol.main",
    "g5_scoring.score_case",
    "g5_scoring.score_run",
    "g5_scoring.main",
    "historical_replay.main",
)
NORMALIZER_PROHIBITED_READ_NAMES = frozenset(
    {
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
    }
)
NORMALIZER_PROHIBITED_WRITE_CALLS = frozenset({"open", "write", "writelines"})
COMPOSITE_SUBUNIT_CONTRACTS = MappingProxyType(
    {
        "bidirectional_island_grid": (
            "/input_payload/protocol_input/cells/*",
            "cell_id",
            ("generator_id",),
        ),
        "supplied_l30_inequalities": (
            "/input_payload/protocol_input/inequalities/*",
            "name",
            (
                "capacities",
                "finite_capacity_s3pr_ens3pr",
                "inequality_provenance",
            ),
        ),
        "adapted_candidate_monitor_cover": (
            "/input_payload/protocol_input/candidate_monitors/*",
            "monitor_id",
            ("finite_lts", "legal_states", "first_met_bad_states", "state_bound"),
        ),
    }
)
SEMANTIC_COMPARISON_DIMENSIONS = frozenset(
    {
        "case_content_sha256",
        "state_snapshot_sha256",
        "route_signature_sha256",
        "parameter_tuple_sha256",
        "sealed_prediction_sha256",
    }
)
COMPARISON_FAIL_CLOSED_STATUSES = frozenset(
    {
        "overlap_hit",
        "missing_source",
        "unreconstructable",
        "normalizer_error",
        "semantic_lineage_ambiguous",
    }
)
COMPARISON_SUCCESS_STATUSES = frozenset(
    {
        "pass_distinct",
        "controlled_reuse_pass",
        "disjoint_stream_pass",
        "not_applicable_by_protocol_pass",
        "containment_separation_pass",
        "inherited_compared",
    }
)
INHERITED_COMPARISON_TERMINAL_STATUSES = frozenset(
    {
        "pass_distinct",
        "controlled_reuse_pass",
        "disjoint_stream_pass",
        "not_applicable_by_protocol_pass",
        "containment_separation_pass",
    }
)
DIMENSION_DEPENDS_ON = MappingProxyType(
    {
        "case_content_sha256": frozenset(
            {
                "state_snapshot_sha256",
                "route_signature_sha256",
                "parameter_tuple_sha256",
            }
        ),
        "state_snapshot_sha256": frozenset({"case_content_sha256"}),
        "route_signature_sha256": frozenset({"case_content_sha256"}),
        "parameter_tuple_sha256": frozenset({"case_content_sha256"}),
        "random_stream_manifest_sha256": frozenset(),
        "output_root_reservation_sha256": frozenset(),
        "sealed_prediction_sha256": frozenset(),
        "metric_schema_sha256": frozenset(),
    }
)
DIMENSION_CORRELATED_WITH = MappingProxyType(
    {
        "case_content_sha256": frozenset(
            {
                "state_snapshot_sha256",
                "route_signature_sha256",
                "parameter_tuple_sha256",
            }
        ),
        "state_snapshot_sha256": frozenset(
            {
                "case_content_sha256",
                "route_signature_sha256",
                "parameter_tuple_sha256",
            }
        ),
        "route_signature_sha256": frozenset(
            {
                "case_content_sha256",
                "state_snapshot_sha256",
                "parameter_tuple_sha256",
            }
        ),
        "parameter_tuple_sha256": frozenset(
            {
                "case_content_sha256",
                "state_snapshot_sha256",
                "route_signature_sha256",
            }
        ),
        "random_stream_manifest_sha256": frozenset(),
        "output_root_reservation_sha256": frozenset(),
        "sealed_prediction_sha256": frozenset(),
        "metric_schema_sha256": frozenset(),
    }
)
DIMENSION_NULL_PROJECTION_STATUSES = frozenset(
    {
        "not_applicable_retired_stage",
        "unreconstructable_refuse",
    }
)
BUNDLE_STATES = (
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
CASE_UNIT_STATES = (
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
METHOD_OBSERVATION_STATES = (
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
DIMENSION_STATUS_VALUES = (
    "direct_stored",
    "derived_by_versioned_normalizer",
    "inherited_from_authority",
    "not_applicable_by_protocol",
    "not_applicable_retired_stage",
    "unreconstructable_refuse",
)
COMPARISON_STATUS_VALUES = (
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

ALLOWED_OPERATIONS = (
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
ALLOWED_OUTPUT_SCHEMA_IDS = (
    "ims-deadlock/g6b-command-capture/v1",
    "ims-deadlock/g6b-filesystem-manifest/v1",
    "ims-deadlock/g6b-hash-manifest/v1",
    "ims-deadlock/g6b-preflight-failure-ledger-entry/v1",
    "ims-deadlock/g6b-target-certificate/v1",
    "ims-deadlock/g6b-target-certification-batch-manifest/v1",
    "ims-deadlock/g6b-target-certification-case-result/v1",
    "ims-deadlock/g6b-target-refusal/v1",
)
ALLOWED_FILE_ROLES = (
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
FILE_ROLE_TO_SCHEMA_ID = MappingProxyType(
    {
        "batch_manifest": "ims-deadlock/g6b-target-certification-batch-manifest/v1",
        "command_transcript": "ims-deadlock/g6b-command-capture/v1",
        "exit_code_capture": "ims-deadlock/g6b-command-capture/v1",
        "failure_ledger_entry": ("ims-deadlock/g6b-preflight-failure-ledger-entry/v1"),
        "filesystem_after_manifest": "ims-deadlock/g6b-filesystem-manifest/v1",
        "filesystem_before_manifest": "ims-deadlock/g6b-filesystem-manifest/v1",
        "hash_manifest": "ims-deadlock/g6b-hash-manifest/v1",
        "per_case_result": "ims-deadlock/g6b-target-certification-case-result/v1",
        "stderr_capture": "ims-deadlock/g6b-command-capture/v1",
        "target_certificate": "ims-deadlock/g6b-target-certificate/v1",
        "target_refusal": "ims-deadlock/g6b-target-refusal/v1",
    }
)

PREFLIGHT_PLACEHOLDER_CODES = (
    "case_scope_manifest",
    "preflight_authorization",
    "preflight_evidence_root",
    "python_runtime",
    "repo_source_root",
    "sealed_bundle_manifest",
)
QUANTITATIVE_PLACEHOLDER_CODES = (
    "case_input",
    "method_scope_manifest",
    "output_root",
    "python_runtime",
    "quantitative_authorization",
    "repo_source_root",
    "sealed_bundle_manifest",
    "target_certificate_manifest",
)
ALLOWED_ENVIRONMENT_VARIABLE_NAMES = ("PYTHONDONTWRITEBYTECODE", "PYTHONPATH")
SELECTOR_KINDS = (
    "exact_pointer_set",
    "prefix_set",
    "element_pointer_pattern_set",
    "raw_bytes_only",
)
ALLOWED_USE_VALUES = (
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
PREFLIGHT_COMMAND_MANIFEST_REQUIRED_FIELDS = (
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
PREFLIGHT_COMMAND_RECORD_REQUIRED_FIELDS = (
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
PREFLIGHT_RESOURCE_BUDGET_REQUIRED_FIELDS = (
    "max_wall_clock_seconds",
    "max_cpu_seconds",
    "max_memory_bytes",
    "max_storage_bytes",
    "max_states_per_case",
    "max_transitions_per_case",
    "max_cases",
    "max_workers",
)
PREFLIGHT_EVIDENCE_ROOT_REQUIRED_FIELDS = (
    "root_schema_version",
    "bundle_id",
    "repo_relative_posix_path",
    "state",
    "allowed_file_roles",
    "reservation_sha256",
)
QUANTITATIVE_COMMAND_MANIFEST_REQUIRED_FIELDS = (
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
QUANTITATIVE_COMMAND_RECORD_REQUIRED_FIELDS = (
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
OVERLAP_LOCK_REQUIRED_FIELDS = (
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
SOURCE_WORKTREE_IDENTITY_REQUIRED_FIELDS = frozenset(
    {
        "logical_worktree_id",
        "worktree_kind",
        "gitdir_file_sha256_or_null",
        "common_dir_identity_sha256",
        "worktree_admin_identity_sha256",
        "checked_out_tree_hash",
    }
)
OVERLAP_LOCK_WORKTREE_KIND = "linked"
OVERLAP_LOCK_DIRTY_STATE = "clean"

INPUT_OVERLAP_REPORT_REQUIRED_FIELDS = (
    "schema_version",
    "report_id",
    "bundle_id",
    "input_overlap_authority_lock_sha256",
    "sealed_bundle_manifest_sha256",
    "normalization_manifest_sha256",
    "declared_case_unit_ids",
    "declared_method_observation_ids",
    "declared_method_companion_group_ids",
    "new_fingerprint_record_hashes",
    "retired_fingerprint_record_hashes",
    "comparison_record_hashes",
    "semantic_lineage_audit_hashes",
    "metric_schema_reuse_record_hashes",
    "per_case_status",
    "per_method_status",
    "per_companion_group_status",
    "unique_retired_lineage_count",
    "inherited_record_count",
    "duplicate_lineage_record_count",
    "planned_case_count",
    "passed_case_count",
    "refused_case_count",
    "pending_case_count",
    "planned_method_count",
    "passed_method_count",
    "refused_method_count",
    "pending_method_count",
    "planned_companion_group_count",
    "passed_companion_group_count",
    "refused_companion_group_count",
    "pending_companion_group_count",
    "admission_policy_version",
    "report_status",
    "ledger_head_hash",
    "report_sha256",
)
OVERLAP_SUBJECT_STATUS_REQUIRED_FIELDS = (
    "subject_type",
    "subject_id",
    "required_fingerprint_record_hashes",
    "required_comparison_record_hashes",
    "required_lineage_audit_hashes",
    "required_reuse_record_hashes",
    "admission_status",
    "refusal_reason_codes",
    "ledger_entry_ids",
)
OVERLAP_ADMISSION_STATUS_VALUES = ("admitted", "refused", "pending")
OVERLAP_REPORT_STATUS_VALUES = (
    "complete_all_admitted",
    "complete_with_refusals",
    "incomplete_refused",
)

PREFLIGHT_CASE_RESULT_REQUIRED_FIELDS = (
    "schema_version",
    "bundle_id",
    "case_unit_id",
    "input_identity_hashes",
    "runtime_lock_sha256",
    "authorization_sha256",
    "result_status",
    "completeness_status",
    "state_count",
    "transition_count",
    "selected_target_identity",
    "state_space_hash",
    "partition_hash",
    "rate_manifest_hash",
    "positive_rate_graph_hash",
    "policy_filter_hash",
    "absorption_domain_hash",
    "estimand_id",
    "certificate_version",
    "certificate_status",
    "certificate_payload_or_null",
    "certificate_payload_sha256_or_null",
    "refusal_reason_codes",
    "refusal_details",
    "command_transcript_sha256",
    "stderr_sha256",
    "exit_code",
    "filesystem_before_manifest_sha256",
    "filesystem_after_manifest_sha256",
    "ledger_entry_ids",
)
PREFLIGHT_INPUT_IDENTITY_REQUIRED_FIELDS = (
    "case_content_sha256",
    "state_snapshot_sha256",
    "route_signature_sha256",
    "parameter_tuple_sha256",
    "sealed_prediction_sha256",
    "fingerprint_record_hashes_sha256",
)
PREFLIGHT_SELECTED_TARGET_REQUIRED_FIELDS = (
    "target_schema_version",
    "selected_bad_classes",
    "success_class",
    "exact_stopping_rule",
    "des_stopping_rule",
    "policy_analysis_class",
    "declaration_sha256",
)
SAME_TARGET_LOCK_REQUIRED_FIELDS = (
    "schema_version",
    "same_target_lock_id",
    "bundle_id",
    "case_unit_id",
    "method_companion_group_id",
    "exact_method_observation_id",
    "des_method_observation_id",
    "selected_bad_classes",
    "success_class",
    "target_schema_version",
    "estimand_schema_version",
    "state_space_hash",
    "partition_hash",
    "rate_manifest_hash",
    "positive_rate_graph_hash",
    "policy_filter_hash",
    "absorption_domain_hash",
    "certificate_artifact_hash",
    "estimand_id",
    "exact_stopping_rule_hash",
    "des_stopping_rule_hash",
    "metric_schema_sha256",
    "metric_reuse_authorization_hash",
    "exact_random_stream_manifest_sha256",
    "des_random_stream_manifest_sha256",
    "exact_output_root_reservation_sha256",
    "des_output_root_reservation_sha256",
    "lock_created_at_utc",
    "same_target_lock_sha256",
)
QUANTITATIVE_AUTHORIZATION_REQUIRED_FIELDS = (
    "schema_version",
    "authorization_id",
    "capability",
    "authorized",
    "bundle_id",
    "authorized_scope",
    "sealed_bundle_manifest_hash",
    "target_certification_batch_manifest_hash",
    "runtime_lock_sha256",
    "allowed_command_manifest_hash",
    "allowed_commands",
    "run_roles",
    "resource_budget",
    "output_root_policy",
    "stop_conditions",
    "review_artifact_hash",
    "issued_at_utc",
    "invalidated_by_identity_drift",
    "authorization_sha256",
)
QUANTITATIVE_AUTHORIZED_SCOPE_REQUIRED_FIELDS = (
    "case_unit_ids",
    "method_observation_ids",
    "certificate_hashes",
    "same_target_lock_hashes",
    "output_root_reservations",
)
QUANTITATIVE_RESOURCE_BUDGET_REQUIRED_FIELDS = (
    "max_wall_clock_seconds",
    "max_cpu_seconds",
    "max_memory_bytes",
    "max_storage_bytes",
    "max_cases",
    "max_concurrent_methods",
    "max_retries",
    "max_replicates_per_method",
)
QUANTITATIVE_OUTPUT_ROOT_POLICY_REQUIRED_FIELDS = (
    "root_template",
    "reservation_required",
    "unmaterialized_before_launch",
    "one_writer_per_method_run",
    "fallback_path_prohibited",
    "absolute_path_prohibited",
    "tracked_inventory_required",
    "no_cross_method_writes",
)
ALLOWED_PREFLIGHT_PROJECT_IMPORTS = (
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
ALLOWED_PREFLIGHT_WRITER_SYMBOLS = (
    "ims_deadlock.g6b_target_artifacts.write_certificate_record",
    "ims_deadlock.g6b_target_artifacts.write_refusal_record",
    "ims_deadlock.g6b_target_artifacts.write_batch_manifest",
    "ims_deadlock.g6b_target_artifacts.write_capture_record",
    "ims_deadlock.g6b_target_artifacts.write_filesystem_manifest",
    "ims_deadlock.g6b_target_artifacts.write_hash_manifest",
    "ims_deadlock.g6b_target_artifacts.append_failure_ledger",
)
PREFLIGHT_FORBIDDEN_IMPORTS = (
    "ims_deadlock.cases",
    "ims_deadlock.ctmc",
    "ims_deadlock.g4_instances",
    "ims_deadlock.g4_protocol",
    "ims_deadlock.g5_scoring",
    "ims_deadlock.historical_replay",
    "ims_deadlock.confirmation",
    "ims_deadlock.cli",
)
PREFLIGHT_FORBIDDEN_CALLS = (
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
PREFLIGHT_FORBIDDEN_RESULT_FIELDS = (
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
PREFLIGHT_FORBIDDEN_SIDE_EFFECTS = (
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
PREFLIGHT_ALLOWED_ENTRYPOINT = "ims_deadlock.g6b_target_preflight.main"
_POSITIVE_CANONICAL_DECIMAL_PATTERN = re.compile(r"^(0|[1-9][0-9]*)(\.[0-9]*[1-9])?$")
_VERSIONED_STOP_CONDITION_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*-v[1-9][0-9]*$")
PREFLIGHT_RECURSIVE_PROHIBITED_FIELDS = frozenset(
    PREFLIGHT_FORBIDDEN_RESULT_FIELDS
    + (
        "actual_overlap_result",
        "execution_result",
        "observed_result",
        "state_enumeration_result",
    )
)
OVERLAP_RECURSIVE_PROHIBITED_FIELDS = frozenset(
    {
        "authorized",
        "authorization_id",
        "bundle_id",
        "case_unit_id",
        "method_observation_id",
        "observed_result",
        "exact_output",
        "des_output",
        "state_enumeration_result",
        "metric_value",
        "actual_overlap_result",
        "current_runtime_lock",
    }
)
QUANTITATIVE_RECURSIVE_PROHIBITED_FIELDS = frozenset(
    {
        "actual_overlap_result",
        "des_estimate",
        "des_output",
        "des_trajectory",
        "exact_output",
        "execution_result",
        "metric_observations",
        "observed_result",
        "quantitative_output_root",
        "science_summary",
        "scientific_score",
        "state_enumeration_result",
        "theorem_falsification",
        "theorem_support",
        "wildcard_scope",
    }
)
NORMALIZATION_RECURSIVE_PROHIBITED_FIELDS = frozenset(
    {
        "actual_overlap_result",
        "authorization_id",
        "authorized",
        "bundle_id",
        "case_unit_id",
        "current_runtime_lock",
        "des_output",
        "exact_output",
        "execution_result",
        "method_observation_id",
        "metric_value",
        "observed_result",
        "quantitative_execution_authorized",
        "quantitative_output_root",
        "science_summary",
        "state_enumeration_result",
    }
)
ALL_RECURSIVE_PROHIBITED_FIELDS = frozenset().union(
    NORMALIZATION_RECURSIVE_PROHIBITED_FIELDS,
    OVERLAP_RECURSIVE_PROHIBITED_FIELDS,
    PREFLIGHT_RECURSIVE_PROHIBITED_FIELDS,
    QUANTITATIVE_RECURSIVE_PROHIBITED_FIELDS,
)
SIDE_EFFECT_IMPORT_ROOTS = frozenset(
    {
        "asyncio.subprocess",
        "ctypes",
        "ftplib",
        "http.client",
        "multiprocessing",
        "nt",
        "posix",
        "requests",
        "shutil",
        "socket",
        "subprocess",
        "telnetlib",
        "urllib.request",
    }
)
SIDE_EFFECT_CALL_PREFIXES = (
    "asyncio.create_subprocess_",
    "asyncio.subprocess.",
    "ctypes.",
    "ftplib.",
    "http.client.",
    "multiprocessing.",
    "os.exec",
    "os.popen",
    "os.spawn",
    "os.system",
    "requests.",
    "shutil.",
    "socket.",
    "subprocess.",
    "telnetlib.",
    "urllib.request.",
)
FILESYSTEM_MUTATOR_NAMES = frozenset(
    {
        "chmod",
        "chown",
        "link",
        "mkdir",
        "makedirs",
        "remove",
        "rename",
        "renames",
        "replace",
        "rmdir",
        "symlink",
        "touch",
        "truncate",
        "unlink",
        "write",
        "write_bytes",
        "write_text",
        "writelines",
    }
)
CROSS_GATE_REFUSAL_CODES = (
    "batch_incomplete",
    "canonicalization_violation",
    "missing_hash",
    "outcome_leakage",
    "runtime_identity_drift",
    "sealed_input_drift",
    "self_hash_mismatch",
)
CONSTRUCTION_REFUSAL_CODES = (
    "output_root_reuse_or_materialized",
    "subject_id_contaminated_projection",
    "unauthorized_case_creation_attempt",
    "unclassified_scientific_input",
)
NORMALIZATION_REFUSAL_CODES = (
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
OVERLAP_REFUSAL_CODES = (
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
PREFLIGHT_REFUSAL_CODES = (
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
QUANTITATIVE_REFUSAL_CODES = (
    "exact_des_target_mismatch",
    "failed_negative_control",
    "output_root_reuse_or_materialized",
    "quantitative_scope_violation",
    "retry_stop_policy_violation",
    "same_target_lock_stale",
    "unauthorized_quantitative_execution_attempt",
)
REFUSAL_CODE_GROUPS = MappingProxyType(
    {
        "cross_gate": CROSS_GATE_REFUSAL_CODES,
        "construction": CONSTRUCTION_REFUSAL_CODES,
        "normalization": NORMALIZATION_REFUSAL_CODES,
        "overlap": OVERLAP_REFUSAL_CODES,
        "preflight": PREFLIGHT_REFUSAL_CODES,
        "quantitative": QUANTITATIVE_REFUSAL_CODES,
    }
)

_PROJECTION_REQUIRED_KEYS = MappingProxyType(
    {
        "case_content_sha256": frozenset(
            {
                "projection_schema_version",
                "input_mode",
                "input_semantics_version",
                "state_snapshot_sha256",
                "route_signature_sha256",
                "parameter_tuple_sha256",
                "rate_manifest_content_sha256",
                "policy_declaration_content_sha256",
                "selected_target_declaration_sha256",
                "control_declaration_sha256",
            }
        ),
        "state_snapshot_sha256": frozenset(
            {
                "projection_schema_version",
                "input_mode",
                "state_payload_schema_version",
                "state_payload",
            }
        ),
        "route_signature_sha256": frozenset(
            {
                "projection_schema_version",
                "input_mode",
                "route_semantics_version",
                "typed_resource_roles",
                "typed_route_graph",
                "transition_kinds",
                "resource_demand_structure",
                "mode_transition_structure",
            }
        ),
        "parameter_tuple_sha256": frozenset(
            {
                "projection_schema_version",
                "parameter_semantics_version",
                "structural_parameter_entries",
                "numeric_parameter_entries",
                "state_bound",
                "rate_manifest_content_sha256",
                "policy_declaration_content_sha256",
            }
        ),
        "output_root_reservation_sha256": frozenset(
            {
                "projection_schema_version",
                "bundle_id",
                "case_unit_id",
                "method_observation_id",
                "run_role",
                "logical_root_id",
                "repo_relative_posix_path",
                "reserved",
                "materialized",
                "reservation_sha256",
            }
        ),
        "sealed_prediction_sha256": frozenset(
            {
                "projection_schema_version",
                "research_question",
                "directional_hypotheses",
                "falsifiers",
                "mandatory_control_roles",
                "planned_method_roles",
                "scoring_rule",
                "claim_boundary",
            }
        ),
        "metric_schema_sha256": frozenset(
            {
                "projection_schema_version",
                "estimand_schema_version",
                "metric_entries",
                "aggregation_rules",
                "censoring_rules",
                "failure_rules",
                "scoring_rules",
                "comparability_scope",
            }
        ),
    }
)
_RANDOM_STREAM_EXACT_KEYS = frozenset(
    {"projection_schema_version", "applicability_status", "method_role", "reason_code"}
)
_RANDOM_STREAM_STOCHASTIC_KEYS = frozenset(
    {
        "projection_schema_version",
        "applicability_status",
        "method_role",
        "prng_family",
        "prng_version",
        "seed_root_commitment",
        "seed_derivation_rule",
        "substream_allocation",
        "replicate_plan",
        "sampling_plan",
    }
)
_SUBJECT_CONTAMINATION_KEYS = frozenset(
    {
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
    }
)
_DOWNSTREAM_REFERENCE_KEYS = frozenset({"runtime_lock_sha256", "authorization_sha256"})
_SHELL_FORBIDDEN_FRAGMENTS = (
    ">",
    "<",
    "|",
    "$(",
    "`",
    ";",
    "&",
    "\n",
    "\r",
    "\x00",
)
_GLOB_FORBIDDEN_FRAGMENTS = ("*", "?", "[", "]")


def validate_exact_keys(
    value: Mapping[str, JsonValue],
    required: Collection[str],
    *,
    label: str,
) -> None:
    _validate_key_set(value, required, label=label)


def _validate_key_set(
    value: Mapping[str, object],
    required: Collection[str],
    *,
    label: str,
) -> None:
    actual = set(value)
    expected = set(required)
    missing = sorted(expected - actual)
    if missing:
        raise SchemaContractError("missing_key", f"{label}: {missing[0]}")
    extra = sorted(actual - expected)
    if extra:
        raise SchemaContractError("unexpected_key", f"{label}: {extra[0]}")


def validate_typed_capabilities(value: Mapping[str, JsonValue]) -> None:
    validate_exact_keys(value, CAPABILITY_FIELDS, label="typed_capabilities")
    for field in CAPABILITY_FIELDS:
        if value[field] is not False:
            raise SchemaContractError("capability_true", field)


def validate_subject_free_projection(
    dimension: str,
    projection: Mapping[str, JsonValue],
) -> None:
    if dimension not in FINGERPRINT_DIMENSIONS:
        raise SchemaContractError("unknown_dimension", dimension)
    _validate_estimand_id_scope(dimension, projection)
    if "state_space_hash" in projection and dimension == "state_snapshot_sha256":
        raise SchemaContractError("state_space_hash_substitution", dimension)
    if DIMENSION_PROJECTION_KINDS[dimension] != "provenance_containment":
        contamination = sorted(_find_contaminated_keys(projection))
        if contamination:
            raise SchemaContractError(
                "subject_id_contaminated_projection", contamination[0]
            )
    if dimension == "random_stream_manifest_sha256":
        actual = set(projection)
        if actual == _RANDOM_STREAM_EXACT_KEYS:
            if (
                projection.get("applicability_status") != "not_applicable_by_protocol"
                or projection.get("method_role") != "exact_companion"
            ):
                raise SchemaContractError("random_stream_branch_mismatch")
            return
        if actual == _RANDOM_STREAM_STOCHASTIC_KEYS:
            if (
                projection.get("applicability_status") != "applicable"
                or projection.get("method_role") != "des_companion"
            ):
                raise SchemaContractError("random_stream_branch_mismatch")
            return
        missing = sorted(_RANDOM_STREAM_EXACT_KEYS - actual)
        if missing:
            raise SchemaContractError("missing_key", missing[0])
        raise SchemaContractError("unclassified_scientific_input")
    required = _PROJECTION_REQUIRED_KEYS.get(dimension)
    if required is not None:
        actual = set(projection)
        missing = sorted(required - actual)
        if missing:
            raise SchemaContractError("missing_key", missing[0])
        extra = sorted(actual - required)
        if extra:
            raise SchemaContractError("unclassified_scientific_input", extra[0])


def _validate_estimand_id_scope(
    projection_role: str,
    payload: Mapping[str, JsonValue],
) -> None:
    for path, value in _find_estimand_id_paths(payload):
        if not _is_allowed_estimand_id_path(projection_role, path):
            raise SchemaContractError("estimand_id_scope_violation", _format_path(path))
        if not isinstance(value, str) or value not in G6B_ALLOWED_ESTIMAND_IDS:
            raise SchemaContractError("estimand_id_scope_violation", _format_path(path))


def _is_allowed_estimand_id_path(projection_role: str, path: JsonPath) -> bool:
    if projection_role == "sealed_prediction_sha256":
        return (
            len(path) == 3
            and path[0] == "directional_hypotheses"
            and isinstance(path[1], int)
            and path[2] == "estimand_id"
        )
    if projection_role == "metric_schema_sha256":
        return (
            len(path) == 3
            and path[0] == "metric_entries"
            and isinstance(path[1], int)
            and path[2] == "estimand_id"
        )
    return False


def validate_fingerprint_record(
    record: Mapping[str, JsonValue],
    projection: Mapping[str, JsonValue] | None,
) -> None:
    validate_exact_keys(
        record,
        FINGERPRINT_RECORD_REQUIRED_FIELDS,
        label="fingerprint_record",
    )
    dimension = record.get("dimension")
    if not isinstance(dimension, str) or dimension not in FINGERPRINT_DIMENSIONS:
        raise SchemaContractError("unknown_dimension")
    if record.get("projection_kind") != DIMENSION_PROJECTION_KINDS[dimension]:
        raise SchemaContractError("projection_kind_mismatch", dimension)
    if record.get("subject_type") != DIMENSION_SUBJECTS[dimension]:
        raise SchemaContractError("subject_type_mismatch", dimension)
    if record.get("comparison_policy") != DIMENSION_POLICIES[dimension]:
        raise SchemaContractError("comparison_policy_mismatch", dimension)
    if record.get("canonicalization_version") != G6B_CANONICAL_JSON_VERSION:
        raise SchemaContractError("canonicalization_version_mismatch")
    if record.get("dimension_status") not in DIMENSION_STATUS_VALUES:
        raise SchemaContractError("unknown_dimension_status", dimension)
    if record.get("projection_schema_version") in (None, ""):
        raise SchemaContractError("projection_schema_version_missing", dimension)
    _validate_dimension_relation(
        record.get("depends_on_dimensions"),
        DIMENSION_DEPENDS_ON[dimension],
        label="depends_on_dimensions",
    )
    _validate_dimension_relation(
        record.get("correlated_with_dimensions"),
        DIMENSION_CORRELATED_WITH[dimension],
        label="correlated_with_dimensions",
    )
    _validate_source_artifacts(
        record.get("source_artifact_refs"),
        record.get("source_artifact_byte_hashes"),
    )
    declared_hash = record.get("comparison_projection_sha256_or_null")
    projection_ref = record.get("comparison_projection_ref_or_null")
    if projection is None:
        if declared_hash is not None or projection_ref is not None:
            raise SchemaContractError("projection_null_relation_mismatch", dimension)
        if record.get("dimension_status") not in DIMENSION_NULL_PROJECTION_STATUSES:
            raise SchemaContractError("missing_source", dimension)
    else:
        if projection_ref is None:
            raise SchemaContractError("projection_ref_missing", dimension)
        if projection.get("projection_schema_version") != record.get(
            "projection_schema_version"
        ):
            raise SchemaContractError("projection_schema_version_mismatch", dimension)
        validate_subject_free_projection(dimension, projection)
        expected_hash = g6b_canonical_json.canonical_sha256_v2(dict(projection))
        if declared_hash != expected_hash:
            raise SchemaContractError("comparison_projection_hash_mismatch", dimension)
    _verify_finalized_self_hash(record, "record_provenance_sha256")


def validate_output_root_reservation(record: Mapping[str, JsonValue]) -> None:
    validate_exact_keys(
        record,
        OUTPUT_ROOT_RESERVATION_REQUIRED_FIELDS,
        label="output_root_reservation",
    )
    if record.get("projection_schema_version") in (None, ""):
        raise SchemaContractError("projection_schema_version_missing")
    if record.get("reserved") is not True:
        raise SchemaContractError("output_root_not_reserved")
    if record.get("materialized") is not False:
        raise SchemaContractError("output_root_materialized")
    bundle_id = _require_nonempty_string(record.get("bundle_id"), "bundle_id")
    case_unit_id = _require_nonempty_string(record.get("case_unit_id"), "case_unit_id")
    method_observation_id = _require_nonempty_string(
        record.get("method_observation_id"),
        "method_observation_id",
    )
    run_role = _require_nonempty_string(record.get("run_role"), "run_role")
    _require_nonempty_string(
        record.get("logical_root_id"),
        "logical_root_id",
    )
    path = _require_nonempty_string(
        record.get("repo_relative_posix_path"),
        "repo_relative_posix_path",
    )
    _validate_repo_relative_path(path)
    expected_path = (
        "artifacts/g6b/quantitative/"
        f"{bundle_id}/{case_unit_id}/{method_observation_id}/{run_role}"
    )
    if path != expected_path:
        raise SchemaContractError("output_root_path_mismatch")
    _verify_finalized_self_hash(record, "reservation_sha256")


def validate_dimension_comparison_record(
    record: Mapping[str, JsonValue],
    *,
    semantic_lineage_audit_passed: bool | None = None,
    random_stream_branch: Literal["exact", "stochastic"] | None = None,
    disjoint_substream_proof_passed: bool | None = None,
    metric_reuse_authorized: bool | None = None,
    unique_ancestor_status: str | None = None,
) -> None:
    validate_exact_keys(
        record,
        DIMENSION_COMPARISON_RECORD_REQUIRED_FIELDS,
        label="dimension_comparison_record",
    )
    dimension = record.get("dimension")
    if not isinstance(dimension, str) or dimension not in FINGERPRINT_DIMENSIONS:
        raise SchemaContractError("unknown_dimension")
    if record.get("projection_kind") != DIMENSION_PROJECTION_KINDS[dimension]:
        raise SchemaContractError("projection_kind_mismatch", dimension)
    if record.get("new_subject_type") != DIMENSION_SUBJECTS[dimension]:
        raise SchemaContractError("subject_type_mismatch", dimension)
    if record.get("comparison_policy") != DIMENSION_POLICIES[dimension]:
        raise SchemaContractError("comparison_policy_mismatch", dimension)
    status = record.get("comparison_status")
    if not isinstance(status, str) or status not in COMPARISON_STATUS_VALUES:
        raise SchemaContractError("unknown_comparison_status", dimension)
    _validate_lower_sha256(
        record.get("new_fingerprint_record_hash"),
        label="new_fingerprint_record_hash",
    )
    _validate_lower_sha256(
        record.get("retired_fingerprint_record_hash"),
        label="retired_fingerprint_record_hash",
    )
    new_projection_hash = _validate_optional_projection_hash(
        record.get("new_comparison_projection_sha256_or_null"),
        label="new_comparison_projection_sha256_or_null",
    )
    retired_projection_hash = _validate_optional_projection_hash(
        record.get("retired_comparison_projection_sha256_or_null"),
        label="retired_comparison_projection_sha256_or_null",
    )
    semantic_ref = record.get("semantic_lineage_audit_ref_or_null")
    reuse_ref = record.get("reuse_authorization_ref_or_null")
    refusal_code = record.get("refusal_reason_code_or_null")
    _validate_nullable_ref(semantic_ref, label="semantic_lineage_audit_ref_or_null")
    _validate_nullable_ref(reuse_ref, label="reuse_authorization_ref_or_null")
    _validate_nullable_refusal_code(refusal_code)
    _validate_comparison_status_refusals(status, refusal_code)
    if status == "inherited_compared":
        if unique_ancestor_status not in INHERITED_COMPARISON_TERMINAL_STATUSES:
            raise SchemaContractError("unique_ancestor_status_not_allowed", dimension)
    elif unique_ancestor_status is not None:
        raise SchemaContractError("unique_ancestor_status_unexpected", dimension)
    if dimension in SEMANTIC_COMPARISON_DIMENSIONS:
        _validate_semantic_dimension_comparison(
            dimension=dimension,
            status=status,
            new_projection_hash=new_projection_hash,
            retired_projection_hash=retired_projection_hash,
            semantic_lineage_audit_ref=semantic_ref,
            semantic_lineage_audit_passed=semantic_lineage_audit_passed,
        )
    elif dimension == "random_stream_manifest_sha256":
        _validate_random_stream_comparison(
            status=status,
            new_projection_hash=new_projection_hash,
            retired_projection_hash=retired_projection_hash,
            random_stream_branch=random_stream_branch,
            disjoint_substream_proof_passed=disjoint_substream_proof_passed,
        )
    elif dimension == "output_root_reservation_sha256":
        _validate_output_root_comparison(
            status=status,
            new_projection_hash=new_projection_hash,
            retired_projection_hash=retired_projection_hash,
        )
    elif dimension == "metric_schema_sha256":
        _validate_metric_schema_comparison(
            status=status,
            new_projection_hash=new_projection_hash,
            retired_projection_hash=retired_projection_hash,
            reuse_authorization_ref=reuse_ref,
            metric_reuse_authorized=metric_reuse_authorized,
        )
    _verify_finalized_self_hash(record, "comparison_record_sha256")


def validate_retired_inventory(
    *,
    expected_paths: Sequence[str],
    observed_paths: Sequence[str],
    stale_paths: Sequence[str] = (),
    mismatched_paths: Sequence[str] = (),
    local_only_paths: Sequence[str] = (),
    unverified_paths: Sequence[str] = (),
) -> None:
    expected_values = _as_string_sequence(expected_paths, "expected_paths")
    observed_values = _as_string_sequence(observed_paths, "observed_paths")
    if len(set(expected_values)) != len(expected_values):
        raise SchemaContractError("set_array_duplicate", "expected_paths")
    if len(set(observed_values)) != len(observed_values):
        raise SchemaContractError("set_array_duplicate", "observed_paths")
    if expected_values != EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY:
        raise SchemaContractError("missing_retired_authority")
    expected = set(expected_values)
    observed = set(observed_values)
    _validate_inventory_fail_category(
        stale_paths,
        expected,
        code="retired_authority_hash_mismatch",
        label="stale_paths",
    )
    _validate_inventory_fail_category(
        mismatched_paths,
        expected,
        code="retired_authority_hash_mismatch",
        label="mismatched_paths",
    )
    _validate_inventory_fail_category(
        local_only_paths,
        expected,
        code="missing_retired_authority",
        label="local_only_paths",
    )
    _validate_inventory_fail_category(
        unverified_paths,
        expected,
        code="missing_retired_authority",
        label="unverified_paths",
    )
    if observed != expected:
        missing = expected - observed
        if missing:
            raise SchemaContractError("missing_retired_authority", min(missing))
        extra = observed - expected
        if extra:
            raise SchemaContractError("unexpected_key", min(extra))


def validate_source_selector_matrix(matrix: Sequence[Mapping[str, JsonValue]]) -> None:
    seen_rows: set[tuple[str, str, tuple[str, ...], str]] = set()
    for row in matrix:
        validate_exact_keys(
            row,
            {"source_path_pattern", "selector_kind", "selectors", "allowed_use"},
            label="source_selector_row",
        )
        source_path = _require_nonempty_string(
            row.get("source_path_pattern"),
            "source_path_pattern",
        )
        selector_kind_value = row.get("selector_kind")
        if (
            not isinstance(selector_kind_value, str)
            or selector_kind_value not in SELECTOR_KINDS
        ):
            raise SchemaContractError("unknown_selector_kind")
        selector_kind = selector_kind_value
        allowed_use_value = row.get("allowed_use")
        if (
            not isinstance(allowed_use_value, str)
            or allowed_use_value not in ALLOWED_USE_VALUES
        ):
            raise SchemaContractError("unknown_allowed_use")
        allowed_use = allowed_use_value
        selectors = row.get("selectors")
        if selector_kind == "raw_bytes_only":
            if selectors != []:
                raise SchemaContractError("raw_bytes_only_json_parse", source_path)
            selector_tuple: tuple[str, ...] = ()
        else:
            selector_tuple = _as_string_sequence(selectors, "selectors")
            if len(set(selector_tuple)) != len(selector_tuple):
                raise SchemaContractError("set_array_duplicate", "selectors")
            for selector in selector_tuple:
                if not selector.startswith("/"):
                    raise SchemaContractError("json_pointer_contract")
        row_key = (source_path, selector_kind, selector_tuple, allowed_use)
        if row_key in seen_rows:
            raise SchemaContractError("source_selector_row_duplicate", source_path)
        seen_rows.add(row_key)


def validate_lineage_deduplication(
    records: Sequence[Mapping[str, JsonValue]],
    *,
    declared_unique_lineage_count: int,
) -> None:
    if (
        type(declared_unique_lineage_count) is not int
        or declared_unique_lineage_count < 0
    ):
        raise SchemaContractError("duplicate_lineage_miscount")
    by_record_id: dict[str, Mapping[str, JsonValue]] = {}
    for record in records:
        record_id = _require_nonempty_string(record.get("record_id"), "record_id")
        if record_id in by_record_id:
            raise SchemaContractError("set_array_duplicate", record_id)
        by_record_id[record_id] = record
        dimension = record.get("dimension")
        if dimension not in FINGERPRINT_DIMENSIONS:
            raise SchemaContractError("unknown_dimension")
        status = record.get("dimension_status")
        if status not in DIMENSION_STATUS_VALUES:
            raise SchemaContractError("unknown_dimension_status")
    unique_lineages: set[str] = set()
    for record_id, record in by_record_id.items():
        lineage_id = _require_nonempty_string(record.get("lineage_id"), "lineage_id")
        inherited = record.get("inherited_from_record_id_or_null")
        duplicate = record.get("duplicate_lineage_of_record_id_or_null")
        if inherited is not None and duplicate is not None:
            raise SchemaContractError("duplicate_lineage_miscount", record_id)
        if inherited is None and duplicate is None:
            if lineage_id != _expected_origin_lineage_id(record):
                raise SchemaContractError("semantic_lineage_ambiguous", record_id)
            unique_lineages.add(lineage_id)
            continue
        target_id = inherited if inherited is not None else duplicate
        if not isinstance(target_id, str) or target_id not in by_record_id:
            raise SchemaContractError("semantic_lineage_ambiguous", record_id)
        target = by_record_id[target_id]
        if target.get("lineage_id") != lineage_id:
            raise SchemaContractError("duplicate_lineage_miscount", record_id)
        _reject_failure_status_upgrade(record, target)
    if len(unique_lineages) != declared_unique_lineage_count:
        raise SchemaContractError("duplicate_lineage_miscount")


def validate_normalization_authorization(
    record: Mapping[str, JsonValue],
    *,
    expected_inventory: Sequence[str] | None = None,
    expected_selector_matrix: Sequence[Mapping[str, JsonValue]] | None = None,
) -> None:
    validate_exact_keys(
        record,
        NORMALIZATION_AUTHORIZATION_REQUIRED_FIELDS,
        label="normalization_authorization",
    )
    if record.get("capability") != "retired_authority_fingerprint_normalization":
        raise SchemaContractError("capability_mismatch")
    if (
        record.get("schema_version")
        != "ims-deadlock/g6b-retired-normalization-authorization/v1"
    ):
        raise SchemaContractError("schema_version_drift")
    _require_nonempty_string(record.get("authorization_id"), "authorization_id")
    if record.get("authorized") is not True:
        raise SchemaContractError("unauthorized_retired_normalization_attempt")
    if (
        _as_string_sequence(record.get("authority_ids"), "authority_ids")
        != RETIRED_AUTHORITY_IDS
    ):
        raise SchemaContractError("missing_retired_authority")
    for field in (
        "source_head",
        "source_tree_hash",
        "expected_file_manifest_hash",
        "normalizer_code_sha256",
        "review_artifact_hash",
    ):
        _validate_lower_sha256(record.get(field), label=field)
    allowed_source_paths = _as_string_sequence(
        record.get("allowed_source_paths"),
        "allowed_source_paths",
    )
    if expected_inventory is None or expected_selector_matrix is None:
        raise SchemaContractError("missing_normalization_authorization")
    schema_inventory = tuple(expected_inventory)
    if schema_inventory != EXPECTED_RETIRED_SOURCE_INVENTORY:
        raise SchemaContractError("missing_retired_authority")
    expected_paths = EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY
    validate_retired_inventory(
        expected_paths=expected_paths,
        observed_paths=allowed_source_paths,
    )
    if tuple(allowed_source_paths) != tuple(expected_paths):
        raise SchemaContractError("missing_retired_authority")
    matrix = record.get("allowed_json_fields_by_source")
    if not isinstance(matrix, list):
        raise SchemaContractError("source_selector_row")
    matrix_rows: list[Mapping[str, JsonValue]] = []
    for row in matrix:
        if not isinstance(row, Mapping):
            raise SchemaContractError("source_selector_row")
        matrix_rows.append(row)
    validate_source_selector_matrix(matrix_rows)
    if [dict(row) for row in matrix_rows] != [
        dict(row) for row in expected_selector_matrix
    ]:
        raise SchemaContractError("source_field_read_violation")
    if record.get("allowed_historical_builder_symbols") != []:
        raise SchemaContractError("retired_normalizer_error")
    if (
        _as_string_sequence(record.get("allowed_operations"), "allowed_operations")
        != NORMALIZATION_ALLOWED_OPERATIONS
    ):
        raise SchemaContractError("operation_contract_drift")
    if (
        _as_string_sequence(
            record.get("allowed_project_imports"),
            "allowed_project_imports",
        )
        != NORMALIZATION_ALLOWED_PROJECT_IMPORTS
    ):
        raise SchemaContractError("capability_import_violation")
    if (
        _as_string_sequence(record.get("forbidden_imports"), "forbidden_imports")
        != NORMALIZATION_FORBIDDEN_IMPORTS
    ):
        raise SchemaContractError("capability_import_violation")
    if (
        _as_string_sequence(record.get("forbidden_calls"), "forbidden_calls")
        != NORMALIZATION_FORBIDDEN_CALLS
    ):
        raise SchemaContractError("capability_call_violation")
    _validate_output_schema_and_root(
        record.get("allowed_output_schema"),
        record.get("allowed_output_root"),
    )
    _validate_utc_timestamp(record.get("issued_at_utc"), label="issued_at_utc")
    if record.get("invalidated_by_identity_drift") is not False:
        raise SchemaContractError("runtime_identity_drift")
    _verify_finalized_self_hash(record, "authorization_sha256")


def validate_normalizer_source_guard(source: str) -> None:
    if not isinstance(source, str):
        raise SchemaContractError("retired_normalizer_error")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise SchemaContractError("retired_normalizer_error") from exc
    if any(isinstance(node, ast.ClassDef) for node in ast.walk(tree)):
        raise SchemaContractError("retired_normalizer_error")
    if _uses_reserved_safe_alias_name(tree):
        raise SchemaContractError("retired_normalizer_error")
    aliases: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                _validate_normalizer_import(alias.name)
                if alias.asname is not None:
                    _add_callable_alias(aliases, alias.asname, {alias.name})
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            _validate_normalizer_import(module_name)
            for alias in node.names:
                if alias.name == "*":
                    raise SchemaContractError("capability_import_violation")
                _add_callable_alias(
                    aliases,
                    alias.asname or alias.name,
                    {f"{module_name}.{alias.name}"},
                )
    _extend_callable_assignment_aliases(tree, aliases)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Subscript):
                raise SchemaContractError("capability_call_violation")
            call_names = _ast_callable_value_names(node.func, aliases)
            if not call_names:
                raise SchemaContractError("capability_call_violation")
            for call_name in call_names:
                if _is_unknown_callable_alias(call_name):
                    raise SchemaContractError("retired_normalizer_error", call_name)
                _validate_normalizer_call(call_name, node)
            _reject_sensitive_callable_escapes(
                node,
                aliases,
                error_code="retired_normalizer_error",
            )
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in NORMALIZER_PROHIBITED_READ_NAMES:
                raise SchemaContractError("source_field_read_violation", node.value)
        elif isinstance(node, ast.Name) and node.id in NORMALIZER_PROHIBITED_READ_NAMES:
            raise SchemaContractError("source_field_read_violation", node.id)


def validate_g4_manifest_freeze_reconciliation(
    manifest_rows: Sequence[Mapping[str, JsonValue]],
    *,
    included_case_ids: Sequence[str] | None = None,
    freeze_case_hashes: Mapping[str, str] | None = None,
    case_base_path: str = "cases/confirmation/g4",
) -> None:
    rows_by_id: dict[str, Mapping[str, JsonValue]] = {}
    for row in manifest_rows:
        validate_exact_keys(
            row,
            {"case_id", "repo_relative_posix_path", "declared_sha256"},
            label="g4_manifest_row",
        )
        case_id = _require_nonempty_string(row.get("case_id"), "case_id")
        _validate_lower_sha256(row.get("declared_sha256"), label=case_id)
        path = _require_nonempty_string(
            row.get("repo_relative_posix_path"),
            "repo_relative_posix_path",
        )
        _validate_repo_relative_path(path)
        expected_path = f"{case_base_path}/cases/{case_id}.json"
        if not path.startswith(f"{case_base_path}/cases/"):
            raise SchemaContractError("repo_relative_path_violation", path)
        if path != expected_path:
            raise SchemaContractError("retired_authority_hash_mismatch", case_id)
        if case_id in rows_by_id:
            raise SchemaContractError("set_array_duplicate", case_id)
        rows_by_id[case_id] = row
    expected_ids = (
        tuple(included_case_ids)
        if included_case_ids is not None
        else G4_MANIFEST_CASE_IDS
    )
    if expected_ids != G4_MANIFEST_CASE_IDS:
        raise SchemaContractError("set_array_not_sorted", "included_case_ids")
    actual_ids = set(rows_by_id)
    expected_id_set = set(expected_ids)
    if actual_ids != expected_id_set:
        if expected_id_set - actual_ids:
            raise SchemaContractError("missing_retired_authority")
        raise SchemaContractError("unexpected_key")
    for case_id in expected_ids:
        row = rows_by_id[case_id]
        expected_path = f"{case_base_path}/cases/{case_id}.json"
        if row.get("repo_relative_posix_path") != expected_path:
            raise SchemaContractError("retired_authority_hash_mismatch", case_id)
    if freeze_case_hashes is not None:
        if set(freeze_case_hashes) != expected_id_set:
            raise SchemaContractError("retired_authority_hash_mismatch")
        for case_id, digest in freeze_case_hashes.items():
            _validate_lower_sha256(digest, label=case_id)
            if rows_by_id[case_id].get("declared_sha256") != digest:
                raise SchemaContractError("retired_authority_hash_mismatch", case_id)


def validate_composite_subunit_record(record: Mapping[str, JsonValue]) -> None:
    validate_exact_keys(
        record,
        {
            "parent_case_id",
            "owner_object_id",
            "protocol_kind",
            "selector",
            "unique_key",
            "subunit_id_component",
            "parent_context_fields",
            "canonical_payload_sha256",
        },
        label="composite_subunit_record",
    )
    parent_case_id = _require_nonempty_string(
        record.get("parent_case_id"),
        "parent_case_id",
    )
    if record.get("owner_object_id") != parent_case_id:
        raise SchemaContractError("semantic_lineage_ambiguous")
    protocol_kind = _require_nonempty_string(
        record.get("protocol_kind"),
        "protocol_kind",
    )
    if protocol_kind not in COMPOSITE_SUBUNIT_CONTRACTS:
        raise SchemaContractError("retired_normalizer_error")
    selector, unique_key, parent_context = COMPOSITE_SUBUNIT_CONTRACTS[protocol_kind]
    if record.get("selector") != selector:
        raise SchemaContractError("source_field_read_violation")
    if record.get("unique_key") != unique_key:
        raise SchemaContractError("semantic_lineage_ambiguous")
    _require_nonempty_string(
        record.get("subunit_id_component"),
        "subunit_id_component",
    )
    if (
        _as_string_sequence(
            record.get("parent_context_fields"), "parent_context_fields"
        )
        != parent_context
    ):
        raise SchemaContractError("source_field_read_violation")
    _validate_lower_sha256(
        record.get("canonical_payload_sha256"),
        label="canonical_payload_sha256",
    )


def validate_retired_authority_source_inventory(
    inventory: Sequence[Mapping[str, JsonValue]],
    *,
    expected_hashes: Mapping[str, str],
    selector_rows: Sequence[Mapping[str, JsonValue]] | None = None,
    schema_definition: Mapping[str, JsonValue] | None = None,
) -> None:
    if schema_definition is None:
        raise SchemaContractError("missing_retired_authority")
    expected_value = schema_definition.get("expected_source_inventory")
    if not isinstance(expected_value, list):
        raise SchemaContractError("missing_retired_authority")
    expected_patterns = _as_string_sequence(
        expected_value,
        "expected_source_inventory",
    )
    if expected_patterns != EXPECTED_RETIRED_SOURCE_INVENTORY:
        raise SchemaContractError("missing_retired_authority")
    expected_paths = EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY
    if set(expected_hashes) != set(expected_paths):
        raise SchemaContractError("retired_authority_hash_mismatch")
    if len(inventory) != len(expected_paths):
        raise SchemaContractError("missing_retired_authority")
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for expected_path, row in zip(expected_paths, inventory, strict=True):
        for field in (
            "authority_id",
            "source_id",
            "repo_relative_posix_path",
            "declared_sha256",
            "verification_status",
            "lineage_status",
            "local_only",
        ):
            if field not in row:
                raise SchemaContractError("missing_retired_authority", field)
        validate_exact_keys(
            row,
            {
                "authority_id",
                "source_id",
                "repo_relative_posix_path",
                "declared_sha256",
                "verification_status",
                "lineage_status",
                "local_only",
            },
            label="retired_source_inventory_row",
        )
        source_id = _require_nonempty_string(row.get("source_id"), "source_id")
        if source_id in seen_ids:
            raise SchemaContractError("set_array_duplicate", source_id)
        seen_ids.add(source_id)
        path = _require_nonempty_string(
            row.get("repo_relative_posix_path"),
            "repo_relative_posix_path",
        )
        _validate_repo_relative_path(path)
        if path in seen_paths:
            raise SchemaContractError("set_array_duplicate", path)
        seen_paths.add(path)
        if path != expected_path:
            raise SchemaContractError("missing_retired_authority", expected_path)
        expected_authority_id = (
            "G4_FREEZE"
            if path.startswith("cases/confirmation/g4/")
            else "G5_EXECUTION"
            if path.startswith("evidence/g5/")
            else "G6_R_REPLAY_R3"
        )
        if row.get("authority_id") != expected_authority_id:
            raise SchemaContractError("missing_retired_authority", path)
        _validate_lower_sha256(row.get("declared_sha256"), label=source_id)
        if row.get("declared_sha256") != expected_hashes[path]:
            raise SchemaContractError("retired_authority_hash_mismatch", source_id)
        if row.get("local_only") is not False:
            raise SchemaContractError("missing_retired_authority", source_id)
        if row.get("verification_status") != "verified":
            raise SchemaContractError("missing_retired_authority", source_id)
        if row.get("lineage_status") not in DIMENSION_STATUS_VALUES:
            raise SchemaContractError("retired_projection_unreconstructable", source_id)
    if selector_rows is not None:
        validate_source_selector_matrix(selector_rows)
        expected_matrix = schema_definition.get("allowed_json_fields_by_source")
        if (
            not isinstance(expected_matrix, list)
            or list(selector_rows) != expected_matrix
        ):
            raise SchemaContractError("source_field_read_violation")


def validate_retired_authority_lineage_reproduction(
    metadata: Mapping[str, JsonValue],
) -> None:
    validate_exact_keys(
        metadata,
        {"dimension_statuses", "comparison_statuses", "origin_rows"},
        label="retired_lineage_reproduction",
    )
    statuses = set(
        _as_string_sequence(metadata.get("dimension_statuses"), "dimension_statuses")
    )
    if set(DIMENSION_STATUS_VALUES) - statuses:
        raise SchemaContractError("retired_projection_unreconstructable")
    comparison_statuses = set(
        _as_string_sequence(metadata.get("comparison_statuses"), "comparison_statuses")
    )
    if not comparison_statuses <= set(COMPARISON_STATUS_VALUES):
        raise SchemaContractError("unknown_comparison_status")
    origin_rows = metadata.get("origin_rows")
    if not isinstance(origin_rows, Sequence) or isinstance(origin_rows, str | bytes):
        raise SchemaContractError("duplicate_lineage_miscount")
    origin_count_by_lineage: Counter[str] = Counter()
    all_lineages: set[str] = set()
    seen_authority_lineages: set[tuple[str, str]] = set()
    for row in origin_rows:
        if not isinstance(row, Mapping):
            raise SchemaContractError("duplicate_lineage_miscount")
        validate_exact_keys(
            row,
            {"origin", "lineage_id", "duplicate_of_or_null", "counts_as_evidence"},
            label="retired_lineage_origin_row",
        )
        origin = _require_nonempty_string(row.get("origin"), "origin")
        if origin not in RETIRED_AUTHORITY_IDS:
            raise SchemaContractError("semantic_lineage_ambiguous", origin)
        lineage_id = _require_nonempty_string(row.get("lineage_id"), "lineage_id")
        _validate_prefixed_sha256(lineage_id, label="lineage_id")
        all_lineages.add(lineage_id)
        authority_lineage = (origin, lineage_id)
        if authority_lineage in seen_authority_lineages:
            raise SchemaContractError("duplicate_lineage_miscount", origin)
        seen_authority_lineages.add(authority_lineage)
        duplicate_of = row.get("duplicate_of_or_null")
        counts = row.get("counts_as_evidence")
        if duplicate_of is None:
            if counts is not True:
                raise SchemaContractError("duplicate_lineage_miscount")
            origin_count_by_lineage[lineage_id] += 1
        else:
            if duplicate_of != lineage_id or counts is not False:
                raise SchemaContractError("duplicate_lineage_miscount")
    if set(origin_count_by_lineage) != all_lineages or any(
        count != 1 for count in origin_count_by_lineage.values()
    ):
        raise SchemaContractError("duplicate_lineage_miscount")


def validate_retired_authority_subunit_family(
    family: Mapping[str, JsonValue],
) -> None:
    validate_exact_keys(family, {"parent_id", "subunits"}, label="subunit_family")
    _require_nonempty_string(family.get("parent_id"), "parent_id")
    subunits = family.get("subunits")
    if not isinstance(subunits, Sequence) or isinstance(subunits, str | bytes):
        raise SchemaContractError("retired_normalizer_error")
    allowed = {"grid_cells", "l30_inequalities", "b05_monitors"}
    seen: set[str] = set()
    for subunit in subunits:
        if not isinstance(subunit, Mapping):
            raise SchemaContractError("retired_normalizer_error")
        validate_exact_keys(subunit, {"subunit_id", "family"}, label="subunit")
        subunit_id = _require_nonempty_string(subunit.get("subunit_id"), "subunit_id")
        if subunit_id in seen:
            raise SchemaContractError("set_array_duplicate", subunit_id)
        seen.add(subunit_id)
        if subunit.get("family") not in allowed:
            raise SchemaContractError("retired_normalizer_error")


def validate_normalizer_static_source(source: str) -> None:
    validate_normalizer_source_guard(source)


def validate_input_overlap_report(
    report: Mapping[str, JsonValue],
    *,
    method_owner_case_ids: Mapping[str, str],
    fingerprint_dimensions_by_hash: Mapping[str, str],
) -> None:
    validate_exact_keys(
        report,
        INPUT_OVERLAP_REPORT_REQUIRED_FIELDS,
        label="input_overlap_report",
    )
    if report.get("schema_version") != "ims-deadlock/g6b-input-overlap-report/v1":
        raise SchemaContractError("schema_version_drift")
    _require_nonempty_string(report.get("report_id"), "report_id")
    _require_nonempty_string(report.get("bundle_id"), "bundle_id")
    _require_nonempty_string(
        report.get("admission_policy_version"),
        "admission_policy_version",
    )
    for field in (
        "per_case_status",
        "per_method_status",
        "per_companion_group_status",
    ):
        found = _find_forbidden_keys(
            report.get(field),
            set(OVERLAP_RECURSIVE_PROHIBITED_FIELDS),
        )
        if found:
            raise SchemaContractError("recursive_forbidden_field", min(found))
    for field in (
        "input_overlap_authority_lock_sha256",
        "sealed_bundle_manifest_sha256",
        "normalization_manifest_sha256",
        "ledger_head_hash",
    ):
        _validate_lower_sha256(report.get(field), label=field)

    declared_cases = _unique_sorted_set(
        _as_string_sequence(
            report.get("declared_case_unit_ids"), "declared_case_unit_ids"
        ),
        "declared_case_unit_ids",
    )
    declared_methods = _unique_sorted_set(
        _as_string_sequence(
            report.get("declared_method_observation_ids"),
            "declared_method_observation_ids",
        ),
        "declared_method_observation_ids",
    )
    declared_groups = _unique_sorted_set(
        _as_string_sequence(
            report.get("declared_method_companion_group_ids"),
            "declared_method_companion_group_ids",
        ),
        "declared_method_companion_group_ids",
    )
    if (
        set(method_owner_case_ids) != declared_methods
        or not set(method_owner_case_ids.values()) <= declared_cases
    ):
        raise SchemaContractError("method_refusal_case_mismatch")

    hash_maps = {
        field: _validate_hash_map(report.get(field), label=field)
        for field in (
            "new_fingerprint_record_hashes",
            "retired_fingerprint_record_hashes",
            "comparison_record_hashes",
            "semantic_lineage_audit_hashes",
            "metric_schema_reuse_record_hashes",
        )
    }
    subject_maps: dict[str, Mapping[str, JsonValue]] = {}
    required_hashes: dict[str, list[str]] = {
        "new_fingerprint_record_hashes": [],
        "comparison_record_hashes": [],
        "semantic_lineage_audit_hashes": [],
        "metric_schema_reuse_record_hashes": [],
    }
    status_counts: dict[str, Counter[str]] = {}
    for field, expected_type, declared_ids in (
        ("per_case_status", "case_unit", declared_cases),
        ("per_method_status", "method_observation", declared_methods),
        (
            "per_companion_group_status",
            "method_companion_group",
            declared_groups,
        ),
    ):
        value = report.get(field)
        if not isinstance(value, Mapping) or set(value) != declared_ids:
            raise SchemaContractError("terminal_partition_incomplete", field)
        typed_value: dict[str, JsonValue] = dict(value)
        subject_maps[field] = typed_value
        counts: Counter[str] = Counter()
        for subject_id, status_value in typed_value.items():
            if not isinstance(subject_id, str) or not isinstance(status_value, Mapping):
                raise SchemaContractError("terminal_partition_incomplete", field)
            validate_exact_keys(
                status_value,
                OVERLAP_SUBJECT_STATUS_REQUIRED_FIELDS,
                label=field,
            )
            if status_value.get("subject_type") != expected_type:
                raise SchemaContractError("subject_type_mismatch", subject_id)
            if status_value.get("subject_id") != subject_id:
                raise SchemaContractError("subject_id_mismatch", subject_id)
            admission_status = status_value.get("admission_status")
            if admission_status not in OVERLAP_ADMISSION_STATUS_VALUES:
                raise SchemaContractError("unknown_admission_status", subject_id)
            counts[str(admission_status)] += 1
            refusal_codes = _as_string_sequence(
                status_value.get("refusal_reason_codes"),
                "refusal_reason_codes",
            )
            _unique_sorted_set(refusal_codes, "refusal_reason_codes")
            validate_refusal_codes("normalization_overlap", refusal_codes)
            ledger_ids = _as_string_sequence(
                status_value.get("ledger_entry_ids"),
                "ledger_entry_ids",
            )
            _unique_sorted_set(ledger_ids, "ledger_entry_ids")
            if admission_status == "admitted" and (refusal_codes or ledger_ids):
                raise SchemaContractError("refusal_reason_unexpected", subject_id)
            if admission_status == "refused" and (not refusal_codes or not ledger_ids):
                raise SchemaContractError("refusal_reason_required", subject_id)
            for subject_field, report_field in (
                (
                    "required_fingerprint_record_hashes",
                    "new_fingerprint_record_hashes",
                ),
                ("required_comparison_record_hashes", "comparison_record_hashes"),
                (
                    "required_lineage_audit_hashes",
                    "semantic_lineage_audit_hashes",
                ),
                (
                    "required_reuse_record_hashes",
                    "metric_schema_reuse_record_hashes",
                ),
            ):
                digests = _as_string_sequence(
                    status_value.get(subject_field),
                    subject_field,
                )
                _unique_sorted_set(digests, subject_field)
                for digest in digests:
                    _validate_lower_sha256(digest, label=subject_field)
                required_hashes[report_field].extend(digests)
                if subject_field == "required_fingerprint_record_hashes":
                    expected_dimensions = {
                        dimension
                        for dimension, subject_type in DIMENSION_SUBJECTS.items()
                        if subject_type == expected_type
                    }
                    observed_dimensions = {
                        fingerprint_dimensions_by_hash.get(digest) for digest in digests
                    }
                    if (
                        None in observed_dimensions
                        or observed_dimensions != expected_dimensions
                    ):
                        raise SchemaContractError(
                            "overlap_dimension_coverage",
                            subject_id,
                        )
        status_counts[field] = counts

    for field, relation_digests in required_hashes.items():
        if Counter(relation_digests) != Counter(hash_maps[field].values()) or any(
            count != 1 for count in Counter(relation_digests).values()
        ):
            raise SchemaContractError("overlap_relation_ownership", field)
    referenced_fingerprints = set(required_hashes["new_fingerprint_record_hashes"])
    if set(fingerprint_dimensions_by_hash) != referenced_fingerprints:
        raise SchemaContractError("overlap_dimension_coverage")
    if set(fingerprint_dimensions_by_hash.values()) != set(FINGERPRINT_DIMENSIONS):
        raise SchemaContractError("overlap_dimension_coverage")

    for method_id, owner_case_id in method_owner_case_ids.items():
        method_record = subject_maps["per_method_status"][method_id]
        case_record = subject_maps["per_case_status"][owner_case_id]
        if not isinstance(method_record, Mapping) or not isinstance(
            case_record, Mapping
        ):
            raise SchemaContractError("method_refusal_case_mismatch")
        if (
            method_record.get("admission_status") == "refused"
            and case_record.get("admission_status") != "refused"
        ):
            raise SchemaContractError("method_refusal_case_mismatch", method_id)

    count_contract = (
        (
            "per_case_status",
            "planned_case_count",
            "passed_case_count",
            "refused_case_count",
            "pending_case_count",
        ),
        (
            "per_method_status",
            "planned_method_count",
            "passed_method_count",
            "refused_method_count",
            "pending_method_count",
        ),
        (
            "per_companion_group_status",
            "planned_companion_group_count",
            "passed_companion_group_count",
            "refused_companion_group_count",
            "pending_companion_group_count",
        ),
    )
    for (
        subject_field,
        planned_field,
        passed_field,
        refused_field,
        pending_field,
    ) in count_contract:
        counts = status_counts[subject_field]
        expected_values = (
            sum(counts.values()),
            counts["admitted"],
            counts["refused"],
            counts["pending"],
        )
        for field, expected in zip(
            (planned_field, passed_field, refused_field, pending_field),
            expected_values,
            strict=True,
        ):
            if type(report.get(field)) is not int or report.get(field) != expected:
                raise SchemaContractError("terminal_count_mismatch", field)
    overlap_counts: dict[str, int] = {}
    for field in (
        "unique_retired_lineage_count",
        "inherited_record_count",
        "duplicate_lineage_record_count",
    ):
        value = report.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise SchemaContractError("terminal_count_type", field)
        overlap_counts[field] = value
    if overlap_counts["unique_retired_lineage_count"] != len(
        hash_maps["retired_fingerprint_record_hashes"]
    ):
        raise SchemaContractError("duplicate_lineage_miscount")

    report_status = report.get("report_status")
    if report_status not in OVERLAP_REPORT_STATUS_VALUES:
        raise SchemaContractError("unknown_report_status")
    terminal_counts: dict[str, int] = {}
    for field in (
        "pending_case_count",
        "pending_method_count",
        "pending_companion_group_count",
        "refused_case_count",
        "refused_method_count",
        "refused_companion_group_count",
    ):
        value = report.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise SchemaContractError("terminal_count_type", field)
        terminal_counts[field] = value
    pending_count = sum(
        terminal_counts[field]
        for field in (
            "pending_case_count",
            "pending_method_count",
            "pending_companion_group_count",
        )
    )
    refused_count = sum(
        terminal_counts[field]
        for field in (
            "refused_case_count",
            "refused_method_count",
            "refused_companion_group_count",
        )
    )
    if report_status != "incomplete_refused" and pending_count != 0:
        raise SchemaContractError("terminal_partition_incomplete")
    if report_status == "complete_all_admitted" and refused_count != 0:
        raise SchemaContractError("report_status_count_mismatch")
    if report_status == "complete_with_refusals" and refused_count == 0:
        raise SchemaContractError("report_status_count_mismatch")
    _verify_finalized_self_hash(report, "report_sha256")


def validate_manifest_retention(manifest: Mapping[str, JsonValue]) -> None:
    validate_exact_keys(
        manifest,
        {
            "declared_object_ids",
            "refused_object_ids",
            "superseded_object_ids",
            "later_manifest_object_ids",
        },
        label="manifest_retention_chain",
    )
    retained = _unique_sorted_set(
        _as_string_sequence(
            manifest.get("later_manifest_object_ids"),
            "later_manifest_object_ids",
        ),
        "later_manifest_object_ids",
    )
    required = _unique_sorted_set(
        _as_string_sequence(
            manifest.get("declared_object_ids"),
            "declared_object_ids",
        ),
        "declared_object_ids",
    )
    refused = _unique_sorted_set(
        _as_string_sequence(
            manifest.get("refused_object_ids"),
            "refused_object_ids",
        ),
        "refused_object_ids",
    )
    superseded = _unique_sorted_set(
        _as_string_sequence(
            manifest.get("superseded_object_ids"),
            "superseded_object_ids",
        ),
        "superseded_object_ids",
    )
    if not refused <= required or not superseded <= required:
        raise SchemaContractError("manifest_retention_gap")
    if not required <= retained:
        raise SchemaContractError("manifest_retention_gap")


def validate_recursive_forbidden_fields(payload: Mapping[str, JsonValue]) -> None:
    found = _find_forbidden_keys(
        payload,
        set(ALL_RECURSIVE_PROHIBITED_FIELDS),
    )
    if found:
        raise SchemaContractError("recursive_forbidden_field", min(found))


def validate_preflight_static_source(source: str) -> None:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise SchemaContractError("capability_call_violation") from exc
    if any(isinstance(node, ast.ClassDef) for node in ast.walk(tree)):
        raise SchemaContractError("capability_call_violation")
    if _uses_reserved_safe_alias_name(tree):
        raise SchemaContractError("capability_call_violation")
    aliases: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                _validate_preflight_import(alias.name)
                if alias.asname is not None:
                    _add_callable_alias(aliases, alias.asname, {alias.name})
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            _validate_preflight_import(module_name)
            for alias in node.names:
                if alias.name == "*":
                    raise SchemaContractError("capability_import_violation")
                local_name = alias.asname or alias.name
                _add_callable_alias(
                    aliases, local_name, {f"{module_name}.{alias.name}"}
                )
    _extend_callable_assignment_aliases(tree, aliases)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Subscript):
                raise SchemaContractError("capability_call_violation")
            call_names = _ast_callable_value_names(node.func, aliases)
            if not call_names:
                raise SchemaContractError("capability_call_violation")
            for call_name in call_names:
                if _is_unknown_callable_alias(call_name):
                    raise SchemaContractError("capability_call_violation", call_name)
                if _is_dynamic_import_call(call_name) or _is_dynamic_builtin_call(
                    call_name
                ):
                    code = (
                        "capability_import_violation"
                        if _is_dynamic_import_call(call_name)
                        else "capability_call_violation"
                    )
                    raise SchemaContractError(code, call_name)
                if _is_safe_object_method(call_name):
                    continue
                if _is_unlisted_safe_object_method(call_name):
                    raise SchemaContractError("capability_call_violation", call_name)
                if call_name in PREFLIGHT_FORBIDDEN_CALLS or any(
                    call_name.endswith(f".{forbidden.rsplit('.', 1)[-1]}")
                    for forbidden in PREFLIGHT_FORBIDDEN_CALLS
                ):
                    raise SchemaContractError("capability_call_violation", call_name)
                _reject_unapproved_side_effect_call(
                    call_name,
                    node,
                    allowed_writer_symbols=ALLOWED_PREFLIGHT_WRITER_SYMBOLS,
                    error_code="capability_call_violation",
                )
                leaf_name = call_name.rsplit(".", 1)[-1]
                if (
                    leaf_name.startswith(("write_", "append_"))
                    and call_name not in ALLOWED_PREFLIGHT_WRITER_SYMBOLS
                ):
                    raise SchemaContractError("capability_call_violation", call_name)
            _reject_sensitive_callable_escapes(
                node,
                aliases,
                error_code="capability_call_violation",
            )
            for arg in node.args:
                if isinstance(arg, ast.Dict):
                    keys = {
                        key.value
                        for key in arg.keys
                        if isinstance(key, ast.Constant) and isinstance(key.value, str)
                    }
                    if keys & PREFLIGHT_RECURSIVE_PROHIBITED_FIELDS:
                        raise SchemaContractError("capability_call_violation")


def validate_preflight_result_payload(payload: Mapping[str, JsonValue]) -> None:
    validate_exact_keys(
        payload,
        PREFLIGHT_CASE_RESULT_REQUIRED_FIELDS,
        label="preflight_result",
    )
    found = _find_forbidden_keys(
        payload,
        set(PREFLIGHT_RECURSIVE_PROHIBITED_FIELDS),
    )
    if found:
        raise SchemaContractError("outcome_leakage", min(found))
    for field in ("schema_version", "bundle_id", "case_unit_id"):
        _require_nonempty_string(payload.get(field), field)
    input_identity_hashes = payload.get("input_identity_hashes")
    if not isinstance(input_identity_hashes, Mapping):
        raise SchemaContractError("missing_key", "input_identity_hashes")
    validate_exact_keys(
        input_identity_hashes,
        PREFLIGHT_INPUT_IDENTITY_REQUIRED_FIELDS,
        label="input_identity_hashes",
    )
    for field in PREFLIGHT_INPUT_IDENTITY_REQUIRED_FIELDS:
        _validate_lower_sha256(input_identity_hashes.get(field), label=field)
    selected_target = payload.get("selected_target_identity")
    if not isinstance(selected_target, Mapping):
        raise SchemaContractError("missing_key", "selected_target_identity")
    validate_exact_keys(
        selected_target,
        PREFLIGHT_SELECTED_TARGET_REQUIRED_FIELDS,
        label="selected_target_identity",
    )
    for field in (
        "target_schema_version",
        "success_class",
        "exact_stopping_rule",
        "des_stopping_rule",
        "policy_analysis_class",
    ):
        _require_nonempty_string(selected_target.get(field), field)
    selected_bad_classes = _as_string_sequence(
        selected_target.get("selected_bad_classes"),
        "selected_bad_classes",
    )
    _unique_sorted_set(selected_bad_classes, "selected_bad_classes")
    _validate_lower_sha256(
        selected_target.get("declaration_sha256"),
        label="declaration_sha256",
    )
    for field in (
        "runtime_lock_sha256",
        "authorization_sha256",
        "command_transcript_sha256",
        "stderr_sha256",
        "filesystem_before_manifest_sha256",
        "filesystem_after_manifest_sha256",
    ):
        _validate_lower_sha256(payload.get(field), label=field)
    for field in ("state_count", "transition_count", "exit_code"):
        value = payload.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise SchemaContractError("terminal_count_type", field)
    refusal_codes = _as_string_sequence(
        payload.get("refusal_reason_codes"),
        "refusal_reason_codes",
    )
    _unique_sorted_set(refusal_codes, "refusal_reason_codes")
    validate_refusal_codes("preflight", refusal_codes)
    ledger_entry_ids = _as_string_sequence(
        payload.get("ledger_entry_ids"),
        "ledger_entry_ids",
    )
    _unique_sorted_set(ledger_entry_ids, "ledger_entry_ids")
    result_status = payload.get("result_status")
    if result_status not in {"certified", "refused"}:
        raise SchemaContractError("unknown_result_status")
    _require_nonempty_string(
        payload.get("completeness_status"),
        "completeness_status",
    )
    if result_status == "certified":
        for field in (
            "state_space_hash",
            "partition_hash",
            "rate_manifest_hash",
            "positive_rate_graph_hash",
            "policy_filter_hash",
            "absorption_domain_hash",
        ):
            _validate_lower_sha256(payload.get(field), label=field)
        _require_nonempty_string(payload.get("estimand_id"), "estimand_id")
        _require_nonempty_string(
            payload.get("certificate_version"),
            "certificate_version",
        )
        if payload.get("certificate_status") != "certified":
            raise SchemaContractError("certificate_schema_violation")
        certificate_payload = payload.get("certificate_payload_or_null")
        if certificate_payload is None:
            raise SchemaContractError("certificate_schema_violation")
        certificate_hash = payload.get("certificate_payload_sha256_or_null")
        _validate_lower_sha256(
            certificate_hash, label="certificate_payload_sha256_or_null"
        )
        if (
            g6b_canonical_json.canonical_sha256_v2(certificate_payload)
            != certificate_hash
        ):
            raise SchemaContractError("certificate_schema_violation")
        if refusal_codes or payload.get("refusal_details") != []:
            raise SchemaContractError("refusal_reason_unexpected")
        if payload.get("exit_code") != 0:
            raise SchemaContractError("certificate_schema_violation")
    else:
        if not refusal_codes or not isinstance(payload.get("refusal_details"), list):
            raise SchemaContractError("refusal_reason_required")


def validate_certified_record_runtime_evidence(
    record: Mapping[str, JsonValue],
) -> None:
    validate_preflight_result_payload(record)
    if record.get("result_status") != "certified":
        raise SchemaContractError("certificate_schema_violation")


def validate_same_target_lock(record: Mapping[str, JsonValue]) -> None:
    validate_exact_keys(
        record,
        SAME_TARGET_LOCK_REQUIRED_FIELDS,
        label="same_target_lock",
    )
    if record.get("schema_version") != "ims-deadlock/g6b-same-target-lock/v1":
        raise SchemaContractError("schema_version_drift")
    for field in (
        "same_target_lock_id",
        "bundle_id",
        "case_unit_id",
        "method_companion_group_id",
        "exact_method_observation_id",
        "des_method_observation_id",
        "target_schema_version",
        "estimand_schema_version",
        "estimand_id",
    ):
        _require_nonempty_string(record.get(field), field)
    _validate_utc_timestamp(
        record.get("lock_created_at_utc"),
        label="lock_created_at_utc",
    )
    if record.get("exact_method_observation_id") == record.get(
        "des_method_observation_id"
    ):
        raise SchemaContractError("exact_des_target_mismatch")
    if (
        _as_string_sequence(record.get("selected_bad_classes"), "selected_bad_classes")
        != ("D_global", "D_local")
        or record.get("success_class") != "F"
    ):
        raise SchemaContractError("exact_des_target_mismatch")
    hash_fields = (
        "state_space_hash",
        "partition_hash",
        "rate_manifest_hash",
        "positive_rate_graph_hash",
        "policy_filter_hash",
        "absorption_domain_hash",
        "certificate_artifact_hash",
        "exact_stopping_rule_hash",
        "des_stopping_rule_hash",
        "metric_schema_sha256",
        "metric_reuse_authorization_hash",
        "exact_random_stream_manifest_sha256",
        "des_random_stream_manifest_sha256",
        "exact_output_root_reservation_sha256",
        "des_output_root_reservation_sha256",
    )
    for field in hash_fields:
        _validate_lower_sha256(record.get(field), label=field)
    if record.get("exact_random_stream_manifest_sha256") == record.get(
        "des_random_stream_manifest_sha256"
    ):
        raise SchemaContractError("random_stream_overlap")
    if record.get("exact_output_root_reservation_sha256") == record.get(
        "des_output_root_reservation_sha256"
    ):
        raise SchemaContractError("output_root_reuse_or_materialized")
    _verify_finalized_self_hash(record, "same_target_lock_sha256")


def validate_same_target_certificate_pair(pair: Mapping[str, JsonValue]) -> None:
    validate_same_target_lock(pair)


def validate_preflight_authorization(
    record: Mapping[str, JsonValue],
    *,
    expected_bundle_id: str,
    expected_case_unit_ids: Sequence[str],
    expected_sealed_bundle_manifest_hash: str,
    expected_runtime_lock_sha256: str,
    command_manifest: Mapping[str, JsonValue],
    command_records: Mapping[str, Mapping[str, JsonValue]],
) -> None:
    validate_exact_keys(
        record,
        PREFLIGHT_AUTHORIZATION_REQUIRED_FIELDS,
        label="preflight_authorization",
    )
    if record.get("schema_version") != "ims-deadlock/g6b-preflight-authorization/v1":
        raise SchemaContractError("schema_version_drift")
    _require_nonempty_string(record.get("authorization_id"), "authorization_id")
    if record.get("capability") != "target_certification_preflight":
        raise SchemaContractError("capability_mismatch")
    if record.get("authorized") is not True:
        raise SchemaContractError("unauthorized_target_certification_attempt")
    if record.get("invalidated_by_identity_drift") is not False:
        raise SchemaContractError("runtime_identity_drift")

    expected_bundle = _require_nonempty_string(
        expected_bundle_id,
        "expected_bundle_id",
    )
    if record.get("bundle_id") != expected_bundle:
        raise SchemaContractError("command_scope_violation", "bundle_id")
    case_ids = _as_string_sequence(record.get("case_unit_ids"), "case_unit_ids")
    expected_case_ids = _as_string_sequence(
        expected_case_unit_ids,
        "expected_case_unit_ids",
    )
    if not case_ids or not expected_case_ids:
        raise SchemaContractError("command_scope_violation", "case_unit_ids")
    _unique_sorted_set(case_ids, "case_unit_ids")
    _unique_sorted_set(expected_case_ids, "expected_case_unit_ids")
    if case_ids != expected_case_ids:
        raise SchemaContractError("command_scope_violation", "case_unit_ids")

    for field in (
        "sealed_bundle_manifest_hash",
        "runtime_lock_sha256",
        "allowed_command_manifest_hash",
        "review_artifact_hash",
    ):
        _validate_lower_sha256(record.get(field), label=field)
    _validate_lower_sha256(
        expected_sealed_bundle_manifest_hash,
        label="expected_sealed_bundle_manifest_hash",
    )
    _validate_lower_sha256(
        expected_runtime_lock_sha256,
        label="expected_runtime_lock_sha256",
    )
    if (
        record.get("sealed_bundle_manifest_hash")
        != expected_sealed_bundle_manifest_hash
    ):
        raise SchemaContractError("sealed_input_drift")
    if record.get("runtime_lock_sha256") != expected_runtime_lock_sha256:
        raise SchemaContractError("runtime_identity_drift")

    if record.get("allowed_entrypoint") != PREFLIGHT_ALLOWED_ENTRYPOINT:
        raise SchemaContractError("command_scope_violation", "allowed_entrypoint")
    if (
        _as_string_sequence(record.get("allowed_operations"), "allowed_operations")
        != ALLOWED_OPERATIONS
    ):
        raise SchemaContractError("operation_contract_drift")
    if (
        _as_string_sequence(
            record.get("allowed_output_schemas"),
            "allowed_output_schemas",
        )
        != ALLOWED_OUTPUT_SCHEMA_IDS
    ):
        raise SchemaContractError("command_scope_violation", "allowed_output_schemas")
    if (
        _as_string_sequence(record.get("forbidden_calls"), "forbidden_calls")
        != PREFLIGHT_FORBIDDEN_CALLS
    ):
        raise SchemaContractError("capability_call_violation")
    if (
        _as_string_sequence(
            record.get("forbidden_side_effects"),
            "forbidden_side_effects",
        )
        != PREFLIGHT_FORBIDDEN_SIDE_EFFECTS
    ):
        raise SchemaContractError("unexpected_preflight_side_effect")

    budget = record.get("resource_budget")
    if not isinstance(budget, Mapping):
        raise SchemaContractError("command_scope_violation", "resource_budget")
    validate_exact_keys(
        budget,
        PREFLIGHT_RESOURCE_BUDGET_REQUIRED_FIELDS,
        label="resource_budget",
    )
    for field in ("max_wall_clock_seconds", "max_cpu_seconds"):
        value = budget.get(field)
        if (
            not isinstance(value, str)
            or value == "0"
            or _POSITIVE_CANONICAL_DECIMAL_PATTERN.fullmatch(value) is None
        ):
            raise SchemaContractError("command_scope_violation", field)
    for field in PREFLIGHT_RESOURCE_BUDGET_REQUIRED_FIELDS[2:]:
        value = budget.get(field)
        if type(value) is not int or value <= 0:
            raise SchemaContractError("command_scope_violation", field)
    max_cases = budget.get("max_cases")
    if type(max_cases) is not int or max_cases < len(case_ids):
        raise SchemaContractError("command_scope_violation", "max_cases")

    stop_conditions = _as_string_sequence(
        record.get("stop_conditions"),
        "stop_conditions",
    )
    if not stop_conditions:
        raise SchemaContractError("command_scope_violation", "stop_conditions")
    _unique_sorted_set(stop_conditions, "stop_conditions")
    if any(
        _VERSIONED_STOP_CONDITION_PATTERN.fullmatch(code) is None
        for code in stop_conditions
    ):
        raise SchemaContractError("command_scope_violation", "stop_conditions")

    evidence_root = record.get("preflight_evidence_root")
    if not isinstance(evidence_root, Mapping):
        raise SchemaContractError("command_scope_violation", "preflight_evidence_root")
    validate_exact_keys(
        evidence_root,
        PREFLIGHT_EVIDENCE_ROOT_REQUIRED_FIELDS,
        label="preflight_evidence_root",
    )
    if (
        evidence_root.get("root_schema_version")
        != "ims-deadlock/g6b-preflight-evidence-root/v1"
    ):
        raise SchemaContractError("schema_version_drift")
    if evidence_root.get("bundle_id") != expected_bundle:
        raise SchemaContractError("command_scope_violation", "preflight_evidence_root")
    root_path = _require_nonempty_string(
        evidence_root.get("repo_relative_posix_path"),
        "repo_relative_posix_path",
    )
    _validate_repo_relative_path(root_path)
    expected_root_path = f"evidence/g6b/target_certification/{expected_bundle}"
    if root_path != expected_root_path:
        raise SchemaContractError("unexpected_preflight_side_effect")
    if evidence_root.get("state") != "reserved_not_materialized":
        raise SchemaContractError("unexpected_preflight_side_effect")
    if (
        _as_string_sequence(
            evidence_root.get("allowed_file_roles"),
            "allowed_file_roles",
        )
        != ALLOWED_FILE_ROLES
    ):
        raise SchemaContractError("command_scope_violation", "allowed_file_roles")
    _verify_finalized_self_hash(evidence_root, "reservation_sha256")
    reservation_sha256 = evidence_root.get("reservation_sha256")

    validate_command_manifest(
        command_manifest,
        command_records,
        capability="target_certification_preflight",
    )
    if record.get("allowed_command_manifest_hash") != command_manifest.get(
        "manifest_sha256"
    ):
        raise SchemaContractError(
            "command_scope_violation", "allowed_command_manifest_hash"
        )
    if command_manifest.get("sealed_bundle_manifest_hash") != record.get(
        "sealed_bundle_manifest_hash"
    ):
        raise SchemaContractError("sealed_input_drift")
    if (
        command_manifest.get("preflight_evidence_root_reservation_sha256")
        != reservation_sha256
    ):
        raise SchemaContractError("command_scope_violation", "preflight_evidence_root")
    command_case_ids: set[str] = set()
    for command_record in command_records.values():
        if command_record.get("entrypoint") != record.get("allowed_entrypoint"):
            raise SchemaContractError("command_scope_violation", "allowed_entrypoint")
        if command_record.get("authorized_preflight_root_hash") != reservation_sha256:
            raise SchemaContractError(
                "command_scope_violation", "preflight_evidence_root"
            )
        command_case_ids.update(
            _as_string_sequence(
                command_record.get("authorized_case_unit_ids"),
                "authorized_case_unit_ids",
            )
        )
    if command_case_ids != set(case_ids):
        raise SchemaContractError("command_scope_violation", "case_unit_ids")

    _validate_utc_timestamp(record.get("issued_at_utc"), label="issued_at_utc")
    _verify_finalized_self_hash(record, "authorization_sha256")


def validate_quantitative_authorization(
    record: Mapping[str, JsonValue],
    *,
    mandatory_control_statuses: Mapping[str, bool],
    required_mandatory_control_ids: Sequence[str],
    command_manifest: Mapping[str, JsonValue],
    command_records: Mapping[str, Mapping[str, JsonValue]],
) -> None:
    validate_exact_keys(
        record,
        QUANTITATIVE_AUTHORIZATION_REQUIRED_FIELDS,
        label="quantitative_authorization",
    )
    if record.get("schema_version") != "ims-deadlock/g6b-quantitative-authorization/v1":
        raise SchemaContractError("schema_version_drift")
    for field in ("authorization_id", "bundle_id"):
        _require_nonempty_string(record.get(field), field)
    _validate_utc_timestamp(record.get("issued_at_utc"), label="issued_at_utc")
    if record.get("capability") != "quantitative_execution":
        raise SchemaContractError("capability_mismatch")
    if record.get("authorized") is not True:
        raise SchemaContractError("unauthorized_quantitative_execution_attempt")
    if record.get("invalidated_by_identity_drift") is not False:
        raise SchemaContractError("runtime_identity_drift")
    scope = record.get("authorized_scope")
    if not isinstance(scope, Mapping):
        raise SchemaContractError("quantitative_scope_violation")
    validate_exact_keys(
        scope,
        QUANTITATIVE_AUTHORIZED_SCOPE_REQUIRED_FIELDS,
        label="authorized_scope",
    )
    case_ids = _unique_sorted_set(
        _as_string_sequence(scope.get("case_unit_ids"), "case_unit_ids"),
        "case_unit_ids",
    )
    method_ids = _unique_sorted_set(
        _as_string_sequence(
            scope.get("method_observation_ids"),
            "method_observation_ids",
        ),
        "method_observation_ids",
    )
    if not case_ids or not method_ids:
        raise SchemaContractError("quantitative_scope_violation")
    certificate_hashes = _validate_hash_map(
        scope.get("certificate_hashes"),
        label="certificate_hashes",
    )
    same_target_hashes = _validate_hash_map(
        scope.get("same_target_lock_hashes"),
        label="same_target_lock_hashes",
    )
    output_root_hashes = _validate_hash_map(
        scope.get("output_root_reservations"),
        label="output_root_reservations",
    )
    if set(certificate_hashes) != case_ids or set(same_target_hashes) != case_ids:
        raise SchemaContractError("quantitative_scope_violation")
    if set(output_root_hashes) != method_ids:
        raise SchemaContractError("quantitative_scope_violation")
    for field in (
        "sealed_bundle_manifest_hash",
        "target_certification_batch_manifest_hash",
        "runtime_lock_sha256",
        "allowed_command_manifest_hash",
        "review_artifact_hash",
    ):
        _validate_lower_sha256(record.get(field), label=field)
    allowed_commands = _as_string_sequence(
        record.get("allowed_commands"),
        "allowed_commands",
    )
    if not allowed_commands:
        raise SchemaContractError("command_scope_violation")
    _unique_sorted_set(allowed_commands, "allowed_commands")
    for digest in allowed_commands:
        _validate_lower_sha256(digest, label="allowed_commands")
    run_roles = _as_string_sequence(record.get("run_roles"), "run_roles")
    if not run_roles:
        raise SchemaContractError("quantitative_scope_violation")
    _unique_sorted_set(run_roles, "run_roles")
    budget = record.get("resource_budget")
    if not isinstance(budget, Mapping):
        raise SchemaContractError("quantitative_scope_violation")
    validate_exact_keys(
        budget,
        QUANTITATIVE_RESOURCE_BUDGET_REQUIRED_FIELDS,
        label="resource_budget",
    )
    for field in QUANTITATIVE_RESOURCE_BUDGET_REQUIRED_FIELDS:
        minimum = 0 if field == "max_retries" else 1
        value = budget.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
            raise SchemaContractError("quantitative_scope_violation", field)
    output_policy = record.get("output_root_policy")
    if not isinstance(output_policy, Mapping):
        raise SchemaContractError("quantitative_scope_violation")
    validate_exact_keys(
        output_policy,
        QUANTITATIVE_OUTPUT_ROOT_POLICY_REQUIRED_FIELDS,
        label="output_root_policy",
    )
    root_template = _require_nonempty_string(
        output_policy.get("root_template"),
        "root_template",
    )
    _validate_repo_relative_path(root_template)
    for field in QUANTITATIVE_OUTPUT_ROOT_POLICY_REQUIRED_FIELDS[1:]:
        if output_policy.get(field) is not True:
            raise SchemaContractError("output_root_reuse_or_materialized", field)
    stop_conditions = _as_string_sequence(
        record.get("stop_conditions"),
        "stop_conditions",
    )
    if not stop_conditions:
        raise SchemaContractError("quantitative_scope_violation")
    _unique_sorted_set(stop_conditions, "stop_conditions")
    required_controls = _unique_sorted_set(
        required_mandatory_control_ids,
        "required_mandatory_control_ids",
    )
    if set(mandatory_control_statuses) != required_controls or not required_controls:
        raise SchemaContractError("failed_negative_control")
    if any(value is not True for value in mandatory_control_statuses.values()):
        raise SchemaContractError("failed_negative_control")
    validate_command_manifest(
        command_manifest,
        command_records,
        capability="quantitative_execution",
    )
    if record.get("allowed_command_manifest_hash") != command_manifest.get(
        "manifest_sha256"
    ):
        raise SchemaContractError("command_hash_map_mismatch")
    command_hashes = _validate_hash_map(
        command_manifest.get("command_record_hashes"),
        label="command_record_hashes",
    )
    if tuple(allowed_commands) != tuple(sorted(command_hashes.values())):
        raise SchemaContractError("command_hash_map_mismatch")
    if command_manifest.get("sealed_bundle_manifest_hash") != record.get(
        "sealed_bundle_manifest_hash"
    ) or command_manifest.get("target_certification_batch_manifest_hash") != record.get(
        "target_certification_batch_manifest_hash"
    ):
        raise SchemaContractError("quantitative_scope_violation")
    if command_manifest.get(
        "authorized_scope_sha256"
    ) != g6b_canonical_json.canonical_sha256_v2(dict(scope)):
        raise SchemaContractError("quantitative_scope_violation")
    if command_manifest.get("same_target_lock_hashes") != dict(same_target_hashes):
        raise SchemaContractError("same_target_hash_map_mismatch")
    if command_manifest.get("output_root_reservation_hashes") != dict(
        output_root_hashes
    ):
        raise SchemaContractError("output_root_hash_map_mismatch")
    command_case_ids: set[str] = set()
    command_method_ids: set[str] = set()
    command_run_roles: set[str] = set()
    for command_record in command_records.values():
        command_case_ids.update(
            _as_string_sequence(
                command_record.get("authorized_case_unit_ids"),
                "authorized_case_unit_ids",
            )
        )
        command_method_ids.update(
            _as_string_sequence(
                command_record.get("authorized_method_observation_ids"),
                "authorized_method_observation_ids",
            )
        )
        command_run_roles.update(
            _as_string_sequence(
                command_record.get("authorized_run_roles"),
                "authorized_run_roles",
            )
        )
    if command_case_ids != case_ids or command_method_ids != method_ids:
        raise SchemaContractError("quantitative_scope_violation")
    if command_run_roles != set(run_roles):
        raise SchemaContractError("quantitative_scope_violation")
    _verify_finalized_self_hash(record, "authorization_sha256")


def validate_append_only_failure_evidence_hashes(
    current_entry_hashes: Sequence[str],
    *,
    prior_entry_hashes: Sequence[str] = (),
) -> None:
    current = _as_string_sequence(current_entry_hashes, "current_entry_hashes")
    prior = _as_string_sequence(prior_entry_hashes, "prior_entry_hashes")
    if len(set(current)) != len(current) or len(set(prior)) != len(prior):
        raise SchemaContractError("append_only_ledger_rewrite")
    for digest in (*prior, *current):
        _validate_lower_sha256(digest, label="failure_evidence_entry_hash")
    if len(prior) > len(current) or current[: len(prior)] != prior:
        raise SchemaContractError("append_only_ledger_rewrite")


def validate_refusal_codes(
    gate: Literal[
        "construction",
        "normalization_overlap",
        "preflight",
        "quantitative",
        "ledger",
    ],
    codes: Sequence[str],
) -> None:
    group_by_gate = {
        "construction": CONSTRUCTION_REFUSAL_CODES,
        "normalization_overlap": NORMALIZATION_REFUSAL_CODES + OVERLAP_REFUSAL_CODES,
        "preflight": PREFLIGHT_REFUSAL_CODES,
        "quantitative": QUANTITATIVE_REFUSAL_CODES,
        "ledger": (),
    }
    universe = set(CROSS_GATE_REFUSAL_CODES).union(*REFUSAL_CODE_GROUPS.values())
    allowed = (
        universe
        if gate == "ledger"
        else set(CROSS_GATE_REFUSAL_CODES).union(group_by_gate[gate])
    )
    for code in codes:
        if code not in universe:
            raise SchemaContractError("unknown_refusal_code", code)
        if code not in allowed:
            raise SchemaContractError("wrong_gate_refusal_code", code)


def validate_declared_terminal_partition(
    declared_ids: Sequence[str],
    terminal_id_sets: Mapping[str, Sequence[str]],
    counts: Mapping[str, int],
) -> None:
    expected_keys = {"certified", "refused", "pending"}
    _validate_key_set(terminal_id_sets, expected_keys, label="terminal_id_sets")
    _validate_key_set(counts, expected_keys, label="terminal_counts")
    declared = _unique_sorted_set(declared_ids, "declared_ids")
    seen: set[str] = set()
    union: set[str] = set()
    for key in ("certified", "refused", "pending"):
        values = _unique_sorted_set(terminal_id_sets[key], key)
        if type(counts[key]) is not int or counts[key] < 0:
            raise SchemaContractError("terminal_count_type", key)
        if len(values) != counts[key]:
            raise SchemaContractError("terminal_count_mismatch", key)
        overlap = seen & values
        if overlap:
            raise SchemaContractError("terminal_partition_overlap", min(overlap))
        seen |= values
        union |= values
    if union != declared:
        raise SchemaContractError("terminal_partition_incomplete")


def validate_command_manifest(
    manifest: Mapping[str, JsonValue],
    command_records: Mapping[str, Mapping[str, JsonValue]],
    *,
    capability: Literal["target_certification_preflight", "quantitative_execution"],
) -> None:
    manifest_fields: Collection[str] = (
        PREFLIGHT_COMMAND_MANIFEST_REQUIRED_FIELDS
        if capability == "target_certification_preflight"
        else QUANTITATIVE_COMMAND_MANIFEST_REQUIRED_FIELDS
    )
    for key in _DOWNSTREAM_REFERENCE_KEYS:
        if key in manifest:
            raise SchemaContractError("downstream_reference", key)
    validate_exact_keys(manifest, manifest_fields, label="command_manifest")
    expected_schema = (
        "ims-deadlock/g6b-preflight-allowed-command-manifest/v1"
        if capability == "target_certification_preflight"
        else "ims-deadlock/g6b-quantitative-allowed-command-manifest/v1"
    )
    if manifest.get("schema_version") != expected_schema:
        raise SchemaContractError("schema_version_drift")
    if manifest.get("capability") != capability:
        raise SchemaContractError("capability_mismatch")
    _require_nonempty_string(manifest.get("manifest_id"), "manifest_id")
    _validate_git_object_id(manifest.get("source_head"), label="source_head")
    _validate_git_object_id(manifest.get("source_tree_hash"), label="source_tree_hash")
    _validate_lower_sha256(
        manifest.get("sealed_bundle_manifest_hash"),
        label="sealed_bundle_manifest_hash",
    )
    _validate_utc_timestamp(manifest.get("created_at_utc"), label="created_at_utc")
    if capability == "target_certification_preflight":
        for field in (
            "input_overlap_report_sha256",
            "preflight_evidence_root_reservation_sha256",
        ):
            _validate_lower_sha256(manifest.get(field), label=field)
    else:
        for field in (
            "target_certification_batch_manifest_hash",
            "authorized_scope_sha256",
        ):
            _validate_lower_sha256(manifest.get(field), label=field)
    placeholders = (
        PREFLIGHT_PLACEHOLDER_CODES
        if capability == "target_certification_preflight"
        else QUANTITATIVE_PLACEHOLDER_CODES
    )
    placeholder_values = _as_string_sequence(
        manifest.get("placeholder_vocabulary"),
        "placeholder_vocabulary",
    )
    if placeholder_values != placeholders:
        raise SchemaContractError("placeholder_vocabulary_drift")
    if manifest.get("wildcard_scope_allowed") is not False:
        raise SchemaContractError("wildcard_scope")
    environment_names = _as_string_sequence(
        manifest.get("environment_variable_name_allowlist"),
        "environment_variable_name_allowlist",
    )
    if environment_names != ALLOWED_ENVIRONMENT_VARIABLE_NAMES:
        raise SchemaContractError("environment_allowlist_mismatch")
    command_ids = _as_string_sequence(
        manifest.get("declared_command_ids"), "declared_command_ids"
    )
    if sorted(command_ids) != list(command_ids) or len(set(command_ids)) != len(
        command_ids
    ):
        raise SchemaContractError("command_id_set_mismatch")
    if capability == "target_certification_preflight" and len(command_ids) != 1:
        raise SchemaContractError("preflight_command_count")
    if capability == "quantitative_execution" and not command_ids:
        raise SchemaContractError("command_id_set_mismatch")
    hashes = _validate_hash_map(
        manifest.get("command_record_hashes"),
        label="command_record_hashes",
    )
    if set(hashes) != set(command_ids):
        raise SchemaContractError("command_hash_map_mismatch")
    command_count = manifest.get("command_count")
    if type(command_count) is not int or command_count < 0:
        raise SchemaContractError("command_count_type")
    if command_count != len(command_ids):
        raise SchemaContractError("command_count_mismatch")
    if set(command_records) != set(command_ids):
        raise SchemaContractError("command_record_set_mismatch")
    quantitative_case_ids: set[str] = set()
    quantitative_output_roots: dict[str, str] = {}
    for command_id in command_ids:
        record = command_records[command_id]
        record_fields: Collection[str] = (
            PREFLIGHT_COMMAND_RECORD_REQUIRED_FIELDS
            if capability == "target_certification_preflight"
            else QUANTITATIVE_COMMAND_RECORD_REQUIRED_FIELDS
        )
        validate_exact_keys(record, record_fields, label="command_record")
        if record.get("command_id") != command_id:
            raise SchemaContractError("command_record_set_mismatch")
        if record.get("capability") != capability:
            raise SchemaContractError("capability_mismatch")
        _validate_lower_sha256(
            record.get("executable_sha256"),
            label="executable_sha256",
        )
        _require_nonempty_string(record.get("entrypoint"), "entrypoint")
        if record.get("stdin_policy") != "closed":
            raise SchemaContractError("command_scope_violation")
        if record.get("command_record_sha256") != hashes[command_id]:
            raise SchemaContractError("command_hash_map_mismatch")
        _validate_tokens(record.get("argv_tokens"), placeholders)
        _validate_environment(
            record.get("environment_variable_allowlist"), placeholders
        )
        _reject_wildcard_scope(record.get("authorized_case_unit_ids"))
        _reject_wildcard_scope(record.get("authorized_method_observation_ids"))
        _reject_wildcard_scope(record.get("authorized_run_roles"))
        authorized_case_ids = _as_string_sequence(
            record.get("authorized_case_unit_ids"),
            "authorized_case_unit_ids",
        )
        if not authorized_case_ids:
            raise SchemaContractError("command_scope_violation")
        _unique_sorted_set(authorized_case_ids, "authorized_case_unit_ids")
        if capability == "target_certification_preflight":
            _validate_lower_sha256(
                record.get("authorized_preflight_root_hash"),
                label="authorized_preflight_root_hash",
            )
        if capability == "quantitative_execution":
            quantitative_case_ids.update(authorized_case_ids)
            method_ids = _as_string_sequence(
                record.get("authorized_method_observation_ids"),
                "authorized_method_observation_ids",
            )
            run_roles = _as_string_sequence(
                record.get("authorized_run_roles"),
                "authorized_run_roles",
            )
            if not method_ids or not run_roles:
                raise SchemaContractError("command_scope_violation")
            _unique_sorted_set(method_ids, "authorized_method_observation_ids")
            _unique_sorted_set(run_roles, "authorized_run_roles")
            record_roots = _validate_hash_map(
                record.get("authorized_output_root_reservation_hashes"),
                label="authorized_output_root_reservation_hashes",
            )
            for key, value in record_roots.items():
                if (
                    key in quantitative_output_roots
                    and quantitative_output_roots[key] != value
                ):
                    raise SchemaContractError("output_root_hash_map_mismatch", key)
                quantitative_output_roots[key] = value
        _verify_finalized_self_hash(record, "command_record_sha256")
    if capability == "quantitative_execution":
        same_target_hashes = _validate_hash_map(
            manifest.get("same_target_lock_hashes"),
            label="same_target_lock_hashes",
        )
        manifest_output_roots = _validate_hash_map(
            manifest.get("output_root_reservation_hashes"),
            label="output_root_reservation_hashes",
        )
        if set(same_target_hashes) != quantitative_case_ids:
            raise SchemaContractError("same_target_hash_map_mismatch")
        if manifest_output_roots != quantitative_output_roots:
            raise SchemaContractError("output_root_hash_map_mismatch")
    _verify_finalized_self_hash(manifest, "manifest_sha256")


def validate_file_role_cardinality(
    *,
    batch_status: str,
    certified_count: int,
    refused_count: int,
    failure_ledger_entry_count: int,
    file_roles: Sequence[str],
) -> None:
    for count in (certified_count, refused_count, failure_ledger_entry_count):
        if type(count) is not int or count < 0:
            raise SchemaContractError("file_role_count_type")
    counts = Counter(file_roles)
    unknown = sorted(set(counts) - set(ALLOWED_FILE_ROLES))
    if unknown:
        raise SchemaContractError("unknown_file_role", unknown[0])
    for role in (
        "batch_manifest",
        "command_transcript",
        "exit_code_capture",
        "filesystem_after_manifest",
        "filesystem_before_manifest",
        "hash_manifest",
        "stderr_capture",
    ):
        if counts[role] != 1:
            raise SchemaContractError("fixed_file_role_cardinality", role)
    if counts["per_case_result"] != certified_count + refused_count:
        raise SchemaContractError("per_case_result_cardinality")
    if counts["target_certificate"] != certified_count:
        raise SchemaContractError("target_certificate_cardinality")
    if counts["target_refusal"] != refused_count:
        raise SchemaContractError("target_refusal_cardinality")
    if counts["failure_ledger_entry"] != failure_ledger_entry_count:
        raise SchemaContractError("failure_ledger_entry_cardinality")
    if batch_status == "complete_all_certified" and refused_count != 0:
        raise SchemaContractError("batch_status_count_mismatch")
    if batch_status == "complete_with_refusals" and refused_count <= 0:
        raise SchemaContractError("batch_status_count_mismatch")
    if batch_status not in {
        "complete_all_certified",
        "complete_with_refusals",
        "incomplete_refused",
    }:
        raise SchemaContractError("unknown_batch_status", batch_status)


def validate_source_pointer_use(
    source_path: str,
    json_pointer: str | None,
    allowed_use: str,
    matrix: Sequence[Mapping[str, JsonValue]],
) -> None:
    matches: list[Mapping[str, JsonValue]] = []
    for row in matrix:
        validate_exact_keys(
            row,
            {"source_path_pattern", "selector_kind", "selectors", "allowed_use"},
            label="source_selector_row",
        )
        if row.get("selector_kind") not in SELECTOR_KINDS:
            raise SchemaContractError("unknown_selector_kind")
        if row.get("allowed_use") not in ALLOWED_USE_VALUES:
            raise SchemaContractError("unknown_allowed_use")
        pattern = _require_nonempty_string(
            row.get("source_path_pattern"),
            "source_path_pattern",
        )
        if not _source_path_pattern_matches(pattern, source_path):
            continue
        selector_kind = row.get("selector_kind")
        selectors = row.get("selectors")
        if selector_kind == "raw_bytes_only":
            if json_pointer is not None:
                raise SchemaContractError("raw_bytes_only_json_parse", source_path)
            matches.append(row)
            continue
        if not isinstance(selectors, Sequence) or isinstance(selectors, str):
            continue
        if selector_kind == "exact_pointer_set" and json_pointer in selectors:
            matches.append(row)
        if selector_kind == "prefix_set" and json_pointer is not None:
            for selector in selectors:
                if not isinstance(selector, str):
                    continue
                if json_pointer == selector or json_pointer.startswith(f"{selector}/"):
                    matches.append(row)
        if selector_kind == "element_pointer_pattern_set" and json_pointer is not None:
            for selector in selectors:
                if isinstance(selector, str) and _element_pattern_matches(
                    selector, json_pointer
                ):
                    matches.append(row)
    if not matches:
        raise SchemaContractError("source_pointer_use_not_allowed")
    uses = {row["allowed_use"] for row in matches}
    if allowed_use not in uses:
        raise SchemaContractError("source_pointer_use_not_allowed")


def _validate_exact_sequence(
    value: Sequence[str],
    expected: Sequence[str],
    *,
    label: str,
) -> None:
    code = (
        "output_schema_id_drift"
        if label == "allowed_output_schema_ids"
        else "operation_contract_drift"
    )
    if tuple(value) != tuple(expected):
        raise SchemaContractError(code, label)


def _validate_exact_mapping(
    value: Mapping[str, str],
    expected: Mapping[str, str],
    *,
    label: str,
) -> None:
    if dict(value) != dict(expected):
        raise SchemaContractError("role_schema_mapping_drift", label)


def _unique_sorted_set(values: Sequence[str], label: str) -> set[str]:
    string_values = _as_string_sequence(values, label)
    if list(string_values) != sorted(string_values):
        raise SchemaContractError("set_array_not_sorted", label)
    if len(set(string_values)) != len(string_values):
        raise SchemaContractError("set_array_duplicate", label)
    return set(string_values)


def _as_string_sequence(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, str):
        raise SchemaContractError("expected_string_sequence", label)
    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise SchemaContractError("expected_string_sequence", label)
        result.append(item)
    return tuple(result)


def _validate_tokens(value: object, placeholders: tuple[str, ...]) -> None:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise SchemaContractError("token_contract_violation")
    for token in value:
        if not isinstance(token, Mapping):
            raise SchemaContractError("token_contract_violation")
        kind = token.get("token_kind")
        if kind == "literal":
            validate_exact_keys(token, {"token_kind", "value"}, label="literal_token")
            literal = token["value"]
            if not isinstance(literal, str):
                raise SchemaContractError("token_contract_violation")
            if any(fragment in literal for fragment in _GLOB_FORBIDDEN_FRAGMENTS):
                raise SchemaContractError("wildcard_scope")
            if literal.endswith("/"):
                raise SchemaContractError("wildcard_scope")
            if any(fragment in literal for fragment in _SHELL_FORBIDDEN_FRAGMENTS):
                raise SchemaContractError("shell_syntax")
        elif kind == "placeholder":
            validate_exact_keys(
                token, {"token_kind", "placeholder_code"}, label="placeholder_token"
            )
            if token["placeholder_code"] not in placeholders:
                raise SchemaContractError("unknown_placeholder")
        else:
            raise SchemaContractError("token_contract_violation")


def _validate_environment(value: object, placeholders: tuple[str, ...]) -> None:
    if not isinstance(value, Mapping):
        raise SchemaContractError("environment_allowlist_mismatch")
    if set(value) != set(ALLOWED_ENVIRONMENT_VARIABLE_NAMES):
        raise SchemaContractError("environment_allowlist_mismatch")
    if value["PYTHONDONTWRITEBYTECODE"] != {"token_kind": "literal", "value": "1"}:
        raise SchemaContractError("environment_resolution_drift")
    if value["PYTHONPATH"] != {
        "token_kind": "placeholder",
        "placeholder_code": "repo_source_root",
    }:
        raise SchemaContractError("environment_resolution_drift")
    _validate_tokens([value["PYTHONDONTWRITEBYTECODE"]], placeholders)
    _validate_tokens([value["PYTHONPATH"]], placeholders)


def _reject_wildcard_scope(value: object) -> None:
    if value is None:
        return
    if not isinstance(value, Sequence) or isinstance(value, str):
        raise SchemaContractError("wildcard_scope")
    for item in value:
        if not isinstance(item, str):
            raise SchemaContractError("wildcard_scope")
        if (
            any(fragment in item for fragment in _GLOB_FORBIDDEN_FRAGMENTS)
            or item.endswith("/")
            or item == ""
        ):
            raise SchemaContractError("wildcard_scope")


def _validate_hash_map(value: object, *, label: str) -> dict[str, str]:
    if not isinstance(value, Mapping) or not value:
        raise SchemaContractError("hash_map_empty", label)
    result: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise SchemaContractError("hash_map_key_scope", label)
        if (
            any(fragment in key for fragment in _GLOB_FORBIDDEN_FRAGMENTS)
            or key.endswith("/")
            or "/" in key
        ):
            raise SchemaContractError("hash_map_key_scope", key)
        if not isinstance(item, str) or not item:
            raise SchemaContractError("hash_map_value", key)
        result[key] = _validate_lower_sha256(item, label=key)
    return result


def _source_path_pattern_matches(pattern: str, source_path: str) -> bool:
    _validate_repo_relative_path(source_path)
    if "{" not in pattern and "}" not in pattern:
        return pattern == source_path
    if pattern.count("{") != 1 or pattern.count("}") != 1:
        raise SchemaContractError("source_field_read_violation", pattern)
    prefix, remainder = pattern.split("{", 1)
    token, suffix = remainder.split("}", 1)
    if "{" in suffix or "}" in suffix:
        raise SchemaContractError("source_field_read_violation", pattern)
    alternatives = (
        G4_MANIFEST_CASE_IDS if token == "case_id" else tuple(token.split(","))
    )
    if not alternatives or any(not value for value in alternatives):
        raise SchemaContractError("source_field_read_violation", pattern)
    return source_path in {f"{prefix}{value}{suffix}" for value in alternatives}


def _validate_inventory_fail_category(
    values: Sequence[str],
    expected: set[str],
    *,
    code: str,
    label: str,
) -> None:
    paths = _unique_sorted_set(values, label)
    unknown = paths - expected
    if unknown:
        raise SchemaContractError(code, min(unknown))
    if paths:
        raise SchemaContractError(code, min(paths))


def _expected_origin_lineage_id(record: Mapping[str, JsonValue]) -> str:
    source_hashes = record.get("source_artifact_byte_hashes")
    if not isinstance(source_hashes, Mapping):
        raise SchemaContractError("semantic_lineage_ambiguous")
    preimage: dict[str, JsonValue] = {
        "origin_authority_id": _require_nonempty_string(
            record.get("source_authority_id"),
            "source_authority_id",
        ),
        "origin_subject_type": _require_nonempty_string(
            record.get("subject_type"),
            "subject_type",
        ),
        "origin_subject_id": _require_nonempty_string(
            record.get("subject_id"),
            "subject_id",
        ),
        "origin_dimension": _require_nonempty_string(
            record.get("dimension"),
            "dimension",
        ),
        "origin_comparison_projection_sha256_or_null": record.get(
            "comparison_projection_sha256_or_null"
        ),
        "origin_source_artifact_byte_hashes": dict(source_hashes),
    }
    return f"sha256:{g6b_canonical_json.canonical_sha256_v2(preimage)}"


def _reject_failure_status_upgrade(
    record: Mapping[str, JsonValue],
    target: Mapping[str, JsonValue],
) -> None:
    failure_statuses = {
        "not_applicable_retired_stage",
        "unreconstructable_refuse",
    }
    if target.get("dimension_status") in failure_statuses and record.get(
        "dimension_status"
    ) != target.get("dimension_status"):
        raise SchemaContractError("retired_projection_unreconstructable")


def _validate_output_schema_and_root(schema: object, root: object) -> None:
    if not isinstance(schema, Mapping):
        raise SchemaContractError("output_schema_id_drift")
    validate_exact_keys(
        schema,
        {"schema_id", "schema_version"},
        label="allowed_output_schema",
    )
    _require_nonempty_string(schema.get("schema_id"), "schema_id")
    _require_nonempty_string(schema.get("schema_version"), "schema_version")
    if not isinstance(root, Mapping):
        raise SchemaContractError("repo_relative_path_violation")
    validate_exact_keys(
        root,
        {"repo_relative_posix_path", "contains_only_governance_outputs"},
        label="allowed_output_root",
    )
    path = _require_nonempty_string(
        root.get("repo_relative_posix_path"),
        "repo_relative_posix_path",
    )
    _validate_repo_relative_path(path)
    if root.get("contains_only_governance_outputs") is not True:
        raise SchemaContractError("output_root_reuse_or_materialized")


def _reject_downstream_and_wildcard_refs(record: Mapping[str, JsonValue]) -> None:
    for key, value in record.items():
        if key in _DOWNSTREAM_REFERENCE_KEYS:
            raise SchemaContractError("downstream_reference", key)
        if isinstance(value, str):
            if any(fragment in value for fragment in _GLOB_FORBIDDEN_FRAGMENTS):
                raise SchemaContractError("wildcard_scope", key)
        elif isinstance(value, Sequence) and not isinstance(value, str | bytes):
            for item in value:
                if isinstance(item, str) and any(
                    fragment in item for fragment in _GLOB_FORBIDDEN_FRAGMENTS
                ):
                    raise SchemaContractError("wildcard_scope", key)


def _validate_normalizer_import(name: str) -> None:
    _reject_side_effect_import(name)
    if not name.startswith("ims_deadlock"):
        return
    if any(
        name == forbidden or name.startswith(f"{forbidden}.")
        for forbidden in NORMALIZATION_FORBIDDEN_IMPORTS
    ):
        raise SchemaContractError("capability_import_violation", name)
    if not any(
        name == allowed or name.startswith(f"{allowed}.")
        for allowed in NORMALIZATION_ALLOWED_PROJECT_IMPORTS
    ):
        raise SchemaContractError("capability_import_violation", name)


def _validate_preflight_import(name: str) -> None:
    _reject_side_effect_import(name)
    if not name.startswith("ims_deadlock"):
        return
    if any(
        name == forbidden or name.startswith(f"{forbidden}.")
        for forbidden in PREFLIGHT_FORBIDDEN_IMPORTS
    ):
        raise SchemaContractError("capability_import_violation", name)
    if not any(
        name == allowed or name.startswith(f"{allowed}.")
        for allowed in ALLOWED_PREFLIGHT_PROJECT_IMPORTS
    ):
        raise SchemaContractError("capability_import_violation", name)


def _validate_normalizer_call(call_name: str, node: ast.Call) -> None:
    if _is_dynamic_import_call(call_name):
        imported_name = node.args[0] if node.args else None
        if isinstance(imported_name, ast.Constant) and isinstance(
            imported_name.value,
            str,
        ):
            _validate_normalizer_import(imported_name.value)
        raise SchemaContractError("capability_import_violation", call_name)
    if _is_dynamic_builtin_call(call_name):
        raise SchemaContractError("capability_call_violation", call_name)
    if _is_safe_object_method(call_name):
        return
    if _is_unlisted_safe_object_method(call_name):
        raise SchemaContractError("retired_normalizer_error", call_name)
    _reject_unapproved_side_effect_call(
        call_name,
        node,
        allowed_writer_symbols=ALLOWED_NORMALIZER_WRITER_SYMBOLS,
        error_code="retired_normalizer_error",
    )
    if call_name in NORMALIZER_PROHIBITED_WRITE_CALLS:
        if call_name == "open":
            for arg in node.args[1:2]:
                if (
                    isinstance(arg, ast.Constant)
                    and isinstance(arg.value, str)
                    and any(flag in arg.value for flag in ("w", "a", "+"))
                ):
                    raise SchemaContractError("retired_normalizer_error")
            for keyword in node.keywords:
                if (
                    keyword.arg == "mode"
                    and isinstance(keyword.value, ast.Constant)
                    and isinstance(keyword.value.value, str)
                    and any(flag in keyword.value.value for flag in ("w", "a", "+"))
                ):
                    raise SchemaContractError("retired_normalizer_error")
        else:
            raise SchemaContractError("retired_normalizer_error")
    forbidden_suffixes = {
        "run_after_freeze": "capability_call_violation",
        "enumerate_stable_lts": "capability_call_violation",
        "partition_stable_lts": "capability_call_violation",
        "certify_absorption_domain": "capability_call_violation",
        "derive_absorbing_ctmc": "capability_call_violation",
        "simulate": "capability_call_violation",
        "score_case": "capability_call_violation",
        "score_run": "capability_call_violation",
    }
    for suffix, code in forbidden_suffixes.items():
        if call_name == suffix or call_name.endswith(f".{suffix}"):
            raise SchemaContractError(code, call_name)
    if call_name in NORMALIZATION_FORBIDDEN_CALLS:
        raise SchemaContractError("capability_call_violation", call_name)


def _reject_side_effect_import(name: str) -> None:
    if any(
        name == forbidden or name.startswith(f"{forbidden}.")
        for forbidden in SIDE_EFFECT_IMPORT_ROOTS
    ):
        raise SchemaContractError("capability_import_violation", name)


def _reject_unapproved_side_effect_call(
    call_name: str,
    node: ast.Call,
    *,
    allowed_writer_symbols: Sequence[str],
    error_code: str,
) -> None:
    if call_name in allowed_writer_symbols:
        return
    leaf_name = call_name.rsplit(".", 1)[-1]
    if leaf_name == "open" and (
        call_name not in {"open", "io.open"} or _call_uses_write_mode(node)
    ):
        raise SchemaContractError(error_code, call_name)
    if leaf_name in FILESYSTEM_MUTATOR_NAMES or leaf_name.startswith(
        ("write_", "append_")
    ):
        raise SchemaContractError(error_code, call_name)
    if call_name.startswith("os."):
        raise SchemaContractError(error_code, call_name)
    if any(call_name.startswith(prefix) for prefix in SIDE_EFFECT_CALL_PREFIXES):
        raise SchemaContractError(error_code, call_name)


def _call_uses_write_mode(node: ast.Call) -> bool:
    mode_nodes = list(node.args[1:2]) + [
        keyword.value for keyword in node.keywords if keyword.arg == "mode"
    ]
    if not mode_nodes:
        return False
    for mode_node in mode_nodes:
        if not isinstance(mode_node, ast.Constant) or not isinstance(
            mode_node.value,
            str,
        ):
            return True
        if any(flag in mode_node.value for flag in ("w", "a", "x", "+")):
            return True
    return False


def _ast_call_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base_node = node.value.func if isinstance(node.value, ast.Call) else node.value
        base = _ast_call_name(base_node)
        if node.attr == "__call__":
            return base
        return f"{base}.{node.attr}" if base else ""
    return ""


def _add_callable_alias(
    aliases: dict[str, set[str]],
    name: str,
    targets: set[str],
) -> None:
    if targets:
        aliases.setdefault(name, set()).update(targets)


def _ast_callable_value_names(
    node: ast.expr,
    aliases: Mapping[str, set[str]],
) -> set[str]:
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Call):
        base_names = _safe_call_result_object_names(node.value, aliases)
        if base_names:
            return {f"{base_name}.{node.attr}" for base_name in base_names}
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Subscript):
        base_names = _ast_callable_value_names(node.value, aliases)
        if base_names:
            return {f"{base_name}.{node.attr}" for base_name in base_names}
    if isinstance(node, ast.IfExp):
        return _ast_callable_value_names(
            node.body, aliases
        ) | _ast_callable_value_names(
            node.orelse,
            aliases,
        )
    if isinstance(node, ast.BoolOp):
        value_names: set[str] = set()
        for value in node.values:
            value_names.update(_ast_callable_value_names(value, aliases))
        return value_names
    if isinstance(node, ast.List | ast.Tuple | ast.Set):
        value_names = set()
        for element in node.elts:
            value_names.update(_ast_callable_value_names(element, aliases))
        return value_names
    if isinstance(node, ast.Dict):
        value_names = set()
        for key, value in zip(node.keys, node.values, strict=False):
            if key is not None:
                value_names.update(_ast_callable_value_names(key, aliases))
            value_names.update(_ast_callable_value_names(value, aliases))
        return value_names
    if isinstance(node, ast.Subscript):
        selected_value = _literal_container_subscript_value(node)
        if selected_value is not None:
            return _ast_callable_value_names(selected_value, aliases)
        base_name = _ast_call_name(node.value)
        if (
            base_name == "__builtins__"
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        ):
            return {node.slice.value}
        if base_name in aliases:
            return _resolve_imported_symbols(base_name, aliases)
        if isinstance(node.value, ast.Subscript):
            return _ast_callable_value_names(node.value, aliases)
    call_name = _ast_call_name(node)
    if call_name:
        return _resolve_imported_symbols(call_name, aliases)
    return set()


def _safe_call_result_object_names(
    node: ast.expr,
    aliases: Mapping[str, set[str]],
) -> set[str]:
    if not isinstance(node, ast.Call):
        return set()
    raw_call_name = _ast_call_name(node.func)
    if not raw_call_name:
        return set()
    resolved_names = _resolve_imported_symbols(raw_call_name, aliases)
    if not resolved_names:
        return set()
    safe_names: set[str] = set()
    for call_name in resolved_names:
        safe_name = _SAFE_CALL_RESULT_OBJECTS.get(call_name)
        if safe_name is None:
            return set()
        safe_names.add(safe_name)
    return safe_names


def _is_safe_object_method(call_name: str) -> bool:
    base_name, separator, method_name = call_name.rpartition(".")
    if not separator:
        return False
    return method_name in _SAFE_OBJECT_METHODS.get(base_name, frozenset())


def _is_unlisted_safe_object_method(call_name: str) -> bool:
    base_name, separator, method_name = call_name.rpartition(".")
    return bool(
        separator
        and base_name in _SAFE_OBJECT_METHODS
        and method_name not in _SAFE_OBJECT_METHODS[base_name]
    )


def _uses_reserved_safe_alias_name(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in _RESERVED_SAFE_ALIAS_NAMES:
            return True
    return False


def _literal_container_subscript_value(node: ast.Subscript) -> ast.expr | None:
    if not isinstance(node.slice, ast.Constant):
        return None
    key = node.slice.value
    if (
        isinstance(node.value, ast.List | ast.Tuple)
        and isinstance(key, int)
        and 0 <= key < len(node.value.elts)
    ):
        return node.value.elts[key]
    if isinstance(node.value, ast.Dict):
        for dict_key, dict_value in zip(
            node.value.keys,
            node.value.values,
            strict=False,
        ):
            if isinstance(dict_key, ast.Constant) and dict_key.value == key:
                return dict_value
    return None


def _value_may_produce_unknown_callable(node: ast.expr) -> bool:
    if isinstance(node, ast.Call | ast.Lambda):
        return True
    if isinstance(node, ast.Attribute):
        return _value_may_produce_unknown_callable(node.value)
    if isinstance(node, ast.IfExp):
        return _value_may_produce_unknown_callable(
            node.body
        ) or _value_may_produce_unknown_callable(node.orelse)
    if isinstance(node, ast.BoolOp):
        return any(_value_may_produce_unknown_callable(value) for value in node.values)
    if isinstance(node, ast.Subscript):
        return True
    if isinstance(node, ast.List | ast.Tuple | ast.Set | ast.Dict):
        return any(
            isinstance(child, ast.expr)
            and (_ast_call_name(child) or isinstance(child, ast.Call | ast.Lambda))
            for child in ast.walk(node)
            if child is not node
        )
    return False


def _extend_callable_assignment_aliases(
    tree: ast.AST,
    aliases: dict[str, set[str]],
) -> None:
    pending_aliases: dict[str, set[str]] = {}
    called_names = {
        call_name
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        if (call_name := _ast_call_name(node.func))
    }

    def target_is_called(target_name: str) -> bool:
        return any(
            call_name == target_name or call_name.startswith(f"{target_name}.")
            for call_name in called_names
        )

    source_names: set[str] = set()

    def collect_source_names(value: ast.expr) -> None:
        for child in ast.walk(value):
            if isinstance(child, ast.Name | ast.Attribute):
                source_name = _ast_call_name(child)
                if source_name:
                    source_names.add(source_name)

    def collect_extraction_source_names(value: ast.expr) -> None:
        if isinstance(value, ast.Call):
            return
        if isinstance(value, ast.Name | ast.Attribute):
            source_name = _ast_call_name(value)
            if source_name:
                source_names.add(source_name)
            return
        for child in ast.iter_child_nodes(value):
            if isinstance(child, ast.expr):
                collect_extraction_source_names(child)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Tuple | ast.List) for target in node.targets):
                collect_source_names(node.value)
            else:
                collect_extraction_source_names(node.value)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Tuple | ast.List) and node.value is not None:
                collect_source_names(node.value)
            elif node.value is not None:
                collect_extraction_source_names(node.value)
        elif isinstance(node, ast.NamedExpr):
            collect_extraction_source_names(node.value)
        elif isinstance(node, ast.For | ast.AsyncFor | ast.comprehension):
            collect_source_names(node.iter)
        elif isinstance(node, ast.Match):
            collect_source_names(node.subject)
        elif isinstance(node, ast.With | ast.AsyncWith):
            for item in node.items:
                collect_source_names(item.context_expr)

    def target_is_source(target_name: str) -> bool:
        return any(
            source_name == target_name or source_name.startswith(f"{target_name}.")
            for source_name in source_names
        )

    def add_binding_alias(
        target: ast.expr,
        value_names: set[str],
        *,
        unknown_source: bool,
    ) -> None:
        if isinstance(target, ast.Tuple | ast.List):
            for target_item in target.elts:
                add_binding_alias(
                    target_item,
                    value_names,
                    unknown_source=unknown_source,
                )
            return
        target_name = _ast_call_name(target)
        if not target_name:
            return
        if value_names:
            _add_callable_alias(pending_aliases, target_name, value_names)
        elif unknown_source and target_is_called(target_name):
            _add_callable_alias(
                pending_aliases,
                target_name,
                {_UNKNOWN_CALLABLE_ALIAS},
            )

    def binding_target_names(target: ast.expr) -> set[str]:
        if isinstance(target, ast.Name):
            return {target.id}
        if isinstance(target, ast.Starred):
            return binding_target_names(target.value)
        if isinstance(target, ast.Tuple | ast.List):
            names: set[str] = set()
            for target_item in target.elts:
                names.update(binding_target_names(target_item))
            return names
        return set()

    def has_starred_target(target: ast.expr) -> bool:
        return any(isinstance(child, ast.Starred) for child in ast.walk(target))

    def iter_value_names(value: ast.expr) -> set[str]:
        if isinstance(value, ast.List | ast.Tuple | ast.Set):
            names: set[str] = set()
            for element in value.elts:
                names.update(_ast_callable_value_names(element, aliases))
            return names
        return _ast_callable_value_names(value, aliases)

    def add_alias(target: ast.expr, value: ast.expr) -> None:
        if isinstance(target, ast.Tuple | ast.List):
            if isinstance(value, ast.Tuple | ast.List) and not has_starred_target(
                target
            ):
                for target_item, value_item in zip(
                    target.elts,
                    value.elts,
                    strict=False,
                ):
                    add_alias(target_item, value_item)
                return
            value_names = _ast_callable_value_names(value, aliases)
            for target_name in binding_target_names(target):
                if not target_is_called(target_name):
                    continue
                if value_names:
                    _add_callable_alias(pending_aliases, target_name, value_names)
                else:
                    _add_callable_alias(
                        pending_aliases,
                        target_name,
                        {_UNKNOWN_CALLABLE_ALIAS},
                    )
            return
        target_name = _ast_call_name(target)
        value_names = _ast_callable_value_names(value, aliases)
        if target_name and not value_names:
            value_names = _safe_call_result_object_names(value, aliases)
        if (
            target_name
            and not value_names
            and (target_is_called(target_name) or target_is_source(target_name))
            and _value_may_produce_unknown_callable(value)
        ):
            value_names = {_UNKNOWN_CALLABLE_ALIAS}
        if target_name and value_names:
            _add_callable_alias(pending_aliases, target_name, value_names)

    def capture_pattern_names(pattern: ast.pattern) -> set[str]:
        if isinstance(pattern, ast.MatchAs):
            return (
                {pattern.name}
                if pattern.name is not None and pattern.name != "_"
                else set()
            )
        if isinstance(pattern, ast.MatchStar):
            return (
                {pattern.name}
                if pattern.name is not None and pattern.name != "_"
                else set()
            )
        names: set[str] = set()
        for child in ast.iter_child_nodes(pattern):
            if isinstance(child, ast.pattern):
                names.update(capture_pattern_names(child))
        return names

    def add_class_aliases(node: ast.ClassDef, prefix: str) -> None:
        class_name = f"{prefix}.{node.name}" if prefix else node.name
        for statement in node.body:
            if isinstance(statement, ast.Assign):
                for target in statement.targets:
                    if isinstance(target, ast.Name):
                        add_alias(
                            ast.Attribute(
                                value=ast.Name(id=class_name, ctx=ast.Load()),
                                attr=target.id,
                                ctx=ast.Store(),
                            ),
                            statement.value,
                        )
            elif isinstance(statement, ast.AnnAssign) and isinstance(
                statement.target,
                ast.Name,
            ):
                if statement.value is not None:
                    add_alias(
                        ast.Attribute(
                            value=ast.Name(id=class_name, ctx=ast.Load()),
                            attr=statement.target.id,
                            ctx=ast.Store(),
                        ),
                        statement.value,
                    )
            elif isinstance(statement, ast.ClassDef):
                add_class_aliases(statement, class_name)

    function_defs: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}

    def positional_args(args: ast.arguments) -> list[ast.arg]:
        return [*args.posonlyargs, *args.args]

    def returned_callable_value_names(value: ast.expr) -> set[str]:
        if isinstance(value, ast.IfExp):
            return returned_callable_value_names(
                value.body
            ) | returned_callable_value_names(value.orelse)
        if isinstance(value, ast.BoolOp):
            value_names: set[str] = set()
            for item in value.values:
                value_names.update(returned_callable_value_names(item))
            return value_names
        if isinstance(value, ast.List | ast.Tuple | ast.Set):
            value_names = set()
            for element in value.elts:
                value_names.update(returned_callable_value_names(element))
            return value_names
        if isinstance(value, ast.Dict):
            value_names = set()
            for key, item in zip(value.keys, value.values, strict=False):
                if key is not None:
                    value_names.update(returned_callable_value_names(key))
                value_names.update(returned_callable_value_names(item))
            return value_names
        if isinstance(value, ast.Subscript):
            selected_value = _literal_container_subscript_value(value)
            if selected_value is not None:
                return returned_callable_value_names(selected_value)
            value_names = returned_callable_value_names(value.value)
            return value_names or {_UNKNOWN_CALLABLE_ALIAS}
        if isinstance(value, ast.Call):
            value_names = _ast_callable_value_names(value.func, aliases)
            raw_call_name = _ast_call_name(value.func)
            if raw_call_name:
                value_names.add(raw_call_name)
            return value_names
        return _ast_callable_value_names(value, aliases)

    def add_parameter_taints(args: ast.arguments, body: ast.AST) -> None:
        positional = positional_args(args)
        parameter_names = {arg.arg for arg in [*positional, *args.kwonlyargs]} | (
            {args.vararg.arg} if args.vararg is not None else set()
        )
        parameter_names |= {args.kwarg.arg} if args.kwarg is not None else set()

        def add_parameter_member_taint(call_name: str) -> None:
            if "." not in call_name:
                return
            parameter_name, member_name = call_name.split(".", 1)
            if (
                parameter_name in parameter_names
                and (parameter_name, member_name) not in _SAFE_PARAMETER_DATA_METHODS
            ):
                _add_callable_alias(
                    pending_aliases,
                    call_name,
                    {_UNKNOWN_CALLABLE_ALIAS},
                )

        for child in ast.walk(body):
            if isinstance(child, ast.Attribute):
                add_parameter_member_taint(_ast_call_name(child))
        for call in ast.walk(body):
            if not isinstance(call, ast.Call):
                continue
            call_name = _ast_call_name(call.func)
            if call_name in parameter_names:
                _add_callable_alias(
                    pending_aliases,
                    call_name,
                    {_UNKNOWN_CALLABLE_ALIAS},
                )
            else:
                add_parameter_member_taint(call_name)
        if args.defaults:
            for arg, positional_default in zip(
                positional[-len(args.defaults) :],
                args.defaults,
                strict=False,
            ):
                _add_callable_alias(
                    pending_aliases,
                    arg.arg,
                    _ast_callable_value_names(positional_default, aliases),
                )
        for arg, keyword_default in zip(
            args.kwonlyargs,
            args.kw_defaults,
            strict=False,
        ):
            default_value = keyword_default
            if default_value is None:
                continue
            _add_callable_alias(
                pending_aliases,
                arg.arg,
                _ast_callable_value_names(default_value, aliases),
            )

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            function_defs[node.name] = node
            add_parameter_taints(node.args, node)
            for return_node in ast.walk(node):
                if return_node is node or not isinstance(return_node, ast.Return):
                    continue
                if return_node.value is not None:
                    _add_callable_alias(
                        pending_aliases,
                        node.name,
                        returned_callable_value_names(return_node.value),
                    )
        elif isinstance(node, ast.Lambda):
            add_parameter_taints(node.args, node.body)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                add_alias(target, node.value)
        elif isinstance(node, ast.AnnAssign):
            if node.value is not None:
                add_alias(node.target, node.value)
        elif isinstance(node, ast.NamedExpr):
            add_alias(node.target, node.value)
        elif isinstance(node, ast.ClassDef):
            add_class_aliases(node, "")
        elif isinstance(node, ast.For | ast.AsyncFor | ast.comprehension):
            iter_expr = node.iter
            value_names = iter_value_names(iter_expr)
            add_binding_alias(
                node.target,
                value_names,
                unknown_source=not value_names,
            )
        elif isinstance(node, ast.Match):
            value_names = _ast_callable_value_names(node.subject, aliases)
            unknown_source = not value_names
            for match_case in node.cases:
                for capture_name in capture_pattern_names(match_case.pattern):
                    add_binding_alias(
                        ast.Name(id=capture_name, ctx=ast.Store()),
                        value_names,
                        unknown_source=unknown_source,
                    )
        elif isinstance(node, ast.With | ast.AsyncWith):
            for item in node.items:
                if item.optional_vars is None:
                    continue
                value_names = _ast_callable_value_names(item.context_expr, aliases)
                add_binding_alias(
                    item.optional_vars,
                    value_names,
                    unknown_source=not value_names,
                )
        elif isinstance(node, ast.Call):
            function_name = _ast_call_name(node.func)
            function_def = function_defs.get(function_name)
            if function_def is None:
                continue
            for arg, value in zip(
                positional_args(function_def.args),
                node.args,
                strict=False,
            ):
                _add_callable_alias(
                    pending_aliases,
                    arg.arg,
                    _ast_callable_value_names(value, aliases),
                )
            for keyword in node.keywords:
                if keyword.arg is not None:
                    _add_callable_alias(
                        pending_aliases,
                        keyword.arg,
                        _ast_callable_value_names(keyword.value, aliases),
                    )

    for alias_name, alias_targets in pending_aliases.items():
        _add_callable_alias(aliases, alias_name, alias_targets)
    for _ in range(len(pending_aliases) + 1):
        changed = False
        for alias_name, alias_targets in pending_aliases.items():
            resolved_targets: set[str] = set()
            for alias_target in alias_targets:
                resolved_targets.update(
                    _resolve_imported_symbols(alias_target, aliases)
                )
            before = set(aliases.get(alias_name, set()))
            _add_callable_alias(aliases, alias_name, resolved_targets)
            if aliases.get(alias_name, set()) != before:
                changed = True
        if not changed:
            break


def _resolve_imported_symbols(
    call_name: str,
    aliases: Mapping[str, set[str]],
) -> set[str]:
    def resolve_exact(name: str, seen: set[str]) -> set[str]:
        if name in seen:
            return {_UNKNOWN_CALLABLE_ALIAS}
        targets = aliases.get(name)
        if not targets:
            return {name}
        resolved: set[str] = set()
        for target in targets:
            resolved.update(resolve_name(target, seen | {name}))
        return resolved

    def resolve_name(name: str, seen: set[str]) -> set[str]:
        exact = resolve_exact(name, seen)
        if exact != {name}:
            return exact
        parts = name.split(".")
        for index in range(len(parts) - 1, 0, -1):
            prefix = ".".join(parts[:index])
            suffix = ".".join(parts[index:])
            resolved_prefixes = resolve_exact(prefix, seen)
            if resolved_prefixes != {prefix}:
                resolved_names: set[str] = set()
                for resolved_prefix in resolved_prefixes:
                    resolved_names.update(
                        resolve_name(f"{resolved_prefix}.{suffix}", seen | {prefix})
                    )
                return resolved_names
        return {name}

    return resolve_name(call_name, set())


def _is_unknown_callable_alias(call_name: str) -> bool:
    return call_name == _UNKNOWN_CALLABLE_ALIAS or call_name.startswith(
        f"{_UNKNOWN_CALLABLE_ALIAS}."
    )


def _is_dynamic_import_call(call_name: str) -> bool:
    return call_name in {
        "__import__",
        "builtins.__import__",
        "importlib.import_module",
    }


def _is_dynamic_builtin_call(call_name: str) -> bool:
    return call_name in {
        "eval",
        "exec",
        "getattr",
        "setattr",
        "builtins.eval",
        "builtins.exec",
        "builtins.getattr",
        "builtins.setattr",
        "operator.attrgetter",
        "operator.methodcaller",
    }


def _is_sensitive_callable_value(call_name: str) -> bool:
    if _is_unknown_callable_alias(call_name):
        return True
    if _is_unlisted_safe_object_method(call_name):
        return True
    if _is_dynamic_import_call(call_name) or _is_dynamic_builtin_call(call_name):
        return True
    if call_name in {"open", "io.open"}:
        return True
    leaf_name = call_name.rsplit(".", 1)[-1]
    if call_name.startswith("os."):
        return True
    if leaf_name in FILESYSTEM_MUTATOR_NAMES:
        return True
    if any(call_name.startswith(prefix) for prefix in SIDE_EFFECT_CALL_PREFIXES):
        return True
    forbidden_calls = (*NORMALIZATION_FORBIDDEN_CALLS, *PREFLIGHT_FORBIDDEN_CALLS)
    return any(
        call_name == forbidden or call_name.endswith(f".{forbidden.rsplit('.', 1)[-1]}")
        for forbidden in forbidden_calls
    )


def _reject_sensitive_callable_escapes(
    node: ast.Call,
    aliases: Mapping[str, set[str]],
    *,
    error_code: str,
) -> None:
    values = list(node.args) + [keyword.value for keyword in node.keywords]
    for value in values:
        for child in ast.walk(value):
            if not isinstance(child, ast.expr):
                continue
            call_names = _ast_callable_value_names(child, aliases)
            for call_name in call_names:
                if _is_sensitive_callable_value(call_name):
                    code = (
                        "capability_import_violation"
                        if "import" in call_name
                        else error_code
                    )
                    raise SchemaContractError(code, call_name)


def _find_forbidden_keys(value: object, forbidden: set[str]) -> set[str]:
    found: set[str] = set()
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if isinstance(key, str) and key in forbidden:
                found.add(key)
            found.update(_find_forbidden_keys(nested, forbidden))
    elif isinstance(value, Sequence) and not isinstance(value, str | bytes):
        for item in value:
            found.update(_find_forbidden_keys(item, forbidden))
    return found


def _find_estimand_id_paths(
    value: object,
    path: JsonPath = (),
) -> list[tuple[JsonPath, object]]:
    found: list[tuple[JsonPath, object]] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            nested_path = (*path, key)
            if key == "estimand_id":
                found.append((nested_path, nested))
            found.extend(_find_estimand_id_paths(nested, nested_path))
    elif isinstance(value, Sequence) and not isinstance(value, str | bytes):
        for index, item in enumerate(value):
            found.extend(_find_estimand_id_paths(item, (*path, index)))
    return found


def _format_path(path: JsonPath) -> str:
    if not path:
        return "/"
    return "/" + "/".join(str(part) for part in path)


def _validate_optional_projection_hash(value: object, *, label: str) -> str | None:
    if value is None:
        return None
    return _validate_lower_sha256(value, label=label)


def _validate_nullable_ref(value: object, *, label: str) -> None:
    if value is None:
        return
    if not isinstance(value, str) or value == "":
        raise SchemaContractError("expected_nullable_ref", label)


def _validate_nullable_refusal_code(value: object) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        raise SchemaContractError("unknown_refusal_code")
    validate_refusal_codes("normalization_overlap", [value])


def _validate_comparison_status_refusals(
    status: str,
    refusal_code: JsonValue,
) -> None:
    if status in COMPARISON_FAIL_CLOSED_STATUSES:
        if refusal_code is None:
            raise SchemaContractError("refusal_reason_required", status)
        return
    if status in COMPARISON_SUCCESS_STATUSES:
        if refusal_code is not None:
            raise SchemaContractError("refusal_reason_unexpected", status)
        return
    raise SchemaContractError("unknown_comparison_status", status)


def _require_comparison_projection_hashes(
    new_projection_hash: str | None,
    retired_projection_hash: str | None,
    *,
    status: str,
) -> tuple[str, str]:
    if new_projection_hash is None or retired_projection_hash is None:
        raise SchemaContractError("missing_source", status)
    return new_projection_hash, retired_projection_hash


def _validate_semantic_dimension_comparison(
    *,
    dimension: str,
    status: str,
    new_projection_hash: str | None,
    retired_projection_hash: str | None,
    semantic_lineage_audit_ref: JsonValue,
    semantic_lineage_audit_passed: bool | None,
) -> None:
    if status in COMPARISON_FAIL_CLOSED_STATUSES or status == "inherited_compared":
        return
    if status != "pass_distinct":
        raise SchemaContractError("comparison_status_not_allowed", dimension)
    new_hash, retired_hash = _require_comparison_projection_hashes(
        new_projection_hash,
        retired_projection_hash,
        status=status,
    )
    if new_hash == retired_hash:
        raise SchemaContractError("overlap_hit", dimension)
    if semantic_lineage_audit_ref is None or semantic_lineage_audit_passed is not True:
        raise SchemaContractError("semantic_lineage_ambiguous", dimension)


def _validate_random_stream_comparison(
    *,
    status: str,
    new_projection_hash: str | None,
    retired_projection_hash: str | None,
    random_stream_branch: Literal["exact", "stochastic"] | None,
    disjoint_substream_proof_passed: bool | None,
) -> None:
    if status in COMPARISON_FAIL_CLOSED_STATUSES or status == "inherited_compared":
        return
    new_hash, retired_hash = _require_comparison_projection_hashes(
        new_projection_hash,
        retired_projection_hash,
        status=status,
    )
    if random_stream_branch == "exact":
        if status != "not_applicable_by_protocol_pass":
            raise SchemaContractError("comparison_status_not_allowed", status)
        if new_hash != retired_hash:
            raise SchemaContractError("not_applicable_projection_mismatch")
        return
    if random_stream_branch == "stochastic":
        if status != "disjoint_stream_pass":
            raise SchemaContractError("comparison_status_not_allowed", status)
        if disjoint_substream_proof_passed is not True:
            raise SchemaContractError("random_stream_disjointness_unproved")
        if new_hash == retired_hash:
            raise SchemaContractError("random_stream_overlap")
        return
    raise SchemaContractError("random_stream_branch_required")


def _validate_output_root_comparison(
    *,
    status: str,
    new_projection_hash: str | None,
    retired_projection_hash: str | None,
) -> None:
    if status in COMPARISON_FAIL_CLOSED_STATUSES or status == "inherited_compared":
        return
    if status != "containment_separation_pass":
        raise SchemaContractError("comparison_status_not_allowed", status)
    new_hash, retired_hash = _require_comparison_projection_hashes(
        new_projection_hash,
        retired_projection_hash,
        status=status,
    )
    if new_hash == retired_hash:
        raise SchemaContractError("output_root_reuse_or_materialized")


def _validate_metric_schema_comparison(
    *,
    status: str,
    new_projection_hash: str | None,
    retired_projection_hash: str | None,
    reuse_authorization_ref: JsonValue,
    metric_reuse_authorized: bool | None,
) -> None:
    if status in COMPARISON_FAIL_CLOSED_STATUSES or status == "inherited_compared":
        return
    new_hash, retired_hash = _require_comparison_projection_hashes(
        new_projection_hash,
        retired_projection_hash,
        status=status,
    )
    if status == "pass_distinct":
        if new_hash == retired_hash:
            raise SchemaContractError("metric_reuse_unauthorized")
        return
    if status == "controlled_reuse_pass":
        if reuse_authorization_ref is None or metric_reuse_authorized is not True:
            raise SchemaContractError("metric_reuse_unauthorized")
        return
    raise SchemaContractError("comparison_status_not_allowed", status)


def _validate_dimension_relation(
    value: object,
    expected: frozenset[str],
    *,
    label: str,
) -> None:
    actual = _unique_sorted_set(_require_sequence(value, label), label)
    unknown = sorted(actual - set(FINGERPRINT_DIMENSIONS))
    if unknown:
        raise SchemaContractError("unknown_dimension", unknown[0])
    if actual != set(expected):
        raise SchemaContractError("dimension_relation_mismatch", label)


def _validate_source_artifacts(refs: object, byte_hashes: object) -> None:
    if not isinstance(refs, Sequence) or isinstance(refs, str | bytes):
        raise SchemaContractError("expected_source_artifact_refs")
    seen_refs: set[tuple[str, str, str | None, str]] = set()
    ordered_refs: list[tuple[str, str, str, str]] = []
    paths: set[str] = set()
    for ref in refs:
        if not isinstance(ref, Mapping):
            raise SchemaContractError("source_artifact_ref_type")
        validate_exact_keys(
            ref,
            SOURCE_ARTIFACT_REF_REQUIRED_FIELDS,
            label="source_artifact_ref",
        )
        authority_id = _require_nonempty_string(ref.get("authority_id"), "authority_id")
        path = _require_nonempty_string(
            ref.get("repo_relative_posix_path"),
            "repo_relative_posix_path",
        )
        _validate_repo_relative_path(path)
        pointer = ref.get("json_pointer_or_null")
        if pointer is not None and (
            not isinstance(pointer, str) or not pointer.startswith("/")
        ):
            raise SchemaContractError("json_pointer_contract")
        source_role = _require_nonempty_string(ref.get("source_role"), "source_role")
        ref_key = (authority_id, path, pointer, source_role)
        if ref_key in seen_refs:
            raise SchemaContractError("source_artifact_ref_duplicate", path)
        seen_refs.add(ref_key)
        ordered_refs.append(
            (authority_id, path, "" if pointer is None else pointer, source_role)
        )
        paths.add(path)
    if ordered_refs != sorted(ordered_refs):
        raise SchemaContractError("source_artifact_ref_not_sorted")
    if not isinstance(byte_hashes, Mapping):
        raise SchemaContractError("source_artifact_hash_map_mismatch")
    if set(byte_hashes) != paths:
        raise SchemaContractError("source_artifact_hash_map_mismatch")
    for path, digest in byte_hashes.items():
        if not isinstance(path, str):
            raise SchemaContractError("source_artifact_hash_map_mismatch")
        _validate_repo_relative_path(path)
        _validate_lower_sha256(digest, label=path)


def _validate_lower_sha256(value: object, *, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise SchemaContractError("invalid_hash_digest", label)
    if any(character not in LOWER_SHA256_HEX_DIGITS for character in value):
        raise SchemaContractError("invalid_hash_digest", label) from None
    return value


def _validate_git_object_id(value: object, *, label: str) -> str:
    if not isinstance(value, str) or len(value) not in {40, 64}:
        raise SchemaContractError("invalid_hash_digest", label)
    if any(character not in LOWER_SHA256_HEX_DIGITS for character in value):
        raise SchemaContractError("invalid_hash_digest", label)
    return value


def _validate_prefixed_sha256(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise SchemaContractError("invalid_hash_digest", label)
    _validate_lower_sha256(value.removeprefix("sha256:"), label=label)
    return value


def _validate_utc_timestamp(value: object, *, label: str) -> str:
    timestamp = _require_nonempty_string(value, label)
    try:
        parsed = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError as exc:
        raise SchemaContractError("timestamp_format_violation", label) from exc
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != timestamp:
        raise SchemaContractError("timestamp_format_violation", label)
    return timestamp


def _validate_repo_relative_path(path: str) -> None:
    try:
        g6b_canonical_json.validate_repo_relative_posix_path(path)
    except g6b_canonical_json.CanonicalJsonError as exc:
        raise SchemaContractError("repo_relative_path_violation", exc.code) from exc


def _verify_finalized_self_hash(record: Mapping[str, JsonValue], field: str) -> None:
    try:
        g6b_canonical_json.verify_finalized_self_hash(dict(record), field)
    except g6b_canonical_json.CanonicalJsonError as exc:
        raise SchemaContractError(exc.code, field) from exc


def _require_nonempty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or value == "":
        raise SchemaContractError("expected_nonempty_string", label)
    return value


def _require_sequence(value: object, label: str) -> Sequence[str]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise SchemaContractError("expected_string_sequence", label)
    return value


def _element_pattern_matches(pattern: str, pointer: str) -> bool:
    pattern_parts = pattern.split("/")
    pointer_parts = pointer.split("/")
    if len(pattern_parts) != len(pointer_parts):
        return False
    for pattern_part, pointer_part in zip(pattern_parts, pointer_parts, strict=True):
        if pattern_part == "*":
            if pointer_part == "":
                return False
            continue
        if pattern_part != pointer_part:
            return False
    return True


def _find_contaminated_keys(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if isinstance(key, str) and key in _SUBJECT_CONTAMINATION_KEYS:
                found.add(key)
            found.update(_find_contaminated_keys(nested))
    elif isinstance(value, Sequence) and not isinstance(value, str | bytes):
        for item in value:
            found.update(_find_contaminated_keys(item))
    return found
