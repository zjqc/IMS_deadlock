"""T-ASE hardening panel: identity, workers, H1–H4 builders. No CTMC/DES."""

from __future__ import annotations

import json
import os
import time
from collections.abc import Callable, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Any, Literal

from ims_deadlock.analysis import enumerate_stable_lts
from ims_deadlock.baselines import state_dependent_knot_screen
from ims_deadlock.cases import CASE_SCHEMA_VERSION, CaseSpec
from ims_deadlock.certificates import (
    find_deadlock_certificate,
    find_local_blocking_certificate,
)
from ims_deadlock.engine import EventKind, TransitionSpec, zero_time_closure
from ims_deadlock.families import BIX2Parameters, build_bix2_persist_instance
from ims_deadlock.model import (
    DeadlockCertificate,
    Holding,
    IMSModel,
    IMSState,
    RequestAlternative,
    Resource,
    ResourceDemand,
)
from ims_deadlock.petri import build_wait_snapshot_bridge

SCOPE_ID = "tase_hardening_v1"
ARTICLE_CORE_SCOPE_LOCK_SHA256 = (
    "86ec7b80c888c7758d326a9de7793b0f0f65f4740ecf0303e1b17d2d14344660"
)
H2_TYPES = (
    "residual_cycle",
    "unit_deadlock",
    "multi_capacity_residual",
    "agv_required",
    "sip1_positive",
    "siphon_refusal_outside_sip1",
    "local_with_bypass",
    "global_with_local_looking_core",
)
H2_CELLS = ("tight", "one-below", "balanced", "loose")
H3_STATE_CAP = 100_000
H3_TIME_CAP_S = 300
H1_IDS = (
    "H1_CE_CL1_nonconfluent_closure",
    "H1_CE_BIXD2_optional_drain",
    "H1_CE_INT1_new_core_after_cut",
    "H1_P3_nonchain_refuse",
)


class IdentityCollision(ValueError):
    """A designed subject reused a frozen identity hash."""


class QuantitativeExecutionRefused(RuntimeError):
    """CTMC/DES is not authorized on this tranche."""


class WorkerProtocolError(RuntimeError):
    """Parallel-wave contract violated."""


@dataclass(frozen=True)
class ComputeProbe:
    """Live CPU/RAM snapshot used to size a wave."""

    logical_cpus: int
    free_ram_gib: float
    other_python_jobs: int = 0


@dataclass(frozen=True)
class H2Plant:
    """One same-semantics baseline plant."""

    type_id: str
    cell: str
    model: IMSModel
    initial_state: IMSState
    transitions: tuple[TransitionSpec, ...]


@dataclass(frozen=True)
class H4Island:
    """Synthetic two-cell island, base or intervention."""

    role: Literal["base", "intervention"]
    label: str
    model: IMSModel
    initial_state: IMSState
    transitions: tuple[TransitionSpec, ...]
    intervention: str


def pool_square(value: int) -> int:
    """Picklable helper used by the process-pool unit test."""

    return value * value


def authorization_flags() -> dict[str, bool]:
    """Return the five spec flags. All stay false in this tranche."""

    return {
        "case_construction_authorized": False,
        "overlap_audit_authorized": False,
        "target_certification_preflight_authorized": False,
        "quantitative_execution_authorized": False,
        "theory_revision_authorized": False,
    }


def reject_forbidden_identity(digest: str) -> None:
    """Refuse article-core v1 and other frozen identity hashes."""

    if digest == ARTICLE_CORE_SCOPE_LOCK_SHA256:
        raise IdentityCollision("article-core v1 scope lock must not be reused")


def refuse_quantitative_execution() -> None:
    """Hard stop for CTMC/DES until a later hashed authorization exists."""

    if not authorization_flags()["quantitative_execution_authorized"]:
        raise QuantitativeExecutionRefused(
            "quantitative_execution_authorized is false for tase_hardening_v1"
        )


def plan_workers(probe: ComputeProbe, *, family: str) -> int:
    """Section 12 worker formula."""

    del family
    if probe.free_ram_gib < 16:
        return 4
    reserve = 8
    max_workers = max(4, min(48, probe.logical_cpus - reserve))
    if probe.free_ram_gib < 32:
        max_workers = min(max_workers, 16)
    if probe.logical_cpus >= 56 and probe.free_ram_gib >= 64:
        desired = 48
    elif probe.logical_cpus >= 56:
        desired = 32
    else:
        desired = max_workers
    return max(4, min(max_workers, desired))


def pin_blas_thread_env(*, workers: int) -> dict[str, str]:
    """Pin BLAS/OpenMP threads when the process pool is wide."""

    if workers < 8:
        return {}
    env = {
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
    }
    os.environ.update(env)
    return env


def validate_wave(
    *,
    wave: str,
    workers: int,
    probe: ComputeProbe,
    primary_repro_overlap: bool,
    reducer_count: int,
) -> None:
    """Refuse illegal waves before any shard is launched."""

    del wave
    if primary_repro_overlap:
        raise WorkerProtocolError("primary and repro of one case must not overlap")
    if reducer_count != 1:
        raise WorkerProtocolError("exactly one reducer may write the manifest")
    if (
        workers == 1
        and probe.logical_cpus >= 16
        and probe.free_ram_gib >= 32
        and probe.other_python_jobs == 0
    ):
        raise WorkerProtocolError(
            "serial scientific launch refused on a 16+ CPU / 32+ GiB probe"
        )


def build_shard_plan(
    units: Sequence[str], *, workers: int
) -> tuple[tuple[str, ...], ...]:
    """Split units into contiguous disjoint shards."""

    if workers < 1:
        raise WorkerProtocolError("workers must be positive")
    shards: list[list[str]] = [[] for _ in range(min(workers, len(units) or 1))]
    for index, unit in enumerate(units):
        shards[index % len(shards)].append(unit)
    return tuple(tuple(shard) for shard in shards if shard)


def run_process_pool(
    units: Sequence[Any],
    fn: Callable[[Any], Any],
    *,
    workers: int,
) -> list[Any]:
    """Run independent units in a process pool."""

    if workers < 1:
        raise WorkerProtocolError("workers must be positive")
    pin_blas_thread_env(workers=workers)
    if workers == 1 or len(units) <= 1:
        return [fn(unit) for unit in units]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(fn, units))


def reduce_shards(
    shard_dir: Path, *, expected_ids: Sequence[str]
) -> list[dict[str, Any]]:
    """Read a complete shard directory or refuse a partial wave."""

    found: dict[str, dict[str, Any]] = {}
    for path in sorted(shard_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        found[str(payload["id"])] = payload
    missing = [unit for unit in expected_ids if unit not in found]
    if missing:
        raise WorkerProtocolError(f"incomplete shards: {missing!r}")
    return [found[unit] for unit in expected_ids]


def _alt(*resource_ids: str) -> RequestAlternative:
    return RequestAlternative(tuple(ResourceDemand(item) for item in resource_ids))


def _hold(job: str, resource: str, units: int = 1) -> Holding:
    return Holding(job, resource, units)


def build_h1_cases() -> dict[str, CaseSpec]:
    """Return the four H1 logical witnesses."""

    return {
        "H1_CE_CL1_nonconfluent_closure": _h1_cl1(),
        "H1_CE_BIXD2_optional_drain": _h1_bixd2(),
        "H1_CE_INT1_new_core_after_cut": _h1_int1_original(),
        "H1_P3_nonchain_refuse": _h1_p3(),
    }


def evaluate_h1(case_id: str) -> dict[str, Any]:
    """Evaluate one H1 witness against its expected machine outcome."""

    if case_id == "H1_CE_CL1_nonconfluent_closure":
        spec = _h1_cl1()
        closure = zero_time_closure(spec.model, spec.initial_state, spec.transitions)
        count = len(closure.stable_states)
        return {
            "outcome": "refuse_deterministic_kappa" if count > 1 else "unexpected",
            "stable_successor_count": count,
        }
    if case_id == "H1_CE_BIXD2_optional_drain":
        spec = _h1_bixd2()
        lts = enumerate_stable_lts(
            spec.model, spec.initial_state, spec.transitions, max_states=4096
        )
        saturation = any(
            record.state.mode_by_job.get("A1") == "a_blocked_for_D"
            and record.state.mode_by_job.get("B1") == "b_blocked_for_Q"
            and record.state.mode_by_job.get("C1") == "c_blocked_for_M"
            for record in lts.states
        )
        drain_names = {transition.name for transition in spec.transitions}
        return {
            "optional_drain_present": any(
                "optional-drain" in name for name in drain_names
            ),
            "ring_deadlock_reachable": saturation,
            "structural_deadlock_free": not saturation,
        }
    if case_id == "H1_CE_INT1_new_core_after_cut":
        original = _h1_int1_original()
        intervened = _h1_int1_intervened()
        original_cert = find_local_blocking_certificate(
            original.model, original.initial_state, original.transitions
        )
        intervened_cert = find_local_blocking_certificate(
            intervened.model, intervened.initial_state, intervened.transitions
        )
        original_kernel = (
            tuple(sorted(original_cert.kernel_resources)) if original_cert else ()
        )
        intervened_kernel = (
            tuple(sorted(intervened_cert.kernel_resources)) if intervened_cert else ()
        )
        return {
            "original_kernel": original_kernel,
            "intervened_kernel": intervened_kernel,
        }
    if case_id == "H1_P3_nonchain_refuse":
        spec = _h1_p3()
        certificate = find_deadlock_certificate(
            spec.model, spec.initial_state, spec.transitions
        )
        chain = False
        if certificate is not None:
            chain = _is_chain_decomposable(spec.model, spec.initial_state, certificate)
        return {
            "has_covering_kernel": certificate is not None,
            "chain_decomposable": chain,
            "p3_verdict": (
                "not_applicable"
                if certificate is not None and not chain
                else "unexpected"
            ),
        }
    raise KeyError(case_id)


def _h1_cl1() -> CaseSpec:
    model = IMSModel(
        id="h1-cl1-nonconfluent",
        resources={"slot": Resource("slot", 1, "buffer")},
        jobs=("j1", "j2"),
    )
    state = IMSState(
        id="h1-cl1-race",
        holds=(),
        requests={"j1": (_alt("slot"),), "j2": (_alt("slot"),)},
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"j1": "idle", "j2": "idle"},
        stage_by_job={"j1": "idle", "j2": "idle"},
    )
    transitions = (
        TransitionSpec(
            name="claim-slot-j1",
            kind=EventKind.DISPATCH,
            job_id="j1",
            source_mode="idle",
            target_mode="holding",
            controllable=False,
            zero_time=True,
            urgent=True,
            acquire=(ResourceDemand("slot", 1),),
            clears_requests=True,
        ),
        TransitionSpec(
            name="claim-slot-j2",
            kind=EventKind.DISPATCH,
            job_id="j2",
            source_mode="idle",
            target_mode="holding",
            controllable=False,
            zero_time=True,
            urgent=True,
            acquire=(ResourceDemand("slot", 1),),
            clears_requests=True,
        ),
    )
    return _spec(
        "H1_CE_CL1_nonconfluent_closure",
        "CE-CL1 nonconfluent closure",
        model,
        state,
        transitions,
    )


def _h1_bixd2() -> CaseSpec:
    instance = build_bix2_persist_instance(BIX2Parameters(1, 1, 1, 1, 1, 1, "ring"))
    drain = TransitionSpec(
        name="C1-optional-drain",
        kind=EventKind.RELEASE,
        job_id="C1",
        source_mode="c_blocked_for_M",
        target_mode="completed",
        controllable=True,
        zero_time=False,
        clears_requests=True,
        release=(ResourceDemand("Q", 1),),
        mark_complete=True,
    )
    return _spec(
        "H1_CE_BIXD2_optional_drain",
        "CE-BIXD2 optional drain is not structural repair",
        instance.model,
        instance.initial_state,
        instance.transitions + (drain,),
    )


def _h1_int1_original() -> CaseSpec:
    model = IMSModel(
        id="h1-int1-original",
        resources={
            "a": Resource("a", 1),
            "b": Resource("b", 1),
            "c": Resource("c", 1),
        },
        jobs=("j1", "j2", "j3"),
    )
    state = IMSState(
        id="h1-int1-k1",
        holds=(_hold("j1", "a"), _hold("j2", "b"), _hold("j3", "c")),
        requests={"j1": (_alt("b"),), "j2": (_alt("a"),), "j3": ()},
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"j1": "wait", "j2": "wait", "j3": "hold"},
        stage_by_job={"j1": "wait", "j2": "wait", "j3": "hold"},
    )
    transitions = (
        TransitionSpec(
            name="j2-acquire-a",
            kind=EventKind.DISPATCH,
            job_id="j2",
            source_mode="wait",
            target_mode="done",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("a", 1),),
            release=(ResourceDemand("b", 1),),
            clears_requests=True,
            mark_complete=True,
        ),
        TransitionSpec(
            name="j1-acquire-b",
            kind=EventKind.DISPATCH,
            job_id="j1",
            source_mode="wait",
            target_mode="done",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("b", 1),),
            release=(ResourceDemand("a", 1),),
            clears_requests=True,
            mark_complete=True,
        ),
    )
    return _spec(
        "H1_CE_INT1_new_core_after_cut",
        "CE-INT1 original kernel",
        model,
        state,
        transitions,
    )


def _h1_int1_intervened() -> CaseSpec:
    original = _h1_int1_original()
    state = IMSState(
        id="h1-int1-k2",
        holds=original.initial_state.holds,
        requests={"j1": (_alt("b"),), "j2": (_alt("c"),), "j3": (_alt("b"),)},
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"j1": "wait", "j2": "wait", "j3": "wait"},
        stage_by_job={"j1": "wait", "j2": "wait", "j3": "wait"},
    )
    transitions = (
        TransitionSpec(
            name="j2-acquire-c",
            kind=EventKind.DISPATCH,
            job_id="j2",
            source_mode="wait",
            target_mode="done",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("c", 1),),
            release=(ResourceDemand("b", 1),),
            clears_requests=True,
            mark_complete=True,
        ),
        TransitionSpec(
            name="j3-acquire-b",
            kind=EventKind.DISPATCH,
            job_id="j3",
            source_mode="wait",
            target_mode="done",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("b", 1),),
            release=(ResourceDemand("c", 1),),
            clears_requests=True,
            mark_complete=True,
        ),
        TransitionSpec(
            name="j1-acquire-b",
            kind=EventKind.DISPATCH,
            job_id="j1",
            source_mode="wait",
            target_mode="done",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("b", 1),),
            release=(ResourceDemand("a", 1),),
            clears_requests=True,
            mark_complete=True,
        ),
    )
    return _spec(
        "H1_CE_INT1_intervened",
        "CE-INT1 new kernel after cut",
        original.model,
        state,
        transitions,
    )


def _h1_p3() -> CaseSpec:
    model = IMSModel(
        id="h1-p3-nonchain",
        resources={"R": Resource("R", 2, "buffer")},
        jobs=("j1", "j2"),
    )
    state = IMSState(
        id="h1-p3-pool",
        holds=(_hold("j1", "R"), _hold("j2", "R")),
        requests={"j1": (_alt_units("R", 2),), "j2": (_alt_units("R", 2),)},
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"j1": "wait", "j2": "wait"},
        stage_by_job={"j1": "wait", "j2": "wait"},
    )
    transitions = (
        TransitionSpec(
            name="j1-need-two",
            kind=EventKind.DISPATCH,
            job_id="j1",
            source_mode="wait",
            target_mode="done",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("R", 2),),
            clears_requests=True,
            mark_complete=True,
        ),
        TransitionSpec(
            name="j2-need-two",
            kind=EventKind.DISPATCH,
            job_id="j2",
            source_mode="wait",
            target_mode="done",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("R", 2),),
            clears_requests=True,
            mark_complete=True,
        ),
    )
    return _spec(
        "H1_P3_nonchain_refuse",
        "P3 non-chain-decomposable covering kernel",
        model,
        state,
        transitions,
    )


def _alt_units(resource_id: str, units: int) -> RequestAlternative:
    return RequestAlternative((ResourceDemand(resource_id, units),))


def _is_chain_decomposable(
    model: IMSModel,
    state: IMSState,
    certificate: DeadlockCertificate,
) -> bool:
    """True only if every witness holder has a strictly next resource."""

    del model
    if not certificate.capacity_witnesses:
        return False
    for witness in certificate.capacity_witnesses:
        if not witness.holders:
            return False
        holder = witness.holders[0]
        nxt = {
            demand.resource_id
            for alternative in state.requests.get(holder, ())
            for demand in alternative.demands
            if demand.resource_id in certificate.kernel_resources
        }
        nxt.discard(witness.resource_id)
        if not nxt:
            return False
    return True


def build_h2_plants() -> tuple[H2Plant, ...]:
    """Eight semantic types times four capacity cells."""

    plants: list[H2Plant] = []
    for type_id, cell in product(H2_TYPES, H2_CELLS):
        model, state, transitions = _h2_payload(type_id, cell)
        plants.append(
            H2Plant(
                type_id=type_id,
                cell=cell,
                model=model,
                initial_state=state,
                transitions=transitions,
            )
        )
    return tuple(plants)


def evaluate_h2_plant(plant: H2Plant) -> dict[str, Any]:
    """Run four methods on one plant against LTS truth."""

    started = time.perf_counter()
    lts = enumerate_stable_lts(
        plant.model,
        plant.initial_state,
        plant.transitions,
        max_states=4096,
    )
    truth_deadlock = False
    if not lts.truncated:
        for record in lts.states:
            cert = find_deadlock_certificate(
                plant.model, record.state, plant.transitions
            )
            if cert is not None:
                truth_deadlock = True
                break
    knot = state_dependent_knot_screen(plant.model, plant.initial_state)
    cycle_pos = bool(
        knot.get("has_terminal_cyclic_scc") or knot.get("has_capacity_closed_knot")
    )
    core = find_deadlock_certificate(
        plant.model, plant.initial_state, plant.transitions
    )
    siphon_refusal = 0
    if core is None:
        siphon_refusal = 1
        siphon_pos = False
    else:
        bridge = build_wait_snapshot_bridge(plant.model, plant.initial_state, core)
        siphon_pos = bridge.exact
        if not bridge.applicable:
            siphon_refusal = 1
    core_pos = core is not None
    methods = {
        "machine_cycle_scc": cycle_pos,
        "closed_core": core_pos,
        "sip1_or_refuse": siphon_pos,
        "lts_truth": truth_deadlock and not lts.truncated,
    }
    false_positive = int(core_pos and not methods["lts_truth"] and not lts.truncated)
    false_negative = int(methods["lts_truth"] and not core_pos)
    return {
        "methods": methods,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "refusal_count": siphon_refusal + int(lts.truncated),
        "certificate_size": 0 if core is None else len(core.kernel_jobs),
        "runtime_s": time.perf_counter() - started,
        "peak_state_count": len(lts.states),
        "type_id": plant.type_id,
        "cell": plant.cell,
    }


def _cell_capacity(cell: str, tight: int) -> int:
    return {
        "tight": tight,
        "one-below": tight + 1,
        "balanced": max(tight, 2),
        "loose": max(tight + 2, 3),
    }[cell]


def _h2_payload(
    type_id: str, cell: str
) -> tuple[IMSModel, IMSState, tuple[TransitionSpec, ...]]:
    cap = _cell_capacity(cell, 1)
    mutex_types = {
        "unit_deadlock",
        "sip1_positive",
        "residual_cycle",
        "multi_capacity_residual",
    }
    if type_id in mutex_types:
        if type_id in {"unit_deadlock", "sip1_positive"}:
            r2_cap = 1
        else:
            r2_cap = cap + 1
        if type_id == "residual_cycle":
            r2_cap = max(cap, 2)
        if type_id == "multi_capacity_residual":
            r2_cap = max(cap, 2)
        model = IMSModel(
            id=f"h2-{type_id}-{cell}",
            resources={
                "r1": Resource(
                    "r1", 1 if type_id != "multi_capacity_residual" else cap
                ),
                "r2": Resource("r2", r2_cap),
            },
            jobs=("j1", "j2"),
        )
        holds: tuple[Holding, ...] = (_hold("j1", "r1"), _hold("j2", "r2"))
        if type_id == "multi_capacity_residual":
            holds = (_hold("j1", "r1"),)
        state = IMSState(
            id=f"h2-{type_id}-{cell}-s0",
            holds=holds,
            requests={"j1": (_alt("r2"),), "j2": (_alt("r1"),)},
            stable=True,
            complete=False,
            event_calendar_empty=True,
            mode_by_job={"j1": "wait", "j2": "wait"},
            stage_by_job={"j1": "wait", "j2": "wait"},
        )
        transitions = _mutex_pair_transitions()
        return model, state, transitions
    if type_id in {"agv_required", "siphon_refusal_outside_sip1"}:
        model = IMSModel(
            id=f"h2-{type_id}-{cell}",
            resources={
                "m1": Resource("m1", 1, "machine"),
                "buf": Resource("buf", cap, "buffer"),
                "agv": Resource("agv", 1, "agv"),
            },
            jobs=("pA", "pB"),
        )
        state = IMSState(
            id=f"h2-{type_id}-{cell}-s0",
            holds=(_hold("pA", "m1"), _hold("pB", "agv")),
            requests={
                "pA": (_alt("agv", "buf"),),
                "pB": (_alt("m1"),),
            },
            stable=True,
            complete=False,
            event_calendar_empty=True,
            mode_by_job={"pA": "blocked_unload", "pB": "wait"},
            stage_by_job={"pA": "blocked_unload", "pB": "wait"},
        )
        transitions = (
            TransitionSpec(
                name="pA-handoff",
                kind=EventKind.UNLOAD,
                job_id="pA",
                source_mode="blocked_unload",
                target_mode="done",
                controllable=True,
                zero_time=False,
                acquire=(ResourceDemand("agv"), ResourceDemand("buf")),
                release=(ResourceDemand("m1"),),
                clears_requests=True,
                mark_complete=True,
            ),
            TransitionSpec(
                name="pB-enter",
                kind=EventKind.DISPATCH,
                job_id="pB",
                source_mode="wait",
                target_mode="done",
                controllable=True,
                zero_time=False,
                acquire=(ResourceDemand("m1"),),
                release=(ResourceDemand("agv"),),
                clears_requests=True,
                mark_complete=True,
            ),
        )
        return model, state, transitions
    if type_id == "local_with_bypass":
        return _bypass_payload(cell)
    return _global_local_payload(cell)


def _mutex_pair_transitions() -> tuple[TransitionSpec, ...]:
    return (
        TransitionSpec(
            name="j1-get-r2",
            kind=EventKind.DISPATCH,
            job_id="j1",
            source_mode="wait",
            target_mode="done",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("r2"),),
            release=(ResourceDemand("r1"),),
            clears_requests=True,
            mark_complete=True,
        ),
        TransitionSpec(
            name="j2-get-r1",
            kind=EventKind.DISPATCH,
            job_id="j2",
            source_mode="wait",
            target_mode="done",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("r1"),),
            release=(ResourceDemand("r2"),),
            clears_requests=True,
            mark_complete=True,
        ),
    )


def _bypass_payload(cell: str) -> tuple[IMSModel, IMSState, tuple[TransitionSpec, ...]]:
    model = IMSModel(
        id=f"h2-bypass-{cell}",
        resources={
            "r1": Resource("r1", 1),
            "r2": Resource("r2", 1),
            "r3": Resource("r3", 1),
        },
        jobs=("j1", "j2", "j3"),
    )
    state = IMSState(
        id=f"h2-bypass-{cell}-s0",
        holds=(_hold("j1", "r1"), _hold("j2", "r2"), _hold("j3", "r3")),
        requests={"j1": (_alt("r2"),), "j2": (_alt("r1"),), "j3": ()},
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"j1": "wait", "j2": "wait", "j3": "hold"},
        stage_by_job={"j1": "wait", "j2": "wait", "j3": "hold"},
    )
    transitions = (
        TransitionSpec(
            name="j3-release",
            kind=EventKind.RELEASE,
            job_id="j3",
            source_mode="hold",
            target_mode="completed",
            controllable=True,
            zero_time=False,
            release=(ResourceDemand("r3"),),
            mark_complete=True,
        ),
        TransitionSpec(
            name="j1-bypass-on-r3",
            kind=EventKind.DISPATCH,
            job_id="j1",
            source_mode="wait",
            target_mode="done",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("r3"),),
            release=(ResourceDemand("r1"),),
            clears_requests=True,
            mark_complete=True,
        ),
        TransitionSpec(
            name="j2-finish-on-r1",
            kind=EventKind.DISPATCH,
            job_id="j2",
            source_mode="wait",
            target_mode="done",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("r1"),),
            release=(ResourceDemand("r2"),),
            clears_requests=True,
            mark_complete=True,
        ),
        *_mutex_pair_transitions(),
    )
    return model, state, transitions


def _global_local_payload(
    cell: str,
) -> tuple[IMSModel, IMSState, tuple[TransitionSpec, ...]]:
    model = IMSModel(
        id=f"h2-global-local-{cell}",
        resources={
            "r1": Resource("r1", 1),
            "r2": Resource("r2", 1),
            "r3": Resource("r3", 1),
        },
        jobs=("j1", "j2", "j3"),
    )
    state = IMSState(
        id=f"h2-global-local-{cell}-s0",
        holds=(_hold("j1", "r1"), _hold("j2", "r2"), _hold("j3", "r3")),
        requests={"j1": (_alt("r2"),), "j2": (_alt("r1"),), "j3": (_alt("r1"),)},
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"j1": "wait", "j2": "wait", "j3": "wait"},
        stage_by_job={"j1": "wait", "j2": "wait", "j3": "wait"},
    )
    transitions = (
        *_mutex_pair_transitions(),
        TransitionSpec(
            name="j3-get-r1",
            kind=EventKind.DISPATCH,
            job_id="j3",
            source_mode="wait",
            target_mode="done",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("r1"),),
            release=(ResourceDemand("r3"),),
            clears_requests=True,
            mark_complete=True,
        ),
    )
    return model, state, transitions


def build_h3_rows() -> tuple[dict[str, int | bool], ...]:
    """Axis product for the scale family. 576 independent rows."""

    jobs = (2, 3, 4, 6)
    resources = (2, 3, 4)
    capacities = (1, 2)
    alternatives = (1, 2)
    kernels = (0, 1, 2)
    bypasses = (False, True)
    transports = (False, True)
    rows = []
    axes = product(
        jobs, resources, capacities, alternatives, kernels, bypasses, transports
    )
    for item in axes:
        rows.append(
            {
                "n_jobs": item[0],
                "n_resources": item[1],
                "capacity": item[2],
                "n_alternatives": item[3],
                "kernel_count": item[4],
                "bypass": item[5],
                "transport": item[6],
            }
        )
    return tuple(rows)


def classify_h3_row(row: dict[str, Any]) -> str:
    """Refuse truncated or overtime H3 rows."""

    if int(row.get("state_count", 0)) > H3_STATE_CAP:
        return "refused"
    if float(row.get("elapsed_s", 0.0)) > H3_TIME_CAP_S:
        return "refused"
    return "enumerated"


def build_h4_islands() -> tuple[H4Island, ...]:
    """Base island plus one predeclared backflow deletion."""

    return (_h4_island("base"), _h4_island("intervention"))


def _h4_island(role: Literal["base", "intervention"]) -> H4Island:
    model = IMSModel(
        id=f"h4-island-{role}",
        resources={
            "I1": Resource("I1", 1, "buffer"),
            "M1": Resource("M1", 1, "machine"),
            "O1": Resource("O1", 1, "buffer"),
            "I2": Resource("I2", 1, "buffer"),
            "M2": Resource("M2", 1, "machine"),
            "O2": Resource("O2", 1, "buffer"),
            "AGV": Resource("AGV", 1, "agv"),
        },
        jobs=("A", "B"),
    )
    state = IMSState(
        id=f"h4-{role}-s0",
        holds=(),
        requests={"A": (_alt("I1"),), "B": (_alt("I2"),)},
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"A": "idle", "B": "idle"},
        stage_by_job={"A": "idle", "B": "idle"},
    )
    forward = _cell_chain("A", "a", "I1", "M1", "O1", "AGV", "I2")
    if role == "base":
        reverse = _cell_chain("B", "b", "I2", "M2", "O2", "AGV", "I1")
        intervention = "none"
    else:
        reverse = _cell_chain("B", "b", "I2", "M2", "O2", None, None)
        intervention = "delete_backflow_B_to_I1"
    return H4Island(
        role=role,
        label="synthetic digital-twin",
        model=model,
        initial_state=state,
        transitions=forward + reverse,
        intervention=intervention,
    )


def _cell_chain(
    job: str,
    prefix: str,
    first: str,
    machine: str,
    output: str,
    agv: str | None,
    next_input: str | None,
) -> tuple[TransitionSpec, ...]:
    steps = [
        TransitionSpec(
            name=f"{job}-start-{first}",
            kind=EventKind.START,
            job_id=job,
            source_mode="idle",
            target_mode=f"{prefix}_on_{first}",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand(first),),
            clears_requests=True,
        ),
        TransitionSpec(
            name=f"{job}-to-{machine}",
            kind=EventKind.DISPATCH,
            job_id=job,
            source_mode=f"{prefix}_on_{first}",
            target_mode=f"{prefix}_in_service",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand(machine),),
            release=(ResourceDemand(first),),
        ),
        TransitionSpec(
            name=f"{job}-service-complete",
            kind=EventKind.SERVICE_COMPLETE,
            job_id=job,
            source_mode=f"{prefix}_in_service",
            target_mode=f"{prefix}_blocked_unload",
            controllable=False,
            zero_time=False,
        ),
        TransitionSpec(
            name=f"{job}-unload-{output}",
            kind=EventKind.UNLOAD,
            job_id=job,
            source_mode=f"{prefix}_blocked_unload",
            target_mode=f"{prefix}_on_{output}",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand(output),),
            release=(ResourceDemand(machine),),
        ),
    ]
    if agv is None or next_input is None:
        steps.append(
            TransitionSpec(
                name=f"{job}-complete",
                kind=EventKind.RELEASE,
                job_id=job,
                source_mode=f"{prefix}_on_{output}",
                target_mode="completed",
                controllable=False,
                zero_time=False,
                release=(ResourceDemand(output),),
                mark_complete=True,
            )
        )
        return tuple(steps)
    steps.extend(
        (
            TransitionSpec(
                name=f"{job}-claim-agv",
                kind=EventKind.DISPATCH,
                job_id=job,
                source_mode=f"{prefix}_on_{output}",
                target_mode=f"{prefix}_on_agv",
                controllable=True,
                zero_time=False,
                acquire=(ResourceDemand(agv),),
                release=(ResourceDemand(output),),
            ),
            TransitionSpec(
                name=f"{job}-to-{next_input}",
                kind=EventKind.DISPATCH,
                job_id=job,
                source_mode=f"{prefix}_on_agv",
                target_mode="completed",
                controllable=True,
                zero_time=False,
                acquire=(ResourceDemand(next_input),),
                release=(ResourceDemand(agv),),
                mark_complete=True,
            ),
        )
    )
    return tuple(steps)


def _spec(
    case_id: str,
    title: str,
    model: IMSModel,
    state: IMSState,
    transitions: tuple[TransitionSpec, ...],
) -> CaseSpec:
    return CaseSpec(
        schema_version=CASE_SCHEMA_VERSION,
        case_id=case_id,
        title=title,
        status="DISCOVERY",
        model=model,
        initial_state=state,
        transitions=transitions,
        notes=(SCOPE_ID,),
    )


def materialize_discovery_bundle(root: Path) -> list[Path]:
    """Write H1/H4 JSON and the false authorization map. No science."""

    root.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    auth_path = root / "authorization.json"
    auth_path.write_text(
        json.dumps({"scope_id": SCOPE_ID, **authorization_flags()}, indent=2) + "\n",
        encoding="utf-8",
    )
    written.append(auth_path)
    h1_dir = root / "h1"
    h1_dir.mkdir(exist_ok=True)
    for case_id, spec in build_h1_cases().items():
        path = h1_dir / f"{case_id}.json"
        path.write_text(
            json.dumps(spec.to_json_dict(), indent=2) + "\n", encoding="utf-8"
        )
        written.append(path)
    intervened = _h1_int1_intervened()
    path = h1_dir / f"{intervened.case_id}.json"
    path.write_text(
        json.dumps(intervened.to_json_dict(), indent=2) + "\n", encoding="utf-8"
    )
    written.append(path)
    h2_dir = root / "h2"
    h2_dir.mkdir(exist_ok=True)
    h2_path = h2_dir / "generator.json"
    h2_path.write_text(
        json.dumps(
            {"types": list(H2_TYPES), "cells": list(H2_CELLS), "n_plants": 32},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    written.append(h2_path)
    h3_dir = root / "h3"
    h3_dir.mkdir(exist_ok=True)
    h3_path = h3_dir / "family.json"
    h3_path.write_text(
        json.dumps(
            {
                "n_rows": len(build_h3_rows()),
                "state_cap": H3_STATE_CAP,
                "time_cap_s": H3_TIME_CAP_S,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    written.append(h3_path)
    h4_dir = root / "h4"
    h4_dir.mkdir(exist_ok=True)
    for island in build_h4_islands():
        spec = _spec(
            f"H4_{island.role}",
            f"H4 {island.role} {island.label}",
            island.model,
            island.initial_state,
            island.transitions,
        )
        path = h4_dir / f"H4_{island.role}.json"
        path.write_text(
            json.dumps(spec.to_json_dict(), indent=2) + "\n", encoding="utf-8"
        )
        written.append(path)
    return written
