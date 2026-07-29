"""Executable IMS-RAS semantics for small finite models."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass, field

from ims_deadlock.model import (
    Holding,
    IMSModel,
    IMSState,
    RequestAlternative,
    ResourceDemand,
)


class EventKind:
    """Canonical event-kind labels used by the executable semantics."""

    RELEASE = "release"
    UNLOAD = "unload"
    START = "start"
    DISPATCH = "dispatch"
    SERVICE_COMPLETE = "service_complete"
    TRANSPORT_COMPLETE = "transport_complete"
    RESERVE = "reserve"
    REDEEM = "redeem"
    CANCEL = "cancel"


EVENT_PRIORITY: dict[str, int] = {
    EventKind.RELEASE: 0,
    EventKind.UNLOAD: 1,
    EventKind.START: 2,
    EventKind.DISPATCH: 3,
    EventKind.RESERVE: 4,
    EventKind.REDEEM: 5,
    EventKind.CANCEL: 6,
    EventKind.SERVICE_COMPLETE: 7,
    EventKind.TRANSPORT_COMPLETE: 8,
}


@dataclass(frozen=True)
class TransitionSpec:
    """A single executable transition rule for one job."""

    name: str
    kind: str
    job_id: str
    source_mode: str
    target_mode: str
    controllable: bool
    zero_time: bool
    urgent: bool = False
    clears_requests: bool = False
    acquire: tuple[ResourceDemand, ...] = field(default_factory=tuple)
    release: tuple[ResourceDemand, ...] = field(default_factory=tuple)
    requires: tuple[RequestAlternative, ...] = field(default_factory=tuple)
    next_requests: tuple[RequestAlternative, ...] = field(default_factory=tuple)
    mark_complete: bool = False

    def __post_init__(self) -> None:
        if self.urgent and self.zero_time and self.controllable:
            msg = "urgent zero-time transition must be uncontrollable"
            raise ValueError(msg)
        object.__setattr__(self, "acquire", _normalize_resource_demands(self.acquire))
        object.__setattr__(self, "release", _normalize_resource_demands(self.release))
        if self.clears_requests and self.next_requests:
            msg = "clear-request transition must not also provide next_requests"
            raise ValueError(msg)


@dataclass(frozen=True)
class ScheduledEvent:
    """A timed event on the simulation calendar."""

    time: float
    name: str
    job_id: str
    kind: str


@dataclass(frozen=True)
class ZeroTimeClosureResult:
    """Deterministic set-valued zero-time closure result."""

    stable_states: tuple[IMSState, ...]
    canonical_trace: tuple[TransitionSpec, ...]
    explored_states: tuple[IMSState, ...] = field(default_factory=tuple)
    stable_successors: tuple[tuple[IMSState, tuple[TransitionSpec, ...]], ...] = field(
        default_factory=tuple
    )


@dataclass(frozen=True)
class SimulationClosureBranch:
    """One stable successor of a non-confluent urgent closure."""

    state: IMSState
    zero_time_trace: tuple[str, ...]

    def to_json_dict(self) -> dict[str, object]:
        return {
            "state_id": self.state.id,
            "mode_by_job": dict(sorted(self.state.mode_by_job.items())),
            "completed_jobs": sorted(self.state.completed_jobs),
            "zero_time_trace": list(self.zero_time_trace),
        }


@dataclass(frozen=True)
class SimulationResult:
    """Finite simulation summary with explicit terminal classification."""

    terminal_classification: str
    unfinished_jobs: tuple[str, ...]
    final_state: IMSState
    canonical_trace: tuple[str, ...]
    closure_branches: tuple[SimulationClosureBranch, ...] = field(default_factory=tuple)


TransitionArc = tuple[str, str, str, bool]


@dataclass(frozen=True)
class FiniteLTS:
    """Finite labeled transition system."""

    states: tuple[str, ...]
    initial_state: str
    marked_states: tuple[str, ...]
    transitions: tuple[TransitionArc, ...]

    def outgoing(self, state: str) -> tuple[TransitionArc, ...]:
        return tuple(arc for arc in self.transitions if arc[0] == state)


@dataclass(frozen=True)
class SupervisorPolicy:
    """Exact greatest nonblocking supervisor on a finite LTS."""

    safe_states: tuple[str, ...]
    coaccessible_states: tuple[str, ...]
    disabled_transitions: tuple[str, ...]
    disabled_state_events: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    initial_state_feasible: bool = False
    forbidden_states: tuple[str, ...] = field(default_factory=tuple)
    dead_states: tuple[str, ...] = field(default_factory=tuple)


def zero_time_closure(
    model: IMSModel,
    state: IMSState,
    transitions: Iterable[TransitionSpec],
) -> ZeroTimeClosureResult:
    """Compute the canonical zero-time closure from a state."""

    zero_time_rules = tuple(
        sorted(
            (
                transition
                for transition in transitions
                if (
                    transition.zero_time
                    and transition.urgent
                    and not transition.controllable
                )
            ),
            key=_transition_sort_key,
        )
    )
    initial = _normalize_state(state)
    queue: deque[tuple[IMSState, tuple[TransitionSpec, ...]]] = deque([(initial, ())])
    seen: set[tuple[object, ...]] = {configuration_signature(initial)}
    stable: dict[tuple[object, ...], tuple[IMSState, tuple[TransitionSpec, ...]]] = {}
    explored: dict[tuple[object, ...], IMSState] = {
        configuration_signature(initial): initial
    }

    while queue:
        current, trace = queue.popleft()
        enabled = [
            transition
            for transition in zero_time_rules
            if _enabled(model, current, transition)
        ]
        if not enabled:
            key = configuration_signature(current)
            stable.setdefault(key, (current, trace))
            continue
        for transition in enabled:
            next_state = _apply_transition(model, current, transition)
            if next_state is None:
                continue
            next_key = configuration_signature(next_state)
            if next_key in seen:
                continue
            seen.add(next_key)
            explored[next_key] = next_state
            queue.append((next_state, trace + (transition,)))

    stable_items = sorted(stable.items(), key=lambda item: item[0])
    stable_states = tuple(item[1][0] for item in stable_items)
    canonical_trace = stable_items[0][1][1] if stable_items else ()
    explored_states = tuple(state for _key, state in sorted(explored.items()))
    return ZeroTimeClosureResult(
        stable_states=stable_states,
        canonical_trace=canonical_trace,
        explored_states=explored_states,
        stable_successors=tuple(item[1] for item in stable_items),
    )


def simulate(
    model: IMSModel,
    state: IMSState,
    transitions: Iterable[TransitionSpec],
    calendar: tuple[ScheduledEvent, ...] = (),
) -> SimulationResult:
    """Simulate a finite calendar until the next explicit terminal class."""

    current = _normalize_state(state)
    trace: list[str] = []
    calendar_queue = tuple(
        sorted(calendar, key=lambda item: (item.time, item.job_id, item.name))
    )
    transitions = tuple(transitions)

    while True:
        closure = zero_time_closure(model, current, transitions)
        if not closure.stable_successors:
            return SimulationResult(
                terminal_classification="zero_time_closure_nontermination",
                unfinished_jobs=tuple(sorted(current.unfinished_jobs(model))),
                final_state=current,
                canonical_trace=tuple(trace),
            )
        if len(closure.stable_successors) > 1:
            branches = tuple(
                SimulationClosureBranch(
                    state=stable,
                    zero_time_trace=tuple(event.name for event in branch_trace),
                )
                for stable, branch_trace in closure.stable_successors
            )
            unfinished = tuple(
                sorted(
                    {
                        job
                        for branch in branches
                        for job in branch.state.unfinished_jobs(model)
                    }
                )
            )
            return SimulationResult(
                terminal_classification="nonconfluent_zero_time_closure",
                unfinished_jobs=unfinished,
                final_state=current,
                canonical_trace=tuple(trace),
                closure_branches=branches,
            )
        current, closure_trace = closure.stable_successors[0]
        trace.extend(transition.name for transition in closure_trace)
        unfinished = tuple(sorted(current.unfinished_jobs(model)))

        if current.complete or not unfinished:
            return SimulationResult(
                terminal_classification="complete",
                unfinished_jobs=(),
                final_state=current,
                canonical_trace=tuple(trace),
            )

        if _has_capacity_deadlock_evidence(model, current, transitions):
            return SimulationResult(
                terminal_classification="capacity_deadlock",
                unfinished_jobs=unfinished,
                final_state=current,
                canonical_trace=tuple(trace),
            )

        if calendar_queue:
            next_event, *rest = calendar_queue
            fired_state = _fire_calendar_event(model, current, transitions, next_event)
            calendar_queue = tuple(rest)
            if fired_state is None:
                return SimulationResult(
                    terminal_classification="calendar_mismatch",
                    unfinished_jobs=unfinished,
                    final_state=current,
                    canonical_trace=tuple(trace),
                )
            current = fired_state
            if not calendar_queue:
                current = _set_event_calendar_empty(current, True)
            continue

        if current.event_calendar_empty:
            if unfinished and set(unfinished).issubset(current.blocked_jobs(model)):
                return SimulationResult(
                    terminal_classification="calendar_empty_terminal_block",
                    unfinished_jobs=unfinished,
                    final_state=current,
                    canonical_trace=tuple(trace),
                )
            return SimulationResult(
                terminal_classification="model_incomplete",
                unfinished_jobs=unfinished,
                final_state=current,
                canonical_trace=tuple(trace),
            )

        if not transitions:
            return SimulationResult(
                terminal_classification="model_incomplete",
                unfinished_jobs=unfinished,
                final_state=current,
                canonical_trace=tuple(trace),
            )

        if _has_enabled_controllable_decision(model, current, transitions):
            return SimulationResult(
                terminal_classification="policy_induced_stall",
                unfinished_jobs=unfinished,
                final_state=current,
                canonical_trace=tuple(trace),
            )

        return SimulationResult(
            terminal_classification="calendar_mismatch",
            unfinished_jobs=unfinished,
            final_state=current,
            canonical_trace=tuple(trace),
        )


def exact_max_nonblocking_supervisor(
    lts: FiniteLTS,
    *,
    forbidden_states: Iterable[str] = (),
    dead_states: Iterable[str] = (),
) -> SupervisorPolicy:
    """Greatest fixed point of the exact finite-state nonblocking supervisor."""

    _validate_lts(lts)
    allowed = set(lts.states)
    marked = set(lts.marked_states)
    transitions = tuple(lts.transitions)
    outgoing_by_state = {
        state: [arc for arc in transitions if arc[0] == state] for state in lts.states
    }
    forbidden = set(forbidden_states)
    dead = set(dead_states)
    if not forbidden.issubset(allowed):
        msg = "explicit forbidden states must belong to the LTS"
        raise ValueError(msg)
    if not dead.issubset(allowed):
        msg = "explicit dead states must belong to the LTS"
        raise ValueError(msg)
    allowed -= forbidden | dead

    changed = True
    while changed:
        changed = False
        coaccessible = _reverse_reachable_to_marked(allowed, marked, transitions)
        newly_dead = allowed - coaccessible
        if newly_dead:
            allowed -= newly_dead
            dead |= newly_dead
            changed = True
            continue

        newly_forbidden = {
            state
            for state in allowed
            if any(
                (not controllable) and target not in allowed
                for _source, _event, target, controllable in outgoing_by_state[state]
            )
        }
        if newly_forbidden:
            allowed -= newly_forbidden
            forbidden |= newly_forbidden
            changed = True

    coaccessible = _reverse_reachable_to_marked(allowed, marked, transitions)
    disabled_state_events = sorted(
        (source, event)
        for source, event, target, controllable in transitions
        if controllable and (source not in allowed or target not in allowed)
    )
    disabled_transitions = sorted(event for _source, event in disabled_state_events)
    safe = tuple(sorted(allowed & coaccessible))
    coaccessible_states = tuple(sorted(coaccessible & allowed))
    return SupervisorPolicy(
        safe_states=safe,
        coaccessible_states=coaccessible_states,
        disabled_transitions=tuple(disabled_transitions),
        disabled_state_events=tuple(disabled_state_events),
        initial_state_feasible=lts.initial_state in safe,
        forbidden_states=tuple(sorted(forbidden)),
        dead_states=tuple(sorted(dead)),
    )


def configuration_signature(state: IMSState) -> tuple[object, ...]:
    """Hashable state configuration used for zero-time closure cycle detection."""

    return (
        tuple(sorted(state.mode_by_job.items())),
        tuple(sorted(state.stage_by_job.items())),
        tuple(
            (holding.job_id, holding.resource_id, holding.units)
            for holding in sorted(
                state.holds,
                key=lambda item: (item.job_id, item.resource_id, item.units),
            )
        ),
        tuple(
            (
                job_id,
                tuple(
                    tuple(
                        (demand.resource_id, demand.units)
                        for demand in alternative.demands
                    )
                    for alternative in alternatives
                ),
            )
            for job_id, alternatives in sorted(state.requests.items())
        ),
        tuple(sorted(state.completed_jobs)),
    )


def semantic_signature(state: IMSState) -> tuple[object, ...]:
    """Hashable semantic signature including terminal-relevant state facts."""

    return configuration_signature(state) + (
        state.stable,
        state.complete,
        state.event_calendar_empty,
        state.zero_time_trace,
    )


def transition_sort_key(transition: TransitionSpec) -> tuple[int, str, str]:
    """Public deterministic transition order used by analyses."""

    return _transition_sort_key(transition)


def enabled_transition(
    model: IMSModel, state: IMSState, transition: TransitionSpec
) -> bool:
    """Return whether a transition is enabled under the executable semantics."""

    return _enabled(model, state, transition)


def apply_enabled_transition(
    model: IMSModel, state: IMSState, transition: TransitionSpec
) -> IMSState | None:
    """Apply an enabled transition under the executable semantics."""

    return _apply_transition(model, state, transition)


def _transition_sort_key(transition: TransitionSpec) -> tuple[int, str, str]:
    return (
        EVENT_PRIORITY.get(transition.kind, 99),
        transition.job_id,
        transition.name,
    )


def _normalize_state(state: IMSState) -> IMSState:
    return IMSState(
        id=state.id,
        holds=state.holds,
        requests=state.requests,
        completed_jobs=state.completed_jobs,
        stable=state.stable,
        complete=state.complete,
        event_calendar_empty=state.event_calendar_empty,
        stage_by_job=dict(state.stage_by_job),
        mode_by_job=dict(state.mode_by_job),
        zero_time_trace=state.zero_time_trace,
    )


def _set_event_calendar_empty(state: IMSState, event_calendar_empty: bool) -> IMSState:
    return IMSState(
        id=state.id,
        holds=state.holds,
        requests=state.requests,
        completed_jobs=state.completed_jobs,
        stable=state.stable,
        complete=state.complete,
        event_calendar_empty=event_calendar_empty,
        stage_by_job=dict(state.stage_by_job),
        mode_by_job=dict(state.mode_by_job),
        zero_time_trace=state.zero_time_trace,
    )


def _enabled(model: IMSModel, state: IMSState, transition: TransitionSpec) -> bool:
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


def _enabled_zero_time_transitions(
    model: IMSModel, state: IMSState, transitions: Iterable[TransitionSpec]
) -> tuple[TransitionSpec, ...]:
    return tuple(
        transition
        for transition in transitions
        if transition.zero_time and _enabled(model, state, transition)
    )


def _requests_satisfied(
    model: IMSModel,
    state: IMSState,
    requests: tuple[RequestAlternative, ...],
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


def _has_enabled_controllable_decision(
    model: IMSModel, state: IMSState, transitions: Iterable[TransitionSpec]
) -> bool:
    return any(
        transition.controllable
        and not transition.zero_time
        and _enabled(model, state, transition)
        for transition in transitions
    )


def _matches_calendar_event(event: ScheduledEvent, transition: TransitionSpec) -> bool:
    return (
        event.name == transition.name
        and event.job_id == transition.job_id
        and event.kind == transition.kind
    )


def _fire_calendar_event(
    model: IMSModel,
    state: IMSState,
    transitions: Iterable[TransitionSpec],
    event: ScheduledEvent,
) -> IMSState | None:
    candidates = [
        transition
        for transition in transitions
        if not transition.zero_time and _matches_calendar_event(event, transition)
    ]
    for transition in sorted(candidates, key=_transition_sort_key):
        if not _enabled(model, state, transition):
            continue
        next_state = _apply_transition(model, state, transition)
        if next_state is not None:
            return next_state
    return None


def _apply_transition(
    model: IMSModel, state: IMSState, transition: TransitionSpec
) -> IMSState | None:
    if not _enabled(model, state, transition):
        return None

    new_holds = _remove_holding(
        list(state.holds), transition.job_id, *transition.release
    )
    if new_holds is None:
        return None
    for demand in transition.acquire:
        new_holds.append(
            _make_holding(transition.job_id, demand.resource_id, demand.units)
        )

    mode_by_job = dict(state.mode_by_job)
    mode_by_job[transition.job_id] = transition.target_mode
    stage_by_job = dict(state.stage_by_job)
    stage_by_job[transition.job_id] = transition.target_mode
    if transition.target_mode == "completed" or transition.mark_complete:
        completed_jobs = frozenset(set(state.completed_jobs) | {transition.job_id})
    else:
        completed_jobs = state.completed_jobs

    if transition.clears_requests:
        requests = dict(state.requests)
        requests.pop(transition.job_id, None)
    elif transition.next_requests:
        requests = {**state.requests, transition.job_id: transition.next_requests}
    else:
        requests = dict(state.requests)

    complete = len(completed_jobs) == len(model.jobs) and not new_holds and not requests

    return IMSState(
        id=state.id,
        holds=tuple(
            sorted(
                new_holds,
                key=lambda item: (item.job_id, item.resource_id, item.units),
            )
        ),
        requests={
            job_id: tuple(alternatives)
            for job_id, alternatives in sorted(requests.items())
        },
        completed_jobs=completed_jobs,
        stable=True,
        complete=complete,
        event_calendar_empty=state.event_calendar_empty,
        stage_by_job=stage_by_job,
        mode_by_job=mode_by_job,
        zero_time_trace=(
            state.zero_time_trace + (transition.name,)
            if transition.zero_time
            else state.zero_time_trace
        ),
    )


def _validate_lts(lts: FiniteLTS) -> None:
    if len(set(lts.states)) != len(lts.states):
        msg = "LTS states must be unique"
        raise ValueError(msg)
    if lts.initial_state not in lts.states:
        msg = "LTS initial state must belong to the state set"
        raise ValueError(msg)
    if len(set(lts.marked_states)) != len(lts.marked_states):
        msg = "LTS marked states must be unique"
        raise ValueError(msg)
    if not set(lts.marked_states).issubset(lts.states):
        msg = "LTS marked states must belong to the state set"
        raise ValueError(msg)
    for source, _event, target, _controllable in lts.transitions:
        if source not in lts.states or target not in lts.states:
            msg = "LTS transitions must stay inside the state set"
            raise ValueError(msg)


def _has_capacity_deadlock_evidence(
    model: IMSModel, state: IMSState, transitions: Iterable[TransitionSpec]
) -> bool:
    unfinished = state.unfinished_jobs(model)
    if not unfinished:
        return False
    if not unfinished.issubset(state.blocked_jobs(model)):
        return False
    return not any(_enabled(model, state, transition) for transition in transitions)


def _remove_holding(
    holdings: list[Holding], job_id: str, *demands: ResourceDemand
) -> list[Holding] | None:
    remaining = list(holdings)
    updated: list[Holding] = []
    for demand in demands:
        needed = demand.units
        next_pass: list[Holding] = []
        for holding in remaining:
            if (
                holding.job_id == job_id
                and holding.resource_id == demand.resource_id
                and needed > 0
            ):
                take = min(holding.units, needed)
                needed -= take
                leftover = holding.units - take
                if leftover > 0:
                    next_pass.append(
                        _make_holding(job_id, demand.resource_id, leftover)
                    )
            else:
                next_pass.append(holding)
        if needed > 0:
            return None
        remaining = next_pass
    updated.extend(remaining)
    return updated


def _make_holding(job_id: str, resource_id: str, units: int) -> Holding:
    return Holding(job_id, resource_id, units)


def _reverse_reachable_to_marked(
    allowed: set[str],
    marked: set[str],
    transitions: tuple[TransitionArc, ...],
) -> set[str]:
    reverse: dict[str, set[str]] = {state: set() for state in allowed}
    for source, _event, target, _controllable in transitions:
        if source in allowed and target in allowed:
            reverse.setdefault(target, set()).add(source)
    stack = [state for state in marked if state in allowed]
    reachable = set(stack)
    while stack:
        state = stack.pop()
        for predecessor in reverse.get(state, set()):
            if predecessor in reachable:
                continue
            reachable.add(predecessor)
            stack.append(predecessor)
    return reachable


def _normalize_resource_demands(
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
