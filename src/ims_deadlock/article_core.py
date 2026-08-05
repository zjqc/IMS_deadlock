"""Scoped theory-to-case closure for the minimal G6-B article panel.

The module deliberately leaves the original eight-dimension G6-B gate open.
It validates a predeclared constructive six-case panel, solves the stopped
finite CTMC exactly, and cross-checks the same target with reproducible DES.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from math import isfinite
from pathlib import Path
from random import Random
from typing import cast

from ims_deadlock.ctmc import AbsorbingCTMC
from ims_deadlock.g6b_canonical_json import (
    JsonObject,
    JsonValue,
    canonical_bytes_v2,
    finalized_self_hash,
    loads_v2,
    validate_canonical_decimal_string,
    validate_repo_relative_posix_path,
    verify_finalized_self_hash,
)

SCOPE_LOCK_PATH = Path("cases/article_core/article_scope_lock_v1.json")
BRIDGE_CASE_PATH = Path(
    "cases/article_core/g6b_article_bridge_competing_local_completion_v1.json"
)
SEALED_BASE = Path(
    "cases/discovery/g6b/row_families/structural_discovery_v1/case_units"
)
SEALED_MANIFEST_PATH = Path(
    "cases/discovery/g6b/row_families/structural_discovery_v1/governance/"
    "g6b_discovery_case_construction_v1/sealed_bundle_manifest.json"
)
NORMALIZATION_MANIFEST_PATH = Path(
    "cases/discovery/g6b/row_families/structural_discovery_v1/governance/"
    "g6b_retired_authority_normalization_v1/normalization_manifest.json"
)
DEFAULT_EVIDENCE_ROOT = Path("evidence/article_core/minimal_closure_v1")

ARTICLE_CASE_IDS = (
    "g6b_article_bridge_competing_local_completion_v1",
    "g6b_cu_nc_dglobal_only_with_dlocal_v1",
    "g6b_cu_nc_local_bypass_completes_v1",
    "g6b_cu_pc_dglobal_only_v1",
    "g6b_cu_pc_dlocal_a2b_single_kernel_v1",
    "g6b_cu_pc_dlocal_lts_multi_kernel_v1",
)
SEALED_CASE_IDS = ARTICLE_CASE_IDS[1:]
ESTIMANDS = (
    "theta_global_before_success",
    "theta_local_before_success",
    "theta_selected_bad_before_success",
)
TARGET_CLASSES = ("D_global", "D_local", "F")
ORIGINAL_G6B_GATE = "OPEN_PENDING"


@dataclass(frozen=True)
class ArticleTransition:
    """One positive-rate plant transition in an article case."""

    source: str
    event: str
    target: str
    rate: Decimal


@dataclass(frozen=True)
class ArticleCase:
    """Typed finite-state article witness and its admitted target classes."""

    case_id: str
    source_role: str
    source_path: Path | None
    source_sha256: str
    states: tuple[str, ...]
    initial_state: str
    transitions: tuple[ArticleTransition, ...]
    d_global_states: frozenset[str]
    d_local_states: frozenset[str]
    completion_states: frozenset[str]
    local_candidate_states: frozenset[str]
    a2b_verified_states: frozenset[str]
    lts_complete: bool
    admission_route: str
    expected_boundary: str


@dataclass(frozen=True)
class CaseCertificate:
    """Mechanical theory-obligation certificate for one case."""

    case_id: str
    source_role: str
    source_path: str | None
    source_sha256: str
    admission_route: str
    d_global_states: tuple[str, ...]
    d_local_states: tuple[str, ...]
    completion_states: tuple[str, ...]
    local_candidate_states: tuple[str, ...]
    completion_reachable_by_candidate: dict[str, bool]
    plant_transition_count: int
    stopped_transition_count: int
    checks: dict[str, bool]


@dataclass(frozen=True)
class ExactFirstHitResult:
    """Exact finite-CTMC first-hit result for the three frozen estimands."""

    case_id: str
    probabilities: dict[str, Decimal]
    mean_absorption_time: Decimal
    committor_residuals: dict[str, Decimal]
    analytical_identity: str | None


@dataclass(frozen=True)
class DesFirstHitResult:
    """Reproducible multiclass Gillespie estimate."""

    case_id: str
    sample_count: int
    counts: dict[str, int]
    probabilities: dict[str, Decimal]
    mean_absorption_time: Decimal
    stream_manifest: dict[str, JsonValue]


@dataclass(frozen=True)
class CompatibilityCell:
    """One preregistered exact-versus-DES comparison cell."""

    case_id: str
    estimand: str
    exact: Decimal
    des: Decimal
    absolute_error: Decimal
    tolerance: Decimal
    compatible: bool


@dataclass(frozen=True)
class ArticleClosureResult:
    """Complete in-memory result for the predeclared article panel."""

    case_ids: tuple[str, ...]
    certificates: tuple[CaseCertificate, ...]
    exact_results: tuple[ExactFirstHitResult, ...]
    des_results: tuple[DesFirstHitResult, ...]
    compatibility_cells: tuple[CompatibilityCell, ...]
    comparison_cell_count: int
    all_cells_compatible: bool
    claim_tier: str
    original_g6b_gate: str


def load_article_scope(repo_root: Path) -> JsonObject:
    """Load and validate the frozen pre-outcome article scope."""

    scope = _load_json_object(repo_root / SCOPE_LOCK_PATH)
    verify_finalized_self_hash(scope, "scope_lock_sha256")
    if _string_tuple(scope.get("article_core_case_ids"), "article_core_case_ids") != (
        ARTICLE_CASE_IDS
    ):
        raise ValueError("article_core_case_ids do not match the frozen panel")
    if scope.get("no_failed_case_substitution") is not True:
        raise ValueError("no_failed_case_substitution must be true")
    if scope.get("study_role") != (
        "scoped_constructive_theory_article_not_confirmation"
    ):
        raise ValueError("study_role must retain the constructive article boundary")

    denominator = _object(scope.get("original_sealed_denominator"), "denominator")
    if denominator.get("case_unit_count") != 13:
        raise ValueError("original sealed denominator must retain all 13 cases")
    if denominator.get("method_observation_count") != 26:
        raise ValueError("original method-observation denominator must remain 26")

    des_contract = _object(scope.get("des_contract"), "des_contract")
    expected_des: JsonObject = {
        "absolute_error_tolerance": "0.028340",
        "comparison_cell_count": 18,
        "familywise_delta": "0.05",
        "master_seed": 2026080601,
        "planned_replicates_per_case": 4096,
        "seed_derivation_rule": "sha256(master_seed:replication_index)",
    }
    if des_contract != expected_des:
        raise ValueError("des_contract differs from the frozen pre-outcome contract")
    return scope


def build_article_cases(repo_root: Path) -> tuple[ArticleCase, ...]:
    """Build the exact six cases after verifying every upstream identity."""

    scope = load_article_scope(repo_root)
    sealed_manifest = _verify_upstream_identities(repo_root, scope)
    cases_by_id = {
        case_id: _build_sealed_case(repo_root, sealed_manifest, case_id)
        for case_id in SEALED_CASE_IDS
    }
    bridge = _build_bridge_case(repo_root, scope)
    cases_by_id[bridge.case_id] = bridge
    cases = tuple(cases_by_id[case_id] for case_id in ARTICLE_CASE_IDS)
    if tuple(case.case_id for case in cases) != ARTICLE_CASE_IDS:
        raise ValueError("built article case order differs from the scope lock")
    return cases


def validate_article_case(case: ArticleCase) -> CaseCertificate:
    """Validate target partition, method assumptions, and absorption structure."""

    if not case.states or len(set(case.states)) != len(case.states):
        raise ValueError("states must be a nonempty unique registry")
    state_set = set(case.states)
    if case.initial_state not in state_set:
        raise ValueError("initial_state is absent from the state registry")

    target_sets = (
        case.d_global_states,
        case.d_local_states,
        case.completion_states,
    )
    if any(not set(target).issubset(state_set) for target in target_sets):
        raise ValueError("target class contains an unknown state")
    if (
        case.d_global_states & case.d_local_states
        or case.d_global_states & case.completion_states
        or case.d_local_states & case.completion_states
    ):
        raise ValueError("D_global, D_local, and F must be pairwise disjoint")
    if not case.local_candidate_states.issubset(state_set):
        raise ValueError("local candidate contains an unknown state")
    if not case.d_local_states.issubset(case.local_candidate_states):
        raise ValueError("every D_local state must be an explicit local candidate")
    if not case.a2b_verified_states.issubset(case.d_local_states):
        raise ValueError("A2b proof may only be attached to admitted D_local states")

    transition_keys: set[tuple[str, str, str]] = set()
    adjacency = {state: set[str]() for state in case.states}
    for transition in case.transitions:
        if transition.source not in state_set or transition.target not in state_set:
            raise ValueError("transition endpoint is absent from the state registry")
        if transition.source == transition.target:
            raise ValueError("plant transition self loops are not permitted")
        if not transition.rate.is_finite() or transition.rate <= 0:
            raise ValueError("every transition rate must be positive finite")
        key = (transition.source, transition.event, transition.target)
        if key in transition_keys:
            raise ValueError("duplicate plant transition identity")
        transition_keys.add(key)
        adjacency[transition.source].add(transition.target)

    completion_reachable = {
        state: _can_reach_any(state, case.completion_states, adjacency)
        for state in sorted(case.local_candidate_states)
    }
    dlocal_cannot_reach_completion = all(
        not _can_reach_any(state, case.completion_states, adjacency)
        for state in case.d_local_states
    )

    if case.admission_route == "A2b_request_closed":
        if case.a2b_verified_states != case.d_local_states:
            raise ValueError("every A2b-admitted D_local state needs an A2b proof")
    elif case.admission_route == "complete_LTS_nonreachability":
        if not case.lts_complete:
            raise ValueError("complete-LTS admission requires a complete LTS")
        if not dlocal_cannot_reach_completion:
            raise ValueError("completion reachable from complete-LTS D_local state")
    elif case.admission_route == "boundary_control_not_admitted":
        if case.d_local_states:
            raise ValueError("bypass boundary control must not admit D_local")
        if not completion_reachable or not all(completion_reachable.values()):
            raise ValueError("bypass boundary control must retain a path to completion")
    elif case.admission_route in {
        "time_zero_global",
        "global_precedence_control",
    }:
        if case.initial_state not in case.d_global_states:
            raise ValueError("global witness must start in D_global")
    else:
        raise ValueError(f"unknown article admission route {case.admission_route!r}")

    selected_targets = frozenset().union(*target_sets)
    for state in case.states:
        if state in selected_targets:
            continue
        if not _can_reach_any(state, selected_targets, adjacency):
            raise ValueError(f"state {state!r} cannot reach a selected absorbing class")

    stopped_transition_count = sum(
        transition.source not in selected_targets for transition in case.transitions
    )
    checks = {
        "a2b_request_closed_proof": (
            case.admission_route != "A2b_request_closed"
            or case.a2b_verified_states == case.d_local_states
        ),
        "complete_lts": case.lts_complete,
        "dlocal_cannot_reach_completion": dlocal_cannot_reach_completion,
        "global_precedence_no_double_count": not bool(
            case.d_global_states & case.d_local_states
        ),
        "pairwise_disjoint_target_partition": True,
        "positive_finite_rates": True,
        "selected_absorption_almost_sure": True,
        "stopped_process_separate_from_plant": True,
    }
    return CaseCertificate(
        case_id=case.case_id,
        source_role=case.source_role,
        source_path=case.source_path.as_posix() if case.source_path else None,
        source_sha256=case.source_sha256,
        admission_route=case.admission_route,
        d_global_states=tuple(sorted(case.d_global_states)),
        d_local_states=tuple(sorted(case.d_local_states)),
        completion_states=tuple(sorted(case.completion_states)),
        local_candidate_states=tuple(sorted(case.local_candidate_states)),
        completion_reachable_by_candidate=completion_reachable,
        plant_transition_count=len(case.transitions),
        stopped_transition_count=stopped_transition_count,
        checks=checks,
    )


def solve_article_case(case: ArticleCase) -> ExactFirstHitResult:
    """Solve the three stopped-process first-hit probabilities exactly in memory."""

    validate_article_case(case)
    target_union = case.d_global_states | case.d_local_states | case.completion_states
    if case.initial_state in target_union:
        probabilities = _time_zero_probabilities(case)
        return ExactFirstHitResult(
            case_id=case.case_id,
            probabilities=probabilities,
            mean_absorption_time=Decimal("0"),
            committor_residuals={estimand: Decimal("0") for estimand in ESTIMANDS},
            analytical_identity=None,
        )

    global_value, global_time, global_residual = _solve_binary_committor(
        case,
        desired_absorbers=case.d_global_states,
    )
    local_value, local_time, local_residual = _solve_binary_committor(
        case,
        desired_absorbers=case.d_local_states,
    )
    selected_value, selected_time, selected_residual = _solve_binary_committor(
        case,
        desired_absorbers=case.d_global_states | case.d_local_states,
    )
    if abs((global_value + local_value) - selected_value) > Decimal("1e-10"):
        raise ValueError("multiclass committors do not sum to the selected target")
    if max(global_time, local_time, selected_time) - min(
        global_time,
        local_time,
        selected_time,
    ) > Decimal("1e-10"):
        raise ValueError("binary reductions disagree on mean absorption time")

    return ExactFirstHitResult(
        case_id=case.case_id,
        probabilities={
            ESTIMANDS[0]: global_value,
            ESTIMANDS[1]: local_value,
            ESTIMANDS[2]: selected_value,
        },
        mean_absorption_time=selected_time,
        committor_residuals={
            ESTIMANDS[0]: global_residual,
            ESTIMANDS[1]: local_residual,
            ESTIMANDS[2]: selected_residual,
        },
        analytical_identity=(
            "1/3"
            if case.case_id == "g6b_article_bridge_competing_local_completion_v1"
            else None
        ),
    )


def derive_replication_seed(master_seed: int, replication_index: int) -> int:
    """Derive the frozen independent replication seed."""

    if isinstance(master_seed, bool) or not isinstance(master_seed, int):
        raise ValueError("master_seed must be an integer")
    if (
        isinstance(replication_index, bool)
        or not isinstance(replication_index, int)
        or replication_index < 0
    ):
        raise ValueError("replication_index must be a nonnegative integer")
    digest = sha256(f"{master_seed}:{replication_index}".encode("ascii")).digest()
    return int.from_bytes(digest, byteorder="big")


def simulate_article_case(
    case: ArticleCase,
    *,
    sample_count: int,
    master_seed: int,
) -> DesFirstHitResult:
    """Run the frozen multiclass Gillespie estimator without a retry path."""

    validate_article_case(case)
    if isinstance(sample_count, bool) or not isinstance(sample_count, int):
        raise ValueError("sample_count must be a positive integer")
    if sample_count <= 0:
        raise ValueError("sample_count must be a positive integer")

    counts = {target: 0 for target in TARGET_CLASSES}
    total_time = 0.0
    seed_digest = sha256()
    first_seed: int | None = None
    last_seed: int | None = None
    transitions_by_source = _transitions_by_source(case)
    for replication_index in range(sample_count):
        seed = derive_replication_seed(master_seed, replication_index)
        if first_seed is None:
            first_seed = seed
        last_seed = seed
        seed_digest.update(seed.to_bytes(32, byteorder="big"))
        absorbed_class, elapsed = _run_replication(
            case,
            transitions_by_source,
            seed,
        )
        counts[absorbed_class] += 1
        total_time += elapsed

    assert first_seed is not None and last_seed is not None
    global_probability = Decimal(counts["D_global"]) / Decimal(sample_count)
    local_probability = Decimal(counts["D_local"]) / Decimal(sample_count)
    return DesFirstHitResult(
        case_id=case.case_id,
        sample_count=sample_count,
        counts=counts,
        probabilities={
            ESTIMANDS[0]: global_probability,
            ESTIMANDS[1]: local_probability,
            ESTIMANDS[2]: global_probability + local_probability,
        },
        mean_absorption_time=Decimal(str(total_time / sample_count)),
        stream_manifest={
            "first_replication_seed": first_seed,
            "last_replication_seed": last_seed,
            "master_seed": master_seed,
            "replication_seed_digest": seed_digest.hexdigest(),
            "sample_count": sample_count,
            "seed_derivation": "sha256(master_seed:replication_index)",
        },
    )


def run_article_closure(repo_root: Path) -> ArticleClosureResult:
    """Run the full predeclared six-case closure in memory without writing."""

    scope = load_article_scope(repo_root)
    des_contract = _object(scope.get("des_contract"), "des_contract")
    sample_count = _integer(
        des_contract.get("planned_replicates_per_case"),
        "planned_replicates_per_case",
    )
    master_seed = _integer(des_contract.get("master_seed"), "master_seed")
    tolerance = Decimal(
        _string(des_contract.get("absolute_error_tolerance"), "tolerance")
    )

    cases = build_article_cases(repo_root)
    certificates = tuple(validate_article_case(case) for case in cases)
    exact_results = tuple(solve_article_case(case) for case in cases)
    des_results = tuple(
        simulate_article_case(
            case,
            sample_count=sample_count,
            master_seed=master_seed,
        )
        for case in cases
    )
    exact_by_case = {result.case_id: result for result in exact_results}
    des_by_case = {result.case_id: result for result in des_results}
    cells = tuple(
        _compatibility_cell(
            case_id,
            estimand,
            exact_by_case[case_id],
            des_by_case[case_id],
            tolerance,
        )
        for case_id in ARTICLE_CASE_IDS
        for estimand in ESTIMANDS
    )
    if len(cells) != _integer(
        des_contract.get("comparison_cell_count"),
        "comparison_cell_count",
    ):
        raise ValueError("comparison cell count differs from the scope lock")
    all_compatible = all(cell.compatible for cell in cells)
    tier = _select_claim_tier(certificates, cells, all_compatible)
    return ArticleClosureResult(
        case_ids=tuple(case.case_id for case in cases),
        certificates=certificates,
        exact_results=exact_results,
        des_results=des_results,
        compatibility_cells=cells,
        comparison_cell_count=len(cells),
        all_cells_compatible=all_compatible,
        claim_tier=tier,
        original_g6b_gate=ORIGINAL_G6B_GATE,
    )


def write_article_closure_evidence(
    repo_root: Path,
    *,
    output_root: Path | None = None,
) -> ArticleClosureResult:
    """Run once and write canonical evidence, with the manifest written last."""

    destination = output_root or (repo_root / DEFAULT_EVIDENCE_ROOT)
    try:
        destination.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise FileExistsError(
            f"write-once evidence root already exists: {destination}"
        ) from exc

    result = run_article_closure(repo_root)
    scope = load_article_scope(repo_root)
    scope_sha256 = _string(scope.get("scope_lock_sha256"), "scope_lock_sha256")

    records: tuple[tuple[str, JsonObject], ...] = (
        (
            "article_case_certificates.json",
            _finalize_artifact(
                {
                    "artifact_sha256": None,
                    "case_certificates": [
                        _certificate_json(certificate)
                        for certificate in result.certificates
                    ],
                    "schema_version": ("ims-deadlock/article-case-certificates/v1"),
                    "scope_lock_sha256": scope_sha256,
                }
            ),
        ),
        (
            "exact_results.json",
            _finalize_artifact(
                {
                    "artifact_sha256": None,
                    "exact_results": [
                        _exact_result_json(exact) for exact in result.exact_results
                    ],
                    "schema_version": "ims-deadlock/article-exact-results/v1",
                    "scope_lock_sha256": scope_sha256,
                }
            ),
        ),
        (
            "des_results.json",
            _finalize_artifact(
                {
                    "artifact_sha256": None,
                    "des_results": [
                        _des_result_json(des) for des in result.des_results
                    ],
                    "schema_version": "ims-deadlock/article-des-results/v1",
                    "scope_lock_sha256": scope_sha256,
                }
            ),
        ),
        (
            "article_closure_report.json",
            _finalize_artifact(
                {
                    "all_cells_compatible": result.all_cells_compatible,
                    "artifact_sha256": None,
                    "claim_tier": result.claim_tier,
                    "comparison_cell_count": result.comparison_cell_count,
                    "comparison_cells": [
                        _compatibility_json(cell) for cell in result.compatibility_cells
                    ],
                    "forbidden_claims_retained": True,
                    "original_g6b_gate": result.original_g6b_gate,
                    "schema_version": "ims-deadlock/article-closure-report/v1",
                    "scope_lock_sha256": scope_sha256,
                    "study_role": (
                        "scoped_constructive_theory_article_not_confirmation"
                    ),
                }
            ),
        ),
    )
    raw_hashes: JsonObject = {}
    for filename, record in records:
        raw_hashes[filename] = _write_json_artifact(destination / filename, record)

    manifest = _finalize_artifact(
        {
            "artifact_raw_sha256": raw_hashes,
            "artifact_sha256": None,
            "case_ids": list(result.case_ids),
            "claim_tier": result.claim_tier,
            "manifest_written_last": True,
            "original_g6b_gate": result.original_g6b_gate,
            "schema_version": "ims-deadlock/article-closure-manifest/v1",
            "scope_lock_sha256": scope_sha256,
        }
    )
    _write_json_artifact(destination / "article_closure_manifest.json", manifest)
    return result


def _verify_upstream_identities(repo_root: Path, scope: JsonObject) -> JsonObject:
    sealed_identity = _object(
        scope.get("sealed_bundle_identity"),
        "sealed_bundle_identity",
    )
    sealed_path = repo_root / SEALED_MANIFEST_PATH
    if _sha256_file(sealed_path) != _string(
        sealed_identity.get("manifest_raw_sha256"),
        "sealed manifest raw hash",
    ):
        raise ValueError("sealed bundle raw hash differs from the scope lock")
    sealed_manifest = _load_json_object(sealed_path)
    verify_finalized_self_hash(sealed_manifest, "manifest_sha256")
    if sealed_manifest.get("manifest_sha256") != sealed_identity.get(
        "manifest_self_sha256"
    ):
        raise ValueError("sealed bundle self hash differs from the scope lock")

    normalized_identity = _object(
        scope.get("retired_normalization_identity"),
        "retired_normalization_identity",
    )
    normalized_path = repo_root / NORMALIZATION_MANIFEST_PATH
    if _sha256_file(normalized_path) != _string(
        normalized_identity.get("manifest_raw_sha256"),
        "normalization manifest raw hash",
    ):
        raise ValueError("normalization raw hash differs from the scope lock")
    normalized_manifest = _load_json_object(normalized_path)
    verify_finalized_self_hash(normalized_manifest, "manifest_sha256")
    if normalized_manifest.get("manifest_sha256") != normalized_identity.get(
        "manifest_self_sha256"
    ):
        raise ValueError("normalization self hash differs from the scope lock")
    return sealed_manifest


def _build_sealed_case(
    repo_root: Path,
    sealed_manifest: JsonObject,
    case_id: str,
) -> ArticleCase:
    case_path = SEALED_BASE / case_id / "case_input.json"
    case_input = _load_json_object(repo_root / case_path)
    if case_input.get("case_unit_id") != case_id:
        raise ValueError(f"sealed case id mismatch for {case_id}")
    source_sha256 = _sha256_file(repo_root / case_path)
    record_hashes = _object(
        sealed_manifest.get("case_unit_record_hashes"),
        "case_unit_record_hashes",
    )
    if record_hashes.get(case_id) != source_sha256:
        raise ValueError(f"sealed case source hash mismatch for {case_id}")

    paths = _object(case_input.get("case_artifact_paths"), "case_artifact_paths")
    snapshot_path = Path(_string(paths.get("state_snapshot"), "state_snapshot path"))
    validate_repo_relative_posix_path(snapshot_path.as_posix())
    if _sha256_file(repo_root / snapshot_path) != _string(
        case_input.get("state_snapshot_sha256"),
        "state_snapshot_sha256",
    ):
        raise ValueError(f"state snapshot hash mismatch for {case_id}")
    snapshot = _load_json_object(repo_root / snapshot_path)
    payload = _object(snapshot.get("state_payload"), "state_payload")

    if case_id == "g6b_cu_pc_dglobal_only_v1":
        _validate_snapshot_flags(payload, calendar_empty=True, complete=False)
        return ArticleCase(
            case_id=case_id,
            source_role="sealed_constructive_witness",
            source_path=case_path,
            source_sha256=source_sha256,
            states=("s_initial",),
            initial_state="s_initial",
            transitions=(),
            d_global_states=frozenset({"s_initial"}),
            d_local_states=frozenset(),
            completion_states=frozenset(),
            local_candidate_states=frozenset(),
            a2b_verified_states=frozenset(),
            lts_complete=False,
            admission_route="time_zero_global",
            expected_boundary="D_global",
        )
    if case_id == "g6b_cu_nc_dglobal_only_with_dlocal_v1":
        _validate_snapshot_flags(payload, calendar_empty=True, complete=False)
        return ArticleCase(
            case_id=case_id,
            source_role="sealed_boundary_control",
            source_path=case_path,
            source_sha256=source_sha256,
            states=("s_initial",),
            initial_state="s_initial",
            transitions=(),
            d_global_states=frozenset({"s_initial"}),
            d_local_states=frozenset(),
            completion_states=frozenset(),
            local_candidate_states=frozenset({"s_initial"}),
            a2b_verified_states=frozenset(),
            lts_complete=False,
            admission_route="global_precedence_control",
            expected_boundary="D_global/no_double_count_through_D_local",
        )
    if case_id == "g6b_cu_pc_dlocal_a2b_single_kernel_v1":
        _validate_snapshot_flags(payload, calendar_empty=False, complete=False)
        return ArticleCase(
            case_id=case_id,
            source_role="sealed_constructive_witness",
            source_path=case_path,
            source_sha256=source_sha256,
            states=("s_initial",),
            initial_state="s_initial",
            transitions=(),
            d_global_states=frozenset(),
            d_local_states=frozenset({"s_initial"}),
            completion_states=frozenset(),
            local_candidate_states=frozenset({"s_initial"}),
            a2b_verified_states=frozenset({"s_initial"}),
            lts_complete=False,
            admission_route="A2b_request_closed",
            expected_boundary="D_local via A2b_proof",
        )

    states = _string_tuple(payload.get("states"), "states")
    initial_state = _string(payload.get("initial_state"), "initial_state")
    completion_states = frozenset(
        _string_tuple(payload.get("marked_states"), "marked_states")
    )
    rate_path = Path(_string(paths.get("rate_manifest"), "rate_manifest path"))
    validate_repo_relative_posix_path(rate_path.as_posix())
    rates = _load_rate_map(repo_root / rate_path)
    transitions = _load_transitions(payload.get("transitions"), rates)
    if case_id == "g6b_cu_pc_dlocal_lts_multi_kernel_v1":
        return ArticleCase(
            case_id=case_id,
            source_role="sealed_constructive_witness",
            source_path=case_path,
            source_sha256=source_sha256,
            states=states,
            initial_state=initial_state,
            transitions=transitions,
            d_global_states=frozenset(),
            d_local_states=frozenset({"dlocal_ab", "dlocal_cd"}),
            completion_states=completion_states,
            local_candidate_states=frozenset({"dlocal_ab", "dlocal_cd"}),
            a2b_verified_states=frozenset(),
            lts_complete=True,
            admission_route="complete_LTS_nonreachability",
            expected_boundary="D_local via complete-LTS audit",
        )
    if case_id == "g6b_cu_nc_local_bypass_completes_v1":
        return ArticleCase(
            case_id=case_id,
            source_role="sealed_boundary_control",
            source_path=case_path,
            source_sha256=source_sha256,
            states=states,
            initial_state=initial_state,
            transitions=transitions,
            d_global_states=frozenset(),
            d_local_states=frozenset(),
            completion_states=completion_states,
            local_candidate_states=frozenset({"s_local_candidate"}),
            a2b_verified_states=frozenset(),
            lts_complete=True,
            admission_route="boundary_control_not_admitted",
            expected_boundary="D_local_not_admitted/reachable_completion_bypass",
        )
    raise ValueError(f"unsupported sealed article case {case_id!r}")


def _build_bridge_case(repo_root: Path, scope: JsonObject) -> ArticleCase:
    path = repo_root / BRIDGE_CASE_PATH
    record = _load_json_object(path)
    verify_finalized_self_hash(record, "case_sha256")
    case_id = _string(record.get("case_id"), "bridge case_id")
    if case_id != ARTICLE_CASE_IDS[0]:
        raise ValueError("bridge case id differs from the scope lock")
    if record.get("target_semantics") != ("first_hit_D_global_or_D_local_or_F_v1"):
        raise ValueError("bridge target semantics differ from the scope lock")

    state_evidence = _list(record.get("state_evidence"), "state_evidence")
    states: list[str] = []
    d_global: set[str] = set()
    d_local: set[str] = set()
    completion: set[str] = set()
    candidates: set[str] = set()
    a2b_verified: set[str] = set()
    for raw_state in state_evidence:
        state = _object(raw_state, "state_evidence entry")
        state_id = _string(state.get("state_id"), "state_id")
        states.append(state_id)
        if state.get("global_deadlock") is True:
            d_global.add(state_id)
        if state.get("local_deadlock") is True:
            d_local.add(state_id)
        if state.get("completion") is True:
            completion.add(state_id)
        if state.get("local_candidate") is True:
            candidates.add(state_id)
        if state.get("a2b_request_closed_proof") is True:
            a2b_verified.add(state_id)

    transitions = _load_transitions(record.get("transitions"), rates=None)
    bridge_contract = _object(scope.get("bridge_case_contract"), "bridge contract")
    rate_by_event = {transition.event: transition.rate for transition in transitions}
    if rate_by_event != {
        "complete": Decimal(
            _string(bridge_contract.get("completion_rate"), "completion_rate")
        ),
        "enter_local": Decimal(
            _string(bridge_contract.get("local_hit_rate"), "local_hit_rate")
        ),
    }:
        raise ValueError("bridge rates differ from the frozen scope")

    return ArticleCase(
        case_id=case_id,
        source_role=_string(record.get("source_role"), "source_role"),
        source_path=BRIDGE_CASE_PATH,
        source_sha256=_sha256_file(path),
        states=tuple(states),
        initial_state=_string(record.get("initial_state"), "initial_state"),
        transitions=transitions,
        d_global_states=frozenset(d_global),
        d_local_states=frozenset(d_local),
        completion_states=frozenset(completion),
        local_candidate_states=frozenset(candidates),
        a2b_verified_states=frozenset(a2b_verified),
        lts_complete=True,
        admission_route=_string(
            record.get("theory_admission_route"),
            "theory_admission_route",
        ),
        expected_boundary="nontrivial D_local versus F first-hit bridge",
    )


def _load_rate_map(path: Path) -> dict[str, Decimal]:
    record = _load_json_object(path)
    entries = _list(record.get("event_rate_entries"), "event_rate_entries")
    result: dict[str, Decimal] = {}
    for raw_entry in entries:
        entry = _object(raw_entry, "rate entry")
        event = _string(entry.get("event_role"), "event_role")
        rate_text = _string(entry.get("canonical_rate"), "canonical_rate")
        validate_canonical_decimal_string(rate_text)
        if event in result:
            raise ValueError(f"duplicate rate entry for {event!r}")
        result[event] = Decimal(rate_text)
    return result


def _load_transitions(
    raw_transitions: JsonValue | None,
    rates: Mapping[str, Decimal] | None,
) -> tuple[ArticleTransition, ...]:
    transitions: list[ArticleTransition] = []
    for raw_transition in _list(raw_transitions, "transitions"):
        transition = _object(raw_transition, "transition")
        event_key = "event_kind" if "event_kind" in transition else "event"
        event = _string(transition.get(event_key), event_key)
        if rates is None:
            rate_text = _string(transition.get("rate"), "rate")
            validate_canonical_decimal_string(rate_text)
            rate = Decimal(rate_text)
        else:
            if event not in rates:
                raise ValueError(f"transition {event!r} has no declared rate")
            rate = rates[event]
        transitions.append(
            ArticleTransition(
                source=_string(transition.get("source"), "source"),
                event=event,
                target=_string(transition.get("target"), "target"),
                rate=rate,
            )
        )
    return tuple(transitions)


def _validate_snapshot_flags(
    payload: JsonObject,
    *,
    calendar_empty: bool,
    complete: bool,
) -> None:
    if payload.get("stable") is not True:
        raise ValueError("sealed snapshot must be stable")
    if payload.get("event_calendar_empty") is not calendar_empty:
        raise ValueError("sealed snapshot calendar flag differs from article role")
    if payload.get("complete") is not complete:
        raise ValueError("sealed snapshot completion flag differs from article role")


def _can_reach_any(
    start: str,
    targets: frozenset[str],
    adjacency: Mapping[str, set[str]],
) -> bool:
    if start in targets:
        return True
    seen: set[str] = set()
    stack = [start]
    while stack:
        state = stack.pop()
        if state in seen:
            continue
        seen.add(state)
        for target in sorted(adjacency.get(state, set())):
            if target in targets:
                return True
            if target not in seen:
                stack.append(target)
    return False


def _time_zero_probabilities(case: ArticleCase) -> dict[str, Decimal]:
    is_global = case.initial_state in case.d_global_states
    is_local = case.initial_state in case.d_local_states
    return {
        ESTIMANDS[0]: Decimal(int(is_global)),
        ESTIMANDS[1]: Decimal(int(is_local)),
        ESTIMANDS[2]: Decimal(int(is_global or is_local)),
    }


def _solve_binary_committor(
    case: ArticleCase,
    *,
    desired_absorbers: frozenset[str],
) -> tuple[Decimal, Decimal, Decimal]:
    all_absorbers = case.d_global_states | case.d_local_states | case.completion_states
    transient_states = tuple(
        state for state in case.states if state not in all_absorbers
    )
    transient_rates: dict[tuple[str, str], float] = {}
    deadlock_rates: dict[tuple[str, str], float] = {}
    completion_rates: dict[tuple[str, str], float] = {}
    for transition in case.transitions:
        if transition.source in all_absorbers:
            continue
        rate = float(transition.rate)
        key = (transition.source, transition.target)
        if transition.target in desired_absorbers:
            deadlock_rates[key] = deadlock_rates.get(key, 0.0) + rate
        elif transition.target in all_absorbers:
            completion_rates[key] = completion_rates.get(key, 0.0) + rate
        else:
            transient_rates[key] = transient_rates.get(key, 0.0) + rate
    ctmc = AbsorbingCTMC(
        transient_states=transient_states,
        completion_rates=completion_rates,
        deadlock_rates=deadlock_rates,
        transient_rates=transient_rates,
        generator_provenance="article_case_derived_stopped_ctmc_v1",
        case_derived=True,
    )
    result = ctmc.solve()
    return (
        Decimal(str(result.deadlock_probability[case.initial_state])),
        Decimal(str(result.mean_absorption_time[case.initial_state])),
        Decimal(str(result.committor_residual_inf_norm)),
    )


def _transitions_by_source(
    case: ArticleCase,
) -> dict[str, tuple[ArticleTransition, ...]]:
    result: dict[str, tuple[ArticleTransition, ...]] = {}
    for state in case.states:
        result[state] = tuple(
            sorted(
                (
                    transition
                    for transition in case.transitions
                    if transition.source == state
                ),
                key=lambda transition: (
                    transition.event,
                    transition.target,
                    transition.rate,
                ),
            )
        )
    return result


def _run_replication(
    case: ArticleCase,
    transitions_by_source: Mapping[str, tuple[ArticleTransition, ...]],
    seed: int,
) -> tuple[str, float]:
    rng = Random(seed)
    current = case.initial_state
    elapsed = 0.0
    for _step in range(1_000_000):
        absorbed = _absorbed_class(case, current)
        if absorbed is not None:
            return absorbed, elapsed
        transitions = transitions_by_source[current]
        total_rate = sum(float(transition.rate) for transition in transitions)
        if not isfinite(total_rate) or total_rate <= 0.0:
            raise ValueError(f"state {current!r} has no positive finite outgoing rate")
        elapsed += rng.expovariate(total_rate)
        threshold = rng.random() * total_rate
        cumulative = 0.0
        selected = transitions[-1]
        for transition in transitions:
            cumulative += float(transition.rate)
            if threshold < cumulative:
                selected = transition
                break
        current = selected.target
    raise RuntimeError("DES step limit exceeded despite absorption validation")


def _absorbed_class(case: ArticleCase, state: str) -> str | None:
    if state in case.d_global_states:
        return "D_global"
    if state in case.d_local_states:
        return "D_local"
    if state in case.completion_states:
        return "F"
    return None


def _compatibility_cell(
    case_id: str,
    estimand: str,
    exact: ExactFirstHitResult,
    des: DesFirstHitResult,
    tolerance: Decimal,
) -> CompatibilityCell:
    exact_value = exact.probabilities[estimand]
    des_value = des.probabilities[estimand]
    error = abs(des_value - exact_value)
    return CompatibilityCell(
        case_id=case_id,
        estimand=estimand,
        exact=exact_value,
        des=des_value,
        absolute_error=error,
        tolerance=tolerance,
        compatible=error <= tolerance,
    )


def _select_claim_tier(
    certificates: tuple[CaseCertificate, ...],
    cells: tuple[CompatibilityCell, ...],
    all_compatible: bool,
) -> str:
    certificate_by_case = {
        certificate.case_id: certificate for certificate in certificates
    }
    a2b = certificate_by_case["g6b_cu_pc_dlocal_a2b_single_kernel_v1"]
    lts = certificate_by_case["g6b_cu_pc_dlocal_lts_multi_kernel_v1"]
    bridge = certificate_by_case["g6b_article_bridge_competing_local_completion_v1"]
    precedence = certificate_by_case["g6b_cu_nc_dglobal_only_with_dlocal_v1"]
    bypass = certificate_by_case["g6b_cu_nc_local_bypass_completes_v1"]
    controls_pass = (
        precedence.checks["global_precedence_no_double_count"]
        and precedence.checks["pairwise_disjoint_target_partition"]
        and not precedence.d_local_states
        and bypass.checks["pairwise_disjoint_target_partition"]
        and not bypass.d_local_states
        and bool(bypass.completion_reachable_by_candidate)
        and all(bypass.completion_reachable_by_candidate.values())
    )
    bridge_compatible = all(
        cell.compatible for cell in cells if cell.case_id == bridge.case_id
    )
    a2b_pass = a2b.checks["a2b_request_closed_proof"]
    lts_pass = (
        lts.checks["complete_lts"] and lts.checks["dlocal_cannot_reach_completion"]
    )
    lts_bridge_available = (
        bridge.checks["complete_lts"]
        and bridge.checks["dlocal_cannot_reach_completion"]
    )
    common = controls_pass and bridge_compatible and all_compatible
    if common and a2b_pass and lts_pass:
        return "tier_a_dual_route_closure"
    if common and a2b_pass:
        return "tier_b_a2b_only_closure"
    if common and lts_pass and lts_bridge_available:
        return "tier_b_lts_only_closure"
    return "tier_c_no_local_method_article_closure"


def _certificate_json(certificate: CaseCertificate) -> JsonObject:
    return {
        "admission_route": certificate.admission_route,
        "case_id": certificate.case_id,
        "checks": _json_bool_map(certificate.checks),
        "completion_reachable_by_candidate": _json_bool_map(
            certificate.completion_reachable_by_candidate
        ),
        "completion_states": list(certificate.completion_states),
        "d_global_states": list(certificate.d_global_states),
        "d_local_states": list(certificate.d_local_states),
        "local_candidate_states": list(certificate.local_candidate_states),
        "plant_transition_count": certificate.plant_transition_count,
        "source_path": certificate.source_path,
        "source_role": certificate.source_role,
        "source_sha256": certificate.source_sha256,
        "stopped_transition_count": certificate.stopped_transition_count,
    }


def _exact_result_json(result: ExactFirstHitResult) -> JsonObject:
    return {
        "analytical_identity": result.analytical_identity,
        "case_id": result.case_id,
        "committor_residuals": {
            key: _decimal_text(value)
            for key, value in result.committor_residuals.items()
        },
        "mean_absorption_time": _decimal_text(result.mean_absorption_time),
        "probabilities": {
            key: _decimal_text(value) for key, value in result.probabilities.items()
        },
    }


def _des_result_json(result: DesFirstHitResult) -> JsonObject:
    return {
        "case_id": result.case_id,
        "counts": _json_int_map(result.counts),
        "mean_absorption_time": _decimal_text(result.mean_absorption_time),
        "probabilities": {
            key: _decimal_text(value) for key, value in result.probabilities.items()
        },
        "sample_count": result.sample_count,
        "stream_manifest": result.stream_manifest,
    }


def _compatibility_json(cell: CompatibilityCell) -> JsonObject:
    return {
        "absolute_error": _decimal_text(cell.absolute_error),
        "case_id": cell.case_id,
        "compatible": cell.compatible,
        "des": _decimal_text(cell.des),
        "estimand": cell.estimand,
        "exact": _decimal_text(cell.exact),
        "tolerance": _decimal_text(cell.tolerance),
    }


def _json_bool_map(values: Mapping[str, bool]) -> JsonObject:
    result: JsonObject = {}
    for key, value in values.items():
        result[key] = value
    return result


def _json_int_map(values: Mapping[str, int]) -> JsonObject:
    result: JsonObject = {}
    for key, value in values.items():
        result[key] = value
    return result


def _finalize_artifact(record: JsonObject) -> JsonObject:
    record["artifact_sha256"] = finalized_self_hash(record, "artifact_sha256")
    return record


def _write_json_artifact(path: Path, record: JsonObject) -> str:
    raw = canonical_bytes_v2(record)
    path.write_bytes(raw)
    return sha256(raw).hexdigest()


def _decimal_text(value: Decimal) -> str:
    if not value.is_finite():
        raise ValueError("nonfinite decimal cannot enter article evidence")
    if value.is_zero():
        return "0"
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    validate_canonical_decimal_string(text)
    return text


def _load_json_object(path: Path) -> JsonObject:
    value = loads_v2(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object at {path}")
    return value


def _sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _object(value: JsonValue | object, label: str) -> JsonObject:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return cast(JsonObject, value)


def _list(value: JsonValue | object, label: str) -> list[JsonValue]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    return cast(list[JsonValue], value)


def _string(value: JsonValue | object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a nonempty string")
    return value


def _string_tuple(value: JsonValue | object, label: str) -> tuple[str, ...]:
    return tuple(_string(item, label) for item in _list(value, label))


def _integer(value: JsonValue | object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    return value


def main(argv: Sequence[str] | None = None) -> int:
    """CLI for a no-write preflight or one write-once evidence execution."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args(argv)
    repo_root = cast(Path, args.repo_root).resolve()
    if cast(bool, args.preflight):
        result = run_article_closure(repo_root)
    else:
        output_root = cast(Path | None, args.output_root)
        result = write_article_closure_evidence(
            repo_root,
            output_root=output_root,
        )
    summary: JsonObject = {
        "all_cells_compatible": result.all_cells_compatible,
        "case_ids": list(result.case_ids),
        "claim_tier": result.claim_tier,
        "comparison_cell_count": result.comparison_cell_count,
        "original_g6b_gate": result.original_g6b_gate,
    }
    print(canonical_bytes_v2(summary).decode("utf-8"))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through the CLI
    raise SystemExit(main())
