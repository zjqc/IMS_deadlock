# G6-B Retired-Authority Normalization Review

Status: `RETIRED_AUTHORITY_NORMALIZATION_COMPLETE / G6-B OPEN-PENDING`

Date: 2026-08-05 UTC

## 1. Claim boundary

This tranche closes a canonical, data-only retired-authority corpus for the
frozen G4, G5, and G6-R R3 inputs. It does not compare any sealed G6-B input
with that corpus. Consequently:

- normalization completeness is established;
- later comparison eligibility or a typed refusal is established per retired
  fingerprint record;
- actual input-level overlap is not established;
- semantic independence is not established by hashes alone;
- Barrier-A target certification, exact/CTMC execution, DES execution,
  scoring, output inspection, and a G6-B scientific verdict remain unopened.

The exact terminal statement is therefore
`RETIRED_AUTHORITY_NORMALIZATION_COMPLETE / G6-B OPEN-PENDING`, not
`G6-B PASS` and not `ACTUAL_OVERLAP PASS`.

## 2. Frozen subject and commit chain

The authoritative worktree was
`D:\worktree\IMS_deadlock-g6b-retired-normalization` on branch
`codex/g6b-retired-normalization`.

| Role | Commit | Tree | Scope |
| --- | --- | --- | --- |
| C1 source/test subject | `90214d4ecbb7ac62492966c7ede3ca68da259cd7` | `66e951ebb34e95912a4f496fcf6c783fdd1144da` | exact-decimal retired parser repair; two paths only |
| C2 artifact-only successor | `73916f2d5a1a5ae644f3fa0be42b17fcada097d9` | `d8cd83e473292b1c8f83d701abb830c395a3184c` | exact normalization root; 213 paths only |
| C3 documentation-only successor | resolve with `git log -1 --format=%H -- docs/verification/G6_B_RETIRED_AUTHORITY_NORMALIZATION_REVIEW.md` | resolve from live Git | this review, `PROJECT_HANDOFF.md`, and `docs/ROADMAP.md` only |

C1 raw file hashes were:

- normalizer:
  `1ef0645b172a037c36c5fc8a0fa93d4ad455a17aa9f97f6e1cea57af8f9e5516`;
- normalizer tests:
  `a79c38148ff30ce319f1bca0dfc606479673cdb31a78ed38775c5f4c745905ad`;
- unchanged schema contracts:
  `a15ee72d4274199ea35b2aa3f5051984d7972cc06a5be4561846f62173b8bd0f`;
- unchanged canonical JSON helper:
  `92317a4e4a7bd954a7b4650d969e6c78dd6d5e0fc93b27a4c24915b010dfcf8d`;
- unchanged schema tests:
  `5ae1208b1716bcbfb7ffb3d1ca6dba4809868bc5cccc3ce7468f74797e0f6aa7`.

The repaired generic selector remains canonical-v2 strict and rejects binary
floats. Only the private frozen-G4 case-content path converts valid
non-integral historical JSON number tokens to exact canonical decimal strings.
Duplicate members, non-NFC strings, negative zero, nonfinite tokens, malformed
numbers, unauthorized pointers, and raw-bytes-only misuse still refuse closed.

## 3. Approved authorization and single execution

The user explicitly approved these exact identities before the one successful
normalizer execution:

| Artifact | SHA-256 |
| --- | --- |
| authorization raw bytes | `fc04ffe450dee355ac89b7b201be287eff4caa6d892dc698f462300721b10c6c` |
| authorization finalized self-hash | `646787f1888e3254d63da0a37af0287e1bb66b14ab78f09b54b7eeab0162f0eb` |
| independent authorization review raw bytes | `bfcfa4a9b378f2602a30679f561e068d92d5c7c949fcbda186ae28bb99bc7146` |

The approved authorization review recorded `85/85 PASS` and P0/P1/P2
`0/0/0`. The sequential workload was 27 committed input files and 191,738 raw
bytes, so sharding would have added coordination risk without meaningful
compute benefit. The final runner contained exactly one `Popen`, no retry,
terminate, kill, shard, or pool path, and had raw SHA-256
`e94579290a7357ccdf40e6e8c8fe925cc0db0190ab2f8df8f05f3137d576b8a4`.

The successful run produced no stdout or stderr. Its retained external record
hashes are:

| Record | SHA-256 |
| --- | --- |
| launch intent | `b156e21355f01fb953af4c68f2ea275bb8a714509b87fd552ac11dedbe719b4d` |
| execution gate | `a45a3579d20f6850cd9ed4f5ba85ba27770f4bd4e59d3fada7112c88c8807037` |
| monotone progress | `89b6aed777ae5c04962978638b2a391cef18a4f5d74551862577a96a21c54366` |
| exit record | `9fc91afad6160d8485302a2c90923e55b06e76be85e5c185457370558de9a759` |
| stdout | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| stderr | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The child exited `0` after 6.024672 seconds with
`normalization_success=true`, `manifest_exists=true`, and 181 fingerprint
records. Earlier prelaunch, no-op, and exact-decimal refusal attempts remain
preserved as negative execution evidence and were not retried in place or
deleted.

## 4. Independent artifact-only verification

The independent verifier imported the locked C1 validators, read every C2
artifact, and wrote its report outside the repository. It did not invoke the
normalizer or any downstream scientific entrypoint.

| Evidence | SHA-256 |
| --- | --- |
| verifier source | `039186270dd22225b8bbb14feb41eabc6132332e8da8003a0e786fcf5f2ff339` |
| verifier report raw bytes | `4b75575b6bf2cb42b4196c77d687c3e0338f7edd5b27121d916d2c9ce5298fe6` |
| complete C2 file-hash manifest | `9512528a8d6357534859d38f70de34567f4734993068f91a8a8eb75d49050761` |
| normalization manifest raw bytes | `d1391920c97c254fe8874175d502853354b9859322ac624a94b2f2573f371d23` |
| normalization manifest finalized self-hash | `3fcb863d8f7f19820c8ea5f5edbaf213dec587fb4497265b5ec005f525c587ad` |

The verifier returned `PASS` and established:

- exact closure of all 213 files;
- three authority-lock records and 27 authority-source records;
- 181 fingerprint records and 165 unique lineages;
- exact reconciliation of every raw hash, finalized self-hash, record hash,
  lineage map, status count, eligibility entry, and manifest reference;
- zero missing source records;
- preservation of all 62 `unreconstructable_refuse` records;
- zero forbidden outcome/result/score/stdout/stderr field findings;
- no overlap report, comparison record, target certificate, CTMC/DES output,
  scientific summary, or later governance root.

Only the case-construction and retired-normalization governance roots exist.

## 5. Corpus closure and refusal structure

### 5.1 Dimension status

| Status | Records | Interpretation |
| --- | ---: | --- |
| `derived_by_versioned_normalizer` | 80 | exact data-only projection derived under the versioned normalizer |
| `inherited_from_authority` | 16 | lineage-preserving inherited projection; not a new independent origin |
| `not_applicable_retired_stage` | 23 | dimension was not applicable at that retired stage; retain the typed status |
| `unreconstructable_refuse` | 62 | fail-closed absence of a comparison projection; never impute or discard |
| total | 181 | exact fingerprint-record closure |

The manifest marks 119 records eligible for a later input-level audit and 62
ineligible with typed refusal. Eligibility means only that the later auditor
may process the record under its dimension policy. In particular,
`not_applicable_retired_stage` is not a claim that a retired hash exists or
that a future input is independent.

### 5.2 By retired authority

| Authority | Total | Later-audit eligible | Typed refusal |
| --- | ---: | ---: | ---: |
| `G4_FREEZE` | 152 | 103 | 49 |
| `G5_EXECUTION` | 8 | 0 | 8 |
| `G6_R_REPLAY_R3` | 21 | 16 | 5 |
| total | 181 | 119 | 62 |

G5's eight refusals are retained evidence, not a reason to remove G5 from the
retired corpus or to reinterpret its evidence-closed failure status.

### 5.3 By fingerprint dimension

| Dimension | Total | Later-audit eligible | Typed refusal |
| --- | ---: | ---: | ---: |
| `case_content_sha256` | 30 | 24 | 6 |
| `state_snapshot_sha256` | 30 | 28 | 2 |
| `route_signature_sha256` | 30 | 28 | 2 |
| `parameter_tuple_sha256` | 30 | 24 | 6 |
| `random_stream_manifest_sha256` | 10 | 0 | 10 |
| `output_root_reservation_sha256` | 10 | 9 | 1 |
| `sealed_prediction_sha256` | 26 | 6 | 20 |
| `metric_schema_sha256` | 15 | 0 | 15 |
| total | 181 | 119 | 62 |

Zero eligible records in a dimension means the retired side supplies only
typed non-applicability/refusal there. It does not waive the future case's
predeclared independence, random-stream, output-containment, or metric-schema
obligations.

### 5.4 By retired subject type

| Subject type | Total | Later-audit eligible | Typed refusal |
| --- | ---: | ---: | ---: |
| `retired_case` | 66 | 46 | 20 |
| `retired_case_subunit` | 80 | 64 | 16 |
| `retired_method_observation` | 20 | 9 | 11 |
| `retired_method_companion_group` | 15 | 0 | 15 |
| total | 181 | 119 | 62 |

## 6. Theory-to-case closure

### 6.1 Ontology lock

| Object | Exact role | Forbidden conflation |
| --- | --- | --- |
| `K_local` | structural local closed-blocking-kernel candidate | not a bad stopping target without an admission audit |
| `D_local` | stopped-process bad first-hit target admitted by A2b or complete-LTS completion-nonreachability | not a plant terminal SCC |
| `D_global` | plant-level capacity-mediated operational deadlock | not every local core |
| `F` | all-jobs-complete success target | not a bad class |
| `R_livelock`, `R_terminal` | unselected residual plant terminal-SCC classes | not selected bad targets without a new estimand |
| `P_policy` | policy-induced stall class | not plant deadlock and not a plant-partition member |

`D_local` may have outgoing plant arcs generated by work outside its admitted
kernel. Its role is stopping-target semantics, not plant-terminal-SCC
semantics.

### 6.2 Evidence ladder

```text
sealed case-unit identity                              CLOSED at R7
  -> normalized retired fingerprint/lineage authority CLOSED at C2/Task 10
  -> actual input-level overlap PASS or refusal        PENDING, not authorized here
  -> Barrier-A target certificate or refusal           PENDING, not authorized here
  -> exact/DES same-target locks and observations       PENDING, not authorized here
  -> G6-B scientific verdict                           OPEN/PENDING
```

Normalization closes only the retired side of the second link. It does not
compare the 13 sealed case units against the 181 records.

### 6.3 Sealed case-unit obligation map

| Sealed case unit | Theory/control obligation | Status after normalization |
| --- | --- | --- |
| `g6b_cu_nc_local_bypass_completes_v1` | bypass counterexample against unjustified `D_local` admission | retired corpus ready; actual overlap and A2b/LTS admission pending |
| `g6b_cu_nc_unselected_livelock_v1` | `R_livelock` residual-class probe | retired corpus ready; overlap and terminal-class classification pending |
| `g6b_cu_nc_calendar_empty_terminal_v1` | `R_terminal` versus resource-deadlock boundary | retired corpus ready; overlap and target classification pending |
| `g6b_cu_nc_policy_only_stall_v1` | `P_policy` versus plant-deadlock boundary | retired corpus ready; overlap and policy/plant separation pending |
| `g6b_cu_nc_or_of_and_feasible_branch_v1` | feasible alternative blocks a false `D_local` claim | retired corpus ready; overlap and feasible-branch certificate pending |
| `g6b_cu_nc_agv_reservation_boundary_v1` | refusal or new versioned semantics at the AGV/reservation boundary | retired corpus ready; overlap then semantic refusal/versioning pending |
| `g6b_cu_nc_dglobal_only_with_dlocal_v1` | one `D_global` classification; no double counting through `D_local` | retired corpus ready; overlap and target-partition certificate pending |
| `g6b_cu_pc_dglobal_only_v1` | intended `D_global` positive-control probe | retired corpus ready; overlap and target certificate pending |
| `g6b_cu_pc_dlocal_a2b_single_kernel_v1` | intended A2b single-kernel admission probe | retired corpus ready; overlap and A2b certificate pending |
| `g6b_cu_pc_dlocal_lts_multi_kernel_v1` | intended complete-LTS multi-kernel admission probe | retired corpus ready; overlap and complete-LTS certificate pending |
| `g6b_cu_bc_crp_zero_kernel_v1` | CRP/local-bridge zero-kernel boundary | retired corpus ready; overlap and zero-kernel classification pending |
| `g6b_cu_bc_multi_capacity_residual_v1` | multi-capacity residual versus simple-cycle boundary | retired corpus ready; overlap and residual-capacity certificate pending |
| `g6b_cu_pc_medium_independent_island_v1` | medium-island probe | retired corpus ready; actual independence and target gates pending |

For every row, exact and DES remain companion methods sharing one
`case_unit_id`, selected labels, a versioned stopping target, and a future
`absorption_domain_hash`. They are not independent cases. No result is inferred
from the case name or intended control role.

## 7. Preserved negative and boundary evidence

This publication does not alter the following evidence:

- G5 remains evidence-closed failure evidence: locked scorer `4/3/2`,
  transparent audit `6/1/2`, and both certificate-minimality failures;
- G6-R R1 and R2 remain failures, while R3 remains historical mechanism
  regression only, not held-out confirmation;
- all 62 normalization refusals remain committed and manifest-addressed;
- earlier Task 9 prelaunch, no-op, and exact-decimal refusal records remain
  external negative execution evidence;
- C3/R7 construction remains `CASE_UNIT_SEALED_NO_EXECUTION`, with 13 case
  units, 26 method observations, and 13 companion groups but no outputs.

No favorable subset was selected and no failure was renamed as a PASS.

## 8. Three bounded R10 publication lanes

The plan-required post-run review was executed once as three non-overlapping,
read-only lanes over the pre-publication documentation candidate and the exact
artifact-verifier report. The reviewed raw document hashes were:

- this review candidate:
  `8520204871a526dbc96aa2488763e403569629bfc762f2b448e044a8c12b92f2`;
- `PROJECT_HANDOFF.md` candidate:
  `78c091ea893dab361a721063d79696f9d1a1ab488fc2a8f22599ebf500dfc2f8`;
- `docs/ROADMAP.md` candidate:
  `17a535a817b06b546e88855607eeeb63a5c41c5a3f6dd812ac1bebde00957528`;
- artifact-verifier report:
  `4b75575b6bf2cb42b4196c77d687c3e0338f7edd5b27121d916d2c9ce5298fe6`.

| Lane | Bounded question | Verdict | P0/P1/P2 |
| --- | --- | --- | --- |
| ontology/estimand | Are `D_local`, `D_global`, `F`, residual classes, policy stall, case obligations, and exact/DES companion semantics kept distinct, with normalization never called overlap? | PASS | `0/0/0` |
| selector/leakage/nonreuse | Are outcome-bearing fields absent, hashes kept below semantic independence, refusals retained, and G5/R1/R2/R3 boundaries preserved? | PASS | `0/0/0` |
| artifact/hash/lineage | Do C1/C2 identities, 213/3/27/181/165 closure, 119/62 eligibility, manifest/report hashes, and three-document C3 scope reconcile? | PASS | `0/0/0` |

The publication successor adds only this review-result record to the reviewed
candidate; it does not change any scientific claim, count, hash subject,
artifact, source, test, or boundary. No additional generic code-review cycle
was performed.

## 9. Verification and publication verdict

C1 verification passed:

- repaired decimal boundary: `14 passed in 15.11s`;
- all nine real G4 projections: `1 passed in 0.34s`;
- complete normalizer/schema suite: `730 passed in 45.07s`;
- Ruff check, Ruff format check, strict mypy, static capability guard, and
  `git diff --check`.

C2 artifact verification passed the exact closure and hash checks in Section
4. C1..C2 contains only the 213 normalization-root paths. C2..C3 is restricted
to this review, `PROJECT_HANDOFF.md`, and `docs/ROADMAP.md`.

Publication verdict:

```text
RETIRED_AUTHORITY_NORMALIZATION_COMPLETE
G6-B OPEN-PENDING
ACTUAL_OVERLAP NOT RUN
BARRIER A NOT AUTHORIZED / NOT RUN
BARRIER B NOT AUTHORIZED / NOT RUN
G6-C/D/E NOT STARTED / NOT PASSED
PAPER GATE CLOSED
```

The next scientifically meaningful tranche is a separately bounded,
input-level actual-overlap audit that compares the 13 sealed case inputs with
the normalized retired corpus under the eight dimension policies and preserves
all typed refusals. This review does not authorize or execute that tranche.
