# G6-B Materialization Projection-Scope Wording Erratum Review

Status: `PASS / WORDING-ONLY / REPOSITORY-PUBLICATION REVIEW`

Date: 2026-08-05

## Reviewed subject

- Erratum:
  `docs/superpowers/specs/2026-08-05-g6b-case-construction-materialization-contract-wording-erratum.md`.
- Erratum raw SHA-256:
  `5192aec8e7269ec0c209e535c263a31c39be8c3f46238cde59e887a7b1db6841`.
- Immutable original corrigendum SHA-256:
  `ff469d9c5105835fde5feb170e501bdde14506df50632990f7c2cddc251da36c`.
- Immutable approved v2 plan SHA-256:
  `81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7`.
- Immutable independent v2 plan-review SHA-256:
  `da6da7c2e513e11761e439f8b43ef6260556c912d3e730f94f15eae088d90ea0`.

The review rejected direct modification of the approved corrigendum because it
would invalidate the plan's and review's content-addressed subject statements.
The successor erratum preserves those exact historical bytes.

## Trigger and resolution

PR #7 review identified that the background phrase `those five per-case
projections` incorrectly sounds as though all five subjects share one scope.
The successor erratum names all five subjects and records the already normative
scope split:

- case content is case scoped;
- DES and exact output-root reservations are method scoped;
- DES and exact random-stream manifests are method scoped.

The original file roster already contains the five separately stored paths,
and its `File-role and hash closure` section already states the same case/group
versus method scope. The finding is therefore a wording ambiguity, not a
missing artifact or executable contract defect.

## Independent review lanes

Three read-only lanes reviewed the exact erratum subject and its publication
integration:

1. semantic/governance review: `PASS`, P0/P1/P2 `0/0/0`;
2. mechanical hash, path-roster, and scope review: `PASS`, P0/P1/P2 `0/0/0`;
3. handoff/roadmap consistency review after repair: `PASS`, P0/P1/P2 `0/0/0`.

The mechanical lane independently recomputed the three bound historical hashes
from the PR #9 head files and confirmed C3 commit
`0fa08e66c249fb19d8c014127cca8441efa90505` / tree
`8153fd46c4dae6dbd08a20fec93eab469fa8bc37` from the durable R7 evidence.

## Regression evidence

The first full PR-head suite correctly retained two failures rather than being
reported as green:

```text
2 failed, 2419 passed, 2 skipped in 895.66s
```

Both failures were stale publication-guard assumptions: the cumulative
Task6-origin diff allowlist had not declared the later R7/normalization/erratum
documents, and a handoff test still required two transitional prose phrases.
The repair added only exact document paths to the allowlist and replaced the
prose checks with the durable Task6 review path and historical schema-governance
fact. Forbidden science/capability prefixes, exact-path refusals, the exact
394-file R5 artifact allowlist, later-root absence, and capability-false checks
remain unchanged.

The two exact failing node IDs then returned:

```text
2 passed in 0.72s
```

`git diff --check` also passed. The full repository suite and static checks are
run again on the final publication commit before merge; their results are merge
evidence rather than claims embedded into this content-addressed review.

## Boundary verdict

The erratum changes wording only. It does not change a path, artifact, schema,
hash subject, count, writer, validator, recovery transition, task, gate,
authorization, executed byte, or scientific status. It does not authorize or
rerun case construction, retired-authority normalization, overlap, target
preflight, CTMC, DES, scoring, output inspection, or confirmation.

G6-B remains `OPEN/PENDING`; downstream typed capabilities remain false.
