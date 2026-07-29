# 概率层：IMS-CTMC、Committor 与 Doob-h

本文件只覆盖有限 CTMC 或显式 PH 展开后的有限状态模型。一般非指数时间不得直接使用本层方程。

## 1. 竞争吸收类

状态：定义。

在闭包归一化稳定状态集合上，令：

- `D` 为死锁吸收类；
- `F` 为完成吸收类；
- `U = S_st \ (D union F)` 为尚未分类的非吸收集合。

不能先验把 `U` 全部称为暂态。必须先做闭合类分解：

- `S_T`：从这些状态出发以概率 1 命中 `D union F` 的 transient-to-absorption 状态；
- `R_c`：不属于 `D union F` 的其它 closed/recurrent/livelock 类；
- `B`：若存在从初始可达区域通向 `R_c` 的状态，需要作为边界处理或单独坏类。

若控制策略或模型允许从死锁状态恢复，则该状态不属于本层的死锁吸收类，而应建模为恢复控制问题。

核心吸收假设 `A_abs`：从所有分析范围内可达的非 `D/F` 状态，以概率 1 命中 `D union F`。只有在 `A_abs` 成立，且 `S_T` 等于分析范围内非 `D/F` 状态时，下列 `Q_{S_T,S_T}` 线性系统才可直接用于全域 committor 与平均吸收时间。

## 2. 生成元

状态：定义。

有限 CTMC 生成元 `Q` 满足：

- `q_ij >= 0` for `i != j`；
- `q_ii = -sum_{j != i} q_ij`；
- `D` 与 `F` 中状态吸收，或在分块前折叠为吸收类；
- 非指数时长必须 PH 展开后才可进入 `Q`。

在 `A_abs` 成立或已经限制到 `S_T` 后，分块：

`Q = [[Q_{S_T,S_T}, Q_{S_T,D}, Q_{S_T,F}], [0,0,0], [0,0,0]]`。

若 `R_c` 非空，必须执行边界处理：

- 若 `R_c` 是不可接受 livelock 或 terminal block，将其并入新的坏吸收类并重新定义 committor 目标；
- 若 `R_c` 是可接受循环行为，则死锁 committor 只在能命中 `D union F` 的 basin 上解释，报告从初始状态进入 `R_c` 的概率；
- 若模型意图证明几乎必然完成/死锁竞争，则 `R_c` 非空直接否定该吸收假设。

## 3. 死锁 Committor

状态：P4 项目内已证明（严格有限 CTMC）；L23 提供离散 committor 背景，
L28 提供条件跳过程全文锚点。

死锁 committor `h_i = P_i(tau_D < tau_F)` 满足边界：

- `h_i = 1` for `i in D`；
- `h_i = 0` for `i in F`；
- `Q_{S_T,S_T} h_{S_T} = - Q_{S_T,D} 1` for `i in S_T`。

解释：`h_i` 是先到达死锁而不是完成的概率，不是结构死锁存在性。

## 4. 平均吸收时间

状态：P4 项目内已证明（严格有限 CTMC）。

到任一吸收类的平均时间 `tau_i` 满足：

在 `A_abs` 成立或限制到 `S_T` 后，到 `D union F` 的平均时间 `tau_i` 满足：

`Q_{S_T,S_T} tau_{S_T} = -1`。

若 `R_c` 可达且没有并入吸收目标，无条件平均吸收时间可能为无穷或不定义。

若只关心条件于死锁的时间，需要在 Doob-`h` 条件链或条件分布下重新计算，不能直接把无条件 `tau` 当作死锁时间。

## 5. 参数敏感性

状态：P4 项目内已证明；要求参数邻域内分区固定且速率可微。

对参数 `theta` 微分 committor 方程，得到候选敏感性线性系统：

`Q_{S_T,S_T} partial_theta h_{S_T} = - (partial_theta Q_{S_T,S_T}) h_{S_T} - (partial_theta Q_{S_T,D}) 1`。

证明义务：

- `Q_{S_T,S_T}` 在暂态到吸收子空间可逆；该可逆性依赖 `A_abs` 或已完成 closed-class 分解。
- 参数扰动不改变状态划分，或显式处理状态划分变化。
- 速率参数可微。

## 6. Doob-h 条件化

状态：P4 项目内已证明（严格有限竞争吸收 CTMC）；L28 为全文迁移锚点。

对 `h_i > 0` 的暂态状态，条件于先达 `D` 的跳转率为：

`q^h_ij = q_ij h_j / h_i` for `i != j`。

对角元：

`q^h_ii = - sum_{j != i} q^h_ij`。

边界：

- 不在 `h_i = 0` 的状态上定义该比值。
- Doob-`h` 变换解释条件高风险路径和稀有事件采样目标分布。
- Doob-`h` 不是控制器；它不告诉系统应禁止哪些事件。
- `Corstanje and van der Meulen (2025)` 现在给出可公开核验的 conditioned CT jump-process/change-of-measure 主线：
  `Eq. 3.1` 给出 adjusted intensities，`Eq. 3.3` 给出生成元形式，Appendix D 解释 change of generator。

## 7. 来源使用边界

状态：来源边界。

- Markov jump transition path theory 与离散 committor 背景可引用 Metzner et al. 2009，DOI `10.1137/070699500`，但该来源按当前核验边界只支撑 ergodic Markov jump process TPT/discrete committor background，不能直接支撑 absorbing IMS theorem。
- 本文件中的 committor、平均吸收时间、敏感性和 Doob-`h` 公式在项目内标为标准有限 CTMC 方程/项目推导；吸收 CTMC 条件化主来源现在由 `Corstanje and van der Meulen 2025` 提供可公开核验的 change-of-measure 基线，但把它迁移为 IMS absorbing boundary theorem 仍需单独证明。
- Narahari 等制造系统吸收 Markov 基线只能按已核验摘要和可读内容边界使用：吸收死锁、平均时间、平均产出和暂态分布是迁移线索；具体定理需全文核验后进入证明依据。

## 8. 验证输出

状态：计算验证。

`quantify` CLI 需要输出版本化 JSON：

- 状态数、`D/F/S_T/R_c` 大小；
- `A_abs` 是否成立；若不成立，报告 `R_c` 的可达概率和处理方式；
- `Q` 的构造摘要；
- `h`、`tau`；
- 线性系统残差；
- 条件路径统计；
- 参数敏感性；
- 与独立 DES 仿真的置信区间对照；
- 所用速率和随机流清单。
