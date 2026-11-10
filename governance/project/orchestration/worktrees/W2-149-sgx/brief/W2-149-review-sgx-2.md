Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-149-sgx/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-149 — the review of set-up A's wiring (DAEO-52ku)

You are a fresh, read-only independent reviewer (FULL profile). **Scope: set-up A's wiring.** The CTO's delegated
rulings (DEC-1112 (3); recorded in the main tree at `4fd701aba`: `governance/project/orchestration/DECISIONS-IN-FORCE.md`'s
last entries and `governance/project/orchestration/packages/SANDBOX-GUARD-EXP-DECLARATION.md`'s amendment A5) and the
ticket's changed and new lines: **S16, S20, S22 to S28 and the new failure line**, each marked `[changed, DEC-1112 (3)]`
in `.tickets/DAEO-52ku.md` (read the ticket's last note). The rest of W2-149 was reviewed READY and merged (`b4de529b`,
F11 `ff1865184`); re-open it only where this change touches it. READY is computed by `verdict.py` from your block.

**The hard constraint:** the five owner-approved set-up A briefs' bytes do not change (DEC-1101 (2), DEC-1113); the
template supplies what their front matter lacks. Their text is in your worktree at
`.gov-runtime/scratch/ref/sgx1-briefs/*.md` (sha256 `bbff1249…`, `e13b5f96…`, `82134b3d…`, `137a73d1…`,
`b212a424…`; the declaration §12). Their inputs, outputs and result forms are the spec the wiring must meet.

## What to review
- **The branch:** `w2/W2-149-sgx` in `/home/usain/gov-os-worktrees/W2-149-sgx`, head `7df7c35e3`, with `w2/integrate`
  (`7b08bd12d`) merged in: the change is the diff from `7b08bd12d` to `7df7c35e3`. The designer's cases (`tests/acceptance/W2-149/`, commits `f65c0c992`,
  `59030819b`; the README's "Set-up A's wiring: the interface"); the engineer's commits (`indep_launch.py`, the
  template's `kinds.yaml` and `tree-exclude.txt`, the new schemas in `indep-schemas/`, the unit tests, the evidence):
  `1f6051e12` (the build; its session ended on a network error after committing it), `0d21a1dca` and `499fb8fc1` (a
  fresh engineer's finish); the designer's fix of S16's writer case `45fa65963` (a `str`/`Path` skip compare in the
  cases' helper, found by the lead), merged at `7df7c35e3`.
- **The runs:** the lead's, at `7df7c35e3`, outside the sandbox (2026-11-10 09:5x UTC): the acceptance folder (but
  `live`) and the two unit files with `GOV_W2_149_BWRAP=1`: **227 passed, 0 failed** (the 9 `bwrap` cases included);
  the 3 live cases (`GOV_W2_149_LIVE=1`, haiku, planted roots, the real HOME for the login): **3 passed**. The
  engineer's `gov accept W2-149` in the sandbox before the S16 fix: 135 passed, 2 failed (S16's writer case), 12
  skipped (3 live, 9 `bwrap`). The designer's red check before the build: 61 red for their stated reasons.
- **The engineer's own notes, for you to weigh** (none is in the interface; judge each): labeller 2's `labels-2.jsonl`
  is delivered byte for byte with no line check (a malformed file surfaces only as the auditor's 10); a writer whose
  `result.json` says `stopped` other than `none` but leaves a partial `out/cases.jsonl` still has it delivered; writer 2
  stopping `not-sealed` with no `cases.jsonl` ends `rejected` (20), not `stopped`.
- **Check:**
  1. **The briefs pass unchanged:** each of the five passes stage 10 from the template's values (S22) and gets exactly
     the inputs its brief names, and its outputs land where its brief says (S16, S24 to S27); no brief needs a change
     to work. Read the code path, not only the tests.
  2. **The confined rule script (S25):** `label_rules.py` is code written by an independent session that the CTO's
     unsandboxed script runs. Can it read anything (the sets root, HOME, the repository, the wall, the other half),
     write anything, reach the network, start a process, outlive its cap, or make the script stage partial or forged
     labels? Is every failure 18, never a pass? Does any part of the confinement fail open when `bwrap` or the
     interpreter behaves unexpectedly?
  3. **Independence (question 2):** nothing of one labeller reaches the other's wall; the x/y map and the labellers'
     identities never enter the auditor's wall; the second labeller's sample is the declaration's rule from its own
     wall's seed (A5); the seeds stay the script's own draw (S6); no caller input chooses content.
  4. **Deliveries:** all or nothing; no overwrite but the two the interface allows; `labels.jsonl`'s rewrite keeps the
     old bytes; the overlap auditor never writes `AUDITS.log`; nothing lands under the sets root or the experiment
     folder outside a flow's destination; the hidden part's budget (S18) still counts what set-up A adds.
  5. **No regression:** the memory writer, checker and auditor flows and S1 to S15, S17 to S19, S21 unchanged; the
     template's two files changed only as the rulings say (`tree-exclude.txt` gains `governance/project/indep-briefs/**`;
     `kinds.yaml` a `model` per kind and the five `briefs:` entries with their `tree_exclude`).
  6. **The cases test what the lines say:** each new or revised case red without the change and green with it, for
     its stated reason; no case weakened; the revised cases carry their `Rewrite-Reason`.
  7. **Failure lines:** none of the ticket's failure lines now passes where it should fail.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns set-up A's wiring.

## Write and return
- **You write nothing** in any tree. You may run the tests read-only (`-p no:cacheprovider --optin=lifted
  --optin=breadth`) through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
  with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149-sgx/src` and an empty scratch HOME
  (`PYTHONUSERBASE=/home/usain/.local` so pytest is found). A nested `bwrap` cannot start in your sandbox: the 9
  `bwrap` cases were run by the lead outside it (above). Never run anything against the real `~/gov-os-eval/`,
  `~/gov-os-runs/`, `~/gov-os-wall-trees/`, `~/.claude/` or a real `claude` session. No GPU. Single simple Bash
  commands (DEC-1080). The hidden-half rule holds. Read the template folder `governance/project/indep-walls/` with the
  Read tool only, never naming it in a Bash line.
- **Search again once (DEC-1092 (1))** if a search does not answer.
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (task,
  status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
  recommended_next_action; sandbox and `ps` checks first), your answers to checks 1-7, every finding with its two lines
  and scope (ids from F18), and at the end the fenced `verdict` block over the lines the change touches:
  `{"kpis": [{"kpi": "S16", "verdict": "pass|fail", "findings": [...]}, {"kpi": "S20", ...}, {"kpi": "S22", ...}, {"kpi": "S23", ...}, {"kpi": "S24", ...}, {"kpi": "S25", ...}, {"kpi": "S26", ...}, {"kpi": "S27", ...}, {"kpi": "S28", ...}]}`
  with each finding `{"id", "scope", "ordinary_work", "consequence"}`.
Refused twice for the same call: stop and say so; no third try.
