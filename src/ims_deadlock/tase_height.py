"""H6 published-net embedding, H7 island v4, H8 supervisor baseline."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Literal

from ims_deadlock.analysis import StableLTS, enumerate_stable_lts
from ims_deadlock.certificates import enumerate_local_blocking_certificates
from ims_deadlock.engine import (
    EventKind,
    FiniteLTS,
    TransitionSpec,
    apply_enabled_transition,
    enabled_transition,
    exact_max_nonblocking_supervisor,
)
from ims_deadlock.model import (
    Holding,
    IMSModel,
    IMSState,
    RequestAlternative,
    Resource,
    ResourceDemand,
)
from ims_deadlock.tase_hardening import (
    ARTICLE_CORE_SCOPE_LOCK_SHA256,
    H4Island,
    reject_forbidden_identity,
)
from ims_deadlock.terminal_classes import (
    TerminalPartitionError,
    partition_stable_lts,
)

H6_SPEC_SHA256 = "31dca21694069c35f61a7e9f4a8360313ba900d2a2b3666bf95a94d4fb8d7e6c"
H7_SPEC_SHA256 = "57b236a24ee59ca91b8e1633954d5270a1776063fb4f0a3902b349b1e5173950"
H8_SPEC_SHA256 = "afec89477308551e55021dc98f048835bd6d1d0a400a5919aa9c4a8cce4366d8"

H6_A_ID = "H6_A_ezpeleta_unit_s3pr"
H6_B_ID = "H6_B_agv_distortion"
H7_BASE_MODEL_ID = "h7-island-v4-base"
H7_INT_MODEL_ID = "h7-island-v4-intervention"

SOURCE_LOCATOR = {
    "citation": (
        "J. Ezpeleta, J. M. Colom, and J. Martinez, "
        '"A Petri net based deadlock prevention policy for flexible '
        'manufacturing systems," IEEE Trans. Robot. Autom., vol. 11, '
        "no. 2, pp. 173-184, Apr. 1995."
    ),
    "doi": "10.1109/70.370500",
    "object": (
        "Smallest deadlock-prone S3PR admitted by the S3PR definition: "
        "two sequential processes sharing two unit-capacity resource places. "
        "Not a reconstruction of Ezpeleta Figure 1."
    ),
    "incidence": [
        {"t": "tA1", "pre": ["pA0", "pr1"], "post": ["pA1"]},
        {"t": "tA2", "pre": ["pA1", "pr2"], "post": ["pA2", "pr1"]},
        {"t": "tA3", "pre": ["pA2"], "post": ["pA0", "pr2"]},
        {"t": "tB1", "pre": ["pB0", "pr2"], "post": ["pB1"]},
        {"t": "tB2", "pre": ["pB1", "pr1"], "post": ["pB2", "pr2"]},
        {"t": "tB3", "pre": ["pB2"], "post": ["pB0", "pr1"]},
    ],
}

IOTA_MAP = [
    {"source": "pr1", "image": "r1", "clause": "resource"},
    {"source": "pr2", "image": "r2", "clause": "resource"},
    {"source": "pA0", "image": "A:idle", "clause": "idle"},
    {"source": "pA1", "image": "A:hold:r1", "clause": "operation"},
    {"source": "pA2", "image": "A:hold:r2", "clause": "operation"},
    {"source": "pB0", "image": "B:idle", "clause": "idle"},
    {"source": "pB1", "image": "B:hold:r2", "clause": "operation"},
    {"source": "pB2", "image": "B:hold:r1", "clause": "operation"},
    {"source": "tA1", "image": "A-start-r1", "clause": "event"},
    {"source": "tA2", "image": "A-to-r2", "clause": "event"},
    {"source": "tA3", "image": "A-complete", "clause": "event"},
    {"source": "tB1", "image": "B-start-r2", "clause": "event"},
    {"source": "tB2", "image": "B-to-r1", "clause": "event"},
    {"source": "tB3", "image": "B-complete", "clause": "event"},
]

TARGET_HOLDS = (("A", "r1", 1), ("B", "r2", 1))
TARGET_REQUESTS = (("A", ("r2",)), ("B", ("r1",)))


def _alt(*resource_ids: str) -> RequestAlternative:
    return RequestAlternative(tuple(ResourceDemand(item) for item in resource_ids))


def _hold(job: str, resource: str, units: int = 1) -> Holding:
    return Holding(job, resource, units)


def canonical_dumps(payload: object) -> bytes:
    body = json.dumps(payload, sort_keys=True, ensure_ascii=True, indent=2)
    return (body + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_payload(payload: object) -> str:
    return sha256_bytes(canonical_dumps(payload))


@dataclass(frozen=True)
class HeightPlant:
    """One H6 or H7 executable plant."""

    plant_id: str
    model: IMSModel
    initial_state: IMSState
    transitions: tuple[TransitionSpec, ...]
    role: str = "base"
    intervention: str = "none"


def _by_name(transitions: tuple[TransitionSpec, ...]) -> dict[str, TransitionSpec]:
    return {item.name: item for item in transitions}


def fire_word(plant: HeightPlant, names: tuple[str, ...]) -> IMSState:
    """Apply a named word; raise if any step is disabled."""

    current = plant.initial_state
    lookup = _by_name(plant.transitions)
    for name in names:
        transition = lookup[name]
        nxt = apply_enabled_transition(plant.model, current, transition)
        if nxt is None:
            raise AssertionError(f"{name} is not enabled")
        current = nxt
    return current


def _h6_registry(*, distort: bool) -> tuple[TransitionSpec, ...]:
    a_second_acquire: tuple[ResourceDemand, ...]
    a_second_requests: tuple[RequestAlternative, ...]
    a_complete_release: tuple[ResourceDemand, ...]
    if distort:
        a_second_acquire = (ResourceDemand("r2"), ResourceDemand("V"))
        a_second_requests = (
            RequestAlternative((ResourceDemand("r2"), ResourceDemand("V"))),
        )
        a_complete_release = (ResourceDemand("r2"), ResourceDemand("V"))
    else:
        a_second_acquire = (ResourceDemand("r2"),)
        a_second_requests = (_alt("r2"),)
        a_complete_release = (ResourceDemand("r2"),)
    return (
        TransitionSpec(
            name="A-start-r1",
            kind=EventKind.START,
            job_id="A",
            source_mode="idle",
            target_mode="hold_r1",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("r1"),),
            next_requests=a_second_requests,
        ),
        TransitionSpec(
            name="A-to-r2",
            kind=EventKind.DISPATCH,
            job_id="A",
            source_mode="hold_r1",
            target_mode="hold_r2",
            controllable=True,
            zero_time=False,
            acquire=a_second_acquire,
            release=(ResourceDemand("r1"),),
            clears_requests=True,
        ),
        TransitionSpec(
            name="A-complete",
            kind=EventKind.RELEASE,
            job_id="A",
            source_mode="hold_r2",
            target_mode="completed",
            controllable=False,
            zero_time=False,
            release=a_complete_release,
            mark_complete=True,
        ),
        TransitionSpec(
            name="B-start-r2",
            kind=EventKind.START,
            job_id="B",
            source_mode="idle",
            target_mode="hold_r2",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("r2"),),
            next_requests=(_alt("r1"),),
        ),
        TransitionSpec(
            name="B-to-r1",
            kind=EventKind.DISPATCH,
            job_id="B",
            source_mode="hold_r2",
            target_mode="hold_r1",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("r1"),),
            release=(ResourceDemand("r2"),),
            clears_requests=True,
        ),
        TransitionSpec(
            name="B-complete",
            kind=EventKind.RELEASE,
            job_id="B",
            source_mode="hold_r1",
            target_mode="completed",
            controllable=False,
            zero_time=False,
            release=(ResourceDemand("r1"),),
            mark_complete=True,
        ),
    )


def build_h6_a_plant() -> HeightPlant:
    """Faithful embedding of the definitional two-process S3PR."""

    model = IMSModel(
        id="h6-a-ezpeleta-unit-s3pr",
        resources={
            "r1": Resource("r1", 1, "machine"),
            "r2": Resource("r2", 1, "machine"),
        },
        jobs=("A", "B"),
    )
    state = IMSState(
        id="h6-a-s0",
        holds=(),
        requests={"A": (), "B": ()},
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"A": "idle", "B": "idle"},
        stage_by_job={"A": "idle", "B": "idle"},
    )
    return HeightPlant(
        plant_id=H6_A_ID,
        model=model,
        initial_state=state,
        transitions=_h6_registry(distort=False),
        role="faithful",
    )


def build_h6_b_plant() -> HeightPlant:
    """Declared AGV-token distortion of H6-A. Field 4 must fail E5."""

    model = IMSModel(
        id="h6-b-agv-distortion",
        resources={
            "r1": Resource("r1", 1, "machine"),
            "r2": Resource("r2", 1, "machine"),
            "V": Resource("V", 1, "agv"),
        },
        jobs=("A", "B"),
    )
    state = IMSState(
        id="h6-b-s0",
        holds=(),
        requests={"A": (), "B": ()},
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"A": "idle", "B": "idle"},
        stage_by_job={"A": "idle", "B": "idle"},
    )
    return HeightPlant(
        plant_id=H6_B_ID,
        model=model,
        initial_state=state,
        transitions=_h6_registry(distort=True),
        role="distortion",
        intervention="declared_distortion_agv_token",
    )


def build_h6_plants() -> tuple[HeightPlant, HeightPlant]:
    return build_h6_a_plant(), build_h6_b_plant()


def _ims_identity_payload(plant: HeightPlant) -> dict[str, Any]:
    return {
        "model_id": plant.model.id,
        "state_id": plant.initial_state.id,
        "resources": sorted(plant.model.resources),
        "jobs": list(plant.model.jobs),
        "transitions": [
            {
                "name": item.name,
                "kind": item.kind,
                "job_id": item.job_id,
                "acquire": [demand.resource_id for demand in item.acquire],
                "release": [demand.resource_id for demand in item.release],
            }
            for item in plant.transitions
        ],
    }


def _hold_signature(state: IMSState) -> tuple[tuple[str, str, int], ...]:
    return tuple(
        sorted((item.job_id, item.resource_id, item.units) for item in state.holds)
    )


def _request_signature(state: IMSState) -> tuple[tuple[str, tuple[str, ...]], ...]:
    rows: list[tuple[str, tuple[str, ...]]] = []
    for job, alternatives in state.requests.items():
        names = tuple(
            sorted(
                demand.resource_id
                for alternative in alternatives
                for demand in alternative.demands
            )
        )
        if names:
            rows.append((job, names))
    return tuple(sorted(rows))


def _match_target(state: IMSState) -> bool:
    return (
        _hold_signature(state) == TARGET_HOLDS
        and _request_signature(state) == TARGET_REQUESTS
    )


def _find_target_record(lts: StableLTS) -> Any | None:
    for record in lts.states:
        if _match_target(record.state):
            return record
    return None


def _enabled_names(plant: HeightPlant, state: IMSState) -> set[str]:
    return {
        item.name
        for item in plant.transitions
        if enabled_transition(plant.model, state, item)
    }


def verify_embedding_certificate(
    plant: HeightPlant, *, claimed_prefix: tuple[str, ...] | None = None
) -> dict[str, Any]:
    """Check E1-E6. claimed_prefix is accepted and ignored (Lemma H6.1)."""

    del claimed_prefix
    resources = set(plant.model.resources)
    source_resources = {"r1", "r2"}
    clauses: dict[str, bool] = {}
    clauses["E1"] = all(
        plant.model.resources[name].capacity == 1 for name in source_resources
    )
    idle = plant.initial_state
    clauses["E2"] = (
        idle.holds == ()
        and idle.mode_by_job.get("A") == "idle"
        and idle.mode_by_job.get("B") == "idle"
        and not any(idle.requests.get(job) for job in ("A", "B"))
    )
    enabled = _enabled_names(plant, idle)
    clauses["E3"] = enabled == {"A-start-r1", "B-start-r2"}
    after_a = apply_enabled_transition(
        plant.model, idle, _by_name(plant.transitions)["A-start-r1"]
    )
    after_b = apply_enabled_transition(
        plant.model, idle, _by_name(plant.transitions)["B-start-r2"]
    )
    clauses["E4"] = (
        after_a is not None
        and after_b is not None
        and _hold_signature(after_a) == (("A", "r1", 1),)
        and _hold_signature(after_b) == (("B", "r2", 1),)
    )
    extra = sorted(resources - source_resources)
    clauses["E5"] = extra == []
    clauses["E6"] = tuple(plant.model.jobs) == ("A", "B")
    verified = all(clauses.values())
    reason = None
    if not verified:
        if extra:
            reason = "declared_distortion_agv_token"
        else:
            reason = "embedding_clause_failed:" + ",".join(
                name for name, ok in clauses.items() if not ok
            )
    lts = enumerate_stable_lts(
        plant.model, plant.initial_state, plant.transitions, max_states=4096
    )
    target = _find_target_record(lts)
    identity = _ims_identity_payload(plant)
    reachability = {
        "state_count": len(lts.states),
        "truncated": lts.truncated,
        "target_signature": {
            "holds": [list(item) for item in TARGET_HOLDS],
            "requests": [list(item) for item in TARGET_REQUESTS],
        },
        "bfs_witness": list(target.witness) if target is not None else [],
    }
    certificate = {
        "plant_id": plant.plant_id,
        "source_locator": SOURCE_LOCATOR,
        "iota": IOTA_MAP,
        "clauses": clauses,
        "verified": verified,
        "field4_reason": None if verified else reason,
        "source_locator_sha256": sha256_payload(SOURCE_LOCATOR),
        "iota_map_sha256": sha256_payload(IOTA_MAP),
        "ims_identity_sha256": sha256_payload(identity),
        "lts_reachability_sha256": sha256_payload(reachability),
        "reachability": reachability,
        "ims_identity": identity,
    }
    digest = sha256_payload(certificate)
    reject_forbidden_identity(certificate["ims_identity_sha256"])
    reject_forbidden_identity(digest)
    if digest == ARTICLE_CORE_SCOPE_LOCK_SHA256:
        raise AssertionError("forbidden identity")
    certificate["embedding_certificate_sha256"] = digest
    return certificate


def evaluate_h6_subject(
    plant: HeightPlant, *, claimed_prefix: tuple[str, ...] | None = None
) -> dict[str, Any]:
    """Score Proposition 4 on an H6 plant. claimed_prefix is ignored."""

    certificate = verify_embedding_certificate(plant, claimed_prefix=claimed_prefix)
    lts = enumerate_stable_lts(
        plant.model, plant.initial_state, plant.transitions, max_states=4096
    )
    target = _find_target_record(lts)
    reachable = target is not None and not lts.truncated
    prefix = () if target is None else target.witness
    eval_state = plant.initial_state if target is None else target.state
    family = (
        ()
        if target is None
        else enumerate_local_blocking_certificates(
            plant.model,
            eval_state,
            plant.transitions,
            reachable_prefix=prefix,
        )
    )
    matching = [
        cert for cert in family if frozenset(cert.kernel_resources) == {"r1", "r2"}
    ]
    overlap = bool(certificate["verified"])
    fields = {
        "reachable": reachable,
        "local_family_available": len(family) > 0,
        "matching_kernel_count": len(matching),
        "s4pr_overlap": overlap,
    }
    agreement = (
        fields["reachable"]
        and fields["local_family_available"]
        and fields["matching_kernel_count"] >= 1
        and fields["s4pr_overlap"]
    )
    return {
        "id": plant.plant_id,
        "role": plant.role,
        "r_crp": ["r1", "r2"],
        "fields": fields,
        "field4_reason": certificate.get("field4_reason"),
        "bridge_agreement": agreement,
        "family_size": len(family),
        "kernel_resource_sets": [sorted(cert.kernel_resources) for cert in family],
        "truncated": lts.truncated,
        "state_count": len(lts.states),
        "g4_g5_identity_reused": False,
        "sba_ran": False,
        "crp_equations_ran": False,
        "embedding_certificate_sha256": certificate["embedding_certificate_sha256"],
        "certificate": certificate,
        "h6_spec_sha256": H6_SPEC_SHA256,
    }


def evaluate_h6_subjects() -> tuple[dict[str, Any], ...]:
    return tuple(evaluate_h6_subject(plant) for plant in build_h6_plants())


def _h7_registry() -> list[TransitionSpec]:
    return [
        TransitionSpec(
            name="A-start-m1",
            kind=EventKind.START,
            job_id="A",
            source_mode="idle",
            target_mode="in_service",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("M1"),),
            next_requests=(_alt("V"),),
        ),
        TransitionSpec(
            name="A-service-complete",
            kind=EventKind.SERVICE_COMPLETE,
            job_id="A",
            source_mode="in_service",
            target_mode="blocked_unload",
            controllable=False,
            zero_time=False,
        ),
        TransitionSpec(
            name="A-unload-v",
            kind=EventKind.UNLOAD,
            job_id="A",
            source_mode="blocked_unload",
            target_mode="on_v",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("V"),),
            release=(ResourceDemand("M1"),),
            clears_requests=True,
        ),
        TransitionSpec(
            name="A-complete-release-v",
            kind=EventKind.RELEASE,
            job_id="A",
            source_mode="on_v",
            target_mode="completed",
            controllable=False,
            zero_time=False,
            release=(ResourceDemand("V"),),
            mark_complete=True,
        ),
        TransitionSpec(
            name="B-start-v",
            kind=EventKind.START,
            job_id="B",
            source_mode="idle",
            target_mode="wait",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("V"),),
            next_requests=(_alt("M1"),),
        ),
        TransitionSpec(
            name="B-enter-m1",
            kind=EventKind.DISPATCH,
            job_id="B",
            source_mode="wait",
            target_mode="on_m1",
            controllable=True,
            zero_time=False,
            acquire=(ResourceDemand("M1"),),
            release=(ResourceDemand("V"),),
            clears_requests=True,
        ),
        TransitionSpec(
            name="B-complete-release-m1",
            kind=EventKind.RELEASE,
            job_id="B",
            source_mode="on_m1",
            target_mode="completed",
            controllable=False,
            zero_time=False,
            release=(ResourceDemand("M1"),),
            mark_complete=True,
        ),
        TransitionSpec(
            name="C-service-1",
            kind=EventKind.SERVICE_COMPLETE,
            job_id="C",
            source_mode="in_service_1",
            target_mode="in_service_2",
            controllable=False,
            zero_time=False,
        ),
        TransitionSpec(
            name="C-service-2",
            kind=EventKind.SERVICE_COMPLETE,
            job_id="C",
            source_mode="in_service_2",
            target_mode="blocked_unload",
            controllable=False,
            zero_time=False,
        ),
        TransitionSpec(
            name="C-release-m2",
            kind=EventKind.RELEASE,
            job_id="C",
            source_mode="blocked_unload",
            target_mode="completed",
            controllable=True,
            zero_time=False,
            clears_requests=True,
            release=(ResourceDemand("M2"),),
            mark_complete=True,
        ),
    ]


def build_h7_island(role: Literal["base", "intervention"]) -> H4Island:
    """Positive-time local-hit island. Does not overwrite H4-v3."""

    agv_capacity = 2 if role == "intervention" else 1
    model = IMSModel(
        id=H7_INT_MODEL_ID if role == "intervention" else H7_BASE_MODEL_ID,
        resources={
            "M1": Resource("M1", 1, "machine"),
            "M2": Resource("M2", 1, "machine"),
            "V": Resource("V", agv_capacity, "agv"),
        },
        jobs=("A", "B", "C"),
    )
    state = IMSState(
        id=f"h7-v4-{role}-s0",
        holds=(_hold("C", "M2"),),
        requests={"A": (), "B": (), "C": ()},
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"A": "idle", "B": "idle", "C": "in_service_1"},
        stage_by_job={"A": "idle", "B": "idle", "C": "in_service_1"},
    )
    return H4Island(
        role=role,
        label="synthetic digital-twin v4",
        model=model,
        initial_state=state,
        transitions=tuple(_h7_registry()),
        intervention="extra_agv_slot" if role == "intervention" else "none",
    )


def build_h7_islands() -> tuple[H4Island, H4Island]:
    return build_h7_island("base"), build_h7_island("intervention")


def h7_as_height_plant(island: H4Island) -> HeightPlant:
    return HeightPlant(
        plant_id=f"H7_v4_{island.role}",
        model=island.model,
        initial_state=island.initial_state,
        transitions=island.transitions,
        role=island.role,
        intervention=island.intervention,
    )


H7_LOCAL_HIT_WORD = ("A-start-m1", "A-service-complete", "B-start-v")


def h7_event_rates(transitions: tuple[TransitionSpec, ...]) -> dict[str, float]:
    special = {
        "A-start-m1": 1.0,
        "B-start-v": 1.0,
        "A-service-complete": 2.0,
        "C-service-1": 0.5,
        "C-service-2": 0.5,
    }
    return {item.name: special.get(item.name, 1.0) for item in transitions}


def eval_h7_barrier(role: str) -> dict[str, Any]:
    """Barrier B for the H7 island. Payload shape matches H4 so exact/DES reuse."""

    island = build_h7_island("intervention" if role == "intervention" else "base")
    lts = enumerate_stable_lts(
        island.model,
        island.initial_state,
        island.transitions,
        max_states=4096,
    )
    payload: dict[str, Any] = {
        "id": f"H7_v4_{island.role}",
        "role": island.role,
        "label": island.label,
        "intervention": island.intervention,
        "model_id": island.model.id,
        "state_count": len(lts.states),
        "truncated": lts.truncated,
        "barrier_a": "refused",
        "refusal_code": None,
        "states": [],
        "transitions": [],
        "d_global": [],
        "d_local": [],
        "completion": [],
        "initial_state": None,
        "initial_class": None,
        "local_with_outgoing": 0,
        "h7_spec_sha256": H7_SPEC_SHA256,
    }
    if lts.truncated or not lts.states:
        payload["refusal_code"] = "truncated_or_empty_lts"
        return payload
    try:
        partition = partition_stable_lts(
            island.model,
            lts,
            island.transitions,
            verify_generated_lts=True,
        )
        unselected = (
            list(partition.r_livelock_state_ids)
            + list(partition.r_terminal_state_ids)
            + list(partition.unreachable_nonabsorbing_state_ids)
        )
        if unselected:
            payload["refusal_code"] = "unselected_closed_or_unreachable"
            payload["refusal_details"] = {"state_ids": unselected}
            return payload
    except TerminalPartitionError as error:
        payload["refusal_code"] = error.code
        payload["refusal_details"] = error.details
        return payload
    rates = h7_event_rates(island.transitions)
    outgoing_sources = {arc.source for arc in lts.transitions}
    local_with_outgoing = sum(
        1 for state_id in partition.d_local_state_ids if state_id in outgoing_sources
    )
    initial = lts.initial_state_id
    if initial in partition.d_global_state_ids:
        initial_class = "D_global"
    elif initial in partition.d_local_state_ids:
        initial_class = "D_local"
    elif initial in partition.f_state_ids:
        initial_class = "F"
    else:
        initial_class = "transient"
    payload.update(
        {
            "barrier_a": "certified",
            "initial_state": initial,
            "initial_class": initial_class,
            "states": [record.state_id for record in lts.states],
            "d_global": list(partition.d_global_state_ids),
            "d_local": list(partition.d_local_state_ids),
            "completion": list(partition.f_state_ids),
            "local_with_outgoing": local_with_outgoing,
            "plant_identity": _ims_identity_payload(h7_as_height_plant(island)),
            "transitions": [
                {
                    "source": arc.source,
                    "event": arc.event,
                    "target": arc.target,
                    "rate": rates[arc.event],
                }
                for arc in lts.transitions
            ],
        }
    )
    return payload


def h7_local_hit_enabled() -> bool:
    plant = h7_as_height_plant(build_h7_island("base"))
    try:
        state = fire_word(plant, H7_LOCAL_HIT_WORD)
    except AssertionError:
        return False
    holds = set(_hold_signature(state))
    return {
        ("A", "M1", 1),
        ("B", "V", 1),
        ("C", "M2", 1),
    }.issubset(holds) and "C-service-1" in _enabled_names(plant, state)


def build_supervised_lts(barrier: dict[str, Any], island: H4Island) -> FiniteLTS:
    ctrl = {item.name: item.controllable for item in island.transitions}
    return FiniteLTS(
        states=tuple(barrier["states"]),
        initial_state=str(barrier["initial_state"]),
        marked_states=tuple(barrier["completion"]),
        transitions=tuple(
            (
                str(arc["source"]),
                str(arc["event"]),
                str(arc["target"]),
                bool(ctrl[str(arc["event"])]),
            )
            for arc in barrier["transitions"]
        ),
    )


def evaluate_h8_supervisor(barrier: dict[str, Any], island: H4Island) -> dict[str, Any]:
    """Ramadge-Wonham baseline on the bound H7 (or fallback) plant."""

    if barrier["barrier_a"] != "certified":
        return {
            "id": f"H8_{barrier['id']}",
            "status": "refused",
            "reason": barrier.get("refusal_code"),
            "h8_spec_sha256": H8_SPEC_SHA256,
        }
    finite = build_supervised_lts(barrier, island)
    forbidden = list(barrier["d_global"]) + list(barrier["d_local"])
    policy = exact_max_nonblocking_supervisor(finite, forbidden_states=forbidden)
    disabled = policy.disabled_state_events
    if any(
        not any(item.name == event and item.controllable for item in island.transitions)
        for _state, event in disabled
    ):
        raise AssertionError("supervisor disabled an uncontrollable event")
    cut = {(str(source), str(event)) for source, event in disabled}
    supervised_transitions = [
        arc
        for arc in barrier["transitions"]
        if (str(arc["source"]), str(arc["event"])) not in cut
    ]
    supervised = {
        "id": f"{barrier['id']}__supervised",
        "barrier_a": "certified",
        "initial_state": barrier["initial_state"],
        "states": list(barrier["states"]),
        "d_global": list(barrier["d_global"]),
        "d_local": list(barrier["d_local"]),
        "completion": list(barrier["completion"]),
        "transitions": supervised_transitions,
    }
    from ims_deadlock.tase_hardening_run import solve_h4_exact

    supervised_exact = (
        solve_h4_exact(supervised) if policy.initial_state_feasible else None
    )
    return {
        "id": f"H8_{barrier['id']}",
        "status": "computed",
        "plant_id": barrier["id"],
        "model_id": island.model.id,
        "n_states": len(barrier["states"]),
        "n_safe": len(policy.safe_states),
        "n_disabled_state_events": len(disabled),
        "initial_state_feasible": policy.initial_state_feasible,
        "supervisor_initial_infeasible": not policy.initial_state_feasible,
        "disabled_state_events": [list(item) for item in disabled],
        "supervised_exact": supervised_exact,
        "h8_spec_sha256": H8_SPEC_SHA256,
        "h8_plant": barrier["id"],
    }
