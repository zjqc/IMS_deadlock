# G6-B Materialization Contract Projection-Scope Wording Erratum

Status: `FINAL / WORDING-ONLY / NO BYTE REPLACEMENT / NO NEW AUTHORITY`

Date: 2026-08-05

## Bound immutable subjects

This successor erratum preserves, rather than rewrites, the exact bytes that
were reviewed, approved, and used for the completed R1-R7 construction tranche:

- materialization-contract corrigendum SHA-256:
  `ff469d9c5105835fde5feb170e501bdde14506df50632990f7c2cddc251da36c`;
- revised v2 plan SHA-256:
  `81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7`;
- independent v2 plan-review SHA-256:
  `da6da7c2e513e11761e439f8b43ef6260556c912d3e730f94f15eae088d90ea0`;
- repaired sealed construction subject C3:
  commit `0fa08e66c249fb19d8c014127cca8441efa90505`, tree
  `8153fd46c4dae6dbd08a20fec93eab469fa8bc37`.

Changing the approved corrigendum would change its hash and would make the
plan's and review's content-addressed subject statements false. The original
three documents therefore remain byte-immutable historical authorities.

## Corrected reading

In the original corrigendum's non-normative background under `Why revision is
required`, the phrase `those five per-case projections` is imprecise. For all
future readings, interpret it as:

> five separately stored projection subjects: case content, DES output-root
> reservation, exact output-root reservation, DES random-stream manifest, and
> exact random-stream manifest.

Their scopes are not all per-case. Case content is case scoped. The DES and
exact output-root reservations and the DES and exact random-stream manifests
are method scoped.

This is the same rule already stated normatively in the original
`File-role and hash closure` section: case-content, state, route, parameter,
prediction, and metric projections are case/group scoped, while random-stream
and output-root projections are method scoped. The exact path roster likewise
already lists distinct DES and exact files for both method-scoped dimensions.

## Effect and non-effect

This erratum corrects wording only. It does not add, delete, rename, or rescope
any required file; change a schema field, hash subject, count, writer,
validator, recovery transition, task, approval gate, or authorization; or
change any sealed construction artifact. It does not retroactively authorize
or rerun case construction and does not authorize retired-authority
normalization, overlap audit, target preflight, CTMC, DES, scoring, output
inspection, confirmation, or any scientific-status upgrade.

G6-B remains `OPEN/PENDING`. The three downstream typed capabilities remain
false. Repository publication of this erratum is an audit clarification only.
