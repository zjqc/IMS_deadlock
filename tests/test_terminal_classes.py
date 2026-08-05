from dataclasses import replace
from typing import Any, cast

import pytest

from ims_deadlock.analysis import (
    LTSStateRecord,
    StableLTS,
    StableLTSArc,
    enumerate_stable_lts,
)
from ims_deadlock.engine import EventKind, TransitionSpec
from ims_deadlock.model import (
    Holding,
    IMSModel,
    IMSState,
    RequestAlternative,
    Resource,
    ResourceDemand,
)
from ims_deadlock.terminal_classes import (
    ABSORPTION_DOMAIN_ALGORITHM_VERSION,
    ABSORPTION_DOMAIN_CERTIFICATE_VERSION,
    CERTIFIED_STATUS,
    DEFAULT_ESTIMAND_SPEC,
    NO_POLICY_FILTER_DECLARATION,
    AbsorptionDomainCertificate,
    TerminalPartitionError,
    TerminalStoppingPartition,
    VersionedEstimandSpec,
    canonical_no_policy_filter_declaration,
    certify_absorption_domain,
    partition_stable_lts,
)


def _local_model() -> IMSModel:
    return IMSModel(
        id="local-onset-model",
        resources={
            "r1": Resource("r1", 1),
            "r2": Resource("r2", 1),
            "r3": Resource("r3", 1),
        },
        jobs=("j1", "j2", "free_job"),
    )


def _state(
    state_id: str,
    *,
    holds: tuple[Holding, ...] = (),
    requests: dict[str, tuple[RequestAlternative, ...]] | None = None,
    mode_by_job: dict[str, str] | None = None,
    completed_jobs: frozenset[str] = frozenset(),
    complete: bool = False,
) -> IMSState:
    return IMSState(
        id=state_id,
        holds=holds,
        requests=requests or {},
        completed_jobs=completed_jobs,
        stable=True,
        complete=complete,
        event_calendar_empty=True,
        mode_by_job=mode_by_job or {},
        stage_by_job=mode_by_job or {},
    )


def _record(
    state_id: str, state: IMSState, witness: tuple[str, ...] = ()
) -> LTSStateRecord:
    return LTSStateRecord(
        state_id=state_id,
        state=state,
        signature=(state_id,),
        witness=witness,
    )


def _lts(
    records: tuple[LTSStateRecord, ...],
    transitions: tuple[StableLTSArc, ...] = (),
    *,
    initial_state_id: str = "s0",
) -> StableLTS:
    return StableLTS(
        states=records,
        initial_state_id=initial_state_id,
        initial_state_ids=(initial_state_id,),
        transitions=transitions,
        truncated_arcs=(),
        marked_state_ids=tuple(
            record.state_id for record in records if record.state.complete
        ),
        truncated=False,
        max_states=64,
        unavailable_reasons=(),
    )


def _event(name: str, *, job_id: str = "j1") -> TransitionSpec:
    return TransitionSpec(
        name=name,
        kind=EventKind.DISPATCH,
        job_id=job_id,
        source_mode="ready",
        target_mode="done",
        controllable=False,
        zero_time=False,
    )


def _finish_event(
    name: str = "finish", *, source_mode: str = "start"
) -> TransitionSpec:
    return TransitionSpec(
        name=name,
        kind=EventKind.SERVICE_COMPLETE,
        job_id="j1",
        source_mode=source_mode,
        target_mode="completed",
        controllable=False,
        zero_time=False,
        mark_complete=True,
    )


def _mode_event(name: str, *, source_mode: str, target_mode: str) -> TransitionSpec:
    return TransitionSpec(
        name=name,
        kind=EventKind.DISPATCH,
        job_id="j1",
        source_mode=source_mode,
        target_mode=target_mode,
        controllable=False,
        zero_time=False,
    )


def _state_id_by_mode(graph: StableLTS, mode: str) -> str:
    matches = [
        record.state_id
        for record in graph.states
        if record.state.mode_by_job.get("j1") == mode
    ]
    assert len(matches) == 1
    return matches[0]


def _branching_closed_fixture() -> tuple[
    StableLTS,
    tuple[TransitionSpec, ...],
    str,
    str,
    str,
]:
    model = IMSModel(id="branching-ce-nb1", resources={}, jobs=("j1",))
    initial = _state("initial", mode_by_job={"j1": "start"})
    transitions = (
        _finish_event("finish", source_mode="start"),
        _mode_event("enter-closed", source_mode="start", target_mode="closed"),
        _mode_event("closed-loop", source_mode="closed", target_mode="closed"),
    )
    graph = enumerate_stable_lts(model, initial, transitions, max_states=8)
    assert graph.truncated is False
    assert graph.unavailable_reasons == ()
    start_state_id = _state_id_by_mode(graph, "start")
    closed_state_id = _state_id_by_mode(graph, "closed")
    assert len(graph.marked_state_ids) == 1
    finish_state_id = graph.marked_state_ids[0]
    return graph, transitions, start_state_id, closed_state_id, finish_state_id


def _simple_finish_fixture() -> tuple[StableLTS, tuple[TransitionSpec, ...], str, str]:
    model = IMSModel(id="simple-finish", resources={}, jobs=("j1",))
    initial = _state("initial", mode_by_job={"j1": "start"})
    finish = _finish_event(source_mode="start")
    graph = enumerate_stable_lts(model, initial, (finish,), max_states=8)
    assert graph.truncated is False
    assert graph.unavailable_reasons == ()
    return (
        graph,
        (finish,),
        _state_id_by_mode(graph, "start"),
        graph.marked_state_ids[0],
    )


def _detour_finish_fixture() -> tuple[StableLTS, tuple[TransitionSpec, ...], str, str]:
    model = IMSModel(id="detour-finish", resources={}, jobs=("j1",))
    initial = _state("initial", mode_by_job={"j1": "start"})
    transitions = (
        _finish_event("finish", source_mode="start"),
        _mode_event("detour", source_mode="start", target_mode="middle"),
        _finish_event("finish-middle", source_mode="middle"),
    )
    graph = enumerate_stable_lts(model, initial, transitions, max_states=8)
    assert graph.truncated is False
    assert graph.unavailable_reasons == ()
    return (
        graph,
        transitions,
        _state_id_by_mode(graph, "start"),
        graph.marked_state_ids[0],
    )


def _empty_absorbing_fixture() -> tuple[StableLTS, tuple[TransitionSpec, ...], str]:
    model = IMSModel(id="empty-absorbing", resources={}, jobs=())
    initial = _state("complete", complete=True)
    graph = enumerate_stable_lts(model, initial, (), max_states=4)
    assert graph.truncated is False
    assert graph.unavailable_reasons == ()
    assert graph.marked_state_ids == ("s0",)
    return graph, (), "s0"


def _simple_certified_partition_and_certificate() -> tuple[
    TerminalStoppingPartition,
    AbsorptionDomainCertificate,
    StableLTS,
    str,
]:
    graph, transitions, _start_state_id, finish_state_id = _simple_finish_fixture()
    partition = partition_stable_lts(
        IMSModel(id="simple-finish", resources={}, jobs=("j1",)),
        graph,
        transitions,
        event_rates={"finish": 1.0},
        verify_generated_lts=True,
    )
    certificate = certify_absorption_domain(
        partition,
        graph,
        {"finish": 1.0},
        selected_bad_state_ids=(),
        selected_success_state_ids=(finish_state_id,),
        policy_filter_declaration={
            "version": "ims-deadlock/g6-policy-filter-declaration/v1",
            "mode": "no_policy_filter",
            "excluded_plant_arcs": [],
        },
        require_global=True,
    )
    return partition, certificate, graph, finish_state_id


def _generated_global_deadlock_fixture() -> tuple[
    StableLTS, tuple[TransitionSpec, ...]
]:
    model = IMSModel(
        id="generated-global-deadlock",
        resources={"r1": Resource("r1", 1), "r2": Resource("r2", 1)},
        jobs=("j1", "j2"),
    )
    initial = _state(
        "deadlock",
        holds=(Holding("j1", "r1", 1), Holding("j2", "r2", 1)),
        requests={
            "j1": (RequestAlternative((ResourceDemand("r2", 1),)),),
            "j2": (RequestAlternative((ResourceDemand("r1", 1),)),),
        },
        mode_by_job={"j1": "waiting", "j2": "waiting"},
    )
    graph = enumerate_stable_lts(model, initial, (), max_states=4)
    assert graph.truncated is False
    assert graph.unavailable_reasons == ()
    assert len(graph.states) == 1
    return graph, ()


def _certified_certificate(
    *,
    false_assumption: str | None = None,
    rate_manifest_hash: str | None = "rate-hash",
) -> AbsorptionDomainCertificate:
    return AbsorptionDomainCertificate(
        version=ABSORPTION_DOMAIN_CERTIFICATE_VERSION,
        algorithm_version=ABSORPTION_DOMAIN_ALGORITHM_VERSION,
        certification_status=CERTIFIED_STATUS,
        reason_codes=(),
        selected_absorbing_state_ids=("s1",),
        unselected_closed_sccs=(),
        closed_class_reverse_basin_state_ids=("s0",),
        s_t_state_ids=("s0", "s1"),
        non_almost_sure_absorbing_state_ids=(),
        finite_state_space_verified=false_assumption != "finite_state_space_verified",
        complete_nontruncated_lts_verified=false_assumption
        != "complete_nontruncated_lts_verified",
        lts_generation_provenance_verified=false_assumption
        != "lts_generation_provenance_verified",
        positive_finite_rate_manifest_verified=false_assumption
        != "positive_finite_rate_manifest_verified",
        selected_target_identity_verified=false_assumption
        != "selected_target_identity_verified",
        policy_filter_identity_verified=false_assumption
        != "policy_filter_identity_verified",
        state_space_hash="state-hash",
        partition_hash="partition-hash",
        rate_manifest_hash=rate_manifest_hash,
        positive_rate_graph_hash="positive-rate-hash",
        policy_filter_hash="policy-filter-hash",
        absorption_domain_hash="absorption-domain-hash",
    )


def test_estimand_spec_validates_selected_classes_and_exclusivity() -> None:
    assert DEFAULT_ESTIMAND_SPEC.selected_bad_classes == ("D_global", "D_local")
    assert DEFAULT_ESTIMAND_SPEC.success_class == "F"
    assert VersionedEstimandSpec(
        selected_bad_classes=("D_local", "D_global")
    ).selected_bad_classes == ("D_global", "D_local")

    with pytest.raises(ValueError, match="unknown selected bad class"):
        VersionedEstimandSpec(selected_bad_classes=("D_global", "R_livelock"))

    with pytest.raises(ValueError, match="must not include the success class"):
        VersionedEstimandSpec(selected_bad_classes=("F",))

    with pytest.raises(ValueError, match="duplicate selected"):
        VersionedEstimandSpec(selected_bad_classes=("D_local", "D_local"))

    with pytest.raises(ValueError, match="version must be nonempty"):
        VersionedEstimandSpec(version="")

    with pytest.raises(ValueError, match="policy_analysis_class must be P_policy"):
        VersionedEstimandSpec(policy_analysis_class="custom_policy")


def test_local_first_hit_keeps_free_job_transient_edge_but_selects_local_bad() -> None:
    model = _local_model()
    local_state = _state(
        "local",
        holds=(Holding("j1", "r1", 1), Holding("j2", "r2", 1)),
        requests={
            "j1": (RequestAlternative((ResourceDemand("r2", 1),)),),
            "j2": (RequestAlternative((ResourceDemand("r1", 1),)),),
        },
        mode_by_job={"j1": "waiting_r2", "j2": "waiting_r1", "free_job": "ready"},
    )
    after_free = _state(
        "after-free",
        holds=(Holding("j1", "r1", 1), Holding("j2", "r2", 1)),
        requests=local_state.requests,
        completed_jobs=frozenset({"free_job"}),
        mode_by_job={
            "j1": "waiting_r2",
            "j2": "waiting_r1",
        },
    )
    free_transition = TransitionSpec(
        name="complete-free-job",
        kind=EventKind.SERVICE_COMPLETE,
        job_id="free_job",
        source_mode="ready",
        target_mode="completed",
        controllable=False,
        zero_time=False,
        mark_complete=True,
    )
    graph = _lts(
        (
            _record("s0", local_state),
            _record("s1", after_free, ("complete-free-job",)),
        ),
        (StableLTSArc("s0", "complete-free-job", "s1", False, ("complete-free-job",)),),
    )

    partition = partition_stable_lts(model, graph, (free_transition,))

    assert partition.d_local_state_ids == ("s0",)
    assert partition.d_global_state_ids == ("s1",)
    assert partition.f_state_ids == ()
    assert ("s0", "complete-free-job", "s1") in partition.plant_arcs
    assert partition.terminal_sccs == ()
    assert partition.selected_bad_state_ids == ("s0", "s1")
    assert partition.local_bad_soundness_audit == {
        "method": "complete_lts_completion_nonreachability_v1",
        "verified": True,
        "candidate_state_ids": ["s0"],
        "completion_state_ids": [],
        "completion_reachable_candidate_state_ids": [],
    }
    assert partition.to_json_dict()["local_bad_soundness_audit"] == (
        partition.local_bad_soundness_audit
    )


def test_local_kernel_with_future_external_bypass_is_structured_refusal() -> None:
    model = IMSModel(
        id="local-kernel-future-bypass",
        resources={
            "r1": Resource("r1", 1),
            "r2": Resource("r2", 1),
            "r3": Resource("r3", 1),
        },
        jobs=("j1", "j2", "j3"),
    )
    initial = _state(
        "initial",
        holds=(
            Holding("j1", "r1", 1),
            Holding("j2", "r2", 1),
            Holding("j3", "r3", 1),
        ),
        requests={
            "j1": (RequestAlternative((ResourceDemand("r2", 1),)),),
            "j2": (RequestAlternative((ResourceDemand("r1", 1),)),),
        },
        mode_by_job={"j1": "waiting", "j2": "waiting", "j3": "working"},
    )
    rules = (
        TransitionSpec(
            name="release-r3",
            kind=EventKind.SERVICE_COMPLETE,
            job_id="j3",
            source_mode="working",
            target_mode="completed",
            controllable=False,
            zero_time=False,
            release=(ResourceDemand("r3", 1),),
            mark_complete=True,
        ),
        TransitionSpec(
            name="j1-bypass-on-r3",
            kind=EventKind.SERVICE_COMPLETE,
            job_id="j1",
            source_mode="waiting",
            target_mode="completed",
            controllable=False,
            zero_time=False,
            requires=(RequestAlternative((ResourceDemand("r3", 1),)),),
            release=(ResourceDemand("r1", 1),),
            clears_requests=True,
            mark_complete=True,
        ),
        TransitionSpec(
            name="j2-finish-on-r1",
            kind=EventKind.SERVICE_COMPLETE,
            job_id="j2",
            source_mode="waiting",
            target_mode="completed",
            controllable=False,
            zero_time=False,
            requires=(RequestAlternative((ResourceDemand("r1", 1),)),),
            release=(ResourceDemand("r2", 1),),
            clears_requests=True,
            mark_complete=True,
        ),
    )
    graph = enumerate_stable_lts(model, initial, rules, max_states=16)
    assert graph.truncated is False
    assert graph.marked_state_ids

    with pytest.raises(TerminalPartitionError) as excinfo:
        partition_stable_lts(model, graph, rules, verify_generated_lts=True)

    assert excinfo.value.code == "local_core_completion_reachable"
    assert excinfo.value.details["candidate_state_ids"] == ["s0"]
    assert excinfo.value.details["completion_state_ids"]
    assert excinfo.value.details["counterexample_event_paths"] == {
        "s0": ["release-r3", "j1-bypass-on-r3", "j2-finish-on-r1"]
    }


def test_arbitrary_waiting_without_capacity_kernel_is_not_local_bad() -> None:
    model = IMSModel(
        id="non-capacity-wait",
        resources={"r1": Resource("r1", 2), "r2": Resource("r2", 2)},
        jobs=("j1", "j2"),
    )
    waiting = _state(
        "waiting",
        holds=(Holding("j1", "r1", 1),),
        requests={"j1": (RequestAlternative((ResourceDemand("r2", 1),)),)},
    )
    done = _state("done", completed_jobs=frozenset({"j1", "j2"}), complete=True)
    graph = _lts(
        (_record("s0", waiting), _record("s1", done)),
        (StableLTSArc("s0", "finish", "s1", False, ("finish",)),),
    )

    partition = partition_stable_lts(model, graph, (_event("finish"),))

    assert partition.d_local_state_ids == ()
    assert partition.transient_state_ids == ("s0",)
    assert partition.f_state_ids == ("s1",)


def test_generated_lts_verifier_rejects_hand_built_arc_semantics() -> None:
    model = IMSModel(id="forged-lts-model", resources={}, jobs=("j1",))
    start = _state("start", mode_by_job={"j1": "blocked"})
    done = _state(
        "done",
        completed_jobs=frozenset({"j1"}),
        complete=True,
        mode_by_job={"j1": "completed"},
    )
    graph = _lts(
        (_record("s0", start), _record("s1", done)),
        (StableLTSArc("s0", "finish", "s1", False, ("finish",)),),
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        partition_stable_lts(
            model,
            graph,
            (_event("finish"),),
            verify_generated_lts=True,
        )

    assert excinfo.value.code == "lts_generation_mismatch"
    assert excinfo.value.details["state_space_match"] is False
    assert excinfo.value.details["plant_arc_match"] is False


def test_closed_sccs_distinguish_terminal_singleton_and_livelock() -> None:
    model = IMSModel(id="closed-scc-model", resources={}, jobs=("j1",))
    terminal = _state("terminal")
    live_a = _state("live-a")
    live_b = _state("live-b")
    graph = _lts(
        (
            _record("s0", terminal),
            _record("s1", live_a),
            _record("s2", live_b),
        ),
        (
            StableLTSArc("s1", "a", "s2", False, ("a",)),
            StableLTSArc("s2", "b", "s1", False, ("b",)),
        ),
    )

    partition = partition_stable_lts(model, graph, (_event("a"), _event("b")))

    assert partition.r_terminal_state_ids == ("s0",)
    assert partition.r_livelock_state_ids == ("s1", "s2")


def test_incomplete_partition_raises_structured_error() -> None:
    model = IMSModel(id="incomplete-model", resources={}, jobs=("j1",))
    s0 = _state("s0")
    s1 = _state("s1")
    graph = _lts(
        (_record("s0", s0), _record("s1", s1)),
        (StableLTSArc("s0", "to_missing", "missing", False, ("to_missing",)),),
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        partition_stable_lts(model, graph, (_event("to_missing"),))

    assert excinfo.value.code == "transition_target_missing"
    assert excinfo.value.details["target"] == "missing"


@pytest.mark.parametrize(
    ("truncated", "unavailable_reasons", "expected_details"),
    [
        (True, (), {"truncated": True, "truncated_arc_count": 0}),
        (
            False,
            ("zero_time_closure_nontermination",),
            {"unavailable_reasons": ["zero_time_closure_nontermination"]},
        ),
    ],
)
def test_partition_refuses_incomplete_stable_lts(
    truncated: bool,
    unavailable_reasons: tuple[str, ...],
    expected_details: dict[str, object],
) -> None:
    model = IMSModel(id="incomplete-lts-model", resources={}, jobs=("j1",))
    graph = replace(
        _lts((_record("s0", _state("start")),)),
        truncated=truncated,
        unavailable_reasons=unavailable_reasons,
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        partition_stable_lts(model, graph, ())

    assert excinfo.value.code == "incomplete_stable_lts"
    assert excinfo.value.details == expected_details


def test_partition_refuses_model_invalid_completion_state() -> None:
    model = IMSModel(id="invalid-completion-model", resources={}, jobs=("j1",))
    invalid_complete = _state("invalid", complete=True)
    graph = _lts((_record("s0", invalid_complete),))

    with pytest.raises(TerminalPartitionError) as excinfo:
        partition_stable_lts(model, graph, ())

    assert excinfo.value.code == "invalid_lts_state"
    assert excinfo.value.details["state_id"] == "s0"
    assert excinfo.value.details["issues"] == [
        {
            "code": "complete_state_has_open_work",
            "message": (
                "complete state must have all jobs completed and no holds or requests"
            ),
        }
    ]


def test_hashes_are_stable_and_drift_with_rules_rates_and_stopping() -> None:
    model = _local_model()
    completion = _state(
        "complete",
        completed_jobs=frozenset({"j1", "j2", "free_job"}),
        complete=True,
    )
    graph = _lts((_record("s0", _state("start")), _record("s1", completion)))
    finish = _event("finish", job_id="free_job")

    base = partition_stable_lts(
        model,
        graph,
        (finish,),
        event_rates={"finish": 1.0},
        estimand_spec=DEFAULT_ESTIMAND_SPEC,
    )
    rate_drift = partition_stable_lts(
        model,
        graph,
        (finish,),
        event_rates={"finish": 2.0},
        estimand_spec=DEFAULT_ESTIMAND_SPEC,
    )
    rule_drift = partition_stable_lts(
        model,
        graph,
        (finish,),
        event_rates={"finish": 1.0},
        estimand_spec=VersionedEstimandSpec(selected_bad_classes=("D_global",)),
    )
    stopping_drift = partition_stable_lts(
        model,
        graph,
        (finish,),
        event_rates={"finish": 1.0},
        estimand_spec=VersionedEstimandSpec(
            exact_stopping_rule="exact/changed",
            des_stopping_rule="des/changed",
        ),
    )

    assert (
        base.partition_hash
        == partition_stable_lts(
            model,
            graph,
            (finish,),
            event_rates={"finish": 1.0},
            estimand_spec=DEFAULT_ESTIMAND_SPEC,
        ).partition_hash
    )
    assert base.rate_manifest_hash != rate_drift.rate_manifest_hash
    assert base.stopping_rule_hash != stopping_drift.stopping_rule_hash
    assert base.des_stopping_rule_hash != stopping_drift.des_stopping_rule_hash
    assert base.stopping_rule_hash != rule_drift.stopping_rule_hash
    assert base.estimand_id is None
    assert rate_drift.estimand_id is None
    assert rule_drift.estimand_id is None
    assert stopping_drift.estimand_id is None


def test_selected_reachable_s_t_differs_from_all_nonabsorbing() -> None:
    model = IMSModel(id="s-t-model", resources={}, jobs=("j1",))
    start = _state("start")
    done = _state("done", completed_jobs=frozenset({"j1"}), complete=True)
    unreachable = _state("unreachable-closed")
    graph = _lts(
        (_record("s0", start), _record("s1", done), _record("s2", unreachable)),
        (StableLTSArc("s0", "finish", "s1", False, ("finish",)),),
    )

    partition = partition_stable_lts(model, graph, (_event("finish"),))
    payload = partition.to_json_dict()

    assert partition.transient_state_ids == ("s0", "s2")
    assert partition.selected_reachable_state_ids == ("s0",)
    derived_state_sets = cast(dict[str, object], payload["derived_state_sets"])
    s_reach = cast(dict[str, object], derived_state_sets["S_reach"])
    assert s_reach["state_ids"] == ["s0"]

    assert partition.unreachable_nonabsorbing_state_ids == ("s2",)


def test_partition_hash_is_independent_of_selected_bad_union() -> None:
    model = _local_model()
    local_state = _state(
        "local",
        holds=(Holding("j1", "r1", 1), Holding("j2", "r2", 1)),
        requests={
            "j1": (RequestAlternative((ResourceDemand("r2", 1),)),),
            "j2": (RequestAlternative((ResourceDemand("r1", 1),)),),
        },
    )
    graph = _lts((_record("s0", local_state),))

    both = partition_stable_lts(
        model,
        graph,
        (),
        estimand_spec=VersionedEstimandSpec(
            selected_bad_classes=("D_local", "D_global")
        ),
    )
    global_only = partition_stable_lts(
        model,
        graph,
        (),
        estimand_spec=VersionedEstimandSpec(selected_bad_classes=("D_global",)),
    )

    assert both.partition_hash == global_only.partition_hash
    assert both.stopping_rule_hash != global_only.stopping_rule_hash
    assert both.estimand_id is None
    assert global_only.estimand_id is None


def test_reversed_selected_bad_classes_have_identical_hashes() -> None:
    model = _local_model()
    graph = _lts((_record("s0", _state("start")),))

    forward = partition_stable_lts(
        model,
        graph,
        (),
        estimand_spec=VersionedEstimandSpec(
            selected_bad_classes=("D_global", "D_local")
        ),
    )
    reversed_order = partition_stable_lts(
        model,
        graph,
        (),
        estimand_spec=VersionedEstimandSpec(
            selected_bad_classes=("D_local", "D_global")
        ),
    )

    assert forward.stopping_rule_hash == reversed_order.stopping_rule_hash
    assert forward.estimand_id == reversed_order.estimand_id


def test_partition_hash_is_independent_of_lts_provenance_verification_mode() -> None:
    model = IMSModel(id="generated-provenance-model", resources={}, jobs=("j1",))
    initial = _state("start", mode_by_job={"j1": "ready"})
    finish = TransitionSpec(
        name="finish",
        kind=EventKind.SERVICE_COMPLETE,
        job_id="j1",
        source_mode="ready",
        target_mode="completed",
        controllable=False,
        zero_time=False,
        mark_complete=True,
    )
    graph = enumerate_stable_lts(model, initial, (finish,), max_states=8)
    assert graph.truncated is False
    assert graph.unavailable_reasons == ()

    caller_contract = partition_stable_lts(
        model,
        graph,
        (finish,),
        verify_generated_lts=False,
    )
    verified = partition_stable_lts(
        model,
        graph,
        (finish,),
        verify_generated_lts=True,
    )

    assert caller_contract.state_space_hash == verified.state_space_hash
    assert caller_contract.d_global_state_ids == verified.d_global_state_ids
    assert caller_contract.d_local_state_ids == verified.d_local_state_ids
    assert caller_contract.f_state_ids == verified.f_state_ids
    assert caller_contract.r_livelock_state_ids == verified.r_livelock_state_ids
    assert caller_contract.r_terminal_state_ids == verified.r_terminal_state_ids
    assert caller_contract.plant_arcs == verified.plant_arcs
    caller_payload = caller_contract.plant_partition_json_dict()
    verified_payload = verified.plant_partition_json_dict()
    if caller_payload != verified_payload:
        assert [
            key
            for key in sorted(set(caller_payload) | set(verified_payload))
            if caller_payload.get(key) != verified_payload.get(key)
        ] == ["lts_provenance_audit"]
    assert caller_contract.partition_hash == verified.partition_hash


def test_unknown_lts_arc_event_is_structured_refusal() -> None:
    model = IMSModel(id="registry-model", resources={}, jobs=("j1",))
    graph = _lts(
        (_record("s0", _state("start")), _record("s1", _state("done"))),
        (StableLTSArc("s0", "not-declared", "s1", False, ("not-declared",)),),
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        partition_stable_lts(model, graph, (_event("declared"),))

    assert excinfo.value.code == "unknown_lts_event"
    assert excinfo.value.details["event"] == "not-declared"


def test_rate_manifest_rejects_invalid_or_missing_arc_rates() -> None:
    model = IMSModel(id="rate-model", resources={}, jobs=("j1",))
    graph = _lts(
        (_record("s0", _state("start")), _record("s1", _state("done"))),
        (StableLTSArc("s0", "go", "s1", False, ("go",)),),
    )

    for bad_rate in (True, 0.0, -1.0, float("nan"), float("inf")):
        with pytest.raises(TerminalPartitionError) as excinfo:
            partition_stable_lts(
                model,
                graph,
                (_event("go"),),
                event_rates={"go": bad_rate},
            )
        assert excinfo.value.code == "invalid_event_rate"

    with pytest.raises(TerminalPartitionError) as excinfo:
        partition_stable_lts(
            model,
            graph,
            (_event("go"),),
            event_rates={"other": 1.0},
        )
    assert excinfo.value.code == "missing_event_rate"
    assert excinfo.value.details["event"] == "go"


@pytest.mark.parametrize(
    "field_name",
    [
        "finite_state_space_verified",
        "complete_nontruncated_lts_verified",
        "lts_generation_provenance_verified",
        "positive_finite_rate_manifest_verified",
        "selected_target_identity_verified",
        "policy_filter_identity_verified",
    ],
)
def test_certified_absorption_certificate_requires_all_assumptions_true(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match="certified absorption certificate"):
        _certified_certificate(false_assumption=field_name)


def test_certified_absorption_certificate_requires_rate_manifest_hash() -> None:
    with pytest.raises(ValueError, match="certified absorption certificate"):
        _certified_certificate(rate_manifest_hash=None)


def test_v3_serialization_separates_plant_policy_and_derived_sets() -> None:
    model = _local_model()
    start = _state("start")
    done = _state(
        "done",
        completed_jobs=frozenset({"j1", "j2", "free_job"}),
        complete=True,
    )
    graph = _lts(
        (_record("s0", start), _record("s1", done)),
        (StableLTSArc("s0", "finish", "s1", False, ("finish",)),),
    )

    payload = partition_stable_lts(
        model,
        graph,
        (_event("finish", job_id="free_job"),),
    ).to_json_dict()

    classes = cast(dict[str, object], payload["classes"])
    assert set(classes) == {"D_global", "D_local", "F", "R_livelock", "R_terminal"}
    assert classes == {
        "D_global": [],
        "D_local": [],
        "F": ["s1"],
        "R_livelock": [],
        "R_terminal": [],
    }
    assert payload["policy_analysis_classes"] == {"P_policy": []}
    assert "P_policy" not in classes
    assert "S_T" not in classes
    derived_state_sets = cast(dict[str, object], payload["derived_state_sets"])
    assert set(derived_state_sets) == {
        "S_reach",
        "S_T",
        "unselected_closed_sccs",
        "closed_class_reverse_basin_state_ids",
        "non_almost_sure_absorbing_state_ids",
    }
    s_reach = cast(dict[str, object], derived_state_sets["S_reach"])
    assert set(s_reach) == {
        "state_ids",
        "support_unreachable_state_ids",
        "graph_semantics",
        "positive_rate_verified",
    }
    assert s_reach["state_ids"] == ["s0"]
    assert s_reach["support_unreachable_state_ids"] == []
    assert s_reach["graph_semantics"] == "complete_stopped_lts_support"
    assert s_reach["positive_rate_verified"] is False
    assert "selected_reachable_state_ids" not in payload
    assert "unreachable_nonabsorbing_state_ids" not in payload


def test_classification_without_rates_is_explicitly_uncertified() -> None:
    model = _local_model()
    start = _state("start")
    done = _state(
        "done",
        completed_jobs=frozenset({"j1", "j2", "free_job"}),
        complete=True,
    )
    graph = _lts(
        (_record("s0", start), _record("s1", done)),
        (StableLTSArc("s0", "finish", "s1", False, ("finish",)),),
    )

    partition = partition_stable_lts(
        model,
        graph,
        (_event("finish", job_id="free_job"),),
    )
    payload = partition.to_json_dict()
    hashes = cast(dict[str, object], payload["hashes"])
    derived_state_sets = cast(dict[str, object], payload["derived_state_sets"])
    s_reach = cast(dict[str, object], derived_state_sets["S_reach"])
    s_t = cast(dict[str, object], derived_state_sets["S_T"])
    certificate = cast(dict[str, object], payload["absorption_domain_certificate"])
    identity = cast(dict[str, object], certificate["identity"])
    assumptions = cast(dict[str, object], certificate["assumptions"])

    assert s_reach == {
        "state_ids": ["s0"],
        "support_unreachable_state_ids": [],
        "graph_semantics": "complete_stopped_lts_support",
        "positive_rate_verified": False,
    }
    assert s_t == {
        "state_ids": None,
        "certification_status": "not_certified",
        "reason_codes": ["rate_manifest_absent"],
    }
    assert hashes["rate_manifest_hash"] is None
    assert hashes["positive_rate_graph_hash"] is None
    assert hashes["policy_filter_hash"] is None
    assert hashes["absorption_domain_hash"] is None
    assert hashes["estimand_id"] is None
    assert certificate["version"] == "ims-deadlock/g6-absorption-domain-certificate/v1"
    assert certificate["algorithm_version"] == (
        "finite-positive-rate-stopped-ctmc-scc-domain/v1"
    )
    assert certificate["certification_status"] == "not_certified"
    assert certificate["reason_codes"] == ["rate_manifest_absent"]
    assert certificate["selected_absorbing_state_ids"] == ["s1"]
    assert identity == {
        "state_space_hash": partition.state_space_hash,
        "partition_hash": partition.partition_hash,
        "rate_manifest_hash": None,
        "positive_rate_graph_hash": None,
        "policy_filter_hash": None,
        "absorption_domain_hash": None,
    }
    assert assumptions == {
        "finite_state_space_verified": True,
        "complete_nontruncated_lts_verified": True,
        "lts_generation_provenance_verified": False,
        "positive_finite_rate_manifest_verified": False,
        "selected_target_identity_verified": True,
        "policy_filter_identity_verified": False,
    }


def test_absent_and_explicitly_empty_rate_manifests_are_distinct() -> None:
    model = IMSModel(id="edgeless-model", resources={}, jobs=())
    complete = _state("complete", complete=True)
    graph = _lts((_record("s0", complete),))

    absent = partition_stable_lts(model, graph, (), event_rates=None)
    explicit_empty = partition_stable_lts(model, graph, (), event_rates={})

    assert absent.rate_manifest_hash is None
    assert explicit_empty.rate_manifest_hash is not None
    assert absent.positive_rate_graph_hash is None
    assert explicit_empty.positive_rate_graph_hash is None
    assert absent.estimand_id is None
    assert explicit_empty.estimand_id is None
    assert absent.absorption_domain_certificate.reason_codes == (
        "rate_manifest_absent",
    )
    assert explicit_empty.absorption_domain_certificate.reason_codes == (
        "absorption_domain_not_certified",
    )
    assert (
        explicit_empty.absorption_domain_certificate.rate_manifest_hash
        == explicit_empty.rate_manifest_hash
    )


def test_rate_manifest_keys_exactly_match_declared_transition_events() -> None:
    model = IMSModel(id="rate-registry-model", resources={}, jobs=("j1",))
    graph = _lts(
        (_record("s0", _state("start")), _record("s1", _state("done"))),
        (StableLTSArc("s0", "realized", "s1", False, ("realized",)),),
    )
    transitions = (_event("realized"), _event("declared-unreachable"))

    partition = partition_stable_lts(
        model,
        graph,
        transitions,
        event_rates={"declared-unreachable": 2.0, "realized": 1.0},
    )

    assert partition.declared_transition_event_names == (
        "declared-unreachable",
        "realized",
    )
    assert partition.rate_manifest_hash is not None

    with pytest.raises(TerminalPartitionError) as excinfo:
        partition_stable_lts(model, graph, transitions, event_rates={"realized": 1.0})
    assert excinfo.value.code == "missing_event_rate"
    assert excinfo.value.details["event"] == "declared-unreachable"

    with pytest.raises(TerminalPartitionError) as excinfo:
        partition_stable_lts(
            model,
            graph,
            transitions,
            event_rates={
                "declared-unreachable": 2.0,
                "realized": 1.0,
                "extra": 3.0,
            },
        )
    assert excinfo.value.code == "unexpected_event_rate"
    assert excinfo.value.details["event"] == "extra"


def test_plant_partition_payload_excludes_policy_and_derived_sets() -> None:
    model = _local_model()
    start = _state("start")
    done = _state(
        "done",
        completed_jobs=frozenset({"j1", "j2", "free_job"}),
        complete=True,
    )
    graph = _lts(
        (_record("s0", start), _record("s1", done)),
        (StableLTSArc("s0", "finish", "s1", False, ("finish",)),),
    )

    partition = partition_stable_lts(
        model,
        graph,
        (_event("finish", job_id="free_job"),),
    )
    payload = partition.plant_partition_json_dict()
    full_payload = partition.to_json_dict()

    assert set(payload) == {
        "classification_version",
        "classes",
        "bad_hit_sets",
        "local_bad_soundness_audit",
        "terminal_sccs",
        "plant_arcs",
    }
    classes = cast(dict[str, object], payload["classes"])
    assert set(classes) == {"D_global", "D_local", "F", "R_livelock", "R_terminal"}
    assert "P_policy" not in classes
    assert "S_T" not in classes
    assert "policy_analysis_classes" not in payload
    assert "derived_state_sets" not in payload
    assert "selected_bad_state_ids" not in payload
    assert "selected_reachable_state_ids" not in payload
    assert "lts_provenance_audit" not in payload
    assert "lts_provenance_audit" in full_payload


def test_estimand_spec_v2_uses_policy_analysis_class() -> None:
    spec = VersionedEstimandSpec(policy_analysis_class="P_policy")

    assert spec.version == "ims-deadlock/g6-versioned-estimand/v2"
    assert spec.policy_analysis_class == "P_policy"
    assert spec.to_json_dict()["policy_analysis_class"] == "P_policy"
    assert "plant_policy_class" not in spec.to_json_dict()

    with pytest.raises(ValueError, match="policy_analysis_class must be P_policy"):
        VersionedEstimandSpec(policy_analysis_class="custom_policy")


def test_branching_closed_class_separates_s_reach_from_s_t() -> None:
    graph, transitions, start_state_id, closed_state_id, finish_state_id = (
        _branching_closed_fixture()
    )
    partition = partition_stable_lts(
        IMSModel(id="branching-ce-nb1", resources={}, jobs=("j1",)),
        graph,
        transitions,
        event_rates={transition.name: 1.0 for transition in transitions},
        verify_generated_lts=True,
    )

    certificate = certify_absorption_domain(
        partition,
        graph,
        {transition.name: 1.0 for transition in transitions},
        selected_bad_state_ids=partition.selected_bad_state_ids,
        selected_success_state_ids=(finish_state_id,),
        policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
        require_global=False,
    )

    assert partition.selected_reachable_state_ids == (start_state_id,)
    assert certificate.unselected_closed_sccs == ((closed_state_id,),)
    assert certificate.closed_class_reverse_basin_state_ids == tuple(
        sorted((closed_state_id, start_state_id))
    )
    assert certificate.s_t_state_ids == ()
    assert certificate.non_almost_sure_absorbing_state_ids == tuple(
        sorted((closed_state_id, start_state_id))
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        certify_absorption_domain(
            partition,
            graph,
            {transition.name: 1.0 for transition in transitions},
            selected_bad_state_ids=partition.selected_bad_state_ids,
            selected_success_state_ids=(finish_state_id,),
            policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
            require_global=True,
        )
    assert excinfo.value.code == "non_almost_sure_absorption_domain"
    assert excinfo.value.details["certificate"] == certificate.to_json_dict()


def test_full_positive_rate_domain_certifies_global_s_t() -> None:
    graph, transitions, start_state_id, finish_state_id = _simple_finish_fixture()
    partition = partition_stable_lts(
        IMSModel(id="simple-finish", resources={}, jobs=("j1",)),
        graph,
        transitions,
        event_rates={"finish": 1.0},
        verify_generated_lts=True,
    )

    certificate = certify_absorption_domain(
        partition,
        graph,
        {"finish": 1.0},
        selected_bad_state_ids=(),
        selected_success_state_ids=(finish_state_id,),
        policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
        require_global=True,
    )

    assert certificate.certification_status == CERTIFIED_STATUS
    assert certificate.unselected_closed_sccs == ()
    assert certificate.closed_class_reverse_basin_state_ids == ()
    assert certificate.s_t_state_ids == (start_state_id,)
    assert certificate.non_almost_sure_absorbing_state_ids == ()


def test_explicit_empty_manifest_certifies_empty_nonabsorbing_domain() -> None:
    graph, transitions, finish_state_id = _empty_absorbing_fixture()
    partition = partition_stable_lts(
        IMSModel(id="empty-absorbing", resources={}, jobs=()),
        graph,
        transitions,
        event_rates={},
        verify_generated_lts=True,
    )

    certificate = certify_absorption_domain(
        partition,
        graph,
        {},
        selected_bad_state_ids=(),
        selected_success_state_ids=(finish_state_id,),
        policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
        require_global=True,
    )

    assert certificate.unselected_closed_sccs == ()
    assert certificate.closed_class_reverse_basin_state_ids == ()
    assert certificate.s_t_state_ids == ()
    assert certificate.non_almost_sure_absorbing_state_ids == ()


def test_missing_rate_manifest_fails_scientific_certification() -> None:
    graph, transitions, _start_state_id, finish_state_id = _simple_finish_fixture()
    partition = partition_stable_lts(
        IMSModel(id="simple-finish", resources={}, jobs=("j1",)),
        graph,
        transitions,
        event_rates={"finish": 1.0},
        verify_generated_lts=True,
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        certify_absorption_domain(
            partition,
            graph,
            None,
            selected_bad_state_ids=(),
            selected_success_state_ids=(finish_state_id,),
            policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
            require_global=True,
        )
    assert excinfo.value.code == "missing_rate_manifest"


@pytest.mark.parametrize("bad_rate", [True, 0.0, -1.0, float("nan"), float("inf")])
def test_zero_rate_fails_scientific_certification(bad_rate: object) -> None:
    graph, transitions, _start_state_id, finish_state_id = _simple_finish_fixture()
    partition = partition_stable_lts(
        IMSModel(id="simple-finish", resources={}, jobs=("j1",)),
        graph,
        transitions,
        event_rates={"finish": 1.0},
        verify_generated_lts=True,
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        certify_absorption_domain(
            partition,
            graph,
            {"finish": cast(float, bad_rate)},
            selected_bad_state_ids=(),
            selected_success_state_ids=(finish_state_id,),
            policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
            require_global=True,
        )
    assert excinfo.value.code == "invalid_event_rate"


def test_extra_rate_event_fails_scientific_certification() -> None:
    graph, transitions, _start_state_id, finish_state_id = _simple_finish_fixture()
    partition = partition_stable_lts(
        IMSModel(id="simple-finish", resources={}, jobs=("j1",)),
        graph,
        transitions,
        event_rates={"finish": 1.0},
        verify_generated_lts=True,
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        certify_absorption_domain(
            partition,
            graph,
            {"finish": 1.0, "extra": 1.0},
            selected_bad_state_ids=(),
            selected_success_state_ids=(finish_state_id,),
            policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
            require_global=True,
        )
    assert excinfo.value.code == "unexpected_event_rate"


def test_truncated_lts_fails_scientific_certification() -> None:
    graph, transitions, _start_state_id, finish_state_id = _simple_finish_fixture()
    model = IMSModel(id="simple-finish", resources={}, jobs=("j1",))
    partition = partition_stable_lts(
        model,
        graph,
        transitions,
        event_rates={"finish": 1.0},
        verify_generated_lts=True,
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        certify_absorption_domain(
            partition,
            replace(graph, truncated=True),
            {"finish": 1.0},
            selected_bad_state_ids=(),
            selected_success_state_ids=(finish_state_id,),
            policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
            require_global=True,
        )
    assert excinfo.value.code == "incomplete_stable_lts"


def test_unavailable_branch_fails_scientific_certification() -> None:
    graph, transitions, _start_state_id, finish_state_id = _simple_finish_fixture()
    partition = partition_stable_lts(
        IMSModel(id="simple-finish", resources={}, jobs=("j1",)),
        graph,
        transitions,
        event_rates={"finish": 1.0},
        verify_generated_lts=True,
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        certify_absorption_domain(
            partition,
            replace(graph, unavailable_reasons=("branch_unavailable",)),
            {"finish": 1.0},
            selected_bad_state_ids=(),
            selected_success_state_ids=(finish_state_id,),
            policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
            require_global=True,
        )
    assert excinfo.value.code == "incomplete_stable_lts"


def test_unverified_lts_provenance_fails_certification() -> None:
    graph, transitions, _start_state_id, finish_state_id = _simple_finish_fixture()
    partition = partition_stable_lts(
        IMSModel(id="simple-finish", resources={}, jobs=("j1",)),
        graph,
        transitions,
        event_rates={"finish": 1.0},
        verify_generated_lts=False,
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        certify_absorption_domain(
            partition,
            graph,
            {"finish": 1.0},
            selected_bad_state_ids=(),
            selected_success_state_ids=(finish_state_id,),
            policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
            require_global=True,
        )
    assert excinfo.value.code == "unverified_lts_provenance"
    assert excinfo.value.details["method"] == "caller_contract_only"


def test_selected_target_drift_fails_certification() -> None:
    graph, transitions, _start_state_id, finish_state_id = _simple_finish_fixture()
    partition = partition_stable_lts(
        IMSModel(id="simple-finish", resources={}, jobs=("j1",)),
        graph,
        transitions,
        event_rates={"finish": 1.0},
        verify_generated_lts=True,
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        certify_absorption_domain(
            partition,
            graph,
            {"finish": 1.0},
            selected_bad_state_ids=(finish_state_id,),
            selected_success_state_ids=(finish_state_id,),
            policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
            require_global=True,
        )
    assert excinfo.value.code == "selected_target_drift"


def test_policy_filter_drift_fails_certification() -> None:
    graph, transitions, _start_state_id, finish_state_id = _simple_finish_fixture()
    partition = partition_stable_lts(
        IMSModel(id="simple-finish", resources={}, jobs=("j1",)),
        graph,
        transitions,
        event_rates={"finish": 1.0},
        verify_generated_lts=True,
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        certify_absorption_domain(
            partition,
            graph,
            {"finish": 1.0},
            selected_bad_state_ids=(),
            selected_success_state_ids=(finish_state_id,),
            policy_filter_declaration={"mode": "custom"},
            require_global=True,
        )
    assert excinfo.value.code == "policy_filter_drift"


def test_absorption_hash_binds_target_support_and_closed_basin() -> None:
    graph, transitions, _start_state_id, _closed_state_id, finish_state_id = (
        _branching_closed_fixture()
    )
    model = IMSModel(id="branching-ce-nb1", resources={}, jobs=("j1",))
    rates = {transition.name: 1.0 for transition in transitions}
    partition = partition_stable_lts(
        model, graph, transitions, event_rates=rates, verify_generated_lts=True
    )
    base = certify_absorption_domain(
        partition,
        graph,
        rates,
        selected_bad_state_ids=(),
        selected_success_state_ids=(finish_state_id,),
        policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
        require_global=False,
    )
    changed_rate_partition = partition_stable_lts(
        model,
        graph,
        transitions,
        event_rates={**rates, "finish": 2.0},
        verify_generated_lts=True,
    )
    changed_rates = certify_absorption_domain(
        changed_rate_partition,
        graph,
        {**rates, "finish": 2.0},
        selected_bad_state_ids=(),
        selected_success_state_ids=(finish_state_id,),
        policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
        require_global=False,
    )
    detour_graph, detour_transitions, _detour_start_id, detour_finish_id = (
        _detour_finish_fixture()
    )
    detour_model = IMSModel(id="detour-finish", resources={}, jobs=("j1",))
    detour_rates = {transition.name: 1.0 for transition in detour_transitions}
    detour_partition = partition_stable_lts(
        detour_model,
        detour_graph,
        detour_transitions,
        event_rates=detour_rates,
        verify_generated_lts=True,
    )
    detour = certify_absorption_domain(
        detour_partition,
        detour_graph,
        detour_rates,
        selected_bad_state_ids=(),
        selected_success_state_ids=(detour_finish_id,),
        policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
        require_global=True,
    )
    deadlock_graph, deadlock_transitions = _generated_global_deadlock_fixture()
    deadlock_model = IMSModel(
        id="generated-global-deadlock",
        resources={"r1": Resource("r1", 1), "r2": Resource("r2", 1)},
        jobs=("j1", "j2"),
    )
    selected_deadlock = partition_stable_lts(
        deadlock_model,
        deadlock_graph,
        deadlock_transitions,
        event_rates={},
        estimand_spec=VersionedEstimandSpec(selected_bad_classes=("D_global",)),
        verify_generated_lts=True,
    )
    unselected_deadlock = partition_stable_lts(
        deadlock_model,
        deadlock_graph,
        deadlock_transitions,
        event_rates={},
        estimand_spec=VersionedEstimandSpec(selected_bad_classes=("D_local",)),
        verify_generated_lts=True,
    )
    selected_deadlock_certificate = certify_absorption_domain(
        selected_deadlock,
        deadlock_graph,
        {},
        selected_bad_state_ids=selected_deadlock.selected_bad_state_ids,
        selected_success_state_ids=(),
        policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
        require_global=True,
    )
    unselected_deadlock_certificate = certify_absorption_domain(
        unselected_deadlock,
        deadlock_graph,
        {},
        selected_bad_state_ids=unselected_deadlock.selected_bad_state_ids,
        selected_success_state_ids=(),
        policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
        require_global=False,
    )

    assert base.positive_rate_graph_hash != detour.positive_rate_graph_hash
    assert base.absorption_domain_hash != detour.absorption_domain_hash
    assert base.positive_rate_graph_hash == changed_rates.positive_rate_graph_hash
    assert base.rate_manifest_hash != changed_rates.rate_manifest_hash
    assert base.absorption_domain_hash == changed_rates.absorption_domain_hash
    assert partition.with_absorption_domain_certificate(base).estimand_id != (
        changed_rate_partition.with_absorption_domain_certificate(
            changed_rates
        ).estimand_id
    )
    assert selected_deadlock.partition_hash == unselected_deadlock.partition_hash
    assert selected_deadlock_certificate.absorption_domain_hash != (
        unselected_deadlock_certificate.absorption_domain_hash
    )
    assert (
        selected_deadlock.with_absorption_domain_certificate(
            selected_deadlock_certificate
        ).estimand_id
        != unselected_deadlock.with_absorption_domain_certificate(
            unselected_deadlock_certificate
        ).estimand_id
    )


def test_attached_certificate_marks_positive_rate_reachability_verified() -> None:
    graph, transitions, start_state_id, finish_state_id = _simple_finish_fixture()
    partition = partition_stable_lts(
        IMSModel(id="simple-finish", resources={}, jobs=("j1",)),
        graph,
        transitions,
        event_rates={"finish": 1.0},
        verify_generated_lts=True,
    )
    certificate = certify_absorption_domain(
        partition,
        graph,
        {"finish": 1.0},
        selected_bad_state_ids=(),
        selected_success_state_ids=(finish_state_id,),
        policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
        require_global=True,
    )

    attached = partition.with_absorption_domain_certificate(certificate)
    payload = attached.to_json_dict()
    hashes = cast(dict[str, object], payload["hashes"])
    derived_state_sets = cast(dict[str, object], payload["derived_state_sets"])
    s_reach = cast(dict[str, object], derived_state_sets["S_reach"])

    assert partition.estimand_id is None
    assert attached.estimand_id is not None
    assert attached.absorption_domain_certificate == certificate
    assert attached.positive_rate_graph_hash == certificate.positive_rate_graph_hash
    assert attached.policy_filter_hash == certificate.policy_filter_hash
    assert attached.absorption_domain_hash == certificate.absorption_domain_hash
    assert hashes["estimand_id"] == attached.estimand_id
    assert s_reach["positive_rate_verified"] is True
    assert derived_state_sets["S_T"] == {
        "state_ids": [start_state_id],
        "certification_status": CERTIFIED_STATUS,
        "reason_codes": [],
    }
    with pytest.raises(TerminalPartitionError) as excinfo:
        partition.with_absorption_domain_certificate(
            partition.absorption_domain_certificate
        )
    assert excinfo.value.code == "uncertified_absorption_domain_certificate"


@pytest.mark.parametrize(
    ("field_name", "forged_value"),
    [
        ("s_t_state_ids", ("forged",)),
        ("closed_class_reverse_basin_state_ids", ("forged",)),
        ("unselected_closed_sccs", (("forged",),)),
        ("policy_filter_hash", "forged-policy-hash"),
        ("positive_rate_graph_hash", "forged-positive-graph-hash"),
        ("absorption_domain_hash", "forged-absorption-domain-hash"),
    ],
)
def test_attachment_rejects_forged_certificate_derived_fields(
    field_name: str,
    forged_value: object,
) -> None:
    partition, certificate, _graph, _finish_state_id = (
        _simple_certified_partition_and_certificate()
    )

    assert partition.with_absorption_domain_certificate(certificate).estimand_id
    with pytest.raises(TerminalPartitionError) as excinfo:
        partition.with_absorption_domain_certificate(
            replace(certificate, **cast(Any, {field_name: forged_value}))
        )

    assert excinfo.value.code == "absorption_certificate_identity_mismatch"
    assert partition.estimand_id is None


def test_attachment_rejects_verified_certificate_on_unverified_partition() -> None:
    verified_partition, certificate, graph, _finish_state_id = (
        _simple_certified_partition_and_certificate()
    )
    unverified_partition = partition_stable_lts(
        IMSModel(id="simple-finish", resources={}, jobs=("j1",)),
        graph,
        (_finish_event(source_mode="start"),),
        event_rates={"finish": 1.0},
        verify_generated_lts=False,
    )

    assert verified_partition.partition_hash == unverified_partition.partition_hash
    with pytest.raises(TerminalPartitionError) as excinfo:
        unverified_partition.with_absorption_domain_certificate(certificate)

    assert excinfo.value.code == "unverified_lts_provenance"


class _StringLikeStateId:
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value


@pytest.mark.parametrize("bad_id", [True, 1, _StringLikeStateId("s1")])
def test_certifier_rejects_non_string_selected_success_ids(bad_id: object) -> None:
    partition, _certificate, graph, _finish_state_id = (
        _simple_certified_partition_and_certificate()
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        certify_absorption_domain(
            partition,
            graph,
            {"finish": 1.0},
            selected_bad_state_ids=(),
            selected_success_state_ids=cast(tuple[str, ...], (bad_id,)),
            policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
            require_global=True,
        )

    assert excinfo.value.code == "invalid_selected_state_id"


@pytest.mark.parametrize("bad_id", [False, 1, _StringLikeStateId("s0")])
def test_certifier_rejects_non_string_selected_bad_ids(bad_id: object) -> None:
    graph, transitions = _generated_global_deadlock_fixture()
    model = IMSModel(
        id="generated-global-deadlock",
        resources={"r1": Resource("r1", 1), "r2": Resource("r2", 1)},
        jobs=("j1", "j2"),
    )
    partition = partition_stable_lts(
        model,
        graph,
        transitions,
        event_rates={},
        estimand_spec=VersionedEstimandSpec(selected_bad_classes=("D_global",)),
        verify_generated_lts=True,
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        certify_absorption_domain(
            partition,
            graph,
            {},
            selected_bad_state_ids=cast(tuple[str, ...], (bad_id,)),
            selected_success_state_ids=(),
            policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
            require_global=True,
        )

    assert excinfo.value.code == "invalid_selected_state_id"


class _StringLikeEventName:
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value


@pytest.mark.parametrize("bad_event", [True, 1, _StringLikeEventName("finish")])
def test_partition_rejects_non_string_rate_manifest_keys(bad_event: object) -> None:
    graph, transitions, _start_state_id, _finish_state_id = _simple_finish_fixture()

    with pytest.raises(TerminalPartitionError) as excinfo:
        partition_stable_lts(
            IMSModel(id="simple-finish", resources={}, jobs=("j1",)),
            graph,
            transitions,
            event_rates=cast(dict[str, float], {bad_event: 1.0}),
            verify_generated_lts=True,
        )

    assert excinfo.value.code == "invalid_event_rate_identity"


@pytest.mark.parametrize("bad_event", [True, 1, _StringLikeEventName("finish")])
def test_certifier_rejects_non_string_rate_manifest_keys(bad_event: object) -> None:
    partition, _certificate, graph, finish_state_id = (
        _simple_certified_partition_and_certificate()
    )

    with pytest.raises(TerminalPartitionError) as excinfo:
        certify_absorption_domain(
            partition,
            graph,
            cast(dict[str, float], {bad_event: 1.0}),
            selected_bad_state_ids=(),
            selected_success_state_ids=(finish_state_id,),
            policy_filter_declaration=NO_POLICY_FILTER_DECLARATION,
            require_global=True,
        )

    assert excinfo.value.code == "invalid_event_rate_identity"


def test_no_policy_filter_declaration_factory_returns_fresh_canonical_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = canonical_no_policy_filter_declaration()
    second = canonical_no_policy_filter_declaration()
    expected = {
        "version": "ims-deadlock/g6-policy-filter-declaration/v1",
        "mode": "no_policy_filter",
        "excluded_plant_arcs": [],
    }

    assert first == expected
    assert second == expected
    assert first is not second
    assert first["excluded_plant_arcs"] is not second["excluded_plant_arcs"]

    cast(list[object], first["excluded_plant_arcs"]).append(["s0", "finish", "s1"])
    first["mode"] = "mutated"
    monkeypatch.setitem(NO_POLICY_FILTER_DECLARATION, "mode", "legacy_mutated")
    legacy_excluded = cast(
        list[object], NO_POLICY_FILTER_DECLARATION["excluded_plant_arcs"]
    )
    legacy_excluded.append(["legacy", "arc", "mutation"])

    later = canonical_no_policy_filter_declaration()
    assert second == expected
    assert later == expected
    assert later is not first
    assert later is not second
    assert later["excluded_plant_arcs"] is not first["excluded_plant_arcs"]
    assert later["excluded_plant_arcs"] is not second["excluded_plant_arcs"]

    partition, certificate, graph, finish_state_id = (
        _simple_certified_partition_and_certificate()
    )
    recertified = certify_absorption_domain(
        partition,
        graph,
        {"finish": 1.0},
        selected_bad_state_ids=(),
        selected_success_state_ids=(finish_state_id,),
        policy_filter_declaration=canonical_no_policy_filter_declaration(),
        require_global=True,
    )

    assert recertified.policy_filter_hash == certificate.policy_filter_hash


def test_policy_hash_ignores_mutated_public_no_policy_dict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    partition, certificate, graph, finish_state_id = (
        _simple_certified_partition_and_certificate()
    )
    canonical_policy = {
        "version": "ims-deadlock/g6-policy-filter-declaration/v1",
        "mode": "no_policy_filter",
        "excluded_plant_arcs": [],
    }

    monkeypatch.setitem(NO_POLICY_FILTER_DECLARATION, "mode", "mutated")
    excluded = cast(list[object], NO_POLICY_FILTER_DECLARATION["excluded_plant_arcs"])
    excluded.append(["s0", "finish", "s1"])

    recertified = certify_absorption_domain(
        partition,
        graph,
        {"finish": 1.0},
        selected_bad_state_ids=(),
        selected_success_state_ids=(finish_state_id,),
        policy_filter_declaration=canonical_policy,
        require_global=True,
    )

    assert recertified.policy_filter_hash == certificate.policy_filter_hash
