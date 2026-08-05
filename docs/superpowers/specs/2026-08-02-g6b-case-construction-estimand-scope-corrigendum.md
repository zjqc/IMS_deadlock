# G6-B Case Construction Estimand Scope Corrigendum

Date: 2026-08-02

Status: schema/governance corrigendum only

## Scope

This corrigendum resolves the case-construction `estimand_id` contradiction in
the G6-B schema bundle. The original 2026-08-01 design remains immutable. This
document does not add a thirteenth bundle schema file, create a case, authorize
retired-authority normalization, authorize target certification preflight, or
authorize quantitative execution.

## Correction

The construction payload contract permits `estimand_id` only in these two
predeclared comparison-projection positions:

- `/directional_hypotheses/*/estimand_id` in the
  `sealed_prediction_sha256` projection, with use
  `predeclared_directional_hypothesis_identifier_only`.
- `/metric_entries/*/estimand_id` in the `metric_schema_sha256` projection,
  with use `predeclared_metric_identifier_only`.

Every other construction-instance path remains under recursive prohibition.
That includes root, sibling, result, runtime, certificate, observation,
authorization, quantitative, and arbitrary nested placements.

Allowed values are exactly:

- `g6b_estimand_theta_global_before_success_v1`
- `g6b_estimand_theta_local_before_success_v1`
- `g6b_estimand_theta_selected_bad_before_success_v1`

Runtime-derived hashes, observations, execution results, quantitative
authorization fields, and post-outcome estimand substitutions remain
prohibited.

## Versioned Schema Contract

The following three schema-governance JSON documents carry the same
`estimand_id_scope_contract` object:

- `case_construction_schema.json`,
  `ims-deadlock/g6b-case-construction-schema/v2`
- `identity_schema.json`,
  `ims-deadlock/g6b-row-family-identity/v3`
- `retired_authority_fingerprint_schema.json`,
  `ims-deadlock/g6b-retired-authority-fingerprint-schema/v2`

The exact-twelve JSON bundle inventory remains closed. The nine other bundle
JSON files are not modified by this corrigendum.

## Non-Authorization Statement

All four runtime capabilities remain false:

- `case_construction_authorized=false`
- `retired_authority_fingerprint_normalization_authorized=false`
- `target_certification_preflight_authorized=false`
- `quantitative_execution_authorized=false`

The roster remains exactly 13 case units, 26 method observations, and 13
companion groups. This corrigendum creates no construction authorization and
must stop before Task 2 materializer work.
