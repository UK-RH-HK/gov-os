# W2-60: the rules probe, and the launch switches measured (lens G Q4; KPI line 9 of W2-60a)

- **Measured by:** the ticket lead of W2-60a (DAEO-cv58), run 1, in its own session, on 2026-10-29 between
  17:40 and 18:20 UTC, before any engineer started. Committed unchanged in substance by the engineer's design batch.
- **CLI:** Claude Code 2.1.292 at `~/.local/bin/claude`. **Model:** `claude-opus-5-5`, `--effort low`, every session.
- **Launcher:** the pinned `gov` (`~/.local/bin/gov`, interpreter `~/.local/share/gov-os/pin-5c401220/bin/python`),
  whose `src/gov/launch/` and `src/gov/guard/` are `w2/integrate`'s at the time of writing. No `PYTHONPATH`.
- **18 live sessions in all,** about USD 2.32: 4 for the three questions, 11 for the switches the CIT-E needs (part 2),
  3 for the CIT-E's unmeasured points (part 2b).

## 1. The rules probe

### The repository

A throwaway repository built from scratch at `/tmp/gov-os-lead-W2-60a/rules-probe/` (the lead's temp folder; never
under `.gov-runtime/`, never a copy of the tree), the way W1-46's live tests build theirs:

- a fixture engineer ticket `DAEO-zp60` (`in_progress`, role engineer, `allowed_paths: src/probe/**, lib/probe/**`);
- `.claude/settings.json`: this repository's committed settings less its absolute `Read` deny rules (as W1-46's
  `make_project` does), so the guard hooks are wired;
- the six kernel hook scripts (`template/governance/kernel/hooks/*.py`), copied as single named files;
- two files of identical content, `src/probe/alpha.py` (matched by the rule) and `lib/probe/alpha.py` (not matched),
  paths of equal length;
- one rule, `.claude/rules/probe.md` (189 bytes), holding a token found nowhere else:

```
---
paths:
  - "src/probe/**"
---
# Probe rule (W2-60a rules probe)

The probe token is KESTREL-7731-BASALT. When you are asked for the probe token, give it exactly.

EDIT-TARGET: original
```

The builder and the runner are the lead's scratch scripts `build_probe.py` and `run_probe.py`. The environment of
each launch is the caller's less `GOV_ROLE`, `GOV_TICKET`, `PYTHONPATH` and every name beginning `CLAUDE` (as W1-46's
live tests start theirs, DEC-784), with `TMPDIR=/tmp/gov-os-lead-W2-60a`.

### The command (each of the four sessions)

```
cd /tmp/gov-os-lead-W2-60a/rules-probe && gov launch engineer DAEO-zp60 -- -p "<prompt>" \
  --model claude-opus-5-5 --effort low --output-format stream-json --verbose \
  --permission-mode acceptEdits --max-turns 8 --allowedTools Read Edit Write Bash
```

`gov launch` started every session; no difference from a worker's launch but the environment above.

### Q1. Does the file load in a headless worker started by `gov launch`?

**Yes, and only for a path it matches.** Prompt: read one file once, then answer `TOKEN=<the probe token your
context gives>` or `TOKEN=NONE`.

| Session | Rule file | File read | Answer | Session id |
|---|---|---|---|---|
| s1 | present | `src/probe/alpha.py` (matched) | `TOKEN=KESTREL-7731-BASALT` | dafa53fd-aafb-46f6-ac3c-54b43e2d3932 |
| s2 | present | `lib/probe/alpha.py` (not matched) | `TOKEN=NONE` | a0f8196b-c7ee-4832-9537-87e2de1d8802 |
| s3 | absent | `src/probe/alpha.py` | `TOKEN=NONE` | f2760ec6-545c-4a09-9302-422a75301533 |

The rule enters the context when a matching file is read (with the read's result), not at the session's start.

### Q2. What does it cost in tokens?

From each session's stream-json usage (`input_tokens` + `cache_creation_input_tokens` + `cache_read_input_tokens`
per request):

| Session | First request (the start) | Added by the second request (after the read) |
|---|---|---|
| s1 rule, matched | 25,990 | 232 |
| s2 rule, not matched | 25,985 | 122 |
| s3 no rule, matched | 25,987 | 121 |

- **At the start:** no measurable cost. The three starts are within 5 tokens of each other (noise; the rule file is
  not listed or loaded at start).
- **When it matches:** 232 − 121 = **111 tokens** for this 189-byte rule, added once, with the matching read.
- So a `paths:`-scoped rule costs about its own size plus a short wrapper, and only in sessions that touch its paths.
- Whole-session totals (for the record): s1 `in 3, cache_create 26,220, cache_read 25,988, out 181`, USD 0.2186;
  s2 `4, 15,346, 36,742, 94`, USD 0.1320; s3 `4, 13,559, 38,532, 93`, USD 0.1181. They differ by the cache's
  state across sessions, not by the rule; the per-request figures above are the comparison.

### Q3. Can the worker change it?

**No, by any of the three routes.** Session s4 (423ec9d7-900c-4aa2-8f74-3791ce5943ca, rule present), told to try
each once:

| Route | Result | Refused by |
|---|---|---|
| Edit (after a Read) | refused: "File is in a directory that is denied by your permission settings." | the launcher's `Edit` deny rules for `.claude/**` (DEC-315) |
| Bash `printf 'bash-was-here\n' >> .claude/rules/probe.md` | refused: "PreToolUse:Bash hook error: Bash write to '…/.claude/rules/probe.md' denied for role 'engineer'" | the guard |
| Write | refused: "File is in a directory that is denied by your permission settings." | the launcher's `Edit` deny rules |

The file was byte-for-byte unchanged afterwards and `git status --short` in the probe repository was empty. The
session's `permission_denials` lists all three calls. The sandbox's own write fence was not reached for Bash (the
guard refused first).

### What it means

- A `paths:`-scoped `.claude/rules/` file works in a `gov launch` worker: it loads for matching paths only, costs
  nothing until then, and the worker cannot change it (the `.claude/**` protections already cover `.claude/rules/`).
- It is a fit for path-specific method text (lens G Q4). Nothing in this ticket uses it.

## 2. The launch switches, measured for the CIT-E

The CLI started directly with the `--settings` the pinned `gov launch` builds for an engineer in the probe repository
(`build_settings` of the pinned launcher, plus the temp folder as the launcher sets it), so that switches the pinned
launcher refuses after `--` could be tried (runner: the lead's scratch `run_switch.py`). **The difference from
`gov launch`:** the CLI is started by the script, not by the launcher; the settings and the environment are the
same. Each session's start was read from the stream-json `system`/`init` event (`--output-format stream-json
--verbose`), whose keys `mcp_servers`, `agents`, `skills`, `plugins`, `memory_paths` and `tools` show what the
session loaded. For these sessions the probe repository also held a fixture `.claude/agents/engineer.md` (agent token
OSPREY-2209-GRANITE) and a fixture role file `roles/engineer.md` (role-file token HERON-5518-SHALE); r4 added a
`CLAUDE.md` (token PLOVER-3364-CHALK).

| Session | Switch | What the start showed | Session id |
|---|---|---|---|
| w0 | none (a no-op settings key) | 4 claude.ai connectors (2 connected, 2 needing sign-in) and their 19 `mcp__` tools; user-level agents `code-reviewer`, `explore`, `refactor-scout`, `test-writer`; the user's synced skills `anthropic-skills:*` (13); `memory_paths.auto` set | d60bbf6a-68ac-40c7-8fef-8461731baa6e |
| w1 | `--strict-mcp-config` (no `--mcp-config`) | **no connectors, no `mcp__` tool**; the rest as w0 | 1420b597-5dab-487b-9d89-a692a7b74348 |
| w3 | `--setting-sources project,local` | **no user-level agent, no user-level skill**; connectors still there; the project's hooks still load (project source kept) | 954cc2f2-39b2-4789-8983-5aef8a8694b0 |
| w4 | settings key `"autoMemoryEnabled": false` in `--settings` | **`memory_paths` absent**; the rest as w0 | 5fd7d96e-a9fd-47a5-9979-17f46cb2b0d9 |
| w5 | `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` in the process environment | **`memory_paths` absent** | 56e6099a-f580-4888-a7e9-9a84ec3eee7c |
| r3 | none; prompt asks for both tokens | `AGENT=NONE`, `ROLEFILE=NONE` | 0b378817-c98e-4417-901f-4e5e135f80df |
| r1 | `--agent engineer` | `AGENT=OSPREY-2209-GRANITE`, `ROLEFILE=NONE`. **The tools become the agent's `tools:` list only** (`Read`, `Bash` for the fixture; no `mcp__` tool, no `Edit`, `Write`, `Task`, `Skill`). **The start is 6,293 tokens, against 25,976 without** (r3): the agent's text replaces the CLI's default system prompt. Connectors are still listed as connected. | 383bf4e0-bf71-48db-9a38-1caad243b3fa |
| r4 | `--agent engineer`, with a `CLAUDE.md` | the guard still refuses a Bash write to `.claude/agents/hooked.md` (hooks fire); `CLAUDE.md` is loaded (`CLAUDEMD=PLOVER-3364-CHALK`); `AGENT=OSPREY-2209-GRANITE` | fa88590c-61f2-44e8-b00f-5659e42181fd |
| r2 | `--append-system-prompt-file roles/engineer.md` | `ROLEFILE=HERON-5518-SHALE`, `AGENT=NONE`; the default prompt and tools are kept | b566034f-a254-4fc0-87aa-e7cb34023054 |
| x1 | `--resume <r3's id> --session-id <new uuid>` | **refused by the CLI**, exit 1, no session: "Error: --session-id can only be used with --continue or --resume if --fork-session is also specified." | none |
| x2 | `--resume <r3's id> --fork-session --session-id <new uuid>` | runs; the session's id is the new uuid (16756a4c-3e1a-471b-85b1-519f468367bc) | 16756a4c-3e1a-471b-85b1-519f468367bc |
| c1 | `--strict-mcp-config --setting-sources project,local --append-system-prompt-file roles/engineer.md --session-id <uuid>`, settings `"autoMemoryEnabled": false` | **no connector, no `mcp__` tool, no user-level agent or skill, no `memory_paths`;** the session's id is the uuid given; `ROLEFILE=HERON-5518-SHALE` | 9791e991-8f79-4b2a-aa32-21219ba0e148 |

**What stays after c1's switches** (no switch removes it without removing the project's own too):

- the CLI's built-in skills (19 names: `deep-research`, `design`, `design-sync`, `dataviz`, `update-config`,
  `verify`, `debug`, `code-review`, `simplify`, `batch`, `fewer-permission-prompts`, `doctor`, `loop`, `schedule`,
  `claude-api`, `workflow-authoring`, `run`, `run-skill-generator`, `plugin-authoring`); `--disable-slash-commands`
  ("Disable all skills") would remove the project's skills as well;
- the CLI's built-in agents (`claude`, `Explore`, `general-purpose`, `Plan`, `statusline-setup`);
- the CLI's built-in plugins (`cc-plugin-agents-md`, `cc-plugin-telemetry`, `cc-plugin-plugin-authoring`).

These are the CLI's own, not user-level. The KPI asks for no user-level agents or skills; the built-ins are named
here so the CIT-E can say how it treats them.

**Also seen:** `--setting-sources project,local` drops the user's settings file as a whole: on this machine that file
sets `effortLevel` and the env `CLAUDE_CODE_SUBAGENT_MODEL` (names only read), so a launch with it gets neither from
there. The caller's process environment here carries `CLAUDE_EFFORT` and `CLAUDE_CODE_SUBAGENT_MODEL` (names only),
which a launcher that passes the caller's environment hands on (lens E F13; W2-56's environment).

## 2b. Three follow-up measurements (after the CIT-E's package P-W2-60a-2)

Same runner and settings as part 2, each with `--strict-mcp-config --setting-sources project,local` and settings
`"autoMemoryEnabled": false`. The probe repository also held a fixture project skill
`.claude/skills/probe-skill/SKILL.md` (skill token WAGTAIL-8842-FLINT) and a second fixture role file
`roles/engineer2.md` (token IBIS-6670-MARL).

| Session | What | Result | Session id |
|---|---|---|---|
| k1 | `--permission-mode acceptEdits --allowedTools Read Bash Edit Write Grep Glob` (no `Skill`); asked to load `probe-skill` with the Skill tool | **loaded:** `SKILL=WAGTAIL-8842-FLINT`. A `-p` worker loads a project skill on request without `Skill` in `--allowedTools`. The start lists `probe-skill` first among the skills. | 2d820436-d5c4-48f3-a34f-59d4ab1a1f18 |
| f1 | `--append-system-prompt-file roles/engineer.md --session-id <A>`; "READY" (the token never appears in a message) | `READY` | aede90ec-ebd5-450d-bf08-30590655bed6 (A) |
| f2 | `--resume <A> --fork-session --session-id <B> --append-system-prompt-file roles/engineer2.md`; asked for both tokens from its system instructions only | **`FIRST=HERON-5518-SHALE`, `SECOND=NONE`:** the forked, resumed session keeps the original session's system prompt (the text appended at its first launch) and does not take the text appended at the resume. | d9f62b1b-642c-4a75-8353-3cefb4ae9c22 (B) |

- So the role text a resumed session has is the one its original launch appended, whatever the resume passes.
- **Not measured:** whether `--setting-sources project,local` drops a user-level `~/.claude/CLAUDE.md` and
  `~/.claude/rules/`. Neither exists on this machine (checked 2026-10-29); measuring it would mean planting one in
  the real home, which every running session on the machine would load, or copying the CLI's sign-in into a test
  home, which Policy 2 (a) refuses. A named residual.

## 3. Left behind

- `/tmp/gov-os-lead-W2-60a/rules-probe/` (the throwaway repository; removed by the lead after the commit of this
  record, or named in its return).
- `~/gov-os-runs/P60-rules-probe/` (made by the pinned launcher for s1 to s4; the launcher never removes it).
- `~/.claude/projects/-tmp-gov-os-lead-W2-60a-rules-probe/` (the CLI's session transcripts of these sessions).
- The raw stream-json logs: the lead's scratch `log/probe-*.jsonl` and `log/switch-*.jsonl`.
