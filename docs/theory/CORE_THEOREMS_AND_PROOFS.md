# IMS-RAS^CW 核心定理与证明

状态：项目内已证明（严格受限子类）。

本文只给首篇论文可立即承载的受限主链。结论不声称覆盖一般 `IMS-RAS`、经典 `S3PR` 的结构虹吸等价、软预约、随机非 Markov 时间、无限到达、设备故障、抢占或在线插单。

## 0. 受限子类 `IMS-RAS^CW`

`IMS-RAS^CW` 是满足下列结构假设的有限批资源分配系统。上标 `CW` 表示 capacity-aware closed wait，即容量敏感的封闭等待语义。

### CW 假设

- `CW1` 有限性：工件集合 `J`、资源集合 `R`、每个资源容量 `cap(r)`、每个工件路线阶段、硬预约 token 和事件模板均有限。
- `CW2` 闭包归一化：所有主命题只在稳定状态 `S_st` 上陈述。每个非零时间事件触发后执行零时间闭包；闭包终止。若闭包非合流，则闭包后继按集合语义保留。
- `CW3` 容量守恒：对物理资源，`occ_s(r)=sum_j hold_s(j,r) <= cap(r)`；对硬预约 token，`book_s(v)=sum_j res_s(j,v) <= cap(v)`。若硬预约是 future claim，则使用 `occ_s(r)+hard_res_s(r) <= cap(r)`。本文不把软预约纳入完备定理。
- `CW4` 有限 capacity-ready 替代需求：稳定状态 `s` 中每个未完成工件 `j` 的每个当前非容量前置条件已满足的直接进展，都可写成有限个需求替代 `Alt_s(j)={a_1,...,a_m}`。每个替代 `a` 是有限的资源需求向量 `need_s(j,a,r) in N`。替代采用 OR-of-AND 语义：只要存在一个替代的全部需求容量可行，工件就有当前 admissible acquisition/progress 候选。非容量 guard、时钟成熟、同步握手或策略选择尚未就绪的事件不进入 `Alt_s(j)`；每个当前 enabled 的 timed/transport completion 必须作为空需求替代进入 `Alt_s(j)`。
- `CW5` 原子获取：一个 capacity-ready acquisition/progress 事件只有在某个替代 `a` 的所有需求同时满足 `avail_s(r) >= need_s(j,a,r)`（以及对应硬预约可兑现）时才允许发生；不允许半获取。
- `CW6` BAS/AGV 持有保持：加工完成后的 blocked holder、blocked unload、AGV 载货或已承诺运输者，在成功 acquire/unload/handoff/leave 或语义指定 completion-release 事件前，不释放所持资源。
- `CW7` 不可自主释放可判定：对稳定状态中的每个持有量，可以判定它是否存在不依赖新资源获取的释放事件。被证书使用的 blocking capacity 必须由不可自主释放持有或硬预约解释。
- `CW8` 事件分类完备：稳定状态的可发生非零时间事件被分成 timed completion/transport completion、acquire/dispatch/reservation/transport choice、unload/handoff/release、completion/marking 四类；零时间事件只在闭包内发生。
- `CW9` 首篇排除项：无设备故障、无抢占、无动态插单、无无限外生到达、无软预约过售。
- `CW10` 死锁判定排除策略停滞：人为禁用可控事件造成的 policy stall 不叫系统操作死锁；calendar-empty terminal block 必须单独标注为终端阻塞边界，不能混入结构死锁证书。

`event_calendar_empty` 只记录编码状态中当前没有 scheduled timed completion
或 transport completion。它不是 calendar-empty terminal block 的同义词；
后者是对外部/未来事件缺失、调度地平线耗尽或未建模事件源造成停滞的解释
分类。P2 排除的是 calendar-empty terminal block 解释分类，而不是所有
`event_calendar_empty=True` 的状态事实。

### 稳定状态的直接进展

对 `s in S_st` 和未完成工件 `j`，令 `Alt_s(j)` 为其 capacity-ready 直接进展替代集合：事件的非容量 guard、时钟成熟条件、同步握手和策略选择已经满足，剩余问题只是不知道所需容量或硬预约 token 是否可用。若 `j` 已完成，则 `Alt_s(j)=emptyset`。若 `j` 的下一步是当前 enabled 的 timed/transport completion、纯完成标记、无需新容量的释放、无需新容量的交接或无需新容量的卸载，则对应 alternative 的需求向量为空。若 `j` 处于 blocked-after-service 或 blocked-unload，则其替代包含所有当前非容量 guard 已满足的卸载、交接、进入输出缓冲、获得 AGV、兑现硬预约等直接解除阻塞动作。

替代 `a` 在 `s` 中容量可行，当且仅当对所有资源或硬预约 token `r`，

`avail_s(r) >= need_s(j,a,r)`.

其中 `avail_s(r)` 按 `CW3` 的 ontology 计算。

## 1. P1 有限 LTS 与 reachability-net representation

### 定理 P1

给定任意 `IMS-RAS^CW` 模型 `I` 和初始稳定状态 `s0 in S_st`，存在有限闭包归一化 LTS

`T_I=(X,x0,E,->,F,D)`

以及一个 1-safe 有界 Petri 网

`N_I=(P,T,Pre,Post,M0)`

使得可达稳定状态集合 `X` 与可达标识集合 `Reach(N_I,M0)` 一一对应，并且每条 LTS 边与一个 Petri transition 对应。

该定理只是有限 LTS 的 reachability-net 表示定理，不是 `S3PR` 结构等价或虹吸桥接结论。

### 构造

由 `CW1-CW3`，所有工件阶段、阻塞模式、持有量、预约量、闭包选择结果和 pending-free 稳定配置均取自有限集合。令 `X` 为从 `s0` 出发，按 `CW2` 闭包归一化后可达的稳定状态集合。因全状态空间有限，`X` 有限。

对 `x,y in X` 与非零时间事件 `e`，若存在直接触发后状态 `u` 使 `fire(x,e)=u` 且 `y in Cl(u)`，定义 LTS 边 `x --e--> y`。若闭包多值，则对每个 `y in Cl(u)` 建一条边。

构造 Petri 网：

- 对每个 `x in X` 建一个 place `p_x`。
- 对每条 LTS 边 `b=(x,e,y)` 建一个 transition `t_b`。
- `Pre(p_x,t_b)=1`，`Post(t_b,p_y)=1`；其它弧权为 0。
- 初始标识 `M0(p_x)=1` 当且仅当 `x=s0`，其它 place 为 0。

令 `phi(x)` 为在 `p_x` 上有一个 token、其它 place 为 0 的标识。

### 证明

**有限性。** `X` 是有限全状态空间的子集，因此有限。边集合由有限 `X` 和有限事件模板生成，也有限。故 `N_I` 有有限 place 和 transition。

**安全性。** 初始标识只有一个 token。每个 transition 消耗恰好一个状态 place 的 token，并产生恰好一个状态 place 的 token。对 firing 序列长度归纳可知任意可达标识总 token 数为 1，且每个 place token 数为 0 或 1。因此 `N_I` 是 1-safe 且有界。

**正向轨迹保持。** 对 LTS 可达轨迹长度归纳。长度 0 时，`x=s0`，`phi(x)=M0`。假设轨迹 `s0 --...--> x` 对应到可达标识 `phi(x)`。若 LTS 有边 `x --e--> y`，构造中存在 transition `t_b`，其唯一输入 place 为 `p_x`。在 `phi(x)` 下 `p_x` 有 token，因此 `t_b` 使能；发射后 token 移到 `p_y`，得到 `phi(y)`。归纳成立。

**反向轨迹保持。** 对 Petri firing 序列长度归纳。长度 0 时标识为 `M0=phi(s0)`。假设可达标识为 `phi(x)`。任何可发 transition 必须以某个 `p_x` 为输入；构造中这样的 transition 只来自某条 LTS 边 `x --e--> y`。发射后标识为 `phi(y)`，因此对应 LTS 延拓存在。归纳成立。

**双射。** `phi` 从 `X` 到单 token 状态标识显然单射。正向与反向轨迹保持说明每个可达 LTS 状态标识可达，且每个 Petri 可达标识等于某个 `phi(x)`。故 `phi` 是 `X` 与 `Reach(N_I,M0)` 之间的双射。

### Assumption dependence

使用 `CW1-CW3` 得到有限状态和容量守恒，使用 `CW2` 定义稳定 LTS 边。未使用 `S3PR` 结构条件。

### Failure counterexample obligation

若加入无限到达、未界定软预约过售计数或不终止闭包，`X` 可能无限或未定义，应作为 P1 外反例记录。

### Case/enum verifier

枚举 `C0-C5` 的稳定状态，验证每条 LTS 边在 reachability net 中有唯一 transition，且所有可达 Petri 标识都是单 token 状态 place。

## 2. P2 容量介导死锁证书定理

### 定义 2.1 容量缺口 witness

给定稳定状态 `s`、工件 `j` 和替代 `a in Alt_s(j)`。资源 `r` 是替代 `a` 的容量缺口 witness，当且仅当

`need_s(j,a,r) > avail_s(r)`.

若 `a` 为空需求向量，则它没有容量缺口 witness。

### 定义 2.2 封闭阻塞核

在 `s in S_st` 中，`K=(J_K,R_K,W_K,H_K)` 是封闭阻塞核。这里 `W_K` 是 witness 记录集合，元素形如 `(j,a,r)`，表示工件 `j` 的 capacity-ready 替代 `a` 被资源或硬预约 token `r` 的容量缺口阻塞；`H_K` 是 holder 解释记录集合，元素形如 `(j_h,r,q,j,a)`，表示工件 `j_h in J_K` 对 `r` 的数量 `q>0` 的不可自主释放持有或硬预约，参与解释 witness `(j,a,r)` 的缺口。`K` 是封闭阻塞核，当且仅当满足下列可独立核验条件：

1. 非空未完成：`J_K` 非空，且每个 `j in J_K` 未完成。
2. 替代全阻塞：对每个 `j in J_K` 和每个 `a in Alt_s(j)`，存在 `(j,a,r) in W_K`，使 `r in R_K` 且 `r` 是 `a` 的容量缺口 witness。
3. 缺口解释：每个被 `W_K` 记录为 witness 的 `r` 的不足容量，完全由 `H_K` 中核内工件持有或硬预约的不可自主释放量解释。形式化地，对每条 witness `(j,a,r)`，令 `block_K(j,a,r)=sum{q: (j_h,r,q,j,a) in H_K}`；则 `need_s(j,a,r) > cap(r)-block_K(j,a,r)-fixed_out_s(r)`，其中 `fixed_out_s(r)` 是不依赖本事件且不被本证书声明可释放的外部固定占用。覆盖全局死锁时 `fixed_out_s(r)=0`。同一 holder 可作为多条 witness 的解释记录重复出现，但每条不等式只按该 witness 自己的 `block_K(j,a,r)` 审计，不能把重复记录相加后当作真实容量。
4. 释放依赖：`H_K` 中每个 holder 记录 `(j_h,r,q,j,a)` 的持有或硬预约，在不发生 `j_h` 的某个被条件 2 阻塞的 capacity-ready 替代进展前，没有合法 release/unload/handoff 事件可释放相应容量。
5. 至少一个真实阻塞者：存在 `j in J_K`，`Alt_s(j)` 非空且 `j` 处于等待、blocked-after-service、blocked-unload、等待运输或等待硬预约兑现之一。

`K` 覆盖 `s`，当且仅当 `J_K` 等于 `s` 中所有未完成且非 calendar-empty terminal 边界的工件集合。

注意：定义没有使用“无后继”作为条件，因此不是同义反复。

### 定义 2.3 容量介导全局操作死锁

稳定状态 `s` 是 capacity-mediated global operational deadlock，当且仅当：

1. `s` 是一般全局操作死锁；
2. `s` 不是 policy stall、calendar-empty terminal block、永久非资源 guard 阻塞、永久同步缺失阻塞或其它未建模外部边界状态；
3. `s` 中每个未完成、非终端、被覆盖的阻塞工件都有非空 `Alt_s(j)`，并且 `Alt_s(j)` 只含 capacity-ready 直接进展替代；
4. 若任一 timed/transport completion 当前 enabled，则它作为空需求替代进入 `Alt_s(j)`；因此满足本定义的死锁状态中不存在 enabled timed/transport completion。

一般全局操作死锁定义仍保留在 `DEFINITIONS.md`。P2 只刻画容量介导子域，不覆盖永久非资源 guard、外部同步永不满足、人工停机或 calendar-empty 终端边界。

### 定理 P2

在 `IMS-RAS^CW` 中，对稳定状态 `s`：

`s` 是 capacity-mediated global operational deadlock，当且仅当 `s` 存在覆盖的封闭阻塞核。

### 证明

**正向。** 假设 `s` 是 capacity-mediated global operational deadlock。令 `U_s` 为 `s` 中所有未完成且非 terminal 边界的工件。由定义，`U_s` 非空，每个被覆盖阻塞工件都有非空 capacity-ready `Alt_s(j)`，并且至少一个工件处于等待或阻塞。

取 `J_K=U_s`。对任意 `j in J_K` 和任意 `a in Alt_s(j)`，若 `a` 没有容量缺口 witness，则由 `Alt_s(j)` 的 capacity-ready 定义，非容量前置条件已满足；由 `CW5`，该替代全部资源容量可行；由 `CW8`，相应 acquire/progress/release/completion/timed-completion 事件属于完整事件分类；触发后再按 `CW2` 闭包可得到至少一个稳定后继。这与一般全局操作死锁“无允许系统走向不同稳定状态的 admissible successor”矛盾。因此每个替代都有至少一个 witness。把所有 witness 资源收入 `R_K`，把三元组 `(j,a,r)` 收入 `W_K`。

下面证明缺口解释。对 witness `(j,a,r)`，容量不足意味着 `avail_s(r)<need_s(j,a,r)`，即已有占用或硬预约使 `r` 不足。若不足容量中存在一部分由 `J_K` 外部工件持有，并且该外部工件未完成，则它属于 `U_s=J_K`，矛盾；若外部工件已完成，则按完成状态定义不应持有机器、缓冲、AGV 或预约 token；若外部占用来自 calendar-empty terminal block 或未建模环境，则该状态被定理前提排除。故覆盖全局死锁时不足容量由 `J_K` 内持有或硬预约解释。为每条 witness 选择足够的核内不可释放持有或硬预约，形成 `H_K` 记录，使条件 3 的不等式成立。

再证明释放依赖。若某个用于解释 witness 的 holder 可在不依赖被阻塞替代进展的情况下释放相应资源，则该 release/unload/handoff 的非容量前置条件已满足并进入相应 holder 的 `Alt_s(j_h)`，其中若无需新容量则为空需求替代；按 `CW8` 与 `CW2` 将产生稳定后继，矛盾于死锁。因此用于解释缺口的持有均可选为不可自主释放持有，`H_K` 满足条件 4。

非空未完成、替代全阻塞、缺口解释、释放依赖和真实阻塞者均已成立，所以得到覆盖封闭阻塞核。

**反向。** 假设存在覆盖封闭阻塞核 `K`。需证明 `s` 无 admissible successor。按 `CW8` 分类讨论任何可能事件。

1. acquire/dispatch/reservation/transport choice：若该类事件当前非容量 guard 已满足，则它必须对应某个未完成工件 `j` 的某个 capacity-ready 替代 `a`。覆盖性给出 `j in J_K`。条件 2 给出 `a` 至少有一个容量缺口 witness，因此由 `CW5` 原子获取条件，事件不可发生。若非容量 guard 尚未满足，则该事件本来不是当前 admissible successor。
2. unload/handoff/release：该类事件若对未完成工件合法，则按 `Alt_s(j)` 定义是该工件的一个直接进展替代。若该释放不需要新资源，则它是空需求替代，条件 2 不可能成立；若它需要输出缓冲、交接位、AGV 或硬预约兑现，则条件 2 给出容量缺口 witness，事件不可发生。若事件声称可释放证书中解释缺口的容量而不依赖被阻塞替代，则还直接违反条件 4。已完成工件按完成状态定义不持有资源；外部 terminal block 被定理前提排除。
3. timed completion/transport completion：每个当前 enabled 的 timed/transport completion 按 `CW4` 必须作为空需求替代进入 `Alt_s(j)`。空需求替代没有容量缺口 witness，故与条件 2 矛盾。因此覆盖封闭阻塞核存在时，不存在当前 enabled 的 timed/transport completion。尚未时钟成熟或非容量同步未满足的 completion 不属于当前 admissible successor；若完成后仍需 blocked-unload/handoff 才释放，`CW6` 说明完成不释放当前 holder，其后续解除阻塞仍按 capacity-ready 替代全阻塞处理。
4. completion/marking：若某工件可直接完成且释放所有资源，则其替代为空或容量可行，违反条件 2；若全部工件已完成，则违反条件 1 和覆盖性下的非空未完成。
5. 零时间 closure：`s in S_st`，按定义没有启用的零时间事件；非零时间触发后的 closure 已在前四类后继中处理。

因此不存在允许系统走向不同稳定状态的 admissible successor。由覆盖性和条件 5，`s` 非完成且有真实阻塞者；由条件 2 和定义 2.2，所有覆盖阻塞都由 capacity-ready 替代上的容量缺口解释，不是永久非资源 guard、外部同步缺失、policy stall 或 calendar-empty terminal block。故 `s` 是 capacity-mediated global operational deadlock。

### P2a 有限包含极小核存在

若 `s` 存在覆盖封闭阻塞核，则存在一个包含极小的覆盖封闭阻塞核。偏序定义为证书包含：

`K' <= K` 当且仅当 `J_{K'} subset J_K`、`R_{K'} subset R_K`、`W_{K'} subset W_K` 且 `H_{K'} subset H_K`。

因为 `J`、`R`、替代集合和 witness 集合有限，任意非空证书族在有限偏序下都有极小元。该极小性是 inclusion-minimal，不等于最小基数、最小容量增量或唯一证书。

### P2b 单实例一持一求环/SCC 推论

在额外子类 `IMS-RAS^1` 中，若每个关键资源容量为 1，每个阻塞工件恰持有一个关键资源并请求一个关键资源，无替代路线、无硬预约拆分、无残余容量，并且每个 holder 只有在获得所请求资源后才释放当前资源，则：

- 局部量词：资源等待有向图中的每个 terminal SCC `C` 都定义一个局部封闭阻塞核 `K_C`，其工件集恰为 `C` 中资源 holder 对应的工件；反过来，每个 inclusion-minimal 局部封闭阻塞核的等待图恰是一个 terminal SCC。在每个节点出度为 1 的情形，该 terminal SCC 包含一个简单有向环。
- 全局量词：若某个 `K_C` 的工件集覆盖所有未完成工件，则由 P2 得到 capacity-mediated global operational deadlock；它也是一般全局操作死锁的一个子类。

证明：在 `IMS-RAS^1` 中每个阻塞替代只有一个请求资源，容量缺口等价于该资源被某个核内工件持有；于是每个阻塞工件在等待图中有一条指向 holder 的边。若 `C` 是 terminal SCC，则 `C` 内每个请求资源的 holder 仍在 `C` 内，无出边保证所有请求均由 `C` 内持有阻塞，得到局部封闭阻塞核 `K_C`。反过来，设 `K` 是 inclusion-minimal 局部封闭阻塞核。核内等待图每个节点出度为 1 且所有出边留在核内；若该图含多个 terminal SCC 或含不属于 terminal SCC 的前驱节点，则删去前驱节点或取其中一个 terminal SCC 仍保持封闭阻塞，违背 inclusion-minimal。因此 `K` 对应恰一个 terminal SCC。覆盖性把局部结论提升为全局结论。该推论不适用于多容量、多请求、OR-of-AND 替代、AGV/预约拆分或残余容量情形。

### P2c `IMS-SIP^1` wait-snapshot siphon bridge

定义 `IMS-SIP^1` 为 `IMS-RAS^CW` 的局部证书子类：状态 `s` reachable
且 stable；证书以 `shortest_reachable_prefix is not None` 或等价案例 witness
记录可达性；证书核 `K` inclusion-minimal；每个核内资源或硬预约 token
单位容量且 residual 为 0；每个核内工件恰持有一个核内资源 `h(j)` 并
恰有一个当前 request alternative，该 alternative 恰请求一个单位核内资源
`q(j)`；无 OR、无 conjunctive AND 请求、无 soft reservation、无外部
guard、无隐藏 release、无影响释放的非合流闭包。AGV 与硬预约 token 只有
作为普通单位资源时才可纳入。

当前实现只机械检查可达 witness 是否提供、证书极小性、稳定态、单位容量、
一持一求、OR/AND 缺失和 residual marking。closed-world 事件完备、无隐藏
release、guard 已满足和闭包语义仍由证书假设、案例 witness 与人工证明审计
承担；该实现不是一般 plant/S3PR 双模拟检查器。

对给定 `s,K` 构造 state-induced wait-snapshot Petri net：

- place 集 `P_K={free:r | r in R_K}`；
- marking `M_s(free:r)=cap(r)-occ_s(r)`；
- 对每个 `j in J_K` 建 transition `t_j`，满足
  `Pre(t_j)={free:q(j)}` 且 `Post(t_j)={free:h(j)}`。

这里 `t_j` 不是 IMS 事件本体，而是“获得请求资源后才可能释放当前资源”的
等待依赖诊断投影。该网不同于 P1 的 one-place-per-state reachability net。

**定理 P2c。** 在 reachable stable `IMS-SIP^1` 状态中，inclusion-minimal
local closed blocking core 与上述 wait-snapshot net 中的
inclusion-minimal empty siphon 双向对应。

**证明。** 正向取 `Sigma_K={free:r | r in R_K}`。单位容量和 residual 为
0 说明 `Sigma_K` 在 `M_s` 下 empty。任一向 `free:h(j)` 输出的 transition
为 `t_j`，而 `t_j` 的输入 `free:q(j)` 仍在 `Sigma_K`，故
`bullet Sigma_K subseteq Sigma_K bullet`，`Sigma_K` 是 ordinary siphon。
若 `Sigma_K` 有真子 empty siphon，则该真子资源集在一持一求语义下恢复出
真子 local closed blocking core，违背 `K` 的 inclusion minimality。

反向给定 inclusion-minimal empty siphon `Sigma`。令
`R_S={r | free:r in Sigma}`。empty marking 与单位容量给出每个 `r in R_S`
均由唯一核内工件持有。siphon 条件说明任一释放到 `R_S` 的 holder
transition 在释放前请求的资源也在 `R_S`；一持一求和无替代条件于是恢复出
一个 local closed blocking core。若它不是 inclusion-minimal，则其真子
core 对应真子 empty siphon，矛盾。

该结论不适用于 C4/C5 这类 conjunctive request、OR 路由、多容量 residual、
soft reservation、control-only siphon 或任何缺少工件持有-请求证据的
Petri 辅助 place。

### Assumption dependence

P2 使用 `CW2-CW8`、`CW10` 与 capacity-mediated domain 定义。P2b 额外使用单实例、一持一求、无替代和出度为 1 条件。P2c 额外使用 `IMS-SIP^1` 的 reachable stable、单位容量、一持一求、无 OR、无 AND、无隐藏 release 和 ordinary wait-snapshot net 条件；它不使用 P1 reachability-net 构造。

### Failure counterexample obligation

`C1` 必须给出资源图有环但 residual 足够的非死锁状态。`C3` 必须给出多容量下简单环或无汇 WCC 产生错误判据的反例。另需新增非资源边界反例：某工件因永久质量 guard、外部同步永不满足或未建模批准缺失而无 admissible successor，但没有 capacity-ready alternative；该状态可是一种一般操作死锁/终端阻塞，却不是 P2 的 capacity-mediated deadlock。P2c 另需保留 control-only/approval-only siphon 反例：Petri 投影中存在 empty siphon，但没有 IMS 工件持有-请求证据，故不能反向恢复 blocking core。

### Case/enum verifier

枚举小模型所有可达稳定状态，对每个 capacity-mediated deadlock 生成覆盖核；对每个覆盖核用事件分类检查无后继。对无 capacity-ready alternative 的非资源 guard 阻塞，验证其被标为 P2 外边界。对 `IMS-SIP^1` 小模型构造 wait-snapshot net，枚举 minimal empty siphon 并与 local core 比对；对 C4/C5、OR 替代和多容量状态断言 bridge 拒绝。枚举只用于反例搜索和实现审计，不替代上述证明。

## 3. P3 全局获取偏序无死锁定理

### 定义 3.1 全局获取偏序

对关键资源 `R_key subseteq R`，严格偏序 `<` 覆盖所有可能作为 blocked holder 或需求 witness 的机器、缓冲、AGV 和硬预约 token。模型满足 acquisition precedence，当且仅当任意工件在持有资源 `r` 后请求或硬预约资源 `r'` 时，都有 `r < r'`。BAS blocked holder、AGV blocked holder 和硬预约兑现也必须服从同一偏序。

### 定义 3.2 chain-decomposable certificate

封闭阻塞核 `K` 是 chain-decomposable 的，当且仅当对每条 witness `(j,a,r) in W_K`，存在一个 holder 记录 `(j_h,r,q,j,a) in H_K`，其中 witness 资源或硬预约 token `r` 本身就是 `j_h` 当前不可自主释放持有的关键资源，且 `r in R_key`；并且对每个被选中的 holder `j_h`，都存在属于 `j_h` 自己的 blocked capacity-ready 替代及其下一条 witness `r'`。acquisition precedence 要求

`r < r'`.

该条件排除只在“若释放依赖”时才给出下一跳的空洞证明；每个被选中的 holder 都必须提供自己的下一条阻塞责任链。无法把聚合容量缺口分解到具体 holder-dependency chain 的情形，一般多容量、池化硬预约、共享库存或批量容量聚合只作为 P3 之外的候选扩展。

### 引理 P3-L1 证书到资源链选择

若 `K` 是非空 covering closed blocking core 且 chain-decomposable，则从任一 witness 出发，可以构造一条无限资源序列 `r_1,r_2,...`，满足每一步 `r_n < r_{n+1}`。

证明：取任意 witness `(j_0,a_0,r_1) in W_K`。由 chain-decomposable，存在 holder `j_1` 持有或硬预约 witness 资源 `r_1`；同一定义还要求这个被选中的 holder `j_1` 有自己的 blocked capacity-ready 替代和下一 witness，记为 `r_2`。acquisition precedence 给出 `r_1 < r_2`。对 witness `r_2` 重复同一选择。`K` 有限但选择过程可无限重复；每一步都由 chain-decomposable 的 holder-specific next-witness 条件给出下一 witness，得到无限严格上升链。

### 定理 P3

若 `IMS-RAS^CW` 的所有覆盖封闭阻塞核均为 chain-decomposable，且满足全局获取严格偏序，则不存在 P2 所刻画的 capacity-mediated global operational deadlock。

该结论不推出 standard nonblocking、livelock-free、policy-stall-free 或 almost-sure completion。

### 证明

反设存在 capacity-mediated global operational deadlock。由 P2，存在覆盖封闭阻塞核 `K`。按本定理前提，`K` 是 chain-decomposable。由 P3-L1，从任一 witness 出发得到无限严格上升资源链

`r_1 < r_2 < r_3 < ...`.

每一步都在有限的 `R_key` 内。由于 `R_key` 有限，资源序列必有重复：存在 `m<n` 使 `r_m=r_n`。于是严格偏序传递性给出

`r_m < r_{m+1} < ... < r_n = r_m`,

推出 `r_m < r_m`，违反严格偏序的反自反性。矛盾。因此不存在覆盖封闭阻塞核；由 P2，系统无 capacity-mediated global operational deadlock。

### Assumption dependence

使用窄化后的 P2、`CW1` 的有限资源、`CW6-CW7` 的不可释放持有语义和 chain-decomposable 责任链假设。偏序必须覆盖机器、缓冲、AGV 与硬预约 token。没有责任链分解的聚合容量缺口不属于 P3 已证范围；永久非资源 guard 阻塞也不属于 P3 的死锁排除结论。

### Failure counterexample obligation

若只对机器投影建 DAG 而遗漏 AGV、缓冲或预约逆序，P3 不适用；若多容量池化或硬预约聚合缺口无法分配到 holder-dependency chain，P3 也不适用。`C3-C5` 必须保留这些反例边界。

### Case/enum verifier

对满足偏序的小模型网格枚举覆盖核，并额外检查每个候选核是否 chain-decomposable；若发现 chain-decomposable 覆盖核，输出违反偏序的最短资源链；若发现非 chain-decomposable 聚合核或非资源 guard 终端阻塞，登记为 P3 外边界案例。

### P3c 双向启动饱和候选态 `BIX0`

定义 `BIX0(c_M,c_G,c_D,n_A,n_B)`，其中
`c_M,c_G,c_D >= 1`。它构造一个无成功 transfer 前缀的候选饱和状态：

- 至多 `c_M` 个 A 类工件可启动并各持有一个 `M`；服务后 BAS 保持
  `M`，其唯一 capacity-ready 进展原子请求一个 `D` 槽和一个 `G`；
- 至多 `c_G` 个 B 类工件可启动并各持有一个 `G`；blocked-unload
  保持 `G`，其唯一 capacity-ready 进展原子请求一个 `M`；
- 候选状态不含任何成功 A/B transfer，因此 `D` 从初始空保持为空；
- 没有替代路线、自主释放、软预约、额外 guard 或 policy/calendar
  停止。

**命题 P3c。** `BIX0` 候选状态存在 closed blocking kernel，当且仅当

`n_A >= c_M` 且 `n_B >= c_G`。

`BIX0` 是候选态前置结果，不再作为可达性定理使用。它只机检在一个
已构造的空前缀饱和状态上，闭核阈值是否等于 `M-G` 双向容量阈值。

### P3d 可达饱和族 `BIX1-SAT`

定义 `BIX1-SAT(c_M,c_G,c_D,c_V,n_A,n_B)`，其中
`c_M,c_G,c_D,c_V >= 1`。模型从空持有状态出发，所有 A 工件初始请求
`M`，所有 B 工件初始请求 `G`，且事件注册表显式含有下列完成事件；
`event_calendar_empty=True` 只表示没有外部日历，不表示完成事件缺失。

- A 链：`start` 获取 `M` 并清除启动请求；`service_complete` 为
  uncontrollable，仍持有 `M`，并请求 `{G,D,V}`；`transfer` 为
  controllable，原子获取 `G,D,V`、释放 `M` 并清除请求；`drain` 为
  uncontrollable，释放 `G,D,V` 并完成。
- B 链：`start` 获取 `G` 并清除启动请求；`transport_complete` 为
  uncontrollable，仍持有 `G`，并请求 `M`；`unload` 为 controllable，
  原子获取 `M`、释放 `G` 并清除请求；`complete` 为 uncontrollable，
  释放 `M` 并完成。
- `V` 是 hard reservation token。所有转移都是显式 `TransitionSpec`；
  零时闭包在该族中平凡。

**定理 P3d。** `BIX1-SAT` 中 capacity-mediated global operational
deadlock 可达，当且仅当

`n_A >= c_M` 且 `n_B >= c_G`。

**充分性。** 先对恰好 `c_M` 个 A 工件依次执行 `start` 与
`service_complete`，使它们持满 `M` 并请求 `{G,D,V}`；再对恰好
`c_G` 个 B 工件依次执行 `start` 与 `transport_complete`，使它们
持满 `G` 并请求 `M`。该前缀没有成功 transfer，因此 residual
`M=0,G=0,D=c_D,V=c_V`。每个 A 的 AND 请求因 `G` 缺口而不可发生；
每个 B 因 `M` 缺口而不可发生；任何未启动 A/B 也分别因 `M/G` 满而
不能启动。所有 completion 事件已显式建模，但在该状态没有工件处于
可触发 completion 的 source mode。全部未完成活动由同一 `M-G` 封闭核
覆盖，故由 P2 得到 capacity-mediated global deadlock。

**必要性。** 先观察任一全局死锁都不能含 `a_transferred` 工件，因为
其 `drain` uncontrollable 且 enabled；也不能含 `b_on_M` 工件，因为其
`complete` uncontrollable 且 enabled。因此在全局死锁中，`M` 只可能由
尚未 transfer 的 A 持有，`G` 只可能由尚未 unload 的 B 持有，并且
`D,V` 无占用。

若 `n_A<c_M`，则 `M` 不可能被持满，故 residual `M>0`。如果存在
`b_blocked_unload` 工件，其 `unload` enabled；否则任一未完成 B 必处于
`b_idle` 或 `b_in_transport`，而前者在 `G` 有余量时可 `start`，后者的
`transport_complete` enabled。若 `G` 无余量，则必有 B 持有 G；在没有
`b_blocked_unload` 的假设下，该 holder 处于 `b_in_transport`，仍有
enabled completion。若没有未完成 B，则任一未完成 A 处于 `a_idle`、
`a_in_service` 或 `a_blocked_complete`；分别有 `start`、
`service_complete`，或因 `D,V` 空闲且不存在 B 占满 G 而有 `transfer`。
所以不存在全局死锁。

对称地，若 `n_B<c_G`，则在上述死锁必要状态形态中 residual `G>0` 且
`D,V` 全空。任一 `a_blocked_complete` 的 `{G,D,V}` transfer enabled；
若没有这种工件，则任一未完成 A 的 `start` 或 `service_complete`
enabled。若没有未完成 A，任一未完成 B 的 `start`、
`transport_complete`、`unload` 或 `complete` 链上至少一个事件 enabled；
其中若 M 被 A 持满，则这些 A 必处于 `a_in_service` 或
`a_blocked_complete`，前者 completion enabled，后者 transfer enabled。
故任何全局死锁都必须同时满足
`n_A>=c_M,n_B>=c_G`。

**为什么 `c_D,c_V` 消失。** P3d 的见证前缀没有成功 transfer，
因此没有工件持有 `D` 或 `V`；A 的 AND 请求已由 `G` 缺口阻塞。
在 `c_D,c_V>=1` 的本族内，`D,V` 不进入阈值。这不是一般有限缓冲或
预约容量无关性结论。

**边界反例。** 若允许成功 A transfer 后长期占用 `D`，则
`c_M=c_G=c_D=1,n_A=2,n_B=0` 已击穿上述一般化：A1 进入并占满 D，
A2 随后持 M 等待 D。若 D 中实体没有已建模的 capacity-ready drain，
该状态属于 buffer-full/calendar/外部-drain 终端边界，而不是 P2 的
capacity-mediated 全局死锁；若 drain 已建模，则阈值取决于 drain
资源与释放语义。该反例分类为 `outside_bix1_sat`，不是 P3d 的
theorem mismatch。

**DAG repair 边界。** 删除 B 对 M 的回流请求，并给 B 一个 enabled
release/unload，会破坏上述 `M-G` 封闭核。它只消除这个双向饱和机制；
若 D 可持续积累且无 drain，仍不能据此推出一般 deadlock-free 或
nonblocking。

## 4. P4 有限竞争吸收 CTMC 定理

### 定理 P4

给定有限 `IMS-CTMC`，设 `D` 为死锁吸收类、`F` 为完成吸收类。若 `A_abs` 成立，或已把分析限制到会以概率 1 命中 `D union F` 的暂态集合 `S_T`，则：

1. 死锁 committor `h_i=P_i(tau_D<tau_F)` 在 `S_T` 上唯一满足
   `Q_{S_T,S_T} h = - Q_{S_T,D} 1`，边界 `h_D=1,h_F=0`。
2. 平均吸收时间 `tau_i=E_i[tau_{D union F}]` 在 `S_T` 上唯一满足
   `Q_{S_T,S_T} tau = -1`。
3. 若速率生成元 `Q(theta)` 可微且 `S_T,D,F` 分区在参数邻域内不变，则 `h(theta)` 可微，并满足
   `Q_{S_T,S_T} partial_theta h = - (partial_theta Q_{S_T,S_T})h - (partial_theta Q_{S_T,D})1`。
4. 令 `H={i in S_T: h_i>0}`。在状态域 `H union D` 上，定义 `D` 为吸收边界；对 `i in H`、`j in H` 令 `q^h_ij=q_ij h_j/h_i`，对 `d in D` 令 `q^h_id=q_id/h_i`，对 `f in F` 的条件化跳转率为 0，对角元 `q^h_ii=-sum_{k in (H union D), k != i} q^h_ik`，且 `q^h_dd=0`。这定义了条件于先达 `D` 的 Doob-`h` 生成元；其行和为 0，且只在 `h_i>0` 的域上解释。

### 证明

**可逆性。** 在有限 CTMC 中，`S_T` 内状态以概率 1 离开并命中 `D union F`。因此 `Q_{S_T,S_T}` 是暂态子生成元，存在非负 fundamental matrix

`N = int_0^infty exp(Q_{S_T,S_T} t) dt`,

且积分有限。于是 `Q_{S_T,S_T} N = N Q_{S_T,S_T} = -I`，所以 `Q_{S_T,S_T}` 可逆。

**committor 方程。** 对 `i in S_T`，用首跳分解。设离开率 `lambda_i=-q_ii>0`。下一跳到 `j` 的概率为 `q_ij/lambda_i`。边界贡献中跳入 `D` 的概率为 `sum_{d in D} q_id/lambda_i`，跳入 `F` 的贡献为 0。因此

`h_i = sum_{j in S_T} (q_ij/lambda_i) h_j + sum_{d in D} q_id/lambda_i`.

两边乘以 `lambda_i` 并移项，得到

`sum_{j in S_T} q_ij h_j + sum_{d in D} q_id = 0`,

即 `Q_{S_T,S_T}h=-Q_{S_T,D}1`。可逆性给出唯一性。

**平均吸收时间方程。** 对 `i in S_T` 首跳分解：

`tau_i = 1/lambda_i + sum_{j in S_T}(q_ij/lambda_i) tau_j`.

乘以 `lambda_i` 并移项得到

`sum_{j in S_T} q_ij tau_j = -1`。

可逆性给出唯一解。

**敏感性。** 方程写作 `A(theta)h(theta)=b(theta)`，其中 `A=Q_{S_T,S_T}`，`b=-Q_{S_T,D}1`。在分区固定且速率可微的邻域内，`A(theta)` 可微且持续可逆。有限维矩阵求逆在可逆集上可微，故 `h=A^{-1}b` 可微。微分得

`(partial_theta A)h + A(partial_theta h)=partial_theta b`.

代入 `partial_theta b=-(partial_theta Q_{S_T,D})1` 即得命题中的敏感性方程。

**Doob-h 生成元。** 对 `i in H` 与 `j in H`，`q^h_ij >=0`；对 `d in D`，`q^h_id=q_id/h_i >=0`，因为 `h_d=1`。对 `F` 的跳转率设为 0，因为条件事件是先达 `D`，一旦跳入 `F` 条件概率为 0。对角元定义为 `H union D` 内非对角行和的负值，故 `i in H` 的行和为 0；`D` 行全为 0，故吸收且行和也为 0。若原链跳向 `S_T \ H`，该目标的 `h=0`，条件化率为 0，不进入条件链状态域。标准 h-transform 的有限维首跳 Radon-Nikodym 比率给出对任意到达 `D` 前的有限路径 `i_0,...,i_n`，路径率被乘以 `h_{i_n}/h_{i_0}`；到 `D` 时以吸收边界结束。因此它解释的是条件于先达死锁的路径动力学。该构造没有选择或禁用系统事件，因此不是控制器。

### Assumption dependence

使用有限 CTMC、指数或 PH 展开、`A_abs` 或已完成 closed-class 分解。
Metzner 等 ergodic TPT 只作背景边界；Corstanje 和 van der Meulen
(2025) 的 Section 3.1、Eq. 3.1、Eq. 3.3 与 Appendix D 是条件跳过程和
Doob-style 生成元的全文锚点。竞争吸收边界值、平均吸收时间和敏感性仍按
本项目有限 CTMC 设定独立推导，不能把化学反应网络结果直接称为 IMS
吸收定理。

### Failure counterexample obligation

若 `R_c` 可达且未并入边界，`Q_{S_T,S_T}` 的选择不完备，平均吸收时间可能无穷。若参数改变使状态分区变化，敏感性方程只在分段固定区域内成立。

### Case/enum verifier

对 `C0/C5` 精确求解线性系统，报告残差、`h` 边界值、`tau` 非负性、Doob-h 行和和 DES 置信区间覆盖。

## 5. P5 有限全观测确定性状态监督器基准

### 定义 5.1 安全集、不可控闭包和 marked coaccessibility

给定有限 LTS `T=(X,x0,E,->,F,D)`，事件划分为可控 `E_c` 与不可控 `E_u`。令基础安全域 `X0 = X \ D`，或项目指定的更保守安全域。对任意 `Y subseteq X`：

- `UPre(Y)={x in Y: every uncontrollable successor of x lies in Y}`。
- `CoAcc(Y)={x in Y: there exists a finite path from x to F using only states in Y}`。若同一事件标签有多个 nondeterministic successors，则一个可控事件在 supervisor 下被允许的条件是它的所有后继都留在当前候选域。

定义下降算子

`G(Y)=CoAcc(UPre(Y))`.

### 定理 P5

从 `Y_0=X0` 迭代 `Y_{k+1}=G(Y_k)`，有限步终止于最大不变 nonblocking 安全域 `Y*`。若 `x0 in Y*`，基于 `Y*` 的 state-based supervisor 允许且仅允许所有后继留在 `Y*` 的可控事件，并必须保留所有不可控后继；该 supervisor sound，且在 full-observation deterministic/state-based 域内最大许可。若 `x0 notin Y*`，则不存在满足相同安全、不可控闭合与 marked coaccessibility 要求的 full-observation state-based supervisor 可从该初始状态实施。

### 证明

**单调下降与终止。** `UPre(Y) subseteq Y`，`CoAcc(UPre(Y)) subseteq UPre(Y)`，故 `Y_{k+1} subseteq Y_k`。`X` 有限，因此序列有限步稳定，记不动点为 `Y*`。

**安全性。** 初始若 `x0 in Y*`，supervisor 只允许可控后继留在 `Y*`；不可控闭包由 `UPre` 保证所有不可控后继留在 `Y*`。对路径长度归纳，闭环可达状态始终在 `Y* subseteq X0` 内，因此不达 `D`。

**nonblocking/coaccessibility。** 因 `Y*=G(Y*)=CoAcc(UPre(Y*))`，每个 `x in Y*` 都有一条完全留在 `Y*` 的有限路径到 `F`。故闭环状态域是 marked coaccessible 的。该结论是存在延拓的 standard nonblocking，不保证所有随机或不公平路径必然完成。

**最大性。** 设 `Z subseteq X0` 是任一 full-observation state-based 域，满足不可控闭合并且每个状态在 `Z` 内 coaccessible。则 `Z subseteq UPre(Z)` 且 `Z subseteq CoAcc(UPre(Z))=G(Z)`。由 `G` 关于包含关系单调，且 `Z subseteq Y_0`，归纳得 `Z subseteq Y_k` 对所有 `k` 成立，故 `Z subseteq Y*`。因此 `Y*` 是最大安全且 nonblocking 的状态域；允许所有保持在 `Y*` 内的可控事件给出该域上的最大许可 state-based supervisor。

**初始状态不可行性。** 若 `x0 notin Y*`，且存在某个满足安全、不可控闭合与 coaccessibility 的可实施状态域 `Z` 包含 `x0`，则由最大性 `Z subseteq Y*`，推出 `x0 in Y*`，矛盾。因此此类 supervisor 不存在；算法应报告 initial-state infeasible，而不是输出空策略并称为死锁控制成功。

### Assumption dependence

使用有限 LTS、全状态观测、事件可控/不可控划分和状态域监督。若采用语言层部分观测或无穷 DES，需要另行引用 Ramadge-Wonham 框架，不能由 P5 直接推出。

### Failure counterexample obligation

如果 supervisor 禁用所有可控事件造成 policy stall，则只说明控制策略过保守，不说明系统结构无死锁。若 nondeterministic event 的某些后继离开安全域，则该事件不能按存在后继量词允许。

### Case/enum verifier

对 `C0-C5` 输出 `Y*`、删除状态、禁用事件、不可控闭合检查和每个保留状态到完成的见证路径。

## 6. P6 表示敏感的复杂性边界

### 定义 6.1 `IMS-SU^A` 与判定问题

`IMS-SU^A` 是 `IMS-RAS^CW` 的如下受限子类：

- 无缓冲、AGV、预约、BAS、时钟和非平凡零时间闭包；
- 每个工件沿有限无环路线依次请求一个单位资源；
- 获得下一资源与释放当前资源是一个原子进展事件；
- 最后一个阶段完成时释放最后资源；
- 输入显式给出资源容量、每条路线和当前阶段/持有状态。

`IMS-SU-SAFE` 问：从给定合法状态出发，是否存在一个有限事件序列使全部工件完成。

### 定理 P6

1. `IMS-SU-SAFE` 是 NP-complete。
2. 若闭包归一化有限 LTS `T=(X,x0,E,->,F,D)` 已显式给出，则 P5 的
   最大不变 nonblocking 安全域 `Y*` 可在
   `O(|X|(|X|+|->|))` 时间和 `O(|X|+|->|)` 空间内计算。
3. 对紧凑 IMS 输入，判定 `x0` 是否属于某个满足 P5 条件的
   full-observation state-based supervisor 的可实施域至少 NP-hard；完整
   supervisor 的显式输出还可能因可达 LTS 指数增长而具有指数大小。

上述结论不给一般紧凑 `IMS-RAS^CW` 判定问题贴上未经证明的
PSPACE/EXPTIME 标签。它把“模型输入大小”和“已展开状态图大小”分开：
显式图上的精确 fixed point 是多项式的，而从紧凑制造模型生成该图及判定
初始可行性已经包含 NP-hard 子类。

### 证明

**NP membership。** 在 `IMS-SU^A` 中路线无环，每个事件使某个工件阶段
严格前进一次。任一完成见证的长度不超过所有工件剩余路线阶段数之和。
给定事件序列，可逐步检查请求容量、原子 acquire-release、容量守恒和最终
完成，所需时间关于显式输入与见证长度为多项式。因此
`IMS-SU-SAFE in NP`。

**NP hardness。** Lawley and Reveliotis (2001) 的 Theorem 1 证明
`SU-SAFE` 为 NP-complete。对任意 `SU-SAFE` 实例作如下恒等结构映射：
每个 SU-RAS 资源及容量映射为同容量 IMS 资源，每个 process route 映射为
一条 `IMS-SU^A` 工件路线，每次单单位 allocation 及同时释放前一资源映射为
原子 IMS 进展事件，终止 allocation 映射为完成并释放。该构造线性于实例
大小，不引入缓冲、AGV、预约、BAS 或时间事件。由事件序列逐步对应，
SU-RAS 状态存在安全完成序列，当且仅当映射后的 IMS 状态存在全部工件完成
序列。因此 `SU-SAFE <=p IMS-SU-SAFE`，得到 NP-hard；结合 membership 得
NP-complete。

**显式 LTS 上界。** P5 的下降迭代每轮至少删除一个状态或达到不动点，
故至多 `|X|` 轮。每轮用一次反向图搜索计算 `CoAcc`，并扫描边集合检查
`UPre`，时间 `O(|X|+|->|)`、空间 `O(|X|+|->|)`。相乘得所述保守上界。

**紧凑输入下的 supervisor 初始可行性下界。** 对上述 `IMS-SU^A`
映射，把所有进展事件声明为可控、完成状态作为 `F`、无额外坏状态。此时
P5 fixed point 包含 `x0` 当且仅当存在一条完成延拓，即当且仅当
`IMS-SU-SAFE` 为真。因此紧凑输入上的初始可行性判定至少 NP-hard。可达
状态是各工件阶段、持有和容量配置的组合，其显式数量可相对紧凑输入指数
增长，所以输出完整状态 supervisor 本身可能需要指数空间；这是一项输出
大小边界，不是更强复杂性完备性的替代证明。

### Assumption dependence

第一部分使用 `IMS-SU^A` 的有限无环路线和原子单单位 acquire-release
语义，并只迁移 Lawley-Reveliotis Theorem 1 的 `SU-SAFE` 复杂性。第二部分
使用显式有限 LTS。第三部分只给一般紧凑 IMS 的 NP-hard 下界。

### Failure counterexample obligation

若允许循环路线，完成见证不再由剩余阶段数直接多项式界定，不能沿用
NP membership 证明。若输入本身已经是显式 LTS，则不能把紧凑模型的
NP-hard 下界误写成图 fixed point 的复杂性。

### Case/enum verifier

对小型 `IMS-SU^A` 实例同时运行安全序列枚举和 P5 fixed point，检查
`x0 in Y*` 与存在完成序列一致；记录紧凑配置数与展开状态数，但程序枚举
不替代上述 reduction。

## 7. 主链状态边界

已闭合的项目内主链是：

`IMS-RAS^CW` 语义有限化 -> LTS/reachability-net 表示 -> covering closed blocking core 与 capacity-mediated global operational deadlock 等价 -> chain-decomposable strict-precedence 排除 capacity-mediated deadlock -> finite CTMC risk equations -> finite full-observation supervisor benchmark -> 显式图多项式 fixed point / 紧凑输入 NP-hard 的表示敏感复杂性边界。

仍未闭合的命题：

- 一般 IMS 到 structured Petri/S3PR 的同构或双模拟。
- 最小封闭阻塞核与最小致死虹吸的双向最小性对应。
- 双向制造岛容量/WIP/AGV 精确阈值。
- 一般紧凑 `IMS-RAS^CW` 安全与 supervisor 初始可行性问题在 NP-hard
  下界之上的精确复杂性分类。
- risk-budget 控制的递归可行性或 Pareto 最优性。
- 软预约、非指数时间、故障、抢占、动态插单与无限到达扩展。
