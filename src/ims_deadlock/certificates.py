"""Deadlock-certificate construction for stable finite IMS states."""

from __future__ import annotations

from collections.abc import Iterable
from itertools import combinations

from ims_deadlock.engine import TransitionSpec
from ims_deadlock.model import (
    CapacityWitness,
    CertificateScope,
    DeadlockCertificate,
    EvidenceEdge,
    IMSModel,
    IMSState,
    RequestAlternative,
    ResourceDemand,
    validate_model_state,
)


def find_deadlock_certificate(
    model: IMSModel,
    state: IMSState,
    transitions: Iterable[TransitionSpec] = (),
    *,
    reachable_prefix: tuple[str, ...] | None = None,
) -> DeadlockCertificate | None:
    """Return a global operational deadlock certificate when one exists."""

    if not state.stable or state.complete or not state.event_calendar_empty:
        return None
    if not validate_model_state(model, state).valid:
        return None
    if any(_transition_enabled(model, state, transition) for transition in transitions):
        return None

    unfinished = state.unfinished_jobs(model)
    if not unfinished:
        return None
    if not unfinished.issubset(state.blocked_jobs(model)):
        return None
    transitions = tuple(transitions)
    return _certificate_for_jobs(
        model,
        state,
        unfinished,
        "global",
        transitions,
        reachable_prefix=reachable_prefix,
    )


def find_local_blocking_certificate(
    model: IMSModel,
    state: IMSState,
    transitions: Iterable[TransitionSpec] = (),
    *,
    reachable_prefix: tuple[str, ...] | None = None,
) -> DeadlockCertificate | None:
    """Return an inclusion-minimal local closed blocking-kernel certificate."""

    if not state.stable or state.complete:
        return None
    if not validate_model_state(model, state).valid:
        return None

    jobs = sorted(state.blocked_jobs(model))
    transitions = tuple(transitions)
    for size in range(1, len(jobs) + 1):
        for subset_tuple in combinations(jobs, size):
            certificate = _certificate_for_jobs(
                model,
                state,
                frozenset(subset_tuple),
                "local",
                transitions,
                reachable_prefix=reachable_prefix,
            )
            if certificate is not None:
                return certificate
    return None


def _certificate_for_jobs(
    model: IMSModel,
    state: IMSState,
    jobs: frozenset[str],
    scope: CertificateScope,
    transitions: tuple[TransitionSpec, ...],
    *,
    reachable_prefix: tuple[str, ...] | None,
) -> DeadlockCertificate | None:
    if _has_enabled_transition_for_jobs(model, state, jobs, transitions):
        return None
    resources = _minimal_witness_resources(model, state, jobs)
    if resources is None:
        return None
    return _certificate(
        model=model,
        state=state,
        jobs=jobs,
        resources=resources,
        scope=scope,
        is_minimal=not _has_proper_closed_kernel(model, state, jobs, resources),
        reachable_prefix=reachable_prefix,
    )


def _minimal_witness_resources(
    model: IMSModel, state: IMSState, jobs: frozenset[str]
) -> frozenset[str] | None:
    candidates = sorted(_candidate_witness_resources(model, state, jobs))
    for size in range(1, len(candidates) + 1):
        for subset_tuple in combinations(candidates, size):
            resources = frozenset(subset_tuple)
            if _covers_every_alternative(model, state, jobs, resources):
                return resources
    return None


def _candidate_witness_resources(
    model: IMSModel, state: IMSState, jobs: frozenset[str]
) -> frozenset[str]:
    resources: set[str] = set()
    for job in jobs:
        for alternative in state.requests.get(job, ()):
            for demand in alternative.demands:
                if _is_closed_blocking_witness(model, state, jobs, demand):
                    resources.add(demand.resource_id)
    return frozenset(resources)


def _covers_every_alternative(
    model: IMSModel,
    state: IMSState,
    jobs: frozenset[str],
    resources: frozenset[str],
) -> bool:
    for job in jobs:
        alternatives = state.requests.get(job, ())
        if not alternatives:
            return False
        for alternative in alternatives:
            if not _alternative_has_witness(model, state, jobs, alternative, resources):
                return False
    return True


def _alternative_has_witness(
    model: IMSModel,
    state: IMSState,
    jobs: frozenset[str],
    alternative: RequestAlternative,
    resources: frozenset[str],
) -> bool:
    return any(
        demand.resource_id in resources
        and _is_closed_blocking_witness(model, state, jobs, demand)
        for demand in alternative.demands
    )


def _is_closed_blocking_witness(
    model: IMSModel,
    state: IMSState,
    jobs: frozenset[str],
    demand: ResourceDemand,
) -> bool:
    holders = state.holders(demand.resource_id)
    if not holders or not holders.issubset(jobs):
        return False
    return state.held_units(demand.resource_id) + demand.units > model.capacity(
        demand.resource_id
    )


def _has_proper_closed_kernel(
    model: IMSModel,
    state: IMSState,
    jobs: frozenset[str],
    resources: frozenset[str],
) -> bool:
    ordered_jobs = sorted(jobs)
    for size in range(1, len(ordered_jobs)):
        for subset_tuple in combinations(ordered_jobs, size):
            subset = frozenset(subset_tuple)
            subset_resources = _minimal_witness_resources(model, state, subset)
            if subset_resources is not None and subset_resources.issubset(resources):
                return True

    ordered_resources = sorted(resources)
    for size in range(1, len(ordered_resources)):
        for subset_tuple in combinations(ordered_resources, size):
            subset_resources = frozenset(subset_tuple)
            if _covers_every_alternative(model, state, jobs, subset_resources):
                return True
    return False


def _has_enabled_transition_for_jobs(
    model: IMSModel,
    state: IMSState,
    jobs: frozenset[str],
    transitions: tuple[TransitionSpec, ...],
) -> bool:
    return any(
        transition.job_id in jobs and _transition_enabled(model, state, transition)
        for transition in transitions
    )


def _certificate(
    model: IMSModel,
    state: IMSState,
    jobs: frozenset[str],
    resources: frozenset[str],
    scope: CertificateScope,
    is_minimal: bool,
    reachable_prefix: tuple[str, ...] | None,
) -> DeadlockCertificate:
    edges: list[EvidenceEdge] = []
    capacity_witnesses: list[CapacityWitness] = []
    for holding in sorted(
        state.holds, key=lambda item: (item.resource_id, item.job_id, item.units)
    ):
        if holding.job_id in jobs and holding.resource_id in resources:
            edges.append(
                EvidenceEdge(
                    kind="hold",
                    source=holding.resource_id,
                    target=holding.job_id,
                    units=holding.units,
                )
            )
    for job in sorted(jobs):
        for alternative_index, alternative in enumerate(state.requests.get(job, ())):
            for demand in alternative.demands:
                if demand.resource_id in resources and _is_closed_blocking_witness(
                    model, state, jobs, demand
                ):
                    edges.append(
                        EvidenceEdge(
                            kind="request",
                            source=job,
                            target=demand.resource_id,
                            units=demand.units,
                        )
                    )
                    capacity_witnesses.append(
                        _capacity_witness(
                            model=model,
                            state=state,
                            jobs=jobs,
                            job=job,
                            alternative_index=alternative_index,
                            demand=demand,
                        )
                    )
    return DeadlockCertificate(
        model_id=model.id,
        state_id=state.id,
        kernel_jobs=jobs,
        kernel_resources=resources,
        evidence_edges=tuple(edges),
        assumptions=(
            "stable_zero_time_closure",
            "capacity_mediated_blocking",
            "closed_world_transition_registry",
            "all_enabled_transitions_supplied",
        ),
        is_minimal=is_minimal,
        scope=scope,
        zero_time_trace=state.zero_time_trace,
        capacity_witnesses=tuple(capacity_witnesses),
        shortest_reachable_prefix=reachable_prefix,
        corresponding_siphon=None,
        bridge_status="not_applicable_no_petri_subclass_mapping",
    )


def _capacity_witness(
    *,
    model: IMSModel,
    state: IMSState,
    jobs: frozenset[str],
    job: str,
    alternative_index: int,
    demand: ResourceDemand,
) -> CapacityWitness:
    capacity = model.capacity(demand.resource_id)
    held_units = state.held_units(demand.resource_id)
    residual_units = capacity - held_units
    shortage_units = demand.units - residual_units
    return CapacityWitness(
        job_id=job,
        alternative_index=alternative_index,
        resource_id=demand.resource_id,
        requested_units=demand.units,
        capacity=capacity,
        held_units=held_units,
        residual_units=residual_units,
        kernel_held_units=state.held_units_by_jobs(demand.resource_id, jobs),
        holders=tuple(state.holders(demand.resource_id)),
        shortage_units=shortage_units,
    )


def _transition_enabled(
    model: IMSModel, state: IMSState, transition: TransitionSpec
) -> bool:
    if state.mode_by_job.get(transition.job_id) != transition.source_mode:
        return False
    if transition.requires and not _requests_satisfied(
        model, state, transition.requires
    ):
        return False
    if transition.acquire and not _resources_available(
        model, state, transition.acquire
    ):
        return False
    if transition.release and not _resources_held(
        state, transition.job_id, transition.release
    ):
        return False
    return True


def _requests_satisfied(
    model: IMSModel, state: IMSState, requests: tuple[RequestAlternative, ...]
) -> bool:
    if not requests:
        return True
    for alternative in requests:
        if all(
            state.available_units(model, demand.resource_id) >= demand.units
            for demand in alternative.demands
        ):
            return True
    return False


def _resources_available(
    model: IMSModel, state: IMSState, demands: tuple[ResourceDemand, ...]
) -> bool:
    return all(
        state.available_units(model, demand.resource_id) >= demand.units
        for demand in demands
    )


def _resources_held(
    state: IMSState, job_id: str, demands: tuple[ResourceDemand, ...]
) -> bool:
    return all(
        state.held_units_by_jobs(demand.resource_id, {job_id}) >= demand.units
        for demand in demands
    )
