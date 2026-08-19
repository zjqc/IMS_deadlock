# T-ASE Hardening Preregistration

Status: `PREREGISTRATION DRAFT / NO RESULTS`
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

H1–H3 do not emit these probabilities.

## Sample size and tolerance (H4 only)

To be computed at authorization time from:

- number of H4 quantitative cells `k` (expected 3 component probabilities
  plus mean time, or a declared subset)
- replications `n`
- simultaneous failure probability `alpha`

The bound must be written into the authorization object. Copying
article-core `n=4096` or `tol=0.028340` is not allowed without recomputing
the budget.

Master seed must not be `2026080601`.

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
