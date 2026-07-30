# G5 Reproducibility Audit

## Scope

This audit checks the supplied primary and reproducibility captures for the
nine frozen G4 confirmation cases. It uses:

- `G5_RAW_CAPTURE.tar.gz`;
- `G5_RAW_HASH_MANIFEST.json`;
- `G5_RESULT_SUMMARY.json`;
- per-case `record.json`, `stdout.json` or `stdout.bin`, and `stderr.txt`.

No third run, retry, rerun, retuning, or raw-output repair was performed.

## Execution Lock

| Item | Value |
| --- | --- |
| Freeze ID | `G4-FREEZE-C-20260730T051210Z` |
| Branch recorded by capture | `codex/g5-confirmation-execution` |
| Git head recorded by capture | `8aa752804b885b79e5371c98e7961087c540f2a8` |
| Raw output root | `artifacts/g5-confirmation/G5-CONFIRMATION-20260730-R1` |
| Required labels | `primary`, `repro` |
| Original raw manifest SHA-256 | `c1940b5f421d5a22621d36a69fb055672d809277ccb8739d7ca2304b81397cf4` |
| Raw archive SHA-256 | `e4fcd845bf17b6fec18734f75741462a5e0f2b5e614fe8112968643a6ca0358c` |

## Exact Reproducibility

All nine cases have one primary capture and one reproducibility capture. The
manifest reports exact agreement for raw stdout, canonical JSON when present,
stderr, execution status, and metadata for all 9/9 cases.

| Case | Primary exit | Repro exit | Raw stdout | Canonical JSON | Stderr | Metadata |
| --- | ---: | ---: | --- | --- | --- | --- |
| `G4_ADVERSARIAL_BOUNDARY` | 0 | 0 | match | match | match | match |
| `G4_B05_SUPERVISOR_COMPARATOR` | 0 | 0 | match | match | match | match |
| `G4_CRP_OUTSIDE_S4PR` | 0 | 0 | match | match | match | match |
| `G4_CRP_S4PR_AGREE` | 0 | 0 | match | match | match | match |
| `G4_CRP_UNREACHABLE_CANDIDATE` | 0 | 0 | match | match | match | match |
| `G4_IMS_PARAMETER_GRID` | 1 | 1 | match | match | match | match |
| `G4_L30_RESOURCE_BASELINE` | 0 | 0 | match | match | match | match |
| `G4_MEDIUM_ISLAND_REBUILD` | 1 | 1 | match | match | match | match |
| `G4_RECORDER_TARGET_QUANTIFICATION` | 0 | 0 | match | match | match | match |

The two `NONZERO_EXIT` cases are reproducible failures, not stochastic
mismatches.

## Retained Nonzero Exits

`G4_MEDIUM_ISLAND_REBUILD` primary and repro both ended with:

```text
ValueError: state 's79' must have reachable absorbing transition
```

`G4_IMS_PARAMETER_GRID` primary and repro both ended with:

```text
ValueError: state 's5' must have reachable absorbing transition
```

Both cases remain `INCONCLUSIVE`. The captures retain empty stdout hashes,
non-empty stderr hashes, exit code `1`, and no canonical JSON payload.

## Hash Evidence

| Case | Raw stdout SHA-256 | Canonical JSON SHA-256 | Stderr SHA-256 |
| --- | --- | --- | --- |
| `G4_ADVERSARIAL_BOUNDARY` | `cececd6efa166bc528091aaed10c08971916279b75c0389db92fe284f88974ca` | `6e5f9f05b92ddd604555c79ca086344f6cb22cc1bc5e7ee1a3d9db3cde5abb9f` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `G4_B05_SUPERVISOR_COMPARATOR` | `8bb8023659ad89075e1b33fd8f36998470939236c9dceb4089c6469cf39a6924` | `3fb14993c25fdbd6da87737cd21ed43c6b8c374772095dfd22ac2e0dcb131cce` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `G4_CRP_OUTSIDE_S4PR` | `a62edb7ecb1c5c773dde172ab39bb3ff3b616ed4af67d0ef538926a0b0bcd062` | `a74a7b66a9258eae7e5ac866446dc5681dc06c26ff247000d4c980b6fea9bb65` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `G4_CRP_S4PR_AGREE` | `e4264a549be56c4790be2692c07ee4f3ea1e8ef0e94657aec5faac0177b3d67c` | `c90679797526034b5f89435850ecf23da2e640c88a9a471508429605703d54e4` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `G4_CRP_UNREACHABLE_CANDIDATE` | `726721b11e88b7024dd662359c86c7380ad3ad533bea44c16235961414bea3ed` | `3b2c4318fc0557a8b0f94c444851b714b2015c8135e441d93d2649df2c409c38` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `G4_IMS_PARAMETER_GRID` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `null` | `204424d2898042bf3864bff1249a5eedfead10675d0674d831d678a8cf28f98a` |
| `G4_L30_RESOURCE_BASELINE` | `009c16cd63742b838a32d0c7309ddc5fe9f17d692e7bf9cbef7792d08b054a4d` | `a330084a5db13ab80e05ad5b335aaaec43f479f15fa685bd16a40ed75e6cd6d2` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `G4_MEDIUM_ISLAND_REBUILD` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `null` | `aa842fb3deafc390c137455d8a45d162db88200e315f488f277345c07c57452a` |
| `G4_RECORDER_TARGET_QUANTIFICATION` | `aa192e9926a01f1495c49a4da70b4c026f52c29a894417b87550c4d488858aad` | `3fc8dd50549863c718f3369191d7e63a6f8ed427d71cb7b44853616cfd960f6c` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## Audit Verdict

Reproducibility evidence is exact for 9/9 primary/repro pairs. Scientific
closure is not achieved because two cases reproducibly exit nonzero and the
scoring erratum requires a successor scorer before paper use.
