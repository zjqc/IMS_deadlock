# G6-B Case Construction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task.

Status: `PROPOSED / PLAN-ONLY / AWAITING EXACT-BYTES USER APPROVAL`

Date: 2026-08-02

## Goal

Create one sealed, discovery-only G6-B case-construction bundle that covers the
seven mandatory negative controls and the remaining handoff discovery axes with
the smallest defensible combined roster. The tranche ends with input,
prediction, metric-schema, method, provenance, reservation, and manifest
artifacts. It does not normalize retired authorities, compute overlap results,
open Barrier A, enumerate a state space, classify a target, construct or solve a
CTMC, run DES, inspect quantitative output, or change a scientific verdict.

## Authority and baseline lock

- Remote authority worktree:
  `D:\worktree\IMS_deadlock-g6b-spec-final-review`.
- Publication branch:
  `codex/g6b-case-target-certification-final-review`.
- Schema-contract remediation baseline:
  `b2f2f285a68793ce9ca4cb1b47a05dd7a3cfb9bb`.
- Approved design:
  `docs/superpowers/specs/2026-08-01-g6b-case-target-certification-design.md`.
- Approved design SHA-256:
  `b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6`.
- Frozen row-family matrix raw SHA-256:
  `487d81aa79a7bca681db81f19a4d6bd315668c43b1c4538c47f01f099d8e205f`.
- Final schema-review subject:
  `948ff5746adcb66b68fb9c47e519f070dd2c96ba`.
- Runtime:
  `D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe`
  with `PYTHONPATH` bound to the locked implementation worktree `src`.

Before every implementation task, re-lock path, branch, HEAD, upstream,
worktree identity, dirty state, approved-design digest, and frozen-matrix
digest. A mismatch is a stop condition, not an invitation to repair history.

After exact plan approval, create one isolated implementation target from the
approved plan-publication commit:

- worktree: `D:\worktree\IMS_deadlock-g6b-case-construction`;
- branch: `codex/g6b-case-construction`;
- base: the exact commit containing the approved plan and final plan-review
  artifact;
- initial state: clean, with `HEAD^{tree}` recorded before any edit.

All Task 1-7 edits and validation commands run in that implementation worktree.
The final-review worktree remains the publication baseline and must not be used
as a second mutable source tree. If the requested implementation path or branch
already exists with a different identity or dirty state, stop and resolve the
identity conflict without deleting, resetting, or overwriting it.

## Approval semantics

Approval must name this plan's exact SHA-256 and its review artifact SHA-256.
General instructions to continue the project do not approve changed plan bytes.
Approval of this plan permits only the tasks and paths listed here. It does not
itself set any capability to true. A separate machine-valid
`case_construction` authorization record must still be created and validated
before the first case-instance byte is written.

The canonical current capability object remains unchanged throughout the
tranche:

```text
case_construction_authorized=false
retired_authority_fingerprint_normalization_authorized=false
target_certification_preflight_authorized=false
quantitative_execution_authorized=false
```

The construction authorization is an immutable scoped instance artifact. It
does not rewrite the schema bundle's canonical false values.

## Non-negotiable boundaries

- Preserve the top-level exact-five and nested exact-twelve schema-governance
  architecture. A separately reviewed schema corrigendum may change exact
  schema bytes but may not add a thirteenth nested schema-governance file.
- Do not modify the approved 2026-08-01 design bytes. Bind any correction in a
  new, separately hashed corrigendum.
- Do not read outcome-bearing retired G4, G5, or G6-R payloads while designing
  or materializing new inputs. Only approved data-only normalization may later
  read the declared selectors.
- Do not copy, rename, parameter-shift, or graph-isomorphically reproduce a
  retired case. Code-level semantic primitives may be reused, but every reuse
  must be declared in the lineage record and cannot establish independence.
- Do not create `evidence/g6b/target_certification` or materialize anything
  under `artifacts/g6b/quantitative`.
- Output-root reservations are inert repo-relative strings with
  `reserved=true` and `materialized=false`; their directories remain absent.
- Every refused, failed, superseded, or partially written attempt is retained
  in append-only accounting. No favorable-subset deletion is allowed.
- Exact and DES observations are two methods on one case unit, not two
  independent cases.

## Task 0 blocker: resolve the scoped `estimand_id` contradiction

The current approved schema requires `estimand_id` in both sealed directional
hypotheses and metric entries, while `recursive_prohibited_fields` and
`prohibited_instance_fields` also prohibit `estimand_id`. Literal enforcement
makes valid construction payloads impossible. This must be repaired before any
construction authorization can validate.

The approved repair is a narrow scope exception, not deletion of the
predeclared estimand identity and not permission for runtime/result-bearing
estimand fields:

- allow `/directional_hypotheses/*/estimand_id` only in the
  `sealed_prediction_sha256` comparison payload;
- allow `/metric_entries/*/estimand_id` only in the
  `metric_schema_sha256` comparison payload;
- require both values to be canonical, schema-enumerated G6-B estimand IDs;
- continue rejecting `estimand_id` at every other construction-instance path;
- continue rejecting runtime-derived hashes, observations, execution results,
  and quantitative authorization fields at every construction-instance path.

Implement the repair as an explicit versioned construction-schema contract.
Keep the original design immutable and add:

- `docs/superpowers/specs/2026-08-02-g6b-case-construction-estimand-scope-corrigendum.md`;
- `ims-deadlock/g6b-case-construction-schema/v2` in
  `case_construction_schema.json`;
- `ims-deadlock/g6b-row-family-identity/v3` in `identity_schema.json`;
- `ims-deadlock/g6b-retired-authority-fingerprint-schema/v2` in
  `retired_authority_fingerprint_schema.json`;
- the same exact `estimand_id_scope_contract` object in all three files;
- canonical/self-hash and manifest reference updates required by those exact
  bytes;
- validator tests proving the two exact allowed paths and fail-closed rejection
  for root, sibling, nested-result, runtime, certificate, and arbitrary paths.

The synchronized contract object is exactly:

```json
{
  "additional_allowed_paths": false,
  "allowed_predeclared_paths": [
    {
      "allowed_use": "predeclared_directional_hypothesis_identifier_only",
      "json_pointer_pattern": "/directional_hypotheses/*/estimand_id",
      "projection_role": "sealed_prediction_sha256"
    },
    {
      "allowed_use": "predeclared_metric_identifier_only",
      "json_pointer_pattern": "/metric_entries/*/estimand_id",
      "projection_role": "metric_schema_sha256"
    }
  ],
  "allowed_value_codes": [
    "g6b_estimand_theta_global_before_success_v1",
    "g6b_estimand_theta_local_before_success_v1",
    "g6b_estimand_theta_selected_bad_before_success_v1"
  ],
  "default_policy": "recursive_prohibition",
  "runtime_certificate_observation_or_result_use": "prohibited"
}
```

This correction remains schema/governance work. It creates no case and opens no
capability.

## Exact construction roster

Bundle ID: `g6b_discovery_case_construction_v1`.

The roster has exactly 13 case units, 26 method observations, and 13
exact/DES companion groups. The seven mandatory controls are one case each.
Six additional cases combine the uncovered design axes so that no extra case
is created merely to repeat an already covered axis.

| # | Case unit ID | Family ID | Input mode | Frozen role and expected boundary |
| --- | --- | --- | --- | --- |
| 1 | `g6b_cu_nc_local_bypass_completes_v1` | `local_bypass_completion_family` | `explicit_finite_lts_input` | Mandatory `NC_LOCAL_BYPASS_COMPLETES`; a declared local candidate has a reachable completion bypass and must be refused as `reachable_completion_bypass`. |
| 2 | `g6b_cu_nc_unselected_livelock_v1` | `unselected_livelock_family` | `explicit_finite_lts_input` | Mandatory `NC_UNSELECTED_LIVELOCK`; a reachable closed recurrent class is retained as `R_livelock`, not selected bad. |
| 3 | `g6b_cu_nc_calendar_empty_terminal_v1` | `calendar_empty_terminal_family` | `explicit_finite_lts_input` | Mandatory `NC_CALENDAR_EMPTY_TERMINAL`; an empty-calendar non-resource terminal is `R_terminal`, not resource deadlock. |
| 4 | `g6b_cu_nc_policy_only_stall_v1` | `policy_only_stall_family` | `explicit_finite_lts_input` | Mandatory `NC_POLICY_ONLY_STALL`; a policy-only stall is `P_policy` and does not alter the plant partition. |
| 5 | `g6b_cu_nc_or_of_and_feasible_branch_v1` | `or_of_and_feasible_branch_family` | `model_generated_lts` | Mandatory `NC_OR_OF_AND_FEASIBLE_BRANCH`; one OR branch remains feasible, so the local candidate is not admitted. |
| 6 | `g6b_cu_nc_agv_reservation_boundary_v1` | `agv_reservation_boundary_family` | `model_generated_lts` | Mandatory `NC_AGV_RESERVATION_BOUNDARY`; changed AGV/reservation semantics require refusal or a new versioned target. |
| 7 | `g6b_cu_nc_dglobal_only_with_dlocal_v1` | `dglobal_with_local_core_family` | `model_generated_lts` | Mandatory `NC_DGLOBAL_ONLY_WITH_DLOCAL`; a global deadlock containing a local core is counted once as `D_global`. It tests the no-double-count guard only and is not the separate `D_global`-only positive. |
| 8 | `g6b_cu_pc_dglobal_only_v1` | `dglobal_only_positive_family` | `model_generated_lts` | Distinct positive with the selected plant state in `D_global`, no admitted `D_local` subject, and no completion branch; this alone covers the handoff's `D_global`-only positive axis. |
| 9 | `g6b_cu_pc_dlocal_a2b_single_kernel_v1` | `dlocal_a2b_single_kernel_positive_family` | `model_generated_lts` | Request-closed local-first-hit positive with one minimal matching CRP kernel, an exterior event, and an A2b proof; the exterior event must not restore completion. |
| 10 | `g6b_cu_pc_dlocal_lts_multi_kernel_v1` | `dlocal_complete_lts_multi_kernel_positive_family` | `explicit_finite_lts_input` | Complete finite-LTS local-first-hit positive with multiple minimal matching kernels and no path to `F`; exercises the second admission route. |
| 11 | `g6b_cu_bc_crp_zero_kernel_v1` | `crp_zero_matching_kernel_boundary_family` | `model_generated_lts` | Zero matching CRP kernel; the bridge is inapplicable and cannot borrow a global certificate. |
| 12 | `g6b_cu_bc_multi_capacity_residual_v1` | `multi_capacity_residual_boundary_family` | `model_generated_lts` | Residual capacity changes a simple-cycle predicate while the versioned capacity witness remains the authority. |
| 13 | `g6b_cu_pc_medium_independent_island_v1` | `medium_independent_island_family` | `model_generated_lts` | Fresh `four_cell_dual_agv_crossroute_v1` island with four workcell roles, three finite-buffer roles, two AGV/reservation roles, and four routes including one bypass; it is a bounded applicability probe, not a generality claim. |

Case recipes must use canonical semantic roles rather than retired case labels.
Cases 1-4 and 10 are hand-authored finite LTS inputs. Cases 5-9 and 11-13 use
fresh, declarative plant/state inputs that are later eligible for bounded LTS
generation only under Barrier A. Construction must not call that generator.

Cases 1-12 use declared `state_bound=512`. Case 13 uses declared
`state_bound=100000`. These are preflight refusal ceilings, not promises
about reachable-state counts. Exceeding a ceiling produces a later structured
refusal; it never authorizes truncation or a larger unreviewed run.

## Exact recipe registry

The recipe registry below is normative. The materializer stores it as immutable
Python data and its tests snapshot the canonical JSON bytes. No worker may add a
resource, state, transition, route, parameter, rate, policy rule, target label,
control, hypothesis, or falsifier not listed here.

R01-R13 map one-to-one, in order, to roster rows 1-13. The code shown in each
R-heading is that case's exact `source_template_id`; no case may select a second
template or share another row's template ID.

All semantic tokens in this section belong to the versioned immutable
`g6b_case_recipe_code_registry_v1` constant in the materializer. Its canonical
hash is included in every case-content and parameter projection. Unknown aliases
and synonyms refuse; they cannot be used to manufacture hash distinctness.

Tuple grammar is exact:

- resource: `role:kind:capacity`;
- hold: `job:resource:amount`;
- request: `job:[[resource:amount,...], ...]`, where the outer list is OR and
  each inner list is AND;
- route: `route:[ordered_stage_roles]`;
- model transition:
  `role:event_kind:source_mode:target_mode:[acquire]:[release]`;
- explicit-LTS transition: `source:event_kind:target`.

Arrays are sorted by canonical JSON except route stage order and each AND-demand
order, which are scientific and preserved exactly as written. Capacity
parameters are generated as `capacity_<resource-role>`. Every recipe also has
`state_bound`, `recipe_version=<source_template_id>`, and
`input_semantics_version=ims-deadlock/g6b-case-input-semantics/v1` in its
parameter projection. There are no implicit scientific defaults beyond the
common constants below.

Common constants for all cases except an explicit override are:

```text
state_payload_schema_version = ims-deadlock/g6b-state-snapshot-payload/v1
route_semantics_version = ims-deadlock/g6b-route-semantics/v1
parameter_semantics_version = ims-deadlock/g6b-parameter-semantics/v1
rate_units = events_per_time_unit
canonical_rate(each declared event role) = "1"
rate_source_code = plan_constant_rate_v1
policy.mode = plant_unfiltered
policy.excluded_plant_arc_roles = []
policy.filter_rule_code = identity_filter_v1
target_schema_version = ims-deadlock/g6-terminal-stopping-partition/v3
selected_bad_classes = [D_global, D_local]
success_class = F
exact_stopping_rule = first_hit_D_global_or_D_local_or_F_v1
des_stopping_rule = first_hit_D_global_or_D_local_or_F_or_censor_budget_v1
policy_analysis_class = P_policy
```

### R01 `g6b_recipe_nc_local_bypass_completes_v1`

```text
resources = [r_hold:buffer:1, r_req:machine:1]
routes = [route_job_a:[r_hold,r_req,bypass,complete]]
model_transitions = [
  t_bypass:release:waiting:bypassed:[]:[r_hold:1],
  t_complete:complete:bypassed:complete:[]:[]
]
states = [f_complete,s_bypass,s_local_candidate]
initial_state = s_local_candidate
marked_states = [f_complete]
transitions = [
  s_bypass:t_complete:f_complete,
  s_local_candidate:t_bypass:s_bypass
]
```

### R02 `g6b_recipe_nc_unselected_livelock_v1`

```text
resources = [r_loop:machine:1]
routes = [route_job_a:[loop_a,loop_b]]
model_transitions = [
  t_loop_ab:move:loop_a:loop_b:[]:[],
  t_loop_ba:move:loop_b:loop_a:[]:[]
]
states = [f_complete,r_livelock_a,r_livelock_b]
initial_state = r_livelock_a
marked_states = [f_complete]
transitions = [
  r_livelock_a:t_loop_ab:r_livelock_b,
  r_livelock_b:t_loop_ba:r_livelock_a
]
```

### R03 `g6b_recipe_nc_calendar_empty_terminal_v1`

```text
resources = [r_idle:machine:1]
routes = [route_job_a:[terminal]]
model_transitions = []
states = [f_complete,r_terminal]
initial_state = r_terminal
marked_states = [f_complete]
transitions = []
```

### R04 `g6b_recipe_nc_policy_only_stall_v1`

```text
resources = [r_machine:machine:1]
routes = [route_job_a:[processing,complete]]
model_transitions = [t_plant_complete:complete:processing:complete:[]:[r_machine:1]]
states = [f_complete,p_policy_stall]
initial_state = p_policy_stall
marked_states = [f_complete]
transitions = [p_policy_stall:t_plant_complete:f_complete]
policy.mode = analysis_overlay_only
policy.excluded_plant_arc_roles = [t_plant_complete]
policy.filter_rule_code = policy_overlay_does_not_change_plant_partition_v1
```

### R05 `g6b_recipe_nc_or_of_and_feasible_branch_v1`

```text
resources = [r_block_a:buffer:1, r_block_b:machine:1, r_free:buffer:1]
routes = [
  route_job_a:[waiting,branch_blocked,branch_free,complete],
  route_job_b:[hold_a],
  route_job_c:[hold_b]
]
model_transitions = [
  t_take_blocked:request:waiting:branch_blocked:[r_block_a:1,r_block_b:1]:[],
  t_take_free:request:waiting:branch_free:[r_free:1]:[],
  t_free_complete:complete:branch_free:complete:[]:[r_free:1]
]
stable = true
complete = false
event_calendar_empty = false
holds = [job_b:r_block_a:1, job_c:r_block_b:1]
requests = [job_a:[[r_block_a:1,r_block_b:1],[r_free:1]]]
mode_by_job = [job_a:waiting, job_b:holding, job_c:holding]
stage_by_job = [job_a:waiting, job_b:hold_a, job_c:hold_b]
```

### R06 `g6b_recipe_nc_agv_reservation_boundary_v1`

```text
resources = [agv_a:agv:1, destination_slot:reservation:1, machine_a:machine:1]
routes = [route_job_a:[machine_a,agv_a,destination_slot,complete]]
model_transitions = [
  t_preclaim_destination:reserve:on_machine:reserved:[destination_slot:1]:[],
  t_load_agv:transport:reserved:on_agv:[agv_a:1]:[machine_a:1],
  t_arrive:transport:on_agv:complete:[]:[agv_a:1,destination_slot:1]
]
stable = true
complete = false
event_calendar_empty = false
holds = [job_a:agv_a:1, job_b:destination_slot:1]
requests = [job_a:[[destination_slot:1]]]
mode_by_job = [job_a:reserved_wait, job_b:holding]
stage_by_job = [job_a:destination_claim, job_b:destination_occupied]
parameter override = reservation_semantics:enum:preclaim_destination_v1
target_schema_version override = ims-deadlock/g6-terminal-stopping-partition-agv-release-on-arrival/v1
```

### R07 `g6b_recipe_nc_dglobal_only_with_dlocal_v1`

```text
resources = [r_a:buffer:1, r_b:buffer:1, r_c:machine:1]
routes = [route_j1:[r_a,r_b], route_j2:[r_b,r_a], route_j3:[r_c,r_a]]
model_transitions = [
  t_j1_request:request:hold_a:wait_b:[r_b:1]:[],
  t_j2_request:request:hold_b:wait_a:[r_a:1]:[],
  t_j3_request:request:hold_c:wait_a:[r_a:1]:[]
]
stable = true
complete = false
event_calendar_empty = true
holds = [j1:r_a:1, j2:r_b:1, j3:r_c:1]
requests = [j1:[[r_b:1]], j2:[[r_a:1]], j3:[[r_a:1]]]
mode_by_job = [j1:waiting, j2:waiting, j3:waiting]
stage_by_job = [j1:wait_b, j2:wait_a, j3:wait_a]
```

### R08 `g6b_recipe_pc_dglobal_only_v1`

```text
resources = [r_a:buffer:1, r_b:machine:1, r_c:reservation:1]
routes = [route_j1:[r_a,r_b], route_j2:[r_b,r_c], route_j3:[r_c,r_a]]
model_transitions = [
  t_j1_request:request:hold_a:wait_b:[r_b:1]:[],
  t_j2_request:request:hold_b:wait_c:[r_c:1]:[],
  t_j3_request:request:hold_c:wait_a:[r_a:1]:[]
]
stable = true
complete = false
event_calendar_empty = true
holds = [j1:r_a:1, j2:r_b:1, j3:r_c:1]
requests = [j1:[[r_b:1]], j2:[[r_c:1]], j3:[[r_a:1]]]
mode_by_job = [j1:waiting, j2:waiting, j3:waiting]
stage_by_job = [j1:wait_b, j2:wait_c, j3:wait_a]
```

### R09 `g6b_recipe_pc_dlocal_a2b_single_kernel_v1`

```text
resources = [r_local_a:buffer:1, r_local_b:machine:1, r_outer:machine:1]
routes = [
  route_j1:[r_local_a,r_local_b],
  route_j2:[r_local_b,r_local_a],
  route_j3:[outer_tick]
]
model_transitions = [
  t_j1_request:request:hold_a:wait_b:[r_local_b:1]:[],
  t_j2_request:request:hold_b:wait_a:[r_local_a:1]:[],
  t_outer_tick:move:outer_ready:outer_ready:[]:[]
]
stable = true
complete = false
event_calendar_empty = false
holds = [j1:r_local_a:1, j2:r_local_b:1]
requests = [j1:[[r_local_b:1]], j2:[[r_local_a:1]]]
mode_by_job = [j1:waiting, j2:waiting, j3:outer_ready]
stage_by_job = [j1:wait_b, j2:wait_a, j3:outer_tick]
parameter override = dlocal_admission_route:enum:A2b_proof
```

### R10 `g6b_recipe_pc_dlocal_lts_multi_kernel_v1`

```text
resources = [r_a:buffer:1, r_b:machine:1, r_c:buffer:1, r_d:machine:1]
routes = [
  route_j1:[r_a,r_b], route_j2:[r_b,r_a],
  route_j3:[r_c,r_d], route_j4:[r_d,r_c]
]
model_transitions = [
  t_hit_ab:request:s_initial:dlocal_ab:[r_b:1]:[],
  t_hit_cd:request:s_initial:dlocal_cd:[r_d:1]:[],
  t_post_ab:move:dlocal_ab:post_hit:[]:[],
  t_post_cd:move:dlocal_cd:post_hit:[]:[],
  t_return_ab:move:post_hit:dlocal_ab:[]:[],
  t_return_cd:move:post_hit:dlocal_cd:[]:[]
]
states = [dlocal_ab,dlocal_cd,f_complete,post_hit,s_initial]
initial_state = s_initial
marked_states = [f_complete]
transitions = [
  dlocal_ab:t_post_ab:post_hit,
  dlocal_cd:t_post_cd:post_hit,
  post_hit:t_return_ab:dlocal_ab,
  post_hit:t_return_cd:dlocal_cd,
  s_initial:t_hit_ab:dlocal_ab,
  s_initial:t_hit_cd:dlocal_cd
]
parameter override = dlocal_admission_route:enum:complete_LTS_completion_nonreachability_audit
```

### R11 `g6b_recipe_bc_crp_zero_kernel_v1`

```text
resources = [r_a:buffer:1, r_b:machine:1, r_res:reservation:1]
routes = [route_j1:[r_a,and_request], route_j2:[r_b,r_a]]
model_transitions = [
  t_j1_and_request:request:hold_a:wait_and:[r_b:1,r_res:1]:[],
  t_j2_request:request:hold_b:wait_a:[r_a:1]:[]
]
stable = true
complete = false
event_calendar_empty = true
holds = [j1:r_a:1, j2:r_b:1]
requests = [j1:[[r_b:1,r_res:1]], j2:[[r_a:1]]]
mode_by_job = [j1:waiting, j2:waiting]
stage_by_job = [j1:wait_and, j2:wait_a]
parameter override = declared_crp_family:enum:S4PR_single_resource_request_only_v1
```

### R12 `g6b_recipe_bc_multi_capacity_residual_v1`

```text
resources = [r_a:machine:1, r_shared:buffer:2]
routes = [route_j1:[r_a,r_shared], route_j2:[r_shared,r_a]]
model_transitions = [
  t_j1_request:request:hold_a:wait_shared:[r_shared:1]:[],
  t_j2_request:request:hold_shared:wait_a:[r_a:1]:[]
]
stable = true
complete = false
event_calendar_empty = false
holds = [j1:r_a:1, j2:r_shared:1]
requests = [j1:[[r_shared:1]], j2:[[r_a:1]]]
mode_by_job = [j1:waiting, j2:waiting]
stage_by_job = [j1:wait_shared, j2:wait_a]
parameter override = simple_cycle_diagnostic_only:boolean:true
```

### R13 `g6b_recipe_pc_medium_independent_island_v1`

```text
resources = [
  agv_x:agv:1, agv_y:agv:1,
  buffer_ab:buffer:2, buffer_bc:buffer:3, buffer_cd:buffer:2,
  cell_a:machine:1, cell_b:machine:1, cell_c:machine:1, cell_d:machine:1
]
routes = [
  route_alpha:[cell_a,buffer_ab,cell_b,buffer_bc,cell_c],
  route_beta:[cell_c,buffer_cd,cell_d,buffer_ab,cell_a],
  route_delta_bypass:[cell_d,agv_y,cell_a],
  route_gamma:[cell_b,agv_x,cell_d]
]
model_transitions = [
  t_alpha_ab:transfer:cell_a:buffer_ab:[buffer_ab:1]:[cell_a:1],
  t_alpha_b:transfer:buffer_ab:cell_b:[cell_b:1]:[buffer_ab:1],
  t_alpha_bc:transfer:cell_b:buffer_bc:[buffer_bc:1]:[cell_b:1],
  t_alpha_c:transfer:buffer_bc:cell_c:[cell_c:1]:[buffer_bc:1],
  t_beta_cd:transfer:cell_c:buffer_cd:[buffer_cd:1]:[cell_c:1],
  t_beta_d:transfer:buffer_cd:cell_d:[cell_d:1]:[buffer_cd:1],
  t_beta_ab:transfer:cell_d:buffer_ab:[buffer_ab:1]:[cell_d:1],
  t_beta_a:transfer:buffer_ab:cell_a:[cell_a:1]:[buffer_ab:1],
  t_gamma_load:reserve:cell_b:agv_x:[agv_x:1]:[],
  t_gamma_unload:transfer:agv_x:cell_d:[cell_d:1]:[agv_x:1,cell_b:1],
  t_delta_load:reserve:cell_d:agv_y:[agv_y:1]:[],
  t_delta_unload:transfer:agv_y:cell_a:[cell_a:1]:[agv_y:1,cell_d:1]
]
stable = true
complete = false
event_calendar_empty = false
holds = [
  job_alpha:cell_a:1, job_beta:cell_c:1,
  job_delta:agv_y:1, job_gamma:agv_x:1
]
requests = [
  job_alpha:[[buffer_ab:1]], job_beta:[[buffer_cd:1]],
  job_delta:[[cell_a:1]], job_gamma:[[cell_d:1]]
]
mode_by_job = [
  job_alpha:waiting, job_beta:waiting, job_delta:reserved_wait, job_gamma:reserved_wait
]
stage_by_job = [
  job_alpha:buffer_ab, job_beta:buffer_cd, job_delta:cell_a, job_gamma:cell_d
]
parameter overrides = [
  route_alpha_wip:integer:2, route_beta_wip:integer:3,
  route_delta_bypass_wip:integer:1, route_gamma_wip:integer:2,
  reservation_semantics:enum:preclaim_destination_v1
]
```

R13 is deliberately not the retired G4 three-island recipe: it uses four
workcells, three unequal buffer capacities, two AGV resources, four different
routes, and different role labels. These declared differences do not prove
non-isomorphism; later normalization and semantic-lineage audit must still
decide that question.

The exact control/prediction registry is:

| Recipe | Control ID or null | Expected classification/refusal | Exact falsifier codes |
| --- | --- | --- | --- |
| R01 | `NC_LOCAL_BYPASS_COMPLETES` | `D_local_not_admitted` / `reachable_completion_bypass` | `violated_A2b_premise`, `reachable_completion_bypass`, `proof_check_failure` |
| R02 | `NC_UNSELECTED_LIVELOCK` | `R_livelock` / `not_selected_bad_class` | `selected_as_D_global`, `selected_as_D_local`, `missing_closed_recurrent_class` |
| R03 | `NC_CALENDAR_EMPTY_TERMINAL` | `R_terminal` / `not_resource_deadlock` | `selected_as_D_global`, `selected_as_D_local`, `resource_wait_cycle_present` |
| R04 | `NC_POLICY_ONLY_STALL` | `P_policy` / `policy_only_not_plant_partition` | `plant_partition_changed_by_policy`, `plant_completion_path_missing` |
| R05 | `NC_OR_OF_AND_FEASIBLE_BRANCH` | `D_local_not_admitted` / `feasible_branch_exists` | `all_request_alternatives_blocked`, `feasible_branch_ignored` |
| R06 | `NC_AGV_RESERVATION_BOUNDARY` | `boundary_or_new_versioned_target_required` / `semantic_boundary_changed` | `reservation_semantics_silently_coerced`, `target_version_not_changed` |
| R07 | `NC_DGLOBAL_ONLY_WITH_DLOCAL` | `D_global` / `no_double_count_through_D_local` | `counted_in_both_D_global_and_D_local`, `global_deadlock_not_recognized` |
| R08 | null | `D_global` | `path_to_F`, `classified_only_as_D_local`, `global_deadlock_not_recognized` |
| R09 | null | `D_local` via `A2b_proof` | `violated_A2b_premise`, `reachable_completion_bypass`, `proof_check_failure` |
| R10 | null | `D_local` via complete-LTS audit | `path_to_F`, `truncation`, `unavailable_transition_branch`, `incomplete_state_registry` |
| R11 | null | `CRP_bridge_inapplicable` | `matching_local_kernel_found`, `global_certificate_borrowed`, `unclassified_scientific_input` |
| R12 | null | `simple_cycle_not_sufficient_with_residual_capacity` | `residual_capacity_zero`, `capacity_witness_failure`, `simple_cycle_treated_as_deadlock` |
| R13 | null | `bounded_target_certifiable_or_structured_refusal` | `state_bound_exceeded`, `unavailable_transition_branch`, `target_identity_mismatch`, `non_almost_sure_global_domain` |

For each row, the sealed directional-hypothesis statement is generated from
the exact template: `Under <recipe-id>, the expected discovery-only boundary is
<expected-classification/refusal>; any listed falsifier retains the case and
prevents claim upgrade.` It uses all three frozen estimand IDs, direction code
`case_specific_predeclared`, scope code `single_case_discovery_only`, and the
listed falsifier roles. No observed value is permitted in the registry.

Control declarations are deterministic. R01-R07 set
`mandatory_control_roles=[<control-id>]`,
`expected_guard_codes=[<classification>,<refusal>]`, and
`failure_effect_codes=[block_quantitative_authorization,no_claim_upgrade,retain_control_failure]`.
R08-R13 set `mandatory_control_roles=[]`, `expected_guard_codes=[]`, and
`failure_effect_codes=[no_claim_upgrade,retain_mismatch]`.

Every sealed prediction uses:

```text
scoring_rule_id = g6b_case_prediction_decision_table_v1
required_input_roles = [target_certification_case_result]
failure_handling_code = retain_refusal_or_mismatch_no_support_v1
claim_boundary.study_role = discovery_only
claim_boundary.confirmation_use = prohibited
claim_boundary.estimand_scope_code = single_sealed_case_v1
claim_boundary.population_scope_code = exact_13_case_roster_no_generalization_v1
claim_boundary.forbidden_upgrade_codes = [
  confirmation_claim,
  full_tranche_support_from_survivors,
  general_ims_claim,
  publication_ready_claim
]
```

The decision table has four exact rows: expected certified classification gives
`consistent_with_prediction_not_confirmation`; expected boundary refusal gives
`expected_boundary_retained`; a certified mismatch gives
`falsified_or_definition_limited`; and truncation, missing input, unexpected
refusal, or incomplete batch gives `not_evaluable_retained`. The decision-table
hash is computed from those four canonical rows before any case root is
created.

Every semantic-lineage declaration sets
`constructor_role=post_approval_first_principles_materializer`,
`visible_retired_authority_ids=[G4,G5,G6_R]`,
`declared_source_template_ids=[<recipe-id>]`,
`declared_source_artifact_hashes=[approved_plan_hash,materializer_source_hash]`,
`declared_semantic_parent_ids=[]`,
`declared_transform_codes=[canonical_role_projection_v1,from_first_principles_recipe_v1]`,
`graph_isomorphism_check_required=true`, and
`outcome_driven_tuning_prohibited=true`. The construction log and review hashes
are finalized upstream before the lineage self hash. No retired data artifact
may appear as a source template or semantic parent.

The exact method/group roster is:

| Case stem | Exact method observation | DES method observation | Companion group |
| --- | --- | --- | --- |
| `nc_local_bypass_completes` | `g6b_mo_nc_local_bypass_completes_exact_v1` | `g6b_mo_nc_local_bypass_completes_des_v1` | `g6b_mcg_nc_local_bypass_completes_v1` |
| `nc_unselected_livelock` | `g6b_mo_nc_unselected_livelock_exact_v1` | `g6b_mo_nc_unselected_livelock_des_v1` | `g6b_mcg_nc_unselected_livelock_v1` |
| `nc_calendar_empty_terminal` | `g6b_mo_nc_calendar_empty_terminal_exact_v1` | `g6b_mo_nc_calendar_empty_terminal_des_v1` | `g6b_mcg_nc_calendar_empty_terminal_v1` |
| `nc_policy_only_stall` | `g6b_mo_nc_policy_only_stall_exact_v1` | `g6b_mo_nc_policy_only_stall_des_v1` | `g6b_mcg_nc_policy_only_stall_v1` |
| `nc_or_of_and_feasible_branch` | `g6b_mo_nc_or_of_and_feasible_branch_exact_v1` | `g6b_mo_nc_or_of_and_feasible_branch_des_v1` | `g6b_mcg_nc_or_of_and_feasible_branch_v1` |
| `nc_agv_reservation_boundary` | `g6b_mo_nc_agv_reservation_boundary_exact_v1` | `g6b_mo_nc_agv_reservation_boundary_des_v1` | `g6b_mcg_nc_agv_reservation_boundary_v1` |
| `nc_dglobal_only_with_dlocal` | `g6b_mo_nc_dglobal_only_with_dlocal_exact_v1` | `g6b_mo_nc_dglobal_only_with_dlocal_des_v1` | `g6b_mcg_nc_dglobal_only_with_dlocal_v1` |
| `pc_dglobal_only` | `g6b_mo_pc_dglobal_only_exact_v1` | `g6b_mo_pc_dglobal_only_des_v1` | `g6b_mcg_pc_dglobal_only_v1` |
| `pc_dlocal_a2b_single_kernel` | `g6b_mo_pc_dlocal_a2b_single_kernel_exact_v1` | `g6b_mo_pc_dlocal_a2b_single_kernel_des_v1` | `g6b_mcg_pc_dlocal_a2b_single_kernel_v1` |
| `pc_dlocal_lts_multi_kernel` | `g6b_mo_pc_dlocal_lts_multi_kernel_exact_v1` | `g6b_mo_pc_dlocal_lts_multi_kernel_des_v1` | `g6b_mcg_pc_dlocal_lts_multi_kernel_v1` |
| `bc_crp_zero_kernel` | `g6b_mo_bc_crp_zero_kernel_exact_v1` | `g6b_mo_bc_crp_zero_kernel_des_v1` | `g6b_mcg_bc_crp_zero_kernel_v1` |
| `bc_multi_capacity_residual` | `g6b_mo_bc_multi_capacity_residual_exact_v1` | `g6b_mo_bc_multi_capacity_residual_des_v1` | `g6b_mcg_bc_multi_capacity_residual_v1` |
| `pc_medium_independent_island` | `g6b_mo_pc_medium_independent_island_exact_v1` | `g6b_mo_pc_medium_independent_island_des_v1` | `g6b_mcg_pc_medium_independent_island_v1` |

All thirteen groups set `same_target_required=true`, record one planned shared
selected-target declaration, and count as one case unit with two distinct
method observations. This is a construction-time requirement only; actual
same-target identity is established later by reviewed Barrier-A certificates
and `same_target_lock` artifacts.

## Frozen estimands, predictions, and metric schema

The corrigendum permits only these predeclared estimand IDs during case
construction:

- `g6b_estimand_theta_global_before_success_v1` for
  `theta_G = P(T_D_global < T_F)`;
- `g6b_estimand_theta_local_before_success_v1` for
  `theta_L = P(T_D_local < T_F)`;
- `g6b_estimand_theta_selected_bad_before_success_v1` for the union of the two
  selected bad classes under the disjoint partition.

Every case seals directional hypotheses and falsifiers before any result-bearing
operation. Negative-control cases copy the frozen expected
classification/refusal semantics from `row_family_matrix.json`; they do not
copy an observed outcome. The six additional cases use bounded, case-specific
hypotheses. A mismatch falsifies or limits the corresponding hypothesis and is
retained; it never deletes the case or changes the estimand after inspection.

All thirteen groups intentionally reuse one reviewed metric-schema payload for
exact/DES comparability. It contains exactly three probability metrics, one for
each estimand above. Controlled reuse requires an exact reuse record per group.
The three metric IDs are, respectively,
`g6b_metric_theta_global_before_success_v1`,
`g6b_metric_theta_local_before_success_v1`, and
`g6b_metric_theta_selected_bad_before_success_v1`. Every entry uses
`unit=probability`, `domain=closed_unit_interval`,
`direction=case_specific_predeclared`,
`aggregation_rule_id=g6b_first_hit_probability_by_method_v1`,
`censoring_rule_id=g6b_nonhit_is_censored_v1`,
`failure_rule_id=g6b_refusal_is_non_supporting_v1`,
`scoring_rule_id=g6b_case_prediction_decision_table_v1`, and
`applicability_rule=target_certified_and_same_target_locked_v1`.

The exact rule records freeze:

- aggregation: exact companion uses the certified finite-domain probability;
  DES companion uses the 4096-replicate first-hit Bernoulli estimator; method
  roles may not be pooled as independent cases;
- censoring: no selected hit before the draw budget is censored and reported in
  the original denominator; it is never recoded as success or failure;
- failure: refusal, truncation, missing rate, target mismatch, nonzero exit, and
  incomplete batch are retained non-supporting statuses;
- scoring: use the four-row decision table above, with no completed-case-only
  bundle conclusion;
- comparability scope: exact/DES within one companion group only; cross-case
  equality of metric-schema hashes is controlled reuse, not independence.

Rule-record keys are closed: aggregation has
`aggregation_rule_id,exact_method_rule,des_method_rule,evidence_counting_rule`;
censoring has `censoring_rule_id,censoring_event,denominator_policy`;
failure has `failure_rule_id,retained_status_codes,subset_selection_policy`;
scoring has `scoring_rule_id,decision_table_sha256,claim_upgrade_policy`.
No additional rule key or free-form rule object is permitted.

The metric schema therefore freezes:

- unit `probability`, domain `[0,1]`, and case-specific directional scoring;
- exact aggregation as the certified finite-domain value;
- DES aggregation as a preregistered first-hit Bernoulli estimator;
- non-hit-at-budget as censored, never silently recoded as success or failure;
- refusal, truncation, missing rate, target mismatch, and execution failure as
  retained non-supporting statuses;
- no completed-case-only bundle conclusion;
- no post-outcome metric, rule, horizon, or estimator substitution.

Metric reuse is comparability evidence, not case-independence evidence.

## Random streams and inert output reservations

- Exact methods use a method-specific `not_applicable_by_protocol` stream
  record; no global shared placeholder is permitted.
- DES methods declare `Philox` / `v1`, a sealed root commitment, deterministic
  SHA-256 derivation over the seed root, PRNG version, subject-free
  `case_content_sha256` comparison-projection hash, method role, stream role,
  and replicate index, with disjoint sorted substreams and a frozen replicate
  plan of 4096 replicates indexed
  `[0,4096)`. The per-replication draw budget is
  `min(65536, 16 * declared_state_bound)`, common-random-numbers group is null,
  and antithetic policy is `none`. Construction writes declarations only and
  consumes zero random draws.
- Bundle, case, method, and filename IDs appear only in the provenance/allocation
  envelope. They are excluded from the random-stream comparison projection and
  cannot manufacture distinctness. The exact derivation label is
  `sha256("g6b_des_stream_v1" || seed_root || prng_version ||
  case_content_projection_sha256 || method_role || stream_role ||
  replicate_index)` with length-prefixed UTF-8 fields.
- Each method reserves exactly one `primary` logical output root using
  `artifacts/g6b/quantitative/{bundle_id}/{case_unit_id}/{method_observation_id}/primary/`.
  The path is stored as a repo-relative POSIX string; the directory is not
  created or inspected.

## Candidate-source and independence contract

Every case is constructed from a new post-approval recipe. The lineage record
must declare:

- visible retired authorities exactly `G4`, `G5`, and `G6_R`;
- all code-level semantic primitives and documentation clauses used;
- no retired case-data artifact as a source template;
- no observed retired outcome as an input;
- all canonical-role mappings and deterministic transforms;
- graph-isomorphism review required;
- outcome-driven tuning prohibited.

Generic data types and semantic primitives may be reused from
`src/ims_deadlock/engine.py`, but construction must not import or call
`StableLTS` enumeration in `src/ims_deadlock/analysis.py`. The existing G4
`build_medium_island_case`, `three_island_bas_v1`, `ABG/BAG/AG` route template,
and `G4_MEDIUM_ISLAND_REBUILD.json` are retired-authority evidence, not a G6-B
input template. Case 13 must use the fresh four-cell/two-AGV recipe above and
must later pass graph-isomorphism and eight-dimension overlap review; source
code reuse alone never establishes that pass.

Input-hash inequality is not enough. After construction is sealed, the project
must stop. Retired-authority normalization and the actual eight-dimension
overlap audit are later, separately authorized tasks. Until that audit passes,
no Barrier-A authorization may exist.

## Construction runtime and write scope

The case materializer is a data-only, fail-closed module:

- new module: `src/ims_deadlock/g6b_case_materializer.py`;
- new tests: `tests/test_g6b_case_materializer.py`;
- shared canonical validators remain in
  `src/ims_deadlock/g6b_schema_contracts.py`;
- no import from CTMC, stochastic execution, terminal classification,
  enumeration, G4 instance execution, G5 execution, or G6-R replay modules;
- no network, stdin, subprocess, filesystem discovery, or output inspection;
- maximum wall clock 600 seconds, CPU 600 seconds, memory 2 GiB, workers 1;
- writes only the exact authorized case-unit and governance roots;
- validates a complete in-memory candidate bundle before create-new,
  atomic-per-file writes. A pre-write refusal writes only an append-only ledger
  entry. An interruption after writing begins retains every partial file,
  refuses the whole bundle, and appends the causal ledger entry on recovery;
  files are never deleted or overwritten to simulate a clean attempt.

The materializer must reject a false/missing authorization, identity drift,
source-tree drift, plan/review hash drift, scope widening, unexpected case or
method ID, path escape, existing materialized output root, extra field,
unclassified scientific input, self-hash mismatch, partial manifest, or any
attempt to call a forbidden operation.

The exact governance files are:

```text
governance/g6b_discovery_case_construction_v1/construction_authorization.json
governance/g6b_discovery_case_construction_v1/construction_ledger.json
governance/g6b_discovery_case_construction_v1/construction_log.json
governance/g6b_discovery_case_construction_v1/sealed_bundle_manifest.json
```

Within each authorized `case_units/{case_unit_id}/` root, the exact relative
file layout is:

```text
case_input.json
declarations/control_declaration.json
declarations/policy_declaration.json
declarations/rate_manifest.json
declarations/selected_target_declaration.json
fingerprints/case_content_sha256.json
fingerprints/metric_schema_sha256.json
fingerprints/output_root_reservation_sha256_exact.json
fingerprints/output_root_reservation_sha256_des.json
fingerprints/parameter_tuple_sha256.json
fingerprints/random_stream_manifest_sha256_exact.json
fingerprints/random_stream_manifest_sha256_des.json
fingerprints/route_signature_sha256.json
fingerprints/sealed_prediction_sha256.json
fingerprints/state_snapshot_sha256.json
method_companion_group.json
method_observations/des.json
method_observations/exact.json
metric_schema.json
metric_schema_reuse.json
projections/parameter_tuple.json
projections/route_signature.json
projections/state_snapshot.json
sealed_prediction.json
semantic_lineage_declaration.json
```

No other governance or case-unit file is allowed. A future schema review may
reject this layout; in that event the plan must be revised and reapproved
instead of adding an inferred file.

## Implementation tasks

### Task 1: publish and test the estimand-scope corrigendum

**Files**

- Create:
  `docs/superpowers/specs/2026-08-02-g6b-case-construction-estimand-scope-corrigendum.md`.
- Modify the synchronized construction payload contracts in:
  `cases/discovery/g6b/row_families/structural_discovery_v1/case_construction_schema.json`,
  `identity_schema.json`, and `retired_authority_fingerprint_schema.json`.
- Modify:
  `src/ims_deadlock/g6b_row_family_protocol.py`,
  `src/ims_deadlock/g6b_schema_contracts.py`,
  `tests/test_g6b_row_family_protocol.py`, and
  `tests/test_g6b_schema_contracts.py`.

The exact-twelve bundle file inventory is closed. Task 1 changes the three JSON
contracts named above and the two validators/two tests named above. It updates
the three schema-version constants, exact-key sets, and synchronized
fingerprint-payload equality assertions. The following nine JSON files are
explicitly unchanged and must be byte-identical to the approved baseline:

- `row_family_protocol.json` (its exact artifact-path array and four false
  capabilities remain unchanged);
- `row_family_matrix.json`;
- `reuse_matrix.json`;
- `overlap_report_schema.json`;
- `runtime_lock_schema.json`;
- `review_state.json`;
- `failure_ledger.json`;
- `target_certification_schema.json`;
- `quantitative_authorization_schema.json`.

The corrigendum path and digest are bound by the approved plan, Task-1 review
record, handoff, and construction authorization. They are not inserted as a
thirteenth bundle artifact or by mutating the original design pointer in
`row_family_protocol.json`.

**TDD sequence**

1. Add failing tests for both exact allowed JSON-pointer roles and for
   forbidden sibling/root/result/runtime placements.
2. Run the focused tests and retain the intended RED evidence.
3. Implement v2 validation and synchronized schema/hash changes.
4. Re-run focused tests, exact row-family validation, Ruff, strict mypy, JSON
   duplicate-member parsing, canonical/self-hash checks, and `git diff --check`.
5. Obtain independent ontology, boundary, and code/capability approval for this
   correction before Task 2.

Stop if the repair needs a broader exception, changes the estimand definitions,
or makes the exact-twelve bundle unreviewable.

### Task 2: implement fail-closed construction authorization and materializer

**Files**

- Create `src/ims_deadlock/g6b_case_materializer.py`.
- Create `tests/test_g6b_case_materializer.py`.
- Modify `src/ims_deadlock/g6b_schema_contracts.py` and its focused test file.

**TDD sequence**

1. Add failing tests for the exact authorization field set, explicit
   `authorized is True`, `invalidated_by_identity_drift is False`, exact bundle
   and roster scope, source tree/HEAD, plan/review hashes, ordered allowed and
   forbidden operations, path containment, and self hash.
2. Add negative import/call-graph tests proving the materializer cannot reach
   enumeration, terminal classification, CTMC, DES, retired normalization,
   preflight, or quantitative-output surfaces.
3. Add dry-run tests for both input modes and all thirteen roster IDs.
4. Implement only enough code to make those tests pass.
5. Keep the CLI incapable of running unless the exact authorization artifact
   validates against the reviewed plan and clean source identity.

### Task 3: create the reviewed construction authorization

Create only after exact user approval and after Task 1 review passes:

`cases/discovery/g6b/row_families/structural_discovery_v1/governance/g6b_discovery_case_construction_v1/construction_authorization.json`.

It must bind the approved plan hash, plan-review hash, exact 13 case IDs, exact
26 method IDs, clean source HEAD/tree, closed operation arrays from the schema,
and `invalidated_by_identity_drift=false`. Validate it before any case root is
created. Creating this record does not open normalization, preflight, or
quantitative execution.

### Task 4: materialize sealed case inputs and comparison projections

For each exact case ID, create only the schema-declared artifacts beneath:

`cases/discovery/g6b/row_families/structural_discovery_v1/case_units/{case_unit_id}/`.

Write and validate the case input, state snapshot, route signature, parameter
tuple, rate manifest, policy declaration, selected target declaration, control
declaration, sealed prediction, semantic lineage declaration, and fingerprint
records. Use exact-key validation and canonical JSON. Preserve each failed
attempt in the construction ledger. Do not derive a runtime state-space hash,
partition, target certificate, absorption domain, or result.

### Task 5: materialize methods, companion groups, metrics, and reservations

Create the exact 26 method records and 13 companion groups. Write method-specific
stream manifests, inert output-root reservations, the shared metric schema,
and per-group controlled-reuse records. Validate unique sorted IDs, exact
two-member roles, shared case identity, one metric hash per group, distinct
method-specific provenance, and non-materialization of all reserved roots.

### Task 6: seal the bundle and reconcile all accounting

Create the sealed bundle manifest in the authorized governance root. It must
reconcile exactly:

- 13 planned case IDs;
- 26 planned method IDs;
- 13 companion-group IDs;
- seven mandatory negative-control IDs;
- every case/method/group record hash;
- every prediction, lineage, metric, fingerprint, and reservation hash;
- append-only failure/supersession entries;
- `planned_case_unit_count=13`, `planned_method_count=26`, and
  `planned_companion_group_count=13`.

Any missing or extra ID, duplicate, partial case, unexpected path, or count/hash
mismatch refuses the whole bundle. Do not present a passing subset.

### Task 7: verify, independently review, document, and publish

Run the smallest focused tests first, then the exact G6-B protocol/schema files,
then the full repository suite. Also run Ruff check/format, strict mypy for all
touched source/tests, duplicate-member JSON parsing, canonical/self-hash tests,
`git diff --check`, forbidden-root inventory, and a clean branch/upstream lock.

Three independent reviewers must review the same commit:

1. ontology/estimand reviewer;
2. scientific-boundary and nonreuse reviewer;
3. code/capability and artifact-scope reviewer.

Publish their exact subject, commands, finding counts, and verdicts in
`docs/verification/G6_B_CASE_CONSTRUCTION_REVIEW.md`. Update
`PROJECT_HANDOFF.md` and `ROADMAP.md` with current commit/PR/test evidence and
the unchanged downstream gates. Push a reviewable branch and open a draft PR.
Do not merge without separate authority.

## Verification commands

Use the locked Windows runtime with bytecode and pytest cache disabled. The
focused command set is:

```bat
set PYTHONPATH=D:\worktree\IMS_deadlock-g6b-case-construction\src
set PYTHONDONTWRITEBYTECODE=1
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests\test_g6b_case_materializer.py tests\test_g6b_schema_contracts.py tests\test_g6b_row_family_protocol.py tests\test_g6b_protocol.py
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -m ruff check src\ims_deadlock\g6b_case_materializer.py src\ims_deadlock\g6b_schema_contracts.py tests\test_g6b_case_materializer.py tests\test_g6b_schema_contracts.py tests\test_g6b_row_family_protocol.py tests\test_g6b_protocol.py
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -m ruff format --check src\ims_deadlock\g6b_case_materializer.py src\ims_deadlock\g6b_schema_contracts.py tests\test_g6b_case_materializer.py tests\test_g6b_schema_contracts.py tests\test_g6b_row_family_protocol.py tests\test_g6b_protocol.py
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -m mypy src\ims_deadlock\g6b_case_materializer.py src\ims_deadlock\g6b_schema_contracts.py tests\test_g6b_case_materializer.py tests\test_g6b_schema_contracts.py
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
git diff --check
```

Read every command's result. A historical or pre-change result is not evidence
for the final subject.

## Tranche exit and downstream stop

Success means only:

- the corrigendum is reviewed;
- one exact construction authorization validates;
- the full 13/26/13 sealed construction bundle is complete and hash-valid;
- all negative/failure/supersession accounting is retained;
- all tests and three reviews pass for one exact commit;
- no later root or scientific output exists.

Then stop. The next allowed work is a separately scoped, data-only retired-
authority normalization authorization. Actual overlap, Barrier A target
certification, exact/DES same-target certificates, Barrier B quantitative
execution, G6-B PASS, G6-C/D/E, and paper-gate claims remain unstarted.
