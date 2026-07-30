import pytest

from ims_deadlock.engine import FiniteLTS
from ims_deadlock.g4_comparators import (
    CandidateMonitor,
    CRPEvidenceProfile,
    IntegerLinearInequality,
    adapted_candidate_monitor_cover,
    audit_crp_evidence,
    evaluate_supplied_l30_inequalities,
    fixed_recorder_target_reachability,
)


def _recorder_lts() -> FiniteLTS:
    return FiniteLTS(
        states=("s0", "s1", "target"),
        initial_state="s0",
        marked_states=("target",),
        transitions=(
            ("s0", "record", "s1", True),
            ("s0", "skip", "target", True),
            ("s1", "finish", "target", True),
            ("s1", "record", "s1", True),
        ),
    )


def test_fixed_recorder_target_distinguishes_existential_projection() -> None:
    result = fixed_recorder_target_reachability(
        _recorder_lts(),
        target_state="target",
        recorder_events=("record",),
        fixed_counts={"record": 2},
    )

    assert result.original_target_reachable is True
    assert result.shortest_original_witness == ("skip",)
    assert result.fixed_target_reachable is True
    assert result.shortest_fixed_witness == ("record", "record", "finish")
    assert result.fixed_counts == (("record", 2),)


def test_fixed_recorder_target_reports_unreachable_fixed_count() -> None:
    result = fixed_recorder_target_reachability(
        _recorder_lts(),
        target_state="target",
        recorder_events=("record",),
        fixed_counts={"record": 3},
    )

    assert result.original_target_reachable is True
    assert result.fixed_target_reachable is True
    assert result.shortest_fixed_witness == (
        "record",
        "record",
        "record",
        "finish",
    )

    impossible = fixed_recorder_target_reachability(
        FiniteLTS(
            states=("s0", "target"),
            initial_state="s0",
            marked_states=("target",),
            transitions=(("s0", "skip", "target", True),),
        ),
        target_state="target",
        recorder_events=("record",),
        fixed_counts={"record": 1},
    )
    assert impossible.original_target_reachable is True
    assert impossible.fixed_target_reachable is False
    assert impossible.shortest_fixed_witness == ()


def test_fixed_recorder_target_prunes_paths_that_exceed_frozen_count() -> None:
    result = fixed_recorder_target_reachability(
        FiniteLTS(
            states=("s0", "s1", "target"),
            initial_state="s0",
            marked_states=("target",),
            transitions=(
                ("s0", "record", "s1", True),
                ("s1", "record", "target", True),
            ),
        ),
        target_state="target",
        recorder_events=("record",),
        fixed_counts={"record": 1},
    )

    assert result.original_target_reachable is True
    assert result.fixed_target_reachable is False


def test_fixed_recorder_target_validates_predeclared_count_vector() -> None:
    with pytest.raises(ValueError, match="exactly match"):
        fixed_recorder_target_reachability(
            _recorder_lts(),
            target_state="target",
            recorder_events=("record",),
            fixed_counts={},
        )

    with pytest.raises(ValueError, match="nonnegative"):
        fixed_recorder_target_reachability(
            _recorder_lts(),
            target_state="target",
            recorder_events=("record",),
            fixed_counts={"record": -1},
        )


def _crp_lts() -> FiniteLTS:
    return FiniteLTS(
        states=("initial", "reachable_deadlock", "unreachable_candidate"),
        initial_state="initial",
        marked_states=(),
        transitions=(("initial", "advance", "reachable_deadlock", True),),
    )


def test_crp_evidence_profile_agrees_only_with_complete_hashed_evidence() -> None:
    profile = CRPEvidenceProfile(
        s4pr_applicable=True,
        embedding_sha256="a" * 64,
        crp_pairs=(("p1", "r2"), ("p2", "r1")),
        translated_target_state="reachable_deadlock",
        external_prefix_claimed=True,
        outside_s4pr_reasons=(),
    )

    result = audit_crp_evidence(_crp_lts(), profile)

    assert result.classification == "agreement"
    assert result.independent_target_reachable is True
    assert result.independent_witness == ("advance",)
    assert result.source_algorithm_reproduced is False


def test_crp_evidence_profile_preserves_unreachable_and_outside_boundaries() -> None:
    unreachable = audit_crp_evidence(
        _crp_lts(),
        CRPEvidenceProfile(
            s4pr_applicable=True,
            embedding_sha256="b" * 64,
            crp_pairs=(("p1", "r2"),),
            translated_target_state="unreachable_candidate",
            external_prefix_claimed=False,
            outside_s4pr_reasons=(),
        ),
    )
    assert unreachable.classification == "unreachable_candidate"
    assert unreachable.independent_target_reachable is False

    outside = audit_crp_evidence(
        _crp_lts(),
        CRPEvidenceProfile(
            s4pr_applicable=False,
            embedding_sha256=None,
            crp_pairs=(),
            translated_target_state=None,
            external_prefix_claimed=None,
            outside_s4pr_reasons=("conjunctive_request", "agv_reservation"),
        ),
    )
    assert outside.classification == "not_applicable"
    assert outside.independent_target_reachable is None


def test_crp_evidence_profile_reports_claim_or_oracle_disagreement() -> None:
    result = audit_crp_evidence(
        _crp_lts(),
        CRPEvidenceProfile(
            s4pr_applicable=True,
            embedding_sha256="c" * 64,
            crp_pairs=(("p1", "r2"),),
            translated_target_state="unreachable_candidate",
            external_prefix_claimed=True,
            outside_s4pr_reasons=(),
        ),
    )

    assert result.classification == "evidence_disagreement"
    assert result.independent_target_reachable is False


def test_crp_evidence_profile_rejects_noncanonical_pair_evidence() -> None:
    with pytest.raises(ValueError, match="unique"):
        CRPEvidenceProfile(
            s4pr_applicable=True,
            embedding_sha256="d" * 64,
            crp_pairs=(("p1", "r2"), ("p1", "r2")),
            translated_target_state="reachable_deadlock",
            external_prefix_claimed=True,
            outside_s4pr_reasons=(),
        )

    with pytest.raises(ValueError, match="nonempty"):
        CRPEvidenceProfile(
            s4pr_applicable=True,
            embedding_sha256="e" * 64,
            crp_pairs=(("", "r2"),),
            translated_target_state="reachable_deadlock",
            external_prefix_claimed=True,
            outside_s4pr_reasons=(),
        )


def test_l30_checker_is_only_a_supplied_sufficient_condition_evaluator() -> None:
    inequalities = (
        IntegerLinearInequality(
            name="sms-1",
            coefficients=(("r1", 1), ("r2", 2)),
            rhs=5,
        ),
    )
    result = evaluate_supplied_l30_inequalities(
        {"r1": 1, "r2": 2},
        inequalities,
        finite_capacity_s3pr_ens3pr=True,
        inequality_provenance="sms_derived_external",
    )

    assert result.applicable is True
    assert result.classification == "sufficient_conditions_satisfied"
    assert result.sufficient_conditions_satisfied is True
    assert result.exact_ims_threshold_claimed is False
    assert result.source_algorithm_reproduced is False
    assert result.evaluations == (("sms-1", 5, 5, True),)


def test_l30_checker_refuses_non_s3pr_or_unverified_inequalities() -> None:
    inequality = IntegerLinearInequality(
        name="sms-1",
        coefficients=(("r1", 1),),
        rhs=1,
    )
    outside = evaluate_supplied_l30_inequalities(
        {"r1": 1},
        (inequality,),
        finite_capacity_s3pr_ens3pr=False,
        inequality_provenance="sms_derived_external",
    )
    assert outside.applicable is False
    assert outside.classification == "not_applicable"
    assert outside.sufficient_conditions_satisfied is None

    unverified = evaluate_supplied_l30_inequalities(
        {"r1": 1},
        (inequality,),
        finite_capacity_s3pr_ens3pr=True,
        inequality_provenance="hand_tuned",
    )
    assert unverified.applicable is False
    assert unverified.classification == "not_applicable"


def test_adapted_monitor_cover_is_exact_only_over_supplied_candidates() -> None:
    result = adapted_candidate_monitor_cover(
        legal_states=("l0", "l1"),
        first_met_bad_states=("b0", "b1"),
        candidates=(
            CandidateMonitor("m0", ("b0",), ()),
            CandidateMonitor("m1", ("b1",), ()),
            CandidateMonitor("m2", ("b0", "b1"), ("l1",)),
        ),
    )

    assert result.classification == "optimal_over_supplied_candidates"
    assert result.selected_monitor_ids == ("m0", "m1")
    assert result.minimum_cardinality == 2
    assert result.all_bad_states_covered is True
    assert result.all_legal_states_preserved is True
    assert result.source_algorithm_reproduced is False
    assert result.optimality_scope == "supplied_candidate_monitor_set"


def test_adapted_monitor_cover_reports_infeasible_without_overclaiming() -> None:
    result = adapted_candidate_monitor_cover(
        legal_states=("l0",),
        first_met_bad_states=("b0", "b1"),
        candidates=(
            CandidateMonitor("m0", ("b0",), ()),
            CandidateMonitor("m1", ("b1",), ("l0",)),
        ),
    )

    assert result.classification == "infeasible_over_supplied_candidates"
    assert result.selected_monitor_ids == ()
    assert result.minimum_cardinality is None
    assert result.all_bad_states_covered is False
    assert result.all_legal_states_preserved is True
