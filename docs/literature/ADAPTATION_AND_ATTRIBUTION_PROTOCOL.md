# Adaptation and Attribution Protocol

## Purpose

IMS_deadlock may reuse mature mathematical objects, proof techniques,
counterexample patterns, and algorithms when that reuse improves correctness.
Reuse is not a novelty claim. The project must make the intellectual lineage
auditable while proving the IMS-specific adaptation independently.

Cosmetic renaming, reordered exposition, or notation changes do not turn a
published result into a new contribution. Deliberately disguising a source is
prohibited.

## Source-use Classes

Every nontrivial source use must be assigned one of these classes:

1. `DIRECT-BASELINE`: the published theorem or algorithm is implemented or
   evaluated under its original assumptions.
2. `ADAPTED-RESULT`: a published result supplies the proof architecture, but
   the IMS statement changes the state semantics, assumptions, or conclusion.
3. `INDEPENDENT-REDERIVATION`: the same mathematical fact is rederived for IMS
   from the operational semantics; the prior result is still cited as lineage.
4. `HEURISTIC-INSPIRATION`: a graph, counterexample, or algorithmic idea guides
   design but supplies no theorem evidence.
5. `NON-TRANSFERABLE`: the result is relevant prior art, but at least one
   indispensable assumption fails in IMS.

Only a source with an inspected full text and exact locator may support
`DIRECT-BASELINE` or `ADAPTED-RESULT` theorem language.

## Required Adaptation Record

Before a sourced result enters a theorem, proof, algorithm, or case design, its
migration card must record:

- canonical citation and exact theorem/equation/section/page locator;
- source model, state semantics, assumptions, and conclusion;
- the borrowed object: statement, proof device, reduction, algorithm,
  counterexample pattern, or evaluation design;
- an explicit symbol/semantic map from the source model to IMS-RAS;
- source assumptions that fail, are strengthened, or are newly proved;
- the IMS-specific lemma or counterexample that repairs the gap;
- the genuinely new conclusion, if any;
- the case and machine check that attack the adapted result;
- where the citation will appear in the paper.

If the proof order closely follows a source, the citation must appear at the
start of the proof, not only in the bibliography.

## Reuse Limits

- Do not copy substantial prose, proof text, tables, figures, or formula
  sequences. Short unavoidable terminology or notation must be cited.
- Do not present changed variable names, relabeled resources, or a translated
  proof as originality.
- Do not use an abstract to reconstruct missing theorem assumptions.
- Do not merge several known results and claim that the combination alone is a
  top-journal contribution.
- Do not remove negative cases that expose a failed transfer.
- Do not claim priority when a recent closed-access comparator has not been
  read in full.

## Similarity and Novelty Audit

Before manuscript freeze, each main theorem must pass two separate checks:

1. `lineage audit`: every borrowed proof step or design idea has an adjacent
   citation and a complete migration card;
2. `novelty audit`: after deleting all direct baselines and inherited proof
   devices, the remaining IMS-specific statement, lemma, counterexample, or
   interface is still substantive.

The audit outcome is one of:

- `independent IMS theorem`;
- `transparent adapted theorem`;
- `restricted corollary / benchmark`;
- `context only`;
- `novelty insufficient — stop and reformulate`.

## Current High-risk Comparators

- `L29`: modified resource-requirement graph, PDDP characterization, and
  iterative Petri-net control.
- `L30`: finite-capacity S3PR minimum-resource configuration.
- `L31`: CRP and linear-equation reachable partial-deadlock detection.
- `L32-L33`: structure modification intended to make Petri-net reachability
  decidable or polynomial-time analyzable.
- `L34-L35`: legal-firing-sequence methods that expose the gap between a state
  equation's nonnegative integer solution and actual reachability.
- `B05`: compressed maximally permissive monitor supervisor via full RG and
  NP-hard MCPP.

After the 2026-07-30 supplied full-text audit, `L30-L35` and `B05` are
full-text theorem-located comparators under their recorded assumptions and
nontransferable IMS boundaries. They are not priority proofs, general IMS
theorems, or generic Petri-net bit-polynomial reachability results.
