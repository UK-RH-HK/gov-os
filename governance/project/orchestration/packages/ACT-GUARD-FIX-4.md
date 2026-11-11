# ACT-GUARD-FIX-4: rules 1 and 5 judge only what resolves (G-1, G-2); `rm` free but the catastrophic (O-7 wider)

For the owner's operator. Under DEC-1050 (8) and (12) and DEC-1052; plan rows G-1, G-2 and O-7, step P1-3 (i). Built by
the E3 engineer (ticket DAEO-sdxk), 2026-11-03. **The independent review returned READY (§6).**

**Basis (DEC-1052):**
- **(2):** today's hook refuses honest work again and again, and an `rm` prompt stalls a session until the owner answers. Without the catastrophic-`rm` rule, one bad `rm -rf` loses the repository.
- **(4):** fewer refusals and prompts, with role separation (1) kept on every write that resolves.

## 1. What changes
- **Rules 1 and 5 judge only the writes the guard resolves.** A Write or Edit, or a Bash write whose target resolves:
  - into `tests/acceptance/` is still refused to every role but the independent test designer;
  - outside a reviewer's records is still refused to reviewers and auditors.

  A target the guard cannot work out is let through. It is no longer guessed at from the words the command holds. The backstops:
  - G-1's landing check, live since today (`tools/land.py`, `acceptance_authors`);
  - the reviewed tree's `git status` (G-2).
- **Rule 5 names the CTO's review folder.** `.gov-runtime/scratch/orchestrator/reviews/` is now a record path. Today's hook refused the E1 reviewer's own record there twice (a Bash `cat >` and a Write, 12:22–12:23), and the CTO transcribed it. Logged rows 75 and 76 (2026-11-02) are the same case.
  - **Cause:** the hook's `REVIEW_PATHS` listed only `docs/probes/`, `docs/audit/`, `docs/assessment/` and `.gov-runtime/scratch/review/`/`audit/`. The folder itself (`mkdir -p …/reviews`) never matched, because the test needs the trailing `/`.
  - **Now:** files under `reviews/` are allowed. The folder itself is allowed only when the command makes it with `mkdir`. Deleting or moving the folder is still refused, and so is every other folder (`src/`, `tests/`, `briefs/`, `log/`, …).
- **Code's writes into the tests:** these are judged against the trees of this repository (this tree, its worktrees and run clones, and any folder under `~/gov-os-worktrees/` or `~/gov-os-runs/`). A scratch folder in `/tmp` whose name holds `tests/acceptance` no longer counts (logged row 81).
- **`rm` is free for every role, except the catastrophic.** These are refused with a plain reason:
  - the repository's root;
  - any `.git`;
  - the main tree's tracked files;
  - a folder that holds the project, its worktrees or its scratch;
  - anything outside the project (the main tree, `~/gov-os-worktrees/`, `~/gov-os-runs/`) and its scratch (`/tmp`, `/dev/shm`, `.gov-runtime/scratch/`).

  An `rm` whose variable the guard cannot resolve is judged as if the variable were empty (`rm -rf "$D"/` is `rm -rf /`). The reason then names the cure: `${D:?}`.
- **Every other rule is unchanged:** 2 (hidden half, held-out), 3 (secrets) and 4 (installs, `sudo`).
- **The settings stop asking for `rm`.**
  - `.claude/settings.json` and `.claude/settings.local.json` hold no `rm` rule.
  - The ask is in the **user settings, `~/.claude/settings.json` lines 16–18**, in `permissions.ask`:
    ```
          "Bash(rm -r:*)",
          "Bash(rm -rf:*)",
          "Bash(rm:*)",
    ```
  - These three lines go. The four `owner-ping` asks (lines 19–22) stay. `settings_rm_ask.py` removes exactly these entries: tested on a copy, the diff is those 3 lines, and its undo gives a byte-identical file.

**Files (SHA-256, first 12):**

| File | Hash | Size or change |
|---|---|---|
| `pretooluse.py` | 8cf1daf2804b | |
| `bash_writes.py` | bb246a21735e | +122/−2 |
| `ACT-GUARD-FIX-4.diff` | a7d3d9ceeb70 | 639 lines; applies to today's hooks, git blobs 52ab9bc647b1 and ceb6fdefbb5f, to give exactly the two files |
| `guard4_check.py` | 4136269dc4c4 | 4 cases re-baselined, 12 added |
| `test_guard_fix_4.py` | 1871f7b6d123 | |
| `settings_rm_ask.py` | 0dbc06457737 | |

## 2. Measured (each through `heavy_slot.sh`, pin `pin-9894b0cf`)

| | Today's hook (ACT-GUARD-FIX-3) | This candidate |
|---|---|---|
| The 87 logged refusals, replayed from their transcripts: refused | **20** | **13** |
| … of them by rules 1 and 5 | 9 | **0** |
| … the 83 logged false refusals: still refused | 16 | 11 (all rule 2's listing, W2-42a's fix, and rule 4's `sudo` in heredoc text: rules this ACT leaves as they are) |
| … the 4 logged true refusals | 4 refused | rows 73, 80 (hidden half) refused; rows 75, 76 (a reviewer's record in `reviews/`) pass |
| … newly refused | — | 0 |
| Today's 2 rule-5 refusals (the E1 review's record) | 2 refused | 0 refused |
| ACT-GUARD-FIX-3's planted cases (252): the 169 to refuse | 169 refused | 116 refused; 53 let through by design (`LET_THROUGH`: unresolvable targets, or `/tmp/tests/acceptance`) |
| … the 83 to pass (or ask) | 83 | 83 |
| `tools/guard4_check.py` (54) | PASS | 50/54; the 4 that differ are re-baselined in the new copy |
| The new `guard4_check.py` (65) | FAIL (12) | **PASS** |
| `tools/test_guard_fix_3.py` | 269 passed, 1 skipped | 53 failed (exactly the `LET_THROUGH` names), 216 passed, 1 skipped |
| `test_guard_fix_4.py` (451) | 182 failed | **451 passed** |
| Real `rm` calls since 2026-10-30 (562, every transcript) | asked every time | 1 refused: the operator's folder (`~/gov-os-operator`), where this hook is not registered, so **0 in practice**; 0 crashes; slowest 0.02 s |

Notes on the measurements:
- **The logged rows** come from `log/guard-refusals.jsonl`, rebuilt by tool_use id. 73 match W2-42a's fixture exactly. The 3 that differ (rows 23, 67, 72) give the same answers in both spellings.
- **The catastrophic cases (55 commands × 2 roles)** are all refused. Among them: `~`, `/`, `$HOME`, an empty variable, a loop holding `~`, `bash -c`, `$(…)`, a heredoc script run by `bash`, `\rm`, `/bin/rm`, `command rm`, the repository's root, `.git`, tracked files, the worktrees' and runs' folders, `/tmp`, `/dev/shm`, `~/.config` and `~/.bashrc`.
- **The 21 honest deletes** all pass. Among them: scratch, `/tmp`, `/dev/shm` locks, a worktree's own files, a removed worktree's scratch, `mktemp` folders, `${X:?}`, `find -delete` and `git rm -n`.

## 3. The commands (your operator, in the main tree)
Preconditions:
- the review of E3 is READY;
- E1's landing check is live: `grep -n "def acceptance_authors" .gov-runtime/scratch/orchestrator/tools/land.py` shows line 82;
- no merge-queue landing is running.
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
D=.gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4
T=.gov-runtime/scratch/orchestrator/tools
git status --short -- .claude/
git rev-parse HEAD:.claude/hooks/pretooluse.py HEAD:.claude/hooks/bash_writes.py | cut -c1-12
sha256sum $D/pretooluse.py $D/bash_writes.py $D/guard4_check.py | cut -c1-12
mkdir -p $D/backup
cp -p .claude/hooks/pretooluse.py .claude/hooks/bash_writes.py $T/guard4_check.py $D/backup/
cp $D/pretooluse.py $D/bash_writes.py .claude/hooks/
cp $D/guard4_check.py $T/guard4_check.py
python3 $T/guard4_check.py --settings /home/usain/Dynamic-Agentic-Engineering-OS | tail -1
GUARD_FIX4_HOOK=$PWD/.claude/hooks/pretooluse.py bash $T/heavy_slot.sh python3 -m pytest -q -n 6 -p no:cacheprovider $D/test_guard_fix_4.py | tail -1
git add .claude/hooks/pretooluse.py .claude/hooks/bash_writes.py
git commit -m "ACT-GUARD-FIX-4: rules 1 and 5 judge only what resolves (G-1, G-2); rm free but the catastrophic (O-7); a reviewer's record in the CTO's reviews/" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1050, DEC-1052" --trailer "Role: owner"
python3 $D/settings_rm_ask.py check
python3 $D/settings_rm_ask.py apply
diff ~/.claude/settings.json.pre-act-guard-fix-4 ~/.claude/settings.json
```
What each line must show (stop at the first that differs and tell the CTO):
- `git status --short -- .claude/`: nothing.
- The two blobs: `52ab9bc647b1` and `ceb6fdefbb5f`, today's hooks.
- The three hashes: `8cf1daf2804b`, `bb246a21735e` and `4136269dc4c4`.
- `guard4_check.py --settings`: ends `PASS`. Before the ACT it was run on the candidate by path only: the `--settings` form needs the files in place. It runs the registered hook line itself, so it covers:
  - a planted catastrophic `rm` refused (`rm -rf ~`, the repository's root, `.git`, a tracked file, an empty variable, `~/.bashrc`);
  - a reviewer's record write allowed in `reviews/`, by Write and by `mkdir -p … && cat > …`;
  - a reviewer refused for deleting `reviews/` or writing `briefs/`.
- The test file: `451 passed`.
- `settings_rm_ask.py check`: names lines `[16, 17, 18]`.
- `apply`: prints the backup's path.
- `diff`: exactly the three `rm` lines removed.

**When it takes effect:**
- The hook: on the next tool call of a session in the main tree (the hook file is read at each call). A lead's worktree gets it when `w2/integrate` is merged into it.
- The user settings: Claude Code reads them at session start, so sessions started after the change stop asking. A running session may keep asking until it restarts.

**Check after (the next day):** `rm` prompts in the permission log drop to none, and no catastrophic delete happened.

## 4. The undo
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
D=.gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4
git revert --no-edit "$(git log -1 --format=%H --grep='^ACT-GUARD-FIX-4:' -- .claude/hooks/)"
cp -p $D/backup/guard4_check.py .gov-runtime/scratch/orchestrator/tools/guard4_check.py
python3 $D/settings_rm_ask.py undo
python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py --settings /home/usain/Dynamic-Agentic-Engineering-OS | tail -1
```
- The revert puts both hook files back together; `$D/backup/` holds copies too.
- **Never restore one hook file alone.** The hook and the module go together, and a mismatch fails closed on every Bash call.
- The last line must end `PASS` (the old 54 cases).

## 5. The risk
**What is let through that today's hook refused.** Writes into the tests or outside a reviewer's records whose target the guard cannot work out:
- `perl`/`node` code;
- `exec`, `getattr`;
- Python loops, functions and globals;
- computed paths;
- variables bound by `read`, `if` or `source`;
- patches;
- scripts run by forms the guard does not read.

These are 53 planted cases, and G-1 and G-2 accept them (DEC-1050 (12)):
- An engineer's commit touching `tests/acceptance/` without `Role: independent-test-designer` is refused at landing.
- A reviewer's stray write shows in the reviewed tree's `git status` (the lead template's line, P1-7).

**The `rm` rule's limits:**
- It reads `rm` only. `find -delete`, `xargs rm`, `git clean` and `shutil.rmtree` in Python are not judged. They were never asked for either, so this is no worse than today.
- `mv` of the repository's root is not refused.
- A glob of more than 20,000 paths is refused as too many to check.
- If `git ls-files` fails in the main tree, an `rm` inside the main tree is refused (fail closed).

**Rule 5's `reviews/` folder** holds every reviewer's records. A reviewer can overwrite another reviewer's record there, as it can in `docs/probes/` today. Rule 5 has never told one reviewer's record from another's.

## 6. The independent review: READY
Reviewed 2026-11-03 by an independent auditor (Sonnet, read-only), judged by `JUDGEMENT.md`; the record is
`.gov-runtime/scratch/orchestrator/reviews/e3-guard-fix-4.md`; READY computed by `tools/verdict.py`: **(True, [])**,
all four KPIs pass (rules 1 and 5, `rm`, the reviews/ records, this ACT). It re-ran the 451 tests and the new
`guard4_check.py` (PASS), about 130 planted rule-1/5 cases with resolving targets (all refused), about 250 `rm` cases
(catastrophic refused, honest passed), crash and speed probes (0.05-0.10 s; malformed input fails closed), and
`settings_rm_ask.py` apply/undo (byte-identical). Its findings, none blocking (Wave 3 rows): F1 a literal write into
ANOTHER tree's `tests/acceptance/` is allowed (pre-existing; G-1 backstops it at landing); F2 rare `rm` forms (`xargs
rm`, `git clean -fdx`, loops over `rm`) are not judged; F3 an honest delete outside the project (`~/.cache/x`) is
refused with a reason; F4-F6 below; F7 an unreadable glob fails closed.
- **F6, answered by the CTO:** removing the three `ask` lines does stop the prompt: `~/.claude/settings.json`'s
  `permissions.allow` holds `"Bash(*)"` (read 2026-11-03 with the owner's approval), and the project's
  `.claude/settings*.json` hold no `rm` rule. The two hook files are copied in one step after the backups; the undo
  restores both together.
- **F4:** `settings_rm_ask.py apply` rewrites the file with `json.dumps(indent=2)`; your file is already in that form
  (a 3-line diff measured): the `diff` line in §3 shows it; stop if it shows more than the three lines.
- **F5:** `undo` writes the backup back, so it loses any settings change made after the apply: undo only right after
  the apply, or remove the three lines' return by hand.

## 7. Recommendation
Apply, **confidence high on the measurements and the review, medium-high on the new code on the guard's path**
(about 250 lines in the hook and 120 in the module; pinned by 451 tests and the 562-call history).

## 8. Applied (2026-11-03), with one correction to §3
- **The stop:** the owner's operator stopped at §3's test step: "1 failed, 461 passed", not the ACT's "451 passed".
  The cause was the ACT's order, not the hook: §3 copies the new `guard4_check.py` into `tools/` before the test, and
  the new copy renames four planted cases (now let through under G-1/G-2, expecting `allow`) and adds 11 (54 to 65),
  while `test_guard_fix_4.py`'s `test_let_through_names_are_planted_cases` still named the four by their old names.
  The 451 had been measured with the old copy in place.
- **The fix (the CTO, the test only):** the check accepts either copy (each of the four by its old name expecting
  `deny`, or by its new name expecting `allow`); the hook and `guard4_check.py` unchanged. Re-run on the files in
  place: **462 passed**. Test sha256 `0b37aa565dc3`; the finishing steps:
  `.gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4/FINISH-20261103.md`.
- **Applied:** every line of the finishing steps matched; 462 passed; the hooks committed `3bc25241` (the two files,
  `Role: owner`); the three `rm` lines removed from `~/.claude/settings.json` (backup
  `~/.claude/settings.json.pre-act-guard-fix-4`), the four `owner-ping` asks kept. The CTO confirmed
  `guard4_check.py --settings` PASS from its own session afterwards.
- **For the undo (§4):** the expected test count after an undo is the old copy's; `undo` restores the settings backup
  above (review F5: only right after the apply).
