# G6-B Row-Family Protocol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement an execution-disabled, machine-auditable G6-B row-family
protocol bundle and pure data validator without creating discovery cases or
running scientific computation.

**Architecture:** Keep the existing exact-five G6-B foundation bundle
unchanged. Add an exact-eight nested bundle at
`cases/discovery/g6b/row_families/structural_discovery_v1/`, validate it with a
stdlib-only module, and fail closed on path, schema, ontology, identity,
independence, control, scoring, ledger, review-state, or authorization drift.
The implementation may define schemas for later evidence, but it cannot
materialize cases, actual overlap results, current locks, outputs, or science.

**Tech Stack:** Python 3.13, stdlib `dataclasses`/`hashlib`/`json`/`pathlib`,
pytest, Ruff, strict mypy, Git.

---

## Frozen Scope And Stop Boundary

Approved design:
`docs/superpowers/specs/2026-07-31-g6b-row-family-design.md` at feature-branch
commit `c00812c790111b9debdc23deefa484c4b2362aa6`.

This plan may create or modify only:

- `cases/discovery/g6b/row_families/structural_discovery_v1/*.json`;
- `src/ims_deadlock/g6b_row_family_protocol.py`;
- `tests/test_g6b_row_family_protocol.py`;
- `docs/superpowers/specs/2026-07-31-g6b-row-family-design.md`;
- `docs/superpowers/plans/2026-07-31-g6b-row-family-protocol.md`;
- `docs/cases/CASE_CHANGE_LEDGER.md`;
- `docs/ROADMAP.md`;
- `PROJECT_HANDOFF.md`;
- `docs/verification/G6_B_ROW_FAMILY_PROTOCOL_REVIEW.md`.

This plan must stop before:

- discovery-case or `CaseSpec` creation;
- state enumeration or LTS generation;
- CTMC construction/solve;
- DES or random-number generation;
- output-root creation or output inspection;
- actual overlap values;
- a current overlap-authority or execution-runtime lock;
- `adversarial_review_status = PASSED`;
- `case_creation_authorized = true`;
- `scientific_execution_authorized = true`;
- G6-B `PASS` or any G6-C/D/E progress.

## Execution Target, Runtime, And Shell Lock

Run implementation and watched verification in the visible Remote-SSH
PowerShell terminal. Do not run the plan from the local bootstrap snapshot,
from `D:\py_pro\IMS_deadlock`, or from another worktree. Before Task 1, execute
this exact preflight:

```powershell
$Repo = "D:\worktree\IMS_deadlock-g6b-discovery"
$Python = (
  "D:\worktree\IMS_deadlock-final-integration\.venv\" +
  "Scripts\python.exe"
)
Set-Location -LiteralPath $Repo
$Top = (& git rev-parse --show-toplevel).Trim()
$Branch = (& git branch --show-current).Trim()
$Head = (& git rev-parse HEAD).Trim()
$Origin = (& git remote get-url origin).Trim()
$CommonDir = (& git rev-parse --git-common-dir).Trim()
$GitDir = (& git rev-parse --git-dir).Trim()
$Worktrees = @(& git worktree list --porcelain)
$Dirty = @(& git status --porcelain=v1)
if ($Top -ne "D:/worktree/IMS_deadlock-g6b-discovery") {
  throw "wrong worktree: $Top"
}
if ($Branch -ne "codex/g6b-discovery-estimand-lock") {
  throw "wrong branch: $Branch"
}
if ($Origin -ne "git@github.com:zjqc/IMS_deadlock.git") {
  throw "wrong origin: $Origin"
}
if ($CommonDir -ne "D:/py_pro/IMS_deadlock/.git") {
  throw "wrong Git common dir: $CommonDir"
}
if (
  $GitDir -ne (
    "D:/py_pro/IMS_deadlock/.git/worktrees/" +
    "IMS_deadlock-g6b-discovery"
  )
) {
  throw "wrong Git worktree identity: $GitDir"
}
if (
  $Worktrees -notcontains (
    "worktree D:/worktree/IMS_deadlock-g6b-discovery"
  )
) {
  throw "locked worktree is absent from git worktree list"
}
if ($Dirty.Count -ne 0) {
  throw "worktree must be clean before Task 1"
}
& git merge-base --is-ancestor `
  c00812c790111b9debdc23deefa484c4b2362aa6 $Head
if ($LASTEXITCODE -ne 0) {
  throw "approved design commit is not an ancestor of HEAD"
}
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
  throw "qualified Python is missing: $Python"
}
$env:PYTHONPATH = Join-Path $Repo "src"
$env:PYTHONDONTWRITEBYTECODE = "1"
$Version = (& $Python -c "import platform; print(platform.python_version())").Trim()
if ($Version -ne "3.13.9") {
  throw "unexpected Python version: $Version"
}
$Imported = (
  & $Python -c (
    "import ims_deadlock, pathlib; " +
    "print(pathlib.Path(ims_deadlock.__file__).resolve())"
  )
).Trim()
if (-not $Imported.StartsWith("$Repo\src\ims_deadlock\")) {
  throw "PYTHONPATH did not select the locked worktree: $Imported"
}
$UpstreamRaw = @(
  & git rev-parse --abbrev-ref --symbolic-full-name `
    '@{upstream}' 2>$null
)
if ($LASTEXITCODE -eq 0) {
  $Upstream = ($UpstreamRaw -join "").Trim()
  $Counts = (
    & git rev-list --left-right --count "HEAD...${Upstream}"
  ).Trim() -split "\s+"
  if ($Counts.Count -ne 2) {
    throw "unexpected ahead/behind result: $Counts"
  }
  $Ahead = $Counts[0]
  $Behind = $Counts[1]
} else {
  $Upstream = "NO_UPSTREAM"
  $Ahead = "NOT_APPLICABLE"
  $Behind = "NOT_APPLICABLE"
}
```

Record `$Top`, `$Branch`, `$Head`, `$Origin`, `$CommonDir`, `$GitDir`, the
matching worktree-list entry, the empty dirty-state result, `$Upstream`,
`$Ahead`, `$Behind`, `$Python`, `$Version`, and `$Imported`. If no upstream
exists live, the only valid record is `NO_UPSTREAM` with both counts marked
`NOT_APPLICABLE`; do not infer counts. All later command blocks use this same
PowerShell session and absolute `$Python`; never substitute bare `python`, `py`,
an activated environment, or a PATH-selected executable. Re-run the repository
identity, worktree identity, branch, ancestry, upstream, runtime, and
source-import checks immediately before Task 8 full verification, allowing only
the task-owned uncommitted state files expected at that point.

## Public API And Schema Versions

The implementation must expose exactly:

```python
G6B_ROW_FAMILY_PROTOCOL_VERSION = "ims-deadlock/g6b-row-family-protocol/v1"
G6B_ROW_FAMILY_IDENTITY_VERSION = "ims-deadlock/g6b-row-family-identity/v1"
G6B_ROW_FAMILY_MATRIX_VERSION = "ims-deadlock/g6b-row-family-matrix/v1"
G6B_ROW_FAMILY_REUSE_VERSION = "ims-deadlock/g6b-row-family-reuse/v1"
G6B_ROW_FAMILY_OVERLAP_VERSION = "ims-deadlock/g6b-row-family-overlap-schema/v1"
G6B_ROW_FAMILY_RUNTIME_LOCK_VERSION = (
    "ims-deadlock/g6b-row-family-runtime-lock-schema/v1"
)
G6B_ROW_FAMILY_REVIEW_STATE_VERSION = (
    "ims-deadlock/g6b-row-family-review-state/v1"
)
G6B_ROW_FAMILY_FAILURE_LEDGER_VERSION = (
    "ims-deadlock/g6b-row-family-failure-ledger/v1"
)


@dataclass(frozen=True)
class G6BRowFamilyValidation:
    valid: bool
    errors: tuple[str, ...]
    scientific_execution_authorized: bool
    case_creation_authorized: bool
    adversarial_review_status: str
    review_state: str
    bundle_hashes: dict[str, str]


def validate_g6b_row_family_bundle(root: Path) -> G6BRowFamilyValidation:
    """Validate the nested G6-B row-family protocol without science."""
```

The nested bundle must contain exactly:

```python
_DOCUMENTS = (
    "row_family_protocol.json",
    "identity_schema.json",
    "row_family_matrix.json",
    "reuse_matrix.json",
    "overlap_report_schema.json",
    "runtime_lock_schema.json",
    "review_state.json",
    "failure_ledger.json",
)
```

## Task 1: Create The Exact-Eight Disabled Bundle And Canonical Result

**Files:**

- Create:
  `cases/discovery/g6b/row_families/structural_discovery_v1/row_family_protocol.json`
- Create:
  `cases/discovery/g6b/row_families/structural_discovery_v1/identity_schema.json`
- Create:
  `cases/discovery/g6b/row_families/structural_discovery_v1/row_family_matrix.json`
- Create:
  `cases/discovery/g6b/row_families/structural_discovery_v1/reuse_matrix.json`
- Create:
  `cases/discovery/g6b/row_families/structural_discovery_v1/overlap_report_schema.json`
- Create:
  `cases/discovery/g6b/row_families/structural_discovery_v1/runtime_lock_schema.json`
- Create:
  `cases/discovery/g6b/row_families/structural_discovery_v1/review_state.json`
- Create:
  `cases/discovery/g6b/row_families/structural_discovery_v1/failure_ledger.json`
- Create: `src/ims_deadlock/g6b_row_family_protocol.py`
- Create: `tests/test_g6b_row_family_protocol.py`

- [x] **Step 1: Write the canonical-bundle test before the module exists**

```python
from pathlib import Path

from ims_deadlock.g6b_row_family_protocol import (
    validate_g6b_row_family_bundle,
)

BUNDLE = Path(
    "cases/discovery/g6b/row_families/structural_discovery_v1"
)


def test_canonical_bundle_loads_disabled_before_semantic_validation() -> None:
    result = validate_g6b_row_family_bundle(BUNDLE)

    assert result.valid is False
    assert result.errors == ("semantic validation incomplete",)
    assert result.scientific_execution_authorized is False
    assert result.case_creation_authorized is False
    assert result.adversarial_review_status == "PENDING"
    assert result.review_state == "ROW_FAMILY_BUNDLE_IMPLEMENTED"
    assert set(result.bundle_hashes) == {
        "row_family_protocol.json",
        "identity_schema.json",
        "row_family_matrix.json",
        "reuse_matrix.json",
        "overlap_report_schema.json",
        "runtime_lock_schema.json",
        "review_state.json",
        "failure_ledger.json",
    }
```

- [x] **Step 2: Run the test and record RED**

Run:

```powershell
& $Python -m pytest -p no:cacheprovider -q `
  tests/test_g6b_row_family_protocol.py::test_canonical_bundle_loads_disabled_before_semantic_validation
```

Expected: collection fails with
`ModuleNotFoundError: No module named 'ims_deadlock.g6b_row_family_protocol'`.

- [x] **Step 3: Add the frozen result type, exact document list, duplicate-key loader, and canonical hash**

```python
"""Data-only validation for the G6-B row-family protocol bundle."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

JsonObject: TypeAlias = dict[str, Any]
G6B_ROW_FAMILY_PROTOCOL_VERSION = "ims-deadlock/g6b-row-family-protocol/v1"
G6B_ROW_FAMILY_IDENTITY_VERSION = "ims-deadlock/g6b-row-family-identity/v1"
G6B_ROW_FAMILY_MATRIX_VERSION = "ims-deadlock/g6b-row-family-matrix/v1"
G6B_ROW_FAMILY_REUSE_VERSION = "ims-deadlock/g6b-row-family-reuse/v1"
G6B_ROW_FAMILY_OVERLAP_VERSION = (
    "ims-deadlock/g6b-row-family-overlap-schema/v1"
)
G6B_ROW_FAMILY_RUNTIME_LOCK_VERSION = (
    "ims-deadlock/g6b-row-family-runtime-lock-schema/v1"
)
G6B_ROW_FAMILY_REVIEW_STATE_VERSION = (
    "ims-deadlock/g6b-row-family-review-state/v1"
)
G6B_ROW_FAMILY_FAILURE_LEDGER_VERSION = (
    "ims-deadlock/g6b-row-family-failure-ledger/v1"
)
_DOCUMENTS = (
    "row_family_protocol.json",
    "identity_schema.json",
    "row_family_matrix.json",
    "reuse_matrix.json",
    "overlap_report_schema.json",
    "runtime_lock_schema.json",
    "review_state.json",
    "failure_ledger.json",
)


@dataclass(frozen=True)
class G6BRowFamilyValidation:
    valid: bool
    errors: tuple[str, ...]
    scientific_execution_authorized: bool
    case_creation_authorized: bool
    adversarial_review_status: str
    review_state: str
    bundle_hashes: dict[str, str]


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> JsonObject:
    result: JsonObject = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_json_object(path: Path) -> JsonObject:
    try:
        loaded = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(str(exc)) from exc
    if not isinstance(loaded, dict):
        raise ValueError("root must be a JSON object")
    return loaded


def _canonical_sha256(document: JsonObject) -> str:
    payload = json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
```

- [x] **Step 4a: Create `row_family_protocol.json`**

Use `ROW_FAMILY_PROTOCOL` from Canonical Document Appendix A field-for-field.

- [x] **Step 4b: Create `identity_schema.json`**

Use `IDENTITY_SCHEMA` from Canonical Document Appendix A field-for-field.

- [x] **Step 4c: Create `row_family_matrix.json`**

Use `ROW_FAMILY_MATRIX` from Canonical Document Appendix A field-for-field.

- [x] **Step 4d: Create `reuse_matrix.json`**

Use `REUSE_MATRIX` from Canonical Document Appendix A field-for-field.

- [x] **Step 4e: Create `overlap_report_schema.json`**

Use `OVERLAP_REPORT_SCHEMA` from Canonical Document Appendix A field-for-field.

- [x] **Step 4f: Create `runtime_lock_schema.json`**

Use `RUNTIME_LOCK_SCHEMA` from Canonical Document Appendix A field-for-field.

- [x] **Step 4g: Create `review_state.json`**

Use `REVIEW_STATE` from Canonical Document Appendix A field-for-field.

- [x] **Step 4h: Create `failure_ledger.json`**

Use `FAILURE_LEDGER` from Canonical Document Appendix A field-for-field.

- [x] **Step 5: Implement the minimal orchestrating validator**

```python
def validate_g6b_row_family_bundle(root: Path) -> G6BRowFamilyValidation:
    bundle_root = root.resolve()
    errors: list[str] = []
    documents: dict[str, JsonObject] = {}
    hashes: dict[str, str] = {}
    actual = sorted(
        path.name for path in bundle_root.glob("*.json") if path.is_file()
    )
    missing = sorted(set(_DOCUMENTS) - set(actual))
    unexpected = sorted(set(actual) - set(_DOCUMENTS))
    if missing:
        errors.append(f"missing JSON documents: {missing}")
    if unexpected:
        errors.append(f"unexpected JSON documents: {unexpected}")
    for name in _DOCUMENTS:
        if name in missing:
            continue
        try:
            document = _load_json_object(bundle_root / name)
        except ValueError as exc:
            errors.append(f"{name}: {exc}")
            continue
        documents[name] = document
        hashes[name] = _canonical_sha256(document)
    protocol = documents.get("row_family_protocol.json", {})
    review = documents.get("review_state.json", {})
    if set(documents) == set(_DOCUMENTS):
        errors.append("semantic validation incomplete")
    return G6BRowFamilyValidation(
        valid=not errors,
        errors=tuple(errors),
        scientific_execution_authorized=any(
            item.get("scientific_execution_authorized") is True
            for item in documents.values()
        ),
        case_creation_authorized=any(
            item.get("case_creation_authorized") is True
            for item in documents.values()
        ),
        adversarial_review_status=str(
            protocol.get("adversarial_review_status", "")
        ),
        review_state=str(review.get("current_state", "")),
        bundle_hashes=hashes,
    )
```

- [x] **Step 6: Run the load-only test and record GREEN**

Run:

```powershell
& $Python -m pytest -p no:cacheprovider -q `
  tests/test_g6b_row_family_protocol.py::test_canonical_bundle_loads_disabled_before_semantic_validation
```

Expected: `1 passed`. This proves loading and disabled-status reporting only;
the canonical result remains invalid until Task 6 closes all semantic checks.

- [x] **Step 7: Commit**

```powershell
git add cases/discovery/g6b/row_families/structural_discovery_v1 `
  src/ims_deadlock/g6b_row_family_protocol.py `
  tests/test_g6b_row_family_protocol.py
git commit -m "test: scaffold disabled G6-B row-family bundle"
```

## Task 2: Fail Closed On Files, Paths, Keys, And Authorization

**Files:**

- Modify: `src/ims_deadlock/g6b_row_family_protocol.py`
- Modify: `tests/test_g6b_row_family_protocol.py`

- [x] **Step 1: Add mutation helpers and RED tests**

```python
import json
import shutil
from pathlib import Path
from typing import Any

import pytest

_NAMES = (
    "row_family_protocol.json",
    "identity_schema.json",
    "row_family_matrix.json",
    "reuse_matrix.json",
    "overlap_report_schema.json",
    "runtime_lock_schema.json",
    "review_state.json",
    "failure_ledger.json",
)


def _copy_bundle(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    target = (
        repo
        / "cases/discovery/g6b/row_families/structural_discovery_v1"
    )
    shutil.copytree(BUNDLE, target)
    design = Path(
        "docs/superpowers/specs/2026-07-31-g6b-row-family-design.md"
    )
    copied_design = repo / design
    copied_design.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(design, copied_design)
    return target


def _load(bundle: Path, name: str) -> dict[str, Any]:
    loaded = json.loads((bundle / name).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _write(bundle: Path, name: str, value: dict[str, Any]) -> None:
    (bundle / name).write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)
        + "\n",
        encoding="utf-8",
    )


def _assert_invalid(bundle: Path, text: str) -> None:
    result = validate_g6b_row_family_bundle(bundle)
    assert result.valid is False
    assert any(text in error for error in result.errors), result.errors


@pytest.mark.parametrize("name", _NAMES)
def test_missing_document_is_rejected(tmp_path: Path, name: str) -> None:
    bundle = _copy_bundle(tmp_path)
    (bundle / name).unlink()
    _assert_invalid(bundle, f"missing JSON documents: ['{name}']")


def test_copied_noncanonical_root_is_rejected(tmp_path: Path) -> None:
    floating = tmp_path / "floating"
    shutil.copytree(BUNDLE, floating)
    _assert_invalid(
        floating,
        "bundle root must be <repo>/cases/discovery/g6b/row_families/"
        "structural_discovery_v1",
    )


@pytest.mark.parametrize(
    "field", ["scientific_execution_authorized", "case_creation_authorized"]
)
def test_true_authorization_is_rejected(
    tmp_path: Path, field: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, "row_family_protocol.json")
    value[field] = True
    _write(bundle, "row_family_protocol.json", value)
    _assert_invalid(bundle, f"{field} must be false")
```

- [x] **Step 2: Run the new tests and record RED**

Run:

```powershell
& $Python -m pytest -p no:cacheprovider -q `
  tests/test_g6b_row_family_protocol.py -k `
  "missing_document or noncanonical_root or true_authorization"
```

Expected: failures because canonical layout, exact keys, common status, and
cross-document authorization are not yet validated.

- [x] **Step 3: Implement canonical-root, exact-key, and common-contract helpers**

```python
_RELATIVE_ROOT = Path(
    "cases/discovery/g6b/row_families/structural_discovery_v1"
)
_COMMON_KEYS = {
    "schema_version",
    "study_role",
    "confirmation_use",
    "scientific_execution_authorized",
    "case_creation_authorized",
}


def _repo_root_for(bundle_root: Path) -> Path | None:
    parts = _RELATIVE_ROOT.parts
    if tuple(bundle_root.parts[-len(parts) :]) != parts:
        return None
    return bundle_root.parents[len(parts) - 1]


def _expect(
    condition: bool, message: str, errors: list[str]
) -> None:
    if not condition:
        errors.append(message)


def _exact_keys(
    document: JsonObject,
    expected: set[str],
    label: str,
    errors: list[str],
) -> None:
    missing = sorted(expected - set(document))
    extra = sorted(set(document) - expected)
    if missing:
        errors.append(f"{label}: missing keys: {missing}")
    if extra:
        errors.append(f"{label}: unexpected keys: {extra}")


def _expect_exact_document(
    actual: JsonObject,
    expected: JsonObject,
    label: str,
    errors: list[str],
) -> None:
    if actual != expected:
        errors.append(f"{label}: document must match the canonical contract")


def _common_contract(
    document: JsonObject,
    label: str,
    schema_version: str,
    errors: list[str],
) -> None:
    _expect(
        document.get("schema_version") == schema_version,
        f"{label}: wrong schema_version",
        errors,
    )
    _expect(
        document.get("study_role") == "discovery_only",
        f"{label}: study_role must be discovery_only",
        errors,
    )
    _expect(
        document.get("confirmation_use") == "prohibited",
        f"{label}: confirmation_use must be prohibited",
        errors,
    )
    _expect(
        document.get("scientific_execution_authorized") is False,
        f"{label}: scientific_execution_authorized must be false",
        errors,
    )
    _expect(
        document.get("case_creation_authorized") is False,
        f"{label}: case_creation_authorized must be false",
        errors,
    )
```

`_repo_root_for` must return `None` for every noncanonical copy and must never
use `Path.cwd()`. Define `_EXPECTED_ROW_FAMILY_PROTOCOL` from Appendix A and
validate `row_family_protocol.json` with `_expect_exact_document` in this task.
Replace the Task 1 sentinel insertion with this orchestration:

```python
_SCHEMA_VERSIONS = {
    "row_family_protocol.json": G6B_ROW_FAMILY_PROTOCOL_VERSION,
    "identity_schema.json": G6B_ROW_FAMILY_IDENTITY_VERSION,
    "row_family_matrix.json": G6B_ROW_FAMILY_MATRIX_VERSION,
    "reuse_matrix.json": G6B_ROW_FAMILY_REUSE_VERSION,
    "overlap_report_schema.json": G6B_ROW_FAMILY_OVERLAP_VERSION,
    "runtime_lock_schema.json": G6B_ROW_FAMILY_RUNTIME_LOCK_VERSION,
    "review_state.json": G6B_ROW_FAMILY_REVIEW_STATE_VERSION,
    "failure_ledger.json": G6B_ROW_FAMILY_FAILURE_LEDGER_VERSION,
}

if set(documents) == set(_DOCUMENTS):
    repo_root = _repo_root_for(bundle_root)
    if repo_root is None:
        errors.append(
            "bundle root must be <repo>/cases/discovery/g6b/"
            "row_families/structural_discovery_v1"
        )
    elif not (
        repo_root
        / "docs/superpowers/specs/2026-07-31-g6b-row-family-design.md"
    ).is_file():
        errors.append("source design path is missing")
    for name, version in _SCHEMA_VERSIONS.items():
        _common_contract(documents[name], name, version, errors)
    _expect_exact_document(
        documents["row_family_protocol.json"],
        _EXPECTED_ROW_FAMILY_PROTOCOL,
        "row_family_protocol.json",
        errors,
    )
    errors.append("semantic validation incomplete")
```

- [x] **Step 4: Add duplicate-key, non-object, extra-file, unknown-key, and review-status mutations**

Add these exact parameterized tests:

```python
@pytest.mark.parametrize("name", _NAMES)
def test_non_object_root_is_rejected(
    tmp_path: Path, name: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    (bundle / name).write_text("[]\n", encoding="utf-8")
    _assert_invalid(bundle, f"{name}: root must be a JSON object")


@pytest.mark.parametrize("name", _NAMES)
def test_duplicate_key_is_rejected(tmp_path: Path, name: str) -> None:
    bundle = _copy_bundle(tmp_path)
    raw = (bundle / name).read_text(encoding="utf-8")
    duplicate = raw.replace(
        '"schema_version":',
        '"schema_version": "shadow",\n  "schema_version":',
        1,
    )
    (bundle / name).write_text(duplicate, encoding="utf-8")
    _assert_invalid(bundle, f"{name}: duplicate JSON key")


def test_extra_nested_json_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    _write(bundle, "extra.json", {"schema_version": "unexpected"})
    _assert_invalid(
        bundle, "unexpected JSON documents: ['extra.json']"
    )


def test_foundation_top_level_json_set_remains_exact_five() -> None:
    root = Path("cases/discovery/g6b")
    assert sorted(
        path.name for path in root.glob("*.json") if path.is_file()
    ) == [
        "estimand_schema.json",
        "failure_ledger.json",
        "independence_schema.json",
        "negative_controls.json",
        "protocol.json",
    ]


def test_unknown_protocol_key_is_rejected(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, "row_family_protocol.json")
    value["unexpected"] = "not allowed"
    _write(bundle, "row_family_protocol.json", value)
    _assert_invalid(
        bundle, "row_family_protocol.json: document must match"
    )
```

Add explicit tests rejecting:

```text
adversarial_review_status != PENDING
bundle_role != schema_only
case_creation != prohibited
enumeration != prohibited
ctmc != prohibited
des != prohibited
output_inspection != prohibited
```

- [x] **Step 5: Run targeted tests and record GREEN**

Run:

```powershell
& $Python -m pytest -p no:cacheprovider -q `
  tests/test_g6b_row_family_protocol.py
& $Python -m pytest -p no:cacheprovider -q `
  tests/test_g6b_protocol.py::test_extra_json_document_is_rejected `
  tests/test_g6b_row_family_protocol.py::test_foundation_top_level_json_set_remains_exact_five
```

Expected: all Task 1-2 tests pass, and both explicit top-level exact-five
guards pass.

- [x] **Step 6: Run static guards**

```powershell
rg -n 'Path\.cwd|subprocess|ims_deadlock\.(analysis|ctmc|stochastic|engine|g4|g5)' `
  src/ims_deadlock/g6b_row_family_protocol.py
```

Expected: no matches.

- [x] **Step 7: Commit**

```powershell
git add src/ims_deadlock/g6b_row_family_protocol.py `
  tests/test_g6b_row_family_protocol.py
git commit -m "feat: fail closed on row-family protocol drift"
```

## Task 3: Validate Identity, Fingerprints, And Controlled Reuse

**Files:**

- Modify:
  `cases/discovery/g6b/row_families/structural_discovery_v1/identity_schema.json`
- Modify:
  `cases/discovery/g6b/row_families/structural_discovery_v1/reuse_matrix.json`
- Modify: `src/ims_deadlock/g6b_row_family_protocol.py`
- Modify: `tests/test_g6b_row_family_protocol.py`

- [x] **Step 1: Freeze the identity schema content**

`identity_schema.json` must encode:

```json
{
  "schema_version": "ims-deadlock/g6b-row-family-identity/v1",
  "study_role": "discovery_only",
  "confirmation_use": "prohibited",
  "scientific_execution_authorized": false,
  "case_creation_authorized": false,
  "identity_levels": [
    "family_id",
    "case_unit_id",
    "method_observation_id"
  ],
  "canonical_dimensions": [
    "case_content_sha256",
    "state_snapshot_sha256",
    "route_signature_sha256",
    "parameter_tuple_sha256",
    "random_stream_manifest_sha256",
    "output_root",
    "sealed_prediction_sha256",
    "metric_schema_sha256"
  ],
  "fingerprint_record_keys": [
    "dimension",
    "applicability_status",
    "artifact_role",
    "sha256_or_null"
  ],
  "no_stochastic_method_manifest": {
    "allowed": true,
    "must_be_case_unit_specific": true,
    "shared_global_sentinel_prohibited": true,
    "proves_provenance_only": true,
    "proves_stochastic_independence": false
  },
  "method_roles": [
    "exact_companion",
    "des_companion",
    "schema_only_refusal",
    "review_only_placeholder"
  ],
  "method_observations_are_independent_cases": false
}
```

- [x] **Step 2: Freeze the controlled reuse matrix**

`reuse_matrix.json["relations"]` must equal
`REUSE_MATRIX["relations"]` from Canonical Document Appendix A: four allowed
declared relation objects plus the retired-authority refusal relation. The
relation IDs, in canonical order, are:

```json
[
  "exact_des_companion",
  "controlled_family_variant",
  "negative_control_pair",
  "method_schema_reuse",
  "retired_authority_overlap"
]
```

For `exact_des_companion`, require same `case_unit_id` and prohibit counting
both methods as independent cases. For `controlled_family_variant`, require a
named variation axis and a preregistered list of held-fixed dimensions. For
`method_schema_reuse`, require outcome-independent comparability. For
`retired_authority_overlap`, set `admission = refused`.

- [x] **Step 3: Write RED mutations**

Add tests that reject:

```python
@pytest.mark.parametrize(
    "level", ["family_id", "case_unit_id", "method_observation_id"]
)
def test_missing_identity_level_is_rejected(
    tmp_path: Path, level: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, "identity_schema.json")
    value["identity_levels"].remove(level)
    _write(bundle, "identity_schema.json", value)
    _assert_invalid(bundle, "identity_levels must match")
```

Also mutate each fingerprint key, method role, relation id, and no-stochastic
truth value. Add a test that changes
`method_observations_are_independent_cases` to `true`.

- [x] **Step 3b: Run identity/reuse tests and record RED**

```powershell
& $Python -m pytest -p no:cacheprovider -q `
  tests/test_g6b_row_family_protocol.py -k `
  "identity or fingerprint or stochastic or reuse or companion"
```

Expected: the new mutations fail because exact identity/reuse validation is
not implemented.

- [x] **Step 4: Implement exact-list and exact-object validation**

Add immutable module constants equal to `IDENTITY_SCHEMA` and `REUSE_MATRIX`
from Appendix A, then reuse Task 2 `_expect_exact_document`:

```python
_expect_exact_document(
    documents["identity_schema.json"],
    _EXPECTED_IDENTITY_SCHEMA,
    "identity_schema.json",
    errors,
)
_expect_exact_document(
    documents["reuse_matrix.json"],
    _EXPECTED_REUSE_MATRIX,
    "reuse_matrix.json",
    errors,
)
```

Whole-object equality makes order-sensitive arrays, duplicates, missing
values, extra values, and semantic drift fail deterministically.

- [x] **Step 5: Run tests and record GREEN**

Run:

```powershell
& $Python -m pytest -p no:cacheprovider -q `
  tests/test_g6b_row_family_protocol.py -k `
  "identity or fingerprint or stochastic or reuse or companion"
```

Expected: all identity/reuse mutation tests pass. The load-only canonical test
still reports the deliberate `semantic validation incomplete` invalid state.

- [x] **Step 6: Commit**

```powershell
git add cases/discovery/g6b/row_families/structural_discovery_v1/identity_schema.json `
  cases/discovery/g6b/row_families/structural_discovery_v1/reuse_matrix.json `
  src/ims_deadlock/g6b_row_family_protocol.py `
  tests/test_g6b_row_family_protocol.py
git commit -m "feat: lock row-family identity and controlled reuse"
```

## Task 4: Validate Independence, Schema-Only Overlap, And Two Later Locks

**Files:**

- Modify:
  `cases/discovery/g6b/row_families/structural_discovery_v1/overlap_report_schema.json`
- Modify:
  `cases/discovery/g6b/row_families/structural_discovery_v1/runtime_lock_schema.json`
- Modify: `src/ims_deadlock/g6b_row_family_protocol.py`
- Modify: `tests/test_g6b_row_family_protocol.py`

- [x] **Step 1: Freeze overlap scope and dimensions**

The overlap schema must encode:

```json
{
  "report_role": "schema_only",
  "actual_overlap_checked": false,
  "actual_overlap_report_available": false,
  "schema_only_overlap_report_cannot_authorize_execution": true,
  "missing_actual_overlap_report_blocks_execution": true,
  "retired_authorities": ["G4", "G5", "G6_R"],
  "retired_dimensions": [
    "case_content_sha256",
    "state_snapshot_sha256",
    "route_signature_sha256",
    "parameter_tuple_sha256",
    "random_stream_manifest_sha256",
    "output_root",
    "sealed_prediction_sha256",
    "metric_schema_sha256"
  ],
  "future_confirmation_dimensions": [
    "case_content_sha256",
    "state_snapshot_sha256",
    "route_signature_sha256",
    "parameter_tuple_sha256",
    "random_stream_manifest_sha256",
    "output_root",
    "sealed_prediction_sha256"
  ],
  "future_confirmation_metric_reuse": {
    "explicitly_preregistered": true,
    "same_target_comparability": true,
    "not_derived_from_outcomes": true
  },
  "required_lock_before_actual_report": "overlap_authority_lock"
}
```

It must also contain:

```json
{
  "remote_only_G5_authority_paths": [
    "evidence/g5/G5_RAW_HASH_MANIFEST.json",
    "evidence/g5/G5_RESULT_SUMMARY.json"
  ],
  "local_absence_is_nonoverlap_evidence": false
}
```

- [x] **Step 2: Freeze the two distinct later lock schemas**

`runtime_lock_schema.json` must set both statuses to `required_later` and list
the exact approved fields:

```json
{
  "overlap_authority_lock": {
    "status": "required_later",
    "authorizes_execution": false,
    "required_fields": [
      "target_path",
      "target_branch",
      "target_head",
      "target_dirty_state",
      "upstream_ahead_behind",
      "worktree_identity",
      "repo_remote_url",
      "source_tree_hash",
      "sealed_case_artifact_hashes",
      "retired_authority_paths_and_hashes"
    ]
  },
  "execution_runtime_lock": {
    "status": "required_later",
    "allowed_only_after": "ACTUAL_OVERLAP_REPORT_PASSED",
    "authorizes_execution": false,
    "required_fields": [
      "python_executable",
      "python_version",
      "package_lock_or_environment_hash",
      "validation_commands",
      "validation_results",
      "runtime_lock_created_at_utc",
      "science_execution_authorized_by_artifact",
      "pythondontwritebytecode_or_cache_policy",
      "output_root_policy"
    ]
  }
}
```

- [x] **Step 3: Write RED tests for every dimension and lock field**

Parameterize removal, duplication, and replacement of all eight retired
dimensions, all seven future-confirmation dimensions, every metric-reuse flag,
and every required lock field. Explicitly reject:

```text
actual_overlap_checked = true
actual_overlap_report_available = true
overlap_authority_lock.status != required_later
execution_runtime_lock.status != required_later
execution_runtime_lock.allowed_only_after != ACTUAL_OVERLAP_REPORT_PASSED
```

- [x] **Step 3b: Run overlap/lock mutations and record RED**

```powershell
& $Python -m pytest -p no:cacheprovider -q `
  tests/test_g6b_row_family_protocol.py -k `
  "overlap or retired or confirmation or authority_lock or runtime_lock"
```

Expected: the new mutations fail because overlap/lock exact validation is not
implemented.

- [x] **Step 4: Implement full-object validation**

Add `_EXPECTED_OVERLAP_REPORT_SCHEMA` and `_EXPECTED_RUNTIME_LOCK_SCHEMA` from
Appendix A and validate each with `_expect_exact_document`.

- [x] **Step 4b: Run overlap/lock mutations and record GREEN**

```powershell
& $Python -m pytest -p no:cacheprovider -q `
  tests/test_g6b_row_family_protocol.py -k `
  "overlap or retired or confirmation or authority_lock or runtime_lock"
```

Expected: all overlap/lock mutation tests pass. Canonical validation remains
deliberately incomplete until Task 6.

- [x] **Step 5: Commit**

```powershell
git add cases/discovery/g6b/row_families/structural_discovery_v1/overlap_report_schema.json `
  cases/discovery/g6b/row_families/structural_discovery_v1/runtime_lock_schema.json `
  src/ims_deadlock/g6b_row_family_protocol.py `
  tests/test_g6b_row_family_protocol.py
git commit -m "feat: define future overlap and lock gates"
```

## Task 5: Validate Controls, Probes, Ontology, Pairing, And Scoring

**Files:**

- Modify:
  `cases/discovery/g6b/row_families/structural_discovery_v1/row_family_matrix.json`
- Modify: `src/ims_deadlock/g6b_row_family_protocol.py`
- Modify: `tests/test_g6b_row_family_protocol.py`

- [x] **Step 1: Encode all seven controls exactly**

Use the seven complete records in Appendix A `ROW_FAMILY_MATRIX`. The frozen
foundation fields are:

| Control | Expected classification | Expected refusal |
| --- | --- | --- |
| `NC_LOCAL_BYPASS_COMPLETES` | `D_local_not_admitted` | `reachable_completion_bypass` |
| `NC_UNSELECTED_LIVELOCK` | `R_livelock` | `not_selected_bad_class` |
| `NC_CALENDAR_EMPTY_TERMINAL` | `R_terminal` | `not_resource_deadlock` |
| `NC_POLICY_ONLY_STALL` | `P_policy` | `policy_only_not_plant_partition` |
| `NC_OR_OF_AND_FEASIBLE_BRANCH` | `D_local_not_admitted` | `feasible_branch_exists` |
| `NC_AGV_RESERVATION_BOUNDARY` | `boundary_or_new_versioned_target_required` | `semantic_boundary_changed` |
| `NC_DGLOBAL_ONLY_WITH_DLOCAL` | `D_global` | `no_double_count_through_D_local` |

Every Appendix A record also freezes its structural family id, attacked
hypothesis, allowed admission route, `not_support_if_failed = true`,
`supports_hypothesis_if_failed = false`, `case_creation_authorized = false`,
and `observed_outcome = null`.

- [x] **Step 2: Encode the three outcome-neutral probes**

```json
[
  {
    "role": "a2b_admission_probe",
    "frozen_question": "Does the declared finite-semantics A2b proof admit the candidate to D_local?",
    "falsifiers": [
      "violated_A2b_premise",
      "reachable_completion_bypass",
      "proof_check_failure"
    ]
  },
  {
    "role": "complete_lts_admission_probe",
    "frozen_question": "Does a complete LTS show completion nonreachability from the candidate?",
    "falsifiers": [
      "path_to_F",
      "truncation",
      "unavailable_transition_branch",
      "incomplete_state_registry"
    ]
  },
  {
    "role": "same_target_exact_des_probe",
    "frozen_question": "Do exact and DES companions evaluate the same frozen target without semantic drift?",
    "falsifiers": [
      "selected_label_mismatch",
      "versioned_target_mismatch",
      "stopping_hash_mismatch",
      "companion_identity_mismatch"
    ]
  }
]
```

Every probe has `observed_outcome = null`,
`favorable_outcome_frozen = false`, and `case_creation_authorized = false`.

- [x] **Step 3: Encode ontology, exact/DES, and scoring contracts**

Require:

```json
{
  "D_local_definition": "verified_first_hit_bad_set_not_terminal_scc",
  "D_local_admission_routes": [
    "A2b_proof",
    "complete_LTS_completion_nonreachability_audit"
  ],
  "exact_des_pairing": {
    "same_case_unit_id": true,
    "same_selected_bad_labels": ["D_global", "D_local"],
    "same_selected_success_label": "F",
    "same_versioned_target": true,
    "method_observations_are_independent_cases": false
  },
  "initial_scoring_state": {
    "theorem_prediction_status": "not_evaluated",
    "metric_applicability": "not_assessed",
    "metric_observations": [],
    "execution_status": "not_executed",
    "reproducibility_status": "not_assessed"
  }
}
```

- [x] **Step 4: Write RED semantic mutations**

Mutate every control field, remove each probe/falsifier, change `D_local` to a
terminal SCC, remove either admission route, drift exact/DES labels/target,
mark method companions independent, and copy `not_executed` into all scoring
fields.

- [x] **Step 4b: Run semantic mutations and record RED**

```powershell
& $Python -m pytest -p no:cacheprovider -q `
  tests/test_g6b_row_family_protocol.py -k `
  "control or probe or ontology or admission or exact_des or scoring"
```

Expected: the new mutations fail because matrix exact validation is absent.

- [x] **Step 5: Implement exact semantic validation**

Add `_EXPECTED_ROW_FAMILY_MATRIX` from Appendix A and validate it with
`_expect_exact_document`.

- [x] **Step 5b: Run semantic mutations and record GREEN**

```powershell
& $Python -m pytest -p no:cacheprovider -q `
  tests/test_g6b_row_family_protocol.py -k `
  "control or probe or ontology or admission or exact_des or scoring"
```

Expected: every matrix mutation test passes. Canonical validation remains
deliberately incomplete until Task 6.

- [x] **Step 6: Commit**

```powershell
git add cases/discovery/g6b/row_families/structural_discovery_v1/row_family_matrix.json `
  src/ims_deadlock/g6b_row_family_protocol.py `
  tests/test_g6b_row_family_protocol.py
git commit -m "feat: lock G6-B controls and outcome-neutral probes"
```

## Task 6: Validate The Append-Only Ledger, State Machine, And Leakage Boundary

**Files:**

- Modify:
  `cases/discovery/g6b/row_families/structural_discovery_v1/review_state.json`
- Modify:
  `cases/discovery/g6b/row_families/structural_discovery_v1/failure_ledger.json`
- Modify: `src/ims_deadlock/g6b_row_family_protocol.py`
- Modify: `tests/test_g6b_row_family_protocol.py`

- [x] **Step 1: Freeze the non-executing state machine**

```json
{
  "current_state": "ROW_FAMILY_BUNDLE_IMPLEMENTED",
  "allowed_states_in_order": [
    "SPEC_DRAFTED",
    "ROW_FAMILY_BUNDLE_IMPLEMENTED",
    "DATA_ONLY_VALIDATION_PASSED",
    "ADVERSARIAL_ROW_FAMILY_REVIEW_PASSED",
    "CASE_CONSTRUCTION_PLAN_APPROVED",
    "CASE_ARTIFACTS_SEALED_NO_SCIENCE",
    "OVERLAP_AUTHORITY_LOCK_RECORDED",
    "ACTUAL_OVERLAP_REPORT_PASSED",
    "EXECUTION_RUNTIME_LOCK_RECORDED",
    "EXPLICIT_SCIENCE_AUTHORIZATION_RECORDED"
  ],
  "adversarial_review_status": "PENDING",
  "forward_only": true,
  "current_state_authorizes_case_creation": false,
  "current_state_authorizes_science": false
}
```

The validator does not transition the file to
`DATA_ONLY_VALIDATION_PASSED`; a later reviewed state-integration task records
that fact without changing `adversarial_review_status`.

- [x] **Step 2: Freeze the empty append-only ledger**

```json
{
  "schema_version": "ims-deadlock/g6b-row-family-failure-ledger/v1",
  "study_role": "discovery_only",
  "confirmation_use": "prohibited",
  "scientific_execution_authorized": false,
  "case_creation_authorized": false,
  "append_only": true,
  "entries": [],
  "empty_entries_meaning": "no row-family admission or execution attempt has occurred",
  "empty_entries_do_not_mean_no_historical_failures": true,
  "required_future_reason_codes": [
    "schema_drift",
    "ontology_drift",
    "target_drift",
    "overlap_hit",
    "missing_hash",
    "failed_negative_control",
    "incomplete_LTS_audit",
    "outcome_leakage",
    "unauthorized_case_creation_attempt",
    "unauthorized_science_execution_attempt"
  ]
}
```

- [x] **Step 3: Write RED state/ledger/leakage mutations**

Reject a reordered or missing state, any current state beyond
`ROW_FAMILY_BUNDLE_IMPLEMENTED`, `PENDING` drift, `append_only = false`,
nonempty entries, weakened empty-entry meaning, missing reason codes, or any
field matching:

```text
observed_result
exact_output
des_output
state_enumeration_result
metric_value
actual_overlap_result
current_runtime_lock
```

- [x] **Step 3b: Run state/ledger/leakage mutations and record RED**

```powershell
& $Python -m pytest -p no:cacheprovider -q `
  tests/test_g6b_row_family_protocol.py -k `
  "review_state or ledger or leakage or prohibited_key"
```

Expected: the new mutations fail because state/ledger/leakage validation is
absent.

- [x] **Step 4: Implement recursive prohibited-key scan**

```python
_PROHIBITED_OUTCOME_KEYS = {
    "observed_result",
    "exact_output",
    "des_output",
    "state_enumeration_result",
    "metric_value",
    "actual_overlap_result",
    "current_runtime_lock",
}


def _walk_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        keys = set(value)
        for child in value.values():
            keys.update(_walk_keys(child))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for child in value:
            keys.update(_walk_keys(child))
        return keys
    return set()
```

Reject any intersection with `_PROHIBITED_OUTCOME_KEYS`.

- [x] **Step 5: Close exact review/ledger validation and remove the incomplete sentinel**

Add `_EXPECTED_REVIEW_STATE` and `_EXPECTED_FAILURE_LEDGER` from Appendix A,
validate them with `_expect_exact_document`, then remove:

```python
errors.append("semantic validation incomplete")
```

Replace the Task 1 load-only test with:

```python
def test_canonical_row_family_bundle_is_valid_and_disabled() -> None:
    result = validate_g6b_row_family_bundle(BUNDLE)

    assert result.valid is True
    assert result.errors == ()
    assert result.scientific_execution_authorized is False
    assert result.case_creation_authorized is False
    assert result.adversarial_review_status == "PENDING"
    assert result.review_state == "ROW_FAMILY_BUNDLE_IMPLEMENTED"
    assert set(result.bundle_hashes) == set(_NAMES)
```

- [x] **Step 5b: Run targeted tests and record GREEN**

```powershell
& $Python -m pytest -p no:cacheprovider -q `
  tests/test_g6b_row_family_protocol.py
```

Expected: canonical bundle passes; all state/ledger/leakage mutations fail.

- [x] **Step 6: Commit**

```powershell
git add cases/discovery/g6b/row_families/structural_discovery_v1/review_state.json `
  cases/discovery/g6b/row_families/structural_discovery_v1/failure_ledger.json `
  src/ims_deadlock/g6b_row_family_protocol.py `
  tests/test_g6b_row_family_protocol.py
git commit -m "feat: enforce row-family review and failure state"
```

## Task 7: Close Mutation Coverage And Prove The Validator Is Data-Only

**Files:**

- Modify: `src/ims_deadlock/g6b_row_family_protocol.py`
- Modify: `tests/test_g6b_row_family_protocol.py`

- [x] **Step 1: Add exhaustive parameterized mutation tables**

Create parameter tables for:

```python
from ims_deadlock.g6b_row_family_protocol import (
    G6B_ROW_FAMILY_FAILURE_LEDGER_VERSION,
    G6B_ROW_FAMILY_IDENTITY_VERSION,
    G6B_ROW_FAMILY_MATRIX_VERSION,
    G6B_ROW_FAMILY_OVERLAP_VERSION,
    G6B_ROW_FAMILY_PROTOCOL_VERSION,
    G6B_ROW_FAMILY_REUSE_VERSION,
    G6B_ROW_FAMILY_REVIEW_STATE_VERSION,
    G6B_ROW_FAMILY_RUNTIME_LOCK_VERSION,
    validate_g6b_row_family_bundle,
)

SCHEMA_FILES = {
    "row_family_protocol.json": G6B_ROW_FAMILY_PROTOCOL_VERSION,
    "identity_schema.json": G6B_ROW_FAMILY_IDENTITY_VERSION,
    "row_family_matrix.json": G6B_ROW_FAMILY_MATRIX_VERSION,
    "reuse_matrix.json": G6B_ROW_FAMILY_REUSE_VERSION,
    "overlap_report_schema.json": G6B_ROW_FAMILY_OVERLAP_VERSION,
    "runtime_lock_schema.json": G6B_ROW_FAMILY_RUNTIME_LOCK_VERSION,
    "review_state.json": G6B_ROW_FAMILY_REVIEW_STATE_VERSION,
    "failure_ledger.json": G6B_ROW_FAMILY_FAILURE_LEDGER_VERSION,
}
EXPECTED_DOCUMENTS = _NAMES
```

Each document receives tests for duplicate keys, non-object root, missing key,
extra key, wrong schema version, true authorization, and wrong common status.
Each scientific contract list/object receives at least one removal, addition,
reorder, duplicate, and semantic-value mutation.

Add these exact common mutation tests:

```python
@pytest.mark.parametrize(("name", "version"), sorted(SCHEMA_FILES.items()))
def test_wrong_schema_version_is_rejected(
    tmp_path: Path, name: str, version: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, name)
    value["schema_version"] = f"{version}-drift"
    _write(bundle, name, value)
    _assert_invalid(bundle, f"{name}: wrong schema_version")


@pytest.mark.parametrize("name", sorted(SCHEMA_FILES))
@pytest.mark.parametrize(
    ("field", "drift"),
    [
        ("study_role", "confirmation"),
        ("confirmation_use", "allowed"),
        ("scientific_execution_authorized", True),
        ("case_creation_authorized", True),
    ],
)
def test_common_contract_drift_is_rejected(
    tmp_path: Path,
    name: str,
    field: str,
    drift: object,
) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, name)
    value[field] = drift
    _write(bundle, name, value)
    _assert_invalid(bundle, f"{name}: {field}")


@pytest.mark.parametrize("name", sorted(EXPECTED_DOCUMENTS))
def test_unknown_key_is_rejected_for_every_document(
    tmp_path: Path, name: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, name)
    value["unexpected"] = "not allowed"
    _write(bundle, name, value)
    _assert_invalid(bundle, f"{name}: document must match")


@pytest.mark.parametrize("name", sorted(EXPECTED_DOCUMENTS))
def test_missing_key_is_rejected_for_every_document(
    tmp_path: Path, name: str
) -> None:
    bundle = _copy_bundle(tmp_path)
    value = _load(bundle, name)
    key = sorted(value)[0]
    value.pop(key)
    _write(bundle, name, value)
    _assert_invalid(bundle, f"{name}: document must match")
```

The document-specific removal/addition/reorder/duplicate/semantic mutations
are the exact tests already introduced in Tasks 3-6; Task 7 collects them into
the full targeted run rather than describing new unnamed cases.

- [x] **Step 2: Add AST-based import and call guards**

```python
import ast


def test_validator_remains_data_only() -> None:
    path = Path("src/ims_deadlock/g6b_row_family_protocol.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    allowed_imports = {
        "__future__",
        "hashlib",
        "json",
        "dataclasses",
        "pathlib",
        "typing",
    }
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            assert node.module is not None
            assert node.level == 0
            imported.add(node.module)
    assert imported <= allowed_imports
    assert "Path.cwd" not in path.read_text(encoding="utf-8")


def test_validator_has_no_filesystem_mutation_surface() -> None:
    path = Path("src/ims_deadlock/g6b_row_family_protocol.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    forbidden_methods = {
        "write_text",
        "write_bytes",
        "mkdir",
        "touch",
        "unlink",
        "rmdir",
        "rename",
        "replace",
        "chmod",
        "lchmod",
        "symlink_to",
        "hardlink_to",
        "link_to",
        "truncate",
        "writelines",
        "write",
    }
    forbidden_dynamic_calls = {
        "__import__",
        "compile",
        "delattr",
        "eval",
        "exec",
        "getattr",
        "setattr",
    }

    def literal_mode(
        node: ast.Call, positional_index: int
    ) -> str | None:
        keyword = next(
            (
                item.value
                for item in node.keywords
                if item.arg == "mode"
            ),
            None,
        )
        candidate = (
            keyword
            if keyword is not None
            else (
                node.args[positional_index]
                if len(node.args) > positional_index
                else None
            )
        )
        if candidate is None:
            return None
        assert isinstance(candidate, ast.Constant)
        assert isinstance(candidate.value, str)
        return candidate.value

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            assert node.attr not in forbidden_methods
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "open":
                mode = literal_mode(node, 0)
                if mode is not None:
                    assert not set(mode) & {"w", "a", "x", "+"}
        if isinstance(node.func, ast.Name):
            assert node.func.id not in forbidden_dynamic_calls
            if node.func.id == "open":
                mode = literal_mode(node, 1)
                if mode is not None:
                    assert not set(mode) & {"w", "a", "x", "+"}


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_valid_validation_does_not_mutate_canonical_bundle() -> None:
    before = _snapshot(BUNDLE)
    result = validate_g6b_row_family_bundle(BUNDLE)
    after = _snapshot(BUNDLE)

    assert result.valid is True
    assert after == before


def test_invalid_floating_copy_is_rejected_without_mutation(
    tmp_path: Path,
) -> None:
    floating = tmp_path / "floating_bundle"
    shutil.copytree(BUNDLE, floating)
    value = _load(floating, "review_state.json")
    value["current_state"] = "EXECUTION_AUTHORIZED"
    _write(floating, "review_state.json", value)

    before = _snapshot(floating)
    result = validate_g6b_row_family_bundle(floating)
    after = _snapshot(floating)

    assert result.valid is False
    assert any(
        "bundle root must be <repo>/cases/discovery/g6b/"
        "row_families/structural_discovery_v1" in error
        for error in result.errors
    )
    assert any(
        "review_state.json: document must match" in error
        for error in result.errors
    )
    assert after == before
```

- [x] **Step 3: Run targeted, adjacent, Ruff, and strict mypy**

```powershell
& $Python -m pytest -p no:cacheprovider -q `
  tests/test_g6b_row_family_protocol.py
& $Python -m pytest -p no:cacheprovider -q `
  tests/test_g6b_protocol.py tests/test_g6b_row_family_protocol.py `
  tests/test_terminal_classes.py tests/test_g4_protocol.py tests/test_g4_freeze.py
& $Python -m ruff check --no-cache `
  src/ims_deadlock/g6b_row_family_protocol.py `
  tests/test_g6b_row_family_protocol.py
& $Python -m ruff format --check --no-cache `
  src/ims_deadlock/g6b_row_family_protocol.py `
  tests/test_g6b_row_family_protocol.py
& $Python -m mypy --no-incremental --strict `
  src/ims_deadlock/g6b_row_family_protocol.py `
  tests/test_g6b_row_family_protocol.py
```

Expected: all pass. Record exact counts; do not predict counts in state docs
before reading output.

- [x] **Step 4: Run all eight JSON parsers**

```powershell
$JsonFiles = @(
  "row_family_protocol.json",
  "identity_schema.json",
  "row_family_matrix.json",
  "reuse_matrix.json",
  "overlap_report_schema.json",
  "runtime_lock_schema.json",
  "review_state.json",
  "failure_ledger.json"
)
foreach ($File in $JsonFiles) {
  $Path = Join-Path (
    "cases/discovery/g6b/row_families/structural_discovery_v1"
  ) $File
  & $Python -m json.tool $Path | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "JSON parse failed: $Path"
  }
}
```

Expected: all eight parse.

- [x] **Step 5: Commit**

```powershell
git add src/ims_deadlock/g6b_row_family_protocol.py `
  tests/test_g6b_row_family_protocol.py
git commit -m "test: harden G6-B row-family validation"
```

## Task 8: Integrate State, Run Full Verification, And Review

**Files:**

- Modify: `docs/cases/CASE_CHANGE_LEDGER.md`
- Modify: `docs/ROADMAP.md`
- Modify: `PROJECT_HANDOFF.md`
- Modify:
  `docs/superpowers/plans/2026-07-31-g6b-row-family-protocol.md`
- Create:
  `docs/verification/G6_B_ROW_FAMILY_PROTOCOL_REVIEW.md`

- [x] **Step 1: Record only the bounded implementation status**

State documents must say:

```text
row-family nested bundle = IMPLEMENTED / DATA-ONLY
case creation = false
scientific execution = false
adversarial row-family review = PENDING until independent review completes
actual overlap report = absent
overlap-authority lock = absent
execution-runtime lock = absent
discovery outcomes = absent
G6-B = OPEN
G6-C/D/E = NOT STARTED
historical evidence changed = false
```

- [x] **Step 2a: Run the full qualified pytest suite**

Using the locked remote worktree and canonical qualified Python:

```powershell
& $Python -m pytest -p no:cacheprovider -q
```

Expected: pass. Record the exact test count and elapsed time.

- [x] **Step 2b: Run both Ruff checks**

```powershell
& $Python -m ruff check --no-cache src tests
& $Python -m ruff format --check --no-cache src tests
```

Expected: both pass. Record the exact formatted-file count.

- [x] **Step 2c: Run both strict mypy scopes**

```powershell
& $Python -m mypy --no-incremental --strict src
& $Python -m mypy --no-incremental --strict `
  --explicit-package-bases src tests
```

Expected: both pass. Record both exact source-file counts.

- [x] **Step 2d: Run the Git diff check**

```powershell
git diff --check
```

Expected: pass with no output.

Phase A evidence recorded 2026-07-31 before final documentation reconciliation:

```text
target path = D:\worktree\IMS_deadlock-g6b-discovery
branch = codex/g6b-discovery-estimand-lock
HEAD = 4fda4896d2284c360f3021e48475f7678b0f37fd
upstream = NO_UPSTREAM
candidate dirty scope = PROJECT_HANDOFF.md; docs/ROADMAP.md;
  docs/cases/CASE_CHANGE_LEDGER.md;
  docs/superpowers/plans/2026-07-31-g6b-row-family-protocol.md;
  untracked docs/verification/G6_B_ROW_FAMILY_PROTOCOL_REVIEW.md
Python = D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe
Python version = 3.13.9
PYTHONPATH = D:\worktree\IMS_deadlock-g6b-discovery\src
PYTHONDONTWRITEBYTECODE = 1
pytest = 1307 passed in 150.84s
ruff check = All checks passed!
ruff format = 43 files already formatted
mypy src = Success: no issues found in 23 source files
mypy src tests = Success: no issues found in 43 source files
git diff --check = pass before docs edits
nested JSON parse = 8/8 passed with python -m json.tool
top-level G6-B JSON set = exact five: estimand_schema.json,
  failure_ledger.json, independence_schema.json, negative_controls.json,
  protocol.json
nested row-family JSON set = exact eight: failure_ledger.json,
  identity_schema.json, overlap_report_schema.json, reuse_matrix.json,
  review_state.json, row_family_matrix.json, row_family_protocol.json,
  runtime_lock_schema.json
row_families inventory = one structural_discovery_v1 directory plus those
  exact-eight JSON files
foundation tests = 52 passed in 5.00s
canonical row-family test = 1 passed in 0.12s
canonical validator = valid=True, errors=[], science=False, case=False,
  adversarial_review_status=PENDING,
  current_state=ROW_FAMILY_BUNDLE_IMPLEMENTED, hashes=8
recursive exact-eight scan = 8 scientific authorization occurrences all false;
  18 case authorization occurrences all false; both review-status occurrences
  PENDING
Tasks 1-7 diff a4897ab..4fda489 = exact-eight nested JSON,
  src/ims_deadlock/g6b_row_family_protocol.py,
  tests/test_g6b_row_family_protocol.py only
artifact inventory = no discovery cases/outcomes, actual overlap report,
  actual overlap value, current lock, overlap-authority lock,
  execution-runtime lock, output root, result/science summary, enumeration,
  CTMC, DES, or science artifact
task-owned mypy cache dirs = absent:
  D:\worktree\_task8_mypy_src_cache;
  D:\worktree\_task8_mypy_src_tests_cache
```

- [x] **Step 3: Run a specification-compliance review**

The reviewer must compare every approved design section with an implemented
artifact/test and report either `APPROVED` or exact file:line blockers.

Phase B verdict: `APPROVED`; no blockers.

- [x] **Step 4: Run a code-quality review**

The reviewer must check data-only imports, no cwd fallback, exact-root
resolution, strict JSON/key behavior, deterministic errors, type safety,
mutation coverage, and no case/science call surface.

Phase B verdict: `APPROVED`; no Critical/Important/Minor blockers.

- [x] **Step 5: Run an independent scientific-boundary review**

The review must check:

```text
K_local != D_local
A2b proof route != complete-LTS audit route
D_local != terminal SCC
exact/DES companions != independent cases
controlled reuse != pseudoreplication
no-stochastic manifest proves provenance only
retired scope = G4/G5/G6-R on exactly eight dimensions
future confirmation scope = seven dimensions plus limited metric reuse
seven controls and three probes are complete and outcome-neutral
scoring layers remain type-distinct
overlap-authority lock precedes actual overlap
execution-runtime lock follows overlap
no actual cases, locks, overlap values, outputs, or science exist
```

Verdict may be `PASS PROTOCOL ONLY`; it must not authorize case construction
or science.

Phase B verdict: `PASS PROTOCOL ONLY`; no blockers. This is a protocol-only
scientific-boundary verdict and does not authorize case construction or
science.

- [x] **Step 6: Fix every Critical/Important finding and re-run its review**

Do not waive, downgrade, or delete negative findings. Minor findings may remain
only if the reviewer explicitly states they cannot change scientific meaning,
execution authority, reproducibility, or handoff correctness.

Phase B finding disposition: no Critical, Important, or Minor blockers were
reported, so no fixes or review re-runs were required.

- [ ] **Step 7: Commit bounded state integration**

```powershell
git add docs/cases/CASE_CHANGE_LEDGER.md docs/ROADMAP.md PROJECT_HANDOFF.md `
  docs/superpowers/plans/2026-07-31-g6b-row-family-protocol.md `
  docs/verification/G6_B_ROW_FAMILY_PROTOCOL_REVIEW.md
git commit -m "docs: record G6-B row-family protocol gate"
```

- [ ] **Step 8: Re-lock and report final branch evidence**

Record:

```text
target path
branch
full HEAD
dirty state
upstream/ahead-behind or no-upstream fact
qualified Python path/version
full validation output
review verdicts
all still-open science gates
```

## Canonical Document Appendix A

The eight JSON files are the UTF-8, two-space-indented, newline-terminated JSON
serialization of these exact Python objects. Dictionary key order is not
semantic; every list order is semantic.

```python
COMMON = {
    "study_role": "discovery_only",
    "confirmation_use": "prohibited",
    "scientific_execution_authorized": False,
    "case_creation_authorized": False,
}

ROW_FAMILY_PROTOCOL = {
    "schema_version": G6B_ROW_FAMILY_PROTOCOL_VERSION,
    **COMMON,
    "protocol_id": "G6-B-ROW-FAMILY-STRUCTURAL-DISCOVERY-V1",
    "adversarial_review_status": "PENDING",
    "bundle_role": "schema_only",
    "source_design": (
        "docs/superpowers/specs/2026-07-31-g6b-row-family-design.md"
    ),
    "artifact_paths": [
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "identity_schema.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "row_family_matrix.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "reuse_matrix.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "overlap_report_schema.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "runtime_lock_schema.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "review_state.json",
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "failure_ledger.json",
    ],
    "execution_boundary": {
        "case_creation": "prohibited",
        "enumeration": "prohibited",
        "ctmc": "prohibited",
        "des": "prohibited",
        "output_inspection": "prohibited",
    },
}

IDENTITY_SCHEMA = {
    "schema_version": G6B_ROW_FAMILY_IDENTITY_VERSION,
    **COMMON,
    "identity_levels": [
        "family_id",
        "case_unit_id",
        "method_observation_id",
    ],
    "canonical_dimensions": [
        "case_content_sha256",
        "state_snapshot_sha256",
        "route_signature_sha256",
        "parameter_tuple_sha256",
        "random_stream_manifest_sha256",
        "output_root",
        "sealed_prediction_sha256",
        "metric_schema_sha256",
    ],
    "fingerprint_record_keys": [
        "dimension",
        "applicability_status",
        "artifact_role",
        "sha256_or_null",
    ],
    "no_stochastic_method_manifest": {
        "allowed": True,
        "must_be_case_unit_specific": True,
        "shared_global_sentinel_prohibited": True,
        "proves_provenance_only": True,
        "proves_stochastic_independence": False,
    },
    "method_roles": [
        "exact_companion",
        "des_companion",
        "schema_only_refusal",
        "review_only_placeholder",
    ],
    "method_observations_are_independent_cases": False,
}

REUSE_MATRIX = {
    "schema_version": G6B_ROW_FAMILY_REUSE_VERSION,
    **COMMON,
    "relations": [
        {
            "id": "exact_des_companion",
            "same_case_unit_id": True,
            "allowed_shared_dimensions": [
                "case_content_sha256",
                "state_snapshot_sha256",
                "route_signature_sha256",
                "parameter_tuple_sha256",
                "sealed_prediction_sha256",
                "metric_schema_sha256",
            ],
            "required_distinct_fields": [
                "method_observation_id",
                "method_role",
                "output_root",
            ],
            "evidence_counting": "one_case_unit",
        },
        {
            "id": "controlled_family_variant",
            "same_case_unit_id": False,
            "allowed_shared_dimensions": [
                "family_id",
                "ontology_version",
                "metric_schema_sha256",
                "selected_target_version",
                "declared_held_fixed_dimensions",
            ],
            "required_fields": [
                "declared_variation_axis",
                "declared_held_fixed_dimensions",
                "outcome_independent_declaration",
            ],
            "evidence_counting": "distinct_case_units_not_independent_replicates",
        },
        {
            "id": "negative_control_pair",
            "same_case_unit_id": False,
            "allowed_shared_dimensions": [
                "family_id",
                "ontology_version",
                "metric_schema_sha256",
            ],
            "required_fields": [
                "required_negative_control_id",
                "hypothesis_attacked",
                "mechanism_difference",
            ],
            "evidence_counting": "control_pair",
        },
        {
            "id": "method_schema_reuse",
            "same_case_unit_id": False,
            "allowed_shared_dimensions": [
                "metric_schema_sha256",
                "orthogonal_scoring_layers",
            ],
            "required_fields": [
                "explicitly_preregistered",
                "same_target_comparability",
                "not_derived_from_outcomes",
            ],
            "evidence_counting": "no_independence_claim_from_schema_reuse",
        },
        {
            "id": "retired_authority_overlap",
            "same_case_unit_id": False,
            "allowed_shared_dimensions": [],
            "required_fields": [
                "retired_authority",
                "overlap_dimension",
                "refusal_ledger_entry",
            ],
            "admission": "refused",
        },
    ],
}

ROW_FAMILY_MATRIX = {
    "schema_version": G6B_ROW_FAMILY_MATRIX_VERSION,
    **COMMON,
    "negative_control_families": [
        {
            "structural_family_id": "local_bypass_completion_family",
            "required_negative_control_id": "NC_LOCAL_BYPASS_COMPLETES",
            "hypothesis_attacked": (
                "local_candidate_with_reachable_completion_is_D_local"
            ),
            "admission_route_allowed": "boundary_probe_only",
            "expected_classification": "D_local_not_admitted",
            "expected_refusal": "reachable_completion_bypass",
            "expected_refusal_or_classification": {
                "classification": "D_local_not_admitted",
                "refusal": "reachable_completion_bypass",
            },
            "not_support_if_failed": True,
            "supports_hypothesis_if_failed": False,
            "case_creation_authorized": False,
            "observed_outcome": None,
        },
        {
            "structural_family_id": "unselected_livelock_family",
            "required_negative_control_id": "NC_UNSELECTED_LIVELOCK",
            "hypothesis_attacked": (
                "unselected_closed_recurrent_class_is_selected_bad"
            ),
            "admission_route_allowed": "classification_probe_only",
            "expected_classification": "R_livelock",
            "expected_refusal": "not_selected_bad_class",
            "expected_refusal_or_classification": {
                "classification": "R_livelock",
                "refusal": "not_selected_bad_class",
            },
            "not_support_if_failed": True,
            "supports_hypothesis_if_failed": False,
            "case_creation_authorized": False,
            "observed_outcome": None,
        },
        {
            "structural_family_id": "calendar_empty_terminal_family",
            "required_negative_control_id": "NC_CALENDAR_EMPTY_TERMINAL",
            "hypothesis_attacked": (
                "non_resource_terminal_is_resource_deadlock"
            ),
            "admission_route_allowed": "classification_probe_only",
            "expected_classification": "R_terminal",
            "expected_refusal": "not_resource_deadlock",
            "expected_refusal_or_classification": {
                "classification": "R_terminal",
                "refusal": "not_resource_deadlock",
            },
            "not_support_if_failed": True,
            "supports_hypothesis_if_failed": False,
            "case_creation_authorized": False,
            "observed_outcome": None,
        },
        {
            "structural_family_id": "policy_only_stall_family",
            "required_negative_control_id": "NC_POLICY_ONLY_STALL",
            "hypothesis_attacked": "policy_stall_changes_plant_partition",
            "admission_route_allowed": "classification_probe_only",
            "expected_classification": "P_policy",
            "expected_refusal": "policy_only_not_plant_partition",
            "expected_refusal_or_classification": {
                "classification": "P_policy",
                "refusal": "policy_only_not_plant_partition",
            },
            "not_support_if_failed": True,
            "supports_hypothesis_if_failed": False,
            "case_creation_authorized": False,
            "observed_outcome": None,
        },
        {
            "structural_family_id": "or_of_and_feasible_branch_family",
            "required_negative_control_id": "NC_OR_OF_AND_FEASIBLE_BRANCH",
            "hypothesis_attacked": (
                "local_candidate_with_feasible_branch_is_D_local"
            ),
            "admission_route_allowed": "boundary_probe_only",
            "expected_classification": "D_local_not_admitted",
            "expected_refusal": "feasible_branch_exists",
            "expected_refusal_or_classification": {
                "classification": "D_local_not_admitted",
                "refusal": "feasible_branch_exists",
            },
            "not_support_if_failed": True,
            "supports_hypothesis_if_failed": False,
            "case_creation_authorized": False,
            "observed_outcome": None,
        },
        {
            "structural_family_id": "agv_reservation_boundary_family",
            "required_negative_control_id": "NC_AGV_RESERVATION_BOUNDARY",
            "hypothesis_attacked": (
                "changed_AGV_reservation_semantics_preserve_target_identity"
            ),
            "admission_route_allowed": "boundary_or_new_target_only",
            "expected_classification": (
                "boundary_or_new_versioned_target_required"
            ),
            "expected_refusal": "semantic_boundary_changed",
            "expected_refusal_or_classification": {
                "classification": (
                    "boundary_or_new_versioned_target_required"
                ),
                "refusal": "semantic_boundary_changed",
            },
            "not_support_if_failed": True,
            "supports_hypothesis_if_failed": False,
            "case_creation_authorized": False,
            "observed_outcome": None,
        },
        {
            "structural_family_id": "dglobal_with_local_core_family",
            "required_negative_control_id": "NC_DGLOBAL_ONLY_WITH_DLOCAL",
            "hypothesis_attacked": (
                "global_deadlock_with_local_core_counts_twice"
            ),
            "admission_route_allowed": "classification_probe_only",
            "expected_classification": "D_global",
            "expected_refusal": "no_double_count_through_D_local",
            "expected_refusal_or_classification": {
                "classification": "D_global",
                "refusal": "no_double_count_through_D_local",
            },
            "not_support_if_failed": True,
            "supports_hypothesis_if_failed": False,
            "case_creation_authorized": False,
            "observed_outcome": None,
        },
    ],
    "discovery_probes": [
        {
            "role": "a2b_admission_probe",
            "frozen_question": (
                "Does the declared finite-semantics A2b proof admit the "
                "candidate to D_local?"
            ),
            "falsifiers": [
                "violated_A2b_premise",
                "reachable_completion_bypass",
                "proof_check_failure",
            ],
            "favorable_outcome_frozen": False,
            "case_creation_authorized": False,
            "observed_outcome": None,
        },
        {
            "role": "complete_lts_admission_probe",
            "frozen_question": (
                "Does a complete LTS show completion nonreachability from "
                "the candidate?"
            ),
            "falsifiers": [
                "path_to_F",
                "truncation",
                "unavailable_transition_branch",
                "incomplete_state_registry",
            ],
            "favorable_outcome_frozen": False,
            "case_creation_authorized": False,
            "observed_outcome": None,
        },
        {
            "role": "same_target_exact_des_probe",
            "frozen_question": (
                "Do exact and DES companions evaluate the same frozen target "
                "without semantic drift?"
            ),
            "falsifiers": [
                "selected_label_mismatch",
                "versioned_target_mismatch",
                "stopping_hash_mismatch",
                "companion_identity_mismatch",
            ],
            "favorable_outcome_frozen": False,
            "case_creation_authorized": False,
            "observed_outcome": None,
        },
    ],
    "ontology_contract": {
        "D_local_definition": (
            "verified_first_hit_bad_set_not_terminal_scc"
        ),
        "D_local_admission_routes": [
            "A2b_proof",
            "complete_LTS_completion_nonreachability_audit",
        ],
    },
    "exact_des_pairing": {
        "same_case_unit_id": True,
        "same_selected_bad_labels": ["D_global", "D_local"],
        "same_selected_success_label": "F",
        "same_versioned_target": True,
        "method_observations_are_independent_cases": False,
    },
    "initial_scoring_state": {
        "theorem_prediction_status": "not_evaluated",
        "metric_applicability": "not_assessed",
        "metric_observations": [],
        "execution_status": "not_executed",
        "reproducibility_status": "not_assessed",
    },
}

OVERLAP_REPORT_SCHEMA = {
    "schema_version": G6B_ROW_FAMILY_OVERLAP_VERSION,
    **COMMON,
    "report_role": "schema_only",
    "actual_overlap_checked": False,
    "actual_overlap_report_available": False,
    "schema_only_overlap_report_cannot_authorize_execution": True,
    "missing_actual_overlap_report_blocks_execution": True,
    "retired_authorities": ["G4", "G5", "G6_R"],
    "retired_dimensions": [
        "case_content_sha256",
        "state_snapshot_sha256",
        "route_signature_sha256",
        "parameter_tuple_sha256",
        "random_stream_manifest_sha256",
        "output_root",
        "sealed_prediction_sha256",
        "metric_schema_sha256",
    ],
    "future_confirmation_dimensions": [
        "case_content_sha256",
        "state_snapshot_sha256",
        "route_signature_sha256",
        "parameter_tuple_sha256",
        "random_stream_manifest_sha256",
        "output_root",
        "sealed_prediction_sha256",
    ],
    "future_confirmation_metric_reuse": {
        "explicitly_preregistered": True,
        "same_target_comparability": True,
        "not_derived_from_outcomes": True,
    },
    "required_lock_before_actual_report": "overlap_authority_lock",
    "remote_only_G5_authority_paths": [
        "evidence/g5/G5_RAW_HASH_MANIFEST.json",
        "evidence/g5/G5_RESULT_SUMMARY.json",
    ],
    "local_absence_is_nonoverlap_evidence": False,
    "later_actual_report_required_fields": [
        "locked_target_identity",
        "retired_authority_hashes",
        "discovery_case_unit_hashes",
        "per_dimension_results",
        "per_unit_results",
        "refusal_entries",
    ],
}

RUNTIME_LOCK_SCHEMA = {
    "schema_version": G6B_ROW_FAMILY_RUNTIME_LOCK_VERSION,
    **COMMON,
    "overlap_authority_lock": {
        "status": "required_later",
        "authorizes_execution": False,
        "required_fields": [
            "target_path",
            "target_branch",
            "target_head",
            "target_dirty_state",
            "upstream_ahead_behind",
            "worktree_identity",
            "repo_remote_url",
            "source_tree_hash",
            "sealed_case_artifact_hashes",
            "retired_authority_paths_and_hashes",
        ],
    },
    "execution_runtime_lock": {
        "status": "required_later",
        "allowed_only_after": "ACTUAL_OVERLAP_REPORT_PASSED",
        "authorizes_execution": False,
        "required_fields": [
            "python_executable",
            "python_version",
            "package_lock_or_environment_hash",
            "validation_commands",
            "validation_results",
            "runtime_lock_created_at_utc",
            "science_execution_authorized_by_artifact",
            "pythondontwritebytecode_or_cache_policy",
            "output_root_policy",
        ],
    },
}

REVIEW_STATE = {
    "schema_version": G6B_ROW_FAMILY_REVIEW_STATE_VERSION,
    **COMMON,
    "current_state": "ROW_FAMILY_BUNDLE_IMPLEMENTED",
    "allowed_states_in_order": [
        "SPEC_DRAFTED",
        "ROW_FAMILY_BUNDLE_IMPLEMENTED",
        "DATA_ONLY_VALIDATION_PASSED",
        "ADVERSARIAL_ROW_FAMILY_REVIEW_PASSED",
        "CASE_CONSTRUCTION_PLAN_APPROVED",
        "CASE_ARTIFACTS_SEALED_NO_SCIENCE",
        "OVERLAP_AUTHORITY_LOCK_RECORDED",
        "ACTUAL_OVERLAP_REPORT_PASSED",
        "EXECUTION_RUNTIME_LOCK_RECORDED",
        "EXPLICIT_SCIENCE_AUTHORIZATION_RECORDED",
    ],
    "adversarial_review_status": "PENDING",
    "forward_only": True,
    "current_state_authorizes_case_creation": False,
    "current_state_authorizes_science": False,
}

FAILURE_LEDGER = {
    "schema_version": G6B_ROW_FAMILY_FAILURE_LEDGER_VERSION,
    **COMMON,
    "append_only": True,
    "entries": [],
    "empty_entries_meaning": (
        "no row-family admission or execution attempt has occurred"
    ),
    "empty_entries_do_not_mean_no_historical_failures": True,
    "required_future_reason_codes": [
        "schema_drift",
        "ontology_drift",
        "target_drift",
        "overlap_hit",
        "missing_hash",
        "failed_negative_control",
        "incomplete_LTS_audit",
        "outcome_leakage",
        "unauthorized_case_creation_attempt",
        "unauthorized_science_execution_attempt",
    ],
}
```

## Final Review Gate

Before any later case-construction plan:

- [ ] Every Task 1-8 checkbox is truthfully complete.
- [ ] Exact-eight nested JSON set passes the validator.
- [ ] Existing exact-five top-level G6-B bundle still passes its 52-test suite.
- [ ] No extra top-level JSON exists under `cases/discovery/g6b/`.
- [ ] Full pytest, Ruff, both strict mypy commands, JSON parsing, and diff check
  pass on the exact locked worktree.
- [ ] Specification, code-quality, and independent scientific-boundary reviews
  pass after all fixes.
- [ ] `scientific_execution_authorized` remains false everywhere.
- [ ] `case_creation_authorized` remains false everywhere.
- [ ] `adversarial_review_status` remains `PENDING` in the implemented bundle;
  the review verdict is stored separately as `PASS PROTOCOL ONLY`.
- [ ] G6-B remains `OPEN`; G6-C/D/E remain not started.
- [ ] No case artifact, actual overlap value, current lock, output root,
  enumeration, CTMC, DES, or science summary exists.

Stop after this gate. The only permitted successor is a separately approved
case-construction plan. Do not infer execution authorization from green tests,
review approval, or protocol completeness.
