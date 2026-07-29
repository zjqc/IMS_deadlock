from dataclasses import replace
from typing import Any, cast

import pytest

from ims_deadlock.cases import c0_two_resource_deadlock, load_case_spec
from ims_deadlock.certificates import find_deadlock_certificate
from ims_deadlock.model import (
    EvidenceEdge,
    Holding,
    IMSModel,
    IMSState,
    RequestAlternative,
    Resource,
    ResourceDemand,
)
from ims_deadlock.petri import (
    PetriTransition,
    WaitSnapshotNet,
    build_wait_snapshot_bridge,
    certificate_with_wait_snapshot_bridge,
    is_siphon,
    minimal_empty_siphons,
)


def test_c0_builds_exact_wait_snapshot_siphon_bridge() -> None:
    model, state = c0_two_resource_deadlock()
    certificate = find_deadlock_certificate(
        model,
        state,
        reachable_prefix=("start_j1", "start_j2", "finish_j1", "finish_j2"),
    )

    assert certificate is not None
    result = build_wait_snapshot_bridge(model, state, certificate)

    assert result.applicable is True
    assert result.exact is True
    assert result.reason == "ims_sip1_assumptions_satisfied"
    assert result.core_jobs == ("j1", "j2")
    assert result.core_resources == ("r1", "r2")
    assert result.siphon_places == ("free:r1", "free:r2")
    assert result.empty is True
    assert result.minimal is True
    assert result.net == WaitSnapshotNet(
        places=("free:r1", "free:r2"),
        transitions=(
            PetriTransition("t:j1", ("free:r2",), ("free:r1",)),
            PetriTransition("t:j2", ("free:r1",), ("free:r2",)),
        ),
        marking={"free:r1": 0, "free:r2": 0},
    )
    assert is_siphon(result.net, result.siphon_places)
    assert minimal_empty_siphons(result.net) == (("free:r1", "free:r2"),)


def test_wait_snapshot_marking_is_immutable_after_construction() -> None:
    net = WaitSnapshotNet(
        places=("free:r1",),
        transitions=(),
        marking={"free:r1": 0},
    )
    marking = cast("Any", net.marking)

    with pytest.raises(TypeError):
        marking["free:r1"] = 1

    assert net.to_json_dict()["marking"] == {"free:r1": 0}


def test_bridge_helper_embeds_exact_wait_snapshot_payload_in_certificate() -> None:
    model, state = c0_two_resource_deadlock()

    certificate = find_deadlock_certificate(
        model,
        state,
        reachable_prefix=("start_j1", "start_j2"),
    )

    assert certificate is not None
    bridged_certificate = certificate_with_wait_snapshot_bridge(
        model, state, certificate
    )
    payload = bridged_certificate.to_json_dict()
    assert payload["bridge_status"] == "exact_ims_sip1_wait_snapshot_duality"
    assert payload["corresponding_siphon"] == {
        "type": "state_induced_wait_snapshot",
        "places": ["free:r1", "free:r2"],
        "empty": True,
        "minimal": True,
        "core_jobs": ["j1", "j2"],
        "core_resources": ["r1", "r2"],
    }


def test_bridge_rejects_conjunctive_c5_request_without_fabricating_siphon() -> None:
    spec = load_case_spec("C5")
    certificate = find_deadlock_certificate(
        spec.model,
        spec.initial_state,
        reachable_prefix=("reachable_c5_fixture_state",),
    )

    assert certificate is not None
    result = build_wait_snapshot_bridge(spec.model, spec.initial_state, certificate)

    assert result.applicable is False
    assert result.exact is False
    assert result.net is None
    assert result.corresponding_siphon_json() is None
    assert result.reason == "job pA alternative 0 has conjunctive demand"


def test_bridge_requires_reachability_witness_and_minimal_certificate() -> None:
    model, state = c0_two_resource_deadlock()
    no_prefix_certificate = find_deadlock_certificate(model, state)

    assert no_prefix_certificate is not None
    no_prefix_result = build_wait_snapshot_bridge(model, state, no_prefix_certificate)
    assert no_prefix_result.applicable is False
    assert no_prefix_result.reason == "certificate has no reachability witness"

    reachable_certificate = find_deadlock_certificate(model, state, reachable_prefix=())

    assert reachable_certificate is not None
    non_minimal_certificate = replace(reachable_certificate, is_minimal=False)
    non_minimal_result = build_wait_snapshot_bridge(
        model, state, non_minimal_certificate
    )
    assert non_minimal_result.applicable is False
    assert non_minimal_result.reason == "certificate is not inclusion-minimal"


def test_bridge_rejects_or_alternatives_and_multi_capacity_resources() -> None:
    or_model = IMSModel(
        id="or-not-sip1",
        resources={
            "r1": Resource("r1", 1),
            "r2": Resource("r2", 1),
            "r3": Resource("r3", 1),
        },
        jobs=("j1", "j2", "j3"),
    )
    or_state = IMSState(
        id="or-blocked",
        holds=(
            Holding("j1", "r1"),
            Holding("j2", "r2"),
            Holding("j3", "r3"),
        ),
        requests={
            "j1": (
                RequestAlternative((ResourceDemand("r2"),)),
                RequestAlternative((ResourceDemand("r3"),)),
            ),
            "j2": (RequestAlternative((ResourceDemand("r1"),)),),
            "j3": (RequestAlternative((ResourceDemand("r1"),)),),
        },
        stable=True,
        complete=False,
        event_calendar_empty=True,
    )
    or_certificate = find_deadlock_certificate(
        or_model, or_state, reachable_prefix=("reach_or_fixture",)
    )

    assert or_certificate is not None
    or_result = build_wait_snapshot_bridge(or_model, or_state, or_certificate)
    assert or_result.applicable is False
    assert or_result.reason == "job j1 has OR alternatives"

    capacity_model = IMSModel(
        id="capacity-not-sip1",
        resources={"buf": Resource("buf", 2, "buffer")},
        jobs=("j1",),
    )
    capacity_state = IMSState(
        id="capacity-blocked",
        holds=(Holding("j1", "buf", 2),),
        requests={"j1": (RequestAlternative((ResourceDemand("buf"),)),)},
        stable=True,
        complete=False,
        event_calendar_empty=True,
    )
    capacity_certificate = find_deadlock_certificate(
        capacity_model,
        capacity_state,
        reachable_prefix=("reach_capacity_fixture",),
    )

    assert capacity_certificate is not None
    capacity_result = build_wait_snapshot_bridge(
        capacity_model, capacity_state, capacity_certificate
    )
    assert capacity_result.applicable is False
    assert capacity_result.reason == "resource buf capacity 2 is not unit capacity"


def test_control_only_empty_siphon_has_no_inverse_ims_core_mapping() -> None:
    control_net = WaitSnapshotNet(
        places=("approval",),
        transitions=(
            PetriTransition(
                "approval-self-loop",
                inputs=("approval",),
                outputs=("approval",),
            ),
        ),
        marking={"approval": 0},
    )

    assert minimal_empty_siphons(control_net) == (("approval",),)
    assert is_siphon(control_net, ("approval",)) is True
    assert not control_net.places[0].startswith("free:")


def test_bridge_rejects_certificate_evidence_that_disagrees_with_state() -> None:
    model, state = c0_two_resource_deadlock()
    certificate = find_deadlock_certificate(model, state, reachable_prefix=())

    assert certificate is not None
    malformed = replace(
        certificate,
        evidence_edges=(
            EvidenceEdge("hold", "r2", "j1", 1),
            EvidenceEdge("hold", "r1", "j2", 1),
            EvidenceEdge("request", "j1", "r2", 1),
            EvidenceEdge("request", "j2", "r1", 1),
        ),
    )

    result = build_wait_snapshot_bridge(model, state, malformed)

    assert result.applicable is False
    assert result.exact is False
    assert result.corresponding_siphon_json() is None
    assert result.reason == "certificate evidence disagrees with model state"
