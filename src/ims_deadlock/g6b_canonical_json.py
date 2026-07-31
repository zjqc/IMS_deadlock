from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from typing import TypeAlias, cast

JsonValue: TypeAlias = (
    None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
)
JsonObject: TypeAlias = dict[str, JsonValue]
JsonPath: TypeAlias = tuple[str | int, ...]

_LOWER_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_DRIVE_LETTER_RE = re.compile(r"^[A-Za-z]:")
_CANONICAL_DECIMAL_RE = re.compile(r"^-?(0|[1-9][0-9]*)(\.[0-9]*[1-9])?$")
_HISTORICAL_JSON_NUMBER_RE = re.compile(
    r"-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?"
)


class CanonicalJsonError(ValueError):
    code: str

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def loads_v2(raw: str) -> JsonValue:
    try:
        value = cast(
            JsonValue,
            json.loads(
                raw,
                object_pairs_hook=_object_without_duplicate_members,
                parse_int=_parse_json_int,
                parse_float=_parse_json_float,
                parse_constant=_parse_json_constant,
            ),
        )
    except json.JSONDecodeError as exc:
        raise CanonicalJsonError("invalid_json") from exc
    _validate_canonical_value(
        value,
        path=(),
        set_like_paths=frozenset(),
        seen_set_like_paths=set(),
    )
    return value


def canonical_bytes_v2(
    value: JsonValue,
    *,
    set_like_paths: frozenset[JsonPath] = frozenset(),
) -> bytes:
    seen_set_like_paths: set[JsonPath] = set()
    _validate_canonical_value(
        value,
        path=(),
        set_like_paths=set_like_paths,
        seen_set_like_paths=seen_set_like_paths,
    )
    missing_paths = set_like_paths - seen_set_like_paths
    if missing_paths:
        raise CanonicalJsonError("set_like_path_missing")
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256_v2(
    value: JsonValue,
    *,
    set_like_paths: frozenset[JsonPath] = frozenset(),
) -> str:
    canonical_bytes = canonical_bytes_v2(value, set_like_paths=set_like_paths)
    return hashlib.sha256(canonical_bytes).hexdigest()


def canonical_decimal_from_historical_token(token: str) -> str:
    if not _HISTORICAL_JSON_NUMBER_RE.fullmatch(token):
        raise CanonicalJsonError("invalid_decimal_token")
    try:
        value = Decimal(token)
    except InvalidOperation as exc:
        raise CanonicalJsonError("invalid_decimal_token") from exc
    if not value.is_finite() or (value.is_zero() and value.is_signed()):
        raise CanonicalJsonError("invalid_decimal_token")

    decimal_text = format(value, "f")
    if "." in decimal_text:
        decimal_text = decimal_text.rstrip("0").rstrip(".")
    if decimal_text in {"", "-0"}:
        decimal_text = "0"
    try:
        validate_canonical_decimal_string(decimal_text)
    except CanonicalJsonError as exc:
        raise CanonicalJsonError("invalid_decimal_token") from exc
    return decimal_text


def validate_canonical_decimal_string(value: str) -> None:
    if value == "-0" or not _CANONICAL_DECIMAL_RE.fullmatch(value):
        raise CanonicalJsonError("noncanonical_decimal_string")


def validate_repo_relative_posix_path(value: str) -> None:
    _validate_nfc(value)
    if value == "":
        raise CanonicalJsonError("path_empty")
    if _DRIVE_LETTER_RE.match(value):
        raise CanonicalJsonError("path_drive_letter")
    if value.startswith("/"):
        raise CanonicalJsonError("path_absolute")
    if "\\" in value:
        raise CanonicalJsonError("path_backslash")

    parts = value.split("/")
    if any(part == "" for part in parts):
        raise CanonicalJsonError("path_empty_component")
    if any(part == "." for part in parts):
        raise CanonicalJsonError("path_dot_component")
    if any(part == ".." for part in parts):
        raise CanonicalJsonError("path_parent_component")


def finalized_self_hash(record: JsonObject, field: str) -> str:
    _validate_self_hash_common(record, field)
    if record[field] is None:
        return canonical_sha256_v2(record)
    if record[field] == "":
        raise CanonicalJsonError("empty_hash")
    raise CanonicalJsonError("prepopulated_digest")


def verify_finalized_self_hash(record: JsonObject, field: str) -> None:
    _validate_self_hash_common(record, field)
    digest = record[field]
    if digest == "":
        raise CanonicalJsonError("empty_hash")
    if not isinstance(digest, str) or not _LOWER_SHA256_RE.fullmatch(digest):
        raise CanonicalJsonError("invalid_hash_digest")

    preimage = dict(record)
    preimage[field] = None
    expected = canonical_sha256_v2(preimage)
    if digest != expected:
        raise CanonicalJsonError("self_hash_mismatch")


def validate_hash_reference_dag(
    record_ids: frozenset[str],
    upstream_by_record_id: Mapping[str, frozenset[str]],
) -> None:
    for record_id, upstream_ids in upstream_by_record_id.items():
        if record_id not in record_ids:
            raise CanonicalJsonError("hash_dag_missing_node")
        for upstream_id in upstream_ids:
            if upstream_id not in record_ids:
                raise CanonicalJsonError("hash_dag_missing_node")
            if upstream_id == record_id:
                raise CanonicalJsonError("hash_dag_self_loop")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(record_id: str) -> None:
        if record_id in visited:
            return
        if record_id in visiting:
            raise CanonicalJsonError("hash_dag_cycle")
        visiting.add(record_id)
        for upstream_id in upstream_by_record_id.get(record_id, frozenset()):
            visit(upstream_id)
        visiting.remove(record_id)
        visited.add(record_id)

    for record_id in record_ids:
        visit(record_id)


def _object_without_duplicate_members(
    pairs: list[tuple[str, JsonValue]],
) -> dict[str, JsonValue]:
    result: dict[str, JsonValue] = {}
    for key, value in pairs:
        if key in result:
            raise CanonicalJsonError("duplicate_member")
        result[key] = value
    return result


def _parse_json_int(token: str) -> int:
    if token == "-0":
        raise CanonicalJsonError("negative_zero")
    return int(token)


def _parse_json_float(token: str) -> float:
    if Decimal(token).is_zero() and token.startswith("-"):
        raise CanonicalJsonError("negative_zero")
    raise CanonicalJsonError("json_float_prohibited")


def _parse_json_constant(token: str) -> None:
    del token
    raise CanonicalJsonError("non_finite_number")


def _validate_canonical_value(
    value: JsonValue,
    *,
    path: JsonPath,
    set_like_paths: frozenset[JsonPath],
    seen_set_like_paths: set[JsonPath],
) -> None:
    if path in set_like_paths and not isinstance(value, list):
        raise CanonicalJsonError("set_like_path_not_array")
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        raise CanonicalJsonError("json_float_prohibited")
    if isinstance(value, str):
        _validate_nfc(value)
        return
    if isinstance(value, list):
        _validate_set_like_array(
            value,
            path=path,
            set_like_paths=set_like_paths,
            seen_set_like_paths=seen_set_like_paths,
        )
        for index, item in enumerate(value):
            _validate_canonical_value(
                item,
                path=(*path, index),
                set_like_paths=set_like_paths,
                seen_set_like_paths=seen_set_like_paths,
            )
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _validate_nfc(key)
            _validate_canonical_value(
                item,
                path=(*path, key),
                set_like_paths=set_like_paths,
                seen_set_like_paths=seen_set_like_paths,
            )
        return
    raise CanonicalJsonError("unsupported_json_value")


def _validate_nfc(value: str) -> None:
    if unicodedata.normalize("NFC", value) != value:
        raise CanonicalJsonError("non_nfc_string")


def _validate_set_like_array(
    value: list[JsonValue],
    *,
    path: JsonPath,
    set_like_paths: frozenset[JsonPath],
    seen_set_like_paths: set[JsonPath],
) -> None:
    if path not in set_like_paths:
        return
    seen_set_like_paths.add(path)

    encoded_items = [
        canonical_bytes_v2(item, set_like_paths=frozenset()) for item in value
    ]
    if len(set(encoded_items)) != len(encoded_items):
        raise CanonicalJsonError("set_like_array_duplicate")
    if encoded_items != sorted(encoded_items):
        raise CanonicalJsonError("set_like_array_unsorted")


def _validate_self_hash_common(record: JsonObject, field: str) -> None:
    if not isinstance(field, str) or field == "":
        raise CanonicalJsonError("invalid_hash_field")
    try:
        _validate_nfc(field)
    except CanonicalJsonError as exc:
        raise CanonicalJsonError("invalid_hash_field") from exc
    if "hash_excludes_fields" in record:
        raise CanonicalJsonError("hash_excludes_fields")
    if field not in record:
        raise CanonicalJsonError("missing_hash")
