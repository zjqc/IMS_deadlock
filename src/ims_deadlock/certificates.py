"""Deadlock-certificate construction for stable finite IMS states."""

from __future__ import annotations

from itertools import combinations

from ims_deadlock.model import DeadlockCertificate, IMSModel, IMSState


def find_deadlock_certificate(
    model: IMSModel, state: IMSState
) -> DeadlockCertificate | None:
    """Return a minimal closed blocking-kernel certificate when one exists."""

    if not state.stable or state.complete:
        return None

    jobs = sorted(state.blocked_jobs())
    for size in range(1, len(jobs) + 1):
        for subset_tuple in combinations(jobs, size):
            subset = frozenset(subset_tuple)
            resources = _requested_resources(state, subset)
            if resources and _is_closed_saturated_kernel(
                model, state, subset, resources
            ):
                return _certificate(model, state, subset, resources)
    return None


def _requested_resources(state: IMSState, jobs: frozenset[str]) -> frozenset[str]:
    resources: set[str] = set()
    for job in jobs:
        resources.update(state.requests.get(job, frozenset()))
    return frozenset(resources)


def _is_closed_saturated_kernel(
    model: IMSModel,
    state: IMSState,
    jobs: frozenset[str],
    resources: frozenset[str],
) -> bool:
    for job in jobs:
        requested = state.requests.get(job, frozenset())
        if not requested or requested.isdisjoint(resources):
            return False

    for resource_id in resources:
        holders = {
            job
            for job, held_resources in state.holds.items()
            if resource_id in held_resources
        }
        if not holders.issubset(jobs):
            return False
        if len(holders) < model.capacity(resource_id):
            return False
    return True


def _certificate(
    model: IMSModel,
    state: IMSState,
    jobs: frozenset[str],
    resources: frozenset[str],
) -> DeadlockCertificate:
    edges: list[tuple[str, str, str]] = []
    for job in sorted(jobs):
        for resource_id in sorted(state.holds.get(job, frozenset()) & resources):
            edges.append(("hold", resource_id, job))
        for resource_id in sorted(state.requests.get(job, frozenset()) & resources):
            edges.append(("request", job, resource_id))
    return DeadlockCertificate(
        model_id=model.id,
        state_id=state.id,
        kernel_jobs=jobs,
        kernel_resources=resources,
        evidence_edges=tuple(edges),
        assumptions=("stable_state", "capacity_saturation"),
        is_minimal=True,
    )
