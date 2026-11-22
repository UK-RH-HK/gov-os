# Lead brief: fixes-015a, five fixes for release 0.1.5 in how sessions start and stop (DEC-1232 (6), DEC-1233 (2))

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it. **Do not merge.** Every helper Sonnet (DEC-1225). Each fix: failing test first by the independent test designer, then the engineer; one commit series per fix with its own `Task:` and `Fix:` trailers; record each in its owning ticket's file as a `## Fix: ...` section (the form of `.tickets/DAEO-xm6l.md`'s last section). Find each owning ticket with `gov retrieve` and `grep -l "^wbs_id: W.-N" .tickets/*.md`. The audits these come from: `docs/emergency-2/audits/E2-AUDIT-{1,2,3}-*.md` and the merged table `.gov-runtime/scratch/orchestrator/log/audits-merged-2026-11-22.md` (ids N-nn, M-nn). Decisions: DEC-1232, DEC-1233.
Name: `fixes-015a`; worktree `/home/usain/gov-os-worktrees/E2-fixes-015a` (if a worktree or branch of that name exists from a stopped first start, remove it first: `git worktree remove --force` and `git branch -D`), branch `e2/fixes-015a` from `w2/integrate`, **then merge `e2/models-rubric` into it first** (DEC-1225's launcher, role files and hook; it lands through `gov queue` before yours; read only, never commit to it). Effort: this lead runs medium (DEC-1236 (2)).

## The fixes
- **F1 No session loads the owner's claude.ai connectors; each gets only its role's MCP tools** (the owner, DEC-1232 (6):
  "no Gov OS or EXAMIN session loads my claude.ai connectors (Gmail, Drive, Calendar, Docs); none of them is needed. Fix
  it by code, in how every session starts: each session gets only the MCP tools its role needs. It goes into 0.1.5.").
  Proven by the CTO on 2026-11-22: `claude mcp list` in a project whose `.claude/settings.json` holds
  `"disableClaudeAiConnectors": true` lists no server (without it: the four claude.ai connectors);
  `ENABLE_CLAUDEAI_MCP_SERVERS=false` does the same. (a) The kit's settings (`template/governance/kernel/settings.json`)
  carry the key, and `gov update` and `gov adopt` merge it into an adopted repository's `.claude/settings.json` (EXAMIN
  gets it with 0.1.5); Gov OS's own `.claude/settings.json` already carries it (the CTO's commit). (b) `gov launch` starts
  every session (CTO, senior engineer, lead, fix and chore leads, workers) with `--strict-mcp-config` and an
  `--mcp-config` built from the role's MCP list (a list in the role file or one committed per-role file, empty for every
  role today), and sets `ENABLE_CLAUDEAI_MCP_SERVERS=false` in the session's environment; `gov launch` no longer refuses
  `--mcp-config` outright: it accepts only what the role's list allows. (c) `gov doctor` reports a repository whose
  settings lack the key (a drift line, exit 0). Verify: planted launches of each role record the flags; an adopted
  repository updated to the candidate has the key; a role with an MCP tool listed gets exactly it. Owners: the
  launcher's ticket (W2-201 `DAEO-k1us` or the ticket of `gov launch`'s lead start) and W2-17 for the update merge.
- **F3 `gov --version` prints `commit unknown`** in a pinned install: it prints the commit the wheel was built from.
  Owner: the ticket of `gov --version` / the release build.
- **F10 Pause really stops** (N-07, the owner: "so pause really stops the dispatcher and the lead starter before releases
  are cut on my behalf"; CAP-05.a): while `gov pause` holds, the product's dispatch pass and `gov launch` start nothing
  (refused, `PAUSED`, naming the pause), `gov release --patch` refuses, and the pause sends the stop message to every
  running session's inbox. Verify: a planted pause: no launch, no dispatch start, no patch release, one stop message per
  session. Owner: W1-28. (The CTO makes the scratch dispatcher and `start_lead.sh` read the same pause in the live tools.)
- **F11 No unfilled template slot in a generated agent file** (N-08): the generated `.claude/agents/*.md` (and the kit's
  copies, EXAMIN's) carry `{CMD:retrieve}`, `{ID}` and other slots (46 in `orchestrator.md`); generation fills or drops
  every slot, and the portability check refuses a generated file holding one. Run it after `e2/models-rubric`'s
  regeneration (it is on your base). Owner: W1-38.
- **F12 The SubagentStop hook stops blocking twice** (N-09): it reads a value on the next line of the return and honours
  `stop_hook_active` (exit 0 when set). Verify: a planted return with the value on the next line passes once; with
  `stop_hook_active` true the hook exits 0. Owner: W1-29.

- **F13 Every helper runs Sonnet, whatever its agent type** (DEC-1225, the owner's priority 1): on 2026-11-22 audit 1's
  four `Explore` helpers (the built-in type, no `model` named) ran **Opus** although `CLAUDE_CODE_SUBAGENT_MODEL` named
  Sonnet (`.gov-runtime/scratch/orchestrator/log/usage-breakdown-2026-11-22.md`, audit 1's helpers); general-purpose and
  role helpers ran Sonnet. `.claude/hooks/agent_model.py` passes a spawn that names no model on the assumption the
  default applies. Make the hook write the model into the spawn: a PreToolUse hook may return `updatedInput`; every
  Agent spawn that names no model gets `model: "sonnet"` (and an Opus spawn the exceptions file lets through keeps its
  model), so no built-in or plugin agent type can run its own or its parent's model. The kit's copy of the hook does the
  same (EXAMIN gets it by `gov update`). Verify: planted spawns of `Explore`, `Plan`, `general-purpose` and a role type
  with no model each come back with `model: "sonnet"`; an Opus auditor under the exception keeps Opus; Fable refused.
  Owner: W2-201 `DAEO-k1us`.

- **F14 Ticket leads run Sonnet at medium effort** (DEC-1236 (2), the owner's change to the rubric): the rubric table
  (`governance/project/criticality.yaml` and wherever `e2/models-rubric` put the DEC-1225 table), the role files and
  their copies, and `gov launch` give a ticket lead (and a fix or chore lead) `--effort medium`; every other role's
  model and effort stay exactly as DEC-1225 and the table set them (DEC-1236 (3): no other change to a model or effort).
  Verify: a planted lead launch records Sonnet and medium; a worker launch is unchanged. Owner: W2-201 `DAEO-k1us`.

- **F15 The memory measure's figure carries its stamp** (audit 4 A-9, placed in 0.1.5 before EXAMIN's fresh 80; the
  owner's priority 4): `FIGURES.json` (and the printed verdict) stamps `release`, `commit`, `reader_model`,
  `grader_models`, `forbidden_rule` and `questions_with_forbidden: <n>`; `declare` refuses `forbidden_rule: strict` when no
  question carries a `forbidden` list; a figure without the stamp is never compared with one that has it. Builds on D5's
  `forbidden_rule` (landed with `e2/d5-memaudit-strict`). Owner: W2-204 `DAEO-ma4q`.

- **F16 W1-21's two rerank cases pin a retired bound:** `tests/acceptance/W1-21/test_w1_21_merge.py`
  `test_several_batches_are_reranked_in_one_pass_over_the_merged_set` and `test_a_rerank_over_more_than_thirty_candidates`
  assert at most 16 texts a request (DEC-1067 (f)); the code's bound is `MAX_REQUEST_TEXTS = 64` with
  `MAX_REQUEST_CHARS = 24_000` (`src/gov/retrieval/rerank.py:38-50`, DEC-1090 (2), W2-137), so both fail on a green base
  (18 and 40 texts). The test designer revises them to the bounds in force (count ≤ `MAX_REQUEST_TEXTS`, padded size ≤
  `MAX_REQUEST_CHARS`, read from the module, not restated), with a Rewrite-Reason naming DEC-1090 (2). No code change.
  Owner: W1-21 `DAEO-5x4l`.
- **F17 `gov accept W1-06` and `gov accept W1-48` stop with `ACCEPT_MAP_UNREADABLE`:** the test designer writes each
  README's KPI map in the form `gov accept` reads (as fixes-015b's F5 did for W2-16); no test changed. Owners: W1-06, W1-48.
- **F18 `gov doctor` reports the pytest plugins as missing tools:** `pytest-xdist`, `pytest-timeout`, `pytest-testmon`
  (registry entries, Python packages with no binary) read `ok: false`; doctor checks them as packages (by
  `importlib.metadata` version, as `pyyaml` is), not as binaries. Owner: W2-22 `DAEO-xm6l`.

- **F19 No launch takes a model the rubric does not give** (DEC-1225, the owner's priority 1; `models-rubric`'s return,
  "what is not enforced"): a worker launched on a role file whose table still names Opus (an adopted repository on an
  older kit) gets Opus. Add the one condition in `gov launch`'s `_rubric` that refuses (or replaces with the rubric's
  Sonnet) any model the rubric table does not give that role, whatever the role file says, and move the planted role
  files in the unit and W2-184, W2-33, W2-60a fixtures to Sonnet (the lead measured 92 unit and 272 acceptance cases that
  plant Opus tables). Also the orchestration tools that still launch Haiku: `governance/project/orchestration/tools/dispatch/dispatcher.py`
  (about `:1426`) and the dead-man (`deadman.py:158`, `:301`, wherever it lives in the tree) launch Sonnet; and
  `governance/project/briefs/LEAD-w2-common.md`'s `--model claude-opus-5-5` lines (29, 93, 97) are archived or corrected.
  No role's model or effort changes beyond DEC-1225 and DEC-1236 (2). Owner: W2-201 `DAEO-k1us`.

## Green and return
`gov accept` of each owning ticket green; `tests/unit/launch`, `tests/unit/hooks` (with F13's cases), `tests/unit/update`,
`tests/unit/adapters`, `tests/unit/memaudit`, W2-204, W1-06, W1-21, W1-28, W1-29, W1-38, W1-48, W2-22, W2-201, W2-17, `tests/unit/optin`. Return: branch and head; each fix with its
owning ticket and tests; reds not yours; the trial figures.
