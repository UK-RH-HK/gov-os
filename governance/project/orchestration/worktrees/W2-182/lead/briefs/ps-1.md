# Brief: product-spec, W2-182 (DAEO-5y8d), run 2: the template's hooks source wires context_watch.py (line E (a))

You are a fresh product-spec worker (role product-spec), ticket DAEO-5y8d (W2-182), profile LITE, class C1. Headless:
only your last message is read.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-182 |
| branch | w2/W2-182 (head 23e7c4971) |
| the ticket (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-5y8d.md |
| the ticket's context bundle (gov context output) | /home/usain/gov-os-worktrees/W2-182/.gov-runtime/scratch/lead/briefs/ps-context.md |
| the decision register (grep by id only) | /home/usain/gov-os-worktrees/W2-182/docs/DECISION_REGISTER.md |
| scratch for scripts and temp folders | your sandbox's own `$TMPDIR` only |

Your one allowed path (write nothing else): `template/.rulesync/hooks.jsonc`.

## The line (the ticket's E)
E: the template's hooks source `template/.rulesync/hooks.jsonc` wires `context_watch.py` as the root `.rulesync/hooks.jsonc`
does (ACT-CONTEXT-WATCH-1), and W2-23 S6 expects the seven kernel hooks [DEC-1163 (6) E (a)]. Verify: W2-23 S6 passes; a
planted eighth hook script with no wiring fails it; `python3 -m gov.adapters.portability` exits 0 on the template.

W2-176 added the seventh kernel hook `template/governance/kernel/hooks/context_watch.py` (13fd1dd34, hand merge 3430341c4);
ACT-CONTEXT-WATCH-1 wired it into the root `.rulesync/hooks.jsonc` only (a `postToolUse` entry, matcher `Bash`, timeout 10,
running `$CLAUDE_PROJECT_DIR/template/governance/kernel/hooks/context_watch.py` through the pinned gov's interpreter). Read
DEC-1163 (6) E by id. Read the hook program itself (`template/governance/kernel/hooks/context_watch.py`) and its unit test
(`tests/unit/hooks/test_w2_176_context_watch.py`) for what it expects (event, matcher, exit codes).

## The task
Add one `postToolUse` entry for `context_watch.py` to `template/.rulesync/hooks.jsonc`, beside the existing `posttooluse.py`
entry:
- the path is the adopted project's: `$CLAUDE_PROJECT_DIR/governance/kernel/hooks/context_watch.py` (Copier puts the kernel's
  hooks at `governance/kernel/hooks/`; every other template line uses that form);
- matcher `Bash`, timeout 10, and the root line's behaviour (the pinned gov's interpreter, `-E`; a missing pin or interpreter
  ends with the root line's message and exit). Where the template's own suites pin a line form for every template hook line
  (read them first: `tests/unit/hooks/test_w2_106_template_hook_lines.py`, `tests/acceptance/W2-106/`, `W2-65/`, `W2-59/`,
  `W2-05/`, `W1-38/test_w1_38_hooks_source.py`, `W1-38/test_w1_38_hooks_any_folder.py`, `W2-66/`, `tests/unit/gitenv/test_hooks_lifted.py`,
  `W2-90/w2_90_kernel_wiring.py`), choose the form they accept for a template line (for example the template's own
  `h="…"; … refused` form), and say in your return which form you chose and why. Change no other entry.

## Check
1. `python3 -m gov.adapters.portability` on the template (read its `--help`/source for the argument form) exits 0, before and after.
2. `tests/acceptance/W2-23/test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir` passes
   (red before your edit, naming `context_watch.py` as unreached).
3. Planted break: in a throwaway copy of the tree under `$TMPDIR` (never in the worktree), add an eighth script
   `template/governance/kernel/hooks/zz_unwired.py` with no wiring; the S6 case must fail naming it. Record plant, command
   and failing line.
4. Run, once before and once after your edit, the suites that read the template's hook lines (the list above, whole files
   or folders), and `tests/unit/hooks/`. Report each with counts. A case red after but green before is yours to fix by the
   line's form if the form is the cause; if a case pins the template's number of hook entries or names the six, so that any
   correct wiring of a seventh hook turns it red, do not touch it: name it with file:line in `discoveries` (the CTO fixes
   another ticket's case under DEC-1156 (7)).

## How you run tests
Every pytest through the heavy slot, TMPDIR the sandbox's own `$TMPDIR` (outside the repository and outside ~/gov-os-runs):
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-182/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-182/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
The three W2-23 cases failing with ADOPT_CODE_GRAPH_UNREADABLE (`w2_23_support.py:199`, a sandbox limit named in W2-23's
README) are known; name them, do not fix them. A resource gate's refusal is a wait: wait and retry, it is not a refusal.

## Searching and forms
No `gov retrieve` and no `gov context` in the sandbox: Read and Grep; search again once in different words if needed. Never
open the evaluation sets' root, held-out material or any hidden or memory-verdict folder. Write and edit with the Write and
Edit tools and absolute paths; scripts longer than one line go in `$TMPDIR`. Refused twice for the same call: stop and say
so; never work around a refusal. No merge, no push. Do not touch `tests/` (a test designer works in parallel in another tree).

## Commit (your path only)
```
git -C /home/usain/gov-os-worktrees/W2-182 commit -m "W2-182: the template's hooks source wires context_watch.py (E (a))" --trailer "Task: DAEO-5y8d" --trailer "Role: product-spec" --trailer "Implements: DEC-1163" -- template/.rulesync/hooks.jsonc
```
Never `Role: owner` or `Decided-by:`. Before you return: tracked `git status --short` empty; `git diff 23e7c4971 --stat`
names only `template/.rulesync/hooks.jsonc`.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: (portability exit codes; S6 before/after; the plant, command, failing line; each suite before/after with counts) / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; guard_refusals: none or a line each.
