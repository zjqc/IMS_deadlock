# Petri wait-snapshot bridge

状态：`IMS-SIP^1` 受限子类已形成项目内定理和枚举实现；一般
`IMS-RAS^CW` 到经典 S3PR 的双向虹吸等价仍不主张。

本文区分两个 Petri 对象：

- P1 的 reachability net：每个可达稳定 IMS 状态一个 place，每条 LTS 边
  一个 transition。它只证明有限 LTS 可表示性，不是结构 Petri 网，也不
  产生 S3PR 虹吸结论。
- P2c 的 wait-snapshot diagnostic net：固定在一个已给定的稳定证书态，
  只表示核内工件“释放当前资源之前必须先获得下一资源”的局部等待快照。

## 1. `IMS-SIP^1` 适用条件

给定稳定状态 `s` 和 inclusion-minimal local closed blocking core
`K=(J_K,R_K,W_K,H_K)`，`IMS-SIP^1` 要求：

- `s` 已经完成零时间闭包归一化；可达性由调用者用最短前缀或案例 witness
  单独记录。实现要求 `certificate.shortest_reachable_prefix is not None`；
  空 tuple 可表示初始态可达，`None` 表示未提供可达性证据。
- `K` 必须是 inclusion-minimal。非极小证书可以包含一个 siphon，但不能用于
  P2c 的极小双向对应。
- 每个 `r in R_K` 都是单位容量资源或硬预约 token，且在 `s` 中 residual
  availability 为 0。
- 每个 `j in J_K` 恰持有一个核内资源 `h(j)`，持有量为 1。
- 每个 `j in J_K` 恰有一个当前 request alternative，且该 alternative
  恰请求一个单位核内资源 `q(j)`。
- 不存在 OR 替代、AND/conjunctive 请求、soft reservation、外部 guard、
  隐藏 release 或非合流闭包产生的额外释放路径。
- AGV 与硬预约 token 只有在作为普通单位资源建模时才可进入 `R_K`。

若任一条件失败，bridge 输出
`not_applicable_ims_sip1_assumptions_failed:<reason>`，不得从该状态伪造
Petri siphon 结论。

实现机械检查证书态、可达 witness、极小性、单位容量、一持一求、OR/AND
缺失、residual marking，以及证书 evidence edges 与实际 state
holds/requests 的逐项一致性。构造后还独立检查目标 place set 确为 empty、
siphon 且 inclusion-minimal；任一检查失败都不能标记 exact。closed-world
事件完备、不可隐藏释放、非容量 guard 已满足、闭包合流等语义条件由
`DeadlockCertificate.assumptions`、案例 witness 和调用者的理论审计负责；
API 不把 snapshot 诊断网升级为一般 plant 或 S3PR 双模拟。

## 2. Wait-Snapshot Net 构造

对 `R_K` 中每个资源建 place `free:r`，其 marking 为

`M_s(free:r)=cap(r)-occ_s(r)`.

对 `J_K` 中每个工件建 transition

`t_j: free:q(j) -> free:h(j)`.

含义是：工件 `j` 只有先获得它请求的下一资源 `q(j)`，才可能释放当前持有
资源 `h(j)`。该 transition 不是 IMS 事件本体，而是等待依赖的诊断投影。

ordinary siphon 判据采用：

`bullet Sigma subseteq Sigma bullet`,

即任一向 `Sigma` 输出 token 的 transition，也必须从 `Sigma` 消耗 token。
实现中等价检查为：若 `Post(t)` 与 `Sigma` 相交，则 `Pre(t)` 也与
`Sigma` 相交。

## 3. P2c 定理

在 reachable stable `IMS-SIP^1` 状态中，inclusion-minimal local closed
blocking core 与其 state-induced wait-snapshot net 中的 inclusion-minimal
empty siphon 双向对应。

### Core 到 Siphon

取 `Sigma_K={free:r | r in R_K}`。单位容量且 residual 为 0 给出
`M_s(p)=0` 对所有 `p in Sigma_K`。对任一向 `free:h(j)` 输出的 transition
`t_j`，其输入为 `free:q(j)`。由于 `q(j) in R_K`，输入也在
`Sigma_K`，故 `Sigma_K` 满足 siphon 条件。

若 `Sigma_K` 含有真子集 `Sigma'` 也是 empty siphon，则对应资源子集
`R'` 对所有输出回 `R'` 的 holder 仍有输入留在 `R'`。由一持一求和单位
容量条件，可恢复一个真子 closed blocking core，违背 `K` 的 inclusion
minimality。因此 `Sigma_K` 是 inclusion-minimal empty siphon。

### Siphon 到 Core

给定 inclusion-minimal empty siphon `Sigma`，令
`R_S={r | free:r in Sigma}`。empty marking 和单位容量说明每个 `r in R_S`
由唯一核内工件持有。siphon 条件说明每个释放到 `R_S` 的 holder transition
在释放前请求的 `q(j)` 仍在 `R_S`。因此这些 holder 工件的唯一
capacity-ready alternative 均被 `R_S` 内资源阻塞，形成 local closed
blocking core。若存在真子 core，则其资源 places 给出真子 empty siphon，
违背 `Sigma` 的 minimality。

## 4. 边界与反例

P2c 不是一般 Petri/S3PR 桥：

- C4/C5 的 blocked-unload 或 blocked-complete 状态含 conjunctive
  request，例如 `{D,G}`；wait-snapshot bridge 必须拒绝，而不是把其中某
  一个资源投影成伪 siphon。
- 多容量资源有 residual/witness 算术；简单环或普通 siphon empty 条件不足
  以刻画容量缺口。
- OR 替代需要选择语义；一个替代受阻不能推出工件被阻塞。
- control-only、approval-only 或 soft-reservation place 可以形成 Petri
  siphon，但没有可审计的工件持有-请求证据，因此不能反向恢复 IMS 核。

## 5. 七篇全文审计后的 Petri 边界

G1 全文审计把 `L30-L35` 与 `B05` 纳入比较器，但不改变本项目定理真值。

- `L30` 的 finite-capacity S3PR/ENS3PR resource-configuration 结论只能作为
  liveness-preserving 初始资源标识的保守充分基线。它不授权把本项目的
  BIX/P3e 阈值改写成一般 finite-capacity S3PR 的 exact reachable iff
  threshold，也不替代 IMS 可达前缀证据。
- `L31` 的 S4PR CRP 给出 marking-level partial-deadlock iff certificate；
  但 CRP 候选 marking 的可达性仍由 SBA/合法 firing-sequence 层检查，且
  复杂性为 NP-hard。对 IMS 的使用必须先证明 S4PR overlap map，再把
  unreachable structural/algebraic candidate 作为拒绝边界保留。
- `L32/L33` 的 USPN/UniPN recorder-place transformations 不改变原
  transition enabling，并可把原网 trace 嵌入到 instrumented counter
  state；但这不自动给出 IMS operational/Petri plant 证明，也不自动关闭
  固定原 IMS 目标到 recorder target 时的 existential/fixed-count 量化。
- `L34/L35` 的 BA/SBA 法检查给定 NIS `X` 是否存在 legal firing sequence。
  `O(n*n1*(c*m+n^2))` 是依赖 firing-count/marking 参数的伪多项式或
  参数化界，不得写成标准 bit-polynomial reachability algorithm for IMS。
- `B05` 的 compressed maximally permissive supervisor 依赖完整 reachability
  graph、legal/first-met-bad marking covering 与 NP-hard MCPP，只能作为小
  显式状态/PN overlap 的 permissiveness comparator；不能作为紧凑 IMS 的
  可扩展控制定理。

由此，任何后续 Petri 比较必须同时记录四类 refusal/obligation boundary：

1. 原 IMS operational 到 source plant Petri 的语义证明是否先独立完成；
   recorder transformation 不能替代这一步，还须另证原目标固定后
   recorder count 的存在量化和固定计数量化是否一致；
2. CRP 与本项目 closed blocking core 的重叠是否已经限制到 S4PR marking
   语义，且候选 marking 是否有 executable prefix；
3. structural/algebraic candidate 与 reachable IMS deadlock 的差距是否被
   显式合法 firing/event witness 关闭；小确认模型以完整 BFS/LTS 穷举为
   独立基准，SBA 仅作比较器；
4. resource-configuration theorem 是 exact iff threshold、sufficient
   liveness condition，还是 comparator-only baseline。

## 6. 枚举实现

`ims_deadlock.petri` 实现：

- `build_wait_snapshot_bridge(model,state,certificate)`：验证 `IMS-SIP^1`
  条件并构造 diagnostic net。
- `is_siphon(net, places)`：ordinary siphon 谓词。
- `minimal_empty_siphons(net)`：小规模确定性枚举 inclusion-minimal empty
  siphons。
- `certificate_with_wait_snapshot_bridge(...)`：返回附带
  `corresponding_siphon` 和 `bridge_status` 的证书副本。

验证只作为证明审计；它不替代 P2c 的数学证明。
