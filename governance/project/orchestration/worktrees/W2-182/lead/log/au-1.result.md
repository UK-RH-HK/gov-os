task: DAEO-5y8d (W2-182), narrow independent check, run 3, head f0cb5284d117
status: PASS. No finding is in scope, reachable in ordinary work, and fails open or loses work. But landing as is turns one unit test red on integrate (F-E1 below), and that needs a decision before the land.
work_completed: Sandbox check; identity check; read the ticket, the ticket's own diff (`w2/integrate...HEAD`, 14 files, 5 commits) and the W2-182 folder. Planted each of the six breaks in a copy of HEAD in `$TMPDIR`: each case was green before the plant, red with it, and green again after reverting. Ran the no-lowering case against six plants. Ran `gov accept W2-182` in the copy. Ran portability on `template/` and at the root, before and after f0cb5284d. Compared a unit and acceptance subset between the head and its parent.
files_changed: none
evidence: the result lines under each point below
tests: 9/9 mapped cases green unplanted; 6/6 plants red on the expected assertion; R case 20/20 beside 20 busy workers; `gov accept W2-182` (copy): pass, 7/7 lines, 9 passed, 0 unmapped; unit/adapters + unit/gitenv + acceptance/W2-153: head has 19 failed, parent has 18, and the only difference is `test_this_repository_s_two_hooks_sources_agree`
discoveries: E's line makes the repository-root hooks drift check report `HOOKS_MATCHER_DIFFERS` on postToolUse, so `tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree` goes from green on the parent to red on the head.
risks: landing f0cb5284d as is puts one new red on integrate and the nightly, from a ticket whose purpose is clearing nightly reds.
lessons: a template hooks change needs checking at the repository root (the DEC-805 drift comparison), not only inside `template/`.
proposed_decisions: none
unresolved: how to clear F-E1 (options under the finding); E's literal "exits 0" (F-E2)
recommended_next_action: the CTO routes F-E1 before the land: either revise the unit test, as an own-branch path case under DEC-1156 (7) followed by a narrow check, or ask the owner for a ticket to make portability's comparison of the postToolUse event (a lifted event) ignore the lifted `posttooluse.py` entry. Then land.

**Step 0, the sandbox check (`EMG-d4b-launched.md`):**
- (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-5y8d` failed with `OSError: [Errno 30] Read-only file system` (no file left).
- (b) `git hash-object -w --stdin` printed `1ae28402a…`, exit 0; `git update-index --refresh` exit 0.
- `GOV_TICKET=DAEO-5y8d`. HEAD is `f0cb5284d1172ce85a750537b934f46f345000a3`. `git status --porcelain` was empty at the start and is empty at the end.
- `ps` check: no ollama, no llama-server, none of my stand-ins or busy loops left (only the grep's own shell matched).

## Point 1: each revised case still catches its planted break. Verdict: yes, all six

All runs used heavy_slot, `PYTHONPATH=<copy>/src` and an empty HOME, from the copy's root. The copy came from `git archive HEAD | tar -x`. Each plant was reverted by re-extracting the file from HEAD.

- **Unplanted, all 7 cases plus no-lowering:** `9 passed in 8.66s`, no skips.
- **B:** a `frobnicate` subcommand added in `src/gov/cli/main.py`.
  - Red: `AssertionError: gov has commands the command list does not record: ['frobnicate']`
- **C, W1-18:** `retrieve()` started `$GOV_OLLAMA_BIN serve`.
  - Red: `AssertionError: gov ran the stand-in ollama: [{'kind': 'exec', 'argv': ['serve'], …}] (DEC-1065 (1))`
- **C, W2-123:** `_gave_up` returned the bare `NO_EMBEDDING`, so the last failed try is not recorded in the stage's reason.
  - Red: `AssertionError: the failure's message does not state the tries and waits: … Ollama did not embed with qwen3-embedding:0.6b`
  - Also tried: not appending the `retries` list entry. The case stayed green (see F-C1). The case before the revision never checked that list either; the `refresh` cases check it.
- **R:** `status.read()` wrote `planted-by-status.txt` into the state folder.
  - Red: `` `gov dispatch status` wrote into the state folder … Left contains 1 more item ``
  - Without the plant: 20/20 passes beside 20 `while 1: pass` workers (20 CPUs). This loop ran outside heavy_slot so that it ran under the load. The busy loops were bounded by `timeout 150` and ended with `pkill -P $$`.
- **D:** `subprocess.run(["gov","plan","--ready","x"])`, planted once in `src/gov/check/planted_plan.py` and once in a sibling folder `src/gov/session_watch_extra/__init__.py`.
  - Both red: `AssertionError: {'src/gov/check/planted_plan.py': ["['gov', 'plan', '--ready', 'x']"]}` and the same for `session_watch_extra`.
  - Green after removal (`1 passed`).
- **E:** an unwired `template/governance/kernel/hooks/eighth_hook.py`.
  - Red: `…do not reach the seven kernel hooks: ['eighth_hook.py']`
  - With the parent's `hooks.jsonc` instead: red, `['context_watch.py']`.
- **F:** the "until W2-56" line appended to `template/governance/kernel/templates/role-lead.md`.
  - Red: `FAILED …[role-lead]` with `role-lead.md still carries the line … ['Run `gov accept` … until W2-56.']`; role-cto passed.
  - After revert: `2 passed`.

## Point 2: no mark added, no assertion lowered. Verdict: yes; the no-lowering case is sound for what it states, narrower than "any lowering"

- **Marks:** grepping the ticket's diff for added `skip|xfail|flaky|rerun|importorskip` finds them only inside the W2-182 folder's own text and code. The mapped cases gained none.
- **Assertions:** four assert lines were removed, and each was replaced by the decided form:
  - W1-32: the exact pin keeps W1-07's list exactly.
  - W1-18 and W2-123: `ok is True` became `ok is False` plus `REBUILD_FAILED` plus `store == semantic`. Every later check is kept, and W2-123 gains a check that the error message carries the reason.
  - W2-23: 6 became 7.
  - W2-128 row 8: the old "the line is required" check became "the line is absent", as DEC-1163 (1) decided.
  - W2-121: only an added bounded wait for the `.exit` file; the snapshot still covers every file.
- **The no-lowering case against plants:**
  - Caught: (a) `@pytest.mark.skip` on the W1-32 case; (b) a module-level `pytestmark = pytest.mark.xfail` in W2-23; (c) a second `pytest.skip` inside the W1-18 case.
  - Not caught: (d) a `pytest.skip` inside a helper the case calls (W1-32's `_commands`), which ran as `8 passed, 1 skipped`; (e) an annotated `pytestmark: list = [pytest.mark.skip]`, also `8 passed, 1 skipped`. See F-F1.
  - `gov accept` fails a line with 0 passed (`runner.py:681`), so a skip on a one-case line still fails closed.

## Point 3: only the ticket's files changed. Verdict: yes

- All 14 paths of `git diff --stat w2/integrate...HEAD` (merge base 4233668ea) are in `allowed_paths`. Nothing under `src/gov/**` changed.
- All five commits carry `Task: DAEO-5y8d`. `Implements:` uses DEC-1163, DEC-1156, DEC-1150 and DEC-105, all in `sources:`.
- The rewrites carry `Rewrite-Reason:`: DEC-1163 (6) on 6e3697785, DEC-1163 (1) on 498968115.
- f0cb5284d has `Role: orchestrator`, with no `Decided-by:` and no `Role: owner`.
- The branch's copy of the ticket differs from the main repository's only by the "Delegated (CTO…)" note.

## Point 4: the map, and E against the root. Verdict: the map is complete; E's line matches the root form; portability exit 1 is unchanged on `template/`

- **The map:** the README names every line (Success 1 to 6, Failure 1) with full node ids that collect.
  - `gov accept W2-182 --root <copy> --json` gives `pass [('success-1','pass',1,0,0), ('success-2','pass',2,0,0), ('success-3','pass',1,0,0), ('success-4','pass',1,0,0), ('success-5','pass',1,0,0), ('success-6','pass',2,0,0), ('failure-1','pass',1,0,0)]`, unmapped 0, totals 9/0/0. This matches the lead's `accept-f0cb5284d.txt`.
  - The conftest redirects only a run whose arguments are all inside the folder.
- **E against the root:** the template entry and the root entry have the same event (postToolUse), matcher (`Bash`), timeout (10) and command, byte for byte. The one difference is the hook path, `$CLAUDE_PROJECT_DIR/governance/kernel/hooks/context_watch.py` against the root's `…/template/governance/kernel/hooks/…`, which is correct for an adopted project. The template keeps `posttooluse.py` first in postToolUse, as before.
- **Portability inside `template/`:** before (10213e3bb) exit 1, after exit 1, outputs identical (`diff` gives IDENTICAL): `RULESYNC_VERSION_UNKNOWN` plus eight `TEMPLATE_COPY_MISSING`.
- **Portability at the repository root:** before, 4 findings; after, 5. The added one is `HOOKS_MATCHER_DIFFERS: hook event postToolUse: matchers ['Bash'] here, ['Bash', 'Bash'] in template/.rulesync/hooks.jsonc`. See F-E1.

## Findings

**F-E1.** After E's line, the repository-root hooks drift check reports postToolUse as drifted. The root's postToolUse holds only `context_watch.py`, because `posttooluse.py` was lifted from the root; the template now holds `posttooluse.py` and `context_watch.py`. So `tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree` is green on the parent and red on the head. In `gov check --structural` this is a notice, not a refusal. The ticket can't fix it inside its paths: the unit test and `src/gov` are both outside them. Two routes: revise the unit test as an own-branch path case (DEC-1156 (7)) with a narrow check; or ask the owner for a ticket that makes portability ignore the lifted `posttooluse.py` entry when it compares the postToolUse event.
Would reverse it: the unit test green on f0cb5284d in a git checkout of the head.
Ordinary work: yes, because every unit-suite run and every nightly hits it, with no construction.
Consequence: other (a new red test; nothing passes that should not, and no work is lost).

**F-E2.** E's Verify says portability "exits 0 on the template". Measured inside `template/`, it exits 1 both before and after the line, with the same nine findings. Those findings come from `template/` not being an adopted project: it has no tool registry and no generated `.claude` copies. I accept the CTO's reading for `template/`: the line adds no finding there. Literally, the clause is not met; and at the root the line does add one (F-E1). The clause should read "adds no finding" or be measured in an adopted bed.
Would reverse it: an owner reading that "exits 0" is literal.
Ordinary work: yes, because every run of that Verify clause shows exit 1.
Consequence: other.

**F-C1.** W2-123's revised case is green when the rebuild's `retries` list entry is not written. It reads the "last failed try's record" as the stage's status and reason, and that reason is built from the failures, not from the list. The case before the revision had the same reach, so nothing was lowered.
Would reverse it: the ticket meaning the `retries` list in the rebuild's stage.
Ordinary work: no, because the list is still checked by the W2-123 `refresh` cases.
Consequence: other.

**F-F1.** The no-lowering case does not see a skip inside a helper or fixture the case calls, or an annotated or augmented `pytestmark`. Line C (two cases) would then pass with one case skipped. This ticket's diff carries no such skip (checked by grep).
Would reverse it: a skip of that kind in this ticket's diff.
Ordinary work: no, because only this ticket's `gov accept` reads the guard, and the ticket's own diff is clean.
Consequence: other.

**F-R1.** The README's "Known reds" still says line E is red until the template line lands. That is stale since f0cb5284d.
Would reverse it: nothing; it is text.
Ordinary work: yes, because any reader of the README sees it.
Consequence: other.

Classification: 5 findings; none in scope with ordinary work yes and fails open or loses work. F-E1 needs routing before the land.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "F-C1", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": [{"id": "F-E1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F-E2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S6", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": [{"id": "F-F1", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "F-R1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```

guard_refusals:
- Writing a runner script into `$TMPDIR/aud/scripts/` with `cat >` was refused: "a reviewer or auditor writes only its own review or audit record …, its own scratch, or /tmp (DEC-953 item 2)". Two Write-tool calls to the explicit `/tmp/gov-launch-…/aud/scripts/` path were then not granted permission. I wrote no scripts after that and ran everything as inline commands.
- A portability `for` loop over the two copies was refused: "reads files whose names another command gives at run time … name the folder the listing starts at (DEC-820 (c), (d))". I re-ran it as two explicit commands naming each folder, as the message asks; both ran.

Exclusions: the unit and W2-153 comparison ran with `-m "not local_only" -k "not real and not green_here and not time_limit"`, which deselected 48 cases on each side.