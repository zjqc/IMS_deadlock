# IMS Deadlock Gate Roadmap

## 2026-08-05 Repository-Publication Closeout

PRs #3 through #9 are merged into `main` in dependency order with merge
commits. The exact closeout baseline is commit
`1f87f9d34d3b6f29812d9b904e2ba5ec58d8643e`, tree
`05844c0e72f18b6de7ebb984a6397a0896e0580b`; the authoritative Windows primary
checkout was clean and synchronized `0/0`. Older draft/unmerged/no-merge
statements are historical only. This documentation-only successor records the
closeout and must resolve its own commit from live Git history.

Final stack verification was `2421 passed, 2 skipped in 888.15s` on a head with
the same tree, followed by post-merge `2 passed in 1.07s` and green Ruff,
format, strict mypy, and diff checks. Both PR #7 review threads were resolved;
no open PR remained at the #9 closeout baseline.

This closeout records count-level validation evidence only. The originating
PR #9 body and repository-publication closeout discussion retain the run and
review evidence; this successor does not claim a new CI artifact or a new
full-suite run at the baseline above.

This is repository publication only. G6-B remains `OPEN/PENDING`; G6-C/D/E and
the paper gate remain closed. Normalization Tasks 1-8 still require exact
approval of plan `7b2396b9e85b834715167d05b4b2a545b57541b0ad168e6a23bbe8752cc749be`,
corrigendum `79c843fd64c6249447309b84e19d73b503fdfe9b4372018a483b89e15af23e49`,
and review `63e5a146d4ca707899b2f6905eae81f09f27d8f912538be9992deedb6fea2a92`.
Tasks 9-10 retain a later separate exact-authorization gate; no normalization,
overlap, Barrier A/B, CTMC, DES, scoring, or scientific-status upgrade is open.

## 2026-08-05 Projection-Scope Wording Erratum

The approved materialization corrigendum, v2 plan, and independent review stay
byte-immutable at SHA-256
`ff469d9c5105835fde5feb170e501bdde14506df50632990f7c2cddc251da36c`,
`81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7`,
and `da6da7c2e513e11761e439f8b43ef6260556c912d3e730f94f15eae088d90ea0`.
PR #7's wording finding is closed by the successor audit clarification
`docs/superpowers/specs/2026-08-05-g6b-case-construction-materialization-contract-wording-erratum.md`,
raw SHA-256
`5192aec8e7269ec0c209e535c263a31c39be8c3f46238cde59e887a7b1db6841`.
The matching review is
`docs/verification/G6_B_MATERIALIZATION_PROJECTION_SCOPE_WORDING_ERRATUM_REVIEW.md`,
raw SHA-256
`e9aeb3c145c7b72a75dbf0a5456e30da15cdbde923c5480e9d20c4c1aa16102e`,
and records three PASS lanes with P0/P1/P2 `0/0/0`.
It names one case-scoped case-content projection and four method-scoped
DES/exact output-root and random-stream projections. No contract, artifact,
authorization, execution, capability, gate, or scientific status changes;
G6-B remains `OPEN/PENDING`.

## 2026-08-05 Historical / Pre-Closeout R7 Case-Construction Publication Status

Historical snapshot: approved v2 Tasks R1-R7 were complete on repaired artifact
subject C3 `0fa08e66c249fb19d8c014127cca8441efa90505`, tree
`8153fd46c4dae6dbd08a20fec93eab469fa8bc37`. C3 adds exactly 394 construction
artifacts: 13 case units, 26 sealed method observations, 13 exact/DES companion
groups, 390 case files, and four governance files. It changes no
source/schema/test/review/documentation path. The repository-publication
closeout above now has precedence for live Git/PR state; the scientific
post-R7 stop remains current.

Three independent R7 lanes reviewed the same C3 and returned PASS with
P0/P1/P2 `0/0/0`. The durable review is
`docs/verification/G6_B_CASE_CONSTRUCTION_REVIEW_V2.md`, raw SHA-256
`069307796147e25edf077ab8019e1b8b7e5cd2c27b980955c950e1dec2f65739`.
The documentation-only C4 successor changes only that review,
`PROJECT_HANDOFF.md`, and this roadmap; resolve its commit from live branch
history. At this historical snapshot PR #8 was draft and unmerged, with base
`codex/g6b-case-construction-contract-revision` / PR #7. It was later retargeted
to `main`, marked ready, and merged as
`3ef2a14e0396c21f825740728df7a08544964b81` during #3-#9 closeout.
Repository publication changes no scientific authorization.

Authorization semantics are split by design. The generated construction
authorization is `authorized=true` for the bounded `case_construction`
operation and has been consumed. The source protocol's frozen typed reference
still contains `case_construction_authorized=false`; it is not the live
authorization artifact. Downstream capabilities remain unopened:

```text
retired_authority_fingerprint_normalization_authorized=false
target_certification_preflight_authorized=false
quantitative_execution_authorized=false
```

No normalization, actual-overlap audit, Barrier-A preflight, CTMC, DES,
scoring, output inspection, confirmation, or scientific-status advancement was
run. Final verification recorded artifact-only 390/4/394 with no later roots,
focused `1975 passed, 2 skipped`, full four-worker worksteal
`2421 passed, 2 skipped`, and green Ruff/format/strict-mypy/diff checks.

G6-B remains `OPEN/PENDING`; G6-C/D/E remain
`NOT STARTED / NOT PASSED`; the paper gate remains closed. The mandatory post-R7
stop is active. The first possible next tranche is separately authorized,
data-only retired-authority fingerprint normalization.

## 2026-08-02 Historical / Pre-R7 Task2 Materialization Contract Revision Status

Historical snapshot: the user authorized the original Task2, but its TDD
implementation was stopped before commit and before any authorization or case
instance because the approved Tasks 2-7 did not close the construction
log/ledger, interruption recovery, comparison projections, seed commitment,
metric-sharing semantics, or C2/C3 source identity. The retained intermediate
`442 passed in 109.73s` is negative/partial engineering evidence, not a Task2
pass. This section no longer defines current status; the 2026-08-05
repository-publication closeout at the top has precedence.

The corrected plan-only subject is
`79091b863db897e3087640d0c72eb154751a5f6d` / tree
`e837d7d8bf680bb8d22211fdd20543e3bf6d5ebb` on
`codex/g6b-case-construction-contract-revision`. At this historical snapshot,
stacked Draft PR #7 was
`https://github.com/zjqc/IMS_deadlock/pull/7`, targeting
`codex/g6b-case-construction` / Draft PR #6. PR #7 was later retargeted and
merged as `b78fe6e84f248d405c934cd7c375cb810cb610a9`. Exact identities:

- materialization-contract corrigendum SHA-256:
  `ff469d9c5105835fde5feb170e501bdde14506df50632990f7c2cddc251da36c`;
- revised-plan SHA-256:
  `81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7`;
- independent-plan-review SHA-256:
  `da6da7c2e513e11761e439f8b43ef6260556c912d3e730f94f15eae088d90ea0`.

Three independent lanes returned `PASS`: ontology/scientific boundary,
mechanical DAG/count/hash/path closure, and adversarial implementability and
recovery. The v2 contract closes 36 schema keys, 30 files per case, 390 case
files plus four governance files, 393 deterministic transient paths, a
manifest-last create-new DAG, ordered repeated torn-frame recovery, nine-path
C2 source identity, artifact-only C3, documentation-only C4, deterministic
pre-outcome seed commitment, and the separation between intra-bundle metric
sharing and later retired-authority reuse.

The old Task2 worktree remains quarantined at
`codex/g6b-case-construction@01cf48c7623fa2d4652a1397c79c3c6202cf84fb`
with exactly two modified and two untracked draft paths. It must not be cleaned,
committed, transferred, or treated as v2 truth. All four capabilities remain
false; no case, normalization, overlap, preflight, CTMC/DES, quantitative
artifact, output inspection, or scientific verdict exists. G6-B remains
`OPEN/PENDING`.

Historical first unchecked next step at that time was exact user approval naming revised-plan SHA-256
`81b93394233b8201ab4ba234952f17110c87398bf34a83883481ac017112a4f7` and
review SHA-256
`da6da7c2e513e11761e439f8b43ef6260556c912d3e730f94f15eae088d90ea0`.
That approval later occurred; the repaired path completed R1-R7. The current
boundary is the mandatory post-R7 stop before any separately authorized
data-only retired-authority fingerprint normalization.

## 2026-08-02 Historical Task1 Corrigendum Review Status

G6-B case construction Task1 is `COMPLETED / REVIEWED` at subject `f8b777713fc7d5f239ab6449d99c050452db6f98` tree `b65b096a6135991ede09c125fbd9de4f381733e9`. At that historical snapshot, Draft PR #6 was `https://github.com/zjqc/IMS_deadlock/pull/6`, targeting `codex/g6b-case-construction-plan` / PR #5; it was later retargeted and merged as `3bb449fddde951cb641dc1019c70bc903a0ccccd`. The review artifact is `docs/verification/G6_B_CASE_CONSTRUCTION_ESTIMAND_SCOPE_CORRIGENDUM_REVIEW.md`; its SHA-256 is `744cac6caff24779d862704ad83d186023ea918f06f941e78fcc2f797c1b07c7`.

The bounded change is a schema/test/documentation corrigendum for `estimand_id` scope only. It keeps the original design SHA-256 `b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6`, plan SHA-256 `c20393328f8f98e7b35a6507fd6e993b2f17e068d977c3dc6253b05e9a75de5f`, plan review SHA-256 `297a69382347e16e894af63e70f8fa95807407048b2e89c45701410a4e9289e1`, and corrigendum raw SHA-256 `5b5266a562fb4e1515121a351d0b98227338bf34c991eef2fe76557b0e17334f` bound. It does not authorize construction or science.

Final evidence: schema `401 passed`; full repository `2170 passed, 2 skipped in 611.87s (0:10:11)`; Ruff/format/strict mypy clean; direct bundle valid with science false, case false, `PENDING`; ontology, boundary, and code-quality reviews all `APPROVE` with Critical/High/Medium/Low all zero.

Historical next step at Task1 closure: renewed Task2 entry approval was then
required and was later obtained. The original Task2 stopped on a contract gap
before authorization/case bytes; the later repaired path completed R1-R7. The
live next boundary is now the mandatory post-R7 stop, not v2 plan approval.


本路线图采用用户批准的理论优先顺序。Gate 的 `PASS` 只表示其明确列出的
受限结论已满足，不把候选定理、发现集程序结果或文献摘要包装成完成证据。

## 当前状态

| Gate | 状态 | 当前证据 | 未关闭项 |
| --- | --- | --- | --- |
| G0 仓库门 | PASS | Dell 目标路径、GitHub SSH 与项目 Python 3.13.9 已核验；PRs #3-#9 were merged in dependency order；closeout baseline `main@1f87f9d...` / tree `05844c0e...` was clean and upstream `0/0` with no open PR | 每个新进程仍须重锁 live `main` branch/HEAD/tree/upstream/status/open-PR state；repository merge 不等于科学授权 |
| G1 文献门 | PASS（scope-bounded） | 六条文献链、43 项审计矩阵、20 个全文/全文审计锚点、迁移卡；L30-L35 与 B05 七篇审计已纳入比较边界；R7/R8 类别饱和保持 | 不支持首创性、系统综述或一般 IMS/Petri 等价；G4 必须检验 CRP、recorder、SBA、L30/B05 comparator 边界 |
| G2 理论门 | PASS（严格受限主链） | P1 有限 LTS/reachability-net；P2 capacity-mediated 封闭核 iff；P2c `IMS-SIP^1` 诊断虹吸双向桥；P3 偏序充分条件；P3d `BIX1-SAT` 可达阈值；P3e `BIX2-PERSIST` 三资源 ring 精确阈值与同语义 DAG 修复；P4 CTMC；P5 supervisor；P6 复杂性边界 | plant-level structured Petri/S3PR 桥、替代/AND/AGV/预约/多 persistent-buffer 一般岛阈值、一般紧凑 IMS 精确复杂性和 risk-budget 控制仍开放 |
| G3 算法门 | PASS（严格小有限模型 + P2c/P3d/P3e） | 原 G3 证据为 123 tests；加入 G4/G5/G6 协议、局部核/终端类恢复、replay 数值完整性和 post-R3 comparator fail-closed 回归后，Dell 项目 Python 3.13.9 全库 341 tests、Ruff check/format、strict mypy 通过；原 C0、BIX1/BIX2 结果不变 | 一般 plant/S3PR、结构案例物理速率、一般 persistent-buffer/AGV 阈值和风险预算/Pareto 算法仍开放 |
| G4 案例冻结门 | PASS（historical C seal；已在 G5 原样执行） | A=`f9b9a5a5652c7a49053e7ef26d08911bd757f465`，B2=`58bbd4ab7da8c2c1d0bcdea4a12f2ae7c020d09a`，C=`e91be4d6d7511c76918093899269de4b78e69fd8`；封存时 checker 为 `FROZEN`、`errors=[]`、`confirmation_results_inspected=false`；随后只在 G5-B execution lock 下执行一次 primary 和一次 repro | G4/G5 九行已退役为历史 discovery/regression，不能再次充当 held-out；后续缺陷必须进入独立 successor freeze |
| G5 论文门 | FAIL（evidence closed） | G5-A=`b5e5dc0494b23a54c78c420bbca50a3639de8bff`，G5-B=`8aa752804b885b79e5371c98e7961087c540f2a8`，G5-C=`ff281481068a2325cb0bde00e85fd7b753ba854a`；9/9 案例完成 primary/repro，raw/canonical/stderr hash 一致；锁定 scorer 为 `4/3/2`，透明 theorem audit 为 `6/1/2` 并另保留两项 minimality failure | CRP local bridge 预测失败；grid/medium 因 `D/F` 未穷尽 terminal classes 而确定性拒绝；不能形成完整 exact/DES 证据链或宣称论文门通过 |
| G6 局部核—终端类恢复门 | IN PROGRESS / G6-A 与 G6-R PASS / G6-B `R7 CASE-CONSTRUCTION PUBLICATION REVIEWED / OPEN-PENDING` | repaired C3 `0fa08e66...` contains exact 13/26/13 and 390/4/394 sealed artifacts；three R7 lanes PASS 0/0/0；PR #8 later merged as `3ef2a14e...` | construction authorization is true only for bounded construction；repository merge changes no downstream capability/root；无 normalization/actual overlap/preflight/CTMC/DES/output/scientific verdict；mandatory post-R7 stop |

## G0 仓库门

通过条件：

- 远程主目录是 `D:\py_pro\IMS_deadlock`，连接
  `git@github.com:zjqc/IMS_deadlock.git`；
- 污染提交只按确认 lease 隔离/替换，不混入新历史；
- `buffer-design`、`makespan_doob_h` 和旧 `work_case` 仅只读取证；
- 仓库不含 secret、环境、缓存、下载论文或历史输出；
- 项目自己的 Python、依赖和验证命令已在锁定 worktree 中核验。

## G1 文献门

通过条件：

- Petri/S3PR、DES/RAS、有限缓冲队列、AGV/交通、吸收 CTMC 与稀有事件
  六条链均有审计矩阵；
- 前向/后向追踪连续两轮不产生新的模型类别、定理类型或关键反例；
- 每个实际进入定理的来源都有全文定位、原假设、迁移卡和不可迁移边界；
- metadata/abstract/context 只能用于导航或历史说明。

当前 `PASS（scope-bounded）` 只关闭本项目受限 P1-P6 与下一轮 G4 设计所需
的文献边界，不是系统综述完成、首创性完成或一般 IMS/Petri 等价完成。
20 个锚点包括原 P1-P6 所用全文 theorem/equation/context anchors，以及
七篇新增全文审计边界：

- `L30` finite-capacity S3PR/ENS3PR 是保守充分 resource-configuration
  baseline，不是 exact reachable iff threshold。
- `L31` S4PR CRP 是 marking-level partial-deadlock iff certificate；
  candidate reachability 仍需 SBA/可执行前缀检查，复杂性 NP-hard。
- `L32/L33` output-only recorder-place USPN/UniPN transformations 不改变
  原 transition enabling，但不自动替代 IMS operational 到 plant Petri 的
  语义桥，也不自动关闭固定原目标到 recorder target 的量化义务。
- `L34/L35` BA/SBA 决定给定 NIS 是否有 legal firing sequence，其
  `O(n*n1*(c*m+n^2))` 界不得写成标准 bit-polynomial IMS 判定。
- `B05` compressed maximally permissive supervisor 依赖 full RG 和 NP-hard
  MCPP，只能作为小 PN overlap comparator。

因此 G1 允许继续推进 G4，但仍阻止任何“首个可达/无需 reachability tree
的结构检测”、“首次使 Petri 可达性可判定/多项式化”、“一般 finite-capacity
exact threshold”或“一般紧凑 IMS 最大许可 supervisor”表述。

## G2 理论门

最低通过链：

`IMS-RAS^CW 稳定语义`
`-> finite LTS/reachability-net`
`-> covering closed blocking core iff capacity-mediated deadlock`
`-> IMS-SIP^1 state-induced wait-snapshot minimal empty siphon dual`
`-> strict-precedence restricted sufficient condition`
`-> BIX1-SAT reachable saturation threshold`
`-> BIX2-PERSIST exact three-resource ring threshold and paired DAG repair`
`-> finite competing-absorption CTMC`
`-> exact finite full-observation supervisor`
`-> representation-sensitive complexity boundary`.

所有更强结论必须保持 `拟证明` 或 `开放`：

- 一般 IMS 与 plant-level structured Petri/S3PR 的同构；
- `IMS-SIP^1` 之外最小封闭核与最小致死虹吸的双向最小性；
- P3e 明确三资源子类之外的 persistent-buffer、替代/AND 请求、AGV/预约
  或外部 drain 一般双向岛精确阈值；
- 一般紧凑 IMS 在 NP-hard 下界之上的完备复杂性；
- risk-budget 控制的递归可行性/Pareto 最优性。

## G3 算法门

通过条件：

- 穷举小模型的稳定状态与事件映射，输出确定性状态 ID 和最短可达前缀；
- 核验 capacity-aware closed kernel，并把 simple cycle、terminal SCC/knot、
  Banker、Petri siphon 和 exact supervisor 分成不同假设层；
- 对 `IMS-SIP^1` 构造 immutable state-induced wait-snapshot net，核验
  evidence fidelity、minimal empty siphon，并对 OR/AND、多容量和
  control-only 边界给出机器可读拒绝；
- 对 `BIX1-SAT` 从空状态穷举小网格，截断行不得计作理论证据；
- 对 `BIX2-PERSIST` 按预注册 discovery grid 穷举 ring 阈值及同语义 DAG
  修复；截断、invalid instance、DAG 无完成路径或任一 mismatch 均不得
  计作证据；
- exact supervisor 检查不可控闭合、marked coaccessibility 与初始可行性；
- CTMC 报告 committor、平均吸收时间、线性残差、灵敏度、Doob-h 行和和
  生成元来源；
- 随机 DES/CTMC 采样使用独立可复现随机流、置信区间和 stream manifest；
- `validate`、`prove`、`quantify`、`simulate`、`verify-case` 输出版本化 JSON；
- `pytest`、`ruff`、strict `mypy` 在项目专用远程环境全部通过。

程序枚举是证明审计器，不替代 P1-P6 的数学证明。

## G4 案例冻结门

历史 C-sealed 确认集：

- C0-C5 与 BIX2-PERSIST 仅是发现集，允许因反例修正定义和假设，但每次
  修改进入账本；BIX2 参与过 P3e 推导，不得进入确认集；
- C4 必须保留“完整运输模型有证书、机器投影漏检”的成对结果；
- C5 必须保留“双向回流阻塞、删除回流 DAG 修复”的成对模型；
- 当前候选确认集参数族、中型独立重建和对抗案例记录为
  `independent_preregistration`，不得从 C0-C5、BIX1-SAT 或 BIX2-PERSIST
  复制、改名或参数平移；
- 当前候选包含九个 case：S4PR CRP agreement、unreachable structural
  candidate、BAS/AGV/AND outside-S4PR refusal、recorder fixed-target
  quantification、`L30` supplied sufficient inequalities、`B05` adapted
  monitor cover、ten-cell IMS parameter grid、medium island rebuild、adversarial
  OR-of-AND/reservation boundary；
- 十格 grid 预测固定为 `G01=false`、`G02=false`、`G03-G10=true`；
- supervisor throughput/makespan/WIP/due-date-risk cost、conditioned path
  mass、rare-event efficiency 在当前 G4 中全部不适用；exact CTMC probability、
  mean absorption time 与 DES confidence interval 仅适用于 grid 和 medium。

结构验证只允许读取、解析、哈希和 schema/checker 测试。C seal 之前不得运行
`verify-case`、`quantify`、`simulate`、supervisor synthesis、CTMC solve、DES
或 rare-event 后端；不得检查、汇总或回填 held-out 输出。

冻结动作已由 A/B2/C 三提交闭合。`FREEZE_ENTRY.json` 锁定参数范围、指标、
基线、随机流方案、九个 artifact hash 与九个 case hash；提交后的 Dell
checker 返回 `FROZEN`、`errors=[]`、`confirmation_results_inspected=false`。
该 PASS 只表示确认协议在结果检查前已冻结，不表示任何确认预测得到支持。
G5 随后按锁定命令执行九行各一次 primary/repro；该面板现在已退役，不能
再次作为 held-out 或通过修复后重跑来改变其证据状态。

## G5 论文门

通过条件：

- 精确状态/CTMC 分析与独立 DES 置信区间一致；
- 报告 false positive/false negative、失败命题、监督性能代价和适用边界；
- 不删除冻结后的失败案例，不事后更换指标；
- 论文主张能逐项回链到定理、原假设、迁移卡、案例哈希和机器验证。

实际结论：`FAIL（evidence closed）`。

- 九个案例均只有一次 primary 和一次 repro；七例 exit 0，grid/medium
  都以相同非零 exit、空 stdout 和相同 stderr hash 确定性拒绝，没有 retry
  或第三次运行。
- 锁定 scorer 的原始 `4 SUPPORTED / 3 FALSIFIED / 2 INCONCLUSIVE`
  作为不可变证据保留。
- 事后规则审计发现 scorer 把两个独立
  `certificate_minimality=FAIL` 错并入 theorem falsifier；透明、非覆盖式
  审计为 `6 SUPPORTED / 1 FALSIFIED / 2 INCONCLUSIVE`，原始输出不删除。
- `G4_CRP_S4PR_AGREE` 仍是冻结预测失败：target reachability agreement
  没有关闭 local certificate 与 mapped-resource equality。
- grid/medium 保持 `INCONCLUSIVE`：在求解前发现 reachable non-`D/F`
  state 不能到达声明吸收类，因此没有 exact probability、mean time 或同目标
  DES 证据。

完整报告见 `docs/verification/G5_CONFIRMATION_REPORT.md`、
`G5_REPRODUCIBILITY_AUDIT.md` 和 `G5_CLAIM_EVIDENCE_TABLE.md`；评分勘误
见 `evidence/g5/G5_SCORING_ERRATUM.json`。

## G6 局部核—终端类恢复门

G6 是新科学门，不是 G5 repair rerun。通过顺序：

1. theorem prediction 与 ancillary metric 独立计分，execution status 不得
   被任一者覆盖；
2. global certificate、all-minimal local kernels 与 minimality evidence
   使用显式 scope；
3. CRP partial bridge 只消费声明的 local-kernel family，并冻结多核匹配量词；
4. CTMC 在 estimand 之前完成
   `D_global,D_local,F,R_livelock,R_terminal` closed-class decomposition；
5. 用未复用 G4 参数或状态的 synthetic regressions 关闭已知机制；
6. 建立新的 discovery set 与独立 confirmation set，预注册、hash lock、
   C seal 后才允许一次 primary/repro。

当前阶段审计：

- G6-A 的受限语义、局部核、CRP bridge、终端/停止分区、scorer
  正交性和 post-R3 comparator fail-closed 行为已经由 341 项全库测试及
  静态检查验证；
- R1 因 Windows schedule-state 租约竞争失败，保持
  `FAILED_INCOMPLETE`，未补齐缺失行；
- R2 的五对原始结果完全匹配，但 consumer 使用严格 `[0,1]` 而 producer
  使用 `1e-10` 数值容差，导致 grid/medium 被误判；R2 保持
  `FAILED_MECHANISM_CHECK`，没有事后重评分；
- 修复统一 producer/G5/G6 consumer 的完整 probability map、reported
  bounds 与 linear residual 数值契约，不做 clamp，也不改写 R1/R2；
- 预注册 R3 在不可变代码树上完成一次 primary 和一次 repro，五对
  raw/canonical/stderr 完全匹配且五项 mechanism 均为 `PASS`；
- 两个 boundary 行的 theorem 仍为 `SUPPORTED`，同时独立保留
  `certificate_minimality=FAIL/false`；
- R3 是 `historical_replay`，只关闭已诊断机制，不进入新确认集的预测
  正确率，也不使 G6-C/D/E 通过。

以下 2026-07-30/2026-07-31 段落保留历史 exact-five/exact-eight 证据，不是
当前 continuation instruction；当前 v2 入口见本节末的 2026-08-01 段落。

在该历史阶段，下一硬门不是继续重放旧案例，而是 G6-B：相对 retired G4、retired G5
和 G6-R historical replay，新 discovery rows 必须在
`case_content_sha256`、`state_snapshot_sha256`、`route_signature_sha256`、
`parameter_tuple_sha256`、`random_stream_manifest_sha256`、`output_root`、
`sealed_prediction_sha256` 和 `metric_schema_sha256` 八个 canonical
dimensions 上全部 zero overlap，并预先锁定 terminal/stopping estimand、
负对照、exact/DES 同目标规则和失败账本。G6-B protocol foundation 已创建
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md`、`cases/discovery/g6b/`、
`src/ims_deadlock/g6b_protocol.py` 和 `tests/test_g6b_protocol.py`；该基础
只完成 execution-disabled/PENDING 的协议和 data-only validator，Task2
targeted+adjacent 验证为 52 validator tests + 59 adjacent = 111 passed；
随后 locked worktree `D:\worktree\IMS_deadlock-g6b-discovery` at HEAD
`4c24f39` 在 state-doc commit 前通过 full pytest `393 passed in 47.22s`、
Ruff check、Ruff format 41 files already formatted、strict mypy `src`
22 source files、strict mypy `src+tests` 41 source files、five protocol JSON
parse checks、targeted protocol tests `52 passed in 2.48s` 和
`git diff --check`。
它没有创建 discovery case，没有运行 enumeration、CTMC 或 DES，也没有
检查任何新科学输出。Independent foundation review 已通过
`PASS FOUNDATION ONLY`，artifact 为
`docs/verification/G6_B_PROTOCOL_FOUNDATION_REVIEW.md`，无
Critical/Important/Minor protocol findings；这不改变
`adversarial_review_status=PENDING`、`scientific_execution_authorized=false`、
G6-B `OPEN` 或 G6-C/D/E 未开始状态。在该历史阶段，下一步曾是单独编写
adversarial row-family discovery-model/execution plan；该旧指引已由本节末的
2026-08-01 exact-twelve schema-review continuation 取代。actual overlap report、
runtime lock 和 discovery outcomes 当时仍开放。

2026-07-31 row-family protocol bundle 继续保持同一边界：nested row-family
bundle 为 `IMPLEMENTED / DATA-ONLY`，canonical protocol validation 返回
`valid=True`、0 errors、`scientific_execution_authorized=false`、
`case_creation_authorized=false`、`adversarial_review_status=PENDING`，但这
不是科学证据或执行授权。Locked worktree
`D:\worktree\IMS_deadlock-g6b-discovery` at HEAD
`4fda4896d2284c360f3021e48475f7678b0f37fd` 在 Phase A state-doc edit 前通过
full pytest `1307 passed in 150.84s`、Ruff check、Ruff format
`43 files already formatted`、strict mypy `src` 23 source files、strict mypy `src+tests`
43 source files、eight nested JSON parse checks、top-level foundation tests
`52 passed in 5.00s`、canonical row-family test `1 passed in 0.12s`、
canonical row-family validator `valid=True`/errors empty/`science=False`/
`case=False`/`PENDING`/`ROW_FAMILY_BUNDLE_IMPLEMENTED`/8 hashes、recursive
authorization scan 和 `git diff --check`。Top-level `cases/discovery/g6b/`
JSON set 精确为五个，nested row-family JSON set 精确为八个；Task 1-7 diff
`a4897ab..4fda489` 只包含 exact-eight nested JSON、row-family validator source
和 row-family tests；actual overlap report、
overlap-authority lock、execution-runtime lock、discovery cases/outcomes、
output root、enumeration、CTMC、DES 和 science summary 均 absent。上述
`4fda489...` 是 earlier Phase A evidence，不是 current committed target。
Phase C post-commit verification 在 committed HEAD
`13adc15e8b7b8047a25ab5a340880621ee3ad0bd`、clean、`NO_UPSTREAM` 上采集：
Python 3.13.9；full pytest `1307 passed in 144.93s (0:02:24)`；Ruff check
pass；Ruff format `43 files already formatted`；strict mypy `src` 23 和
`src tests` 43 pass；`git diff --check` pass；foundation
`52 passed in 9.87s`；canonical row-family `1 passed in 0.09s`；8/8 JSON
parse；exact five/exact eight；foundation validator valid/errors0/science
false/`PENDING`/hashes5；row validator valid/errors0/science false/case
false/`PENDING`/`ROW_FAMILY_BUNDLE_IMPLEMENTED`/hashes8；recursive 13-JSON
scan `non_false_auth=0`、`non_pending_status=0`；base diff forbidden paths=0、
actual marker hits=0；relevant output roots 和 task mypy cache dirs 均 absent。
Bundle
`adversarial_review_status` 必须保持 `PENDING`；独立 review verdict 必须
存储在单独文档中，不得改写 JSON bundle state。2026-07-31 三道独立 review
已完成：specification compliance 为 `APPROVED` 且无 blockers，code quality 为
`APPROVED` 且无 Critical/Important/Minor blockers，scientific boundary 为
`PASS PROTOCOL ONLY` 且无 blockers。这些 verdict 只批准
protocol/spec/code/boundary，不授权 case construction 或 science。在该
historical/pre-v2 阶段，后续仍需要另行批准 case-construction plan；当前 v2
continuation rule 见下一段，不允许从 review verdict 直接跳到 G6-C
confirmation preregistration。

2026-08-01 current v2 状态取代上述 exact-eight 作为继续入口，但不改写其历史：
Historical/pre-repair Task-5 schema-code subject 为
`9ef6fcec9e410b2ab7afc4144df8b948a238d95f`，nested bundle 是 exact-twelve。
Final Section 18 evidence subject 为
`948ff5746adcb66b68fb9c47e519f070dd2c96ba`，已完成 independent review
publication：schema `356 passed`、Git-scope `19 passed`、four-file
`1695 passed, 2 skipped`、full repo `2122 passed, 2 skipped`、retired focus
`1 passed`、manifest `1 passed`、Ruff full green、format `47 files`、strict
mypy `src` 25 和 `src tests` 47 pass、JSON duplicate parse `53 files`、sets `5/12`、
auth fields 21 true0、future roots/modules0、canonical 19 on Python
remote3.13.9/local3.12.3/local3.13.5、diff checks green；ontology review
`APPROVE` 无 P0-P2，scientific/boundary review `APPROVE` 无 P0-P2，
code/capability review `APPROVE` P0-P3 zero；review 唯一指出的 P3
evidence-publication sync 由本次文档更新关闭。批准规格
digest
`b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6` 与 frozen
matrix raw SHA
`487d81aa79a7bca681db81f19a4d6bd315668c43b1c4538c47f01f099d8e205f` match。
G6-B 保持 `OPEN/PENDING`。四个 typed capabilities 分别为
`case_construction_authorized=false`、
`retired_authority_fingerprint_normalization_authorized=false`、
`target_certification_preflight_authorized=false`、
`quantitative_execution_authorized=false`；later instance roots 均 absent。
本 tranche 没有创建 case、运行 normalization/overlap/preflight/CTMC/DES、
检查 output 或形成 scientific verdict。作为历史已批准对象，原
case-construction plan SHA
`c20393328f8f98e7b35a6507fd6e993b2f17e068d977c3dc6253b05e9a75de5f`
与 review SHA
`297a69382347e16e894af63e70f8fa95807407048b2e89c45701410a4e9289e1`
已发布、获批并关闭 Task1；其 Tasks 2-7 随后由 v2 修订取代。该历史阶段的
first unchecked next step 曾是 v2 plan/review exact approval；该批准后来发生，
repaired R1-R7 已完成。当前 first unchecked boundary 是 mandatory post-R7
stop；未经单独 data-only normalization 授权，不能继续进入 downstream science。
计划发布作用域守卫在新路径未声明时按预期 RED，随后仅允许两个精确计划文档
路径并保持 governance-instance 路径拒绝；final direct `2 passed`、Task-6
selection `17 passed, 1112 deselected`，Ruff/format/strict mypy/diff green。

完整根因和 R3 证据见
`docs/verification/G6_HARD_PROBLEM_ROOT_CAUSE_AND_R3_REPAIR.md`、
`evidence/g6/G6_HISTORICAL_REPLAY_FAILURE_LEDGER.json`、
`evidence/g6/G6_HISTORICAL_REPLAY_R3_REPORT.json` 与
`evidence/g6/G6_HISTORICAL_REPLAY_R3_RAW_HASH_MANIFEST.json`。

详细执行契约、恢复理论和边界审查见
`docs/superpowers/plans/2026-07-30-g6-local-core-terminal-class-recovery.md`、
`docs/superpowers/plans/2026-07-30-g6b-protocol-foundation.md`、
`docs/superpowers/plans/2026-08-01-g6b-schema-only-governance-v2-implementation.md`、
`docs/theory/G6_LOCAL_FIRST_HIT_AND_STOPPING_THEOREMS.md`、
`docs/verification/G6_B_PROTOCOL_FOUNDATION_REVIEW.md` 与
`docs/verification/G6_B_CASE_TARGET_SCHEMA_V2_REVIEW.md`。

## 科学停止条件

若最终只剩“把 Petri、RAS、CTMC 和仿真工程拼装起来”，就在扩展案例和
大规模实验前停止并重构科学问题。若一般等价被反例推翻，则收缩到可证明
子类并把反例作为边界结果；不得模糊定义或降低证据标准。

历史标识 `e0b07a52ed667ce2651dfccf2455d6876a96b02d` 仅作隔离来源记录，
不能成为案例、算法、证明或验证证据。

## 2026-07-31 G6-B Ontology And Absorption-Domain Correction

Implementation status: Task 7 documentation alignment is applied on top of the
v2 foundation estimand, v3 terminal stopping partition, certificate v1, and
generator provenance v3 work already present on this branch. The correction does
not create a G6-B case, does not run LTS/CTMC/DES science, and does not upgrade
G6-B to PASS.

Current boundary: `selected_stopping_targets` are `D_global`, `D_local`, and
`F`; `unselected_plant_terminal_classes` are `R_livelock` and `R_terminal`;
`P_policy` is separate; `S_reach` and `S_T` are derived and nonselectable.
`S_reach` is support graph reachability only. `S_T` is certified by the finite
positive-rate stopped-CTMC closed-SCC/reverse-basin certificate, where SCC
closedness is checked against the full stopped graph including selected `A_stop`, with
`absorption_domain_hash` binding the domain identity. Missing rates remain
distinct from explicit empty rates. G6-B remains OPEN/PENDING,
`case_creation_authorized=false`, and `scientific_execution_authorized=false`;
G6-C, G6-D, and G6-E are not started.
