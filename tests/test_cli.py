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

    assert payload["schema_version"] == "ims-deadlock/cli/v1"
    assert payload["command"] == "verify-case"
    assert payload["case_id"] == "C0"
    assert payload["analysis_schema_version"] == "ims-deadlock/analysis/v1"
    certificate_payload = cast("dict[str, Any]", payload["certificate"])
    assert certificate_payload["available"] is True
    certificate = cast("dict[str, Any]", certificate_payload["certificate"])
    assert certificate["kernel_jobs"] == ["j1", "j2"]
    lts = cast("dict[str, Any]", payload["lts"])
    petri_bridge = cast("dict[str, Any]", payload["petri_bridge"])
    unavailable = cast("dict[str, Any]", payload["unavailable"])
    assert lts["initial_state_id"] == "s0"
    assert petri_bridge["status"] == "exact_ims_sip1_wait_snapshot_duality"
    assert petri_bridge["available"] is True
    assert petri_bridge["corresponding_siphon"] == {
        "type": "state_induced_wait_snapshot",
        "places": ["free:r1", "free:r2"],
        "empty": True,
        "minimal": True,
        "core_jobs": ["j1", "j2"],
        "core_resources": ["r1", "r2"],
    }
    assert unavailable["siphon"] is None


def test_verify_case_cli_honors_max_states() -> None:
    payload = run_cli("verify-case", "C2", "--max-states", "1")

    lts = cast("dict[str, Any]", payload["lts"])
    supervisor = cast("dict[str, Any]", payload["supervisor"])
    assert payload["schema_version"] == "ims-deadlock/cli/v1"
    assert lts["max_states"] == 1
    assert lts["truncated"] is True
    assert supervisor["available"] is False
    assert supervisor["reason"] == "lts_truncated"


def test_prove_cli_uses_reachable_structural_analysis_certificate() -> None:
    payload = run_cli("prove", "C0")

    assert payload["schema_version"] == "ims-deadlock/cli/v1"
    assert payload["evidence_kind"] == "program_observation_not_mathematical_proof"
    assert payload["deadlock"] is True
    assert payload["certificate_state_id"] == "s0"
    assert payload["reachability_witness"] == []
    certificate = cast("dict[str, Any]", payload["certificate"])
    assert certificate["kernel_jobs"] == ["j1", "j2"]


def test_quantify_cli_returns_exact_ctmc_values_for_builtin_c0() -> None:
    payload = run_cli("quantify", "C0")

    assert payload["schema_version"] == "ims-deadlock/cli/v1"
    probabilities = cast("dict[str, float]", payload["deadlock_probability"])
    mean_times = cast("dict[str, float]", payload["mean_absorption_time"])
    assert probabilities["s0"] == 1.0
    assert mean_times["s0"] == 1.0
    assert payload["analysis_mode"] == "fixture_unverified"
    assert payload["case_bound"] is False
    exact = cast("dict[str, Any]", payload["exact_solution"])
    residuals = cast("dict[str, float]", exact["residuals"])
    doob = cast("dict[str, Any]", payload["doob_h_generator"])
    sensitivity = cast("dict[str, Any]", payload["sensitivity"])
    partition = cast("dict[str, Any]", payload["partition_summary"])
    generator = cast("dict[str, Any]", payload["generator_summary"])
    assert exact["evidence_kind"] == "exact_finite_ctmc_linear_system_solution"
    assert residuals["committor_inf_norm"] == 0.0
    assert exact["probability_bounds_valid"] is True
    assert doob["available"] is True
    assert doob["deadlock_rates"] == [["s0", "dead", 1.0]]
    assert doob["transient_rates"] == []
    assert partition == {
        "transient_state_count": 1,
        "deadlock_absorber_count": 1,
        "completion_absorber_count": 0,
        "unclassified_recurrent_class_count": 0,
        "a_abs_validated_for_explicit_partition": True,
    }
    assert generator["deadlock_rates"] == [["s0", "dead", 1.0]]
    assert generator["ctmc_provenance"] == "fixture_unverified"
    assert sensitivity == {
        "available": False,
        "reason": "derivative_rate_metadata_not_supplied",
        "required_metadata": [
            "derivative_completion_rates",
            "derivative_deadlock_rates",
            "derivative_transient_rates",
        ],
    }


def test_quantify_cli_reports_unavailable_for_case_without_ctmc() -> None:
    payload = run_cli("quantify", "C2")

    assert payload["schema_version"] == "ims-deadlock/cli/v1"
    assert payload["available"] is False
    assert payload["reason"] == "case_has_no_builtin_ctmc"
    assert payload["deadlock_probability"] == {}
    assert payload["doob_h_generator"] == {"available": False}


def test_validate_cli_reports_real_validator_result() -> None:
    payload = run_cli("validate", "C0")

    assert payload["schema_version"] == "ims-deadlock/cli/v1"
    assert payload["valid"] is True
    assert payload["issues"] == []


def test_simulate_cli_returns_terminal_classification_json() -> None:
    payload = run_cli("simulate", "C0")

    assert payload["schema_version"] == "ims-deadlock/cli/v1"
    assert payload["command"] == "simulate"
    assert payload["case_id"] == "C0"
    assert payload["simulation_mode"] == "calendar"
    assert payload["available"] is True
    assert payload["terminal_classification"] == "capacity_deadlock"
    assert payload["unfinished_jobs"] == ["j1", "j2"]
    assert payload["closure_branches"] == []


def test_simulate_cli_ctmc_mode_reports_independent_stream_manifest() -> None:
    payload = run_cli(
        "simulate",
        "C0",
        "--mode",
        "ctmc",
        "--samples",
        "20",
        "--seed",
        "123",
        "--initial-state",
        "s0",
    )

    manifest = cast("dict[str, Any]", payload["stream_manifest"])
    ci = cast("list[float]", payload["wilson_95_ci"])
    assert payload["schema_version"] == "ims-deadlock/cli/v1"
    assert payload["simulation_mode"] == "ctmc"
    assert payload["available"] is True
    assert payload["initial_state"] == "s0"
    assert payload["sample_count"] == 20
    assert payload["deadlock_count"] == 20
    assert payload["deadlock_estimate"] == 1.0
    assert ci[0] <= payload["deadlock_estimate"] <= ci[1]
    assert manifest["master_seed"] == 123
    assert manifest["sample_count"] == 20
    assert manifest["replication_seed_digest"]


def test_simulate_cli_ctmc_mode_reports_unavailable_without_builtin_ctmc() -> None:
    payload = run_cli("simulate", "C2", "--mode", "ctmc")

    assert payload["schema_version"] == "ims-deadlock/cli/v1"
    assert payload["simulation_mode"] == "ctmc"
    assert payload["available"] is False
    assert payload["reason"] == "case_has_no_builtin_ctmc"
