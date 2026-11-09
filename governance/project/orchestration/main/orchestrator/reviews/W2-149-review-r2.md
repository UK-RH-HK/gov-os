**Sandbox check (step 0):** it holds. (a) The write to `/home/usain/gov-os-worktrees/.sandbox-trial-W2-149` failed with `OSError: [Errno 30] Read-only file system`. (b) `git hash-object -w --stdin` wrote blob `1ae28402a109`, and `git update-index --refresh` exited 0.

**`ps` check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing (exit 1).

- **task:** W2-149 (DAEO-52ku), independent review, round 2 of 2 (DEC-1010), profile FULL. Branch `w2/W2-149` at head `a929356ea`. The change reviewed is `8d4569bfef3c..a929356ea`.
- **status:** DONE. **Nothing blocks. Every KPI line, S1 to S21, passes.**
  - F1 is fixed, and so are F5 and F6. S12 now passes.
  - F3 and F8 are partly fixed and stay as rows.
  - I found three new findings (F13, F14, F15). All three are rows, because each needs something other than ordinary work.
- **work_completed:**
  - Read the ticket in full, round 1's record, JUDGEMENT.md and EMG-common.md.
  - Read round 2's whole diff: the script, the unit tests and the evidence record's "Round 2" section.
  - Read every path of the changed code in context: `run_canary`, `run_session`, `read_session`, `count_traces`, `check_traces`, `deliver`, `pack`, the end of `build_and_run`, and `main` with its two handlers.
  - Read the live acceptance cases and the stub's flag table.
  - Ran the tests read-only.
  - Searched twice for where the drawn id could go: every use of an id, then every log, write and print call. DEC-1064 forbids `gov retrieve` in the sandbox, so both searches were Grep.
- **files_changed:** none in any tree.
  - Step 0 wrote one blob to the git object store and refreshed the index's stat data.
  - `git status` lists untracked dotfiles (`.bashrc`, `.mcp.json`, `.idea`, …). These are the sandbox's own `/dev/null` mount points (character device 1,3, dated 2026-11-03), not files I wrote.
- **evidence:**
  - Unit tests and acceptance cases together: 150 passed, 4 deselected. The filter was `-m "not local_only and not live" -k "not real and not green_here and not time_limit"`, with `--optin=lifted --optin=breadth`.
  - The one stub-only case that `-k "not real"` drops, `test_w2_149_seed_content.py::test_s6_two_real_builds_draw_different_63_bit_seeds`, passed when run alone.
  - Total: 74 unit and 77 acceptance cases pass, with 3 live cases not run.
  - Scratch: 3.2M and 777 inodes in my TMPDIR.
- **tests:**
  - Everything ran through `heavy_slot.sh` with `PYTHONDONTWRITEBYTECODE=1` and an empty scratch HOME. `PYTHONUSERBASE=/home/usain/.local` was needed because pytest lives in the user site.
  - The heavy slot refuses `--basetemp` (DEC-898), so I ran without it.
  - Left out: the 3 live cases (S9 live, S11, S12). I relied on the CTO's live runs for those, as briefed.
- **discoveries:**
  1. The trace count can still read 0 without a completed check, but only through an unreadable or linked trace folder (F13).
  2. A trace left by the canary does not stop the real session. The run goes on and returns 22. This costs one session, the trace is counted, and no KPI line asks for more.
  3. The live S12 case searches only by the reported id. The script's `traces` covers the drawn id too, and the live run reported `traces` 0.
- **risks:** none new that block. F2 (the path map's hidden globs) is still an entry criterion before the first real writer run (DEC-803).
- **lessons:** pytest here needs `PYTHONUSERBASE` when HOME is planted, and `--basetemp` is refused by the slot.
- **proposed_decisions:** none. F13, F14 and F15 go to the Wave 3 hardening pass as rows.
- **unresolved:** whether the real `claude` reports the id passed with `--session-id` as its `session_id`. It does not matter for the count, because both ids are keys.
- **recommended_next_action:** READY by `verdict.py`. Merge after the CTO's close. Send F2 to the operator before step 4.

## Verdict per KPI line

- **S1 to S8: pass.** Round 2 did not change the build path. Its only additions there are a log line, two keys in `WALL.json` and `read_schema` called before B1. Round 1's reasoning still holds.
  - The result schema now refuses with 10 (`:1347-1349`) before anything is written. It is read once, and its sha256 goes into `WALL.json`.
- **S9: pass.** The canary still adds its own temporary folder. Its flags are the session's, except that it has its own drawn `--session-id`, which the CTO settled. The CTO's live run confirms both directions.
- **S10: pass.** `--session-id <uuid4>` is the closing flag before the prompt (`:728`), as settled. The id is drawn by the script, never given by the caller. `a[6:-3]` in the unit test and the acceptance S10 cases agree.
- **S11: pass,** on the CTO's live run.
- **S12: pass. F1 and F6 are closed.**
  - A drawn id is in `trace_ids` before each start: the canary's at `:800`, the session's at `:838`.
  - The canary's count runs in its `finally` once it has started (`:831-834`), so it runs on a pass, a 16, a timeout or an exception.
  - The session's count runs right after `read_session` (`:1539`), whether or not the output parses.
  - An exception between the start and the count reaches `main`'s catch-all, which counts again (`:1615-1619`). A `Refuse` cannot arise between the session and the count.
  - Ids that a session reports are added (`:816-819`, `:1536-1537`), and each entry is counted once (`seen` set).
  - The only ways left to a 0 without a check are F13 (a row).
- **S13: pass.**
  - The drawn and reported ids live only in `trace_ids`.
  - `check_traces` logs only the number.
  - The `error` line logs only the class name.
  - `argv` is never logged.
  - The unit test greps stdout, stderr, `launch.log` and `counts.json` for the drawn id and finds nothing.
  - The counts schema is unchanged (`traces`: integer ≥ 0).
- **S14: pass. F5 is closed.**
  - The labeller's `labels/` is made only after `regular(src)` and the sealed-folder check, and is removed if the copy fails (`:1078-1100`).
  - Writer round 1 checks its nearest existing folder before any `mkdir`. It makes the missing folders top-down and removes `hidden/` and every folder it made on any `BaseException` (`:1007-1033`).
- **S15: pass.** Unchanged. The new F1 test checks a timed-out session.
- **S16: pass.**
  - Delivery stays all or nothing and inside the root: the new folders are fresh `mkdir`s under a checked ancestor, so they cannot be links, and `deliver_file` still uses a temporary name, a hash check and a rename.
  - Rows F14 and F15 apply.
- **S17 to S21: pass.** Unchanged. There is still no `pkill`, `killall` or `pgrep` in the script.
- **Failure line 10:** pass by test design (planted HOME and roots).

## Findings

**F1 (scope: in, S12): fixed in round 2.** The id is drawn and always counted, as shown under S12 above.

**F6 (scope: in, S12): fixed in round 2.**

**F5 (scope: in, S14/S16): fixed in round 2.**

**F3 (scope: in, S4/S5): a row, partly fixed.** It is now recorded: `WALL.json` has `test_hook` and `launch.log` has `test_hook set` (`:1385-1387`, `:1515`). The hook still runs in real runs.
- Ordinary work: no, because it needs the variable exported by hand in the CTO's shell.
- Consequence: fails open.

**F8 (scope: in, S13/S14): a row, partly fixed.**
- Each schema is read once, with no link followed, and its sha256 goes into `WALL.json`. The result schema fails closed with 10.
- Two gaps remain:
  - Both schemas still come from the script's folder on disk, not from `--commit`.
  - An unreadable counts schema does not stop a real run. `main` stores `None` (`:1590`); the build, the canary, the session and the delivery all go ahead; `finish` only logs `counts schema unreadable` (`:376-377`) and prints unvalidated counts. Only `--counts-only` refuses (`:1572`).
- Ordinary work: no, because it needs a broken or uncommitted schema in the tool's own folder.
- Consequence: other (every counts value is typed by the script's own code).

**F13 (scope: in, S12): new. The trace count can still read 0 without a completed check.**
- `count_traces` silently skips a trace folder that is a link (`:904`) and an unreadable second-level folder (`:914-915`).
- `os.scandir(top)` on an unreadable top folder (`:906`) raises `PermissionError`.
  - In the canary's `finally`, that error replaces the canary's own outcome.
  - After the session it escapes `:1539`.
  - Either way, `main` tries again and swallows the `OSError` (`:1617-1619`), so `traces` keeps its default of 0 (`:361`).
  - Example: the session's check raises, and the line reads `stopped`, 21, `traces: 0`. The log has `error PermissionError stage 21` and no `traces checked` line.
- With a linked trace folder, a session that left traces is delivered with `traces: 0`.
- Fix: count through links (names only), and set `traces` to a value the schema refuses, or return 22, when the walk fails.
- Ordinary work: no, because Claude Code makes these folders itself, as plain folders the user can read; it takes a hand-made link or a permission fault.
- Consequence: fails open.

**F14 (scope: in, S16): new. Writer round 1's new destination check is uneven, and it refuses only after the session.**
- A link at the nearest existing folder (for example `fixtures/evaluation` as a link) refuses 20 after the session has spent its budget (`:1011`).
- A link higher up passes through `real_inside`'s realpath, though it still stays inside the root.
- The evidence record's "no link on the way" says more than the check does.
- Ordinary work: no, because the sets root is a plain folder the operator builds; a link in it is a deliberate layout.
- Consequence: other (fails closed; the product is kept in the tar; it costs one session).

**F15 (scope: in, S16): new, but not part of round 2's change. An auditor delivery can be reported as rejected after its file has landed.**
- The `AUDITS.log` line is appended after `miss-classes.json` is renamed into place (`:1102-1105`). An `OSError` there reaches `main`'s catch-all at stage 20, and the line reads `rejected`, 20, with the file delivered.
- Ordinary work: no, because it needs an unwritable runs folder or a full disk.
- Consequence: other (nothing leaks or is lost; the record is wrong).

**Round 1's rows, carried unchanged (round 2 did not touch their code; I confirmed each still holds):**
- **F4 (in, S18):** the expected-file count is too low for writers. Ordinary work: yes. Consequence: other.
- **F7 (in, S16):** writer round 1 into an existing set is refused only after the session. Ordinary work: yes. Consequence: other.
- **F9 (in, S16):** checker and auditor deliveries replace an existing file. Ordinary work: yes. Consequence: other.
- **F10 (in, S3):** two launches in the same second can collide. Ordinary work: no. Consequence: other.
- **F12 (in, S17):** a failed pack is reported as a clean delivery. Ordinary work: no. Consequence: other.
- **F2 (out, the path-map ACT):** new sets' destinations are under no hidden glob. Ordinary work: yes. Consequence: fails open. It is an entry criterion of step 4.
- **F11 (out):** the real HOME's settings may load into wall sessions. Ordinary work: yes. Consequence: other.

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
 {"kpi": "S12", "verdict": "pass", "findings": [{"id": "F13", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S13", "verdict": "pass", "findings": []},
 {"kpi": "S14", "verdict": "pass", "findings": [{"id": "F8", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S15", "verdict": "pass", "findings": []},
 {"kpi": "S16", "verdict": "pass", "findings": [{"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F14", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F15", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S17", "verdict": "pass", "findings": [{"id": "F12", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S18", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S19", "verdict": "pass", "findings": []},
 {"kpi": "S20", "verdict": "pass", "findings": []},
 {"kpi": "S21", "verdict": "pass", "findings": []}
]}
```