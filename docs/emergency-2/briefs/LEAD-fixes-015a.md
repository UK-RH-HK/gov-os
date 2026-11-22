# Lead brief: fixes-015a, five fixes for release 0.1.5 in how sessions start and stop (DEC-1232 (6), DEC-1233 (2))

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it. **Do not merge.** Every helper Sonnet (DEC-1225). Each fix: failing test first by the independent test designer, then the engineer; one commit series per fix with its own `Task:` and `Fix:` trailers; record each in its owning ticket's file as a `## Fix: ...` section (the form of `.tickets/DAEO-xm6l.md`'s last section). Find each owning ticket with `gov retrieve` and `grep -l "^wbs_id: W.-N" .tickets/*.md`. The audits these come from: `docs/emergency-2/audits/E2-AUDIT-{1,2,3}-*.md` and the merged table `.gov-runtime/scratch/orchestrator/log/audits-merged-2026-11-22.md` (ids N-nn, M-nn). Decisions: DEC-1232, DEC-1233.
Name: `fixes-015a`; worktree `/home/usain/gov-os-worktrees/E2-fixes-015a`, branch `e2/fixes-015a` from `w2/integrate` (it already holds DEC-1225's launcher changes from `e2/models-rubric`).

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

## Green and return
`gov accept` of each owning ticket green; `tests/unit/launch`, `tests/unit/hooks`, `tests/unit/update`,
`tests/unit/adapters`, W1-28, W1-29, W1-38, W2-201, W2-17, `tests/unit/optin`. Return: branch and head; each fix with its
owning ticket and tests; reds not yours; the trial figures.
