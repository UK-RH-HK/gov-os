# Brief: independent test designer, W2-185 (DAEO-qyt2), run 2 batch 3: revise 18 cases to the decided behaviour (DEC-1167 (4), DEC-1156 (7))

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-qyt2 (W2-185), profile STANDARD,
class C2. Headless: only your last message is read.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-185-tests |
| branch | w2/W2-185-tests (head 0c7e4d68f: the ticket's build, its narrow check PASS, and w2/integrate merged) |
| your context packet (gov context output: the ticket, KPIs, sources) | /home/usain/gov-os-worktrees/W2-185-tests/.gov-runtime/scratch/brief/td-context.md |
| the ticket (read-only; widened 2026-11-13 by the eight files below) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-qyt2.md |
| the probe record naming the 18 cases and a one-line revision for each | /home/usain/gov-os-worktrees/W2-185-tests/docs/probes/DAEO-qyt2/PR-DAEO-qyt2.md (lines 41-57) |
| the decision register (grep by id only) | /home/usain/gov-os-worktrees/W2-185-tests/docs/DECISION_REGISTER.md |
| scratch | your sandbox's own `$TMPDIR` only (`/tmp` and `.gov-runtime/scratch/` are refused) |

Your allowed paths (write nothing else; NOT `src/**`, NOT `template/**`, NOT `tests/acceptance/W2-185/**`):
- `tests/unit/gitenv/test_hooks_lifted.py`
- `tests/acceptance/W2-59/test_w2_59_hook_lines.py`
- `tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py`
- `tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py`
- `tests/acceptance/W1-38/test_w1_38_hooks_source.py`
- `tests/acceptance/W1-38/w1_38_hooks_support.py`
- `tests/unit/hooks/test_w2_106_template_hook_lines.py`
- `tests/acceptance/W2-05/test_w2_05_hooks_source.py`

## The decided behaviour (what the cases must now pin)
DEC-1167 (4) (read it by id in the register, with DEC-971 item 3 and DEC-1156 (7)):
- The template's hooks source `template/.rulesync/hooks.jsonc` wires `context_watch.py` in `postToolUse` (matcher `Bash`,
  timeout 10, command `$CLAUDE_PROJECT_DIR/governance/kernel/hooks/context_watch.py` in the root's form), beside its
  existing `posttooluse.py` entry. So the template's `postToolUse` has two entries, and the kernel hooks are seven.
  `context_watch.py` imports only the standard library (read `template/governance/kernel/hooks/context_watch.py`).
- Portability's hooks comparison (`gov.adapters.portability`, its public findings: `HOOKS_EVENT_DIFFERS`,
  `HOOKS_MATCHER_DIFFERS`, `HOOKS_UNREADABLE`) exempts DEC-971 item 3's lift **per hook**: only the template's entries
  running `posttooluse.py`, in `postToolUse` and `postToolUseFailure`, while the root does not run `posttooluse.py` in
  that event. Every other entry of those events compares as any other: a real drift (another matcher, another event) is
  still a finding. It no longer exempts a whole event.

## The order
The 18 node ids are red at 0c7e4d68f because each assumed one entry in `postToolUse` or the whole-event lift. Revise each
to the decided behaviour, following the probe record's one-line revision for it (lines 41-57). The lead's run of the
eight files on 0c7e4d68f, with the opt-in suites, is at
`/home/usain/gov-os-worktrees/W2-185-tests/.gov-runtime/scratch/brief/reds-pre-0c7e4d68f.txt` (the failing output; it
may still be running when you start: if it is absent or has no count line, make the same run first yourself, unchanged,
and keep its count line as the "before").
- **No case loses its point.** Each case keeps what it guarded (a lifted entry is no finding; another event in one source
  only is still a finding; the finding form is unchanged; the seven hooks' lines; the pin's package import; the guard
  entry's line in every folder; the settings line equals its source; a non-drift difference leaves portability green).
  Where a case pinned "the lift exempts a whole event", rewrite it to "the lift exempts the `posttooluse.py` entry" and keep
  the opposite face (a non-exempt entry in the same event is a finding). Pick entries by their program, never by index.
- Lower nothing; add no skip, xfail, flaky or rerun mark; delete no case; keep the parametrised ids where you can (the
  probe record and `tests/optin-lifted*.txt` name them; if an id must change, say so and check the `rep:` lines in
  `tests/optin-lifted*.txt` still match a case: you may not edit those lists, so prefer keeping the ids).
- **One commit per file**, each with the trailer `Rewrite-Reason: DEC-1167 (4), DEC-1156 (7) (W2-185 run 2)`.
- Do not read `git diff` of `src/gov/adapters/portability.py` or `tests/unit/adapters/test_w2_185_*.py` (the engineer's
  work on this ticket, DEC-820); test portability through its public entry the existing cases already use. Reading the
  template's hooks source and the kernel hooks is open.

## Prove it
Every pytest through the heavy slot, TMPDIR your sandbox's own `$TMPDIR`, with the opt-in suites:
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-185-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-185-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest --optin lifted,breadth tests/unit/gitenv/test_hooks_lifted.py tests/acceptance/W2-59/test_w2_59_hook_lines.py tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py tests/acceptance/W1-38/test_w1_38_hooks_source.py tests/unit/hooks/test_w2_106_template_hook_lines.py tests/acceptance/W2-05/test_w2_05_hooks_source.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" -rf
```
1. All 18 ids pass at your head; quote the count line (compare it with the pre-run's count: no case gone).
2. For each file, one plant in a copy (or reverted edit) showing the revised case still fails on what it guards (for
   example: the template's `posttooluse.py` lift entry given another matcher still green, but a non-exempt template entry
   in `postToolUse` added is a finding; `context_watch.py` removed from the template turns the seven-hook line red).
   Revert every plant; say each in one line.
3. `tests/acceptance/W2-185` and `tests/unit/adapters/test_w2_185_hooks_exemption.py` still pass (run them, same form).
A resource gate's refusal is a wait.

Read and Grep only; no `gov retrieve` or `gov context`; search again once if the first search does not answer. Write and
edit with the Edit tool and absolute paths. Refused twice for the same call: stop and say so; never work around a refusal.
No merge, no push. Never open the evaluation sets' root, held-out material or any hidden or memory-verdict folder.

## Commit (your paths only, one file per commit)
```
git -C /home/usain/gov-os-worktrees/W2-185-tests commit -m "<subject>" --trailer "Rewrite-Reason: DEC-1167 (4), DEC-1156 (7) (W2-185 run 2)" --trailer "Task: DAEO-qyt2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1167, DEC-1156" -- <the one file>
```
Trailers in one final paragraph. Never `Role: owner` or `Decided-by:`. Before you return: tracked `git status --short` empty.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; per case: <node id> | what it guards | the revision in one line; guard_refusals: none or a line each.
