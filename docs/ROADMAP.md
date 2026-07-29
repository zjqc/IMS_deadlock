# IMS Deadlock Gate Roadmap

本路线图采用用户批准的理论优先顺序。Gate 的 `PASS` 只表示其明确列出的
受限结论已满足，不把候选定理、发现集程序结果或文献摘要包装成完成证据。

## 当前状态

| Gate | 状态 | 当前证据 | 未关闭项 |
| --- | --- | --- | --- |
| G0 仓库门 | PASS | Dell 目标路径、GitHub SSH、干净集成 worktree 和项目专用 Python 3.13.9 已核验；污染历史保持隔离；最终源状态在该 worktree 验证后前推 `origin/main` | 无 |
| G1 文献门 | PARTIAL | 六条文献链、39 项审计矩阵、13 个全文定理锚点、迁移卡；L04/L16/L22/L29 已完成范围定位 | `L31` 新增可达部分死锁类别并重置饱和计数；L30/L31 需全文；需以 L29-L31 为种子再完成连续两轮无新类别追踪 |
| G2 理论门 | PASS（严格受限主链） | P1 有限 LTS/reachability-net；P2 capacity-mediated 封闭核 iff；P2c `IMS-SIP^1` 诊断虹吸双向桥；P3 偏序充分条件；P3d `BIX1-SAT` 可达阈值；P4 CTMC；P5 supervisor；P6 复杂性边界 | plant-level structured Petri/S3PR 桥、persistent-buffer 一般岛阈值、一般紧凑 IMS 精确复杂性和 risk-budget 控制仍开放 |
| G3 算法门 | PASS（严格小有限模型 + P2c/P3d） | Dell 干净集成 worktree、项目 Python 3.13.9：111 tests、Ruff check/format、strict mypy；C0 exact Petri bridge、拒绝边界、BIX1-SAT 144 点小网格和双重复核通过 | 一般 plant/S3PR、结构案例物理速率、persistent-buffer 一般阈值和风险预算/Pareto 算法仍开放 |
| G4 案例冻结门 | NOT FROZEN | C0-C5 发现集、反例账本、预注册模板和冻结协议已建立 | 确认模型、参数范围、哈希、指标与基线尚未冻结；不得报告确认结果 |
| G5 论文门 | NOT STARTED | 研究定位、定理梯和证据边界已建立 | 需 G3/G4 后进行精确分析与独立 DES 一致性、负例/代价/边界报告和论文成稿 |

## G0 仓库门

通过条件：

- 远程主目录是 `D:\py_pro\IMS_deadlock`，连接
  `git@github.com:zjqc/IMS_deadlock.git`；
- 污染提交只按确认 lease 隔离/替换，不混入新历史；
- `buffer-design`、`makespan_doob_h` 和旧 `work_case` 仅只读取证；
- 仓库不含 secret、环境、缓存、下载论文或历史输出；
- 项目自己的 Python、依赖和验证命令已在锁定 worktree 中核验。

## G1 文献门

通过条件：

- Petri/S3PR、DES/RAS、有限缓冲队列、AGV/交通、吸收 CTMC 与稀有事件
  六条链均有审计矩阵；
- 前向/后向追踪连续两轮不产生新的模型类别、定理类型或关键反例；
- 每个实际进入定理的来源都有全文定位、原假设、迁移卡和不可迁移边界；
- metadata/abstract/context 只能用于导航或历史说明。

当前 `PARTIAL` 不阻止受限 P1-P6 的项目内证明，因为这些证明所用的外部
锚点已核验；它阻止任何“首个可达/无需 reachability tree 的结构检测”
或“一般有限容量阈值”优先权表述，也阻止把 L30/L31 摘要写成定理依据。

## G2 理论门

最低通过链：

`IMS-RAS^CW 稳定语义`
`-> finite LTS/reachability-net`
`-> covering closed blocking core iff capacity-mediated deadlock`
`-> IMS-SIP^1 state-induced wait-snapshot minimal empty siphon dual`
`-> strict-precedence restricted sufficient condition`
`-> BIX1-SAT reachable saturation threshold`
`-> finite competing-absorption CTMC`
`-> exact finite full-observation supervisor`
`-> representation-sensitive complexity boundary`.

所有更强结论必须保持 `拟证明` 或 `开放`：

- 一般 IMS 与 plant-level structured Petri/S3PR 的同构；
- `IMS-SIP^1` 之外最小封闭核与最小致死虹吸的双向最小性；
- persistent-buffer、替代路线或外部 drain 下的一般双向岛精确阈值；
- 一般紧凑 IMS 在 NP-hard 下界之上的完备复杂性；
- risk-budget 控制的递归可行性/Pareto 最优性。

## G3 算法门

通过条件：

- 穷举小模型的稳定状态与事件映射，输出确定性状态 ID 和最短可达前缀；
- 核验 capacity-aware closed kernel，并把 simple cycle、terminal SCC/knot、
  Banker、Petri siphon 和 exact supervisor 分成不同假设层；
- 对 `IMS-SIP^1` 构造 immutable state-induced wait-snapshot net，核验
  evidence fidelity、minimal empty siphon，并对 OR/AND、多容量和
  control-only 边界给出机器可读拒绝；
- 对 `BIX1-SAT` 从空状态穷举小网格，截断行不得计作理论证据；
- exact supervisor 检查不可控闭合、marked coaccessibility 与初始可行性；
- CTMC 报告 committor、平均吸收时间、线性残差、灵敏度、Doob-h 行和和
  生成元来源；
- 随机 DES/CTMC 采样使用独立可复现随机流、置信区间和 stream manifest；
- `validate`、`prove`、`quantify`、`simulate`、`verify-case` 输出版本化 JSON；
- `pytest`、`ruff`、strict `mypy` 在项目专用远程环境全部通过。

程序枚举是证明审计器，不替代 P1-P6 的数学证明。

## G4 案例冻结门

冻结前：

- C0-C5 仅是发现集，允许因反例修正定义和假设，但每次修改进入账本；
- C4 必须保留“完整运输模型有证书、机器投影漏检”的成对结果；
- C5 必须保留“双向回流阻塞、删除回流 DAG 修复”的成对模型；
- 确认集参数族、中型独立重建和对抗案例必须未参与主命题拟合。

冻结动作必须一次性提交参数范围、指标、基线、随机流方案和内容哈希。
字段为空、哈希未提交或理论门未关闭时，状态只能是 `NOT FROZEN`。

## G5 论文门

通过条件：

- 精确状态/CTMC 分析与独立 DES 置信区间一致；
- 报告 false positive/false negative、失败命题、监督性能代价和适用边界；
- 不删除冻结后的失败案例，不事后更换指标；
- 论文主张能逐项回链到定理、原假设、迁移卡、案例哈希和机器验证。

## 科学停止条件

若最终只剩“把 Petri、RAS、CTMC 和仿真工程拼装起来”，就在扩展案例和
大规模实验前停止并重构科学问题。若一般等价被反例推翻，则收缩到可证明
子类并把反例作为边界结果；不得模糊定义或降低证据标准。

历史标识 `e0b07a52ed667ce2651dfccf2455d6876a96b02d` 仅作隔离来源记录，
不能成为案例、算法、证明或验证证据。
