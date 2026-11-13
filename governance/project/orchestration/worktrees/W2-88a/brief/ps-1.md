Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-88a/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief ps-1: product-spec worker for DAEO-pg6i (W2-88a), profile STANDARD, class C2

You are the product-spec worker for ticket DAEO-pg6i (W2-88a: the adopt skill's kernel text). You write the adopt skill's
new text in its three byte-equal copies, refresh the practice record's §6 to the same order, and write the CIT-P record.
The acceptance tests are written and merged (`tests/acceptance/W2-88a/`, 35 cases, 18 red on the base); you make them
green by writing the text, never by touching a test. You write to the ticket; you never change it. A gap or a clash in it
comes back as a package (status PACKAGES: question, options with cost, recommendation, confidence, what it blocks).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-88a |
| branch | w2/W2-88a (head `1b8595b2b973`; base of the ticket `ba27e4c0d`) |
| your allowed paths (nothing else) | template/governance/kernel/skills/adopt/SKILL.md, template/.rulesync/skills/adopt/SKILL.md, .rulesync/skills/adopt/SKILL.md, docs/research/W2-88-memory-practice.md, docs/changes/W2-88a-CIT-P.md |
| the ticket (read it first, whole) | /home/usain/gov-os-worktrees/W2-88a/.tickets/DAEO-pg6i.md |
| the parents the lines moved from | .tickets/DAEO-2bdu.md (W2-88: S10 to S16, which S17 cites), .tickets/DAEO-zmo4.md (W2-174: the pass, its Approach and Interface) |
| the acceptance tests and their readings (read the README first: it states exactly how each line is matched) | tests/acceptance/W2-88a/README.md, w2_88a_support.py |
| the practice record (§6 is the old order) | docs/research/W2-88-memory-practice.md |
| a CIT-P record for form | docs/changes/W2-146-CIT-P.md |
| the skills check | `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt` (src/gov/check/skill_validator.py: front matter, description at most 60 tokens, body at most 2500 tokens, `gov <command>` names must exist) |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1150, DEC-996, DEC-995, DEC-1098, DEC-1130, CAP-33; also DEC-1071, DEC-1072, DEC-1074 (4), DEC-1083, DEC-1116 named in the lines |
| the ticket's context packet (`gov context DAEO-pg6i --role product-spec --budget 20000`, built by your lead) | /home/usain/gov-os-worktrees/W2-88a/.gov-runtime/scratch/context/ctx-ps.json |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## What to write
1. **A9's step (S1, W2-88's S17), in the kernel skill.** A section whose heading names A9 (for example
   `## A9: Wave 0 memory practice`; a heading is safer than a bullet, since the Wave 3 paragraph's passing mention of A9
   is no step). It states the practice in this order, as a numbered list, one step per item, in the KPI line's own words:
   1. assess and plan; 2. census the stated links and build the graph from them; 3. build the store with the standard
   and its refresh; 4. have the verdict set and the tuning set written; 5. measure the tuning set and fix only the
   structure, never a named question, until its halves agree within 5 points; 6. declare and measure the verdict set
   once; 7. record every method and figure. It points to the practice record by its path
   `docs/research/W2-88-memory-practice.md`, inside the section. Keep each step's words inside its own list item (the
   matchers do not cross a full stop or a semicolon). The S-numbers (S10 to S14) are W2-88's KPI ids, which do not exist
   in an adopted repository: write the meaning, not the ids (the tests do not require them). Make the section consistent
   with the Wave 3 paragraph, which today says "A9 itself" is Wave 3 (adjust that sentence so the skill does not
   contradict itself; say what you chose in `work_completed`).
2. **The Verify pass (S2, W2-174's S5), in the three copies.** A section headed exactly
   `## Verify clauses for adopted tickets`, stating the four things in its own sentences: when the pass runs (for a
   ticket about to launch, not for the whole tracker); who writes the clauses (a product-spec session); what checks them
   (the tool, the ticket's test designer, and the auditor's sample: all three named); and that the owner approves the
   rule once. Take the tool's description from W2-174's Approach and Interface (the list, the check, the apply by
   editing the lines' text, the marker). W2-174's code is not built yet: if you name its flags, say in `unresolved` that
   they land with W2-174; never name a `gov` subcommand that does not exist (the skills check refuses it). Add the
   sources the new text cites to `## Governing sources`.
3. **The three copies byte-equal.** Write the kernel copy, then copy its bytes to `template/.rulesync/skills/adopt/SKILL.md`
   and `.rulesync/skills/adopt/SKILL.md` (`cmp` all three before you commit).
4. **The practice record's §6** (`docs/research/W2-88-memory-practice.md`, "For an adopted repository's Wave 0"):
   refresh it to the same seven steps in the same order (it may keep fuller wording and its notes, such as the model
   choice, as a note after the seven), so the skill and the record agree. Change nothing else in the record.
5. **Commit the text first**, the four files above in one commit (the after-hash is read from the latest commit after
   the base that changes the kernel skill and carries `Task: DAEO-pg6i`, so the skill must not change after the record).
6. **The CIT-P record** `docs/changes/W2-88a-CIT-P.md` (form: W2-146-CIT-P.md; front matter with `status: PROPOSED`,
   `task: DAEO-pg6i`, `state_class: EVIDENCE`), holding:
   - the kernel skill's sha256 **before**: `641a347b9b14101dde711f3550f087e714e404575f780be2a3cd91ff2925102d` (the base
     `ba27e4c0d`), on a line that says "before";
   - its sha256 **after**: `sha256sum` of the committed kernel skill, on a line that says "after";
   - the lines added and removed: the two numbers of `git diff --numstat ba27e4c0d <your text commit> -- template/governance/kernel/skills/adopt/SKILL.md`,
     written as "N lines added, M removed" and the `--numstat` row, and the added lines themselves in a fenced block;
   - the copies: the three files byte-equal, with their sha256;
   - the trigger table (the ticket's two moved lines and the CIT-P line, with their decisions);
   - an **independent review** section stating that the independent review is pending (`verdict: PENDING`; never write
     PASS: your lead records the reviewer's verdict after the review);
   - an **owner's approval** section: a line "Owner's approval of the skill's bytes (sha256 <after>): pending", to be
     filled by the owner before the merge (CAP-33).
   Commit the record alone in a second commit.

## Rules
- Never touch `tests/`, `.claude/`, the ticket or any path outside your five.
- **Every pytest through the heavy-slot gate**, with the sandbox's own TMPDIR (do not set TMPDIR to a folder of your
  choosing: the sandbox refused `/tmp/gov-w2-88a-td` in the tests run; `echo "$TMPDIR"` first and check it is outside the
  repository and outside ~/gov-os-runs), an empty HOME (make it first with `mkdir -p`):
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-88a/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88a/src python3 -m pytest tests/acceptance/W2-88a -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  A heavy-slot or resource refusal is a wait: run again when it opens.
- Expected at your end: 34 of 35 green; the one red is
  `test_w2_88a_citp_and_copies.py::test_s3_the_record_gives_the_independent_review_with_its_pass_verdict` (green only
  once the review's PASS is recorded by your lead). Anything else red is yours to fix.
- Run the skills check above (exit 0) and report its output line.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-88a/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-pg6i" --trailer "Role: product-spec" --trailer "Implements: DEC-1150, DEC-996, DEC-995, DEC-1098, DEC-1130, CAP-33" -- <your paths>`
  An id you need that is not in that list goes in `discoveries`, never in `Implements:`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line; the skills check's output; the before and after
sha256; `cmp` of the three copies; the numstat row) / tests / discoveries / risks / lessons / proposed_decisions /
unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each:
time | form | the hook's reason | true or false-positive).
