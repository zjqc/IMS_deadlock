"""Deterministic candidate-state verifiers for structured IMS-RAS families."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from ims_deadlock.certificates import find_deadlock_certificate
from ims_deadlock.model import (
    DeadlockCertificate,
    Holding,
    IMSModel,
    IMSState,
    RequestAlternative,
    Resource,
    ResourceDemand,
    validate_model_state,
)

BIX0_REPORT_VERSION = "bix0-candidate-state-grid-v1"
BIX0_FAMILY_ID = "BIX0"

BIX0Classification = Literal[
    "closed_kernel",
    "not_closed_kernel",
    "completed_zero_jobs",
    "invalid_candidate",
]


@dataclass(frozen=True)
class BIX0Parameters:
    """Finite BIX0 candidate-state parameters."""

    c_M: int
    c_G: int
    c_D: int
    n_A: int
    n_B: int

    def __post_init__(self) -> None:
        _require_int("c_M", self.c_M)
        _require_int("c_G", self.c_G)
        _require_int("c_D", self.c_D)
        _require_int("n_A", self.n_A)
        _require_int("n_B", self.n_B)
        if self.c_M < 1 or self.c_G < 1 or self.c_D < 1:
            msg = "BIX0 capacities c_M, c_G, and c_D must be at least 1"
            raise ValueError(msg)
        if self.n_A < 0 or self.n_B < 0:
            msg = "BIX0 job counts n_A and n_B must be nonnegative"
            raise ValueError(msg)

    @property
    def total_jobs(self) -> int:
        return self.n_A + self.n_B

    @property
    def predicts_closed_kernel(self) -> bool:
        """P3c BIX0 candidate-state threshold, not a reachability claim."""

        return self.n_A >= self.c_M and self.n_B >= self.c_G

    def to_json_dict(self) -> dict[str, int]:
        return {
            "c_M": self.c_M,
            "c_G": self.c_G,
            "c_D": self.c_D,
            "n_A": self.n_A,
            "n_B": self.n_B,
        }

    @classmethod
    def from_json_dict(cls, payload: object) -> BIX0Parameters:
        if not isinstance(payload, dict):
            msg = "BIX0 parameters payload must be an object"
            raise TypeError(msg)
        allowed = {"c_M", "c_G", "c_D", "n_A", "n_B"}
        _require_keys("parameters", payload, allowed)
        return cls(
            c_M=_json_int(payload["c_M"], "c_M"),
            c_G=_json_int(payload["c_G"], "c_G"),
            c_D=_json_int(payload["c_D"], "c_D"),
            n_A=_json_int(payload["n_A"], "n_A"),
            n_B=_json_int(payload["n_B"], "n_B"),
        )


@dataclass(frozen=True)
class BIX0Candidate:
    """Constructed BIX0 candidate model/state pair."""

    parameters: BIX0Parameters
    model: IMSModel
    state: IMSState


@dataclass(frozen=True)
class BIX0Observation:
    """Observed detector result for one constructed BIX0 candidate state."""

    classification: BIX0Classification
    certificate_resources: tuple[str, ...]
    certificate: DeadlockCertificate | None
    validation_issues: tuple[str, ...]

    @property
    def closed_kernel(self) -> bool:
        return self.classification == "closed_kernel"

    def to_json_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "closed_kernel": self.closed_kernel,
            "certificate_resources": list(self.certificate_resources),
            "validation_issues": list(self.validation_issues),
        }

    @classmethod
    def from_json_dict(cls, payload: object) -> BIX0Observation:
        if not isinstance(payload, dict):
            msg = "BIX0 observation payload must be an object"
            raise TypeError(msg)
        allowed = {
            "classification",
            "closed_kernel",
            "certificate_resources",
            "validation_issues",
        }
        _require_keys("observation", payload, allowed)
        classification = payload["classification"]
        if classification not in {
            "closed_kernel",
            "not_closed_kernel",
            "completed_zero_jobs",
            "invalid_candidate",
        }:
            msg = f"unknown BIX0 observation classification {classification!r}"
            raise ValueError(msg)
        closed_kernel = payload["closed_kernel"]
        if not isinstance(closed_kernel, bool):
            msg = "observation closed_kernel must be a boolean"
            raise TypeError(msg)
        if closed_kernel != (classification == "closed_kernel"):
            msg = "observation closed_kernel disagrees with classification"
            raise ValueError(msg)
        return cls(
            classification=classification,
            certificate_resources=_json_str_tuple(
                payload["certificate_resources"], "certificate_resources"
            ),
            certificate=None,
            validation_issues=_json_str_tuple(
                payload["validation_issues"], "validation_issues"
            ),
        )


@dataclass(frozen=True)
class BIX0ReportRow:
    """Versioned deterministic BIX0 grid row."""

    version: str
    family: str
    parameters: BIX0Parameters
    predicted_closed_kernel: bool
    observed: BIX0Observation
    match: bool
    note: str

    def __post_init__(self) -> None:
        if self.version != BIX0_REPORT_VERSION:
            msg = f"unsupported BIX0 report version {self.version!r}"
            raise ValueError(msg)
        if self.family != BIX0_FAMILY_ID:
            msg = f"unsupported BIX0 family {self.family!r}"
            raise ValueError(msg)
        expected = self.parameters.predicts_closed_kernel
        if self.predicted_closed_kernel != expected:
            msg = "BIX0 row prediction does not match the P3c threshold formula"
            raise ValueError(msg)
        if self.match != (self.predicted_closed_kernel == self.observed.closed_kernel):
            msg = "BIX0 row match flag disagrees with predicted/observed result"
            raise ValueError(msg)

    def to_json_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "family": self.family,
            "parameters": self.parameters.to_json_dict(),
            "predicted_closed_kernel": self.predicted_closed_kernel,
            "observed": self.observed.to_json_dict(),
            "match": self.match,
            "note": self.note,
        }

    @classmethod
    def from_json_dict(cls, payload: object) -> BIX0ReportRow:
        if not isinstance(payload, dict):
            msg = "BIX0 report row payload must be an object"
            raise TypeError(msg)
        allowed = {
            "version",
            "family",
            "parameters",
            "predicted_closed_kernel",
            "observed",
            "match",
            "note",
        }
        _require_keys("row", payload, allowed)
        version = _json_str(payload["version"], "version")
        family = _json_str(payload["family"], "family")
        predicted = payload["predicted_closed_kernel"]
        match = payload["match"]
        if not isinstance(predicted, bool):
            msg = "predicted_closed_kernel must be a boolean"
            raise TypeError(msg)
        if not isinstance(match, bool):
            msg = "match must be a boolean"
            raise TypeError(msg)
        return cls(
            version=version,
            family=family,
            parameters=BIX0Parameters.from_json_dict(payload["parameters"]),
            predicted_closed_kernel=predicted,
            observed=BIX0Observation.from_json_dict(payload["observed"]),
            match=match,
            note=_json_str(payload["note"], "note"),
        )


@dataclass(frozen=True)
class BIX0GridReport:
    """A deterministic collection of BIX0 candidate-state report rows."""

    version: str
    family: str
    rows: tuple[BIX0ReportRow, ...]

    def __post_init__(self) -> None:
        if self.version != BIX0_REPORT_VERSION:
            msg = f"unsupported BIX0 report version {self.version!r}"
            raise ValueError(msg)
        if self.family != BIX0_FAMILY_ID:
            msg = f"unsupported BIX0 family {self.family!r}"
            raise ValueError(msg)
        for row in self.rows:
            if row.version != self.version or row.family != self.family:
                msg = "BIX0 grid row version/family must match the report header"
                raise ValueError(msg)

    @property
    def mismatches(self) -> tuple[BIX0ReportRow, ...]:
        return tuple(row for row in self.rows if not row.match)

    def to_json_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "family": self.family,
            "rows": [row.to_json_dict() for row in self.rows],
        }

    @classmethod
    def from_json_dict(cls, payload: object) -> BIX0GridReport:
        if not isinstance(payload, dict):
            msg = "BIX0 grid report payload must be an object"
            raise TypeError(msg)
        allowed = {"version", "family", "rows"}
        _require_keys("report", payload, allowed)
        rows_payload = payload["rows"]
        if not isinstance(rows_payload, list):
            msg = "rows must be a list"
            raise TypeError(msg)
        return cls(
            version=_json_str(payload["version"], "version"),
            family=_json_str(payload["family"], "family"),
            rows=tuple(BIX0ReportRow.from_json_dict(row) for row in rows_payload),
        )


def build_bix0_candidate(parameters: BIX0Parameters) -> BIX0Candidate:
    """Build the P3c BIX0 no-transfer candidate saturation state.

    This encodes only the documented empty-prefix start-saturation candidate state.
    It does not assert that the candidate state is reachable from a richer runtime.
    """

    a_jobs = tuple(f"A{i + 1}" for i in range(parameters.n_A))
    b_jobs = tuple(f"B{i + 1}" for i in range(parameters.n_B))
    model = IMSModel(
        id=_model_id(parameters),
        resources={
            "M": Resource("M", parameters.c_M, "machine"),
            "G": Resource("G", parameters.c_G, "agv"),
            "D": Resource("D", parameters.c_D, "buffer"),
        },
        jobs=a_jobs + b_jobs,
    )

    holds: list[Holding] = []
    requests: dict[str, tuple[RequestAlternative, ...]] = {}
    stage_by_job: dict[str, str] = {}
    mode_by_job: dict[str, str] = {}

    a_holders = a_jobs[: parameters.c_M]
    b_holders = b_jobs[: parameters.c_G]

    for job in a_holders:
        holds.append(Holding(job, "M", 1))
        requests[job] = (
            RequestAlternative((ResourceDemand("D", 1), ResourceDemand("G", 1))),
        )
        stage_by_job[job] = "a_started_holding_M"
        mode_by_job[job] = "requesting_D_and_G"

    for job in a_jobs[parameters.c_M :]:
        requests[job] = (RequestAlternative((ResourceDemand("M", 1),)),)
        stage_by_job[job] = "a_empty_prefix"
        mode_by_job[job] = "requesting_M_to_start"

    for job in b_holders:
        holds.append(Holding(job, "G", 1))
        requests[job] = (RequestAlternative((ResourceDemand("M", 1),)),)
        stage_by_job[job] = "b_started_holding_G"
        mode_by_job[job] = "requesting_M"

    for job in b_jobs[parameters.c_G :]:
        requests[job] = (RequestAlternative((ResourceDemand("G", 1),)),)
        stage_by_job[job] = "b_empty_prefix"
        mode_by_job[job] = "requesting_G_to_start"

    state = IMSState(
        id=_state_id(parameters),
        holds=tuple(holds),
        requests=requests,
        completed_jobs=frozenset(),
        stable=True,
        complete=parameters.total_jobs == 0,
        event_calendar_empty=True,
        stage_by_job=stage_by_job,
        mode_by_job=mode_by_job,
    )
    return BIX0Candidate(parameters=parameters, model=model, state=state)


def observe_bix0_candidate(parameters: BIX0Parameters) -> BIX0Observation:
    """Run the existing detector against one BIX0 candidate state."""

    candidate = build_bix0_candidate(parameters)
    validation = validate_model_state(candidate.model, candidate.state)
    if not validation.valid:
        return BIX0Observation(
            classification="invalid_candidate",
            certificate_resources=(),
            certificate=None,
            validation_issues=tuple(issue.code for issue in validation.issues),
        )
    if parameters.total_jobs == 0:
        return BIX0Observation(
            classification="completed_zero_jobs",
            certificate_resources=(),
            certificate=None,
            validation_issues=(),
        )

    certificate = find_deadlock_certificate(candidate.model, candidate.state)
    if certificate is None:
        return BIX0Observation(
            classification="not_closed_kernel",
            certificate_resources=(),
            certificate=None,
            validation_issues=(),
        )
    return BIX0Observation(
        classification="closed_kernel",
        certificate_resources=tuple(sorted(certificate.kernel_resources)),
        certificate=certificate,
        validation_issues=(),
    )


def bix0_report_row(parameters: BIX0Parameters) -> BIX0ReportRow:
    """Return one deterministic P3c BIX0 candidate-state report row."""

    observed = observe_bix0_candidate(parameters)
    predicted = parameters.predicts_closed_kernel
    match = predicted == observed.closed_kernel
    note = (
        "zero-job completed case; skipped as a deadlock threshold observation"
        if observed.classification == "completed_zero_jobs"
        else "candidate-state verifier only; no reachability claim"
    )
    return BIX0ReportRow(
        version=BIX0_REPORT_VERSION,
        family=BIX0_FAMILY_ID,
        parameters=parameters,
        predicted_closed_kernel=predicted,
        observed=observed,
        match=match,
        note=note,
    )


def bix0_grid_report(
    *,
    max_c_M: int,
    max_c_G: int,
    max_c_D: int,
    max_n_A: int,
    max_n_B: int,
    include_zero_job_case: bool = False,
) -> BIX0GridReport:
    """Build a versioned deterministic grid report for BIX0 candidates."""

    for name, value in {
        "max_c_M": max_c_M,
        "max_c_G": max_c_G,
        "max_c_D": max_c_D,
        "max_n_A": max_n_A,
        "max_n_B": max_n_B,
    }.items():
        _require_int(name, value)
    if max_c_M < 1 or max_c_G < 1 or max_c_D < 1:
        msg = "BIX0 grid capacity maxima must be at least 1"
        raise ValueError(msg)
    if max_n_A < 0 or max_n_B < 0:
        msg = "BIX0 grid job-count maxima must be nonnegative"
        raise ValueError(msg)

    rows: list[BIX0ReportRow] = []
    for c_M in range(1, max_c_M + 1):
        for c_G in range(1, max_c_G + 1):
            for c_D in range(1, max_c_D + 1):
                for n_A in range(0, max_n_A + 1):
                    for n_B in range(0, max_n_B + 1):
                        if not include_zero_job_case and n_A + n_B == 0:
                            continue
                        rows.append(
                            bix0_report_row(
                                BIX0Parameters(
                                    c_M=c_M,
                                    c_G=c_G,
                                    c_D=c_D,
                                    n_A=n_A,
                                    n_B=n_B,
                                )
                            )
                        )
    return BIX0GridReport(
        version=BIX0_REPORT_VERSION,
        family=BIX0_FAMILY_ID,
        rows=tuple(rows),
    )


def _model_id(parameters: BIX0Parameters) -> str:
    return (
        "BIX0"
        f"-cM{parameters.c_M}-cG{parameters.c_G}-cD{parameters.c_D}"
        f"-nA{parameters.n_A}-nB{parameters.n_B}"
    )


def _state_id(parameters: BIX0Parameters) -> str:
    return f"{_model_id(parameters)}-candidate"


def _require_keys(label: str, payload: dict[Any, Any], allowed: set[str]) -> None:
    keys = set(payload)
    if keys != allowed:
        missing = sorted(allowed - keys)
        extra = sorted(keys - allowed)
        msg = f"{label} keys mismatch: missing={missing}, extra={extra}"
        raise ValueError(msg)


def _json_int(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        msg = f"{label} must be an integer"
        raise TypeError(msg)
    return value


def _require_int(label: str, value: object) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        msg = f"{label} must be an integer"
        raise TypeError(msg)


def _json_str(value: object, label: str) -> str:
    if not isinstance(value, str):
        msg = f"{label} must be a string"
        raise TypeError(msg)
    return value


def _json_str_tuple(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        msg = f"{label} must be a list"
        raise TypeError(msg)
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            msg = f"{label}[{index}] must be a string"
            raise TypeError(msg)
        result.append(item)
    return tuple(result)
