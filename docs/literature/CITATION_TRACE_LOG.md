# Citation Trace Log

## Scope

This log records the bounded citation-tracking work performed on 2026-07-29.
It is an OpenAlex taxonomy screen, not a systematic review and not a proof
source. The goal was to test whether new in-scope model classes, theorem
families, complexity boundaries, or counterexample categories kept appearing.

Conclusion:

> scope-bounded taxonomy saturation reached in two consecutive bounded rounds (R2/R3), but full-text theorem verification gate remains open.

This conclusion means the current taxonomy is stable enough to continue G2
formalization. It does not mean all relevant citations have been exhausted.

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
  - bibliographic identity and abstract remain verified;
  - no stable locally auditable equation locator was obtained, so the row
    remains `ABSTRACT` and cannot support CTMC equations.
- `B04`, Chen et al. (2011):
  - author-uploaded technical-report text inspected;
  - report p19: Assumptions 1-2 and Theorem 6, with the explicit proviso
    "if such a supervisor exists";
  - the 2012 correction to Section V-B is recorded and blocks verbatim reuse
    of that implementation paragraph until the correction text is checked.

This audit upgrades only the theorem-specific uses recorded in
`SOURCE_VERIFICATION.md`. It does not close the remaining L04/L16/L22/B05
full-text gates and does not transfer any source's complexity or convergence
result to IMS without the migration assumptions in `MIGRATION_CARDS.md`.
