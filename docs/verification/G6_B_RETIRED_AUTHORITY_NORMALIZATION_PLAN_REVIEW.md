# G6-B Retired-Authority Normalization Plan Review

Verdict: PASS PLAN-ONLY PUBLICATION / IMPLEMENTATION AND NORMALIZATION NOT AUTHORIZED

Review status: FINAL INDEPENDENT PLAN-ONLY REVIEW

P0 count: 0

P1 count: 0

P2 count: 1 watch item

## Bound Subjects

This review binds exactly these plan subjects:

- Implementation plan raw SHA-256: 7b2396b9e85b834715167d05b4b2a545b57541b0ad168e6a23bbe8752cc749be
- Capability corrigendum raw SHA-256: 79c843fd64c6249447309b84e19d73b503fdfe9b4372018a483b89e15af23e49
- C4 base commit: 0943e6eeeb17ff9a310d0d4b461cca301c08aefa
- C4 base tree: c1ba3956614988c6deb39ead085f6e57cf9e278c

The review also binds the frozen anchors named by the plan:

- Approved design raw SHA-256: b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6
- Retired authority fingerprint schema raw SHA-256: f0c8b649bee392752aec15aed28ac492584a6071d09ef7bdd963ee28a00323bc
- Current schema contracts raw SHA-256: cf84fff421eae6d31eed5ac578748eb00de4d3bda9095456f979146b523e9a27
- Current schema-contract tests raw SHA-256: 22f3bc365d141eee3b4d4fa5b210568f0e9d10b65eb501b6a2d51844448c8522
- Schema v2 review raw SHA-256: cabdb3c1cf9994197eda58809ea328f01a2558976594c06ef792f2dc0f4cd5ab

No remote command, scientific process, retired-field parsing, normalization execution, overlap comparison, target preflight, CTMC, DES, scoring, or evidence-producing run was performed for this review.

## Authorization Boundary

This review, its hash, a Draft PR, reviewer PASS verdicts, or ordinary continuation language do not authorize implementation or normalization.

Tasks 1-8 remain blocked until the user exactly names and approves all three raw byte subjects together:

- the implementation plan raw SHA-256;
- the capability corrigendum raw SHA-256;
- this independent plan-review artifact raw SHA-256.

Tasks 9-10 remain blocked after Tasks 1-8. They require a later, separate user approval that exactly names the normalization authorization raw/self SHA-256 and the normalization-authorization-review raw SHA-256. Only that later approval can authorize retired-field parsing, creation of the normalization governance root, or normalizer execution.

## Lane A: Plan Critic Review

Scope:

- Capability overreach and science-boundary preservation.
- Full writer closure and output-root semantics.
- Approval gates and task ordering.
- Git object ID versus SHA-256 typing.
- Two-review aggregation.
- Nineteen-pattern inventory versus twenty-seven concrete source paths.
- Six-field lineage preimage and duplicate-alias semantics.
- Manifest-last, interruption, and no-retry behavior.

Evidence:

- The plan has two explicit gates. The plan gate authorizes only Tasks 1-8 after exact user approval and explicitly does not authorize retired projection parsing or root creation. The execution gate separately authorizes only Tasks 9-10 after exact authorization and authorization-review approval.
- The scientific boundary prohibits use of G5/G6-R result values, stdout/stderr, scores, observed probabilities, observed times, mechanism verdicts, raw historical output payloads, overlap comparison, LTS enumeration, target certification, CTMC/DES, hypothesis scoring, scientific output inspection, downstream roots, and status advancement.
- The exact output closure contains only one normalization governance root with authorization, three authority locks, source records, fingerprint records, and a final manifest. It excludes overlap reports, comparison records, target certificates, output reservations, scientific summaries, and execution results.
- The authorization validator task separates `expected_schema_inventory_patterns` from `expected_concrete_source_paths`, preserving the frozen nineteen-row pattern inventory while binding authorization `allowed_source_paths` to the expanded twenty-seven concrete file paths.
- The corrigendum expands the writer surface from the frozen two-writer shape to exactly five artifact writers and requires lexical plus runtime containment.
- The corrigendum permits only the closed schema-contract validator surface from `g6b_schema_contracts` and requires transitive project-import closure tests.
- Git `source_head` and `source_tree_hash` are treated as caller-bound Git object IDs under the live object format. Content, record, code, inventory, review, and manifest hashes remain lowercase SHA-256.
- Origin lineage IDs use exactly the frozen six-field preimage. Duplicate and inherited records remain visible but are non-counting aliases when they map unambiguously to one valid origin lineage.
- The source review bundle is canonical JSON v2 with exactly two independent lanes, identical source HEAD/tree, PASS verdicts, aggregate count reconciliation, and P0/P1 aggregate counts of zero.
- The manifest is written last, an interrupted root is preserved without a valid manifest, and no cleanup, promotion, duplicate process, or in-place retry is allowed.

Lane A result: PASS

Lane A counts: P0=0, P1=0, P2=0

## Lane B: Readiness Verifier Review

Scope:

- Implementation-readiness after the prior P0/P1 repair cycle.
- Closure of the schema-contract import/call surface.
- Verification adequacy before allowing a plan-only publication.
- Residual watch items that should be enforced during implementation review.

Evidence:

- The readiness verifier result is PASS with P0=0 and P1=0.
- The verifier accepted the repaired schema-contract import and exact validator-call closure.
- The verifier accepted the frozen six-field lineage preimage and duplicate-alias one-count semantics.
- The verifier accepted the split between frozen nineteen-row schema inventory patterns and expanded twenty-seven concrete authorization paths.
- The verifier accepted the five-writer closure and manifest-last/interruption/no-retry contract.

Lane B result: PASS

Lane B counts: P0=0, P1=0, P2=1 watch item

## Closed Prior Findings

The previous P0/P1 findings are closed in the current plan and corrigendum bytes:

- Prior P0: the normalizer needed schema-contract validators but the frozen allowlist did not include `ims_deadlock.g6b_schema_contracts`. Closed by the corrigendum's closed schema-contract import surface and the plan's AST/import-closure test requirements.
- Prior P1: the lineage preimage had drifted from the frozen six-field definition. Closed by requiring exactly `origin_authority_id`, `origin_subject_type`, `origin_subject_id`, `origin_dimension`, `origin_comparison_projection_sha256_or_null`, and sorted `origin_source_artifact_byte_hashes`.
- Prior P1: duplicate lineage could be read as automatic ineligibility. Closed by defining inherited and duplicate records as visible non-counting aliases when they map unambiguously to one valid origin lineage.
- Prior P2: the abstract inventory and concrete inventory could be conflated. Closed by separating `expected_schema_inventory_patterns` from `expected_concrete_source_paths` and binding `allowed_source_paths` to the expanded twenty-seven-file tuple.

## P2 Watch Item

P2-WATCH-1: `ims_deadlock.g6b_governance` remains in the authorization allowlist because it exists in the frozen allowlist shape, but the plan and corrigendum prohibit creating or importing a new `g6b_governance.py` in this tranche. Implementation review must verify the actual normalizer source and transitive import closure tests enforce that prohibition.

This is not a P0 or P1 because the current plan explicitly says not to create or import `ims_deadlock.g6b_governance`, keeps the source/test commit closure to four files, and requires actual-source plus transitive import closure tests.

## Representative Task Simulation

Task 2/3 authorization-binding simulation:

- A valid fixture must use 40-character Git object IDs for `source_head` and `source_tree_hash` under the current SHA-1 object format.
- It must pass separate expected pattern inventory and concrete source path arguments.
- It must reject any mismatch in source HEAD/tree, file-manifest hash, normalizer code hash, review hash, output root, selector matrix, or source path closure.

Result: actionable without guessing.

Task 4/5 writer-containment simulation:

- Only five top-level writer functions may contain `Path.mkdir`, `Path.write_bytes`, or `Path.replace`.
- The authorization writer creates the absent root and writes the approved authorization bytes first.
- The other writers write only deterministic child paths under that root.
- The manifest writer writes last and refuses until referenced records exist with matching bytes.
- Any exception before manifest finalization preserves incomplete evidence and cannot be retried in place.

Result: actionable without guessing.

Task 6 lineage and producer simulation:

- The producer map remains the frozen Section 10.2 table.
- Raw-bytes-only sources are not parsed.
- Outcome/result/stdout/stderr/score fields cannot enter projection preimages.
- G5 and G6-R inherited records copy a unique G4 lineage rather than minting new independent lineages.
- Duplicate records remain visible aliases and the unique lineage is counted once.

Result: actionable without guessing.

Task 7/8 review and authorization simulation:

- Source review requires two independent lanes over the same exact HEAD/tree.
- Any source/test change invalidates both reviews.
- The canonical source-review bundle binds both lane reviews, raw hashes, counts, source HEAD/tree, and normalizer byte hash.
- The external authorization candidate is reviewed but not committed and does not authorize normalization until exact user approval.

Result: actionable without guessing.

Task 9/10 execution-boundary simulation:

- Execution starts only after the second exact approval gate.
- The root must be absent before retired-field parsing.
- Completion requires an independently valid final manifest.
- Artifact successor C2 is artifact-only, and documentation successor C3 is documentation-only.
- Publication stops at `RETIRED_AUTHORITY_NORMALIZATION_COMPLETE / G6-B OPEN-PENDING`.

Result: actionable without guessing.

## Final Counts

Aggregate P0 count: 0

Aggregate P1 count: 0

Aggregate P2 count: 1

Publication recommendation: PASS PLAN-ONLY PUBLICATION.

Implementation authorization: NOT AUTHORIZED.

Normalization authorization: NOT AUTHORIZED.

Stop condition: publish this review only as a plan-review artifact. Do not proceed to Tasks 1-8 until exact user approval binds the plan, corrigendum, and this review. Do not proceed to Tasks 9-10 until the later exact normalization authorization and authorization-review approval exists.
