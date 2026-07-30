import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from ims_deadlock.g4_freeze import (
    G4_REQUIRED_BASELINES,
    G4_REQUIRED_FAMILIES,
    G4_REQUIRED_METRICS,
    canonical_json_sha256,
    check_g4_freeze,
    main,
)


def _canonical_sha(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _confirmation_case(case_id: str, family: str) -> dict[str, object]:
    return {
        "schema_version": "ims-deadlock/confirmation-case/v1",
        "case_id": case_id,
        "family": "G4",
        "held_out": True,
        "status": "PREREGISTERED",
        "protocol": "g4_confirmation_freeze_v1",
        "contamination": {
            "derived_from_discovery_case": False,
            "excluded_discovery_case_ids": [],
            "provenance": "independent_preregistration",
        },
        "input_payload": {
            "g4_family": family,
            "protocol_input": {"fixture": "development-only-freeze-test"},
        },
        "expected_outputs_schema": {
            "required_fields": ["classification"],
        },
    }


def _complete_bundle(tmp_path: Path, *, include_freeze_entry: bool = True) -> Path:
    repository_root = tmp_path / "repo"
    cases_root = repository_root / "cases"
    bundle_root = cases_root / "confirmation" / "g4"
    case_rows: list[dict[str, str]] = []
    case_ids: list[str] = []
    for index, family in enumerate(G4_REQUIRED_FAMILIES, start=1):
        case_id = f"G4-HELD-{index:02d}"
        case_ids.append(case_id)
        payload = _confirmation_case(case_id, family)
        relative_path = f"cases/{case_id}.json"
        _write_json(bundle_root / relative_path, payload)
        case_rows.append(
            {
                "case_id": case_id,
                "family": family,
                "path": relative_path,
                "hash_mode": "canonical_json",
                "sha256": _canonical_sha(payload),
            }
        )

    case_manifest = {
        "schema_version": "ims-deadlock/g4-case-manifest/v1",
        "cases": case_rows,
    }
    predictions = {
        "schema_version": "ims-deadlock/g4-predictions/v1",
        "predictions": [
            {
                "case_id": case_id,
                "prediction_class": "scope_or_refusal_prediction",
                "theory_scope": "frozen before evaluation",
                "required_evidence": ["complete finite-state oracle"],
                "falsifier": "the frozen oracle contradicts this scope statement",
            }
            for case_id in case_ids
        ],
    }
    baseline_applicability = {
        "schema_version": "ims-deadlock/g4-baselines/v1",
        "applicability": [
            {
                "case_id": case_id,
                "baselines": {
                    baseline: {
                        "applicable": False,
                        "reason": (
                            "development freeze fixture marks baseline inapplicable"
                        ),
                        "required_evidence": ["frozen applicability evidence"],
                    }
                    for baseline in G4_REQUIRED_BASELINES
                },
            }
            for case_id in case_ids
        ],
    }
    metrics_schema = {
        "schema_version": "ims-deadlock/g4-metrics/v1",
        "metrics": [
            {
                "metric_id": metric,
                "definition": f"locked definition for {metric}",
                "unit": "case",
                "denominator": "all applicable frozen cases",
                "applicability_by_case": {
                    case_id: {
                        "applicable": False,
                        "reason": "not used by this development freeze fixture",
                    }
                    for case_id in case_ids
                },
            }
            for metric in G4_REQUIRED_METRICS
        ],
    }
    runtime_lock = {
        "schema_version": "ims-deadlock/g4-runtime-lock/v1",
        "implementation_commit": "a" * 40,
        "platform": "development-test-platform",
        "python": {
            "executable": "/opt/development/python",
            "version": "3.13.0",
        },
        "packages": {"ims-deadlock": "0.1.0", "pytest": "9.0.0"},
        "commands": [
            "python -m ims_deadlock.g4_freeze --root cases/confirmation/g4 check"
        ],
    }
    random_stream_manifest = {
        "schema_version": "ims-deadlock/g4-random-streams/v1",
        "streams_by_case": {
            case_id: {
                "applicable": False,
                "reason": "exact-only development freeze fixture",
            }
            for case_id in case_ids
        },
    }

    script_path = repository_root / "src" / "ims_deadlock" / "g4_protocol.py"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text("# development freeze fixture\n", encoding="utf-8")
    experiment_scripts = {
        "schema_version": "ims-deadlock/g4-experiment-scripts/v1",
        "files": [
            {
                "path": "src/ims_deadlock/g4_protocol.py",
                "hash_mode": "file_bytes",
                "sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
            }
        ],
        "entrypoints": [
            {
                "protocol": "development_fixture",
                "callable": "ims_deadlock.g4_protocol:run_after_freeze",
            }
        ],
    }

    theory_path = repository_root / "docs" / "theory" / "G4_FIXTURE.md"
    theory_path.parent.mkdir(parents=True, exist_ok=True)
    theory_path.write_text("# Development-only theory fixture\n", encoding="utf-8")
    theory_manifest = {
        "schema_version": "ims-deadlock/g4-theory-manifest/v1",
        "files": [
            {
                "path": "docs/theory/G4_FIXTURE.md",
                "hash_mode": "file_bytes",
                "sha256": hashlib.sha256(theory_path.read_bytes()).hexdigest(),
            }
        ],
    }
    exclusions = {
        "schema_version": "ims-deadlock/g4-exclusions/v1",
        "excluded_discovery_case_ids": [],
        "forbidden_result_keys": [
            "observed_result",
            "confirmation_result",
            "estimate",
            "measured",
        ],
        "post_freeze_rules": [
            "do not replace a held-out case after inspecting an outcome"
        ],
    }

    artifacts: dict[str, object] = {
        "case_manifest.json": case_manifest,
        "predictions.json": predictions,
        "baseline_applicability.json": baseline_applicability,
        "metrics_schema.json": metrics_schema,
        "runtime_lock.json": runtime_lock,
        "random_stream_manifest.json": random_stream_manifest,
        "experiment_scripts_manifest.json": experiment_scripts,
        "theory_manifest.json": theory_manifest,
        "exclusions.json": exclusions,
    }
    for filename, artifact_payload in artifacts.items():
        _write_json(bundle_root / filename, artifact_payload)

    if include_freeze_entry:
        freeze_entry = {
            "schema_version": "ims-deadlock/g4-freeze-entry/v1",
            "freeze_id": "G4-FREEZE-DEVELOPMENT-TEST",
            "implementation_commit": "a" * 40,
            "preregistration_commit": "b" * 40,
            "date_utc": "2026-07-30T00:00:00Z",
            "owner": "development-test",
            "confirmation_results_inspected": False,
            "included_cases": case_ids,
            "excluded_cases": [],
            "artifact_hashes": {
                "case_manifest_sha256": _canonical_sha(case_manifest),
                "prediction_sheet_sha256": _canonical_sha(predictions),
                "baseline_manifest_sha256": _canonical_sha(baseline_applicability),
                "metric_schema_sha256": _canonical_sha(metrics_schema),
                "runtime_lock_sha256": _canonical_sha(runtime_lock),
                "random_stream_manifest_sha256": _canonical_sha(random_stream_manifest),
                "experiment_script_manifest_sha256": _canonical_sha(experiment_scripts),
                "theory_manifest_sha256": _canonical_sha(theory_manifest),
                "exclusions_sha256": _canonical_sha(exclusions),
            },
            "case_json_sha256_by_id": {
                row["case_id"]: row["sha256"] for row in case_rows
            },
        }
        _write_json(bundle_root / "FREEZE_ENTRY.json", freeze_entry)
    return bundle_root


def test_canonical_json_hash_is_stable_across_key_order() -> None:
    left = {"β": [2, 1], "a": {"z": True, "x": None}}
    right = {"a": {"x": None, "z": True}, "β": [2, 1]}

    assert canonical_json_sha256(left) == canonical_json_sha256(right)
    assert canonical_json_sha256(left) == _canonical_sha(left)


def test_freeze_check_reports_not_frozen_when_entry_is_missing(
    tmp_path: Path,
) -> None:
    root = _complete_bundle(tmp_path, include_freeze_entry=False)

    result = check_g4_freeze(root)

    assert result.status == "NOT_FROZEN"
    assert "missing required artifact FREEZE_ENTRY.json" in result.errors


def test_freeze_check_reports_frozen_for_complete_hash_locked_bundle(
    tmp_path: Path,
) -> None:
    root = _complete_bundle(tmp_path)

    result = check_g4_freeze(root)

    assert result.status == "FROZEN"
    assert result.errors == ()
    assert result.confirmation_results_inspected is False
    assert set(result.case_ids) == {
        f"G4-HELD-{index:02d}" for index in range(1, len(G4_REQUIRED_FAMILIES) + 1)
    }


def test_freeze_check_rejects_blank_or_mismatched_hash(tmp_path: Path) -> None:
    root = _complete_bundle(tmp_path)
    entry_path = root / "FREEZE_ENTRY.json"
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    entry["artifact_hashes"]["metric_schema_sha256"] = ""
    _write_json(entry_path, entry)

    blank = check_g4_freeze(root)

    assert blank.status == "NOT_FROZEN"
    assert any("metric_schema_sha256" in error for error in blank.errors)

    entry["artifact_hashes"]["metric_schema_sha256"] = "0" * 64
    _write_json(entry_path, entry)
    mismatched = check_g4_freeze(root)
    assert any(
        "metric_schema_sha256 hash mismatch" in error for error in mismatched.errors
    )


def test_freeze_check_requires_all_families_predictions_and_baselines(
    tmp_path: Path,
) -> None:
    root = _complete_bundle(tmp_path)
    manifest_path = root / "case_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["cases"] = manifest["cases"][:-1]
    _write_json(manifest_path, manifest)

    result = check_g4_freeze(root)

    assert result.status == "NOT_FROZEN"
    assert any("required G4 families" in error for error in result.errors)


def test_freeze_check_rejects_result_directory_or_inspected_flag(
    tmp_path: Path,
) -> None:
    root = _complete_bundle(tmp_path)
    (root / "results").mkdir()
    entry_path = root / "FREEZE_ENTRY.json"
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    entry["confirmation_results_inspected"] = True
    _write_json(entry_path, entry)

    result = check_g4_freeze(root)

    assert result.status == "NOT_FROZEN"
    assert any("result/output directory" in error for error in result.errors)
    assert any("confirmation_results_inspected" in error for error in result.errors)


def test_freeze_check_rejects_result_key_hidden_in_any_manifest(
    tmp_path: Path,
) -> None:
    root = _complete_bundle(tmp_path)
    metric_path = root / "metrics_schema.json"
    metrics = json.loads(metric_path.read_text(encoding="utf-8"))
    metrics["metrics"][0]["observed_result"] = "leaked"
    _write_json(metric_path, metrics)
    entry_path = root / "FREEZE_ENTRY.json"
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    entry["artifact_hashes"]["metric_schema_sha256"] = _canonical_sha(metrics)
    _write_json(entry_path, entry)

    result = check_g4_freeze(root)

    assert result.status == "NOT_FROZEN"
    assert any("forbidden result key" in error for error in result.errors)


def test_freeze_check_requires_distinct_implementation_and_preregistration_commits(
    tmp_path: Path,
) -> None:
    root = _complete_bundle(tmp_path)
    entry_path = root / "FREEZE_ENTRY.json"
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    entry["preregistration_commit"] = entry["implementation_commit"]
    _write_json(entry_path, entry)

    result = check_g4_freeze(root)

    assert result.status == "NOT_FROZEN"
    assert any("must be distinct" in error for error in result.errors)


def test_freeze_check_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    root = _complete_bundle(tmp_path)
    (root / "exclusions.json").write_text(
        """
        {
          "schema_version": "ims-deadlock/g4-exclusions/v1",
          "schema_version": "ims-deadlock/g4-exclusions/v1"
        }
        """,
        encoding="utf-8",
    )

    result = check_g4_freeze(root)

    assert result.status == "NOT_FROZEN"
    assert any("duplicate JSON key" in error for error in result.errors)


def test_freeze_check_rejects_path_traversal(tmp_path: Path) -> None:
    root = _complete_bundle(tmp_path)
    manifest_path = root / "theory_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"][0]["path"] = "../outside.md"
    _write_json(manifest_path, manifest)

    result = check_g4_freeze(root)

    assert result.status == "NOT_FROZEN"
    assert any("must stay inside repository root" in error for error in result.errors)


def test_freeze_check_does_not_execute_confirmation_analysis(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _complete_bundle(tmp_path)

    def forbidden(*_args: object, **_kwargs: object) -> Any:
        raise AssertionError("freeze checker executed a scientific analysis")

    monkeypatch.setattr("ims_deadlock.analysis.analyze_case", forbidden)
    monkeypatch.setattr(
        "ims_deadlock.engine.exact_max_nonblocking_supervisor", forbidden
    )
    monkeypatch.setattr(
        "ims_deadlock.stochastic.estimate_competing_absorption",
        forbidden,
    )

    result = check_g4_freeze(root)

    assert result.status == "FROZEN"


def test_internal_module_main_emits_versioned_json_and_exit_status(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    frozen_root = _complete_bundle(tmp_path / "frozen")
    not_frozen_root = _complete_bundle(
        tmp_path / "draft",
        include_freeze_entry=False,
    )

    assert main(["--root", str(frozen_root), "check"]) == 0
    frozen_output = json.loads(capsys.readouterr().out)
    assert frozen_output["schema_version"] == "ims-deadlock/g4-freeze-check/v1"
    assert frozen_output["status"] == "FROZEN"

    assert main(["--root", str(not_frozen_root), "check"]) == 1
    draft_output = json.loads(capsys.readouterr().out)
    assert draft_output["status"] == "NOT_FROZEN"
