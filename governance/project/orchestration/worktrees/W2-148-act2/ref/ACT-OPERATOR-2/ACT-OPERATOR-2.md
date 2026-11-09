# ACT-OPERATOR-2: the operator agent re-installed to carry the replay check, and its call set named (DEC-1108 (2), DEC-1104 (2))

- **For:** the owner's operator, by hand, as the message in §5 (DEC-1104 (4)). About one minute in a plain terminal or
  the operator's console. Nothing in the repository changes; nothing is committed.
- **By:** a helper agent for the CTO (orchestrator `DAEO-sdxk`, session `ad44f5fe`), 2026-11-09. Built and rehearsed in
  a clone with a planted HOME. **Nothing live is changed** until the operator runs §5. Reviewed independently (§7).
- **Under:** DEC-1108 (2) (the CTO's tool builds the 48-hour call set; the operator agent checks it against the guard's
  call log by sha256 both ways before re-judging; built tests first before the first path-map ACT goes through the
  agent); DEC-1104 (2) (OPERATOR-AGENT-1: the operator's own install is the owner's, applied by hand, §5); DEC-1106 (3)
  and DEC-1108 (5) (rule 2d: no session writes into `~/gov-os-operator` but `queue/`); DEC-1057 (rehearsed); DEC-1112 (3)
  (delegated to the CTO).
- **Sources:** W2-148's replay check, merged `a170641e` (`governance/project/operator/operator_run.py` `replay()`,
  `read_call_set`, `read_guard_log`, `check_against_log`; `opcommon.py`'s `calls`, `guard_calls`, `replay_stale_h`;
  `docs/changes/W2-148-evidence.md` "Replay check"); ACT-OPERATOR-1 (the install as applied, `2a6462653`; its §7 item 3:
  "that build puts its corpus where the operator reads it and sets `calls` in the install's settings (a change to the
  install: yours)"); the CTO's builder `.gov-runtime/scratch/orchestrator/tools/build_replay_calls.py`.
- **Class: (O).** The operator's own install (OPERATOR-AGENT-1 §5: "the operator's own install … changes to them reach
  you as a package and are applied by your operator by hand"); the code's vote is the same (a path no rule names, under
  `~/gov-os-operator/install`). The operator agent cannot apply it: rule 2d and `APPROVED` keep its own install out of
  its reach. No queue request, no yes line: the owner's go is handing §5 to the operator.
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/operator-2/` (§4).

## 1. What lands
Three files in `~/gov-os-operator/install/`, then its `APPROVED`. Nothing else on the machine, nothing in the repository.

| File (in `install/`) | Before → after (first 12) | Why |
|---|---|---|
| `operator_run.py` | `41271992b637` → `fe2e2f424616` | the replay check (W2-148 S15 with DEC-1108 (2), merged `a170641e`): before any guard hook re-judges a call, the CTO's call set is checked against the guard's call log both ways by sha256; any mismatch refuses, undoes the ACT's own files and pushes a P1. The agent's own dry-run record moves to `log/operator-calls.jsonl` |
| `opcommon.py` | `1c6946921290` → `e392d8a0e177` | the three settings the check reads: `calls`, `guard_calls` (default `~/.gov-os/guard-calls`), `replay_stale_h` (default 12) |
| `operator-settings.json` | `a7d6dcbf40be` → `5a347f365136` | one key added: `"calls": "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/acts/replay/calls.jsonl"` (§2) |
| `APPROVED` | `157a9dc01fca` → `b4a15c8f3b7c` | sha256sum's form over every install file but itself, as ACT-OPERATOR-1 built it; the three new lines |

- **`APPROVED`'s sha256, live after:** `b4a15c8f3b7c769259f25b8d71406e6c7d387d30c021343f26f4bad6e3831fa4` (every result
  and the digest print it; the digest's expected value changes from `157a9dc0…` to this).
- **Unchanged and checked by hash:** the other eleven install files (`act_class.py`, both briefs as you approved them,
  `brief.md` `51c459cf…` and `reviewer-brief.md` `e8670330…`, `class-rules.yaml`, `freeze_gate.py`, `landing_check.py`,
  `operator_launch.py`, `verdict.py`, the wall's hook and settings template, `win_toast.ps1`). The git hook, the guard,
  the path map, the crontab line and the landing tool are untouched.

## 2. Why the call set lives in the CTO's scratch
The merged default for `calls` is `<operator root>/log/calls.jsonl`. Rule 2d refuses every session's writes there
(only `queue/` is open), so the CTO's builder could never write it, and every path-map or deny-list (a) ACT would be
refused at its after-check for good. The setting therefore names a file the CTO can write:
`.gov-runtime/scratch/orchestrator/acts/replay/calls.jsonl` in the main tree (mode 0600, written by
`build_replay_calls.py --out <that file>`). Nothing is trusted from it but each call's event: the agent recomputes every
hash and checks every line against the guard's own log, which rule 2d closes to every session. A file the CTO edits by
hand fails the check (a call with no log line, or a logged call missing).

## 3. When the first path-map ACT can go through the agent
- **The 48 hours (the CTO's rule, DEC-1108 (2)):** the guard's call log began at ACT-GUARD-CALLLOG-1's apply, 2026-11-09
  18:13Z, so the first window of 48 hours of log history ends about **2026-11-11 18:16Z**. Until then, no path-map or
  deny-list ACT is queued to the agent; opt-in and test-map (a) ACTs (no replay) can go as before.
- **Found in the rehearsal, the CTO's to enforce until fixed:** the check does not require the log to cover the window's
  start. `read_guard_log` skips a day file that does not exist, and the CTO's builder leaves out calls the log does not
  hold. So a 48-hour set built today passes steps 1 to 4 with only about 5 hours of real log behind it: the rehearsal's
  real set (§6) covered 7,499 logged calls and left out 7,072 calls from before the log began, and the check refused it
  only for the reason below. Until a fix (a follow-up row: refuse when the log's first line is later than the window's
  start plus the slack), the 48-hour rule is kept by the CTO, not by code.
- **And one logged call the builder cannot place:** a `Monitor` call of 2026-11-09 20:03:44Z (session `ad44f5fe`), whose
  input in the transcript carries `"timeout": "600000"` (a string, under a key the tool names `timeout_ms`), hashes
  differently from what the guard logged. The check refuses the whole set ("1 logged live call(s) missing from the set")
  until that call leaves the window, at about **2026-11-11 20:06Z**, unless the builder learns to write such a call as a
  dropped line with the log's own sha256 (the CTO's tool; a follow-up). So **the first path-map ACT through the agent:
  after 2026-11-11 20:06Z**, or after 18:16Z once the builder fix lands. It fails closed either way (a refused after-check
  undoes the ACT and pushes a P1).

## 4. The files (drafts; checked by hash before they apply)
| File (`drafts/operator-2/`) | sha256 (first 12) |
|---|---|
| `code/operator_run.py`, `code/opcommon.py`: byte for byte the tree's at `a170641e` and today's head | `fe2e2f424616`, `e392d8a0e177` |
| `operator-settings.before.json` (the live install's), `operator-settings.after.json` | `a7d6dcbf40be`, `5a347f365136` |
| `APPROVED.after` (for reading; `apply.sh` computes the same bytes) | `b4a15c8f3b7c` |
| `apply.sh`: `check`, `apply`, `undo` | `4132c2176604` |
| `op2_rehearsal.py`, `rehearse.sh` (the rehearsal's own), `rehearsal.log` | `9b88b7dc7cf7`, `f5870f6e994f`, `603f7aca2ae8` |

`apply.sh check` and `apply` stop unless:
- the draft code and the tree's `governance/project/operator/opcommon.py` and `operator_run.py` hash as merged;
- the install is exactly as ACT-OPERATOR-1 left it (all fourteen files and `APPROVED` `157a9dc0…`), or exactly as this
  ACT leaves it ("already applied"); anything else stops with "the CTO rebuilds";
- the operator holds nothing: no freeze (`install/act-in-progress.txt`), no journal (`log/journal.json`), no lock of a
  failed undo (`log/operator.lock`), no request waiting in `queue/`, and (apply and undo) no launch running
  (`log/launch.lock` taken for the swap, so the cron's launcher waits).

`apply` backs up the four files with their sha256s (`drafts/operator-2/backup/`), writes each new file beside its old
one and renames it over (0444), `APPROVED` last, then runs the install's own `APPROVED` check. `undo` checks the backup
and puts the four files back byte for byte, `APPROVED` last. **Checked on the live install, 2026-11-09 23:2x UTC:
"install: before (APPROVED 157a9dc01fca)", "check: ready to apply".** If the install or the merged code moves before you
apply, the CTO rebuilds and re-rehearses.

## 5. The operator's steps: the message
> **ACT-OPERATOR-2 (DEC-1108 (2), DEC-1104 (2)): re-install the operator agent with the replay check.** Your
> operator's own install, by hand; nothing in the repository changes and nothing is committed. About one minute. Best
> not at a :x0 minute (the cron's launch).
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> G=.gov-runtime/scratch/orchestrator/drafts/operator-2
> bash $G/apply.sh check     # "install: before (APPROVED 157a9dc01fca)", then "check: ready to apply" (exit 0)
> bash $G/apply.sh apply     # backup; the two code files and the settings; APPROVED last; "the install's own APPROVED check: ok"; "state applied"
> sha256sum ~/gov-os-operator/install/APPROVED    # expect b4a15c8f3b7c769259f25b8d71406e6c7d387d30c021343f26f4bad6e3831fa4
> ```
> If `check` stops, send its line to the CTO and apply nothing.
> **Undo:** `bash $G/apply.sh undo` puts the four files back byte for byte (`APPROVED` `157a9dc0…` again); it refuses
> while the operator holds a run or a request waits.

**Then the CTO**, the same day: record the apply (the "Applied" line here, from the operator's words and
`sha256sum`); expect `b4a15c8f…` in the next result line and digest; queue no path-map or deny-list ACT before the time
in §3; file the follow-ups in §8.

## 6. The rehearsal (DEC-1057): `rehearsal.log`
One clean run (run 3), 2026-11-09 23:29–23:32 UTC, from a fresh `env -i` shell, **failures: 0**, in a `--no-hardlinks`
clone of the main tree at `92b725a98` with a planted HOME: the live install copied in (read only), its settings the
rehearsal's (the clone, the planted HOME, the real `claude` with the real HOME for its sign-in only) and its `APPROVED`
rebuilt for them; the owner's operator files planted; the planted guard log and call set in the planted HOME. Runs 1 and
2 (same day) stopped on the rehearsal script's own faults (a planted `APPROVED` that listed its own temporary file; an
expectation reading the launcher's line instead of the log), not on the ACT; both fixed.

| Step | Result |
|---|---|
| The code the install carries, on the clone | W2-148 acceptance **183 passed**; `tests/unit/operator` **220 passed** |
| `apply.sh` | check "ready to apply"; apply: the install's own `APPROVED` check ok, "state applied"; a second apply refused; check "already applied"; undo: every file back, `APPROVED` as before, "ready to apply" again; a waiting request: refused; the freeze held: refused; apply again |
| The launcher as the cron runs it (`python3 -I`, `env -i`), nothing queued | `"result": "idle"`, the re-installed `APPROVED` accepted |
| **A class-(a) path-map ACT through every gate** (one refusal glob added to `sets_root_hidden`; the planted 48.5-hour set of 3 calls and 1 dropped call, each logged once) | the canary, then the real walled session (19 s); G1–G9 pass, votes a/a/a; applied and committed (`Role: operator`, `Act:`, `Act-sha:`, `Class: a`, `Review:`); **after-check: the both-way check passed, 3 calls re-judged, 0 turned, 1 dropped counted**; the owner's `undo` line: undone |
| **The same kind of ACT with one logged live call the set does not hold** | G1–G9 pass; **after-check refused: "the call set does not match the guard's call log by sha256 (DEC-1108 (2)): 1 logged live call(s) missing from the set"**; the ACT undone byte for byte; a P1 notice; the map as before |
| **The real data, read only:** the CTO's builder over the real transcripts (48 hours to 23:32Z) against the real guard log, by the re-installed `check_against_log` | 14,709 calls in the window: 7,525 written, 112 dropped (they name the sets root), 7,072 left out (before the log began); 7,499 logged replayable calls, 7,498 in the set; **refused: 1 logged live call missing** (the `Monitor` call of §3) |
| The owner's planted files; live files (the install, the operator folder but `log/`, the hook, the map, the settings, the operator code, `~/.claude/settings.json`, the crontab) | unchanged; **unchanged** (hashed before and after) |

Where the real run differs: the live install's settings name the main tree and `/home/usain`, not the clone and the
planted HOME; the launcher at your apply is the cron's; the real `calls` file does not exist until the CTO's builder
writes it (an (a) path-map ACT before then is refused at the after-check: "no header" or a missing file, fail closed).

## 7. The review
`.gov-runtime/scratch/orchestrator/reviews/ACT-OPERATOR-2-review-r1.md`: @REVIEW@

## 8. Residuals, and what follows
1. **The window's start is not enforced in code** (§3): a follow-up row for `read_guard_log` (W2-148's code; a ticket,
   tests first, then a further re-install ACT). Until then the CTO queues no path-map or deny-list ACT before the log
   holds 48 hours.
2. **The builder and calls Claude Code normalises** (§3): `build_replay_calls.py` reconciles string booleans only; a
   logged call whose transcript input differs otherwise (a string number, an unknown key) blocks every replay for 48
   hours. Follow-up (the CTO's tool, no ACT): write such a call as a dropped line carrying the log's own sha256, named
   and counted.
3. **The operator's wall loads the user's settings too** (as W2-149's F11 found for the walls): `operator_launch.py`
   starts `claude -p --restricted --settings …` with no `--setting-sources`. Its wall's deny list and hook refuse what
   an allow line would open, as for the walls. Follow-up row: the same `--setting-sources project`, in W2-148's code,
   with the next re-install.
4. **A launch at the swap's instant:** the launcher checks `APPROVED` before it takes its lock; a cron launch in the
   millisecond between the code files and `APPROVED` would refuse "APPROVED mismatch" once (logged, no apply) and the
   next one at +10 minutes runs. Hence "not at a :x0 minute".
5. **Threat model (unchanged):** ADR-0001's honest mistakes; a hand-forged call set or log is a Wave 3 row
   (OPERATOR-AGENT-1 §6).

**What it costs:** nothing measurable per run (the check reads one day file per day of the window, about 7,500 lines
today); the owner's minute. No install, no GPU.

**Basis:** question 2 (an operator that cannot be shown a curated replay: every path-map ACT's replay is the guard's own
record of the calls).
