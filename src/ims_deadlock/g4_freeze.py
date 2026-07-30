"""Read-only integrity checker for the G4 preregistration freeze bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Literal

FREEZE_CHECK_SCHEMA_VERSION = "ims-deadlock/g4-freeze-check/v1"
G4_DISCOVERY_CASE_IDS = (
    "C0",
    "C1",
    "C2",
    "C3",
    "C4",
    "C5",
    "C5_DAG",
)
G4_DISCOVERY_FAMILY_IDS = (
    "BIX1-SAT",
    "BIX2-PERSIST",
)
G4_REQUIRED_FAMILIES = (
    "G4-ADVERSARIAL-BOUNDARY",
    "G4-B05-SUPERVISOR-COMPARATOR",
    "G4-CRP-OUTSIDE-S4PR",
    "G4-CRP-S4PR-AGREE",
    "G4-CRP-UNREACHABLE-CANDIDATE",
    "G4-IMS-PARAMETER-GRID",
    "G4-L30-RESOURCE-BASELINE",
    "G4-MEDIUM-ISLAND-REBUILD",
    "G4-RECORDER-TARGET-QUANTIFICATION",
)
G4_REQUIRED_BASELINES = (
    "B05_ADAPTED_MONITOR_COVER",
    "L30_SUPPLIED_SUFFICIENT_INEQUALITIES",
    "L31_CRP_EVIDENCE_PROFILE",
    "L32_L33_FIXED_RECORDER_TARGET",
    "L34_L35_FIXED_NIS_FILTER",
    "banker_safety_sequence",
    "delete_backflow_repair",
    "exact_max_nonblocking_supervisor",
    "simple_directed_cycle",
    "state_dependent_knot",
    "wait_snapshot_siphon",
)
G4_REQUIRED_METRICS = (
    "certificate_minimality",
    "conditioned_path_mass",
    "des_confidence_interval",
    "exact_deadlock_probability",
    "mean_absorption_time",
    "rare_event_efficiency",
    "supervisor_due_date_risk_change",
    "supervisor_makespan_loss",
    "supervisor_throughput_loss",
    "supervisor_wip_change",
    "theorem_prediction_correctness",
)
G4_GRID_CELL_IDS = (
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
)
G4_GRID_PREDICTION_CLASS = (
    "acyclic_controls_safe_and_bidirectional_cells_structurally_exposed"
)

_REQUIRED_ARTIFACTS = (
    "case_manifest.json",
    "predictions.json",
    "baseline_applicability.json",
    "metrics_schema.json",
    "runtime_lock.json",
    "random_stream_manifest.json",
    "experiment_scripts_manifest.json",
    "theory_manifest.json",
    "exclusions.json",
    "FREEZE_ENTRY.json",
)
_ARTIFACT_HASH_FIELDS = {
    "case_manifest_sha256": "case_manifest.json",
    "prediction_sheet_sha256": "predictions.json",
    "baseline_manifest_sha256": "baseline_applicability.json",
    "metric_schema_sha256": "metrics_schema.json",
    "runtime_lock_sha256": "runtime_lock.json",
    "random_stream_manifest_sha256": "random_stream_manifest.json",
    "experiment_script_manifest_sha256": "experiment_scripts_manifest.json",
    "theory_manifest_sha256": "theory_manifest.json",
    "exclusions_sha256": "exclusions.json",
}
_FORBIDDEN_RESULT_KEYS = frozenset(
    {
        "confirmation_result",
        "estimate",
        "fail",
        "match",
        "measured",
        "mismatch_count",
        "observed_result",
        "pass",
        "result",
    }
)
_RESULT_DIRECTORY_NAMES = frozenset(
    {
        "confirmation_results",
        "outputs",
        "results",
    }
)

FreezeStatus = Literal["FROZEN", "NOT_FROZEN"]


@dataclass(frozen=True)
class FreezeCheckResult:
    """Versioned, no-result integrity status for one G4 bundle."""

    status: FreezeStatus
    errors: tuple[str, ...]
    case_ids: tuple[str, ...]
    artifact_hashes: Mapping[str, str]
    confirmation_results_inspected: bool | None
    schema_version: str = FREEZE_CHECK_SCHEMA_VERSION

    def to_json_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "errors": list(self.errors),
            "case_ids": list(self.case_ids),
            "artifact_hashes": dict(sorted(self.artifact_hashes.items())),
            "confirmation_results_inspected": (self.confirmation_results_inspected),
        }


def canonical_json_sha256(payload: object) -> str:
    """Hash a JSON value using the project canonical semantic encoding."""

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def check_g4_freeze(root: Path) -> FreezeCheckResult:
    """Read, hash, and validate a G4 bundle without executing its cases."""

    bundle_root = root.resolve()
    errors: list[str] = []
    documents: dict[str, Mapping[str, Any]] = {}
    computed_hashes: dict[str, str] = {}

    for filename in _REQUIRED_ARTIFACTS:
        path = bundle_root / filename
        if not path.is_file():
            errors.append(f"missing required artifact {filename}")
            continue
        payload = _load_json_object(path, errors)
        if payload is None:
            continue
        documents[filename] = payload
        _reject_result_keys(payload, filename, errors)
        if filename != "FREEZE_ENTRY.json":
            computed_hashes[filename] = canonical_json_sha256(payload)

    _reject_result_directories(bundle_root, errors)

    case_ids: tuple[str, ...] = ()
    case_hashes: dict[str, str] = {}
    manifest = documents.get("case_manifest.json")
    if manifest is not None:
        case_ids, case_hashes = _validate_case_manifest(
            bundle_root,
            manifest,
            errors,
        )

    predictions = documents.get("predictions.json")
    if predictions is not None:
        _validate_predictions(predictions, case_ids, errors)
    baselines = documents.get("baseline_applicability.json")
    if baselines is not None:
        _validate_baselines(baselines, case_ids, errors)
    metrics = documents.get("metrics_schema.json")
    if metrics is not None:
        _validate_metrics(metrics, case_ids, errors)
    runtime = documents.get("runtime_lock.json")
    if runtime is not None:
        _validate_runtime_lock(runtime, case_ids, errors)
    random_streams = documents.get("random_stream_manifest.json")
    if random_streams is not None:
        _validate_random_streams(random_streams, case_ids, errors)
    if metrics is not None and random_streams is not None:
        _validate_metric_stream_consistency(
            metrics,
            random_streams,
            case_ids,
            errors,
        )

    repository_root = _repository_root(bundle_root, errors)
    scripts = documents.get("experiment_scripts_manifest.json")
    if scripts is not None and repository_root is not None:
        _validate_file_manifest(
            scripts,
            repository_root=repository_root,
            expected_schema="ims-deadlock/g4-experiment-scripts/v1",
            require_entrypoints=True,
            errors=errors,
        )
    theory = documents.get("theory_manifest.json")
    if theory is not None and repository_root is not None:
        _validate_file_manifest(
            theory,
            repository_root=repository_root,
            expected_schema="ims-deadlock/g4-theory-manifest/v1",
            require_entrypoints=False,
            errors=errors,
        )
    exclusions = documents.get("exclusions.json")
    if exclusions is not None:
        _validate_exclusions(exclusions, errors)

    inspected: bool | None = None
    freeze_entry = documents.get("FREEZE_ENTRY.json")
    if freeze_entry is not None:
        inspected = _validate_freeze_entry(
            freeze_entry,
            documents=documents,
            computed_hashes=computed_hashes,
            case_ids=case_ids,
            case_hashes=case_hashes,
            runtime=runtime,
            errors=errors,
        )

    status: FreezeStatus = "FROZEN" if not errors else "NOT_FROZEN"
    return FreezeCheckResult(
        status=status,
        errors=tuple(errors),
        case_ids=case_ids,
        artifact_hashes={
            field: computed_hashes.get(filename, "")
            for field, filename in _ARTIFACT_HASH_FIELDS.items()
        },
        confirmation_results_inspected=inspected,
    )


def _validate_case_manifest(
    bundle_root: Path,
    manifest: Mapping[str, Any],
    errors: list[str],
) -> tuple[tuple[str, ...], dict[str, str]]:
    _require_schema(
        manifest,
        "ims-deadlock/g4-case-manifest/v1",
        "case manifest",
        errors,
    )
    rows = _list_of_objects(manifest.get("cases"), "case manifest cases", errors)
    case_ids: list[str] = []
    families: list[str] = []
    hashes: dict[str, str] = {}
    for index, row in enumerate(rows):
        label = f"case manifest row {index}"
        case_id = _nonempty_string(row.get("case_id"), f"{label} case_id", errors)
        family = _nonempty_string(row.get("family"), f"{label} family", errors)
        relative = _nonempty_string(row.get("path"), f"{label} path", errors)
        declared_hash = _sha256_string(row.get("sha256"), f"{label} sha256", errors)
        if row.get("hash_mode") != "canonical_json":
            errors.append(f"{label} hash_mode must be canonical_json")
        if case_id is None or family is None or relative is None:
            continue
        case_ids.append(case_id)
        families.append(family)
        path = _safe_relative_path(bundle_root, relative, bundle_root, errors)
        if path is None or not path.is_file():
            if path is not None:
                errors.append(f"{label} file does not exist: {relative}")
            continue
        payload = _load_json_object(path, errors)
        if payload is None:
            continue
        actual_hash = canonical_json_sha256(payload)
        hashes[case_id] = actual_hash
        if declared_hash is not None and actual_hash != declared_hash:
            errors.append(f"{label} case hash mismatch")
        _validate_confirmation_case_payload(
            payload,
            expected_case_id=case_id,
            expected_family=family,
            label=label,
            errors=errors,
        )

    if len(set(case_ids)) != len(case_ids):
        errors.append("case manifest case IDs must be unique")
    if len(set(families)) != len(families):
        errors.append("case manifest must contain exactly one case per G4 family")
    if set(families) != set(G4_REQUIRED_FAMILIES):
        errors.append("case manifest does not contain all required G4 families")
    return tuple(sorted(set(case_ids))), hashes


def _validate_confirmation_case_payload(
    payload: Mapping[str, Any],
    *,
    expected_case_id: str,
    expected_family: str,
    label: str,
    errors: list[str],
) -> None:
    _reject_result_keys(payload, label, errors)
    _require_schema(
        payload,
        "ims-deadlock/confirmation-case/v1",
        label,
        errors,
    )
    if payload.get("case_id") != expected_case_id:
        errors.append(f"{label} payload case_id mismatch")
    if payload.get("family") != "G4":
        errors.append(f"{label} payload family must be G4")
    if payload.get("held_out") is not True:
        errors.append(f"{label} must declare held_out=true")
    if payload.get("protocol") != "g4_confirmation_freeze_v1":
        errors.append(f"{label} has an unsupported protocol")
    contamination = payload.get("contamination")
    if not isinstance(contamination, dict):
        errors.append(f"{label} contamination must be an object")
    else:
        if contamination.get("derived_from_discovery_case") is not False:
            errors.append(f"{label} must not be derived from discovery")
        if contamination.get("provenance") != "independent_preregistration":
            errors.append(f"{label} must use independent preregistration provenance")
        if not _matches_string_set(
            contamination.get("excluded_discovery_case_ids"),
            G4_DISCOVERY_CASE_IDS,
        ):
            errors.append(f"{label} discovery case exclusions are incomplete")
        if not _matches_string_set(
            contamination.get("excluded_discovery_family_ids"),
            G4_DISCOVERY_FAMILY_IDS,
        ):
            errors.append(f"{label} discovery family exclusions are incomplete")
    input_payload = payload.get("input_payload")
    if not isinstance(input_payload, dict):
        errors.append(f"{label} input_payload must be an object")
    else:
        if input_payload.get("g4_family") != expected_family:
            errors.append(f"{label} g4_family does not match the case manifest")
        from ims_deadlock.g4_protocol import parse_g4_protocol_input

        try:
            parse_g4_protocol_input(
                input_payload,
                case_id=expected_case_id,
                expected_family=expected_family,
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{label} protocol input is not executable: {exc}")


def _validate_predictions(
    payload: Mapping[str, Any],
    case_ids: tuple[str, ...],
    errors: list[str],
) -> None:
    _require_schema(
        payload,
        "ims-deadlock/g4-predictions/v1",
        "prediction sheet",
        errors,
    )
    _reject_result_keys(payload, "prediction sheet", errors)
    rows = _list_of_objects(payload.get("predictions"), "predictions", errors)
    predicted_ids: list[str] = []
    for index, row in enumerate(rows):
        label = f"prediction row {index}"
        case_id = _nonempty_string(row.get("case_id"), f"{label} case_id", errors)
        for field in (
            "prediction_class",
            "theory_scope",
            "falsifier",
            "scoring_rule",
        ):
            _nonempty_string(row.get(field), f"{label} {field}", errors)
        evidence = row.get("required_evidence")
        if not _nonempty_string_list(evidence):
            errors.append(f"{label} required_evidence must be a nonempty string list")
        if row.get("prediction_class") == G4_GRID_PREDICTION_CLASS:
            _validate_grid_cell_predictions(
                row.get("cell_predictions"),
                label,
                errors,
            )
        if case_id is not None:
            predicted_ids.append(case_id)
    if len(set(predicted_ids)) != len(predicted_ids):
        errors.append("prediction case IDs must be unique")
    if set(predicted_ids) != set(case_ids):
        errors.append("prediction sheet must contain every frozen case exactly once")


def _validate_grid_cell_predictions(
    value: object,
    label: str,
    errors: list[str],
) -> None:
    if not isinstance(value, dict):
        errors.append(f"{label} cell_predictions must be an object")
        return
    if set(value) != set(G4_GRID_CELL_IDS):
        errors.append(f"{label} cell_predictions must cover the exact frozen grid")
    for cell_id, decision in value.items():
        cell_label = f"{label} cell {cell_id}"
        if not isinstance(decision, dict):
            errors.append(f"{cell_label} prediction must be an object")
            continue
        if set(decision) != {"expected_reachable_closed_core", "rationale"}:
            errors.append(
                f"{cell_label} must contain exactly "
                "expected_reachable_closed_core and rationale"
            )
        if not isinstance(decision.get("expected_reachable_closed_core"), bool):
            errors.append(
                f"{cell_label} expected_reachable_closed_core must be boolean"
            )
        _nonempty_string(decision.get("rationale"), f"{cell_label} rationale", errors)


def _validate_baselines(
    payload: Mapping[str, Any],
    case_ids: tuple[str, ...],
    errors: list[str],
) -> None:
    _require_schema(
        payload,
        "ims-deadlock/g4-baselines/v1",
        "baseline manifest",
        errors,
    )
    rows = _list_of_objects(payload.get("applicability"), "baseline rows", errors)
    seen: list[str] = []
    for index, row in enumerate(rows):
        label = f"baseline row {index}"
        case_id = _nonempty_string(row.get("case_id"), f"{label} case_id", errors)
        decisions = row.get("baselines")
        if not isinstance(decisions, dict):
            errors.append(f"{label} baselines must be an object")
            continue
        if set(decisions) != set(G4_REQUIRED_BASELINES):
            errors.append(f"{label} must decide every required baseline")
        for baseline, decision in decisions.items():
            if not isinstance(decision, dict):
                errors.append(f"{label} baseline {baseline} must be an object")
                continue
            if not isinstance(decision.get("applicable"), bool):
                errors.append(f"{label} baseline {baseline} applicable must be boolean")
            _nonempty_string(
                decision.get("reason"),
                f"{label} baseline {baseline} reason",
                errors,
            )
            if not _nonempty_string_list(decision.get("required_evidence")):
                errors.append(
                    f"{label} baseline {baseline} required_evidence must be nonempty"
                )
        if case_id is not None:
            seen.append(case_id)
    if len(set(seen)) != len(seen) or set(seen) != set(case_ids):
        errors.append("baseline manifest must contain every frozen case exactly once")


def _validate_metrics(
    payload: Mapping[str, Any],
    case_ids: tuple[str, ...],
    errors: list[str],
) -> None:
    _require_schema(
        payload,
        "ims-deadlock/g4-metrics/v1",
        "metric schema",
        errors,
    )
    rows = _list_of_objects(payload.get("metrics"), "metric rows", errors)
    metric_ids: list[str] = []
    for index, row in enumerate(rows):
        label = f"metric row {index}"
        metric_id = _nonempty_string(
            row.get("metric_id"),
            f"{label} metric_id",
            errors,
        )
        for field in ("definition", "unit", "denominator"):
            _nonempty_string(row.get(field), f"{label} {field}", errors)
        decisions = row.get("applicability_by_case")
        if not isinstance(decisions, dict):
            errors.append(f"{label} applicability_by_case must be an object")
        else:
            if set(decisions) != set(case_ids):
                errors.append(f"{label} must decide applicability for every case")
            for case_id, decision in decisions.items():
                if not isinstance(decision, dict):
                    errors.append(
                        f"{label} applicability for {case_id} must be an object"
                    )
                    continue
                if not isinstance(decision.get("applicable"), bool):
                    errors.append(
                        f"{label} applicability for {case_id} must be boolean"
                    )
                _nonempty_string(
                    decision.get("reason"),
                    f"{label} applicability reason for {case_id}",
                    errors,
                )
        if metric_id is not None:
            metric_ids.append(metric_id)
    if len(set(metric_ids)) != len(metric_ids):
        errors.append("metric IDs must be unique")
    if set(metric_ids) != set(G4_REQUIRED_METRICS):
        errors.append("metric schema must define every required metric")


def _validate_runtime_lock(
    payload: Mapping[str, Any],
    case_ids: tuple[str, ...],
    errors: list[str],
) -> None:
    _require_schema(
        payload,
        "ims-deadlock/g4-runtime-lock/v1",
        "runtime lock",
        errors,
    )
    _commit_string(payload.get("implementation_commit"), "runtime lock commit", errors)
    _nonempty_string(payload.get("platform"), "runtime lock platform", errors)
    python = payload.get("python")
    if not isinstance(python, dict):
        errors.append("runtime lock python must be an object")
    else:
        _nonempty_string(
            python.get("executable"),
            "runtime lock Python executable",
            errors,
        )
        _nonempty_string(python.get("version"), "runtime lock Python version", errors)
    packages = payload.get("packages")
    if not isinstance(packages, dict) or not packages:
        errors.append("runtime lock packages must be a nonempty object")
    commands = payload.get("commands")
    if not isinstance(commands, list) or not _nonempty_string_list(commands):
        errors.append("runtime lock commands must be a nonempty string list")
        return
    expected_commands = {
        "python -m ims_deadlock.g4_freeze --root cases/confirmation/g4 check",
        "python -m ims_deadlock.g4_protocol --root cases/confirmation/g4 validate",
        "python -m pytest tests/test_confirmation.py "
        "tests/test_g4_protocol.py tests/test_g4_freeze.py -q",
        *{
            "python -m ims_deadlock.g4_protocol --root "
            f"cases/confirmation/g4 run {case_id}"
            for case_id in case_ids
        },
    }
    if set(commands) != expected_commands:
        errors.append(
            "runtime lock commands must exactly match the structural checks "
            "and one post-freeze internal run command per case"
        )


def _validate_random_streams(
    payload: Mapping[str, Any],
    case_ids: tuple[str, ...],
    errors: list[str],
) -> None:
    _require_schema(
        payload,
        "ims-deadlock/g4-random-streams/v1",
        "random stream manifest",
        errors,
    )
    streams = payload.get("streams_by_case")
    if not isinstance(streams, dict):
        errors.append("random streams_by_case must be an object")
        return
    if set(streams) != set(case_ids):
        errors.append("random stream manifest must cover every frozen case")
    for case_id, decision in streams.items():
        label = f"random stream {case_id}"
        if not isinstance(decision, dict):
            errors.append(f"{label} must be an object")
            continue
        applicable = decision.get("applicable")
        if not isinstance(applicable, bool):
            errors.append(f"{label} applicable must be boolean")
            continue
        if not applicable:
            if set(decision) != {"applicable", "reason"}:
                errors.append(
                    f"{label} inapplicable row must contain exactly "
                    "applicable and reason"
                )
            _nonempty_string(decision.get("reason"), f"{label} reason", errors)
            continue
        if set(decision) != {
            "applicable",
            "derivation",
            "master_seeds",
            "replicates",
        }:
            errors.append(
                f"{label} applicable row must contain exactly applicable, "
                "derivation, master_seeds, and replicates"
            )
        seeds = decision.get("master_seeds")
        if (
            not isinstance(seeds, list)
            or not seeds
            or any(
                isinstance(seed, bool) or not isinstance(seed, int) or seed < 0
                for seed in seeds
            )
        ):
            errors.append(f"{label} master_seeds must be nonempty nonnegative integers")
        elif len(set(seeds)) != len(seeds):
            errors.append(f"{label} master_seeds must be unique")
        replicates = decision.get("replicates")
        if (
            isinstance(replicates, bool)
            or not isinstance(replicates, int)
            or replicates <= 0
        ):
            errors.append(f"{label} replicates must be a positive integer")
        derivation = _nonempty_string(
            decision.get("derivation"), f"{label} derivation", errors
        )
        if (
            derivation is not None
            and derivation != "sha256(master_seed:replication_index)"
        ):
            errors.append(f"{label} uses an unsupported seed derivation")


def _validate_metric_stream_consistency(
    metrics: Mapping[str, Any],
    random_streams: Mapping[str, Any],
    case_ids: tuple[str, ...],
    errors: list[str],
) -> None:
    metric_rows = metrics.get("metrics")
    streams = random_streams.get("streams_by_case")
    if not isinstance(metric_rows, list) or not isinstance(streams, dict):
        return
    des_rows = [
        row
        for row in metric_rows
        if isinstance(row, dict) and row.get("metric_id") == "des_confidence_interval"
    ]
    if len(des_rows) != 1:
        return
    applicability = des_rows[0].get("applicability_by_case")
    if not isinstance(applicability, dict):
        return
    for case_id in case_ids:
        metric_decision = applicability.get(case_id)
        stream_decision = streams.get(case_id)
        if not isinstance(metric_decision, dict) or not isinstance(
            stream_decision, dict
        ):
            continue
        if metric_decision.get("applicable") != stream_decision.get("applicable"):
            errors.append(
                f"DES metric and random-stream applicability disagree for {case_id}"
            )


def _validate_file_manifest(
    payload: Mapping[str, Any],
    *,
    repository_root: Path,
    expected_schema: str,
    require_entrypoints: bool,
    errors: list[str],
) -> None:
    label = "experiment script manifest" if require_entrypoints else "theory manifest"
    _require_schema(payload, expected_schema, label, errors)
    rows = _list_of_objects(payload.get("files"), f"{label} files", errors)
    if not rows:
        errors.append(f"{label} files must be nonempty")
    for index, row in enumerate(rows):
        row_label = f"{label} row {index}"
        relative = _nonempty_string(row.get("path"), f"{row_label} path", errors)
        declared_hash = _sha256_string(
            row.get("sha256"),
            f"{row_label} sha256",
            errors,
        )
        if row.get("hash_mode") != "file_bytes":
            errors.append(f"{row_label} hash_mode must be file_bytes")
        if relative is None:
            continue
        path = _safe_relative_path(
            repository_root,
            relative,
            repository_root,
            errors,
        )
        if path is None:
            continue
        if not path.is_file():
            errors.append(f"{row_label} file does not exist: {relative}")
            continue
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if declared_hash is not None and actual_hash != declared_hash:
            errors.append(f"{row_label} file hash mismatch")
    if require_entrypoints:
        entrypoints = _list_of_objects(
            payload.get("entrypoints"),
            "experiment entrypoints",
            errors,
        )
        if not entrypoints:
            errors.append("experiment entrypoints must be nonempty")
        for index, entrypoint in enumerate(entrypoints):
            _nonempty_string(
                entrypoint.get("protocol"),
                f"experiment entrypoint {index} protocol",
                errors,
            )
            callable_name = _nonempty_string(
                entrypoint.get("callable"),
                f"experiment entrypoint {index} callable",
                errors,
            )
            if callable_name is not None and ":" not in callable_name:
                errors.append(
                    f"experiment entrypoint {index} callable must use module:name"
                )


def _validate_exclusions(
    payload: Mapping[str, Any],
    errors: list[str],
) -> None:
    _require_schema(
        payload,
        "ims-deadlock/g4-exclusions/v1",
        "exclusions",
        errors,
    )
    excluded = payload.get("excluded_discovery_case_ids")
    if (
        not isinstance(excluded, list)
        or any(not isinstance(case_id, str) or not case_id for case_id in excluded)
        or set(excluded) != set(G4_DISCOVERY_CASE_IDS)
    ):
        errors.append("discovery case exclusions must be complete")
    excluded_families = payload.get("excluded_discovery_family_ids")
    if (
        not isinstance(excluded_families, list)
        or any(
            not isinstance(family_id, str) or not family_id
            for family_id in excluded_families
        )
        or set(excluded_families) != set(G4_DISCOVERY_FAMILY_IDS)
    ):
        errors.append("discovery family exclusions must be complete")
    keys = payload.get("forbidden_result_keys")
    if not _nonempty_string_list(keys):
        errors.append("forbidden result keys must be a nonempty string list")
    elif isinstance(keys, list) and not {
        "observed_result",
        "confirmation_result",
        "estimate",
        "measured",
    } <= set(keys):
        errors.append("forbidden result key list is incomplete")
    if not _nonempty_string_list(payload.get("post_freeze_rules")):
        errors.append("post-freeze rules must be a nonempty string list")


def _validate_freeze_entry(
    payload: Mapping[str, Any],
    *,
    documents: Mapping[str, Mapping[str, Any]],
    computed_hashes: Mapping[str, str],
    case_ids: tuple[str, ...],
    case_hashes: Mapping[str, str],
    runtime: Mapping[str, Any] | None,
    errors: list[str],
) -> bool | None:
    _require_schema(
        payload,
        "ims-deadlock/g4-freeze-entry/v1",
        "freeze entry",
        errors,
    )
    _nonempty_string(payload.get("freeze_id"), "freeze entry freeze_id", errors)
    implementation_commit = _commit_string(
        payload.get("implementation_commit"),
        "freeze entry implementation_commit",
        errors,
    )
    preregistration_commit = _commit_string(
        payload.get("preregistration_commit"),
        "freeze entry preregistration_commit",
        errors,
    )
    if (
        implementation_commit is not None
        and preregistration_commit is not None
        and implementation_commit == preregistration_commit
    ):
        errors.append(
            "freeze entry implementation and preregistration commits must be distinct"
        )
    for field in ("date_utc", "owner"):
        _nonempty_string(payload.get(field), f"freeze entry {field}", errors)

    inspected = payload.get("confirmation_results_inspected")
    if inspected is not False:
        errors.append("freeze entry confirmation_results_inspected must be false")
    if runtime is not None and implementation_commit is not None:
        if runtime.get("implementation_commit") != implementation_commit:
            errors.append("freeze entry implementation_commit must match runtime lock")

    included = payload.get("included_cases")
    if not isinstance(included, list) or set(included) != set(case_ids):
        errors.append("freeze entry included_cases must equal frozen case IDs")
    excluded = payload.get("excluded_cases")
    if not isinstance(excluded, list):
        errors.append("freeze entry excluded_cases must be a list")

    declared_hashes = payload.get("artifact_hashes")
    if not isinstance(declared_hashes, dict):
        errors.append("freeze entry artifact_hashes must be an object")
    else:
        if set(declared_hashes) != set(_ARTIFACT_HASH_FIELDS):
            errors.append("freeze entry artifact hash fields are incomplete")
        for field, filename in _ARTIFACT_HASH_FIELDS.items():
            declared = _sha256_string(
                declared_hashes.get(field),
                f"freeze entry {field}",
                errors,
            )
            actual = computed_hashes.get(filename)
            if declared is not None and actual is not None and declared != actual:
                errors.append(f"{field} hash mismatch")
            if filename not in documents:
                errors.append(
                    f"{field} cannot be checked because {filename} is missing"
                )

    declared_cases = payload.get("case_json_sha256_by_id")
    if not isinstance(declared_cases, dict):
        errors.append("freeze entry case_json_sha256_by_id must be an object")
    else:
        if set(declared_cases) != set(case_ids):
            errors.append("freeze entry case hashes must cover every frozen case")
        for case_id in case_ids:
            declared = _sha256_string(
                declared_cases.get(case_id),
                f"freeze entry case hash {case_id}",
                errors,
            )
            actual = case_hashes.get(case_id)
            if declared is not None and actual is not None and declared != actual:
                errors.append(f"freeze entry case hash mismatch for {case_id}")
    return inspected if isinstance(inspected, bool) else None


def _repository_root(bundle_root: Path, errors: list[str]) -> Path | None:
    try:
        repository_root = bundle_root.parents[2]
    except IndexError:
        errors.append("G4 bundle path is too shallow to resolve repository root")
        return None
    expected_suffix = ("cases", "confirmation", "g4")
    if tuple(part.lower() for part in bundle_root.parts[-3:]) != expected_suffix:
        errors.append("G4 bundle must be located at cases/confirmation/g4")
    return repository_root


def _reject_result_directories(bundle_root: Path, errors: list[str]) -> None:
    if not bundle_root.exists():
        return
    for path in sorted(bundle_root.rglob("*")):
        if path.is_dir() and path.name.lower() in _RESULT_DIRECTORY_NAMES:
            errors.append(
                f"result/output directory is forbidden before freeze: {path.name}"
            )


def _load_json_object(
    path: Path,
    errors: list[str],
) -> Mapping[str, Any] | None:
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_no_duplicate_keys_object_pairs_hook,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"invalid JSON artifact {path.name}: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"JSON artifact {path.name} must contain an object")
        return None
    return payload


def _no_duplicate_keys_object_pairs_hook(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in pairs:
        if key in payload:
            raise ValueError(f"duplicate JSON key {key!r}")
        payload[key] = value
    return payload


def _safe_relative_path(
    base: Path,
    relative: str,
    boundary: Path,
    errors: list[str],
) -> Path | None:
    posix_path = PurePosixPath(relative)
    windows_path = PureWindowsPath(relative)
    if (
        Path(relative).is_absolute()
        or posix_path.is_absolute()
        or windows_path.is_absolute()
        or bool(windows_path.drive)
        or "\\" in relative
        or posix_path.as_posix() != relative
    ):
        errors.append(f"path {relative!r} must be a relative POSIX repository path")
        return None
    candidate = (base / relative).resolve()
    try:
        candidate.relative_to(boundary.resolve())
    except ValueError:
        errors.append(f"path {relative!r} must stay inside repository root")
        return None
    return candidate


def _reject_result_keys(
    value: object,
    label: str,
    errors: list[str],
) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in _FORBIDDEN_RESULT_KEYS:
                errors.append(f"{label} contains forbidden result key {key!r}")
            _reject_result_keys(nested, label, errors)
    elif isinstance(value, list):
        for item in value:
            _reject_result_keys(item, label, errors)


def _require_schema(
    payload: Mapping[str, Any],
    expected: str,
    label: str,
    errors: list[str],
) -> None:
    if payload.get("schema_version") != expected:
        errors.append(f"{label} schema_version must be {expected}")


def _list_of_objects(
    value: object,
    label: str,
    errors: list[str],
) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    rows: list[Mapping[str, Any]] = []
    for index, row in enumerate(value):
        if not isinstance(row, dict):
            errors.append(f"{label} row {index} must be an object")
            continue
        rows.append(row)
    return rows


def _nonempty_string(
    value: object,
    label: str,
    errors: list[str],
) -> str | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a nonempty string")
        return None
    return value


def _sha256_string(
    value: object,
    label: str,
    errors: list[str],
) -> str | None:
    text = _nonempty_string(value, label, errors)
    if text is None:
        return None
    if re.fullmatch(r"[0-9a-f]{64}", text) is None:
        errors.append(f"{label} must be a lowercase SHA-256")
        return None
    return text


def _commit_string(
    value: object,
    label: str,
    errors: list[str],
) -> str | None:
    text = _nonempty_string(value, label, errors)
    if text is None:
        return None
    if re.fullmatch(r"[0-9a-f]{40}", text) is None:
        errors.append(f"{label} must be a 40-character lowercase Git commit")
        return None
    return text


def _nonempty_string_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def _matches_string_set(value: object, expected: tuple[str, ...]) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(item, str) for item in value)
        and len(value) == len(set(value))
        and set(value) == set(expected)
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only IMS_deadlock G4 freeze integrity checker."
    )
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("command", choices=("check",))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    result = check_g4_freeze(args.root)
    print(
        json.dumps(
            result.to_json_dict(),
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
    )
    return 0 if result.status == "FROZEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
