"""G5 scoring layer for frozen G4 confirmation captures."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from math import isfinite
from pathlib import Path
from typing import Any

from ims_deadlock.ctmc import (
    PROBABILITY_ABSOLUTE_TOLERANCE,
    linear_residual_is_numerically_valid,
    probability_bounds_match_values,
    probability_interval_is_numerically_valid,
    probability_values_are_numerically_valid,
)
from ims_deadlock.engine import enabled_transition
from ims_deadlock.g4_freeze import canonical_json_sha256, check_g4_freeze
from ims_deadlock.g4_instances import (
    BuiltG4Case,
    build_adversarial_boundary_case,
    build_medium_island_case,
)
from ims_deadlock.g4_protocol import (
    AdversarialProtocol,
    MediumProtocol,
    parse_g4_protocol_input,
)

SCORING_RUN_SCHEMA = "ims-deadlock/g5-scoring-run/v1"
SCORING_CASE_SCHEMA = "ims-deadlock/g5-case-score/v1"
HASH_MANIFEST_SCHEMA = "ims-deadlock/g5-raw-hash-manifest/v1"
G4_RESULT_SCHEMA = "ims-deadlock/g4-protocol-result/v1"
G5_CAPTURE_SCHEMA = "ims-deadlock/g5-capture-record/v1"
_MAX_JSON_BYTES = 1024 * 1024 * 1024
_EXPECTED_CASE_COUNT = 9
_GRID_CELL_IDS = (
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


class ExecutionStatus(Enum):
    COMPLETED = "COMPLETED"
    TIMED_OUT = "TIMED_OUT"
    NONZERO_EXIT = "NONZERO_EXIT"
    INVALID_RESULT = "INVALID_RESULT"


class ScientificStatus(Enum):
    SUPPORTED = "SUPPORTED"
    FALSIFIED = "FALSIFIED"
    INCONCLUSIVE = "INCONCLUSIVE"


class ScoringError(RuntimeError):
    """Raised for pre-scientific integrity or schema failures."""

    def __init__(self, category: str, message: str) -> None:
        super().__init__(f"{category}: {message}")
        self.category = category


@dataclass(frozen=True)
class CaseScore:
    case_id: str
    family: str
    execution_status: ExecutionStatus
    scientific_status: ScientificStatus
    supported: bool
    failure_categories: tuple[str, ...]
    reasons: tuple[str, ...]
    raw_stdout_sha256: Mapping[str, str | None]
    canonical_json_sha256: Mapping[str, str | None]
    stderr_raw_sha256: Mapping[str, str | None]
    reproducibility: Mapping[str, object]
    observations: Mapping[str, object]
    frozen_metric_applicability: Mapping[str, object]
    metric_results: Mapping[str, object]
    freeze_id: str | None

    def to_json_dict(self) -> dict[str, object]:
        """Return deterministic JSON-ready scoring data."""

        return {
            "schema_version": SCORING_CASE_SCHEMA,
            "case_id": self.case_id,
            "family": self.family,
            "execution_status": self.execution_status.value,
            "scientific_status": self.scientific_status.value,
            "supported": self.supported,
            "theorem_prediction_status": self.scientific_status.value,
            "theorem_supported": self.supported,
            "failure_categories": list(self.failure_categories),
            "reasons": list(self.reasons),
            "raw_stdout_sha256": dict(sorted(self.raw_stdout_sha256.items())),
            "canonical_json_sha256": dict(sorted(self.canonical_json_sha256.items())),
            "stderr_raw_sha256": dict(sorted(self.stderr_raw_sha256.items())),
            "reproducibility": dict(sorted(self.reproducibility.items())),
            "observations": _stable_json_value(self.observations),
            "frozen_metric_applicability": _stable_json_value(
                self.frozen_metric_applicability
            ),
            "metric_results": _stable_json_value(self.metric_results),
            "freeze_id": self.freeze_id,
        }


@dataclass(frozen=True)
class RunFiles:
    stdout_raw_sha256: str | None
    stdout_canonical_json_sha256: str | None
    stderr_raw_sha256: str | None
    stdout_json_present: bool
    stdout_bin_present: bool
    stdout_ambiguous: bool


def score_case(
    bundle_root: Path,
    result: Mapping[str, object],
    capture_record: Mapping[str, object],
) -> CaseScore:
    """Score one captured G4 result against frozen G5 scientific rules."""

    bundle = _bundle(bundle_root)
    case_id, identity_reasons = _case_id_from_record(capture_record)
    family = _case_family(bundle, case_id) if case_id else "UNKNOWN"
    capture_hash = _optional_string_or_reason(
        capture_record.get("stdout_canonical_json_sha256")
    )
    freeze_id = _optional_string_or_reason(capture_record.get("freeze_id"))

    execution_status = _execution_status(capture_record)
    schema_reasons = identity_reasons + _result_schema_reasons(
        bundle, result, capture_record, case_id, family
    )
    hash_reasons = _hash_reasons(result, capture_hash)
    if execution_status is not ExecutionStatus.COMPLETED:
        return _case_score(
            case_id,
            family,
            execution_status,
            ScientificStatus.INCONCLUSIVE,
            ("execution",),
            tuple(schema_reasons + hash_reasons),
            _hashes_from_record(capture_record, "stdout_raw_sha256"),
            _hashes_from_record(capture_record, "stdout_canonical_json_sha256"),
            _hashes_from_record(capture_record, "stderr_raw_sha256"),
            _default_reproducibility(),
            {},
            _metric_applicability(bundle, case_id) if case_id else {},
            freeze_id,
        )
    if schema_reasons or hash_reasons:
        return _case_score(
            case_id,
            family,
            ExecutionStatus.INVALID_RESULT,
            ScientificStatus.INCONCLUSIVE,
            ("result_schema",),
            tuple(schema_reasons + hash_reasons),
            _hashes_from_record(capture_record, "stdout_raw_sha256"),
            _hashes_from_record(capture_record, "stdout_canonical_json_sha256"),
            _hashes_from_record(capture_record, "stderr_raw_sha256"),
            _default_reproducibility(),
            {},
            _metric_applicability(bundle, case_id) if case_id else {},
            freeze_id,
        )

    try:
        reasons = _scientific_reasons(bundle, case_id, family, result)
        observations = _observations(bundle, case_id, family, result)
        metric_results = _metric_results(
            bundle,
            case_id,
            family,
            result,
            ScientificStatus.FALSIFIED if reasons else ScientificStatus.SUPPORTED,
        )
    except ScoringError as exc:
        if exc.category != "result_schema":
            raise
        return _case_score(
            case_id,
            family,
            ExecutionStatus.INVALID_RESULT,
            ScientificStatus.INCONCLUSIVE,
            ("result_schema",),
            (str(exc),),
            _hashes_from_record(capture_record, "stdout_raw_sha256"),
            _hashes_from_record(capture_record, "stdout_canonical_json_sha256"),
            _hashes_from_record(capture_record, "stderr_raw_sha256"),
            _default_reproducibility(),
            {},
            _metric_applicability(bundle, case_id),
            freeze_id,
        )
    if reasons:
        return _case_score(
            case_id,
            family,
            ExecutionStatus.COMPLETED,
            ScientificStatus.FALSIFIED,
            ("scientific_falsification",),
            tuple(reasons),
            _hashes_from_record(capture_record, "stdout_raw_sha256"),
            _hashes_from_record(capture_record, "stdout_canonical_json_sha256"),
            _hashes_from_record(capture_record, "stderr_raw_sha256"),
            _default_reproducibility(),
            observations,
            _metric_applicability(bundle, case_id),
            freeze_id,
            metric_results,
        )
    return _case_score(
        case_id,
        family,
        ExecutionStatus.COMPLETED,
        ScientificStatus.SUPPORTED,
        (),
        (),
        _hashes_from_record(capture_record, "stdout_raw_sha256"),
        _hashes_from_record(capture_record, "stdout_canonical_json_sha256"),
        _hashes_from_record(capture_record, "stderr_raw_sha256"),
        _default_reproducibility(),
        observations,
        _metric_applicability(bundle, case_id),
        freeze_id,
        metric_results,
    )


def score_run(bundle_root: Path, capture_root: Path) -> dict[str, object]:
    """Score a primary/repro G5 capture set for the complete frozen bundle."""

    bundle = _bundle(bundle_root)
    capture = capture_root.resolve()
    _require_contained(capture, capture, "capture_root")
    cases = _case_manifest(bundle)
    case_ids = tuple(case["case_id"] for case in cases)
    if (
        len(case_ids) != _EXPECTED_CASE_COUNT
        or len(set(case_ids)) != _EXPECTED_CASE_COUNT
    ):
        raise ScoringError(
            "protocol_integrity", "bundle must contain exactly nine cases"
        )
    captured_case_ids = _captured_case_ids(capture)
    if captured_case_ids != case_ids:
        raise ScoringError(
            "protocol_integrity",
            "capture root must contain exactly nine frozen cases",
        )

    scores: list[CaseScore] = []
    for case in cases:
        case_id = case["case_id"]
        primary_dir = _safe_child(capture, ("cases", case_id, "primary"))
        repro_dir = _safe_child(capture, ("cases", case_id, "repro"))
        primary_record = _load_json_object(primary_dir / "record.json")
        repro_record = _load_json_object(repro_dir / "record.json")
        primary_execution = _execution_status(primary_record)
        repro_execution = _execution_status(repro_record)
        primary_files = _run_files(primary_dir, primary_execution)
        repro_files = _run_files(repro_dir, repro_execution)
        pair_reasons = _capture_pair_reasons(
            case_id,
            primary_record,
            repro_record,
            primary_files,
            repro_files,
            expected_freeze_id=_freeze_id(bundle),
        )
        if primary_execution is not ExecutionStatus.COMPLETED:
            execution_match = primary_execution is repro_execution
            primary_reasons = list(pair_reasons)
            if not execution_match:
                primary_reasons.append(
                    f"primary execution status is {primary_execution.value}; "
                    f"repro execution status is {repro_execution.value}"
                )
            scores.append(
                _case_score(
                    case_id,
                    case["family"],
                    primary_execution,
                    ScientificStatus.INCONCLUSIVE,
                    ("execution",),
                    tuple(primary_reasons),
                    _pair_hashes(primary_files, repro_files, "stdout_raw_sha256"),
                    _pair_hashes(
                        primary_files, repro_files, "stdout_canonical_json_sha256"
                    ),
                    _pair_hashes(primary_files, repro_files, "stderr_raw_sha256"),
                    _reproducibility(
                        primary_record,
                        repro_record,
                        primary_files,
                        repro_files,
                        execution_match=execution_match,
                    ),
                    {},
                    _metric_applicability(bundle, case_id),
                    _freeze_id(bundle),
                )
            )
            continue
        if repro_execution is not ExecutionStatus.COMPLETED:
            scores.append(
                _case_score(
                    case_id,
                    case["family"],
                    ExecutionStatus.INVALID_RESULT,
                    ScientificStatus.INCONCLUSIVE,
                    ("result_schema",),
                    tuple(
                        pair_reasons
                        + [
                            f"repro execution status is {repro_execution.value}; "
                            "primary/repro captures must both complete"
                        ]
                    ),
                    _pair_hashes(primary_files, repro_files, "stdout_raw_sha256"),
                    _pair_hashes(
                        primary_files, repro_files, "stdout_canonical_json_sha256"
                    ),
                    _pair_hashes(primary_files, repro_files, "stderr_raw_sha256"),
                    _reproducibility(
                        primary_record,
                        repro_record,
                        primary_files,
                        repro_files,
                        execution_match=False,
                    ),
                    {},
                    _metric_applicability(bundle, case_id),
                    _freeze_id(bundle),
                )
            )
            continue
        primary_result, primary_result_reason = _load_result_json(primary_dir)
        repro_result, repro_result_reason = _load_result_json(repro_dir)
        result_reasons = pair_reasons + [
            reason
            for reason in (primary_result_reason, repro_result_reason)
            if reason is not None
        ]
        if primary_result is None:
            scores.append(
                _case_score(
                    case_id,
                    case["family"],
                    ExecutionStatus.INVALID_RESULT,
                    ScientificStatus.INCONCLUSIVE,
                    ("result_schema",),
                    tuple(result_reasons),
                    _pair_hashes(primary_files, repro_files, "stdout_raw_sha256"),
                    _pair_hashes(
                        primary_files, repro_files, "stdout_canonical_json_sha256"
                    ),
                    _pair_hashes(primary_files, repro_files, "stderr_raw_sha256"),
                    _reproducibility(
                        primary_record, repro_record, primary_files, repro_files
                    ),
                    {},
                    _metric_applicability(bundle, case_id),
                    _freeze_id(bundle),
                )
            )
            continue
        score = score_case(bundle, primary_result, primary_record)
        if result_reasons:
            score = _case_score(
                score.case_id,
                score.family,
                ExecutionStatus.INVALID_RESULT,
                ScientificStatus.INCONCLUSIVE,
                tuple(sorted(set(score.failure_categories + ("result_schema",)))),
                tuple(score.reasons + tuple(result_reasons)),
                _pair_hashes(primary_files, repro_files, "stdout_raw_sha256"),
                _pair_hashes(
                    primary_files, repro_files, "stdout_canonical_json_sha256"
                ),
                _pair_hashes(primary_files, repro_files, "stderr_raw_sha256"),
                _reproducibility(
                    primary_record, repro_record, primary_files, repro_files
                ),
                score.observations,
                score.frozen_metric_applicability,
                score.freeze_id,
            )
        else:
            score = _case_score(
                score.case_id,
                score.family,
                score.execution_status,
                score.scientific_status,
                score.failure_categories,
                score.reasons,
                _pair_hashes(primary_files, repro_files, "stdout_raw_sha256"),
                _pair_hashes(
                    primary_files, repro_files, "stdout_canonical_json_sha256"
                ),
                _pair_hashes(primary_files, repro_files, "stderr_raw_sha256"),
                _reproducibility(
                    primary_record, repro_record, primary_files, repro_files
                ),
                score.observations,
                score.frozen_metric_applicability,
                score.freeze_id,
                score.metric_results,
            )
        scores.append(score)

    execution_counts = Counter(score.execution_status.value for score in scores)
    scientific_counts = Counter(score.scientific_status.value for score in scores)
    return {
        "schema_version": SCORING_RUN_SCHEMA,
        "freeze_id": _freeze_id(bundle),
        "case_count": len(scores),
        "supported": all(score.supported for score in scores),
        "execution_status_counts": dict(sorted(execution_counts.items())),
        "scientific_status_counts": dict(sorted(scientific_counts.items())),
        "scores": [
            score.to_json_dict() for score in sorted(scores, key=lambda s: s.case_id)
        ],
    }


def _case_score(
    case_id: str,
    family: str,
    execution_status: ExecutionStatus,
    scientific_status: ScientificStatus,
    categories: tuple[str, ...],
    reasons: tuple[str, ...],
    raw_stdout_sha256: Mapping[str, str | None],
    canonical_json_sha256: Mapping[str, str | None],
    stderr_raw_sha256: Mapping[str, str | None],
    reproducibility: Mapping[str, object],
    observations: Mapping[str, object],
    frozen_metric_applicability: Mapping[str, object],
    freeze_id: str | None,
    metric_results: Mapping[str, object] | None = None,
) -> CaseScore:
    theorem_supported = (
        execution_status is ExecutionStatus.COMPLETED
        and scientific_status is ScientificStatus.SUPPORTED
    )
    return CaseScore(
        case_id=case_id,
        family=family,
        execution_status=execution_status,
        scientific_status=scientific_status,
        supported=theorem_supported,
        failure_categories=categories,
        reasons=reasons,
        raw_stdout_sha256=raw_stdout_sha256,
        canonical_json_sha256=canonical_json_sha256,
        stderr_raw_sha256=stderr_raw_sha256,
        reproducibility=reproducibility,
        observations=observations,
        frozen_metric_applicability=frozen_metric_applicability,
        metric_results=(
            metric_results
            if metric_results is not None
            else _empty_metric_results(frozen_metric_applicability)
        ),
        freeze_id=freeze_id,
    )


def _bundle(bundle_root: Path) -> Path:
    bundle = bundle_root.resolve()
    freeze = check_g4_freeze(bundle)
    if freeze.status != "FROZEN":
        raise ScoringError(
            "protocol_integrity",
            "G5 scoring requires a FROZEN G4 bundle",
        )
    entry = _freeze_entry(bundle)
    included = _string_list(entry.get("included_cases"), "FREEZE_ENTRY.included_cases")
    manifest_ids = [case["case_id"] for case in _case_manifest(bundle)]
    if included != manifest_ids:
        raise ScoringError(
            "protocol_integrity",
            "FREEZE_ENTRY included_cases must match case_manifest order exactly",
        )
    expected_hashes = _mapping(
        entry.get("case_json_sha256_by_id"),
        "FREEZE_ENTRY.case_json_sha256_by_id",
    )
    for case in _case_manifest(bundle):
        case_id = case["case_id"]
        if expected_hashes.get(case_id) != case["sha256"]:
            raise ScoringError(
                "protocol_integrity",
                f"{case_id} freeze hash identity disagrees with case manifest",
            )
    return bundle


def _case_manifest(bundle: Path) -> list[dict[str, str]]:
    payload = _load_json_object(bundle / "case_manifest.json")
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise ScoringError("protocol_integrity", "case_manifest.cases must be a list")
    rows: list[dict[str, str]] = []
    for index, item in enumerate(cases):
        row = _mapping(item, f"case_manifest.cases[{index}]")
        case_id = _string(row.get("case_id"), f"case_manifest.cases[{index}].case_id")
        family = _string(row.get("family"), f"case_manifest.cases[{index}].family")
        path = _string(row.get("path"), f"case_manifest.cases[{index}].path")
        sha256 = _string(row.get("sha256"), f"case_manifest.cases[{index}].sha256")
        case_payload = _load_json_object(_safe_child(bundle, (path,)))
        if canonical_json_sha256(case_payload) != sha256:
            raise ScoringError(
                "protocol_integrity",
                f"{case_id} case JSON hash does not match manifest",
            )
        rows.append(
            {
                "case_id": case_id,
                "family": family,
                "path": path,
                "sha256": sha256,
            }
        )
    return rows


def _case_family(bundle: Path, case_id: str) -> str:
    for case in _case_manifest(bundle):
        if case["case_id"] == case_id:
            return case["family"]
    raise ScoringError("protocol_integrity", f"{case_id} is not a frozen case")


def _case_id_from_record(record: Mapping[str, object]) -> tuple[str, list[str]]:
    value = record.get("case_id")
    if not isinstance(value, str) or not value:
        return "", ["capture record case_id must be a nonempty string"]
    return value, []


def _result_schema_reasons(
    bundle: Path,
    result: Mapping[str, object],
    capture_record: Mapping[str, object],
    case_id: str,
    family: str,
) -> list[str]:
    reasons: list[str] = []
    if result.get("schema_version") != G4_RESULT_SCHEMA:
        reasons.append("result schema_version is not the G4 protocol result schema")
    result_case_id = result.get("case_id")
    if capture_record.get("schema_version") != G5_CAPTURE_SCHEMA:
        reasons.append("capture record schema_version is not the G5 capture schema")
    if result_case_id != case_id:
        reasons.append("capture record case_id disagrees with result case_id")
    if capture_record.get("freeze_status") != "FROZEN":
        reasons.append("capture record freeze_status is not FROZEN")
    if capture_record.get("freeze_id") != _freeze_id(bundle):
        reasons.append("capture record freeze_id disagrees with bundle freeze_id")
    if result.get("family") != family:
        reasons.append("result family disagrees with frozen case manifest")
    if not isinstance(result.get("classification"), str):
        reasons.append("result classification must be a string")
    return reasons


def _optional_string_or_reason(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _hashes_from_record(
    record: Mapping[str, object], field: str
) -> Mapping[str, str | None]:
    return {"primary": _optional_string_or_reason(record.get(field)), "repro": None}


def _default_reproducibility() -> Mapping[str, object]:
    return {
        "match": None,
        "raw_stdout_match": None,
        "canonical_json_match": None,
        "stderr_match": None,
        "metadata_match": None,
    }


def _execution_status(record: Mapping[str, object]) -> ExecutionStatus:
    launch_error = record.get("launch_error")
    if launch_error not in (None, ""):
        return ExecutionStatus.INVALID_RESULT
    if record.get("timed_out") is True:
        return ExecutionStatus.TIMED_OUT
    exit_code = record.get("exit_code")
    exit_code_value = _strict_int_value(exit_code)
    if exit_code_value is None:
        return ExecutionStatus.INVALID_RESULT
    if exit_code_value != 0:
        return ExecutionStatus.NONZERO_EXIT
    return ExecutionStatus.COMPLETED


def _hash_reasons(
    result: Mapping[str, object],
    capture_hash: str | None,
) -> list[str]:
    if capture_hash is None:
        return ["capture record has no canonical JSON stdout hash"]
    if canonical_json_sha256(result) != capture_hash:
        return ["capture canonical JSON hash disagrees with result payload"]
    return []


def _scientific_reasons(
    bundle: Path,
    case_id: str,
    family: str,
    result: Mapping[str, object],
) -> list[str]:
    if family == "G4-CRP-S4PR-AGREE":
        return _score_crp_agree(result)
    if family == "G4-CRP-UNREACHABLE-CANDIDATE":
        return _score_crp_unreachable(result)
    if family == "G4-CRP-OUTSIDE-S4PR":
        return _score_crp_outside(bundle, case_id, result)
    if family == "G4-RECORDER-TARGET-QUANTIFICATION":
        return _score_recorder(result)
    if family == "G4-L30-RESOURCE-BASELINE":
        return _score_l30(result)
    if family == "G4-B05-SUPERVISOR-COMPARATOR":
        return _score_b05(result)
    if family == "G4-IMS-PARAMETER-GRID":
        return _score_grid(bundle, result)
    if family == "G4-MEDIUM-ISLAND-REBUILD":
        return _score_medium(bundle, result)
    if family == "G4-ADVERSARIAL-BOUNDARY":
        return _score_adversarial(bundle, result)
    return [f"unsupported frozen family {family!r}"]


def _score_crp_agree(result: Mapping[str, object]) -> list[str]:
    reasons = _require_value(
        result,
        "classification",
        "partial_deadlock_bridge_agreement",
    )
    audit = _mapping_or_empty(result.get("evidence_profile_audit"))
    reasons += _require_value(audit, "classification", "agreement", "audit")
    if audit.get("source_algorithm_reproduced") is not False:
        reasons.append("CRP agreement row overclaims source algorithm reproduction")
    bridge = _mapping_or_empty(result.get("partial_deadlock_bridge"))
    if bridge.get("certificate_available") is not True:
        reasons.append("partial bridge certificate is unavailable")
    if not isinstance(bridge.get("certificate"), Mapping):
        reasons.append("partial bridge certificate payload is absent")
    elif _mapping_or_empty(bridge.get("certificate")).get("is_minimal") is not True:
        reasons.append("partial bridge certificate is not minimal")
    if bridge.get("agrees") is not True:
        reasons.append("partial bridge does not agree")
    if set(
        _string_list(bridge.get("certificate_resources"), "certificate_resources")
    ) != set(_string_list(bridge.get("mapped_crp_resources"), "mapped_crp_resources")):
        reasons.append("certificate resources differ from mapped CRP resources")
    return reasons


def _score_crp_unreachable(result: Mapping[str, object]) -> list[str]:
    audit = _mapping_or_empty(result.get("evidence_profile_audit"))
    reasons = _require_value(result, "classification", "unreachable_candidate")
    reasons += _require_value(audit, "classification", "unreachable_candidate", "audit")
    if audit.get("source_algorithm_reproduced") is not False:
        reasons.append("CRP unreachable row overclaims source algorithm reproduction")
    if audit.get("independent_target_reachable") is not False:
        reasons.append("unreachable candidate target is reported reachable")
    if _list(audit.get("independent_witness"), "independent_witness"):
        reasons.append("unreachable candidate witness is nonempty")
    return reasons


def _score_crp_outside(
    bundle: Path,
    case_id: str,
    result: Mapping[str, object],
) -> list[str]:
    reasons = _require_value(result, "classification", "not_applicable")
    audit = _mapping_or_empty(result.get("evidence_profile_audit"))
    reasons += _require_value(audit, "classification", "not_applicable", "audit")
    if audit.get("source_algorithm_reproduced") is not False:
        reasons.append("CRP outside row overclaims source algorithm reproduction")
    case_input = _case_protocol_input(bundle, case_id)
    profile = _mapping_or_empty(case_input.get("crp_profile"))
    if profile.get("embedding") is not None:
        reasons.append("outside-S4PR frozen input supplies an embedding")
    outside = _mapping_or_empty(result.get("outside_scope_boundary"))
    analysis = _mapping_or_empty(outside.get("analysis"))
    built = _built_outside(bundle, case_id)
    enabled = [
        transition.name
        for transition in built.spec.transitions
        if enabled_transition(built.spec.model, built.spec.initial_state, transition)
    ]
    if enabled:
        reasons.append("outside boundary frozen target has enabled request transitions")
    reasons.extend(_or_and_reasons(analysis, built, "outside boundary"))
    if not _certificate_has_resource_kind(analysis, built, {"agv", "reservation"}):
        reasons.append("outside boundary omits AGV/reservation resource semantics")
    return reasons


def _score_recorder(result: Mapping[str, object]) -> list[str]:
    reasons = _require_value(result, "classification", "fixed_recorder_target_audit")
    if result.get("original_target_reachable") is not True:
        reasons.append("original recorder target is not reachable")
    if result.get("fixed_target_reachable") is not True:
        reasons.append("fixed recorder target is not reachable")
    if not _list(result.get("shortest_original_witness"), "shortest_original_witness"):
        reasons.append("shortest original witness is empty")
    if not _list(result.get("shortest_fixed_witness"), "shortest_fixed_witness"):
        reasons.append("shortest fixed witness is empty")
    if result.get("source_algorithm_reproduced") is not False:
        reasons.append("recorder row overclaims source algorithm reproduction")
    return reasons


def _score_l30(result: Mapping[str, object]) -> list[str]:
    reasons = _require_value(
        result, "classification", "sufficient_conditions_satisfied"
    )
    if result.get("applicable") is not True:
        reasons.append("L30 row is not applicable")
    if result.get("sufficient_conditions_satisfied") is not True:
        reasons.append("L30 sufficient_conditions_satisfied is not true")
    evaluations = _list(result.get("evaluations"), "evaluations")
    if not evaluations:
        reasons.append("L30 evaluations are empty")
    for index, item in enumerate(evaluations):
        if _mapping_or_empty(item).get("satisfied") is not True:
            reasons.append(f"L30 evaluation {index} is not satisfied")
    if result.get("exact_ims_threshold_claimed") is not False:
        reasons.append("L30 row claims an exact IMS threshold")
    if result.get("source_algorithm_reproduced") is not False:
        reasons.append("L30 row overclaims source algorithm reproduction")
    return reasons


def _score_b05(result: Mapping[str, object]) -> list[str]:
    reasons = _require_value(
        result,
        "classification",
        "optimal_over_supplied_candidates",
    )
    if set(
        _string_list(result.get("selected_monitor_ids"), "selected_monitor_ids")
    ) != {
        "m_alpha",
        "m_beta",
    }:
        reasons.append("B05 selected monitors are not exactly m_alpha and m_beta")
    if result.get("minimum_cardinality") != 2:
        reasons.append("B05 minimum cardinality is not 2")
    if result.get("all_bad_states_covered") is not True:
        reasons.append("B05 bad-state coverage is not complete")
    if result.get("all_legal_states_preserved") is not True:
        reasons.append("B05 legal-state preservation is not true")
    if result.get("optimality_scope") != "supplied_candidate_monitor_set":
        reasons.append("B05 optimality scope is not supplied_candidate_monitor_set")
    if result.get("source_algorithm_reproduced") is not False:
        reasons.append("B05 row overclaims source algorithm reproduction")
    baseline = _mapping_or_empty(result.get("exact_supervisor_baseline"))
    for field in (
        "safe_states",
        "coaccessible_states",
        "disabled_state_events",
    ):
        if not isinstance(baseline.get(field), list):
            reasons.append(f"B05 exact supervisor baseline missing {field}")
    if baseline.get("initial_state_feasible") is not True:
        reasons.append("B05 exact supervisor initial_state_feasible is not true")
    return reasons


def _score_grid(bundle: Path, result: Mapping[str, object]) -> list[str]:
    reasons = _require_value(result, "classification", "grid_executed")
    cells = _list(result.get("cells"), "cells")
    by_id = {
        _string(_mapping_or_empty(cell).get("cell_id"), "cell_id"): _mapping_or_empty(
            cell
        )
        for cell in cells
    }
    if tuple(by_id) != _GRID_CELL_IDS:
        reasons.append("grid cells are not the exact ten frozen cell IDs/order")
    if len(cells) != len(_GRID_CELL_IDS):
        reasons.append("grid row count is not 10")
    seeds, replicates, derivation = _stream_plan(bundle, "G4_IMS_PARAMETER_GRID")
    for cell_id in _GRID_CELL_IDS:
        cell = by_id.get(cell_id, {})
        analysis = _mapping_or_empty(cell.get("analysis"))
        if _mapping_or_empty(analysis.get("lts")).get("truncated") is not False:
            reasons.append(f"{cell_id} LTS is truncated")
        expected_available = cell_id not in {"G01_FWD_DAG", "G02_REV_DAG"}
        if _certificate_available(analysis) is not expected_available:
            reasons.append(f"{cell_id} certificate availability disagrees")
        if expected_available and _certificate_minimal(analysis) is not True:
            reasons.append(f"{cell_id} certificate is not minimal")
        quantitative = _mapping_or_empty(cell.get("quantitative"))
        reasons.extend(_quantitative_reasons(cell_id, cell, quantitative))
        initial_state = cell.get("ctmc_initial_state")
        reasons.extend(
            _des_reasons(
                cell_id,
                cell,
                seeds=seeds,
                replicates=replicates,
                derivation=derivation,
                exact_probability=_exact_probability(quantitative, initial_state),
            )
        )
    return reasons


def _score_medium(bundle: Path, result: Mapping[str, object]) -> list[str]:
    reasons = _require_value(result, "classification", "medium_instance_executed")
    analysis = _mapping_or_empty(result.get("analysis"))
    if _mapping_or_empty(analysis.get("lts")).get("truncated") is not False:
        reasons.append("medium LTS is truncated")
    if _certificate_available(analysis) is not True:
        reasons.append("medium certificate is unavailable")
    if _certificate_minimal(analysis) is not True:
        reasons.append("medium certificate is not minimal")
    medium_protocol = _typed_medium(bundle, "G4_MEDIUM_ISLAND_REBUILD")
    built = build_medium_island_case(medium_protocol.parameters)
    route_ids = {route_id for route_id, _count in medium_protocol.parameters.route_wip}
    if route_ids != {"ABG", "AG", "BAG"}:
        reasons.append("medium frozen routes are not exactly ABG, AG, BAG")
    if not _certificate_has_resource_kind(analysis, built, {"agv", "buffer"}):
        reasons.append("medium certificate lacks AGV or finite buffer resource")
    quantitative = _mapping_or_empty(result.get("quantitative"))
    reasons.extend(_quantitative_reasons("medium", result, quantitative))
    seeds, replicates, derivation = _stream_plan(bundle, "G4_MEDIUM_ISLAND_REBUILD")
    reasons.extend(
        _des_reasons(
            "medium",
            result,
            seeds=seeds,
            replicates=replicates,
            derivation=derivation,
            exact_probability=_exact_probability(
                quantitative, result.get("ctmc_initial_state")
            ),
        )
    )
    return reasons


def _score_adversarial(bundle: Path, result: Mapping[str, object]) -> list[str]:
    reasons = _require_value(result, "classification", "adversarial_boundary_executed")
    analysis = _mapping_or_empty(result.get("analysis"))
    if _certificate_available(analysis) is not True:
        reasons.append("adversarial certificate is unavailable")
    built = _built_adversarial(bundle, "G4_ADVERSARIAL_BOUNDARY")
    enabled = [
        transition.name
        for transition in built.spec.transitions
        if _transition_enabled(built, transition.name)
    ]
    if enabled:
        reasons.append("adversarial frozen target has enabled request transitions")
    reasons.extend(_or_and_reasons(analysis, built, "adversarial"))
    if not _certificate_has_resource_kind(analysis, built, {"agv", "reservation"}):
        reasons.append("adversarial result omits resource kind boundary evidence")
    if not _capacity_witnesses_cover_certificate(analysis):
        reasons.append("adversarial certificate capacity witnesses are incomplete")
    simple_cycle = _mapping_or_empty(analysis.get("simple_cycle_screen"))
    if simple_cycle.get("screen_only") is not True:
        reasons.append("adversarial simple-cycle output is not marked diagnostic")
    petri = _mapping_or_empty(analysis.get("petri_bridge"))
    status = petri.get("status")
    if not isinstance(status, str) or not status.startswith("not_applicable"):
        reasons.append("adversarial Petri bridge is not diagnostic/nonclaim")
    return reasons


def _certificate_available(analysis: Mapping[str, object]) -> bool:
    certificate = _mapping_or_empty(analysis.get("certificate"))
    return certificate.get("available") is True


def _certificate_minimal(analysis: Mapping[str, object]) -> bool:
    certificate = _mapping_or_empty(analysis.get("certificate"))
    payload = _mapping_or_empty(certificate.get("certificate"))
    return payload.get("is_minimal") is True


def _certificate_has_resource_kind(
    analysis: Mapping[str, object],
    built: BuiltG4Case,
    kinds: set[str],
) -> bool:
    certificate = _mapping_or_empty(
        _mapping_or_empty(analysis.get("certificate")).get("certificate")
    )
    resources = _string_list(certificate.get("kernel_resources"), "kernel_resources")
    model = built.spec.model
    return any(
        resource_id in model.resources and model.resources[resource_id].kind in kinds
        for resource_id in resources
    )


def _capacity_witnesses_cover_certificate(analysis: Mapping[str, object]) -> bool:
    certificate = _mapping_or_empty(
        _mapping_or_empty(analysis.get("certificate")).get("certificate")
    )
    resources = set(
        _string_list(certificate.get("kernel_resources"), "kernel_resources")
    )
    witnesses = _list(certificate.get("capacity_witnesses"), "capacity_witnesses")
    witnessed = {
        item.get("resource_id")
        for item in (_mapping_or_empty(entry) for entry in witnesses)
        if isinstance(item.get("resource_id"), str)
    }
    return bool(resources) and resources <= witnessed


def _or_and_reasons(
    analysis: Mapping[str, object],
    built: BuiltG4Case,
    label: str,
) -> list[str]:
    reasons: list[str] = []
    spec = built.spec
    expected_edges = {
        (job_id, alternative_index, demand.resource_id)
        for job_id, alternatives in spec.initial_state.requests.items()
        for alternative_index, alternative in enumerate(alternatives)
        for demand in alternative.demands
    }
    if not any(
        len(alternatives) > 1 for alternatives in spec.initial_state.requests.values()
    ):
        reasons.append(f"{label} frozen target lacks OR alternatives")
    if not any(
        len(alternative.demands) > 1
        for alternatives in spec.initial_state.requests.values()
        for alternative in alternatives
    ):
        reasons.append(f"{label} frozen target lacks AND demand alternatives")
    wait_graph = _mapping_or_empty(analysis.get("wait_graph"))
    observed_edges = set[tuple[str, int, str]]()
    for edge in (
        _mapping_or_empty(item)
        for item in _list(wait_graph.get("edges"), "wait_graph.edges")
    ):
        source = edge.get("source")
        target = edge.get("target")
        alternative_index = edge.get("alternative_index")
        if not (
            isinstance(source, str)
            and source.startswith("job:")
            and isinstance(target, str)
            and target.startswith("resource:")
            and isinstance(alternative_index, int)
        ):
            continue
        observed_edges.add(
            (
                source.removeprefix("job:"),
                alternative_index,
                target.removeprefix("resource:"),
            )
        )
    if not expected_edges <= observed_edges:
        reasons.append(
            f"{label} result does not retain every OR alternative AND demand edge"
        )
    return reasons


def _transition_enabled(built: BuiltG4Case, transition_name: str) -> bool:
    spec = built.spec
    for transition in spec.transitions:
        if transition.name == transition_name:
            return enabled_transition(spec.model, spec.initial_state, transition)
    raise ScoringError("result_schema", f"unknown transition {transition_name!r}")


def _quantitative_reasons(
    label: str,
    container: Mapping[str, object],
    quantitative: Mapping[str, object],
) -> list[str]:
    reasons: list[str] = []
    if quantitative.get("case_derived") is not True:
        reasons.append(f"{label} quantitative result is not case-derived")
    if quantitative.get("generator_provenance") != "derived_from_locked_g4_ims_lts":
        reasons.append(
            f"{label} quantitative generator provenance is not locked G4 LTS"
        )
    initial_state = container.get("ctmc_initial_state")
    probabilities = _mapping_or_empty(quantitative.get("deadlock_probability"))
    mean_times = _mapping_or_empty(quantitative.get("mean_absorption_time"))
    probability_values_valid = probability_values_are_numerically_valid(
        probabilities.values()
    )
    if not probability_values_valid:
        reasons.append(f"{label} deadlock probabilities contain an invalid value")
    initial_probability: float | None = None
    if not isinstance(initial_state, str) or initial_state not in probabilities:
        reasons.append(f"{label} exact p is absent for ctmc_initial_state")
    else:
        value = _strict_finite_float(probabilities[initial_state])
        if value is None or not probability_interval_is_numerically_valid(
            value,
            value,
        ):
            reasons.append(f"{label} exact p is not a finite probability")
        else:
            initial_probability = value
    if not isinstance(initial_state, str) or initial_state not in mean_times:
        reasons.append(f"{label} mean time is absent for ctmc_initial_state")
    else:
        value = _strict_finite_float(mean_times[initial_state])
        if value is None or value < 0.0:
            reasons.append(f"{label} mean time is not finite nonnegative")
    for field in ("committor_residual_inf_norm", "mean_time_residual_inf_norm"):
        value = _strict_finite_float(quantitative.get(field))
        if value is None or value < 0.0:
            reasons.append(f"{label} {field} is not finite nonnegative")
        elif not linear_residual_is_numerically_valid(value):
            reasons.append(f"{label} {field} exceeds numerical residual tolerance")
    bounds = _mapping_or_empty(quantitative.get("probability_bounds"))
    lower = _strict_finite_float(bounds.get("min"))
    upper = _strict_finite_float(bounds.get("max"))
    if lower is None or upper is None:
        reasons.append(f"{label} probability bounds are incomplete")
    elif not probability_interval_is_numerically_valid(lower, upper):
        reasons.append(f"{label} probability bounds are outside [0,1]")
    elif not probability_values_valid or not probability_bounds_match_values(
        probabilities.values(),
        lower,
        upper,
    ):
        reasons.append(
            f"{label} probability bounds do not match the full probability map"
        )
    elif initial_probability is not None and not (
        lower - PROBABILITY_ABSOLUTE_TOLERANCE
        <= initial_probability
        <= upper + PROBABILITY_ABSOLUTE_TOLERANCE
    ):
        reasons.append(f"{label} probability bounds do not contain initial p")
    if quantitative.get("probability_bounds_valid") is not True:
        reasons.append(f"{label} probability bounds are not valid")
    return reasons


def _strict_int_value(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _strict_finite_float(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    numeric = float(value)
    return numeric if isfinite(numeric) else None


def _exact_probability(
    quantitative: Mapping[str, object],
    initial_state: object,
) -> float | None:
    probabilities = _mapping_or_empty(quantitative.get("deadlock_probability"))
    value = probabilities.get(initial_state) if isinstance(initial_state, str) else None
    return _strict_finite_float(value)


def _des_reasons(
    label: str,
    payload: Mapping[str, object],
    *,
    seeds: tuple[int, ...],
    replicates: int,
    derivation: str,
    exact_probability: float | None,
) -> list[str]:
    reasons: list[str] = []
    crosscheck = _mapping_or_empty(payload.get("des_crosscheck"))
    stream_count = _strict_int_value(crosscheck.get("replicate_stream_count"))
    if stream_count is None or stream_count != len(seeds):
        reasons.append(f"{label} DES replicate stream count is not frozen")
    rows = _des_rows(payload)
    if len(rows) != len(seeds):
        reasons.append(f"{label} DES crosscheck does not have three rows")
    observed_seeds: list[int] = []
    for index, row_obj in enumerate(rows):
        row = _mapping_or_empty(row_obj)
        seed = _strict_int_value(row.get("master_seed"))
        if seed is None:
            reasons.append(f"{label} DES row {index} seed is invalid")
            continue
        observed_seeds.append(seed)
        sample_count = _strict_int_value(row.get("sample_count"))
        if sample_count is None or sample_count != replicates:
            reasons.append(f"{label} DES row {seed} replicate count is not frozen")
        deadlock_count = _strict_int_value(row.get("deadlock_count"))
        if deadlock_count is None:
            reasons.append(f"{label} DES row {seed} invalid deadlock_count")
        estimate = _strict_finite_float(row.get("deadlock_estimate"))
        if estimate is None or not 0.0 <= estimate <= 1.0:
            reasons.append(f"{label} DES row {seed} invalid deadlock_estimate")
        mean_time = _strict_finite_float(row.get("mean_absorption_time"))
        if mean_time is None or mean_time < 0.0:
            reasons.append(f"{label} DES row {seed} invalid mean_absorption_time")
        interval = row.get("wilson_95_ci")
        if not (
            isinstance(interval, list)
            and len(interval) == 2
            and all(_strict_finite_float(value) is not None for value in interval)
        ):
            reasons.append(f"{label} DES row {seed} Wilson interval is invalid")
        elif not (0.0 <= float(interval[0]) <= float(interval[1]) <= 1.0):
            reasons.append(f"{label} DES row {seed} Wilson interval is out of order")
        manifest = _mapping_or_empty(row.get("stream_manifest"))
        manifest_seed = _strict_int_value(manifest.get("master_seed"))
        if manifest_seed is None or manifest_seed != seed:
            reasons.append(f"{label} DES row {seed} stream manifest seed mismatch")
        manifest_sample_count = _strict_int_value(manifest.get("sample_count"))
        if manifest_sample_count is None or manifest_sample_count != replicates:
            reasons.append(f"{label} DES row {seed} stream manifest sample mismatch")
        if manifest.get("seed_derivation") != derivation:
            reasons.append(f"{label} DES row {seed} derivation is not frozen")
    if tuple(observed_seeds) != seeds:
        reasons.append(f"{label} DES seeds do not match frozen order")
    return reasons


def _des_rows(payload: Mapping[str, object]) -> list[object]:
    crosscheck = _mapping_or_empty(payload.get("des_crosscheck"))
    return _list(crosscheck.get("rows"), "des_crosscheck.rows")


def _observations(
    bundle: Path,
    case_id: str,
    family: str,
    result: Mapping[str, object],
) -> Mapping[str, object]:
    if family == "G4-IMS-PARAMETER-GRID":
        cells = []
        for cell_obj in _list(result.get("cells"), "cells"):
            cell = _mapping_or_empty(cell_obj)
            cells.append(_quantitative_observation(cell))
        return {"cells": cells}
    if family == "G4-MEDIUM-ISLAND-REBUILD":
        return _quantitative_observation(result)
    if family in {"G4-ADVERSARIAL-BOUNDARY", "G4-CRP-OUTSIDE-S4PR"}:
        built = (
            _built_adversarial(bundle, "G4_ADVERSARIAL_BOUNDARY")
            if family == "G4-ADVERSARIAL-BOUNDARY"
            else _built_outside(bundle, case_id)
        )
        return {
            "frozen_request_transition_enabled": [
                {
                    "transition": transition.name,
                    "enabled": enabled_transition(
                        built.spec.model,
                        built.spec.initial_state,
                        transition,
                    ),
                }
                for transition in built.spec.transitions
            ]
        }
    return {}


def _quantitative_observation(payload: Mapping[str, object]) -> Mapping[str, object]:
    quantitative = _mapping_or_empty(payload.get("quantitative"))
    initial_state = payload.get("ctmc_initial_state")
    exact_p = _exact_probability(quantitative, initial_state)
    mean_times = _mapping_or_empty(quantitative.get("mean_absorption_time"))
    mean_time = (
        mean_times.get(initial_state) if isinstance(initial_state, str) else None
    )
    rows = []
    for row_obj in _des_rows(payload):
        row = _mapping_or_empty(row_obj)
        interval = row.get("wilson_95_ci")
        in_ci = None
        if (
            exact_p is not None
            and isinstance(interval, list)
            and len(interval) == 2
            and all(_strict_finite_float(value) is not None for value in interval)
        ):
            in_ci = float(interval[0]) <= exact_p <= float(interval[1])
        rows.append(
            {
                "master_seed": row.get("master_seed"),
                "deadlock_estimate": row.get("deadlock_estimate"),
                "deadlock_count": row.get("deadlock_count"),
                "sample_count": row.get("sample_count"),
                "mean_absorption_time": row.get("mean_absorption_time"),
                "wilson_95_ci": row.get("wilson_95_ci"),
                "exact_probability_in_wilson_95_ci": in_ci,
            }
        )
    return {
        "cell_id": payload.get("cell_id"),
        "ctmc_initial_state": initial_state,
        "exact_probability": exact_p,
        "mean_absorption_time": mean_time,
        "committor_residual_inf_norm": quantitative.get("committor_residual_inf_norm"),
        "mean_time_residual_inf_norm": quantitative.get("mean_time_residual_inf_norm"),
        "probability_bounds": quantitative.get("probability_bounds"),
        "probability_bounds_valid": quantitative.get("probability_bounds_valid"),
        "des_rows": rows,
    }


def _metric_applicability(bundle: Path, case_id: str) -> Mapping[str, object]:
    metrics = _load_json_object(bundle / "metrics_schema.json")
    rows = _list(metrics.get("metrics"), "metrics")
    result: dict[str, object] = {}
    for row_obj in rows:
        row = _mapping(row_obj, "metric")
        metric_id = _string(row.get("metric_id"), "metric_id")
        applicability = _mapping(
            _mapping(row.get("applicability_by_case"), "applicability_by_case").get(
                case_id
            ),
            f"{metric_id}.applicability_by_case[{case_id}]",
        )
        result[metric_id] = {
            "applicable": applicability.get("applicable"),
            "reason": applicability.get("reason"),
        }
    return result


def _empty_metric_results(
    frozen_metric_applicability: Mapping[str, object],
) -> Mapping[str, object]:
    results: dict[str, object] = {}
    for metric_id, applicability_obj in frozen_metric_applicability.items():
        applicability = _mapping_or_empty(applicability_obj)
        applicable = applicability.get("applicable") is True
        results[str(metric_id)] = _metric_result(
            applicable=applicable,
            status="UNAVAILABLE" if applicable else "NOT_APPLICABLE",
            value=None,
            evidence_field=None,
        )
    return results


def _metric_results(
    bundle: Path,
    case_id: str,
    family: str,
    result: Mapping[str, object],
    theorem_status: ScientificStatus,
) -> Mapping[str, object]:
    applicability = _metric_applicability(bundle, case_id)
    metric_results = dict(_empty_metric_results(applicability))
    if "certificate_minimality" in metric_results:
        metric_results["certificate_minimality"] = _certificate_minimality_metric(
            family,
            result,
            _mapping_or_empty(applicability.get("certificate_minimality")).get(
                "applicable"
            )
            is True,
        )
    if "theorem_prediction_correctness" in metric_results:
        theorem_supported = theorem_status is ScientificStatus.SUPPORTED
        metric_results["theorem_prediction_correctness"] = _metric_result(
            applicable=True,
            status="PASS" if theorem_supported else "FAIL",
            value=theorem_supported,
            evidence_field="theorem_prediction_status",
        )
    return metric_results


def _certificate_minimality_metric(
    family: str,
    result: Mapping[str, object],
    applicable: bool,
) -> Mapping[str, object]:
    evidence_field, value = _certificate_minimality_value(family, result)
    if not applicable:
        return _metric_result(
            applicable=False,
            status="NOT_APPLICABLE",
            value=value,
            evidence_field=evidence_field,
        )
    if value is True:
        status = "PASS"
    elif value is False:
        status = "FAIL"
    else:
        status = "UNAVAILABLE"
    return _metric_result(
        applicable=True,
        status=status,
        value=value,
        evidence_field=evidence_field,
    )


def _certificate_minimality_value(
    family: str,
    result: Mapping[str, object],
) -> tuple[str | None, bool | None]:
    if family == "G4-CRP-S4PR-AGREE":
        evidence_field = "partial_deadlock_bridge.certificate.is_minimal"
        certificate = _mapping_or_empty(
            _mapping_or_empty(result.get("partial_deadlock_bridge")).get("certificate")
        )
        value = certificate.get("is_minimal")
        return evidence_field, value if isinstance(value, bool) else None
    if family == "G4-CRP-OUTSIDE-S4PR":
        evidence_field = (
            "outside_scope_boundary.analysis.certificate.certificate.is_minimal"
        )
        analysis = _mapping_or_empty(
            _mapping_or_empty(result.get("outside_scope_boundary")).get("analysis")
        )
        return evidence_field, _certificate_minimal_value_from_analysis(analysis)
    if family == "G4-ADVERSARIAL-BOUNDARY":
        evidence_field = "analysis.certificate.certificate.is_minimal"
        analysis = _mapping_or_empty(result.get("analysis"))
        return evidence_field, _certificate_minimal_value_from_analysis(analysis)
    if family == "G4-MEDIUM-ISLAND-REBUILD":
        evidence_field = "analysis.certificate.certificate.is_minimal"
        analysis = _mapping_or_empty(result.get("analysis"))
        return evidence_field, _certificate_minimal_value_from_analysis(analysis)
    if family == "G4-IMS-PARAMETER-GRID":
        cells = _list(result.get("cells"), "cells")
        values = [
            _certificate_minimal(
                _mapping_or_empty(_mapping_or_empty(cell).get("analysis"))
            )
            for cell in cells
            if _certificate_available(
                _mapping_or_empty(_mapping_or_empty(cell).get("analysis"))
            )
        ]
        return "cells[].analysis.certificate.certificate.is_minimal", (
            all(values) if values else None
        )
    return None, None


def _certificate_minimal_value_from_analysis(
    analysis: Mapping[str, object],
) -> bool | None:
    certificate = _mapping_or_empty(analysis.get("certificate"))
    payload = _mapping_or_empty(certificate.get("certificate"))
    value = payload.get("is_minimal")
    return value if isinstance(value, bool) else None


def _metric_result(
    *,
    applicable: bool,
    status: str,
    value: object,
    evidence_field: str | None,
) -> Mapping[str, object]:
    return {
        "applicable": applicable,
        "status": status,
        "value": value,
        "evidence_field": evidence_field,
    }


def _stream_plan(bundle: Path, case_id: str) -> tuple[tuple[int, ...], int, str]:
    payload = _load_json_object(bundle / "random_stream_manifest.json")
    row = _mapping(
        _mapping(payload.get("streams_by_case"), "streams_by_case").get(case_id),
        f"streams_by_case[{case_id}]",
    )
    seeds = tuple(int(seed) for seed in _list(row.get("master_seeds"), "master_seeds"))
    replicates = row.get("replicates")
    derivation = _string(row.get("derivation"), "derivation")
    replicate_count = _strict_int_value(replicates)
    if replicate_count is None:
        raise ScoringError("protocol_integrity", "stream replicates must be integer")
    return seeds, replicate_count, derivation


def _case_protocol_input(bundle: Path, case_id: str) -> Mapping[str, object]:
    for case in _case_manifest(bundle):
        if case["case_id"] == case_id:
            payload = _load_json_object(_safe_child(bundle, (case["path"],)))
            input_payload = _mapping(payload.get("input_payload"), "input_payload")
            return _mapping(input_payload.get("protocol_input"), "protocol_input")
    raise ScoringError("protocol_integrity", f"{case_id} is not in case manifest")


def _typed_medium(bundle: Path, case_id: str) -> MediumProtocol:
    protocol = _typed_protocol(bundle, case_id)
    if not isinstance(protocol, MediumProtocol):
        raise ScoringError("protocol_integrity", f"{case_id} is not a medium protocol")
    return protocol


def _typed_adversarial(bundle: Path, case_id: str) -> AdversarialProtocol:
    protocol = _typed_protocol(bundle, case_id)
    if not isinstance(protocol, AdversarialProtocol):
        raise ScoringError(
            "protocol_integrity", f"{case_id} is not an adversarial protocol"
        )
    return protocol


def _typed_protocol(bundle: Path, case_id: str) -> object:
    for case in _case_manifest(bundle):
        if case["case_id"] == case_id:
            payload = _load_json_object(_safe_child(bundle, (case["path"],)))
            input_payload = _mapping(payload.get("input_payload"), "input_payload")
            return parse_g4_protocol_input(
                input_payload,
                case_id=case_id,
                expected_family=case["family"],
            )
    raise ScoringError("protocol_integrity", f"{case_id} is not in case manifest")


def _built_adversarial(bundle: Path, case_id: str) -> BuiltG4Case:
    protocol = _typed_adversarial(bundle, case_id)
    return build_adversarial_boundary_case(protocol.parameters)


def _built_outside(bundle: Path, case_id: str) -> BuiltG4Case:
    case_input = _case_protocol_input(bundle, case_id)
    outside = _mapping(
        case_input.get("outside_scope_generator"), "outside_scope_generator"
    )
    protocol = parse_g4_protocol_input(
        {
            "schema_version": G4_RESULT_SCHEMA.replace("result", "input"),
            "g4_family": "G4-ADVERSARIAL-BOUNDARY",
            "protocol_kind": "adversarial_snapshot",
            "protocol_input": outside,
        },
        case_id=case_id,
        expected_family="G4-ADVERSARIAL-BOUNDARY",
    )
    if not isinstance(protocol, AdversarialProtocol):
        raise ScoringError("protocol_integrity", "outside boundary protocol mismatch")
    return build_adversarial_boundary_case(protocol.parameters)


def _freeze_entry(bundle: Path) -> Mapping[str, object]:
    return _load_json_object(bundle / "FREEZE_ENTRY.json")


def _freeze_id(bundle: Path) -> str | None:
    return _optional_string(_freeze_entry(bundle).get("freeze_id"), "freeze_id")


def _run_files(run_dir: Path, execution_status: ExecutionStatus) -> RunFiles:
    stdout_json = run_dir / "stdout.json"
    stdout_bin = run_dir / "stdout.bin"
    stdout_ambiguous = stdout_json.exists() and stdout_bin.exists()
    stdout_path = stdout_json if stdout_json.exists() else stdout_bin
    raw_hash: str | None = None
    canonical_hash: str | None = None
    if stdout_path.exists() and not stdout_ambiguous:
        stdout_bytes = _read_limited_bytes(stdout_path)
        raw_hash = hashlib.sha256(stdout_bytes).hexdigest()
        if stdout_json.exists():
            try:
                payload = _loads_json_object(stdout_path, stdout_bytes)
            except ScoringError as exc:
                if exc.category != "result_schema":
                    raise
            else:
                canonical_hash = canonical_json_sha256(payload)
    elif execution_status is ExecutionStatus.COMPLETED:
        raw_hash = None
    stderr_path = run_dir / "stderr.txt"
    stderr_hash = (
        hashlib.sha256(_read_limited_bytes(stderr_path)).hexdigest()
        if stderr_path.exists()
        else None
    )
    return RunFiles(
        stdout_raw_sha256=raw_hash,
        stdout_canonical_json_sha256=canonical_hash,
        stderr_raw_sha256=stderr_hash,
        stdout_json_present=stdout_json.exists(),
        stdout_bin_present=stdout_bin.exists(),
        stdout_ambiguous=stdout_ambiguous,
    )


def _read_limited_bytes(path: Path) -> bytes:
    resolved = path.resolve()
    try:
        if resolved.stat().st_size > _MAX_JSON_BYTES:
            raise ScoringError("result_schema", f"{resolved} exceeds JSON size limit")
        return resolved.read_bytes()
    except OSError as exc:
        raise ScoringError("protocol_integrity", f"cannot read {resolved}") from exc


def _loads_json_object(path: Path, data: bytes) -> Mapping[str, object]:
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ScoringError(
            "result_schema", f"{path.resolve()} is not valid JSON"
        ) from exc
    if not isinstance(payload, Mapping):
        raise ScoringError(
            "result_schema", f"{path.resolve()} must contain a JSON object"
        )
    _reject_nonfinite_json(payload, str(path.resolve()))
    return payload


def _reject_nonfinite_json(value: object, label: str) -> None:
    if isinstance(value, float) and not isfinite(value):
        raise ScoringError("result_schema", f"{label} contains non-finite JSON number")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_nonfinite_json(item, f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_nonfinite_json(item, f"{label}[{index}]")


def _load_result_json(run_dir: Path) -> tuple[Mapping[str, object] | None, str | None]:
    path = run_dir / "stdout.json"
    if not path.exists():
        return None, f"{path.resolve()} is missing for completed run"
    try:
        return _load_json_object(path), None
    except ScoringError as exc:
        if exc.category == "result_schema":
            return None, str(exc)
        raise


def _pair_hashes(
    primary: RunFiles,
    repro: RunFiles,
    field: str,
) -> Mapping[str, str | None]:
    return {
        "primary": getattr(primary, field),
        "repro": getattr(repro, field),
    }


def _capture_pair_reasons(
    case_id: str,
    primary_record: Mapping[str, object],
    repro_record: Mapping[str, object],
    primary_files: RunFiles,
    repro_files: RunFiles,
    *,
    expected_freeze_id: str | None,
) -> list[str]:
    reasons: list[str] = []
    for label, record, files in (
        ("primary", primary_record, primary_files),
        ("repro", repro_record, repro_files),
    ):
        if record.get("case_id") != case_id:
            reasons.append(f"{label} record case_id disagrees with capture path")
        if record.get("run_label") != label:
            reasons.append(f"{label} record run_label disagrees with capture path")
        if record.get("schema_version") != G5_CAPTURE_SCHEMA:
            reasons.append(f"{label} record schema_version is invalid")
        if record.get("freeze_status") != "FROZEN":
            reasons.append(f"{label} record freeze_status is not FROZEN")
        if record.get("freeze_id") != expected_freeze_id:
            reasons.append(f"{label} record freeze_id disagrees with bundle")
        for field in ("argv", "git_head", "git_branch", "cwd", "bundle_root"):
            value = record.get(field)
            if value in (None, "", []):
                reasons.append(f"{label} record {field} is empty")
        if files.stdout_ambiguous:
            reasons.append(f"{label} run contains both stdout.json and stdout.bin")
        if record.get("stdout_raw_sha256") != files.stdout_raw_sha256:
            reasons.append(f"{label} stdout_raw_sha256 disagrees with stdout bytes")
        if (
            record.get("stdout_canonical_json_sha256")
            != files.stdout_canonical_json_sha256
        ):
            reasons.append(
                f"{label} stdout_canonical_json_sha256 disagrees with stdout JSON"
            )
        if record.get("stderr_raw_sha256") != files.stderr_raw_sha256:
            reasons.append(f"{label} stderr_raw_sha256 disagrees with stderr bytes")
    if primary_record.get("stdout_raw_sha256") != repro_record.get("stdout_raw_sha256"):
        reasons.append("primary/repro raw stdout hashes differ")
    if primary_record.get("stdout_canonical_json_sha256") != repro_record.get(
        "stdout_canonical_json_sha256"
    ):
        reasons.append("primary/repro canonical JSON hashes differ")
    if primary_files.stderr_raw_sha256 != repro_files.stderr_raw_sha256:
        reasons.append("primary/repro stderr hashes differ")
    metadata_fields = (
        "argv",
        "freeze_id",
        "git_head",
        "git_branch",
        "cwd",
        "bundle_root",
    )
    for field in metadata_fields:
        if primary_record.get(field) != repro_record.get(field):
            reasons.append(f"primary/repro {field} differs")
    return reasons


def _reproducibility(
    primary_record: Mapping[str, object],
    repro_record: Mapping[str, object],
    primary_files: RunFiles,
    repro_files: RunFiles,
    *,
    execution_match: bool = True,
) -> Mapping[str, object]:
    raw_match = primary_files.stdout_raw_sha256 == repro_files.stdout_raw_sha256
    canonical_match = (
        primary_files.stdout_canonical_json_sha256
        == repro_files.stdout_canonical_json_sha256
    )
    stderr_match = primary_files.stderr_raw_sha256 == repro_files.stderr_raw_sha256
    metadata_match = all(
        primary_record.get(field) == repro_record.get(field)
        for field in (
            "argv",
            "freeze_id",
            "git_head",
            "git_branch",
            "cwd",
            "bundle_root",
        )
    )
    return {
        "match": (
            execution_match
            and raw_match
            and canonical_match
            and stderr_match
            and metadata_match
        ),
        "execution_status_match": execution_match,
        "raw_stdout_match": raw_match,
        "canonical_json_match": canonical_match,
        "stderr_match": stderr_match,
        "metadata_match": metadata_match,
    }


def _captured_case_ids(capture: Path) -> tuple[str, ...]:
    cases_root = _safe_child(capture, ("cases",))
    try:
        entries = tuple(path for path in cases_root.iterdir() if path.is_dir())
    except OSError as exc:
        raise ScoringError("protocol_integrity", "cannot read capture cases") from exc
    return tuple(sorted(path.name for path in entries))


def _load_json_object(path: Path) -> Mapping[str, object]:
    resolved = path.resolve()
    try:
        if resolved.stat().st_size > _MAX_JSON_BYTES:
            raise ScoringError("result_schema", f"{resolved} exceeds JSON size limit")
        with resolved.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except OSError as exc:
        raise ScoringError("protocol_integrity", f"cannot read {resolved}") from exc
    except json.JSONDecodeError as exc:
        raise ScoringError("result_schema", f"{resolved} is not valid JSON") from exc
    if not isinstance(payload, Mapping):
        raise ScoringError("result_schema", f"{resolved} must contain a JSON object")
    _reject_nonfinite_json(payload, str(resolved))
    return payload


def _safe_child(root: Path, parts: tuple[str, ...]) -> Path:
    current = root.resolve()
    for part in parts:
        path = Path(part)
        if path.is_absolute() or ".." in path.parts:
            raise ScoringError("protocol_integrity", "path traversal is not allowed")
        current = current / path
    return _require_contained(root.resolve(), current.resolve(), str(current))


def _require_contained(root: Path, path: Path, label: str) -> Path:
    if path != root and root not in path.parents:
        raise ScoringError("protocol_integrity", f"{label} escapes its root")
    return path


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ScoringError("result_schema", f"{label} must be an object")
    return value


def _mapping_or_empty(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ScoringError("result_schema", f"{label} must be a nonempty string")
    return value


def _optional_string(value: object, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ScoringError("result_schema", f"{label} must be null or a string")
    return value


def _string_list(value: object, label: str) -> list[str]:
    items = _list(value, label)
    if not all(isinstance(item, str) for item in items):
        raise ScoringError("result_schema", f"{label} must contain only strings")
    return list(items)


def _list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ScoringError("result_schema", f"{label} must be a list")
    return value


def _require_value(
    mapping: Mapping[str, object],
    key: str,
    expected: object,
    label: str | None = None,
) -> list[str]:
    if mapping.get(key) == expected:
        return []
    prefix = f"{label} " if label else ""
    return [f"{prefix}{key} is not {expected!r}"]


def _stable_json_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _stable_json_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, tuple | list):
        return [_stable_json_value(item) for item in value]
    return value


def hash_manifest_from_score(summary: Mapping[str, object]) -> dict[str, object]:
    scores = _list(summary.get("scores"), "scores")
    cases = []
    for score_obj in scores:
        score = _mapping(score_obj, "score")
        cases.append(
            {
                "case_id": score.get("case_id"),
                "raw_stdout_sha256": score.get("raw_stdout_sha256"),
                "canonical_json_sha256": score.get("canonical_json_sha256"),
                "stderr_raw_sha256": score.get("stderr_raw_sha256"),
                "reproducibility": score.get("reproducibility"),
            }
        )
    return {
        "schema_version": HASH_MANIFEST_SCHEMA,
        "freeze_id": summary.get("freeze_id"),
        "case_count": summary.get("case_count"),
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m ims_deadlock.g5_scoring")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--hash-output", type=Path)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    output_target = _preflight_output_path(
        args.output, capture_root=args.capture_root, bundle_root=args.root
    )
    hash_target = (
        _preflight_output_path(
            args.hash_output,
            capture_root=args.capture_root,
            bundle_root=args.root,
        )
        if args.hash_output is not None
        else None
    )
    if hash_target is not None and hash_target == output_target:
        raise ScoringError("protocol_integrity", "output paths must be distinct")
    summary = score_run(args.root, args.capture_root)
    payloads: list[tuple[Path, Mapping[str, object]]] = [(output_target, summary)]
    if hash_target is not None:
        payloads.append((hash_target, hash_manifest_from_score(summary)))
    _write_outputs_atomically(payloads, compact=args.compact)
    return 0


def _preflight_output_path(
    path: Path,
    *,
    capture_root: Path,
    bundle_root: Path,
) -> Path:
    target = _safe_output_path(path, capture_root=capture_root, bundle_root=bundle_root)
    if target.exists():
        raise ScoringError("protocol_integrity", f"output already exists: {target}")
    return target


def _write_outputs_atomically(
    payloads: list[tuple[Path, Mapping[str, object]]],
    *,
    compact: bool,
) -> None:
    temporary_paths: list[Path] = []
    try:
        for index, (target, payload) in enumerate(payloads):
            target.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256(str(target).encode()).hexdigest()[:12]
            temp = target.with_name(f".{target.name}.tmp-{index}-{digest}")
            if temp.exists():
                raise ScoringError(
                    "protocol_integrity", f"temporary output already exists: {temp}"
                )
            temporary_paths.append(temp)
            temp.write_text(_output_text(payload, compact=compact), encoding="utf-8")
        targets = [target for target, _payload in payloads]
        for target, temp in reversed(list(zip(targets, temporary_paths, strict=True))):
            temp.replace(target)
    except OSError as exc:
        for target, _payload in payloads:
            target.unlink(missing_ok=True)
        raise ScoringError("protocol_integrity", "cannot write output") from exc
    finally:
        for temp in temporary_paths:
            temp.unlink(missing_ok=True)


def _output_text(payload: Mapping[str, object], *, compact: bool) -> str:
    return (
        json.dumps(
            _stable_json_value(payload),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        if compact
        else json.dumps(
            _stable_json_value(payload),
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    )


def _write_output(
    path: Path,
    payload: Mapping[str, object],
    *,
    capture_root: Path,
    bundle_root: Path,
    compact: bool,
) -> None:
    _write_outputs_atomically(
        [
            (
                _preflight_output_path(
                    path, capture_root=capture_root, bundle_root=bundle_root
                ),
                payload,
            )
        ],
        compact=compact,
    )


def _safe_output_path(path: Path, *, capture_root: Path, bundle_root: Path) -> Path:
    if ".." in path.parts:
        raise ScoringError("protocol_integrity", "output path traversal is not allowed")
    capture = capture_root.resolve()
    bundle = bundle_root.resolve()
    target = path.resolve()
    if target == bundle or bundle in target.parents:
        raise ScoringError(
            "protocol_integrity", "output path must not enter frozen bundle"
        )
    if target == capture or capture in target.parents:
        raise ScoringError(
            "protocol_integrity", "output path must not enter raw capture root"
        )
    return target


if __name__ == "__main__":
    raise SystemExit(main())
