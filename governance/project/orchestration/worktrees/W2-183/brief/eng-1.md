Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-183/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: engineer, W2-183 (DAEO-href), run 2: build to the stated interface

You are a fresh engineer (role engineer), ticket DAEO-href (W2-183), profile STANDARD, class C2.
Headless: only your last message is read. You implement the ticket until its acceptance tests pass, inside its allowed paths.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-183 |
| branch | w2/W2-183 (head 74d35283b; the acceptance tests are merged at 8a62f6c60) |
| allowed paths (nothing else) | src/gov/context/__init__.py, src/gov/close/command.py, governance/project/facts.yaml, tests/unit/context/test_w2_183_*.py, tests/unit/close/test_w2_183_*.py, tests/unit/close/test_context.py |
| the ticket (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-href.md |
| your context packet (gov context output, JSON) | /home/usain/gov-os-worktrees/W2-183/.gov-runtime/scratch/lead/briefs/ctx-eng.txt |
| the acceptance tests (read-only; never edit) | /home/usain/gov-os-worktrees/W2-183/tests/acceptance/W2-183/ (README.md maps each case to its KPI line) |
| the decision register (grep by id only: DEC-1165, DEC-1027, DEC-860; CAP-15.d is in docs/contract/) | /home/usain/gov-os-worktrees/W2-183/docs/DECISION_REGISTER.md |

## What must be true (KPI lines)
| id | line |
|---|---|
| S1 | gov close builds the ticket's context packet at the project's setting `budgets.close_context_tokens` in governance/project/facts.yaml (65536 in this repository), not at gov context's default of 6,000; with no setting, the default applies as today [DEC-1165 (1), DEC-1027 H] |
| S2 | gov context's supplementary block holds at most 6,000 tokens whatever --budget is passed (its room is the smaller of the budget less the mandatory part, and 6,000); the close's packet is capped the same way [DEC-1165 (2), DEC-860] |
| S3 | the mandatory part is never shortened, and a packet whose budget leaves under 6,000 tokens of room is unchanged: the same items and the same hash as before the change [DEC-1165 (3), CAP-15.d] |
| F1 | A setting that is not a positive whole number refuses by name (never a silent default, never a crash): `0`, `-5`, `"many"` each make the close's context step refuse with a named finding. |

Non-goals (do not build): no trimming of any ticket's text or sources; no change to `src/gov/context/context_check.py`, to the brief builder (`src/gov/brief/`), to the kernel's facts schema, or to `gov context`'s CLI (`--budget`, default 6000); no change to `DEFAULT_BUDGET` (6000).

## The interface (stated by the CTO; build exactly this, nothing else changes)
- **`src/gov/context/__init__.py`:** a constant `SUPPLEMENTARY_CAP = 6000` beside `DEFAULT_BUDGET`. In `context(...)` the room passed to `_try_supplementary` (today `limit - mandatory_tokens`, near line 348) becomes `min(limit - mandatory_tokens, SUPPLEMENTARY_CAP)`. Nothing else about the packet changes: the mandatory part, the refusals (`CONTEXT_OVER_CEILING` with its details), the `budget` field (`limit` stays the limit passed), the hash.
- **A reader `close_budget(root: Path) -> int`** in the same module: the value of `budgets.close_context_tokens` in `<root>/governance/project/facts.yaml`; `DEFAULT_BUDGET` when facts.yaml is absent, when it has no `budgets:` mapping, or when the key is absent. A value that is not a whole number ≥ 1 raises `gov.cli.errors.GovError` with code `CONTEXT_SETTING_INVALID`, a message naming the key `budgets.close_context_tokens` and the value, and details carrying both. **Refused:** `0`, `-5`, `"many"`, `2.5`, a bool (`true`/`false`: `isinstance(v, bool)` is checked before `int`), and a **quoted number** (`"65536"`, a YAML string, is not a whole number: the CTO's answer). A facts.yaml that is not readable YAML or not a mapping: refuse by name too (a `GovError`, never a crash and never a silent default); say in your return which code you chose.
- **`src/gov/close/command.py`, `_build_context(root, ticket)`:** calls `build_context(root, ticket, budget=close_budget(root))`, with the `close_budget` call inside the existing `try ... except GovError` so its `GovError` becomes the existing `_Finding("CONTEXT_FAILED", …)` with `details["context_error"] == "CONTEXT_SETTING_INVALID"`. A packet over the ceiling stays `_Finding("CONTEXT_FAILED", …)` with `context_error` `CONTEXT_OVER_CEILING` (today's form). No other close step changes.
- **`governance/project/facts.yaml`:** add `close_context_tokens: 65536` under `budgets:` (keep the existing keys and order; a one-line comment citing DEC-1165 (1) is fine).

## The unit tests you write (the CTO's answers)
- `tests/unit/close/test_context.py`: revise only its `test_the_packet_is_the_one_gov_context_built` case (line 31, `built.assert_called_once_with(ROOT, "T-1")`) to the decided call, `built.assert_called_once_with(ROOT, "T-1", budget=close_budget(ROOT))` (import `close_budget` from `gov.context`; `ROOT` is `/no-such-project`, so it is `DEFAULT_BUDGET`), keeping what the case guards (the packet is gov context's own). Leave the file's other cases as they are; they must stay green.
- `tests/unit/context/test_w2_183_close_budget.py` (or a name of that form): `close_budget` on `tmp_path` stand-ins: the setting read (65536); absent file / no `budgets:` / no key → 6000; each refusal `0`, `-5`, `"many"`, `2.5`, `true`, `false`, the **quoted `"65536"`** → `GovError` `CONTEXT_SETTING_INVALID` naming the key; malformed YAML → your named refusal; `SUPPLEMENTARY_CAP == 6000` and `DEFAULT_BUDGET == 6000`.
- `tests/unit/close/test_w2_183_*.py`: `_build_context` with a quoted `"65536"` and with `true` in a stand-in's facts.yaml → `_Finding` `CONTEXT_FAILED`, `context_error` `CONTEXT_SETTING_INVALID`, and `gov.context.context` never called (patch it as test_context.py does); and with the setting at 65536 → `gov.context.context` called with `budget=65536`.

## Order
1. Read the acceptance folder's README.md and the cases; read `src/gov/context/__init__.py` and `_build_context` in `src/gov/close/command.py` (near line 500).
2. Write the unit tests first; see them red.
3. Implement; see the unit tests and the acceptance folder green.
4. Run the suites that judge the context (below); every case green, or name each red with file:line and why.
5. Commit (below); `git -C /home/usain/gov-os-worktrees/W2-183 status --short` empty for tracked files.

## How you run tests
Every pytest through the heavy slot, with your sandbox's own `$TMPDIR` as the TMPDIR (the sandbox's /tmp is read-only; use no other temporary folder), an empty HOME, PYTHONPATH absolute:
```
env TMPDIR="$TMPDIR" PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-183/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-183/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <FOLDER_OR_FILE> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Put that line in a script file under /home/usain/gov-os-worktrees/W2-183/.gov-runtime/scratch/ and run it with `bash <file>`. The folders that judge the context: `tests/acceptance/W2-183`, `tests/acceptance/W1-24`, `tests/acceptance/W2-04`, `tests/unit/context`, `tests/unit/close`, and W2-13's S5 cases (`tests/acceptance/W2-13/test_w2_13_role_separation.py`). The W2-183 ledger cases need `gitleaks` on PATH (it is in /home/usain/.local/bin; add it to PATH in the env line if it is not found). If a case asserts that a large `--budget` fills the supplementary block past 6,000 tokens, do not change it: name it with file:line in your return (its revision is the CTO's). If another ticket's case turns red, name it with file:line and leave it. A resource gate's refusal is a wait, not a refusal: wait and retry. Never a hand-written sleep loop.

## Searching
No `gov retrieve` and no `gov context` in the sandbox: use the Read and Grep tools; if the first search does not answer, search again once in different words; then answer from both with path and lines, or say "not found". Reads are open, except: secrets, the held-out qualification material's contents, the evaluation sets' root and any hidden or memory-verdict folder (never open them).

## Forms that work
Write and edit with the Write and Edit tools and absolute paths. Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-183/.gov-runtime/scratch/, run with `bash <file>` or `python3 <file>`. Literal paths only as write targets. Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal, not by another tool or form. No merge, no push, no edit under tests/acceptance/.

## Commit (your paths only; one or more commits)
```
git -C /home/usain/gov-os-worktrees/W2-183 commit -m "W2-183: <subject>" --trailer "Task: DAEO-href" --trailer "Role: engineer" --trailer "Implements: DEC-1165, DEC-1027, DEC-860, CAP-15.d" -- <your paths>
```
`Implements:` only ids from the ticket's sources (DEC-1165, DEC-1027, DEC-860, CAP-15.d), the ones your change applies. Never `Role: owner` or `Decided-by:`. Before you return: `git -C /home/usain/gov-os-worktrees/W2-183 diff 74d35283b --stat` names only your allowed paths; no skip, xfail, flaky or rerun mark.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: (DONE or PACKAGES or ESCALATION) / work_completed: / files_changed: / evidence: (each suite's command and counts, passed/failed; each red named with file:line and why; the malformed-YAML code you chose) / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; guard_refusals: none or a line each.
