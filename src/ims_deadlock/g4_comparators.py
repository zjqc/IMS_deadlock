"""Narrow, auditable G4 comparator primitives.

The functions in this module deliberately do not reproduce the source
algorithms cited by the G4 protocol.  They validate frozen interoperability
evidence or solve a smaller, explicitly stated finite problem.
"""

from __future__ import annotations

import re
from collections import deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from itertools import combinations
from typing import Literal

from ims_deadlock.engine import FiniteLTS, TransitionArc

CRPClassification = Literal[
    "agreement",
    "unreachable_candidate",
    "not_applicable",
    "incomplete_evidence",
    "evidence_disagreement",
]
L30Classification = Literal[
    "sufficient_conditions_satisfied",
    "not_certified",
    "not_applicable",
]
MonitorCoverClassification = Literal[
    "optimal_over_supplied_candidates",
    "infeasible_over_supplied_candidates",
]


@dataclass(frozen=True)
class RecorderTargetResult:
    """Exact reachability result for a predeclared output-counter target."""

    target_state: str
    fixed_counts: tuple[tuple[str, int], ...]
    original_target_reachable: bool
    fixed_target_reachable: bool
    shortest_original_witness: tuple[str, ...]
    shortest_fixed_witness: tuple[str, ...]
    explored_augmented_states: int
    source_algorithm_reproduced: bool = False
    claim_scope: str = "finite_lts_output_counter_augmentation"

    def to_json_dict(self) -> dict[str, object]:
        return {
            "target_state": self.target_state,
            "fixed_counts": dict(self.fixed_counts),
            "original_target_reachable": self.original_target_reachable,
            "fixed_target_reachable": self.fixed_target_reachable,
            "shortest_original_witness": list(self.shortest_original_witness),
            "shortest_fixed_witness": list(self.shortest_fixed_witness),
            "explored_augmented_states": self.explored_augmented_states,
            "source_algorithm_reproduced": self.source_algorithm_reproduced,
            "claim_scope": self.claim_scope,
        }


@dataclass(frozen=True)
class CRPEvidenceProfile:
    """Frozen L31 interoperability evidence supplied by an external encoding."""

    s4pr_applicable: bool
    embedding_sha256: str | None
    crp_pairs: tuple[tuple[str, str], ...]
    translated_target_state: str | None
    external_prefix_claimed: bool | None
    outside_s4pr_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if len(set(self.crp_pairs)) != len(self.crp_pairs):
            raise ValueError("supplied CRP pairs must be unique")
        if any(not place or not resource for place, resource in self.crp_pairs):
            raise ValueError("supplied CRP pair members must be nonempty")
        if len(set(self.outside_s4pr_reasons)) != len(self.outside_s4pr_reasons):
            raise ValueError("outside-S4PR reasons must be unique")
        if any(not reason for reason in self.outside_s4pr_reasons):
            raise ValueError("outside-S4PR reasons must be nonempty")
        object.__setattr__(self, "crp_pairs", tuple(sorted(self.crp_pairs)))
        object.__setattr__(
            self,
            "outside_s4pr_reasons",
            tuple(sorted(self.outside_s4pr_reasons)),
        )


@dataclass(frozen=True)
class CRPEvidenceAudit:
    """Independent finite-LTS audit of a supplied CRP evidence profile."""

    classification: CRPClassification
    independent_target_reachable: bool | None
    independent_witness: tuple[str, ...]
    reasons: tuple[str, ...]
    source_algorithm_reproduced: bool = False
    claim_scope: str = "supplied_crp_interoperability_evidence"

    def to_json_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "independent_target_reachable": self.independent_target_reachable,
            "independent_witness": list(self.independent_witness),
            "reasons": list(self.reasons),
            "source_algorithm_reproduced": self.source_algorithm_reproduced,
            "claim_scope": self.claim_scope,
        }


@dataclass(frozen=True)
class IntegerLinearInequality:
    """One externally supplied integer inequality ``a*x >= rhs``."""

    name: str
    coefficients: tuple[tuple[str, int], ...]
    rhs: int

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("inequality name must be nonempty")
        if isinstance(self.rhs, bool) or not isinstance(self.rhs, int):
            raise TypeError("inequality rhs must be an integer")
        if not self.coefficients:
            raise ValueError("inequality coefficients must be nonempty")
        variable_names = tuple(name for name, _coefficient in self.coefficients)
        if any(not name for name in variable_names):
            raise ValueError("inequality variable names must be nonempty")
        if len(set(variable_names)) != len(variable_names):
            raise ValueError("inequality variables must be unique")
        for _name, coefficient in self.coefficients:
            if isinstance(coefficient, bool) or not isinstance(coefficient, int):
                raise TypeError("inequality coefficients must be integers")
        object.__setattr__(
            self,
            "coefficients",
            tuple(sorted(self.coefficients)),
        )


@dataclass(frozen=True)
class L30SufficientCheck:
    """Evaluation of supplied L30-style sufficient inequalities only."""

    applicable: bool
    classification: L30Classification
    sufficient_conditions_satisfied: bool | None
    evaluations: tuple[tuple[str, int, int, bool], ...]
    reasons: tuple[str, ...]
    exact_ims_threshold_claimed: bool = False
    source_algorithm_reproduced: bool = False
    claim_scope: str = "supplied_sufficient_inequalities"

    def to_json_dict(self) -> dict[str, object]:
        return {
            "applicable": self.applicable,
            "classification": self.classification,
            "sufficient_conditions_satisfied": (self.sufficient_conditions_satisfied),
            "evaluations": [
                {
                    "name": name,
                    "lhs": lhs,
                    "rhs": rhs,
                    "satisfied": satisfied,
                }
                for name, lhs, rhs, satisfied in self.evaluations
            ],
            "reasons": list(self.reasons),
            "exact_ims_threshold_claimed": self.exact_ims_threshold_claimed,
            "source_algorithm_reproduced": self.source_algorithm_reproduced,
            "claim_scope": self.claim_scope,
        }


@dataclass(frozen=True)
class CandidateMonitor:
    """One already-generated candidate monitor represented by its state cover."""

    monitor_id: str
    covered_bad_states: tuple[str, ...]
    excluded_legal_states: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.monitor_id:
            raise ValueError("candidate monitor id must be nonempty")
        if len(set(self.covered_bad_states)) != len(self.covered_bad_states):
            raise ValueError("candidate covered bad states must be unique")
        if len(set(self.excluded_legal_states)) != len(self.excluded_legal_states):
            raise ValueError("candidate excluded legal states must be unique")
        object.__setattr__(
            self,
            "covered_bad_states",
            tuple(sorted(self.covered_bad_states)),
        )
        object.__setattr__(
            self,
            "excluded_legal_states",
            tuple(sorted(self.excluded_legal_states)),
        )


@dataclass(frozen=True)
class AdaptedMonitorCoverResult:
    """Exact cover result over the supplied candidate-monitor set."""

    classification: MonitorCoverClassification
    selected_monitor_ids: tuple[str, ...]
    minimum_cardinality: int | None
    all_bad_states_covered: bool
    all_legal_states_preserved: bool
    examined_subsets: int
    source_algorithm_reproduced: bool = False
    optimality_scope: str = "supplied_candidate_monitor_set"
    claim_scope: str = "adapted_candidate_monitor_cover"

    def to_json_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "selected_monitor_ids": list(self.selected_monitor_ids),
            "minimum_cardinality": self.minimum_cardinality,
            "all_bad_states_covered": self.all_bad_states_covered,
            "all_legal_states_preserved": self.all_legal_states_preserved,
            "examined_subsets": self.examined_subsets,
            "source_algorithm_reproduced": self.source_algorithm_reproduced,
            "optimality_scope": self.optimality_scope,
            "claim_scope": self.claim_scope,
        }


def fixed_recorder_target_reachability(
    lts: FiniteLTS,
    *,
    target_state: str,
    recorder_events: tuple[str, ...],
    fixed_counts: Mapping[str, int],
) -> RecorderTargetResult:
    """Solve a fixed output-counter target by complete augmented-state BFS."""

    _validate_finite_lts(lts)
    if target_state not in lts.states:
        raise ValueError("recorder target state must belong to the LTS")
    if len(set(recorder_events)) != len(recorder_events):
        raise ValueError("recorder events must be unique")
    normalized_events = tuple(sorted(recorder_events))
    if set(fixed_counts) != set(normalized_events):
        raise ValueError("fixed count keys must exactly match recorder events")
    normalized_counts: list[tuple[str, int]] = []
    for event in normalized_events:
        count = fixed_counts[event]
        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError("fixed recorder counts must be integers")
        if count < 0:
            raise ValueError("fixed recorder counts must be nonnegative")
        normalized_counts.append((event, count))
    fixed_count_tuple = tuple(normalized_counts)

    original_witness = _shortest_state_witness(lts, target_state)
    fixed_witness, explored = _shortest_augmented_witness(
        lts,
        target_state=target_state,
        recorder_events=normalized_events,
        fixed_counts=tuple(count for _event, count in fixed_count_tuple),
    )
    return RecorderTargetResult(
        target_state=target_state,
        fixed_counts=fixed_count_tuple,
        original_target_reachable=original_witness is not None,
        fixed_target_reachable=fixed_witness is not None,
        shortest_original_witness=original_witness or (),
        shortest_fixed_witness=fixed_witness or (),
        explored_augmented_states=explored,
    )


def audit_crp_evidence(
    lts: FiniteLTS,
    profile: CRPEvidenceProfile,
) -> CRPEvidenceAudit:
    """Audit supplied L31/CRP interoperability evidence with an LTS oracle."""

    _validate_finite_lts(lts)
    if not profile.s4pr_applicable:
        if not profile.outside_s4pr_reasons:
            return CRPEvidenceAudit(
                classification="incomplete_evidence",
                independent_target_reachable=None,
                independent_witness=(),
                reasons=("outside-S4PR classification requires a reason",),
            )
        return CRPEvidenceAudit(
            classification="not_applicable",
            independent_target_reachable=None,
            independent_witness=(),
            reasons=tuple(sorted(profile.outside_s4pr_reasons)),
        )

    missing: list[str] = []
    if (
        profile.embedding_sha256 is None
        or re.fullmatch(r"[0-9a-f]{64}", profile.embedding_sha256) is None
    ):
        missing.append("valid embedding_sha256")
    if not profile.crp_pairs:
        missing.append("nonempty supplied CRP pairs")
    if profile.translated_target_state is None:
        missing.append("translated target state")
    elif profile.translated_target_state not in lts.states:
        missing.append("translated target state in finite LTS")
    if profile.external_prefix_claimed is None:
        missing.append("external legal-prefix claim")
    if missing:
        return CRPEvidenceAudit(
            classification="incomplete_evidence",
            independent_target_reachable=None,
            independent_witness=(),
            reasons=tuple(missing),
        )

    target_state = profile.translated_target_state
    if target_state is None:
        raise AssertionError("validated target state unexpectedly missing")
    witness = _shortest_state_witness(lts, target_state)
    reachable = witness is not None
    reasons: tuple[str, ...]
    if reachable == profile.external_prefix_claimed:
        classification: CRPClassification = (
            "agreement" if reachable else "unreachable_candidate"
        )
        reasons = ()
    else:
        classification = "evidence_disagreement"
        reasons = ("external prefix claim disagrees with complete finite-LTS BFS",)
    return CRPEvidenceAudit(
        classification=classification,
        independent_target_reachable=reachable,
        independent_witness=witness or (),
        reasons=reasons,
    )


def evaluate_supplied_l30_inequalities(
    capacities: Mapping[str, int],
    inequalities: Iterable[IntegerLinearInequality],
    *,
    finite_capacity_s3pr_ens3pr: bool,
    inequality_provenance: str,
) -> L30SufficientCheck:
    """Evaluate supplied sufficient inequalities without deriving or optimizing."""

    normalized_capacities: dict[str, int] = {}
    for resource, capacity in capacities.items():
        if not resource:
            raise ValueError("capacity variable names must be nonempty")
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise TypeError("capacities must be integers")
        if capacity < 0:
            raise ValueError("capacities must be nonnegative")
        normalized_capacities[resource] = capacity

    if not finite_capacity_s3pr_ens3pr:
        return L30SufficientCheck(
            applicable=False,
            classification="not_applicable",
            sufficient_conditions_satisfied=None,
            evaluations=(),
            reasons=("finite-capacity S3PR/ENS3PR applicability is not established",),
        )
    if inequality_provenance != "sms_derived_external":
        return L30SufficientCheck(
            applicable=False,
            classification="not_applicable",
            sufficient_conditions_satisfied=None,
            evaluations=(),
            reasons=("supplied inequalities lack SMS-derived external provenance",),
        )

    frozen_inequalities = tuple(sorted(inequalities, key=lambda item: item.name))
    if not frozen_inequalities:
        raise ValueError("applicable L30 check requires supplied inequalities")
    if len({item.name for item in frozen_inequalities}) != len(frozen_inequalities):
        raise ValueError("supplied inequality names must be unique")

    evaluations: list[tuple[str, int, int, bool]] = []
    for inequality in frozen_inequalities:
        unknown = sorted(
            variable
            for variable, _coefficient in inequality.coefficients
            if variable not in normalized_capacities
        )
        if unknown:
            raise ValueError(
                f"inequality {inequality.name!r} references unknown capacity "
                f"{unknown[0]!r}"
            )
        lhs = sum(
            coefficient * normalized_capacities[variable]
            for variable, coefficient in inequality.coefficients
        )
        evaluations.append(
            (inequality.name, lhs, inequality.rhs, lhs >= inequality.rhs)
        )
    satisfied = all(item[3] for item in evaluations)
    return L30SufficientCheck(
        applicable=True,
        classification=(
            "sufficient_conditions_satisfied" if satisfied else "not_certified"
        ),
        sufficient_conditions_satisfied=satisfied,
        evaluations=tuple(evaluations),
        reasons=(),
    )


def adapted_candidate_monitor_cover(
    *,
    legal_states: Iterable[str],
    first_met_bad_states: Iterable[str],
    candidates: Iterable[CandidateMonitor],
) -> AdaptedMonitorCoverResult:
    """Find a minimum legal-preserving cover over supplied candidates."""

    legal = _unique_state_set("legal states", legal_states)
    bad = _unique_state_set("first-met bad states", first_met_bad_states)
    overlap = sorted(legal & bad)
    if overlap:
        raise ValueError(f"legal and bad states overlap at {overlap[0]!r}")
    if not bad:
        raise ValueError("first-met bad states must be nonempty")

    frozen_candidates = tuple(sorted(candidates, key=lambda item: item.monitor_id))
    if len({item.monitor_id for item in frozen_candidates}) != len(frozen_candidates):
        raise ValueError("candidate monitor ids must be unique")
    for candidate in frozen_candidates:
        unknown_bad = sorted(set(candidate.covered_bad_states) - bad)
        if unknown_bad:
            raise ValueError(
                f"candidate {candidate.monitor_id!r} covers unknown bad state "
                f"{unknown_bad[0]!r}"
            )
        unknown_legal = sorted(set(candidate.excluded_legal_states) - legal)
        if unknown_legal:
            raise ValueError(
                f"candidate {candidate.monitor_id!r} excludes unknown legal state "
                f"{unknown_legal[0]!r}"
            )

    legal_preserving = tuple(
        candidate
        for candidate in frozen_candidates
        if not candidate.excluded_legal_states
    )
    examined = 0
    for cardinality in range(1, len(legal_preserving) + 1):
        for subset in combinations(legal_preserving, cardinality):
            examined += 1
            covered = {
                state for candidate in subset for state in candidate.covered_bad_states
            }
            if covered >= bad:
                return AdaptedMonitorCoverResult(
                    classification="optimal_over_supplied_candidates",
                    selected_monitor_ids=tuple(
                        candidate.monitor_id for candidate in subset
                    ),
                    minimum_cardinality=cardinality,
                    all_bad_states_covered=True,
                    all_legal_states_preserved=True,
                    examined_subsets=examined,
                )

    return AdaptedMonitorCoverResult(
        classification="infeasible_over_supplied_candidates",
        selected_monitor_ids=(),
        minimum_cardinality=None,
        all_bad_states_covered=False,
        all_legal_states_preserved=True,
        examined_subsets=examined,
    )


def _shortest_state_witness(
    lts: FiniteLTS,
    target_state: str,
) -> tuple[str, ...] | None:
    outgoing = _outgoing_by_state(lts)
    queue: deque[tuple[str, tuple[str, ...]]] = deque([(lts.initial_state, ())])
    seen = {lts.initial_state}
    while queue:
        state, witness = queue.popleft()
        if state == target_state:
            return witness
        for _source, event, target, _controllable in outgoing[state]:
            if target in seen:
                continue
            seen.add(target)
            queue.append((target, witness + (event,)))
    return None


def _shortest_augmented_witness(
    lts: FiniteLTS,
    *,
    target_state: str,
    recorder_events: tuple[str, ...],
    fixed_counts: tuple[int, ...],
) -> tuple[tuple[str, ...] | None, int]:
    event_index = {event: index for index, event in enumerate(recorder_events)}
    initial_counts = tuple(0 for _event in recorder_events)
    queue: deque[tuple[str, tuple[int, ...], tuple[str, ...]]] = deque(
        [(lts.initial_state, initial_counts, ())]
    )
    seen = {(lts.initial_state, initial_counts)}
    outgoing = _outgoing_by_state(lts)
    while queue:
        state, counts, witness = queue.popleft()
        if state == target_state and counts == fixed_counts:
            return witness, len(seen)
        for _source, event, target, _controllable in outgoing[state]:
            next_counts = list(counts)
            index = event_index.get(event)
            if index is not None:
                next_counts[index] += 1
                if next_counts[index] > fixed_counts[index]:
                    continue
            next_count_tuple = tuple(next_counts)
            augmented = (target, next_count_tuple)
            if augmented in seen:
                continue
            seen.add(augmented)
            queue.append((target, next_count_tuple, witness + (event,)))
    return None, len(seen)


def _outgoing_by_state(lts: FiniteLTS) -> dict[str, tuple[TransitionArc, ...]]:
    outgoing: dict[str, list[TransitionArc]] = {state: [] for state in lts.states}
    for arc in sorted(lts.transitions):
        outgoing[arc[0]].append(arc)
    return {state: tuple(arcs) for state, arcs in outgoing.items()}


def _validate_finite_lts(lts: FiniteLTS) -> None:
    if len(set(lts.states)) != len(lts.states):
        raise ValueError("LTS states must be unique")
    states = set(lts.states)
    if lts.initial_state not in states:
        raise ValueError("LTS initial state must belong to the state set")
    if len(set(lts.marked_states)) != len(lts.marked_states):
        raise ValueError("LTS marked states must be unique")
    if not set(lts.marked_states) <= states:
        raise ValueError("LTS marked states must belong to the state set")
    for source, _event, target, _controllable in lts.transitions:
        if source not in states or target not in states:
            raise ValueError("LTS transitions must stay inside the state set")


def _unique_state_set(label: str, values: Iterable[str]) -> set[str]:
    frozen = tuple(values)
    if any(not value for value in frozen):
        raise ValueError(f"{label} must be nonempty strings")
    if len(set(frozen)) != len(frozen):
        raise ValueError(f"{label} must be unique")
    return set(frozen)
