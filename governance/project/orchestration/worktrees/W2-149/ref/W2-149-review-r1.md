**Sandbox check (step 0):** (a) the write to `/home/usain/gov-os-worktrees/.sandbox-trial-W2-149` failed (`OSError: [Errno 30] Read-only file system`); (b) `git hash-object -w --stdin` wrote blob `1ae28402a109` and `git update-index --refresh` worked (exit 0). The sandbox holds.
**`ps` check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing (exit 1), at the start and at the end.

- **task:** W2-149 (DAEO-52ku), independent review, round 1, profile FULL. Branch `w2/W2-149`, head `8d4569bfef3c`, against `w2/integrate`.
- **status:** DONE. **One finding blocks: F1, on S12.** For a session that times out, the trace check reports 0 without having run. Every other KPI line passes. The other eleven findings are rows (eight in scope, three out of scope).
- **work_completed:**
  - Read the ticket in full, including its readings 1 to 5, and LAUNCH-SPEC §1 to §6.
  - Read all 1,550 lines of `indep_launch.py`, line by line.
  - Read the five schemas, the six template files, the acceptance README's interface, the evidence record and the ACT's layout.
  - Traced every refusal path (codes 10 to 17 and 20 to 22), including the catch-all handler, `_after_refusal` and `pack`.
  - Ran all tests read-only.
  - Put the script's own six documented lines through the tree's guard hook as the orchestrator, with a planted HOME.
- **files_changed:** none in any tree. Two side effects:
  - Step 0 wrote one blob to the git object store and refreshed the index's stat data.
  - My scratch driver lives at `/tmp/gov-launch-independent-auditor-xku2pcrw/claude-1000/-home-usain-gov-os-worktrees-W2-149/15beffa2-1d37-4377-9355-2752d2db423c/scratchpad/drive_guard.py`.
- **evidence:**
  - **Tests:** 141 passed, 3 live deselected: 64 unit and 77 acceptance, run with `--optin=lifted --optin=breadth -m "not live"`.
  - **Guard (S19):** all six of the script's own documented lines are allowed; each line with `--sets-root ~/gov-os-eval/indep-walls` is refused.
  - **Scratch:** 7.6M and 1,823 inodes in `$TMPDIR`.
- **tests:**
  - The first standard run gave 117 passed, 3 skipped, 24 deselected.
  - 23 of those 24 were dropped by the repository's opt-in plugin (`tests/conftest.py:37-53` keeps only the first row of each parametrized test). The 24th was dropped by `-k "not real"`: `test_s6_two_real_builds_…`, a stub-only case.
  - I re-ran with both opt-ins and all of them pass. No real model is involved in this ticket.
- **discoveries:**
  - (1) The trace check is blind when the session id is unknown (F1).
  - (2) New sets' destinations are not hidden by any glob (F2, the CTO's reading; my answer is below).
  - (3) The designer's S19 test drives the README's lines, not the script's docstring lines. I drove the docstring lines myself and they pass.
- **risks:** F2 must be closed before the first real writer run for a new set.
- **lessons:** In this repository, a reviewer needs `--optin=lifted --optin=breadth` to see every parametrized row.
- **proposed_decisions:** For F2, an ACT on the path map before real runs (an entry criterion, DEC-803), with the script-side refusal as a row.
- **unresolved:**
  - Whether Claude Code prints its JSON result, with the session id, when `timeout` sends it SIGTERM. No case shows it; F1 assumes it does not.
  - Whether `--restricted` stops user-level settings and `~/.claude/CLAUDE.md` from loading (F11; not verified).
- **recommended_next_action:** Fix F1 in a short round 2 and carry the in-scope rows along with it (DEC-802). Send the F2 path-map ACT to the operator before step 4.

## Verdict per KPI line

- **S1, S2: pass.** The brief and all six template files are read with `git cat-file` at `--commit` (`blob`, :384) and hashed before any write.
  - A template file needs exactly one matching `template` line: `t_lines.get(rel) != {sha}` at :1234, so two different lines refuse.
  - Comment lines are skipped. A brief line with a different path spelling or a trailing comment does not match its normalized path, so it refuses (10).
  - A second `brief` line for the same kind passes only if its hash is the given one, which is the owner's list working as intended.
- **S3: pass.** Code 12 is raised before `st.built`, so the planted entries are untouched. Every refusal after B1 packs the wall and removes the tree. A later run gets a new run id and B1 refuses anything that is not empty. See row F10.
- **S4: pass.** The order is: `seed.txt`, then `wait_past`, then the ledger line with fsync, then `wait_past`, then the tree and `input/`. `seed_check` checks the ledger line's hash and that `seed_ns < ledger_ns < least`. A tree or `input/` that already exists refuses with 13. See row F3.
- **S5: pass.** The selection follows the rule after the seed is drawn. No option takes a path. `AUDITS.log` is read from the runs folder (or its override, which is recorded).
- **S6: pass.** A given seed is accepted only with `--dry`, else 17. A real run draws `secrets.randbits(63)`.
- **S7: pass.**
  - `ls-tree` refuses modes 120000 and 160000 before anything is written.
  - At extraction, a link, an absolute path, `..`, `.git` or any non-file, non-folder member refuses (14).
  - Exclusions apply to files and folders; fnmatch's `*` also crosses `/`, which can only exclude more. Files are 0444, folders 0555.
- **S8: pass.**
- **S9: pass.**
  - The canary's target is in its own `mkdtemp` folder. The script checks that this folder does not overlap the sets root, trees, runs, repository, wall or tree, and adds it with `--add-dir` for the canary only, so `--restricted` alone would allow the Read. Only the wall hook refuses it (the settings' deny list does not name the temp folder).
  - Only a `Read` whose `file_path` is the exact target counts.
  - A non-zero exit, unreadable output, `is_error: true`, a timeout or an exception (stage 16) all refuse.
  - The CTO's live run confirms both directions.
- **S10: pass.** The flags match the ticket one for one. Tools come from `kinds.yaml`; model, budget and timeout from the approved brief, capped at the kind's. The environment is only those of `HOME PATH LANG USER` that are set. The command runs from the wall with stdin `/dev/null` in its own session. The prompt's hash is checked at start (11).
- **S11: pass** on the CTO's live run.
- **S12: fail (F1).**
- **S13: pass.**
  - Every schema object is closed and every string is a const, an enum or an anchored pattern.
  - Log words are literals or exception class names. stderr carries only status, code and reason. No path is printed.
  - `finish()` prints the counts even if their schema check fails (:357), but every value is typed by the script's own code, so no free text can get through.
- **S14: pass.** See row F5.
- **S15: pass.** `timeout` leads the process group; the script stops the group with a `killpg` backstop and a final sweep, and waits by pid. A budget subtype counts as stopped.
- **S16: pass.**
  - Delivery is all or nothing: one file goes by a temporary name, is hashed, then renamed; writer round 1 copies to a temp folder and cleans up on failure; writer round 2 moves the old set aside and rolls back on any error, `BaseException` included.
  - See rows F5, F7 and F9, and F2 (out of scope).
- **S17: pass.** See row F12.
- **S18: pass.** See row F4.
- **S19: pass,** including the script's own lines.
- **S20: pass.**
- **S21: pass.** No `pkill`, `killall`, `pgrep` or `/proc` appears in the script. pid and pgid are written to the counts folder.
- **Failure line 10:**
  - Pass by test design. The unit `World` plants HOME, and the acceptance cases add the `check_planted` tripwire.
  - The script's defaults derive only from `HOME`, so a test that forgot to set HOME would get as far as B1 only on a planted sets root with matching APPROVED hashes.

## The CTO's reading (hidden destinations)

The fix belongs to **the path map, an ACT outside this ticket**, not to a refusal in the script:
- The guard hides only what `sets_root_hidden` names, and it reads the main tree's copy. The script can only see `--commit`'s copy.
- Nothing runs against the real sets root until the briefs are approved, so under DEC-803 this is an entry criterion of step 4.
- Suggested globs: `fixtures/evaluation/*/hidden/**`, `fixtures/evaluation/*/XCHECK-r*.md`, `runs/*/miss-classes.json`. Also consider `runs/*/misses.jsonl`.
- A script-side check, refusing when the kind's destination matches no hidden glob at `--commit`, is cheap because B0 already reads those globs. I recommend it as a defence-in-depth row, recorded as F2.

## Findings

**F1 (scope: in, S12, code 22). For a stopped session, the trace check returns 0 without running.**
- `count_traces` returns 0 when `sid` is None (`indep_launch.py:845-847`). `read_session` returns a None id whenever the session's output does not parse (:826-827).
- A `claude -p --output-format json` killed by `timeout` writes nothing to stdout, so every timeout reports `traces: 0` without anyone having looked.
- A process killed with SIGTERM or SIGKILL is the one most likely to skip its own clean-up (`session-env/`, `todos/`).
- A trace in `~/.claude/projects` is free text the CTO can read. This check is the tripwire against that leak.
- Fix options:
  - (a) Draw the session id in the script and pass `--session-id`. This amends S10's flag list, so it is a DEC-105 choice.
  - (b) Allow `traces: null` in the schema, and return 22 as "unchecked" when the id is unknown.
- Ordinary work: yes, because a session past its timeout is the ordinary stop path S15 exists for.
- Consequence: fails open.

**F2 (scope: out, path-map ACT). New sets' destinations are under no hidden glob.**
- A writer's `fixtures/evaluation/<new set>/hidden/`, the checker's `XCHECK-r<round>.md` and the auditor's `runs/<audit>/miss-classes.json` match no `sets_root_hidden` glob, so every guarded role, the CTO included, can read them.
- See the CTO's reading above.
- Ordinary work: yes, because the first writer run for any new set delivers there.
- Consequence: fails open.

**F3 (scope: in, S4/S5). `GOV_INDEP_TEST_HOOK` runs in real runs and leaves no record.**
- `hook()` (:685-692) runs the executable at seven points in real runs, not just `--dry` ones.
- It can change `input/`, the tree or the settings between the seed and the canary, and neither `WALL.json` nor `counts.json` records that it ran.
- Fix: honour it only together with an override or `--dry`, or record it like the overrides.
- Ordinary work: no, because it needs the variable exported by hand in the CTO's shell; the tests set it per subprocess.
- Consequence: fails open.

**F4 (scope: in, S18). The expected-file count is too low for writers.**
- `expected` = 7 + staged copies + 3 (:1301). It counts the writer's delivered set as one file and ignores files in `out/` beyond `result.json`.
- During a run the hidden part holds `out/set/**` and its delivered copy at the same time.
- Also, `hidden_count`'s `os.walk` silently skips an unreadable folder.
- Ordinary work: yes, because every writer run delivers more than one file.
- Consequence: other (a 2,000-file margin below the guard's 10,000 walk cap; the wall's files go once it is packed).

**F5 (scope: in, S14/S16). A rejected run can leave an empty folder.**
- The labeller's delivery makes `labels/` in the sealed folder before checking that `out/labels.jsonl` exists (:1011-1018). A rejection then leaves an empty folder.
- Writer round 1's `makedirs(setdir)` comes before its checks in the same way (:954).
- Ordinary work: yes, because a first labeller run whose session wrote `result.json` but no labels does this.
- Consequence: other (an empty folder; nothing leaks or is lost).

**F6 (scope: in, S12). The canary's own traces are never counted.**
- The canary's session id is in its output, but the script never reads it or counts traces for it.
- Ordinary work: yes, every real run.
- Consequence: other (the canary sees only a random token file and the wall's note).

**F7 (scope: in, S16). Writer round 1 into an existing set is refused only after the session.**
- The script finds out at delivery (20). By then it has spent up to $25 and 7,200 s.
- A pre-check at B0 as well (keeping the delivery-time check) would save the session.
- Ordinary work: yes, because a round 1 named after an existing set (a slip, or a repeat) does this.
- Consequence: other (cost only; the product is kept in the tar).

**F8 (scope: in). The result and counts schemas come from the working tree.**
- They are read from the script's folder on disk (:1268), not from git at `--commit`, and no hash of them goes into `APPROVED` or `WALL.json`.
- Fix: read them at `--commit`, or record their sha256.
- Ordinary work: no, because it needs an uncommitted schema edit in the tree the CTO runs the tool from.
- Consequence: other (a looser schema lets a malformed result be delivered; the counts still carry fixed keys and numbers only).

**F9 (scope: in, S16). Checker and auditor deliveries silently replace an existing file.**
- `deliver_file` renames over an existing `XCHECK-r<n>.md` or `miss-classes.json`; only the labeller refuses an existing destination. `AUDITS.log` gains a second line.
- Ordinary work: yes, because a second checker run for the same set and round does this.
- Consequence: other (the replaced file came from an earlier run of this script and survives in that run's tar; the earlier manual notes are `XCHECK.md`, a different name).

**F10 (scope: in, S3). Two same-second launches can collide.**
- B1 accepts an existing empty wall. If two launches of one kind, set and round pick the same run id in the same second, the second one's `O_EXCL` failure on `seed.txt` (stage 13) packs and removes the first one's wall mid-build.
- Ordinary work: no, because `choose_run` moves to the next second as soon as it sees the first wall; it takes two launches in the same instant.
- Consequence: other (the first run then fails closed; the wall ends up in a tar).

**F11 (scope: out, the ticket's flag set or the template). The real HOME's settings may load into wall sessions.**
- With the real HOME, user-level `~/.claude/settings.json` and `~/.claude/CLAUDE.md` may load, because there is no `--setting-sources`. Not verified; it depends on what `--restricted` does.
- Ordinary work: yes, because the live runs use the real HOME to log in.
- Consequence: other (the deny rules and the wall hook refuse whatever an allow rule says; S11 live passed).

**F12 (scope: in, S17). A failed pack is reported as a clean delivery.**
- If `pack` fails it removes the tree but leaves the wall, and the result is still `delivered`, exit 0, with only "pack failed" in `launch.log`.
- Ordinary work: no, because it needs a full disk or a permission fault.
- Consequence: other.

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": []},
 {"kpi": "S2", "verdict": "pass", "findings": []},
 {"kpi": "S3", "verdict": "pass", "findings": [{"id": "F10", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S4", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S5", "verdict": "pass", "findings": []},
 {"kpi": "S6", "verdict": "pass", "findings": []},
 {"kpi": "S7", "verdict": "pass", "findings": []},
 {"kpi": "S8", "verdict": "pass", "findings": []},
 {"kpi": "S9", "verdict": "pass", "findings": []},
 {"kpi": "S10", "verdict": "pass", "findings": [{"id": "F11", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S11", "verdict": "pass", "findings": []},
 {"kpi": "S12", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S13", "verdict": "pass", "findings": []},
 {"kpi": "S14", "verdict": "pass", "findings": [{"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F8", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S15", "verdict": "pass", "findings": []},
 {"kpi": "S16", "verdict": "pass", "findings": [{"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S17", "verdict": "pass", "findings": [{"id": "F12", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S18", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S19", "verdict": "pass", "findings": []},
 {"kpi": "S20", "verdict": "pass", "findings": []},
 {"kpi": "S21", "verdict": "pass", "findings": []}
]}
```