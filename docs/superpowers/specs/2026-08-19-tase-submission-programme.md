# T-ASE Submission Programme

Status: `PROCESS MASTER / P0–P4 CLOSED / P5 OUTLINE ONLY / NO IEEE BODY`
Date: 2026-08-19
Venue: IEEE Transactions on Automation Science and Engineering
Worktree: `D:\worktree\IMS_deadlock-journal-hardening-v1`
Branch: `codex/journal-hardening-v1`
Base scientific facts: article-core v1 `TIER A`; tase_hardening v1 H1–H3
  executed; H4 v1 refused; H4 v2 certified with \(\theta_b=0\); H4-v3
  island closed; H2-v2 in-domain table closed; H3-v2 scale closed.

This file is the operating plan for making Paper A *submittable to T-ASE*.
It is not the paper. Do not write the IEEE body, title-page metadata, or
Note to Practitioners prose until Phase P5. Keep every decision, refusal,
and evidence root in process documents.

## 0. Frozen decisions

1. Single target venue: IEEE T-ASE. Automatica / TAC / JMS are out of
   scope for this programme.
2. Single paper centre: typed local first-hit. P5, P6, BIX full proofs,
   and the original 13-case G6-B overlap are not Paper A main claims.
3. Isolation: all writes stay on `codex/journal-hardening-v1`. Never edit
   `main`. Never overwrite
   `evidence/article_core/minimal_closure_v1/`,
   `evidence/tase_hardening/v1/`, or
   `evidence/tase_hardening/v2/`.
4. New science uses a new scope id and a new evidence root.
5. A general “continue” does not authorize quantitative execution. Each
   phase that creates cases or numbers needs an explicit go on that
   phase’s spec hash, or a named user approval of that phase.
6. Failed or all-completion islands are retained. They are not replaced
   in place.

## 1. Why the current package is not T-ASE-ready

| Blocker | Current fact | T-ASE need |
| --- | --- | --- |
| B1 Manufacturing meaning | H4 v2 \(\theta_b=0\), 65536/65536 hits `F` | An island where admitted `D_local` or `D_global` occurs, and an intervention changes \(\theta_b\) or mean stopped time |
| B2 Scale | H3 max 496 states | At least one family that reaches \(10^3\)–\(10^5\) states or typed refusal at a declared cap, with runtime / kernel-count curves |
| B3 In-domain baselines | H2 siphon refused 32/32 | Same-semantics table that includes *applicable* siphon positives and at least one CRP/local-kernel comparison that is not a G5 replay |
| B4 Novelty locators | Matrix exists as positioning draft | Five-axis rows with exact source locators (paper, section/theorem) for L29/L30/L31/B05 and local-deadlock comparators |
| B5 Practitioner message | None | 100–300 word Note to Practitioners *outline* first; full prose only in P5 |
| B6 Manuscript form | Markdown draft | IEEE template, later. Not this phase |

## 2. Work packages (strict order)

```text
P0  Process lock          — claim ladder, gap ledger, this programme
P1  Island that deadlocks — H4-v3 design → cases → Barrier A → exact/DES
P2  In-domain baselines   — H2-v2 siphon-applicable + optional CRP row
P3  Real scale            — H3-v2 families that hit 1e3–1e5 or refuse
P4  Novelty locators      — five-axis matrix with full-text anchors
P5  T-ASE packaging       — NtP outline, figure list, page budget
                           (still not a polished body until P1–P4 close)
```

P1 is on the critical path. P2 and P3 may be prepared in parallel *as
documents*, but their science runs only after their own case specs exist.
P4 is documentation and may start as soon as P0 exists. P5 waits for P1.

### P0 — Process lock

**Deliverables**

- this file
- `docs/paper/TASE_CLAIM_LADDER.md`
- `docs/verification/TASE_GAP_LEDGER.md`
- handoff / roadmap pointer only (no scientific upgrade)

**Done when** every later phase can cite a claim id and a gap id.

### P1 — H4-v3 deadlock island

**Scientific obligation.** Construct one synthetic two- or three-cell
island such that all of the following hold on the *base* plant:

1. Barrier A returns `certified` (no `completed_job_holds_resource`).
2. The admitted partition contains a nonempty `D_local` or `D_global`.
3. If `D_local` is used, at least one admitted local-hit state has a
   plant outgoing arc (so it is not a terminal SCC).
4. One predeclared intervention (delete backflow **or** add one AGV/buffer
   slot **or** disable one controllable handoff) changes at least one of
   \(\theta_b\), or mean stopped time, by more than the predeclared
   numerical floor.
5. Exact and DES share one stopping hash; `n=65536`; Hoeffding tolerance
   recomputed; primary then repro; 32–48 workers.

**Forbidden.** Calling H4 v2 a manufacturing demonstration. Overwriting
v1/v2. Labelling the island shop-floor data.

**Roots**

- cases: `cases/discovery/tase_hardening_v1/h4_v3/`
- evidence: `evidence/tase_hardening/v3/`
- spec: `docs/superpowers/specs/2026-08-19-tase-h4-v3-island-design.md`

**Done when** v3 report shows Barrier A certified, \(\theta_b>0\) on the
base (or a documented `D_global` time-zero hit plus a changing
intervention), and 6/6 probability cells compatible.

### P2 — In-domain baselines

**Scientific obligation.** Rebuild the baseline table so siphon is not
only a refusal column:

- at least 4 `IMS-SIP^1`-applicable positives where siphon and local
  core agree
- at least 4 typed siphon refusals (OR/AND, multi-capacity, AGV
  projection)
- cycle/SCC false positives retained (C1-type)
- closed-core vs LTS truth FP/FN
- optional: one new CRP overlap row using Prop 6.4 four fields, not a
  G4/G5 hash

**Roots**

- `cases/discovery/tase_hardening_v1/h2_v2/`
- `evidence/tase_hardening/h2_v2/`

**Done when** the table has both applicable agreements and typed
refusals, all on one generator semantics.

### P3 — Real scale

**Scientific obligation.** Replace “576 rows, max 496 states” with a
family that either

- reaches at least \(10^3\) states on ≥8 rows and \(10^4\) on ≥2 rows, or
- hits a declared cap (\(10^5\) states or 300 s) and reports refusal
  rate, runtime, and kernel-family size versus jobs/resources/capacity.

Use the existing 48-worker contract. BLAS threads stay 1.

**Roots**

- `cases/discovery/tase_hardening_v1/h3_v2/`
- `evidence/tase_hardening/h3_v2/`

**Done when** a scale figure can be drawn from v2 numbers without using
the 496-state family as “large”.

### P4 — Novelty locators

**Obligation.** For each comparator in
`docs/literature/NOVELTY_DIFFERENCE_MATRIX.md`, add:

- citation key (L29/L30/L31/B05/…)
- theorem/section locator already audited in G1
- one sentence: “they lack X; we add checkable object Y”
- Paper A claim id that is allowed to cite it

No new priority slogans. No “first reachable certificate”.

**Done when** P1–P3 claim sentences can be footnoted to a locator row.

### P5 — Packaging, not body

**Obligation.** Produce:

- Note to Practitioners *outline* (bullets, 100–300 words later)
- figure list (research chain, case panel, exact/DES, island before/after)
- page budget (T-ASE regular paper, ~12 pp without mandatory extras)
- what goes to appendix (P3e, P5, P6)

Do **not** rewrite `IMS_LOCAL_FIRST_HIT_THEORY_AND_CASES.md` into IEEE
format in this programme until P1 is closed.

## 3. Parallel compute (standing rule)

Dell Xeon w7-3465X, 56 threads, ~127 GiB. Default 32 workers, 48 if free
RAM ≥ 64 GiB. Primary wave completes before repro. One reducer. GPU
unused. Serial H3/H4 sweeps are protocol misses.

## 4. What this programme will not do

- Close G6-B eight-dimension overlap as a T-ASE prerequisite
- Start G6-C/D/E
- Risk-budget supervisor theorems (Paper C)
- General plant/S3PR isomorphism
- Claim H4 v2 method superiority
- Push to `main` without an explicit later request

## 5. Immediate next step

P0–P4 are closed on this worktree. P5 has an NtP *outline* and page
budget only. Do **not** start the IEEE body until the user asks for
manuscript packaging. Optional leftover: H5 CRP four-field row
(explicitly omitted). G5 FAIL and G6-B `OPEN_PENDING` stay retained.
