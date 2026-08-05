# G6-B Case Construction v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development` (recommended) or `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce one reviewed, discovery-only, sealed G6-B construction bundle with exactly 13 case units, 26 method observations, 13 exact/DES companion groups, 390 case files, and four governance files, without opening any downstream scientific gate.

**Architecture:** A schema-first revision closes every file role, source identity, random-stream commitment, metric-sharing relation, and append-only recovery transition before writer code is accepted. The materializer validates the complete 394-file success state and ledger sequence before writing through a create-new forward-only DAG, then seals with the manifest as the last successful file. Any partial write is retained and terminal for that bundle identity.

**Tech Stack:** Python 3.13.9, project canonical-JSON/self-hash utilities, pytest, Ruff, mypy, Git linked worktrees, Windows remote runtime.

---

Status: `PROPOSED / PLAN-ONLY / AWAITING EXACT-BYTES USER APPROVAL`

Date: 2026-08-02

## Authority, prior evidence, and supersession

This plan supersedes Tasks 2-7 of
`docs/superpowers/plans/2026-08-02-g6b-case-construction.md`. Its Task 1 is
already complete and remains valid at implementation baseline commit
`01cf48c7623fa2d4652a1397c79c3c6202cf84fb`, tree
`6e7fef9323d6b827fd9555df16b33d6dd3b31642`.

The immutable prior identities are:

- original approved plan SHA-256:
  `c20393328f8f98e7b35a6507fd6e993b2f17e068d977c3dc6253b05e9a75de5f`;
- prior plan-review SHA-256:
  `297a69382347e16e894af63e70f8fa95807407048b2e89c45701410a4e9289e1`;
- approved design SHA-256:
  `b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6`;
- completed estimand-scope corrigendum SHA-256:
  `5b5266a562fb4e1515121a351d0b98227338bf34c991eef2fe76557b0e17334f`;
- completed Task-1 review SHA-256:
  `744cac6caff24779d862704ad83d186023ea918f06f941e78fcc2f797c1b07c7`;
- frozen row-family matrix SHA-256:
  `487d81aa79a7bca681db81f19a4d6bd315668c43b1c4538c47f01f099d8e205f`;
- materialization-contract corrigendum:
  `docs/superpowers/specs/2026-08-02-g6b-case-construction-materialization-contract-corrigendum.md`;
- materialization-contract corrigendum SHA-256:
  `ff469d9c5105835fde5feb170e501bdde14506df50632990f7c2cddc251da36c`.

The earlier implementation worktree
`D:\worktree\IMS_deadlock-g6b-case-construction` is intentionally preserved
with exactly four uncommitted Task-2 draft paths. They contain useful RED/GREEN
intermediate evidence but are stale against this plan. Do not reset, clean,
stash, commit, transfer, or use them as test truth.

After exact approval, create a fresh worktree and branch from the exact commit
that publishes this plan, its corrigendum, and the independent plan review:

```text
worktree: D:\worktree\IMS_deadlock-g6b-case-construction-v2
branch:   codex/g6b-case-construction-v2
base:     exact approved plan-publication commit
```

The remote runtime is:

```text
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe
```

Every Python command sets
`PYTHONPATH=D:\worktree\IMS_deadlock-g6b-case-construction-v2\src` and
`PYTHONDONTWRITEBYTECODE=1`, and disables pytest cache with
`-p no:cacheprovider`.

## Approval semantics and stop boundary

Approval must name this plan's exact SHA-256 and the independent plan-review
artifact SHA-256. A general instruction to continue does not approve changed
bytes. Approval opens only Tasks R1-R7 below; no task begins from the old dirty
worktree.

The four canonical capabilities remain false. The tranche creates no retired-
authority normalization, overlap report, Barrier-A authorization, target
certificate, CTMC, DES output, Barrier-B authorization, G6-B verdict, or paper
claim. After Task R7, stop at the separately approved retired-authority-
normalization authorization boundary.

## Fixed roster and output surface

The exact roster, scientific recipes, hypotheses, falsifiers, controls,
estimands, metric rules, and case IDs remain those in the original approved
plan. No case may be added, removed, renamed, copied from retired payloads, or
post-outcome tuned.

The corrected per-case file inventory is the exact 30-file list in the
materialization-contract corrigendum. The total closed inventory is:

```text
13 case units * 30 files = 390 case files
4 governance files        =   4 governance files
total                     = 394 files
```

The materializer performs one logical materialization run in Task R5. It
does not run separate commands that partially create cases, then methods, then
metrics.

## Task R1: implement and test construction-schema v3

**Files**

- Modify:
  `cases/discovery/g6b/row_families/structural_discovery_v1/case_construction_schema.json`.
- Modify only the exact manifest/hash closure required by that byte change in:
  `cases/discovery/g6b/row_families/structural_discovery_v1/row_family_protocol.json`.
- Modify:
  `src/ims_deadlock/g6b_row_family_protocol.py` and
  `src/ims_deadlock/g6b_schema_contracts.py`.
- Modify:
  `tests/test_g6b_row_family_protocol.py` and
  `tests/test_g6b_schema_contracts.py`.
- Do not modify the other ten nested schema-governance JSON files.

- [ ] **Step 1: add RED tests for the v3 top-level closure**

  Add exact-key tests requiring schema version v3 and these new/updated
  contracts: `materialization_file_contracts`, `construction_log_contract`,
  `construction_ledger_contract`, `source_identity_contract`,
  `transient_path_contract`, `des_seed_contract`,
  `metric_schema_sharing_record_required_fields`, manifest v2 additions, the
  exact v3 top-level key set, the 30-file case inventory, and the 17-key
  `case_artifact_paths_required_keys` array.

- [ ] **Step 2: add RED tests for every concrete file role**

  Parameterize all 30 relative paths and assert exact schema version, record
  class, hash meaning, projection subject, and direct-stored fingerprint target.
  Assert that the five formerly absent projections are required and that
  `metric_schema_reuse.json` is prohibited in construction roots.

- [ ] **Step 3: add RED tests for ledger/log/source/seed/metric semantics**

  Test exact log and ledger field arrays, event enums and transitions,
  READY-to-manifest DAG, authorization-v2 source fields, deterministic seed
  golden vectors, the 393-path transient inventory, sharing-record constants,
  the 13-key manifest sharing-record final-file-byte hash map plus separate
  sharing self-hash validation, refusal vocabulary v2,
  removal of retired-reuse fields from construction v3, and the unchanged
  retired reuse record in the overlap/retired schemas.

- [ ] **Step 4: run RED and retain the intended failure set**

  Run:

  ```bat
  D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_g6b_schema_contracts.py tests\test_g6b_row_family_protocol.py
  ```

  Expected: failures only for missing v3 constants/contracts and the old file
  inventory; no collection error or unrelated regression.

- [ ] **Step 5: implement the exact v3 schema and validators**

  Use immutable constants for the 30-path map, log/ledger field tuples, event
  transition map, authorization-v2 fields, seed rule, sharing fields, and counts.
  `validate_construction_ledger_bytes()` parses the exact RS/canonical-JSON/LF
  sequence, verifies retained interrupted fragments, and verifies the complete
  hash chain and state machine. The ordinary JSON loader remains duplicate-
  member rejecting and must reject the ledger sequence as an ordinary object.

- [ ] **Step 6: update only required protocol hashes and validators**

  Update the case-construction schema version and canonical manifest digest.
  Assert byte identity for all untouched nested schema files and preserve all
  four typed capabilities as literal false.

- [ ] **Step 7: run GREEN and static checks**

  Run the focused pytest command above, then:

  ```bat
  D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -B -m ruff check src\ims_deadlock\g6b_row_family_protocol.py src\ims_deadlock\g6b_schema_contracts.py tests\test_g6b_row_family_protocol.py tests\test_g6b_schema_contracts.py
  D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -B -m ruff format --check src\ims_deadlock\g6b_row_family_protocol.py src\ims_deadlock\g6b_schema_contracts.py tests\test_g6b_row_family_protocol.py tests\test_g6b_schema_contracts.py
  D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -B -m mypy src\ims_deadlock\g6b_row_family_protocol.py src\ims_deadlock\g6b_schema_contracts.py tests\test_g6b_row_family_protocol.py tests\test_g6b_schema_contracts.py
  git diff --check
  ```

- [ ] **Step 8: commit the schema increment**

  Commit only the four task-owned code/test paths and two JSON paths after
  verifying the remaining exact-twelve files are byte-identical to baseline.

## Task R2: rebuild the full in-memory materializer by TDD

**Files**

- Create:
  `src/ims_deadlock/g6b_case_materializer.py` and
  `tests/test_g6b_case_materializer.py`.
- Modify only if required by an already RED schema assertion:
  `src/ims_deadlock/g6b_schema_contracts.py` and
  `tests/test_g6b_schema_contracts.py`.

The old four-file draft is not copied wholesale. Every retained line must be
audited against this plan; generic `*-candidate/v1` wrappers and inferred schema
versions are prohibited.

- [ ] **Step 1: add RED tests for authorization v2 and source baseline**

  Require exact fields, literal `authorized is True`, literal
  `invalidated_by_identity_drift is False`, exact 13/26/13 scope, source
  HEAD/tree and exact nine-path hash map,
  schema/recipe/matrix/corrigendum/plan/review hashes,
  exact operations, self hash, and clean-C2 creation. Runtime validation accepts
  only closed output-path dirtiness and rejects any tracked source drift. Add a
  separate post-seal mode that accepts descendant C3/C4 publication commits only
  when C2 is an ancestor and the authorized source/schema hashes are unchanged.

- [ ] **Step 2: add RED tests for the full recipe catalog**

  For all 13 approved cases, assert the complete state/route/resource/rate/
  policy/target/control/prediction/lineage recipe objects, not only IDs and
  labels. Assert exact 13/26/13 counts, the seven control IDs, both input modes,
  unique case-content projections, and the frozen recipe-registry golden hash.

- [ ] **Step 3: add RED tests for all 390 in-memory case files**

  `build_candidate_bundle()` must return canonical final bytes and hashes for
  every exact file, plus immutable log bytes, ledger-ready metadata, and manifest
  bytes. Tests validate all cross-references, fingerprint projection refs,
  self-hashes, record-byte hashes, sorted key sets, 390/4/394 counts, and zero
  filesystem writes.

- [ ] **Step 4: add seed and metric-sharing golden tests**

  Recompute the seed root and commitment from a fixed authorization vector;
  verify the exact eight-byte length-prefix derivation vector for replicate 0
  and 4095; reject any clock/environment/input seed. Assert one identical metric
  projection hash, 13 distinct sharing records, the lexicographically first
  canonical owner, exact 13-ID `sharing_group_ids` roster, false
  independence/reuse booleans, and null retired-reuse reference. Assert each
  companion group's intra-bundle reason code and null reuse-authorization ref.

- [ ] **Step 5: add negative import/call and duplicate-key tests**

  Parse the module AST and reject imports/calls reaching analysis/enumeration,
  terminal classification, CTMC, DES, retired normalization, preflight,
  quantitative output, network, subprocess, stdin, or outcome-bearing payloads.
  The CLI must load authorization with the canonical duplicate-member rejecting
  loader, not plain `json.loads`.

- [ ] **Step 6: run RED**

  Run:

  ```bat
  D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_g6b_case_materializer.py tests\test_g6b_schema_contracts.py
  ```

  Expected: missing materializer symbols/contracts only.

- [ ] **Step 7: implement immutable data builders**

  Implement focused functions with these stable boundaries:

  ```python
  def validate_construction_authorization_for_materializer(...) -> Mapping[str, object]: ...
  def build_case_recipe_catalog() -> Mapping[str, object]: ...
  def derive_seed_root_hex(authorization: Mapping[str, object]) -> str: ...
  def derive_philox_key_hex(..., replicate_index: int) -> str: ...
  def build_candidate_bundle(authorization: Mapping[str, object]) -> CandidateBundle: ...
  def validate_candidate_bundle(candidate: CandidateBundle) -> None: ...
  ```

  Builders return frozen structures or immutable bytes. They receive no observed
  data and perform no filesystem action.

- [ ] **Step 8: reach focused GREEN**

  Re-run the RED command. Then run Ruff check/format, strict mypy, and
  `git diff --check` on the four owned source/test paths.

## Task R3: implement create-new writer, ledger, and terminal recovery

**Files**

- Modify:
  `src/ims_deadlock/g6b_case_materializer.py` and
  `tests/test_g6b_case_materializer.py`.

- [ ] **Step 1: add RED writer tests**

  Use a temporary repository root. Require complete in-memory validation before
  touching disk; same-directory temporary files; exclusive create; atomic rename;
  exact path containment; verified final hash; and manifest-last ordering.
  Require the exact deterministic 393-path transient map. Existing temp/final
  paths, symlinks, escapes, unexpected files, or reserved quantitative roots
  must refuse without overwrite/delete.

- [ ] **Step 2: add RED ledger state-machine tests**

  Test exact RS/canonical-JSON/LF frames, exact fields, entry indices,
  prior/self hashes, valid transitions, exactly 391 FILE_CREATED entries (one log
  plus 390 case files), cumulative 391-path READY map, and rejection of CRLF,
  blank/noncanonical/corrupt/reordered/truncated chains. Inject one and repeated
  torn appends and require the next complete recovery frame's ordered
  `interrupted_fragments` array to bind every retained raw fragment hash and byte
  count. A pre-write refusal may append only PREWRITE_REFUSED.

- [ ] **Step 3: add RED interruption/recovery tests**

  Inject failure before log creation, after log creation, at each file-order
  boundary class, immediately before READY, and immediately before manifest
  rename. Preserve all partial final and temp bytes. Recovery inventories only
  the closed 394 final plus 393 transient paths, appends one causal
  INTERRUPTED_PARTIAL entry, creates no other byte, and makes the same bundle
  permanently non-resumable. A completed manifest rename is detected as sealed
  success and causes no ledger append.

- [ ] **Step 4: implement the forward-only writer**

  Implement these explicit operations:

  ```python
  def append_ledger_entry_exclusive(...) -> LedgerEntry: ...
  def create_atomic_file_exclusive(path: Path, final_bytes: bytes) -> str: ...
  def materialize_candidate(repo_root: Path, candidate: CandidateBundle) -> None: ...
  def recover_interrupted_bundle(repo_root: Path, authorization: Mapping[str, object]) -> None: ...
  ```

  No cleanup, resume, overwrite, truncation, or favorable-subset path exists.

- [ ] **Step 5: run writer GREEN and mutation tests**

  Run the focused materializer/schema command, then Ruff, format check, mypy,
  canonical JSON mutation tests, and `git diff --check`.

## Task R4: obtain exact Task-R2/R3 review and freeze clean source C2

**Files**

- Create:
  `docs/verification/G6_B_CASE_CONSTRUCTION_TASK2_SOURCE_REVIEW.md`.

- [ ] **Step 1: run the full focused source validation on one staged source manifest**

  Record exact source/schema/test hashes and commands. The review artifact binds
  those hashes, not a future commit ID, so it can be committed with the reviewed
  source without a self-reference cycle.

- [ ] **Step 2: obtain sequential spec-compliance and code-quality reviews**

  The spec reviewer checks every corrigendum requirement. Only after PASS, the
  code-quality reviewer checks safety, determinism, exception paths, types, and
  tests. Fixes require re-running both affected reviews.

- [ ] **Step 3: commit source and review together as C2**

  Commit all R2/R3 source/tests plus the review artifact. Re-run targeted tests
  from clean C2 and record `HEAD`, `HEAD^{tree}`, the exact nine-path hash map,
  schema hash, recipe-registry hash, and review-artifact hash. No protected-path
  edit is allowed after this point without discarding authorization and
  repeating R4.

## Task R5: create and validate authorization, then materialize once

**Files**

- Create only under the exact governance/case roots listed in the corrigendum.

- [ ] **Step 1: re-lock clean C2 and create authorization v2**

  Require exact path, branch, HEAD/tree, upstream relation, clean state, source
  hashes, plan/corrigendum/review/schema/recipe/matrix hashes, and 13/26/13 scope.
  Write only `construction_authorization.json` through its deterministic
  create-new transient path, validate it, require the temp path absent, and
  verify every later root is still absent. Any retained authorization temp is a
  preserved blocker, not permission to delete or retry the same bundle.

- [ ] **Step 2: run a pure dry run**

  Build and validate all candidate bytes in memory; print only IDs, counts, and
  hashes. Require 390/4/394, exact 13/26/13, exact seven controls, zero forbidden
  roots, and zero unexpected existing paths.

- [ ] **Step 3: run one bounded materialization command**

  Use one worker, 600-second wall/CPU bounds, and 2 GiB memory bound. The process
  writes log, 390 case files, ledger events, and manifest through the approved
  DAG. It consumes zero random draws and performs no scientific computation.

- [ ] **Step 4: handle outcomes fail-closed**

  On success, require manifest-last and the exact READY ledger head. On any
  interruption, run recovery once, retain all partial files, mark the bundle
  terminal, and stop this plan; do not retry with the same bundle ID.

## Task R6: verify the sealed bundle and repository

- [ ] **Step 1: run artifact-only verification**

  Reparse every ordinary JSON file with duplicate-member rejection, every ledger
  text-sequence frame as canonical JSON, every self hash, every record-byte hash,
  every ref, every ID/key-set/count relation, and the exact 394-file inventory.
  Assert all 393 transient paths, reserved directories, target-certification
  roots, quantitative roots, and scientific outputs are absent.

- [ ] **Step 2: run focused tests and static checks**

  Run:

  ```bat
  D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_g6b_case_materializer.py tests\test_g6b_schema_contracts.py tests\test_g6b_row_family_protocol.py tests\test_g6b_protocol.py
  D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -B -m ruff check src\ims_deadlock\g6b_case_materializer.py src\ims_deadlock\g6b_schema_contracts.py src\ims_deadlock\g6b_row_family_protocol.py tests\test_g6b_case_materializer.py tests\test_g6b_schema_contracts.py tests\test_g6b_row_family_protocol.py tests\test_g6b_protocol.py
  D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -B -m ruff format --check src\ims_deadlock\g6b_case_materializer.py src\ims_deadlock\g6b_schema_contracts.py src\ims_deadlock\g6b_row_family_protocol.py tests\test_g6b_case_materializer.py tests\test_g6b_schema_contracts.py tests\test_g6b_row_family_protocol.py tests\test_g6b_protocol.py
  D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -B -m mypy src\ims_deadlock\g6b_case_materializer.py src\ims_deadlock\g6b_schema_contracts.py src\ims_deadlock\g6b_row_family_protocol.py tests\test_g6b_case_materializer.py tests\test_g6b_schema_contracts.py tests\test_g6b_row_family_protocol.py tests\test_g6b_protocol.py
  git diff --check
  ```

- [ ] **Step 3: analyze and run the full suite with remote parallelism**

  Before execution, recollect the test count and verify CPU/RAM plus xdist
  availability. Do not install into the shared project venv. If needed, install
  `pytest-xdist` into an explicit task-owned directory outside the repository,
  record its resolved version/hash, prepend it to `PYTHONPATH`, and use
  `-n 4 --dist=worksteal`. Four workers are the initial evidence-backed setting;
  change it only after an actual bounded timing sample. Capture live percentage
  progress and estimate completion only from observed throughput.

  Run the full suite once on the final subject. A run projected under 24 hours is
  allowed to finish. A live projection above 24 hours stops for user approval.

- [ ] **Step 4: commit the sealed artifact subject C3**

  Commit C3 as an artifact descendant of C2: include the exact 394 artifact
  files and no other path. No source, schema, test, review, documentation, or
  schema-governance byte may differ from C2; if one
  does, discard authorization and repeat R4. Record C3 HEAD/tree and prove the
  reserved/forbidden roots remain absent.

## Task R7: three-way independent review, handoff, and publication

**Files**

- Create:
  `docs/verification/G6_B_CASE_CONSTRUCTION_REVIEW_V2.md`.
- Modify:
  `PROJECT_HANDOFF.md` and `docs/ROADMAP.md`.

- [ ] **Step 1: review the same C3 commit in three independent lanes**

  1. ontology/estimand and metric-sharing reviewer;
  2. scientific-boundary, nonreuse, source/seed, and recovery reviewer;
  3. code/capability, schema/hash, artifact-scope, and test-evidence reviewer.

  Each reports exact subject, commands, findings, and verdict. Any finding is
  fixed on a new subject and all affected reviews/tests repeat.

- [ ] **Step 2: publish review and durable handoff**

  Record exact plan/corrigendum/review/source/authorization/log/ledger/manifest
  hashes, 13/26/13 and 390/4/394 counts, focused/full test evidence, static checks,
  branch/upstream state, PR, retained negative/partial evidence, and unchanged
  downstream gates.

- [ ] **Step 3: commit documentation as C4, push, and open/update a draft PR**

  C4 changes exactly the three R7 documentation paths and no artifact/source/
  schema/test path. Push without force. Do not merge. The old dirty worktree and its draft PR are
  labeled superseded only after the v2 branch is published and verified; neither
  is deleted or rewritten.

## Verification claims

Completion proves only that one exact discovery construction bundle is sealed,
hash-valid, reviewed, and non-scientific. It does not prove retired-authority
distinctness, pass Barrier A or B, validate a target, establish exact/DES
same-target equivalence, estimate an outcome, or upgrade G6-B from
`OPEN/PENDING`.

## Mandatory stop

After R7, stop. The first possible next tranche is separately authorized,
data-only retired-authority fingerprint normalization. If this plan exposes any
new identity-bearing ambiguity, schema mismatch, unexpected output path,
source drift, partial write, test failure, or reviewer finding, stop before the
next downstream task and revise the reviewed bytes rather than inventing a
repair.
