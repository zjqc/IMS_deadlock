"""Data-only validation for the exact-twelve G6-B schema bundle."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn, TypeAlias

JsonObject: TypeAlias = dict[str, Any]
JsonPath: TypeAlias = tuple[str | int, ...]

G6B_ROW_FAMILY_PROTOCOL_VERSION = "ims-deadlock/g6b-row-family-protocol/v2"
G6B_ROW_FAMILY_IDENTITY_VERSION = "ims-deadlock/g6b-row-family-identity/v3"
G6B_ROW_FAMILY_MATRIX_VERSION = "ims-deadlock/g6b-row-family-matrix/v1"
G6B_ROW_FAMILY_REUSE_VERSION = "ims-deadlock/g6b-row-family-reuse/v2"
G6B_ROW_FAMILY_OVERLAP_VERSION = "ims-deadlock/g6b-row-family-overlap-schema/v2"
G6B_ROW_FAMILY_RUNTIME_LOCK_VERSION = (
    "ims-deadlock/g6b-row-family-runtime-lock-schema/v2"
)
G6B_ROW_FAMILY_REVIEW_STATE_VERSION = "ims-deadlock/g6b-row-family-review-state/v2"
G6B_ROW_FAMILY_FAILURE_LEDGER_VERSION = "ims-deadlock/g6b-row-family-failure-ledger/v2"
G6B_CASE_CONSTRUCTION_SCHEMA_VERSION = "ims-deadlock/g6b-case-construction-schema/v3"
G6B_RETIRED_AUTHORITY_FINGERPRINT_SCHEMA_VERSION = (
    "ims-deadlock/g6b-retired-authority-fingerprint-schema/v2"
)
G6B_TARGET_CERTIFICATION_SCHEMA_VERSION = (
    "ims-deadlock/g6b-target-certification-schema/v1"
)
G6B_QUANTITATIVE_AUTHORIZATION_SCHEMA_VERSION = (
    "ims-deadlock/g6b-quantitative-authorization-schema/v1"
)

_DOCUMENTS = (
    "row_family_protocol.json",
    "identity_schema.json",
    "row_family_matrix.json",
    "reuse_matrix.json",
    "overlap_report_schema.json",
    "runtime_lock_schema.json",
    "review_state.json",
    "failure_ledger.json",
    "case_construction_schema.json",
    "retired_authority_fingerprint_schema.json",
    "target_certification_schema.json",
    "quantitative_authorization_schema.json",
)
_SCHEMA_VERSIONS = {
    "row_family_protocol.json": G6B_ROW_FAMILY_PROTOCOL_VERSION,
    "identity_schema.json": G6B_ROW_FAMILY_IDENTITY_VERSION,
    "row_family_matrix.json": G6B_ROW_FAMILY_MATRIX_VERSION,
    "reuse_matrix.json": G6B_ROW_FAMILY_REUSE_VERSION,
    "overlap_report_schema.json": G6B_ROW_FAMILY_OVERLAP_VERSION,
    "runtime_lock_schema.json": G6B_ROW_FAMILY_RUNTIME_LOCK_VERSION,
    "review_state.json": G6B_ROW_FAMILY_REVIEW_STATE_VERSION,
    "failure_ledger.json": G6B_ROW_FAMILY_FAILURE_LEDGER_VERSION,
    "case_construction_schema.json": G6B_CASE_CONSTRUCTION_SCHEMA_VERSION,
    "retired_authority_fingerprint_schema.json": (
        G6B_RETIRED_AUTHORITY_FINGERPRINT_SCHEMA_VERSION
    ),
    "target_certification_schema.json": G6B_TARGET_CERTIFICATION_SCHEMA_VERSION,
    "quantitative_authorization_schema.json": (
        G6B_QUANTITATIVE_AUTHORIZATION_SCHEMA_VERSION
    ),
}
_RELATIVE_ROOT = Path("cases/discovery/g6b/row_families/structural_discovery_v1")
_APPROVED_SOURCE_DESIGN = Path(
    "docs/superpowers/specs/2026-08-01-g6b-case-target-certification-design.md"
)
_APPROVED_SOURCE_DESIGN_SHA256 = (
    "b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6"
)
_EXPECTED_TYPED_CAPABILITIES: JsonObject = {
    "case_construction_authorized": False,
    "retired_authority_fingerprint_normalization_authorized": False,
    "target_certification_preflight_authorized": False,
    "quantitative_execution_authorized": False,
}
_EXPECTED_TYPED_CAPABILITIES_SHA256 = (
    "21ad3b3663fe1a693a7f64c19a91010c6eb1bc2ac3f3018b8c54de38997135fc"
)
_EXPECTED_CANONICALIZATION_CONTRACT: JsonObject = {
    "version": "ims-deadlock/g6b-canonical-json/v2",
    "duplicate_members": "reject_at_every_depth",
    "unicode_normalization": {
        "member_names": "require_nfc_reject_non_nfc",
        "string_values": "require_nfc_reject_non_nfc",
        "silent_normalization": "prohibited",
    },
    "object_key_order": "unicode_code_point",
    "array_order_policy": {
        "declared_array_order": "preserve",
        "schema_declared_set_like_arrays": "unique_and_already_sorted",
    },
    "utf8_serialization": {
        "encoding": "utf-8",
        "ensure_ascii": False,
        "sort_keys": True,
        "separators": [",", ":"],
        "allow_nan": False,
    },
    "numeric_policy": {
        "json_nan_infinity_negative_zero_float": "prohibited",
        "counts_and_integral_budgets": "json_integers",
        "non_integral_values": {
            "encoding": "canonical_decimal_string",
            "grammar": r"^-?(0|[1-9][0-9]*)(\.[0-9]*[1-9])?$",
            "negative_zero": "prohibited",
            "exponent": "prohibited",
        },
        "historical_json_numbers": (
            "parse_lexical_token_as_exact_decimal_not_binary_float"
        ),
    },
    "path_policy": {
        "committed_paths": "case_sensitive_repo_relative_posix",
        "drive_letter_leading_slash_backslash_empty_dot_dotdot": "prohibited",
        "symlink_dependent_resolution": "prohibited",
        "runtime_executables": (
            "logical_id_plus_byte_and_environment_hashes_not_absolute_path"
        ),
    },
    "timestamp_policy": {
        "timezone": "utc",
        "format": "YYYY-MM-DDTHH:MM:SSZ",
        "precision": "seconds",
    },
}
_EXPECTED_ESTIMAND_ID_SCOPE_CONTRACT: JsonObject = {
    "additional_allowed_paths": False,
    "allowed_predeclared_paths": [
        {
            "allowed_use": "predeclared_directional_hypothesis_identifier_only",
            "json_pointer_pattern": "/directional_hypotheses/*/estimand_id",
            "projection_role": "sealed_prediction_sha256",
        },
        {
            "allowed_use": "predeclared_metric_identifier_only",
            "json_pointer_pattern": "/metric_entries/*/estimand_id",
            "projection_role": "metric_schema_sha256",
        },
    ],
    "allowed_value_codes": [
        "g6b_estimand_theta_global_before_success_v1",
        "g6b_estimand_theta_local_before_success_v1",
        "g6b_estimand_theta_selected_bad_before_success_v1",
    ],
    "default_policy": "recursive_prohibition",
    "runtime_certificate_observation_or_result_use": "prohibited",
}
_EXPECTED_SELF_HASH_FINALIZATION_CONTRACT: JsonObject = {
    "version": "ims-deadlock/g6b-self-hash-finalization/v2",
    "placeholder_value": None,
    "replaced_field_count": 1,
    "omitted_field_allowed": False,
    "prepopulated_digest_allowed": False,
    "excluded_field_escape_hatch_allowed": False,
    "cross_record_reference_order": {
        "graph": "directed_acyclic_lifecycle_order",
        "record_may_reference": "already_finalized_upstream_records_only",
        "upstream_embeds_downstream_back_reference": "prohibited",
        "self_hash_field": "schema_fixed",
    },
    "digest_algorithm": "sha256",
    "digest_encoding": "lowercase_hexadecimal",
}
_EXPECTED_FINGERPRINT_PAYLOAD_SCHEMA_KEYS = {
    "projection_kind",
    "subject_type",
    "required_fields",
    "set_like_array_paths",
    "nested_field_contracts",
    "additional_properties",
    "prohibited_fields",
}
_EXPECTED_FINGERPRINT_PROJECTION_KINDS = {
    "case_content_sha256": "semantic_content",
    "state_snapshot_sha256": "semantic_content",
    "route_signature_sha256": "semantic_content",
    "parameter_tuple_sha256": "semantic_content",
    "random_stream_manifest_sha256": "random_process",
    "output_root_reservation_sha256": "provenance_containment",
    "sealed_prediction_sha256": "semantic_content",
    "metric_schema_sha256": "controlled_schema",
}
_EXPECTED_FINGERPRINT_SUBJECT_TYPES = {
    "case_content_sha256": "case_unit",
    "state_snapshot_sha256": "case_unit",
    "route_signature_sha256": "case_unit",
    "parameter_tuple_sha256": "case_unit",
    "random_stream_manifest_sha256": "method_observation",
    "output_root_reservation_sha256": "method_observation",
    "sealed_prediction_sha256": "case_unit",
    "metric_schema_sha256": "method_companion_group",
}
_EXPECTED_MATRIX_RAW_SHA256 = (
    "487d81aa79a7bca681db81f19a4d6bd315668c43b1c4538c47f01f099d8e205f"
)
_EXPECTED_IDENTITY_LEVELS = (
    "family_id",
    "case_unit_id",
    "method_observation_id",
    "method_companion_group_id",
)
_EXPECTED_FINGERPRINT_RECORD_KEYS = (
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
_EXPECTED_METHOD_ROLES = (
    "exact_companion",
    "des_companion",
    "schema_only_refusal",
    "review_only_placeholder",
)
_EXPECTED_NO_STOCHASTIC_METHOD_MANIFEST: JsonObject = {
    "allowed": True,
    "must_be_case_unit_specific": True,
    "shared_global_sentinel_prohibited": True,
    "proves_provenance_only": True,
    "proves_stochastic_independence": False,
}
_EXPECTED_REUSE_RELATION_IDS = (
    "exact_des_companion",
    "controlled_family_variant",
    "negative_control_pair",
    "method_companion_group_metric_reuse",
    "retired_authority_overlap",
)
_EXPECTED_REVIEW_STATES = (
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
_EXPECTED_CASE_STATES = (
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
_EXPECTED_METHOD_STATES = (
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
_EXPECTED_REFUSAL_CODES = (
    "batch_incomplete",
    "canonicalization_violation",
    "capability_call_violation",
    "capability_import_violation",
    "certificate_schema_violation",
    "command_scope_violation",
    "duplicate_lineage_miscount",
    "exact_des_target_mismatch",
    "failed_negative_control",
    "filesystem_scope_violation",
    "incomplete_stable_lts",
    "metric_reuse_unauthorized",
    "missing_hash",
    "missing_normalization_authorization",
    "missing_retired_authority",
    "non_almost_sure_absorption_domain",
    "outcome_leakage",
    "output_root_reuse_or_materialized",
    "overlap_hit",
    "policy_filter_drift",
    "prediction_semantic_reuse",
    "quantitative_scope_violation",
    "random_stream_disjointness_unproved",
    "random_stream_overlap",
    "rate_manifest_drift",
    "rename_or_cosmetic_shift_detected",
    "retired_authority_hash_mismatch",
    "retired_normalizer_error",
    "retired_projection_unreconstructable",
    "retry_stop_policy_violation",
    "runtime_identity_drift",
    "same_target_lock_stale",
    "sealed_input_drift",
    "selected_target_drift",
    "self_hash_mismatch",
    "semantic_identity_reuse",
    "semantic_lineage_ambiguous",
    "source_field_read_violation",
    "state_bound_truncation",
    "subject_id_contaminated_projection",
    "unauthorized_case_creation_attempt",
    "unauthorized_quantitative_execution_attempt",
    "unauthorized_retired_normalization_attempt",
    "unauthorized_target_certification_attempt",
    "unavailable_transition_branch",
    "unclassified_scientific_input",
    "unexpected_preflight_side_effect",
    "unverified_lts_provenance",
)
_EXPECTED_SCHEMA_REFUSAL_CODES = {
    "case_construction_schema.json": (
        "batch_incomplete",
        "canonicalization_violation",
        "ledger_append_interrupted",
        "missing_hash",
        "outcome_leakage",
        "output_root_reuse_or_materialized",
        "partial_bundle_terminal",
        "post_seal_ledger_mutation",
        "projection_file_missing",
        "runtime_identity_drift",
        "sealed_input_drift",
        "self_hash_mismatch",
        "source_identity_phase_violation",
        "subject_id_contaminated_projection",
        "unauthorized_case_creation_attempt",
        "unclassified_scientific_input",
        "unexpected_transient_path",
    ),
    "retired_authority_fingerprint_schema.json": (
        "batch_incomplete",
        "canonicalization_violation",
        "capability_call_violation",
        "capability_import_violation",
        "duplicate_lineage_miscount",
        "metric_reuse_unauthorized",
        "missing_hash",
        "missing_normalization_authorization",
        "missing_retired_authority",
        "outcome_leakage",
        "output_root_reuse_or_materialized",
        "overlap_hit",
        "prediction_semantic_reuse",
        "random_stream_disjointness_unproved",
        "random_stream_overlap",
        "rename_or_cosmetic_shift_detected",
        "retired_authority_hash_mismatch",
        "retired_normalizer_error",
        "retired_projection_unreconstructable",
        "runtime_identity_drift",
        "sealed_input_drift",
        "self_hash_mismatch",
        "semantic_identity_reuse",
        "semantic_lineage_ambiguous",
        "source_field_read_violation",
        "subject_id_contaminated_projection",
        "unauthorized_retired_normalization_attempt",
        "unclassified_scientific_input",
    ),
    "target_certification_schema.json": (
        "batch_incomplete",
        "canonicalization_violation",
        "capability_call_violation",
        "capability_import_violation",
        "certificate_schema_violation",
        "command_scope_violation",
        "filesystem_scope_violation",
        "incomplete_stable_lts",
        "missing_hash",
        "non_almost_sure_absorption_domain",
        "outcome_leakage",
        "policy_filter_drift",
        "rate_manifest_drift",
        "runtime_identity_drift",
        "sealed_input_drift",
        "selected_target_drift",
        "self_hash_mismatch",
        "state_bound_truncation",
        "unauthorized_target_certification_attempt",
        "unavailable_transition_branch",
        "unexpected_preflight_side_effect",
        "unverified_lts_provenance",
    ),
    "quantitative_authorization_schema.json": (
        "batch_incomplete",
        "canonicalization_violation",
        "exact_des_target_mismatch",
        "failed_negative_control",
        "missing_hash",
        "outcome_leakage",
        "output_root_reuse_or_materialized",
        "quantitative_scope_violation",
        "retry_stop_policy_violation",
        "runtime_identity_drift",
        "same_target_lock_stale",
        "sealed_input_drift",
        "self_hash_mismatch",
        "unauthorized_quantitative_execution_attempt",
    ),
}
_EXPECTED_SCHEMA_REFUSAL_CODES["overlap_report_schema.json"] = (
    _EXPECTED_SCHEMA_REFUSAL_CODES["retired_authority_fingerprint_schema.json"]
)
_EXPECTED_OVERLAP_SUBJECT_STATUSES = ("admitted", "refused", "pending")

_TOP_LEVEL_KEYS = {
    "row_family_protocol.json": {
        "schema_version",
        "study_role",
        "confirmation_use",
        "protocol_id",
        "adversarial_review_status",
        "bundle_role",
        "source_design",
        "source_design_sha256",
        "artifact_paths",
        "artifact_manifest_sha256",
        "canonicalization_contract",
        "self_hash_finalization_contract",
        "typed_capabilities",
        "typed_capabilities_sha256",
        "execution_boundary",
    },
    "identity_schema.json": {
        "schema_version",
        "study_role",
        "confirmation_use",
        "schema_role",
        "canonicalization_contract",
        "self_hash_finalization_contract",
        "estimand_id_scope_contract",
        "identity_levels",
        "canonical_dimensions",
        "fingerprint_record_keys",
        "fingerprint_subject_map",
        "fingerprint_payload_schemas",
        "dimension_dependence_contract",
        "projection_descriptors",
        "provenance_envelope_fields",
        "output_root_reservation_contract",
        "no_stochastic_method_manifest",
        "method_roles",
        "method_observations_are_independent_cases",
    },
    "row_family_matrix.json": {
        "schema_version",
        "study_role",
        "confirmation_use",
        "scientific_execution_authorized",
        "case_creation_authorized",
        "negative_control_families",
        "discovery_probes",
        "ontology_contract",
        "exact_des_pairing",
        "initial_scoring_state",
    },
    "reuse_matrix.json": {
        "schema_version",
        "study_role",
        "confirmation_use",
        "schema_role",
        "canonicalization_contract",
        "self_hash_finalization_contract",
        "subject_identity_rules",
        "controlled_metric_reuse_contract",
        "exact_des_pair_counting_contract",
        "relations",
    },
    "overlap_report_schema.json": {
        "schema_version",
        "study_role",
        "confirmation_use",
        "schema_role",
        "canonicalization_contract",
        "self_hash_finalization_contract",
        "retired_authorities",
        "typed_admission_contract",
        "per_case_overlap_required_fields",
        "per_method_overlap_required_fields",
        "per_companion_group_overlap_required_fields",
        "terminal_partition_contract",
        "semantic_lineage_audit_required_fields",
        "metric_schema_reuse_record_required_fields",
        "input_overlap_report_required_fields",
        "input_overlap_subject_status_values",
        "input_overlap_report_status_values",
        "recursive_prohibited_fields",
        "refusal_code_vocabulary_version",
        "refusal_reason_codes",
        "schema_only_overlap_report_cannot_authorize_execution",
    },
    "runtime_lock_schema.json": {
        "schema_version",
        "study_role",
        "confirmation_use",
        "schema_role",
        "canonicalization_contract",
        "self_hash_finalization_contract",
        "input_overlap_authority_lock",
        "target_certification_runtime_lock",
        "quantitative_runtime_lock",
        "runtime_lock_must_not_contain_downstream_authorization",
    },
    "review_state.json": {
        "schema_version",
        "study_role",
        "confirmation_use",
        "schema_role",
        "canonicalization_contract",
        "self_hash_finalization_contract",
        "current_state",
        "allowed_states_in_order",
        "case_state_values",
        "method_state_values",
        "adversarial_review_status",
        "forward_only",
        "aggregate_predicates",
        "current_capability_reference",
        "current_capability_sha256",
    },
    "failure_ledger.json": {
        "schema_version",
        "study_role",
        "confirmation_use",
        "schema_role",
        "canonicalization_contract",
        "self_hash_finalization_contract",
        "append_only",
        "entries",
        "empty_entries_meaning",
        "empty_entries_do_not_mean_no_historical_failures",
        "refusal_code_vocabulary_version",
        "required_future_reason_codes",
        "refusal_reason_code_groups",
    },
    "case_construction_schema.json": {
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
    },
    "retired_authority_fingerprint_schema.json": {
        "schema_version",
        "study_role",
        "confirmation_use",
        "schema_role",
        "canonicalization_contract",
        "self_hash_finalization_contract",
        "estimand_id_scope_contract",
        "retired_authority_ids",
        "expected_source_inventory",
        "authority_lock_record_required_fields",
        "authority_source_record_required_fields",
        "fingerprint_record_required_fields",
        "fingerprint_payload_schemas",
        "dimension_status_values",
        "comparison_status_values",
        "normalization_manifest_required_fields",
        "normalization_authorization_required_fields",
        "allowed_use_values",
        "allowed_json_fields_by_source",
        "input_overlap_authority_lock_required_fields",
        "source_worktree_identity_required_fields",
        "per_dimension_comparison_required_fields",
        "semantic_lineage_audit_required_fields",
        "metric_schema_reuse_record_required_fields",
        "input_overlap_report_required_fields",
        "input_overlap_subject_status_values",
        "input_overlap_report_status_values",
        "retired_subject_type_values",
        "retired_protocol_kind_by_case_id",
        "retired_subject_expansion_contract",
        "source_projection_map",
        "lineage_deduplication_contract",
        "typed_admission_contract",
        "recursive_prohibited_fields",
        "refusal_code_vocabulary_version",
        "refusal_reason_codes",
        "schema_does_not_authorize_normalization",
    },
    "target_certification_schema.json": {
        "schema_version",
        "study_role",
        "confirmation_use",
        "schema_role",
        "current_capability_reference",
        "prerequisite_bundle_states",
        "canonicalization_contract",
        "self_hash_finalization_contract",
        "preflight_runtime_lock_required_fields",
        "preflight_authorization_required_fields",
        "allowed_command_manifest_required_fields",
        "allowed_command_record_required_fields",
        "allowed_command_placeholder_codes",
        "allowed_environment_variable_names",
        "allowed_operations",
        "allowed_output_schema_ids",
        "allowed_file_roles",
        "file_role_to_schema_id",
        "file_role_cardinality_contract",
        "allowed_result_fields",
        "allowed_project_imports",
        "allowed_writer_symbols",
        "forbidden_imports",
        "forbidden_calls",
        "forbidden_result_fields",
        "nested_field_contracts",
        "recursive_prohibited_fields",
        "preflight_evidence_root_contract",
        "per_case_result_required_fields",
        "result_status_values",
        "batch_manifest_required_fields",
        "batch_status_values",
        "refusal_code_vocabulary_version",
        "refusal_reason_codes",
        "schema_does_not_authorize_preflight",
    },
    "quantitative_authorization_schema.json": {
        "schema_version",
        "study_role",
        "confirmation_use",
        "schema_role",
        "current_capability_reference",
        "prerequisite_bundle_states",
        "canonicalization_contract",
        "self_hash_finalization_contract",
        "same_target_lock_required_fields",
        "quantitative_runtime_lock_required_fields",
        "quantitative_authorization_required_fields",
        "authorized_scope_required_fields",
        "allowed_command_manifest_required_fields",
        "allowed_command_record_required_fields",
        "allowed_command_placeholder_codes",
        "allowed_environment_variable_names",
        "nested_field_contracts",
        "recursive_prohibited_fields",
        "allowed_method_roles",
        "wildcard_scope_allowed",
        "survivor_scope_claim_contract",
        "refusal_code_vocabulary_version",
        "refusal_reason_codes",
        "schema_does_not_authorize_quantitative_execution",
    },
}

_EXPECTED_CANONICAL_SHA256 = {
    "row_family_protocol.json": (
        "2a725f990feba8f35739200ce5b0299622d2e447602cc94e699758b5f6088e3f"
    ),
    "identity_schema.json": (
        "dd33178221ed6a0fdce9b6dd0260c492c011ad5f04e43ee6b0e75fedbeb31b3a"
    ),
    "row_family_matrix.json": (
        "435783028dd7a118bc160aeea54f3081be60ecef94b863e0b73978186cd17e4a"
    ),
    "reuse_matrix.json": (
        "dcd700cfc8b0ceb15448989cb42b879a00f2748f85a040005291a734fda53f7c"
    ),
    "overlap_report_schema.json": (
        "55d833d8772d3493c09f15d995973db87f22e197f9a9e42606affd7e6ff52db4"
    ),
    "runtime_lock_schema.json": (
        "1da275b64535b8ad22020c4f158fcb9355d20ea291eee28580299fb9f051da08"
    ),
    "review_state.json": (
        "358c69a23451778f94432bb020a8bd0a35e2d6e9e5fd084179fd24f23bbba4d8"
    ),
    "failure_ledger.json": (
        "34be766f1f8dd97037180547f9b2bde242787c941969771433bceda394dffb87"
    ),
    "case_construction_schema.json": (
        "bdc881151ae847a43171a5b656bf1bd4480ee7846c5c59730118f7b11d045335"
    ),
    "retired_authority_fingerprint_schema.json": (
        "456a66067b5703695948719dc7ccbdfa09d8c2d6eced1c9f544d387234ee8f78"
    ),
    "target_certification_schema.json": (
        "d090c6fb4621b7d9c78f18d133970eeb308eb6202023878297a394941a42515b"
    ),
    "quantitative_authorization_schema.json": (
        "e42b1089330206fcd46a2eac90d68abba80e10e13940c7a53186140dd403a624"
    ),
}

_LIVE_INSTANCE_OR_RESULT_KEYS = {
    "actual_overlap_result",
    "authorization_id",
    "authorized",
    "bundle_id",
    "case_construction_authorized",
    "case_creation_authorized",
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
    "retired_authority_fingerprint_normalization_authorized",
    "science_summary",
    "scientific_execution_authorized",
    "state_enumeration_result",
    "target_certification_preflight_authorized",
}

_ALLOWED_DECLARATIVE_LIVE_KEY_VALUES: dict[tuple[str, JsonPath], Any] = {
    (
        "row_family_protocol.json",
        ("typed_capabilities", "case_construction_authorized"),
    ): False,
    (
        "row_family_protocol.json",
        (
            "typed_capabilities",
            "retired_authority_fingerprint_normalization_authorized",
        ),
    ): False,
    (
        "row_family_protocol.json",
        ("typed_capabilities", "target_certification_preflight_authorized"),
    ): False,
    (
        "row_family_protocol.json",
        ("typed_capabilities", "quantitative_execution_authorized"),
    ): False,
    (
        "row_family_matrix.json",
        ("scientific_execution_authorized",),
    ): False,
    (
        "row_family_matrix.json",
        ("case_creation_authorized",),
    ): False,
    (
        "reuse_matrix.json",
        ("subject_identity_rules", "case_unit_id"),
    ): "one_scientific_case_subject",
    (
        "reuse_matrix.json",
        ("subject_identity_rules", "method_observation_id"),
    ): "distinct_method_subject_not_independent_case",
}


@dataclass(frozen=True)
class G6BRowFamilyValidation:
    valid: bool
    errors: tuple[str, ...]
    scientific_execution_authorized: bool
    case_creation_authorized: bool
    adversarial_review_status: str
    review_state: str
    bundle_hashes: dict[str, str]


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> JsonObject:
    result: JsonObject = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse_json_int(token: str) -> int:
    if token == "-0":
        raise ValueError("JSON negative zero is prohibited")
    return int(token)


def _reject_json_float(_token: str) -> NoReturn:
    raise ValueError("JSON floating-point values are prohibited")


def _reject_json_constant(token: str) -> NoReturn:
    raise ValueError(f"non-finite JSON constant prohibited: {token}")


def _validate_unicode_nfc(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if unicodedata.normalize("NFC", key) != key:
                raise ValueError(f"member name is not Unicode NFC at {child_path}")
            _validate_unicode_nfc(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_unicode_nfc(child, f"{path}[{index}]")
    elif isinstance(value, str) and unicodedata.normalize("NFC", value) != value:
        raise ValueError(f"string value is not Unicode NFC at {path}")


def _load_json_object(path: Path) -> JsonObject:
    try:
        loaded = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_int=_parse_json_int,
            parse_float=_reject_json_float,
            parse_constant=_reject_json_constant,
        )
        _validate_unicode_nfc(loaded)
    except (OSError, TypeError, ValueError) as exc:
        raise ValueError(str(exc)) from exc
    if not isinstance(loaded, dict):
        raise TypeError("root must be a JSON object")
    return loaded


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _repo_root_for(bundle_root: Path) -> Path | None:
    parts = _RELATIVE_ROOT.parts
    if tuple(bundle_root.parts[-len(parts) :]) != parts:
        return None
    return bundle_root.parents[len(parts) - 1]


def _expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _expect_exact_keys(
    document: JsonObject,
    expected: set[str],
    label: str,
    errors: list[str],
) -> None:
    missing = sorted(expected - set(document))
    extra = sorted(set(document) - expected)
    if missing:
        errors.append(f"{label}: missing keys: {missing}")
    if extra:
        errors.append(f"{label}: unexpected keys: {extra}")


def _expect_shared_contracts(
    name: str,
    document: JsonObject,
    errors: list[str],
) -> None:
    _expect(
        document.get("canonicalization_contract")
        == _EXPECTED_CANONICALIZATION_CONTRACT,
        f"{name}: canonicalization_contract must match the closed v2 contract",
        errors,
    )
    _expect(
        document.get("self_hash_finalization_contract")
        == _EXPECTED_SELF_HASH_FINALIZATION_CONTRACT,
        f"{name}: self_hash_finalization_contract must match the closed v2 contract",
        errors,
    )
    if name in {
        "identity_schema.json",
        "case_construction_schema.json",
        "retired_authority_fingerprint_schema.json",
    }:
        _expect(
            document.get("estimand_id_scope_contract")
            == _EXPECTED_ESTIMAND_ID_SCOPE_CONTRACT,
            f"{name}: estimand_id_scope_contract must match",
            errors,
        )


def _expect_fingerprint_payload_schemas(
    name: str,
    document: JsonObject,
    errors: list[str],
) -> None:
    payload_schemas = document.get("fingerprint_payload_schemas")
    if not isinstance(payload_schemas, dict):
        errors.append(f"{name}: fingerprint_payload_schemas must be an object")
        return
    _expect(
        tuple(payload_schemas) == tuple(_EXPECTED_FINGERPRINT_PROJECTION_KINDS),
        f"{name}: fingerprint_payload_schemas dimensions must match",
        errors,
    )
    for dimension, projection_kind in _EXPECTED_FINGERPRINT_PROJECTION_KINDS.items():
        entry = payload_schemas.get(dimension)
        if not isinstance(entry, dict):
            errors.append(
                f"{name}: fingerprint payload {dimension} must be a closed object"
            )
            continue
        _expect_exact_keys(
            entry,
            _EXPECTED_FINGERPRINT_PAYLOAD_SCHEMA_KEYS,
            f"{name}: fingerprint payload {dimension}",
            errors,
        )
        _expect(
            entry.get("projection_kind") == projection_kind,
            f"{name}: fingerprint payload {dimension} has wrong projection_kind",
            errors,
        )
        _expect(
            entry.get("subject_type") == _EXPECTED_FINGERPRINT_SUBJECT_TYPES[dimension],
            f"{name}: fingerprint payload {dimension} has wrong subject_type",
            errors,
        )
        _expect(
            entry.get("additional_properties") is False,
            f"{name}: fingerprint payload {dimension} must prohibit extra fields",
            errors,
        )
        set_like_paths = entry.get("set_like_array_paths")
        _expect(
            isinstance(set_like_paths, list)
            and set_like_paths == sorted(set(set_like_paths)),
            f"{name}: fingerprint payload {dimension} set-like paths must be an array",
            errors,
        )
        nested = entry.get("nested_field_contracts")
        _expect(
            isinstance(nested, dict) and bool(nested),
            f"{name}: fingerprint payload {dimension} nested contract must be nonempty",
            errors,
        )
        prohibited = entry.get("prohibited_fields")
        _expect(
            isinstance(prohibited, list)
            and bool(prohibited)
            and prohibited == sorted(set(prohibited)),
            f"{name}: fingerprint payload {dimension} prohibited fields "
            "must be nonempty, unique, and sorted",
            errors,
        )
        required = entry.get("required_fields")
        if dimension == "random_stream_manifest_sha256":
            valid_required = (
                isinstance(required, dict)
                and tuple(required) == ("stochastic", "exact")
                and all(
                    isinstance(fields, list) and bool(fields)
                    for fields in required.values()
                )
            )
        else:
            valid_required = isinstance(required, list) and bool(required)
        _expect(
            valid_required,
            f"{name}: fingerprint payload {dimension} required fields must match shape",
            errors,
        )


def _expect_refusal_contract(
    name: str,
    document: JsonObject,
    errors: list[str],
) -> None:
    expected = _EXPECTED_SCHEMA_REFUSAL_CODES.get(name)
    if expected is not None:
        _expect(
            document.get("refusal_reason_codes") == list(expected),
            f"{name}: refusal_reason_codes must match the exact gate union",
            errors,
        )
    if name in {
        "overlap_report_schema.json",
        "retired_authority_fingerprint_schema.json",
    }:
        _expect(
            document.get("input_overlap_subject_status_values")
            == list(_EXPECTED_OVERLAP_SUBJECT_STATUSES),
            f"{name}: input_overlap_subject_status_values must match",
            errors,
        )


def _expect_document(
    name: str,
    document: JsonObject,
    canonical_hash: str,
    errors: list[str],
) -> None:
    _expect_exact_keys(document, _TOP_LEVEL_KEYS[name], name, errors)
    _expect(
        document.get("schema_version") == _SCHEMA_VERSIONS[name],
        f"{name}: wrong schema_version",
        errors,
    )
    _expect(
        document.get("study_role") == "discovery_only",
        f"{name}: study_role must be discovery_only",
        errors,
    )
    _expect(
        document.get("confirmation_use") == "prohibited",
        f"{name}: confirmation_use must be prohibited",
        errors,
    )
    for legacy_flag in (
        "scientific_execution_authorized",
        "case_creation_authorized",
    ):
        if legacy_flag in document:
            _expect(
                document[legacy_flag] is False,
                f"{name}: {legacy_flag} must be false",
                errors,
            )
    if name != "row_family_matrix.json":
        _expect_shared_contracts(name, document, errors)
    _expect_refusal_contract(name, document, errors)
    if canonical_hash != _EXPECTED_CANONICAL_SHA256[name]:
        errors.append(f"{name}: document must match the canonical contract")


def _expect_protocol(
    document: JsonObject, hashes: dict[str, str], errors: list[str]
) -> None:
    expected_paths = [(_RELATIVE_ROOT / name).as_posix() for name in _DOCUMENTS[1:]]
    _expect(
        document.get("artifact_paths") == expected_paths,
        "row_family_protocol.json: artifact_paths must match exact twelve bundle",
        errors,
    )
    _expect(
        document.get("source_design") == _APPROVED_SOURCE_DESIGN.as_posix(),
        "row_family_protocol.json: source_design must match approved specification",
        errors,
    )
    _expect(
        document.get("source_design_sha256") == _APPROVED_SOURCE_DESIGN_SHA256,
        "row_family_protocol.json: source_design_sha256 must match",
        errors,
    )
    missing_artifact_hashes = [name for name in _DOCUMENTS[1:] if name not in hashes]
    if not missing_artifact_hashes:
        artifact_manifest = {
            (_RELATIVE_ROOT / name).as_posix(): hashes[name] for name in _DOCUMENTS[1:]
        }
        _expect(
            document.get("artifact_manifest_sha256")
            == _canonical_sha256(artifact_manifest),
            "row_family_protocol.json: artifact_manifest_sha256 must match",
            errors,
        )
    capabilities = document.get("typed_capabilities")
    _expect(
        capabilities == _EXPECTED_TYPED_CAPABILITIES,
        "row_family_protocol.json: typed_capabilities must remain all false",
        errors,
    )
    _expect(
        document.get("typed_capabilities_sha256")
        == _EXPECTED_TYPED_CAPABILITIES_SHA256,
        "row_family_protocol.json: typed_capabilities_sha256 must match",
        errors,
    )


def _expect_identity_schema(document: JsonObject, errors: list[str]) -> None:
    _expect(
        document.get("identity_levels") == list(_EXPECTED_IDENTITY_LEVELS),
        "identity_schema.json: identity_levels must match",
        errors,
    )
    fingerprint_keys = document.get("fingerprint_record_keys")
    _expect(
        fingerprint_keys == list(_EXPECTED_FINGERPRINT_RECORD_KEYS),
        "identity_schema.json: fingerprint_record_keys must match",
        errors,
    )
    _expect(
        document.get("method_roles") == list(_EXPECTED_METHOD_ROLES),
        "identity_schema.json: method_roles must match",
        errors,
    )
    _expect(
        document.get("no_stochastic_method_manifest")
        == _EXPECTED_NO_STOCHASTIC_METHOD_MANIFEST,
        "identity_schema.json: no_stochastic_method_manifest must match",
        errors,
    )
    _expect(
        document.get("method_observations_are_independent_cases") is False,
        "identity_schema.json: method_observations_are_independent_cases must be false",
        errors,
    )


def _expect_reuse_matrix(document: JsonObject, errors: list[str]) -> None:
    relations = document.get("relations")
    relation_ids = (
        [item.get("id") for item in relations if isinstance(item, dict)]
        if isinstance(relations, list)
        else []
    )
    _expect(
        relation_ids == list(_EXPECTED_REUSE_RELATION_IDS),
        "reuse_matrix.json: reuse relation ids must match",
        errors,
    )


def _expect_review_state(document: JsonObject, errors: list[str]) -> None:
    _expect(
        document.get("allowed_states_in_order") == list(_EXPECTED_REVIEW_STATES),
        "review_state.json: allowed_states_in_order must match",
        errors,
    )
    _expect(
        document.get("case_state_values") == list(_EXPECTED_CASE_STATES),
        "review_state.json: case_state_values must match",
        errors,
    )
    _expect(
        document.get("method_state_values") == list(_EXPECTED_METHOD_STATES),
        "review_state.json: method_state_values must match",
        errors,
    )
    _expect(
        document.get("current_state") == "ROW_FAMILY_BUNDLE_IMPLEMENTED",
        "review_state.json: current_state must remain ROW_FAMILY_BUNDLE_IMPLEMENTED",
        errors,
    )
    _expect(
        document.get("adversarial_review_status") == "PENDING",
        "review_state.json: adversarial_review_status must remain PENDING",
        errors,
    )
    _expect(
        document.get("forward_only") is True,
        "review_state.json: forward_only must be true",
        errors,
    )
    _expect(
        document.get("current_capability_reference")
        == "row_family_protocol.json#/typed_capabilities",
        "review_state.json: current_capability_reference must match",
        errors,
    )
    _expect(
        document.get("current_capability_sha256")
        == _EXPECTED_TYPED_CAPABILITIES_SHA256,
        "review_state.json: current_capability_sha256 must match",
        errors,
    )


def _expect_failure_ledger(document: JsonObject, errors: list[str]) -> None:
    _expect(
        document.get("append_only") is True,
        "failure_ledger.json: append_only must be true",
        errors,
    )
    _expect(
        document.get("entries") == [],
        "failure_ledger.json: entries must remain empty",
        errors,
    )
    _expect(
        document.get("empty_entries_meaning")
        == "no authorized current row-family attempt has occurred",
        "failure_ledger.json: empty_entries_meaning must match",
        errors,
    )
    _expect(
        document.get("empty_entries_do_not_mean_no_historical_failures") is True,
        "failure_ledger.json: empty_entries_do_not_mean_no_historical_failures "
        "must be true",
        errors,
    )
    _expect(
        document.get("refusal_code_vocabulary_version")
        == "ims-deadlock/g6b-refusal-codes/v1",
        "failure_ledger.json: refusal_code_vocabulary_version must match",
        errors,
    )
    _expect(
        document.get("required_future_reason_codes") == list(_EXPECTED_REFUSAL_CODES),
        "failure_ledger.json: required_future_reason_codes must match",
        errors,
    )


def _reject_recursive_live_keys(
    name: str,
    document: JsonObject,
    errors: list[str],
) -> None:
    violations: set[str] = set()

    def visit(value: Any, path: JsonPath = ()) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = (*path, key)
                if key in _LIVE_INSTANCE_OR_RESULT_KEYS:
                    allowed = (name, child_path)
                    frozen_matrix_case_boundary = (
                        name == "row_family_matrix.json"
                        and key == "case_creation_authorized"
                        and child is False
                        and len(child_path) == 3
                        and child_path[0]
                        in {"negative_control_families", "discovery_probes"}
                        and isinstance(child_path[1], int)
                    )
                    if not frozen_matrix_case_boundary and (
                        allowed not in _ALLOWED_DECLARATIVE_LIVE_KEY_VALUES
                        or child != _ALLOWED_DECLARATIVE_LIVE_KEY_VALUES[allowed]
                    ):
                        violations.add(key)
                visit(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, (*path, index))

    visit(document)
    for key in sorted(violations):
        errors.append(f"{name}: prohibited outcome key present: {key}")


def _validate_source_design(repo_root: Path, errors: list[str]) -> None:
    source_design = repo_root / _APPROVED_SOURCE_DESIGN
    if not source_design.is_file():
        errors.append("source design path is missing")
        return
    if hashlib.sha256(source_design.read_bytes()).hexdigest() != (
        _APPROVED_SOURCE_DESIGN_SHA256
    ):
        errors.append("source design SHA-256 is not the approved digest")


def _reject_later_instance_roots(repo_root: Path, errors: list[str]) -> None:
    later_roots = (
        repo_root / _RELATIVE_ROOT / "governance",
        repo_root / _RELATIVE_ROOT / "case_units",
        repo_root / "evidence/g6b/target_certification",
        repo_root / "artifacts/g6b/quantitative",
    )
    for path in later_roots:
        if path.exists():
            errors.append(
                "schema-only migration requires later instance root absent: "
                f"{path.relative_to(repo_root).as_posix()}"
            )


def validate_g6b_row_family_bundle(root: Path) -> G6BRowFamilyValidation:
    bundle_root = root.resolve()
    errors: list[str] = []
    documents: dict[str, JsonObject] = {}
    hashes: dict[str, str] = {}
    actual = sorted(path.name for path in bundle_root.glob("*.json") if path.is_file())
    missing = sorted(set(_DOCUMENTS) - set(actual))
    unexpected = sorted(set(actual) - set(_DOCUMENTS))
    if missing:
        errors.append(f"missing JSON documents: {missing}")
    if unexpected:
        errors.append(f"unexpected JSON documents: {unexpected}")

    for name in _DOCUMENTS:
        if name in missing:
            continue
        path = bundle_root / name
        try:
            document = _load_json_object(path)
        except (TypeError, ValueError) as exc:
            errors.append(f"{name}: {exc}")
            continue
        canonical_hash = _canonical_sha256(document)
        documents[name] = document
        hashes[name] = canonical_hash
        _expect_document(name, document, canonical_hash, errors)
        _reject_recursive_live_keys(name, document, errors)
        if (
            name == "row_family_matrix.json"
            and hashlib.sha256(path.read_bytes()).hexdigest()
            != _EXPECTED_MATRIX_RAW_SHA256
        ):
            errors.append("row_family_matrix.json: document must match byte-for-byte")

    repo_root = _repo_root_for(bundle_root)
    if repo_root is None:
        errors.append(
            "bundle root must be <repo>/cases/discovery/g6b/"
            "row_families/structural_discovery_v1"
        )
    else:
        _validate_source_design(repo_root, errors)
        _reject_later_instance_roots(repo_root, errors)

    protocol = documents.get("row_family_protocol.json", {})
    review = documents.get("review_state.json", {})
    if protocol:
        _expect_protocol(protocol, hashes, errors)
    identity = documents.get("identity_schema.json")
    if identity:
        _expect_identity_schema(identity, errors)
    payload_documents = (
        "identity_schema.json",
        "case_construction_schema.json",
        "retired_authority_fingerprint_schema.json",
    )
    for name in payload_documents:
        payload_document = documents.get(name)
        if payload_document:
            _expect_fingerprint_payload_schemas(name, payload_document, errors)
    if all(name in documents for name in payload_documents):
        identity_payloads = documents["identity_schema.json"].get(
            "fingerprint_payload_schemas"
        )
        identity_estimand_scope = documents["identity_schema.json"].get(
            "estimand_id_scope_contract"
        )
        for name in payload_documents[1:]:
            _expect(
                documents[name].get("fingerprint_payload_schemas") == identity_payloads,
                f"{name}: fingerprint_payload_schemas must match identity schema",
                errors,
            )
            _expect(
                documents[name].get("estimand_id_scope_contract")
                == identity_estimand_scope,
                f"{name}: estimand_id_scope_contract must match identity schema",
                errors,
            )
    reuse = documents.get("reuse_matrix.json")
    if reuse:
        _expect_reuse_matrix(reuse, errors)
    if review:
        _expect_review_state(review, errors)
    ledger = documents.get("failure_ledger.json")
    if ledger:
        _expect_failure_ledger(ledger, errors)

    valid = not errors
    return G6BRowFamilyValidation(
        valid=valid,
        errors=tuple(errors),
        scientific_execution_authorized=False,
        case_creation_authorized=False,
        adversarial_review_status=(
            str(protocol.get("adversarial_review_status", "")) if valid else "INVALID"
        ),
        review_state=(str(review.get("current_state", "")) if valid else "INVALID"),
        bundle_hashes=hashes,
    )
