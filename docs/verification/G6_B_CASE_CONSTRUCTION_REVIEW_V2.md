# G6-B Case Construction Review V2

## Review target

- Remote worktree:
  `D:\worktree\IMS_deadlock-g6b-case-construction-v2-r6-testfix`.
- Branch: `codex/g6b-case-construction-v2-r6-testfix`.
- Reviewed artifact subject C3:
  `0fa08e66c249fb19d8c014127cca8441efa90505`.
- C3 tree: `8153fd46c4dae6dbd08a20fec93eab469fa8bc37`.
- Source subject C2:
  `f000717aae1d5b385cf7ac494b07fc22b300c296`.
- C2 tree: `79a080d68e582d83c421d2e41db839ef07526ba6`.
- Draft PR: `https://github.com/zjqc/IMS_deadlock/pull/8`, stacked on
  `codex/g6b-case-construction-contract-revision` / Draft PR #7.
- Review mode: three independent read-only R7 lanes over the same exact C3.

## Verdict

**PASS CASE-CONSTRUCTION PUBLICATION / G6-B OPEN-PENDING**

| Review lane | Verdict | P0 | P1 | P2 |
| --- | --- | ---: | ---: | ---: |
| ontology / estimand / metric sharing | APPROVE / PASS WITH BOUNDARY NOTE | 0 | 0 | 0 |
| scientific boundary / nonreuse / source-seed-recovery | PASS / APPROVE | 0 | 0 | 0 |
| code / capability / schema-hash / artifact scope / test evidence | PASS | 0 | 0 | 0 |

The three reviews approve C3 only as a sealed, discovery-only
case-construction bundle. They do not approve retired-authority normalization,
actual-overlap analysis, Barrier-A target preflight, CTMC or DES execution,
scoring, confirmation, a G6-B scientific verdict, or paper readiness.

## Authorization semantics

The generated construction authorization is intentionally separate from the
immutable schema-only capability reference:

- `construction_authorization.json` has `authorized=true` for capability
  `case_construction`; this bounded authorization was consumed to create the
  sealed bundle.
- The source `row_family_protocol.json` still records its immutable reference
  `typed_capabilities.case_construction_authorized=false`. That frozen field is
  not evidence that construction did not occur and must not be presented as
  the live authorization artifact.
- The downstream capabilities remain unopened:
  `retired_authority_fingerprint_normalization_authorized=false`,
  `target_certification_preflight_authorized=false`, and
  `quantitative_execution_authorized=false`.
- The construction authorization explicitly forbids state enumeration,
  terminal classification, target certification, CTMC construction/solution,
  DES, scoring, output inspection, quantitative-root materialization,
  observation writing, and scientific-status advancement.

Construction authorization is therefore not scientific-execution
authorization. G6-B remains `OPEN/PENDING`.

## Immutable identity and artifact closure

- Approved v2 plan SHA-256:
  `81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7`.
- Materialization-contract corrigendum SHA-256:
  `ff469d9c5105835fde5feb170e501bdde14506df50632990f7c2cddc251da36c`.
- Independent v2 plan-review SHA-256:
  `da6da7c2e513e11761e439f8b43ef6260556c912d3e730f94f15eae088d90ea0`.
- Post-seal repair-plan SHA-256:
  `e749442d3f07c36ced57c21e8a7b3f7650e3197ba9c07d837b54076cf08bef8d`.
- Post-seal repair-plan-review SHA-256:
  `11be5b70b80f0994e3bfce46d87503b7f73ac04adbb56db67e77859bac2bac97`.
- Final Task-R2 source-review raw SHA-256:
  `6083632d9527ef56d7962f808dd71823dac31af106178cc1aa73a5b19dd16c49`.
- C3 commit-record raw SHA-256:
  `3f6d00a6753074a47872d9b39c18c922f56ee0bc3db71c6da848ea08291d5483`.
- C3 artifact-inventory SHA-256:
  `ea675bb6733e0d31d3085d29a0b32a1e418d4ae9135980477a132fa743469057`.

The C2..C3 diff contains exactly 394 paths, all with status `A`:

- 13 case units;
- 26 sealed method observations;
- 13 exact/DES companion groups;
- 390 case files, exactly 30 per case unit;
- four governance files;
- no source, schema, test, review, handoff, roadmap, or other documentation
  path.

Governance identities:

- authorization raw / self SHA-256:
  `1421a42242ed85e6c72573cd905514b2b5013b7731fe5ae9266d4d6d1dc8567b` /
  `942f1eaa2b9887c8a670513b363821f378121f99fc4a7235772d3592d0860890`;
- construction-log raw / self SHA-256:
  `8a89b4deeeebde49ff95a914901a9c07999cdb85ac1b9602c166181f012e35e5` /
  `adb7dfe9a277cef32a4e9ad0124c853e0c4a3a5d9a8c67ffa1f98799d19140da`;
- ledger raw SHA-256:
  `1e3ddb63450627a7832a0362b82af9b08d8af8db9c8a5551b39c24badf565cae`;
- ledger entry count / head: `393` /
  `600e8d13dbc08ca0d9c1bf25046ddaa0fbe859e50e8a4ccfa280610aeef4a713`;
- sealed-manifest raw / self SHA-256:
  `95fc411a02d8085b84c1a4f2025d2c7806e1d8c632b645f556c61aefe1b6406b` /
  `36622495237f2c22677190b3858d275ea8285d0ee8fc1ed004f8c03e8543a68c`.

The independent verifier confirmed canonical/self hashes, ledger chaining,
manifest references, exact IDs/counts/inventory, manifest-last ordering, and
absence of transient, reserved, and later scientific roots. Artifact-only
verification raw SHA-256 is
`feae518021191dc77d9658359ee90c4b7a2b606a3fd18b5bf6582c8b7c533486`.

## R6 validation closure

- Four-file post-seal focused suite:
  `1975 passed, 2 skipped in 2895.04s (0:48:15)`;
  log SHA-256
  `26450819ad2b73dcc79c66d2b4f001643e7ef0f477df9ca3a2d8d602421ba9b3`;
  focused/static summary raw SHA-256
  `8640cfe4cd8446185f0292aa39680e488f4f450861cb5613a93198177180f1d4`.
- Full collection: 2423 tests; summary raw SHA-256
  `05a967282b64d7ebcbc073e6801d87a438f2555a930aa1330ee20ec652da688a`.
- Full repository with four isolated xdist workers and `worksteal`:
  `2421 passed, 2 skipped in 799.34s (0:13:19)`;
  log SHA-256
  `5526de5862214ff40b01f21929745ce75d64414a47b4e4f80b638ffd12b2b5c5`;
  summary raw SHA-256
  `531744867d295f76eb579beaeb18a1bccba2a654d1337ad14321b6d15ee1c496`.
- Ruff check, Ruff format, strict mypy, and `git diff --check` all exited zero.
- The C3 worktree was clean. Before first publication it had no upstream; the
  branch was then pushed without force and now tracks
  `origin/codex/g6b-case-construction-v2-r6-testfix`.

## Independent lane evidence

### Lane 1: ontology, estimand, and metric sharing

The reviewer locked C3 and recursively parsed the artifact set. All 13 case
units have `CASE_UNIT_SEALED_NO_EXECUTION`, all 26 method observations have
`METHOD_SEALED_NO_OUTPUT`, and all 13 companion groups have
`METHOD_SEALED_NO_OUTPUT`. All selected targets retain the predeclared first-hit
stopping rule. Output reservations have `materialized=false` for 26/26.
Exact/DES appears as sealed companion-method and future metric semantics, not as
observed output. No ontology collapse or estimand drift was found.

### Lane 2: scientific boundary, nonreuse, source, seed, and recovery

The reviewer verified one consistent bundle ID, the C2 source lock, the
authorization/log/ledger/manifest chain, 393 ordered ledger entries, and zero
interruption/refusal records. All 13 transform records have
`retired_case_payload_read=false`, `retired_outcome_used=false`,
`outcome_driven_tuning_prohibited=true`, and no declared semantic parent.
No old absolute worktree path or later instance root is serialized in C3. No
actual-overlap, preflight, CTMC, DES, scoring, confirmation, or G6-B-PASS output
was found.

### Lane 3: code, capability, schema/hash, artifact scope, and test evidence

The reviewer independently reproduced the exact 394-path all-added closure,
13-times-30 case inventory, four governance files, all governance self-hashes,
all 393 ledger entry hashes, manifest references, and absence of cache,
transient, reserved, and downstream roots. No source/test/doc path is part of
C3. No actionable finding was found.

## Retained negative and partial evidence

Negative evidence was not erased or promoted to a passing result:

- The prior post-seal subject remains preserved. Its focused result was
  `1 failed, 1974 passed, 2 skipped`, caused by a phase-stale fixture attempting
  to recreate an already copied `case_units` directory. Incident raw / self
  SHA-256 is
  `da37b05654202157e938b4e623c607cabf80bbf46d9c59994409b50d5e727eb8` /
  `3ab768a2f89c3b5359b569a252354034814181d15b7ffe83dcbf76efc4b4087f`;
  failed log SHA-256 is
  `0a8311aa2a6a93eb1903982c6fdd8bc595f5a1af5dfe59b6be6f74e30c8ef5d0`.
- The first rebound focused attempt failed before test execution because it was
  bound to the wrong import source; its log SHA-256
  `766789d3aaab5b3e5d6317a422867ec9d260c92804c49c67c44f358822e0a5d0`
  remains in the final focused summary.
- The first full remote stream was interrupted after reaching 97%; interruption
  record SHA-256
  `8cd34775b5dc574914c2692bd5175d43f2c3cce6f34d1ee248e6dfc95e50b571`
  remains referenced by the passing resume-2 summary.
- A scheduled-task execution context was shown non-equivalent to the normal SSH
  test token and was not accepted as scientific verification. The decisive
  focused and full passes above both used the normal SSH token.

## Claim and continuation boundary

This review proves only that the exact C3 discovery construction bundle is
sealed, hash-valid, independently reviewed, and non-scientific. It does not
prove semantic independence from retired authorities, actual overlap, target
validity, exact/DES same-target equivalence, any outcome estimate, Barrier A or
B, or G6-B PASS.

G6-C, G6-D, and G6-E remain `NOT STARTED / NOT PASSED`. After the
documentation-only C4 publication, the mandatory stop remains in force. The
first possible scientific successor is a separately authorized, data-only
retired-authority fingerprint-normalization tranche.
