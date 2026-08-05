# G6-B Minimal Article Closure Scope

**Status:** FROZEN PRE-OUTCOME ARTICLE SCOPE

**Date:** 2026-08-06

## 1. Purpose

This scope converts the remaining research work from an attempted all-case
validation programme into a bounded theory-and-example article. The article
does not require one method to cover every case. Each method is evaluated only
on the cases that exercise its declared assumptions, and every limitation is
reported as part of the result.

The article asks one narrow question:

> Can request-closed A2b reasoning or a complete finite-LTS
> completion-nonreachability audit soundly admit a local blocking core as a
> stopped-process bad hit without confusing it with a plant terminal SCC, and
> do exact and DES first-hit calculations agree on predeclared constructive
> witnesses under the same target semantics?

## 2. Relation to the original G6-B gate

This is a versioned successor scope, not a rewrite of the sealed 13-case G6-B
bundle.

- The original 13 case units, 26 method observations, 13 companion groups,
  119 later-audit-eligible retired fingerprints, and 62 typed normalization
  refusals remain intact.
- The original eight-dimension G6-B overlap gate remains `OPEN/PENDING`.
- This scope does not assert G6-B PASS, held-out confirmation, blinded
  independence, full-tranche support, or broad IMS performance generalization.
- The article may use sealed G6-B cases as constructive or boundary witnesses
  after verifying their source identities. It does not relabel them as
  confirmation cases.
- G5 `4/3/2`, transparent `6/1/2`, both G5 minimality failures, G6-R R1/R2
  failures, and R3 historical-only status remain negative evidence.

The retired corpus has no later-audit-eligible projection in the
`random_stream_manifest_sha256` or `metric_schema_sha256` dimensions. This
absence is retained and is not converted into independence evidence. The
article therefore makes no claim that its random streams or metric schema are
independent replications of retired studies. It uses exact/DES agreement only
as a within-case semantic cross-check.

## 3. Frozen case panel

The machine-readable lock is
`cases/article_core/article_scope_lock_v1.json`. Selection is frozen before any
article-core target classification, exact solution, or DES result is produced.
No failed core case may be replaced after outcomes are observed.

| Case | Role | Method boundary |
| --- | --- | --- |
| `g6b_cu_pc_dglobal_only_v1` | time-zero `D_global` positive witness | classification witness, not a factory-wide stochastic model |
| `g6b_cu_pc_dlocal_a2b_single_kernel_v1` | request-closed A2b `D_local` positive witness with an outside progressing job | supports only the A2b subclass |
| `g6b_cu_pc_dlocal_lts_multi_kernel_v1` | complete-LTS multi-kernel `D_local` positive witness | supports only the enumerated finite LTS |
| `g6b_cu_nc_local_bypass_completes_v1` | completion-bypass negative control | a local candidate with a path to `F` must not enter `D_local` |
| `g6b_cu_nc_dglobal_only_with_dlocal_v1` | global/local precedence control | `D_global` is not double counted through `D_local` |
| `g6b_article_bridge_competing_local_completion_v1` | nontrivial first-hit probability bridge | one transient state jumps to an admitted `D_local` witness at rate 1 or `F` at rate 2 |

The remaining eight sealed cases stay in the original denominator and are
retained as taxonomy or appendix evidence. They are not required to close the
minimal article claim.

## 4. Constructive bridge case

The new bridge case is declared before execution:

```text
s0 --(enter_local, rate 1)--> d_local
s0 --(complete,    rate 2)--> f_complete
```

`d_local` carries the same request-closed A2b witness type as the sealed A2b
positive case. `f_complete` is the all-batch success class. The stopped target
is `D_global union D_local` versus `F`. Consequently, the exact selected-bad
first-hit probability is the preregistered analytical value `1 / 3`; this
formula is a derivation target, not an observed result.

The case exists because the five reused sealed witnesses are intentionally
small classification and counterexample cases. It supplies a non-degenerate
probability calculation without pretending to be a broad empirical benchmark.

## 5. Theory-to-case obligations

The case checker must establish the following before quantitative execution:

1. `D_global`, `D_local`, and `F` are pairwise disjoint under the declared
   precedence rule.
2. An A2b-admitted `D_local` state has a local closed blocking-kernel witness,
   is not `D_global`, and carries an explicit request-closed proof flag.
3. A complete-LTS-admitted `D_local` state has no plant path to `F` in the
   complete, nontruncated finite LTS.
4. A local candidate with a plant path to `F` is retained as a counterexample
   and excluded from `D_local`.
5. Plant arcs leaving a `D_local` state are permitted; they disappear only in
   the stopped process. Therefore `D_local` is a bad hit set, not a plant
   terminal SCC.
6. A state satisfying the global predicate is classified only as `D_global`,
   even if a local candidate is also present.
7. Every transient state in a quantitative case reaches `D_global`, `D_local`,
   or `F` almost surely under positive finite rates.

## 6. Quantitative compatibility rule

Each case reports the three frozen estimands:

- first hit of `D_global` before `F` under the stopped target;
- first hit of `D_local` before `F` under the stopped target;
- first hit of `D_global union D_local` before `F`.

Exact values are computed from the finite stopped CTMC. DES uses 4096
independent replications with master seed `2026080601` and per-replication seed
`sha256(master_seed:replication_index)`.

There are at most 18 case-estimand comparisons. With familywise error budget
`delta = 0.05`, the preregistered simultaneous Hoeffding tolerance is

```text
epsilon = sqrt(log(2 * 18 / 0.05) / (2 * 4096)) < 0.028340.
```

A cell is compatible when its absolute DES-minus-exact error is at most
`0.028340`. Any execution failure, missing cell, target mismatch, nonpositive
rate, nonabsorbing closed class, or post-hoc rerun is non-supporting. No retry
is allowed solely because a Monte Carlo estimate misses the tolerance.

## 7. Predeclared claim ladder

The article claim is chosen by a frozen ladder, not by replacing cases:

- **Tier A — dual-route closure:** both the A2b and complete-LTS positive
  witnesses pass their proof obligations; both boundary controls pass; the
  bridge exact/DES cell is compatible.
- **Tier B-A2b — A2b-only closure:** the A2b route and controls pass, the bridge
  is compatible, and the complete-LTS route is retained as refused or
  unresolved. The manuscript removes the complete-LTS empirical closure claim.
- **Tier B-LTS — complete-LTS-only closure:** the complete-LTS route and
  controls pass and a versioned LTS bridge is available; the A2b route is
  retained as refused or unresolved. The manuscript removes the A2b empirical
  closure claim.
- **Tier C — no local-method article closure:** neither local route closes.
  Results remain a negative/boundary report and cannot support the proposed
  article thesis.

## 8. Permitted and forbidden conclusions

Permitted, if the corresponding tier passes:

- a scoped theorem-to-witness consistency claim;
- a statement that `D_local` is a stopped-process bad hit rather than a plant
  terminal SCC;
- a within-case exact/DES same-target agreement claim;
- a counterexample-based statement that an apparent local core is insufficient
  when a completion bypass exists;
- an explicit method-limitations comparison between A2b and complete-LTS
  admission.

Forbidden:

- universal completeness or necessity of A2b;
- applicability to every IMS-RAS model or every AGV/reservation semantics;
- held-out confirmation or statistical independence from retired evidence;
- method superiority, production performance, rare-event efficiency, or
  generalization beyond the declared finite positive-rate cases;
- erasing failed, refused, residual, or noncore cases;
- claiming the original G6-B, G6-C, G6-D, G6-E, or paper gate has passed.

## 9. Manuscript logic

The article is organized around matched methods and cases:

1. define the objective state partition and stopped target;
2. prove the request-closed A2b sufficient condition;
3. define complete-LTS completion-nonreachability as the general finite-model
   fallback;
4. show the bypass counterexample and global/local precedence control;
5. derive the bridge case's exact first-hit formula;
6. report the predeclared DES cross-check and limitations;
7. state that the examples establish scoped constructive closure, not universal
   empirical coverage.

This is sufficient for a logically self-consistent theory/method article even
when methods cover different cases.
