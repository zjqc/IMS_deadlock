# G6-B Authorization-Gate Remediation Review

Date: 2026-08-02

This record closes two fail-open authorization-validation defects found during
independent review of the schema-only G6-B publication branch. It is an
engineering/governance correction. It is not a case-construction
authorization, normalization authorization, target-certification preflight
authorization, quantitative-execution authorization, or scientific result.

## Locked subject

- Authority worktree:
  `D:\worktree\IMS_deadlock-g6b-spec-final-review`.
- Branch:
  `codex/g6b-case-target-certification-final-review`.
- Parent:
  `f92d6360619e9b21617f366147812d480ac11f1c`.
- Remediation subject:
  `b2f2f285a68793ce9ca4cb1b47a05dd7a3cfb9bb`.
- Commit subject:
  `fix:g6b-authorization-gates`.
- Runtime:
  `D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe`
  (Python 3.13.9), with `PYTHONPATH` bound to the authority worktree `src`,
  bytecode disabled, and the pytest cache provider disabled.

The committed worktree was re-locked clean after the remediation commit. At
the pre-push lock it was one commit ahead of its upstream and had no unrelated
tracked or untracked change.

## Findings repaired

### 1. Missing explicit Barrier-A authorization validator

The schema described a target-certification preflight authorization artifact,
but the shared contract module had no first-class validator that fail-closed on
its exact schema, scope, source/runtime identities, command manifest, evidence
root, operation arrays, resource budget, stop conditions, and self hashes.

The remediation adds `validate_preflight_authorization` and regression coverage
for:

- exact schema and required fields;
- explicit `authorized is True`;
- `invalidated_by_identity_drift is False`;
- exact bundle/case scope and sealed-manifest/runtime identities;
- ordered allowed/forbidden operations and exact command-manifest links;
- allowed entrypoint, output schemas, side effects, resource budget, and stop
  conditions;
- exact evidence-root schema
  `ims-deadlock/g6b-preflight-evidence-root/v1`;
- exact evidence root `evidence/g6b/target_certification/{bundle_id}`;
- refusal of quantitative, case-unit, governance, arbitrary fallback, stale-
  schema, materialized, and mismatched roots;
- canonical record/root/command-manifest/command-record hash links.

### 2. Retired-normalization authorization accepted false/drifted records

`validate_normalization_authorization` now requires `authorized is True` and
`invalidated_by_identity_drift is False`. Boolean-like values, explicit false,
and identity-drifted records fail closed.

## Changed files and exact content hashes

| File | SHA-256 at remediation subject |
| --- | --- |
| `src/ims_deadlock/g6b_schema_contracts.py` | `2769d051ea10770b7b8af6199341e49a70c970e44b8c663bcbf573e6597e306b` |
| `tests/test_g6b_schema_contracts.py` | `a084bccb51669cf10cba268ef6649f360e1c08646ffd4d5967dc908e2b5cbc97` |

The commit contains 575 insertions and 7 deletions across those two files.
No case, governance instance, preflight evidence, or quantitative artifact root
was created.

## TDD and verification evidence

The regression tests were introduced before implementation and produced the
intended RED behavior for the missing validator, false/drifted normalization
authorization, and noncanonical preflight roots. The final subject contains the
GREEN regression suite; the interactive RED output is not presented as a
property of the final commit.

| Check | Result |
| --- | --- |
| Focused schema-contract suite | `379 passed` |
| Focused preflight-authorization tests | `20 passed` |
| Exact touched-file Ruff check | passed |
| Exact touched-file Ruff format check | passed |
| Strict mypy on touched source/test | `Success: no issues found` |
| `git diff --check` | passed |
| Full repository suite at remediation subject | `2145 passed, 2 skipped in 2766.88s (0:46:06)` |
| Documentation-successor scope guard | unlisted-path RED `1 failed, 1 passed`; allowlist-only exact-set RED `1 failed, 1 passed`; final GREEN `2 passed`; Task-6 selection `17 passed, 1111 deselected` |
| Scope-guard Ruff/format/strict mypy | passed |

The historical predecessor full-suite result was
`2122 passed, 2 skipped in 2635.37s (0:43:55)`. It is retained only as a
pre-remediation baseline and is not substituted for the remediation-subject
run.

The documentation publication successor adds this review artifact and updates
the handoff, roadmap, and Section 18 successor record. Its only test change adds
`docs/verification/G6_B_AUTHORIZATION_GATE_REMEDIATION_REVIEW.md` to the
existing fail-closed declared-path allowlist and its exact-set assertion in
`tests/test_g6b_row_family_protocol.py`. Before the path was added, the scope
guard produced the intended RED failure naming this exact path. The
allowlist-only intermediate edit then produced the intended exact-set RED
failure; after the matching assertion was synchronized, the two direct
documentation/scope tests and the 17-test Task-6 selection passed. This
successor does not modify production code or schemas.
The 2145-test full-suite claim remains explicitly bound to remediation subject
`b2f2f285...`, while the successor is supported by the narrower tests above.

## Independent review

The initial independent review reported two HIGH findings corresponding to the
two defects above. A follow-up review then found one additional HIGH path-scope
gap: a correctly rehashed authorization could substitute a quantitative,
case-unit, governance, or arbitrary fallback root. Regression tests were added
with the entire linked hash chain resealed, and the validator was restricted to
the exact preflight root schema and path. A final strict-mypy inference issue in
the touched source was also corrected with explicit string narrowing.

The final independent code/capability review returned `APPROVE`, with zero
Critical, High, or Medium findings. This verdict is scoped to the exact
remediation subject and does not review future case construction.

## Remaining pre-case blocker

The schema-only bundle still has a separate design ambiguity: its sealed-
prediction and metric payload contracts require predeclared `estimand_id`
fields, while its recursive/prohibited construction-instance field lists also
prohibit `estimand_id`. Current row-family validation does not resolve that
future-instance contradiction. It must be handled by an exact, independently
reviewed case-construction plan/corrigendum before any case authorization or
case-instance root is created.

## Claim boundary

All canonical current typed capabilities remain false. G6-B remains
`OPEN/PENDING`; G6-C/D/E remain unstarted. No retired normalization, actual
overlap audit, Barrier-A preflight, CTMC, DES, output inspection, scientific
scoring, or G6-B verdict occurred. The publication PR must remain draft while
the known pre-case design blocker and the separately approved construction
plan are unresolved.
