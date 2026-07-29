# 控制层：监督、干预与风险预算

本文件定义控制理论目标。P5 已关闭严格有限、全观测、显式 LTS 上的
最大许可 nonblocking supervisor 基准；结构干预、风险预算与性能 Pareto
结论仍为拟证明。

## 1. 可控与不可控事件

状态：定义。

可控事件：

- release 授权；
- dispatch；
- transport choice；
- reservation acquire/redeem/cancel；
- 路线选择或重路由中在首篇允许的静态选择。

不可控事件：

- service completion；
- transport completion；
- 已承诺零时间闭包中的强制整理事件；
- 必要时的环境到达，但首篇排除无限外生到达。

加工完成不可控，且不等同资源释放。

## 2. 最大不变安全集与 game predecessor

状态：P5 项目内已证明（严格有限、全观测、显式 LTS）；风险约束扩展拟证明。

令 `Bad` 包含死锁状态、不可接受准死锁或违反风险预算的状态。对状态 `s`，记：

- `Post_u(s)`：所有 enabled uncontrollable events 及其闭包后的稳定后继；
- `Post_c(s,a)`：选择可控事件或可控动作 `a` 后的稳定后继集合；
- `A_c(s)`：supervisor 可启用的可控动作集合；
- `Marked`：完成状态集合，通常等于 `F`，或论文中显式定义的完成标识集合。

安全 game predecessor 候选为：

`Pre(Y) = {s notin Bad : Post_u(s) subset Y and (s in Marked or Post_u(s) nonempty or exists a in A_c(s), Post_c(s,a) subset Y)}`。

固定点：

1. `Y_0 = S_st \ Bad`。
2. `Y_{k+1} = Y_k cap Pre(Y_k)`。
3. `Y_*` 为候选最大不变安全域。

关键边界：

- 若存在 enabled uncontrollable successors 且全部留在 `Y`，状态不能仅因没有 controllable choice 被删除。
- 若没有任何不可控后继，则 supervisor 至少需有一个可控动作保持在 `Y`，除非 `s in Marked`。
- nonblocking 版本还必须在 `Y_*` 内检查 coaccessibility：每个保留状态存在一条 admissible path 到 `Marked`。
- “进展”不能作为未定义逃生条款；若需要 fairness 或 livelock 排除，必须另列假设。

证明义务：证明所有不可控后继闭合、marked/coaccessible 条件成立，并证明删除规则不多删最大许可行为。

## 3. 最大许可 Nonblocking Supervisor

状态：Ramadge-Wonham 文献基线 + P5 项目内已证明（严格受限显式 LTS）。

在有限 LTS 中，标准 nonblocking supervisor 应保留所有仍可到 marked completion 的安全行为，并禁用必要的可控事件。IMS 迁移时必须：

- 在闭包归一化状态上计算；
- 对不可控 service/transport completion 闭合；
- 区分策略停滞和结构死锁；
- 输出被禁用事件及其证书。

## 4. 最小结构干预

状态：拟证明。

候选干预包括：

- 增加或重分配缓冲容量；
- 增加 AGV 或交接位容量；
- 加硬预约、限制软预约或改预约顺序；
- 删除或断开回流路线；
- 施加资源获取偏序。

命题边界：

覆盖全部最小封闭阻塞核可写成 hitting set 只有在以下条件成立时才可用：

- core 全集已完备枚举或证明覆盖；
- 每个干预确实击中对应 core；
- 干预不会创造新 core；
- 干预后路线仍满足完成可达性。

否则必须采用“干预-重枚举-反例生成”的迭代流程。

## 5. 概率风险预算

状态：拟证明。

概率控制目标：

`h_i^pi <= epsilon`，同时优化吞吐、工期或 WIP 代价。

候选输出：

- 风险预算 `epsilon`；
- supervisor 或策略 `pi`；
- 死锁概率；
- 平均吸收时间；
- 吞吐/工期损失；
- Pareto 支配关系；
- 递归可行性证明或保守界。

不能把 Doob-`h` 条件路径动力学当成控制策略。它只提供高风险路径解释和稀有事件采样目标。

## 6. 验证输出

状态：计算验证。

`prove` 与 `verify-case` 需要输出：

- 安全域状态数；
- 被禁用事件列表；
- 每个禁用事件对应的死锁核或 nonblocking 失败证据；
- 不可控闭合检查；
- marked/coaccessibility 检查；
- 干预前后 core 集合变化；
- 若产生新 core，写入 `COUNTEREXAMPLE_LEDGER.md`。
