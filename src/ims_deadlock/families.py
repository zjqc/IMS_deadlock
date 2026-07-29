"""Deterministic candidate-state verifiers for structured IMS-RAS families."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from ims_deadlock.analysis import enumerate_stable_lts
from ims_deadlock.certificates import find_deadlock_certificate
from ims_deadlock.engine import EventKind, TransitionSpec
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
BIX1_REPORT_VERSION = "bix1-sat-reachable-grid-v1"
BIX1_FAMILY_ID = "BIX1-SAT"

BIX0Classification = Literal[
    "closed_kernel",
    "not_closed_kernel",
    "completed_zero_jobs",
    "invalid_candidate",
]
BIX1Classification = Literal[
    "reachable_closed_kernel",
    "not_reachable_closed_kernel",
    "truncated",
    "invalid_instance",
]
BIX1BoundaryClassification = Literal["outside_bix1_sat"]


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


@dataclass(frozen=True)
class BIX1Parameters:
    """Finite BIX1-SAT runtime parameters."""

    c_M: int
    c_G: int
    c_D: int
    c_V: int
    n_A: int
    n_B: int

    def __post_init__(self) -> None:
        _require_int("c_M", self.c_M)
        _require_int("c_G", self.c_G)
        _require_int("c_D", self.c_D)
        _require_int("c_V", self.c_V)
        _require_int("n_A", self.n_A)
        _require_int("n_B", self.n_B)
        if self.c_M < 1 or self.c_G < 1 or self.c_D < 1 or self.c_V < 1:
            msg = "BIX1 capacities c_M, c_G, c_D, and c_V must be at least 1"
            raise ValueError(msg)
        if self.n_A < 0 or self.n_B < 0:
            msg = "BIX1 job counts n_A and n_B must be nonnegative"
            raise ValueError(msg)

    @property
    def total_jobs(self) -> int:
        return self.n_A + self.n_B

    @property
    def predicts_reachable_closed_kernel(self) -> bool:
        """P3d BIX1-SAT reachable threshold oracle."""

        return self.n_A >= self.c_M and self.n_B >= self.c_G

    def to_json_dict(self) -> dict[str, int]:
        return {
            "c_M": self.c_M,
            "c_G": self.c_G,
            "c_D": self.c_D,
            "c_V": self.c_V,
            "n_A": self.n_A,
            "n_B": self.n_B,
        }

    @classmethod
    def from_json_dict(cls, payload: object) -> BIX1Parameters:
        if not isinstance(payload, dict):
            msg = "BIX1 parameters payload must be an object"
            raise TypeError(msg)
        allowed = {"c_M", "c_G", "c_D", "c_V", "n_A", "n_B"}
        _require_keys("parameters", payload, allowed)
        return cls(
            c_M=_json_int(payload["c_M"], "c_M"),
            c_G=_json_int(payload["c_G"], "c_G"),
            c_D=_json_int(payload["c_D"], "c_D"),
            c_V=_json_int(payload["c_V"], "c_V"),
            n_A=_json_int(payload["n_A"], "n_A"),
            n_B=_json_int(payload["n_B"], "n_B"),
        )


@dataclass(frozen=True)
class BIX1Instance:
    """Executable BIX1-SAT runtime instance."""

    parameters: BIX1Parameters
    model: IMSModel
    initial_state: IMSState
    transitions: tuple[TransitionSpec, ...]


@dataclass(frozen=True)
class BIX1Observation:
    """Observed reachable BIX1-SAT certificate result."""

    classification: BIX1Classification
    reachable_closed_kernel: bool
    certificate_resources: tuple[str, ...]
    shortest_reachable_prefix: tuple[str, ...]
    state_count: int
    truncated: bool
    certificate: DeadlockCertificate | None
    validation_issues: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.reachable_closed_kernel != (
            self.classification == "reachable_closed_kernel"
        ):
            msg = (
                "BIX1 observation reachable_closed_kernel disagrees with classification"
            )
            raise ValueError(msg)
        if self.truncated != (self.classification == "truncated"):
            msg = "BIX1 observation truncated flag disagrees with classification"
            raise ValueError(msg)
        if self.state_count < 0:
            msg = "BIX1 observation state_count must be nonnegative"
            raise ValueError(msg)

    def to_json_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "reachable_closed_kernel": self.reachable_closed_kernel,
            "certificate_resources": list(self.certificate_resources),
            "shortest_reachable_prefix": list(self.shortest_reachable_prefix),
            "state_count": self.state_count,
            "truncated": self.truncated,
            "validation_issues": list(self.validation_issues),
        }

    @classmethod
    def from_json_dict(cls, payload: object) -> BIX1Observation:
        if not isinstance(payload, dict):
            msg = "BIX1 observation payload must be an object"
            raise TypeError(msg)
        allowed = {
            "classification",
            "reachable_closed_kernel",
            "certificate_resources",
            "shortest_reachable_prefix",
            "state_count",
            "truncated",
            "validation_issues",
        }
        _require_keys("observation", payload, allowed)
        classification = payload["classification"]
        if classification not in {
            "reachable_closed_kernel",
            "not_reachable_closed_kernel",
            "truncated",
            "invalid_instance",
        }:
            msg = f"unknown BIX1 observation classification {classification!r}"
            raise ValueError(msg)
        reachable = payload["reachable_closed_kernel"]
        truncated = payload["truncated"]
        if not isinstance(reachable, bool):
            msg = "reachable_closed_kernel must be a boolean"
            raise TypeError(msg)
        if not isinstance(truncated, bool):
            msg = "truncated must be a boolean"
            raise TypeError(msg)
        return cls(
            classification=classification,
            reachable_closed_kernel=reachable,
            certificate_resources=_json_str_tuple(
                payload["certificate_resources"], "certificate_resources"
            ),
            shortest_reachable_prefix=_json_str_tuple(
                payload["shortest_reachable_prefix"], "shortest_reachable_prefix"
            ),
            state_count=_json_int(payload["state_count"], "state_count"),
            truncated=truncated,
            certificate=None,
            validation_issues=_json_str_tuple(
                payload["validation_issues"], "validation_issues"
            ),
        )


@dataclass(frozen=True)
class BIX1ReportRow:
    """Versioned deterministic BIX1-SAT grid row."""

    version: str
    family: str
    parameters: BIX1Parameters
    predicted_reachable_closed_kernel: bool
    observed: BIX1Observation
    match: bool
    note: str

    def __post_init__(self) -> None:
        if self.version != BIX1_REPORT_VERSION:
            msg = f"unsupported BIX1 report version {self.version!r}"
            raise ValueError(msg)
        if self.family != BIX1_FAMILY_ID:
            msg = f"unsupported BIX1 family {self.family!r}"
            raise ValueError(msg)
        expected = self.parameters.predicts_reachable_closed_kernel
        if self.predicted_reachable_closed_kernel != expected:
            msg = "BIX1 row prediction does not match the P3d threshold formula"
            raise ValueError(msg)
        expected_match = (
            False
            if self.observed.truncated
            else self.predicted_reachable_closed_kernel
            == self.observed.reachable_closed_kernel
        )
        if self.match != expected_match:
            msg = "BIX1 row match flag disagrees with predicted/observed result"
            raise ValueError(msg)

    def to_json_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "family": self.family,
            "parameters": self.parameters.to_json_dict(),
            "predicted_reachable_closed_kernel": (
                self.predicted_reachable_closed_kernel
            ),
            "observed": self.observed.to_json_dict(),
            "match": self.match,
            "note": self.note,
        }

    @classmethod
    def from_json_dict(cls, payload: object) -> BIX1ReportRow:
        if not isinstance(payload, dict):
            msg = "BIX1 report row payload must be an object"
            raise TypeError(msg)
        allowed = {
            "version",
            "family",
            "parameters",
            "predicted_reachable_closed_kernel",
            "observed",
            "match",
            "note",
        }
        _require_keys("row", payload, allowed)
        predicted = payload["predicted_reachable_closed_kernel"]
        match = payload["match"]
        if not isinstance(predicted, bool):
            msg = "predicted_reachable_closed_kernel must be a boolean"
            raise TypeError(msg)
        if not isinstance(match, bool):
            msg = "match must be a boolean"
            raise TypeError(msg)
        return cls(
            version=_json_str(payload["version"], "version"),
            family=_json_str(payload["family"], "family"),
            parameters=BIX1Parameters.from_json_dict(payload["parameters"]),
            predicted_reachable_closed_kernel=predicted,
            observed=BIX1Observation.from_json_dict(payload["observed"]),
            match=match,
            note=_json_str(payload["note"], "note"),
        )


@dataclass(frozen=True)
class BIX1GridReport:
    """A deterministic collection of BIX1-SAT reachable report rows."""

    version: str
    family: str
    rows: tuple[BIX1ReportRow, ...]

    def __post_init__(self) -> None:
        if self.version != BIX1_REPORT_VERSION:
            msg = f"unsupported BIX1 report version {self.version!r}"
            raise ValueError(msg)
        if self.family != BIX1_FAMILY_ID:
            msg = f"unsupported BIX1 family {self.family!r}"
            raise ValueError(msg)
        for row in self.rows:
            if row.version != self.version or row.family != self.family:
                msg = "BIX1 grid row version/family must match the report header"
                raise ValueError(msg)

    @property
    def mismatches(self) -> tuple[BIX1ReportRow, ...]:
        return tuple(row for row in self.rows if not row.match)

    def to_json_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "family": self.family,
            "rows": [row.to_json_dict() for row in self.rows],
        }


@dataclass(frozen=True)
class BIX1BoundaryRecord:
    """Boundary classification for cases intentionally outside BIX1-SAT."""

    case_id: str
    classification: BIX1BoundaryClassification
    note: str

    def to_json_dict(self) -> dict[str, str]:
        return {
            "case_id": self.case_id,
            "classification": self.classification,
            "note": self.note,
        }


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


def build_bix1_sat_instance(parameters: BIX1Parameters) -> BIX1Instance:
    """Build the executable BIX1-SAT saturation runtime from an empty state."""

    a_jobs = tuple(f"A{i + 1}" for i in range(parameters.n_A))
    b_jobs = tuple(f"B{i + 1}" for i in range(parameters.n_B))
    model = IMSModel(
        id=_bix1_model_id(parameters),
        resources={
            "M": Resource("M", parameters.c_M, "machine"),
            "G": Resource("G", parameters.c_G, "agv"),
            "D": Resource("D", parameters.c_D, "buffer"),
            "V": Resource("V", parameters.c_V, "reservation"),
        },
        jobs=a_jobs + b_jobs,
    )

    requests: dict[str, tuple[RequestAlternative, ...]] = {}
    stage_by_job: dict[str, str] = {}
    mode_by_job: dict[str, str] = {}
    for job in a_jobs:
        requests[job] = (_single_resource_alternative("M"),)
        stage_by_job[job] = "a_idle"
        mode_by_job[job] = "a_idle"
    for job in b_jobs:
        requests[job] = (_single_resource_alternative("G"),)
        stage_by_job[job] = "b_idle"
        mode_by_job[job] = "b_idle"

    initial_state = IMSState(
        id=_bix1_state_id(parameters),
        holds=(),
        requests=requests,
        completed_jobs=frozenset(),
        stable=True,
        complete=parameters.total_jobs == 0,
        event_calendar_empty=True,
        stage_by_job=stage_by_job,
        mode_by_job=mode_by_job,
    )
    return BIX1Instance(
        parameters=parameters,
        model=model,
        initial_state=initial_state,
        transitions=_bix1_transitions(a_jobs, b_jobs),
    )


def observe_bix1_sat(
    parameters: BIX1Parameters,
    *,
    max_states: int = 4096,
) -> BIX1Observation:
    """Enumerate BIX1-SAT reachability and keep the shortest certificate prefix."""

    instance = build_bix1_sat_instance(parameters)
    validation = validate_model_state(instance.model, instance.initial_state)
    if not validation.valid:
        return BIX1Observation(
            classification="invalid_instance",
            reachable_closed_kernel=False,
            certificate_resources=(),
            shortest_reachable_prefix=(),
            state_count=0,
            truncated=False,
            certificate=None,
            validation_issues=tuple(issue.code for issue in validation.issues),
        )

    lts = enumerate_stable_lts(
        instance.model,
        instance.initial_state,
        instance.transitions,
        max_states=max_states,
    )
    if lts.truncated:
        return BIX1Observation(
            classification="truncated",
            reachable_closed_kernel=False,
            certificate_resources=(),
            shortest_reachable_prefix=(),
            state_count=len(lts.states),
            truncated=True,
            certificate=None,
            validation_issues=tuple(lts.unavailable_reasons),
        )

    best_record_and_certificate = None
    for record in lts.states:
        certificate = find_deadlock_certificate(
            instance.model,
            record.state,
            instance.transitions,
            reachable_prefix=record.witness,
        )
        if certificate is None:
            continue
        candidate = (record, certificate)
        if best_record_and_certificate is None or (
            len(record.witness),
            record.witness,
            record.state_id,
        ) < (
            len(best_record_and_certificate[0].witness),
            best_record_and_certificate[0].witness,
            best_record_and_certificate[0].state_id,
        ):
            best_record_and_certificate = candidate

    if best_record_and_certificate is None:
        return BIX1Observation(
            classification="not_reachable_closed_kernel",
            reachable_closed_kernel=False,
            certificate_resources=(),
            shortest_reachable_prefix=(),
            state_count=len(lts.states),
            truncated=False,
            certificate=None,
            validation_issues=tuple(lts.unavailable_reasons),
        )

    record, certificate = best_record_and_certificate
    return BIX1Observation(
        classification="reachable_closed_kernel",
        reachable_closed_kernel=True,
        certificate_resources=tuple(sorted(certificate.kernel_resources)),
        shortest_reachable_prefix=tuple(record.witness),
        state_count=len(lts.states),
        truncated=False,
        certificate=certificate,
        validation_issues=tuple(lts.unavailable_reasons),
    )


def bix1_sat_report_row(
    parameters: BIX1Parameters,
    *,
    max_states: int = 4096,
) -> BIX1ReportRow:
    """Return one deterministic P3d BIX1-SAT reachable report row."""

    observed = observe_bix1_sat(parameters, max_states=max_states)
    predicted = parameters.predicts_reachable_closed_kernel
    match = (
        False if observed.truncated else predicted == observed.reachable_closed_kernel
    )
    note = (
        "bounded search truncated; row is not evidence"
        if observed.truncated
        else "reachable-state verifier with explicit start and completion events"
    )
    return BIX1ReportRow(
        version=BIX1_REPORT_VERSION,
        family=BIX1_FAMILY_ID,
        parameters=parameters,
        predicted_reachable_closed_kernel=predicted,
        observed=observed,
        match=match,
        note=note,
    )


def bix1_sat_grid_report(
    *,
    max_c_M: int,
    max_c_G: int,
    max_c_D: int,
    max_c_V: int,
    max_n_A: int,
    max_n_B: int,
    max_states: int = 4096,
) -> BIX1GridReport:
    """Build a versioned deterministic grid report for BIX1-SAT reachability."""

    for name, value in {
        "max_c_M": max_c_M,
        "max_c_G": max_c_G,
        "max_c_D": max_c_D,
        "max_c_V": max_c_V,
        "max_n_A": max_n_A,
        "max_n_B": max_n_B,
        "max_states": max_states,
    }.items():
        _require_int(name, value)
    if max_c_M < 1 or max_c_G < 1 or max_c_D < 1 or max_c_V < 1:
        msg = "BIX1 grid capacity maxima must be at least 1"
        raise ValueError(msg)
    if max_n_A < 0 or max_n_B < 0:
        msg = "BIX1 grid job-count maxima must be nonnegative"
        raise ValueError(msg)
    if max_states <= 0:
        msg = "BIX1 grid max_states must be positive"
        raise ValueError(msg)

    rows: list[BIX1ReportRow] = []
    for c_M in range(1, max_c_M + 1):
        for c_G in range(1, max_c_G + 1):
            for c_D in range(1, max_c_D + 1):
                for c_V in range(1, max_c_V + 1):
                    for n_A in range(0, max_n_A + 1):
                        for n_B in range(0, max_n_B + 1):
                            rows.append(
                                bix1_sat_report_row(
                                    BIX1Parameters(
                                        c_M=c_M,
                                        c_G=c_G,
                                        c_D=c_D,
                                        c_V=c_V,
                                        n_A=n_A,
                                        n_B=n_B,
                                    ),
                                    max_states=max_states,
                                )
                            )
    return BIX1GridReport(
        version=BIX1_REPORT_VERSION,
        family=BIX1_FAMILY_ID,
        rows=tuple(rows),
    )


def bix1_persistent_d_boundary_record() -> BIX1BoundaryRecord:
    """Return the CE-BIXD1 classification boundary for BIX1-SAT reports."""

    return BIX1BoundaryRecord(
        case_id="CE-BIXD1",
        classification="outside_bix1_sat",
        note=(
            "persistent-D variants are excluded because BIX1-SAT drains D before "
            "completion and its witness prefix never needs a successful transfer"
        ),
    )


def _model_id(parameters: BIX0Parameters) -> str:
    return (
        "BIX0"
        f"-cM{parameters.c_M}-cG{parameters.c_G}-cD{parameters.c_D}"
        f"-nA{parameters.n_A}-nB{parameters.n_B}"
    )


def _state_id(parameters: BIX0Parameters) -> str:
    return f"{_model_id(parameters)}-candidate"


def _bix1_model_id(parameters: BIX1Parameters) -> str:
    return (
        "BIX1-SAT"
        f"-cM{parameters.c_M}-cG{parameters.c_G}-cD{parameters.c_D}"
        f"-cV{parameters.c_V}-nA{parameters.n_A}-nB{parameters.n_B}"
    )


def _bix1_state_id(parameters: BIX1Parameters) -> str:
    return f"{_bix1_model_id(parameters)}-initial"


def _single_resource_alternative(resource_id: str) -> RequestAlternative:
    return RequestAlternative((ResourceDemand(resource_id, 1),))


def _bix1_transitions(
    a_jobs: tuple[str, ...], b_jobs: tuple[str, ...]
) -> tuple[TransitionSpec, ...]:
    transitions: list[TransitionSpec] = []
    for job in a_jobs:
        transitions.extend(
            (
                TransitionSpec(
                    name=f"{job}-start-M",
                    kind=EventKind.START,
                    job_id=job,
                    source_mode="a_idle",
                    target_mode="a_in_service",
                    controllable=True,
                    zero_time=False,
                    clears_requests=True,
                    acquire=(ResourceDemand("M", 1),),
                ),
                TransitionSpec(
                    name=f"{job}-service-complete",
                    kind=EventKind.SERVICE_COMPLETE,
                    job_id=job,
                    source_mode="a_in_service",
                    target_mode="a_blocked_complete",
                    controllable=False,
                    zero_time=False,
                    next_requests=(
                        RequestAlternative(
                            (
                                ResourceDemand("G", 1),
                                ResourceDemand("D", 1),
                                ResourceDemand("V", 1),
                            )
                        ),
                    ),
                ),
                TransitionSpec(
                    name=f"{job}-transfer-G-D-V-release-M",
                    kind=EventKind.DISPATCH,
                    job_id=job,
                    source_mode="a_blocked_complete",
                    target_mode="a_transferred",
                    controllable=True,
                    zero_time=False,
                    clears_requests=True,
                    acquire=(
                        ResourceDemand("G", 1),
                        ResourceDemand("D", 1),
                        ResourceDemand("V", 1),
                    ),
                    release=(ResourceDemand("M", 1),),
                ),
                TransitionSpec(
                    name=f"{job}-drain-G-D-V",
                    kind=EventKind.RELEASE,
                    job_id=job,
                    source_mode="a_transferred",
                    target_mode="completed",
                    controllable=False,
                    zero_time=False,
                    release=(
                        ResourceDemand("G", 1),
                        ResourceDemand("D", 1),
                        ResourceDemand("V", 1),
                    ),
                    mark_complete=True,
                ),
            )
        )
    for job in b_jobs:
        transitions.extend(
            (
                TransitionSpec(
                    name=f"{job}-start-G",
                    kind=EventKind.START,
                    job_id=job,
                    source_mode="b_idle",
                    target_mode="b_in_transport",
                    controllable=True,
                    zero_time=False,
                    clears_requests=True,
                    acquire=(ResourceDemand("G", 1),),
                ),
                TransitionSpec(
                    name=f"{job}-transport-complete",
                    kind=EventKind.TRANSPORT_COMPLETE,
                    job_id=job,
                    source_mode="b_in_transport",
                    target_mode="b_blocked_unload",
                    controllable=False,
                    zero_time=False,
                    next_requests=(_single_resource_alternative("M"),),
                ),
                TransitionSpec(
                    name=f"{job}-unload-M-release-G",
                    kind=EventKind.UNLOAD,
                    job_id=job,
                    source_mode="b_blocked_unload",
                    target_mode="b_on_M",
                    controllable=True,
                    zero_time=False,
                    clears_requests=True,
                    acquire=(ResourceDemand("M", 1),),
                    release=(ResourceDemand("G", 1),),
                ),
                TransitionSpec(
                    name=f"{job}-complete-release-M",
                    kind=EventKind.RELEASE,
                    job_id=job,
                    source_mode="b_on_M",
                    target_mode="completed",
                    controllable=False,
                    zero_time=False,
                    release=(ResourceDemand("M", 1),),
                    mark_complete=True,
                ),
            )
        )
    return tuple(transitions)


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
