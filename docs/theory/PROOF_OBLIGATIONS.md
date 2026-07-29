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

计算验证：

- 生成 `DeadlockCertificate` JSON，要求每条等待边有 job、resource、need、hold/reservation 和 residual 字段。
- 对 C1/C3 断言简单环或 WCC 不能单独触发死锁结论。

## T3 虹吸桥

状态：拟证明。

- `PO-T3-1` 给出 IMS 子类到 Petri place/transition 的构造。
- `PO-T3-2` 证明最小 closed core 映射到最小或包含最小致死 siphon。
- `PO-T3-3` 证明致死 siphon 反向映射到可审计阻塞核的条件。
- `PO-T3-4` 给出一般情形失败的最小反例。
- `PO-T3-5` 标记 S3PR 可用条件与超出条件。

计算验证：

- 对 Petri 子类枚举 siphon，与 core 做包含/最小性检查。
- 对 AGV/预约投影反例检查 false negative。

## T4 结构充分条件与阈值

状态：P3 chain-decomposable strict-precedence 子类排除 capacity-mediated
deadlock 已证明；P3c 的 `BIX0` 启动饱和族有精确可达阈值；一般操作
死锁、多容量/聚合预约和含 transfer/drain 的双向制造岛阈值仍拟证明。

- `[closed in P3] PO-T4-1` 定义获取偏序覆盖所有关键资源。
- `[closed in P3] PO-T4-2` 定义 chain-decomposable certificate 并证明证书到资源链选择引理。
- `[closed in P3] PO-T4-3` 用有限严格偏序反证 circular wait 不存在。
- `[closed in P3] PO-T4-4` 明确该命题不推出标准 nonblocking 或几乎必然完成。
- `[closed in P3] PO-T4-4a` 明确该命题不排除永久非资源 guard 或外部同步缺失导致的一般操作死锁边界。
- `[closed in P3c] PO-T4-5` 定义无成功 transfer 前缀的双向启动饱和
  参数族 `BIX0`。
- `[closed in P3c] PO-T4-6` 证明 `BIX0` 死锁可达 iff
  `n_A>=c_M` 且 `n_B>=c_G`，并给出 persistent-D 一般化的最小边界反例。
- `PO-T4-6a` 为含成功 transfer、D drain、替代路线与时序的更一般
  制造岛族寻找分段阈值或最小反例。
- `[closed in P6] PO-T4-7` 用 SU-RAS identity reduction 证明无
  buffer/AGV/reservation/BAS 的无环单单位 IMS 子类安全性为 NP-complete；
  对一般紧凑 IMS 只声称至少 NP-hard，不猜测更强完备类。

计算验证：

- 对同时满足偏序与 chain-decomposable 条件的 C2 网格断言无 capacity-mediated 覆盖封闭核；非 chain-decomposable 聚合核和非资源 guard 阻塞登记为 P3 外边界。
- 对 C5 双向/删回流成对模型记录首个死锁参数。
- 对 `BIX0` 小网格逐点核验 P3c；不得把无 drain 的 D-full terminal
  block 计入 P2 capacity-mediated 命中。

## T5 概率层

状态：P4 项目内已证明（严格有限 CTMC）；条件跳过程/Doob-style 主来源
L28 已全文核验，竞争吸收 IMS 适配由 P4 独立证明。

- `[closed in P4] PO-T5-1` 构造有限生成元 `Q`，先做 closed-class 分解，再分块为 `S_T,D,F` 和可能的 `R_c`。
- `[closed in P4] PO-T5-2` committor 方程：`h_D=1`，`h_F=0`，`Q_{S_T,S_T} h_{S_T} = -Q_{S_T,D} 1`；只在吸收假设 `A_abs` 成立或限制到 `S_T` 时使用。
- `[closed in P4] PO-T5-3` 平均吸收时间：`Q_{S_T,S_T} tau_{S_T} = -1`；若 `R_c` 可达且未并入吸收目标，需报告无穷或不定义边界。
- `[closed in P4] PO-T5-4` 敏感性：`Q_{S_T,S_T} partial_theta h_{S_T} = - (partial_theta Q_{S_T,S_T}) h_{S_T} - (partial_theta Q_{S_T,D}) 1`。
- `[closed in P4] PO-T5-5` Doob-`h`：在 `H union D` 上定义，`D` 吸收，跳入 `F` 的条件化率为 0，`q^h_ij = q_ij h_j / h_i` 只在 `i,j in H`。
- `[closed in P4] PO-T5-6` 解释边界：Doob-`h` 是条件路径动力学，不是控制器。

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

计算验证：

- 对小 LTS 输出禁用事件集、保留状态数和不可控闭合检查。
- 对概率控制输出风险预算残差和 Pareto 候选点。
