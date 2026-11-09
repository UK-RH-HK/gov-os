---
id: DAEO-wnnz
status: in_progress
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
- tests/unit/resources/test_w2_20_round3.py  # its stand-in CLI reads MARKS from the environment S5 now cleans: the value written into the stand-in (the engineer's P-2) [added, DEC-1112 (3)]
- template/.rulesync/permissions.jsonc  # the rulesync source of S14's allow rule, so a regeneration keeps it (the engineer's P-3) [added, DEC-1112 (3)]
- template/governance/kernel/settings.json  # S14's one allow rule, Bash(gov launch:*) (DEC-715), moved here from W2-21 S7 without its path [added, DEC-1083]
- tests/conftest.py  # S1's one daemon folder per test session and the tool off PATH (the designer's D-1) [added, DEC-1099 (1)]
kpis:
  success:
  - 'A suite that builds the code graph uses one daemon folder per test session (DAEMON_BASE, src/gov/codeintel/__init__.py:35), cleaned when the session ends, so no daemon folder is left behind; the real code-graph daemon runs only in W1-16 and W1-20, and on a change under `src/gov/codeintel/**` or to the tool''s pin, and elsewhere the tool is off PATH (T-8); inside a launched, sandboxed worker the session''s daemon folder is under its own temporary folder, and the suite runs there [DEC-799 item 1, DEC-1052, P1-PLAN T-8, INVESTIGATION-1 T-8] [re-scoped, DEC-1083]'
  - 'The sandbox''s write list stays today''s: the session''s temp folder (DEC-159) and its own run folder (DEC-728), with the literal deny rules for .gov-runtime/ outside the session''s scratch and, for every role but the test designer, tests/acceptance/**; no entry comes from the ticket''s allowed paths, and a worker''s script writing into another worktree or a denied name is still refused by the operating system, as today. Write scope to the ticket''s allowed paths (DEC-820 (4)) is the path-map guard''s: a file-tool write, or a Bash write the guard can name, outside them is refused for each worker role; a script''s write the guard cannot name, inside the worktree (python3 -c with open(..., ''w'')), is the known gap the CIT-E names, and its operating-system write list is set-up B''s Wave 3 row [DEC-799 item 1, DEC-789, DEC-180, DEC-315, DEC-820 (4)] [changed, DEC-1112 (1)]'
  - 'An allowed path that is a name pattern (such as test_batch*) is held by the path-map guard''s match, for the file tools and the Bash writes it names, and no sandbox entry is made from any allowed path, so nothing is widened silently; the CIT-E states how each form is held and what is left open beside it (S2''s script write inside the worktree) [DEC-799 item 1, DEC-801] [changed, DEC-1112 (1)]'
  - 'No placeholder file that the sandbox makes (.bashrc, .gitconfig, .mcp.json and the others, in the worktree or at a denied name) can reach a commit: a test plants each name the sandbox makes and shows it neither staged nor committed by an ordinary git add and git commit [DEC-799 item 1, DEC-402, row W2-I012]'
  - 'A launched session gets a cleaned process environment: PATH, HOME, the locale, what the CLI needs to sign in, its identity and the launcher''s own values (TMPDIR, CLAUDE_CODE_TMPDIR); none of the parent''s CLAUDE* and GOV* variables (its session id, messaging socket and token, child-session mark, effort, compaction window, subagent model, GOV_DEV_TIERS) and no PYTHONPATH reach it, shown by a test that starts the launcher with each set [DEC-826 Q5, lens E F13, DEC-784, DEC-877 item 4, row W2-M393]'
  - 'The remaining arguments that drop the guard or add context are refused after --, beside DEC-313''s: --restricted, --safe-mode, --agents, --plugin-dir, --plugin-url, --mcp-config and --system-prompt, each in its spaced and = forms; the CIT-E weighs an accepted-arguments list against this refusal list (lens E R6) [DEC-826 Q5, DEC-313]'
  - 'Sandboxed sessions started together in worktrees that share one .git do not fail on a missing .git/*.lock source path: the launcher starts sessions one at a time per repository (a short start lock), or the CIT-E shows another way; a test starts at least three launches at once [lens E F17]'
  - 'A session started by `gov launch` (sandboxed) can connect to the shared reranker service''s socket (W2-112: one path in the user''s own folder, mode 0600) and gets its answers: the sandbox block allows that one Unix socket path and no other; the path comes from the same setting the service uses, never a pattern wider than it [DEC-1035, P-W2-112-T2 (a)] [moved from W2-127 S1, DEC-1083]'
  - 'Nothing else in the sandbox widens: no other Unix socket, no network port, `allowUnsandboxedCommands` false and `strictAllowlist` as today; `sandbox_faults` still refuses any other change; a planted sandboxed session that opens another Unix socket is refused [DEC-1035] [moved from W2-127 S2, DEC-1083]'
  - 'Measured, in docs/changes/W2-127-evidence.md: a sandboxed worker''s search reranked by the shared service (not the fallback), and its time against the fallback''s [DEC-1035] [moved from W2-127 S3, DEC-1083]'
  - 'A sandboxed session''s search that the shared service does not answer (W2-145: the order kept, named unavailable, one FALLBACK line, unranked) is counted where the service''s other FALLBACK lines are, so `gov status` shows it (today a sandboxed session cannot write that log and it shows 0); the sandbox''s write list widens by at most that one log file, named in the CIT-E, or the CIT-E shows another way [W2-112 review round 1, F3; the CTO as moderator, DEC-1010; W2-145] [moved from W2-127 S4, DEC-1083] [changed, DEC-1097 (8)]'
  - 'Signals reach the session''s process group, and temporary folders are removed on every ending [W2-M187, W2-M095, W2-L105]. [moved from W2-21 S5, DEC-1083]'
  - 'Launched sessions can run gov check and their own suite inside the sandbox; gov rebuild inside the sandbox (it writes .gov-runtime/rebuild/ and codeintel/, which S2''s literal deny rules keep read-only, DEC-180) is a Wave 3 row with set-up B [W2-M275, W2-M094, W2-M097, W2-M181]. [moved from W2-21 S6, DEC-1083] [changed, DEC-1112 (3): the engineer''s P-1 (b)]'
  - 'The kernel template''s settings carry one narrow allow rule, Bash(gov launch:*) [DEC-715]. [moved from W2-21 S7, DEC-1083]'
  - 'A sandboxed worker''s temp folder is removed when the worker ends, whatever its exit, and a test shows none left under /tmp after a worker''s run [W2-M405, DEC-902] [moved from W2-21 S8, DEC-1083]'
  failure:
  - 'A file-tool write, or a Bash write the guard can name, outside the ticket''s paths still succeeds; the sandbox''s write list holds anything beyond today''s (the session''s temp folder, its run folder, and S11''s one log file if the CIT-E names it); /tmp/gov-cbm-<uid> is on the write list (DEC-799 item 2); an allowed path widened with nothing naming it. [changed, DEC-1112 (1)]'
  - A launch whose sandbox cannot be built starts; a refusal the launcher makes today no longer refuses.
  - A placeholder file in a commit; a parent's CLAUDE*, GOV* or PYTHONPATH value in a launched session.
  - 'A sandboxed session that can open any Unix socket or port beyond the reranker''s one path (containment widened). [moved from W2-127 F1, DEC-1083]'
  - 'A sandboxed search answered unranked while the service runs; an unranked sandboxed search that `gov status` does not count. [moved from W2-127 F2, DEC-1083] [changed, DEC-1097 (8)]'
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
- DEC-1010
- DEC-1035
- DEC-1052
- DEC-1083
- DEC-715
- DEC-902
- W2-112
- W2-127
- W2-21
- W2-I012
- W2-L105
- W2-M094
- W2-M095
- W2-M097
- W2-M181
- W2-M187
- W2-M275
- W2-M393
- W2-M405
- DEC-1099
- DEC-1097
- DEC-1098
- DEC-1112
- DEC-820
- W2-145
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

**The first half's points settled (the CTO, 2026-11-09):**
- ~~Nothing of W2-56 is built before the sandbox experiment's results reach the owner (DEC-1098 (4))~~: its first-half
  tests are on `w2/W2-56-tests` (`6ffcc77c0`). [changed, DEC-1112 (1): W2-56 builds now, below]
- **D-1:** `tests/conftest.py` added to the paths, for S1's two lines only [DEC-1099 (1)].
- **D-2:** moving `DAEMON_BASE` breaks W1-27's W2-67 cases that hard-code `/tmp/gov-cbm-<uid>`; a test designer
  revises them together with W2-56's merge [DEC-1099 (1)].
- **S11** (a sandboxed session's reranker fallback logged and counted) is revised after W2-145 (`DAEO-2tfd`) removes
  the private fallback [DEC-1097 (8)].

**The guard-alone outcome (DEC-1112 (1); the CTO, 2026-11-09):**
- W2-56 builds now on the path-map guard alone, with today's launcher sandbox for workers unchanged: not generated from
  the path map (no write entry from the allowed paths, no generated deny or read lists). Set-up B is a Wave 3 row.
- **Changed:** S2, S3 and F1 (write scope is the guard's; the script-write gap named) [DEC-1112 (1)]; S11 and F5 to
  W2-145's form (no private fallback: an unranked search, counted) [DEC-1097 (8)].
- **Kept as written:** S8 to S10 (the reranker's one socket is DEC-1035 (2)'s, not set-up B's: "unchanged" is read as
  "not generated from the path map"); S1's sandboxed part, S7's lock failure, S9, S13, F2's sandbox refusals and F4
  hold under today's sandbox and are tested in the second half.
- **S10** is measured by the CTO outside the sandbox (a real sandboxed session against the live service) before the
  close; the engineer leaves its section in `docs/changes/W2-127-evidence.md` to the CTO.
- The second half's tests: the independent test designer on `w2/W2-56-tests`, then the engineer with the tests'
  interface section in its brief.

**The second half's points settled (the CTO, 2026-11-09; delegated, DEC-1112 (3)):** tests `w2/W2-56-tests`
(`72f2433f0`, the designer's D-11 to D-14).
- **D-11 (a):** S11's count by `~/.cache/gov-os/rerank.log` on the write list, made by the launcher if missing, never
  a link; the one widening S11 allows.
- **D-12:** a shorter launcher temp folder (the `gov-launch-` prefix kept) and the daemon folders at the launcher's
  folder, found from `CLAUDE_CODE_TMPDIR`, so every role's folder fits the tool's 107-byte socket.
- **D-13, measured (a real `claude -p` session, a planted socket):** on Linux `network.allowUnixSockets` with the one
  path leaves the connect refused (EPERM), as with none; only `allowAllUnixSockets` connects, which S9 and F4 refuse.
  S8's settings-level form (the one path, nothing wider) is built, inert on Linux; S8's reach and S10 on Linux go to
  the owner as a DEC-105 choice (against DEC-1035 (2)). Until then a sandboxed search on Linux stays unranked, named
  and counted (S11).
- **D-14** (`rerank.py`'s chmod before connect) waits with D-13; not in W2-56's paths.
- **Outside the sandbox (the CTO's run, integrate's code):** the S2 real case passes; S7's is red on the sandbox's
  placeholder character devices (`git add -A` fails: S4's work); S13's is red on `gov rebuild` writing
  `.gov-runtime/rebuild/` under the literal deny rules (the engineer reconciles S13 with S2 or names the conflict).
  W1-27's revised W2-67 cases (D-2) are green, 5 of 5.

**The engineer's round-1 points settled (the CTO, 2026-11-09; delegated, DEC-1112 (3), listed in the digest):** head
`8eb7a39aa`, `gov accept W2-56` 255/0/5 in the sandbox.
- **P-1 (b):** S13's `gov rebuild` inside the sandbox deferred (Wave 3, with set-up B); no deny rule dropped, DEC-180
  kept; gov check and the suite stay in S13. (a) would widen today's sandbox into `.gov-runtime/`, against DEC-1112
  (1) and DEC-180; (c) needs the rebuild's and the code index's working folders moved, outside these paths.
- **P-2, P-3:** `tests/unit/resources/test_w2_20_round3.py` and `template/.rulesync/permissions.jsonc` added to the
  paths, one line each.
- `gov accept W1-27` stops on its README map (`ACCEPT_MAP_UNREADABLE`, as on integrate); its W2-67 cases are run
  directly outside the sandbox by the CTO.
