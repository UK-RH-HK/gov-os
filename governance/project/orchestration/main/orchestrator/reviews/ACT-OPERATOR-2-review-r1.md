I found nothing that blocks: ACT-OPERATOR-2 is READY by `verdict.py`. Seven findings: five in scope, none of them both ordinary work and fail-open or work-losing; two fail-open residuals out of scope. Class is (O).

**Sandbox check (Step 0):**
- (a) The write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-xafn` failed with `Read-only file system`, as required.
- (b) `echo sandbox-trial | git hash-object -w --stdin` printed `1ae28402a109c3397a44b19239a00adfa9472eb0`, and `git update-index --refresh` exited 0. Both worked.
- A first try of (b) ran without the `echo` and wrote the empty blob `e69de29b…`, which every repository already holds.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.

**task:** the independent review of ACT-OPERATOR-2, one round. This was a fresh, read-only session (role `independent-auditor`, `GOV_TICKET=DAEO-xafn`), checking K1–K8.

**status:** DONE. Findings: 7, none blocking.
- In scope: F1, F3, F5 (ordinary work yes, consequence other) and F2, F4 (ordinary work no, other).
- Out of scope: F6, F7 (fail-open residuals in W2-148's merged design).

**work_completed:**
- **Read:**
  - the package, ACT-OPERATOR-1, OPERATOR-AGENT-1 §2–§6;
  - `apply.sh`, `rehearse.sh`, `op2_rehearsal.py`, `rehearsal.log` and the builder;
  - the merged `operator_run.py` and `opcommon.py`, the launcher, and the guard's call-log writer and rule 2d;
  - `path-map.yaml`'s `write_refused` block, `class-rules.yaml` and `verdict.py`.
- **Hashed:** every draft, the live-install copy, the tree's code, and the main tree's drafts and code (the files the operator will actually run). I also hashed the live install itself, read only.
- **Ran `apply.sh` against copies:** about 60 runs, on the default settings path (the live form), against copies of the live install with a planted HOME in my temp folder. Cases covered:
  - check, apply and undo, with a diff of the whole planted folder around apply and undo;
  - every hold, and every "other" state;
  - three tampered backups;
  - a planted failure partway through apply, and a planted swap that ends in a state other than "applied".
- **Ran the tests:** W2-148's acceptance tests and `tests/unit/operator`, through the heavy slot.

**files_changed:** none in any tree (`git status --porcelain` is empty). Outside the trees there were only the harness and the planted folders in my temp folder, now removed, plus Step 0's git object.

**evidence:**
- **Hashes:** all match the package.
  - `apply.sh` is `4132c2176604e33481ef78cef5d60305589f62002c41829cb504c1d53a7f1f38`.
  - `code/opcommon.py` is `e392d8a0e177…` and `code/operator_run.py` is `fe2e2f424616…`. Both equal the tree's files at HEAD (`966a9ac67`, which is `w2/integrate`) and at `a170641e`; nothing in `governance/project/operator/` has changed since.
  - The settings files are `a7d6dcbf40be…` before and `5a347f365136…` after; `APPROVED.after` is `b4a15c8f…`. The rehearsal files hash as stated.
  - The main tree's drafts, builder and code hash the same as my copies.
- **Live install (read only):**
  - All 15 files hash as the copy does, with `APPROVED` `157a9dc0…`, so the install is in the "before" state.
  - It already holds `install/__pycache__/opcommon.cpython-312.pyc` (47,438 bytes, written 18:57:02 by ACT-OPERATOR-1's own check, its `apply.sh:242`).
  - There is no `backup/` in the main tree's drafts.
- **Guard log:** the first line is `2026-11-09T18:16:17.623Z`, and `2026-11-09.jsonl` is the only day file.
- **Call-set folder:** `.gov-runtime/scratch/orchestrator/acts/replay/` does not exist yet.
- **Harness:** run 23:53:32–23:53:36Z, 0 unexpected results. Scratch was 20 MB and 3,831 inodes before removal.

**tests:**
- W2-148 acceptance: **182 passed, 1 deselected**. The deselected one is `test_w2_148_launch.py::test_s18_settings_that_did_not_load_fail_the_canary_and_no_real_session_starts`. The exclusion caught it only because its name contains "real"; it uses no model, and the rehearsal ran it (183).
- `tests/unit/operator`: **220 passed**.
- Both runs used `-m "not local_only" -k "not real and not green_here and not time_limit"`, `PYTHONPATH=<worktree>/src`, an empty scratch HOME and `PYTHONDONTWRITEBYTECODE=1`.

**discoveries:**
- Every apply rewrites the live `__pycache__` file (F1).
- The guard log starts at 18:16:17Z; 18:13Z is when the call-log ACT was applied (F3).
- The rehearsal's replay could not have turned a call (F6).
- `build_replay_calls.py` creates no parent folder, so `acts/replay/` has to be made before the first build.
- `check` exits 1 silently if `queue/` is missing (fails closed).

**risks:**
- F6 and F7 are fail-open residuals of the replay check. They are held only by the CTO's own rules.
- A failed apply needs a hand restore from `backup/` (F4).
- Any new call that Claude Code normalises can block every replay for 48 hours again (§8 item 2).

**lessons:**
- Running `apply.sh` with its override flags leaves the live path's own checks unexercised. Running the default path on a copy of the live install closes that gap cheaply.
- Diff the whole planted folder around apply, not only the expected files. That is how F1 showed up.

**proposed_decisions:** none is needed for READY. Proposed:
- (1) A §8 row for F6, with a CTO rule beside the 48-hour one.
- (2) Widen F7's follow-up beyond the window's start.
- (3) With the next re-install (§8 item 3 already plans one), add `-B` to the Python check in `apply.sh` and an `APPROVED` before-check in undo.
- (4) A line in §5 for what to do after a failed apply.

**unresolved:** I did not open the CTO's transcript, which was not copied to me. So the transcript form behind the Monitor mismatch (`"timeout": "600000"`) is the package's reading. The mechanism matches the code and the rehearsal output.

**recommended_next_action:**
- Hand §5 to the owner's operator as written. Expect `APPROVED` `b4a15c8f…`, plus a rewritten `install/__pycache__/opcommon.cpython-312.pyc`.
- Correct the wording in §0, §2, §3 and §6 (F3, F5). This is text only; `apply.sh` is unchanged.
- File the F6 and F7 rows, and create `acts/replay/` before the first build.
- Queue no path-map or deny-list ACT before about 2026-11-11 20:02Z (the package's 20:06Z is also safe). Queue no `sets_root_hidden` addition until F6 is answered.
- Process note: the Write tool's write of my harness into my temp folder was not granted (a permission prompt in this non-interactive session). Under DEC-1040 item 3, I wrote the same script with a quoted here-document in Bash to the same path. There were no other refusals.

## K1–K8

**K1, the touched set is exact: pass, with F1.**
- `apply` changes the four files to the stated hashes, each 0444:
  - `opcommon.py` → `e392d8a0…`
  - `operator_run.py` → `fe2e2f42…`
  - `operator-settings.json` → `5a347f36…`
  - `APPROVED` → `b4a15c8f…`
- It creates `backup/`, holding the four before-files plus `SHA256SUMS`, under the git-ignored `.gov-runtime/` (`.gitignore:18`).
- `state()` checks the other eleven files by hash, and refuses any extra file, before the swap and after it.
- `apply.sh` contains no git, crontab, guard, path-map or hook command.
- `log/launch.lock` is only opened. It is created only if missing; it exists live.
- One more write: the install's own check at `apply.sh:145` runs `python3 -I` without `-B`, so Python rewrites `install/__pycache__/opcommon.cpython-312.pyc` (F1).

**K2, the undo is real: pass, with F2.**
- `undo` restores all four files byte for byte. I compared each with `cmp` against the live copy: `APPROVED` is `157a9dc0…` again.
- It renames `backup/` to `backup.undone-<UTC>`, so a later apply makes a fresh backup.
- It refuses in each of these cases:
  - no `SHA256SUMS`;
  - a changed backup file;
  - backup settings that are not the before state;
  - a state other than "applied";
  - any hold.
- The gap is `backup/APPROVED`, which undo checks only against `backup/SHA256SUMS` (F2).
- The rehearsal log shows the restore (lines 28–33) but none of undo's refusals. My harness covered those.
- If `backup/` were ever lost, the old code is recoverable from git: the live files are exactly the blobs at `2a6462653`.

**K3, the rehearsal is real: pass, with F3.**
- It is a run of this `apply.sh`:
  - `rehearse.sh:65` copies the main tree's drafts into the clone, and the clone's copy is what runs.
  - `apply.sh`'s file time (23:19:30Z) is before the run started (23:29:26Z), and its hash today is the package's.
  - The log itself never prints `apply.sh`'s hash.
- The setup is as stated: a `--no-hardlinks` clone, a planted HOME, an `env -i` shell, ending `failures: 0`.
- Every count matches the package:
  - tests: 183 and 220 passed;
  - the apply sequence;
  - the idle launch;
  - the class-(a) ACT: 3 calls, 0 turned, 1 dropped;
  - the planted missing call: refused;
  - real data: 14,709 calls, 7,525 written, 112 dropped, 7,072 left out, 7,499 logged, 1 missing (17 reconciled);
  - live files unchanged (32 lines hashed).
- Where it differs from the live run:
  1. It passed `--settings-before`/`--settings-after`, with a planted `APPROVED` (`2dbf8e0b…` → `9b0d07d0…`). So the live-only checks and the default path's apply and undo never ran there. My harness ran them on a copy of the live install: `157a9dc0…` → `b4a15c8f…` → `157a9dc0…`.
  2. It removed `install/__pycache__` before starting, and never looked beyond the four files, so it could not show F1.
  3. Only two holds were rehearsed (a waiting request and the freeze), and only on `apply`.
  4. The call sets were planted, and its replay never turned a call (F6).
  5. The clone was at `6129d96cd40c`, not `92b725a98` (F3).
  6. The session used a `claude` wrapper rather than the cron's binary.

**K4, the refusals fail closed: pass, with F4.**
- `check` and `apply` in the before state each refuse, and change nothing, under:
  - the freeze;
  - the journal;
  - the operator lock;
  - a waiting `*.req` request.
- `undo` refuses under the same four holds and under a held `log/launch.lock`. `apply` refuses under a held `log/launch.lock` too.
- `check` takes no launch lock, which matches the package. In the applied state it reports "already applied" even under a hold; it writes nothing.
- These "other" states all refuse:
  - a changed file;
  - an extra file;
  - a missing file;
  - a link;
  - `wall/__pycache__`, which `apply.sh` calls "other" although the install's own check accepts it (fails closed);
  - an earlier `backup/`.
- The holds are checked before the lock is taken. That is harmless: a launch that starts in between holds the lock and is refused. A launch that lands mid-swap refuses once on "APPROVED mismatch" (`operator_launch.py:219`), as §8 item 4 says.
- A partial apply is visible ("other") and fails closed, since the install's own check refuses every launch. But undo **cannot** restore it (F4).

**K5, the class: (O).**
- OPERATOR-AGENT-1 §2 puts "the operator's own files" in (O), and §5 says changes to the operator's own install and `APPROVED` are "applied by your operator by hand".
- The code agrees: the rule table's first row, `operator-own` (`home: gov-os-operator/**`), gives (O). It is not "a path no rule names", as the package says (F3).
- The agent cannot apply its own install: that row makes its class gate refuse it as "yours".

**K6, the settings change is right: pass, with F5 and F6.**
- Only one key is added: `calls` = `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/acts/replay/calls.jsonl`.
- Rule 2d's `write_refused` covers only `~/gov-os-operator` except `queue/`, and `~/.gov-os/guard-calls` (`path-map.yaml:601-607`). No guard rule closes the main tree's scratch to the CTO, so the CTO can write this file.
- `guard_calls` keeps its default, `/home/usain/.gov-os/guard-calls`, which is the hook's own log folder (`pretooluse.py:99`).
- `replay_stale_h` (12 hours) is a new refusal, so it tightens.
- Nothing weakens a gate. Before this ACT, the installed replay re-judged only the agent's own dry-run commands.
- Trusted from the CTO's file beyond each call's hashed event:
  - which logged calls are re-judged and which are only counted as dropped;
  - the event's `cwd`, which is neither hashed nor in the log (F5, F6).

**K7, the claims about the replay check are true: pass, with F7.**
- **(a) True.** `read_guard_log` skips a day file that doesn't exist (`operator_run.py:1219`). `check_against_log` never compares the log's start with `since`. The builder leaves out calls with no log line (`build_replay_calls.py:239-241`). For the check this is a fail-open; for this ACT it is a residual, because the ACT only installs merged, reviewed code (F7).
- **(b) True.** The log's first line is 18:16:17Z; 18:13Z is when the call-log ACT was applied. The builder's window is exactly 48 hours back from its end. So a window fully inside the log ends at or after 2026-11-11 18:16:17Z (18:18Z if the 2-minute read margin must also fall inside the log). "About 18:16Z" is right.
- **(c) True in substance.** The Monitor call logged at 20:03:44.464Z blocks every real set (rehearsal log lines 109–111). The builder hashes the transcript's input, the guard hashed what Claude Code gave the hook, and the builder reconciles only string booleans. The check only requires calls between since + 2 min and until − 2 min (`operator_run.py:1248`). So the block lifts once the window's end passes 2026-11-11 **20:01:44Z**, about 4 minutes before the package's 20:06Z (F3; that time is conservative).

**K8, the code installed is the merged code: pass.**
- `code/*.py` are byte for byte the tree's files at HEAD and at `a170641e`, and the main tree's own copies.
- `APPROVED.after` lists exactly the 14 install files other than itself: the 11 unchanged ones plus the 3 new ones, in `sha256sum`'s C sort order.
- On the applied copy, `approved_state` is `True b4a15c8f`, and `APPROVED` matches `APPROVED.after` byte for byte.

## Findings

**F1 (K1): apply also rewrites `install/__pycache__/opcommon.cpython-312.pyc`.** The check at `apply.sh:145` uses `python3 -I` without `-B`. `undo` leaves the new file behind; it goes stale and Python ignores it, because the restored source's size differs. The live install already has this file from ACT-OPERATOR-1's identical check. The install's own check (S17), the control-file hash and `state()` all skip `__pycache__`. The package's list of touched files doesn't name it.
Ordinary work: yes, because every apply rewrites it (shown by my diff).
Consequence: other — no gate changes; the file is compiled from the approved source.
Scope: in.

**F2 (K2): undo checks `backup/APPROVED` only against `backup/SHA256SUMS`.** Apply writes both into the CTO-writable scratch. If both are changed together, undo swaps all four files and then stops with "after the undo the install is other", a state undo then refuses. My harness shows this: exit 1, then "other" on the next run. A check against the computed before-`APPROVED`, made before taking the lock, would refuse first.
Ordinary work: no, because it needs two matching hand edits in `backup/`, which only apply writes.
Consequence: other — the approved old code and settings are back; the operator is told; the digest shows the `APPROVED` hash.
Scope: in.

**F3 (K3, K5, K7): five wording errors in the package, none affecting a gate.**
- §6: the clone was at `6129d96cd40c`, not `92b725a98`.
- §6: the 7,072 left-out calls are the builder's "no log line" count. Not all are "before the log began": the Monitor call came after.
- §3: the log began with its first line at 18:16:17Z, not at 18:13Z.
- §3: the Monitor block lifts at about 20:02Z, not 20:06Z.
- Class line: the code's vote comes from the `operator-own` row, not "a path no rule names".

Ordinary work: yes, because the CTO and the owner act on the package's text.
Consequence: other — each error is neutral or conservative.
Scope: in.

**F4 (K4): a failed apply leaves a state that undo refuses, and apply's own message says to run undo.**
- I planted a failure at the second file. It exited through `set -e` with only the tool's own error, and left:
  - `opcommon.py` new and `operator_run.py` old;
  - a temporary file `.operator_run.py.act-operator-2.<pid>`;
  - the settings and `APPROVED` old.
- After that, `check` says "other … the CTO rebuilds", both `undo` and `apply` refuse, and the install's own check refuses every launch. The backup is intact and passes its `SHA256SUMS` check.
- When the swap completes but the result is not "applied", apply says `run 'bash apply.sh undo'` (`apply.sh:144`), and undo then refuses. §5 gives no step for a failed apply.

Ordinary work: no, because it needs a failure inside a swap of about 50 ms (a full disk, a kill, or a concurrent write).
Consequence: other — it fails closed until the CTO restores the four files by hand; no work is lost.
Scope: in.

**F5 (K6): §2 overstates what the agent checks in the CTO's file.** §2 says "Nothing is trusted from it but each call's event". In the code, two more things are taken from the file:
- (a) Which logged calls are re-judged and which are only counted as `dropped`. A dropped line's hash is accepted if any log line of the same session has it. The reason is never checked, and there is no limit on how many.
- (b) The event's `cwd`. It is neither in the hash (tool name and input only, `operator_run.py:1151-1154`) nor in the guard's log (`pretooluse.py:186-193`), yet it is passed to the hook (`:1346-1348`).

Ordinary work: yes, because the builder already writes dropped lines (112 in the real set) and every call's `cwd`.
Consequence: other — it misstates the trust boundary; the effect of (a) is F6.
Scope: in.

**F6 (K6): the replay re-judges no call that names the sets root.** The builder writes every such call as a dropped line, to keep sets-root paths out of the file, and the agent never re-judges dropped lines. For a path-map ACT that adds a glob to `sets_root_hidden`, those are exactly the calls the glob can turn. The rehearsal's own class-(a) ACT is this kind: its single dropped call was the only one its glob could reach, so "0 turned" was certain from the start. An over-broad glob would pass the after-check.
Ordinary work: yes, because an honest CTO can write a glob broader than intended, and the builder drops these calls by design.
Consequence: fails open — the after-check passes an ACT it exists to stop. The effect is over-refusal (agents are refused reads they need until the owner's undo line), not a loosening.
Scope: out — this comes from DEC-1108 (2)'s design, the builder's secrecy rule and W2-148's merged code. This ACT neither creates it nor can fix it. It needs a residual row and a CTO rule.

**F7 (K7 a): the check doesn't require the guard log to cover the window.** The package's proposed fix covers only the window's start. A gap inside the window passes the same way: a missing day file, or log lines lost to the guard's 2-second write deadline or to an error (which "never blocks the call"). A set with no logged live calls in its window passes with 0 calls re-judged.
Ordinary work: yes, because the guard's log writes can fail silently under load, and until the log holds 48 hours the CTO's own rule is the only hold.
Consequence: fails open — the replay passes a set that doesn't meet DEC-1108 (2)'s 48-hour premise.
Scope: out — a residual of W2-148's merged code. The ACT only installs it. Today it cannot be reached with the real set before about 2026-11-11 20:02Z, because the Monitor call refuses every set until then, which is later than the 48-hour point.

```verdict
{"act": "ACT-OPERATOR-2", "class": "O", "apply_sh_sha256": "4132c2176604e33481ef78cef5d60305589f62002c41829cb504c1d53a7f1f38", "kpis": [{"kpi": "K1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "K2", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "K3", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "K4", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "K5", "verdict": "pass", "findings": []}, {"kpi": "K6", "verdict": "pass", "findings": [{"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F6", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}, {"kpi": "K7", "verdict": "pass", "findings": [{"id": "F7", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}, {"kpi": "K8", "verdict": "pass", "findings": []}]}
```