# IMS Deadlock 项目创新性、顶刊适配、投稿成熟度与局限评估

> 评估日期：2026-08-07<br>
> 评估对象：当前仓库中已经证明、实现并由冻结案例支撑的成果<br>
> 文章核心状态：`tier_a_dual_route_closure`<br>
> 原始 G6-B 状态：`OPEN_PENDING`<br>
> 评估原则：区分“项目内已闭合”“论文逻辑可自洽”“可正式投稿”“达到顶刊门槛”四个不同层级

## 执行结论

**当前成果已经可以写成一篇逻辑自洽、可公开为 working paper／preprint 的理论—方法稿，但还不建议直接投稿顶级期刊。**

当前最成熟的论文核心不是“一个覆盖所有制造死锁的通用算法”，而是：

```text
capacity-aware IMS semantics
  -> global closed-core certificate
  -> two typed local-admission routes
  -> disjoint global/local/completion first-hit target
  -> certified finite CTMC
  -> exact/DES same-target constructive closure
```

这个核心具备明确研究问题、形式定义、定理、正例、反例、解析桥和冻结数值证据，已经达到“文章主逻辑成立”的程度。限制它直接进入顶刊的主要因素不是理论主线未闭合，而是：

1. 六案例仍以最小构造和边界控制为主，缺少规模性与制造现实性；
2. 尚未与近期 Petri 网、状态空间、优化／SAT 或其它死锁方法做统一实验基线比较；
3. 没有真实产线、数字孪生校准或行业数据；
4. 最新文献定位与逐项差异表还需扩充；
5. 项目已有 P1–P6 很宽，但如果全部塞进一篇稿件，主贡献会被稀释；
6. 原始 G6-B 保持 `OPEN_PENDING`，不能在投稿中暗示更广门已经通过。

**最合适的顶级目标是 IEEE Transactions on Automation Science and Engineering（T-ASE），但应作为完成扩展实验后的首选，而不是现在立即投。** Automatica 与 IEEE Transactions on Automatic Control（TAC）只适合在进一步提升一般理论意义、算法结果和控制论关联后尝试。IEEE Transactions on Systems, Man, and Cybernetics: Systems（TSMC-S）、Journal of Manufacturing Systems（JMS）和 International Journal of Production Research（IJPR）是高水平备选；Computers & Industrial Engineering（C&IE）在补足方法对比和工业工程评价后更现实。

---

## 1. 当前成果成熟度快照

### 1.1 已经闭合的成果

| 成果层 | 当前状态 | 证据 |
| --- | --- | --- |
| `IMS-RAS^CW` 有限稳定语义 | 已定义并有实现契约 | 集合值闭包、容量 ontology、BAS／AGV／预约边界 |
| P1 有限 LTS 表示 | 项目内已证明 | 1-safe one-place-per-state reachability net |
| P2 全局容量死锁证书 | 项目内已证明 | 覆盖封闭核双向证明与反例边界 |
| P2c Petri 桥 | 严格子类已证明 | `IMS-SIP^1` wait-snapshot empty-siphon 对应 |
| P3 偏序排除 | 受限责任链子类已证明 | chain-decomposable strict-precedence |
| P3d/P3e 阈值族 | 已证明并机检 | BIX1-SAT、BIX2-PERSIST ring/DAG |
| P4 CTMC 概率层 | 有限认证域内已证明 | committor、mean time、sensitivity、Doob-\(h\) |
| P5 监督器 | 显式有限全观测域已证明 | UPre／CoAcc 下降不动点 |
| P6 复杂性 | 受限子类与显式图边界已证明 | NP-complete 子类、显式图多项式上界 |
| 局部坏首达理论 | 已形成双路线闭环 | A2b + complete-LTS fallback |
| Article-core 案例 | 六案例已冻结执行 | 正例、反例、优先级和 \(1/3\) 桥 |
| Exact／DES | 18/18 compatible | 最大误差 0.0030924479 |
| 可复现性 | 较高 | scope lock、manifest、证书、图形脚本、测试 |

### 1.2 尚未闭合或不应宣称的成果

- 一般 IMS 与 S3PR／结构化 Petri 网的同构或双模拟；
- 一般多容量极小核与极小致死虹吸的双向对应；
- 一般紧凑 `IMS-RAS^CW` 安全／监督可行性的精确复杂性完备分类；
- 风险预算 supervisor 的递归可行性、最优性或 Pareto 定理；
- 软预约、非指数时间、故障、抢占、动态插单与无限到达；
- 生产规模外部验证和实际部署效果；
- 原始 G6-B、G6-C、G6-D、G6-E 的全面确认。

---

## 2. 创新性成果分解

### 2.1 创新 1：保留制造释放语义的容量感知统一模型

项目把机器、有限缓冲、AGV／运输、交接位和硬预约 token 放入同一资源分配语义，同时严格区分：

- 物理持有与预约持有；
- future claim 与独立 token resource 两种 ontology；
- service completion 与真正 resource release；
- zero-time closure 前状态与稳定状态；
- OR-of-AND capacity-ready alternatives。

**创新价值：** 它减少了把 blocked-complete 当释放、把硬预约重复计数、把非容量 guard 当容量不足等常见语义错误，为后续证书与概率层提供一致对象。

**原创性强度：中等偏强。** 单个概念并非全新，但把这些要素组成可审计、可执行且与证书／概率共享的形式语义，是项目的实质性方法贡献。

### 2.2 创新 2：从“有环”升级为可审计的容量封闭核

封闭阻塞核不只记录 wait-for cycle，而是同时量化：

1. 每个工件的所有合法 alternative；
2. 每个 alternative 的至少一个容量缺口 witness；
3. 解释缺口的实际 holder／硬预约数量；
4. holder 的释放依赖；
5. 核的覆盖性和 inclusion minimality；
6. policy stall、calendar-empty 和非资源边界的排除。

**创新价值：** 对多容量、AND 请求、AGV 和预约系统，比简单环或 SCC 更接近实际死锁证据对象；证书还能输出可复核 provenance。

**原创性强度：强，但需文献差异表加固。** 顶刊投稿前必须逐项对比近期 capacity-aware Petri、RAS deadlock certificate 和 resource-allocation safety 工作，明确哪些条件已有近似形式，哪些组合与双向证明是本文新增。

### 2.3 创新 3：严格分离 predicate、terminal SCC 与 stopping target

项目明确指出：

- \(D_{\mathrm{global}}\) 是 plant-level operational predicate；
- \(D_{\mathrm{local}}\) 是经健全性准入的 stopped-process bad first-hit set；
- `R_livelock`／`R_terminal` 才是剩余 plant graph 的 terminal SCC 类；
- “局部坏状态还有 outgoing plant arc”并不否定 first-hit 事件已经发生。

**创新价值：** 这是文章最清晰的概念贡献之一。它修复了把“局部不可恢复失效”错误称为“全系统 terminal class”的范畴混淆，使结构理论与 competing-risk 概率建模能够连接。

**原创性强度：强。** 需要在外部文献中谨慎检索相近的 partial deadlock、local deadlock、quasi-deadlock 和 absorbing-event 表述，但项目给出的 typed admission + stopped-process distinction 具有明显论文辨识度。

### 2.4 创新 4：局部坏首达的两条有类型准入路线

两条路线不是相互竞争的万能算法，而是类型明确的证明接口：

- **A2b：** 对 request-closed 子类给出结构可迁移的充分定理；
- **Complete LTS：** 对一般有限 TransitionSpec 给出具体模型的 completion-nonreachability 证明；
- **Bypass refusal：** 一旦存在到完成的路径，候选必须拒绝；
- **Global precedence：** 同一状态只计入一个停止类别。

**创新价值：** 既避免把理论范围收得过窄，也避免把结构候选无限外推。失败响应本身是方法的一部分。

**原创性强度：很强，是当前最适合做论文标题和摘要主贡献的成果。**

### 2.5 创新 5：吸收域认证先于概率计算

项目不把“存在到目标的路径”误当作“几乎必然吸收”。它在完整正速率 stopped graph 中识别未选择闭 SCC 及其反向 basin，定义认证暂态域 \(S_T\)，然后才求解：

\[
Q_{TT}h=-Q_{TD}\mathbf1,
\qquad
Q_{TT}\tau=-\mathbf1.
\]

**创新价值：** 把结构拒绝、目标身份、rate manifest、committor residual 和 DES stopping hash 连接为一条可审计概率协议。

**原创性强度：中等偏强。** 线性方程本身是标准有限 CTMC 结果；创新不在“重新发现 committor”，而在 IMS 目标认证、未选择闭类拒绝与同目标执行契约。

### 2.6 创新 6：正例—反例—概率桥的冻结闭环

六案例不是仅展示成功结果，而是预先配置：

- 两条准入路线的正例；
- 一个完成旁路负控制；
- 一个全局／局部重复计数负控制；
- 一个解析 \(1/3\) 非退化桥；
- 18 个预声明 exact／DES 比较单元。

**创新价值：** 它把可证伪边界纳入论文设计，避免只展示有利案例。冻结 seed、容差和 evidence manifest 又避免 post-hoc 调参。

**原创性强度：作为研究方法与可复现性贡献较强；作为工业实验贡献仍弱。**

### 2.7 创新 7：表示敏感的复杂性与控制边界

项目同时保留两种不同复杂性对象：

- 紧凑模型中的 `IMS-SU-SAFE` NP-complete；
- 显式 LTS 上 P5 fixed point 多项式；
- 完整显式 supervisor 可能因状态展开而指数大。

**创新价值：** 防止把“显式图算法很快”误写成“紧凑制造问题整体多项式”，也防止无证明地贴更强复杂性标签。

**原创性强度：中等。** 更适合作为项目第二篇理论／控制论文或当前稿件的支撑性质，不宜与局部 first-hit 主贡献争夺中心位置。

---

## 3. 哪些内容不是创新，必须主动降调

以下内容是经典基础或常见结构，论文应明确引用而非包装成原创：

1. circular wait、wait-for graph 和简单资源环；
2. 删除环中一条回流边形成 DAG 的基本思想；
3. Petri net siphon、deadlock prevention 和 monitor control 的一般框架；
4. Ramadge–Wonham supervisory control 的一般理论；
5. 有限 CTMC committor、mean hitting time 与 Doob-\(h\) 的标准方程；
6. Gillespie 路径抽样；
7. Hoeffding concentration inequality；
8. one-place-per-state 对有限 LTS 的朴素 Petri 表示。

项目的贡献应表述为“这些基础在明确 IMS 语义、证书、准入和冻结执行契约中的新组合与受限定理”，而不是声称这些基础概念本身由项目首次提出。

---

## 4. 当前是否可以投稿

### 4.1 四级成熟度判断

| 层级 | 判断 | 说明 |
| --- | --- | --- |
| 内部科研主线 | **已达到** | 理论、案例、反例和数值对象已闭合 |
| Working paper／preprint | **已基本达到** | 两份完整稿、图、证据和参考文献已具备；仍需作者信息与英文润色 |
| 一般同行评审期刊 | **接近但不建议立即投** | 至少还需系统文献比较、方法基线和更大案例 |
| 顶级／旗舰期刊 | **当前未达到** | 实证广度、规模性、基线、现实性和最新文献定位不足 |

### 4.2 为什么不是“理论闭环了就能立即投顶刊”

顶刊评审通常同时判断：

- 问题是否重要且与现有文献差异充分；
- 定理是否具有足够一般性或方法影响；
- 算法是否可扩展；
- 实验是否与最强相关方法公平比较；
- 案例是否体现真实自动化／制造价值；
- 结论是否超出人为构造的最小样例；
- 论文是否把失败边界和适用范围说清楚。

当前项目在“理论对象清楚、证据可追溯、边界诚实”上较强，在“外部比较、规模与现实性”上明显不足。因此正确策略是保留理论核心，再补期刊要求的验证层，而不是继续无休止重审已经闭合的基础代码。

---

## 5. 顶刊与高水平期刊适配

本节不使用易变的影响因子或分区数字，只依据期刊官方 scope、审稿重点与本文成果形态判断。

### 5.1 第一优先：IEEE Transactions on Automation Science and Engineering

- 官方范围：[T-ASE Information for Authors](https://www.ieee-ras.org/publications/t-ase/information-for-authors-t-ase/)
- 投稿检查：[T-ASE Author Checklist](https://www.ieee-ras.org/publications/t-ase/information-for-authors-t-ase/author-checklist-for-papers-submitted-to-ieee-t-ase/)
- Note to Practitioners 要求：[T-ASE FAQ](https://www.ieee-ras.org/publications/t-ase/frequently-asked-questions/)

**适配度：高。** T-ASE 接受自动化科学中的模型、方法、系统和案例研究；制造、系统建模、风险和自动化决策都与本项目契合。

**当前成熟度：不宜立即投稿。**

**至少需要补：**

1. 近期 deadlock／automation science 方法的系统比较；
2. 至少 2–4 个基线：cycle/SCC、适用域内 siphon、complete-LTS truth、一个现代优化／控制方法；
3. 多规模、多容量、多产品和运输／预约混合 benchmark；
4. 一个接近真实制造岛的详细案例与 KPI；
5. runtime、state count、certificate count 和 failure/refusal scaling；
6. 面向工程人员的 Note to Practitioners；
7. 明确“为什么 typed local first-hit 会改变自动化风险决策”。

**投稿前景：** 如果上述内容补齐，T-ASE 是最合理的旗舰目标。

### 5.2 远期理论目标：Automatica

- 官方范围：[Automatica journal page](https://www.sciencedirect.com/journal/automatica)

**适配度：中等。** Automatica 强调系统与控制中具有持久理论／方法价值的成果。当前稿件的 stopping-set ontology 和吸收域认证有控制理论潜力，但案例与主要表述仍偏制造专用。

**当前成熟度：低。**

**若要投，需把主贡献提升为更一般结果：**

- 把 typed admission 抽象到一类有限 DES／Markov jump systems；
- 给出比案例特定 LTS 更强的可组合／模块化充分条件；
- 建立 supervisor 与 first-hit risk 的非平凡联系；
- 提供算法复杂性、近似或可扩展性定理；
- 证明该方法相对已有 DES／stochastic reachability 理论的明确新增性。

仅以六个制造构造案例投稿 Automatica，理论影响力证据不足。

### 5.3 远期理论目标：IEEE Transactions on Automatic Control

- 官方范围：[IEEE TAC](https://ieeecss.org/publication/transactions-automatic-control)
- 作者与 prescreening 信息：[TAC Author Information](https://ieeecss.org/publication/transactions-automatic-control/author-info)

**适配度：中低。** TAC 强调自动控制理论基础和显著的方法创新，并在预审中关注新颖性与重要性。

**当前成熟度：低。**

**主要缺口：**

- 当前主定理是受限 IMS 子类和 model-specific fallback 的组合，尚未展示足够一般的控制理论影响；
- P5 主要是有限 state-based supervisor 基准，接近经典框架的受限实例；
- 风险预算控制、递归可行性和最优性仍未证明；
- 案例难以证明理论普适影响。

除非后续关闭“风险约束最大许可 supervisor／stochastic safety control”一类更强定理，否则不建议 TAC 作为当前稿件目标。

### 5.4 高水平系统目标：IEEE Transactions on Systems, Man, and Cybernetics: Systems

- 官方范围：[IEEE TSMC: Systems](https://www.ieeesmc.org/publications/transactions-on-smc-systems/)
- 作者信息：[Information for Authors](https://www.ieeesmc.org/publications/transactions-on-smc-systems/information-for-authors/)

**适配度：中高。** 期刊关注系统工程、复杂系统建模和仿真；官方作者信息也强调实验或充分仿真支撑。

**当前成熟度：中低。**

**需要补：** 更大系统、多场景仿真、基线比较、系统级消融与制造／物流解释。若扩展不够顶刊级但系统性较强，TSMC-S 是合理目标。

### 5.5 高水平制造目标：Journal of Manufacturing Systems

- 官方范围：[Journal of Manufacturing Systems](https://www.sciencedirect.com/journal/journal-of-manufacturing-systems)

**适配度：中高。** JMS 关注制造系统层面的基础与应用研究，项目的 finite buffers、AGV、blocked-unload 和 risk modeling 与其主题相关。

**当前成熟度：中低。**

**主要缺口：** 真实或高保真制造系统案例、制造 KPI、近期制造系统方法对比和可执行设计建议。若加入数字孪生式案例与 throughput／WIP／deadlock-risk 权衡，JMS 适配度会显著上升。

### 5.6 高水平生产研究目标：International Journal of Production Research

- 官方期刊页：[International Journal of Production Research](https://www.tandfonline.com/journals/tprs20)

**适配度：中等。** IJPR 接受面向生产／物流决策问题的基础方法与现实应用。

**当前成熟度：中低。**

**主要缺口：** 当前文章强调语义和定理，生产决策变量与管理意义偏弱。需要加入 buffer／AGV／reservation intervention、性能代价和实际生产场景。

### 5.7 更现实的工程方法目标：Computers & Industrial Engineering

- 官方范围：[Computers & Industrial Engineering](https://www.sciencedirect.com/journal/computers-and-industrial-engineering)

**适配度：中高。** C&IE 关注面向工业工程问题的计算方法。

**当前成熟度：中等偏低。**

如果补充算法 benchmark、规模性、工业工程指标和决策实验，而不追求更一般控制定理，C&IE 可能比 Automatica／TAC 更现实。它仍不是“现在原样即可投”，但补齐路径更短。

### 5.8 期刊选择总表

| 期刊 | 当前适配 | 当前可投性 | 达标所需的核心升级 |
| --- | --- | --- | --- |
| IEEE T-ASE | 高 | 否 | 基线 + 规模 + 现实案例 + Note to Practitioners |
| Automatica | 中 | 否 | 更一般理论、算法与控制意义 |
| IEEE TAC | 中低 | 否 | 新的风险控制／监督定理与广泛影响 |
| IEEE TSMC-S | 中高 | 否 | 系统级大规模仿真与比较 |
| JMS | 中高 | 否 | 高保真制造案例与 KPI |
| IJPR | 中 | 否 | 生产决策与应用价值 |
| C&IE | 中高 | 接近但仍否 | 计算 benchmark、规模性、工业指标 |

---

## 6. 推荐的论文拆分与定位

### 6.1 论文 A：当前最成熟主稿

**建议题目方向：**

> Local Deadlock as a Stopping Event: Two Sound Admission Routes and a Constructive Finite-Case Closure for Integrated Manufacturing Resource-Allocation Systems

**核心内容：**

- `IMS-RAS^CW` 中与 local first-hit 必需的语义；
- global certificate 作为前置；
- A2b 和 complete-LTS 两条路线；
- global precedence 与吸收域；
- 六案例与 exact／DES；
- 负证据和适用边界。

**不应过度装入：** P5 完整 supervisor、P6 复杂性全文、所有 BIX 阈值和所有 Petri bridge 细节。它们可作为背景性质、附录或后续论文。

### 6.2 论文 B：容量证书与结构修复

**潜在主线：**

```text
IMS-RAS^CW
  -> covering closed-core equivalence
  -> strict-precedence exclusion
  -> IMS-SIP^1 Petri bridge
  -> BIX1/BIX2 exact thresholds and paired repair
```

这篇需要更系统地与 Petri net／RAS 文献比较，并用多容量、AGV、buffer、reservation benchmark 证明证书相对 cycle/siphon 方法的增量价值。

### 6.3 论文 C：风险约束监督控制

**潜在主线：**

- P5 最大许可 nonblocking supervisor；
- P4 first-hit risk；
- 风险预算 \(h^\pi\le\epsilon\)；
- performance／risk Pareto；
- Doob-\(h\) 只作解释或重要抽样；
- 递归可行性与策略最优性。

目前风险预算、递归可行性和最优性尚未关闭，因此该论文仍是后续研究，而不是当前投稿成果。

---

## 7. 顶刊投稿前的最小充分扩展

### 7.1 文献与 novelty hardening

建立“定义／假设／输出／复杂性／案例”五维相关工作矩阵，至少覆盖：

- Petri siphon／monitor 方法；
- sequential RAS safety／deadlock avoidance；
- partial／local deadlock；
- finite-buffer／BAS／AGV deadlock；
- supervisory control；
- stochastic reachability／absorbing CTMC；
- exact 与 simulation validation。

每个创新声明都应落到“已有方法缺哪一条条件，本文多出什么可验证对象”。这一步是投稿必须，且不需要再做重型代码审计。

### 7.2 基线实验

建议建立同一案例输入上的四类基线：

1. 机器 wait-for cycle／SCC；
2. capacity-aware closed core；
3. 在 `IMS-SIP^1` 适用域内的 siphon detector；
4. complete-LTS reachability truth。

对比指标至少包括 false positive、false negative、refusal coverage、certificate size、runtime 和 peak state count。若引入外部优化／控制基线，必须使用相同 plant semantics，不能让“加工完成是否释放”等语义差异污染结果。

### 7.3 规模与多样性

不需要寻找一个覆盖所有现象的超级案例，但需要一组可解释的参数族：

- 作业数、资源数、容量、alternative 数；
- buffer／AGV／token 的组合；
- 单核与多核；
- bypass 密度；
- rate scale 与风险区间；
- state-space expansion 和 all-minimal core 数量。

建议把“逻辑案例面板”与“规模 benchmark 面板”分开。前者证明语义，后者评估计算能力。

### 7.4 现实制造案例

至少构造一个具备以下字段的高保真案例：

- 工艺路线和产品混合；
- 机器／缓冲／AGV／交接位容量；
- BAS／blocked-unload 的真实释放规则；
- 速率或加工时间校准来源；
- deadlock／completion／local failure 的工程解释；
- 对 throughput、WIP、makespan 或 tardiness 的影响；
- 一个结构干预或监督策略。

若无法取得企业数据，可以使用公开 benchmark 或明确标注的 synthetic digital-twin case；但不能称为实厂验证。

### 7.5 算法与统计

- 报告 all-minimal enumeration 的最坏情形与实际 scaling；
- 对大 LTS 使用稀疏线性求解并报告 residual；
- 若研究 rare event，引入重要抽样或 splitting，并与 naive DES 比较；
- 为 mean time／KPI 另行预声明统计协议；
- 保持 seed、stopping target 和 case denominator 冻结。

### 7.6 论文呈现

- T-ASE：加入 Note to Practitioners；
- Automatica／TAC：将制造例作为实例，突出一般系统定理；
- JMS／IJPR／C&IE：强化 manufacturing decision 与 KPI；
- 正文只保留一条中心主线，其它定理放附录或拆稿；
- 明确所有 “sufficient but not necessary”“model-specific”“not held-out” 边界。

---

## 8. 局限与不足完整清单

### 8.1 模型层

1. 有限批假设排除了无限到达和稳态生产网络。
2. 设备故障、维修、抢占和人工干预未进入主定理。
3. 软预约过售未纳入完备容量定理。
4. 非合流零时闭包虽以集合语义允许，但大规模实现与控制分析仍困难。
5. 非指数时间需要 PH 扩展或 DES；当前 CTMC 不能直接覆盖一般加工分布。
6. 模型忠实性依赖 transition registry 完备，漏事件会产生伪证书。

### 8.2 理论层

1. P2 只覆盖 capacity-mediated global operational deadlock。
2. A2b 不是局部不可完成的必要条件。
3. complete-LTS 路线是 model-specific 证明，不可升级为结构通用定理。
4. P3 对 non-chain-decomposable 聚合缺口不适用。
5. Petri bridge 的 `IMS-SIP^1` 限制很强。
6. P5 只在有限、全观测、state-based 域最大许可。
7. 一般紧凑模型复杂性只到至少 NP-hard，不是完整分类。
8. 风险约束 supervisor 尚无递归可行性和最优性证明。

### 8.3 算法层

1. 完整 LTS 可能指数增长。
2. all-minimal kernel family 最坏情况下指数大。
3. 当前没有 compositional／symbolic／partial-order reduction 的正式结果。
4. 未给出大规模稀疏 CTMC 性能上限。
5. 结构拒绝虽然科学正确，但在工程工具中可能降低 coverage，需要清楚报告拒绝率。

### 8.4 案例层

1. 六案例规模小，以逻辑见证为主。
2. 五个复用案例不是 held-out。
3. 竞争桥是人为最小 \(1:2\) hazard。
4. 缺真实制造布局、生产数据和长期运行。
5. 缺近期强基线。
6. 缺大规模、多产品、复杂交通冲突和多预约策略。
7. 原始 G6-B 广覆盖门仍未关闭。

### 8.5 数值与统计层

1. 4096 replications 足以执行当前预声明容差，但不能说明 rare-event efficiency。
2. 概率门不自动适用于 mean time、throughput 或 tail risk。
3. Exact 与 DES 共享模型和速率，不是外部独立模型验证。
4. 没有对模型参数不确定性、估计误差或校准误差传播。
5. 没有多场景泛化或 out-of-distribution 评估。

### 8.6 论文与发表层

1. 需要更完整的 2022–2026 相关工作核验与引用。
2. 需要英文母语级润色和符号统一。
3. 作者、单位、基金、利益冲突和 AI disclosure 尚待作者确认。
4. 需要按目标期刊页数、图表和附录规范重构。
5. 如果 P1–P6 全部作为主贡献，容易被评审认为过宽、主线不聚焦。
6. 如果把构造案例说成工业验证，会构成明显 claim inflation。

---

## 9. 主要审稿风险与应对

| 可能审稿意见 | 风险等级 | 建议应对 |
| --- | --- | --- |
| “局部死锁不是 terminal SCC” | 高 | 明确 stopped-process ontology，并展示 6 vs 4 plant/stopped arcs |
| “为什么不用 siphon／wait-for cycle” | 高 | 做适用域和多容量反例对比；保留 `IMS-SIP^1` 桥 |
| “案例太小” | 高 | 保留逻辑面板，再补独立规模 benchmark 与现实案例 |
| “CTMC 方程是标准的” | 高 | 不把方程本身称创新，突出目标认证与同目标执行协议 |
| “A2b 假设太强” | 中高 | 强调它是充分路线，并用 complete-LTS 作为另一有类型路线 |
| “完整 LTS 不可扩展” | 高 | 报告 scaling、拒绝域并研究 symbolic／compositional 扩展 |
| “DES 不是独立确认” | 中高 | 只称 within-case cross-check，不用 confirmation language |
| “历史案例 post-hoc” | 中 | 保留 discovery 身份、冻结 scope 和负证据 |
| “创新与经典 Petri／DES 工作重叠” | 高 | 做逐项 novelty matrix，主动降调经典成分 |
| “实际价值不明确” | 高 | 加制造 KPI、干预方案和 Note to Practitioners |

---

## 10. 推荐推进优先级

在不重复繁重审计的前提下，建议按以下顺序推进：

1. **锁定论文 A 的中心主张与不宣称项。**
2. **补近期相关工作差异矩阵。**
3. **实现统一基线和规模 benchmark。**
4. **构造一个高保真制造案例并连接 KPI。**
5. **按 T-ASE 结构重写英文稿和 Note to Practitioners。**
6. **用目标期刊 checklist 做一次最终而非循环式审查。**

这些任务比继续重复全仓库审计更能提升发表可能性。除非新增代码改变核心语义，不需要重跑已冻结的 article-core science；新增 benchmark 应建立独立 protocol 和新 evidence root。

---

## 11. 最终投稿判断

### 11.1 现在能否投稿

- **作为完整中文研究底稿：可以。**
- **作为 working paper／preprint：可以，在作者信息、英文版和披露补齐后。**
- **作为普通同行评审稿：技术上可以送审，但当前命中率预期不高，不建议仓促投稿。**
- **作为 T-ASE／Automatica／TAC 等顶刊稿：当前不建议投。**

### 11.2 最现实的目标路径

**首选路线：** 补齐“近期文献 + 基线 + 规模 benchmark + 高保真制造案例 + KPI／practitioner message”，然后优先投 IEEE T-ASE。

**若理论进一步增强：** 把 typed admission 与风险控制推广成一般 DES／Markov jump system 定理，再考虑 Automatica；若关闭风险约束监督控制的新理论，再评估 TAC。

**若以制造应用为主：** 增加数字孪生式案例、性能权衡和设计干预，考虑 JMS／IJPR。

**若以计算方法为主：** 强化 benchmark、scaling 与工业工程决策，考虑 C&IE。

### 11.3 当前成果的准确定位

最准确的一句话是：

> 当前项目已经获得一个具有形式语义、双路线健全准入、明确反例和 exact／DES 冻结闭环的局部坏首达理论／方法成果；它已经足以支撑一篇自洽论文，但要达到顶刊发表标准，还需要外部文献定位、强基线、规模性和制造现实性，而不是继续无限扩张基础审计。

---

## 12. 评估依据与官方链接

### 12.1 项目证据

- 完整科研链路：`docs/paper/IMS_COMPLETE_RESEARCH_CHAIN_ZH.md`
- 现有英文核心稿：`docs/paper/IMS_LOCAL_FIRST_HIT_THEORY_AND_CASES.md`
- Claim–evidence matrix：`docs/paper/ARTICLE_CLAIM_EVIDENCE_MATRIX.md`
- Scope lock：`cases/article_core/article_scope_lock_v1.json`
- Frozen evidence：`evidence/article_core/minimal_closure_v1/`
- 核心理论：`docs/theory/CORE_THEOREMS_AND_PROOFS.md`
- 局部首达理论：`docs/theory/G6_LOCAL_FIRST_HIT_AND_STOPPING_THEOREMS.md`

### 12.2 期刊官方来源

- [IEEE T-ASE Information for Authors](https://www.ieee-ras.org/publications/t-ase/information-for-authors-t-ase/)
- [IEEE T-ASE Author Checklist](https://www.ieee-ras.org/publications/t-ase/information-for-authors-t-ase/author-checklist-for-papers-submitted-to-ieee-t-ase/)
- [Automatica](https://www.sciencedirect.com/journal/automatica)
- [IEEE Transactions on Automatic Control](https://ieeecss.org/publication/transactions-automatic-control)
- [IEEE TSMC: Systems](https://www.ieeesmc.org/publications/transactions-on-smc-systems/)
- [Journal of Manufacturing Systems](https://www.sciencedirect.com/journal/journal-of-manufacturing-systems)
- [International Journal of Production Research](https://www.tandfonline.com/journals/tprs20)
- [Computers & Industrial Engineering](https://www.sciencedirect.com/journal/computers-and-industrial-engineering)
