# 证明义务清单

本文件把定理梯拆成可审计义务。每条义务在完成前不得在论文中写成已证结论。

## T1 语义等价

状态：P1 项目内已证明（严格受限子类）；Petri 结构桥仍拟证明。

- `[closed in P1] PO-T1-1` 有限性：从 `CW1-CW3` 推出可达稳定状态空间有限。
- `[closed in P1] PO-T1-2` LTS 边构造：所有闭包归一化稳定后继进入有限 LTS。
- `[closed in P1] PO-T1-3` reachability net：每个可达稳定状态一个 place、每条 LTS 边一个 transition，1-safe bounded，正反轨迹归纳。
- `[closed in P1] PO-T1-4` 闭包处理：闭包终止；非合流时保留集合后继。
- `PO-T1-5` Petri 映射：在 `A7` 子类中证明 `phi` 与 firing 对应。
- `PO-T1-6` 反向映射：只有在无额外 Petri 标识歧义时证明 `psi`。

计算验证：

- 枚举所有小模型稳定状态，检查每个后继满足容量守恒。
- 对可投影子类比较 LTS trace 与 Petri firing trace。

## T2 容量介导死锁证书

状态：P2/P2a/P2b 对 capacity-mediated 子域已证明；一般操作死锁、非资源 guard 与软预约仍拟证明或边界。

- `[closed in P2] PO-T2-1` 从 capacity-mediated global operational deadlock 构造至少一个覆盖封闭阻塞核。
- `[closed in P2] PO-T2-2` 从覆盖封闭阻塞核按事件分类推出无 admissible successor；timed/transport completion 只有当前 enabled 时才进入 `Alt_s(j)`，并作为空需求替代排除。
- `[closed in P2] PO-T2-3` 证明 capacity-mediated 全局死锁需要覆盖所有未完成活动；否则只得局部死锁。
- `[closed in P2] PO-T2-4` 多容量 residual/witness 不能简化为简单环。
- `[closed in P2] PO-T2-5` 有限 capacity-ready OR-of-AND 替代后继与多 AGV/硬预约选择全部纳入阻塞条件；软预约排除在 P2 完备定理外。
- `[closed in P2a/P2b] PO-T2-6` 有限包含极小核存在；单实例受限子类中 terminal SCC 与 inclusion-minimal local kernel 的对应，以及 simple cycle 推论。
- `PO-T2-7` 为永久非资源 guard/外部同步缺失构造 P2 外反例，防止把一般停滞误写成容量核 iff。
- `PO-T2-8` G4 CRP agreement 行必须同时关闭三个独立义务：
  translated target 在冻结有限 LTS 中可达、冻结 IMS target snapshot 产生
  capacity-aware closed blocking certificate、以及 CRP resource-place 到 IMS
  resource 的冻结映射与 certificate kernel resource set 精确相等。仅有
  reachability agreement 不得命名为 partial-deadlock bridge agreement。

计算验证：

- 生成 `DeadlockCertificate` JSON，要求每条等待边有 job、resource、need、hold/reservation 和 residual 字段。
- 对 C1/C3 断言简单环或 WCC 不能单独触发死锁结论。

## T3 虹吸桥

状态：P2c 对 reachable stable `IMS-SIP^1` wait-snapshot diagnostic net
已证明并实现；一般 `IMS-RAS^CW` 到经典 S3PR/plant Petri 网的双向虹吸桥
仍不主张。

- `[closed in P2c] PO-T3-1` 给出 `IMS-SIP^1` 状态诱导
  wait-snapshot net：`free:r` place、`t_j: free:q(j)->free:h(j)`。
- `[closed in P2c] PO-T3-2` 证明 inclusion-minimal local closed core
  映射到 inclusion-minimal empty siphon。
- `[closed in P2c] PO-T3-3` 证明 inclusion-minimal empty siphon 在
  `IMS-SIP^1` 条件下反向恢复可审计 local blocking core。
- `[closed in P2c] PO-T3-4` 给出一般情形失败边界：C4/C5 conjunctive
  request、OR 替代、多容量 residual、control-only/approval-only siphon、
  soft reservation 和隐藏 release。
- `[closed in P2c] PO-T3-5` 标记 P1 reachability net、P2c
  wait-snapshot diagnostic net 与经典 S3PR plant net 的对象差异。
- `PO-T3-6` 若后续要使用经典 S3PR monitor theorem，仍需独立构造
  plant-level S3PR 子类映射；不得由 P2c 自动推出。
- `PO-T3-7` 若使用 `L32/L33` recorder-place/USPN/UniPN transformation，
  必须先独立证明原 IMS operational 到 source plant Petri 的语义桥；
  recorder transformation 不能替代此前置义务。随后还要记录原 trace 到
  instrumented counter state 的保存方向、固定原目标映射到 recorder
  target 时的 existential/fixed-count 量化、完成/死锁谓词投影，以及
  BAS/AGV/预约/OR/AND/闭包语义是否已进入 source plant model。
- `PO-T3-7a` G4 的 `L32/L33` fixed-recorder-target comparator 必须证明：
  对给定有限 LTS、预注册目标状态、事件计数器集合和固定输出计数，增强
  BFS 在 `(state, bounded_count_vector)` 上的可达性等价于“存在一条原 LTS
  路径到该目标且记录事件计数恰为固定向量”。计数上界剪枝、最短 witness
  的确定性、目标/计数输入不可由 reachable output 推断，都必须可审计。
  该义务只关闭 adapted finite-LTS oracle，不关闭 `L32/L33` source
  transform reproduction。
- `PO-T3-8` 若使用 `L31` CRP，必须先限定到 S4PR overlap，并把 CRP
  marking-level iff 与 IMS closed blocking core 的对象差异写清楚；候选
  marking 没有 executable prefix 时必须作为 unreachable candidate 拒绝。
- `PO-T3-8a` G4 的 `L31` CRP evidence-profile audit 必须证明 reachability
  分类独立于 supplied CRP/legal-prefix claim：输入只可包含 S4PR 适用性、
  外部 S4PR embedding hash、冻结 CRP/resource-limit-pair set、冻结 IMS
  target state 和外部 legal-prefix claim；可达/不可达必须由独立有限
  LTS BFS 给出。audit 不得生成 CRP、不得运行 SBA、不得把
  `evidence_disagreement` 改写成 source theorem result。

计算验证：

- 对 `IMS-SIP^1` 子类枚举 siphon，与 core 做包含/最小性检查。
- 对缺少 reachability witness、非极小证书、C4/C5 conjunctive request、
  OR 替代和多容量状态断言 bridge 非适用且不生成 `corresponding_siphon`。
- 对 AGV/硬预约 token 仅在普通单位资源语义下允许进入 wait-snapshot net；
  soft reservation 保持非适用。
- G4 必须包含 recorder-preservation/target-quantification obligation：
  若 recorder case 可证明保存所需目标，则承认为 comparator agreement；
  若只能证明单向保存或量化不匹配，则记录为未迁移边界，而不是硬造负例。
- G4 CRP evidence-profile 必须保存 disagreement/unreachable/not-applicable
  等负面分类，不得用 CRP 方程或外部 claim 覆盖独立 BFS 结论。

## T4 结构充分条件与阈值

状态：P3 chain-decomposable strict-precedence 子类排除 capacity-mediated
deadlock 已证明；P3c 的 `BIX0` 是候选态前置命题；P3d 的
`BIX1-SAT` 启动/完成饱和族有精确可达阈值；P3e 关闭一个显式
persistent-D 三资源环及其删回流修复。一般操作死锁、多容量/聚合预约和
更一般 persistent-buffer/AGV 制造岛阈值仍拟证明。

- `[closed in P3] PO-T4-1` 定义获取偏序覆盖所有关键资源。
- `[closed in P3] PO-T4-2` 定义 chain-decomposable certificate 并证明证书到资源链选择引理。
- `[closed in P3] PO-T4-3` 用有限严格偏序反证 circular wait 不存在。
- `[closed in P3] PO-T4-4` 明确该命题不推出标准 nonblocking 或几乎必然完成。
- `[closed in P3] PO-T4-4a` 明确该命题不排除永久非资源 guard 或外部同步缺失导致的一般操作死锁边界。
- `[closed in P3c] PO-T4-5` 定义无成功 transfer 的双向启动饱和
  候选态 `BIX0`。
- `[closed in P3c] PO-T4-6` 证明 `BIX0` 候选态 closed-kernel iff
  `n_A>=c_M` 且 `n_B>=c_G`；不再把它作为可达性定理。
- `[closed in P3d] PO-T4-6a` 定义 `BIX1-SAT` 的显式 start/completion
  事件链、reservation token `V` 和空初态 BFS 观察器。
- `[closed in P3d] PO-T4-6b` 证明 `BIX1-SAT` 可达 deadlock iff
  `n_A>=c_M` 且 `n_B>=c_G`；若 BFS 截断，不计入 match 或证据。
- `[closed in P3e] PO-T4-6c` 为显式 `M->D->Q->M` persistent-buffer
  ring 证明可达 deadlock iff
  `n_A>=c_M,n_B>=c_D,n_C>=c_Q`。
- `[closed in P3e] PO-T4-6d` 删除 `Q->M` 后证明无
  capacity-mediated global deadlock，并构造串行 marked completion
  路径；DAG 行只有同时满足两项才计为 match。
- `PO-T4-6e` 为替代路线、AGV/预约、外部 drain、多个 persistent
  buffers 与强制时序的更一般制造岛族寻找分段阈值或最小反例。
- `[closed in P6] PO-T4-7` 用 SU-RAS identity reduction 证明无
  buffer/AGV/reservation/BAS 的无环单单位 IMS 子类安全性为 NP-complete；
  对一般紧凑 IMS 只声称至少 NP-hard，不猜测更强完备类。
- `PO-T4-8` `L30` finite-capacity S3PR/ENS3PR 只能迁移为保守充分
  resource-configuration baseline；若声称 exact reachable iff threshold，
  必须另外证明候选死锁 marking 的 reachability、阈值必要性和 IMS 语义
  覆盖，不能由 liveness-sufficient initial marking theorem 推出。
- `PO-T4-8a` G4 的 `L30` supplied-inequality checker 必须证明输出含义只是
  sufficient-condition evaluation：输入需声明 `finite_capacity_s3pr_ens3pr`
  适用且 inequality provenance 为 `sms_derived_external`；checker 只评价
  已供应整数线性 `>=` 约束和容量向量。不得声称 SMS enumeration、Algorithm
  1、ILP、minimum `M0(P_R)`、必要性、或 exact IMS threshold。
- `PO-T4-9` `L34/L35` BA/SBA 给定 NIS 的 legal-firing-sequence 判定只能
  作为比较过滤器；项目正向可达结论仍须保存显式合法 firing/event
  sequence，小确认模型的不可达结论须由完整有限 LTS/BFS 穷举独立关闭。
  复杂性报告必须区分参数/伪多项式界与标准 bit-polynomial bound。

计算验证：

- 对同时满足偏序与 chain-decomposable 条件的 C2 网格断言无 capacity-mediated 覆盖封闭核；非 chain-decomposable 聚合核和非资源 guard 阻塞登记为 P3 外边界。
- 对 C5 双向/删回流成对模型记录首个死锁参数。
- 对 `BIX0` 小网格逐点核验 P3c 候选态阈值。
- 对 `BIX1-SAT` 小网格逐点核验 P3d 可达阈值；`c_D,c_V` 不变性只因
  witness prefix 没有成功 transfer。不得把 CE-BIXD1/persistent-D
  计为 P3d theorem mismatch。
- 对 `BIX2-PERSIST` 的预注册 32 行 threshold/one-below ring/DAG
  发现网格逐点核验 P3e；截断、DAG 无完成路径或任一 mismatch 都是失败
  证据。
- G4 CRP triad 必须同时含：S4PR overlap agreement、unreachable
  structural/algebraic candidate、以及 BAS/AGV/AND outside-S4PR refusal。

## T5 概率层

状态：P4 项目内已证明（严格有限 CTMC）；条件跳过程/Doob-style 主来源
L28 已全文核验，竞争吸收 IMS 适配由 P4 独立证明。

- `[closed in P4] PO-T5-1` 构造有限生成元 `Q`，先做 closed-class 分解，再分块为 `S_T,D,F` 和可能的 `R_c`。
- `[closed in P4] PO-T5-2` committor 方程：`h_D=1`，`h_F=0`，`Q_{S_T,S_T} h_{S_T} = -Q_{S_T,D} 1`；只在吸收假设 `A_abs` 成立或限制到 `S_T` 时使用。
- `[closed in P4] PO-T5-3` 平均吸收时间：`Q_{S_T,S_T} tau_{S_T} = -1`；若 `R_c` 可达且未并入吸收目标，需报告无穷或不定义边界。
- `[closed in P4] PO-T5-4` 敏感性：`Q_{S_T,S_T} partial_theta h_{S_T} = - (partial_theta Q_{S_T,S_T}) h_{S_T} - (partial_theta Q_{S_T,D}) 1`。
- `[closed in P4] PO-T5-5` Doob-`h`：在 `H union D` 上定义，`D` 吸收，跳入 `F` 的条件化率为 0，`q^h_ij = q_ij h_j / h_i` 只在 `i,j in H`。
- `[closed in P4] PO-T5-6` 解释边界：Doob-`h` 是条件路径动力学，不是控制器。
- `PO-T5-7` G4 grid/medium 的 CTMC 必须由同一冻结 `CaseSpec` 的完整 stable
  LTS 和逐事件冻结速率生成。任何截断、多个 closure initial state、未分类
  terminal class、缺失 event rate 或非吸收 recurrent class 都触发 refusal，
  不得补造 rate matrix。
- `PO-T5-8` G4 的 independent DES 只作为同一 case-derived CTMC 的
  Gillespie cross-check；master seed、replication count 和
  `sha256(master_seed:replication_index)` 派生规则在结果检查前冻结。
  该实现不支持 rare-event efficiency 或 conditioned path mass，二者在
  G4 必须保持不适用。

计算验证：

- 线性系统残差小于预注册容差。
- DES 仿真置信区间覆盖精确 CTMC 概率。

## T6 控制层

状态：P5 精确 supervisor 基准已项目内证明（严格有限全观测状态域）；结构/概率控制仍拟证明。

- `[closed in P5] PO-T6-1` 划分可控与不可控事件。
- `[closed in P5] PO-T6-2` 最大不变安全集固定点必须对所有不可控后继闭合。
- `[closed in P5] PO-T6-3` 最大许可 state-based nonblocking supervisor 保留所有能到 marked completion 的安全行为；nondeterministic events 用 all-successor 量词。
- `[closed in P5] PO-T6-3a` 若 `x0 notin Y*`，报告 initial-state infeasible，不能输出空策略并称成功。
- `[closed in P6] PO-T6-3b` 区分显式 LTS 输入和紧凑 IMS 输入：
  前者 fixed point 有 `O(|X|(|X|+|->|))` 保守多项式上界，后者的初始
  可行性至少 NP-hard，且完整显式策略可能具有指数输出大小。
- `PO-T6-4` 结构干预 hitting set 需要 core 全集完备。
- `PO-T6-5` 若干预产生新 core，必须迭代反例生成。
- `PO-T6-6` 概率控制给出风险预算递归可行性或保守界。
- `PO-T6-7` `B05` compressed maximally permissive supervisor 只能在完整
  RG、legal/FBM covering 和 MCPP 求解已明确的小 PN overlap 中作为
  comparator；不得作为紧凑 IMS 的多项式或一般最大许可控制定理。
- `PO-T6-7a` G4 的 `B05`-inspired exhaustive cover 必须证明 optimality 只
  相对于 supplied candidate-monitor set：给定 explicit legal states、
  first-met bad states 和候选 monitor cover sets，穷举选择保持 legal 且覆盖
  bad 的字典序确定最小基数子集；若候选集不完备则返回 infeasible。该证明
  不得外推为 P-semiflow synthesis、MCPP optimality、source-net minimal
  control places 或 source-theorem maximal permissiveness。

计算验证：

- 对小 LTS 输出禁用事件集、保留状态数和不可控闭合检查。
- 对概率控制输出风险预算残差和 Pareto 候选点。
