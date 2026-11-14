# Brief: independent test designer, W2-130 (DAEO-q8cl): pin run 3 (the two S4 cases still reading HEAD pinned; variant_findings runs the pinned tree's own gov links)

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-q8cl (W2-130), profile
STANDARD, class C2. Headless: only your last message is read. You work in the tests worktree and make ONE commit there;
the lead merges it. Every pytest goes through heavy_slot.sh (below). Your scratch is your sandbox's own `$TMPDIR`.

## Where things are
| what | path |
|---|---|
| your worktree (write here only) / branch | /home/usain/gov-os-worktrees/W2-130-tests / w2/W2-130-tests (at aafaf6259d10) |
| the ticket (KPI lines S3, S4, F3 and their Verify clauses) | `.tickets/DAEO-q8cl.md` |
| your context packet (the ticket and its authority, built by `gov context` outside the sandbox) | /home/usain/gov-os-worktrees/W2-130-tests/.gov-runtime/scratch/context-td.md |
| pin runs 1 and 2 (read their bodies first: what was pinned and how) | `git show 35b6ac6ba`, `git show 6a0b84a81`, `git show ed0e54dfe` |
| pin run 2's narrow check (its F1 and F2 are what this run answers) | `docs/probes/DAEO-q8cl/PR-DAEO-q8cl-pin2.md` |
| W2-130's record (read only; never edited) | `docs/research/W2-130-link-cleanup.md`: blocks `w2-130:counts-after` (its `measured_at`), `w2-130:closed-missing`, `w2-130:no-record` |

## Your paths (only these files change)
`tests/acceptance/W2-130/test_w2_130_sources.py`, `tests/acceptance/W2-130/conftest.py`,
`tests/acceptance/W2-130/test_w2_130_audit.py` (its docstrings), `tests/acceptance/W2-130/README.md` (only the
"HEAD's tool" wording near line 61, and any other line that says a case now pinned reads HEAD), and only if needed
`tests/acceptance/W2-130/w2_130_support.py`. No record, ticket, register, source or other test file changes. The
README's map rows (node ids) are not edited.

## The decided behaviour (the CTO, under DEC-1164 (18) and DEC-1156 (7); listed for the owner's reading)
- **P-W2-130-PIN2-HEAD (a):** the two S4 cases that still read HEAD are pinned at the record's
  `counts-after.measured_at`, with the pinned tree's own `gov links`, as S4's other three already are:
  - `test_w2_130_sources.py::test_s4_closed_missing_lists_per_closed_ticket_the_ids_its_sources_lack`
  - `test_w2_130_sources.py::test_s4_no_record_lists_per_ticket_ids_that_name_no_record`
  They now take `head_findings`/`head_tree`; instead they read the findings, the ticket statuses and files, and the
  register headings and ticket stems, all in the same `measured_at` clone, through the same `pinned_findings` and
  `s.measured_at(record)` route the other three S4 cases use (`_pinned(record, pinned_findings)`). W2-130 lands once,
  after this pass, so no case that a ticket event (a close, a reopen, a new id on a live ticket) can turn red reaches
  integrate.
- **Row F1 rides along:** `variant_findings` (conftest.py, used by the S3/F3 cases in `test_w2_130_audit.py`) runs the
  pinned tree's own tool too: `links_json(tree, home, src=support.pinned_src(tree))` on the variant clone (the commit's
  own tree with its appended marks taken off, so its `src` is the commit's own). Fix its docstring, the
  `test_w2_130_audit.py` module docstring ("HEAD's tool", line 6) and README line 61 ("HEAD's tool") to say "the
  commit's own tool (its tree's `src`)".
- After this run, the only cases left on the branch's tool are the HEAD-wide ones on `head_findings` (S2's "no
  UNMARKED_CHANGE but the 8 pairs", S6's no STATUS_CONFLICT, S7's no UNKNOWN_ID on a lesson). Leave them as they are,
  and name them in your commit body. If you find any other case that runs `gov links` at a fixed commit on the branch's
  tool, say so and pin it the same way; if you judge one should not be, say why.
- **Keep every case name the README map uses** (`gov accept` collects mapped node ids; no new unmapped case). Put a
  docstring on each revised case saying what tree and which tool it now reads, and that the name is kept for the README
  map (DEC-1156 (7), DEC-1164 (18) pin run 3).

## The lead's measurement (for your check, not instead of it)
With the cases' own counting (lead's probe `.gov-runtime/scratch/lead/run7/probe_pin3.py` in
/home/usain/gov-os-worktrees/W2-130; judge the tests, not the script): at `measured_at` 6b62de94e3fd, with the clone's
own `src`, `closed-missing` equals gov links' UNLINKED_ID on the tickets closed there (every listed ticket closed there,
none listing an id its `sources:` holds), and `no-record` has no problem and no unlisted (ticket, id). For each marks
commit (e12f8a30ca7d, c4420040f9b3, bce798c3a911), the variant tree's free-text pairs are the same under the branch's
tool and under the commit's own `src` (19, 8 and 6). So every case should stay green with the pinned tool.

## No case loses its point (show it)
In a scratch copy under `$TMPDIR` (a `git clone --shared` of your worktree with your change committed, records edited
in the copy only; never in your worktree):
1. `closed-missing`: drop one listed id from one ticket, and list one ticket that is not closed at `measured_at`: the
   case fails each time, naming it.
2. `no-record`: drop one listed (ticket, id), and add one id that names a register heading: the case fails each time.
3. Show the pin holds: in the copy, commit a reopen of a closed ticket listed in `closed-missing` and a new unknown id
   (e.g. DEC-99999) on an open ticket's `sources:` at the copy's HEAD (after `measured_at`): both pinned cases stay
   green (pin run 2's check turned them red this way).
4. Show the tool is pinned: put first on PYTHONPATH a copy of `src` whose `gov links` drops one UNLINKED_ID on a closed
   ticket, one UNKNOWN_ID on a ticket and one `text: true` flag: the two S4 cases and the F3/S3 cases stay green, while
   a HEAD-wide case (S2's) reads it.
Say what you planted and what failed in the commit body and in your return.

## Run
Run the changed test files, then both folders, each through heavy_slot.sh:
`env PYTHONUSERBASE=/home/usain/.local HOME=<an empty folder under $TMPDIR> PYTHONPATH=/home/usain/gov-os-worktrees/W2-130-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <file or folder> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
on `tests/acceptance/W2-130` and `tests/acceptance/W2-175`. Both folders must be green at your commit; report every red
with its message. Then `--collect-only -q` on `tests/acceptance/W2-130` and confirm every node id the README map names
collects (and that the `def test_*` names of every file are unchanged from aafaf6259d10). A resource gate's refusal is
a wait (relaunch when open). No merge, no `gov retrieve`, no `gov context` in the sandbox.

## Commit (one commit, your paths only, trailers in ONE final paragraph, no blank line inside it)
Write the message to a file under `$TMPDIR` and commit with `git -C /home/usain/gov-os-worktrees/W2-130-tests commit -F <file> -- <your changed paths>`.
Subject: `W2-130 (DAEO-q8cl) tests: pin run 3: S4's closed_missing and no_record at counts-after.measured_at; variant_findings runs the commit's own gov links`.
Body: what changed and why; **which cases now run the pinned tool** (by node id, and at which commit); which cases are
left on the branch's tool and why; the planted-value demonstrations. Final paragraph, exactly these lines:
```
Task: DAEO-q8cl
Role: independent-test-designer
Implements: DEC-1073, DEC-1010
Rewrite-Reason: DEC-1156 (7), DEC-1164 (18) (W2-130 pin run 3)
Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
```
(DEC-1156 and DEC-1164 are not in the ticket's sources:, so they go in Rewrite-Reason and your discoveries, not
Implements.)

## Return (your last message): the twelve fields, each a labelled line ("none" where nothing)
task: / status: (DONE, PACKAGES or ESCALATION) / work_completed: / files_changed: / evidence: (the commit hash in full,
both folders' pytest counts, the collect-only check, the planted-value failures) / tests: / discoveries: / risks: /
lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Report step 0's sandbox check first. Also say whether any W2-130 or W2-175 case still reads a value that a later ticket
event or approved change moves (W2-175's cases are in `tests/acceptance/W2-175/`; read, do not change them).

## Searching and refusals
Read and Grep, and git show/log; search once, then once more in other words; answer from what you read with path and
line, or say "not found". Never open the evaluation sets' root, held-out material or any hidden or memory-verdict
folder. Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a
refusal.
