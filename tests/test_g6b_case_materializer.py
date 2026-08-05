from __future__ import annotations

import ast
import copy
import hashlib
import importlib
import importlib.util
import threading
from collections.abc import Mapping
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import pytest

from ims_deadlock import g6b_schema_contracts
from ims_deadlock.g6b_canonical_json import (
    canonical_bytes_v2,
    canonical_sha256_v2,
    loads_v2,
)

EXPECTED_CASE_IDS = (
    "g6b_cu_nc_local_bypass_completes_v1",
    "g6b_cu_nc_unselected_livelock_v1",
    "g6b_cu_nc_calendar_empty_terminal_v1",
    "g6b_cu_nc_policy_only_stall_v1",
    "g6b_cu_nc_or_of_and_feasible_branch_v1",
    "g6b_cu_nc_agv_reservation_boundary_v1",
    "g6b_cu_nc_dglobal_only_with_dlocal_v1",
    "g6b_cu_pc_dglobal_only_v1",
    "g6b_cu_pc_dlocal_a2b_single_kernel_v1",
    "g6b_cu_pc_dlocal_lts_multi_kernel_v1",
    "g6b_cu_bc_crp_zero_kernel_v1",
    "g6b_cu_bc_multi_capacity_residual_v1",
    "g6b_cu_pc_medium_independent_island_v1",
)
EXPECTED_CONTROL_IDS = (
    "NC_AGV_RESERVATION_BOUNDARY",
    "NC_CALENDAR_EMPTY_TERMINAL",
    "NC_DGLOBAL_ONLY_WITH_DLOCAL",
    "NC_LOCAL_BYPASS_COMPLETES",
    "NC_OR_OF_AND_FEASIBLE_BRANCH",
    "NC_POLICY_ONLY_STALL",
    "NC_UNSELECTED_LIVELOCK",
)
EXPECTED_GROUP_IDS = (
    "g6b_mcg_bc_crp_zero_kernel_v1",
    "g6b_mcg_bc_multi_capacity_residual_v1",
    "g6b_mcg_nc_agv_reservation_boundary_v1",
    "g6b_mcg_nc_calendar_empty_terminal_v1",
    "g6b_mcg_nc_dglobal_only_with_dlocal_v1",
    "g6b_mcg_nc_local_bypass_completes_v1",
    "g6b_mcg_nc_or_of_and_feasible_branch_v1",
    "g6b_mcg_nc_policy_only_stall_v1",
    "g6b_mcg_nc_unselected_livelock_v1",
    "g6b_mcg_pc_dglobal_only_v1",
    "g6b_mcg_pc_dlocal_a2b_single_kernel_v1",
    "g6b_mcg_pc_dlocal_lts_multi_kernel_v1",
    "g6b_mcg_pc_medium_independent_island_v1",
)
EXPECTED_AUTH_FIELDS = (
    "schema_version",
    "artifact_id",
    "capability",
    "authorized",
    "bundle_id",
    "case_unit_ids",
    "method_observation_ids",
    "method_companion_group_ids",
    "source_head",
    "source_tree_hash",
    "source_file_hashes",
    "case_construction_schema_sha256",
    "case_recipe_registry_sha256",
    "frozen_row_family_matrix_sha256",
    "approved_corrigendum_hash",
    "approved_plan_artifact_hash",
    "plan_review_artifact_hash",
    "task2_review_artifact_hash",
    "allowed_operations",
    "forbidden_operations",
    "issued_at_utc",
    "invalidated_by_identity_drift",
    "artifact_sha256",
)
EXPECTED_CASE_ARTIFACT_PATH_KEYS = (
    "case_input",
    "case_content_projection",
    "state_snapshot",
    "route_signature",
    "parameter_tuple",
    "rate_manifest",
    "policy_declaration",
    "selected_target_declaration",
    "control_declaration",
    "sealed_prediction",
    "semantic_lineage_declaration",
    "method_observations",
    "random_stream_manifests",
    "output_root_reservations",
    "metric_schema",
    "metric_schema_sharing",
    "fingerprint_records",
)
RUN4_SELECTED_TARGET_SEMANTIC_FIELDS = (
    "target_schema_version",
    "selected_bad_classes",
    "success_class",
    "exact_stopping_rule",
    "des_stopping_rule",
    "policy_analysis_class",
)
RUN4_APPROVED_CASE_RECIPE_REGISTRY_SHA256 = (
    "e94246b42ec762221dfc1dec066498c4b279a0b9c4266380243b40dd75cc1b72"
)


def materializer_module() -> ModuleType:
    spec = importlib.util.find_spec("ims_deadlock.g6b_case_materializer")
    assert spec is not None, "missing ims_deadlock.g6b_case_materializer"
    return importlib.import_module("ims_deadlock.g6b_case_materializer")


def finalized(record: Mapping[str, Any], field: str) -> dict[str, Any]:
    candidate = dict(record)
    candidate[field] = canonical_sha256_v2({**candidate, field: None})
    return candidate


def valid_authorization(module: Any) -> dict[str, Any]:
    auth = {
        "schema_version": "ims-deadlock/g6b-construction-authorization/v2",
        "artifact_id": "g6b_discovery_case_construction_v1_authorization",
        "capability": "case_construction",
        "authorized": True,
        "bundle_id": module.BUNDLE_ID,
        "case_unit_ids": list(module.CASE_UNIT_IDS),
        "method_observation_ids": list(module.METHOD_OBSERVATION_IDS),
        "method_companion_group_ids": list(module.METHOD_COMPANION_GROUP_IDS),
        "source_head": "a" * 40,
        "source_tree_hash": "b" * 40,
        "source_file_hashes": {
            path: "c" * 64 for path in module.AUTHORIZED_SOURCE_FILE_PATHS
        },
        "case_construction_schema_sha256": module.CASE_CONSTRUCTION_SCHEMA_SHA256,
        "case_recipe_registry_sha256": module.CASE_RECIPE_REGISTRY_SHA256,
        "frozen_row_family_matrix_sha256": module.FROZEN_ROW_FAMILY_MATRIX_SHA256,
        "approved_corrigendum_hash": module.APPROVED_CORRIGENDUM_HASH,
        "approved_plan_artifact_hash": module.APPROVED_PLAN_ARTIFACT_HASH,
        "plan_review_artifact_hash": module.PLAN_REVIEW_ARTIFACT_HASH,
        "task2_review_artifact_hash": "d" * 64,
        "allowed_operations": list(module.ALLOWED_OPERATIONS),
        "forbidden_operations": list(module.FORBIDDEN_OPERATIONS),
        "issued_at_utc": "2026-08-02T00:00:00Z",
        "invalidated_by_identity_drift": False,
        "artifact_sha256": None,
    }
    return finalized(auth, "artifact_sha256")


def candidate_with(
    candidate: Any,
    *,
    case_files: Mapping[str, Any] | None = None,
    governance_files: Mapping[str, Any] | None = None,
    manifest_bytes: bytes | None = None,
    ledger_bytes: bytes | None = None,
    ledger_ready_metadata: Mapping[str, object] | None = None,
) -> Any:
    module = materializer_module()
    return module.CandidateBundle(
        authorization=candidate.authorization,
        case_files=case_files if case_files is not None else candidate.case_files,
        governance_files=(
            governance_files
            if governance_files is not None
            else candidate.governance_files
        ),
        manifest_bytes=(
            manifest_bytes if manifest_bytes is not None else candidate.manifest_bytes
        ),
        ledger_bytes=ledger_bytes
        if ledger_bytes is not None
        else candidate.ledger_bytes,
        immutable_log_bytes=candidate.immutable_log_bytes,
        ledger_ready_metadata=(
            ledger_ready_metadata
            if ledger_ready_metadata is not None
            else candidate.ledger_ready_metadata
        ),
        filesystem_writes_performed=candidate.filesystem_writes_performed,
    )


def candidate_replacing_case_record(
    candidate: Any, path: str, record: Mapping[str, Any]
) -> Any:
    module = materializer_module()
    content = canonical_bytes_v2(dict(record))
    replacement = module.CandidateFile(path, content, hashlib_sha256(content), record)
    case_files = dict(candidate.case_files)
    case_files[path] = replacement

    log_path = module._governance_path("construction_log.json")
    ledger_path = module._governance_path("construction_ledger.json")
    manifest_path = module._governance_path("sealed_bundle_manifest.json")
    ledger_entries = module._successful_ledger_entries(
        candidate.authorization,
        candidate.governance_files[log_path],
        dict(sorted(case_files.items())),
    )
    ledger_bytes = b"".join(
        b"\x1e" + canonical_bytes_v2(entry) + b"\n" for entry in ledger_entries
    )
    ledger_file = module.CandidateFile(
        ledger_path,
        ledger_bytes,
        hashlib_sha256(ledger_bytes),
        {"entry_count": len(ledger_entries)},
    )

    manifest = cast(dict[str, Any], loads_v2(candidate.manifest_bytes.decode("utf-8")))
    case_id = path.split("/case_units/", 1)[1].split("/", 1)[0]
    if path.endswith("/case_input.json"):
        manifest["case_unit_record_hashes"][case_id] = replacement.sha256
    elif "/method_observations/" in path:
        manifest["method_observation_record_hashes"][
            record["method_observation_id"]
        ] = replacement.sha256
    elif path.endswith("/method_companion_group.json"):
        manifest["method_companion_group_record_hashes"][
            record["method_companion_group_id"]
        ] = replacement.sha256
    elif "/fingerprints/" in path:
        manifest["fingerprint_record_hashes"][path] = replacement.sha256
    elif path.endswith("/sealed_prediction.json"):
        manifest["sealed_prediction_hashes"][case_id] = replacement.sha256
    elif path.endswith("/semantic_lineage_declaration.json"):
        manifest["semantic_lineage_declaration_hashes"][case_id] = replacement.sha256
    elif path.endswith("/metric_schema.json"):
        manifest["metric_schema_hashes"][module._group_id_for_case_path(path)] = (
            replacement.sha256
        )
    elif path.endswith(
        "/projections/output_root_reservation_des.json"
    ) or path.endswith("/projections/output_root_reservation_exact.json"):
        manifest["quantitative_output_root_reservations"][
            record["method_observation_id"]
        ] = replacement.sha256
    elif path.endswith("/metric_schema_sharing.json"):
        manifest["metric_schema_sharing_record_hashes"][
            record["method_companion_group_id"]
        ] = replacement.sha256
    elif "/declarations/" in path:
        pass
    else:
        raise AssertionError(f"unhandled replacement path: {path}")
    manifest["construction_ledger_head_sha256"] = ledger_entries[-1]["entry_sha256"]
    manifest = finalized({**manifest, "manifest_sha256": None}, "manifest_sha256")
    manifest_bytes = canonical_bytes_v2(manifest)
    manifest_file = module.CandidateFile(
        manifest_path, manifest_bytes, hashlib_sha256(manifest_bytes), manifest
    )

    governance_files = dict(candidate.governance_files)
    governance_files[ledger_path] = ledger_file
    governance_files[manifest_path] = manifest_file
    ready_created = cast(dict[str, str], ledger_entries[-1]["created_file_hashes"])
    metadata = dict(candidate.ledger_ready_metadata)
    metadata["ready_to_seal_entry_sha256"] = ledger_entries[-1]["entry_sha256"]
    metadata["created_file_hash_count"] = len(ready_created)
    if "ready_created_file_hashes" in metadata:
        metadata["ready_created_file_hashes"] = ready_created
    return candidate_with(
        candidate,
        case_files=case_files,
        governance_files=governance_files,
        manifest_bytes=manifest_bytes,
        ledger_bytes=ledger_bytes,
        ledger_ready_metadata=metadata,
    )


def forbidden_ast_hits(source: str) -> set[str]:
    tree = ast.parse(source)
    hits: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            rendered = ast.unparse(node.func)
            if rendered in {"json.loads", "json.load"}:
                hits.add(rendered)
    return hits


def hashlib_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def ledger_frame(entry: Mapping[str, Any]) -> bytes:
    return b"\x1e" + canonical_bytes_v2(dict(entry)) + b"\n"


def refinalized_ledger_entry(
    entry: Mapping[str, Any], **patch: object
) -> dict[str, Any]:
    mutated = {**dict(entry), **patch, "entry_sha256": None}
    return finalized(mutated, "entry_sha256")


def auth_with_patch(module: Any, patch: Mapping[str, object]) -> dict[str, Any]:
    auth = valid_authorization(module)
    broken = copy.deepcopy(auth)
    broken.update(patch)
    if "artifact_sha256" not in patch:
        broken["artifact_sha256"] = canonical_sha256_v2(
            {**broken, "artifact_sha256": None}
        )
    return broken


def test_required_materializer_symbols_exist() -> None:
    module = materializer_module()
    for name in (
        "validate_construction_authorization_for_materializer",
        "build_case_recipe_catalog",
        "derive_seed_root_hex",
        "derive_philox_key_hex",
        "build_candidate_bundle",
        "validate_candidate_bundle",
        "load_authorization_bytes",
    ):
        assert hasattr(module, name), name


def test_authorization_v2_exact_fields_hashes_scope_and_runtime_identity() -> None:
    module = materializer_module()
    auth = valid_authorization(module)
    validated = module.validate_construction_authorization_for_materializer(auth)
    assert tuple(validated) == EXPECTED_AUTH_FIELDS
    assert validated["authorized"] is True
    assert validated["invalidated_by_identity_drift"] is False
    assert validated["case_unit_ids"] == list(EXPECTED_CASE_IDS)
    assert len(validated["method_observation_ids"]) == 26
    assert validated["method_companion_group_ids"] == sorted(EXPECTED_GROUP_IDS)
    assert (
        validated["approved_corrigendum_hash"]
        == "ff469d9c5105835fde5feb170e501bdde14506df50632990f7c2cddc251da36c"
    )
    assert (
        validated["approved_plan_artifact_hash"]
        == "81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7"
    )
    assert (
        validated["plan_review_artifact_hash"]
        == "da6da7c2e513e11761e439f8b43ef6260556c912d3e730f94f15eae088d90ea0"
    )
    assert (
        validated["frozen_row_family_matrix_sha256"]
        == "487d81aa79a7bca681db81f19a4d6bd315668c43b1c4538c47f01f099d8e205f"
    )
    module.validate_runtime_source_identity(
        validated,
        current_head="a" * 40,
        current_tree_hash="b" * 40,
        current_source_file_hashes=validated["source_file_hashes"],
        dirty_paths=[
            "cases/discovery/g6b/row_families/structural_discovery_v1/governance/g6b_discovery_case_construction_v1/construction_log.json"
        ],
    )
    with pytest.raises(ValueError, match="source_identity_phase_violation"):
        module.validate_runtime_source_identity(
            validated,
            current_head="a" * 40,
            current_tree_hash="b" * 40,
            current_source_file_hashes={
                **validated["source_file_hashes"],
                "src/ims_deadlock/g6b_case_materializer.py": "e" * 64,
            },
            dirty_paths=[],
        )
    module.validate_runtime_source_identity(
        validated,
        current_head="f" * 40,
        current_tree_hash="e" * 40,
        current_source_file_hashes=validated["source_file_hashes"],
        dirty_paths=["docs/verification/G6_B_CASE_CONSTRUCTION_REVIEW_V2.md"],
        post_seal=True,
        source_head_is_ancestor=True,
    )


def test_authorization_rejects_false_drift_duplicate_and_plain_json_loader() -> None:
    module = materializer_module()
    auth = valid_authorization(module)
    for patch in (
        {"authorized": False},
        {"invalidated_by_identity_drift": True},
        {"case_unit_ids": list(EXPECTED_CASE_IDS[:-1])},
        {"allowed_operations": list(module.ALLOWED_OPERATIONS[:-1])},
    ):
        broken = dict(auth)
        broken.update(patch)
        broken["artifact_sha256"] = canonical_sha256_v2(
            {**broken, "artifact_sha256": None}
        )
        with pytest.raises(ValueError):
            module.validate_construction_authorization_for_materializer(broken)
    duplicate = b'{"schema_version":"x","schema_version":"y"}'
    with pytest.raises(ValueError, match="duplicate_member"):
        module.load_authorization_bytes(duplicate)


def test_canonical_authorization_bytes_round_trip_through_loader() -> None:
    module = materializer_module()
    candidate = module.build_candidate_bundle(valid_authorization(module))
    authorization_path = module._governance_path("construction_authorization.json")

    loaded = module.load_authorization_bytes(
        candidate.governance_files[authorization_path].content
    )

    assert tuple(loaded) == module.AUTHORIZATION_FIELDS
    assert dict(loaded) == dict(candidate.authorization)


@pytest.mark.parametrize("value", [1, "true", None])
def test_authorization_requires_authorized_exact_json_true(value: object) -> None:
    module = materializer_module()
    auth = valid_authorization(module)
    broken = finalized(
        {**auth, "authorized": value, "artifact_sha256": None}, "artifact_sha256"
    )
    with pytest.raises(ValueError):
        module.validate_construction_authorization_for_materializer(broken)


@pytest.mark.parametrize("value", [0, "false", None])
def test_authorization_requires_identity_drift_exact_json_false(value: object) -> None:
    module = materializer_module()
    auth = valid_authorization(module)
    broken = finalized(
        {**auth, "invalidated_by_identity_drift": value, "artifact_sha256": None},
        "artifact_sha256",
    )
    with pytest.raises(ValueError):
        module.validate_construction_authorization_for_materializer(broken)


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("source_head", int("1" * 40)),
        ("source_tree_hash", int("1" * 40)),
        ("task2_review_artifact_hash", int("1" * 64)),
        ("case_construction_schema_sha256", int("1" * 64)),
        ("case_recipe_registry_sha256", int("1" * 64)),
        ("frozen_row_family_matrix_sha256", int("1" * 64)),
        ("approved_corrigendum_hash", int("1" * 64)),
        ("approved_plan_artifact_hash", int("1" * 64)),
        ("plan_review_artifact_hash", int("1" * 64)),
        ("artifact_sha256", int("1" * 64)),
    ],
)
def test_authorization_hash_fields_reject_non_string_json_numbers(
    field: str, bad_value: object
) -> None:
    module = materializer_module()
    broken = auth_with_patch(module, {field: bad_value})
    with pytest.raises(ValueError, match=field):
        module.validate_construction_authorization_for_materializer(broken)


@pytest.mark.parametrize("bad_value", [int("1" * 64), True, None])
def test_authorization_source_file_hash_values_must_be_strings(
    bad_value: object,
) -> None:
    module = materializer_module()
    source_file_hashes = dict(valid_authorization(module)["source_file_hashes"])
    source_file_hashes["src/ims_deadlock/g6b_case_materializer.py"] = bad_value
    broken = auth_with_patch(module, {"source_file_hashes": source_file_hashes})
    with pytest.raises(ValueError, match="source_file_hashes"):
        module.validate_construction_authorization_for_materializer(broken)


@pytest.mark.parametrize("field", ["source_head", "task2_review_artifact_hash"])
@pytest.mark.parametrize("bad_value", [True, None])
def test_authorization_identity_digest_fields_reject_bool_and_null(
    field: str, bad_value: object
) -> None:
    module = materializer_module()
    broken = auth_with_patch(module, {field: bad_value})
    with pytest.raises(ValueError, match=field):
        module.validate_construction_authorization_for_materializer(broken)


def test_full_approved_recipe_catalog_and_golden_hash() -> None:
    module = materializer_module()
    catalog = module.build_case_recipe_catalog()
    assert catalog["schema_version"] == "ims-deadlock/g6b-case-recipe-catalog/v1"
    assert tuple(catalog["case_unit_ids"]) == EXPECTED_CASE_IDS
    assert catalog["method_observation_count"] == 26
    assert catalog["method_companion_group_count"] == 13
    assert tuple(catalog["mandatory_control_ids"]) == EXPECTED_CONTROL_IDS
    assert sorted({recipe["input_mode"] for recipe in catalog["recipes"].values()}) == [
        "explicit_finite_lts_input",
        "model_generated_lts",
    ]
    assert (
        len(
            {
                canonical_sha256_v2(recipe["case_content_projection"])
                for recipe in catalog["recipes"].values()
            }
        )
        == 13
    )
    assert catalog["catalog_sha256"] == canonical_sha256_v2(
        {**catalog, "catalog_sha256": None}
    )
    assert (
        module.CASE_RECIPE_REGISTRY_SHA256 == RUN4_APPROVED_CASE_RECIPE_REGISTRY_SHA256
    )
    assert module.CASE_RECIPE_REGISTRY_SHA256 == catalog["catalog_sha256"]
    r01 = catalog["recipes"]["g6b_cu_nc_local_bypass_completes_v1"]
    assert r01["recipe"]["resources"] == ["r_hold:buffer:1", "r_req:machine:1"]
    assert r01["state"]["state_payload"]["transitions"] == [
        {"event_kind": "t_complete", "source": "s_bypass", "target": "f_complete"},
        {
            "event_kind": "t_bypass",
            "source": "s_local_candidate",
            "target": "s_bypass",
        },
    ]
    r06 = catalog["recipes"]["g6b_cu_nc_agv_reservation_boundary_v1"]
    assert (
        r06["target"]["target_schema_version"]
        == "ims-deadlock/g6-terminal-stopping-partition-agv-release-on-arrival/v1"
    )
    assert r06["recipe"]["parameter_overrides"] == [
        "reservation_semantics:enum:preclaim_destination_v1"
    ]
    r13 = catalog["recipes"]["g6b_cu_pc_medium_independent_island_v1"]
    assert r13["recipe"]["resources"] == [
        "agv_x:agv:1",
        "agv_y:agv:1",
        "buffer_ab:buffer:2",
        "buffer_bc:buffer:3",
        "buffer_cd:buffer:2",
        "cell_a:machine:1",
        "cell_b:machine:1",
        "cell_c:machine:1",
        "cell_d:machine:1",
    ]
    assert r13["control"]["control_id_or_null"] is None
    assert (
        r13["prediction"]["expected_boundary"]
        == "bounded_target_certifiable_or_structured_refusal"
    )


def test_candidate_bundle_has_all_files_and_no_writes() -> None:
    module = materializer_module()
    candidate = module.build_candidate_bundle(valid_authorization(module))
    module.validate_candidate_bundle(candidate)
    assert len(candidate.case_files) == 390
    assert len(candidate.governance_files) == 4
    assert len(candidate.all_files) == 394
    assert candidate.case_file_count == 390
    assert candidate.governance_file_count == 4
    assert candidate.total_file_count == 394
    assert list(candidate.case_files) == sorted(candidate.case_files)
    assert (
        b"construction_authorization"
        in candidate.governance_files[
            "cases/discovery/g6b/row_families/structural_discovery_v1/governance/g6b_discovery_case_construction_v1/construction_log.json"
        ].content
    )
    manifest = loads_v2(candidate.manifest_bytes.decode("utf-8"))
    assert isinstance(manifest, dict)
    manifest_obj = cast(dict[str, Any], manifest)
    assert manifest_obj["case_file_count"] == 390
    assert manifest_obj["governance_file_count"] == 4
    assert manifest_obj["total_file_count"] == 394
    assert set(manifest_obj["metric_schema_sharing_record_hashes"]) == set(
        EXPECTED_GROUP_IDS
    )
    for path, entry in candidate.case_files.items():
        assert entry.sha256 == canonical_sha256_v2(
            loads_v2(entry.content.decode("utf-8"))
        )
        assert path.startswith(
            "cases/discovery/g6b/row_families/structural_discovery_v1/case_units/"
        )
    assert candidate.filesystem_writes_performed == 0


def test_r4_candidate_manifest_uses_immutable_log_self_hash_not_final_bytes() -> None:
    module = materializer_module()
    candidate = module.build_candidate_bundle(valid_authorization(module))
    manifest = cast(dict[str, Any], loads_v2(candidate.manifest_bytes.decode("utf-8")))
    log_record = cast(
        dict[str, Any],
        loads_v2(candidate.governance_files[log_path(module)].content.decode("utf-8")),
    )
    ledger_entries = parse_rs_ledger(candidate.ledger_bytes)

    assert manifest["construction_log_sha256"] == log_record["log_sha256"]
    assert (
        manifest["construction_log_sha256"]
        != candidate.governance_files[log_path(module)].sha256
    )
    assert all(
        entry["candidate_log_sha256_or_null"]
        == candidate.governance_files[log_path(module)].sha256
        for entry in ledger_entries
    )
    assert ledger_entries[-1]["created_file_hashes"][log_path(module)] == (
        candidate.governance_files[log_path(module)].sha256
    )


def test_run4_recipe_target_payload_is_semantic_six_field_baseline() -> None:
    module = materializer_module()
    catalog = module.build_case_recipe_catalog()

    assert catalog["catalog_sha256"] == RUN4_APPROVED_CASE_RECIPE_REGISTRY_SHA256
    for recipe in catalog["recipes"].values():
        target = cast(dict[str, Any], recipe["target"])
        assert tuple(target) == RUN4_SELECTED_TARGET_SEMANTIC_FIELDS
        assert "schema_version" not in target
        assert recipe["case_content_projection"][
            "selected_target_declaration_sha256"
        ] == canonical_sha256_v2(target)


def test_run4_materialized_selected_target_file_is_schema_wrapped_payload() -> None:
    module = materializer_module()
    candidate = module.build_candidate_bundle(valid_authorization(module))
    selected_path = (
        "cases/discovery/g6b/row_families/structural_discovery_v1/case_units/"
        f"{EXPECTED_CASE_IDS[0]}/declarations/selected_target_declaration.json"
    )
    case_content_path = (
        "cases/discovery/g6b/row_families/structural_discovery_v1/case_units/"
        f"{EXPECTED_CASE_IDS[0]}/projections/case_content.json"
    )
    selected = cast(
        dict[str, Any],
        loads_v2(candidate.case_files[selected_path].content.decode("utf-8")),
    )
    case_content = cast(
        dict[str, Any],
        loads_v2(candidate.case_files[case_content_path].content.decode("utf-8")),
    )
    semantic_payload = {
        field: selected[field] for field in RUN4_SELECTED_TARGET_SEMANTIC_FIELDS
    }

    assert set(selected) == {"schema_version", *RUN4_SELECTED_TARGET_SEMANTIC_FIELDS}
    assert len(selected) == 7
    assert selected["schema_version"] == (
        "ims-deadlock/g6b-selected-target-declaration/v1"
    )
    assert case_content["selected_target_declaration_sha256"] == canonical_sha256_v2(
        semantic_payload
    )
    assert candidate.case_files[selected_path].sha256 != canonical_sha256_v2(
        semantic_payload
    )
    g6b_schema_contracts.validate_materialization_record_exact_keys(
        "declarations/selected_target_declaration.json",
        selected,
    )


def test_r4_candidate_records_satisfy_materialization_contracts_and_fingerprints() -> (
    None
):
    module = materializer_module()
    candidate = module.build_candidate_bundle(valid_authorization(module))

    fingerprint_count = 0
    for path, entry in candidate.case_files.items():
        record = cast(dict[str, Any], loads_v2(entry.content.decode("utf-8")))
        relative_path = path.split("/case_units/", 1)[1].split("/", 1)[1]
        contract = g6b_schema_contracts.CASE_MATERIALIZATION_FILE_CONTRACTS[
            relative_path
        ]
        schema_field = str(contract["schema_version_field_name"])
        assert record[schema_field] == contract["schema_version_field_value"]
        if relative_path == "declarations/selected_target_declaration.json":
            assert record["schema_version"] == (
                "ims-deadlock/g6b-selected-target-declaration/v1"
            )
            assert isinstance(record["target_schema_version"], str)
            assert record["target_schema_version"].startswith("ims-deadlock/")
        if relative_path.startswith("fingerprints/"):
            fingerprint_count += 1
            dimension = record["dimension"]
            assert record["depends_on_dimensions"] == sorted(
                g6b_schema_contracts.DIMENSION_DEPENDS_ON[dimension]
            )
            assert record["correlated_with_dimensions"] == sorted(
                g6b_schema_contracts.DIMENSION_CORRELATED_WITH[dimension]
            )
            target = contract["direct_stored_fingerprint_target"]
            assert isinstance(target, str)
            projection_entry = candidate.case_files[
                path.rsplit("/", 2)[0] + "/" + target
            ]
            projection = cast(
                dict[str, Any],
                loads_v2(projection_entry.content.decode("utf-8")),
            )
            g6b_schema_contracts.validate_fingerprint_record(record, projection)
    assert fingerprint_count == 130


@pytest.mark.parametrize(
    "bad_issued_at",
    [
        0,
        None,
        {},
        "2026-8-02T00:00:00Z",
        "2026-08-02T00:00:00+00:00",
        "2026-08-02T00:00:00.000Z",
        "2026-02-30T00:00:00Z",
    ],
)
def test_r4_authorization_issued_at_utc_contract_is_strict(
    bad_issued_at: object,
) -> None:
    module = materializer_module()
    module.validate_construction_authorization_for_materializer(
        valid_authorization(module)
    )
    broken = auth_with_patch(module, {"issued_at_utc": bad_issued_at})
    with pytest.raises(ValueError, match="issued_at_utc|timestamp_format_violation"):
        module.validate_construction_authorization_for_materializer(broken)


def test_r4_candidate_validator_rejects_materialized_record_contract_drift() -> None:
    module = materializer_module()
    candidate = module.build_candidate_bundle(valid_authorization(module))
    selected_path = (
        "cases/discovery/g6b/row_families/structural_discovery_v1/case_units/"
        f"{EXPECTED_CASE_IDS[0]}/declarations/selected_target_declaration.json"
    )
    selected = cast(
        dict[str, Any],
        loads_v2(candidate.case_files[selected_path].content.decode("utf-8")),
    )
    selected["schema_version"] = "evil/v0"
    bad = candidate_replacing_case_record(candidate, selected_path, selected)

    with pytest.raises(ValueError):
        module.validate_candidate_bundle(bad)


@pytest.mark.parametrize("mutation", ["extra", "missing"])
def test_r4_candidate_validator_rejects_method_observation_exact_key_drift(
    mutation: str,
) -> None:
    module = materializer_module()
    candidate = module.build_candidate_bundle(valid_authorization(module))
    method_path = (
        "cases/discovery/g6b/row_families/structural_discovery_v1/case_units/"
        f"{EXPECTED_CASE_IDS[0]}/method_observations/exact.json"
    )
    method = cast(
        dict[str, Any],
        loads_v2(candidate.case_files[method_path].content.decode("utf-8")),
    )
    if mutation == "extra":
        method["unexpected_extra_member"] = "must_be_rejected"
    else:
        method.pop("method_role")
    bad = candidate_replacing_case_record(candidate, method_path, method)

    with pytest.raises(ValueError, match="materialization_required_fields"):
        module.validate_candidate_bundle(bad)


def test_r4_candidate_validator_rejects_fingerprint_relation_drift() -> None:
    module = materializer_module()
    candidate = module.build_candidate_bundle(valid_authorization(module))
    fingerprint_path = (
        "cases/discovery/g6b/row_families/structural_discovery_v1/case_units/"
        f"{EXPECTED_CASE_IDS[0]}/fingerprints/case_content_sha256.json"
    )
    fingerprint = cast(
        dict[str, Any],
        loads_v2(candidate.case_files[fingerprint_path].content.decode("utf-8")),
    )
    fingerprint["depends_on_dimensions"] = []
    fingerprint["record_provenance_sha256"] = canonical_sha256_v2(
        {**fingerprint, "record_provenance_sha256": None}
    )
    bad = candidate_replacing_case_record(candidate, fingerprint_path, fingerprint)

    with pytest.raises(ValueError):
        module.validate_candidate_bundle(bad)


def test_validate_candidate_bundle_rejects_fake_394_empty_files() -> None:
    module = materializer_module()
    auth = valid_authorization(module)
    empty_content = b"{}"
    empty_hash = canonical_sha256_v2({})
    case_files = {
        path: module.CandidateFile(path, empty_content, empty_hash, {})
        for path in module._authorized_output_paths()
        if "/case_units/" in path
    }
    manifest = finalized(
        {
            "schema_version": "ims-deadlock/g6b-sealed-bundle-manifest/v2",
            "bundle_id": module.BUNDLE_ID,
            "case_file_count": 390,
            "governance_file_count": 4,
            "total_file_count": 394,
            "manifest_sha256": None,
        },
        "manifest_sha256",
    )
    manifest_bytes = canonical_bytes_v2(manifest)
    governance_files = {
        path: module.CandidateFile(
            path,
            manifest_bytes
            if path.endswith("sealed_bundle_manifest.json")
            else empty_content,
            hashlib_sha256(
                manifest_bytes
                if path.endswith("sealed_bundle_manifest.json")
                else empty_content
            ),
            manifest if path.endswith("sealed_bundle_manifest.json") else {},
        )
        for path in module._authorized_output_paths()
        if "/governance/" in path
    }
    fake = module.CandidateBundle(
        authorization=auth,
        case_files=case_files,
        governance_files=governance_files,
        manifest_bytes=manifest_bytes,
        ledger_bytes=empty_content,
        immutable_log_bytes=empty_content,
        ledger_ready_metadata={
            "ready_to_seal_entry_sha256": "0" * 64,
            "created_file_hash_count": 391,
            "manifest_last": True,
        },
    )
    with pytest.raises(ValueError):
        module.validate_candidate_bundle(fake)


@pytest.mark.parametrize("mutation", ["content", "manifest_map", "cross_ref", "ledger"])
def test_validate_candidate_bundle_rejects_closed_bundle_mutations(
    mutation: str,
) -> None:
    module = materializer_module()
    candidate = module.build_candidate_bundle(valid_authorization(module))
    if mutation == "content":
        first_path, first_file = next(iter(candidate.case_files.items()))
        bad_file = module.CandidateFile(
            first_path,
            b"{}",
            first_file.sha256,
            first_file.record,
        )
        bad_case_files = {**candidate.case_files, first_path: bad_file}
        bad = candidate_with(candidate, case_files=bad_case_files)
    elif mutation == "manifest_map":
        manifest = cast(
            dict[str, Any], loads_v2(candidate.manifest_bytes.decode("utf-8"))
        )
        manifest["case_unit_record_hashes"][EXPECTED_CASE_IDS[0]] = "0" * 64
        manifest = finalized({**manifest, "manifest_sha256": None}, "manifest_sha256")
        bad = candidate_with(candidate, manifest_bytes=canonical_bytes_v2(manifest))
    elif mutation == "cross_ref":
        first_path, first_file = next(iter(candidate.case_files.items()))
        record = cast(dict[str, Any], loads_v2(first_file.content.decode("utf-8")))
        record["case_artifact_paths"]["case_input"] = "wrong/path.json"
        bad = candidate_replacing_case_record(candidate, first_path, record)
    else:
        bad = candidate_with(
            candidate,
            ledger_ready_metadata={
                **candidate.ledger_ready_metadata,
                "created_file_hash_count": 1,
            },
        )
    with pytest.raises(ValueError):
        module.validate_candidate_bundle(bad)


@pytest.mark.parametrize("artifact_path_key", EXPECTED_CASE_ARTIFACT_PATH_KEYS)
def test_validate_candidate_bundle_rejects_every_case_artifact_path_mutation(
    artifact_path_key: str,
) -> None:
    module = materializer_module()
    candidate = module.build_candidate_bundle(valid_authorization(module))
    case_id = EXPECTED_CASE_IDS[0]
    case_input_path = module._case_path(case_id, "case_input.json")
    case_input = cast(
        dict[str, Any], loads_v2(candidate.case_files[case_input_path].content.decode())
    )
    artifact_paths = cast(dict[str, Any], case_input["case_artifact_paths"])
    original = artifact_paths[artifact_path_key]
    if isinstance(original, list):
        artifact_paths[artifact_path_key] = list(reversed(original))
    else:
        artifact_paths[artifact_path_key] = f"{original}.unexpected"
    bad = candidate_replacing_case_record(candidate, case_input_path, case_input)
    with pytest.raises(ValueError, match="case_artifact_paths"):
        module.validate_candidate_bundle(bad)


def test_candidate_records_are_deeply_immutable() -> None:
    module = materializer_module()
    candidate = module.build_candidate_bundle(valid_authorization(module))
    case_id = EXPECTED_CASE_IDS[0]
    case_input_path = module._case_path(case_id, "case_input.json")
    sharing_path = module._case_path(case_id, "metric_schema_sharing.json")
    manifest_path = module._governance_path("sealed_bundle_manifest.json")

    with pytest.raises(TypeError):
        candidate.case_files[case_input_path].record["case_artifact_paths"][
            "method_observations"
        ] += ("bad/path.json",)
    with pytest.raises(AttributeError):
        candidate.case_files[sharing_path].record["sharing_group_ids"].append(
            "bad_group"
        )
    with pytest.raises(TypeError):
        candidate.governance_files[manifest_path].record["case_unit_record_hashes"][
            case_id
        ] = "0" * 64
    ready_created = candidate.ledger_ready_metadata["ready_created_file_hashes"]
    with pytest.raises(TypeError):
        ready_created[case_input_path] = "0" * 64


def test_seed_derivation_and_metric_sharing_contract() -> None:
    module = materializer_module()
    auth = valid_authorization(module)
    seed_root = module.derive_seed_root_hex(auth)
    assert seed_root == module.derive_seed_root_hex(copy.deepcopy(auth))
    changed_auth = finalized(
        {**auth, "source_tree_hash": "1" * 40, "artifact_sha256": None},
        "artifact_sha256",
    )
    assert seed_root != module.derive_seed_root_hex(changed_auth)
    key_0 = module.derive_philox_key_hex(seed_root, "0" * 64, replicate_index=0)
    key_4095 = module.derive_philox_key_hex(seed_root, "0" * 64, replicate_index=4095)
    assert key_0 == module.derive_philox_key_hex(seed_root, "0" * 64, replicate_index=0)
    assert key_0 != key_4095
    assert len(key_0) == 64
    with pytest.raises(ValueError, match="replicate_index"):
        module.derive_philox_key_hex(seed_root, "0" * 64, replicate_index=4096)
    candidate = module.build_candidate_bundle(auth)
    manifest = loads_v2(candidate.manifest_bytes.decode("utf-8"))
    assert isinstance(manifest, dict)
    manifest_obj = cast(dict[str, Any], manifest)
    metric_hashes = cast(dict[str, str], manifest_obj["metric_schema_hashes"])
    assert len(set(metric_hashes.values())) == 1
    sharing_records = [
        loads_v2(entry.content.decode("utf-8"))
        for path, entry in candidate.case_files.items()
        if path.endswith("/metric_schema_sharing.json")
    ]
    assert len(sharing_records) == 13
    for record in sharing_records:
        assert isinstance(record, dict)
        assert (
            record["canonical_owner_method_companion_group_id"] == EXPECTED_GROUP_IDS[0]
        )
        assert record["sharing_group_ids"] == list(EXPECTED_GROUP_IDS)
        assert (
            record["sharing_reason_code"]
            == "same_preregistered_estimand_metric_and_scoring_contract"
        )
        assert (
            record["comparability_requirement"]
            == "exact_des_and_cross_case_schema_parity"
        )
        assert record["independent_case_evidence"] is False
        assert record["retired_authority_reuse_claimed"] is False
        assert record["retired_reuse_authorization_ref_or_null"] is None


@pytest.mark.parametrize(
    ("seed_root", "case_hash"),
    [
        ("0" * 63, "0" * 64),
        ("A" * 64, "0" * 64),
        ("g" * 64, "0" * 64),
        (None, "0" * 64),
        ("0" * 64, "0" * 63),
        ("0" * 64, "A" * 64),
        ("0" * 64, "g" * 64),
        ("0" * 64, None),
    ],
)
def test_philox_rejects_bad_seed_and_case_hashes(
    seed_root: object, case_hash: object
) -> None:
    module = materializer_module()
    with pytest.raises(ValueError):
        module.derive_philox_key_hex(seed_root, case_hash, replicate_index=0)


@pytest.mark.parametrize("replicate_index", [True, False, -1, 4096, "0", None])
def test_philox_rejects_bad_replicate_index(replicate_index: object) -> None:
    module = materializer_module()
    with pytest.raises(ValueError, match="replicate_index"):
        module.derive_philox_key_hex(
            "0" * 64, "1" * 64, replicate_index=replicate_index
        )


def test_negative_ast_import_call_and_forbidden_payload_surface() -> None:
    module = materializer_module()
    source = module.__loader__.get_source(module.__name__)  # type: ignore[union-attr]
    assert source is not None
    tree = ast.parse(source)
    forbidden_imports = {
        "ims_deadlock.analysis",
        "ims_deadlock.terminal_classes",
        "ims_deadlock.ctmc",
        "ims_deadlock.historical_replay",
        "ims_deadlock.g6b_target_preflight",
        "subprocess",
        "socket",
        "urllib",
        "requests",
    }
    imported: set[str] = set()
    called: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Call):
            func = node.func
            called.add(ast.unparse(func))
            if isinstance(func, ast.Name):
                called.add(func.id)
            elif isinstance(func, ast.Attribute):
                called.add(func.attr)
    assert forbidden_ast_hits("import json\njson.loads('{}')\n") == {"json.loads"}
    assert not (imported & forbidden_imports)
    assert "_split_interrupted_fragment" not in source
    assert "T0RN_FRAGMENT" not in source
    assert not (
        called
        & {
            "open",
            "write",
            "writelines",
            "json.loads",
            "input",
            "run_des",
            "construct_ctmc",
        }
    )
    candidate = module.build_candidate_bundle(valid_authorization(module))
    forbidden_payload = b"".join(
        entry.content
        for path, entry in candidate.case_files.items()
        if not path.endswith(("/semantic_lineage_declaration.json",))
    )
    for token in (
        b"state_space_hash",
        b"terminal_classes",
        b"execution_result",
        b"metric_observations",
        b"retired_payload",
    ):
        assert token not in forbidden_payload


def parse_rs_ledger(raw: bytes) -> list[dict[str, Any]]:
    assert raw.endswith(b"\n")
    entries: list[dict[str, Any]] = []
    for frame in raw.splitlines(keepends=True):
        assert frame.startswith(b"\x1e")
        assert frame.endswith(b"\n")
        assert b"\r" not in frame
        value = loads_v2(frame[1:-1].decode("utf-8"))
        assert isinstance(value, dict)
        assert canonical_bytes_v2(value) == frame[1:-1]
        entries.append(cast(dict[str, Any], value))
    return entries


def materialized_files(repo_root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in repo_root.rglob("*"):
        if item.is_file():
            rel = item.relative_to(repo_root).as_posix()
            result[rel] = hashlib_sha256(item.read_bytes())
    return dict(sorted(result.items()))


def build_valid_candidate(module: Any) -> Any:
    return module.build_candidate_bundle(valid_authorization(module))


def auth_path(module: Any) -> str:
    return str(module._governance_path("construction_authorization.json"))


def ledger_path(module: Any) -> str:
    return str(module._governance_path("construction_ledger.json"))


def manifest_path(module: Any) -> str:
    return str(module._governance_path("sealed_bundle_manifest.json"))


def log_path(module: Any) -> str:
    return str(module._governance_path("construction_log.json"))


def write_existing_authorization(repo_root: Path, module: Any, candidate: Any) -> None:
    auth_file = candidate.governance_files[auth_path(module)]
    target = repo_root / auth_file.path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(auth_file.content)


def expected_temp_path(module: Any, rel_path: str, candidate: Any) -> str:
    token = (
        module.APPROVED_PLAN_ARTIFACT_HASH[:16]
        if rel_path == auth_path(module)
        else candidate.authorization["artifact_sha256"][:16]
    )
    path = Path(rel_path)
    return path.with_name(f".g6b-tmp-{token}-{path.name}").as_posix()


def all_expected_temp_paths(module: Any, candidate: Any) -> set[str]:
    return {
        expected_temp_path(module, rel, candidate)
        for rel in candidate.all_files
        if rel != ledger_path(module)
    }


def assert_no_real_roots(repo_root: Path) -> None:
    for root in ("case_units", "governance", "artifact", "science"):
        assert not (repo_root / root).exists()


def assert_authorization_precreated_only(
    repo_root: Path, module: Any, candidate: Any
) -> None:
    files = materialized_files(repo_root)
    assert files == {
        auth_path(module): candidate.governance_files[auth_path(module)].sha256
    }


def ledger_frame_events(repo_root: Path, module: Any) -> list[dict[str, Any]]:
    return parse_rs_ledger((repo_root / ledger_path(module)).read_bytes())


def test_r3_writer_uses_forward_only_append_dag_and_existing_authorization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = materializer_module()
    candidate = build_valid_candidate(module)
    write_existing_authorization(tmp_path, module, candidate)
    calls: list[str] = []
    original_validate = module.validate_candidate_bundle

    def validate_spy(bundle: Any) -> None:
        calls.append("validate")
        assert_authorization_precreated_only(tmp_path, module, candidate)
        original_validate(bundle)

    monkeypatch.setattr(module, "validate_candidate_bundle", validate_spy)
    module.materialize_candidate(tmp_path, candidate)

    assert calls == ["validate"]
    assert_no_real_roots(tmp_path)
    files = materialized_files(tmp_path)
    assert files == {path: entry.sha256 for path, entry in candidate.all_files.items()}
    assert len(files) == 394
    assert not any(
        (tmp_path / rel).exists() for rel in all_expected_temp_paths(module, candidate)
    )

    ledger_bytes = (tmp_path / ledger_path(module)).read_bytes()
    assert ledger_bytes == candidate.ledger_bytes
    validation = g6b_schema_contracts.validate_construction_ledger_bytes(ledger_bytes)
    entries = parse_rs_ledger(ledger_bytes)
    assert validation.entry_count == len(entries)
    assert validation.ledger_head_sha256 == entries[-1]["entry_sha256"]
    assert [entry["event_code"] for entry in entries[:2]] == [
        "WRITE_STARTED",
        "FILE_CREATED",
    ]
    assert entries[1]["created_file_hashes"] == {
        log_path(module): candidate.governance_files[log_path(module)].sha256
    }
    assert [
        next(iter(entry["created_file_hashes"])) for entry in entries[2:392]
    ] == list(candidate.case_files)
    assert entries[-1]["event_code"] == "READY_TO_SEAL"
    assert (
        entries[-1]["created_file_hashes"]
        == candidate.ledger_ready_metadata["ready_created_file_hashes"]
    )
    assert (
        cast(
            dict[str, Any],
            loads_v2((tmp_path / manifest_path(module)).read_text(encoding="utf-8")),
        )["construction_ledger_head_sha256"]
        == entries[-1]["entry_sha256"]
    )


def test_r3_writer_requires_existing_exact_authorization_and_validation_first(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = materializer_module()
    candidate = build_valid_candidate(module)
    with pytest.raises(ValueError, match="authorization_missing"):
        module.materialize_candidate(tmp_path, candidate)
    assert materialized_files(tmp_path) == {}

    write_existing_authorization(tmp_path, module, candidate)
    calls = 0

    def fail_validation(bundle: Any) -> None:
        nonlocal calls
        calls += 1
        raise ValueError("candidate_validation_failed")

    monkeypatch.setattr(module, "validate_candidate_bundle", fail_validation)
    with pytest.raises(ValueError, match="candidate_validation_failed"):
        module.materialize_candidate(tmp_path, candidate)
    assert calls == 1
    assert_authorization_precreated_only(tmp_path, module, candidate)


def test_r3_transient_contract_exact_tokens_and_manifest_temp_retained(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = materializer_module()
    candidate = build_valid_candidate(module)
    temps = all_expected_temp_paths(module, candidate)
    assert len(temps) == 393
    assert expected_temp_path(module, auth_path(module), candidate).endswith(
        f".g6b-tmp-{module.APPROVED_PLAN_ARTIFACT_HASH[:16]}-construction_authorization.json"
    )
    assert expected_temp_path(module, log_path(module), candidate).endswith(
        f".g6b-tmp-{candidate.authorization['artifact_sha256'][:16]}-construction_log.json"
    )
    assert ledger_path(module) not in temps

    write_existing_authorization(tmp_path, module, candidate)
    monkeypatch.setattr(
        module, "_MATERIALIZER_TEST_FAILURE_POINT", "before_manifest_rename"
    )
    with pytest.raises(RuntimeError, match="injected_failure"):
        module.materialize_candidate(tmp_path, candidate)
    retained = materialized_files(tmp_path)
    manifest_tmp = expected_temp_path(module, manifest_path(module), candidate)
    assert manifest_path(module) not in retained
    assert manifest_tmp in retained
    assert (
        retained[manifest_tmp]
        == candidate.governance_files[manifest_path(module)].sha256
    )
    assert not (
        tmp_path / expected_temp_path(module, ledger_path(module), candidate)
    ).exists()

    module.recover_interrupted_bundle(tmp_path, candidate.authorization)
    recovered = ledger_frame_events(tmp_path, module)[-1]
    assert recovered["event_code"] == "INTERRUPTED_PARTIAL"
    assert recovered["observed_partial_file_hashes"] == retained
    assert "ledger_append_interrupted" in recovered["refusal_reason_codes"]


def test_r3_atomic_create_is_no_replace_and_retains_temp_on_race(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = materializer_module()
    target = tmp_path / "root" / "sealed.json"
    token = "0123456789abcdef"
    calls = 0
    original_rename = module._atomic_rename_no_replace

    def racing_rename(src: Path, dst: Path) -> None:
        nonlocal calls
        calls += 1
        dst.write_bytes(b"old")
        original_rename(src, dst)

    monkeypatch.setattr(module, "_atomic_rename_no_replace", racing_rename)
    with pytest.raises(ValueError, match="final_exists"):
        module.create_atomic_file_exclusive(target, b"new", attempt_token=token)
    assert calls == 1
    assert target.read_bytes() == b"old"
    tmp = target.with_name(f".g6b-tmp-{token}-{target.name}")
    assert tmp.read_bytes() == b"new"

    with pytest.raises(ValueError, match="attempt_token"):
        module.create_atomic_file_exclusive(tmp_path / "missing-token.json", b"x")
    with pytest.raises(ValueError):
        module.create_atomic_file_exclusive(
            tmp_path / "escape" / ".." / "x.json", b"x", attempt_token=token
        )
    symlink_parent = tmp_path / "link_parent"
    symlink_parent.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        module.create_atomic_file_exclusive(
            symlink_parent / "x.json", b"x", attempt_token=token
        )


def test_r3_atomic_create_fails_closed_off_windows_and_retains_temp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = materializer_module()
    target = tmp_path / "root" / "sealed.json"
    token = "0123456789abcdef"
    monkeypatch.setattr(module, "_WINDOWS_CREATE_NEW_RENAME", False)
    with pytest.raises(ValueError, match="atomic_rename_platform"):
        module.create_atomic_file_exclusive(target, b"new", attempt_token=token)
    assert not target.exists()
    assert target.with_name(f".g6b-tmp-{token}-{target.name}").read_bytes() == b"new"


def test_r3_preflight_allows_repo_files_but_rejects_output_root_intrusions(
    tmp_path: Path,
) -> None:
    module = materializer_module()
    candidate = build_valid_candidate(module)
    (tmp_path / ".git").mkdir()
    (tmp_path / "README.md").write_text("repo file", encoding="utf-8")
    write_existing_authorization(tmp_path, module, candidate)
    unexpected = tmp_path / log_path(module)
    unexpected.parent.mkdir(parents=True, exist_ok=True)
    unexpected.write_bytes(b"old")
    with pytest.raises(ValueError, match="preexisting_output"):
        module.materialize_candidate(tmp_path, candidate)
    assert unexpected.read_bytes() == b"old"

    unexpected.unlink()
    target_root = tmp_path / "cases" / "discovery" / "g6b" / "target_certification"
    target_root.mkdir(parents=True)
    with pytest.raises(ValueError, match="reserved_output_root"):
        module.materialize_candidate(tmp_path, candidate)

    target_root.rmdir()
    history_root = tmp_path / "artifacts" / "g6b" / "history"
    history_root.mkdir(parents=True)
    (history_root / "README.txt").write_text("historical note", encoding="utf-8")
    module.materialize_candidate(tmp_path, candidate)
    assert (history_root / "README.txt").read_text(encoding="utf-8") == (
        "historical note"
    )

    tmp_path = tmp_path / "second"
    candidate = build_valid_candidate(module)
    write_existing_authorization(tmp_path, module, candidate)
    top_level_artifact_root = tmp_path / "artifacts" / "g6b" / "quantitative"
    top_level_artifact_root.mkdir(parents=True)
    with pytest.raises(ValueError, match="reserved_output_root"):
        module.materialize_candidate(tmp_path, candidate)

    top_level_artifact_root.rmdir()
    (tmp_path / "artifacts" / "g6b").rmdir()
    (tmp_path / "artifacts").rmdir()
    reservations = cast(
        dict[str, str],
        cast(
            dict[str, Any],
            loads_v2(candidate.manifest_bytes.decode("utf-8")),
        )["quantitative_output_root_reservations"],
    )
    assert len(reservations) == 26
    first_reservation = next(
        entry.record["repo_relative_posix_path"]
        for path, entry in candidate.case_files.items()
        if path.endswith("/projections/output_root_reservation_des.json")
    )
    assert isinstance(first_reservation, str)
    (tmp_path / first_reservation).mkdir(parents=True)
    with pytest.raises(ValueError, match="reserved_output_root"):
        module.materialize_candidate(tmp_path, candidate)


@pytest.mark.parametrize(
    "mutation",
    ["crlf", "blank", "noncanonical", "corrupt", "reordered", "truncated"],
)
def test_r3_ledger_rejects_malformed_chains(mutation: str) -> None:
    module = materializer_module()
    candidate = build_valid_candidate(module)
    raw = candidate.ledger_bytes
    frames = raw.splitlines(keepends=True)
    if mutation == "crlf":
        bad = raw.replace(b"\n", b"\r\n", 1)
    elif mutation == "blank":
        bad = frames[0] + b"\n" + b"".join(frames[1:])
    elif mutation == "noncanonical":
        entry = parse_rs_ledger(frames[0])[0]
        bad = (
            b"\x1e"
            + canonical_bytes_v2({"z": 1, **entry})
            + b"\n"
            + b"".join(frames[1:])
        )
    elif mutation == "corrupt":
        bad = frames[0][:-3] + b"xx\n" + b"".join(frames[1:])
    elif mutation == "reordered":
        bad = frames[1] + frames[0] + b"".join(frames[2:])
    else:
        bad = raw[:-7]
    with pytest.raises(ValueError):
        module.validate_candidate_bundle(candidate_with(candidate, ledger_bytes=bad))


def test_r3_candidate_ledger_is_bound_to_schema_validator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = materializer_module()
    candidate = build_valid_candidate(module)
    calls: list[bytes] = []
    original = g6b_schema_contracts.validate_construction_ledger_bytes

    def validating_spy(raw: bytes) -> Any:
        calls.append(raw)
        return original(raw)

    monkeypatch.setattr(
        g6b_schema_contracts,
        "validate_construction_ledger_bytes",
        validating_spy,
    )
    module.validate_candidate_bundle(candidate)
    assert calls == [candidate.ledger_bytes]


def test_r3_append_ledger_derives_index_prior_and_rejects_forged_transition(
    tmp_path: Path,
) -> None:
    module = materializer_module()
    candidate = build_valid_candidate(module)
    lp = tmp_path / ledger_path(module)
    first = module.append_ledger_entry_exclusive(
        lp,
        authorization=candidate.authorization,
        event_code="WRITE_STARTED",
        entry_index=99,
        prior_entry_sha256_or_null="0" * 64,
        candidate_log_sha256_or_null=candidate.governance_files[
            log_path(module)
        ].sha256,
    )
    assert first.record["entry_index"] == 0
    assert first.record["prior_entry_sha256_or_null"] is None
    with pytest.raises(ValueError, match="ledger_transition"):
        module.append_ledger_entry_exclusive(
            lp,
            authorization=candidate.authorization,
            event_code="READY_TO_SEAL",
            entry_index=1,
            prior_entry_sha256_or_null=first.sha256,
            candidate_log_sha256_or_null=candidate.governance_files[
                log_path(module)
            ].sha256,
        )
    assert len(parse_rs_ledger(lp.read_bytes())) == 1


def test_r3_concurrent_append_lease_allows_one_writer_and_valid_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = materializer_module()
    lp = tmp_path / ledger_path(module)
    original_read_ledger_bytes = module._read_locked_ledger_bytes
    race = threading.Barrier(2)

    def raced_read_ledger_bytes(lease: Any) -> bytes:
        result = cast(bytes, original_read_ledger_bytes(lease))
        try:
            race.wait(timeout=1.0)
        except threading.BrokenBarrierError:
            pass
        return result

    monkeypatch.setattr(module, "_read_locked_ledger_bytes", raced_read_ledger_bytes)
    successes: list[Any] = []
    failures: list[BaseException] = []

    def append_started() -> None:
        try:
            successes.append(
                module.append_ledger_entry_exclusive(
                    lp,
                    authorization=None,
                    event_code="PREWRITE_REFUSED",
                    entry_index=-1,
                    prior_entry_sha256_or_null=None,
                    candidate_log_sha256_or_null=None,
                    refusal_reason_codes=["unauthorized_case_creation_attempt"],
                )
            )
        except BaseException as exc:
            failures.append(exc)

    threads = [threading.Thread(target=append_started) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5.0)
    assert all(not thread.is_alive() for thread in threads)

    assert len(successes) == 1
    assert len(failures) == 1
    assert "ledger_lease" in str(failures[0])
    entries = parse_rs_ledger(lp.read_bytes())
    assert [entry["entry_index"] for entry in entries] == [0]
    assert [entry["event_code"] for entry in entries] == ["PREWRITE_REFUSED"]
    g6b_schema_contracts.validate_construction_ledger_bytes(lp.read_bytes())


def test_r3_materialize_lease_blocks_recovery_interleaving(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = materializer_module()
    candidate = build_valid_candidate(module)
    write_existing_authorization(tmp_path, module, candidate)
    original_create = module._create_candidate_file
    recovery_failures: list[BaseException] = []

    def create_spy(repo_root: Path, bundle: Any, rel_path: str, **kwargs: Any) -> None:
        if rel_path == log_path(module) and not recovery_failures:
            try:
                module.recover_interrupted_bundle(repo_root, bundle.authorization)
            except BaseException as exc:
                recovery_failures.append(exc)
        original_create(repo_root, bundle, rel_path, **kwargs)

    monkeypatch.setattr(module, "_create_candidate_file", create_spy)
    module.materialize_candidate(tmp_path, candidate)

    assert len(recovery_failures) == 1
    assert "ledger_lease" in str(recovery_failures[0])
    ledger_bytes = (tmp_path / ledger_path(module)).read_bytes()
    assert ledger_bytes == candidate.ledger_bytes
    g6b_schema_contracts.validate_construction_ledger_bytes(ledger_bytes)


def test_r3_ledger_lease_releases_after_validation_exception(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = materializer_module()
    candidate = build_valid_candidate(module)
    lp = tmp_path / ledger_path(module)
    original_read_ledger_bytes = module._read_locked_ledger_bytes
    calls = 0

    def failing_once_read_ledger_bytes(lease: Any) -> bytes:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise ValueError("injected_validation_failure")
        return cast(bytes, original_read_ledger_bytes(lease))

    monkeypatch.setattr(
        module, "_read_locked_ledger_bytes", failing_once_read_ledger_bytes
    )
    with pytest.raises(ValueError, match="injected_validation_failure"):
        module.append_ledger_entry_exclusive(
            lp,
            authorization=candidate.authorization,
            event_code="WRITE_STARTED",
            entry_index=-1,
            prior_entry_sha256_or_null=None,
            candidate_log_sha256_or_null=candidate.governance_files[
                log_path(module)
            ].sha256,
        )
    assert not lp.exists() or lp.read_bytes() == b""

    written = module.append_ledger_entry_exclusive(
        lp,
        authorization=candidate.authorization,
        event_code="WRITE_STARTED",
        entry_index=-1,
        prior_entry_sha256_or_null=None,
        candidate_log_sha256_or_null=candidate.governance_files[
            log_path(module)
        ].sha256,
    )
    assert parse_rs_ledger(lp.read_bytes())[-1]["entry_sha256"] == written.sha256


def test_r3_append_and_recovery_reject_mixed_valid_auth_prefix_without_mutation(
    tmp_path: Path,
) -> None:
    module = materializer_module()
    candidate = build_valid_candidate(module)
    current_log = candidate.governance_files[log_path(module)].sha256
    foreign = module.append_ledger_entry_exclusive(
        tmp_path / "foreign.json",
        authorization=auth_with_patch(
            module,
            {
                "artifact_id": "g6b_discovery_case_construction_v1_other_auth",
                "source_head": "f" * 40,
                "source_tree_hash": "e" * 40,
            },
        ),
        event_code="WRITE_STARTED",
        entry_index=-1,
        prior_entry_sha256_or_null=None,
        candidate_log_sha256_or_null="f" * 64,
    )
    lp = tmp_path / ledger_path(module)
    lp.parent.mkdir(parents=True, exist_ok=True)
    lp.write_bytes(foreign.frame)
    before = lp.read_bytes()

    with pytest.raises(ValueError, match="ledger_identity"):
        module.append_ledger_entry_exclusive(
            lp,
            authorization=candidate.authorization,
            event_code="FILE_CREATED",
            entry_index=-1,
            prior_entry_sha256_or_null=None,
            candidate_log_sha256_or_null=current_log,
            created_file_hashes={log_path(module): current_log},
        )
    assert lp.read_bytes() == before

    write_existing_authorization(tmp_path, module, candidate)
    with pytest.raises(ValueError, match="ledger_identity"):
        module.recover_interrupted_bundle(tmp_path, candidate.authorization)
    assert lp.read_bytes() == before


def test_r3_unauthorized_prewrite_then_current_write_started_is_legal(
    tmp_path: Path,
) -> None:
    module = materializer_module()
    candidate = build_valid_candidate(module)
    lp = tmp_path / ledger_path(module)
    prewrite = module.append_ledger_entry_exclusive(
        lp,
        authorization=None,
        event_code="PREWRITE_REFUSED",
        entry_index=99,
        prior_entry_sha256_or_null="0" * 64,
        candidate_log_sha256_or_null="f" * 64,
        refusal_reason_codes=["unauthorized_case_creation_attempt"],
    )
    assert prewrite.record["attempt_id"] == module._UNAUTHORIZED_ATTEMPT_ID
    assert prewrite.record["construction_authorization_sha256_or_null"] is None
    assert prewrite.record["source_head_or_null"] is None
    assert prewrite.record["source_tree_hash_or_null"] is None
    assert prewrite.record["candidate_log_sha256_or_null"] is None
    g6b_schema_contracts.validate_construction_ledger_bytes(lp.read_bytes())

    current = module.append_ledger_entry_exclusive(
        lp,
        authorization=candidate.authorization,
        event_code="WRITE_STARTED",
        entry_index=-1,
        prior_entry_sha256_or_null=None,
        candidate_log_sha256_or_null=candidate.governance_files[
            log_path(module)
        ].sha256,
    )
    entries = parse_rs_ledger(lp.read_bytes())
    assert [entry["event_code"] for entry in entries] == [
        "PREWRITE_REFUSED",
        "WRITE_STARTED",
    ]
    assert entries[-1]["entry_sha256"] == current.sha256


def test_r3_invalid_authorization_can_only_append_unauthorized_prewrite(
    tmp_path: Path,
) -> None:
    module = materializer_module()
    lp = tmp_path / ledger_path(module)
    invalid_auth = {"schema_version": module.AUTHORIZATION_SCHEMA_VERSION}
    frame = module.append_ledger_entry_exclusive(
        lp,
        authorization=invalid_auth,
        event_code="PREWRITE_REFUSED",
        entry_index=-1,
        prior_entry_sha256_or_null=None,
        candidate_log_sha256_or_null=None,
        refusal_reason_codes=[
            "ledger_append_interrupted",
            "unauthorized_case_creation_attempt",
        ],
    )
    assert frame.record["attempt_id"] == module._UNAUTHORIZED_ATTEMPT_ID
    assert frame.record["refusal_reason_codes"] == [
        "ledger_append_interrupted",
        "unauthorized_case_creation_attempt",
    ]
    g6b_schema_contracts.validate_construction_ledger_bytes(lp.read_bytes())

    before = lp.read_bytes()
    with pytest.raises(ValueError, match="authorization"):
        module.append_ledger_entry_exclusive(
            lp,
            authorization=invalid_auth,
            event_code="WRITE_STARTED",
            entry_index=-1,
            prior_entry_sha256_or_null=None,
            candidate_log_sha256_or_null="f" * 64,
        )
    assert lp.read_bytes() == before


def test_r3_recovery_prewrite_torn_tail_is_prewrite_and_idempotent(
    tmp_path: Path,
) -> None:
    module = materializer_module()
    lp = tmp_path / ledger_path(module)
    lp.parent.mkdir(parents=True, exist_ok=True)
    fragments = [b'\x1e{"partial":', b'\x1e{"another":true']
    lp.write_bytes(b"".join(fragments))

    module.recover_interrupted_bundle(tmp_path, None)
    first = lp.read_bytes()
    g6b_schema_contracts.validate_construction_ledger_bytes(first)
    entries = parse_rs_ledger(first[first.rfind(b"\x1e") :])
    assert entries[-1]["event_code"] == "PREWRITE_REFUSED"
    assert entries[-1]["attempt_id"] == module._UNAUTHORIZED_ATTEMPT_ID
    assert entries[-1]["candidate_log_sha256_or_null"] is None
    assert entries[-1]["interrupted_fragments"] == [
        {
            "fragment_index": index,
            "fragment_sha256": hashlib_sha256(fragment),
            "fragment_byte_count": len(fragment),
        }
        for index, fragment in enumerate(fragments)
    ]

    module.recover_interrupted_bundle(tmp_path, None)
    assert lp.read_bytes() == first


def test_r3_recovery_absent_ledger_appends_valid_auth_prewrite_and_is_idempotent(
    tmp_path: Path,
) -> None:
    module = materializer_module()
    candidate = build_valid_candidate(module)
    lp = tmp_path / ledger_path(module)
    assert not lp.exists()

    module.recover_interrupted_bundle(tmp_path, candidate.authorization)
    first = lp.read_bytes()
    g6b_schema_contracts.validate_construction_ledger_bytes(first)
    entries = parse_rs_ledger(first)
    assert [entry["event_code"] for entry in entries] == ["PREWRITE_REFUSED"]
    assert entries[0]["attempt_id"] == candidate.authorization["artifact_id"]
    assert (
        entries[0]["construction_authorization_sha256_or_null"]
        == candidate.authorization["artifact_sha256"]
    )
    assert entries[0]["source_head_or_null"] == candidate.authorization["source_head"]
    assert (
        entries[0]["source_tree_hash_or_null"]
        == candidate.authorization["source_tree_hash"]
    )
    assert entries[0]["candidate_log_sha256_or_null"] is None
    assert entries[0]["refusal_reason_codes"] == ["ledger_append_interrupted"]

    module.recover_interrupted_bundle(tmp_path, candidate.authorization)
    assert lp.read_bytes() == first


def test_r3_recovery_zero_byte_ledger_appends_unauthorized_prewrite_and_is_idempotent(
    tmp_path: Path,
) -> None:
    module = materializer_module()
    lp = tmp_path / ledger_path(module)
    lp.parent.mkdir(parents=True, exist_ok=True)
    lp.write_bytes(b"")

    module.recover_interrupted_bundle(tmp_path, None)
    first = lp.read_bytes()
    g6b_schema_contracts.validate_construction_ledger_bytes(first)
    entries = parse_rs_ledger(first)
    assert [entry["event_code"] for entry in entries] == ["PREWRITE_REFUSED"]
    assert entries[0]["attempt_id"] == module._UNAUTHORIZED_ATTEMPT_ID
    assert entries[0]["construction_authorization_sha256_or_null"] is None
    assert entries[0]["source_head_or_null"] is None
    assert entries[0]["source_tree_hash_or_null"] is None
    assert entries[0]["candidate_log_sha256_or_null"] is None
    assert entries[0]["refusal_reason_codes"] == [
        "ledger_append_interrupted",
        "unauthorized_case_creation_attempt",
    ]

    module.recover_interrupted_bundle(tmp_path, None)
    assert lp.read_bytes() == first


def test_r3_invalid_non_prewrite_append_empty_ledger_then_recovery_is_legal(
    tmp_path: Path,
) -> None:
    module = materializer_module()
    lp = tmp_path / ledger_path(module)
    with pytest.raises(ValueError, match="authorization"):
        module.append_ledger_entry_exclusive(
            lp,
            authorization={"schema_version": module.AUTHORIZATION_SCHEMA_VERSION},
            event_code="WRITE_STARTED",
            entry_index=-1,
            prior_entry_sha256_or_null=None,
            candidate_log_sha256_or_null="f" * 64,
        )
    assert not lp.exists() or lp.read_bytes() == b""

    module.recover_interrupted_bundle(tmp_path, None)
    recovered = lp.read_bytes()
    g6b_schema_contracts.validate_construction_ledger_bytes(recovered)
    stable = lp.read_bytes()
    module.recover_interrupted_bundle(tmp_path, None)
    assert lp.read_bytes() == stable


def test_r3_recovery_after_complete_prewrite_binds_pending_prewrite_fragment(
    tmp_path: Path,
) -> None:
    module = materializer_module()
    lp = tmp_path / ledger_path(module)
    first = module.append_ledger_entry_exclusive(
        lp,
        authorization=None,
        event_code="PREWRITE_REFUSED",
        entry_index=-1,
        prior_entry_sha256_or_null=None,
        candidate_log_sha256_or_null=None,
        refusal_reason_codes=["unauthorized_case_creation_attempt"],
    )
    fragments = [b'\x1e{"partial":', b'\x1e{"another":true']
    with lp.open("ab") as handle:
        handle.write(b"".join(fragments))

    module.recover_interrupted_bundle(tmp_path, None)
    recovered = lp.read_bytes()
    g6b_schema_contracts.validate_construction_ledger_bytes(recovered)
    entries = parse_rs_ledger(recovered[recovered.rfind(b"\x1e") :])
    assert entries[-1]["event_code"] == "PREWRITE_REFUSED"
    assert entries[-1]["prior_entry_sha256_or_null"] == first.sha256
    assert entries[-1]["interrupted_fragments"] == [
        {
            "fragment_index": index,
            "fragment_sha256": hashlib_sha256(fragment),
            "fragment_byte_count": len(fragment),
        }
        for index, fragment in enumerate(fragments)
    ]

    module.recover_interrupted_bundle(tmp_path, None)
    assert lp.read_bytes() == recovered


@pytest.mark.parametrize(
    "failure_point",
    [
        "after_write_started",
        "after_log_file_rename",
        "after_log",
        *[f"after_case_{index:03d}_file_rename" for index in range(1, 31)],
        *[f"after_case_{index:03d}" for index in range(1, 31)],
        "after_case_390",
        "before_ready",
        "before_manifest_rename",
    ],
)
def test_r3_interruption_recovery_preserves_partial_bytes_and_terminalizes_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure_point: str
) -> None:
    module = materializer_module()
    candidate = build_valid_candidate(module)
    write_existing_authorization(tmp_path, module, candidate)
    monkeypatch.setattr(module, "_MATERIALIZER_TEST_FAILURE_POINT", failure_point)
    with pytest.raises(RuntimeError, match="injected_failure"):
        module.materialize_candidate(tmp_path, candidate)
    before = materialized_files(tmp_path)
    assert manifest_path(module) not in before

    module.recover_interrupted_bundle(tmp_path, candidate.authorization)
    after = materialized_files(tmp_path)
    for rel, digest in before.items():
        if rel != ledger_path(module):
            assert after[rel] == digest
    entries = ledger_frame_events(tmp_path, module)
    assert entries[-1]["event_code"] == "INTERRUPTED_PARTIAL"
    assert entries[-1]["observed_partial_file_hashes"] == before
    assert entries[-1]["causal_entry_sha256_or_null"] == entries[-2]["entry_sha256"]
    assert "ledger_append_interrupted" in entries[-1]["refusal_reason_codes"]

    stable = (tmp_path / ledger_path(module)).read_bytes()
    module.recover_interrupted_bundle(tmp_path, candidate.authorization)
    assert (tmp_path / ledger_path(module)).read_bytes() == stable
    with pytest.raises(ValueError, match="non_resumable"):
        module.materialize_candidate(tmp_path, candidate)


def test_r3_recovery_records_general_rs_torn_append_fragments(
    tmp_path: Path,
) -> None:
    module = materializer_module()
    candidate = build_valid_candidate(module)
    lp = tmp_path / ledger_path(module)
    first = module.append_ledger_entry_exclusive(
        lp,
        authorization=candidate.authorization,
        event_code="WRITE_STARTED",
        entry_index=0,
        prior_entry_sha256_or_null=None,
        candidate_log_sha256_or_null=candidate.governance_files[
            log_path(module)
        ].sha256,
    )
    fragments = [b'\x1e{"event_code":', b'\x1e{"another":true']
    with lp.open("ab") as handle:
        for fragment in fragments:
            handle.write(fragment)
    module.recover_interrupted_bundle(tmp_path, candidate.authorization)
    raw = lp.read_bytes()
    assert all(fragment in raw for fragment in fragments)
    entries = parse_rs_ledger(raw[raw.rfind(b"\x1e") :])
    recovered = entries[-1]
    assert recovered["event_code"] == "INTERRUPTED_PARTIAL"
    assert recovered["prior_entry_sha256_or_null"] == first.sha256
    assert recovered["interrupted_fragments"] == [
        {
            "fragment_index": index,
            "fragment_sha256": hashlib_sha256(fragment),
            "fragment_byte_count": len(fragment),
        }
        for index, fragment in enumerate(fragments)
    ]
    assert "ledger_append_interrupted" in recovered["refusal_reason_codes"]


def test_r3_completed_manifest_recovery_is_strict_read_only_sealed_success(
    tmp_path: Path,
) -> None:
    module = materializer_module()
    candidate = build_valid_candidate(module)
    write_existing_authorization(tmp_path, module, candidate)
    module.materialize_candidate(tmp_path, candidate)
    before = materialized_files(tmp_path)
    ledger_before = (tmp_path / ledger_path(module)).read_bytes()
    assert before == {path: entry.sha256 for path, entry in candidate.all_files.items()}
    assert not any(
        (tmp_path / rel).exists() for rel in all_expected_temp_paths(module, candidate)
    )

    module.recover_interrupted_bundle(tmp_path, candidate.authorization)
    assert materialized_files(tmp_path) == before
    assert (tmp_path / ledger_path(module)).read_bytes() == ledger_before

    with (tmp_path / ledger_path(module)).open("ab") as handle:
        handle.write(b"extra")
    with pytest.raises(ValueError, match="post_seal_ledger_mutation"):
        module.recover_interrupted_bundle(tmp_path, candidate.authorization)
    assert (tmp_path / ledger_path(module)).read_bytes() == ledger_before + b"extra"

    (tmp_path / ledger_path(module)).write_bytes(ledger_before)
    (tmp_path / next(iter(candidate.case_files))).write_bytes(b"mutated")
    with pytest.raises(ValueError):
        module.recover_interrupted_bundle(tmp_path, candidate.authorization)
    assert (tmp_path / ledger_path(module)).read_bytes() == ledger_before
