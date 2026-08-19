# T-ASE Hardening T0 Approval

Date: 2026-08-19
Worktree: `D:\worktree\IMS_deadlock-journal-hardening-v1`
Branch: `codex/journal-hardening-v1`
User instruction: `批准这三组`

The following `compute-parallel-v2` bytes were re-hashed on the locked
worktree immediately before implementation and matched exactly:

```text
approved_spec_sha256=5f4e0a3d58bdf4a090322d1537dd8b4a3125e75845e146a15a02760aab5be8b2
approved_plan_sha256=ee99c64ad56fcabaa74f5dc1c87c3cdb4b3ebe4e200a271b4498c8681d6b6cb4
approved_review_sha256=e418a81b5d30708ca894fd009238782c02987ecf6e9d82d549521161c0bc2c83
```

This approval opens plan tasks T1–T5 (module, H1–H4 materialization,
process-pool scheduler). It does **not** set
`quantitative_execution_authorized=true` and does not authorize Barrier B
CTMC/DES (plan T6).
