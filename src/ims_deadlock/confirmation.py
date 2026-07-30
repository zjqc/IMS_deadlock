"""Data-only loading for held-out confirmation case preregistrations."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ims_deadlock import cases

CONFIRMATION_SCHEMA_VERSION = "ims-deadlock/confirmation-case/v1"

_ALLOWED_PROTOCOLS = frozenset({"g4_confirmation_freeze_v1"})
_ALLOWED_PROVENANCE = frozenset({"independent_preregistration"})
_RESULT_BEARING_KEYS = frozenset(
    {
        "confirmation_result",
        "estimate",
        "fail",
        "match",
        "measured",
        "observed_result",
        "pass",
    }
)


@dataclass(frozen=True)
class ConfirmationCase:
    """Preregistered held-out confirmation case structure."""

    case_id: str
    family: str
    held_out: bool
    status: str
    protocol: str
    contamination: Mapping[str, object]
    input_payload: Mapping[str, object]
    expected_outputs_schema: Mapping[str, object]


def list_confirmation_case_ids(
    family: str, *, root: Path | None = None
) -> tuple[str, ...]:
    """List preregistered confirmation case IDs for a family."""

    family_id = _validate_family(family)
    confirmation_dir = _confirmation_dir(family_id, root=root)
    if not confirmation_dir.exists():
        return ()
    case_ids: list[str] = []
    normalized_ids: set[str] = set()
    for path in sorted(confirmation_dir.glob("*.json")):
        if not path.is_file():
            continue
        case_id = _validate_case_id(path.stem)
        normalized = case_id.casefold()
        if normalized in normalized_ids:
            msg = f"duplicate confirmation case_id {case_id!r}"
            raise ValueError(msg)
        normalized_ids.add(normalized)
        case_ids.append(case_id)
    return tuple(case_ids)


def load_confirmation_case(
    case_id: str, family: str, *, root: Path | None = None
) -> ConfirmationCase:
    """Load and validate a held-out confirmation preregistration."""

    family_id = _validate_family(family)
    normalized_case_id = _validate_case_id(case_id)
    confirmation_dir = _confirmation_dir(family_id, root=root).resolve()
    path = (confirmation_dir / f"{normalized_case_id}.json").resolve()
    if path.parent != confirmation_dir:
        msg = "confirmation case_id must stay inside its family directory"
        raise ValueError(msg)
    if not path.exists():
        msg = f"unknown confirmation case {case_id!r} for family {family_id!r}"
        raise ValueError(msg)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.loads(
            handle.read(), object_pairs_hook=_no_duplicate_keys_object_pairs_hook
        )
    return _confirmation_case_from_json(
        payload,
        requested_case_id=normalized_case_id,
        family_id=family_id,
        root=root,
    )


def _confirmation_case_from_json(
    payload: Mapping[str, Any],
    *,
    requested_case_id: str,
    family_id: str,
    root: Path | None,
) -> ConfirmationCase:
    _reject_result_bearing_keys(payload)
    schema_version = str(payload["schema_version"])
    if schema_version != CONFIRMATION_SCHEMA_VERSION:
        msg = (
            f"confirmation schema version {schema_version!r} does not match "
            f"expected {CONFIRMATION_SCHEMA_VERSION!r}"
        )
        raise ValueError(msg)

    case_id = _validate_case_id(str(payload["case_id"]))
    if case_id != requested_case_id:
        msg = "confirmation payload case_id must match the requested case"
        raise ValueError(msg)
    family = _validate_family(str(payload["family"]))
    if family != family_id:
        msg = f"confirmation family {family!r} does not match requested {family_id!r}"
        raise ValueError(msg)
    discovery_case_ids = cases.list_case_ids(root=root)
    if case_id in discovery_case_ids:
        msg = f"confirmation case {case_id!r} reuses discovery case id"
        raise ValueError(msg)

    held_out_value = payload["held_out"]
    if held_out_value is not True:
        msg = "confirmation case must declare held_out=true"
        raise ValueError(msg)
    held_out = True

    protocol = str(payload["protocol"])
    if protocol not in _ALLOWED_PROTOCOLS:
        msg = f"unknown confirmation protocol {protocol!r}"
        raise ValueError(msg)

    contamination = _mapping(payload["contamination"], field_name="contamination")
    if contamination.get("derived_from_discovery_case") is not False:
        msg = "confirmation case must not be derived from discovery"
        raise ValueError(msg)
    provenance = str(contamination.get("provenance", ""))
    if provenance not in _ALLOWED_PROVENANCE:
        msg = f"unsupported confirmation provenance {provenance!r}"
        raise ValueError(msg)
    _validate_complete_discovery_exclusions(contamination, discovery_case_ids)

    input_payload = _mapping(payload["input_payload"], field_name="input_payload")
    expected_outputs_schema = _mapping(
        payload["expected_outputs_schema"], field_name="expected_outputs_schema"
    )
    return ConfirmationCase(
        case_id=case_id,
        family=family,
        held_out=held_out,
        status=str(payload["status"]),
        protocol=protocol,
        contamination=contamination,
        input_payload=input_payload,
        expected_outputs_schema=expected_outputs_schema,
    )


def _confirmation_dir(family_id: str, *, root: Path | None) -> Path:
    cases_dir = cases._CASES_DIR if root is None else root
    return cases_dir / "confirmation" / family_id.lower() / "cases"


def _validate_family(family: str) -> str:
    family_id = family.upper()
    if family_id != "G4":
        msg = f"unsupported confirmation family {family!r}"
        raise ValueError(msg)
    return family_id


def _validate_case_id(case_id: str) -> str:
    if re.fullmatch(r"[A-Z0-9][A-Z0-9_-]*", case_id) is None:
        msg = "confirmation case_id must be uppercase ASCII with no path separators"
        raise ValueError(msg)
    return case_id


def _mapping(value: object, *, field_name: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        msg = f"{field_name} must be a JSON object"
        raise ValueError(msg)
    return value


def _validate_complete_discovery_exclusions(
    contamination: Mapping[str, object], discovery_case_ids: tuple[str, ...]
) -> None:
    declared = contamination.get("excluded_discovery_case_ids")
    if not isinstance(declared, list):
        msg = "complete discovery exclusion list is required"
        raise ValueError(msg)
    excluded_case_ids = tuple(str(case_id) for case_id in declared)
    if set(excluded_case_ids) != set(discovery_case_ids):
        msg = "complete discovery exclusion list is required"
        raise ValueError(msg)
    if len(set(excluded_case_ids)) != len(excluded_case_ids):
        msg = "duplicate discovery exclusion case id"
        raise ValueError(msg)


def _reject_result_bearing_keys(value: object) -> None:
    if isinstance(value, dict):
        for key, nested_value in value.items():
            if str(key).lower() in _RESULT_BEARING_KEYS:
                msg = f"result-bearing key {key!r} is forbidden"
                raise ValueError(msg)
            _reject_result_bearing_keys(nested_value)
    elif isinstance(value, list):
        for item in value:
            _reject_result_bearing_keys(item)


def _no_duplicate_keys_object_pairs_hook(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in pairs:
        if key in payload:
            msg = f"duplicate JSON key {key!r}"
            raise ValueError(msg)
        payload[key] = value
    return payload
