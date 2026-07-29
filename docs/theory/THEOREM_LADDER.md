# 六级定理梯

所有条目是论文候选主链。状态字段用于区分定义、文献基线、拟证明、计算验证与反例。

## T1 语义等价定理

状态：拟证明。

### Statement

给定满足有限性、容量守恒、BAS 明确释放点和闭包良定义的 `IMS-RAS`，其操作语义可构造为有限状态转换系统；在附加 Petri 可投影条件下，可构造有界 Petri 网，使闭包归一化稳定状态与可达标识之间存在事件对应和候选双模拟或 trace equivalence。

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

定义 + 拟证明。枚举只检查小模型事件守恒与状态映射。

### Case mapping

`C0`、`C2` 用于最小 LTS/Petri 映射；`C4` 用于检查 AGV 投影是否丢失死锁。

### Enumeration assertion

对每个小模型，枚举所有 `S_st`，检查所有事件后继均满足容量守恒，且 Petri 子类中 `phi` 后继集合与 LTS 后继集合一致。

## T2 死锁证书定理

状态：拟证明。

### Statement

在闭包归一化稳定状态上，IMS 全局操作死锁当且仅当存在覆盖所有未完成活动的多容量封闭阻塞核。对单实例、一持一求、无替代路线的受限子类，可推出简单有向环判据。

### Assumptions

- 证书包含持有量、需求量、残余容量、预约 token、可选后继和不可自主释放条件。
- 所有未完成工件的可继续后继都被证书覆盖。
- 不允许把 Palmer 队列网络 `knot` 直接替换成一般 IMS 证明。

### Proof obligations

- 死锁到封闭核：从无可发生事件构造最小阻塞核。
- 封闭核到死锁：证明每个未完成活动均被封闭条件阻断。
- 多容量资源下证明残余容量不足，而不仅是存在等待边。
- 替代路线下证明所有替代均被阻断。

### Failure modes

- 资源图有环但残余容量足够。
- WCC 无汇快捷等价在 Palmer 2/3 服务器反例中失败。
- 局部封闭核未覆盖所有未完成工件，只能推出局部死锁。

### Evidence status

文献基线 + 拟证明 + 反例。Palmer knot 是有限队列网络基线；无汇 WCC 快捷只在单节点、两节点每节点不超过 2 服务器、或全有限单服务器条件下使用。

### Case mapping

`C1` 击穿“有环即死锁”；`C3` 比较简单环、无汇 WCC 与多容量封闭核。

### Enumeration assertion

枚举小模型可达稳定状态，输出最小 `DeadlockCertificate`，并检查每个证书边都有具体工件-资源证据和最短可达前缀。

## T3 虹吸桥接定理

状态：拟证明。

### Statement

在可投影的 IMS 子类上，最小封闭阻塞核与构造 Petri 网中的最小致死虹吸存在对应；一般 IMS 中仅保留单向蕴含或反例边界。

### Assumptions

- 每个资源占有与工件阶段可投影为 Petri place。
- 预约 token、AGV 交接和 BAS 卸载都有守恒 place 表示。
- 闭包不会隐藏可见资源释放。
- 无软预约过售，或过售已经显式 finite-state 展开。

### Proof obligations

- 从封闭核构造失标或不可恢复 siphon。
- 从致死 siphon 恢复可审计的工件-资源阻塞核。
- 证明最小性在映射下保持，或给出只保持包含关系的条件。

### Failure modes

- siphon 含结构 place 但没有对应工件等待证据。
- AGV/预约 place 被投影掉后 false negative。
- 软预约使 Petri 守恒关系失真。

### Evidence status

文献基线 + 拟证明 + 反例准备。

### Case mapping

`C0` 验证正例；`C4` 验证投影漏项；专门反例验证双向映射失败。

### Enumeration assertion

对 Petri 子类计算最小 siphon，与 IMS 最小 core 做双向包含检查；一般类仅报告不可映射原因。

## T4 结构充分条件与阈值族

状态：拟证明。

### Statement

若所有必须获取且不可抢占保持的机器、缓冲、AGV 和预约 token 存在全局严格获取偏序，并且每条路线按该偏序请求资源，则不存在 circular-wait 型操作死锁。对双向制造岛交换族，容量、AGV、WIP 和双向路线负载阈值作为待推导命题族。

### Assumptions

- 偏序覆盖 machine、buffer、AGV、reservation。
- 工件不得持有高序资源再请求低序资源。
- BAS 阻塞持有也服从同一偏序。
- 释放规则不制造隐式逆序请求。
- 该结论只保证 circular-wait deadlock 排除，不自动保证所有状态 nonblocking。

### Proof obligations

- 反证：若存在封闭核，则沿每条等待边导出严格上升资源序列；有限偏序中不可能闭合。
- 处理多资源需求：至少一个阻塞需求必须导出违反偏序的等待链。
- 双向岛族需推导或证伪容量/WIP/AGV 阈值，不得预置公式。

### Failure modes

- 只有机器投影为 DAG，但 AGV 或缓冲预约存在逆序。
- 拓扑 DAG 不含容量持有顺序，不能推出 deadlock-free。
- 满足无 circular-wait 仍可能存在 livelock 或策略性 blocking。

### Evidence status

拟证明 + 计算验证。双向制造岛是 conjecture family。

### Case mapping

`C2` 对应偏序无环正例；`C5` 对比 M-D 双向回流与删除回流 DAG 版本。

### Enumeration assertion

穷举小参数网格，检查偏序条件满足时无封闭核；对双向岛族记录第一个可达死锁参数点和最小证书。

## T5 概率桥接定理

状态：拟证明。

### Statement

对有限 `IMS-CTMC`，把死锁类 `D` 与完成类 `F` 设为竞争吸收类，可用 committor、平均吸收时间、条件死锁路径和参数敏感性量化结构死锁风险；Doob-`h` 变换给出条件于先达死锁的路径动力学解释。

### Assumptions

- CTMC 有限且非爆炸。
- 所有非指数时间已 PH 展开；否则不使用 CTMC 方程。
- `D` 与 `F` 为吸收类，暂态集合 `T` 有良定义。
- 对 Doob-`h`，只在 `h_i > 0` 的状态上定义。

### Proof obligations

- 从 LTS 和速率构造生成元 `Q`。
- 证明吸收概率方程与边界条件一致。
- 证明敏感性方程来自线性系统微分。
- 证明 Doob-`h` 条件化生成元行和为零且条件路径解释成立。

### Failure modes

- 非指数 DES 被误写成 CTMC。
- `h_i=0` 状态上使用 `q^h_ij=q_ij h_j/h_i`。
- 将 Doob-`h` 路径解释误写成控制器。

### Evidence status

文献基线 + 拟证明。Markov jump TPT 与 committor 基线引用 Metzner et al. 2009；Narahari 仅按当前可核验摘要边界用于制造系统吸收 Markov 基线。

### Case mapping

`C0` 做手算吸收概率；`C5` 做中型案例精确 CTMC 与独立 DES 一致性。

### Enumeration assertion

对小模型求解 `h` 与 `tau`，检查边界条件、残差范数和仿真置信区间。

## T6 控制与干预定理

状态：拟证明。

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

文献基线 + 拟证明 + 计算验证。

### Case mapping

`C0` 对照精确 supervisor；`C5` 比较删除回流、容量调整、预约约束和路线断环。

### Enumeration assertion

枚举有限 LTS，计算最大不变安全集和 nonblocking supervisor；输出禁用事件、保持状态数、吞吐/工期代价与风险预算残差。
