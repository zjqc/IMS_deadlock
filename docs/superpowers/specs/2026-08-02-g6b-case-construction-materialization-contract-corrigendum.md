# G6-B Case Construction Materialization Contract Corrigendum

Status: `PROPOSED / GOVERNANCE-ONLY / AWAITING EXACT-BYTES USER APPROVAL`

Date: 2026-08-02

## Purpose and precedence

This corrigendum closes implementation gaps discovered during Task 2 of the
approved G6-B case-construction plan. It supplements, but does not mutate, the
approved design and the estimand-scope corrigendum. Within the case-construction
tranche it supersedes conflicting Task 2-6 wording in
`docs/superpowers/plans/2026-08-02-g6b-case-construction.md`.

The discovery was made before any construction authorization, case-unit root,
quantitative root, target-certificate root, or scientific output was created.
The four intermediate Task-2 paths remain uncommitted forensic draft material;
they are not evidence of compliance and may be reused only after a fresh
requirement-by-requirement audit against an approved revision.

This corrigendum authorizes no implementation or case construction by itself.
Exact approval must name the SHA-256 of the revised plan and its independent
review artifact before implementation resumes.

## Preserved boundaries

- The bundle series still contains exactly 13 case units, 26 method
  observations, 13 exact/DES companion groups, and the seven mandatory negative
  controls.
- The approved design bytes and the completed estimand-scope corrigendum bytes
  remain immutable.
- The nested row-family governance bundle remains exact-twelve. The only
  machine-readable schema changed by this correction is the existing
  `case_construction_schema.json`, with its manifest/hash closure; no thirteenth
  schema-governance file is added.
- The canonical typed capabilities remain false:
  `case_construction_authorized`,
  `retired_authority_fingerprint_normalization_authorized`,
  `target_certification_preflight_authorized`, and
  `quantitative_execution_authorized`.
- No retired outcome-bearing payload may be read. No normalization, overlap
  audit, state enumeration, terminal classification, target certification,
  CTMC construction/solution, DES run, result inspection, scoring, or scientific
  state advance is authorized.
- All reservations remain inert strings with `reserved=true` and
  `materialized=false`; reserved directories remain absent.

## Why revision is required

The approved bytes name `construction_log.json` and
`construction_ledger.json` but do not define their schemas, hash rules, write
order, or recovery transitions. A single JSON document also cannot be both
ordinary canonical JSON and append-only without rewriting prior bytes.

The closed 25-file case layout contains fingerprint envelopes for case-content,
random-stream, and output-root dimensions but contains no separate stored
comparison-projection bytes for those five per-case projections. A direct
fingerprint record is therefore unable to satisfy its required
`comparison_projection_ref_or_null` without inventing a path or embedding an
undeclared field.

The DES contract requires a seed-root commitment but does not fix how seed
material is generated, committed, or recomputed. The construction plan also
requires a per-group metric reuse file while the existing reuse schema requires
retired-authority identity and a retired metric hash. That schema cannot
represent intra-bundle sharing before retired-authority normalization.

Finally, authorization binds a clean source tree while authorized instance
writes necessarily dirty the worktree. The source baseline and later artifact
state must be distinguished explicitly.

## Versioned correction surface

After approval, Task R1 upgrades the construction schema to
`ims-deadlock/g6b-case-construction-schema/v3` and introduces these instance
schema versions:

| Object | Exact schema version |
| --- | --- |
| construction authorization | `ims-deadlock/g6b-construction-authorization/v2` |
| immutable construction log | `ims-deadlock/g6b-construction-log/v1` |
| append-only ledger entry | `ims-deadlock/g6b-construction-ledger-entry/v1` |
| sealed bundle manifest | `ims-deadlock/g6b-sealed-bundle-manifest/v2` |
| metric-schema sharing record | `ims-deadlock/g6b-metric-schema-sharing/v1` |
| recipe catalog | `ims-deadlock/g6b-case-recipe-catalog/v1` |
| case-unit record | `ims-deadlock/g6b-case-unit/v1` |
| method-observation record | `ims-deadlock/g6b-method-observation/v1` |
| companion-group record | `ims-deadlock/g6b-method-companion-group/v1` |
| fingerprint record | `ims-deadlock/g6b-fingerprint-record/v2` |

All objects remain exact-key, recursively closed, NFC, duplicate-member
rejecting canonical JSON under `ims-deadlock/g6b-canonical-json/v2`.

A `method_observation` record is a preregistered method-side descriptor inside
one companion group. It is not an empirical outcome observation and is not
evidence that the method ran or succeeded.

The exact top-level key set of
`ims-deadlock/g6b-case-construction-schema/v3` is:

```text
schema_version
study_role
confirmation_use
schema_role
current_capability_reference
prerequisite_bundle_state
canonicalization_contract
self_hash_finalization_contract
estimand_id_scope_contract
governance_instance_root_template
case_unit_root_template
construction_authorization_required_fields
sealed_bundle_manifest_required_fields
case_unit_required_fields
method_observation_required_fields
method_companion_group_required_fields
semantic_lineage_declaration_required_fields
metric_schema_sharing_record_required_fields
fingerprint_record_required_fields
fingerprint_subject_map
fingerprint_payload_schemas
materialization_file_contracts
construction_log_contract
construction_ledger_contract
source_identity_contract
transient_path_contract
des_seed_contract
dimension_dependence_contract
allowed_input_modes
output_root_reservation_contract
nested_field_contracts
recursive_prohibited_fields
prohibited_instance_fields
refusal_code_vocabulary_version
refusal_reason_codes
schema_does_not_authorize_case_creation
```

The v2 key `metric_schema_reuse_record_required_fields` is removed from the
construction schema and replaced by
`metric_schema_sharing_record_required_fields`. The same-named retired reuse
contract in `overlap_report_schema.json` and
`retired_authority_fingerprint_schema.json` remains byte-identical and is not a
construction-file contract.

## Closed file layout

The governance root remains exactly four files:

```text
governance/{bundle_id}/construction_authorization.json
governance/{bundle_id}/construction_ledger.json
governance/{bundle_id}/construction_log.json
governance/{bundle_id}/sealed_bundle_manifest.json
```

`construction_ledger.json` is the sole exception to the one-object-per-file
serialization rule. It is a UTF-8 canonical JSON text sequence. Every complete
frame is exactly one RS byte (`0x1e`), one canonical ledger-entry JSON object,
and one LF byte (`0x0a`). Canonical JSON cannot contain an unescaped RS byte, so
RS is the unambiguous frame boundary. Blank frames, CRLF, duplicate members,
noncanonical complete frames, and rewriting or truncating existing bytes are
invalid. A torn final append is preserved as an incomplete RS-prefixed fragment
and recovered only by the fragment protocol below.

Each case root contains exactly 30 files. The v1 layout's
`metric_schema_reuse.json` is replaced by `metric_schema_sharing.json`, and five
missing direct comparison projections are added:

```text
case_input.json
declarations/control_declaration.json
declarations/policy_declaration.json
declarations/rate_manifest.json
declarations/selected_target_declaration.json
fingerprints/case_content_sha256.json
fingerprints/metric_schema_sha256.json
fingerprints/output_root_reservation_sha256_des.json
fingerprints/output_root_reservation_sha256_exact.json
fingerprints/parameter_tuple_sha256.json
fingerprints/random_stream_manifest_sha256_des.json
fingerprints/random_stream_manifest_sha256_exact.json
fingerprints/route_signature_sha256.json
fingerprints/sealed_prediction_sha256.json
fingerprints/state_snapshot_sha256.json
method_companion_group.json
method_observations/des.json
method_observations/exact.json
metric_schema.json
metric_schema_sharing.json
projections/case_content.json
projections/output_root_reservation_des.json
projections/output_root_reservation_exact.json
projections/parameter_tuple.json
projections/random_stream_manifest_des.json
projections/random_stream_manifest_exact.json
projections/route_signature.json
projections/state_snapshot.json
sealed_prediction.json
semantic_lineage_declaration.json
```

No other governance or case-unit path is allowed. There are exactly 390 case
files and 394 files including the four governance files.

## File-role and hash closure

The v3 schema must contain a `materialization_file_contracts` object that maps
every relative path above to one exact role. The required mapping is:

| File class | Schema and hash rule |
| --- | --- |
| `case_input.json` | exact `case_unit_required_fields`; `schema_version=ims-deadlock/g6b-case-unit/v1`; manifest record hash is SHA-256 of final canonical file bytes |
| four declaration files | exact nested declaration field set already defined by the v2 case-content contract; each file's own schema field uses its role-specific `ims-deadlock/g6b-*-declaration/v1`; content hash is SHA-256 of final canonical file bytes |
| eight `fingerprints/*.json` dimensions, with exact/DES variants for the two method dimensions | exact `fingerprint_record_required_fields`; `record_schema_version=ims-deadlock/g6b-fingerprint-record/v2`; `record_provenance_sha256` uses the null-placeholder self-hash rule |
| `method_observations/*.json` | exact `method_observation_required_fields`; record hash is SHA-256 of final canonical file bytes |
| `method_companion_group.json` | exact `method_companion_group_required_fields`; record hash is SHA-256 of final canonical file bytes |
| `metric_schema.json` | exact `metric_schema_sha256` comparison-projection contract; content hash is SHA-256 of final canonical file bytes |
| `metric_schema_sharing.json` | exact sharing fields below; `sharing_record_sha256` uses null-placeholder self-hash |
| eight `projections/*.json` files | the corresponding exact comparison-projection contract; output reservations use `reservation_sha256` null-placeholder self-hash; other projection hashes are SHA-256 of final canonical file bytes |
| `sealed_prediction.json` | exact `sealed_prediction_sha256` comparison-projection contract; content hash is SHA-256 of final canonical file bytes |
| `semantic_lineage_declaration.json` | exact existing lineage field set; `declaration_sha256` uses null-placeholder self-hash |

Every direct-stored fingerprint record must point to its exact stored projection
file and must carry that projection's exact content/self hash. No record may
point to itself, an absent path, a governance file, or another subject's
projection. The case-content, state, route, parameter, prediction, and metric
projections are case/group scoped; random-stream and output-root projections are
method scoped.

`case_artifact_paths_required_keys` becomes exactly:

```text
case_input
case_content_projection
state_snapshot
route_signature
parameter_tuple
rate_manifest
policy_declaration
selected_target_declaration
control_declaration
sealed_prediction
semantic_lineage_declaration
method_observations
random_stream_manifests
output_root_reservations
metric_schema
metric_schema_sharing
fingerprint_records
```

Record-hash maps in the manifest always mean SHA-256 of final canonical file
bytes. A field explicitly defined as a null-placeholder self-hash is separately
recomputed and must also validate; the two meanings may not be conflated.

## Closed transient-path contract

Atomic create-new writes use a closed transient inventory, not inferred random
temporary names. For a final path `P`, its only permitted sibling temporary path
is:

```text
P.parent/.g6b-tmp-{attempt_token}-{P.name}
```

For `construction_authorization.json`, `attempt_token` is the first 16 lowercase
hex characters of the approved-plan SHA-256. For the immutable log, all 390 case
files, and the manifest, it is the first 16 lowercase hex characters of the
validated authorization's `artifact_sha256`. The ledger is append-only and has
no temporary path. The resulting transient inventory has exactly 393 possible
paths: authorization, log, 390 case files, and manifest.

`transient_path_contract` has exactly `schema_version`, `path_template`,
`authorization_token_rule`, `authorized_write_token_rule`,
`covered_final_path_count`, `exclusive_create_required`,
`flush_and_fsync_before_rename`, `atomic_no_replace_rename_required`,
`sealed_success_requires_all_absent`, and
`interrupted_recovery_preserves_and_hashes`.

Before each rename, the writer exclusively creates the exact temp path, writes
and flushes the complete bytes, fsyncs the file, and performs an atomic
no-replace rename to the final path. It then verifies the final hash. On sealed
success all 393 transient paths are absent. On interruption, recovery inventories
only the 394 final paths plus these 393 transient paths, hashes every retained
raw temp byte sequence, includes temp paths in
`observed_partial_file_hashes`, and never renames, deletes, truncates, or resumes
them. An interrupted bundle is not required to have the 394-file sealed
inventory and can never be presented as a partial pass.

## Clean source baseline and authorization

Task R4 freezes one clean commit `C2`. Before creating authorization, all tracked
source, test, schema, and review paths must be committed, and the worktree must
be clean. Authorization v2 has exactly these fields:

```text
schema_version
artifact_id
capability
authorized
bundle_id
case_unit_ids
method_observation_ids
method_companion_group_ids
source_head
source_tree_hash
source_file_hashes
case_construction_schema_sha256
case_recipe_registry_sha256
frozen_row_family_matrix_sha256
approved_corrigendum_hash
approved_plan_artifact_hash
plan_review_artifact_hash
task2_review_artifact_hash
allowed_operations
forbidden_operations
issued_at_utc
invalidated_by_identity_drift
artifact_sha256
```

`source_head` and `source_tree_hash` are exactly `C2` and `C2^{tree}`.
`source_file_hashes` is an exact-key map for these nine C2 paths:

```text
cases/discovery/g6b/row_families/structural_discovery_v1/case_construction_schema.json
cases/discovery/g6b/row_families/structural_discovery_v1/row_family_protocol.json
docs/verification/G6_B_CASE_CONSTRUCTION_TASK2_SOURCE_REVIEW.md
src/ims_deadlock/g6b_case_materializer.py
src/ims_deadlock/g6b_row_family_protocol.py
src/ims_deadlock/g6b_schema_contracts.py
tests/test_g6b_case_materializer.py
tests/test_g6b_row_family_protocol.py
tests/test_g6b_schema_contracts.py
```

The Task-R2 review artifact is committed in `C2` and binds the other eight exact
path hashes plus fresh verification commands; it does not self-reference its
own hash or a future commit ID. Authorization binds the final hash of all nine
paths after the review artifact is finalized.

Authorization creation requires a clean worktree at `C2`. After authorization
is created and until the manifest is sealed, the worktree is expected to become
dirty only under the one exact authorized governance root and the 13 exact case
roots. Pre-seal runtime validation must require:

- current `HEAD == source_head` and `HEAD^{tree} == source_tree_hash`;
- all nine authorized paths byte-equal their authorized hashes;
- no tracked source/schema/test/review path differs from `C2`;
- every dirty or untracked path is a member of the closed authorized output
  inventory; and
- the authorization self-hash, plan/review hashes, schema hash, recipe hash, and
  frozen-matrix hash all match.

Any source edit after authorization invalidates the authorization. A fix requires
a new clean `C2`, a new Task-R2 review, and a new authorization before any new
output byte. Artifact dirtiness alone is not source drift.

After the sealed artifact tree is committed as a descendant `C3`, post-seal
validation does not require `HEAD == C2`; it requires that `C2` is an ancestor of
`HEAD`, all nine authorized paths remain byte-equal their C2 hashes, and the
authorized schema/recipe/matrix hashes still match. The C2..C3 diff may contain
only the exact 394 artifact paths. A later C4 publication diff may additionally
contain only `docs/verification/G6_B_CASE_CONSTRUCTION_REVIEW_V2.md`,
`PROJECT_HANDOFF.md`, and `docs/ROADMAP.md`. No other post-C2 path is allowed. This
phase distinction permits committing sealed artifacts and their handoff without
redefining the source baseline.

## Immutable construction log

`construction_log.json` is one canonical object written exactly once before any
case file. It has exactly:

```text
schema_version
log_id
bundle_id
construction_authorization_sha256
source_head
source_tree_hash
source_file_hashes
case_construction_schema_sha256
case_recipe_catalog_schema_version
case_recipe_registry_sha256
case_recipe_hashes
case_transform_records
candidate_case_unit_ids
candidate_method_observation_ids
candidate_method_companion_group_ids
planned_case_file_paths
write_order
forbidden_operation_checks
log_sha256
```

`case_recipe_hashes` has exactly the 13 case IDs as keys.
`case_transform_records` has exactly the 13 case IDs as keys; each value has
exactly `declared_source_template_ids`, `declared_source_artifact_hashes`,
`declared_semantic_parent_ids`, `declared_transform_codes`,
`visible_retired_authority_ids`, `retired_case_payload_read=false`,
`retired_outcome_used=false`, `graph_isomorphism_check_required=true`, and
`outcome_driven_tuning_prohibited=true`.

`planned_case_file_paths` contains every one of the 390 final case-file paths
exactly once and no hashes. `write_order` is byte-for-byte the same sorted path
array and freezes deterministic lexicographic POSIX write order.
`forbidden_operation_checks` is an exact-key map from every authorization-
forbidden operation to `false`. The log deliberately contains no downstream
case-file hash because semantic-lineage files bind `log_sha256`; including their
hashes in the log would create a cycle.

`log_sha256` uses the null-placeholder rule. Every semantic-lineage declaration
sets `construction_log_sha256` equal to this `log_sha256`. The log is immutable;
it is never appended, rewritten, or used to record runtime events.

## Append-only construction ledger

Each complete canonical JSON sequence frame contains an entry with exactly:

```text
schema_version
bundle_id
attempt_id
entry_index
event_code
prior_entry_sha256_or_null
construction_authorization_sha256_or_null
source_head_or_null
source_tree_hash_or_null
candidate_log_sha256_or_null
created_file_hashes
observed_partial_file_hashes
refusal_reason_codes
causal_entry_sha256_or_null
interrupted_fragments
entry_sha256
```

`entry_index` starts at 0 and increments by one. `prior_entry_sha256_or_null` is
null only for entry 0 and otherwise equals the immediately prior entry's
`entry_sha256`. `entry_sha256` uses the null-placeholder rule. Path-hash maps
are exact-key, lexicographically ordered canonical objects. Reason codes are
unique and sorted. `attempt_id` equals the validated authorization's
`artifact_id`; when authorization is missing or cannot be parsed, it is exactly
`g6b_discovery_case_construction_v1_unauthorized`. The authorization/source/log
fields are null only when their subject is unavailable at the event's state.

The construction schema v3 sets
`refusal_code_vocabulary_version=ims-deadlock/g6b-refusal-codes/v2`, retains
every v1 code, and adds exactly:
`ledger_append_interrupted`, `partial_bundle_terminal`,
`post_seal_ledger_mutation`, `projection_file_missing`,
`source_identity_phase_violation`, and `unexpected_transient_path`.

Normal complete entries set `interrupted_fragments` to an empty array. Each
array element has exactly `fragment_index`, `fragment_sha256`, and
`fragment_byte_count`; indices are the contiguous zero-based order of raw
fragments since the prior complete entry. If an append tears, recovery hashes
every retained raw fragment beginning with its RS byte, records the exact byte
counts, and appends a new complete RS/JSON/LF frame without altering any
fragment. The new entry's prior hash names the last complete entry, not a
fragment. Before writing has started it is a
`PREWRITE_REFUSED` entry; after `WRITE_STARTED` it is
`INTERRUPTED_PARTIAL`. Its refusal reasons include
`ledger_append_interrupted`. A validator accepts an incomplete fragment only
when the next complete entry's ordered array records every intervening fragment
hash/count and a valid transition. This rule recovers repeated torn recovery
appends while preserving every byte.

The only event codes and transitions are:

```text
EMPTY -> PREWRITE_REFUSED
PREWRITE_REFUSED -> PREWRITE_REFUSED
EMPTY -> WRITE_STARTED
PREWRITE_REFUSED -> WRITE_STARTED
WRITE_STARTED -> FILE_CREATED
FILE_CREATED -> FILE_CREATED
FILE_CREATED -> READY_TO_SEAL
WRITE_STARTED -> INTERRUPTED_PARTIAL
FILE_CREATED -> INTERRUPTED_PARTIAL
READY_TO_SEAL -> INTERRUPTED_PARTIAL
```

`PREWRITE_REFUSED` is the only permitted write when complete in-memory
validation has not passed. It has empty file maps and at least one refusal code.
`WRITE_STARTED` is appended immediately before the immutable log is created.
Each `FILE_CREATED` entry records exactly one newly created final path and its
verified hash; this includes one entry for the immutable log and one for each of
the 390 case files. `READY_TO_SEAL.created_file_hashes` is the exact cumulative
391-path map. `FILE_CREATED.created_file_hashes` contains its one path; the
remaining successful event types use an empty map.
`observed_partial_file_hashes` is nonempty only for `INTERRUPTED_PARTIAL`;
`causal_entry_sha256_or_null` then names the last valid write-chain entry and is
null otherwise. `READY_TO_SEAL` is appended only after the log and all 390 case
files exist, every hash equals the in-memory candidate, and no unexpected path
exists. The sealed manifest is then the last successful file write.

After a post-`WRITE_STARTED` interruption, recovery may inspect only the closed
final-plus-transient
inventory, must not create or alter any case/log/manifest/temp file, and appends exactly one
`INTERRUPTED_PARTIAL` entry containing the observed retained files. That state is
terminal. The same bundle ID/root may never resume or retry. Any superseding
attempt requires a separately approved plan, a new bundle ID, a new
authorization, and new roots; the partial bundle remains preserved.

After a valid manifest exists, any additional ledger byte invalidates the bundle.
The manifest therefore binds the exact `READY_TO_SEAL` ledger head.
If a process stops after the atomic manifest rename, recovery validates the
existing manifest read-only and returns sealed success; it appends nothing.

## Sealed manifest v2

Manifest v2 retains every v1 field and adds exactly:

```text
construction_log_sha256
construction_ledger_head_sha256
metric_schema_sharing_record_hashes
case_file_count
governance_file_count
total_file_count
```

The counts are exactly 390, 4, and 394. The ledger head must be a valid
`READY_TO_SEAL` entry. The log hash must equal the immutable log self-hash. All
v1 13/26/13 key-set and count relations remain unchanged. `manifest_sha256`
uses the null-placeholder rule, and `sealed_bundle_manifest.json` is the last
successful file created. `metric_schema_sharing_record_hashes` has exactly the
13 companion-group IDs as keys and the SHA-256 values of the final canonical
`metric_schema_sharing.json` file bytes. Each file's internal
`sharing_record_sha256` null-placeholder self-hash is validated separately.

## Deterministic DES seed lifecycle

No entropy is sampled and no seed is accepted from stdin, environment, network,
clock, filesystem discovery, or outcome-bearing data. The seed root is
deterministically recomputable from pre-outcome authorized inputs.

Construct this exact canonical object:

```json
{
  "approved_plan_artifact_hash": "<authorization value>",
  "bundle_id": "g6b_discovery_case_construction_v1",
  "case_recipe_registry_sha256": "<authorization value>",
  "frozen_row_family_matrix_sha256": "487d81aa79a7bca681db81f19a4d6bd315668c43b1c4538c47f01f099d8e205f",
  "plan_review_artifact_hash": "<authorization value>",
  "schema_version": "ims-deadlock/g6b-des-seed-root-material/v1",
  "source_head": "<authorization value>",
  "source_tree_hash": "<authorization value>"
}
```

`seed_root_hex` is SHA-256 of those canonical bytes. It is not serialized as a
free input. `seed_root_commitment` is SHA-256 of the canonical bytes of:

```json
{
  "schema_version": "ims-deadlock/g6b-des-seed-root-commitment/v1",
  "seed_root_hex": "<recomputed seed_root_hex>"
}
```

Every DES projection stores the same commitment and the exact rule code
`g6b_philox_length_prefixed_sha256_v2`. Later quantitative execution, if
separately authorized, must recompute the root from the sealed authorization and
refuse on commitment mismatch; there is no discretionary reveal step.

For replicate index `r`, derive the Philox key as SHA-256 over UTF-8 fields
encoded as an unsigned 8-byte big-endian length followed by bytes, in this exact
order:

```text
g6b_des_stream_v2
seed_root_hex
Philox
v1
case_content_sha256
des_companion
primary
base-10 replicate index without leading zeros
```

The projection declares 4096 replicates `[0,4096)`, draw counter `[0,B)` per
replicate where `B=min(65536,16*declared_state_bound)`, no common-random-numbers
group, and no antithetic pairing. The allocation record represents this closed
replicate domain; it does not enumerate or consume keys during construction.
Hash inequality is never presented as proof of statistical independence.

`substream_allocation` contains exactly one record with `stream_role=primary`,
`start_counter=0`, `stop_counter_exclusive=4096`, and `stride=1`; those counters
index replicate labels, while `sampling_plan.draw_budget_per_replication`
defines each derived Philox key's draw-counter domain. Its
`derivation_label_sha256` is SHA-256 of the canonical bytes of:

```json
{
  "case_content_sha256": "<validated projection hash>",
  "derivation_rule": "g6b_philox_length_prefixed_sha256_v2",
  "method_role": "des_companion",
  "prng_family": "Philox",
  "prng_version": "v1",
  "replicate_index_start": 0,
  "replicate_index_stop_exclusive": 4096,
  "schema_version": "ims-deadlock/g6b-des-derivation-domain/v1",
  "seed_root_commitment": "<recomputed commitment>",
  "stream_role": "primary"
}
```

## Intra-bundle metric sharing versus retired reuse

`metric_schema_sharing.json` documents only preregistered sharing among the 13
new companion groups. It has exactly:

```text
schema_version
sharing_record_id
bundle_id
method_companion_group_id
metric_schema_sha256
canonical_owner_method_companion_group_id
sharing_group_ids
sharing_reason_code
comparability_requirement
independent_case_evidence
retired_authority_reuse_claimed
retired_reuse_authorization_ref_or_null
review_artifact_hash
sharing_record_sha256
```

The canonical owner is the lexicographically first companion-group ID. The peer
`sharing_group_ids` array is the exact sorted 13-group roster.
`sharing_reason_code` is exactly
`same_preregistered_estimand_metric_and_scoring_contract`;
`comparability_requirement` is exactly `exact_des_and_cross_case_schema_parity`;
`independent_case_evidence=false`; `retired_authority_reuse_claimed=false`; and
`retired_reuse_authorization_ref_or_null=null`.

Every construction companion-group record sets
`allowed_reuse_reason_code=intra_bundle_preregistered_comparability_only` and
`reuse_authorization_ref_or_null=null`. The sharing record's
`review_artifact_hash` equals the approved v2 plan-review artifact hash.

The existing retired `metric_schema_reuse_record` contract remains unchanged in
the overlap/retired-normalization schemas but is removed from construction-file
requirements. Such a record may be created only after separately authorized
retired normalization establishes the exact retired authority, lineage, and
metric hash. Equality among the 13 new metric projections is comparability
evidence only and never case-independence evidence.

## Materializer write DAG

The only successful DAG is:

```text
approved v2 plan and review
  -> clean reviewed source commit C2
  -> validated authorization v2
  -> complete in-memory 13/26/13 candidate
  -> exact schema/hash/path/forbidden-call closure
  -> WRITE_STARTED ledger entry
  -> immutable construction log and its FILE_CREATED entry
  -> 390 create-new case files with FILE_CREATED entries
  -> READY_TO_SEAL ledger entry
  -> sealed manifest v2 as final write
```

All candidate bytes and hashes are finalized in memory before `WRITE_STARTED`.
Every file creation is create-new, same-directory temporary write plus atomic
rename, with refusal if either temporary or final path already exists. No
overwrite, delete, truncate, cleanup, resume, favorable-subset seal, or path
inference is permitted.

## Review and stop conditions

The revised plan must be independently reviewed for schema closure, scientific
boundary preservation, source identity, recovery safety, random-stream
determinism, metric-sharing ontology, and exact file/count reconciliation.

Implementation must stop before authorization if any file role, schema version,
field set, hash subject, seed derivation, ledger transition, source identity, or
metric relation still requires invention. After a sealed bundle passes review,
stop at the separate retired-authority-normalization authorization boundary.
