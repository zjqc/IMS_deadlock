import json
from pathlib import Path
from typing import Any

import pytest

from ims_deadlock.confirmation import (
    CONFIRMATION_SCHEMA_VERSION,
    list_confirmation_case_ids,
    load_confirmation_case,
)


def _write_discovery_case(root: Path, case_id: str = "C0") -> None:
    (root / f"{case_id}.json").write_text(
        json.dumps(
            {
                "schema_version": "ims-deadlock/case/v1",
                "case_id": case_id,
                "model": {
                    "id": f"{case_id}-model",
                    "resources": [{"id": "r1", "capacity": 1, "kind": "machine"}],
                    "jobs": ["j1"],
                },
                "initial_state": {
                    "id": f"{case_id}-state",
                    "holds": [],
                    "requests": {},
                    "completed_jobs": [],
                    "stable": True,
                    "complete": False,
                    "event_calendar_empty": True,
                },
            }
        ),
        encoding="utf-8",
    )


def _confirmation_payload(case_id: str = "G4-HELD-OUT") -> dict[str, Any]:
    return {
        "schema_version": CONFIRMATION_SCHEMA_VERSION,
        "case_id": case_id,
        "family": "G4",
        "held_out": True,
        "status": "PREREGISTERED",
        "protocol": "g4_confirmation_freeze_v1",
        "contamination": {
            "derived_from_discovery_case": False,
            "excluded_discovery_case_ids": ["C0", "C1"],
            "provenance": "independent_preregistration",
        },
        "input_payload": {"resource_count": 3, "jobs": ["j1", "j2"]},
        "expected_outputs_schema": {
            "type": "object",
            "required": ["classification"],
        },
    }


def _write_confirmation_case(
    root: Path, payload: dict[str, Any], filename: str | None = None
) -> Path:
    path = (
        root
        / "confirmation"
        / "g4"
        / "cases"
        / f"{filename or payload['case_id']}.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_list_confirmation_case_ids_reads_g4_confirmation_folder_only(
    tmp_path: Path,
) -> None:
    _write_discovery_case(tmp_path, "C0")
    _write_discovery_case(tmp_path, "C1")
    _write_confirmation_case(tmp_path, _confirmation_payload("G4-B"))
    _write_confirmation_case(tmp_path, _confirmation_payload("G4-A"))

    assert list_confirmation_case_ids("g4", root=tmp_path) == ("G4-A", "G4-B")


def test_load_confirmation_case_accepts_preregistered_data_only(
    tmp_path: Path,
) -> None:
    _write_discovery_case(tmp_path, "C0")
    _write_discovery_case(tmp_path, "C1")
    _write_confirmation_case(tmp_path, _confirmation_payload())

    case = load_confirmation_case("G4-HELD-OUT", "g4", root=tmp_path)

    assert case.case_id == "G4-HELD-OUT"
    assert case.family == "G4"
    assert case.held_out is True
    assert case.contamination["derived_from_discovery_case"] is False


def test_confirmation_loader_rejects_discovery_derived_fixture(
    tmp_path: Path,
) -> None:
    _write_discovery_case(tmp_path, "C0")
    _write_discovery_case(tmp_path, "C1")
    payload = _confirmation_payload()
    contamination = dict(payload["contamination"])
    contamination["derived_from_discovery_case"] = True
    payload["contamination"] = contamination
    _write_confirmation_case(tmp_path, payload)

    with pytest.raises(ValueError, match="derived from discovery"):
        load_confirmation_case("G4-HELD-OUT", "g4", root=tmp_path)


def test_confirmation_loader_rejects_unknown_provenance(tmp_path: Path) -> None:
    _write_discovery_case(tmp_path, "C0")
    _write_discovery_case(tmp_path, "C1")
    payload = _confirmation_payload()
    contamination = dict(payload["contamination"])
    contamination["provenance"] = "discovery_snapshot"
    payload["contamination"] = contamination
    _write_confirmation_case(tmp_path, payload)

    with pytest.raises(ValueError, match="unsupported confirmation provenance"):
        load_confirmation_case("G4-HELD-OUT", "g4", root=tmp_path)


def test_confirmation_loader_rejects_payload_id_mismatch(tmp_path: Path) -> None:
    _write_discovery_case(tmp_path, "C0")
    _write_discovery_case(tmp_path, "C1")
    _write_confirmation_case(
        tmp_path, _confirmation_payload("G4-OTHER"), filename="G4-HELD-OUT"
    )

    with pytest.raises(ValueError, match="payload case_id"):
        load_confirmation_case("G4-HELD-OUT", "g4", root=tmp_path)


def test_confirmation_loader_rejects_omitted_discovery_exclusion(
    tmp_path: Path,
) -> None:
    _write_discovery_case(tmp_path, "C0")
    _write_discovery_case(tmp_path, "C1")
    payload = _confirmation_payload()
    contamination = dict(payload["contamination"])
    contamination["excluded_discovery_case_ids"] = ["C0"]
    payload["contamination"] = contamination
    _write_confirmation_case(tmp_path, payload)

    with pytest.raises(ValueError, match="complete discovery exclusion"):
        load_confirmation_case("G4-HELD-OUT", "g4", root=tmp_path)


def test_confirmation_loader_rejects_nested_result_bearing_key(
    tmp_path: Path,
) -> None:
    _write_discovery_case(tmp_path, "C0")
    _write_discovery_case(tmp_path, "C1")
    payload = _confirmation_payload()
    payload["input_payload"] = {"nested": [{"observed_result": "deadlock"}]}
    _write_confirmation_case(tmp_path, payload)

    with pytest.raises(ValueError, match="result-bearing key"):
        load_confirmation_case("G4-HELD-OUT", "g4", root=tmp_path)


def test_confirmation_loader_rejects_duplicate_json_key(tmp_path: Path) -> None:
    _write_discovery_case(tmp_path, "C0")
    _write_discovery_case(tmp_path, "C1")
    path = tmp_path / "confirmation" / "g4" / "cases" / "G4-DUP.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        """
        {
          "schema_version": "ims-deadlock/confirmation-case/v1",
          "case_id": "G4-DUP",
          "case_id": "G4-DUP-2"
        }
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate JSON key"):
        load_confirmation_case("G4-DUP", "g4", root=tmp_path)


def test_confirmation_loader_rejects_unknown_protocol(tmp_path: Path) -> None:
    _write_discovery_case(tmp_path, "C0")
    _write_discovery_case(tmp_path, "C1")
    payload = _confirmation_payload()
    payload["protocol"] = "ad_hoc_analysis"
    _write_confirmation_case(tmp_path, payload)

    with pytest.raises(ValueError, match="unknown confirmation protocol"):
        load_confirmation_case("G4-HELD-OUT", "g4", root=tmp_path)


def test_confirmation_loader_rejects_discovery_id_reuse(tmp_path: Path) -> None:
    _write_discovery_case(tmp_path, "C0")
    _write_discovery_case(tmp_path, "C1")
    payload = _confirmation_payload("C0")
    _write_confirmation_case(tmp_path, payload)

    with pytest.raises(ValueError, match="reuses discovery case id"):
        load_confirmation_case("C0", "g4", root=tmp_path)


def test_confirmation_loader_rejects_path_traversal_case_id(
    tmp_path: Path,
) -> None:
    _write_discovery_case(tmp_path, "C0")
    _write_discovery_case(tmp_path, "C1")

    with pytest.raises(ValueError, match="confirmation case_id"):
        load_confirmation_case("../EVIL", "g4", root=tmp_path)


def test_confirmation_loader_requires_literal_boolean_true(
    tmp_path: Path,
) -> None:
    _write_discovery_case(tmp_path, "C0")
    _write_discovery_case(tmp_path, "C1")
    payload = _confirmation_payload()
    payload["held_out"] = "false"
    _write_confirmation_case(tmp_path, payload)

    with pytest.raises(ValueError, match="held_out=true"):
        load_confirmation_case("G4-HELD-OUT", "g4", root=tmp_path)


def test_confirmation_listing_rejects_nonuppercase_filename(
    tmp_path: Path,
) -> None:
    _write_discovery_case(tmp_path, "C0")
    _write_discovery_case(tmp_path, "C1")
    _write_confirmation_case(
        tmp_path,
        _confirmation_payload("G4-VALID"),
        filename="g4-invalid",
    )

    with pytest.raises(ValueError, match="confirmation case_id"):
        list_confirmation_case_ids("g4", root=tmp_path)
