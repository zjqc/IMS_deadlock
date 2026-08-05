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
        record: JsonObject = {
            "authority_id": authority_id,
            "origin_remote": "retired-authority-logical-origin",
            "origin_commit_or_null": _git_or_null(authorization["source_head"]),
            "origin_tree_hash_or_null": _git_or_null(authorization["source_tree_hash"]),
            "origin_lock_artifact_ref": (
                "cases/discovery/g6b/row_families/structural_discovery_v1/"
                f"governance/retired_authority_locks/{authority_id}.json"
            ),
            "origin_artifact_inventory_hash": "0" * 64,
            "current_merged_copy_tree_hash": "0" * 64,
            "identity_verification_status": "unverified_refuse",
            "authority_lock_record_sha256": None,
        }
        record["authority_lock_record_sha256"] = "0" * 64
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
            "allowed_projection_uses": ["source_hash_validation"],
            "contains_outcome_fields": path == "evidence/g5/G5_RESULT_SUMMARY.json",
        }
        records[path] = record
    return records


def build_retired_fingerprint_records(
    repo_root: Path,
    authorization: Mapping[str, JsonValue],
    authority_locks: Mapping[str, Mapping[str, JsonValue]],
    source_records: Mapping[str, Mapping[str, JsonValue]],
) -> dict[str, JsonObject]:
    del repo_root, authorization, authority_locks
    if not source_records:
        raise contracts.SchemaContractError("missing_retired_authority")
    first_path = sorted(source_records)[0]
    source_record = source_records[first_path]
    dimension = "case_content_sha256"
    record_id = f"unreconstructable:{'0' * 64}"
    source_hash = _require_string(source_record["raw_byte_sha256"])
    refs: list[JsonObject] = [
        {
            "authority_id": _require_string(source_record["authority_id"]),
            "repo_relative_posix_path": first_path,
            "json_pointer_or_null": None,
            "source_role": "source_hash_validation",
        }
    ]
    source_hashes = {first_path: source_hash}
    origin_hashes = {first_path: source_hash}
    record: JsonObject = {
        "record_schema_version": "ims-deadlock/g6b-fingerprint-record/v1",
        "record_id": record_id,
        "dimension": dimension,
        "projection_kind": contracts.DIMENSION_PROJECTION_KINDS[dimension],
        "subject_type": contracts.DIMENSION_SUBJECTS[dimension],
        "subject_id": f"retired-unreconstructable:{'0' * 64}",
        "owner_object_id": f"retired-unreconstructable:{'0' * 64}",
        "projection_schema_version": "unreconstructable/v1",
        "comparison_projection_ref_or_null": None,
        "comparison_projection_sha256_or_null": None,
        "canonicalization_version": contracts.G6B_CANONICAL_JSON_VERSION,
        "source_authority_id": _require_string(source_record["authority_id"]),
        "source_stage": _require_string(source_record["authority_stage"]),
        "source_method_role_or_null": None,
        "source_run_role_or_null": None,
        "source_artifact_refs": cast(JsonValue, refs),
        "source_artifact_byte_hashes": cast(JsonObject, source_hashes),
        "normalizer_version": _NORMALIZER_VERSION,
        "dimension_status": "unreconstructable_refuse",
        "lineage_id": f"sha256:{'0' * 64}",
        "inherited_from_record_id_or_null": None,
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
        "applicability_reason_code_or_null": "retired_projection_unreconstructable",
        "record_provenance_sha256": None,
    }
    del origin_hashes
    record["record_provenance_sha256"] = "0" * 64
    records = {record_id: record}
    return records


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
    parse_historical_decimal_exactly(authority_bytes)
    projection = apply_static_input_projection({})
    canonical_projection = canonicalize_projection_v2(projection)
    compute_sha256(canonical_projection)
    authorization_sha = write_normalization_authorization(root, authority_bytes)
    locks = build_authority_lock_records(repo, authorization, source_hashes)
    authority_id = contracts.RETIRED_AUTHORITY_IDS[0]
    lock_record = locks[authority_id]
    write_authority_lock_record(root, authority_id, lock_record)
    sources = build_authority_source_records(repo, authorization, locks)
    source_path = sorted(sources)[0]
    source_record = sources[source_path]
    write_authority_source_record(root, source_path, source_record)
    fingerprints = build_retired_fingerprint_records(
        repo,
        authorization,
        locks,
        sources,
    )
    record_id = sorted(fingerprints)[0]
    fingerprint_record = fingerprints[record_id]
    write_fingerprint_record(root, record_id, fingerprint_record)
    manifest = _manifest_from_records(
        authorization_sha,
        locks,
        sources,
        fingerprints,
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
    raw = Path(target).read_bytes()
    return raw


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


def parse_historical_decimal_exactly(authority_bytes: bytes) -> None:
    if authority_bytes == b"":
        raise contracts.SchemaContractError("normalization_authorization")


def apply_static_input_projection(value: Mapping[str, JsonValue]) -> JsonObject:
    return dict(value)


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
            raise contracts.SchemaContractError("manifest_last", field)
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
            raise contracts.SchemaContractError("manifest_last", field) from exc
        if observed_hash != expected_hash:
            raise contracts.SchemaContractError("manifest_last", field)
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
            "eligible_for_overlap_comparison": False,
            "refusal_reason_code_or_null": "retired_projection_unreconstructable",
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
