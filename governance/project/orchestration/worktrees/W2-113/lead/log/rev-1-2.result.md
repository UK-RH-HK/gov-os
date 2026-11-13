```verdict
ticket: DAEO-g29a
head: 6542b7ec525b
round: 1
verdict: PASS
blocking: 0
```

**Step 0, the sandbox check:** (a) writing the trial file failed with `OSError: [Errno 30] Read-only file system`, and no file was created. (b) `git hash-object -w --stdin` worked and returned `1ae28402a109…`. `GOV_ROLE=independent-auditor` and `GOV_TICKET=DAEO-g29a`. HEAD is `6542b7ec525b47b8…` and the worktree was clean at the start and at the end.

**Classification:** 6 findings, none blocking. Four cannot happen in ordinary work. The other two (R1-2, R1-6) can, but neither fails open nor loses work. R1-6 is out of scope.

## Findings

**R1-1, non-blocking, in scope: success-2 (W2-110's F5).** `src/gov/guard/install.py:320-321` and `:336-343`.
- **What happens:** when the rule itself cannot run, the refusal still says the coordination ticket "is not set" and that the roster "cannot be read". It then tells the CTO to set a key that is already set. This is exactly F5's own case, and it was not changed.
- **How I showed it:** I planted a correct roster (`coordination_ticket: hc-0001`) and the ticket file, then called `cto_install` in-process for the CTO, with PyYAML blocked. Normal run: `(True, '')`. With PyYAML blocked: `(False, "…coordination ticket is not set (governance/project/roster.yaml cannot be read: ModuleNotFoundError…). Set the top-level key…")`.
- **Ordinary work:** no, because the pinned interpreter ships PyYAML. W2-110's review judged it the same way.
- **Consequence:** other. It still refuses.
- **What would be right:** when the lookup itself fails, the words should say that the rule could not run, not that the key is missing.
- **What would reverse this:** a KPI reading that limits success-2 to the two cases in its parenthesis.

**R1-2, non-blocking, in scope: success-2 and I2 (iii).** `src/gov/guard/install.py:339-343`.
- **What happens:** when `tk` is missing, A0 creates no ticket. The refusal still says to set the key to "the coordination ticket in .tickets/". No such ticket exists, and the words do not say to create one or to run A0 again once `tk` is vendored.
- **What it gets right:** it names `GOV_TICKET`, says how to set the key, refuses, and does not claim a key was set.
- **How I showed it:** an adopted product without `tk`. A0 succeeded with `created []` and `roster None`. The orchestrator's install was refused (deny) with the text above.
- **Ordinary work:** yes, because I2 (iii) is a decided default.
- **Consequence:** other. The guard stays closed.
- **What would be right:** when no coordination ticket exists, the refusal should say to create one first, or to vendor `tk` and run A0 again.
- **What would reverse this:** the owner reading "the coordination ticket in .tickets/" as an instruction that includes creating it.

**R1-3, non-blocking, in scope: I1 (A0's failure path).** `src/gov/adopt/stages.py:102-104`; also `src/gov/tasks/tickets.py:28`, which is outside the ticket's paths.
- **What happens:**
  - If `tk` writes its ticket file and then fails, or prints an unexpected last line, A0 refuses but leaves the ticket file untracked in `.tickets/`.
  - If the ticket file `tk` writes has no closing `---`, `gov adopt` crashes with an uncaught `ValueError` traceback (exit 1, no JSON envelope) and leaves the file behind too.
- **How I showed it:** I replaced `tk` with stand-in scripts:
  - writes then fails: `ADOPT_COORDINATION_TICKET_FAILED`, then `?? .tickets/hb-zzzz.md`
  - extra output line: refused, then `?? .tickets/hb-yyyy.md`
  - no closing `---`: traceback, then `?? .tickets/hb-xxxx.md`
  - in all three, HEAD did not move and no backup ref was made
- **Ordinary work:** no. The vendored `tk` writes the file, prints only the id, and cannot fail after writing.
- **Consequence:** other. The next A0 refuses `TREE_NOT_CLEAN` and names the file.
- **What would be right:** on any `tk` failure, A0 removes the files `tk` added and refuses with its own code; it never ends in a traceback.
- **What would reverse this:** showing that the real `tk` can exit non-zero after writing.

**R1-4, non-blocking, in scope: I1.** `src/gov/adopt/stages.py:103-110`.
- **What happens:** `tk create` picks a random 4-character id and does not check for clashes. If the new id equals an existing ticket's id, `tk` overwrites that file and A0 commits the coordination ticket over it. The key then names the old ticket's id.
- **How I showed it:** a stand-in `tk` that reuses `DAEO-eng1`. A0 succeeded, `eng1 changed True`, and the result was committed.
- **Ordinary work:** no. The chance is about N in 1.68 million per adoption, where N is the number of tickets with the same prefix.
- **Consequence:** loses work. The overwritten ticket can be recovered from the backup ref.
- **What would be right:** A0 refuses (or retries) when the new id's file is already tracked at HEAD.
- **What would reverse this:** showing that `tk` refuses an id that already exists.

**R1-5, non-blocking, in scope: I2 (ii), "changes nothing else".** `src/gov/adopt/stages.py:76`, `:95`, `:110`.
- **What happens:** a roster with CRLF or lone-CR line ends is written back with LF on every line. The meaning, comments and order are kept.
- **How I showed it:** the roster `b'# c\r\na: 1\r\nb: 2\r\n'` became `b'# c\na: 1\nb: 2\ncoordination_ticket: har-ex4y\n'`.
- **Ordinary work:** no. With git's usual Windows setting (`core.autocrlf`) the repository already stores LF, so only the added line changes. It takes CRLF stored in the repository itself.
- **Consequence:** other.
- **What would be right:** keep the file's line ends as they are, and add the key line with the same line end.
- **What would reverse this:** a reading that line ends are not "something else".

**R1-6, non-blocking, out of scope: I1's effect on later stages.** `template/governance/project/path-map.yaml` and `src/gov/adopt/project.py:29`; neither is in the ticket's paths.
- **What happens:** in a freshly generated product, A0's `.tickets/<id>.md` is a file that no namespace of the template's path map holds. The guard before A6 refuses while any such file exists (CAP-06.c). W2-23 S5 gave A0's other set-up files a namespace so no later stage would refuse them; the coordination ticket has none.
- **How I showed it:** a fresh product with no `.tickets/`, then A0. The files no namespace holds afterwards include `.tickets/har-048a.md`. A1 and A2 still succeed.
- **Ordinary work:** yes, in every fresh adoption. But the template's map also leaves `.claude/**`, `AGENTS.md` and `CLAUDE.md` unheld, so the adopter has to extend the map anyway.
- **Consequence:** other. It fails closed at A6 and names the path.
- **What would be right:** the template's path map, or A0's set-up list, holds `.tickets/**`. This belongs to W2-88/W2-174 or the owner.
- **What would reverse this:** a template path map that already holds `.tickets/` at merge.

## Probes run
1. **I1, end to end:** product generated with copier and `rulesync generate`, committed, then A0.
   - A0 succeeded. Ticket `har-zkdo`, title exactly `harbour coordination`, `class: coordination`, `state_class: AUTHORITATIVE`.
   - The roster is `coordination_ticket: har-zkdo`.
   - The record keeps `baseline_commit`, `backup_ref`, `tree` and `set_up`, and adds `coordination_ticket`, `roster` and `coordination`.
   - A0's one commit holds exactly the ticket, the record and the roster (3 commits before, 4 after). The tree is clean and the backup ref exists.
2. **The hook's decisions (failure-2):** 35 sessions × 4 commands, 140 calls.
   - **Asked:** only the CTO (orchestrator on the coordination ticket), the same with whitespace around role and ticket, and the CTO's orchestrator subagent. `sudo` was denied for these (DEC-083).
   - **Refused (deny):**
     - every role (engineer, test designer, auditor, product-spec, research), on its own ticket and on the coordination ticket
     - an orchestrator on another ticket, by id and by WBS id
     - an orchestrator with no ticket, an empty ticket, or a ticket the product does not have
     - the ticket id in upper case, with `.md`, or given as the ticket's title
     - `Orchestrator` with a capital O
     - no role, empty role, `owner`, `ticket-lead`
     - general-purpose and Explore subagents, and worker subagents in the CTO's session
     - an orchestrator subagent inside an engineer's session
   - Nothing was let through.
3. **I2, roster variants:** 29 rosters.
   - The key by id, by WBS id, under a quoted key name, or with padded text: kept, nothing created.
   - No final newline, empty, comment only, anchors, `---` start, BOM, duplicate key, the key nested under another key, keep-chomped block scalar, indented last line, comment last with no newline: one line added, everything else kept byte for byte.
   - CRLF and lone CR: see R1-5.
   - Flow mapping, `...` end, several documents, tabs, a list, a scalar: left as they are, the record says so, the guard is closed.
   - A null, empty, integer, or missing-ticket key: left as it is, closed.
   - Duplicate `coordination_ticket` lines: A0 recorded the same value the guard reads.
   - In all 29, what A0 recorded never differs from what the guard reads.
   - I2 (iii), `tk` missing: success, no ticket, no key, and the record says so.
4. **A0's failure paths:** 6 `tk` stand-ins (R1-3, R1-4).
   - `tk` failing or printing nothing: refused, nothing written, no ref.
   - A0 run twice: no second ticket, the key kept, the tree clean.
   - A ticket with the same title already there: a second `harbour coordination` ticket is created. That is I1 as written, so I report no finding.
   - `.tickets/` in `.gitignore`: `ADOPT_GIT_FAILED`, the tree clean, no ref.
5. **success-2's words:** 7 configurations (no roster, no key, null, empty, naming no ticket, unparsable, list), each tried by a CTO guess and by an engineer, plus the adopted product without `tk`. Every one is refused, names `GOV_TICKET`, says how to set the key, keeps "Set the top-level key" and the ESCALATE tail, and never claims a key was set. The remaining wording problems are R1-1 and R1-2.
6. **No other change to the guard:** W2-110's acceptance suite, its unit tests and W2-113's unit tests: **252 passed**, 9 deselected.
7. **Scope:** `git diff --name-only 4ede6c3fee3d..6542b7ec525b` touches `stages.py`, `install.py` and `tests/unit/adopt/test_w2_113_coordination.py`, all inside `allowed_paths`, plus `tests/acceptance/W2-113/*`, which is the test designer's.

## The lead's known items
- **A key naming no existing ticket is left as it is.** This is within I1/I2: I2 (i) and (ii) do not cover this case, and leaving it never overwrites a value set by hand. It fails closed. Null, empty and integer values behave the same way.
- **A roster that is not a readable mapping, or cannot take one added line, is left as it is.** Within I2 (ii) and fails closed. I probed 8 forms.
- **`tk` present but failing makes A0 refuse and write nothing.** A0 itself writes nothing, makes no commit and no ref. Not true when `tk` wrote a file before failing (R1-3). It still fails closed.
- **A second A0 run creates no second ticket.** Confirmed.
- **Older suites red at A3:** I did not judge them. Their planted projects have no `tk` (`grep` finds no `bin/tk` in the W1-41, W2-23 or W2-05 support files), so A0's new code creates nothing there and cannot be what turns them red.
- **The W2-23 seventh hook:** not this ticket's doing; I did not judge it.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "R1-3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "R1-4", "scope": "in", "ordinary_work": "no", "consequence": "loses work"}, {"id": "R1-5", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "R1-6", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "R1-1", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "R1-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}]}
```

task: DAEO-g29a
decisions: DEC-971, DEC-982, DEC-1052, DEC-1156, DEC-1157, DEC-801, DEC-1010, DEC-1014
status: done — PASS, 0 blocking
work_completed: audit round 1 of head 6542b7ec525b: I1, I2, I3 and the four KPI lines probed against the code on planted products in my TMPDIR
files_changed: none
evidence: the probe outputs quoted above; W2-110 and W2-113 unit suites 252 passed; worktree `status --porcelain` empty
tests: W2-110 acceptance, `test_w2_110_cto_install.py` and `test_w2_113_coordination.py` through heavy_slot: 252 passed, 9 deselected. Probe suite: 6 probe tests, 208 probed calls
discoveries: F5's own case (PyYAML missing) still says "not set" (R1-1); the template's path map does not hold `.tickets/**` (R1-6)
risks: R1-4, a clash on the random id overwrites a committed ticket (rare; recoverable from the backup ref)
lessons: a KPI that cites an earlier finding (F5) should be probed in that finding's own case as well as the cases in its Verify
proposed_decisions: none; R1-6 is a row for W2-88/W2-174 or the owner
unresolved: none
recommended_next_action: land on the PASS; record R1-1 to R1-6 as rows (R1-2 and R1-3 fit a later hardening pass of the A0 refusal and the guard's words)
guard_refusals: none (the heavy-slot gate waited once for a free slot, then ran; its wait-log write hit a read-only file system. Neither was a guard refusal)