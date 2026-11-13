Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-88a/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief rv-1: independent review of DAEO-pg6i (W2-88a), profile STANDARD, class C2

You are the independent auditor for ticket DAEO-pg6i (W2-88a: the adopt skill's kernel text). You are a fresh,
read-only session: you change no file in the tree and make no commit. Your verdict (PASS or FAIL, with findings) is the
independent review that the change's CIT-P record (CAP-33) carries before the owner approves the skill's bytes.

## What to review
| what | where |
|---|---|
| the tree (read only) | /home/usain/gov-os-worktrees/W2-88a, branch w2/W2-88a |
| the head to probe | `ba400b94e738` (text commit `f1ae5fecbc52`, record commit `ba400b94e738`); the ticket's base `ba27e4c0d` |
| the ticket (its three success lines, non-goals, sources) | /home/usain/gov-os-worktrees/W2-88a/.tickets/DAEO-pg6i.md |
| the parents the lines moved from | .tickets/DAEO-2bdu.md (W2-88: S10 to S16, cited by S17), .tickets/DAEO-zmo4.md (W2-174: the pass, its Approach and Interface) |
| the changed files | template/governance/kernel/skills/adopt/SKILL.md, template/.rulesync/skills/adopt/SKILL.md, .rulesync/skills/adopt/SKILL.md, docs/research/W2-88-memory-practice.md (§6), docs/changes/W2-88a-CIT-P.md |
| the acceptance tests (written before the text by the independent test designer) | tests/acceptance/W2-88a/ (README.md states the readings) |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1150, DEC-996, DEC-995, DEC-1098, DEC-1130, CAP-33; also DEC-1071, DEC-1072, DEC-1074 (4), DEC-1083, DEC-1116, DEC-1050 cited by the text |

`git diff ba27e4c0d ba400b94e738` shows the whole change.

## Check, and say for each what you found, with path and line
1. **S1 (W2-88's S17):** A9's section in the kernel skill states the seven steps in the KPI's order and points to the
   practice record; each step is faithful to the decisions it cites (DEC-1098 (1), DEC-1072 (2), DEC-1071 (1)-(3),
   DEC-1074 (4)) and to W2-88's S10 to S14 it renders. Look in particular at: step 3's gloss of "the standard" and "its
   refresh"; step 4's "both held outside every worktree" (the worker flagged that S13 may say this of the verdict set
   only); step 6's added sentence. Nothing in the skill contradicts itself (the Wave 3 paragraph now says "the full A9").
2. **S2 (W2-174's S5):** the section `Verify clauses for adopted tickets` states the four things (when; who; what checks:
   the tool, the test designer, the auditor's sample; the owner approves the rule once), faithful to DEC-1130 and
   DEC-1083 and to W2-174's Approach and Interface. W2-174's code is not built: judge whether the tool paragraph
   describes it accurately, and whether describing a not-yet-built option in a kernel skill is acceptable or a finding.
   Check each cited decision (including DEC-1050) supports the sentence it is cited on.
3. **S3 (the CIT-P record):** the before sha256 equals `git show ba27e4c0d:template/governance/kernel/skills/adopt/SKILL.md | sha256sum`;
   the after sha256 equals the committed kernel skill; the stated line counts equal `git diff --numstat`; the added lines
   listed are the diff's; the three copies are byte-equal; a place for the owner's approval of the bytes exists.
   (The record's review section says PENDING: that is expected; the lead writes your verdict into it after you return.)
4. **The practice record §6** is refreshed to the same seven steps in the same order and nothing else in the record changed.
5. **Scope:** only the five allowed paths changed in the two commits (`git diff --stat ba27e4c0d..ba400b94e738` beside
   the merged tests commit `1b8595b2b973`); commit trailers `Task: DAEO-pg6i`, `Role: product-spec`, `Implements:` only
   ids from the ticket's `sources:`.
6. **The tests:** run the acceptance folder and the skills check yourself (commands below); report the counts. One case
   is red by design until your verdict is recorded:
   `test_w2_88a_citp_and_copies.py::test_s3_the_record_gives_the_independent_review_with_its_pass_verdict`.
   Also probe the tests' strength on the text where useful (a copy in your TMPDIR, never in the tree).

## Rules
- Read only. Probes and copies go in your own TMPDIR (the sandbox's; `echo "$TMPDIR"` first), never in the tree
  (DEC-1144 (7)).
- **Every pytest through the heavy-slot gate**, with an empty HOME:
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-88a/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88a/src python3 -m pytest tests/acceptance/W2-88a -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  Run it alone (no pipe, no compound command). A heavy-slot or resource refusal is a wait: run again when it opens.
- The skills check: `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-88a/src python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt`
- Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
  then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE or ESCALATION) / work_completed /
files_changed (none) / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then a fenced verdict block, exactly:
```
verdict: PASS | FAIL
head: ba400b94e738
findings: <n>
```
then `findings:` (each: id, severity blocking or non-blocking, path:line, what, why, the fix as a described behaviour),
and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
