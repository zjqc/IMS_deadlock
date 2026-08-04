# G6-B Case Construction Task-R2/R3 Replacement-C2 Source Review

Date: 2026-08-04

Status: `REPLACEMENT_C2_SOURCE_REVIEW_ONLY / PASS`

This record reviews the exact replacement-C2 Task-R2/R3 source candidate for
the discovery-only G6-B case-construction tranche after the approved post-seal
test-contract repair. It is not construction authorization, artifact evidence,
retired-authority normalization, target-certification authority, quantitative
execution authority, scientific evidence, or a G6-B verdict.

## Locked authority and approved inputs

- Authority worktree:
  `D:\worktree\IMS_deadlock-g6b-case-construction-v2-r6-repair`.
- Branch: `codex/g6b-case-construction-v2-r6-repair` with no upstream.
- Pre-replacement-C2 base HEAD:
  `9cd5b5da0af1684a377ba02a35167164d83ab01c`.
- Pre-replacement-C2 base tree:
  `42c280f20f6707e53d49fd9f5e1800771afaac13`.
- Runtime:
  `D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe`,
  Python 3.13.9.
- Approved materialization-contract corrigendum SHA-256:
  `ff469d9c5105835fde5feb170e501bdde14506df50632990f7c2cddc251da36c`.
- Approved v2 implementation-plan SHA-256:
  `81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7`.
- Independent plan-review SHA-256:
  `da6da7c2e513e11761e439f8b43ef6260556c912d3e730f94f15eae088d90ea0`.
- Approved post-seal test-contract repair plan SHA-256:
  `e749442d3f07c36ced57c21e8a7b3f7650e3197ba9c07d837b54076cf08bef8d`.
- Independent repair-plan review SHA-256:
  `11be5b70b80f0994e3bfce46d87503b7f73ac04adbb56db67e77859bac2bac97`.
- Frozen row-family matrix SHA-256:
  `487d81aa79a7bca681db81f19a4d6bd315668c43b1c4538c47f01f099d8e205f`.
- Construction-schema v3 semantic identity SHA-256:
  `4d8d55ce85cb8c8b2260c718ab3d5e0325e80312712dbd07f628f47f46e329cc`.
- Case-recipe registry SHA-256:
  `e94246b42ec762221dfc1dec066498c4b279a0b9c4266380243b40dd75cc1b72`.

The approved v2 plan, v2 plan review, corrigendum, repair plan, repair-plan
review, and frozen matrix were rehashed from their locked locations and
matched the identities above. The schema semantic identity, recipe registry,
frozen matrix, approved v2 plan, v2 plan review, and corrigendum identities are
unchanged from the original C2 review. The recipe registry identity is the
validated semantic catalog identity; no unsupported historical field-count or
old-to-new drift claim is made here.

The construction-schema semantic identity above is not the raw file hash used
in the authorization `source_file_hashes` map. The raw SHA-256 of
`case_construction_schema.json` in the reviewed replacement-C2 tree is
`9c96dc2dea1a407167b618c4a6be4a511d4bbb94a877df0ac196627e9a8609d6`.
These two identities bind different subjects and are not interchangeable.

## Exact reviewed nine-key source subject

The authorization `source_file_hashes` subject remains the exact nine keys
required by `AUTHORIZED_SOURCE_FILE_PATHS`. This document is the ninth key, but
its final raw hash cannot be embedded in its own bytes without a self-reference
cycle. The table below therefore lists the eight non-self peer raw hashes. The
final raw hash of this review document is computed only after these bytes are
stable and is bound externally by the new `c2_source_lock.json` and the
replacement C2 tree.

| Path | Raw SHA-256 |
| --- | --- |
| `cases/discovery/g6b/row_families/structural_discovery_v1/case_construction_schema.json` | `9c96dc2dea1a407167b618c4a6be4a511d4bbb94a877df0ac196627e9a8609d6` |
| `cases/discovery/g6b/row_families/structural_discovery_v1/row_family_protocol.json` | `ecd9e91d3f3b2a041367e73e14abb9db63e6579517cd40d21d8100347671f1cf` |
| `src/ims_deadlock/g6b_case_materializer.py` | `e2ab27c23bbb795145962a1131697dc060c8a9c2a0c8227f3cd5b420cc811e93` |
| `src/ims_deadlock/g6b_row_family_protocol.py` | `8c05c019e9b70d819adbe388c2c6d30d90129f7da71ce1042f161ed226db4fef` |
| `src/ims_deadlock/g6b_schema_contracts.py` | `cf84fff421eae6d31eed5ac578748eb00de4d3bda9095456f979146b523e9a27` |
| `tests/test_g6b_case_materializer.py` | `a77e09acf85f80baad21fbbde5f56ea2ab3c0c0fbd542309493a340fa7818255` |
| `tests/test_g6b_row_family_protocol.py` | `e4c17acf6d61fa2ef7dfddae02450268d6f61a69221dc8bcc6937478230fd8f5` |
| `tests/test_g6b_schema_contracts.py` | `22f3bc365d141eee3b4d4fa5b210568f0e9d10b65eb501b6a2d51844448c8522` |

Separate companion test hash, outside `source_file_hashes`:

| Path | Raw SHA-256 |
| --- | --- |
| `tests/test_g6b_protocol.py` | `9f385fa3373d2e6464c95663a56696b80dcce708e7495e41277f93b3bd813a6d` |

`tests/test_g6b_protocol.py` is part of the approved replacement-C2 tracked
test diff, but it is not a tenth authorization source key. It is bound by the
replacement C2 tree identity and by the exact C2..C3 and C3..C4 diff closures,
not by being represented in the authorization source map.

Before this review artifact was edited for replacement C2, Git reported only
these dirty paths:

- `tests/test_g6b_row_family_protocol.py`;
- `tests/test_g6b_protocol.py`.

After this review artifact edit, the intended replacement-C2 tracked diff is
exactly:

- `tests/test_g6b_row_family_protocol.py`;
- `tests/test_g6b_protocol.py`;
- `docs/verification/G6_B_CASE_CONSTRUCTION_TASK2_SOURCE_REVIEW.md`.

Production files, schema files, recipe registry, frozen matrix, and approved
identity artifacts have no replacement-C2 diff. No governance instance root,
case-unit root, target-certification root, quantitative root, science root, or
artifact root exists in the replacement-C2 source review subject.

## Closed contract and inventory

The reviewed implementation closes the following source-level subject without
materializing it:

- exactly 13 case units, 26 method observations, and 13 exact/DES companion
  groups;
- exactly 30 files per case, hence 390 case files, four governance files, and
  394 final files;
- exactly 393 deterministic transient paths, because the append-only ledger is
  the sole non-atomic-rename exception;
- exactly seven mandatory controls;
- authorization-v2 exact fields, canonical duplicate-member rejection,
  finalized self-hash, strict UTC, source HEAD/tree/nine-key hashes, frozen
  document/matrix/schema/recipe identities, and fail-closed identity drift;
- deterministic recipe, projection, fingerprint, seed-root, and commitment
  relations without random draws, clock input, filesystem discovery, outcome
  reads, state enumeration, CTMC, DES, scoring, or scientific status changes;
- create-new, manifest-last, append-only ledger, deterministic temp-name,
  retained-partial, single-recovery, and terminal-no-retry semantics.

The selected-target semantic payload remains the six-field recipe/catalog
subject. Its materialized declaration is the seven-field file envelope formed
by adding the role-specific `schema_version`. This preserves the reviewed
recipe registry identity while satisfying the file-role schema. The immutable
construction log is bound by its finalized `log_sha256`; downstream lineage
references that self-hash rather than a circular hash of final log bytes.

## Test and static evidence

The decisive formal source gate ran single-process because its exhaustive
mutation/oracle tests are internally sequential and the formal subject must not
change under a parallel scheduler. Remote capacity was independently adequate;
short independent static checks were run concurrently as independent read-only
processes.

Formal command:

```bat
set PYTHONPATH=src
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_g6b_case_materializer.py tests\test_g6b_schema_contracts.py tests\test_g6b_row_family_protocol.py tests\test_g6b_protocol.py
```

Decisive formal run 2 result:
`1975 passed, 2 skipped in 3419.06s (0:56:59)`, exit code `0`.
Retained evidence hashes:

- `pytest.log`: `1ce318b5ee510bab5d70bfda427c9354ade56f15aa0781fb2f94b0a1d8c35160`;
- `run.cmd`: `79531fd52e2688ea411e8b14a0f2191c1907ab9617e9fed0fee21fc7fd6339d8`;
- `exit_code.txt`: `13bf7b3039c63bf5a50491fa3cfd8eb4e699d1ba1436315aef9cbe5711530354`;
- `sha256_manifest.txt`: `b9532c34afce29a1c139a020baf054744b70322e9c3b27ab8d0301dbb5b48e5e`.

Fresh static run 3 on the same replacement-C2 bytes:

- Ruff check: PASS, manifest SHA-256
  `64699ce84ac0e44cab96e4d1043efec3f1027c539734882b10408dcf738c2cdd`;
- Ruff format check: 49 files already formatted, manifest SHA-256
  `946829952bd19f767e24f991fff881fd468b7dc8f90c6945543ccfcf25031b32`;
- mypy: 9 files passed, manifest SHA-256
  `faf944bbe9cb5f8f22f1e3a18985e7f7137e36d54056992106de19d6c9d3bfd0`;
- `git diff --check`: exit code `0`;
- `git diff --cached --check`: exit code `0`;
- combined diff-check manifest SHA-256
  `c62366c59b2be85527df27b75b607414d0a81169ecdaea47bcf834bae405b05a`.

## Preserved negative and repair evidence

The replacement-C2 PASS does not erase intermediate failures or convert repair
tests into scientific evidence.

The sealed old subject at
`D:\worktree\IMS_deadlock-g6b-case-construction-v2` remains frozen. Its old R6
focused gate failed with `214 failed, 1757 passed, 2 skipped`, exit code `1`.
The failure evidence manifest SHA-256 is
`d3a117eb2412ab6692cc6c9759f66226823b1491d43e15b32f0f0e0b1550259a`.
That failure is retained as historical negative test-contract evidence only.

Original C2 source-review failure and repair history:

- run 2: `1 failed, 1949 passed, 2 skipped in 3242.85s`; the sole live
  diff-scope failure was repaired;
- run 3: `1951 passed, 2 skipped in 3452.73s` before contract review;
- contract review found selected-target envelope, output-reservation ref,
  authorization-field, log-hash, fingerprint-relation, and UTC-validation
  defects; mutation coverage then exposed exact-key drift acceptance;
- run 4 intentionally exposed stale canonical candidate bytes after those
  repairs: `213 failed, 1753 passed, 2 skipped in 688.73s`;
- two-file run 5: `642 passed in 336.43s` after restoring the semantic/file
  envelope boundary and exact-nine scope;
- run 6: `1970 passed, 2 skipped in 3383.58s`;
- final old code review then found that canonical sorted authorization bytes
  could not round-trip through the loader. The new regression test first failed
  with `ValueError: authorization_field_set`; after exact-key validation plus
  normalization into `AUTHORIZATION_FIELDS`, the new and existing round-trip
  tests passed (`2 passed`), the authorization-focused selection passed
  (`36 passed`), and final old run 7 passed with
  `1971 passed, 2 skipped in 3466.44s`.

These original C2 source-review records remain historical negative and repair
evidence. They are not covered over or reclassified by the replacement-C2 PASS.

Repair RED/GREEN and postformal evidence:

- Task 3 RED: `3 failed in 0.89s`, pytest log SHA-256
  `2d3562cf821bcc9f1a4ad7e6ae2e39a29ce51220e5c4ee31c370190feccf0b33`,
  manifest SHA-256
  `b18111da862a397556f0c4810ceee35f51b99ee1c7220bb4900bff7b4a9e1994`;
- Task 4 row-family GREEN: `17 passed in 4.75s`, pytest log SHA-256
  `3063e1d15b897ed0d9c74afc7f2d571f1e71fe7b671097167ce7f7d542ba227a`;
- Task 5 protocol GREEN: `6 passed in 0.66s`, pytest log SHA-256
  `dc04634fe8a308f73e9aa5d87931b264acaec94fd296d2eed6faf86da29081ba`;
- Task 6 exact-scope GREEN: `11 passed in 0.70s`, pytest log SHA-256
  `33bac6a6d3d8d17cfae95f983d81f6eecff25d8a6ea41810498d051df10839fd`;
- formal run 1: `2 failed, 1973 passed, 2 skipped in 3403.78s`, pytest log
  SHA-256
  `922e0af717e117fff2d1d648147c98ff48cc16284cb350d8476d9be35dcfae33`,
  manifest SHA-256
  `d3e607f9a9d9d779b47d0c219bbbdb1cf09286dd949cbecbcf5d3e75240c54cb`;
- formal run 1 runner supplemental evidence was retained separately and did
  not change the failure classification;
- postformal RED: `2 failed in 0.48s`, pytest log SHA-256
  `24dbd819a0c71634184e00278135e9336974cda715a08b30cb5fb71fe6aade9f`;
- postformal GREEN: `13 passed in 0.69s`, pytest log SHA-256
  `8a5857916f4ba6286a4b5da15281cc61888e37f0c3cd91b68bf3268c1d7a0f2f`.

The formal run 1 root cause was stale negative samples in the repaired test
contract only. It did not identify a production scientific-behavior defect.
No failed, partial, repair-negative, or review-negative evidence was deleted or
reclassified as success. The repair RED/GREEN runs validate the replacement
test contract; they are not construction authorization, artifact evidence,
quantitative evidence, scientific evidence, or a G6-B verdict.

## Review boundary before replacement C2

Task 3 through Task 6 repair reviews completed before this final review
artifact update, including the postformal spec re-review PASS with P0/P1/P2
`0/0/0` and the separate quality re-review APPROVE with P0/P1/P2 `0/0/0`.

This final document's stable bytes must still receive a sequential
replacement-C2 specification-compliance review and then a separate code-quality
review before commit. Any edit after either final Task 7 review invalidates the
affected review and requires the applicable gate and both final reviews to be
repeated.

## Claim and next-gate boundary

This source review proves only that the exact replacement-C2 source and test
contract candidate is ready for final Task 7 review and, if approved, atomic
replacement-C2 commit with exactly the two repaired test files plus this review
artifact. It does not create or authorize a construction bundle. R5 must begin
from a clean replacement C2 and a separately validated authorization v2. R6
artifact verification, R7 three-way review, retired-authority normalization,
target certification, quantitative execution, and all scientific claims remain
closed.

G6-B remains `OPEN/PENDING`.
