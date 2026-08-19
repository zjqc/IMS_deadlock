# H4-v3 Deadlock Island Design

Status: `P1 DESIGN / IMPLEMENT ON THIS WORKTREE`
Feeds: TA1, TA6
Does not overwrite: H4 v1, H4 v2 evidence

## Scientific target

One synthetic two-cell clothing of the already-proved local-first-hit
rule, such that a T-ASE reader can see:

- a local AGV–machine interlock
- another job that can still move (plant outgoing arc)
- an intervention that removes the interlock and drives selected-bad
  probability from 1 to 0

## Plants

Shared resources: `M1` (machine), `AGV` (agv), `M2` (machine), all
capacity 1. Jobs `A`, `B`, `C`.

### Base snapshot (`H4_v3_base`)

Holdings:

- `A` holds `M1`, requests `AGV`, mode `blocked_unload`
- `B` holds `AGV`, requests `M1`, mode `wait`
- `C` holds `M2`, mode `in_service` (service-complete enabled)

Enabled plant events: only `C-service-complete`. `A` and `B` have no
enabled transition. `{A,B}` is an inclusion-minimal local kernel.
`F` is unreachable. Admitted class: `D_local`. Plant outgoing arcs
exist because `C` can move. Time-zero selected-bad probability is 1.

### Intervention (`H4_v3_intervention`)

Same holdings and requests. Add one controllable `B-optional-drain`
that releases `AGV` and completes `B` without acquiring `M1`.

Then `{A,B}` is not a closed kernel (`B` has an enabled transition).
After `B` drains, `A` can take `AGV` and complete; `C` can complete.
Predicted: no admitted bad class at the snapshot; \(\theta_b=0\);
mean stopped time strictly positive.

This is a manufacturing-clothed CE-INT1 / optional-release, not a
relabel of H4 v2.

## Rates

Synthetic, documented: `service_complete` rate 2, every other
non-zero-time event rate 1. Not plant data.

## Protocol

- cases: `cases/discovery/tase_hardening_v1/h4_v3/`
- evidence: `evidence/tase_hardening/v3/`
- `n=65536`, seeds 2026081901 / 2026081902
- 32–48 workers, primary then repro
- v1 and v2 directories remain immutable

## Stop

If Barrier A reports `completed_job_holds_resource`, the builder is
wrong — fix the builder, do not relabel. If \(\theta_b=0\) on the
*base* plant, the island failed its P1 obligation; keep the run and
redesign as v4.
