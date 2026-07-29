"""Command-line entry points for deterministic IMS_deadlock JSON outputs."""

from __future__ import annotations

import argparse
import json
from typing import Any

from ims_deadlock.cases import load_builtin_case
from ims_deadlock.certificates import find_deadlock_certificate
from ims_deadlock.ctmc import AbsorbingCTMC, QuantitativeResult

SCHEMA_VERSION = "ims-deadlock/v0"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ims-deadlock")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("validate", "prove", "simulate", "verify-case"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("case_id")
    quantify = subparsers.add_parser("quantify")
    quantify.add_argument("case_id")

    args = parser.parse_args(argv)
    payload = _dispatch(args.command, args.case_id)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


def _dispatch(command: str, case_id: str) -> dict[str, Any]:
    if command == "validate":
        model, state = load_builtin_case(case_id)
        return _base(command, case_id) | {
            "model_id": model.id,
            "state_id": state.id,
            "valid": True,
        }
    if command in {"prove", "verify-case"}:
        model, state = load_builtin_case(case_id)
        certificate = find_deadlock_certificate(model, state)
        return _base(command, case_id) | {
            "model_id": model.id,
            "state_id": state.id,
            "deadlock": certificate is not None,
            "certificate": certificate.to_json_dict() if certificate else None,
        }
    if command == "quantify":
        result = _builtin_quantification(case_id)
        return _base(command, case_id) | result.to_json_dict()
    if command == "simulate":
        return _base(command, case_id) | {
            "status": "not_implemented",
            "reason": "DES simulation is intentionally deferred until case freeze.",
        }
    msg = f"unsupported command {command!r}"
    raise ValueError(msg)


def _base(command: str, case_id: str) -> dict[str, str]:
    return {
        "schema_version": SCHEMA_VERSION,
        "command": command,
        "case_id": case_id.upper(),
    }


def _builtin_quantification(case_id: str) -> QuantitativeResult:
    if case_id.upper() == "C0":
        return AbsorbingCTMC(
            transient_states=("s0",),
            completion_rates={},
            deadlock_rates={("s0", "dead"): 1.0},
            transient_rates={},
        ).solve()
    if case_id.upper() == "C1":
        return AbsorbingCTMC(
            transient_states=("s0",),
            completion_rates={("s0", "done"): 1.0},
            deadlock_rates={},
            transient_rates={},
        ).solve()
    msg = f"no built-in quantification for {case_id!r}"
    raise ValueError(msg)


if __name__ == "__main__":
    raise SystemExit(main())
