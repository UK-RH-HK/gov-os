---
id: DAEO-wnnz
status: open
deps: []
links: []
created: 2026-10-29T15:55:50Z
type: task
priority: 1
assignee: engineer
external-ref: W2-56
tags: [wave-2, implementation, full, launch, sandbox, keystone-6]
wbs_id: W2-56
title: 'gov launch usable for every worker: the code graph in the session''s temp folder, the write list, no placeholders, a cleaned environment'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/codeintel/__init__.py
- src/gov/launch/launcher.py
- src/gov/launch/sandbox.py
- src/gov/launch/environ.py
- tests/unit/launch/**
- tests/unit/codeintel/**
- docs/changes/W2-56-CIT-E.md
kpis:
  success:
  - 'Inside a launched, sandboxed worker, a suite that builds the code graph runs: the code graph''s folder (DAEMON_BASE, src/gov/codeintel/__init__.py:35) is under the session''s own temporary folder, and outside a sandbox it stays where it is [DEC-799 item 1]'
  - 'The sandbox''s write list is the ticket''s allowed paths plus git''s folders (with the session''s temp folder, DEC-159, and its own run folder, DEC-728, as today), written as literal paths, since the Linux sandbox skips patterns: a worker''s script writing a file outside them (python3 -c with open(..., ''w'')), .gov-runtime/ outside the session''s scratch, another worktree and tests/acceptance/** for every role but the test designer included, is refused by the operating system [DEC-799 item 1, DEC-789, DEC-180, DEC-315]'
  - 'An allowed path the operating system cannot hold literally (a name pattern such as test_batch*) is never widened silently: the CIT-E states how each form is held, and what the operating system leaves open beside it is named there and in the launcher''s one line on stderr, with the guard''s refusal of the file tools still on [DEC-799 item 1, DEC-801]'
  - 'No placeholder file that the sandbox makes (.bashrc, .gitconfig, .mcp.json and the others, in the worktree or at a denied name) can reach a commit: a test plants each name the sandbox makes and shows it neither staged nor committed by an ordinary git add and git commit [DEC-799 item 1, DEC-402, row W2-I012]'
  - 'A launched session gets a cleaned process environment: PATH, HOME, the locale, what the CLI needs to sign in, its identity and the launcher''s own values (TMPDIR, CLAUDE_CODE_TMPDIR); none of the parent''s CLAUDE* and GOV* variables (its session id, messaging socket and token, child-session mark, effort, compaction window, subagent model, GOV_DEV_TIERS) and no PYTHONPATH reach it, shown by a test that starts the launcher with each set [DEC-826 Q5, lens E F13, DEC-784, DEC-877 item 4, row W2-M393]'
  - 'The remaining arguments that drop the guard or add context are refused after --, beside DEC-313''s: --restricted, --safe-mode, --agents, --plugin-dir, --plugin-url, --mcp-config and --system-prompt, each in its spaced and = forms; the CIT-E weighs an accepted-arguments list against this refusal list (lens E R6) [DEC-826 Q5, DEC-313]'
  - 'Sandboxed sessions started together in worktrees that share one .git do not fail on a missing .git/*.lock source path: the launcher starts sessions one at a time per repository (a short start lock), or the CIT-E shows another way; a test starts at least three launches at once [lens E F17]'
  failure:
  - A write outside the list from a script still succeeds; /tmp/gov-cbm-<uid> is on the write list (DEC-799 item 2); an allowed path widened with nothing naming it.
  - A launch whose sandbox cannot be built starts; a refusal the launcher makes today no longer refuses.
  - A placeholder file in a commit; a parent's CLAUDE*, GOV* or PYTHONPATH value in a launched session.
profile: FULL
sources:
- DEC-799
- DEC-789
- DEC-826
- DEC-801
- DEC-786
- DEC-180
- DEC-315
- DEC-159
- DEC-728
- DEC-402
- DEC-313
- DEC-784
- DEC-877
- DEC-941
est_loc: 250
acceptance_tests:
  path: tests/acceptance/W2-56/
  author: independent-test-designer (MR-3); written before implementation
track: A
list_rows: [W2-M393, W2-I012]
---
# W2-56 `gov launch` usable for every worker

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-56; DEC-799), widened by the accepted plan (`docs/plan/WAVE_2_REVISED_PLAN.md` §4.6: DEC-826 Q5's refused flags, lens E F13's cleaned environment shared with W2-60, lens E F17's lock retry); keystone 6, the leads' sandbox. Started now by the re-plan the owner accepted on 2026-10-29 (DEC-941), beside the memory work.

- **Why:** the `gov launch` trial (DEC-789): the sandbox refuses writes outside the worktree and lets git commit, but a worker cannot run a suite that builds the code graph, because `/tmp/gov-cbm-<uid>` is read-only inside the sandbox. A worker's script can write anywhere in its worktree; the launcher's `.gov-runtime/` deny rules are patterns, which the Linux sandbox skips; placeholder files appear in a worktree while a sandboxed worker runs. Until it closes, workers whose suites need the code graph start in the old form with DEC-789's tripwire (prompt §6, DEC-799 item 3).
- **Profile FULL:** the write list is the operating system's boundary for every worker, and the launcher refuses or starts the session; a mistake here fails open in ordinary work (DEC-801).
- **Place:** starts as soon as filed (DEC-941), stacked on `w2/integrate` (DEC-786), which holds W2-58's launcher (`af5d1a25`); W2-58 (`DAEO-5j8b`) is in the close queue and still names `src/gov/launch/**`. W2-05 (`DAEO-0z8c`, in progress) holds `src/gov/**/*.py` for the git environment of git calls: W2-56 leaves those lines as they are, and the later merge takes the conflict. W2-20 (`DAEO-r30l`) holds `src/gov/launch/gate*`: untouched. **Closes** before W2-27 starts (DEC-799 item 4); W2-21 follows it on the launcher.
- **Beside W2-60a:** both change `launcher.py`. Each puts its work in modules of its own (W2-56: `sandbox.py`, `environ.py`; W2-60a: `role.py`, `record.py`) and touches `launcher.py` at its call sites and argument checks only; the second to merge merges the first back first (DEC-786). The split of lens E F13 and DEC-826 Q5: W2-56 takes the process environment and the refused flags above; W2-60a takes what the session loads (no connectors, no user-level agents or skills, no model-side memory) and refuses the arguments it then sets itself (`--agent`, `--model` other than the role's, `--autocompact` and the rest).
- **Paths:** `src/gov/codeintel/__init__.py` for the daemon's folder only; `tests/unit/codeintel/**` for the daemon's folder only. A file outside the paths that the placeholder KPI needs (an ignore file, the guard's containment check) is a package.
- **The test designer's files** (MR-3: named here, not in the engineer's paths): `tests/acceptance/W2-56/**`.
