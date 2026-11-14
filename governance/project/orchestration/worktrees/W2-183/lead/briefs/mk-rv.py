from pathlib import Path
root = Path("/home/usain/gov-os-worktrees/W2-183")
judgement = (root / "governance/project/briefs/JUDGEMENT.md").read_text(encoding="utf-8")
head = """# Brief: independent auditor, W2-183 (DAEO-href), the STANDARD review (round 1)

You are a fresh independent auditor (role independent-auditor), ticket DAEO-href (W2-183), profile STANDARD, class C2.
Headless and read-only: you write nothing (no file, no commit); only your last message is read. You judge the head below against the ticket's KPI lines and return a structured verdict per line.

## What you review
| what | value |
|---|---|
| the tree (read only) | /home/usain/gov-os-worktrees/W2-183 |
| the head to probe | e0c076514c9dbbf84d8fca72a93c37b7fa60847b (branch w2/W2-183) |
| the base of the ticket's own change | 74d35283b (the diff: `git -C /home/usain/gov-os-worktrees/W2-183 diff 74d35283b e0c076514c9d`) |
| the ticket (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-href.md |
| the decision register (grep by id only: DEC-1165, DEC-1027, DEC-860; CAP-15.d is in docs/contract/) | /home/usain/gov-os-worktrees/W2-183/docs/DECISION_REGISTER.md |
| the acceptance tests and their map | /home/usain/gov-os-worktrees/W2-183/tests/acceptance/W2-183/ (README.md) |
| the implementer's session | b1f27b65-a5cf-47c1-aa82-f46022cc2690 (engineer, commit e0c076514c9d) |

## The KPI lines (judge each)
| id | line | verify |
|---|---|---|
| S1 | gov close builds the ticket's context packet at the project's setting `budgets.close_context_tokens` in governance/project/facts.yaml (65536 in this repository), not at gov context's default of 6,000; with no setting, the default applies as today [DEC-1165 (1), DEC-1027 H] | in a stand-in repository, a ticket whose own text and mandatory inputs come to about 10,000 tokens passes the close's context step with the setting at 65536 and is refused CONTEXT_FAILED (context_error CONTEXT_OVER_CEILING) with the setting at 8000 or absent |
| S2 | gov context's supplementary block holds at most 6,000 tokens whatever --budget is passed (its room is the smaller of the budget less the mandatory part, and 6,000); the close's packet is capped the same way [DEC-1165 (2), DEC-860] | in a stand-in with a store large enough to fill it, `gov context <ticket> --budget 60000` gives a supplementary block of at most 6,000 tokens; the same with the close's setting at 65536 |
| S3 | the mandatory part is never shortened, and a packet whose budget leaves under 6,000 tokens of room is unchanged: the same items and the same hash as before the change [DEC-1165 (3), CAP-15.d] | a small stand-in ticket's packet at the default budget has the hash it had before the change; a ticket whose mandatory part passes its ceiling is still refused CONTEXT_OVER_CEILING, named |
| F1 | A setting that is not a positive whole number refuses by name (never a silent default, never a crash). | `budgets.close_context_tokens: 0`, `-5` and `"many"` each make the close's context step refuse with a named finding |

Non-goals (not findings): no trimming of any ticket's own text or sources; no change to gov check's context-reproducibility (`src/gov/context/context_check.py`), to the brief builder or to the kernel's facts schema; no change to the default ceiling of 6,000 for gov context and briefs.

The interface the CTO stated (the build is judged against it): `SUPPLEMENTARY_CAP = 6000` beside `DEFAULT_BUDGET` in `src/gov/context/__init__.py`; the supplementary room `min(limit - mandatory_tokens, SUPPLEMENTARY_CAP)`; `close_budget(root) -> int` reading the setting, `DEFAULT_BUDGET` when the file or key is absent, a `GovError` `CONTEXT_SETTING_INVALID` naming the key and value for anything that is not a whole number >= 1 (a bool and a quoted number such as `"65536"` refuse too); `_build_context` in `src/gov/close/command.py` calling `context(root, ticket, budget=close_budget(root))`, a `GovError` from it becoming `_Finding("CONTEXT_FAILED", ...)` with `context_error`; nothing else changed.

## What the lead already has (do not re-run the whole suite; probe)
- `gov accept W2-183` on the head: pass, 49 of 49 (S1 14, S2 11, S3 11, F1 13).
- The scoped run on the head (lead_verify, 6,137 tests): 6 red. Five are red on the base too (W2-128 row 8 x2, W2-152 S10, W2-153 compose and portability: role-file composition, not this ticket's paths). One is caused by the decided cap: `tests/acceptance/W2-54/test_w2_54_dropped_order.py:172` (`test_a_ticket_whose_items_fit_keeps_every_item_and_drops_nothing`) gives a budget "with room for every item of its evidence" and asserts nothing is dropped; under the cap an item past 6,000 is dropped. The lead returns that to the CTO as a package (its revision is the CTO's): judge whether the cap's behaviour there is what S2 decides, and say so; it is not a finding against this branch unless you find the cap applied wrongly.
- The suites that judge the context, all green on the head: tests/acceptance/W1-24 (54), W2-04 (74), W2-13 role separation (12), tests/unit/context (84), tests/unit/close (184).

## What to probe (in proportion to STANDARD)
Read the diff whole and the KPI lines; check each line against the code and the tests (not only that the tests pass: that they would catch a wrong implementation). Planted checks are welcome in a throwaway copy under your sandbox's own `$TMPDIR` (copy `src/gov` there and put its parent first on PYTHONPATH; never edit the tree). Things worth a look: the close's other uses of the packet (the close record's packet hash, `gov check`'s context reproducibility, which builds at the default: is a close packet built at 65536 still compared with a packet built the same way, or does a reader now see two different hashes for one ticket?); the case where `budget` is smaller than the mandatory part plus the cap; an empty or malformed facts.yaml in a real close; whether any other caller of `gov.context.context` relied on a big budget filling the supplementary block.

## How you run tests
Every pytest through the heavy slot, with your sandbox's own `$TMPDIR` (the sandbox's /tmp is read-only; use no other temporary folder), an empty HOME inside that `$TMPDIR`, PYTHONPATH absolute:
```
env TMPDIR="$TMPDIR" PATH=/home/usain/.local/bin:$PATH PYTHONUSERBASE=/home/usain/.local HOME="$TMPDIR/empty-home" PYTHONPATH=/home/usain/gov-os-worktrees/W2-183/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <FOLDER_OR_FILE> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
A resource gate's refusal is a wait, not a refusal: wait and retry. Never a hand-written sleep loop.

## Searching
No `gov retrieve` and no `gov context` in the sandbox: use the Read and Grep tools; if the first search does not answer, search again once in different words; then answer from both with path and lines, or say "not found". Reads are open, except: secrets, the held-out qualification material's contents, the evaluation sets' root and any hidden or memory-verdict folder (never open them). Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal, not by another tool or form.

"""
tail = """

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: (DONE) / work_completed: / files_changed: none / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then each finding (F1, F2, ...) with its file:line, what it is, `Ordinary work: yes|no, because ...` and `Consequence: fails open|loses work|other`, and scope in or out.
Then your judgement in one line (pass or fail), and the fenced verdict block, exactly this form (one entry per line S1, S2, S3, F1):
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
Then: guard_refusals: none or a line each.
"""
(root / ".gov-runtime/scratch/lead/briefs/rv-1.md").write_text(head + judgement + tail, encoding="utf-8")
