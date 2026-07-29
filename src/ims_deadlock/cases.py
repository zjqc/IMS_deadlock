"""Built-in discovery cases used by tests and CLI smoke checks."""

from __future__ import annotations

from ims_deadlock.model import IMSModel, IMSState, Resource


def c0_two_resource_deadlock() -> tuple[IMSModel, IMSState]:
    """Two jobs hold one singleton resource each and request the other."""

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
        holds={
            "j1": frozenset({"r1"}),
            "j2": frozenset({"r2"}),
        },
        requests={
            "j1": frozenset({"r2"}),
            "j2": frozenset({"r1"}),
        },
        stable=True,
        complete=False,
        event_calendar_empty=True,
    )
    return model, state


def c1_cycle_insufficient_wip() -> tuple[IMSModel, IMSState]:
    """Static cycle exists, but resource `r2` is not saturated."""

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
        holds={
            "j1": frozenset({"r1"}),
            "j2": frozenset({"r2"}),
        },
        requests={
            "j1": frozenset({"r2"}),
            "j2": frozenset({"r1"}),
        },
        stable=True,
        complete=False,
        event_calendar_empty=False,
    )
    return model, state


def load_builtin_case(case_id: str) -> tuple[IMSModel, IMSState]:
    normalized = case_id.upper()
    if normalized == "C0":
        return c0_two_resource_deadlock()
    if normalized == "C1":
        return c1_cycle_insufficient_wip()
    msg = f"unknown built-in case {case_id!r}"
    raise ValueError(msg)

