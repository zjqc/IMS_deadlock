"""Data-only validation for the G6-B row-family protocol bundle."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

JsonObject: TypeAlias = dict[str, Any]
G6B_ROW_FAMILY_PROTOCOL_VERSION = "ims-deadlock/g6b-row-family-protocol/v1"
G6B_ROW_FAMILY_IDENTITY_VERSION = "ims-deadlock/g6b-row-family-identity/v1"
G6B_ROW_FAMILY_MATRIX_VERSION = "ims-deadlock/g6b-row-family-matrix/v1"
G6B_ROW_FAMILY_REUSE_VERSION = "ims-deadlock/g6b-row-family-reuse/v1"
G6B_ROW_FAMILY_OVERLAP_VERSION = "ims-deadlock/g6b-row-family-overlap-schema/v1"
G6B_ROW_FAMILY_RUNTIME_LOCK_VERSION = (
    "ims-deadlock/g6b-row-family-runtime-lock-schema/v1"
)
G6B_ROW_FAMILY_REVIEW_STATE_VERSION = "ims-deadlock/g6b-row-family-review-state/v1"
G6B_ROW_FAMILY_FAILURE_LEDGER_VERSION = "ims-deadlock/g6b-row-family-failure-ledger/v1"
_DOCUMENTS = (
    "row_family_protocol.json",
    "identity_schema.json",
    "row_family_matrix.json",
    "reuse_matrix.json",
    "overlap_report_schema.json",
    "runtime_lock_schema.json",
    "review_state.json",
    "failure_ledger.json",
)


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


def _load_json_object(path: Path) -> JsonObject:
    try:
        loaded = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(str(exc)) from exc
    if not isinstance(loaded, dict):
        raise ValueError("root must be a JSON object")
    return loaded


def _canonical_sha256(document: JsonObject) -> str:
    payload = json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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
        try:
            document = _load_json_object(bundle_root / name)
        except ValueError as exc:
            errors.append(f"{name}: {exc}")
            continue
        documents[name] = document
        hashes[name] = _canonical_sha256(document)
    protocol = documents.get("row_family_protocol.json", {})
    review = documents.get("review_state.json", {})
    if set(documents) == set(_DOCUMENTS):
        errors.append("semantic validation incomplete")
    return G6BRowFamilyValidation(
        valid=not errors,
        errors=tuple(errors),
        scientific_execution_authorized=any(
            item.get("scientific_execution_authorized") is True
            for item in documents.values()
        ),
        case_creation_authorized=any(
            item.get("case_creation_authorized") is True for item in documents.values()
        ),
        adversarial_review_status=str(protocol.get("adversarial_review_status", "")),
        review_state=str(review.get("current_state", "")),
        bundle_hashes=hashes,
    )
