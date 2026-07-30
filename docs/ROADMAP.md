# IMS Deadlock Gate Roadmap

本路线图采用用户批准的理论优先顺序。Gate 的 `PASS` 只表示其明确列出的
受限结论已满足，不把候选定理、发现集程序结果或文献摘要包装成完成证据。

## 当前状态

| Gate | 状态 | 当前证据 | 未关闭项 |
| --- | --- | --- | --- |
| G0 仓库门 | PASS | Dell 目标路径、GitHub SSH、干净集成 worktree 和项目专用 Python 3.13.9 已核验；污染历史保持隔离；最终源状态在该 worktree 验证后前推 `origin/main` | 无 |
| G1 文献门 | PASS（scope-bounded） | 六条文献链、43 项审计矩阵、20 个全文/全文审计锚点、迁移卡；L30-L35 与 B05 七篇审计已纳入比较边界；R7/R8 类别饱和保持 | 不支持首创性、系统综述或一般 IMS/Petri 等价；G4 必须检验 CRP、recorder、SBA、L30/B05 comparator 边界 |
| G2 理论门 | PASS（严格受限主链） | P1 有限 LTS/reachability-net；P2 capacity-mediated 封闭核 iff；P2c `IMS-SIP^1` 诊断虹吸双向桥；P3 偏序充分条件；P3d `BIX1-SAT` 可达阈值；P3e `BIX2-PERSIST` 三资源 ring 精确阈值与同语义 DAG 修复；P4 CTMC；P5 supervisor；P6 复杂性边界 | plant-level structured Petri/S3PR 桥、替代/AND/AGV/预约/多 persistent-buffer 一般岛阈值、一般紧凑 IMS 精确复杂性和 risk-budget 控制仍开放 |
| G3 算法门 | PASS（严格小有限模型 + P2c/P3d/P3e） | 原 G3 证据为 123 tests；加入 G4/G5 协议、capture/scoring 基础设施后，Dell 项目 Python 3.13.9 全库 242 tests、Ruff check/format、strict mypy 通过；原 C0、BIX1/BIX2 结果不变 | 一般 plant/S3PR、结构案例物理速率、一般 persistent-buffer/AGV 阈值和风险预算/Pareto 算法仍开放 |
| G4 案例冻结门 | PASS（historical C seal；已在 G5 原样执行） | A=`f9b9a5a5652c7a49053e7ef26d08911bd757f465`，B2=`58bbd4ab7da8c2c1d0bcdea4a12f2ae7c020d09a`，C=`e91be4d6d7511c76918093899269de4b78e69fd8`；封存时 checker 为 `FROZEN`、`errors=[]`、`confirmation_results_inspected=false`；随后只在 G5-B execution lock 下执行一次 primary 和一次 repro | G4/G5 九行已退役为历史 discovery/regression，不能再次充当 held-out；后续缺陷必须进入独立 successor freeze |
| G5 论文门 | FAIL（evidence closed） | G5-A=`b5e5dc0494b23a54c78c420bbca50a3639de8bff`，G5-B=`8aa752804b885b79e5371c98e7961087c540f2a8`，G5-C=`ff281481068a2325cb0bde00e85fd7b753ba854a`；9/9 案例完成 primary/repro，raw/canonical/stderr hash 一致；锁定 scorer 为 `4/3/2`，透明 theorem audit 为 `6/1/2` 并另保留两项 minimality failure | CRP local bridge 预测失败；grid/medium 因 `D/F` 未穷尽 terminal classes 而确定性拒绝；不能形成完整 exact/DES 证据链或宣称论文门通过 |
| G6 局部核—终端类恢复门 | NEXT HARD GATE / PRE-IMPLEMENTATION | G5 负结果、评分 category error 和复现证据已定位；恢复义务已进入反例账本、证书、概率层和证明义务 | 先完成 theorem/metric 分离、all-minimal local kernels、CRP local bridge、closed-class taxonomy 与 synthetic regressions；再创建独立 discovery/confirmation set 并重新封存，封存前不得运行新 held-out |

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

当前 `PASS（scope-bounded）` 只关闭本项目受限 P1-P6 与下一轮 G4 设计所需
的文献边界，不是系统综述完成、首创性完成或一般 IMS/Petri 等价完成。
20 个锚点包括原 P1-P6 所用全文 theorem/equation/context anchors，以及
七篇新增全文审计边界：

- `L30` finite-capacity S3PR/ENS3PR 是保守充分 resource-configuration
  baseline，不是 exact reachable iff threshold。
- `L31` S4PR CRP 是 marking-level partial-deadlock iff certificate；
  candidate reachability 仍需 SBA/可执行前缀检查，复杂性 NP-hard。
- `L32/L33` output-only recorder-place USPN/UniPN transformations 不改变
  原 transition enabling，但不自动替代 IMS operational 到 plant Petri 的
  语义桥，也不自动关闭固定原目标到 recorder target 的量化义务。
- `L34/L35` BA/SBA 决定给定 NIS 是否有 legal firing sequence，其
  `O(n*n1*(c*m+n^2))` 界不得写成标准 bit-polynomial IMS 判定。
- `B05` compressed maximally permissive supervisor 依赖 full RG 和 NP-hard
  MCPP，只能作为小 PN overlap comparator。

因此 G1 允许继续推进 G4，但仍阻止任何“首个可达/无需 reachability tree
的结构检测”、“首次使 Petri 可达性可判定/多项式化”、“一般 finite-capacity
exact threshold”或“一般紧凑 IMS 最大许可 supervisor”表述。

## G2 理论门

最低通过链：

`IMS-RAS^CW 稳定语义`
`-> finite LTS/reachability-net`
`-> covering closed blocking core iff capacity-mediated deadlock`
`-> IMS-SIP^1 state-induced wait-snapshot minimal empty siphon dual`
`-> strict-precedence restricted sufficient condition`
`-> BIX1-SAT reachable saturation threshold`
`-> BIX2-PERSIST exact three-resource ring threshold and paired DAG repair`
`-> finite competing-absorption CTMC`
`-> exact finite full-observation supervisor`
`-> representation-sensitive complexity boundary`.

所有更强结论必须保持 `拟证明` 或 `开放`：

- 一般 IMS 与 plant-level structured Petri/S3PR 的同构；
- `IMS-SIP^1` 之外最小封闭核与最小致死虹吸的双向最小性；
- P3e 明确三资源子类之外的 persistent-buffer、替代/AND 请求、AGV/预约
  或外部 drain 一般双向岛精确阈值；
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
- 对 `BIX2-PERSIST` 按预注册 discovery grid 穷举 ring 阈值及同语义 DAG
  修复；截断、invalid instance、DAG 无完成路径或任一 mismatch 均不得
  计作证据；
- exact supervisor 检查不可控闭合、marked coaccessibility 与初始可行性；
- CTMC 报告 committor、平均吸收时间、线性残差、灵敏度、Doob-h 行和和
  生成元来源；
- 随机 DES/CTMC 采样使用独立可复现随机流、置信区间和 stream manifest；
- `validate`、`prove`、`quantify`、`simulate`、`verify-case` 输出版本化 JSON；
- `pytest`、`ruff`、strict `mypy` 在项目专用远程环境全部通过。

程序枚举是证明审计器，不替代 P1-P6 的数学证明。

## G4 案例冻结门

历史 C-sealed 确认集：

- C0-C5 与 BIX2-PERSIST 仅是发现集，允许因反例修正定义和假设，但每次
  修改进入账本；BIX2 参与过 P3e 推导，不得进入确认集；
- C4 必须保留“完整运输模型有证书、机器投影漏检”的成对结果；
- C5 必须保留“双向回流阻塞、删除回流 DAG 修复”的成对模型；
- 当前候选确认集参数族、中型独立重建和对抗案例记录为
  `independent_preregistration`，不得从 C0-C5、BIX1-SAT 或 BIX2-PERSIST
  复制、改名或参数平移；
- 当前候选包含九个 case：S4PR CRP agreement、unreachable structural
  candidate、BAS/AGV/AND outside-S4PR refusal、recorder fixed-target
  quantification、`L30` supplied sufficient inequalities、`B05` adapted
  monitor cover、ten-cell IMS parameter grid、medium island rebuild、adversarial
  OR-of-AND/reservation boundary；
- 十格 grid 预测固定为 `G01=false`、`G02=false`、`G03-G10=true`；
- supervisor throughput/makespan/WIP/due-date-risk cost、conditioned path
  mass、rare-event efficiency 在当前 G4 中全部不适用；exact CTMC probability、
  mean absorption time 与 DES confidence interval 仅适用于 grid 和 medium。

结构验证只允许读取、解析、哈希和 schema/checker 测试。C seal 之前不得运行
`verify-case`、`quantify`、`simulate`、supervisor synthesis、CTMC solve、DES
或 rare-event 后端；不得检查、汇总或回填 held-out 输出。

冻结动作已由 A/B2/C 三提交闭合。`FREEZE_ENTRY.json` 锁定参数范围、指标、
基线、随机流方案、九个 artifact hash 与九个 case hash；提交后的 Dell
checker 返回 `FROZEN`、`errors=[]`、`confirmation_results_inspected=false`。
该 PASS 只表示确认协议在结果检查前已冻结，不表示任何确认预测得到支持。
G5 随后按锁定命令执行九行各一次 primary/repro；该面板现在已退役，不能
再次作为 held-out 或通过修复后重跑来改变其证据状态。

## G5 论文门

通过条件：

- 精确状态/CTMC 分析与独立 DES 置信区间一致；
- 报告 false positive/false negative、失败命题、监督性能代价和适用边界；
- 不删除冻结后的失败案例，不事后更换指标；
- 论文主张能逐项回链到定理、原假设、迁移卡、案例哈希和机器验证。

实际结论：`FAIL（evidence closed）`。

- 九个案例均只有一次 primary 和一次 repro；七例 exit 0，grid/medium
  都以相同非零 exit、空 stdout 和相同 stderr hash 确定性拒绝，没有 retry
  或第三次运行。
- 锁定 scorer 的原始 `4 SUPPORTED / 3 FALSIFIED / 2 INCONCLUSIVE`
  作为不可变证据保留。
- 事后规则审计发现 scorer 把两个独立
  `certificate_minimality=FAIL` 错并入 theorem falsifier；透明、非覆盖式
  审计为 `6 SUPPORTED / 1 FALSIFIED / 2 INCONCLUSIVE`，原始输出不删除。
- `G4_CRP_S4PR_AGREE` 仍是冻结预测失败：target reachability agreement
  没有关闭 local certificate 与 mapped-resource equality。
- grid/medium 保持 `INCONCLUSIVE`：在求解前发现 reachable non-`D/F`
  state 不能到达声明吸收类，因此没有 exact probability、mean time 或同目标
  DES 证据。

完整报告见 `docs/verification/G5_CONFIRMATION_REPORT.md`、
`G5_REPRODUCIBILITY_AUDIT.md` 和 `G5_CLAIM_EVIDENCE_TABLE.md`；评分勘误
见 `evidence/g5/G5_SCORING_ERRATUM.json`。

## G6 局部核—终端类恢复门

G6 是新科学门，不是 G5 repair rerun。通过顺序：

1. theorem prediction 与 ancillary metric 独立计分，execution status 不得
   被任一者覆盖；
2. global certificate、all-minimal local kernels 与 minimality evidence
   使用显式 scope；
3. CRP partial bridge 只消费声明的 local-kernel family，并冻结多核匹配量词；
4. CTMC 在 estimand 之前完成
   `D_global,D_local,F,R_livelock,R_terminal` closed-class decomposition；
5. 用未复用 G4 参数或状态的 synthetic regressions 关闭已知机制；
6. 建立新的 discovery set 与独立 confirmation set，预注册、hash lock、
   C seal 后才允许一次 primary/repro。

详细执行契约见
`docs/superpowers/plans/2026-07-30-g6-local-core-terminal-class-recovery.md`。

## 科学停止条件

若最终只剩“把 Petri、RAS、CTMC 和仿真工程拼装起来”，就在扩展案例和
大规模实验前停止并重构科学问题。若一般等价被反例推翻，则收缩到可证明
子类并把反例作为边界结果；不得模糊定义或降低证据标准。

历史标识 `e0b07a52ed667ce2651dfccf2455d6876a96b02d` 仅作隔离来源记录，
不能成为案例、算法、证明或验证证据。
