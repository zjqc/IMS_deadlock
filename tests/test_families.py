import pytest

from ims_deadlock.families import (
    BIX0Parameters,
    BIX0ReportRow,
    BIX1Parameters,
    BIX1ReportRow,
    bix0_grid_report,
    bix0_report_row,
    bix1_persistent_d_boundary_record,
    bix1_sat_grid_report,
    bix1_sat_report_row,
    build_bix0_candidate,
    build_bix1_sat_instance,
)
from ims_deadlock.model import RequestAlternative


def test_bix0_grid_matches_p3c_threshold_on_requested_domain() -> None:
    report = bix0_grid_report(
        max_c_M=3,
        max_c_G=3,
        max_c_D=3,
        max_n_A=4,
        max_n_B=4,
    )

    assert len(report.rows) == 3 * 3 * 3 * ((5 * 5) - 1)
    assert report.mismatches == ()
    assert all(row.match for row in report.rows)


def test_bix0_constructs_empty_prefix_candidate_state() -> None:
    candidate = build_bix0_candidate(BIX0Parameters(c_M=2, c_G=1, c_D=3, n_A=4, n_B=3))

    assert candidate.state.held_units("M") == 2
    assert candidate.state.held_units("G") == 1
    assert candidate.state.held_units("D") == 0
    assert _request_resources(candidate.state.requests["A1"]) == ("D", "G")
    assert _request_resources(candidate.state.requests["A3"]) == ("M",)
    assert _request_resources(candidate.state.requests["B1"]) == ("M",)
    assert _request_resources(candidate.state.requests["B2"]) == ("G",)
    assert candidate.state.stable is True
    assert candidate.state.event_calendar_empty is True
    assert candidate.state.complete is False


def test_bix0_closed_kernel_certificate_resources_are_exactly_m_g() -> None:
    row = bix0_report_row(BIX0Parameters(c_M=2, c_G=2, c_D=3, n_A=3, n_B=4))

    assert row.predicted_closed_kernel is True
    assert row.observed.closed_kernel is True
    assert row.observed.certificate_resources == ("G", "M")
    assert set(row.observed.certificate_resources) == {"M", "G"}
    assert row.observed.certificate is not None
    assert row.observed.certificate.kernel_resources == frozenset({"M", "G"})
    assert "D" not in row.observed.certificate.kernel_resources


def test_bix0_threshold_is_invariant_to_d_capacity_on_grid() -> None:
    grouped: dict[tuple[int, int, int, int], set[bool]] = {}
    report = bix0_grid_report(
        max_c_M=3,
        max_c_G=3,
        max_c_D=3,
        max_n_A=4,
        max_n_B=4,
    )

    for row in report.rows:
        key = (
            row.parameters.c_M,
            row.parameters.c_G,
            row.parameters.n_A,
            row.parameters.n_B,
        )
        grouped.setdefault(key, set()).add(row.observed.closed_kernel)

    assert all(len(observed_values) == 1 for observed_values in grouped.values())


def test_bix0_zero_job_case_is_classified_honestly_when_included() -> None:
    report = bix0_grid_report(
        max_c_M=1,
        max_c_G=1,
        max_c_D=1,
        max_n_A=0,
        max_n_B=0,
        include_zero_job_case=True,
    )

    assert len(report.rows) == 1
    row = report.rows[0]
    assert row.parameters.total_jobs == 0
    assert row.predicted_closed_kernel is False
    assert row.observed.classification == "completed_zero_jobs"
    assert row.observed.closed_kernel is False
    assert row.match is True


def test_bix0_report_json_round_trips_with_strict_schema() -> None:
    row = bix0_report_row(BIX0Parameters(c_M=1, c_G=2, c_D=3, n_A=1, n_B=2))
    payload = row.to_json_dict()

    assert BIX0ReportRow.from_json_dict(payload).to_json_dict() == payload

    payload_with_extra = dict(payload)
    payload_with_extra["extra"] = "not allowed"
    with pytest.raises(ValueError, match="row keys mismatch"):
        BIX0ReportRow.from_json_dict(payload_with_extra)

    bad_parameters = dict(payload)
    bad_parameters["parameters"] = {
        "c_M": True,
        "c_G": 2,
        "c_D": 3,
        "n_A": 1,
        "n_B": 2,
    }
    with pytest.raises(TypeError, match="c_M must be an integer"):
        BIX0ReportRow.from_json_dict(bad_parameters)

    bad_observed = dict(payload)
    bad_observed["observed"] = {
        "classification": "closed_kernel",
        "closed_kernel": False,
        "certificate_resources": ["G", "M"],
        "validation_issues": [],
    }
    with pytest.raises(ValueError, match="closed_kernel disagrees"):
        BIX0ReportRow.from_json_dict(bad_observed)


def test_bix0_parameters_reject_invalid_domains() -> None:
    with pytest.raises(ValueError, match="capacities"):
        BIX0Parameters(c_M=0, c_G=1, c_D=1, n_A=0, n_B=0)
    with pytest.raises(ValueError, match="job counts"):
        BIX0Parameters(c_M=1, c_G=1, c_D=1, n_A=-1, n_B=0)


def test_bix1_sat_minimal_instance_reaches_m_g_deadlock_with_prefix() -> None:
    row = bix1_sat_report_row(
        BIX1Parameters(c_M=1, c_G=1, c_D=1, c_V=1, n_A=1, n_B=1),
        max_states=64,
    )

    assert row.predicted_reachable_closed_kernel is True
    assert row.observed.reachable_closed_kernel is True
    assert row.observed.certificate_resources == ("G", "M")
    assert row.observed.shortest_reachable_prefix
    assert row.observed.truncated is False
    assert row.match is True


def test_bix1_sat_below_a_or_b_threshold_has_no_reachable_deadlock() -> None:
    for parameters in (
        BIX1Parameters(c_M=2, c_G=1, c_D=1, c_V=1, n_A=1, n_B=1),
        BIX1Parameters(c_M=1, c_G=2, c_D=1, c_V=1, n_A=1, n_B=1),
        BIX1Parameters(c_M=1, c_G=1, c_D=1, c_V=1, n_A=0, n_B=1),
        BIX1Parameters(c_M=1, c_G=1, c_D=1, c_V=1, n_A=1, n_B=0),
    ):
        row = bix1_sat_report_row(parameters, max_states=256)

        assert row.predicted_reachable_closed_kernel is False
        assert row.observed.reachable_closed_kernel is False
        assert row.observed.truncated is False
        assert row.match is True


def test_bix1_sat_d_and_v_capacities_do_not_change_threshold() -> None:
    report = bix1_sat_grid_report(
        max_c_M=2,
        max_c_G=2,
        max_c_D=2,
        max_c_V=2,
        max_n_A=2,
        max_n_B=2,
        max_states=4096,
    )
    grouped: dict[tuple[int, int, int, int], set[bool]] = {}

    assert report.mismatches == ()
    assert all(not row.observed.truncated for row in report.rows)
    for row in report.rows:
        key = (
            row.parameters.c_M,
            row.parameters.c_G,
            row.parameters.n_A,
            row.parameters.n_B,
        )
        grouped.setdefault(key, set()).add(row.observed.reachable_closed_kernel)

    assert all(len(observed_values) == 1 for observed_values in grouped.values())


def test_bix1_sat_initial_state_has_no_holds_and_start_requests() -> None:
    instance = build_bix1_sat_instance(
        BIX1Parameters(c_M=2, c_G=1, c_D=3, c_V=2, n_A=3, n_B=2)
    )

    assert instance.initial_state.holds == ()
    assert _request_resources(instance.initial_state.requests["A1"]) == ("M",)
    assert _request_resources(instance.initial_state.requests["B1"]) == ("G",)
    assert instance.model.resources["V"].kind == "reservation"
    assert instance.initial_state.event_calendar_empty is True


def test_bix1_sat_truncated_search_is_not_reported_as_evidence_or_match() -> None:
    row = bix1_sat_report_row(
        BIX1Parameters(c_M=1, c_G=1, c_D=1, c_V=1, n_A=1, n_B=1),
        max_states=1,
    )

    assert row.observed.truncated is True
    assert row.observed.reachable_closed_kernel is False
    assert row.observed.shortest_reachable_prefix == ()
    assert row.match is False


def test_bix1_sat_report_json_round_trips_with_strict_schema() -> None:
    row = bix1_sat_report_row(
        BIX1Parameters(c_M=1, c_G=2, c_D=3, c_V=4, n_A=1, n_B=2),
        max_states=1024,
    )
    payload = row.to_json_dict()

    assert BIX1ReportRow.from_json_dict(payload).to_json_dict() == payload

    payload_with_extra = dict(payload)
    payload_with_extra["extra"] = "not allowed"
    with pytest.raises(ValueError, match="row keys mismatch"):
        BIX1ReportRow.from_json_dict(payload_with_extra)

    bad_parameters = dict(payload)
    bad_parameters["parameters"] = {
        "c_M": 1,
        "c_G": 2,
        "c_D": 3,
        "c_V": True,
        "n_A": 1,
        "n_B": 2,
    }
    with pytest.raises(TypeError, match="c_V must be an integer"):
        BIX1ReportRow.from_json_dict(bad_parameters)

    bad_observed = dict(payload)
    bad_observed["observed"] = {
        "classification": "reachable_closed_kernel",
        "reachable_closed_kernel": False,
        "certificate_resources": ["G", "M"],
        "shortest_reachable_prefix": ["A1-start-M"],
        "state_count": 4,
        "truncated": False,
        "validation_issues": [],
    }
    with pytest.raises(ValueError, match="reachable_closed_kernel disagrees"):
        BIX1ReportRow.from_json_dict(bad_observed)


def test_bix1_parameters_reject_invalid_domains() -> None:
    with pytest.raises(ValueError, match="capacities"):
        BIX1Parameters(c_M=1, c_G=1, c_D=1, c_V=0, n_A=0, n_B=0)
    with pytest.raises(ValueError, match="job counts"):
        BIX1Parameters(c_M=1, c_G=1, c_D=1, c_V=1, n_A=-1, n_B=0)


def test_bix1_persistent_d_boundary_is_classified_outside_sat_theorem() -> None:
    boundary = bix1_persistent_d_boundary_record()

    assert boundary.case_id == "CE-BIXD1"
    assert boundary.classification == "outside_bix1_sat"
    assert boundary.to_json_dict()["classification"] == "outside_bix1_sat"


def _request_resources(alternatives: tuple[RequestAlternative, ...]) -> tuple[str, ...]:
    alternative = alternatives[0]
    return tuple(demand.resource_id for demand in alternative.demands)
