"""Data-only structural validation for the G6-B discovery protocol bundle."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

from ims_deadlock.g6b_canonical_json import (
    CanonicalJsonError,
    canonical_sha256_v2,
    loads_v2,
)

G6B_PROTOCOL_SCHEMA_VERSION = "ims-deadlock/g6b-discovery-protocol/v2"
G6B_ESTIMAND_SCHEMA_VERSION = "ims-deadlock/g6b-estimand-schema/v2"
G6B_INDEPENDENCE_SCHEMA_VERSION = "ims-deadlock/g6b-independence-schema/v2"
G6B_NEGATIVE_CONTROLS_VERSION = "ims-deadlock/g6b-negative-controls/v1"
G6B_FAILURE_LEDGER_VERSION = "ims-deadlock/g6b-failure-ledger/v1"

_DOCUMENTS = (
    "protocol.json",
    "estimand_schema.json",
    "independence_schema.json",
    "negative_controls.json",
    "failure_ledger.json",
)
_CANONICAL_V2_DOCUMENTS = frozenset({"protocol.json", "independence_schema.json"})
JsonObject: TypeAlias = dict[str, Any]
_PROTOCOL_KEYS = {
    "schema_version",
    "protocol_id",
    "study_role",
    "confirmation_use",
    "scientific_execution_authorized",
    "adversarial_review_status",
    "artifact_paths",
    "tracked_historical_authorities",
    "typed_capability_vocabulary",
    "current_row_family_capability_reference",
    "execution_boundary",
    "orthogonal_scoring_layers",
}
_COMMON_KEYS = {
    "schema_version",
    "study_role",
    "confirmation_use",
    "scientific_execution_authorized",
}
_ARTIFACT_PATHS = [
    "docs/cases/G6_B_DISCOVERY_PROTOCOL.md",
    "cases/discovery/g6b/estimand_schema.json",
    "cases/discovery/g6b/independence_schema.json",
    "cases/discovery/g6b/negative_controls.json",
    "cases/discovery/g6b/failure_ledger.json",
]
_HISTORICAL_AUTHORITIES = [
    "cases/confirmation/g4/FREEZE_ENTRY.json",
    "cases/confirmation/g4/case_manifest.json",
    "cases/confirmation/g4/random_stream_manifest.json",
    "cases/confirmation/g4/predictions.json",
    "cases/confirmation/g4/metrics_schema.json",
    "evidence/g5/G5_EXECUTION_LOCK.json",
    "evidence/g5/G5_RAW_HASH_MANIFEST.json",
    "evidence/g5/G5_RESULT_SUMMARY.json",
    "evidence/g5/G5_SCORING_ERRATUM.json",
    "evidence/g6/G6_HISTORICAL_REPLAY_FAILURE_LEDGER.json",
    "evidence/g6/G6_HISTORICAL_REPLAY_R3_REPORT.json",
]
_REMOTE_ONLY_HISTORICAL_AUTHORITIES = {
    "evidence/g5/G5_RAW_HASH_MANIFEST.json",
    "evidence/g5/G5_RESULT_SUMMARY.json",
}
_TYPED_CAPABILITY_VOCABULARY = [
    "case_construction_authorized",
    "retired_authority_fingerprint_normalization_authorized",
    "target_certification_preflight_authorized",
    "quantitative_execution_authorized",
]
_ROW_FAMILY_CAPABILITY_REFERENCE = (
    "row_families/structural_discovery_v1/row_family_protocol.json#/typed_capabilities"
)
_SELECTED_STOPPING_TARGETS = {
    "bad_hit_sets": ["D_global", "D_local"],
    "success_class": "F",
}
_UNSELECTED_PLANT_TERMINAL_CLASSES = [
    "R_livelock",
    "R_terminal",
]
_POLICY_ANALYSIS_CLASS = {
    "label": "P_policy",
    "plant_partition_member": False,
    "selectable_target": False,
}
_DERIVED_STATE_SETS = {
    "S_reach": {
        "definition": "complete_stopped_lts_support_reachability",
        "role": "diagnostic_only",
        "selectable_target": False,
    },
    "S_T": {
        "definition": (
            "probability_one_hit_selected_target_in_finite_positive_rate_stopped_ctmc"
        ),
        "role": "certified_absorption_domain",
        "selectable_target": False,
    },
}
_D_LOCAL_ONTOLOGY = {
    "ontology": "first_hit_bad_set_not_terminal_scc",
    "definition": (
        "verified first-hit bad set selected by the G6-B estimand, "
        "not a plant terminal SCC"
    ),
    "admission": [
        "A2b_proof",
        "complete_LTS_completion_nonreachability_audit",
    ],
}
_TYPED_ONTOLOGY = {
    "selected_stopping_targets": _SELECTED_STOPPING_TARGETS,
    "unselected_plant_terminal_classes": _UNSELECTED_PLANT_TERMINAL_CLASSES,
    "policy_analysis_class": _POLICY_ANALYSIS_CLASS,
    "derived_state_sets": _DERIVED_STATE_SETS,
    "D_local": _D_LOCAL_ONTOLOGY,
}
_FUTURE_HASHES = [
    "state_space_hash",
    "partition_hash",
    "rate_manifest_hash",
    "positive_rate_graph_hash",
    "policy_filter_hash",
    "absorption_domain_hash",
    "stopping_rule_hash",
    "des_stopping_rule_hash",
    "estimand_id",
]
_DIMENSIONS = [
    "case_content_sha256",
    "state_snapshot_sha256",
    "route_signature_sha256",
    "parameter_tuple_sha256",
    "random_stream_manifest_sha256",
    "output_root_reservation_sha256",
    "sealed_prediction_sha256",
    "metric_schema_sha256",
]
_FUTURE_CONFIRMATION_DIMENSIONS = [
    "case_content_sha256",
    "state_snapshot_sha256",
    "route_signature_sha256",
    "parameter_tuple_sha256",
    "random_stream_manifest_sha256",
    "output_root_reservation_sha256",
    "sealed_prediction_sha256",
]
_FINGERPRINT_SUBJECT_MAP = {
    "case_content_sha256": "case_unit",
    "state_snapshot_sha256": "case_unit",
    "route_signature_sha256": "case_unit",
    "parameter_tuple_sha256": "case_unit",
    "random_stream_manifest_sha256": "method_observation",
    "output_root_reservation_sha256": "method_observation",
    "sealed_prediction_sha256": "case_unit",
    "metric_schema_sha256": "method_companion_group",
}
_FINGERPRINT_POLICY_MAP = {
    "case_content_sha256": "strict_semantic_distinctness",
    "state_snapshot_sha256": "strict_semantic_distinctness",
    "route_signature_sha256": "strict_semantic_distinctness",
    "parameter_tuple_sha256": "strict_semantic_distinctness",
    "random_stream_manifest_sha256": "disjoint_random_substreams",
    "output_root_reservation_sha256": "provenance_containment_only",
    "sealed_prediction_sha256": "strict_semantic_distinctness",
    "metric_schema_sha256": "controlled_schema_reuse",
}
_ALLOWED_CLAIM_PREDICATES = [
    "canonical_byte_distinctness",
    "provenance_nonreuse",
    "semantic_non_derivation",
    "construction_process_separation",
    "mechanism_diversity",
    "random_process_independence",
    "confirmation_blinding",
    "bounded_nonreuse_admission",
]
_CANONICALIZATION_CONTRACT = {
    "version": "ims-deadlock/g6b-canonical-json/v2",
    "duplicate_members": "rejected_at_every_depth",
    "unicode_normalization": {
        "required_form": "NFC",
        "silent_normalization": False,
        "scope": ["member_names", "string_values"],
    },
    "object_key_order": "unicode_code_point",
    "array_order_policy": {
        "ordinary_arrays": "preserve_declared_order",
        "set_like_arrays": "unique_and_already_sorted_when_schema_declared",
    },
    "utf8_serialization": {
        "encoding": "utf-8",
        "ensure_ascii": False,
        "sort_keys": True,
        "separators": [",", ":"],
        "allow_nan": False,
    },
    "numeric_policy": {
        "json_float_values": "prohibited",
        "nan": "prohibited",
        "infinity": "prohibited",
        "negative_zero": "prohibited",
        "integers": "json_integers_for_counts_and_integral_budgets",
        "decimal_strings_regex": "^-?(0|[1-9][0-9]*)(\\.[0-9]*[1-9])?$",
        "historical_json_numbers": "exact_decimal_token_no_binary_float",
    },
    "path_policy": {
        "format": "case_sensitive_repo_relative_posix",
        "separator": "/",
        "drive_letter": "prohibited",
        "leading_slash": "prohibited",
        "backslash": "prohibited",
        "empty_component": "prohibited",
        "dot_or_dotdot": "prohibited",
        "symlink_dependent_resolution": "prohibited",
        "runtime_executables": "logical_id_plus_byte_environment_hashes",
    },
    "timestamp_policy": {
        "utc": "fixed_rfc3339_z",
        "format": "YYYY-MM-DDTHH:MM:SSZ",
    },
}
_SELF_HASH_FINALIZATION_CONTRACT = {
    "version": "ims-deadlock/g6b-self-hash-finalization/v1",
    "placeholder_value": None,
    "replaced_field_count": 1,
    "omitted_field_allowed": False,
    "empty_string_placeholder_allowed": False,
    "prepopulated_digest_allowed": False,
    "excluded_field_escape_hatch_allowed": False,
    "cross_record_reference_order": "upstream_records_finalized_first",
    "digest_algorithm": "sha256",
    "digest_encoding": "lowercase_hex",
}
_SUBJECT_FREE_PROJECTION_EXCLUDES = [
    "bundle_id",
    "case_unit_id",
    "method_observation_id",
    "method_companion_group_id",
    "filenames",
    "repo_paths",
    "display_names",
    "authors",
    "timestamps",
    "review_ids",
    "new_g6b_provenance_labels",
]
_FINGERPRINT_RECORD_REQUIRED_FIELDS = [
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
]
_RECORDED_CONTEXTS = [
    "subject",
    "authority",
    "stage",
    "lineage",
    "sources",
    "derivation",
]
_TYPED_ADMISSION_CONTRACT = {
    "version": "ims-deadlock/g6b-typed-admission-contract/v1",
    "schema_tranche_role": "top_level_summary_only",
    "full_machine_contract_reference": (
        "row_families/structural_discovery_v1/"
        "retired_authority_fingerprint_schema.json#/typed_admission_contract"
    ),
    "summary_does_not_establish_admission": True,
    "replaces_unconditional_zero_overlap": True,
    "semantic_projection_dimensions": [
        "case_content_sha256",
        "state_snapshot_sha256",
        "route_signature_sha256",
        "parameter_tuple_sha256",
        "sealed_prediction_sha256",
    ],
    "semantic_projection_required_status": "pass_distinct",
    "semantic_projection_scope": "every_comparable_unique_retired_lineage",
    "semantic_lineage_audit_required": True,
    "stochastic_random_stream_record_requires": "disjoint_stream_pass",
    "exact_random_stream_record_requires": "not_applicable_by_protocol_pass",
    "output_root_reservation_requires": "containment_separation_pass",
    "metric_schema_requires_one_of": ["pass_distinct", "controlled_reuse_pass"],
    "controlled_metric_reuse_requires_exact_record": True,
    "controlled_metric_reuse_requires_companion_group_comparability_rationale": True,
    "fail_closed_statuses": [
        "overlap_hit",
        "missing_source",
        "unreconstructable",
        "normalizer_error",
        "semantic_lineage_ambiguous",
    ],
    "inherited_compared_requires_unique_ancestor_allowed_terminal_status": True,
    "retired_alias_lineage_compared_once": True,
    "retired_aliases_count_as_independent_authorities": False,
    "admission_rule": "bounded_lineage_deduplicated_nonreuse",
    "non_authorization_boundary": (
        "schema_review_and_overlap_preflight_do_not_authorize_scientific_or_"
        "quantitative_execution"
    ),
    "result_field_prohibition": "no_generic_independent_result",
}
_NONREUSE_CLAIM_LATTICE = {
    "version": "ims-deadlock/g6b-nonreuse-claim-lattice/v1",
    "claim_boundary": "predicates_remain_separate_no_status_upgrade",
    "byte_distinctness_not_statistical_independence": True,
    "output_root_not_case_identity": True,
    "bounded_admission_not_eight_observations": True,
}
_COMPARISON_PROJECTION_CONTRACT = {
    "version": "ims-deadlock/g6b-comparison-projection-contract/v1",
    "subject_free_projection_kinds": [
        "semantic_content",
        "random_process",
        "controlled_schema",
    ],
    "provenance_containment_logical_coordinates_allowed": True,
    "provenance_containment_supports_semantic_distinctness": False,
    "governance_only_changes_leave_subject_free_projection_unchanged": True,
    "subject_free_projection_excludes": _SUBJECT_FREE_PROJECTION_EXCLUDES,
    "unequal_record_provenance_hash_does_not_support_non_overlap": True,
    "counting_rule": (
        "exact_des_companions_share_one_case_unit_and_distinct_method_observations"
    ),
}
_PROVENANCE_ENVELOPE_CONTRACT = {
    "version": "ims-deadlock/g6b-provenance-envelope-contract/v1",
    "envelope_scope": "artifact_lineage_locks_paths_and_reservations",
    "applicable_subject_ids_required": True,
    "recorded_contexts": _RECORDED_CONTEXTS,
    "fingerprint_record_required_fields": _FINGERPRINT_RECORD_REQUIRED_FIELDS,
    "separate_from_comparison_projection": True,
    "unequal_envelope_hash_does_not_support_non_overlap": True,
    "confirmation_boundary": "future_confirmation_tranche_only",
}
_FORBIDDEN_STATUS_UPGRADE_PHRASES = (
    "g6-b passed",
    "g6b passed",
    "g6-c passed",
    "g6c passed",
    "g6-d passed",
    "g6d passed",
    "g6-e passed",
    "g6e passed",
    "confirmed for g6-c",
    "eight independent dimensions",
    "two independent cases",
)
_SCORING_LAYERS = [
    "theorem_prediction_status",
    "metric_applicability",
    "metric_observations",
    "execution_status",
    "reproducibility_status",
]
_NEGATIVE_CONTROL_IDS = [
    "NC_LOCAL_BYPASS_COMPLETES",
    "NC_UNSELECTED_LIVELOCK",
    "NC_CALENDAR_EMPTY_TERMINAL",
    "NC_POLICY_ONLY_STALL",
    "NC_OR_OF_AND_FEASIBLE_BRANCH",
    "NC_AGV_RESERVATION_BOUNDARY",
    "NC_DGLOBAL_ONLY_WITH_DLOCAL",
]
_NEGATIVE_CONTROLS = [
    {
        "id": "NC_LOCAL_BYPASS_COMPLETES",
        "expected_classification": "D_local_not_admitted",
        "expected_refusal": "reachable_completion_bypass",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_UNSELECTED_LIVELOCK",
        "expected_classification": "R_livelock",
        "expected_refusal": "not_selected_bad_class",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_CALENDAR_EMPTY_TERMINAL",
        "expected_classification": "R_terminal",
        "expected_refusal": "not_resource_deadlock",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_POLICY_ONLY_STALL",
        "expected_classification": "P_policy",
        "expected_refusal": "policy_only_not_plant_partition",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_OR_OF_AND_FEASIBLE_BRANCH",
        "expected_classification": "D_local_not_admitted",
        "expected_refusal": "feasible_branch_exists",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_AGV_RESERVATION_BOUNDARY",
        "expected_classification": "boundary_or_new_versioned_target_required",
        "expected_refusal": "semantic_boundary_changed",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_DGLOBAL_ONLY_WITH_DLOCAL",
        "expected_classification": "D_global",
        "expected_refusal": "no_double_count_through_D_local",
        "not_support_if_failed": True,
    },
]


@dataclass(frozen=True)
class G6BProtocolValidation:
    valid: bool
    errors: tuple[str, ...]
    scientific_execution_authorized: bool
    adversarial_review_status: str
    bundle_hashes: dict[str, str]


def validate_g6b_protocol_bundle(root: Path) -> G6BProtocolValidation:
    """Validate the G6-B protocol foundation without scientific execution."""

    bundle_root = root.resolve()
    documents: dict[str, JsonObject] = {}
    bundle_hashes: dict[str, str] = {}
    errors: list[str] = []
    actual_json_names = sorted(
        path.name for path in bundle_root.glob("*.json") if path.is_file()
    )
    expected_names = set(_DOCUMENTS)
    actual_names = set(actual_json_names)
    missing_names = sorted(expected_names - actual_names)
    unexpected_names = sorted(actual_names - expected_names)
    if missing_names:
        errors.append(f"missing JSON documents: {missing_names}")
    if unexpected_names:
        errors.append(f"unexpected JSON documents: {unexpected_names}")

    for name in _DOCUMENTS:
        if name in missing_names:
            continue
        path = bundle_root / name
        use_canonical_v2 = name in _CANONICAL_V2_DOCUMENTS
        try:
            document = _load_document_object(path, use_canonical_v2=use_canonical_v2)
        except ValueError as exc:
            errors.append(f"{name}: {exc}")
            continue
        documents[name] = document
        bundle_hashes[name] = _document_sha256(
            document, use_canonical_v2=use_canonical_v2
        )

    if set(documents) == set(_DOCUMENTS):
        repo_root = _repo_root_for(bundle_root)
        if repo_root is None:
            errors.append("bundle root must be <repo>/cases/discovery/g6b")
            repo_root = bundle_root
        _validate_protocol(documents["protocol.json"], repo_root, errors)
        _validate_estimand(documents["estimand_schema.json"], errors)
        _validate_independence(documents["independence_schema.json"], errors)
        _validate_negative_controls(documents["negative_controls.json"], errors)
        _validate_failure_ledger(documents["failure_ledger.json"], errors)

    protocol = documents.get("protocol.json", {})
    scientific_execution_authorized = any(
        document.get("scientific_execution_authorized") is True
        for document in documents.values()
    )
    return G6BProtocolValidation(
        valid=not errors,
        errors=tuple(errors),
        scientific_execution_authorized=scientific_execution_authorized,
        adversarial_review_status=str(protocol.get("adversarial_review_status", "")),
        bundle_hashes=bundle_hashes,
    )


def _validate_protocol(
    document: JsonObject, repo_root: Path, errors: list[str]
) -> None:
    _exact_keys(document, _PROTOCOL_KEYS, "protocol.json", errors)
    _common_contract(
        document,
        "protocol.json",
        G6B_PROTOCOL_SCHEMA_VERSION,
        errors,
    )
    _expect(
        document.get("protocol_id"),
        "G6-B-DISCOVERY-PROTOCOL-FOUNDATION",
        "protocol.json: protocol_id",
        errors,
    )
    _expect(
        document.get("adversarial_review_status"),
        "PENDING",
        "protocol.json: adversarial_review_status",
        errors,
    )
    if document.get("scientific_execution_authorized") is True:
        errors.append(
            "protocol.json: scientific execution true while review is PENDING"
        )
    _expect_path_list(
        document.get("artifact_paths"),
        _ARTIFACT_PATHS,
        "protocol.json: artifact_paths",
        repo_root,
        required_existing=set(_ARTIFACT_PATHS),
        errors=errors,
    )
    _expect_path_list(
        document.get("tracked_historical_authorities"),
        _HISTORICAL_AUTHORITIES,
        "protocol.json: tracked_historical_authorities",
        repo_root,
        required_existing=(
            set(_HISTORICAL_AUTHORITIES) - _REMOTE_ONLY_HISTORICAL_AUTHORITIES
        ),
        errors=errors,
    )
    _expect(
        document.get("typed_capability_vocabulary"),
        _TYPED_CAPABILITY_VOCABULARY,
        "protocol.json: typed_capability_vocabulary",
        errors,
    )
    _expect(
        document.get("current_row_family_capability_reference"),
        _ROW_FAMILY_CAPABILITY_REFERENCE,
        "protocol.json: current_row_family_capability_reference",
        errors,
    )
    _expect(
        document.get("execution_boundary"),
        {
            "creates_cases": False,
            "authorizes_enumeration": False,
            "authorizes_ctmc_solve": False,
            "authorizes_des_run": False,
            "requires_adversarial_review_before_scientific_execution": True,
        },
        "protocol.json: execution_boundary",
        errors,
    )
    _expect(
        document.get("orthogonal_scoring_layers"),
        {
            "required_layers": _SCORING_LAYERS,
            "metric_failure_changes_theorem_status": False,
            "exception": "only_if_frozen_falsifier_explicitly_references_metric",
        },
        "protocol.json: orthogonal_scoring_layers",
        errors,
    )


def _validate_estimand(document: JsonObject, errors: list[str]) -> None:
    _exact_keys(
        document,
        _COMMON_KEYS | {"future_required_hashes", "ontology", "exact_des_consistency"},
        "estimand_schema.json",
        errors,
    )
    _common_contract(
        document,
        "estimand_schema.json",
        G6B_ESTIMAND_SCHEMA_VERSION,
        errors,
    )
    _expect(
        document.get("future_required_hashes"),
        _FUTURE_HASHES,
        "estimand_schema.json: future_required_hashes",
        errors,
    )
    ontology = document.get("ontology")
    if not isinstance(ontology, dict):
        errors.append("estimand_schema.json: ontology must be an object")
    else:
        _expect(
            ontology,
            _TYPED_ONTOLOGY,
            "estimand_schema.json: ontology",
            errors,
        )
    _expect(
        document.get("exact_des_consistency"),
        {
            "same_target_required": True,
            "same_selected_bad_labels_required": True,
            "same_selected_success_label_required": True,
            "same_versioned_target_required": True,
            "certified_absorption_domain_required": True,
            "same_absorption_domain_hash_required": True,
        },
        "estimand_schema.json: exact_des_consistency",
        errors,
    )


def _validate_independence(document: JsonObject, errors: list[str]) -> None:
    _exact_keys(
        document,
        _COMMON_KEYS
        | {
            "canonicalization_contract",
            "self_hash_finalization_contract",
            "dimensions",
            "fingerprint_subject_map",
            "fingerprint_policy_map",
            "allowed_claim_predicates",
            "typed_admission_contract",
            "nonreuse_claim_lattice",
            "comparison_projection_contract",
            "provenance_envelope_contract",
            "retired_authorities",
            "comparison_scopes",
            "prohibitions",
        },
        "independence_schema.json",
        errors,
    )
    _common_contract(
        document,
        "independence_schema.json",
        G6B_INDEPENDENCE_SCHEMA_VERSION,
        errors,
    )
    _expect(
        document.get("canonicalization_contract"),
        _CANONICALIZATION_CONTRACT,
        "independence_schema.json: canonicalization_contract",
        errors,
    )
    _expect(
        document.get("self_hash_finalization_contract"),
        _SELF_HASH_FINALIZATION_CONTRACT,
        "independence_schema.json: self_hash_finalization_contract",
        errors,
    )
    _expect(
        document.get("dimensions"),
        _DIMENSIONS,
        "independence_schema.json: dimensions",
        errors,
    )
    _validate_no_legacy_output_root(document, "independence_schema.json", errors)
    _expect(
        document.get("fingerprint_subject_map"),
        _FINGERPRINT_SUBJECT_MAP,
        "independence_schema.json: fingerprint_subject_map",
        errors,
    )
    _expect(
        document.get("fingerprint_policy_map"),
        _FINGERPRINT_POLICY_MAP,
        "independence_schema.json: fingerprint_policy_map",
        errors,
    )
    _expect(
        document.get("allowed_claim_predicates"),
        _ALLOWED_CLAIM_PREDICATES,
        "independence_schema.json: allowed_claim_predicates",
        errors,
    )
    _expect(
        document.get("typed_admission_contract"),
        _TYPED_ADMISSION_CONTRACT,
        "independence_schema.json: typed_admission_contract",
        errors,
    )
    _expect(
        document.get("nonreuse_claim_lattice"),
        _NONREUSE_CLAIM_LATTICE,
        "independence_schema.json: nonreuse_claim_lattice",
        errors,
    )
    _expect(
        document.get("comparison_projection_contract"),
        _COMPARISON_PROJECTION_CONTRACT,
        "independence_schema.json: comparison_projection_contract",
        errors,
    )
    _expect(
        document.get("provenance_envelope_contract"),
        _PROVENANCE_ENVELOPE_CONTRACT,
        "independence_schema.json: provenance_envelope_contract",
        errors,
    )
    _validate_no_forbidden_status_upgrade_claims(
        document, "independence_schema.json", errors
    )
    _expect(
        document.get("retired_authorities"),
        {
            "G4": "historical_authority_only",
            "G5": "historical_authority_only",
            "G6_R": "historical_replay_authority_only",
        },
        "independence_schema.json: retired_authorities",
        errors,
    )
    _expect(
        document.get("comparison_scopes"),
        {
            "discovery_vs_retired": {
                "description": (
                    "Every G6-B discovery row is compared against retired "
                    "G4/G5/G6-R authorities through typed dimensions and "
                    "lineage-deduplicated policies."
                ),
                "compare_against": ["G4", "G5", "G6_R"],
                "typed_dimensions": _DIMENSIONS,
                "admission_predicate": "bounded_nonreuse_admission",
                "lineage_deduplication_required": True,
            },
            "discovery_internal": {
                "description": (
                    "This schema does not impose unconditional zero overlap "
                    "across all admitted G6-B discovery rows."
                ),
                "typed_dimensions": _DIMENSIONS,
                "row_family_protocol_required": True,
                "generic_independent_result_allowed": False,
            },
            "future_confirmation_vs_retired_and_discovery": {
                "description": (
                    "Future G6 confirmation rows must preserve typed non-reuse "
                    "from retired authorities and G6-B discovery case "
                    "identity/provenance."
                ),
                "compare_against": ["G4", "G5", "G6_R", "G6_B_discovery"],
                "typed_dimensions": _FUTURE_CONFIRMATION_DIMENSIONS,
                "metric_schema_sha256": {
                    "controlled_reuse_requires_preregistration": True,
                    "reuse_allowed_only_if": [
                        "explicitly_preregistered",
                        "same_target_comparability",
                        "not_derived_from_outcomes",
                    ],
                },
            },
        },
        "independence_schema.json: comparison_scopes",
        errors,
    )
    _expect(
        document.get("prohibitions"),
        {
            "rename_shift": "prohibited",
            "parameter_shift_from_retired_authority": "prohibited",
            "case_snapshot_reuse": "prohibited",
            "random_stream_reuse": "prohibited",
            "output_root_materialization_reuse": "prohibited",
            "confirmation_use": "prohibited",
            "generic_independent_result": "prohibited",
        },
        "independence_schema.json: prohibitions",
        errors,
    )


def _validate_negative_controls(document: JsonObject, errors: list[str]) -> None:
    _exact_keys(
        document,
        _COMMON_KEYS | {"controls"},
        "negative_controls.json",
        errors,
    )
    _common_contract(
        document,
        "negative_controls.json",
        G6B_NEGATIVE_CONTROLS_VERSION,
        errors,
    )
    controls = document.get("controls")
    if controls != _NEGATIVE_CONTROLS:
        errors.append("negative_controls.json: controls drifted")
    if not isinstance(controls, list) or len(controls) != len(_NEGATIVE_CONTROLS):
        errors.append("negative_controls.json: controls must be the exact controls")
        return
    for expected_id, control in zip(_NEGATIVE_CONTROL_IDS, controls, strict=True):
        if not isinstance(control, dict):
            errors.append("negative_controls.json: controls entries must be objects")
            continue
        if set(control) != {
            "id",
            "expected_classification",
            "expected_refusal",
            "not_support_if_failed",
        }:
            errors.append("negative_controls.json: controls entry keys drifted")
        if control.get("id") != expected_id:
            errors.append("negative_controls.json: controls IDs drifted")
        if control.get("not_support_if_failed") is not True:
            errors.append("negative_controls.json: controls must not support if failed")
        if not isinstance(control.get("expected_classification"), str):
            errors.append("negative_controls.json: expected_classification required")
        if not isinstance(control.get("expected_refusal"), str):
            errors.append("negative_controls.json: expected_refusal required")


def _validate_failure_ledger(document: JsonObject, errors: list[str]) -> None:
    _exact_keys(
        document,
        _COMMON_KEYS | {"append_only", "entries", "empty_entries_meaning"},
        "failure_ledger.json",
        errors,
    )
    _common_contract(
        document,
        "failure_ledger.json",
        G6B_FAILURE_LEDGER_VERSION,
        errors,
    )
    _expect(
        document.get("append_only"), True, "failure_ledger.json: append_only", errors
    )
    _expect(document.get("entries"), [], "failure_ledger.json: entries", errors)
    _expect(
        document.get("empty_entries_meaning"),
        (
            "no discovery attempt has been admitted under this protocol; "
            "this does not mean no failures exist"
        ),
        "failure_ledger.json: empty_entries_meaning",
        errors,
    )


def _validate_no_legacy_output_root(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "output_root":
                errors.append(f"{label}: legacy output_root key is prohibited in v2")
            _validate_no_legacy_output_root(child, label, errors)
        return
    if isinstance(value, list):
        if "output_root" in value:
            errors.append(f"{label}: legacy output_root dimension is prohibited in v2")
        for child in value:
            _validate_no_legacy_output_root(child, label, errors)


def _validate_no_forbidden_status_upgrade_claims(
    value: Any, label: str, errors: list[str]
) -> None:
    if isinstance(value, dict):
        for child in value.values():
            _validate_no_forbidden_status_upgrade_claims(child, label, errors)
        return
    if isinstance(value, list):
        for child in value:
            _validate_no_forbidden_status_upgrade_claims(child, label, errors)
        return
    if isinstance(value, str):
        normalized = value.lower()
        if any(phrase in normalized for phrase in _FORBIDDEN_STATUS_UPGRADE_PHRASES):
            errors.append(f"{label}: forbidden status-upgrade claim")


def _common_contract(
    document: JsonObject,
    label: str,
    schema_version: str,
    errors: list[str],
) -> None:
    if document.get("schema_version") != schema_version:
        errors.append(f"{label}: unsupported schema_version")
    _expect(
        document.get("study_role"), "discovery_only", f"{label}: study_role", errors
    )
    _expect(
        document.get("confirmation_use"),
        "prohibited",
        f"{label}: confirmation_use",
        errors,
    )
    _expect(
        document.get("scientific_execution_authorized"),
        False,
        f"{label}: scientific_execution_authorized",
        errors,
    )


def _exact_keys(
    document: JsonObject,
    expected_keys: set[str],
    label: str,
    errors: list[str],
) -> None:
    actual = set(document)
    missing = sorted(expected_keys - actual)
    unexpected = sorted(actual - expected_keys)
    if missing:
        errors.append(f"{label}: missing keys {missing}")
    if unexpected:
        errors.append(f"{label}: unexpected keys {unexpected}")


def _expect(actual: Any, expected: Any, label: str, errors: list[str]) -> None:
    if not _json_equal_strict(actual, expected):
        errors.append(f"{label} drifted")


def _json_equal_strict(actual: Any, expected: Any) -> bool:
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        if set(actual) != set(expected):
            return False
        return all(_json_equal_strict(actual[key], expected[key]) for key in expected)
    if isinstance(expected, list):
        if len(actual) != len(expected):
            return False
        return all(
            _json_equal_strict(actual_item, expected_item)
            for actual_item, expected_item in zip(actual, expected, strict=True)
        )
    return bool(actual == expected)


def _expect_path_list(
    actual: Any,
    expected: list[str],
    label: str,
    repo_root: Path,
    *,
    required_existing: set[str],
    errors: list[str],
) -> None:
    if actual != expected:
        errors.append(f"{label} drifted")
    if not isinstance(actual, list) or not all(
        isinstance(path, str) for path in actual
    ):
        errors.append(f"{label} must be a list of strings")
        return
    if len(set(actual)) != len(actual):
        errors.append(f"{label} contains duplicate paths")
    for path in actual:
        if not _is_unambiguous_repo_relative_path(path):
            errors.append(f"{label} contains unsafe or ambiguous path {path!r}")
            continue
        if path in required_existing and not (repo_root / path).is_file():
            errors.append(f"{label} missing local artifact {path!r}")


def _is_unambiguous_repo_relative_path(path: str) -> bool:
    candidate = Path(path)
    if candidate.is_absolute() or "\\" in path or path.startswith("~"):
        return False
    if path == "" or path != candidate.as_posix():
        return False
    return all(part not in {"", ".", ".."} for part in candidate.parts)


def _repo_root_for(bundle_root: Path) -> Path | None:
    if (
        len(bundle_root.parents) >= 3
        and bundle_root.name == "g6b"
        and bundle_root.parent.name == "discovery"
        and bundle_root.parent.parent.name == "cases"
    ):
        return bundle_root.parents[2]
    return None


def _load_document_object(path: Path, *, use_canonical_v2: bool) -> JsonObject:
    if use_canonical_v2:
        return _load_canonical_v2_object(path)
    return _load_legacy_json_object(path)


def _load_canonical_v2_object(path: Path) -> JsonObject:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot read document: {exc}") from exc
    try:
        document = loads_v2(raw)
    except CanonicalJsonError as exc:
        if exc.code == "duplicate_member":
            raise ValueError(
                f"duplicate JSON key (canonical JSON v2 {exc.code})"
            ) from exc
        raise ValueError(f"canonical JSON v2 {exc.code}") from exc
    if not isinstance(document, dict):
        raise ValueError("root must be a JSON object")
    return dict(document)


def _load_legacy_json_object(path: Path) -> JsonObject:
    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> JsonObject:
        seen: set[str] = set()
        result: JsonObject = {}
        for key, value in pairs:
            if key in seen:
                raise ValueError(f"duplicate JSON key {key!r}")
            seen.add(key)
            result[key] = value
        return result

    try:
        with path.open(encoding="utf-8") as handle:
            document = json.load(handle, object_pairs_hook=reject_duplicate_keys)
    except OSError as exc:
        raise ValueError(f"cannot read document: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError("root must be a JSON object")
    return document


def _document_sha256(document: JsonObject, *, use_canonical_v2: bool) -> str:
    if use_canonical_v2:
        return canonical_sha256_v2(document)
    return _legacy_canonical_sha256(document)


def _legacy_canonical_sha256(document: JsonObject) -> str:
    canonical = json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
