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

Gate 状态是：G0 仓库门通过，G1 文献门部分通过，G2 受限理论主链通过，
G3 严格小有限模型算法门通过，G4 确认集尚未冻结，G5 论文门尚未开始。
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
