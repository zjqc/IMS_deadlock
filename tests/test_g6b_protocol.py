import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from ims_deadlock.g6b_protocol import validate_g6b_protocol_bundle

_DOCUMENT_TOP_LEVEL_KEYS = {
    "protocol.json": "protocol_id",
    "estimand_schema.json": "future_required_hashes",
    "independence_schema.json": "canonicalization_contract",
    "negative_controls.json": "controls",
    "failure_ledger.json": "append_only",
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

_EXPECTED_NEGATIVE_CONTROLS = [
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
_NEW_FUTURE_HASHES = [
    "positive_rate_graph_hash",
    "policy_filter_hash",
    "absorption_domain_hash",
]
_TYPED_CAPABILITY_VOCABULARY = [
    "case_construction_authorized",
    "retired_authority_fingerprint_normalization_authorized",
    "target_certification_preflight_authorized",
    "quantitative_execution_authorized",
]
_ROW_FAMILY_CAPABILITY_REFERENCE = (
    "row_families/structural_discovery_v1/row_family_protocol.json#/typed_capabilities"
)
_FINGERPRINT_DIMENSIONS = [
    "case_content_sha256",
    "state_snapshot_sha256",
    "route_signature_sha256",
    "parameter_tuple_sha256",
    "random_stream_manifest_sha256",
    "output_root_reservation_sha256",
    "sealed_prediction_sha256",
    "metric_schema_sha256",
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


def _copy_bundle(tmp_path: Path) -> Path:
    source_root = Path.cwd()
    repo_root = tmp_path / "repo"
    target = repo_root / "cases/discovery/g6b"
    source = source_root / "cases/discovery/g6b"
    shutil.copytree(source, target)
    for relative_path in [*_ARTIFACT_PATHS, *_HISTORICAL_AUTHORITIES]:
        if relative_path in _REMOTE_ONLY_HISTORICAL_AUTHORITIES:
            continue
        source_path = source_root / relative_path
        assert source_path.is_file(), relative_path
        target_path = repo_root / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
    return target


def _load(bundle: Path, filename: str) -> dict[str, Any]:
    with (bundle / filename).open(encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def _write(bundle: Path, filename: str, data: dict[str, Any]) -> None:
    with (bundle / filename).open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")


def _assert_invalid(bundle: Path, expected: str) -> None:
    validation = validate_g6b_protocol_bundle(bundle)
    assert validation.valid is False
    assert any(expected in error for error in validation.errors), validation.errors


def _nested_set(document: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    cursor: Any = document
    for key in path[:-1]:
        assert isinstance(cursor, dict)
        cursor = cursor[key]
    assert isinstance(cursor, dict)
    cursor[path[-1]] = value


def test_canonical_g6b_bundle_is_valid_and_execution_disabled() -> None:
    validation = validate_g6b_protocol_bundle(Path("cases/discovery/g6b"))

    assert validation.valid is True
    assert validation.errors == ()
    assert validation.scientific_execution_authorized is False
    assert validation.adversarial_review_status == "PENDING"
    assert set(validation.bundle_hashes) == {
        "protocol.json",
        "estimand_schema.json",
        "independence_schema.json",
        "negative_controls.json",
        "failure_ledger.json",
    }


def test_duplicate_json_key_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = (bundle / "protocol.json").read_text(encoding="utf-8")
    duplicate = protocol.replace(
        '"schema_version": "ims-deadlock/g6b-discovery-protocol/v2",',
        (
            '"schema_version": "ims-deadlock/g6b-discovery-protocol/v2",\n'
            '  "schema_version": "ims-deadlock/g6b-discovery-protocol/v2",'
        ),
        1,
    )
    (bundle / "protocol.json").write_text(duplicate, encoding="utf-8")

    _assert_invalid(bundle, "duplicate JSON key")


def test_copied_bundle_outside_canonical_layout_fails_closed(tmp_path: Path) -> None:
    bundle = tmp_path / "floating_g6b"
    shutil.copytree(Path("cases/discovery/g6b"), bundle)

    _assert_invalid(bundle, "bundle root must be <repo>/cases/discovery/g6b")


def test_extra_json_document_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    _write(bundle, "extra.json", {"schema_version": "unexpected"})

    _assert_invalid(bundle, "unexpected JSON documents: ['extra.json']")


@pytest.mark.parametrize("filename", sorted(_DOCUMENT_TOP_LEVEL_KEYS))
def test_missing_required_document_is_reported_deterministically(
    tmp_path: Path, filename: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    (bundle / filename).unlink()

    _assert_invalid(bundle, f"missing JSON documents: ['{filename}']")


@pytest.mark.parametrize("filename", sorted(_DOCUMENT_TOP_LEVEL_KEYS))
def test_non_object_root_is_rejected_for_each_document(
    tmp_path: Path, filename: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    (bundle / filename).write_text("[]\n", encoding="utf-8")

    _assert_invalid(bundle, f"{filename}: root must be a JSON object")


@pytest.mark.parametrize("filename", sorted(_DOCUMENT_TOP_LEVEL_KEYS))
def test_unknown_top_level_key_is_rejected_for_each_document(
    tmp_path: Path, filename: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    document = _load(bundle, filename)
    document["unexpected"] = "not allowed"
    _write(bundle, filename, document)

    _assert_invalid(bundle, f"{filename}: unexpected keys")


@pytest.mark.parametrize(
    ("filename", "key_to_remove"),
    sorted(_DOCUMENT_TOP_LEVEL_KEYS.items()),
)
def test_missing_top_level_key_is_rejected_for_each_document(
    tmp_path: Path, filename: str, key_to_remove: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    document = _load(bundle, filename)
    document.pop(key_to_remove)
    _write(bundle, filename, document)

    _assert_invalid(bundle, f"{filename}: missing keys")


@pytest.mark.parametrize("filename", sorted(_DOCUMENT_TOP_LEVEL_KEYS))
def test_duplicate_json_key_is_rejected_for_each_document(
    tmp_path: Path, filename: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    raw = (bundle / filename).read_text(encoding="utf-8")
    duplicate = raw.replace(
        '"schema_version":',
        '"schema_version": "duplicate-shadow",\n  "schema_version":',
        1,
    )
    (bundle / filename).write_text(duplicate, encoding="utf-8")

    _assert_invalid(bundle, f"{filename}: duplicate JSON key")


def test_unsupported_schema_version_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    protocol["schema_version"] = "ims-deadlock/g6b-discovery-protocol/v1"
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: unsupported schema_version")


def test_protocol_scientific_execution_authorized_requires_json_false(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    protocol["scientific_execution_authorized"] = 0
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: scientific_execution_authorized")


def test_protocol_rejects_canonical_negative_zero_in_v2_document(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol_path = bundle / "protocol.json"
    raw = protocol_path.read_text(encoding="utf-8")
    mutated = raw.replace(
        '"scientific_execution_authorized": false',
        '"scientific_execution_authorized": -0',
        1,
    )
    assert mutated != raw
    protocol_path.write_text(mutated, encoding="utf-8")

    _assert_invalid(bundle, "protocol.json: canonical JSON v2 negative_zero")


def test_spec_17_3_01_schema_state_order(tmp_path: Path) -> None:
    # Task 2 provides only the top-level/schema-tranche order evidence for
    # Section 17.3.01. Task 4 closes the full state-object order:
    # normalizer -> overlap -> preflight -> quantitative authorization.
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    independence = _load(bundle, "independence_schema.json")

    assert protocol["schema_version"] == "ims-deadlock/g6b-discovery-protocol/v2"
    assert protocol["typed_capability_vocabulary"] == _TYPED_CAPABILITY_VOCABULARY
    assert (
        protocol["current_row_family_capability_reference"]
        == _ROW_FAMILY_CAPABILITY_REFERENCE
    )
    assert protocol["scientific_execution_authorized"] is False
    assert independence["schema_version"] == "ims-deadlock/g6b-independence-schema/v2"
    assert independence["dimensions"] == _FINGERPRINT_DIMENSIONS
    assert independence["dimensions"][5] == "output_root_reservation_sha256"
    assert "output_root" not in independence["dimensions"]
    assert set(independence["fingerprint_subject_map"]) == set(
        independence["dimensions"]
    )
    assert independence["fingerprint_subject_map"] == _FINGERPRINT_SUBJECT_MAP
    assert independence["fingerprint_policy_map"] == _FINGERPRINT_POLICY_MAP
    assert independence["allowed_claim_predicates"] == _ALLOWED_CLAIM_PREDICATES
    assert "independent" not in independence["allowed_claim_predicates"]
    assert protocol["execution_boundary"] == {
        "creates_cases": False,
        "authorizes_enumeration": False,
        "authorizes_ctmc_solve": False,
        "authorizes_des_run": False,
        "requires_adversarial_review_before_scientific_execution": True,
    }

    reordered = _load(bundle, "protocol.json")
    capabilities = reordered["typed_capability_vocabulary"]
    assert isinstance(capabilities, list)
    capabilities[1], capabilities[2] = capabilities[2], capabilities[1]
    _write(bundle, "protocol.json", reordered)
    _assert_invalid(bundle, "protocol.json: typed_capability_vocabulary")


@pytest.mark.parametrize("index", range(len(_TYPED_CAPABILITY_VOCABULARY)))
def test_protocol_typed_capability_vocabulary_entry_drift_is_rejected(
    tmp_path: Path, index: int
) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    capabilities = protocol["typed_capability_vocabulary"]
    assert capabilities == _TYPED_CAPABILITY_VOCABULARY
    assert isinstance(capabilities, list)
    capabilities[index] = f"{capabilities[index]}_drifted"
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: typed_capability_vocabulary")


def test_protocol_rejects_top_level_typed_capability_value_object(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    protocol["typed_capabilities"] = {
        capability: False for capability in _TYPED_CAPABILITY_VOCABULARY
    }
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: unexpected keys")


def test_protocol_row_family_capability_reference_drift_is_rejected(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    protocol["current_row_family_capability_reference"] = (
        "row_families/structural_discovery_v1/"
        "row_family_protocol.json#/case_creation_authorized"
    )
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: current_row_family_capability_reference")


def test_spec_17_3_02_schema_only_capabilities_false(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    validation = validate_g6b_protocol_bundle(bundle)
    protocol = _load(bundle, "protocol.json")

    assert validation.valid is True
    assert validation.scientific_execution_authorized is False
    assert protocol["adversarial_review_status"] == "PENDING"
    assert protocol["scientific_execution_authorized"] is False
    assert "typed_capabilities" not in protocol

    protocol["scientific_execution_authorized"] = True
    _write(bundle, "protocol.json", protocol)
    _assert_invalid(bundle, "protocol.json: scientific execution")


@pytest.mark.parametrize(
    ("map_name", "dimension", "replacement"),
    [
        ("fingerprint_subject_map", "case_content_sha256", "method_observation"),
        (
            "fingerprint_subject_map",
            "random_stream_manifest_sha256",
            "case_unit",
        ),
        (
            "fingerprint_subject_map",
            "metric_schema_sha256",
            "method_observation",
        ),
        (
            "fingerprint_policy_map",
            "case_content_sha256",
            "provenance_containment_only",
        ),
        (
            "fingerprint_policy_map",
            "random_stream_manifest_sha256",
            "strict_semantic_distinctness",
        ),
        (
            "fingerprint_policy_map",
            "output_root_reservation_sha256",
            "strict_semantic_distinctness",
        ),
        (
            "fingerprint_policy_map",
            "metric_schema_sha256",
            "strict_semantic_distinctness",
        ),
    ],
)
def test_independence_subject_and_policy_drift_is_rejected(
    tmp_path: Path, map_name: str, dimension: str, replacement: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "independence_schema.json")
    mapping = schema[map_name]
    assert isinstance(mapping, dict)
    mapping[dimension] = replacement
    _write(bundle, "independence_schema.json", schema)

    _assert_invalid(bundle, f"independence_schema.json: {map_name}")


@pytest.mark.parametrize("predicate", _ALLOWED_CLAIM_PREDICATES)
def test_independence_claim_lattice_predicate_drift_is_rejected(
    tmp_path: Path, predicate: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "independence_schema.json")
    predicates = schema["allowed_claim_predicates"]
    assert predicates == _ALLOWED_CLAIM_PREDICATES
    assert isinstance(predicates, list)
    predicates[predicates.index(predicate)] = "independent"
    _write(bundle, "independence_schema.json", schema)

    _assert_invalid(bundle, "independence_schema.json: allowed_claim_predicates")


@pytest.mark.parametrize(
    ("path", "claim"),
    [
        (
            ("typed_admission_contract", "non_authorization_boundary"),
            "G6-B passed",
        ),
        (
            ("nonreuse_claim_lattice", "claim_boundary"),
            "eight independent dimensions",
        ),
        (
            ("comparison_projection_contract", "counting_rule"),
            "exact/DES are two independent cases",
        ),
        (
            ("provenance_envelope_contract", "confirmation_boundary"),
            "confirmed for G6-C",
        ),
    ],
)
def test_spec_17_3_36_no_status_upgrade_from_intermediate_state(
    tmp_path: Path, path: tuple[str, ...], claim: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "independence_schema.json")
    assert "independent" not in schema["allowed_claim_predicates"]

    _nested_set(schema, path, claim)
    _write(bundle, "independence_schema.json", schema)

    _assert_invalid(bundle, "forbidden status-upgrade claim")


@pytest.mark.parametrize(
    ("list_path", "replacement"),
    [
        (("dimensions",), "output_root"),
        (
            ("comparison_scopes", "discovery_vs_retired", "typed_dimensions"),
            "output_root",
        ),
        (
            (
                "comparison_scopes",
                "future_confirmation_vs_retired_and_discovery",
                "typed_dimensions",
            ),
            "output_root",
        ),
    ],
)
def test_legacy_output_root_is_rejected_in_v2_dimension_lists(
    tmp_path: Path, list_path: tuple[str, ...], replacement: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "independence_schema.json")
    cursor: Any = schema
    for key in list_path:
        assert isinstance(cursor, dict)
        cursor = cursor[key]
    assert isinstance(cursor, list)
    cursor[5] = replacement
    _write(bundle, "independence_schema.json", schema)

    _assert_invalid(bundle, "legacy output_root")


@pytest.mark.parametrize(
    ("contract_name", "expected", "path", "replacement"),
    [
        (
            "canonicalization_contract",
            _CANONICALIZATION_CONTRACT,
            ("version",),
            "ims-deadlock/canonical-json/v2",
        ),
        (
            "canonicalization_contract",
            _CANONICALIZATION_CONTRACT,
            ("duplicate_members",),
            "last_member_wins",
        ),
        (
            "canonicalization_contract",
            _CANONICALIZATION_CONTRACT,
            ("unicode_normalization", "silent_normalization"),
            True,
        ),
        (
            "canonicalization_contract",
            _CANONICALIZATION_CONTRACT,
            ("object_key_order",),
            "locale_order",
        ),
        (
            "canonicalization_contract",
            _CANONICALIZATION_CONTRACT,
            ("array_order_policy", "ordinary_arrays"),
            "sort_all_arrays",
        ),
        (
            "canonicalization_contract",
            _CANONICALIZATION_CONTRACT,
            ("array_order_policy", "set_like_arrays"),
            "deduplicate_after_sorting",
        ),
        (
            "canonicalization_contract",
            _CANONICALIZATION_CONTRACT,
            ("utf8_serialization", "ensure_ascii"),
            True,
        ),
        (
            "canonicalization_contract",
            _CANONICALIZATION_CONTRACT,
            ("utf8_serialization", "allow_nan"),
            True,
        ),
        (
            "canonicalization_contract",
            _CANONICALIZATION_CONTRACT,
            ("numeric_policy", "json_float_values"),
            "allowed",
        ),
        (
            "canonicalization_contract",
            _CANONICALIZATION_CONTRACT,
            ("numeric_policy", "decimal_strings_regex"),
            ".*",
        ),
        (
            "canonicalization_contract",
            _CANONICALIZATION_CONTRACT,
            ("path_policy", "symlink_dependent_resolution"),
            "allowed",
        ),
        (
            "canonicalization_contract",
            _CANONICALIZATION_CONTRACT,
            ("timestamp_policy", "format"),
            "RFC3339",
        ),
        (
            "self_hash_finalization_contract",
            _SELF_HASH_FINALIZATION_CONTRACT,
            ("version",),
            "ims-deadlock/self-hash-finalization/v1",
        ),
        (
            "self_hash_finalization_contract",
            _SELF_HASH_FINALIZATION_CONTRACT,
            ("placeholder_value",),
            "omitted",
        ),
        (
            "self_hash_finalization_contract",
            _SELF_HASH_FINALIZATION_CONTRACT,
            ("replaced_field_count",),
            2,
        ),
        (
            "self_hash_finalization_contract",
            _SELF_HASH_FINALIZATION_CONTRACT,
            ("excluded_field_escape_hatch_allowed",),
            True,
        ),
    ],
)
def test_independence_v2_canonicalization_and_self_hash_contracts_are_closed(
    tmp_path: Path,
    contract_name: str,
    expected: dict[str, Any],
    path: tuple[str, ...],
    replacement: Any,
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "independence_schema.json")
    assert schema[contract_name] == expected
    assert set(schema[contract_name]) == set(expected)

    _nested_set(schema[contract_name], path, replacement)
    _write(bundle, "independence_schema.json", schema)
    _assert_invalid(bundle, f"independence_schema.json: {contract_name}")


def test_independence_v2_removes_legacy_canonical_hash_normalization(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "independence_schema.json")
    assert "canonical_hash_normalization" not in schema

    schema["canonical_hash_normalization"] = {
        "format": "canonical_json_sha256",
        "encoding": "utf-8",
        "sort_keys": True,
        "separators": [",", ":"],
        "duplicate_keys_allowed": False,
    }
    _write(bundle, "independence_schema.json", schema)

    _assert_invalid(bundle, "independence_schema.json: unexpected keys")


@pytest.mark.parametrize("excluded", _SUBJECT_FREE_PROJECTION_EXCLUDES)
def test_comparison_projection_excludes_exact_governance_subject_fields(
    tmp_path: Path, excluded: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "independence_schema.json")
    contract = schema["comparison_projection_contract"]
    assert contract["subject_free_projection_excludes"] == (
        _SUBJECT_FREE_PROJECTION_EXCLUDES
    )
    assert (
        contract["governance_only_changes_leave_subject_free_projection_unchanged"]
        is True
    )
    assert "governance_only_changes_do_not_support_semantic_non_overlap" not in contract

    excludes = contract["subject_free_projection_excludes"]
    assert isinstance(excludes, list)
    excludes[excludes.index(excluded)] = f"{excluded}_drift"
    _write(bundle, "independence_schema.json", schema)

    _assert_invalid(bundle, "independence_schema.json: comparison_projection_contract")


def test_comparison_projection_excludes_reject_remove_and_reorder(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path / "remove")
    schema = _load(bundle, "independence_schema.json")
    excludes = schema["comparison_projection_contract"][
        "subject_free_projection_excludes"
    ]
    assert isinstance(excludes, list)
    excludes.pop()
    _write(bundle, "independence_schema.json", schema)
    _assert_invalid(bundle, "independence_schema.json: comparison_projection_contract")

    bundle = _copy_bundle(tmp_path / "reorder")
    schema = _load(bundle, "independence_schema.json")
    excludes = schema["comparison_projection_contract"][
        "subject_free_projection_excludes"
    ]
    assert isinstance(excludes, list)
    excludes[0], excludes[1] = excludes[1], excludes[0]
    _write(bundle, "independence_schema.json", schema)
    _assert_invalid(bundle, "independence_schema.json: comparison_projection_contract")


@pytest.mark.parametrize("field", _FINGERPRINT_RECORD_REQUIRED_FIELDS)
def test_provenance_envelope_closes_required_fingerprint_fields(
    tmp_path: Path, field: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "independence_schema.json")
    contract = schema["provenance_envelope_contract"]
    assert contract["applicable_subject_ids_required"] is True
    assert contract["recorded_contexts"] == _RECORDED_CONTEXTS
    assert contract["fingerprint_record_required_fields"] == (
        _FINGERPRINT_RECORD_REQUIRED_FIELDS
    )

    fields = contract["fingerprint_record_required_fields"]
    assert isinstance(fields, list)
    fields[fields.index(field)] = f"{field}_drift"
    _write(bundle, "independence_schema.json", schema)

    _assert_invalid(bundle, "independence_schema.json: provenance_envelope_contract")


@pytest.mark.parametrize("context", _RECORDED_CONTEXTS)
def test_provenance_envelope_recorded_contexts_are_exact(
    tmp_path: Path, context: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "independence_schema.json")
    contexts = schema["provenance_envelope_contract"]["recorded_contexts"]
    assert isinstance(contexts, list)
    contexts[contexts.index(context)] = f"{context}_drift"
    _write(bundle, "independence_schema.json", schema)

    _assert_invalid(bundle, "independence_schema.json: provenance_envelope_contract")


def test_provenance_envelope_required_fields_reject_remove_and_reorder(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path / "remove")
    schema = _load(bundle, "independence_schema.json")
    fields = schema["provenance_envelope_contract"][
        "fingerprint_record_required_fields"
    ]
    assert isinstance(fields, list)
    fields.pop()
    _write(bundle, "independence_schema.json", schema)
    _assert_invalid(bundle, "independence_schema.json: provenance_envelope_contract")

    bundle = _copy_bundle(tmp_path / "reorder")
    schema = _load(bundle, "independence_schema.json")
    fields = schema["provenance_envelope_contract"][
        "fingerprint_record_required_fields"
    ]
    assert isinstance(fields, list)
    fields[0], fields[1] = fields[1], fields[0]
    _write(bundle, "independence_schema.json", schema)
    _assert_invalid(bundle, "independence_schema.json: provenance_envelope_contract")


@pytest.mark.parametrize("field", sorted(_TYPED_ADMISSION_CONTRACT))
def test_typed_admission_contract_is_schema_tranche_summary(
    tmp_path: Path, field: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "independence_schema.json")
    contract = schema["typed_admission_contract"]
    assert contract == _TYPED_ADMISSION_CONTRACT

    if isinstance(contract[field], bool):
        contract[field] = not contract[field]
    elif isinstance(contract[field], list):
        contract[field] = [*contract[field], "drift"]
    else:
        contract[field] = f"{contract[field]}_drift"
    _write(bundle, "independence_schema.json", schema)

    _assert_invalid(bundle, "independence_schema.json: typed_admission_contract")


def test_independence_self_hash_replaced_field_count_requires_json_integer(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "independence_schema.json")
    contract = schema["self_hash_finalization_contract"]
    assert isinstance(contract, dict)
    contract["replaced_field_count"] = True
    _write(bundle, "independence_schema.json", schema)

    _assert_invalid(bundle, "independence_schema.json: self_hash_finalization_contract")


def test_independence_rejects_canonical_float_in_v2_document(
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema_path = bundle / "independence_schema.json"
    raw = schema_path.read_text(encoding="utf-8")
    mutated = raw.replace(
        '"replaced_field_count": 1',
        '"replaced_field_count": 1.0',
        1,
    )
    assert mutated != raw
    schema_path.write_text(mutated, encoding="utf-8")

    _assert_invalid(
        bundle, "independence_schema.json: canonical JSON v2 json_float_prohibited"
    )


@pytest.mark.parametrize(
    ("contract_name", "field", "replacement"),
    [
        (
            "comparison_projection_contract",
            "subject_free_projection_kinds",
            [
                "semantic_content",
                "random_process",
                "controlled_schema",
                "provenance_containment",
            ],
        ),
        (
            "comparison_projection_contract",
            "provenance_containment_logical_coordinates_allowed",
            False,
        ),
        (
            "comparison_projection_contract",
            "provenance_containment_supports_semantic_distinctness",
            True,
        ),
        (
            "comparison_projection_contract",
            "governance_only_changes_leave_subject_free_projection_unchanged",
            False,
        ),
        (
            "comparison_projection_contract",
            "unequal_record_provenance_hash_does_not_support_non_overlap",
            False,
        ),
        (
            "comparison_projection_contract",
            "counting_rule",
            "exact_des_companions_are_two_independent_cases",
        ),
        (
            "provenance_envelope_contract",
            "separate_from_comparison_projection",
            False,
        ),
        (
            "provenance_envelope_contract",
            "unequal_envelope_hash_does_not_support_non_overlap",
            False,
        ),
    ],
)
def test_independence_v2_projection_and_envelope_contracts_are_separate(
    tmp_path: Path, contract_name: str, field: str, replacement: Any
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "independence_schema.json")
    assert schema["comparison_projection_contract"] == {
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
    assert schema["provenance_envelope_contract"] == {
        "version": "ims-deadlock/g6b-provenance-envelope-contract/v1",
        "envelope_scope": "artifact_lineage_locks_paths_and_reservations",
        "applicable_subject_ids_required": True,
        "recorded_contexts": _RECORDED_CONTEXTS,
        "fingerprint_record_required_fields": _FINGERPRINT_RECORD_REQUIRED_FIELDS,
        "separate_from_comparison_projection": True,
        "unequal_envelope_hash_does_not_support_non_overlap": True,
        "confirmation_boundary": "future_confirmation_tranche_only",
    }

    schema[contract_name][field] = replacement
    _write(bundle, "independence_schema.json", schema)
    _assert_invalid(bundle, f"independence_schema.json: {contract_name}")


def test_missing_independence_dimension_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "independence_schema.json")
    dimensions = schema["dimensions"]
    assert isinstance(dimensions, list)
    dimensions.remove("metric_schema_sha256")
    _write(bundle, "independence_schema.json", schema)

    _assert_invalid(bundle, "independence_schema.json: dimensions")


def test_estimand_schema_v2_uses_typed_ontology() -> None:
    estimand = _load(Path("cases/discovery/g6b"), "estimand_schema.json")

    assert estimand["schema_version"] == "ims-deadlock/g6b-estimand-schema/v2"
    assert "objective_classes" not in estimand["ontology"]
    assert estimand["ontology"]["selected_stopping_targets"] == {
        "bad_hit_sets": ["D_global", "D_local"],
        "success_class": "F",
    }
    assert estimand["ontology"]["unselected_plant_terminal_classes"] == [
        "R_livelock",
        "R_terminal",
    ]
    assert estimand["ontology"]["policy_analysis_class"] == {
        "label": "P_policy",
        "plant_partition_member": False,
        "selectable_target": False,
    }
    assert estimand["ontology"]["derived_state_sets"] == {
        "S_reach": {
            "definition": "complete_stopped_lts_support_reachability",
            "role": "diagnostic_only",
            "selectable_target": False,
        },
        "S_T": {
            "definition": (
                "probability_one_hit_selected_target_in_finite_positive_rate_"
                "stopped_ctmc"
            ),
            "role": "certified_absorption_domain",
            "selectable_target": False,
        },
    }


def test_legacy_objective_classes_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "estimand_schema.json")
    ontology = schema["ontology"]
    assert isinstance(ontology, dict)
    ontology["objective_classes"] = [
        "D_global",
        "D_local",
        "F",
        "R_livelock",
        "R_terminal",
        "P_policy",
        "S_T",
    ]
    _write(bundle, "estimand_schema.json", schema)

    _assert_invalid(bundle, "estimand_schema.json: ontology")


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("bad_hit_sets", ["D_global", "D_local", "S_T"]),
        ("bad_hit_sets", ["D_global", "D_local", "S_reach"]),
        ("bad_hit_sets", ["D_global", "D_local", "R_livelock"]),
        ("success_class", "P_policy"),
    ],
)
def test_selected_target_kind_drift_is_rejected(
    tmp_path: Path, field: str, replacement: list[str] | str
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "estimand_schema.json")
    ontology = schema["ontology"]
    assert isinstance(ontology, dict)
    assert ontology.get("selected_stopping_targets") == {
        "bad_hit_sets": ["D_global", "D_local"],
        "success_class": "F",
    }
    selected = ontology["selected_stopping_targets"]
    assert isinstance(selected, dict)
    selected[field] = replacement
    _write(bundle, "estimand_schema.json", schema)

    _assert_invalid(bundle, "estimand_schema.json: ontology")


@pytest.mark.parametrize("missing_hash", _NEW_FUTURE_HASHES)
def test_future_hashes_require_absorption_identity(
    tmp_path: Path, missing_hash: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "estimand_schema.json")
    future_hashes = schema["future_required_hashes"]
    assert isinstance(future_hashes, list)
    assert missing_hash in future_hashes
    future_hashes.remove(missing_hash)
    _write(bundle, "estimand_schema.json", schema)

    _assert_invalid(bundle, "estimand_schema.json: future_required_hashes")


@pytest.mark.parametrize(
    "rule",
    [
        "certified_absorption_domain_required",
        "same_absorption_domain_hash_required",
    ],
)
def test_exact_des_contract_requires_same_absorption_domain(
    tmp_path: Path, rule: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "estimand_schema.json")
    consistency = schema["exact_des_consistency"]
    assert isinstance(consistency, dict)
    assert consistency.get(rule) is True
    consistency[rule] = False
    _write(bundle, "estimand_schema.json", schema)

    _assert_invalid(bundle, "estimand_schema.json: exact_des_consistency")


def test_wrong_d_local_ontology_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "estimand_schema.json")
    ontology = schema["ontology"]
    assert isinstance(ontology, dict)
    d_local = ontology["D_local"]
    assert isinstance(d_local, dict)
    d_local["ontology"] = "terminal_scc"
    _write(bundle, "estimand_schema.json", schema)

    _assert_invalid(bundle, "estimand_schema.json: ontology")


def test_exact_des_consistency_drift_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "estimand_schema.json")
    consistency = schema["exact_des_consistency"]
    assert isinstance(consistency, dict)
    consistency["same_selected_bad_labels_required"] = False
    _write(bundle, "estimand_schema.json", schema)

    _assert_invalid(bundle, "estimand_schema.json: exact_des_consistency")


def test_missing_negative_control_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    controls = _load(bundle, "negative_controls.json")
    control_list = controls["controls"]
    assert isinstance(control_list, list)
    control_list.pop()
    _write(bundle, "negative_controls.json", controls)

    _assert_invalid(bundle, "negative_controls.json: controls")


@pytest.mark.parametrize("index", range(len(_EXPECTED_NEGATIVE_CONTROLS)))
@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("expected_classification", "DRIFTED_CLASSIFICATION"),
        ("expected_refusal", "drifted_refusal"),
    ],
)
def test_negative_control_semantic_drift_is_rejected(
    tmp_path: Path, index: int, field: str, replacement: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    controls = _load(bundle, "negative_controls.json")
    control_list = controls["controls"]
    assert control_list == _EXPECTED_NEGATIVE_CONTROLS
    assert isinstance(control_list, list)
    control = control_list[index]
    assert isinstance(control, dict)
    control[field] = replacement
    _write(bundle, "negative_controls.json", controls)

    _assert_invalid(bundle, "negative_controls.json: controls")


def test_absolute_unapproved_historical_path_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    authorities = protocol["tracked_historical_authorities"]
    assert isinstance(authorities, list)
    authorities[0] = "/tmp/FREEZE_ENTRY.json"
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: tracked_historical_authorities")


def test_execution_true_while_review_pending_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    protocol["scientific_execution_authorized"] = True
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: scientific execution")


def test_append_only_false_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    ledger = _load(bundle, "failure_ledger.json")
    ledger["append_only"] = False
    _write(bundle, "failure_ledger.json", ledger)

    _assert_invalid(bundle, "failure_ledger.json: append_only")


def test_artifact_path_ambiguity_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    paths = protocol["artifact_paths"]
    assert isinstance(paths, list)
    paths[0] = "docs/cases/../cases/G6_B_DISCOVERY_PROTOCOL.md"
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: artifact_paths")


def test_g6b_theory_documents_lock_typed_absorption_domain() -> None:
    protocol_path = Path("docs/cases/G6_B_DISCOVERY_PROTOCOL.md")
    theorem_path = Path("docs/theory/G6_LOCAL_FIRST_HIT_AND_STOPPING_THEOREMS.md")
    assumption_path = Path("docs/theory/ASSUMPTION_REGISTER.md")
    probability_path = Path("docs/theory/PROBABILITY_LAYER.md")
    symbol_path = Path("docs/theory/SYMBOL_TABLE.md")
    counterexample_path = Path("docs/theory/COUNTEREXAMPLE_LEDGER.md")
    foundation_review_path = Path(
        "docs/verification/G6_B_PROTOCOL_FOUNDATION_REVIEW.md"
    )

    g6b_protocol_text = protocol_path.read_text(encoding="utf-8")
    counterexample_ledger_text = counterexample_path.read_text(encoding="utf-8")
    foundation_review_text = foundation_review_path.read_text(encoding="utf-8")
    combined_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            protocol_path,
            theorem_path,
            assumption_path,
            probability_path,
            symbol_path,
            counterexample_path,
        ]
    )

    assert "S_reach" in combined_text
    assert "support graph" in combined_text or "support-graph" in combined_text
    assert "probability one" in combined_text
    assert "absorption_domain_hash" in combined_text
    assert "Objective classes are:" not in g6b_protocol_text
    assert "selected_stopping_targets" in g6b_protocol_text
    assert "unselected_plant_terminal_classes" in g6b_protocol_text
    assert "CE-NB1" in counterexample_ledger_text
    assert "S_reach" in counterexample_ledger_text
    assert "S_T" in counterexample_ledger_text
    assert "non_almost_sure_absorption_domain" in counterexample_ledger_text
    assert "SUPERSEDED IN PART" in foundation_review_text
    assert (
        "docs/superpowers/specs/2026-07-31-g6b-ontology-absorption-domain-correction-design.md"
        in foundation_review_text
    )

    theorem_text = theorem_path.read_text(encoding="utf-8")
    probability_text = probability_path.read_text(encoding="utf-8")
    assumption_text = assumption_path.read_text(encoding="utf-8")
    symbol_text = symbol_path.read_text(encoding="utf-8")
    active_scoped_text = "\n".join(
        [
            g6b_protocol_text,
            theorem_text,
            probability_text,
            assumption_text,
            symbol_text,
            counterexample_ledger_text,
        ]
    )

    for document_text in [
        g6b_protocol_text,
        theorem_text,
        probability_text,
        assumption_text,
        symbol_text,
    ]:
        assert "S_T = T \\ B_closed" in document_text
        assert "unselected closed SCC" in document_text
        assert "full stopped" in document_text
        assert "outgoing" in document_text
        assert "A_stop" in document_text

    assert "rate_manifest_hash" in symbol_text
    assert "absorption_domain_hash" in symbol_text
    absorption_row = _symbol_row(symbol_text, "absorption_domain_hash")
    for field in [
        "algorithm version",
        "state_space_hash",
        "partition_hash",
        "positive_rate_graph_hash",
        "policy_filter_hash",
        "selected IDs",
        "unselected closed SCCs",
        "B_closed",
        "S_T",
    ]:
        assert field in absorption_row
    assert "full declared rate manifest" not in absorption_row
    assert "Hash of the full declared rate manifest" in _symbol_row(
        symbol_text,
        "rate_manifest_hash",
    )
    assert "absorption-domain identity" in _symbol_row(symbol_text, "estimand_id")

    stale_reverse_basin_sentence = (
        "\u4ece\u6240\u9009\u5438\u6536\u96c6\u53cd\u5411"
        "\u53ef\u8fbe\uff0c\u5f97\u5230\u5b8c\u6574"
        "\u975e\u5438\u6536 basin `S_T`"
    )
    stale_reachability_sentence = (
        "`S_T` \u662f\u80fd\u5230\u8fbe\u6240\u9009"
        " bad/success absorption \u7684\u5168\u90e8"
        "\u975e\u5438\u6536\u72b6\u6001"
    )
    assert stale_reverse_basin_sentence not in theorem_text
    assert stale_reachability_sentence not in theorem_text
    assert "reverse-reachability definition" not in theorem_text
    assert "`R_c`" not in probability_text
    assert "`R_c`" not in symbol_text
    assert "| `B` |" not in symbol_text

    assert len(_symbol_rows(symbol_text, "A")) == 1
    assert "AGV" in _symbol_rows(symbol_text, "A")[0]
    assert len(_symbol_rows(symbol_text, "C")) == 1
    assert "directed cycle" in _symbol_rows(symbol_text, "C")[0]
    assert len(_symbol_rows(symbol_text, "A_stop")) == 1
    assert len(_symbol_rows(symbol_text, "D_sel")) == 1
    assert len(_symbol_rows(symbol_text, "C_closed")) == 1
    assert len(_symbol_rows(symbol_text, "V")) == 1
    assert "reservation" in _symbol_rows(symbol_text, "V")[0]
    assert len(_symbol_rows(symbol_text, "X_stop")) == 1
    assert "full finite stopped state set" in _symbol_rows(symbol_text, "X_stop")[0]
    assert "D_sel := D_global union D_local" in active_scoped_text
    assert "A_stop := D_sel union F" in active_scoped_text
    assert "T := X_stop \\ A_stop" in active_scoped_text
    assert "C_closed subset T" in active_scoped_text
    assert "outgoing" in active_scoped_text
    assert "A_stop" in active_scoped_text
    assert "S_reach" in active_scoped_text
    assert "path to `A_stop`" in active_scoped_text
    assert "到 `A_stop` 的 support path" in theorem_text
    assert "到 `A` 的 support path" not in theorem_text
    assert "S_T = T \\ B_closed" in active_scoped_text
    assert "h_i = P_i(tau_{D_sel} < tau_F)" in probability_text
    assert "conditioning on first hitting `D_sel`" in probability_text
    assert "tau_{A_stop}" in probability_text
    assert "Q_{S_T,D_sel}" in probability_text
    assert "C subset T" not in active_scoped_text
    assert "selected `A`" not in active_scoped_text
    assert "selected A." not in active_scoped_text
    assert "selected A," not in active_scoped_text
    assert "for `i in D`" not in active_scoped_text
    assert "for i in D`" not in active_scoped_text
    assert "first hitting `D`" not in active_scoped_text
    assert "counts for `A`" not in active_scoped_text
    assert "path to `A`" not in active_scoped_text
    assert "V \\ A_stop" not in active_scoped_text
    assert "`C` may have" not in g6b_protocol_text
    assert "`C_closed` may have" in g6b_protocol_text
    assert "source-local" in probability_text
    assert "F_N=(I-T_N)^-1" in probability_text
    assert "G_N=F_N C_N" in probability_text
    assert "printed in the source as `F=(I-T)^-1`" in probability_text
    assert "printed in the source as `G=FC`" in probability_text
    assert "L23" in probability_text
    assert "L28" in probability_text
    assert "L16" in probability_text


def test_g6b_ontology_absorption_review_locks_domain_semantics() -> None:
    review_path = Path(
        "docs/verification/G6_B_ONTOLOGY_ABSORPTION_DOMAIN_CORRECTION_REVIEW.md"
    )
    review_text = review_path.read_text(encoding="utf-8")
    normalized_review_text = " ".join(review_text.split())

    assert "Verification date: 2026-07-31" in review_text
    assert "Record commit date: 2026-08-01" in review_text
    assert (
        "git log --diff-filter=A --format=%H -- "
        "docs/verification/G6_B_ONTOLOGY_ABSORPTION_DOMAIN_CORRECTION_REVIEW.md"
    ) in review_text
    assert (
        "git log -1 --format=%H -- "
        "docs/verification/G6_B_ONTOLOGY_ABSORPTION_DOMAIN_CORRECTION_REVIEW.md"
    ) in review_text

    assert (
        "`C_closed`: unselected closed SCC with membership "
        "`C_closed subset T`; closedness is checked against every outgoing "
        "positive-rate edge in the full stopped graph, including exits to "
        "`A_stop`"
    ) in normalized_review_text
    assert review_text.count("`C_closed`:") == 1

    assert (
        "Current production supports only the global `A_abs` certificate-or-"
        "refusal protocol. It does not support a partial-domain quantitative "
        "solve or payload; any such payload requires a separate versioned and "
        "reviewed design."
    ) in normalized_review_text
    assert (
        "Dropping only `C_closed` while retaining `B_closed \\ C_closed` is "
        "also prohibited."
    ) in normalized_review_text
    assert (
        "Partial-domain mathematics is documented as a possible future design "
        "surface, but production payloads that drop `B_closed` while retaining "
        "states that can reach it remain unsupported."
    ) not in normalized_review_text

    assert (
        "Under the current global production protocol, this refuses with "
        "`non_almost_sure_absorption_domain` before CTMC generator construction "
        "or solve."
    ) in normalized_review_text
    assert (
        "This is a protocol-domain refusal, not a mathematical claim that "
        "partial-domain probabilities do not exist."
    ) in normalized_review_text


def _symbol_row(symbol_text: str, symbol: str) -> str:
    for line in symbol_text.splitlines():
        if line.startswith(f"| `{symbol}` |"):
            return line
    raise AssertionError(f"missing symbol row: {symbol}")


def _symbol_rows(symbol_text: str, symbol: str) -> list[str]:
    return [
        line for line in symbol_text.splitlines() if line.startswith(f"| `{symbol}` |")
    ]
