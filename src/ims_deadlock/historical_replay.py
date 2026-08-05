"""G6 historical replay lane.

This module intentionally stays separate from G5 capture/scoring artifacts.  It
replays a fixed historical five-case subset for replay-only diagnostics and
never writes or regenerates G5 evidence files.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from ims_deadlock.ctmc import (
    PROBABILITY_ABSOLUTE_TOLERANCE,
    linear_residual_is_numerically_valid,
    probability_bounds_match_values,
    probability_interval_is_numerically_valid,
)
from ims_deadlock.g4_freeze import check_g4_freeze
from ims_deadlock.g5_scoring import G5_CAPTURE_SCHEMA, ScoringError, score_case

LOCK_SCHEMA = "ims-deadlock/g6-historical-replay-lock/v1"
G4_PROTOCOL_RESULT_SCHEMA = "ims-deadlock/g4-protocol-result/v1"
CAPTURE_RECORD_SCHEMA = "ims-deadlock/g6-historical-replay-capture/v1"
COMPARE_SCHEMA = "ims-deadlock/g6-historical-replay-compare/v1"
SUMMARY_SCHEMA = "ims-deadlock/g6-historical-replay-summary/v1"
SCHEDULE_STATE_SCHEMA = "ims-deadlock/g6-historical-replay-schedule-state/v1"
SCHEDULE_LOCK_INCIDENT_SCHEMA = (
    "ims-deadlock/g6-historical-replay-schedule-lock-incident/v1"
)
SCHEDULE_LOCK_CONTENTION_WAIT_SECONDS = 30.0
SCHEDULE_LOCK_STALE_SECONDS = 60.0
SCHEDULE_LOCK_INITIALIZATION_GRACE_SECONDS = 0.25
HISTORICAL_TERMINAL_CLASSIFICATION_V2 = "ims-deadlock/g6-terminal-stopping-partition/v2"
HISTORICAL_TERMINAL_CLASSIFICATION_V3 = "ims-deadlock/g6-terminal-stopping-partition/v3"
HISTORICAL_ABSORPTION_DOMAIN_CERTIFICATE_VERSION = (
    "ims-deadlock/g6-absorption-domain-certificate/v1"
)
HISTORICAL_ABSORPTION_DOMAIN_ALGORITHM_VERSION = (
    "finite-positive-rate-stopped-ctmc-scc-domain/v1"
)
HISTORICAL_CERTIFIED_STATUS = "certified_finite_positive_rate_stopped_ctmc"
HISTORICAL_SUPPORT_GRAPH_SEMANTICS = "complete_stopped_lts_support"
_HISTORICAL_CERTIFICATE_ASSUMPTION_FLAGS = (
    "finite_state_space_verified",
    "complete_nontruncated_lts_verified",
    "lts_generation_provenance_verified",
    "positive_finite_rate_manifest_verified",
    "selected_target_identity_verified",
    "policy_filter_identity_verified",
)
_HISTORICAL_CERTIFICATE_IDENTITY_HASHES = (
    "state_space_hash",
    "partition_hash",
    "rate_manifest_hash",
    "positive_rate_graph_hash",
    "policy_filter_hash",
    "absorption_domain_hash",
)
CASE_IDS = (
    "G4_CRP_S4PR_AGREE",
    "G4_CRP_OUTSIDE_S4PR",
    "G4_ADVERSARIAL_BOUNDARY",
    "G4_IMS_PARAMETER_GRID",
    "G4_MEDIUM_ISLAND_REBUILD",
)
RUN_LABELS = ("primary", "repro")
DEFAULT_ESTIMAND_SPEC: Mapping[str, object] = {
    "schema_version": "ims-deadlock/g6-default-estimand-spec/v1",
    "study_role": "historical_replay",
    "no_confirmation_use": True,
    "case_estimands": {
        "G4_CRP_S4PR_AGREE": ["crp_local_certificate_matching"],
        "G4_CRP_OUTSIDE_S4PR": ["theorem_prediction", "certificate_minimality"],
        "G4_ADVERSARIAL_BOUNDARY": [
            "theorem_prediction",
            "certificate_minimality",
        ],
        "G4_IMS_PARAMETER_GRID": [
            "grid_cell_deadlock_probability",
            "grid_cell_probability_bounds",
        ],
        "G4_MEDIUM_ISLAND_REBUILD": [
            "medium_deadlock_probability",
            "medium_probability_bounds",
        ],
    },
}
_LOCK_KEYS = frozenset(
    {
        "schema_version",
        "case_ids",
        "run_labels",
        "study_role",
        "no_confirmation_use",
        "retry_enabled",
        "third_run_allowed",
        "same_case_overlap_allowed",
        "nested_scientific_parallelism_allowed",
        "stale_lease_policy",
        "execution_schedule",
        "output_root",
        "historical_g4",
        "g6_code_file_hashes",
        "default_estimand_spec",
        "default_estimand_spec_sha256",
        "original_g5",
        "runtime",
        "caps",
        "published_ref",
        "published_head",
        "published_tree",
    }
)
_HISTORICAL_G4_KEYS = frozenset({"freeze_id", "artifact_hashes"})
_ORIGINAL_G5_KEYS = frozenset(
    {
        "summary_path",
        "summary_sha256",
        "raw_manifest_path",
        "raw_manifest_sha256",
        "execution_lock_path",
        "execution_lock_sha256",
        "scoring_erratum_path",
        "scoring_erratum_sha256",
        "scorer_path",
        "scorer_sha256",
    }
)
_RUNTIME_KEYS = frozenset({"python_executable", "python_version"})
_CAP_KEYS = frozenset(
    {
        "max_stdout_bytes",
        "max_stderr_bytes",
        "timeout_seconds",
        "max_parallel_cases",
    }
)
REQUIRED_BEHAVIOR_FILES = frozenset(
    {
        "src/ims_deadlock/historical_replay.py",
        "src/ims_deadlock/g4_protocol.py",
        "src/ims_deadlock/g4_instances.py",
        "src/ims_deadlock/terminal_classes.py",
        "src/ims_deadlock/certificates.py",
        "src/ims_deadlock/g5_scoring.py",
    }
)
EXPECTED_STALE_LEASE_POLICY = "manual_incident_classification_no_auto_reap"
EXPECTED_EXECUTION_SCHEDULE: Mapping[str, object] = {
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


class ReplayError(RuntimeError):
    """Raised for historical replay lock, capture, compare, or summary failures."""


@dataclass(frozen=True)
class HistoricalTerminalClassification:
    classification_version: str
    d_local_state_ids: tuple[str, ...]
    certified_s_t_state_ids: tuple[str, ...] | None


def canonical_json_sha256(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


DEFAULT_ESTIMAND_SPEC_SHA256 = canonical_json_sha256(DEFAULT_ESTIMAND_SPEC)


def validate_lock(
    lock_path: Path,
    bundle_root: Path,
    published_head: str,
    published_tree: str,
) -> dict[str, Any]:
    lock = _load_json_object(lock_path)
    if set(lock) != _LOCK_KEYS:
        raise ReplayError("lock must contain exact keys")
    if lock.get("schema_version") != LOCK_SCHEMA:
        raise ReplayError("schema_version is not the historical replay lock schema")
    if _string_list(lock.get("case_ids"), "case_ids") != list(CASE_IDS):
        raise ReplayError("case_ids must match exact G6 historical replay universe")
    if _string_list(lock.get("run_labels"), "run_labels") != list(RUN_LABELS):
        raise ReplayError("run_labels must be exactly primary/repro")
    if lock.get("study_role") != "historical_replay":
        raise ReplayError("study_role must be historical_replay")
    for field, expected in (
        ("no_confirmation_use", True),
        ("retry_enabled", False),
        ("third_run_allowed", False),
        ("same_case_overlap_allowed", False),
        ("nested_scientific_parallelism_allowed", False),
    ):
        if not isinstance(lock.get(field), bool) or lock[field] is not expected:
            raise ReplayError(f"{field} has invalid boolean value")
    if lock.get("stale_lease_policy") != EXPECTED_STALE_LEASE_POLICY:
        raise ReplayError("stale_lease_policy is not the locked manual policy")
    if lock.get("execution_schedule") != EXPECTED_EXECUTION_SCHEDULE:
        raise ReplayError("execution_schedule disagrees with locked replay schedule")
    if "commit_sha" in lock:
        raise ReplayError("lock must not self-reference a commit SHA")
    published_ref = _string(lock.get("published_ref"), "published_ref")
    if published_ref == "":
        raise ReplayError("published_ref must be a nonempty string")
    if _string(lock.get("published_head"), "published_head") != published_head:
        raise ReplayError("lock published head disagrees with CLI published head")
    if _string(lock.get("published_tree"), "published_tree") != published_tree:
        raise ReplayError("lock published tree disagrees with CLI published tree")
    if _current_git_head() != published_head:
        raise ReplayError("current git HEAD disagrees with published head")
    if _current_git_tree() != published_tree:
        raise ReplayError("current git tree disagrees with published tree")
    if _current_git_tree_state() != "clean":
        raise ReplayError("historical replay requires a clean git tree")
    ref_head, ref_tree = _resolve_published_ref(published_ref)
    if ref_head != published_head or ref_tree != published_tree:
        raise ReplayError("published ref disagrees with published head/tree")
    output_root = _safe_output_root(
        Path(_string(lock.get("output_root"), "output_root")),
        bundle_root.resolve(),
    )
    historical = _mapping(lock.get("historical_g4"), "historical_g4")
    _require_keys(historical, _HISTORICAL_G4_KEYS, "historical_g4")
    freeze = check_g4_freeze(bundle_root)
    if getattr(freeze, "status", None) != "FROZEN":
        raise ReplayError("bundle_root must be a FROZEN historical bundle")
    if _historical_freeze_id(bundle_root, freeze) != historical["freeze_id"]:
        raise ReplayError("historical freeze_id disagrees with lock")
    artifact_hashes = _string_mapping(
        getattr(freeze, "artifact_hashes", {}),
        "freeze artifact_hashes",
    )
    if _string_mapping(historical.get("artifact_hashes"), "artifact_hashes") != dict(
        artifact_hashes
    ):
        raise ReplayError("historical artifact_hashes disagree with lock")
    code_hashes = _string_mapping(
        lock.get("g6_code_file_hashes"),
        "g6_code_file_hashes",
    )
    if not REQUIRED_BEHAVIOR_FILES <= set(code_hashes):
        raise ReplayError("lock must pin all required behavior file hashes")
    if code_hashes != _current_g6_code_hashes():
        raise ReplayError("G6 code file hashes disagree with current tree")
    if lock.get("default_estimand_spec") != DEFAULT_ESTIMAND_SPEC:
        raise ReplayError("DEFAULT_ESTIMAND_SPEC payload disagrees with lock")
    if lock.get("default_estimand_spec_sha256") != DEFAULT_ESTIMAND_SPEC_SHA256:
        raise ReplayError("DEFAULT_ESTIMAND_SPEC hash disagrees with lock")
    original_g5 = _mapping(lock.get("original_g5"), "original_g5")
    _require_keys(original_g5, _ORIGINAL_G5_KEYS, "original_g5")
    for path_field, hash_field in (
        ("summary_path", "summary_sha256"),
        ("raw_manifest_path", "raw_manifest_sha256"),
        ("execution_lock_path", "execution_lock_sha256"),
        ("scoring_erratum_path", "scoring_erratum_sha256"),
        ("scorer_path", "scorer_sha256"),
    ):
        actual = _sha256_file(Path(_string(original_g5[path_field], path_field)))
        if actual != original_g5[hash_field]:
            raise ReplayError("original G5 evidence hash disagrees with lock")
    runtime = _mapping(lock.get("runtime"), "runtime")
    _require_keys(runtime, _RUNTIME_KEYS, "runtime")
    locked_executable = os.path.normcase(
        os.path.abspath(_string(runtime.get("python_executable"), "python_executable"))
    )
    current_executable = os.path.normcase(os.path.abspath(sys.executable))
    if locked_executable != current_executable:
        raise ReplayError("runtime python_executable disagrees with current runtime")
    if (
        _string(runtime.get("python_version"), "python_version")
        != platform.python_version()
    ):
        raise ReplayError("runtime python_version disagrees with current runtime")
    caps = _mapping(lock.get("caps"), "caps")
    _require_keys(caps, _CAP_KEYS, "caps")
    if _strict_int(caps.get("max_stdout_bytes")) <= 0:
        raise ReplayError("caps.max_stdout_bytes must be positive")
    if _strict_int(caps.get("max_stderr_bytes")) <= 0:
        raise ReplayError("caps.max_stderr_bytes must be positive")
    if _strict_float(caps.get("timeout_seconds")) <= 0.0:
        raise ReplayError("caps.timeout_seconds must be positive")
    if _strict_int(caps.get("max_parallel_cases")) != 1:
        raise ReplayError("nested scientific parallelism is not allowed")
    result = dict(lock)
    result["output_root"] = str(output_root)
    result["_lock_path"] = str(lock_path.resolve())
    return result


def capture(
    lock_path: Path,
    bundle_root: Path,
    case_id: str,
    run_label: str,
    published_head: str,
    published_tree: str,
) -> dict[str, object]:
    lock = validate_lock(lock_path, bundle_root, published_head, published_tree)
    if case_id not in CASE_IDS:
        raise ReplayError("case_id is not allowed by historical replay lock")
    if run_label not in RUN_LABELS:
        raise ReplayError("run_label must be primary or repro")
    output_root = Path(_string(lock["output_root"], "output_root"))
    run_dir = output_root / "cases" / case_id / run_label
    if _schedule_pair_has_incident(lock, case_id, run_label):
        raise ReplayError("terminal schedule incident blocks recapture")
    if run_dir.exists():
        raise ReplayError(f"run directory already exists: {run_dir}")
    schedule_entry = _acquire_schedule_slot(
        lock,
        case_id=case_id,
        run_label=run_label,
        published_head=published_head,
        published_tree=published_tree,
    )
    case_lease_acquired = False
    lease = output_root / "cases" / case_id / ".capture.lock"
    success = False
    try:
        _acquire_case_lease(
            lease,
            case_id=case_id,
            run_label=run_label,
            published_head=published_head,
            published_tree=published_tree,
        )
        case_lease_acquired = True
        run_dir.mkdir(parents=True, exist_ok=False)
        argv = [
            sys.executable,
            "-m",
            "ims_deadlock.g4_protocol",
            "--root",
            str(bundle_root.resolve()),
            "run",
            case_id,
        ]
        caps = _mapping(lock["caps"], "caps")
        timeout_seconds = _strict_float(caps["timeout_seconds"])
        max_stdout_bytes = _strict_int(caps["max_stdout_bytes"])
        max_stderr_bytes = _strict_int(caps["max_stderr_bytes"])
        started = time.time()
        timed_out = False
        exit_code: int | None = None
        stdout_bytes = b""
        stderr_bytes = b""
        try:
            process = subprocess.Popen(
                argv,
                cwd=str(Path.cwd()),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
            )
            try:
                stdout_bytes, stderr_bytes = process.communicate(
                    timeout=timeout_seconds
                )
            except subprocess.TimeoutExpired:
                timed_out = True
                process.kill()
                stdout_bytes, stderr_bytes = process.communicate()
            exit_code = process.returncode
        except OSError as exc:
            stderr_bytes = str(exc).encode("utf-8")
            exit_code = None
        parse_result = _write_stdout(run_dir, stdout_bytes, max_stdout_bytes)
        stderr_error: str | None = None
        if len(stderr_bytes) > max_stderr_bytes:
            stderr_error = "stderr is oversize"
        _write_bytes_atomic(run_dir / "stderr.txt", stderr_bytes)
        record = _capture_record(
            lock=lock,
            bundle_root=bundle_root.resolve(),
            case_id=case_id,
            run_label=run_label,
            argv=argv,
            started=started,
            elapsed=time.time() - started,
            timeout_seconds=timeout_seconds,
            exit_code=exit_code,
            timed_out=timed_out,
            stdout_bytes=stdout_bytes,
            stderr_bytes=stderr_bytes,
            stdout_canonical_json_sha256=parse_result.canonical_hash,
            result_payload=parse_result.payload,
        )
        _write_json_atomic(run_dir / "record.json", record)
        if stderr_error is not None:
            raise ReplayError(stderr_error)
        if timed_out:
            raise ReplayError("historical replay capture timed out")
        if exit_code != 0:
            raise ReplayError("historical replay capture exited nonzero")
        if parse_result.error is not None:
            raise ReplayError(parse_result.error)
        success_error = _formal_success_error(
            parse_result.payload,
            case_id,
            parse_result.canonical_hash,
        )
        if success_error is not None:
            raise ReplayError(success_error)
        success = True
        return record
    finally:
        if case_lease_acquired:
            _release_case_lease(lease)
        _finish_schedule_slot(
            lock,
            schedule_entry,
            record_exists=(run_dir / "record.json").is_file(),
            success=success,
        )


def compare(
    lock_path: Path,
    bundle_root: Path,
    case_id: str,
    published_head: str,
    published_tree: str,
) -> dict[str, object]:
    lock = validate_lock(lock_path, bundle_root, published_head, published_tree)
    if case_id not in CASE_IDS:
        raise ReplayError("case_id is not allowed by historical replay lock")
    output_root = Path(_string(lock["output_root"], "output_root"))
    primary_dir = output_root / "cases" / case_id / "primary"
    repro_dir = output_root / "cases" / case_id / "repro"
    primary = _load_run(primary_dir)
    repro = _load_run(repro_dir)
    errors: list[str] = []
    for label, run in (("primary", primary), ("repro", repro)):
        if run.record.get("run_label") != label:
            errors.append(f"{label} run_label mismatch")
        if run.ambiguous_stdout:
            errors.append(f"{label} has both stdout.json and stdout.bin")
        errors.extend(
            _record_integrity_errors(label, run, lock, published_head, published_tree)
        )
    for field in (
        "schema_version",
        "case_id",
        "published_head",
        "published_tree",
        "lock_sha256",
        "argv",
        "exit_code",
        "timed_out",
        "estimand_ids",
    ):
        if primary.record.get(field) != repro.record.get(field):
            errors.append(f"primary/repro {field} mismatch")
    if primary.record.get("published_head") != published_head:
        errors.append("published_head disagrees with current invocation")
    if errors:
        raise ReplayError("; ".join(errors))
    raw_match = primary.record.get("stdout_raw_sha256") == repro.record.get(
        "stdout_raw_sha256"
    )
    canonical_match = primary.record.get(
        "stdout_canonical_json_sha256"
    ) == repro.record.get("stdout_canonical_json_sha256")
    stderr_match = primary.record.get("stderr_raw_sha256") == repro.record.get(
        "stderr_raw_sha256"
    )
    if not raw_match:
        errors.append("primary/repro stdout_raw_sha256 mismatch")
    if not canonical_match:
        errors.append("primary/repro stdout_canonical_json_sha256 mismatch")
    if not stderr_match:
        errors.append("primary/repro stderr_raw_sha256 mismatch")
    if errors:
        raise ReplayError("; ".join(errors))
    return {
        "schema_version": COMPARE_SCHEMA,
        "case_id": case_id,
        "study_role": "historical_replay",
        "no_confirmation_use": True,
        "match": raw_match and canonical_match and stderr_match,
        "raw_stdout_sha256_match": raw_match,
        "canonical_json_sha256_match": canonical_match,
        "stderr_raw_sha256_match": stderr_match,
        "raw_stdout_sha256": {
            "primary": primary.record.get("stdout_raw_sha256"),
            "repro": repro.record.get("stdout_raw_sha256"),
        },
        "canonical_json_sha256": {
            "primary": primary.record.get("stdout_canonical_json_sha256"),
            "repro": repro.record.get("stdout_canonical_json_sha256"),
        },
        "stderr_raw_sha256": {
            "primary": primary.record.get("stderr_raw_sha256"),
            "repro": repro.record.get("stderr_raw_sha256"),
        },
        "estimand_ids": primary.record.get("estimand_ids"),
    }


def summarize(
    lock_path: Path,
    bundle_root: Path,
    published_head: str,
    published_tree: str,
) -> dict[str, object]:
    lock = validate_lock(lock_path, bundle_root, published_head, published_tree)
    output_root = Path(_string(lock["output_root"], "output_root"))
    cases_root = output_root / "cases"
    if not cases_root.is_dir():
        raise ReplayError("summary requires exactly five cases")
    case_dirs = sorted(path.name for path in cases_root.iterdir() if path.is_dir())
    if len(case_dirs) != len(CASE_IDS) or set(case_dirs) != set(CASE_IDS):
        raise ReplayError("summary requires exactly five locked cases")
    scores: list[dict[str, object]] = []
    for case_id in CASE_IDS:
        case_dir = cases_root / case_id
        labels = sorted(path.name for path in case_dir.iterdir() if path.is_dir())
        if labels != list(RUN_LABELS):
            raise ReplayError("summary run_labels must be exactly primary/repro")
        comparison = compare(
            lock_path,
            bundle_root,
            case_id,
            published_head,
            published_tree,
        )
        if comparison["match"] is not True:
            raise ReplayError(f"{case_id} primary/repro comparison failed")
        primary = _load_run(case_dir / "primary")
        repro = _load_run(case_dir / "repro")
        for label, run in (("primary", primary), ("repro", repro)):
            if (
                run.record.get("exit_code") != 0
                or run.record.get("timed_out") is not False
                or run.record.get("stdout_canonical_json_sha256") in (None, "")
                or not run.record.get("estimand_ids")
                or run.payload == {}
                or _formal_success_error(
                    run.payload,
                    case_id,
                    cast(str | None, run.record.get("stdout_canonical_json_sha256")),
                )
                is not None
            ):
                raise ReplayError(
                    f"{case_id} {label} requires completed canonical stdout JSON "
                    "with estimand ids"
                )
        result = primary.payload
        mechanism = _mechanism_check(case_id, result, primary.record, bundle_root)
        scores.append(
            {
                "case_id": case_id,
                "comparison": comparison,
                "mechanism": mechanism,
            }
        )
    return {
        "schema_version": SUMMARY_SCHEMA,
        "study_role": "historical_replay",
        "no_confirmation_use": True,
        "case_count": len(scores),
        "case_ids": list(CASE_IDS),
        "original_g5": lock["original_g5"],
        "default_estimand_spec_sha256": DEFAULT_ESTIMAND_SPEC_SHA256,
        "execution_schedule_sha256": canonical_json_sha256(lock["execution_schedule"]),
        "scores": scores,
    }


def extract_estimand_ids(result: Mapping[str, object]) -> list[str]:
    case_id = result.get("case_id")
    if case_id == "G4_IMS_PARAMETER_GRID":
        cells = result.get("cells")
        if isinstance(cells, list):
            ids: list[str] = []
            for cell in cells:
                if not isinstance(cell, Mapping) or not isinstance(
                    cell.get("cell_id"), str
                ):
                    continue
                estimand_id = _estimand_id_from_payload(cell)
                if estimand_id is not None:
                    ids.append(f"{cell['cell_id']}:{estimand_id}")
            return ids
    if case_id == "G4_MEDIUM_ISLAND_REBUILD":
        estimand_id = _estimand_id_from_payload(result)
        return [] if estimand_id is None else [estimand_id]
    if case_id == "G4_CRP_S4PR_AGREE":
        return ["crp:local_certificate_matching"]
    if case_id in {"G4_CRP_OUTSIDE_S4PR", "G4_ADVERSARIAL_BOUNDARY"}:
        return ["boundary:theorem_prediction", "boundary:certificate_minimality"]
    return []


def evidence_g5_fingerprints() -> dict[str, str | None]:
    paths = sorted(Path("evidence/g5").glob("*.json"))
    for canonical in (
        Path("evidence/g5/G5_RESULT_SUMMARY.json"),
        Path("evidence/g5/G5_RAW_HASH_MANIFEST.json"),
    ):
        if canonical not in paths:
            paths.append(canonical)
    return {
        str(path): hashlib.sha256(path.read_bytes()).hexdigest()
        if path.exists()
        else None
        for path in paths
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m ims_deadlock.historical_replay")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate-lock")
    validate_parser.add_argument("--lock", type=Path, required=True)
    validate_parser.add_argument("--bundle-root", type=Path, required=True)
    validate_parser.add_argument("--published-head", required=True)
    validate_parser.add_argument("--published-tree", required=True)
    validate_parser.add_argument("--output", type=Path)
    capture_parser = subparsers.add_parser("capture")
    capture_parser.add_argument("--lock", type=Path, required=True)
    capture_parser.add_argument("--bundle-root", type=Path, required=True)
    capture_parser.add_argument("--published-head", required=True)
    capture_parser.add_argument("--published-tree", required=True)
    capture_parser.add_argument("--case-id", required=True)
    capture_parser.add_argument("--run-label", required=True)
    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--lock", type=Path, required=True)
    compare_parser.add_argument("--bundle-root", type=Path, required=True)
    compare_parser.add_argument("--published-head", required=True)
    compare_parser.add_argument("--published-tree", required=True)
    compare_parser.add_argument("--case-id", required=True)
    summarize_parser = subparsers.add_parser("summarize")
    summarize_parser.add_argument("--lock", type=Path, required=True)
    summarize_parser.add_argument("--bundle-root", type=Path, required=True)
    summarize_parser.add_argument("--published-head", required=True)
    summarize_parser.add_argument("--published-tree", required=True)
    summarize_parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    try:
        if args.command == "validate-lock":
            payload = validate_lock(
                args.lock,
                args.bundle_root,
                args.published_head,
                args.published_tree,
            )
        elif args.command == "capture":
            payload = capture(
                args.lock,
                args.bundle_root,
                args.case_id,
                args.run_label,
                args.published_head,
                args.published_tree,
            )
        elif args.command == "compare":
            payload = compare(
                args.lock,
                args.bundle_root,
                args.case_id,
                args.published_head,
                args.published_tree,
            )
        else:
            payload = summarize(
                args.lock,
                args.bundle_root,
                args.published_head,
                args.published_tree,
            )
        output = getattr(args, "output", None)
        if output is not None:
            lock = _load_json_object(args.lock)
            output_root = _safe_output_root(
                Path(_string(lock.get("output_root"), "output_root")),
                getattr(args, "bundle_root", Path.cwd()).resolve(),
            )
            _write_json_atomic(output, payload, output_root=output_root)
        else:
            print(_json_text(payload), end="")
        return 0
    except ReplayError as exc:
        print(_json_text({"error": str(exc), "schema_version": "error"}), end="")
        return 1


class _StdoutResult:
    def __init__(
        self,
        canonical_hash: str | None,
        payload: Mapping[str, object] | None,
        error: str | None,
    ) -> None:
        self.canonical_hash = canonical_hash
        self.payload = payload
        self.error = error


class _Run:
    def __init__(
        self,
        run_dir: Path,
        record: Mapping[str, object],
        payload: Mapping[str, object],
        ambiguous_stdout: bool,
    ) -> None:
        self.run_dir = run_dir
        self.record = record
        self.payload = payload
        self.ambiguous_stdout = ambiguous_stdout


def _write_stdout(
    run_dir: Path,
    stdout_bytes: bytes,
    max_stdout_bytes: int,
) -> _StdoutResult:
    if len(stdout_bytes) > max_stdout_bytes:
        _write_bytes_atomic(run_dir / "stdout.bin", stdout_bytes)
        return _StdoutResult(None, None, "stdout is oversize")
    try:
        stdout_text = stdout_bytes.decode("utf-8")
    except UnicodeDecodeError:
        _write_bytes_atomic(run_dir / "stdout.bin", stdout_bytes)
        return _StdoutResult(None, None, "stdout is not valid UTF-8")
    try:
        payload = json.loads(
            stdout_text,
            parse_constant=_reject_json_constant,
            object_pairs_hook=_no_duplicate_object,
        )
    except json.JSONDecodeError as exc:
        _write_bytes_atomic(run_dir / "stdout.bin", stdout_bytes)
        return _StdoutResult(None, None, f"stdout JSON decode failed: {exc.msg}")
    except ValueError as exc:
        _write_bytes_atomic(run_dir / "stdout.bin", stdout_bytes)
        if "non-finite" in str(exc):
            return _StdoutResult(None, None, str(exc))
        if "duplicate" in str(exc):
            return _StdoutResult(None, None, str(exc))
        return _StdoutResult(None, None, f"stdout JSON decode failed: {exc}")
    if not isinstance(payload, Mapping):
        _write_bytes_atomic(run_dir / "stdout.bin", stdout_bytes)
        return _StdoutResult(None, None, "stdout JSON must be an object")
    _reject_nonfinite_json(payload, "stdout")
    _write_bytes_atomic(run_dir / "stdout.json", stdout_bytes)
    return _StdoutResult(canonical_json_sha256(payload), payload, None)


def _formal_success_error(
    result_payload: Mapping[str, object] | None,
    case_id: str,
    canonical_hash: str | None,
) -> str | None:
    if canonical_hash in (None, ""):
        return "stdout canonical JSON hash is required for formal success"
    if result_payload is None:
        return "stdout result payload is required for formal success"
    if result_payload.get("schema_version") != G4_PROTOCOL_RESULT_SCHEMA:
        return "stdout schema_version is not the locked G4 protocol result schema"
    if result_payload.get("case_id") != case_id:
        return "stdout case_id must match requested case_id"
    if not extract_estimand_ids(result_payload):
        return "stdout result must expose estimand ids"
    return None


def _capture_record(
    *,
    lock: Mapping[str, object],
    bundle_root: Path,
    case_id: str,
    run_label: str,
    argv: list[str],
    started: float,
    elapsed: float,
    timeout_seconds: float,
    exit_code: int | None,
    timed_out: bool,
    stdout_bytes: bytes,
    stderr_bytes: bytes,
    stdout_canonical_json_sha256: str | None,
    result_payload: Mapping[str, object] | None,
) -> dict[str, object]:
    historical = _mapping(lock["historical_g4"], "historical_g4")
    return {
        "schema_version": CAPTURE_RECORD_SCHEMA,
        "case_id": case_id,
        "run_label": run_label,
        "study_role": "historical_replay",
        "no_confirmation_use": True,
        "published_ref": lock["published_ref"],
        "published_head": _current_git_head(),
        "published_tree": _current_git_tree(),
        "git_head": _current_git_head(),
        "git_tree": _current_git_tree(),
        "git_tree_state": _current_git_tree_state(),
        "historical_freeze_id": historical["freeze_id"],
        "lock_sha256": _sha256_file(Path(_string(lock["_lock_path"], "_lock_path"))),
        "bundle_root": str(bundle_root),
        "argv": argv,
        "cwd": str(Path.cwd()),
        "started_at_unix": round(started, 9),
        "elapsed_seconds": round(elapsed, 9),
        "timeout_seconds": timeout_seconds,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "stdout_raw_sha256": hashlib.sha256(stdout_bytes).hexdigest(),
        "stdout_canonical_json_sha256": stdout_canonical_json_sha256,
        "stderr_raw_sha256": hashlib.sha256(stderr_bytes).hexdigest(),
        "estimand_ids": extract_estimand_ids(result_payload or {}),
    }


def _load_run(run_dir: Path) -> _Run:
    stdout_json = run_dir / "stdout.json"
    stdout_bin = run_dir / "stdout.bin"
    ambiguous = stdout_json.exists() and stdout_bin.exists()
    record = _load_json_object(run_dir / "record.json")
    payload: Mapping[str, object] = {}
    if stdout_json.exists() and not ambiguous:
        payload = _load_json_object(stdout_json)
    return _Run(run_dir, record, payload, ambiguous)


def _record_integrity_errors(
    label: str,
    run: _Run,
    lock: Mapping[str, object],
    published_head: str,
    published_tree: str,
) -> list[str]:
    errors: list[str] = []
    record = run.record
    if record.get("published_ref") != lock.get("published_ref"):
        errors.append(f"{label} published_ref mismatch")
    if record.get("published_head") != published_head:
        errors.append(f"{label} published_head mismatch")
    if record.get("published_tree") != published_tree:
        errors.append(f"{label} published_tree mismatch")
    if record.get("git_head") != published_head:
        errors.append(f"{label} git_head mismatch")
    if record.get("git_tree") != published_tree:
        errors.append(f"{label} git_tree mismatch")
    if record.get("git_tree_state") != "clean":
        errors.append(f"{label} record does not have clean git tree")
    expected_lock_hash = _sha256_file(Path(_string(lock["_lock_path"], "_lock_path")))
    if record.get("lock_sha256") != expected_lock_hash:
        errors.append(f"{label} lock_sha256 mismatch")
    stdout_hashes = _stdout_hashes(run)
    if record.get("stdout_raw_sha256") != stdout_hashes[0]:
        errors.append(f"{label} stdout_raw_sha256 mismatch")
    if record.get("stdout_canonical_json_sha256") != stdout_hashes[1]:
        errors.append(f"{label} stdout_canonical_json_sha256 mismatch")
    stderr_path = run.run_dir / "stderr.txt"
    stderr_hash = _sha256_file(stderr_path) if stderr_path.exists() else None
    if record.get("stderr_raw_sha256") != stderr_hash:
        errors.append(f"{label} stderr_raw_sha256 mismatch")
    return errors


def _stdout_hashes(run: _Run) -> tuple[str | None, str | None]:
    run_dir = run.run_dir
    stdout_json = run_dir / "stdout.json"
    stdout_bin = run_dir / "stdout.bin"
    if stdout_json.exists() and stdout_bin.exists():
        return None, None
    if stdout_json.exists():
        data = stdout_json.read_bytes()
        payload = _load_json_object(stdout_json)
        return hashlib.sha256(data).hexdigest(), canonical_json_sha256(payload)
    if stdout_bin.exists():
        return hashlib.sha256(stdout_bin.read_bytes()).hexdigest(), None
    return None, None


def _mechanism_check(
    case_id: str,
    result: Mapping[str, object],
    record: Mapping[str, object],
    bundle_root: Path,
) -> dict[str, object]:
    if case_id == "G4_CRP_S4PR_AGREE":
        bridge = _mapping(result.get("partial_deadlock_bridge"), "bridge")
        resources = set(_string_list(bridge.get("certificate_resources"), "resources"))
        mapped = set(_string_list(bridge.get("mapped_crp_resources"), "mapped"))
        matching_count = _strict_int(bridge.get("matching_kernel_count"))
        certificate_available = bridge.get("certificate_available") is True
        agrees = bridge.get("agrees") is True
        classification_ok = result.get("classification") == (
            "partial_deadlock_bridge_agreement"
        )
        resources_equal = resources == mapped
        passed = (
            classification_ok
            and certificate_available
            and agrees
            and matching_count >= 1
            and resources_equal
        )
        return {
            "status": "PASS" if passed else "FAIL",
            "matching_kernel_count": matching_count,
            "certificate_available": certificate_available,
            "agrees": agrees,
            "resources_equal": resources_equal,
            "family": result.get("family"),
        }
    if case_id in {"G4_IMS_PARAMETER_GRID", "G4_MEDIUM_ISLAND_REBUILD"}:
        bounds_ok = _probability_bounds_valid(result)
        estimands = record.get("estimand_ids")
        terminal_visible = _terminal_d_local_verified(result)
        complete = record.get("exit_code") == 0 and record.get("timed_out") is False
        return {
            "status": "PASS"
            if complete and bounds_ok and terminal_visible and estimands
            else "FAIL",
            "execution_complete": complete,
            "probability_bounds_valid": bounds_ok,
            "probability_absolute_tolerance": PROBABILITY_ABSOLUTE_TOLERANCE,
            "terminal_d_local_verified": terminal_visible,
            "estimand_ids": estimands,
            "stdout_canonical_json_sha256": record.get("stdout_canonical_json_sha256"),
        }
    if case_id in {"G4_CRP_OUTSIDE_S4PR", "G4_ADVERSARIAL_BOUNDARY"}:
        return _boundary_score(case_id, result, record, bundle_root)
    return {"status": "FAIL"}


def _boundary_score(
    case_id: str,
    result: Mapping[str, object],
    record: Mapping[str, object],
    bundle_root: Path,
) -> dict[str, object]:
    import ims_deadlock.g5_scoring as g5_scoring

    freeze = check_g4_freeze(bundle_root)
    g5_module = cast(Any, g5_scoring)
    original = g5_module.check_g4_freeze
    g5_module.check_g4_freeze = lambda _root: freeze
    adapter = _g5_scoring_capture_adapter(record, freeze)
    try:
        score = score_case(bundle_root, result, adapter).to_json_dict()
    except (ScoringError, ReplayError):
        return {
            "status": "FAIL",
            "scorer_status": "rejected",
            "scoring_adapter_schema": G5_CAPTURE_SCHEMA,
        }
    finally:
        g5_module.check_g4_freeze = original
    return {
        "status": "PASS" if score.get("theorem_supported") is True else "FAIL",
        "scoring_adapter_schema": G5_CAPTURE_SCHEMA,
        "theorem_prediction_status": score.get("theorem_prediction_status"),
        "metric_results": score.get("metric_results"),
    }


def _g5_scoring_capture_adapter(
    record: Mapping[str, object],
    freeze: object,
) -> dict[str, object]:
    adapted = dict(record)
    adapted["schema_version"] = G5_CAPTURE_SCHEMA
    adapted["freeze_status"] = "FROZEN"
    adapted["freeze_id"] = _string(
        record.get("historical_freeze_id")
        if record.get("historical_freeze_id") is not None
        else getattr(freeze, "freeze_id", None),
        "freeze_id",
    )
    adapted["launch_error"] = None
    return adapted


def _probability_bounds_valid(result: Mapping[str, object]) -> bool:
    if result.get("case_id") == "G4_IMS_PARAMETER_GRID":
        cells = result.get("cells")
        if not isinstance(cells, list) or not cells:
            return False
        return all(
            isinstance(cell, Mapping)
            and _quantitative_probability_integrity_valid(
                _mapping(cell.get("quantitative"), "quantitative")
            )
            for cell in cells
        )
    quantitative = _mapping(result.get("quantitative"), "quantitative")
    return _quantitative_probability_integrity_valid(quantitative)


def _quantitative_probability_integrity_valid(
    quantitative: Mapping[str, object],
) -> bool:
    probabilities = quantitative.get("deadlock_probability")
    bounds = quantitative.get("probability_bounds")
    if not isinstance(probabilities, Mapping) or not probabilities:
        return False
    if not isinstance(bounds, Mapping):
        return False
    return (
        quantitative.get("probability_bounds_valid") is True
        and probability_bounds_match_values(
            probabilities.values(),
            bounds.get("min"),
            bounds.get("max"),
        )
        and linear_residual_is_numerically_valid(
            quantitative.get("committor_residual_inf_norm")
        )
        and linear_residual_is_numerically_valid(
            quantitative.get("mean_time_residual_inf_norm")
        )
    )


def _bounds_mapping_valid(bounds: Mapping[str, object]) -> bool:
    return probability_interval_is_numerically_valid(
        bounds.get("min"),
        bounds.get("max"),
    )


def _estimand_id_from_payload(payload: Mapping[str, object]) -> str | None:
    estimand = payload.get("estimand")
    if not isinstance(estimand, Mapping):
        return None
    hashes = estimand.get("hashes")
    if not isinstance(hashes, Mapping):
        return None
    estimand_id = hashes.get("estimand_id")
    return estimand_id if isinstance(estimand_id, str) and estimand_id else None


def _terminal_d_local_verified(result: Mapping[str, object]) -> bool:
    if result.get("case_id") == "G4_IMS_PARAMETER_GRID":
        cells = result.get("cells")
        if not isinstance(cells, list) or not cells:
            return False
        any_nonempty = False
        for cell in cells:
            if not isinstance(cell, Mapping):
                return False
            d_local = _terminal_d_local(cell)
            if d_local is None:
                return False
            any_nonempty = any_nonempty or bool(d_local)
        return any_nonempty
    d_local = _terminal_d_local(result)
    return d_local is not None and bool(d_local)


def read_historical_terminal_classification(
    payload: Mapping[str, object],
) -> HistoricalTerminalClassification | None:
    if "terminal_classification" in payload:
        terminal_value = payload.get("terminal_classification")
        if not isinstance(terminal_value, Mapping):
            return None
        terminal = terminal_value
    else:
        terminal = payload
    provenance = terminal.get("lts_provenance_audit")
    local_audit = terminal.get("local_bad_soundness_audit")
    if not isinstance(provenance, Mapping) or provenance.get("verified") is not True:
        return None
    if not isinstance(local_audit, Mapping) or local_audit.get("verified") is not True:
        return None
    version = terminal.get("classification_version")
    classes = terminal.get("classes")
    if not isinstance(version, str) or not isinstance(classes, Mapping):
        return None
    d_local = _historical_string_tuple(classes.get("D_local"))
    if d_local is None:
        return None
    if version == HISTORICAL_TERMINAL_CLASSIFICATION_V2:
        return HistoricalTerminalClassification(
            classification_version=version,
            d_local_state_ids=d_local,
            certified_s_t_state_ids=None,
        )
    if version != HISTORICAL_TERMINAL_CLASSIFICATION_V3:
        return None
    certified_s_t = _historical_certified_s_t_state_ids(terminal, classes, d_local)
    if certified_s_t is None:
        return None
    return HistoricalTerminalClassification(
        classification_version=version,
        d_local_state_ids=d_local,
        certified_s_t_state_ids=certified_s_t,
    )


def _historical_certified_s_t_state_ids(
    terminal: Mapping[str, object],
    classes: Mapping[str, object],
    d_local: tuple[str, ...],
) -> tuple[str, ...] | None:
    d_global = _historical_string_tuple(classes.get("D_global"))
    f_state_ids = _historical_string_tuple(classes.get("F"))
    if d_global is None or f_state_ids is None:
        return None
    selected_bad = tuple(sorted(set(d_global) | set(d_local)))
    selected_targets = tuple(sorted(set(selected_bad) | set(f_state_ids)))
    bad_hit_sets = terminal.get("bad_hit_sets")
    if not isinstance(bad_hit_sets, Mapping):
        return None
    bad_hit_d_global = _historical_string_tuple(bad_hit_sets.get("D_global"))
    bad_hit_d_local = _historical_string_tuple(bad_hit_sets.get("D_local"))
    if bad_hit_d_global != d_global or bad_hit_d_local != d_local:
        return None
    if _historical_string_tuple(terminal.get("selected_bad_state_ids")) != selected_bad:
        return None
    certificate = terminal.get("absorption_domain_certificate")
    if not isinstance(certificate, Mapping):
        return None
    if certificate.get("version") != HISTORICAL_ABSORPTION_DOMAIN_CERTIFICATE_VERSION:
        return None
    if (
        certificate.get("algorithm_version")
        != HISTORICAL_ABSORPTION_DOMAIN_ALGORITHM_VERSION
    ):
        return None
    if certificate.get("certification_status") != HISTORICAL_CERTIFIED_STATUS:
        return None
    if certificate.get("reason_codes") != []:
        return None
    selected_absorbing = _historical_string_tuple(
        certificate.get("selected_absorbing_state_ids")
    )
    if selected_absorbing != selected_targets:
        return None
    assumptions = certificate.get("assumptions")
    if not isinstance(assumptions, Mapping):
        return None
    if any(
        assumptions.get(flag) is not True
        for flag in _HISTORICAL_CERTIFICATE_ASSUMPTION_FLAGS
    ):
        return None
    identity = certificate.get("identity")
    if not isinstance(identity, Mapping):
        return None
    if any(
        not isinstance(identity.get(field), str) or identity.get(field) == ""
        for field in _HISTORICAL_CERTIFICATE_IDENTITY_HASHES
    ):
        return None
    hashes = terminal.get("hashes")
    if not isinstance(hashes, Mapping):
        return None
    for field in _HISTORICAL_CERTIFICATE_IDENTITY_HASHES:
        if hashes.get(field) != identity.get(field):
            return None
    derived = terminal.get("derived_state_sets")
    if not isinstance(derived, Mapping):
        return None
    s_reach = derived.get("S_reach")
    if not isinstance(s_reach, Mapping):
        return None
    if s_reach.get("graph_semantics") != HISTORICAL_SUPPORT_GRAPH_SEMANTICS:
        return None
    if s_reach.get("positive_rate_verified") is not True:
        return None
    s_reach_ids = _historical_string_tuple(s_reach.get("state_ids"))
    support_unreachable = _historical_string_tuple(
        s_reach.get("support_unreachable_state_ids")
    )
    if s_reach_ids is None or support_unreachable is None:
        return None
    s_t = derived.get("S_T")
    if not isinstance(s_t, Mapping):
        return None
    if s_t.get("certification_status") != HISTORICAL_CERTIFIED_STATUS:
        return None
    if s_t.get("reason_codes") != []:
        return None
    s_t_state_ids = _historical_string_tuple(s_t.get("state_ids"))
    if s_t_state_ids is None:
        return None
    if _historical_string_tuple(certificate.get("s_t_state_ids")) != s_t_state_ids:
        return None
    derived_unselected_closed = _historical_component_tuple(
        derived.get("unselected_closed_sccs")
    )
    certificate_unselected_closed = _historical_component_tuple(
        certificate.get("unselected_closed_sccs")
    )
    if derived_unselected_closed is None or certificate_unselected_closed is None:
        return None
    if derived_unselected_closed != certificate_unselected_closed:
        return None
    derived_closed_basin = _historical_string_tuple(
        derived.get("closed_class_reverse_basin_state_ids")
    )
    certificate_closed_basin = _historical_string_tuple(
        certificate.get("closed_class_reverse_basin_state_ids")
    )
    if derived_closed_basin != certificate_closed_basin:
        return None
    derived_non_as = _historical_string_tuple(
        derived.get("non_almost_sure_absorbing_state_ids")
    )
    certificate_non_as = _historical_string_tuple(
        certificate.get("non_almost_sure_absorbing_state_ids")
    )
    if derived_non_as != certificate_non_as:
        return None
    if derived_closed_basin is None or derived_non_as is None:
        return None
    if derived_closed_basin != derived_non_as:
        return None
    selected_absorbing_set = set(selected_absorbing)
    non_as_set = set(derived_non_as)
    nonabsorbing_domain = set(s_reach_ids) | set(support_unreachable)
    if nonabsorbing_domain & selected_absorbing_set:
        return None
    if not set(s_t_state_ids) <= nonabsorbing_domain:
        return None
    if set(s_t_state_ids) & (selected_absorbing_set | non_as_set):
        return None
    return s_t_state_ids


def _historical_string_tuple(value: object) -> tuple[str, ...] | None:
    if not isinstance(value, list):
        return None
    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            return None
        result.append(item)
    return tuple(result)


def _historical_component_tuple(
    value: object,
) -> tuple[tuple[str, ...], ...] | None:
    if not isinstance(value, list):
        return None
    result: list[tuple[str, ...]] = []
    for component in value:
        parsed = _historical_string_tuple(component)
        if parsed is None:
            return None
        result.append(parsed)
    return tuple(result)


def _terminal_d_local(payload: Mapping[str, object]) -> list[str] | None:
    classification = read_historical_terminal_classification(payload)
    if classification is None:
        return None
    return list(classification.d_local_state_ids)


def _safe_output_root(path: Path, bundle_root: Path) -> Path:
    if ".." in path.parts:
        raise ReplayError("output_root contains path traversal")
    resolved = path.resolve()
    if resolved == bundle_root or bundle_root in resolved.parents:
        raise ReplayError("output_root must not enter historical bundle")
    evidence_g5 = Path("evidence/g5").resolve()
    if resolved == evidence_g5 or evidence_g5 in resolved.parents:
        raise ReplayError("output_root must not enter repository evidence/g5")
    return resolved


def _historical_freeze_id(bundle_root: Path, freeze: object) -> str | None:
    value = getattr(freeze, "freeze_id", None)
    if isinstance(value, str):
        return value
    entry = bundle_root / "FREEZE_ENTRY.json"
    if entry.is_file():
        payload = _load_json_object(entry)
        entry_value = payload.get("freeze_id")
        return entry_value if isinstance(entry_value, str) else None
    return None


def _current_git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=Path.cwd(),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def _current_git_tree() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD^{tree}"],
            cwd=Path.cwd(),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def _current_git_tree_state() -> str:
    try:
        output = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=Path.cwd(),
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"
    return "dirty" if output.strip() else "clean"


def _resolve_published_ref(ref: str) -> tuple[str, str]:
    try:
        head = subprocess.check_output(
            ["git", "rev-parse", ref],
            cwd=Path.cwd(),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        tree = subprocess.check_output(
            ["git", "rev-parse", f"{ref}^{{tree}}"],
            cwd=Path.cwd(),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN", "UNKNOWN"
    return head, tree


def _current_g6_code_hashes() -> dict[str, str]:
    root = Path.cwd().resolve()
    hashes: dict[str, str] = {}
    source_root = root / "src" / "ims_deadlock"
    for path in sorted(source_root.rglob("*.py")):
        if any(part == "__pycache__" for part in path.parts):
            continue
        hashes[path.relative_to(root).as_posix()] = _sha256_file(path)
    return hashes


def _sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.resolve().read_bytes()).hexdigest()
    except OSError as exc:
        raise ReplayError(f"cannot hash file: {path}") from exc


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ReplayError(f"cannot read JSON file: {path}") from exc
    try:
        payload = json.loads(text, object_pairs_hook=_no_duplicate_object)
    except ValueError as exc:
        raise ReplayError(f"invalid JSON file: {path}") from exc
    if not isinstance(payload, dict):
        raise ReplayError(f"{path} must contain a JSON object")
    _reject_nonfinite_json(payload, str(path))
    return payload


def _no_duplicate_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is not allowed: {value}")


def _reject_nonfinite_json(value: object, label: str) -> None:
    if isinstance(value, float) and value != value:
        raise ReplayError(f"{label} contains non-finite JSON number")
    if isinstance(value, float) and value in (float("inf"), float("-inf")):
        raise ReplayError(f"{label} contains non-finite JSON number")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_nonfinite_json(item, f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_nonfinite_json(item, f"{label}[{index}]")


def _json_text(payload: object) -> str:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    )


def _acquire_schedule_slot(
    lock: Mapping[str, object],
    *,
    case_id: str,
    run_label: str,
    published_head: str,
    published_tree: str,
) -> dict[str, object]:
    output_root = Path(_string(lock["output_root"], "output_root"))
    lock_path = output_root / ".schedule.lock"
    _acquire_schedule_state_lock(lock_path, case_id, run_label)
    try:
        state_path = output_root / "schedule_state.json"
        state = _load_schedule_state(state_path, lock)
        wave = _schedule_wave(case_id, run_label)
        completed = _validated_completed_pairs(
            state.get("completed"),
            output_root,
            lock,
            published_head,
            published_tree,
        )
        incidents = _schedule_pairs(state.get("incidents"))
        active = _schedule_active(state.get("active"))
        if (run_label, case_id) in incidents:
            raise ReplayError("terminal schedule incident blocks recapture")
        if _prior_incident_blocks(incidents, run_label, str(wave["wave_id"])):
            raise ReplayError("terminal schedule incident blocks downstream")
        if run_label == "repro" and not all(
            ("primary", primary_case_id) in completed for primary_case_id in CASE_IDS
        ):
            raise ReplayError("repro capture requires all primary captures complete")
        for prior_wave in _prior_waves(run_label, str(wave["wave_id"])):
            missing = [
                prior_case_id
                for prior_case_id in _string_list(prior_wave["case_ids"], "case_ids")
                if (run_label, prior_case_id) not in completed
            ]
            if missing:
                raise ReplayError(f"prior wave {prior_wave['wave_id']} is incomplete")
        wave_id = _string(wave["wave_id"], "wave_id")
        max_concurrent = _strict_int(wave["max_concurrent"])
        active_in_wave = [
            item
            for item in active
            if item.get("run_label") == run_label and item.get("wave_id") == wave_id
        ]
        if len(active_in_wave) >= max_concurrent or len(active) >= max_concurrent:
            raise ReplayError("schedule concurrency limit reached")
        if (run_label, case_id) in {
            (
                _string(item.get("run_label"), "run_label"),
                _string(item.get("case_id"), "case_id"),
            )
            for item in active
        }:
            raise ReplayError("same-case schedule overlap is not allowed")
        if (run_label, case_id) in completed:
            raise ReplayError("capture is already completed in schedule state")
        entry: dict[str, object] = {
            "case_id": case_id,
            "run_label": run_label,
            "wave_id": wave_id,
            "published_head": published_head,
            "published_tree": published_tree,
            "pid": os.getpid(),
            "hostname": socket.gethostname(),
            "started_at": time.time(),
        }
        cast(list[object], state["active"]).append(entry)
        cast(list[object], state["events"]).append(
            {"event": "capture_started", **entry}
        )
        _replace_json_atomic(state_path, state)
        return entry
    finally:
        _release_schedule_state_lock(lock_path)


def _finish_schedule_slot(
    lock: Mapping[str, object],
    entry: Mapping[str, object],
    *,
    record_exists: bool,
    success: bool,
) -> None:
    output_root = Path(_string(lock["output_root"], "output_root"))
    lock_path = output_root / ".schedule.lock"
    _acquire_schedule_state_lock(
        lock_path,
        _string(entry.get("case_id"), "case_id"),
        _string(entry.get("run_label"), "run_label"),
    )
    try:
        state_path = output_root / "schedule_state.json"
        state = _load_schedule_state(state_path, lock)
        active = _schedule_active(state.get("active"))
        entry_key = (
            _string(entry.get("run_label"), "run_label"),
            _string(entry.get("case_id"), "case_id"),
        )
        state["active"] = [
            item
            for item in active
            if (
                _string(item.get("run_label"), "run_label"),
                _string(item.get("case_id"), "case_id"),
            )
            != entry_key
        ]
        if record_exists and success:
            completed_entry = {
                "case_id": entry["case_id"],
                "run_label": entry["run_label"],
                "wave_id": entry["wave_id"],
                "published_head": entry["published_head"],
                "published_tree": entry["published_tree"],
                "finished_at": time.time(),
                "status": "recorded",
            }
            completed = cast(list[object], state["completed"])
            if entry_key not in _schedule_pairs(completed):
                completed.append(completed_entry)
            cast(list[object], state["events"]).append(
                {"event": "capture_recorded", **completed_entry}
            )
        elif record_exists:
            incident_entry = {
                "case_id": entry["case_id"],
                "run_label": entry["run_label"],
                "wave_id": entry["wave_id"],
                "published_head": entry["published_head"],
                "published_tree": entry["published_tree"],
                "finished_at": time.time(),
                "status": "terminal_capture_failure",
            }
            incidents = cast(list[object], state["incidents"])
            if entry_key not in _schedule_pairs(incidents):
                incidents.append(incident_entry)
            cast(list[object], state["events"]).append(
                {"event": "terminal_capture_failure", **incident_entry}
            )
        else:
            incident_entry = {
                "case_id": entry["case_id"],
                "run_label": entry["run_label"],
                "wave_id": entry["wave_id"],
                "published_head": entry["published_head"],
                "published_tree": entry["published_tree"],
                "finished_at": time.time(),
                "status": "terminal_capture_failure_before_record",
            }
            incidents = cast(list[object], state["incidents"])
            if entry_key not in _schedule_pairs(incidents):
                incidents.append(incident_entry)
            cast(list[object], state["events"]).append(
                {"event": "terminal_capture_failure_before_record", **incident_entry}
            )
        _replace_json_atomic(state_path, state)
    finally:
        _release_schedule_state_lock(lock_path)


def _acquire_schedule_state_lock(path: Path, case_id: str, run_label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "started_at": time.time(),
        "case_id": case_id,
        "run_label": run_label,
    }
    deadline = time.monotonic() + SCHEDULE_LOCK_CONTENTION_WAIT_SECONDS
    fd: int | None = None
    while fd is None:
        try:
            fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            if time.monotonic() < deadline:
                time.sleep(0.01)
                continue
            if sys.platform == "win32":
                _write_schedule_lock_incident(
                    path,
                    case_id=case_id,
                    run_label=run_label,
                    classification="windows_schedule_lease_contention_timeout",
                    owner_liveness="unknown",
                    read_lease_metadata=False,
                )
            else:
                lease_status = _schedule_lock_status(path)
                classification = str(lease_status["classification"])
                if classification in {"None", "missing_schedule_lease"}:
                    classification = _schedule_lock_timeout_classification(lease_status)
                _write_schedule_lock_incident(
                    path,
                    case_id=case_id,
                    run_label=run_label,
                    classification=classification,
                    owner_liveness=str(lease_status["owner_liveness"]),
                )
            raise ReplayError(
                "existing schedule lease requires manual incident classification; "
                "automatic recovery is forbidden"
            ) from exc
        except PermissionError as exc:
            if _is_windows_schedule_lock_permission_contention(exc):
                if time.monotonic() < deadline:
                    time.sleep(0.01)
                    continue
                if path.exists():
                    _write_schedule_lock_incident(
                        path,
                        case_id=case_id,
                        run_label=run_label,
                        classification="windows_schedule_lease_contention_timeout",
                        owner_liveness="unknown",
                        read_lease_metadata=False,
                    )
                    raise ReplayError(
                        "existing schedule lease requires manual incident "
                        "classification; automatic recovery is forbidden"
                    ) from exc
            raise ReplayError(f"cannot create schedule lease: {path}") from exc
        except OSError as exc:
            raise ReplayError(f"cannot create schedule lease: {path}") from exc
    try:
        os.write(fd, _json_text(payload).encode("utf-8"))
    finally:
        os.close(fd)


def _is_windows_schedule_lock_permission_contention(exc: PermissionError) -> bool:
    if sys.platform != "win32":
        return False
    if exc.errno != errno.EACCES and getattr(exc, "winerror", None) not in {5, 32}:
        return False
    return True


def _schedule_lock_status(path: Path) -> dict[str, object]:
    try:
        payload = _load_json_object(path)
    except ReplayError:
        try:
            stat = path.stat()
            if time.time() - stat.st_mtime < SCHEDULE_LOCK_INITIALIZATION_GRACE_SECONDS:
                return {
                    "classification": None,
                    "owner_liveness": "unknown",
                    "age_exceeded": False,
                }
        except OSError:
            pass
        if path.exists():
            return {
                "classification": "unclassifiable_schedule_lease",
                "owner_liveness": "unknown",
                "age_exceeded": True,
            }
        return {
            "classification": "missing_schedule_lease",
            "owner_liveness": "unknown",
            "age_exceeded": False,
        }
    try:
        pid = _strict_int(payload.get("pid"))
        hostname = _string(payload.get("hostname"), "hostname")
        started_at = _strict_float(payload.get("started_at"))
        _string(payload.get("case_id"), "case_id")
        _string(payload.get("run_label"), "run_label")
    except ReplayError:
        return {
            "classification": "unclassifiable_schedule_lease",
            "owner_liveness": "unknown",
            "age_exceeded": True,
        }
    liveness = _schedule_lock_owner_liveness(pid, hostname)
    if liveness == "dead":
        classification = "dead_schedule_lease_owner"
    else:
        classification = None
    return {
        "classification": classification,
        "owner_liveness": liveness,
        "age_exceeded": time.time() - started_at >= SCHEDULE_LOCK_STALE_SECONDS,
    }


def _schedule_lock_timeout_classification(status: Mapping[str, object]) -> str:
    owner_liveness = _string(status.get("owner_liveness"), "owner_liveness")
    age_exceeded = status.get("age_exceeded") is True
    if owner_liveness == "live":
        return "live_schedule_lease_contention_timeout"
    if owner_liveness == "unknown" and age_exceeded:
        return "unknown_schedule_lease_age_exceeded"
    if owner_liveness == "unknown":
        return "unknown_schedule_lease_contention_timeout"
    return "schedule_lease_contention_timeout"


def _schedule_lock_owner_liveness(pid: int, hostname: str) -> str:
    if hostname != socket.gethostname():
        return "unknown"
    if sys.platform == "win32":
        return "unknown"
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return "dead"
    except PermissionError:
        return "unknown"
    except OSError:
        return "unknown"
    return "live"


def _write_schedule_lock_incident(
    lock_path: Path,
    *,
    case_id: str,
    run_label: str,
    classification: str,
    owner_liveness: str,
    read_lease_metadata: bool = True,
) -> None:
    lease_payload: object = None
    if read_lease_metadata:
        try:
            lease_payload = _load_json_object(lock_path)
        except ReplayError:
            lease_payload = None
    incident = {
        "schema_version": SCHEDULE_LOCK_INCIDENT_SCHEMA,
        "classification": classification,
        "owner_liveness": owner_liveness,
        "action": "fail_closed_no_auto_reap",
        "lease_path": str(lock_path),
        "case_id": case_id,
        "run_label": run_label,
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "observed_at": time.time(),
        "lease_metadata": lease_payload,
    }
    incident_path = lock_path.with_name(
        f"{lock_path.name}.incident-{time.time_ns()}-{os.getpid()}.json"
    )
    _write_json_atomic(incident_path, incident)


def _release_schedule_state_lock(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except PermissionError as exc:
        raise ReplayError(f"cannot release schedule lease: {path}") from exc
    except OSError as exc:
        raise ReplayError(f"cannot release schedule lease: {path}") from exc


def _load_schedule_state(path: Path, lock: Mapping[str, object]) -> dict[str, object]:
    if not path.exists():
        return {
            "schema_version": SCHEDULE_STATE_SCHEMA,
            "execution_schedule_sha256": canonical_json_sha256(
                lock["execution_schedule"]
            ),
            "active": [],
            "completed": [],
            "incidents": [],
            "events": [],
        }
    state = _load_json_object(path)
    if state.get("schema_version") != SCHEDULE_STATE_SCHEMA:
        raise ReplayError("schedule_state schema_version is invalid")
    if state.get("execution_schedule_sha256") != canonical_json_sha256(
        lock["execution_schedule"]
    ):
        raise ReplayError("schedule_state execution_schedule_sha256 mismatch")
    if not isinstance(state.get("active"), list):
        raise ReplayError("schedule_state active must be a list")
    if not isinstance(state.get("completed"), list):
        raise ReplayError("schedule_state completed must be a list")
    if not isinstance(state.get("incidents"), list):
        raise ReplayError("schedule_state incidents must be a list")
    if not isinstance(state.get("events"), list):
        raise ReplayError("schedule_state events must be a list")
    return state


def _schedule_wave(case_id: str, run_label: str) -> Mapping[str, object]:
    schedule = EXPECTED_EXECUTION_SCHEDULE.get(run_label)
    if not isinstance(schedule, list):
        raise ReplayError("execution_schedule run label must be a list")
    for wave in schedule:
        wave_mapping = _mapping(wave, "wave")
        if case_id in _string_list(wave_mapping.get("case_ids"), "case_ids"):
            return wave_mapping
    raise ReplayError("case_id is not in locked execution_schedule")


def _prior_waves(run_label: str, wave_id: str) -> list[Mapping[str, object]]:
    schedule = EXPECTED_EXECUTION_SCHEDULE.get(run_label)
    if not isinstance(schedule, list):
        raise ReplayError("execution_schedule run label must be a list")
    prior: list[Mapping[str, object]] = []
    for wave in schedule:
        wave_mapping = _mapping(wave, "wave")
        if wave_mapping.get("wave_id") == wave_id:
            return prior
        prior.append(wave_mapping)
    raise ReplayError("wave_id is not in locked execution_schedule")


def _prior_incident_blocks(
    incidents: set[tuple[str, str]],
    run_label: str,
    wave_id: str,
) -> bool:
    if run_label == "repro" and any(label == "primary" for label, _case in incidents):
        return True
    for prior_wave in _prior_waves(run_label, wave_id):
        for case_id in _string_list(prior_wave.get("case_ids"), "case_ids"):
            if (run_label, case_id) in incidents:
                return True
    return False


def _schedule_pair_has_incident(
    lock: Mapping[str, object],
    case_id: str,
    run_label: str,
) -> bool:
    state_path = (
        Path(_string(lock["output_root"], "output_root")) / "schedule_state.json"
    )
    if not state_path.exists():
        return False
    state = _load_schedule_state(state_path, lock)
    return (run_label, case_id) in _schedule_pairs(state.get("incidents"))


def _validated_completed_pairs(
    value: object,
    output_root: Path,
    lock: Mapping[str, object],
    published_head: str,
    published_tree: str,
) -> set[tuple[str, str]]:
    if not isinstance(value, list):
        raise ReplayError("schedule completed entries must be a list")
    pairs: set[tuple[str, str]] = set()
    for item in value:
        entry = _mapping(item, "completed schedule entry")
        run_label = _string(entry.get("run_label"), "run_label")
        case_id = _string(entry.get("case_id"), "case_id")
        try:
            run = _load_run(output_root / "cases" / case_id / run_label)
            errors = _record_integrity_errors(
                "completed",
                run,
                lock,
                published_head,
                published_tree,
            )
            if (
                errors
                or run.record.get("case_id") != case_id
                or run.record.get("run_label") != run_label
                or run.record.get("exit_code") != 0
                or run.record.get("timed_out") is not False
                or run.record.get("stdout_canonical_json_sha256") in (None, "")
                or run.payload == {}
                or _formal_success_error(
                    run.payload,
                    case_id,
                    cast(str | None, run.record.get("stdout_canonical_json_sha256")),
                )
                is not None
            ):
                raise ReplayError("invalid completed capture")
        except ReplayError as exc:
            raise ReplayError(
                "schedule completed entry lacks successful capture record"
            ) from exc
        pairs.add((run_label, case_id))
    return pairs


def _schedule_pairs(value: object) -> set[tuple[str, str]]:
    if not isinstance(value, list):
        raise ReplayError("schedule entries must be a list")
    pairs: set[tuple[str, str]] = set()
    for item in value:
        entry = _mapping(item, "schedule entry")
        pairs.add(
            (
                _string(entry.get("run_label"), "run_label"),
                _string(entry.get("case_id"), "case_id"),
            )
        )
    return pairs


def _schedule_active(value: object) -> list[Mapping[str, object]]:
    if not isinstance(value, list):
        raise ReplayError("schedule active entries must be a list")
    return [_mapping(item, "active schedule entry") for item in value]


def _acquire_case_lease(
    path: Path,
    *,
    case_id: str,
    run_label: str,
    published_head: str,
    published_tree: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "started_at": time.time(),
        "case_id": case_id,
        "run_label": run_label,
        "published_head": published_head,
        "published_tree": published_tree,
    }
    try:
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        try:
            _load_json_object(path)
        except ReplayError:
            pass
        raise ReplayError(
            "existing capture lease requires manual incident classification; "
            "automatic recovery is forbidden"
        ) from exc
    except OSError as exc:
        raise ReplayError(f"cannot create capture lease: {path}") from exc
    try:
        os.write(fd, _json_text(payload).encode("utf-8"))
    finally:
        os.close(fd)


def _release_case_lease(path: Path) -> None:
    path.unlink(missing_ok=True)


def _write_bytes_atomic(path: Path, payload: bytes) -> None:
    if path.exists():
        raise ReplayError(f"output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    if temp.exists():
        raise ReplayError(f"temporary output already exists: {temp}")
    try:
        with temp.open("xb") as handle:
            handle.write(payload)
        os.replace(temp, path)
    except OSError as exc:
        temp.unlink(missing_ok=True)
        raise ReplayError(f"cannot write output: {path}") from exc
    finally:
        temp.unlink(missing_ok=True)


def _replace_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    if temp.exists():
        raise ReplayError(f"temporary output already exists: {temp}")
    try:
        with temp.open("x", encoding="utf-8") as handle:
            handle.write(_json_text(payload))
        os.replace(temp, path)
    except OSError as exc:
        temp.unlink(missing_ok=True)
        raise ReplayError(f"cannot write output: {path}") from exc
    finally:
        temp.unlink(missing_ok=True)


def _write_json_atomic(
    path: Path,
    payload: object,
    *,
    output_root: Path | None = None,
) -> None:
    if output_root is not None:
        target = path.resolve()
        root = output_root.resolve()
        if target != root and root not in target.parents:
            raise ReplayError("output must be under locked replay output root")
    if path.exists():
        raise ReplayError(f"output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    if temp.exists():
        raise ReplayError(f"temporary output already exists: {temp}")
    try:
        with temp.open("x", encoding="utf-8") as handle:
            handle.write(_json_text(payload))
        os.replace(temp, path)
    except OSError as exc:
        temp.unlink(missing_ok=True)
        raise ReplayError(f"cannot write output: {path}") from exc
    finally:
        temp.unlink(missing_ok=True)


def _require_keys(
    payload: Mapping[str, object],
    expected: frozenset[str],
    label: str,
) -> None:
    if set(payload) != expected:
        raise ReplayError(f"{label} must contain exact keys")


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ReplayError(f"{label} must be an object")
    return value


def _string(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ReplayError(f"{label} must be a string")
    return value


def _string_list(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ReplayError(f"{label} must contain only strings")
    return value


def _string_mapping(value: object, label: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ReplayError(f"{label} must be an object")
    result: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not isinstance(item, str):
            raise ReplayError(f"{label} must map strings to strings")
        result[key] = item
    return result


def _strict_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ReplayError("integer field has invalid type")
    return value


def _strict_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ReplayError("numeric field has invalid type")
    return float(value)


if __name__ == "__main__":
    raise SystemExit(main())
