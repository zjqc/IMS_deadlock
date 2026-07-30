import hashlib
import json
import platform
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

import ims_deadlock.historical_replay as replay

BUNDLE_ROOT = Path("cases/confirmation/g4")
CASE_IDS = [
    "G4_CRP_S4PR_AGREE",
    "G4_CRP_OUTSIDE_S4PR",
    "G4_ADVERSARIAL_BOUNDARY",
    "G4_IMS_PARAMETER_GRID",
    "G4_MEDIUM_ISLAND_REBUILD",
]
FREEZE_ARTIFACT_HASHES = {
    "case_manifest.json": "case-hash",
    "random_stream_manifest.json": "stream-hash",
    "runtime_lock.json": "runtime-hash",
    "metrics_schema.json": "metrics-hash",
}
EXECUTION_SCHEDULE = {
    "primary": [
        {
            "wave_id": "P1",
            "case_ids": [
                "G4_CRP_S4PR_AGREE",
                "G4_CRP_OUTSIDE_S4PR",
                "G4_ADVERSARIAL_BOUNDARY",
            ],
            "max_concurrent": 3,
        },
        {
            "wave_id": "P2",
            "case_ids": [
                "G4_IMS_PARAMETER_GRID",
                "G4_MEDIUM_ISLAND_REBUILD",
            ],
            "max_concurrent": 2,
        },
    ],
    "repro": [
        {
            "wave_id": "R1",
            "case_ids": [
                "G4_CRP_S4PR_AGREE",
                "G4_CRP_OUTSIDE_S4PR",
                "G4_ADVERSARIAL_BOUNDARY",
            ],
            "max_concurrent": 3,
        },
        {
            "wave_id": "R2",
            "case_ids": [
                "G4_IMS_PARAMETER_GRID",
                "G4_MEDIUM_ISLAND_REBUILD",
            ],
            "max_concurrent": 2,
        },
    ],
    "repro_starts_after_all_primary_complete": True,
    "same_case_overlap_allowed": False,
    "nested_scientific_parallelism_allowed": False,
}
REQUIRED_CODE_HASHES = {
    "src/ims_deadlock/historical_replay.py": "code-hash",
    "src/ims_deadlock/g4_protocol.py": "protocol-hash",
    "src/ims_deadlock/g4_instances.py": "instances-hash",
    "src/ims_deadlock/terminal_classes.py": "terminal-hash",
    "src/ims_deadlock/certificates.py": "certificates-hash",
    "src/ims_deadlock/g5_scoring.py": "scorer-hash",
    "src/ims_deadlock/engine.py": "engine-hash",
}


class _CompletedProcess:
    def __init__(
        self,
        stdout: bytes,
        stderr: bytes = b"",
        returncode: int = 0,
    ) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

    def communicate(self, timeout: float | None = None) -> tuple[bytes, bytes]:
        return self.stdout, self.stderr

    def kill(self) -> None:
        raise AssertionError("completed process should not be killed")


class _TimeoutProcess:
    returncode = -9

    def __init__(self) -> None:
        self.killed = False

    def communicate(self, timeout: float | None = None) -> tuple[bytes, bytes]:
        if not self.killed:
            raise subprocess.TimeoutExpired(
                cmd=["python", "-m", "ims_deadlock.g4_protocol"],
                timeout=timeout if timeout is not None else 0.0,
                output=b"partial-before-kill",
                stderr=b"stderr-before-kill",
            )
        return b"partial", b"terminated"

    def kill(self) -> None:
        self.killed = True


def _canonical_hash(payload: object) -> str:
    return replay.canonical_json_sha256(payload)


def _write_json(path: Path, payload: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    path.write_bytes(encoded)
    return hashlib.sha256(encoded).hexdigest()


def _file_hash(path: Path, data: bytes = b"data") -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def _freeze(
    *,
    status: str = "FROZEN",
    freeze_id: str = "G4-FREEZE-HISTORICAL",
    case_hash: str = "case-hash",
    stream_hash: str = "stream-hash",
) -> SimpleNamespace:
    return SimpleNamespace(
        status=status,
        errors=() if status == "FROZEN" else ("changed",),
        artifact_hashes={
            **FREEZE_ARTIFACT_HASHES,
            "case_manifest.json": case_hash,
            "random_stream_manifest.json": stream_hash,
        },
        case_ids=tuple(CASE_IDS),
        confirmation_results_inspected=False,
        freeze_id=freeze_id,
    )


def _base_lock(tmp_path: Path) -> dict[str, Any]:
    evidence = tmp_path / "historical-evidence"
    summary = evidence / "G5_RESULT_SUMMARY.json"
    raw = evidence / "G5_RAW_HASH_MANIFEST.json"
    execution_lock = evidence / "G5_EXECUTION_LOCK.json"
    scoring_erratum = evidence / "G5_SCORING_ERRATUM.json"
    scorer = tmp_path / "src" / "ims_deadlock" / "g5_scoring.py"
    return {
        "schema_version": replay.LOCK_SCHEMA,
        "case_ids": CASE_IDS,
        "run_labels": ["primary", "repro"],
        "study_role": "historical_replay",
        "no_confirmation_use": True,
        "retry_enabled": False,
        "third_run_allowed": False,
        "same_case_overlap_allowed": False,
        "nested_scientific_parallelism_allowed": False,
        "stale_lease_policy": "manual_incident_classification_no_auto_reap",
        "execution_schedule": json.loads(json.dumps(EXECUTION_SCHEDULE)),
        "output_root": str(tmp_path / "replay-output"),
        "historical_g4": {
            "freeze_id": "G4-FREEZE-HISTORICAL",
            "artifact_hashes": dict(FREEZE_ARTIFACT_HASHES),
        },
        "g6_code_file_hashes": dict(REQUIRED_CODE_HASHES),
        "default_estimand_spec": replay.DEFAULT_ESTIMAND_SPEC,
        "default_estimand_spec_sha256": replay.DEFAULT_ESTIMAND_SPEC_SHA256,
        "original_g5": {
            "summary_path": str(summary),
            "summary_sha256": _file_hash(summary, b"summary"),
            "raw_manifest_path": str(raw),
            "raw_manifest_sha256": _file_hash(raw, b"raw"),
            "execution_lock_path": str(execution_lock),
            "execution_lock_sha256": _file_hash(execution_lock, b"execution-lock"),
            "scoring_erratum_path": str(scoring_erratum),
            "scoring_erratum_sha256": _file_hash(scoring_erratum, b"erratum"),
            "scorer_path": str(scorer),
            "scorer_sha256": _file_hash(scorer, b"scorer"),
        },
        "runtime": {
            "python_executable": sys.executable,
            "python_version": platform.python_version(),
        },
        "caps": {
            "max_stdout_bytes": 1024,
            "max_stderr_bytes": 1024,
            "timeout_seconds": 1.0,
            "max_parallel_cases": 1,
        },
        "published_ref": "refs/heads/published-g6",
        "published_head": "HEAD1",
        "published_tree": "TREE1",
    }


def _write_lock(tmp_path: Path, payload: dict[str, Any]) -> Path:
    path = tmp_path / "lock.json"
    _write_json(path, payload)
    return path


def _schedule_state_path(lock: dict[str, Any]) -> Path:
    return Path(lock["output_root"]) / "schedule_state.json"


def _write_schedule_state(
    lock: dict[str, Any],
    *,
    active: list[dict[str, Any]] | None = None,
    completed: list[dict[str, Any]] | None = None,
) -> None:
    _write_json(
        _schedule_state_path(lock),
        {
            "schema_version": "ims-deadlock/g6-historical-replay-schedule-state/v1",
            "execution_schedule_sha256": replay.canonical_json_sha256(
                EXECUTION_SCHEDULE
            ),
            "active": active or [],
            "completed": completed or [],
            "incidents": [],
            "events": [],
        },
    )


def _completed(case_id: str, run_label: str) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "run_label": run_label,
        "wave_id": "P1" if run_label == "primary" else "R1",
        "published_head": "HEAD1",
        "published_tree": "TREE1",
        "finished_at": 1.0,
        "status": "recorded",
    }


def _active(case_id: str, run_label: str, *, wave_id: str) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "run_label": run_label,
        "wave_id": wave_id,
        "published_head": "HEAD1",
        "published_tree": "TREE1",
        "pid": 999999,
        "hostname": "host",
        "started_at": 1.0,
    }


def _patch_valid_environment(
    monkeypatch: pytest.MonkeyPatch,
    *,
    head: str = "HEAD1",
    tree: str = "TREE1",
    freeze: SimpleNamespace | None = None,
) -> None:
    monkeypatch.setattr(replay, "_current_git_head", lambda: head)
    monkeypatch.setattr(replay, "_current_git_tree", lambda: tree)
    monkeypatch.setattr(replay, "_current_git_tree_state", lambda: "clean")
    monkeypatch.setattr(
        replay,
        "_resolve_published_ref",
        lambda _ref: (head, tree),
    )
    monkeypatch.setattr(
        replay,
        "_current_g6_code_hashes",
        lambda: dict(REQUIRED_CODE_HASHES),
    )
    monkeypatch.setattr(
        replay,
        "check_g4_freeze",
        lambda _root: freeze if freeze is not None else _freeze(),
    )


def _valid_result(case_id: str) -> dict[str, Any]:
    if case_id == "G4_CRP_S4PR_AGREE":
        return {
            "schema_version": "ims-deadlock/g4-protocol-result/v1",
            "case_id": case_id,
            "family": "G4-CRP-S4PR-AGREE",
            "classification": "partial_deadlock_bridge_agreement",
            "partial_deadlock_bridge": {
                "certificate_available": True,
                "certificate_resources": ["r1"],
                "mapped_crp_resources": ["r1"],
                "matching_kernel_count": 1,
                "agrees": True,
            },
        }
    if case_id == "G4_IMS_PARAMETER_GRID":
        return {
            "schema_version": "ims-deadlock/g4-protocol-result/v1",
            "case_id": case_id,
            "family": "G4-IMS-PARAMETER-GRID",
            "classification": "grid_executed",
            "cells": [
                {
                    "cell_id": "G01_FWD_DAG",
                    "quantitative": {
                        "deadlock_probability": {"s0": 0.25},
                        "probability_bounds": {"min": 0.0, "max": 1.0},
                        "probability_bounds_valid": True,
                    },
                    "terminal_classification": _terminal_classification(["s_dead"]),
                    "estimand": _estimand("grid-estimand-1"),
                }
            ],
        }
    if case_id == "G4_MEDIUM_ISLAND_REBUILD":
        return {
            "schema_version": "ims-deadlock/g4-protocol-result/v1",
            "case_id": case_id,
            "family": "G4-MEDIUM-ISLAND-REBUILD",
            "classification": "medium_instance_executed",
            "quantitative": {
                "deadlock_probability": {"s0": 0.25},
                "probability_bounds": {"min": 0.0, "max": 1.0},
                "probability_bounds_valid": True,
            },
            "terminal_classification": _terminal_classification(["s_dead"]),
            "estimand": _estimand("medium-estimand-1"),
        }
    return {
        "schema_version": "ims-deadlock/g4-protocol-result/v1",
        "case_id": case_id,
        "family": case_id.replace("_", "-"),
        "classification": "adversarial_boundary_executed",
        "analysis": {"certificate": {"available": True}},
    }


def _terminal_classification(d_local: list[str]) -> dict[str, Any]:
    return {
        "classification_version": "ims-deadlock/g6-terminal-stopping-partition/v2",
        "classes": {
            "D_global": [],
            "D_local": d_local,
            "F": [],
            "R_livelock": [],
            "R_terminal": [],
            "P_policy": [],
            "S_T": [],
        },
        "lts_provenance_audit": {"verified": True},
        "local_bad_soundness_audit": {"verified": True},
        "hashes": {"estimand_id": "classification-estimand"},
    }


def _estimand(estimand_id: str) -> dict[str, Any]:
    return {"hashes": {"estimand_id": estimand_id}}


def _actual_freeze_id() -> str:
    payload = json.loads((BUNDLE_ROOT / "FREEZE_ENTRY.json").read_text("utf-8"))
    freeze_id = payload["freeze_id"]
    assert isinstance(freeze_id, str)
    return freeze_id


def _adversarial_boundary_result() -> dict[str, Any]:
    return {
        "schema_version": "ims-deadlock/g4-protocol-result/v1",
        "case_id": "G4_ADVERSARIAL_BOUNDARY",
        "family": "G4-ADVERSARIAL-BOUNDARY",
        "classification": "adversarial_boundary_executed",
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
            "wait_graph": {
                "edges": [
                    {
                        "source_job": "left",
                        "target_job": "right",
                        "kind": "request",
                        "resource_id": "reserve_a",
                        "alternative_index": 0,
                    },
                    {
                        "source_job": "right",
                        "target_job": "left",
                        "kind": "request",
                        "resource_id": "cart_left",
                        "alternative_index": 1,
                    },
                ],
            },
            "simple_cycle_screen": {"screen_only": True},
            "petri_bridge": {"status": "not_applicable_no_petri_subclass_mapping"},
        },
    }


def _write_run(
    output_root: Path,
    case_id: str,
    run_label: str,
    *,
    head: str = "HEAD1",
    tree: str = "TREE1",
    lock_hash: str = "lock-hash",
    result: dict[str, Any] | None = None,
    stdout_bytes: bytes | None = None,
    stderr: bytes = b"",
    exit_code: int = 0,
) -> Path:
    run_dir = output_root / "cases" / case_id / run_label
    run_dir.mkdir(parents=True, exist_ok=False)
    payload = result if result is not None else _valid_result(case_id)
    stdout = (
        stdout_bytes
        if stdout_bytes is not None
        else json.dumps(payload, sort_keys=True).encode("utf-8")
    )
    canonical_hash = None
    try:
        canonical_hash = _canonical_hash(json.loads(stdout.decode("utf-8")))
        (run_dir / "stdout.json").write_bytes(stdout)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        (run_dir / "stdout.bin").write_bytes(stdout)
    (run_dir / "stderr.txt").write_bytes(stderr)
    record = {
        "schema_version": replay.CAPTURE_RECORD_SCHEMA,
        "case_id": case_id,
        "run_label": run_label,
        "study_role": "historical_replay",
        "no_confirmation_use": True,
        "published_ref": "refs/heads/published-g6",
        "published_head": head,
        "published_tree": tree,
        "git_head": head,
        "git_tree": tree,
        "git_tree_state": "clean",
        "historical_freeze_id": "G4-FREEZE-HISTORICAL",
        "lock_sha256": lock_hash,
        "argv": [
            sys.executable,
            "-m",
            "ims_deadlock.g4_protocol",
            "--root",
            str(BUNDLE_ROOT.resolve()),
            "run",
            case_id,
        ],
        "cwd": str(Path.cwd()),
        "exit_code": exit_code,
        "timed_out": False,
        "stdout_raw_sha256": hashlib.sha256(stdout).hexdigest(),
        "stdout_canonical_json_sha256": canonical_hash,
        "stderr_raw_sha256": hashlib.sha256(stderr).hexdigest(),
        "estimand_ids": replay.extract_estimand_ids(payload),
    }
    _write_json(run_dir / "record.json", record)
    return run_dir


def _write_completed_runs(
    output_root: Path,
    case_ids: list[str],
    run_label: str,
    *,
    lock_hash: str,
) -> list[dict[str, Any]]:
    completed = []
    for case_id in case_ids:
        _write_run(output_root, case_id, run_label, lock_hash=lock_hash)
        completed.append(_completed(case_id, run_label))
    return completed


def test_validate_lock_accepts_exact_schema_and_rejects_universe_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)

    loaded = replay.validate_lock(
        lock_path,
        bundle_root=BUNDLE_ROOT,
        published_head="HEAD1",
        published_tree="TREE1",
    )

    assert loaded["case_ids"] == CASE_IDS

    bad = dict(lock)
    bad["extra"] = True
    with pytest.raises(replay.ReplayError, match="exact keys"):
        replay.validate_lock(_write_lock(tmp_path, bad), BUNDLE_ROOT, "HEAD1", "TREE1")

    bad = dict(lock)
    bad["case_ids"] = list(reversed(CASE_IDS))
    with pytest.raises(replay.ReplayError, match="case_ids"):
        replay.validate_lock(_write_lock(tmp_path, bad), BUNDLE_ROOT, "HEAD1", "TREE1")

    bad = dict(lock)
    bad["no_confirmation_use"] = 1
    with pytest.raises(replay.ReplayError, match="no_confirmation_use"):
        replay.validate_lock(_write_lock(tmp_path, bad), BUNDLE_ROOT, "HEAD1", "TREE1")


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda lock: lock.update({"output_root": "../escape"}), "path traversal"),
        (
            lambda lock: lock["historical_g4"].update({"freeze_id": "wrong"}),
            "freeze_id",
        ),
        (
            lambda lock: lock["historical_g4"]["artifact_hashes"].update(
                {"case_manifest.json": "wrong"}
            ),
            "artifact_hashes",
        ),
        (
            lambda lock: lock["runtime"].update({"python_executable": "python"}),
            "runtime",
        ),
        (lambda lock: lock["runtime"].update({"python_version": "3.11.0"}), "runtime"),
        (
            lambda lock: lock["original_g5"].update({"execution_lock_sha256": "wrong"}),
            "G5",
        ),
        (lambda lock: lock["original_g5"].update({"summary_sha256": "wrong"}), "G5"),
        (lambda lock: lock["g6_code_file_hashes"].update({"x.py": "wrong"}), "G6"),
    ],
)
def test_validate_lock_rejects_path_hash_head_and_freeze_mismatches(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutator: Any,
    message: str,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    mutator(lock)

    with pytest.raises(replay.ReplayError, match=message):
        replay.validate_lock(_write_lock(tmp_path, lock), BUNDLE_ROOT, "HEAD1", "TREE1")

    with pytest.raises(replay.ReplayError, match="published head"):
        replay.validate_lock(
            _write_lock(tmp_path, _base_lock(tmp_path)),
            BUNDLE_ROOT,
            "bad",
            "TREE1",
        )

    with pytest.raises(replay.ReplayError, match="published tree"):
        replay.validate_lock(
            _write_lock(tmp_path, _base_lock(tmp_path)),
            BUNDLE_ROOT,
            "HEAD1",
            "bad-tree",
        )


def test_validate_lock_rejects_dirty_tree_ref_and_missing_behavior_hashes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock["g6_code_file_hashes"] = {"src/ims_deadlock/historical_replay.py": "code-hash"}
    with pytest.raises(replay.ReplayError, match="behavior file hashes"):
        replay.validate_lock(_write_lock(tmp_path, lock), BUNDLE_ROOT, "HEAD1", "TREE1")

    lock = _base_lock(tmp_path)
    del lock["g6_code_file_hashes"]["src/ims_deadlock/engine.py"]
    with pytest.raises(replay.ReplayError, match="G6 code file hashes"):
        replay.validate_lock(_write_lock(tmp_path, lock), BUNDLE_ROOT, "HEAD1", "TREE1")

    _patch_valid_environment(monkeypatch, tree="TREE2")
    with pytest.raises(replay.ReplayError, match="published tree"):
        replay.validate_lock(
            _write_lock(tmp_path, _base_lock(tmp_path)),
            BUNDLE_ROOT,
            "HEAD1",
            "TREE1",
        )

    _patch_valid_environment(monkeypatch)
    monkeypatch.setattr(
        replay,
        "_resolve_published_ref",
        lambda _ref: ("OTHER", "TREE1"),
    )
    with pytest.raises(replay.ReplayError, match="published ref"):
        replay.validate_lock(
            _write_lock(tmp_path, _base_lock(tmp_path)),
            BUNDLE_ROOT,
            "HEAD1",
            "TREE1",
        )

    _patch_valid_environment(monkeypatch)
    monkeypatch.setattr(replay, "_current_git_tree_state", lambda: "dirty")
    with pytest.raises(replay.ReplayError, match="clean"):
        replay.validate_lock(
            _write_lock(tmp_path, _base_lock(tmp_path)),
            BUNDLE_ROOT,
            "HEAD1",
            "TREE1",
        )

    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    del lock["historical_g4"]["artifact_hashes"]["runtime_lock.json"]
    with pytest.raises(replay.ReplayError, match="artifact_hashes"):
        replay.validate_lock(
            _write_lock(tmp_path, lock),
            BUNDLE_ROOT,
            "HEAD1",
            "TREE1",
        )

    lock = _base_lock(tmp_path)
    lock["execution_schedule"]["primary"][0]["max_concurrent"] = 2
    with pytest.raises(replay.ReplayError, match="execution_schedule"):
        replay.validate_lock(
            _write_lock(tmp_path, lock),
            BUNDLE_ROOT,
            "HEAD1",
            "TREE1",
        )


def test_validate_lock_rejects_current_not_frozen_bundle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch, freeze=_freeze(status="NOT_FROZEN"))

    with pytest.raises(replay.ReplayError, match="FROZEN historical bundle"):
        replay.validate_lock(
            _write_lock(tmp_path, _base_lock(tmp_path)),
            BUNDLE_ROOT,
            "HEAD1",
            "TREE1",
        )


def test_validate_lock_real_current_bundle_is_not_historical_fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(replay, "_current_git_head", lambda: "HEAD1")
    monkeypatch.setattr(replay, "_current_git_tree", lambda: "TREE1")
    monkeypatch.setattr(replay, "_current_git_tree_state", lambda: "clean")
    monkeypatch.setattr(
        replay,
        "_resolve_published_ref",
        lambda _ref: ("HEAD1", "TREE1"),
    )
    monkeypatch.setattr(
        replay,
        "_current_g6_code_hashes",
        lambda: dict(REQUIRED_CODE_HASHES),
    )

    with pytest.raises(replay.ReplayError, match="FROZEN historical bundle"):
        replay.validate_lock(
            _write_lock(tmp_path, _base_lock(tmp_path)),
            BUNDLE_ROOT,
            "HEAD1",
            "TREE1",
        )


def test_capture_records_authorized_command_and_rejects_overwrite_or_third_label(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    calls: list[list[str]] = []
    stdout_bytes = json.dumps(_valid_result(CASE_IDS[0]), sort_keys=True).encode(
        "utf-8"
    )

    def fake_popen(
        argv: list[str],
        *,
        cwd: str,
        stdout: int,
        stderr: int,
        shell: bool,
    ) -> _CompletedProcess:
        calls.append(argv)
        lease = Path(lock["output_root"]) / "cases" / CASE_IDS[0] / ".capture.lock"
        lease_payload = json.loads(lease.read_text(encoding="utf-8"))
        assert lease_payload["case_id"] == CASE_IDS[0]
        assert lease_payload["run_label"] == "primary"
        assert lease_payload["published_head"] == "HEAD1"
        assert lease_payload["published_tree"] == "TREE1"
        assert isinstance(lease_payload["pid"], int)
        assert isinstance(lease_payload["hostname"], str)
        assert isinstance(lease_payload["started_at"], float)
        return _CompletedProcess(stdout_bytes)

    monkeypatch.setattr("ims_deadlock.historical_replay.subprocess.Popen", fake_popen)

    record = replay.capture(
        lock_path,
        bundle_root=BUNDLE_ROOT,
        case_id=CASE_IDS[0],
        run_label="primary",
        published_head="HEAD1",
        published_tree="TREE1",
    )

    assert calls == [
        [
            sys.executable,
            "-m",
            "ims_deadlock.g4_protocol",
            "--root",
            str(BUNDLE_ROOT.resolve()),
            "run",
            CASE_IDS[0],
        ]
    ]
    assert record["study_role"] == "historical_replay"
    assert record["no_confirmation_use"] is True
    assert record["published_head"] == "HEAD1"
    assert record["stdout_canonical_json_sha256"]
    assert not (
        Path(lock["output_root"]) / "cases" / CASE_IDS[0] / ".capture.lock"
    ).exists()
    with pytest.raises(replay.ReplayError, match="already exists"):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[0], "primary", "HEAD1", "TREE1")
    with pytest.raises(replay.ReplayError, match="run_label"):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[0], "third", "HEAD1", "TREE1")


def test_capture_preserves_failure_artifacts_for_nan_oversize_and_timeout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock["caps"]["max_stdout_bytes"] = 12
    lock_path = _write_lock(tmp_path, lock)

    monkeypatch.setattr(
        "ims_deadlock.historical_replay.subprocess.Popen",
        lambda *args, **kwargs: _CompletedProcess(b'{"bad":NaN}'),
    )
    with pytest.raises(replay.ReplayError, match="non-finite"):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[0], "primary", "HEAD1", "TREE1")
    nan_dir = Path(lock["output_root"]) / "cases" / CASE_IDS[0] / "primary"
    assert (nan_dir / "stdout.bin").is_file()
    assert (nan_dir / "record.json").is_file()

    lock = _base_lock(tmp_path)
    lock["output_root"] = str(tmp_path / "oversize-output")
    lock["caps"]["max_stdout_bytes"] = 12
    lock_path = _write_lock(tmp_path, lock)
    monkeypatch.setattr(
        "ims_deadlock.historical_replay.subprocess.Popen",
        lambda *args, **kwargs: _CompletedProcess(b"x" * 13),
    )
    with pytest.raises(replay.ReplayError, match="oversize"):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[1], "primary", "HEAD1", "TREE1")

    lock = _base_lock(tmp_path)
    lock["output_root"] = str(tmp_path / "timeout-output")
    lock_path = _write_lock(tmp_path, lock)
    calls = 0

    def timeout_popen(*args: object, **kwargs: object) -> _TimeoutProcess:
        nonlocal calls
        calls += 1
        return _TimeoutProcess()

    monkeypatch.setattr(
        "ims_deadlock.historical_replay.subprocess.Popen",
        timeout_popen,
    )
    with pytest.raises(replay.ReplayError, match="timed out"):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[2], "primary", "HEAD1", "TREE1")
    assert calls == 1
    timeout_dir = Path(lock["output_root"]) / "cases" / CASE_IDS[2] / "primary"
    timeout_record = json.loads((timeout_dir / "record.json").read_text("utf-8"))
    assert timeout_record["timed_out"] is True
    assert (timeout_dir / "stdout.bin").read_bytes() == b"partial"


@pytest.mark.parametrize(
    ("stdout_bytes", "match"),
    [
        (b"not-json", "stdout JSON decode failed"),
        (b"\xff\xfe", "stdout is not valid UTF-8"),
    ],
)
def test_capture_malformed_stdout_records_terminal_incident(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stdout_bytes: bytes,
    match: str,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    monkeypatch.setattr(
        "ims_deadlock.historical_replay.subprocess.Popen",
        lambda *args, **kwargs: _CompletedProcess(stdout_bytes),
    )

    with pytest.raises(replay.ReplayError, match=match):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[0], "primary", "HEAD1", "TREE1")

    run_dir = Path(lock["output_root"]) / "cases" / CASE_IDS[0] / "primary"
    assert (run_dir / "stdout.bin").read_bytes() == stdout_bytes
    assert not (run_dir / "stdout.json").exists()
    assert (run_dir / "record.json").is_file()
    state = json.loads(_schedule_state_path(lock).read_text(encoding="utf-8"))
    assert state["completed"] == []
    assert state["incidents"][0]["case_id"] == CASE_IDS[0]
    assert state["incidents"][0]["run_label"] == "primary"

    with pytest.raises(replay.ReplayError, match="terminal schedule incident"):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[0], "primary", "HEAD1", "TREE1")


@pytest.mark.parametrize(
    ("case_id", "payload", "match", "completed"),
    [
        (
            CASE_IDS[0],
            {**_valid_result(CASE_IDS[0]), "schema_version": "bad-schema"},
            "schema_version",
            [],
        ),
        (
            CASE_IDS[0],
            _valid_result(CASE_IDS[1]),
            "case_id",
            [],
        ),
        (
            CASE_IDS[3],
            {
                **_valid_result(CASE_IDS[3]),
                "cells": [
                    {
                        **cast(
                            list[dict[str, Any]], _valid_result(CASE_IDS[3])["cells"]
                        )[0],
                        "estimand": {"hashes": {}},
                    }
                ],
            },
            "estimand",
            CASE_IDS[:3],
        ),
    ],
)
def test_capture_valid_json_must_be_formal_success_payload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case_id: str,
    payload: dict[str, Any],
    match: str,
    completed: list[str],
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    lock["_lock_path"] = str(lock_path.resolve())
    lock_hash = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    if completed:
        _write_schedule_state(
            lock,
            completed=_write_completed_runs(
                Path(lock["output_root"]),
                completed,
                "primary",
                lock_hash=lock_hash,
            ),
        )
    stdout = json.dumps(payload, sort_keys=True).encode("utf-8")
    monkeypatch.setattr(
        "ims_deadlock.historical_replay.subprocess.Popen",
        lambda *args, **kwargs: _CompletedProcess(stdout),
    )

    with pytest.raises(replay.ReplayError, match=match):
        replay.capture(lock_path, BUNDLE_ROOT, case_id, "primary", "HEAD1", "TREE1")

    run_dir = Path(lock["output_root"]) / "cases" / case_id / "primary"
    assert (run_dir / "stdout.json").read_bytes() == stdout
    record = json.loads((run_dir / "record.json").read_text("utf-8"))
    assert record["stdout_canonical_json_sha256"]
    state = json.loads(_schedule_state_path(lock).read_text(encoding="utf-8"))
    assert state["incidents"][-1]["case_id"] == case_id
    assert state["incidents"][-1]["run_label"] == "primary"
    assert all(entry["case_id"] != case_id for entry in state["completed"])


def test_capture_rejects_duplicate_key_stderr_oversize_and_overlap_lease(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock["caps"]["max_stderr_bytes"] = 4
    lock_path = _write_lock(tmp_path, lock)

    monkeypatch.setattr(
        "ims_deadlock.historical_replay.subprocess.Popen",
        lambda *args, **kwargs: _CompletedProcess(b'{"a":1,"a":2}'),
    )
    with pytest.raises(replay.ReplayError, match="duplicate"):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[0], "primary", "HEAD1", "TREE1")

    lock = _base_lock(tmp_path)
    lock["output_root"] = str(tmp_path / "stderr-output")
    lock["caps"]["max_stderr_bytes"] = 4
    lock_path = _write_lock(tmp_path, lock)
    monkeypatch.setattr(
        "ims_deadlock.historical_replay.subprocess.Popen",
        lambda *args, **kwargs: _CompletedProcess(b"{}", b"too-long"),
    )
    with pytest.raises(replay.ReplayError, match="stderr.*oversize"):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[1], "primary", "HEAD1", "TREE1")

    lock = _base_lock(tmp_path)
    lock["output_root"] = str(tmp_path / "lease-output")
    lock_path = _write_lock(tmp_path, lock)
    lease = Path(lock["output_root"]) / "cases" / CASE_IDS[1] / ".capture.lock"
    lease.parent.mkdir(parents=True)
    stale_metadata = {
        "pid": 999999,
        "hostname": "old-host",
        "started_at": 1.0,
        "case_id": CASE_IDS[1],
        "run_label": "primary",
        "published_head": "HEAD1",
        "published_tree": "TREE1",
    }
    lease.write_text(json.dumps(stale_metadata), encoding="utf-8")
    with pytest.raises(
        replay.ReplayError,
        match=(
            "existing capture lease requires manual incident classification; "
            "automatic recovery is forbidden"
        ),
    ):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[1], "primary", "HEAD1", "TREE1")
    assert json.loads(lease.read_text(encoding="utf-8")) == stale_metadata


def test_capture_rejects_repro_before_all_primary_complete(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    lock["_lock_path"] = str(lock_path.resolve())
    lock_hash = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    _write_schedule_state(
        lock,
        completed=_write_completed_runs(
            Path(lock["output_root"]),
            [
                "G4_CRP_S4PR_AGREE",
                "G4_CRP_OUTSIDE_S4PR",
                "G4_ADVERSARIAL_BOUNDARY",
                "G4_IMS_PARAMETER_GRID",
            ],
            "primary",
            lock_hash=lock_hash,
        ),
    )
    monkeypatch.setattr(
        "ims_deadlock.historical_replay.subprocess.Popen",
        lambda *args, **kwargs: pytest.fail("repro must be refused before launch"),
    )

    with pytest.raises(replay.ReplayError, match="all primary captures complete"):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[0], "repro", "HEAD1", "TREE1")


def test_capture_rejects_wave2_before_wave1_complete(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    lock["_lock_path"] = str(lock_path.resolve())
    lock_hash = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    _write_schedule_state(
        lock,
        completed=_write_completed_runs(
            Path(lock["output_root"]),
            [
                "G4_CRP_S4PR_AGREE",
                "G4_CRP_OUTSIDE_S4PR",
            ],
            "primary",
            lock_hash=lock_hash,
        ),
    )
    monkeypatch.setattr(
        "ims_deadlock.historical_replay.subprocess.Popen",
        lambda *args, **kwargs: pytest.fail("P2 must be refused before launch"),
    )

    with pytest.raises(replay.ReplayError, match="prior wave P1 is incomplete"):
        replay.capture(
            lock_path,
            BUNDLE_ROOT,
            "G4_IMS_PARAMETER_GRID",
            "primary",
            "HEAD1",
            "TREE1",
        )


def test_capture_rejects_schedule_concurrency_and_existing_global_lock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    _write_schedule_state(
        lock,
        active=[
            _active("G4_CRP_S4PR_AGREE", "primary", wave_id="P1"),
            _active("G4_CRP_OUTSIDE_S4PR", "primary", wave_id="P1"),
            _active("G4_ADVERSARIAL_BOUNDARY", "primary", wave_id="P1"),
        ],
    )
    monkeypatch.setattr(
        "ims_deadlock.historical_replay.subprocess.Popen",
        lambda *args, **kwargs: pytest.fail("over-limit capture must not launch"),
    )

    with pytest.raises(replay.ReplayError, match="schedule concurrency limit"):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[0], "primary", "HEAD1", "TREE1")

    state_lock = Path(lock["output_root"]) / ".schedule.lock"
    state_lock.write_text("manual incident", encoding="utf-8")
    with pytest.raises(
        replay.ReplayError,
        match=(
            "existing schedule lease requires manual incident classification; "
            "automatic recovery is forbidden"
        ),
    ):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[0], "primary", "HEAD1", "TREE1")
    assert state_lock.read_text(encoding="utf-8") == "manual incident"


def test_case_lease_failure_after_schedule_admission_records_terminal_incident(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    lease = Path(lock["output_root"]) / "cases" / CASE_IDS[0] / ".capture.lock"
    lease.parent.mkdir(parents=True)
    lease.write_text("manual incident", encoding="utf-8")

    with pytest.raises(replay.ReplayError, match="existing capture lease"):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[0], "primary", "HEAD1", "TREE1")

    state = json.loads(_schedule_state_path(lock).read_text(encoding="utf-8"))
    assert state["completed"] == []
    assert state["incidents"][0]["case_id"] == CASE_IDS[0]
    assert state["incidents"][0]["run_label"] == "primary"

    with pytest.raises(replay.ReplayError, match="terminal schedule incident"):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[0], "primary", "HEAD1", "TREE1")


def test_forged_completed_schedule_without_successful_record_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    _write_schedule_state(
        lock,
        completed=[
            _completed("G4_CRP_S4PR_AGREE", "primary"),
            _completed("G4_CRP_OUTSIDE_S4PR", "primary"),
            _completed("G4_ADVERSARIAL_BOUNDARY", "primary"),
        ],
    )

    with pytest.raises(replay.ReplayError, match="successful capture record"):
        replay.capture(
            lock_path,
            BUNDLE_ROOT,
            "G4_IMS_PARAMETER_GRID",
            "primary",
            "HEAD1",
            "TREE1",
        )


@pytest.mark.parametrize(
    "forged_payload",
    [
        {**_valid_result(CASE_IDS[0]), "schema_version": "bad-schema"},
        _valid_result(CASE_IDS[1]),
        {
            **_valid_result(CASE_IDS[3]),
            "cells": [
                {
                    **cast(list[dict[str, Any]], _valid_result(CASE_IDS[3])["cells"])[
                        0
                    ],
                    "estimand": {"hashes": {}},
                }
            ],
        },
    ],
)
def test_forged_completed_schedule_with_non_formal_success_record_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    forged_payload: dict[str, Any],
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    lock["_lock_path"] = str(lock_path.resolve())
    lock_hash = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    completed = [
        _completed("G4_CRP_S4PR_AGREE", "primary"),
        _completed("G4_CRP_OUTSIDE_S4PR", "primary"),
        _completed("G4_ADVERSARIAL_BOUNDARY", "primary"),
    ]
    _write_run(
        Path(lock["output_root"]),
        "G4_CRP_S4PR_AGREE",
        "primary",
        lock_hash=lock_hash,
        result=forged_payload,
    )
    _write_run(
        Path(lock["output_root"]),
        "G4_CRP_OUTSIDE_S4PR",
        "primary",
        lock_hash=lock_hash,
    )
    _write_run(
        Path(lock["output_root"]),
        "G4_ADVERSARIAL_BOUNDARY",
        "primary",
        lock_hash=lock_hash,
    )
    _write_schedule_state(lock, completed=completed)

    with pytest.raises(replay.ReplayError, match="successful capture record"):
        replay.capture(
            lock_path,
            BUNDLE_ROOT,
            "G4_IMS_PARAMETER_GRID",
            "primary",
            "HEAD1",
            "TREE1",
        )


def test_failed_capture_records_terminal_schedule_incident_and_blocks_downstream(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    monkeypatch.setattr(
        "ims_deadlock.historical_replay.subprocess.Popen",
        lambda *args, **kwargs: _CompletedProcess(b'{"bad":NaN}'),
    )

    with pytest.raises(replay.ReplayError, match="non-finite"):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[0], "primary", "HEAD1", "TREE1")

    state = json.loads(_schedule_state_path(lock).read_text(encoding="utf-8"))
    assert state["completed"] == []
    assert state["incidents"][0]["case_id"] == CASE_IDS[0]
    assert state["incidents"][0]["run_label"] == "primary"

    with pytest.raises(replay.ReplayError, match="terminal schedule incident"):
        replay.capture(lock_path, BUNDLE_ROOT, CASE_IDS[0], "primary", "HEAD1", "TREE1")

    with pytest.raises(replay.ReplayError, match="terminal schedule incident"):
        replay.capture(
            lock_path,
            BUNDLE_ROOT,
            "G4_IMS_PARAMETER_GRID",
            "primary",
            "HEAD1",
            "TREE1",
        )


def test_schedule_admission_is_atomic_under_concurrent_wave_requests(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    lock["_lock_path"] = str(lock_path.resolve())
    lock_hash = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    _write_schedule_state(
        lock,
        completed=_write_completed_runs(
            Path(lock["output_root"]),
            [
                "G4_CRP_S4PR_AGREE",
                "G4_CRP_OUTSIDE_S4PR",
                "G4_ADVERSARIAL_BOUNDARY",
            ],
            "primary",
            lock_hash=lock_hash,
        ),
    )

    def admit(case_id: str) -> str:
        try:
            replay._acquire_schedule_slot(
                lock,
                case_id=case_id,
                run_label="primary",
                published_head="HEAD1",
                published_tree="TREE1",
            )
        except replay.ReplayError as exc:
            return str(exc)
        return "admitted"

    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(
            pool.map(
                admit,
                [
                    "G4_IMS_PARAMETER_GRID",
                    "G4_MEDIUM_ISLAND_REBUILD",
                    "G4_IMS_PARAMETER_GRID",
                ],
            )
        )

    assert results.count("admitted") == 2
    assert any(result != "admitted" for result in results)


def test_compare_rejects_head_estimand_hash_mismatch_and_ambiguous_stdout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    lock_hash = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    primary = _write_run(
        Path(lock["output_root"]),
        CASE_IDS[0],
        "primary",
        lock_hash=lock_hash,
    )
    repro = _write_run(
        Path(lock["output_root"]),
        CASE_IDS[0],
        "repro",
        lock_hash=lock_hash,
    )

    assert (
        replay.compare(lock_path, BUNDLE_ROOT, CASE_IDS[0], "HEAD1", "TREE1")["match"]
        is True
    )
    assert (
        replay.main(
            [
                "compare",
                "--lock",
                str(lock_path),
                "--bundle-root",
                str(BUNDLE_ROOT),
                "--published-head",
                "HEAD1",
                "--published-tree",
                "TREE1",
                "--case-id",
                CASE_IDS[0],
            ]
        )
        == 0
    )

    record_path = repro / "record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["published_head"] = "OTHER"
    _write_json(record_path, record)
    with pytest.raises(replay.ReplayError, match="published_head"):
        replay.compare(lock_path, BUNDLE_ROOT, CASE_IDS[0], "HEAD1", "TREE1")

    record["published_head"] = "HEAD1"
    record["estimand_ids"] = ["different"]
    _write_json(record_path, record)
    with pytest.raises(replay.ReplayError, match="estimand"):
        replay.compare(lock_path, BUNDLE_ROOT, CASE_IDS[0], "HEAD1", "TREE1")

    record["estimand_ids"] = replay.extract_estimand_ids(_valid_result(CASE_IDS[0]))
    _write_json(record_path, record)
    (primary / "stdout.bin").write_bytes(b"ambiguous")
    with pytest.raises(replay.ReplayError, match="both stdout.json and stdout.bin"):
        replay.compare(lock_path, BUNDLE_ROOT, CASE_IDS[0], "HEAD1", "TREE1")


def test_compare_recomputes_hashes_and_rejects_dirty_record_tree(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    lock_hash = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    primary = _write_run(
        Path(lock["output_root"]),
        CASE_IDS[0],
        "primary",
        lock_hash=lock_hash,
    )
    repro = _write_run(
        Path(lock["output_root"]),
        CASE_IDS[0],
        "repro",
        lock_hash=lock_hash,
    )

    (primary / "stdout.json").write_bytes(b'{"tampered":true}')
    with pytest.raises(replay.ReplayError, match="stdout_raw_sha256"):
        replay.compare(lock_path, BUNDLE_ROOT, CASE_IDS[0], "HEAD1", "TREE1")

    _write_json(primary / "stdout.json", _valid_result(CASE_IDS[0]))
    primary_record = json.loads((primary / "record.json").read_text(encoding="utf-8"))
    primary_record["stdout_raw_sha256"] = hashlib.sha256(
        (primary / "stdout.json").read_bytes()
    ).hexdigest()
    primary_record["stdout_canonical_json_sha256"] = _canonical_hash(
        _valid_result(CASE_IDS[0])
    )
    _write_json(primary / "record.json", primary_record)
    repro_record = json.loads((repro / "record.json").read_text(encoding="utf-8"))
    repro_record["git_tree_state"] = "dirty"
    _write_json(repro / "record.json", repro_record)
    with pytest.raises(replay.ReplayError, match="clean git tree"):
        replay.compare(lock_path, BUNDLE_ROOT, CASE_IDS[0], "HEAD1", "TREE1")


def test_summarize_rejects_missing_extra_and_writes_replay_only_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    lock_hash = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    output_root = Path(lock["output_root"])
    for case_id in CASE_IDS[:-1]:
        _write_run(output_root, case_id, "primary", lock_hash=lock_hash)
        _write_run(output_root, case_id, "repro", lock_hash=lock_hash)

    with pytest.raises(replay.ReplayError, match="exactly five"):
        replay.summarize(lock_path, BUNDLE_ROOT, "HEAD1", "TREE1")

    _write_run(output_root, CASE_IDS[-1], "primary", lock_hash=lock_hash)
    _write_run(output_root, CASE_IDS[-1], "repro", lock_hash=lock_hash)
    (output_root / "cases" / CASE_IDS[-1] / "third").mkdir()
    with pytest.raises(replay.ReplayError, match="run_labels"):
        replay.summarize(lock_path, BUNDLE_ROOT, "HEAD1", "TREE1")
    (output_root / "cases" / CASE_IDS[-1] / "third").rmdir()

    summary = replay.summarize(lock_path, BUNDLE_ROOT, "HEAD1", "TREE1")
    original_g5 = cast("dict[str, Any]", summary["original_g5"])

    assert summary["schema_version"] == replay.SUMMARY_SCHEMA
    assert summary["study_role"] == "historical_replay"
    assert summary["no_confirmation_use"] is True
    assert summary["case_count"] == 5
    assert summary["execution_schedule_sha256"] == replay.canonical_json_sha256(
        EXECUTION_SCHEDULE
    )
    assert original_g5["summary_sha256"] == lock["original_g5"]["summary_sha256"]
    by_case = {score["case_id"]: score for score in cast(list[Any], summary["scores"])}
    assert by_case["G4_IMS_PARAMETER_GRID"]["mechanism"]["status"] == "PASS"
    assert by_case["G4_MEDIUM_ISLAND_REBUILD"]["mechanism"]["status"] == "PASS"


def test_real_payload_estimands_terminal_classification_and_crp_strictness(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    grid = _valid_result("G4_IMS_PARAMETER_GRID")
    medium = _valid_result("G4_MEDIUM_ISLAND_REBUILD")

    assert replay.extract_estimand_ids(grid) == ["G01_FWD_DAG:grid-estimand-1"]
    assert replay.extract_estimand_ids(medium) == ["medium-estimand-1"]

    grid_cell = cast(list[dict[str, Any]], grid["cells"])[0]
    grid_cell["terminal_classification"] = _terminal_classification([])
    mechanism = replay._mechanism_check(
        "G4_IMS_PARAMETER_GRID",
        grid,
        {"exit_code": 0, "timed_out": False, "estimand_ids": ["x"]},
        BUNDLE_ROOT,
    )
    assert mechanism["status"] == "FAIL"


def test_boundary_score_uses_g5_capture_adapter_without_mutating_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    freeze = _freeze(freeze_id=_actual_freeze_id())
    monkeypatch.setattr(replay, "check_g4_freeze", lambda _root: freeze)
    result = _adversarial_boundary_result()
    record: dict[str, Any] = {
        "schema_version": replay.CAPTURE_RECORD_SCHEMA,
        "case_id": "G4_ADVERSARIAL_BOUNDARY",
        "run_label": "primary",
        "argv": ["python", "-m", "ims_deadlock.g4_protocol", "run"],
        "cwd": str(Path.cwd().resolve()),
        "bundle_root": str(BUNDLE_ROOT.resolve()),
        "exit_code": 0,
        "timed_out": False,
        "timeout_seconds": 1.0,
        "historical_freeze_id": _actual_freeze_id(),
        "git_head": "HEAD1",
        "git_tree": "TREE1",
        "stderr_raw_sha256": hashlib.sha256(b"").hexdigest(),
        "stdout_raw_sha256": hashlib.sha256(
            json.dumps(result, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "stdout_canonical_json_sha256": replay.canonical_json_sha256(result),
    }

    mechanism = replay._boundary_score(
        "G4_ADVERSARIAL_BOUNDARY",
        result,
        record,
        BUNDLE_ROOT,
    )

    assert record["schema_version"] == replay.CAPTURE_RECORD_SCHEMA
    assert "freeze_status" not in record
    assert mechanism["scoring_adapter_schema"] == "ims-deadlock/g5-capture-record/v1"
    assert mechanism["theorem_prediction_status"] in {"SUPPORTED", "FALSIFIED"}
    assert isinstance(mechanism["metric_results"], dict)

    crp = _valid_result("G4_CRP_S4PR_AGREE")
    bridge = cast(dict[str, Any], crp["partial_deadlock_bridge"])
    bridge["mapped_crp_resources"] = ["r1", "extra"]
    mechanism = replay._mechanism_check(
        "G4_CRP_S4PR_AGREE",
        crp,
        {"exit_code": 0, "timed_out": False, "estimand_ids": ["x"]},
        BUNDLE_ROOT,
    )
    assert mechanism["status"] == "FAIL"


def test_summarize_rejects_failed_or_noncanonical_pairs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    lock_hash = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    output_root = Path(lock["output_root"])
    for case_id in CASE_IDS:
        exit_code = 2 if case_id == CASE_IDS[0] else 0
        _write_run(
            output_root,
            case_id,
            "primary",
            lock_hash=lock_hash,
            exit_code=exit_code,
        )
        _write_run(
            output_root,
            case_id,
            "repro",
            lock_hash=lock_hash,
            exit_code=exit_code,
        )

    with pytest.raises(replay.ReplayError, match="completed canonical stdout JSON"):
        replay.summarize(lock_path, BUNDLE_ROOT, "HEAD1", "TREE1")

    output_root = tmp_path / "third-output"
    lock["output_root"] = str(output_root)
    lock_path = _write_lock(tmp_path, lock)
    lock_hash = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    for case_id in CASE_IDS:
        payload = _valid_result(case_id)
        if case_id == "G4_IMS_PARAMETER_GRID":
            cell = cast(list[dict[str, Any]], payload["cells"])[0]
            cast(dict[str, Any], cell["estimand"])["hashes"] = {}
        _write_run(output_root, case_id, "primary", lock_hash=lock_hash, result=payload)
        _write_run(output_root, case_id, "repro", lock_hash=lock_hash, result=payload)

    with pytest.raises(replay.ReplayError, match="estimand"):
        replay.summarize(lock_path, BUNDLE_ROOT, "HEAD1", "TREE1")

    output_root = tmp_path / "second-output"
    lock["output_root"] = str(output_root)
    lock_path = _write_lock(tmp_path, lock)
    lock_hash = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    for case_id in CASE_IDS:
        stdout = b"not-json" if case_id == CASE_IDS[0] else None
        _write_run(
            output_root,
            case_id,
            "primary",
            lock_hash=lock_hash,
            stdout_bytes=stdout,
        )
        _write_run(
            output_root,
            case_id,
            "repro",
            lock_hash=lock_hash,
            stdout_bytes=stdout,
        )

    with pytest.raises(replay.ReplayError, match="completed canonical stdout JSON"):
        replay.summarize(lock_path, BUNDLE_ROOT, "HEAD1", "TREE1")


def test_g5_evidence_fingerprints_unchanged_and_cli_atomic_preflight_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    before = replay.evidence_g5_fingerprints()
    lock = _base_lock(tmp_path)
    lock["case_ids"] = CASE_IDS[:-1]
    lock_path = _write_lock(tmp_path, lock)
    output = tmp_path / "summary.json"

    assert (
        replay.main(
            [
                "summarize",
                "--lock",
                str(lock_path),
                "--bundle-root",
                str(BUNDLE_ROOT),
                "--published-head",
                "HEAD1",
                "--published-tree",
                "TREE1",
                "--output",
                str(output),
            ]
        )
        == 1
    )

    assert not output.exists()
    assert replay.evidence_g5_fingerprints() == before


def test_cli_output_must_be_under_replay_root_and_no_overwrite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_environment(monkeypatch)
    lock = _base_lock(tmp_path)
    lock_path = _write_lock(tmp_path, lock)
    outside = tmp_path / "outside.json"

    assert (
        replay.main(
            [
                "validate-lock",
                "--lock",
                str(lock_path),
                "--bundle-root",
                str(BUNDLE_ROOT),
                "--published-head",
                "HEAD1",
                "--published-tree",
                "TREE1",
                "--output",
                str(outside),
            ]
        )
        == 1
    )
    assert not outside.exists()

    inside = Path(lock["output_root"]) / "reports" / "validate.json"
    inside.parent.mkdir(parents=True)
    inside.write_text("existing", encoding="utf-8")
    assert (
        replay.main(
            [
                "validate-lock",
                "--lock",
                str(lock_path),
                "--bundle-root",
                str(BUNDLE_ROOT),
                "--published-head",
                "HEAD1",
                "--published-tree",
                "TREE1",
                "--output",
                str(inside),
            ]
        )
        == 1
    )
    assert inside.read_text(encoding="utf-8") == "existing"

    binary_target = Path(lock["output_root"]) / "reports" / "stdout.bin"
    binary_target.write_bytes(b"existing")
    with pytest.raises(replay.ReplayError, match="already exists"):
        replay._write_bytes_atomic(binary_target, b"new")
    assert binary_target.read_bytes() == b"existing"
