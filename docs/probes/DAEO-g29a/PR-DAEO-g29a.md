---
type: probe
task: DAEO-g29a
reviewer_session: 33fd2ff1-6a73-4688-b0f3-cc3159e02dd9
implementer_session: 92fd41d1-9a32-49ec-9c4a-4b97e78286e3
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 6542b7ec525b47b84ff6008a00d6e3236192db32
decisions_applied: [DEC-971, DEC-957, DEC-982, DEC-1052, DEC-1156, DEC-1157, DEC-1010]
---

# Probe record: W2-113 (DAEO-g29a)

```verdict
ticket: DAEO-g29a
head: 6542b7ec525b
round: 1
verdict: PASS
blocking: 0
```

- **What was probed:** Stage A0's new coordination ticket and roster key, and the guard's install refusal when the
  rule cannot run, at 6542b7ec525b (code of a322b1f94, the engineer's commit). The reviewer was an independent
  auditor (Opus, read-only), and ran everything as code on planted products in its own TMPDIR, using this worktree's
  `src`:
  - I1 end to end: a product generated with copier and `rulesync generate`, committed, then `gov adopt --lite --stage A0`.
  - The hook's decisions: 35 session forms × 4 commands, 140 calls.
  - 29 roster variants for I2 (i)/(ii) and I2 (iii) (`tk` missing).
  - 6 `tk` stand-ins for A0's failure paths, plus A0 run twice, a ticket with the same title already there, and `.tickets/` git-ignored.
  - success-2's words in 7 configurations, each tried by a CTO guess and by an engineer, plus the adopted product without `tk`.
  - W2-110's acceptance suite and unit tests with W2-113's unit tests (252 passed).
  - Scope: `git diff --name-only 4ede6c3fee3d..6542b7ec525b`.

  The reviewer wrote nothing to the repository. The worktree was clean at the start and at the end.
- **What it found:**
  - **R1-1, non-blocking, in scope (success-2, W2-110's F5).** `src/gov/guard/install.py:320-321`, `:336-343`.
    When the rule itself cannot run (PyYAML blocked, roster correct), the refusal still says the coordination ticket
    "is not set" and asks the CTO to set a key that is already set.
    Ordinary work: no, because the pinned interpreter ships PyYAML; W2-110's review judged it the same way.
    Consequence: other (it still refuses).
  - **R1-2, non-blocking, in scope (success-2, I2 (iii)).** `src/gov/guard/install.py:339-343`.
    With `tk` missing, A0 creates no ticket. The refusal tells the CTO to set the key to "the coordination ticket in
    .tickets/", which does not exist, and does not say to create one or to vendor `tk` and run A0 again. It does name
    `GOV_TICKET`, refuse, say how to set the key, and claim nothing false about a key.
    Ordinary work: yes, because I2 (iii) is a decided default.
    Consequence: other (the guard stays closed).
  - **R1-3, non-blocking, in scope (I1, A0's failure path).** `src/gov/adopt/stages.py:102-104`; `src/gov/tasks/tickets.py:28`, which is outside the ticket's paths.
    A `tk` that writes its file and then fails, or prints an extra line, leaves the file untracked in `.tickets/`
    (A0 refuses, HEAD unmoved, no ref). A ticket file with no closing `---` ends in an uncaught `ValueError` traceback.
    Ordinary work: no, because the vendored `tk` writes the file, prints only the id, and cannot fail after writing.
    Consequence: other (the next A0 refuses `TREE_NOT_CLEAN` and names the file).
  - **R1-4, non-blocking, in scope (I1).** `src/gov/adopt/stages.py:103-110`.
    `tk create`'s random 4-character id is not checked for a clash; on a clash A0 commits the coordination ticket over
    the existing ticket.
    Ordinary work: no, because the chance is about N in 1.68 million per adoption.
    Consequence: loses work (recoverable from A0's backup ref).
  - **R1-5, non-blocking, in scope (I2 (ii)).** `src/gov/adopt/stages.py:76`, `:95`, `:110`.
    A roster stored with CRLF or lone-CR line ends is written back with LF throughout. The meaning, comments and order
    are kept.
    Ordinary work: no, because it needs CRLF stored in the repository itself.
    Consequence: other.
  - **R1-6, non-blocking, out of scope (I1's effect on later stages).** `template/governance/project/path-map.yaml`, `src/gov/adopt/project.py:29`.
    The template's path map holds no namespace for `.tickets/**`, so A0's coordination ticket is an unheld file that
    the A6 guard refuses (CAP-06.c). The template also leaves `.claude/**`, `AGENTS.md` and `CLAUDE.md` unheld.
    Ordinary work: yes, in every fresh adoption.
    Consequence: other (it fails closed at A6 and names the path). This is a row for W2-88/W2-174 or the owner.
- **Sound:**
  - A0 on a fresh product creates the ticket with exactly the title `harbour coordination` (the folder's name),
    `class: coordination` and `state_class: AUTHORITATIVE`, and writes the roster `coordination_ticket: <id>`.
  - A0's record keeps `baseline_commit`, `backup_ref`, `tree` and `set_up`, and adds `coordination_ticket`, `roster`
    and `coordination`. All of it is in A0's one commit, the tree is clean after, and the backup ref exists.
  - Only the CTO is asked: the orchestrator on the coordination ticket, the same with whitespace around role and
    ticket, and its orchestrator subagent. Every other session form of the 35 is refused, and nothing is let through.
  - In all 29 roster variants, what A0 recorded equals what the guard reads. Rosters A0 cannot safely extend are left
    as they are, the record says so, and the guard stays closed.
  - With `tk` missing, A0 succeeds, creates no ticket and no key, and its record says so in words.
  - A0 run twice creates no second ticket.
  - In every configuration where the rule cannot run, the refusal names `GOV_TICKET`, says how to set the key, keeps
    "Set the top-level key" and the escalation tail, and never claims a key was set.
  - W2-110's guard behaviour is unchanged (252 passed).
  - The ticket's code changes stay inside `allowed_paths`.
- **The lead's known items, as the reviewer judged them:**
  - Leaving a key that names no ticket as it is, and leaving an unextendable roster as it is: within I1/I2, and both fail closed.
  - `tk` failing: A0 refuses and writes nothing itself; R1-3 covers the case where `tk` writes a file first.
  - A second A0 run: confirmed, no second ticket.
- **Lead's verification at this head:**
  - `gov accept W2-113`: 74 passed, 0 failed (success-1 30, success-2 44, failure-1 3, failure-2 14).
  - `lead_verify.sh`: 5609 tests with 1 failed, and the serial half 5/0. The one red is `tests/acceptance/W2-23/test_w2_23_space.py:99`, which pins six kernel hooks and finds `context_watch.py` (W2-176, c10be8fd0, already in the merge base 4ede6c3fee3d). It is red on the base and not this ticket's.
- **Verdict:** pass. No finding is blocking: none breaks a KPI or failure line, contradicts I1-I3, opens the guard, or
  claims a key was set. R1-1 to R1-5 go to a later hardening pass of A0's failure path and the guard's words. R1-2
  belongs with the owner's I2 (iii) default. R1-6 goes to W2-88/W2-174.
