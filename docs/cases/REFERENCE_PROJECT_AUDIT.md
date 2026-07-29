# Reference Project Audit

## Authority Boundary

The reference projects are evidence sources only. `IMS_deadlock` may reuse
semantic ideas, model interfaces, and published mathematical formulas after
independent restatement, but it must not copy private source files, function
bodies, configuration values, tracked outputs, checkpoints, trajectories, or
paper-specific numerical results.

## Live Read-only Evidence

| Source | Locked evidence | Use in this project |
| --- | --- | --- |
| `buffer-design` | `D:\py_pro\buffer-design`, branch `main`, HEAD `91e02db4...`, clean. Worktrees: `D:\worktree\buffer-design-economic-optimization` at `06b782df...`, `D:\worktree\buffer-design-mechanism-analysis` at `ad35d0d8...`, both clean. | Theory style, verification discipline, economic/control framing. |
| `makespan_doob_h` | Primary checkout `D:\py_pro\makespan-15-doob-h-gnn-fixed-restored`, branch `main`, HEAD `386384f0...`, with one modified and one untracked documentation file; comparison only. Clean theory worktree `C:\Users\dell\.config\superpowers\worktrees\makespan-15-doob-h-gnn-fixed-restored\v15-theory-case-validation`, branch `codex/v15-theory-case-validation`, HEAD `165b37ef...`. | Doob-h, committor, generator-interface, uniformization, and independent DES cross-validation ideas. |
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

