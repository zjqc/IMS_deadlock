import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from ims_deadlock.g6b_protocol import validate_g6b_protocol_bundle

_DOCUMENT_TOP_LEVEL_KEYS = {
    "protocol.json": "protocol_id",
    "estimand_schema.json": "future_required_hashes",
    "independence_schema.json": "dimensions",
    "negative_controls.json": "controls",
    "failure_ledger.json": "append_only",
}
_ARTIFACT_PATHS = [
    "docs/cases/G6_B_DISCOVERY_PROTOCOL.md",
    "cases/discovery/g6b/estimand_schema.json",
    "cases/discovery/g6b/independence_schema.json",
    "cases/discovery/g6b/negative_controls.json",
    "cases/discovery/g6b/failure_ledger.json",
]
_HISTORICAL_AUTHORITIES = [
    "cases/confirmation/g4/FREEZE_ENTRY.json",
    "cases/confirmation/g4/case_manifest.json",
    "cases/confirmation/g4/random_stream_manifest.json",
    "cases/confirmation/g4/predictions.json",
    "cases/confirmation/g4/metrics_schema.json",
    "evidence/g5/G5_EXECUTION_LOCK.json",
    "evidence/g5/G5_RAW_HASH_MANIFEST.json",
    "evidence/g5/G5_RESULT_SUMMARY.json",
    "evidence/g5/G5_SCORING_ERRATUM.json",
    "evidence/g6/G6_HISTORICAL_REPLAY_FAILURE_LEDGER.json",
    "evidence/g6/G6_HISTORICAL_REPLAY_R3_REPORT.json",
]
_REMOTE_ONLY_HISTORICAL_AUTHORITIES = {
    "evidence/g5/G5_RAW_HASH_MANIFEST.json",
    "evidence/g5/G5_RESULT_SUMMARY.json",
}

_EXPECTED_NEGATIVE_CONTROLS = [
    {
        "id": "NC_LOCAL_BYPASS_COMPLETES",
        "expected_classification": "D_local_not_admitted",
        "expected_refusal": "reachable_completion_bypass",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_UNSELECTED_LIVELOCK",
        "expected_classification": "R_livelock",
        "expected_refusal": "not_selected_bad_class",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_CALENDAR_EMPTY_TERMINAL",
        "expected_classification": "R_terminal",
        "expected_refusal": "not_resource_deadlock",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_POLICY_ONLY_STALL",
        "expected_classification": "P_policy",
        "expected_refusal": "policy_only_not_plant_partition",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_OR_OF_AND_FEASIBLE_BRANCH",
        "expected_classification": "D_local_not_admitted",
        "expected_refusal": "feasible_branch_exists",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_AGV_RESERVATION_BOUNDARY",
        "expected_classification": "boundary_or_new_versioned_target_required",
        "expected_refusal": "semantic_boundary_changed",
        "not_support_if_failed": True,
    },
    {
        "id": "NC_DGLOBAL_ONLY_WITH_DLOCAL",
        "expected_classification": "D_global",
        "expected_refusal": "no_double_count_through_D_local",
        "not_support_if_failed": True,
    },
]
_NEW_FUTURE_HASHES = [
    "positive_rate_graph_hash",
    "policy_filter_hash",
    "absorption_domain_hash",
]


def _copy_bundle(tmp_path: Path) -> Path:
    source_root = Path.cwd()
    repo_root = tmp_path / "repo"
    target = repo_root / "cases/discovery/g6b"
    source = source_root / "cases/discovery/g6b"
    shutil.copytree(source, target)
    for relative_path in [*_ARTIFACT_PATHS, *_HISTORICAL_AUTHORITIES]:
        if relative_path in _REMOTE_ONLY_HISTORICAL_AUTHORITIES:
            continue
        source_path = source_root / relative_path
        assert source_path.is_file(), relative_path
        target_path = repo_root / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
    return target


def _load(bundle: Path, filename: str) -> dict[str, Any]:
    with (bundle / filename).open(encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def _write(bundle: Path, filename: str, data: dict[str, Any]) -> None:
    with (bundle / filename).open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")


def _assert_invalid(bundle: Path, expected: str) -> None:
    validation = validate_g6b_protocol_bundle(bundle)
    assert validation.valid is False
    assert any(expected in error for error in validation.errors), validation.errors


def test_canonical_g6b_bundle_is_valid_and_execution_disabled() -> None:
    validation = validate_g6b_protocol_bundle(Path("cases/discovery/g6b"))

    assert validation.valid is True
    assert validation.errors == ()
    assert validation.scientific_execution_authorized is False
    assert validation.adversarial_review_status == "PENDING"
    assert set(validation.bundle_hashes) == {
        "protocol.json",
        "estimand_schema.json",
        "independence_schema.json",
        "negative_controls.json",
        "failure_ledger.json",
    }


def test_duplicate_json_key_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = (bundle / "protocol.json").read_text(encoding="utf-8")
    duplicate = protocol.replace(
        '"schema_version": "ims-deadlock/g6b-discovery-protocol/v1",',
        (
            '"schema_version": "ims-deadlock/g6b-discovery-protocol/v1",\n'
            '  "schema_version": "ims-deadlock/g6b-discovery-protocol/v1",'
        ),
        1,
    )
    (bundle / "protocol.json").write_text(duplicate, encoding="utf-8")

    _assert_invalid(bundle, "duplicate JSON key")


def test_copied_bundle_outside_canonical_layout_fails_closed(tmp_path: Path) -> None:
    bundle = tmp_path / "floating_g6b"
    shutil.copytree(Path("cases/discovery/g6b"), bundle)

    _assert_invalid(bundle, "bundle root must be <repo>/cases/discovery/g6b")


def test_extra_json_document_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    _write(bundle, "extra.json", {"schema_version": "unexpected"})

    _assert_invalid(bundle, "unexpected JSON documents: ['extra.json']")


@pytest.mark.parametrize("filename", sorted(_DOCUMENT_TOP_LEVEL_KEYS))
def test_missing_required_document_is_reported_deterministically(
    tmp_path: Path, filename: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    (bundle / filename).unlink()

    _assert_invalid(bundle, f"missing JSON documents: ['{filename}']")


@pytest.mark.parametrize("filename", sorted(_DOCUMENT_TOP_LEVEL_KEYS))
def test_non_object_root_is_rejected_for_each_document(
    tmp_path: Path, filename: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    (bundle / filename).write_text("[]\n", encoding="utf-8")

    _assert_invalid(bundle, f"{filename}: root must be a JSON object")


@pytest.mark.parametrize("filename", sorted(_DOCUMENT_TOP_LEVEL_KEYS))
def test_unknown_top_level_key_is_rejected_for_each_document(
    tmp_path: Path, filename: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    document = _load(bundle, filename)
    document["unexpected"] = "not allowed"
    _write(bundle, filename, document)

    _assert_invalid(bundle, f"{filename}: unexpected keys")


@pytest.mark.parametrize(
    ("filename", "key_to_remove"),
    sorted(_DOCUMENT_TOP_LEVEL_KEYS.items()),
)
def test_missing_top_level_key_is_rejected_for_each_document(
    tmp_path: Path, filename: str, key_to_remove: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    document = _load(bundle, filename)
    document.pop(key_to_remove)
    _write(bundle, filename, document)

    _assert_invalid(bundle, f"{filename}: missing keys")


@pytest.mark.parametrize("filename", sorted(_DOCUMENT_TOP_LEVEL_KEYS))
def test_duplicate_json_key_is_rejected_for_each_document(
    tmp_path: Path, filename: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    raw = (bundle / filename).read_text(encoding="utf-8")
    duplicate = raw.replace(
        '"schema_version":',
        '"schema_version": "duplicate-shadow",\n  "schema_version":',
        1,
    )
    (bundle / filename).write_text(duplicate, encoding="utf-8")

    _assert_invalid(bundle, f"{filename}: duplicate JSON key")


def test_unsupported_schema_version_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    protocol["schema_version"] = "ims-deadlock/g6b-discovery-protocol/v2"
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: unsupported schema_version")


def test_missing_independence_dimension_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "independence_schema.json")
    dimensions = schema["dimensions"]
    assert isinstance(dimensions, list)
    dimensions.remove("metric_schema_sha256")
    _write(bundle, "independence_schema.json", schema)

    _assert_invalid(bundle, "independence_schema.json: dimensions")


def test_estimand_schema_v2_uses_typed_ontology() -> None:
    estimand = _load(Path("cases/discovery/g6b"), "estimand_schema.json")

    assert estimand["schema_version"] == "ims-deadlock/g6b-estimand-schema/v2"
    assert "objective_classes" not in estimand["ontology"]
    assert estimand["ontology"]["selected_stopping_targets"] == {
        "bad_hit_sets": ["D_global", "D_local"],
        "success_class": "F",
    }
    assert estimand["ontology"]["unselected_plant_terminal_classes"] == [
        "R_livelock",
        "R_terminal",
    ]
    assert estimand["ontology"]["policy_analysis_class"] == {
        "label": "P_policy",
        "plant_partition_member": False,
        "selectable_target": False,
    }
    assert estimand["ontology"]["derived_state_sets"] == {
        "S_reach": {
            "definition": "complete_stopped_lts_support_reachability",
            "role": "diagnostic_only",
            "selectable_target": False,
        },
        "S_T": {
            "definition": (
                "probability_one_hit_selected_target_in_finite_positive_rate_"
                "stopped_ctmc"
            ),
            "role": "certified_absorption_domain",
            "selectable_target": False,
        },
    }


def test_legacy_objective_classes_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "estimand_schema.json")
    ontology = schema["ontology"]
    assert isinstance(ontology, dict)
    ontology["objective_classes"] = [
        "D_global",
        "D_local",
        "F",
        "R_livelock",
        "R_terminal",
        "P_policy",
        "S_T",
    ]
    _write(bundle, "estimand_schema.json", schema)

    _assert_invalid(bundle, "estimand_schema.json: ontology")


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("bad_hit_sets", ["D_global", "D_local", "S_T"]),
        ("bad_hit_sets", ["D_global", "D_local", "S_reach"]),
        ("bad_hit_sets", ["D_global", "D_local", "R_livelock"]),
        ("success_class", "P_policy"),
    ],
)
def test_selected_target_kind_drift_is_rejected(
    tmp_path: Path, field: str, replacement: list[str] | str
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "estimand_schema.json")
    ontology = schema["ontology"]
    assert isinstance(ontology, dict)
    assert ontology.get("selected_stopping_targets") == {
        "bad_hit_sets": ["D_global", "D_local"],
        "success_class": "F",
    }
    selected = ontology["selected_stopping_targets"]
    assert isinstance(selected, dict)
    selected[field] = replacement
    _write(bundle, "estimand_schema.json", schema)

    _assert_invalid(bundle, "estimand_schema.json: ontology")


@pytest.mark.parametrize("missing_hash", _NEW_FUTURE_HASHES)
def test_future_hashes_require_absorption_identity(
    tmp_path: Path, missing_hash: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "estimand_schema.json")
    future_hashes = schema["future_required_hashes"]
    assert isinstance(future_hashes, list)
    assert missing_hash in future_hashes
    future_hashes.remove(missing_hash)
    _write(bundle, "estimand_schema.json", schema)

    _assert_invalid(bundle, "estimand_schema.json: future_required_hashes")


@pytest.mark.parametrize(
    "rule",
    [
        "certified_absorption_domain_required",
        "same_absorption_domain_hash_required",
    ],
)
def test_exact_des_contract_requires_same_absorption_domain(
    tmp_path: Path, rule: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "estimand_schema.json")
    consistency = schema["exact_des_consistency"]
    assert isinstance(consistency, dict)
    assert consistency.get(rule) is True
    consistency[rule] = False
    _write(bundle, "estimand_schema.json", schema)

    _assert_invalid(bundle, "estimand_schema.json: exact_des_consistency")


def test_wrong_d_local_ontology_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "estimand_schema.json")
    ontology = schema["ontology"]
    assert isinstance(ontology, dict)
    d_local = ontology["D_local"]
    assert isinstance(d_local, dict)
    d_local["ontology"] = "terminal_scc"
    _write(bundle, "estimand_schema.json", schema)

    _assert_invalid(bundle, "estimand_schema.json: ontology")


def test_exact_des_consistency_drift_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    schema = _load(bundle, "estimand_schema.json")
    consistency = schema["exact_des_consistency"]
    assert isinstance(consistency, dict)
    consistency["same_selected_bad_labels_required"] = False
    _write(bundle, "estimand_schema.json", schema)

    _assert_invalid(bundle, "estimand_schema.json: exact_des_consistency")


def test_missing_negative_control_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    controls = _load(bundle, "negative_controls.json")
    control_list = controls["controls"]
    assert isinstance(control_list, list)
    control_list.pop()
    _write(bundle, "negative_controls.json", controls)

    _assert_invalid(bundle, "negative_controls.json: controls")


@pytest.mark.parametrize("index", range(len(_EXPECTED_NEGATIVE_CONTROLS)))
@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("expected_classification", "DRIFTED_CLASSIFICATION"),
        ("expected_refusal", "drifted_refusal"),
    ],
)
def test_negative_control_semantic_drift_is_rejected(
    tmp_path: Path, index: int, field: str, replacement: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    controls = _load(bundle, "negative_controls.json")
    control_list = controls["controls"]
    assert control_list == _EXPECTED_NEGATIVE_CONTROLS
    assert isinstance(control_list, list)
    control = control_list[index]
    assert isinstance(control, dict)
    control[field] = replacement
    _write(bundle, "negative_controls.json", controls)

    _assert_invalid(bundle, "negative_controls.json: controls")


def test_absolute_unapproved_historical_path_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    authorities = protocol["tracked_historical_authorities"]
    assert isinstance(authorities, list)
    authorities[0] = "/tmp/FREEZE_ENTRY.json"
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: tracked_historical_authorities")


def test_execution_true_while_review_pending_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    protocol["scientific_execution_authorized"] = True
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: scientific execution")


def test_append_only_false_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    ledger = _load(bundle, "failure_ledger.json")
    ledger["append_only"] = False
    _write(bundle, "failure_ledger.json", ledger)

    _assert_invalid(bundle, "failure_ledger.json: append_only")


def test_artifact_path_ambiguity_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    protocol = _load(bundle, "protocol.json")
    paths = protocol["artifact_paths"]
    assert isinstance(paths, list)
    paths[0] = "docs/cases/../cases/G6_B_DISCOVERY_PROTOCOL.md"
    _write(bundle, "protocol.json", protocol)

    _assert_invalid(bundle, "protocol.json: artifact_paths")


def test_g6b_theory_documents_lock_typed_absorption_domain() -> None:
    protocol_path = Path("docs/cases/G6_B_DISCOVERY_PROTOCOL.md")
    theorem_path = Path("docs/theory/G6_LOCAL_FIRST_HIT_AND_STOPPING_THEOREMS.md")
    assumption_path = Path("docs/theory/ASSUMPTION_REGISTER.md")
    probability_path = Path("docs/theory/PROBABILITY_LAYER.md")
    symbol_path = Path("docs/theory/SYMBOL_TABLE.md")
    counterexample_path = Path("docs/theory/COUNTEREXAMPLE_LEDGER.md")
    foundation_review_path = Path(
        "docs/verification/G6_B_PROTOCOL_FOUNDATION_REVIEW.md"
    )

    g6b_protocol_text = protocol_path.read_text(encoding="utf-8")
    counterexample_ledger_text = counterexample_path.read_text(encoding="utf-8")
    foundation_review_text = foundation_review_path.read_text(encoding="utf-8")
    combined_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            protocol_path,
            theorem_path,
            assumption_path,
            probability_path,
            symbol_path,
            counterexample_path,
        ]
    )

    assert "S_reach" in combined_text
    assert "support graph" in combined_text or "support-graph" in combined_text
    assert "probability one" in combined_text
    assert "absorption_domain_hash" in combined_text
    assert "Objective classes are:" not in g6b_protocol_text
    assert "selected_stopping_targets" in g6b_protocol_text
    assert "unselected_plant_terminal_classes" in g6b_protocol_text
    assert "CE-NB1" in counterexample_ledger_text
    assert "S_reach" in counterexample_ledger_text
    assert "S_T" in counterexample_ledger_text
    assert "non_almost_sure_absorption_domain" in counterexample_ledger_text
    assert "SUPERSEDED IN PART" in foundation_review_text
    assert (
        "docs/superpowers/specs/2026-07-31-g6b-ontology-absorption-domain-correction-design.md"
        in foundation_review_text
    )

    theorem_text = theorem_path.read_text(encoding="utf-8")
    probability_text = probability_path.read_text(encoding="utf-8")
    assumption_text = assumption_path.read_text(encoding="utf-8")
    symbol_text = symbol_path.read_text(encoding="utf-8")
    active_scoped_text = "\n".join(
        [
            g6b_protocol_text,
            theorem_text,
            probability_text,
            assumption_text,
            symbol_text,
            counterexample_ledger_text,
        ]
    )

    for document_text in [
        g6b_protocol_text,
        theorem_text,
        probability_text,
        assumption_text,
        symbol_text,
    ]:
        assert "S_T = T \\ B_closed" in document_text
        assert "unselected closed SCC" in document_text
        assert "full stopped" in document_text
        assert "outgoing" in document_text
        assert "A_stop" in document_text

    assert "rate_manifest_hash" in symbol_text
    assert "absorption_domain_hash" in symbol_text
    absorption_row = _symbol_row(symbol_text, "absorption_domain_hash")
    for field in [
        "algorithm version",
        "state_space_hash",
        "partition_hash",
        "positive_rate_graph_hash",
        "policy_filter_hash",
        "selected IDs",
        "unselected closed SCCs",
        "B_closed",
        "S_T",
    ]:
        assert field in absorption_row
    assert "full declared rate manifest" not in absorption_row
    assert "Hash of the full declared rate manifest" in _symbol_row(
        symbol_text,
        "rate_manifest_hash",
    )
    assert "absorption-domain identity" in _symbol_row(symbol_text, "estimand_id")

    stale_reverse_basin_sentence = (
        "\u4ece\u6240\u9009\u5438\u6536\u96c6\u53cd\u5411"
        "\u53ef\u8fbe\uff0c\u5f97\u5230\u5b8c\u6574"
        "\u975e\u5438\u6536 basin `S_T`"
    )
    stale_reachability_sentence = (
        "`S_T` \u662f\u80fd\u5230\u8fbe\u6240\u9009"
        " bad/success absorption \u7684\u5168\u90e8"
        "\u975e\u5438\u6536\u72b6\u6001"
    )
    assert stale_reverse_basin_sentence not in theorem_text
    assert stale_reachability_sentence not in theorem_text
    assert "reverse-reachability definition" not in theorem_text
    assert "`R_c`" not in probability_text
    assert "`R_c`" not in symbol_text
    assert "| `B` |" not in symbol_text

    assert len(_symbol_rows(symbol_text, "A")) == 1
    assert "AGV" in _symbol_rows(symbol_text, "A")[0]
    assert len(_symbol_rows(symbol_text, "C")) == 1
    assert "directed cycle" in _symbol_rows(symbol_text, "C")[0]
    assert len(_symbol_rows(symbol_text, "A_stop")) == 1
    assert len(_symbol_rows(symbol_text, "D_sel")) == 1
    assert len(_symbol_rows(symbol_text, "C_closed")) == 1
    assert "D_sel := D_global union D_local" in active_scoped_text
    assert "A_stop := D_sel union F" in active_scoped_text
    assert "T = V \\ A_stop" in active_scoped_text
    assert "C_closed subset T" in active_scoped_text
    assert "outgoing" in active_scoped_text
    assert "A_stop" in active_scoped_text
    assert "S_reach" in active_scoped_text
    assert "path to `A_stop`" in active_scoped_text
    assert "S_T = T \\ B_closed" in active_scoped_text
    assert "tau_{D_sel}" in probability_text
    assert "tau_{A_stop}" in probability_text
    assert "Q_{S_T,D_sel}" in probability_text
    assert "C subset T" not in active_scoped_text
    assert "selected `A`" not in active_scoped_text
    assert "selected A." not in active_scoped_text
    assert "selected A," not in active_scoped_text


def _symbol_row(symbol_text: str, symbol: str) -> str:
    for line in symbol_text.splitlines():
        if line.startswith(f"| `{symbol}` |"):
            return line
    raise AssertionError(f"missing symbol row: {symbol}")


def _symbol_rows(symbol_text: str, symbol: str) -> list[str]:
    return [
        line for line in symbol_text.splitlines() if line.startswith(f"| `{symbol}` |")
    ]
