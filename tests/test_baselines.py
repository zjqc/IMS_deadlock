from typing import Any, cast

from ims_deadlock.baselines import state_dependent_knot_screen
from ims_deadlock.cases import load_case_spec
from ims_deadlock.model import (
    Holding,
    IMSModel,
    IMSState,
    RequestAlternative,
    Resource,
    ResourceDemand,
)


def test_c0_has_capacity_closed_state_dependent_knot() -> None:
    spec = load_case_spec("C0")

    screen = state_dependent_knot_screen(spec.model, spec.initial_state)

    assert screen["available"] is True
    assert screen["has_capacity_closed_knot"] is True
    knots = cast(list[dict[str, Any]], screen["capacity_closed_knots"])
    assert len(knots) == 1
    assert knots[0]["jobs"] == ["j1", "j2"]
    assert knots[0]["resources"] == ["r1", "r2"]


def test_c1_raw_cycle_is_rejected_when_residual_capacity_allows_progress() -> None:
    spec = load_case_spec("C1")

    screen = state_dependent_knot_screen(spec.model, spec.initial_state)

    assert screen["has_capacity_closed_knot"] is False
    assert screen["terminal_cyclic_sccs"] == []
    assert screen["blocked_jobs"] == ["j2"]


def test_c4_knot_includes_transport_resource_but_not_free_buffer() -> None:
    spec = load_case_spec("C4")

    screen = state_dependent_knot_screen(spec.model, spec.initial_state)

    knots = cast(list[dict[str, Any]], screen["capacity_closed_knots"])
    assert knots[0]["resources"] == ["agv", "m1"]
    graph = cast(dict[str, Any], screen["graph"])
    request_resources = {
        edge["resource_id"]
        for edge in graph["edges"]
        if edge["kind"] == "blocking_request"
    }
    assert request_resources == {"agv", "m1"}
    assert "buf" not in request_resources


def test_multi_capacity_cycle_without_blocked_jobs_has_no_knot() -> None:
    spec = load_case_spec("C3")

    screen = state_dependent_knot_screen(spec.model, spec.initial_state)

    assert screen["blocked_jobs"] == []
    assert screen["has_terminal_cyclic_scc"] is False
    assert screen["has_capacity_closed_knot"] is False


def test_open_or_alternative_prevents_false_knot() -> None:
    model = IMSModel(
        id="or-alternative-knot-boundary",
        resources={
            "held": Resource("held", 1),
            "free": Resource("free", 1),
        },
        jobs=("j1", "j2"),
    )
    state = IMSState(
        id="or-alternative-open",
        holds=(Holding("j1", "held", 1),),
        requests={
            "j1": (
                RequestAlternative((ResourceDemand("held", 1),)),
                RequestAlternative((ResourceDemand("free", 1),)),
            )
        },
        stable=True,
        complete=False,
        event_calendar_empty=True,
    )

    screen = state_dependent_knot_screen(model, state)

    assert screen["blocked_jobs"] == []
    assert screen["has_capacity_closed_knot"] is False


def test_unstable_state_is_not_presented_as_post_closure_knot_analysis() -> None:
    model = IMSModel(id="unstable", resources={"r": Resource("r", 1)}, jobs=("j",))
    state = IMSState(id="unstable", stable=False, event_calendar_empty=False)

    screen = state_dependent_knot_screen(model, state)

    assert screen["available"] is False
    assert screen["reason"] == "state_not_zero_time_closed"
