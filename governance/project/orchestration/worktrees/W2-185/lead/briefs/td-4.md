# Brief: independent test designer, W2-185 (DAEO-qyt2), run 3 batch 4: revise the two `[PostToolUse]` cases of W1-38's hooks command-line file to the decided behaviour (DEC-1167 (4), DEC-1156 (7))

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-qyt2 (W2-185), profile STANDARD,
class C2. Headless: only your last message is read.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-185-tests |
| branch | w2/W2-185-tests (head 6b4bafb71: the ticket's build, its run-2 revision and narrow check PASS, and w2/integrate merged) |
| your context packet (gov context output: the ticket, KPIs, sources) | /home/usain/gov-os-worktrees/W2-185-tests/.gov-runtime/scratch/brief/td-context.md |
| the ticket (read-only; widened 2026-11-14 by the one file below) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-qyt2.md |
| the failing output before your revision (the lead's run at 6b4bafb71; may still be running when you start) | /home/usain/gov-os-worktrees/W2-185-tests/.gov-runtime/scratch/brief/reds-pre-6b4bafb71.txt |
| the run-2 probe record (how the 18 sibling cases were revised: the same pattern) | /home/usain/gov-os-worktrees/W2-185-tests/docs/probes/DAEO-qyt2/ |
| the decision register (grep by id only) | /home/usain/gov-os-worktrees/W2-185-tests/docs/DECISION_REGISTER.md |
| scratch | your sandbox's own `$TMPDIR` only (`/tmp` and `.gov-runtime/scratch/` are refused) |

Your allowed paths (write nothing else; NOT `src/**`, NOT `template/**`, NOT `tests/acceptance/W2-185/**`):
- `tests/acceptance/W1-38/test_w1_38_hooks_command_line.py`
- `tests/acceptance/W1-38/w1_38_hooks_support.py` (only if a helper there must learn to pick an entry by its program;
  every other caller of a helper you change must stay green: run them)

## The decided behaviour (what the cases must now pin)
DEC-1167 (4) (read it by id in the register, with DEC-971 item 3, DEC-917 and DEC-1156 (7)):
- The template's hooks source `template/.rulesync/hooks.jsonc` wires `context_watch.py` in `postToolUse` (matcher `Bash`,
  timeout 10, command running `$CLAUDE_PROJECT_DIR/governance/kernel/hooks/context_watch.py`, in the root
  `.rulesync/hooks.jsonc`'s form), beside its guard entry running `posttooluse.py`. So the template's `postToolUse` has two
  entries, and the kernel hooks are seven. The context watch is not a guard line: DEC-917's rule (a guard line is the
  kernel template's exit-mapping line exactly) applies to the guard's entry, the one running `posttooluse.py`.

## The order
Two node ids are red at 6b4bafb71 because each assumes one entry under `PostToolUse`:
1. `tests/acceptance/W1-38/test_w1_38_hooks_command_line.py::TestGeneratedCommandLines::test_the_generated_command_line_is_the_kernel_template_s[PostToolUse]`
   (via `_one_generated`, which asserts `len(commands) == 1` over `hooks.registered_commands(settings, PROGRAMS, event)`)
2. `tests/acceptance/W1-38/test_w1_38_hooks_command_line.py::test_the_source_s_command_line_is_the_kernel_template_s_form[PostToolUse]`
   (asserts `len(hooks.source_command_lines()[event]) == 1`)

Revise both to the decided behaviour: **pick the guard's entry by its program** (the one running the guard program of
that event, `posttooluse.py` under PostToolUse), never by index, and hold that one entry's line to the kernel template's
line exactly, as before.
- **No case loses its point.** Each still guards: exactly one guard entry under each guard event (two guard entries, or
  none, is still red); that entry's line equals the kernel template's exit-mapping line exactly; under a lifecycle event,
  one entry in DEC-608's plain form. Where the PostToolUse event now also holds the context watch's entry, the case may
  say so (the context watch's own line in the root's form is pinned elsewhere; you may check it is present, but do not
  hold it to the guard's form).
- The other parametrised ids (PreToolUse, PostToolUseFailure, the lifecycle events) must stay green and unchanged in
  what they assert. Lower nothing; add no skip, xfail, flaky or rerun mark; delete no case; keep the parametrised ids
  (`tests/optin-lifted-breadth.txt` names this file's cases; you may not edit those lists).
- **One commit** (for both cases; the support file too if you touch it, in the same commit), with the trailer
  `Rewrite-Reason: DEC-1167 (4), DEC-1156 (7) (W2-185 run 3)`.
- Do not read `git diff` or the history of `src/gov/adapters/portability.py` or `tests/unit/adapters/test_w2_185_*.py`
  (the engineer's work on this ticket, DEC-820). Reading the template's hooks source, the kernel hooks and the kernel
  template's settings is open.

## Prove it
Every pytest through the heavy slot, TMPDIR your sandbox's own `$TMPDIR`, with the opt-in suites:
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-185-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-185-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest --optin lifted,breadth tests/acceptance/W1-38/test_w1_38_hooks_command_line.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" -rf
```
1. Both ids pass at your head; quote the count line and compare with the pre-run's count (no case gone). If the pre-run
   file is absent or has no count line, make the same run first yourself at 6b4bafb71, unchanged, and keep its count line.
2. Plants in a reverted edit, each showing the revised cases still fail on what they guard: (a) a second guard entry
   running `posttooluse.py` under the template's `postToolUse` turns both red; (b) the guard entry's command changed by
   one character turns both red; (c) the guard entry removed (only the context watch left) turns both red. Revert every
   plant; say each in one line with the failing line.
3. If you touched `w1_38_hooks_support.py`: run every test file that imports it (grep `w1_38_hooks_support`), same form,
   and quote each count line. In any case also run `tests/acceptance/W1-38/test_w1_38_hooks_source.py` and
   `tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py`, same form.
A resource gate's refusal is a wait.

Read and Grep only; no `gov retrieve` or `gov context`; search again once if the first search does not answer. Write and
edit with the Edit tool and absolute paths. Refused twice for the same call: stop and say so; never work around a refusal.
No merge, no push. Never open the evaluation sets' root, held-out material or any hidden or memory-verdict folder.

## Commit (your paths only)
```
git -C /home/usain/gov-os-worktrees/W2-185-tests commit -m "<subject>" --trailer "Rewrite-Reason: DEC-1167 (4), DEC-1156 (7) (W2-185 run 3)" --trailer "Task: DAEO-qyt2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1167, DEC-1156" -- <the file(s)>
```
Trailers in one final paragraph. Never `Role: owner` or `Decided-by:`. Before you return: tracked `git status --short` empty.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; per case: <node id> | what it guards | the revision in one line; guard_refusals: none or a line each.
