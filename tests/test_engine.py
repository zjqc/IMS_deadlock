import pytest

from ims_deadlock.cases import load_case_spec
from ims_deadlock.engine import (
    EventKind,
    FiniteLTS,
    ScheduledEvent,
    TransitionSpec,
    _enabled,
    configuration_signature,
    exact_max_nonblocking_supervisor,
    semantic_signature,
    simulate,
    zero_time_closure,
)
from ims_deadlock.model import (
    Holding,
    IMSModel,
    IMSState,
    RequestAlternative,
    Resource,
    ResourceDemand,
)


def test_zero_time_closure_keeps_urgent_successors_in_canonical_order() -> None:
    model = IMSModel(
        id="closure-order",
        resources={
            "machine": Resource("machine", 1, "machine"),
            "buffer": Resource("buffer", 1, "buffer"),
            "agv": Resource("agv", 1, "agv"),
        },
        jobs=("j1", "j2"),
    )
    state = IMSState(
        id="closure-seed",
        mode_by_job={"j1": "blocked_complete", "j2": "blocked_unload"},
        stage_by_job={"j1": "s0", "j2": "s0"},
        holds=(Holding("j1", "machine", 1),),
        requests={},
        completed_jobs=frozenset(),
        stable=False,
        complete=False,
        event_calendar_empty=False,
    )
    transitions = (
        TransitionSpec(
            name="normalize-j1",
            kind="normalize",
            job_id="j1",
            source_mode="blocked_complete",
            target_mode="waiting_input",
            controllable=False,
            zero_time=True,
            urgent=True,
            release=(ResourceDemand("machine", 1),),
        ),
        TransitionSpec(
            name="normalize-j2",
            kind="normalize",
            job_id="j2",
            source_mode="blocked_unload",
            target_mode="waiting_input",
            controllable=False,
            zero_time=True,
            urgent=True,
        ),
    )

    closure = zero_time_closure(model, state, transitions)

    assert [event.name for event in closure.canonical_trace] == [
        "normalize-j1",
        "normalize-j2",
    ]
    assert {item.mode_by_job["j1"] for item in closure.stable_states} == {
        "waiting_input"
    }
    assert [
        [event.name for event in trace] for _state, trace in closure.stable_successors
    ] == [["normalize-j1", "normalize-j2"]]
    assert closure.stable_states[0].zero_time_trace == (
        "normalize-j1",
        "normalize-j2",
    )


def test_zero_time_closure_reports_trace_per_stable_successor() -> None:
    model = IMSModel(
        id="closure-branch-traces",
        resources={
            "a": Resource("a", 1, "machine"),
            "b": Resource("b", 1, "machine"),
        },
        jobs=("j",),
    )
    state = IMSState(
        id="branch-seed",
        mode_by_job={"j": "seed"},
        stage_by_job={"j": "seed"},
        holds=(),
        requests={},
        completed_jobs=frozenset(),
        stable=False,
        complete=False,
        event_calendar_empty=False,
    )
    transitions = (
        TransitionSpec(
            name="branch-a",
            kind="normalize",
            job_id="j",
            source_mode="seed",
            target_mode="a",
            controllable=False,
            zero_time=True,
            urgent=True,
            acquire=(ResourceDemand("a", 1),),
        ),
        TransitionSpec(
            name="branch-b",
            kind="normalize",
            job_id="j",
            source_mode="seed",
            target_mode="b",
            controllable=False,
            zero_time=True,
            urgent=True,
            acquire=(ResourceDemand("b", 1),),
        ),
    )

    closure = zero_time_closure(model, state, transitions)

    trace_by_mode = {
        stable.mode_by_job["j"]: tuple(event.name for event in trace)
        for stable, trace in closure.stable_successors
    }
    assert trace_by_mode == {"a": ("branch-a",), "b": ("branch-b",)}


def test_simulate_refuses_to_collapse_nonconfluent_urgent_closure() -> None:
    model = IMSModel(
        id="simulate-branch-traces",
        resources={
            "a": Resource("a", 1, "machine"),
            "b": Resource("b", 1, "machine"),
        },
        jobs=("j",),
    )
    state = IMSState(
        id="simulate-branch-seed",
        mode_by_job={"j": "seed"},
        stage_by_job={"j": "seed"},
        stable=False,
        complete=False,
        event_calendar_empty=False,
    )
    transitions = (
        TransitionSpec(
            name="to-safe",
            kind="normalize",
            job_id="j",
            source_mode="seed",
            target_mode="safe",
            controllable=False,
            zero_time=True,
            urgent=True,
            acquire=(ResourceDemand("a", 1),),
        ),
        TransitionSpec(
            name="to-unsafe",
            kind="normalize",
            job_id="j",
            source_mode="seed",
            target_mode="unsafe",
            controllable=False,
            zero_time=True,
            urgent=True,
            acquire=(ResourceDemand("b", 1),),
        ),
    )

    result = simulate(model, state, transitions)

    assert result.terminal_classification == "nonconfluent_zero_time_closure"
    assert result.canonical_trace == ()
    branch_by_mode = {
        branch.state.mode_by_job["j"]: branch.zero_time_trace
        for branch in result.closure_branches
    }
    assert branch_by_mode == {
        "safe": ("to-safe",),
        "unsafe": ("to-unsafe",),
    }


def test_simulate_fires_calendar_event_before_terminal_classification() -> None:
    model = IMSModel(
        id="calendar-fire",
        resources={"machine": Resource("machine", 1, "machine")},
        jobs=("j1",),
    )
    state = IMSState(
        id="calendar-fire-seed",
        mode_by_job={"j1": "waiting_input"},
        stage_by_job={"j1": "s0"},
        holds=(),
        requests={},
        completed_jobs=frozenset(),
        stable=True,
        complete=False,
        event_calendar_empty=False,
    )
    transitions = (
        TransitionSpec(
            name="start-j1",
            kind=EventKind.START,
            job_id="j1",
            source_mode="waiting_input",
            target_mode="processing",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("machine", 1),),
        ),
    )
    calendar = (
        ScheduledEvent(time=1.0, name="start-j1", job_id="j1", kind=EventKind.START),
    )

    result = simulate(model, state, transitions=transitions, calendar=calendar)

    assert result.final_state.mode_by_job["j1"] == "processing"
    assert result.terminal_classification == "model_incomplete"
    assert result.final_state.zero_time_trace == ()


def test_controllable_zero_time_decision_is_not_auto_fired_by_closure() -> None:
    model = IMSModel(
        id="controllable-zero-time",
        resources={"machine": Resource("machine", 1, "machine")},
        jobs=("j1",),
    )
    state = IMSState(
        id="controllable-zero-time-seed",
        mode_by_job={"j1": "waiting_input"},
        stage_by_job={"j1": "s0"},
        holds=(),
        requests={},
        completed_jobs=frozenset(),
        stable=False,
        complete=False,
        event_calendar_empty=False,
    )
    transitions = (
        TransitionSpec(
            name="start-j1",
            kind=EventKind.START,
            job_id="j1",
            source_mode="waiting_input",
            target_mode="processing",
            controllable=True,
            zero_time=True,
        ),
    )

    closure = zero_time_closure(model, state, transitions)

    assert closure.canonical_trace == ()
    assert closure.stable_states == (state,)


def test_urgent_zero_time_transition_requires_uncontrollable() -> None:
    with pytest.raises(
        ValueError,
        match="urgent zero-time transition must be uncontrollable",
    ):
        TransitionSpec(
            name="bad-urgent",
            kind=EventKind.START,
            job_id="j1",
            source_mode="waiting_input",
            target_mode="processing",
            controllable=True,
            zero_time=True,
            urgent=True,
        )


def test_empty_request_alternative_is_allowed() -> None:
    alternative = RequestAlternative(())

    assert alternative.demands == ()


def test_simulate_classifies_incomplete_state_as_model_incomplete() -> None:
    model = IMSModel(
        id="calendar-empty",
        resources={"machine": Resource("machine", 1, "machine")},
        jobs=("j1",),
    )
    state = IMSState(
        id="calendar-empty-seed",
        holds=(),
        requests={
            "j1": (RequestAlternative((ResourceDemand("machine", 1),)),),
        },
        completed_jobs=frozenset(),
        stable=True,
        complete=False,
        event_calendar_empty=True,
    )

    result = simulate(model, state, transitions=())

    assert result.terminal_classification == "model_incomplete"
    assert result.unfinished_jobs == ("j1",)


def test_discovery_cases_are_not_operational_deadlock() -> None:
    for case_id in ("C1", "C2"):
        spec = load_case_spec(case_id)

        result = simulate(
            spec.model,
            spec.initial_state,
            spec.transitions,
            spec.calendar,
        )

        assert result.terminal_classification in {
            "model_incomplete",
            "calendar_mismatch",
        }


def test_transition_next_requests_empty_clears_existing_requests() -> None:
    model = IMSModel(
        id="request-clear",
        resources={"machine": Resource("machine", 1, "machine")},
        jobs=("j1",),
    )
    state = IMSState(
        id="request-clear-seed",
        mode_by_job={"j1": "waiting_input"},
        stage_by_job={"j1": "s0"},
        holds=(),
        requests={
            "j1": (RequestAlternative((ResourceDemand("machine", 1),)),),
        },
        completed_jobs=frozenset(),
        stable=True,
        complete=False,
        event_calendar_empty=False,
    )
    transitions = (
        TransitionSpec(
            name="clear-request",
            kind=EventKind.UNLOAD,
            job_id="j1",
            source_mode="waiting_input",
            target_mode="ready",
            controllable=False,
            zero_time=False,
            clears_requests=True,
        ),
    )
    calendar = (
        ScheduledEvent(
            time=1.0,
            name="clear-request",
            job_id="j1",
            kind=EventKind.UNLOAD,
        ),
    )

    result = simulate(model, state, transitions=transitions, calendar=calendar)

    assert result.final_state.requests == {}


def test_transition_next_requests_absent_preserves_existing_requests() -> None:
    model = IMSModel(
        id="request-preserve",
        resources={"machine": Resource("machine", 1, "machine")},
        jobs=("j1",),
    )
    state = IMSState(
        id="request-preserve-seed",
        mode_by_job={"j1": "waiting_input"},
        stage_by_job={"j1": "s0"},
        holds=(),
        requests={
            "j1": (RequestAlternative((ResourceDemand("machine", 1),)),),
        },
        completed_jobs=frozenset(),
        stable=True,
        complete=False,
        event_calendar_empty=False,
    )
    transitions = (
        TransitionSpec(
            name="preserve-request",
            kind=EventKind.UNLOAD,
            job_id="j1",
            source_mode="waiting_input",
            target_mode="ready",
            controllable=False,
            zero_time=False,
        ),
    )
    calendar = (
        ScheduledEvent(
            time=1.0,
            name="preserve-request",
            job_id="j1",
            kind=EventKind.UNLOAD,
        ),
    )

    result = simulate(model, state, transitions=transitions, calendar=calendar)

    assert "j1" in result.final_state.requests


def test_release_transition_requires_holder_on_same_job() -> None:
    model = IMSModel(
        id="release-owner",
        resources={"machine": Resource("machine", 1, "machine")},
        jobs=("j1", "j2"),
    )
    state = IMSState(
        id="release-owner-seed",
        mode_by_job={"j1": "waiting_input", "j2": "waiting_input"},
        stage_by_job={"j1": "s0", "j2": "s0"},
        holds=(Holding("j2", "machine", 1),),
        requests={},
        completed_jobs=frozenset(),
        stable=True,
        complete=False,
        event_calendar_empty=False,
    )
    transition = TransitionSpec(
        name="release-j1",
        kind=EventKind.RELEASE,
        job_id="j1",
        source_mode="waiting_input",
        target_mode="ready",
        controllable=False,
        zero_time=False,
        release=(ResourceDemand("machine", 1),),
    )

    assert not _enabled(model, state, transition)


def test_exact_max_nonblocking_supervisor_respects_uncontrollable_closure() -> None:
    lts = FiniteLTS(
        states=("s0", "s1", "s2", "dead"),
        initial_state="s0",
        marked_states=("s2",),
        transitions=(
            ("s0", "safe", "s1", True),
            ("s1", "force_dead", "dead", True),
            ("s1", "finish", "s2", False),
        ),
    )

    policy = exact_max_nonblocking_supervisor(lts)

    assert policy.safe_states == ("s0", "s1", "s2")
    assert policy.disabled_transitions == ("force_dead",)
    assert policy.coaccessible_states == ("s0", "s1", "s2")
    assert policy.disabled_state_events == (("s1", "force_dead"),)
    assert policy.initial_state_feasible is True
    assert policy.forbidden_states == ()
    assert policy.dead_states == ("dead",)


def test_configuration_signature_excludes_terminal_flags() -> None:
    left = IMSState(
        id="sig-left",
        mode_by_job={"j1": "waiting_input"},
        stage_by_job={"j1": "s0"},
        holds=(),
        requests={},
        completed_jobs=frozenset(),
        stable=True,
        complete=False,
        event_calendar_empty=False,
    )
    right = IMSState(
        id="sig-right",
        mode_by_job={"j1": "waiting_input"},
        stage_by_job={"j1": "s0"},
        holds=(),
        requests={},
        completed_jobs=frozenset(),
        stable=False,
        complete=True,
        event_calendar_empty=True,
    )

    assert configuration_signature(left) == configuration_signature(right)
    assert semantic_signature(left) != semantic_signature(right)
