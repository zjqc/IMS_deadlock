# 假设登记表

每条理论命题必须引用本登记表中的假设编号，并说明是否用于定义、文献基线、拟证明、计算验证或反例。

## A0 有限批与有限容量

状态：定义。

`J` 有限，路线有限，所有资源容量有限，预约 token 有限。首篇不允许无限外生到达。

用途：T1-T6。

失败后果：状态空间可能无限，有限 LTS、精确 supervisor 和有限 CTMC 方程均不成立。

## A1 容量守恒

状态：定义。

每个物理资源与每类预约 token 均满足其 ontology 对应的不变量。future-claim ontology 使用 `occ(r)+hard_res(r)<=cap(r)`；token-resource ontology 使用 `occ(r)<=cap(r)`、`res(v)<=cap(v)` 和兑现安全映射。物理占用与预约占用不得混同。

用途：T1-T4、T6。

失败后果：多容量等待证书和 Petri 守恒 place 无法成立。

## A2 BAS 释放点明确

状态：定义。

`blocked_complete` 与 `blocked_unload` 在完成后持续占有当前机器、AGV 或载体，直到语义中明确的卸载、交接或离开事件发生。

用途：T1-T4、案例 C4/C5。

失败后果：加工完成被错误当作释放，死锁风险被系统性低估。

## A3 闭包良定义

状态：项目内已证明（严格受限子类）/一般情形拟证明。

零时间闭包终止，并产生至少一个稳定后继。若非合流，则保留 set-valued `Cl(s)`；只有终止+合流或固定优先级/排序时使用 `kappa(s)`。

用途：T1-T6。

失败后果：稳定状态不唯一，确定 LTS、CTMC 和 supervisor 需要改成非确定模型。

## A4 闭包归一化陈述

状态：定义。

所有主定理只在 `S_st` 上陈述；非零时间事件触发后立即闭包。

用途：T1-T6。

失败后果：中间 transient 状态会被误判为死锁或可控状态。

## A5 无抢占、无故障、无动态插单

状态：定义。

首篇排除抢占、设备故障维修、动态插单和无限外生到达。

用途：T1-T6。

失败后果：持有-请求-释放和吸收类定义需要扩展，当前主链不适用。

## A6 证书完备性

状态：项目内已证明（严格受限子类）/一般情形拟证明。

封闭阻塞核必须记录持有量、需求量、残余容量、预约、capacity-ready 替代后继、witness 集合 `W_K`、holder 解释集合 `H_K` 和不可自主释放条件。P2 只把这类证书用于 capacity-mediated deadlock；永久非资源 guard 或外部同步缺失不属于证书完备性范围。

用途：T2、T6。

失败后果：简单环或 WCC 可能产生 false positive/false negative。

## A7 Petri 可投影条件

状态：拟证明。

IMS 子类的资源、阶段、预约、BAS 阻塞和闭包选择可表达为有限有界 Petri 网 place/transition，且不丢失释放时点。

用途：T1、T3。

失败后果：S3PR/siphon 结论只能作为启发或单向边界。

## A8 全局获取严格偏序

状态：项目内已证明（严格受限子类）/一般情形拟证明。

存在严格偏序覆盖机器、缓冲、AGV 与预约 token；所有持有后请求均严格上升，BAS 阻塞也不产生逆序请求。P3 已证版本还要求每个覆盖封闭阻塞核是 chain-decomposable：对每个被选中的 holder，都必须存在该 holder 自己的 blocked capacity-ready 替代和下一条 witness。P3 只排除 capacity-mediated deadlock；不能分解到具体 holder-dependency chain 的聚合容量缺口、永久非资源 guard 和外部同步缺失不在已证范围内。

用途：T4。

失败后果：不能用 circular-wait 反证链证明无死锁。

## A9 CTMC 指数或 PH 时间

状态：定义。

所有随机时长为指数，或已 PH 展开成有限相位 CTMC。一般非指数时间只能用于 DES 仿真或另列扩展。

用途：T5、T6 概率版本。

失败后果：`Q`、committor、Doob-`h` 生成元不适用。

## A10 控制可观测与不可控闭合

状态：项目内已证明（严格受限子类）/一般情形拟证明。

控制器能观测 `IMSState` 所需的占用、预约、阶段与阻塞模式；安全集必须包含所有不可控后继。

用途：T6。

失败后果：最大许可 supervisor 计算结果不可实施或不安全。

## A11 最小干预独立性

状态：拟证明。

core 全集完备，且容量调整、预约约束或路线断环不会引入新 core，才可把干预写成 hitting-all-minimal-cores。

用途：T6。

失败后果：必须使用迭代反例生成，而不是一次性 set cover。

## A12 / A_abs 竞争吸收完备性

状态：项目内已证明（严格受限子类）/一般情形拟证明。

对 T5 的竞争吸收分析，所有分析范围内可达的非 `D/F` 状态必须以概率 1 命中 `D union F`；若不满足，必须先做 closed-class 分解，显式给出 `S_T`、其它 closed/recurrent/livelock 类 `R_c`，并把 `R_c` 并入坏吸收类、报告其可达概率，或把 committor/平均吸收时间方程限制到 `S_T`。

用途：T5、T6 概率版本。

失败后果：`Q_{S_T,S_T}` 可能不可逆，无条件平均吸收时间可能为无穷或不定义，`h` 不能解释为全域竞争吸收概率。

## CW1-CW10 IMS-RAS^CW 受限主链假设

状态：项目内已证明（严格受限子类）。

`IMS-RAS^CW` 的完整假设写在 `CORE_THEOREMS_AND_PROOFS.md`，包括有限批、闭包终止、容量守恒、有限 capacity-ready OR-of-AND 替代需求、enabled timed/transport completion 空需求替代、原子获取、BAS/AGV 持有保持、不可自主释放可判定、事件分类完备、首篇排除项和 policy-stall/calendar-empty 边界。P2 的 iff 只覆盖 capacity-mediated global operational deadlock；P3 额外使用 chain-decomposable strict-precedence 条件。

用途：P1-P6 已闭合主链，其中 P2/P3 的死锁结论仅覆盖
capacity-mediated 子域，P6 的 NP-complete 结论仅覆盖 `IMS-SU^A`。

失败后果：若任一 CW 假设被实际案例击穿，已证结论必须收缩到更小子类，或把该案例登记为一般 IMS 的边界反例。

## A13 表示与路线单调性

状态：项目内已证明（严格受限子类）/一般情形开放。

P6 的 NP membership 使用显式有限无环路线，因此每个事件使某个工件阶段
严格前进，完成见证长度由总剩余阶段数界定。P6 的显式图上界则假定整个
闭包归一化 LTS 已作为输入给出，不能把该图大小等同于紧凑制造模型大小。

用途：P6 复杂性边界。

失败后果：循环路线、隐式无限重试或未展开闭包可能破坏短见证；此时
`IMS-SU-SAFE in NP` 的现有证明不适用。一般紧凑 IMS 目前只保留
NP-hard 下界。

## A14 `BIX0` 启动饱和前缀

状态：项目内已证明（候选态前置命题）。

BIX0 只构造无成功 A/B transfer 的候选饱和状态。A holder 请求
`{D,G}`，B holder 请求 `M`，没有自主释放、替代路线、额外 guard 或
policy/calendar 停止，且 `c_M,c_G,c_D>=1`。

用途：P3c 候选态 closed-kernel 阈值；不再作为可达性定理。

失败后果：一旦允许 persistent-D、drain、替代路线或强制事件优先级，
`c_D` 和释放语义重新进入阈值；P3c 公式不能外推。

## A15 `BIX1-SAT` 可达启动/完成饱和族

状态：项目内已证明并有小网格程序观测。

BIX1-SAT 从空持有状态出发，A 初始请求 `M`，B 初始请求 `G`。
A 链显式包含 `start`、uncontrollable `service_complete`、controllable
`transfer(G,D,V; release M)`、uncontrollable `drain`；B 链显式包含
`start`、uncontrollable `transport_complete`、controllable
`unload(M; release G)`、uncontrollable `complete`。`V` 是硬预约 token；
`event_calendar_empty=True` 仅表示无外部日历，完成事件仍在 transition
registry 中。所有转移为显式非零时 `TransitionSpec`。

用途：P3d 可达 capacity-mediated global deadlock 阈值
`n_A>=c_M and n_B>=c_G`。

失败后果：persistent-D、无 drain 外部堵塞、替代路线、强制调度优先级或
成功 transfer 后的 D/V 积累属于 `outside_bix1_sat` 边界，不能登记为
P3d theorem mismatch。

## A16 `IMS-SIP^1` 状态诱导诊断桥

状态：项目内已证明并有小模型枚举审计。

给定 reachable stable 状态及 inclusion-minimal local closed blocking
core，`IMS-SIP^1` 要求核资源单位容量且 residual 为 0；每个核工件恰持有
一个单位核资源并恰有一个单资源单位请求；没有 OR、AND、soft
reservation、外部 guard、隐藏 release 或非合流闭包释放路径。Petri
对象只能是以 `free:r` 为 place、以“先获得请求资源才释放持有资源”为
transition 的 state-induced wait-snapshot diagnostic net。

用途：P2c 中 inclusion-minimal local core 与 inclusion-minimal empty
siphon 的受限双向对应；`certificate.bridge_status` 的精确/拒绝分类。

失败后果：该桥必须返回
`not_applicable_ims_sip1_assumptions_failed:<reason>`。P1 的
one-place-per-state reachability net、经典 plant/S3PR、control-only 或
approval-only place、C4/C5 conjunctive request、OR 替代和多容量 residual
均不能由 P2c 自动获得双向等价。
