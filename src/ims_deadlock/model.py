"""Core finite IMS-RAS data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ResourceKind = Literal["machine", "buffer", "agv", "reservation"]
CertificateScope = Literal["global", "local"]


@dataclass(frozen=True)
class Resource:
    """Reusable resource with finite capacity."""

    id: str
    capacity: int
    kind: ResourceKind = "machine"

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            msg = f"resource {self.id!r} must have positive capacity"
            raise ValueError(msg)


@dataclass(frozen=True)
class ResourceDemand:
    """A positive demand for units of one resource."""

    resource_id: str
    units: int = 1

    def __post_init__(self) -> None:
        if self.units <= 0:
            msg = f"demand for {self.resource_id!r} must have positive units"
            raise ValueError(msg)


@dataclass(frozen=True)
class RequestAlternative:
    """One conjunctive option; alternatives on a job are disjunctive."""

    demands: tuple[ResourceDemand, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "demands", _normalize_demands(self.demands))


@dataclass(frozen=True)
class Holding:
    """Units of a resource currently held by a job."""

    job_id: str
    resource_id: str
    units: int = 1

    def __post_init__(self) -> None:
        if self.units <= 0:
            msg = f"holding for {self.resource_id!r} must have positive units"
            raise ValueError(msg)


@dataclass(frozen=True)
class IMSModel:
    """Finite-batch IMS-RAS model skeleton."""

    id: str
    resources: dict[str, Resource]
    jobs: tuple[str, ...]

    def capacity(self, resource_id: str) -> int:
        return self.resources[resource_id].capacity


@dataclass(frozen=True)
class IMSState:
    """Stable IMS-RAS state after zero-time closure."""

    id: str
    holds: tuple[Holding, ...] = field(default_factory=tuple)
    requests: dict[str, tuple[RequestAlternative, ...]] = field(default_factory=dict)
    completed_jobs: frozenset[str] = field(default_factory=frozenset)
    stable: bool = True
    complete: bool = False
    event_calendar_empty: bool = False
    stage_by_job: dict[str, str] = field(default_factory=dict)
    mode_by_job: dict[str, str] = field(default_factory=dict)
    zero_time_trace: tuple[str, ...] = field(default_factory=tuple)

    def held_units(self, resource_id: str) -> int:
        return sum(
            holding.units
            for holding in self.holds
            if holding.resource_id == resource_id
        )

    def held_units_by_jobs(
        self, resource_id: str, jobs: frozenset[str] | set[str]
    ) -> int:
        return sum(
            holding.units
            for holding in self.holds
            if holding.resource_id == resource_id and holding.job_id in jobs
        )

    def holders(self, resource_id: str) -> frozenset[str]:
        return frozenset(
            holding.job_id
            for holding in self.holds
            if holding.resource_id == resource_id
        )

    def available_units(self, model: IMSModel, resource_id: str) -> int:
        return model.capacity(resource_id) - self.held_units(resource_id)

    def unfinished_jobs(self, model: IMSModel) -> frozenset[str]:
        return frozenset(job for job in model.jobs if job not in self.completed_jobs)

    def blocked_jobs(self, model: IMSModel) -> frozenset[str]:
        blocked: set[str] = set()
        for job, alternatives in self.requests.items():
            if job in self.completed_jobs or not alternatives:
                continue
            all_alternatives_blocked = True
            for alternative in alternatives:
                alternative_blocked = False
                for demand in alternative.demands:
                    if demand.resource_id not in model.resources:
                        continue
                    if self.available_units(model, demand.resource_id) < demand.units:
                        alternative_blocked = True
                        break
                if not alternative_blocked:
                    all_alternatives_blocked = False
                    break
            if all_alternatives_blocked:
                blocked.add(job)
        return frozenset(blocked)


@dataclass(frozen=True)
class EvidenceEdge:
    """Directed certificate edge with explicit resource units."""

    kind: Literal["hold", "request"]
    source: str
    target: str
    units: int

    def __post_init__(self) -> None:
        if self.units <= 0:
            msg = "evidence edge units must be positive"
            raise ValueError(msg)

    def to_json_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "source": self.source,
            "target": self.target,
            "units": self.units,
        }


@dataclass(frozen=True)
class CapacityWitness:
    """Auditable per-request capacity shortage witness."""

    job_id: str
    alternative_index: int
    resource_id: str
    requested_units: int
    capacity: int
    held_units: int
    residual_units: int
    kernel_held_units: int
    holders: tuple[str, ...]
    shortage_units: int

    def __post_init__(self) -> None:
        if not self.job_id or not self.resource_id:
            msg = "capacity witness job and resource ids must be non-empty"
            raise ValueError(msg)
        if self.alternative_index < 0:
            msg = "alternative index must be non-negative"
            raise ValueError(msg)
        if self.requested_units <= 0:
            msg = "requested units must be positive"
            raise ValueError(msg)
        if self.capacity <= 0:
            msg = "capacity must be positive"
            raise ValueError(msg)
        if self.held_units < 0 or self.residual_units < 0:
            msg = "held and residual units must be non-negative"
            raise ValueError(msg)
        if self.kernel_held_units < 0:
            msg = "kernel held units must be non-negative"
            raise ValueError(msg)
        if self.held_units > self.capacity:
            msg = "held units must not exceed capacity"
            raise ValueError(msg)
        if self.residual_units != self.capacity - self.held_units:
            msg = "residual units must equal capacity minus held units"
            raise ValueError(msg)
        if self.kernel_held_units > self.held_units:
            msg = "kernel held units must not exceed total held units"
            raise ValueError(msg)
        if self.shortage_units != self.requested_units - self.residual_units:
            msg = "shortage units must equal requested units minus residual units"
            raise ValueError(msg)
        if self.shortage_units <= 0:
            msg = "shortage units must be positive"
            raise ValueError(msg)
        normalized_holders = tuple(sorted(set(self.holders)))
        if len(normalized_holders) != len(self.holders):
            msg = "capacity witness holders must be unique"
            raise ValueError(msg)
        if self.kernel_held_units > 0 and not normalized_holders:
            msg = "positive kernel holdings require at least one holder"
            raise ValueError(msg)
        object.__setattr__(self, "holders", normalized_holders)

    def to_json_dict(self) -> dict[str, object]:
        return {
            "job_id": self.job_id,
            "alternative_index": self.alternative_index,
            "resource_id": self.resource_id,
            "requested_units": self.requested_units,
            "capacity": self.capacity,
            "held_units": self.held_units,
            "residual_units": self.residual_units,
            "kernel_held_units": self.kernel_held_units,
            "holders": list(self.holders),
            "shortage_units": self.shortage_units,
        }


@dataclass(frozen=True)
class DeadlockCertificate:
    """Auditable closed blocking-kernel certificate."""

    model_id: str
    state_id: str
    kernel_jobs: frozenset[str]
    kernel_resources: frozenset[str]
    evidence_edges: tuple[EvidenceEdge, ...]
    assumptions: tuple[str, ...]
    is_minimal: bool
    scope: CertificateScope = "global"
    certificate_type: str = "closed_blocking_kernel"
    zero_time_trace: tuple[str, ...] = field(default_factory=tuple)
    capacity_witnesses: tuple[CapacityWitness, ...] = field(default_factory=tuple)
    shortest_reachable_prefix: tuple[str, ...] | None = None
    corresponding_siphon: dict[str, object] | None = None
    bridge_status: str = "not_applicable_no_petri_subclass_mapping"

    def to_json_dict(self) -> dict[str, object]:
        return {
            "type": self.certificate_type,
            "model_id": self.model_id,
            "state_id": self.state_id,
            "kernel_jobs": sorted(self.kernel_jobs),
            "kernel_resources": sorted(self.kernel_resources),
            "evidence_edges": [edge.to_json_dict() for edge in self.evidence_edges],
            "assumptions": list(self.assumptions),
            "is_minimal": self.is_minimal,
            "scope": self.scope,
            "zero_time_trace": list(self.zero_time_trace),
            "capacity_witnesses": [
                witness.to_json_dict() for witness in self.capacity_witnesses
            ],
            "shortest_reachable_prefix": (
                list(self.shortest_reachable_prefix)
                if self.shortest_reachable_prefix is not None
                else None
            ),
            "corresponding_siphon": self.corresponding_siphon,
            "bridge_status": self.bridge_status,
        }


@dataclass(frozen=True)
class ValidationIssue:
    """Structured model/state validation issue."""

    code: str
    message: str

    def to_json_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True)
class ValidationResult:
    """Validation result with stable issue ordering."""

    issues: tuple[ValidationIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues

    def to_json_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "issues": [issue.to_json_dict() for issue in self.issues],
        }


def validate_model_state(model: IMSModel, state: IMSState) -> ValidationResult:
    """Validate references, capacities, and stable/complete consistency."""

    issues: list[ValidationIssue] = []

    for key, resource in sorted(model.resources.items()):
        if key != resource.id:
            issues.append(
                ValidationIssue(
                    "resource_key_id_mismatch",
                    f"resource key {key!r} does not match id {resource.id!r}",
                )
            )

    if len(set(model.jobs)) != len(model.jobs):
        issues.append(ValidationIssue("duplicate_job_id", "model jobs must be unique"))

    job_set = set(model.jobs)
    resource_ids = set(model.resources)

    for completed_job in sorted(state.completed_jobs):
        if completed_job not in job_set:
            issues.append(
                ValidationIssue(
                    "unknown_completed_job",
                    f"completed job {completed_job!r} is not in model",
                )
            )

    held_by_resource: dict[str, int] = {resource_id: 0 for resource_id in resource_ids}
    for holding in state.holds:
        if holding.job_id not in job_set:
            issues.append(
                ValidationIssue(
                    "unknown_hold_job",
                    f"holding references unknown job {holding.job_id!r}",
                )
            )
        if holding.resource_id not in resource_ids:
            issues.append(
                ValidationIssue(
                    "unknown_hold_resource",
                    f"holding references unknown resource {holding.resource_id!r}",
                )
            )
        else:
            held_by_resource[holding.resource_id] += holding.units
        if holding.job_id in state.completed_jobs:
            issues.append(
                ValidationIssue(
                    "completed_job_holds_resource",
                    f"completed job {holding.job_id!r} still holds resources",
                )
            )

    for resource_id, units in sorted(held_by_resource.items()):
        if units > model.capacity(resource_id):
            issues.append(
                ValidationIssue(
                    "overcapacity_resource",
                    f"resource {resource_id!r} holds {units} units over capacity "
                    f"{model.capacity(resource_id)}",
                )
            )

    for job_id, alternatives in sorted(state.requests.items()):
        if job_id not in job_set:
            issues.append(
                ValidationIssue(
                    "unknown_request_job",
                    f"request references unknown job {job_id!r}",
                )
            )
        if job_id in state.completed_jobs:
            issues.append(
                ValidationIssue(
                    "completed_job_has_request",
                    f"completed job {job_id!r} still has requests",
                )
            )
        for alternative in alternatives:
            for demand in alternative.demands:
                if demand.resource_id not in resource_ids:
                    issues.append(
                        ValidationIssue(
                            "unknown_request_resource",
                            "request references unknown resource "
                            f"{demand.resource_id!r}",
                        )
                    )
                    continue
                if demand.units > model.capacity(demand.resource_id):
                    issues.append(
                        ValidationIssue(
                            "demand_exceeds_capacity",
                            f"demand for {demand.resource_id!r} needs {demand.units} "
                            f"units over capacity {model.capacity(demand.resource_id)}",
                        )
                    )

    if state.complete:
        has_open_work = (
            state.completed_jobs != frozenset(model.jobs)
            or bool(state.holds)
            or bool(state.requests)
        )
        if has_open_work:
            issues.append(
                ValidationIssue(
                    "complete_state_has_open_work",
                    "complete state must have all jobs completed and no holds "
                    "or requests",
                )
            )
        if not state.event_calendar_empty:
            issues.append(
                ValidationIssue(
                    "complete_state_has_event_calendar",
                    "complete state must have an empty event calendar",
                )
            )

    if not state.stable:
        issues.append(
            ValidationIssue(
                "state_not_closure_normalized",
                "public IMSState must be normalized after zero-time closure",
            )
        )

    return ValidationResult(tuple(issues))


def _normalize_demands(
    demands: tuple[ResourceDemand, ...] | list[ResourceDemand],
) -> tuple[ResourceDemand, ...]:
    aggregated: dict[str, int] = {}
    for demand in demands:
        aggregated[demand.resource_id] = (
            aggregated.get(demand.resource_id, 0) + demand.units
        )
    return tuple(
        ResourceDemand(resource_id, units)
        for resource_id, units in sorted(aggregated.items())
    )
