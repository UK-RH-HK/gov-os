---
id: DAEO-o4fg
status: in_progress
deps: [DAEO-6cc2]
links: []
created: 2026-10-03T13:05:33Z
type: task
priority: 2
assignee: engineer
external-ref: W1-47
tags: [wave-1, implementation, full]
wbs_id: W1-47
title: 'Guard hardening: escape hatch, failed commands, oracle path'
class: implementation
role: engineer
depends_on:
- W1-45
allowed_paths:
- src/gov/guard/**
- template/governance/kernel/hooks/pretooluse*
- template/governance/kernel/hooks/posttooluse*
- template/governance/kernel/settings*
- .claude/settings.json
- governance/project/held-out.yaml
- tests/unit/guard/**
- tests/unit/install/**
kpis:
  success:
  - 'The guard''s PreToolUse hook denies any Bash call carrying dangerouslyDisableSandbox: true, whatever the role [CAP-62.a]'
  - The containment check is registered on PostToolUseFailure as well as PostToolUse, in this repository's settings and in the kernel template; a command that writes a file and then fails is caught [CAP-58.f]
  - 'The repository''s committed .claude/settings.json carries a Read deny rule with the qualification oracle''s absolute path; the oracle path is held in governance/project/held-out.yaml and in the committed deny rule built from it, and the acceptance test checks the committed rule statically, by its presence and its exact path in the file: it reads the configured value from held-out.yaml and asserts that the committed rule is built from it, so the test file carries no literal path and opens nothing under that path; the owner confirms at close that the value in held-out.yaml is the oracle''s path, because no automatic check may name it (DEC-162) [CAP-49.c]'
  - 'The guard denies any tool call whose input names the oracle path (a Read, Grep, Glob or Bash call, or any other tool), for every role, the orchestrator included; the guard takes the path from governance/project/held-out.yaml, and the guard''s behaviour is tested against a stand-in path, never the qualification oracle (DEC-162) [CAP-49.c]'
  - 'The committed .claude/settings.json carries no install or download ask rule: this ticket removes the Bash ask rules for pip, pip3, python -m pip, python3 -m pip, uv, npm install, cargo install, apt, apt-get, curl and wget, and leaves the Bash(sudo:*) deny rule and the other deny rules in place; the guard''s install rule then decides install commands alone, and in a launched worker session the sandbox backs it; an acceptance test checks the committed file statically, and the acceptance tests of W1-04 still pass (DEC-172) [CAP-25.f]'
  - 'The guard''s install rule recognises uv add, uv sync, uv run --with and uvx as installs, with or without options before the subcommand: from the orchestrator they return an ask decision, from engineer, independent test designer and independent auditor they are denied, and a uv run without --with is not classified by this change; the research role''s exception (DEC-163, W1-46) still lets them through inside its experiment folder; the acceptance tests of W1-04 still pass (DEC-174) [CAP-25.g]'
  - 'The guard function that resolves a role''s allowed paths fails closed when its session-role argument is missing: without that argument the orchestrator gets no wide scope (DEC-178), and a builder test in tests/unit/guard/ shows it (DEC-179)'
  failure:
  - 'A Bash call carrying dangerouslyDisableSandbox: true reaches execution'
  - Any tool call whose input names the oracle path is allowed, whatever the tool and whatever the call does (a read, a listing, a search, a write or a command), in a session started in the repository root
  - The committed Read deny rule is missing from .claude/settings.json, or its path differs from the oracle's absolute path
  - An acceptance test of this ticket reads or names the qualification oracle
  - The committed .claude/settings.json still carries an install or download ask rule, or the Bash(sudo:*) deny rule is gone
  - uv add, uv sync, uv run --with or uvx runs from the orchestrator without an ask, or from engineer, independent test designer or independent auditor without a denial
  - An implementation file of this ticket reads the qualification oracle, or names its path anywhere but governance/project/held-out.yaml and the committed Read deny rule
profile: FULL
sources:
- DEC-152
- DEC-153
- DEC-162
- DEC-172
- DEC-174
- DEC-179
- DEC-083
- EXP-001
- CAP-25
- CAP-49
- CAP-58
- CAP-62
est_loc: 60
acceptance_tests:
  path: tests/acceptance/W1-47/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-47 Guard hardening: escape hatch, failed commands, oracle path

DEC-153 ticket 2 and DEC-162. Follows W1-45 because both change the same guard files.

- `PostToolUseFailure` for Bash is already registered in this repository's settings by W1-05; this ticket makes the
  registration a tested requirement, here and in the kernel template.
- **How the two oracle layers are tested (S2-A round 1, F-04).** The committed `Read` deny rule is tested statically:
  the test reads the configured path from `governance/project/held-out.yaml` and checks that the rule in
  `.claude/settings.json` is present and built from that exact value. The oracle path is held in `held-out.yaml` and
  in the committed deny rule built from it; register entry DEC-067 names the directory historically (S2A-F-14). The
  owner confirms the value in `held-out.yaml` at close. The guard rule is tested by
  behaviour, against a stand-in path set through the same configuration. No test opens or names the oracle. The
  launcher (W1-46) takes the path from the same file.
- The failure KPI covers any allowed tool call that names the oracle path, not only reads.
- **The settings ask rules (DEC-172).** This ticket also removes the install and download ask rules from the
  committed `.claude/settings.json`. The guard's install rule (W1-04) then stands alone: W1-05's live attempts showed
  that an install no settings rule matched still got the hook's `ask`. This withdraws the settings second line of
  DEC-120 and DEC-151. The rules live in this repository's settings only; the kernel template carries none.
- **Four `uv` forms become installs (DEC-174).** A run of the classifier (`src/gov/guard/install.py`) over the commands
  the ask rules match showed which ones lose their prompt under DEC-172; `governance/project/bootstrap.md` lists them.
  The owner decided that `uv add`, `uv sync`, `uv run --with` and `uvx` keep an `ask` for the orchestrator: this ticket
  adds them to the install rule. `uvx` was matched by no settings rule before. The unit tests of the install rule live
  in `tests/unit/install/`, which is why that path is in `allowed_paths`. The other commands on the list stay
  without a prompt.
- The oracle is hidden from every session started in the repository root by two layers: the committed `Read` deny rule
  and the guard rule. An opaque Bash read in the orchestrator's own session is an accepted residual (DEC-162,
  `governance/project/bootstrap.md`).
