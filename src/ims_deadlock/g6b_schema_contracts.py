"""Pure closed-vocabulary validators for G6-B schema contracts."""

from __future__ import annotations

from collections import Counter
from collections.abc import Collection, Mapping, Sequence
from types import MappingProxyType
from typing import Literal, TypeAlias

JsonValue: TypeAlias = (
    None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
)


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
    allowed = set(CROSS_GATE_REFUSAL_CODES).union(group_by_gate[gate])
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
    hashes = manifest.get("command_record_hashes")
    if not isinstance(hashes, Mapping) or set(hashes) != set(command_ids):
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
        if record.get("command_record_sha256") != hashes[command_id]:
            raise SchemaContractError("command_hash_map_mismatch")
        _validate_tokens(record.get("argv_tokens"), placeholders)
        _validate_environment(
            record.get("environment_variable_allowlist"), placeholders
        )
        _reject_wildcard_scope(record.get("authorized_case_unit_ids"))
        _reject_wildcard_scope(record.get("authorized_method_observation_ids"))
        _reject_wildcard_scope(record.get("authorized_run_roles"))
        if capability == "quantitative_execution":
            quantitative_case_ids.update(
                _as_string_sequence(
                    record.get("authorized_case_unit_ids"),
                    "authorized_case_unit_ids",
                )
            )
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
        if row.get("source_path_pattern") != source_path:
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
        result[key] = item
    return result


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
