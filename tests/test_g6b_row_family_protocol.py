import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any, TypedDict

import pytest

from ims_deadlock import g6b_case_materializer as case_materializer
from ims_deadlock.g6b_canonical_json import canonical_sha256_v2
from ims_deadlock.g6b_row_family_protocol import (
    validate_g6b_row_family_bundle,
)

PathPart = str | int


class _SpecRequirementStatus(TypedDict):
    schema_tranche: str
    runtime_capability: str


class _SpecRequirementEntry(TypedDict, total=False):
    test_id: str
    owner: str
    task: str
    aspect: str
    labels: tuple[str, ...]


_REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE = Path("cases/discovery/g6b/row_families/structural_discovery_v1")
_TASK5_SCHEMA_CODE_SUBJECT_COMMIT = "9ef6fcec9e410b2ab7afc4144df8b948a238d95f"
_TASK6_SCOPE_SUBJECT_COMMIT = "42856b991059d6f800eb0244fa7847187da3bccd"
_TASK6_DECLARED_CHANGED_PATHS = {
    "PROJECT_HANDOFF.md",
    "docs/ROADMAP.md",
    "docs/cases/CASE_CHANGE_LEDGER.md",
    "docs/verification/G6_B_CASE_TARGET_SCHEMA_V2_REVIEW.md",
    "tests/test_g6b_protocol.py",
    "tests/test_g6b_row_family_protocol.py",
}
_TASK7_REPAIR_DECLARED_CHANGED_PATHS = {
    "docs/verification/G6_B_AUTHORIZATION_GATE_REMEDIATION_REVIEW.md",
    "src/ims_deadlock/g6b_schema_contracts.py",
    "tests/test_g6b_schema_contracts.py",
    "tests/test_g6b_row_family_protocol.py",
}
_CASE_CONSTRUCTION_PLAN_DECLARED_CHANGED_PATHS = {
    "docs/superpowers/plans/2026-08-02-g6b-case-construction.md",
    "docs/verification/G6_B_CASE_CONSTRUCTION_PLAN_REVIEW.md",
}
_TASK1_ESTIMAND_SCOPE_CORRIGENDUM_DECLARED_CHANGED_PATHS = {
    "cases/discovery/g6b/row_families/structural_discovery_v1/"
    "case_construction_schema.json",
    "cases/discovery/g6b/row_families/structural_discovery_v1/identity_schema.json",
    "cases/discovery/g6b/row_families/structural_discovery_v1/"
    "retired_authority_fingerprint_schema.json",
    "docs/superpowers/specs/"
    "2026-08-02-g6b-case-construction-estimand-scope-corrigendum.md",
    "src/ims_deadlock/g6b_row_family_protocol.py",
    "src/ims_deadlock/g6b_schema_contracts.py",
    "tests/test_g6b_row_family_protocol.py",
    "tests/test_g6b_schema_contracts.py",
}
_TASK1_REVIEW_PUBLICATION_DECLARED_CHANGED_PATHS = {
    "PROJECT_HANDOFF.md",
    "docs/ROADMAP.md",
    "docs/verification/G6_B_CASE_CONSTRUCTION_ESTIMAND_SCOPE_CORRIGENDUM_REVIEW.md",
}
_CASE_CONSTRUCTION_V2_GOVERNANCE_DECLARED_CHANGED_PATHS = {
    "docs/superpowers/specs/"
    "2026-08-02-g6b-case-construction-materialization-contract-corrigendum.md",
    "docs/superpowers/plans/2026-08-02-g6b-case-construction-v2.md",
    "docs/verification/G6_B_CASE_CONSTRUCTION_V2_PLAN_REVIEW.md",
}
_R1_CASE_CONSTRUCTION_SCHEMA_V3_DECLARED_CHANGED_PATHS = {
    "cases/discovery/g6b/row_families/structural_discovery_v1/"
    "case_construction_schema.json",
    "cases/discovery/g6b/row_families/structural_discovery_v1/row_family_protocol.json",
    "src/ims_deadlock/g6b_row_family_protocol.py",
    "src/ims_deadlock/g6b_schema_contracts.py",
    "tests/test_g6b_row_family_protocol.py",
    "tests/test_g6b_schema_contracts.py",
}
_R4_CASE_CONSTRUCTION_C2_SOURCE_IDENTITY_PATHS = {
    "cases/discovery/g6b/row_families/structural_discovery_v1/"
    "case_construction_schema.json",
    "cases/discovery/g6b/row_families/structural_discovery_v1/row_family_protocol.json",
    "docs/verification/G6_B_CASE_CONSTRUCTION_TASK2_SOURCE_REVIEW.md",
    "src/ims_deadlock/g6b_case_materializer.py",
    "src/ims_deadlock/g6b_row_family_protocol.py",
    "src/ims_deadlock/g6b_schema_contracts.py",
    "tests/test_g6b_case_materializer.py",
    "tests/test_g6b_row_family_protocol.py",
    "tests/test_g6b_schema_contracts.py",
}
_R7_CASE_CONSTRUCTION_PUBLICATION_DECLARED_CHANGED_PATHS = {
    "docs/verification/G6_B_CASE_CONSTRUCTION_REVIEW_V2.md",
}
_RETIRED_NORMALIZATION_PLAN_PUBLICATION_DECLARED_CHANGED_PATHS = {
    "docs/superpowers/plans/"
    "2026-08-05-g6b-retired-authority-fingerprint-normalization.md",
    "docs/superpowers/specs/"
    "2026-08-05-g6b-retired-normalization-capability-corrigendum.md",
    "docs/verification/G6_B_RETIRED_AUTHORITY_NORMALIZATION_PLAN_REVIEW.md",
}
_MATERIALIZATION_WORDING_ERRATUM_PUBLICATION_DECLARED_CHANGED_PATHS = {
    "docs/superpowers/specs/"
    "2026-08-05-g6b-case-construction-materialization-contract-wording-erratum.md",
    "docs/verification/G6_B_MATERIALIZATION_PROJECTION_SCOPE_WORDING_ERRATUM_REVIEW.md",
}
_FINAL_SCHEMA_REVIEW_DECLARED_CHANGED_PATHS = (
    _TASK6_DECLARED_CHANGED_PATHS
    | _TASK7_REPAIR_DECLARED_CHANGED_PATHS
    | _CASE_CONSTRUCTION_PLAN_DECLARED_CHANGED_PATHS
    | _TASK1_ESTIMAND_SCOPE_CORRIGENDUM_DECLARED_CHANGED_PATHS
    | _TASK1_REVIEW_PUBLICATION_DECLARED_CHANGED_PATHS
    | _CASE_CONSTRUCTION_V2_GOVERNANCE_DECLARED_CHANGED_PATHS
    | _R1_CASE_CONSTRUCTION_SCHEMA_V3_DECLARED_CHANGED_PATHS
    | _R4_CASE_CONSTRUCTION_C2_SOURCE_IDENTITY_PATHS
    | _R7_CASE_CONSTRUCTION_PUBLICATION_DECLARED_CHANGED_PATHS
    | _RETIRED_NORMALIZATION_PLAN_PUBLICATION_DECLARED_CHANGED_PATHS
    | _MATERIALIZATION_WORDING_ERRATUM_PUBLICATION_DECLARED_CHANGED_PATHS
)
_TASK6_FORBIDDEN_EXACT_PATHS = {
    "docs/superpowers/specs/2026-08-01-g6b-case-target-certification-design.md": (
        "approved_specification"
    ),
}
_TASK6_FORBIDDEN_PATH_PREFIXES = (
    ("cases/confirmation/g4/", "retired_g4_evidence"),
    ("evidence/g5/", "retired_g5_evidence"),
    ("evidence/g6/", "retired_g6r_evidence"),
    ("evidence/g6b/", "target_certification_evidence"),
    ("artifacts/", "scientific_artifact_root"),
    (
        "cases/discovery/g6b/row_families/structural_discovery_v1/governance/",
        "case_governance_instance_root",
    ),
    (
        "cases/discovery/g6b/row_families/structural_discovery_v1/case_units/",
        "case_instance_root",
    ),
)
_R5_CASE_CONSTRUCTION_ARTIFACT_PATHS = frozenset(
    case_materializer._authorized_output_paths()
)
_TASK6_BENIGN_IGNORED_ROOT_PREFIXES = (
    ".mypy_cache/",
    ".pytest_cache/",
    ".ruff_cache/",
)
_NAMES = (
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
SCHEMA_FILES = {
    "row_family_protocol.json": "ims-deadlock/g6b-row-family-protocol/v2",
    "identity_schema.json": "ims-deadlock/g6b-row-family-identity/v3",
    "row_family_matrix.json": "ims-deadlock/g6b-row-family-matrix/v1",
    "reuse_matrix.json": "ims-deadlock/g6b-row-family-reuse/v2",
    "overlap_report_schema.json": "ims-deadlock/g6b-row-family-overlap-schema/v2",
    "runtime_lock_schema.json": "ims-deadlock/g6b-row-family-runtime-lock-schema/v2",
    "review_state.json": "ims-deadlock/g6b-row-family-review-state/v2",
    "failure_ledger.json": "ims-deadlock/g6b-row-family-failure-ledger/v2",
    "case_construction_schema.json": "ims-deadlock/g6b-case-construction-schema/v3",
    "retired_authority_fingerprint_schema.json": (
        "ims-deadlock/g6b-retired-authority-fingerprint-schema/v2"
    ),
    "target_certification_schema.json": (
        "ims-deadlock/g6b-target-certification-schema/v1"
    ),
    "quantitative_authorization_schema.json": (
        "ims-deadlock/g6b-quantitative-authorization-schema/v1"
    ),
}
EXPECTED_DOCUMENTS = _NAMES
NEW_SCHEMA_DOCUMENTS = (
    "case_construction_schema.json",
    "retired_authority_fingerprint_schema.json",
    "target_certification_schema.json",
    "quantitative_authorization_schema.json",
)
EXISTING_SCHEMA_FILES = {
    name: version
    for name, version in SCHEMA_FILES.items()
    if name not in NEW_SCHEMA_DOCUMENTS
}
APPROVED_SOURCE_DESIGN = (
    "docs/superpowers/specs/2026-08-01-g6b-case-target-certification-design.md"
)
APPROVED_SOURCE_DESIGN_SHA256 = (
    "b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6"
)
EXPECTED_TYPED_CAPABILITIES = {
    "case_construction_authorized": False,
    "retired_authority_fingerprint_normalization_authorized": False,
    "target_certification_preflight_authorized": False,
    "quantitative_execution_authorized": False,
}
EXPECTED_TYPED_CAPABILITIES_SHA256 = hashlib.sha256(
    json.dumps(
        EXPECTED_TYPED_CAPABILITIES,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
).hexdigest()
EXPECTED_CANONICALIZATION_CONTRACT = {
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
EXPECTED_SELF_HASH_FINALIZATION_CONTRACT = {
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
EXPECTED_FINGERPRINT_PAYLOAD_SCHEMA_KEYS = (
    "projection_kind",
    "subject_type",
    "required_fields",
    "set_like_array_paths",
    "nested_field_contracts",
    "additional_properties",
    "prohibited_fields",
)
EXPECTED_FINGERPRINT_PROJECTION_KINDS = {
    "case_content_sha256": "semantic_content",
    "state_snapshot_sha256": "semantic_content",
    "route_signature_sha256": "semantic_content",
    "parameter_tuple_sha256": "semantic_content",
    "random_stream_manifest_sha256": "random_process",
    "output_root_reservation_sha256": "provenance_containment",
    "sealed_prediction_sha256": "semantic_content",
    "metric_schema_sha256": "controlled_schema",
}
EXPECTED_FINGERPRINT_SUBJECT_TYPES = {
    "case_content_sha256": "case_unit",
    "state_snapshot_sha256": "case_unit",
    "route_signature_sha256": "case_unit",
    "parameter_tuple_sha256": "case_unit",
    "random_stream_manifest_sha256": "method_observation",
    "output_root_reservation_sha256": "method_observation",
    "sealed_prediction_sha256": "case_unit",
    "metric_schema_sha256": "method_companion_group",
}
EXPECTED_FINGERPRINT_RECORD_KEYS = (
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
EXPECTED_REUSE_RELATION_IDS = (
    "exact_des_companion",
    "controlled_family_variant",
    "negative_control_pair",
    "method_companion_group_metric_reuse",
    "retired_authority_overlap",
)
_TASK5_MATRIX_ERROR = "row_family_matrix.json: document must match"
_LEGACY_GLOBAL_AUTHORIZATION_FIELDS = (
    "scientific_execution_authorized",
    "case_creation_authorized",
)
_REQUIRED_FUTURE_REASON_CODES = (
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
EXPECTED_SCHEMA_REFUSAL_CODES = {
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
EXPECTED_SCHEMA_REFUSAL_CODES["overlap_report_schema.json"] = (
    EXPECTED_SCHEMA_REFUSAL_CODES["retired_authority_fingerprint_schema.json"]
)
EXPECTED_OVERLAP_SUBJECT_STATUSES = ("admitted", "refused", "pending")
_PROHIBITED_OUTCOME_KEYS = (
    "observed_result",
    "exact_output",
    "des_output",
    "state_enumeration_result",
    "metric_value",
    "actual_overlap_result",
    "current_runtime_lock",
)
TASK4_RECURSIVE_PROHIBITED_FIELDS = (
    "authorized",
    "authorization_id",
    "bundle_id",
    "case_unit_id",
    "method_observation_id",
    *_PROHIBITED_OUTCOME_KEYS,
)
CHANGED_SCHEMA_DOCUMENTS = tuple(
    name for name in _NAMES if name != "row_family_matrix.json"
)
EXPECTED_TOP_LEVEL_KEYS = {
    "row_family_protocol.json": (
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
    ),
    "identity_schema.json": (
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
    ),
    "reuse_matrix.json": (
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
    ),
    "overlap_report_schema.json": (
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
    ),
    "runtime_lock_schema.json": (
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
    ),
    "review_state.json": (
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
    ),
    "failure_ledger.json": (
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
    ),
    "case_construction_schema.json": (
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
    ),
    "retired_authority_fingerprint_schema.json": (
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
    ),
    "target_certification_schema.json": (
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
    ),
    "quantitative_authorization_schema.json": (
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
    ),
}
REORDER_SENSITIVE_FIELDS: dict[str, tuple[PathPart, ...]] = {
    "row_family_protocol.json": ("artifact_paths",),
    "identity_schema.json": ("canonical_dimensions",),
    "reuse_matrix.json": ("relations",),
    "overlap_report_schema.json": ("retired_authorities",),
    "runtime_lock_schema.json": (),
    "review_state.json": ("allowed_states_in_order",),
    "failure_ledger.json": ("required_future_reason_codes",),
    "case_construction_schema.json": ("allowed_input_modes",),
    "retired_authority_fingerprint_schema.json": ("retired_authority_ids",),
    "target_certification_schema.json": ("allowed_operations",),
    "quantitative_authorization_schema.json": ("allowed_method_roles",),
}
WRONG_NESTED_FIELD_PATHS: dict[str, tuple[PathPart, ...]] = {
    "row_family_protocol.json": ("execution_boundary", "case_creation"),
    "identity_schema.json": ("no_stochastic_method_manifest", "allowed"),
    "reuse_matrix.json": ("relations", 0),
    "overlap_report_schema.json": ("typed_admission_contract",),
    "runtime_lock_schema.json": ("target_certification_runtime_lock",),
    "review_state.json": ("aggregate_predicates",),
    "failure_ledger.json": ("refusal_reason_code_groups",),
    "case_construction_schema.json": ("nested_field_contracts",),
    "retired_authority_fingerprint_schema.json": ("source_projection_map",),
    "target_certification_schema.json": ("nested_field_contracts",),
    "quantitative_authorization_schema.json": ("nested_field_contracts",),
}
LIVE_INJECTION_PARENT_PATHS: dict[str, tuple[PathPart, ...]] = {
    "row_family_protocol.json": ("execution_boundary",),
    "identity_schema.json": ("no_stochastic_method_manifest",),
    "reuse_matrix.json": ("relations", 0),
    "overlap_report_schema.json": ("typed_admission_contract",),
    "runtime_lock_schema.json": ("target_certification_runtime_lock",),
    "review_state.json": ("aggregate_predicates",),
    "failure_ledger.json": ("refusal_reason_code_groups",),
    "case_construction_schema.json": ("nested_field_contracts",),
    "retired_authority_fingerprint_schema.json": ("source_projection_map",),
    "target_certification_schema.json": ("nested_field_contracts",),
    "quantitative_authorization_schema.json": ("nested_field_contracts",),
}
EXPECTED_ESTIMAND_ID_SCOPE_CONTRACT = {
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


def _probe_nested_falsifier_cases() -> Iterable[Any]:
    matrix = _matrix()
    for probe_index, probe in enumerate(matrix["discovery_probes"]):
        for operation in ("add", "reorder", "duplicate", "semantic"):
            yield pytest.param(
                probe_index,
                operation,
                id=f"probe_{probe['role']}_falsifiers_{operation}",
            )


def _control_expected_object_key_cases() -> Iterable[Any]:
    matrix = _matrix()
    for control_index, control in enumerate(matrix["negative_control_families"]):
        control_id = control["required_negative_control_id"]
        for key in ("classification", "refusal"):
            for operation in ("remove_key", "add_key"):
                yield pytest.param(
                    control_index,
                    key,
                    operation,
                    id=f"control_{control_id}_expected_object_{key}_{operation}",
                )


def _path_get(document: dict[str, Any], path: tuple[PathPart, ...]) -> Any:
    target: Any = document
    for part in path:
        if isinstance(part, int):
            assert isinstance(target, list)
            target = target[part]
        else:
            assert isinstance(target, dict)
            target = target[part]
    return target


def _path_set(document: dict[str, Any], path: tuple[PathPart, ...], value: Any) -> None:
    target: Any = document
    for part in path[:-1]:
        if isinstance(part, int):
            assert isinstance(target, list)
            target = target[part]
        else:
            assert isinstance(target, dict)
            target = target[part]
    final = path[-1]
    if isinstance(final, int):
        assert isinstance(target, list)
        target[final] = value
    else:
        assert isinstance(target, dict)
        target[final] = value


def _path_pop(document: dict[str, Any], path: tuple[PathPart, ...]) -> None:
    target: Any = document
    for part in path[:-1]:
        if isinstance(part, int):
            assert isinstance(target, list)
            target = target[part]
        else:
            assert isinstance(target, dict)
            target = target[part]
    final = path[-1]
    if isinstance(final, int):
        assert isinstance(target, list)
        target.pop(final)
    else:
        assert isinstance(target, dict)
        target.pop(final)


def _reuse_relation_nested_list_cases() -> Iterable[Any]:
    reuse = _load(BUNDLE, "reuse_matrix.json")
    relations = reuse["relations"]
    assert isinstance(relations, list)
    for relation_index, relation in enumerate(relations):
        assert isinstance(relation, dict)
        relation_id = relation["id"]
        fields = (
            "allowed_shared_dimensions",
            "required_distinct_fields",
            "required_fields",
        )
        for field in fields:
            if field not in relation:
                continue
            value = relation[field]
            assert isinstance(value, list)
            operations = (
                ("add",)
                if not value
                else (
                    ("remove", "add", "reorder", "duplicate", "semantic")
                    if len(value) >= 2
                    else ("remove", "add", "duplicate", "semantic")
                )
            )
            for operation in operations:
                yield pytest.param(
                    relation_index,
                    field,
                    operation,
                    id=f"reuse_{relation_id}_{field}_{operation}",
                )


def _nested_scientific_list_cases() -> Iterable[Any]:
    list_cases: tuple[tuple[str, tuple[PathPart, ...], str], ...] = (
        (
            "row_family_protocol.json",
            ("artifact_paths",),
            "row_family_protocol.json: document must match",
        ),
        (
            "identity_schema.json",
            ("identity_levels",),
            "identity_schema.json: identity_levels must match",
        ),
        (
            "identity_schema.json",
            ("canonical_dimensions",),
            "identity_schema.json: document must match",
        ),
        (
            "identity_schema.json",
            ("fingerprint_record_keys",),
            "identity_schema.json: fingerprint_record_keys must match",
        ),
        (
            "identity_schema.json",
            ("method_roles",),
            "identity_schema.json: method_roles must match",
        ),
        ("row_family_matrix.json", ("negative_control_families",), _TASK5_MATRIX_ERROR),
        ("row_family_matrix.json", ("discovery_probes",), _TASK5_MATRIX_ERROR),
        (
            "row_family_matrix.json",
            ("discovery_probes", 0, "falsifiers"),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("discovery_probes", 1, "falsifiers"),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("discovery_probes", 2, "falsifiers"),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("ontology_contract", "D_local_admission_routes"),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("exact_des_pairing", "same_selected_bad_labels"),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("initial_scoring_state", "metric_observations"),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "reuse_matrix.json",
            ("relations",),
            "reuse_matrix.json: reuse relation ids must match",
        ),
        (
            "reuse_matrix.json",
            ("relations", 0, "allowed_shared_dimensions"),
            "reuse_matrix.json: document must match",
        ),
        (
            "reuse_matrix.json",
            ("relations", 0, "required_distinct_fields"),
            "reuse_matrix.json: document must match",
        ),
        (
            "reuse_matrix.json",
            ("relations", 1, "allowed_shared_dimensions"),
            "reuse_matrix.json: document must match",
        ),
        (
            "reuse_matrix.json",
            ("relations", 1, "required_fields"),
            "reuse_matrix.json: document must match",
        ),
        (
            "reuse_matrix.json",
            ("relations", 2, "allowed_shared_dimensions"),
            "reuse_matrix.json: document must match",
        ),
        (
            "reuse_matrix.json",
            ("relations", 2, "required_fields"),
            "reuse_matrix.json: document must match",
        ),
        (
            "reuse_matrix.json",
            ("relations", 3, "allowed_shared_dimensions"),
            "reuse_matrix.json: document must match",
        ),
        (
            "reuse_matrix.json",
            ("relations", 3, "required_fields"),
            "reuse_matrix.json: document must match",
        ),
        (
            "reuse_matrix.json",
            ("relations", 4, "allowed_shared_dimensions"),
            "reuse_matrix.json: document must match",
        ),
        (
            "reuse_matrix.json",
            ("relations", 4, "required_fields"),
            "reuse_matrix.json: document must match",
        ),
        (
            "overlap_report_schema.json",
            ("retired_authorities",),
            "overlap_report_schema.json: document must match",
        ),
        (
            "review_state.json",
            ("allowed_states_in_order",),
            "review_state.json: allowed_states_in_order must match",
        ),
        (
            "failure_ledger.json",
            ("entries",),
            "failure_ledger.json: entries must remain empty",
        ),
        (
            "failure_ledger.json",
            ("required_future_reason_codes",),
            "failure_ledger.json: required_future_reason_codes must match",
        ),
    )
    for name, path, expected_error in list_cases:
        value = _path_get(_load(BUNDLE, name), path)
        assert isinstance(value, list)
        operations = (
            ("add",)
            if not value
            else (
                ("remove", "add", "reorder", "duplicate", "semantic")
                if len(value) >= 2
                else ("remove", "add", "duplicate", "semantic")
            )
        )
        case_id = "_".join(str(item) for item in path).replace("[", "").replace("]", "")
        for operation in operations:
            yield pytest.param(
                name,
                path,
                expected_error,
                operation,
                id=f"{name}_{case_id}_{operation}",
            )


def _nested_scientific_object_cases() -> Iterable[Any]:
    object_cases: tuple[tuple[str, tuple[PathPart, ...], str], ...] = (
        (
            "row_family_protocol.json",
            ("execution_boundary",),
            "row_family_protocol.json: document must match",
        ),
        (
            "identity_schema.json",
            ("no_stochastic_method_manifest",),
            "identity_schema.json: no_stochastic_method_manifest must match",
        ),
        (
            "row_family_matrix.json",
            ("negative_control_families", 0),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("negative_control_families", 1),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("negative_control_families", 2),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("negative_control_families", 3),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("negative_control_families", 4),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("negative_control_families", 5),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("negative_control_families", 6),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("negative_control_families", 0, "expected_refusal_or_classification"),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("negative_control_families", 1, "expected_refusal_or_classification"),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("negative_control_families", 2, "expected_refusal_or_classification"),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("negative_control_families", 3, "expected_refusal_or_classification"),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("negative_control_families", 4, "expected_refusal_or_classification"),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("negative_control_families", 5, "expected_refusal_or_classification"),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("negative_control_families", 6, "expected_refusal_or_classification"),
            _TASK5_MATRIX_ERROR,
        ),
        ("row_family_matrix.json", ("discovery_probes", 0), _TASK5_MATRIX_ERROR),
        ("row_family_matrix.json", ("discovery_probes", 1), _TASK5_MATRIX_ERROR),
        ("row_family_matrix.json", ("discovery_probes", 2), _TASK5_MATRIX_ERROR),
        ("row_family_matrix.json", ("ontology_contract",), _TASK5_MATRIX_ERROR),
        ("row_family_matrix.json", ("exact_des_pairing",), _TASK5_MATRIX_ERROR),
        ("row_family_matrix.json", ("initial_scoring_state",), _TASK5_MATRIX_ERROR),
        (
            "reuse_matrix.json",
            ("relations", 0),
            "reuse_matrix.json: document must match",
        ),
        (
            "reuse_matrix.json",
            ("relations", 1),
            "reuse_matrix.json: document must match",
        ),
        (
            "reuse_matrix.json",
            ("relations", 2),
            "reuse_matrix.json: document must match",
        ),
        (
            "reuse_matrix.json",
            ("relations", 3),
            "reuse_matrix.json: document must match",
        ),
        (
            "reuse_matrix.json",
            ("relations", 4),
            "reuse_matrix.json: document must match",
        ),
    )
    for name, path, expected_error in object_cases:
        value = _path_get(_load(BUNDLE, name), path)
        assert isinstance(value, dict)
        semantic_key = min(value)
        case_id = "_".join(str(item) for item in path).replace("[", "").replace("]", "")
        for operation in ("remove_key", "add_key", "semantic"):
            yield pytest.param(
                name,
                path,
                semantic_key,
                expected_error,
                operation,
                id=f"{name}_{case_id}_{semantic_key}_{operation}",
            )


def _drift_value(value: Any) -> Any:
    if isinstance(value, str):
        return "TASK5_DETERMINISTIC_DRIFT"
    if isinstance(value, bool):
        return not value
    if isinstance(value, int | float):
        return value + 1
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


def _copy_schema_documents(source: Path, target: Path) -> None:
    target.mkdir(parents=True)
    for name in EXPECTED_DOCUMENTS:
        shutil.copy2(source / name, target / name)


def _copy_bundle(tmp_path: Path, *, source: Path = BUNDLE) -> Path:
    repo = tmp_path / "repo"
    target = repo / "cases/discovery/g6b/row_families/structural_discovery_v1"
    _copy_schema_documents(source, target)
    for design in (
        Path("docs/superpowers/specs/2026-07-31-g6b-row-family-design.md"),
        Path(APPROVED_SOURCE_DESIGN),
    ):
        if not design.is_file():
            continue
        copied_design = repo / design
        copied_design.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(design, copied_design)
    return target


def test_copy_bundle_is_schema_only_after_post_seal_materialization(
    tmp_path: Path,
) -> None:
    sealed_source = tmp_path / "sealed_source"
    shutil.copytree(BUNDLE, sealed_source)
    (sealed_source / "case_units").mkdir(exist_ok=True)
    (sealed_source / "governance").mkdir(exist_ok=True)

    bundle = _copy_bundle(tmp_path / "copied", source=sealed_source)

    assert tuple(sorted(path.name for path in bundle.iterdir())) == tuple(
        sorted(EXPECTED_DOCUMENTS)
    )
    result = validate_g6b_row_family_bundle(bundle)
    assert result.valid is True, result.errors


def _load(bundle: Path, name: str) -> dict[str, Any]:
    loaded = json.loads((bundle / name).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _write(bundle: Path, name: str, value: dict[str, Any]) -> None:
    (bundle / name).write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_preserving_key_order(bundle: Path, name: str, value: dict[str, Any]) -> None:
    (bundle / name).write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _root_key_order(path: Path) -> list[str]:
    loaded = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=lambda pairs: pairs,
    )
    assert isinstance(loaded, list)
    return [key for key, _value in loaded]


def _assert_invalid(bundle: Path, text: str) -> None:
    result = validate_g6b_row_family_bundle(bundle)
    assert result.valid is False
    assert any(text in error for error in result.errors), result.errors


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


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


def _add_contract_sentinel(value: list[Any]) -> list[Any]:
    mutated = list(value)
    sample = mutated[0] if mutated else "TASK7_SENTINEL"
    if isinstance(sample, dict):
        mutated.append({"id": "TASK7_SENTINEL"})
    else:
        mutated.append("TASK7_SENTINEL")
    return mutated


def _mutate_contract_list(value: list[Any], operation: str) -> list[Any]:
    mutated = list(value)
    if operation == "remove":
        mutated.pop(0)
    elif operation == "add":
        mutated = _add_contract_sentinel(mutated)
    elif operation == "reorder":
        assert len(mutated) > 1
        mutated[0], mutated[1] = mutated[1], mutated[0]
    elif operation == "duplicate":
        mutated.insert(0, mutated[0])
    elif operation == "semantic":
        if isinstance(mutated[0], dict):
            mutated[0] = {**mutated[0], "id": "TASK7_SEMANTIC_DRIFT"}
        else:
            mutated[0] = "TASK7_SEMANTIC_DRIFT"
    else:  # pragma: no cover - parameterization guard
        raise AssertionError(operation)
    return mutated


def _nested_get(document: dict[str, Any], path: tuple[str, ...]) -> Any:
    target: Any = document
    for key in path:
        assert isinstance(target, dict)
        target = target[key]
    return target


def _nested_set(document: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    target: Any = document
    for key in path[:-1]:
        assert isinstance(target, dict)
        target = target[key]
    assert isinstance(target, dict)
    target[path[-1]] = value


def _nested_pop(document: dict[str, Any], path: tuple[str, ...]) -> None:
    target: Any = document
    for key in path[:-1]:
        assert isinstance(target, dict)
        target = target[key]
    assert isinstance(target, dict)
    target.pop(path[-1])


def _iter_scalar_paths(value: Any, prefix: tuple[PathPart, ...] = ()) -> Iterable[Any]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _iter_scalar_paths(child, (*prefix, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_scalar_paths(child, (*prefix, index))
    else:
        yield prefix


def _iter_member_paths(value: Any, prefix: tuple[PathPart, ...] = ()) -> Iterable[Any]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield (*prefix, key)
            yield from _iter_member_paths(child, (*prefix, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield (*prefix, index)
            yield from _iter_member_paths(child, (*prefix, index))


def _representative_scalar_paths(
    document: dict[str, Any],
) -> tuple[tuple[PathPart, ...], ...]:
    return tuple(_iter_scalar_paths(document))[:12]


def _representative_member_paths(
    document: dict[str, Any],
) -> tuple[tuple[PathPart, ...], ...]:
    return tuple(_iter_member_paths(document))[:12]


def _assert_task4_baseline_valid(bundle: Path) -> None:
    result = validate_g6b_row_family_bundle(bundle)
    assert result.valid is True, result.errors


def _insert_prohibited_key(document: dict[str, Any], key: str) -> None:
    document["task6_leakage_probe"] = [{"nested": {key: "TASK6_INERT_SENTINEL"}}]


def _insert_live_instance_key_at_path(
    document: dict[str, Any], path: tuple[PathPart, ...], key: str
) -> None:
    parent = _path_get(document, path)
    if isinstance(parent, dict):
        parent[key] = "TASK4_LIVE_INSTANCE_SENTINEL"
    elif isinstance(parent, list):
        parent.append({key: "TASK4_LIVE_INSTANCE_SENTINEL"})
    else:
        raise TypeError(f"cannot inject beneath scalar path: {path!r}")


def _protocol_manifest_names(protocol: dict[str, Any]) -> tuple[str, ...]:
    paths = protocol.get("artifact_paths")
    assert isinstance(paths, list)
    return ("row_family_protocol.json",) + tuple(Path(path).name for path in paths)


def test_task4_inventory_freezes_exact_ordered_twelve_document_tuple(
    tmp_path: Path,
) -> None:
    protocol = _load(BUNDLE, "row_family_protocol.json")
    result = validate_g6b_row_family_bundle(_copy_bundle(tmp_path))

    assert tuple(result.bundle_hashes) == EXPECTED_DOCUMENTS
    assert _protocol_manifest_names(protocol) == EXPECTED_DOCUMENTS


@pytest.mark.parametrize(("name", "version"), SCHEMA_FILES.items())
def test_task4_version_contract_freezes_exact_v2_and_new_schema_versions(
    name: str, version: str
) -> None:
    document = _load(BUNDLE, name)

    assert document["schema_version"] == version


def test_task4_capability_contract_is_typed_and_all_false() -> None:
    protocol = _load(BUNDLE, "row_family_protocol.json")

    assert protocol["source_design"] == APPROVED_SOURCE_DESIGN
    assert protocol["source_design_sha256"] == APPROVED_SOURCE_DESIGN_SHA256
    assert protocol["typed_capabilities"] == EXPECTED_TYPED_CAPABILITIES
    assert protocol["typed_capabilities_sha256"] == EXPECTED_TYPED_CAPABILITIES_SHA256


def test_task4_review_state_uses_capability_reference_not_duplicate_booleans() -> None:
    review_state = _load(BUNDLE, "review_state.json")

    assert review_state["current_state"] == "ROW_FAMILY_BUNDLE_IMPLEMENTED"
    assert review_state["adversarial_review_status"] == "PENDING"
    assert (
        review_state["current_capability_reference"]
        == "row_family_protocol.json#/typed_capabilities"
    )
    assert (
        review_state["current_capability_sha256"] == EXPECTED_TYPED_CAPABILITIES_SHA256
    )
    assert "current_state_authorizes_case_creation" not in review_state
    assert "current_state_authorizes_science" not in review_state


def test_spec_17_3_02_schema_row_family_typed_capabilities_all_false() -> None:
    protocol = _load(BUNDLE, "row_family_protocol.json")
    review_state = _load(BUNDLE, "review_state.json")

    assert review_state["current_state"] == "ROW_FAMILY_BUNDLE_IMPLEMENTED"
    assert review_state["adversarial_review_status"] == "PENDING"
    assert protocol["typed_capabilities"] == EXPECTED_TYPED_CAPABILITIES
    assert all(value is False for value in protocol["typed_capabilities"].values())
    assert protocol["typed_capabilities_sha256"] == EXPECTED_TYPED_CAPABILITIES_SHA256
    assert (
        review_state["current_capability_reference"]
        == "row_family_protocol.json#/typed_capabilities"
    )
    assert (
        review_state["current_capability_sha256"] == EXPECTED_TYPED_CAPABILITIES_SHA256
    )


def test_row_family_protocol_artifact_manifest_sha256_matches_schema_hashes() -> None:
    protocol = _load(BUNDLE, "row_family_protocol.json")
    manifest: dict[str, Any] = {
        str(BUNDLE / name).replace("\\", "/"): canonical_sha256_v2(_load(BUNDLE, name))
        for name in EXPECTED_DOCUMENTS[1:]
    }

    assert protocol["artifact_manifest_sha256"] == canonical_sha256_v2(manifest)


@pytest.mark.parametrize("name", CHANGED_SCHEMA_DOCUMENTS)
def test_task4_oracle_freezes_exact_top_level_keys_for_changed_documents(
    name: str,
) -> None:
    document = _load(BUNDLE, name)

    assert tuple(document) == EXPECTED_TOP_LEVEL_KEYS[name]


@pytest.mark.parametrize("name", CHANGED_SCHEMA_DOCUMENTS)
def test_task4_oracle_uses_closed_field_level_canonical_and_self_hash_contracts(
    name: str,
) -> None:
    document = _load(BUNDLE, name)

    assert document["canonicalization_contract"] == EXPECTED_CANONICALIZATION_CONTRACT
    assert (
        document["self_hash_finalization_contract"]
        == EXPECTED_SELF_HASH_FINALIZATION_CONTRACT
    )


def test_task1_estimand_scope_contract_is_synchronized_across_payload_schemas() -> None:
    documents = {
        name: _load(BUNDLE, name)
        for name in (
            "identity_schema.json",
            "case_construction_schema.json",
            "retired_authority_fingerprint_schema.json",
        )
    }

    assert {
        json.dumps(document["estimand_id_scope_contract"], sort_keys=True)
        for document in documents.values()
    } == {json.dumps(EXPECTED_ESTIMAND_ID_SCOPE_CONTRACT, sort_keys=True)}


@pytest.mark.parametrize(
    "name",
    (
        "identity_schema.json",
        "case_construction_schema.json",
        "retired_authority_fingerprint_schema.json",
    ),
)
def test_task4_oracle_fingerprint_payload_schemas_are_closed_typed_objects(
    name: str,
) -> None:
    document = _load(BUNDLE, name)
    payload_schemas = document["fingerprint_payload_schemas"]

    assert tuple(payload_schemas) == tuple(EXPECTED_FINGERPRINT_PROJECTION_KINDS)
    for dimension, payload_schema in payload_schemas.items():
        assert tuple(payload_schema) == EXPECTED_FINGERPRINT_PAYLOAD_SCHEMA_KEYS
        assert (
            payload_schema["projection_kind"]
            == EXPECTED_FINGERPRINT_PROJECTION_KINDS[dimension]
        )
        assert (
            payload_schema["subject_type"]
            == EXPECTED_FINGERPRINT_SUBJECT_TYPES[dimension]
        )
        assert payload_schema["additional_properties"] is False
        assert isinstance(payload_schema["set_like_array_paths"], list)
        assert payload_schema["set_like_array_paths"] == sorted(
            set(payload_schema["set_like_array_paths"])
        )
        assert isinstance(payload_schema["nested_field_contracts"], dict)
        assert payload_schema["nested_field_contracts"]
        assert isinstance(payload_schema["prohibited_fields"], list)
        assert payload_schema["prohibited_fields"]
        assert payload_schema["prohibited_fields"] == sorted(
            set(payload_schema["prohibited_fields"])
        )

    random_required = payload_schemas["random_stream_manifest_sha256"][
        "required_fields"
    ]
    assert tuple(random_required) == ("stochastic", "exact")
    assert all(
        isinstance(fields, list) and fields for fields in random_required.values()
    )
    for dimension, payload_schema in payload_schemas.items():
        if dimension != "random_stream_manifest_sha256":
            assert isinstance(payload_schema["required_fields"], list)
            assert payload_schema["required_fields"]


@pytest.mark.parametrize(("name", "expected"), EXPECTED_SCHEMA_REFUSAL_CODES.items())
def test_task4_oracle_refusal_code_union_matches_exact_gate_contract(
    name: str, expected: tuple[str, ...]
) -> None:
    document = _load(BUNDLE, name)

    assert tuple(document["refusal_reason_codes"]) == expected
    assert tuple(document["refusal_reason_codes"]) == tuple(
        sorted(set(document["refusal_reason_codes"]))
    )


@pytest.mark.parametrize(
    "name",
    ("overlap_report_schema.json", "retired_authority_fingerprint_schema.json"),
)
def test_task4_oracle_overlap_subject_status_order_matches_spec(name: str) -> None:
    document = _load(BUNDLE, name)

    assert tuple(document["input_overlap_subject_status_values"]) == (
        EXPECTED_OVERLAP_SUBJECT_STATUSES
    )


@pytest.mark.parametrize("name", CHANGED_SCHEMA_DOCUMENTS)
def test_task4_oracle_missing_top_level_key_is_rejected(
    tmp_path: Path, name: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    _assert_task4_baseline_valid(bundle)
    document = _load(bundle, name)
    document.pop(EXPECTED_TOP_LEVEL_KEYS[name][0])
    _write(bundle, name, document)

    assert validate_g6b_row_family_bundle(bundle).valid is False


@pytest.mark.parametrize("name", CHANGED_SCHEMA_DOCUMENTS)
def test_task4_oracle_extra_top_level_key_is_rejected(
    tmp_path: Path, name: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    _assert_task4_baseline_valid(bundle)
    document = _load(bundle, name)
    document["task4_unexpected_top_level_key"] = "not allowed"
    _write(bundle, name, document)

    assert validate_g6b_row_family_bundle(bundle).valid is False


@pytest.mark.parametrize(("name", "version"), SCHEMA_FILES.items())
def test_task4_oracle_version_drift_is_rejected(
    tmp_path: Path, name: str, version: str
) -> None:
    if name == "row_family_matrix.json":
        pytest.skip("Task4 preserves row_family_matrix.json byte-for-byte.")
    bundle = _copy_bundle(tmp_path)
    _assert_task4_baseline_valid(bundle)
    document = _load(bundle, name)
    document["schema_version"] = f"{version}-drift"
    _write(bundle, name, document)

    assert validate_g6b_row_family_bundle(bundle).valid is False


@pytest.mark.parametrize("name", CHANGED_SCHEMA_DOCUMENTS)
def test_task4_oracle_representative_reorder_sensitive_array_drift_is_rejected(
    tmp_path: Path, name: str
) -> None:
    field_path = REORDER_SENSITIVE_FIELDS[name]
    if not field_path:
        pytest.skip(f"{name} has no Task4-assigned reorder-sensitive array.")
    bundle = _copy_bundle(tmp_path)
    _assert_task4_baseline_valid(bundle)
    document = _load(bundle, name)
    value = _path_get(document, field_path)
    assert isinstance(value, list)
    assert len(value) >= 2
    value[0], value[1] = value[1], value[0]
    _write(bundle, name, document)

    assert validate_g6b_row_family_bundle(bundle).valid is False


@pytest.mark.parametrize("name", CHANGED_SCHEMA_DOCUMENTS)
def test_task4_oracle_wrong_nested_field_is_rejected(tmp_path: Path, name: str) -> None:
    bundle = _copy_bundle(tmp_path)
    _assert_task4_baseline_valid(bundle)
    document = _load(bundle, name)
    path = WRONG_NESTED_FIELD_PATHS[name]
    value = _path_get(document, path)
    _path_set(document, path, _drift_value(value))
    _write(bundle, name, document)

    assert validate_g6b_row_family_bundle(bundle).valid is False


@pytest.mark.parametrize("name", CHANGED_SCHEMA_DOCUMENTS)
@pytest.mark.parametrize("prohibited_key", TASK4_RECURSIVE_PROHIBITED_FIELDS)
def test_task4_oracle_recursive_live_instance_injection_is_rejected(
    tmp_path: Path, name: str, prohibited_key: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    _assert_task4_baseline_valid(bundle)
    document = _load(bundle, name)
    _insert_live_instance_key_at_path(
        document, LIVE_INJECTION_PARENT_PATHS[name], prohibited_key
    )
    _write(bundle, name, document)

    result = validate_g6b_row_family_bundle(bundle)
    assert result.valid is False
    assert f"{name}: prohibited outcome key present: {prohibited_key}" in result.errors


@pytest.mark.parametrize("name", CHANGED_SCHEMA_DOCUMENTS)
def test_task4_oracle_scalar_leaf_mutation_walker_is_rejected(
    tmp_path: Path, name: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    _assert_task4_baseline_valid(bundle)
    baseline = _load(bundle, name)
    paths = tuple(_iter_scalar_paths(baseline))
    assert paths
    for index, path in enumerate(paths):
        isolated = _copy_bundle(tmp_path / f"scalar_{index}")
        _assert_task4_baseline_valid(isolated)
        document = _load(isolated, name)
        _path_set(document, path, _drift_value(_path_get(document, path)))
        _write(isolated, name, document)
        assert validate_g6b_row_family_bundle(isolated).valid is False, path


@pytest.mark.parametrize("name", CHANGED_SCHEMA_DOCUMENTS)
def test_task4_oracle_list_and_map_member_removal_walker_is_rejected(
    tmp_path: Path, name: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    _assert_task4_baseline_valid(bundle)
    baseline = _load(bundle, name)
    paths = tuple(_iter_member_paths(baseline))
    assert paths
    for index, path in enumerate(paths):
        isolated = _copy_bundle(tmp_path / f"member_{index}")
        _assert_task4_baseline_valid(isolated)
        document = _load(isolated, name)
        _path_pop(document, path)
        _write(isolated, name, document)
        assert validate_g6b_row_family_bundle(isolated).valid is False, path


def test_task4_oracle_prohibited_vocabularies_are_not_live_instances(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path)
    _assert_task4_baseline_valid(bundle)
    for name in CHANGED_SCHEMA_DOCUMENTS:
        document = _load(bundle, name)
        for field in ("recursive_prohibited_fields", "prohibited_instance_fields"):
            if field in document:
                assert isinstance(document[field], list)

    result = validate_g6b_row_family_bundle(bundle)

    assert result.valid is True, result.errors


def test_canonical_row_family_bundle_is_valid_and_disabled(tmp_path: Path) -> None:
    result = validate_g6b_row_family_bundle(_copy_bundle(tmp_path))

    assert result.valid is True
    assert result.errors == ()
    assert result.scientific_execution_authorized is False
    assert result.case_creation_authorized is False
    assert result.adversarial_review_status == "PENDING"
    assert result.review_state == "ROW_FAMILY_BUNDLE_IMPLEMENTED"
    assert set(result.bundle_hashes) == set(_NAMES)


@pytest.mark.parametrize(("name", "version"), sorted(EXISTING_SCHEMA_FILES.items()))
def test_wrong_schema_version_is_rejected(
    tmp_path: Path, name: str, version: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, name)
    value["schema_version"] = f"{version}-drift"
    _write(bundle, name, value)
    _assert_invalid(bundle, f"{name}: wrong schema_version")


@pytest.mark.parametrize("name", sorted(SCHEMA_FILES))
@pytest.mark.parametrize(
    ("field", "drift"),
    [
        ("study_role", "confirmation"),
        ("confirmation_use", "allowed"),
    ],
)
def test_common_contract_drift_is_rejected(
    tmp_path: Path, name: str, field: str, drift: object
) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, name)
    value[field] = drift
    _write(bundle, name, value)
    _assert_invalid(bundle, f"{name}: {field}")


@pytest.mark.parametrize("field", _LEGACY_GLOBAL_AUTHORIZATION_FIELDS)
@pytest.mark.parametrize("name", CHANGED_SCHEMA_DOCUMENTS)
def test_changed_v2_documents_reject_inserted_legacy_global_authorization_flags(
    tmp_path: Path, name: str, field: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, name)
    value[field] = True
    _write(bundle, name, value)
    _assert_invalid(bundle, f"{name}: prohibited outcome key present: {field}")


@pytest.mark.parametrize("field", sorted(EXPECTED_TYPED_CAPABILITIES))
def test_protocol_typed_capability_true_drift_is_rejected(
    tmp_path: Path, field: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "row_family_protocol.json")
    protocol["typed_capabilities"][field] = True
    protocol["typed_capabilities_sha256"] = hashlib.sha256(
        json.dumps(
            protocol["typed_capabilities"],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    _write(bundle, "row_family_protocol.json", protocol)
    result = validate_g6b_row_family_bundle(bundle)
    assert result.valid is False
    assert any(
        "row_family_protocol.json: document must match" in error
        for error in result.errors
    )
    assert result.scientific_execution_authorized is False
    assert result.case_creation_authorized is False


@pytest.mark.parametrize("field", _LEGACY_GLOBAL_AUTHORIZATION_FIELDS)
def test_row_family_matrix_legacy_false_authorization_flags_are_immutable(
    tmp_path: Path, field: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    matrix[field] = True
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


@pytest.mark.parametrize("name", sorted(EXPECTED_DOCUMENTS))
def test_unknown_key_is_rejected_for_every_document(tmp_path: Path, name: str) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, name)
    value["unexpected"] = "not allowed"
    _write(bundle, name, value)
    _assert_invalid(bundle, f"{name}: document must match")


@pytest.mark.parametrize("name", sorted(EXPECTED_DOCUMENTS))
def test_missing_key_is_rejected_for_every_document(tmp_path: Path, name: str) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, name)
    key = min(value)
    value.pop(key)
    _write(bundle, name, value)
    _assert_invalid(bundle, f"{name}: document must match")


@pytest.mark.parametrize(
    ("name", "path", "expected_error"),
    [
        (
            "row_family_protocol.json",
            ("artifact_paths",),
            "row_family_protocol.json: document must match",
        ),
        (
            "identity_schema.json",
            ("identity_levels",),
            "identity_schema.json: identity_levels must match",
        ),
        (
            "identity_schema.json",
            ("canonical_dimensions",),
            "identity_schema.json: document must match",
        ),
        (
            "identity_schema.json",
            ("fingerprint_record_keys",),
            "identity_schema.json: fingerprint_record_keys must match",
        ),
        (
            "identity_schema.json",
            ("method_roles",),
            "identity_schema.json: method_roles must match",
        ),
        ("row_family_matrix.json", ("negative_control_families",), _TASK5_MATRIX_ERROR),
        ("row_family_matrix.json", ("discovery_probes",), _TASK5_MATRIX_ERROR),
        (
            "row_family_matrix.json",
            ("ontology_contract", "D_local_admission_routes"),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("exact_des_pairing", "same_selected_bad_labels"),
            _TASK5_MATRIX_ERROR,
        ),
        (
            "reuse_matrix.json",
            ("relations",),
            "reuse_matrix.json: reuse relation ids must match",
        ),
        (
            "overlap_report_schema.json",
            ("retired_authorities",),
            "overlap_report_schema.json: document must match",
        ),
        (
            "review_state.json",
            ("allowed_states_in_order",),
            "review_state.json: allowed_states_in_order must match",
        ),
        (
            "failure_ledger.json",
            ("required_future_reason_codes",),
            "failure_ledger.json: required_future_reason_codes must match",
        ),
    ],
)
@pytest.mark.parametrize(
    "operation", ["remove", "add", "reorder", "duplicate", "semantic"]
)
def test_major_contract_list_mutations_are_rejected(
    tmp_path: Path,
    name: str,
    path: tuple[str, ...],
    expected_error: str,
    operation: str,
) -> None:
    bundle = _copy_bundle(tmp_path)
    document = _load(bundle, name)
    value = _nested_get(document, path)
    assert isinstance(value, list)
    document_path = path
    _nested_set(document, document_path, _mutate_contract_list(value, operation))
    _write(bundle, name, document)
    _assert_invalid(bundle, expected_error)


@pytest.mark.parametrize(
    ("name", "path", "operation", "expected_error"),
    [
        (
            "failure_ledger.json",
            ("entries",),
            "add",
            "failure_ledger.json: entries must remain empty",
        ),
        (
            "row_family_matrix.json",
            ("initial_scoring_state", "metric_observations"),
            "add",
            _TASK5_MATRIX_ERROR,
        ),
    ],
)
def test_empty_canonical_lists_reject_nonempty_drift(
    tmp_path: Path,
    name: str,
    path: tuple[str, ...],
    operation: str,
    expected_error: str,
) -> None:
    bundle = _copy_bundle(tmp_path)
    document = _load(bundle, name)
    value = _nested_get(document, path)
    assert isinstance(value, list)
    assert value == []
    _nested_set(document, path, _mutate_contract_list(value, operation))
    _write(bundle, name, document)
    _assert_invalid(bundle, expected_error)


@pytest.mark.parametrize(
    ("name", "path", "semantic_key", "expected_error"),
    [
        (
            "row_family_protocol.json",
            ("execution_boundary",),
            "case_creation",
            "row_family_protocol.json: document must match",
        ),
        (
            "identity_schema.json",
            ("no_stochastic_method_manifest",),
            "allowed",
            "identity_schema.json: no_stochastic_method_manifest must match",
        ),
        (
            "row_family_matrix.json",
            ("ontology_contract",),
            "D_local_definition",
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("exact_des_pairing",),
            "same_case_unit_id",
            _TASK5_MATRIX_ERROR,
        ),
        (
            "row_family_matrix.json",
            ("initial_scoring_state",),
            "execution_status",
            _TASK5_MATRIX_ERROR,
        ),
    ],
)
@pytest.mark.parametrize("operation", ["remove_key", "add_key", "semantic"])
def test_major_contract_object_mutations_are_rejected(
    tmp_path: Path,
    name: str,
    path: tuple[str, ...],
    semantic_key: str,
    expected_error: str,
    operation: str,
) -> None:
    bundle = _copy_bundle(tmp_path)
    document = _load(bundle, name)
    value = _nested_get(document, path)
    assert isinstance(value, dict)
    if operation == "remove_key":
        _nested_pop(document, (*path, semantic_key))
    elif operation == "add_key":
        value["task7_unexpected"] = "not allowed"
    elif operation == "semantic":
        _nested_set(document, (*path, semantic_key), _drift_value(value[semantic_key]))
    else:  # pragma: no cover - parameterization guard
        raise AssertionError(operation)
    _write(bundle, name, document)
    _assert_invalid(bundle, expected_error)


@pytest.mark.parametrize(
    ("name", "path", "expected_error", "operation"),
    list(_nested_scientific_list_cases()),
)
def test_nested_scientific_list_mutation_inventory_is_rejected(
    tmp_path: Path,
    name: str,
    path: tuple[PathPart, ...],
    expected_error: str,
    operation: str,
) -> None:
    bundle = _copy_bundle(tmp_path)
    document = _load(bundle, name)
    value = _path_get(document, path)
    assert isinstance(value, list)
    _path_set(document, path, _mutate_contract_list(value, operation))
    _write(bundle, name, document)
    _assert_invalid(bundle, expected_error)


@pytest.mark.parametrize(
    ("name", "path", "semantic_key", "expected_error", "operation"),
    list(_nested_scientific_object_cases()),
)
def test_nested_scientific_object_mutation_inventory_is_rejected(
    tmp_path: Path,
    name: str,
    path: tuple[PathPart, ...],
    semantic_key: str,
    expected_error: str,
    operation: str,
) -> None:
    bundle = _copy_bundle(tmp_path)
    document = _load(bundle, name)
    value = _path_get(document, path)
    assert isinstance(value, dict)
    if operation == "remove_key":
        _path_pop(document, (*path, semantic_key))
    elif operation == "add_key":
        value["task7_nested_unexpected"] = "not allowed"
    elif operation == "semantic":
        _path_set(document, (*path, semantic_key), _drift_value(value[semantic_key]))
    else:  # pragma: no cover - parameterization guard
        raise AssertionError(operation)
    _write(bundle, name, document)
    _assert_invalid(bundle, expected_error)


@pytest.mark.parametrize(
    ("probe_index", "operation"), list(_probe_nested_falsifier_cases())
)
def test_probe_matrix_nested_falsifier_mutations_are_rejected(
    tmp_path: Path, probe_index: int, operation: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    probes = matrix["discovery_probes"]
    assert isinstance(probes, list)
    probe = probes[probe_index]
    assert isinstance(probe, dict)
    falsifiers = probe["falsifiers"]
    assert isinstance(falsifiers, list)
    probe["falsifiers"] = _mutate_contract_list(falsifiers, operation)
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


@pytest.mark.parametrize(
    ("relation_index", "field", "operation"), list(_reuse_relation_nested_list_cases())
)
def test_reuse_relation_nested_list_mutations_are_rejected(
    tmp_path: Path, relation_index: int, field: str, operation: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    reuse = _load(bundle, "reuse_matrix.json")
    relations = reuse["relations"]
    assert isinstance(relations, list)
    relation = relations[relation_index]
    assert isinstance(relation, dict)
    value = relation[field]
    assert isinstance(value, list)
    relation[field] = _mutate_contract_list(value, operation)
    _write(bundle, "reuse_matrix.json", reuse)
    _assert_invalid(bundle, "reuse_matrix.json: document must match")


@pytest.mark.parametrize(
    ("control_index", "key", "operation"), list(_control_expected_object_key_cases())
)
def test_control_expected_refusal_or_classification_key_mutations_are_rejected(
    tmp_path: Path, control_index: int, key: str, operation: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    controls = matrix["negative_control_families"]
    assert isinstance(controls, list)
    control = controls[control_index]
    assert isinstance(control, dict)
    expected = control["expected_refusal_or_classification"]
    assert isinstance(expected, dict)
    if operation == "remove_key":
        expected.pop(key)
    elif operation == "add_key":
        expected["task7_nested_unexpected"] = "not allowed"
    else:  # pragma: no cover - parameterization guard
        raise AssertionError(operation)
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


def test_json_object_key_reordering_remains_semantically_neutral(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path)
    canonical_path = BUNDLE / "row_family_protocol.json"
    target_path = bundle / "row_family_protocol.json"
    canonical_order = _root_key_order(canonical_path)
    protocol = _load(bundle, "row_family_protocol.json")
    reordered = dict(reversed(list(protocol.items())))
    _write_preserving_key_order(bundle, "row_family_protocol.json", reordered)
    reordered_order = _root_key_order(target_path)

    result = validate_g6b_row_family_bundle(bundle)

    assert reordered_order != canonical_order
    assert reordered_order == list(reversed(canonical_order))
    assert result.valid is True


def test_review_state_order_drift_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    review_state = _load(bundle, "review_state.json")
    states = review_state["allowed_states_in_order"]
    states[0], states[1] = states[1], states[0]
    _write(bundle, "review_state.json", review_state)
    _assert_invalid(bundle, "review_state.json: allowed_states_in_order must match")


def test_review_state_allowed_state_removal_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    baseline = _load(bundle, "review_state.json")
    states = baseline["allowed_states_in_order"]
    assert isinstance(states, list)
    assert states
    for index, state in enumerate(states):
        isolated = _copy_bundle(tmp_path / f"state_{index}")
        review_state = _load(isolated, "review_state.json")
        review_state["allowed_states_in_order"].remove(state)
        _write(isolated, "review_state.json", review_state)
        _assert_invalid(
            isolated, "review_state.json: allowed_states_in_order must match"
        )


def test_review_state_forward_transition_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    baseline = _load(bundle, "review_state.json")
    states = baseline["allowed_states_in_order"]
    assert isinstance(states, list)
    later_states = [
        state
        for state in states
        if state != "ROW_FAMILY_BUNDLE_IMPLEMENTED"
        and state != baseline["current_state"]
    ]
    assert later_states
    for index, state in enumerate(later_states):
        isolated = _copy_bundle(tmp_path / f"forward_{index}")
        review_state = _load(isolated, "review_state.json")
        review_state["current_state"] = state
        _write(isolated, "review_state.json", review_state)
        _assert_invalid(
            isolated,
            "review_state.json: current_state must remain "
            "ROW_FAMILY_BUNDLE_IMPLEMENTED",
        )


def test_review_state_adversarial_status_drift_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    review_state = _load(bundle, "review_state.json")
    review_state["adversarial_review_status"] = "PASSED"
    _write(bundle, "review_state.json", review_state)
    _assert_invalid(
        bundle,
        "review_state.json: adversarial_review_status must remain PENDING",
    )


def test_review_state_forward_only_false_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    review_state = _load(bundle, "review_state.json")
    review_state["forward_only"] = False
    _write(bundle, "review_state.json", review_state)
    _assert_invalid(bundle, "review_state.json: forward_only must be true")


def test_review_state_inserted_case_creation_authorization_is_rejected(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path)
    review_state = _load(bundle, "review_state.json")
    review_state["current_state_authorizes_case_creation"] = True
    _write(bundle, "review_state.json", review_state)
    _assert_invalid(bundle, "review_state.json: document must match")


def test_review_state_inserted_science_authorization_is_rejected(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path)
    review_state = _load(bundle, "review_state.json")
    review_state["current_state_authorizes_science"] = True
    _write(bundle, "review_state.json", review_state)
    _assert_invalid(bundle, "review_state.json: document must match")


def test_ledger_append_only_false_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    ledger = _load(bundle, "failure_ledger.json")
    ledger["append_only"] = False
    _write(bundle, "failure_ledger.json", ledger)
    _assert_invalid(bundle, "failure_ledger.json: append_only must be true")


def test_ledger_nonempty_entries_are_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    ledger = _load(bundle, "failure_ledger.json")
    ledger["entries"] = [{"reason_code": "schema_drift"}]
    _write(bundle, "failure_ledger.json", ledger)
    _assert_invalid(bundle, "failure_ledger.json: entries must remain empty")


def test_ledger_empty_entries_meaning_drift_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    ledger = _load(bundle, "failure_ledger.json")
    ledger["empty_entries_meaning"] = "no failures"
    _write(bundle, "failure_ledger.json", ledger)
    _assert_invalid(bundle, "failure_ledger.json: empty_entries_meaning must match")


def test_ledger_historical_failure_flag_false_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    ledger = _load(bundle, "failure_ledger.json")
    ledger["empty_entries_do_not_mean_no_historical_failures"] = False
    _write(bundle, "failure_ledger.json", ledger)
    _assert_invalid(
        bundle,
        "failure_ledger.json: empty_entries_do_not_mean_no_historical_failures "
        "must be true",
    )


@pytest.mark.parametrize("reason_code", _REQUIRED_FUTURE_REASON_CODES)
def test_ledger_required_reason_code_removal_is_rejected(
    tmp_path: Path, reason_code: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    ledger = _load(bundle, "failure_ledger.json")
    ledger["required_future_reason_codes"].remove(reason_code)
    _write(bundle, "failure_ledger.json", ledger)
    _assert_invalid(
        bundle,
        "failure_ledger.json: required_future_reason_codes must match",
    )


@pytest.mark.parametrize("name", _NAMES)
@pytest.mark.parametrize("prohibited_key", _PROHIBITED_OUTCOME_KEYS)
def test_prohibited_key_leakage_is_rejected_recursively(
    tmp_path: Path, name: str, prohibited_key: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    document = _load(bundle, name)
    _insert_prohibited_key(document, prohibited_key)
    _write(bundle, name, document)
    _assert_invalid(
        bundle,
        f"{name}: prohibited outcome key present: {prohibited_key}",
    )


@pytest.mark.parametrize("name", _NAMES)
def test_missing_document_is_rejected(tmp_path: Path, name: str) -> None:
    bundle = _copy_bundle(tmp_path)
    (bundle / name).unlink()
    _assert_invalid(bundle, f"missing JSON documents: ['{name}']")


def test_copied_noncanonical_root_is_rejected(tmp_path: Path) -> None:
    floating = tmp_path / "floating"
    _copy_schema_documents(BUNDLE, floating)
    _assert_invalid(
        floating,
        "bundle root must be <repo>/cases/discovery/g6b/row_families/"
        "structural_discovery_v1",
    )


@pytest.mark.parametrize("field", sorted(EXPECTED_TYPED_CAPABILITIES))
def test_true_typed_capability_without_matching_contract_is_rejected(
    tmp_path: Path, field: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, "row_family_protocol.json")
    value["typed_capabilities"][field] = True
    _write(bundle, "row_family_protocol.json", value)
    _assert_invalid(bundle, "row_family_protocol.json: document must match")


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


@pytest.mark.parametrize(
    ("token", "expected_error"),
    [
        ("NaN", "non-finite JSON constant prohibited: NaN"),
        ("Infinity", "non-finite JSON constant prohibited: Infinity"),
        ("1.25", "JSON floating-point values are prohibited"),
        ("-0", "JSON negative zero is prohibited"),
    ],
)
def test_noncanonical_json_number_is_reported_as_invalid(
    tmp_path: Path, token: str, expected_error: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    path = bundle / "row_family_protocol.json"
    raw = path.read_text(encoding="utf-8")
    raw = raw.replace('"study_role": "discovery_only"', f'"study_role": {token}', 1)
    path.write_text(raw, encoding="utf-8")

    _assert_invalid(bundle, expected_error)


@pytest.mark.parametrize(
    ("old", "new", "expected_path"),
    [
        ('"study_role"', '"study_role_e\u0301"', "$.study_role_é"),
        ('"discovery_only"', '"discovery_only_e\u0301"', "$.study_role"),
    ],
)
def test_non_nfc_member_name_or_string_value_is_reported_as_invalid(
    tmp_path: Path, old: str, new: str, expected_path: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    path = bundle / "row_family_protocol.json"
    raw = path.read_text(encoding="utf-8").replace(old, new, 1)
    path.write_text(raw, encoding="utf-8")

    _assert_invalid(bundle, f"Unicode NFC at {expected_path}")


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
    "level",
    [
        "family_id",
        "case_unit_id",
        "method_observation_id",
        "method_companion_group_id",
    ],
)
def test_missing_identity_level_is_rejected(tmp_path: Path, level: str) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, "identity_schema.json")
    value["identity_levels"].remove(level)
    _write(bundle, "identity_schema.json", value)
    _assert_invalid(bundle, "identity_levels must match")


@pytest.mark.parametrize("key", EXPECTED_FINGERPRINT_RECORD_KEYS)
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


@pytest.mark.parametrize("relation_id", EXPECTED_REUSE_RELATION_IDS)
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


def test_row_family_matrix_requires_foundation_estimand_v2(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    assert (
        matrix["ontology_contract"]["foundation_estimand_schema_version"]
        == "ims-deadlock/g6b-estimand-schema/v2"
    )
    matrix["ontology_contract"]["foundation_estimand_schema_version"] = (
        "ims-deadlock/g6b-estimand-schema/v1"
    )
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


def test_row_family_matrix_requires_terminal_partition_v3(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    assert (
        matrix["ontology_contract"]["terminal_classification_version"]
        == "ims-deadlock/g6-terminal-stopping-partition/v3"
    )
    matrix["ontology_contract"]["terminal_classification_version"] = (
        "ims-deadlock/g6-terminal-stopping-partition/v2"
    )
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


def test_row_family_matrix_rejects_s_reach_as_selected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    matrix["ontology_contract"]["derived_state_sets"]["S_reach"][
        "selectable_target"
    ] = True
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


def test_row_family_matrix_requires_nonnull_certified_domain_hash(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    matrix["ontology_contract"]["derived_state_sets"]["S_T"][
        "requires_nonnull_absorption_domain_hash"
    ] = False
    _write(bundle, "row_family_matrix.json", matrix)
    _assert_invalid(bundle, _TASK5_MATRIX_ERROR)


def test_exact_des_pairing_requires_same_absorption_domain_hash(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path)
    matrix = _row_family_matrix_from(bundle)
    assert matrix["exact_des_pairing"]["same_absorption_domain_hash"] is True
    matrix["exact_des_pairing"]["same_absorption_domain_hash"] = False
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
        pytest.param(
            "certified_absorption_domain_required_false",
            id="exact_des_certified_absorption_domain_required_false",
        ),
        pytest.param(
            "same_absorption_domain_hash_false",
            id="exact_des_same_absorption_domain_hash_false",
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
    elif mutation == "certified_absorption_domain_required_false":
        pairing["certified_absorption_domain_required"] = False
    elif mutation == "same_absorption_domain_hash_false":
        pairing["same_absorption_domain_hash"] = False
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


def test_validator_remains_data_only() -> None:
    path = Path("src/ims_deadlock/g6b_row_family_protocol.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    allowed_imports = {
        "__future__",
        "hashlib",
        "json",
        "unicodedata",
        "dataclasses",
        "pathlib",
        "typing",
    }
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            assert node.module is not None
            assert node.level == 0
            imported.add(node.module)
    assert imported <= allowed_imports
    assert "Path.cwd" not in path.read_text(encoding="utf-8")


def test_validator_has_no_filesystem_mutation_surface() -> None:
    path = Path("src/ims_deadlock/g6b_row_family_protocol.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    forbidden_methods = {
        "write_text",
        "write_bytes",
        "mkdir",
        "touch",
        "unlink",
        "rmdir",
        "rename",
        "replace",
        "chmod",
        "lchmod",
        "symlink_to",
        "hardlink_to",
        "link_to",
        "truncate",
        "writelines",
        "write",
    }
    forbidden_dynamic_calls = {
        "__import__",
        "compile",
        "delattr",
        "eval",
        "exec",
        "getattr",
        "setattr",
    }

    def literal_mode(node: ast.Call, positional_index: int) -> str | None:
        keyword = next(
            (item.value for item in node.keywords if item.arg == "mode"), None
        )
        candidate = (
            keyword
            if keyword is not None
            else (
                node.args[positional_index]
                if len(node.args) > positional_index
                else None
            )
        )
        if candidate is None:
            return None
        assert isinstance(candidate, ast.Constant)
        assert isinstance(candidate.value, str)
        return candidate.value

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            assert node.attr not in forbidden_methods
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Attribute) and node.func.attr == "open":
            mode = literal_mode(node, 0)
            if mode is not None:
                assert not set(mode) & {"w", "a", "x", "+"}
        if isinstance(node.func, ast.Name):
            assert node.func.id not in forbidden_dynamic_calls
            if node.func.id == "open":
                mode = literal_mode(node, 1)
                if mode is not None:
                    assert not set(mode) & {"w", "a", "x", "+"}


def test_valid_validation_does_not_mutate_canonical_bundle(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    before = _snapshot(bundle)
    result = validate_g6b_row_family_bundle(bundle)
    after = _snapshot(bundle)
    assert result.valid is True
    assert after == before


def test_invalid_floating_copy_is_rejected_without_mutation(tmp_path: Path) -> None:
    floating = tmp_path / "floating_bundle"
    _copy_schema_documents(BUNDLE, floating)
    value = _load(floating, "review_state.json")
    value["current_state"] = "EXECUTION_AUTHORIZED"
    _write(floating, "review_state.json", value)
    before = _snapshot(floating)
    result = validate_g6b_row_family_bundle(floating)
    after = _snapshot(floating)
    assert result.valid is False
    assert any(
        "bundle root must be <repo>/cases/discovery/g6b/row_families/"
        "structural_discovery_v1" in error
        for error in result.errors
    )
    assert any(
        "review_state.json: document must match" in error for error in result.errors
    )
    assert after == before


_SPEC_17_3_TEST_FILES = (
    Path("tests/test_g6b_canonical_json.py"),
    Path("tests/test_g6b_schema_contracts.py"),
    Path("tests/test_g6b_protocol.py"),
    Path("tests/test_g6b_row_family_protocol.py"),
)
_SPEC_17_3_PREFIX = "test_spec_17_3_"
_SPEC_17_3_STATUSES: dict[int, _SpecRequirementStatus] = {
    number: {
        "schema_tranche": (
            "PASS_SCHEMA_GUARD_ONLY" if number in {15, 27} else "PASS_SCHEMA_TRANCHE"
        ),
        "runtime_capability": (
            "DEFERRED_REQUIRES_SEPARATE_GATE"
            if number in {15, 27}
            else "NOT_REQUIRED_BY_THIS_SCHEMA_ITEM"
        ),
    }
    for number in range(1, 45)
}
_SPEC_17_3_REQUIREMENT_MANIFEST: dict[
    int,
    tuple[_SpecRequirementEntry, ...],
] = {
    1: (
        {
            "test_id": (
                "tests/test_g6b_protocol.py::test_spec_17_3_01_schema_state_order"
            ),
            "owner": "Task 2",
            "task": "protocol_state_surface",
            "aspect": (
                "state order places normalization and preflight before quantitative "
                "authorization"
            ),
        },
    ),
    2: (
        {
            "test_id": (
                "tests/test_g6b_protocol.py::"
                "test_spec_17_3_02_schema_only_capabilities_false"
            ),
            "owner": "Task 2",
            "task": "protocol_state_surface",
            "aspect": "current state remains pending and all four capabilities false",
        },
        {
            "test_id": (
                "tests/test_g6b_row_family_protocol.py::"
                "test_spec_17_3_02_schema_row_family_typed_capabilities_all_false"
            ),
            "owner": "Task 4",
            "task": "row_family_capability_surface",
            "aspect": (
                "row-family review state references the typed capability hash with "
                "all four capabilities false"
            ),
        },
    ),
    3: (
        {
            "test_id": (
                "tests/test_g6b_canonical_json.py::"
                "test_spec_17_3_03_schema_self_hash_and_dag"
            ),
            "owner": "Task 1",
            "task": "canonical_json",
            "aspect": "null-placeholder self-hash and DAG mutations fail",
        },
    ),
    4: (
        {
            "test_id": (
                "tests/test_g6b_canonical_json.py::"
                "test_spec_17_3_04_schema_canonical_json_refusals"
            ),
            "owner": "Task 1",
            "task": "canonical_json",
            "aspect": "duplicate NFC number path and set-array mutations fail",
        },
    ),
    5: (
        {
            "test_id": (
                "tests/test_g6b_canonical_json.py::"
                "test_spec_17_3_05_schema_historical_decimal_exactness"
            ),
            "owner": "Task 1",
            "task": "canonical_json",
            "aspect": "historical numeric tokens use exact Decimal conversion",
        },
    ),
    6: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_06_schema_fingerprint_projection_relations"
            ),
            "owner": "Task 3",
            "task": "schema_contracts",
            "aspect": (
                "fingerprint subject projection payload dependency correlation "
                "envelope relations are enforced"
            ),
        },
    ),
    7: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_07_schema_governance_only_projection_hash_invariance"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "governance-only ID path label timestamp changes leave subject-free "
                "projection hashes invariant"
            ),
        },
    ),
    8: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_08_schema_renamed_content_predictions_refuse"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "renamed retired content and paraphrased unchanged predictions refuse"
            ),
        },
    ),
    9: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_09_schema_content_mutations_keep_correlations"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "scientific content mutations change owning projection without "
                "converting correlations into independent evidence"
            ),
        },
    ),
    10: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_10_schema_state_snapshot_parent_link_free"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "state_snapshot is pre-enumeration parent-linked subject-free and "
                "cannot be replaced by state_space_hash"
            ),
        },
    ),
    11: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_11_schema_unknown_scientific_inputs_refuse"
            ),
            "owner": "Task 3",
            "task": "schema_contracts",
            "aspect": (
                "unknown scientific input fields refuse rather than hash silently"
            ),
        },
    ),
    12: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_12_schema_retired_inventory_fail_closed"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "retired inventory missing stale mismatched local-only unverified "
                "states fail closed"
            ),
        },
    ),
    13: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_13_schema_inherited_g4_records_keep_one_lineage_and_count"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "G5 and G6-R inherited G4 records keep one lineage and one evidence "
                "count"
            ),
        },
    ),
    14: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_14_schema_lineage_statuses_remain_distinct"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "direct derived inherited not-applicable unreconstructable statuses "
                "remain distinct"
            ),
        },
    ),
    15: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_15_schema_normalizer_allowlist_guard"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "normalizer source analyzer rejects imports calls reads and outputs "
                "outside exact data-only allowlist"
            ),
            "labels": ("SCHEMA_REPRESENTABILITY_ONLY",),
        },
    ),
    16: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_16_schema_not_applicable_projection_pass_is_protocol_only"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "equal subject-free not-applicable projections yield only "
                "not_applicable_by_protocol_pass"
            ),
        },
    ),
    17: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_17_schema_stochastic_streams_require_disjoint_substream_proof"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "stochastic streams require disjoint-substream proof and unequal "
                "hashes alone do not pass"
            ),
        },
    ),
    18: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_18_schema_output_root_reservations_are_inert"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "output-root reservations are deterministic inert containment-only and "
                "cannot rescue copied content"
            ),
        },
    ),
    19: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_19_schema_root_projection_boundaries"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "G4 root is not-applicable and G5 G6-R root projections exclude "
                "absolute prefixes and output content"
            ),
        },
    ),
    20: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_20_schema_metric_reuse_requires_companion_auth"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "metric reuse requires one exact companion-group authorization and "
                "preserves one-case two-method counting"
            ),
        },
    ),
    21: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_21_schema_method_refusal_propagates_to_case"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "method refusal propagates to its case and sealed methods cannot be "
                "dropped"
            ),
        },
    ),
    22: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_22_schema_overlap_report_covers_every_object_and_dimension"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "overlap report covers every case method group unique lineage and "
                "required dimension with zero pending for complete state"
            ),
        },
    ),
    23: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_23_schema_refused_and_superseded_objects_remain_in_manifests"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": "refused and superseded objects remain in later manifests",
        },
    ),
    24: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_24_schema_forbidden_keys_reject_recursively"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "unknown forbidden keys are rejected recursively under every permitted "
                "nested container"
            ),
        },
    ),
    25: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_25_schema_runtime_locks_have_no_downstream_authorization"
            ),
            "owner": "Task 3",
            "task": "schema_contracts",
            "aspect": (
                "preflight and quantitative locks are distinct and contain no "
                "downstream authorization circularity"
            ),
        },
    ),
    26: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_26_schema_preflight_authorization_exact_scope_and_commands"
            ),
            "owner": "Task 3",
            "task": "schema_contracts",
            "aspect": (
                "preflight authorization has exact scope imports writers and tokenized "
                "command records"
            ),
            "labels": ("SCHEMA_REPRESENTABILITY_ONLY",),
        },
    ),
    27: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_27_schema_preflight_allowlist_guard"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "preflight source analyzer rejects hazardous imports calls and writers "
                "while governance validator remains import-guarded from any runner"
            ),
        },
    ),
    28: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_28_schema_preflight_results_reject_quantitative_fields"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "preflight result fixtures reject quantitative scoring summary "
                "output-root fields at every depth"
            ),
        },
    ),
    29: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_29_schema_every_preflight_case_is_terminal_or_incomplete"
            ),
            "owner": "Task 3",
            "task": "schema_contracts",
            "aspect": (
                "every declared preflight case is terminal or the batch is incomplete"
            ),
        },
    ),
    30: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_30_schema_terminal_partition_counts_reconcile"
            ),
            "owner": "Task 3",
            "task": "schema_contracts",
            "aspect": (
                "batch terminal sets are disjoint complete and counts hash-map keys "
                "match"
            ),
        },
    ),
    31: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_31_schema_certified_records_require_runtime_hashes"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": "certified records require all runtime hashes and estimand_id",
        },
    ),
    32: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_32_schema_exact_des_same_case_target_certificate_domain_metric"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "Exact and DES share one case target certificate domain hash and "
                "metric schema while retaining distinct method IDs"
            ),
        },
    ),
    33: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_33_schema_failed_control_blocks_quant_authorization"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": "failed mandatory control blocks quantitative authorization",
        },
    ),
    34: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_34_schema_quantitative_scope_rejects_implicit_expansion"
            ),
            "owner": "Task 3",
            "task": "schema_contracts",
            "aspect": (
                "quantitative authorization rejects wildcard implicit prefix glob null "
                "or expanded scope"
            ),
            "labels": ("SCHEMA_REPRESENTABILITY_ONLY",),
        },
    ),
    35: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_35_schema_failure_refusal_evidence_append_only"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": "failure refusal negative boundary evidence is append-only",
        },
    ),
    36: (
        {
            "test_id": (
                "tests/test_g6b_protocol.py::"
                "test_spec_17_3_36_schema_no_status_upgrade_from_intermediate_state"
            ),
            "owner": "Task 2",
            "task": "protocol_state_surface",
            "aspect": (
                "no schema normalization overlap or preflight state implies G6-B or "
                "later-stage status upgrade"
            ),
        },
    ),
    37: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_37_schema_g4_manifest_freeze_sets_reconcile_exactly"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "G4 manifest freeze path ID hash sets reconcile exactly with missing "
                "extra duplicate cross-ID wrong-base failures"
            ),
        },
    ),
    38: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_38_schema_subunits_reject_renamed_enclosing_ids"
            ),
            "owner": "Task 5",
            "task": "schema_contracts",
            "aspect": (
                "grid cells L30 inequalities and B05 monitors expand as deterministic "
                "parent-owned subunits"
            ),
        },
    ),
    39: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_39_schema_source_dimension_uses_exact_producer_row"
            ),
            "owner": "Task 3",
            "task": "schema_contracts",
            "aspect": "each retired dimension uses only its exact producer row",
        },
    ),
    40: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_40_schema_source_selector_grants_one_use_only"
            ),
            "owner": "Task 3",
            "task": "schema_contracts",
            "aspect": (
                "each source selector grants one use only and result streams never "
                "enter comparison projections"
            ),
        },
    ),
    41: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_41_schema_barrier_a_rejects_operation_and_role_drift"
            ),
            "owner": "Task 3",
            "task": "schema_contracts",
            "aspect": (
                "Barrier A rejects aliases wrong order schema role map cardinality "
                "drift and duplicate file ownership"
            ),
        },
    ),
    42: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_42_schema_refusal_code_unions_are_gate_specific"
            ),
            "owner": "Task 3",
            "task": "schema_contracts",
            "aspect": (
                "each gate accepts exactly cross-gate union named-gate refusal codes"
            ),
        },
    ),
    43: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_43_schema_overlap_lock_rejects_admin_identity_drift"
            ),
            "owner": "Task 3",
            "task": "schema_contracts",
            "aspect": (
                "overlap lock rejects branch dirty non-linked tree admin-hash "
                "privacy-path drift"
            ),
        },
    ),
    44: (
        {
            "test_id": (
                "tests/test_g6b_schema_contracts.py::"
                "test_spec_17_3_44_schema_command_manifest_hash_maps_and_placeholders"
            ),
            "owner": "Task 3",
            "task": "schema_contracts",
            "aspect": (
                "command manifests reconcile hashes maps placeholders environments and "
                "cannot reference downstream locks or authorizations"
            ),
        },
    ),
}


def _test_number(test_name: str) -> int:
    prefix = _SPEC_17_3_PREFIX
    assert test_name.startswith(prefix)
    number_text = test_name[len(prefix) : len(prefix) + 2]
    assert test_name[len(prefix) + 2 :].startswith("_schema_")
    return int(number_text)


def _test_id(path: Path, test_name: str) -> str:
    return f"{path.as_posix()}::{test_name}"


def _is_skip_or_xfail_decorator(decorator: ast.expr) -> bool:
    target = decorator.func if isinstance(decorator, ast.Call) else decorator
    if isinstance(target, ast.Attribute):
        parts: list[str] = []
        current: ast.expr = target
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts)) in {
            "pytest.mark.skip",
            "pytest.mark.skipif",
            "pytest.mark.xfail",
        }
    return isinstance(target, ast.Name) and target.id in {"skip", "skipif", "xfail"}


def _collect_spec_17_3_tests() -> tuple[list[tuple[str, int]], list[str]]:
    collected: list[tuple[str, int]] = []
    decorated: list[str] = []
    for path in _SPEC_17_3_TEST_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            if not node.name.startswith(_SPEC_17_3_PREFIX):
                continue
            if not node.name[len(_SPEC_17_3_PREFIX) + 2 :].startswith("_schema_"):
                continue
            test_id = _test_id(path, node.name)
            collected.append((test_id, _test_number(node.name)))
            if any(_is_skip_or_xfail_decorator(item) for item in node.decorator_list):
                decorated.append(test_id)
    return collected, decorated


def _collect_pytest_nodeids() -> set[str]:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            "--collect-only",
            "-q",
            *[path.as_posix() for path in _SPEC_17_3_TEST_FILES],
        ],
        check=False,
        env={
            **os.environ,
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": "src",
        },
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return {
        line
        for line in result.stdout.splitlines()
        if "::" in line and not line.startswith("<")
    }


def test_spec_17_3_requirement_manifest_status_and_collection_are_mechanical() -> None:
    assert set(_SPEC_17_3_REQUIREMENT_MANIFEST) == set(range(1, 45))
    assert set(_SPEC_17_3_STATUSES) == set(range(1, 45))
    for number, status in _SPEC_17_3_STATUSES.items():
        if number in {15, 27}:
            assert status == {
                "schema_tranche": "PASS_SCHEMA_GUARD_ONLY",
                "runtime_capability": "DEFERRED_REQUIRES_SEPARATE_GATE",
            }
        else:
            assert status == {
                "schema_tranche": "PASS_SCHEMA_TRANCHE",
                "runtime_capability": "NOT_REQUIRED_BY_THIS_SCHEMA_ITEM",
            }

    manifest_entries = [
        (number, entry)
        for number, entries in _SPEC_17_3_REQUIREMENT_MANIFEST.items()
        for entry in entries
    ]
    manifest_ids = [entry["test_id"] for _, entry in manifest_entries]
    assert len(manifest_ids) == len(set(manifest_ids))
    for number, entry in manifest_entries:
        assert entry["test_id"].startswith("tests/test_g6b_")
        assert f"::test_spec_17_3_{number:02d}_schema_" in entry["test_id"]
        assert entry["owner"]
        assert entry["task"]
        assert entry["aspect"]
        labels = entry.get("labels", ())
        if labels:
            assert labels == ("SCHEMA_REPRESENTABILITY_ONLY",)
            assert _SPEC_17_3_STATUSES[number]["runtime_capability"] != (
                "PASS_RUNTIME_CAPABILITY"
            )

    aspects_by_number = {
        number: {(entry["owner"], entry["aspect"]) for entry in entries}
        for number, entries in _SPEC_17_3_REQUIREMENT_MANIFEST.items()
    }
    for number, entries in _SPEC_17_3_REQUIREMENT_MANIFEST.items():
        assert len(aspects_by_number[number]) == len(entries)

    ast_collected, skip_or_xfail_ids = _collect_spec_17_3_tests()
    ast_collected_ids = [test_id for test_id, _number in ast_collected]
    ast_collected_numbers = {number for _test_id_value, number in ast_collected}
    duplicate_ast_ids = [
        test_id for test_id, count in Counter(ast_collected_ids).items() if count != 1
    ]

    pytest_nodeids = _collect_pytest_nodeids()
    uncollected_manifest_ids = [
        manifest_id
        for manifest_id in manifest_ids
        if manifest_id not in pytest_nodeids
        and not any(nodeid.startswith(f"{manifest_id}[") for nodeid in pytest_nodeids)
    ]
    errors = {
        "missing_requirement_numbers": sorted(
            set(range(1, 45)) - ast_collected_numbers
        ),
        "missing_manifest_ids_from_ast": sorted(
            set(manifest_ids) - set(ast_collected_ids)
        ),
        "orphan_ast_ids_not_in_manifest": sorted(
            set(ast_collected_ids) - set(manifest_ids)
        ),
        "duplicate_ast_ids": duplicate_ast_ids,
        "skip_skipif_xfail_ids": skip_or_xfail_ids,
        "manifest_ids_not_collected_by_pytest": uncollected_manifest_ids,
    }
    errors = {key: value for key, value in errors.items() if value}
    assert errors == {}, json.dumps(errors, indent=2, sort_keys=True)


def _task6_scope_policy_category(path: str) -> str | None:
    normalized = path.replace("\\", "/").removeprefix("./")
    exact_category = _TASK6_FORBIDDEN_EXACT_PATHS.get(normalized)
    if exact_category is not None:
        return exact_category
    if normalized in _R5_CASE_CONSTRUCTION_ARTIFACT_PATHS:
        return None
    for prefix, category in _TASK6_FORBIDDEN_PATH_PREFIXES:
        if normalized.startswith(prefix):
            return category
    if normalized not in _FINAL_SCHEMA_REVIEW_DECLARED_CHANGED_PATHS:
        return "outside_task6_declared_files"
    return None


def _task6_is_benign_ignored_path(path: str) -> bool:
    normalized = path.replace("\\", "/").removeprefix("./")
    if normalized.startswith(_TASK6_BENIGN_IGNORED_ROOT_PREFIXES):
        return True
    return "__pycache__" in normalized.split("/")


def _task6_changed_and_untracked_paths() -> list[str]:
    # This is a historical Task6/R1-R7 scope certificate. Pin both ends of
    # the reviewed range so later, separately authorized work does not change
    # the old guard's meaning or make the repository-wide suite fail.
    diff = subprocess.run(
        [
            "git",
            "diff",
            "--name-status",
            "--no-renames",
            _TASK5_SCHEMA_CODE_SUBJECT_COMMIT,
            _TASK6_SCOPE_SUBJECT_COMMIT,
            "--",
        ],
        cwd=_REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert diff.returncode == 0, diff.stdout + diff.stderr
    changed: list[str] = []
    for line in diff.stdout.splitlines():
        parts = line.split("\t")
        assert len(parts) == 2, f"unexpected git diff --name-status row: {line!r}"
        changed.append(parts[1])
    return sorted(set(changed))


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (".mypy_cache/3.13/src.data.json", True),
        (".pytest_cache/v/cache/nodeids", True),
        (".ruff_cache/0.14.4/123456", True),
        ("src/ims_deadlock/__pycache__/g6b.cpython-313.pyc", True),
        ("evidence/g6b/.pytest_cache_like_result.json", False),
        ("scratch/outside.json", False),
    ],
)
def test_task6_ignored_scope_policy_only_excludes_benign_cache_paths(
    path: str,
    expected: bool,
) -> None:
    assert _task6_is_benign_ignored_path(path) is expected


def test_task6_ignored_outside_declared_paths_remain_scope_violations() -> None:
    path = "scratch/outside.json"

    assert _task6_scope_policy_category(path) == "outside_task6_declared_files"
    assert not _task6_is_benign_ignored_path(path)


def test_task7_repair_scope_is_exact_and_keeps_future_capabilities_forbidden() -> None:
    assert _TASK7_REPAIR_DECLARED_CHANGED_PATHS == {
        "docs/verification/G6_B_AUTHORIZATION_GATE_REMEDIATION_REVIEW.md",
        "src/ims_deadlock/g6b_schema_contracts.py",
        "tests/test_g6b_schema_contracts.py",
        "tests/test_g6b_row_family_protocol.py",
    }
    assert all(
        _task6_scope_policy_category(path) is None
        for path in _TASK7_REPAIR_DECLARED_CHANGED_PATHS
    )
    assert (
        _task6_scope_policy_category("src/ims_deadlock/g6b_target_preflight.py")
        == "outside_task6_declared_files"
    )


def test_case_construction_plan_publication_scope_is_exact_and_plan_only() -> None:
    assert _CASE_CONSTRUCTION_PLAN_DECLARED_CHANGED_PATHS == {
        "docs/superpowers/plans/2026-08-02-g6b-case-construction.md",
        "docs/verification/G6_B_CASE_CONSTRUCTION_PLAN_REVIEW.md",
    }
    assert all(
        _task6_scope_policy_category(path) is None
        for path in _CASE_CONSTRUCTION_PLAN_DECLARED_CHANGED_PATHS
    )
    assert (
        _task6_scope_policy_category(
            "cases/discovery/g6b/row_families/structural_discovery_v1/"
            "governance/construction_authorization.json"
        )
        == "case_governance_instance_root"
    )


def test_r1_case_construction_schema_v3_scope_is_exact_schema_hash_closure() -> None:
    assert _R1_CASE_CONSTRUCTION_SCHEMA_V3_DECLARED_CHANGED_PATHS == {
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "case_construction_schema.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "row_family_protocol.json",
        "src/ims_deadlock/g6b_row_family_protocol.py",
        "src/ims_deadlock/g6b_schema_contracts.py",
        "tests/test_g6b_row_family_protocol.py",
        "tests/test_g6b_schema_contracts.py",
    }
    assert all(
        _task6_scope_policy_category(path) is None
        for path in _R1_CASE_CONSTRUCTION_SCHEMA_V3_DECLARED_CHANGED_PATHS
    )
    assert (
        _task6_scope_policy_category(
            "cases/discovery/g6b/row_families/structural_discovery_v1/"
            "case_units/case-01/case_input.json"
        )
        == "case_instance_root"
    )


def test_r4_case_construction_c2_source_identity_scope_is_exact() -> None:
    assert _R4_CASE_CONSTRUCTION_C2_SOURCE_IDENTITY_PATHS == {
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "case_construction_schema.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "row_family_protocol.json",
        "docs/verification/G6_B_CASE_CONSTRUCTION_TASK2_SOURCE_REVIEW.md",
        "src/ims_deadlock/g6b_case_materializer.py",
        "src/ims_deadlock/g6b_row_family_protocol.py",
        "src/ims_deadlock/g6b_schema_contracts.py",
        "tests/test_g6b_case_materializer.py",
        "tests/test_g6b_row_family_protocol.py",
        "tests/test_g6b_schema_contracts.py",
    }
    assert all(
        _task6_scope_policy_category(path) is None
        for path in _R4_CASE_CONSTRUCTION_C2_SOURCE_IDENTITY_PATHS
    )
    assert (
        _task6_scope_policy_category(
            "cases/discovery/g6b/row_families/structural_discovery_v1/"
            "case_units/case-01/case_input.json"
        )
        == "case_instance_root"
    )
    assert (
        _task6_scope_policy_category(
            "cases/discovery/g6b/row_families/structural_discovery_v1/"
            "governance/case_construction_v2.json"
        )
        == "case_governance_instance_root"
    )
    assert (
        _task6_scope_policy_category("src/ims_deadlock/g6b_quantitative_runner.py")
        == "outside_task6_declared_files"
    )
    assert (
        _task6_scope_policy_category("src/ims_deadlock/g6b_target_preflight.py")
        == "outside_task6_declared_files"
    )
    assert (
        _task6_scope_policy_category("artifacts/g6b/quantitative/result.json")
        == "scientific_artifact_root"
    )
    assert (
        _task6_scope_policy_category("src/ims_deadlock/g6b_future_module.py")
        == "outside_task6_declared_files"
    )


def test_case_construction_v2_governance_scope_is_exact_and_plan_only() -> None:
    assert _CASE_CONSTRUCTION_V2_GOVERNANCE_DECLARED_CHANGED_PATHS == {
        "docs/superpowers/specs/"
        "2026-08-02-g6b-case-construction-materialization-contract-corrigendum.md",
        "docs/superpowers/plans/2026-08-02-g6b-case-construction-v2.md",
        "docs/verification/G6_B_CASE_CONSTRUCTION_V2_PLAN_REVIEW.md",
    }
    assert all(
        _task6_scope_policy_category(path) is None
        for path in _CASE_CONSTRUCTION_V2_GOVERNANCE_DECLARED_CHANGED_PATHS
    )
    assert (
        _task6_scope_policy_category(
            "cases/discovery/g6b/row_families/structural_discovery_v1/"
            "governance/case_construction_v2.json"
        )
        == "case_governance_instance_root"
    )


def test_task1_estimand_scope_corrigendum_scope_is_exact_and_schema_only() -> None:
    assert _TASK1_ESTIMAND_SCOPE_CORRIGENDUM_DECLARED_CHANGED_PATHS == {
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "case_construction_schema.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/identity_schema.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "retired_authority_fingerprint_schema.json",
        "docs/superpowers/specs/"
        "2026-08-02-g6b-case-construction-estimand-scope-corrigendum.md",
        "src/ims_deadlock/g6b_row_family_protocol.py",
        "src/ims_deadlock/g6b_schema_contracts.py",
        "tests/test_g6b_row_family_protocol.py",
        "tests/test_g6b_schema_contracts.py",
    }
    assert all(
        _task6_scope_policy_category(path) is None
        for path in _TASK1_ESTIMAND_SCOPE_CORRIGENDUM_DECLARED_CHANGED_PATHS
    )
    assert "src/ims_deadlock/g6b_case_materializer.py" not in (
        _TASK1_ESTIMAND_SCOPE_CORRIGENDUM_DECLARED_CHANGED_PATHS
    )
    assert "tests/test_g6b_case_materializer.py" not in (
        _TASK1_ESTIMAND_SCOPE_CORRIGENDUM_DECLARED_CHANGED_PATHS
    )
    assert (
        _task6_scope_policy_category(
            "cases/discovery/g6b/row_families/structural_discovery_v1/"
            "governance/g6b_discovery_case_construction_v1/"
            "unapproved.json"
        )
        == "case_governance_instance_root"
    )


def test_task1_review_publication_scope_is_exact_and_document_only() -> None:
    assert _TASK1_REVIEW_PUBLICATION_DECLARED_CHANGED_PATHS == {
        "PROJECT_HANDOFF.md",
        "docs/ROADMAP.md",
        "docs/verification/G6_B_CASE_CONSTRUCTION_ESTIMAND_SCOPE_CORRIGENDUM_REVIEW.md",
    }
    assert all(
        _task6_scope_policy_category(path) is None
        for path in _TASK1_REVIEW_PUBLICATION_DECLARED_CHANGED_PATHS
    )
    assert (
        "src/ims_deadlock/g6b_case_materializer.py"
        not in _TASK1_REVIEW_PUBLICATION_DECLARED_CHANGED_PATHS
    )
    assert (
        "tests/test_g6b_case_materializer.py"
        not in _TASK1_REVIEW_PUBLICATION_DECLARED_CHANGED_PATHS
    )
    assert (
        _task6_scope_policy_category(
            "cases/discovery/g6b/row_families/structural_discovery_v1/"
            "governance/g6b_discovery_case_construction_v1/"
            "unapproved.json"
        )
        == "case_governance_instance_root"
    )
    assert (
        _task6_scope_policy_category("artifacts/g6b/quantitative/result.json")
        == "scientific_artifact_root"
    )


@pytest.mark.parametrize(
    ("path", "expected_category"),
    [
        (
            "cases/confirmation/g4/FREEZE_ENTRY.json",
            "retired_g4_evidence",
        ),
        ("evidence/g5/G5_RESULT_SUMMARY.json", "retired_g5_evidence"),
        (
            "evidence/g6/G6_HISTORICAL_REPLAY_R3_REPORT.json",
            "retired_g6r_evidence",
        ),
        (
            "evidence/g6b/target_certification/case.json",
            "target_certification_evidence",
        ),
        ("artifacts/g6b/quantitative/result.json", "scientific_artifact_root"),
        (
            (
                "cases/discovery/g6b/row_families/structural_discovery_v1/"
                "governance/authorization.json"
            ),
            "case_governance_instance_root",
        ),
        (
            (
                "cases/discovery/g6b/row_families/structural_discovery_v1/"
                "case_units/case.json"
            ),
            "case_instance_root",
        ),
        (
            (
                "docs/superpowers/specs/"
                "2026-08-01-g6b-case-target-certification-design.md"
            ),
            "approved_specification",
        ),
        ("src/ims_deadlock/g6b_quantitative_runner.py", "outside_task6_declared_files"),
    ],
)
def test_task6_diff_scope_policy_rejects_forbidden_paths(
    path: str,
    expected_category: str,
) -> None:
    assert _task6_scope_policy_category(path) == expected_category


def test_r5_exact_artifact_scope_is_allowed_without_widening_prefixes() -> None:
    authorized_paths = _R5_CASE_CONSTRUCTION_ARTIFACT_PATHS
    case_file_paths = {path for path in authorized_paths if "/case_units/" in path}
    governance_paths = {path for path in authorized_paths if "/governance/" in path}
    category_by_path = {
        path: _task6_scope_policy_category(path) for path in sorted(authorized_paths)
    }

    assert len(authorized_paths) == 394
    assert len(case_file_paths) == 390
    assert len(governance_paths) == 4
    assert case_file_paths | governance_paths == authorized_paths
    assert category_by_path == {path: None for path in sorted(authorized_paths)}
    assert (
        _task6_scope_policy_category(
            "cases/discovery/g6b/row_families/structural_discovery_v1/"
            "case_units/near_miss/case_input.json"
        )
        == "case_instance_root"
    )
    assert (
        _task6_scope_policy_category(
            "cases/discovery/g6b/row_families/structural_discovery_v1/"
            "governance/near_miss/construction_log.json"
        )
        == "case_governance_instance_root"
    )


def test_task6_git_diff_scope_excludes_science_and_capability_surfaces() -> None:
    changed_paths = _task6_changed_and_untracked_paths()
    assert changed_paths
    assert "docs/verification/G6_B_CASE_TARGET_SCHEMA_V2_REVIEW.md" in changed_paths
    violations = [
        (path, category)
        for path in changed_paths
        if (category := _task6_scope_policy_category(path)) is not None
    ]
    assert violations == [], violations[0] if violations else None
