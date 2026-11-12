Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# The review of ACT-CONTEXT-WATCH-1: W2-176's context_watch.py registered as a PostToolUse hook (DEC-1140 (1)(b))

You are a fresh, read-only independent reviewer of an ACT before it goes to the owner (DEC-1104 (2): rehearsal, a READY
review and matching hashes). READY is computed by `verdict.py` from your block.

## The ACT
- **Package:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/context-watch-1/ACT-CONTEXT-WATCH-1.md`.
- **Bundle:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/acts/ACT-CONTEXT-WATCH-1/` (manifest sha256
  `487c93c13e1b6ee2f223c5386fbb5cc38101737be200e94e4583aeb52350e58f`).
- **What it changes:** one PostToolUse block (matcher `Bash`, timeout 10) in `.claude/settings.json` and `.rulesync/hooks.jsonc`,
  running `template/governance/kernel/hooks/context_watch.py` in PreCompact's wrapper form. `check` and `apply` refuse (exit 6)
  unless that hook file exists with W2-176's approved sha256 `c6dabb5eed394c89c31aae40a9466185355cfb3d161c44284c863c636559607c`.
  It applies after W2-176 (DAEO-ktiw, `w2/W2-176` `3a580a4b4d42`, review round 2 READY; its CIT-P
  `/home/usain/gov-os-worktrees/W2-176/docs/changes/W2-176-CIT-P.md`) merges into w2/integrate.
- **Why matcher `Bash`, not all tools:** the template's `postToolUse` uses `Bash`, and the portability check's
  `HOOKS_MATCHER_DIFFERS` is a hard block; the package's §1 states the follow-up for all tools.

## Check
1. **Hashes and scope:** `before/` equals the live `.claude/settings.json` and `.rulesync/hooks.jsonc` on `w2/integrate` today;
   `after/` adds only the one block in each; every hash in the package, `list.txt` and `manifest.json` recomputed; it touches
   none of tonight's other ACTs' files (`dispatch/launch_now.sh`, `dispatch/dispatcher.py`, `dispatch/balancer.py`, their tests,
   `tools/stop_idle_check.py` and its test, `.claude/templates/**`, `.rulesync/subagents/**`, `.claude/agents/**`, `.claude/skills/**`).
2. **Fail safe and nothing weaker:** the new entry adds no permission, no allow rule and no decision field; the hook it runs can
   only add context (read W2-176's `context_watch.py`: on any error no output, exit 0); with the hook file missing, what does a
   Bash call do (the package says the registered command exits 2): is that a fail-closed block of every Bash call, and is the
   `check` refusal enough to keep it from being applied too early? Judge by the two questions.
3. **The matcher choice and the reach:** is `Bash` sound for tonight (the reminder fires after Bash calls only), and does the
   reminder still reach the CTO, leads and workers in ordinary runs?
4. **Rehearsal and class:** the counts hold in your own clone with W2-176 merged (one folder per pytest run through
   `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, TMPDIR outside the
   repository, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`);
   `python3 -m gov.adapters.portability` from the clone's root gives `findings: []` after the apply; the class is (b) and the
   route the owner's operator by hand tonight (the agent does not run 01:00-08:00).
Never touch the live `.claude/`; never run a real Claude session.

KPI id for the verdict block: `act-context-watch-1`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this ACT.

## Write and return
- **You write nothing** in any tree. Single simple Bash commands (DEC-1080). Every wait by pid only
  (`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`).
  Row W2-L423's rule: under `.gov-runtime/`, commit hashes as 12 digits and none of that rule's keywords.
- Scratch budget 30 GB, your own TMPDIR; remove your clone (`chmod -R u+w` first); report du in `evidence`.
- The hidden-half rule holds: never open anything under the evaluation sets' root or any hidden folder. Refused twice for
  the same call: stop and say so.
- **Your record is your session's final message:** the twelve labelled fields first; your answers to the checks; every finding
  with its two lines and scope; then `REVIEW_MD_BEGIN`, the review record in markdown, `REVIEW_MD_END`; at the end the fenced
  `verdict` block `{"kpis": [{"kpi": "act-context-watch-1", "verdict": "pass|fail", "findings": [...]}]}`, each finding
  `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Time matters (the owner wants it applied before 03:00 UTC if READY): aim for 25 minutes.
