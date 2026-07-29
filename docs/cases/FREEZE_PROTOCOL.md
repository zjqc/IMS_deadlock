# Freeze Protocol

## Discovery-confirmation Separation

Discovery cases may change the theory. Confirmation cases may only test a
theory that has already passed the theory gate. A case cannot move from
discovery to confirmation unless its parameters are regenerated or withheld
from theorem construction.

## Freeze Requirements

Before running confirmation evaluation:

1. commit all theory, case, and code files;
2. generate deterministic JSON manifests for every model file;
3. record hashes for model files, theorem pages, and experiment scripts;
4. record the exact Python runtime and dependency lock;
5. record the full metric list and baseline list;
6. record all exclusion rules;
7. mark the freeze entry in `CONFIRMATION_PREREGISTRATION.md`.

## After Freeze

The project may not:

- delete failed cases;
- change metrics after seeing results;
- replace parameter ranges after seeing results;
- relabel discovery cases as confirmation evidence;
- change baseline implementations without a new freeze entry.

Allowed post-freeze actions:

- fix implementation bugs with a documented bug ledger entry;
- rerun all affected baselines and IMS methods;
- report both original and corrected results if the bug affected published
  conclusions.

## Stop Conditions

Stop extending cases and return to theory if:

- the claimed contribution is only an engineering combination of existing
  Petri-net, RAS, and CTMC tools;
- the general equivalence theorem is falsified and no meaningful restricted
  subclass has been stated;
- C5 requires ambiguous old-project details that cannot be independently
  reconstructed;
- exact enumeration contradicts a theorem and the contradiction is not a code
  bug.

