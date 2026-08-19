# T-ASE H8 — Finite-State Supervisor Baseline Design

Status: `DESIGN / BINDS AFTER H7 PLANT HASH`
Date: 2026-08-19
Worktree: `D:\worktree\IMS_deadlock-journal-hardening-v1`
Branch: `codex/journal-hardening-v1`
Feeds: G-H8
Depends: `evidence/tase_hardening/h7_island_v4/plant_identity.json`
  or documented fallback to frozen H4-v3
Does not overwrite: H4/H6/H7 evidence roots

This package is a **baseline**, not a new theorem. It cites
Ramadge–Wonham nonblocking synthesis on an explicit finite graph
(Ramadge–Wonham, *SIAM J. Control Optim.* / standard Th. 7.1 /
Prop. 7.1) and, equivalently, the boundary-unsafe LES shape of
Nazeem–Reveliotis, T-ASE 2011. Compact-input NP-hardness and MCPP
maximally-permissive existence are out of scope.

## 0. Scientific obligation

On the H7 *base* plant (or on H4-v3 if H7 is refused), compute the
greatest nonblocking supervisor of the explicit stable LTS, treating

\[
A^\dagger = D^{\mathrm{G}}\cup D^{\mathrm{L}}
\]

as forbidden, \(F\) as marked, and the `controllable` flag of each
`TransitionSpec` as the controllability partition. Report four numbers
on *one* semantics:

| Quantity | Meaning |
| --- | --- |
| \(\lvert X\rvert\) | plant stable states |
| \(\lvert X_{\mathrm{safe}}\rvert\) | states retained by the supervisor |
| disabled controllable events | count of cut *state-event* pairs |
| \(\theta^{\mathrm{B}},m\) under the supervisor | first-hit KPIs on the supervised stopped graph |

Reuse `exact_max_nonblocking_supervisor` in `engine.py`. Do not
reimplement the fixed point.

## 1. Binding

After G-H7 passes, copy

```text
h7_base_plant_sha256
h7_stopping_hash
```

into this spec’s evidence as `h8_plant_sha256` / `h8_stopping_hash`.
If G-H7 failed, set `h8_plant = h4_v3_fallback` and hash the frozen
H4-v3 base plant; the report must say the fallback is a weaker
baseline (time-zero local hit).

H8 implementation **must not start** until one of those two identities
is on disk. This spec may be committed before that fill-in; the
fill-in is a required evidence field, not a deferred hole in the
theory.

## 2. What is computed

1. Enumerate the stable LTS of the bound plant.
2. Partition with `partition_stable_lts` (same family as H7).
3. Build a `FiniteLTS` whose forbidden states are the partition’s
   \(D^{\mathrm{G}}\cup D^{\mathrm{L}}\) and whose marked states are
   \(F\).
4. Call `exact_max_nonblocking_supervisor`.
5. Record `safe_states`, `disabled_state_events`,
   `initial_state_feasible`.
6. If the initial state is not feasible, the supervisor is a *refusal
   of the plant as specified* (the plant cannot be made nonblocking
   from \(x_0\) by disabling only controllable events). That is a
   valid baseline outcome; report it as
   `supervisor_initial_infeasible` and skip supervised KPIs.
7. If feasible, delete the disabled controllable arcs, re-partition
   the supervised graph with the *same* stopping hash family, and
   compute exact \(\theta^{\mathrm{B}},m\). DES on the supervised
   graph is optional; exact is required.

## 3. Theory (citation, not a new proof)

Quote Ramadge–Wonham: the supremal nonblocking controllable sublanguage
of a regular language exists and is regular; on a finite explicit
graph it is the greatest fixed point of “remove states that can
uncontrollably leave the remaining set or cannot reach a marked
state.” The implementation is that fixed point. Record:

- synthesis is polynomial in \(\lvert X\rvert\);
- the compact (unexpanded) input problem remains at least NP-hard;
- this is not a risk-budget supervisor;
- this is not maximally permissive in the MCPP monitor sense;
- this is not Paper C.

Do not add a Theorem 13 that restates Theorem 3.

## 4. Roots and tests

- Cases: `cases/discovery/tase_hardening_v1/h8/`
- Evidence: `evidence/tase_hardening/h8_supervisor/`
- CLI: `tase_hardening_run.py --h8`
- Tests:
  1. Supervisor is computed on the bound plant hash, not a silent
     rebuild of a different plant.
  2. Forbidden set equals \(D^{\mathrm{G}}\cup D^{\mathrm{L}}\) of
     that partition.
  3. `disabled_state_events` contains only controllable events.
  4. If initial is feasible, supervised \(\theta^{\mathrm{B}}\le\)
     plant \(\theta^{\mathrm{B}}\) (disabling arcs cannot raise the
     first-hit probability of a previously absorbing class; if the
     numbers violate this, the stopping labels drifted — fail the
     run).
  5. No write into H7/H4 evidence roots.

## 5. Gate G-H8

Pass iff the supervisor table and the H7 (or fallback) table share
the same plant identity and the same stopping-hash family, and the
four numbers (or the typed `supervisor_initial_infeasible`) are in
the evidence root.

Fail action: omit the supervisor subsection; height +1 is incomplete.

## 6. Forbidden

- Claiming a new nonblocking theorem.
- Claiming maximal permissiveness.
- Running H8 on a plant that is not the bound hash.
- Shop-floor or throughput claims.
