---
id: DAEO-jdqr
status: open
deps: [DAEO-drvn, DAEO-0qs5]
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
- W1-48
allowed_paths:
- src/gov/launch/**
- src/gov/cli/**
- template/governance/kernel/launch/**
- tests/unit/launch/**
kpis:
  success:
  - gov launch refuses to start a worker session, with a non-zero exit and a named reason, unless the settings it built have the sandbox enabled, failIfUnavailable true, allowUnsandboxedCommands false and
    network strictAllowlist; it passes them through --settings and reads no sandbox setting from the repository [CAP-61.a]
  - For each worker role (engineer, independent-test-designer, independent-auditor, research or experiment) it builds a --settings file with the sandbox block and the role's Edit deny rules, and sets GOV_ROLE
    and GOV_TICKET; an acceptance test shows that a launched worker is sandboxed and that both variables reach the guard (DEC-161) [CAP-61.b]
  - 'Network profiles (DEC-158): engineer, independent test designer and independent auditor get an empty allowlist; research or experiment work gets an allowlist built from an owner-extensible list (GitHub,
    PyPI, npm, Hugging Face, arXiv, documentation sites); an acceptance test shows the profile applies, the empty list refusing a connection and the research allowlist accepting the research domains [CAP-61.c]'
  - A research or experiment session's writes and installs stay inside its own experiment folder (a venv or local prefix); no worker role installs system-wide (DEC-157) [CAP-61.c]
  - It sets a per-session temp directory for each worker session, and an acceptance test shows whether the session uses it; if it cannot be overridden, the shared $TMPDIR is recorded as a residual in governance/project/bootstrap.md
    by the orchestrator (DEC-159) [CAP-61.d]
  - In a launched worker session a Bash write outside the repository through an opaque form (interpreter one-liner, command substitution) fails at the OS level, and a file-tool write outside it is refused
    by the permission rules and the guard [CAP-58.d]
  - The settings it builds carry the Read deny rule for the held-out directory, and from a launched worker's Bash that directory looks empty; the test uses a stand-in directory, never the qualification
    oracle [CAP-49.b]
  failure:
  - A worker session starts with the sandbox off, not strict or not fail-closed
  - A sandbox setting is read from the repository's settings
  - A worker role installs system-wide
  - An acceptance test or implementation file of this ticket reads or names the qualification oracle
profile: FULL
sources:
- DEC-152
- DEC-153
- DEC-158
- DEC-159
- DEC-161
- EXP-001
- CAP-49
- CAP-58
- CAP-61
est_loc: 180
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
