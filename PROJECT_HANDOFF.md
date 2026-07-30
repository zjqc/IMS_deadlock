# IMS Deadlock 当前项目交接

更新时间：2026-07-30（Asia/Shanghai）

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

G6-B protocol foundation 和 data-only validator 已在 feature branch 上完成，
但它只建立 execution-disabled/PENDING 的协议基础：没有创建 discovery case，
没有运行 enumeration、CTMC 或 DES，没有检查任何新科学输出，不能把 G6-B
改为 PASS。

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
- 交接编写前实时锁定：
  `main@235b69a189a869578d9760fcc5585fbfe21a7808`
- 交接编写前 tree：
  `9ffa5974ced053e3ffd9943f34e163c4606eddf2`
- 交接编写前状态：clean，`HEAD...origin/main = 0/0`
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

若本文件已发布到 `main`，包含它的提交会是上述 source baseline 的后继。
下一进程不得把交接前 SHA 当作当前 SHA，必须重新运行锁定命令。实际包含
本文件的提交可用以下命令定位：

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
# <SSH_ALIAS> 和 <REMOTE_PROJECT_PATH> 必须取自本地操作契约。
ssh -o BatchMode=yes -o ConnectTimeout=10 <SSH_ALIAS> \
  "echo SSH_OK && hostname && whoami"
ssh -o BatchMode=yes -o ConnectTimeout=10 <SSH_ALIAS> \
  "cd /d <REMOTE_PROJECT_PATH> && git rev-parse --show-toplevel && git branch --show-current && git rev-parse HEAD && git status --short && git remote get-url origin && git rev-list --left-right --count HEAD...origin/main && git worktree list --porcelain"
```

若本地契约要求单独的 Tailscale 连通性检查，按契约中的当前目标执行；不要
把私有网络地址复制进仓库文档。

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
| G6 恢复门 | IN PROGRESS | G6-A 和 G6-R 通过；G6-B protocol foundation + validator 在 feature branch 完成且 execution disabled/PENDING；locked worktree `D:\worktree\IMS_deadlock-g6b-discovery` at HEAD `4c24f39` 已通过 full pytest 393、Ruff、format check、strict mypy、five JSON parse checks、52 protocol tests 和 `git diff --check` | G6-B 仍 OPEN；independent foundation review、actual overlap report、runtime lock 和 discovery outcomes 仍开放；G6-C/D/E 未通过 |

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

交接前最后一次 Dell 主工作区验证：

- full pytest：`341 passed in 50.48s`
- Ruff check：PASS
- Ruff format：39 files
- strict mypy `src`：21 source files PASS
- strict mypy `src tests`：39 source files PASS
- tracked evidence JSON：10 files parsed
- independent focused review：0 issues

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

下一进程不要继续重放 G4/G5，也不要先写成投稿稿件。第一未完成工作是
independent foundation review；通过后才可另写 row-family
discovery-model/execution plan 并做 adversarial review。该审查和后续计划
审查完成前，不得把下一步描述为科学案例构造或执行。

G6-B protocol foundation 已在 feature branch
`codex/g6b-discovery-estimand-lock` 的 pre-integration commits
`73cbbbc52be59fa6a14fcd2a4cf647ea5dc8f811` 和
`4c24f39dfd1b47fee874a2315ee77759b51311cb` 中完成协议文档、五个 JSON
文件和 strict data-only validator。其状态仍是
`scientific_execution_authorized=false`、`adversarial_review_status=PENDING`；
G6-B 仍为 `OPEN`，G6-C/D/E 仍未开始。该批次没有创建 discovery case，
没有运行 enumeration、CTMC 或 DES，没有改变 G4/G5/R1/R2/R3 历史证据。
Task2 targeted+adjacent 验证为 52 validator tests + 59 adjacent = 111
passed；随后 locked worktree `D:\worktree\IMS_deadlock-g6b-discovery` at HEAD
`4c24f39` 在 state-doc commit 前通过 full pytest `393 passed in 47.22s`、
Ruff check、Ruff format 41 files already formatted、strict mypy `src`
22 source files、strict mypy `src+tests` 41 source files、five protocol JSON
parse checks、targeted protocol tests `52 passed in 2.48s` 和
`git diff --check`。这些验证不改变 `OPEN/PENDING` 状态，也不表示执行了
science、创建了 cases 或检查了 outcomes。

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
discovery rows 相对这些退役证据必须在以下八个 canonical dimensions 上
全部 zero overlap：

- `case_content_sha256`
- `state_snapshot_sha256`
- `route_signature_sha256`
- `parameter_tuple_sha256`
- `random_stream_manifest_sha256`
- `output_root`
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

`metric_schema_sha256` 不属于 future confirmation 的强制 zero-overlap 维度；
metric schema reuse 只允许在预注册中明确用于 same-target comparability，且
不得由 discovery outcome 派生。该规则不声明 discovery rows 内部必须彼此在
八个维度上无条件 zero overlap；discovery-internal family/row 独立性必须由
后续 row-family discovery-model/execution plan 单独定义并接受审查。

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

1. 原始步骤 1 已在 feature branch 中完成：从本地操作契约读取并实时锁定
   `<REMOTE_PROJECT_PATH>`，目标 worktree 为
   `D:\worktree\IMS_deadlock-g6b-discovery`。
2. 原始步骤 2 已在 feature branch 中完成：专用分支为
   `codex/g6b-discovery-estimand-lock`，base 为
   `main@9c707ce3d990541847aee745bec211bb55c74f6b`。
3. 原始步骤 3 已在 feature branch 中完成：阅读本文件、`docs/ROADMAP.md`、
   `docs/theory/G6_LOCAL_FIRST_HIT_AND_STOPPING_THEOREMS.md`、
   `docs/verification/G6_HARD_PROBLEM_ROOT_CAUSE_AND_R3_REPAIR.md` 和
   G6 recovery plan。
4. 原始步骤 4 已在 feature branch 中完成：写入
   `docs/cases/G6_B_DISCOVERY_PROTOCOL.md`、独立性 schema、estimand
   schema、negative-control table、failure ledger 和 validator。
5. 下一未完成工作：做 independent foundation review；通过前不得把 G6-B
   标为 PASS。
6. 通过 full verification 和 independent foundation review 后，另写
   row-family discovery-model/execution plan，并对该计划做 adversarial review。
7. 只有独立审查通过且新计划明确授权后，才可进入 discovery science；actual
   overlap report、runtime lock 和 discovery outcomes 目前仍开放。
8. 达到 G6-B 通过条件后，独立复核并冻结结论；否则保留失败并继续修正。

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
