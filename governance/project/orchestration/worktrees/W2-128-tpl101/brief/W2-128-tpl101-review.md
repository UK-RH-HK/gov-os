Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-128-tpl101/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# The review of the kernel ticket template 1.0.1 (DEC-1121; W2-128, DAEO-t8mp) — C3

You are a fresh, read-only independent reviewer. RUBRIC-2 (DEC-1120): C3 work, Opus at high. READY is computed by
`verdict.py` from your block. The owner approves the template's hash only after your review.

## What happened
- The owner approved W2-128's kernel templates as 1.0.0 (DEC-1116). CAP-31.a (`docs/contract/CONTRACT_v4.md` ~494)
  names `class` in the task contract; the schema `template/governance/kernel/schemas/ticket.schema.json` keeps `class`
  optional; the 1.0.0 ticket template's record block had no `class`. The owner chose (a) (DEC-1121,
  `grep -n "^### DEC-1121" docs/DECISION_REGISTER.md`): add `class`, version 1.0.1.
- A product-spec session committed `8df648cc9` on `w2/W2-128-tpl101` (worktree `/home/usain/gov-os-worktrees/W2-128-tpl101`):
  `version: 1.0.1` and one line `class: implementation   # or research, test-design, discovery, data, integration, skill`
  before `role`. Template sha256 after `0f584330c6f1c996873c66dd251b6f4ecc24ddd5c6220cf590f937a1dbbad65b`.
  It reports: W1-08 all suites 234 passed, 1 failed (the known path-map namespace fault for
  `governance/project/indep-briefs/`, fixed separately by ACT-PATHMAP-NS-2); W2-128 121 passed; `gov.check.schema` ok.

## Check
1. **Exactly two changes** in `git -C <worktree> diff 905b82a3b 8df648cc9`; nothing else in the commit; recompute the
   sha256.
2. **The values are right:** the comment's list equals what the schema allows for `class` (read the property: enum,
   pattern or free text?) and what `src/gov/` reads (e.g. `src/gov/close/command.py` ~298, the plan, the ready check:
   grep `"class"` / `.get("class"`); `implementation` is a valid default. Is the placement and comment in the block's
   own style? Is `class` here clearly not RUBRIC-2's C0-C3 criticality class (say whether the comment could mislead a
   reader into thinking it is, as a finding if so)?
3. **Nothing pinned breaks:** anything that pins the ticket template's version or hash (keys.yaml, the templates'
   README, the facts file, `tests/acceptance/W2-128/`, `governance/project/orchestration/packages/TEMPLATES-APPROVAL-1.md`)
   either follows or needs a named follow-up (the approval table's 1.0.1 line is the CTO's after the owner's approval).
4. **The run:** once, read-only, in the worktree:
   `env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=/home/usain/gov-os-worktrees/W2-128-tpl101/src python3 -m pytest /home/usain/gov-os-worktrees/W2-128-tpl101/tests/acceptance/W1-08 /home/usain/gov-os-worktrees/W2-128-tpl101/tests/acceptance/W2-128 -q -p no:cacheprovider --no-header -o tmp_path_retention_policy=failed --optin=lifted,breadth`
   through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`
   (`PYTHONUSERBASE=/home/usain/.local` if HOME is empty). Counts only.
5. **Trailers:** Task, Role, Implements, Co-Authored-By.

KPI id for the verdict block: `ticket-template-1-0-1`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this revision.

## Write and return
- **You write nothing** in any tree. One test run (check 4) only. No GPU, no installs. Single simple Bash commands
  (DEC-1080). `EMG-common.md`'s hidden-half rule holds. Row W2-L423's rule: under `.gov-runtime/`, commit hashes as 12
  digits and none of that rule's keywords. Any wait by pid only.
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (sandbox
  and `ps` checks first); your answers to the checks; every finding with its two lines and its scope; at the end the
  fenced `verdict` block `{"kpis": [{"kpi": "<id>", "verdict": "pass|fail", "findings": [...]}]}`, each finding
  `{"id", "scope", "ordinary_work", "consequence"}`.
- Estimate: 15 minutes.
