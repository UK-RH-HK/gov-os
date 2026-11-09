# W2-148 — the independent test designer's brief, the replay round: DEC-1108 (2) (DAEO-xafn)

You are the independent test designer for **W2-148** (`.tickets/DAEO-xafn.md`: read it, with its DEC-1106 note and
the new **DEC-1108 (2) note** at its end, and S15's line): the operator agent (DEC-1104 (2),
`governance/project/orchestration/packages/OPERATOR-AGENT-1.md`). Your earlier rounds wrote `tests/acceptance/W2-148/`
(169 cases, merged into `w2/integrate`). Read your own README (the settings, the replay's interface under "The replay
(S15)", N-9, N-10) and support module first.

## What the owner decided (DEC-1108 (2), in `docs/DECISION_REGISTER.md`; the reasoning in
`governance/project/orchestration/packages/ACT-GUARD-CALLLOG-1.md` §2 (the log), §3 (a) and §7 item 2)
The guard now appends one line per decision to a call log (hashes, never contents). S15's replay must no longer trust
the `calls` file: the CTO builds the 48-hour call set from the transcripts, and the agent **checks it against the
guard's log by sha256 both ways before it re-judges anything**. A dropped, altered or invented call fails the check,
so the CTO cannot shape the replay.

## The interface (put it in your README, replacing "The replay (S15)"'s first sentence; the engineer builds to it)
- **The call set** (the `calls` setting's file), JSON lines:
  - line 1, the header: `{"v": 1, "window": {"since": ISO, "until": ISO}, ...}` (other keys ignored);
  - a call: `{"id", "time", "session", "role", "ticket", "agent", "sha256", "event": {"tool_name", "tool_input", "cwd"}}`
    (the line's own `sha256` is ignored: the agent recomputes it from the event);
  - a dropped call: `{"id", "time", "session", "sha256", "dropped": "<reason>"}`, no `event` (a call the CTO's tool
    may not copy, such as one naming the sets root): checked against the log, never re-judged.
- **The guard's log:** new setting `guard_calls` (a folder; default `<home>/.gov-os/guard-calls`). One file per UTC day,
  `<YYYY-MM-DD>.jsonl`; each line `{"v": 1, "time": ISO ms "Z", "session", "role", "agent", "ticket", "tool",
  "decision", "rule", "tree", "ms", "sha256", "keyed"}`; a marker file `<day>.jsonl.capped` means that day was cut short.
- **The hash:** `sha256(json.dumps({"tool": tool_name, "input": tool_input}, sort_keys=True, separators=(",", ":"),
  ensure_ascii=False).encode("utf-8"))`, hex.
- **Before anything is re-judged** (when an (a) ACT touches the path map or a deny list, as today), the replay refuses
  (so the after-check undoes the ACT and pushes a P1, as any replay refusal does today) unless all hold:
  1. **The window:** the first line is the header; `until` is no later than the clock plus 5 minutes and no older than
     the clock minus `replay_stale_h` hours (new setting, default 12); `until - since` is at least 48 hours.
  2. **Well formed:** every other line is a call (an `event` object) or a dropped call (a 64-hex `sha256` and a
     non-empty `dropped`); anything else is malformed (fail closed, as today).
  3. **The log readable and whole:** the folder exists; no day file from `since - 2 min` to `until + 2 min` has a
     `.capped` marker; no line in those files is malformed.
  4. **Set to log:** every set line whose `time` lies in `[since, until]` has a log line with the **same session** and
     the same sha256 (a call's recomputed from its event; a dropped call's from its line), the log line's time within
     `[since - 2 min, until + 2 min]`.
  5. **Log to set:** every log line whose time lies in `[since + 2 min, until - 2 min]`, whose `session` is a UUID
     (lower-case 8-4-4-4-12 hex) and whose `tree` is `main` or `worktree`, has a set line (call or dropped) with the
     same session and sha256; a null `sha256` counts as missing. Other sessions (the suites' fixed names) and trees
     (`run`, `scratch`, `other`) are not required.
  - The refusal's reason names the mismatches (at most 5 of each kind): a set call by its `id`, a logged call by its
    session's first 8 characters, its sha256's first 12 and its time; never an input's text.
- **Then the re-judging, as today,** over the set's calls (not the dropped ones) in the window, each with the **role
  and ticket of its matching log line** (they win over the set's); the dropped calls are counted by reason. The
  replay's own runs of the hook never write the live log: the hook is run with `GOV_GUARD_CALLS_DIR` set to a folder
  inside the replay's own temporary folder (never `guard_calls`).

## What the cases must show (add them first; the engineer then builds)
Plant the set and the log in the temporary folder (your support module's world; a `guard_calls` key in its config).
- **Guard (green after):** a well-formed set and log that agree both ways (calls and one dropped call), with the
  existing S15 addition: the ACT stays applied; the listed refused call still lets it stay.
- **The existing S15 cases** (a planted path-map addition whose replay turns an unlisted call to refused: undone, P1;
  the listed one: stays) **updated** to plant a header and a matching log, so they test the re-judging, not the check.
- **Refused (undone, P1, the reason naming the mismatch), one case each:** a set call with no log line (an invented
  call); a call whose input was altered by one character (so its hash no longer matches); a logged live call missing
  from the set (a dropped call, by the CTO); a set call whose hash is logged only under **another session**; a window
  shorter than 48 hours; a stale window (`until` older than 12 hours by the clock); no header; a capped day in the
  window; a malformed log line; a missing log folder.
- **Not required (green):** a logged call by a session named like a suite (`guard4-check`) or in a `run` tree, absent
  from the set: the replay goes on.
- **The log's role wins:** a call whose set line says one role and whose log line another, where only the log's role
  makes the new map refuse it: judged with the log's role (choose the planted guard and map so the difference shows).
- **The live log untouched:** the planted hook writes the `GOV_GUARD_CALLS_DIR` it was given (or its absence) to a
  file; the replay's hook runs never name the `guard_calls` folder, and no file in it changes.
- Map every case to **S15** (and to the ticket's failure line on gates that fail open where it fits); say for each
  what it expects and whether it is red today and why. Update the README: the interface above, the settings line
  (`guard_calls`, `replay_stale_h`), and a note N-11 for DEC-1108 (2). Keep it to about 12 to 16 new or changed cases.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-148-replay-tests`, branch `w2/W2-148-replay-tests`, made from
  `w2/integrate` at `75a29ff64` plus the CTO's ticket note `7438f7e91`. You write only `tests/acceptance/W2-148/`.
- **Your record:** your whole return is your session's **final message**, in full: the launcher keeps it in this
  worktree's `.gov-runtime/scratch/lead/log/`.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** it is in `governance/project/operator/` on
  `w2/integrate` and in your own worktree: **never open, grep or list that folder** (nor the engineer's worktree, base
  name `W2-148-replay`, nor `W2-148`, `W2-148-f21`, nor their branches), never `git show`/`git log -p`/`git diff` on it.
  Run its code only through your cases, and read only their results. The package names a function of it in words;
  that is all you need. You work from the ticket, the package, DEC-1108 and your own cases.
- **The exclusion line (DEC-1093 (2)), by base name:** every recursive grep carries `--exclude-dir=operator`, every
  Grep or Glob call that could reach it carries `!governance/project/operator/**`, find carries
  `-path '*/governance/project/operator' -prune`; keep searches inside your own worktree. If a search shows you a line
  of the implementation anyway, stop reading it and say so in your return.
- **Search again once (DEC-1092 (1));** two searches in all.
- **Planted folders only;** never the real `~/.gov-os/` (the live log), `~/gov-os-operator/`, `~/.claude/`, crontab,
  live hook, settings or git hooks; no real `claude`; no GPU, model, network or installs. **The hidden-half rule:**
  never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or
  `memory-verdict-2` folder.
- Run your cases through the heavy slot that `EMG-common.md` names, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-148-replay-tests/src` and a scratch HOME (link `.local/lib` to the user
  site so pytest is found), and run `python3 -m gov.cli.main accept W2-148 --root
  /home/usain/gov-os-worktrees/W2-148-replay-tests`: the code is present on this branch, so the earlier cases should
  pass (those you changed may go red for the right reason) and your new cases red where the check is missing.
- **DEC-1080:** Read and Grep tools; one simple command per Bash call; no `cd … &&` chains.
- **Commit** on `w2/W2-148-replay-tests`, only `tests/acceptance/W2-148/`, with
  `--trailer "Task: DAEO-xafn" --trailer "Implements: DEC-1108" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished; waits and stops by pid only.

## Return
The twelve labelled fields of `EMG-common.md` (sandbox check and `ps` check first), the new and changed cases (node
id, KPI line, what each expects, red or green today and why), the README's changed interface lines quoted in full,
the commit, `gov accept`'s counts, `TESTS-READY` text, and anything ambiguous as `discoveries`.
