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
_RELATIVE_ROOT = Path("cases/discovery/g6b/row_families/structural_discovery_v1")
_COMMON_KEYS = {
    "schema_version",
    "study_role",
    "confirmation_use",
    "scientific_execution_authorized",
    "case_creation_authorized",
}
_SCHEMA_VERSIONS = {
    "row_family_protocol.json": G6B_ROW_FAMILY_PROTOCOL_VERSION,
    "identity_schema.json": G6B_ROW_FAMILY_IDENTITY_VERSION,
    "row_family_matrix.json": G6B_ROW_FAMILY_MATRIX_VERSION,
    "reuse_matrix.json": G6B_ROW_FAMILY_REUSE_VERSION,
    "overlap_report_schema.json": G6B_ROW_FAMILY_OVERLAP_VERSION,
    "runtime_lock_schema.json": G6B_ROW_FAMILY_RUNTIME_LOCK_VERSION,
    "review_state.json": G6B_ROW_FAMILY_REVIEW_STATE_VERSION,
    "failure_ledger.json": G6B_ROW_FAMILY_FAILURE_LEDGER_VERSION,
}
_EXPECTED_ROW_FAMILY_PROTOCOL: JsonObject = {
    "schema_version": "ims-deadlock/g6b-row-family-protocol/v1",
    "study_role": "discovery_only",
    "confirmation_use": "prohibited",
    "scientific_execution_authorized": False,
    "case_creation_authorized": False,
    "protocol_id": "G6-B-ROW-FAMILY-STRUCTURAL-DISCOVERY-V1",
    "adversarial_review_status": "PENDING",
    "bundle_role": "schema_only",
    "source_design": "docs/superpowers/specs/2026-07-31-g6b-row-family-design.md",
    "artifact_paths": [
        "cases/discovery/g6b/row_families/structural_discovery_v1/identity_schema.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "row_family_matrix.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/reuse_matrix.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "overlap_report_schema.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "runtime_lock_schema.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/review_state.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/failure_ledger.json",
    ],
    "execution_boundary": {
        "case_creation": "prohibited",
        "enumeration": "prohibited",
        "ctmc": "prohibited",
        "des": "prohibited",
        "output_inspection": "prohibited",
    },
}


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


def _repo_root_for(bundle_root: Path) -> Path | None:
    parts = _RELATIVE_ROOT.parts
    if tuple(bundle_root.parts[-len(parts) :]) != parts:
        return None
    return bundle_root.parents[len(parts) - 1]


def _expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _exact_keys(
    document: JsonObject,
    expected: set[str],
    label: str,
    errors: list[str],
) -> None:
    missing = sorted(expected - set(document))
    extra = sorted(set(document) - expected)
    if missing:
        errors.append(f"{label}: missing keys: {missing}")
    if extra:
        errors.append(f"{label}: unexpected keys: {extra}")


def _expect_exact_document(
    actual: JsonObject,
    expected: JsonObject,
    label: str,
    errors: list[str],
) -> None:
    _exact_keys(actual, set(expected), label, errors)
    if actual != expected:
        errors.append(f"{label}: document must match the canonical contract")


def _common_contract(
    document: JsonObject,
    label: str,
    schema_version: str,
    errors: list[str],
) -> None:
    _expect(
        document.get("schema_version") == schema_version,
        f"{label}: wrong schema_version",
        errors,
    )
    _expect(
        document.get("study_role") == "discovery_only",
        f"{label}: study_role must be discovery_only",
        errors,
    )
    _expect(
        document.get("confirmation_use") == "prohibited",
        f"{label}: confirmation_use must be prohibited",
        errors,
    )
    _expect(
        document.get("scientific_execution_authorized") is False,
        f"{label}: scientific_execution_authorized must be false",
        errors,
    )
    _expect(
        document.get("case_creation_authorized") is False,
        f"{label}: case_creation_authorized must be false",
        errors,
    )


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
        repo_root = _repo_root_for(bundle_root)
        if repo_root is None:
            errors.append(
                "bundle root must be <repo>/cases/discovery/g6b/"
                "row_families/structural_discovery_v1"
            )
        elif not (
            repo_root / "docs/superpowers/specs/2026-07-31-g6b-row-family-design.md"
        ).is_file():
            errors.append("source design path is missing")
        for name, version in _SCHEMA_VERSIONS.items():
            _common_contract(documents[name], name, version, errors)
        _expect_exact_document(
            documents["row_family_protocol.json"],
            _EXPECTED_ROW_FAMILY_PROTOCOL,
            "row_family_protocol.json",
            errors,
        )
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
