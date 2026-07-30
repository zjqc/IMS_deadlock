"""Deterministic, implementation-locked IMS builders for G4 confirmation.

The builders in this module only translate frozen parameters into ``CaseSpec``
objects.  They do not enumerate reachability, classify deadlocks, synthesize a
supervisor, solve a CTMC, or inspect a confirmation outcome.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from ims_deadlock.cases import CASE_SCHEMA_VERSION, CaseSpec
from ims_deadlock.ctmc import AbsorbingCTMC
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
    G6_CTM_GENERATOR_PROVENANCE,
    TerminalPartitionError,
    TerminalStoppingPartition,
    VersionedEstimandSpec,
    partition_stable_lts,
)

BIDIRECTIONAL_GENERATOR_ID = "bidirectional_bas_v1"
MEDIUM_ISLAND_GENERATOR_ID = "three_island_bas_v1"
ADVERSARIAL_GENERATOR_ID = "or_and_reservation_v1"

_MEDIUM_ROUTE_IDS = ("ABG", "AG", "BAG")


@dataclass(frozen=True)
class BidirectionalGridCell:
    """One exact cell in the held-out bidirectional BAS grid."""

    cell_id: str
    machine_capacity: int
    buffer_capacity: int
    agv_count: int
    forward_wip: int
    reverse_wip: int
    service_rate: float
    transfer_rate: float
    release_rate: float
    state_bound: int

    def __post_init__(self) -> None:
        _require_identifier("cell_id", self.cell_id)
        _require_positive_int("machine_capacity", self.machine_capacity)
        _require_positive_int("buffer_capacity", self.buffer_capacity)
        _require_positive_int("agv_count", self.agv_count)
        _require_nonnegative_int("forward_wip", self.forward_wip)
        _require_nonnegative_int("reverse_wip", self.reverse_wip)
        if self.total_wip <= 0:
            raise ValueError("a grid cell must contain at least one job")
        _require_positive_rate("service_rate", self.service_rate)
        _require_positive_rate("transfer_rate", self.transfer_rate)
        _require_positive_rate("release_rate", self.release_rate)
        _require_positive_int("state_bound", self.state_bound)

    @property
    def total_wip(self) -> int:
        return self.forward_wip + self.reverse_wip

    @property
    def route_mix(self) -> tuple[int, int]:
        return (self.forward_wip, self.reverse_wip)

    @property
    def event_rates(self) -> dict[str, float]:
        return {
            "release": float(self.release_rate),
            "service": float(self.service_rate),
            "transfer": float(self.transfer_rate),
        }


@dataclass(frozen=True)
class MediumIslandParameters:
    """Exact parameters for the independent three-island rebuild."""

    instance_id: str
    machine_capacity: int
    buffer_capacity: int
    agv_count: int
    route_wip: tuple[tuple[str, int], ...]
    service_rate: float
    transfer_rate: float
    release_rate: float
    state_bound: int

    def __post_init__(self) -> None:
        _require_identifier("instance_id", self.instance_id)
        _require_positive_int("machine_capacity", self.machine_capacity)
        _require_positive_int("buffer_capacity", self.buffer_capacity)
        _require_positive_int("agv_count", self.agv_count)
        _require_positive_rate("service_rate", self.service_rate)
        _require_positive_rate("transfer_rate", self.transfer_rate)
        _require_positive_rate("release_rate", self.release_rate)
        _require_positive_int("state_bound", self.state_bound)
        route_ids = tuple(route_id for route_id, _count in self.route_wip)
        if len(set(route_ids)) != len(route_ids):
            raise ValueError("medium route_wip route IDs must be unique")
        unknown = sorted(set(route_ids) - set(_MEDIUM_ROUTE_IDS))
        if unknown:
            raise ValueError(f"unknown medium route ID {unknown[0]!r}")
        for route_id, count in self.route_wip:
            _require_nonnegative_int(f"route_wip[{route_id}]", count)
        if self.total_wip <= 0:
            raise ValueError("the medium instance must contain at least one job")
        object.__setattr__(self, "route_wip", tuple(sorted(self.route_wip)))

    @property
    def total_wip(self) -> int:
        return sum(count for _route_id, count in self.route_wip)

    @property
    def event_rates(self) -> dict[str, float]:
        return {
            "release": float(self.release_rate),
            "service": float(self.service_rate),
            "transfer": float(self.transfer_rate),
        }


@dataclass(frozen=True)
class AdversarialBoundaryParameters:
    """Exact parameters for the OR-of-AND reservation boundary generator."""

    instance_id: str
    fixture_capacity: int
    cart_capacity: int
    reservation_capacity: int
    decision_rate: float
    state_bound: int

    def __post_init__(self) -> None:
        _require_identifier("instance_id", self.instance_id)
        _require_positive_int("fixture_capacity", self.fixture_capacity)
        if self.fixture_capacity < 2:
            raise ValueError("fixture_capacity must be at least two")
        _require_positive_int("cart_capacity", self.cart_capacity)
        _require_positive_int("reservation_capacity", self.reservation_capacity)
        _require_positive_rate("decision_rate", self.decision_rate)
        _require_positive_int("state_bound", self.state_bound)


@dataclass(frozen=True)
class BuiltG4Case:
    """A deterministic case plus an exact rate for every generated event."""

    spec: CaseSpec
    event_rates: dict[str, float]
    state_bound: int
    generator_id: str


@dataclass(frozen=True)
class DerivedG4CTMC:
    """Exact CTMC partition derived from a complete generated stable LTS."""

    ctmc: AbsorbingCTMC
    initial_state: str
    stable_state_count: int
    completion_state_ids: tuple[str, ...]
    deadlock_state_ids: tuple[str, ...]
    global_deadlock_state_ids: tuple[str, ...] = ()
    local_deadlock_state_ids: tuple[str, ...] = ()
    terminal_classification: TerminalStoppingPartition | None = None
    estimand: dict[str, object] | None = None
    truncated: bool = False


def build_bidirectional_island_case(
    parameters: BidirectionalGridCell,
) -> BuiltG4Case:
    """Build a two-island BAS exchange model with AGV-coupled transfer."""

    resources = {
        "agv": Resource("agv", parameters.agv_count, "agv"),
        "buffer_x": Resource("buffer_x", parameters.buffer_capacity, "buffer"),
        "buffer_y": Resource("buffer_y", parameters.buffer_capacity, "buffer"),
        "machine_x": Resource("machine_x", parameters.machine_capacity, "machine"),
        "machine_y": Resource("machine_y", parameters.machine_capacity, "machine"),
    }
    routes: dict[str, tuple[tuple[str, ...], ...]] = {
        "FWD": (
            ("machine_x",),
            ("agv", "buffer_y"),
            ("machine_y",),
        ),
        "REV": (
            ("machine_y",),
            ("agv", "buffer_x"),
            ("machine_x",),
        ),
    }
    route_wip = (
        ("FWD", parameters.forward_wip),
        ("REV", parameters.reverse_wip),
    )
    return _build_bas_route_case(
        case_id=f"G4_GRID_{parameters.cell_id}",
        model_id=f"g4-grid-{parameters.cell_id.lower()}",
        title=f"G4 bidirectional BAS grid cell {parameters.cell_id}",
        resources=resources,
        routes=routes,
        route_wip=route_wip,
        service_rate=parameters.service_rate,
        transfer_rate=parameters.transfer_rate,
        release_rate=parameters.release_rate,
        state_bound=parameters.state_bound,
        generator_id=BIDIRECTIONAL_GENERATOR_ID,
    )


def build_medium_island_case(
    parameters: MediumIslandParameters,
) -> BuiltG4Case:
    """Build the exact three-island BAS/AGV confirmation instance."""

    resources = {
        "agv": Resource("agv", parameters.agv_count, "agv"),
        "alpha_out": Resource("alpha_out", parameters.buffer_capacity, "buffer"),
        "beta_out": Resource("beta_out", parameters.buffer_capacity, "buffer"),
        "inspect": Resource("inspect", parameters.machine_capacity, "machine"),
        "lathe": Resource("lathe", parameters.machine_capacity, "machine"),
        "mill": Resource("mill", parameters.machine_capacity, "machine"),
        "oven": Resource("oven", parameters.machine_capacity, "machine"),
        "paint": Resource("paint", parameters.machine_capacity, "machine"),
    }
    routes: dict[str, tuple[tuple[str, ...], ...]] = {
        "ABG": (
            ("lathe",),
            ("agv", "alpha_out"),
            ("paint",),
            ("oven",),
            ("agv", "beta_out"),
            ("inspect",),
        ),
        "BAG": (
            ("paint",),
            ("oven",),
            ("agv", "beta_out"),
            ("mill",),
            ("agv", "alpha_out"),
            ("inspect",),
        ),
        "AG": (
            ("mill",),
            ("agv", "alpha_out"),
            ("inspect",),
        ),
    }
    return _build_bas_route_case(
        case_id=f"G4_MEDIUM_{parameters.instance_id}",
        model_id=f"g4-medium-{parameters.instance_id.lower()}",
        title=f"G4 independent medium island {parameters.instance_id}",
        resources=resources,
        routes=routes,
        route_wip=parameters.route_wip,
        service_rate=parameters.service_rate,
        transfer_rate=parameters.transfer_rate,
        release_rate=parameters.release_rate,
        state_bound=parameters.state_bound,
        generator_id=MEDIUM_ISLAND_GENERATOR_ID,
    )


def build_adversarial_boundary_case(
    parameters: AdversarialBoundaryParameters,
) -> BuiltG4Case:
    """Build an exact multi-capacity OR-of-AND reservation snapshot."""

    resources = {
        "cart_left": Resource("cart_left", parameters.cart_capacity, "agv"),
        "cart_right": Resource("cart_right", parameters.cart_capacity, "agv"),
        "fixture_a": Resource("fixture_a", parameters.fixture_capacity, "machine"),
        "fixture_b": Resource("fixture_b", parameters.fixture_capacity, "machine"),
        "inspection": Resource("inspection", 1, "machine"),
        "reserve_a": Resource(
            "reserve_a", parameters.reservation_capacity, "reservation"
        ),
        "reserve_b": Resource(
            "reserve_b", parameters.reservation_capacity, "reservation"
        ),
    }
    jobs = ("gate", "left", "right")
    left_cross = RequestAlternative(_demands(("fixture_b", "cart_right")))
    left_inspect = RequestAlternative(_demands(("inspection", "reserve_b")))
    right_cross = RequestAlternative(_demands(("fixture_a", "cart_left")))
    right_inspect = RequestAlternative(_demands(("inspection", "reserve_a")))
    gate_release = RequestAlternative(_demands(("reserve_a", "reserve_b")))
    initial_state = IMSState(
        id=f"g4-adversarial-{parameters.instance_id.lower()}-target",
        holds=(
            Holding(
                "left",
                "fixture_a",
                parameters.fixture_capacity,
            ),
            Holding("left", "reserve_a", parameters.reservation_capacity),
            Holding(
                "right",
                "fixture_b",
                parameters.fixture_capacity,
            ),
            Holding("right", "reserve_b", parameters.reservation_capacity),
            Holding("gate", "cart_left", parameters.cart_capacity),
            Holding("gate", "cart_right", parameters.cart_capacity),
            Holding("gate", "inspection", 1),
        ),
        requests={
            "gate": (gate_release,),
            "left": (left_cross, left_inspect),
            "right": (right_cross, right_inspect),
        },
        completed_jobs=frozenset(),
        stable=True,
        complete=False,
        event_calendar_empty=True,
        stage_by_job={
            "gate": "gate_wait",
            "left": "or_pending",
            "right": "or_pending",
        },
        mode_by_job={
            "gate": "gate_wait",
            "left": "or_pending",
            "right": "or_pending",
        },
    )
    transitions = (
        _boundary_choice(
            "gate:release_reservations",
            "gate",
            "gate_wait",
            "gate_released",
            gate_release,
        ),
        _boundary_choice(
            "left:choose_cross",
            "left",
            "or_pending",
            "left_branch_cross",
            left_cross,
        ),
        _boundary_choice(
            "left:choose_inspection",
            "left",
            "or_pending",
            "left_branch_inspection",
            left_inspect,
        ),
        _boundary_choice(
            "right:choose_cross",
            "right",
            "or_pending",
            "right_branch_cross",
            right_cross,
        ),
        _boundary_choice(
            "right:choose_inspection",
            "right",
            "or_pending",
            "right_branch_inspection",
            right_inspect,
        ),
    )
    model = IMSModel(
        id=f"g4-adversarial-{parameters.instance_id.lower()}",
        resources=resources,
        jobs=jobs,
    )
    spec = CaseSpec(
        schema_version=CASE_SCHEMA_VERSION,
        case_id=f"G4_ADVERSARIAL_{parameters.instance_id}",
        title=f"G4 OR-of-AND boundary {parameters.instance_id}",
        status="PREREGISTERED",
        model=model,
        initial_state=initial_state,
        transitions=transitions,
        notes=(
            "Generated deterministically from frozen G4 parameters.",
            "Each OR branch is an explicit transition to a persistent branch mode.",
            "The target retains AGV and reservation resources explicitly.",
        ),
    )
    return BuiltG4Case(
        spec=spec,
        event_rates={
            transition.name: float(parameters.decision_rate)
            for transition in transitions
        },
        state_bound=parameters.state_bound,
        generator_id=ADVERSARIAL_GENERATOR_ID,
    )


def derive_absorbing_ctmc(
    built: BuiltG4Case,
    *,
    estimand_spec: VersionedEstimandSpec = DEFAULT_ESTIMAND_SPEC,
) -> DerivedG4CTMC:
    """Derive a case-bound CTMC from a complete generated stable LTS.

    This is a scientific execution entrypoint and must not be called on a
    held-out G4 case until the freeze seal has validated.
    """

    from ims_deadlock.analysis import enumerate_stable_lts

    stable_lts = enumerate_stable_lts(
        built.spec.model,
        built.spec.initial_state,
        built.spec.transitions,
        max_states=built.state_bound,
    )
    if stable_lts.truncated:
        raise ValueError("generated stable LTS exceeds the frozen state_bound")
    if len(stable_lts.initial_state_ids) != 1:
        raise ValueError("CTMC derivation requires one stable initial state")

    partition = partition_stable_lts(
        built.spec.model,
        stable_lts,
        built.spec.transitions,
        event_rates=built.event_rates,
        estimand_spec=estimand_spec,
        require_selected_absorption=False,
        verify_generated_lts=True,
    )
    if (
        partition.d_local_state_ids
        and "D_local" not in estimand_spec.selected_bad_classes
    ):
        raise TerminalPartitionError(
            "d_global_only_estimand_refuses_local_core",
            "D_global-only estimand is invalid when local blocking cores exist",
            {
                "local_state_ids": list(partition.d_local_state_ids),
                "selected_bad_classes": list(estimand_spec.selected_bad_classes),
            },
        )
    if partition.unreachable_nonabsorbing_state_ids:
        raise TerminalPartitionError(
            "unreachable_nonabsorbing_state",
            "nonabsorbing state cannot reach selected bad or success absorption",
            {
                "unreachable_state_ids": list(
                    partition.unreachable_nonabsorbing_state_ids
                ),
                "terminal_scc_state_ids": sorted(
                    set(partition.r_terminal_state_ids)
                    | set(partition.r_livelock_state_ids)
                ),
            },
        )
    completion_states = set(partition.f_state_ids)
    deadlock_states = set(partition.selected_bad_state_ids)
    overlap = completion_states & deadlock_states
    if overlap:
        raise ValueError("a stable state cannot be completion and deadlock")
    transient_states = partition.transient_state_ids
    initial_state = stable_lts.initial_state_ids[0]
    if initial_state in completion_states or initial_state in deadlock_states:
        raise ValueError("CTMC derivation requires a transient initial state")

    transient_rates: dict[tuple[str, str], float] = {}
    completion_rates: dict[tuple[str, str], float] = {}
    deadlock_rates: dict[tuple[str, str], float] = {}
    transient_set = set(transient_states)
    for arc in stable_lts.transitions:
        if arc.source not in transient_set:
            continue
        try:
            rate = built.event_rates[arc.event]
        except KeyError as exc:
            raise ValueError(f"missing frozen event rate for {arc.event!r}") from exc
        if arc.target in completion_states:
            _add_rate(completion_rates, (arc.source, "__completion__"), rate)
        elif arc.target in deadlock_states:
            _add_rate(deadlock_rates, (arc.source, "__deadlock__"), rate)
        elif arc.target in transient_set and arc.target != arc.source:
            _add_rate(transient_rates, (arc.source, arc.target), rate)
        elif arc.target not in transient_set:
            raise ValueError("stable LTS target has no absorption classification")

    ctmc = AbsorbingCTMC(
        transient_states=transient_states,
        completion_rates=completion_rates,
        deadlock_rates=deadlock_rates,
        transient_rates=transient_rates,
        generator_provenance=G6_CTM_GENERATOR_PROVENANCE,
        case_derived=True,
    )
    ctmc._validate()
    return DerivedG4CTMC(
        ctmc=ctmc,
        initial_state=initial_state,
        stable_state_count=len(stable_lts.states),
        completion_state_ids=tuple(sorted(completion_states)),
        deadlock_state_ids=tuple(sorted(deadlock_states)),
        global_deadlock_state_ids=partition.d_global_state_ids,
        local_deadlock_state_ids=partition.d_local_state_ids,
        terminal_classification=partition,
        estimand={
            **partition.estimand_spec.to_json_dict(),
            "hashes": partition.hashes_json_dict(),
        },
    )


def _build_bas_route_case(
    *,
    case_id: str,
    model_id: str,
    title: str,
    resources: dict[str, Resource],
    routes: dict[str, tuple[tuple[str, ...], ...]],
    route_wip: tuple[tuple[str, int], ...],
    service_rate: float,
    transfer_rate: float,
    release_rate: float,
    state_bound: int,
    generator_id: str,
) -> BuiltG4Case:
    jobs: list[str] = []
    job_routes: list[tuple[str, tuple[tuple[str, ...], ...]]] = []
    for route_id, count in sorted(route_wip):
        if route_id not in routes:
            raise ValueError(f"unknown BAS route ID {route_id!r}")
        for ordinal in range(1, count + 1):
            job_id = f"{route_id}_{ordinal:02d}"
            jobs.append(job_id)
            job_routes.append((job_id, routes[route_id]))

    transitions: list[TransitionSpec] = []
    event_rates: dict[str, float] = {}
    for job_id, route in job_routes:
        if not route:
            raise ValueError("BAS routes must contain at least one stage")
        start_name = f"{job_id}:release"
        transitions.append(
            TransitionSpec(
                name=start_name,
                kind=EventKind.START,
                job_id=job_id,
                source_mode="outside",
                target_mode="processing_0",
                controllable=True,
                zero_time=False,
                acquire=_demands(route[0]),
            )
        )
        event_rates[start_name] = float(release_rate)

        for stage_index, stage in enumerate(route):
            service_name = f"{job_id}:service:{stage_index}"
            is_last = stage_index == len(route) - 1
            if is_last:
                transitions.append(
                    TransitionSpec(
                        name=service_name,
                        kind=EventKind.SERVICE_COMPLETE,
                        job_id=job_id,
                        source_mode=f"processing_{stage_index}",
                        target_mode="completed",
                        controllable=False,
                        zero_time=False,
                        clears_requests=True,
                        release=_demands(stage),
                        mark_complete=True,
                    )
                )
                event_rates[service_name] = float(service_rate)
                continue

            next_stage = route[stage_index + 1]
            transitions.append(
                TransitionSpec(
                    name=service_name,
                    kind=EventKind.SERVICE_COMPLETE,
                    job_id=job_id,
                    source_mode=f"processing_{stage_index}",
                    target_mode=f"blocked_{stage_index}",
                    controllable=False,
                    zero_time=False,
                    next_requests=(RequestAlternative(_demands(next_stage)),),
                )
            )
            event_rates[service_name] = float(service_rate)

            transfer_name = f"{job_id}:transfer:{stage_index + 1}"
            next_alternative = RequestAlternative(_demands(next_stage))
            transitions.append(
                TransitionSpec(
                    name=transfer_name,
                    kind=EventKind.DISPATCH,
                    job_id=job_id,
                    source_mode=f"blocked_{stage_index}",
                    target_mode=f"processing_{stage_index + 1}",
                    controllable=True,
                    zero_time=False,
                    clears_requests=True,
                    acquire=_demands(next_stage),
                    release=_demands(stage),
                    requires=(next_alternative,),
                )
            )
            event_rates[transfer_name] = float(transfer_rate)

    model = IMSModel(
        id=model_id,
        resources=dict(sorted(resources.items())),
        jobs=tuple(sorted(jobs)),
    )
    initial_state = IMSState(
        id=f"{model_id}-initial",
        completed_jobs=frozenset(),
        stable=True,
        complete=False,
        event_calendar_empty=False,
        stage_by_job={job: "outside" for job in model.jobs},
        mode_by_job={job: "outside" for job in model.jobs},
    )
    spec = CaseSpec(
        schema_version=CASE_SCHEMA_VERSION,
        case_id=case_id,
        title=title,
        status="PREREGISTERED",
        model=model,
        initial_state=initial_state,
        transitions=tuple(
            sorted(
                transitions,
                key=lambda item: (item.job_id, item.name),
            )
        ),
        calendar=(),
        ctmc=None,
        ctmc_provenance=None,
        notes=(
            "Generated deterministically from frozen G4 parameters.",
            "BAS semantics: a job retains its current stage bundle until the "
            "next bundle is acquired.",
            "AGV occupancy is an explicit reusable resource in transfer bundles.",
        ),
    )
    return BuiltG4Case(
        spec=spec,
        event_rates=dict(sorted(event_rates.items())),
        state_bound=state_bound,
        generator_id=generator_id,
    )


def _demands(resource_ids: tuple[str, ...]) -> tuple[ResourceDemand, ...]:
    return tuple(ResourceDemand(resource_id, 1) for resource_id in resource_ids)


def _boundary_choice(
    name: str,
    job_id: str,
    source_mode: str,
    target_mode: str,
    alternative: RequestAlternative,
) -> TransitionSpec:
    return TransitionSpec(
        name=name,
        kind=EventKind.RESERVE,
        job_id=job_id,
        source_mode=source_mode,
        target_mode=target_mode,
        controllable=True,
        zero_time=False,
        clears_requests=True,
        acquire=alternative.demands,
        requires=(alternative,),
    )


def _add_rate(
    rates: dict[tuple[str, str], float],
    edge: tuple[str, str],
    rate: float,
) -> None:
    rates[edge] = rates.get(edge, 0.0) + float(rate)


def _require_identifier(name: str, value: object) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a nonempty string")
    if not all(character.isalnum() or character == "_" for character in value):
        raise ValueError(f"{name} must contain only letters, digits, or underscore")


def _require_positive_int(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _require_nonnegative_int(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


def _require_positive_rate(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a positive finite rate")
    if not isfinite(float(value)) or float(value) <= 0.0:
        raise ValueError(f"{name} must be a positive finite rate")
