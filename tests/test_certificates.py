import pytest

from ims_deadlock.cases import (
    c0_two_resource_deadlock,
    c1_cycle_insufficient_wip,
    load_case_spec,
)
from ims_deadlock.certificates import (
    find_deadlock_certificate,
    find_local_blocking_certificate,
)
from ims_deadlock.engine import EventKind, TransitionSpec
from ims_deadlock.model import (
    CapacityWitness,
    Holding,
    IMSModel,
    IMSState,
    RequestAlternative,
    Resource,
    ResourceDemand,
    validate_model_state,
)


def test_c0_two_resource_model_has_minimal_closed_blocking_kernel() -> None:
    model, state = c0_two_resource_deadlock()

    certificate = find_deadlock_certificate(model, state)

    assert certificate is not None
    assert certificate.kernel_jobs == frozenset({"j1", "j2"})
    assert certificate.kernel_resources == frozenset({"r1", "r2"})
    assert certificate.is_minimal is True
    assert certificate.assumptions == (
        "stable_zero_time_closure",
        "capacity_mediated_blocking",
        "closed_world_transition_registry",
        "all_enabled_transitions_supplied",
    )


def test_c1_static_cycle_without_saturation_is_not_deadlock_certificate() -> None:
    model, state = c1_cycle_insufficient_wip()

    certificate = find_deadlock_certificate(model, state)

    assert certificate is None


def test_global_deadlock_requires_empty_event_calendar() -> None:
    model, state = c0_two_resource_deadlock()
    active_calendar = IMSState(
        id="c0-with-event",
        holds=state.holds,
        requests=state.requests,
        stable=True,
        complete=False,
        event_calendar_empty=False,
    )

    certificate = find_deadlock_certificate(model, active_calendar)

    assert certificate is None


def test_local_kernel_is_not_global_when_unfinished_job_can_still_move() -> None:
    model = IMSModel(
        id="local-not-global",
        resources={
            "r1": Resource("r1", 1),
            "r2": Resource("r2", 1),
            "r3": Resource("r3", 1),
        },
        jobs=("j1", "j2", "j3"),
    )
    state = IMSState(
        id="local-blocking-only",
        holds=(
            Holding("j1", "r1", 1),
            Holding("j2", "r2", 1),
        ),
        requests={
            "j1": (RequestAlternative((ResourceDemand("r2", 1),)),),
            "j2": (RequestAlternative((ResourceDemand("r1", 1),)),),
        },
        stable=True,
        complete=False,
        event_calendar_empty=True,
    )

    global_certificate = find_deadlock_certificate(model, state)
    local_certificate = find_local_blocking_certificate(model, state)

    assert global_certificate is None
    assert local_certificate is not None
    assert local_certificate.scope == "local"
    assert local_certificate.kernel_jobs == frozenset({"j1", "j2"})


def test_local_kernel_survives_enabled_transition_outside_kernel() -> None:
    model = IMSModel(
        id="local-kernel-with-outside-progress",
        resources={
            "r1": Resource("r1", 1),
            "r2": Resource("r2", 1),
            "r3": Resource("r3", 1),
        },
        jobs=("j1", "j2", "j3"),
    )
    state = IMSState(
        id="local-cycle-plus-enabled-job",
        holds=(
            Holding("j1", "r1", 1),
            Holding("j2", "r2", 1),
        ),
        requests={
            "j1": (RequestAlternative((ResourceDemand("r2", 1),)),),
            "j2": (RequestAlternative((ResourceDemand("r1", 1),)),),
        },
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"j1": "waiting_r2", "j2": "waiting_r1", "j3": "ready"},
        stage_by_job={"j1": "waiting_r2", "j2": "waiting_r1", "j3": "ready"},
    )
    outside_progress = (
        TransitionSpec(
            name="complete-j3",
            kind=EventKind.SERVICE_COMPLETE,
            job_id="j3",
            source_mode="ready",
            target_mode="completed",
            controllable=False,
            zero_time=False,
            mark_complete=True,
        ),
    )

    global_certificate = find_deadlock_certificate(model, state, outside_progress)
    local_certificate = find_local_blocking_certificate(model, state, outside_progress)

    assert global_certificate is None
    assert local_certificate is not None
    assert local_certificate.scope == "local"
    assert local_certificate.kernel_jobs == frozenset({"j1", "j2"})
    assert local_certificate.kernel_resources == frozenset({"r1", "r2"})


def test_local_kernel_rejects_enabled_progress_inside_kernel() -> None:
    model = IMSModel(
        id="local-kernel-with-inside-progress",
        resources={
            "r1": Resource("r1", 1),
            "r2": Resource("r2", 1),
        },
        jobs=("j1", "j2"),
    )
    state = IMSState(
        id="local-cycle-plus-enabled-release",
        holds=(
            Holding("j1", "r1", 1),
            Holding("j2", "r2", 1),
        ),
        requests={
            "j1": (RequestAlternative((ResourceDemand("r2", 1),)),),
            "j2": (RequestAlternative((ResourceDemand("r1", 1),)),),
        },
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"j1": "waiting_r2", "j2": "waiting_r1"},
        stage_by_job={"j1": "waiting_r2", "j2": "waiting_r1"},
    )
    inside_progress = (
        TransitionSpec(
            name="j1-release-r1",
            kind=EventKind.RELEASE,
            job_id="j1",
            source_mode="waiting_r2",
            target_mode="released_r1",
            controllable=False,
            zero_time=False,
            release=(ResourceDemand("r1", 1),),
        ),
    )

    local_certificate = find_local_blocking_certificate(model, state, inside_progress)

    assert local_certificate is None


def test_request_alternatives_use_or_semantics() -> None:
    model = IMSModel(
        id="or-requests",
        resources={
            "r1": Resource("r1", 1),
            "b1": Resource("b1", 1, "buffer"),
            "b2": Resource("b2", 1, "buffer"),
        },
        jobs=("j1", "j2"),
    )
    state = IMSState(
        id="one-alternative-free",
        holds=(Holding("j2", "b1", 1),),
        requests={
            "j1": (
                RequestAlternative((ResourceDemand("b1", 1),)),
                RequestAlternative((ResourceDemand("b2", 1),)),
            )
        },
        stable=True,
        complete=False,
        event_calendar_empty=True,
    )

    assert state.blocked_jobs(model) == frozenset()
    assert find_deadlock_certificate(model, state) is None


def test_conjunctive_request_blocks_when_any_required_resource_is_missing() -> None:
    model = IMSModel(
        id="and-requests",
        resources={
            "agv": Resource("agv", 1, "agv"),
            "buf": Resource("buf", 1, "buffer"),
        },
        jobs=("j1", "j2"),
    )
    state = IMSState(
        id="agv-plus-buffer",
        holds=(Holding("j2", "agv", 1),),
        requests={
            "j1": (
                RequestAlternative(
                    (ResourceDemand("agv", 1), ResourceDemand("buf", 1))
                ),
            )
        },
        stable=True,
        complete=False,
        event_calendar_empty=True,
    )

    assert state.blocked_jobs(model) == frozenset({"j1"})


def test_multi_unit_holdings_are_counted_by_units() -> None:
    model = IMSModel(
        id="multi-unit-hold",
        resources={"buf": Resource("buf", 3, "buffer")},
        jobs=("j1",),
    )
    state = IMSState(
        id="holds-two-units",
        holds=(Holding("j1", "buf", 2),),
        stable=True,
        complete=False,
        event_calendar_empty=True,
    )

    assert state.held_units("buf") == 2
    assert validate_model_state(model, state).valid is True


def test_validator_reports_overcapacity_and_unknown_references() -> None:
    model = IMSModel(
        id="invalid-state",
        resources={"buf": Resource("buf", 1, "buffer")},
        jobs=("j1",),
    )
    state = IMSState(
        id="bad",
        holds=(Holding("j1", "buf", 2), Holding("ghost", "missing", 1)),
        requests={"j1": (RequestAlternative((ResourceDemand("missing", 1),)),)},
        stable=True,
        complete=True,
        event_calendar_empty=False,
    )

    result = validate_model_state(model, state)

    assert result.valid is False
    codes = {issue.code for issue in result.issues}
    assert "overcapacity_resource" in codes
    assert "unknown_hold_job" in codes
    assert "unknown_hold_resource" in codes
    assert "unknown_request_resource" in codes
    assert "complete_state_has_open_work" in codes


def test_validator_reports_unstable_state_as_not_closure_normalized() -> None:
    model = IMSModel(
        id="unstable-state",
        resources={"r1": Resource("r1", 1)},
        jobs=("j1",),
    )
    calendar_empty_state = IMSState(
        id="unstable-empty-calendar",
        stable=False,
        complete=False,
        event_calendar_empty=True,
    )
    calendar_active_state = IMSState(
        id="unstable-active-calendar",
        stable=False,
        complete=False,
        event_calendar_empty=False,
    )

    empty_codes = {
        issue.code for issue in validate_model_state(model, calendar_empty_state).issues
    }
    active_codes = {
        issue.code
        for issue in validate_model_state(model, calendar_active_state).issues
    }

    assert "state_not_closure_normalized" in empty_codes
    assert "state_not_closure_normalized" in active_codes
    assert "unstable_state_without_calendar" not in empty_codes
    assert "unstable_state_without_calendar" not in active_codes


def test_redundant_requested_resource_is_not_in_minimal_certificate() -> None:
    model = IMSModel(
        id="minimal-witness",
        resources={
            "r1": Resource("r1", 1),
            "r2": Resource("r2", 1),
            "free": Resource("free", 1),
        },
        jobs=("j1", "j2"),
    )
    state = IMSState(
        id="redundant-request",
        holds=(Holding("j1", "r1", 1), Holding("j2", "r2", 1)),
        requests={
            "j1": (
                RequestAlternative(
                    (ResourceDemand("r2", 1), ResourceDemand("free", 1))
                ),
            ),
            "j2": (RequestAlternative((ResourceDemand("r1", 1),)),),
        },
        stable=True,
        complete=False,
        event_calendar_empty=True,
    )

    certificate = find_deadlock_certificate(model, state)

    assert certificate is not None
    assert certificate.kernel_resources == frozenset({"r1", "r2"})
    assert certificate.is_minimal is True


def test_certificate_evidence_edges_include_auditable_units_in_json() -> None:
    model = IMSModel(
        id="unit-aware-certificate",
        resources={"buf": Resource("buf", 2, "buffer")},
        jobs=("j1",),
    )
    state = IMSState(
        id="multi-unit-blocked",
        holds=(Holding("j1", "buf", 2),),
        requests={"j1": (RequestAlternative((ResourceDemand("buf", 1),)),)},
        stable=True,
        complete=False,
        event_calendar_empty=True,
    )

    certificate = find_deadlock_certificate(model, state)

    assert certificate is not None
    edges = certificate.to_json_dict()["evidence_edges"]
    assert edges == [
        {"kind": "hold", "source": "buf", "target": "j1", "units": 2},
        {"kind": "request", "source": "j1", "target": "buf", "units": 1},
    ]


def test_certificate_json_includes_capacity_witnesses_and_bridge_boundary() -> None:
    model = IMSModel(
        id="capacity-witness",
        resources={"buf": Resource("buf", 2, "buffer")},
        jobs=("j1",),
    )
    state = IMSState(
        id="capacity-shortage",
        holds=(Holding("j1", "buf", 2),),
        requests={"j1": (RequestAlternative((ResourceDemand("buf", 1),)),)},
        stable=True,
        complete=False,
        event_calendar_empty=True,
        zero_time_trace=("finish_m1", "blocked_unload"),
    )

    certificate = find_deadlock_certificate(
        model, state, reachable_prefix=("start_j1", "finish_j1")
    )

    assert certificate is not None
    payload = certificate.to_json_dict()
    assert payload["zero_time_trace"] == ["finish_m1", "blocked_unload"]
    assert payload["shortest_reachable_prefix"] == ["start_j1", "finish_j1"]
    assert payload["corresponding_siphon"] is None
    assert payload["bridge_status"] == "not_applicable_no_petri_subclass_mapping"
    assert payload["capacity_witnesses"] == [
        {
            "job_id": "j1",
            "alternative_index": 0,
            "resource_id": "buf",
            "requested_units": 1,
            "capacity": 2,
            "held_units": 2,
            "residual_units": 0,
            "kernel_held_units": 2,
            "holders": ["j1"],
            "shortage_units": 1,
        }
    ]


def test_capacity_witness_rejects_internally_inconsistent_arithmetic() -> None:
    with pytest.raises(ValueError, match="residual units"):
        CapacityWitness(
            job_id="j1",
            alternative_index=0,
            resource_id="r1",
            requested_units=1,
            capacity=2,
            held_units=2,
            residual_units=1,
            kernel_held_units=2,
            holders=("j1",),
            shortage_units=1,
        )

    with pytest.raises(ValueError, match="shortage units"):
        CapacityWitness(
            job_id="j1",
            alternative_index=0,
            resource_id="r1",
            requested_units=2,
            capacity=2,
            held_units=2,
            residual_units=0,
            kernel_held_units=2,
            holders=("j1",),
            shortage_units=1,
        )


def test_local_certificate_accepts_reachable_prefix_keyword() -> None:
    model, state = c0_two_resource_deadlock()

    certificate = find_local_blocking_certificate(
        model, state, reachable_prefix=("a", "b")
    )

    assert certificate is not None
    assert certificate.to_json_dict()["shortest_reachable_prefix"] == ["a", "b"]


def test_c4_certificate_mentions_transport_layer_resources() -> None:
    spec = load_case_spec("C4")

    certificate = find_deadlock_certificate(spec.model, spec.initial_state)

    assert certificate is not None
    assert certificate.kernel_resources == frozenset({"agv", "m1"})


def test_c5_certificate_mentions_bidirectional_route_resources() -> None:
    spec = load_case_spec("C5")

    certificate = find_deadlock_certificate(spec.model, spec.initial_state)

    assert certificate is not None
    assert certificate.kernel_resources == frozenset({"G", "M"})


def test_transition_aware_certificate_rejects_enabled_progress() -> None:
    model = IMSModel(
        id="progress-reject",
        resources={"m1": Resource("m1", 1)},
        jobs=("j1",),
    )
    state = IMSState(
        id="progress-reject-state",
        mode_by_job={"j1": "waiting_input"},
        holds=(),
        requests={},
        stable=True,
        complete=False,
        event_calendar_empty=True,
    )
    transitions = (
        TransitionSpec(
            name="release-progress",
            kind=EventKind.RELEASE,
            job_id="j1",
            source_mode="waiting_input",
            target_mode="ready",
            controllable=False,
            zero_time=False,
            acquire=(ResourceDemand("m1", 1),),
        ),
    )

    certificate = find_deadlock_certificate(model, state, transitions=transitions)

    assert certificate is None


def test_transition_aware_certificate_ignores_other_jobs_release_holding() -> None:
    model = IMSModel(
        id="release-owner-certificate",
        resources={"m1": Resource("m1", 1)},
        jobs=("j1", "j2"),
    )
    state = IMSState(
        id="release-owner-state",
        holds=(Holding("j2", "m1", 1),),
        requests={},
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"j1": "waiting_input", "j2": "waiting_input"},
    )
    transitions = (
        TransitionSpec(
            name="release-progress",
            kind=EventKind.RELEASE,
            job_id="j1",
            source_mode="waiting_input",
            target_mode="ready",
            controllable=False,
            zero_time=False,
            release=(ResourceDemand("m1", 1),),
        ),
    )

    certificate = find_deadlock_certificate(model, state, transitions=transitions)

    assert certificate is None


def test_c4_machine_only_projection_is_not_a_deadlock_certificate() -> None:
    model = IMSModel(
        id="C4-projection",
        resources={
            "m1": Resource("m1", 1),
            "buf": Resource("buf", 1, "buffer"),
        },
        jobs=("pA", "pB"),
    )
    state = IMSState(
        id="c4-projection",
        holds=(Holding("pA", "m1", 1),),
        requests={"pA": (RequestAlternative((ResourceDemand("buf", 1),)),)},
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"pA": "blocked_complete", "pB": "waiting_input"},
    )

    certificate = find_deadlock_certificate(model, state)

    assert certificate is None
