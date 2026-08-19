# T-ASE Note to Practitioners — Outline and Draft Prose

Status: `P5 DRAFT PROSE / NOT IEEE BODY`
Venue: IEEE T-ASE
Evidence: P1 H4-v3; P2 H2-v2; P3 H3-v2; P4 locators; P2 leftover H5
  diagnostic. This file is still a process document. It is not the IEEE
  manuscript.

## Practitioner message (bullets)

1. A wait-for cycle on the shop graph is not by itself a stop. Residual
   capacity or an alternate unload can still finish the batch.
2. The object to compute is a *first hit* of a certified local or global
   blocked set, not a plant terminal SCC.
3. If a completion bypass exists, do not treat the local cycle as
   irreversible. Drain / cut the wrong edge can create a new kernel.
4. Diagnostic siphon language applies only when every core resource is
   unit, residual-zero, and one-hold-one-request. Otherwise refuse.
5. A one-slot AGV drain can move the plant from “already locally
   stopped” to “all jobs finish”. That is an intervention KPI, not a
   factory claim.
6. Exact CTMC and DES must share the same stopping hash. Agreement is
   numerical, not a proof of the plant.

Forbidden in any later IEEE prose: shop-floor data, G6-B passed, “first
certificate”, throughput improvement, H4-v2 as a deadlock demo.

## Draft prose (≈220 words; not title-page copy)

Flexible manufacturing cells routinely stop because a job holds one
resource and waits for another. Drawing a cycle on the wait graph is
not enough to declare that stop: leftover buffer slots or an alternate
unload can still finish the batch. This paper treats local blocking as
a *first hit* of a certified blocked set in a stopped process. Two
typed admission routes are used. On a request-closed subclass, a local
closed kernel is enough to prove that the blocked jobs cannot complete.
On a general finite model, the same local set is admitted only after a
complete state graph shows that batch completion is unreachable, and it
is refused when a completion bypass exists.

The diagnostic siphon language of Petri-net control applies only when
every core resource is unit capacity, residual-zero, and
one-hold-one-request. Outside that subclass the method must return a
typed refusal rather than a monitor. On a three-job machine–AGV island,
an optional one-slot AGV drain changes the plant from already locally
stopped to all jobs finishing. Exact continuous-time probabilities and
discrete-event replications share one stopping definition; numerical
agreement is a check, not a proof of the plant and not evidence from a
factory floor.

## Figure list (research chain)

| Fig | Content | Source |
| --- | --- | --- |
| F1 | Claim ladder: cycle → closed core → `D_local` / `D_global` / `F` | `TASE_CLAIM_LADDER.md` |
| F2 | H4-v3 island before/after optional AGV drain | `evidence/tase_hardening/v3/` |
| F3 | Exact vs DES six cells, Hoeffding band | v3 compatibility table |
| F4 | H2-v2 same-semantics table: siphon agree / typed refuse / C1 | `evidence/tase_hardening/h2_v2/` |
| F5 | H3-v2 `|X|` and runtime vs jobs × stages (log y) | `evidence/tase_hardening/h3_v2/` |
| F6 | Novelty five-axis, locator footnotes L29/L30/L31/B05 | P4 matrix |
| F7 | H5 four-field CRP diagnostic (fields 1–3 vs refused field 4) | `evidence/tase_hardening/h5/` |

Appendix: H1 four witnesses; H4-v1 refusal; H4-v2 θ=0 certified
all-completion; P3e/P5/P6 stay out.

## Page budget (T-ASE regular, ~12 pp without mandatory extras)

| Block | Pages |
| --- | --- |
| Abstract + Note to Practitioners | 0.7 |
| Introduction + related work (locator footnotes) | 2.0 |
| IMS-RAS and local-first-hit definitions | 2.0 |
| Theorems 1–2 / Prop 2, bypass refusal | 2.0 |
| H4-v3 island + exact/DES | 2.0 |
| H2-v2 baselines + H3-v2 scale + H5 diagnostic | 1.8 |
| Discussion / limitations / G5 FAIL retained | 1.0 |
| References | remainder |

IEEE body remains blocked (`G-IEEE-BODY`) until the user asks to start
the manuscript.
