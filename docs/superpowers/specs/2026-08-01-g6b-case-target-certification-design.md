# G6-B Case Construction and Target-Certification Authorization Design

Status: `APPROVED CONCEPT / WRITTEN SPEC AWAITING USER REVIEW /
EXECUTION-DISABLED / NO CASE CREATION`.

This specification records the approved concept-level staged G6-B design that
repairs the case-construction, overlap-admission, target-certification, and
quantitative-authorization circularities. It is a governance and architecture
document. It
does not create a discovery case, enumerate an LTS, certify an absorption
domain, construct or solve a CTMC, run DES, inspect scientific outputs, create
a quantitative output root, authorize science, or mark G6-B as `PASS`.

`APPROVED CONCEPT` means only that the design direction was approved for
written specification. It is not approval of this written spec, an
implementation plan, the future case-construction plan, any case artifact,
target-certification preflight, or quantitative execution.

The audited source base is commit
`1f342baea755f7c85ef538c7403c52cfb9d610c4`. The current nested G6-B bundle
remains schema-only at `ROW_FAMILY_BUNDLE_IMPLEMENTED`; its adversarial review
state remains `PENDING`, `case_creation_authorized` remains false, and
`scientific_execution_authorized` remains false.

## 1. Objective

Make the future G6-B gate graph reachable without weakening any scientific
boundary. The design separates six capabilities that the current v1 row-family
contract partially conflates:

1. approved case-construction planning;
2. sealed pre-enumeration case inputs;
3. input/provenance overlap admission against retired authorities;
4. explicitly authorized target-certification preflight;
5. exact/DES same-target identity locking; and
6. separately authorized quantitative execution.

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

### 2.6 Audited source anchors

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
  with no target-certification preflight state.

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

## 4. Chosen Architecture: Two Authorization Barriers

The chosen design has two explicit execution barriers.

### Barrier A: target-certification preflight

Barrier A may be opened only after case inputs and predictions are sealed, the
input-level retired-authority overlap audit is complete, the exact preflight
runtime is locked, and a scope-specific authorization artifact exists.

Barrier A permits only:

- loading the sealed case inputs;
- complete, bounded stable-LTS enumeration;
- deterministic LTS provenance re-verification;
- typed terminal/stopping partition construction;
- frozen event-rate and no-policy identity validation;
- global absorption-domain certification or structured refusal;
- canonical target-certificate/refusal and transcript-hash artifacts; and
- data-only validation of those artifacts.

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

All canonical payloads use UTF-8 JSON, sorted keys, minimal separators, no
duplicate keys, explicit payload version, explicit subject ID, no absolute
machine paths, and no path-dependent serialization.

| Dimension | Subject | Required meaning |
| --- | --- | --- |
| `case_content_sha256` | case unit | Hash of the complete sealed case-spec payload, excluding generated reachable states and outputs. |
| `state_snapshot_sha256` | case unit | Hash of the declared state-bearing input snapshot before enumeration; never the reachable state universe. |
| `route_signature_sha256` | case unit | Hash of the canonical structural route/transition-registry signature, independent of filenames and display names. |
| `parameter_tuple_sha256` | case unit | Hash of every frozen structural and numeric parameter that can affect semantics or target certification, including the state bound and rate-manifest reference. |
| `random_stream_manifest_sha256` | method observation | Hash of the method-specific random-stream declaration; exact-only methods use a case-and-method-specific not-applicable provenance manifest. |
| `output_root` | method observation | Canonical logical reservation identity for a later quantitative root; the path does not exist yet. |
| `sealed_prediction_sha256` | case unit | Hash of the preregistered question, hypotheses, falsifiers, controls, and planned method roles before preflight. |
| `metric_schema_sha256` | method companion group | Hash of the preregistered metric/scoring schema; controlled exact/DES or future-confirmation reuse requires an explicit reuse record. |

An overlap report must record `fingerprint_subject_type` and
`fingerprint_subject_id` for every comparison. A case unit is overlap-admissible
only when every required case-level dimension and every planned method-level
dimension is present and passes against the retired-authority scope. A method
cannot borrow the passing random-stream or output-root record of its companion.

### 7.1 `state_snapshot_sha256`

The v2 identity contract defines two mutually exclusive input modes:

- `model_generated_lts`: the snapshot payload is the validated
  `CaseSpec.initial_state` subtree plus its payload version and case-unit ID;
- `explicit_finite_lts_input`: the snapshot payload is the declared, sealed
  input state/arc snapshot because that finite LTS is itself the input.

The input mode is sealed. Switching modes creates a new case-unit identity.
Neither payload may contain enumeration results, runtime state counts,
terminal partitions, `S_reach`, `S_T`, or certificate fields.

`state_space_hash` has a different subject and time: it is produced only from
the complete runtime `StableLTS` during authorized target certification. The
validator must reject substituting `state_space_hash` for
`state_snapshot_sha256` in any retired-authority overlap comparison.

`state_snapshot_sha256` may be a named sub-identity within the complete
`case_content_sha256` payload. That declared nesting is allowed and must be
machine-recorded; it does not make the two dimensions statistically independent
or turn one case input into two independent identity observations.

### 7.2 Random-stream not-applicable records

An exact method without stochastic sampling uses a method-specific canonical
manifest with `applicability_status = not_applicable_by_protocol`. A global
shared sentinel is prohibited. The manifest proves explicit provenance only;
it does not prove random-process independence.

### 7.3 Output-root reservation

The `output_root` dimension is a canonical logical reservation, not an existing
directory and not a claim of case independence. It must include bundle, case,
method, and run-role identity. Before quantitative authorization, validators
must require both `reserved = true` and `materialized = false`, and must reject
filesystem creation or inspection fields. Root uniqueness proves containment
and provenance separation only.

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
| `zero_overlap_admission` | All required subject-aware comparisons and refusals. | The unit passed the protocol's bounded retired-authority admission rule. |

The report must never collapse these predicates into a single boolean named
`independent`. In particular:

- unequal hashes do not prove statistical independence;
- a unique output root does not prove case identity independence;
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

## 10. Input-Level Overlap Audit

The actual overlap audit occurs only after sealing and uses a fresh, clean
`input_overlap_authority_lock`. The lock binds:

- repository remote, branch, exact HEAD and tree;
- a required clean Git state and linked-worktree identity;
- sealed bundle and per-object manifest hashes;
- exact retired G4/G5/G6-R authority paths and hashes;
- canonicalization algorithm versions;
- comparison command/validator versions; and
- append-only ledger head.

Local absence of remote-only G5 authority material is never non-overlap
evidence. Missing authority, missing discovery fingerprints, an unknown
canonicalization version, semantic lineage ambiguity, or any prohibited
retired overlap produces a refusal.

The audit is batch-complete. Every sealed case and method subject receives a
per-dimension result. A report with missing subjects, missing dimensions, or
`pending_count > 0` is incomplete and cannot advance. Refused units remain in
the denominator and ledger. Revision after refusal requires a new identity or
an explicit supersession record with old/new hashes and reason codes.

## 11. Target-Certification Preflight Capability

### 11.1 Dedicated entrypoint and dependency boundary

Implementation must add a dedicated G6-B target-certification entrypoint whose
maximum capability is:

`load sealed input -> enumerate_stable_lts -> partition_stable_lts ->
certify_absorption_domain -> emit certificate/refusal`.

The entrypoint must stop before CTMC generator construction. It must not call
`derive_absorbing_ctmc`, import or call a CTMC solver, invoke DES, execute G5 or
G6-R replay, score a theorem, or use any quantitative-output writer. Capability
separation must be enforced by module dependencies and tests, not comments
alone.

### 11.2 Preflight runtime lock

`target_certification_runtime_lock` is created only after the input overlap
audit is complete and before preflight authorization. It binds:

- exact repository HEAD/tree and sealed bundle hash;
- Python executable/version and environment/package identity;
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
transcript/stderr/exit-code captures, the filesystem manifest, and the hash
manifest. This root is not the quantitative `output_root` dimension and cannot
contain CTMC/DES/metric results.

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
that only the authorized certificate/refusal, transcript, and hash-manifest
files were written.

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
- distinct method-specific random-stream/output-root records.

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
  status, every refusal is ledgered, and `pending_count = 0`;
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

Required refusal codes include at least:

- `overlap_hit`;
- `missing_hash`;
- `semantic_identity_reuse`;
- `semantic_lineage_ambiguous`;
- `unauthorized_case_creation_attempt`;
- `incomplete_stable_lts`;
- `state_bound_truncation`;
- `unavailable_transition_branch`;
- `unverified_lts_provenance`;
- `rate_manifest_drift`;
- `selected_target_drift`;
- `policy_filter_drift`;
- `non_almost_sure_absorption_domain`;
- `batch_incomplete`;
- `exact_des_target_mismatch`;
- `unexpected_preflight_side_effect`;
- `failed_negative_control`;
- `unauthorized_quantitative_execution_attempt`; and
- `outcome_leakage`.

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
  the non-reuse claim lattice;
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
- `target_certification_schema.json`; and
- `quantitative_authorization_schema.json`.

They live under
`cases/discovery/g6b/row_families/structural_discovery_v1/` and must be added to
the exact nested file manifest. Adding them does not create case instances or
authorizations. Any additional schema filename requires written-spec review
rather than an opportunistic addition during implementation.

The schema-only nested root therefore changes from exact eight JSON files to
exact eleven. Implementation must update `_DOCUMENTS`, `_SCHEMA_VERSIONS`, the
expected `row_family_protocol.json.artifact_paths`, the exact-file-set tests,
and the corresponding review/handoff file inventories together. A validator
that accepts either eight or eleven without an explicit schema version is
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
| `governance_instance_root_template` | Exact repo-relative governance root from Section 16.4 |
| `case_unit_root_template` | Exact repo-relative case-unit root from Section 16.4 |
| `construction_authorization_required_fields` | Exact field-name array below |
| `sealed_bundle_manifest_required_fields` | Exact field-name array below |
| `case_unit_required_fields` | Exact field-name array below |
| `method_observation_required_fields` | Exact field-name array below |
| `fingerprint_subject_map` | Exact eight-key subject map from Section 7 |
| `allowed_input_modes` | Exactly `model_generated_lts`, `explicit_finite_lts_input` |
| `output_root_reservation_contract` | Exact inert-reservation object below |
| `prohibited_instance_fields` | Exact outcome/certificate/authorization blacklist below |
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
`case_unit_record_hashes`, `method_observation_record_hashes`,
`mandatory_control_ids`, `fingerprint_record_hashes`,
`sealed_prediction_hashes`, `metric_schema_hashes`,
`quantitative_output_root_reservations`, `planned_case_unit_count`,
`planned_method_count`, and `manifest_sha256`.

`case_unit_required_fields` is exactly:
`schema_version`, `bundle_id`, `case_unit_id`, `family_id`, `input_mode`,
`structural_family_role`, `negative_control_id_or_null`, `case_artifact_paths`,
`case_content_sha256`, `state_snapshot_sha256`, `route_signature_sha256`,
`parameter_tuple_sha256`, `sealed_prediction_sha256`, `rate_manifest_ref`,
`policy_declaration_ref`, `selected_target_ref`, `state_bound`,
`method_observation_ids`, and `case_unit_state`.

`method_observation_required_fields` is exactly:
`schema_version`, `bundle_id`, `method_observation_id`, `case_unit_id`,
`method_companion_group_id`, `method_role`,
`random_stream_manifest_sha256`, `output_root`, `metric_schema_sha256`,
`stopping_rule_ref`, `des_stopping_rule_ref_or_null`, and `method_state`.

`output_root_reservation_contract` has exactly
`logical_repo_independent_identity_required = true`,
`reserved = true`, `materialized = false`,
`absolute_path_prohibited = true`, and
`filesystem_inspection_before_quantitative_authorization = prohibited`.

`prohibited_instance_fields` is exactly: `state_space_hash`, `partition_hash`,
`positive_rate_graph_hash`, `policy_filter_hash`, `absorption_domain_hash`,
`estimand_id`, `metric_observations`, `theorem_prediction_status_observed`,
`execution_result`, and `quantitative_execution_authorized`.

#### 16.3.2 `target_certification_schema.json` exact shape

Its top-level keys are exactly:

| Key | Value contract |
| --- | --- |
| `schema_version` | `ims-deadlock/g6b-target-certification-schema/v1` |
| `study_role` | `discovery_only` |
| `confirmation_use` | `prohibited` |
| `schema_role` | `schema_only` |
| `current_capability_reference` | `row_family_protocol.json#/typed_capabilities` |
| `prerequisite_bundle_states` | Exact ordered prerequisites through `INPUT_OVERLAP_AUDIT_COMPLETE` |
| `preflight_runtime_lock_required_fields` | Exact field-name array below |
| `preflight_authorization_required_fields` | Exact field-name array below |
| `allowed_operations` | Exact Barrier A allowlist from Section 4 |
| `allowed_result_fields` | Exact field-name array below |
| `forbidden_calls` | Exact hazardous-call array below |
| `forbidden_result_fields` | Exact quantitative/scoring field array below |
| `preflight_evidence_root_contract` | Exact two-state root contract from Section 11.3 |
| `per_case_result_required_fields` | Exact field-name array below |
| `result_status_values` | Exactly `certified`, `refused` |
| `batch_manifest_required_fields` | Exact field-name array below |
| `batch_status_values` | Exactly `complete_all_certified`, `complete_with_refusals`, `incomplete_refused` |
| `refusal_reason_codes` | Exact versioned code list including Section 14 codes |
| `schema_does_not_authorize_preflight` | `true` |

`preflight_runtime_lock_required_fields` is exactly:
`schema_version`, `runtime_lock_id`, `source_head`, `source_tree_hash`,
`source_dirty_state`, `sealed_bundle_manifest_hash`, `python_executable`,
`python_version`, `environment_identity_hash`, `pythonpath_source_hash`,
`bytecode_cache_policy`, `entrypoint_hash`, `allowed_command_manifest_hash`,
`target_certificate_schema_version`, `canonicalization_version`,
`case_unit_ids`, `expected_input_hashes`, `preflight_evidence_root`,
`resource_budget`, `capture_policy`, `failure_budget`, `ledger_head_hash`,
`created_at_utc`, and `runtime_lock_sha256`.

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

`per_case_result_required_fields` equals `allowed_result_fields`. A certified
record requires every runtime-derived hash, non-null canonical certificate,
empty refusal codes, and exit code zero. A refused record requires null hashes
that were not safely produced, nonempty versioned reason codes, retained
details, and an exit code consistent with the declared refusal contract.

`batch_manifest_required_fields` is exactly:
`schema_version`, `bundle_id`, `sealed_bundle_manifest_hash`,
`runtime_lock_sha256`, `authorization_sha256`, `declared_case_unit_ids`,
`per_case_result_hashes`, `certified_case_unit_ids`, `refused_case_unit_ids`,
`planned_count`, `certified_count`, `refused_count`, `pending_count`,
`batch_status`, `transcript_manifest_sha256`, `filesystem_manifest_sha256`,
`ledger_head_hash`, and `batch_manifest_sha256`.

`forbidden_calls` is exactly:
`ims_deadlock.g4_instances.derive_absorbing_ctmc`,
`ims_deadlock.ctmc.AbsorbingCTMC.solve`,
`ims_deadlock.engine.simulate`,
`ims_deadlock.g4_protocol.run_after_freeze`,
`ims_deadlock.g4_protocol.main`,
`ims_deadlock.g5_scoring.score_case`,
`ims_deadlock.g5_scoring.score_run`,
`ims_deadlock.g5_scoring.main`,
`ims_deadlock.historical_replay.main`, every writer whose allowed root is a
quantitative output root, and every manuscript/scientific-summary writer.
`forbidden_result_fields` is exactly: `committor`,
`completion_probability`, `deadlock_probability`, `mean_absorption_time`,
`sensitivity`, `doob_h`, `des_trajectory`, `des_estimate`,
`metric_observations`, `theorem_support`, `theorem_falsification`,
`scientific_score`, `science_summary`, and `quantitative_output_root`.

#### 16.3.3 `quantitative_authorization_schema.json` exact shape

Its top-level keys are exactly:

| Key | Value contract |
| --- | --- |
| `schema_version` | `ims-deadlock/g6b-quantitative-authorization-schema/v1` |
| `study_role` | `discovery_only` |
| `confirmation_use` | `prohibited` |
| `schema_role` | `schema_only` |
| `current_capability_reference` | `row_family_protocol.json#/typed_capabilities` |
| `prerequisite_bundle_states` | Exact ordered prerequisites through `TARGET_CERTIFICATION_PREFLIGHT_COMPLETE` |
| `same_target_lock_required_fields` | Exact field-name array below |
| `quantitative_runtime_lock_required_fields` | Exact field-name array below |
| `quantitative_authorization_required_fields` | Exact field-name array below |
| `authorized_scope_required_fields` | Exactly `case_unit_ids`, `method_observation_ids`, `certificate_hashes`, `same_target_lock_hashes`, `output_root_reservations` |
| `allowed_method_roles` | Exactly `exact_companion`, `des_companion` |
| `wildcard_scope_allowed` | `false` |
| `survivor_scope_claim_contract` | Exact original-denominator and claim-boundary rule from Section 11.6 |
| `refusal_reason_codes` | Exact quantitative refusal codes including Section 14 |
| `schema_does_not_authorize_quantitative_execution` | `true` |

`same_target_lock_required_fields` is exactly the identity fields listed in
Section 12 plus `same_target_lock_id`, `bundle_id`, `lock_created_at_utc`, and
`same_target_lock_sha256`.

`quantitative_runtime_lock_required_fields` is exactly:
`schema_version`, `runtime_lock_id`, `source_head`, `source_tree_hash`,
`source_dirty_state`, `sealed_bundle_manifest_hash`,
`target_certification_batch_manifest_hash`, `case_unit_ids`,
`method_observation_ids`, `same_target_lock_hashes`, `python_executable`,
`python_version`, `environment_identity_hash`, `allowed_command_manifest_hash`,
`random_stream_manifest_hashes`, `output_root_reservations`, `resource_budget`,
`run_retry_stop_policy`, `capture_policy`, `ledger_head_hash`,
`created_at_utc`, and `runtime_lock_sha256`.

`quantitative_authorization_required_fields` is exactly:
`schema_version`, `authorization_id`, `capability`, `authorized`, `bundle_id`,
`authorized_scope`, `sealed_bundle_manifest_hash`,
`target_certification_batch_manifest_hash`, `runtime_lock_sha256`,
`allowed_commands`, `run_roles`, `resource_budget`, `output_root_policy`,
`stop_conditions`, `review_artifact_hash`, `issued_at_utc`,
`invalidated_by_identity_drift`, and `authorization_sha256`. The only valid
capability is `quantitative_execution`; the schema-only file contains no
instance with `authorized = true`.

### 16.4 Planned later instance artifacts

Only after separate gate approval may later tranches materialize versioned,
repo-relative instance artifacts for:

- case-construction authorization and sealed object manifest;
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

1. v2 state order includes target preflight before any quantitative lock or
   authorization;
2. current instance remains schema-only/PENDING with all authorization flags
   false;
3. fingerprints declare and enforce the correct subject type;
4. `state_snapshot_sha256` is pre-enumeration and cannot be replaced by
   `state_space_hash`;
5. exact methods require method-specific not-applicable random-stream
   manifests;
6. output-root reservations are inert and unmaterialized;
7. byte distinctness cannot set statistical-independence fields;
8. overlap reports cover every sealed case and method subject with no pending
   entries;
9. refused/superseded objects cannot disappear from later manifests;
10. preflight and quantitative runtime locks are distinct and neither embeds a
    future authorization circularly;
11. preflight authorization names exact scope and a positive command allowlist;
12. the preflight entrypoint stops after certificate/refusal, and runtime spies
    fail if it imports or calls any exact `forbidden_calls` symbol, including
    `derive_absorbing_ctmc`, `AbsorbingCTMC.solve`, `engine.simulate`,
    `g4_protocol.run_after_freeze`, G5 scoring, historical replay, or
    quantitative-output writers;
13. preflight artifacts reject committor, mean-time, sensitivity, Doob-h, DES,
    metrics, scoring, summary, and quantitative-output keys;
14. every sealed overlap-passed case receives a certificate/refusal or the batch
    is incomplete;
15. certificate records require all runtime-derived hashes and `estimand_id`;
16. exact/DES companions share one case, target, certificate, and
    `absorption_domain_hash` but remain distinct method observations;
17. mandatory-control failure blocks quantitative authorization;
18. quantitative authorization enumerates exact case/method/certificate/runtime
    scope;
19. failed, refused, negative, and boundary evidence remains append-only; and
20. no G6-B/G6-C/D/E status upgrade can be inferred from schema, overlap, or
    preflight completion.

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
- exact top-level and nested file-set checks pass;
- `git diff --check` passes;
- an independent ontology review validates subject and state categories;
- an independent scientific review validates the two-authorization boundary;
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
  observations, with P passed, R refused, and zero pending."
- "This case unit has a certified global absorption domain under the locked
  finite positive-rate stopped-CTMC contract."
- "This exact/DES method pair shares one frozen target and is eligible for a
  separately scoped quantitative-authorization review."

Forbidden examples:

- "G6-B passed" from schema, overlap, or preflight completion;
- "all cases are independent" based only on unequal hashes;
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
- It assigns every overlap dimension to the correct identity subject.
- It defines pre-enumeration `state_snapshot_sha256` separately from runtime
  `state_space_hash`.
- It separates byte distinctness, provenance, semantic lineage, construction
  process, mechanism diversity, random streams, and confirmation blinding.
- It defines sealed-case, overlap, preflight, same-target, quantitative, and
  refusal/revision contracts.
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
