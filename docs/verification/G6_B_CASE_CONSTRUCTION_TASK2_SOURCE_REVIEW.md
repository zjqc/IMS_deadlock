# G6-B Case Construction Task-R2/R3 Repair-C2 Source Review

Date: 2026-08-04

Status: `REPAIR_C2_SOURCE_REVIEW_ONLY / PASS`

This record reviews the exact repair-C2 source candidate for the discovery-only
G6-B case-construction tranche after a post-seal test-fixture repair. It is not
construction authorization, artifact evidence, target-certification authority,
quantitative execution authority, scientific evidence, or a G6-B verdict.

## Locked authority and approved inputs

- Worktree: `D:\worktree\IMS_deadlock-g6b-case-construction-v2-r6-testfix`.
- Branch: `codex/g6b-case-construction-v2-r6-testfix` with no upstream.
- Repair base HEAD: `b33bda7ee037be9f29ddc838024a7fe0b8e04d8c`.
- Repair base tree: `a18605756931bd99f1ebeb10d332148c02a4fff0`.
- Runtime: `D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe`.
- Approved materialization-contract corrigendum SHA-256:
  `ff469d9c5105835fde5feb170e501bdde14506df50632990f7c2cddc251da36c`.
- Approved v2 plan SHA-256:
  `81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7`.
- Independent plan review SHA-256:
  `da6da7c2e513e11761e439f8b43ef6260556c912d3e730f94f15eae088d90ea0`.
- Frozen row-family matrix SHA-256:
  `487d81aa79a7bca681db81f19a4d6bd315668c43b1c4538c47f01f099d8e205f`.
- Construction-schema v3 semantic identity SHA-256:
  `4d8d55ce85cb8c8b2260c718ab3d5e0325e80312712dbd07f628f47f46e329cc`.
- Case-recipe registry SHA-256:
  `e94246b42ec762221dfc1dec066498c4b279a0b9c4266380243b40dd75cc1b72`.

The candidate changes only two test-fixture calls from `mkdir()` to
`mkdir(exist_ok=True)` in one test. Production, schema, recipe, matrix,
materializer, authorization, inventory, and scientific semantics are unchanged.

## Exact reviewed nine-key source subject

The authorization source map remains the exact nine-key subject required by
`AUTHORIZED_SOURCE_FILE_PATHS`. This document is the ninth key; its raw hash is
bound externally after these bytes stabilize, avoiding a self-reference cycle.
The eight non-self peer hashes are:

| Path | Raw SHA-256 |
| --- | --- |
| `cases/discovery/g6b/row_families/structural_discovery_v1/case_construction_schema.json` | `9c96dc2dea1a407167b618c4a6be4a511d4bbb94a877df0ac196627e9a8609d6` |
| `cases/discovery/g6b/row_families/structural_discovery_v1/row_family_protocol.json` | `ecd9e91d3f3b2a041367e73e14abb9db63e6579517cd40d21d8100347671f1cf` |
| `src/ims_deadlock/g6b_case_materializer.py` | `e2ab27c23bbb795145962a1131697dc060c8a9c2a0c8227f3cd5b420cc811e93` |
| `src/ims_deadlock/g6b_row_family_protocol.py` | `8c05c019e9b70d819adbe388c2c6d30d90129f7da71ce1042f161ed226db4fef` |
| `src/ims_deadlock/g6b_schema_contracts.py` | `cf84fff421eae6d31eed5ac578748eb00de4d3bda9095456f979146b523e9a27` |
| `tests/test_g6b_case_materializer.py` | `a77e09acf85f80baad21fbbde5f56ea2ab3c0c0fbd542309493a340fa7818255` |
| `tests/test_g6b_row_family_protocol.py` | `91ddbec0e6055d857cdc41d1f856cdd224aff128c0ea44c974f32cdb510c2879` |
| `tests/test_g6b_schema_contracts.py` | `22f3bc365d141eee3b4d4fa5b210568f0e9d10b65eb501b6a2d51844448c8522` |

The companion test outside the nine-key authorization map is:

| Path | Raw SHA-256 |
| --- | --- |
| `tests/test_g6b_protocol.py` | `9f385fa3373d2e6464c95663a56696b80dcce708e7495e41277f93b3bd813a6d` |

Before finalizing this document Git reported exactly one modified path,
`tests/test_g6b_row_family_protocol.py`. After finalization the intended C2 diff
is exactly that test and this review document. No production, schema, recipe,
matrix, governance-instance, case-unit, target-certification, quantitative, or
scientific-output path is present.

## Repair and preserved negative evidence

The old sealed subject is preserved at
`D:\worktree\IMS_deadlock-g6b-case-construction-v2-r6-repair`. Its formal
focused gate completed all 1,977 outcomes but failed only because the fixture
copied an already sealed bundle and then unconditionally recreated `case_units`.
The retained incident raw SHA-256 is `da37b05654202157e938b4e623c607cabf80bbf46d9c59994409b50d5e727eb8`; the
retained pytest result was `1 failed, 1974 passed, 2 skipped in 3318.50s`.

That negative evidence is not erased or relabeled. It triggered a new clean C2,
new review, new authorization, and new materialization as required by the
approved fail-closed contract. The fix changes no production behavior and
performs no scientific computation.

## Contract and inventory boundary

The unchanged source contract still closes exactly 13 case units, 26 method
observations, 13 exact/DES companion groups, seven mandatory controls, 390 case
files, four governance files, 394 final files, and 393 deterministic transient
paths. It retains canonical duplicate-member rejection, source HEAD/tree/hash
binding, create-new/manifest-last/append-only semantics, retained partials,
single recovery, terminal no-retry, zero random draws, and the prohibitions on
retired outcomes, state enumeration, CTMC, DES, scoring, and status upgrades.

## Test and static evidence

Formal command (the two added options control terminal rendering only):

```bat
set PYTHONPATH=src
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q --color=no -o console_output_style=progress tests\test_g6b_case_materializer.py tests\test_g6b_schema_contracts.py tests\test_g6b_row_family_protocol.py tests\test_g6b_protocol.py
```

- Formal result: `1975 passed, 2 skipped in 3393.79s (0:56:33)`, exit `0`.
- Collected/outcome count: `1977`.
- Wall time captured by wrapper: `3394.831162` s.
- Pytest log SHA-256: `6ea9d062658fb4a7517f7f81f000ccaa84b255e3e4d4c145bf417b614c9ac23d`.
- Progress JSONL SHA-256: `c5e44db0cc0a92305069d5999617e620543452aac5a0db27cc078994a4c5bb1e`.
- Formal start-record SHA-256: `f5ff4e1b5ddd64a554d34ed82852d8fa26696b07704ca98a72924edf2cc76e0b`.
- Formal summary raw SHA-256: `acf57ddc114cbbc2c99cb3ea4d2b5047afb7f61fc6df62b1666f1ec36a0627e0`.

Targeted repair and static evidence:

- `git_diff_check`: exit `0`, 0.120518 s, log SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- `mypy`: exit `0`, 9.515293 s, log SHA-256 `8e63ae22e8213e327a5e9cbd584067681681bd8ef7f25c869877887ccdcfc4ff`.
- `ruff_check`: exit `0`, 0.904681 s, log SHA-256 `82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18`.
- `ruff_format`: exit `0`, 0.900670 s, log SHA-256 `fd2299c9f1c6dc869070883e281051bfe93aacf66c1a3b0069f45b4aa410ca50`.
- `targeted_pytest`: exit `0`, 1.488938 s, log SHA-256 `201f5a20b2fed2d18981a2cf094a90cbd230f4e0c22d666d1e0e2af3e8aef27a`.
- Targeted summary raw SHA-256: `fcf5796114b4d50e05d5e34c752adefbf1d375f2b465dfb5b51cbfadc8d9674e`.

Both gates used the repair worktree source through explicit `PYTHONPATH`,
disabled pytest cache and Python bytecode, preserved the exact one-test diff,
and left no repository cache artifacts. The formal run remained single-process
because its exhaustive mutation/oracle checks are internally sequential.

## Independent final-review boundary

These stable bytes must receive sequential specification-compliance review and
then separate code-quality review before C2 commit. The external review records
must bind this document raw hash, the test hash, formal summary hash, exact
two-path diff, branch/base identity, and P0/P1/P2 counts. Any edit after review
invalidates the affected review and requires repetition.

## Claim and next-gate boundary

This source review proves only that the exact repair-C2 test contract candidate
is ready for independent review and, if approved, an atomic C2 commit containing
exactly the repaired test and this document. It does not authorize construction.

R5 must start from clean repair C2 with a new authorization. The previous
authorization and 394-file subject do not carry over. Retired-authority
normalization, target certification, quantitative execution, CTMC, DES, and all
scientific claims remain closed. G6-B remains `OPEN/PENDING`.
