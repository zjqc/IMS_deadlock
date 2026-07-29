# Reference Project Audit

## Authority Boundary

The reference projects are evidence sources only. `IMS_deadlock` may reuse
semantic ideas, model interfaces, and published mathematical formulas after
independent restatement, but it must not copy private source files, function
bodies, configuration values, tracked outputs, checkpoints, trajectories, or
paper-specific numerical results.

## Live Read-only Evidence

Audit lock:

- lock time UTC: `2026-07-29T14:33:43Z`;
- lock time China: `2026-07-29T22:33:43+08:00`;
- channel: direct SSH to `friend-win`;
- probe per Git path: `git branch --show-current`, `git rev-parse HEAD`,
  `git status --short`;
- mode: read-only; no `fetch`, `checkout`, file write, or repository mutation
  was performed during this audit.

| Source | Locked evidence | Use in this project |
| --- | --- | --- |
| `buffer-design` main | `D:\py_pro\buffer-design`, branch `main`, HEAD `91e02db4c330bf5c2607f098e6c347c1f55dd12d`, clean. | Theory style, verification discipline, economic/control framing. |
| `buffer-design` economic worktree | `D:\worktree\buffer-design-economic-optimization`, branch `codex/economic-buffer-optimization`, HEAD `06b782df215b9f27812bed44d47e1306ce05dddd`, clean. | Economic intervention framing only. |
| `buffer-design` mechanism worktree | `D:\worktree\buffer-design-mechanism-analysis`, branch `codex/mechanism-rigorous-analysis`, HEAD `ad35d0d85da288acc9092a56a5c18352d5ac7a2c`, clean. | Mechanism-analysis discipline only. |
| `makespan_doob_h` primary checkout | `D:\py_pro\makespan-15-doob-h-gnn-fixed-restored`, branch `main`, HEAD `386384f0cc4cf17c910d32c3e80bdf3cba5b7733`, dirty with exactly ` M docs/superpowers/plans/2026-06-23-v15-handoff-status-and-remaining-plan.md` and `?? docs/superpowers/plans/2026-07-02-v15-main-merge-codex-tracking.md`; comparison only. | Doob-h, committor, generator-interface, uniformization, and independent DES cross-validation ideas; not an authoritative clean source. |
| `makespan_doob_h` theory worktree | `C:\Users\dell\.config\superpowers\worktrees\makespan-15-doob-h-gnn-fixed-restored\v15-theory-case-validation`, branch `codex/v15-theory-case-validation`, HEAD `165b37ef1e9dbb87b262e5107d2633db4e2d52ef`, clean. | Clean comparison source for theory/case-validation ideas. |
| Old manufacturing-island `work_case` | `D:\py_pro\makespan交付风险-v12.8-重要-换案例含死锁-doob_closure_response_rebuild\work_case`, not a Git repository, no visible license. | Read-only semantic provenance for blocked completion, finite buffers, AGV blocked-unload, and M-D bidirectional flow. |

## Old Case Semantics Observed

- The old 3 x 4 manufacturing-island case contains `T`, `M`, `D`, and `G`
  resources, three products, finite input/output buffers, and three AGVs.
- Route evidence includes `B: T -> D -> M -> G` and `C: M -> D -> G`; therefore
  `D -> M` and `M -> D` both appear in the route family.
- A machine completion with a full output buffer becomes
  `blocked_complete`: the job and machine remain held.
- An AGV arrival with a full input buffer becomes `blocked_unload`: the job and
  AGV remain held.
- Zero-time closure order observed in the old event loop:
  release blocked machines, unload blocked AGVs, start machines, dispatch AGVs
  from outputs.
- Dispatch capacity checks counted in-transit reservations, but direct release
  into the first-stage input did not use the same hard-reservation contract.
  This can create overbooking-like ambiguity and must be fixed in IMS semantics.
- The event loop ran `while heap`; if the event calendar emptied while jobs were
  unfinished, it integrated to the horizon and wrote unfinished completion times
  as `now`. IMS_deadlock must instead classify
  `event calendar empty && unfinished jobs` as an explicit, auditable deadlock
  or blocked terminal state.

## Migratable Ideas

- state-space generator interface;
- committor equation and Doob-h conditioned-path interpretation;
- uniformization for CTMC validation;
- complete successor contract that accounts for held, requested, reserved, and
  blocked resources;
- independent DES simulation as a cross-check against exact equations.

## Non-migratable Items

- private function bodies, comments, variable/action labels, and configuration
  files;
- historical traces, hashes, checkpoints, and output tables;
- old numerical parameter values unless they are rederived and explicitly
  justified;
- any claim that the old non-Git `work_case` grants a reusable license.
