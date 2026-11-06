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
  - 'A suite that builds the code graph uses one daemon folder per test session (DAEMON_BASE, src/gov/codeintel/__init__.py:35), removed when the session ends, so no daemon folder is left behind (T-8); inside a launched, sandboxed worker that folder is under the session''s own temporary folder, and the suite runs there [DEC-799 item 1, INVESTIGATION-1 T-8] [re-scoped, DEC-1083]'
  - 'The sandbox''s write list is the ticket''s allowed paths plus git''s folders (with the session''s temp folder, DEC-159, and its own run folder, DEC-728, as today), written as literal paths, since the Linux sandbox skips patterns: a worker''s script writing a file outside them (python3 -c with open(..., ''w'')), .gov-runtime/ outside the session''s scratch, another worktree and tests/acceptance/** for every role but the test designer included, is refused by the operating system [DEC-799 item 1, DEC-789, DEC-180, DEC-315]'
  - 'An allowed path the operating system cannot hold literally (a name pattern such as test_batch*) is never widened silently: the CIT-E states how each form is held, and what the operating system leaves open beside it is named there and in the launcher''s one line on stderr, with the guard''s refusal of the file tools still on [DEC-799 item 1, DEC-801]'
  - 'No placeholder file that the sandbox makes (.bashrc, .gitconfig, .mcp.json and the others, in the worktree or at a denied name) can reach a commit: a test plants each name the sandbox makes and shows it neither staged nor committed by an ordinary git add and git commit [DEC-799 item 1, DEC-402, row W2-I012]'
  - 'A launched session gets a cleaned process environment: PATH, HOME, the locale, what the CLI needs to sign in, its identity and the launcher''s own values (TMPDIR, CLAUDE_CODE_TMPDIR); none of the parent''s CLAUDE* and GOV* variables (its session id, messaging socket and token, child-session mark, effort, compaction window, subagent model, GOV_DEV_TIERS) and no PYTHONPATH reach it, shown by a test that starts the launcher with each set [DEC-826 Q5, lens E F13, DEC-784, DEC-877 item 4, row W2-M393]'
  - 'The remaining arguments that drop the guard or add context are refused after --, beside DEC-313''s: --restricted, --safe-mode, --agents, --plugin-dir, --plugin-url, --mcp-config and --system-prompt, each in its spaced and = forms; the CIT-E weighs an accepted-arguments list against this refusal list (lens E R6) [DEC-826 Q5, DEC-313]'
  - 'Sandboxed sessions started together in worktrees that share one .git do not fail on a missing .git/*.lock source path: the launcher starts sessions one at a time per repository (a short start lock), or the CIT-E shows another way; a test starts at least three launches at once [lens E F17]'
  - 'A session started by `gov launch` (sandboxed) can connect to the shared reranker service''s socket (W2-112: one path in the user''s own folder, mode 0600) and gets its answers: the sandbox block allows that one Unix socket path and no other; the path comes from the same setting the service uses, never a pattern wider than it [DEC-1035, P-W2-112-T2 (a)] [moved from W2-127 S1, DEC-1083]'
  - 'Nothing else in the sandbox widens: no other Unix socket, no network port, `allowUnsandboxedCommands` false and `strictAllowlist` as today; `sandbox_faults` still refuses any other change; a planted sandboxed session that opens another Unix socket is refused [DEC-1035] [moved from W2-127 S2, DEC-1083]'
  - 'Measured, in docs/changes/W2-127-evidence.md: a sandboxed worker''s search reranked by the shared service (not the fallback), and its time against the fallback''s [DEC-1035] [moved from W2-127 S3, DEC-1083]'
  - 'A sandboxed session''s reranker fallback is logged and counted where the service''s own answers are, so `gov status` shows it (today it shows 0) [W2-112 review round 1, F3; the CTO as moderator, DEC-1010] [moved from W2-127 S4, DEC-1083]'
  - 'Signals reach the session''s process group, and temporary folders are removed on every ending [W2-M187, W2-M095, W2-L105]. [moved from W2-21 S5, DEC-1083]'
  - 'Launched sessions can run gov check, gov rebuild and their own suite inside the sandbox [W2-M275, W2-M094, W2-M097, W2-M181]. [moved from W2-21 S6, DEC-1083]'
  - 'The kernel template''s settings carry one narrow allow rule, Bash(gov launch:*) [DEC-715]. [moved from W2-21 S7, DEC-1083]'
  - 'A sandboxed worker''s temp folder is removed when the worker ends, whatever its exit, and a test shows none left under /tmp after a worker''s run [W2-M405, DEC-902] [moved from W2-21 S8, DEC-1083]'
  failure:
  - A write outside the list from a script still succeeds; /tmp/gov-cbm-<uid> is on the write list (DEC-799 item 2); an allowed path widened with nothing naming it.
  - A launch whose sandbox cannot be built starts; a refusal the launcher makes today no longer refuses.
  - A placeholder file in a commit; a parent's CLAUDE*, GOV* or PYTHONPATH value in a launched session.
  - 'A sandboxed session that can open any Unix socket or port beyond the reranker''s one path (containment widened). [moved from W2-127 F1, DEC-1083]'
  - 'A sandboxed search that still falls back while the service runs. [moved from W2-127 F2, DEC-1083]'
  - 'A raw claude launch stays unallowed in the template. [moved from W2-21 F1, DEC-1083]'
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
