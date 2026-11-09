# W2-148 — the engineer's brief, the replay round: DEC-1108 (2) (DAEO-xafn)

You are a fresh engineer for **W2-148** (`.tickets/DAEO-xafn.md`: read it, with its DEC-1106 note, the new **DEC-1108
(2) note** at its end and S15's line). The operator agent (`governance/project/operator/`) is merged into
`w2/integrate`. The owner's **DEC-1108 (2)** (in `docs/DECISION_REGISTER.md`; the reasoning in
`governance/project/orchestration/packages/ACT-GUARD-CALLLOG-1.md` §2, §3 (a) and §7 item 2): S15's replay must no
longer trust the `calls` file. **One pass, for that point only.**

## The point
`replay()` in `operator_run.py` (with the settings in `opcommon.py`) checks the CTO's call set against the guard's call
log **by sha256 both ways before it re-judges anything**, names the mismatches, and only then re-judges as today.

## The interface the test designer wrote (its README; you build to it, you never read the cases)
> `calls` (the CTO's call set for the replay, DEC-1108 (2)), `guard_calls` (the guard's call log, a folder; default `<home>/.gov-os/guard-calls`, DEC-1108 (2)), `replay_stale_h` (how old the set's `until` may be, hours; default 12, DEC-1108 (2)),

> **The replay (S15), checked against the guard's call log (DEC-1108 (2)):** the replay runs when an (a) ACT touches the path map or a deny list, as before; until a set is configured such an ACT is refused at its after-check.
> - **The call set** (the `calls` setting's file), JSON lines, the events' paths relative to the repository:
>   - line 1, the header: `{"v": 1, "window": {"since": ISO, "until": ISO}, ...}` (other keys ignored);
>   - a call: `{"id", "time", "session", "role", "ticket", "agent", "sha256", "event": {"tool_name", "tool_input", "cwd"}}` (the line's own `sha256` is ignored: the agent recomputes it from the event);
>   - a dropped call: `{"id", "time", "session", "sha256", "dropped": "<reason>"}`, no `event` (a call the CTO's tool may not copy, such as one naming the sets root): checked against the log, never re-judged.
> - **The guard's log:** setting `guard_calls` (a folder; default `<home>/.gov-os/guard-calls`). One file per UTC day, `<YYYY-MM-DD>.jsonl`; each line `{"v": 1, "time": ISO ms "Z", "session", "role", "agent", "ticket", "tool", "decision", "rule", "tree", "ms", "sha256", "keyed"}`; a marker file `<day>.jsonl.capped` means that day was cut short.
> - **The hash:** `sha256(json.dumps({"tool": tool_name, "input": tool_input}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))`, hex.
> - **Before anything is re-judged** (no run of the guard hook before), the replay refuses (so the after-check undoes the ACT and pushes a P1, as any replay refusal does) unless all hold:
>   1. **The window:** the first line is the header; `until` is no later than the clock plus 5 minutes and no older than the clock minus `replay_stale_h` hours; `until - since` is at least 48 hours.
>   2. **Well formed:** every other line is a call (an `event` object) or a dropped call (a 64-hex `sha256` and a non-empty `dropped`); anything else is malformed (fail closed).
>   3. **The log readable and whole:** the folder exists; no day file from `since - 2 min` to `until + 2 min` has a `.capped` marker; no line in those files is malformed.
>   4. **Set to log:** every set line whose `time` lies in `[since, until]` has a log line with the **same session** and the same sha256 (a call's recomputed from its event; a dropped call's from its line), the log line's time within `[since - 2 min, until + 2 min]`.
>   5. **Log to set:** every log line whose time lies in `[since + 2 min, until - 2 min]`, whose `session` is a UUID (lower-case 8-4-4-4-12 hex) and whose `tree` is `main` or `worktree`, has a set line (call or dropped) with the same session and sha256; a null `sha256` counts as missing. Other sessions (the suites' fixed names) and trees (`run`, `scratch`, `other`) are not required.
>   - **The refusal's reason** (the result line's `reason` or a P1's `text`) names the mismatches (at most 5 of each kind): a set call by its `id`, a logged call by its session's first 8 characters, its sha256's first 12 and its time as the log line writes it (at least to the minute); never an input's text. The check's other refusals carry a fixed phrase: `no header`; `window short`; `window stale` (an `until` older than the clock minus `replay_stale_h`); `log capped` and `log malformed`, each with the day `YYYY-MM-DD`; `log missing`. A refusal by the re-judging carries none of these phrases and not the word `malformed`.
> - **Then the re-judging, as today,** over the set's calls (not the dropped ones) in the window, each with the **role and ticket of its matching log line** (they win over the set's), given to the hook as `GOV_ROLE` and `GOV_TICKET` (as the live guard reads them); the dropped calls are counted by reason. The replay's own runs of the hook never write the live log: each is run with `GOV_GUARD_CALLS_DIR` set to an absolute folder inside the replay's own temporary folder, never in `guard_calls` or `<home>/.gov-os/guard-calls`; no file in `guard_calls` changes.
> - The planted guard `.claude/hooks/pretooluse.py` reads `<CLAUDE_PROJECT_DIR or cwd>/governance/project/path-map.yaml` and the event on stdin and denies a Read under a `sets_root_hidden` glob. Calls outside the header's window are neither checked nor re-judged. The DEC-1108 cases commit a variant of it before the ACT is built (`plant_guard`): `record` appends `{dir: GOV_GUARD_CALLS_DIR, role: GOV_ROLE, path}` per run to a file of the world; `role_aware` denies only when `GOV_ROLE` is in the path map's `sets_root_hidden.refused_roles`.

## Notes
- **The hash** must be exactly the guard's: `json.dumps({"tool": tool_name, "input": tool_input}, sort_keys=True,
  separators=(",", ":"), ensure_ascii=False).encode("utf-8")` (the live hook's `action_bytes`,
  `.claude/hooks/pretooluse.py`; read it, do not import it: the install runs without the repository's hook beside it).
- **The trial (S23)** replays ACT-GUARD-SETS-1, a path-map change: its replay must now find a set and a log. Plant both
  in the trial's own temporary folders (`tests/unit/operator/test_w2_148_trial.py`), agreeing both ways, so the
  trial's outcomes are unchanged; say so in the evidence record.
- Your unit tests (`tests/unit/operator/test_w2_148_replay.py`): each rule of the interface refusing on its own, the
  re-judging with the log's role, and the live log untouched.
- Size: about 60 to 100 lines in `operator_run.py`/`opcommon.py`; keep the existing replay's structure.

## Where you work
- `/home/usain/gov-os-worktrees/W2-148-replay`, branch `w2/W2-148-replay` (from `w2/integrate` at `75a29ff64`, the
  CTO's ticket note and the designer's cases merged at ``235d5d45d` (cases `841c64944`)`). Your paths are the ticket's `allowed_paths`:
  `governance/project/operator/**`, `tests/unit/operator/test_w2_148*`, `docs/changes/W2-148-evidence.md`.
- **Do not touch** `governance/project/operator/brief.md` (another session is rebuilding ACT-OPERATOR-1's hashes).
- **You never read `tests/acceptance/W2-148/`** (G-14; DEC-820 (c)): only `gov accept`'s results. **The exclusion
  line (DEC-1093 (2)), by base name:** every recursive grep carries `--exclude-dir=W2-148`; every Grep or Glob call that
  could reach the folder carries `!tests/acceptance/W2-148/**`; find carries `-path '*/W2-148' -prune`. Start searches
  from relative paths inside your worktree. If a search shows you a line of the cases anyway, stop and say so.

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
  with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-148-replay/src` and a scratch HOME (link `.local/lib` to the user
  site): your unit tests (all of `tests/unit/operator/`); then
  `python3 -m gov.cli.main accept W2-148 --root /home/usain/gov-os-worktrees/W2-148-replay` (all must be green; the
  designer's run had 167 passed, 16 red: the 14 new cases in `test_w2_148_replay_check.py` and the 2 changed S15 cases). Add a short "Replay check (DEC-1108 (2))" section to
  `docs/changes/W2-148-evidence.md`. Commit as you go.

## Rules
- **Nothing live:** never read or write the real `~/.gov-os/` (the live log), `~/gov-os-operator/`, `~/.claude/`, the
  crontab, the live hook's runs, settings or git hooks; no real `claude` session, no real notice.
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No GPU, model, network, installs or service.
- DEC-1080: Read and Grep tools; one simple command per Bash call; no `cd … &&` chains. Waits and stops by pid or
  pgid only. Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-148-replay` with
  `--trailer "Task: DAEO-xafn" --trailer "Implements: DEC-1108" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it; it is the record): the twelve
labelled fields of `EMG-common.md` (sandbox and `ps` checks first), the change (commits, unit cases), `gov accept
W2-148`'s counts per line, the unit counts, every red named.
