# Citation Trace Log

## Scope

This log records the bounded citation tracking begun on 2026-07-29 and the
current-work freshness audit on 2026-07-30. It is not a systematic review and
not a proof source. The goal is to test whether new in-scope model classes,
theorem families, complexity boundaries, or counterexample categories keep
appearing.

Conclusion:

> R2/R3 reached historical scope-bounded saturation, but Round 4 found a new
> reachable-partial-deadlock theorem category and reset the stop counter.

The historical result was enough to begin G2 formalization. It no longer
satisfies the current stop rule: `L29-L31` must seed new bounded rounds, and
`L30-L31` require full-text verification.

## Method Limits

- Database: OpenAlex.
- Sorting: `cited_by_count:desc`, which favors visible, older, highly cited
  records and can miss recent or niche work.
- Screening: title/abstract/metadata first, with follow-up only for candidate
  category changes.
- Coverage: OpenAlex reference lists and citation edges can be incomplete.
- Exclusions: unreliable-resource, partial-observation, continuous/hybrid timed
  PN, collision scheduling, and generic vehicle-routing branches were logged as
  outside the first-paper scope unless they changed IMS-RAS deadlock theory.

## Round 1

- Date: 2026-07-29.
- Database: OpenAlex.
- Seeds and OpenAlex IDs:
  - `10.1109/70.370500` -> `W2140872435`
  - `10.1137/0325013` -> `W1979349468`
  - `10.1023/A:1012203214611` -> `W1483186571`
  - `10.1016/j.ejor.2017.10.039` -> `W2767453465`
  - `10.1109/ROBOT.2001.932531` -> `W2133158797`
  - `10.1137/070699500` -> `W2055484248`
- Forward filter: `filter=cites:<id>&sort=cited_by_count:desc&per-page=10`.
- Backward screen: up to first 50 referenced IDs, sorted by cited count, with
  `per-page=10`.
- In-scope new categories / boundaries:
  - multiple acquisition and flexible routing: `10.1109/9.956052`;
  - multi-AGV deadlock/liveness control: `10.1109/TSMCB.2005.850141`;
  - multi-vehicle maximal-permissive complexity: `10.1109/TAC.2010.2046111`;
  - classical FMS Petri-net prevention/avoidance: `10.1109/70.63257`;
  - siphon plus mathematical programming: `10.1109/70.650158`;
  - intersection deadlock probability: `10.1049/itr2.12210`.
- Out-of-scope branches:
  - unreliable-resource and outage robustness for first paper;
  - partial observation/diagnosis variants.
- Reseed reason: new in-scope taxonomy categories appeared.

## Round 2

- Date: 2026-07-29.
- Database: OpenAlex.
- Anchors:
  - six new Round 1 items above;
  - `10.1109/TASE.2006.884674`;
  - `10.1109/TAC.2008.929375`.
- Forward filter: `filter=cites:<id>&sort=cited_by_count:desc&per-page=8`.
- Backward screen: referenced IDs sorted by cited count, `per-page=8`.
- In-scope result:
  - repeated taxonomy: siphon control, maximally permissive supervision,
    multi-AGV deadlock/liveness, and traffic/intersection deadlock.
- Out-of-scope categories:
  - continuous/hybrid timed Petri nets;
  - collision scheduling and generic vehicle routing.
- Stop/reseed reason: no new in-scope model/theorem/counterexample category,
  but one more bounded round was required to test saturation.

## Round 3

- Date: 2026-07-29.
- Database: OpenAlex.
- Anchors:
  - `10.1109/TAC.2014.2381453`;
  - `10.1109/TASE.2018.2798630`;
  - `10.1109/TSMC.2022.3232743`;
  - `10.1109/TASE.2010.2060332`;
  - `10.1109/TSMCA.2008.2007947`.
- Forward/backward bound: `per-page=5`.
- In-scope result:
  - repeated categories: vehicle routing/scheduling, PN supervisory control,
    maximally permissive control, complexity, and multi-AGV traffic.
- Out-of-scope categories:
  - continuous/hybrid timed Petri nets;
  - collision-free scheduling and path planning without IMS-RAS blocking
    certificate implications.
- Stop reason:
  - second consecutive bounded round without a new in-scope
    model/theorem/counterexample category.

## Use in G1 Gate

The taxonomy screen supports continuing to G2 formalization with the current
six-chain map. It does not close the full-text verification gate. Sources may
enter theorem statements only through `SOURCE_VERIFICATION.md` and
`LITERATURE_MATRIX.md` as `FULLTEXT-THEOREM` rows with exact locators.

## Targeted Full-Text Locator Audit

- Date: 2026-07-29.
- Temporary research copies only; PDFs were not added to the repository.
- `L08`, Lawley and Reveliotis (2001):
  - author PDF visually inspected;
  - PDF p10: Theorem 1, `SU-SAFE is NP-complete`;
  - PDF p15: Proposition 2, intractable SU-RAS subclasses contain
    deadlock-free unsafe states;
  - PDF pp18-24: capacitated-knot definition and RC1/SR1/SR2/CB1
    hard/easy-boundary conditions.
- `L09`, Nazeem and Reveliotis (2011):
  - Georgia Tech author PDF visually inspected;
  - PDF p5: Proposition 1 and Definition 1 on componentwise safe/unsafe
    monotonicity and maximal-safe/minimal-unsafe states;
  - Section III: boundary reachable unsafe states as the implementation
    interface for the maximally permissive LES.
- `L25`, Cerou and Guyader (2007):
  - author full text visually inspected;
  - journal p422 / PDF p7: Hypothesis H and Theorem 1 on almost-sure
    consistency;
  - journal p425 / PDF p10: Theorem 2 on asymptotic normality and variance.
- `L16`, Narahari et al. (1990):
  - full 11-page article inspected;
  - Section 3 / journal pp. 346-348: finite transient/absorbing partition and
    `F=(I-T)^-1`;
  - Section 3.1: mean time to deadlock;
  - Section 3.2: `G=FC` absorption probabilities;
  - Section 4 / journal pp. 350-351: transient time-to-deadlock distribution;
  - upgraded only for this historical DTMC/embedded-chain scope, not for the
    project's CTMC sensitivity or Doob-h theorem.
- `B04`, Chen et al. (2011):
  - author-uploaded technical-report text inspected;
  - report p19: Assumptions 1-2 and Theorem 6, with the explicit proviso
    "if such a supervisor exists";
  - the 2012 correction to Section V-B is recorded and blocks verbatim reuse
    of that implementation paragraph until the correction text is checked.

## Targeted Full-Text Locator Audit, Round 2

- Date: 2026-07-30.
- `L04`, Liu et al. siphon survey:
  - publisher full text inspected;
  - Section 4, Theorems 2-3 locate the ordinary-net deadlock/siphon facts;
  - Theorems 4-7 map generalized/controlled-siphon and S3PR-family results;
  - retained as `FULLTEXT-CONTEXT` because it is a secondary survey, not the
    original proof source.
- `L22`, Viswanadham, Narahari, and Johnson (1990):
  - full 11-page journal article inspected;
  - Petri/GSPN definitions, GE-FMS blocked-machine/buffer model, reachable
    deadlock, reachability-based prevention, and finite-look-ahead avoidance
    were located;
  - retained as `FULLTEXT-CONTEXT` because the methods paper has no numbered
    theorem/proposition/lemma chain for migration.
- `B05`, Chen and Li (2011):
  - DOI and publisher metadata remain stable;
  - no auditable full theorem text was recovered;
  - remains blocked for theorem-level use; B04 is the theorem-located
    maximum-permissiveness benchmark.

These audits close the targeted L04/L16/L22 locator questions with
scope-specific classifications. B05 remains open by design. No source's
complexity, liveness, or convergence result transfers to IMS without the
assumption mapping in `MIGRATION_CARDS.md`.

## Round 4: Current-work Freshness Audit

- Date: 2026-07-30.
- Search objective: challenge the proposed reachability-certificate,
  finite-capacity-threshold, and structural-control novelty against work
  published or indexed after the original anchor set.
- Current in-scope comparators:
  - `L29`, Lu, Chen, Hadjicostis, and Li (2026), was read in publisher full
    text. Its modified resource-requirement graph, PDDP characterization,
    iterative control-place insertion, and controlled-net liveness theorem
    make it the mandatory structural/control baseline.
  - `L30`, Pang et al. (2025), officially describes minimum resource
    configuration for an equivalent finite-capacity S3PR net. It remains
    abstract-only and therefore cannot yet support a theorem comparison.
  - `L31`, Su et al. (2026), officially describes critical
    resource-limit-pair linear equations for detecting reachable partial
    deadlocks without a reachability tree. It remains abstract-only and is the
    highest-priority full-text threat audit.
- New category found:
  - `L31` adds a direct reachable-partial-deadlock/no-reachability-tree claim,
    which is materially closer to the proposed structural certificate than
    the categories recorded in Rounds 1-3.
- Consequence:
  - the previous two-round taxonomy saturation is historical evidence, not a
    current stop certificate;
  - freshness tracking is reopened and must be reseeded from `L29-L31`;
  - at least two consecutive bounded rounds after this reseed must find no new
    in-scope model, theorem, or counterexample category before the taxonomy
    stop rule is satisfied again;
  - no manuscript may claim the first reachable structural certificate,
    the first reachability-free partial-deadlock detector, or general
    finite-capacity threshold novelty while `L30-L31` remain unread in full.
