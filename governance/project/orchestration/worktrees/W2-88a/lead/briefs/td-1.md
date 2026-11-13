# Brief td-1: independent test designer for DAEO-pg6i (W2-88a), profile STANDARD, class C2

You are the independent test designer (MR-3) for ticket DAEO-pg6i (W2-88a: the adopt skill's kernel text). You write
the acceptance tests from the ticket's three KPI lines (S1 = W2-88's S17, the Wave 0 order in A9's step; S2 = W2-174's
skill line, the section `Verify clauses for adopted tickets`; S3 = the CIT-P record), before the product-spec worker
writes the text. You write to the ticket; you never change it. A gap or a clash in it comes back as a package (status
PACKAGES: question, options with cost, recommendation, confidence, what it blocks), not as your own invention; a small
reading the ticket does not settle goes into the test's docstring and `unresolved`. You never read the product-spec
worker's work on this ticket (branch w2/W2-88a after this brief's base; there is none yet).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-88a-tests |
| branch | w2/W2-88a-tests (base `ba27e4c0d`) |
| your allowed paths | tests/acceptance/W2-88a/** |
| the ticket (read it first, whole) | /home/usain/gov-os-worktrees/W2-88a-tests/.tickets/DAEO-pg6i.md |
| the parents the lines moved from | .tickets/DAEO-2bdu.md (W2-88: S10 to S16, the S-numbers S17 cites; its last section), .tickets/DAEO-zmo4.md (W2-174: the pass, its Interface, its last section) |
| the skill today (three byte-equal copies at the base, sha256 `641a347b9b14101dde711f3550f087e714e404575f780be2a3cd91ff2925102d`, 51 lines, no A9 step and no Verify section) | template/governance/kernel/skills/adopt/SKILL.md, template/.rulesync/skills/adopt/SKILL.md, .rulesync/skills/adopt/SKILL.md |
| the practice record the A9 step must point to | docs/research/W2-88-memory-practice.md (§6 is the old order) |
| the skills check S1's Verify names | `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt` (src/gov/check/skill_validator.py: required front-matter fields, description at most 60 tokens, body at most 2500 tokens, gov-command references); judge it by exit code in a child process |
| earlier skill-text and CIT-P suites, for form | tests/acceptance/W2-62/ (test_w2_62_documents.py, README.md) |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1150, DEC-996, DEC-995, DEC-1098, DEC-1130, CAP-33; also DEC-1071, DEC-1072, DEC-1074 (4), DEC-1083, DEC-1116 named in the lines |
| the ticket's context packet (`gov context DAEO-pg6i --role independent-test-designer --budget 20000`, built by your lead) | /home/usain/gov-os-worktrees/W2-88a-tests/.gov-runtime/scratch/context/ctx-td.json |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## What to test (one test or more per line; name each after its id: `test_s1_...`, `test_s2_...`, `test_s3_...`)
- **S1 (the Wave 0 order, kernel copy):** find A9's step in `template/governance/kernel/skills/adopt/SKILL.md` and check
  that it states the seven steps in the ticket's order and points to `docs/research/W2-88-memory-practice.md`:
  1. assess and plan; 2. census the stated links and build the graph from them; 3. build the store with the standard
  (S10) and its refresh (S11); 4. have the verdict set and the tuning set written (S13, S12); 5. measure the tuning set
  and fix only the structure, never a named question, until its halves agree within 5 points; 6. declare and measure the
  verdict set once (S14); 7. record every method and figure.
  - Be tolerant of form, strict on content and order. The ticket does not say whether A9's step is a heading or a stage
    bullet: accept either (a heading naming A9, or a bullet led by A9 like the A0 to A8 bullets today), and take its
    text up to the next heading of the same or higher level or the next stage bullet; state your reading in the
    docstring. Build each step's matcher from the KPI line's own words (case-insensitive, whitespace-normalised), so any
    faithful rendering passes and a text that drops or reorders a step fails. The essential ones: step 5's "never a
    named question" (or the same meaning in the KPI's words) and "5 points"; step 6's "once"; the S-numbers if you
    judge them part of the line (say which you require).
  - Each failure message names the missing or out-of-order step, since the writer sees the failing output.
  - The skills check: the validator above exits 0 on the kernel adopt skill.
  - Not a KPI line, so no test: the practice record's §6 refreshed to the order (the reviewer checks it).
- **S2 (the Verify pass, three copies):** each of the three files carries a section headed
  `Verify clauses for adopted tickets` (the heading's level is not stated: accept `##` or `###`), and that section
  states the four things: when it runs (for a ticket about to launch, not for the whole tracker); who writes the clauses
  (a product-spec session); what checks them (the tool, the ticket's test designer, the auditor's sample: all three);
  and that the owner approves the rule once. The section's bytes are equal in the three files. Same tolerance rule:
  matchers from the KPI's words, failure messages naming the missing statement or the differing copy.
- **S3 (the CIT-P record and the copies):** `docs/changes/W2-88a-CIT-P.md` exists and holds: the kernel skill's sha256
  before (equal to `641a347b…102d`, the sha256 of `git show ba27e4c0d:template/governance/kernel/skills/adopt/SKILL.md`,
  a fixed commit) and after (a different 64-hex value equal to the kernel file's sha256 as committed; think about the
  suite staying green after the merge into w2/integrate and after a later ticket changes the skill, and state your
  choice); the lines added or removed (counts, or the diff: your reading, stated); the independent review with its
  verdict; and a place for the owner's approval of the bytes. The owner approves only after this run's review, so do not
  require the approval to be filled in; say so in `unresolved`. The copies: the two `.rulesync` files equal the kernel
  copy in the changed sections (simplest strong form: the three files byte-equal; if you choose a weaker form, say why).
- Non-goals (no test): the adopt code (W2-88, W2-174), the proofs (W2-88b), `.claude/skills/adopt/SKILL.md` (the copies
  ACT after the owner's approval).

## Rules
- Tests read files and run `git` and the validator in child processes; no network, no model, never the store. Locate
  the repository from `Path(__file__)` (parents[3]); give every child this tree's `src/` first on `PYTHONPATH`.
- Tests are red now (no A9 step, no Verify section, no CIT-P record). Run them and say which are red and why; anything
  green now is a fault in the test unless it guards something that already holds (say which).
- No test named with `real`, `green_here` or `time_limit`. Keep the folder to seconds.
- **Every pytest through the heavy-slot gate**, TMPDIR outside the repository and outside ~/gov-os-runs (make the TMPDIR
  and empty HOME folders first with `mkdir -p`):
  `TMPDIR=/tmp/gov-w2-88a-td bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-88a-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88a-tests/src python3 -m pytest tests/acceptance/W2-88a -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  A heavy-slot or resource refusal is a wait: run again when it opens.
- Add `tests/acceptance/W2-88a/README.md`: how the tests reach the files, each KPI's cases, your readings.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-88a-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-pg6i" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1150, DEC-996, DEC-995, DEC-1098, DEC-1130, CAP-33" -- tests/acceptance/W2-88a`
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line, red and green counts per KPI) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers), `readings:` (each reading you chose where the ticket is silent: A9's step's form, the S-numbers,
the after hash, the lines added or removed, the copies' form) and `guard_refusals:` (none, or each: time | form | the
hook's reason | true or false-positive).
