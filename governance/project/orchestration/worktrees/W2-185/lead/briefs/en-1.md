# Brief: engineer, W2-185 (DAEO-qyt2), run 1 batch 1: S1 (the template's context-watch line) and S2 (the per-hook lift exemption)

You are a fresh engineer (role engineer), ticket DAEO-qyt2 (W2-185), profile STANDARD, class C2. Headless: only your last
message is read.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-185 |
| branch | w2/W2-185 (from 31eab2103) |
| your context packet (gov context output, JSON: the ticket, KPIs, sources) | /home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/brief/en-context.md |
| the ticket (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-qyt2.md |
| the decision register (grep by id only) | /home/usain/gov-os-worktrees/W2-185/docs/DECISION_REGISTER.md |
| scratch | your sandbox's own `$TMPDIR` only (`/tmp` is read-only in the sandbox) |

Your allowed paths (write nothing else):
- `template/.rulesync/hooks.jsonc`
- `src/gov/adapters/portability.py`
- `tests/unit/adapters/test_w2_185_*.py` (new: your unit cases)

NOT `tests/acceptance/**` (a test designer writes `tests/acceptance/W2-185/` and revises
`tests/acceptance/W1-38/w1_38_support.py` in `/home/usain/gov-os-worktrees/W2-185-tests` at the same time: never read
that tree or its branch, DEC-820). NOT the root's `.rulesync/hooks.jsonc` or `.claude/` (a non-goal: no change to what
this repository's sessions run). Nothing under `template/governance/kernel/` (the kernel gate; if you find you need it,
stop and say so).

## What to build
- S1: in `template/.rulesync/hooks.jsonc`'s `postToolUse`, after the existing `posttooluse.py` entry (which stays), add
  one entry `{"type": "command", "matcher": "Bash", "command": <the root .rulesync/hooks.jsonc's context_watch.py
  command, with `$CLAUDE_PROJECT_DIR/template/governance/kernel/hooks/` written `$CLAUDE_PROJECT_DIR/governance/kernel/hooks/`>,
  "timeout": 10}`. The CTO's earlier try of exactly this line is commit f0cb5284d (reverted in f299a5eb6 because S2 and
  W1-38's fixture were not there yet): `git show f0cb5284d` gives the bytes. [DEC-1163 (6) E (a), DEC-1167 (4)]
- S2: `gov.adapters.portability._hooks_findings(root)` today skips a lifted event (`LIFTED_HOOK_EVENTS`: `postToolUse`,
  `postToolUseFailure`) as a whole while only the template has it, and compares by sorted matchers per event
  (`_hook_matchers`). With S1, the template's `postToolUse` has two `Bash` entries (`posttooluse.py`, `context_watch.py`)
  against the root's one (`context_watch.py`): a `HOOKS_MATCHER_DIFFERS`. Change the exemption to per hook: in the
  template's lifted events, the entries whose command runs `posttooluse.py` are left out of the comparison (DEC-971
  item 3's lift: exactly ACT 1's lifted hook, named in the comparison, ending with W2-08); the rest of each event
  compares with the root's as any other event; a lifted event left with no entries on the template's side and absent
  from the root is no finding. Keep the finding codes and messages' forms (`HOOKS_EVENT_DIFFERS`,
  `HOOKS_MATCHER_DIFFERS`, `HOOKS_UNREADABLE`) and the function's signature. Update the module docstring (lines 17-20),
  the constant's comment (lines 45-48) and `_hooks_findings`'s docstring to say per hook. [DEC-971 item 3, DEC-805,
  DEC-1167 (4)]
- F1 (must still hold): a real drift is still a finding: an extra matcher on the root's `postToolUse`; a template hook in
  another event; a template `postToolUse` entry other than `posttooluse.py` while the root has no `postToolUse`.
- Unit cases (test first, red before the code): `tests/unit/adapters/test_w2_185_hooks_exemption.py`, over stand-in roots
  in `tmp_path` (a `template/governance/kernel/` folder, `template/.rulesync/hooks.jsonc`, `.rulesync/hooks.jsonc`): the
  exempt entry gives no finding; the S1-shaped pair gives none; each F1 drift gives its finding naming the event; a
  `posttooluse.py` entry in a non-lifted event is not exempt.

## Prove it
1. Your unit file passes; red before the code (quote it).
2. With S1 and S2 both in: `tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree`,
   `tests/acceptance/W2-05/test_w2_05_hooks_source.py` (whole file), `tests/acceptance/W2-23/test_w2_23_space.py`
   (whole file; its line 94 case S6 turns green with S1), and `tests/unit/adapters/` (whole folder) pass.
3. Expected red on your branch and not yours to fix: `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist`
   and `tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_an_ordinary_allowed_call_is_not_blocked`
   turn red with S1 until the test designer's fixture (seven hooks) is merged. Run them once and quote the failure; do
   not touch them. Any other red: name it with file:line and stop there (the CTO fixes another ticket's case).

Every pytest through the heavy slot, TMPDIR your sandbox's own `$TMPDIR`:
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-185/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <file or folder>[::<test>] -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
A whole-folder run adds `-m "not local_only" -k "not real and not green_here and not time_limit"`. A resource gate's
refusal is a wait (relaunch when it opens). Quote the count lines in your return.

## Searching
Read and Grep only; no `gov retrieve` or `gov context` in the sandbox. Search once, then once more in other words; answer
from what you read with path and line, or say "not found". Never open the evaluation sets' root, held-out material or any
hidden or memory-verdict folder.

## Forms that work
Write and edit with the Write and Edit tools and absolute paths. Anything longer than one line of shell goes in a script
under your `$TMPDIR`, run with `bash <file>`. Refused twice for the same call by the guard, the sandbox or a hook: stop and
say so; never work around a refusal. No merge, no push.

## Commit (your paths only; one or more commits)
```
git -C /home/usain/gov-os-worktrees/W2-185 commit -m "<subject>" --trailer "Task: DAEO-qyt2" --trailer "Role: engineer" --trailer "Implements: DEC-1167, DEC-1163, DEC-971, DEC-805" -- <your paths>
```
Trailers in one final paragraph. Never `Role: owner` or `Decided-by:`. Before you return: tracked `git status --short` empty.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; guard_refusals: none or a line each.
