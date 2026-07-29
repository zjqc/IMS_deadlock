"""Auditable structural baselines for stable IMS-RAS states."""

from __future__ import annotations

from collections import defaultdict

from ims_deadlock.model import IMSModel, IMSState, validate_model_state


def state_dependent_knot_screen(
    model: IMSModel,
    state: IMSState,
) -> dict[str, object]:
    """Screen a stable state for capacity-aware terminal wait-graph knots.

    The screen uses only resource shortages that block every legal alternative
    of a job.  It is a reproducible structural baseline, not a replacement for
    the project-specific closed-blocking-kernel theorem.
    """

    if not state.stable:
        return _unavailable_knot_payload("state_not_zero_time_closed")
    validation = validate_model_state(model, state)
    if not validation.valid:
        return _unavailable_knot_payload("invalid_model_state")

    blocked_jobs = state.blocked_jobs(model)
    graph: dict[str, set[str]] = {}
    edges: list[dict[str, object]] = []

    def add_edge(
        source: str,
        target: str,
        payload: dict[str, object],
    ) -> None:
        graph.setdefault(source, set()).add(target)
        graph.setdefault(target, set())
        edges.append({"source": source, "target": target, **payload})

    blocking_resources: set[str] = set()
    for job_id in sorted(blocked_jobs):
        job_node = _job_node(job_id)
        graph.setdefault(job_node, set())
        alternatives = state.requests.get(job_id, ())
        for alternative_index, alternative in enumerate(alternatives):
            for demand in alternative.demands:
                if demand.resource_id not in model.resources:
                    continue
                residual = state.available_units(model, demand.resource_id)
                if residual >= demand.units:
                    continue
                blocking_resources.add(demand.resource_id)
                add_edge(
                    job_node,
                    _resource_node(demand.resource_id),
                    {
                        "kind": "blocking_request",
                        "job_id": job_id,
                        "resource_id": demand.resource_id,
                        "alternative_index": alternative_index,
                        "demand_units": demand.units,
                        "residual_units": residual,
                        "shortage_units": demand.units - residual,
                    },
                )

    held_units: dict[tuple[str, str], int] = defaultdict(int)
    for holding in state.holds:
        if holding.resource_id in blocking_resources:
            held_units[(holding.resource_id, holding.job_id)] += holding.units
    for (resource_id, job_id), units in sorted(held_units.items()):
        add_edge(
            _resource_node(resource_id),
            _job_node(job_id),
            {
                "kind": "hold",
                "job_id": job_id,
                "resource_id": resource_id,
                "units": units,
            },
        )

    components = _strongly_connected_components(graph)
    terminal_components: list[dict[str, object]] = []
    capacity_closed_knots: list[dict[str, object]] = []
    for component in components:
        component_set = set(component)
        cyclic = len(component) > 1 or any(
            node in graph.get(node, set()) for node in component
        )
        if not cyclic:
            continue
        terminal = not any(
            target not in component_set
            for source in component
            for target in graph.get(source, set())
        )
        if not terminal:
            continue
        jobs = tuple(
            sorted(
                node.removeprefix("job:")
                for node in component
                if node.startswith("job:")
            )
        )
        resources = tuple(
            sorted(
                node.removeprefix("resource:")
                for node in component
                if node.startswith("resource:")
            )
        )
        capacity_closed = _component_is_capacity_closed(
            model=model,
            state=state,
            jobs=frozenset(jobs),
            resources=frozenset(resources),
        )
        record: dict[str, object] = {
            "nodes": list(component),
            "jobs": list(jobs),
            "resources": list(resources),
            "capacity_closed": capacity_closed,
        }
        terminal_components.append(record)
        if capacity_closed:
            capacity_closed_knots.append(record)

    return {
        "available": True,
        "screen_only": True,
        "state_id": state.id,
        "assumptions": [
            "stable_zero_time_closed_state",
            "capacity_shortage_edges_only",
            "hard_holdings_only",
            "all_request_alternatives_checked",
            "no_unmodeled_release_or_guard",
        ],
        "graph": {
            "nodes": sorted(graph),
            "edges": sorted(edges, key=_edge_sort_key),
        },
        "blocked_jobs": sorted(blocked_jobs),
        "terminal_cyclic_sccs": terminal_components,
        "capacity_closed_knots": capacity_closed_knots,
        "has_terminal_cyclic_scc": bool(terminal_components),
        "has_capacity_closed_knot": bool(capacity_closed_knots),
        "interpretation": (
            "baseline_only; general IMS deadlock requires the full "
            "closed-blocking-kernel and transition-release checks"
        ),
    }


def _component_is_capacity_closed(
    *,
    model: IMSModel,
    state: IMSState,
    jobs: frozenset[str],
    resources: frozenset[str],
) -> bool:
    if not jobs or not resources:
        return False
    if not jobs.issubset(state.blocked_jobs(model)):
        return False

    for job_id in jobs:
        alternatives = state.requests.get(job_id, ())
        if not alternatives:
            return False
        for alternative in alternatives:
            if not any(
                demand.resource_id in resources
                and state.available_units(model, demand.resource_id) < demand.units
                for demand in alternative.demands
            ):
                return False

    for resource_id in resources:
        holders = state.holders(resource_id)
        if not holders or not holders.issubset(jobs):
            return False
    return True


def _unavailable_knot_payload(reason: str) -> dict[str, object]:
    return {
        "available": False,
        "screen_only": True,
        "reason": reason,
        "graph": {"nodes": [], "edges": []},
        "blocked_jobs": [],
        "terminal_cyclic_sccs": [],
        "capacity_closed_knots": [],
        "has_terminal_cyclic_scc": False,
        "has_capacity_closed_knot": False,
        "interpretation": (
            "baseline_only; requires a valid stable zero-time-closed state"
        ),
    }


def _job_node(job_id: str) -> str:
    return f"job:{job_id}"


def _resource_node(resource_id: str) -> str:
    return f"resource:{resource_id}"


def _edge_sort_key(edge: dict[str, object]) -> tuple[str, str, str, int]:
    alternative_index = edge.get("alternative_index")
    normalized_index = (
        alternative_index
        if isinstance(alternative_index, int)
        and not isinstance(alternative_index, bool)
        else -1
    )
    return (
        str(edge["source"]),
        str(edge["target"]),
        str(edge["kind"]),
        normalized_index,
    )


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
