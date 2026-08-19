# Journal Theory Audit v1

Status: `AUDIT / NO SCIENCE EXECUTION / NO CLAIM UPGRADE`

Worktree: `D:\worktree\IMS_deadlock-journal-hardening-v1`
Branch: `codex/journal-hardening-v1`
Base HEAD: `5f852e06650e29b71f79bc344246aca79524bfba`
Base tree: `8f6d732ff3e3ae3207e9a2da6340ce079f9708b4`
Date: 2026-08-19 Asia/Shanghai

This audit reads the live worktree, not Mac `bootstrap_source`. It does not
rerun article-core v1, does not change frozen evidence bytes, and does not
upgrade G6-B or the paper gate.

Verdict vocabulary:

- `KEEP` — wording is already scoped; no repair required for Paper A
- `TIGHTEN` — keep the theorem, make the hidden assumption explicit
- `REPAIR` — a proof step or ledger binding is incomplete
- `DEMOTE` — do not sell the result as a Paper A novelty or iff

No item below is a P0 unsoundness finding against Theorem 1 or Proposition 2
of the scoped English manuscript.

## A. Per-item audit

### A1. P1 is a representation theorem

- Locator: `docs/theory/CORE_THEOREMS_AND_PROOFS.md` §1 Theorem P1;
  `docs/theory/PROOF_OBLIGATIONS.md` PO-T1-1..4 closed, PO-T1-5/6 open;
  Chinese chain `docs/paper/IMS_COMPLETE_RESEARCH_CHAIN_ZH.md` §2.6
- Claim as written: any `IMS-RAS^CW` has a finite stable LTS and a 1-safe
  one-place-per-state reachability net with step correspondence.
- Hidden assumption: places are states, not resources. Safety is by
  construction (one token, one consume/produce).
- Possible overclaim: presenting P1 as a Petri structural contribution or as
  an S3PR bridge.
- Repair: keep P1 as background / appendix. Do not list it among Paper A
  novelties. Leave PO-T1-5/6 open.
- Verdict: `DEMOTE` as novelty; `KEEP` as representation lemma
- Touches frozen article-core? no

### A2. P2 reverse direction is relative to the declared registry

- Locator: CORE §2 Theorem P2 reverse; CW4, CW8, CW10;
  `src/ims_deadlock/certificates.py` (certificate extractor);
  P2c implementation note that closed-world completeness is human-audited
- Claim as written: a covering closed blocking kernel implies no admissible
  successor, hence capacity-mediated global operational deadlock.
- Hidden assumption: every currently admissible non-zero-time event is in
  the transition registry and is captured by `Alt_s(j)`.
- Possible overclaim: an iff against the unmodelled physical plant, rather
  than against the declared `TransitionSpec` world.
- Repair: Paper A and CORE should say “relative to the declared complete
  registry.” A machine-checkable registry-completeness audit is a hardening
  obligation, not a new iff. G6 already refuses missing rates / incomplete
  LTS; that refusal must stay visible.
- Verdict: `TIGHTEN`
- Touches frozen article-core? no (manuscript already treats registry
  completeness as a scope condition)

### A3. P2c uses ordinary empty siphons on a diagnostic net

- Locator: CORE §2 P2c; `src/ims_deadlock/petri.py` `is_siphon`
  (`•Σ ⊆ Σ•` via “every transition that outputs into Σ also inputs from Σ”);
  `minimal_empty_siphons`; CE-SIP1
- Claim as written: in reachable stable `IMS-SIP^1`, inclusion-minimal local
  closed cores correspond to inclusion-minimal empty siphons of the
  state-induced wait-snapshot net.
- Hidden assumption: the net is not a plant S3PR. Emptiness is residual-zero
  unit-capacity marking. The siphon predicate is ordinary, not a general
  deadly-siphon + liveness theorem.
- Possible overclaim: “IMS deadlock iff Petri siphon.”
- Repair: keep the diagnostic-net scope. In Paper A, mention P2c only as a
  restricted comparator, not as the main theorem. Paper B must restate the
  siphon dialect and the inverse-map hypotheses.
- Verdict: `TIGHTEN` (already scoped; wording must stay diagnostic)
- Touches frozen article-core? no

### A4. P3 can look tautological without a non-chain-decomposable refusal

- Locator: CORE §3 Theorem P3 and Definition 3.2; PO-T4-1..4 closed;
  no dedicated non-chain-decomposable covering-kernel case
- Claim as written: if every covering closed kernel is chain-decomposable and
  a global acquisition strict order exists, then no capacity-mediated global
  deadlock.
- Hidden assumption: kernels that cannot be charged to a holder-dependency
  chain are outside the theorem, not counterexamples to it.
- Possible overclaim: “strict resource order prevents manufacturing deadlock.”
- Repair: keep P3 as a sufficient condition. Design case
  `H1_P3_nonchain_refuse` so P3 returns not-applicable rather than
  deadlock-free.
- Verdict: `TIGHTEN` + future case
- Touches frozen article-core? no

### A5. A2b residual-upper-bound step

- Locator: `docs/theory/G6_LOCAL_FIRST_HIT_AND_STOPPING_THEOREMS.md` Lemma 3.2
  steps 4–6; English manuscript Theorem 1 proof
- Claim as written: outside jobs cannot raise availability of witness units
  above the hit-state bound, and A2b blocks request-independent bypass, so
  kernel jobs never complete.
- Hidden assumption: witness units held by kernel jobs stay locked (A3, A5);
  residual used by outside jobs returns at most those residual units;
  A2b excludes a same-mode bypass that ignores current requests.
- Possible overclaim: the certificate object is invariant; A2b is necessary.
- Repair: write an explicit capacity invariant in the next theory increment:

  ```text
  for each witness resource r:
    locked_by_J_K(r) is nonincreasing
    avail(r) <= cap(r) - locked_by_J_K(r)
  ```

  The manuscript already says the invariant is job noncompletion, not
  certificate JSON identity. Add the inequality in G6 theory, not in v1
  evidence JSON.
- Verdict: `TIGHTEN`
- Touches frozen article-core? no (proof prose only)

### A6. Global-before-local precedence is a convention

- Locator: manuscript §2.2; G6 definition 2.2–2.3; article case
  `g6b_cu_nc_dglobal_only_with_dlocal_v1`
- Claim as written: a state satisfying the global predicate is counted only
  in `D_global`.
- Hidden assumption: this is the versioned estimand rule, not a physical law.
- Possible overclaim: “nature counts global first.”
- Repair: keep C5 / F6 as written. Always attach the estimand id.
- Verdict: `KEEP`
- Touches frozen article-core? no

### A7. Theorem 5.1 is algorithmic soundness

- Locator: G6 §5 Theorem 5.1 and the structural-refusal list
- Claim as written: if the partition algorithm returns, the reported classes
  are mutually exclusive under the precedence rule and exact/DES can share
  labels.
- Hidden assumption: success means the algorithm did not refuse.
- Possible overclaim: a new existence theory of absorption.
- Repair: cite it as a soundness theorem for the stopped-process construction.
- Verdict: `KEEP` if claimed as soundness; `DEMOTE` if claimed as novelty
  beyond the ontology
- Touches frozen article-core? no

### A8. All-minimal completeness is subset enumeration

- Locator: G6 Proposition 6.2; complexity §7
- Claim as written: cardinality-increasing blocked-job subsets plus
  inclusion-minimal witness filtering return every minimal local kernel.
- Hidden assumption: jobs, alternatives, and resources are finite (A0).
- Possible overclaim: a polynomial structural detector.
- Repair: Paper A must keep the exponential worst case. T-ASE hardening
  Family H3 reports actual family size vs job count.
- Verdict: `KEEP` with mandatory complexity sentence
- Touches frozen article-core? no

### A9. Counterexample ledger was stale on C1/C3/C4

- Locator: `docs/theory/COUNTEREXAMPLE_LEDGER.md` vs `cases/C1.json`,
  `cases/C3.json`, `cases/C4.json`, `docs/cases/CASE_CATALOG.md`
- Finding: C1, C3, C4 already exist as `DISCOVERY` case files on this HEAD,
  but CE-C1/C3/C4 were still marked 待实例化.
- Repair: bind them in this commit. C1 is a clean cycle-with-residual witness
  (`r2.capacity=2`, transition `finish-j1-via-free-r2`). C4 is a clean AGV
  projection witness. C3 is a multi-capacity screening discovery case; it
  binds CE-C3 as an IMS capacity-vs-cycle witness, not as a Palmer 2/3-server
  WCC replica.
- Verdict: `REPAIR` (ledger metadata only)
- Touches frozen article-core? no

### A10. Open CE entries that still harden the theory

Still candidates after this audit:

| ID | Status on this HEAD | Role for T-ASE panel |
| --- | --- | --- |
| CE-CL1 | 待实例化 | set-valued closure vs deterministic `kappa` |
| CE-RSV1 | 待实例化 | soft reservation ≠ physical capacity |
| CE-INT1 | 待实例化 | intervention creates a new core |
| CE-BIXD2 | 待实例化 | optional drain is control, not structural repair |

Already instantiated, do not reopen:

| ID | Status |
| --- | --- |
| CE-SIP1 | Petri inverse-map boundary |
| CE-BIXD1 | `outside_bix1_sat` persistent-D boundary |
| CE-NB1 | concrete stopped-chain + `test_branching_closed_class_separates_s_reach_from_s_t` |
| CE-G6-BYPASS | machine regression + article bypass case |

- Verdict: `KEEP` the open four as Family H1 inputs
- Touches frozen article-core? no

### A11. G5 CRP failure is not a positive journal result

- Locator: `docs/theory/G5_BOUNDARY_FINDINGS.md` BF-G5-2;
  G6 Proposition 6.4; G5 row `G4_CRP_S4PR_AGREE`
- Claim as written: the frozen implementation-level bridge was falsified
  because a global extractor was used while an unrelated job remained.
- Hidden assumption: this does not refute Su et al. CRP in S4PR.
- Possible overclaim: “we disproved CRP” or “we now have a CRP theorem.”
- Repair: Prop 6.4 is the repaired *rule*. Paper A may cite the failure as
  motivation. A same-semantics CRP overlap case is optional Family H5, not
  required to keep Theorem 1.
- Verdict: `KEEP` as negative evidence; not a Paper A main theorem
- Touches frozen article-core? no

### A12. Article-core 5/6 cases reuse discovery bytes

- Locator: claim matrix F2; manuscript §8 limitation 1;
  `cases/article_core/article_scope_lock_v1.json`
- Finding: the scoped loop is constructively closed, not independently
  confirmed.
- Repair: none to v1. Any new panel must use a new scope id.
- Verdict: `KEEP`
- Touches frozen article-core? no

### A13. Frozen Hoeffding tolerance is loose

- Locator: article-core report; tolerance `0.028340`; observed max error
  `0.0030924479166667`
- Finding: v1 numbers are immutable. Reviewers may call the bound generous.
- Repair: new panel pre-registers a tolerance derived from its own `n` and
  simultaneous-test budget. Do not copy `0.028340`.
- Verdict: `TIGHTEN` for the next panel only
- Touches frozen article-core? no (do not rewrite v1)

### A14. Implementation–proof gap already admitted

- Locator: CORE P2c implementation paragraph; G6 A4
- Finding: closed-world completeness, hidden release, guards, and confluence
  remain human-audited except where a case supplies an explicit witness.
- Repair: any later iff must repeat this sentence. Do not hide it in an
  appendix footnote only.
- Verdict: `KEEP` as an explicit limitation
- Touches frozen article-core? no

## B. Manuscript sentence scan against C1–C9 / F1–F12

Source: `docs/paper/IMS_LOCAL_FIRST_HIT_THEORY_AND_CASES.md` at base HEAD.

| Section | Declarative result | Map | Action |
| --- | --- | --- | --- |
| Abstract | local blocking need not be a plant terminal SCC | C1 | keep |
| Abstract | two admission routes | C2, C3 | keep |
| Abstract | six-case constructive closure, not confirmation | C8, F2 | keep |
| Abstract | 18/18 within tolerance | C7 | keep; do not upgrade to external validation (F7) |
| §1 contribution list | four scoped contributions | C1–C4, C8 | keep |
| Theorem 1 | A2b sufficient noncompletion | C2 | keep; not necessity (F3) |
| Proposition 2 | finite-LTS admission | C3 | keep; not general (F4) |
| §3.4 | methods need not cover the same cases | C9 | keep |
| §4 | almost-sure absorption on certified `S_T` | C7 + CE-NB1 | keep |
| §5–6 numerical table | exact/DES cells | C6, C7 | keep |
| §6.3 tier | `tier_a_dual_route_closure` | C8, F1 | keep; original G6-B remains open |
| §8 limitations | 1–9 | F2, F7, F8, F9, F10, F11 | keep |

No manuscript sentence requires F1–F12 as a positive claim. No corrigendum
to the English draft is required before designing the T-ASE panel.

P0/P1 count for Paper A soundness: `0 / 0`.
Items that must be tightened in the next theory increment: A2, A5, A4, A13.

## C. What this audit authorizes

Authorized now:

- ledger status bindings for CE-C1, CE-C3, CE-C4
- theorem–case loop map
- novelty difference matrix
- T-ASE hardening spec/plan drafting

Not authorized:

- case JSON materialization
- CTMC / DES
- rewriting `evidence/article_core/minimal_closure_v1/`
- claiming G6-B PASS or T-ASE readiness
