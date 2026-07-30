from dataclasses import replace
from typing import cast

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
    DEFAULT_ESTIMAND_SPEC,
    TerminalPartitionError,
    VersionedEstimandSpec,
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

    with pytest.raises(ValueError, match="plant_policy_class must be P_policy"):
        VersionedEstimandSpec(plant_policy_class="custom_policy")


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

    base = partition_stable_lts(
        model,
        graph,
        (),
        event_rates={"finish": 1.0},
        estimand_spec=DEFAULT_ESTIMAND_SPEC,
    )
    rate_drift = partition_stable_lts(
        model,
        graph,
        (),
        event_rates={"finish": 2.0},
        estimand_spec=DEFAULT_ESTIMAND_SPEC,
    )
    rule_drift = partition_stable_lts(
        model,
        graph,
        (),
        event_rates={"finish": 1.0},
        estimand_spec=VersionedEstimandSpec(selected_bad_classes=("D_global",)),
    )
    stopping_drift = partition_stable_lts(
        model,
        graph,
        (),
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
            (),
            event_rates={"finish": 1.0},
            estimand_spec=DEFAULT_ESTIMAND_SPEC,
        ).partition_hash
    )
    assert base.rate_manifest_hash != rate_drift.rate_manifest_hash
    assert base.estimand_id != rate_drift.estimand_id
    assert base.stopping_rule_hash != stopping_drift.stopping_rule_hash
    assert base.des_stopping_rule_hash != stopping_drift.des_stopping_rule_hash
    assert base.estimand_id != rule_drift.estimand_id
    assert base.estimand_id != stopping_drift.estimand_id


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
    classes = cast(dict[str, object], payload["classes"])

    assert partition.transient_state_ids == ("s0", "s2")
    assert partition.selected_reachable_state_ids == ("s0",)
    assert classes["S_T"] == ["s0"]

    with pytest.raises(TerminalPartitionError) as excinfo:
        partition_stable_lts(
            model,
            graph,
            (_event("finish"),),
            require_selected_absorption=True,
        )
    assert excinfo.value.code == "unreachable_nonabsorbing_state"
    assert excinfo.value.details["unreachable_state_ids"] == ["s2"]
    assert excinfo.value.details["terminal_scc_state_ids"] == ["s2"]


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
    assert both.estimand_id != global_only.estimand_id


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
