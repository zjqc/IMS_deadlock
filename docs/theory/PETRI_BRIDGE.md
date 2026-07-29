# Petri 网与 S3PR 桥接

本文件限定 Petri 网桥的可用范围，避免把经典 S3PR/siphon 结果无条件套到 IMS-RAS。

## 1. 构造目标

状态：拟证明。

从 `IMS-RAS` 的闭包归一化 LTS 构造有界 Petri 网 `N=(P,T,F,W,M0)`，使：

- 每个稳定 IMS 状态 `s` 有标识 `phi(s)`；
- 每个可观察事件 `e` 对应一个或一组 Petri transition；
- 在可投影子类中，`s ->e t` 当且仅当 `phi(s) -> phi(t)`；
- 若存在不可逆投影，只主张 trace inclusion 或 sound abstraction，不主张双模拟。

## 2. Place 设计

状态：拟证明。

候选 place 类别：

- 工件阶段 place：表示 `stage_s(j)`。
- 机器持有 place：表示工件占有机器。
- 输入/输出缓冲 place：表示缓冲 token 剩余或占用。
- AGV 持有 place：表示装载、空车占用、站点等待。
- 预约 token place：硬预约下可作为守恒资源；软预约需额外 overbook/claim place。
- blocked place：显式表示 `blocked_complete`、`blocked_unload` 或等待运输状态。

## 3. 事件对应

状态：拟证明。

候选 transition 类别：

- dispatch：可控，获取机器/输入缓冲或预约。
- service completion：不可控，只移动到完成待卸载或 blocked 状态，不释放资源。
- unload/handoff/release：可控或语义授权事件，释放机器或 AGV。
- transport start/choice：可控，获取 AGV/路线/预约。
- transport completion：不可控，进入站点或 blocked-unload。
- reservation acquire/redeem/cancel：可控或闭包事件，视预约规则而定。

## 4. 经典 S3PR 可用条件

状态：文献基线 + 拟证明。

S3PR/siphon 控制可作为基线的条件包括：

- 资源持有与路线阶段可由普通 place 保守表示；
- 每个加工/运输步骤有明确 acquire/release；
- 不存在未建模软预约过售；
- 闭包不会隐藏影响 liveness 的可见释放；
- AGV、缓冲和预约若参与死锁，必须进入 Petri 资源集合。

若以上条件不满足，只能把 S3PR 作为启发或投影基线。

## 5. 超出经典 S3PR 的 IMS 语义

状态：反例。

以下语义通常超出直接 S3PR：

- `blocked_complete` 或 `blocked_unload` 使完成后继续占有机器/AGV。
- 硬预约需要未来占用 token 与当前物理占用并存。
- 软预约允许 overbook，破坏简单守恒 place。
- 非合流零时间闭包依赖优先级或排序。
- AGV 路径/站台/交接位引入运输资源层。

## 6. Siphon 桥接候选

状态：拟证明。

候选命题：

在满足 Petri 可投影条件的 IMS 子类中，最小封闭阻塞核对应某个最小致死 siphon；反向成立需要 siphon 中每个失标 place 都可恢复为工件-资源阻塞证据。

证明方向：

- `core -> siphon`：从被封闭资源需求构造不会被外部 transition 重新标识的 place 集。
- `siphon -> core`：从失标 siphon 追踪到被阻塞工件和不可释放资源。

边界：

- 若 siphon 只含控制或预约辅助 place，可能没有实际工件等待证据。
- 若 IMS 有 soft reservation，core 可能无法在普通 Petri 守恒网中表达。

## 7. 枚举验证

状态：计算验证。

小模型验证应输出：

- IMS 状态数、Petri 可达标识数；
- `phi` 是否单射；
- trace inclusion 或 equivalence 结果；
- 最小 siphon 列表；
- 最小 closed core 列表；
- 匹配失败的最小状态与原因。
