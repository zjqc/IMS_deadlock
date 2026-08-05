"""G6-B case-construction candidate builder and create-new materializer.

This module builds the reviewed discovery-only construction candidate bytes and
writes them only through the approved create-new ledger/materialization DAG. It
does not enumerate states, classify terminal sets, run DES, solve CTMCs, read
retired outcome payloads, or advance scientific status.
"""

from __future__ import annotations

import hashlib
import os
import re
import threading
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, TypeAlias, cast

from ims_deadlock import g6b_schema_contracts
from ims_deadlock.g6b_canonical_json import (
    canonical_bytes_v2,
    canonical_sha256_v2,
    loads_v2,
    verify_finalized_self_hash,
)

_msvcrt: Any
if os.name == "nt":
    import msvcrt as _msvcrt
else:
    _msvcrt = None

JsonValue: TypeAlias = Any
JsonObject: TypeAlias = dict[str, Any]
LedgerRecord: TypeAlias = tuple[JsonObject, tuple[bytes, ...]]

BUNDLE_ID = "g6b_discovery_case_construction_v1"
AUTHORIZATION_SCHEMA_VERSION = "ims-deadlock/g6b-construction-authorization/v2"
APPROVED_CORRIGENDUM_HASH = (
    "ff469d9c5105835fde5feb170e501bdde14506df50632990f7c2cddc251da36c"
)
APPROVED_PLAN_ARTIFACT_HASH = (
    "81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7"
)
PLAN_REVIEW_ARTIFACT_HASH = (
    "da6da7c2e513e11761e439f8b43ef6260556c912d3e730f94f15eae088d90ea0"
)
FROZEN_ROW_FAMILY_MATRIX_SHA256 = (
    "487d81aa79a7bca681db81f19a4d6bd315668c43b1c4538c47f01f099d8e205f"
)
CASE_CONSTRUCTION_SCHEMA_SHA256 = (
    "4d8d55ce85cb8c8b2260c718ab3d5e0325e80312712dbd07f628f47f46e329cc"
)
CATALOG_SCHEMA_VERSION = "ims-deadlock/g6b-case-recipe-catalog/v1"
CANONICAL_JSON_VERSION = "ims-deadlock/g6b-canonical-json/v2"
CASE_RECIPE_REGISTRY_SHA256 = (
    "e94246b42ec762221dfc1dec066498c4b279a0b9c4266380243b40dd75cc1b72"
)
RANDOM_STREAM_PROJECTION_VERSION = (
    "ims-deadlock/g6b-random-stream-manifest-projection/v1"
)
OUTPUT_ROOT_RESERVATION_PROJECTION_VERSION = (
    "ims-deadlock/g6b-output-root-reservation-projection/v1"
)
AGV_RELEASE_TARGET_SCHEMA_VERSION = (
    "ims-deadlock/g6-terminal-stopping-partition-agv-release-on-arrival/v1"
)
INCOMPLETE_BATCH_CONDITION = (
    "truncation_missing_input_unexpected_refusal_incomplete_batch"
)

AUTHORIZATION_FIELDS = (
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
AUTHORIZED_SOURCE_FILE_PATHS = (
    "cases/discovery/g6b/row_families/structural_discovery_v1/case_construction_schema.json",
    "cases/discovery/g6b/row_families/structural_discovery_v1/row_family_protocol.json",
    "docs/verification/G6_B_CASE_CONSTRUCTION_TASK2_SOURCE_REVIEW.md",
    "src/ims_deadlock/g6b_case_materializer.py",
    "src/ims_deadlock/g6b_row_family_protocol.py",
    "src/ims_deadlock/g6b_schema_contracts.py",
    "tests/test_g6b_case_materializer.py",
    "tests/test_g6b_row_family_protocol.py",
    "tests/test_g6b_schema_contracts.py",
)
ALLOWED_OPERATIONS = (
    "write_sealed_case_input",
    "write_input_projection",
    "write_method_declaration",
    "write_companion_group_declaration",
    "write_inert_random_stream_manifest",
    "reserve_inert_output_root",
    "write_sealed_prediction",
    "write_metric_schema",
    "write_semantic_lineage_declaration",
    "compute_input_hash",
    "write_sealed_bundle_manifest",
    "append_construction_ledger",
)
FORBIDDEN_OPERATIONS = (
    "enumerate_states",
    "classify_terminal_sets",
    "certify_target",
    "construct_ctmc",
    "solve_ctmc",
    "run_des",
    "score_hypothesis",
    "inspect_g6b_output",
    "materialize_quantitative_root",
    "write_observation",
    "advance_scientific_status",
)
SEALED_BUNDLE_MANIFEST_FIELDS = (
    "schema_version",
    "bundle_id",
    "construction_authorization_hash",
    "planned_case_unit_ids",
    "planned_method_observation_ids",
    "planned_method_companion_group_ids",
    "case_unit_record_hashes",
    "method_observation_record_hashes",
    "method_companion_group_record_hashes",
    "mandatory_control_ids",
    "fingerprint_record_hashes",
    "sealed_prediction_hashes",
    "semantic_lineage_declaration_hashes",
    "metric_schema_hashes",
    "quantitative_output_root_reservations",
    "planned_case_unit_count",
    "planned_method_count",
    "planned_companion_group_count",
    "manifest_sha256",
    "construction_log_sha256",
    "construction_ledger_head_sha256",
    "metric_schema_sharing_record_hashes",
    "case_file_count",
    "governance_file_count",
    "total_file_count",
)
CONSTRUCTION_LOG_FIELDS = (
    "schema_version",
    "log_id",
    "bundle_id",
    "construction_authorization_sha256",
    "source_head",
    "source_tree_hash",
    "source_file_hashes",
    "case_construction_schema_sha256",
    "case_recipe_catalog_schema_version",
    "case_recipe_registry_sha256",
    "case_recipe_hashes",
    "case_transform_records",
    "candidate_case_unit_ids",
    "candidate_method_observation_ids",
    "candidate_method_companion_group_ids",
    "planned_case_file_paths",
    "write_order",
    "forbidden_operation_checks",
    "log_sha256",
)
LEDGER_ENTRY_FIELDS = (
    "schema_version",
    "bundle_id",
    "attempt_id",
    "entry_index",
    "event_code",
    "prior_entry_sha256_or_null",
    "construction_authorization_sha256_or_null",
    "source_head_or_null",
    "source_tree_hash_or_null",
    "candidate_log_sha256_or_null",
    "created_file_hashes",
    "observed_partial_file_hashes",
    "refusal_reason_codes",
    "causal_entry_sha256_or_null",
    "interrupted_fragments",
    "entry_sha256",
)
CASE_UNIT_IDS = (
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
MANDATORY_CONTROL_IDS = (
    "NC_AGV_RESERVATION_BOUNDARY",
    "NC_CALENDAR_EMPTY_TERMINAL",
    "NC_DGLOBAL_ONLY_WITH_DLOCAL",
    "NC_LOCAL_BYPASS_COMPLETES",
    "NC_OR_OF_AND_FEASIBLE_BRANCH",
    "NC_POLICY_ONLY_STALL",
    "NC_UNSELECTED_LIVELOCK",
)
ESTIMAND_IDS = (
    "g6b_estimand_theta_global_before_success_v1",
    "g6b_estimand_theta_local_before_success_v1",
    "g6b_estimand_theta_selected_bad_before_success_v1",
)

_ROSTER = (
    {
        "case": "g6b_cu_nc_local_bypass_completes_v1",
        "family": "local_bypass_completion_family",
        "stem": "nc_local_bypass_completes",
        "mode": "explicit_finite_lts_input",
        "template": "g6b_recipe_nc_local_bypass_completes_v1",
        "control": "NC_LOCAL_BYPASS_COMPLETES",
        "expected": "D_local_not_admitted/reachable_completion_bypass",
        "falsifiers": (
            "violated_A2b_premise",
            "reachable_completion_bypass",
            "proof_check_failure",
        ),
        "resources": ("r_hold:buffer:1", "r_req:machine:1"),
        "routes": ("route_job_a:[r_hold,r_req,bypass,complete]",),
        "model_transitions": (
            "t_bypass:release:waiting:bypassed:[]:[r_hold:1]",
            "t_complete:complete:bypassed:complete:[]:[]",
        ),
        "states": ("f_complete", "s_bypass", "s_local_candidate"),
        "initial": "s_local_candidate",
        "marked": ("f_complete",),
        "transitions": (
            "s_bypass:t_complete:f_complete",
            "s_local_candidate:t_bypass:s_bypass",
        ),
    },
    {
        "case": "g6b_cu_nc_unselected_livelock_v1",
        "family": "unselected_livelock_family",
        "stem": "nc_unselected_livelock",
        "mode": "explicit_finite_lts_input",
        "template": "g6b_recipe_nc_unselected_livelock_v1",
        "control": "NC_UNSELECTED_LIVELOCK",
        "expected": "R_livelock/not_selected_bad_class",
        "falsifiers": (
            "selected_as_D_global",
            "selected_as_D_local",
            "missing_closed_recurrent_class",
        ),
        "resources": ("r_loop:machine:1",),
        "routes": ("route_job_a:[loop_a,loop_b]",),
        "model_transitions": (
            "t_loop_ab:move:loop_a:loop_b:[]:[]",
            "t_loop_ba:move:loop_b:loop_a:[]:[]",
        ),
        "states": ("f_complete", "r_livelock_a", "r_livelock_b"),
        "initial": "r_livelock_a",
        "marked": ("f_complete",),
        "transitions": (
            "r_livelock_a:t_loop_ab:r_livelock_b",
            "r_livelock_b:t_loop_ba:r_livelock_a",
        ),
    },
    {
        "case": "g6b_cu_nc_calendar_empty_terminal_v1",
        "family": "calendar_empty_terminal_family",
        "stem": "nc_calendar_empty_terminal",
        "mode": "explicit_finite_lts_input",
        "template": "g6b_recipe_nc_calendar_empty_terminal_v1",
        "control": "NC_CALENDAR_EMPTY_TERMINAL",
        "expected": "R_terminal/not_resource_deadlock",
        "falsifiers": (
            "selected_as_D_global",
            "selected_as_D_local",
            "resource_wait_cycle_present",
        ),
        "resources": ("r_idle:machine:1",),
        "routes": ("route_job_a:[terminal]",),
        "model_transitions": (),
        "states": ("f_complete", "r_terminal"),
        "initial": "r_terminal",
        "marked": ("f_complete",),
        "transitions": (),
    },
    {
        "case": "g6b_cu_nc_policy_only_stall_v1",
        "family": "policy_only_stall_family",
        "stem": "nc_policy_only_stall",
        "mode": "explicit_finite_lts_input",
        "template": "g6b_recipe_nc_policy_only_stall_v1",
        "control": "NC_POLICY_ONLY_STALL",
        "expected": "P_policy/policy_only_not_plant_partition",
        "falsifiers": (
            "plant_partition_changed_by_policy",
            "plant_completion_path_missing",
        ),
        "resources": ("r_machine:machine:1",),
        "routes": ("route_job_a:[processing,complete]",),
        "model_transitions": (
            "t_plant_complete:complete:processing:complete:[]:[r_machine:1]",
        ),
        "states": ("f_complete", "p_policy_stall"),
        "initial": "p_policy_stall",
        "marked": ("f_complete",),
        "transitions": ("p_policy_stall:t_plant_complete:f_complete",),
        "policy": (
            "analysis_overlay_only",
            ("t_plant_complete",),
            "policy_overlay_does_not_change_plant_partition_v1",
        ),
    },
    {
        "case": "g6b_cu_nc_or_of_and_feasible_branch_v1",
        "family": "or_of_and_feasible_branch_family",
        "stem": "nc_or_of_and_feasible_branch",
        "mode": "model_generated_lts",
        "template": "g6b_recipe_nc_or_of_and_feasible_branch_v1",
        "control": "NC_OR_OF_AND_FEASIBLE_BRANCH",
        "expected": "D_local_not_admitted/feasible_branch_exists",
        "falsifiers": ("all_request_alternatives_blocked", "feasible_branch_ignored"),
        "resources": ("r_block_a:buffer:1", "r_block_b:machine:1", "r_free:buffer:1"),
        "routes": (
            "route_job_a:[waiting,branch_blocked,branch_free,complete]",
            "route_job_b:[hold_a]",
            "route_job_c:[hold_b]",
        ),
        "model_transitions": (
            "t_take_blocked:request:waiting:branch_blocked:[r_block_a:1,r_block_b:1]:[]",
            "t_take_free:request:waiting:branch_free:[r_free:1]:[]",
            "t_free_complete:complete:branch_free:complete:[]:[r_free:1]",
        ),
        "state_payload": (
            True,
            False,
            False,
            ("job_b:r_block_a:1", "job_c:r_block_b:1"),
            ("job_a:[[r_block_a:1,r_block_b:1],[r_free:1]]",),
            ("job_a:waiting", "job_b:holding", "job_c:holding"),
            ("job_a:waiting", "job_b:hold_a", "job_c:hold_b"),
        ),
    },
    {
        "case": "g6b_cu_nc_agv_reservation_boundary_v1",
        "family": "agv_reservation_boundary_family",
        "stem": "nc_agv_reservation_boundary",
        "mode": "model_generated_lts",
        "template": "g6b_recipe_nc_agv_reservation_boundary_v1",
        "control": "NC_AGV_RESERVATION_BOUNDARY",
        "expected": (
            "boundary_or_new_versioned_target_required/semantic_boundary_changed"
        ),
        "falsifiers": (
            "reservation_semantics_silently_coerced",
            "target_version_not_changed",
        ),
        "resources": (
            "agv_a:agv:1",
            "destination_slot:reservation:1",
            "machine_a:machine:1",
        ),
        "routes": ("route_job_a:[machine_a,agv_a,destination_slot,complete]",),
        "model_transitions": (
            "t_preclaim_destination:reserve:on_machine:reserved:[destination_slot:1]:[]",
            "t_load_agv:transport:reserved:on_agv:[agv_a:1]:[machine_a:1]",
            "t_arrive:transport:on_agv:complete:[]:[agv_a:1,destination_slot:1]",
        ),
        "state_payload": (
            True,
            False,
            False,
            ("job_a:agv_a:1", "job_b:destination_slot:1"),
            ("job_a:[[destination_slot:1]]",),
            ("job_a:reserved_wait", "job_b:holding"),
            ("job_a:destination_claim", "job_b:destination_occupied"),
        ),
        "parameters": ("reservation_semantics:enum:preclaim_destination_v1",),
        "target_schema": AGV_RELEASE_TARGET_SCHEMA_VERSION,
    },
    {
        "case": "g6b_cu_nc_dglobal_only_with_dlocal_v1",
        "family": "dglobal_with_local_core_family",
        "stem": "nc_dglobal_only_with_dlocal",
        "mode": "model_generated_lts",
        "template": "g6b_recipe_nc_dglobal_only_with_dlocal_v1",
        "control": "NC_DGLOBAL_ONLY_WITH_DLOCAL",
        "expected": "D_global/no_double_count_through_D_local",
        "falsifiers": (
            "counted_in_both_D_global_and_D_local",
            "global_deadlock_not_recognized",
        ),
        "resources": ("r_a:buffer:1", "r_b:buffer:1", "r_c:machine:1"),
        "routes": ("route_j1:[r_a,r_b]", "route_j2:[r_b,r_a]", "route_j3:[r_c,r_a]"),
        "model_transitions": (
            "t_j1_request:request:hold_a:wait_b:[r_b:1]:[]",
            "t_j2_request:request:hold_b:wait_a:[r_a:1]:[]",
            "t_j3_request:request:hold_c:wait_a:[r_a:1]:[]",
        ),
        "state_payload": (
            True,
            False,
            True,
            ("j1:r_a:1", "j2:r_b:1", "j3:r_c:1"),
            ("j1:[[r_b:1]]", "j2:[[r_a:1]]", "j3:[[r_a:1]]"),
            ("j1:waiting", "j2:waiting", "j3:waiting"),
            ("j1:wait_b", "j2:wait_a", "j3:wait_a"),
        ),
    },
    {
        "case": "g6b_cu_pc_dglobal_only_v1",
        "family": "dglobal_only_positive_family",
        "stem": "pc_dglobal_only",
        "mode": "model_generated_lts",
        "template": "g6b_recipe_pc_dglobal_only_v1",
        "control": None,
        "expected": "D_global",
        "falsifiers": (
            "path_to_F",
            "classified_only_as_D_local",
            "global_deadlock_not_recognized",
        ),
        "resources": ("r_a:buffer:1", "r_b:machine:1", "r_c:reservation:1"),
        "routes": ("route_j1:[r_a,r_b]", "route_j2:[r_b,r_c]", "route_j3:[r_c,r_a]"),
        "model_transitions": (
            "t_j1_request:request:hold_a:wait_b:[r_b:1]:[]",
            "t_j2_request:request:hold_b:wait_c:[r_c:1]:[]",
            "t_j3_request:request:hold_c:wait_a:[r_a:1]:[]",
        ),
        "state_payload": (
            True,
            False,
            True,
            ("j1:r_a:1", "j2:r_b:1", "j3:r_c:1"),
            ("j1:[[r_b:1]]", "j2:[[r_c:1]]", "j3:[[r_a:1]]"),
            ("j1:waiting", "j2:waiting", "j3:waiting"),
            ("j1:wait_b", "j2:wait_c", "j3:wait_a"),
        ),
    },
    {
        "case": "g6b_cu_pc_dlocal_a2b_single_kernel_v1",
        "family": "dlocal_a2b_single_kernel_positive_family",
        "stem": "pc_dlocal_a2b_single_kernel",
        "mode": "model_generated_lts",
        "template": "g6b_recipe_pc_dlocal_a2b_single_kernel_v1",
        "control": None,
        "expected": "D_local via A2b_proof",
        "falsifiers": (
            "violated_A2b_premise",
            "reachable_completion_bypass",
            "proof_check_failure",
        ),
        "resources": ("r_local_a:buffer:1", "r_local_b:machine:1", "r_outer:machine:1"),
        "routes": (
            "route_j1:[r_local_a,r_local_b]",
            "route_j2:[r_local_b,r_local_a]",
            "route_j3:[outer_tick]",
        ),
        "model_transitions": (
            "t_j1_request:request:hold_a:wait_b:[r_local_b:1]:[]",
            "t_j2_request:request:hold_b:wait_a:[r_local_a:1]:[]",
            "t_outer_tick:move:outer_ready:outer_ready:[]:[]",
        ),
        "state_payload": (
            True,
            False,
            False,
            ("j1:r_local_a:1", "j2:r_local_b:1"),
            ("j1:[[r_local_b:1]]", "j2:[[r_local_a:1]]"),
            ("j1:waiting", "j2:waiting", "j3:outer_ready"),
            ("j1:wait_b", "j2:wait_a", "j3:outer_tick"),
        ),
        "parameters": ("dlocal_admission_route:enum:A2b_proof",),
    },
    {
        "case": "g6b_cu_pc_dlocal_lts_multi_kernel_v1",
        "family": "dlocal_complete_lts_multi_kernel_positive_family",
        "stem": "pc_dlocal_lts_multi_kernel",
        "mode": "explicit_finite_lts_input",
        "template": "g6b_recipe_pc_dlocal_lts_multi_kernel_v1",
        "control": None,
        "expected": "D_local via complete-LTS audit",
        "falsifiers": (
            "path_to_F",
            "truncation",
            "unavailable_transition_branch",
            "incomplete_state_registry",
        ),
        "resources": ("r_a:buffer:1", "r_b:machine:1", "r_c:buffer:1", "r_d:machine:1"),
        "routes": (
            "route_j1:[r_a,r_b]",
            "route_j2:[r_b,r_a]",
            "route_j3:[r_c,r_d]",
            "route_j4:[r_d,r_c]",
        ),
        "model_transitions": (
            "t_hit_ab:request:s_initial:dlocal_ab:[r_b:1]:[]",
            "t_hit_cd:request:s_initial:dlocal_cd:[r_d:1]:[]",
            "t_post_ab:move:dlocal_ab:post_hit:[]:[]",
            "t_post_cd:move:dlocal_cd:post_hit:[]:[]",
            "t_return_ab:move:post_hit:dlocal_ab:[]:[]",
            "t_return_cd:move:post_hit:dlocal_cd:[]:[]",
        ),
        "states": ("dlocal_ab", "dlocal_cd", "f_complete", "post_hit", "s_initial"),
        "initial": "s_initial",
        "marked": ("f_complete",),
        "transitions": (
            "dlocal_ab:t_post_ab:post_hit",
            "dlocal_cd:t_post_cd:post_hit",
            "post_hit:t_return_ab:dlocal_ab",
            "post_hit:t_return_cd:dlocal_cd",
            "s_initial:t_hit_ab:dlocal_ab",
            "s_initial:t_hit_cd:dlocal_cd",
        ),
        "parameters": (
            "dlocal_admission_route:enum:complete_LTS_completion_nonreachability_audit",
        ),
    },
    {
        "case": "g6b_cu_bc_crp_zero_kernel_v1",
        "family": "crp_zero_matching_kernel_boundary_family",
        "stem": "bc_crp_zero_kernel",
        "mode": "model_generated_lts",
        "template": "g6b_recipe_bc_crp_zero_kernel_v1",
        "control": None,
        "expected": "CRP_bridge_inapplicable",
        "falsifiers": (
            "matching_local_kernel_found",
            "global_certificate_borrowed",
            "unclassified_scientific_input",
        ),
        "resources": ("r_a:buffer:1", "r_b:machine:1", "r_res:reservation:1"),
        "routes": ("route_j1:[r_a,and_request]", "route_j2:[r_b,r_a]"),
        "model_transitions": (
            "t_j1_and_request:request:hold_a:wait_and:[r_b:1,r_res:1]:[]",
            "t_j2_request:request:hold_b:wait_a:[r_a:1]:[]",
        ),
        "state_payload": (
            True,
            False,
            True,
            ("j1:r_a:1", "j2:r_b:1"),
            ("j1:[[r_b:1,r_res:1]]", "j2:[[r_a:1]]"),
            ("j1:waiting", "j2:waiting"),
            ("j1:wait_and", "j2:wait_a"),
        ),
        "parameters": (
            "declared_crp_family:enum:S4PR_single_resource_request_only_v1",
        ),
    },
    {
        "case": "g6b_cu_bc_multi_capacity_residual_v1",
        "family": "multi_capacity_residual_boundary_family",
        "stem": "bc_multi_capacity_residual",
        "mode": "model_generated_lts",
        "template": "g6b_recipe_bc_multi_capacity_residual_v1",
        "control": None,
        "expected": "simple_cycle_not_sufficient_with_residual_capacity",
        "falsifiers": (
            "residual_capacity_zero",
            "capacity_witness_failure",
            "simple_cycle_treated_as_deadlock",
        ),
        "resources": ("r_a:machine:1", "r_shared:buffer:2"),
        "routes": ("route_j1:[r_a,r_shared]", "route_j2:[r_shared,r_a]"),
        "model_transitions": (
            "t_j1_request:request:hold_a:wait_shared:[r_shared:1]:[]",
            "t_j2_request:request:hold_shared:wait_a:[r_a:1]:[]",
        ),
        "state_payload": (
            True,
            False,
            False,
            ("j1:r_a:1", "j2:r_shared:1"),
            ("j1:[[r_shared:1]]", "j2:[[r_a:1]]"),
            ("j1:waiting", "j2:waiting"),
            ("j1:wait_shared", "j2:wait_a"),
        ),
        "parameters": ("simple_cycle_diagnostic_only:boolean:true",),
    },
    {
        "case": "g6b_cu_pc_medium_independent_island_v1",
        "family": "medium_independent_island_family",
        "stem": "pc_medium_independent_island",
        "mode": "model_generated_lts",
        "template": "g6b_recipe_pc_medium_independent_island_v1",
        "control": None,
        "expected": "bounded_target_certifiable_or_structured_refusal",
        "falsifiers": (
            "state_bound_exceeded",
            "unavailable_transition_branch",
            "target_identity_mismatch",
            "non_almost_sure_global_domain",
        ),
        "resources": (
            "agv_x:agv:1",
            "agv_y:agv:1",
            "buffer_ab:buffer:2",
            "buffer_bc:buffer:3",
            "buffer_cd:buffer:2",
            "cell_a:machine:1",
            "cell_b:machine:1",
            "cell_c:machine:1",
            "cell_d:machine:1",
        ),
        "routes": (
            "route_alpha:[cell_a,buffer_ab,cell_b,buffer_bc,cell_c]",
            "route_beta:[cell_c,buffer_cd,cell_d,buffer_ab,cell_a]",
            "route_delta_bypass:[cell_d,agv_y,cell_a]",
            "route_gamma:[cell_b,agv_x,cell_d]",
        ),
        "model_transitions": (
            "t_alpha_ab:transfer:cell_a:buffer_ab:[buffer_ab:1]:[cell_a:1]",
            "t_alpha_b:transfer:buffer_ab:cell_b:[cell_b:1]:[buffer_ab:1]",
            "t_alpha_bc:transfer:cell_b:buffer_bc:[buffer_bc:1]:[cell_b:1]",
            "t_alpha_c:transfer:buffer_bc:cell_c:[cell_c:1]:[buffer_bc:1]",
            "t_beta_cd:transfer:cell_c:buffer_cd:[buffer_cd:1]:[cell_c:1]",
            "t_beta_d:transfer:buffer_cd:cell_d:[cell_d:1]:[buffer_cd:1]",
            "t_beta_ab:transfer:cell_d:buffer_ab:[buffer_ab:1]:[cell_d:1]",
            "t_beta_a:transfer:buffer_ab:cell_a:[cell_a:1]:[buffer_ab:1]",
            "t_gamma_load:reserve:cell_b:agv_x:[agv_x:1]:[]",
            "t_gamma_unload:transfer:agv_x:cell_d:[cell_d:1]:[agv_x:1,cell_b:1]",
            "t_delta_load:reserve:cell_d:agv_y:[agv_y:1]:[]",
            "t_delta_unload:transfer:agv_y:cell_a:[cell_a:1]:[agv_y:1,cell_d:1]",
        ),
        "state_payload": (
            True,
            False,
            False,
            (
                "job_alpha:cell_a:1",
                "job_beta:cell_c:1",
                "job_delta:agv_y:1",
                "job_gamma:agv_x:1",
            ),
            (
                "job_alpha:[[buffer_ab:1]]",
                "job_beta:[[buffer_cd:1]]",
                "job_delta:[[cell_a:1]]",
                "job_gamma:[[cell_d:1]]",
            ),
            (
                "job_alpha:waiting",
                "job_beta:waiting",
                "job_delta:reserved_wait",
                "job_gamma:reserved_wait",
            ),
            (
                "job_alpha:buffer_ab",
                "job_beta:buffer_cd",
                "job_delta:cell_a",
                "job_gamma:cell_d",
            ),
        ),
        "parameters": (
            "route_alpha_wip:integer:2",
            "route_beta_wip:integer:3",
            "route_delta_bypass_wip:integer:1",
            "route_gamma_wip:integer:2",
            "reservation_semantics:enum:preclaim_destination_v1",
        ),
    },
)

METHOD_OBSERVATION_IDS = tuple(
    item
    for row in _ROSTER
    for item in (
        f"g6b_mo_{row['stem']}_exact_v1",
        f"g6b_mo_{row['stem']}_des_v1",
    )
)
METHOD_COMPANION_GROUP_IDS = tuple(
    sorted(f"g6b_mcg_{row['stem']}_v1" for row in _ROSTER)
)

CASE_RELATIVE_PATHS = (
    "case_input.json",
    "declarations/control_declaration.json",
    "declarations/policy_declaration.json",
    "declarations/rate_manifest.json",
    "declarations/selected_target_declaration.json",
    "fingerprints/case_content_sha256.json",
    "fingerprints/metric_schema_sha256.json",
    "fingerprints/output_root_reservation_sha256_des.json",
    "fingerprints/output_root_reservation_sha256_exact.json",
    "fingerprints/parameter_tuple_sha256.json",
    "fingerprints/random_stream_manifest_sha256_des.json",
    "fingerprints/random_stream_manifest_sha256_exact.json",
    "fingerprints/route_signature_sha256.json",
    "fingerprints/sealed_prediction_sha256.json",
    "fingerprints/state_snapshot_sha256.json",
    "method_companion_group.json",
    "method_observations/des.json",
    "method_observations/exact.json",
    "metric_schema.json",
    "metric_schema_sharing.json",
    "projections/case_content.json",
    "projections/output_root_reservation_des.json",
    "projections/output_root_reservation_exact.json",
    "projections/parameter_tuple.json",
    "projections/random_stream_manifest_des.json",
    "projections/random_stream_manifest_exact.json",
    "projections/route_signature.json",
    "projections/state_snapshot.json",
    "sealed_prediction.json",
    "semantic_lineage_declaration.json",
)


@dataclass(frozen=True)
class LedgerEntry:
    record: Mapping[str, object]
    frame: bytes
    sha256: str


@dataclass(frozen=True)
class CandidateFile:
    path: str
    content: bytes
    sha256: str
    record: Mapping[str, object]


@dataclass(frozen=True)
class CandidateBundle:
    authorization: Mapping[str, object]
    case_files: Mapping[str, CandidateFile]
    governance_files: Mapping[str, CandidateFile]
    manifest_bytes: bytes
    ledger_bytes: bytes
    immutable_log_bytes: bytes
    ledger_ready_metadata: Mapping[str, object]
    filesystem_writes_performed: int = 0

    @property
    def all_files(self) -> Mapping[str, CandidateFile]:
        return MappingProxyType({**self.governance_files, **self.case_files})

    @property
    def case_file_count(self) -> int:
        return len(self.case_files)

    @property
    def governance_file_count(self) -> int:
        return len(self.governance_files)

    @property
    def total_file_count(self) -> int:
        return len(self.all_files)


_MATERIALIZER_TEST_FAILURE_POINT: str | None = None
_UNAUTHORIZED_ATTEMPT_ID = "g6b_discovery_case_construction_v1_unauthorized"
_WINDOWS_CREATE_NEW_RENAME = os.name == "nt"
_WINDOWS_LEDGER_BYTE_LOCK = os.name == "nt" and _msvcrt is not None
_LEDGER_PROCESS_LOCKS_GUARD = threading.Lock()
_LEDGER_PROCESS_LOCKS: dict[Path, threading.Lock] = {}
_BASE_OUTPUT_ROOT = "cases/discovery/g6b/row_families/structural_discovery_v1"
_RESERVED_OUTPUT_ROOTS = (
    "case_units",
    "governance",
    "artifacts/g6b/quantitative",
    "artifacts/g6b/science",
    "artifacts/g6b/target_certification",
    "science",
    "cases/discovery/g6b/target_certification",
    "cases/discovery/g6b/quantitative",
    "cases/discovery/g6b/science",
    f"{_BASE_OUTPUT_ROOT}/target_certification",
    f"{_BASE_OUTPUT_ROOT}/quantitative",
    f"{_BASE_OUTPUT_ROOT}/science",
    f"{_BASE_OUTPUT_ROOT}/artifacts",
)
_TERMINAL_LEDGER_EVENTS = frozenset(
    {"PREWRITE_REFUSED", "READY_TO_SEAL", "INTERRUPTED_PARTIAL"}
)
_TRANSITIONS = MappingProxyType(
    {
        "EMPTY": ("PREWRITE_REFUSED", "WRITE_STARTED"),
        "PREWRITE_REFUSED": ("PREWRITE_REFUSED", "WRITE_STARTED"),
        "WRITE_STARTED": ("FILE_CREATED", "INTERRUPTED_PARTIAL"),
        "FILE_CREATED": ("FILE_CREATED", "READY_TO_SEAL", "INTERRUPTED_PARTIAL"),
        "READY_TO_SEAL": ("INTERRUPTED_PARTIAL",),
        "INTERRUPTED_PARTIAL": (),
    }
)


@dataclass
class _LedgerLease:
    path: Path
    fd: int
    process_lock: threading.Lock
    byte_locked: bool = False
    closed: bool = False

    def __enter__(self) -> _LedgerLease:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def read_all(self) -> bytes:
        os.lseek(self.fd, 0, os.SEEK_SET)
        chunks: list[bytes] = []
        while True:
            chunk = os.read(self.fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)

    def append_frame(self, frame: bytes) -> None:
        os.lseek(self.fd, 0, os.SEEK_END)
        _write_all(self.fd, frame)
        os.fsync(self.fd)

    def close(self) -> None:
        if self.closed:
            return
        try:
            if self.byte_locked and _msvcrt is not None:
                os.lseek(self.fd, 0, os.SEEK_SET)
                _msvcrt.locking(self.fd, _msvcrt.LK_UNLCK, 1)
        finally:
            try:
                os.close(self.fd)
            finally:
                self.closed = True
                self.process_lock.release()


def _process_lock_for_ledger(path: Path) -> threading.Lock:
    resolved = path.resolve(strict=False)
    with _LEDGER_PROCESS_LOCKS_GUARD:
        lock = _LEDGER_PROCESS_LOCKS.get(resolved)
        if lock is None:
            lock = threading.Lock()
            _LEDGER_PROCESS_LOCKS[resolved] = lock
        return lock


def _acquire_ledger_lease(ledger_path: Path) -> _LedgerLease:
    if not _WINDOWS_LEDGER_BYTE_LOCK or _msvcrt is None:
        _refuse("ledger_lease_platform")
    process_lock = _process_lock_for_ledger(ledger_path)
    if not process_lock.acquire(blocking=False):
        _refuse("ledger_lease_busy")
    fd = -1
    byte_locked = False
    try:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        fd = _open_fd(ledger_path, os.O_RDWR | os.O_CREAT)
        os.lseek(fd, 0, os.SEEK_SET)
        _msvcrt.locking(fd, _msvcrt.LK_NBLCK, 1)
        byte_locked = True
        return _LedgerLease(
            path=ledger_path,
            fd=fd,
            process_lock=process_lock,
            byte_locked=byte_locked,
        )
    except OSError as exc:
        if fd >= 0:
            if byte_locked:
                try:
                    os.lseek(fd, 0, os.SEEK_SET)
                    _msvcrt.locking(fd, _msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
            os.close(fd)
        process_lock.release()
        raise ValueError("ledger_lease_busy") from exc


def _read_locked_ledger_bytes(lease: _LedgerLease) -> bytes:
    return lease.read_all()


def append_ledger_entry_exclusive(
    ledger_path: Path,
    *,
    authorization: Mapping[str, object] | None,
    event_code: str,
    entry_index: int,
    prior_entry_sha256_or_null: object,
    candidate_log_sha256_or_null: object,
    created_file_hashes: Mapping[str, str] | None = None,
    observed_partial_file_hashes: Mapping[str, str] | None = None,
    refusal_reason_codes: Sequence[str] | None = None,
    causal_entry_sha256_or_null: object = None,
    interrupted_fragments: Sequence[Mapping[str, object]] | None = None,
) -> LedgerEntry:
    with _acquire_ledger_lease(ledger_path) as lease:
        return _append_ledger_entry_locked(
            lease,
            authorization=authorization,
            event_code=event_code,
            entry_index=entry_index,
            prior_entry_sha256_or_null=prior_entry_sha256_or_null,
            candidate_log_sha256_or_null=candidate_log_sha256_or_null,
            created_file_hashes=created_file_hashes,
            observed_partial_file_hashes=observed_partial_file_hashes,
            refusal_reason_codes=refusal_reason_codes,
            causal_entry_sha256_or_null=causal_entry_sha256_or_null,
            interrupted_fragments=interrupted_fragments,
        )


def _append_ledger_entry_locked(
    lease: _LedgerLease,
    *,
    authorization: Mapping[str, object] | None,
    event_code: str,
    entry_index: int,
    prior_entry_sha256_or_null: object,
    candidate_log_sha256_or_null: object,
    created_file_hashes: Mapping[str, str] | None = None,
    observed_partial_file_hashes: Mapping[str, str] | None = None,
    refusal_reason_codes: Sequence[str] | None = None,
    causal_entry_sha256_or_null: object = None,
    interrupted_fragments: Sequence[Mapping[str, object]] | None = None,
) -> LedgerEntry:
    del entry_index, prior_entry_sha256_or_null, interrupted_fragments
    auth, auth_is_valid = _append_authorization_context(authorization, event_code)
    existing = _read_locked_ledger_bytes(lease)
    records, fragments = _parse_ledger_records(existing)
    _validate_ledger_sequence(records, fragments, allow_terminal_partial=True)
    _validate_existing_ledger_identity(
        records,
        current_auth=auth,
        current_auth_is_valid=auth_is_valid,
        expected_candidate_log_sha256_or_null=candidate_log_sha256_or_null,
    )
    entries = [entry for entry, _pending in records]
    prior_event = str(entries[-1]["event_code"]) if entries else "EMPTY"
    prior_hash = cast(str, entries[-1]["entry_sha256"]) if entries else None
    if event_code not in _TRANSITIONS[prior_event]:
        _refuse("ledger_transition")
    if fragments and event_code not in {"INTERRUPTED_PARTIAL", "PREWRITE_REFUSED"}:
        _refuse("interrupted_fragment_unrecorded")
    codes = tuple(sorted(set(refusal_reason_codes or ())))
    if len(codes) != len(tuple(refusal_reason_codes or ())) or list(codes) != list(
        refusal_reason_codes or ()
    ):
        _refuse("refusal_reason_codes")
    bound_fragments = _fragment_records(fragments)
    causal = causal_entry_sha256_or_null
    if event_code == "INTERRUPTED_PARTIAL":
        if "ledger_append_interrupted" not in codes:
            codes = tuple(sorted({*codes, "ledger_append_interrupted"}))
        causal = prior_hash
    elif event_code == "PREWRITE_REFUSED":
        if not auth_is_valid and "unauthorized_case_creation_attempt" not in codes:
            codes = tuple(sorted({*codes, "unauthorized_case_creation_attempt"}))
        if fragments and "ledger_append_interrupted" not in codes:
            codes = tuple(sorted({*codes, "ledger_append_interrupted"}))
        if not auth_is_valid:
            candidate_log_sha256_or_null = None
    record = _ledger_record(
        auth,
        event_code=event_code,
        entry_index=len(entries),
        prior_hash=prior_hash,
        candidate_log_sha256_or_null=candidate_log_sha256_or_null,
        created_file_hashes=created_file_hashes or {},
        observed_partial_file_hashes=observed_partial_file_hashes or {},
        refusal_reason_codes=codes,
        causal_entry_sha256_or_null=causal,
        interrupted_fragments=bound_fragments,
    )
    _validate_ledger_entry_semantics(record, prior_event, prior_hash, fragments)
    frame = b"\x1e" + canonical_bytes_v2(record) + b"\n"
    if event_code in _TERMINAL_LEDGER_EVENTS:
        _validate_complete_ledger_bytes(existing + frame)
    lease.append_frame(frame)
    return LedgerEntry(
        record=MappingProxyType(record),
        frame=frame,
        sha256=cast(str, record["entry_sha256"]),
    )


def create_atomic_file_exclusive(
    path: Path,
    final_bytes: bytes,
    *,
    attempt_token: str | None = None,
    stop_before_rename: bool = False,
) -> str:
    if not isinstance(final_bytes, bytes):
        _refuse("final_bytes")
    _validate_path_for_create(path)
    if attempt_token is None:
        _refuse("attempt_token")
    token = cast(str, attempt_token)
    if not _is_lower_hex(token, 16):
        _refuse("attempt_token")
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    tmp_path = _temp_path_for(path, token)
    if path.exists() or path.is_symlink():
        _refuse("final_exists")
    if tmp_path.exists() or tmp_path.is_symlink():
        _refuse("temp_exists")
    fd = _open_fd(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    try:
        _write_all(fd, final_bytes)
        os.fsync(fd)
    except BaseException:
        os.close(fd)
        raise
    else:
        os.close(fd)
    digest = hashlib.sha256(final_bytes).hexdigest()
    if hashlib.sha256(tmp_path.read_bytes()).hexdigest() != digest:
        _refuse("temp_hash_mismatch")
    if stop_before_rename:
        return digest
    try:
        _atomic_rename_no_replace(tmp_path, path)
    except FileExistsError as exc:
        raise ValueError("final_exists") from exc
    if tmp_path.exists():
        _refuse("temp_retained_after_success")
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        _refuse("final_hash_mismatch")
    return digest


def materialize_candidate(repo_root: Path, candidate: CandidateBundle) -> None:
    repo_root = Path(repo_root)
    auth_file = candidate.governance_files[
        _governance_path("construction_authorization.json")
    ]
    auth_disk = _contained(repo_root, auth_file.path)
    if not auth_disk.exists():
        _refuse("authorization_missing")
    if hashlib.sha256(auth_disk.read_bytes()).hexdigest() != auth_file.sha256:
        _refuse("authorization_mismatch")
    if _temp_for_rel(
        repo_root, auth_file.path, _authorization_attempt_token()
    ).exists():
        _refuse("authorization_temp_exists")
    validate_candidate_bundle(candidate)

    manifest_rel = _governance_path("sealed_bundle_manifest.json")
    log_rel = _governance_path("construction_log.json")
    ledger_rel = _governance_path("construction_ledger.json")
    ledger_file = _contained(repo_root, ledger_rel)
    with _acquire_ledger_lease(ledger_file) as lease:
        existing_ledger = _read_locked_ledger_bytes(lease)
        records, fragments = _parse_ledger_records(existing_ledger)
        _validate_ledger_sequence(records, fragments, allow_terminal_partial=True)
        entries = [entry for entry, _pending in records]
        if entries and entries[-1]["event_code"] == "INTERRUPTED_PARTIAL":
            _refuse("non_resumable")
        if fragments:
            _refuse("non_resumable")

        _preflight_materialization_root(repo_root, candidate, allow_authorization=True)
        failure = _MATERIALIZER_TEST_FAILURE_POINT
        log_file = candidate.governance_files[log_rel]
        _append_ledger_entry_locked(
            lease,
            authorization=candidate.authorization,
            event_code="WRITE_STARTED",
            entry_index=-1,
            prior_entry_sha256_or_null=None,
            candidate_log_sha256_or_null=log_file.sha256,
        )
        if failure == "after_write_started":
            raise RuntimeError("injected_failure:after_write_started")

        _create_candidate_file(repo_root, candidate, log_rel)
        if failure == "after_log_file_rename":
            raise RuntimeError("injected_failure:after_log_file_rename")
        _append_ledger_entry_locked(
            lease,
            authorization=candidate.authorization,
            event_code="FILE_CREATED",
            entry_index=-1,
            prior_entry_sha256_or_null=None,
            candidate_log_sha256_or_null=log_file.sha256,
            created_file_hashes={log_rel: log_file.sha256},
        )
        if failure == "after_log":
            raise RuntimeError("injected_failure:after_log")

        cumulative: dict[str, str] = {log_rel: log_file.sha256}
        for index, (rel_path, entry) in enumerate(
            candidate.case_files.items(), start=1
        ):
            _create_candidate_file(repo_root, candidate, rel_path)
            cumulative[rel_path] = entry.sha256
            if failure == f"after_case_{index:03d}_file_rename":
                raise RuntimeError(
                    f"injected_failure:after_case_{index:03d}_file_rename"
                )
            _append_ledger_entry_locked(
                lease,
                authorization=candidate.authorization,
                event_code="FILE_CREATED",
                entry_index=-1,
                prior_entry_sha256_or_null=None,
                candidate_log_sha256_or_null=log_file.sha256,
                created_file_hashes={rel_path: entry.sha256},
            )
            if failure == f"after_case_{index:03d}":
                raise RuntimeError(f"injected_failure:after_case_{index:03d}")
        if failure == "before_ready":
            raise RuntimeError("injected_failure:before_ready")

        _append_ledger_entry_locked(
            lease,
            authorization=candidate.authorization,
            event_code="READY_TO_SEAL",
            entry_index=-1,
            prior_entry_sha256_or_null=None,
            candidate_log_sha256_or_null=log_file.sha256,
            created_file_hashes=cumulative,
        )
        actual_ledger = _read_locked_ledger_bytes(lease)
        if actual_ledger != candidate.ledger_bytes:
            _refuse("ledger_bytes_mismatch")
        _create_candidate_file(
            repo_root,
            candidate,
            manifest_rel,
            stop_before_rename=failure == "before_manifest_rename",
        )
        if failure == "before_manifest_rename":
            raise RuntimeError("injected_failure:before_manifest_rename")


def recover_interrupted_bundle(
    repo_root: Path, authorization: Mapping[str, object] | None
) -> None:
    repo_root = Path(repo_root)
    auth, auth_is_valid = _coerce_authorization(authorization)
    candidate = build_candidate_bundle(auth) if auth_is_valid else None
    manifest_rel = _governance_path("sealed_bundle_manifest.json")
    ledger_rel = _governance_path("construction_ledger.json")
    manifest_file = _contained(repo_root, manifest_rel)
    ledger_file = _contained(repo_root, ledger_rel)
    with _acquire_ledger_lease(ledger_file) as lease:
        ledger_bytes = _read_locked_ledger_bytes(lease)
        if manifest_file.exists():
            if candidate is None:
                _refuse("authorization")
            assert candidate is not None
            _validate_sealed_success(repo_root, candidate, ledger_bytes=ledger_bytes)
            return
        inventory = (
            _closed_materialization_inventory(
                repo_root, candidate, ledger_bytes=ledger_bytes
            )
            if candidate is not None
            else {}
        )
        expected_log = (
            candidate.governance_files[_governance_path("construction_log.json")].sha256
            if candidate is not None
            else None
        )
        records, fragments = _parse_ledger_records(ledger_bytes)
        _validate_ledger_sequence(records, fragments, allow_terminal_partial=False)
        _validate_existing_ledger_identity(
            records,
            current_auth=auth,
            current_auth_is_valid=auth_is_valid,
            expected_candidate_log_sha256_or_null=expected_log,
        )
        entries = [entry for entry, _pending in records]
        if (
            entries
            and not fragments
            and entries[-1]["event_code"] in {"INTERRUPTED_PARTIAL", "PREWRITE_REFUSED"}
        ):
            return
        event_code = (
            "PREWRITE_REFUSED"
            if not entries or not auth_is_valid
            else "INTERRUPTED_PARTIAL"
        )
        observed = {} if event_code == "PREWRITE_REFUSED" else inventory
        _append_ledger_entry_locked(
            lease,
            authorization=auth if auth_is_valid else None,
            event_code=event_code,
            entry_index=-1,
            prior_entry_sha256_or_null=None,
            candidate_log_sha256_or_null=None
            if event_code == "PREWRITE_REFUSED"
            else expected_log,
            observed_partial_file_hashes=observed,
            refusal_reason_codes=["ledger_append_interrupted"],
        )


def _coerce_authorization(
    authorization: Mapping[str, object] | None,
) -> tuple[Mapping[str, object], bool]:
    if authorization is None:
        return MappingProxyType({}), False
    try:
        return validate_construction_authorization_for_materializer(authorization), True
    except (TypeError, ValueError):
        return MappingProxyType({}), False


def _append_authorization_context(
    authorization: Mapping[str, object] | None, event_code: str
) -> tuple[Mapping[str, object], bool]:
    auth, auth_is_valid = _coerce_authorization(authorization)
    if auth_is_valid:
        return auth, True
    if event_code != "PREWRITE_REFUSED":
        _refuse("authorization")
    return auth, False


def _validate_existing_ledger_identity(
    records: Sequence[LedgerRecord],
    *,
    current_auth: Mapping[str, object],
    current_auth_is_valid: bool,
    expected_candidate_log_sha256_or_null: object,
) -> None:
    if not current_auth_is_valid:
        return
    expected_attempt_id = current_auth["artifact_id"]
    expected_auth_hash = current_auth["artifact_sha256"]
    expected_source_head = current_auth["source_head"]
    expected_tree_hash = current_auth["source_tree_hash"]
    for entry, _pending in records:
        event = entry["event_code"]
        attempt_id = entry["attempt_id"]
        auth_hash = entry["construction_authorization_sha256_or_null"]
        source_head = entry["source_head_or_null"]
        tree_hash = entry["source_tree_hash_or_null"]
        log_hash = entry["candidate_log_sha256_or_null"]
        if event == "PREWRITE_REFUSED" and attempt_id == _UNAUTHORIZED_ATTEMPT_ID:
            if any(
                value is not None
                for value in (auth_hash, source_head, tree_hash, log_hash)
            ):
                _refuse("ledger_identity")
            continue
        if (
            attempt_id != expected_attempt_id
            or auth_hash != expected_auth_hash
            or source_head != expected_source_head
            or tree_hash != expected_tree_hash
        ):
            _refuse("ledger_identity")
        if event == "PREWRITE_REFUSED":
            if (
                log_hash is not None
                and log_hash != expected_candidate_log_sha256_or_null
            ):
                _refuse("ledger_identity")
        elif log_hash != expected_candidate_log_sha256_or_null:
            _refuse("ledger_identity")


def _ledger_record(
    auth: Mapping[str, object],
    *,
    event_code: str,
    entry_index: int,
    prior_hash: str | None,
    candidate_log_sha256_or_null: object,
    created_file_hashes: Mapping[str, str],
    observed_partial_file_hashes: Mapping[str, str],
    refusal_reason_codes: Sequence[str],
    causal_entry_sha256_or_null: object,
    interrupted_fragments: Sequence[Mapping[str, object]],
) -> JsonObject:
    return _finalize(
        {
            "schema_version": "ims-deadlock/g6b-construction-ledger-entry/v1",
            "bundle_id": BUNDLE_ID,
            "attempt_id": str(auth.get("artifact_id", _UNAUTHORIZED_ATTEMPT_ID)),
            "entry_index": entry_index,
            "event_code": event_code,
            "prior_entry_sha256_or_null": prior_hash,
            "construction_authorization_sha256_or_null": auth.get("artifact_sha256"),
            "source_head_or_null": auth.get("source_head"),
            "source_tree_hash_or_null": auth.get("source_tree_hash"),
            "candidate_log_sha256_or_null": candidate_log_sha256_or_null,
            "created_file_hashes": dict(sorted(created_file_hashes.items())),
            "observed_partial_file_hashes": dict(
                sorted(observed_partial_file_hashes.items())
            ),
            "refusal_reason_codes": list(refusal_reason_codes),
            "causal_entry_sha256_or_null": causal_entry_sha256_or_null,
            "interrupted_fragments": [dict(item) for item in interrupted_fragments],
            "entry_sha256": None,
        },
        "entry_sha256",
    )


def _validate_ledger_entry_semantics(
    entry: Mapping[str, object],
    prior_event: str,
    prior_hash: str | None,
    pending_fragments: Sequence[bytes],
) -> None:
    event = entry["event_code"]
    if event not in _TRANSITIONS[prior_event]:
        _refuse("ledger_transition")
    created = cast(Mapping[str, str], entry["created_file_hashes"])
    observed = cast(Mapping[str, str], entry["observed_partial_file_hashes"])
    reasons = cast(Sequence[str], entry["refusal_reason_codes"])
    if list(reasons) != sorted(set(reasons)):
        _refuse("refusal_reason_codes")
    fragments = cast(Sequence[Mapping[str, object]], entry["interrupted_fragments"])
    if event == "PREWRITE_REFUSED":
        if (
            created
            or observed
            or not reasons
            or entry["causal_entry_sha256_or_null"] is not None
        ):
            _refuse("ledger_event")
        if entry["attempt_id"] == _UNAUTHORIZED_ATTEMPT_ID:
            if any(
                entry[field] is not None
                for field in (
                    "construction_authorization_sha256_or_null",
                    "source_head_or_null",
                    "source_tree_hash_or_null",
                    "candidate_log_sha256_or_null",
                )
            ):
                _refuse("ledger_identity")
            if "unauthorized_case_creation_attempt" not in reasons:
                _refuse("refusal_reason_codes")
    elif event == "WRITE_STARTED":
        if (
            created
            or observed
            or reasons
            or entry["causal_entry_sha256_or_null"] is not None
        ):
            _refuse("ledger_event")
    elif event == "FILE_CREATED":
        if (
            len(created) != 1
            or observed
            or reasons
            or entry["causal_entry_sha256_or_null"] is not None
        ):
            _refuse("ledger_event")
    elif event == "READY_TO_SEAL":
        if (
            len(created) != 391
            or observed
            or reasons
            or entry["causal_entry_sha256_or_null"] is not None
        ):
            _refuse("ledger_event")
    elif event == "INTERRUPTED_PARTIAL":
        if created or (not observed and not pending_fragments):
            _refuse("ledger_event")
        if "ledger_append_interrupted" not in reasons:
            _refuse("refusal_reason_codes")
        if entry["causal_entry_sha256_or_null"] != prior_hash:
            _refuse("ledger_causal")
    if pending_fragments:
        if event not in {
            "INTERRUPTED_PARTIAL",
            "PREWRITE_REFUSED",
        } or list(fragments) != _fragment_records(pending_fragments):
            _refuse("interrupted_fragment_unrecorded")
        if event == "PREWRITE_REFUSED" and "ledger_append_interrupted" not in reasons:
            _refuse("refusal_reason_codes")
    elif fragments:
        _refuse("interrupted_fragment_unexpected")


def _read_ledger_prefix(ledger_path: Path) -> tuple[list[LedgerRecord], list[bytes]]:
    if not ledger_path.exists():
        return [], []
    return _parse_ledger_records(ledger_path.read_bytes())


def _create_candidate_file(
    repo_root: Path,
    candidate: CandidateBundle,
    rel_path: str,
    *,
    stop_before_rename: bool = False,
) -> None:
    entry = candidate.all_files[rel_path]
    token = _write_attempt_token(candidate)
    digest = create_atomic_file_exclusive(
        _contained(repo_root, rel_path),
        entry.content,
        attempt_token=token,
        stop_before_rename=stop_before_rename,
    )
    if digest != entry.sha256:
        _refuse("final_hash_mismatch")


def _preflight_materialization_root(
    repo_root: Path, candidate: CandidateBundle, *, allow_authorization: bool
) -> None:
    for reserved in _reserved_output_roots(candidate):
        if (_contained(repo_root, reserved)).exists():
            _refuse("reserved_output_root")
    allowed_final = _authorized_output_paths()
    allowed_temps: set[str] = set()
    roots = (
        _contained(
            repo_root, _governance_path("construction_authorization.json")
        ).parent,
        _contained(repo_root, _case_path(CASE_UNIT_IDS[0], "case_input.json")).parents[
            1
        ],
    )
    for root in roots:
        if not root.exists():
            continue
        for item in root.rglob("*"):
            if item.is_symlink():
                _refuse("symlink")
            rel = item.relative_to(repo_root).as_posix()
            if item.is_file():
                if rel in allowed_final:
                    if allow_authorization and rel in {
                        _governance_path("construction_authorization.json"),
                        _governance_path("construction_ledger.json"),
                    }:
                        continue
                    _refuse("preexisting_output")
                if rel not in allowed_temps:
                    _refuse("unexpected_file")
            elif item.is_dir() and rel not in _allowed_output_directories():
                _refuse("unexpected_file")


def _closed_allowed_paths(candidate: CandidateBundle) -> set[str]:
    return set(candidate.all_files)


def _transient_paths_for_candidate(candidate: CandidateBundle) -> set[str]:
    return {
        _temp_rel_path(
            rel,
            _authorization_attempt_token()
            if rel == _governance_path("construction_authorization.json")
            else _write_attempt_token(candidate),
        )
        for rel in candidate.all_files
        if rel != _governance_path("construction_ledger.json")
    }


def _deterministic_temp_paths(candidate: CandidateBundle) -> set[str]:
    return _transient_paths_for_candidate(candidate)


def _reserved_output_roots(candidate: CandidateBundle) -> set[str]:
    roots = set(_RESERVED_OUTPUT_ROOTS)
    for entry in candidate.case_files.values():
        record = entry.record
        path = record.get("repo_relative_posix_path")
        if record.get("reserved") is True and isinstance(path, str):
            roots.add(path.rstrip("/"))
    return roots


def _closed_materialization_inventory(
    repo_root: Path, candidate: CandidateBundle, *, ledger_bytes: bytes | None = None
) -> dict[str, str]:
    allowed = _closed_allowed_paths(candidate) | _transient_paths_for_candidate(
        candidate
    )
    inventory: dict[str, str] = {}
    for rel in sorted(allowed):
        path = _contained(repo_root, rel)
        if path.exists():
            if path.is_symlink() or not path.is_file():
                _refuse("unexpected_file")
            if (
                rel == _governance_path("construction_ledger.json")
                and ledger_bytes is not None
            ):
                inventory[rel] = hashlib.sha256(ledger_bytes).hexdigest()
            else:
                inventory[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    for root in (
        _contained(
            repo_root, _governance_path("construction_authorization.json")
        ).parent,
        _contained(repo_root, _case_path(CASE_UNIT_IDS[0], "case_input.json")).parents[
            1
        ],
    ):
        if not root.exists():
            continue
        for item in root.rglob("*"):
            rel = item.relative_to(repo_root).as_posix()
            if item.is_file() and rel not in allowed:
                _refuse("unexpected_file")
            if item.is_symlink():
                _refuse("symlink")
    return dict(sorted(inventory.items()))


def _parse_ledger_with_fragments(
    raw: bytes,
) -> tuple[list[JsonObject], list[bytes]]:
    records, fragments = _parse_ledger_records(raw)
    return [entry for entry, _pending in records], fragments


def _parse_ledger_records(raw: bytes) -> tuple[list[LedgerRecord], list[bytes]]:
    entries: list[JsonObject] = []
    records: list[LedgerRecord] = []
    pending_fragments: list[bytes] = []
    offset = 0
    while offset < len(raw):
        if raw[offset] != 0x1E:
            _refuse("ledger_frame_missing_rs")
        next_lf = raw.find(b"\n", offset + 1)
        next_rs = raw.find(b"\x1e", offset + 1)
        if next_lf != -1 and (next_rs == -1 or next_lf < next_rs):
            frame = raw[offset : next_lf + 1]
            if b"\r" in frame or frame == b"\x1e\n":
                _refuse("ledger_frame")
            value = loads_v2(frame[1:-1].decode("utf-8"))
            if not isinstance(value, dict):
                _refuse("ledger_entry")
            entry = cast(JsonObject, value)
            if canonical_bytes_v2(entry) != frame[1:-1]:
                _refuse("ledger_noncanonical")
            _require_keys(entry, LEDGER_ENTRY_FIELDS, "ledger_field_set")
            verify_finalized_self_hash(entry, "entry_sha256")
            entries.append(entry)
            records.append((entry, tuple(pending_fragments)))
            pending_fragments.clear()
            offset = next_lf + 1
        else:
            end = next_rs if next_rs != -1 else len(raw)
            pending_fragments.append(raw[offset:end])
            offset = end
    return records, pending_fragments


def _validate_ledger_sequence(
    records: Sequence[LedgerRecord],
    fragments: Sequence[bytes],
    *,
    allow_terminal_partial: bool,
) -> None:
    prior_event = "EMPTY"
    prior_hash: str | None = None
    cumulative: dict[str, str] = {}
    for index, (entry, pending) in enumerate(records):
        if (
            entry["entry_index"] != index
            or entry["prior_entry_sha256_or_null"] != prior_hash
        ):
            _refuse("ledger_index")
        _validate_ledger_entry_semantics(entry, prior_event, prior_hash, pending)
        created = cast(Mapping[str, str], entry["created_file_hashes"])
        if entry["event_code"] == "FILE_CREATED":
            path, digest = next(iter(created.items()))
            if path in cumulative:
                _refuse("file_created_path_repeated")
            cumulative[path] = digest
        elif entry["event_code"] == "READY_TO_SEAL" and created != cumulative:
            _refuse("ledger_ready_created_map")
        prior_event = str(entry["event_code"])
        prior_hash = cast(str, entry["entry_sha256"])
    entries = [entry for entry, _pending in records]
    if fragments and not records:
        return
    if entries and entries[-1]["event_code"] == "INTERRUPTED_PARTIAL":
        if fragments:
            _refuse("interrupted_fragment_unrecorded")
        return
    if fragments and not allow_terminal_partial:
        return


def _validate_complete_ledger_bytes(raw: bytes) -> None:
    try:
        g6b_schema_contracts.validate_construction_ledger_bytes(raw)
    except g6b_schema_contracts.SchemaContractError as exc:
        raise ValueError(str(exc)) from exc


def _fragment_records(fragments: Sequence[bytes]) -> list[JsonObject]:
    return [
        {
            "fragment_index": index,
            "fragment_sha256": hashlib.sha256(fragment).hexdigest(),
            "fragment_byte_count": len(fragment),
        }
        for index, fragment in enumerate(fragments)
    ]


def _temp_path_for(path: Path, token: str) -> Path:
    return path.with_name(f".g6b-tmp-{token}-{path.name}")


def _temp_rel_path(rel_path: str, token: str) -> str:
    path = Path(rel_path)
    return path.with_name(f".g6b-tmp-{token}-{path.name}").as_posix()


def _authorization_attempt_token() -> str:
    return APPROVED_PLAN_ARTIFACT_HASH[:16]


def _write_attempt_token(candidate: CandidateBundle) -> str:
    return str(candidate.authorization["artifact_sha256"])[:16]


def _temp_for_rel(repo_root: Path, rel_path: str, token: str) -> Path:
    return _temp_path_for(_contained(repo_root, rel_path), token)


def _contained(repo_root: Path, rel_path: str) -> Path:
    if rel_path == "" or rel_path.startswith("/") or "\\" in rel_path:
        _refuse("path_escape")
    parts = rel_path.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        _refuse("path_escape")
    root = repo_root.resolve()
    candidate = root.joinpath(*parts)
    try:
        candidate.resolve(strict=False).relative_to(root)
    except ValueError as exc:
        raise ValueError("path_escape") from exc
    return candidate


def _validate_path_for_create(path: Path) -> None:
    if ".." in path.parts:
        _refuse("path_escape")
    for ancestor in reversed(path.parents):
        if ancestor.exists() and ancestor.is_symlink():
            _refuse("symlink")
    parent = path.parent
    if parent.exists() and not parent.is_dir():
        _refuse("parent_not_directory")


def _atomic_rename_no_replace(src: Path, dst: Path) -> None:
    if not _WINDOWS_CREATE_NEW_RENAME:
        raise ValueError("atomic_rename_platform")
    renamer = vars(os)["rename"]
    try:
        renamer(src, dst)
    except FileExistsError:
        raise
    except OSError as err:
        if dst.exists():
            raise FileExistsError(dst) from err
        raise ValueError("atomic_rename_failed") from err


def _validate_sealed_success(
    repo_root: Path, candidate: CandidateBundle, *, ledger_bytes: bytes | None = None
) -> None:
    ledger = (
        ledger_bytes
        if ledger_bytes is not None
        else (
            _contained(repo_root, _governance_path("construction_ledger.json"))
        ).read_bytes()
    )
    if ledger != candidate.ledger_bytes:
        _refuse("post_seal_ledger_mutation")
    inventory = _closed_materialization_inventory(
        repo_root, candidate, ledger_bytes=ledger
    )
    expected = {path: entry.sha256 for path, entry in candidate.all_files.items()}
    if inventory != expected:
        _refuse("sealed_inventory")
    if any(
        (_contained(repo_root, rel)).exists()
        for rel in _transient_paths_for_candidate(candidate)
    ):
        _refuse("sealed_transient")
    entries = _parse_ledger(ledger)
    manifest = loads_v2(
        _contained(
            repo_root, _governance_path("sealed_bundle_manifest.json")
        ).read_text(encoding="utf-8")
    )
    if not isinstance(manifest, dict):
        _refuse("manifest")
    manifest_obj = cast(Mapping[str, object], manifest)
    if manifest_obj["construction_ledger_head_sha256"] != entries[-1]["entry_sha256"]:
        _refuse("manifest_ledger_mismatch")


def _allowed_output_directories() -> set[str]:
    dirs: set[str] = set()
    for rel in _authorized_output_paths():
        path = Path(rel)
        for parent in path.parents:
            if parent == Path("."):
                continue
            dirs.add(parent.as_posix())
    return dirs


def _binary_flags(flags: int) -> int:
    return flags | getattr(os, "O_BINARY", 0)


def _open_fd(path: Path, flags: int) -> int:
    opener = vars(os)["open"]
    return cast(int, opener(path, _binary_flags(flags), 0o666))


def _write_all(fd: int, data: bytes) -> None:
    writer = vars(os)["write"]
    view = memoryview(data)
    offset = 0
    while offset < len(view):
        written = writer(fd, view[offset:])
        if written <= 0:
            _refuse("short_write")
        offset += written


def load_authorization_bytes(raw: bytes) -> Mapping[str, object]:
    value = loads_v2(raw.decode("utf-8"))
    if not isinstance(value, dict):
        _refuse("authorization_not_object")
    return validate_construction_authorization_for_materializer(
        cast(Mapping[str, object], value)
    )


def validate_construction_authorization_for_materializer(
    authorization: Mapping[str, object],
) -> Mapping[str, object]:
    _require_keys(authorization, AUTHORIZATION_FIELDS, "authorization_field_set")
    auth = cast(
        dict[str, object],
        _deep_thaw({key: authorization[key] for key in AUTHORIZATION_FIELDS}),
    )
    checks: tuple[tuple[str, object], ...] = (
        ("schema_version", AUTHORIZATION_SCHEMA_VERSION),
        ("capability", "case_construction"),
        ("authorized", True),
        ("bundle_id", BUNDLE_ID),
        ("case_unit_ids", list(CASE_UNIT_IDS)),
        ("method_observation_ids", list(METHOD_OBSERVATION_IDS)),
        ("method_companion_group_ids", list(METHOD_COMPANION_GROUP_IDS)),
        ("case_construction_schema_sha256", CASE_CONSTRUCTION_SCHEMA_SHA256),
        ("case_recipe_registry_sha256", CASE_RECIPE_REGISTRY_SHA256),
        ("frozen_row_family_matrix_sha256", FROZEN_ROW_FAMILY_MATRIX_SHA256),
        ("approved_corrigendum_hash", APPROVED_CORRIGENDUM_HASH),
        ("approved_plan_artifact_hash", APPROVED_PLAN_ARTIFACT_HASH),
        ("plan_review_artifact_hash", PLAN_REVIEW_ARTIFACT_HASH),
        ("allowed_operations", list(ALLOWED_OPERATIONS)),
        ("forbidden_operations", list(FORBIDDEN_OPERATIONS)),
        ("invalidated_by_identity_drift", False),
    )
    for key, expected in checks:
        if auth.get(key) != expected:
            _refuse(key)
    if auth["authorized"] is not True:
        _refuse("authorized")
    if auth["invalidated_by_identity_drift"] is not False:
        _refuse("invalidated_by_identity_drift")
    if not isinstance(auth["artifact_id"], str) or not auth["artifact_id"]:
        _refuse("artifact_id")
    _validate_issued_at_utc(auth["issued_at_utc"])
    for key in ("source_head", "source_tree_hash"):
        _require_lower_hex(auth[key], 40, key)
    for key in (
        "case_construction_schema_sha256",
        "case_recipe_registry_sha256",
        "frozen_row_family_matrix_sha256",
        "approved_corrigendum_hash",
        "approved_plan_artifact_hash",
        "plan_review_artifact_hash",
        "task2_review_artifact_hash",
        "artifact_sha256",
    ):
        _require_lower_hex(auth[key], 64, key)
    source_file_hashes = auth["source_file_hashes"]
    if not isinstance(source_file_hashes, dict):
        _refuse("source_file_hashes")
    source_hash_map = cast(Mapping[str, object], source_file_hashes)
    if tuple(source_hash_map) != AUTHORIZED_SOURCE_FILE_PATHS:
        _refuse("source_file_hashes")
    for value in source_hash_map.values():
        _require_lower_hex(value, 64, "source_file_hashes")
    try:
        verify_finalized_self_hash(cast(JsonObject, auth), "artifact_sha256")
    except ValueError as exc:
        raise ValueError("self_hash_mismatch") from exc
    return MappingProxyType(auth)


def _validate_issued_at_utc(value: object) -> None:
    if not isinstance(value, str):
        raise ValueError("issued_at_utc")
    timestamp = value
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", timestamp) is None:
        _refuse("issued_at_utc")
    try:
        parsed = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError as exc:
        raise ValueError("issued_at_utc") from exc
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != timestamp:
        _refuse("issued_at_utc")


def validate_runtime_source_identity(
    authorization: Mapping[str, object],
    *,
    current_head: str,
    current_tree_hash: str,
    current_source_file_hashes: Mapping[str, str],
    dirty_paths: Sequence[str],
    post_seal: bool = False,
    source_head_is_ancestor: bool = False,
) -> None:
    auth = validate_construction_authorization_for_materializer(authorization)
    if post_seal:
        if not source_head_is_ancestor:
            _refuse("source_identity_phase_violation")
    elif (
        current_head != auth["source_head"]
        or current_tree_hash != auth["source_tree_hash"]
    ):
        _refuse("source_identity_phase_violation")
    if dict(current_source_file_hashes) != dict(
        cast(Mapping[str, str], auth["source_file_hashes"])
    ):
        _refuse("source_identity_phase_violation")
    allowed_dirty = set(_authorized_output_paths())
    if post_seal:
        allowed_dirty.update(
            {
                "docs/verification/G6_B_CASE_CONSTRUCTION_REVIEW_V2.md",
                "PROJECT_HANDOFF.md",
                "docs/ROADMAP.md",
            }
        )
    if any(path not in allowed_dirty for path in dirty_paths):
        _refuse("source_identity_phase_violation")


def build_case_recipe_catalog() -> Mapping[str, object]:
    recipes = {str(row["case"]): _recipe_record(row) for row in _ROSTER}
    catalog: JsonObject = {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "bundle_id": BUNDLE_ID,
        "case_unit_ids": list(CASE_UNIT_IDS),
        "method_observation_ids": list(METHOD_OBSERVATION_IDS),
        "method_companion_group_ids": list(METHOD_COMPANION_GROUP_IDS),
        "case_unit_count": 13,
        "method_observation_count": 26,
        "method_companion_group_count": 13,
        "mandatory_control_ids": list(MANDATORY_CONTROL_IDS),
        "allowed_input_modes": ["explicit_finite_lts_input", "model_generated_lts"],
        "common_constants": _common_constants(),
        "recipes": cast(JsonObject, recipes),
        "catalog_sha256": None,
    }
    return MappingProxyType(_finalize(catalog, "catalog_sha256"))


def derive_seed_root_hex(authorization: Mapping[str, object]) -> str:
    auth = validate_construction_authorization_for_materializer(authorization)
    material: JsonObject = {
        "approved_plan_artifact_hash": str(auth["approved_plan_artifact_hash"]),
        "bundle_id": BUNDLE_ID,
        "case_recipe_registry_sha256": str(auth["case_recipe_registry_sha256"]),
        "frozen_row_family_matrix_sha256": FROZEN_ROW_FAMILY_MATRIX_SHA256,
        "plan_review_artifact_hash": str(auth["plan_review_artifact_hash"]),
        "schema_version": "ims-deadlock/g6b-des-seed-root-material/v1",
        "source_head": str(auth["source_head"]),
        "source_tree_hash": str(auth["source_tree_hash"]),
    }
    return canonical_sha256_v2(material)


def derive_seed_root_commitment_hex(seed_root_hex: str) -> str:
    if not _is_lower_hex(seed_root_hex, 64):
        _refuse("seed_root_hex")
    return canonical_sha256_v2(
        {
            "schema_version": "ims-deadlock/g6b-des-seed-root-commitment/v1",
            "seed_root_hex": seed_root_hex,
        }
    )


def derive_philox_key_hex(
    seed_root_hex: str,
    case_content_sha256: str,
    *,
    replicate_index: int,
) -> str:
    if not isinstance(seed_root_hex, str) or not _is_lower_hex(seed_root_hex, 64):
        _refuse("seed_root_hex")
    if not isinstance(case_content_sha256, str) or not _is_lower_hex(
        case_content_sha256, 64
    ):
        _refuse("case_content_sha256")
    if type(replicate_index) is not int or not 0 <= replicate_index < 4096:
        _refuse("replicate_index")
    fields = (
        "g6b_des_stream_v2",
        seed_root_hex,
        "Philox",
        "v1",
        case_content_sha256,
        "des_companion",
        "primary",
        str(replicate_index),
    )
    payload = b"".join(
        len(field.encode("utf-8")).to_bytes(8, "big") + field.encode("utf-8")
        for field in fields
    )
    return hashlib.sha256(payload).hexdigest()


def build_candidate_bundle(authorization: Mapping[str, object]) -> CandidateBundle:
    auth = validate_construction_authorization_for_materializer(authorization)
    catalog = build_case_recipe_catalog()
    planned_case_paths = _planned_case_paths()
    log = _construction_log(auth, catalog, planned_case_paths)
    log_file = _candidate_file(_governance_path("construction_log.json"), log)
    seed_root = derive_seed_root_hex(auth)
    seed_commitment = derive_seed_root_commitment_hex(seed_root)

    case_files: dict[str, CandidateFile] = {}
    case_record_hashes: dict[str, str] = {}
    method_record_hashes: dict[str, str] = {}
    group_record_hashes: dict[str, str] = {}
    prediction_hashes: dict[str, str] = {}
    lineage_hashes: dict[str, str] = {}
    metric_hashes: dict[str, str] = {}
    sharing_hashes: dict[str, str] = {}
    output_reservation_hashes: dict[str, str] = {}
    fingerprint_hashes: dict[str, str] = {}

    for row in _ROSTER:
        built = _build_case_files(row, str(log["log_sha256"]), seed_commitment)
        for rel_path, record in built.items():
            path = _case_path(str(row["case"]), rel_path)
            case_files[path] = _candidate_file(path, record)
        case_id = str(row["case"])
        exact_method_id = f"g6b_mo_{row['stem']}_exact_v1"
        des_method_id = f"g6b_mo_{row['stem']}_des_v1"
        group_id = f"g6b_mcg_{row['stem']}_v1"
        case_record_hashes[case_id] = case_files[
            _case_path(case_id, "case_input.json")
        ].sha256
        method_record_hashes[exact_method_id] = case_files[
            _case_path(case_id, "method_observations/exact.json")
        ].sha256
        method_record_hashes[des_method_id] = case_files[
            _case_path(case_id, "method_observations/des.json")
        ].sha256
        group_record_hashes[group_id] = case_files[
            _case_path(case_id, "method_companion_group.json")
        ].sha256
        prediction_hashes[case_id] = case_files[
            _case_path(case_id, "sealed_prediction.json")
        ].sha256
        lineage_hashes[case_id] = case_files[
            _case_path(case_id, "semantic_lineage_declaration.json")
        ].sha256
        metric_hashes[group_id] = case_files[
            _case_path(case_id, "metric_schema.json")
        ].sha256
        sharing_hashes[group_id] = case_files[
            _case_path(case_id, "metric_schema_sharing.json")
        ].sha256
        output_reservation_hashes[exact_method_id] = case_files[
            _case_path(case_id, "projections/output_root_reservation_exact.json")
        ].sha256
        output_reservation_hashes[des_method_id] = case_files[
            _case_path(case_id, "projections/output_root_reservation_des.json")
        ].sha256
        for rel_path in CASE_RELATIVE_PATHS:
            if rel_path.startswith("fingerprints/"):
                fingerprint_hashes[_case_path(case_id, rel_path)] = case_files[
                    _case_path(case_id, rel_path)
                ].sha256

    sorted_case_files = dict(sorted(case_files.items()))
    ledger_entries = _successful_ledger_entries(auth, log_file, sorted_case_files)
    ledger_bytes = b"".join(
        b"\x1e" + canonical_bytes_v2(entry) + b"\n" for entry in ledger_entries
    )
    ledger_file = CandidateFile(
        path=_governance_path("construction_ledger.json"),
        content=ledger_bytes,
        sha256=hashlib.sha256(ledger_bytes).hexdigest(),
        record=cast(
            Mapping[str, object], _deep_freeze({"entry_count": len(ledger_entries)})
        ),
    )
    manifest = _manifest(
        auth,
        case_record_hashes,
        method_record_hashes,
        group_record_hashes,
        fingerprint_hashes,
        prediction_hashes,
        lineage_hashes,
        metric_hashes,
        output_reservation_hashes,
        sharing_hashes,
        str(log["log_sha256"]),
        ledger_entries[-1]["entry_sha256"],
    )
    manifest_file = _candidate_file(
        _governance_path("sealed_bundle_manifest.json"), manifest
    )
    auth_file = _candidate_file(
        _governance_path("construction_authorization.json"),
        cast(JsonObject, _deep_thaw(auth)),
    )
    governance_files = {
        auth_file.path: auth_file,
        ledger_file.path: ledger_file,
        log_file.path: log_file,
        manifest_file.path: manifest_file,
    }
    candidate = CandidateBundle(
        authorization=auth,
        case_files=MappingProxyType(sorted_case_files),
        governance_files=MappingProxyType(dict(sorted(governance_files.items()))),
        manifest_bytes=manifest_file.content,
        ledger_bytes=ledger_bytes,
        immutable_log_bytes=log_file.content,
        ledger_ready_metadata=cast(
            Mapping[str, object],
            _deep_freeze(
                {
                    "ready_to_seal_entry_sha256": ledger_entries[-1]["entry_sha256"],
                    "created_file_hash_count": len(
                        cast(
                            Mapping[str, str], ledger_entries[-1]["created_file_hashes"]
                        )
                    ),
                    "manifest_last": True,
                    "ready_created_file_hashes": dict(
                        cast(
                            Mapping[str, str], ledger_entries[-1]["created_file_hashes"]
                        )
                    ),
                }
            ),
        ),
    )
    validate_candidate_bundle(candidate)
    return candidate


def validate_candidate_bundle(candidate: CandidateBundle) -> None:
    if candidate.filesystem_writes_performed != 0:
        _refuse("filesystem_write")
    if len(candidate.case_files) != 390:
        _refuse("case_file_count")
    if len(candidate.governance_files) != 4 or len(candidate.all_files) != 394:
        _refuse("total_file_count")
    if tuple(candidate.case_files) != tuple(sorted(candidate.case_files)):
        _refuse("case_file_order")
    expected_paths = set(_authorized_output_paths())
    if set(candidate.all_files) != expected_paths:
        _refuse("path_inventory")
    auth = validate_construction_authorization_for_materializer(candidate.authorization)
    parsed_records: dict[str, JsonObject] = {}
    for path, entry in candidate.all_files.items():
        if (
            entry.path != path
            or hashlib.sha256(entry.content).hexdigest() != entry.sha256
        ):
            _refuse("record_byte_hash")
        if path.endswith("construction_ledger.json"):
            continue
        parsed = loads_v2(entry.content.decode("utf-8"))
        if not isinstance(parsed, dict):
            _refuse("ordinary_file_not_object")
        parsed_record = cast(JsonObject, parsed)
        if canonical_bytes_v2(parsed_record) != entry.content:
            _refuse("noncanonical_content")
        if _deep_thaw(entry.record) != parsed_record:
            _refuse("record_content_drift")
        parsed_records[path] = parsed_record
    auth_path = _governance_path("construction_authorization.json")
    log_path = _governance_path("construction_log.json")
    ledger_path = _governance_path("construction_ledger.json")
    manifest_path = _governance_path("sealed_bundle_manifest.json")
    if parsed_records[auth_path] != _deep_thaw(auth):
        _refuse("authorization_record_mismatch")
    if candidate.immutable_log_bytes != candidate.governance_files[log_path].content:
        _refuse("log_bytes_mismatch")
    if candidate.ledger_bytes != candidate.governance_files[ledger_path].content:
        _refuse("ledger_bytes_mismatch")
    if candidate.manifest_bytes != candidate.governance_files[manifest_path].content:
        _refuse("manifest_bytes_mismatch")
    manifest_value = loads_v2(candidate.manifest_bytes.decode("utf-8"))
    if not isinstance(manifest_value, dict):
        _refuse("manifest")
    manifest = cast(JsonObject, manifest_value)
    if manifest != parsed_records[manifest_path]:
        _refuse("manifest_record_mismatch")
    _require_keys(manifest, SEALED_BUNDLE_MANIFEST_FIELDS, "manifest_field_set")
    verify_finalized_self_hash(manifest, "manifest_sha256")
    if manifest["case_file_count"] != 390 or manifest["governance_file_count"] != 4:
        _refuse("manifest_counts")
    if manifest["total_file_count"] != 394:
        _refuse("manifest_counts")
    log = parsed_records[log_path]
    _require_keys(log, CONSTRUCTION_LOG_FIELDS, "log_field_set")
    verify_finalized_self_hash(log, "log_sha256")
    if log["construction_authorization_sha256"] != auth["artifact_sha256"]:
        _refuse("log_auth_mismatch")
    if log["planned_case_file_paths"] != list(candidate.case_files):
        _refuse("log_path_inventory")
    if log["write_order"] != list(candidate.case_files):
        _refuse("log_write_order")
    if manifest["construction_authorization_hash"] != auth["artifact_sha256"]:
        _refuse("manifest_auth_mismatch")
    if manifest["construction_log_sha256"] != log["log_sha256"]:
        _refuse("manifest_log_mismatch")
    _validate_complete_ledger_bytes(candidate.ledger_bytes)
    ledger_entries = _parse_ledger(candidate.ledger_bytes)
    _validate_ledger_entries(
        ledger_entries,
        auth,
        candidate.governance_files[log_path],
        candidate.case_files,
    )
    if (
        manifest["construction_ledger_head_sha256"]
        != ledger_entries[-1]["entry_sha256"]
    ):
        _refuse("manifest_ledger_mismatch")
    ready_created_file_hashes = cast(
        Mapping[str, str], ledger_entries[-1]["created_file_hashes"]
    )
    if _deep_thaw(candidate.ledger_ready_metadata) != {
        "ready_to_seal_entry_sha256": ledger_entries[-1]["entry_sha256"],
        "created_file_hash_count": 391,
        "manifest_last": True,
        "ready_created_file_hashes": dict(ready_created_file_hashes),
    }:
        _refuse("ledger_ready_metadata")
    _validate_manifest_maps(manifest, candidate.case_files)
    _validate_case_cross_refs(parsed_records, candidate.case_files)
    _validate_materialization_file_contracts(parsed_records, candidate.case_files)
    for forbidden in (
        "state_space_hash",
        "partition_hash",
        "terminal_classes",
        "execution_result",
        "metric_observations",
    ):
        if forbidden.encode("utf-8") in b"".join(
            entry.content for entry in candidate.all_files.values()
        ):
            _refuse("outcome_leakage")


def _validate_materialization_file_contracts(
    records: Mapping[str, JsonObject],
    case_files: Mapping[str, CandidateFile],
) -> None:
    for path in case_files:
        record = records[path]
        relative_path = _case_relative_path(path)
        contract = g6b_schema_contracts.CASE_MATERIALIZATION_FILE_CONTRACTS.get(
            relative_path
        )
        if contract is None:
            raise ValueError("materialization_contract")
        schema_field = str(contract["schema_version_field_name"])
        if record.get(schema_field) != contract["schema_version_field_value"]:
            _refuse("materialization_schema_version")
        try:
            g6b_schema_contracts.validate_materialization_record_exact_keys(
                relative_path,
                record,
            )
        except g6b_schema_contracts.SchemaContractError as exc:
            raise ValueError("materialization_required_fields") from exc
        if relative_path.startswith("fingerprints/"):
            target = contract["direct_stored_fingerprint_target"]
            if not isinstance(target, str):
                raise ValueError("fingerprint_target")
            projection_path = path.rsplit("/", 2)[0] + "/" + target
            projection = records.get(projection_path)
            if projection is None:
                _refuse("fingerprint_target")
            try:
                g6b_schema_contracts.validate_fingerprint_record(
                    record,
                    projection,
                )
            except g6b_schema_contracts.SchemaContractError as exc:
                raise ValueError("fingerprint_contract") from exc
        elif relative_path.startswith("projections/output_root_reservation_"):
            try:
                g6b_schema_contracts.validate_output_root_reservation(record)
            except g6b_schema_contracts.SchemaContractError as exc:
                raise ValueError("output_root_reservation_contract") from exc


def _case_relative_path(path: str) -> str:
    try:
        return path.split("/case_units/", 1)[1].split("/", 1)[1]
    except IndexError as exc:
        raise ValueError("materialization_contract") from exc


def _require_keys(record: Mapping[str, object], keys: Sequence[str], code: str) -> None:
    if set(record) != set(keys):
        _refuse(code)


def _deep_freeze(value: JsonValue) -> JsonValue:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                str(key): _deep_freeze(nested)
                for key, nested in cast(Mapping[str, JsonValue], value).items()
            }
        )
    if isinstance(value, list | tuple):
        return tuple(_deep_freeze(nested) for nested in value)
    return value


def _deep_thaw(value: JsonValue) -> JsonValue:
    if isinstance(value, Mapping):
        return {
            str(key): _deep_thaw(nested)
            for key, nested in cast(Mapping[str, JsonValue], value).items()
        }
    if isinstance(value, tuple | list):
        return [_deep_thaw(nested) for nested in value]
    return value


def _parse_ledger(raw: bytes) -> list[JsonObject]:
    if not raw or not raw.endswith(b"\n") or b"\r" in raw:
        _refuse("ledger_frame")
    if b"\n\n" in raw:
        _refuse("ledger_frame")
    entries, fragments = _parse_ledger_with_fragments(raw)
    if fragments or not entries:
        _refuse("ledger_frame")
    return entries


def _validate_ledger_entries(
    entries: Sequence[JsonObject],
    auth: Mapping[str, object],
    log_file: CandidateFile,
    case_files: Mapping[str, CandidateFile],
) -> None:
    if entries[0]["event_code"] != "WRITE_STARTED":
        _refuse("ledger_start")
    prior: object = None
    cumulative: dict[str, str] = {}
    file_created_count = 0
    expected_file_order = [log_file.path, *case_files]
    for index, entry in enumerate(entries):
        if entry["entry_index"] != index:
            _refuse("ledger_index")
        if entry["prior_entry_sha256_or_null"] != prior:
            _refuse("ledger_prior")
        if (
            entry["construction_authorization_sha256_or_null"]
            != auth["artifact_sha256"]
        ):
            _refuse("ledger_authorization")
        if entry["source_head_or_null"] != auth["source_head"]:
            _refuse("ledger_source")
        if entry["source_tree_hash_or_null"] != auth["source_tree_hash"]:
            _refuse("ledger_source")
        if entry["candidate_log_sha256_or_null"] != log_file.sha256:
            _refuse("ledger_log")
        event_code = entry["event_code"]
        created = cast(Mapping[str, str], entry["created_file_hashes"])
        if event_code == "WRITE_STARTED":
            if created:
                _refuse("ledger_write_started")
        elif event_code == "FILE_CREATED":
            if len(created) != 1:
                _refuse("ledger_file_created")
            path, digest = next(iter(created.items()))
            expected_path = expected_file_order[file_created_count]
            if path != expected_path:
                _refuse("ledger_file_order")
            expected_digest = (
                log_file.sha256 if path == log_file.path else case_files[path].sha256
            )
            if digest != expected_digest:
                _refuse("ledger_file_hash")
            cumulative[path] = digest
            file_created_count += 1
        elif event_code == "READY_TO_SEAL":
            if created != cumulative:
                _refuse("ledger_ready_created_map")
            if file_created_count != 391:
                _refuse("ledger_ready_count")
        else:
            _refuse("ledger_event")
        prior = entry["entry_sha256"]
    if entries[-1]["event_code"] != "READY_TO_SEAL":
        _refuse("ledger_terminal")


def _validate_manifest_maps(
    manifest: Mapping[str, object],
    case_files: Mapping[str, CandidateFile],
) -> None:
    actual_case_hashes: dict[str, str] = {}
    actual_method_hashes: dict[str, str] = {}
    actual_group_hashes: dict[str, str] = {}
    actual_fingerprint_hashes: dict[str, str] = {}
    actual_prediction_hashes: dict[str, str] = {}
    actual_lineage_hashes: dict[str, str] = {}
    actual_metric_hashes: dict[str, str] = {}
    actual_output_hashes: dict[str, str] = {}
    actual_sharing_hashes: dict[str, str] = {}

    for path, entry in case_files.items():
        record = entry.record
        if path.endswith("/case_input.json"):
            actual_case_hashes[str(record["case_unit_id"])] = entry.sha256
        elif "/method_observations/" in path:
            actual_method_hashes[str(record["method_observation_id"])] = entry.sha256
        elif path.endswith("/method_companion_group.json"):
            actual_group_hashes[str(record["method_companion_group_id"])] = entry.sha256
        elif "/fingerprints/" in path:
            actual_fingerprint_hashes[path] = entry.sha256
        elif path.endswith("/sealed_prediction.json"):
            case_id = path.split("/case_units/", 1)[1].split("/", 1)[0]
            actual_prediction_hashes[case_id] = entry.sha256
        elif path.endswith("/semantic_lineage_declaration.json"):
            actual_lineage_hashes[str(record["case_unit_id"])] = entry.sha256
        elif path.endswith("/metric_schema.json"):
            group_id = _group_id_for_case_path(path)
            actual_metric_hashes[group_id] = entry.sha256
        elif path.endswith("/metric_schema_sharing.json"):
            actual_sharing_hashes[str(record["method_companion_group_id"])] = (
                entry.sha256
            )
        elif path.endswith(
            "/projections/output_root_reservation_des.json"
        ) or path.endswith("/projections/output_root_reservation_exact.json"):
            actual_output_hashes[str(record["method_observation_id"])] = entry.sha256

    comparisons = (
        ("case_unit_record_hashes", actual_case_hashes),
        ("method_observation_record_hashes", actual_method_hashes),
        ("method_companion_group_record_hashes", actual_group_hashes),
        ("fingerprint_record_hashes", actual_fingerprint_hashes),
        ("sealed_prediction_hashes", actual_prediction_hashes),
        ("semantic_lineage_declaration_hashes", actual_lineage_hashes),
        ("metric_schema_hashes", actual_metric_hashes),
        ("quantitative_output_root_reservations", actual_output_hashes),
        ("metric_schema_sharing_record_hashes", actual_sharing_hashes),
    )
    for key, actual in comparisons:
        if cast(Mapping[str, str], manifest[key]) != dict(sorted(actual.items())):
            _refuse(f"manifest_{key}")
    if manifest["planned_case_unit_ids"] != list(CASE_UNIT_IDS):
        _refuse("manifest_case_ids")
    if manifest["planned_method_observation_ids"] != list(METHOD_OBSERVATION_IDS):
        _refuse("manifest_method_ids")
    if manifest["planned_method_companion_group_ids"] != list(
        METHOD_COMPANION_GROUP_IDS
    ):
        _refuse("manifest_group_ids")
    if manifest["mandatory_control_ids"] != list(MANDATORY_CONTROL_IDS):
        _refuse("manifest_control_ids")


def _validate_case_cross_refs(
    records: Mapping[str, JsonObject],
    case_files: Mapping[str, CandidateFile],
) -> None:
    for path, record in records.items():
        if "/case_units/" not in path:
            continue
        if path.endswith("/semantic_lineage_declaration.json"):
            verify_finalized_self_hash(record, "declaration_sha256")
        elif path.endswith("/metric_schema_sharing.json"):
            verify_finalized_self_hash(record, "sharing_record_sha256")
        elif "/fingerprints/" in path:
            verify_finalized_self_hash(record, "record_provenance_sha256")
        elif path.endswith(
            "/projections/output_root_reservation_des.json"
        ) or path.endswith("/projections/output_root_reservation_exact.json"):
            verify_finalized_self_hash(record, "reservation_sha256")

    for case_id in CASE_UNIT_IDS:
        case_input_path = _case_path(case_id, "case_input.json")
        case_input = records[case_input_path]
        artifact_paths = cast(Mapping[str, object], case_input["case_artifact_paths"])
        if _deep_thaw(artifact_paths) != _expected_case_artifact_paths(case_id):
            _refuse("case_artifact_paths")
        ref_checks = {
            "case_content_sha256": _case_path(case_id, "projections/case_content.json"),
            "state_snapshot_sha256": _case_path(
                case_id, "projections/state_snapshot.json"
            ),
            "route_signature_sha256": _case_path(
                case_id, "projections/route_signature.json"
            ),
            "parameter_tuple_sha256": _case_path(
                case_id, "projections/parameter_tuple.json"
            ),
            "sealed_prediction_sha256": _case_path(case_id, "sealed_prediction.json"),
        }
        for field, ref_path in ref_checks.items():
            if case_input[field] != case_files[ref_path].sha256:
                _refuse("case_cross_ref")
        lineage = records[_case_path(case_id, "semantic_lineage_declaration.json")]
        if (
            case_input["semantic_lineage_declaration_hash"]
            != lineage["declaration_sha256"]
        ):
            _refuse("lineage_cross_ref")
        fingerprint_hashes = cast(
            Mapping[str, str], case_input["fingerprint_record_hashes"]
        )
        expected_fingerprints = {
            rel_path: records[_case_path(case_id, rel_path)]["record_provenance_sha256"]
            for rel_path in CASE_RELATIVE_PATHS
            if rel_path.startswith("fingerprints/")
        }
        if fingerprint_hashes != expected_fingerprints:
            _refuse("fingerprint_cross_ref")
        for method_rel in (
            "method_observations/des.json",
            "method_observations/exact.json",
        ):
            method = records[_case_path(case_id, method_rel)]
            suffix = "des" if method_rel.endswith("des.json") else "exact"
            stream_path = _case_path(
                case_id, f"projections/random_stream_manifest_{suffix}.json"
            )
            output_path = _case_path(
                case_id, f"projections/output_root_reservation_{suffix}.json"
            )
            if (
                method["random_stream_manifest_sha256"]
                != case_files[stream_path].sha256
            ):
                _refuse("method_stream_ref")
            if (
                method["output_root_reservation_sha256"]
                != records[output_path]["reservation_sha256"]
            ):
                _refuse("method_output_ref")
        companion = records[_case_path(case_id, "method_companion_group.json")]
        metric_path = _case_path(case_id, "metric_schema.json")
        sharing_path = _case_path(case_id, "metric_schema_sharing.json")
        if companion["metric_schema_sha256"] != case_files[metric_path].sha256:
            _refuse("companion_metric_ref")
        if (
            records[sharing_path]["metric_schema_sha256"]
            != case_files[metric_path].sha256
        ):
            _refuse("sharing_metric_ref")


def _group_id_for_case_path(path: str) -> str:
    case_id = path.split("/case_units/", 1)[1].split("/", 1)[0]
    for row in _ROSTER:
        if row["case"] == case_id:
            return f"g6b_mcg_{row['stem']}_v1"
    _refuse("unknown_case_id")
    raise AssertionError("unreachable")


def _expected_case_artifact_paths(case_id: str) -> JsonObject:
    return {
        "case_input": _case_path(case_id, "case_input.json"),
        "case_content_projection": _case_path(case_id, "projections/case_content.json"),
        "state_snapshot": _case_path(case_id, "projections/state_snapshot.json"),
        "route_signature": _case_path(case_id, "projections/route_signature.json"),
        "parameter_tuple": _case_path(case_id, "projections/parameter_tuple.json"),
        "rate_manifest": _case_path(case_id, "declarations/rate_manifest.json"),
        "policy_declaration": _case_path(
            case_id, "declarations/policy_declaration.json"
        ),
        "selected_target_declaration": _case_path(
            case_id, "declarations/selected_target_declaration.json"
        ),
        "control_declaration": _case_path(
            case_id, "declarations/control_declaration.json"
        ),
        "sealed_prediction": _case_path(case_id, "sealed_prediction.json"),
        "semantic_lineage_declaration": _case_path(
            case_id, "semantic_lineage_declaration.json"
        ),
        "method_observations": [
            _case_path(case_id, "method_observations/des.json"),
            _case_path(case_id, "method_observations/exact.json"),
        ],
        "random_stream_manifests": [
            _case_path(case_id, "projections/random_stream_manifest_des.json"),
            _case_path(case_id, "projections/random_stream_manifest_exact.json"),
        ],
        "output_root_reservations": [
            _case_path(case_id, "projections/output_root_reservation_des.json"),
            _case_path(case_id, "projections/output_root_reservation_exact.json"),
        ],
        "metric_schema": _case_path(case_id, "metric_schema.json"),
        "metric_schema_sharing": _case_path(case_id, "metric_schema_sharing.json"),
        "fingerprint_records": [
            _case_path(case_id, rel_path)
            for rel_path in sorted(CASE_RELATIVE_PATHS)
            if rel_path.startswith("fingerprints/")
        ],
    }


def _build_case_files(
    row: Mapping[str, object], log_sha256: str, seed_commitment: str
) -> Mapping[str, JsonObject]:
    case_id = str(row["case"])
    stem = str(row["stem"])
    exact_id = f"g6b_mo_{stem}_exact_v1"
    des_id = f"g6b_mo_{stem}_des_v1"
    group_id = f"g6b_mcg_{stem}_v1"
    state_snapshot = _state_snapshot(row)
    route_signature = _route_signature(row)
    rate_manifest = _rate_manifest(row)
    policy = _policy(row)
    target_payload = _target_payload(row)
    target = _target(row)
    control = _control(row)
    parameter_tuple = _parameter_tuple(
        row, _hash_record(rate_manifest), _hash_record(policy)
    )
    sealed_prediction = _sealed_prediction(row)
    case_content = {
        "projection_schema_version": "ims-deadlock/g6b-case-content-projection/v1",
        "input_mode": str(row["mode"]),
        "input_semantics_version": "ims-deadlock/g6b-case-input-semantics/v1",
        "state_snapshot_sha256": _hash_record(state_snapshot),
        "route_signature_sha256": _hash_record(route_signature),
        "parameter_tuple_sha256": _hash_record(parameter_tuple),
        "rate_manifest_content_sha256": _hash_record(rate_manifest),
        "policy_declaration_content_sha256": _hash_record(policy),
        "selected_target_declaration_sha256": _hash_record(target_payload),
        "control_declaration_sha256": _hash_record(control),
    }
    case_content_hash = _hash_record(case_content)
    metric_schema = _metric_schema()
    metric_hash = _hash_record(metric_schema)
    exact_stream = _exact_stream_projection()
    des_stream = _des_stream_projection(row, case_content_hash, seed_commitment)
    exact_output = _output_reservation(case_id, exact_id, "exact")
    des_output = _output_reservation(case_id, des_id, "des")
    semantic_lineage = _semantic_lineage(row, log_sha256)
    sharing = _metric_sharing(group_id, metric_hash)
    exact_method = _method_record(
        exact_id,
        case_id,
        group_id,
        "exact_companion",
        exact_stream,
        exact_output,
        metric_hash,
    )
    des_method = _method_record(
        des_id, case_id, group_id, "des_companion", des_stream, des_output, metric_hash
    )
    companion = _companion_record(group_id, case_id, exact_id, des_id, metric_hash)
    fingerprints = {
        "fingerprints/case_content_sha256.json": _fingerprint(
            "case_content_sha256",
            case_id,
            case_id,
            "case_unit",
            "projections/case_content.json",
            case_content_hash,
            str(case_content["projection_schema_version"]),
        ),
        "fingerprints/state_snapshot_sha256.json": _fingerprint(
            "state_snapshot_sha256",
            case_id,
            case_id,
            "case_unit",
            "projections/state_snapshot.json",
            _hash_record(state_snapshot),
            str(state_snapshot["projection_schema_version"]),
        ),
        "fingerprints/route_signature_sha256.json": _fingerprint(
            "route_signature_sha256",
            case_id,
            case_id,
            "case_unit",
            "projections/route_signature.json",
            _hash_record(route_signature),
            str(route_signature["projection_schema_version"]),
        ),
        "fingerprints/parameter_tuple_sha256.json": _fingerprint(
            "parameter_tuple_sha256",
            case_id,
            case_id,
            "case_unit",
            "projections/parameter_tuple.json",
            _hash_record(parameter_tuple),
            str(parameter_tuple["projection_schema_version"]),
        ),
        "fingerprints/sealed_prediction_sha256.json": _fingerprint(
            "sealed_prediction_sha256",
            case_id,
            case_id,
            "case_unit",
            "sealed_prediction.json",
            _hash_record(sealed_prediction),
            str(sealed_prediction["projection_schema_version"]),
        ),
        "fingerprints/metric_schema_sha256.json": _fingerprint(
            "metric_schema_sha256",
            group_id,
            group_id,
            "method_companion_group",
            "metric_schema.json",
            metric_hash,
            str(metric_schema["projection_schema_version"]),
        ),
        "fingerprints/random_stream_manifest_sha256_exact.json": _fingerprint(
            "random_stream_manifest_sha256",
            exact_id,
            exact_id,
            "method_observation",
            "projections/random_stream_manifest_exact.json",
            _hash_record(exact_stream),
            str(exact_stream["projection_schema_version"]),
            method_role="exact_companion",
        ),
        "fingerprints/random_stream_manifest_sha256_des.json": _fingerprint(
            "random_stream_manifest_sha256",
            des_id,
            des_id,
            "method_observation",
            "projections/random_stream_manifest_des.json",
            _hash_record(des_stream),
            str(des_stream["projection_schema_version"]),
            method_role="des_companion",
        ),
        "fingerprints/output_root_reservation_sha256_exact.json": _fingerprint(
            "output_root_reservation_sha256",
            exact_id,
            exact_id,
            "method_observation",
            "projections/output_root_reservation_exact.json",
            _hash_record(exact_output),
            str(exact_output["projection_schema_version"]),
            method_role="exact_companion",
        ),
        "fingerprints/output_root_reservation_sha256_des.json": _fingerprint(
            "output_root_reservation_sha256",
            des_id,
            des_id,
            "method_observation",
            "projections/output_root_reservation_des.json",
            _hash_record(des_output),
            str(des_output["projection_schema_version"]),
            method_role="des_companion",
        ),
    }
    case_input = _case_input(
        row,
        case_content_hash,
        state_snapshot,
        route_signature,
        parameter_tuple,
        sealed_prediction,
        fingerprints,
        semantic_lineage,
        exact_id,
        des_id,
    )
    records: dict[str, JsonObject] = {
        "case_input.json": case_input,
        "declarations/control_declaration.json": control,
        "declarations/policy_declaration.json": policy,
        "declarations/rate_manifest.json": rate_manifest,
        "declarations/selected_target_declaration.json": target,
        "method_companion_group.json": companion,
        "method_observations/des.json": des_method,
        "method_observations/exact.json": exact_method,
        "metric_schema.json": metric_schema,
        "metric_schema_sharing.json": sharing,
        "projections/case_content.json": case_content,
        "projections/output_root_reservation_des.json": des_output,
        "projections/output_root_reservation_exact.json": exact_output,
        "projections/parameter_tuple.json": parameter_tuple,
        "projections/random_stream_manifest_des.json": des_stream,
        "projections/random_stream_manifest_exact.json": exact_stream,
        "projections/route_signature.json": route_signature,
        "projections/state_snapshot.json": state_snapshot,
        "sealed_prediction.json": sealed_prediction,
        "semantic_lineage_declaration.json": semantic_lineage,
        **fingerprints,
    }
    return MappingProxyType(dict(sorted(records.items())))


def _recipe_record(row: Mapping[str, object]) -> JsonObject:
    rate = _rate_manifest(row)
    policy = _policy(row)
    target = _target_payload(row)
    control = _control(row)
    parameter = _parameter_tuple(row, _hash_record(rate), _hash_record(policy))
    state = _state_snapshot(row)
    route = _route_signature(row)
    case_content = {
        "projection_schema_version": "ims-deadlock/g6b-case-content-projection/v1",
        "input_mode": str(row["mode"]),
        "input_semantics_version": "ims-deadlock/g6b-case-input-semantics/v1",
        "state_snapshot_sha256": _hash_record(state),
        "route_signature_sha256": _hash_record(route),
        "parameter_tuple_sha256": _hash_record(parameter),
        "rate_manifest_content_sha256": _hash_record(rate),
        "policy_declaration_content_sha256": _hash_record(policy),
        "selected_target_declaration_sha256": _hash_record(target),
        "control_declaration_sha256": _hash_record(control),
    }
    return {
        "case_unit_id": str(row["case"]),
        "family_id": str(row["family"]),
        "source_template_id": str(row["template"]),
        "input_mode": str(row["mode"]),
        "state_bound": 100000 if row["case"] == CASE_UNIT_IDS[-1] else 512,
        "recipe": {
            "resources": list(cast(Sequence[str], row["resources"])),
            "routes": list(cast(Sequence[str], row["routes"])),
            "model_transitions": list(cast(Sequence[str], row["model_transitions"])),
            "state_payload": state["state_payload"],
            "parameter_overrides": list(cast(Sequence[str], row.get("parameters", ()))),
            "recipe_version": str(row["template"]),
        },
        "state": state,
        "route": route,
        "resource": list(cast(Sequence[str], row["resources"])),
        "rate": rate,
        "policy": policy,
        "target": target,
        "control": {
            "control_id_or_null": row["control"],
            "declaration": control,
        },
        "prediction": {
            "expected_boundary": str(row["expected"]),
            "sealed_prediction": _sealed_prediction(row),
        },
        "lineage": {
            "visible_retired_authority_ids": ["G4", "G5", "G6_R"],
            "declared_source_template_ids": [str(row["template"])],
            "declared_semantic_parent_ids": [],
            "declared_transform_codes": [
                "canonical_role_projection_v1",
                "from_first_principles_recipe_v1",
            ],
        },
        "case_content_projection": case_content,
        "recipe_sha256": canonical_sha256_v2(cast(JsonValue, case_content)),
    }


def _common_constants() -> JsonObject:
    return {
        "state_payload_schema_version": "ims-deadlock/g6b-state-snapshot-payload/v1",
        "route_semantics_version": "ims-deadlock/g6b-route-semantics/v1",
        "parameter_semantics_version": "ims-deadlock/g6b-parameter-semantics/v1",
        "rate_units": "events_per_time_unit",
        "canonical_rate": "1",
        "rate_source_code": "plan_constant_rate_v1",
        "policy_mode": "plant_unfiltered",
        "policy_filter_rule_code": "identity_filter_v1",
        "target_schema_version": "ims-deadlock/g6-terminal-stopping-partition/v3",
        "selected_bad_classes": ["D_global", "D_local"],
        "success_class": "F",
        "exact_stopping_rule": "first_hit_D_global_or_D_local_or_F_v1",
        "des_stopping_rule": "first_hit_D_global_or_D_local_or_F_or_censor_budget_v1",
        "policy_analysis_class": "P_policy",
    }


def _state_snapshot(row: Mapping[str, object]) -> JsonObject:
    if row["mode"] == "explicit_finite_lts_input":
        payload: JsonObject = {
            "states": list(cast(Sequence[str], row["states"])),
            "initial_state": str(row["initial"]),
            "marked_states": list(cast(Sequence[str], row["marked"])),
            "transitions": [
                _explicit_transition(item)
                for item in cast(Sequence[str], row["transitions"])
            ],
        }
    else:
        stable, complete, calendar, holds, requests, modes, stages = cast(
            tuple[object, ...], row["state_payload"]
        )
        payload = {
            "stable": bool(stable),
            "complete": bool(complete),
            "event_calendar_empty": bool(calendar),
            "holds": [_hold(item) for item in cast(Sequence[str], holds)],
            "requests": [_request(item) for item in cast(Sequence[str], requests)],
            "mode_by_job": [
                _pair_record(item, "job_role", "value")
                for item in cast(Sequence[str], modes)
            ],
            "stage_by_job": [
                _pair_record(item, "job_role", "value")
                for item in cast(Sequence[str], stages)
            ],
        }
    return {
        "projection_schema_version": "ims-deadlock/g6b-state-snapshot-projection/v1",
        "input_mode": str(row["mode"]),
        "state_payload_schema_version": "ims-deadlock/g6b-state-snapshot-payload/v1",
        "state_payload": payload,
    }


def _route_signature(row: Mapping[str, object]) -> JsonObject:
    return {
        "projection_schema_version": "ims-deadlock/g6b-route-signature-projection/v1",
        "input_mode": str(row["mode"]),
        "route_semantics_version": "ims-deadlock/g6b-route-semantics/v1",
        "typed_resource_roles": [
            _resource(item) for item in cast(Sequence[str], row["resources"])
        ],
        "typed_route_graph": [
            _route(item) for item in cast(Sequence[str], row["routes"])
        ],
        "transition_kinds": [
            _transition_kind(item)
            for item in cast(Sequence[str], row["model_transitions"])
        ],
        "resource_demand_structure": [
            _resource_demand(item)
            for item in cast(Sequence[str], row["model_transitions"])
        ],
        "mode_transition_structure": [
            _mode_transition(item)
            for item in cast(Sequence[str], row["model_transitions"])
        ],
    }


def _parameter_tuple(
    row: Mapping[str, object], rate_hash: str, policy_hash: str
) -> JsonObject:
    structural = [
        {
            "name": "input_semantics_version",
            "value_type": "string",
            "value": "ims-deadlock/g6b-case-input-semantics/v1",
        },
        {
            "name": "recipe_version",
            "value_type": "string",
            "value": str(row["template"]),
        },
    ]
    numeric = []
    for item in cast(Sequence[str], row["resources"]):
        role, _kind, capacity = item.split(":")
        numeric.append(
            {
                "name": f"capacity_{role}",
                "value_type": "integer",
                "value": int(capacity),
            }
        )
    for item in cast(Sequence[str], row.get("parameters", ())):
        name, value_type, value = item.split(":", 2)
        if value_type == "integer":
            actual: JsonValue = int(value)
        elif value_type == "boolean":
            actual = value == "true"
        else:
            actual = value
        structural.append({"name": name, "value_type": value_type, "value": actual})
    return {
        "projection_schema_version": "ims-deadlock/g6b-parameter-tuple-projection/v1",
        "parameter_semantics_version": "ims-deadlock/g6b-parameter-semantics/v1",
        "structural_parameter_entries": sorted(
            structural, key=lambda item: str(item["name"])
        ),
        "numeric_parameter_entries": sorted(
            numeric, key=lambda item: str(item["name"])
        ),
        "state_bound": 100000 if row["case"] == CASE_UNIT_IDS[-1] else 512,
        "rate_manifest_content_sha256": rate_hash,
        "policy_declaration_content_sha256": policy_hash,
    }


def _rate_manifest(row: Mapping[str, object]) -> JsonObject:
    event_roles = sorted(
        {
            _transition_kind(item)["transition_role"]
            for item in cast(Sequence[str], row["model_transitions"])
        }
    )
    return {
        "schema_version": "ims-deadlock/g6b-rate-manifest/v1",
        "rate_units": "events_per_time_unit",
        "event_rate_entries": [
            {
                "event_role": role,
                "canonical_rate": "1",
                "rate_source_code": "plan_constant_rate_v1",
            }
            for role in event_roles
        ],
    }


def _policy(row: Mapping[str, object]) -> JsonObject:
    mode, excluded, rule = cast(
        tuple[str, Sequence[str], str],
        row.get("policy", ("plant_unfiltered", (), "identity_filter_v1")),
    )
    return {
        "schema_version": "ims-deadlock/g6b-policy-declaration/v1",
        "mode": mode,
        "excluded_plant_arc_roles": list(excluded),
        "filter_rule_code": rule,
    }


def _target_payload(row: Mapping[str, object]) -> JsonObject:
    return {
        "target_schema_version": str(
            row.get("target_schema", "ims-deadlock/g6-terminal-stopping-partition/v3")
        ),
        "selected_bad_classes": ["D_global", "D_local"],
        "success_class": "F",
        "exact_stopping_rule": "first_hit_D_global_or_D_local_or_F_v1",
        "des_stopping_rule": "first_hit_D_global_or_D_local_or_F_or_censor_budget_v1",
        "policy_analysis_class": "P_policy",
    }


def _target(row: Mapping[str, object]) -> JsonObject:
    return {
        "schema_version": "ims-deadlock/g6b-selected-target-declaration/v1",
        **_target_payload(row),
    }


def _control(row: Mapping[str, object]) -> JsonObject:
    control = row["control"]
    if control is None:
        guards: list[str] = []
        controls: list[str] = []
        effects = ["no_claim_upgrade", "retain_mismatch"]
    else:
        controls = [str(control)]
        guards = str(row["expected"]).split("/")
        effects = [
            "block_quantitative_authorization",
            "no_claim_upgrade",
            "retain_control_failure",
        ]
    return {
        "schema_version": "ims-deadlock/g6b-control-declaration/v1",
        "mandatory_control_roles": controls,
        "expected_guard_codes": guards,
        "failure_effect_codes": effects,
    }


def _sealed_prediction(row: Mapping[str, object]) -> JsonObject:
    hypotheses = [
        {
            "hypothesis_role": f"{estimand}_direction",
            "statement": (
                f"Under {row['template']}, the expected discovery-only boundary is "
                f"{row['expected']}; any listed falsifier retains the case "
                "and prevents claim upgrade."
            ),
            "direction": "case_specific_predeclared",
            "estimand_id": estimand,
            "scope_code": "single_case_discovery_only",
            "falsifier_roles": list(cast(Sequence[str], row["falsifiers"])),
        }
        for estimand in ESTIMAND_IDS
    ]
    decision_table_hash = canonical_sha256_v2(
        [
            {
                "condition": "expected_certified_classification",
                "decision": "consistent_with_prediction_not_confirmation",
            },
            {
                "condition": "expected_boundary_refusal",
                "decision": "expected_boundary_retained",
            },
            {
                "condition": "certified_mismatch",
                "decision": "falsified_or_definition_limited",
            },
            {
                "condition": INCOMPLETE_BATCH_CONDITION,
                "decision": "not_evaluable_retained",
            },
        ]
    )
    return {
        "projection_schema_version": "ims-deadlock/g6b-sealed-prediction-projection/v1",
        "research_question": "first_hit_selected_bad_before_success_boundary",
        "directional_hypotheses": hypotheses,
        "falsifiers": [
            {
                "falsifier_role": code,
                "condition_code": code,
                "affected_hypothesis_roles": [
                    f"{estimand}_direction" for estimand in ESTIMAND_IDS
                ],
            }
            for code in cast(Sequence[str], row["falsifiers"])
        ],
        "mandatory_control_roles": []
        if row["control"] is None
        else [str(row["control"])],
        "planned_method_roles": ["des_companion", "exact_companion"],
        "scoring_rule": {
            "scoring_rule_id": "g6b_case_prediction_decision_table_v1",
            "required_input_roles": ["target_certification_case_result"],
            "decision_table_sha256": decision_table_hash,
            "failure_handling_code": "retain_refusal_or_mismatch_no_support_v1",
        },
        "claim_boundary": {
            "study_role": "discovery_only",
            "confirmation_use": "prohibited",
            "estimand_scope_code": "single_sealed_case_v1",
            "population_scope_code": "exact_13_case_roster_no_generalization_v1",
            "forbidden_upgrade_codes": [
                "confirmation_claim",
                "full_tranche_support_from_survivors",
                "general_ims_claim",
                "publication_ready_claim",
            ],
        },
    }


def _metric_schema() -> JsonObject:
    entries = [
        (
            "g6b_metric_theta_global_before_success_v1",
            "g6b_estimand_theta_global_before_success_v1",
        ),
        (
            "g6b_metric_theta_local_before_success_v1",
            "g6b_estimand_theta_local_before_success_v1",
        ),
        (
            "g6b_metric_theta_selected_bad_before_success_v1",
            "g6b_estimand_theta_selected_bad_before_success_v1",
        ),
    ]
    decision_table_hash = canonical_sha256_v2(
        [
            {
                "condition": "expected_certified_classification",
                "decision": "consistent_with_prediction_not_confirmation",
            },
            {
                "condition": "expected_boundary_refusal",
                "decision": "expected_boundary_retained",
            },
            {
                "condition": "certified_mismatch",
                "decision": "falsified_or_definition_limited",
            },
            {
                "condition": INCOMPLETE_BATCH_CONDITION,
                "decision": "not_evaluable_retained",
            },
        ]
    )
    return {
        "projection_schema_version": "ims-deadlock/g6b-metric-schema-projection/v1",
        "estimand_schema_version": "ims-deadlock/g6b-estimand-scope/v1",
        "metric_entries": [
            {
                "metric_id": metric,
                "estimand_id": estimand,
                "unit": "probability",
                "domain": "closed_unit_interval",
                "direction": "case_specific_predeclared",
                "aggregation_rule_id": "g6b_first_hit_probability_by_method_v1",
                "censoring_rule_id": "g6b_nonhit_is_censored_v1",
                "failure_rule_id": "g6b_refusal_is_non_supporting_v1",
                "scoring_rule_id": "g6b_case_prediction_decision_table_v1",
                "applicability_rule": "target_certified_and_same_target_locked_v1",
            }
            for metric, estimand in entries
        ],
        "aggregation_rules": [
            {
                "aggregation_rule_id": "g6b_first_hit_probability_by_method_v1",
                "exact_method_rule": "certified_finite_domain_probability",
                "des_method_rule": "4096_replicate_first_hit_bernoulli_estimator",
                "evidence_counting_rule": "methods_not_pooled_as_independent_cases",
            }
        ],
        "censoring_rules": [
            {
                "censoring_rule_id": "g6b_nonhit_is_censored_v1",
                "censoring_event": "no_selected_hit_before_draw_budget",
                "denominator_policy": "retain_original_denominator",
            }
        ],
        "failure_rules": [
            {
                "failure_rule_id": "g6b_refusal_is_non_supporting_v1",
                "retained_status_codes": [
                    "execution_failure",
                    "incomplete_batch",
                    "missing_rate",
                    "refusal",
                    "target_mismatch",
                    "truncation",
                ],
                "subset_selection_policy": "no_completed_case_only_bundle_conclusion",
            }
        ],
        "scoring_rules": [
            {
                "scoring_rule_id": "g6b_case_prediction_decision_table_v1",
                "decision_table_sha256": decision_table_hash,
                "claim_upgrade_policy": "no_completed_case_only_bundle_conclusion",
            }
        ],
        "comparability_scope": "exact_des_within_one_companion_group_only",
    }


def _exact_stream_projection() -> JsonObject:
    return {
        "projection_schema_version": RANDOM_STREAM_PROJECTION_VERSION,
        "applicability_status": "not_applicable_by_protocol",
        "method_role": "exact_companion",
        "reason_code": "exact_method_has_no_random_stream",
    }


def _des_stream_projection(
    row: Mapping[str, object], case_content_hash: str, seed_commitment: str
) -> JsonObject:
    label = canonical_sha256_v2(
        {
            "case_content_sha256": case_content_hash,
            "derivation_rule": "g6b_philox_length_prefixed_sha256_v2",
            "method_role": "des_companion",
            "prng_family": "Philox",
            "prng_version": "v1",
            "replicate_index_start": 0,
            "replicate_index_stop_exclusive": 4096,
            "schema_version": "ims-deadlock/g6b-des-derivation-domain/v1",
            "seed_root_commitment": seed_commitment,
            "stream_role": "primary",
        }
    )
    state_bound = 100000 if row["case"] == CASE_UNIT_IDS[-1] else 512
    return {
        "projection_schema_version": RANDOM_STREAM_PROJECTION_VERSION,
        "applicability_status": "applicable",
        "method_role": "des_companion",
        "prng_family": "Philox",
        "prng_version": "v1",
        "seed_root_commitment": seed_commitment,
        "seed_derivation_rule": "g6b_philox_length_prefixed_sha256_v2",
        "substream_allocation": [
            {
                "stream_role": "primary",
                "derivation_label_sha256": label,
                "start_counter": 0,
                "stop_counter_exclusive": 4096,
                "stride": 1,
            }
        ],
        "replicate_plan": {
            "planned_replicates": 4096,
            "replicate_index_start": 0,
            "replicate_index_stop_exclusive": 4096,
        },
        "sampling_plan": {
            "stopping_rule_sha256": canonical_sha256_v2(
                "first_hit_D_global_or_D_local_or_F_or_censor_budget_v1"
            ),
            "draw_budget_per_replication": min(65536, 16 * state_bound),
            "common_random_numbers_group_or_null": None,
            "antithetic_policy": "none",
        },
    }


def _output_reservation(case_id: str, method_id: str, suffix: str) -> JsonObject:
    root_path = "/".join(
        (
            "artifacts",
            "g6b",
            "quantitative",
            BUNDLE_ID,
            case_id,
            method_id,
            "primary",
        )
    )
    record = {
        "projection_schema_version": OUTPUT_ROOT_RESERVATION_PROJECTION_VERSION,
        "bundle_id": BUNDLE_ID,
        "case_unit_id": case_id,
        "method_observation_id": method_id,
        "run_role": "primary",
        "logical_root_id": "primary",
        "repo_relative_posix_path": root_path,
        "reserved": True,
        "materialized": False,
        "reservation_sha256": None,
    }
    del suffix
    return _finalize(record, "reservation_sha256")


def _method_record(
    method_id: str,
    case_id: str,
    group_id: str,
    role: str,
    stream: JsonObject,
    output: JsonObject,
    metric_hash: str,
) -> JsonObject:
    return {
        "schema_version": "ims-deadlock/g6b-method-observation/v1",
        "bundle_id": BUNDLE_ID,
        "method_observation_id": method_id,
        "case_unit_id": case_id,
        "method_companion_group_id": group_id,
        "method_role": role,
        "random_stream_manifest_sha256": _hash_record(stream),
        "output_root_reservation_sha256": _self_hash(output, "reservation_sha256"),
        "metric_schema_sha256": metric_hash,
        "fingerprint_record_hashes": {},
        "stopping_rule_ref": "first_hit_D_global_or_D_local_or_F_v1",
        "des_stopping_rule_ref_or_null": (
            "first_hit_D_global_or_D_local_or_F_or_censor_budget_v1"
            if role == "des_companion"
            else None
        ),
        "method_state": "METHOD_SEALED_NO_OUTPUT",
    }


def _companion_record(
    group_id: str, case_id: str, exact_id: str, des_id: str, metric_hash: str
) -> JsonObject:
    return {
        "schema_version": "ims-deadlock/g6b-method-companion-group/v1",
        "bundle_id": BUNDLE_ID,
        "method_companion_group_id": group_id,
        "case_unit_id": case_id,
        "member_method_observation_ids": sorted([des_id, exact_id]),
        "member_method_roles": {
            des_id: "des_companion",
            exact_id: "exact_companion",
        },
        "metric_schema_ref": "metric_schema.json",
        "metric_schema_sha256": metric_hash,
        "same_target_required": True,
        "allowed_reuse_reason_code": "intra_bundle_preregistered_comparability_only",
        "reuse_authorization_ref_or_null": None,
        "evidence_counting_rule": (
            "one_case_unit_distinct_method_observations_not_independent_cases"
        ),
        "fingerprint_record_hashes": {},
        "companion_group_state": "METHOD_SEALED_NO_OUTPUT",
    }


def _semantic_lineage(row: Mapping[str, object], log_sha256: str) -> JsonObject:
    return _finalize(
        {
            "schema_version": "ims-deadlock/g6b-semantic-lineage-declaration/v1",
            "declaration_id": f"{row['case']}_semantic_lineage_v1",
            "case_unit_id": str(row["case"]),
            "constructor_role": "post_approval_first_principles_materializer",
            "visible_retired_authority_ids": ["G4", "G5", "G6_R"],
            "declared_source_template_ids": [str(row["template"])],
            "declared_source_artifact_hashes": [
                APPROVED_PLAN_ARTIFACT_HASH,
                "materializer_source_hash_bound_in_authorization",
            ],
            "declared_semantic_parent_ids": [],
            "declared_transform_codes": [
                "canonical_role_projection_v1",
                "from_first_principles_recipe_v1",
            ],
            "construction_log_sha256": log_sha256,
            "graph_isomorphism_check_required": True,
            "outcome_driven_tuning_prohibited": True,
            "review_artifact_hash": PLAN_REVIEW_ARTIFACT_HASH,
            "declaration_sha256": None,
        },
        "declaration_sha256",
    )


def _metric_sharing(group_id: str, metric_hash: str) -> JsonObject:
    return _finalize(
        {
            "schema_version": "ims-deadlock/g6b-metric-schema-sharing/v1",
            "sharing_record_id": f"{group_id}_metric_schema_sharing_v1",
            "bundle_id": BUNDLE_ID,
            "method_companion_group_id": group_id,
            "metric_schema_sha256": metric_hash,
            "canonical_owner_method_companion_group_id": METHOD_COMPANION_GROUP_IDS[0],
            "sharing_group_ids": list(METHOD_COMPANION_GROUP_IDS),
            "sharing_reason_code": (
                "same_preregistered_estimand_metric_and_scoring_contract"
            ),
            "comparability_requirement": "exact_des_and_cross_case_schema_parity",
            "independent_case_evidence": False,
            "retired_authority_reuse_claimed": False,
            "retired_reuse_authorization_ref_or_null": None,
            "review_artifact_hash": PLAN_REVIEW_ARTIFACT_HASH,
            "sharing_record_sha256": None,
        },
        "sharing_record_sha256",
    )


def _fingerprint(
    dimension: str,
    subject_id: str,
    owner_id: str,
    subject_type: str,
    projection_ref: str,
    projection_hash: str,
    projection_schema_version: str,
    *,
    method_role: str | None = None,
) -> JsonObject:
    return _finalize(
        {
            "record_schema_version": "ims-deadlock/g6b-fingerprint-record/v2",
            "record_id": (
                f"{owner_id}_"
                f"{projection_ref.replace('/', '_').replace('.', '_')}"
                "_fingerprint_v1"
            ),
            "dimension": dimension,
            "projection_kind": g6b_schema_contracts.DIMENSION_PROJECTION_KINDS[
                dimension
            ],
            "subject_type": subject_type,
            "subject_id": subject_id,
            "owner_object_id": owner_id,
            "projection_schema_version": projection_schema_version,
            "comparison_projection_ref_or_null": projection_ref,
            "comparison_projection_sha256_or_null": projection_hash,
            "canonicalization_version": CANONICAL_JSON_VERSION,
            "source_authority_id": BUNDLE_ID,
            "source_stage": "case_construction",
            "source_method_role_or_null": method_role,
            "source_run_role_or_null": None,
            "source_artifact_refs": [
                {
                    "authority_id": BUNDLE_ID,
                    "repo_relative_posix_path": projection_ref,
                    "json_pointer_or_null": None,
                    "source_role": "direct_stored_projection",
                }
            ],
            "source_artifact_byte_hashes": {projection_ref: projection_hash},
            "normalizer_version": "direct_store_no_normalizer_v1",
            "dimension_status": "direct_stored",
            "lineage_id": f"sha256:{projection_hash}",
            "inherited_from_record_id_or_null": None,
            "duplicate_lineage_of_record_id_or_null": None,
            "depends_on_dimensions": sorted(
                g6b_schema_contracts.DIMENSION_DEPENDS_ON[dimension]
            ),
            "correlated_with_dimensions": sorted(
                g6b_schema_contracts.DIMENSION_CORRELATED_WITH[dimension]
            ),
            "comparison_policy": g6b_schema_contracts.DIMENSION_POLICIES[dimension],
            "applicability_reason_code_or_null": None,
            "record_provenance_sha256": None,
        },
        "record_provenance_sha256",
    )


def _case_input(
    row: Mapping[str, object],
    case_content_hash: str,
    state: JsonObject,
    route: JsonObject,
    parameter: JsonObject,
    prediction: JsonObject,
    fingerprints: Mapping[str, JsonObject],
    lineage: JsonObject,
    exact_id: str,
    des_id: str,
) -> JsonObject:
    case_id = str(row["case"])
    artifact_paths = {
        "case_input": _case_path(case_id, "case_input.json"),
        "case_content_projection": _case_path(case_id, "projections/case_content.json"),
        "state_snapshot": _case_path(case_id, "projections/state_snapshot.json"),
        "route_signature": _case_path(case_id, "projections/route_signature.json"),
        "parameter_tuple": _case_path(case_id, "projections/parameter_tuple.json"),
        "rate_manifest": _case_path(case_id, "declarations/rate_manifest.json"),
        "policy_declaration": _case_path(
            case_id, "declarations/policy_declaration.json"
        ),
        "selected_target_declaration": _case_path(
            case_id, "declarations/selected_target_declaration.json"
        ),
        "control_declaration": _case_path(
            case_id, "declarations/control_declaration.json"
        ),
        "sealed_prediction": _case_path(case_id, "sealed_prediction.json"),
        "semantic_lineage_declaration": _case_path(
            case_id, "semantic_lineage_declaration.json"
        ),
        "method_observations": [
            _case_path(case_id, "method_observations/des.json"),
            _case_path(case_id, "method_observations/exact.json"),
        ],
        "random_stream_manifests": [
            _case_path(case_id, "projections/random_stream_manifest_des.json"),
            _case_path(case_id, "projections/random_stream_manifest_exact.json"),
        ],
        "output_root_reservations": [
            _case_path(case_id, "projections/output_root_reservation_des.json"),
            _case_path(case_id, "projections/output_root_reservation_exact.json"),
        ],
        "metric_schema": _case_path(case_id, "metric_schema.json"),
        "metric_schema_sharing": _case_path(case_id, "metric_schema_sharing.json"),
        "fingerprint_records": [
            _case_path(case_id, path) for path in sorted(fingerprints)
        ],
    }
    return {
        "schema_version": "ims-deadlock/g6b-case-unit/v1",
        "bundle_id": BUNDLE_ID,
        "case_unit_id": case_id,
        "family_id": str(row["family"]),
        "input_mode": str(row["mode"]),
        "structural_family_role": str(row["template"]),
        "negative_control_id_or_null": row["control"],
        "case_artifact_paths": artifact_paths,
        "case_content_sha256": case_content_hash,
        "state_snapshot_sha256": _hash_record(state),
        "route_signature_sha256": _hash_record(route),
        "parameter_tuple_sha256": _hash_record(parameter),
        "sealed_prediction_sha256": _hash_record(prediction),
        "rate_manifest_ref": "declarations/rate_manifest.json",
        "policy_declaration_ref": "declarations/policy_declaration.json",
        "selected_target_ref": "declarations/selected_target_declaration.json",
        "control_declaration_ref": "declarations/control_declaration.json",
        "state_bound": 100000 if case_id == CASE_UNIT_IDS[-1] else 512,
        "state_snapshot_payload_schema_version": (
            "ims-deadlock/g6b-state-snapshot-payload/v1"
        ),
        "state_snapshot_nesting_relation": "declared_subidentity_of_case_content",
        "state_snapshot_parent_case_content_sha256": case_content_hash,
        "fingerprint_record_hashes": {
            path: _self_hash(record, "record_provenance_sha256")
            for path, record in sorted(fingerprints.items())
        },
        "semantic_lineage_declaration_hash": _self_hash(lineage, "declaration_sha256"),
        "method_observation_ids": sorted([des_id, exact_id]),
        "case_unit_state": "CASE_UNIT_SEALED_NO_EXECUTION",
    }


def _construction_log(
    auth: Mapping[str, object],
    catalog: Mapping[str, object],
    planned_paths: Sequence[str],
) -> JsonObject:
    recipes = cast(Mapping[str, Mapping[str, object]], catalog["recipes"])
    return _finalize(
        {
            "schema_version": "ims-deadlock/g6b-construction-log/v1",
            "log_id": f"{BUNDLE_ID}_construction_log_v1",
            "bundle_id": BUNDLE_ID,
            "construction_authorization_sha256": str(auth["artifact_sha256"]),
            "source_head": str(auth["source_head"]),
            "source_tree_hash": str(auth["source_tree_hash"]),
            "source_file_hashes": cast(
                JsonObject, dict(cast(Mapping[str, str], auth["source_file_hashes"]))
            ),
            "case_construction_schema_sha256": CASE_CONSTRUCTION_SCHEMA_SHA256,
            "case_recipe_catalog_schema_version": CATALOG_SCHEMA_VERSION,
            "case_recipe_registry_sha256": CASE_RECIPE_REGISTRY_SHA256,
            "case_recipe_hashes": {
                case_id: str(recipes[case_id]["recipe_sha256"])
                for case_id in CASE_UNIT_IDS
            },
            "case_transform_records": {
                case_id: {
                    "declared_source_template_ids": [
                        str(recipes[case_id]["source_template_id"])
                    ],
                    "declared_source_artifact_hashes": [
                        APPROVED_PLAN_ARTIFACT_HASH,
                        "materializer_source_hash_bound_in_authorization",
                    ],
                    "declared_semantic_parent_ids": [],
                    "declared_transform_codes": [
                        "canonical_role_projection_v1",
                        "from_first_principles_recipe_v1",
                    ],
                    "visible_retired_authority_ids": ["G4", "G5", "G6_R"],
                    "retired_case_payload_read": False,
                    "retired_outcome_used": False,
                    "graph_isomorphism_check_required": True,
                    "outcome_driven_tuning_prohibited": True,
                }
                for case_id in CASE_UNIT_IDS
            },
            "candidate_case_unit_ids": list(CASE_UNIT_IDS),
            "candidate_method_observation_ids": list(METHOD_OBSERVATION_IDS),
            "candidate_method_companion_group_ids": list(METHOD_COMPANION_GROUP_IDS),
            "planned_case_file_paths": list(planned_paths),
            "write_order": list(planned_paths),
            "forbidden_operation_checks": {
                operation: False for operation in FORBIDDEN_OPERATIONS
            },
            "log_sha256": None,
        },
        "log_sha256",
    )


def _successful_ledger_entries(
    auth: Mapping[str, object],
    log_file: CandidateFile,
    case_files: Mapping[str, CandidateFile],
) -> list[JsonObject]:
    cumulative: dict[str, str] = {}
    entries: list[JsonObject] = []

    def append(event_code: str, created: Mapping[str, str]) -> None:
        prior = entries[-1]["entry_sha256"] if entries else None
        entry = _finalize(
            {
                "schema_version": "ims-deadlock/g6b-construction-ledger-entry/v1",
                "bundle_id": BUNDLE_ID,
                "attempt_id": str(auth["artifact_id"]),
                "entry_index": len(entries),
                "event_code": event_code,
                "prior_entry_sha256_or_null": prior,
                "construction_authorization_sha256_or_null": str(
                    auth["artifact_sha256"]
                ),
                "source_head_or_null": str(auth["source_head"]),
                "source_tree_hash_or_null": str(auth["source_tree_hash"]),
                "candidate_log_sha256_or_null": log_file.sha256,
                "created_file_hashes": dict(sorted(created.items())),
                "observed_partial_file_hashes": {},
                "refusal_reason_codes": [],
                "causal_entry_sha256_or_null": None,
                "interrupted_fragments": [],
                "entry_sha256": None,
            },
            "entry_sha256",
        )
        entries.append(entry)

    append("WRITE_STARTED", {})
    cumulative[log_file.path] = log_file.sha256
    append("FILE_CREATED", {log_file.path: log_file.sha256})
    for path, entry_file in case_files.items():
        cumulative[path] = entry_file.sha256
        append("FILE_CREATED", {path: entry_file.sha256})
    append("READY_TO_SEAL", cumulative)
    return entries


def _manifest(
    auth: Mapping[str, object],
    case_hashes: Mapping[str, str],
    method_hashes: Mapping[str, str],
    group_hashes: Mapping[str, str],
    fingerprint_hashes: Mapping[str, str],
    prediction_hashes: Mapping[str, str],
    lineage_hashes: Mapping[str, str],
    metric_hashes: Mapping[str, str],
    output_hashes: Mapping[str, str],
    sharing_hashes: Mapping[str, str],
    log_hash: str,
    ledger_head_hash: object,
) -> JsonObject:
    return _finalize(
        {
            "schema_version": "ims-deadlock/g6b-sealed-bundle-manifest/v2",
            "bundle_id": BUNDLE_ID,
            "construction_authorization_hash": str(auth["artifact_sha256"]),
            "planned_case_unit_ids": list(CASE_UNIT_IDS),
            "planned_method_observation_ids": list(METHOD_OBSERVATION_IDS),
            "planned_method_companion_group_ids": list(METHOD_COMPANION_GROUP_IDS),
            "case_unit_record_hashes": dict(sorted(case_hashes.items())),
            "method_observation_record_hashes": dict(sorted(method_hashes.items())),
            "method_companion_group_record_hashes": dict(sorted(group_hashes.items())),
            "mandatory_control_ids": list(MANDATORY_CONTROL_IDS),
            "fingerprint_record_hashes": dict(sorted(fingerprint_hashes.items())),
            "sealed_prediction_hashes": dict(sorted(prediction_hashes.items())),
            "semantic_lineage_declaration_hashes": dict(sorted(lineage_hashes.items())),
            "metric_schema_hashes": dict(sorted(metric_hashes.items())),
            "quantitative_output_root_reservations": dict(
                sorted(output_hashes.items())
            ),
            "planned_case_unit_count": 13,
            "planned_method_count": 26,
            "planned_companion_group_count": 13,
            "manifest_sha256": None,
            "construction_log_sha256": log_hash,
            "construction_ledger_head_sha256": str(ledger_head_hash),
            "metric_schema_sharing_record_hashes": dict(sorted(sharing_hashes.items())),
            "case_file_count": 390,
            "governance_file_count": 4,
            "total_file_count": 394,
        },
        "manifest_sha256",
    )


def _resource(value: str) -> JsonObject:
    role, kind, capacity = value.split(":")
    return {
        "resource_role": role,
        "resource_kind": kind,
        "capacity_parameter_name": f"capacity_{role}",
    }


def _route(value: str) -> JsonObject:
    role, stages = value.split(":[", 1)
    return {
        "route_role": role,
        "ordered_stage_roles": stages.rstrip("]").split(",")
        if stages.rstrip("]")
        else [],
    }


def _transition_parts(value: str) -> tuple[str, str, str, str, str, str]:
    role, event, source, target, demands = value.split(":", 4)
    separator = demands.find("]:[")
    if separator < 0:
        _refuse("transition_tuple")
    acquire = demands[: separator + 1]
    release = demands[separator + 2 :]
    return role, event, source, target, acquire, release


def _transition_kind(value: str) -> JsonObject:
    role, event, source, target, _acquire, _release = _transition_parts(value)
    return {
        "transition_role": role,
        "event_kind": event,
        "source_mode": source,
        "target_mode": target,
    }


def _resource_demand(value: str) -> JsonObject:
    role, _event, _source, _target, acquire, release = _transition_parts(value)
    return {
        "transition_role": role,
        "acquire_demands": _demands(acquire),
        "release_demands": _demands(release),
    }


def _mode_transition(value: str) -> JsonObject:
    role, event, source, target, _acquire, _release = _transition_parts(value)
    return {
        "job_role": role,
        "source_stage": source,
        "event_kind": event,
        "target_stage": target,
    }


def _demands(value: str) -> list[JsonObject]:
    inner = value.strip("[]")
    if not inner:
        return []
    return [_demand(item) for item in inner.split(",")]


def _demand(value: str) -> JsonObject:
    role, amount = value.split(":")
    return {"resource_role": role, "amount": int(amount)}


def _hold(value: str) -> JsonObject:
    job, resource, amount = value.split(":")
    return {"job_role": job, "resource_role": resource, "amount": int(amount)}


def _request(value: str) -> JsonObject:
    job, rest = value.split(":", 1)
    alternatives = []
    for raw_alt in rest.removeprefix("[").removesuffix("]").split("],["):
        cleaned = raw_alt.strip("[]")
        alternatives.append([_demand(item) for item in cleaned.split(",") if item])
    return {"job_role": job, "alternatives": alternatives}


def _pair_record(value: str, key_name: str, value_name: str) -> JsonObject:
    key, data = value.split(":", 1)
    return {key_name: key, value_name: data}


def _explicit_transition(value: str) -> JsonObject:
    source, event, target = value.split(":")
    return {"source": source, "event_kind": event, "target": target}


def _planned_case_paths() -> list[str]:
    return sorted(
        _case_path(case_id, rel_path)
        for case_id in CASE_UNIT_IDS
        for rel_path in CASE_RELATIVE_PATHS
    )


def _authorized_output_paths() -> tuple[str, ...]:
    return tuple(
        sorted(
            (
                _governance_path("construction_authorization.json"),
                _governance_path("construction_ledger.json"),
                _governance_path("construction_log.json"),
                _governance_path("sealed_bundle_manifest.json"),
                *_planned_case_paths(),
            )
        )
    )


def _case_path(case_id: str, rel_path: str) -> str:
    return (
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        f"case_units/{case_id}/{rel_path}"
    )


def _governance_path(name: str) -> str:
    return (
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        f"governance/{BUNDLE_ID}/{name}"
    )


def _candidate_file(path: str, record: JsonObject) -> CandidateFile:
    content = canonical_bytes_v2(record)
    parsed = loads_v2(content.decode("utf-8"))
    if not isinstance(parsed, dict):
        _refuse("candidate_file_record")
    return CandidateFile(
        path=path,
        content=content,
        sha256=hashlib.sha256(content).hexdigest(),
        record=cast(Mapping[str, object], _deep_freeze(parsed)),
    )


def _hash_record(record: JsonValue) -> str:
    return canonical_sha256_v2(record)


def _self_hash(record: JsonObject, field: str) -> str:
    value = record[field]
    if not isinstance(value, str):
        _refuse(field)
    return cast(str, value)


def _finalize(record: JsonObject, field: str) -> JsonObject:
    finalized = dict(record)
    finalized[field] = canonical_sha256_v2({**finalized, field: None})
    return finalized


def _is_lower_hex(value: str, length: int) -> bool:
    return len(value) == length and all(char in "0123456789abcdef" for char in value)


def _require_lower_hex(value: object, length: int, code: str) -> None:
    if not isinstance(value, str) or not _is_lower_hex(value, length):
        _refuse(code)


def _refuse(code: str) -> None:
    raise ValueError(code)
