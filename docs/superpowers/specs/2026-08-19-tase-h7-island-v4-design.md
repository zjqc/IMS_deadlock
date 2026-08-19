# T-ASE H7 — Positive-Time Local-Hit Island v4 Design

Status: `DESIGN / IMPLEMENT ON JOURNAL-HARDENING WORKTREE`
Date: 2026-08-19
Worktree: `D:\worktree\IMS_deadlock-journal-hardening-v1`
Branch: `codex/journal-hardening-v1`
Feeds: G-H7, manufacturing-island figure, H8 plant hash
Does not overwrite: H4 v1 / v2 / v3 cases or
`evidence/tase_hardening/v1|v2|v3/`

H4-v3 remains the *time-zero* local-hit witness: at \(t=0\) the plant
is already in \(D^{\mathrm{L}}\), \(\theta^{\mathrm{L}}=1\), \(m=0\).
That clothing is scientifically correct and frozen. H7 is a *new*
island whose first local hit is a stopping *event*, not the initial
condition.

## 0. Scientific obligation

On the *base* plant all of the following must hold.

1. Barrier \(\mathbf{B}\) certified (no `completed_job_holds_resource`,
   LTS finite, partition defined).
2. Initial state \(x_0\notin D^{\mathrm{G}}\cup D^{\mathrm{L}}\cup F\).
3. Admitted \(D^{\mathrm{L}}\) is nonempty, and at least one admitted
   local-hit state has a plant outgoing arc (a third job can still move).
4. From \(x_0\): \(\theta^{\mathrm{L}}(x_0)>0\) and exact mean stopped
   time \(m\ge 0.25\) under the declared rates. If the floor cannot be
   met without violating 1–3, write a typed refusal and redesign as
   v4b; do not lower the floor silently.
5. One *predeclared* intervention changes \(\theta^{\mathrm{B}}\) or
   \(m\) by more than the Hoeffding band
   \(\varepsilon=\sqrt{\log(2K/\alpha)/(2n)}\) with \(n=65536\),
   \(K=6\), \(\alpha=0.01\) (same formula as H4-v3,
   \(\varepsilon\approx 0.00735\)).
6. Exact CTMC and DES share one stopping-hash family; primary seed
   `2026081901`, repro seed `2026081902`; 32–48 workers; BLAS threads
   \(=1\); one reducer. Serial H7 DES is a protocol miss.

Selected-bad class is \(A^\dagger=D^{\mathrm{G}}\cup D^{\mathrm{L}}\)
as in the paper. \(\theta^{\mathrm{B}}=\mathbb{P}(\tau^\dagger<\infty)\)
on the stopped process; \(\theta^{\mathrm{L}}\) is the probability that
the first hit is in \(D^{\mathrm{L}}\); \(m=\mathbb{E}[\tau^\dagger]\)
with the usual convention that the stopped clock is used.

## 1. Why a new island, and what was learned from H4

| Clothing | Initial | \(\theta^{\mathrm{L}}\) | \(m\) | Role after H7 |
| --- | --- | --- | --- | --- |
| H4-v2 | idle, two-cell chain | 0 | \(>0\) | negative: all-completion, not a deadlock demo |
| H4-v3 | already in \(\{A,B\}\) interlock, C in service | 1 | 0 | time-zero *boundary* example |
| H7-v4 | A,B idle; C already in service with remaining work | \(\in(0,1]\) | \(\ge 0.25\) | *lead* manufacturing figure |

Design constraint, copied from the height-plus-one plan: **do not
start in the interlock.** Start with at least one job still moving
*into* the contested pair, so the first hit is an event.

## 2. Plants

Shared resources of the *base* plant:

| Id | Kind | Capacity |
| --- | --- | --- |
| M1 | machine | 1 |
| M2 | machine | 1 |
| V | agv | 1 |

Jobs: \(\mathsf{A},\mathsf{B},\mathsf{C}\) (manuscript letters
\(\mathsf{A},\mathsf{B},\mathsf{C}\); code ids `A`, `B`, `C`).

Manufacturing reading (same island story as H4-v3, earlier in time):

- Cell 1: job \(\mathsf{A}\) is about to take M1 and will then need
  the AGV to unload.
- Inbound: job \(\mathsf{B}\) is about to take the AGV and will then
  need M1.
- Cell 2: job \(\mathsf{C}\) is already in service on M2 and has
  *two* remaining uncontrollable service stages, so it is still a
  moving plant witness when \(\{\mathsf{A},\mathsf{B}\}\) close.

### 2.1 Base snapshot (`H7_v4_base`)

Initial state \(x_0\):

| Job | Holds | Requests | Mode |
| --- | --- | --- | --- |
| A | — | — | `idle` |
| B | — | — | `idle` |
| C | M2 | — | `in_service_1` |

`stable=True`, `complete=False`, calendar empty.

Registry (all non-zero-time; release-then-complete; no completed job
holds a resource):

| Name | Kind | Job | Source \(\to\) target | Ctrl | Acquire | Release | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `A-start-m1` | START | A | idle \(\to\) in_service | yes | M1 | — | next request V |
| `A-service-complete` | SERVICE_COMPLETE | A | in_service \(\to\) blocked_unload | no | — | — | request V already set |
| `A-unload-v` | UNLOAD | A | blocked_unload \(\to\) on_v | yes | V | M1 | clears requests |
| `A-complete-release-v` | RELEASE | A | on_v \(\to\) completed | no | — | V | `mark_complete` |
| `B-start-v` | START | B | idle \(\to\) wait | yes | V | — | next request M1 |
| `B-enter-m1` | DISPATCH | B | wait \(\to\) on_m1 | yes | M1 | V | clears |
| `B-complete-release-m1` | RELEASE | B | on_m1 \(\to\) completed | no | — | M1 | `mark_complete` |
| `C-service-1` | SERVICE_COMPLETE | C | in_service_1 \(\to\) in_service_2 | no | — | — | still holds M2 |
| `C-service-2` | SERVICE_COMPLETE | C | in_service_2 \(\to\) blocked_unload | no | — | — | still holds M2 |
| `C-release-m2` | RELEASE | C | blocked_unload \(\to\) completed | yes | — | M2 | `mark_complete`; `clears_requests` |

The local-hit state \(x^\mathrm{L}\) that the island is built to
*reach* (not start in) is

```text
A holds M1, requests V, mode blocked_unload
B holds V,  requests M1, mode wait
C holds M2, mode in_service_1 or in_service_2 or blocked_unload
```

At every such state \(\{\mathsf{A},\mathsf{B}\}\) is an
inclusion-minimal closed kernel and C still has a plant outgoing arc
unless C has already completed. States where C has already completed
and \(\{\mathsf{A},\mathsf{B}\}\) are interlocked belong to
\(D^{\mathrm{G}}\), not \(D^{\mathrm{L}}\). Both classes may be
nonempty; the gate requires \(D^{\mathrm{L}}\neq\emptyset\).

\(F\) is the unique all-complete state.

### 2.2 Intervention (`H7_v4_intervention`)

**Primary, predeclared:** same holdings, same registry, same initial
modes; resource V has capacity **2** (one extra AGV slot).

Prediction: the pair \(\{\mathsf{A},\mathsf{B}\}\) is no longer a
closed kernel, because `A-unload-v` is enabled whenever A is in
`blocked_unload` (a free V unit remains even if B holds one).
Therefore admitted \(D^{\mathrm{L}}\) on \(\{M1,V\}\) vanishes.
\(\theta^{\mathrm{B}}\) must drop by more than \(\varepsilon\), or
\(m\) must rise by more than \(\varepsilon\) if some other selected-bad
class remains. The designed reading is
\(\theta^{\mathrm{B}}_{\mathrm{base}}>\theta^{\mathrm{B}}_{\mathrm{int}}+\varepsilon\).

**Fallback, also predeclared, used only if the primary fails the
Hoeffding delta after a recorded attempt:** add
`B-optional-drain` exactly as in H4-v3 (B releases V and completes
without taking M1). The failed primary clothing is retained under
`cases/discovery/tase_hardening_v1/h7/failed/`. The fallback is
H7-v4b, not an overwrite of v4.

### 2.3 Rates

Synthetic, documented, not plant data:

| Event class | Rate |
| --- | --- |
| `A-start-m1`, `B-start-v` | \(1\) |
| `A-service-complete` | \(2\) |
| `C-service-1`, `C-service-2` | \(1/2\) |
| every other non-zero-time event | \(1\) |

C’s remaining work is slower than A’s service so that, on paths that
close the interlock, C is typically still moving. If exact \(m<0.25\)
under these rates, first multiply every rate by \(1/2\) (time unit
rescaling raises \(m\) without changing \(\theta\)). If \(m\) is still
below the floor, that is a topology failure — redesign, do not report
a rescaled number as if it were the original rates.

## 3. Theory that must be written (instance lemmas, not a new theorem)

H7 does **not** add a Theorem 13. Theorems 3–5 of the manuscript
apply if A2b holds; otherwise Theorem 4 (complete-LTS fallback) is
the admission route and the report must say so.

### Lemma H7.1 (initial is transient)

At \(x_0\) the enabled set contains
`{A-start-m1, B-start-v, C-service-1}`. Hence \(x_0\) is not
complete, not a global deadlock, and not a local closed kernel
(A and B hold nothing). Therefore
\(x_0\notin D^{\mathrm{G}}\cup D^{\mathrm{L}}\cup F\).

*Proof.* A global deadlock requires every unfinished job blocked and
no enabled plant transition. Three events are enabled, contradiction.
A local certificate requires a nonempty inclusion-minimal closed
kernel. The unfinished jobs that hold resources are \(\{\mathsf{C}\}\);
C has an enabled transition, so no kernel exists. \(F\) requires
`complete=True`. \(\square\)

### Lemma H7.2 (a local-hit state is reachable and has a plant outgoing)

The finite word

```text
A-start-m1, A-service-complete, B-start-v
```

is enabled from \(x_0\) (C has not yet moved). The resulting state
\(x^\mathrm{L}\) has

- A holding M1 requesting V,
- B holding V requesting M1,
- C holding M2 in `in_service_1`,

so `C-service-1` is enabled. The pair \(\{\mathsf{A},\mathsf{B}\}\) is
a unit-capacity one-hold-one-request cycle with residual 0 on
\(\{M1,V\}\). By Theorem 2 (IMS-SIP\(^1\) dual) and Theorem 3 (A2b
covering-core, or Theorem 4 if A2b is declined), \(x^\mathrm{L}\) is
an admitted local-hit state, and it has a plant outgoing arc.

*Proof of enabledness.* At \(x_0\), M1 and V are free, so both starts
are enabled; they commute with each other and with C’s service. After
`A-start-m1`, A holds M1 and requests V; `A-service-complete` is
uncontrollable and does not change holds; after it A is in
`blocked_unload` still holding M1. `B-start-v` acquires the still-free
V. Residual of M1 and V is then 0. C still holds M2 in `in_service_1`,
so `C-service-1` is enabled. \(\square\)

### Lemma H7.3 (\(\theta^{\mathrm{L}}(x_0)>0\) and \(m>0\))

The stopped process is the finite absorbing CTMC of Lemma 1 / Theorem 6
on the certified partition. The path of Lemma H7.2 has positive
probability (every rate is positive and finite) and hits
\(D^{\mathrm{L}}\) in three events. Therefore
\(\theta^{\mathrm{L}}(x_0)>0\). The same path has positive duration,
and every other path to \(A^\dagger\cup F\) has nonnegative duration,
so \(m=\mathbb{E}[\tau^\dagger]>0\).

The numerical floor \(m\ge 0.25\) is *not* a theorem; it is a design
gate checked by the exact solver. Lemma H7.3 only gives \(m>0\).

### Lemma H7.4 (primary intervention destroys the \(\{M1,V\}\) kernel)

On the capacity-2 plant, if B holds one unit of V and A requests V,
residual\( (V)\ge 1\), so `A-unload-v` is enabled. Hence
\(\{\mathsf{A},\mathsf{B}\}\) is not request-closed. No other pair
among \(\{\mathsf{A},\mathsf{B},\mathsf{C}\}\) is a unit circular wait
on a residual-zero set (C never requests M1 or V). Therefore every
previously admitted \(D^{\mathrm{L}}\) state of the base plant is
absent from the intervention plant. \(\theta^{\mathrm{L}}_{\mathrm{int}}=0\).
Whether \(\theta^{\mathrm{B}}_{\mathrm{int}}=0\) depends on whether
\(D^{\mathrm{G}}\) is also empty; the gate requires only that
\(\lvert\theta^{\mathrm{B}}_{\mathrm{base}}-\theta^{\mathrm{B}}_{\mathrm{int}}\rvert>\varepsilon\)
or \(\lvert m_{\mathrm{base}}-m_{\mathrm{int}}\rvert>\varepsilon\).

### Lemma H7.5 (no new general theorem)

If the partitioner admits the local family by A2b, cite Theorem 3.
If A2b fails (for example because a next-request is recorded as OR),
cite Theorem 4 and record `admission_route = lts_fallback`. Do not
invent a weaker island-specific iff.

## 4. Protocol and compute

- Cases: `cases/discovery/tase_hardening_v1/h7/`
  (`H7_v4_base.json`, `H7_v4_intervention.json`; failed clothings
  under `h7/failed/`)
- Evidence: `evidence/tase_hardening/h7_island_v4/`
  (write-once; `tase_hardening_h7_report.json`)
- Module: `src/ims_deadlock/tase_height.py`
- CLI: `tase_hardening_run.py --h7`
- `n=65536`, seeds `2026081901` / `2026081902`
- Workers: `plan_workers` on a live probe; 48 if free RAM \(\ge 64\) GiB
  and logical CPUs \(\ge 56\)
- `pin_blas_thread_env` when workers \(\ge 8\)
- Exact CTMC via existing `AbsorbingCTMC` / `partition_stable_lts`
- DES shards via process pool, same stopping labels as exact
- Compatibility: 6/6 cells inside Hoeffding, or a typed DES refusal
- Quantitative authorization: reuse the already-approved T6 file
  `cases/discovery/tase_hardening_v1/quantitative_authorization.json`
  at SHA-256
  `090c75516fbbde24dcc4cde03b0d24aa633955f1ce9b97cc4c49b229f7b193c9`.
  This spec *names* that hash; it does not rewrite the file.

Barrier A/B checks (same as H4-v3):

- no `completed_job_holds_resource`
- LTS not truncated under `max_states=4096`
- partition defined
- initial class recorded

## 5. Tests (must fail before the builder exists)

1. Base initial is not in \(\{D^{\mathrm{G}}, D^{\mathrm{L}}, F\}\).
2. Base admitted \(D^{\mathrm{L}}\) is nonempty and at least one such
   state has a plant outgoing arc.
3. The word of Lemma H7.2 is enabled and lands in \(D^{\mathrm{L}}\).
4. Barrier A does not report `completed_job_holds_resource`.
5. Exact \(\theta^{\mathrm{L}}_{\mathrm{base}}>0\).
6. Exact \(m_{\mathrm{base}}\ge 0.25\).
7. Intervention changes \(\theta^{\mathrm{B}}\) or \(m\) by more than
   \(\varepsilon\).
8. H4-v3 builders and evidence paths are untouched.
9. Model ids are `h7-island-v4-base` / `h7-island-v4-intervention`,
   never `h4-island-v3-*`.

A fast unit subset (1–4, 8–9) runs without the DES wave. Tests 5–7
may use the exact CTMC only; the DES wave is a CLI obligation, not a
unit-test obligation.

## 6. Iteration protocol (case \(\leftrightarrow\) theory)

| Observation | Action |
| --- | --- |
| Barrier A = `completed_job_holds_resource` | fix the builder (release-then-complete). Keep the failed run. |
| \(x_0\in D^{\mathrm{L}}\) | the island collapsed to H4-v3; redesign initial. Do not relabel. |
| \(D^{\mathrm{L}}=\emptyset\) but \(D^{\mathrm{G}}\neq\emptyset\) | C finishes too fast or the third job is missing; lengthen C or start C later in its remaining work. |
| \(\theta^{\mathrm{L}}=0\) | the interlock is unreachable; restore the word of Lemma H7.2. |
| \(0<m<0.25\) | rescale rates by \(1/2\) once; if still below, redesign topology as v4b. |
| Intervention delta \(\le\varepsilon\) | switch to the predeclared fallback (extra drain) as v4b; retain v4 primary as a failed clothing. |
| A2b fails | use Theorem 4; do not weaken Theorem 3. |
| DES 6/6 fails | typed DES refusal; do not silently drop a cell. |

Every failed clothing stays on disk. Theory text is amended only when
a lemma’s *hypothesis* is shown false (for example, if the word of
Lemma H7.2 is not enabled because `next_requests` is recorded
differently). Predictions (\(\theta^{\mathrm{L}}>0\), \(m\ge 0.25\),
intervention delta) are gates, not theorems, except where a lemma
already proves the qualitative part.

## 7. Forbidden

- Overwriting H4-v3 cases or `evidence/tase_hardening/v3/`.
- Calling v4 shop-floor or a digital twin of a named factory.
- Calling H4-v2 a deadlock demonstration.
- Starting in the interlock and claiming “positive-time hit.”
- Serial DES.
- Inventing a new general iff.

## 8. Manuscript delta (after G-H7)

H7 becomes the lead island figure. H4-v3 becomes the “already-hit
boundary” example. Abstract: one clause on the positive-time hit.
NtP: “the cell runs and then locally stops; a one-slot change
prevents that stop.”

## 9. Gate G-H7

Pass iff the v4 report records:

1. Barrier B certified on base and intervention.
2. Initial not absorbing.
3. \(D^{\mathrm{L}}\neq\emptyset\) with a plant outgoing.
4. Exact \(\theta^{\mathrm{L}}>0\) and \(m\ge 0.25\) on the base.
5. Intervention delta \(>\varepsilon\) on \(\theta^{\mathrm{B}}\) or \(m\).
6. Exact/DES 6/6 compatible or a typed DES refusal (exact still stands).

Fail action: keep H4-v3 as the main island; do not call height +1
done.

## 10. Plant hash (input to H8)

After a passing G-H7, write

```text
h7_base_plant_sha256
h7_intervention_plant_sha256
h7_stopping_hash
```

into `evidence/tase_hardening/h7_island_v4/plant_identity.json`.
H8 may start only after those three hashes exist. If G-H7 fails, H8
falls back to the frozen H4-v3 plant and the report must say
`h8_plant = h4_v3_fallback`.
