"""Structural analysis screens for small IMS-RAS case models."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from ims_deadlock.baselines import state_dependent_knot_screen
from ims_deadlock.cases import CASE_SCHEMA_VERSION, CaseSpec
from ims_deadlock.certificates import find_deadlock_certificate
from ims_deadlock.engine import (
    FiniteLTS,
    TransitionArc,
    TransitionSpec,
    apply_enabled_transition,
    configuration_signature,
    enabled_transition,
    exact_max_nonblocking_supervisor,
    transition_sort_key,
    zero_time_closure,
)
from ims_deadlock.model import (
    DeadlockCertificate,
    IMSModel,
    IMSState,
    RequestAlternative,
    Resource,
    ResourceDemand,
)

ANALYSIS_SCHEMA_VERSION = "ims-deadlock/analysis/v1"


@dataclass(frozen=True)
class LTSStateRecord:
    """A stable reachable state with deterministic ID and shortest witness."""

    state_id: str
    state: IMSState
    signature: tuple[object, ...]
    witness: tuple[str, ...]

    def to_json_dict(self) -> dict[str, object]:
        return {
            "state_id": self.state_id,
            "source_state_id": self.state.id,
            "signature": self.signature,
            "witness": list(self.witness),
            "complete": self.state.complete,
            "mode_by_job": dict(sorted(self.state.mode_by_job.items())),
            "completed_jobs": sorted(self.state.completed_jobs),
        }


@dataclass(frozen=True)
class StableLTSArc:
    """One non-zero transition arc between stable LTS states."""

    source: str
    event: str
    target: str
    controllable: bool
    edge_trace: tuple[str, ...]

    def to_engine_arc(self) -> TransitionArc:
        return (self.source, self.event, self.target, self.controllable)

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "event": self.event,
            "target": self.target,
            "controllable": self.controllable,
            "edge_trace": list(self.edge_trace),
        }


@dataclass(frozen=True)
class TruncatedArc:
    """A transition successor omitted from the exact graph by the state bound."""

    source: str
    event: str
    target_signature: tuple[object, ...]
    controllable: bool
    reason: str

    def to_json_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "event": self.event,
            "target_signature": self.target_signature,
            "controllable": self.controllable,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class StableLTS:
    """Bounded stable-state LTS enumeration result."""

    states: tuple[LTSStateRecord, ...]
    initial_state_id: str | None
    initial_state_ids: tuple[str, ...]
    transitions: tuple[StableLTSArc, ...]
    truncated_arcs: tuple[TruncatedArc, ...]
    marked_state_ids: tuple[str, ...]
    truncated: bool
    max_states: int
    unavailable_reasons: tuple[str, ...]

    def to_finite_lts(self) -> FiniteLTS | None:
        if not self.initial_state_ids:
            return None
        if len(self.initial_state_ids) == 1:
            initial_state = self.initial_state_ids[0]
            states = tuple(record.state_id for record in self.states)
            transitions = tuple(arc.to_engine_arc() for arc in self.transitions)
        else:
            initial_state = "__initial_closure__"
            states = (initial_state,) + tuple(record.state_id for record in self.states)
            transitions = tuple(
                (initial_state, f"initial->{state_id}", state_id, False)
                for state_id in self.initial_state_ids
            ) + tuple(arc.to_engine_arc() for arc in self.transitions)
        return FiniteLTS(
            states=states,
            initial_state=initial_state,
            marked_states=self.marked_state_ids,
            transitions=transitions,
        )

    def to_json_dict(self) -> dict[str, object]:
        return {
            "initial_state_id": self.initial_state_id,
            "initial_state_ids": list(self.initial_state_ids),
            "state_count": len(self.states),
            "transition_count": len(self.transitions),
            "marked_state_ids": list(self.marked_state_ids),
            "truncated": self.truncated,
            "max_states": self.max_states,
            "states": [state.to_json_dict() for state in self.states],
            "transitions": [arc.to_json_dict() for arc in self.transitions],
            "truncated_arcs": [arc.to_json_dict() for arc in self.truncated_arcs],
            "unavailable_reasons": list(self.unavailable_reasons),
        }


def enumerate_stable_lts(
    model: IMSModel,
    initial_state: IMSState,
    transitions: Iterable[TransitionSpec],
    *,
    max_states: int = 128,
) -> StableLTS:
    """Enumerate reachable stable states by bounded deterministic BFS."""

    if max_states <= 0:
        msg = "max_states must be positive"
        raise ValueError(msg)

    rules = tuple(sorted(transitions, key=transition_sort_key))
    unavailable: list[str] = []
    truncated = False
    records: list[LTSStateRecord] = []
    by_signature: dict[tuple[object, ...], LTSStateRecord] = {}
    queue: deque[LTSStateRecord] = deque()
    arcs: list[StableLTSArc] = []
    truncated_arcs: list[TruncatedArc] = []
    initial_state_ids: list[str] = []

    initial_closure = zero_time_closure(model, initial_state, rules)
    if not initial_closure.stable_states:
        return StableLTS(
            states=(),
            initial_state_id=None,
            initial_state_ids=(),
            transitions=(),
            truncated_arcs=(),
            marked_state_ids=(),
            truncated=False,
            max_states=max_states,
            unavailable_reasons=("zero_time_closure_nontermination",),
        )

    for stable, trace in sorted(
        initial_closure.stable_successors,
        key=lambda item: _stable_semantic_signature(item[0]),
    ):
        if len(records) >= max_states:
            truncated = True
            truncated_arcs.append(
                TruncatedArc(
                    source="__initial_closure__",
                    event="urgent_zero_time_closure",
                    target_signature=_stable_semantic_signature(stable),
                    controllable=False,
                    reason="max_states",
                )
            )
            break
        witness = tuple(event.name for event in trace)
        record = _record_for_state(stable, len(records), witness)
        records.append(record)
        by_signature[record.signature] = record
        queue.append(record)
        initial_state_ids.append(record.state_id)

    while queue:
        current = queue.popleft()
        for transition in rules:
            if transition.zero_time:
                continue
            if not enabled_transition(model, current.state, transition):
                continue
            next_state = apply_enabled_transition(model, current.state, transition)
            if next_state is None:
                continue
            closure = zero_time_closure(model, next_state, rules)
            if not closure.stable_states:
                unavailable.append("zero_time_closure_nontermination")
                continue
            for stable, trace in sorted(
                closure.stable_successors,
                key=lambda item: _stable_semantic_signature(item[0]),
            ):
                signature = _stable_semantic_signature(stable)
                target = by_signature.get(signature)
                if target is None:
                    if len(records) >= max_states:
                        truncated = True
                        truncated_arcs.append(
                            TruncatedArc(
                                source=current.state_id,
                                event=transition.name,
                                target_signature=signature,
                                controllable=transition.controllable,
                                reason="max_states",
                            )
                        )
                        continue
                    closure_witness = tuple(event.name for event in trace)
                    target = _record_for_state(
                        stable,
                        len(records),
                        current.witness + (transition.name,) + closure_witness,
                    )
                    records.append(target)
                    by_signature[signature] = target
                    queue.append(target)
                arc = StableLTSArc(
                    source=current.state_id,
                    event=transition.name,
                    target=target.state_id,
                    controllable=transition.controllable,
                    edge_trace=(transition.name,)
                    + tuple(event.name for event in trace),
                )
                if arc not in arcs:
                    arcs.append(arc)

    records = list(
        _records_with_shortest_event_witnesses(
            records,
            initial_state_ids=tuple(initial_state_ids),
            arcs=tuple(arcs),
        )
    )
    return StableLTS(
        states=tuple(records),
        initial_state_id=records[0].state_id if records else None,
        initial_state_ids=tuple(initial_state_ids),
        transitions=tuple(arcs),
        truncated_arcs=tuple(truncated_arcs),
        marked_state_ids=tuple(
            record.state_id for record in records if record.state.complete
        ),
        truncated=truncated,
        max_states=max_states,
        unavailable_reasons=tuple(sorted(set(unavailable))),
    )


def analyze_case(spec: CaseSpec, *, max_states: int = 128) -> dict[str, Any]:
    """Return versioned structural analysis for one case specification."""

    lts = enumerate_stable_lts(
        spec.model, spec.initial_state, spec.transitions, max_states=max_states
    )
    certificate_record = _shortest_certificate_record(lts, spec.model, spec.transitions)
    certificate = certificate_record[1] if certificate_record else None
    supervisor = _supervisor_payload(lts)
    screen_state = lts.states[0].state if lts.states else spec.initial_state
    finite_lts_terminal_scc = _terminal_scc_screen(lts)
    certificate_payload: dict[str, object] = {
        "available": certificate is not None,
        "certificate": certificate.to_json_dict() if certificate else None,
        "state_id": certificate_record[0].state_id if certificate_record else None,
        "reachability_witness": (
            list(certificate_record[0].witness) if certificate_record else None
        ),
        "reason": None if certificate else "no_reachable_closed_blocking_kernel",
    }
    return {
        "analysis_schema_version": ANALYSIS_SCHEMA_VERSION,
        "case_schema_version": CASE_SCHEMA_VERSION,
        "case_id": spec.case_id,
        "model_id": spec.model.id,
        "state_id": spec.initial_state.id,
        "provenance": {
            "analysis": "program_observation",
            "case_status": spec.status,
            "max_states": max_states,
        },
        "lts": lts.to_json_dict(),
        "screen_state_id": lts.states[0].state_id if lts.states else None,
        "wait_graph": _wait_graph_payload(spec.model, screen_state),
        "simple_cycle_screen": _simple_cycle_screen(spec.model, screen_state),
        "state_dependent_knot_screen": _reachable_knot_payload(lts, spec.model),
        "finite_lts_terminal_scc_screen": finite_lts_terminal_scc,
        "terminal_scc_screen": finite_lts_terminal_scc,
        "certificate": certificate_payload,
        "banker_snapshot": _banker_snapshot(spec.model, spec.initial_state),
        "supervisor": supervisor,
        "baselines": {
            "simple_cycle": "screening_only",
            "state_dependent_knot": (
                "capacity_aware_bipartite_wait_graph_baseline_after_closure"
            ),
            "finite_lts_terminal_scc": "screening_only_finite_lts_assumption",
            "banker": "limited_single_stage_or_alternative_snapshot",
            "projection": "diagnostic_only_not_a_valid_plant_claim",
        },
        "witness": {
            "initial": list(lts.states[0].witness) if lts.states else None,
            "first_completion": _first_completion_witness(lts),
        },
        "unavailable": {
            "siphon": "unavailable_without_petri_subclass",
            "ctmc_rates": "not_fabricated_by_structural_analysis",
        },
    }


def project_case_without_transport(spec: CaseSpec) -> CaseSpec:
    """Project AGV/reservation entities out for the C4 false-negative screen."""

    keep_resources = {
        resource_id: resource
        for resource_id, resource in spec.model.resources.items()
        if resource.kind not in {"agv", "reservation"}
    }
    model = IMSModel(
        id=f"{spec.model.id}-machine-buffer-projection",
        resources=keep_resources,
        jobs=spec.model.jobs,
    )
    state = IMSState(
        id=f"{spec.initial_state.id}-machine-buffer-projection",
        holds=tuple(
            holding
            for holding in spec.initial_state.holds
            if holding.resource_id in keep_resources
        ),
        requests={
            job_id: alternatives
            for job_id, alternatives in (
                (
                    job_id,
                    tuple(
                        alternative
                        for alternative in (
                            _project_alternative(alternative, keep_resources)
                            for alternative in alternatives
                        )
                        if alternative is not None
                    ),
                )
                for job_id, alternatives in spec.initial_state.requests.items()
            )
            if alternatives
        },
        completed_jobs=spec.initial_state.completed_jobs,
        stable=spec.initial_state.stable,
        complete=spec.initial_state.complete,
        event_calendar_empty=spec.initial_state.event_calendar_empty,
        stage_by_job=dict(spec.initial_state.stage_by_job),
        mode_by_job=dict(spec.initial_state.mode_by_job),
        zero_time_trace=spec.initial_state.zero_time_trace,
    )
    transitions = tuple(
        _project_transition(transition, keep_resources)
        for transition in spec.transitions
    )
    return CaseSpec(
        schema_version=spec.schema_version,
        case_id=f"{spec.case_id}_MACHINE_PROJECTION",
        title=f"{spec.title} machine/buffer projection",
        status=spec.status,
        model=model,
        initial_state=state,
        transitions=transitions,
        calendar=(),
        ctmc=None,
        ctmc_provenance=None,
        notes=spec.notes + ("AGV/reservation projection for false-negative screen.",),
    )


def _record_for_state(
    state: IMSState, ordinal: int, witness: tuple[str, ...]
) -> LTSStateRecord:
    signature = _stable_semantic_signature(state)
    return LTSStateRecord(
        state_id=f"s{ordinal}",
        state=state,
        signature=signature,
        witness=witness,
    )


def _records_with_shortest_event_witnesses(
    records: list[LTSStateRecord],
    *,
    initial_state_ids: tuple[str, ...],
    arcs: tuple[StableLTSArc, ...],
) -> tuple[LTSStateRecord, ...]:
    """Recompute witnesses by full event-count weight after graph enumeration."""

    best: dict[str, tuple[str, ...]] = {}
    record_by_id = {record.state_id: record for record in records}
    for state_id in initial_state_ids:
        record = record_by_id[state_id]
        best[state_id] = record.witness

    outgoing: dict[str, list[StableLTSArc]] = {
        record.state_id: [] for record in records
    }
    for arc in arcs:
        outgoing.setdefault(arc.source, []).append(arc)
    for source in outgoing:
        outgoing[source].sort(key=lambda arc: (arc.event, arc.target, arc.edge_trace))

    changed = True
    while changed:
        changed = False
        for state_id in sorted(outgoing):
            prefix = best.get(state_id)
            if prefix is None:
                continue
            for arc in outgoing[state_id]:
                candidate = prefix + arc.edge_trace
                current = best.get(arc.target)
                if current is None or _witness_key(candidate) < _witness_key(current):
                    best[arc.target] = candidate
                    changed = True

    return tuple(
        LTSStateRecord(
            state_id=record.state_id,
            state=record.state,
            signature=record.signature,
            witness=best.get(record.state_id, record.witness),
        )
        for record in records
    )


def _witness_key(witness: tuple[str, ...]) -> tuple[int, tuple[str, ...]]:
    return (len(witness), witness)


def _shortest_certificate_record(
    lts: StableLTS, model: IMSModel, transitions: Iterable[TransitionSpec]
) -> tuple[LTSStateRecord, DeadlockCertificate] | None:
    candidates = []
    for record in lts.states:
        certificate = find_deadlock_certificate(
            model,
            record.state,
            transitions,
            reachable_prefix=record.witness,
        )
        if certificate is None:
            continue
        candidates.append(
            (_witness_key(record.witness), record.state_id, record, certificate)
        )
    if not candidates:
        return None
    _witness, _state_id, record, certificate = min(candidates)
    return record, certificate


def _reachable_knot_payload(
    lts: StableLTS,
    model: IMSModel,
) -> dict[str, object]:
    if not lts.states:
        return {
            "available": False,
            "complete_search": not lts.truncated,
            "reason": "no_stable_lts_states",
            "states_screened": 0,
            "has_reachable_capacity_closed_knot": False,
            "matching_state_ids": [],
            "first_state_id": None,
            "reachability_witness": None,
            "screen": None,
        }

    matches: list[
        tuple[
            tuple[int, tuple[str, ...]],
            str,
            LTSStateRecord,
            dict[str, object],
        ]
    ] = []
    for record in lts.states:
        screen = state_dependent_knot_screen(model, record.state)
        if screen["has_capacity_closed_knot"] is not True:
            continue
        matches.append((_witness_key(record.witness), record.state_id, record, screen))

    if not matches:
        return {
            "available": True,
            "complete_search": not lts.truncated,
            "reason": (
                "not_observed_in_truncated_lts"
                if lts.truncated
                else "no_reachable_capacity_closed_knot"
            ),
            "states_screened": len(lts.states),
            "has_reachable_capacity_closed_knot": False,
            "matching_state_ids": [],
            "first_state_id": None,
            "reachability_witness": None,
            "screen": None,
        }

    _key, _state_id, first_record, first_screen = min(matches)
    return {
        "available": True,
        "complete_search": not lts.truncated,
        "reason": None,
        "states_screened": len(lts.states),
        "has_reachable_capacity_closed_knot": True,
        "matching_state_ids": sorted(match[2].state_id for match in matches),
        "first_state_id": first_record.state_id,
        "reachability_witness": list(first_record.witness),
        "screen": first_screen,
    }


def _stable_semantic_signature(state: IMSState) -> tuple[object, ...]:
    return configuration_signature(state) + (
        state.stable,
        state.complete,
        state.event_calendar_empty,
    )


def _wait_graph_payload(model: IMSModel, state: IMSState) -> dict[str, object]:
    edges: list[dict[str, object]] = []
    for holding in sorted(
        state.holds, key=lambda item: (item.resource_id, item.job_id)
    ):
        edges.append(
            {
                "kind": "hold",
                "source": f"resource:{holding.resource_id}",
                "target": f"job:{holding.job_id}",
                "units": holding.units,
            }
        )
    for job_id in sorted(state.requests):
        for alternative_index, alternative in enumerate(state.requests[job_id]):
            for demand in alternative.demands:
                if demand.resource_id not in model.resources:
                    continue
                edges.append(
                    {
                        "kind": "request",
                        "source": f"job:{job_id}",
                        "target": f"resource:{demand.resource_id}",
                        "units": demand.units,
                        "alternative_index": alternative_index,
                    }
                )
    return {
        "nodes": sorted(
            {f"job:{job}" for job in model.jobs}
            | {f"resource:{resource_id}" for resource_id in model.resources}
        ),
        "edges": edges,
    }


def _simple_cycle_screen(model: IMSModel, state: IMSState) -> dict[str, object]:
    graph = _adjacency_from_wait_graph(_wait_graph_payload(model, state))
    cycle = _find_cycle(graph)
    return {
        "screen_only": True,
        "has_cycle": bool(cycle),
        "cycle": cycle,
        "assumption": "directed_resource_job_wait_graph_ignores_capacity_sufficiency",
    }


def _terminal_scc_screen(lts: StableLTS) -> dict[str, object]:
    graph = {record.state_id: set[str]() for record in lts.states}
    for arc in lts.transitions:
        graph.setdefault(arc.source, set()).add(arc.target)
    components = _strongly_connected_components(graph)
    terminal_components: list[list[str]] = []
    for component in components:
        component_set = set(component)
        if any(
            target not in component_set
            for source in component
            for target in graph.get(source, set())
        ):
            continue
        if not component_set & set(lts.marked_state_ids):
            terminal_components.append(sorted(component))
    return {
        "screen_only": True,
        "available": not lts.truncated,
        "assumption": "finite_nontruncated_lts_terminal_unmarked_scc_screen",
        "terminal_unmarked_sccs": sorted(terminal_components),
    }


def _banker_snapshot(model: IMSModel, state: IMSState) -> dict[str, object]:
    work = {
        resource_id: state.available_units(model, resource_id)
        for resource_id in sorted(model.resources)
    }
    remaining = set(state.unfinished_jobs(model))
    sequence: list[str] = []
    changed = True
    while changed:
        changed = False
        for job_id in sorted(remaining):
            alternatives = state.requests.get(job_id, ())
            can_finish = not alternatives or any(
                all(
                    work[demand.resource_id] >= demand.units
                    for demand in alternative.demands
                )
                for alternative in alternatives
            )
            if not can_finish:
                continue
            sequence.append(job_id)
            remaining.remove(job_id)
            for holding in state.holds:
                if holding.job_id == job_id:
                    work[holding.resource_id] += holding.units
            changed = True
            break
    return {
        "safe": not remaining,
        "sequence": sequence,
        "blocked_jobs": sorted(remaining),
        "assumptions": [
            "snapshot_only",
            "single_stage_finish_releases_current_holds",
            "or_alternatives_choose_one_satisfied_option",
            "future_route_demands_ignored",
        ],
    }


def _supervisor_payload(lts: StableLTS) -> dict[str, object]:
    if lts.truncated:
        return {
            "available": False,
            "reason": "lts_truncated",
            "initial_state_ids": list(lts.initial_state_ids),
        }
    if not lts.marked_state_ids:
        return {
            "available": False,
            "reason": "no_marked_completion_reachable",
            "initial_state_ids": list(lts.initial_state_ids),
        }
    finite_lts = lts.to_finite_lts()
    if finite_lts is None:
        return {
            "available": False,
            "reason": "lts_unavailable",
            "initial_state_ids": list(lts.initial_state_ids),
        }
    policy = exact_max_nonblocking_supervisor(finite_lts)
    safe_states = set(policy.safe_states)
    unsafe_initials = tuple(
        state_id for state_id in lts.initial_state_ids if state_id not in safe_states
    )
    return {
        "available": True,
        "safe_states": list(policy.safe_states),
        "coaccessible_states": list(policy.coaccessible_states),
        "disabled_transitions": list(policy.disabled_transitions),
        "disabled_state_events": [list(item) for item in policy.disabled_state_events],
        "initial_state_feasible": not unsafe_initials,
        "policy_initial_state_feasible": policy.initial_state_feasible,
        "initial_state_ids": list(lts.initial_state_ids),
        "unsafe_initial_state_ids": list(unsafe_initials),
        "forbidden_states": list(policy.forbidden_states),
        "dead_states": list(policy.dead_states),
    }


def _first_completion_witness(lts: StableLTS) -> list[str] | None:
    for state in lts.states:
        if state.state.complete:
            return list(state.witness)
    return None


def _adjacency_from_wait_graph(payload: dict[str, object]) -> dict[str, set[str]]:
    raw_nodes = payload["nodes"]
    nodes = {str(node) for node in raw_nodes} if isinstance(raw_nodes, list) else set()
    graph = {node: set[str]() for node in nodes}
    edges = payload["edges"]
    if not isinstance(edges, list):
        return graph
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        edge_payload = dict(edge)
        graph.setdefault(str(edge_payload["source"]), set()).add(
            str(edge_payload["target"])
        )
    return graph


def _find_cycle(graph: dict[str, set[str]]) -> list[str]:
    visited: set[str] = set()
    active: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> list[str]:
        visited.add(node)
        active.add(node)
        stack.append(node)
        for target in sorted(graph.get(node, set())):
            if target not in visited:
                found = visit(target)
                if found:
                    return found
            elif target in active:
                start = stack.index(target)
                return stack[start:] + [target]
        active.remove(node)
        stack.pop()
        return []

    for node in sorted(graph):
        if node in visited:
            continue
        found = visit(node)
        if found:
            return found
    return []


def _strongly_connected_components(graph: dict[str, set[str]]) -> list[list[str]]:
    index = 0
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[list[str]] = []

    def strongconnect(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in sorted(graph.get(node, set())):
            if target not in indices:
                strongconnect(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[target])
        if lowlinks[node] != indices[node]:
            return
        component: list[str] = []
        while True:
            member = stack.pop()
            on_stack.remove(member)
            component.append(member)
            if member == node:
                break
        components.append(sorted(component))

    for node in sorted(graph):
        if node not in indices:
            strongconnect(node)
    return components


def _project_transition(
    transition: TransitionSpec, resources: dict[str, Resource]
) -> TransitionSpec:
    return TransitionSpec(
        name=transition.name,
        kind=transition.kind,
        job_id=transition.job_id,
        source_mode=transition.source_mode,
        target_mode=transition.target_mode,
        controllable=transition.controllable,
        zero_time=transition.zero_time,
        urgent=transition.urgent,
        acquire=_project_demands(transition.acquire, resources),
        release=_project_demands(transition.release, resources),
        requires=tuple(
            alternative
            for alternative in (
                _project_alternative(alternative, resources)
                for alternative in transition.requires
            )
            if alternative is not None
        ),
        next_requests=tuple(
            alternative
            for alternative in (
                _project_alternative(alternative, resources)
                for alternative in transition.next_requests
            )
            if alternative is not None
        ),
        clears_requests=transition.clears_requests,
        mark_complete=transition.mark_complete,
    )


def _project_alternative(
    alternative: RequestAlternative, resources: dict[str, Resource]
) -> RequestAlternative | None:
    demands = _project_demands(alternative.demands, resources)
    if not demands:
        return None
    return RequestAlternative(demands)


def _project_demands(
    demands: tuple[ResourceDemand, ...], resources: dict[str, Resource]
) -> tuple[ResourceDemand, ...]:
    return tuple(demand for demand in demands if demand.resource_id in resources)
