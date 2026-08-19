# T-ASE Theory Height +1 Plan

Status: `PLAN / NO SCIENCE YET / WORKTREE ONLY`
Date: 2026-08-19
Worktree: `D:\worktree\IMS_deadlock-journal-hardening-v1`
Branch: `codex/journal-hardening-v1` (now on `origin`)
Baseline HEAD at plan writing: `5fb9abd`
Companion verdict: `docs/verification/TASE_THEORY_HEIGHT_VERDICT.md`

This plan raises theoretical height **one tier** above the current scoped
T-ASE methods paper. It does not target Automatica/TAC, does not close
G6-B, and does not authorize shop-floor claims.

## 0. What “+1 tier” means

Current tier (already earned, do not reopen):

```text
operational IMS first-hit semantics
+ complete proofs on IMS^CW
+ typed admission / bypass refusal
+ diagnostic siphon on IMS-SIP^1
+ synthetic island that is already in D^L at t = 0
+ same-semantics baselines and a tandem scale family
```

AE residual risk at this tier: “toy island + incremental versus T-ASE
2026 CRP (L31).”

Target tier after this plan:

```text
current tier
+ an independently hashed published-net comparator
  so Proposition 4 field 4 is decided, not refused by missing embedding
+ a manufacturing island whose first local hit occurs at positive time
  (base m > 0, not already absorbing)
+ a finite-state supervisor baseline on the same island semantics
  (Ramadge–Wonham / boundary-unsafe LES style), labelled baseline
```

That is one step up in *comparability and dynamics*, not a new general
iff that beats Lu–Chen–Hadjicostis–Li (L29) or Su et al. CRP (L31).

Success is defined by the three gates in §4. Missing any one gate keeps
the paper at the current tier.

## 1. Frozen decisions

1. Venue remains IEEE T-ASE Regular Paper only.
2. Paper centre remains typed local first-hit. The new work *clothes and
   compares* that centre; it does not replace it.
3. Isolation: all writes stay on `codex/journal-hardening-v1`. Never edit
   `main`. Never overwrite
   `evidence/article_core/minimal_closure_v1/`,
   `evidence/tase_hardening/v1|v2|v3/`,
   `evidence/tase_hardening/h2_v2|h3_v2|h5/`.
4. New science uses new scope fragments and new evidence roots:
   - `evidence/tase_hardening/h6_embed/`
   - `evidence/tase_hardening/h7_island_v4/`
   - `evidence/tase_hardening/h8_supervisor/`
5. Failed clothings are retained. They are not replaced in place.
6. H4-v3 stays the time-zero local-hit witness. H7 is a *new* island,
   not an overwrite of v3.
7. G5 FAIL and G6-B `OPEN_PENDING` stay retained.
8. Forbidden sentences stay TX1–TX12.
9. A general “continue” still does not authorize quantitative waves.
   Each of H6/H7/H8 needs its own hashed spec (or an explicit user go
   on that spec hash) before case bytes or numbers are written.
10. Compute: Xeon w7-3465X, 32–48 workers, BLAS threads = 1, primary
    then repro, one reducer. Serial H7 DES is a protocol miss.

## 2. Why these three packages, and not others

The height verdict named exactly three raisers that move AE risk without
changing venue:

| Package | Risk it removes | What it is not |
| --- | --- | --- |
| H6 published-net embedding | “you never touched L31’s object” | not a CRP theorem; not SBA |
| H7 positive-time island | “already stopped toy” | not shop-floor; not H4-v3 rewrite |
| H8 finite supervisor baseline | “no method comparison a T-ASE reader knows” | not Paper C; not risk-budget optimal |

Rejected as *this* tier (they jump two tiers or change the paper):

- General IMS \(\equiv\) S3PR isomorphism
- Bit-polynomial reachability
- Maximally permissive monitor existence (MCPP)
- G6-B eight-dimension overlap as a T-ASE gate
- Shop-floor logs / throughput
- Doob-\(h\) as a controller
- Raising Theorem 3 from sufficient to necessary

## 3. Work packages

### H6 — Independent S4PR / published-net embedding

**Scientific obligation.** Build a *new* subject whose Petri encoding is
taken from a published S4PR/S3PR figure (prefer L31’s running example
or a classical small S3PR from Ezpeleta–Colom–Martínez 1995), then:

1. Write an embedding certificate with four frozen hashes:
   - source PDF/figure locator (already in G1)
   - place/transition map \(\iota: P\cup T \to\) IMS resources/events
   - IMS model+state+registry hash
   - independent LTS BFS reachability hash
2. Score Proposition 4’s four fields on that subject:
   - field 1: target reachable by *our* BFS, not by a supplied prefix
   - field 2: local certificate family nonempty or recorded empty
   - field 3: \(\lvert\{K:R_K=R^{\star}\}\rvert\)
   - field 4: `true` only if the embedding certificate verifies
3. Do **not** run SBA. Do **not** generate CRP candidates. Do **not**
   reuse G4/G5 hashes.
4. Two rows are required:
   - H6-A: in-domain published net, field 4 true, fields 1–3 reported
     honestly (agreement may still be false if 1–3 fail)
   - H6-B: same net after a declared IMS-only distortion (BAS hold or
     AGV token), field 4 false or fields 1–3 change, typed reason

**Done when** a reviewer can open H6-A and check locator → map → hashes
→ four fields without trusting a chat summary. Agreement is allowed to
be false. A missing embedding is no longer the reason.

**Roots.** `cases/discovery/tase_hardening_v1/h6/` and
`evidence/tase_hardening/h6_embed/`.

**Manuscript delta.** One subsection in Related Work / Experiments:
“Proposition 4 on a published net.” Update Table I checkable-addition
cell for L31. Do not claim CRP iff.

### H7 — Positive-time local-hit island (v4)

**Scientific obligation.** One new synthetic two- or three-cell island
such that **all** hold on the *base* plant:

1. Barrier \(\mathbf{B}\) certified (no `completed_job_holds_resource`).
2. Initial state \(\notin D^{\mathrm{G}}\cup D^{\mathrm{L}}\cup F\).
3. Admitted \(D^{\mathrm{L}}\) is nonempty, and at least one admitted
   local-hit state has a plant outgoing arc.
4. From the initial state, \(\theta^{\mathrm{L}}>0\) and exact mean
   stopped time \(m>0\) (numerical floor: \(m\ge 0.25\) time units under
   the declared rates, or a documented refusal if the floor cannot be
   met without violating 1–3).
5. One predeclared intervention (extra AGV slot **or** delete one
   backflow **or** disable one controllable handoff) changes
   \(\theta^{\mathrm{B}}\) or \(m\) by more than the Hoeffding band.
6. Exact and DES share one stopping hash; \(n_{\mathrm{s}}=65536\);
   primary then repro; 32–48 workers.

**Design constraint learned from H4-v3.** Do not start in the interlock.
Start with at least one job still moving into the contested pair, so the
first hit is a stopping *event*, not the initial condition.

**Forbidden.** Overwriting H4-v3. Calling v4 shop-floor. Calling H4-v2
a deadlock demonstration.

**Roots.** `cases/discovery/tase_hardening_v1/h7/` and
`evidence/tase_hardening/h7_island_v4/`.

**Manuscript delta.** Replace “already-hit island” as the *main*
manufacturing figure with H7; keep H4-v3 as the time-zero boundary
example (it remains scientifically correct and useful).

### H8 — Finite-state supervisor baseline on the same island

**Scientific obligation.** On the H7 base plant (or on H4-v3 if H7 is
refused), compute a finite explicit-graph supervisor in the
Ramadge–Wonham nonblocking sense, or a boundary-unsafe LES in the
sense of Nazeem–Reveliotis T-ASE 2011, and report four numbers on
*one* semantics:

| Quantity | Meaning |
| --- | --- |
| \(\lvert X\rvert\) | plant stable states |
| \(\lvert X_{\mathrm{safe}}\rvert\) | states retained by the supervisor |
| disabled controllable events | count of cut edges |
| \(\theta^{\mathrm{B}},m\) under the supervisor | first-hit KPIs on the supervised stopped graph |

The supervisor is a **baseline**, not a new theorem. State explicitly:
explicit-graph synthesis is polynomial in \(\lvert X\rvert\); compact
input remains at least NP-hard; this is not a risk-budget supervisor
and not maximally permissive in the MCPP sense.

**Done when** Table II/H7 and the supervisor table share the same
plant, same registry, and same stopping hash family.

**Roots.** `cases/discovery/tase_hardening_v1/h8/` and
`evidence/tase_hardening/h8_supervisor/`.

**Manuscript delta.** New comparison subsection. Cite [5] and [15] as
baselines. Do not open Paper C.

## 4. Gates (all required for +1)

| Gate | Evidence | Fail action |
| --- | --- | --- |
| G-H6 | H6-A embedding certificate verifies; field 4 decided | stay at current tier; do not invent field 4 |
| G-H7 | v4 report: initial not absorbing, \(m>0\), \(\mathbf{B}\) certified, 6/6 compatible or typed DES refusal | keep H4-v3 as main island; do not call +1 done |
| G-H8 | supervisor table on the same plant | omit the supervisor subsection; height +1 incomplete |

Manuscript claim after all three gates:

```text
typed local first-hit,
compared on a published-net embedding,
demonstrated on an island that hits D^L at positive time,
and contrasted with a finite-state supervisor on the same graph.
```

## 5. Order and compute

```text
H6 design spec (hash) → H6 implementation + tests → H6 wave
H7 design spec (hash) → H7 plant + Barrier B tests → H7 exact/DES
H8 depends on H7 plant (or documented fallback to H4-v3)
Manuscript delta only after G-H6 and G-H7
```

H6 and H7 *design* may proceed in parallel. H8 implementation waits for
the locked H7 (or fallback) plant hash. H7 DES uses 48 workers if free
RAM \(\ge 64\,\mathrm{GiB}\). H6 is cheap (tiny nets). H8 is explicit
graph and should stay well under the H3 state cap.

## 6. Theory obligations that must be written, not just coded

H6: a one-page embedding definition: what \(\iota\) preserves (holds,
requests, capacities, enabled events) and what it does *not* preserve
(BAS, AGV occupancy unless encoded). Proof that field 1 is independent
of any prefix claimed by the source paper.

H7: no new theorem required if Theorems 3–5 apply. If the plant needs a
weaker A2b, use Theorem 4 and say so.

H8: quote the existing nonblocking fixed-point (Ramadge–Wonham Th. 7.1 /
Prop. 7.1) as a *baseline citation*, not as a new proof. Record that
the supervisor is computed on the explicit LTS of Lemma 1.

Do not add a Theorem 13 that restates Theorem 3.

## 7. Manuscript impact (after gates)

- Abstract: one clause on positive-time hit and one clause on the
  published-net four-field decision.
- NtP: the drain/intervention sentence may move from “already stopped”
  to “the cell runs and then locally stops; a one-slot change prevents
  that stop.”
- §X: H7 becomes the lead island figure; H4-v3 becomes “already-hit
  boundary.”
- §II / Table I: L31 cell updated with H6 locator + field-4 decision.
- Limitations: still no shop floor; still no CRP theorem; still no
  general S3PR isomorphism.

IEEE two-column conversion remains later production.

## 8. Immediate next step

Write and hash `docs/superpowers/specs/2026-08-19-tase-h6-embedding-design.md`
and `docs/superpowers/specs/2026-08-19-tase-h7-island-v4-design.md`.
Do not materialize cases until those two hashes are named and approved
(or the user names them).
