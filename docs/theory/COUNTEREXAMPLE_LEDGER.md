# 反例与失败账本

本账本记录会击穿过强命题的最小案例设计。只有已经给出 concrete model、reachable prefix 和 certificate/failure witness 的条目才能标为“反例”；发现阶段尚未实例化的条目标为“反例候选/待实例化”。

## CE-C1 多容量有环但不死锁

状态：反例候选/待实例化。

目标击穿命题：资源请求图存在有向环即充分死锁。

构造要点：

- 两个资源 `r1,r2`，至少一个资源容量大于 1。
- 两个工件形成 `r1 -> r2 -> r1` 请求环。
- 残余容量仍足以满足至少一个请求，因此存在可继续事件。

预期结论：简单环只能提示风险，不能作为多容量 IMS 的充分证书。

## CE-C3 WCC/simple-cycle failure

状态：反例候选/待实例化。

目标击穿命题：无汇弱连通分量或普通 SCC 总能等价于死锁。

基线边界：Palmer 的有限队列网络 knot 判据是文献基线；无汇 WCC 快捷只在单节点、两节点每节点不超过 2 服务器、或全有限单服务器条件下成立。2/3 服务器构造保留为 WCC 快捷失败边界。

IMS 迁移要求：必须使用容量敏感封闭阻塞核，而不是 WCC 快捷。

## CE-C4 机器投影漏掉 AGV/预约

状态：反例候选/待实例化。

目标击穿命题：只看机器资源即可判断制造岛死锁。

构造要点：

- 机器投影无环或可继续。
- 加入 AGV、站台或预约 token 后，一个工件占有机器等待 AGV，另一个占有 AGV 等待目标机器或交接位。
- `blocked_unload` 持续占有机器或 AGV。

预期结论：运输资源不可省略；Petri 或 RAS 映射必须保留 AGV/预约 place。

## CE-CL1 闭包不合流

状态：反例候选/待实例化。

目标击穿命题：零时间闭包总可写成确定函数 `kappa`。

构造要点：

- 同一触发后状态存在两个零时间事件，兑现不同预约或抢占同一剩余缓冲。
- 两条零时间序列都终止，但到达不同稳定状态。

预期结论：一般理论必须使用集合值 `Cl(s)`；确定 `kappa` 需要额外优先级或合流证明。

## CE-RSV1 软预约超卖

状态：反例候选/待实例化。

目标击穿命题：预约 token 可直接等同物理容量。

构造要点：

- 两个工件软预约同一容量为 1 的未来资源。
- 调度策略允许两个软预约同时存在。
- 兑现时只有一个能进入，另一个进入等待或改路。

预期结论：软预约需要独立状态和兑现失败语义；不能直接用 S3PR 守恒 place 表示。

## CE-SIP1 Siphon 双向映射失败

状态：已实例化 Petri 边界反模型；它攻击一般 Petri-to-IMS 逆映射，不是
一个 `IMS-SIP^1` 内部反例。

目标击穿命题：任意 IMS 中最小封闭阻塞核与最小致死 siphon 双向等价。

最小反模型：

- 一个 Petri place `approval`，初始 marking 为 0；
- 一个 transition `approval-self-loop`，其 pre/post 均为
  `{approval}`；
- `{approval}` 是 inclusion-minimal empty siphon，但 place 不是
  `free:r`，不存在工件持有边、资源请求边或 IMS reachable prefix。

失败证据：`tests/test_petri.py` 的
`test_control_only_empty_siphon_has_no_inverse_ims_core_mapping` 枚举出该
empty siphon，同时确认它不属于 wait-snapshot resource-place 命名域。

定理修正：P2c 只在 `IMS-SIP^1` state-induced diagnostic net 中证明
双向对应；任意 plant/control Petri net 的 empty siphon 不能反向恢复 IMS
blocking core。软预约、审批和闭包优先级的更丰富反例仍保留为后续扩展。

## CE-INT1 干预创造新 core

状态：反例候选/待实例化。

目标击穿命题：覆盖所有当前最小 core 的一次性干预必然消除所有死锁。

构造要点：

- 删除一条回流路线或增加一个预约约束后，原 core 消失。
- 新路线选择或排队模式产生以前不可达的新封闭阻塞核。

预期结论：hitting-all-minimal-cores 需要 core 全集完备和干预不创造新 core；否则必须迭代反例生成。

## CE-BIXD1 `BIX1-SAT` 阈值不能越过 persistent-D 边界

状态：已实例化理论边界；程序分类为 `outside_bix1_sat`。

目标击穿命题：`n_A>=c_M 且 n_B>=c_G` 是所有双向/有限缓冲制造岛
deadlock 的充要条件，或删除 B->M 回流即可推出一般 deadlock-free。

最小配置：

- `c_M=c_G=c_D=1`；
- `n_A=2,n_B=0`；
- A1 成功 transfer 后长期占用 D，A2 随后持 M 请求 D。

最短前缀：`start(A1) -> transfer(A1,D) -> start(A2)`。

失败证据：此时 D 满、A2 的 `{D,G}` 因 D 缺口阻塞，但
`n_B>=c_G` 为假。若 A1 没有 capacity-ready drain，该状态是
buffer-full/calendar/外部-drain 终端边界，不属于 P2 capacity-mediated
全局死锁；若 drain 存在，则必须把 drain 资源和释放语义纳入新阈值。

定理修正：P3c 只用于无成功 transfer 的 `BIX0` 候选态；P3d 只用于
显式含 drain、且见证前缀没有成功 transfer 的 `BIX1-SAT`。CE-BIXD1
属于 persistent-D 边界，不是 BIX1-SAT theorem mismatch。删除回流只
消除 M-G 双向封闭核，不能独自保证有限 D 无终端阻塞。

后续闭环：P3e 的 `BIX2-PERSIST` 不把缺失 external drain 的 terminal
block 冒充容量死锁，而是显式加入下游资源 Q 和每次 handoff 后的 release，
在 `M->D->Q->M` 子族中得到 D 进入最小核的精确阈值，并用删除 `Q->M`
构造同语义 DAG 修复。它关闭的是 CE-BIXD1 的一个可证明子类，不是一般
persistent-buffer 结论。

## CE-BIXD2 Optional Drain Is Not a Structural Repair

状态：反例候选/待实例化。

目标击穿命题：给 ring 增加一条可选 controllable drain，就能推出结构
deadlock-free。

构造要点：

- 保留 `M->D->Q->M` 的原 ring 路径；
- 添加一个可控 alternate drain，但不强制其在进入饱和前发生；
- 调度仍可选择原 ring 的饱和前缀。

预期结论：存在可选安全动作只说明 supervisor 可能规避死锁，不消除坏
可达前缀。P3e-b 的修复必须真正删除 `Q->M` 或施加等价的不可绕过结构
顺序；可选 drain 属于 P5 控制问题。

## CE-NB1 Nonblocking 不等于所有随机路径完成

状态：反例候选/待实例化。

目标击穿命题：标准 nonblocking 保证每条随机路径完成。

构造要点：

- 每个状态都存在到 completion 的延拓。
- 同时存在无限循环路径或策略反复选择不完成事件。

预期结论：standard nonblocking 是存在性延拓性质；要推出几乎必然完成需要额外进展、公平性或 CTMC 非爆炸假设。

## 登记规则

状态：定义。

每个新增反例必须记录：

- 被击穿命题；
- 最小资源/工件/容量配置；
- 最短可达前缀；
- 证书或失败证据；
- 对定理假设的修正；
- 是否进入发现集或冻结确认集。
