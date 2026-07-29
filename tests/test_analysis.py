from typing import Any, cast

from ims_deadlock.analysis import (
    analyze_case,
    enumerate_stable_lts,
    project_case_without_transport,
)
from ims_deadlock.cases import CaseSpec, load_case_spec
from ims_deadlock.engine import TransitionSpec
from ims_deadlock.model import (
    Holding,
    IMSModel,
    IMSState,
    RequestAlternative,
    Resource,
    ResourceDemand,
)


def test_enumeration_is_deterministic_and_records_shortest_witnesses() -> None:
    spec = load_case_spec("C2")

    left = enumerate_stable_lts(
        spec.model, spec.initial_state, spec.transitions, max_states=20
    )
    right = enumerate_stable_lts(
        spec.model, spec.initial_state, spec.transitions, max_states=20
    )

    assert [state.state_id for state in left.states] == [
        state.state_id for state in right.states
    ]
    assert [state.signature for state in left.states] == [
        state.signature for state in right.states
    ]
    assert [arc.to_json_dict() for arc in left.transitions] == [
        arc.to_json_dict() for arc in right.transitions
    ]
    assert left.states[0].witness == ()
    completion = next(state for state in left.states if state.state.complete)
    assert completion.witness
    assert completion.state_id in left.marked_state_ids


def test_c1_cycle_screen_true_without_kernel_and_completion_reachable() -> None:
    analysis = analyze_case(load_case_spec("C1"), max_states=20)

    assert analysis["simple_cycle_screen"]["has_cycle"] is True
    assert (
        analysis["state_dependent_knot_screen"]["has_reachable_capacity_closed_knot"]
        is False
    )
    assert analysis["certificate"]["available"] is False
    assert analysis["petri_bridge"] == {
        "status": "not_applicable_no_reachable_closed_blocking_kernel",
        "available": False,
        "corresponding_siphon": None,
    }
    assert (
        analysis["unavailable"]["siphon"]
        == "not_applicable_no_reachable_closed_blocking_kernel"
    )
    assert analysis["supervisor"]["available"] is True
    assert analysis["supervisor"]["initial_state_feasible"] is True
    assert analysis["banker_snapshot"]["safe"] is True


def test_c2_has_no_cycle_and_reaches_completion() -> None:
    analysis = analyze_case(load_case_spec("C2"), max_states=20)

    assert analysis["simple_cycle_screen"]["has_cycle"] is False
    assert analysis["certificate"]["available"] is False
    assert analysis["lts"]["marked_state_ids"]
    assert analysis["supervisor"]["available"] is True


def test_c4_full_agv_certificate_but_machine_projection_has_progress() -> None:
    spec = load_case_spec("C4")
    full = analyze_case(spec, max_states=20)
    projection = analyze_case(project_case_without_transport(spec), max_states=20)

    assert full["certificate"]["available"] is True
    full_certificate = cast("dict[str, Any]", full["certificate"]["certificate"])
    assert "agv" in full_certificate["kernel_resources"]
    assert (
        full["state_dependent_knot_screen"]["has_reachable_capacity_closed_knot"]
        is True
    )
    assert projection["certificate"]["available"] is False
    assert projection["lts"]["transition_count"] >= 1


def test_c5_bidirectional_certificate_and_dag_repair_completion() -> None:
    bidirectional = analyze_case(load_case_spec("C5"), max_states=20)
    dag_repair = analyze_case(load_case_spec("C5_DAG"), max_states=20)

    assert bidirectional["certificate"]["available"] is True
    assert dag_repair["certificate"]["available"] is False
    assert dag_repair["lts"]["marked_state_ids"]
    assert dag_repair["supervisor"]["available"] is True


def test_truncation_disables_exact_supervisor() -> None:
    analysis = analyze_case(load_case_spec("C2"), max_states=1)

    assert analysis["lts"]["truncated"] is True
    assert analysis["supervisor"]["available"] is False
    assert analysis["supervisor"]["reason"] == "lts_truncated"


def test_supervisor_requires_reachable_marked_completion() -> None:
    analysis = analyze_case(load_case_spec("C0"), max_states=20)

    assert analysis["lts"]["marked_state_ids"] == []
    assert analysis["supervisor"]["available"] is False
    assert analysis["supervisor"]["reason"] == "no_marked_completion_reachable"


def test_c0_analysis_exposes_exact_wait_snapshot_petri_bridge() -> None:
    analysis = analyze_case(load_case_spec("C0"), max_states=20)

    assert analysis["petri_bridge"] == {
        "status": "exact_ims_sip1_wait_snapshot_duality",
        "available": True,
        "corresponding_siphon": {
            "type": "state_induced_wait_snapshot",
            "places": ["free:r1", "free:r2"],
            "empty": True,
            "minimal": True,
            "core_jobs": ["j1", "j2"],
            "core_resources": ["r1", "r2"],
        },
    }
    assert analysis["unavailable"]["siphon"] is None
    certificate = cast(dict[str, Any], analysis["certificate"]["certificate"])
    assert certificate["bridge_status"] == "exact_ims_sip1_wait_snapshot_duality"
    assert (
        certificate["corresponding_siphon"]
        == analysis["petri_bridge"]["corresponding_siphon"]
    )


def test_non_sip1_certificate_reports_bridge_refusal_without_siphon() -> None:
    analysis = analyze_case(load_case_spec("C5"), max_states=20)

    assert analysis["certificate"]["available"] is True
    bridge = cast(dict[str, Any], analysis["petri_bridge"])
    assert bridge["available"] is False
    assert bridge["corresponding_siphon"] is None
    assert cast(str, bridge["status"]).startswith(
        "not_applicable_ims_sip1_assumptions_failed:"
    )
    assert analysis["unavailable"]["siphon"] == bridge["status"]
    certificate = cast(dict[str, Any], analysis["certificate"]["certificate"])
    assert certificate["corresponding_siphon"] is None
    assert certificate["bridge_status"] == bridge["status"]


def test_certificate_uses_shortest_reachable_stable_lts_state() -> None:
    model = IMSModel(
        id="reachable-certificate",
        resources={"r1": Resource("r1", 1), "r2": Resource("r2", 1)},
        jobs=("j1", "j2"),
    )
    state = IMSState(
        id="reachable-certificate-seed",
        holds=(Holding("j1", "r1", 1), Holding("j2", "r2", 1)),
        requests={},
        completed_jobs=frozenset(),
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"j1": "ready", "j2": "ready"},
        stage_by_job={"j1": "ready", "j2": "ready"},
    )
    transitions = (
        TransitionSpec(
            name="j1-request-r2",
            kind="request",
            job_id="j1",
            source_mode="ready",
            target_mode="waiting_r2",
            controllable=False,
            zero_time=False,
            next_requests=(RequestAlternative((ResourceDemand("r2", 1),)),),
        ),
        TransitionSpec(
            name="j2-request-r1",
            kind="request",
            job_id="j2",
            source_mode="ready",
            target_mode="waiting_r1",
            controllable=False,
            zero_time=False,
            next_requests=(RequestAlternative((ResourceDemand("r1", 1),)),),
        ),
    )

    analysis = analyze_case(
        load_case_spec("C0").__class__(
            schema_version="ims-deadlock/case/v1",
            case_id="REACHABLE_CERT",
            title="reachable cert",
            status="DISCOVERY",
            model=model,
            initial_state=state,
            transitions=transitions,
        ),
        max_states=10,
    )

    assert analysis["certificate"]["available"] is True
    assert analysis["certificate"]["state_id"] == "s3"
    assert analysis["certificate"]["reachability_witness"] == [
        "j1-request-r2",
        "j2-request-r1",
    ]
    certificate = cast(dict[str, Any], analysis["certificate"]["certificate"])
    assert certificate["shortest_reachable_prefix"] == [
        "j1-request-r2",
        "j2-request-r1",
    ]


def test_certificate_witness_minimizes_full_event_count_after_enumeration() -> None:
    model = IMSModel(
        id="weighted-witness-certificate",
        resources={"r": Resource("r", 1)},
        jobs=("j",),
    )
    state = IMSState(
        id="weighted-witness-seed",
        holds=(Holding("j", "r", 1),),
        requests={},
        completed_jobs=frozenset(),
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"j": "seed"},
        stage_by_job={"j": "seed"},
    )
    transitions = (
        TransitionSpec(
            name="a-slow",
            kind="release",
            job_id="j",
            source_mode="seed",
            target_mode="slow0",
            controllable=False,
            zero_time=False,
        ),
        TransitionSpec(
            name="b-fast-1",
            kind="start",
            job_id="j",
            source_mode="seed",
            target_mode="mid",
            controllable=False,
            zero_time=False,
        ),
        TransitionSpec(
            name="b-fast-2",
            kind="start",
            job_id="j",
            source_mode="mid",
            target_mode="dead",
            controllable=False,
            zero_time=False,
            next_requests=(RequestAlternative((ResourceDemand("r", 1),)),),
        ),
        TransitionSpec(
            name="z-slow-1",
            kind="normalize",
            job_id="j",
            source_mode="slow0",
            target_mode="slow1",
            controllable=False,
            zero_time=True,
            urgent=True,
        ),
        TransitionSpec(
            name="z-slow-2",
            kind="normalize",
            job_id="j",
            source_mode="slow1",
            target_mode="dead",
            controllable=False,
            zero_time=True,
            urgent=True,
            next_requests=(RequestAlternative((ResourceDemand("r", 1),)),),
        ),
    )

    analysis = analyze_case(
        CaseSpec(
            schema_version="ims-deadlock/case/v1",
            case_id="WEIGHTED_WITNESS_CERT",
            title="weighted witness cert",
            status="DISCOVERY",
            model=model,
            initial_state=state,
            transitions=transitions,
        ),
        max_states=10,
    )

    assert analysis["certificate"]["available"] is True
    assert analysis["certificate"]["reachability_witness"] == [
        "b-fast-1",
        "b-fast-2",
    ]
    done_state = next(
        record
        for record in analysis["lts"]["states"]
        if record["mode_by_job"] == {"j": "dead"}
    )
    assert done_state["witness"] == ["b-fast-1", "b-fast-2"]


def test_multiple_initial_closure_outcomes_use_all_initial_feasibility() -> None:
    model = IMSModel(
        id="multi-initial-unsafe",
        resources={"safe": Resource("safe", 1), "trap": Resource("trap", 1)},
        jobs=("j",),
    )
    state = IMSState(
        id="multi-initial-seed",
        holds=(),
        requests={},
        completed_jobs=frozenset(),
        stable=False,
        complete=False,
        event_calendar_empty=False,
        mode_by_job={"j": "seed"},
        stage_by_job={"j": "seed"},
    )
    transitions = (
        TransitionSpec(
            name="to-safe",
            kind="normalize",
            job_id="j",
            source_mode="seed",
            target_mode="safe_ready",
            controllable=False,
            zero_time=True,
            urgent=True,
            acquire=(ResourceDemand("safe", 1),),
        ),
        TransitionSpec(
            name="to-unsafe",
            kind="normalize",
            job_id="j",
            source_mode="seed",
            target_mode="unsafe_trap",
            controllable=False,
            zero_time=True,
            urgent=True,
            acquire=(ResourceDemand("trap", 1),),
        ),
        TransitionSpec(
            name="finish-safe",
            kind="service_complete",
            job_id="j",
            source_mode="safe_ready",
            target_mode="completed",
            controllable=True,
            zero_time=False,
            release=(ResourceDemand("safe", 1),),
            mark_complete=True,
        ),
    )

    lts = enumerate_stable_lts(model, state, transitions, max_states=10)
    analysis = analyze_case(
        load_case_spec("C0").__class__(
            schema_version="ims-deadlock/case/v1",
            case_id="MULTI_INITIAL",
            title="multi initial",
            status="DISCOVERY",
            model=model,
            initial_state=state,
            transitions=transitions,
        ),
        max_states=10,
    )

    assert set(lts.initial_state_ids) == {"s0", "s1"}
    witness_by_mode = {
        record.state.mode_by_job["j"]: record.witness for record in lts.states[:2]
    }
    assert witness_by_mode == {
        "safe_ready": ("to-safe",),
        "unsafe_trap": ("to-unsafe",),
    }
    assert analysis["supervisor"]["available"] is True
    assert analysis["supervisor"]["initial_state_feasible"] is False
    assert analysis["supervisor"]["initial_state_ids"] == ["s0", "s1"]
    assert analysis["supervisor"]["unsafe_initial_state_ids"] == ["s1"]


def test_truncation_records_frontier_omissions() -> None:
    analysis = analyze_case(load_case_spec("C2"), max_states=1)

    assert analysis["lts"]["truncated"] is True
    omissions = analysis["lts"]["truncated_arcs"]
    assert omissions
    assert omissions[0]["source"] == "s0"
    assert "target_signature" in omissions[0]
    assert omissions[0]["reason"] == "max_states"
