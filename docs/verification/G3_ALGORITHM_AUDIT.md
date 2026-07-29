# G3 Algorithm Audit

## Scope

This audit covers only the small finite-model verifier, the restricted
`IMS-SIP^1` state-induced wait-snapshot bridge, and the executable
`BIX1-SAT` family. It does not close a plant-level Petri/S3PR bridge, derive
physical rates for C5, prove a general persistent-buffer island threshold,
freeze confirmation cases, or replace the mathematical proofs in
`docs/theory/CORE_THEOREMS_AND_PROOFS.md`.

## Implemented checks

| Obligation | Executable evidence | Scientific boundary |
| --- | --- | --- |
| stable semantics | deterministic bounded LTS, set-valued urgent closure, per-successor trace, capacity validation | state truncation is explicit and disables exact-supervisor claims |
| reachable certificate | all reachable stable states scanned; full-event shortest prefix; inclusion-minimal kernel and capacity witnesses | capacity-mediated closed-world transition registry only |
| structural baselines | raw simple cycle, capacity-aware state-dependent wait-graph knot, Banker snapshot, finite-LTS terminal SCC | each baseline has a separate assumption label; none substitutes for P2 |
| `IMS-SIP^1` bridge | immutable free-resource wait-snapshot net, evidence-fidelity validation, exact minimal-empty-siphon enumeration, explicit refusal status | diagnostic state dual only; not P1 reachability net, plant net, or general S3PR equivalence |
| BIX0 threshold | deterministic grid over `c_M,c_G,c_D=1..3`, `n_A,n_B=0..4` | candidate-state/no-successful-transfer family only; no reachability claim |
| BIX1-SAT threshold | exact stable-LTS BFS from empty holdings with explicit A/B start, completion, transfer, unload and drain events | family-specific reachable-existence threshold only; persistent-D and external drain are outside |
| exact supervisor | uncontrollable closure, marked coaccessibility, disabled state-event pairs, all initial closure outcomes | explicit finite full-observation LTS only |
| CTMC | committor, mean absorption time, fixed-partition sensitivity, residuals, positive-h Doob generator | explicit exponential/PH finite generator; provenance carried in output |
| independent sampling | SHA-256-derived replication streams, Gillespie paths, Wilson 95% interval, stream digest | vanilla estimator, not yet an IMS rare-event splitting theorem |
| public interface | `validate`, `prove`, `quantify`, `simulate`, `verify-case` with `ims-deadlock/cli/v1` JSON | unavailable inputs remain unavailable; no fabricated rates or siphons |

## Local validation, current integration

On 2026-07-30, the cache-disabled local coordination copy passed:

```text
pytest: 111 passed
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
   classification.

## Remote authoritative validation

The current 69-file source surface was packaged without caches, environments,
PDFs, credentials, or downloaded outputs. The initial integration archive
SHA-256 was:

```text
9395325008d59a59f98f0112b59d482d1ec53f90ef033932b2add79816069237
```

The hash matched on Dell before extraction into an isolated staging
directory and non-destructive copy into the clean integration worktree. The
qualified runtime was:

```text
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe
Python 3.13.9
```

Remote results:

```text
pytest: 111 passed
ruff check: passed
ruff format --check: passed
strict mypy: passed
CLI C0: exact_ims_sip1_wait_snapshot_duality, minimal empty siphon
BIX1-SAT test grid: 144 rows, 0 mismatches, 0 truncations
C5 non-SIP1 refusal regression: passed without fabricated siphon
```

The first staging pytest invocation inherited the editable installation's old
worktree source path and therefore imported the previous 91-test package. It
was rerun with `PYTHONPATH` fixed to the isolated staging `src` and passed all
111 tests. The first staging Ruff-format command also used a flag position not
accepted by the Dell Ruff version; `ruff format --no-cache --check .` passed.
These invocation corrections happened before the authority copy and are not
counted as source failures.

## Gate verdict

`G3 = PASS` on the locked Dell worktree for the explicitly implemented small
finite-model, `IMS-SIP^1`, and `BIX1-SAT` scope. The verdict does not close a
plant-level Petri/S3PR bridge, physical rate derivation, rare-event splitting,
general C5/persistent-buffer threshold, confirmation freeze, or paper claims.
