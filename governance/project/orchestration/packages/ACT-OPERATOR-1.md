# ACT-OPERATOR-1: the operator agent installed, its commit freeze, the guard's rule 2d, F26, the queue and the cron (DEC-1104 (2), DEC-1106, DEC-1107, DEC-1108 (5))

- **For:** the owner's operator, as the message in §8 (DEC-1104 (4)). It is (b) and (O) (guard code, a git hook, a
  crontab line, the operator's own install: OPERATOR-AGENT-1 §7 step 2), so it is applied by hand one last time.
- **By:** an agent for the CTO, 2026-11-09. Built and rehearsed in two clones with a planted HOME. **Nothing live is
  changed** until the operator runs §8. Reviewed independently (§6).
- **Sources:** DEC-1104 (2) (OPERATOR-AGENT-1, Q1 to Q7 as recommended; Q5: the cron launches from a queue, the CTO
  only queues), DEC-1104 (4) (ACTs as messages); DEC-1106 (1)-(5) (F15, the call log, the freeze in the install, F7
  kept, then this ACT); DEC-1107 (F21, merged at `ddc3414b`); DEC-1108 (5) (every session refused writes into
  `~/.gov-os/guard-calls`, in this ACT with the freeze's rule); DEC-1028 (6) (the commit freeze); DEC-1057 (rehearsed);
  W2-148 (`DAEO-xafn`, merged `511a4a17`) and its README's interface; W2-148's review records
  (`.gov-runtime/scratch/orchestrator/log/W2-148-review-r1..r3.md`, `-f21.md`); ACT-INDEP-WALLS-1 (`147706ae`, the
  model and the walls' three layers); ACT-GUARD-CALLLOG-1 (the post-calllog hook).
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/operator-1/` (§5).

## 1. What lands
| Part | What | Why |
|---|---|---|
| **install** | `~/gov-os-operator/install/`: the 13 code files of `governance/project/operator/` as the ACT's commit holds them (the 12 merged files, `operator_run.py` among them with F26, and the new `freeze_gate.py`), the install's own `operator-settings.json`, and `APPROVED` (sha256sum's form, every file but itself). Files 0444, the folder 0755 (the freeze is written there). `~/gov-os-operator/queue/` (0700) | DEC-1104 (2); W2-148's interface: `install/APPROVED`, the freeze `install/act-in-progress.txt` (DEC-1106 (3)) |
| **guard rule 2d** | `.claude/hooks/pretooluse.py`: every session the guard judges is refused writes into the folders of the path map's new `write_refused` block. File tools by the path they name, links followed; a Bash line by the writes the guard resolves (its own and its inline code's). Built on whichever hook is live: before ACT-GUARD-CALLLOG-1 (`d5be03dbb48e` → `4b528eb87118`) or after it (`a7981319f877` → `97a84e770058`, its answer carrying the call log's rule id `2d`); `apply.sh check` refuses any other hook | DEC-1106 (3) "the guard denies the CTO's session writing it"; DEC-1108 (5) |
| **path map** | `governance/project/path-map.yaml` (`3f7ae7f83d99` → `40085090306e`): `write_refused:` `~/gov-os-operator` except `queue/`, and `~/.gov-os/guard-calls` | the package's "closing that folder to the CTO's writes, except the queue" (OPERATOR-AGENT-1 §7 step 2) |
| **the freeze in the commit path** | `.git/hooks/reference-transaction` (`6fbbf312bacd` → `099de326c45b`): in the `prepared` state, only while the freeze exists, `install/freeze_gate.py` refuses an update of the live branch that touches the ACT's repository paths or the operator's control paths, unless its commits carry the operator's own `Act:`/`Act-sha:` trailers. No freeze: one `[ -e ]`, nothing else | DEC-1106 (3), DEC-1028 (6); W2-148 review r1 F5 |
| **the CTO's tools read it** | `merge_queue.py` (`36c8e1573285` → `1f3b1d44f507`): its landing stops cleanly (entries kept) while the freeze exists. `tools/landing_select.sh` (`984d4dfc7f82` → `9e55c0b88032`): `--hook` waits for the freeze to clear (an hour at most, then DEFERRED, state not advanced), `--fg` refuses while it holds; and every range it examines goes to the install's `landing_check.py` (S16), each flagged commit one P1 inbox item. Its tests `+5` cases | DEC-1106 (3) "the CTO's tools and the landing hook read it"; OPERATOR-AGENT-1 §3 (the landing check) |
| **F26** | `operator_run.py` (`fb6092758b01` → `41271992b637`): `.claude/scheduled_tasks.lock` leaves the control-file snapshot (§3) | W2-148 review r3 F26, an entry criterion of this ACT |
| **tests** | `tests/unit/operator/test_act_operator_1.py` (new, 18 cases): F26, the freeze gate (11 cases), the merge queue's wait | the code parts above |
| **cron** | one crontab line, the old table backed up (§4) | DEC-1104 (2) Q5 |

**The install's layout** (the owner's own files there are never read or written: `CLAUDE.md`, `.claude/`, `hooks/`,
the dated `log/*.log`; rehearsed unchanged):
```
~/gov-os-operator/
  install/                 0755; 14 files 0444 + APPROVED (APPROVED_SHA below); act-in-progress.txt only while a run applies
    act_class.py class-rules.yaml opcommon.py operator_run.py operator_launch.py landing_check.py freeze_gate.py
    verdict.py (pinned: 277c8ca9…d909378, byte for byte tools/verdict.py) brief.md reviewer-brief.md win_toast.ps1
    wall/operator_wall_hook.py wall/settings.json.tmpl operator-settings.json APPROVED
  queue/                   0700: the CTO's only door, one <stamp>-<ACT>.req per request; taken/ done/ rejected/ by the launcher
  acts/<ACT>-<sha12>/      the frozen, read-only copies (G1), made by runs
  wall/                    the walled session's folder, rebuilt per launch (restricted mode, the wall's settings and hook,
                           a canary first: ACT-INDEP-WALLS-1's three layers)
  log/operator.jsonl act-approvals.jsonl journal.json operator.lock session.json session-output.json launch.lock
      calls.jsonl operator-launch.out      the agent's own named files, beside the owner's dated logs
```
- **`APPROVED`'s sha256, live:** `157a9dc01fcaab78b04dc78f153df8b077460a33ffaa9027cb05bc4b8e474ad7` (computed from
  `install.sums` and the built settings; every result and the digest print it).
- **`operator-settings.json`** (`a7d6dcbf40be`): `repo` the main tree, `home` `/home/usain`, `claude`
  `/home/usain/.local/bin/claude` (cron's PATH has no `~/.local/bin`). Every other key takes the merged default.
- **The two briefs, approved by you (DEC-1109 (1)):** `brief.md`
  `51c459cfbcfec47652df455844480a56a5bc91b5fba3bcf57dc807c5dbf08cc2` (with your one change, committed at `0240833b4`:
  "unless the program's final result line asks for it"), `reviewer-brief.md`
  `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a` as written; the rule table `class-rules.yaml`
  `0f130073bbbd06f7b56c7be44e72d42ffe6460bc49f4c6a684f81f499979bab1`.

## 2. The guard rule (2d) and the freeze
- **Rule 2d** sits after 2c and before G-14 (all denials, so the order changes only the message), reads the main
  tree's block only (a branch cannot weaken it), runs only for a write tool or Bash, and fails closed on a malformed
  block (every write refused, reads untouched). An open folder is matched by its own name under the real root, never
  followed: a link in `queue/` pointing into the root stays refused. It reaches every session but the operator agent's
  walled session, which runs outside this guard (`claude --restricted` in `~/gov-os-operator/wall/`), and the owner's
  hand operator, whose folder loads no repository hook. **Limits** (2d judges resolved writes, as rules 1 and 5 do): a
  target in a variable the line does not set, and a script that writes in its own code, are let through; the
  backstops are `APPROVED` (one byte off refuses every run), the operator's own control hash of its install, and the
  freeze's readers.
- **Scope: the whole `~/gov-os-operator` but `queue/`**, as the approved package words it ("closing that folder to the
  CTO's writes, except the queue"): the install and freeze, and also `acts/` (frozen copies a later edit could change
  between G1 and the apply), `log/` (the lock, the journal) and `wall/`. Narrower (the install only) is a one-line
  change if you prefer it.
- **The freeze, its writer and its readers:** written only by `operator_run.py` (before `apply.sh apply`, removed by
  the run that wrote it); read by G9 (the operator's own hold), the commit path (`freeze_gate.py`), the merge queue
  and the landing tool. The CTO's records and tickets go on during an apply; only commits on the ACT's paths and the
  control paths (`.claude/**`, `.rulesync/**`, the path map, the dead-man's and the sentinel's files) wait, because a
  commit there mid-apply locks the operator (DEC-1106 (1)).

## 3. F26: what leaves the control-file list, and what stays
W2-148's review r3 names two files Claude Code writes under `.claude/**` during a dry run: `scheduled_tasks.lock` and
`settings.local.json`.
- **Leaves: `.claude/scheduled_tasks.lock`.** Claude Code's scheduler lock (`sessionId`, `pid`, `procStart`,
  `acquiredAt`), rewritten whenever a session takes the scheduler. It governs no agent, it is git-ignored, and the
  snapshot was the only check that saw it. Skipped by its exact path (a file of that name elsewhere stays).
- **Stays: `.claude/settings.local.json`.** Claude Code writes it on a "don't ask again" answer, but it holds
  `permissions.allow` and hooks: that write *is* a loosening of a control, and an (a) ACT's apply.sh writing it
  unlisted would be caught only by the after-check (the clone's dry run has no ignored files). A change there during an
  apply therefore still refuses and holds the lock with a P1, as DEC-1106 (1) says.
- **Also stays, by the same reasoning (review F6):** `.claude/hooks/__pycache__/*.pyc`, rewritten by Python only when
  a hook module's source changes. Only a guard-code (b) ACT whose check goes red, or that you undo, can meet it; that
  P1 is expected.

## 4. The queue and the cron
- **The CTO only queues:** one file `~/gov-os-operator/queue/<stamp>-<ACT>.req` holding `ACT-<id> <64 hex>` (the
  manifest's sha256), the bundle in `.gov-runtime/scratch/orchestrator/acts/<ACT>/`. Rule 2d leaves it `queue/` and
  nothing else.
- **The cron line** (the owner's crontab; the old table backed up by `apply.sh` and restored by its undo):
  ```
  */10 0,8-23 * * * /usr/bin/python3 -I /home/usain/gov-os-operator/install/operator_launch.py >> /home/usain/gov-os-operator/log/operator-launch.out 2>&1  # DEC-1104 (2) (5), ACT-OPERATOR-1: the operator agent launched from its queue (the CTO only queues)
  ```
  Every 10 minutes, the last launch at 00:50 so a 45-minute session ends before the quiet hours (02:00 to 07:30) and
  the nightly's window (03:50 to 08:00), which the launcher holds on anyway (review F9). `python3 -I`: no user site,
  no inherited `PYTHON*`; PyYAML is the system's. One launch at a time (the launcher's own lock).

## 5. The files (drafts; checked by hash before they apply)
| File (`drafts/operator-1/`) | sha256 (first 12) |
|---|---|
| `pretooluse.pre.candidate.py`, `pretooluse.post.candidate.py` (+ `.diff`) | `4b528eb87118`, `97a84e770058` |
| `path-map.candidate.yaml`, `path-map.patch` | `40085090306e` |
| `code/operator_run.py`, `code/freeze_gate.py`, `code/merge_queue.py`, `code/test_act_operator_1.py` | `41271992b637`, `00e8ce13249e`, `1f3b1d44f507`, `5ced364cdf06` |
| `reference-transaction.candidate` | `099de326c45b` |
| `landing_select.candidate.sh`, `test_landing_select.candidate.sh` | `9e55c0b88032`, `16aa390131c6` |
| `operator-settings.json`, `crontab.line`, `install.sums` | `a7d6dcbf40be`, `77dcf4661777`, `29ea26233916` |
| `apply.sh` (check, apply, undo) | `6bcdcf2f6ca8` (DEC-1109: only its `SUMS` line changed from `7e9398ad91ca`, the reviewed one) |
| `build.py`, `freeze.py` (the builders), `op_cases.py`, `op_rehearsal.py`, `rehearse.sh` | the rehearsal's own |
| `rehearsal-pre.log`, `rehearsal-post.log`, `REHEARSAL.md` | §6 |

`apply.sh check` and `apply` stop unless every draft and every install source hashes as built, the hook is one of
the two rehearsed, and every other part is as before (the map `3f7ae7f83d99`, `operator_run.py` `fb6092758b01`,
`merge_queue.py` `36c8e1573285`, the git hook `6fbbf312bacd`, the landing tool `984d4dfc7f82`, no install, no
operator line in the crontab). **If anything moves before you apply, the CTO rebuilds (`build.py`, `freeze.py`) and
re-runs the rehearsal.**

## 6. The rehearsal (DEC-1057) and the review
Two clean runs on 2026-11-09, each from a fresh `env -i` shell in a `--no-hardlinks` clone at the main tree's head
(`b7a373cf9`) with a worktree, a planted HOME (the owner's operator files planted in `gov-os-operator/`, a dummy sets
root), a crontab stub seeded with the live table, and the clone's git hooks pointed at a safe copy (no clone ref update
can start a live job). **pre:** the clone's hook before ACT-GUARD-CALLLOG-1 (`d5be03dbb48e`), **0 failures**
(18:03–18:31). **post:** the clone's hook after it (`a7981319f877`, live since 18:13), every hook run logging into the
rehearsal's own folder, **0 failures** (18:03–18:28). Record: `REHEARSAL.md`, `rehearsal-pre.log`, `rehearsal-post.log`.

| Step | Result (pre; post the same where run) |
|---|---|
| Guard suites before / after | `test_guard_fix_4` 467 / 467 passed; `test_g14` 150 passed, 1 skipped, 1 failed / **the same** (`test_w2_91_tests_today` fails at this head without the ACT); live hook and reads 85 / 85; `guard4_check.py --settings <clone>` **501 run, 0 failed** before and after; `walls_check.py repo <clone>` **331, 0 failed** before and after |
| Rule 2d's cases (`op_cases.py`, 9 roles, HOME planted) | before: every R case allowed (the gap, 243); after: **412 cases, 0 failed**: 252 refused by 2d (Write, Edit, MultiEdit, NotebookEdit, redirects, `cp`, `tee`, `sed -i`, inline code, a variable set on the line, a link from /tmp, a link in `queue/`), 144 allowed (queue writes, reads, the program run by hand, prose, siblings), 16 known limits allowed |
| The operator's suites before / after | W2-148 acceptance 169 / 169; `tests/unit/operator` 184 / **202** (+18); the merge queue's units 97 / 97; `test_landing_select.sh` 49 / **54** ok (+5), 0 failures |
| `apply.sh` | check ready; apply; a second apply refused; check "already applied"; the commit 4 M + 2 A |
| Replay of the real calls of the last 48 hours | 7,898 unique calls: **0 changed** (7,861 allow, 37 deny); post 7,897: **0 changed** |
| **The CTO's session refused a write into the install** | a real session (haiku, `orchestrator` on DAEO-sdxk): Write and Bash into `install/` and Bash into `guard-calls` **refused by rule 2d**; the queue write and a Read of `install/brief.md` allowed; nothing written but the queue file |
| **A past class-(a) ACT through every gate** | ACT-RERANK-GPU-SLOTS-1 (DEC-1031; its module at `d03ce368b` into the planted HOME's reranker environment) queued, then the launcher as the cron runs it (`python3 -I`, `env -i`, no config): the canary, then the real walled session (`claude --restricted`, 19 s, about $0.02); G1–G9, the recompute, the apply, its check, the after-check: **applied**, votes a/a/a, logged, pushed; the owner's `undo` line: **undone**, both files gone |
| **A class-(b) ACT, without and with the yes** | one record_only path into the test map (SELECT-FIXES-1's kind): with no yes, **refused at G6**, HEAD unchanged; with `yes ACT-SELECT-FIXES-1R 546f2e6c` planted as the owner's turn: **applied** and committed (`Role: operator`, `Act:`, `Act-sha:`, `Class: b`, `Review:`, `Approved-by:`) through the freeze gate; the freeze removed by its run; the owner's `undo` line: **undone** |
| **The freeze honoured** | while a freeze holds: the CTO's commit on the ACT's path **refused**, on `.claude/settings.json` **refused**, on another path committed; the freeze gone: committed. `landing_select.sh`: `--fg` HELD (exit 4), `--hook` deferred past its wait (state kept), waits and then examines the whole range once the freeze clears; the landing check filed one P1 for a CTO guard commit, none for the operator's or a ticket's |
| The owner's files in the planted root | unchanged |
| `apply.sh undo` | every part as before the ACT's commit; the git hook, the landing tool and the crontab as before; `queue/`'s record kept; check "ready to apply" again |
| Live files (the hook and modules, the map, the settings, the git hook, the operator code, the landing tool, `~/.claude/settings.json`, `~/gov-os-operator` but its logs, the crontab) | **unchanged**, hashed before and after each run |

Run 2 was stopped by its own guard when the live `~/.gov-os/guard-calls` appeared: the owner's operator had applied
ACT-GUARD-CALLLOG-1 at 18:13. `apply.sh check` on the live main tree now reads "ready to apply (the hook is
post-calllog)".

**The independent review** (`.gov-runtime/scratch/orchestrator/reviews/ACT-OPERATOR-1-review-r1.md`, a fresh session,
READY by `verdict.py`, 12 findings none blocking). Fixed in the drafts: F1 (undo's state with `queue/`'s record), F2
(the planted sets root), F3 and F4 (the gate on pack-refs and gc, and on a detached main tree), F5 (the merge queue
reads the freeze), F8 (every source checked before the first write; undo checks every part first and clears a partial
install), F9 (the cron's hours). In this package: F6 (§3), F7, F10, F11, F12 (§7). **Round 2**
(`ACT-OPERATOR-1-review-r2.md`, a narrow re-check of those fixes and both final rehearsal logs, `apply.sh` as read
`7e9398ad91ca`): **READY** by `verdict.py`, every fix confirmed; two new findings, neither ordinary work, both failing
closed (§7 items 9 and 10).

**After DEC-1109 (1)** (the brief's one change, `0240833b4`): `install.sums`, the expected `APPROVED` and `apply.sh`'s
`SUMS` line rebuilt (nothing else in `apply.sh` changed). Re-run in a fresh clone at `0240833b4` (`rehearsal-dec1109.log`,
18:52–18:53, **0 failures**) the steps the brief touches: `apply.sh` check and apply (the install's own APPROVED check
ok), the commit (4 M, 2 A), the (a) ACT through the real walled session (its wall holding the new brief, `51c459cf…`):
applied, undone; the (b) ACT: refused at G6 without the yes, applied and committed with it, undone; the freeze's
commit cases; the owner's files unchanged; `apply.sh undo` then "ready to apply"; live files unchanged. W2-148's
acceptance tests 169/169 and `tests/unit/operator` 184/184 on `0240833b4`. `apply.sh check` on the live main tree:
"ready to apply (the hook is post-calllog)".

## 7. Residuals, and what follows
1. **Order with ACT-GUARD-CALLLOG-1 (review F7):** met: CALLLOG-1 is live (`b7a373cf9`), so this ACT lands on the
   post-calllog hook. Undo in reverse (this ACT's undo first, if both are ever undone).
2. **The owner's undo has no queue form (F10):** the launcher only runs `run`. Until a queue form exists, your
   `undo ACT-<id> <sha8>` line is carried out by your operator, one line:
   `python3 ~/gov-os-operator/install/operator_run.py undo <ACT> <manifest sha>` (it reads your line from the CTO
   session's transcript, as the yes is read).
3. **Path-map and deny-list (a) ACTs wait for DEC-1108 (2) (F11):** until the corpus builder and its check exist, the
   after-check replays only the operator's own dry-run commands (`calls` = `log/calls.jsonl`, which rule 2d closes to
   the CTO). That build puts its corpus where the operator reads it and sets `calls` in the install's settings (a
   change to the install: yours).
4. **The landing check's rate (F12):** on the last 300 landings it would have filed 4 P1 items (CTO merges without a
   `Task:` trailer, decision records touching the path map): about one a day, each a true control path outside an ACT.
5. **A (b) ACT queued before your yes** is refused at G6 and logged; that refusal (before G7) is not pushed. The CTO
   reads `log/operator.jsonl` and pings you for the yes; it queues again after it.
6. **The CTO's habits change:** it writes the session id to `log/cto-session.txt` (the yes and the undo are read from
   that transcript), and it no longer writes the scratch's `log/act-in-progress.txt` for a queued ACT (the launcher
   would hold on it: W2-148 review r1 F5).
7. **Follow-ups (the CTO's):** `calllog_check.py`'s rule list gains `2d`, or its `validate` rejects 2d's lines once
   both ACTs are live; the suites that run the live hook point `GOV_GUARD_CALLS_DIR` at a temporary folder (DEC-1108
   (5)); the two `test_w2_148_trial.py` files get distinct names (review O2); guard4's planted-root cases (O1).
8. **Threat model (unchanged):** ADR-0001's (honest mistakes). A deliberate forgery (a hand-rewritten install, a planted
   transcript line) stays a Wave 3 row, as OPERATOR-AGENT-1 §6 says.
9. **A deletion of the live branch passes the gate (review r2 F1):** so that `pack-refs` and `gc` work during an apply
   (git 2.43 sends each packed ref's loose deletion as `X → 0`, in its own transaction), a deletion goes on. A real
   `update-ref -d` of `w2/integrate` during an apply would then make the operator's commit fail: it undoes, holds the
   lock and sends you a P1 (fails closed). Not ordinary work; a follow-up if it ever matters.
10. **The merge queue's tests read the live freeze path (review r2 F2):** run during a live apply, they would stop with
   exit 4. Follow-up: their conftest sets `MERGE_QUEUE_OPERATOR_FREEZE` to a temporary path.

## 8. The operator's steps: the message
> **ACT-OPERATOR-1 (DEC-1104 (2), DEC-1106, DEC-1107, DEC-1108 (5)): install the operator agent.** In the main tree,
> about two minutes. ACT-GUARD-CALLLOG-1 is already applied, so `check` says "post-calllog". The install carries the
> two briefs you approved (DEC-1109 (1)): `brief.md` `51c459cf…f08cc2`, `reviewer-brief.md` `e8670330…61ff81a`.
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> G=.gov-runtime/scratch/orchestrator/drafts/operator-1
> bash $G/apply.sh check     # "check: ready to apply (the hook is post-calllog)" (exit 0)
> bash $G/apply.sh apply     # backup; the code; ~/gov-os-operator/install with APPROVED and queue/; the map; the hook; the git hook; the landing tool; the crontab line last; "state applied"
> git add .claude/hooks/pretooluse.py governance/project/path-map.yaml governance/project/operator/operator_run.py governance/project/operator/freeze_gate.py governance/project/orchestration/tools/merge_queue.py tests/unit/operator/test_act_operator_1.py
> git diff --cached --name-status    # expect exactly 4 M and 2 A: those six files
> git commit -m "ACT-OPERATOR-1: the operator agent installed in ~/gov-os-operator/install (APPROVED), launched by the cron from its queue; the guard refuses every session's writes into the operator's folder but queue/ and into ~/.gov-os/guard-calls (rule 2d); the commit freeze in the commit path and the CTO's tools; F26" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1104, DEC-1106" --trailer "Role: owner"
> sha256sum ~/gov-os-operator/install/APPROVED    # expect 157a9dc01fcaab78b04dc78f153df8b077460a33ffaa9027cb05bc4b8e474ad7
> crontab -l | tail -1                            # the operator's line, */10 0,8-23
> ```
> **Undo:** `bash $G/apply.sh undo`, then commit the six restored files the same way, subject "ACT-OPERATOR-1 undone".

`apply.sh undo` checks every part first and refuses while a run holds the freeze, the journal or the lock, or a request
waits; then the crontab line first, every part byte for byte, the install removed; `queue/`'s record, `acts/`, `wall/`
and the agent's own logs stay as the record (rehearsed, both kinds).

**Then the CTO, the same day:** merge `w2/integrate` into the live worktrees (each runs its own copy of the hook);
write its session id to `log/cto-session.txt`; queue nothing until the first eligible ACT (an opt-in or test-map
coupling ACT, not a path-map one: §7 item 3); file the follow-ups of §7 item 7.
