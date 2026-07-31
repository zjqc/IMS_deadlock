# 符号表

本文档记录 `IMS-RAS` 候选理论的统一记号。状态：定义。

## 集合与索引

| 符号 | 含义 | 状态 |
| --- | --- | --- |
| `J` | 有限批工件集合，`|J| < infinity` | 定义 |
| `R` | 资源集合，含机器、缓冲、AGV、预约 token | 定义 |
| `M` | 机器资源子集，`M subset R` | 定义 |
| `B_in, B_out` | 输入缓冲、输出缓冲资源子集 | 定义 |
| `A` | AGV 或运输载具资源子集 | 定义 |
| `V` | reservation-token resource subset; keep distinct from stopped state sets | Definition |
| `P_j` | 工件 `j` 的有限路线阶段集合 | 定义 |
| `E` | 离散事件集合 | 定义 |
| `E_c, E_u` | 可控事件与不可控事件 | 定义 |
| `D, F` | CTMC 中的死锁吸收类与完成吸收类 | 定义 |
| `S_reach` | support graph 中存在到 `A_stop` 路径的诊断状态集合 | 定义 |
| `S_T` | certified probability-one absorption domain, `S_T = T \ B_closed` | 定义 |
| `B_closed` | unselected closed SCCs 的 reverse basin | 定义 |
| `A_abs` | global gate: `B_closed = empty` over claimed nonabsorbing domain | 定义 |

## 容量、持有与请求

| 符号 | 含义 | 状态 |
| --- | --- | --- |
| `cap(r)` | 资源 `r` 的整数容量 | 定义 |
| `hold_s(j,r)` | 状态 `s` 下工件 `j` 实际持有资源 `r` 的数量 | 定义 |
| `res_s(j,r)` | 状态 `s` 下工件 `j` 持有的预约 token 数量 | 定义 |
| `occ_s(r)` | `sum_j hold_s(j,r)`，物理占用量 | 定义 |
| `book_s(r)` | `sum_j res_s(j,r)`，预约占用量 | 定义 |
| `avail_s(r)` | `cap(r)-occ_s(r)`；预约可用量另记，不与物理占用混合 | 定义 |
| `need_s(j,r)` | 工件 `j` 在状态 `s` 为使某个待选后继可发生而需要的资源数量 | 定义 |
| `rem_s(r)` | 等待证书中扣除不可自主释放持有后的残余容量 | 定义 |

## 路线与事件

| 符号 | 含义 | 状态 |
| --- | --- | --- |
| `route(j)` | 工件 `j` 的有限路线，可含分支或运输段 | 定义 |
| `stage_s(j)` | 工件 `j` 当前阶段 | 定义 |
| `pre(e), post(e)` | 事件 `e` 的前置与后置状态约束 | 定义 |
| `fire(s,e)` | 事件 `e` 在状态 `s` 可发生时的直接后继 | 定义 |
| `Z` | 零时间事件集合，例如自动卸载、预约兑现、闭包内部整理事件 | 定义 |
| `leadsto_Z` | 仅由零时间事件诱导的可达关系 | 定义 |
| `Cl(s)` | 从 `s` 出发经过任意零时间事件到达的稳定后继集合 | 定义 |
| `kappa(s)` | 只在闭包终止且合流，或给定固定优先级/排序语义变体时定义的确定闭包函数 | 定义 |

## 语义与图

| 符号 | 含义 | 状态 |
| --- | --- | --- |
| `S` | 有限状态空间 | 定义 |
| `S_st` | 闭包归一化后的稳定状态集合 | 定义 |
| `s ->e s'` | 状态转换系统中的标号转换 | 定义 |
| `mathcal T` | IMS 的闭包归一化有限 LTS，避免与 CTMC 暂态集合混用 | 定义 |
| `W_s` | 状态依赖等待结构；可为 job-resource 二部图或容量敏感超图 | 定义 |
| `K` | 封闭阻塞核，含阻塞工件、资源需求边和不可释放证据 | 拟证明 |
| `C` | resource-request directed cycle; only in restricted single-instance subclasses can it be a sufficient-certificate candidate | Counterexample boundary |
| `Theta` | IMS 模型参数，包括容量、WIP、路线混合、速率和预约规则 | 定义 |

## Petri 网桥

| 符号 | 含义 | 状态 |
| --- | --- | --- |
| `N=(P_P,T_P,Arc_P,W_P,M0)` | 构造的有界 Petri 网；`T_P` 是 Petri transition 集 | 拟证明 |
| `mu` | Petri 网标识 | 定义 |
| `phi(s)` | IMS 稳定状态到 Petri 标识的映射 | 拟证明 |
| `psi(mu)` | 可逆子类中 Petri 标识到 IMS 状态的映射 | 拟证明 |
| `Sigma` | siphon，即每个输入变迁也有输出变迁落入该 place 集 | 文献基线 |
| `Sigma_deadly` | 致死虹吸，存在可达标识使其失标且阻塞相关变迁 | 文献基线 |

## 概率层

| 符号 | 含义 | 状态 |
| --- | --- | --- |
| `Q` | 有限 CTMC 生成元 | 定义 |
| `Q_{S_T,S_T}, Q_{S_T,D_sel}, Q_{S_T,F}` | 暂态到暂态、暂态到死锁、暂态到完成的生成元分块 | 定义 |
| `h_i` | committor from state `i` for hitting selected bad target `D_sel` before `F` | Literature baseline |
| `tau_i` | 从状态 `i` 到任一吸收类的平均吸收时间 | 文献基线 |
| `theta` | 模型参数或速率参数 | 定义 |
| `partial_theta h` | committor 参数敏感性 | 拟证明 |
| `Q^h` | Doob-`h` 条件化生成元，只在 `h_i>0` 的状态上定义 | 文献基线 |

## 证据状态标签

| 标签 | 用法 |
| --- | --- |
| 定义 | 本项目给出的语义约定或记号 |
| 文献基线 | 已有文献中成立的结果或标准方程 |
| 拟证明 | 本项目首篇论文目标命题，尚需完整证明 |
| 计算验证 | 小模型枚举或数值校验目标，不替代证明 |
| 反例 | 已知会击穿更强或错误命题的边界案例 |

## G6-B Certified Absorption-Domain Symbols

| Symbol | Meaning | Status |
| --- | --- | --- |
| `D_sel` | Selected bad target union, `D_sel := D_global union D_local` | Definition |
| `A_stop` | Selected stopped target, `A_stop := D_sel union F` | Definition |
| `X_stop` | full finite stopped state set for the G6-B stopped process | Definition |
| `T` | Nonabsorbing stopped states, `T := X_stop \ A_stop` | Definition |
| `S_reach` | States in the complete stopped-LTS support graph with at least one path to `A_stop` | Diagnostic, nonselectable |
| `C_closed` | Unselected closed SCC with membership `C_closed subset T`; closedness is checked against all outgoing positive-rate edges in the full stopped graph, including edges to selected `A_stop` | Certificate component |
| `B_closed` | Reverse basin in `T` of all unselected closed SCCs | Certificate component |
| `S_T` | `T \ B_closed`; states that hit `A_stop` with probability one in the finite positive-rate stopped CTMC | Certified absorption domain |
| `A_abs` | Global-domain gate `B_closed = empty` over the claimed nonabsorbing analysis domain | Strict protocol gate |
| `rate_manifest_hash` | Hash of the full declared rate manifest; absent rates and explicit empty rates are distinct | Nullable hash |
| `positive_rate_graph_hash` | Identity of the realized positive-rate stopped graph used by the certificate | Nullable hash |
| `policy_filter_hash` | Identity of the policy-filter declaration, including no-filter declarations | Nullable hash |
| `absorption_domain_hash` | Certificate-domain identity over algorithm version, `state_space_hash`, `partition_hash`, `positive_rate_graph_hash`, `policy_filter_hash`, selected IDs, unselected closed SCCs, `B_closed`, and `S_T` | Nullable hash |
| `estimand_id` | Identity binding the v2 estimand, selected targets, partition identity, rate-manifest identity, positive-rate graph, policy filter, and certified absorption-domain identity | Nullable hash |
