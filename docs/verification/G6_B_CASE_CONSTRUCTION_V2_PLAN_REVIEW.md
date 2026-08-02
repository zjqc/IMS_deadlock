# G6-B Case Construction v2 Plan Review

Status: `APPROVE / PLAN-ONLY / NO IMPLEMENTATION AUTHORITY`

Date: 2026-08-02

## Reviewed subject

- Remote worktree:
  `D:\worktree\IMS_deadlock-g6b-case-construction-contract-revision`.
- Branch: `codex/g6b-case-construction-contract-revision`.
- Subject commit: `79091b863db897e3087640d0c72eb154751a5f6d`.
- Subject tree: `e837d7d8bf680bb8d22211fdd20543e3bf6d5ebb`.
- Base commit: `01cf48c7623fa2d4652a1397c79c3c6202cf84fb`.
- Base tree: `6e7fef9323d6b827fd9555df16b33d6dd3b31642`.
- Corrigendum:
  `docs/superpowers/specs/2026-08-02-g6b-case-construction-materialization-contract-corrigendum.md`.
- Corrigendum SHA-256:
  `ff469d9c5105835fde5feb170e501bdde14506df50632990f7c2cddc251da36c`.
- Revised plan:
  `docs/superpowers/plans/2026-08-02-g6b-case-construction-v2.md`.
- Revised-plan SHA-256:
  `81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7`.

The commit contains exactly the two reviewed documents. The reviewers inspected
content-addressed bytes with the same two SHA-256 values before publication; the
remote commit and local reviewed subject were proven byte-identical.

## Trigger and retained intermediate evidence

Task-2 TDD against the prior approved plan first produced the intended RED:
module collection failed only because
`ims_deadlock.g6b_case_materializer` and
`validate_construction_authorization` were absent. The retained intermediate
GREEN was `442 passed in 109.73s`, but the implementation generated generic
candidate wrappers rather than final schema-valid bytes and had no reviewed
writer/sealer/recovery contract. It was correctly not committed or pushed.

The original implementation worktree remains dirty at the prior Task-1 source
commit with exactly four Task-2 paths. It is forensic draft evidence, not a
partial pass or implementation source. No construction authorization, case root,
normalization root, target-certification root, quantitative root, or scientific
output was created.

## Review method

Three independent review lanes assessed the same content hashes:

1. ontology and scientific-boundary review;
2. mechanical field/count/hash/DAG/path verification;
3. adversarial implementability and failure-recovery review.

Reviews were sequentially repeated after each material correction. A rejection
was not waived. The final byte subject was accepted only after every blocking
finding was repaired and all three lanes returned PASS.

## Retained negative review history

The review retains, rather than hides, the following rejected draft states:

1. The first draft placed all downstream case-file hashes in
   `construction_log.json` while semantic-lineage files referenced the log hash.
   This formed a direct log/lineage hash cycle. The final contract stores only
   the 390 planned paths in the upstream log; downstream hashes are sealed by
   ledger/manifest.
2. The first draft did not account for a crash between same-directory temporary
   write and atomic rename. The final contract defines exactly 393 deterministic
   transient paths, preserves and hashes them on interruption, and requires all
   of them absent on sealed success.
3. The first ledger draft used canonical JSON Lines but could not retain a torn
   append while remaining parseable. The final contract uses RS/canonical-JSON/LF
   frames and an ordered `interrupted_fragments` array that binds one or repeated
   torn frames without rewriting bytes.
4. An intermediate draft used sharing-record self hashes in a manifest map whose
   global semantics required final-file-byte hashes. The final contract stores
   final canonical file-byte SHA-256 values in the manifest and validates the
   internal null-placeholder self hash separately.
5. Source identity initially named only two source files and did not close C3/C4
   publication diffs. The final contract binds nine C2 paths, restricts C2..C3
   to the exact 394 artifacts, and restricts C3..C4 to three named documentation
   paths.

## Final mechanical closure

The final corrigendum and plan agree on:

- 36 exact construction-schema v3 top-level keys;
- four exact governance files;
- 30 exact files per case root;
- 13 case units, 26 method observations, and 13 companion groups;
- 390 case files plus four governance files, 394 final files total;
- 393 possible deterministic transient paths, all absent on success;
- 17 exact `case_artifact_paths` keys;
- 23 construction-authorization v2 fields;
- 19 immutable construction-log fields;
- 16 append-only ledger-entry fields;
- one immutable upstream construction log with no downstream hash cycle;
- one RS/canonical-JSON/LF ledger sequence with ordered torn-fragment recovery;
- one final-file-byte hash meaning for manifest record-hash maps;
- separate validation of null-placeholder self hashes;
- a manifest-last success DAG and terminal no-resume partial state;
- a deterministic, pre-outcome, recomputable DES seed commitment;
- intra-bundle metric sharing separated from later retired-authority reuse; and
- clean C2 source, artifact-only C3, and documentation-only C4 phases.

## Final reviewer verdicts

### Ontology and scientific boundary

Verdict: `PASS`.

The review found no remaining category error among schema, instance,
capability, comparison projection, fingerprint envelope, method descriptor,
metric sharing, retired reuse, seed reproducibility, independence, ledger
evidence, or scientific evidence. A method-observation record is explicitly a
preregistered descriptor, not an empirical observation. Four typed capabilities
remain false, and no materialization evidence is upgraded to a scientific pass.

Final finding counts: `Critical=0, High=0, Medium=0, Low=0`.

### Mechanical field/count/hash/DAG/path verification

Verdict: `PASS`.

The reviewer mechanically counted 36/30/23/19/16 contract blocks, reconciled
`30*13+4=394`, verified the 393-path transient closure, verified absence of the
log/lineage cycle, verified manifest sharing hash semantics, verified ordered
torn-fragment recovery, and reconciled the exact C2/C3/C4 path boundaries.

Final finding counts: `Critical=0, High=0, Medium=0, Low=0`.

### Adversarial implementability and recovery review

Verdict: `PASS`.

The final review found the specification and plan implementable without
inventing any file role, schema version, hash subject, ledger transition,
transient path, source identity, seed rule, metric relation, or approval gate.
It confirmed that every earlier Critical/High finding was repaired in the final
content-addressed bytes.

Final finding counts: `Critical=0, High=0, Medium=0, Low=0`.

## Verification evidence

Remote SHA-256 verification returned:

```text
ff469d9c5105835fde5feb170e501bdde14506df50632990f7c2cddc251da36c  corrigendum
81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7  revised plan
```

The qualified remote Python 3.13.9 contract-document validator returned:

```text
CONTRACT_DOCS_OK spec_sha256=ff469d9c5105835fde5feb170e501bdde14506df50632990f7c2cddc251da36c plan_sha256=81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7 top_keys=36 case_files=30 auth_fields=23 log_fields=19 ledger_fields=16 total_files=394
```

`git diff --check` passed before commit. The committed subject was clean after
publication, and `git show --stat` reported exactly two created files and 1171
insertions.

No slow scientific test or experiment was needed for this plan-only correction.
The prior implementation full suite remains historical Task-1 evidence and was
not falsely rebound to this documentation-only subject.

## Approval and scope verdict

The reviewed v2 plan is approved for exact-bytes user consideration. User
approval must name both:

- revised-plan SHA-256
  `81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7`;
- this review artifact's exact SHA-256, computed after publication.

Until that exact approval exists, do not create the v2 implementation worktree,
modify schema/code/tests, create construction authorization, write case bytes,
normalize retired authorities, run overlap/preflight/CTMC/DES, inspect outputs,
or change G6-B from `OPEN/PENDING`.
