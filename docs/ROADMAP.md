# IMS Deadlock Roadmap

This roadmap freezes a theory-first gate sequence for IMS-RAS deadlock research. Each gate has an input, output, and stop condition so implementation does not outrun definitions and evidence.

## G0: Clean Baseline

- Input: local bootstrap source directory and project operating contract.
- Output: minimal repository metadata, contribution contract, ignore rules, and roadmap.
- Stop condition: the baseline contains no core algorithm, no case corpus, no downloaded papers, no generated outputs, and no secret material.

## G1: Literature And Definitions

- Input: G0 baseline plus authoritative IMS-RAS, deadlock, supervisory control, stochastic process, and resource allocation references.
- Output: DOI-backed literature notes, symbol table, minimal IMS-RAS state model, resource/process definitions, deadlock/liveness definitions, and explicit scope exclusions.
- Stop condition: every imported claim has a source boundary, every primitive term is defined, and open assumptions are listed before implementation begins.

## G2: Structural Theory

- Input: G1 definitions and scoped assumptions.
- Output: structural invariants, reachability conditions, siphon/trap or equivalent deadlock criteria, candidate lemmas, proof sketches, and counterexample search plan.
- Stop condition: candidate criteria are stated as mathematical claims with assumptions, proof obligations, and known failure modes.

## G3: Probabilistic Layer

- Input: G2 structural claims and declared stochastic model family.
- Output: probability model, transition assumptions, risk metrics, sampling semantics, uncertainty bounds, and separation between theoretical probability statements and simulation estimates.
- Stop condition: stochastic claims are testable without redefining the structural model and do not rely on unrecorded empirical tuning.

## G4: Control Synthesis And Verification

- Input: G2/G3 claims, controller observability assumptions, and frozen confirmation cases.
- Output: control policy specification, correctness argument, program-verification harness, discovery-case results, and confirmation-case results.
- Stop condition: program evidence is traceable to frozen cases and each accepted control claim has either a proof or a clearly bounded conjecture status.

## G5: Reproducible Release

- Input: verified G4 theory, code, cases, tests, and evidence ledger.
- Output: reproducible package, documented commands, versioned case suite, citation ledger, and release notes.
- Stop condition: clean checkout validation can reproduce the claimed checks without private files, hidden state, or untracked generated inputs.

## Isolated Contamination Notice

The historical identifier `e0b07a52ed667ce2651dfccf2455d6876a96b02d` is marked as isolated polluted history. It may be mentioned only as provenance context for exclusion decisions. It must not be used as scientific evidence, validation evidence, proof support, benchmark source, or source material for cases, algorithms, or claims in this repository.
