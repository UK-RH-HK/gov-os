# Brief: independent test designer, W2-130 (DAEO-q8cl): the pin run (two decided-behaviour test revisions)

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-q8cl (W2-130), profile
STANDARD, class C2. Headless: only your last message is read. You work in the tests worktree and make ONE commit there;
the lead merges it. Every pytest goes through heavy_slot.sh (below). Your scratch is your sandbox's own `$TMPDIR`.

## Where things are
| what | path |
|---|---|
| your worktree (write here only) / branch | /home/usain/gov-os-worktrees/W2-130-tests / w2/W2-130-tests (at f4511c723) |
| the ticket (KPI lines and Verify clauses; read its last paragraph, "Reopened 2026-11-14", first) | `.tickets/DAEO-q8cl.md` |
| your context packet (the ticket and its authority, built by `gov context` outside the sandbox) | /home/usain/gov-os-worktrees/W2-130-tests/.gov-runtime/scratch/context-td.md |
| the CTO's diagnosis of the reds (sections "1-2" and "3-4" only) | /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/nightly-20261114/DIAG.md |
| W2-130's record (read only; never edited) | `docs/research/W2-130-link-cleanup.md`, block ```` ```yaml w2-130:counts-after ```` near line 5473, and `w2-130:left` |
| W2-175's CIT-P record (read only; never edited) | `docs/changes/W2-175-CIT-P.md` |
| W2-175's ticket (its S7 Verify: "at the ticket's head") | `.tickets/DAEO-wahn.md` |

## Your paths (only these files change)
- `tests/acceptance/W2-130/test_w2_130_record.py` (and, only if a fixture is needed, `tests/acceptance/W2-130/conftest.py`)
- `tests/acceptance/W2-175/test_w2_175_record.py`, `tests/acceptance/W2-175/w2_175_support.py`
No record, ticket, register, source or other test file changes.

## The two revisions (decided by the CTO under DEC-1156 (7) and DEC-1164 (18))

### 1. W2-130 S8: two cases stop reading HEAD
`test_w2_130_record.py::test_s8_gov_links_at_head_gives_the_after_counts` and
`::test_s8_left_holds_d_5_d_6_and_d_9_by_path_and_role_as_gov_links_finds_them_at_head` run `gov links --all --json`
on a clone at HEAD (`head_findings`), so every ticket close or reopen after the land moves the counts (122 -> 124
CLOSED_TICKET_EDITED in five hours). The CTO's decided behaviour: both cases run `gov links` at a commit the record
pins, through the existing `clone_at` fixture, not at HEAD.

**Which pinned commit: the lead's measurement and decision.** The CTO's text names `counts-after.head` (57cbacfbf, the
last clean-up commit). The record's block also holds `measured_at: 6b62de94e3fd...`, and its `command` says the counts
are of the tree at 6b62de94e3fd ("'head' names the last clean-up commit and 'measured_at' the tree counted"). The ticket's
S8 Verify says "a re-run of gov links --all at the record's last commit gives the record's after counts"; the record's
last commit is a2671a340, whose parent is 6b62de94e and which changes only the record. The lead ran both, with the
cases' own counting:
- at 57cbacfbf: by_code differs (UNLINKED_ID record 1420, tool 1417; UNKNOWN_ID record 56, tool 57) and `left.D-9`
  differs on five ticket paths. So pinning to `counts-after.head` stays red with the record unedited.
- at 6b62de94e (`measured_at`): by_code, by_code_role, unlinked_by_status and left D-5, D-6, D-9 all equal the record.
So: **run `gov links` at the record's `counts-after.measured_at`** (the tree the record says it counted), and keep
`counts-after.head` == the last clean-up commit as the existing case `test_s8_counts_before_...` already asserts. Add,
in the revised cases, that `measured_at` is a full hash, is `counts-after.head` or a descendant of it, and is an
ancestor of HEAD (so the pinned tree is one this branch's history really holds). The UNLINKED_ID-by-status count reads
each ticket's status in the pinned tree (`_counts(findings, tree)` already takes the tree). Rename the two cases so
their names no longer say "at head" (e.g. `..._at_the_record_s_measured_tree_...`); keep `S8` in the name. If you find
a reason this choice is wrong, say so in your return rather than choosing silently.
**Unchanged:** the HEAD-wide "no UNMARKED_CHANGE but the 8 pairs" case (in another file) and every other case. Do not
remove the `head_findings`/`head_tree` fixtures: other files use them.

### 2. W2-175 S7: hash the templates at W2-175's landing, not the working tree
`tests/acceptance/W2-175/test_w2_175_record.py::test_s7_record_sha256_of_each_template_is_its_sha256_at_the_head`
(parametrised over `t.SEVEN`) hashes `t.path_of(stem)` in the working tree. An owner-approved change (b88a76172) moved
role-cto.md and role-lead.md after W2-175 closed. W2-175's Verify says "at the ticket's head". Decided behaviour: the
case reads each template at **W2-175's landing commit, 61cae50dc5b45e84145cc398f14ad7cd9ef7485b** (the merge
"Merge w2/W2-175 (DAEO-wahn) ...") through git, the way `test_s7_record_names_each_template_s_base_sha256` already
pins its base commits (`t.BASE`, `t.git_show`, `t.base_bytes`). Put the pinned landing commit as a named constant in
`w2_175_support.py` with a comment saying why (a closed ticket's head; later approved template changes must not turn
it red), and a helper reading a template's bytes at it. Assert the constant is an ancestor of HEAD. The lead checked:
each of the six non-test-designer templates' sha256 at 61cae50dc appears once in the record; check role-test-designer
yourself. The CIT-P record is not edited. Rename the case's "at_the_head" to say the landing (keep `s7`).

## No case loses its point (show it)
Each revised case must still fail on a record that disagrees with its pinned commit. Show it in a scratch copy under
`$TMPDIR` (never in the worktree): plant one wrong count in a copy of the W2-130 record's `counts-after` block (and one
wrong path count in `left`) and one wrong sha256 in a copy of the W2-175 record's role-lead row; run the revised cases
against the copies (e.g. by pointing the support module's record path at the copy through a monkeypatch in a throwaway
scratch test, or a scratch copy of the repository); each must fail, with the message naming the disagreement. Say
what you planted and what failed in the commit body and in your return.

## Run
Run the two changed files, then both folders, each through heavy_slot.sh:
`env PYTHONUSERBASE=/home/usain/.local HOME=<an empty folder under $TMPDIR> PYTHONPATH=/home/usain/gov-os-worktrees/W2-130-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <file or folder> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
Both folders must be green at your commit. A resource gate's refusal is a wait (relaunch when open). No merge, no
`gov retrieve`, no `gov context` in the sandbox.

## Commit (one commit, your paths only, trailers in ONE final paragraph, no blank line inside it)
Write the message to a file under `$TMPDIR` and commit with `git -C /home/usain/gov-os-worktrees/W2-130-tests commit -F <file> -- <your changed paths>`.
Subject: `W2-130 (DAEO-q8cl) tests: pin run: S8's two cases at the record's measured tree; W2-175 S7 at its landing 61cae50dc`.
Body: what changed and why; the planted-value demonstrations; the pinned-commit choice (measured_at, with the lead's
measurement). Final paragraph, exactly these lines:
```
Task: DAEO-q8cl
Role: independent-test-designer
Implements: DEC-1073, DEC-1010
Rewrite-Reason: DEC-1156 (7), DEC-1164 (18) (W2-130 pin run)
Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
```
(DEC-1156 and DEC-1164 are not in the ticket's sources:, so they go in Rewrite-Reason and your discoveries, not
Implements.)

## Return (your last message): the twelve fields, each a labelled line ("none" where nothing)
task: / status: (DONE, PACKAGES or ESCALATION) / work_completed: / files_changed: / evidence: (the commit hash in full,
the pytest counts of both folders, the planted-value failures) / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:
Report step 0's sandbox check first.

## Searching and refusals
Read and Grep, and git show/log; search once, then once more in other words; answer from what you read with path and
line, or say "not found". Never open the evaluation sets' root, held-out material or any hidden or memory-verdict
folder. Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a
refusal.
