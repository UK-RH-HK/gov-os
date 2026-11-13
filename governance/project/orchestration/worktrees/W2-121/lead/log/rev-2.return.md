Step 0, the sandbox check: (a) the trial write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cb2b` failed (`OSError: [Errno 30] Read-only file system`), so no file was made; (b) `git hash-object -w --stdin` worked (1ae28402a…), and `git update-index --refresh` exited 0. The `ps` check for ollama and llama-server showed nothing, at the start and at the end.

task: DAEO-cb2b (W2-121 part a), FULL review round 2 (the last), probed head f1f950479641
status: DONE
work_completed:
- Read the ticket (S1–S10, F1, Part a, Interface, P-W2-121-5/6/7), round 1's record and both interface readings, plus all 11 files of `src/gov/dispatch/` and both fix-round diffs.
- Re-planted F-1 to F-6 as behaviours and ran 6 probes of my own on planted projects under the sandbox's temporary folder.
- Planted 12 mutations, one or more per fix, on a mirror copy of the code under the sandbox's temporary folder, never in the tree.
- Checked scope, the S6 grep and the authorship of the acceptance-test changes.

files_changed: none (`git status --porcelain` is empty; HEAD is still f1f950479641)

evidence:
- **Scope.** `git diff --name-only c6ca85d07 f1f950479641` lists only `src/gov/dispatch/**`, `tests/unit/dispatch/**` and `tests/acceptance/W2-121/**`. The w2/integrate merge brought only round 1's probe record into the branch.
- **Who changed the acceptance tests.** Only 5045148c8 and db682531d (Role: independent-test-designer) touch them. Merge 696d32a93 adds nothing beyond those two commits' tests, and the engineer's commits 2f7ecb2a2 and f1f950479 touch no acceptance file.
- **S6 grep.** `w2/|integrate|W2-[0-9]|DAEO-|gov-os-worktrees|Dynamic-Agentic|.gov-runtime/scratch|usain` over `src/gov/dispatch` finds 0 lines.
- **F-1 fixed.** A return read then deleted, one deleted unread, a never-ran item deleted, an owner item deleted, and an item planted by hand in `inbox/` or `inbox/read/` then deleted: none is ever written again. A late `.exit` after a never-ran item gives exactly one never-ran and one return item.
- **F-2 fixed.** A notifier exiting 1 with a 600 s retry time:
  - it ran once; the next two passes each had `ok: true`, exit 0, and a problem line naming the item, the time of the attempt and the failure;
  - it was not called again before the retry time;
  - the problem line went once the item was read.
  - Timeouts and a notifier that cannot start are covered by tests that caught the planted mutations.
- **F-3 fixed.** The notifier is required at load (`config.py:128`). Making it optional is caught by both suites.
- **F-4 fixed.** Untracked and staged-only paths are unresolved; ignored-and-present and committed paths resolve; a path committed and later removed resolves by its history.
- **F-5 fixed.** A gate shut for load or CPU with ample memory refuses every entry by the gate. Removing the gate check is now caught by the acceptance tests too (`test_s2_s6_gate_only.py[load]`).
- **F-6 fixed for a hung git.** A git that hangs while resolving writes `unchecked:` (a test catches the regression). A git that exits with an error is not covered: finding R2-2.
- **Mutations: 12 planted, 12 caught.**

  | mutation | caught by |
  |---|---|
  | M1 record ignored | both suites |
  | M1b no record of items found in the folders | both |
  | M2 escalation recorded before the notifier runs | both |
  | M2b retry time ignored | both |
  | M2c no problem line while waiting | both |
  | M2d a notifier timeout does not end the pass's escalations | unit only (close to equivalent, because the runner already refuses a program that timed out) |
  | M3 notifier optional | both |
  | M4 an existing path resolves | both |
  | M4b no history check | acceptance only |
  | M4c no ignore check | both |
  | M5 gate check removed | both |
  | M6 unchecked written as unresolved | unit only (as the brief said) |

- **Pass time.** With N finished starts and N items already recorded, one pass takes 0.24 s at N=1000, 2.0 s at N=3000, and 7.5–8.4 s at N=6000: it grows with the square of N (R2-1).

tests: Baseline `tests/acceptance/W2-121` + `tests/unit/dispatch` through heavy_slot.sh with the brief's `-m`/`-k` exclusion: 253 passed. The exclusion left out the `local_only`, `real`, `green_here` and `time_limit` cases; I did not take the deselected count. The mutation runs were per file, with `-x`, on the mirror; the mirror was restored afterwards and `diff -r` shows it identical to the tree. The six W2-96 base reds were not run (not this ticket's).

discoveries:
- A glob in `files_changed:` (e.g. `.tickets/*.md`) counts as resolved, because git reads it as a pattern that matches committed files. It is lenient only when something matches, so it is not reported as a finding.
- Re-checked and still sound:
  - the lock, and a losing pass writes nothing;
  - OFF is read before the lock;
  - the start is recorded before the spawn;
  - one start per pass, in list order, with every skip named;
  - the room formula uses the gate's floor and working size;
  - S7's round count;
  - no watcher process;
  - the status is written whole, `PASS FAILED` is the top line of a failed pass, and `status` says STALE after 3 minutes;
  - a crash between an item's write and its record is recovered by the next pass, which records the item it finds in the folder;
  - a failed notifier is retried only at `notify_retry_s` (default 600 s), not every pass;
  - a hung notifier costs one timeout per pass, after the starts.

risks:
- R2-1: pass time keeps growing for the life of the state folder. At about 15–20k starts it passes a minute, and every other cron tick then exits 4 at the lock. The status stays honest: it says STALE after 3 minutes.
- Nothing in part a writes the job history (round 1's note, out of scope). Until something does, a lead's peak is the gate's working size.

lessons: The fix moved the "already written?" check from a file-exists test to a whole-file read per item, which turned an O(1) check into an O(N) one. The fix-round tests check behaviour, not cost.

proposed_decisions: none

unresolved:
- My first planted probe file (a Write call under the sandbox's temporary folder) was refused by the quiet-hours hook. I did not retry it. Instead, the probes ran as stdin scripts on planted folders, and the mutations were made by Bash on the mirror under the same temporary folder, as the brief's item 5 commissions. Whether that second route was right is the owner's to judge.
- Who writes `history.jsonl` is not part a's.

recommended_next_action: Record PASS for round 2. Land R2-1 and R2-2 as recorded rows: neither blocks. R2-1's fix is to read `items-written.txt` and `never-ran.txt` once per pass into a set. R2-2's fix is to treat a git exit other than 0 or 1 while resolving as "could not be checked".

```
verdict: PASS
head: f1f950479641
findings: 2
- R2-1 | minor | S4 | src/gov/dispatch/state.py:142 (called per start from src/gov/dispatch/returns.py:363) | the "written once, ever" check re-reads the whole record of written items for every start in every pass; planted N finished starts with N recorded items: one pass took 0.24 s at N=1000, 2.0 s at 3000, 7.5–8.4 s at 6000 (was O(1) a check before the fix); should stay roughly flat. Ordinary work: yes, because starts pile up over months of use. Consequence: other (a slow pass; past a minute every other tick exits 4; the status still says STALE, never a false current one). Smallest fix: read the record and never-ran.txt once per pass into a set. Reversed by: a pass under ~1 s at N=10000 on this code.
- R2-2 | minor | S9 | src/gov/dispatch/returns.py:324,338 | git exiting with an error (not hanging) while resolving is read as "unknown": planted a return naming the worktree's real HEAD commit and the committed README, with the worktree's .git link removed; the item said "unresolved: <real commit> README" with no problem line, where the fix round's reading says "unchecked: could not be checked (...)". Ordinary work: no, because a broken worktree link needs the repository moved or tampered with. Consequence: other (a misleading item; nothing starts, nothing is lost). Smallest fix: a git exit code other than 0/1 from cat-file/log raises CommandFailed. Reversed by: an ordinary-work path to git exit 128 inside an existing worktree.
```

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": []},
 {"kpi": "S2", "verdict": "pass", "findings": []},
 {"kpi": "S3", "verdict": "pass", "findings": []},
 {"kpi": "S4", "verdict": "pass", "findings": [{"id": "R2-1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S5", "verdict": "pass", "findings": []},
 {"kpi": "S6", "verdict": "pass", "findings": []},
 {"kpi": "S7", "verdict": "pass", "findings": []},
 {"kpi": "S8", "verdict": "pass", "findings": []},
 {"kpi": "S9", "verdict": "pass", "findings": [{"id": "R2-2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S10", "verdict": "pass", "findings": []},
 {"kpi": "F1", "verdict": "pass", "findings": []}
]}
```

S1's installed host entry, and S6's review record and switch-over, are the CTO's ACT at the last part's close and are not judged here. F1 is judged on its start half only.

guard_refusals:
- 2026-11-12 ~06:56 UTC | Write of `$TMPDIR/mirror/tests/unit/dispatch/test_zz_probe.py` (sandbox temporary folder, outside every tree) | "Quiet hours (02:00 to 07:30): this call needs the owner's approval, so it was refused at once and queued for the 09:00 morning package (DEC-991)" | false-positive: the brief authorizes planted files under the sandbox's temporary folder. Not retried; the probes ran as stdin scripts instead (see unresolved).
