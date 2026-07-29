# 六级定理梯

所有条目是论文候选主链。状态字段用于区分定义、文献基线、拟证明、计算验证与反例。

## T1 语义等价定理

状态：项目内已证明（严格受限子类）；structured Petri/S3PR 桥仍拟证明。

### Statement

给定 `IMS-RAS^CW`，其闭包归一化可达稳定语义可构造为有限 LTS；进一步可用每个可达稳定状态一个 place、每条 LTS 边一个 transition 的 reachability net 得到 1-safe 有界 Petri 网，并与 LTS 可达状态双射、step correspondence 成立。该结论不是 S3PR 结构创新；附加 Petri 可投影条件下的资源结构桥仍为拟证明。

### Assumptions

- `J`、路线、资源容量和预约 token 均有限。
- 加工完成、运输完成与资源释放分离。
- 所有可观察转换在 `S_st` 上陈述。
- 若使用确定闭包 `kappa`，必须有闭包终止+合流或固定优先级/排序。
- Petri 桥只覆盖离散、守恒、无软过售或软过售已显式扩展成有限状态的子类。

### Proof obligations

- 证明状态空间有限。
- 证明每个 IMS 事件映射到 LTS 转换。
- 证明 BAS blocked-unload 的资源占有不被事件映射丢失。
- Petri 子类需证明 `phi(fire(s,e))` 与 Petri firing 兼容。
- 多值闭包情形需证明集合后继语义，而不是强行构造函数。

### Failure modes

- closure 不合流导致同一触发事件有多个稳定后继。
- 软预约过售需要额外状态，无法直接落入经典 S3PR。
- 优先级闭包若未进入语义，等价证明不成立。

### Evidence status

P1 项目内已证明（严格受限子类）。枚举只检查小模型事件守恒与状态映射。Structured Petri/S3PR 映射仍拟证明。

### Case mapping

`C0`、`C2` 用于最小 LTS/Petri 映射；`C4` 用于检查 AGV 投影是否丢失死锁。

### Enumeration assertion

对每个小模型，枚举所有 `S_st`，检查所有事件后继均满足容量守恒，且 Petri 子类中 `phi` 后继集合与 LTS 后继集合一致。

## T2 容量介导死锁证书定理

状态：capacity-mediated deadlock 已证明（严格受限子类）；一般操作死锁/软预约/非资源 guard 仍拟证明或边界。

### Statement

在 `IMS-RAS^CW` 闭包归一化稳定状态上，capacity-mediated global operational deadlock 当且仅当存在覆盖所有未完成活动的多容量封闭阻塞核。该死锁子域要求 `Alt_s(j)` 只含非容量 guard/时钟/同步已经满足的 capacity-ready 替代，且每个被覆盖未完成非终端阻塞工件有非空 `Alt_s(j)`；每个当前 enabled timed/transport completion 必须作为空需求替代进入 `Alt_s(j)`，因此不能出现在容量介导死锁中。对单实例、一持一求、无替代路线的受限子类，可推出 terminal SCC/简单有向环局部判据；只有对应 SCC 核覆盖所有未完成工件时才推出容量介导全局操作死锁。

### Assumptions

- 证书包含持有量、需求量、残余容量、预约 token、capacity-ready 可选后继、witness 集合 `W_K` 和 holder 解释集合 `H_K`。
- 所有未完成工件的可继续后继都被证书覆盖。
- 不允许把 Palmer 队列网络 `knot` 直接替换成一般 IMS 证明。

### Proof obligations

- 死锁到封闭核：从无可发生事件构造最小阻塞核。
- 封闭核到死锁：证明每个未完成活动均被封闭条件阻断。
- 多容量资源下证明残余容量不足，而不仅是存在等待边。
- 替代路线下证明所有替代均被阻断。

### Failure modes

- 资源图有环但残余容量足够。
- 永久非资源 guard 或外部同步永不满足造成停滞，但没有 capacity-ready alternative；这是 P2 外边界，不得用封闭容量核解释。
- WCC 无汇快捷等价在 Palmer 2/3 服务器反例中失败。
- 局部封闭核未覆盖所有未完成工件，只能推出局部死锁。

### Evidence status

P2/P2a/P2b 对 capacity-mediated 子域项目内已证明 + 反例边界。Palmer knot 是有限队列网络基线；无汇 WCC 快捷只在单节点、两节点每节点不超过 2 服务器、或全有限单服务器条件下使用。

### Case mapping

`C1` 击穿“有环即死锁”；`C3` 比较简单环、无汇 WCC 与多容量封闭核。

### Enumeration assertion

枚举小模型可达稳定状态，输出最小 `DeadlockCertificate`，并检查每个证书边都有具体工件-资源证据和最短可达前缀。

## T3 虹吸桥接定理

状态：`IMS-SIP^1` state-induced wait-snapshot diagnostic net 已证明；
一般 IMS plant/S3PR 双向桥仍开放。

### Statement

在 reachable stable `IMS-SIP^1` 状态中，inclusion-minimal local
closed blocking core 与 state-induced wait-snapshot diagnostic net 中
的 inclusion-minimal empty siphon 双向对应。该诊断网只含
`free:r` places 和“先取得请求资源才释放当前持有资源”的 transitions；
它不是 P1 reachability net，也不是 IMS plant 或经典 S3PR 网。一般 IMS
只保留机器可读拒绝与反例边界。

### Assumptions

- 状态已完成零时间闭包且有可达 witness，core 为 inclusion-minimal。
- 核资源单位容量、residual 为 0。
- 每个核工件恰持有一个单位核资源，并恰有一个单资源单位请求。
- 没有 OR、AND、soft reservation、外部 guard、隐藏 release 或非合流
  闭包释放路径。
- AGV/硬预约只有作为普通单位资源时才可进入该诊断桥。

### Proof obligations

- `[closed in P2c]` 从 minimal core 构造 minimal empty siphon。
- `[closed in P2c]` 从 minimal empty siphon 恢复一持一求的 minimal
  local core。
- `[closed in P2c]` 证明最小性在 functional one-hold/one-request 映射
  下保持。
- `[open]` 对 plant-level structured Petri/S3PR 给出独立语义等价或
  明确更窄子类；不得由诊断快照自动推出。

### Failure modes

- C4/C5 conjunctive request、OR 替代或多容量 residual 使诊断桥拒绝。
- control-only/approval-only empty siphon 没有工件持有-请求证据。
- AGV/预约 place 被投影掉后 false negative。
- 软预约或隐藏 release 使 Petri 守恒/等待解释失真。

### Evidence status

P2c 项目内证明、`ims_deadlock.petri` 最小 siphon 枚举和 C0/C5/OR/
multi-capacity/control-only 回归。一般 plant/S3PR bridge 仍开放。

### Case mapping

`C0` 验证正例；`C4` 验证投影漏项；专门反例验证双向映射失败。

### Enumeration assertion

对 `IMS-SIP^1` 计算 minimal empty siphon，与 IMS minimal core 做双向
包含检查；一般类只报告不可映射原因，不伪造 siphon。

## T4 结构充分条件与阈值族

状态：chain-decomposable strict-precedence 子类、`BIX0` 候选态阈值、
`BIX1-SAT` 可达启动/完成饱和阈值和表示敏感复杂性下界已证明；一般
多容量/聚合预约、persistent-buffer 制造岛阈值和一般紧凑 IMS 的精确
复杂性类别仍拟证明。

### Statement

若所有必须获取且不可抢占保持的机器、缓冲、AGV 和预约 token 存在全局严格获取偏序，并且每个覆盖封闭阻塞核都能把容量缺口分解为 chain-decomposable holder-dependency chain，则在 A8 与窄化 T2 证书定理适用条件下，不存在覆盖所有未完成 non-terminal activities 的封闭阻塞核，因此不存在 capacity-mediated IMS operational deadlock。

`BIX0` 的 P3c 只给出已构造无成功-transfer 候选态含 closed kernel 的
阈值，不作可达性主张。对从空持有状态出发并显式含 start、completion、
transfer、unload 和 drain 的 `BIX1-SAT`，P3d 给出精确可达性阈值：
capacity-mediated global deadlock reachable iff
`n_A>=c_M` 且 `n_B>=c_G`。该式只说明存在死锁前缀，不说明死锁必然
发生；`c_D,c_V` 只因见证前缀没有成功 transfer 且完成 drain 已显式建模
而消失。persistent-D、替代路线、外部 drain 或额外优先级的更一般族
仍开放。

复杂性边界：无 buffer/AGV/reservation/BAS、有限无环路线、原子单单位
acquire-release 的 `IMS-SU^A` 子类，其 `IMS-SU-SAFE` 由 SU-SAFE
identity reduction 得到 NP-complete。对显式给出的闭包归一化 LTS，P5
fixed point 可在 `O(|X|(|X|+|->|))` 时间内精确计算；对紧凑一般 IMS，
supervisor 初始可行性至少 NP-hard，完整状态策略可能具有指数输出大小。
未证明一般问题为 PSPACE/EXPTIME-complete。

### Assumptions

- 偏序覆盖 machine、buffer、AGV、reservation。
- 工件不得持有高序资源再请求低序资源。
- BAS 阻塞持有也服从同一偏序。
- 释放规则不制造隐式逆序请求。
- 证书必须是 chain-decomposable；池化硬预约、共享库存或聚合容量缺口若无法归责到具体 holder chain，则不属于 T4 已证范围。
- 该结论只排除可由窄化 T2 覆盖证书刻画的 capacity-mediated operational deadlock，不自动保证 general operational-deadlock-free、standard nonblocking、livelock-free 或 almost-sure completion。

### Proof obligations

- 反证：若存在覆盖所有未完成 non-terminal activities 的 chain-decomposable 封闭核，则由证书到资源链选择引理沿等待证据导出无限严格上升资源依赖；有限严格偏序中不可能存在这种链。
- 处理多资源需求：至少一个阻塞需求必须导出违反偏序的等待链。
- 调用窄化 T2：无 covering closed blocking kernel 推出无 capacity-mediated operational deadlock；不得跳过 T2 的覆盖、capacity-ready 和证书条件。
- `[closed in P3d]` 对 `BIX1-SAT` 从空持有状态构造充分性前缀，并利用
  enabled drain/completion 排除阈值以下的全局死锁。
- `BIX1-SAT` 之外、含 persistent-D、替代路线、外部 drain 或优先级的
  双向岛族仍需推导或证伪容量/WIP/AGV 分段阈值，不得预置公式。

### Failure modes

- 只有机器投影为 DAG，但 AGV 或缓冲预约存在逆序。
- 拓扑 DAG 不含容量持有顺序，不能推出 deadlock-free。
- 聚合容量或硬预约缺口不能分解到具体 holder-dependency chain 时，不能推出 deadlock-free。
- 永久非资源 guard、外部同步缺失或 policy/calendar 边界不由容量偏序排除。
- 满足偏序条件仍可能存在 livelock、policy-induced stall、calendar-empty terminal block 或 nonblocking 失败。

### Evidence status

P3 chain-decomposable strict-precedence 子类无 capacity-mediated 操作
死锁已项目内证明；P3c 闭合 `BIX0` 候选态阈值；P3d 闭合
`BIX1-SAT` 从空状态可达的 WIP/机器/AGV 双向饱和阈值；
P6 给出 `IMS-SU^A` NP-complete、显式 LTS 多项式 fixed point 和紧凑
输入至少 NP-hard 的边界。一般操作死锁、永久非资源 guard、多容量/
聚合预约、一般紧凑 IMS 的精确复杂性分类和 persistent-buffer 一般
制造岛容量/WIP/AGV 阈值仍是 conjecture family 或边界。

### Case mapping

`C2` 对应偏序无环正例；`C5` 对比 M-D 双向回流与删除回流 DAG 版本。

### Enumeration assertion

穷举小参数网格，先检查偏序条件与封闭核 chain-decomposable 条件；在二者同时满足时断言无覆盖封闭核。对双向岛族记录第一个可达死锁参数点、最小证书以及是否属于 P3 外聚合边界。

## T5 概率桥接定理

状态：项目内已证明（严格受限有限 CTMC）；条件跳过程/Doob-style
全文锚点已固定，竞争吸收 IMS 适配仍以本项目证明为准。

### Statement

对有限 `IMS-CTMC`，把死锁类 `D` 与完成类 `F` 设为竞争吸收类，可用 committor、平均吸收时间、条件死锁路径和参数敏感性量化结构死锁风险；Doob-`h` 变换给出条件于先达死锁的路径动力学解释。

### Assumptions

- CTMC 有限且非爆炸。
- 所有非指数时间已 PH 展开；否则不使用 CTMC 方程。
- `D` 与 `F` 为吸收类；A12/A_abs 成立，或已做 closed-class 分解并把方程限制到 `S_T`。
- 对 Doob-`h`，只在 `H={i:h_i>0}` 加成功吸收边界 `D` 上定义；跳入 `F` 的条件化率为 0。

### Proof obligations

- 从 LTS 和速率构造生成元 `Q`。
- 证明吸收概率方程与边界条件一致。
- 证明敏感性方程来自线性系统微分。
- 证明 Doob-`h` 在 `H union D` 上的条件化生成元行和为零、`D` 吸收、`F` 条件化率为 0，且条件路径解释成立。

### Failure modes

- 非指数 DES 被误写成 CTMC。
- `h_i=0` 状态上使用 `q^h_ij=q_ij h_j/h_i`。
- 将 Doob-`h` 路径解释误写成控制器。

### Evidence status

P4 标准有限 CTMC 方程项目内已证明；条件跳过程/Doob-style 来源已全文
定位。Metzner et al. 2009 只作为 ergodic Markov jump TPT/discrete
committor 背景，不能直接支撑 absorbing IMS theorem；Narahari 的全文
只锚定其 Section 3/3.1/3.2/4 中的有限吸收 DTMC/embedded-chain
fundamental matrix、平均死锁时间、吸收概率和瞬态分布，不是本项目 CTMC
sensitivity 或 Doob-h 的来源。

### Case mapping

`C0` 做手算吸收概率；`C5` 做中型案例精确 CTMC 与独立 DES 一致性。

### Enumeration assertion

对小模型求解 `h` 与 `tau`，检查边界条件、残差范数和仿真置信区间。

## T6 控制与干预定理

状态：精确 supervisor 基准已项目内证明（严格有限全观测状态域）；结构干预与概率控制仍拟证明。

### Statement

在有限模型上，可用最大不变安全集或最大许可 nonblocking supervisor 作为精确控制基准；覆盖所有最小死锁核的容量、预约或路线干预可作为候选结构干预问题；概率版本以风险预算与吞吐/工期代价 Pareto 边界表达。

### Assumptions

- 可控事件：release 授权、dispatch、transport choice、reservation。
- 不可控事件：service completion、transport completion；首篇排除无限环境到达。
- supervisor 必须对所有不可控后继闭合。
- hitting-all-minimal-cores 只在 core 全集完备且干预不创造新 core 条件下成立。

### Proof obligations

- 最大安全集固定点：从坏状态反向删除不能避免坏后继或不可控坏后继的状态。
- 最大许可 nonblocking：保留所有可控选择中不破坏 marked reachability 的行为。
- 结构干预：证明每个死锁必须包含至少一个被干预击中的最小 core。
- 概率控制：证明风险预算递归可行性或给出保守界。

### Failure modes

- 禁用可控事件造成策略停滞，被误称为系统死锁消除。
- 干预一个 core 后创造新的 core。
- 只覆盖发现集 core，未覆盖确认集或新可达 core。

### Evidence status

P5 有限全观测 state-based supervisor 基准已项目内证明；若 `x0 notin Y*`，必须报告 initial-state infeasible。Ramadge-Wonham 语言学精确基线仍作为文献基线。结构干预 hitting set、风险预算递归可行性和 Pareto 边界仍拟证明 + 计算验证。

### Case mapping

`C0` 对照精确 supervisor；`C5` 比较删除回流、容量调整、预约约束和路线断环。

### Enumeration assertion

枚举有限 LTS，计算最大不变安全集和 nonblocking supervisor；输出禁用事件、保持状态数、吞吐/工期代价与风险预算残差。
