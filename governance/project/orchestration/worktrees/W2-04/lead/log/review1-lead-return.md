task: W2-04 (DAEO-u4oz): run the FULL independent review on the verified head b37b5c8f1741, triage it under the moderator rule, and land it (DONE) or return the blocking finding (PACKAGES).
status: PACKAGES — the review failed: F1 is in scope, can be hit in ordinary work, and fails open (an emptied mandatory file is shown as read with the empty-content hash and 0 tokens); `verdict.py` gives READY = False.
work_completed: Checked the head (b37b5c8f1741, tree clean, hooks folder has only samples). Updated `briefs/rev-1.md`: it now carries JUDGEMENT.md word for word as it stands on `w2/integrate` (with DEC-1010 item 1's section on how reviews converge, checked by diff), asks for the ```verdict block (ids success-1 to success-7 and failure-1, plus a `judgement:` line), and adds a note on the embedder (`timeout 120` on `gov retrieve`). Filled it as `briefs/rev-1.filled.md`, with the head written as 12 digits. Started one fresh independent-auditor through `gov launch`, sandboxed, `--effort max`, read-only tools (session 5042a938, 100 turns, 18.7 min). Its return has all twelve fields. Triaged it, computed READY with the CTO's `verdict.py`, and wrote the failing record as a draft (not committed). Updated CHECKPOINT.md. No test run, no rebuild, no commit.
files_changed: none in the tracked tree. Scratch only: `.gov-runtime/scratch/lead/briefs/rev-1.md`, `briefs/rev-1.results.part`, `briefs/rev-1.filled.md`, `fill_rev.py`, `ready_check.py`, `draft_probe.py`, `probes/PR-DAEO-u4oz-rev-1-DRAFT.md`, `tripwire-before-7.json`, `log/rev-1.json`, `log/rev-1.rc`, `CHECKPOINT.md`.
evidence: head b37b5c8f1741, unchanged; `git status --short` shows nothing. Reviewer's step 0: the write outside the sandbox was refused (read-only file system), and the git object write and index refresh worked. Reviewer's check: `gov.__file__` = /home/usain/gov-os-worktrees/W2-04/src/gov/__init__.py. `ready_check.py` → `(False, ['success-5: F1 blocks (in scope, ordinary work, fails open)'])`. Tripwire-7 compare (rc 1): nothing changed in this tree; heads moved in the main tree, W2-00-record, W2-91 (its W2-86 and W2-91 acceptance folders) and W2-92, and the W2-91-tests tree appeared. All of these are other sessions. keyword_warn: 0 files. Scratch: /tmp/gov-os-lead-W2-04 is 24 MB / 3.0K inodes; `.gov-runtime/scratch` is 21 MB / 140 inodes.
tests: none run, as the brief said. The reviewer ran 12 small probes of its own and no suites.
discoveries: (1) F1: `_read_record` in `src/gov/context/__init__.py` (lines 48-50) hashes whatever the working-tree file holds. An emptied capability file, or an emptied dependency ticket, gives exit 0 and `ok: true`, the empty-content sha256 and 0 tokens, and `context_check` is green. `--brief`, which the session-start hook injects, lists it as present. Spec S5 forbids exactly this. Register spans are not affected. (2) F2: the round-2 fix (e0d06a04ae53) makes `further_batch` empty when the room ends exactly on a batch boundary or is zero. Spec S7 and S7a say it starts at the first ranked item not stacked, so the fix and the spec disagree. (3) F4: 31 open or in-progress tickets refuse their context at 6,000 tokens (8 in progress: W2-11, W2-20, W2-56, W2-61h, W2-81, W2-90b, W2-91, W2-92). The close builds the context only after its acceptance and regression runs, and counts that refusal. The session-start hook drops the error without a word. (4) DEC-960 still reads ACCEPTED although DEC-961 supersedes it, against DEC-866 item 1; no ticket cites it today. (5) JUDGEMENT.md in this worktree is older than DEC-1010.
risks: Merging as it is would show a worker a mandatory record as read after its file has been truncated (F1). After the merge, the closes of the 31 tickets in F4 fail late, after their full runs, and their sessions lose the context silently. F1's repair must check that the working-tree file still holds the record the store lists, so it neither misses a file cut to whitespace nor blocks a file that was legitimately edited.
lessons: Every Python probe in the sandbox should run with `PYTHONDONTWRITEBYTECODE=1`. Otherwise a `PYTHONPATH=src` import writes `__pycache__` beside `src/`. It is git-ignored; the tree stayed clean. A reviewer brief should name the session-start hook as the second caller of `gov.context.context`.
proposed_decisions: P-W2-04-6 (F1, blocks), P-W2-04-7 (F4) and P-W2-04-8 (F2), below. Rows: F3, F5, F6 and DEC-960's status line.
unresolved: The reviewer did not check whether held-out material is in the lexical corpus: that needs a search over `governance/project/`, which DEC-820 forbids. The behaviour is unchanged from before this ticket. The reviewer's sandbox temp probe folder (about 27 MB, 1,936 entries) was left because its delete was refused. P-W2-04-4 (the embedder) and the W2-55 table follow-up stay with the owner.
recommended_next_action: The CTO decides P-W2-04-6 (one repair round: a test-design batch for F1, then a fresh engineer, then review 2 with a different model or effort) and P-W2-04-8. P-W2-04-7 goes to the CTO before the merge.

guard_refusals:
- 09:34 | the reviewer's recursive delete of its own probe folder in its sandbox temp | a harness permission was not granted (no hook reason) | true | 1 min; left in place and named
- read refusals (DEC-849): lead 0, reviewer 0

brief_gaps:
- JUDGEMENT.md in this worktree predates DEC-1010; the current text is on `w2/integrate` only | this ticket's part (the resume) | 5 min, estimated
- The verdict block's KPI line ids (success-n, failure-n) are not defined anywhere I found | skill orchestration / JUDGEMENT.md | 3 min, estimated
- Reviewer: the session-start hook is a second caller of `gov.context.context` that drops errors | the reviewer brief's "What you read" | 3 min (reviewer's figure)
- Reviewer: the close builds the context only after its runs, and counts that refusal | the same place | 4 min (reviewer's figure)
- Reviewer: `PYTHONPATH=src` writes `__pycache__` beside `src/` in the sandbox | the DEC-732 standing rule | 2 min (reviewer's figure)
- Reviewer: `tests/acceptance/W2-04/w2_04_support.py` builds fixture projects and can be imported read-only | "What you read" | 2 min (reviewer's figure)

**Workers:** one, the reviewer rev-1 (independent-auditor), sandboxed through `gov launch`. Its brief told it to use `gov retrieve` (with a timeout), but it did not: everything it read was named in the brief or found by targeted searches in named folders. Tripwire is as above.

## P-W2-04-6 (F1): an emptied mandatory file is shown as read. **It blocks all of W2-04's landing.**
1. **Context:** KPI 5 and spec S5: a mandatory input that cannot be read, or is missing, blocks the context or is marked `"read": false`. It is "never shown as read with the sha256 of empty content or with 0 tokens" (row W2-H034).
2. **What happened:** review 1 at b37b5c8f1741 emptied a capability file in the working tree (what a truncating write leaves), and also a dependency ticket. `gov context` gave exit 0 and `ok: true`, the input ACTIVE with 0 tokens and the empty-content sha256, and the check was green. A file cut to one newline gives 1 token. Register entries already block, because their span is read from the store.
3. **Why it matters:** a worker's packet presents a constraint as read when it holds nothing. That is W2-H034's own symptom, so it fails open. A truncating write is an ordinary accident, and the session-start hook rebuilds the context at every start, resume and compaction. The close is safe, because it refuses a tree that differs from HEAD.
4. **Options:**
   - (a) One repair round (the last before the owner). A test-design batch gets F1 as a described behaviour (DEC-136): a mandatory file, or a dependency ticket, emptied or reduced to whitespace in the working tree → BLOCKED naming the id and the file, or `read: false`. Then a fresh engineer implements it inside `src/gov/context/**`, with F2 and F3 riding along if decided (DEC-802). Then `gov accept`, the scoped run, and review 2, the last, with a different model or effort (DEC-1014). Cost about 3 to 4 hours including slot waits; low risk; nothing outside the ticket's paths.
   - (b) Land now and make F1 a row. This leaves a fail-open on the ticket's own KPI, so it contradicts DEC-1010's blocking rule. Not recommended.
5. **Recommendation:** (a), confidence high. Classification (DEC-809): F1 is in scope, ordinary work yes, fails open (blocks). F2, F3 and F6 are in scope, ordinary work yes, other (rows). F4 and F5 are out of scope (rows or packages).
6. **What it blocks:** the merge and the close of W2-04, and so W2-15a on memory's critical chain. Waiting costs W2-15a's start. Nothing else in this ticket is open.

## P-W2-04-8 (F2): `further_batch` on an exact fit. **Part only; it does not block.**
1. **Context:** S7 and S7a say `further_batch` starts with the first ranked item not stacked, and is "an empty list when nothing was left".
2. **What happened:** the round-2 fix (e0d06a04ae53, made for the acceptance case `test_further_batch_is_at_most_one_batch_long`) returns `[]` when the room ends exactly on a batch boundary, or is zero, even though ranked items remain (39 in the probe).
3. **Why it matters:** the packet hides what it left, which goes against DEC-860's "names what it left". It is not a fail-open: a full last batch hints that more remains.
4. **Options:**
   - (a) S7a holds as written: in the repair round the test designer adds the exact-fit and zero-room cases and the engineer fixes them. Small cost, but the test designer may have to revise round 2's case (`Rewrite-Reason`).
   - (b) Keep the code as it is and record the exact fit as a row.
5. **Recommendation:** (a) if P-W2-04-6 (a) runs anyway, because it rides along at no extra round; confidence medium. The CTO's P2, since it touches a test's reading.
6. **What it blocks:** nothing on its own.

## P-W2-04-7 (F4): 31 tickets refuse at the default ceiling. **Out of scope; it blocks nothing in W2-04, but should be decided before the merge.**
1. **Context:** S2's refusal is working as specified. The reviewer ran the context over 182 tickets: 8 in progress and 23 open refuse.
2. **What happened:** the close builds the context only after its acceptance and regression runs (`src/gov/close/command.py:239-243`) and counts `CONTEXT_FAILED` (lines 247 and 335). The session-start hook drops the error without a word (`template/governance/kernel/hooks/sessionstart.py:150-158`).
3. **Why it matters:** after the merge, those closes fail late and are counted, and their sessions start without a context and without saying so.
4. **Options:**
   - (a) Merge, and tell the 8 in-progress leads now to trim their sources or text before they close.
   - (b) A follow-up ticket (owning `src/gov/close` and the hook) that moves the context gate before the test runs, uncounted, and makes the hook name the refusal.
   - (c) Re-baseline the ceiling for implementation tickets (DEC-105's three options).
5. **Recommendation:** (a) now plus (b), confidence medium. Filing (b) is the owner's P1 (DEC-974).
6. **What it blocks:** none of W2-04's own work; waiting costs late failed closes after the merge.

**Rows (Wave 3 or follow-up):**
- F3: the check is green when every ticket refuses ("0 built, 2 refused"); it should say unmeasured. In scope, could ride along with the repair.
- F5: on a store older than HEAD, `gov context` lets a source that HEAD retired satisfy the ticket. The check and the close already handle a stale store.
- F6: only the 12 longest words of the query are searched, and the packet does not show which.
- DEC-960's status line should be marked superseded by DEC-961 (DEC-866).

**Branch state:** w2/W2-04 at b37b5c8f1741, clean, nothing committed this run. The failing record is the draft `.gov-runtime/scratch/lead/probes/PR-DAEO-u4oz-rev-1-DRAFT.md` (READY False). The lead checkpoint is `/home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/CHECKPOINT.md`. The temp folder /tmp/gov-os-lead-W2-04 (24 MB) is left for the orchestrator to remove. The plan validator was not run (DEC-738).