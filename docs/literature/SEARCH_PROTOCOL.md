# G1 Literature Search Protocol

## Scope

This literature library supports the IMS-RAS project claim:

> 在明确定义的有限批 IMS-RAS 子类中，操作死锁何时具有可计算、可审计且足以支持非阻塞监督的最小结构证书？

The search is theory-first. It is not a broad narrative review and it does not
authorize theorem claims from abstracts, metadata, or secondary summaries.

## Six Evidence Chains

1. Petri nets, S3PR/S4PR, siphons, monitors, liveness.
2. DES supervisory control, controllability, nonblocking, maximum permissiveness.
3. RAS safety, deadlock avoidance policies, complexity, tractable subclasses.
4. Finite-buffer queueing networks and manufacturing blocking.
5. AGV, traffic/transport resources, reservation conflicts.
6. Absorbing CTMC, committor/Doob-h transforms, rare-event estimation.

## Source Status

| Status | Meaning | Allowed use |
| --- | --- | --- |
| `FULLTEXT-THEOREM` | Full text was inspected and a theorem/proposition/equation, appendix, or section locator is recorded. | May support IMS theorem statements, proof obligations, and migration cards within that locator's scope. |
| `FULLTEXT-CONTEXT` | Full text was inspected, but no theorem locator is yet fixed for this project. | May support background, examples, and boundary discussion. |
| `ABSTRACT` | Only abstract, publisher page, or landing page was inspected. | Search guidance only. No theorem claims. |
| `METADATA` | Bibliographic metadata or DOI record only. | Citation candidate only. No scientific claim. |
| `PENDING` | Candidate identified but not yet verified. | Search backlog only. |
| `REJECTED/CORRECTED` | Candidate was wrong, mismatched, or superseded by corrected source. | Error ledger and audit trail only. |

## Forward/Backward Tracking Rule

The concrete 2026-07-29 bounded OpenAlex trace is recorded in
`CITATION_TRACE_LOG.md`.

For each seed source, record:

- backward references that introduce a new model class, theorem type, proof
  technique, complexity boundary, or counterexample;
- forward citations that introduce the same;
- the reason for stopping.

The search may declare taxonomy saturation only after two consecutive bounded
tracking rounds produce no new in-scope model category, theorem category, or
critical counterexample. Current status: **scope-bounded taxonomy saturation reached in two consecutive bounded rounds (R2/R3), but full-text theorem verification gate remains open**. This is not a completed systematic review and does not claim exhaustive citation saturation.

## Theorem-use Rule

A theorem, lemma, equivalence, complexity result, or counterexample can enter
`docs/theory/` only if the source row in `LITERATURE_MATRIX.md` is
`FULLTEXT-THEOREM` and has a locator. Section-level locators may support only
the section-level result actually recorded; they do not authorize unlisted
theorem claims.

## No-copy Rule

PDFs, cached publisher pages, private datasets, credentials, and old simulation
outputs are not part of this repository. Bibliographic records should cite DOI
links, author pages, or publisher pages only.

## Audit Queries

Core search strings:

- `"S3PR" siphon deadlock prevention Petri net`
- `"resource allocation systems" deadlock avoidance safety NP-hard`
- `"finite buffer" queueing network deadlock knot`
- `"AGV" deadlock Petri net manufacturing reservation`
- `"absorbing Markov chain" deadlock manufacturing system`
- `committor Doob h transform rare event Markov chain`

Each query must be logged in future updates with date, database, filters, and
new candidate count.
