# Brief: independent test designer, W2-183 (DAEO-href), run 3: revise one W2-54 case to the decided cap

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-href (W2-183), profile STANDARD, class C2.
Headless: only your last message is read. You revise ONE existing acceptance case to a decided behaviour (a decided-behaviour test revision, DEC-1156 (7)); you write nothing else.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-183-tests |
| branch | w2/W2-183-tests (base da3edd181: the ticket's built code, merged with w2/integrate) |
| your one allowed path | tests/acceptance/W2-54/test_w2_54_dropped_order.py (nothing else: not w2_54_support.py, not the W2-54 README, not tests/acceptance/W2-183/) |
| your scratch | /home/usain/gov-os-worktrees/W2-183-tests/.gov-runtime/scratch/ |
| your context packet (gov context output, JSON: the ticket text, KPIs, sources) | /home/usain/gov-os-worktrees/W2-183-tests/.gov-runtime/scratch/brief/td-context.md |
| the ticket (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-href.md |
| the decision register (grep by id only: DEC-1165, DEC-1156, DEC-860; CAP-15.d is in docs/contract/) | /home/usain/gov-os-worktrees/W2-183-tests/docs/DECISION_REGISTER.md |

## The decided behaviour (DEC-1165 (2), the ticket's S2)
S2: gov context's supplementary block holds at most 6,000 tokens whatever --budget is passed (its room is the smaller of the budget less the mandatory part, and 6,000); the close's packet is capped the same way [DEC-1165 (2), DEC-860].
The interface: `gov.context.SUPPLEMENTARY_CAP = 6000` (src/gov/context/__init__.py:23); the supplementary search's room is `min(limit - mandatory_tokens, SUPPLEMENTARY_CAP)`. The mandatory part is never shortened (S3, CAP-15.d).

## The case to revise
`tests/acceptance/W2-54/test_w2_54_dropped_order.py:172`, `test_a_ticket_whose_items_fit_keeps_every_item_and_drops_nothing`. It runs `gov context` for TK-W254-SMALL with `--budget S.room_for_all(...)` (`w2_54_support.py:613`: the fixed part plus four times the text of every file), and asserts nothing dropped, nothing left for a further batch, every item read stacked once in order, and the last batch read fewer items than its limit.
Its premise (a `--budget` holds every item of the evidence) can no longer be reached through `--budget` once the evidence passes 6,000 tokens: on this branch's head the case is red, with CHARTER-W254-BIG dropped "budget exceeded". The cap is applied as S2 decides (the STANDARD review agreed: docs/probes/DAEO-href/PR-DAEO-href.md); the case, not the code, is revised. Do not change src/.

The CTO's decision (P-W2-183-1 (a), recorded in the ticket's body): the case's "room for all" becomes `min(room_for_all, mandatory + SUPPLEMENTARY_CAP)`, **or** its stand-in's evidence stays under 6,000 tokens. You pick the form that keeps the case's point: **a ticket whose items fit keeps every item and drops nothing.** Note that capping the budget alone does not make the evidence fit if the evidence itself passes 6,000 tokens; work out from the packet's own figures which form actually keeps the point, and say in your return why you chose it. If you need a smaller stand-in, build it inside the test file (from the support module's builders, e.g. `S.order_project` with a corpus you derive), never by editing w2_54_support.py. The other cases that use `room_for_all` (`:210`, `:233`, `pressure_budget` at support `:637`) are green on the head; leave them alone.

## Rules for the revision
- Lower nothing: every assertion the case makes today stays, at the same strength (nothing dropped, nothing further, each item read stacked once in order, the evidence ended). You may add an assertion (for example, that the stand-in's evidence really fits under the cap, so the premise is checked, not assumed).
- Add no mark (no skip, xfail, flaky, rerun, local_only).
- Add `Rewrite-Reason: DEC-1165 (2)` to the case's docstring with one sentence of why (the file's existing form: see its module docstring and `test_an_empty_retrieval_result_gives_one_packet`), and the same as a commit trailer.
- It must pass on this head and **fail on a planted break: an item dropped while it fits.** Prove it in a throwaway copy of `src/gov` under your scratch (its parent first on PYTHONPATH; never edit `src/` in your tree, never commit it): plant the smallest break that drops one item although the room holds it (e.g. the room computed as one token less than the items need, or the last fitting item skipped), run the case, record the plant, the command and the failing assertion line. A second plant worth recording: the cap removed (room `limit - mandatory` only) and your case still green, or not, and why (it shows whether the case depends on the cap). Delete the copy afterwards.

## How you run tests
Every pytest through the heavy slot, TMPDIR outside the repository and outside ~/gov-os-runs (in the sandbox: your sandbox's own `$TMPDIR`). gitleaks must be on PATH (/home/usain/.local/bin).
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-183-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-183-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-54/test_w2_54_dropped_order.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
(keep `TMPDIR` set to your sandbox's `$TMPDIR`; PYTHONPATH must be absolute; make the empty-home folder first). Run the whole file once at the end: every case green. If another case turns red, name it with file:line and leave it. A resource gate's refusal is a wait, not a refusal: wait and retry. Never a hand-written sleep loop.

## Searching
No `gov retrieve` and no `gov context` in the sandbox: use the Read and Grep tools; if the first search does not answer, search again once in different words; then answer from both with path and lines, or say "not found". Reads are open, except: secrets, the held-out qualification material's contents, the evaluation sets' root and any hidden or memory-verdict folder (never open them).

## Forms that work
Write and edit with the Write and Edit tools and absolute paths. Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-183-tests/.gov-runtime/scratch/, run with `bash <file>` or `python3 <file>`. Literal paths only as write targets. Refused twice for the same call by the guard, sandbox or a hook: stop and say so; never work around a refusal. No merge, no push.

## Commit (your one path only; one commit)
```
git -C /home/usain/gov-os-worktrees/W2-183-tests commit -m "W2-183: <subject>" --trailer "Task: DAEO-href" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1165" --trailer "Rewrite-Reason: DEC-1165 (2)" -- tests/acceptance/W2-54/test_w2_54_dropped_order.py
```
`Implements:` only ids from the ticket's sources (DEC-1165, DEC-1027, DEC-860, CAP-15.d). Never `Role: owner` or `Decided-by:`. Before you return, `git -C /home/usain/gov-os-worktrees/W2-183-tests status --short` must be empty for tracked files, and `git -C /home/usain/gov-os-worktrees/W2-183-tests diff da3edd181 --stat` must name only tests/acceptance/W2-54/test_w2_54_dropped_order.py.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: (DONE or PACKAGES or ESCALATION) / work_completed: / files_changed: / evidence: (the form chosen and why, with the packet's figures: fixed part, evidence tokens, budget used; the file's run on the head with counts; each planted break: plant, command, failing line) / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; guard_refusals: none or a line each.
