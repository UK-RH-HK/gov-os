# Brief: independent test designer, W2-183 (DAEO-href), run 1: the acceptance tests

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-href (W2-183), profile STANDARD, class C2.
Headless: only your last message is read. You write the acceptance tests from the KPI lines below, before the implementation exists. Do not read or wait for any implementer's work on this ticket (there is none on your branch).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-183-tests |
| branch | w2/W2-183-tests (base d36c268c1) |
| your allowed paths | tests/acceptance/W2-183/** (nothing else) |
| your scratch | /home/usain/gov-os-worktrees/W2-183-tests/.gov-runtime/scratch/ |
| your context packet (gov context output, JSON: the ticket text, KPIs, sources) | /home/usain/gov-os-worktrees/W2-183-tests/.gov-runtime/scratch/brief/td-context.md |
| the ticket (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-href.md |
| the decision register (grep by id only: DEC-1165, DEC-1027, DEC-860; CAP-15.d is in docs/contract/) | /home/usain/gov-os-worktrees/W2-183-tests/docs/DECISION_REGISTER.md |

## The KPI lines (write each line's success and failure, plus the key edges)
| id | line | verify |
|---|---|---|
| S1 | gov close builds the ticket's context packet at the project's setting `budgets.close_context_tokens` in governance/project/facts.yaml (65536 in this repository), not at gov context's default of 6,000; with no setting, the default applies as today [DEC-1165 (1), DEC-1027 H] | in a stand-in repository, a ticket whose own text and mandatory inputs come to about 10,000 tokens passes the close's context step with the setting at 65536 and is refused CONTEXT_FAILED (context_error CONTEXT_OVER_CEILING) with the setting at 8000 or absent |
| S2 | gov context's supplementary block holds at most 6,000 tokens whatever --budget is passed (its room is the smaller of the budget less the mandatory part, and 6,000); the close's packet is capped the same way [DEC-1165 (2), DEC-860] | in a stand-in with a store large enough to fill it, `gov context <ticket> --budget 60000` gives a supplementary block of at most 6,000 tokens; the same with the close's setting at 65536 |
| S3 | the mandatory part is never shortened, and a packet whose budget leaves under 6,000 tokens of room is unchanged: the same items and the same hash as before the change [DEC-1165 (3), CAP-15.d] | a small stand-in ticket's packet at the default budget has the hash it had before the change; a ticket whose mandatory part passes its ceiling is still refused CONTEXT_OVER_CEILING, named |
| F1 | A setting that is not a positive whole number refuses by name (never a silent default, never a crash). | `budgets.close_context_tokens: 0`, `-5` and `"many"` each make the close's context step refuse with a named finding |

Non-goals (do not test): no trimming of a ticket's own text or sources; no change to gov check's context-reproducibility (`src/gov/context/context_check.py`), to the brief builder (`src/gov/brief/build.py`) or to the kernel's facts schema; no change to the default ceiling of 6,000 for `gov context` and briefs (a case that `gov context` with no `--budget` still refuses a ~10,000-token mandatory part at 6,000 is in scope as S1's "default as today" edge).

## The interface (stated at claim by the CTO; test against it, do not invent another)
- **The setting:** `budgets.close_context_tokens: <int>` in the stand-in's `governance/project/facts.yaml` (`budgets:` admits any key with a whole number ≥ 1).
- **`gov.context`** (`src/gov/context/__init__.py`): a constant `SUPPLEMENTARY_CAP = 6000` beside `DEFAULT_BUDGET` (6000); in `context(root, ticket, *, budget=...)` the room given to the supplementary search is `min(limit - mandatory_tokens, SUPPLEMENTARY_CAP)`; nothing else about the packet changes (mandatory part, refusals, hash). A reader `close_budget(root) -> int`: the setting from facts.yaml; `DEFAULT_BUDGET` when facts.yaml or the key is absent; a `GovError` (`gov.cli.errors.GovError`) with code `CONTEXT_SETTING_INVALID`, naming the key and the value, for a value that is not a whole number ≥ 1 (a bool is not a whole number: `true` refuses too).
- **`gov close`** (`src/gov/close/command.py`, `_build_context(root, ticket)`, the close's context step): calls `context(root, ticket, budget=close_budget(root))`; a `GovError` from `close_budget` becomes the existing `_Finding("CONTEXT_FAILED", …)` with the code in its details (`context_error`). A packet over the ceiling is `_Finding("CONTEXT_FAILED", …)` with `details["context_error"] == "CONTEXT_OVER_CEILING"` (today's form). No other close step changes.
- Not changed: `gov context`'s CLI (`--budget`, default 6000), `context_check.py`, the brief builder, the facts schema.

You may drive the close's context step through `gov.close.command._build_context(root, ticket)` on a real stand-in (no mock of `gov.context`), and `gov context` through its CLI (`python3 -m gov.cli.main context --json --root <stand-in> <ticket> --budget N`, as `tests/acceptance/W1-24/w1_24_support.py:255` does). Read how the earlier suites build a stand-in project with a store, a register and an index (fresh enough that the supplementary block is actually filled): `tests/acceptance/W1-24/w1_24_support.py`, `tests/acceptance/W1-24/test_w1_24_supplementary.py`, `tests/acceptance/W1-24/test_w1_24_pressure.py`, `tests/acceptance/W2-04/w2_04_support.py`, `tests/acceptance/W2-04/test_w2_04_ceiling.py`, `tests/acceptance/W2-04/test_w2_04_batches.py`. Reuse their patterns by copying into your own support module under `tests/acceptance/W2-183/` (never import across another ticket's folder if it would make your cases depend on edits there; importing an unchanged helper is fine). Never use this repository's own store or `.gov-runtime/`; every case works in `tmp_path` stand-ins.

## What each case must show (the key edges)
- **S1:** a ~10,000-token mandatory part (ticket text plus mandatory inputs): `_build_context` returns a packet with the setting at 65536; refused `CONTEXT_FAILED`, `context_error` `CONTEXT_OVER_CEILING`, with the setting at 8000 and with the key absent and with facts.yaml absent; `gov context` with no `--budget` on the same stand-in still refuses at 6,000 (the default unchanged). Optionally `close_budget(root)` returns 65536 / 6000 directly.
- **S2:** a stand-in store with enough supplementary material to pass 6,000 tokens: `gov context <t> --budget 60000` → the supplementary block's tokens sum (each item's `tokens`) ≤ 6000 and > 0; the close's packet with the setting at 65536 likewise ≤ 6000 and > 0. Prove the stand-in really fills: at the base (before the change) the same call gives more than 6,000 tokens of supplementary context — record that number in your return (this is what makes the case red now). Also an edge: a budget whose room is under 6,000 (for example mandatory + 3,000) still gets at most that room.
- **S3:** a small stand-in ticket at the default budget: the packet's `hash` and its item ids (mandatory and supplementary) equal the values it had before the change. Record them on the base code (d36c268c1, the code in your tree now) and pin them in the test with a comment naming the base commit; make the stand-in fully deterministic (fixed text, no timestamps in what is hashed). And: a ticket whose mandatory part passes the budget is refused `CONTEXT_OVER_CEILING`, the error names the ticket and the token count; and the mandatory items in a passing packet are whole (each mandatory input present, not cut).
- **F1:** `budgets.close_context_tokens` at `0`, `-5`, `"many"` (and `true`, `2.5` as edges) each make `_build_context` raise `_Finding` with code `CONTEXT_FAILED` and `details["context_error"] == "CONTEXT_SETTING_INVALID"`, the message naming the key `budgets.close_context_tokens`; never a packet built at a default, never another exception type.

Expected on the base: S1's passing case, S2's cap cases and F1 red (the code does not exist yet); S3's cases and S1's refusal cases green (they guard what must not change). State each case's expected base result in the folder's README.md (a map: case → KPI line → expected on base). A case red on the base must fail on its assertion (or on the missing name `close_budget`/`SUPPLEMENTARY_CAP` as an import inside the test function, not at module import, so the other cases still run).

## Planted breaks (prove, then remove)
Your cases must catch a wrong implementation, not only a missing one. In a throwaway copy of `src/gov` under your scratch (put its parent first on PYTHONPATH; never edit `src/` in your tree, never commit it), make the smallest stand-in implementation of the interface, see your cases pass, then plant each break and record: the plant, the command, the failing assertion line. Breaks: (a) the cap applied as `limit - mandatory` only (no min with 6000) → S2 fails; (b) the cap applied to the whole packet (mandatory shortened) → S3 fails; (c) `close_budget` ignoring the setting (always 6000) → S1 fails; (d) an invalid setting silently defaulting to 6000 → F1 fails; (e) `close_budget` accepting `true` as 1 → the bool edge fails. Delete the copy afterwards.

## How you run tests
Every pytest through the heavy slot, TMPDIR outside the repository and outside ~/gov-os-runs (make it first with `mkdir -p /tmp/w2-183-td`):
```
env TMPDIR=/tmp/w2-183-td PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-183-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-183-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-183 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
PYTHONPATH must be absolute. Keep the folder fast (well under a minute; build each stand-in once per module with a module-scoped fixture where you can). If another ticket's case turns red, name it with file:line and leave it. A resource gate's refusal is a wait, not a refusal: wait and retry. Never a hand-written sleep loop.

## Searching
No `gov retrieve` and no `gov context` in the sandbox: use the Read and Grep tools; if the first search does not answer, search again once in different words; then answer from both with path and lines, or say "not found". Reads are open, except: secrets, the held-out qualification material's contents, the evaluation sets' root and any hidden or memory-verdict folder (never open them). Do not read `src/gov/context/__init__.py`'s or `src/gov/close/command.py`'s internals to shape your cases beyond the interface above; the CLI's usage and the earlier suites are your guide.

## Forms that work
Write and edit with the Write and Edit tools and absolute paths. Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-183-tests/.gov-runtime/scratch/, run with `bash <file>` or `python3 <file>`. Literal paths only as write targets. Refused twice for the same call by the guard, sandbox or a hook: stop and say so; never work around a refusal. No merge, no push.

## Commit (your paths only; one or more commits)
```
git -C /home/usain/gov-os-worktrees/W2-183-tests commit -m "W2-183: <subject>" --trailer "Task: DAEO-href" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1165, DEC-1027, DEC-860, CAP-15.d" -- tests/acceptance/W2-183
```
`Implements:` only ids from the ticket's sources (DEC-1165, DEC-1027, DEC-860, CAP-15.d), the ones your change applies. Never `Role: owner` or `Decided-by:`. Before you return, `git -C /home/usain/gov-os-worktrees/W2-183-tests status --short` must be empty for tracked files, and `git -C /home/usain/gov-os-worktrees/W2-183-tests diff d36c268c1 --stat` must name only tests/acceptance/W2-183/; no skip, xfail, flaky or rerun mark.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: (DONE or PACKAGES or ESCALATION) / work_completed: / files_changed: / evidence: (the folder's run on the base with counts, each case red or green and why; the base's supplementary tokens at --budget 60000 in the S2 stand-in; the S3 pinned hash and how recorded; each planted break: plant, command, failing line) / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; guard_refusals: none or a line each.
