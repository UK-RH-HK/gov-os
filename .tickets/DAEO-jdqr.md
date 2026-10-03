---
id: DAEO-jdqr
status: open
deps: [DAEO-drvn, DAEO-0qs5, DAEO-o4fg]
links: []
created: 2026-10-03T13:05:33Z
type: task
priority: 2
assignee: engineer
external-ref: W1-46
tags: [wave-1, implementation, full]
wbs_id: W1-46
title: Worker session launcher (gov launch)
class: implementation
role: engineer
depends_on:
- W1-07
- W1-47
- W1-48
allowed_paths:
- src/gov/launch/**
- src/gov/cli/**
- template/governance/kernel/launch/**
- tests/unit/launch/**
- src/gov/guard/**
- template/governance/kernel/hooks/pretooluse*
- template/governance/kernel/roles/research*
- .claude/agents/research.md
- governance/project/roster.yaml
- tests/unit/guard/**
kpis:
  success:
  - gov launch refuses to start a worker session, with a non-zero exit and a named reason, unless the settings it built have the sandbox enabled, failIfUnavailable true, allowUnsandboxedCommands false and
    network strictAllowlist; it passes them through --settings and reads no sandbox setting from the repository; the settings it builds carry no excludedCommands (DEC-164) [CAP-61.a]
  - For each worker role (engineer, independent-test-designer, independent-auditor, research; a research or experiment session runs as GOV_ROLE=research) it builds a --settings file with the sandbox block and the role's Edit deny rules, and sets GOV_ROLE
    and GOV_TICKET; an acceptance test shows that a launched worker is sandboxed and that both variables reach the guard (DEC-161) [CAP-61.b]
  - 'Network profiles (DEC-158): engineer, independent test designer and independent auditor get an empty allowlist; research or experiment work gets an allowlist built from an owner-extensible list (GitHub,
    PyPI, npm, Hugging Face, arXiv, documentation sites); an acceptance test shows the profile applies, the empty list refusing a connection and the research allowlist accepting the research domains [CAP-61.c]'
  - 'A research or experiment session''s writes and installs stay inside its own experiment folder (a venv or local prefix): because the working directory is always writable inside the sandbox, the launcher generates at launch an Edit deny rule for every other path of the repository, from its top-level entries and the siblings along the path to the folder; the deny list is computed at launch, from the paths that exist then, with two exceptions: .git/, so that the session can commit its evidence record, and an entry whose name contains *, ? or [, which the sandbox skips on Linux (EXP-001 §1); a path created after launch outside the experiment folder is not in the list and is covered by the guard''s per-ticket allow-list, with the containment check reporting a change the guard did not see; an acceptance test shows that a research session''s Bash write to a sibling directory inside the repository fails, that a write to a new path created after launch outside the experiment folder is refused by the guard or reported as a containment finding, and that the generated list leaves out exactly the named exceptions; no worker role installs system-wide (DEC-157, EXP-001 §1, §3.4, §5.3) [CAP-61.c]'
  - 'A minimal research role is in the Wave 1 roster: a role file with purpose, allowed-path pattern, tools, model tier, authority level and handoff format, plus its roster entry; a research or experiment session runs as GOV_ROLE=research; the guard knows the role and holds its writes to its ticket''s allowed_paths (its experiment folder); its network grant comes from the launcher''s profile, the research allowlist of DEC-158, not from the guard (DEC-163) [CAP-22.d]'
  - 'In a launched research session an install command, the uv forms of DEC-174 included (uv add, uv sync, uv run --with, uvx), is not denied by the install rule and meets no settings ask rule, because the committed .claude/settings.json carries none once W1-47 has removed them (DEC-172): it succeeds into a venv or local prefix inside the experiment folder, within the ticket''s allowed_paths, and a system-wide install fails at the sandbox''s write fence (the sandbox stops a write outside the repository, and the generated Edit deny rules stop one to a path that existed at launch elsewhere inside it); the acceptance test of the install runs with the repository''s committed settings loaded; install commands stay denied for engineer, independent test designer and independent auditor, and the acceptance tests of W1-04 still pass (DEC-163, DEC-172, DEC-174) [CAP-25.e]'
  - It sets a per-session temp directory for each worker session, and an acceptance test shows whether the session uses it; if it cannot be overridden, the shared $TMPDIR is recorded as a residual in governance/project/bootstrap.md
    by the orchestrator (DEC-159) [CAP-61.d]
  - In a launched worker session a Bash write outside the repository through an opaque form (interpreter one-liner, command substitution) fails at the OS level, and a file-tool write outside it is refused
    by the permission rules and the guard [CAP-58.d]
  - 'The settings it builds carry the Read deny rule for the held-out directory, whose path the launcher takes from governance/project/held-out.yaml, the file W1-47 creates; from a launched worker''s Bash that directory looks empty; the test uses a stand-in directory, never the qualification oracle [CAP-49.b]'
  failure:
  - A worker session starts with the sandbox off, not strict or not fail-closed
  - A sandbox setting is read from the repository's settings
  - A worker role installs system-wide
  - A research session installs system-wide, or writes to a path that existed at launch outside its experiment folder
  - A research session's write to a path created after launch outside its experiment folder is neither refused by the guard nor reported by the containment check
  - A launched research session's install inside its experiment folder is stopped by a settings ask rule
  - A role other than research and the orchestrator gets an install command through
  - The settings the launcher builds carry an excludedCommands entry
  - An acceptance test or implementation file of this ticket reads or names the qualification oracle
profile: FULL
sources:
- DEC-152
- DEC-153
- DEC-158
- DEC-159
- DEC-161
- DEC-163
- DEC-164
- DEC-172
- DEC-174
- EXP-001
- CAP-49
- CAP-58
- CAP-61
- CAP-22
- CAP-25
est_loc: 220
acceptance_tests:
  path: tests/acceptance/W1-46/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-46 Worker session launcher (gov launch)

DEC-153 ticket 1, scoped by DEC-161: the launcher starts worker sessions only (engineer, independent test designer,
independent auditor, research or experiment), each inside the OS sandbox with its network profile (DEC-158) and a
per-session temp directory (DEC-159). The orchestrator's own session is not launched through it and is not sandboxed
(DEC-156). Configuration: `spike-sandbox/EVIDENCE.md` §5.2 and §5.3.

`gov launch` is a start command for the orchestrator and the owner. It is not one of the twelve governance operations
reserved by W1-07 (CAP-28.b), whose count is unchanged.

**The research role (DEC-163).** This ticket also delivers a minimal research role for the Wave 1 roster: the role
file, its roster entry, and the guard change that lets the role exist and install inside its experiment folder. The
sandbox's write fence, limited to the ticket's `allowed_paths`, is what denies a system-wide install. Inside the repository the fence is a generated list of `Edit` deny rules, because
the sandbox always leaves the working directory writable (EXP-001 §3.4, §5.3; S2A-F-03). The list is computed at
launch, so it names only paths that exist then. A path created later outside the experiment folder is covered by the
guard's per-ticket allow-list, and the containment check reports a change the guard did not see. The list leaves out
`.git/`, so that the session can commit its evidence record, and any entry whose name contains `*`, `?` or `[`, which
the sandbox skips on Linux (EXP-001 §1); both are left to the guard and the containment check (S2A-F-13). The full research
lifecycle (CAP-32) stays in Wave 3. Follows W1-47 because both change the guard files, and because the launcher reads
the held-out path from `governance/project/held-out.yaml`, which W1-47 creates (S2A-F-04).

**No settings ask rule on installs (DEC-172).** The committed `.claude/settings.json` asked before every `pip`, `uv`,
`npm install`, `curl` and `wget` command, and a later settings file cannot lift an ask rule (S2A-F-11). The owner
withdrew those rules: W1-47 removes them, and the guard's install rule decides alone. This ticket follows W1-47, and
its install test runs with the committed settings loaded.

**No `excludedCommands` (DEC-164).** The launcher sets none. Subagents inside a sandboxed worker session, and
`excludedCommands`, are open residuals until experiment EXP-002 (Wave 2).
