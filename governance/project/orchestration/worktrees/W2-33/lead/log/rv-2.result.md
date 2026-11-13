**Sandbox check (step 0):** passed. (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-33` failed with `OSError: [Errno 30] Read-only file system`, and no file exists. (b) `git hash-object -w --stdin` worked (blob `1ae28402a109`), and `git update-index --refresh` exited 0. `GOV_TICKET=DAEO-lrre`.
**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing. No embedder, reranker or model was started.

task: DAEO-lrre (W2-33), rv-2, the narrow independent check after review round 1. decisions: DEC-801, DEC-808, DEC-1010, DEC-1050, DEC-537, DEC-236, DEC-1156
status: DONE (PASS)
work_completed: I checked `git diff 3b3a90d74c3e 1221ee0e4` against the four questions. HEAD is `1221ee0e4feb0585bc452fca2bab2ae00a9bc087`, as expected. I ran W2-33 and W2-128 read-only through the gate, ran the compose check, recomputed every sha256 and line count in the CIT-P, and compared its §4 with the 50 failures of the full-suite run on `3b3a90d74c3e`.
files_changed: none. `git status --porcelain` is empty at the end. The only write was the blob from the step 0 check, which the check requires.
evidence: the test run gave `217 passed in 11.10s` and nothing was deselected. The compose check printed `equal(template root): True`. The sha256 values and `--numstat` counts at `3df1ac2deb1b` and `c4b97716164e` match every row of the CIT-P table. Between `c4b97716164e` and `1221ee0e4` only `docs/changes/W2-33-CIT-P.md` changes.
tests: `tests/acceptance/W2-33` and `tests/acceptance/W2-128`, 217 passed, run with `-m "not local_only" -k "not real and not green_here and not time_limit"`. The exclusion left out nothing in these two folders (pytest reported 0 deselected).
discoveries: (1) The brief's path `.gov-runtime/scratch/lead/log/verify/parallel.xml` no longer exists. At 00:37 the lead started a new verify run in `verify/`, and the run on `3b3a90d74c3e` moved to `.gov-runtime/scratch/lead/log/verify.20261113-001601-2517310/parallel.xml`. I used that file: 5590 tests, 50 failed. (2) Inside the launch sandbox, `heavy_slot.sh` cannot remove `/tmp/gov-os-heavy-prio-*` (read-only) and cannot write `.../orchestrator/log/heavy-slot-waits.jsonl`. The run still went through the gate. The leftover priority files may skew the gate's order for other waiters. This is not part of this diff.
risks: the 46 copy-related reds (W2-153, W1-38, W1-33) and the research-hash red stay on this branch until the copies ACT and the CTO's DEC-1156 (7) revision land.
lessons: a brief that names a lead's verify path should name the timestamped folder, because the next verify run moves the old one.
proposed_decisions: none
unresolved: none
recommended_next_action: land on this check. Record N1–N3 as rows. Pair the land with the copies ACT, as CIT-P §4 says.

## Findings
Classification: 3 findings, all recorded rows, none in scope and fail-open or work-losing. Nothing blocks.

**N1.** The new sentence in the CTO's file says the CTO "starts each ticket lead" from `role-lead.md` and `brief.md`. The roster in the same change says the Senior Engineer starts the lead, or the CTO only until Senior Engineers run.
- Where: `template/governance/kernel/roles/orchestrator.md:11`, and the same text in `template/.rulesync/subagents/orchestrator.md:96`. It conflicts with `ticket-lead.md:11` and `senior-engineer.md:11` and `:18`.
- Severity: low.
- Ordinary work: yes, because a CTO reading only its own file could think it starts leads after the layers run. Consequence: other (a wording gap, not a guard or gate statement). Row.
- Would reverse it: an owner decision saying the CTO keeps starting every lead after Senior Engineers run.

**N2.** CIT-P §4 says "50 failed, all listed here" inside the copies bullet, but that bullet lists 46. The other 4 (the research-hash case and the 3 W2-128 cases) sit in the next two bullets. The total over §4 is complete and correct.
- Where: `docs/changes/W2-33-CIT-P.md:77-97`.
- Severity: cosmetic.
- Ordinary work: yes. Consequence: other. Row.
- Would reverse it: none needed. It is a matter of phrasing.

**N3.** The CIT-P's `review:` header already cites "narrow check of the fix c4b977161" while that check (this one) had not yet run.
- Where: `docs/changes/W2-33-CIT-P.md:12`.
- Severity: low.
- Ordinary work: yes. Consequence: other. It becomes true with this PASS. Row.
- Would reverse it: a FAIL here, which would make the header false.

## Answers
1. **Nothing changes beyond what is stated.**
   - `engineer.md`: the Purpose line, unchanged in text, moves up to line 5, so the defaults lines follow it.
   - `orchestrator.md`, kernel and rulesync source: one sentence is added to Purpose.
   - The CIT-P is the only other file touched.
   - Every labelled line form appears once, whole, at column 0. In `engineer.md` there are 14 labels; Purpose is on line 5. In `orchestrator.md` there are 15 labels. The tests agree: 217 passed.

2. **The sentence is true about the templates, with N1's caveat about who starts leads.**
   - `brief-lead.md` reads "Replaced by `role-lead.md` (the role) and `brief.md` (the envelope) in this folder (DEC-1050, TPL-1)".
   - `brief.md` describes itself as the assignment envelope, and `role-lead.md` is the lead's role.
   - DEC-1050 orders templates for every role, the lead included, and DEC-537 created the lead brief template. Both citations hold.
   - `template/.rulesync/subagents/orchestrator.md` still equals `portability.compose(Path('template'), 'orchestrator')`: True.

3. **No.** The fix brings no fail-open or work-losing statement. It adds one descriptive sentence and moves one line. No guard, gate, permission or path statement changes.

4. **Yes, the hashes are right and §4 names every red.**
   - All 10 sha256 values match the files: the "before" column at `3df1ac2deb1b` (three files absent there, as the table says) and the "after" column at `c4b97716164e`. All line counts match too.
   - §4 names every one of the 50 failures:
     - 23 W2-153 source cases;
     - 2 unit cases;
     - 5 W1-38 field-agreement cases, plus the registered-family check;
     - 10 W1-38 held-out-step cases;
     - 5 W1-33 kernel-equals-generated cases;
     - the research-hash case;
     - the 3 W2-128 cases. The fix turns these green: both F6 params and line-5 pass in my run.
   - That leaves 47 reds after the land, all named.

```verdict
verdict: PASS
probed_commit: 1221ee0e4feb0585bc452fca2bab2ae00a9bc087
findings: 3
```
guard_refusals: none