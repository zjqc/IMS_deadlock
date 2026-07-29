# Methodology Blueprint

## Research Design

This project uses formal methods and computational falsification. It has no
human subjects and no IRB component.

## Core Method

1. Define finite-batch `IMS-RAS` operational semantics:
   resources, capacities, routes, hold-request-release relations,
   blocked-unload BAS, finite buffers, AGV occupancy, reservations, and
   zero-time event closure.
2. Construct a finite transition system and, where valid, a bounded Petri net.
3. Define operational deadlock, local deadlock, quasi-deadlock, structural
   deadlock, probabilistic deadlock, completion, and nonblocking without
   overloading terms.
4. Prove the theorem ladder:
   semantic equivalence, knot certificate, siphon/RAS bridge under restrictions,
   structural thresholds, absorbing CTMC equations, and control/intervention
   theorems.
5. Attack every theorem with minimal counterexamples before case freezing.
6. Use exhaustive enumeration to test proof obligations, not to replace proof.

## Case Discipline

Discovery cases `C0`-`C5` may change definitions and assumptions, but every
change must enter `docs/literature/FAILURE_LEDGER.md` or the later case ledger.

Frozen confirmation cases cannot be changed after preregistration. Metrics,
baselines, and parameter ranges are fixed before evaluation.

## Baselines

- simple directed cycle detection;
- knot / terminal SCC detection;
- Banker-style safety sequence;
- siphon-control baseline where Petri assumptions hold;
- exact maximum-permissive finite supervisor;
- original "delete backflow route" repair from the source manufacturing-island
  project, with provenance documented.

## Output Contract

Every theorem page should eventually have:

- assumption table;
- statement;
- proof obligations;
- proof sketch;
- counterexamples and non-applicability cases;
- machine enumeration checklist;
- migration cards linking back to `docs/literature/MIGRATION_CARDS.md`.
