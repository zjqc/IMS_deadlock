"""Declarative case specifications for discovery and verification."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

from ims_deadlock.ctmc import AbsorbingCTMC
from ims_deadlock.engine import ScheduledEvent, TransitionSpec
from ims_deadlock.model import (
    Holding,
    IMSModel,
    IMSState,
    RequestAlternative,
    Resource,
    ResourceDemand,
    ResourceKind,
    validate_model_state,
)

CASE_SCHEMA_VERSION = "ims-deadlock/case/v1"
_CASES_DIR = Path(__file__).resolve().parents[2] / "cases"
_ALLOWED_RESOURCE_KINDS = {"machine", "buffer", "agv", "reservation"}


@dataclass(frozen=True)
class CaseSpec:
    """Declarative case payload used by the CLI and tests."""

    schema_version: str
    case_id: str
    title: str
    status: str
    model: IMSModel
    initial_state: IMSState
    transitions: tuple[TransitionSpec, ...] = field(default_factory=tuple)
    calendar: tuple[ScheduledEvent, ...] = field(default_factory=tuple)
    ctmc: AbsorbingCTMC | None = None
    ctmc_provenance: str | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "title": self.title,
            "status": self.status,
            "model": _model_to_json(self.model),
            "initial_state": _state_to_json(self.initial_state),
            "transitions": [
                _transition_to_json(transition) for transition in self.transitions
            ],
            "calendar": [_calendar_to_json(event) for event in self.calendar],
            "notes": list(self.notes),
        }
        if self.ctmc is not None:
            payload["ctmc"] = _ctmc_to_json(self.ctmc)
        if self.ctmc_provenance is not None:
            payload["ctmc_provenance"] = self.ctmc_provenance
        return payload


def load_case_spec(case_id: str, *, root: Path | None = None) -> CaseSpec:
    """Load a declarative case JSON file from ``cases/``."""

    cases_dir = _CASES_DIR if root is None else root
    path = cases_dir / f"{case_id.upper()}.json"
    if not path.exists():
        raise ValueError(f"unknown case specification {case_id!r}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.loads(
            handle.read(), object_pairs_hook=_no_duplicate_keys_object_pairs_hook
        )
    return case_spec_from_json(payload)


def case_spec_from_json(payload: Mapping[str, Any]) -> CaseSpec:
    """Parse one data-only case payload without reading or analyzing it."""

    if not isinstance(payload, dict):
        raise TypeError("case specification payload must be a JSON object")
    return _case_spec_from_json(payload)


def c0_two_resource_deadlock() -> tuple[IMSModel, IMSState]:
    """Discovery case C0: two singleton resources in a closed wait."""

    model = IMSModel(
        id="C0-two-resource-minimal",
        resources={
            "r1": Resource("r1", 1),
            "r2": Resource("r2", 1),
        },
        jobs=("j1", "j2"),
    )
    state = IMSState(
        id="c0-deadlocked",
        holds=(Holding("j1", "r1", 1), Holding("j2", "r2", 1)),
        requests={
            "j1": (RequestAlternative((ResourceDemand("r2", 1),)),),
            "j2": (RequestAlternative((ResourceDemand("r1", 1),)),),
        },
        stable=True,
        complete=False,
        event_calendar_empty=True,
        mode_by_job={"j1": "waiting_r2", "j2": "waiting_r1"},
        stage_by_job={"j1": "need_r2", "j2": "need_r1"},
    )
    return model, state


def c1_cycle_insufficient_wip() -> tuple[IMSModel, IMSState]:
    """Discovery case C1: a request cycle with residual capacity."""

    model = IMSModel(
        id="C1-cycle-but-insufficient-wip",
        resources={
            "r1": Resource("r1", 1),
            "r2": Resource("r2", 2),
        },
        jobs=("j1", "j2"),
    )
    state = IMSState(
        id="c1-cycle-not-deadlocked",
        holds=(Holding("j1", "r1", 1), Holding("j2", "r2", 1)),
        requests={
            "j1": (RequestAlternative((ResourceDemand("r2", 1),)),),
            "j2": (RequestAlternative((ResourceDemand("r1", 1),)),),
        },
        stable=True,
        complete=False,
        event_calendar_empty=False,
        mode_by_job={"j1": "waiting_r2", "j2": "waiting_r1"},
        stage_by_job={"j1": "need_r2", "j2": "need_r1"},
    )
    return model, state


def load_builtin_case(case_id: str) -> tuple[IMSModel, IMSState]:
    normalized = case_id.upper()
    if normalized == "C0":
        return c0_two_resource_deadlock()
    if normalized == "C1":
        return c1_cycle_insufficient_wip()
    spec = load_case_spec(case_id)
    return spec.model, spec.initial_state


def list_case_ids(*, root: Path | None = None) -> tuple[str, ...]:
    cases_dir = _CASES_DIR if root is None else root
    if not cases_dir.exists():
        return ()
    return tuple(
        sorted(path.stem.upper() for path in cases_dir.glob("*.json") if path.is_file())
    )


def case_manifest(*, root: Path | None = None) -> tuple[CaseSpec, ...]:
    return tuple(
        load_case_spec(case_id, root=root) for case_id in list_case_ids(root=root)
    )


def _case_spec_from_json(payload: dict[str, Any]) -> CaseSpec:
    schema_version = str(payload["schema_version"])
    if schema_version != CASE_SCHEMA_VERSION:
        msg = (
            f"case schema version {schema_version!r} does not match "
            f"expected {CASE_SCHEMA_VERSION!r}"
        )
        raise ValueError(msg)
    case_id = str(payload["case_id"]).upper()
    if case_id != str(payload["case_id"]):
        msg = "case_id must be uppercase"
        raise ValueError(msg)
    title = str(payload.get("title", case_id))
    status = str(payload.get("status", "DISCOVERY"))
    model = _model_from_json(payload["model"])
    initial_state = _state_from_json(payload["initial_state"])
    model_jobs = set(model.jobs)
    unknown_stage_jobs = sorted(set(initial_state.stage_by_job) - model_jobs)
    if unknown_stage_jobs:
        msg = f"stage_by_job references unknown job {unknown_stage_jobs[0]!r}"
        raise ValueError(msg)
    unknown_mode_jobs = sorted(set(initial_state.mode_by_job) - model_jobs)
    if unknown_mode_jobs:
        msg = f"mode_by_job references unknown job {unknown_mode_jobs[0]!r}"
        raise ValueError(msg)
    validation = validate_model_state(model, initial_state)
    if not validation.valid:
        msg = "; ".join(issue.message for issue in validation.issues)
        raise ValueError(msg)
    transitions = tuple(
        _transition_from_json(item) for item in payload.get("transitions", [])
    )
    calendar = tuple(_calendar_from_json(item) for item in payload.get("calendar", []))
    ctmc_payload = payload.get("ctmc")
    ctmc = _ctmc_from_json(ctmc_payload) if ctmc_payload is not None else None
    if ctmc is None:
        ctmc_provenance = None
        if "ctmc_provenance" in payload:
            msg = "ctmc_provenance is only valid when ctmc is present"
            raise ValueError(msg)
    else:
        ctmc_provenance = str(payload.get("ctmc_provenance", "fixture_unverified"))
        if ctmc_provenance not in {"fixture_unverified", "derived"}:
            msg = f"unsupported CTMC provenance {ctmc_provenance!r}"
            raise ValueError(msg)
    notes = tuple(str(note) for note in payload.get("notes", ()))
    return CaseSpec(
        schema_version=schema_version,
        case_id=case_id,
        title=title,
        status=status,
        model=model,
        initial_state=initial_state,
        transitions=transitions,
        calendar=calendar,
        ctmc=ctmc,
        ctmc_provenance=ctmc_provenance,
        notes=notes,
    )


def _model_from_json(payload: dict[str, Any]) -> IMSModel:
    resources: dict[str, Resource] = {}
    for item in payload["resources"]:
        resource_id = str(item["id"])
        if resource_id in resources:
            msg = f"duplicate resource id {resource_id!r}"
            raise ValueError(msg)
        kind = str(item.get("kind", "machine"))
        if kind not in _ALLOWED_RESOURCE_KINDS:
            msg = f"invalid resource kind {kind!r}"
            raise ValueError(msg)
        resources[resource_id] = Resource(
            id=resource_id,
            capacity=int(item["capacity"]),
            kind=cast(ResourceKind, kind),
        )
    jobs = tuple(str(job) for job in payload["jobs"])
    if len(set(jobs)) != len(jobs):
        msg = "duplicate job id in case model"
        raise ValueError(msg)
    return IMSModel(
        id=str(payload["id"]),
        resources=resources,
        jobs=jobs,
    )


def _state_from_json(payload: dict[str, Any]) -> IMSState:
    holds = tuple(_hold_from_json(item) for item in payload.get("holds", []))
    requests = {
        str(job_id): tuple(
            RequestAlternative(
                tuple(
                    ResourceDemand(str(demand["resource_id"]), int(demand["units"]))
                    for demand in alternative
                )
            )
            for alternative in alternatives
        )
        for job_id, alternatives in payload.get("requests", {}).items()
    }
    completed_jobs = frozenset(str(job) for job in payload.get("completed_jobs", []))
    stage_by_job = {
        str(job_id): str(stage)
        for job_id, stage in payload.get("stage_by_job", {}).items()
    }
    mode_by_job = {
        str(job_id): str(mode)
        for job_id, mode in payload.get("mode_by_job", {}).items()
    }
    return IMSState(
        id=str(payload["id"]),
        holds=holds,
        requests=requests,
        completed_jobs=completed_jobs,
        stable=bool(payload.get("stable", True)),
        complete=bool(payload.get("complete", False)),
        event_calendar_empty=bool(payload.get("event_calendar_empty", False)),
        stage_by_job=stage_by_job,
        mode_by_job=mode_by_job,
        zero_time_trace=tuple(str(item) for item in payload.get("zero_time_trace", [])),
    )


def _transition_from_json(payload: dict[str, Any]) -> TransitionSpec:
    next_requests_present = "next_requests" in payload
    next_requests_payload = payload.get("next_requests", [])
    return TransitionSpec(
        name=str(payload["name"]),
        kind=str(payload["kind"]),
        job_id=str(payload["job_id"]),
        source_mode=str(payload["source_mode"]),
        target_mode=str(payload["target_mode"]),
        controllable=bool(payload["controllable"]),
        zero_time=bool(payload["zero_time"]),
        urgent=bool(payload.get("urgent", False)),
        acquire=tuple(
            ResourceDemand(str(item["resource_id"]), int(item["units"]))
            for item in payload.get("acquire", [])
        ),
        release=tuple(
            ResourceDemand(str(item["resource_id"]), int(item["units"]))
            for item in payload.get("release", [])
        ),
        requires=tuple(
            RequestAlternative(
                tuple(
                    ResourceDemand(str(demand["resource_id"]), int(demand["units"]))
                    for demand in alternative
                )
            )
            for alternative in payload.get("requires", [])
        ),
        clears_requests=next_requests_present and not next_requests_payload,
        next_requests=tuple(
            RequestAlternative(
                tuple(
                    ResourceDemand(str(demand["resource_id"]), int(demand["units"]))
                    for demand in alternative
                )
            )
            for alternative in next_requests_payload
        ),
        mark_complete=bool(payload.get("mark_complete", False)),
    )


def _calendar_from_json(payload: dict[str, Any]) -> ScheduledEvent:
    return ScheduledEvent(
        time=float(payload["time"]),
        name=str(payload["name"]),
        job_id=str(payload["job_id"]),
        kind=str(payload["kind"]),
    )


def _ctmc_from_json(payload: dict[str, Any]) -> AbsorbingCTMC:
    return AbsorbingCTMC(
        transient_states=tuple(str(item) for item in payload["transient_states"]),
        completion_rates={
            (str(source), str(target)): float(rate)
            for source, target, rate in payload.get("completion_rates", [])
        },
        deadlock_rates={
            (str(source), str(target)): float(rate)
            for source, target, rate in payload.get("deadlock_rates", [])
        },
        transient_rates={
            (str(source), str(target)): float(rate)
            for source, target, rate in payload.get("transient_rates", [])
        },
    )


def _ctmc_to_json(ctmc: AbsorbingCTMC) -> dict[str, object]:
    return {
        "transient_states": list(ctmc.transient_states),
        "completion_rates": [
            [source, target, rate]
            for (source, target), rate in sorted(ctmc.completion_rates.items())
        ],
        "deadlock_rates": [
            [source, target, rate]
            for (source, target), rate in sorted(ctmc.deadlock_rates.items())
        ],
        "transient_rates": [
            [source, target, rate]
            for (source, target), rate in sorted(ctmc.transient_rates.items())
        ],
    }


def _model_to_json(model: IMSModel) -> dict[str, object]:
    return {
        "id": model.id,
        "resources": [
            {"id": resource.id, "capacity": resource.capacity, "kind": resource.kind}
            for resource in sorted(model.resources.values(), key=lambda item: item.id)
        ],
        "jobs": list(model.jobs),
    }


def _state_to_json(state: IMSState) -> dict[str, object]:
    return {
        "id": state.id,
        "holds": [_hold_to_json(holding) for holding in state.holds],
        "requests": {
            job_id: [
                [
                    {"resource_id": demand.resource_id, "units": demand.units}
                    for demand in alternative.demands
                ]
                for alternative in alternatives
            ]
            for job_id, alternatives in sorted(state.requests.items())
        },
        "completed_jobs": sorted(state.completed_jobs),
        "stable": state.stable,
        "complete": state.complete,
        "event_calendar_empty": state.event_calendar_empty,
        "stage_by_job": dict(sorted(state.stage_by_job.items())),
        "mode_by_job": dict(sorted(state.mode_by_job.items())),
        "zero_time_trace": list(state.zero_time_trace),
    }


def _transition_to_json(transition: TransitionSpec) -> dict[str, object]:
    payload: dict[str, object] = {
        "name": transition.name,
        "kind": transition.kind,
        "job_id": transition.job_id,
        "source_mode": transition.source_mode,
        "target_mode": transition.target_mode,
        "controllable": transition.controllable,
        "zero_time": transition.zero_time,
        "urgent": transition.urgent,
        "clears_requests": transition.clears_requests,
        "acquire": [
            {"resource_id": demand.resource_id, "units": demand.units}
            for demand in transition.acquire
        ],
        "release": [
            {"resource_id": demand.resource_id, "units": demand.units}
            for demand in transition.release
        ],
        "requires": [
            [
                {"resource_id": demand.resource_id, "units": demand.units}
                for demand in alternative.demands
            ]
            for alternative in transition.requires
        ],
        "mark_complete": transition.mark_complete,
    }
    if transition.clears_requests:
        payload["next_requests"] = []
    elif transition.next_requests:
        payload["next_requests"] = [
            [
                {"resource_id": demand.resource_id, "units": demand.units}
                for demand in alternative.demands
            ]
            for alternative in transition.next_requests
        ]
    return payload


def _calendar_to_json(event: ScheduledEvent) -> dict[str, object]:
    return {
        "time": event.time,
        "name": event.name,
        "job_id": event.job_id,
        "kind": event.kind,
    }


def _hold_from_json(payload: dict[str, Any]) -> Holding:
    return Holding(
        job_id=str(payload["job_id"]),
        resource_id=str(payload["resource_id"]),
        units=int(payload.get("units", 1)),
    )


def _hold_to_json(holding: Holding) -> dict[str, object]:
    return {
        "job_id": holding.job_id,
        "resource_id": holding.resource_id,
        "units": holding.units,
    }


def _no_duplicate_keys_object_pairs_hook(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in pairs:
        if key in payload:
            msg = f"duplicate JSON key {key!r}"
            raise ValueError(msg)
        payload[key] = value
    return payload
