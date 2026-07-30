# G3 Algorithm Audit

## Scope

This audit covers only the small finite-model verifier, the restricted
`IMS-SIP^1` state-induced wait-snapshot bridge, and the executable
`BIX1-SAT` and `BIX2-PERSIST` families. It does not close a plant-level
Petri/S3PR bridge, derive physical rates for C5, prove a general
persistent-buffer/AGV island threshold, freeze confirmation cases, or replace
the mathematical proofs in `docs/theory/CORE_THEOREMS_AND_PROOFS.md`.

## Implemented checks

| Obligation | Executable evidence | Scientific boundary |
| --- | --- | --- |
| stable semantics | deterministic bounded LTS, set-valued urgent closure, per-successor trace, capacity validation | state truncation is explicit and disables exact-supervisor claims |
| reachable certificate | all reachable stable states scanned; full-event shortest prefix; inclusion-minimal kernel and capacity witnesses | capacity-mediated closed-world transition registry only |
| structural baselines | raw simple cycle, capacity-aware state-dependent wait-graph knot, Banker snapshot, finite-LTS terminal SCC | each baseline has a separate assumption label; none substitutes for P2 |
| `IMS-SIP^1` bridge | immutable free-resource wait-snapshot net, evidence-fidelity validation, exact minimal-empty-siphon enumeration, explicit refusal status | diagnostic state dual only; not P1 reachability net, plant net, or general S3PR equivalence |
| BIX0 threshold | deterministic grid over `c_M,c_G,c_D=1..3`, `n_A,n_B=0..4` | candidate-state/no-successful-transfer family only; no reachability claim |
| BIX1-SAT threshold | exact stable-LTS BFS from empty holdings with explicit A/B start, completion, transfer, unload and drain events | family-specific reachable-existence threshold only; persistent-D and external drain are outside |
| BIX2-PERSIST threshold and repair | exact stable-LTS BFS from empty holdings; unit start/request/handoff; explicit post-handoff release; preregistered ring/DAG facet grid | exact only for the stated three-resource, single-current-hold family; not a general persistent-buffer or AGV theorem |
| exact supervisor | uncontrollable closure, marked coaccessibility, disabled state-event pairs, all initial closure outcomes | explicit finite full-observation LTS only |
| CTMC | committor, mean absorption time, fixed-partition sensitivity, residuals, positive-h Doob generator | explicit exponential/PH finite generator; provenance carried in output |
| independent sampling | SHA-256-derived replication streams, Gillespie paths, Wilson 95% interval, stream digest | vanilla estimator, not yet an IMS rare-event splitting theorem |
| public interface | `validate`, `prove`, `quantify`, `simulate`, `verify-case` with `ims-deadlock/cli/v1` JSON | unavailable inputs remain unavailable; no fabricated rates or siphons |

## Local validation, current integration

On 2026-07-30, the cache-disabled local coordination copy passed:

```text
family tests: 27 passed
pytest: 123 passed
ruff check: passed
ruff format --check: passed
strict mypy: passed
```

Independent specification and code-quality reviews also passed the adversarial
checks for:

1. a deadlock certificate reached only after non-zero transitions;
2. non-confluent urgent closure with distinct branch traces;
3. multiple uncontrollable initial closure outcomes, one unsafe;
4. omitted frontier arcs under `max_states`;
5. a three-event early-discovered path versus a two-event later-discovered
   path to the same certificate state;
6. a malformed certificate whose hold evidence disagrees with the model state;
7. attempted mutation of an already constructed wait-snapshot marking;
8. `BIX1-SAT` threshold-below modes, truncation, and persistent-D boundary
   classification;
9. `BIX2-PERSIST` exact-threshold, each one-below facet, asymmetric
   multi-capacity cases, empty initial holdings, deterministic shortest prefix,
   strict JSON schema, and truncation exclusion;
10. a DAG row that would otherwise report no deadlock but has no completion
    path;
11. an `invalid_instance` observation that would otherwise agree with a
    negative prediction.

## Remote authoritative validation

The 21-file BIX2/literature increment was packaged without caches,
environments, PDFs, credentials, or downloaded outputs. Its archive SHA-256
was:

```text
adb083aa78ad1098d8c6dd93807b4f1037f4b1e48992bc8bc8b51e4f4235fd80
```

The archive and explicit path-manifest hashes matched on Dell before
extraction. An isolated test tree was built from the locked Git `HEAD` and the
21-file overlay; `PYTHONPATH` was fixed to that tree's `src`. It passed before
the same explicit overlay was copied non-destructively into the clean
integration worktree. The qualified runtime was:

```text
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe
Python 3.13.9
```

Remote results:

```text
pytest: 123 passed
ruff check: passed
ruff format --check: passed
strict mypy: passed
CLI C0: exact_ims_sip1_wait_snapshot_duality, minimal empty siphon
BIX1-SAT test grid: 144 rows, 0 mismatches, 0 truncations
BIX2-PERSIST discovery grid: 32 rows, 0 mismatches, 0 truncations
BIX2 ring: 4 predicted positives, 4 observed positives
BIX2 DAG: 0 observed deadlocks, completion reachable in 16/16 rows
BIX2 state counts: min 14, max 452
BIX2 positive certificate resources: D, M, Q
C5 non-SIP1 refusal regression: passed without fabricated siphon
```

The smallest `1/1/1` positive certificate was reached after the deterministic
prefix `A1-start-M`, `A1-complete-request-D`, `B1-start-D`,
`B1-complete-request-Q`, `C1-start-Q`, `C1-complete-request-M`. Across the four
ring positives, every certificate used resources `{D,M,Q}` and the capacity
witness counts were `3,4,4,4`.

## Gate verdict

`G3 = PASS` on the locked Dell worktree for the explicitly implemented small
finite-model, `IMS-SIP^1`, `BIX1-SAT`, and `BIX2-PERSIST` scope. The verdict
does not close a plant-level Petri/S3PR bridge, physical rate derivation,
rare-event splitting, general C5/persistent-buffer/AGV threshold, confirmation
freeze, or paper claims.
