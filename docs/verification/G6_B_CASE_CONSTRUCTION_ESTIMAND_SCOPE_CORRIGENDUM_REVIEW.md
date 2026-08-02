# G6-B Case Construction Estimand Scope Corrigendum Review

Date: 2026-08-02 Asia/Shanghai

Status: Task1 `COMPLETED / REVIEWED`. This is a schema/test/documentation corrigendum only. It does not authorize Task2, does not create construction authorization, does not create case units, does not normalize retired authority fingerprints, does not run overlap/preflight/CTMC/DES, and does not inspect scientific outputs.

## Locked Subject

| Item | Value |
| --- | --- |
| Base commit | `7c7d11d7960ef650fbded1cca413da790285970b` |
| Base tree | `3b014960dee4107892d422a7b74259cfecf7cb5e` |
| Subject commit | `f8b777713fc7d5f239ab6449d99c050452db6f98` |
| Subject tree | `b65b096a6135991ede09c125fbd9de4f381733e9` |
| Plan SHA-256 | `c20393328f8f98e7b35a6507fd6e993b2f17e068d977c3dc6253b05e9a75de5f` |
| Plan review SHA-256 | `297a69382347e16e894af63e70f8fa95807407048b2e89c45701410a4e9289e1` |
| Corrigendum raw SHA-256 | `5b5266a562fb4e1515121a351d0b98227338bf34c991eef2fe76557b0e17334f` |
| Original design SHA-256 | `b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6` |
| Typed capability hash | `21ad3b3663fe1a693a7f64c19a91010c6eb1bc2ac3f3018b8c54de38997135fc` |
| Branch | `codex/g6b-case-construction` |
| Draft PR | `https://github.com/zjqc/IMS_deadlock/pull/6` |
| PR base | `codex/g6b-case-construction-plan` / PR #5 |

## Changed Bytes

| Name | SHA-256 |
| --- | --- |
| `cases/discovery/g6b/row_families/structural_discovery_v1/case_construction_schema.json` | `e4107f92afd957ad41f55e29fd053ace0062a20b25a1fe3b5f3d75b7dd36a6c4` |
| `cases/discovery/g6b/row_families/structural_discovery_v1/identity_schema.json` | `a31bcfbb51c5c8d0594f319bd64f4465b3b0d157e3a331abedbedbaa996dd6d8` |
| `cases/discovery/g6b/row_families/structural_discovery_v1/retired_authority_fingerprint_schema.json` | `f0c8b649bee392752aec15aed28ac492584a6071d09ef7bdd963ee28a00323bc` |
| `docs/superpowers/specs/2026-08-02-g6b-case-construction-estimand-scope-corrigendum.md` | `5b5266a562fb4e1515121a351d0b98227338bf34c991eef2fe76557b0e17334f` |
| `src/ims_deadlock/g6b_row_family_protocol.py` | `e991b7ca5a32930151591aac66a0eef91780c4e1859793e6a30ce1953141e915` |
| `src/ims_deadlock/g6b_schema_contracts.py` | `a533e5ce383acbb4c5ff4b68d1f7941e5d1baf962805810197e09833bb917225` |
| `tests/test_g6b_row_family_protocol.py` | `5b127b444b613cb4099c6f1401b24624974de104e7e478e47bd0f60034cfdd11` |
| `tests/test_g6b_schema_contracts.py` | `d2feb628921abeb9eaac0b4441092d89a2b2963f7887249fb1d419e73657bf16` |

## Canonical Bundle Hashes

| Name | SHA-256 |
| --- | --- |
| `row_family_protocol` | `bc3d451c2996dc1104773d44cd4b64bffa3228d8865713a929d70aadf8c3edbc` |
| `identity` | `dd33178221ed6a0fdce9b6dd0260c492c011ad5f04e43ee6b0e75fedbeb31b3a` |
| `matrix` | `435783028dd7a118bc160aeea54f3081be60ecef94b863e0b73978186cd17e4a` |
| `reuse` | `dcd700cfc8b0ceb15448989cb42b879a00f2748f85a040005291a734fda53f7c` |
| `overlap` | `55d833d8772d3493c09f15d995973db87f22e197f9a9e42606affd7e6ff52db4` |
| `runtime` | `1da275b64535b8ad22020c4f158fcb9355d20ea291eee28580299fb9f051da08` |
| `review` | `358c69a23451778f94432bb020a8bd0a35e2d6e9e5fd084179fd24f23bbba4d8` |
| `failure` | `34be766f1f8dd97037180547f9b2bde242787c941969771433bceda394dffb87` |
| `case` | `828382b6787408477c9b0a3170475e08a8971c54b4860349b1da3b8495d74b42` |
| `retired` | `456a66067b5703695948719dc7ccbdfa09d8c2d6eced1c9f544d387234ee8f78` |
| `target` | `d090c6fb4621b7d9c78f18d133970eeb308eb6202023878297a394941a42515b` |
| `quantitative` | `e42b1089330206fcd46a2eac90d68abba80e10e13940c7a53186140dd403a624` |

## Protected Byte-Identical JSON

| Name | SHA-256 |
| --- | --- |
| `row_family_protocol.json` | `43889604fe411e21e17ece9b8a99bd18aadd7d7c14ed9893221494fcd5683acc` |
| `row_family_matrix.json` | `487d81aa79a7bca681db81f19a4d6bd315668c43b1c4538c47f01f099d8e205f` |
| `reuse_matrix.json` | `c0f9c836d63e6f929de778d124d9b4ac464eb1b6e936301359156db566d7d228` |
| `overlap_report_schema.json` | `b309cf686b803cb93945e265f40c191e8f5f5c318fd2fe034160899caaa9b884` |
| `runtime_lock_schema.json` | `2ef6ab4443b9d705671a09c900be20c8404c919849d12388087204235f07bf64` |
| `review_state.json` | `eab8aa61fa93d6cc21f572fa2496e69453abfdd1ea25940f32fb49a18e76bf26` |
| `failure_ledger.json` | `dec8fa38a22d6e726f318313c84224b7d5e8b9accf68f770efee21f590413529` |
| `target_certification_schema.json` | `2edfd65cfc5fcb0ac98b67dbe75632a86b255f5d8cd7a11e03a978eae257fef6` |
| `quantitative_authorization_schema.json` | `9263d41b34aa51bf6aeb9924e3f2be59d59f2aba3214c84aaad53666eb16a91d` |

## Exact Artifact Sets

Exact-twelve nested row-family bundle paths:

- `cases/discovery/g6b/row_families/structural_discovery_v1/case_construction_schema.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/failure_ledger.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/identity_schema.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/overlap_report_schema.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/quantitative_authorization_schema.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/retired_authority_fingerprint_schema.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/reuse_matrix.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/review_state.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/row_family_matrix.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/row_family_protocol.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/runtime_lock_schema.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/target_certification_schema.json`

The exact-twelve inventory consists of row_family_protocol.json plus its exact ordered eleven artifact_paths. Task1 changes only three JSON schemas; the other nine JSON artifacts listed in Protected Byte-Identical JSON remain byte-identical.

The corrigendum spec is `docs/superpowers/specs/2026-08-02-g6b-case-construction-estimand-scope-corrigendum.md`. It is not a thirteenth nested bundle JSON.

## Scope And Semantics

- Task1 synchronized `estimand_id_scope_contract` across the case-construction schema, identity schema, and retired-authority-fingerprint schema.
- Schema versions after Task1 are case construction v2, identity v3, and retired-authority fingerprint v2.
- Only these two nested path patterns are allowed to carry predeclared identifiers: `/directional_hypotheses/*/estimand_id` and `/metric_entries/*/estimand_id`.
- Only these value codes are allowed: `g6b_estimand_theta_global_before_success_v1`, `g6b_estimand_theta_local_before_success_v1`, and `g6b_estimand_theta_selected_bad_before_success_v1`.
- Default policy remains recursive prohibition; runtime certificate observation or result use is prohibited.
- Four capabilities remain false: `case_construction_authorized=false`, `retired_authority_fingerprint_normalization_authorized=false`, `target_certification_preflight_authorized=false`, and `quantitative_execution_authorized=false`.
- Later roots remain absent: `cases/discovery/g6b/row_families/structural_discovery_v1/governance/`, `cases/discovery/g6b/row_families/structural_discovery_v1/case_units/`, `evidence/g6b/target_certification/`, and `artifacts/g6b/quantitative/`.

## TDD And Negative Evidence

- Initial focused RED: `11 failed, 10 passed`.
- Initial GREEN: `21 passed`.
- Schema suite after first fix: `387 passed`.
- Scope-guard full serial on `dfe9dbe81851dbff5e7dd104fe27caacd6268ca9`: `1 failed, 1127 passed, 2 skipped in 2713.04s (0:45:13)`.
- Scope guard was fixed on `a72a7cac4254ef31933b6f3233575bb7b4253c9f`.
- Independent code review found a HIGH fail-closed taxonomy issue where unhashable JSON list/dict `estimand_id` values raised `TypeError`.
- Type-fix RED: `4 failed, 8 passed`.
- Type-fix GREEN: `14 passed`.
- Final schema suite: `401 passed`.
- Documentation-successor scope RED: review path was rejected as `outside_task6_declared_files`, `1 failed in 0.62s`.
- Documentation-successor GREEN: review publication, Task1 exact-eight, and global diff-scope nodes `3 passed in 0.64s`; Task-6 selection `17 passed, 1115 deselected in 0.65s`.
- The final full repository evidence is bound to subject `f8b777713fc7d5f239ab6449d99c050452db6f98`; this documentation successor uses narrow scope, formatting, type, Markdown, path, and diff checks only.

These RED results are retained as evidence. Interrupted exploratory or superseded runs are not counted as final completion evidence.

## Final Verification Evidence

- Full repository: `2170 passed, 2 skipped in 611.87s (0:10:11)`.
- Full run used four-process `pytest-xdist` worksteal only through an isolated temporary dependency target outside both the repository and shared project virtual environment.
- Ruff: `All checks passed!`; format check: `47 files already formatted`.
- Strict mypy: `Success: no issues found in 25 source files`; strict mypy over source and tests: `Success: no issues found in 47 source files`.
- Direct canonical bundle validation: `valid=True`, `errors=0`, `scientific_execution_authorized=False`, `case_creation_authorized=False`, `adversarial_review_status=PENDING`, `current_state=ROW_FAMILY_BUNDLE_IMPLEMENTED`.
- Final independent reviews: ontology/spec, boundary/nonreuse, and code-quality all `APPROVE`; Critical/High/Medium/Low counts are all zero.

## Stop Condition

Task1 is complete and reviewed. The first unchecked next step is Task2 materializer implementation, but it may start only after the user again explicitly approves entry into Task2. The current execution stops at Task1.
