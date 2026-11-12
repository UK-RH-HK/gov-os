---
type: probe
task: DAEO-ifgf
reviewer_session: 6b780fde-de77-42cf-b74a-2e17f98434b3
reviewer_session_round_1: 88a93c93-c2a0-4791-8167-d4eb85b38889
implementer_session: bc2586bf-4089-4ab5-b83c-826f8b6fd3c7
implementer_session_round_1: dcea294b-6e50-4ab3-8bae-aea1673e461a
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: dae1c10e0392360d9d4d2dfe06a8889800cf8c91
decisions_applied: [DEC-801, DEC-802, DEC-808, DEC-809, DEC-1010, DEC-136, DEC-820, DEC-1052, DEC-1112, DEC-1144]
---

# Probe record: W2-121b (DAEO-ifgf) gov dispatch part b, the landing: reviews 1 and 2 of at most 2 (DEC-1010)

## The lead's judgement

- **Who probed.** Each round had a fresh, read-only reviewer: role `independent-auditor`, Opus 5.5 at effort high, class C2, started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-12.
  - Round 1: session `88a93c93-c2a0-4791-8167-d4eb85b38889`, probing head `951dbcfa5cc7`.
  - Round 2: session `6b780fde-de77-42cf-b74a-2e17f98434b3`, probing head `dae1c10e0392`.
  - In both rounds step 0 held: the write outside the tree failed with a read-only file system, and the index refresh worked. The head was the same at the start and at the end, and `git status --porcelain` was empty.
  - Neither reviewer met a read refusal. Each met one Write refusal for a probe script under its TMPDIR. Neither retried it or worked around it: round 1 probed inline instead, and round 2 used code reading and the S2 file run.
  - The tripwire changes listed were in other sessions' trees.
- **What was probed.** The branch `w2/W2-121b`, from base `1ef597a43909`:
  - the independent test designer's acceptance suite `tests/acceptance/W2-121b/`:
    - `a60ee938c`, the first 48 cases, red 48 on the base;
    - `ed8aa4904`, two cases fixed to the ticket on the engineer's findings (the batch log's count; the midnight-crossing window's outside case);
    - `7143cabd7`, four S2 wrapper-close cases from review round 1's RV1, red on `951dbcfa5`;
  - the engineer's build `ab5799760`: `src/gov/dispatch/landing.py` and `heavy.py`, the changes in `config.py`, `procs.py`, `run.py`, `state.py` and `status.py`, the read helper `slots.runners`, and unit tests;
  - the round 2 fix `dae1c10e0`, by a fresh engineer given the failing output only: `landing.close_arguments` reads a close's tickets from every process matching the close marker, and part a's `procs.find` is unchanged.
  - `git diff --name-only w2/integrate...HEAD` lists only the ticket's `allowed_paths` and the designer's suite.
- **The lead's own results at `dae1c10e0392`.**
  - The store was rebuilt (exit 0).
  - `gov accept W2-121b`: pass, 52 passed, 0 failed: success-1 10, success-2 12, success-3 13, success-4 14. The runner's `gov.__file__` is `/home/usain/.local/share/gov-os/pin-797495bdfc70/lib/python3.12/site-packages/gov/__init__.py`, and the cases import the tree's `src/` (`/home/usain/gov-os-worktrees/W2-121b/src/gov/__init__.py`).
  - Part a's suites, per the engineer: `tests/acceptance/W2-121` 179/179 and `tests/unit/dispatch` 112/112.
  - `lead_verify`: 4,699 tests, 4 failed, 1 error, 7 skipped. None of them is this ticket's:
    - (1) `tests/acceptance/W2-02/test_w2_02_green_here.py::test_core_schema_is_green_on_this_repository`. The front matter of `docs/changes/W2-176-CIT-P.md` is not YAML at the branch's base (`e395dd430`). `w2/integrate` fixed it in `5289bec52`, so this red goes when the branch lands on `w2/integrate`.
    - (2) `tests/unit/resources/test_w2_157_backstop.py`: three failures (`test_s1_below_then_above…`, `test_s1_the_limit_and_period…`, `test_l5b_…[last]`) and one error (`test_s3_the_limit_comes_before…`, worker gw2). These are W2-157's load-sensitive cases. The run hung on them for about 30 minutes, so the lead stopped by pid, with `proc.sh`, first three SIGSTOPped `time.sleep(120)` children of the verify's own worker, then the looping worker. Re-run alone, the file gave 94 passed in 6.4 s. `backstop.py` does not use `slots`, and `slots.py` gained only a read function.
- **Judged by the threat model (DEC-801, DEC-808, DEC-1010).**
  - Round 1 found one in-scope finding, RV1, judged ordinary work yes and fails open. On a close started through a shell wrapper (an agent's Bash tool, or cron), only the wrapper was read, so a landing of the same ticket went ahead. That is a fail of S2.
  - Per DEC-136 the fix started with a test-design batch given the finding as described behaviour (td-3, four cases red). A fresh engineer then fixed it, and round 2 confirmed the fix, with both directions covered by the cases.
  - RV2 to RV6 are rows, judged `other` or out of scope, and the round 2 fix leaves them unchanged:
    - RV2: a malformed approval sent beside good ones is named in the claiming pass's status only.
    - RV3: a batch whose wrapper is killed with no exit file holds landings as "still running". The Interface defines finalisation by the exit file, so this is for the CTO.
    - RV4: a re-approval at a failed head is dropped without a word ("never twice").
    - RV5: a heavy step under a shell wrapper is reported outside a slot. It is a false finding, never a missed one.
    - RV6: a landing item with several W2 ids holds no start, because part a's start check compares the whole field. Out of scope.
  - Round 1 also gave one narrow Wave 3 row: finalisation records the claimed file's lines, not the batch actually read. Ordinary work: no.
  - Round 2 found no new finding.
- **Judgement: pass.** S1 to S4 pass at `dae1c10e0392`. This was the last round.

## The reviewer's record, round 2 (as returned)

````
**Verdict: all four KPI lines pass at `dae1c10e0392`, and the round 2 fix opens nothing new.** The round 1 fail (RV1) is fixed: a close run under a shell wrapper now blocks the landing of its ticket. I found no new finding. One limit: the Write tool refused my probe script in TMPDIR, so I did not run a real-process probe. The fix is supported by code reading and by the acceptance file run on planted processes.

task: DAEO-ifgf (W2-121b), independent review round 2 (the last, DEC-1010)
decisions: DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-820, DEC-1144

status: done. S1, S2, S3 and S4 all pass at `dae1c10e0392`. Round 1's RV1 is fixed, and the fix adds no new finding.

work_completed:
- Checked identity and ran step 0.
- Read the ticket in full: S1 to S4, the non-goals, "K9 decided", and the Interface items 1 to 4 with the exit codes.
- Read the round 2 fix (`git diff 8675dfded..dae1c10e0`): `landing.close_arguments` and the new `conflicting_close`.
- Read all of `landing.py` and `heavy.py`, and part b's changes to `procs.py`, `run.py`, `state.py`, `status.py`, `config.py` and `slots.py`.
- Read the S2 acceptance file, including the four wrapper cases (`7143cabd7`), and the support helpers they use.
- Ran `tests/acceptance/W2-121b/test_b_s2_closes.py` alone through heavy_slot.sh.

files_changed: none

evidence:
- **Step 0:**
  - (a) the write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ifgf` failed with `OSError: [Errno 30] Read-only file system`.
  - (b) `git update-index --refresh` worked (exit 0, no output).
- **Identity:** `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-ifgf`, top level `/home/usain/gov-os-worktrees/W2-121b`, branch `w2/W2-121b`.
- **Head at start:** `dae1c10e0392`. **Head at end:** `dae1c10e0392`.
- **`git status --porcelain` at the end:** empty.
- **`gov.__file__`:** `/home/usain/gov-os-worktrees/W2-121b/src/gov/__init__.py`.
- **Read refusals:** none.
- **Write refusal (one, not repeated, not worked around):** the Write tool needed a permission that cannot be granted in this session, for `/tmp/gov-launch-6ogh4pma/claude-1000/probe_close.py`. That script was a real-process probe of a close under `bash -c` and `sh -c`. I did not write it another way (Bash or `python3 -c`). I used the acceptance cases and code reading instead.
- **Paths:** `git diff --name-only w2/integrate...HEAD` lists only `src/gov/dispatch/{config,heavy,landing,procs,run,state,status}.py`, `src/gov/resources/slots.py`, `tests/unit/dispatch/test_w2_121b_landing.py` and `tests/acceptance/W2-121b/*`. All are in `allowed_paths` or are the designer's.
- **Nothing in the code names this repository or the CTO's tool:** a search of `src/gov/dispatch` for `Dynamic-Agentic`, `orchestration/tools`, `DAEO-` and `W2-1` found nothing.

tests:
- `test_b_s2_closes.py` through heavy_slot.sh: 15 passed in 11.08s. This includes the four `test_a_close_under_a_shell_wrapper_blocks_the_landing_of_its_ticket[...]` cases.
- I re-ran nothing else; the lead's results stand as reported.

discoveries:
- **What the fix does now.**
  - A close run under a shell wrapper (`bash -c "cd x && <close> W2-7 ; …"` or `sh -c …`) blocks the landing of W2-7. That holds whether the close names the W2 id or the ticket id.
  - The ids are read from every process carrying the close marker, so the close's own child is read, not only the wrapper. It is no longer judged from the wrapper's one-string argument.
  - The same wrapper shape closing a ticket outside the landing (W2-8) does not hold it.
  - The acceptance case checks both directions. An implementation that blocked on any wrapper would fail its second half, so the case cannot pass while S2 is false.
- **Part a is unchanged.** Part a's job counting (`procs.find`) is untouched, so its Interface and the jobs list are unchanged. The "committing its records" checks (`index.lock`, `close_record_paths`) still name the close from the jobs list, and that list is built with the same marker, so the two cannot disagree.
- **Edges I probed by reading and found sound:**
  - A lead's process is excluded from the close reading, as it is in part a.
  - The dispatcher's own process is excluded.
  - A process that ends between the process-table read and the argument read gives no arguments, and so no hold.
  - The sort over `(pid, arguments)` never compares the argument sets (each pid is unique).
  - A non-sharing wrapper whose command string happens to contain the landing's id does not block, because arguments are matched whole.
  - The order is unchanged: a shared ticket first, then `index.lock`, then `close_record_paths`.
- **The fix holds more landings than strictly needed; it never lets more through.** Any process anywhere on the machine that carries the close marker and an argument exactly equal to an id in the landing now holds that landing. Examples are a close in another project, or a viewer started with the marker and the id as separate arguments. The landing waits until that process ends: the fix fails closed, never open. Part a already counted such processes as close jobs. Not a finding.
- **Round 1's rows are not changed by the fix.** RV2, RV3, RV4 and RV6 do not touch close detection. RV5, a heavy step under a wrapper reported outside a slot, comes from part a's `procs.find` and from `heavy.py`, and the fix touches neither. They stay rows as judged in round 1.
- S1, S3 and S4: the fix touches none of their code (`finalise`, `step`, `nightly`, `heavy.py` and `slots.runners` are as round 1 judged them), so their pass stands.

risks:
- No real-process probe was run, because of the Write refusal. Evidence that would reverse the S2 pass: a real close under `bash -c "cd / && <close> W2-7 ; echo"` whose child's command line, as read from `/proc`, lacks the close marker. That would be the case for a close command that renames its own process title. Nothing in `src/` does that.
- The fix scans the process table a second time in each pass that has a close running. This costs efficiency only.

lessons: a fix that reads ids from a wrapper's children needs a case in both directions (the sharing child blocks, the non-sharing child does not). `7143cabd7` has both, which is what makes this pass trustworthy.

proposed_decisions: none

unresolved:
- The Write tool refusal for a probe script under TMPDIR. The brief allows probe scripts there, but the tool asked for a permission this session cannot grant. The lead may want to check the auditor's write permission for TMPDIR before the next review.

recommended_next_action: the lead records this verdict. No round is proposed. Rows RV2 to RV6 from round 1 go forward as recorded rows. Part b is ready for the lead's return to the orchestrator.

**Findings:** none new at this head. Round 1's RV1 (S2, in scope, ordinary work yes, fails open) is fixed and verified by the four wrapper cases. RV2 to RV6 are unchanged rows from round 1, and the fix does not change their classification.

Classification: 0 findings blocking; 0 new rows; RV1 fixed; RV2 to RV6 carried as rows, unchanged by the fix.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}]}
```
````

## The reviewer's record, round 1 (as returned)

````
I recommend one more round, for one fix. The close check in S2 can let a landing go while a close of the same ticket is running, in the way closes are normally run. S1, S3 and S4 pass, with five findings to note but no block. I wrote nothing in the worktree, and the head is the same as at the start.

task: DAEO-ifgf (W2-121b), independent review, round 1 of at most 2, head 951dbcfa5cc7 on w2/W2-121b
status: done. S1 pass, S2 fail, S3 pass, S4 pass. One finding blocks (RV1).
work_completed: Read the ticket (S1–S4, non-goals, "K9 decided", Interface items 1–4 and the exit codes) and part a's Interface. Read the engineer's code (3476e8628..ab5799760, all of `landing.py` and `heavy.py`, and the changes to `config.py`, `procs.py`, `run.py`, `state.py`, `status.py` and `slots.py`). Read all of `tests/acceptance/W2-121b/`, the fix commit ed8aa4904, and the unit test list. Compared the meaning with the reference dispatcher's landing, close and nightly code. Reproduced RV1 in memory against this worktree's `src/`, plus one read-only check of this session's own process tree.
files_changed: none
evidence:
- Step 0: (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ifgf` failed with `OSError: [Errno 30] Read-only file system`, so the sandbox holds; (b) `git update-index --refresh` worked, no output.
- Identity: `independent-auditor`, `DAEO-ifgf`; worktree `/home/usain/gov-os-worktrees/W2-121b`, branch `w2/W2-121b`.
- Head at my start: 951dbcfa5cc7. Head at my end: 951dbcfa5cc7.
- `git status --porcelain` at the end: empty.
- `gov.__file__` = `/home/usain/gov-os-worktrees/W2-121b/src/gov/__init__.py`
- `git diff --name-only w2/integrate...HEAD` lists only the ticket's `allowed_paths` (`src/gov/dispatch/*`, `src/gov/resources/slots.py`, `tests/unit/dispatch/test_w2_121b_landing.py`) plus `tests/acceptance/W2-121b/*`.
- Read refusals: none. One write refusal: the Write tool asked for permission to create a probe script at `$TMPDIR/ancestry.py`, and it was not granted. I did not retry it or write the file another way; I ran the probe inline with `python3 -c`, which writes nothing.
- RV1 probe 1, this session's process tree: a command run from the agent's Bash tool is a child of `/bin/bash -c "…; eval '<command>' < /dev/null && pwd -P …"`. The whole command text sits inside one argument of that shell.
- RV1 probe 2, in memory: a table with that shell (pid 100) and its child `python3 …/gov close W2-7` (pid 101), with marker `gov close`. `procs.find` returned `jobs [{'kind': 'close', 'pid': 100}]`, and the tickets shared with the landing `{W2-7}` were `[]`.
tests: I re-ran no suite. The lead's results stand: `gov accept` 48 passed; lead_verify 2 reds outside this ticket's paths. I ran no pytest.
discoveries:
- The reference dispatcher found closes by checking every process that runs the close script. This code checks only the topmost process matching the marker (part a's `procs.find` drops its children), which causes RV1.
- The reference finalised a landing when its process was gone. This code finalises only when an exit file exists, as the Interface says, which causes RV3.
- This project's `heavy_slot.sh` takes its own flock slots, not `gov resources` slots. Under it, every heavy step would show as outside a slot. That is a project-setup matter, not code in this ticket.
- What I checked and found sound:
  - S1:
    - The claim needs all four conditions.
    - The claim is an atomic `os.rename` made before the spawn.
    - Lines already in `land-done.txt` are dropped.
    - A second pass while a batch runs claims nothing and says why.
    - Unapproved and malformed lines are never sent, and malformed ones are named.
    - Finalisation happens in a safe order (done lines, then the inbox item, then removing the claimed file), so a pass that dies halfway is finished by the next. Exit 0 gives `landed`, others give `failed (exit N)`.
    - A launch that fails writes exit 127 and is finalised as failed.
    - A `land.txt` rewritten during a landing waits for it to finish.
  - S2:
    - Matching by W2 id and by ticket id (through `.tickets/` `external-ref`/`wbs_id`) works.
    - `index.lock` is found in the right git folder, `close_record_paths` blocks when all changes are under it, and a close with no shared ticket does not block.
    - `commit_records` retries only on an `index.lock` message, commits only the given paths, raises `CommitFailed` at the end, and two at once both land.
  - S3:
    - The window maths is right, including a window crossing midnight.
    - The marker is read relative to the root or as an absolute path, and its absence means the hold lasts until `until`.
    - A claimed landing is still finalised during the hold and never stopped; starts and the inbox are not held.
    - The `land_hold` key, the status line text and exit 0 all match the Interface.
  - S4:
    - Only the four kinds count.
    - The ancestor walk ends at init and at a loop.
    - Slot runners come from the holders read by `gate.read` (flock-held only).
    - The finding text is exact and the exit code does not change.
    - `slots.py` gains only a read helper, and `command.py` is untouched.
  - Every held landing gives exit 0 with a `land:` reason.
  - Part a's Interface is changed only by additions.
  - No new key lives outside `dispatch:`, and nothing in `src/` names this repository or the reference tool.
  - Both fixed cases in ed8aa4904 are right against the ticket:
    - The stub counts all of its arguments, so 4.
    - `(60, 30)` put "now" inside a window crossing midnight; `(60, -30)` is truly outside it.
risks: none beyond the findings below.
lessons: Acceptance tests that plant a process as one flat command line miss how commands really appear when run from a shell. A planted close (or heavy step) needs at least one case under a `bash -c` wrapper whose child matches the same marker.
proposed_decisions: none
unresolved: none
recommended_next_action: Classification: 1 finding in scope, ordinary work, fails open (RV1); 5 rows (RV2–RV6: other, or not reachable in ordinary work). Recommendation: round 2 for RV1 only.
- The fix: work out a close's tickets from every process in its tree that matches the marker (or every process matching it), not only the topmost one.
- The designer adds an S2 case: a close running under a `bash -c` wrapper with a matching child.
- RV2, RV3 and RV4 can ride along as small fixes if the lead agrees; RV5 and RV6 are rows.

RV1: src/gov/dispatch/landing.py:216 (with src/gov/dispatch/procs.py:71) When `gov close <ticket>` is run through a shell, a landing of that same ticket goes ahead while the close runs. This happens from an agent's Bash tool (`bash -c "… eval 'gov close W2-7' …"`) or from cron (`sh -c`). Both the shell and its `gov close` child match the close marker. Only the shell is kept as the close (its matching child is dropped), and the shell's arguments hold the whole command as one string. So no argument equals `W2-7`, the close shares no ticket with the landing, and the landing is claimed and sent. It should have been held, as with the test's flat planted close. Unless the close's record commit holds `index.lock` or leaves the tree unclean at that moment, nothing else stops it.
Ordinary work: yes, because closes are run by the orchestrator from a Claude Code session, whose Bash tool always wraps the command in `bash -c` (seen in this session's own process tree).
Consequence: fails open
Scope: in (S2: "a running close with a ticket in the landing's set blocks the landing")
Would reverse it: a pass, with a real close started from an agent's Bash tool for a ticket in `land.txt`, that holds the landing; or evidence that closes never run under a shell wrapper whose child matches the marker.

RV2: src/gov/dispatch/landing.py:102,113 A malformed approval sent together with good ones disappears after one status. For example `W2-8=abc1234`, a short hash. It is named as not sent in the status of the claiming pass, then goes into the claimed file with the batch. Finalisation works out the bad lines but reports them nowhere, puts them in neither the inbox item nor `land-done`, and deletes the claimed file. From the next pass on, no file and no status mentions the line. It should stay visible until someone acts, for example named in the `.land.txt` item.
Ordinary work: yes, because short or mistyped hashes are common (row W2-L423's 12-digit rule exists for that reason).
Consequence: other (the Interface asks only that it is "named in the status", and it is, but for a single pass)
Scope: in (S1)
Would reverse it: a reading of the Interface under which a mention in one pass's status is the intended, lasting record.

RV3: src/gov/dispatch/landing.py:91,283 A batch whose wrapper shell is killed blocks all landings for good, with a false "still running". This happens on a reboot, `wsl --shutdown`, or a kill of the whole process group during a long landing. No exit file is written, so the claimed file is never finalised: each later pass says `land-… is still running (one landing at a time)`, claims nothing, and writes no inbox item for that outcome. The approvals stay on disk; nothing is sent wrongly. The reference checked whether the landing process was still alive.
Ordinary work: yes, because a machine restart during a landing of many minutes is plausible.
Consequence: other (landing stops and stays stopped; nothing is sent or lost)
Scope: in (S1, "each outcome becomes an inbox item"); the Interface itself defines finalisation by the exit file.
Would reverse it: an owner reading that a landing with no exit file is meant to wait for a person indefinitely.

RV4: src/gov/dispatch/landing.py:281 Re-approving a failed landing at the same head is ignored without a word. The failed approval's line goes into `land-done.txt` with its non-zero exit code. When the orchestrator writes `W2-7=<same head>` again to retry, it is dropped from every batch: the status says `nothing to land`, `queue` hides it too, and `land.txt` keeps the line forever. This follows the Interface's "never twice", but the drop should at least be named.
Ordinary work: yes, because retrying after a flaky landing failure is ordinary.
Consequence: other (the failure was reported by its own inbox item; the retry is held, not sent twice)
Scope: in (S1)
Would reverse it: an owner ruling that a failed head must never be retried and that a silent drop is acceptable.

RV5: src/gov/dispatch/heavy.py:33 (with procs.py:71) A heavy step that does hold a slot is reported as outside one when started through a shell. Take `bash -c "… gov resources --slot test -- pytest …"`: the shell matches the test marker and is kept as the step, and the walk goes up from the shell, never down to the slot runner. So it gets `slot: null` and the finding `heavy step outside a slot: test pid <shell>`. A step really outside a slot is never hidden.
Ordinary work: yes (same wrapper as RV1)
Consequence: other (a false finding, never a missed one)
Scope: in (S4)
Would reverse it: evidence that heavy steps are never started under a wrapper whose own command line holds the marker.

RV6: src/gov/dispatch/landing.py:110 (with run.py:88, readiness.py:133) A landing's inbox item blocks a new start of its W2 only when the landing had one ticket. Part a's start check compares the W2 being started with each unread item's `W2:` field as a whole string. A landing of one ticket (`W2: W2-7`) therefore holds a start of W2-7 ("unread return") until the item is read. A landing of several (`W2: W2-7 W2-8`) holds none.
Ordinary work: yes
Consequence: other
Scope: out (part a's start check meets part b's space-separated field)
Would reverse it: an owner reading that land items are meant to hold starts, or never to.

Not a finding, a narrow row: finalisation records as landed every good line in the claimed file at finalisation time, not the batch actually sent (`landing.py:103`). A write that had opened `land.txt` before the rename and lands in the inode after the batch was read would be recorded as landed without being sent. Ordinary work: no, because it needs a write to land in the microseconds between the rename and the read. Consequence: loses work. Scope: in (S1). A Wave 3 row.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "RV2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "RV3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "RV4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "RV6", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "fail", "findings": [{"id": "RV1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": [{"id": "RV5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
````
