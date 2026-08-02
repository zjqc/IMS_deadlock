# IMS Deadlock 当前项目交接

更新时间：2026-08-02（Asia/Shanghai）

本文件是下一 Codex 进程接管 `IMS_deadlock` 的单一入口。它汇总当前权威
版本、已经成立的受限结论、失败与负证据、可复现实验状态、尚未通过的硬门、
下一步顺序以及禁止越过的科学边界。

如果本文件与实时 Git 状态冲突，以重新锁定后的远程权威工作区及其跟踪文件
为准；不得用聊天记录、旧 worktree 或本地快照替代实时锁定。

## 1. 一句话状态

项目已完成理论优先基础、受限结构—概率—控制主链、范围受限文献门、小有限
模型算法门、历史 G4 冻结与 G5 一次性执行，以及针对 G5 暴露缺陷的 G6-A
理论/代码恢复和 G6-R 历史机制重放。

当前不是论文门通过状态：

- `G5 = FAIL（evidence closed）`；
- `G6-A = PASS`；
- `G6-R = PASS（historical replay only）`；
- `G6-B = NEXT HARD GATE / OPEN`；
- `G6-C/D/E = 均未开始，均未通过`；
- 尚无完整论文主文件，也不能声称达到投稿或顶刊就绪状态。

G6-B 当前为 schema-only governance v2 的 exact-twelve nested bundle，状态是
`ROW_FAMILY_BUNDLE_IMPLEMENTED` 和 `OPEN/PENDING`。初始 Section 18
evidence-publication successor 是
`8336131af19dfa98fceda80fc79dd349b43f19a9`；其后的 handoff 修订仍只是
document-only successor。包含本文件的实际当前文档提交必须用
`git log -1 --format=%H -- PROJECT_HANDOFF.md` 重新定位。最终 Section 18
evidence subject commit 仍是
`948ff5746adcb66b68fb9c47e519f070dd2c96ba`；批准规格
SHA-256 是 `b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6`，
冻结 matrix raw SHA-256 是
`487d81aa79a7bca681db81f19a4d6bd315668c43b1c4538c47f01f099d8e205f`。
四个 capability 仍严格为 `case_construction_authorized=false`、
`retired_authority_fingerprint_normalization_authorized=false`、
`target_certification_preflight_authorized=false`、
`quantitative_execution_authorized=false`。later instance roots 全部 absent；
没有创建 case，没有运行 retired-authority normalization、Barrier-A preflight、
CTMC 或 DES，没有检查 quantitative/scientific output，也没有 G6-B scientific
verdict。Section 18 independent review 已完成并批准：ontology 无 P0-P2，
scientific/boundary 无 P0-P2，code/capability P0-P3 为零；审稿时唯一指出的
P3 evidence-publication sync 由本次文档更新关闭。当时的 first unchecked next
step 是 separately approved case-construction plan；该 plan-only 批次现已完成，
但 exact-bytes 用户批准仍未获得，不能直接进入 construction 或 science。

2026-08-02 的 PR 独立审查随后发现两个工程/治理授权缺口：缺少显式 fail-closed
Barrier-A preflight authorization validator，以及 retired-normalization
authorization 未强制 `authorized is True` 和
`invalidated_by_identity_drift is False`。两项均在 remediation subject
`b2f2f285a68793ce9ca4cb1b47a05dd7a3cfb9bb` 修复；focused schema
`379 passed`、preflight focus `20 passed`、Ruff/format/strict mypy/diff
通过，fresh full repository 为
`2145 passed, 2 skipped in 2766.88s (0:46:06)`；完整记录见
`docs/verification/G6_B_AUTHORIZATION_GATE_REMEDIATION_REVIEW.md`。该修复没有
打开任何 capability，也没有创建 later root。另发现 case-construction schema
对 predeclared `estimand_id` 同时 required/prohibited 的 future-instance 矛盾；它
必须由下一份 exact plan/corrigendum 关闭，不能由执行者自行解释。

包含 remediation review 的文档后继只额外修改
`tests/test_g6b_row_family_protocol.py` 中两条相互对应的 declared-path
allowlist/精确集合断言。未列入新文档时 scope guard 按预期 RED
（`1 failed, 1 passed`）；只更新 allowlist 后，精确集合断言又按预期 RED
（`1 failed, 1 passed`）；同步断言后 direct `2 passed`、Task-6 selection
`17 passed, 1111 deselected`，该测试文件 Ruff/format/strict mypy 与 diff
check 均通过；无 production code/schema 变化。`2145` 项 full suite 仍精确
绑定 `b2f2f285...`，不得误写成文档后继自身的 full-suite count。

G6-B case-construction 计划已发布为
`docs/superpowers/plans/2026-08-02-g6b-case-construction.md`，exact SHA-256 为
`c20393328f8f98e7b35a6507fd6e993b2f17e068d977c3dc6253b05e9a75de5f`；三路
独立审查记录是
`docs/verification/G6_B_CASE_CONSTRUCTION_PLAN_REVIEW.md`，exact SHA-256 为
`297a69382347e16e894af63e70f8fa95807407048b2e89c45701410a4e9289e1`。
ontology/estimand、scientific-boundary/nonreuse、architecture/code/capability
三路均为 `APPROVE`，Critical/High/Medium 均为 0。该计划冻结 13 case units、
26 method observations、13 companion groups，并把 `estimand_id` 矛盾限定为
Task 1 的 exact two-path corrigendum；这些是计划内容，不是实例或结果。当前
唯一 first unchecked task 是用户明确批准上述 plan hash 和 review hash；在此
之前不得创建 construction authorization 或任何 case byte。

计划发布的 fail-closed changed-path guard 在两个新文档路径尚未声明时按预期
RED（`1 failed`，两条路径均为 `outside_task6_declared_files`）。测试后继只新增
这两个计划文档的精确集合及断言，并继续显式拒绝 governance-instance 路径；
final direct 为 `2 passed`，Task-6 selection 为
`17 passed, 1112 deselected`，测试文件 Ruff/format/strict mypy 和 diff check
均通过。该测试后继不允许 production/schema/case/evidence/artifact 路径。
计划发布 subject 是 `bb312fc8db94e977f5c483043715c805fafc86c7`，已推送到
`codex/g6b-case-construction-plan` 并建立堆叠 Draft PR #5：
`https://github.com/zjqc/IMS_deadlock/pull/5`；base 是 PR #4 的
`codex/g6b-case-target-certification-final-review`；包含当前 PR 状态文档后继后，
#5 显示 2 commits / 5
paths。PR #5 的 draft/merge 状态不改变 `USER_APPROVAL_PENDING`。

### 1.1 2026-08-02 当前接管快照

| 工作面 | 当前状态 | 下一动作 |
| --- | --- | --- |
| Section 18 schema/governance v2 | `COMPLETE / PASS_SCHEMA_ONLY`；代码审查对象固定为 `948ff5746adcb66b68fb9c47e519f070dd2c96ba` | 不再重跑 Task 1-7；仅在代码/schema/冻结协议/证据对象变化时重跑完整验证 |
| G6-B case construction | `PLAN PUBLISHED / USER APPROVAL PENDING / CONSTRUCTION NOT STARTED`；plan SHA `c2039332...`，review SHA `297a6938...`，三路 `APPROVE` 0 Critical/High/Medium；`case_construction_authorized=false` | 仅等待用户对两个 exact SHA-256 的明确批准；批准前不得写 construction authorization 或 case byte |
| retired-authority normalization | `NOT AUTHORIZED / NOT RUN` | case sealing 后另开 data-only authorization；不得读取历史 outcome 反推案例 |
| overlap audit | `NOT RUN` | 仅在 sealed inputs 完成后运行；hash 不等同于语义独立性证明 |
| Barrier A target preflight | `NOT AUTHORIZED / NOT RUN` | overlap PASS 后另行授权，只能产出 certificate/refusal/preflight evidence |
| Barrier B quantitative science | `NOT AUTHORIZED / NOT RUN` | exact/DES same-target locks 与单独定量授权完成后，才可运行 CTMC/DES |
| G6-C/D/E | 全部 `NOT STARTED / NOT PASSED` | 只有 G6-B 全条件通过后才能进入 confirmation preregistration、freeze、一次性执行 |
| 论文 | 无统一主稿，paper gate 未通过 | 保留 G5 FAIL、R1/R2 failure、R3 historical-only 与 minimality failures；G6-E 后重建 paper gate |
| Git 集成 | Draft PR #4 `https://github.com/zjqc/IMS_deadlock/pull/4` 已更新到 `004bc7d3...`；stacked Draft PR #5 `https://github.com/zjqc/IMS_deadlock/pull/5` 发布 plan subject `bb312fc8...`，base 为 PR #4 分支；`main` 仍是 `9c707ce3d990541847aee745bec211bb55c74f6b` | 保持 #4/#5 为 draft；不得在未获 merge authority 时合并，且 merge 不构成 plan exact-bytes 批准 |
| 非阻塞工程卫生 | 批准门 `ruff format --check src tests` 为 47 files green；更宽的 `ruff format --check .` 仍会对 3 个历史 plan 文档代码块提出格式建议 | 作为历史文档格式债保留；若清理，必须单独审查且不得改动批准规格 digest、冻结协议或证据 bytes |

当前没有代码运行失败，也不是因理论—实现比较得出矛盾而停机。最近的停顿发生
在交接状态审查层：文档一度混淆 review subject、document successor 与 `main`
基线，并把本地不完整镜像缺少的 plan 文件误判为远程权威仓库缺失。远程仓库
实际保有 `docs/superpowers/plans/` 下的历史执行计划；本文件已按远程事实恢复
索引。该问题不改变代码 tree 或科学结论。

上述 3 处 broad-format 建议不是 Python 代码失败、测试失败或科学不一致，也不能
包装成全仓 format clean。它们目前不阻塞 case-construction plan，但下一进程在
报告质量门时必须区分“批准的 `src tests` scope green”和“历史 Markdown plan
代码块仍有格式建议”。

### 1.2 状态源层级与两个冻结旧字段

下一进程必须按以下优先级解释状态，低层记录不得覆盖高层实时证据：

1. 实时远程 Git 锁：exact worktree、branch、HEAD、upstream、dirty state、
   `main...HEAD` 与 task-owned diff；
2. 科学身份锁：批准规格 digest、冻结 matrix digest、Section 18 review subject；
3. 当前状态文档：本交接、`docs/ROADMAP.md`、Section 18 review record 和 ledger；
4. 历史 implementation plan 的 checkbox、旧标题或旧 footer，仅说明当时的写作
   状态，不是当前 progress oracle。

批准规格 `docs/superpowers/specs/2026-08-01-g6b-case-target-certification-design.md`
内部仍有 `HARDENED REVISION AWAITING USER REVIEW` 及同义 footer。这是批准前
写入、现被冻结在 SHA-256
`b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6`
中的历史 metadata；用户后来批准的是这组 exact bytes。外部批准记录覆盖该旧
状态文字，但不授权修改规格 bytes。若修改该规格，digest 会改变，必须重新审查
和批准。

`docs/superpowers/plans/2026-08-01-g6b-schema-only-governance-v2-implementation.md`
中的 checkbox 仍为未勾选，不能据此重跑 Task 1。Tasks 1-7 已实施并由 Section 18
证据关闭；该文件是历史 execution instruction，不是进度账本。新的
case-construction plan 和三路审查已经发布；当前真正的 first unchecked task 是
用户对 plan SHA `c2039332...` 与 review SHA `297a6938...` 的明确批准。

## 2. 权威目标与版本锁

### 2.1 权威仓库

- 本地协调目录：
  `<LOCAL_COORDINATION_DIR>`，即启动任务时包含本地 `AGENTS.md` 和
  `REMOTE_PROJECT_OPERATIONS.md` 的目录
- 本地材料化快照：
  `<LOCAL_COORDINATION_DIR>/bootstrap_source`
- SSH alias 和远程权威主工作区：从本地
  `REMOTE_PROJECT_OPERATIONS.md` 读取并在每个会话重新核验；不要把本机
  用户名、私有网络地址或个人 SSH 配置复制进 Git
- GitHub：`git@github.com:zjqc/IMS_deadlock.git`
- 当前 G6-B v2 权威工作树：
  `D:\worktree\IMS_deadlock-g6b-spec-final-review`，branch
  `codex/g6b-case-target-certification-final-review`。初始 Section 18 发布 HEAD
  `8336131af19dfa98fceda80fc79dd349b43f19a9` 已推送且提交后
  `HEAD...upstream = 0/0`、工作树 clean；它相对最终 Section 18 evidence subject
  `948ff5746adcb66b68fb9c47e519f070dd2c96ba` 只改四个文档：
  `PROJECT_HANDOFF.md`、`docs/ROADMAP.md`、
  `docs/cases/CASE_CHANGE_LEDGER.md` 和
  `docs/verification/G6_B_CASE_TARGET_SCHEMA_V2_REVIEW.md`。包含本文件的当前
  continuation commit 是上述发布 HEAD 的 document-only 后继，必须实时锁定，
  不应硬编码成 scientific review subject。其后的授权门 remediation code
  subject 是 `b2f2f285a68793ce9ca4cb1b47a05dd7a3cfb9bb`；包含 remediation review
  与本交接更新的 documentation successor 仍须从实时 Git history 定位。
- 当前批准规格：
  `docs/superpowers/specs/2026-08-01-g6b-case-target-certification-design.md`，
  SHA-256
  `b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6`。
- Historical/pre-repair Task-5 权威远端证据：四文件集成 suite
  `1478 passed, 2 skipped in 2672.43s (0:44:32)`；schema suite
  `160 passed`；Section 17.3 requirements 1-44 的 manifest/collection audit
  `1 passed, 1108 deselected`；touched Python Ruff、format、mypy 和
  `git diff --check` 均通过。两个 skip 是既有受控 skip，不是 xfail 或隐藏失败。
- Task-6 / final Section 18 权威远端证据：schema suite `356 passed`；
  Git-scope audit `19 passed`；four-file suite `1695 passed, 2 skipped`；
  full repository suite `2122 passed, 2 skipped`；retired focus `1 passed`；
  manifest audit `1 passed`；Ruff full green；Ruff format `47 files already
  formatted`；strict mypy `src` passed on 25 source files；strict mypy
  `src tests` passed on 47 source/test files；tracked JSON parse/duplicate
  checks covered `53 files`；sets check `5/12`；authorization fields `21` with
  true count `0`；future roots/modules `0`；canonical vectors `19` matched on
  remote Python 3.13.9, local Python 3.12.3, and local Python 3.13.5；diff
  checks green。
- `D:\worktree\IMS_deadlock-g6b-case-target-design@719194c` 是 stale
  exact-eleven plan 的隔离证据，不是代码源、测试 oracle 或当前状态依据；当前
  candidate diff 不得包含其路径或字节。
- 当前主线对照基线：`main@9c707ce3d990541847aee745bec211bb55c74f6b`。
  当前 G6-B 发布分支相对其保持隔离，不得把 feature 分支 HEAD 误写成主线
  通过状态。当前 code remediation subject 为 `b2f2f285...`；包含本文件的
  documentation successor 会使领先数增加，下一进程必须实时重算
  `main...HEAD`、`HEAD...upstream` 和 clean state。
- 分支处置方式已由用户选择为方式 2：推送当前 feature branch 并创建 PR。
  Draft PR #4 已建立：`https://github.com/zjqc/IMS_deadlock/pull/4`。它尚未
  merge，也没有获得 merge authority；已知 pre-case blocker 和计划审批门关闭前
  必须保持 draft，不能写成已进入 `main`。
- 计划发布分支 `codex/g6b-case-construction-plan` 已在 subject
  `bb312fc8db94e977f5c483043715c805fafc86c7` 建立 stacked Draft PR #5：
  `https://github.com/zjqc/IMS_deadlock/pull/5`，base 为
  `codex/g6b-case-target-certification-final-review`。该堆叠结构只隔离 diff，
  不赋予 merge authority 或 exact-bytes approval。
- 历史交接编写前锁定 `main@235b69a189a869578d9760fcc5585fbfe21a7808`
  和 tree `9ffa5974ced053e3ffd9943f34e163c4606eddf2` 仅是旧交接快照，
  不再是当前 G6-B continuation 的目标锁。
- G6-B protocol foundation feature-branch pre-integration evidence:
  worktree `D:\worktree\IMS_deadlock-g6b-discovery`, branch
  `codex/g6b-discovery-estimand-lock`, base
  `main@9c707ce3d990541847aee745bec211bb55c74f6b`, plan commit
  `c3b739c53befc93ff246637e1686d4a0867d44ed`, protocol foundation commit
  `73cbbbc52be59fa6a14fcd2a4cf647ea5dc8f811`, validator commit
  `4c24f39dfd1b47fee874a2315ee77759b51311cb`.
- Feature-branch validation evidence before this local documentation update:
  locked worktree `D:\worktree\IMS_deadlock-g6b-discovery` at HEAD `4c24f39`
  before state-doc commit passed full pytest `393 passed in 47.22s`; Ruff check
  passed; Ruff format reported 41 files already formatted; strict mypy `src`
  passed on 22 source files; strict mypy `src+tests` passed on 41 source files;
  five protocol JSON parse checks passed; targeted protocol tests
  `52 passed in 2.48s`; `git diff --check` passed.
- Earlier row-family Phase A validation evidence before the first documentation
  commit:
  locked worktree `D:\worktree\IMS_deadlock-g6b-discovery`, branch
  `codex/g6b-discovery-estimand-lock`, HEAD
  `4fda4896d2284c360f3021e48475f7678b0f37fd`, no upstream, with the Task 8
  candidate dirty only in the five state-document files listed in this handoff,
  Python `D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe`
  version 3.13.9; exact `PYTHONPATH` pointed at
  `D:\worktree\IMS_deadlock-g6b-discovery\src`,
  `PYTHONDONTWRITEBYTECODE=1`, pytest cache disabled, Ruff no-cache, mypy
  no-incremental. Fresh checks passed: full pytest
  `1307 passed in 150.84s`; Ruff check `All checks passed!`; Ruff format
  `43 files already formatted`; strict mypy `src` passed on 23 source files;
  strict mypy `src tests` passed on 43 source files; `git diff --check` passed;
  all eight nested JSON parsed with `python -m json.tool`; top-level
  `cases/discovery/g6b/` JSON set is exactly five; nested row-family JSON set
  is exactly eight; top-level foundation suite `52 passed in 5.00s`;
  canonical row-family test `1 passed in 0.12s`; canonical row-family
  validator returned `valid=True`, errors empty, `science=False`,
  `case=False`, `adversarial_review_status=PENDING`,
  `current_state=ROW_FAMILY_BUNDLE_IMPLEMENTED`, and 8 hashes; recursive scan
  found 8 scientific authorization occurrences all false, 18 case
  authorization occurrences all false, and both review-status occurrences
  `PENDING`. Git diff `a4897ab..4fda489` for Tasks 1-7 contains only the
  eight row-family JSON files, `src/ims_deadlock/g6b_row_family_protocol.py`,
  and `tests/test_g6b_row_family_protocol.py`; therefore no case artifact,
  actual overlap report/value, current lock, output root, result/science
  summary, enumeration, CTMC, or DES artifact was introduced. Task-owned mypy
  cache directories `D:\worktree\_task8_mypy_src_cache` and
  `D:\worktree\_task8_mypy_src_tests_cache` are absent.
- Row-family Phase C post-commit verification evidence on committed HEAD
  `13adc15e8b7b8047a25ab5a340880621ee3ad0bd`:
  locked worktree `D:\worktree\IMS_deadlock-g6b-discovery`, branch
  `codex/g6b-discovery-estimand-lock`, `NO_UPSTREAM`, clean; Python
  `D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe`
  version 3.13.9; full pytest `1307 passed in 144.93s (0:02:24)`;
  Ruff check passed; Ruff format `43 files already formatted`; strict mypy
  `src` passed on 23 source files; strict mypy `src tests` passed on 43
  source files; `git diff --check` passed; foundation suite
  `52 passed in 9.87s`; canonical row-family test `1 passed in 0.09s`;
  8/8 nested JSON parsed; top-level JSON set exact five; nested row-family
  JSON set exact eight; foundation validator valid/errors0/science false/
  `PENDING`/hashes5; row-family validator valid/errors0/science false/case
  false/`PENDING`/`ROW_FAMILY_BUNDLE_IMPLEMENTED`/hashes8; recursive
  13-JSON scan `non_false_auth=0` and `non_pending_status=0`; base diff
  forbidden paths=0 and actual marker hits=0; relevant output roots absent;
  task mypy cache dirs absent; three verdicts recorded. This is post-commit
  evidence for `13adc15...`; any later evidence-only closure-doc commit will
  create a new HEAD and must be re-locked/revalidated before being externally
  claimed complete.

若本文件已发布为 feature 分支上的 evidence-only 文档后继，包含它的提交会
是上述 Section 18 evidence subject 的后继，但不替代该 evidence subject。
下一进程不得把交接前 SHA 或 review subject SHA 当作当前发布 HEAD，必须重新
运行锁定命令。实际包含本文件的提交可用以下命令定位：

```bash
git log -1 --format=%H -- PROJECT_HANDOFF.md
```

本地 `bootstrap_source` 不是 Git worktree。交接审计时，其 G4 structural
protocol 可解析九个案例且返回 `valid=true`，但本地 `g4_freeze check`
因六个 tracked-file byte hash 不匹配而返回 `NOT_FROZEN`。这不推翻 Dell
精确冻结工作树曾返回的 `FROZEN` 证据，也不能用来重封存 G4；它证明本地
快照不能承担 file-byte freeze authority。需要复核 G4 freeze 时，应使用
锁定的远程干净 checkout 和冻结 bundle，不能“修复”本地快照哈希。

### 2.2 历史/证据 worktree

下列 worktree 是运行时或历史证据对象，不是默认开发目标：

| 用途 | 路径或 ref | 边界 |
| --- | --- | --- |
| 项目 Python 环境 | `D:\worktree\IMS_deadlock-final-integration\.venv` | 仅复用解释器；必须用 `PYTHONPATH` 指向当前精确工作树 |
| 历史 G4/G5 冻结权威 | `D:\worktree\IMS_deadlock-g5-confirmation` | 只读证据源；不得改写、补跑或清理 |
| R3 不可变代码 | `D:\worktree\IMS_deadlock-g6-replay-code-v3` | `codex/g6-replay-code-r3@7b213d279ca6d57b0a8f8e904f4028b315e9b2b5` |
| R3 tree | `9349bf891acc8d68925ba35e72463663fedab5a4` | 历史机制回归代码锁 |
| G6 最终集成审计 | `D:\worktree\IMS_deadlock-g6-final-integration` | detached `b5f6fb6ac09a0e11efa98218e004687c3035fffc`，只作比较 |

不得从其他 worktree 的分支名、HEAD 或脏状态推断主工作区状态。

## 3. 下一进程必须先做的锁定

开始任何阅读结论、编辑、测试或实验前：

1. 阅读本地 `AGENTS.md` 和 `REMOTE_PROJECT_OPERATIONS.md`。
2. 重新核验 SSH 身份、远程路径、仓库 URL、branch、HEAD、dirty state、
   upstream 和 ahead/behind。
3. 枚举 worktree，只把任务明确锁定的工作树当作编辑对象。
4. 从项目自己的 `pyproject.toml`、README 和测试证据确认运行时，不从
   `buffer-design`、`makespan_doob_h` 或旧制造岛项目继承环境。
5. 若需要编辑，建立新的任务分支和独立 worktree；保留所有历史证据
   worktree。

建议的只读锁定命令：

```bash
# <SSH_ALIAS> 必须取自本地操作契约。
ssh -o BatchMode=yes -o ConnectTimeout=10 <SSH_ALIAS> \
  "echo SSH_OK && hostname && whoami"
ssh -o BatchMode=yes -o ConnectTimeout=10 <SSH_ALIAS> \
  "cd /d D:\worktree\IMS_deadlock-g6b-spec-final-review && git rev-parse --show-toplevel && git branch --show-current && git rev-parse HEAD && git status --short && git remote get-url origin && git rev-list --left-right --count @{u}...HEAD && git worktree list --porcelain"
```

若任务不是继续当前 G6-B publication/review 分支，才按
`REMOTE_PROJECT_OPERATIONS.md` 重新选择对应远程路径；不要把私有网络地址
复制进仓库文档。

任何结论中都应记录：

```text
TARGET_PATH=
TARGET_BRANCH=
START_HEAD=
START_DIRTY_STATE=
UPSTREAM_AHEAD_BEHIND=
OWNED_PATHS=
RUNTIME=
VALIDATION_COMMANDS=
```

## 4. 研究问题与首篇论文边界

项目研究对象是有限批 `IMS-RAS`：有限容量机器、输入/输出缓冲、BAS
blocked-unload、工件路线、资源持有—请求—释放、运输/AGV/预约以及零时间
事件闭包。

理论主线是：

```text
IMS-RAS^CW 稳定语义
-> 有限 stable LTS / reachability net
-> capacity-mediated closed blocking core
-> 受限 IMS-SIP^1 wait-snapshot Petri bridge
-> 受限结构无死锁条件和可达阈值
-> competing-absorption CTMC
-> exact finite nonblocking supervisor
-> G6 local-first-hit / terminal-stopping partition
```

首篇论文当前排除：

- 设备故障与维修；
- 抢占；
- 动态插单或无限外生到达；
- 未显式建模的外部 drain；
- 未封闭的 transition registry；
- 一般替代/AND 请求上的全局等价；
- 一般 AGV/预约或多 persistent-buffer 精确阈值；
- 未证明的紧凑输入多项式复杂性；
- 未完成的 risk-budget/Pareto 控制定理。

## 5. Gate 总表

| Gate | 当前状态 | 已关闭内容 | 仍开放或禁止升级 |
| --- | --- | --- | --- |
| G0 仓库门 | PASS | Dell 目标、GitHub SSH、项目运行时、干净主线与隔离历史已核验 | 每个新进程仍须实时重锁 |
| G1 文献门 | PASS（scope-bounded） | 六条文献链、43 项矩阵、20 个全文锚点、L30-L35 与 B05 全文审计、迁移卡和失败账本 | 不代表系统综述、首创性或一般 IMS/Petri 等价 |
| G2 理论门 | PASS（严格受限） | P1、P2/P2c、P3/P3d/P3e、P4、P5、P6 的受限主链 | 一般 plant/S3PR 桥、一般岛阈值、risk-budget 控制仍开放 |
| G3 算法门 | PASS | 稳定 LTS、证书、Petri/refusal、阈值、CTMC、监督器、G4/G5/G6 审计；全库 341 tests | 枚举只核验证明，不替代证明 |
| G4 案例冻结门 | PASS（历史 seal） | 九个 held-out 案例在结果检查前冻结，并在 G5 原样执行 | 该面板已退役，不能再次作为 held-out |
| G5 论文门 | FAIL（evidence closed） | 9/9 primary/repro 精确一致，失败、反例和 inconclusive 已固定 | 不得补跑、改 sealed input、重调参或宣称通过 |
| G6 恢复门 | IN PROGRESS | G6-A 和 G6-R 通过；G6-B schema-only governance v2 exact-twelve bundle 已在 historical/pre-repair Task-5 subject `9ef6fcec9e410b2ab7afc4144df8b948a238d95f` 实现，并在 final Section 18 evidence subject `948ff5746adcb66b68fb9c47e519f070dd2c96ba` 完成 independent review publication；final evidence 包括 schema `356 passed`、Git-scope `19 passed`、four-file `1695 passed, 2 skipped`、full repo `2122 passed, 2 skipped`、JSON duplicate parse `53 files`、canonical `19` on three runtimes、Ruff/format/mypy/diff checks green；批准规格 SHA-256 与 frozen matrix raw SHA-256 均匹配 | G6-B 保持 `OPEN/PENDING`；四个 typed capabilities 全 false，later instance roots absent；无 case、normalization run、overlap instance、preflight、CTMC、DES、output inspection 或 scientific verdict；G6-C/D/E 未通过；first unchecked next step 只能是 separately approved case-construction plan |

状态源：`docs/ROADMAP.md`。

## 6. 已完成的理论结果

### 6.1 形式语义与有限状态桥

- 固化 `IMS-RAS^CW` 的资源、容量、持有、请求替代、BAS、运输/预约和
  zero-time closure 语义。
- 构造有限 stable LTS 和 reachability net。
- 程序对象保持确定性 state ID、stable signature、最短可达前缀和
  transition evidence。

主要文件：

- `docs/theory/FORMAL_SEMANTICS.md`
- `docs/theory/IMS_RAS_FORMALISM.md`
- `docs/theory/CORE_THEOREMS_AND_PROOFS.md`
- `src/ims_deadlock/model.py`
- `src/ims_deadlock/engine.py`
- `src/ims_deadlock/analysis.py`

### 6.2 死锁证书和 Petri 边界

- capacity-aware closed blocking core 用逐替代容量缺口，而不是“存在简单
  环”作为一般充分判据。
- 单实例受限情形可退化到环直觉，多容量一般情形保留反例。
- `IMS-SIP^1` 只构造 state-induced wait-snapshot diagnostic net。
- 满足声明条件时返回受限最小空虹吸双向桥；不满足时返回精确拒绝，不能
  伪造一般 S3PR/plant 结论。

主要文件：

- `docs/theory/DEADLOCK_CERTIFICATES.md`
- `docs/theory/PETRI_BRIDGE.md`
- `src/ims_deadlock/certificates.py`
- `src/ims_deadlock/petri.py`

### 6.3 结构阈值

- P3：严格全局资源请求偏序无环是受限无死锁充分条件。
- P3d / `BIX1-SAT`：从空持有状态得到受限可达饱和阈值。
- P3e / `BIX2-PERSIST`：单位需求、单当前持有、三资源
  persistent-buffer ring 的精确阈值，以及同语义删回流 DAG 修复。
- BIX2 发现网格 32 行，0 mismatch、0 truncation；ring 预测与观察均为
  4 个正例；DAG 16/16 可达完成且无死锁。

P3e 不覆盖替代路线、AND 请求、AGV/预约、多个 persistent buffers、
隐藏释放或外部 drain。

### 6.4 概率与控制

- 有限 competing-absorption CTMC 支持 committor、平均吸收时间、残差、
  灵敏度和 Doob-\(h\) 条件生成元。
- exact finite full-observation supervisor 支持不可控闭合、marked
  coaccessibility 和最大安全域基准。
- 当前结果不是一般风险预算控制或 Pareto 最优性定理。

主要文件：

- `docs/theory/PROBABILITY_LAYER.md`
- `docs/theory/CONTROL_LAYER.md`
- `src/ims_deadlock/ctmc.py`
- `src/ims_deadlock/stochastic.py`
- `src/ims_deadlock/engine.py`

### 6.5 G6 局部核—终端类恢复

已实现并证明/审计的受限内容：

- theorem prediction、ancillary metric 和 execution status 分层；
- global certificate 与 all-minimal local kernel family 分层；
- CRP partial bridge 只消费声明的 local-kernel family；
- `D_global`、`D_local`、`F`、`R_livelock`、`R_terminal` 分类；
- `K_local`/local candidates 只有通过 accepted A2b proof 建立 declared
  finite semantics 下的 structural irreversibility，或通过 complete-LTS
  completion-nonreachability audit 后，才可进入 `D_local`；否则必须保留为
  candidate/refusal，不能进入 selected bad evidence；
- `theta_G=P(T_G<T_F)` 和
  `theta_L=P(T_L<T_F)` 是不同版本化 estimand；
- 同一过程和 completion 集下有 `theta_G <= theta_L`；
- exact CTMC 和 DES 必须共享同一冻结 stopping semantics；
- unselected reachable closed class、缺 rate、截断 LTS 或 registry
  不一致时必须结构化拒绝。

核心文件：

- `docs/theory/G6_LOCAL_FIRST_HIT_AND_STOPPING_THEOREMS.md`
- `src/ims_deadlock/terminal_classes.py`
- `tests/test_terminal_classes.py`
- `docs/cases/G6_B_DISCOVERY_PROTOCOL.md`
- `cases/discovery/g6b/`
- `src/ims_deadlock/g6b_protocol.py`
- `tests/test_g6b_protocol.py`

## 7. 文献工程状态

G1 只在当前首篇论文受限范围内通过：

- Petri/S3PR；
- DES/RAS；
- 有限缓冲排队网络；
- AGV/交通资源；
- 吸收 CTMC；
- 稀有事件。

已建立：

- 文献矩阵和 DOI/来源状态；
- 全文定理定位；
- 迁移卡；
- 引文追踪日志；
- 错误 DOI、误归类和不可迁移条件账本；
- L30-L35 与 B05 的七篇全文审计；
- 两轮范围受限类别饱和。

下一进程不得把 `METADATA`、`ABSTRACT` 或二手摘要升级成定理依据。借鉴
证明技术时必须同时记录原定理、原假设、IMS 映射、缺失假设、适配证明或
反例，并在论文中相邻引用；禁止用“改写得不像”代替合理归因。

主要文件：

- `docs/literature/LITERATURE_MATRIX.md`
- `docs/literature/ANNOTATED_BIBLIOGRAPHY.md`
- `docs/literature/MIGRATION_CARDS.md`
- `docs/literature/SOURCE_VERIFICATION.md`
- `docs/literature/FULLTEXT_AUDIT_L30_L35_B05.md`
- `docs/literature/ADAPTATION_AND_ATTRIBUTION_PROTOCOL.md`
- `docs/literature/FAILURE_LEDGER.md`

当前没有阻塞 G6-B 的 Priority A/B 全文缺口。新增文献只有在改变模型类别、
定理类型、关键反例或 G6 独立案例设计时才进入主链。

## 8. 案例与实验状态

### 8.1 发现集

- `C0`：两资源最小死锁。
- `C1`：有环但容量/WIP 不足，反驳“有环即死锁”。
- `C2`：严格资源顺序无环。
- `C3`：多实例资源，比较 cycle、knot 和容量核。
- `C4`：机器投影漏检，运输资源加入后出现死锁。
- `C5`：制造岛双向回流、有限缓冲和 blocked-unload。
- `C5_DAG`：删除回流后的配对修复。
- `BIX1-SAT`、`BIX2-PERSIST`：参与理论形成的参数化发现族。

这些案例均不能重新命名为独立确认。

### 8.2 历史 G4/G5 面板

G4 freeze：

- freeze id：`G4-FREEZE-C-20260730T051210Z`
- 实现锁 A：`f9b9a5a5652c7a49053e7ef26d08911bd757f465`
- 最终预注册 B2：`58bbd4ab7da8c2c1d0bcdea4a12f2ae7c020d09a`
- seal C：`e91be4d6d7511c76918093899269de4b78e69fd8`

G5：

- G5-A：`b5e5dc0494b23a54c78c420bbca50a3639de8bff`
- G5-B：`8aa752804b885b79e5371c98e7961087c540f2a8`
- G5-C：`ff281481068a2325cb0bde00e85fd7b753ba854a`
- 九例均只有一次 primary 和一次 repro。
- 9/9 raw stdout、canonical JSON（适用时）、stderr 和元数据一致。
- 七例完成；grid 和 medium 均可复现地 nonzero exit。
- 原锁定 scorer：`4 SUPPORTED / 3 FALSIFIED / 2 INCONCLUSIVE`。
- 非覆盖式 rule audit：`6 SUPPORTED / 1 FALSIFIED / 2 INCONCLUSIVE`。
- 两个独立 `certificate_minimality=FAIL` 必须继续保留。

关键失败：

- `G4_CRP_S4PR_AGREE` 的 frozen theorem prediction 被证伪。
- `G4_IMS_PARAMETER_GRID` 在 `s5` 暴露未选 closed class。
- `G4_MEDIUM_ISLAND_REBUILD` 在 `s79` 暴露未选 closed class。

因此 `G5 paper gate = FAIL`，不得补跑、换指标或重写 sealed inputs。

### 8.3 G6 历史重放 R1/R2/R3

R1：

- 状态：`FAILED_INCOMPLETE`。
- 只完成 6 个 capture。
- 根因是 Windows schedule-state critical section、固定 `0.25s` lease
  阈值和 sentinel 释放竞态。
- 缺失行保持缺失，不补齐。

R2：

- 状态：`FAILED_MECHANISM_CHECK`。
- 10 个 capture 完成且五对 hash 匹配。
- producer/solver 接受 `1e-10` 数值容差，consumer 却要求严格 `[0,1]`。
- `1.0000000000000002` 被错误判为概率非法。
- R2 不重评分、不覆盖。

R3：

- 研究角色：`historical_replay`。
- 代码 HEAD：
  `7b213d279ca6d57b0a8f8e904f4028b315e9b2b5`
- tree：`9349bf891acc8d68925ba35e72463663fedab5a4`
- 10/10 formal captures 完整。
- 5/5 primary/repro 的 raw/canonical/stderr 匹配。
- 5/5 mechanism checks 为 PASS。
- 32 个文件，共 18,183,026 bytes。
- canonical path-to-hash map：
  `494b17a3224fba0c8e4586c8afa0429a588d437b8500809b7fcc11cbc6957c14`
- 两个 boundary case 的 theorem prediction 为 `SUPPORTED`，但
  `certificate_minimality=FAIL/false` 仍保留。

R3 只关闭已诊断机制的历史回归，不是 held-out confirmation，不改变 G5。

### 8.4 后续工具修复

G5 capture comparator 已改为 fail-closed：

- malformed 或 partial record 返回结构化失败，不抛 `KeyError`；
- raw/canonical/stderr hash 必须都是非空字符串；
- `None/None` 不得判为相等；
- 该修复只面向未来证据工具，不重算 G5 或 R1/R2/R3。

## 9. 必须保留的负证据

以下内容不得删除、覆盖或改写为成功：

1. G5 原 scorer 的 `4/3/2`。
2. G5 rule audit 的 `6/1/2` 必须始终和 erratum 一起报告。
3. `G4_CRP_S4PR_AGREE = FALSIFIED`。
4. grid/medium 的 G5 `INCONCLUSIVE` 和原 nonzero-exit captures。
5. 两项 `certificate_minimality=FAIL`。
6. R1 `FAILED_INCOMPLETE` 及其缺失行。
7. R2 `FAILED_MECHANISM_CHECK`。
8. R3 的 `historical_replay_only` 和 `no_confirmation_use`。
9. G5 paper gate `FAIL`。
10. 所有 counterexample、refusal 和不适用范围。

权威证据：

- `docs/verification/G5_CONFIRMATION_REPORT.md`
- `docs/verification/G5_REPRODUCIBILITY_AUDIT.md`
- `docs/verification/G5_CLAIM_EVIDENCE_TABLE.md`
- `evidence/g5/G5_SCORING_ERRATUM.json`
- `docs/verification/G6_HARD_PROBLEM_ROOT_CAUSE_AND_R3_REPAIR.md`
- `evidence/g6/G6_HISTORICAL_REPLAY_FAILURE_LEDGER.json`
- `evidence/g6/G6_HISTORICAL_REPLAY_R3_REPORT.json`
- `evidence/g6/G6_HISTORICAL_REPLAY_R3_RAW_HASH_MANIFEST.json`

## 10. 当前允许与禁止的论文表述

### 10.1 允许

- 报告受限 P1-P6 理论链及其明确假设。
- 报告 G5 9/9 primary/repro 可复现。
- 同时报告 G5 原 `4/3/2` 和附 erratum 的 theorem audit `6/1/2`。
- 报告 `G4_CRP_S4PR_AGREE` 被证伪。
- 报告 grid/medium 因 terminal-class 不完备而 inconclusive。
- 报告 R1、R2 根因及不可变失败状态。
- 报告 R3 机制回归 5/5 通过，同时保留 minimality failures。
- 在 A0-A8 和 request-closed/完整 LTS 审计边界内陈述 local-first-hit
  与 terminal/stopping 结果。

### 10.2 禁止

- “G5 论文门通过”。
- “R3 是独立确认”。
- “G6 修好了并重新判定 G5”。
- “一般 IMS 与 S3PR/Petri 网等价”。
- “存在等待环即可推出多容量死锁”。
- “任意 local core 都是全局 operational deadlock”。
- “`D_local` 是 plant LTS terminal SCC”。
- 用 global covering certificate 替代 local CRP bridge。
- 在 closed class 未穷尽、rate 缺失、LTS 截断或 registry 不完整时报告
  二元 CTMC 数值。
- 把 DES 区间覆盖 exact probability 当成 theorem proof。
- 把当前工程组合包装成一般性首创理论。

## 11. 代码结构与稳定接口

### 11.1 主要模块

| 模块 | 职责 |
| --- | --- |
| `model.py` | `IMSModel`、`IMSState`、资源/请求/持有、证书和值对象 |
| `engine.py` | zero-time closure、仿真、事件执行、exact supervisor |
| `analysis.py` | stable LTS、案例分析、证书/基线汇总 |
| `certificates.py` | global 与 all-minimal local blocking certificates |
| `petri.py` | `IMS-SIP^1` wait-snapshot bridge 和 refusal |
| `ctmc.py` | committor、吸收时间、灵敏度、Doob-\(h\)、数值契约 |
| `stochastic.py` | 独立随机流和 CTMC/DES 估计 |
| `terminal_classes.py` | G6 terminal/stopping partition 和 estimand hash |
| `families.py` | BIX1/BIX2 参数族 |
| `g4_instances.py` | 历史 G4 结构/量化案例构造 |
| `g4_freeze.py` / `g4_protocol.py` | freeze 和执行协议 |
| `g5_capture.py` / `g5_scoring.py` | capture、hash、历史 scorer |
| `historical_replay.py` | R1/R2/R3 历史重放机制 |

### 11.2 稳定对象

- `IMSModel`
- `IMSState`
- `DeadlockCertificate`
- `QuantitativeResult`
- `SupervisorPolicy`
- `VersionedEstimandSpec`
- `TerminalStoppingPartition`

### 11.3 CLI

安装项目后：

```bash
ims-deadlock validate C0
ims-deadlock prove C0
ims-deadlock verify-case C5 --max-states 128
ims-deadlock quantify C0
ims-deadlock simulate C0 --mode ctmc --samples 1000 --seed 12345
```

五个入口输出 `ims-deadlock/cli/v1` JSON。`prove` 是程序观察，不是数学
证明；不满足桥接、速率或 closed-class 条件时必须结构化拒绝。

## 12. 运行时与验证

已验证运行时：

```text
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe
Python 3.13.9
```

该环境的 editable install 可能指向旧工作树。使用它验证任何新 worktree
时必须：

```text
PYTHONPATH=<精确锁定工作树>\src
PYTHONDONTWRITEBYTECODE=1
pytest: -p no:cacheprovider
ruff: --no-cache
mypy: --no-incremental
```

标准验证：

```bash
python -m pytest -p no:cacheprovider -q
python -m ruff check --no-cache src tests
python -m ruff format --check --no-cache src tests
python -m mypy --no-incremental --strict src
python -m mypy --no-incremental --strict --explicit-package-bases src tests
git diff --check
```

历史 Dell 主工作区验证：

- full pytest：`341 passed in 50.48s`
- Ruff check：PASS
- Ruff format：39 files
- strict mypy `src`：21 source files PASS
- strict mypy `src tests`：39 source files PASS
- tracked evidence JSON：10 files parsed
- independent focused review：0 issues

Historical/pre-repair G6-B v2 Task-5 候选在权威 Windows 工作树的提交前内容验证：

- four-file pytest：`1478 passed, 2 skipped in 2672.43s (0:44:32)`
- schema pytest：`160 passed in 0.36s`
- Section 17.3 manifest/collection audit：`1 passed, 1108 deselected`
- Ruff touched-file check：PASS
- Ruff touched-file format check：PASS
- mypy touched source/tests：3 source files PASS
- `git diff --check`：PASS
- 提交后 subject：`9ef6fcec9e410b2ab7afc4144df8b948a238d95f`，push 后
  upstream `0/0`、clean

该证据验证 schema/guard 行为，不是 future runtime capability 或 G6-B science。

当前 G6-B v2 final Section 18 evidence subject 在权威 Windows 工作树的验证：

- authority worktree：
  `D:\worktree\IMS_deadlock-g6b-spec-final-review`
- branch：
  `codex/g6b-case-target-certification-final-review`
- subject commit：
  `948ff5746adcb66b68fb9c47e519f070dd2c96ba`
- push/dirty state：已推送，`HEAD...upstream = 0/0`，clean
- schema suite：`356 passed`
- Git-scope audit：`19 passed`
- four-file suite：`1695 passed, 2 skipped`
- full repository suite：`2122 passed, 2 skipped`
- retired focus：`1 passed`
- manifest audit：`1 passed`
- Ruff full check：PASS
- Ruff format check：`47 files already formatted`
- strict mypy `src`：25 source files PASS
- strict mypy `src tests`：47 source/test files PASS
- tracked JSON parse/duplicate checks：`53 files parsed`
- sets check：`5/12`
- authorization fields：21 checked，true count `0`
- future roots/modules：`0`
- approved spec digest：
  `b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6` matched
- frozen matrix raw SHA-256：
  `487d81aa79a7bca681db81f19a4d6bd315668c43b1c4538c47f01f099d8e205f` matched
- canonical vector parity：19 vectors matched on remote Python 3.13.9,
  local Python 3.12.3, and local Python 3.13.5
- diff checks：green
- independent reviews：ontology `APPROVE` with no P0-P2 findings；
  scientific/boundary `APPROVE` with no P0-P2 findings；code/capability
  `APPROVE` with zero P0-P3 findings；the sole P3 evidence-publication sync
  noted during review is closed by this documentation update

该证据完成 Section 18 schema/governance review publication，不创建 case，不运行
retired-authority normalization、Barrier-A preflight、CTMC 或 DES，不检查输出根，
也不形成 G6-B scientific verdict。

文档-only 后继提交至少要重新运行 Markdown 固定检查、链接/路径检查、
`git diff --check` 和目标锁；若 README 或源代码未变，可引用上一完整
测试结果，但必须明确它对应的代码 tree。若任何代码、schema、冻结协议或
证据对象改变，则先跑 targeted tests，再跑全部验证。

最小文档检查形状：

```bash
awk '/^```/{n++} END{print n, n%2}' PROJECT_HANDOFF.md
rg -n '[[:blank:]]+$' PROJECT_HANDOFF.md README.md
git diff --check
git status --short
git log -1 --format=%H -- PROJECT_HANDOFF.md
```

若交接文档列出新的仓库相对路径，还要逐项执行 `test -e <path>`。不要在
本地材料化快照上用 `g4_freeze check` 作为远程当前性证明；第 2.1 节已经
记录该快照的 file-byte mismatch。

## 13. 下一硬门：G6-B

下一进程不要继续重放 G4/G5，也不要先写成投稿稿件。case-construction plan
及其三路审查现已发布；当前 first unchecked next step 只能是用户明确批准
plan SHA `c20393328f8f98e7b35a6507fd6e993b2f17e068d977c3dc6253b05e9a75de5f`
和 review SHA
`297a69382347e16e894af63e70f8fa95807407048b2e89c45701410a4e9289e1`，不是
normalization、preflight、CTMC、DES 或科学执行。
Final Section 18 evidence subject 是
`948ff5746adcb66b68fb9c47e519f070dd2c96ba`。Historical/pre-repair Task-5
schema-code subject 是 `9ef6fcec9e410b2ab7afc4144df8b948a238d95f`，仅作为已保留
的 schema-code baseline 和 pre-repair count evidence；不得把它当作当前继续
入口。top-level bundle 保持 exact-five，nested row-family bundle 为 exact-twelve，
validator 为
`src/ims_deadlock/g6b_row_family_protocol.py` 和
`src/ims_deadlock/g6b_schema_contracts.py`。

当前 `scientific_execution_authorized=false`、
`case_construction_authorized=false`、
`retired_authority_fingerprint_normalization_authorized=false`、
`target_certification_preflight_authorized=false`、
`quantitative_execution_authorized=false`、
`adversarial_review_status=PENDING`；G6-B 保持 `OPEN/PENDING`，G6-C/D/E
仍未开始。四个 later instance roots 和四个 future capability modules 均 absent。
本 tranche 没有创建 case、运行 normalization/overlap/preflight/CTMC/DES 或检查
科学输出。independent schema review 已在 Section 18 final evidence subject 上
通过；后继 case-construction plan 的三路 independent review 也已对同一 exact
plan hash 通过，但状态仍为 `USER_APPROVAL_PENDING`，不自动授权 case
construction、normalization、preflight 或 science。

### 13.1 G6-B 必须冻结前定义的内容

1. 客观 state-class partition：
   `D_global`、`D_local`、`F`、`R_livelock`、`R_terminal`。
2. exact bad/success target 和对应 `estimand_id`。
3. DES stopping rule，并证明与 exact 使用同一目标语义。
4. terminal/stopping hash、state-space hash、rate-manifest hash。
5. theorem prediction、ancillary metric、execution status 的正交 schema。
6. all-minimal local-kernel family 和多核 CRP matching quantifier。
7. negative controls 和 refusal expectations。
8. 独立随机流 manifest。
9. 失败账本、案例变更账本和截断处理。
10. 运行时间、内存、并行度、输出目录和停止条件。

### 13.2 独立性要求

退役证据范围包括 retired G4、retired G5 和 G6-R historical replay。G6-B
未来经单独授权构造的 G6-B discovery subjects 相对这些退役证据，必须按各
subject 所有权在以下八个 fingerprint dimensions 上完成适用的 overlap 审计；
当前 schema-only tranche 没有 subjects，也没有 actual overlap result：

- `case_content_sha256`
- `state_snapshot_sha256`
- `route_signature_sha256`
- `parameter_tuple_sha256`
- `random_stream_manifest_sha256`
- `output_root_reservation_sha256`
- `sealed_prediction_sha256`
- `metric_schema_sha256`

未来 G6-C/D/E confirmation rows 相对 retired G4/G5/G6-R 和 G6-B discovery
rows 必须在七个 canonical identity/provenance dimensions 上 zero overlap：

- `case_content_sha256`
- `state_snapshot_sha256`
- `route_signature_sha256`
- `parameter_tuple_sha256`
- `random_stream_manifest_sha256`
- `output_root`
- `sealed_prediction_sha256`

`metric_schema_sha256` 不属于 future confirmation 的无条件 strict-distinct 维度；
metric schema reuse 只允许在预注册中明确用于 same-target comparability，且
不得由 discovery outcome 派生。该规则不声明未来 discovery subjects 在所有
八个维度上彼此无条件 distinct；case、method observation 和 companion group
必须按批准 schema 的 subject map、policy map 与 lineage 逐项审计。

“改名”“参数平移”或从退役案例复制后轻微修改不构成独立。必须生成
机器可审计的 overlap report，按上述适用范围逐项证明不重合。

### 13.3 建议的发现维度

这些是设计轴，不是预注册结论：

- 只存在 `D_global` 的正控；
- 存在 request-closed `D_local` 且仍有核外事件的 local-first-hit 正控；
- local-candidate 可通过旁路最终完成的负控；
- 可达 `R_livelock`；
- 可达单点 `R_terminal`；
- CRP 有一个、多个和零个 matching local kernels；
- OR-of-AND alternative 有一个真正可行分支的 certificate 负控；
- multi-capacity residual 改变简单环判定但不改变 capacity witness 的案例；
- AGV/预约语义拒绝或明确纳入的边界案例；
- exact/DES 同 stopping target 的小 CTMC；
- 中型制造岛重建，但路线签名、参数和随机流必须与 G4/G5 独立。

发现集允许修正定义和算法，但每次改变必须进入账本。任何失败都不得删除。

### 13.4 G6-B 通过条件

- 完整、非截断 stable LTS 或明确 refusal。
- all-minimal local kernels 完整且顺序不影响真值。
- local-core completion soundness 审计通过，或给出最短 bypass 反例。
- 所有 reachable closed classes 被分类。
- exact 与 DES stopping semantics 同源并可哈希。
- theorem/metric/execution 三层 schema 正交。
- 独立性 overlap report 为零重用。
- negative controls 按预期拒绝或分类。
- 发现网格无未解释 mismatch；truncated/invalid 不计作支持。
- targeted/full tests、Ruff、strict mypy 和 diff check 通过。
- G6-B 报告经过独立科学边界审查。

未满足任一条时，G6-B 继续为开放，不能创建 G6-C confirmation freeze。

## 14. G6-B 之后的严格顺序

### G6-C：独立 confirmation preregistration

只有 G6-B 通过后：

- 设计不参与理论修正的新 confirmation cases；
- 预注册预测、estimands、metrics、baselines、streams、runtime 和失败规则；
- 不运行、不查看、不汇总 held-out 结果；
- 对每个 artifact 和 case 计算 hash；
- 独立审查 discovery/confirmation 不重叠。

### G6-D：seal/freeze

- 固定实现、case、prediction、metric、runtime、stream 和 exclusion hashes；
- freeze checker 必须返回无错误；
- 证明 `confirmation_results_inspected=false`；
- seal 后禁止更换指标、删行、调参或选择性执行。

### G6-E：一次性执行

- 每例一次 primary 和一次 repro；
- repro 只能在全部 primary 完成后开始；
- 禁止 retry、第三次运行和同案例重叠；
- 合理并行只能按预注册 wave 和资源预算执行；
- 保存 raw stdout、canonical JSON、stderr、record、schedule state 和哈希；
- exact 与 DES 必须针对同一 frozen target；
- 负例、拒绝、nonzero exit 和不利结果全部报告。

### 后续论文门

G6-E 之后重新建立 paper gate：

- 主定理与确认结果逐项回链；
- exact 与独立 DES 一致性；
- false positive/negative；
- 证书最小性；
- 吞吐、工期、WIP 和风险代价（仅在适用时）；
- 适用范围和反例；
- 与 CRP/SBA、L30、B05、Banker、cycle/knot、siphon control 等基线比较；
- 独立审稿式攻击和 claim-evidence 审计。

只有新 paper gate 通过后，才把材料整合成投稿版论文。

## 15. 论文文件状态

当前仓库没有统一 `.tex`、`.docx` 或投稿 PDF。现有内容是论文级素材包：

- 研究定位；
- 定义和符号；
- 核心定理与证明草稿；
- 证明义务和反例；
- 文献矩阵与迁移卡；
- 发现/确认案例协议；
- G5/G6 证据和失败边界。

G6-B 推进期间可以建立诚实的 working manuscript skeleton，但必须：

- 把 G5 写成失败证据；
- 把 R3 写成 historical mechanism regression；
- 把 G6-C/D/E 写成 future work，不得预填结果；
- 不把候选定理写成已证；
- 不删除负例；
- 不标记为 submission-ready。

建议最终论文结构：

1. Introduction and contribution boundary
2. Related work and non-transferable assumptions
3. IMS-RAS semantics
4. Closed blocking cores and restricted Petri bridge
5. Structural threshold families
6. Local-first-hit and terminal/stopping theory
7. Exact CTMC and DES same-target methodology
8. Preregistered discovery and confirmation cases
9. Results, negative evidence and control cost
10. Limitations and counterexamples
11. Conclusion
12. Appendices for proofs, hashes and reproducibility

## 16. 下一进程的第一个可执行批次

在当前会话已经明确获得远程写入授权后，下一进程应从以下批次开始；低风险、
可逆的分支—编辑—测试步骤不需要反复询问。若会话仅获本地或只读权限，则
必须停在相应边界，不得把本文件中的命令当作 standing authorization：

1. 从本地操作契约读取 SSH/远程路径并重锁
   `D:\worktree\IMS_deadlock-g6b-spec-final-review`、branch、HEAD、upstream、
   clean/expected-dirty scope 和批准规格 digest。
2. 以 `git log -1 --format=%H -- PROJECT_HANDOFF.md` 定位到的当前文档
   continuation commit 作为文档 continuation 基线；以 final Section 18 evidence subject
   `948ff5746adcb66b68fb9c47e519f070dd2c96ba` 作为 schema/governance review
   evidence subject；以 historical/pre-repair Task-5 subject
   `9ef6fcec9e410b2ab7afc4144df8b948a238d95f` 只作为历史 diff/count evidence。
   拒绝 G4/G5/G6-R evidence、case-instance roots、scientific artifact roots、
   批准规格或 task-declared files 之外的变更。
3. 确认 `docs/verification/G6_B_CASE_TARGET_SCHEMA_V2_REVIEW.md` Section 18
   已完成 independent schema、ontology/boundary 和 code/capability review
   publication：每行必须绑定 exact subject、命令/审稿人和 count/finding；不得把
   review verdict 写回 JSON bundle state。
4. 核验批准规格内的 `AWAITING USER REVIEW` 和历史 implementation plan 未勾选
   checkbox 均按第 1.2 节解释，不得修改批准规格 bytes，不得重跑已关闭的
   schema Tasks 1-7。
5. 定位已经发布的 G6-B case-construction plan 与 review artifact，重新计算并
   核对 plan SHA `c2039332...`、review SHA `297a6938...`，以及三路 review 的
   `APPROVE`/0 Critical/High/Medium；不得修改 exact plan bytes 后沿用旧审查。
6. 只有用户对这两个 exact SHA-256 明确批准后，才可按 plan 新建独立
   implementation worktree 并从 Task 0/Task 1 开始；普通“继续推进”或 PR merge
   不等同于 exact-bytes approval。

后续依赖顺序不得并行越门：

1. approved case-construction plan；
2. materialize sealed case inputs/predictions/controls/metric schemas，仍不执行科学；
3. 单独授权并完成 retired-authority data-only normalization；
4. sealing 后做 input-level overlap audit；
5. overlap PASS 后另行授权 Barrier A target-certification preflight；
6. review target certificate/refusal evidence，并建立 exact/DES same-target locks；
7. 另行授权 Barrier B 后才可运行 CTMC、DES、metric observation 和定量输出；
8. G6-B 全条件通过后才进入 G6-C confirmation preregistration；
9. G6-D freeze 与 G6-E 一次性执行；
10. 重建 paper gate，完成主稿、claim-evidence audit、复现包和投稿元数据。

Git 管理不改变科学顺序：PR #4 以 `main` 为 base；计划分支 PR #5 堆叠在
PR #4 的 final-review 分支上；包含 PR 状态文档后继后，计划 diff 限定为
2 commits / 5 paths。
不得在未核对 PR diff、review subject、负证据保留情况和 merge authority 时
merge；即使 merge，也不替代 plan exact-bytes approval。

## 17. 科学与工程停止条件

立即停止升级主张或 held-out 执行，如果：

- 一般结论只能靠模糊定义维持；
- local kernel 枚举不完整或依赖 first-hit order；
- CRP bridge 仍偷用 global certificate；
- 有 reachable closed class 未分类；
- exact/DES stopping target 不一致；
- G4/G5/G6-R 与新案例独立性无法证明；
- 负控被删除或改名绕过；
- 程序枚举被用作数学证明替代品；
- 结果只剩已有 Petri、RAS、CTMC 和仿真工具的工程拼装；
- 代码、证据或 runtime lock 无法复现；
- frozen 后需要调参、换指标或第三次运行才能得到期望结论。

若强命题被反例推翻，应收缩到可证明子类并把反例作为边界贡献，不得降低
证据标准。

## 18. 关键文件索引

### 状态和计划

- `README.md`
- `docs/ROADMAP.md`
- `docs/superpowers/plans/2026-07-30-g6-local-core-terminal-class-recovery.md`
- `docs/superpowers/plans/2026-07-30-g6b-protocol-foundation.md`
- `docs/theory/G6_LOCAL_FIRST_HIT_AND_STOPPING_THEOREMS.md`
- `docs/verification/G6_B_PROTOCOL_FOUNDATION_REVIEW.md`
- `docs/superpowers/specs/2026-08-01-g6b-case-target-certification-design.md`
- `docs/superpowers/plans/2026-08-01-g6b-schema-only-governance-v2-implementation.md`
- `docs/verification/G6_B_CASE_TARGET_SCHEMA_V2_REVIEW.md`

### 理论

- `docs/theory/CORE_THEOREMS_AND_PROOFS.md`
- `docs/theory/PROOF_OBLIGATIONS.md`
- `docs/theory/THEOREM_LADDER.md`
- `docs/theory/COUNTEREXAMPLE_LEDGER.md`
- `docs/theory/G6_LOCAL_FIRST_HIT_AND_STOPPING_THEOREMS.md`

### 文献

- `docs/literature/LITERATURE_MATRIX.md`
- `docs/literature/MIGRATION_CARDS.md`
- `docs/literature/SOURCE_VERIFICATION.md`
- `docs/literature/FULLTEXT_AUDIT_L30_L35_B05.md`
- `docs/literature/FAILURE_LEDGER.md`

### 案例

- `docs/cases/CASE_CATALOG.md`
- `docs/cases/CASE_CHANGE_LEDGER.md`
- `docs/cases/G4_CASE_PREREGISTRATION.md`
- `docs/cases/G4_EXECUTION_PROTOCOL.md`
- `docs/cases/G6_B_DISCOVERY_PROTOCOL.md`
- `docs/cases/G6_HISTORICAL_REPLAY_R3_PREREGISTRATION.md`
- `cases/discovery/g6b/`
- `cases/confirmation/g4/`

旧 G4 preregistration/catalog 文档只作为历史输入与协议来源。当前状态判断
优先使用 `docs/ROADMAP.md`、`docs/cases/G4_FREEZE_LEDGER.md` 和 G5/G6
verification reports，不得用早期 B-stage 语气覆盖后来的 freeze、执行和
退役事实。

### 结果和证据

- `docs/verification/G5_CONFIRMATION_REPORT.md`
- `docs/verification/G5_REPRODUCIBILITY_AUDIT.md`
- `docs/verification/G5_CLAIM_EVIDENCE_TABLE.md`
- `docs/verification/G6_HARD_PROBLEM_ROOT_CAUSE_AND_R3_REPAIR.md`
- `docs/verification/G6_B_PROTOCOL_FOUNDATION_REVIEW.md`
- `evidence/g5/`
- `evidence/g6/`
- `src/ims_deadlock/g6b_protocol.py`
- `tests/test_g6b_protocol.py`

### 远程操作

- 本地协调目录中的 `AGENTS.md`
- 本地协调目录中的 `REMOTE_PROJECT_OPERATIONS.md`
- 仓库内的 `AGENTS.md`

## 19. 交接完成判据

下一进程只有在以下信息都能从仓库和实时环境独立恢复时，才算成功接管：

- 当前远程 path、branch、HEAD、dirty state 和 upstream；
- 当前 Gate 表；
- G5 原始与勘误结果的区别；
- R1/R2/R3 的不可变状态；
- R3 historical-only 边界；
- G6-B 的精确通过条件；
- 当前 runtime 和安全验证方式；
- 禁止重跑或改写的 evidence objects；
- 下一批可执行任务和停止条件。

若其中任一项只能从聊天记录获得，应先把它补入本文件或相应权威跟踪文件，
再继续科学执行。

## 2026-07-31 G6-B Ontology And Absorption-Domain Correction

Implementation status: Task 7 documentation alignment is applied on top of the
v2 foundation estimand, v3 terminal stopping partition, certificate v1, and
generator provenance v3 work already present on this branch. The correction does
not create a G6-B case, does not run LTS/CTMC/DES science, and does not upgrade
G6-B to PASS.

Current boundary: `selected_stopping_targets` are `D_global`, `D_local`, and
`F`; `unselected_plant_terminal_classes` are `R_livelock` and `R_terminal`;
`P_policy` is separate; `S_reach` and `S_T` are derived and nonselectable.
`S_reach` is support graph reachability only. `S_T` is certified by the finite
positive-rate stopped-CTMC closed-SCC/reverse-basin certificate, where SCC
closedness is checked against the full stopped graph including selected `A_stop`, with
`absorption_domain_hash` binding the domain identity. Missing rates remain
distinct from explicit empty rates. G6-B remains OPEN/PENDING,
`case_creation_authorized=false`, and `scientific_execution_authorized=false`;
G6-C, G6-D, and G6-E are not started.

Approved design: `docs/superpowers/specs/2026-07-31-g6b-ontology-absorption-domain-correction-design.md`. Historical review superseded in part, not deleted. Negative and boundary evidence are retained.

## 2026-07-31 G6-B Ontology And Absorption-Domain Review Record

Final review record:
`docs/verification/G6_B_ONTOLOGY_ABSORPTION_DOMAIN_CORRECTION_REVIEW.md`.

Verification HEAD before the documentation commit:
`94fbf6517eb0abaf3c09a4c7238129547e76b8f5` on
`codex/g6b-discovery-estimand-lock`. The reviewed worktree was clean at
`D:\worktree\IMS_deadlock-g6b-discovery`, with upstream relation
`0 behind / 20 ahead`. The documentation commit containing the review record is
self-identifying through Git history and must be re-locked after push.

Evidence summary: focused verification `1157 passed in 132.13s`; full pytest
`1410 passed in 167.44s`; Ruff check passed; Ruff format reported 43 files
already formatted; strict mypy passed on 23 source files and on 43 source/test
files; diff checks passed. Validators reported exact `5/8`, valid, no errors,
science false, case false, and `PENDING`. Changed-path guards reported 24
changed paths, 1 added plan, outside allowed `[]`, immutable diff `[]`, and
forbidden additions `[]`.

Independent verdicts: theory review `PASS` with 45 targeted checks; code review
`PASS` with no actionable blockers and focused `1157 passed in 116.08s`;
verifier `PASS` with focused `1157 passed in 125.10s`, full
`1410 passed in 172.45s`, and reproduced static/guard checks; Task 7 final
specification, theory, quality, and citation-traceability reviews all `PASS`.

Boundary: this is governance/theory/code correction evidence only. It creates
no G6-B case, runs no enumeration, solves no CTMC, runs no DES, inspects no
scientific output root, replays no R3 evidence, and changes no authorization.
G6-B remains `OPEN/PENDING`; `case_creation_authorized=false` and
`scientific_execution_authorized=false` remain in force; G6-C/D/E are not
started; immutable G4/G5/G6 evidence is unchanged.

The next first action after normal push is to re-lock the pushed branch and
confirm HEAD/upstream/status. The case-construction plan and three independent
reviews are published, but the next transition is still exact-bytes user
approval of plan SHA `c2039332...` and review SHA `297a6938...`, not execution
and not a partial-domain production solve.
