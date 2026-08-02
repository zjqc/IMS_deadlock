# G6-B Case-Target Schema v2 Review

Date: 2026-08-01

This record is the verification surface for the schema-only G6-B case-target
governance tranche. It is not a case-construction authorization, normalization
authorization, target-certification authorization, quantitative-execution
authorization, or scientific result.

## Locked schema boundary

- Approved design:
  `docs/superpowers/specs/2026-08-01-g6b-case-target-certification-design.md`.
- Approved design SHA-256:
  `b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6`.
- The top-level G6-B bundle remains exact-five.
- The nested row-family bundle is exact-twelve schema-only governance.
- `case_construction_authorized=false`.
- `retired_authority_fingerprint_normalization_authorized=false`.
- `target_certification_preflight_authorized=false`.
- `quantitative_execution_authorized=false`.
- `scientific_execution_authorized=false`.
- `adversarial_review_status=PENDING`.
- Current bundle state remains `ROW_FAMILY_BUNDLE_IMPLEMENTED`.

Task-5 schema-code subject commit:
`9ef6fcec9e410b2ab7afc4144df8b948a238d95f` on branch
`codex/g6b-case-target-certification-final-review`. The authority worktree was
`D:\worktree\IMS_deadlock-g6b-spec-final-review`; the project runtime was
`D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe` with
`PYTHONPATH` locked to the authority worktree `src`, bytecode disabled, and the
pytest cache provider disabled.

## Task-5 candidate evidence

The following evidence was collected on the exact file content immediately
before the subject commit; the post-commit worktree was then re-locked clean,
pushed, and `HEAD...upstream` was `0/0`.

| Check | Result |
| --- | --- |
| Four-file G6-B suite | `1478 passed, 2 skipped in 2672.43s (0:44:32)` |
| Schema-contract suite | `160 passed in 0.36s` |
| Section 17.3 manifest/collection audit | `1 passed, 1108 deselected` |
| Ruff touched Python | passed, with the frozen `FLY002` baseline in `tests/test_g6b_protocol.py` excluded explicitly |
| Ruff format touched Python | passed |
| mypy touched source/tests | `Success: no issues found in 3 source files` |
| `git diff --check` | passed |

The two skips are pre-existing controlled skips. They are not xfails and are
not reported as runtime-capability evidence.

Three Task-5 implementation reviews found no P0/P1 blocker in their scoped
preflight/capability, retired-authority, and same-target/quantitative-schema
passes. These are preliminary implementation-review facts, not substitutes for
the three independent Section 18 reviews recorded below for the exact review
subject.

## Task-6 pre-commit candidate evidence

| Check | Result |
| --- | --- |
| Capability-module/later-root absence and current-doc assertions | `2 passed, 192 deselected` |
| Diff-scope policy plus live tracked/untracked/ignored-forbidden audit | `10 passed, 1109 deselected` |
| Full top-level G6-B protocol file | `194 passed in 29.29s` |
| Ruff touched tests | passed; frozen `FLY002` baseline excluded explicitly |
| Ruff format touched tests | passed |
| strict mypy touched tests and owning sources | `Success: no issues found in 4 source files` |
| Markdown trailing whitespace/fence checks | passed |
| `git diff --check` | passed |

The live diff-scope test is anchored to Task-5 subject
`9ef6fcec9e410b2ab7afc4144df8b948a238d95f`. It includes tracked changes,
ordinary untracked files, and ignored untracked files under forbidden roots;
tracked renames are expanded into delete/add paths with `--no-renames`.

Task-6 preliminary reviews produced two code-scope P1 findings and one history
clarity P2 finding. The P1 findings were closed by scanning all four changed
documents for forbidden claims and by admitting ignored forbidden-root files
to the scope decision while directly proving whole `evidence/g6b` and
`artifacts/g6b` roots absent. The P2 was closed by marking the 2026-07-30/31
ROADMAP instructions explicitly historical. The scientific-boundary review
approved the corrected documents with zero findings. These are Task-6
pre-commit reviews, not the three final Section 18 reviews.

## Capability and artifact absence

The following later instance roots must remain absent in this tranche:

- `cases/discovery/g6b/row_families/structural_discovery_v1/governance`;
- `cases/discovery/g6b/row_families/structural_discovery_v1/case_units`;
- `evidence/g6b/target_certification`;
- `artifacts/g6b/quantitative`.

The following future capability modules must remain absent:

- `src/ims_deadlock/g6b_retired_normalizer.py`;
- `src/ims_deadlock/g6b_target_preflight.py`;
- `src/ims_deadlock/g6b_target_artifacts.py`;
- `src/ims_deadlock/g6b_quantitative_runner.py`.

No case was created. No retired-authority normalization run, overlap-instance
audit, Barrier-A preflight, CTMC solve, DES run, quantitative output inspection,
or scientific verdict occurred in this tranche.

## Section 17.3 tranche boundary

Items 1-44 are schema-tranche requirements. Items 15 and 27 may reach only
`PASS_SCHEMA_GUARD_ONLY` here; their runtime-capability portions remain
`DEFERRED_REQUIRES_SEPARATE_GATE`. No schema-level result is reported as a
runtime-capability pass.

## Section 18 verification status

Section 18 review subject:
`948ff5746adcb66b68fb9c47e519f070dd2c96ba`.

The remote authority was re-locked at the subject state: expected path and
branch, pushed clean, `HEAD...upstream` `0/0`. The documentation publication
commit containing this record is a successor self-identifying evidence commit;
it does not replace the Section 18 review subject above.

The initial evidence-publication successor was
`8336131af19dfa98fceda80fc79dd349b43f19a9`. Later handoff-only documentation
successors must be located from live Git history and likewise do not replace
the review subject.

| Section 18 gate | Status | Subject/evidence |
| --- | --- | --- |
| targeted G6-B protocol/row-family/new tests | PASS_SCHEMA_ONLY | schema contract: `356 passed in 0.66s`; git-scope selection: `19 passed, 1109 deselected in 2.38s`; four-file suite: `1695 passed, 2 skipped in 2634.08s` |
| state/subject/overlap/runtime/capability/refusal tests | PASS_SCHEMA_ONLY | authorization-field audit: `21` fields, `0` true; later roots absent: `0`; future modules absent: `0`; retired focus: `1 passed in 0.23s`; manifest: `1 passed in 1.80s` |
| full repository suite at exact commit | PASS_SCHEMA_ONLY | `2122 passed, 2 skipped in 2684.70s` |
| Ruff check and Python format check | PASS_SCHEMA_ONLY | full Ruff green; format check covered `47` files |
| strict mypy for source and source/tests | PASS_SCHEMA_ONLY | strict source mypy covered `25` files; strict source-plus-tests mypy covered `47` files |
| all tracked JSON duplicate-member parse | PASS_SCHEMA_ONLY | `53` tracked JSON files parsed for duplicate members |
| canonical/self-hash properties across qualified runtimes | PASS_SCHEMA_ONLY | canonical `19` passed on remote Python 3.13.9, local Python 3.12.3, and local Python 3.13.5 |
| every declared retired source and lineage-status fixture without outcome reads | PASS_SCHEMA_ONLY | retired-source focus: `1 passed in 0.23s`; spec digest `b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6` matched; frozen matrix raw SHA `487d81aa79a7bca681db81f19a4d6bd315668c43b1c4538c47f01f099d8e205f` matched |
| exact top-level/nested file sets | PASS_SCHEMA_ONLY | exact top-level file set `5`; exact nested file set `12` |
| git diff --check | PASS_SCHEMA_ONLY | remote working-tree and committed-range whitespace checks passed |
| independent ontology review | APPROVE_SCHEMA_ONLY | no P0-P2 blockers; the noted P3 evidence-publication sync is closed by this documentation successor |
| independent scientific/boundary review | APPROVE_SCHEMA_ONLY | no P0-P2 blockers; the noted P3 evidence-publication sync is closed here; explicitly confirmed schema evidence is not science |
| independent code/capability review | APPROVE_SCHEMA_ONLY | P0/P1/P2/P3 finding counts all `0` |
| final branch re-lock clean, pushed, 0/0 | PASS_SCHEMA_ONLY | remote authority path and branch were pushed clean with `HEAD...upstream` `0/0` |

There is no broad scientific PASS, no broad G6-B PASS, and no Section 18
runtime-capability PASS. The evidence above is schema-only governance evidence
for the exact subject commit.

## Claim boundary

G6-B remains OPEN/PENDING. Exact-twelve schema validity does not establish case
independence, confirmation, generality, robustness, or publication readiness.
All authorization flags remain false. No case construction, retired-authority
normalization, overlap audit, Barrier-A preflight, CTMC solve, DES run, output
inspection, or scientific verdict occurred in this tranche. Items 15 and 27
remain runtime deferred. The next eligible gate is a separately approved
case-construction plan. It is not scientific execution.
