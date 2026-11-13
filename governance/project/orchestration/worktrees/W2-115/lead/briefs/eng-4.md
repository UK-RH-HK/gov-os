# Brief: engineer, DAEO-emq1 (W2-115), FULL, class C3 — review round 1's fix round: F-1, F-3, F-7 (run 4, eng-4)

Budget: projection 8 USD. Keep your context short: read only what each finding needs; cut long outputs to head and tail.

You are a fresh engineer for ticket DAEO-emq1 (W2-115), in `/home/usain/gov-os-worktrees/W2-115` on `w2/W2-115`
(DEC-963), head 1a3664a20 (w2/integrate merged). Step 0 (the sandbox check), every standing rule, the writes (the
ticket's `allowed_paths:` only), the never-read rule for `tests/acceptance/W2-115/**`, the Interface, the commands,
the commit form and the return are those of the first engineer's brief, copied beside this one:
`/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/eng-1.md` (read it whole), and the lead's answers in
`eng-2.md` beside it (binding). Do step 0 first and report it first. `gov accept` crashes in the sandbox: do not run
it; the lead runs it outside. The ticket's line "PK-3 (a)" (near its end) is the decision you build.

**Every pytest run goes through the heavy-job slot**, with a TMPDIR outside the repository and outside
`~/gov-os-runs` (your sandbox TMPDIR is fine), `PYTHONUSERBASE=/home/usain/.local`, an empty `HOME`,
`-p no:cacheprovider -o tmp_path_retention_policy=failed`:

    env HOME=/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-115/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <files> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"

If the slot script is refused by the sandbox, say so and run the same line without it, once. A session refused twice
for an action stops and says so; it never reaches the same effect by another command, form or file (DEC-1142 (9)).

The round-1 probe record, with the reviewer's findings verbatim:
`/home/usain/gov-os-worktrees/W2-115/docs/probes/DAEO-emq1/PR-DAEO-emq1-round-1.md` (read F-1, F-3, F-7; F-2, F-4,
F-5, F-6, F-8, F-9 are not yours this round: do not change their behaviour).

## F-1 (S4, F1, blocking, fails open): a red the change caused is never excused

The base a red is judged against ("the head without the change") must be **the green base** (`chosen["green_base"]`,
the newest green record the selection counts the change from, `select.py` ~749) **when it is an ancestor of HEAD**;
otherwise **the parent of the ticket's oldest own commit** (today's rule, `select.py` ~529-538 `ticket_change`, used at
`command.py` ~1815) (DEC-988 item 3, DEC-989). Today a commit between the green base and the first `Task:`-trailered
commit (e.g. an untrailered slip that breaks a test) is counted in the change but sits in the base, so its red is
judged unowned and the close exits 0. After the fix that close refuses with `RED_CAUSED`, the record marks the red as
caused and no repair ticket is opened for it. A red the base already has with the same failure type stays unowned (S4,
S5 unchanged). The selection (S2, S3: `--select`, `--verify` and the close share one code path) must not change. Add
unit tests for: the green base an ancestor (the slip's red is caused), the green base not an ancestor (fallback to the
parent of the oldest own commit), and no green base.

## F-3 (S6, F3): a culprit whose red is its own new test is blamed once confirmed alone

`batch.py` ~588: when a candidate's red is a test that candidate itself adds, the build without that candidate has no
such test (absent), so no candidate "explains" it and the batch refuses `BATCH_UNEXPLAINED`. Instead: a red absent in
the build without candidate X, and red again in the base plus X alone (confirmed once, alone), blames X; X goes back
and the others land on the same run (as `close_build.py` does: it blames an absent case once confirmed with that
candidate alone). If it is not red with X alone (it fails only together with another candidate), no single candidate
explains it and the batch refuses as today. Nothing lands before the culprit is found; the existing S6 refusals
(unexplained, cannot be isolated) are unchanged. Add unit tests for both cases.

## F-7 (S9): the research document states its method honestly

`docs/research/W2-115-smart-close.md` (~line 36): "this close's verdict" was computed by feeding `close_build.py`'s
recorded alone-runs into `judge()`, not by running this close; failure types were not compared; the script (`s9.py`)
is not committed. Your only allowed path there is the `.md`: state the method exactly as it was (what was run, what
was computed from records, what was not compared and why), and put the script that computed the table inline in the
document (a fenced block) so it can be re-run; re-run it to confirm the table still holds at this head, and say so.
Keep the three-batch table (S9's check reads it) with its verdict columns.

## Done

Your unit tests, `tests/unit/close/`, and the strict suites eng-1.md names (F4) pass in your runs; commit each fix
with eng-1.md's form (one commit per finding is fine); return as eng-1.md says, `status` DONE when the three are fixed.
The lead merges the independent designer's new acceptance cases after you return and runs them.
