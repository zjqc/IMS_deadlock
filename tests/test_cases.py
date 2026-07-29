import json
from pathlib import Path

import pytest
from pytest import MonkeyPatch

from ims_deadlock import cases
from ims_deadlock.cases import CASE_SCHEMA_VERSION, list_case_ids, load_case_spec


def test_case_manifest_exposes_all_discovery_cases() -> None:
    assert list_case_ids() == ("C0", "C1", "C2", "C3", "C4", "C5", "C5_DAG")


def test_case_loader_reads_json_spec_for_c0() -> None:
    spec = load_case_spec("C0")

    assert spec.schema_version == CASE_SCHEMA_VERSION
    assert spec.case_id == "C0"
    assert spec.model.id == "C0-two-resource-minimal"
    assert spec.initial_state.id == "c0-deadlocked"


def test_case_loader_rejects_schema_version_mismatch(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(cases, "_CASES_DIR", tmp_path)
    (tmp_path / "BAD.json").write_text(
        json.dumps(
            {
                "schema_version": "ims-deadlock/case/v0",
                "case_id": "BAD",
                "model": {
                    "id": "bad-model",
                    "resources": [{"id": "r1", "capacity": 1, "kind": "machine"}],
                    "jobs": ["j1"],
                },
                "initial_state": {
                    "id": "bad-state",
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

    with pytest.raises(ValueError, match="schema version"):
        load_case_spec("BAD")


def test_case_loader_rejects_duplicate_resource_ids(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(cases, "_CASES_DIR", tmp_path)
    (tmp_path / "DUP.json").write_text(
        json.dumps(
            {
                "schema_version": CASE_SCHEMA_VERSION,
                "case_id": "DUP",
                "model": {
                    "id": "dup-model",
                    "resources": [
                        {"id": "r1", "capacity": 1, "kind": "machine"},
                        {"id": "r1", "capacity": 2, "kind": "buffer"},
                    ],
                    "jobs": ["j1"],
                },
                "initial_state": {
                    "id": "dup-state",
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

    with pytest.raises(ValueError, match="duplicate resource id"):
        load_case_spec("DUP")


def test_case_loader_rejects_invalid_resource_kind(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(cases, "_CASES_DIR", tmp_path)
    (tmp_path / "KIND.json").write_text(
        json.dumps(
            {
                "schema_version": CASE_SCHEMA_VERSION,
                "case_id": "KIND",
                "model": {
                    "id": "kind-model",
                    "resources": [{"id": "r1", "capacity": 1, "kind": "robot"}],
                    "jobs": ["j1"],
                },
                "initial_state": {
                    "id": "kind-state",
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

    with pytest.raises(ValueError, match="invalid resource kind"):
        load_case_spec("KIND")
