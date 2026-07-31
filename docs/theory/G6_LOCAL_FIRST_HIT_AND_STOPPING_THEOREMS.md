# G6 局部首达与停止定理

Status: `G6 SUCCESSOR THEORY / NOT A G5 PATCH / NO HELD-OUT CLAIM`.

本文给出 G6 概率修复所需的独立理论表述。它不改写 G4/G5 的冻结结论，也不把历史重放计为 held-out confirmation。G6 的核心变化是：在完整有限稳定 LTS 上先识别局部容量核和真正闭类，再定义版本化 first-hit stopping estimand。

## 1. IMS 受限语义假设表

| 编号 | 假设 | 用途 | 失败边界 |
| --- | --- | --- | --- |
| A0 | 作业集合、资源集合、容量、mode、request alternative 均有限。 | 保证 reachable stable LTS 可穷举。 | 动态插单、无限缓冲或连续状态。 |
| A1 | 状态先经零时闭包归一化；非合流闭包保留集合后继。 | 定义 stable state 和 stable LTS。 | 零时闭包不终止或被任意选枝。 |
| A2 | `TransitionSpec` 是 per-job 规则：一次 transition 只改变其 `job_id` 的 mode、holds、requests、completion。 | 局部核前向不变的所有权基础。 | 一个外部事件能改写核内作业状态。 |
| A2b | **仅用于结构性不可完成定理**：有未清请求的作业，其当前 mode 下任何会改变 mode、holds、requests 或 completion 的 transition 都必须消费当前 request alternatives 中至少一个可行 alternative；不存在依赖核外另一资源、guard 或中间 mode 的 bypass。若不能静态证明本条，则必须改用完整 LTS 的 completion-nonreachability audit。 | 排除“核外释放旁路资源后核内作业绕过当前请求完成”。 | 任意 `TransitionSpec.requires/acquire` 可与 `state.requests` 脱钩。 |
| A3 | 无抢占、无故障、无外生释放、无外生插单。 | 防止核内持有资源被环境释放或替换。 | 故障释放、人工干预、动态到达。 |
| A4 | transition registry 完整：所有当前 admissible enabled transitions 均已供应。 | 证书的 “无核内 enabled transition” 才有证明力。 | 漏报核内 release 或 bypass transition。 |
| A5 | 资源容量守恒，完成作业不再持有资源或保留请求。 | completion 谓词与容量 witness 一致。 | 完成后仍持有资源。 |
| A6 | request alternative 是 OR-of-AND：每个 alternative 内需求合取，不同 alternatives 析取。 | 局部证书必须覆盖每个 alternative。 | 非资源 guard 或软预约未进入语义。 |
| A7 | 本文只讨论 capacity-mediated blocking。policy-only stall、外部同步缺失、calendar-empty 边界另行分类。 | 防止把一般停滞误写成容量死锁。 | 永久 guard、等待人工批准、策略禁用。 |
| A8 | 概率层只在完整非截断 stable LTS 和冻结 rate manifest 上构造有限 CTMC；科学执行入口用同一 model、initial stable state 与 transition registry 做确定性重枚举并要求 state/plant-arc 全等。 | exact 与 DES 使用同一停止目标并闭合 LTS provenance。 | 缺 rate、截断、未分类闭类或手工伪造 arc。 |

这些是假设而不是观察结果。若任一条在 case 中失败，正确输出是 structured refusal 或 scope narrowing，而不是把失败解释成 G6 支持证据。

## 2. 定义：不要混淆状态谓词、闭类和吸收标签

令 `X` 为完整 reachable stable LTS 的状态集，`->` 为稳定状态间 plant transition。

**定义 2.1 `F`，全批完成。**
`s in F` 当且仅当所有作业完成，且无持有资源、无未满足请求。`F` 是 success stopping class。

**定义 2.2 `D_global`，全局容量介导操作死锁。**
`s in D_global` 当且仅当：

1. `s` stable、未 complete，且事件日历为空或当前语义声明无待处理外部事件；
2. `s` 中没有任何 enabled transition；
3. 所有 unfinished jobs 均 blocked；
4. 存在覆盖全部 unfinished jobs 的 capacity-mediated closed blocking certificate。

`D_global` 是 plant-level operational deadlock 状态谓词，也可作为 stopped process 的 bad absorbing target。

**定义 2.3 `K_local` 与 `D_local`。**
`s in K_local` 当且仅当 `s notin D_global`，且 `s` 含至少一个 inclusion-minimal local closed blocking kernel。结构候选本身只证明当前阻塞。`s in D_local` 还必须满足以下至少一项：

1. 模型属于已核验的 A2b request-closed 子类，因而可用引理 3.2；或
2. 在由同一 transition registry 生成的完整、非截断 plant LTS 上，已机器核验从 `s` 到任一 `F` 状态均不可达。

当前通用实现采用第 2 项并在输出中记录 `local_bad_soundness_audit`；若发现到 `F` 的路径，则返回 `local_core_completion_reachable` 及最短事件反例，而不是把该候选吸收到 bad set。`D_local` 不是 plant LTS terminal SCC：它可以有 outgoing plant arcs，因为核外作业仍可能继续。

**定义 2.4 `R_livelock` 与 `R_terminal`。**
在去除或优先标记 `F`、`D_global`、`D_local` 后，对剩余 plant states 求 SCC。无出边 SCC 才是真正 terminal SCC。单点、无 self-loop、无 outgoing 的闭 SCC 归入 `R_terminal`；其它闭 SCC 归入 `R_livelock`。

**定义 2.5 `P_policy`。**
`P_policy` 是由给定控制策略禁用可控事件造成的停滞。若 plant 本身是分析对象，`P_policy` 不属于 plant terminal partition；若 policy 是分析对象，必须作为单独类进入 schema。

**本体检查。**
把 `D_local` 称为 “terminal class” 是范畴错误。`D_local` 是 first-hit stopping target，不是 plant graph 的闭 SCC。最小修复是使用 “terminal/stopping partition” 或 “bad hit set”，并仅把 `R_livelock/R_terminal` 称为 terminal SCC classes。

## 3. Request-closed 子类的局部核 completion 不可达引理

**定义 3.1 局部闭阻塞核。**
在状态 `s`，`K=(J_K,R_K,W_K)` 是局部闭阻塞核，当且仅当：

1. `J_K` 非空，且每个 `j in J_K` 未完成；
2. 每个 `j in J_K` 当前有非空 capacity-ready request alternatives；
3. 对每个 `j in J_K` 和每个 alternative `a`，存在 `r in R_K`，使 `a` 需求 `r`，且 `avail_s(r) < need(j,a,r)`；
4. 对每个 witness resource `r`，造成缺口的当前 holders 均属于 `J_K`，或由核内硬预约解释；
5. 没有 `j in J_K` 的 enabled transition；
6. `K` 对 job/resource 包含关系 inclusion-minimal。

**引理 3.2 核内作业不可完成不变性。**
在 A0-A7 **及 A2b** 下，若 stable state `s` 含局部闭阻塞核 `K`，则从 `s` 出发的任意 plant path 中，`J_K` 内每个作业一直未完成，且其在命中时刻的 requests 不会变为可满足。因此全批 `F` 从 `s` 不可达。这里前向不变的是核内作业的 blockedness 与 completion 不可达性，不是证书提取器在每个后继状态都返回字面相同的 formal certificate。

**严格证明。**

1. 由定义 3.1(5)，任一核内作业当前没有 enabled transition。由 A4，这不是 registry 缺失造成的假阴性。
2. 由 A2，任一核外 transition 只能改变其自身作业的 mode、holds、requests、completion，不能直接完成 `J_K` 内作业，也不能改写 `J_K` 内作业请求。
3. 由 A3 和 A5，核内作业持有的 witness resource 不会被核外事件、故障或抢占释放；完成作业也不能继续解释持有。
4. 由定义 3.1(3)(4)，命中时每个核内作业的每个 alternative 至少被一个核内 witness resource 阻塞。核外作业在命中时不持有这些 witness units，因此后续只能临时占用并释放原有 residual，不能释放核内作业已经锁住的 units，也不能把可用量提高到命中时刻以上。
5. A2b 排除与当前 requests 脱钩的 bypass；所以核外释放其它资源不能新启用核内 progress/release/completion transition。
6. 因此所有核内作业在任意后继状态仍不能取得任何 capacity-ready alternative，也不能发生 release/progress/completion transition。
7. 全批 `F` 要求所有作业完成，特别要求 `J_K` 内作业完成。与第 6 步矛盾。

故 `F` 不可达。

**一般 `TransitionSpec` 的语义审计命题。**
若不能证明 A2b，单凭当前 local certificate 不推出 `F` 不可达。对完整有限 LTS，可对每个 `K_local` 候选做从候选状态到 `F` 的图可达性检查：若可达，给出最短事件反例并拒绝该 terminal/stopping partition；若不可达，`D_local` 作为该具体有限模型的 bad stopping set 是语义健全的。这个机器审计证明的是“该已枚举模型上的 completion nonreachability”，不升级为一般结构定理。

**Blockedness 不变与 certificate 非不变。**
不变的是 `J_K` 内作业的 blockedness、命中时锁定的核内 units，以及全批 completion 不可达性。不应声称证书提取器在所有后继状态都返回同一 formal certificate，更不能声称同一 certificate JSON 文本不变。核外作业可能临时占用 witness resource 的 residual，使“当前全部 holders 都属于 `J_K`”这一提取语法暂时不成立；`state_id`、`shortest_reachable_prefix`、`zero_time_trace`、全局 residual、holder 列表和审计排序也都可能变化。论文应写 “kernel-job noncompletion is forward invariant after the certified hit”，而不是 “the certificate object is invariant”。

## 4. 新旧 estimand：首达时间、概率包含和时间量

在同一底层 CTMC `X_t` 上定义：

```text
T_G = inf { t >= 0 : X_t in D_global }
T_L = inf { t >= 0 : X_t in D_global union D_local }
T_F = inf { t >= 0 : X_t in F }
```

G5 全局 operational-deadlock estimand：

```text
theta_G = P(T_G < T_F).
```

G6 local-first-hit estimand：

```text
theta_L = P(T_L < T_F).
```

由于 `D_global subset D_global union D_local`，有事件包含：

```text
{T_G < T_F} subset {T_L < T_F}
```

因此在同一底层过程、相同 `F`、相同 rate manifest 且吸收定义有效时：

```text
theta_G <= theta_L.
```

若存在正概率路径先命中 `D_local \ D_global`，且未先命中 `F`，则通常严格：

```text
theta_G < theta_L.
```

平均停止时间的可比性要分清对象。无条件 stopped time：

```text
E[min(T_L,T_F)] <= E[min(T_G,T_F)]
```

因为 `T_L <= T_G` pathwise 对坏命中部分成立，且二者都与同一 `T_F` 取最小。该式可按 extended-real 不等式理解；只有在几乎必然吸收且两侧有限时，才能报告有限数值 mean。否则应报告无穷/未定义或结构化拒绝。条件平均坏命中时间一般不可比：

```text
E[T_L | T_L < T_F]  and  E[T_G | T_G < T_F]
```

可能任一方更小，也可能一方未定义。若旧二元 CTMC 因 reachable `R_*` 或局部核闭集没有被吸收而拒绝构造，则 G5 的平均时间量不存在，不能与 G6 数值比较。

**定理 4.1 新 estimand 定理。**
把 bad class 从 `D_global` 改为 `D_global union D_local` 改变了目标事件、stopping-rule hash 和 estimand id。因此它是 G6 新 estimand，不是 G5 修补。客观 state-class partition 未改变时，partition hash 应保持相同；selection 必须由独立的 stopping-rule hash 表达。

## 5. Terminal SCC 分解与结构拒绝定理

**算法定义。**

1. 枚举完整非截断 stable LTS；科学执行入口从 stable initial state 用同一 transition registry 确定性重枚举，要求 state signatures、plant arcs、controllability 与 edge traces 全等，并记录 `lts_provenance_audit`。
2. 标记 `F`。
3. 标记 `D_global`，并保存 global certificate。
4. 对非 `F/D_global` 状态枚举 all-minimal local kernels，先标记为 `K_local` 候选并保存 certificate family。
5. 若已证明 A2b，可由引理 3.2 把候选认定为 `D_local`；通用实现则在完整 LTS 上检查每个候选到 `F` 的可达性。任一候选可达 `F` 时返回最短事件反例并拒绝；全部不可达时记录 `local_bad_soundness_audit` 并标记 `D_local`。
6. 在剩余状态图上求 SCC；无出边 SCC 归为 `R_terminal` 或 `R_livelock`。
7. 按 `VersionedEstimandSpec` 选择 bad hit union 和 success class，形成 `D_sel := D_global union D_local; A_stop := D_sel union F`。`S_reach` 只是在 complete stopped-LTS support graph 中存在到 `A` 的 support path 的诊断集合。`S_T` 必须由 finite positive-rate stopped CTMC 的 unselected closed SCC / reverse-basin certificate 得出；若全域声明下 `B_closed` 非空，拒绝并报告 `non_almost_sure_absorption_domain`。
8. 冻结 state-space hash、partition hash、rate-manifest hash、exact stopping-rule hash、DES stopping-rule hash。

**定理 5.1 终端/停止分区健全性。**
在 A0-A8 下，若上述算法成功返回，则：

1. `D_global`、`D_local`、`F`、`R_livelock`、`R_terminal` 在报告中按优先级互斥；
2. `R_livelock/R_terminal` 是剩余 plant graph 的 terminal SCC 分类；
3. `D_local` 只作为经 A2b 证明或完整 LTS completion-nonreachability audit 核验的 stopped-process bad hit set 使用；
4. `S_reach` is the existential support-reachability diagnostic; `S_T` is the certified probability-one absorption domain, not a support-reachability basin;
5. exact CTMC 与 DES 可以共享同一 selected bad/success labels。

**结构拒绝定理。**
必须拒绝二元 CTMC 构造的情况包括：

- stable LTS 截断、存在 unavailable branch 或初始零时闭包不可用；
- 任一 LTS state 不满足模型容量、引用、stable/complete 一致性；
- LTS 与同一 model/initial stable state/transition registry 的确定性重枚举不一致；
- transition source/target 缺失；
- 缺失 frozen event rate；
- completion 与 bad absorbing label 重叠；
- 暂态无正 outgoing rate；
- 暂态不能到达 selected bad 或 success absorption；
- reachable `R_livelock/R_terminal` 未被选择为吸收类且不能到达 selected absorption；
- 选择 `D_global`-only 时存在 `D_local`，且该 choice 未声明为另一个可拒绝 estimand；
- policy-only stall 未进入 policy analysis schema。
- local-kernel 候选存在到 `F` 的路径；此时必须保留最短 bypass 反例，不能吸收到 `D_local`。

这一定理的目的不是削弱吸收可达性检查，而是在进入 CTMC solver 之前修正 partition。

## 6. All-Minimal Kernel Completeness 与 CRP Bridge 命题

**命题 6.1 All-minimal enumeration soundness。**
枚举器返回的每个 local certificate 都满足定义 3.1 的六条 closed-kernel 条件。

**命题 6.2 All-minimal enumeration completeness。**
若状态 `s` 中存在 inclusion-minimal local closed blocking kernel，则按 job 子集基数递增、canonical order 枚举所有 blocked-job 子集，并对 witness resource sets 做包含极小筛选，必返回该核。有限性由 A0 保证。

**命题 6.3 Order independence。**
真值不得依赖 first-hit enumeration order。输出顺序可以 canonical 化，但桥接判断必须量化整个 minimal-kernel family。

**命题 6.4 CRP partial bridge。**
给定冻结 target state 和 CRP 映射资源集 `R_crp`，partial-bridge agreement 只能在以下四项独立成立时为真：

1. target 在冻结 stable LTS 中 reachable；
2. local certificate family available；
3. `matching_kernel_count = |{K : resources(K)=R_crp}| >= 1`；
4. source profile consistent 且处于声明的 S4PR overlap。

全局 certificate 不得代替 local bridge。若有多个匹配核，报告 multiplicity；若无匹配核，报告 `matching_kernel_count=0`，不把枚举顺序导致的 first certificate 当成反例。

## 7. 复杂性边界

- 显式 stable LTS 上的 SCC 分解是 `O(|X|+|E|)`。
- all-minimal local kernel enumeration 在最坏情况下对 blocked jobs 指数级，因为需要检查 job subsets 和 resource witness subsets。
- 显式有限 CTMC 线性系统求解可用标准有限维方法；其成本取决于 `|S_T|` 和稀疏结构。
- 对紧凑 IMS 输入，不应声称整体多项式。完整 LTS、完整 all-minimal family 和完整策略输出都可能指数级。
- DES 是同一 stopped CTMC 的随机交叉检查，不证明 rare-event efficiency，也不替代 exact partition proof。

## 8. 最小反例

**反例 8.1 `D_local` 不是 terminal SCC。**
两个作业 `j1,j2` 分别持有 `r1,r2` 并请求对方资源，形成局部核；第三个 `free_job` 有 enabled completion transition。该状态在 `D_local` 中，但 plant LTS 有 outgoing arc。因此把 `D_local` 命名为 terminal SCC 是范畴错误。

**反例 8.2 漏 transition registry。**
若实际存在 `j1` 的 release transition，但 registry 未供应，枚举器可能误判 `j1,j2` 为局部核。此时失败原因是 A4 破坏，不能通过证明补救。

**反例 8.3 抢占或故障释放。**
若环境能释放 `j1` 持有的 `r1`，则 `j2` 可能继续，局部核 completion 不可达引理失败。此时必须把模型扩展为含故障/维修的过程，并重做证书定义。

**反例 8.4 未选闭类。**
若 reachable SCC `{a,b}` 在 `F`、`D_global`、`D_local` 外闭合循环，且未被并入 absorbing bad/success target，则二元 CTMC 的 committor 和平均吸收时间对原问题未定义。正确结果是拒绝或新 estimand。

**反例 8.5 核外释放旁路资源。**
`j1,j2` 持有 `r1,r2` 并相互请求，当前形成 `K_local`；`j3` 持有 `r3`。若 `j1` 在相同 mode 下另有一个只依赖 `r3`、与当前 requests 脱钩的完成 transition，则 `j3` 释放 `r3` 后，`j1` 可绕过互锁请求并继而释放 `r1`，最终全批完成。该模型满足 per-job ownership，却违反 A2b。因此结构候选不能进入 `D_local`；通用实现必须返回 `local_core_completion_reachable` 的最短事件反例。

## 9. 证明义务到测试映射

| 证明义务 | 必要测试 |
| --- | --- |
| A0-A8 语义边界 | invalid state、unknown endpoint、truncated/unavailable LTS、missing rate 均结构化拒绝。 |
| A8 provenance | 手工 plant arc 与同一 registry 的重枚举不一致时返回 `lts_generation_mismatch`；G4 quantitative payload 必须记录 `lts_provenance_audit.verified=true`。 |
| 引理 3.2 | request-closed local core with outside progressing job：`D_local` 命中、`D_global` 不成立、核内作业 completion 不可达；不要求后继 certificate JSON 相同。 |
| A2b 边界 | 核外作业释放与当前 requests 脱钩的旁路资源后可完成核内作业：完整 generated LTS 必须返回 `local_core_completion_reachable` 和最短事件路径。 |
| 核内无 enabled transition | kernel-internal release/progress transition 导致 local certificate unavailable。 |
| all-minimal completeness | 两个不可比 minimal kernels 全部返回，顺序和 JSON 稳定。 |
| OR-of-AND 覆盖 | 每个 alternative 至少一个 capacity witness；有任一可行 alternative 时拒绝 certificate。 |
| CRP bridge | reachable、certificate-family、resource equality、source profile 四字段独立；global certificate 不可替代 local。 |
| `D_local` 非 terminal SCC | local-hit state 允许 plant outgoing arc，但 stopped estimand 把它作为 bad hit。 |
| `D_global` vs `D_global union D_local` | 同一客观分类产生相同 partition hash、不同 stopping/estimand hash；D_global-only 遇 local core 时结构化拒绝。 |
| `R_livelock/R_terminal` | cycle SCC 与单点无出边 terminal state 分开分类。 |
| exact/DES 一致 | exact stopping hash 与 DES stopping hash 同源，DES seed derivation 冻结。 |
| 历史边界 | G5 raw hashes 不覆盖；G4/G5 replay 只能标记为 historical regression。 |

## 10. 可声称与不可声称

**可声称。**

- 在 A0-A8 且满足 A2b request-closed discipline 的有限受限 IMS 子类中，local closed blocking kernel 命中足以排除全批 completion。
- 对一般有限 `TransitionSpec`，只有通过完整 LTS completion-nonreachability audit 的 local candidate 才可进入 `D_local`。
- `D_local` 可以作为 stopped process 的 bad first-hit target。
- `theta_L=P(T_L<T_F)` 与 `theta_G=P(T_G<T_F)` 是不同 estimands，且在同一底层过程上有 `theta_G <= theta_L`。
- 完整 terminal/stopping partition 是 exact CTMC 与 independent DES 共享 stopping semantics 的前置条件。
- all-minimal local kernel family 支持 scope-correct CRP partial bridge。

**不可声称。**

- 不可声称 G6 是 G5 的修补或重新计分。
- 不可声称 historical replay 是 held-out confirmation。
- 不可把 `D_local` 称为 plant LTS terminal SCC。
- 不可声称每个 local core 都是全局 operational deadlock。
- 不可把 global covering certificate 代替 local CRP bridge。
- 不可在 transition registry 不完整、存在抢占/故障/外生插单、或 reachable unselected closed class 时给出二元 CTMC 数值。
- 不可把 DES 置信区间覆盖 exact probability 当成 partition proof 或 theorem proof。

## 11. 论文写法建议

推荐使用如下句式：

> G6 estimates the probability of first hitting a declared bad stopping set,
> `D_global union D_local`, before all-batch completion. This is a new
> versioned estimand. It is not a retroactive repair of the G5
> global-operational-deadlock estimand.

中文对应：

> G6 估计的是在全批完成前首达声明坏停止集 `D_global union D_local` 的概率。
> 该概率是新的版本化 estimand，不是对 G5 全局操作死锁 estimand 的事后修补。

历史 G4/G5 case 可以用于 labelled historical replay，以验证诊断机制是否被新语义修复；它们不能替代新的独立 sealed confirmation set。

## 2026-07-31 Certified Absorption-Domain Correction

Let `D_sel := D_global union D_local; A_stop := D_sel union F` be the selected stopped target and let
`T = V \ A_stop`. `S_reach` is the set of nonabsorbing states in the complete
stopped-LTS support graph that have at least one support path to `A_stop`. It is a
structural diagnostic and a necessary condition for probability-one absorption,
not a sufficient condition.

For a finite complete positive-rate stopped CTMC, compute the positive-rate
edges in the full stopped graph. An unselected closed SCC `C_closed subset T` has no
outgoing positive-rate edge from `C_closed` to `(T \ C_closed)` and no outgoing positive-rate
edge from `C_closed` to selected A_stop. Closure is not checked in the graph induced only
by `T`; a state with `s -> F` is not in an unselected closed SCC. Let
`B_closed` be the reverse basin in `T` of all such unselected closed SCCs.
Define `S_T = T \ B_closed`.

Theorem, under exactly the finite complete positive-rate stopped-CTMC
assumptions: `x in S_T` iff `P_x(tau_{A_stop} < infinity) = 1`. If `x` can reach an
unselected closed SCC, there is positive probability of entering it and then
never hitting `A_stop`. If `x` cannot reach one, every eventual closed class reachable
from `x` in the finite stopped chain is selected A_stop, so `x` hits `A_stop` almost
surely.

The global gate `A_abs` is `B_closed = empty` over the claimed nonabsorbing
analysis domain. The current production G4 gate supports the global
certificate/refusal boundary only; partial-domain committor or mean-time
payloads remain unsupported even though the mathematics of a restricted `S_T`
exists. Committor, mean-time, sensitivity, and Doob-h equations are confined to
certified `S_T`.

Counterexample `CE-NB1`: with unit rates for `s0 -> F`, `s0 -> c`, and `c -> c`,
`P_s0(hit F) = 1/2`. Thus `s0 in S_reach` but `s0 notin S_T`; `{c}` is an
unselected closed SCC, `B_closed = {s0, c}`, and the global certificate refuses
`non_almost_sure_absorption_domain`. Machine regression: `tests/test_terminal_classes.py::test_branching_closed_class_separates_s_reach_from_s_t`.
