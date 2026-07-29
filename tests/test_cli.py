import json
import subprocess
import sys
from typing import Any, cast


def run_cli(*args: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, "-m", "ims_deadlock.cli", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return cast("dict[str, object]", json.loads(completed.stdout))


def test_verify_case_cli_returns_versioned_certificate_json() -> None:
    payload = run_cli("verify-case", "C0")

    assert payload["schema_version"] == "ims-deadlock/v0"
    assert payload["command"] == "verify-case"
    assert payload["case_id"] == "C0"
    assert payload["deadlock"] is True
    certificate = cast("dict[str, Any]", payload["certificate"])
    assert certificate["kernel_jobs"] == ["j1", "j2"]


def test_quantify_cli_returns_exact_ctmc_values_for_builtin_c0() -> None:
    payload = run_cli("quantify", "C0")

    assert payload["schema_version"] == "ims-deadlock/v0"
    probabilities = cast("dict[str, float]", payload["deadlock_probability"])
    mean_times = cast("dict[str, float]", payload["mean_absorption_time"])
    assert probabilities["s0"] == 1.0
    assert mean_times["s0"] == 1.0
