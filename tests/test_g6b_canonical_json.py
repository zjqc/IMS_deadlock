from __future__ import annotations

from typing import Any, cast

import pytest

from ims_deadlock.g6b_canonical_json import (
    CanonicalJsonError,
    JsonObject,
    JsonValue,
    canonical_bytes_v2,
    canonical_decimal_from_historical_token,
    canonical_sha256_v2,
    finalized_self_hash,
    loads_v2,
    validate_canonical_decimal_string,
    validate_hash_reference_dag,
    validate_repo_relative_posix_path,
    verify_finalized_self_hash,
)


def assert_error_code(
    exc_info: pytest.ExceptionInfo[CanonicalJsonError],
    code: str,
) -> None:
    assert exc_info.value.code == code
    assert code in str(exc_info.value)


@pytest.mark.parametrize(
    ("raw", "code"),
    [
        ('{"a":1,"a":2}', "duplicate_member"),
        ('{"nested":{"a":1,"a":2}}', "duplicate_member"),
        ('{"e\\u0301":1}', "non_nfc_string"),
        ('{"text":"e\\u0301"}', "non_nfc_string"),
        ('{"value":NaN}', "non_finite_number"),
        ('{"value":Infinity}', "non_finite_number"),
        ('{"value":-Infinity}', "non_finite_number"),
        ('{"value":-0}', "negative_zero"),
        ('{"value":-0.0}', "negative_zero"),
        ('{"value":-0e0}', "negative_zero"),
        ('{"value":1.5}', "json_float_prohibited"),
    ],
)
def test_loads_v2_rejects_noncanonical_json(raw: str, code: str) -> None:
    with pytest.raises(CanonicalJsonError, match=code) as exc_info:
        loads_v2(raw)
    assert_error_code(exc_info, code)


@pytest.mark.parametrize("raw", ['{"a":', '{"a":1} trailing'])
def test_loads_v2_wraps_json_syntax_errors(raw: str) -> None:
    with pytest.raises(CanonicalJsonError, match="invalid_json") as exc_info:
        loads_v2(raw)
    assert_error_code(exc_info, "invalid_json")


def test_canonical_bytes_v2_uses_utf8_sorted_compact_bytes_and_array_order() -> None:
    value: JsonValue = {"z": "é", "a": 1, "items": ["b", "a"]}

    assert canonical_bytes_v2(value) == '{"a":1,"items":["b","a"],"z":"é"}'.encode()
    assert (
        canonical_sha256_v2({"z": "é", "a": 1})
        == "160c52d506c747530bfe5649cb89704189ea10f8734fbb2a6c6b04cbddf687c8"
    )


def test_canonical_bytes_v2_rejects_direct_python_float_and_non_nfc() -> None:
    with pytest.raises(CanonicalJsonError, match="json_float_prohibited") as float_exc:
        canonical_bytes_v2({"value": 1.5})
    assert_error_code(float_exc, "json_float_prohibited")

    with pytest.raises(CanonicalJsonError, match="non_nfc_string") as nfc_exc:
        canonical_bytes_v2({"text": "e\u0301"})
    assert_error_code(nfc_exc, "non_nfc_string")


def test_canonical_bytes_v2_validates_set_like_array_paths() -> None:
    composite_sorted: JsonValue = {
        "items": [{"name": "a", "rank": 1}, {"name": "b", "rank": 2}]
    }
    indexed_nested: JsonValue = {"groups": [{"ids": ["a", "b"]}]}
    assert (
        canonical_bytes_v2(
            {"outer": {"ids": ["a", "b", "c"]}},
            set_like_paths=frozenset({("outer", "ids")}),
        )
        == b'{"outer":{"ids":["a","b","c"]}}'
    )
    assert (
        canonical_bytes_v2(
            composite_sorted,
            set_like_paths=frozenset({("items",)}),
        )
        == b'{"items":[{"name":"a","rank":1},{"name":"b","rank":2}]}'
    )
    assert (
        canonical_bytes_v2(
            indexed_nested,
            set_like_paths=frozenset({("groups", 0, "ids")}),
        )
        == b'{"groups":[{"ids":["a","b"]}]}'
    )

    with pytest.raises(CanonicalJsonError, match="set_like_array_duplicate") as dup_exc:
        canonical_bytes_v2({"ids": ["a", "a"]}, set_like_paths=frozenset({("ids",)}))
    assert_error_code(dup_exc, "set_like_array_duplicate")

    with pytest.raises(CanonicalJsonError, match="set_like_array_unsorted") as sort_exc:
        canonical_bytes_v2({"ids": ["b", "a"]}, set_like_paths=frozenset({("ids",)}))
    assert_error_code(sort_exc, "set_like_array_unsorted")

    composite_unsorted: JsonValue = {
        "items": [{"name": "b", "rank": 2}, {"name": "a", "rank": 1}]
    }
    with pytest.raises(CanonicalJsonError, match="set_like_array_unsorted") as obj_exc:
        canonical_bytes_v2(
            composite_unsorted,
            set_like_paths=frozenset({("items",)}),
        )
    assert_error_code(obj_exc, "set_like_array_unsorted")

    with pytest.raises(CanonicalJsonError, match="set_like_path_missing") as miss_exc:
        canonical_bytes_v2({"ids": ["a"]}, set_like_paths=frozenset({("missing",)}))
    assert_error_code(miss_exc, "set_like_path_missing")

    with pytest.raises(CanonicalJsonError, match="set_like_path_not_array") as type_exc:
        canonical_bytes_v2({"ids": "a"}, set_like_paths=frozenset({("ids",)}))
    assert_error_code(type_exc, "set_like_path_not_array")


def test_spec_17_3_03_schema_self_hash_and_dag() -> None:
    record: JsonObject = {
        "record_id": "r1",
        "payload": {"value": 1},
        "record_sha256": None,
    }
    digest = finalized_self_hash(record, "record_sha256")
    finalized_record: JsonObject = {**record, "record_sha256": digest}
    verify_finalized_self_hash(finalized_record, "record_sha256")

    missing_hash_record: JsonObject = {"record_id": "r1"}
    mutations: list[tuple[JsonObject, str]] = [
        (missing_hash_record, "missing_hash"),
        ({**record, "record_sha256": ""}, "empty_hash"),
        ({**record, "record_sha256": digest}, "prepopulated_digest"),
        ({**record, "hash_excludes_fields": ["other"]}, "hash_excludes_fields"),
    ]
    for mutated, code in mutations:
        with pytest.raises(CanonicalJsonError, match=code) as exc_info:
            finalized_self_hash(mutated, "record_sha256")
        assert_error_code(exc_info, code)

    with pytest.raises(CanonicalJsonError, match="self_hash_mismatch") as forged_exc:
        forged_record: JsonObject = {**record, "record_sha256": "0" * 64}
        verify_finalized_self_hash(
            forged_record,
            "record_sha256",
        )
    assert_error_code(forged_exc, "self_hash_mismatch")

    invalid_fields = [
        cast(str, cast(Any, None)),
        "",
        "e\u0301_record_sha256",
    ]
    for invalid_field in invalid_fields:
        with pytest.raises(CanonicalJsonError, match="invalid_hash_field") as field_exc:
            finalized_self_hash(record, invalid_field)
        assert_error_code(field_exc, "invalid_hash_field")

    validate_hash_reference_dag(
        frozenset({"a", "b", "c"}),
        {"b": frozenset({"a"}), "c": frozenset({"b"})},
    )

    dag_mutations = [
        ({"a": frozenset({"a"})}, "hash_dag_self_loop"),
        ({"b": frozenset({"missing"})}, "hash_dag_missing_node"),
        ({"a": frozenset({"b"}), "b": frozenset({"a"})}, "hash_dag_cycle"),
    ]
    for upstream_by_record_id, code in dag_mutations:
        with pytest.raises(CanonicalJsonError, match=code) as exc_info:
            validate_hash_reference_dag(frozenset({"a", "b"}), upstream_by_record_id)
        assert_error_code(exc_info, code)


def test_spec_17_3_04_schema_canonical_json_refusals() -> None:
    validate_repo_relative_posix_path("cases/discovery/g6b/protocol.json")
    validate_canonical_decimal_string("0")
    validate_canonical_decimal_string("1000")
    validate_canonical_decimal_string("-12.34")

    path_mutations = [
        ("", "path_empty"),
        ("C:/case.json", "path_drive_letter"),
        ("/case.json", "path_absolute"),
        ("cases\\case.json", "path_backslash"),
        ("cases//case.json", "path_empty_component"),
        ("cases/./case.json", "path_dot_component"),
        ("cases/../case.json", "path_parent_component"),
        ("cases/link/../case.json", "path_parent_component"),
        ("cases/e\u0301.json", "non_nfc_string"),
    ]
    for path, code in path_mutations:
        with pytest.raises(CanonicalJsonError, match=code) as exc_info:
            validate_repo_relative_posix_path(path)
        assert_error_code(exc_info, code)

    with pytest.raises(CanonicalJsonError, match="set_like_array_unsorted") as exc_info:
        canonical_bytes_v2({"values": [2, 1]}, set_like_paths=frozenset({("values",)}))
    assert_error_code(exc_info, "set_like_array_unsorted")

    decimal_string_mutations = [
        "1e-7",
        "-0",
        "-0.0",
        "1.0",
        "1000.000",
        "+1",
        "01",
        " 1",
        "1 ",
        "",
        "1.2.3",
    ]
    for token in decimal_string_mutations:
        with pytest.raises(
            CanonicalJsonError,
            match="noncanonical_decimal_string",
        ) as decimal_exc:
            validate_canonical_decimal_string(token)
        assert_error_code(decimal_exc, "noncanonical_decimal_string")


def test_spec_17_3_05_schema_historical_decimal_exactness() -> None:
    vectors = {
        "1e-7": "0.0000001",
        "1000.000": "1000",
        "-12.3400": "-12.34",
        "0.0000": "0",
        "1e+6": "1000000",
        "1e-6": "0.000001",
        "1e4096": "1" + ("0" * 4096),
    }
    for token, expected in vectors.items():
        assert canonical_decimal_from_historical_token(token) == expected

    assert canonical_decimal_from_historical_token("1e-7") == "0.0000001"
    validate_canonical_decimal_string(canonical_decimal_from_historical_token("1e-7"))

    for token in [
        "-0",
        "-0.0",
        "NaN",
        "Infinity",
        "1.2.3",
        " 1",
        "+1",
        "1_000",
        "01",
        "00.1",
    ]:
        with pytest.raises(
            CanonicalJsonError,
            match="invalid_decimal_token",
        ) as exc_info:
            canonical_decimal_from_historical_token(token)
        assert_error_code(exc_info, "invalid_decimal_token")
