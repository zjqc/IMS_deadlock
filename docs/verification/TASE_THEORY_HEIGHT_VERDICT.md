# T-ASE Theory-Height Verdict

Status: `ANALYSIS / NOT A CLAIM UPGRADE`
Date: 2026-08-19
Worktree HEAD: `2c59f87`
Venue: IEEE T-ASE Regular Paper only

Question answered: is the *theoretical height* enough to submit to T-ASE?
This is not the same question as “is the manuscript file complete” or
“will the paper be accepted.”

## Verdict in one sentence

The theory is **high enough for a scoped T-ASE methods/analysis Regular
Paper**, and **not high enough** if the paper is sold as a 2026
plant-net liveness theorem, a CRP competitor, or a general DES result.

## What “height” means here

Four independent axes, scored only against T-ASE (not Automatica/TAC):

| Axis | Score | Meaning |
| --- | --- | --- |
| Internal soundness on the declared subclass | high | Theorems 1–8 have complete proofs; no P0 hole in A2b or P2 |
| Generality | medium-low | \(\mathrm{IMS}^{CW}\); A2b is sufficient not necessary; LTS route is model-specific and exponential |
| Novelty of the *object* | medium | typed first-hit set \(D^{\mathrm{L}}\) is not in L29/L31/B05; the linear algebra is classical |
| Manufacturing theorem (island) | instance-level | H4-v3 clothes Theorem 3; it is not a new island-dynamics theorem |

T-ASE publishes foundational *automation methods* with a practitioner
Note, method comparison, and recent archival citations. It does not
require an Automatica-grade existence theorem. It does require that the
claimed increment be sharper than a restatement of siphon/CRP/knot
results already in this Transactions and Automatica 2025–2026.

## Where the theory sits relative to 2026 neighbours

| Neighbour | Their theorem | Ours relative to them |
| --- | --- | --- |
| L31 Su et al., *this* T-ASE, 2026 | CRP iff partial deadlock on S4PR, then SBA | different object; no embedding ⇒ we **cannot** claim to match or beat it (H5 agreement = 0) |
| L29 Lu et al., Automatica 2026 | MR2G / PDDP iff partial-deadlock marking | they have a plant-net iff; we have operational IMS + bypass refusal + first-hit probability |
| B05 Chen–Li, Automatica 2011 | maximally permissive monitors / MCPP | they synthesize supervisors; we do not |
| L08 Lawley–Reveliotis | SU-SAFE NP-c; knot subclasses | we keep cycle/SCC as a *screen*, not a theorem |
| L16 Narahari et al. | absorbing Markov deadlock metrics | we reuse the linear algebra on a *certified* \(S^{\circ}\); that certification is the increment, not a new CTMC theorem |

Honest positioning sentence:

```text
The height is operational-semantics and verification,
not a stronger structural iff than CRP/PDDP,
and not a supervisor-synthesis theorem.
```

If an AE reads the paper as “another deadlock detector for FMS Petri
nets,” the height is insufficient and the paper looks incremental.
If the AE reads it as “a typed first-hit semantics for finite IMS cells
with AGV/BAS, with proofs and a same-target exact/DES check,” the
height is in the T-ASE band.

## What is actually proved (no upgrade)

- Theorem 1: covering closed core \(\Leftrightarrow\) capacity-mediated
  *global* operational deadlock, **relative to the declared registry**.
- Theorem 2: empty-siphon dual, **only** on IMS-SIP\(^1\).
- Theorem 3: under A2b, a local core makes kernel jobs incompletable,
  hence \(F\) unreachable. Sufficient, not necessary.
- Theorems 4–5: complete finite-LTS admission and bypass refusal.
  Sound for one enumerated model, not a general structural theorem.
- Theorem 6: chain-decomposable acquisition order is a *sufficient*
  deadlock-free test, not a manufacturing policy.
- Theorem 7: classical absorbing-chain equations on a certified domain.
- Theorems 9–11: exact thresholds on two synthetic families, not a
  general finite-capacity iff.

The manufacturing-island result is a **corollary clothing** of Theorem 3:
time-zero \(D^{\mathrm{L}}\) with a still-moving third job, and an AGV
drain that changes the absorbing class. That is the right T-ASE *example*.
It does not raise the theorem’s generality.

## What would make the height *not* enough

These are the real theory-height risks, not packaging:

1. Selling Theorem 3 as necessary, or Theorem 4 as a general structural
   theorem.
2. Selling Theorem 2 as siphon control or S3PR equivalence.
3. Selling Theorem 7 as new CTMC mathematics.
4. Selling H4-v3 as a plant-scale deadlock-avoidance law. It is a
   three-job, already-hit digital twin.
5. Claiming a CRP overlap after H5 field 4 was refused.
6. Omitting that P2/Theorem 1 is registry-relative.

Any of (1)–(5) would place the paper below T-ASE’s comparison bar
against L31, not above it.

## What would raise height (optional, not a submit gate)

- An independently hashed S4PR embedding so Proposition 4 field 4 can
  be true or honestly false on a published net.
- An island whose first local hit occurs at positive time (so \(m>0\)
  on the base).
- A finite-state supervisor baseline in the Ramadge–Wonham / LES sense,
  clearly labelled as baseline not as Paper C.

None of these is required to *have* T-ASE-height theory. They reduce
AE “incremental / toy” risk.

## Bottom line

| Question | Answer |
| --- | --- |
| Are the proofs complete on the declared subclass? | Yes |
| Is that subclass the right size for T-ASE? | Yes, if advertised as operational IMS |
| Is it the right size for Automatica/TAC? | No |
| Is the increment theoretically sharper than L31 on S4PR? | No, and it must not be claimed |
| Is the increment theoretically real on IMS+AGV+BAS first-hit? | Yes |
| Enough to *submit a scoped Regular Paper*? | Theory: yes, with the positioning above. File: not until IEEE two-column. Acceptance: not guaranteed; AE risk is “toy island + incremental vs CRP.” |
| Enough to claim “theory height already matches flagship T-ASE 2026 Petri papers”? | No |

G5 FAIL and G6-B `OPEN_PENDING` do not lower Theorem 3. They forbid
writing that a prior overlap gate passed.
