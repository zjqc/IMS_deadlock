# T-ASE Hardening Panel Design

Status: `SPEC / AWAITING EXACT USER APPROVAL / NO CASE BYTES`
Date: 2026-08-19
Revision: `compute-parallel-v2` — supersedes the unapproved first draft
  hashes `3f9ca4db…6a0d` / `7cc80339…8eec` / `52bf822d…e3a0`.
Base: `codex/journal-hardening-v1` after the audit commits
Scope id: `tase_hardening_v1`
Evidence root: `evidence/tase_hardening/v1/`
Companion audit: `docs/verification/JOURNAL_THEORY_AUDIT_V1.md`
Companion map: `docs/theory/THEOREM_CASE_LOOP_MAP.md`

This specification authorizes only the design of a new discovery/hardening
panel. It does not authorize case materialization, overlap execution,
Barrier A/B, CTMC, DES, or a scientific PASS. Implementation may start only
after the user names the exact spec SHA-256, exact plan SHA-256, and exact
independent-review SHA-256.

## 1. Purpose

Close the T-ASE blockers that the journal-readiness assessment already named,
without reopening article-core v1 or the original G6-B overlap gate:

1. instantiate the still-open theory counterexamples that keep Paper A honest;
2. run same-semantics baselines on one plant generator;
3. report scale and refusal behaviour on a parameterized family;
4. add one synthetic high-fidelity manufacturing island with a predeclared
   intervention and KPI.

Paper A centre remains typed local first-hit. P5/P6/BIX full texts stay out
of the main claim.

## 2. Non-goals

- Relabel article-core v1 as held-out confirmation.
- Complete the original 13-case eight-dimension G6-B overlap.
- Start G6-C/D/E.
- Rewrite `evidence/article_core/minimal_closure_v1/`.
- Claim shop-floor validation.
- Claim method superiority from a single detector covering every case.
- Copy tolerance `0.028340` by habit.

## 3. Authorization map

All flags start false and remain false until a later, separately hashed
authorization object is approved.

```text
case_construction_authorized = false
overlap_audit_authorized = false
target_certification_preflight_authorized = false
quantitative_execution_authorized = false
theory_revision_authorized = false
```

Creating this spec does not flip any flag.

## 4. Identity and independence

Every materialized subject, when later authorized, must be distinct from:

- article-core v1 scope lock and six case identities
- retired G4 / G5 / G6-R hashes that have eligible projections
- G6-B sealed discovery case-content / snapshot / route / parameter /
  sealed-prediction hashes

Collision on any of those dimensions is a hard stop, not a rename.

New objects:

- `scope_id = tase_hardening_v1`
- `evidence_root = evidence/tase_hardening/v1/`
- new random-stream manifest
- new metric schema
- new stopping-rule hash even if the mathematical target looks similar

## 5. Case families

### Family H1 — theory-hardening counterexamples

| Case ID | Ledger | Expected machine outcome |
| --- | --- | --- |
| `H1_CE_CL1_nonconfluent_closure` | CE-CL1 | two terminating zero-time sequences, two distinct stable successors; refuse deterministic `kappa` |
| `H1_CE_BIXD2_optional_drain` | CE-BIXD2 | optional controllable drain exists; original ring saturation prefix still reachable; not structural deadlock-free |
| `H1_CE_INT1_new_core_after_cut` | CE-INT1 | deleting one backflow removes kernel K1 and creates kernel K2 |
| `H1_P3_nonchain_refuse` | audit A4 | a covering kernel that is not chain-decomposable; P3 returns not-applicable, never deadlock-free |

CE-NB1 is already instantiated and must be cited, not rebuilt.
CE-RSV1 remains optional and is not required for Paper A centre.

H1 cases are logical witnesses. They may be tiny. They may not be replaced
after outcomes are observed.

### Family H2 — same-semantics baselines

One shared generator produces plants on which all four methods see the same
`TransitionSpec` world:

1. machine wait-for cycle / SCC
2. capacity-aware closed core (this project)
3. `IMS-SIP^1` siphon detector if and only if assumptions hold; otherwise
   typed refusal
4. complete finite-LTS reachability truth, or typed truncation refusal

Predeclared metrics, all computed on the same plant:

- false positive vs LTS truth
- false negative vs LTS truth
- refusal count
- certificate size
- runtime
- peak enumerated state count

A semantic mismatch (for example treating service-complete as release) is a
protocol violation, not a baseline win.

Eight semantic types, each crossed with four predeclared capacity/WIP
cells, giving **32 independent plants**:

- residual cycle
- unit-capacity deadlock
- multi-capacity residual
- AGV-required
- `IMS-SIP^1` positive
- siphon-refusal outside SIP1
- local-with-bypass
- global-with-local-looking-core

The four cells are frozen in the preregistration (`tight`, `one-below`,
`balanced`, `loose`). Plants are embarrassingly parallel: one worker
enumerates that plant’s LTS once, then runs the four methods in-process
against the same LTS. Do not spawn one process per method on the same
plant; that would re-enumerate and waste RAM.

### Family H3 — scale and diversity

Parameterized, finite, and either fully enumerable or explicitly refused.

Axes:

- jobs in `{2,3,4,6}`
- resources in `{2,3,4}`
- capacities in `{1,2}`
- alternatives in `{1,2}`
- kernel count in `{0,1,2}`
- bypass present in `{false,true}`
- transport token present in `{false,true}`

H3 may not support a new theorem by itself. It reports state count, kernel
family size, runtime, and refusal rate. Any truncated row is `refused`, not
a numeric success.

Cap any single H3 row at **100_000** stable states or **300** seconds.
Exceeding the cap is a typed refusal, not a numeric success.

The axis product is 576 independent rows. They must be scheduled as a
process pool (Section 12). A serial H3 sweep on this machine is a
protocol miss, not a scientific choice.

### Family H4 — one synthetic manufacturing island

Required fields:

- two or three cells
- finite input and output buffers
- BAS blocked-unload
- at least one AGV or hard reservation token
- explicit routes for at least two job types
- documented synthetic rate source (not claimed plant data)
- engineering interpretation of `D_global`, `D_local`, bypass, and `F`
- exactly one predeclared structural intervention: delete backflow, or add
  one buffer slot, or disable one controllable handoff
- predeclared KPIs: selected-bad first-hit probability and mean stopped
  time on the same target; WIP or makespan only if the estimand is written
  before execution and uses the same stopping hash

Label: `synthetic digital-twin`. Forbidden label: shop-floor validation.

H4 is two plants (base and the one predeclared intervention). After both
Barrier A certificates exist, their exact solves and DES shards run in
parallel. DES uses **65536** replications per plant, sharded across
scientific workers (Section 12). The simultaneous probability tolerance
is the Hoeffding bound written in the preregistration, not article-core
`0.028340`.

### Family H5 — optional CRP overlap

Include only if the later implementation plan keeps Paper A’s reviewer
attack “why not CRP” in scope. Must implement G6 Proposition 6.4’s four
independent fields. Must not reuse G4/G5 case hashes. Default for the first
authorized implementation tranche: **omit H5**.

## 6. Quantitative protocol

When later authorized, and only then:

- exact CTMC and DES share one frozen stopping-rule hash
- selected targets are `D_global`, `D_local`, `F` with the same precedence
  as article-core
- unselected reachable `R_livelock` / `R_terminal` refuse the quantitative
  row
- DES uses a new master seed, not `2026080601`
- H4 sample size is 65536 replications per plant; the simultaneous
  Hoeffding tolerance is computed in the preregistration
- one primary wave and one repro wave; repro starts only after **every**
  primary cell in **every** family finishes
- independent plants, H3 rows, and DES shards **must** run in parallel
  inside a wave (Section 12)
- the same case’s primary and repro must never overlap
- no retry, no third run, no failed-case substitution
- each worker writes only its shard file; one reducer process writes the
  manifest and hashes

H1 logical witnesses do not require DES. H2 uses structure plus LTS truth;
DES is optional. H3 is structural/runtime. H4 is the only family that must
have exact+DES if it emits a probability.

## 7. Theory-revision rule

After authorized results exist:

Allowed:

- tighten a hypothesis
- instantiate a CE ledger row that now has a witness
- demote a claim from proved to restricted or open
- add a lemma that a new case forced
- assign a new theory version id

Forbidden:

- rewrite article-core v1 numbers
- delete a negative H-family member
- replace a failed case
- declare G6-B PASS
- declare T-ASE-ready solely because the panel ran

## 8. Owned paths

Allowed writes after later authorization, and only then:

- `cases/discovery/tase_hardening_v1/`
- `src/ims_deadlock/tase_hardening.py`
- `tests/test_tase_hardening.py`
- `evidence/tase_hardening/v1/`
- `docs/cases/TASE_HARDENING_PREREGISTRATION.md` (this file’s sibling)
- documentation pointers in `PROJECT_HANDOFF.md` and `docs/ROADMAP.md`

Forbidden writes:

- `evidence/article_core/**`
- `cases/confirmation/g4/**`
- `evidence/g5/**`
- `evidence/g6/**`
- frozen G6-B specification bytes
- `main`

## 9. Tests required before any science flag is true

- schema/parse tests for every H-family identifier
- independence tests that reject known article-core and G4/G5 hashes
- authorization tests that keep all five flags false by default
- no quantitative golden values checked in

## 10. Stop conditions

Stop and re-plan if:

- any authorization flag is true in this spec commit
- a designed case collides with a frozen hash
- H4 is labelled as real plant data without a source locator
- H3 numeric rows include truncated enumerations
- the implementation plan starts CTMC in the same commit as case JSON
- a scientific run is launched with `workers=1` while the live probe
  reports at least 16 free logical CPUs and 32 GiB free RAM
- BLAS/OpenMP threads per worker times worker count exceeds
  `1.5 * logical_cpus`

## 11. Approval object

The user must name:

```text
approved_spec_sha256=
approved_plan_sha256=
approved_review_sha256=
```

A general “continue” is not approval of these bytes.

## 12. Compute and parallelism contract

Live Dell facts recorded 2026-08-19 (must be re-probed before every long
run, not treated as standing capacity):

- CPU: Intel Xeon w7-3465X, 28 cores / 56 logical processors
- RAM: 136633843712 bytes (~127 GiB); that session had ~98 GiB free
- GPU: NVIDIA RTX PRO 2000 Blackwell is present
- Qualified runtime already imports `pytest` and `xdist`

The current solvers are CPU process-level (LTS enumeration, sparse linear
CTMC, Gillespie). The GPU is recorded and **unused**. Do not add a CUDA
path in this tranche and do not claim GPU acceleration.

### 12.1 Worker count

Before a long scientific or full-suite command:

1. record logical CPUs, free RAM, and other Python/pytest processes;
2. compute

```text
reserve_cpus = 8
max_workers  = clamp(logical_cpus - reserve_cpus, 4, 48)
if free_ram_giB < 16: max_workers = min(max_workers, 4)
elif free_ram_giB < 32: max_workers = min(max_workers, 16)
per_worker_giB = 2 for H1/H2, 4 for H3/H4
max_workers = min(max_workers, floor(free_ram_giB / per_worker_giB))
```

3. default scientific workers on this box: **32**, raised to **48** only
   if free RAM ≥ 64 GiB and no other heavy Python job is live;
4. default pytest-xdist workers for verification: **16** with
   `--dist worksteal`, or 8 if free RAM < 32 GiB.

On this machine the default 32 scientific workers leave 24 logical CPUs
and tens of GiB for the OS and the reducer.

### 12.2 Oversubscription ban

When `scientific_workers >= 8`, every worker process must start with

```text
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1
NUMEXPR_NUM_THREADS=1
```

Do not combine a 32-process pool with default multi-threaded BLAS.

### 12.3 What may run in parallel

| Unit | Parallel? | Grain |
| --- | --- | --- |
| H1 four witnesses | yes | one case / process |
| H2 32 plants | yes | one plant / process; four methods stay in-process |
| H3 576 rows | yes | one row / process |
| H4 base and intervention Barrier A | yes | one plant / process |
| H4 exact CTMC | yes | one plant / process |
| H4 DES replications | yes | contiguous seed shards, then reduce |
| pytest verification | yes | xdist worksteal |
| same case primary vs repro | **no** | repro wave after all primaries |
| two reducers writing one manifest | **no** | single reducer |

### 12.4 Wave order

```text
wave P0: live probe + worker lock file
wave P1: H1 + H2 + H3 structural (fully parallel)
wave P2: H4 Barrier A for both plants (parallel)
wave P3: H4 exact for both plants (parallel)
wave P4: H4 DES primary shards for both plants (parallel)
wave R0: only after P1–P4 are all terminal
wave R1: H4 DES repro shards (parallel)
wave Z:  single reducer, hashes, refuse partial manifests
```

A missing shard is a failed wave, not an invitation to retry that shard
in isolation after seeing other numbers.

### 12.5 Output isolation

Worker `i` writes only
`evidence/tase_hardening/v1/shards/<wave>/<unit_id>__w<i>.json`.
The reducer reads the shard directory once, writes
`article`-style exact/DES/report/manifest files, and then the shard
directory is immutable. Workers never append to a shared JSON.

### 12.6 Shared environment

Reuse
`D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe`
with `PYTHONPATH` pointing at this worktree. `xdist` is already in that
environment; do not install or upgrade packages for parallelism. Do not
point workers at another project’s interpreter.
