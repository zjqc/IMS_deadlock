import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from ims_deadlock.g4_freeze import (
    G4_DISCOVERY_CASE_IDS,
    G4_DISCOVERY_FAMILY_IDS,
    G4_GRID_PREDICTION_CLASS,
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
            "excluded_discovery_case_ids": list(G4_DISCOVERY_CASE_IDS),
            "excluded_discovery_family_ids": list(G4_DISCOVERY_FAMILY_IDS),
            "provenance": "independent_preregistration",
        },
        "input_payload": _protocol_input(family),
        "expected_outputs_schema": {
            "required_fields": ["classification"],
        },
    }


def _protocol_input(family: str) -> dict[str, object]:
    finite_lts = {
        "states": ["s0", "s1"],
        "initial_state": "s0",
        "marked_states": ["s1"],
        "transitions": [
            {
                "source": "s0",
                "event": "go",
                "target": "s1",
                "controllable": True,
            }
        ],
    }
    base: dict[str, object] = {
        "schema_version": "ims-deadlock/g4-protocol-input/v1",
        "g4_family": family,
    }
    if family.startswith("G4-CRP-"):
        if family == "G4-CRP-OUTSIDE-S4PR":
            finite_lts = {
                "states": ["s0"],
                "initial_state": "s0",
                "marked_states": [],
                "transitions": [],
            }
            profile: dict[str, object] = {
                "s4pr_applicable": False,
                "embedding": None,
                "embedding_sha256": None,
                "crp_pairs": [],
                "translated_target_state": None,
                "external_prefix_claimed": None,
                "outside_s4pr_reasons": ["development boundary"],
            }
            bridge = None
        else:
            embedding = {
                "places": ["p"],
                "resource_places": ["p_r"],
                "transitions": ["t"],
            }
            target = "s1" if family == "G4-CRP-S4PR-AGREE" else "s_unreachable"
            if target == "s_unreachable":
                finite_lts = {
                    **finite_lts,
                    "states": ["s0", "s1", "s_unreachable"],
                }
            profile = {
                "s4pr_applicable": True,
                "embedding": embedding,
                "embedding_sha256": _canonical_sha(embedding),
                "crp_pairs": [["p", "p_r"]],
                "translated_target_state": target,
                "external_prefix_claimed": (family == "G4-CRP-S4PR-AGREE"),
                "outside_s4pr_reasons": [],
            }
            bridge = (
                {
                    "target_state": "s1",
                    "target_snapshot": _deadlock_snapshot(),
                    "crp_resource_to_ims_resource": {"p_r": "r"},
                    "comparison_rule": "exact_resource_set_equality",
                }
                if family == "G4-CRP-S4PR-AGREE"
                else None
            )
        return base | {
            "protocol_kind": "crp_evidence_audit",
            "protocol_input": {
                "finite_lts": finite_lts,
                "state_bound": 8,
                "crp_profile": profile,
                "partial_deadlock_bridge": bridge,
                "outside_scope_generator": (
                    {
                        "generator_id": "or_and_reservation_v1",
                        "parameters": {
                            "instance_id": "DEV_OUTSIDE",
                            "fixture_capacity": 2,
                            "cart_capacity": 1,
                            "reservation_capacity": 1,
                            "decision_rate": 0.5,
                            "state_bound": 32,
                        },
                    }
                    if family == "G4-CRP-OUTSIDE-S4PR"
                    else None
                ),
            },
        }
    if family == "G4-RECORDER-TARGET-QUANTIFICATION":
        return base | {
            "protocol_kind": "fixed_recorder_target",
            "protocol_input": {
                "finite_lts": finite_lts,
                "state_bound": 8,
                "target_state": "s1",
                "recorder_events": ["go"],
                "fixed_counts": {"go": 1},
            },
        }
    if family == "G4-L30-RESOURCE-BASELINE":
        return base | {
            "protocol_kind": "supplied_l30_inequalities",
            "protocol_input": {
                "capacities": {"r": 1},
                "inequalities": [
                    {
                        "name": "i1",
                        "coefficients": [["r", 1]],
                        "rhs": 1,
                    }
                ],
                "finite_capacity_s3pr_ens3pr": True,
                "inequality_provenance": "sms_derived_external",
            },
        }
    if family == "G4-B05-SUPERVISOR-COMPARATOR":
        return base | {
            "protocol_kind": "adapted_candidate_monitor_cover",
            "protocol_input": {
                "finite_lts": finite_lts,
                "state_bound": 8,
                "legal_states": ["s0"],
                "first_met_bad_states": ["s1"],
                "candidate_monitors": [
                    {
                        "monitor_id": "m1",
                        "covered_bad_states": ["s1"],
                        "excluded_legal_states": [],
                    }
                ],
            },
        }
    if family == "G4-IMS-PARAMETER-GRID":
        return base | {
            "protocol_kind": "bidirectional_island_grid",
            "protocol_input": {
                "generator_id": "bidirectional_bas_v1",
                "cells": [
                    {
                        "cell_id": "DEV",
                        "machine_capacity": 1,
                        "buffer_capacity": 1,
                        "agv_count": 1,
                        "forward_wip": 1,
                        "reverse_wip": 1,
                        "service_rate": 1.0,
                        "transfer_rate": 0.8,
                        "release_rate": 0.4,
                        "state_bound": 64,
                    }
                ],
            },
        }
    if family == "G4-MEDIUM-ISLAND-REBUILD":
        return base | {
            "protocol_kind": "medium_island_rebuild",
            "protocol_input": {
                "generator_id": "three_island_bas_v1",
                "parameters": {
                    "instance_id": "DEV",
                    "machine_capacity": 1,
                    "buffer_capacity": 1,
                    "agv_count": 1,
                    "route_wip": {"ABG": 1, "BAG": 1, "AG": 1},
                    "service_rate": 1.0,
                    "transfer_rate": 0.8,
                    "release_rate": 0.4,
                    "state_bound": 512,
                },
            },
        }
    if family == "G4-ADVERSARIAL-BOUNDARY":
        return base | {
            "protocol_kind": "adversarial_snapshot",
            "protocol_input": {
                "generator_id": "or_and_reservation_v1",
                "parameters": {
                    "instance_id": "DEV",
                    "fixture_capacity": 2,
                    "cart_capacity": 1,
                    "reservation_capacity": 1,
                    "decision_rate": 0.5,
                    "state_bound": 32,
                },
            },
        }
    raise AssertionError(f"unknown development G4 family {family}")


def _deadlock_snapshot() -> dict[str, object]:
    return {
        "schema_version": "ims-deadlock/case/v1",
        "case_id": "G4_DEV_TARGET",
        "title": "development target",
        "status": "DEVELOPMENT",
        "model": {
            "id": "development-target",
            "resources": [{"id": "r", "capacity": 1, "kind": "machine"}],
            "jobs": ["j"],
        },
        "initial_state": {
            "id": "target",
            "holds": [{"job_id": "j", "resource_id": "r", "units": 1}],
            "requests": {"j": [[{"resource_id": "r", "units": 1}]]},
            "completed_jobs": [],
            "stable": True,
            "complete": False,
            "event_calendar_empty": True,
            "stage_by_job": {"j": "blocked"},
            "mode_by_job": {"j": "blocked"},
        },
        "transitions": [],
        "calendar": [],
        "notes": ["development fixture"],
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
                "scoring_rule": (
                    "score true exactly when every required evidence field "
                    "supports the frozen prediction class"
                ),
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
            "python -m ims_deadlock.g4_freeze --root cases/confirmation/g4 check",
            "python -m ims_deadlock.g4_protocol --root cases/confirmation/g4 validate",
            "python -m pytest tests/test_confirmation.py "
            "tests/test_g4_protocol.py tests/test_g4_freeze.py -q",
            *[
                "python -m ims_deadlock.g4_protocol --root "
                f"cases/confirmation/g4 run {case_id}"
                for case_id in case_ids
            ],
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
        "excluded_discovery_case_ids": list(G4_DISCOVERY_CASE_IDS),
        "excluded_discovery_family_ids": list(G4_DISCOVERY_FAMILY_IDS),
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
            "excluded_cases": [
                *G4_DISCOVERY_CASE_IDS,
                *G4_DISCOVERY_FAMILY_IDS,
            ],
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


def test_freeze_check_requires_exact_boolean_grid_cell_predictions(
    tmp_path: Path,
) -> None:
    root = _complete_bundle(tmp_path)
    predictions_path = root / "predictions.json"
    predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
    row = predictions["predictions"][0]
    row["prediction_class"] = G4_GRID_PREDICTION_CLASS
    row["cell_predictions"] = {
        "G01_FWD_DAG": {
            "expected_reachable_closed_core": "not-a-boolean",
            "rationale": "development invalid fixture",
        }
    }
    _write_json(predictions_path, predictions)

    entry_path = root / "FREEZE_ENTRY.json"
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    entry["artifact_hashes"]["prediction_sheet_sha256"] = _canonical_sha(predictions)
    _write_json(entry_path, entry)

    result = check_g4_freeze(root)

    assert result.status == "NOT_FROZEN"
    assert any(
        "cell_predictions must cover the exact frozen grid" in error
        for error in result.errors
    )
    assert any(
        "expected_reachable_closed_core must be boolean" in error
        for error in result.errors
    )


def test_freeze_check_requires_complete_discovery_exclusions(
    tmp_path: Path,
) -> None:
    root = _complete_bundle(tmp_path)
    exclusions_path = root / "exclusions.json"
    exclusions = json.loads(exclusions_path.read_text(encoding="utf-8"))
    exclusions["excluded_discovery_family_ids"] = ["BIX1-SAT"]
    _write_json(exclusions_path, exclusions)
    entry_path = root / "FREEZE_ENTRY.json"
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    entry["artifact_hashes"]["exclusions_sha256"] = _canonical_sha(exclusions)
    _write_json(entry_path, entry)

    result = check_g4_freeze(root)

    assert result.status == "NOT_FROZEN"
    assert any("discovery family exclusions" in error for error in result.errors)


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


@pytest.mark.parametrize(
    "excluded_cases",
    [
        [],
        [
            *G4_DISCOVERY_CASE_IDS,
            *G4_DISCOVERY_FAMILY_IDS,
            G4_DISCOVERY_CASE_IDS[0],
        ],
        [
            *G4_DISCOVERY_CASE_IDS,
            *G4_DISCOVERY_FAMILY_IDS,
            "UNDECLARED-EXCLUSION",
        ],
        None,
    ],
)
def test_freeze_check_requires_exact_unique_discovery_exclusions_in_seal(
    tmp_path: Path,
    excluded_cases: object,
) -> None:
    root = _complete_bundle(tmp_path)
    entry_path = root / "FREEZE_ENTRY.json"
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    if excluded_cases is None:
        entry.pop("excluded_cases")
    else:
        entry["excluded_cases"] = excluded_cases
    _write_json(entry_path, entry)

    result = check_g4_freeze(root)

    assert result.status == "NOT_FROZEN"
    assert any(
        "excluded_cases must exactly match discovery exclusions" in error
        for error in result.errors
    )


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


def test_freeze_check_rejects_absolute_manifest_paths(tmp_path: Path) -> None:
    root = _complete_bundle(tmp_path)
    manifest_path = root / "theory_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    repository_root = root.parents[2]
    manifest["files"][0]["path"] = str(
        (repository_root / "docs" / "theory" / "G4_FIXTURE.md").resolve()
    )
    _write_json(manifest_path, manifest)

    entry_path = root / "FREEZE_ENTRY.json"
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    entry["artifact_hashes"]["theory_manifest_sha256"] = _canonical_sha(manifest)
    _write_json(entry_path, entry)

    result = check_g4_freeze(root)

    assert result.status == "NOT_FROZEN"
    assert any(
        "must be a relative POSIX repository path" in error for error in result.errors
    )


def test_freeze_check_rejects_non_executable_protocol_input(tmp_path: Path) -> None:
    root = _complete_bundle(tmp_path)
    manifest_path = root / "case_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    row = manifest["cases"][0]
    case_path = root / row["path"]
    case_payload = json.loads(case_path.read_text(encoding="utf-8"))
    case_payload["input_payload"] = {
        "g4_family": row["family"],
        "protocol_input": {"legacy_prose_only": True},
    }
    _write_json(case_path, case_payload)
    row["sha256"] = _canonical_sha(case_payload)
    _write_json(manifest_path, manifest)

    entry_path = root / "FREEZE_ENTRY.json"
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    entry["case_json_sha256_by_id"][row["case_id"]] = row["sha256"]
    entry["artifact_hashes"]["case_manifest_sha256"] = _canonical_sha(manifest)
    _write_json(entry_path, entry)

    result = check_g4_freeze(root)

    assert result.status == "NOT_FROZEN"
    assert any("protocol input is not executable" in error for error in result.errors)


def test_freeze_check_rejects_des_metric_stream_applicability_drift(
    tmp_path: Path,
) -> None:
    root = _complete_bundle(tmp_path)
    metrics_path = root / "metrics_schema.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    des_metric = next(
        row
        for row in metrics["metrics"]
        if row["metric_id"] == "des_confidence_interval"
    )
    case_id = next(iter(des_metric["applicability_by_case"]))
    des_metric["applicability_by_case"][case_id] = {
        "applicable": True,
        "reason": "development mismatch",
    }
    _write_json(metrics_path, metrics)

    entry_path = root / "FREEZE_ENTRY.json"
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    entry["artifact_hashes"]["metric_schema_sha256"] = _canonical_sha(metrics)
    _write_json(entry_path, entry)

    result = check_g4_freeze(root)

    assert result.status == "NOT_FROZEN"
    assert any(
        "DES metric and random-stream applicability disagree" in error
        for error in result.errors
    )


@pytest.mark.parametrize(
    ("field", "value", "error_fragment"),
    [
        ("derivation", "ad_hoc_not_sha256", "unsupported seed derivation"),
        ("master_seeds", [11, 11], "master_seeds must be unique"),
        (
            "master_seeds",
            [11, -1],
            "master_seeds must be nonempty nonnegative integers",
        ),
    ],
)
def test_freeze_check_rejects_nonreproducible_random_stream_plans(
    tmp_path: Path,
    field: str,
    value: object,
    error_fragment: str,
) -> None:
    root = _complete_bundle(tmp_path)
    streams_path = root / "random_stream_manifest.json"
    streams = json.loads(streams_path.read_text(encoding="utf-8"))
    case_id = next(iter(streams["streams_by_case"]))
    streams["streams_by_case"][case_id] = {
        "applicable": True,
        "derivation": "sha256(master_seed:replication_index)",
        "master_seeds": [11, 17],
        "replicates": 20,
    }
    streams["streams_by_case"][case_id][field] = value
    _write_json(streams_path, streams)

    metrics_path = root / "metrics_schema.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    des_metric = next(
        row
        for row in metrics["metrics"]
        if row["metric_id"] == "des_confidence_interval"
    )
    des_metric["applicability_by_case"][case_id] = {
        "applicable": True,
        "reason": "development stream-validation fixture",
    }
    _write_json(metrics_path, metrics)

    entry_path = root / "FREEZE_ENTRY.json"
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    entry["artifact_hashes"]["random_stream_manifest_sha256"] = _canonical_sha(streams)
    entry["artifact_hashes"]["metric_schema_sha256"] = _canonical_sha(metrics)
    _write_json(entry_path, entry)

    result = check_g4_freeze(root)

    assert result.status == "NOT_FROZEN"
    assert any(error_fragment in error for error in result.errors)


def test_freeze_check_rejects_runtime_commands_that_bypass_g4_dispatch(
    tmp_path: Path,
) -> None:
    root = _complete_bundle(tmp_path)
    runtime_path = root / "runtime_lock.json"
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    runtime["commands"][-1] = "python -m ims_deadlock.cli verify-case G4-HELD-09"
    _write_json(runtime_path, runtime)

    entry_path = root / "FREEZE_ENTRY.json"
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    entry["artifact_hashes"]["runtime_lock_sha256"] = _canonical_sha(runtime)
    _write_json(entry_path, entry)

    result = check_g4_freeze(root)

    assert result.status == "NOT_FROZEN"
    assert any(
        "runtime lock commands must exactly match" in error for error in result.errors
    )


def test_freeze_check_does_not_execute_confirmation_analysis(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _complete_bundle(tmp_path)

    def forbidden(*_args: object, **_kwargs: object) -> Any:
        raise AssertionError("freeze checker executed a scientific analysis")

    monkeypatch.setattr("ims_deadlock.analysis.analyze_case", forbidden)
    monkeypatch.setattr("ims_deadlock.analysis.enumerate_stable_lts", forbidden)
    monkeypatch.setattr(
        "ims_deadlock.engine.exact_max_nonblocking_supervisor", forbidden
    )
    monkeypatch.setattr(
        "ims_deadlock.stochastic.estimate_competing_absorption",
        forbidden,
    )
    monkeypatch.setattr(
        "ims_deadlock.g4_comparators.adapted_candidate_monitor_cover",
        forbidden,
    )
    monkeypatch.setattr(
        "ims_deadlock.g4_comparators.audit_crp_evidence",
        forbidden,
    )
    monkeypatch.setattr(
        "ims_deadlock.g4_comparators.evaluate_supplied_l30_inequalities",
        forbidden,
    )
    monkeypatch.setattr(
        "ims_deadlock.g4_comparators.fixed_recorder_target_reachability",
        forbidden,
    )
    monkeypatch.setattr(
        "ims_deadlock.g4_instances.build_adversarial_boundary_case",
        forbidden,
    )
    monkeypatch.setattr(
        "ims_deadlock.g4_instances.build_bidirectional_island_case",
        forbidden,
    )
    monkeypatch.setattr(
        "ims_deadlock.g4_instances.build_medium_island_case",
        forbidden,
    )
    monkeypatch.setattr(
        "ims_deadlock.g4_instances.derive_absorbing_ctmc",
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
