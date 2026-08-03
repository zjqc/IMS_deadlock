# G6-B Case Construction Task-R2/R3 Source Review

Date: 2026-08-04

Status: `SOURCE_REVIEW_ONLY / PASS`

This record reviews the exact pre-C2 Task-R2/R3 source candidate for the
discovery-only G6-B case-construction tranche. It is not construction
authorization, artifact evidence, retired-authority normalization,
target-certification authority, quantitative-execution authority, scientific
evidence, or a G6-B verdict.

## Locked authority and approved inputs

- Authority worktree:
  `D:\worktree\IMS_deadlock-g6b-case-construction-v2`.
- Branch: `codex/g6b-case-construction-v2` with no upstream.
- Pre-C2 context HEAD:
  `0393b31f9fe56e595bedfb796fe70c097e7cd6c5`.
- Pre-C2 context tree:
  `9ff85e1344120444408ed6810d349531e7560de5`.
- Runtime:
  `D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe`,
  Python 3.13.9.
- Approved materialization-contract corrigendum SHA-256:
  `ff469d9c5105835fde5feb170e501bdde14506df50632990f7c2cddc251da36c`.
- Approved v2 implementation-plan SHA-256:
  `81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7`.
- Independent plan-review SHA-256:
  `da6da7c2e513e11761e439f8b43ef6260556c912d3e730f94f15eae088d90ea0`.
- Frozen row-family matrix SHA-256:
  `487d81aa79a7bca681db81f19a4d6bd315668c43b1c4538c47f01f099d8e205f`.
- Construction-schema v3 SHA-256:
  `4d8d55ce85cb8c8b2260c718ab3d5e0325e80312712dbd07f628f47f46e329cc`.
- Case-recipe registry SHA-256:
  `e94246b42ec762221dfc1dec066498c4b279a0b9c4266380243b40dd75cc1b72`.

The approved plan, plan review, corrigendum, and frozen matrix were rehashed
from the authority worktree and matched the identities above. The recipe
registry identity is the validated semantic catalog identity; no unsupported
historical field-count or old-to-new drift claim is made here.

## Exact reviewed eight-path source subject

The following raw SHA-256 map is the complete source subject bound by this
record. This record itself is intentionally excluded so it can be committed
with these bytes without a self-reference cycle.

| Path | Raw SHA-256 |
| --- | --- |
| `cases/discovery/g6b/row_families/structural_discovery_v1/case_construction_schema.json` | `4d8d55ce85cb8c8b2260c718ab3d5e0325e80312712dbd07f628f47f46e329cc` |
| `cases/discovery/g6b/row_families/structural_discovery_v1/row_family_protocol.json` | `fa72c8a91a7ad1bdb1141e632377a3ed11831fb542f02083bcf195eb8a570e2c` |
| `src/ims_deadlock/g6b_case_materializer.py` | `e2ab27c23bbb795145962a1131697dc060c8a9c2a0c8227f3cd5b420cc811e93` |
| `src/ims_deadlock/g6b_row_family_protocol.py` | `c4be46df1f097c8f94eb60f26436b065660f140e7cf3b07b6501cba3ee9981fb` |
| `src/ims_deadlock/g6b_schema_contracts.py` | `3326169c15199e94edc8b018112da395aeb2c09c1bcd5902b48f093d6d578954` |
| `tests/test_g6b_case_materializer.py` | `a77e09acf85f80baad21fbbde5f56ea2ab3c0c0fbd542309493a340fa7818255` |
| `tests/test_g6b_row_family_protocol.py` | `76cbca61bff21cb112d6f8c341b1c1c1f837fde5e49085249fb800b42a1d0df0` |
| `tests/test_g6b_schema_contracts.py` | `2550ee05e43cb381527819847c4d628e65a602d5125eff5cf0b1f7a50e57b27c` |

Immediately before final review, Git reported exactly these eight staged paths,
zero unstaged paths, and zero ordinary untracked paths. The shared
`identity_schema.json` and `retired_authority_fingerprint_schema.json` remained
byte-identical to `HEAD`.

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
  finalized self-hash, strict UTC, source HEAD/tree/nine-path hashes, frozen
  document/matrix/schema/recipe hashes, and fail-closed identity drift;
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

No governance instance root, case-unit root, target-certification root,
quantitative root, science root, artifact root, or Task-R2 review file existed
while this eight-path subject was reviewed.

## Test and static evidence

The final formal source gate ran single-process because its exhaustive
mutation/oracle tests are internally sequential and the formal subject must not
change under a parallel scheduler. Remote capacity was independently adequate;
short independent static checks were run concurrently.

Formal command:

```bat
set PYTHONPATH=src
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_g6b_case_materializer.py tests\test_g6b_schema_contracts.py tests\test_g6b_row_family_protocol.py tests\test_g6b_protocol.py
```

Final result: `1971 passed, 2 skipped in 3466.44s (0:57:46)`, exit code `0`.
The retained log is
`D:\codex_deps\IMS_deadlock-g6b-v2-xdist-20260802\r4_source_gate_run7_auth_load_closure_20260804\pytest.log`,
raw SHA-256
`7fb8fffe894c292a4883e7593e24f2378ea5c0030c54eb0fd69deb94be7be260`.

Fresh checks on the same eight bytes:

- Ruff check with `--no-cache`: `All checks passed!`;
- Ruff format check with `--no-cache`: `7 files already formatted`;
- mypy with `--no-incremental`: `Success: no issues found in 7 source files`;
- `git diff --check`: PASS;
- `git diff --cached --check`: PASS.

## Preserved negative and repair evidence

The final PASS does not erase intermediate failures:

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
- final code review then found that canonical sorted authorization bytes could
  not round-trip through the loader. The new regression test first failed with
  `ValueError: authorization_field_set`; after exact-key validation plus
  normalization into `AUTHORIZATION_FIELDS`, the new and existing round-trip
  tests passed (`2 passed`), the authorization-focused selection passed
  (`36 passed`), and final run 7 passed as recorded above.

No failed, partial, or review-negative evidence was deleted or reclassified as
success.

## Sequential independent reviews

- Final specification-compliance review: `PASS`, with
  P0/P1/P2=`0/0/0`. The reviewer independently re-locked the eight paths and
  approved documents, generated the in-memory candidate, and confirmed
  `13/26/13`, `390/4/394`, 393 transient paths, 13 recipes, deterministic seed
  identities, no blocked-token path, and no R5/R6 root creation.
- Final code-quality review, started only after specification PASS:
  `APPROVE`, with P0/P1/P2=`0/0/0`. It covered exact-key loader ordering,
  Windows create-new/no-replace behavior, process and ledger locking,
  append-only/torn-fragment recovery, hash subjects, deep immutability,
  exception paths, types, and mutation tests. Its high-risk targeted selection
  passed `11` tests, and its fresh Ruff, format, mypy, and diff checks passed.

Any post-review source, test, schema, or review-byte change invalidates this
record and requires a new applicable test gate and both reviews.

## Claim and next-gate boundary

This source review proves only that the exact eight-path in-memory construction
implementation is ready to be committed with this review as C2. It does not
create or authorize a construction bundle. R5 must begin from a clean C2 and a
separately validated authorization v2. R6 artifact verification, R7 three-way
review, retired-authority normalization, target certification, quantitative
execution, and all scientific claims remain closed.
