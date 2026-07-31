"""G6 stopped-process state partitioning for generated stable IMS LTS objects."""

from __future__ import annotations

import hashlib
import json
from collections import deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from math import isfinite
from typing import NoReturn

from ims_deadlock.analysis import StableLTS, enumerate_stable_lts
from ims_deadlock.certificates import (
    enumerate_local_blocking_certificates,
    find_deadlock_certificate,
)
from ims_deadlock.engine import TransitionSpec, configuration_signature
from ims_deadlock.model import IMSModel, IMSState, validate_model_state

TERMINAL_CLASSIFICATION_VERSION = "ims-deadlock/g6-terminal-stopping-partition/v3"
ESTIMAND_SPEC_VERSION = "ims-deadlock/g6-versioned-estimand/v2"
ABSORPTION_DOMAIN_CERTIFICATE_VERSION = (
    "ims-deadlock/g6-absorption-domain-certificate/v1"
)
ABSORPTION_DOMAIN_ALGORITHM_VERSION = "finite-positive-rate-stopped-ctmc-scc-domain/v1"
G6_CTM_GENERATOR_PROVENANCE = "derived_from_g6_terminal_stopping_partition_ims_lts_v3"
SUPPORT_GRAPH_SEMANTICS = "complete_stopped_lts_support"
CERTIFIED_STATUS = "certified_finite_positive_rate_stopped_ctmc"
NOT_CERTIFIED_STATUS = "not_certified"
NO_POLICY_FILTER_DECLARATION = {
    "version": "ims-deadlock/g6-policy-filter-declaration/v1",
    "mode": "no_policy_filter",
    "excluded_plant_arcs": [],
}

_BAD_CLASSES = frozenset({"D_global", "D_local"})
_CLASS_ORDER = ("D_global", "D_local", "F", "R_livelock", "R_terminal")


class TerminalPartitionError(ValueError):
    """Structured refusal for invalid G6 stopping partitions."""

    def __init__(self, code: str, message: str, details: Mapping[str, object]) -> None:
        super().__init__(message)
        self.code = code
        self.details = dict(sorted(details.items()))

    def to_json_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "message": str(self),
            "details": self.details,
        }


@dataclass(frozen=True)
class VersionedEstimandSpec:
    """Versioned CTMC/DES stopping semantics for a G6 state partition."""

    selected_bad_classes: tuple[str, ...] = ("D_global", "D_local")
    success_class: str = "F"
    exact_stopping_rule: str = (
        "exact_absorption_first_hit_selected_bad_union_or_completion_v1"
    )
    des_stopping_rule: str = "des_first_hit_same_absorbing_ctmc_labels_v1"
    policy_analysis_class: str = "P_policy"
    version: str = ESTIMAND_SPEC_VERSION

    def __post_init__(self) -> None:
        if not self.version:
            raise ValueError("version must be nonempty")
        if self.success_class != "F":
            raise ValueError("success_class must be F")
        if len(set(self.selected_bad_classes)) != len(self.selected_bad_classes):
            raise ValueError("duplicate selected bad classes are not allowed")
        if self.success_class in self.selected_bad_classes:
            raise ValueError("selected bad classes must not include the success class")
        unknown = sorted(set(self.selected_bad_classes) - _BAD_CLASSES)
        if unknown:
            raise ValueError(f"unknown selected bad class {unknown[0]!r}")
        ordered = tuple(
            class_name
            for class_name in _CLASS_ORDER
            if class_name in self.selected_bad_classes
        )
        object.__setattr__(self, "selected_bad_classes", ordered)
        if not self.exact_stopping_rule:
            raise ValueError("exact_stopping_rule must be nonempty")
        if not self.des_stopping_rule:
            raise ValueError("des_stopping_rule must be nonempty")
        if self.policy_analysis_class != "P_policy":
            raise ValueError("policy_analysis_class must be P_policy")

    def to_json_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "selected_bad_classes": list(self.selected_bad_classes),
            "success_class": self.success_class,
            "exact_stopping_rule": self.exact_stopping_rule,
            "des_stopping_rule": self.des_stopping_rule,
            "policy_analysis_class": self.policy_analysis_class,
        }


DEFAULT_ESTIMAND_SPEC = VersionedEstimandSpec()


@dataclass(frozen=True)
class AbsorptionDomainCertificate:
    version: str
    algorithm_version: str
    certification_status: str
    reason_codes: tuple[str, ...]
    selected_absorbing_state_ids: tuple[str, ...]
    unselected_closed_sccs: tuple[tuple[str, ...], ...] | None
    closed_class_reverse_basin_state_ids: tuple[str, ...] | None
    s_t_state_ids: tuple[str, ...] | None
    non_almost_sure_absorbing_state_ids: tuple[str, ...] | None
    finite_state_space_verified: bool
    complete_nontruncated_lts_verified: bool
    lts_generation_provenance_verified: bool
    positive_finite_rate_manifest_verified: bool
    selected_target_identity_verified: bool
    policy_filter_identity_verified: bool
    state_space_hash: str
    partition_hash: str
    rate_manifest_hash: str | None
    positive_rate_graph_hash: str | None
    policy_filter_hash: str | None
    absorption_domain_hash: str | None

    def __post_init__(self) -> None:
        if self.version != ABSORPTION_DOMAIN_CERTIFICATE_VERSION:
            raise ValueError("absorption certificate version mismatch")
        if self.algorithm_version != ABSORPTION_DOMAIN_ALGORITHM_VERSION:
            raise ValueError("absorption certificate algorithm version mismatch")
        if self.certification_status == NOT_CERTIFIED_STATUS:
            if not self.reason_codes:
                raise ValueError(
                    "uncertified absorption certificate needs reason codes"
                )
            if (
                self.unselected_closed_sccs is not None
                or self.closed_class_reverse_basin_state_ids is not None
                or self.s_t_state_ids is not None
                or self.non_almost_sure_absorbing_state_ids is not None
                or self.positive_rate_graph_hash is not None
                or self.policy_filter_hash is not None
                or self.absorption_domain_hash is not None
            ):
                raise ValueError("uncertified absorption certificate has derived data")
        elif self.certification_status == CERTIFIED_STATUS:
            if self.reason_codes:
                raise ValueError("certified absorption certificate has reason codes")
            if (
                self.unselected_closed_sccs is None
                or self.closed_class_reverse_basin_state_ids is None
                or self.s_t_state_ids is None
                or self.non_almost_sure_absorbing_state_ids is None
                or self.positive_rate_graph_hash is None
                or self.policy_filter_hash is None
                or self.absorption_domain_hash is None
            ):
                raise ValueError("certified absorption certificate lacks derived data")
        else:
            raise ValueError("unknown absorption certificate status")

    def to_json_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "algorithm_version": self.algorithm_version,
            "certification_status": self.certification_status,
            "reason_codes": list(self.reason_codes),
            "selected_absorbing_state_ids": list(self.selected_absorbing_state_ids),
            "identity": {
                "state_space_hash": self.state_space_hash,
                "partition_hash": self.partition_hash,
                "rate_manifest_hash": self.rate_manifest_hash,
                "positive_rate_graph_hash": self.positive_rate_graph_hash,
                "policy_filter_hash": self.policy_filter_hash,
                "absorption_domain_hash": self.absorption_domain_hash,
            },
            "assumptions": {
                "finite_state_space_verified": self.finite_state_space_verified,
                "complete_nontruncated_lts_verified": (
                    self.complete_nontruncated_lts_verified
                ),
                "lts_generation_provenance_verified": (
                    self.lts_generation_provenance_verified
                ),
                "positive_finite_rate_manifest_verified": (
                    self.positive_finite_rate_manifest_verified
                ),
                "selected_target_identity_verified": (
                    self.selected_target_identity_verified
                ),
                "policy_filter_identity_verified": self.policy_filter_identity_verified,
            },
        }


@dataclass(frozen=True)
class TerminalStoppingPartition:
    """Deterministic G6 partition for first-hit bad/success stopping.

    ``D_local`` is a stopped-process bad hit set. It is not a plant terminal
    SCC and may have outgoing plant-LTS arcs. Only ``R_livelock`` and
    ``R_terminal`` are classified from terminal SCCs of the remaining graph.
    """

    classification_version: str
    estimand_spec: VersionedEstimandSpec
    d_global_state_ids: tuple[str, ...]
    d_local_state_ids: tuple[str, ...]
    f_state_ids: tuple[str, ...]
    r_livelock_state_ids: tuple[str, ...]
    r_terminal_state_ids: tuple[str, ...]
    p_policy_state_ids: tuple[str, ...]
    transient_state_ids: tuple[str, ...]
    selected_reachable_state_ids: tuple[str, ...]
    unreachable_nonabsorbing_state_ids: tuple[str, ...]
    selected_bad_state_ids: tuple[str, ...]
    terminal_sccs: tuple[tuple[str, ...], ...]
    plant_arcs: tuple[tuple[str, str, str], ...]
    declared_transition_event_names: tuple[str, ...]
    state_space_hash: str
    partition_hash: str
    rate_manifest_hash: str | None
    positive_rate_graph_hash: str | None
    policy_filter_hash: str | None
    absorption_domain_hash: str | None
    stopping_rule_hash: str
    des_stopping_rule_hash: str
    estimand_id: str | None
    absorption_domain_certificate: AbsorptionDomainCertificate
    lts_provenance_audit: dict[str, object]
    local_bad_soundness_audit: dict[str, object]
    global_certificates: dict[str, dict[str, object]] = field(default_factory=dict)
    local_certificates: dict[str, list[dict[str, object]]] = field(default_factory=dict)

    def to_json_dict(self) -> dict[str, object]:
        return {
            "classification_version": self.classification_version,
            "estimand": self.estimand_spec.to_json_dict(),
            "classes": {
                "D_global": list(self.d_global_state_ids),
                "D_local": list(self.d_local_state_ids),
                "F": list(self.f_state_ids),
                "R_livelock": list(self.r_livelock_state_ids),
                "R_terminal": list(self.r_terminal_state_ids),
            },
            "policy_analysis_classes": {
                "P_policy": list(self.p_policy_state_ids),
            },
            "derived_state_sets": {
                "S_reach": {
                    "state_ids": list(self.selected_reachable_state_ids),
                    "support_unreachable_state_ids": list(
                        self.unreachable_nonabsorbing_state_ids
                    ),
                    "graph_semantics": SUPPORT_GRAPH_SEMANTICS,
                    "positive_rate_verified": False,
                },
                "S_T": {
                    "state_ids": (
                        list(self.absorption_domain_certificate.s_t_state_ids)
                        if self.absorption_domain_certificate.s_t_state_ids is not None
                        else None
                    ),
                    "certification_status": (
                        self.absorption_domain_certificate.certification_status
                    ),
                    "reason_codes": list(
                        self.absorption_domain_certificate.reason_codes
                    ),
                },
                "unselected_closed_sccs": (
                    [
                        list(component)
                        for component in (
                            self.absorption_domain_certificate.unselected_closed_sccs
                        )
                    ]
                    if self.absorption_domain_certificate.unselected_closed_sccs
                    is not None
                    else None
                ),
                "closed_class_reverse_basin_state_ids": (
                    list(
                        self.absorption_domain_certificate.closed_class_reverse_basin_state_ids
                    )
                    if (
                        self.absorption_domain_certificate.closed_class_reverse_basin_state_ids
                        is not None
                    )
                    else None
                ),
                "non_almost_sure_absorbing_state_ids": (
                    list(
                        self.absorption_domain_certificate.non_almost_sure_absorbing_state_ids
                    )
                    if (
                        self.absorption_domain_certificate.non_almost_sure_absorbing_state_ids
                        is not None
                    )
                    else None
                ),
            },
            "bad_hit_sets": {
                "D_global": list(self.d_global_state_ids),
                "D_local": list(self.d_local_state_ids),
            },
            "selected_bad_state_ids": list(self.selected_bad_state_ids),
            "terminal_sccs": [list(component) for component in self.terminal_sccs],
            "plant_arcs": [list(arc) for arc in self.plant_arcs],
            "declared_transition_event_names": list(
                self.declared_transition_event_names
            ),
            "lts_provenance_audit": self.lts_provenance_audit,
            "local_bad_soundness_audit": self.local_bad_soundness_audit,
            "absorption_domain_certificate": (
                self.absorption_domain_certificate.to_json_dict()
            ),
            "certificates": {
                "global": self.global_certificates,
                "local": self.local_certificates,
            },
            "hashes": self.hashes_json_dict(),
        }

    def plant_partition_json_dict(self) -> dict[str, object]:
        return {
            "classification_version": self.classification_version,
            "classes": {
                "D_global": list(self.d_global_state_ids),
                "D_local": list(self.d_local_state_ids),
                "F": list(self.f_state_ids),
                "R_livelock": list(self.r_livelock_state_ids),
                "R_terminal": list(self.r_terminal_state_ids),
            },
            "bad_hit_sets": {
                "D_global": list(self.d_global_state_ids),
                "D_local": list(self.d_local_state_ids),
            },
            "local_bad_soundness_audit": self.local_bad_soundness_audit,
            "terminal_sccs": [list(component) for component in self.terminal_sccs],
            "plant_arcs": [list(arc) for arc in self.plant_arcs],
            "lts_provenance_audit": self.lts_provenance_audit,
        }

    def hashes_json_dict(self) -> dict[str, str | None]:
        return {
            "state_space_hash": self.state_space_hash,
            "partition_hash": self.partition_hash,
            "rate_manifest_hash": self.rate_manifest_hash,
            "positive_rate_graph_hash": self.positive_rate_graph_hash,
            "policy_filter_hash": self.policy_filter_hash,
            "absorption_domain_hash": self.absorption_domain_hash,
            "stopping_rule_hash": self.stopping_rule_hash,
            "des_stopping_rule_hash": self.des_stopping_rule_hash,
            "estimand_id": self.estimand_id,
        }

    @property
    def transient_arcs(self) -> tuple[tuple[str, str, str], ...]:
        """Compatibility alias for the full plant LTS arcs."""

        return self.plant_arcs


ClosedClassPartition = TerminalStoppingPartition
"""Compatibility alias; only R_* members are plant-LTS terminal SCC classes."""


def partition_stable_lts(
    model: IMSModel,
    stable_lts: StableLTS,
    transitions: Iterable[TransitionSpec],
    *,
    event_rates: Mapping[str, float] | None = None,
    estimand_spec: VersionedEstimandSpec = DEFAULT_ESTIMAND_SPEC,
    require_selected_absorption: bool = False,
    verify_generated_lts: bool = False,
) -> TerminalStoppingPartition:
    """Classify reachable stable states before deriving a stopped estimand."""

    if stable_lts.truncated or stable_lts.truncated_arcs:
        _raise(
            "incomplete_stable_lts",
            "terminal/stopping partition requires a complete nontruncated stable LTS",
            {
                "truncated": stable_lts.truncated,
                "truncated_arc_count": len(stable_lts.truncated_arcs),
            },
        )
    if stable_lts.unavailable_reasons:
        _raise(
            "incomplete_stable_lts",
            "terminal/stopping partition requires an LTS without unavailable branches",
            {"unavailable_reasons": list(stable_lts.unavailable_reasons)},
        )

    rules = tuple(transitions)
    declared_transition_event_names = tuple(
        sorted(transition.name for transition in rules)
    )
    declared_events = set(declared_transition_event_names)
    state_ids = tuple(record.state_id for record in stable_lts.states)
    if len(set(state_ids)) != len(state_ids):
        _raise("duplicate_state_id", "stable LTS contains duplicate state ids", {})
    for record in stable_lts.states:
        validation = validate_model_state(model, record.state)
        if not validation.valid:
            _raise(
                "invalid_lts_state",
                "stable LTS contains a model-invalid state",
                {
                    "state_id": record.state_id,
                    "issues": [issue.to_json_dict() for issue in validation.issues],
                },
            )
    state_set = set(state_ids)
    for arc in stable_lts.transitions:
        if arc.source not in state_set:
            _raise(
                "transition_source_missing",
                "stable LTS transition source is missing",
                {"source": arc.source, "event": arc.event, "target": arc.target},
            )
        if arc.target not in state_set:
            _raise(
                "transition_target_missing",
                "stable LTS transition target is missing",
                {"source": arc.source, "event": arc.event, "target": arc.target},
            )
        if arc.event not in declared_events:
            _raise(
                "unknown_lts_event",
                "stable LTS arc event is absent from supplied transition registry",
                {"source": arc.source, "event": arc.event, "target": arc.target},
            )

    lts_provenance_audit = (
        _verify_generated_lts(model, stable_lts, rules)
        if verify_generated_lts
        else {
            "method": "caller_contract_only",
            "verified": False,
            "state_count": len(stable_lts.states),
            "plant_arc_count": len(stable_lts.transitions),
        }
    )

    f_ids = tuple(
        sorted(record.state_id for record in stable_lts.states if record.state.complete)
    )
    f_set = set(f_ids)
    global_payloads: dict[str, dict[str, object]] = {}
    local_payloads: dict[str, list[dict[str, object]]] = {}
    d_global: list[str] = []
    d_local: list[str] = []
    for record in stable_lts.states:
        if record.state_id in f_set:
            continue
        global_certificate = find_deadlock_certificate(
            model,
            record.state,
            rules,
            reachable_prefix=record.witness,
        )
        if global_certificate is not None:
            d_global.append(record.state_id)
            global_payloads[record.state_id] = global_certificate.to_json_dict()
            continue
        local_certificates = enumerate_local_blocking_certificates(
            model,
            record.state,
            rules,
            reachable_prefix=record.witness,
        )
        if local_certificates:
            d_local.append(record.state_id)
            local_payloads[record.state_id] = [
                certificate.to_json_dict() for certificate in local_certificates
            ]

    completion_counterexamples = _shortest_completion_paths(
        stable_lts,
        source_state_ids=tuple(sorted(d_local)),
        completion_state_ids=f_set,
    )
    if completion_counterexamples:
        _raise(
            "local_core_completion_reachable",
            (
                "a local blocking-kernel candidate can still reach all-batch "
                "completion under the supplied plant transitions"
            ),
            {
                "candidate_state_ids": sorted(completion_counterexamples),
                "completion_state_ids": sorted(
                    {
                        completion_state_id
                        for completion_state_id, _events in (
                            completion_counterexamples.values()
                        )
                    }
                ),
                "counterexample_event_paths": {
                    state_id: list(events)
                    for state_id, (_completion_state_id, events) in sorted(
                        completion_counterexamples.items()
                    )
                },
            },
        )

    d_global_ids = tuple(sorted(d_global))
    d_local_ids = tuple(sorted(d_local))
    local_bad_soundness_audit: dict[str, object] = {
        "method": "complete_lts_completion_nonreachability_v1",
        "verified": True,
        "candidate_state_ids": list(d_local_ids),
        "completion_state_ids": list(f_ids),
        "completion_reachable_candidate_state_ids": [],
    }
    preclassified = f_set | set(d_global_ids) | set(d_local_ids)
    remaining = tuple(
        state_id for state_id in state_ids if state_id not in preclassified
    )
    terminal_sccs, r_terminal_ids, r_livelock_ids = _terminal_scc_classes(
        remaining,
        stable_lts,
    )
    selected_bad = tuple(
        sorted(
            set(
                d_global_ids if "D_global" in estimand_spec.selected_bad_classes else ()
            )
            | set(
                d_local_ids if "D_local" in estimand_spec.selected_bad_classes else ()
            )
        )
    )
    selected_success = f_ids if estimand_spec.success_class == "F" else ()

    all_absorbing = set(selected_bad) | set(selected_success)
    transient_ids = tuple(
        state_id for state_id in state_ids if state_id not in all_absorbing
    )
    selected_reachable_ids = _selected_reachable_nonabsorbing(
        stable_lts,
        selected_absorbing=all_absorbing,
        nonabsorbing=set(transient_ids),
    )
    unreachable_nonabsorbing_ids = tuple(
        state_id
        for state_id in transient_ids
        if state_id not in set(selected_reachable_ids)
    )
    if require_selected_absorption and unreachable_nonabsorbing_ids:
        _raise(
            "unreachable_nonabsorbing_state",
            "nonabsorbing state cannot reach selected bad or success absorption",
            {
                "unreachable_state_ids": list(unreachable_nonabsorbing_ids),
                "terminal_scc_state_ids": sorted(
                    set(r_terminal_ids) | set(r_livelock_ids)
                ),
            },
        )
    plant_arcs = tuple(
        sorted(
            (arc.source, arc.event, arc.target)
            for arc in stable_lts.transitions
            if arc.source in state_set and arc.target in state_set
        )
    )
    state_space_payload = _state_space_payload(stable_lts)
    partition_payload = {
        "classification_version": TERMINAL_CLASSIFICATION_VERSION,
        "classes": {
            "D_global": list(d_global_ids),
            "D_local": list(d_local_ids),
            "F": list(f_ids),
            "R_livelock": list(r_livelock_ids),
            "R_terminal": list(r_terminal_ids),
        },
        "bad_hit_sets": {
            "D_global": list(d_global_ids),
            "D_local": list(d_local_ids),
        },
        "local_bad_soundness_audit": local_bad_soundness_audit,
        "terminal_sccs": [list(component) for component in terminal_sccs],
        "plant_arcs": [list(arc) for arc in plant_arcs],
        "lts_provenance_audit": lts_provenance_audit,
    }
    state_space_hash = _canonical_sha256(state_space_payload)
    partition_hash = _canonical_sha256(partition_payload)
    rate_manifest = _validated_rate_manifest(
        event_rates,
        declared_transition_event_names=declared_transition_event_names,
    )
    rate_manifest_hash = (
        _canonical_sha256(rate_manifest) if rate_manifest is not None else None
    )
    positive_rate_graph_hash = None
    policy_filter_hash = None
    absorption_domain_hash = None
    common_stopping_spec = {
        "version": estimand_spec.version,
        "selected_bad_classes": list(estimand_spec.selected_bad_classes),
        "success_class": estimand_spec.success_class,
        "policy_analysis_class": estimand_spec.policy_analysis_class,
    }
    stopping_rule_hash = _canonical_sha256(
        {
            **common_stopping_spec,
            "exact_stopping_rule": estimand_spec.exact_stopping_rule,
        }
    )
    des_stopping_rule_hash = _canonical_sha256(
        {
            **common_stopping_spec,
            "des_stopping_rule": estimand_spec.des_stopping_rule,
        }
    )
    estimand_id = None
    absorption_domain_certificate = _uncertified_absorption_domain_certificate(
        selected_absorbing_state_ids=tuple(sorted(all_absorbing)),
        state_space_hash=state_space_hash,
        partition_hash=partition_hash,
        rate_manifest_hash=rate_manifest_hash,
        reason_codes=(
            ("rate_manifest_absent",)
            if rate_manifest is None
            else ("absorption_domain_not_certified",)
        ),
        lts_generation_provenance_verified=bool(lts_provenance_audit.get("verified")),
    )
    return TerminalStoppingPartition(
        classification_version=TERMINAL_CLASSIFICATION_VERSION,
        estimand_spec=estimand_spec,
        d_global_state_ids=d_global_ids,
        d_local_state_ids=tuple(sorted(d_local_ids)),
        f_state_ids=f_ids,
        r_livelock_state_ids=tuple(sorted(r_livelock_ids)),
        r_terminal_state_ids=tuple(sorted(r_terminal_ids)),
        p_policy_state_ids=(),
        transient_state_ids=transient_ids,
        selected_reachable_state_ids=selected_reachable_ids,
        unreachable_nonabsorbing_state_ids=unreachable_nonabsorbing_ids,
        selected_bad_state_ids=selected_bad,
        terminal_sccs=terminal_sccs,
        plant_arcs=plant_arcs,
        declared_transition_event_names=declared_transition_event_names,
        state_space_hash=state_space_hash,
        partition_hash=partition_hash,
        rate_manifest_hash=rate_manifest_hash,
        positive_rate_graph_hash=positive_rate_graph_hash,
        policy_filter_hash=policy_filter_hash,
        absorption_domain_hash=absorption_domain_hash,
        stopping_rule_hash=stopping_rule_hash,
        des_stopping_rule_hash=des_stopping_rule_hash,
        estimand_id=estimand_id,
        absorption_domain_certificate=absorption_domain_certificate,
        lts_provenance_audit=lts_provenance_audit,
        local_bad_soundness_audit=local_bad_soundness_audit,
        global_certificates=dict(sorted(global_payloads.items())),
        local_certificates=dict(sorted(local_payloads.items())),
    )


def _verify_generated_lts(
    model: IMSModel,
    stable_lts: StableLTS,
    rules: tuple[TransitionSpec, ...],
) -> dict[str, object]:
    """Re-enumerate a single-initial LTS and verify exact plant semantics."""

    if len(stable_lts.initial_state_ids) != 1:
        _raise(
            "lts_generation_provenance_unavailable",
            "generated-LTS verification requires exactly one stable initial state",
            {"initial_state_ids": list(stable_lts.initial_state_ids)},
        )
    record_by_id = {record.state_id: record for record in stable_lts.states}
    initial_state_id = stable_lts.initial_state_ids[0]
    initial_record = record_by_id.get(initial_state_id)
    if initial_record is None:
        _raise(
            "lts_generation_provenance_unavailable",
            "stable initial state is absent from the LTS state records",
            {"initial_state_id": initial_state_id},
        )

    regenerated = enumerate_stable_lts(
        model,
        initial_record.state,
        rules,
        max_states=max(1, len(stable_lts.states) + 1),
    )
    original_state_signatures = _state_signatures(stable_lts)
    regenerated_state_signatures = _state_signatures(regenerated)
    state_space_match = (
        not regenerated.truncated
        and not regenerated.unavailable_reasons
        and len(original_state_signatures) == len(stable_lts.states)
        and len(regenerated_state_signatures) == len(regenerated.states)
        and len(stable_lts.states) == len(regenerated.states)
        and original_state_signatures == regenerated_state_signatures
    )
    original_arcs = _semantic_arcs(stable_lts)
    regenerated_arcs = _semantic_arcs(regenerated)
    plant_arc_match = (
        len(original_arcs) == len(stable_lts.transitions)
        and len(regenerated_arcs) == len(regenerated.transitions)
        and original_arcs == regenerated_arcs
    )
    initial_match = len(regenerated.initial_state_ids) == 1 and _state_signature(
        initial_record.state
    ) == _state_signature(
        {record.state_id: record for record in regenerated.states}[
            regenerated.initial_state_ids[0]
        ].state
    )
    if not state_space_match or not plant_arc_match or not initial_match:
        _raise(
            "lts_generation_mismatch",
            "stable LTS does not match deterministic re-enumeration",
            {
                "state_space_match": state_space_match,
                "plant_arc_match": plant_arc_match,
                "initial_state_match": initial_match,
                "original_state_count": len(stable_lts.states),
                "regenerated_state_count": len(regenerated.states),
                "original_plant_arc_count": len(stable_lts.transitions),
                "regenerated_plant_arc_count": len(regenerated.transitions),
                "regenerated_truncated": regenerated.truncated,
                "regenerated_unavailable_reasons": list(
                    regenerated.unavailable_reasons
                ),
            },
        )
    return {
        "method": "deterministic_reenumeration_from_stable_initial_v1",
        "verified": True,
        "state_count": len(stable_lts.states),
        "plant_arc_count": len(stable_lts.transitions),
    }


def _state_signature(state: IMSState) -> tuple[object, ...]:
    return configuration_signature(state) + (
        state.stable,
        state.complete,
        state.event_calendar_empty,
    )


def _state_signatures(stable_lts: StableLTS) -> frozenset[tuple[object, ...]]:
    return frozenset(_state_signature(record.state) for record in stable_lts.states)


def _semantic_arcs(
    stable_lts: StableLTS,
) -> frozenset[
    tuple[tuple[object, ...], str, tuple[object, ...], bool, tuple[str, ...]]
]:
    state_by_id = {record.state_id: record.state for record in stable_lts.states}
    return frozenset(
        (
            _state_signature(state_by_id[arc.source]),
            arc.event,
            _state_signature(state_by_id[arc.target]),
            arc.controllable,
            arc.edge_trace,
        )
        for arc in stable_lts.transitions
    )


def _shortest_completion_paths(
    stable_lts: StableLTS,
    *,
    source_state_ids: tuple[str, ...],
    completion_state_ids: set[str],
) -> dict[str, tuple[str, tuple[str, ...]]]:
    """Return deterministic shortest completion counterexamples for local hits."""

    if not source_state_ids or not completion_state_ids:
        return {}
    adjacency: dict[str, list[tuple[str, str]]] = {}
    for arc in stable_lts.transitions:
        adjacency.setdefault(arc.source, []).append((arc.event, arc.target))
    for source, arcs in adjacency.items():
        adjacency[source] = sorted(arcs, key=lambda item: (item[0], item[1]))

    counterexamples: dict[str, tuple[str, tuple[str, ...]]] = {}
    for source in source_state_ids:
        queue: deque[tuple[str, tuple[str, ...]]] = deque([(source, ())])
        visited = {source}
        while queue:
            state_id, event_path = queue.popleft()
            if state_id in completion_state_ids:
                counterexamples[source] = (state_id, event_path)
                break
            for event, target in adjacency.get(state_id, ()):
                if target in visited:
                    continue
                visited.add(target)
                queue.append((target, event_path + (event,)))
    return counterexamples


def _terminal_scc_classes(
    state_ids: tuple[str, ...],
    stable_lts: StableLTS,
) -> tuple[tuple[tuple[str, ...], ...], tuple[str, ...], tuple[str, ...]]:
    state_set = set(state_ids)
    adjacency = {state_id: set[str]() for state_id in state_ids}
    for arc in stable_lts.transitions:
        if arc.source in state_set and arc.target in state_set:
            adjacency[arc.source].add(arc.target)
    components = _strong_components(adjacency)
    terminal_components: list[tuple[str, ...]] = []
    r_terminal: list[str] = []
    r_livelock: list[str] = []
    for component in components:
        component_set = set(component)
        has_outside = any(
            arc.source in component_set and arc.target not in component_set
            for arc in stable_lts.transitions
        )
        if has_outside:
            continue
        terminal_components.append(component)
        has_self_loop = any(
            arc.source == arc.target and arc.source in component_set
            for arc in stable_lts.transitions
        )
        if len(component) == 1 and not has_self_loop and not adjacency[component[0]]:
            r_terminal.extend(component)
        else:
            r_livelock.extend(component)
    return (
        tuple(sorted(terminal_components)),
        tuple(sorted(r_terminal)),
        tuple(sorted(r_livelock)),
    )


def _strong_components(
    adjacency: Mapping[str, set[str]],
) -> tuple[tuple[str, ...], ...]:
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    components: list[tuple[str, ...]] = []

    def connect(state_id: str) -> None:
        nonlocal index
        indices[state_id] = index
        lowlinks[state_id] = index
        index += 1
        stack.append(state_id)
        on_stack.add(state_id)
        for target in sorted(adjacency[state_id]):
            if target not in indices:
                connect(target)
                lowlinks[state_id] = min(lowlinks[state_id], lowlinks[target])
            elif target in on_stack:
                lowlinks[state_id] = min(lowlinks[state_id], indices[target])
        if lowlinks[state_id] != indices[state_id]:
            return
        component: list[str] = []
        while True:
            target = stack.pop()
            on_stack.remove(target)
            component.append(target)
            if target == state_id:
                break
        components.append(tuple(sorted(component)))

    for state_id in sorted(adjacency):
        if state_id not in indices:
            connect(state_id)
    return tuple(sorted(components))


def _selected_reachable_nonabsorbing(
    stable_lts: StableLTS,
    *,
    selected_absorbing: set[str],
    nonabsorbing: set[str],
) -> tuple[str, ...]:
    reverse: dict[str, set[str]] = {
        record.state_id: set() for record in stable_lts.states
    }
    for arc in stable_lts.transitions:
        reverse.setdefault(arc.target, set()).add(arc.source)
    can_reach = set(selected_absorbing)
    stack = list(selected_absorbing)
    while stack:
        current = stack.pop()
        for source in sorted(reverse.get(current, ())):
            if source in can_reach:
                continue
            can_reach.add(source)
            stack.append(source)
    return tuple(sorted(state_id for state_id in can_reach if state_id in nonabsorbing))


def _uncertified_absorption_domain_certificate(
    *,
    selected_absorbing_state_ids: tuple[str, ...],
    state_space_hash: str,
    partition_hash: str,
    rate_manifest_hash: str | None,
    reason_codes: tuple[str, ...],
    lts_generation_provenance_verified: bool,
) -> AbsorptionDomainCertificate:
    if not reason_codes:
        raise ValueError("uncertified absorption certificate needs reason codes")
    return AbsorptionDomainCertificate(
        version=ABSORPTION_DOMAIN_CERTIFICATE_VERSION,
        algorithm_version=ABSORPTION_DOMAIN_ALGORITHM_VERSION,
        certification_status=NOT_CERTIFIED_STATUS,
        reason_codes=tuple(sorted(reason_codes)),
        selected_absorbing_state_ids=tuple(sorted(selected_absorbing_state_ids)),
        unselected_closed_sccs=None,
        closed_class_reverse_basin_state_ids=None,
        s_t_state_ids=None,
        non_almost_sure_absorbing_state_ids=None,
        finite_state_space_verified=True,
        complete_nontruncated_lts_verified=True,
        lts_generation_provenance_verified=lts_generation_provenance_verified,
        positive_finite_rate_manifest_verified=rate_manifest_hash is not None,
        selected_target_identity_verified=True,
        policy_filter_identity_verified=False,
        state_space_hash=state_space_hash,
        partition_hash=partition_hash,
        rate_manifest_hash=rate_manifest_hash,
        positive_rate_graph_hash=None,
        policy_filter_hash=None,
        absorption_domain_hash=None,
    )


def _validated_rate_manifest(
    event_rates: Mapping[str, float] | None,
    *,
    declared_transition_event_names: tuple[str, ...],
) -> dict[str, float] | None:
    if event_rates is None:
        return None
    rates: dict[str, float] = {}
    for event, rate in sorted(event_rates.items()):
        if isinstance(rate, bool) or not isinstance(rate, int | float):
            _raise(
                "invalid_event_rate",
                "event rate must be a positive finite number",
                {"event": event, "rate": repr(rate)},
            )
        value = float(rate)
        if not isfinite(value) or value <= 0.0:
            _raise(
                "invalid_event_rate",
                "event rate must be a positive finite number",
                {"event": event, "rate": repr(rate)},
            )
        rates[str(event)] = value
    declared_events = set(declared_transition_event_names)
    for event in declared_transition_event_names:
        if event not in rates:
            _raise(
                "missing_event_rate",
                "event rate manifest is missing a declared transition event",
                {"event": event},
            )
    for event in sorted(set(rates) - declared_events):
        _raise(
            "unexpected_event_rate",
            "event rate manifest includes an undeclared transition event",
            {"event": event},
        )
    return rates


def _validate_selected_absorption(
    stable_lts: StableLTS,
    *,
    selected_bad: set[str],
    selected_success: set[str],
    classified_closed: set[str],
) -> None:
    selected = selected_bad | selected_success
    can_reach = set(selected) | set(
        _selected_reachable_nonabsorbing(
            stable_lts,
            selected_absorbing=selected,
            nonabsorbing={record.state_id for record in stable_lts.states} - selected,
        )
    )
    bad = sorted(
        state_id
        for state_id in classified_closed
        if state_id not in selected and state_id not in can_reach
    )
    if bad:
        _raise(
            "unselected_closed_class_unreachable_to_estimand",
            "reachable unselected closed class cannot reach selected bad or success",
            {"state_ids": bad},
        )


def _state_space_payload(stable_lts: StableLTS) -> dict[str, object]:
    return {
        "initial_state_ids": list(stable_lts.initial_state_ids),
        "states": [
            {
                "state_id": record.state_id,
                "source_state_id": record.state.id,
                "complete": record.state.complete,
                "signature": _jsonable(record.signature),
                "witness": list(record.witness),
            }
            for record in stable_lts.states
        ],
        "transitions": [
            {
                "source": arc.source,
                "event": arc.event,
                "target": arc.target,
                "controllable": arc.controllable,
                "edge_trace": list(arc.edge_trace),
            }
            for arc in stable_lts.transitions
        ],
        "truncated": stable_lts.truncated,
        "unavailable_reasons": list(stable_lts.unavailable_reasons),
    }


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, frozenset):
        return sorted((_jsonable(item) for item in value), key=repr)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in sorted(value.items())}
    return value


def _canonical_sha256(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _raise(code: str, message: str, details: Mapping[str, object]) -> NoReturn:
    raise TerminalPartitionError(code, message, details)
