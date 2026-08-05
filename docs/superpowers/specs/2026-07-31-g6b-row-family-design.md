# G6-B Row-Family Discovery-Model Design

Status: `DESIGN SPEC / EXECUTION-DISABLED / NO CASE CREATION`.

This spec is the review target for the user-selected A-route G6-B row-family
discovery-model contract. It is not implementation authority until the written
spec is reviewed and approved. It does not implement the bundle, create cases,
enumerate LTS states, solve CTMC systems, run DES, inspect outputs, authorize
science, or mark G6-B as `PASS`.

## Objective

Create a future nested row-family bundle that can be reviewed before any
scientific execution. The bundle must define identity, reuse, overlap schema,
runtime-lock requirements, controls, scoring placeholders, failure/change
ledger, refusal tests, and review states while preserving:

- `study_role = discovery_only`;
- `confirmation_use = prohibited`;
- `scientific_execution_authorized = false`;
- `adversarial_review_status = PENDING`.

Source anchors:

- `docs/cases/G6_B_DISCOVERY_PROTOCOL.md:5` fixes G6-B as
  protocol-foundation/discovery-only/execution-disabled.
- `docs/cases/G6_B_DISCOVERY_PROTOCOL.md:7` through
  `docs/cases/G6_B_DISCOVERY_PROTOCOL.md:10` prohibit case creation,
  enumeration, CTMC solve, DES run, and science before later authorization.
- `cases/discovery/g6b/protocol.json:28` through
  `cases/discovery/g6b/protocol.json:33` encode the same execution boundary.
- `docs/verification/G6_B_PROTOCOL_FOUNDATION_REVIEW.md:13` through
  `docs/verification/G6_B_PROTOCOL_FOUNDATION_REVIEW.md:16` state that
  `PASS FOUNDATION ONLY` does not pass G6-B and only permits a separate
  row-family plan.

## Non-Goals

- Do not edit the existing five-file bundle under `cases/discovery/g6b/*.json`.
- Do not add any new top-level JSON directly under `cases/discovery/g6b/`.
- Do not create `CaseSpec` files, output roots, snapshots, streams,
  predictions, exact outputs, DES outputs, or science summaries.
- Do not run enumeration, CTMC, DES, or output inspection.
- Do not claim actual overlap, actual runtime lock, G6-B `PASS`, or G6-C/D/E
  progress.
- Do not change `adversarial_review_status` from `PENDING`.

## Current Status

G6-B remains open. `docs/ROADMAP.md:16` records disabled/PENDING status, no
discovery case, no enumeration/CTMC/DES, no new science-output inspection, and
actual overlap report/runtime lock still open. `PROJECT_HANDOFF.md:27` through
`PROJECT_HANDOFF.md:33` records that the foundation review created no science
and cannot upgrade G6-B to pass. `docs/cases/CASE_CHANGE_LEDGER.md:25` records
the execution-disabled protocol and data-only validator with no scientific
execution and no discovery case creation.

## Source-Of-Truth Hierarchy

1. Freshly locked remote authoritative checkout for runtime behavior, branch,
   HEAD, dirty state, upstream state, worktree identity, and validation.
2. Tracked G6-B human protocol and exact-five foundation JSON bundle.
3. G6-B foundation review artifact.
4. G6 theory and terminal-stopping implementation contracts.
5. This design spec.
6. Local `bootstrap_source` snapshot as read-only planning evidence only.

`PROJECT_HANDOFF.md:9` through `PROJECT_HANDOFF.md:10` require a re-locked
remote authority when live Git state matters. `PROJECT_HANDOFF.md:76` through
`PROJECT_HANDOFF.md:81` warn that the local snapshot is not file-byte freeze
authority.

## Ontology Contract

`K_local` is a structural candidate surface. `D_local` is an admitted verified
first-hit bad set. A local candidate enters `D_local` only by one route:

- `A2b_proof`: structural irreversibility under declared finite semantics.
- `complete_LTS_completion_nonreachability_audit`: complete-LTS proof that no
  completion path reaches `F` from the candidate state.

These routes are alternatives, not aliases. A row must cite exactly one
successful route or remain outside `D_local`. `D_local` is not a plant terminal
SCC and may have outgoing plant-LTS arcs; only `R_livelock` and `R_terminal`
are terminal SCC classes of the remaining graph.

Source anchors:

- `docs/theory/G6_LOCAL_FIRST_HIT_AND_STOPPING_THEOREMS.md:41` through
  `docs/theory/G6_LOCAL_FIRST_HIT_AND_STOPPING_THEOREMS.md:47` define
  `K_local`, the two `D_local` routes, and non-terminal `D_local`.
- `docs/theory/G6_LOCAL_FIRST_HIT_AND_STOPPING_THEOREMS.md:55` through
  `docs/theory/G6_LOCAL_FIRST_HIT_AND_STOPPING_THEOREMS.md:56` call terminal
  `D_local` a category error.
- `cases/discovery/g6b/estimand_schema.json:24` through
  `cases/discovery/g6b/estimand_schema.json:30` encode the route split.
- `src/ims_deadlock/terminal_classes.py:97` through
  `src/ims_deadlock/terminal_classes.py:103` encode non-terminal `D_local`.

## File Plan

Keep the current exact-five foundation bundle unchanged:

- existing `cases/discovery/g6b/protocol.json`;
- existing `cases/discovery/g6b/estimand_schema.json`;
- existing `cases/discovery/g6b/independence_schema.json`;
- existing `cases/discovery/g6b/negative_controls.json`;
- existing `cases/discovery/g6b/failure_ledger.json`.

Future implementation may add only a nested bundle under the planned path
`cases/discovery/g6b/row_families/structural_discovery_v1/`. Planned files:

| Planned path | Contract |
| --- | --- |
| `row_family_protocol.json` | Nested bundle index, schema versions, artifact list, disabled execution state. |
| `identity_schema.json` | Family, case-unit, method-observation, and artifact identity rules. |
| `row_family_matrix.json` | Structural row families and mandatory control coverage. |
| `reuse_matrix.json` | Allowed/prohibited reuse across variants and exact/DES companions. |
| `overlap_report_schema.json` | Schema-only overlap-report shape; no actual overlap claim. |
| `runtime_lock_schema.json` | Two later lock types: overlap-authority target lock and execution-runtime lock; no current lock claim. |
| `review_state.json` | Review/authorization state machine, initially non-executing. |
| `failure_ledger.json` | Append-only row-family ledger, initially empty. |

Planned validator: `src/ims_deadlock/g6b_row_family_protocol.py`.
Planned tests: `tests/test_g6b_row_family_protocol.py`.
All paths in this section are planned unless marked existing.

## Identity Hierarchy

The bundle must use three identity levels:

| Level | Meaning | Required fields |
| --- | --- | --- |
| `family_id` | One structural discovery family, not a case. | `family_id`, `family_schema_version`, `ontology_version`, `selected_target_version`, `row_family_role`, `created_by_protocol_version` |
| `case_unit_id` | One planned plant/model input unit; the discovery-case identity unit. | `case_unit_id`, `family_id`, all eight canonical fingerprint records, `structural_family_role`, `negative_control_id_or_null` |
| `method_observation_id` | One method attached to a case unit; not an independent case when paired. | `method_observation_id`, `case_unit_id`, `method_role`, `method_companion_group_id`, `stopping_rule_sha256`, `des_stopping_rule_sha256_or_null`, `runtime_lock_id_or_null`, `output_root_or_null` |

Allowed `method_role` values: `exact_companion`, `des_companion`,
`schema_only_refusal`, `review_only_placeholder`. None authorizes execution.

Each canonical fingerprint record must contain `dimension`,
`applicability_status`, `artifact_role`, and `sha256_or_null`. Schema-only
design files use `sha256_or_null = null`; an actual overlap report cannot pass
until every required dimension has a concrete hash. If a future case unit has
no stochastic observation, its random-stream dimension must hash a
case-unit-specific `no_stochastic_method` provenance manifest with
`applicability_status = not_applicable_by_protocol`. A global shared
not-applicable sentinel is prohibited because it would manufacture or conceal
overlap. The report must state that such a manifest proves provenance only,
not stochastic independence.

## Controlled Reuse Matrix

The bundle must not demand naive zero overlap across all G6-B discovery
variants. Foundation scope is discovery-versus-retired; discovery-internal
reuse is row-family controlled. `docs/cases/G6_B_DISCOVERY_PROTOCOL.md:98`
through `docs/cases/G6_B_DISCOVERY_PROTOCOL.md:101` and
`cases/discovery/g6b/independence_schema.json:55` through
`cases/discovery/g6b/independence_schema.json:60` require that split.

| Relation | Same `case_unit_id` | Shared dimensions allowed | Rule |
| --- | --- | --- | --- |
| `exact_des_companion` | Yes | content, state, route, parameters, target, metric schema | Exact and DES are paired methods, not independent cases. |
| `controlled_family_variant` | No | family id, ontology, metric schema, selected target, explicitly frozen control dimensions | The declared variation axis must differ; every held-fixed dimension and every allowed reuse must be recorded before outputs. |
| `negative_control_pair` | No | family id, ontology, metric schema | Control mechanism must differ and attack a named hypothesis. |
| `method_schema_reuse` | No | metric schema and scoring layers | Allowed only for preregistered outcome-independent comparability. |
| `retired_authority_overlap` | No | none across required dimensions | Any retired G4/G5/G6-R overlap refuses admission. |

Method observations sharing one `case_unit_id` cannot be counted as independent
discovery cases.

## Retired-Authority Overlap

Every future discovery case unit must be zero-overlap against retired
G4/G5/G6-R on exactly eight dimensions:

1. `case_content_sha256`
2. `state_snapshot_sha256`
3. `route_signature_sha256`
4. `parameter_tuple_sha256`
5. `random_stream_manifest_sha256`
6. `output_root`
7. `sealed_prediction_sha256`
8. `metric_schema_sha256`

`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:77` through
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:96` define the rule.
`cases/discovery/g6b/independence_schema.json:18` through
`cases/discovery/g6b/independence_schema.json:27` list the dimensions.
`cases/discovery/g6b/independence_schema.json:34` through
`cases/discovery/g6b/independence_schema.json:53` encode the
discovery-versus-retired scope.

The planned `overlap_report_schema.json` must initially state:

- `report_role = schema_only`;
- `actual_overlap_checked = false`;
- `actual_overlap_report_available = false`;
- `schema_only_overlap_report_cannot_authorize_execution = true`;
- `missing_actual_overlap_report_blocks_execution = true`.

It must define later actual-report fields for locked target identity, retired
authority hashes, discovery case-unit hashes, all eight dimensions, per-unit
results, and refusal entries. It must not claim current overlap evidence.
The two G5 authority files that may be absent from the local snapshot remain
remote-authority-only inputs; the design must not copy them back locally or
treat local absence as evidence of non-overlap.

## Future Confirmation Rule

Future G6 confirmation rows must be independent from retired authorities and
G6-B discovery case identity/provenance on seven dimensions:

1. `case_content_sha256`
2. `state_snapshot_sha256`
3. `route_signature_sha256`
4. `parameter_tuple_sha256`
5. `random_stream_manifest_sha256`
6. `output_root`
7. `sealed_prediction_sha256`

`metric_schema_sha256` reuse is allowed only if explicitly preregistered for
same-target comparability and not derived from inspected outcomes. Source:
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:103` through
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:109` and
`cases/discovery/g6b/independence_schema.json:62` through
`cases/discovery/g6b/independence_schema.json:87`.

## Controls And Structural Families

All seven controls are mandatory before any discovery attempt. Source:
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:127` through
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:149` and
`cases/discovery/g6b/negative_controls.json:6` through
`cases/discovery/g6b/negative_controls.json:49`.

| Control | Planned structural family | Expected result |
| --- | --- | --- |
| `NC_LOCAL_BYPASS_COMPLETES` | `local_bypass_completion_family` | `D_local_not_admitted` for reachable completion bypass. |
| `NC_UNSELECTED_LIVELOCK` | `unselected_livelock_family` | `R_livelock`, not selected bad. |
| `NC_CALENDAR_EMPTY_TERMINAL` | `calendar_empty_terminal_family` | `R_terminal`, not selected bad. |
| `NC_POLICY_ONLY_STALL` | `policy_only_stall_family` | `P_policy`, not plant partition support. |
| `NC_OR_OF_AND_FEASIBLE_BRANCH` | `or_of_and_feasible_branch_family` | Feasible branch blocks `D_local` admission. |
| `NC_AGV_RESERVATION_BOUNDARY` | `agv_reservation_boundary_family` | Boundary or new versioned target required. |
| `NC_DGLOBAL_ONLY_WITH_DLOCAL` | `dglobal_with_local_core_family` | Report `D_global` once; no double count. |

Each family record must include `structural_family_id`,
`required_negative_control_id`, `hypothesis_attacked`, `admission_route_allowed`,
`expected_refusal_or_classification`, `supports_hypothesis_if_failed = false`,
and `case_creation_authorized = false`.

The registry must also define three non-control discovery roles without fixing
their observed outcomes:

| Discovery role | Frozen question | Required falsifier |
| --- | --- | --- |
| `a2b_admission_probe` | Does the declared finite-semantics A2b proof admit the candidate to `D_local`? | Any violated A2b premise, reachable completion bypass, or proof-check failure. |
| `complete_lts_admission_probe` | Does a complete LTS show completion nonreachability from the candidate? | Any path to `F`, truncation, unavailable transition branch, or incomplete state registry. |
| `same_target_exact_des_probe` | Do exact and DES companions evaluate the same frozen target without semantic drift? | Any mismatch in selected labels, versioned target, stopping hashes, or companion identity. |

These roles freeze questions and falsifiers, not favorable classifications or
numeric outcomes. Their later construction requires a separate approved
case-construction plan.

## Outcome-Leakage Prevention

The row-family bundle must freeze target labels, target version, metric schema,
controls, refusal rules, and falsifier references before any output can exist.
Fields derived from exact output, DES output, state enumeration, or observed
metrics are prohibited. `sealed_prediction_sha256` may be only a future
placeholder reference until later preregistration. `output_root` must be absent
or reserved, never created by this bundle.

Failures, missing hashes, overlap hits, target drift, incomplete LTS audits,
failed controls, refused admissions, and execution attempts must remain in the
append-only ledger. Source: `docs/cases/G6_B_DISCOVERY_PROTOCOL.md:184` through
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:195` and
`cases/discovery/g6b/failure_ledger.json:6` through
`cases/discovery/g6b/failure_ledger.json:8`.

## Exact/DES Shared Target

Exact and DES are companion observations over the same `case_unit_id`. They
must share selected bad labels `D_global` and `D_local`, selected success label
`F`, versioned target, target identity, and scoring schema. They may differ only
by method role, DES stopping hash, later DES random stream, and later output
root reservation. Source: `docs/cases/G6_B_DISCOVERY_PROTOCOL.md:58` through
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:60` and
`cases/discovery/g6b/estimand_schema.json:39` through
`cases/discovery/g6b/estimand_schema.json:44`.

## Scoring Layers

The row-family schema must preserve five independent layers:

1. `theorem_prediction_status`
2. `metric_applicability`
3. `metric_observations`
4. `execution_status`
5. `reproducibility_status`

No placeholder supports or falsifies any claim. To preserve type meaning, the
serialized initial values must be
`theorem_prediction_status = not_evaluated`,
`metric_applicability = not_assessed`, `metric_observations = []`,
`execution_status = not_executed`, and
`reproducibility_status = not_assessed`; the generic phrase `not_executed`
must not be copied into all five fields. Source:
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:111`
through `docs/cases/G6_B_DISCOVERY_PROTOCOL.md:125` and
`cases/discovery/g6b/protocol.json:35` through
`cases/discovery/g6b/protocol.json:45`.

## Runtime Lock

The planned `runtime_lock_schema.json` defines two distinct later records.

`overlap_authority_lock` is required before an actual overlap report. It fixes
`target_path`, `target_branch`, `target_head`, `target_dirty_state`,
`upstream_ahead_behind`, `worktree_identity`, `repo_remote_url`,
`source_tree_hash`, sealed case-artifact hashes, and retired-authority artifact
paths/hashes. It proves which repository/case/evidence state was compared; it
does not authorize execution.

`execution_runtime_lock` is required after the actual overlap report passes and
immediately before any later execution-authorization request. It adds
`python_executable`, `python_version`, `package_lock_or_environment_hash`,
`validation_commands`, `validation_results`, `runtime_lock_created_at_utc`,
`science_execution_authorized_by_artifact`,
`pythondontwritebytecode_or_cache_policy`, and `output_root_policy`.

Initial values are `overlap_authority_lock_status = required_later` and
`execution_runtime_lock_status = required_later`. The local snapshot must not
be recorded as either authority. `PROJECT_HANDOFF.md:97` through
`PROJECT_HANDOFF.md:108` require fresh target lock and runtime discovery before
future execution claims.

## Validator Boundary

The planned validator is pure data-only. It may parse JSON, reject duplicate
keys, reject missing/extra/unknown keys, enforce schema versions, require
canonical repo-relative paths, verify fixed values, check cross-document
consistency, compute canonical JSON hashes, and report structural status.

It must not import or call LTS enumeration, CTMC, DES, G4/G5/G6 replay code,
case creation, output-root creation, output inspection, or scientific scoring.
It must resolve only the canonical
`<repo>/cases/discovery/g6b/row_families/structural_discovery_v1` root, reject
wrong-checkout/copy validation, and never fall back to `Path.cwd()`. It must
reject missing or extra nested JSON files just as the foundation validator
rejects top-level bundle drift.
The current foundation validator pattern is anchored at
`src/ims_deadlock/g6b_protocol.py:1`, `src/ims_deadlock/g6b_protocol.py:174`
through `src/ims_deadlock/g6b_protocol.py:227`,
`src/ims_deadlock/g6b_protocol.py:230` through
`src/ims_deadlock/g6b_protocol.py:295`, and
`src/ims_deadlock/g6b_protocol.py:356` through
`src/ims_deadlock/g6b_protocol.py:460`.

## Test Design

Green-path tests:

- canonical nested bundle validates and remains execution-disabled;
- no new top-level JSON appears under `cases/discovery/g6b/`;
- all nested planned JSON files exist;
- all seven controls have structural families;
- exact/DES companions share one `case_unit_id`;
- controlled reuse permits declared companion/schema reuse;
- retired overlap schema requires eight dimensions;
- future confirmation schema requires seven dimensions and limited metric reuse.

Refusal and mutation tests:

- reject top-level JSON additions;
- reject terminal-SCC `D_local`;
- reject `K_local` promotion without A2b or complete-LTS audit;
- reject exact/DES target drift;
- reject missing or semantically drifted controls;
- reject actual-overlap claims without an overlap-authority target lock;
- reject execution-runtime claims before the actual overlap report passes;
- reject runtime claims from local snapshot only;
- reject noncanonical copied bundle roots and any `Path.cwd()` fallback;
- reject missing or extra nested JSON;
- reject `adversarial_review_status = PASSED` in the initial bundle;
- reject `scientific_execution_authorized = true`;
- reject method observations counted as independent cases;
- reject output-root creation or output-inspection fields;
- mutate each retired-overlap dimension, future-confirmation dimension,
  control id, exact/DES consistency flag, ledger append-only flag,
  schema-only overlap flag, and runtime-lock status.

Pattern anchors: `tests/test_g6b_protocol.py:124` through
`tests/test_g6b_protocol.py:137`, `tests/test_g6b_protocol.py:140` through
`tests/test_g6b_protocol.py:230`, `tests/test_g6b_protocol.py:253` through
`tests/test_g6b_protocol.py:274`, and `tests/test_g6b_protocol.py:323` through
`tests/test_g6b_protocol.py:349`.

## Review State Machine

| State | Meaning | Science execution |
| --- | --- | --- |
| `SPEC_DRAFTED` | This design exists. | No |
| `ROW_FAMILY_BUNDLE_IMPLEMENTED` | Nested JSON and validator exist. | No |
| `DATA_ONLY_VALIDATION_PASSED` | Structural validation passes. | No |
| `ADVERSARIAL_ROW_FAMILY_REVIEW_PASSED` | Review permits writing a separate case-construction plan. | No |
| `CASE_CONSTRUCTION_PLAN_APPROVED` | A later plan authorizes only bounded case-artifact construction. | No |
| `CASE_ARTIFACTS_SEALED_NO_SCIENCE` | Planned case units, predictions, targets, and provenance manifests exist without scientific execution. | No |
| `OVERLAP_AUTHORITY_LOCK_RECORDED` | Exact remote source/case/retired-authority identity is locked for the overlap audit. | No |
| `ACTUAL_OVERLAP_REPORT_PASSED` | The sealed case artifacts have a remote-authority overlap report that passes. | No |
| `EXECUTION_RUNTIME_LOCK_RECORDED` | Fresh later runtime evidence exists for the exact sealed source/case state after overlap passes. | No |
| `EXPLICIT_SCIENCE_AUTHORIZATION_RECORDED` | Later artifact authorizes exact scope. | Only within that artifact scope |

Transitions are forward-only. Any failure appends a ledger entry and remains
non-executing. The foundation review stop condition requires a new explicit
authorization artifact, zero-overlap report, runtime lock, current ledger,
exact/DES same-target evidence, and full G6-B pass criteria before science
(`docs/verification/G6_B_PROTOCOL_FOUNDATION_REVIEW.md:205` through
`docs/verification/G6_B_PROTOCOL_FOUNDATION_REVIEW.md:211`).

## Stop Conditions

Stop before future execution if review is pending, explicit authorization is
absent, actual overlap report is absent, the overlap-authority lock or
execution-runtime lock is absent, required JSON is invalid or missing, extra
top-level JSON exists, `D_local` is terminal or unverified, exact/DES target
drifts, a mandatory control is missing or fails, a control failure is used as
support, the ledger is not append-only, or output-derived fields appear in
protocol files.

This spec does not authorize `CASE_CONSTRUCTION_PLAN_APPROVED`; it merely
defines that future gate. Case-artifact construction is therefore also stopped
at the end of this design tranche.

## Rejected Alternatives

| Alternative | Reason rejected |
| --- | --- |
| Add row-family files directly under `cases/discovery/g6b/` | Violates exact-five foundation bundle shape. |
| Require zero overlap across every discovery variant | Conflicts with controlled discovery-internal reuse. |
| Count exact and DES as independent cases | Inflates evidence and breaks companion identity. |
| Treat `PASS FOUNDATION ONLY` as authorization | The review explicitly denies science and G6-B pass. |
| Let validator call LTS/CTMC/DES | Violates data-only execution-disabled boundary. |
| Use local snapshot runtime as lock | Handoff requires fresh remote target lock. |
| Omit controls until execution | Controls must be fixed before outcome inspection. |
| Replace ledger with summaries | Protocol requires append-only retained failures and changes. |

## Acceptance Criteria

- This exact file exists at
  `docs/superpowers/specs/2026-07-31-g6b-row-family-design.md`.
- No protocol JSON, code, tests, roadmap, handoff, or remote file is edited.
- The spec states execution remains disabled and G6-B is not passed.
- It defines source hierarchy, ontology, nested file plan, identity hierarchy,
  controlled reuse matrix, retired eight-dimension overlap, future seven-
  dimension confirmation rule, controls, outcome-leakage prevention, exact/DES
  same-target companion contract, five scoring layers, runtime-lock schema,
  pure data-only validator boundary, tests, state machine, stop conditions, and
  rejected alternatives.
- Planned paths are labeled planned; source anchors are repo-relative.
- The document contains no unresolved placeholder markers or unfilled section.
