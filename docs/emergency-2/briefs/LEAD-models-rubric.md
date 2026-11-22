# Lead brief: the model rubric of DEC-1225 in code, in Gov OS and in EXAMIN (a fix under W2-201, `DAEO-k1us`, the rubric in code)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it. Name: `models-rubric`; worktree
`/home/usain/gov-os-worktrees/E2-models-rubric`, branch `e2/models-rubric` from `w2/integrate`. **Do not merge.** This is
first on the list: the owner wants it live before any new session starts.

**The owner's decision, DEC-1225 (read it whole in `docs/DECISION_REGISTER.md`):** Opus only for the long-running
sessions that orchestrate: each app's CTO and the senior engineer. Every other agent runs Sonnet, C3 work included:
leads, engineers, test designers, helpers, writers, the memory measure's reader and grader, reviewers and auditors, the
operator, proving runs. One exception: a wide, comprehensive audit the owner asks for runs on Opus; a reviewer called
after a failed landing or for a bug runs Sonnet. No session runs Fable. "Put it in the rubric table and enforce it by
code before any new session starts: the launcher picks the model by role, the helper rule refuses any other model, the
role files and their copies say the same, in Gov OS and in EXAMIN."

**Already done by the CTO (`e49c093fd`):** `governance/project/model-exceptions.yaml` lost its four C3 Opus entries and
gained one for `independent-auditor` on Opus (the owner's audits). The helper hook now refuses Opus for every other
helper and refuses Fable (checked by hand).

## The fix lines (each with its verify; a fix under W2-201, recorded in its record, failing test first; models: every helper Sonnet)
- **R1 The role files carry the new table.** In `template/governance/kernel/roles/*.md` and every generated copy
  (`template/.rulesync/subagents/`, `.rulesync/subagents/`, `.claude/agents/`, regenerate with the project's generator):
  `orchestrator` (the CTO) and `senior-engineer`: Opus; `ticket-lead` and every worker role (engineer,
  independent-test-designer, independent-auditor, qa-engineer, product-spec, research, ...): Sonnet at every criticality
  (no `C3 model claude-opus-5-5` line left). The audit exception is stated as the exceptions file's, not as a role
  default. `governance/project/criticality.yaml`'s comments and audit 4's Table 3 as the rubric's source say the same.
- **R2 `gov launch` picks the model by role.** A ticket lead (`gov launch orchestrator|lead <ticket>`, `--fix`,
  `--chore`) gets Sonnet, never the CTO's Opus default; a worker gets Sonnet at C3 too; `--model` naming Opus or Fable is
  refused unless the exceptions file names it. Verify: planted launches of a lead, a C3 engineer and a C3 test designer
  record Sonnet; `--model claude-opus-5-5` for an engineer is refused; `--model claude-fable-5-2` is refused.
- **R3 The helper rule's exception can be limited to the audits the owner asks for.** The exceptions entry for the
  audits carries a limiter the hook reads (for example `task: <id>` matched against the spawn prompt's `Task:` line, or
  `decided` naming the owner's decision and the prompt carrying it); an Opus auditor without it is refused. Fable is
  refused with no Fable hint left (DEC-1215 is over: `governance/project/model-substitution.yaml` retires with its
  readers, or stays `active: false` with its code path removed: say which).
- **R4 The memory measure's reader and grader run Sonnet** (`src/gov/memaudit/judge.py:31`, its prompts and launch
  flags; W2-81's runner already forces Sonnet). DEC-1098's figures stay comparable only from the first fresh 80 graded
  on Sonnet, which becomes the new baseline (DEC-1225 (4)): the measure's record names the models.
- **R5 EXAMIN.** List what in EXAMIN's copy (`/home/usain/gov-os-runs/W2-27/examin`, read only) carries the old
  table: its kernel role files and copies (they come from the kit by `gov update`), its `.claude/hooks/agent_model.py`
  and `governance/project/model-exceptions.yaml` if it has them, its start scripts. What the kit carries reaches EXAMIN
  by `gov update` to 0.1.5; for anything the kit does not carry, write the exact change for the EXAMIN CTO in your
  return (it makes it in its own repository).

## Green and return
`gov accept W2-201` green (the test designer, Sonnet, revises the cases that pin the old table, with a Rewrite-Reason
naming DEC-1225), `tests/unit/launch`, `tests/unit/hooks`, `tests/unit/memaudit`, W2-204, W2-195, W1-28, W1-33,
W2-153, `tests/unit/adapters`, `tests/unit/optin`. Return: branch and head; each R line with its tests; the EXAMIN list;
the trial figures (runs to green, send-backs, minutes, cost); reds not yours.
