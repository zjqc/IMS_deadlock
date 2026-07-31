# G6-B Case Construction and Target-Certification Authorization Design

Status: `PRIOR WRITTEN REVISION APPROVED / HARDENED REVISION AWAITING USER REVIEW / EXECUTION-DISABLED / NO CASE CREATION`.

This specification records the approved concept-level staged G6-B design that
repairs the case-construction, overlap-admission, target-certification, and
quantitative-authorization circularities. It is a governance and architecture
document. It
does not create a discovery case, enumerate an LTS, certify an absorption
domain, construct or solve a CTMC, run DES, inspect scientific outputs, create
a quantitative output root, authorize science, or mark G6-B as `PASS`.

The prior written revision was approved, but a post-approval adversarial audit
found material hash-preimage, retired-authority-normalization, and fingerprint-
projection defects. This hardened revision corrects those defects and therefore
requires renewed written-spec review. Neither approval authorizes an
implementation plan, the future case-construction plan, any case artifact,
target-certification preflight, or quantitative execution.

The audited source base is commit
`1f342baea755f7c85ef538c7403c52cfb9d610c4`. The current nested G6-B bundle
remains schema-only at `ROW_FAMILY_BUNDLE_IMPLEMENTED`; its adversarial review
state remains `PENDING`, `case_creation_authorized` remains false, and
`scientific_execution_authorized` remains false.

## 1. Objective

Make the future G6-B gate graph reachable without weakening any scientific
boundary. The design separates seven capabilities that the current v1 row-family
contract partially conflates:

1. approved case-construction planning;
2. sealed pre-enumeration case inputs;
3. authorized read-only retired-authority fingerprint normalization;
4. input/provenance overlap admission against retired authorities;
5. explicitly authorized target-certification preflight;
6. exact/DES same-target identity locking; and
7. separately authorized quantitative execution.

The design also replaces a single global status with bundle-, case-unit-, and
method-level state. Every sealed unit must remain visible whether it passes,
refuses, fails, or is superseded. A favorable surviving subset may never erase
the denominator or the negative evidence that produced it.

## 2. Blocking Findings

### 2.1 Absorption-domain authorization circularity

`docs/cases/G6_B_DISCOVERY_PROTOCOL.md` requires exact and DES rows to share a
non-null `absorption_domain_hash` before future scientific execution. The hash
is runtime-derived from a complete stable LTS, the typed terminal/stopping
partition, the positive-rate stopped graph, the policy declaration, selected
targets, unselected closed SCCs, their reverse basin, and `S_T`.

The only current integrated producer is inside `derive_absorbing_ctmc` in
`src/ims_deadlock/g4_instances.py`. That function is explicitly documented as
a scientific execution entrypoint. It enumerates the stable LTS, partitions
it, certifies the absorption domain, and then continues into CTMC generator
construction. The current G6-B protocol authorizes neither enumeration nor
that scientific entrypoint. Therefore the current graph asks for a hash before
it permits the only integrated operation that can produce the hash.

### 2.2 Runtime-lock ordering circularity

The current `execution_runtime_lock` is placed before
`EXPLICIT_SCIENCE_AUTHORIZATION_RECORDED`, but its required fields include
`science_execution_authorized_by_artifact`. A pre-authorization runtime lock
cannot truthfully contain the later authorization artifact that depends on the
lock. Target-certification and quantitative execution also have different
capabilities and must not share one undifferentiated runtime lock.

### 2.3 State-subject category collapse

The current `review_state.json` has one `current_state`. That is safe while the
bundle is schema-only. It becomes false or ambiguous once multiple case units
and method observations exist: one unit can pass overlap while another refuses;
one exact/DES pair can match while another drifts. A single state can hide mixed
status and incentivize deleting refused rows.

### 2.4 Fingerprint-subject category collapse

The current identity schema lists all eight overlap dimensions under a
`case_unit_id`, while the row-family design also allows method-specific random
streams and output roots. These statements cannot both be literally true.
Case input identity, method provenance, and companion-group comparability have
different subjects. This design assigns every dimension to its correct
subject before defining overlap admission.

### 2.5 Independence overclaim

Hash inequality proves bounded canonical byte distinctness. It does not by
itself prove semantic non-derivation, independent construction, mechanism
diversity, random-process independence, or confirmatory blinding. G6-B is a
discovery recovery stage designed with knowledge of G5/G6 failures, so it must
not be described as epistemically independent confirmation.

### 2.6 Hash trivialization and retired-authority reconstruction

The prior revision required every canonical payload to contain its new subject
ID. That is invalid for retired-overlap comparison: a copied retired case could
be renamed and would then become hash-distinct by construction. The comparison
payload must therefore exclude governance IDs, paths, display labels, authors,
and timestamps, while a separate provenance envelope retains them for audit.

The prior revision also required records to carry their own final SHA-256 value
without defining the preimage. Literal self-inclusion is circular. Every
self-hashed record needs one versioned null-placeholder finalization rule, a
directed acyclic cross-reference order, and mutation tests.

Finally, the immutable G4, G5, and G6-R authorities do not store a uniform
eight-dimension fingerprint table. G5 and G6-R inherit much of their scientific
input identity from G4; some dimensions are bundle-level, some are method- or
stage-level, and some require a reviewed deterministic projection. Absence,
ambiguity, duplicated lineage, or an unreconstructable projection must never be
converted into non-overlap evidence.

### 2.7 Audited source anchors

The findings above are tied to the audited base, not inferred from the older
local snapshot:

- `docs/cases/G6_B_DISCOVERY_PROTOCOL.md:7-10` prohibits enumeration and
  scientific execution under the current foundation;
- `docs/cases/G6_B_DISCOVERY_PROTOCOL.md:60-62` requires a shared non-null
  `absorption_domain_hash` before future exact/DES science;
- `docs/cases/G6_B_DISCOVERY_PROTOCOL.md:81-111` defines the current eight-
  dimension retired-authority rule and the narrower future-confirmation rule;
- `docs/cases/G6_B_DISCOVERY_PROTOCOL.md:186-197` requires append-only failure
  and change retention;
- `src/ims_deadlock/g4_instances.py:410-505` couples enumeration and absorption
  certification to CTMC generator construction in one scientific entrypoint;
- `src/ims_deadlock/terminal_classes.py:732-818` produces structural/runtime
  hashes while building the typed partition;
- `src/ims_deadlock/terminal_classes.py:826-975` enforces the finite,
  nontruncated, rate, target, policy, and global-domain certificate;
- `src/ims_deadlock/terminal_classes.py:1064-1155` constructs the stopped
  positive-rate graph, closed SCC basin, `S_T`, and
  `absorption_domain_hash`;
- the current `runtime_lock_schema.json` places
  `science_execution_authorized_by_artifact` inside the earlier runtime lock;
  and
- the current `review_state.json` and
  `src/ims_deadlock/g6b_row_family_protocol.py:515-538` encode one global state
  with no target-certification preflight state;
- `cases/confirmation/g4/FREEZE_ENTRY.json` stores per-case canonical JSON
  hashes but bundle-level prediction, metric-schema, and random-stream hashes;
- `evidence/g5/G5_EXECUTION_LOCK.json` reuses the frozen G4 seal and adds a G5
  execution-root identity rather than a new case-input identity table; and
- `evidence/g6/G6_HISTORICAL_REPLAY_LOCK_R3.json` selects a G4 subset, binds
  G4/G5 lineage, and adds a replay root, so its inherited inputs cannot be
  counted as a third independent authority.

## 3. Rejected Architectures

### 3.1 Case-only construction plan

Rejected. It can seal inputs but leaves no legal producer for the required
target-certificate hashes.

### 3.2 Call `derive_absorbing_ctmc` and stop reading after certification

Rejected. Capability boundaries are determined by what the command can do,
not by which fields a reviewer later chooses to inspect. The function proceeds
into generator construction and imports the scientific execution surface.

### 3.3 Treat target certification as ordinary non-scientific validation

Rejected. Complete enumeration, terminal classification, and absorption-domain
certification are result-bearing eligibility evidence. They require their own
predeclared scope, authorization, runtime lock, artifacts, refusal rules, and
claim limits even though they do not estimate quantitative outcomes.

### 3.4 Keep one bundle state and attach free-text notes

Rejected. Notes do not make mixed per-unit states machine-auditable and cannot
prevent selective deletion.

### 3.5 Use unequal hashes as a universal independence certificate

Rejected. Serialization-level inequality and scientific independence are
different predicates with different evidence.

### 3.6 Put new subject IDs inside retired-overlap hash preimages

Rejected. A new case ID, method ID, bundle ID, path, or display name would make
an otherwise copied retired payload unequal by naming alone. Subject identity
belongs in a provenance envelope; the comparison projection is subject-free.

### 3.7 Treat all eight dimensions as eight independent inequality tests

Rejected. Case content may contain state, route, and parameter sub-identities;
metric schemas may be controlled reuse; exact methods have no random stream;
and output roots establish containment only. Admission is a typed conjunction
of dimension-specific policies, not a count of eight independent observations.

## 4. Chosen Architecture: Two Authorization Barriers

The chosen design has two explicit result-bearing execution barriers. A third,
data-only authorization boundary governs retired-authority normalization; it
cannot enumerate, classify, or compute scientific outputs and is not a route
around either result-bearing barrier.

### Barrier A: target-certification preflight

Barrier A may be opened only after case inputs and predictions are sealed, the
input-level retired-authority overlap audit is complete, the exact preflight
runtime is locked, and a scope-specific authorization artifact exists.

Barrier A permits only the following ordered, closed v1 operation-code array;
prose labels, aliases, and additional codes are invalid:

1. `load_sealed_case_input`;
2. `verify_input_hashes`;
3. `enumerate_complete_bounded_stable_lts`;
4. `verify_lts_provenance`;
5. `partition_typed_terminal_stopping_classes`;
6. `verify_rate_manifest`;
7. `verify_policy_declaration`;
8. `verify_selected_target_identity`;
9. `certify_global_absorption_domain`;
10. `emit_target_certificate_or_refusal`;
11. `emit_command_capture`;
12. `emit_filesystem_and_hash_manifests`;
13. `append_preflight_failure_ledger`; and
14. `validate_preflight_artifacts_data_only`.

The closed, lexicographically sorted v1 output-schema-ID array is exactly:

- `ims-deadlock/g6b-command-capture/v1`;
- `ims-deadlock/g6b-filesystem-manifest/v1`;
- `ims-deadlock/g6b-hash-manifest/v1`;
- `ims-deadlock/g6b-preflight-failure-ledger-entry/v1`;
- `ims-deadlock/g6b-target-certificate/v1`;
- `ims-deadlock/g6b-target-certification-batch-manifest/v1`;
- `ims-deadlock/g6b-target-certification-case-result/v1`; and
- `ims-deadlock/g6b-target-refusal/v1`.

The closed, lexicographically sorted v1 file-role array is exactly:
`batch_manifest`, `command_transcript`, `exit_code_capture`,
`failure_ledger_entry`, `filesystem_after_manifest`,
`filesystem_before_manifest`, `hash_manifest`, `per_case_result`,
`stderr_capture`, `target_certificate`, and `target_refusal`. Its exact
role-to-schema map is:

| File role | Required schema ID |
| --- | --- |
| `batch_manifest` | `ims-deadlock/g6b-target-certification-batch-manifest/v1` |
| `command_transcript` | `ims-deadlock/g6b-command-capture/v1` |
| `exit_code_capture` | `ims-deadlock/g6b-command-capture/v1` |
| `failure_ledger_entry` | `ims-deadlock/g6b-preflight-failure-ledger-entry/v1` |
| `filesystem_after_manifest` | `ims-deadlock/g6b-filesystem-manifest/v1` |
| `filesystem_before_manifest` | `ims-deadlock/g6b-filesystem-manifest/v1` |
| `hash_manifest` | `ims-deadlock/g6b-hash-manifest/v1` |
| `per_case_result` | `ims-deadlock/g6b-target-certification-case-result/v1` |
| `stderr_capture` | `ims-deadlock/g6b-command-capture/v1` |
| `target_certificate` | `ims-deadlock/g6b-target-certificate/v1` |
| `target_refusal` | `ims-deadlock/g6b-target-refusal/v1` |

The exact v1 file-role cardinality contract is:

- `batch_manifest`, `command_transcript`, `exit_code_capture`,
  `filesystem_after_manifest`, `filesystem_before_manifest`, `hash_manifest`,
  and `stderr_capture` each occur exactly once for every materialized command
  attempt;
- `per_case_result` occurs exactly `certified_count + refused_count` times and
  has the same case-key set as `per_case_result_hashes`;
- `target_certificate` occurs exactly `certified_count` times, one for each
  certified case;
- `target_refusal` occurs exactly `refused_count` times, one for each refused
  case; therefore zero is required for `complete_all_certified`;
- `failure_ledger_entry` occurs exactly `failure_ledger_entry_count` times with
  the exact IDs in the batch manifest's `failure_ledger_entry_ids`; zero is
  permitted only when no refusal, unexpected exception, capability violation,
  identity drift, side effect, interruption, or other ledger-required event
  occurred; and
- no other role or file is permitted. A pending case in an
  `incomplete_refused` batch has no fabricated per-case result, certificate, or
  refusal; the batch/capture/manifests and any causal failure-ledger entries
  preserve the incomplete attempt.

Barrier A does not permit quantitative science; it remains result-bearing
target-eligibility preflight.

### Barrier B: quantitative execution

Barrier B remains closed until every sealed object is accounted for, target
certification is complete and reviewed, exact/DES companions share the same
frozen target/certificate identity, mandatory negative controls satisfy their
frozen guard conditions, a fresh quantitative runtime lock exists, and a
separate authorization artifact names the exact case and method scope.

Barrier B is the only barrier that may later authorize CTMC generator
construction/solve, DES, metric observation, or quantitative output roots. This
specification does not open Barrier A or Barrier B.

## 5. Scientific and Authorization Boundary

The following current-instance values remain fixed throughout the schema-
design tranche:

- `study_role = discovery_only`;
- `confirmation_use = prohibited`;
- `case_creation_authorized = false`;
- `retired_authority_fingerprint_normalization_authorized = false`;
- `target_certification_preflight_authorized = false`;
- `scientific_execution_authorized = false`;
- `adversarial_review_status = PENDING`;
- `G6_B_status = OPEN`.

The v2 design must not continue using the broad
`scientific_execution_authorized` field as a forward state-transition key. It
is a legacy v1 summary that is false at the audited base and remains false in
the schema-only migration record. Forward-looking v2 artifacts use a typed
capability object with separate booleans:

- `case_construction_authorized`;
- `retired_authority_fingerprint_normalization_authorized`;
- `target_certification_preflight_authorized`; and
- `quantitative_execution_authorized`.

`target_certification_preflight_authorized` and the typed capability object are
proposed v2 fields; they are absent from the audited v1 artifacts and must be
introduced as false in the schema-only migration. The top-level
`protocol.json` v2 defines the capability vocabulary. The canonical current
values for this row-family bundle live only at
`row_family_protocol.json.typed_capabilities`. `review_state.json` references
the canonical object and its hash rather than duplicating mutable booleans.
Later instance authorization artifacts carry a capability name, scope, and
authorization hash; they do not rewrite the schema-bundle current values.

Each flag is false unless an exact capability-specific artifact validates.
Barrier A can therefore be described honestly as authorized result-bearing
target certification without implying quantitative execution. Barrier B alone
sets `quantitative_execution_authorized = true` for its enumerated scope.

The eventual schema implementation may make later states representable. It
must not advance the current instance into those states. A schema that describes
an authorization artifact is not itself that authorization artifact.

Target-certification preflight is scientific substrate and eligibility
evidence. It may establish that a frozen target is or is not well-defined under
the declared finite positive-rate stopped CTMC. It cannot establish theorem
support, metric quality, effect size, robustness, reproducibility of
quantitative outcomes, G6-B pass, or confirmation.

## 6. Identity Subjects and Definitions

### 6.1 Bundle

A `bundle_id` names one governed G6-B tranche containing the immutable planned
object manifest, case units, method observations, locks, reports, ledgers, and
authorizations. A bundle state is an aggregate governance predicate, not a
replacement for object states.

### 6.2 Case unit

A `case_unit_id` names one planned plant/model input unit. It is the unit of
discovery-case counting. Revisions that alter scientific identity require a
new `case_unit_id` or an explicit supersession record that preserves the old
unit and hashes.

### 6.3 Method observation

A `method_observation_id` names one method attached to one case unit. Exact and
DES companions have distinct method IDs but the same `case_unit_id`; they are
not two independent cases.

### 6.4 Method companion group

A `method_companion_group_id` binds exact/DES methods that intentionally reuse
one case input, selected target, absorption-domain certificate, and comparable
metric schema. Shared identity within this declared group is controlled reuse,
not evidence of independence.

### 6.5 Terminal local state

A terminal local state is one from which the object does not advance except by
an explicit, versioned supersession link or retained-refusal closure. Refused
and superseded objects remain in all later accounting manifests.

## 7. Canonical Input and Provenance Fingerprints

### 7.1 Two-layer fingerprint record

Every fingerprint is a typed record with two different hashes:

1. `comparison_projection_sha256_or_null` hashes the dimension-specific
   projection used by the retired-authority comparison policy; and
2. `record_provenance_sha256` hashes the audit envelope that owns the projection
   and records subject, authority, stage, lineage, sources, and derivation.

Except for the explicitly identified output-root containment projection, the
comparison projection must exclude `bundle_id`, `case_unit_id`,
`method_observation_id`, `method_companion_group_id`, filenames, repo paths,
display names, authors, timestamps, review IDs, and new G6-B provenance labels.
Changing only those values must leave the comparison projection unchanged. The
provenance envelope must include the applicable subject IDs and therefore may
change. Retired-overlap admission compares comparison projections only; it must
never use unequal provenance-envelope hashes as non-overlap evidence.

The exact `fingerprint_record_required_fields` are:
`record_schema_version`, `record_id`, `dimension`, `projection_kind`,
`subject_type`, `subject_id`, `owner_object_id`, `projection_schema_version`,
`comparison_projection_ref_or_null`, `comparison_projection_sha256_or_null`,
`canonicalization_version`, `source_authority_id`, `source_stage`,
`source_method_role_or_null`, `source_run_role_or_null`,
`source_artifact_refs`, `source_artifact_byte_hashes`, `normalizer_version`,
`dimension_status`, `lineage_id`, `inherited_from_record_id_or_null`,
`duplicate_lineage_of_record_id_or_null`, `depends_on_dimensions`,
`correlated_with_dimensions`, `comparison_policy`,
`applicability_reason_code_or_null`, and `record_provenance_sha256`.
No additional field is allowed.

Each `source_artifact_ref` element has exactly `authority_id`,
`repo_relative_posix_path`, `json_pointer_or_null`, and `source_role`; the array
is unique and sorted by those fields. `source_artifact_byte_hashes` is a
key-closed map from the same repo-relative paths to lowercase SHA-256 values.
`depends_on_dimensions` and `correlated_with_dimensions` are unique sorted
arrays from the exact eight-dimension vocabulary. `comparison_policy` is one of
`strict_semantic_distinctness`, `disjoint_random_substreams`,
`controlled_schema_reuse`, or `provenance_containment_only` and must match the
dimension table. Dynamic maps may contain only keys fixed by their owning
manifest; they are not free-form extension objects.

`projection_kind` is exactly one of `semantic_content`, `random_process`,
`controlled_schema`, or `provenance_containment`. The first three projections
are subject-free. A `provenance_containment` projection may contain the logical
bundle/case/method/run coordinates required to prove root containment, but its
result is prohibited from supporting semantic case distinctness.

### 7.2 Canonical JSON and hash-finalization contract

All newly introduced G6-B governance records and comparison projections use
`ims-deadlock/g6b-canonical-json/v2`. This version is not retroactively assigned
to frozen historical hashes. It has these exact rules:

- parse JSON with duplicate-member rejection at every depth;
- require all member names and string values to already be Unicode NFC; reject
  rather than silently normalize non-NFC text;
- sort object keys by Unicode code point, preserve declared array order, and
  require schema-declared set-like arrays to be unique and already sorted;
- serialize UTF-8 with `ensure_ascii = false`, `sort_keys = true`, separators
  `(',', ':')`, and `allow_nan = false`;
- prohibit NaN, infinities, JSON negative zero, and JSON floating-point values
  in hash-bearing governance payloads;
- encode counts and integral budgets as JSON integers; encode rates, durations,
  and other non-integral values as canonical decimal strings matching
  `^-?(0|[1-9][0-9]*)(\.[0-9]*[1-9])?$`, with `-0` prohibited and no exponent;
- when normalizing historical JSON numbers, parse their lexical token as an
  exact decimal and emit the same canonical decimal-string grammar rather than
  first converting through binary floating point;
- encode every committed path field only as a case-sensitive repo-relative
  POSIX path with `/`, no drive letter, leading slash, backslash, empty
  component, `.` or `..`, and no symlink-dependent resolution; runtime
  executables are represented by a logical ID and byte/environment hashes, not
  by an absolute path; and
- encode UTC timestamps only as fixed RFC 3339 `YYYY-MM-DDTHH:MM:SSZ` strings.

Every in-record self-hash uses the same finalization protocol. To compute a
field such as `artifact_sha256`, `manifest_sha256`, `runtime_lock_sha256`,
`authorization_sha256`, `record_provenance_sha256`,
`same_target_lock_sha256`, or `batch_manifest_sha256`, the producer validates
the complete record, replaces exactly that field with JSON `null`, canonicalizes
the result under v2, computes lowercase hexadecimal SHA-256, then stores the
digest. Validators reconstruct the null-placeholder preimage. Omission, an
empty string, a pre-populated digest in the preimage, more than one replaced
field, or any unknown excluded field is invalid.

Cross-record hashes form a directed acyclic graph in lifecycle order. A record
may reference only already finalized upstream records; no upstream record may
embed a downstream hash that points back to it. `hash_excludes_fields` is not a
free-form escape hatch and is prohibited; the one null-placeholder field is
fixed by the record schema.

Historical hash algorithms remain named by their actual frozen version. Their
bytes are verified, not silently recomputed under v2. A versioned retired-
authority normalizer produces separate v2 comparison projections and records
the historical source hash plus the projection hash.

### 7.3 Typed dimensions and subjects

| Dimension | Subject | Projection kind | Required policy meaning |
| --- | --- | --- | --- |
| `case_content_sha256` | case unit | semantic content | Composite hash of every classified scientific input component, excluding governance identity and outputs. |
| `state_snapshot_sha256` | case unit | semantic content | Hash of the declared state-bearing input before enumeration; never the reachable state universe. |
| `route_signature_sha256` | case unit | semantic content | Hash of typed route/transition/resource-demand structure, excluding external filenames and display names. |
| `parameter_tuple_sha256` | case unit | semantic content | Hash of all frozen structural/numeric parameters, state bound, rate-content hash, and policy-content hash that can affect semantics or certification. |
| `random_stream_manifest_sha256` | method observation | random process | For stochastic methods, hash of generator and allocation semantics; for exact methods, an explicit provenance-only not-applicable record. |
| `output_root_reservation_sha256` | method observation | provenance containment | Hash of the inert logical reservation; it may prove non-reuse/containment but never semantic case distinctness. |
| `sealed_prediction_sha256` | case unit | semantic content | Hash of the preregistered question, hypotheses, falsifiers, controls, scoring rule, claim boundary, and planned method roles. |
| `metric_schema_sha256` | method companion group | controlled schema | Hash of the preregistered metric/estimand/scoring schema; reviewed controlled reuse may be required for exact/DES comparability. |

`output_root_reservation_sha256` replaces the ambiguous v1 key `output_root` in
the v2 identity and overlap contracts. A migration record maps the old key but
cannot treat an old string value as a v2 reservation hash.

### 7.4 Exact comparison-projection schemas

Each projection is an exact JSON object with no additional properties. The
schema file must encode the following required keys and the indicated nested
contracts:

| Dimension | Exact projection keys |
| --- | --- |
| `case_content_sha256` | `projection_schema_version`, `input_mode`, `input_semantics_version`, `state_snapshot_sha256`, `route_signature_sha256`, `parameter_tuple_sha256`, `rate_manifest_content_sha256`, `policy_declaration_content_sha256`, `selected_target_declaration_sha256`, `control_declaration_sha256` |
| `state_snapshot_sha256` | `projection_schema_version`, `input_mode`, `state_payload_schema_version`, `state_payload` |
| `route_signature_sha256` | `projection_schema_version`, `input_mode`, `route_semantics_version`, `typed_resource_roles`, `typed_route_graph`, `transition_kinds`, `resource_demand_structure`, `mode_transition_structure` |
| `parameter_tuple_sha256` | `projection_schema_version`, `parameter_semantics_version`, `structural_parameter_entries`, `numeric_parameter_entries`, `state_bound`, `rate_manifest_content_sha256`, `policy_declaration_content_sha256` |
| `random_stream_manifest_sha256` | stochastic branch: `projection_schema_version`, `applicability_status`, `method_role`, `prng_family`, `prng_version`, `seed_root_commitment`, `seed_derivation_rule`, `substream_allocation`, `replicate_plan`, `sampling_plan`; exact branch: `projection_schema_version`, `applicability_status`, `method_role`, `reason_code` |
| `output_root_reservation_sha256` | `projection_schema_version`, `bundle_id`, `case_unit_id`, `method_observation_id`, `run_role`, `logical_root_id`, `repo_relative_posix_path`, `reserved`, `materialized`, `reservation_sha256` (null in the hash preimage) |
| `sealed_prediction_sha256` | `projection_schema_version`, `research_question`, `directional_hypotheses`, `falsifiers`, `mandatory_control_roles`, `planned_method_roles`, `scoring_rule`, `claim_boundary` |
| `metric_schema_sha256` | `projection_schema_version`, `estimand_schema_version`, `metric_entries`, `aggregation_rules`, `censoring_rules`, `failure_rules`, `scoring_rules`, `comparability_scope` |

The four component content hashes inside `case_content_sha256` also have closed
preimages. A rate manifest has exactly `schema_version`, `rate_units`, and
`event_rate_entries`, whose elements have `event_role`, `canonical_rate`, and
`rate_source_code`. A policy declaration has exactly `schema_version`, `mode`,
`excluded_plant_arc_roles`, and `filter_rule_code`. A selected-target
declaration has exactly `target_schema_version`, `selected_bad_classes`,
`success_class`, `exact_stopping_rule`, `des_stopping_rule`, and
`policy_analysis_class`. A control declaration has exactly `schema_version`,
`mandatory_control_roles`, `expected_guard_codes`, and `failure_effect_codes`.
Arrays are unique/sorted where order has no semantic meaning; no component may
contain observed states, results, or governance IDs.

`state_payload` is a discriminated union. For `model_generated_lts`, it contains
exactly `stable`, `complete`, `event_calendar_empty`, `holds`, `requests`,
`mode_by_job`, and `stage_by_job`, using sorted arrays of exact typed records;
the external state ID is excluded. For `explicit_finite_lts_input`, it contains
exactly `states`, `initial_state`, `marked_states`, and `transitions`, using the
versioned finite-LTS input schema. Neither branch may contain generated state
counts, reachability results, terminal classes, `S_reach`, `S_T`, or certificate
fields.

Each hold record has exactly `job_role`, `resource_role`, and `amount`; each
request record has exactly `job_role` and `alternatives`, where every alternative
is an ordered array of exact `resource_role`/`amount` demand records. Each mode
or stage record has exactly `job_role` and `value`. Explicit finite-LTS states
and marked states are unique sorted semantic labels; each transition has exactly
`source`, `event_kind`, and `target`, and transitions are unique and sorted.

Every structural or numeric parameter entry has exactly `name`, `value_type`,
and `value`. `value_type` is one of `integer`, `canonical_decimal_string`,
`boolean`, `enum`, `string`, `content_sha256`, or `ordered_tuple`; its value must
match that type. Entries are unique and sorted by `name`. Any scientific input
field not classified into the state, route, parameter, rate, policy, target, or
control projection is a validation refusal rather than an ignored extra.

`metric_entries` are unique and sorted by `metric_id`; each has exactly
`metric_id`, `estimand_id`, `unit`, `domain`, `direction`, `aggregation_rule_id`,
`censoring_rule_id`, `failure_rule_id`, `scoring_rule_id`, and
`applicability_rule`. The referenced rule arrays are exact keyed records with no
free-form objects.

The route projection uses only exact typed records: each resource-role record
has `resource_role`, `resource_kind`, and `capacity_parameter_name`; each route
record has `route_role` and `ordered_stage_roles`; each transition-kind record
has `transition_role`, `event_kind`, `source_mode`, and `target_mode`; each
resource-demand record has `transition_role`, `acquire_demands`, and
`release_demands`; and each mode-transition record has `job_role`,
`source_stage`, `event_kind`, and `target_stage`. Arrays are unique and sorted
where order is not scientific; route-stage order is preserved.

For stochastic streams, every `substream_allocation` element has exactly
`stream_role`, `derivation_label_sha256`, `start_counter`,
`stop_counter_exclusive`, and `stride`; allocations are disjoint and sorted by
stream role. `replicate_plan` has exactly `planned_replicates`,
`replicate_index_start`, and `replicate_index_stop_exclusive`.
`sampling_plan` has exactly `stopping_rule_sha256`,
`draw_budget_per_replication`, `common_random_numbers_group_or_null`, and
`antithetic_policy`.

Each sealed hypothesis record has exactly `hypothesis_role`, `statement`,
`direction`, `estimand_id`, `scope_code`, and `falsifier_roles`; each falsifier
record has exactly `falsifier_role`, `condition_code`, and `affected_hypothesis_roles`.
Statements are bounded NFC text, not identifiers used to manufacture hash
distinctness, embedded JSON, or post-outcome rationales. Mandatory-control and
method-role arrays are unique sorted enums. `scoring_rule` has exactly
`scoring_rule_id`, `required_input_roles`, `decision_table_sha256`, and
`failure_handling_code`. `claim_boundary` has exactly `study_role`,
`confirmation_use`, `estimand_scope_code`, `population_scope_code`, and
`forbidden_upgrade_codes`.

Internal resource, job, route, transition, or finite-state labels can be
scientifically meaningful and are therefore not blindly stripped. Because the
projection hash is not a complete graph-isomorphism oracle, a separate
`semantic_lineage_audit` must test declared renamings, typed-graph isomorphism,
parameter transforms, and cosmetic rewrites. Hash inequality cannot pass a case
whose lineage audit detects an isomorphic or outcome-driven retired derivative.
Every `*_role`, parameter name, metric ID, estimand ID, and condition/rule code
in a comparison projection must be either a schema-enumerated semantic ontology
code or the output of a versioned alias-to-canonical-role map. An unrecognized
alias refuses; minting a synonym cannot manufacture distinctness.

### 7.5 `state_snapshot_sha256`

The input mode is sealed. Switching modes creates a new case-unit identity.
The comparison projection never contains the new case-unit ID. Its provenance
envelope does.

`state_space_hash` has a different subject and time: it is produced only from
the complete runtime `StableLTS` during authorized target certification. The
validator must reject substituting `state_space_hash` for
`state_snapshot_sha256` in any retired-authority overlap comparison.

`state_snapshot_sha256`, `route_signature_sha256`, and
`parameter_tuple_sha256` are declared sub-identities of
`case_content_sha256`. Each fingerprint record must state this relation in
`depends_on_dimensions` and its correlations in `correlated_with_dimensions`.
Reports count them as checked projections, not independent identity
observations.

### 7.6 Random-stream not-applicable records

An exact method without stochastic sampling has a method-specific provenance
envelope whose subject-free projection has
`applicability_status = not_applicable_by_protocol`, its exact method role, and
a versioned reason code. A global shared record is prohibited, but different
envelopes may correctly own the same subject-free not-applicable projection.
That equality is neither overlap nor distinctness and can only yield
`not_applicable_by_protocol_pass`; it never proves random-process independence.

For stochastic methods, unequal manifest hashes are insufficient. Admission
requires a verified disjoint-substream proof over PRNG family/version, seed-root
commitment, derivation rule, allocation, and planned sampling range. The result
is `disjoint_stream_pass`, not an independence claim beyond the frozen generator
contract. A seed derivation may bind the subject-free case-content hash and
method role, but may not manufacture distinctness from a new bundle, case, or
method ID alone.

### 7.7 Output-root reservation

The output-root dimension is a canonical logical reservation, not an existing
directory. It includes bundle, case, method, and run-role coordinates because
those coordinates establish containment. Before quantitative authorization,
validators require `reserved = true`, `materialized = false`, and an exact path
equal to the deterministic expansion of the v2 root template. They reject an
absolute path, fallback path, pre-existing root, filesystem-inspection field,
or reuse of any retired materialized logical root.

G4 freeze has no materialized quantitative root and is recorded as
`not_applicable_retired_stage`, not `pass_distinct`. G5 and G6-R roots are
normalized by stage, logical relative root, case/run subpath, and lineage;
absolute workstation paths remain provenance-only. A renamed root cannot rescue
copied case content. The only successful output-root result is
`containment_separation_pass`, which contributes to provenance containment and
never to semantic distinctness totals.

### 7.8 Dimension outcomes, dependence, and propagation

`dimension_status` is exactly one of `direct_stored`,
`derived_by_versioned_normalizer`, `inherited_from_authority`,
`not_applicable_by_protocol`, `not_applicable_retired_stage`, or
`unreconstructable_refuse`.

`comparison_status` is exactly one of `pass_distinct`, `overlap_hit`,
`controlled_reuse_pass`, `disjoint_stream_pass`,
`not_applicable_by_protocol_pass`, `containment_separation_pass`,
`inherited_compared`, `missing_source`, `unreconstructable`,
`normalizer_error`, or `semantic_lineage_ambiguous`.

Admission is a typed conjunction, not eight hash inequalities:

- case-content, state, route, parameter, and sealed-prediction projections
  require `pass_distinct` against every comparable unique retired lineage plus a
  passed semantic-lineage audit;
- a stochastic random-stream record requires `disjoint_stream_pass`; an exact
  record requires `not_applicable_by_protocol_pass`;
- an output-root reservation requires `containment_separation_pass`; and
- a metric schema requires `pass_distinct` or `controlled_reuse_pass` backed by
  an exact reuse record and companion-group comparability rationale.

A `metric_schema_reuse_record` has exactly `schema_version`, `reuse_record_id`,
`dimension`, `retired_authority_id`, `retired_lineage_id`,
`retired_metric_schema_sha256`, `new_metric_schema_sha256`,
`method_companion_group_id`, `reuse_reason_code`, `comparability_requirement`,
`permitted_claim_codes`, `forbidden_claim_codes`, `review_artifact_hash`, and
`reuse_record_sha256`. Controlled reuse cannot be inferred from equality alone.

`overlap_hit`, `missing_source`, `unreconstructable`, `normalizer_error`, or
`semantic_lineage_ambiguous` is fail-closed. `inherited_compared` may report
provenance but is successful only when its unique ancestor comparison has an
allowed terminal status. Retired aliases sharing one `lineage_id` are compared
once and reported as inherited/duplicate lineage, never counted as independent
authorities.

One refused or missing planned method-level dimension refuses its owning case
unit before `CASE_UNIT_OVERLAP_PASSED`. Before sealing, a method can be replaced
only by a reviewed manifest revision; after sealing, dropping or replacing it
requires retained refusal, a superseding identity, a new sealed-manifest hash,
and renewed overlap review. A companion cannot lend its passing stream, root, or
metric-reuse record.

## 8. Independence and Non-Reuse Claim Lattice

The overlap report must keep the following predicates separate:

| Predicate | Evidence | Permitted claim |
| --- | --- | --- |
| `canonical_byte_distinctness` | Canonical payload/hash comparison. | The compared canonical payloads are unequal. |
| `provenance_nonreuse` | Artifact lineage, source/target locks, path reservations, and immutable manifests. | The governed artifacts were not reused under the declared scope. |
| `semantic_non_derivation` | Case-construction lineage audit showing no rename, copy, cosmetic transform, or outcome-driven parameter shift from a retired case. | No detected semantic derivation under the reviewed construction rules. |
| `construction_process_separation` | Who/what constructed the case, which evidence was visible, and when inputs were sealed. | The recorded construction process had the stated separation; G6-B cannot claim blindness to known G5/G6 failures. |
| `mechanism_diversity` | Structural family and hypothesis-specific audit. | The cases exercise distinct declared mechanisms; this is not statistical independence. |
| `random_process_independence` | PRNG family/version, seed-root derivation, disjoint substream proof, and sampling plan. | The stochastic method streams are disjoint under the frozen generator contract. |
| `confirmation_blinding` | Future G6-C identity and pre-outcome access controls. | Only a later confirmation tranche may make a scoped blinding claim. |
| `bounded_nonreuse_admission` | All typed, lineage-deduplicated comparison outcomes plus semantic-lineage and containment checks. | The unit passed the protocol's bounded retired-authority admission rule; this is not eight independent observations. |

The report must never collapse these predicates into a single boolean named
`independent`. In particular:

- unequal hashes do not prove statistical independence;
- a unique output root does not prove case identity independence;
- changing a subject ID or path cannot make copied scientific content pass;
- inherited G4/G5/G6-R lineage is one lineage, not three independent checks;
- metric-schema reuse does not invalidate a case when preregistered for
  same-target comparability, and does not create an independent method;
- G6-B discovery cannot be relabelled as held-out confirmation; and
- future confirmation must establish its own case/provenance separation and
  blinding rather than inheriting a G6-B overlap result.

## 9. Sealed Case-Construction Contract

A later case-construction plan must be reviewed and explicitly approved before
any case artifact is materialized. Its authority is bounded to the listed case
units and the following non-result-bearing operations:

- create canonical case input payloads;
- create route, parameter, rate-manifest, and policy-declaration payloads;
- create method declarations and inert random-stream manifests;
- reserve, but not materialize, quantitative output-root identities;
- seal predictions, hypotheses, falsifiers, controls, and metric schemas;
- compute input/provenance hashes; and
- append construction refusals or revisions to the ledger.

The sealed case manifest must contain every planned `case_unit_id` and
`method_observation_id`, all subject-aware fingerprints, all mandatory controls,
the exact planned denominator, and a canonical manifest hash. No planned object
may disappear from later manifests.

Case construction must not enumerate states, classify terminal sets, certify
targets, solve a CTMC, run DES, create result directories, inspect prior G6-B
outputs, or populate any observation/scoring field.

Every case carries a sealed `semantic_lineage_declaration`. It records what
retired/template evidence was visible, any declared structural parent or
transform, and the construction log/review hashes. It cannot assert blindness:
G6-B is intentionally a discovery repair stage. The later lineage audit checks
the declaration against subject-free projections, typed-graph isomorphism, and
parameter transforms; a false/ambiguous declaration is itself a refusal.

## 10. Input-Level Overlap Audit

The actual overlap audit occurs only after sealing and uses a fresh, clean
`input_overlap_authority_lock`. The lock binds:

- repository remote, branch, exact HEAD and tree;
- a required clean Git state and linked-worktree identity;
- sealed bundle and per-object manifest hashes;
- exact retired G4/G5/G6-R authority paths and hashes;
- retired-normalization authorization, normalization-manifest, authority-lock,
  and fingerprint-record hashes;
- canonicalization algorithm versions;
- comparison command/validator versions; and
- append-only ledger head.

`input_overlap_authority_lock_required_fields` is exactly `schema_version`,
`lock_id`, `source_remote`, `source_branch`, `source_head`, `source_tree_hash`,
`source_dirty_state`, `source_worktree_identity`, `sealed_bundle_manifest_hash`,
`normalization_authorization_sha256`, `normalization_manifest_sha256`,
`authority_lock_record_hashes`, `unique_lineage_map_sha256`,
`comparison_command_manifest_sha256`, `validator_code_hashes`,
`canonicalization_versions`, `normalizer_version`, `planned_case_unit_ids`,
`planned_method_observation_ids`, `planned_method_companion_group_ids`,
`ledger_head_hash`, `created_at_utc`, and `lock_sha256`.

`source_worktree_identity` has exactly `logical_worktree_id`, `worktree_kind`,
`gitdir_file_sha256_or_null`, `common_dir_identity_sha256`,
`worktree_admin_identity_sha256`, and `checked_out_tree_hash`.
`worktree_kind` is exactly `linked`; `checked_out_tree_hash` must equal the
lock's `source_tree_hash`. The identity hashes bind the resolved Git
administrative identities without serializing an absolute path, user name,
host name, or private-network identifier. `source_branch` must equal the
checked-out branch, and `source_dirty_state` must be `clean`.

### 10.1 Retired-authority source inventory and lineage

Before any comparison, a versioned retired-authority normalizer must verify this
exact immutable inventory against the locked Git tree and the authorities'
internal freeze/hash references:

- G4: `FREEZE_ENTRY.json`, `case_manifest.json`, and every path in
  `case_manifest.json#/cases/*/path` resolved relative to
  `cases/confirmation/g4/`; that path set must be exactly
  `cases/{case_id}.json` for the same unique nine IDs in
  `FREEZE_ENTRY.json#/included_cases`,
  `FREEZE_ENTRY.json#/case_json_sha256_by_id`, and
  `case_manifest.json#/cases/*/case_id`, with no missing, extra, duplicate, or
  cross-ID path and with every manifest/freeze hash independently matching;
  `baseline_applicability.json`, `exclusions.json`,
  `experiment_scripts_manifest.json`, `metrics_schema.json`, `predictions.json`,
  `random_stream_manifest.json`, `runtime_lock.json`, and
  `theory_manifest.json` under `cases/confirmation/g4/`;
- G5: `G5_EXECUTION_LOCK.json`, `G5_RAW_HASH_MANIFEST.json`,
  `G5_RESULT_SUMMARY.json`, and `G5_SCORING_ERRATUM.json` under `evidence/g5/`;
  and
- G6-R: `G6_HISTORICAL_REPLAY_LOCK_R3.json`,
  `G6_HISTORICAL_REPLAY_FAILURE_LEDGER.json`,
  `G6_HISTORICAL_REPLAY_R3_RAW_HASH_MANIFEST.json`, and
  `G6_HISTORICAL_REPLAY_R3_REPORT.json` under `evidence/g6/`.

Every file gets a raw byte SHA-256. Where a frozen authority declares a
canonical/content hash, that hash is independently recomputed with the named
historical algorithm and reconciled. A clean current Git file is not accepted
as the authority merely because the path exists. Missing, extra where an exact
manifest applies, stale, byte-mismatched, internally inconsistent, or only
available in an unverified local snapshot yields `missing_retired_authority` or
`retired_authority_hash_mismatch` and stops the audit.

G4 owns the frozen case-input, prediction, metric, and random-stream lineage.
G5 inherits those inputs and adds execution-stage method/root provenance. G6-R
inherits its selected G4/G5 input lineage and adds replay-stage method/root
provenance. `lineage_id`, `inherited_from_record_id_or_null`, and
`duplicate_lineage_of_record_id_or_null` make this explicit. The report must not
count inherited G4 material once as G4, again as G5, and again as G6-R.

An origin `lineage_id` is `sha256:` plus the v2 canonical hash of exactly
`origin_authority_id`, `origin_subject_type`, `origin_subject_id`,
`origin_dimension`, `origin_comparison_projection_sha256_or_null`, and
`origin_source_artifact_byte_hashes`. These values exist before the fingerprint
record is finalized, so the lineage ID does not depend on
`record_provenance_sha256`. An inherited record copies that lineage ID and names
its immediate ancestor; it must not mint a new lineage from its later stage or
path. The `unique_lineage_map` is a key-closed map from lineage ID to one origin
record and all inherited/duplicate record IDs.

### 10.2 Versioned normalization manifest

The required `retired_authority_normalization_manifest` has exactly:
`schema_version`, `manifest_id`, `source_remote`, `source_head`,
`source_tree_hash`, `source_dirty_state`, `authority_ids`,
`expected_file_manifest`, `verified_file_byte_hashes`,
`frozen_hash_validation_results`, `historical_canonicalization_versions`,
`projection_canonicalization_version`, `normalizer_version`,
`normalizer_code_sha256`, `normalization_authorization_sha256`,
`authority_lock_record_hashes`, `authority_source_record_hashes`,
`fingerprint_record_hashes`,
`unique_lineage_map`, `dimension_status_counts`, `missing_source_records`,
`unreconstructable_records`, `comparison_eligibility`, `created_at_utc`, and
`manifest_sha256`. No additional field is allowed.

Each `authority_lock_record` has exactly `authority_id`, `origin_remote`,
`origin_commit_or_null`, `origin_tree_hash_or_null`, `origin_lock_artifact_ref`,
`origin_artifact_inventory_hash`, `current_merged_copy_tree_hash`,
`identity_verification_status`, and `authority_lock_record_sha256`.
`identity_verification_status` is `verified_historical_identity`,
`verified_merged_copy_against_historical_hashes`, or `unverified_refuse`; only
the first two may supply projections.

Each `authority_source_record` has exactly `authority_id`, `authority_stage`,
`authority_lock_record_sha256`, `repo_relative_path`, `raw_byte_sha256`,
`declared_historical_hash_or_null`, `declared_hash_algorithm_or_null`,
`declared_hash_verified`, `allowed_projection_uses`, and
`contains_outcome_fields`. Outcome-bearing sources may be byte-hash verified for
inventory completeness, but normalization may parse only their listed identity,
root, lineage, and hash-manifest fields; scientific values and favorable or
adverse result fields are not projection inputs.

For every authority/subject/dimension, the normalizer emits a fingerprint
record from Section 7. A source dimension is exactly one of:
`direct_stored`, `derived_by_versioned_normalizer`,
`inherited_from_authority`, `not_applicable_by_protocol`,
`not_applicable_retired_stage`, or `unreconstructable_refuse`.

The G4 protocol-kind discriminator is a closed map, not an inferred name:

| G4 case ID | Exact `input_payload.protocol_kind` |
| --- | --- |
| `G4_ADVERSARIAL_BOUNDARY` | `adversarial_snapshot` |
| `G4_B05_SUPERVISOR_COMPARATOR` | `adapted_candidate_monitor_cover` |
| `G4_CRP_OUTSIDE_S4PR` | `crp_evidence_audit` |
| `G4_CRP_S4PR_AGREE` | `crp_evidence_audit` |
| `G4_CRP_UNREACHABLE_CANDIDATE` | `crp_evidence_audit` |
| `G4_IMS_PARAMETER_GRID` | `bidirectional_island_grid` |
| `G4_L30_RESOURCE_BASELINE` | `supplied_l30_inequalities` |
| `G4_MEDIUM_ISLAND_REBUILD` | `medium_island_rebuild` |
| `G4_RECORDER_TARGET_QUANTIFICATION` | `fixed_recorder_target` |

The retired-only `subject_type` vocabulary is exactly `retired_case`,
`retired_case_subunit`, `retired_method_observation`, and
`retired_method_companion_group`. Each of the nine G4 cases emits one
`retired_case`. Composite protocols additionally emit deterministic
`retired_case_subunit` records with `owner_object_id` equal to the parent case:

| Protocol kind | Exact subunit selector | Exact subunit ID component |
| --- | --- | --- |
| `bidirectional_island_grid` | each element of `/input_payload/protocol_input/cells`, selected by unique `cell_id` | `cell_id` |
| `supplied_l30_inequalities` | each element of `/input_payload/protocol_input/inequalities`, selected by unique `name` | `name` |
| `adapted_candidate_monitor_cover` | each element of `/input_payload/protocol_input/candidate_monitors`, selected by unique `monitor_id` | `monitor_id` |
| all other protocol kinds | no subunit | not applicable |

For a subunit, the versioned transform combines the selected element with only
the parent fields required to interpret it: grid subunits retain
`generator_id`; inequality subunits retain `capacities`,
`finite_capacity_s3pr_ens3pr`, and `inequality_provenance`; monitor subunits
retain `finite_lts`, `legal_states`, `first_met_bad_states`, and `state_bound`.
The subject ID exists only in the provenance envelope. New cases are compared
against every whole retired case and every type-compatible subunit, so copying
one grid cell, inequality, or candidate monitor cannot evade the audit merely
because the enclosing historical case was composite. Dimensions that the exact
subunit transform declares structurally absent are
`not_applicable_retired_stage`; the normalizer may not invent them.

The following table is the closed per-authority/per-dimension producer map.
`select_unique(K,V)` means exactly one array or object member whose key `K`
equals `V`; zero or multiple matches refuse. Every transform produces the exact
Section 7.4 payload, uses canonical decimal parsing from Section 7.2, and has no
unlisted field reads.

| Authority/subject | Dimension | Exact source pointer or inheritance | Transform/status | Missing or ambiguous behavior |
| --- | --- | --- | --- | --- |
| G4 whole case and compatible subunit | `case_content_sha256` | case file `/input_payload` and `/expected_outputs_schema`; a subunit uses the selector and parent context above | `g4_case_content_projection/v1`; `derived_by_versioned_normalizer` | `retired_projection_unreconstructable` |
| G4 `adapted_candidate_monitor_cover`, `crp_evidence_audit`, or `fixed_recorder_target` whole/subunit | `state_snapshot_sha256` | case file `/input_payload/protocol_input/finite_lts` | `g4_explicit_state_projection/v1`; `derived_by_versioned_normalizer` | `retired_projection_unreconstructable` |
| G4 `adversarial_snapshot`, `bidirectional_island_grid`, or `medium_island_rebuild` whole/subunit | `state_snapshot_sha256` | case file `/input_payload/protocol_input/generator_id` plus `/input_payload/protocol_input/parameters` or selected `/input_payload/protocol_input/cells` element | `g4_generated_state_projection/v1`; `derived_by_versioned_normalizer` using the reviewed static map only | `retired_projection_unreconstructable` |
| G4 `supplied_l30_inequalities` whole/subunit | `state_snapshot_sha256` | schema-declared absence | no projection; `not_applicable_retired_stage` | any fabricated state is `retired_normalizer_error` |
| G4 `adapted_candidate_monitor_cover`, `crp_evidence_audit`, or `fixed_recorder_target` whole/subunit | `route_signature_sha256` | case file `/input_payload/protocol_input/finite_lts/transitions` | `g4_explicit_route_projection/v1`; `derived_by_versioned_normalizer` | `retired_projection_unreconstructable` |
| G4 `adversarial_snapshot`, `bidirectional_island_grid`, or `medium_island_rebuild` whole/subunit | `route_signature_sha256` | same generator/parameter or selected-cell pointers as the generated-state row | `g4_generator_route_projection/v1`; `derived_by_versioned_normalizer` using the reviewed static map only | `retired_projection_unreconstructable` |
| G4 `supplied_l30_inequalities` whole/subunit | `route_signature_sha256` | schema-declared absence | no projection; `not_applicable_retired_stage` | any fabricated route is `retired_normalizer_error` |
| every G4 whole case and subunit | `parameter_tuple_sha256` | case file `/input_payload/protocol_input`, narrowed by the subunit rule when applicable | `g4_parameter_projection/v1`; `derived_by_versioned_normalizer` | `retired_projection_unreconstructable` |
| every G4 whole case | `sealed_prediction_sha256` | `predictions.json#/predictions`, `select_unique(case_id, parent_case_id)` | `g4_prediction_projection/v1`; `derived_by_versioned_normalizer` | `retired_projection_unreconstructable` |
| G4 grid subunit | `sealed_prediction_sha256` | selected parent prediction plus `/cell_predictions/{cell_id}` | `g4_grid_cell_prediction_projection/v1`; `derived_by_versioned_normalizer` | `retired_projection_unreconstructable` |
| other G4 subunit | `sealed_prediction_sha256` | schema-declared absence of a subunit-specific frozen prediction | no projection; `not_applicable_retired_stage` | any parent-wide prediction copied as subunit-specific is `retired_normalizer_error` |
| every G4 case method subject | `random_stream_manifest_sha256` | `random_stream_manifest.json#/streams_by_case/{case_id}` | `g4_stream_projection/v1`; `direct_stored` after exact schema translation | `retired_projection_unreconstructable` |
| every G4 case companion-group subject | `metric_schema_sha256` | every `metrics_schema.json#/metrics/*`, retaining the metric definition and only `/applicability_by_case/{case_id}` for that case | `g4_metric_projection/v1`; `derived_by_versioned_normalizer` | `retired_projection_unreconstructable` |
| every G4 method subject | `output_root_reservation_sha256` | schema-declared absence | no projection; `not_applicable_retired_stage` | any fabricated root is `retired_normalizer_error` |
| every G5 case/method/companion subject | case, state, route, parameter, prediction, random-stream, and metric dimensions | exact G4 lineage named by `G5_EXECUTION_LOCK.json#/g4_seal` after all referenced hashes validate | copy the G4 `lineage_id`; `inherited_from_authority`; add G5 method-stage provenance only to the envelope | `retired_authority_hash_mismatch` or `retired_projection_unreconstructable` |
| each G5 `(case_id, run_label)` method subject | `output_root_reservation_sha256` | `G5_EXECUTION_LOCK.json#/output_roots/raw_output_root_relative` plus case IDs and run labels derived only from `/execution_schedule` | `g5_output_root_projection/v1`; `derived_by_versioned_normalizer` | `retired_projection_unreconstructable` |
| every G6-R case/method subject | case, state, route, parameter, prediction, and random-stream dimensions | exact selected G4/G5 lineage named by `G6_HISTORICAL_REPLAY_LOCK_R3.json#/historical_g4` and `/original_g5` after all referenced hashes validate | copy the unique ancestor `lineage_id`; `inherited_from_authority`; add replay-stage provenance only to the envelope | `retired_authority_hash_mismatch` or `retired_projection_unreconstructable` |
| every G6-R companion-group subject | `metric_schema_sha256` | inherited G4 metric projection plus `G6_HISTORICAL_REPLAY_LOCK_R3.json#/default_estimand_spec` and `/default_estimand_spec_sha256` | `g6r_metric_overlay_projection/v1`; `derived_by_versioned_normalizer`, with the G4 lineage explicitly retained as an input lineage | `retired_projection_unreconstructable` |
| each G6-R `(case_id, run_label)` method subject | `output_root_reservation_sha256` | lock `/output_root`, `/case_ids`, `/run_labels`, and `/execution_schedule`; raw manifest `/output_root` is equality validation only | `g6r_output_root_projection/v1`; `derived_by_versioned_normalizer` | `retired_projection_unreconstructable` |

G5 root normalization accepts only its locked
`raw_output_root_relative` after repo-relative POSIX validation. Its case and
run-label sets are derived only from the internally reconciled execution-lock
schedule; `G5_RAW_HASH_MANIFEST.json` is used only for byte/source-hash
validation and supplies no projection preimage.

G6-R root normalization first requires the lock and raw-manifest root strings to
match, normalizes each backslash (`\`) to `/` only for parsing, and extracts the
unique suffix beginning `artifacts/g6-historical-replay/`; a missing, repeated,
or differently cased suffix refuses. Its case/run sets and deterministic
subpaths come only from the internally reconciled lock `/case_ids`,
`/run_labels`, and `/execution_schedule`. Raw-manifest relative-path keys and
all hash values are validation evidence only and supply no comparison-projection
preimage. The absolute prefix and raw string are represented only by the source
artifact byte hash and never copied into a comparison projection or committed
normalization record. No historical output file content is read.

No producer may guess a missing route, state, parameter, stream, metric, or root
from filenames or result values. Historical numeric tokens are projected via
exact-decimal parsing under Section 7.2. If static JSON does not expose a needed
generated input, a later reviewed normalizer may use only an exact whitelisted
deterministic historical input builder to materialize an input object in memory;
its source hash and function symbol must be locked. It may not enumerate states,
classify targets, construct/solve a CTMC, run DES, score, inspect quantitative
payloads, or write evidence. If the projection still cannot be reconstructed,
the dimension is `unreconstructable_refuse`.

### 10.3 Normalization authorization boundary

Running the normalizer requires a separate
`retired_authority_fingerprint_normalization_authorization` whose exact fields
are `schema_version`, `authorization_id`, `capability`, `authorized`,
`source_head`, `source_tree_hash`, `authority_ids`, `expected_file_manifest_hash`,
`allowed_source_paths`, `allowed_json_fields_by_source`,
`allowed_historical_builder_symbols`, `normalizer_code_sha256`,
`allowed_operations`, `allowed_project_imports`, `forbidden_imports`,
`forbidden_calls`,
`allowed_output_schema`, `allowed_output_root`, `review_artifact_hash`,
`issued_at_utc`, `invalidated_by_identity_drift`, and
`authorization_sha256`. The only valid capability is
`retired_authority_fingerprint_normalization`.

For v1, `allowed_json_fields_by_source` is the following closed
pointer-to-use matrix. Each serialized row has exactly `source_path_pattern`,
`selector_kind`, `selectors`, and the singular `allowed_use`. `selector_kind` is
exactly `exact_pointer_set`, `prefix_set`, `element_pointer_pattern_set`, or
`raw_bytes_only`. An exact pointer names only that value; a prefix names that
value and descendants but never a sibling; an element pattern replaces only
the literal `*` array index or declared dynamic-map key and then applies the
remaining exact suffix. A source/selector may be used only for the one use in
its row; permissions do not union across other selectors in the same source.

The only `allowed_use` codes are `authority_identity`,
`source_hash_validation`, `case_content_projection`, `prediction_projection`,
`metric_projection`, `random_stream_projection`, `lineage_link`,
`method_stage_projection`, `output_root_source_equality_validation`, and
`output_root_containment_projection`.

| Source | Selector kind and exact selectors | Singular allowed use |
| --- | --- | --- |
| G4 `FREEZE_ENTRY.json` | exact pointers `/schema_version`, `/freeze_id`, `/implementation_commit`, `/preregistration_commit`, `/confirmation_results_inspected` | `authority_identity` |
| G4 `FREEZE_ENTRY.json` | prefixes `/artifact_hashes`, `/case_json_sha256_by_id` | `source_hash_validation` |
| G4 `FREEZE_ENTRY.json` | exact pointers `/freeze_id`, `/implementation_commit`, `/preregistration_commit`, `/included_cases`, `/excluded_cases` | `lineage_link` |
| each manifest-selected G4 case JSON | exact pointers `/schema_version`, `/case_id`, `/family`, `/protocol`, `/contamination/derived_from_discovery_case`, `/contamination/excluded_discovery_case_ids`, `/contamination/excluded_discovery_family_ids`, `/contamination/provenance` | `lineage_link` |
| each manifest-selected G4 case JSON | prefixes `/input_payload`, `/expected_outputs_schema` | `case_content_projection` |
| G4 `case_manifest.json` | exact pointer `/schema_version`; element pointer patterns `/cases/*/case_id`, `/cases/*/family`, `/cases/*/path`, `/cases/*/hash_mode`, `/cases/*/sha256` | `authority_identity` |
| G4 `case_manifest.json` | element pointer patterns `/cases/*/path`, `/cases/*/hash_mode`, `/cases/*/sha256` | `source_hash_validation` |
| G4 `case_manifest.json` | element pointer patterns `/cases/*/case_id`, `/cases/*/family`, `/cases/*/path` | `lineage_link` |
| G4 `predictions.json` | exact pointer `/schema_version`; prefix `/predictions` | `prediction_projection` |
| G4 `metrics_schema.json` | exact pointer `/schema_version`; prefix `/metrics` | `metric_projection` |
| G4 `random_stream_manifest.json` | exact pointer `/schema_version`; prefix `/streams_by_case` | `random_stream_projection` |
| G4 `baseline_applicability.json`, `exclusions.json`, `experiment_scripts_manifest.json`, `runtime_lock.json`, or `theory_manifest.json` | raw bytes only; JSON parsing prohibited | `source_hash_validation` |
| G5 `G5_EXECUTION_LOCK.json` | exact pointers `/schema_version`, `/lock_id`, `/created_at_utc`, `/contains_held_out_results`, `/confirmation_results_inspected`, `/target_worktree/branch`, `/target_worktree/pre_lock_head_commit`, `/target_worktree/required_execution_parent_commit`, `/target_worktree/dirty`, `/target_worktree/upstream_ahead`, `/target_worktree/upstream_behind`, `/runtime/runtime_lock_sha256`, `/runtime/python_version` | `authority_identity` |
| G5 `G5_EXECUTION_LOCK.json` | exact pointers `/source_plan/sha256`, `/g5a_tooling/tooling_commit`, `/runtime/runtime_lock_sha256`; prefixes `/g5a_tooling/file_hashes`, `/g4_seal/artifact_hashes`, `/g4_seal/case_json_sha256_by_id` | `source_hash_validation` |
| G5 `G5_EXECUTION_LOCK.json` | exact pointers `/source_plan/integrated_source_commit`, `/source_plan/implementation_commit_a`, `/source_plan/preregistration_commit_b2`, `/source_plan/seal_commit_c`; prefix `/g4_seal` | `lineage_link` |
| G5 `G5_EXECUTION_LOCK.json` | exact pointers `/contains_held_out_results`, `/confirmation_results_inspected`; prefix `/execution_schedule` | `method_stage_projection` |
| G5 `G5_EXECUTION_LOCK.json` | exact pointers `/output_roots/raw_output_root_relative`, `/output_roots/must_not_exist_before_execution`, `/output_roots/pre_execution_probe`, `/output_roots/must_be_outside_frozen_bundle`, `/output_roots/frozen_bundle_root_relative`; prefix `/execution_schedule` | `output_root_containment_projection` |
| G5 `G5_RAW_HASH_MANIFEST.json` | exact pointers `/schema_version`, `/freeze_id`, `/case_count`; prefix `/cases` | `source_hash_validation` |
| G5 `G5_RESULT_SUMMARY.json` | raw bytes only; JSON parsing prohibited | `source_hash_validation` |
| G5 `G5_SCORING_ERRATUM.json` | exact pointers `/schema_version`, `/freeze_id`, `/locked_runtime_and_execution/branch`, `/locked_runtime_and_execution/g5_a_tooling_commit`, `/locked_runtime_and_execution/g5_b_execution_lock_commit`, `/locked_runtime_and_execution/post_execution_evidence_commit/full`, `/locked_runtime_and_execution/python_version` | `authority_identity` |
| G5 `G5_SCORING_ERRATUM.json` | prefix `/locked_hashes` | `source_hash_validation` |
| G5 `G5_SCORING_ERRATUM.json` | exact pointers `/freeze_id`, `/locked_runtime_and_execution/g5_a_tooling_commit`, `/locked_runtime_and_execution/g5_b_execution_lock_commit`, `/locked_runtime_and_execution/post_execution_evidence_commit/full` | `lineage_link` |
| G6-R `G6_HISTORICAL_REPLAY_LOCK_R3.json` | exact pointers `/schema_version`, `/study_role`, `/no_confirmation_use`, `/runtime/python_version`, `/published_ref`, `/published_head`, `/published_tree` | `authority_identity` |
| G6-R `G6_HISTORICAL_REPLAY_LOCK_R3.json` | exact pointer `/default_estimand_spec_sha256`; prefixes `/historical_g4/artifact_hashes`, `/g6_code_file_hashes`, `/original_g5` | `source_hash_validation` |
| G6-R `G6_HISTORICAL_REPLAY_LOCK_R3.json` | prefixes `/historical_g4`, `/original_g5` | `lineage_link` |
| G6-R `G6_HISTORICAL_REPLAY_LOCK_R3.json` | exact pointers `/case_ids`, `/run_labels`, `/study_role`, `/no_confirmation_use`, `/retry_enabled`, `/third_run_allowed`, `/same_case_overlap_allowed`, `/nested_scientific_parallelism_allowed`, `/stale_lease_policy`; prefix `/execution_schedule` | `method_stage_projection` |
| G6-R `G6_HISTORICAL_REPLAY_LOCK_R3.json` | exact pointer `/default_estimand_spec_sha256`; prefix `/default_estimand_spec` | `metric_projection` |
| G6-R `G6_HISTORICAL_REPLAY_LOCK_R3.json` | exact pointers `/output_root`, `/case_ids`, `/run_labels`, `/retry_enabled`, `/third_run_allowed`, `/same_case_overlap_allowed`, `/nested_scientific_parallelism_allowed`; prefix `/execution_schedule` | `output_root_containment_projection` |
| G6-R `G6_HISTORICAL_REPLAY_R3_RAW_HASH_MANIFEST.json` | exact pointer `/output_root` | `output_root_source_equality_validation` |
| G6-R `G6_HISTORICAL_REPLAY_R3_RAW_HASH_MANIFEST.json` | exact pointers `/schema_version`, `/manifest_version`, `/study_role`, `/code/published_ref`, `/code/head`, `/code/tree`, `/code/dirty_state`, `/file_count`, `/total_bytes`, `/canonical_path_sha256_map_hash`; prefixes `/canonicalization`, `/excluded_files`, `/relative_path_to_sha256` | `source_hash_validation` |
| G6-R failure ledger and report | raw bytes only; JSON parsing prohibited | `source_hash_validation` |

The authorization serializes every matrix row independently. Any parse/read
outside the matrix, or use of a permitted value for a different purpose, is a
capability refusal. In particular, G5 `/cases/*/canonical_json_sha256`,
`/cases/*/raw_stdout_sha256`, `/cases/*/stderr_raw_sha256`, and reproducibility
statuses, plus every G6-R `/relative_path_to_sha256` hash value, may be read only
inside `source_hash_validation`. Result hashes, stdout/stderr hashes, record
hashes, status values, raw-manifest relative-path keys, file counts, and byte
counts never enter any comparison-projection preimage. G5/G6-R scientific
result, comparison, mechanism, retained-failure, score, stderr, and stdout
payloads remain unreadable. `raw_bytes_only` permits hashing the file bytes and
prohibits JSON parsing.

`allowed_historical_builder_symbols` is the empty array in v1. Generated G4
route/model projections use reviewed static normalizer mappings keyed by frozen
`generator_id`, locked G4 source hashes, and exact protocol parameters; the
normalizer must not import or execute `g4_instances`. Unit tests may separately
cross-check those pure mappings against the three input-only builders, but test
outputs are not normalization evidence. Adding a runtime builder symbol requires
new written-spec review and a schema-version bump.

`allowed_operations` is exactly `read_authority_bytes`,
`parse_allowed_json_pointers`, `verify_source_hashes`,
`parse_historical_decimal_exactly`, `apply_static_input_projection`,
`canonicalize_projection_v2`, `compute_sha256`,
`write_normalization_manifest`, and `write_fingerprint_record`.
`allowed_project_imports` is exactly
`ims_deadlock.g6b_retired_normalizer`, `ims_deadlock.g6b_canonical_json`, and
`ims_deadlock.g6b_governance`, including transitive project imports.
`forbidden_imports` is exactly `ims_deadlock.analysis`, `ims_deadlock.cases`,
`ims_deadlock.ctmc`, `ims_deadlock.engine`, `ims_deadlock.g4_instances`,
`ims_deadlock.g4_protocol`, `ims_deadlock.g5_scoring`,
`ims_deadlock.historical_replay`, `ims_deadlock.terminal_classes`,
`ims_deadlock.confirmation`, and `ims_deadlock.cli`.
`forbidden_calls` is exactly `enumerate_stable_lts`, `partition_stable_lts`,
`certify_absorption_domain`, `derive_absorbing_ctmc`,
`AbsorbingCTMC.solve`, `engine.simulate`, `g4_protocol.run_after_freeze`,
`g4_protocol.main`, `g5_scoring.score_case`, `g5_scoring.score_run`,
`g5_scoring.main`, and `historical_replay.main`.

The schema-only bundle contains no authorized instance. Its allowlist is limited
to reading the exact immutable inventory, duplicate-key validation, source-hash
verification, exact-decimal parsing, approved input-only projection, canonical
hashing, and writing the normalization manifest/fingerprint records to the
listed governance root. Its denylist includes LTS enumeration, terminal
classification, target certification, CTMC/DES, scoring, scientific-summary
generation, output inspection beyond listed identity/hash fields, and evidence
mutation.

### 10.4 Comparison report and fail-closed semantics

Every `per_dimension_comparison` has exactly `comparison_id`, `bundle_id`,
`new_fingerprint_record_hash`, `retired_fingerprint_record_hash`, `dimension`,
`projection_kind`, `new_subject_type`, `new_subject_id`,
`retired_authority_id`, `retired_lineage_id`,
`new_comparison_projection_sha256_or_null`,
`retired_comparison_projection_sha256_or_null`, `comparison_policy`,
`comparison_status`, `semantic_lineage_audit_ref_or_null`,
`reuse_authorization_ref_or_null`, `refusal_reason_code_or_null`, and
`comparison_record_sha256`.

Every referenced `semantic_lineage_audit` has exactly `schema_version`,
`audit_id`, `new_case_unit_id`, `retired_authority_id`,
`retired_lineage_id`, `new_case_content_projection_sha256`,
`retired_case_content_projection_sha256`, `lineage_declaration_sha256`,
`typed_graph_canonicalizer_version`, `typed_graph_isomorphism_status`,
`parameter_transform_audit_status`, `prediction_semantic_reuse_status`,
`declared_provenance_consistency_status`,
`outcome_driven_adjustment_status`, `construction_log_sha256`, `audit_status`,
`reason_codes`, `review_artifact_hash`, and `audit_record_sha256`. Status and
reason values are enums; no free-form similarity score or post-outcome rationale
is allowed. `pass_distinct` is invalid unless the lineage audit is `passed`.
Paraphrasing a retired question, hypothesis, falsifier, or scoring rule without a
scientific-content change is `prediction_semantic_reuse`, not distinctness.

`input_overlap_report_required_fields` is exactly `schema_version`, `report_id`,
`bundle_id`, `input_overlap_authority_lock_sha256`,
`sealed_bundle_manifest_sha256`, `normalization_manifest_sha256`,
`declared_case_unit_ids`, `declared_method_observation_ids`,
`declared_method_companion_group_ids`, `new_fingerprint_record_hashes`,
`retired_fingerprint_record_hashes`, `comparison_record_hashes`,
`semantic_lineage_audit_hashes`, `metric_schema_reuse_record_hashes`,
`per_case_status`, `per_method_status`, `per_companion_group_status`,
`unique_retired_lineage_count`, `inherited_record_count`,
`duplicate_lineage_record_count`, `planned_case_count`, `passed_case_count`,
`refused_case_count`, `pending_case_count`, `planned_method_count`,
`passed_method_count`, `refused_method_count`, `pending_method_count`,
`planned_companion_group_count`, `passed_companion_group_count`,
`refused_companion_group_count`, `pending_companion_group_count`,
`admission_policy_version`, `report_status`, `ledger_head_hash`, and
`report_sha256`.

Every declared ID array is unique/sorted; each per-subject status map has exactly
its declared key set; planned/pass/refuse/pending partitions are disjoint and
count-reconciled at each subject level; every comparison/audit/reuse-record hash
is owned by exactly one declared relation; and inherited/duplicate records map
to one unique retired lineage. `admission_status` is exactly `admitted`,
`refused`, or `pending`. `report_status` is exactly
`complete_all_admitted`, `complete_with_refusals`, or `incomplete_refused`.
Either complete status requires all three pending counts to be zero;
`complete_all_admitted` additionally requires every refused count to be zero,
and `complete_with_refusals` requires at least one refused count. Only a complete
status can advance the gate; `incomplete_refused` cannot.
Every value in a per-subject status map has exactly `subject_type`, `subject_id`,
`required_fingerprint_record_hashes`, `required_comparison_record_hashes`,
`required_lineage_audit_hashes`, `required_reuse_record_hashes`,
`admission_status`, `refusal_reason_codes`, and `ledger_entry_ids`; all arrays
are unique/sorted and the embedded subject ID equals its map key.

Local absence of remote-only authority material is never non-overlap evidence.
A missing authority, missing source field, unknown canonicalization/normalizer
version, semantic-lineage ambiguity, unauthorized builder, hash mismatch, or
unreconstructable required projection is a refusal. A valid
`not_applicable_retired_stage` is permitted only where the v2 source mapping
explicitly declares the dimension logically absent, such as the G4 output root;
it is not converted to `pass_distinct`.

The audit is batch-complete. Every sealed case, method, and companion-group
subject receives every policy-required result. A report with missing subjects,
missing dimensions, unexpanded inheritance, duplicate lineage counted twice,
or any of `pending_case_count`, `pending_method_count`, or
`pending_companion_group_count` greater than zero is incomplete and cannot
advance. Refused units remain
in the denominator and ledger. Revision after refusal requires a new identity
or an explicit supersession record with old/new hashes and reason codes.

## 11. Target-Certification Preflight Capability

### 11.1 Dedicated entrypoint and dependency boundary

Implementation must add a dedicated G6-B target-certification entrypoint whose
maximum capability is:

`load sealed input -> enumerate_stable_lts -> partition_stable_lts -> certify_absorption_domain -> emit certificate/refusal`.

The entrypoint must stop before CTMC generator construction. It must not call
`derive_absorbing_ctmc`, import or call a CTMC solver, invoke DES, execute G5 or
G6-R replay, score a theorem, or use any quantitative-output writer. Capability
separation must be enforced by module dependencies and tests, not comments
alone.

### 11.2 Preflight runtime lock

`target_certification_runtime_lock` is created only after the input overlap
audit is complete and before preflight authorization. It binds:

- exact repository HEAD/tree and sealed bundle hash;
- logical Python runtime ID, executable byte hash, version, and
  environment/package identity, with no committed absolute executable path;
- source-path override and cache/bytecode policy;
- target-certification entrypoint and allowed-command manifest hashes;
- target-certificate schema and canonicalization versions;
- case-unit scope and expected input hashes;
- preflight evidence-root reservation;
- wall-time, memory, CPU, storage, state-bound, and failure budgets;
- transcript, exit-code, and filesystem-diff capture policy; and
- current failure-ledger head.

It contains no science-authorization field. It does not authorize execution.

### 11.3 Preflight authorization artifact

The separate `target_certification_preflight_authorization` references the
runtime-lock hash and names:

- exact bundle and case-unit IDs;
- exact sealed input hashes;
- one allowed entrypoint and command shape;
- allowed operations and output schemas;
- forbidden calls and side effects;
- resource budgets and stop conditions;
- preflight evidence-root reservation;
- transcript/hash-manifest requirements; and
- authorization issuer, review artifact, and UTC timestamp.

Blanket wording such as "authorize G6-B science" is invalid. The authorization
does not cover quantitative methods or later revisions.

The preflight evidence root has two explicit states. Before the authorized
command it is `reserved_not_materialized` and must be absent or empty. The
authorized preflight command may change it to
`materialized_by_target_certification_only`, after which its exact inventory is
limited to per-case certificate/refusal records, the batch manifest, command
transcript/stderr/exit-code captures, the before/after filesystem manifests,
the hash manifest, and append-only preflight failure-ledger entries, with the
exact role/schema map in Section 4. This root is not the quantitative
`output_root_reservation_sha256` dimension and cannot
contain CTMC/DES/metric results.

Within Barrier A, `append_preflight_failure_ledger` means creating immutable,
hash-chained `failure_ledger_entry` objects only inside that exact evidence
root. It never edits `cases/discovery/g6b/failure_ledger.json`, a retired
authority, a sealed input, or another governance/output root. The batch
`ledger_head_hash` is the final entry hash, or the launch ledger-head hash when
no entry was required. Any later incorporation of those entry hashes into a
bundle-level governance ledger is a separate data-only reviewed transition and
is not part of the preflight command.

### 11.4 Allowed result fields

The target-certification result may contain only the fields required to audit
eligibility and identity:

- bundle/case/input/runtime/authorization identities;
- complete/nontruncated/provenance verification status;
- declared state and transition bounds plus observed completeness counts;
- typed target labels and versioned estimand identity;
- `state_space_hash`;
- `partition_hash`;
- `rate_manifest_hash`;
- `positive_rate_graph_hash`;
- `policy_filter_hash`;
- `absorption_domain_hash`;
- `estimand_id`;
- certificate version/status/hash and canonical certificate payload;
- structured refusal reason codes and details;
- command/transcript/stderr/exit-code hashes;
- filesystem before/after manifest hashes; and
- ledger entry references.

The full certificate may expose `S_T`, unselected closed SCCs, and their
reverse basin because those values are necessary to audit the certificate.
They are preflight eligibility evidence. They must not populate theorem or
metric result fields, and they cannot be used to rewrite the sealed prediction.

### 11.5 Forbidden outputs and side effects

The preflight runner and schema must reject or prove absent:

- an `AbsorbingCTMC` generator payload;
- committor, completion probability, or deadlock probability;
- mean absorption time or other time-to-event estimate;
- sensitivity or derivative payloads;
- Doob-h transforms or controlled generators;
- DES trajectories, samples, seeds consumed, or estimates;
- metric observations;
- theorem support/falsification or scientific scoring;
- scientific summaries, plots, tables, or manuscript claims;
- quantitative output-root creation or inspection;
- G5/G6-R reruns or evidence mutation;
- G6-B `PASS` or G6-C/D/E state changes; and
- unlisted files outside the authorized preflight evidence root.

The allowed-command manifest is positive, not merely a blacklist. A post-run
tracked/untracked filesystem diff guard and evidence-root inventory must show
that only files whose roles belong to the exact Section 4 file-role array were
written, that every file validates against `file_role_to_schema_id`, and that
all conditional role cardinalities reconcile with the batch status and counts.

### 11.6 Batch completeness and failure semantics

Preflight operates on the entire sealed, overlap-passed scope in one declared
batch. Every scoped case unit must end as `TARGET_CERTIFIED` or
`TARGET_REFUSED`. A process crash, missing record, state-bound truncation,
unavailable transition branch, provenance failure, rate drift, target drift,
policy drift, non-almost-sure global domain, unexpected file, or
`pending_count > 0` makes the batch incomplete or refused.

No partial successful subset may be presented as the whole batch. Certified
units may become candidates for a later quantitative scope only after the
complete report retains all refused units and a separate review approves the
aggregation. Mandatory-control failure blocks quantitative authorization for
the tranche; an expected control classification/refusal is not itself a
control failure.

Any later quantitative scope restricted to certified survivors must report the
original sealed denominator, every overlap/certificate refusal and supersession,
the frozen selection rule, and the resulting claim boundary. It cannot describe
the survivor scope as the originally planned full tranche or make a full-tranche
performance/generalization claim unless every originally planned unit was
certified, target-matched, and included under the same frozen rule.

## 12. Exact/DES Same-Target Lock

After target-certification review, each exact/DES companion group must have a
frozen `same_target_lock` that references:

- one `case_unit_id`;
- both distinct `method_observation_id` values;
- selected bad labels `D_global` and `D_local`;
- selected success label `F`;
- versioned target/estimand schema;
- `state_space_hash`, `partition_hash`, `rate_manifest_hash`,
  `positive_rate_graph_hash`, `policy_filter_hash`, and
  `absorption_domain_hash`;
- certificate artifact hash and `estimand_id`;
- exact and DES stopping-rule hashes;
- shared metric-schema hash and its reuse authorization; and
- distinct method-specific random-stream/output-root-reservation records.

Exact/DES target mismatch is a method-level refusal. It cannot be hidden by a
case-level or bundle-level pass and cannot be repaired in place after result
inspection.

## 13. Three-Level State Model

In the schema-only migration, `review_state.json` remains the reviewed state
vocabulary/default and stays at `ROW_FAMILY_BUNDLE_IMPLEMENTED`. A later
approved bundle instance records actual progression in
`governance/{bundle_id}/bundle_state.json`, validated against that vocabulary
and bound to the immutable object manifest. The first schema tranche creates no
`bundle_state.json` instance.

### 13.1 Bundle states

| State | Aggregate meaning | Authorizes execution |
| --- | --- | --- |
| `SPEC_DRAFTED` | Design document exists. | No |
| `ROW_FAMILY_BUNDLE_IMPLEMENTED` | Schema-only bundle/validators exist. | No |
| `DATA_ONLY_VALIDATION_PASSED` | Structural validation passes. | No |
| `ADVERSARIAL_ROW_FAMILY_REVIEW_PASSED` | Review permits a separate case-construction plan. | No |
| `CASE_CONSTRUCTION_PLAN_APPROVED` | Exact bounded construction scope is approved. | Case construction only |
| `CASE_INPUTS_SEALED_NO_EXECUTION` | All planned inputs/methods/predictions are sealed and counted. | No enumeration or science |
| `RETIRED_AUTHORITY_NORMALIZATION_AUTHORIZATION_RECORDED` | Exact immutable sources, normalizer, read-only operations, and governance output root are authorized. | Only listed data-only normalization |
| `RETIRED_AUTHORITY_NORMALIZATION_COMPLETE` | Source inventory and every required retired fingerprint are verified, lineage-linked, or fail-closed. | No enumeration or science |
| `INPUT_OVERLAP_AUDIT_COMPLETE` | Every sealed subject has pass/refusal status and counts reconcile. | No enumeration or science |
| `TARGET_CERTIFICATION_RUNTIME_LOCK_RECORDED` | Exact Barrier A source/runtime/scope/evidence policy is locked. | No |
| `TARGET_CERTIFICATION_PREFLIGHT_AUTHORIZATION_RECORDED` | Exact Barrier A command and case scope is authorized. | Only the listed target-certification preflight |
| `TARGET_CERTIFICATION_PREFLIGHT_COMPLETE` | Every overlap-passed case in the declared preflight scope has a certificate/refusal; excluded/refused cases remain accounted for. | No quantitative science |
| `QUANTITATIVE_RUNTIME_LOCK_COMPLETE` | Fresh quantitative runtime/scope lock exists. | No |
| `QUANTITATIVE_EXECUTION_AUTHORIZATION_RECORDED` | Exact listed case/method scope is authorized. | Only listed quantitative scope |
| `QUANTITATIVE_EXECUTION_RECORDED` | Authorized executions/refusals are all recorded. | No additional execution |
| `BUNDLE_CLOSED_WITH_FAILURES` | All objects terminal; adverse/refused evidence is retained. | No |
| `BUNDLE_ELIGIBLE_FOR_BOUNDARY_REVIEW` | All objects terminal and evidence package is ready for a separate G6-B boundary verdict. | No |

The bundle state is forward-only. It must include `planned_count`,
`passed_count`, `refused_count`, `superseded_count`, and `pending_count`, each
reconciled against the immutable manifest. "Bundle passed" is not a valid
machine or manuscript claim without a named gate, exact scope, and counts.

There is no durable `PREFLIGHT_RUNNING` success state. An attempted or
interrupted command is recorded in the transcript and failure ledger while the
bundle remains at the authorization-recorded gate. The bundle advances to
`TARGET_CERTIFICATION_PREFLIGHT_COMPLETE` only when every scoped case has a
terminal certificate/refusal record and the batch counts reconcile.

### 13.2 Case-unit states

Allowed case-unit states are:

1. `CASE_UNIT_PLANNED`;
2. `CASE_UNIT_SEALED_NO_EXECUTION`;
3. `CASE_UNIT_OVERLAP_PASSED`;
4. `CASE_UNIT_OVERLAP_REFUSED`;
5. `CASE_UNIT_TARGET_PREFLIGHT_AUTHORIZED`;
6. `CASE_UNIT_TARGET_CERTIFIED`;
7. `CASE_UNIT_TARGET_REFUSED`;
8. `CASE_UNIT_RUNTIME_LOCKED`;
9. `CASE_UNIT_QUANT_AUTHORIZED`;
10. `CASE_UNIT_EXECUTED`;
11. `CASE_UNIT_RETAINED_REFUSED`; and
12. `CASE_UNIT_REVISED_SUPERSEDED`.

Refusal and supersession are retained terminal branches. They are not deletion
instructions.

### 13.3 Method-observation states

Allowed method states are:

1. `METHOD_PLANNED`;
2. `METHOD_SEALED_NO_OUTPUT`;
3. `METHOD_TARGET_MATCH_VERIFIED`;
4. `METHOD_TARGET_MISMATCH_REFUSED`;
5. `METHOD_RUNTIME_READY`;
6. `METHOD_AUTHORIZED`;
7. `METHOD_EXECUTED`;
8. `METHOD_RETAINED_REFUSED`; and
9. `METHOD_REVISED_SUPERSEDED`.

Every method belongs to exactly one case unit. A method refusal cannot be
hidden by a case-unit pass; a case-unit refusal cannot be hidden by a bundle
gate.

### 13.4 Aggregate predicates

The validator must compute, rather than infer from prose:

- `bundle_schema_valid`: all versioned schema files exist and validate, with no
  actual case/science claim;
- `bundle_sealed`: all manifest case units and methods are sealed, no objects
  are missing, and the manifest hash is frozen;
- `overlap_audit_complete`: every sealed subject has terminal pass/refusal
  status, the retired normalization manifest is complete and authorized, unique
  lineages are deduplicated, every refusal is ledgered, and
  `pending_case_count = 0`, `pending_method_count = 0`, and
  `pending_companion_group_count = 0`;
- `preflight_scope_ready`: the clean target-certification runtime-lock hash and
  preflight-authorization hash both match the sealed bundle, exact case scope,
  allowed-command manifest, evidence-root contract, and current ledger head;
- `target_preflight_complete`: `preflight_scope_ready` was true at launch,
  every overlap-passed case in the declared scope is certified/refused, every
  result is ledger-linked, and `pending_count = 0`;
- `execution_scope_ready`: only certified cases and target-matched methods are
  listed, all controls satisfy frozen guards, and refused/superseded objects
  remain outside the execution scope but inside the bundle manifest; and
- `bundle_boundary_review_eligible`: all planned objects are terminal, counts
  reconcile, ledgers are current, and no unauthorized output field exists.

## 14. Refusal, Revision, and Negative-Evidence Rules

`refusal_code_vocabulary_version` is exactly
`ims-deadlock/g6b-refusal-codes/v1`. The vocabulary is closed and partitioned
into these exact, lexicographically sorted arrays:

- `cross_gate_refusal_codes`: `batch_incomplete`,
  `canonicalization_violation`, `missing_hash`, `outcome_leakage`,
  `runtime_identity_drift`, `sealed_input_drift`, `self_hash_mismatch`;
- `construction_refusal_codes`: `output_root_reuse_or_materialized`,
  `subject_id_contaminated_projection`, `unauthorized_case_creation_attempt`,
  `unclassified_scientific_input`;
- `normalization_refusal_codes`: `capability_call_violation`,
  `capability_import_violation`, `duplicate_lineage_miscount`,
  `missing_normalization_authorization`, `missing_retired_authority`,
  `retired_authority_hash_mismatch`, `retired_normalizer_error`,
  `retired_projection_unreconstructable`, `source_field_read_violation`,
  `unauthorized_retired_normalization_attempt`;
- `overlap_refusal_codes`: `metric_reuse_unauthorized`, `overlap_hit`,
  `output_root_reuse_or_materialized`, `prediction_semantic_reuse`,
  `random_stream_disjointness_unproved`, `random_stream_overlap`,
  `rename_or_cosmetic_shift_detected`, `semantic_identity_reuse`,
  `semantic_lineage_ambiguous`, `subject_id_contaminated_projection`,
  `unclassified_scientific_input`;
- `preflight_refusal_codes`: `capability_call_violation`,
  `capability_import_violation`, `certificate_schema_violation`,
  `command_scope_violation`, `filesystem_scope_violation`,
  `incomplete_stable_lts`, `non_almost_sure_absorption_domain`,
  `policy_filter_drift`, `rate_manifest_drift`, `selected_target_drift`,
  `state_bound_truncation`, `unauthorized_target_certification_attempt`,
  `unavailable_transition_branch`, `unexpected_preflight_side_effect`,
  `unverified_lts_provenance`; and
- `quantitative_refusal_codes`: `exact_des_target_mismatch`,
  `failed_negative_control`, `output_root_reuse_or_materialized`,
  `quantitative_scope_violation`, `retry_stop_policy_violation`,
  `same_target_lock_stale`, `unauthorized_quantitative_execution_attempt`.

Repeated codes across groups are intentional shared semantics, not aliases.
Each schema's exact allowed set is the mathematical set union of
`cross_gate_refusal_codes` and its named gate groups: construction uses
`construction`; retired normalization/overlap uses `normalization` plus
`overlap`; target certification uses `preflight`; quantitative authorization
uses `quantitative`; the append-only failure ledger accepts the union of all six
arrays. No unlisted code, free-form fallback, or extension namespace is valid
without a vocabulary-version and schema-version bump plus written-spec review.

Every refusal records bundle/case/method subject, gate, old identity, reason,
evidence hashes, affected hypotheses, comparability status, and timestamp.
Failures and negative controls are never deleted, collapsed into summaries, or
retroactively relabelled as support.

A revised case after overlap or certification refusal requires a new
`case_unit_id` unless the change is provably administrative and identity-
preserving under a named schema rule. A scientific-identity change requires
new affected hashes and an explicit `supersedes` link. A revised method requires
a new method ID and preserves the refused predecessor. Prior failure remains
citable boundary evidence.

## 15. Quantitative Runtime Lock and Authorization

After target-certification review and same-target locking, a fresh
`quantitative_execution_runtime_lock` binds:

- exact source/runtime/environment identity;
- sealed bundle and target-certificate manifest hashes;
- exact authorized candidate case/method IDs;
- exact/DES same-target lock hashes;
- random-stream and output-root reservations;
- allowed quantitative commands;
- resource/run/retry/stop budgets;
- capture, canonicalization, and reproducibility rules; and
- current failure-ledger head.

The runtime lock does not authorize execution. A separate
`quantitative_execution_authorization` must reference it and enumerate exact
case units, methods, certificate hashes, output-root policy, allowed commands,
run roles, and terminal stop conditions. It cannot authorize an unspecified
class such as "all G6-B science".

No quantitative authorization is valid if the sealed denominator changed, a
required control failed, a certificate is missing/stale, exact/DES target
identity drifts, the runtime lock is stale, a refused object disappeared, or
the ledger is not current.

## 16. Versioning and Planned Artifact Surface

### 16.1 Current reviewed artifacts

The top-level G6-B bundle remains the existing exact five files:

- `cases/discovery/g6b/protocol.json`;
- `cases/discovery/g6b/estimand_schema.json`;
- `cases/discovery/g6b/independence_schema.json`;
- `cases/discovery/g6b/negative_controls.json`; and
- `cases/discovery/g6b/failure_ledger.json`.

The nested `structural_discovery_v1` bundle remains the existing exact eight
files at the audited base:

- `row_family_protocol.json`;
- `identity_schema.json`;
- `row_family_matrix.json`;
- `reuse_matrix.json`;
- `overlap_report_schema.json`;
- `runtime_lock_schema.json`;
- `review_state.json`; and
- `failure_ledger.json`.

Current validators are
`src/ims_deadlock/g6b_protocol.py` and
`src/ims_deadlock/g6b_row_family_protocol.py`; current focused tests are
`tests/test_g6b_protocol.py` and
`tests/test_g6b_row_family_protocol.py`.

### 16.2 Schema migration

The implementation plan must version-bump every changed contract rather than
silently changing a reviewed meaning. The expected changes are:

- `protocol.json` to
  `ims-deadlock/g6b-discovery-protocol/v2`, replacing the broad future
  authorization key with typed capabilities while keeping the current instance
  false;
- `independence_schema.json` to
  `ims-deadlock/g6b-independence-schema/v2`, adding fingerprint subjects and
  the non-reuse claim lattice, replacing legacy `output_root` with
  `output_root_reservation_sha256`, and separating comparison projections from
  provenance envelopes;
- `row_family_protocol.json` to
  `ims-deadlock/g6b-row-family-protocol/v2`, registering the expanded exact
  schema file set and typed capabilities;
- `identity_schema.json` to
  `ims-deadlock/g6b-row-family-identity/v2`;
- `overlap_report_schema.json` to
  `ims-deadlock/g6b-row-family-overlap-schema/v2`;
- `runtime_lock_schema.json` to
  `ims-deadlock/g6b-row-family-runtime-lock-schema/v2`;
- `review_state.json` to
  `ims-deadlock/g6b-row-family-review-state/v2`;
- `failure_ledger.json` to
  `ims-deadlock/g6b-row-family-failure-ledger/v2`; and
- `reuse_matrix.json` to
  `ims-deadlock/g6b-row-family-reuse/v2`, assigning reuse rules to case,
  method, and companion-group subjects.

Every changed v2 contract references
`ims-deadlock/g6b-canonical-json/v2` and the null-placeholder self-hash rule from
Section 7.2. Existing G4/G5/G6-R hashes retain their actual historical
canonicalization labels and are never relabelled v2.

The current `ims-deadlock/g6b-estimand-schema/v2` remains unchanged because it
already requires the certified absorption domain and same domain hash. The
negative-control and row-family matrix versions remain unchanged only if their
exact keys and meanings remain byte-for-byte compatible; otherwise they also
receive explicit version bumps. A changed meaning always requires a new
version.

The v1 state `CASE_ARTIFACTS_SEALED_NO_SCIENCE` is replaced in v2 by
`CASE_INPUTS_SEALED_NO_EXECUTION`. The new name is deliberate: target
certification is result-bearing scientific substrate, so the old phrase
`NO_SCIENCE` is too broad. The migration record must map the legacy state name
without treating any current instance as having reached either state.

### 16.3 Planned schema-only files

The first implementation tranche may add only schema/validator/test artifacts.
The planned exact new nested schema filenames are:

- `case_construction_schema.json`;
- `retired_authority_fingerprint_schema.json`;
- `target_certification_schema.json`; and
- `quantitative_authorization_schema.json`.

They live under
`cases/discovery/g6b/row_families/structural_discovery_v1/` and must be added to
the exact nested file manifest. Adding them does not create case instances or
authorizations. Any additional schema filename requires written-spec review
rather than an opportunistic addition during implementation.

The schema-only nested root therefore changes from exact eight JSON files to
exact twelve. Implementation must update `_DOCUMENTS`, `_SCHEMA_VERSIONS`, the
expected `row_family_protocol.json.artifact_paths`, the exact-file-set tests,
and the corresponding review/handoff file inventories together. A validator
that accepts either eight or twelve without an explicit schema version is
invalid.

#### 16.3.1 `case_construction_schema.json` exact shape

Its top-level keys are exactly:

| Key | Value contract |
| --- | --- |
| `schema_version` | `ims-deadlock/g6b-case-construction-schema/v1` |
| `study_role` | `discovery_only` |
| `confirmation_use` | `prohibited` |
| `schema_role` | `schema_only` |
| `current_capability_reference` | `row_family_protocol.json#/typed_capabilities` |
| `prerequisite_bundle_state` | `ADVERSARIAL_ROW_FAMILY_REVIEW_PASSED` |
| `canonicalization_contract` | Exact v2 contract from Section 7.2 |
| `self_hash_finalization_contract` | Exact null-placeholder/DAG contract from Section 7.2 |
| `governance_instance_root_template` | Exact repo-relative governance root from Section 16.4 |
| `case_unit_root_template` | Exact repo-relative case-unit root from Section 16.4 |
| `construction_authorization_required_fields` | Exact field-name array below |
| `sealed_bundle_manifest_required_fields` | Exact field-name array below |
| `case_unit_required_fields` | Exact field-name array below |
| `method_observation_required_fields` | Exact field-name array below |
| `method_companion_group_required_fields` | Exact field-name array below |
| `semantic_lineage_declaration_required_fields` | Exact field-name array below |
| `metric_schema_reuse_record_required_fields` | Exact field-name array from Section 7.8 |
| `fingerprint_record_required_fields` | Exact field-name array from Section 7.1 |
| `fingerprint_subject_map` | Exact eight-key subject map from Section 7 |
| `fingerprint_payload_schemas` | Exact eight projection contracts from Section 7.4 |
| `dimension_dependence_contract` | Exact dependency/correlation and non-independence rules from Sections 7.5 and 7.8 |
| `allowed_input_modes` | Exactly `model_generated_lts`, `explicit_finite_lts_input` |
| `output_root_reservation_contract` | Exact inert-reservation object below |
| `nested_field_contracts` | Exact nested object/array contracts below |
| `recursive_prohibited_fields` | Exact recursive blacklist below |
| `prohibited_instance_fields` | Exact outcome/certificate/authorization blacklist below |
| `refusal_code_vocabulary_version` | `ims-deadlock/g6b-refusal-codes/v1` |
| `refusal_reason_codes` | Exact union of Section 14 cross-gate and construction arrays |
| `schema_does_not_authorize_case_creation` | `true` |

`construction_authorization_required_fields` is exactly:
`schema_version`, `artifact_id`, `capability`, `authorized`, `bundle_id`,
`case_unit_ids`, `method_observation_ids`, `source_head`, `source_tree_hash`,
`approved_plan_artifact_hash`, `allowed_operations`, `forbidden_operations`,
`review_artifact_hash`, `issued_at_utc`, `invalidated_by_identity_drift`, and
`artifact_sha256`. The only valid capability is `case_construction`; the
schema-only file contains no instance with `authorized = true`.

`sealed_bundle_manifest_required_fields` is exactly:
`schema_version`, `bundle_id`, `construction_authorization_hash`,
`planned_case_unit_ids`, `planned_method_observation_ids`,
`planned_method_companion_group_ids`,
`case_unit_record_hashes`, `method_observation_record_hashes`,
`method_companion_group_record_hashes`, `mandatory_control_ids`,
`fingerprint_record_hashes`,
`sealed_prediction_hashes`, `semantic_lineage_declaration_hashes`,
`metric_schema_hashes`,
`quantitative_output_root_reservations`, `planned_case_unit_count`,
`planned_method_count`, `planned_companion_group_count`, and `manifest_sha256`.
All ID arrays are unique and sorted. Every record-hash map has exactly the same
key set as its planned ID array; every count equals the corresponding array
length. Sealed-prediction and semantic-lineage maps have exactly the planned
case-unit key set; metric-schema maps have exactly the planned companion-group
key set; output-root-reservation maps have exactly the planned method key set.

`case_unit_required_fields` is exactly:
`schema_version`, `bundle_id`, `case_unit_id`, `family_id`, `input_mode`,
`structural_family_role`, `negative_control_id_or_null`, `case_artifact_paths`,
`case_content_sha256`, `state_snapshot_sha256`, `route_signature_sha256`,
`parameter_tuple_sha256`, `sealed_prediction_sha256`, `rate_manifest_ref`,
`policy_declaration_ref`, `selected_target_ref`, `control_declaration_ref`,
`state_bound`,
`state_snapshot_payload_schema_version`, `state_snapshot_nesting_relation`,
`state_snapshot_parent_case_content_sha256`, `fingerprint_record_hashes`,
`semantic_lineage_declaration_hash`, `method_observation_ids`, and
`case_unit_state`. `state_snapshot_nesting_relation` is exactly
`declared_subidentity_of_case_content`; the parent hash must equal the same
record's `case_content_sha256`.

`method_observation_required_fields` is exactly:
`schema_version`, `bundle_id`, `method_observation_id`, `case_unit_id`,
`method_companion_group_id`, `method_role`,
`random_stream_manifest_sha256`, `output_root_reservation_sha256`,
`metric_schema_sha256`, `fingerprint_record_hashes`, `stopping_rule_ref`,
`des_stopping_rule_ref_or_null`, and `method_state`.

`method_companion_group_required_fields` is exactly:
`schema_version`, `bundle_id`, `method_companion_group_id`, `case_unit_id`,
`member_method_observation_ids`, `member_method_roles`, `metric_schema_ref`,
`metric_schema_sha256`, `same_target_required`, `allowed_reuse_reason_code`,
`reuse_authorization_ref_or_null`, `evidence_counting_rule`,
`fingerprint_record_hashes`, and `companion_group_state`. Members are unique and
sorted; each belongs to the same case unit; exact/DES companions are counted as
one case unit and distinct method observations, never independent cases. For an
exact/DES group, there are exactly two member IDs and
`member_method_roles` is a key-closed map assigning exactly one
`exact_companion` and one `des_companion`.

Every output-root reservation instance has exactly `projection_schema_version`,
`bundle_id`, `case_unit_id`, `method_observation_id`, `run_role`,
`logical_root_id`, `repo_relative_posix_path`, `reserved`, `materialized`, and
`reservation_sha256`. `output_root_reservation_contract` has exactly
`deterministic_template_expansion_required = true`, `reserved = true`,
`materialized = false`, `absolute_path_prohibited = true`,
`fallback_path_prohibited = true`, and
`filesystem_inspection_before_quantitative_authorization = prohibited`.
The method record's `output_root_reservation_sha256` must equal that instance's
validated `reservation_sha256` under the Section 7.2 null-placeholder rule.

`case_artifact_paths` has exactly `case_input`, `state_snapshot`,
`route_signature`, `parameter_tuple`, `rate_manifest`, `policy_declaration`,
`selected_target_declaration`, `control_declaration`, `sealed_prediction`,
`semantic_lineage_declaration`, `method_observations`,
`metric_schema`, and `fingerprint_records`; every value is a repo-relative POSIX
path or a sorted array of such paths. Every `*_ref` object has exactly
`repo_relative_posix_path`, `schema_version`, and `content_sha256`.

`allowed_operations` in a case-construction authorization is exactly
`write_sealed_case_input`, `write_input_projection`,
`write_method_declaration`, `write_companion_group_declaration`,
`write_inert_random_stream_manifest`, `reserve_inert_output_root`,
`write_sealed_prediction`, `write_metric_schema`,
`write_semantic_lineage_declaration`, `compute_input_hash`,
`write_sealed_bundle_manifest`, and `append_construction_ledger`.
`forbidden_operations` is exactly `enumerate_states`,
`classify_terminal_sets`, `certify_target`, `construct_ctmc`, `solve_ctmc`,
`run_des`, `score_hypothesis`, `inspect_g6b_output`,
`materialize_quantitative_root`, `write_observation`, and
`advance_scientific_status`.

Every `semantic_lineage_declaration` has exactly `schema_version`,
`declaration_id`, `case_unit_id`, `constructor_role`,
`visible_retired_authority_ids`, `declared_source_template_ids`,
`declared_source_artifact_hashes`, `declared_semantic_parent_ids`,
`declared_transform_codes`, `construction_log_sha256`,
`graph_isomorphism_check_required`, `outcome_driven_tuning_prohibited`,
`review_artifact_hash`, and `declaration_sha256`. Arrays are unique and sorted;
transform codes are versioned enums; no claim of confirmation blindness is
allowed.

All objects and object elements in this schema use `additionalProperties = false`,
recursively. All prohibited instance/result names are rejected at every
depth, not merely at the top level. No bounded text field may contain embedded
JSON, a path, a numeric result, or a key/value serialization.

`prohibited_instance_fields` is exactly: `state_space_hash`, `partition_hash`,
`positive_rate_graph_hash`, `policy_filter_hash`, `absorption_domain_hash`,
`estimand_id`, `metric_observations`, `theorem_prediction_status_observed`,
`execution_result`, and `quantitative_execution_authorized`.

#### 16.3.2 `retired_authority_fingerprint_schema.json` exact shape

Its top-level keys are exactly:

| Key | Value contract |
| --- | --- |
| `schema_version` | `ims-deadlock/g6b-retired-authority-fingerprint-schema/v1` |
| `study_role` | `discovery_only` |
| `confirmation_use` | `prohibited` |
| `schema_role` | `schema_only` |
| `canonicalization_contract` | Exact v2 contract from Section 7.2 |
| `self_hash_finalization_contract` | Exact null-placeholder/DAG contract from Section 7.2 |
| `retired_authority_ids` | Exactly `G4_FREEZE`, `G5_EXECUTION`, `G6_R_REPLAY_R3` |
| `expected_source_inventory` | Exact G4/G5/G6-R paths from Section 10.1 |
| `authority_lock_record_required_fields` | Exact fields from Section 10.2 |
| `authority_source_record_required_fields` | Exact fields from Section 10.2 |
| `fingerprint_record_required_fields` | Exact fields from Section 7.1 |
| `fingerprint_payload_schemas` | Exact projection contracts from Section 7.4 |
| `dimension_status_values` | Exact status list from Section 7.8 |
| `comparison_status_values` | Exact status list from Section 7.8 |
| `normalization_manifest_required_fields` | Exact fields from Section 10.2 |
| `normalization_authorization_required_fields` | Exact fields from Section 10.3 |
| `allowed_use_values` | Exact ten-code allowed-use vocabulary from Section 10.3 |
| `allowed_json_fields_by_source` | Exact pointer-to-use matrix from Section 10.3 |
| `input_overlap_authority_lock_required_fields` | Exact fields from Section 10 introduction |
| `source_worktree_identity_required_fields` | Exact six-field privacy-safe linked-worktree identity from Section 10 introduction |
| `per_dimension_comparison_required_fields` | Exact fields from Section 10.4 |
| `semantic_lineage_audit_required_fields` | Exact fields from Section 10.4 |
| `metric_schema_reuse_record_required_fields` | Exact fields from Section 7.8 |
| `input_overlap_report_required_fields` | Exact fields and count invariants from Section 10.4 |
| `input_overlap_subject_status_values` | Exactly `admitted`, `refused`, `pending` |
| `input_overlap_report_status_values` | Exactly `complete_all_admitted`, `complete_with_refusals`, `incomplete_refused` |
| `retired_subject_type_values` | Exactly `retired_case`, `retired_case_subunit`, `retired_method_observation`, `retired_method_companion_group` |
| `retired_protocol_kind_by_case_id` | Exact nine-key map from Section 10.2 |
| `retired_subject_expansion_contract` | Exact composite-subunit selectors and parent-context rules from Section 10.2 |
| `source_projection_map` | Exact per-authority/per-dimension pointer, transform, status, and refusal map from Section 10.2 |
| `lineage_deduplication_contract` | Inherited/duplicate lineage is compared once and never counted as independent authority |
| `typed_admission_contract` | Exact dimension-specific conjunction from Section 7.8 |
| `recursive_prohibited_fields` | Exact recursive result/output blacklist from this specification |
| `refusal_code_vocabulary_version` | `ims-deadlock/g6b-refusal-codes/v1` |
| `refusal_reason_codes` | Exact union of Section 14 cross-gate, normalization, and overlap arrays |
| `schema_does_not_authorize_normalization` | `true` |

Every dynamic map is key-closed by its owning manifest: authority IDs equal the
declared three-element set; case keys equal the G4 freeze `included_cases` or
the exact G6-R subset as applicable; file keys equal the expected inventory; and
fingerprint keys equal the declared authority/subject/dimension cross-product
after only schema-declared not-applicable branches. Unknown keys, missing keys,
or an unversioned normalizer are invalid.

The schema-only file contains no normalization authorization with
`authorized = true`, no normalization output, and no overlap result.

#### 16.3.3 `target_certification_schema.json` exact shape

Its top-level keys are exactly:

| Key | Value contract |
| --- | --- |
| `schema_version` | `ims-deadlock/g6b-target-certification-schema/v1` |
| `study_role` | `discovery_only` |
| `confirmation_use` | `prohibited` |
| `schema_role` | `schema_only` |
| `current_capability_reference` | `row_family_protocol.json#/typed_capabilities` |
| `prerequisite_bundle_states` | Exact ordered prerequisites through `INPUT_OVERLAP_AUDIT_COMPLETE` |
| `canonicalization_contract` | Exact v2 contract from Section 7.2 |
| `self_hash_finalization_contract` | Exact null-placeholder/DAG contract from Section 7.2 |
| `preflight_runtime_lock_required_fields` | Exact field-name array below |
| `preflight_authorization_required_fields` | Exact field-name array below |
| `allowed_command_manifest_required_fields` | Exact preflight command-manifest fields below |
| `allowed_command_record_required_fields` | Exact preflight command-record fields below |
| `allowed_command_placeholder_codes` | Exact preflight placeholder-code array below |
| `allowed_environment_variable_names` | Exactly `PYTHONDONTWRITEBYTECODE`, `PYTHONPATH` |
| `allowed_operations` | Exact ordered fourteen-code Barrier A array from Section 4 |
| `allowed_output_schema_ids` | Exact sorted eight-ID array from Section 4 |
| `allowed_file_roles` | Exact sorted eleven-role array from Section 4 |
| `file_role_to_schema_id` | Exact eleven-key role map from Section 4 |
| `file_role_cardinality_contract` | Exact status/count-dependent cardinality rules from Section 4 |
| `allowed_result_fields` | Exact field-name array below |
| `allowed_project_imports` | Exact project-module allowlist below |
| `allowed_writer_symbols` | Exact evidence-writer allowlist below |
| `forbidden_imports` | Exact hazardous-module array below |
| `forbidden_calls` | Exact hazardous-call array below |
| `forbidden_result_fields` | Exact quantitative/scoring field array below |
| `nested_field_contracts` | Exact nested contracts below |
| `recursive_prohibited_fields` | Exact recursive blacklist below |
| `preflight_evidence_root_contract` | Exact two-state root contract from Section 11.3 |
| `per_case_result_required_fields` | Exact field-name array below |
| `result_status_values` | Exactly `certified`, `refused` |
| `batch_manifest_required_fields` | Exact field-name array below |
| `batch_status_values` | Exactly `complete_all_certified`, `complete_with_refusals`, `incomplete_refused` |
| `refusal_code_vocabulary_version` | `ims-deadlock/g6b-refusal-codes/v1` |
| `refusal_reason_codes` | Exact union of Section 14 cross-gate and preflight arrays |
| `schema_does_not_authorize_preflight` | `true` |

`preflight_runtime_lock_required_fields` is exactly:
`schema_version`, `runtime_lock_id`, `source_head`, `source_tree_hash`,
`source_dirty_state`, `sealed_bundle_manifest_hash`, `python_runtime_identity`,
`pythonpath_source_hash`,
`bytecode_cache_policy`, `entrypoint_hash`, `allowed_command_manifest_hash`,
`target_certificate_schema_version`, `canonicalization_version`,
`case_unit_ids`, `expected_input_hashes`, `preflight_evidence_root`,
`resource_budget`, `capture_policy`, `failure_budget`, `ledger_head_hash`,
`created_at_utc`, and `runtime_lock_sha256`.

`python_runtime_identity` has exactly `logical_runtime_id`,
`executable_byte_sha256`, `python_implementation`, `python_version`,
`environment_identity_hash`, and `package_lock_hash`. It contains no absolute
path, user name, host name, or private network identifier.

The preflight `allowed_command_manifest` has exactly `schema_version`,
`manifest_id`, `capability`, `source_head`, `source_tree_hash`,
`sealed_bundle_manifest_hash`, `input_overlap_report_sha256`,
`preflight_evidence_root_reservation_sha256`, `declared_command_ids`,
`command_record_hashes`, `command_count`, `placeholder_vocabulary`,
`environment_variable_name_allowlist`, `wildcard_scope_allowed`,
`created_at_utc`, and `manifest_sha256`. Its `schema_version` is exactly
`ims-deadlock/g6b-preflight-allowed-command-manifest/v1`; `capability` is
`target_certification_preflight`; `declared_command_ids` contains exactly the
single preflight command ID; `command_record_hashes` has exactly that key;
`command_count = 1`; and `wildcard_scope_allowed = false`.

The closed, unique, sorted preflight `placeholder_vocabulary` is exactly
`case_scope_manifest`, `preflight_authorization`, `preflight_evidence_root`,
`python_runtime`, `repo_source_root`, and `sealed_bundle_manifest`.
`environment_variable_name_allowlist` is exactly
`PYTHONDONTWRITEBYTECODE`, `PYTHONPATH`; the former resolves only to literal
`1`, and the latter only to the locked `repo_source_root` placeholder. The
manifest is finalized before the runtime lock under the Section 7.2
null-placeholder rule; the runtime lock and authorization must reference the
same `manifest_sha256`, and the manifest cannot reference either downstream
record.

`preflight_authorization_required_fields` is exactly:
`schema_version`, `authorization_id`, `capability`, `authorized`, `bundle_id`,
`case_unit_ids`, `sealed_bundle_manifest_hash`, `runtime_lock_sha256`,
`allowed_entrypoint`, `allowed_command_manifest_hash`, `allowed_operations`,
`allowed_output_schemas`, `forbidden_calls`, `forbidden_side_effects`,
`resource_budget`, `stop_conditions`, `preflight_evidence_root`,
`review_artifact_hash`, `issued_at_utc`, `invalidated_by_identity_drift`, and
`authorization_sha256`. The only valid capability is
`target_certification_preflight`; the schema-only file contains no instance
with `authorized = true`.

The only `allowed_entrypoint` is
`ims_deadlock.g6b_target_preflight.main`. `allowed_operations` is byte-for-byte
the ordered fourteen-code array in Section 4; aliases and reordering are
invalid. `allowed_output_schemas` is byte-for-byte the sorted eight-ID array in
Section 4. The schema's `allowed_file_roles` and `file_role_to_schema_id` are
byte-for-byte the sorted eleven-role array and exact role map in Section 4.
`forbidden_side_effects` is exactly
`write_outside_preflight_root`, `materialize_quantitative_root`,
`write_python_bytecode`, `mutate_retired_evidence`, `mutate_sealed_input`,
`invoke_network`, `invoke_subprocess_outside_manifest`,
`advance_quantitative_state`, and `write_scientific_summary`.

The single `preflight_command_record` has exactly `command_id`, `capability`,
`executable_sha256`, `entrypoint`, `argv_tokens`,
`working_directory_repo_relative`, `environment_variable_allowlist`,
`stdin_policy`, `authorized_case_unit_ids`, `authorized_preflight_root_hash`,
and `command_record_sha256`. It uses literal tokens and schema-declared
placeholders, never a shell string, redirection, or command substitution.
Each `argv_tokens` element is a closed discriminated union: either exactly
`{"token_kind":"literal","value":...}` or exactly
`{"token_kind":"placeholder","placeholder_code":...}`. Literal values are
single argv tokens and may contain no NUL, CR/LF, shell operator, redirection,
or command-substitution syntax; placeholder codes must belong to the exact
preflight vocabulary above. `environment_variable_allowlist` is a key-closed
map for the exact two allowed variable names, using the same literal/placeholder
token union. The record hash must equal its manifest entry.

`preflight_evidence_root` has exactly `root_schema_version`, `bundle_id`,
`repo_relative_posix_path`, `state`, `allowed_file_roles`, and
`reservation_sha256`. `allowed_file_roles` must equal the schema's exact
eleven-role array. Every materialized file must have one declared role, validate
against `file_role_to_schema_id`, and satisfy `file_role_cardinality_contract`;
unknown roles, conditionally missing/excess roles, duplicate ownership, or
schema/role mismatch refuse. Before launch its
state is `reserved_not_materialized`;
after the one allowed command it is
`materialized_by_target_certification_only`.

`allowed_result_fields` is exactly:
`schema_version`, `bundle_id`, `case_unit_id`, `input_identity_hashes`,
`runtime_lock_sha256`, `authorization_sha256`, `result_status`,
`completeness_status`, `state_count`, `transition_count`,
`selected_target_identity`, `state_space_hash`, `partition_hash`,
`rate_manifest_hash`, `positive_rate_graph_hash`, `policy_filter_hash`,
`absorption_domain_hash`, `estimand_id`, `certificate_version`,
`certificate_status`, `certificate_payload_or_null`,
`certificate_payload_sha256_or_null`, `refusal_reason_codes`,
`refusal_details`, `command_transcript_sha256`, `stderr_sha256`, `exit_code`,
`filesystem_before_manifest_sha256`, `filesystem_after_manifest_sha256`, and
`ledger_entry_ids`.

`input_identity_hashes` has exactly `case_content_sha256`,
`state_snapshot_sha256`, `route_signature_sha256`, `parameter_tuple_sha256`,
`sealed_prediction_sha256`, and `fingerprint_record_hashes_sha256`.
`selected_target_identity` has exactly `target_schema_version`,
`selected_bad_classes`, `success_class`, `exact_stopping_rule`,
`des_stopping_rule`, `policy_analysis_class`, and `declaration_sha256`.
`certificate_payload_or_null`, when non-null, must validate against the exact
named certificate schema and may not contain additional fields.

`resource_budget` has exactly `max_wall_clock_seconds`, `max_cpu_seconds`,
`max_memory_bytes`, `max_storage_bytes`, `max_states_per_case`,
`max_transitions_per_case`, `max_cases`, and `max_workers`; integral values are
positive JSON integers and time values use canonical decimal strings.
`capture_policy` has exactly `stdout_capture`, `stderr_capture`,
`command_transcript`, `exit_code_capture`, `filesystem_before_manifest`,
`filesystem_after_manifest`, `hash_manifest`, and `bytecode_write_disabled`,
with boolean or fixed enum values only. `failure_budget` has exactly
`max_case_refusals`, `max_unexpected_exceptions`, `abort_on_capability_leak`,
`abort_on_identity_drift`, and `abort_on_unexpected_file`.
`stop_conditions` is a unique sorted array of exact versioned stop-condition
codes, not shell or prose strings.

`refusal_details` is a typed union keyed by the corresponding refusal reason.
Every variant uses only the applicable subset of these exact keys:
`reason_code`, `phase`, `subject_type`, `subject_id`,
`expected_hash_or_null`, `observed_hash_or_null`, `bound_name_or_null`,
`bound_limit_or_null`, `observed_count_or_null`, `exception_class_or_null`,
`message_code`, and `evidence_refs`. `message_code` is an enum; no variant admits
arbitrary nested data, embedded JSON, quantitative estimates, or free-form
debug payloads.

`per_case_result_required_fields` equals `allowed_result_fields`. A certified
record requires every runtime-derived hash, non-null canonical certificate,
empty refusal codes, and exit code zero. A refused record requires null hashes
that were not safely produced, nonempty versioned reason codes, retained
details, and an exit code consistent with the declared refusal contract.

`batch_manifest_required_fields` is exactly:
`schema_version`, `bundle_id`, `sealed_bundle_manifest_hash`,
`runtime_lock_sha256`, `authorization_sha256`, `declared_case_unit_ids`,
`per_case_result_hashes`, `certified_case_unit_ids`, `refused_case_unit_ids`,
`pending_case_unit_ids`, `planned_count`, `certified_count`, `refused_count`,
`pending_count`, `failure_ledger_entry_ids`, `failure_ledger_entry_count`,
`batch_status`, `transcript_manifest_sha256`, `filesystem_manifest_sha256`,
`ledger_head_hash`, and `batch_manifest_sha256`.

The declared, certified, refused, and pending ID arrays are unique and sorted;
certified, refused, and pending are pairwise disjoint; their union equals the
declared set; and every count equals its array length. The
`per_case_result_hashes` key set equals certified union refused and is a subset
of declared. For either complete batch status, `pending_count = 0` and the
result-hash key set equals declared. `complete_all_certified` additionally has
`refused_count = 0`; `complete_with_refusals` has `refused_count > 0`;
`incomplete_refused` cannot advance the gate. `failure_ledger_entry_ids` is
unique/sorted, its length equals `failure_ledger_entry_count`, and its key set
equals the materialized `failure_ledger_entry` file IDs under the Section 4
cardinality contract.

`allowed_project_imports` is exactly:
`ims_deadlock.g6b_target_preflight`,
`ims_deadlock.g6b_target_artifacts`, `ims_deadlock.g6b_input_loader`,
`ims_deadlock.g6b_lts`, `ims_deadlock.g6b_target_certificate`,
`ims_deadlock.g6b_canonical_json`, `ims_deadlock.g6b_governance`,
`ims_deadlock.model`,
`ims_deadlock.engine`, and `ims_deadlock.certificates`. The implementation may
change this planned list only by written-spec review; transitive project imports
must also belong to the list.

`allowed_writer_symbols` is exactly:
`ims_deadlock.g6b_target_artifacts.write_certificate_record`,
`ims_deadlock.g6b_target_artifacts.write_refusal_record`,
`ims_deadlock.g6b_target_artifacts.write_batch_manifest`,
`ims_deadlock.g6b_target_artifacts.write_capture_record`,
`ims_deadlock.g6b_target_artifacts.write_filesystem_manifest`,
`ims_deadlock.g6b_target_artifacts.write_hash_manifest`, and
`ims_deadlock.g6b_target_artifacts.append_failure_ledger`. Writers must enforce
the exact preflight root and schema allowlist.

`forbidden_imports` is exactly:
`ims_deadlock.cases`, `ims_deadlock.ctmc`, `ims_deadlock.g4_instances`,
`ims_deadlock.g4_protocol`, `ims_deadlock.g5_scoring`,
`ims_deadlock.historical_replay`, `ims_deadlock.confirmation`, and
`ims_deadlock.cli`.

`forbidden_calls` is exactly:
`ims_deadlock.g4_instances.derive_absorbing_ctmc`,
`ims_deadlock.ctmc.AbsorbingCTMC.solve`,
`ims_deadlock.engine.simulate`,
`ims_deadlock.g4_protocol.run_after_freeze`,
`ims_deadlock.g4_protocol.main`,
`ims_deadlock.g5_scoring.score_case`,
`ims_deadlock.g5_scoring.score_run`,
`ims_deadlock.g5_scoring.main`,
and `ims_deadlock.historical_replay.main`. The positive import/writer allowlists,
not an unbounded prose category, exclude every other project writer and
scientific-summary surface.
`forbidden_result_fields` is exactly: `committor`,
`completion_probability`, `deadlock_probability`, `mean_absorption_time`,
`sensitivity`, `doob_h`, `des_trajectory`, `des_estimate`,
`metric_observations`, `theorem_support`, `theorem_falsification`,
`scientific_score`, `science_summary`, and `quantitative_output_root`.
The validator rejects these names recursively at any depth and rejects unknown
properties throughout runtime-lock, authorization, result, refusal, certificate,
and batch structures.

#### 16.3.4 `quantitative_authorization_schema.json` exact shape

Its top-level keys are exactly:

| Key | Value contract |
| --- | --- |
| `schema_version` | `ims-deadlock/g6b-quantitative-authorization-schema/v1` |
| `study_role` | `discovery_only` |
| `confirmation_use` | `prohibited` |
| `schema_role` | `schema_only` |
| `current_capability_reference` | `row_family_protocol.json#/typed_capabilities` |
| `prerequisite_bundle_states` | Exact ordered prerequisites through `TARGET_CERTIFICATION_PREFLIGHT_COMPLETE` |
| `canonicalization_contract` | Exact v2 contract from Section 7.2 |
| `self_hash_finalization_contract` | Exact null-placeholder/DAG contract from Section 7.2 |
| `same_target_lock_required_fields` | Exact field-name array below |
| `quantitative_runtime_lock_required_fields` | Exact field-name array below |
| `quantitative_authorization_required_fields` | Exact field-name array below |
| `authorized_scope_required_fields` | Exactly `case_unit_ids`, `method_observation_ids`, `certificate_hashes`, `same_target_lock_hashes`, `output_root_reservations` |
| `allowed_command_manifest_required_fields` | Exact quantitative command-manifest fields below |
| `allowed_command_record_required_fields` | Exact command-record fields below |
| `allowed_command_placeholder_codes` | Exact quantitative placeholder-code array below |
| `allowed_environment_variable_names` | Exactly `PYTHONDONTWRITEBYTECODE`, `PYTHONPATH` |
| `nested_field_contracts` | Exact nested contracts below |
| `recursive_prohibited_fields` | Exact recursive authorization/result boundary blacklist |
| `allowed_method_roles` | Exactly `exact_companion`, `des_companion` |
| `wildcard_scope_allowed` | `false` |
| `survivor_scope_claim_contract` | Exact original-denominator and claim-boundary rule from Section 11.6 |
| `refusal_code_vocabulary_version` | `ims-deadlock/g6b-refusal-codes/v1` |
| `refusal_reason_codes` | Exact union of Section 14 cross-gate and quantitative arrays |
| `schema_does_not_authorize_quantitative_execution` | `true` |

`same_target_lock_required_fields` is exactly:
`schema_version`, `same_target_lock_id`, `bundle_id`, `case_unit_id`,
`method_companion_group_id`, `exact_method_observation_id`,
`des_method_observation_id`, `selected_bad_classes`, `success_class`,
`target_schema_version`, `estimand_schema_version`, `state_space_hash`,
`partition_hash`, `rate_manifest_hash`, `positive_rate_graph_hash`,
`policy_filter_hash`, `absorption_domain_hash`, `certificate_artifact_hash`,
`estimand_id`, `exact_stopping_rule_hash`, `des_stopping_rule_hash`,
`metric_schema_sha256`, `metric_reuse_authorization_hash`,
`exact_random_stream_manifest_sha256`, `des_random_stream_manifest_sha256`,
`exact_output_root_reservation_sha256`,
`des_output_root_reservation_sha256`, `lock_created_at_utc`, and
`same_target_lock_sha256`.

`quantitative_runtime_lock_required_fields` is exactly:
`schema_version`, `runtime_lock_id`, `source_head`, `source_tree_hash`,
`source_dirty_state`, `sealed_bundle_manifest_hash`,
`target_certification_batch_manifest_hash`, `case_unit_ids`,
`method_observation_ids`, `same_target_lock_hashes`, `python_runtime_identity`,
`allowed_command_manifest_hash`,
`random_stream_manifest_hashes`, `output_root_reservations`, `resource_budget`,
`run_retry_stop_policy`, `capture_policy`, `ledger_head_hash`,
`created_at_utc`, and `runtime_lock_sha256`.

The quantitative `python_runtime_identity` uses the exact same six-field
contract as the preflight runtime identity and must match unless a separately
reviewed runtime change is declared and re-locked.

The quantitative `allowed_command_manifest` has exactly `schema_version`,
`manifest_id`, `capability`, `source_head`, `source_tree_hash`,
`sealed_bundle_manifest_hash`, `target_certification_batch_manifest_hash`,
`authorized_scope_sha256`, `same_target_lock_hashes`,
`output_root_reservation_hashes`, `declared_command_ids`,
`command_record_hashes`, `command_count`, `placeholder_vocabulary`,
`environment_variable_name_allowlist`, `wildcard_scope_allowed`,
`created_at_utc`, and `manifest_sha256`. Its `schema_version` is exactly
`ims-deadlock/g6b-quantitative-allowed-command-manifest/v1`; `capability` is
`quantitative_execution`; `declared_command_ids` is unique/sorted and nonempty;
`command_record_hashes` has exactly that key set; `command_count` equals its
cardinality; `same_target_lock_hashes` is byte-for-byte the authorized scope's
same-named map; `output_root_reservation_hashes` is byte-for-byte the authorized
scope's `output_root_reservations` map; and `wildcard_scope_allowed = false`.

The closed, unique, sorted quantitative `placeholder_vocabulary` is exactly
`case_input`, `method_scope_manifest`, `output_root`, `python_runtime`,
`quantitative_authorization`, `repo_source_root`, `sealed_bundle_manifest`, and
`target_certificate_manifest`. The environment-variable names and resolution
rules are exactly the two-field preflight contract. The manifest is finalized
before the quantitative runtime lock under Section 7.2; the runtime lock and
authorization must reference the same `manifest_sha256`, and the manifest
cannot reference either downstream record.

`quantitative_authorization_required_fields` is exactly:
`schema_version`, `authorization_id`, `capability`, `authorized`, `bundle_id`,
`authorized_scope`, `sealed_bundle_manifest_hash`,
`target_certification_batch_manifest_hash`, `runtime_lock_sha256`,
`allowed_command_manifest_hash`, `allowed_commands`, `run_roles`,
`resource_budget`, `output_root_policy`,
`stop_conditions`, `review_artifact_hash`, `issued_at_utc`,
`invalidated_by_identity_drift`, and `authorization_sha256`. The only valid
capability is `quantitative_execution`; the schema-only file contains no
instance with `authorized = true`.

`authorized_scope` uses exactly the five fields declared above. Every ID array
is unique and sorted; every certificate, same-target-lock, and root-reservation
map has exactly the corresponding scoped key set; no wildcard, prefix, glob,
null scope, or implicit companion expansion is allowed.

Every `allowed_command_record` has exactly `command_id`, `capability`,
`executable_sha256`, `entrypoint`, `argv_tokens`, `working_directory_repo_relative`,
`environment_variable_allowlist`, `stdin_policy`, `authorized_case_unit_ids`,
`authorized_method_observation_ids`, `authorized_run_roles`,
`authorized_output_root_reservation_hashes`, and `command_record_sha256`.
`argv_tokens` and `environment_variable_allowlist` use the exact closed token
union defined for preflight, with placeholder codes restricted to the
quantitative vocabulary above. Shell strings, command substitution, redirection,
and unreviewed environment expansion are prohibited. Each record hash must equal
the same command-ID entry in the quantitative manifest, and the authorization's
`allowed_commands` array must equal the sorted manifest record-hash values.

The quantitative `resource_budget` has exactly `max_wall_clock_seconds`,
`max_cpu_seconds`, `max_memory_bytes`, `max_storage_bytes`, `max_cases`,
`max_concurrent_methods`, `max_retries`, and `max_replicates_per_method`.
`run_retry_stop_policy` has exactly `run_roles`, `retryable_reason_codes`,
`nonretryable_reason_codes`, `max_retries`, `stop_on_identity_drift`,
`stop_on_unexpected_file`, and `stop_on_control_failure`.
`capture_policy` has exactly `stdout_capture`, `stderr_capture`,
`command_transcript`, `exit_code_capture`, `raw_output_hash_manifest`,
`filesystem_before_manifest`, `filesystem_after_manifest`, and
`bytecode_write_disabled`.
`output_root_policy` has exactly `root_template`, `reservation_required`,
`unmaterialized_before_launch`, `one_writer_per_method_run`,
`fallback_path_prohibited`, `absolute_path_prohibited`,
`tracked_inventory_required`, and `no_cross_method_writes`.
`allowed_commands` is a unique sorted array of allowed-command-record hashes;
`stop_conditions` is a unique sorted array of versioned codes. All nested
objects set `additionalProperties = false` and recursively reject authorization
scope, result, output, or scientific-summary fields not explicitly permitted.

### 16.4 Planned later instance artifacts

Only after separate gate approval may later tranches materialize versioned,
repo-relative instance artifacts for:

- case-construction authorization and sealed object manifest;
- retired-authority normalization authorization, source inventory,
  normalization manifest, and fingerprint records;
- subject-aware input overlap authority lock and report;
- target-certification runtime lock and authorization;
- per-case certificate/refusal records and batch manifest;
- allowed-command, transcript, filesystem, and hash manifests;
- exact/DES same-target locks;
- quantitative runtime lock and authorization; and
- append-only refusal/supersession ledgers.

Preflight evidence and quantitative outputs must have distinct roots and
schemas. Neither may overwrite historical G4/G5/G6-R evidence.

The reserved repo-relative roots are exact:

- schema-only governance definitions:
  `cases/discovery/g6b/row_families/structural_discovery_v1/`;
- later bundle governance instances:
  `cases/discovery/g6b/row_families/structural_discovery_v1/governance/{bundle_id}/`;
- later sealed case inputs:
  `cases/discovery/g6b/row_families/structural_discovery_v1/case_units/{case_unit_id}/`;
- later target-certification evidence:
  `evidence/g6b/target_certification/{bundle_id}/`; and
- later quantitative output reservation:
  `artifacts/g6b/quantitative/{bundle_id}/{case_unit_id}/{method_observation_id}/{run_role}/`.

The first schema-only migration requires every later-instance root above to be
absent. A later gate may materialize only its named root and exact manifest.
Absolute workstation paths, aliases, implicit current-working-directory roots,
and fallback locations are prohibited.

## 17. Validator and Test Architecture

### 17.1 Data-only governance validator

The existing row-family validator remains data-only. It may parse canonical
JSON, enforce exact file sets/keys/versions, validate state transitions and
counts, verify cross-document hashes, and reject prohibited fields. It must not
enumerate states, certify a target, create case instances, import scientific
execution code, inspect outputs, or advance current authorization flags.

Concepts formerly prohibited in the schema-only bundle may appear only inside
new typed later-artifact schemas and only when their prerequisite state and
authorization references validate. Free-floating keys such as
`state_enumeration_result`, `actual_overlap_result`, or
`current_runtime_lock` remain prohibited.

### 17.2 Target-certification runner and artifact validator

The preflight runner is a separate capability surface. A pure artifact
validator may validate its already captured certificate/refusal records without
re-enumeration. Tests must prove the runner cannot reach CTMC/DES/scoring
surfaces and that the governance validator never calls the runner.

### 17.3 Required tests

The later implementation plan must add failing tests before production edits
for at least these contracts:

1. v2 state order includes authorized retired normalization and complete overlap
   audit before target preflight, and target preflight before any quantitative
   lock or authorization;
2. current instance remains schema-only/PENDING with all four capability flags
   false;
3. every self-hash recomputes only from its validated null-placeholder preimage;
   an included digest, omitted placeholder, second excluded field, forged digest,
   or cross-record hash cycle fails;
4. canonical JSON v2 rejects duplicate keys, non-NFC strings, NaN, infinities,
   negative zero, JSON floats, exponent-form decimal strings, absolute/Windows/
   parent paths, and unsorted set-like arrays;
5. historical numeric tokens normalize through exact decimal parsing rather than
   binary floating point;
6. fingerprints declare and enforce subject type, projection kind, exact payload
   schema, dependency, correlation, and provenance envelope;
7. changing only bundle/case/method/group IDs, paths, labels, or timestamps does
   not change any subject-free comparison projection;
8. the same retired scientific input under renamed IDs/paths produces the same
   comparison projection and an overlap or semantic-reuse refusal; paraphrased
   predictions without scientific-content change also refuse, and an unequal
   provenance-envelope hash cannot make either pass;
9. changing scientific state, route, parameter, prediction, metric, or stream
   content changes the owning projection, while correlated subdimensions are not
   counted as independent observations;
10. `state_snapshot_sha256` is pre-enumeration, omits the new case ID, declares
    its parent relation, and cannot be replaced by `state_space_hash`;
11. every scientific input field is classified into an exact projection or the
    case refuses; unknown nested fields never hash silently;
12. the retired source inventory is exact, hash-verified, and complete; missing,
    stale, mismatched, locally absent, or unverified snapshot material refuses;
13. G5/G6-R inherited G4 input identities share lineage IDs, are compared once,
    and cannot inflate authority or evidence counts;
14. direct, derived, inherited, not-applicable, and unreconstructable source
    statuses are distinguished; missing/unreconstructable/normalizer-error states
    never become `pass_distinct`;
15. the retired normalizer imports/calls only its exact allowlist, never
    enumerates/classifies/solves/simulates/scores, never parses prohibited outcome
    fields, and writes only its governance manifest/records;
16. exact methods use method-owned provenance envelopes but a subject-free
    not-applicable projection; equality yields only
    `not_applicable_by_protocol_pass`;
17. stochastic methods require a verified disjoint-substream proof; unequal
    stream-manifest hashes alone cannot pass;
18. output-root reservations are deterministic, inert, unmaterialized, and
    containment-only; renaming a root cannot rescue copied case content or count
    as semantic distinctness;
19. G4's absent pre-execution output root is not-applicable, while G5/G6-R roots
    are normalized stage-wise without absolute paths entering comparison;
20. metric-schema reuse requires a companion-group record and exact controlled-
    reuse authorization; companion membership/counting invariants hold;
21. one planned method-level overlap/refusal propagates to the owning case and
    cannot be hidden by dropping the method after seal;
22. overlap reports cover every sealed case, method, companion group, unique
    retired lineage, and policy-required dimension with no pending entries;
23. refused/superseded objects cannot disappear from later manifests;
24. recursive additional-property and forbidden-key checks reject quantitative
    or scientific output smuggled under `refusal_details`, capture policy,
    budgets, command records, target identity, or other permitted containers;
25. preflight and quantitative runtime locks are distinct and neither embeds a
    future authorization circularly;
26. preflight authorization names exact scope, positive project-import and
    writer allowlists, and tokenized command records;
27. the preflight entrypoint stops after certificate/refusal, and runtime spies
    fail if it imports a forbidden module or calls any exact hazardous symbol,
    including `derive_absorbing_ctmc`, `AbsorbingCTMC.solve`, `engine.simulate`,
    `g4_protocol.run_after_freeze`, G5 scoring, or historical replay;
28. preflight artifacts reject committor, mean-time, sensitivity, Doob-h, DES,
    metrics, scoring, summary, and quantitative-output keys at every depth;
29. every sealed overlap-passed case receives a certificate/refusal or the batch
    is incomplete;
30. batch declared/certified/refused/pending sets are disjoint/complete, counts
    equal cardinalities, and result-hash keys equal the terminal set;
31. certificate records require all runtime-derived hashes and `estimand_id`;
32. exact/DES companions share one case, target, certificate, and
    `absorption_domain_hash` but remain distinct method observations;
33. mandatory-control failure blocks quantitative authorization;
34. quantitative authorization enumerates exact case/method/certificate/runtime
    scope and rejects wildcard or implicit expansion;
35. failed, refused, negative, and boundary evidence remains append-only;
36. no G6-B/G6-C/D/E status upgrade can be inferred from schema, normalization,
    overlap, or preflight completion;
37. the G4 manifest-selected case path/ID/hash set equals both freeze ID/hash
    sets exactly; a missing, extra, duplicate, cross-ID, or wrong-base path
    refuses;
38. composite G4 grid cells, L30 inequalities, and B05 candidate monitors expand
    into deterministic parent-owned subunits, and copying one subunit cannot pass
    by changing its new enclosing case ID or surrounding composite payload;
39. every retired dimension is produced only by its exact pointer/transform row;
    a missing pointer, wrong protocol-kind branch, fabricated not-applicable
    dimension, or unlisted transform refuses;
40. the source-read matrix enforces one selector and one use at a time: G5/G6-R
    result, stdout, stderr, record, status, relative-path, file-count, and byte-
    count values can validate source integrity where listed but can never enter a
    comparison projection;
41. Barrier A rejects any operation-code alias, output-schema ID, file role,
    role/schema mapping, missing role, duplicate ownership, or array ordering
    outside the exact Section 4 contracts; and
42. every schema accepts exactly the Section 14 cross-gate plus named gate
    refusal-code union and rejects an unlisted, free-form, or wrong-gate code;
43. the overlap authority lock rejects a branch mismatch, non-clean state,
    non-linked worktree, mismatched checked-out tree, missing Git administrative
    identity hash, or privacy-bearing absolute worktree path; and
44. preflight and quantitative `allowed_command_manifest_hash` values recompute
    from their exact upstream manifests, command-ID/hash maps reconcile, only the
    declared placeholder/environment vocabulary is accepted, and neither
    manifest can reference its downstream runtime lock or authorization.

Mutation tests must remove, duplicate, reorder, drift, or substitute each
critical field and assert fail-closed behavior. Capability tests must use spies
or import guards, not only text scans.

## 18. Verification and Review Gates

The schema implementation is acceptable only after:

- targeted G6-B protocol and row-family tests pass;
- new state, subject-identity, overlap, runtime, capability, and refusal tests
  pass;
- the full test suite passes at the exact commit;
- Ruff check and format check pass;
- strict mypy passes for source and source/tests;
- all tracked JSON parses with duplicate-key rejection;
- canonicalization/self-hash property and mutation tests pass across supported
  runtimes;
- the retired-authority normalization fixtures reproduce every declared source
  and lineage status without reading prohibited outcome fields;
- exact top-level and nested file-set checks pass;
- `git diff --check` passes;
- an independent ontology review validates subject and state categories;
- an independent scientific review validates the data-only normalization
  boundary and the two result-bearing authorization barriers;
- an independent code review finds no capability leak; and
- the branch is re-locked clean and pushed without history rewriting.

Passing these checks implements governance only. It does not authorize case
construction, target preflight, quantitative execution, or a G6-B verdict.

## 19. Publication-Strength Reporting Alignment

The design intentionally adopts a Stage-1-style ordering: research questions,
inputs, targets, controls, falsifiers, methods, and refusal rules are reviewed
and sealed before result-bearing operations. This follows the core Registered
Reports principle that methods are reviewed before outcomes are observed and
that unfavorable outcomes do not invalidate a faithfully executed protocol.

Future DES reporting must map model purpose, input data, initialization,
implementation, experimental design, randomization, run control, outputs, and
limitations to the STRESS-DES reporting surface. Artifact packaging must also
provide an inventory, exact environment, executable instructions, claim-to-
artifact mapping, and verification evidence suitable for independent artifact
evaluation. These reporting frameworks strengthen transparency; they do not
upgrade the mathematical or empirical scope of a claim.

Method sources:

- Center for Open Science, Registered Reports:
  <https://www.cos.io/initiatives/registered-reports>
- Monks et al., *Strengthening the reporting of empirical simulation studies:
  Introducing the STRESS guidelines*, DOI
  <https://doi.org/10.1080/17477778.2018.1442155>
- ACM SIGSIM/PADS artifact-evaluation guidance:
  <https://sigsim.acm.org/conf/pads/2024/blog/artifact-evaluation/>

## 20. Claim Language

Allowed examples:

- "The schema-only G6-B governance bundle validates; no case or science is
  authorized."
- "The input overlap audit is complete for N sealed case units and M method
  observations, with P passed, R refused, zero pending, and inherited retired
  authorities deduplicated into L unique lineages."
- "This case unit has a certified global absorption domain under the locked
  finite positive-rate stopped-CTMC contract."
- "This exact/DES method pair shares one frozen target and is eligible for a
  separately scoped quantitative-authorization review."

Forbidden examples:

- "G6-B passed" from schema, overlap, or preflight completion;
- "all cases are independent" based only on unequal hashes;
- "zero overlap in eight independent dimensions" when the dimensions are
  nested, controlled reuse, not applicable, or containment-only;
- "new identifiers prove non-reuse" or "three retired authorities" when G5 and
  G6-R inherit G4 scientific inputs;
- "exact and DES provide two independent cases" for one case unit;
- "no failures occurred" when no attempt was authorized or refused objects
  were removed;
- "target certification validates the theorem";
- "preflight is non-scientific" without the qualifier that it is
  result-bearing eligibility evidence; and
- any confirmation, generality, robustness, or top-journal-readiness claim not
  supported by later evidence and review.

## 21. Stop Conditions

Stop before case construction if the written spec or later case-construction
plan is not explicitly approved.

Stop before retired-authority normalization if its exact source inventory,
source/tree lock, normalizer hash, field-level read allowlist, builder allowlist,
governance output root, review artifact, or capability-specific authorization is
absent or stale.

Stop before overlap comparison if any retired source is absent/mismatched, a
required projection is missing/unreconstructable, lineage inheritance is
ambiguous, a subject ID/path contaminates a subject-free projection, or the
normalization manifest/counts do not reconcile.

Stop before target preflight if any sealed object is missing, input overlap is
incomplete/refused for the proposed scope, the preflight runtime lock or
authorization is absent/stale, controls/predictions were not sealed, the
ledger is not current, the allowed-command manifest is not exact, or the
evidence root is not inert and isolated.

Stop before quantitative execution if any scoped case lacks a reviewed target
certificate, exact/DES identity drifts, a mandatory control fails, refused or
superseded objects disappear, the quantitative runtime lock or authorization
is absent/stale, output roots are already materialized, or the ledger/counts do
not reconcile.

Stop and retain evidence on any unauthorized operation, unexpected output,
truncation, target/rate/policy drift, overlap hit, certificate refusal,
negative-control failure, runtime mismatch, or capability leak.

## 22. Acceptance Criteria for This Written Specification

- This file is the only project file changed in the design-document commit.
- It records the audited base commit and current execution-disabled state.
- It describes the two authorization barriers without opening either barrier.
- It resolves the absorption-hash and runtime-lock circularities.
- It resolves every in-record self-hash circularity with one canonical
  null-placeholder protocol and a directed acyclic reference order.
- It defines Unicode, numeric, path, duplicate-key, and historical-decimal
  behavior under a versioned canonical JSON contract.
- It assigns every overlap dimension to the correct identity subject.
- It separates subject-free comparison projections from subject-owning
  provenance envelopes so renaming cannot manufacture non-overlap.
- It defines pre-enumeration `state_snapshot_sha256` separately from runtime
  `state_space_hash`.
- It defines an exact, authorized, fail-closed G4/G5/G6-R normalization source
  inventory, producer/status model, and inherited-lineage deduplication rule.
- It separates byte distinctness, provenance, semantic lineage, construction
  process, mechanism diversity, random streams, and confirmation blinding.
- It defines typed admission outcomes for semantic content, random streams,
  controlled metric reuse, and output-root containment rather than treating the
  eight dimensions as independent inequalities.
- It defines sealed-case, overlap, preflight, same-target, quantitative, and
  refusal/revision contracts.
- It defines exact companion-group membership, nested-object closure, recursive
  prohibited-key checks, command allowlists, and batch set/count invariants.
- It defines bundle-, case-, and method-level states with explicit aggregation
  counts and no selective deletion.
- It defines capability-level allowed/forbidden preflight behavior and batch
  completeness.
- It provides versioning, planned artifact surfaces, tests, review gates,
  reporting alignment, claim limits, and stop conditions.
- It contains no unresolved placeholder, silent authorization, favorable
  result, actual case identity, scientific output, or G6-B status upgrade.

After this file is committed, the next step is user review of the written spec.
Only after that review passes may a detailed implementation plan be written.
