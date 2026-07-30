import hashlib
import json
from pathlib import Path
from typing import Any, cast

import pytest

import ims_deadlock.g5_scoring as g5_scoring
from ims_deadlock.g4_freeze import FreezeCheckResult, check_g4_freeze
from ims_deadlock.g5_scoring import (
    _MAX_JSON_BYTES,
    ExecutionStatus,
    ScientificStatus,
    ScoringError,
    main,
    score_case,
    score_run,
)

BUNDLE_ROOT = Path("cases/confirmation/g4")


@pytest.fixture
def real_check_g4_freeze() -> None:
    """Opt out of the unit-test freeze mock for production integration checks."""


@pytest.fixture(autouse=True)
def _mock_g4_freeze_for_scorer_units(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if "real_check_g4_freeze" in request.fixturenames:
        return

    def frozen_check(_root: Path) -> FreezeCheckResult:
        return FreezeCheckResult(
            status="FROZEN",
            errors=(),
            case_ids=tuple(_supported_results()),
            artifact_hashes={},
            confirmation_results_inspected=False,
        )

    monkeypatch.setattr(g5_scoring, "check_g4_freeze", frozen_check)


def _canonical_hash(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _record(
    case_id: str,
    result: object | None,
    run_label: str,
    *,
    stdout_bytes: bytes | None = None,
    stderr_bytes: bytes = b"",
    timed_out: bool = False,
    exit_code: int | None = 0,
    argv: list[str] | None = None,
    git_head: str | None = "f9b9a5a5652c7a49053e7ef26d08911bd757f465",
    git_branch: str | None = "codex/g5-scoring-test",
) -> dict[str, object]:
    actual_stdout = stdout_bytes
    if actual_stdout is None:
        actual_stdout = (
            b"" if result is None else json.dumps(result, sort_keys=True).encode()
        )
    return {
        "schema_version": "ims-deadlock/g5-capture-record/v1",
        "case_id": case_id,
        "run_label": run_label,
        "argv": argv or ["python", "-m", "ims_deadlock.g4_protocol", "run", case_id],
        "cwd": str(Path.cwd().resolve()),
        "bundle_root": str(BUNDLE_ROOT.resolve()),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "timeout_seconds": 300.0,
        "freeze_id": "G4-FREEZE-C-20260730T051210Z",
        "freeze_status": "FROZEN",
        "git_head": git_head,
        "git_branch": git_branch,
        "stderr_raw_sha256": hashlib.sha256(stderr_bytes).hexdigest(),
        "stdout_raw_sha256": hashlib.sha256(actual_stdout).hexdigest(),
        "stdout_canonical_json_sha256": (
            None if result is None else _canonical_hash(result)
        ),
    }


def _write_run(
    capture_root: Path,
    case_id: str,
    result: dict[str, Any] | None,
    *,
    repro_result: dict[str, Any] | None = None,
    timed_out: bool = False,
    exit_code: int | None = 0,
    primary_stdout_bytes: bytes | None = None,
    repro_stdout_bytes: bytes | None = None,
    primary_stderr: bytes = b"",
    repro_stderr: bytes = b"",
    primary_record_patch: dict[str, object] | None = None,
    repro_record_patch: dict[str, object] | None = None,
) -> None:
    for run_label, payload in (
        ("primary", result),
        ("repro", result if repro_result is None else repro_result),
    ):
        run_dir = capture_root / "cases" / case_id / run_label
        run_dir.mkdir(parents=True)
        stdout_bytes = (
            primary_stdout_bytes if run_label == "primary" else repro_stdout_bytes
        )
        stderr_bytes = primary_stderr if run_label == "primary" else repro_stderr
        if payload is not None:
            raw = stdout_bytes or json.dumps(payload, sort_keys=True).encode()
            (run_dir / "stdout.json").write_bytes(raw)
        else:
            raw = stdout_bytes or b""
            (run_dir / "stdout.bin").write_bytes(raw)
        (run_dir / "stderr.txt").write_bytes(stderr_bytes)
        record = _record(
            case_id,
            payload,
            run_label,
            stdout_bytes=raw,
            stderr_bytes=stderr_bytes,
            timed_out=timed_out,
            exit_code=exit_code,
        )
        patch = primary_record_patch if run_label == "primary" else repro_record_patch
        record.update(patch or {})
        (run_dir / "record.json").write_text(
            json.dumps(record, sort_keys=True), encoding="utf-8"
        )


def _score_by_case(summary: dict[str, object], case_id: str) -> dict[str, Any]:
    scores = cast("list[dict[str, Any]]", summary["scores"])
    return next(score for score in scores if score["case_id"] == case_id)


def _evidence_fingerprints() -> dict[Path, str | None]:
    paths = sorted(Path("evidence/g5").glob("*.json"))
    for canonical in (
        Path("evidence/g5/G5_RESULT_SUMMARY.json"),
        Path("evidence/g5/G5_RAW_HASH_MANIFEST.json"),
    ):
        if canonical not in paths:
            paths.append(canonical)
    return {
        path: hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        for path in paths
    }


def _base(case_id: str, family: str, classification: str) -> dict[str, Any]:
    return {
        "schema_version": "ims-deadlock/g4-protocol-result/v1",
        "case_id": case_id,
        "family": family,
        "classification": classification,
    }


def _supported_results() -> dict[str, dict[str, Any]]:
    return {
        "G4_CRP_S4PR_AGREE": _base(
            "G4_CRP_S4PR_AGREE",
            "G4-CRP-S4PR-AGREE",
            "partial_deadlock_bridge_agreement",
        )
        | {
            "evidence_profile_audit": {
                "classification": "agreement",
                "independent_target_reachable": True,
                "source_algorithm_reproduced": False,
            },
            "partial_deadlock_bridge": {
                "certificate_available": True,
                "certificate": {
                    "kernel_resources": ["r_a", "r_b"],
                    "is_minimal": True,
                },
                "certificate_resources": ["r_a", "r_b"],
                "mapped_crp_resources": ["r_b", "r_a"],
                "agrees": True,
            },
        },
        "G4_CRP_UNREACHABLE_CANDIDATE": _base(
            "G4_CRP_UNREACHABLE_CANDIDATE",
            "G4-CRP-UNREACHABLE-CANDIDATE",
            "unreachable_candidate",
        )
        | {
            "evidence_profile_audit": {
                "classification": "unreachable_candidate",
                "independent_target_reachable": False,
                "independent_witness": [],
                "source_algorithm_reproduced": False,
            }
        },
        "G4_CRP_OUTSIDE_S4PR": _base(
            "G4_CRP_OUTSIDE_S4PR",
            "G4-CRP-OUTSIDE-S4PR",
            "not_applicable",
        )
        | {
            "evidence_profile_audit": {
                "classification": "not_applicable",
                "independent_target_reachable": None,
                "source_algorithm_reproduced": False,
            },
            "outside_scope_boundary": {
                "analysis": {
                    "certificate": {
                        "available": True,
                        "certificate": {
                            "kernel_resources": ["cart_left", "reserve_a"],
                            "is_minimal": True,
                            "capacity_witnesses": [
                                {"resource_id": "cart_left"},
                                {"resource_id": "reserve_a"},
                            ],
                        },
                    },
                    "wait_graph": {"edges": _adversarial_wait_edges()},
                    "simple_cycle_screen": {"screen_only": True},
                    "petri_bridge": {
                        "status": "not_applicable_no_petri_subclass_mapping"
                    },
                }
            },
        },
        "G4_RECORDER_TARGET_QUANTIFICATION": _base(
            "G4_RECORDER_TARGET_QUANTIFICATION",
            "G4-RECORDER-TARGET-QUANTIFICATION",
            "fixed_recorder_target_audit",
        )
        | {
            "original_target_reachable": True,
            "fixed_target_reachable": True,
            "shortest_original_witness": ["ordinary"],
            "shortest_fixed_witness": ["fixed"],
            "source_algorithm_reproduced": False,
        },
        "G4_L30_RESOURCE_BASELINE": _base(
            "G4_L30_RESOURCE_BASELINE",
            "G4-L30-RESOURCE-BASELINE",
            "sufficient_conditions_satisfied",
        )
        | {
            "applicable": True,
            "sufficient_conditions_satisfied": True,
            "evaluations": [{"satisfied": True}, {"satisfied": True}],
            "exact_ims_threshold_claimed": False,
            "source_algorithm_reproduced": False,
        },
        "G4_B05_SUPERVISOR_COMPARATOR": _base(
            "G4_B05_SUPERVISOR_COMPARATOR",
            "G4-B05-SUPERVISOR-COMPARATOR",
            "optimal_over_supplied_candidates",
        )
        | {
            "selected_monitor_ids": ["m_beta", "m_alpha"],
            "minimum_cardinality": 2,
            "all_bad_states_covered": True,
            "all_legal_states_preserved": True,
            "source_algorithm_reproduced": False,
            "optimality_scope": "supplied_candidate_monitor_set",
            "exact_supervisor_baseline": {
                "safe_states": ["l0"],
                "coaccessible_states": ["l0"],
                "disabled_state_events": [],
                "initial_state_feasible": True,
            },
        },
        "G4_IMS_PARAMETER_GRID": _base(
            "G4_IMS_PARAMETER_GRID",
            "G4-IMS-PARAMETER-GRID",
            "grid_executed",
        )
        | {
            "cells": [
                _grid_cell(cell_id, available=(index >= 3))
                for index, cell_id in enumerate(
                    [
                        "G01_FWD_DAG",
                        "G02_REV_DAG",
                        "G03_BALANCED_TIGHT",
                        "G04_BALANCED_AGV2",
                        "G05_BALANCED_BUFFER2",
                        "G06_BALANCED_MACHINE2",
                        "G07_BALANCED_LOW_WIP",
                        "G08_FORWARD_SKEW",
                        "G09_FAST_RELEASE",
                        "G10_SLOW_TRANSFER",
                    ],
                    start=1,
                )
            ]
        },
        "G4_MEDIUM_ISLAND_REBUILD": _base(
            "G4_MEDIUM_ISLAND_REBUILD",
            "G4-MEDIUM-ISLAND-REBUILD",
            "medium_instance_executed",
        )
        | {
            "analysis": _analysis(available=True, resources=["agv"], minimal=True),
            "quantitative": _quantitative("s0"),
            "ctmc_initial_state": "s0",
            "des_crosscheck": {
                "replicate_stream_count": 3,
                "rows": [
                    _des_row(1778454307, sample_count=4000),
                    _des_row(1778454308, sample_count=4000),
                    _des_row(1778454309, sample_count=4000),
                ],
            },
        },
        "G4_ADVERSARIAL_BOUNDARY": _base(
            "G4_ADVERSARIAL_BOUNDARY",
            "G4-ADVERSARIAL-BOUNDARY",
            "adversarial_boundary_executed",
        )
        | {
            "analysis": _analysis(
                available=True,
                resources=["cart_left", "reserve_a"],
                minimal=True,
                alternatives=[0, 1],
            )
        },
    }


def test_production_rejects_current_not_frozen_g4_bundle(
    tmp_path: Path,
    real_check_g4_freeze: None,
) -> None:
    real_freeze = check_g4_freeze(BUNDLE_ROOT)
    assert real_freeze.status == "NOT_FROZEN"

    result = _supported_results()["G4_CRP_S4PR_AGREE"]
    with pytest.raises(ScoringError, match="FROZEN G4 bundle"):
        score_case(BUNDLE_ROOT, result, _record("G4_CRP_S4PR_AGREE", result, "primary"))

    capture_root = tmp_path / "capture"
    for case_id, payload in _supported_results().items():
        _write_run(capture_root, case_id, payload)
    with pytest.raises(ScoringError, match="FROZEN G4 bundle"):
        score_run(BUNDLE_ROOT, capture_root)


def _grid_cell(cell_id: str, *, available: bool) -> dict[str, Any]:
    return {
        "cell_id": cell_id,
        "analysis": _analysis(available=available, resources=["AGV_0"], minimal=True),
        "ctmc_initial_state": f"{cell_id}_initial",
        "quantitative": _quantitative(f"{cell_id}_initial"),
        "des_crosscheck": {
            "replicate_stream_count": 3,
            "rows": [_des_row(740091623), _des_row(740091624), _des_row(740091625)],
        },
    }


def _quantitative(initial_state: str) -> dict[str, Any]:
    return {
        "case_derived": True,
        "generator_provenance": "derived_from_locked_g4_ims_lts",
        "deadlock_probability": {initial_state: 0.5},
        "mean_absorption_time": {initial_state: 4.0},
        "committor_residual_inf_norm": 0.0,
        "mean_time_residual_inf_norm": 0.0,
        "probability_bounds": {"min": 0.0, "max": 1.0},
        "probability_bounds_valid": True,
    }


def _des_row(seed: int, *, sample_count: int = 2000) -> dict[str, Any]:
    return {
        "master_seed": seed,
        "sample_count": sample_count,
        "deadlock_count": sample_count // 2,
        "deadlock_estimate": 0.5,
        "wilson_95_ci": [0.47, 0.53],
        "mean_absorption_time": 4.1,
        "stream_manifest": {
            "master_seed": seed,
            "sample_count": sample_count,
            "seed_derivation": "sha256(master_seed:replication_index)",
        },
    }


def _analysis(
    *,
    available: bool,
    resources: list[str],
    minimal: bool,
    alternatives: list[int] | None = None,
) -> dict[str, Any]:
    return {
        "lts": {"truncated": False},
        "certificate": {
            "available": available,
            "certificate": (
                {
                    "kernel_resources": resources,
                    "is_minimal": minimal,
                    "capacity_witnesses": [
                        {"resource_id": resource_id} for resource_id in resources
                    ],
                }
                if available
                else None
            ),
        },
        "wait_graph": {
            "edges": _adversarial_wait_edges()
            if alternatives is not None
            else [{"kind": "request", "alternative_index": index} for index in [0]]
        },
        "simple_cycle_screen": {"screen_only": True},
        "petri_bridge": {"status": "not_applicable_no_petri_subclass_mapping"},
    }


def _adversarial_wait_edges() -> list[dict[str, object]]:
    return [
        {
            "kind": "request",
            "source": "job:gate",
            "target": "resource:reserve_a",
            "alternative_index": 0,
        },
        {
            "kind": "request",
            "source": "job:gate",
            "target": "resource:reserve_b",
            "alternative_index": 0,
        },
        {
            "kind": "request",
            "source": "job:left",
            "target": "resource:fixture_b",
            "alternative_index": 0,
        },
        {
            "kind": "request",
            "source": "job:left",
            "target": "resource:cart_right",
            "alternative_index": 0,
        },
        {
            "kind": "request",
            "source": "job:left",
            "target": "resource:inspection",
            "alternative_index": 1,
        },
        {
            "kind": "request",
            "source": "job:left",
            "target": "resource:reserve_b",
            "alternative_index": 1,
        },
        {
            "kind": "request",
            "source": "job:right",
            "target": "resource:fixture_a",
            "alternative_index": 0,
        },
        {
            "kind": "request",
            "source": "job:right",
            "target": "resource:cart_left",
            "alternative_index": 0,
        },
        {
            "kind": "request",
            "source": "job:right",
            "target": "resource:inspection",
            "alternative_index": 1,
        },
        {
            "kind": "request",
            "source": "job:right",
            "target": "resource:reserve_a",
            "alternative_index": 1,
        },
    ]


def test_score_case_supports_not_applicable_and_unreachable_negative_rows() -> None:
    results = _supported_results()

    outside = score_case(
        BUNDLE_ROOT,
        results["G4_CRP_OUTSIDE_S4PR"],
        _record("G4_CRP_OUTSIDE_S4PR", results["G4_CRP_OUTSIDE_S4PR"], "primary"),
    )
    unreachable = score_case(
        BUNDLE_ROOT,
        results["G4_CRP_UNREACHABLE_CANDIDATE"],
        _record(
            "G4_CRP_UNREACHABLE_CANDIDATE",
            results["G4_CRP_UNREACHABLE_CANDIDATE"],
            "primary",
        ),
    )

    assert outside.execution_status is ExecutionStatus.COMPLETED
    assert outside.scientific_status is ScientificStatus.SUPPORTED
    assert unreachable.scientific_status is ScientificStatus.SUPPORTED
    assert outside.to_json_dict()["scientific_status"] == "SUPPORTED"


def test_score_case_missing_result_fields_are_invalid_not_fatal() -> None:
    result = {"schema_version": "ims-deadlock/g4-protocol-result/v1"}

    score = score_case(
        BUNDLE_ROOT,
        result,
        _record("G4_CRP_UNREACHABLE_CANDIDATE", result, "primary"),
    )

    assert score.execution_status is ExecutionStatus.INVALID_RESULT
    assert score.scientific_status is ScientificStatus.INCONCLUSIVE
    assert "result_schema" in score.failure_categories


def test_score_case_falsifies_scientific_mismatch_without_execution_failure() -> None:
    result = _supported_results()["G4_B05_SUPERVISOR_COMPARATOR"] | {
        "selected_monitor_ids": ["m_gamma"],
    }

    score = score_case(
        BUNDLE_ROOT,
        result,
        _record("G4_B05_SUPERVISOR_COMPARATOR", result, "primary"),
    )

    assert score.execution_status is ExecutionStatus.COMPLETED
    assert score.scientific_status is ScientificStatus.FALSIFIED
    assert "scientific_falsification" in score.failure_categories


def test_b05_source_algorithm_nonclaim_must_be_false() -> None:
    result = _supported_results()["G4_B05_SUPERVISOR_COMPARATOR"] | {
        "source_algorithm_reproduced": True,
    }

    score = score_case(
        BUNDLE_ROOT,
        result,
        _record("G4_B05_SUPERVISOR_COMPARATOR", result, "primary"),
    )

    assert score.scientific_status is ScientificStatus.FALSIFIED
    assert any("source algorithm" in reason for reason in score.reasons)


def test_b05_exact_real_output_shape_is_supported() -> None:
    result = _supported_results()["G4_B05_SUPERVISOR_COMPARATOR"]

    score = score_case(
        BUNDLE_ROOT,
        result,
        _record("G4_B05_SUPERVISOR_COMPARATOR", result, "primary"),
    )

    assert score.scientific_status is ScientificStatus.SUPPORTED


def test_adversarial_static_missing_or_and_edges_falsifies() -> None:
    result = _supported_results()["G4_ADVERSARIAL_BOUNDARY"]
    bad_analysis = dict(result["analysis"])
    bad_analysis["wait_graph"] = {
        "edges": [{"kind": "request", "alternative_index": 0}]
    }
    bad = result | {"analysis": bad_analysis}

    score = score_case(
        BUNDLE_ROOT,
        bad,
        _record("G4_ADVERSARIAL_BOUNDARY", bad, "primary"),
    )

    assert score.scientific_status is ScientificStatus.FALSIFIED
    assert any(
        "OR alternatives" in reason or "AND demand" in reason
        for reason in score.reasons
    )


@pytest.mark.parametrize(
    ("case_id", "analysis_path"),
    [
        ("G4_ADVERSARIAL_BOUNDARY", ("analysis",)),
        ("G4_CRP_OUTSIDE_S4PR", ("outside_scope_boundary", "analysis")),
    ],
)
def test_boundary_nonminimal_certificate_fails_metric_not_theorem(
    case_id: str,
    analysis_path: tuple[str, ...],
) -> None:
    result = json.loads(json.dumps(_supported_results()[case_id]))
    analysis = result
    for key in analysis_path:
        analysis = analysis[key]
    analysis["certificate"]["certificate"]["is_minimal"] = False

    score = score_case(BUNDLE_ROOT, result, _record(case_id, result, "primary"))
    payload = score.to_json_dict()

    assert score.scientific_status is ScientificStatus.SUPPORTED
    assert score.supported is True
    assert payload["scientific_status"] == "SUPPORTED"
    assert payload["supported"] is True
    assert payload["theorem_prediction_status"] == "SUPPORTED"
    assert payload["theorem_supported"] is True
    metric_results = cast("dict[str, Any]", payload["metric_results"])
    assert metric_results["certificate_minimality"] == {
        "applicable": True,
        "status": "FAIL",
        "value": False,
        "evidence_field": ".".join(
            (*analysis_path, "certificate", "certificate", "is_minimal")
        ),
    }


def test_score_case_nested_schema_error_is_invalid_not_exception() -> None:
    result = _supported_results()["G4_CRP_UNREACHABLE_CANDIDATE"]
    bad = result | {
        "evidence_profile_audit": {
            "classification": "unreachable_candidate",
            "independent_target_reachable": False,
            "independent_witness": "not-a-list",
        }
    }

    score = score_case(
        BUNDLE_ROOT,
        bad,
        _record("G4_CRP_UNREACHABLE_CANDIDATE", bad, "primary"),
    )

    assert score.execution_status is ExecutionStatus.INVALID_RESULT
    assert score.scientific_status is ScientificStatus.INCONCLUSIVE


def test_score_run_requires_all_nine_cases_and_matching_capture_hashes(
    tmp_path: Path,
) -> None:
    capture_root = tmp_path / "capture"
    for case_id, result in _supported_results().items():
        _write_run(capture_root, case_id, result)

    summary = score_run(BUNDLE_ROOT, capture_root)
    scores = cast("list[dict[str, Any]]", summary["scores"])

    assert summary["schema_version"] == "ims-deadlock/g5-scoring-run/v1"
    assert summary["case_count"] == 9
    assert summary["scientific_status_counts"] == {"SUPPORTED": 9}
    assert summary["execution_status_counts"] == {"COMPLETED": 9}
    assert summary["supported"] is True
    grid_score = next(
        score for score in scores if score["case_id"] == "G4_IMS_PARAMETER_GRID"
    )
    assert grid_score["raw_stdout_sha256"]["primary"]
    assert grid_score["stderr_raw_sha256"]["primary"]
    assert grid_score["reproducibility"]["match"] is True
    assert (
        grid_score["frozen_metric_applicability"]["exact_deadlock_probability"][
            "applicable"
        ]
        is True
    )
    assert grid_score["observations"]["cells"][0]["exact_probability"] == 0.5
    assert (
        grid_score["observations"]["cells"][0]["des_rows"][0][
            "exact_probability_in_wilson_95_ci"
        ]
        is True
    )

    tampered = _supported_results()["G4_CRP_S4PR_AGREE"] | {
        "classification": "partial_deadlock_bridge_disagreement"
    }
    _write_run(tmp_path / "bad-capture", "G4_CRP_S4PR_AGREE", tampered)
    with pytest.raises(ScoringError, match="exactly nine"):
        score_run(BUNDLE_ROOT, tmp_path / "bad-capture")

    bad_hash_root = tmp_path / "bad-hash"
    for case_id, result in _supported_results().items():
        repro = (
            result | {"classification": "changed"}
            if case_id == "G4_CRP_S4PR_AGREE"
            else None
        )
        _write_run(bad_hash_root, case_id, result, repro_result=repro)
    bad_summary = score_run(BUNDLE_ROOT, bad_hash_root)
    bad_scores = cast("list[dict[str, Any]]", bad_summary["scores"])
    bad_score = next(
        score for score in bad_scores if score["case_id"] == "G4_CRP_S4PR_AGREE"
    )
    assert bad_score["execution_status"] == "INVALID_RESULT"
    assert bad_score["reproducibility"]["canonical_json_match"] is False


def test_score_run_preserves_boundary_nonminimal_metric_failures(
    tmp_path: Path,
) -> None:
    capture_root = tmp_path / "capture"
    for case_id, result in _supported_results().items():
        payload = json.loads(json.dumps(result))
        if case_id == "G4_ADVERSARIAL_BOUNDARY":
            payload["analysis"]["certificate"]["certificate"]["is_minimal"] = False
        elif case_id == "G4_CRP_OUTSIDE_S4PR":
            payload["outside_scope_boundary"]["analysis"]["certificate"]["certificate"][
                "is_minimal"
            ] = False
        _write_run(capture_root, case_id, payload)

    summary = score_run(BUNDLE_ROOT, capture_root)

    assert summary["scientific_status_counts"] == {"SUPPORTED": 9}
    for case_id in ("G4_ADVERSARIAL_BOUNDARY", "G4_CRP_OUTSIDE_S4PR"):
        score = _score_by_case(summary, case_id)
        assert score["scientific_status"] == "SUPPORTED"
        metric_results = cast("dict[str, Any]", score["metric_results"])
        assert metric_results["certificate_minimality"]["status"] == "FAIL"
        assert metric_results["certificate_minimality"]["value"] is False


def test_score_run_preserves_timeout_and_nonzero_without_stdout_json(
    tmp_path: Path,
) -> None:
    capture_root = tmp_path / "capture"
    for case_id, result in _supported_results().items():
        if case_id == "G4_CRP_UNREACHABLE_CANDIDATE":
            _write_run(
                capture_root,
                case_id,
                None,
                timed_out=True,
                exit_code=None,
                primary_stderr=b"terminated",
                repro_stderr=b"terminated",
            )
        elif case_id == "G4_L30_RESOURCE_BASELINE":
            _write_run(
                capture_root,
                case_id,
                None,
                exit_code=2,
                primary_stderr=b"failed",
                repro_stderr=b"failed",
            )
        else:
            _write_run(capture_root, case_id, result)

    summary = score_run(BUNDLE_ROOT, capture_root)
    scores = cast("list[dict[str, Any]]", summary["scores"])
    execution_counts = cast("dict[str, int]", summary["execution_status_counts"])

    assert execution_counts["TIMED_OUT"] == 1
    assert execution_counts["NONZERO_EXIT"] == 1
    timeout_score = next(
        score for score in scores if score["case_id"] == "G4_CRP_UNREACHABLE_CANDIDATE"
    )
    assert timeout_score["scientific_status"] == "INCONCLUSIVE"
    assert timeout_score["raw_stdout_sha256"]["primary"]


@pytest.mark.parametrize(
    ("primary_patch", "expected_status"),
    [
        ({"timed_out": True, "exit_code": None}, "TIMED_OUT"),
        ({"exit_code": 2}, "NONZERO_EXIT"),
    ],
)
def test_score_run_primary_failure_records_execution_mismatch(
    tmp_path: Path,
    primary_patch: dict[str, object],
    expected_status: str,
) -> None:
    capture_root = tmp_path / "capture"
    for case_id, result in _supported_results().items():
        _write_run(
            capture_root,
            case_id,
            None if case_id == "G4_CRP_UNREACHABLE_CANDIDATE" else result,
            primary_record_patch=(
                primary_patch if case_id == "G4_CRP_UNREACHABLE_CANDIDATE" else None
            ),
        )

    score = _score_by_case(
        score_run(BUNDLE_ROOT, capture_root),
        "G4_CRP_UNREACHABLE_CANDIDATE",
    )

    assert score["execution_status"] == expected_status
    assert score["reproducibility"]["execution_status_match"] is False
    assert score["reproducibility"]["match"] is False
    assert any(
        "primary execution status" in reason and "repro execution status" in reason
        for reason in score["reasons"]
    )


def test_score_run_reports_raw_stdout_and_stderr_mismatch_per_case(
    tmp_path: Path,
) -> None:
    capture_root = tmp_path / "capture"
    for case_id, result in _supported_results().items():
        if case_id == "G4_CRP_S4PR_AGREE":
            _write_run(
                capture_root,
                case_id,
                result,
                primary_stdout_bytes=b'{"a":1,"b":2}',
                repro_stdout_bytes=b'{ "b": 2, "a": 1 }',
            )
        elif case_id == "G4_L30_RESOURCE_BASELINE":
            _write_run(
                capture_root,
                case_id,
                result,
                primary_stderr=b"note-a",
                repro_stderr=b"note-b",
            )
        else:
            _write_run(capture_root, case_id, result)

    summary = score_run(BUNDLE_ROOT, capture_root)
    scores = cast("list[dict[str, Any]]", summary["scores"])

    raw_score = next(
        score for score in scores if score["case_id"] == "G4_CRP_S4PR_AGREE"
    )
    stderr_score = next(
        score for score in scores if score["case_id"] == "G4_L30_RESOURCE_BASELINE"
    )
    assert raw_score["reproducibility"]["raw_stdout_match"] is False
    assert raw_score["reproducibility"]["canonical_json_match"] is True
    assert stderr_score["reproducibility"]["stderr_match"] is False
    assert stderr_score["execution_status"] == "INVALID_RESULT"


@pytest.mark.parametrize(
    ("case_id", "primary_patch", "expected_status"),
    [
        ("G4_CRP_S4PR_AGREE", None, "INVALID_RESULT"),
        ("G4_CRP_UNREACHABLE_CANDIDATE", {"exit_code": 2}, "NONZERO_EXIT"),
    ],
)
def test_score_run_rejects_ambiguous_stdout_json_and_bin(
    tmp_path: Path,
    case_id: str,
    primary_patch: dict[str, object] | None,
    expected_status: str,
) -> None:
    capture_root = tmp_path / "capture"
    for supported_case_id, result in _supported_results().items():
        _write_run(
            capture_root,
            supported_case_id,
            result,
            primary_record_patch=(
                primary_patch if supported_case_id == case_id else None
            ),
        )
    primary_dir = capture_root / "cases" / case_id / "primary"
    (primary_dir / "stdout.bin").write_bytes(b"ambiguous raw stdout")

    score = _score_by_case(score_run(BUNDLE_ROOT, capture_root), case_id)

    assert score["execution_status"] == expected_status
    assert score["scientific_status"] == "INCONCLUSIVE"
    assert any(
        "both stdout.json and stdout.bin" in reason for reason in score["reasons"]
    )


@pytest.mark.parametrize(
    ("patch", "reason_fragment"),
    [
        ({"exit_code": 2}, "repro execution status is NONZERO_EXIT"),
        ({"timed_out": True, "exit_code": None}, "repro execution status is TIMED_OUT"),
        (
            {"launch_error": "failed to spawn subprocess"},
            "repro execution status is INVALID_RESULT",
        ),
    ],
)
def test_score_run_requires_repro_capture_completed(
    tmp_path: Path,
    patch: dict[str, object],
    reason_fragment: str,
) -> None:
    capture_root = tmp_path / "capture"
    for case_id, result in _supported_results().items():
        _write_run(
            capture_root,
            case_id,
            result,
            repro_record_patch=patch if case_id == "G4_CRP_S4PR_AGREE" else None,
        )

    score = _score_by_case(score_run(BUNDLE_ROOT, capture_root), "G4_CRP_S4PR_AGREE")

    assert score["execution_status"] == "INVALID_RESULT"
    assert score["scientific_status"] == "INCONCLUSIVE"
    assert score["reproducibility"]["match"] is False
    assert any(reason_fragment in reason for reason in score["reasons"])


@pytest.mark.parametrize(
    ("field_path", "reason_fragment"),
    [
        (
            ("quantitative", "deadlock_probability", "{initial_state}"),
            "exact p is not a finite probability",
        ),
        (
            ("quantitative", "mean_absorption_time", "{initial_state}"),
            "mean time is not finite nonnegative",
        ),
        (
            ("quantitative", "committor_residual_inf_norm"),
            "committor_residual_inf_norm is not finite nonnegative",
        ),
        (("des", "master_seed"), "seed is invalid"),
        (("des", "sample_count"), "replicate count is not frozen"),
        (("des", "deadlock_count"), "invalid deadlock_count"),
        (("des", "deadlock_estimate"), "invalid deadlock_estimate"),
        (("des", "mean_absorption_time"), "invalid mean_absorption_time"),
        (("des", "wilson_95_ci", 0), "Wilson interval is invalid"),
        (("des_manifest", "master_seed"), "stream manifest seed mismatch"),
        (("des_manifest", "sample_count"), "stream manifest sample mismatch"),
    ],
)
def test_quantitative_and_des_bool_pollution_falsifies(
    field_path: tuple[object, ...],
    reason_fragment: str,
) -> None:
    result = _supported_results()["G4_MEDIUM_ISLAND_REBUILD"]
    polluted = json.loads(json.dumps(result))
    if field_path[0] == "quantitative":
        initial_state = polluted["ctmc_initial_state"]
        key_path = [
            initial_state if item == "{initial_state}" else item
            for item in field_path[1:]
        ]
        target = polluted
        for key in ("quantitative", *key_path[:-1]):
            target = target[key]
        target[key_path[-1]] = True
    else:
        row = polluted["des_crosscheck"]["rows"][0]
        if field_path[0] == "des_manifest":
            row = row["stream_manifest"]
        target = row
        for key in field_path[1:-1]:
            target = target[key]
        target[field_path[-1]] = True

    score = score_case(
        BUNDLE_ROOT,
        polluted,
        _record("G4_MEDIUM_ISLAND_REBUILD", polluted, "primary"),
    )

    assert score.scientific_status is ScientificStatus.FALSIFIED
    assert any(reason_fragment in reason for reason in score.reasons)


def test_quantitative_seed_replicate_and_ci_schema_errors_falsify() -> None:
    result = _supported_results()["G4_IMS_PARAMETER_GRID"]
    cells = list(result["cells"])
    bad_cell = dict(cells[0])
    crosscheck = dict(bad_cell["des_crosscheck"])
    rows = list(crosscheck["rows"])
    bad_row = dict(rows[0])
    bad_row["master_seed"] = 999
    bad_row["wilson_95_ci"] = [0.6, 0.7]
    rows[0] = bad_row
    crosscheck["rows"] = rows
    bad_cell["des_crosscheck"] = crosscheck
    cells[0] = bad_cell
    bad = result | {"cells": cells}

    score = score_case(
        BUNDLE_ROOT,
        bad,
        _record("G4_IMS_PARAMETER_GRID", bad, "primary"),
    )

    assert score.scientific_status is ScientificStatus.FALSIFIED
    assert any("seed" in reason or "Wilson" in reason for reason in score.reasons)


def test_wilson_interval_miss_is_observed_not_falsified() -> None:
    result = _supported_results()["G4_IMS_PARAMETER_GRID"]
    cells = list(result["cells"])
    bad_cell = dict(cells[0])
    crosscheck = dict(bad_cell["des_crosscheck"])
    rows = list(crosscheck["rows"])
    row = dict(rows[0])
    row["wilson_95_ci"] = [0.6, 0.7]
    rows[0] = row
    crosscheck["rows"] = rows
    bad_cell["des_crosscheck"] = crosscheck
    cells[0] = bad_cell
    miss = result | {"cells": cells}

    score = score_case(
        BUNDLE_ROOT,
        miss,
        _record("G4_IMS_PARAMETER_GRID", miss, "primary"),
    )

    assert score.scientific_status is ScientificStatus.SUPPORTED
    observations = cast("dict[str, Any]", score.to_json_dict()["observations"])
    assert (
        observations["cells"][0]["des_rows"][0]["exact_probability_in_wilson_95_ci"]
        is False
    )


def test_oversized_json_boundary_is_rejected_without_reading_payload(
    tmp_path: Path,
) -> None:
    capture_root = tmp_path / "capture"
    for case_id, result in _supported_results().items():
        _write_run(capture_root, case_id, result)
    oversized = capture_root / "cases" / "G4_CRP_S4PR_AGREE" / "primary" / "stdout.json"
    with oversized.open("wb") as handle:
        handle.truncate(_MAX_JSON_BYTES + 1)

    with pytest.raises(ScoringError, match="exceeds JSON size limit"):
        score_run(BUNDLE_ROOT, capture_root)


def test_cli_writes_summary_and_hash_manifest_without_overwrite(tmp_path: Path) -> None:
    capture_root = tmp_path / "capture"
    for case_id, result in _supported_results().items():
        _write_run(capture_root, case_id, result)
    output = tmp_path / "outputs" / "test-summary-overwrite.json"
    hash_output = tmp_path / "outputs" / "test-hashes-overwrite.json"

    assert (
        main(
            [
                "--root",
                str(BUNDLE_ROOT),
                "--capture-root",
                str(capture_root),
                "--output",
                str(output),
                "--hash-output",
                str(hash_output),
                "--compact",
            ]
        )
        == 0
    )

    summary = json.loads(output.read_text(encoding="utf-8"))
    manifest = json.loads(hash_output.read_text(encoding="utf-8"))
    assert summary["schema_version"] == "ims-deadlock/g5-scoring-run/v1"
    assert manifest["schema_version"] == "ims-deadlock/g5-raw-hash-manifest/v1"
    assert manifest["case_count"] == 9
    assert "\n" not in output.read_text(encoding="utf-8").strip()
    with pytest.raises(ScoringError, match="already exists"):
        main(
            [
                "--root",
                str(BUNDLE_ROOT),
                "--capture-root",
                str(capture_root),
                "--output",
                str(output),
            ]
        )


def test_cli_preflights_summary_and_hash_outputs_before_writing(
    tmp_path: Path,
) -> None:
    capture_root = tmp_path / "capture"
    for case_id, result in _supported_results().items():
        _write_run(capture_root, case_id, result)
    output = tmp_path / "outputs" / "test-summary-preflight.json"
    hash_output = tmp_path / "outputs" / "test-hashes-preflight.json"
    hash_output.parent.mkdir(parents=True, exist_ok=True)
    hash_output.write_text("existing", encoding="utf-8")

    with pytest.raises(ScoringError, match="already exists"):
        main(
            [
                "--root",
                str(BUNDLE_ROOT),
                "--capture-root",
                str(capture_root),
                "--output",
                str(output),
                "--hash-output",
                str(hash_output),
            ]
        )
    assert not output.exists()
    assert hash_output.read_text(encoding="utf-8") == "existing"


def test_cli_hash_write_failure_leaves_no_new_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    capture_root = tmp_path / "capture"
    for case_id, result in _supported_results().items():
        _write_run(capture_root, case_id, result)
    output = tmp_path / "outputs" / "test-summary-atomic.json"
    hash_output = tmp_path / "outputs" / "test-hashes-atomic.json"

    original_replace = Path.replace

    def fail_hash_replace(self: Path, target: Path) -> Path:
        if target.resolve() == hash_output.resolve():
            raise OSError("simulated hash write failure")
        return original_replace(self, target)

    monkeypatch.setattr(Path, "replace", fail_hash_replace)

    with pytest.raises(ScoringError, match="cannot write output"):
        main(
            [
                "--root",
                str(BUNDLE_ROOT),
                "--capture-root",
                str(capture_root),
                "--output",
                str(output),
                "--hash-output",
                str(hash_output),
            ]
        )
    assert not output.exists()
    assert not hash_output.exists()


def test_cli_does_not_touch_tracked_repo_evidence_paths(tmp_path: Path) -> None:
    capture_root = tmp_path / "raw-capture"
    for case_id, result in _supported_results().items():
        _write_run(capture_root, case_id, result)
    before = _evidence_fingerprints()
    output_dir = tmp_path / "outputs"
    output = output_dir / "G5_RESULT_SUMMARY.json"
    hash_output = output_dir / "G5_RAW_HASH_MANIFEST.json"

    assert (
        main(
            [
                "--root",
                str(BUNDLE_ROOT),
                "--capture-root",
                str(capture_root),
                "--output",
                str(output),
                "--hash-output",
                str(hash_output),
            ]
        )
        == 0
    )

    assert output.is_file()
    assert hash_output.is_file()
    assert _evidence_fingerprints() == before


def test_nan_stdout_json_is_invalid_result_not_uncaught(tmp_path: Path) -> None:
    capture_root = tmp_path / "capture"
    for case_id, result in _supported_results().items():
        _write_run(capture_root, case_id, result)
    run_dir = capture_root / "cases" / "G4_CRP_S4PR_AGREE" / "primary"
    stdout = (
        b'{"schema_version":"ims-deadlock/g4-protocol-result/v1",'
        b'"case_id":"G4_CRP_S4PR_AGREE",'
        b'"family":"G4-CRP-S4PR-AGREE",'
        b'"classification":"partial_deadlock_bridge_agreement",'
        b'"bad":NaN}'
    )
    (run_dir / "stdout.json").write_bytes(stdout)
    record = json.loads((run_dir / "record.json").read_text(encoding="utf-8"))
    record["stdout_raw_sha256"] = hashlib.sha256(stdout).hexdigest()
    record["stdout_canonical_json_sha256"] = None
    (run_dir / "record.json").write_text(json.dumps(record), encoding="utf-8")

    summary = score_run(BUNDLE_ROOT, capture_root)
    scores = cast("list[dict[str, Any]]", summary["scores"])
    score = next(score for score in scores if score["case_id"] == "G4_CRP_S4PR_AGREE")

    assert score["execution_status"] == "INVALID_RESULT"
    assert score["scientific_status"] == "INCONCLUSIVE"


def test_cli_rejects_traversal_and_frozen_bundle_output(tmp_path: Path) -> None:
    capture_root = tmp_path / "capture"
    for case_id, result in _supported_results().items():
        _write_run(capture_root, case_id, result)

    with pytest.raises(ScoringError, match="path traversal"):
        main(
            [
                "--root",
                str(BUNDLE_ROOT),
                "--capture-root",
                str(capture_root),
                "--output",
                "../outside.json",
            ]
        )
    with pytest.raises(ScoringError, match="frozen bundle"):
        main(
            [
                "--root",
                str(BUNDLE_ROOT),
                "--capture-root",
                str(BUNDLE_ROOT),
                "--output",
                str(BUNDLE_ROOT / "summary.json"),
            ]
        )
    with pytest.raises(ScoringError, match="raw capture root"):
        main(
            [
                "--root",
                str(BUNDLE_ROOT),
                "--capture-root",
                str(capture_root),
                "--output",
                str(capture_root / "summary.json"),
            ]
        )
