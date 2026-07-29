"""Core finite IMS-RAS data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ResourceKind = Literal["machine", "buffer", "agv", "reservation"]


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
    holds: dict[str, frozenset[str]] = field(default_factory=dict)
    requests: dict[str, frozenset[str]] = field(default_factory=dict)
    stable: bool = True
    complete: bool = False
    event_calendar_empty: bool = False

    def held_units(self, resource_id: str) -> int:
        return sum(1 for held in self.holds.values() if resource_id in held)

    def blocked_jobs(self) -> frozenset[str]:
        return frozenset(job for job, reqs in self.requests.items() if reqs)


@dataclass(frozen=True)
class DeadlockCertificate:
    """Auditable closed blocking-kernel certificate."""

    model_id: str
    state_id: str
    kernel_jobs: frozenset[str]
    kernel_resources: frozenset[str]
    evidence_edges: tuple[tuple[str, str, str], ...]
    assumptions: tuple[str, ...]
    is_minimal: bool
    certificate_type: str = "closed_blocking_kernel"

    def to_json_dict(self) -> dict[str, object]:
        return {
            "type": self.certificate_type,
            "model_id": self.model_id,
            "state_id": self.state_id,
            "kernel_jobs": sorted(self.kernel_jobs),
            "kernel_resources": sorted(self.kernel_resources),
            "evidence_edges": [
                {"kind": kind, "source": source, "target": target}
                for kind, source, target in self.evidence_edges
            ],
            "assumptions": list(self.assumptions),
            "is_minimal": self.is_minimal,
        }

