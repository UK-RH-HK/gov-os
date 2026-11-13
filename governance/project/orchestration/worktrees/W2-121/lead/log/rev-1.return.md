Sandbox check (step 0): passed.
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cb2b` was refused (`OSError: [Errno 30] Read-only file system`), and no file exists.
- (b) `git hash-object -w --stdin` worked (it wrote `1ae28402a109…`), and `git update-index --refresh` exited 0.
- ps check: no ollama or llama-server process, before or after the runs. `GOV_TICKET=DAEO-cb2b`.

task: DAEO-cb2b (W2-121 part a), independent FULL review, round 1; decisions: DEC-1007, DEC-1010, DEC-1014, DEC-801, DEC-808, DEC-1073
status: DONE
work_completed: Checked the head: `git rev-parse HEAD` = 1ec89f0efdbb. Read the ticket (S1–S10, F1, Part a, Interface, P-W2-121-5), all 11 files in src/gov/dispatch/, the lead's interface-1.md, the acceptance and unit tests, the gate, config and machine code, `build_lead_settings`, the reference README, and DEC-1007/1010/1014/801. Ran the ticket's tests once as a baseline. Ran four planted scenarios and 21 planted mutations on copies under the sandbox TMPDIR, never in the tree.
files_changed: none (`git status --porcelain` is empty at the end)
evidence:
- **Baseline:** `tests/acceptance/W2-121 tests/unit/dispatch` with the brief's form: 189 passed in 76 s.
- **Scope:** `git diff --name-only 2a35ec307 1ec89f0efdbb` lists only src/gov/dispatch/**, tests/unit/dispatch/** and tests/acceptance/W2-121/**. `.tickets/DAEO-ozyt.md` is not in it. `git diff 0384e71db 1ec89f0ef -- tests/acceptance/W2-121` is empty, so the acceptance tests are the designer's own.
- **S6 grep:** `w2/|integrate|W2-|DAEO-|Dynamic-Agentic|gov-os-worktrees|EXAMIN` over src/gov/dispatch/ finds 0 lines.
- **Planted P1:** no `notifier_command` and an item unread past the time. Every pass exits 2 with the top line `PASS FAILED … configuration: notifier_command …`. Yet pass 1 started W2-1 and pass 2 started W2-2, and the status shows neither start nor any running session.
- **Planted P2:** a finished return is read (moved to inbox/read/), then deleted. The next pass writes `W2-1-A5-run.json.return.txt` into inbox/ again as unread.
- **Planted P3:** the notifier exits 1 once. That pass records the escalation and one problems line. After the notifier is fixed, the next pass has 0 escalations and 0 notifier calls, and the problems list is empty.
- **Planted P4:** `files_changed: src/new_uncommitted.py, src/never.py`, where the first file exists only uncommitted in the worktree. The item shows `unresolved: src/never.py` only.
- **Mutations the tests caught:**
  - lock removed (2 fail)
  - worktree-HEAD claim check removed (1)
  - unread check removed (1)
  - running check removed (2)
  - list read in reverse (5)
  - room check removed (8)
  - held memory ignored in the peaks ahead (4)
  - peaks never refreshed (1)
  - 3 open review rounds instead of 2 (3)
  - unresolved line dropped (1)
  - escalation every pass (1)
  - start not recorded (9)
  - failed status not written (1)
  - OFF ignored (2)
  - timeout removed (2)
  - never-ran item written more than once (1)
  - max_leads counted from pending starts only (2)
- **Mutations the acceptance tests missed:** gate check removed, and a line with more than 4 fields accepted. The unit tests catch both (1 each), on a mirror copy. The unit conftest puts the tree's own src first on sys.path, so a plain PYTHONPATH swap does not mutate them.
tests: The 189 above, all passed. The brief's form left out `local_only` and `real|green_here|time_limit` cases; none were deselected in these two folders as far as the run shows. I did not run the six W2-96 cases (P-W2-121-5).
discoveries:
- **F1, blocking, S4.** What happens: delete an inbox item (rm instead of mv, or a prune of inbox/read/) and the next pass writes it again as unread. This covers returns and never-ran items: `never-ran.txt` is written but never read. What should happen: the record that an item was written outlives the item, as the model's returns-seen.txt does. Ordinary work: yes, because an honest operator who removes a handled item, or tidies a folder that grows forever, does it with no deliberate construction. Consequence: duplicates an item; each re-raised W2 is held as "unread return", and the items get escalations. Evidence that would reverse it: a governing rule or guard that items in inbox/ and inbox/read/ are never deleted. Then it becomes a recorded row.
- **F2, blocking, S4.** What happens: `escalated.txt` is written before the notifier runs. A notifier that fails once (exit ≠ 0, or a timeout) loses that escalation for good. After a hang, every other escalation due in the same pass is also marked done without being sent. The failure shows only in that one pass's status. What should happen: record the escalation only when the notifier succeeds, and retry on a bounded cadence. Ordinary work: yes, because a push service failing for a moment is ordinary. Consequence: fails open; the owner is never pushed about an unread return, which is the incident DEC-1007 cites. Evidence that would reverse it: a rule that the host's notifier queues and retries on its own, so the dispatcher's at-most-once is correct. (The lead's reading says "runs notifier_command once"; it is silent on failure.)
- **F3, major, S5/S4.** What happens: `notifier_command` is optional at load, but a missing one raises a configuration error in the middle of the pass, after the start. Every pass then reports `PASS FAILED` with exit 2 while sessions keep being started, and the status hides the starts, the running sessions and the inbox (P1). What should happen: require the key at load, or make its absence a problems line. Ordinary work: yes; an unconfigured notifier plus an owner away for an hour. Consequence: other; the status hides what the pass did, and no start breaks a check.
- **F4, major, S9.** What happens: a path that exists only in the working tree, untracked, counts as resolved (P4). The fall-back to "exists on disk" is probably there for gitignored scratch files. What should happen: an untracked, not-ignored path is named. Ordinary work: yes; a forgotten commit is the case S9 exists for. Consequence: other; an uncommitted file is reported as resolved, and the worktree still counts as clean because untracked files are left out.
- **F5, minor, S6.** The acceptance shut-gate tests plant only a memory-shut gate, which the room check also refuses, and they accept a "memory" reason. Dropping the gate check passes them; the unit test `test_a_shut_gate_refuses_every_entry_with_exit_3` catches it by the "gate shut" text. No load-, CPU- or GPU-shut gate is planted anywhere. Ordinary work: yes (a refactor). Consequence: other (latent; `gov launch` re-checks the gate).
- **F6, minor, S9.** A hung git while resolving writes every id and path as `unresolved:` into a permanent item; "could not be checked" appears only in that pass's status. Ordinary work: rarely. Consequence: other (a misleading item).
- **Sound, as probed:**
  - lock and loser behaviour
  - OFF before the lock
  - the start recorded before the spawn, and a crash before the spawn becoming one never-ran item
  - timeouts with the whole process group killed
  - atomic status, items and peaks
  - identity marker matches `build_lead_settings`
  - one start per pass in list order
  - every skip named
  - room formula, with floor and working size read from gate.json
  - S7 round count
  - no watcher process
  - S6 grep
- **History producer:** nothing in src/gov writes history.jsonl. Until something does, the lead's peak is the gate's working size and other kinds count the working size and no CPU.
risks: F1 and F2 can, in ordinary operation, repeat a wake or lose one, which is the inbox's whole purpose (DEC-1007). F3 makes the status unhelpful exactly when the owner is away.
lessons: The repository's pytest refuses `--basetemp` (DEC-898). The unit conftest pins the tree's src, so mutating the unit tests needs a mirror copy of the tree.
proposed_decisions: none (the fixes fit the KPI lines as written)
unresolved: Whether an inbox item may ever be deleted (F1's reversal). Whether the notifier is at-most-once by design (F2's reversal). Who writes the job history.
recommended_next_action: One fix round, the 2nd and last allowed, for F1 and F2:
- F1: keep a returns-seen record and read `never-ran.txt`.
- F2: record an escalation only on notifier exit 0, retried at most every N passes, with the failure shown every pass while it lasts.

Fold in F3 (require `notifier_command` at load) and F4 (name an untracked, not-ignored path) if cheap. Add a load-shut gate case for F5 as a test-designer row. Record F6 as a row.

```
verdict: FAIL
head: 1ec89f0efdbb
findings: 6
- F1 | blocking | S4 | src/gov/dispatch/returns.py:109 (and :146) | a return or never-ran item deleted from inbox/ or inbox/read/ is rewritten as unread on the next pass (planted: read, then rm → the same return item back in inbox/)
- F2 | blocking | S4 | src/gov/dispatch/returns.py:166 | escalation recorded before the notifier runs; one notifier failure (exit 1, or a timeout, which takes every escalation due that pass) is never retried (planted: exit 1, then a working notifier → 0 calls)
- F3 | major | S5 | src/gov/dispatch/returns.py:165, config.py:133 | no notifier_command plus an item unread past the time: every pass exits 2 with PASS FAILED while still starting sessions, and the status hides them (planted: two passes started W2-1 and W2-2, status says only PASS FAILED)
- F4 | major | S9 | src/gov/dispatch/returns.py:85 | a files_changed path that exists only untracked in the worktree counts as resolved (planted: unresolved names only the missing path)
- F5 | minor | S6 | tests/acceptance/W2-121/test_s2_start_rules.py:346 | shut-gate acceptance tests plant only a memory-shut gate and accept "memory"; with the gate check removed they still pass (a unit test catches it); no load/CPU/GPU-shut case
- F6 | minor | S9 | src/gov/dispatch/returns.py:128 | a hung git while resolving writes every id and path as unresolved into a permanent item
```

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": []},
 {"kpi": "S2", "verdict": "pass", "findings": []},
 {"kpi": "S3", "verdict": "pass", "findings": []},
 {"kpi": "S4", "verdict": "fail", "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
   {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]},
 {"kpi": "S5", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S6", "verdict": "pass", "findings": [{"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S7", "verdict": "pass", "findings": []},
 {"kpi": "S8", "verdict": "pass", "findings": []},
 {"kpi": "S9", "verdict": "pass", "findings": [
   {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F6", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S10", "verdict": "pass", "findings": []},
 {"kpi": "F1", "verdict": "pass", "findings": []}
]}
```

guard_refusals:
- 2026-11-12 ~05:27 | Bash `mkdir -p .gov-runtime/scratch/empty-home` before the pytest run | "a reviewer or auditor writes only its own review or audit record (docs/probes/, docs/audit/, docs/assessment/, .gov-runtime/scratch/orchestrator/reviews/), its own scratch, or /tmp (DEC-953 item 2)" | true (a write in the tree; the folder already existed, so nothing was needed)