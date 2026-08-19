# T-ASE Hardening Preregistration

Status: `PREREGISTRATION DRAFT / NO RESULTS`
Revision: `compute-parallel-v2`
Scope id: `tase_hardening_v1`
Spec: `docs/superpowers/specs/2026-08-19-tase-hardening-panel-design.md`

This file freezes *intent*. It does not freeze case bytes. Case hashes will
be filled only after authorized materialization, before any quantitative
run.

## Estimands

Used only by Family H4 if later authorized:

```text
theta_g = P(hit D_global before F)
theta_l = P(hit D_local before F)
theta_b = P(hit D_global union D_local before F)
mean_stopped_time = E[min(T_G, T_L, T_F)] on the certified domain
```

Classification precedence: `F` exclusion, then `D_global`, then `D_local`.
Unselected reachable closed classes refuse the row.

H1–H3 do not emit these probabilities. Mean stopped time is reported with
its own interval and is **not** in the simultaneous Hoeffding gate.

## Sample size and tolerance (H4 only)

Frozen design budget (authorization object must repeat these numbers):

```text
plants            = 2   (base, intervention)
n                 = 65536 replications / plant
k                 = 3   (theta_g, theta_l, theta_b) per plant
alpha             = 0.01 over the 6 probability cells
t_hoeffding       = sqrt( ln(2*6/alpha) / (2*n) )
                  = sqrt( ln(1200) / 131072 )
                  ≈ 0.00724
master_seed       = 2026081901
shard_size        = n / scientific_workers  (contiguous blocks)
```

Copying article-core `n=4096` or `tol=0.028340` is forbidden.

Master seed must not be `2026080601`.

## Parallel execution

H2: 32 plants (8 types × `{tight, one-below, balanced, loose}`).
H3: 576 rows, cap 100_000 states / 300 s.
Default scientific workers: 32 (max 48) after a live CPU/RAM probe.
Primary wave fully completes before any repro shard starts.

## Baselines (H2)

Truth: complete finite LTS reachability of `D_global` / `D_local` / `F`,
or typed refusal.

Comparators: cycle/SCC, closed core, `IMS-SIP^1` siphon-or-refuse.

## Exclusions

- article-core v1 cases
- G4/G5 confirmation rows
- G6-R historical replay rows
- H5 CRP unless a spec amendment is approved
- any KPI not named above

## Failure handling

Retain every refusal, timeout, truncation, and negative H1 witness.
No substitution after outcomes.
