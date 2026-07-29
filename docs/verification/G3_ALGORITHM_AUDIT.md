# G3 Algorithm Audit

## Scope

This audit covers only the small finite-model verifier. It does not close the
Petri/siphon bridge, derive physical rates for C5, freeze confirmation cases, or
replace the mathematical proofs in `docs/theory/CORE_THEOREMS_AND_PROOFS.md`.

## Implemented checks

| Obligation | Executable evidence | Scientific boundary |
| --- | --- | --- |
| stable semantics | deterministic bounded LTS, set-valued urgent closure, per-successor trace, capacity validation | state truncation is explicit and disables exact-supervisor claims |
| reachable certificate | all reachable stable states scanned; full-event shortest prefix; inclusion-minimal kernel and capacity witnesses | capacity-mediated closed-world transition registry only |
| structural baselines | raw simple cycle, capacity-aware state-dependent wait-graph knot, Banker snapshot, finite-LTS terminal SCC | each baseline has a separate assumption label; none substitutes for P2 |
| BIX0 threshold | deterministic grid over `c_M,c_G,c_D=1..3`, `n_A,n_B=0..4` | candidate-state/no-successful-transfer family only; no richer reachability claim |
| exact supervisor | uncontrollable closure, marked coaccessibility, disabled state-event pairs, all initial closure outcomes | explicit finite full-observation LTS only |
| CTMC | committor, mean absorption time, fixed-partition sensitivity, residuals, positive-h Doob generator | explicit exponential/PH finite generator; provenance carried in output |
| independent sampling | SHA-256-derived replication streams, Gillespie paths, Wilson 95% interval, stream digest | vanilla estimator, not yet an IMS rare-event splitting theorem |
| public interface | `validate`, `prove`, `quantify`, `simulate`, `verify-case` with `ims-deadlock/cli/v1` JSON | unavailable inputs remain unavailable; no fabricated rates or siphons |

## Local validation

On 2026-07-29, the cache-disabled local coordination copy passed:

```text
pytest: 91 passed
ruff check: passed
ruff format --check: passed after formatting
strict mypy: passed
```

An independent structural review also passed the adversarial checks for:

1. a deadlock certificate reached only after non-zero transitions;
2. non-confluent urgent closure with distinct branch traces;
3. multiple uncontrollable initial closure outcomes, one unsafe;
4. omitted frontier arcs under `max_states`;
5. a three-event early-discovered path versus a two-event later-discovered
   path to the same certificate state.

## Remote authoritative validation

The exact 66-file source manifest was packaged without caches, environments,
PDFs or downloaded outputs. Its transfer archive SHA-256 was:

```text
ac6fc02ad7997eefcd1978616e002a515f91b4ab16c8d83e5413c4a809b7cb15
```

The hash matched on Dell before extraction into the clean integration
worktree. The qualified runtime was:

```text
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe
Python 3.13.9
```

Remote results:

```text
pytest: 91 passed
ruff check: passed
ruff format --check: passed
strict mypy: passed
CLI smoke: validate/prove/quantify/simulate/verify-case passed
discovery cases: C0-C5 and C5_DAG passed registered expectations
BIX0 grid: 648 rows, 0 mismatches
```

The first mypy attempt used Windows `NUL` as a cache directory and failed
inside mypy 2.3.0 before checking the project. It was rerun successfully with a
task-owned cache directory, which was then deleted. This tool invocation issue
is not counted as a source failure.

## Gate verdict

`G3 = PASS` for the explicitly implemented small finite-model scope. The
verdict does not close the Petri/siphon bridge, physical rate derivation,
rare-event splitting, general C5 threshold, confirmation freeze, or paper
claims.
