"""Petri wait-snapshot bridge for the narrow IMS-SIP^1 subclass."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from itertools import combinations
from types import MappingProxyType

from ims_deadlock.model import DeadlockCertificate, IMSModel, IMSState

_EXACT_STATUS = "exact_ims_sip1_wait_snapshot_duality"
_FAILED_PREFIX = "not_applicable_ims_sip1_assumptions_failed:"


@dataclass(frozen=True)
class PetriTransition:
    """Ordinary Petri transition over diagnostic free-resource places."""

    name: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "inputs", tuple(sorted(set(self.inputs))))
        object.__setattr__(self, "outputs", tuple(sorted(set(self.outputs))))


@dataclass(frozen=True)
class WaitSnapshotNet:
    """State-induced diagnostic net over residual resource availability."""

    places: tuple[str, ...]
    transitions: tuple[PetriTransition, ...]
    marking: Mapping[str, int]

    def __post_init__(self) -> None:
        places = tuple(sorted(set(self.places)))
        marking = {place: int(self.marking.get(place, 0)) for place in places}
        object.__setattr__(self, "places", places)
        object.__setattr__(self, "transitions", tuple(self.transitions))
        object.__setattr__(self, "marking", MappingProxyType(marking))

    def to_json_dict(self) -> dict[str, object]:
        return {
            "places": list(self.places),
            "transitions": [
                {
                    "name": transition.name,
                    "inputs": list(transition.inputs),
                    "outputs": list(transition.outputs),
                }
                for transition in self.transitions
            ],
            "marking": dict(self.marking),
        }


@dataclass(frozen=True)
class SiphonBridgeResult:
    """Result of attempting the IMS-SIP^1 wait-snapshot bridge."""

    applicable: bool
    exact: bool
    reason: str
    core_jobs: tuple[str, ...]
    core_resources: tuple[str, ...]
    siphon_places: tuple[str, ...]
    empty: bool
    minimal: bool
    net: WaitSnapshotNet | None

    @property
    def bridge_status(self) -> str:
        if self.applicable and self.exact:
            return _EXACT_STATUS
        return f"{_FAILED_PREFIX}{self.reason}"

    def corresponding_siphon_json(self) -> dict[str, object] | None:
        if not self.applicable or not self.exact:
            return None
        return {
            "type": "state_induced_wait_snapshot",
            "places": list(self.siphon_places),
            "empty": self.empty,
            "minimal": self.minimal,
            "core_jobs": list(self.core_jobs),
            "core_resources": list(self.core_resources),
        }


def build_wait_snapshot_bridge(
    model: IMSModel,
    state: IMSState,
    certificate: DeadlockCertificate,
) -> SiphonBridgeResult:
    """Build the exact diagnostic siphon bridge when IMS-SIP^1 assumptions hold."""

    core_jobs = tuple(sorted(certificate.kernel_jobs))
    core_resources = tuple(sorted(certificate.kernel_resources))
    failed = _check_sip1_assumptions(model, state, certificate)
    if failed is not None:
        return SiphonBridgeResult(
            applicable=False,
            exact=False,
            reason=failed,
            core_jobs=core_jobs,
            core_resources=core_resources,
            siphon_places=(),
            empty=False,
            minimal=False,
            net=None,
        )

    hold_by_job = {
        job_id: next(
            holding.resource_id
            for holding in state.holds
            if holding.job_id == job_id
            and holding.resource_id in certificate.kernel_resources
        )
        for job_id in core_jobs
    }
    request_by_job = {
        job_id: state.requests[job_id][0].demands[0].resource_id for job_id in core_jobs
    }
    places = tuple(f"free:{resource_id}" for resource_id in core_resources)
    transitions = tuple(
        PetriTransition(
            name=f"t:{job_id}",
            inputs=(f"free:{request_by_job[job_id]}",),
            outputs=(f"free:{hold_by_job[job_id]}",),
        )
        for job_id in core_jobs
    )
    net = WaitSnapshotNet(
        places=places,
        transitions=transitions,
        marking={
            f"free:{resource_id}": state.available_units(model, resource_id)
            for resource_id in core_resources
        },
    )
    siphon_places = places
    empty = all(net.marking[place] == 0 for place in siphon_places)
    siphon = is_siphon(net, siphon_places)
    minimal = siphon_places in minimal_empty_siphons(net)
    if not empty or not siphon or not minimal:
        if not empty:
            reason = "constructed siphon is not empty"
        elif not siphon:
            reason = "constructed place set is not a siphon"
        else:
            reason = "constructed empty siphon is not inclusion-minimal"
        return SiphonBridgeResult(
            applicable=False,
            exact=False,
            reason=reason,
            core_jobs=core_jobs,
            core_resources=core_resources,
            siphon_places=(),
            empty=False,
            minimal=False,
            net=None,
        )
    return SiphonBridgeResult(
        applicable=True,
        exact=True,
        reason="ims_sip1_assumptions_satisfied",
        core_jobs=core_jobs,
        core_resources=core_resources,
        siphon_places=siphon_places,
        empty=empty,
        minimal=minimal,
        net=net,
    )


def certificate_with_wait_snapshot_bridge(
    model: IMSModel,
    state: IMSState,
    certificate: DeadlockCertificate,
) -> DeadlockCertificate:
    """Return a certificate copy annotated with the attempted bridge result."""

    result = build_wait_snapshot_bridge(model, state, certificate)
    return replace(
        certificate,
        corresponding_siphon=result.corresponding_siphon_json(),
        bridge_status=result.bridge_status,
    )


def is_siphon(net: WaitSnapshotNet, places: tuple[str, ...]) -> bool:
    """Return whether ``places`` satisfy the ordinary siphon predicate."""

    place_set = set(places)
    if not place_set or not place_set.issubset(set(net.places)):
        return False
    for transition in net.transitions:
        if place_set.intersection(transition.outputs) and not place_set.intersection(
            transition.inputs
        ):
            return False
    return True


def minimal_empty_siphons(net: WaitSnapshotNet) -> tuple[tuple[str, ...], ...]:
    """Enumerate inclusion-minimal nonempty siphons empty under ``net.marking``."""

    candidates: list[tuple[str, ...]] = []
    for size in range(1, len(net.places) + 1):
        for subset in combinations(net.places, size):
            if any(set(candidate).issubset(subset) for candidate in candidates):
                continue
            if not all(net.marking[place] == 0 for place in subset):
                continue
            if is_siphon(net, subset):
                candidates.append(subset)
    return tuple(candidates)


def _check_sip1_assumptions(
    model: IMSModel,
    state: IMSState,
    certificate: DeadlockCertificate,
) -> str | None:
    if certificate.model_id != model.id:
        return "certificate model does not match model"
    if certificate.state_id != state.id:
        return "certificate state does not match state"
    if not state.stable:
        return "state is not stable after zero-time closure"
    if certificate.shortest_reachable_prefix is None:
        return "certificate has no reachability witness"
    if not certificate.is_minimal:
        return "certificate is not inclusion-minimal"
    if not certificate.kernel_jobs:
        return "certificate has empty core"

    core_jobs = set(certificate.kernel_jobs)
    core_resources = set(certificate.kernel_resources)
    for resource_id in sorted(core_resources):
        if model.capacity(resource_id) != 1:
            return (
                f"resource {resource_id} capacity {model.capacity(resource_id)} "
                "is not unit capacity"
            )
        if state.available_units(model, resource_id) != 0:
            return f"resource {resource_id} has residual availability"

    holds_by_job: dict[str, str] = {}
    expected_evidence: list[tuple[str, str, str, int]] = []
    for job_id in sorted(core_jobs):
        holdings = [
            holding
            for holding in state.holds
            if holding.job_id == job_id and holding.resource_id in core_resources
        ]
        if len(holdings) != 1:
            return f"job {job_id} does not hold exactly one core resource"
        holding = holdings[0]
        if holding.units != 1:
            return f"job {job_id} holds non-unit resource amount"
        holds_by_job[job_id] = holding.resource_id
        expected_evidence.append(("hold", holding.resource_id, job_id, holding.units))

    requests_by_job: dict[str, str] = {}
    for job_id in sorted(core_jobs):
        alternatives = state.requests.get(job_id, ())
        if len(alternatives) != 1:
            return f"job {job_id} has OR alternatives"
        alternative = alternatives[0]
        if len(alternative.demands) != 1:
            return f"job {job_id} alternative 0 has conjunctive demand"
        demand = alternative.demands[0]
        if demand.units != 1:
            return f"job {job_id} requests non-unit resource amount"
        if demand.resource_id not in core_resources:
            return f"job {job_id} requests resource outside core"
        requests_by_job[job_id] = demand.resource_id
        expected_evidence.append(("request", job_id, demand.resource_id, demand.units))

    actual_evidence = sorted(
        (edge.kind, edge.source, edge.target, edge.units)
        for edge in certificate.evidence_edges
    )
    if actual_evidence != sorted(expected_evidence):
        return "certificate evidence disagrees with model state"

    for resource_id in sorted(core_resources):
        holders = [
            job_id
            for job_id, held_resource in holds_by_job.items()
            if held_resource == resource_id
        ]
        if len(holders) != 1:
            return f"resource {resource_id} is not held by exactly one core job"

    return None
