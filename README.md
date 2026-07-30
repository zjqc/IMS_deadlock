# IMS Deadlock

IMS Deadlock 是面向 IMS-RAS 的结构-概率-控制理论闭环项目。目标是在离散事件系统、资源分配系统、随机扰动和控制策略之间建立可证明的概念边界、判据和验证路径，而不是先堆叠大规模仿真结果。

当前已经形成一条严格受限但闭合的主链：

`IMS-RAS^CW 稳定语义`
`-> 有限 LTS/reachability net`
`-> capacity-mediated closed blocking core`
`-> IMS-SIP^1 wait-snapshot 精确诊断双向桥或机器可读拒绝`
`-> 受限结构无死锁条件、BIX1-SAT 阈值与 BIX2-PERSIST 精确 ring/DAG 边界`
`-> competing-absorption CTMC`
`-> exact finite nonblocking supervisor`.

Gate 状态是：G0 通过，G1 scope-bounded 通过，G2 受限理论主链通过，
G3 严格小有限模型算法门通过，G4 历史确认集已冻结并在 G5 原样执行，
G5 论文门失败且证据已关闭；G6-A 的局部核—终端类代码/理论恢复和
G6-R 历史重放机制门已经通过，独立 G6 discovery/confirmation
设计、封存和执行仍是下一硬门。
完整状态和开放义务见 `docs/ROADMAP.md`。

## 目录

- `docs/literature/`：文献笔记、权威来源、DOI、引用状态和证据边界。
- `docs/theory/`：IMS-RAS 定义、结构不变量、概率模型、控制命题、证明草稿和反例。
- `docs/cases/`：案例规格、发现集与冻结确认集的说明、案例证据审计记录。
- `docs/verification/`：机器审计范围、命令、结果和不能外推的边界。
- `src/ims_deadlock/`：有限语义、证书、结构基线、CTMC、随机估计、案例和 CLI。
- `tests/`：语义、反例、证书、阈值、监督器、CTMC 和 CLI 审计测试。
- `cases/`：可跟踪的 JSON/YAML 案例规格；不得混入下载论文、原始大文件或生成输出。

## 稳定对象

- `IMSModel` / `IMSState`：资源、容量、工件状态、请求替代、持有与闭包状态。
- `DeadlockCertificate`：核、证据边、逐替代容量缺口、最短前缀和 Petri 桥边界。
- `QuantitativeResult`：committor、平均吸收时间、残差和来源状态。
- `SupervisorPolicy`：安全域、不可控闭合、禁用状态-事件和初始可行性。

## CLI

安装开发环境后运行：

```bash
python -m pip install -e ".[dev]"
ims-deadlock validate C0
ims-deadlock prove C0
ims-deadlock verify-case C5 --max-states 128
ims-deadlock quantify C0
ims-deadlock simulate C0 --mode ctmc --samples 1000 --seed 12345
```

五个入口输出 `ims-deadlock/cli/v1` JSON。`prove` 明确标为程序观察，
不冒充数学证明；`verify-case` 对满足 `IMS-SIP^1` 的证书返回受限
wait-snapshot siphon，对不满足条件的案例返回精确拒绝原因。没有速率、
导数或适用桥接条件时返回结构化 `unavailable`，不补造数据。

## 验证

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider -q
PYTHONDONTWRITEBYTECODE=1 python -m ruff check --no-cache src tests
PYTHONDONTWRITEBYTECODE=1 python -m ruff format --check src tests
PYTHONDONTWRITEBYTECODE=1 python -m mypy --no-incremental src tests
```

## G5 确认证据

G5 对九个冻结案例各执行一次 primary 和一次 repro，9/9 运行记录和 hash
链可复核。七例完成，grid/medium 因 reachable non-`D/F` state 不能到达
声明吸收类而被构造器确定性拒绝。

锁定 scorer 原样保留 `4 SUPPORTED / 3 FALSIFIED / 2 INCONCLUSIVE`。
透明勘误把 theorem prediction 与 certificate minimality 分离后为
`6 SUPPORTED / 1 FALSIFIED / 2 INCONCLUSIVE`，并独立保留两项
minimality failure。该勘误不改变 raw execution，也不使 G5 通过。

- `docs/verification/G5_CONFIRMATION_REPORT.md`
- `docs/verification/G5_REPRODUCIBILITY_AUDIT.md`
- `docs/verification/G5_CLAIM_EVIDENCE_TABLE.md`
- `evidence/g5/G5_SCORING_ERRATUM.json`

## G6 历史重放机制修复

G6 将 theorem prediction、ancillary metric 和 execution status 分层，
并实现 all-minimal local kernels、local CRP bridge 以及
`D_global,D_local,F,R_livelock,R_terminal` terminal/stopping
partition。R1 的 Windows 调度失败和 R2 的概率数值契约失败均作为不可变
负证据保留，没有补跑、重评分或覆盖。

预注册 R3 在新代码树、执行锁和输出根下对五个退役 G4 行各执行一次
primary 和一次 repro。五对 raw/canonical/stderr 完全匹配，五个 mechanism
check 均通过；两个 boundary case 的 theorem 为 `SUPPORTED`，同时两项
`certificate_minimality=FAIL/false` 仍独立保留。

R3 只关闭 historical replay 机制回归，不是 held-out confirmation。
下一硬门是建立不复用 G4/G5 模型、参数、状态或随机流的 G6 discovery
set，锁定新 estimand 和负对照，再进入 G6-C/D/E。

- `docs/verification/G6_HARD_PROBLEM_ROOT_CAUSE_AND_R3_REPAIR.md`
- `evidence/g6/G6_HISTORICAL_REPLAY_FAILURE_LEDGER.json`
- `evidence/g6/G6_HISTORICAL_REPLAY_R3_REPORT.json`
- `evidence/g6/G6_HISTORICAL_REPLAY_R3_RAW_HASH_MANIFEST.json`

## 科学边界

- 程序验证只能支持理论判断，不能替代定义、引理和证明。
- 案例发现集用于探索，冻结确认集用于复核；二者必须分离。
- 只有 `FULLTEXT-THEOREM` 且带精确定位的文献可支撑定理迁移。
- `C0/C1` 的内建 CTMC 是 `fixture_unverified`，不是从结构案例速率推导的确认结果。
- P2c 只关闭 state-induced `IMS-SIP^1` diagnostic net，不是一般
  structured plant/S3PR 等价；P3e 只关闭显式单位需求、单当前持有、
  三资源 persistent-buffer ring 及其删回流 DAG 修复，不覆盖替代路线、
  AND 请求、AGV/预约或多个 persistent buffers。一般制造岛阈值、
  风险预算控制与 Pareto 定理仍开放。
- 被隔离的历史提交或外部项目产物不得直接转入本项目证据链。
- G4/G5 九个案例已退役为历史 discovery/regression；G6 必须先修复
  theorem/metric 分离、all-minimal local kernel、CRP local bridge 与
  closed-class taxonomy，再封存完全独立的新确认集。
