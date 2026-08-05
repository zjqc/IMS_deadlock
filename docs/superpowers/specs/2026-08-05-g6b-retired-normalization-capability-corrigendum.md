# G6-B Retired-Normalization Capability Corrigendum

**Status:** `PROPOSED / PLAN-ONLY / NOT EXECUTION AUTHORIZATION`

**Applies to:** the retired-authority fingerprint-normalization clauses of
`docs/superpowers/specs/2026-08-01-g6b-case-target-certification-design.md`
at raw SHA-256
`b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6`.

**Schema subject preserved:**
`cases/discovery/g6b/row_families/structural_discovery_v1/retired_authority_fingerprint_schema.json`
at raw SHA-256
`f0c8b649bee392752aec15aed28ac492584a6071d09ef7bdd963ee28a00323bc`.

## 1. Purpose and authority boundary

The frozen design defines a complete normalization output containing an
authorization record, authority-lock records, authority-source records,
fingerprint records, and a final manifest. Its v1 operation list and static
writer-symbol list name writers only for fingerprint records and the manifest.
Those bytes therefore do not provide a closed, implementable write path for
the declared artifact set. The same design omits
`ims_deadlock.g6b_schema_contracts` from the normalizer's project-import
allowlist even though the normalizer must use the approved fail-closed record
and authorization validators. It also names Git `source_head` and
`source_tree_hash` fields while the current authorization validator treats them
as 64-character SHA-256 values, and its singular `review_artifact_hash` does
not state how two required independent source reviews are aggregated.

This corrigendum repairs only those four execution-contract defects:

1. it closes the lexical writer surface for every declared normalization
   artifact class;
2. it permits the normalizer to call only the exact approved schema-contract
   validators and locks their transitive project-import closure;
3. it distinguishes repository Git object IDs from SHA-256 content digests;
4. it defines the canonical two-lane source-review bundle bound by
   `review_artifact_hash`.

It does not change the retired source inventory, selector matrix, producer
map, fingerprint dimensions, lineage semantics, output schema fields,
scientific estimand, or downstream gates. It does not authorize implementation,
retired-field parsing, normalization execution, overlap comparison, target
preflight, CTMC, DES, scoring, confirmation, or a claim upgrade. It becomes
operative only if the user exactly approves its final raw SHA-256 together
with the companion implementation plan and independent plan review.

## 2. Closed writer and operation contract

The exact `NORMALIZATION_ALLOWED_OPERATIONS` sequence is superseded only for
the writer portion. It is:

```text
read_authority_bytes
parse_allowed_json_pointers
verify_source_hashes
parse_historical_decimal_exactly
apply_static_input_projection
canonicalize_projection_v2
compute_sha256
write_normalization_authorization
write_authority_lock_record
write_authority_source_record
write_fingerprint_record
write_normalization_manifest
```

The exact `ALLOWED_NORMALIZER_WRITER_SYMBOLS` sequence is:

```text
ims_deadlock.g6b_retired_normalizer.write_normalization_authorization
ims_deadlock.g6b_retired_normalizer.write_authority_lock_record
ims_deadlock.g6b_retired_normalizer.write_authority_source_record
ims_deadlock.g6b_retired_normalizer.write_fingerprint_record
ims_deadlock.g6b_retired_normalizer.write_normalization_manifest
```

No generic writer, plugin, callback, publisher, staging-root promoter, or
filesystem escape is added. The five functions are the only top-level lexical
contexts in which the static guard may permit `Path.mkdir`,
`Path.write_bytes`, or `Path.replace`. A nested function, lambda, alias,
rebound symbol, helper, entrypoint, or caller does not inherit writer
authority. `open` in write/append mode, deletion, recursive traversal,
directory iteration, globbing, arbitrary rename, permission/ownership change,
network access, subprocess launch, and mutation outside the exact authorized
root remain forbidden.

Runtime containment is required in addition to lexical containment:

- `write_normalization_authorization` is the only function allowed to create
  the previously absent exact final root. It writes the exact independently
  approved authorization bytes as `normalization_authorization.json` and
  refuses a pre-existing root or file.
- `write_authority_lock_record` writes only one of the three exact filenames
  under `authority_locks/`.
- `write_authority_source_record` writes only
  `source_records/sha256(repo_relative_posix_source_path).json` for a path in
  the approved 27-file inventory.
- `write_fingerprint_record` writes only
  `fingerprints/sha256(record_id).json` for a validated record in the frozen
  producer closure.
- `write_normalization_manifest` writes only
  `normalization_manifest.json`, refuses until every referenced record exists
  with matching bytes, and is always called last.

Each record writer canonicalizes the record, creates at most its one fixed
direct child directory, writes a new sibling temporary file inside the exact
authorized root, verifies its byte SHA-256, and performs one same-directory
`Path.replace` to finalize the previously absent destination. No writer may
overwrite a finalized file. The root is complete only when the final manifest
independently validates. Any interruption preserves the incomplete root and
temporary evidence without a valid manifest; there is no cleanup, promotion,
or in-place retry. A later attempt would require a separately approved new
authorization and a new absent output root.

## 3. Closed schema-contract import surface

The exact `NORMALIZATION_ALLOWED_PROJECT_IMPORTS` sequence is:

```text
ims_deadlock.g6b_retired_normalizer
ims_deadlock.g6b_canonical_json
ims_deadlock.g6b_schema_contracts
ims_deadlock.g6b_governance
```

This addition does not grant general access to every symbol in
`g6b_schema_contracts`. The normalizer may call only these exact validator
symbols from that module:

```text
validate_normalization_authorization
validate_authority_lock_record
validate_authority_source_record
validate_fingerprint_record
validate_normalization_manifest
```

The module may also catch `SchemaContractError`; it may not alias, rebind,
dynamically resolve, or call any other schema-contract symbol. The source-only
implementation commit may modify `g6b_schema_contracts.py` but must keep its
transitive project-import closure exactly
`ims_deadlock.g6b_canonical_json`. Static tests must reject any extra direct or
transitive `ims_deadlock.*` import. The normalizer does not create or import a
new `g6b_governance.py`; the unchanged allowlist entry is not permission to add
that path to the four-file source/test commit closure.

## 4. Git object identity versus content hashes

Within `retired_authority_fingerprint_normalization_authorization`, manifest,
and related normalization lock records:

- `source_head` and `source_tree_hash` are caller-bound Git object IDs. Their
  lowercase hexadecimal length and algorithm must match the live repository's
  `git rev-parse --show-object-format`; the current repository is SHA-1 and
  therefore uses 40 hexadecimal characters.
- `origin_commit_or_null` and `origin_tree_hash_or_null`, when non-null, follow
  the object format of their explicitly locked origin repository.
- raw artifact hashes, record self-hashes, code hashes, inventory hashes,
  review hashes, and manifest hashes remain 64-character lowercase SHA-256.

Validators must receive the expected Git object IDs from the independently
locked caller and compare them exactly. They must not infer the expected
identity from the authorization record itself. Object-format drift or identity
drift is a typed refusal before retired-field parsing.

## 5. Canonical two-lane source-review bundle

After implementation and tests are frozen at one exact candidate HEAD/tree,
two independent reviews must evaluate those same bytes. Any source/test change
invalidates both reviews and requires both lanes to rerun. The final accepted
reviews are aggregated as canonical JSON v2 with exactly these fields:

```text
schema_version
bundle_id
source_head
source_tree_hash
normalizer_code_sha256
lane_reviews
p0_count
p1_count
p2_count
created_at_utc
source_review_bundle_sha256
```

`lane_reviews` is a sorted two-element array. Each element has exactly:

```text
lane_id
subject_head
subject_tree_hash
review_scope
verdict
review_raw_sha256
p0_count
p1_count
p2_count
```

The lane IDs are exactly `implementation_contract` and
`scientific_boundary`. Both subjects must equal the bundle's source HEAD/tree;
both verdicts must be `PASS`; aggregate counts must equal the lane sums; and
aggregate P0/P1 counts must be zero. `source_review_bundle_sha256` is the
finalized canonical self-hash. The authorization field
`review_artifact_hash` equals the raw SHA-256 of the final canonical bundle
bytes. The authorization reviewer recomputes both the bundle self-hash and raw
hash and verifies every referenced lane review.

## 6. Precedence and unchanged clauses

After exact approval, this corrigendum narrowly supersedes only:

- the two-writer operation/symbol lists in the retired-normalization clauses;
- the normalizer project-import list solely to admit the exact closed
  schema-contract validator surface above;
- any interpretation of normalization Git object IDs as SHA-256 content
  digests;
- any interpretation that a single unaggregated review can satisfy the
  two-lane source-review requirement.

All other clauses and frozen bytes remain authoritative. If the implementation
requires any additional read, transform, import, writer, path, output field,
retry, or scientific capability, it must stop with a typed refusal and obtain
a new separately reviewed exact plan; this corrigendum cannot be broadened by
implementation convenience.
