
## W1-31: the governance-share counter (DEC-491, DEC-495, DEC-501, DEC-502, DEC-507, DEC-512; 2026-10-08)

Merged from `w1/W1-31` at `35904984` (131 cases; `src/gov/telemetry` 646 lines against an estimate of 150:
the counter reads the harness's session logs itself, which the estimate did not foresee).
`gov telemetry <ticket> [--json] [--ticket-session <session id>[=<role>]]...` and
`gov.telemetry.counter.measure(root, ticket, sessions)` give a record with the five measured governance
sources, a labelled estimate, three share figures (measured, estimated, total), tokens in and out, cache
creation apart, cache reads outside the share, and "not measured" by name for whatever it could not read.
It outputs counts only, never log text. The log forms were learnt from three specimens made in throwaway
projects in `/tmp` (`specimen/` in the orchestrator's scratch); no worker and no test read a real session
log.

- **The call from `gov close` is not built** (DEC-495: a W1-30 follow-up). `gov close` must write the close
  record first and measure after; the caller supplies each session as `<session id>=<role>`. The close
  record is "not measured" until it exists, so a measure before the close ends with exit code 3.
- **The estimate (DEC-507)** reads the session role's file under `.claude/agents/`, `CLAUDE.md` and
  `AGENTS.md` as they are when the counter runs, not as they were in the session; neither root file exists
  in this repository, so here it is the role file alone. **The role is the caller's word, unverified,**
  until launch records carry it (DEC-470). Without a usable role the estimate and the estimated and total
  shares are "not measured". MCP counts 0 with its reason. A sub-agent's own instruction files are not in
  the estimate (a named gap; DEC-512 F).
- **The counter accepts only logs of Claude Code 2.1.288;** another version is refused until a new specimen
  is read.
- **The denominator is slightly low:** the harness's own totals include calls the log does not show as
  assistant lines, so the share reads slightly high; W1-42 reports the difference once (DEC-501). `cost` is
  ccusage's figure from its built-in prices; only the four token figures are held against the log, and a
  model without a price gives "not measured" for cost.
- **"Not measured" by name, until a fourth specimen shows the form (DEC-512):** an interpreter word other
  than `python3` running `gov.cli.main`; `gov` through a runner on the fixed list (`uv run` and the like); a
  SessionStart with plain text and an added-context line at the same start; a permission rule's denial of a
  tool other than Bash; a user line whose content is a list holding anything but tool results; a text line
  marked `isMeta` of an unknown kind; a feedback line not followed at once by its `system` line.
- **Where the count can be low without a sign:** `gov` inside `bash -c`, `eval`, backticks or a wrapper
  script, or behind a runner outside the fixed list (the first four are named in the record's known gaps,
  the last is not); only Bash tool calls are examined for `gov`; plain output of a successful hook of any
  event but SessionStart counts 0 (DEC-502); governance text in a new key of a known line form; a
  sub-agent's log kept anywhere but the session's `subagents` folder; an over-long result is counted as
  logged (its shortened form; the `tool-results` folder is passed over by name, unchecked); a SessionStart
  run with empty `content` counts 0 without its `stdout` being checked; files in a checkpoint folder whose
  names are not a checkpoint record's; the automatic checkpoint folder of another worktree.
- **Where the larger reading is taken (the record says so):** the text of a blocking, denying or failing
  hook is counted whole, with the harness's prefix (the denial sentence is accepted for any tool word); a
  SessionStart hook's plain text is counted as the packet; a compound, piped or redirected `gov` command has
  its whole result counted.
- **Not shown by any specimen:** an automatic compaction. A PreCompact hook's output is a named gap (it is
  in no hook line); this repository registers such a hook (DEC-512 corrects DEC-502 on that).
- **Order of commits** for "rewritten after implementation began" is git's topological log order, not
  ancestry across parallel branches. `agent.harness` is a literal.
- **The sandbox's added system-prompt tokens** are "not measured" until W1-42 makes the paired measurement
  and places its record (DEC-491, DEC-501).
- **Incident 1:** the run-2 test designer ran a search with a glob over `governance/project/*.yaml`, which
  takes in the held-out file; it reported one hit, in `path-map.yaml`, and nothing else displayed or used.
  Told to the owner; briefs forbid globs, searches and listings over that folder (DEC-508).
- **Incident 2:** the run-4 lead loaded `.claude/settings.json` in a script to list the registered hook
  events (the brief allows `git diff --stat` only on that file). By its own account the script printed the
  `hooks` section only (five event names with matcher and command), so the deny line was not displayed. Told
  to the owner.
- **Launched workers were refused Write under `.gov-runtime/scratch/`** ("directory denied") in this
  worktree. Leads and a test designer fed read-only scripts to the interpreter by here-document; three
  writing commands of the run-4 designer were refused by the guard. The lead's last message of run 3 was a
  note after its return; the return was recovered by resuming that session once without tools.
- **W1-46 in the lead's run 4:** 23 errors at setup from one shared live research session that ran its
  second step from the wrong folder; 493 passed when run alone.
- **KPI disputes:** three in run 3 (settled by DEC-502), six in run 4 (settled by DEC-512). **Acceptance
  tests rewritten after implementation began:** three designer commits (`7fdfb672`, `50e88b9f`, `8e716c60`),
  each with its `Rewrite-Reason:` trailer.
