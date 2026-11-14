Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-183/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: independent auditor, W2-183 (DAEO-href), a narrow independent check of one test revision

You are a fresh independent auditor (role independent-auditor), ticket DAEO-href (W2-183), profile STANDARD, class C2.
Headless and read-only: you write nothing (no file, no commit); only your last message is read. You check exactly one decided-behaviour test revision (DEC-1156 (7)) and return a structured verdict.

## What you check
| what | value |
|---|---|
| the tree (read only) | /home/usain/gov-os-worktrees/W2-183 |
| the head to probe | 8b0056d78370 (branch w2/W2-183; `git -C /home/usain/gov-os-worktrees/W2-183 rev-parse HEAD` must start with it) |
| the revision | commit b2b0c4ed94b9 (independent test designer, session 4c28878e-4aa4-4e68-addb-9e4e7d7c6776), merged in 8b0056d78370; the diff: `git -C /home/usain/gov-os-worktrees/W2-183 diff da3edd181 8b0056d78370` (one file: tests/acceptance/W2-54/test_w2_54_dropped_order.py) |
| the case | `test_a_ticket_whose_items_fit_keeps_every_item_and_drops_nothing` (now near :188), with its new `fits` fixture and `_fitting_files()` |
| the support module (unchanged) | tests/acceptance/W2-54/w2_54_support.py (`room_for_all` :613, `tied_corpus`, `order_project`, `fixed_part`) |
| the ticket (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-href.md |
| the decision register (grep by id only: DEC-1165, DEC-1156, DEC-860) | /home/usain/gov-os-worktrees/W2-183/docs/DECISION_REGISTER.md |
| the STANDARD review's record (round 1, pass at e0c076514c9d) | /home/usain/gov-os-worktrees/W2-183/docs/probes/DAEO-href/PR-DAEO-href.md |

## Why the case was revised
The ticket's S2: gov context's supplementary block holds at most 6,000 tokens whatever --budget is passed (its room is the smaller of the budget less the mandatory part, and 6,000); the close's packet is capped the same way [DEC-1165 (2), DEC-860]. The code (`SUPPLEMENTARY_CAP = 6000`, room `min(limit - mandatory_tokens, SUPPLEMENTARY_CAP)`, src/gov/context/__init__.py:23 and :389) passed the STANDARD review at e0c076514c9d; nothing in src/ has changed since (`git diff --stat e0c076514c9d 8b0056d78370 -- src` is empty).
The old case gave TK-W254-SMALL a `--budget` with "room for every item of its evidence" (`room_for_all`) in the shared `tied` project and asserted nothing dropped. Under the cap it went red: an item past 6,000 tokens (CHARTER-W254-BIG) was dropped "budget exceeded". The CTO's decision (P-W2-183-1 (a), in the ticket's body): the case's "room for all" becomes `min(room_for_all, mandatory + SUPPLEMENTARY_CAP)`, or its stand-in's evidence stays under 6,000 tokens; the test designer picks the form that keeps the case's point (a ticket whose items fit keeps every item and drops nothing); it must still fail on a planted break (an item dropped while it fits); lower nothing; add no mark; `Rewrite-Reason: DEC-1165 (2)`.
The designer chose the second form: a project without `docs/charter/big.md` (its files about 4,786 tokens; the packet's fixed part 177, evidence 4,449 tokens in 37 items), with the old budget form, the four old assertions and a new premise assertion (the files total at most 6,000). The designer reports: plant A (the last fitting item skipped, in retrieval/supplementary.py) and plant B (the room one token short of the items) each fail the case at :201; plant C (the cap removed) leaves it green, because its evidence fits anyway.

## What to judge (narrow: this revision only)
1. Does the revised case keep its point: a ticket whose items fit keeps every item and drops nothing? Are all four old assertions kept at the same strength (nothing dropped, nothing further, every item read stacked once in order, the last batch under its limit)? Is anything lowered, weakened or skipped, any mark added?
2. Is the premise real: does the stand-in's evidence actually fit under the cap (the new assertion counts the files' tokens with the support module's `tokens`; is that the same measure the packet uses, and does it bound what the batches read)? Could the case pass vacuously (no items read, an empty project, an empty `read`)?
3. Does it catch a planted break: an item dropped while it fits? Check it yourself if you can in proportion: `w2_54_support.py` fixes `SRC` from its own `__file__`, so a PYTHONPATH copy of src/gov is ignored; a plant needs a mirror of the root (src/gov, the W2-54 folder, the conftests, pyproject.toml, path-map.yaml, .gitleaks.toml) under your sandbox's own `$TMPDIR`. Never edit the tree.
4. Is the chosen form within the CTO's decision, and is the `Rewrite-Reason: DEC-1165 (2)` in the docstring and the commit's trailer? Does the revision touch only its one allowed path?
5. Does the rest of the file still pass on the head (the lead's run of the W2-54 folder: 66 passed, 1 failed, the failure in `test_w2_54_audit_report.py:231`, core-schema on `docs/changes/W2-98-CIT-P.md`'s frontmatter, which came with w2/integrate and is not this revision's)?

For the verdict block: S2 is judged on this revision. S1, S3 and F1 were judged pass at e0c076514c9d; confirm no file of theirs changed since (`git diff --stat e0c076514c9d 8b0056d78370 -- src tests/acceptance/W2-183 tests/unit/close tests/unit/context governance/project/facts.yaml`) and, if so, carry them as pass with no new finding; otherwise judge what changed.

## How you run tests
Every pytest through the heavy slot, with your sandbox's own `$TMPDIR` (the sandbox's /tmp is read-only; use no other temporary folder), an empty HOME inside that `$TMPDIR`, PYTHONPATH absolute, gitleaks on PATH:
```
env TMPDIR="$TMPDIR" PATH=/home/usain/.local/bin:$PATH PYTHONUSERBASE=/home/usain/.local HOME="$TMPDIR/empty-home" PYTHONPATH=/home/usain/gov-os-worktrees/W2-183/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <FILE_OR_NODE> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Set PYTHONDONTWRITEBYTECODE=1 so nothing is written into the tree. A resource gate's refusal is a wait, not a refusal: wait and retry. Never a hand-written sleep loop.

## Searching
No `gov retrieve` and no `gov context` in the sandbox: use the Read and Grep tools; if the first search does not answer, search again once in different words; then answer from both with path and lines, or say "not found". Reads are open, except: secrets, the held-out qualification material's contents, the evaluation sets' root and any hidden or memory-verdict folder (never open them). Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal, not by another tool or form.

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.


## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: (DONE) / work_completed: / files_changed: none / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then each finding (N1, N2, ...) with its file:line, what it is, `Ordinary work: yes|no, because ...` and `Consequence: fails open|loses work|other`, and scope in or out.
Then your judgement in one line (pass or fail), and the fenced verdict block, exactly this form (one entry per line S1, S2, S3, F1):
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "N1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
Then: guard_refusals: none or a line each.
