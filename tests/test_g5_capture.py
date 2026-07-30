import hashlib
import json
import sys
from pathlib import Path, PureWindowsPath
from types import SimpleNamespace
from typing import Any, cast

import pytest
from tests.test_g4_freeze import _complete_bundle

from ims_deadlock.g5_capture import (
    CaptureError,
    capture_g4_case,
    compare_capture_hashes,
    main,
)


class _CompletedProcess:
    def __init__(self, stdout: bytes, stderr: bytes, returncode: int = 0) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

    def communicate(self, timeout: float | None = None) -> tuple[bytes, bytes]:
        return self.stdout, self.stderr


class _TimeoutProcess:
    returncode = -9

    def __init__(self) -> None:
        self.killed = False

    def communicate(self, timeout: float | None = None) -> tuple[bytes, bytes]:
        if not self.killed:
            raise TimeoutError
        return b"", b"terminated"

    def kill(self) -> None:
        self.killed = True


def _load_record(
    output_root: Path, case_id: str = "G4-HELD-01", run_label: str = "primary"
) -> dict[str, Any]:
    record_path = output_root / "cases" / case_id / run_label / "record.json"
    payload = json.loads(record_path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_capture_runs_exact_g4_command_and_records_hashes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    absolute_bundle = _complete_bundle(tmp_path)
    bundle = absolute_bundle.relative_to(tmp_path / "repo")
    output_root = tmp_path / "out"
    calls: list[dict[str, object]] = []
    stdout_bytes = b'{"b":2,"a":1}\n'
    monkeypatch.chdir(tmp_path / "repo")

    def fake_popen(
        argv: list[str],
        *,
        cwd: str,
        stdout: int,
        stderr: int,
        shell: bool,
    ) -> _CompletedProcess:
        calls.append(
            {
                "argv": argv,
                "cwd": cwd,
                "stdout": stdout,
                "stderr": stderr,
                "shell": shell,
            }
        )
        return _CompletedProcess(stdout=stdout_bytes, stderr=b"note")

    monkeypatch.setattr("ims_deadlock.g5_capture.subprocess.Popen", fake_popen)

    record = capture_g4_case(bundle, output_root, "G4-HELD-01", "primary")

    expected_argv = [
        sys.executable,
        "-m",
        "ims_deadlock.g4_protocol",
        "--root",
        "cases/confirmation/g4",
        "run",
        "G4-HELD-01",
    ]
    assert calls == [
        {
            "argv": expected_argv,
            "cwd": str(Path.cwd()),
            "stdout": -1,
            "stderr": -1,
            "shell": False,
        }
    ]
    assert record["argv"] == expected_argv
    assert record["schema_version"] == "ims-deadlock/g5-capture-record/v1"
    assert record["case_id"] == "G4-HELD-01"
    assert record["run_label"] == "primary"
    assert record["exit_code"] == 0
    assert record["timed_out"] is False
    assert record["timeout_seconds"] == 300.0
    assert record["freeze_status"] == "FROZEN"
    assert record["freeze_id"] == "G4-FREEZE-DEVELOPMENT-TEST"
    assert record["stdout_raw_sha256"]
    assert record["stdout_canonical_json_sha256"]
    assert record["stderr_raw_sha256"] == hashlib.sha256(b"note").hexdigest()
    assert (
        output_root / "cases/G4-HELD-01/primary/stdout.json"
    ).read_bytes() == stdout_bytes
    assert (output_root / "cases/G4-HELD-01/primary/stderr.txt").read_bytes() == b"note"
    assert _load_record(output_root) == record


def test_capture_resolves_preflight_bundle_relative_to_child_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    absolute_bundle = _complete_bundle(tmp_path)
    bundle = absolute_bundle.relative_to(repo)
    output_root = Path("out")
    calls: list[dict[str, object]] = []
    monkeypatch.chdir(tmp_path)

    def fake_popen(
        argv: list[str],
        *,
        cwd: str,
        stdout: int,
        stderr: int,
        shell: bool,
    ) -> _CompletedProcess:
        calls.append({"argv": argv, "cwd": cwd})
        return _CompletedProcess(stdout=b"{}", stderr=b"")

    monkeypatch.setattr("ims_deadlock.g5_capture.subprocess.Popen", fake_popen)

    record = capture_g4_case(bundle, output_root, "G4-HELD-01", "primary", cwd=repo)

    assert calls == [
        {
            "argv": [
                sys.executable,
                "-m",
                "ims_deadlock.g4_protocol",
                "--root",
                "cases/confirmation/g4",
                "run",
                "G4-HELD-01",
            ],
            "cwd": str(repo),
        }
    ]
    assert record["bundle_root"] == str(absolute_bundle)
    assert (repo / "out" / "cases" / "G4-HELD-01" / "primary").is_dir()


def test_capture_preserves_frozen_root_token_for_windows_relative_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    absolute_bundle = _complete_bundle(tmp_path)
    windows_bundle = cast(Path, PureWindowsPath("cases/confirmation/g4"))
    output_root = Path("out")
    calls: list[dict[str, object]] = []
    monkeypatch.chdir(tmp_path)

    def fake_popen(
        argv: list[str],
        *,
        cwd: str,
        stdout: int,
        stderr: int,
        shell: bool,
    ) -> _CompletedProcess:
        calls.append({"argv": argv, "cwd": cwd, "shell": shell})
        return _CompletedProcess(stdout=b"{}", stderr=b"")

    monkeypatch.setattr("ims_deadlock.g5_capture.subprocess.Popen", fake_popen)

    record = capture_g4_case(
        windows_bundle,
        output_root,
        "G4-HELD-01",
        "windows-token",
        cwd=repo,
    )

    expected_argv = [
        sys.executable,
        "-m",
        "ims_deadlock.g4_protocol",
        "--root",
        "cases/confirmation/g4",
        "run",
        "G4-HELD-01",
    ]
    assert calls == [{"argv": expected_argv, "cwd": str(repo), "shell": False}]
    assert record["argv"] == expected_argv
    assert record["bundle_root"] == str(absolute_bundle)
    assert (repo / "out" / "cases" / "G4-HELD-01" / "windows-token").is_dir()


def test_capture_rejects_non_frozen_root_token_before_mkdir_or_popen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    absolute_bundle = _complete_bundle(tmp_path)
    output_root = tmp_path / "out"
    wrong_root = tmp_path / "repo" / "wrong" / "root"
    wrong_root.parent.mkdir()
    wrong_root.symlink_to(absolute_bundle, target_is_directory=True)
    popen_calls = 0
    monkeypatch.chdir(tmp_path / "repo")

    def fake_popen(
        argv: list[str],
        *,
        cwd: str,
        stdout: int,
        stderr: int,
        shell: bool,
    ) -> _CompletedProcess:
        nonlocal popen_calls
        popen_calls += 1
        return _CompletedProcess(stdout=b"{}", stderr=b"")

    monkeypatch.setattr("ims_deadlock.g5_capture.subprocess.Popen", fake_popen)

    with pytest.raises(CaptureError, match="runtime_lock"):
        capture_g4_case(absolute_bundle, output_root, "G4-HELD-01", "absolute")
    with pytest.raises(CaptureError, match="runtime_lock"):
        capture_g4_case(Path("wrong/root"), output_root, "G4-HELD-01", "wrong")

    assert popen_calls == 0
    assert not (output_root / "cases").exists()


def test_capture_refuses_case_outside_freeze_or_runtime_lock_without_popen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = _complete_bundle(tmp_path)
    popen_calls = 0

    def fake_popen(
        argv: list[str],
        *,
        cwd: str,
        stdout: int,
        stderr: int,
        shell: bool,
    ) -> _CompletedProcess:
        nonlocal popen_calls
        popen_calls += 1
        return _CompletedProcess(stdout=b"{}", stderr=b"")

    monkeypatch.setattr("ims_deadlock.g5_capture.subprocess.Popen", fake_popen)
    with pytest.raises(CaptureError, match="not sealed"):
        capture_g4_case(bundle, tmp_path / "out", "G4-UNSEALED", "primary")

    runtime_path = bundle / "runtime_lock.json"
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    runtime["commands"] = [
        command
        for command in runtime["commands"]
        if not command.endswith(" run G4-HELD-01")
    ]
    runtime_path.write_text(
        json.dumps(runtime, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "ims_deadlock.g5_capture.check_g4_freeze",
        lambda root: SimpleNamespace(status="FROZEN", case_ids=("G4-HELD-01",)),
    )

    with pytest.raises(CaptureError, match="not authorized"):
        capture_g4_case(bundle, tmp_path / "out2", "G4-HELD-01", "primary")
    assert popen_calls == 0


def test_capture_refuses_unfrozen_bundle_and_inside_or_existing_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    draft_bundle = _complete_bundle(tmp_path / "draft", include_freeze_entry=False)
    frozen_bundle = _complete_bundle(tmp_path / "frozen")
    relative_frozen_bundle = frozen_bundle.relative_to(tmp_path / "frozen" / "repo")
    output_root = tmp_path / "out"
    existing_run = output_root / "cases" / "G4-HELD-01" / "primary"
    existing_run.mkdir(parents=True)

    with pytest.raises(CaptureError, match="requires FROZEN"):
        capture_g4_case(draft_bundle, tmp_path / "draft-out", "G4-HELD-01", "primary")
    with pytest.raises(CaptureError, match="inside the frozen bundle"):
        capture_g4_case(frozen_bundle, frozen_bundle / "g5", "G4-HELD-01", "primary")
    monkeypatch.chdir(tmp_path / "frozen" / "repo")
    with pytest.raises(CaptureError, match="already exists"):
        capture_g4_case(relative_frozen_bundle, output_root, "G4-HELD-01", "primary")


@pytest.mark.parametrize(
    ("case_id", "run_label"),
    [
        ("../bad", "primary"),
        ("G4-HELD-01", "../bad"),
        ("", "primary"),
        ("G4-HELD-01", ""),
        ("G4 HELD 01", "primary"),
    ],
)
def test_capture_rejects_unsafe_case_or_run_labels(
    tmp_path: Path, case_id: str, run_label: str
) -> None:
    bundle = _complete_bundle(tmp_path)

    with pytest.raises(ValueError, match="safe"):
        capture_g4_case(bundle, tmp_path / "out", case_id, run_label)


def test_capture_records_hard_timeout_without_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    absolute_bundle = _complete_bundle(tmp_path)
    bundle = absolute_bundle.relative_to(tmp_path / "repo")
    output_root = tmp_path / "out"
    processes: list[_TimeoutProcess] = []
    monkeypatch.chdir(tmp_path / "repo")

    def fake_popen(
        argv: list[str],
        *,
        cwd: str,
        stdout: int,
        stderr: int,
        shell: bool,
    ) -> _TimeoutProcess:
        assert shell is False
        process = _TimeoutProcess()
        processes.append(process)
        return process

    monkeypatch.setattr("ims_deadlock.g5_capture.subprocess.Popen", fake_popen)

    record = capture_g4_case(
        bundle,
        output_root,
        "G4-HELD-01",
        "timeout",
        timeout_seconds=0.01,
    )

    assert len(processes) == 1
    assert processes[0].killed is True
    assert record["timed_out"] is True
    assert record["timeout_seconds"] == 0.01
    assert record["exit_code"] is None
    assert record["stdout_canonical_json_sha256"] is None
    assert (output_root / "cases/G4-HELD-01/timeout/stdout.bin").read_bytes() == b""
    assert (output_root / "cases/G4-HELD-01/timeout/stderr.txt").read_bytes() == (
        b"terminated"
    )


def test_capture_cli_returns_nonzero_for_child_nonzero_or_timeout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    absolute_bundle = _complete_bundle(tmp_path)
    bundle = absolute_bundle.relative_to(tmp_path / "repo")
    output_root = tmp_path / "out"
    monkeypatch.chdir(tmp_path / "repo")

    monkeypatch.setattr(
        "ims_deadlock.g5_capture.subprocess.Popen",
        lambda argv, *, cwd, stdout, stderr, shell: _CompletedProcess(
            b'{"ok": false}', b"failed", returncode=7
        ),
    )

    assert (
        main(
            [
                "capture",
                "--root",
                str(bundle),
                "--output-root",
                str(output_root),
                "--run-label",
                "nonzero",
                "G4-HELD-01",
            ]
        )
        == 1
    )
    nonzero = json.loads(capsys.readouterr().out)
    assert nonzero["exit_code"] == 7

    monkeypatch.setattr(
        "ims_deadlock.g5_capture.subprocess.Popen",
        lambda argv, *, cwd, stdout, stderr, shell: _TimeoutProcess(),
    )
    assert (
        main(
            [
                "capture",
                "--root",
                str(bundle),
                "--output-root",
                str(output_root),
                "--run-label",
                "timeout-cli",
                "--timeout-seconds",
                "0.01",
                "G4-HELD-01",
            ]
        )
        == 1
    )
    timeout = json.loads(capsys.readouterr().out)
    assert timeout["timed_out"] is True


def test_capture_records_launch_oserror_without_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    absolute_bundle = _complete_bundle(tmp_path)
    bundle = absolute_bundle.relative_to(tmp_path / "repo")
    output_root = tmp_path / "out"
    launches = 0
    monkeypatch.chdir(tmp_path / "repo")

    def fake_popen(
        argv: list[str],
        *,
        cwd: str,
        stdout: int,
        stderr: int,
        shell: bool,
    ) -> _CompletedProcess:
        nonlocal launches
        launches += 1
        raise OSError("missing executable")

    monkeypatch.setattr("ims_deadlock.g5_capture.subprocess.Popen", fake_popen)

    with pytest.raises(CaptureError, match="launch failed"):
        capture_g4_case(bundle, output_root, "G4-HELD-01", "launch-error")

    run_dir = output_root / "cases" / "G4-HELD-01" / "launch-error"
    record = json.loads((run_dir / "record.json").read_text(encoding="utf-8"))
    assert launches == 1
    assert (run_dir / "stdout.bin").read_bytes() == b""
    assert (run_dir / "stderr.txt").read_bytes() == b""
    assert record["exit_code"] is None
    assert record["timed_out"] is False
    assert record["launch_error_type"] == "OSError"
    assert record["launch_error_message"] == "missing executable"
    assert record["stdout_raw_sha256"] == hashlib.sha256(b"").hexdigest()
    assert record["stderr_raw_sha256"] == hashlib.sha256(b"").hexdigest()


def test_capture_cli_returns_nonzero_for_launch_failure_with_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    absolute_bundle = _complete_bundle(tmp_path)
    bundle = absolute_bundle.relative_to(tmp_path / "repo")
    output_root = tmp_path / "out"
    monkeypatch.chdir(tmp_path / "repo")

    def fake_popen(
        argv: list[str],
        *,
        cwd: str,
        stdout: int,
        stderr: int,
        shell: bool,
    ) -> _CompletedProcess:
        raise OSError("missing executable")

    monkeypatch.setattr("ims_deadlock.g5_capture.subprocess.Popen", fake_popen)

    assert (
        main(
            [
                "capture",
                "--root",
                str(bundle),
                "--output-root",
                str(output_root),
                "--run-label",
                "launch-cli",
                "G4-HELD-01",
            ]
        )
        == 1
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["launch_error_type"] == "OSError"
    assert (
        output_root / "cases" / "G4-HELD-01" / "launch-cli" / "record.json"
    ).is_file()


def test_compare_capture_hashes_and_cli(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    primary_dir = tmp_path / "primary"
    repro_dir = tmp_path / "repro"
    primary_dir.mkdir()
    repro_dir.mkdir()
    base = {
        "schema_version": "ims-deadlock/g5-capture-record/v1",
        "case_id": "G4-HELD-01",
        "run_label": "primary",
        "argv": ["python", "-m", "ims_deadlock.g4_protocol"],
        "freeze_id": "G4-FREEZE-DEVELOPMENT-TEST",
        "git_head": "d" * 40,
        "stdout_raw_sha256": "a" * 64,
        "stdout_canonical_json_sha256": "b" * 64,
        "stderr_raw_sha256": "e" * 64,
    }
    (primary_dir / "record.json").write_text(json.dumps(base), encoding="utf-8")
    (repro_dir / "record.json").write_text(
        json.dumps({**base, "run_label": "repro"}), encoding="utf-8"
    )

    assert compare_capture_hashes(primary_dir, repro_dir)["match"] is True
    assert main(["compare", str(primary_dir), str(repro_dir)]) == 0
    assert json.loads(capsys.readouterr().out)["match"] is True

    (repro_dir / "record.json").write_text(
        json.dumps({**base, "run_label": "repro", "stdout_raw_sha256": "c" * 64}),
        encoding="utf-8",
    )
    assert compare_capture_hashes(primary_dir, repro_dir)["match"] is False
    assert main(["compare", str(primary_dir), str(repro_dir)]) == 1


def test_capture_writes_nonfinite_json_stdout_as_raw_bin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    absolute_bundle = _complete_bundle(tmp_path)
    bundle = absolute_bundle.relative_to(tmp_path / "repo")
    output_root = tmp_path / "out"
    monkeypatch.chdir(tmp_path / "repo")
    monkeypatch.setattr(
        "ims_deadlock.g5_capture.subprocess.Popen",
        lambda argv, *, cwd, stdout, stderr, shell: _CompletedProcess(
            b'{"value": NaN}', b""
        ),
    )

    record = capture_g4_case(bundle, output_root, "G4-HELD-01", "nan")

    run_dir = output_root / "cases" / "G4-HELD-01" / "nan"
    assert (run_dir / "stdout.bin").read_bytes() == b'{"value": NaN}'
    assert not (run_dir / "stdout.json").exists()
    assert record["stdout_canonical_json_sha256"] is None
    assert json.loads((run_dir / "record.json").read_text(encoding="utf-8")) == record


def test_compare_requires_stderr_case_canonical_argv_freeze_and_git_match(
    tmp_path: Path,
) -> None:
    primary_dir = tmp_path / "primary"
    repro_dir = tmp_path / "repro"
    primary_dir.mkdir()
    repro_dir.mkdir()
    base = {
        "schema_version": "ims-deadlock/g5-capture-record/v1",
        "case_id": "G4-HELD-01",
        "run_label": "primary",
        "argv": ["python", "-m", "ims_deadlock.g4_protocol", "run", "G4-HELD-01"],
        "freeze_id": "G4-FREEZE-DEVELOPMENT-TEST",
        "git_head": "d" * 40,
        "stdout_raw_sha256": "a" * 64,
        "stdout_canonical_json_sha256": "b" * 64,
        "stderr_raw_sha256": "e" * 64,
    }
    (primary_dir / "record.json").write_text(json.dumps(base), encoding="utf-8")

    for field, value in [
        ("case_id", "G4-HELD-02"),
        ("stdout_canonical_json_sha256", None),
        ("stderr_raw_sha256", "f" * 64),
        ("argv", ["python", "-m", "other"]),
        ("freeze_id", "OTHER-FREEZE"),
        ("git_head", "c" * 40),
    ]:
        (repro_dir / "record.json").write_text(
            json.dumps({**base, "run_label": "repro", field: value}),
            encoding="utf-8",
        )
        comparison = compare_capture_hashes(primary_dir, repro_dir)
        assert comparison["match"] is False
        assert comparison[f"{field}_match"] is False


def test_compare_invalid_schema_or_missing_hash_fields_cannot_match(
    tmp_path: Path,
) -> None:
    primary_dir = tmp_path / "primary"
    repro_dir = tmp_path / "repro"
    primary_dir.mkdir()
    repro_dir.mkdir()
    base = {
        "schema_version": "ims-deadlock/g5-capture-record/v1",
        "case_id": "G4-HELD-01",
        "argv": ["python", "-m", "ims_deadlock.g4_protocol"],
        "freeze_id": "G4-FREEZE-DEVELOPMENT-TEST",
        "git_head": "d" * 40,
        "stdout_raw_sha256": "a" * 64,
        "stdout_canonical_json_sha256": "b" * 64,
        "stderr_raw_sha256": "e" * 64,
    }
    (primary_dir / "record.json").write_text(json.dumps(base), encoding="utf-8")

    for invalid in [
        {**base, "schema_version": "wrong"},
        {**base, "stdout_raw_sha256": ""},
        {**base, "stdout_raw_sha256": None},
        {key: value for key, value in base.items() if key != "stderr_raw_sha256"},
    ]:
        (repro_dir / "record.json").write_text(
            json.dumps(invalid),
            encoding="utf-8",
        )
        comparison = compare_capture_hashes(primary_dir, repro_dir)
        assert comparison["match"] is False
        assert comparison["records_valid"] is False


def test_capture_reads_head_from_linked_worktree_common_refs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    absolute_bundle = _complete_bundle(tmp_path)
    bundle = absolute_bundle.relative_to(tmp_path / "repo")
    worktree = tmp_path / "worktree"
    common = tmp_path / "main.git"
    gitdir = common / "worktrees" / "linked"
    worktree.mkdir()
    gitdir.mkdir(parents=True)
    (worktree / ".git").write_text(f"gitdir: {gitdir}\n", encoding="utf-8")
    (gitdir / "commondir").write_text("../..\n", encoding="utf-8")
    (gitdir / "HEAD").write_text("ref: refs/heads/feature\n", encoding="utf-8")
    (common / "refs" / "heads").mkdir(parents=True)
    (common / "refs" / "heads" / "feature").write_text(
        "1" * 40 + "\n", encoding="utf-8"
    )
    (worktree / "cases").symlink_to(
        tmp_path / "repo" / "cases", target_is_directory=True
    )

    monkeypatch.setattr(
        "ims_deadlock.g5_capture.subprocess.Popen",
        lambda argv, *, cwd, stdout, stderr, shell: _CompletedProcess(b"{}", b""),
    )

    record = capture_g4_case(
        bundle, tmp_path / "out", "G4-HELD-01", "primary", cwd=worktree
    )

    assert record["git_head"] == "1" * 40
    assert record["git_branch"] == "feature"


@pytest.mark.parametrize("timeout_seconds", [0.0, -1.0])
def test_capture_rejects_nonpositive_timeout_threshold(
    tmp_path: Path, timeout_seconds: float
) -> None:
    bundle = _complete_bundle(tmp_path)

    with pytest.raises(ValueError, match="timeout_seconds"):
        capture_g4_case(
            bundle,
            tmp_path / "out",
            "G4-HELD-01",
            "primary",
            timeout_seconds=timeout_seconds,
        )
