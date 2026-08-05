# G6-B Minimal Article Closure Implementation Plan

> Execute task-by-task with the repository's normal edit-test-verify workflow.

**Goal:** Produce a logically self-consistent theory/method article closure
from a predeclared six-case panel, without requiring one method to cover every
sealed case and without upgrading discovery evidence into held-out
confirmation.

**Architecture:** Add a small article-specific typed finite-LTS layer that
validates the theorem obligations directly, converts the stopped cases into
finite competing-absorption CTMCs, runs one exact solver and one independently
seeded DES implementation, and emits a machine-readable closure report. Keep
the original G6-B eight-dimension overlap gate unchanged and explicitly open.

**Tech stack:** Python 3.13.9, existing `ims_deadlock.ctmc`, existing canonical
JSON utilities, Python standard library, pytest, Ruff, strict mypy.

## Task 1: Freeze the article scope before outcomes

**Create:**

- `docs/superpowers/specs/2026-08-06-g6b-minimal-article-closure-scope.md`
- `cases/article_core/article_scope_lock_v1.json`
- `docs/superpowers/plans/2026-08-06-g6b-minimal-article-closure.md`

1. Validate the scope lock's exact six-case panel, original 13-case denominator,
   no-substitution rule, claim ladder, 4096-replication plan, seed, and
   Hoeffding tolerance.
2. Bind the sealed bundle raw/self hashes and retired normalization raw/self
   hashes.
3. Commit these files before adding an executable case or observing a result.

Expected commit message:

```text
docs(article): freeze minimal theory-case closure scope
```

## Task 2: Specify the typed finite-LTS article contract with RED tests

**Create:**

- `tests/test_article_core.py`

**Test first:**

1. Load and self-hash validate the scope lock.
2. Require exact source hashes for the five sealed case identities.
3. Require disjoint `D_global`, `D_local`, and `F` classes.
4. Require A2b proof flags for A2b admission.
5. Require graph nonreachability from every complete-LTS `D_local` state to
   `F`.
6. Prove the bypass candidate reaches `F` and is not in `D_local`.
7. Prove `D_global` precedence prevents double counting.
8. Reject nonpositive/nonfinite rates and unselected closed classes.
9. Verify the bridge analytical probability is `1 / 3` within solver
   tolerance.
10. Verify DES seed derivation and no outcome-driven retry surface.

Run RED:

```bat
set PYTHONDONTWRITEBYTECODE=1
set PYTHONPATH=%CD%\src
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests\test_article_core.py
```

Expected: import failure because `ims_deadlock.article_core` does not yet
exist.

## Task 3: Implement article cases, theorem checks, exact solution, and DES

**Create:**

- `src/ims_deadlock/article_core.py`
- `cases/article_core/g6b_article_bridge_competing_local_completion_v1.json`

Implement these public surfaces:

```python
def load_article_scope(repo_root: Path) -> Mapping[str, JsonValue]: ...
def build_article_cases(repo_root: Path) -> tuple[ArticleCase, ...]: ...
def validate_article_case(case: ArticleCase) -> CaseCertificate: ...
def solve_article_case(case: ArticleCase) -> ExactFirstHitResult: ...
def simulate_article_case(
    case: ArticleCase,
    *,
    sample_count: int,
    master_seed: int,
) -> DesFirstHitResult: ...
def run_article_closure(repo_root: Path) -> ArticleClosureResult: ...
```

Implementation rules:

- treat the three snapshot witnesses as time-zero classifications;
- use the sealed explicit transitions for the multi-kernel and bypass cases;
- keep plant arcs and stopped-process arcs separate;
- classify `D_global` before considering `D_local`;
- use A2b only when its explicit proof flag is true;
- otherwise admit `D_local` only after complete graph nonreachability to `F`;
- derive the bridge CTMC from rates 1 and 2;
- derive replication seeds with the frozen SHA-256 rule;
- do not import G5/G6 replay runners or read outcome files.

Run GREEN:

```bat
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests\test_article_core.py
```

Expected: all article-core tests pass.

## Task 4: Add a write-once article result command

**Modify:**

- `src/ims_deadlock/article_core.py`
- `tests/test_article_core.py`

**Create during execution only:**

- `evidence/article_core/minimal_closure_v1/article_case_certificates.json`
- `evidence/article_core/minimal_closure_v1/exact_results.json`
- `evidence/article_core/minimal_closure_v1/des_results.json`
- `evidence/article_core/minimal_closure_v1/article_closure_report.json`

The command must fail if the output root already exists, write a manifest last,
and never retry a missed Monte Carlo tolerance in place. The report must retain
every one of the six predeclared cases and select Tier A, Tier B-A2b, Tier B-LTS,
or Tier C mechanically.

Run one preflight-only dry build that performs validation and exact solving in
memory but writes no evidence. Then run the write-once command once.

The workload is six tiny finite cases and 24,576 DES replications. A pilot of
256 bridge replications will establish actual throughput before the final run.
Parallel workers are unnecessary unless the pilot projects material runtime;
process-start overhead would dominate this case size. If projected runtime
becomes material, split independent replication-index ranges across at most
four remote workers and reduce them in canonical order.

## Task 5: Verify the evidence and close the theory-case map

**Create:**

- `docs/verification/G6_B_MINIMAL_ARTICLE_CLOSURE_REPORT.md`

The report must include:

- target path, branch, HEAD/tree, runtime, and dirty-state locks;
- scope-lock and evidence hashes;
- the six-case theorem obligation table;
- exact and DES values for all 18 estimand cells;
- absolute errors and the frozen simultaneous tolerance;
- mechanically selected claim tier;
- all refusals, limitations, and unresolved original G6-B gates;
- an explicit statement that time-zero witnesses test classification semantics,
  while the bridge case supplies the nontrivial probability calculation.

Validation sequence:

```bat
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests\test_article_core.py tests\test_ctmc.py tests\test_stochastic.py
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\ruff.exe check src\ims_deadlock\article_core.py tests\test_article_core.py
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\ruff.exe format --check src\ims_deadlock\article_core.py tests\test_article_core.py
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\mypy.exe --no-incremental src\ims_deadlock\article_core.py
git diff --check
```

## Task 6: Write the manuscript from the closed evidence

**Create:**

- `docs/paper/IMS_LOCAL_FIRST_HIT_THEORY_AND_CASES.md`
- `docs/paper/ARTICLE_CLAIM_EVIDENCE_MATRIX.md`

Write only after Task 5 determines the tier. Preserve the full mathematical
definitions, A2b assumptions, complete-LTS fallback, counterexamples, exact
bridge derivation, DES protocol, negative evidence, and limitations. The claim
matrix must map every manuscript claim to a theorem, case certificate, or
quantitative artifact and mark unsupported stronger claims as forbidden.

## Task 7: Repository integration

1. Run targeted verification, then the full test suite. Use up to four xdist
   workers only if live capacity and xdist availability are confirmed.
2. Inspect exact diff/status and preserve unrelated work.
3. Commit evidence and manuscript in reviewable commits.
4. Push `codex/g6b-minimal-article-closure` and open or update a fully described
   Draft PR. Do not merge while the original stacked PR ancestry remains
   unresolved.
5. Update `PROJECT_HANDOFF.md` and `docs/ROADMAP.md` with the achieved article
   tier and the still-open original G6-B/G6-C/D/E gates.
