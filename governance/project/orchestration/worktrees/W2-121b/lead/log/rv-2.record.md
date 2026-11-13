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