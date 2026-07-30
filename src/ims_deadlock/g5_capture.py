"""G5 execution capture for frozen G4 confirmation runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from typing import Any

from ims_deadlock.g4_freeze import check_g4_freeze

CAPTURE_RECORD_SCHEMA = "ims-deadlock/g5-capture-record/v1"
COMPARISON_SCHEMA = "ims-deadlock/g5-capture-comparison/v1"
_SAFE_LABEL = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")


class CaptureError(RuntimeError):
    """Raised when a G5 capture would violate the preregistered boundary."""

    def __init__(
        self, message: str, *, record: dict[str, object] | None = None
    ) -> None:
        super().__init__(message)
        self.record = record


def capture_g4_case(
    bundle_root: Path,
    output_root: Path,
    case_id: str,
    run_label: str,
    *,
    timeout_seconds: float = 300.0,
    cwd: Path | None = None,
) -> dict[str, object]:
    """Run exactly one frozen G4 case and persist raw bytes plus metadata."""

    safe_case_id = _validate_safe_label(case_id, "case_id")
    safe_run_label = _validate_safe_label(run_label, "run_label")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    run_cwd = (cwd or Path.cwd()).resolve()
    bundle = _resolve_for_child_cwd(bundle_root, run_cwd)
    bundle_arg = bundle_root.as_posix()
    output = _resolve_for_child_cwd(output_root, run_cwd)
    _reject_output_inside_bundle(bundle, output)

    freeze = check_g4_freeze(bundle)
    if freeze.status != "FROZEN":
        raise CaptureError("G5 capture requires FROZEN G4 bundle before launch")
    if safe_case_id not in freeze.case_ids:
        raise CaptureError(
            f"G5 case_id is not sealed in the frozen case universe: {safe_case_id}"
        )

    argv = [
        sys.executable,
        "-m",
        "ims_deadlock.g4_protocol",
        "--root",
        bundle_arg,
        "run",
        safe_case_id,
    ]
    _require_runtime_authorized_g4_run(bundle, safe_case_id, argv)
    run_dir = output / "cases" / safe_case_id / safe_run_label
    if run_dir.exists():
        raise CaptureError(f"capture run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)

    start = datetime.now(UTC)
    start_monotonic = monotonic()
    timed_out = False
    freeze_id = _freeze_id(bundle)
    try:
        process = subprocess.Popen(  # noqa: S603
            argv,
            cwd=str(run_cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
    except OSError as error:
        end = datetime.now(UTC)
        elapsed_seconds = monotonic() - start_monotonic
        stdout_bytes = b""
        stderr_bytes = b""
        (run_dir / "stdout.bin").write_bytes(stdout_bytes)
        (run_dir / "stderr.txt").write_bytes(stderr_bytes)
        record = _record(
            bundle=bundle,
            case_id=safe_case_id,
            run_label=safe_run_label,
            argv=argv,
            cwd=run_cwd,
            start=start,
            end=end,
            elapsed_seconds=elapsed_seconds,
            timeout_seconds=timeout_seconds,
            exit_code=None,
            timed_out=False,
            freeze_status=freeze.status,
            freeze_id=freeze_id,
            stdout_bytes=stdout_bytes,
            stderr_bytes=stderr_bytes,
            stdout_canonical_json_sha256=None,
            launch_error=error,
        )
        _write_json(run_dir / "record.json", record)
        raise CaptureError(
            f"G5 capture launch failed: {error}", record=record
        ) from error
    try:
        stdout_bytes, stderr_bytes = process.communicate(timeout=timeout_seconds)
        exit_code: int | None = process.returncode
    except (subprocess.TimeoutExpired, TimeoutError):
        timed_out = True
        process.kill()
        stdout_bytes, stderr_bytes = process.communicate()
        exit_code = None
    end = datetime.now(UTC)
    elapsed_seconds = monotonic() - start_monotonic

    stdout_json_hash = _write_stdout(run_dir, stdout_bytes)
    (run_dir / "stderr.txt").write_bytes(stderr_bytes)
    record = _record(
        bundle=bundle,
        case_id=safe_case_id,
        run_label=safe_run_label,
        argv=argv,
        cwd=run_cwd,
        start=start,
        end=end,
        elapsed_seconds=elapsed_seconds,
        timeout_seconds=timeout_seconds,
        exit_code=exit_code,
        timed_out=timed_out,
        freeze_status=freeze.status,
        freeze_id=freeze_id,
        stdout_bytes=stdout_bytes,
        stderr_bytes=stderr_bytes,
        stdout_canonical_json_sha256=stdout_json_hash,
    )
    _write_json(run_dir / "record.json", record)
    return record


def compare_capture_hashes(
    primary_run_dir: Path, repro_run_dir: Path
) -> dict[str, object]:
    """Compare raw and canonical JSON stdout hashes from two capture records."""

    primary = _load_record(primary_run_dir)
    repro = _load_record(repro_run_dir)
    primary_valid = _validate_record_for_compare(primary)
    repro_valid = _validate_record_for_compare(repro)
    records_valid = primary_valid and repro_valid
    raw_match = primary.get("stdout_raw_sha256") == repro.get("stdout_raw_sha256")
    primary_canonical = primary.get("stdout_canonical_json_sha256")
    repro_canonical = repro.get("stdout_canonical_json_sha256")
    canonical_present = isinstance(primary_canonical, str) and isinstance(
        repro_canonical, str
    )
    canonical_match = canonical_present and primary_canonical == repro_canonical
    stderr_match = primary.get("stderr_raw_sha256") == repro.get("stderr_raw_sha256")
    case_id_match = primary.get("case_id") == repro.get("case_id")
    argv_match = primary.get("argv") == repro.get("argv")
    freeze_id_match = primary.get("freeze_id") == repro.get("freeze_id")
    git_head_match = primary.get("git_head") == repro.get("git_head")
    match = all(
        [
            case_id_match,
            raw_match,
            canonical_match,
            stderr_match,
            argv_match,
            freeze_id_match,
            git_head_match,
            records_valid,
        ]
    )
    return {
        "schema_version": COMPARISON_SCHEMA,
        "primary_record": str((primary_run_dir / "record.json").resolve()),
        "repro_record": str((repro_run_dir / "record.json").resolve()),
        "case_id_match": case_id_match,
        "argv_match": argv_match,
        "freeze_id_match": freeze_id_match,
        "git_head_match": git_head_match,
        "records_valid": records_valid,
        "stdout_raw_sha256_match": raw_match,
        "stdout_canonical_json_sha256_match": canonical_match,
        "stderr_raw_sha256_match": stderr_match,
        "stdout_raw_sha256": {
            "primary": primary["stdout_raw_sha256"],
            "repro": repro["stdout_raw_sha256"],
            "match": raw_match,
        },
        "stdout_canonical_json_sha256": {
            "primary": primary.get("stdout_canonical_json_sha256"),
            "repro": repro.get("stdout_canonical_json_sha256"),
            "match": canonical_match,
        },
        "stderr_raw_sha256": {
            "primary": primary.get("stderr_raw_sha256"),
            "repro": repro.get("stderr_raw_sha256"),
            "match": stderr_match,
        },
        "match": match,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m ims_deadlock.g5_capture")
    subparsers = parser.add_subparsers(dest="command", required=True)
    capture_parser = subparsers.add_parser("capture")
    capture_parser.add_argument("--root", type=Path, required=True)
    capture_parser.add_argument("--output-root", type=Path, required=True)
    capture_parser.add_argument("--run-label", required=True)
    capture_parser.add_argument("--timeout-seconds", type=float, default=300.0)
    capture_parser.add_argument("case_id")
    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("primary_run_dir", type=Path)
    compare_parser.add_argument("repro_run_dir", type=Path)
    args = parser.parse_args(argv)

    if args.command == "capture":
        try:
            payload = capture_g4_case(
                args.root,
                args.output_root,
                args.case_id,
                args.run_label,
                timeout_seconds=args.timeout_seconds,
            )
        except CaptureError as error:
            if error.record is not None:
                _print_json(error.record)
            return 1
        _print_json(payload)
        return 0 if _capture_succeeded(payload) else 1

    comparison = compare_capture_hashes(args.primary_run_dir, args.repro_run_dir)
    _print_json(comparison)
    return 0 if comparison["match"] is True else 1


def _record(
    *,
    bundle: Path,
    case_id: str,
    run_label: str,
    argv: list[str],
    cwd: Path,
    start: datetime,
    end: datetime,
    elapsed_seconds: float,
    timeout_seconds: float,
    exit_code: int | None,
    timed_out: bool,
    freeze_status: str,
    freeze_id: str | None,
    stdout_bytes: bytes,
    stderr_bytes: bytes,
    stdout_canonical_json_sha256: str | None,
    launch_error: OSError | None = None,
) -> dict[str, object]:
    git = _git_metadata(cwd)
    record: dict[str, object] = {
        "schema_version": CAPTURE_RECORD_SCHEMA,
        "case_id": case_id,
        "run_label": run_label,
        "argv": argv,
        "cwd": str(cwd),
        "bundle_root": str(bundle),
        "started_at_utc": _format_utc(start),
        "ended_at_utc": _format_utc(end),
        "elapsed_seconds": round(elapsed_seconds, 9),
        "timeout_seconds": timeout_seconds,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "git_head": git["head"],
        "git_branch": git["branch"],
        "freeze_id": freeze_id,
        "freeze_status": freeze_status,
        "stdout_raw_sha256": hashlib.sha256(stdout_bytes).hexdigest(),
        "stderr_raw_sha256": hashlib.sha256(stderr_bytes).hexdigest(),
        "stdout_canonical_json_sha256": stdout_canonical_json_sha256,
    }
    if launch_error is not None:
        record["launch_error_type"] = type(launch_error).__name__
        record["launch_error_message"] = str(launch_error)
    return record


def _write_stdout(run_dir: Path, stdout_bytes: bytes) -> str | None:
    try:
        payload = json.loads(
            stdout_bytes.decode("utf-8"),
            parse_constant=_reject_json_constant,
        )
        canonical_hash = _canonical_json_sha256(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        (run_dir / "stdout.bin").write_bytes(stdout_bytes)
        return None
    (run_dir / "stdout.json").write_bytes(stdout_bytes)
    return canonical_hash


def _canonical_json_sha256(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is not allowed: {value}")


def _resolve_for_child_cwd(path: Path, run_cwd: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (run_cwd / path).resolve()


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _print_json(payload: object) -> None:
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    )


def _load_record(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "record.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _capture_succeeded(record: dict[str, object]) -> bool:
    return (
        record.get("exit_code") == 0
        and record.get("timed_out") is False
        and "launch_error_type" not in record
    )


def _validate_record_for_compare(record: dict[str, Any]) -> bool:
    if record.get("schema_version") != CAPTURE_RECORD_SCHEMA:
        return False
    required_strings = [
        "case_id",
        "freeze_id",
        "git_head",
        "stdout_raw_sha256",
        "stdout_canonical_json_sha256",
        "stderr_raw_sha256",
    ]
    if any(
        not isinstance(record.get(field), str) or record.get(field) == ""
        for field in required_strings
    ):
        return False
    argv = record.get("argv")
    return isinstance(argv, list) and all(isinstance(token, str) for token in argv)


def _validate_safe_label(value: str, label: str) -> str:
    if not _SAFE_LABEL.fullmatch(value):
        raise ValueError(f"{label} must be a safe nonempty path label")
    if value in {".", ".."}:
        raise ValueError(f"{label} must be a safe nonempty path label")
    return value


def _reject_output_inside_bundle(bundle: Path, output: Path) -> None:
    if output == bundle or bundle in output.parents:
        raise CaptureError("G5 output root must not be inside the frozen bundle")


def _require_runtime_authorized_g4_run(
    bundle: Path, case_id: str, generated_argv: list[str]
) -> None:
    runtime_path = bundle / "runtime_lock.json"
    try:
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CaptureError(
            "runtime_lock.json is required for G5 authorization"
        ) from error
    if not isinstance(runtime, dict):
        raise CaptureError("runtime_lock.json must contain a JSON object")

    commands = runtime.get("scientific_commands", runtime.get("commands"))
    if not isinstance(commands, list):
        raise CaptureError("runtime_lock.json must list frozen scientific commands")
    for command in commands:
        frozen_tokens = _parse_frozen_g4_run_command(command, case_id)
        if frozen_tokens is None:
            continue
        authorized_argv = [sys.executable, *frozen_tokens[1:]]
        if generated_argv != authorized_argv:
            raise CaptureError(
                "generated G4 argv does not exactly match runtime_lock template"
            )
        return
    raise CaptureError(
        f"G4 run command is not authorized by runtime_lock.json: {case_id}"
    )


def _parse_frozen_g4_run_command(command: object, case_id: str) -> list[str] | None:
    if isinstance(command, str):
        try:
            tokens = shlex.split(command)
        except ValueError:
            return None
    elif isinstance(command, list) and all(isinstance(token, str) for token in command):
        tokens = command
    else:
        return None
    if len(tokens) != 7:
        return None
    if tokens[0] != "python":
        return None
    if tokens[1] != "-m" or tokens[2] != "ims_deadlock.g4_protocol":
        return None
    if tokens[3] != "--root" or tokens[4] != "cases/confirmation/g4":
        return None
    if tokens[5] != "run" or tokens[6] != case_id:
        return None
    return tokens


def _freeze_id(bundle: Path) -> str | None:
    entry_path = bundle / "FREEZE_ENTRY.json"
    try:
        payload = json.loads(entry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    freeze_id = payload.get("freeze_id")
    return freeze_id if isinstance(freeze_id, str) else None


def _format_utc(value: datetime) -> str:
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _git_metadata(cwd: Path) -> dict[str, str | None]:
    git_dir = _find_git_dir(cwd)
    if git_dir is None:
        return {"head": None, "branch": None}
    common_dir = _find_common_git_dir(git_dir)
    head_path = git_dir / "HEAD"
    try:
        head = head_path.read_text(encoding="utf-8").strip()
    except OSError:
        return {"head": None, "branch": None}
    if head.startswith("ref: "):
        ref = head.removeprefix("ref: ").strip()
        branch = ref.removeprefix("refs/heads/")
        commit: str | None
        try:
            commit = (git_dir / ref).read_text(encoding="utf-8").strip()
        except OSError:
            try:
                commit = (common_dir / ref).read_text(encoding="utf-8").strip()
            except OSError:
                commit = _read_packed_ref(git_dir, ref) or _read_packed_ref(
                    common_dir, ref
                )
        return {"head": commit or None, "branch": branch}
    return {"head": head or None, "branch": None}


def _find_git_dir(start: Path) -> Path | None:
    for path in (start, *start.parents):
        candidate = path / ".git"
        if candidate.is_dir():
            return candidate
        if candidate.is_file():
            try:
                content = candidate.read_text(encoding="utf-8").strip()
            except OSError:
                return None
            if content.startswith("gitdir: "):
                gitdir = Path(content.removeprefix("gitdir: ").strip())
                return gitdir if gitdir.is_absolute() else (path / gitdir).resolve()
    return None


def _find_common_git_dir(git_dir: Path) -> Path:
    commondir_path = git_dir / "commondir"
    try:
        content = commondir_path.read_text(encoding="utf-8").strip()
    except OSError:
        return git_dir
    common = Path(content)
    return common if common.is_absolute() else (git_dir / common).resolve()


def _read_packed_ref(git_dir: Path, ref: str) -> str | None:
    packed_refs = git_dir / "packed-refs"
    try:
        lines = packed_refs.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in lines:
        if line.startswith("#") or not line:
            continue
        parts = line.split(" ", 1)
        if len(parts) == 2 and parts[1] == ref:
            return parts[0]
    return None


if __name__ == "__main__":
    raise SystemExit(main())
