"""Command-line entry points for deterministic IMS_deadlock JSON outputs."""

from __future__ import annotations

import argparse
import json
from typing import Any

from ims_deadlock.analysis import analyze_case
from ims_deadlock.cases import CaseSpec, load_case_spec
from ims_deadlock.ctmc import DoobConditionedGenerator
from ims_deadlock.engine import simulate
from ims_deadlock.model import validate_model_state
from ims_deadlock.stochastic import estimate_competing_absorption

SCHEMA_VERSION = "ims-deadlock/cli/v1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ims-deadlock")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("validate", "prove"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("case_id")
    simulate_parser = subparsers.add_parser("simulate")
    simulate_parser.add_argument("case_id")
    simulate_parser.add_argument(
        "--mode", choices=("calendar", "ctmc"), default="calendar"
    )
    simulate_parser.add_argument("--samples", type=int, default=1000)
    simulate_parser.add_argument("--seed", type=int, default=0)
    simulate_parser.add_argument("--initial-state")

    verify_case = subparsers.add_parser("verify-case")
    verify_case.add_argument("case_id")
    verify_case.add_argument("--max-states", type=int, default=128)

    quantify = subparsers.add_parser("quantify")
    quantify.add_argument("case_id")

    args = parser.parse_args(argv)
    payload = _dispatch(args)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


def _dispatch(args: argparse.Namespace) -> dict[str, Any]:
    command = str(args.command)
    case_id = str(args.case_id)
    spec = load_case_spec(case_id)
    if command == "validate":
        model, state = spec.model, spec.initial_state
        validation = validate_model_state(model, state)
        return _base(command, case_id) | {
            "case_schema_version": spec.schema_version,
            "case_status": spec.status,
            "model_id": model.id,
            "state_id": state.id,
            **validation.to_json_dict(),
        }
    if command == "prove":
        analysis = analyze_case(spec)
        certificate = dict(analysis["certificate"])
        return _base(command, case_id) | {
            "case_schema_version": spec.schema_version,
            "case_status": spec.status,
            "model_id": spec.model.id,
            "state_id": spec.initial_state.id,
            "evidence_kind": "program_observation_not_mathematical_proof",
            "analysis_schema_version": analysis["analysis_schema_version"],
            "deadlock": certificate["available"],
            "certificate": certificate["certificate"],
            "certificate_state_id": certificate["state_id"],
            "reachability_witness": certificate["reachability_witness"],
            "reason": certificate["reason"],
            "lts": analysis["lts"],
        }
    if command == "verify-case":
        return _base(command, case_id) | analyze_case(spec, max_states=args.max_states)
    if command == "quantify":
        if spec.ctmc is None:
            return _base(command, case_id) | {
                "case_schema_version": spec.schema_version,
                "case_status": spec.status,
                "analysis_mode": "unavailable",
                "available": False,
                "reason": "case_has_no_builtin_ctmc",
                "case_bound": False,
                "ctmc_provenance": None,
                "deadlock_probability": {},
                "mean_absorption_time": {},
                "exact_solution": {"available": False},
                "doob_h_generator": {"available": False},
                "sensitivity": {"available": False, "reason": "ctmc_unavailable"},
            }
        ctmc_result = spec.ctmc.solve()
        doob_h = spec.ctmc.deadlock_conditioned_generator()
        provenance = spec.ctmc_provenance or "fixture_unverified"
        return _base(command, case_id) | {
            "case_schema_version": spec.schema_version,
            "case_status": spec.status,
            "analysis_mode": provenance,
            "available": True,
            "case_bound": provenance == "derived",
            "ctmc_provenance": provenance,
            **ctmc_result.to_json_dict(),
            "partition_summary": {
                "transient_state_count": len(spec.ctmc.transient_states),
                "deadlock_absorber_count": len(
                    {target for _source, target in spec.ctmc.deadlock_rates}
                ),
                "completion_absorber_count": len(
                    {target for _source, target in spec.ctmc.completion_rates}
                ),
                "unclassified_recurrent_class_count": 0,
                "a_abs_validated_for_explicit_partition": True,
            },
            "generator_summary": {
                "transient_states": list(spec.ctmc.transient_states),
                "transient_rates": _rates_to_json(spec.ctmc.transient_rates),
                "deadlock_rates": _rates_to_json(spec.ctmc.deadlock_rates),
                "completion_rates": _rates_to_json(spec.ctmc.completion_rates),
                "generator_provenance": ctmc_result.generator_provenance,
                "ctmc_provenance": provenance,
            },
            "exact_solution": {
                "available": True,
                "evidence_kind": "exact_finite_ctmc_linear_system_solution",
                "generator_provenance": ctmc_result.generator_provenance,
                "ctmc_provenance": provenance,
                "case_bound": provenance == "derived",
                "residuals": {
                    "committor_inf_norm": ctmc_result.committor_residual_inf_norm,
                    "mean_time_inf_norm": ctmc_result.mean_time_residual_inf_norm,
                },
                "probability_bounds": ctmc_result.probability_bounds,
                "probability_bounds_valid": ctmc_result.probability_bounds_valid,
            },
            "doob_h_generator": _doob_to_json(doob_h, provenance=provenance),
            "sensitivity": {
                "available": False,
                "reason": "derivative_rate_metadata_not_supplied",
                "required_metadata": [
                    "derivative_completion_rates",
                    "derivative_deadlock_rates",
                    "derivative_transient_rates",
                ],
            },
            "des_crosscheck": {
                "available": False,
                "reason": "run_simulate_ctmc_with_preregistered_samples_and_seed",
            },
        }
    if command == "simulate":
        if args.mode == "ctmc":
            return _simulate_ctmc(spec, case_id, args)
        simulation_result = simulate(
            spec.model,
            spec.initial_state,
            spec.transitions,
            spec.calendar,
        )
        return _base(command, case_id) | {
            "case_schema_version": spec.schema_version,
            "case_status": spec.status,
            "simulation_mode": "calendar",
            "available": simulation_result.terminal_classification
            not in {
                "nonconfluent_zero_time_closure",
                "zero_time_closure_nontermination",
            },
            "terminal_classification": simulation_result.terminal_classification,
            "unfinished_jobs": list(simulation_result.unfinished_jobs),
            "final_state_id": simulation_result.final_state.id,
            "final_state_mode_by_job": dict(
                sorted(simulation_result.final_state.mode_by_job.items())
            ),
            "canonical_trace": list(simulation_result.canonical_trace),
            "closure_branches": [
                branch.to_json_dict() for branch in simulation_result.closure_branches
            ],
        }
    msg = f"unsupported command {command!r}"
    raise ValueError(msg)


def _simulate_ctmc(
    spec: CaseSpec,
    case_id: str,
    args: argparse.Namespace,
) -> dict[str, Any]:
    provenance = spec.ctmc_provenance or "fixture_unverified"
    if spec.ctmc is None:
        return _base("simulate", case_id) | {
            "case_schema_version": spec.schema_version,
            "case_status": spec.status,
            "simulation_mode": "ctmc",
            "available": False,
            "reason": "case_has_no_builtin_ctmc",
            "case_bound": False,
            "ctmc_provenance": None,
        }
    initial_state = args.initial_state or spec.ctmc.transient_states[0]
    estimate = estimate_competing_absorption(
        spec.ctmc,
        initial_state=initial_state,
        sample_count=args.samples,
        master_seed=args.seed,
    )
    return _base("simulate", case_id) | {
        "case_schema_version": spec.schema_version,
        "case_status": spec.status,
        "simulation_mode": "ctmc",
        "available": True,
        "initial_state": initial_state,
        "case_bound": provenance == "derived",
        "ctmc_provenance": provenance,
        "generator_provenance": estimate.generator_provenance,
        "sample_count": estimate.sample_count,
        "deadlock_count": estimate.deadlock_count,
        "deadlock_estimate": estimate.deadlock_estimate,
        "wilson_95_ci": list(estimate.wilson_95_ci),
        "mean_absorption_time": estimate.mean_absorption_time,
        "stream_manifest": estimate.stream_manifest,
    }


def _doob_to_json(
    doob_h: DoobConditionedGenerator,
    *,
    provenance: str,
) -> dict[str, Any]:
    return {
        "available": True,
        "generator_provenance": doob_h.generator_provenance,
        "ctmc_provenance": provenance,
        "case_bound": provenance == "derived",
        "transient_states": list(doob_h.transient_states),
        "completion_rates": _rates_to_json(doob_h.completion_rates),
        "deadlock_rates": _rates_to_json(doob_h.deadlock_rates),
        "transient_rates": _rates_to_json(doob_h.transient_rates),
        "row_sum_residual_inf_norm": doob_h.row_sum_residual_inf_norm,
        "domain": doob_h.domain,
        "excluded_transient_states": list(doob_h.excluded_transient_states),
    }


def _rates_to_json(rates: dict[tuple[str, str], float]) -> list[list[object]]:
    return [[source, target, rate] for (source, target), rate in sorted(rates.items())]


def _base(command: str, case_id: str) -> dict[str, str]:
    return {
        "schema_version": SCHEMA_VERSION,
        "command": command,
        "case_id": case_id.upper(),
    }


if __name__ == "__main__":
    raise SystemExit(main())
