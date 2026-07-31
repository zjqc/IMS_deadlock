from pathlib import Path

from ims_deadlock.g6b_row_family_protocol import (
    validate_g6b_row_family_bundle,
)

BUNDLE = Path("cases/discovery/g6b/row_families/structural_discovery_v1")


def test_canonical_bundle_loads_disabled_before_semantic_validation() -> None:
    result = validate_g6b_row_family_bundle(BUNDLE)

    assert result.valid is False
    assert result.errors == ("semantic validation incomplete",)
    assert result.scientific_execution_authorized is False
    assert result.case_creation_authorized is False
    assert result.adversarial_review_status == "PENDING"
    assert result.review_state == "ROW_FAMILY_BUNDLE_IMPLEMENTED"
    assert set(result.bundle_hashes) == {
        "row_family_protocol.json",
        "identity_schema.json",
        "row_family_matrix.json",
        "reuse_matrix.json",
        "overlap_report_schema.json",
        "runtime_lock_schema.json",
        "review_state.json",
        "failure_ledger.json",
    }
