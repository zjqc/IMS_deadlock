from __future__ import annotations

from types import MappingProxyType
from typing import Any

import pytest

from ims_deadlock import g6b_schema_contracts as contracts
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
    validate_exact_keys,
    validate_file_role_cardinality,
    validate_refusal_codes,
    validate_source_pointer_use,
    validate_subject_free_projection,
    validate_typed_capabilities,
)

JsonObject = dict[str, Any]


def _valid_command_record(command_id: str = "cmd-preflight") -> JsonObject:
    return {
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
        "command_record_sha256": "2" * 64,
    }


def _valid_command_manifest() -> tuple[JsonObject, dict[str, JsonObject]]:
    command = _valid_command_record()
    return (
        {
            "schema_version": (
                "ims-deadlock/g6b-preflight-allowed-command-manifest/v1"
            ),
            "manifest_id": "manifest-a",
            "capability": "target_certification_preflight",
            "source_head": "a" * 40,
            "source_tree_hash": "b" * 40,
            "sealed_bundle_manifest_hash": "3" * 64,
            "input_overlap_report_sha256": "4" * 64,
            "preflight_evidence_root_reservation_sha256": "5" * 64,
            "declared_command_ids": ["cmd-preflight"],
            "command_record_hashes": {"cmd-preflight": "2" * 64},
            "command_count": 1,
            "placeholder_vocabulary": list(contracts.PREFLIGHT_PLACEHOLDER_CODES),
            "environment_variable_name_allowlist": [
                "PYTHONDONTWRITEBYTECODE",
                "PYTHONPATH",
            ],
            "wildcard_scope_allowed": False,
            "created_at_utc": "2026-08-01T00:00:00Z",
            "manifest_sha256": "6" * 64,
        },
        {"cmd-preflight": command},
    )


def _valid_quantitative_command_record(
    command_id: str = "cmd-quantitative",
) -> JsonObject:
    return {
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
        "authorized_method_observation_ids": ["method-a"],
        "authorized_run_roles": ["primary"],
        "authorized_output_root_reservation_hashes": {"method-a": "1" * 64},
        "command_record_sha256": "2" * 64,
    }


def _valid_quantitative_command_manifest() -> tuple[JsonObject, dict[str, JsonObject]]:
    command = _valid_quantitative_command_record()
    return (
        {
            "schema_version": (
                "ims-deadlock/g6b-quantitative-allowed-command-manifest/v1"
            ),
            "manifest_id": "manifest-q",
            "capability": "quantitative_execution",
            "source_head": "a" * 40,
            "source_tree_hash": "b" * 40,
            "sealed_bundle_manifest_hash": "3" * 64,
            "target_certification_batch_manifest_hash": "4" * 64,
            "authorized_scope_sha256": "5" * 64,
            "same_target_lock_hashes": {"case-a": "6" * 64},
            "output_root_reservation_hashes": {"method-a": "1" * 64},
            "declared_command_ids": ["cmd-quantitative"],
            "command_record_hashes": {"cmd-quantitative": "2" * 64},
            "command_count": 1,
            "placeholder_vocabulary": list(contracts.QUANTITATIVE_PLACEHOLDER_CODES),
            "environment_variable_name_allowlist": [
                "PYTHONDONTWRITEBYTECODE",
                "PYTHONPATH",
            ],
            "wildcard_scope_allowed": False,
            "created_at_utc": "2026-08-01T00:00:00Z",
            "manifest_sha256": "7" * 64,
        },
        {"cmd-quantitative": command},
    )


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
    validate_refusal_codes("ledger", ["self_hash_mismatch"])
    with pytest.raises(SchemaContractError, match="wrong_gate_refusal_code"):
        validate_refusal_codes("construction", ["certificate_schema_violation"])
    with pytest.raises(SchemaContractError, match="wrong_gate_refusal_code"):
        validate_refusal_codes("normalization_overlap", ["state_bound_truncation"])
    with pytest.raises(SchemaContractError, match="wrong_gate_refusal_code"):
        validate_refusal_codes("preflight", ["quantitative_scope_violation"])
    with pytest.raises(SchemaContractError, match="wrong_gate_refusal_code"):
        validate_refusal_codes("quantitative", ["overlap_hit"])
    with pytest.raises(SchemaContractError, match="wrong_gate_refusal_code"):
        validate_refusal_codes("ledger", ["overlap_hit"])
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
