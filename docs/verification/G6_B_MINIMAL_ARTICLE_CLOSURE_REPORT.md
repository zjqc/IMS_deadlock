# G6-B Minimal Article Closure Verification Report

Status: `SCOPED TIER A / ORIGINAL G6-B OPEN_PENDING`

Date: 2026-08-06

## 1. 结论

本轮已经形成一个可写入论文、但明确受限的理论—案例闭环：

- request-closed A2b 路线通过其构造性正例；
- complete finite-LTS completion-nonreachability 路线通过其多核正例；
- completion-bypass 反例正确阻止 `K_local` 候选进入 `D_local`；
- `D_global` 优先级控制正确阻止同一状态经 `D_local` 重复计数；
- 新增的预结果桥接案例给出解析概率 `1/3`，独立种子 DES 得到
  `0.33642578125`；
- 预先声明的 18 个 exact/DES 比较单元全部兼容，最大绝对误差
  `0.0030924479166667 < 0.028340`；
- 冻结 claim ladder 因此机械选择
  `tier_a_dual_route_closure`。

这个 Tier A 只表示“双路线的范围内构造闭环”。它不表示原 13 案例、
8 维 overlap 的 G6-B gate 已通过。原 G6-B 仍为 `OPEN_PENDING`。

## 2. 权威目标与执行锁

唯一运行与行为权威是远端 Windows linked worktree：

| 字段 | 锁定值 |
| --- | --- |
| path | `D:\worktree\IMS_deadlock-g6b-retired-normalization` |
| branch | `codex/g6b-minimal-article-closure` |
| pre-outcome scope commit | `4e385b6bca685454082ced7465b254c5b95017b8` |
| executable implementation commit | `7aefab705865a57efdaa143d2e2daa8c295a3dfc` |
| implementation tree | `b1bc6710bcf4937c3ce10f50ca26a4641a69d22e` |
| write-once evidence commit | `7d0603a` |
| validated integration subject | `98f429b5e0b1d377a9d4297d48a00532f1c8cbed` |
| validated integration tree | `9e204cbdc55e94ffcd5a362c1d4057112561c53b` |
| runtime | `D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe` |
| Python | `3.13.9` |
| import root | `D:\worktree\IMS_deadlock-g6b-retired-normalization\src` |
| dirty state immediately before execution | clean |
| evidence root immediately before execution | absent |
| write-once wall time | `0.702 s` |

在范围锁提交前没有产生 article-core classification、exact 或 DES 结果。
范围锁、测试、实现和证据分别保存在不同提交中，避免用观察结果更换案例。

## 3. 冻结范围与上游身份

Article scope lock:

- path: `cases/article_core/article_scope_lock_v1.json`;
- self SHA-256:
  `86ec7b80c888c7758d326a9de7793b0f0f65f4740ecf0303e1b17d2d14344660`;
- six-case roster frozen before execution;
- failed-case substitution prohibited;
- DES replications per case: `4096`;
- master seed: `2026080601`;
- replication seed rule: `sha256(master_seed:replication_index)`;
- familywise error budget: `0.05`;
- simultaneous absolute-error tolerance: `0.028340`.

Bound upstream objects:

| 上游对象 | raw SHA-256 | self SHA-256 |
| --- | --- | --- |
| sealed 13-case construction manifest | `95fc411a02d8085b84c1a4f2025d2c7806e1d8c632b645f556c61aefe1b6406b` | `36622495237f2c22677190b3858d275ea8285d0ee8fc1ed004f8c03e8543a68c` |
| retired normalization manifest | `d1391920c97c254fe8874175d502853354b9859322ac624a94b2f2573f371d23` | `3fcb863d8f7f19820c8ea5f5edbaf213dec587fb4497265b5ec005f525c587ad` |

Retired normalization 的 `119` 个 eligible records 和 `62` 个 typed refusals
保持不变。由于其中没有可用于
`random_stream_manifest_sha256` 或 `metric_schema_sha256` 的 eligible
projection，本报告不声称新随机流或 metric schema 与 retired studies 独立。

## 4. 理论义务—案例映射

| Case | 论文角色 | 适用方法 | 机械证书结果 |
| --- | --- | --- | --- |
| `g6b_cu_pc_dglobal_only_v1` | time-zero global positive | global predicate | initial state 仅进入 `D_global` |
| `g6b_cu_pc_dlocal_a2b_single_kernel_v1` | request-closed local positive | A2b | `s_initial` 进入 `D_local`; explicit A2b flag present |
| `g6b_cu_pc_dlocal_lts_multi_kernel_v1` | multi-kernel local positive | complete finite LTS | `dlocal_ab,dlocal_cd` 均不能到达 `F`; plant arcs `6`, stopped arcs `4` |
| `g6b_cu_nc_local_bypass_completes_v1` | negative control | complete finite LTS | `s_local_candidate -> s_bypass -> f_complete`; candidate 不进入 `D_local` |
| `g6b_cu_nc_dglobal_only_with_dlocal_v1` | precedence control | global-before-local classification | local candidate 仅计为 `D_global`, 不重复计数 |
| `g6b_article_bridge_competing_local_completion_v1` | nondegenerate probability bridge | A2b-admitted local target in a complete two-exit LTS | `s0 -> D_local` rate `1`; `s0 -> F` rate `2`; exact selected-bad probability `1/3` |

对 complete-LTS 正例，plant graph 中 `D_local` 后仍有 outgoing arcs；这些 arcs
仅在 stopped process 中删除。因此该案例直接区分了：

```text
D_local = verified bad first-hit set
D_local != plant terminal SCC
```

## 5. Quantitative protocol

令

```text
A_stop = D_global union D_local union F
tau = first hit of A_stop
```

三个比较量为：

```text
theta_global = P(X_tau in D_global)
theta_local = P(X_tau in D_local)
theta_selected_bad = theta_global + theta_local
```

Exact 使用完整有限 stopped CTMC。DES 使用同一 plant transitions、相同 rates
和同一 stopping partition，但逐 replication 使用冻结 SHA-256 种子派生。

对最多 `18` 个 case-estimand cells，冻结 simultaneous Hoeffding bound 为：

```text
epsilon = sqrt(log(2 * 18 / 0.05) / (2 * 4096)) < 0.028340.
```

没有 outcome-driven retry，也没有更换失败案例。

## 6. Exact/DES 结果

| Case | Exact `(global, local, selected)` | DES `(global, local, selected)` | max abs error | Compatible |
| --- | --- | --- | ---: | --- |
| bridge | `(0, 0.3333333333333333, 0.3333333333333333)` | `(0, 0.33642578125, 0.33642578125)` | `0.0030924479166667` | yes |
| global/local precedence control | `(1, 0, 1)` | `(1, 0, 1)` | `0` | yes |
| completion bypass control | `(0, 0, 0)` | `(0, 0, 0)` | `0` | yes |
| time-zero `D_global` positive | `(1, 0, 1)` | `(1, 0, 1)` | `0` | yes |
| A2b `D_local` positive | `(0, 1, 1)` | `(0, 1, 1)` | `0` | yes |
| complete-LTS `D_local` positive | `(0, 1, 1)` | `(0, 1, 1)` | `0` | yes |

DES counts and mean stopped times:

| Case | `D_global` | `D_local` | `F` | exact mean time | DES mean time |
| --- | ---: | ---: | ---: | ---: | ---: |
| bridge | 0 | 1378 | 2718 | `0.3333333333333333` | `0.33568223553583404` |
| precedence control | 4096 | 0 | 0 | `0` | `0` |
| bypass control | 0 | 0 | 4096 | `2` | `2.0179046383604264` |
| global positive | 4096 | 0 | 0 | `0` | `0` |
| A2b local positive | 0 | 4096 | 0 | `0` | `0` |
| complete-LTS local positive | 0 | 4096 | 0 | `0.5` | `0.5035233533037509` |

所有六个 case 使用同一 replication-index set，因此 seed digest 相同：

`a4424776123aaf2dc7163ebbb0fba3cc3b5475161ec69ec98d6c182b979a30a1`.

这表示随机索引身份一致，不表示不同 case 的结果统计独立，也不表示对 retired
studies 的独立复现。

## 7. Evidence integrity

Write-once evidence root:

`evidence/article_core/minimal_closure_v1/`

| Artifact | raw SHA-256 |
| --- | --- |
| `article_case_certificates.json` | `7ddbc11f296c396c6df04b4647cc01f0020869c35ed8d4f2aee6a6f8cde0446b` |
| `exact_results.json` | `e9b9758d43df85847dccaae0676d4e976221d1829da959e73a9fe0794b9b5f3a` |
| `des_results.json` | `c20cdfd60219fc66d7838b42532228acabc3361ef1f5e59f178340cf7c48ea3b` |
| `article_closure_report.json` | `135c939bad1f2e335147f887fccdb9493db59210b16ae1ecb8f7953fefddd037` |
| `article_closure_manifest.json` | `d8b409d6bfb766ab6b992c187afd849e4e67d77cbb34751ffd418574c7b5a98c` |

Manifest self SHA-256:

`1693342ac470b72f9b813edccb772f85751045940a243f7abc9241877cab0c77`.

Fresh verification reproduced all four child raw hashes, all five artifact
self-hashes, and the manifest-last flag.

## 8. Verification evidence

Completed checks:

- article-core RED test: expected import failure before implementation;
- article-core GREEN test after final typing repair: `9 passed in 0.74s`;
- full in-memory preflight: 18/18 compatible, Tier A, `0.635 s`;
- write-once execution: 18/18 compatible, Tier A, `0.702 s`;
- artifact raw/self hash verification: passed;
- four-file G6-B long group with four xdist workers:
  `1885 passed, 2 skipped in 2229.49s` (`2230.28 s` observed wall time);
- disjoint remainder of the repository with eight xdist workers:
  `808 passed in 88.95s`;
- full disjoint-union result: `2693 passed, 2 skipped, 0 failed`;
- `ruff check .`: passed;
- `ruff format --check src tests`: `53 files already formatted`;
- strict mypy with `--explicit-package-bases src tests`:
  `Success: no issues found in 53 source files`;
- `git diff --check`: passed and the validated worktree was clean.

The repository-root Ruff format command also scans fenced Python examples in
Markdown and would reformat four pre-existing historical plan documents. Those
frozen plans were deliberately left unchanged; the complete executable
`src tests` surface is format-clean.

Two historical Task6 guards initially compared old absence/scope claims against
the moving current worktree. The repairs pin both assertions to the reviewed
Task6 subject commit `42856b991059d6f800eb0244fa7847187da3bccd`.
Focused verification passed `18 passed, 1120 deselected in 0.43s` for the path
scope guard and `1 passed, 195 deselected in 0.23s` for the deferred-module
absence guard. Neither repair changes a model, case, rate, solver, classifier,
or evidence object.

## 9. Claim decision

Frozen ladder result:

```text
tier_a_dual_route_closure
```

Allowed interpretation:

- the A2b sufficient route and complete finite-LTS fallback each have a matched
  constructive witness;
- the two main semantic boundary controls behave as required;
- exact and DES agree within the frozen same-target tolerance;
- the theory and cases form a scoped, internally consistent article narrative.

Forbidden interpretation:

- no G6-B PASS;
- no held-out confirmation;
- no universal completeness or necessity claim for A2b;
- no claim that all IMS-RAS/AGV/reservation models are covered;
- no production-performance, rare-event-efficiency, or method-superiority claim;
- no erasure of the original eight noncore cases, `119/62` normalization record,
  G5 `4/3/2`, transparent `6/1/2`, minimality failures, or G6-R R1/R2 failures.

## 10. Remaining work

The article-core science, manuscript, claim matrix, and local repository
validation are closed. Remaining work is publication/integration only:

1. publish this validated branch as a Draft PR stacked on the still-open retired
   normalization PR;
2. verify the remote PR head/base and any CI result without upgrading the claim;
3. leave original full-overlap G6-B and later G6-C/D/E as separately scoped
   optional future work, not prerequisites for this article.
