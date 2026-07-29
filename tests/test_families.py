import pytest

from ims_deadlock.families import (
    BIX0Parameters,
    BIX0ReportRow,
    bix0_grid_report,
    bix0_report_row,
    build_bix0_candidate,
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


def _request_resources(alternatives: tuple[RequestAlternative, ...]) -> tuple[str, ...]:
    alternative = alternatives[0]
    return tuple(demand.resource_id for demand in alternative.demands)
