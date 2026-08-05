from __future__ import annotations

import hashlib
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TypeAlias, cast

import ims_deadlock.g6b_schema_contracts as contracts
from ims_deadlock.g6b_canonical_json import (
    CanonicalJsonError,
    JsonValue,
    canonical_bytes_v2,
    canonical_sha256_v2,
    finalized_self_hash,
    loads_v2,
)

JsonObject: TypeAlias = dict[str, JsonValue]

__all__ = (
    "select_allowed_value",
    "build_authority_lock_records",
    "build_authority_source_records",
    "build_retired_fingerprint_records",
    "write_normalization_authorization",
    "write_authority_lock_record",
    "write_authority_source_record",
    "write_fingerprint_record",
    "write_normalization_manifest",
    "run_normalization",
    "main",
)

_AUTHORIZATION_FILE = "normalization_authorization.json"
_MANIFEST_FILE = "normalization_manifest.json"
_LOCK_DIR = "authority_locks"
_SOURCE_DIR = "source_records"
_FINGERPRINT_DIR = "fingerprints"
_NORMALIZER_VERSION = "retired-authority-normalizer-source-only-v1"
_G4_CASE_PREFIX = "cases/confirmation/g4/cases/"
_G4_CASE_SUFFIX = ".json"
_G4_PREDICTION_PATH = "cases/confirmation/g4/predictions.json"
_G4_METRIC_PATH = "cases/confirmation/g4/metrics_schema.json"
_G4_STREAM_PATH = "cases/confirmation/g4/random_stream_manifest.json"
_G5_LOCK_PATH = "evidence/g5/G5_EXECUTION_LOCK.json"
_G6R_LOCK_PATH = "evidence/g6/G6_HISTORICAL_REPLAY_LOCK_R3.json"
_G6R_RAW_PATH = "evidence/g6/G6_HISTORICAL_REPLAY_R3_RAW_HASH_MANIFEST.json"
_OUTCOME_SOURCE_PATHS = (
    "evidence/g5/G5_RESULT_SUMMARY.json",
    "evidence/g6/G6_HISTORICAL_REPLAY_FAILURE_LEDGER.json",
    "evidence/g6/G6_HISTORICAL_REPLAY_R3_REPORT.json",
)
_CASE_DIMS = (
    "case_content_sha256",
    "state_snapshot_sha256",
    "route_signature_sha256",
    "parameter_tuple_sha256",
    "sealed_prediction_sha256",
)
_METHOD_DIMS = (
    "random_stream_manifest_sha256",
    "output_root_reservation_sha256",
)
_GROUP_DIMS = ("metric_schema_sha256",)
_RETIRED_SUBJECT_TYPES = {
    "case_unit": "retired_case",
    "method_observation": "retired_method_observation",
    "method_companion_group": "retired_method_companion_group",
}
_RETIRED_SUBUNIT_SUBJECT_TYPE = "retired_case_subunit"
_SUBUNIT_LABEL_BY_KEY = {
    "cell_id": "cell",
    "name": "inequality",
    "monitor_id": "monitor",
}
_G4_KIND_BY_CASE = {
    "G4_ADVERSARIAL_BOUNDARY": "adversarial_snapshot",
    "G4_B05_SUPERVISOR_COMPARATOR": "adapted_candidate_monitor_cover",
    "G4_CRP_OUTSIDE_S4PR": "crp_evidence_audit",
    "G4_CRP_S4PR_AGREE": "crp_evidence_audit",
    "G4_CRP_UNREACHABLE_CANDIDATE": "crp_evidence_audit",
    "G4_IMS_PARAMETER_GRID": "bidirectional_island_grid",
    "G4_L30_RESOURCE_BASELINE": "supplied_l30_inequalities",
    "G4_MEDIUM_ISLAND_REBUILD": "medium_island_rebuild",
    "G4_RECORDER_TARGET_QUANTIFICATION": "fixed_recorder_target",
}
_SUBUNIT_CONTEXT_BY_KIND = {
    "bidirectional_island_grid": (
        "/input_payload/protocol_input/cells/*",
        "cell_id",
        ("generator_id",),
    ),
    "supplied_l30_inequalities": (
        "/input_payload/protocol_input/inequalities/*",
        "name",
        ("capacities", "finite_capacity_s3pr_ens3pr", "inequality_provenance"),
    ),
    "adapted_candidate_monitor_cover": (
        "/input_payload/protocol_input/candidate_monitors/*",
        "monitor_id",
        ("finite_lts", "legal_states", "first_met_bad_states", "state_bound"),
    ),
}
_ABSENT_BY_KIND = {
    ("supplied_l30_inequalities", "state_snapshot_sha256"),
    ("supplied_l30_inequalities", "route_signature_sha256"),
}
_G4_GENERATOR_IDS = (
    "bidirectional_bas_v1",
    "three_island_bas_v1",
    "or_and_reservation_v1",
)
_BIDIRECTIONAL_PARAM_KEYS = (
    "cell_id",
    "machine_capacity",
    "buffer_capacity",
    "agv_count",
    "forward_wip",
    "reverse_wip",
    "service_rate",
    "transfer_rate",
    "release_rate",
    "state_bound",
)
_MEDIUM_PARAM_KEYS = (
    "instance_id",
    "machine_capacity",
    "buffer_capacity",
    "agv_count",
    "route_wip",
    "service_rate",
    "transfer_rate",
    "release_rate",
    "state_bound",
)
_ADVERSARIAL_PARAM_KEYS = (
    "instance_id",
    "fixture_capacity",
    "cart_capacity",
    "reservation_capacity",
    "decision_rate",
    "state_bound",
)
_RATE_PARAM_KEYS = ("service_rate", "transfer_rate", "release_rate", "decision_rate")
_MEDIUM_ROUTE_IDS = ("ABG", "AG", "BAG")


def select_allowed_value(
    source_bytes: bytes,
    *,
    pointer: str,
    selector_rows: Sequence[Mapping[str, JsonValue]],
    requested_use: str,
) -> JsonValue:
    for row in selector_rows:
        if (
            row["allowed_use"] == requested_use
            and row["selector_kind"] == "raw_bytes_only"
        ):
            raise contracts.SchemaContractError("raw_bytes_only_json_parse")
    try:
        decoded = str(source_bytes, "utf-8")
        parsed = loads_v2(decoded)
    except (CanonicalJsonError, UnicodeDecodeError) as exc:
        raise contracts.SchemaContractError(str(exc)) from exc
    if not _pointer_allowed(pointer, selector_rows, requested_use):
        raise contracts.SchemaContractError("source_field_read_violation")
    if pointer == "":
        return parsed
    if pointer[:1] != "/":
        raise contracts.SchemaContractError("json_pointer_contract")
    current = parsed
    raw_parts: list[str] = []
    raw_current: list[str] = []
    for char in pointer:
        if char == "/":
            raw_parts += [_chars_to_string(raw_current)]
            raw_current = []
        else:
            raw_current += [char]
    raw_parts += [_chars_to_string(raw_current)]
    for raw_part in raw_parts[1:]:
        part = _decode_json_pointer_part(raw_part)
        if isinstance(current, Mapping):
            if part not in current:
                raise contracts.SchemaContractError("json_pointer_contract")
            current = current[part]
        elif isinstance(current, Sequence) and not isinstance(current, str | bytes):
            digit = part != ""
            for digit_char in part:
                if digit_char < "0" or digit_char > "9":
                    digit = False
            if not digit:
                raise contracts.SchemaContractError("json_pointer_contract")
            index = int(part)
            if index >= len(current):
                raise contracts.SchemaContractError("json_pointer_contract")
            current = current[index]
        else:
            raise contracts.SchemaContractError("json_pointer_contract")
    return current


def build_authority_lock_records(
    repo_root: Path,
    authorization: Mapping[str, JsonValue],
    source_hashes: Mapping[str, str],
) -> dict[str, JsonObject]:
    del repo_root
    records: dict[str, JsonObject] = {}
    for authority_id in _string_sequence(authorization["authority_ids"]):
        authority_hashes = {
            path: source_hashes[path]
            for path in sorted(source_hashes)
            if _authority_id_for_source(path) == authority_id
        }
        record: JsonObject = {
            "authority_id": authority_id,
            "origin_remote": "zjqc/IMS_deadlock",
            "origin_commit_or_null": _git_or_null(authorization["source_head"]),
            "origin_tree_hash_or_null": _git_or_null(authorization["source_tree_hash"]),
            "origin_lock_artifact_ref": (
                "cases/discovery/g6b/row_families/structural_discovery_v1/"
                f"governance/retired_authority_locks/{authority_id}.json"
            ),
            "origin_artifact_inventory_hash": _hash_mapping(authority_hashes),
            "current_merged_copy_tree_hash": _hash_mapping(authority_hashes),
            "identity_verification_status": (
                "verified_merged_copy_against_historical_hashes"
            ),
            "authority_lock_record_sha256": None,
        }
        record["authority_lock_record_sha256"] = finalized_self_hash(
            record,
            "authority_lock_record_sha256",
        )
        records[authority_id] = record
    return records


def build_authority_source_records(
    repo_root: Path,
    authorization: Mapping[str, JsonValue],
    authority_locks: Mapping[str, Mapping[str, JsonValue]],
) -> dict[str, JsonObject]:
    source_hashes = _existing_source_hashes(
        repo_root,
        _string_sequence(authorization["allowed_source_paths"]),
    )
    selector_rows = _mapping_sequence(authorization["allowed_json_fields_by_source"])
    lock_hashes: dict[str, str] = {}
    for authority_id in authority_locks:
        record = authority_locks[authority_id]
        lock_hashes[authority_id] = _require_string(
            record["authority_lock_record_sha256"]
        )
    records: dict[str, JsonObject] = {}
    for path in source_hashes:
        raw_hash = source_hashes[path]
        authority_id = _authority_id_for_source(path)
        record = {
            "authority_id": authority_id,
            "authority_stage": authority_id,
            "authority_lock_record_sha256": lock_hashes[authority_id],
            "repo_relative_path": path,
            "raw_byte_sha256": raw_hash,
            "declared_historical_hash_or_null": None,
            "declared_hash_algorithm_or_null": None,
            "declared_hash_verified": False,
            "allowed_projection_uses": cast(
                JsonValue,
                _allowed_uses_for_path(path, selector_rows),
            ),
            "contains_outcome_fields": path in _OUTCOME_SOURCE_PATHS,
        }
        records[path] = record
    return records


def build_retired_fingerprint_records(
    repo_root: Path,
    authorization: Mapping[str, JsonValue],
    authority_locks: Mapping[str, Mapping[str, JsonValue]],
    source_records: Mapping[str, Mapping[str, JsonValue]],
) -> dict[str, JsonObject]:
    if not source_records:
        raise contracts.SchemaContractError("missing_retired_authority")
    for authority_id in contracts.RETIRED_AUTHORITY_IDS:
        if authority_id not in authority_locks:
            raise contracts.SchemaContractError("missing_retired_authority")
    selectors = _mapping_sequence(authorization["allowed_json_fields_by_source"])
    source_hashes = {
        path: _require_string(source_records[path]["raw_byte_sha256"])
        for path in sorted(source_records)
    }
    source_bytes: dict[str, bytes] = {}
    unreadable_sources: list[str] = []
    for path in sorted(source_records):
        try:
            source_bytes[path] = _read_authorized_source_bytes(
                repo_root,
                path,
                source_hashes,
            )
        except contracts.SchemaContractError:
            source_bytes[path] = b""
            unreadable_sources += [path]
    records: dict[str, JsonObject] = {}
    g4_unique: dict[tuple[str, str], JsonObject] = {}
    for case_path in _sorted_g4_case_paths(source_records):
        case_id = _case_id_from_retired_path(case_path)
        if case_path in unreadable_sources or not _source_is_canonical_json(
            source_bytes[case_path]
        ):
            _add_g4_unreconstructable_records(
                records,
                case_id,
                case_path,
                source_hashes,
            )
            continue
        try:
            kind = _discriminate_g4_kind(
                case_id,
                source_bytes[case_path],
                _selectors_for_path(case_path, selectors),
            )
            subjects = _g4_subjects(
                case_id,
                kind,
                source_bytes[case_path],
                _selectors_for_path(case_path, selectors),
            )
        except contracts.SchemaContractError:
            _add_g4_unreconstructable_records(
                records,
                case_id,
                case_path,
                source_hashes,
            )
            continue
        for subject in subjects:
            for dimension in _CASE_DIMS:
                record = _g4_record(
                    subject,
                    kind,
                    dimension,
                    case_path,
                    source_bytes,
                    source_hashes,
                    selectors,
                )
                records[_require_string(record["record_id"])] = record
                if (
                    record["dimension_status"] != "unreconstructable_refuse"
                    and subject["subject_id"] == case_id
                ):
                    g4_unique[(case_id, dimension)] = record
            for dimension in _METHOD_DIMS:
                record = _method_record(
                    "G4_FREEZE",
                    case_id,
                    "g4",
                    dimension,
                    _G4_STREAM_PATH,
                    source_bytes,
                    source_hashes,
                    selectors,
                    None,
                )
                records[_require_string(record["record_id"])] = record
                if record["dimension_status"] != "unreconstructable_refuse":
                    g4_unique[(case_id, dimension)] = record
            for dimension in _GROUP_DIMS:
                record = _group_record(
                    "G4_FREEZE",
                    case_id,
                    "g4",
                    dimension,
                    _G4_METRIC_PATH,
                    source_bytes,
                    source_hashes,
                    selectors,
                    None,
                )
                records[_require_string(record["record_id"])] = record
                if record["dimension_status"] != "unreconstructable_refuse":
                    g4_unique[(case_id, dimension)] = record
    _inherit_g5_stage(records, g4_unique, source_bytes, source_hashes, selectors)
    _inherit_g6r_stage(records, g4_unique, source_bytes, source_hashes, selectors)
    _mark_duplicate_lineages(records)
    return records


def _sorted_g4_case_paths(
    source_records: Mapping[str, Mapping[str, JsonValue]],
) -> tuple[str, ...]:
    paths: list[str] = []
    for path in sorted(source_records):
        if _has_prefix(path, _G4_CASE_PREFIX) and _has_suffix(path, _G4_CASE_SUFFIX):
            paths += [path]
    return tuple(paths)


def _source_is_canonical_json(raw: bytes) -> bool:
    try:
        _load_source_object(raw)
    except contracts.SchemaContractError:
        return False
    return True


def _add_g4_unreconstructable_records(
    records: dict[str, JsonObject],
    case_id: str,
    case_path: str,
    source_hashes: Mapping[str, str],
) -> None:
    for dimension in _CASE_DIMS:
        record = _unreconstructable_record(
            "G4_FREEZE",
            "G4_FREEZE",
            dimension,
            case_id,
            case_id,
            _g4_refs_for_dimension(case_path, dimension),
            source_hashes,
        )
        records[_require_string(record["record_id"])] = record
    for dimension in _METHOD_DIMS:
        record = _unreconstructable_record(
            "G4_FREEZE",
            "G4_FREEZE",
            dimension,
            f"{case_id}:exact_companion",
            case_id,
            _g4_refs_for_dimension(case_path, dimension),
            source_hashes,
        )
        records[_require_string(record["record_id"])] = record
    for dimension in _GROUP_DIMS:
        record = _unreconstructable_record(
            "G4_FREEZE",
            "G4_FREEZE",
            dimension,
            f"{case_id}:exact_des_companion_group",
            case_id,
            _g4_refs_for_dimension(case_path, dimension),
            source_hashes,
        )
        records[_require_string(record["record_id"])] = record


def _case_id_from_retired_path(path: str) -> str:
    start = len(_G4_CASE_PREFIX)
    stop = len(path) - len(_G4_CASE_SUFFIX)
    if start >= stop:
        raise contracts.SchemaContractError("retired_projection_unreconstructable")
    return path[start:stop]


def _selectors_for_path(
    path: str,
    selector_rows: Sequence[Mapping[str, JsonValue]],
) -> tuple[Mapping[str, JsonValue], ...]:
    rows: list[Mapping[str, JsonValue]] = []
    for row in selector_rows:
        if _path_pattern_matches(_require_string(row["source_path_pattern"]), path):
            rows += [row]
    return tuple(rows)


def _select_allowed_for_path(
    all_selectors: Sequence[Mapping[str, JsonValue]],
    path: str,
    source_bytes: bytes,
    *,
    pointer: str,
    requested_use: str,
) -> JsonValue:
    return select_allowed_value(
        source_bytes,
        pointer=pointer,
        selector_rows=_selectors_for_path(path, all_selectors),
        requested_use=requested_use,
    )


def _discriminate_g4_kind(
    case_id: str,
    case_bytes: bytes,
    selector_rows: Sequence[Mapping[str, JsonValue]],
) -> str:
    selected = select_allowed_value(
        case_bytes,
        pointer="/input_payload/protocol_kind",
        selector_rows=selector_rows,
        requested_use="case_content_projection",
    )
    if isinstance(selected, str) and selected in _G4_KIND_BY_CASE.values():
        if case_id not in _G4_KIND_BY_CASE or _G4_KIND_BY_CASE[case_id] != selected:
            raise contracts.SchemaContractError("semantic_lineage_ambiguous")
        return selected
    raise contracts.SchemaContractError("retired_projection_unreconstructable")


def _g4_subjects(
    case_id: str,
    kind: str,
    case_bytes: bytes,
    selector_rows: Sequence[Mapping[str, JsonValue]],
) -> tuple[JsonObject, ...]:
    subjects: list[JsonObject] = [
        {
            "subject_id": case_id,
            "owner_object_id": case_id,
            "selector_pointer_or_null": None,
        }
    ]
    if kind not in _SUBUNIT_CONTEXT_BY_KIND:
        return tuple(subjects)
    pointer, key, parent_context = _SUBUNIT_CONTEXT_BY_KIND[kind]
    selected = select_allowed_value(
        case_bytes,
        pointer=_parent_array_pointer(pointer),
        selector_rows=selector_rows,
        requested_use="case_content_projection",
    )
    if not isinstance(selected, Sequence) or isinstance(selected, str | bytes):
        raise contracts.SchemaContractError("retired_projection_unreconstructable")
    seen: list[str] = []
    for entry in selected:
        if not isinstance(entry, Mapping) or key not in entry:
            raise contracts.SchemaContractError("retired_projection_unreconstructable")
        subunit_id = entry[key]
        if not isinstance(subunit_id, str) or subunit_id == "" or subunit_id in seen:
            raise contracts.SchemaContractError("retired_projection_unreconstructable")
        seen += [subunit_id]
        subjects += [
            {
                "subject_id": f"{case_id}:{key}:{subunit_id}",
                "owner_object_id": case_id,
                "selector_pointer_or_null": pointer,
                "selector_key": key,
                "selector_value": subunit_id,
                "parent_context_fields": list(parent_context),
            }
        ]
    return tuple(subjects)


def _g4_record(
    subject: Mapping[str, JsonValue],
    kind: str,
    dimension: str,
    case_path: str,
    source_bytes: Mapping[str, bytes],
    source_hashes: Mapping[str, str],
    all_selectors: Sequence[Mapping[str, JsonValue]],
) -> JsonObject:
    if (
        dimension == "sealed_prediction_sha256"
        and _require_string(subject["subject_id"])
        != _require_string(subject["owner_object_id"])
        and _item_or_none(subject, "selector_key") != "cell_id"
    ):
        return _record(
            "G4_FREEZE",
            "G4_FREEZE",
            dimension,
            _require_string(subject["subject_id"]),
            _require_string(subject["owner_object_id"]),
            (case_path,),
            source_hashes,
            None,
            "case_content_projection",
            None,
            "not_applicable_retired_stage/v1",
            "not_applicable_retired_stage",
            "not_applicable_retired_stage",
            None,
            None,
            None,
        )
    if (kind, dimension) in _ABSENT_BY_KIND:
        return _record(
            "G4_FREEZE",
            "G4_FREEZE",
            dimension,
            _require_string(subject["subject_id"]),
            _require_string(subject["owner_object_id"]),
            (case_path,),
            source_hashes,
            None,
            "case_content_projection",
            None,
            "not_applicable_retired_stage/v1",
            "not_applicable_retired_stage",
            "not_applicable_retired_stage",
            None,
            None,
            None,
        )
    projection = _g4_projection(
        subject,
        kind,
        dimension,
        case_path,
        source_bytes,
        all_selectors,
    )
    refs = _g4_refs_for_dimension(case_path, dimension)
    return _record_from_optional_projection_refs(
        "G4_FREEZE",
        "G4_FREEZE",
        dimension,
        _require_string(subject["subject_id"]),
        _require_string(subject["owner_object_id"]),
        refs,
        source_hashes,
        projection,
        None,
        None,
        None,
    )


def _g4_projection(
    subject: Mapping[str, JsonValue],
    kind: str,
    dimension: str,
    case_path: str,
    source_bytes: Mapping[str, bytes],
    all_selectors: Sequence[Mapping[str, JsonValue]],
) -> JsonObject | None:
    return _derive_g4_projection_from_protocol(
        source_bytes[case_path],
        _selectors_for_path(case_path, all_selectors),
        source_bytes,
        all_selectors,
        subject,
        kind,
        dimension,
    )


def _source_ref(
    authority_id: str,
    path: str,
    pointer: str | None,
    role: str,
) -> JsonObject:
    return {
        "authority_id": authority_id,
        "repo_relative_posix_path": path,
        "json_pointer_or_null": pointer,
        "source_role": role,
    }


def _g4_refs_for_dimension(case_path: str, dimension: str) -> tuple[JsonObject, ...]:
    if dimension == "case_content_sha256":
        return (
            _source_ref(
                "G4_FREEZE",
                case_path,
                "/input_payload",
                "case_content_projection",
            ),
            _source_ref(
                "G4_FREEZE",
                case_path,
                "/expected_outputs_schema",
                "case_content_projection",
            ),
        )
    if dimension == "sealed_prediction_sha256":
        return (
            _source_ref(
                "G4_FREEZE",
                _G4_PREDICTION_PATH,
                "/predictions",
                "prediction_projection",
            ),
        )
    if dimension == "random_stream_manifest_sha256":
        return (
            _source_ref(
                "G4_FREEZE",
                _G4_STREAM_PATH,
                f"/streams_by_case/{_case_id_from_retired_path(case_path)}",
                "random_stream_projection",
            ),
        )
    if dimension == "metric_schema_sha256":
        return (
            _source_ref("G4_FREEZE", _G4_METRIC_PATH, "/metrics", "metric_projection"),
        )
    return (
        _source_ref(
            "G4_FREEZE",
            case_path,
            "/input_payload",
            "case_content_projection",
        ),
    )


def _method_record(
    authority_id: str,
    case_id: str,
    run_role: str,
    dimension: str,
    path: str,
    source_bytes: Mapping[str, bytes],
    source_hashes: Mapping[str, str],
    all_selectors: Sequence[Mapping[str, JsonValue]],
    ancestor_id: str | None,
) -> JsonObject:
    if dimension == "output_root_reservation_sha256" and authority_id == "G4_FREEZE":
        projection = None
        status = "not_applicable_retired_stage"
        reason = "not_applicable_retired_stage"
        schema = "not_applicable_retired_stage/v1"
    else:
        projection = _derive_random_stream_projection(
            source_bytes[path],
            _selectors_for_path(path, all_selectors),
            case_id,
        )
        status = (
            "direct_stored"
            if dimension == "random_stream_manifest_sha256"
            else "derived_by_versioned_normalizer"
        )
        reason = None
        schema = _schema_for_dimension(dimension, projection)
    if projection is None and status != "not_applicable_retired_stage":
        status = "unreconstructable_refuse"
        reason = "retired_projection_unreconstructable"
        schema = "unreconstructable/v1"
    subject_id = (
        f"{case_id}:exact_companion"
        if authority_id == "G4_FREEZE"
        else f"{case_id}:{authority_id}:{run_role}:{dimension}"
    )
    refs = (
        _source_ref(
            authority_id,
            path,
            f"/streams_by_case/{case_id}",
            "random_stream_projection",
        ),
    )
    return _record_with_refs(
        authority_id,
        authority_id,
        dimension,
        subject_id,
        case_id,
        refs,
        source_hashes,
        projection,
        schema,
        status,
        reason,
        "retired_method",
        run_role,
        ancestor_id,
    )


def _group_record(
    authority_id: str,
    case_id: str,
    run_role: str,
    dimension: str,
    path: str,
    source_bytes: Mapping[str, bytes],
    source_hashes: Mapping[str, str],
    all_selectors: Sequence[Mapping[str, JsonValue]],
    ancestor_id: str | None,
) -> JsonObject:
    projection = _derive_metric_projection(
        source_bytes[path],
        _selectors_for_path(path, all_selectors),
        case_id,
    )
    return _record_from_optional_projection_refs(
        authority_id,
        authority_id,
        dimension,
        (
            f"{case_id}:exact_des_companion_group"
            if authority_id == "G4_FREEZE"
            else f"{case_id}:{authority_id}:{run_role}:{dimension}"
        ),
        case_id,
        (_source_ref(authority_id, path, "/metrics", "metric_projection"),),
        source_hashes,
        projection,
        "retired_group",
        None,
        ancestor_id,
    )


def _inherit_stage(
    records: dict[str, JsonObject],
    g4_unique: Mapping[tuple[str, str], JsonObject],
    authority_id: str,
    lock_path: str,
    source_hashes: Mapping[str, str],
) -> None:
    if lock_path not in source_hashes:
        return
    for key in sorted(g4_unique):
        ancestor = g4_unique[key]
        case_id, dimension = key
        record = _record(
            authority_id,
            authority_id,
            dimension,
            f"{case_id}:{authority_id}:{dimension}",
            case_id,
            (lock_path,),
            source_hashes,
            None,
            "lineage_link",
            None,
            _require_string(ancestor["projection_schema_version"]),
            "inherited_from_authority",
            None,
            "retired_inheritance",
            None,
            _require_string(ancestor["record_id"]),
        )
        record["comparison_projection_ref_or_null"] = ancestor[
            "comparison_projection_ref_or_null"
        ]
        record["comparison_projection_sha256_or_null"] = ancestor[
            "comparison_projection_sha256_or_null"
        ]
        record["lineage_id"] = _require_string(ancestor["lineage_id"])
        record["record_provenance_sha256"] = None
        record["record_provenance_sha256"] = finalized_self_hash(
            record,
            "record_provenance_sha256",
        )
        records[_require_string(record["record_id"])] = record


def _inherit_g5_stage(
    records: dict[str, JsonObject],
    g4_unique: Mapping[tuple[str, str], JsonObject],
    source_bytes: Mapping[str, bytes],
    source_hashes: Mapping[str, str],
    all_selectors: Sequence[Mapping[str, JsonValue]],
) -> None:
    if _G5_LOCK_PATH not in source_hashes:
        return
    try:
        lock = _load_source_object(source_bytes[_G5_LOCK_PATH])
    except contracts.SchemaContractError:
        _inherit_unreconstructable(
            records,
            "G5_EXECUTION",
            _G5_LOCK_PATH,
            source_hashes,
            "G5_EXECUTION::unreconstructable::lock",
        )
        return
    cases = _g5_schedule_cases(lock)
    run_labels = _g5_schedule_run_labels(lock)
    for case_id in cases:
        for dimension in (
            *_CASE_DIMS,
            "random_stream_manifest_sha256",
            "metric_schema_sha256",
        ):
            ancestor = _g4_unique_or_none(g4_unique, case_id, dimension)
            if ancestor is not None:
                _copy_inherited_record(
                    records,
                    "G5_EXECUTION",
                    dimension,
                    f"G5_EXECUTION:{case_id}:{dimension}",
                    case_id,
                    _G5_LOCK_PATH,
                    source_hashes,
                    ancestor,
                    "retired_inheritance",
                    "g5",
                )
    for case_id in cases:
        for run_label in run_labels:
            projection = _derive_g5_root_projection(
                lock,
                case_id,
                run_label,
                source_bytes[_G5_LOCK_PATH],
                _selectors_for_path(_G5_LOCK_PATH, all_selectors),
            )
            if projection is None:
                continue
            record = _record_from_optional_projection_refs(
                "G5_EXECUTION",
                "G5_EXECUTION",
                "output_root_reservation_sha256",
                f"G5_EXECUTION:{case_id}:{run_label}",
                case_id,
                (
                    _source_ref(
                        "G5_EXECUTION",
                        _G5_LOCK_PATH,
                        "/output_roots/raw_output_root_relative",
                        "output_root_containment_projection",
                    ),
                    _source_ref(
                        "G5_EXECUTION",
                        _G5_LOCK_PATH,
                        "/execution_schedule",
                        "method_stage_projection",
                    ),
                ),
                source_hashes,
                projection,
                "retired_method",
                run_label,
                None,
            )
            records[_require_string(record["record_id"])] = record


def _inherit_g6r_stage(
    records: dict[str, JsonObject],
    g4_unique: Mapping[tuple[str, str], JsonObject],
    source_bytes: Mapping[str, bytes],
    source_hashes: Mapping[str, str],
    all_selectors: Sequence[Mapping[str, JsonValue]],
) -> None:
    if _G6R_LOCK_PATH not in source_hashes:
        return
    try:
        lock = _load_source_object(source_bytes[_G6R_LOCK_PATH])
    except contracts.SchemaContractError:
        _inherit_unreconstructable(
            records,
            "G6_R_REPLAY_R3",
            _G6R_LOCK_PATH,
            source_hashes,
            "G6_R_REPLAY_R3::unreconstructable::lock",
        )
        return
    cases = _string_sequence(_item_or_default(lock, "case_ids", []))
    run_labels = _string_sequence(_item_or_default(lock, "run_labels", []))
    if not cases or not run_labels:
        _inherit_unreconstructable(
            records,
            "G6_R_REPLAY_R3",
            _G6R_LOCK_PATH,
            source_hashes,
            "G6_R_REPLAY_R3::unreconstructable::schedule",
        )
        return
    for case_id in cases:
        for dimension in (
            "case_content_sha256",
            "state_snapshot_sha256",
            "route_signature_sha256",
            "parameter_tuple_sha256",
            "sealed_prediction_sha256",
            "random_stream_manifest_sha256",
        ):
            ancestor = _find_g6r_ancestor(records, g4_unique, case_id, dimension)
            if ancestor is not None:
                _copy_inherited_record(
                    records,
                    "G6_R_REPLAY_R3",
                    dimension,
                    f"G6_R_REPLAY_R3:{case_id}:{dimension}",
                    case_id,
                    _G6R_LOCK_PATH,
                    source_hashes,
                    ancestor,
                    "retired_inheritance",
                    "g6r",
                )
        metric_ancestor = _g4_unique_or_none(
            g4_unique,
            case_id,
            "metric_schema_sha256",
        )
        metric_projection = _derive_g6r_metric_overlay(lock, metric_ancestor)
        metric_refs = [
            _source_ref(
                "G6_R_REPLAY_R3",
                _G6R_LOCK_PATH,
                "/default_estimand_spec",
                "metric_projection",
            ),
            _source_ref(
                "G6_R_REPLAY_R3",
                _G6R_LOCK_PATH,
                "/default_estimand_spec_sha256",
                "metric_projection",
            ),
        ]
        if metric_ancestor is not None:
            metric_refs = [
                *cast(list[JsonObject], metric_ancestor["source_artifact_refs"]),
                *metric_refs,
            ]
        metric_record = _record_from_optional_projection_refs(
            "G6_R_REPLAY_R3",
            "G6_R_REPLAY_R3",
            "metric_schema_sha256",
            f"G6_R_REPLAY_R3:{case_id}:exact_des_companion_group",
            case_id,
            metric_refs,
            source_hashes,
            metric_projection,
            "retired_group",
            "g6r",
            (
                None
                if metric_ancestor is None
                else _require_string(metric_ancestor["record_id"])
            ),
        )
        if metric_ancestor is not None and metric_projection is not None:
            metric_record["lineage_id"] = _require_string(metric_ancestor["lineage_id"])
            metric_record["record_provenance_sha256"] = None
            metric_record["record_provenance_sha256"] = finalized_self_hash(
                metric_record,
                "record_provenance_sha256",
            )
        records[_require_string(metric_record["record_id"])] = metric_record
    for case_id in cases:
        for run_label in run_labels:
            projection = _derive_g6r_root_projection(
                lock,
                source_bytes,
                case_id,
                run_label,
                _selectors_for_path(_G6R_LOCK_PATH, all_selectors),
            )
            if projection is None:
                continue
            ancestor = _find_g5_root_record(records, case_id)
            root_refs = [
                _source_ref(
                    "G6_R_REPLAY_R3",
                    _G6R_LOCK_PATH,
                    "/output_root",
                    "output_root_containment_projection",
                ),
                _source_ref(
                    "G6_R_REPLAY_R3",
                    _G6R_LOCK_PATH,
                    "/case_ids",
                    "method_stage_projection",
                ),
                _source_ref(
                    "G6_R_REPLAY_R3",
                    _G6R_LOCK_PATH,
                    "/run_labels",
                    "method_stage_projection",
                ),
                _source_ref(
                    "G6_R_REPLAY_R3",
                    _G6R_LOCK_PATH,
                    "/execution_schedule",
                    "method_stage_projection",
                ),
                _source_ref(
                    "G6_R_REPLAY_R3",
                    _G6R_RAW_PATH,
                    "/output_root",
                    "output_root_source_equality_validation",
                ),
            ]
            record = _record_from_optional_projection_refs(
                "G6_R_REPLAY_R3",
                "G6_R_REPLAY_R3",
                "output_root_reservation_sha256",
                f"G6_R_REPLAY_R3:{case_id}:{run_label}",
                case_id,
                root_refs,
                source_hashes,
                projection,
                "retired_method",
                run_label,
                None if ancestor is None else _require_string(ancestor["record_id"]),
            )
            if ancestor is not None and projection is None:
                record["lineage_id"] = _require_string(ancestor["lineage_id"])
                record["record_provenance_sha256"] = None
                record["record_provenance_sha256"] = finalized_self_hash(
                    record,
                    "record_provenance_sha256",
                )
            records[_require_string(record["record_id"])] = record


def _derive_g4_projection_from_protocol(
    case_bytes: bytes,
    selector_rows: Sequence[Mapping[str, JsonValue]],
    source_bytes: Mapping[str, bytes],
    all_selectors: Sequence[Mapping[str, JsonValue]],
    subject: Mapping[str, JsonValue],
    kind: str,
    dimension: str,
) -> JsonObject | None:
    try:
        input_payload = _require_mapping(
            select_allowed_value(
                case_bytes,
                pointer="/input_payload",
                selector_rows=selector_rows,
                requested_use="case_content_projection",
            )
        )
    except contracts.SchemaContractError:
        return None
    subject_id = _require_string(subject["subject_id"])
    protocol_input = _mapping_or_empty(_item_or_none(input_payload, "protocol_input"))
    subunit = _selected_subunit_or_none(subject, protocol_input)
    parent_context = _parent_context(subject, protocol_input)
    if dimension == "case_content_sha256":
        state_projection = _derive_g4_projection_from_protocol(
            case_bytes,
            selector_rows,
            source_bytes,
            all_selectors,
            subject,
            kind,
            "state_snapshot_sha256",
        )
        route_projection = _derive_g4_projection_from_protocol(
            case_bytes,
            selector_rows,
            source_bytes,
            all_selectors,
            subject,
            kind,
            "route_signature_sha256",
        )
        parameter_projection = _derive_g4_projection_from_protocol(
            case_bytes,
            selector_rows,
            source_bytes,
            all_selectors,
            subject,
            kind,
            "parameter_tuple_sha256",
        )
        if (
            state_projection is None
            or route_projection is None
            or parameter_projection is None
        ):
            return None
        return {
            "projection_schema_version": "g4_case_content_projection/v1",
            "input_mode": "retired_protocol_input",
            "input_semantics_version": "g6b-retired-input-section-7.4/v1",
            "state_snapshot_sha256": canonical_sha256_v2(state_projection),
            "route_signature_sha256": canonical_sha256_v2(route_projection),
            "parameter_tuple_sha256": canonical_sha256_v2(parameter_projection),
            "rate_manifest_content_sha256": canonical_sha256_v2(
                _mapping_or_empty(_item_or_none(protocol_input, "rates"))
            ),
            "policy_declaration_content_sha256": canonical_sha256_v2(
                _mapping_or_empty(_item_or_none(protocol_input, "policy"))
            ),
            "selected_target_declaration_sha256": canonical_sha256_v2(
                _mapping_or_empty(_item_or_none(input_payload, "selected_target"))
            ),
            "control_declaration_sha256": canonical_sha256_v2(
                _mapping_or_empty(_item_or_none(input_payload, "control"))
            ),
        }
    if dimension == "state_snapshot_sha256":
        if kind in {
            "adapted_candidate_monitor_cover",
            "crp_evidence_audit",
            "fixed_recorder_target",
        }:
            state_payload = _item_or_none(protocol_input, "finite_lts")
            if not isinstance(state_payload, Mapping):
                return None
            schema = "g4_explicit_state_projection/v1"
            mode = "finite_lts_explicit"
        else:
            params = _required_generator_params(protocol_input, subunit)
            if params is None:
                return None
            state_payload = _generated_state_payload(params)
            schema = "g4_generated_state_projection/v1"
            mode = "reviewed_static_generator_map"
        return {
            "projection_schema_version": schema,
            "input_mode": mode,
            "state_payload_schema_version": "g6b-retired-state-section-7.4/v1",
            "state_payload": cast(JsonValue, state_payload),
        }
    if dimension == "route_signature_sha256":
        if kind in {
            "adapted_candidate_monitor_cover",
            "crp_evidence_audit",
            "fixed_recorder_target",
        }:
            finite_lts = _mapping_or_empty(_item_or_none(protocol_input, "finite_lts"))
            return _explicit_finite_lts_route_projection(finite_lts)
        else:
            params = _required_generator_params(protocol_input, subunit)
            if params is None:
                return None
            return _generated_route_projection(params)
    if dimension == "parameter_tuple_sha256":
        parameter_entries = _parameter_projection_entries(
            kind,
            protocol_input,
            subunit,
            parent_context,
        )
        if parameter_entries is None:
            return None
        return {
            "projection_schema_version": "g4_parameter_projection/v1",
            "parameter_semantics_version": "g6b-retired-parameter-section-7.4/v1",
            "structural_parameter_entries": parameter_entries[
                "structural_parameter_entries"
            ],
            "numeric_parameter_entries": parameter_entries["numeric_parameter_entries"],
            "state_bound": parameter_entries["state_bound"],
            "rate_manifest_content_sha256": canonical_sha256_v2(
                _mapping_or_empty(_item_or_none(protocol_input, "rates"))
            ),
            "policy_declaration_content_sha256": canonical_sha256_v2(
                _mapping_or_empty(_item_or_none(protocol_input, "policy"))
            ),
        }
    if dimension == "sealed_prediction_sha256":
        if subject_id != _require_string(subject["owner_object_id"]):
            if (
                _require_string(_item_or_default(subject, "selector_key", ""))
                != "cell_id"
            ):
                return None
        return _derive_prediction_projection(
            source_bytes,
            all_selectors,
            subject,
        )
    return None


def _derive_random_stream_projection(
    raw: bytes,
    selector_rows: Sequence[Mapping[str, JsonValue]],
    case_id: str,
) -> JsonObject | None:
    try:
        streams = _require_mapping(
            select_allowed_value(
                raw,
                pointer="/streams_by_case",
                selector_rows=selector_rows,
                requested_use="random_stream_projection",
            )
        )
    except contracts.SchemaContractError:
        return None
    stream = _item_or_none(streams, case_id)
    if not isinstance(stream, Mapping):
        return None
    if "seed_root_commitment" not in stream:
        method_role = _item_or_none(stream, "method_role")
        if method_role != "exact_companion":
            return None
        return {
            "projection_schema_version": "g4_stream_projection/v1",
            "applicability_status": "not_applicable_by_protocol",
            "method_role": method_role,
            "reason_code": "exact_method_has_no_random_stream",
        }
    method_role = _item_or_none(stream, "method_role")
    prng_family = _item_or_none(stream, "prng_family")
    prng_version = _item_or_none(stream, "prng_version")
    replicate_plan = _item_or_none(stream, "replicate_plan")
    sampling_plan = _item_or_none(stream, "sampling_plan")
    seed_derivation_rule = _item_or_none(stream, "seed_derivation_rule")
    seed_root = _item_or_none(stream, "seed_root_commitment")
    substream_allocation = _item_or_none(stream, "substream_allocation")
    if (
        not isinstance(method_role, str)
        or not isinstance(prng_family, str)
        or not isinstance(prng_version, str)
        or not isinstance(replicate_plan, Sequence)
        or isinstance(replicate_plan, str | bytes)
        or not isinstance(sampling_plan, Mapping)
        or not isinstance(seed_derivation_rule, str)
        or not isinstance(seed_root, str)
        or not isinstance(substream_allocation, Mapping)
    ):
        return None
    return {
        "projection_schema_version": "g4_stream_projection/v1",
        "applicability_status": "applicable",
        "method_role": method_role,
        "prng_family": prng_family,
        "prng_version": prng_version,
        "replicate_plan": cast(JsonValue, list(replicate_plan)),
        "sampling_plan": cast(JsonValue, dict(sampling_plan)),
        "seed_derivation_rule": seed_derivation_rule,
        "seed_root_commitment": seed_root,
        "substream_allocation": cast(JsonValue, dict(substream_allocation)),
    }


def _derive_metric_projection(
    raw: bytes,
    selector_rows: Sequence[Mapping[str, JsonValue]],
    case_id: str,
) -> JsonObject | None:
    try:
        metrics = _require_mapping(
            select_allowed_value(
                raw,
                pointer="/metrics",
                selector_rows=selector_rows,
                requested_use="metric_projection",
            )
        )
    except contracts.SchemaContractError:
        return None
    required = (
        "estimand_schema_version",
        "metric_entries",
        "aggregation_rules",
        "censoring_rules",
        "failure_rules",
        "scoring_rules",
        "comparability_scope",
    )
    for key in required:
        if key not in metrics:
            return None
    applicability = _item_or_none(metrics, "applicability_by_case")
    applicability_case_id: str | None = None
    if isinstance(applicability, Mapping):
        case_metric = _item_or_none(applicability, case_id)
        if not isinstance(case_metric, Mapping):
            return None
        case_metric_entries = _item_or_none(case_metric, "metric_entries")
        if not isinstance(case_metric_entries, Sequence) or isinstance(
            case_metric_entries, str | bytes
        ):
            return None
        metrics = cast(JsonObject, dict(metrics))
        metrics["metric_entries"] = cast(JsonValue, list(case_metric_entries))
        applicability_case_id = case_id
    if (
        not isinstance(metrics["estimand_schema_version"], str)
        or not isinstance(metrics["metric_entries"], Sequence)
        or isinstance(metrics["metric_entries"], str | bytes)
        or not isinstance(metrics["aggregation_rules"], Sequence)
        or isinstance(metrics["aggregation_rules"], str | bytes)
        or not isinstance(metrics["censoring_rules"], Sequence)
        or isinstance(metrics["censoring_rules"], str | bytes)
        or not isinstance(metrics["failure_rules"], Sequence)
        or isinstance(metrics["failure_rules"], str | bytes)
        or not isinstance(metrics["scoring_rules"], Sequence)
        or isinstance(metrics["scoring_rules"], str | bytes)
        or not isinstance(metrics["comparability_scope"], str)
    ):
        return None
    projection: JsonObject = {
        "projection_schema_version": "g4_metric_projection/v1",
        "estimand_schema_version": metrics["estimand_schema_version"],
        "metric_entries": cast(JsonValue, list(metrics["metric_entries"])),
        "aggregation_rules": cast(JsonValue, list(metrics["aggregation_rules"])),
        "censoring_rules": cast(JsonValue, list(metrics["censoring_rules"])),
        "failure_rules": cast(JsonValue, list(metrics["failure_rules"])),
        "scoring_rules": cast(JsonValue, list(metrics["scoring_rules"])),
        "comparability_scope": metrics["comparability_scope"],
    }
    if applicability_case_id is not None:
        projection["applicability_case_id"] = applicability_case_id
    return projection


def _derive_prediction_projection(
    source_bytes: Mapping[str, bytes],
    all_selectors: Sequence[Mapping[str, JsonValue]],
    subject: Mapping[str, JsonValue],
) -> JsonObject | None:
    if _G4_PREDICTION_PATH not in source_bytes:
        return None
    try:
        predictions = _require_mapping(
            select_allowed_value(
                source_bytes[_G4_PREDICTION_PATH],
                pointer="/predictions",
                selector_rows=_selectors_for_path(_G4_PREDICTION_PATH, all_selectors),
                requested_use="prediction_projection",
            )
        )
    except contracts.SchemaContractError:
        return None
    owner_id = _require_string(subject["owner_object_id"])
    prediction = _item_or_none(predictions, owner_id)
    if not isinstance(prediction, Mapping):
        return None
    selected_prediction = cast(JsonObject, dict(prediction))
    selector_key = _item_or_none(subject, "selector_key")
    selector_value = _item_or_none(subject, "selector_value")
    if isinstance(selector_key, str) and selector_key != "":
        if selector_key != "cell_id" or not isinstance(selector_value, str):
            return None
        cell_predictions = _item_or_none(selected_prediction, "cell_predictions")
        if not isinstance(cell_predictions, Mapping):
            return None
        cell_prediction = _item_or_none(cell_predictions, selector_value)
        if not isinstance(cell_prediction, Mapping):
            return None
        parent_prediction = dict(prediction)
        if "cell_predictions" in parent_prediction:
            del parent_prediction["cell_predictions"]
        parent_projection = _prediction_projection_from_payload(
            parent_prediction,
            "g4_prediction_projection/v1",
        )
        if parent_projection is None:
            return None
        cell_override = dict(cell_prediction)
        declared_cell_id = _item_or_none(cell_override, "cell_id")
        if declared_cell_id is not None and declared_cell_id != selector_value:
            return None
        if "cell_id" in cell_override:
            del cell_override["cell_id"]
        allowed_override_keys = {
            "research_question",
            "directional_hypotheses",
            "falsifiers",
            "mandatory_control_roles",
            "planned_method_roles",
            "scoring_rule",
            "claim_boundary",
        }
        if not cell_override or not set(cell_override) <= allowed_override_keys:
            return None
        merged_prediction = dict(parent_projection)
        for key in sorted(cell_override):
            merged_prediction[key] = cell_override[key]
        return _prediction_projection_from_payload(
            merged_prediction,
            "g4_grid_cell_prediction_projection/v1",
        )
    return _prediction_projection_from_payload(
        selected_prediction,
        "g4_prediction_projection/v1",
    )


def _prediction_projection_from_payload(
    selected_prediction: Mapping[str, JsonValue],
    schema_version: str,
) -> JsonObject | None:
    required = (
        "research_question",
        "directional_hypotheses",
        "falsifiers",
        "mandatory_control_roles",
        "planned_method_roles",
        "scoring_rule",
        "claim_boundary",
    )
    for key in required:
        if key not in selected_prediction:
            return None
    if (
        not isinstance(selected_prediction["research_question"], str)
        or not isinstance(selected_prediction["directional_hypotheses"], Sequence)
        or isinstance(selected_prediction["directional_hypotheses"], str | bytes)
        or not isinstance(selected_prediction["falsifiers"], Sequence)
        or isinstance(selected_prediction["falsifiers"], str | bytes)
        or not isinstance(selected_prediction["mandatory_control_roles"], Sequence)
        or isinstance(selected_prediction["mandatory_control_roles"], str | bytes)
        or not isinstance(selected_prediction["planned_method_roles"], Sequence)
        or isinstance(selected_prediction["planned_method_roles"], str | bytes)
        or not isinstance(selected_prediction["scoring_rule"], Mapping)
        or not isinstance(selected_prediction["claim_boundary"], Mapping)
    ):
        return None
    return {
        "projection_schema_version": schema_version,
        "research_question": selected_prediction["research_question"],
        "directional_hypotheses": cast(
            JsonValue,
            list(selected_prediction["directional_hypotheses"]),
        ),
        "falsifiers": cast(JsonValue, list(selected_prediction["falsifiers"])),
        "mandatory_control_roles": cast(
            JsonValue,
            list(selected_prediction["mandatory_control_roles"]),
        ),
        "planned_method_roles": cast(
            JsonValue,
            list(selected_prediction["planned_method_roles"]),
        ),
        "scoring_rule": cast(JsonValue, dict(selected_prediction["scoring_rule"])),
        "claim_boundary": cast(JsonValue, dict(selected_prediction["claim_boundary"])),
    }


def _copy_inherited_record(
    records: dict[str, JsonObject],
    authority_id: str,
    dimension: str,
    subject_id: str,
    owner_id: str,
    path: str,
    source_hashes: Mapping[str, str],
    ancestor: Mapping[str, JsonValue],
    method_role: str,
    run_role: str | None,
) -> None:
    record = _record(
        authority_id,
        authority_id,
        dimension,
        subject_id,
        owner_id,
        (path,),
        source_hashes,
        None,
        "lineage_link",
        None,
        _require_string(ancestor["projection_schema_version"]),
        "inherited_from_authority",
        None,
        method_role,
        run_role,
        _require_string(ancestor["record_id"]),
    )
    record["comparison_projection_ref_or_null"] = ancestor[
        "comparison_projection_ref_or_null"
    ]
    record["comparison_projection_sha256_or_null"] = ancestor[
        "comparison_projection_sha256_or_null"
    ]
    record["lineage_id"] = _require_string(ancestor["lineage_id"])
    record["record_provenance_sha256"] = None
    record["record_provenance_sha256"] = finalized_self_hash(
        record,
        "record_provenance_sha256",
    )
    records[_require_string(record["record_id"])] = record


def _inherit_unreconstructable(
    records: dict[str, JsonObject],
    authority_id: str,
    path: str,
    source_hashes: Mapping[str, str],
    subject_id: str,
) -> None:
    for dimension in (*_CASE_DIMS, *_METHOD_DIMS, *_GROUP_DIMS):
        record = _record(
            authority_id,
            authority_id,
            dimension,
            f"{subject_id}:{dimension}",
            subject_id,
            (path,),
            source_hashes,
            None,
            "lineage_link",
            None,
            "unreconstructable/v1",
            "unreconstructable_refuse",
            "retired_projection_unreconstructable",
            None,
            None,
            None,
        )
        records[_require_string(record["record_id"])] = record


def _find_g6r_ancestor(
    records: Mapping[str, JsonObject],
    g4_unique: Mapping[tuple[str, str], JsonObject],
    case_id: str,
    dimension: str,
) -> JsonObject | None:
    g5_subject = f"G5_EXECUTION:{case_id}:{dimension}"
    for record_id in sorted(records):
        record = records[record_id]
        if (
            record["source_authority_id"] == "G5_EXECUTION"
            and record["subject_id"] == g5_subject
            and record["dimension"] == dimension
        ):
            return record
    return _g4_unique_or_none(g4_unique, case_id, dimension)


def _find_g5_root_record(
    records: Mapping[str, JsonObject],
    case_id: str,
) -> JsonObject | None:
    for record_id in sorted(records):
        record = records[record_id]
        if (
            record["source_authority_id"] == "G5_EXECUTION"
            and record["subject_id"] == f"G5_EXECUTION:{case_id}:primary"
            and record["dimension"] == "output_root_reservation_sha256"
        ):
            return record
    return None


def _g5_schedule_cases(lock: Mapping[str, JsonValue]) -> tuple[str, ...]:
    return _schedule_cases(lock)


def _g5_schedule_run_labels(lock: Mapping[str, JsonValue]) -> tuple[str, ...]:
    return _schedule_run_labels(lock)


def _schedule_case_runs(
    lock: Mapping[str, JsonValue],
) -> tuple[tuple[str, str], ...]:
    schedule = _item_or_none(lock, "execution_schedule")
    if isinstance(schedule, Mapping):
        schedule = _item_or_none(schedule, "case_runs")
    runs: list[tuple[str, str]] = []
    if isinstance(schedule, Sequence) and not isinstance(schedule, str | bytes):
        for item in schedule:
            if isinstance(item, Mapping):
                case_id = _item_or_none(item, "case_id")
                run_label = _item_or_none(item, "run_label")
                if (
                    isinstance(case_id, str)
                    and case_id != ""
                    and isinstance(run_label, str)
                    and run_label != ""
                    and (case_id, run_label) not in runs
                ):
                    runs += [(case_id, run_label)]
    return tuple(sorted(runs))


def _schedule_cases(lock: Mapping[str, JsonValue]) -> tuple[str, ...]:
    cases: list[str] = []
    for case_id, _run_label in _schedule_case_runs(lock):
        if case_id not in cases:
            cases += [case_id]
    return tuple(sorted(cases))


def _schedule_run_labels(lock: Mapping[str, JsonValue]) -> tuple[str, ...]:
    labels: list[str] = []
    for _case_id, run_label in _schedule_case_runs(lock):
        if run_label not in labels:
            labels += [run_label]
    return tuple(sorted(labels))


def _schedule_has_case_run(
    lock: Mapping[str, JsonValue],
    case_id: str,
    run_label: str,
) -> bool:
    return (case_id, run_label) in _schedule_case_runs(lock)


def _derive_g5_root_projection(
    lock: Mapping[str, JsonValue],
    case_id: str,
    run_label: str,
    raw: bytes,
    selector_rows: Sequence[Mapping[str, JsonValue]],
) -> JsonObject | None:
    if not _schedule_has_case_run(lock, case_id, run_label):
        return None
    try:
        root_value = select_allowed_value(
            raw,
            pointer="/output_roots/raw_output_root_relative",
            selector_rows=selector_rows,
            requested_use="output_root_containment_projection",
        )
    except contracts.SchemaContractError:
        return None
    if not isinstance(root_value, str):
        return None
    root = _normalize_repo_relative_root(root_value)
    if root is None:
        return None
    bundle_id = "synthetic_retired_bundle"
    method_id = f"g5_execution_{_lower_id(case_id)}_{_lower_id(run_label)}"
    projection: JsonObject = {
        "projection_schema_version": "task6/output-root/v1",
        "bundle_id": bundle_id,
        "case_unit_id": case_id,
        "method_observation_id": method_id,
        "run_role": run_label,
        "logical_root_id": f"G5_EXECUTION:{root}",
        "repo_relative_posix_path": _reserved_quantitative_path(
            bundle_id,
            case_id,
            method_id,
            run_label,
        ),
        "reserved": True,
        "materialized": False,
        "reservation_sha256": None,
    }
    projection["reservation_sha256"] = finalized_self_hash(
        projection,
        "reservation_sha256",
    )
    return projection


def _derive_g6r_root_projection(
    lock: Mapping[str, JsonValue],
    source_bytes: Mapping[str, bytes],
    case_id: str,
    run_label: str,
    selector_rows: Sequence[Mapping[str, JsonValue]],
) -> JsonObject | None:
    if not _schedule_has_case_run(lock, case_id, run_label):
        return None
    try:
        root_value = select_allowed_value(
            source_bytes[_G6R_LOCK_PATH],
            pointer="/output_root",
            selector_rows=selector_rows,
            requested_use="output_root_containment_projection",
        )
    except contracts.SchemaContractError:
        return None
    if not isinstance(root_value, str):
        return None
    if _G6R_RAW_PATH not in source_bytes:
        return None
    try:
        raw_manifest = _load_source_object(source_bytes[_G6R_RAW_PATH])
    except contracts.SchemaContractError:
        return None
    raw_root = _item_or_none(raw_manifest, "output_root")
    if not isinstance(raw_root, str) or raw_root != root_value:
        return None
    suffix = _unique_g6r_suffix(root_value)
    if suffix is None:
        return None
    bundle_id = "synthetic_retired_bundle"
    method_id = f"g6_r_replay_r3_{_lower_id(case_id)}_{_lower_id(run_label)}"
    projection: JsonObject = {
        "projection_schema_version": "task6/output-root/v1",
        "bundle_id": bundle_id,
        "case_unit_id": case_id,
        "method_observation_id": method_id,
        "run_role": run_label,
        "logical_root_id": f"G6_R_REPLAY_R3:{suffix}",
        "repo_relative_posix_path": _reserved_quantitative_path(
            bundle_id,
            case_id,
            method_id,
            run_label,
        ),
        "reserved": True,
        "materialized": False,
        "reservation_sha256": None,
    }
    projection["reservation_sha256"] = finalized_self_hash(
        projection,
        "reservation_sha256",
    )
    return projection


def _derive_g6r_metric_overlay(
    lock: Mapping[str, JsonValue],
    ancestor: Mapping[str, JsonValue] | None,
) -> JsonObject | None:
    if ancestor is None:
        return None
    spec = _item_or_none(lock, "default_estimand_spec")
    spec_hash = _item_or_none(lock, "default_estimand_spec_sha256")
    if not isinstance(spec, Mapping) or not isinstance(spec_hash, str):
        return None
    if canonical_sha256_v2(cast(JsonValue, dict(spec))) != spec_hash:
        return None
    required = (
        "estimand_schema_version",
        "metric_entries",
        "aggregation_rules",
        "censoring_rules",
        "failure_rules",
        "scoring_rules",
        "comparability_scope",
    )
    for key in required:
        if key not in spec:
            return None
    if (
        not isinstance(spec["estimand_schema_version"], str)
        or not isinstance(spec["metric_entries"], Sequence)
        or isinstance(spec["metric_entries"], str | bytes)
        or not isinstance(spec["aggregation_rules"], Sequence)
        or isinstance(spec["aggregation_rules"], str | bytes)
        or not isinstance(spec["censoring_rules"], Sequence)
        or isinstance(spec["censoring_rules"], str | bytes)
        or not isinstance(spec["failure_rules"], Sequence)
        or isinstance(spec["failure_rules"], str | bytes)
        or not isinstance(spec["scoring_rules"], Sequence)
        or isinstance(spec["scoring_rules"], str | bytes)
        or not isinstance(spec["comparability_scope"], str)
    ):
        return None
    return {
        "projection_schema_version": "g6r_metric_overlay_projection/v1",
        "default_estimand_spec_sha256": spec_hash,
        "estimand_schema_version": spec["estimand_schema_version"],
        "metric_entries": cast(JsonValue, list(spec["metric_entries"])),
        "aggregation_rules": cast(JsonValue, list(spec["aggregation_rules"])),
        "censoring_rules": cast(JsonValue, list(spec["censoring_rules"])),
        "failure_rules": cast(JsonValue, list(spec["failure_rules"])),
        "scoring_rules": cast(JsonValue, list(spec["scoring_rules"])),
        "comparability_scope": spec["comparability_scope"],
    }


def _mark_duplicate_lineages(records: Mapping[str, JsonObject]) -> None:
    canonical_by_lineage: dict[str, str] = {}
    for record_id in sorted(records):
        record = records[record_id]
        if record["inherited_from_record_id_or_null"] is not None:
            continue
        lineage = _require_string(record["lineage_id"])
        if lineage not in canonical_by_lineage:
            canonical_by_lineage[lineage] = record_id
            continue
        record["duplicate_lineage_of_record_id_or_null"] = canonical_by_lineage[lineage]
        record["record_provenance_sha256"] = None
        record["record_provenance_sha256"] = finalized_self_hash(
            record,
            "record_provenance_sha256",
        )


def _record_from_optional_projection(
    authority_id: str,
    source_stage: str,
    dimension: str,
    subject_id: str,
    owner_id: str,
    paths: Sequence[str],
    source_hashes: Mapping[str, str],
    pointer: str | None,
    role: str,
    projection: Mapping[str, JsonValue] | None,
    method_role: str | None,
    inherited_id: str | None,
) -> JsonObject:
    if projection is None:
        return _record(
            authority_id,
            source_stage,
            dimension,
            subject_id,
            owner_id,
            paths,
            source_hashes,
            None,
            role,
            None,
            "unreconstructable/v1",
            "unreconstructable_refuse",
            "retired_projection_unreconstructable",
            method_role,
            None,
            inherited_id,
        )
    return _record(
        authority_id,
        source_stage,
        dimension,
        subject_id,
        owner_id,
        paths,
        source_hashes,
        pointer,
        role,
        projection,
        _schema_for_dimension(dimension, projection),
        "derived_by_versioned_normalizer",
        None,
        method_role,
        None,
        inherited_id,
    )


def _record_from_optional_projection_refs(
    authority_id: str,
    source_stage: str,
    dimension: str,
    subject_id: str,
    owner_id: str,
    refs: Sequence[Mapping[str, JsonValue]],
    source_hashes: Mapping[str, str],
    projection: Mapping[str, JsonValue] | None,
    method_role: str | None,
    run_role: str | None,
    inherited_id: str | None,
) -> JsonObject:
    if projection is None:
        return _record_with_refs(
            authority_id,
            source_stage,
            dimension,
            subject_id,
            owner_id,
            refs,
            source_hashes,
            None,
            "unreconstructable/v1",
            "unreconstructable_refuse",
            "retired_projection_unreconstructable",
            method_role,
            run_role,
            inherited_id,
        )
    return _record_with_refs(
        authority_id,
        source_stage,
        dimension,
        subject_id,
        owner_id,
        refs,
        source_hashes,
        projection,
        _schema_for_dimension(dimension, projection),
        "derived_by_versioned_normalizer",
        None,
        method_role,
        run_role,
        inherited_id,
    )


def _unreconstructable_record(
    authority_id: str,
    source_stage: str,
    dimension: str,
    subject_id: str,
    owner_id: str,
    refs: Sequence[Mapping[str, JsonValue]],
    source_hashes: Mapping[str, str],
) -> JsonObject:
    return _record_with_refs(
        authority_id,
        source_stage,
        dimension,
        subject_id,
        owner_id,
        refs,
        source_hashes,
        None,
        "unreconstructable/v1",
        "unreconstructable_refuse",
        "retired_projection_unreconstructable",
        None,
        None,
        None,
    )


def _record(
    authority_id: str,
    source_stage: str,
    dimension: str,
    subject_id: str,
    owner_id: str,
    paths: Sequence[str],
    source_hashes: Mapping[str, str],
    pointer: str | None,
    role: str,
    projection: Mapping[str, JsonValue] | None,
    schema: str,
    status: str,
    reason: str | None,
    method_role: str | None,
    run_role: str | None,
    inherited_id: str | None,
) -> JsonObject:
    refs = [
        {
            "authority_id": authority_id,
            "repo_relative_posix_path": path,
            "json_pointer_or_null": pointer,
            "source_role": role,
        }
        for path in paths
    ]
    return _record_with_refs(
        authority_id,
        source_stage,
        dimension,
        subject_id,
        owner_id,
        refs,
        source_hashes,
        projection,
        schema,
        status,
        reason,
        method_role,
        run_role,
        inherited_id,
    )


def _record_with_refs(
    authority_id: str,
    source_stage: str,
    dimension: str,
    subject_id: str,
    owner_id: str,
    refs: Sequence[Mapping[str, JsonValue]],
    source_hashes: Mapping[str, str],
    projection: Mapping[str, JsonValue] | None,
    schema: str,
    status: str,
    reason: str | None,
    method_role: str | None,
    run_role: str | None,
    inherited_id: str | None,
) -> JsonObject:
    projection_hash = (
        None if projection is None else canonical_sha256_v2(dict(projection))
    )
    record_id = _record_identity(
        authority_id,
        subject_id,
        dimension,
        projection_hash,
        status,
    )
    refs_value = [cast(JsonObject, dict(ref)) for ref in refs]
    byte_hashes = {
        _require_string(ref["repo_relative_posix_path"]): source_hashes[
            _require_string(ref["repo_relative_posix_path"])
        ]
        for ref in refs_value
    }
    record: JsonObject = {
        "record_schema_version": "ims-deadlock/g6b-fingerprint-record/v1",
        "record_id": record_id,
        "dimension": dimension,
        "projection_kind": contracts.DIMENSION_PROJECTION_KINDS[dimension],
        "subject_type": _retired_subject_type(dimension, subject_id, owner_id),
        "subject_id": subject_id,
        "owner_object_id": owner_id,
        "projection_schema_version": schema,
        "comparison_projection_ref_or_null": (
            None if projection_hash is None else f"retired-normalizer://{record_id}"
        ),
        "comparison_projection_sha256_or_null": projection_hash,
        "canonicalization_version": contracts.G6B_CANONICAL_JSON_VERSION,
        "source_authority_id": authority_id,
        "source_stage": source_stage,
        "source_method_role_or_null": method_role,
        "source_run_role_or_null": run_role,
        "source_artifact_refs": cast(JsonValue, refs_value),
        "source_artifact_byte_hashes": cast(JsonObject, byte_hashes),
        "normalizer_version": _NORMALIZER_VERSION,
        "dimension_status": status,
        "lineage_id": "",
        "inherited_from_record_id_or_null": inherited_id,
        "duplicate_lineage_of_record_id_or_null": None,
        "depends_on_dimensions": cast(
            JsonValue,
            sorted(contracts.DIMENSION_DEPENDS_ON[dimension]),
        ),
        "correlated_with_dimensions": cast(
            JsonValue,
            sorted(contracts.DIMENSION_CORRELATED_WITH[dimension]),
        ),
        "comparison_policy": contracts.DIMENSION_POLICIES[dimension],
        "applicability_reason_code_or_null": reason,
        "record_provenance_sha256": None,
    }
    record["lineage_id"] = _lineage_id(record)
    record["record_provenance_sha256"] = finalized_self_hash(
        record,
        "record_provenance_sha256",
    )
    return record


def _lineage_id(record: Mapping[str, JsonValue]) -> str:
    source_hashes = cast(Mapping[str, JsonValue], record["source_artifact_byte_hashes"])
    preimage: JsonObject = {
        "origin_authority_id": record["source_authority_id"],
        "origin_subject_type": record["subject_type"],
        "origin_subject_id": record["subject_id"],
        "origin_dimension": record["dimension"],
        "origin_comparison_projection_sha256_or_null": record[
            "comparison_projection_sha256_or_null"
        ],
        "origin_source_artifact_byte_hashes": {
            path: source_hashes[path] for path in sorted(source_hashes)
        },
    }
    return f"sha256:{canonical_sha256_v2(preimage)}"


def _retired_subject_type(dimension: str, subject_id: str, owner_id: str) -> str:
    del owner_id
    if dimension in {
        "case_content_sha256",
        "state_snapshot_sha256",
        "route_signature_sha256",
        "parameter_tuple_sha256",
        "sealed_prediction_sha256",
    } and _is_explicit_g4_subunit_subject(subject_id):
        return _RETIRED_SUBUNIT_SUBJECT_TYPE
    base_subject = contracts.DIMENSION_SUBJECTS[dimension]
    return _RETIRED_SUBJECT_TYPES[_require_string(base_subject)]


def _record_identity(
    authority_id: str,
    subject_id: str,
    dimension: str,
    projection_hash: str | None,
    status: str,
) -> str:
    digest = canonical_sha256_v2(
        {
            "authority_id": authority_id,
            "subject_id": subject_id,
            "dimension": dimension,
            "projection_sha256_or_null": projection_hash,
            "status": status,
        }
    )
    return f"{authority_id}:{dimension}:{digest}"


def _schema_for_dimension(
    dimension: str,
    projection: Mapping[str, JsonValue] | None,
) -> str:
    if projection is not None and "projection_schema_version" in projection:
        version = projection["projection_schema_version"]
        if isinstance(version, str) and version != "":
            return version
    if dimension == "case_content_sha256":
        return "g4_case_content_projection/v1"
    if dimension == "state_snapshot_sha256":
        return "g4_explicit_state_projection/v1"
    if dimension == "route_signature_sha256":
        return "g4_explicit_route_projection/v1"
    if dimension == "parameter_tuple_sha256":
        return "g4_parameter_projection/v1"
    if dimension == "sealed_prediction_sha256":
        return "g4_prediction_projection/v1"
    if dimension == "random_stream_manifest_sha256":
        return "g4_stream_projection/v1"
    if dimension == "output_root_reservation_sha256":
        return "g5_output_root_projection/v1"
    return "g4_metric_projection/v1"


def write_normalization_authorization(
    authorized_root: Path,
    authorization_bytes: bytes,
) -> str:
    root = Path(authorized_root)
    value = _load_canonical_object(authorization_bytes, "noncanonical_authorization")
    if canonical_bytes_v2(value) != authorization_bytes:
        raise contracts.SchemaContractError("noncanonical_authorization")
    _require_authorized_root(root, value)
    if Path(root).exists():
        raise contracts.SchemaContractError("preexisting")
    _reject_symlink_components(root)
    parent_candidate = Path(root / "..")
    _reject_symlink_components(parent_candidate)
    parent = Path(parent_candidate).resolve()
    _reject_symlink_components(parent)
    Path(parent).mkdir(exist_ok=True)
    Path(root).mkdir()
    destination = root / _AUTHORIZATION_FILE
    temporary = root / f"{_AUTHORIZATION_FILE}.tmp"
    if Path(destination).exists() or Path(temporary).exists():
        raise contracts.SchemaContractError("preexisting")
    Path(temporary).write_bytes(authorization_bytes)
    digest = hashlib.sha256(Path(temporary).read_bytes()).hexdigest()
    if digest != hashlib.sha256(authorization_bytes).hexdigest():
        raise contracts.SchemaContractError("retired_authority_hash_mismatch")
    Path(temporary).replace(destination)
    return digest


def write_authority_lock_record(
    authorized_root: Path,
    authority_id: str,
    record: Mapping[str, JsonValue],
) -> str:
    root = Path(authorized_root)
    if record["authority_id"] != authority_id:
        raise contracts.SchemaContractError("illegal_retired_authority")
    _require_record_root(root)
    if authority_id not in contracts.RETIRED_AUTHORITY_IDS or "/" in authority_id:
        raise contracts.SchemaContractError("illegal_retired_authority")
    directory = root / _LOCK_DIR
    if Path(directory).is_symlink():
        raise contracts.SchemaContractError("symlink")
    destination = directory / f"{authority_id}.json"
    _reject_symlink_components(destination)
    payload = canonical_bytes_v2(cast(JsonObject, dict(record)))
    Path(directory).mkdir(exist_ok=True)
    temporary = directory / f"{authority_id}.json.tmp"
    if Path(destination).exists() or Path(temporary).exists():
        raise contracts.SchemaContractError("preexisting")
    Path(temporary).write_bytes(payload)
    digest = hashlib.sha256(Path(temporary).read_bytes()).hexdigest()
    if digest != hashlib.sha256(payload).hexdigest():
        raise contracts.SchemaContractError("retired_authority_hash_mismatch")
    Path(temporary).replace(destination)
    result = _require_string(record["authority_lock_record_sha256"])
    return result


def write_authority_source_record(
    authorized_root: Path,
    repo_relative_source_path: str,
    record: Mapping[str, JsonValue],
) -> str:
    root = Path(authorized_root)
    if (
        repo_relative_source_path
        not in contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY
    ):
        raise contracts.SchemaContractError("source_outside_retired_inventory")
    if record["repo_relative_path"] != repo_relative_source_path:
        raise contracts.SchemaContractError("source_outside_retired_inventory")
    _require_record_root(root)
    directory = root / _SOURCE_DIR
    if Path(directory).is_symlink():
        raise contracts.SchemaContractError("symlink")
    destination = directory / f"{_sha256_text(repo_relative_source_path)}.json"
    _reject_symlink_components(destination)
    payload = canonical_bytes_v2(cast(JsonObject, dict(record)))
    Path(directory).mkdir(exist_ok=True)
    temporary = directory / f"{_sha256_text(repo_relative_source_path)}.json.tmp"
    if Path(destination).exists() or Path(temporary).exists():
        raise contracts.SchemaContractError("preexisting")
    Path(temporary).write_bytes(payload)
    digest = hashlib.sha256(Path(temporary).read_bytes()).hexdigest()
    if digest != hashlib.sha256(payload).hexdigest():
        raise contracts.SchemaContractError("retired_authority_hash_mismatch")
    Path(temporary).replace(destination)
    return digest


def write_fingerprint_record(
    authorized_root: Path,
    record_id: str,
    record: Mapping[str, JsonValue],
) -> str:
    root = Path(authorized_root)
    if record["record_id"] != record_id or "/" in record_id or "\\" in record_id:
        raise contracts.SchemaContractError("record_id")
    _require_record_root(root)
    directory = root / _FINGERPRINT_DIR
    if Path(directory).is_symlink():
        raise contracts.SchemaContractError("symlink")
    destination = directory / f"{_sha256_text(record_id)}.json"
    _reject_symlink_components(destination)
    payload = canonical_bytes_v2(cast(JsonObject, dict(record)))
    Path(directory).mkdir(exist_ok=True)
    temporary = directory / f"{_sha256_text(record_id)}.json.tmp"
    if Path(destination).exists() or Path(temporary).exists():
        raise contracts.SchemaContractError("preexisting")
    Path(temporary).write_bytes(payload)
    digest = hashlib.sha256(Path(temporary).read_bytes()).hexdigest()
    if digest != hashlib.sha256(payload).hexdigest():
        raise contracts.SchemaContractError("retired_authority_hash_mismatch")
    Path(temporary).replace(destination)
    result = _require_string(record["record_provenance_sha256"])
    return result


def write_normalization_manifest(
    authorized_root: Path,
    manifest: Mapping[str, JsonValue],
) -> str:
    root = Path(authorized_root)
    _require_record_root(root)
    _verify_manifest_references(root, manifest)
    directory = root
    destination = directory / _MANIFEST_FILE
    _reject_symlink_components(destination)
    payload = canonical_bytes_v2(cast(JsonObject, dict(manifest)))
    temporary = directory / f"{_MANIFEST_FILE}.tmp"
    if Path(destination).exists() or Path(temporary).exists():
        raise contracts.SchemaContractError("preexisting")
    Path(temporary).write_bytes(payload)
    digest = hashlib.sha256(Path(temporary).read_bytes()).hexdigest()
    if digest != hashlib.sha256(payload).hexdigest():
        raise contracts.SchemaContractError("retired_authority_hash_mismatch")
    Path(temporary).replace(destination)
    return digest


def run_normalization(
    repo_root: Path,
    authorization_path: Path,
    output_root: Path,
) -> JsonObject:
    root = Path(output_root)
    repo = Path(repo_root)
    auth_path = Path(authorization_path)
    if Path(root).exists() and not Path(root / _MANIFEST_FILE).is_file():
        raise contracts.SchemaContractError("incomplete")
    if Path(root).exists():
        raise contracts.SchemaContractError("preexisting")
    authority_bytes = read_authority_bytes(auth_path)
    selector_rows = parse_allowed_json_pointers(authority_bytes)
    authorization = _load_canonical_object(
        authority_bytes,
        "normalization_authorization",
    )
    _verify_output_root(repo, root, authorization)
    # Task 9's external execution lock is the independent identity gate.  The
    # expected values below validate record shape only and are not authorization proof.
    contracts.validate_normalization_authorization(
        authorization,
        expected_schema_inventory_patterns=contracts.EXPECTED_RETIRED_SOURCE_INVENTORY,
        expected_concrete_source_paths=contracts.EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY,
        expected_selector_matrix=selector_rows,
        expected_git_object_format="sha1",
        expected_source_head=_require_string(authorization["source_head"]),
        expected_source_tree_hash=_require_string(authorization["source_tree_hash"]),
        expected_file_manifest_hash=_require_string(
            authorization["expected_file_manifest_hash"]
        ),
        expected_normalizer_code_sha256=_require_string(
            authorization["normalizer_code_sha256"]
        ),
        expected_review_artifact_hash=_require_string(
            authorization["review_artifact_hash"]
        ),
        expected_output_root=_require_string(
            cast(Mapping[str, JsonValue], authorization["allowed_output_root"])[
                "repo_relative_posix_path"
            ]
        ),
    )
    source_hashes = verify_source_hashes(repo, authority_bytes)
    locks = build_authority_lock_records(repo, authorization, source_hashes)
    sources = build_authority_source_records(repo, authorization, locks)
    fingerprints = build_retired_fingerprint_records(
        repo,
        authorization,
        locks,
        sources,
    )
    selected_input_bytes = _selected_input_projection_bytes(
        repo,
        authorization,
        source_hashes,
    )
    historical_decimal_bundle = parse_historical_decimal_exactly(selected_input_bytes)
    fingerprint_projection_value = cast(JsonValue, fingerprints)
    projection = apply_static_input_projection(
        {
            "fingerprint_records": fingerprint_projection_value,
            "numeric_selected_bundle": historical_decimal_bundle,
        }
    )
    canonical_projection = canonicalize_projection_v2(projection)
    projection_sha256 = compute_sha256(canonical_projection)
    if projection_sha256 != canonical_sha256_v2(projection):
        raise contracts.SchemaContractError("retired_normalizer_error")
    projected_fingerprints = _require_mapping(projection["fingerprint_records"])
    authorization_sha = write_normalization_authorization(root, authority_bytes)
    for authority_id in contracts.RETIRED_AUTHORITY_IDS:
        write_authority_lock_record(root, authority_id, locks[authority_id])
    for source_path in sorted(sources):
        write_authority_source_record(root, source_path, sources[source_path])
    for record_id in sorted(projected_fingerprints):
        write_fingerprint_record(
            root,
            record_id,
            _require_mapping(projected_fingerprints[record_id]),
        )
    manifest = _manifest_from_records(
        authorization_sha,
        locks,
        sources,
        cast(Mapping[str, Mapping[str, JsonValue]], projected_fingerprints),
        source_hashes,
        authorization,
    )
    write_normalization_manifest(root, manifest)
    return cast(
        JsonObject,
        {"selector_rows": list(selector_rows), "manifest": manifest},
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    expected = ["--authorization", "--repo-root", "--output-root"]
    if (
        len(args) != 6
        or args[0] != expected[0]
        or args[2] != expected[1]
        or args[4] != expected[2]
    ):
        raise SystemExit(2)
    run_normalization(Path(args[3]), Path(args[1]), Path(args[5]))
    return 0


def read_authority_bytes(path: Path) -> bytes:
    target = Path(path)
    if not Path(target).is_file() or Path(target).is_symlink():
        raise contracts.SchemaContractError("missing_retired_authority")
    authority_file_bytes = Path(target).read_bytes()
    return authority_file_bytes


def parse_allowed_json_pointers(
    authority_bytes: bytes,
) -> Sequence[Mapping[str, JsonValue]]:
    record = _load_canonical_object(authority_bytes, "normalization_authorization")
    rows = record["allowed_json_fields_by_source"]
    parsed_rows = _mapping_sequence(rows)
    return parsed_rows


def verify_source_hashes(repo_root: Path, authority_bytes: bytes) -> dict[str, str]:
    record = _load_canonical_object(authority_bytes, "normalization_authorization")
    hashes = _existing_source_hashes(
        repo_root,
        _string_sequence(record["allowed_source_paths"]),
    )
    if _hash_mapping(hashes) != record["expected_file_manifest_hash"]:
        raise contracts.SchemaContractError("file_manifest_drift")
    return hashes


def _selected_input_projection_bytes(
    repo_root: Path,
    authorization: Mapping[str, JsonValue],
    source_hashes: Mapping[str, str],
) -> bytes:
    selector_rows = _mapping_sequence(authorization["allowed_json_fields_by_source"])
    selected_inputs: JsonObject = {}
    for source_path in sorted(source_hashes):
        if not _has_prefix(source_path, _G4_CASE_PREFIX) or not _has_suffix(
            source_path,
            _G4_CASE_SUFFIX,
        ):
            continue
        selected_source_bytes = _read_authorized_source_bytes(
            repo_root,
            source_path,
            source_hashes,
        )
        selected_input = select_allowed_value(
            selected_source_bytes,
            pointer="/input_payload",
            selector_rows=_selectors_for_path(source_path, selector_rows),
            requested_use="case_content_projection",
        )
        selected_inputs[source_path] = selected_input
    if not selected_inputs:
        raise contracts.SchemaContractError("retired_projection_unreconstructable")
    return canonical_bytes_v2({"selected_input_payloads": selected_inputs})


def parse_historical_decimal_exactly(numeric_source_bytes: bytes) -> JsonValue:
    value = _load_canonical_object(
        numeric_source_bytes,
        "selected_input_projection",
    )
    if set(value) == {"decimal"}:
        return _canonicalized_decimal_value_strict(value)
    if set(value) != {"selected_input_payloads"}:
        raise contracts.SchemaContractError("retired_projection_unreconstructable")
    selected_inputs = _item_or_none(value, "selected_input_payloads")
    if not isinstance(selected_inputs, Mapping) or not selected_inputs:
        raise contracts.SchemaContractError("retired_projection_unreconstructable")
    return {
        "selected_input_payloads": _canonicalized_decimal_value(
            cast(JsonValue, dict(selected_inputs))
        ),
    }


def apply_static_input_projection(value: Mapping[str, JsonValue]) -> JsonObject:
    if set(value) != {"fingerprint_records", "numeric_selected_bundle"}:
        raise contracts.SchemaContractError("retired_projection_unreconstructable")
    fingerprint_records = _require_mapping(value["fingerprint_records"])
    numeric_selected_bundle = _require_mapping(value["numeric_selected_bundle"])
    if not fingerprint_records or not numeric_selected_bundle:
        raise contracts.SchemaContractError("retired_projection_unreconstructable")
    return {
        "fingerprint_records": cast(JsonValue, fingerprint_records),
        "numeric_selected_bundle": cast(JsonValue, numeric_selected_bundle),
    }


def canonicalize_projection_v2(value: Mapping[str, JsonValue]) -> bytes:
    return canonical_bytes_v2(cast(JsonObject, dict(value)))


def compute_sha256(value: bytes) -> str:
    digest = hashlib.sha256(value).hexdigest()
    return digest


def _read_authorized_source_bytes(
    repo_root: Path,
    repo_relative_source_path: str,
    expected_hashes: Mapping[str, str],
) -> bytes:
    repo_root_path = Path(repo_root)
    if repo_relative_source_path not in expected_hashes:
        raise contracts.SchemaContractError("source_outside_retired_inventory")
    if repo_relative_source_path[:1] == "/" or _contains_parent_part(
        repo_relative_source_path
    ):
        raise contracts.SchemaContractError("source_outside_retired_inventory")
    repo = Path(repo_root_path).resolve()
    candidate = repo_root_path / repo_relative_source_path
    _reject_symlink_components(candidate)
    try:
        Path(candidate).resolve().relative_to(repo)
    except ValueError as exc:
        raise contracts.SchemaContractError("source_outside_retired_inventory") from exc
    if not Path(candidate).is_file():
        raise contracts.SchemaContractError("missing_retired_authority")
    raw = Path(candidate).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_hashes[repo_relative_source_path]:
        raise contracts.SchemaContractError("retired_authority_hash_mismatch")
    return bytes(raw)


def _pointer_allowed(
    pointer: str,
    selector_rows: Sequence[Mapping[str, JsonValue]],
    requested_use: str,
) -> bool:
    for row in selector_rows:
        if row["allowed_use"] != requested_use:
            continue
        if row["selector_kind"] == "raw_bytes_only":
            return False
        selectors = _string_sequence(row["selectors"])
        for selector in selectors:
            if _selector_matches(selector, row["selector_kind"], pointer):
                return True
    return False


def _selector_matches(selector: str, selector_kind: JsonValue, pointer: str) -> bool:
    if selector_kind == "exact_pointer_set":
        return pointer == selector
    if selector_kind == "prefix_set":
        return pointer == selector or (
            len(pointer) > len(selector)
            and pointer[: len(selector)] == selector
            and pointer[len(selector)] == "/"
        )
    if selector_kind == "element_pointer_pattern_set":
        return _element_pointer_matches(selector, pointer)
    return False


def _element_pointer_matches(selector: str, pointer: str) -> bool:
    selector_parts = _slash_parts(selector)
    pointer_parts = _slash_parts(pointer)
    if len(selector_parts) != len(pointer_parts):
        return False
    for expected, observed in zip(selector_parts, pointer_parts, strict=True):
        if expected == "*":
            if not _decimal_digits(observed):
                return False
        elif expected != observed:
            return False
    return True


def _load_canonical_object(raw: bytes, code: str) -> JsonObject:
    try:
        value = loads_v2(str(raw, "utf-8"))
    except (CanonicalJsonError, UnicodeDecodeError) as exc:
        raise contracts.SchemaContractError(code) from exc
    if not isinstance(value, dict):
        raise contracts.SchemaContractError(code)
    return value


def _load_source_object(raw: bytes) -> JsonObject:
    return _load_canonical_object(raw, "retired_projection_unreconstructable")


def _require_mapping(value: JsonValue) -> JsonObject:
    if not isinstance(value, Mapping):
        raise contracts.SchemaContractError("retired_projection_unreconstructable")
    return cast(JsonObject, dict(value))


def _mapping_or_empty(value: JsonValue | object) -> JsonObject:
    if isinstance(value, Mapping):
        return cast(JsonObject, dict(value))
    return {}


def _item_or_none(value: Mapping[str, JsonValue], key: str) -> JsonValue | None:
    if key in value:
        return value[key]
    return None


def _item_or_default(
    value: Mapping[str, JsonValue],
    key: str,
    default: JsonValue,
) -> JsonValue:
    if key in value:
        return value[key]
    return default


def _g4_unique_or_none(
    records: Mapping[tuple[str, str], JsonObject],
    case_id: str,
    dimension: str,
) -> JsonObject | None:
    key = (case_id, dimension)
    if key in records:
        return records[key]
    return None


def _json_object_or_null(value: Mapping[str, JsonValue] | None) -> JsonObject:
    if value is None:
        return {"value": None}
    return cast(JsonObject, dict(value))


def _string_or_default(value: JsonValue | object, default: str) -> str:
    if isinstance(value, str) and value != "":
        return value
    return default


def _projection_source(value: Mapping[str, JsonValue], role: str) -> JsonObject:
    return {
        "role": role,
        "value": cast(JsonValue, dict(value)),
    }


def _selected_subunit_or_none(
    subject: Mapping[str, JsonValue],
    protocol_input: Mapping[str, JsonValue],
) -> JsonObject | None:
    selector_key = _item_or_none(subject, "selector_key")
    selector_value = _item_or_none(subject, "selector_value")
    pointer = _item_or_none(subject, "selector_pointer_or_null")
    if not isinstance(selector_key, str) or not isinstance(selector_value, str):
        return None
    if not isinstance(pointer, str):
        return None
    collection_name = _last_slash_part(_parent_array_pointer(pointer))
    collection = _item_or_none(protocol_input, collection_name)
    if not isinstance(collection, Sequence) or isinstance(collection, str | bytes):
        return None
    matches: list[JsonObject] = []
    for entry in collection:
        if (
            isinstance(entry, Mapping)
            and _item_or_none(entry, selector_key) == selector_value
        ):
            matches += [cast(JsonObject, dict(entry))]
    if len(matches) != 1:
        raise contracts.SchemaContractError("retired_projection_unreconstructable")
    return matches[0]


def _parent_context(
    subject: Mapping[str, JsonValue],
    protocol_input: Mapping[str, JsonValue],
) -> JsonObject:
    fields = _item_or_none(subject, "parent_context_fields")
    if not isinstance(fields, Sequence) or isinstance(fields, str | bytes):
        return {}
    result: JsonObject = {}
    for field in fields:
        if isinstance(field, str) and field in protocol_input:
            result[field] = protocol_input[field]
    return result


def _state_bound(protocol_input: Mapping[str, JsonValue]) -> int:
    value = _item_or_none(protocol_input, "state_bound")
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return 0


def _supported_generator(
    protocol_input: Mapping[str, JsonValue],
    subunit: Mapping[str, JsonValue] | None,
) -> bool:
    return _required_generator_params(protocol_input, subunit) is not None


def _required_generator_params(
    protocol_input: Mapping[str, JsonValue],
    subunit: Mapping[str, JsonValue] | None,
) -> JsonObject | None:
    generator_id = _item_or_none(protocol_input, "generator_id")
    if isinstance(subunit, Mapping):
        subunit_generator = _item_or_none(subunit, "generator_id")
        if isinstance(subunit_generator, str):
            generator_id = subunit_generator
    if not isinstance(generator_id, str):
        return None
    if generator_id not in _G4_GENERATOR_IDS:
        return None
    raw_params = _item_or_none(protocol_input, "parameters")
    if not isinstance(raw_params, Mapping) and generator_id == "bidirectional_bas_v1":
        raw_params = _bidirectional_params_from_cells(protocol_input, subunit)
    if not isinstance(raw_params, Mapping):
        return None
    params = cast(JsonObject, dict(raw_params))
    keys = _required_param_keys(generator_id)
    for key in params:
        if key not in keys:
            return None
    for key in keys:
        if key not in params:
            return None
    if not _parameter_types_valid(generator_id, params):
        return None
    return {
        "generator_id": generator_id,
        "parameters": cast(JsonValue, params),
    }


def _bidirectional_params_from_cells(
    protocol_input: Mapping[str, JsonValue],
    subunit: Mapping[str, JsonValue] | None,
) -> JsonObject | None:
    if isinstance(subunit, Mapping):
        return cast(JsonObject, dict(subunit))
    return None


def _explicit_finite_lts_route_projection(
    finite_lts: Mapping[str, JsonValue],
) -> JsonObject | None:
    states = _item_or_none(finite_lts, "states")
    transitions = _item_or_none(finite_lts, "transitions")
    if (
        not isinstance(states, Sequence)
        or isinstance(states, str | bytes)
        or not isinstance(transitions, Sequence)
        or isinstance(transitions, str | bytes)
    ):
        return None
    ordered_stage_roles: list[str] = []
    for state in states:
        if not isinstance(state, str):
            return None
        ordered_stage_roles += [state]
    normalized_transitions: list[JsonObject] = []
    for transition in transitions:
        if not isinstance(transition, Mapping):
            return None
        event = _item_or_none(transition, "event")
        source = _item_or_none(transition, "source")
        target = _item_or_none(transition, "target")
        if (
            not isinstance(event, str)
            or not isinstance(source, str)
            or not isinstance(target, str)
        ):
            return None
        normalized_transitions += [
            {
                "transition_role": event,
                "event_kind": event,
                "source_mode": source,
                "target_mode": target,
            }
        ]
    return {
        "projection_schema_version": "g4_explicit_route_projection/v1",
        "input_mode": "explicit_finite_lts_input",
        "route_semantics_version": "g6b-retired-route-section-7.4/v1",
        "typed_resource_roles": [],
        "typed_route_graph": [
            {
                "route_role": "finite_lts",
                "ordered_stage_roles": cast(JsonValue, ordered_stage_roles),
            }
        ],
        "transition_kinds": cast(JsonValue, normalized_transitions),
        "resource_demand_structure": cast(
            JsonValue,
            [
                {
                    "transition_role": _require_string(item["transition_role"]),
                    "acquire_demands": [],
                    "release_demands": [],
                }
                for item in normalized_transitions
            ],
        ),
        "mode_transition_structure": cast(
            JsonValue,
            [
                {
                    "job_role": "finite_lts",
                    "source_stage": _require_string(item["source_mode"]),
                    "event_kind": _require_string(item["event_kind"]),
                    "target_stage": _require_string(item["target_mode"]),
                }
                for item in normalized_transitions
            ],
        ),
    }


def _generated_route_projection(params: Mapping[str, JsonValue]) -> JsonObject:
    generator_id = _require_string(params["generator_id"])
    raw_params = _require_mapping(params["parameters"])
    resource_roles = _generated_resource_roles(generator_id)
    transitions = _generated_route_transitions(generator_id, raw_params)
    return {
        "projection_schema_version": "g4_generator_route_projection/v1",
        "input_mode": "model_generated_lts",
        "route_semantics_version": "g6b-retired-route-section-7.4/v1",
        "typed_resource_roles": cast(JsonValue, resource_roles),
        "typed_route_graph": cast(JsonValue, _typed_route_graph(transitions)),
        "transition_kinds": cast(JsonValue, _transition_kinds(transitions)),
        "resource_demand_structure": cast(
            JsonValue,
            _resource_demand_structure(transitions),
        ),
        "mode_transition_structure": cast(
            JsonValue,
            _mode_transition_structure(transitions),
        ),
    }


def _generated_resource_roles(generator_id: str) -> list[JsonObject]:
    if generator_id == "bidirectional_bas_v1":
        roles = [
            ("agv", "agv", "agv_count"),
            ("buffer_x", "buffer", "buffer_capacity"),
            ("buffer_y", "buffer", "buffer_capacity"),
            ("machine_x", "machine", "machine_capacity"),
            ("machine_y", "machine", "machine_capacity"),
        ]
    elif generator_id == "three_island_bas_v1":
        roles = [
            ("agv", "agv", "agv_count"),
            ("alpha_out", "buffer", "buffer_capacity"),
            ("beta_out", "buffer", "buffer_capacity"),
            ("inspect", "machine", "machine_capacity"),
            ("lathe", "machine", "machine_capacity"),
            ("mill", "machine", "machine_capacity"),
            ("oven", "machine", "machine_capacity"),
            ("paint", "machine", "machine_capacity"),
        ]
    else:
        roles = [
            ("cart_left", "agv", "cart_capacity"),
            ("cart_right", "agv", "cart_capacity"),
            ("fixture_a", "machine", "fixture_capacity"),
            ("fixture_b", "machine", "fixture_capacity"),
            ("inspection", "machine", "inspection_capacity"),
            ("reserve_a", "reservation", "reservation_capacity"),
            ("reserve_b", "reservation", "reservation_capacity"),
        ]
    return [
        {
            "resource_role": role,
            "resource_kind": kind,
            "capacity_parameter_name": capacity_name,
        }
        for role, kind, capacity_name in roles
    ]


def _generated_route_transitions(
    generator_id: str,
    params: Mapping[str, JsonValue],
) -> list[JsonObject]:
    if generator_id == "or_and_reservation_v1":
        return _adversarial_route_transitions()
    transitions: list[JsonObject] = []
    for job_role in _bas_jobs(generator_id, params):
        route_id = _route_id_from_job_role(job_role)
        resources = _route_resource_sequence(generator_id, route_id)
        transitions += [
            _route_transition(
                f"{job_role}:release",
                job_role,
                "start",
                "outside",
                "processing_0",
                resources[0],
                "",
            )
        ]
        index = 0
        last_index = len(resources) - 1
        while index <= last_index:
            target = "completed"
            releases: JsonValue = []
            if index < last_index:
                target = f"blocked_{index}"
            else:
                releases = cast(JsonValue, _demands([resources[index]]))
            transitions += [
                {
                    "transition_role": f"{job_role}:service:{index}",
                    "job_role": job_role,
                    "event_kind": "service_complete",
                    "source_mode": f"processing_{index}",
                    "target_mode": target,
                    "acquire_demands": [],
                    "release_demands": releases,
                }
            ]
            if index < last_index:
                transitions += [
                    _route_transition(
                        f"{job_role}:transfer:{index + 1}",
                        job_role,
                        "dispatch",
                        f"blocked_{index}",
                        f"processing_{index + 1}",
                        resources[index + 1],
                        resources[index],
                    )
                ]
            index += 1
    return _records_sorted_by_string_field(transitions, "transition_role")


def _route_id_from_job_role(job_role: str) -> str:
    marker = "_"
    index = 0
    chars: list[str] = []
    while index < len(job_role) and job_role[index : index + 1] != marker:
        chars += [job_role[index : index + 1]]
        index += 1
    return _chars_to_string(chars)


def _route_resource_sequence(generator_id: str, route_id: str) -> list[str]:
    if generator_id == "bidirectional_bas_v1":
        if route_id == "FWD":
            return ["machine_x", "buffer_y", "machine_y"]
        if route_id == "REV":
            return ["machine_y", "buffer_x", "machine_x"]
    elif generator_id == "three_island_bas_v1":
        if route_id == "ABG":
            return ["lathe", "alpha_out", "paint", "oven", "beta_out", "inspect"]
        if route_id == "AG":
            return ["mill", "alpha_out", "inspect"]
        if route_id == "BAG":
            return ["paint", "oven", "beta_out", "mill", "alpha_out", "inspect"]
    raise contracts.SchemaContractError("retired_projection_unreconstructable")


def _route_transition(
    transition_role: str,
    job_role: str,
    event_kind: str,
    source_mode: str,
    target_mode: str,
    acquire_resource: str,
    release_resource: str,
) -> JsonObject:
    acquire_demands: JsonValue = cast(JsonValue, _demands([acquire_resource]))
    release_demands: JsonValue = []
    if release_resource != "":
        release_demands = cast(JsonValue, _demands([release_resource]))
    return {
        "transition_role": transition_role,
        "job_role": job_role,
        "event_kind": event_kind,
        "source_mode": source_mode,
        "target_mode": target_mode,
        "acquire_demands": acquire_demands,
        "release_demands": release_demands,
    }


def _adversarial_route_transitions() -> list[JsonObject]:
    return [
        {
            "transition_role": "gate:release_reservations",
            "job_role": "gate",
            "event_kind": "reserve",
            "source_mode": "gate_wait",
            "target_mode": "gate_released",
            "acquire_demands": cast(JsonValue, _demands(["reserve_a", "reserve_b"])),
            "release_demands": [],
        },
        {
            "transition_role": "left:choose_cross",
            "job_role": "left",
            "event_kind": "reserve",
            "source_mode": "or_pending",
            "target_mode": "left_branch_cross",
            "acquire_demands": cast(JsonValue, _demands(["cart_right", "fixture_b"])),
            "release_demands": [],
        },
        {
            "transition_role": "left:choose_inspection",
            "job_role": "left",
            "event_kind": "reserve",
            "source_mode": "or_pending",
            "target_mode": "left_branch_inspection",
            "acquire_demands": cast(JsonValue, _demands(["inspection", "reserve_b"])),
            "release_demands": [],
        },
        {
            "transition_role": "right:choose_cross",
            "job_role": "right",
            "event_kind": "reserve",
            "source_mode": "or_pending",
            "target_mode": "right_branch_cross",
            "acquire_demands": cast(JsonValue, _demands(["cart_left", "fixture_a"])),
            "release_demands": [],
        },
        {
            "transition_role": "right:choose_inspection",
            "job_role": "right",
            "event_kind": "reserve",
            "source_mode": "or_pending",
            "target_mode": "right_branch_inspection",
            "acquire_demands": cast(JsonValue, _demands(["inspection", "reserve_a"])),
            "release_demands": [],
        },
    ]


def _demands(resource_roles: Sequence[str]) -> list[JsonObject]:
    return [{"resource_role": role, "amount": 1} for role in sorted(resource_roles)]


def _typed_route_graph(
    transitions: Sequence[Mapping[str, JsonValue]],
) -> list[JsonObject]:
    stages_by_job: dict[str, list[str]] = {}
    for transition in transitions:
        job_role = _require_string(transition["job_role"])
        if job_role not in stages_by_job:
            stages_by_job[job_role] = []
        for key in ("source_mode", "target_mode"):
            stage = _require_string(transition[key])
            if stage not in stages_by_job[job_role]:
                stages_by_job[job_role] += [stage]
    return [
        {
            "route_role": job_role,
            "ordered_stage_roles": cast(JsonValue, stages_by_job[job_role]),
        }
        for job_role in sorted(stages_by_job)
    ]


def _transition_kinds(
    transitions: Sequence[Mapping[str, JsonValue]],
) -> list[JsonObject]:
    return [
        {
            "transition_role": _require_string(transition["transition_role"]),
            "event_kind": _require_string(transition["event_kind"]),
            "source_mode": _require_string(transition["source_mode"]),
            "target_mode": _require_string(transition["target_mode"]),
        }
        for transition in transitions
    ]


def _resource_demand_structure(
    transitions: Sequence[Mapping[str, JsonValue]],
) -> list[JsonObject]:
    return [
        {
            "transition_role": _require_string(transition["transition_role"]),
            "acquire_demands": transition["acquire_demands"],
            "release_demands": transition["release_demands"],
        }
        for transition in transitions
    ]


def _mode_transition_structure(
    transitions: Sequence[Mapping[str, JsonValue]],
) -> list[JsonObject]:
    return [
        {
            "job_role": _require_string(transition["job_role"]),
            "source_stage": _require_string(transition["source_mode"]),
            "event_kind": _require_string(transition["event_kind"]),
            "target_stage": _require_string(transition["target_mode"]),
        }
        for transition in transitions
    ]


def _required_param_keys(generator_id: str) -> tuple[str, ...]:
    if generator_id == "bidirectional_bas_v1":
        return _BIDIRECTIONAL_PARAM_KEYS
    if generator_id == "three_island_bas_v1":
        return _MEDIUM_PARAM_KEYS
    return _ADVERSARIAL_PARAM_KEYS


def _parameter_types_valid(generator_id: str, params: Mapping[str, JsonValue]) -> bool:
    if generator_id == "bidirectional_bas_v1":
        if not isinstance(params["cell_id"], str):
            return False
        for key in (
            "machine_capacity",
            "buffer_capacity",
            "agv_count",
            "forward_wip",
            "reverse_wip",
            "state_bound",
        ):
            if not _nonnegative_int(params[key]):
                return False
    elif generator_id == "three_island_bas_v1":
        if not isinstance(params["instance_id"], str):
            return False
        route_wip = params["route_wip"]
        if not isinstance(route_wip, Mapping):
            return False
        for route_id in route_wip:
            if (
                not isinstance(route_id, str)
                or route_id not in _MEDIUM_ROUTE_IDS
                or not _nonnegative_int(route_wip[route_id])
            ):
                return False
        for key in (
            "machine_capacity",
            "buffer_capacity",
            "agv_count",
            "state_bound",
        ):
            if not _nonnegative_int(params[key]):
                return False
    else:
        if not isinstance(params["instance_id"], str):
            return False
        for key in (
            "fixture_capacity",
            "cart_capacity",
            "reservation_capacity",
            "state_bound",
        ):
            if not _nonnegative_int(params[key]):
                return False
    for key in _RATE_PARAM_KEYS:
        if key in params:
            rate_value = params[key]
            if isinstance(rate_value, int) and not isinstance(rate_value, bool):
                continue
            if not isinstance(rate_value, str) or not _looks_decimal(rate_value):
                return False
    return True


def _nonnegative_int(value: JsonValue) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _require_int(value: JsonValue) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    raise contracts.SchemaContractError("retired_projection_unreconstructable")


def _generated_state_payload(params: Mapping[str, JsonValue]) -> JsonObject:
    generator_id = _require_string(params["generator_id"])
    raw_params = _require_mapping(params["parameters"])
    if generator_id == "or_and_reservation_v1":
        fixture_capacity = _require_int(raw_params["fixture_capacity"])
        cart_capacity = _require_int(raw_params["cart_capacity"])
        reservation_capacity = _require_int(raw_params["reservation_capacity"])
        state_payload: JsonObject = {
            "stable": True,
            "complete": False,
            "event_calendar_empty": True,
            "holds": [
                {
                    "job_role": "left",
                    "resource_role": "fixture_a",
                    "amount": fixture_capacity,
                },
                {
                    "job_role": "left",
                    "resource_role": "reserve_a",
                    "amount": reservation_capacity,
                },
                {
                    "job_role": "right",
                    "resource_role": "fixture_b",
                    "amount": fixture_capacity,
                },
                {
                    "job_role": "right",
                    "resource_role": "reserve_b",
                    "amount": reservation_capacity,
                },
                {
                    "job_role": "gate",
                    "resource_role": "cart_left",
                    "amount": cart_capacity,
                },
                {
                    "job_role": "gate",
                    "resource_role": "cart_right",
                    "amount": cart_capacity,
                },
                {"job_role": "gate", "resource_role": "inspection", "amount": 1},
            ],
            "requests": [
                {
                    "job_role": "gate",
                    "alternatives": [[{"resource_role": "inspection", "amount": 1}]],
                },
                {
                    "job_role": "left",
                    "alternatives": [[{"resource_role": "cart_left", "amount": 1}]],
                },
                {
                    "job_role": "right",
                    "alternatives": [[{"resource_role": "cart_right", "amount": 1}]],
                },
            ],
            "mode_by_job": [
                {"job_role": "gate", "value": "gate_wait"},
                {"job_role": "left", "value": "or_pending"},
                {"job_role": "right", "value": "or_pending"},
            ],
            "stage_by_job": [
                {"job_role": "gate", "value": "gate_wait"},
                {"job_role": "left", "value": "or_pending"},
                {"job_role": "right", "value": "or_pending"},
            ],
        }
        return state_payload
    jobs = _bas_jobs(generator_id, raw_params)
    outside_values = _outside_job_values(jobs)
    bas_state_payload: JsonObject = {
        "stable": True,
        "complete": False,
        "event_calendar_empty": False,
        "holds": [],
        "requests": [],
        "mode_by_job": cast(JsonValue, outside_values),
        "stage_by_job": cast(JsonValue, outside_values),
    }
    return bas_state_payload


def _bas_jobs(generator_id: str, params: Mapping[str, JsonValue]) -> list[str]:
    jobs: list[str] = []
    if generator_id == "bidirectional_bas_v1":
        route_counts: JsonObject = {
            "FWD": params["forward_wip"],
            "REV": params["reverse_wip"],
        }
    else:
        route_counts = _require_mapping(params["route_wip"])
    for route_id in sorted(route_counts):
        count = route_counts[route_id]
        if not _nonnegative_int(count):
            raise contracts.SchemaContractError("retired_projection_unreconstructable")
        count_int = _require_int(count)
        ordinal = 1
        while ordinal <= count_int:
            ordinal_text = _two_digit(ordinal)
            jobs += [f"{route_id}_{ordinal_text}"]
            ordinal += 1
    return jobs


def _outside_job_values(jobs: Sequence[str]) -> list[JsonObject]:
    return [{"job_role": job, "value": "outside"} for job in jobs]


def _two_digit(value: int) -> str:
    if value < 10:
        return f"0{value}"
    return f"{value}"


def _structural_parameter_entries(params: Mapping[str, JsonValue]) -> list[JsonObject]:
    raw_params = _require_mapping(params["parameters"])
    entries: list[JsonObject] = []
    for key in sorted(raw_params):
        if key not in _RATE_PARAM_KEYS:
            entries += [
                {
                    "name": key,
                    "value": raw_params[key],
                    "value_type": _parameter_value_type(raw_params[key]),
                }
            ]
    return entries


def _numeric_parameter_entries(params: Mapping[str, JsonValue]) -> list[JsonObject]:
    raw_params = _require_mapping(params["parameters"])
    entries: list[JsonObject] = []
    for key in _RATE_PARAM_KEYS:
        if key in raw_params:
            entries += [
                {
                    "name": key,
                    "value": _canonical_rate(raw_params[key]),
                    "value_type": "canonical_decimal_string",
                }
            ]
    return entries


def _parameter_projection_entries(
    kind: str,
    protocol_input: Mapping[str, JsonValue],
    subunit: Mapping[str, JsonValue] | None,
    parent_context: Mapping[str, JsonValue],
) -> JsonObject | None:
    try:
        if kind == "bidirectional_island_grid":
            return _bidirectional_parameter_entries(
                protocol_input,
                subunit,
                parent_context,
            )
        if kind == "supplied_l30_inequalities":
            return _l30_parameter_entries(protocol_input, subunit, parent_context)
        if kind == "adapted_candidate_monitor_cover":
            return _monitor_cover_parameter_entries(
                protocol_input,
                subunit,
                parent_context,
            )
        if kind in {
            "crp_evidence_audit",
            "fixed_recorder_target",
        }:
            return _generic_explicit_parameter_entries(
                protocol_input,
                subunit,
                parent_context,
            )
        params = _required_generator_params(protocol_input, subunit)
        if params is None:
            return None
        if kind == "medium_island_rebuild":
            return _medium_parameter_entries(params)
        if kind == "adversarial_snapshot":
            return _adversarial_parameter_entries(params)
    except contracts.SchemaContractError:
        return None
    return None


def _bidirectional_parameter_entries(
    protocol_input: Mapping[str, JsonValue],
    subunit: Mapping[str, JsonValue] | None,
    parent_context: Mapping[str, JsonValue],
) -> JsonObject | None:
    params = _required_generator_params(protocol_input, subunit)
    if params is None:
        return None
    raw_params = _require_mapping(params["parameters"])
    structural_entries: list[JsonObject] = [
        _structural_entry("cell_id", "string", raw_params["cell_id"])
    ]
    generator_id = _item_or_none(parent_context, "generator_id")
    if not isinstance(generator_id, str):
        generator_id = _require_string(params["generator_id"])
    structural_entries += [_structural_entry("generator_id", "string", generator_id)]
    numeric_entries = _integer_entries(
        raw_params,
        (
            "agv_count",
            "buffer_capacity",
            "forward_wip",
            "machine_capacity",
            "reverse_wip",
            "state_bound",
        ),
    )
    numeric_entries += _rate_entries(
        raw_params,
        ("release_rate", "service_rate", "transfer_rate"),
    )
    return _parameter_entries_object(
        structural_entries,
        numeric_entries,
        raw_params["state_bound"],
    )


def _medium_parameter_entries(params: Mapping[str, JsonValue]) -> JsonObject:
    raw_params = _require_mapping(params["parameters"])
    structural_entries = [
        _structural_entry("instance_id", "string", raw_params["instance_id"]),
        _structural_entry(
            "route_wip",
            "ordered_tuple",
            _sorted_mapping_pairs(_require_mapping(raw_params["route_wip"])),
        ),
    ]
    numeric_entries = _integer_entries(
        raw_params,
        ("agv_count", "buffer_capacity", "machine_capacity", "state_bound"),
    )
    numeric_entries += _rate_entries(
        raw_params,
        ("release_rate", "service_rate", "transfer_rate"),
    )
    return _parameter_entries_object(
        structural_entries,
        numeric_entries,
        raw_params["state_bound"],
    )


def _adversarial_parameter_entries(params: Mapping[str, JsonValue]) -> JsonObject:
    raw_params = _require_mapping(params["parameters"])
    structural_entries = [
        _structural_entry("instance_id", "string", raw_params["instance_id"])
    ]
    numeric_entries = _integer_entries(
        raw_params,
        ("cart_capacity", "fixture_capacity", "reservation_capacity", "state_bound"),
    )
    numeric_entries += [_numeric_entry("inspection_capacity", "integer", 1)]
    numeric_entries += _rate_entries(raw_params, ("decision_rate",))
    return _parameter_entries_object(
        structural_entries,
        numeric_entries,
        raw_params["state_bound"],
    )


def _l30_parameter_entries(
    protocol_input: Mapping[str, JsonValue],
    subunit: Mapping[str, JsonValue] | None,
    parent_context: Mapping[str, JsonValue],
) -> JsonObject | None:
    inequality = _explicit_subunit_or_first(subunit, protocol_input, "inequalities")
    if inequality is None:
        return None
    capacities = _context_mapping(parent_context, protocol_input, "capacities")
    if capacities is None:
        return None
    finite_capacity = _context_item(
        parent_context,
        protocol_input,
        "finite_capacity_s3pr_ens3pr",
    )
    provenance = _context_item(parent_context, protocol_input, "inequality_provenance")
    coefficients = _item_or_none(inequality, "coefficients")
    if (
        not isinstance(coefficients, Mapping)
        or not isinstance(finite_capacity, bool)
        or not isinstance(provenance, str)
    ):
        return None
    structural_entries = [
        _structural_entry("finite_capacity_s3pr_ens3pr", "boolean", finite_capacity),
        _structural_entry(
            "inequality_coefficients",
            "ordered_tuple",
            _sorted_mapping_pairs(cast(Mapping[str, JsonValue], coefficients)),
        ),
        _structural_entry("inequality_name", "string", inequality["name"]),
        _structural_entry("inequality_provenance", "string", provenance),
    ]
    if subunit is None:
        all_inequalities = _item_or_none(protocol_input, "inequalities")
        structural_entries += [
            _structural_entry(
                "all_inequalities_content_sha256",
                "content_sha256",
                _content_sha256(all_inequalities),
            )
        ]
    numeric_entries = [_numeric_entry("inequality_rhs", "integer", inequality["rhs"])]
    for capacity_name in sorted(capacities):
        numeric_entries += [
            _numeric_entry(
                f"capacity_{capacity_name}",
                "integer",
                capacities[capacity_name],
            )
        ]
    return _parameter_entries_object(structural_entries, numeric_entries, 0)


def _monitor_cover_parameter_entries(
    protocol_input: Mapping[str, JsonValue],
    subunit: Mapping[str, JsonValue] | None,
    parent_context: Mapping[str, JsonValue],
) -> JsonObject | None:
    monitor = _explicit_subunit_or_first(subunit, protocol_input, "candidate_monitors")
    if monitor is None:
        return None
    finite_lts = _context_mapping(parent_context, protocol_input, "finite_lts")
    legal_states = _context_item(parent_context, protocol_input, "legal_states")
    first_met_bad_states = _context_item(
        parent_context,
        protocol_input,
        "first_met_bad_states",
    )
    state_bound = _context_item(parent_context, protocol_input, "state_bound")
    if state_bound is None:
        return None
    structural_entries = [
        _structural_entry(
            "covered_bad_states",
            "ordered_tuple",
            cast(JsonValue, _sorted_string_sequence(monitor["covered_bad_states"])),
        ),
        _structural_entry(
            "excluded_legal_states",
            "ordered_tuple",
            cast(JsonValue, _sorted_string_sequence(monitor["excluded_legal_states"])),
        ),
        _structural_entry(
            "finite_lts_sha256",
            "content_sha256",
            canonical_sha256_v2(cast(JsonValue, finite_lts)),
        ),
        _structural_entry(
            "first_met_bad_states_sha256",
            "content_sha256",
            canonical_sha256_v2(first_met_bad_states),
        ),
        _structural_entry(
            "legal_states_sha256",
            "content_sha256",
            canonical_sha256_v2(legal_states),
        ),
        _structural_entry("monitor_id", "string", monitor["monitor_id"]),
    ]
    if subunit is None:
        candidate_monitors = _item_or_none(protocol_input, "candidate_monitors")
        structural_entries += [
            _structural_entry(
                "all_candidate_monitors_content_sha256",
                "content_sha256",
                _content_sha256(candidate_monitors),
            )
        ]
    numeric_entries = [_numeric_entry("state_bound", "integer", state_bound)]
    return _parameter_entries_object(structural_entries, numeric_entries, state_bound)


def _generic_explicit_parameter_entries(
    protocol_input: Mapping[str, JsonValue],
    subunit: Mapping[str, JsonValue] | None,
    parent_context: Mapping[str, JsonValue],
) -> JsonObject:
    structural_entries: list[JsonObject] = [
        _structural_entry(
            "protocol_input_content_sha256",
            "content_sha256",
            canonical_sha256_v2(cast(JsonValue, protocol_input)),
        ),
        _structural_entry(
            "selected_subunit_or_null_content_sha256",
            "content_sha256",
            canonical_sha256_v2(_json_object_or_null(subunit)),
        ),
        _structural_entry(
            "parent_context_content_sha256",
            "content_sha256",
            canonical_sha256_v2(cast(JsonValue, parent_context)),
        ),
    ]
    return _parameter_entries_object(
        structural_entries,
        _decimal_entries(cast(JsonValue, protocol_input)),
        _state_bound(protocol_input),
    )


def _parameter_entries_object(
    structural_entries: Sequence[Mapping[str, JsonValue]],
    numeric_entries: Sequence[Mapping[str, JsonValue]],
    state_bound: JsonValue,
) -> JsonObject:
    return {
        "structural_parameter_entries": cast(
            JsonValue,
            _records_sorted_by_string_field(
                [dict(entry) for entry in structural_entries],
                "name",
            ),
        ),
        "numeric_parameter_entries": cast(
            JsonValue,
            _records_sorted_by_string_field(
                [dict(entry) for entry in numeric_entries],
                "name",
            ),
        ),
        "state_bound": _require_int(state_bound),
    }


def _structural_entry(name: str, value_type: str, value: JsonValue) -> JsonObject:
    return {"name": name, "value_type": value_type, "value": value}


def _content_sha256(value: JsonValue | None) -> str:
    return canonical_sha256_v2(value)


def _numeric_entry(name: str, value_type: str, value: JsonValue) -> JsonObject:
    if value_type == "integer":
        value = _require_int(value)
    return {"name": name, "value_type": value_type, "value": value}


def _integer_entries(
    params: Mapping[str, JsonValue],
    names: Sequence[str],
) -> list[JsonObject]:
    return [_numeric_entry(name, "integer", params[name]) for name in names]


def _rate_entries(
    params: Mapping[str, JsonValue],
    names: Sequence[str],
) -> list[JsonObject]:
    return [
        _numeric_entry(name, "canonical_decimal_string", _canonical_rate(params[name]))
        for name in names
    ]


def _sorted_mapping_pairs(value: Mapping[str, JsonValue]) -> list[JsonValue]:
    return [[key, value[key]] for key in sorted(value)]


def _sorted_string_sequence(value: JsonValue) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise contracts.SchemaContractError("retired_projection_unreconstructable")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise contracts.SchemaContractError("retired_projection_unreconstructable")
        result += [item]
    return sorted(result)


def _explicit_subunit_or_first(
    subunit: Mapping[str, JsonValue] | None,
    protocol_input: Mapping[str, JsonValue],
    collection_name: str,
) -> JsonObject | None:
    if isinstance(subunit, Mapping):
        return cast(JsonObject, dict(subunit))
    collection = _item_or_none(protocol_input, collection_name)
    if not isinstance(collection, Sequence) or isinstance(collection, str | bytes):
        return None
    if len(collection) < 1:
        return None
    first = collection[0]
    if not isinstance(first, Mapping):
        return None
    return cast(JsonObject, dict(first))


def _context_item(
    parent_context: Mapping[str, JsonValue],
    protocol_input: Mapping[str, JsonValue],
    key: str,
) -> JsonValue | None:
    value = _item_or_none(parent_context, key)
    if value is not None:
        return value
    return _item_or_none(protocol_input, key)


def _context_mapping(
    parent_context: Mapping[str, JsonValue],
    protocol_input: Mapping[str, JsonValue],
    key: str,
) -> JsonObject | None:
    value = _context_item(parent_context, protocol_input, key)
    if isinstance(value, Mapping):
        return cast(JsonObject, dict(value))
    return None


def _records_sorted_by_string_field(
    records: Sequence[Mapping[str, JsonValue]],
    field: str,
) -> list[JsonObject]:
    result: list[JsonObject] = []
    for record in records:
        item = cast(JsonObject, dict(record))
        item_key = _require_string(item[field])
        insert_at = len(result)
        index = 0
        while index < len(result):
            if item_key < _require_string(result[index][field]):
                insert_at = index
                index = len(result)
            else:
                index += 1
        result = [*result[:insert_at], item, *result[insert_at:]]
    return result


def _canonical_rate(value: JsonValue) -> str:
    if isinstance(value, int) and not isinstance(value, bool):
        return f"{value}"
    return _canonical_decimal(_require_string(value))


def _parameter_value_type(value: JsonValue) -> str:
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, str):
        return "string"
    if isinstance(value, Mapping):
        return "mapping"
    raise contracts.SchemaContractError("retired_projection_unreconstructable")


def _decimal_entries(value: JsonValue) -> list[JsonObject]:
    decimals: list[str] = []
    _collect_canonical_decimals(value, decimals)
    return [
        {
            "name": f"historical_decimal_{index}",
            "value": decimal,
            "value_type": "canonical_decimal_string",
        }
        for index, decimal in enumerate(decimals)
    ]


def _collect_canonical_decimals(value: object, decimals: list[str]) -> None:
    if isinstance(value, str) and _looks_decimal(value):
        decimals += [_canonical_decimal(value)]
    elif isinstance(value, Mapping):
        for key in sorted(value):
            _collect_canonical_decimals(value[key], decimals)
    elif isinstance(value, Sequence) and not isinstance(value, str | bytes):
        for item in value:
            _collect_canonical_decimals(item, decimals)


def _canonicalized_decimal_value(value: JsonValue) -> JsonValue:
    if isinstance(value, str) and _looks_decimal(value):
        return _canonical_decimal(value)
    if isinstance(value, Mapping):
        return {
            _require_string(key): _canonicalized_decimal_value(value[key])
            for key in sorted(value)
        }
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return [_canonicalized_decimal_value(item) for item in value]
    return value


def _canonicalized_decimal_value_strict(value: JsonValue) -> JsonValue:
    if isinstance(value, str):
        return _canonical_decimal(value)
    if isinstance(value, Mapping):
        return {
            _require_string(key): _canonicalized_decimal_value_strict(value[key])
            for key in sorted(value)
        }
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return [_canonicalized_decimal_value_strict(item) for item in value]
    return value


def _looks_decimal(value: str) -> bool:
    return _canonical_decimal_or_none(value) is not None


def _canonical_decimal(value: str) -> str:
    canonical = _canonical_decimal_or_none(value)
    if canonical is None:
        raise contracts.SchemaContractError("retired_projection_unreconstructable")
    return canonical


def _canonical_decimal_or_none(value: str) -> str | None:
    text = value
    sign = ""
    index = 0
    if text[index : index + 1] == "-":
        sign = "-"
        index = 1
    if index >= len(text):
        return None
    int_chars: list[str] = []
    first = text[index : index + 1]
    if first >= "0" and first <= "9":
        current_char = text[index : index + 1]
        while index < len(text) and current_char >= "0" and current_char <= "9":
            int_chars += [current_char]
            index += 1
            current_char = text[index : index + 1]
    else:
        return None
    frac_chars: list[str] = []
    if index < len(text) and text[index : index + 1] == ".":
        index += 1
        current_char = text[index : index + 1]
        if index >= len(text) or current_char < "0" or current_char > "9":
            return None
        while index < len(text) and current_char >= "0" and current_char <= "9":
            frac_chars += [current_char]
            index += 1
            current_char = text[index : index + 1]
    exponent = 0
    if index < len(text) and text[index : index + 1] in ("e", "E"):
        index += 1
        exponent_sign = 1
        if index < len(text) and text[index : index + 1] in ("+", "-"):
            if text[index : index + 1] == "-":
                exponent_sign = -1
            index += 1
        current_char = text[index : index + 1]
        if index >= len(text) or current_char < "0" or current_char > "9":
            return None
        while index < len(text) and current_char >= "0" and current_char <= "9":
            exponent = exponent * 10 + int(current_char)
            index += 1
            current_char = text[index : index + 1]
        exponent = exponent * exponent_sign
    if index != len(text):
        return None
    digits = _chars_to_string([*int_chars, *frac_chars])
    if _all_zero_digits(digits):
        if sign == "-":
            return None
        return "0"
    decimal_at = len(int_chars) + exponent
    if decimal_at <= 0:
        decimal_text = f"0.{_zero_string(-decimal_at)}{digits}"
    elif decimal_at >= len(digits):
        decimal_text = f"{digits}{_zero_string(decimal_at - len(digits))}"
    else:
        decimal_text = f"{digits[:decimal_at]}.{digits[decimal_at:]}"
    while len(decimal_text) > 1 and decimal_text[0] == "0" and decimal_text[1] != ".":
        decimal_text = decimal_text[1:]
    if "." in decimal_text:
        while _has_suffix(decimal_text, "0"):
            decimal_text = decimal_text[:-1]
        if _has_suffix(decimal_text, "."):
            decimal_text = decimal_text[:-1]
    return f"{sign}{decimal_text}"


def _all_zero_digits(value: str) -> bool:
    for char in value:
        if char != "0":
            return False
    return True


def _zero_string(count: int) -> str:
    chars: list[str] = []
    while count > 0:
        chars += ["0"]
        count -= 1
    return _chars_to_string(chars)


def _reserved_quantitative_path(
    bundle_id: str,
    case_unit_id: str,
    method_observation_id: str,
    run_role: str,
) -> str:
    return (
        "artifacts/g6b/quantitative/"
        f"{bundle_id}/{case_unit_id}/{method_observation_id}/{run_role}"
    )


def _lower_id(value: str) -> str:
    chars: list[str] = []
    for char in value:
        if char == "A":
            chars += ["a"]
        elif char == "B":
            chars += ["b"]
        elif char == "C":
            chars += ["c"]
        elif char == "D":
            chars += ["d"]
        elif char == "E":
            chars += ["e"]
        elif char == "F":
            chars += ["f"]
        elif char == "G":
            chars += ["g"]
        elif char == "H":
            chars += ["h"]
        elif char == "I":
            chars += ["i"]
        elif char == "J":
            chars += ["j"]
        elif char == "K":
            chars += ["k"]
        elif char == "L":
            chars += ["l"]
        elif char == "M":
            chars += ["m"]
        elif char == "N":
            chars += ["n"]
        elif char == "O":
            chars += ["o"]
        elif char == "P":
            chars += ["p"]
        elif char == "Q":
            chars += ["q"]
        elif char == "R":
            chars += ["r"]
        elif char == "S":
            chars += ["s"]
        elif char == "T":
            chars += ["t"]
        elif char == "U":
            chars += ["u"]
        elif char == "V":
            chars += ["v"]
        elif char == "W":
            chars += ["w"]
        elif char == "X":
            chars += ["x"]
        elif char == "Y":
            chars += ["y"]
        elif char == "Z":
            chars += ["z"]
        else:
            chars += [char]
    return _chars_to_string(chars)


def _is_explicit_g4_subunit_subject(subject_id: str) -> bool:
    return (
        ":cell_id:" in subject_id
        or ":name:" in subject_id
        or ":monitor_id:" in subject_id
    )


def _normalize_repo_relative_root(value: str) -> str | None:
    normalized = _backslash_to_slash(value)
    if normalized[:1] == "/" or _contains_parent_part(normalized):
        return None
    normalized = _collapse_double_slashes(normalized)
    return _strip_trailing_slashes(normalized)


def _unique_g6r_suffix(value: str) -> str | None:
    normalized = _backslash_to_slash(value)
    marker = "artifacts/g6-historical-replay/"
    occurrences = _substring_count(normalized, marker)
    if occurrences != 1:
        return None
    marker_index = _substring_index(normalized, marker)
    if marker_index < 0:
        return None
    suffix = normalized[marker_index:]
    return _normalize_repo_relative_root(suffix)


def _backslash_to_slash(value: str) -> str:
    chars: list[str] = []
    for char in value:
        if char == "\\":
            chars += ["/"]
        else:
            chars += [char]
    return _chars_to_string(chars)


def _collapse_double_slashes(value: str) -> str:
    chars: list[str] = []
    previous_slash = False
    for char in value:
        if char == "/":
            if not previous_slash:
                chars += [char]
            previous_slash = True
        else:
            chars += [char]
            previous_slash = False
    return _chars_to_string(chars)


def _strip_trailing_slashes(value: str) -> str:
    stop = len(value)
    while stop > 0 and value[stop - 1] == "/":
        stop -= 1
    return value[:stop]


def _substring_count(value: str, needle: str) -> int:
    count = 0
    index = 0
    while index <= len(value) - len(needle):
        if value[index : index + len(needle)] == needle:
            count += 1
        index += 1
    return count


def _substring_index(value: str, needle: str) -> int:
    index = 0
    while index <= len(value) - len(needle):
        if value[index : index + len(needle)] == needle:
            return index
        index += 1
    return -1


def _last_slash_part(value: str) -> str:
    start = 0
    index = 0
    while index < len(value):
        if value[index] == "/":
            start = index + 1
        index += 1
    return value[start:]


def _parent_array_pointer(value: str) -> str:
    if _has_suffix(value, "/*"):
        return value[: len(value) - 2]
    return value


def _require_record_root(root: Path) -> None:
    root_path = Path(root)
    authorization_path = root_path / _AUTHORIZATION_FILE
    _reject_symlink_components(root_path)
    _reject_symlink_components(authorization_path)
    if not Path(root_path).exists() or not Path(authorization_path).is_file():
        raise contracts.SchemaContractError("missing_retired_authority")
    authorization = _load_canonical_object(
        Path(authorization_path).read_bytes(),
        "normalization_authorization",
    )
    _require_authorized_root(root_path, authorization)
    if Path(root_path / _MANIFEST_FILE).exists():
        raise contracts.SchemaContractError("preexisting")


def _require_authorized_root(
    root: Path,
    authorization: Mapping[str, JsonValue],
) -> None:
    allowed = authorization["allowed_output_root"]
    if not isinstance(allowed, Mapping):
        raise contracts.SchemaContractError("output_root_contract_drift")
    expected = _require_string(allowed["repo_relative_posix_path"])
    if expected != contracts.NORMALIZATION_ALLOWED_OUTPUT_ROOT_PATH:
        raise contracts.SchemaContractError("output_root_contract_drift")
    _reject_symlink_components(root)
    observed_parts = _filesystem_parts(str(Path(root).resolve()))
    expected_parts = _slash_parts(expected)
    if len(observed_parts) < len(expected_parts):
        raise contracts.SchemaContractError("output_root_contract_drift")
    offset = len(observed_parts) - len(expected_parts)
    for index in range(len(expected_parts)):
        if observed_parts[offset + index] != expected_parts[index]:
            raise contracts.SchemaContractError("output_root_contract_drift")


def _verify_manifest_references(
    root: Path,
    manifest: Mapping[str, JsonValue],
) -> None:
    root_path = Path(root)
    authorization = _load_canonical_object(
        Path(root_path / _AUTHORIZATION_FILE).read_bytes(),
        "manifest_last",
    )
    selector_rows = _mapping_sequence(authorization["allowed_json_fields_by_source"])
    expected_source_hashes = _string_mapping(manifest["expected_file_manifest"])
    auth_hash = _require_string(manifest["normalization_authorization_sha256"])
    if _file_sha(root_path / _AUTHORIZATION_FILE) != auth_hash:
        raise contracts.SchemaContractError("manifest_last")
    lock_records = _verify_record_hash_map(
        root_path,
        _LOCK_DIR,
        "authority_lock_record_hashes",
        manifest["authority_lock_record_hashes"],
    )
    source_records = _verify_record_hash_map(
        root_path,
        _SOURCE_DIR,
        "authority_source_record_hashes",
        manifest["authority_source_record_hashes"],
    )
    authority_lock_hashes = {
        authority_id: _require_string(
            lock_records[authority_id]["authority_lock_record_sha256"]
        )
        for authority_id in lock_records
    }
    for path in source_records:
        contracts.validate_authority_source_record(
            source_records[path],
            authority_lock_hashes=authority_lock_hashes,
            expected_source_hashes=expected_source_hashes,
            selector_rows=selector_rows,
        )
    fingerprint_records = _verify_record_hash_map(
        root_path,
        _FINGERPRINT_DIR,
        "fingerprint_record_hashes",
        manifest["fingerprint_record_hashes"],
    )
    contracts.validate_normalization_manifest(
        manifest,
        authority_lock_records=lock_records,
        authority_source_records=source_records,
        fingerprint_records=fingerprint_records,
    )


def _verify_record_hash_map(
    root: Path,
    directory_name: str,
    field: str,
    value: JsonValue,
) -> dict[str, JsonObject]:
    root_path = Path(root)
    if not isinstance(value, Mapping):
        raise contracts.SchemaContractError("manifest_last")
    records: dict[str, JsonObject] = {}
    for name in value:
        expected_hash = value[name]
        if not isinstance(name, str) or not isinstance(expected_hash, str):
            raise contracts.SchemaContractError("manifest_last")
        if directory_name == _LOCK_DIR:
            filename = name
        else:
            filename = _sha256_text(name)
        path = root_path / directory_name / f"{filename}.json"
        _reject_symlink_components(path)
        if not Path(path).is_file():
            raise contracts.SchemaContractError("manifest_last")
        try:
            record = _load_canonical_object(Path(path).read_bytes(), "manifest_last")
            if directory_name == _LOCK_DIR:
                contracts.validate_authority_lock_record(record)
                observed_hash = _require_string(record["authority_lock_record_sha256"])
            elif directory_name == _FINGERPRINT_DIR:
                observed_hash = _require_string(record["record_provenance_sha256"])
            else:
                observed_hash = _file_sha(path)
        except contracts.SchemaContractError as exc:
            raise contracts.SchemaContractError("manifest_last") from exc
        if observed_hash != expected_hash:
            raise contracts.SchemaContractError("manifest_last")
        records[name] = record
    return records


def _manifest_from_records(
    authorization_sha: str,
    locks: Mapping[str, Mapping[str, JsonValue]],
    sources: Mapping[str, Mapping[str, JsonValue]],
    fingerprints: Mapping[str, Mapping[str, JsonValue]],
    source_hashes: Mapping[str, str],
    authorization: Mapping[str, JsonValue],
) -> JsonObject:
    dimension_status_counts = {
        status: sum(
            1
            for record_id in fingerprints
            if fingerprints[record_id]["dimension_status"] == status
        )
        for status in contracts.DIMENSION_STATUS_VALUES
    }
    unique_lineage_map = {
        _require_string(fingerprints[record_id]["lineage_id"]): sorted(
            _require_string(fingerprints[other_id]["record_id"])
            for other_id in fingerprints
            if fingerprints[other_id]["lineage_id"]
            == fingerprints[record_id]["lineage_id"]
        )
        for record_id in fingerprints
    }
    comparison_eligibility = {
        record_id: {
            "eligible_for_overlap_comparison": fingerprints[record_id][
                "dimension_status"
            ]
            != "unreconstructable_refuse",
            "refusal_reason_code_or_null": (
                "retired_projection_unreconstructable"
                if fingerprints[record_id]["dimension_status"]
                == "unreconstructable_refuse"
                else None
            ),
        }
        for record_id in sorted(fingerprints)
    }
    unreconstructable_records = sorted(
        record_id
        for record_id in fingerprints
        if fingerprints[record_id]["dimension_status"] == "unreconstructable_refuse"
    )
    manifest: JsonObject = {
        "schema_version": "ims-deadlock/g6b-retired-normalization-manifest/v1",
        "manifest_id": "retired-normalization-source-only",
        "source_remote": "retired-authority-logical-origin",
        "source_head": _require_string(authorization["source_head"]),
        "source_tree_hash": _require_string(authorization["source_tree_hash"]),
        "source_dirty_state": "clean",
        "authority_ids": list(contracts.RETIRED_AUTHORITY_IDS),
        "expected_file_manifest": {
            path: source_hashes[path] for path in sorted(source_hashes)
        },
        "verified_file_byte_hashes": {
            path: source_hashes[path] for path in sorted(source_hashes)
        },
        "frozen_hash_validation_results": {
            path: {
                "declared_sha256": source_hashes[path],
                "observed_sha256": source_hashes[path],
                "status": "match",
            }
            for path in sorted(source_hashes)
        },
        "historical_canonicalization_versions": {
            authority_id: contracts.G6B_CANONICAL_JSON_VERSION
            for authority_id in contracts.RETIRED_AUTHORITY_IDS
        },
        "projection_canonicalization_version": contracts.G6B_CANONICAL_JSON_VERSION,
        "normalizer_version": _NORMALIZER_VERSION,
        "normalizer_code_sha256": _require_string(
            authorization["normalizer_code_sha256"]
        ),
        "normalization_authorization_sha256": authorization_sha,
        "authority_lock_record_hashes": {
            key: _require_string(locks[key]["authority_lock_record_sha256"])
            for key in locks
        },
        "authority_source_record_hashes": {
            key: canonical_sha256_v2(cast(JsonObject, dict(sources[key])))
            for key in sources
        },
        "fingerprint_record_hashes": {
            key: _require_string(fingerprints[key]["record_provenance_sha256"])
            for key in fingerprints
        },
        "unique_lineage_map": cast(JsonObject, unique_lineage_map),
        "dimension_status_counts": cast(JsonObject, dimension_status_counts),
        "missing_source_records": [],
        "unreconstructable_records": cast(JsonValue, unreconstructable_records),
        "comparison_eligibility": cast(JsonObject, comparison_eligibility),
        "created_at_utc": _require_string(authorization["issued_at_utc"]),
        "manifest_sha256": None,
    }
    manifest["manifest_sha256"] = finalized_self_hash(manifest, "manifest_sha256")
    return manifest


def _file_sha(path: Path) -> str:
    target = Path(path)
    return hashlib.sha256(Path(target).read_bytes()).hexdigest()


def _existing_source_hashes(repo_root: Path, paths: Sequence[str]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    repo_root_path = Path(repo_root)
    repo = Path(repo_root_path).resolve()
    for path in paths:
        if path[:1] == "/" or _contains_parent_part(path):
            raise contracts.SchemaContractError("source_outside_retired_inventory")
        candidate = repo_root_path / path
        _reject_symlink_components(candidate)
        try:
            Path(candidate).resolve().relative_to(repo)
        except ValueError as exc:
            raise contracts.SchemaContractError(
                "source_outside_retired_inventory"
            ) from exc
        if not Path(candidate).is_file():
            raise contracts.SchemaContractError("missing_retired_authority")
        hashes[path] = hashlib.sha256(Path(candidate).read_bytes()).hexdigest()
    return hashes


def _verify_output_root(
    repo_root: Path,
    output_root: Path,
    authorization: Mapping[str, JsonValue],
) -> None:
    repo_root_path = Path(repo_root)
    output_root_path = Path(output_root)
    allowed = authorization["allowed_output_root"]
    if not isinstance(allowed, Mapping):
        raise contracts.SchemaContractError("output_root_contract_drift")
    expected = _require_string(allowed["repo_relative_posix_path"])
    if expected[:1] == "/" or _contains_parent_part(expected):
        raise contracts.SchemaContractError("output_root_contract_drift")
    _reject_symlink_components(repo_root_path / expected)
    _reject_symlink_components(output_root_path)
    repo = Path(repo_root_path).resolve()
    expected_root = Path(repo / expected).resolve()
    observed_root = Path(output_root_path).resolve()
    try:
        expected_root.relative_to(repo)
        observed_root.relative_to(repo)
    except ValueError as exc:
        raise contracts.SchemaContractError("output_root_contract_drift") from exc
    _reject_symlink_components(expected_root)
    _reject_symlink_components(observed_root)
    if observed_root != expected_root:
        raise contracts.SchemaContractError("output_root_contract_drift")


def _reject_symlink_components(path: Path) -> None:
    target = Path(path)
    text = str(target)
    if text == "":
        return
    separators = ("/", "\\")
    start = 0
    if len(text) >= 2 and text[1] == ":":
        start = 2
        if len(text) > 2 and text[2] in separators:
            start = 3
    elif text[:2] in ("//", "\\\\"):
        index = 2
        seen = 0
        while index < len(text):
            if text[index] in separators:
                seen += 1
                if seen == 2:
                    start = index + 1
                    break
            index += 1
    elif text[0] in separators:
        start = 1
    index = start
    while index < len(text):
        if text[index] in separators:
            prefix = text[:index]
            if prefix and Path(prefix).is_symlink():
                raise contracts.SchemaContractError("symlink")
        index += 1
    if Path(target).is_symlink():
        raise contracts.SchemaContractError("symlink")


def _allowed_uses_for_path(
    path: str,
    selector_rows: Sequence[Mapping[str, JsonValue]],
) -> list[str]:
    uses = {
        _require_string(row["allowed_use"])
        for row in selector_rows
        if _path_pattern_matches(_require_string(row["source_path_pattern"]), path)
    }
    return sorted(uses) or ["source_hash_validation"]


def _path_pattern_matches(pattern: str, path: str) -> bool:
    if pattern == path:
        return True
    if "{case_id}" in pattern:
        prefix, suffix = _split_once(pattern, "{case_id}")
        return _has_prefix(path, prefix) and _has_suffix(path, suffix)
    if "{" in pattern and "}" in pattern:
        prefix, rest = _split_once(pattern, "{")
        choices, suffix = _split_once(rest, "}")
        return any(
            path == f"{prefix}{choice}{suffix}" for choice in _comma_parts(choices)
        )
    return False


def _has_prefix(value: str, prefix: str) -> bool:
    return bool(value[: len(prefix)] == prefix)


def _has_suffix(value: str, suffix: str) -> bool:
    if suffix == "":
        return True
    return bool(
        len(value) >= len(suffix) and value[len(value) - len(suffix) :] == suffix
    )


def _slash_parts(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    for char in value:
        if char == "/":
            parts += [_chars_to_string(current)]
            current = []
        else:
            current += [char]
    parts += [_chars_to_string(current)]
    return list(parts)


def _filesystem_parts(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    for char in value:
        if char == "/" or char == "\\":
            parts += [_chars_to_string(current)]
            current = []
        else:
            current += [char]
    parts += [_chars_to_string(current)]
    return list(parts)


def _comma_parts(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    for char in value:
        if char == ",":
            parts += [_chars_to_string(current)]
            current = []
        else:
            current += [char]
    parts += [_chars_to_string(current)]
    return list(parts)


def _chars_to_string(chars: Sequence[str]) -> str:
    text = ""
    for char in chars:
        text += char
    return str(text)


def _contains_parent_part(value: str) -> bool:
    return bool(any(part == ".." for part in _slash_parts(value)))


def _decimal_digits(value: str) -> bool:
    return bool(value != "" and all("0" <= char <= "9" for char in value))


def _decode_json_pointer_part(value: str) -> str:
    decoded: list[str] = []
    index = 0
    while index < len(value):
        char = value[index]
        if char == "~" and index + 1 < len(value):
            next_char = value[index + 1]
            if next_char == "1":
                decoded += ["/"]
                index += 2
                continue
            if next_char == "0":
                decoded += ["~"]
                index += 2
                continue
        decoded += [char]
        index += 1
    return _chars_to_string(decoded)


def _split_once(value: str, marker: str) -> tuple[str, str]:
    for index in range(0, len(value) - len(marker) + 1):
        if value[index : index + len(marker)] == marker:
            return (value[:index], value[index + len(marker) :])
    return (value, "")


def _authority_id_for_source(path: str) -> str:
    if _has_prefix(path, "cases/confirmation/g4/"):
        return "G4_FREEZE"
    if _has_prefix(path, "evidence/g5/"):
        return "G5_EXECUTION"
    return "G6_R_REPLAY_R3"


def _string_sequence(value: JsonValue) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise contracts.SchemaContractError("retired_normalizer_error")
    return tuple(_require_string(item) for item in value)


def _mapping_sequence(value: JsonValue) -> tuple[Mapping[str, JsonValue], ...]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise contracts.SchemaContractError("source_selector_row")
    rows: list[Mapping[str, JsonValue]] = []
    for row in value:
        if not isinstance(row, Mapping):
            raise contracts.SchemaContractError("source_selector_row")
        rows += [row]
    return tuple(rows)


def _string_mapping(value: JsonValue) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise contracts.SchemaContractError("retired_normalizer_error")
    result: dict[str, str] = {}
    for key in value:
        if not isinstance(key, str):
            raise contracts.SchemaContractError("retired_normalizer_error")
        result[key] = _require_string(value[key])
    return result


def _require_string(value: JsonValue) -> str:
    if not isinstance(value, str) or value == "":
        raise contracts.SchemaContractError("retired_normalizer_error")
    return value


def _git_or_null(value: JsonValue) -> str | None:
    return value if isinstance(value, str) and len(value) == 40 else None


def _hash_mapping(value: Mapping[str, str]) -> str:
    return canonical_sha256_v2({key: value[key] for key in sorted(value)})


def _sha256_text(value: str) -> str:
    return hashlib.sha256(bytes(value, "utf-8")).hexdigest()
