# W2-90b (DAEO-nqa2): merging `w2/integrate` into `w2/W2-90b` conflicts in three acceptance files

Read only, 2026-11-11 ~20:10 UTC. `git merge-tree --write-tree --name-only w2/W2-90b w2/integrate` (output in `merge-tree.out` beside this file)
exits 1: **three content conflicts, no other.** Nothing was merged, committed or written in the worktree.

| | |
|---|---|
| branch head | `73c18fea1e1f` (a records commit, `CP-DAEO-nqa2-0004`); verified head `d2408361d185`; clean |
| integrate head when measured | `9d288f1b1c49` |
| merge base | `8723754f3fec`; the branch is 6 ahead and 1,860 behind |
| overlap | six test files changed on both sides; three merge without a conflict, three conflict (below) |

## Class of each file

All three are `tests/acceptance/**` files. `governance/project/operator/class-rules.yaml` has no row for them, so no ACT class applies: the
rule is the guard's rule 1 (only the test designer writes acceptance tests) and DEC-1052 / DEC-1031 item 3 (a restore or a conflict resolution in
`tests/acceptance/` is a test designer's, and the merge carries `Role: independent-test-designer`, never `Role: orchestrator`). **All three need a
test designer** (Opus at high; the ticket is LITE, class C2). All three are inside the ticket's `allowed_paths`, so no path is added.

| File | Conflict | Class of the fix |
|---|---|---|
| `tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py` | one hunk, the function `test_the_launcher_starts_no_session_for_a_role_that_is_not_a_worker` (this branch moved it to the `kernel_launch` fixture; integrate rewrote it for DEC-1088 (5)(a) and added a `ready` parameter) | designer; also a second edit outside the hunk (below) |
| `tests/acceptance/W1-47/w1_47_support.py` | one hunk in `installed_environment` (both sides made the stand-in home hold a pinned `gov`) | designer; take integrate's side |
| `tests/acceptance/W2-90/w2_90_kernel_wiring.py` | one hunk in `install_gov_for` (the same fix, written twice) | designer; take integrate's side |

## The resolution, file by file

**1. W1-47 `w1_47_support.py`, `installed_environment` (take integrate's side).** Integrate's commit `3a1be7726` (W2-20 D-10) added
`plant_pinned_gov(home)` (writes `<home>/.local/bin/gov`, its first line naming this interpreter, and the path file in that interpreter's user
site). This branch's `591199ea1` wrote the same thing as `install_editable_gov(home)` with the same effect. Keep integrate's hunk: the docstring
sentence "The pinned lines find the stand-in home's pinned ``gov`` (``plant_pinned_gov``)" and the call `plant_pinned_gov(sandbox.home)`. Drop this branch's
revised paragraph and its call `install_editable_gov(sandbox.home)`. Then `install_editable_gov` and `EDITABLE_PYTHON` (merged in from this branch, further
down the file) are called by nothing: remove both, or leave them with a one-line comment that they are superseded; **never delete a case**.
Nothing else in the file conflicts.

**2. W2-90 `w2_90_kernel_wiring.py`, `install_gov_for` (take integrate's side).** Integrate's `5b6873b3a` made `install_gov_for` write the path file for `python3` and then call
`pinned_support.plant_pinned_gov(home)` (with `import w1_47_support as pinned_support`, merged cleanly above the hunk). This branch's `591199ea1` wrote the
script itself and looped over `(EDITABLE_PYTHON, "python3")`. The two give the same files: `plant_pinned_gov` covers the interpreter's user site, the `python3`
loop covers the other. Keep integrate's whole hunk (its docstring and body); drop this branch's. `EDITABLE_PYTHON` (line 113 of this branch's file) is then unused:
remove it with the hunk. Keep this branch's other additions to the file (the template readers, `w1_46_project`, `w2_59_worker_project`, `copy_project`, ...): they do not conflict.

**3. W1-33 `test_w1_33_guard_and_launcher.py`, the hunk.** Keep integrate's decorators and helper (`_ready_list_without`, the two `parametrize` lines, merged cleanly above the hunk)
and integrate's body, with this branch's fixtures:

```
def test_the_launcher_starts_no_session_for_a_role_that_is_not_a_worker(kernel_launch, kernel_project, role, ready):
    """<integrate's docstring, unchanged>"""
    launch, project = kernel_launch, kernel_project
    ticket = support.w47.TICKET_OF[role]
    if ready != "no ready list":
        _ready_list_without(project, ticket)
    result = launch(role, ticket)
    launch_support.assert_refused(result, *support.LEAD_REFUSAL_WORDS)
    said = result.run.stderr + "\n" + result.run.stdout
    assert ticket in said, f"the refusal does not name the ticket {ticket}\n{result.describe()}"
```

**A second edit that git does not flag, and without which two cases go red:** integrate's `conftest.py` (`e66c69c45`, W2-20 D-10) made W1-33's `launch` fixture plant an open
resource gate (`support.plant_open_gate`, W2-20 S19, DEC-1088 (5)(b)) and pass its readings in the environment, because every `gov launch` now passes the gate. This branch's
`kernel_launch` fixture (in the test file, not the conftest) calls `launch_support.launch(...)` and plants no gate, so `test_the_launcher_gives_the_role_an_empty_network_profile` and the rewritten
case above would be refused by the gate, not by what they test. Change `kernel_launch` the way integrate changed `launch`:

```
    gate = support.plant_open_gate(kernel_sandbox.home, kernel_sandbox.elsewhere / "gate-readings")

    def _launch(role, ticket=None):
        ticket = ticket or launch_support.TICKET_OF.get(role) or w47.TICKET_OF[role]
        before = len(launch_support.calls(cli))
        env = {**launch_support.gov_environment(kernel_project, kernel_sandbox, cli), **gate}
        run = launch_support.run_gov(kernel_project, kernel_sandbox, "launch", role, ticket, cli=cli, env=env)
        return launch_support.Launch(run, tuple(launch_support.calls(cli)[before:]))
```

(update its docstring: "the resource gate is planted open, W2-20 S19".) The `launch_support.run_gov`, `gov_environment`, `calls` and `Launch` names are the ones integrate's conftest uses.

## After the three files

- **The three files that merged without a conflict** (`W2-54/test_w2_54_sandboxed_worker.py`, `W2-59/test_w2_59_hook_lines_worker_env.py`, `W2-90/README.md`) change in different places on the two sides
  (integrate: W2-54 plants W1-46's open gate readings, W2-59's docstring; this branch: the kernel's wiring). Nothing to resolve; **the scoped run is their check.**
- **Prose to correct:** `tests/acceptance/W2-90b/README.md` (lines 28 and 36 name `install_editable_gov`: say `plant_pinned_gov`, and re-measure the "after" row if the helper's name is the measured row's label) and the "next round"
  paragraph this branch added to `tests/acceptance/W2-90/README.md` (it says `install_gov_for` writes the script; since integrate's fix it calls `plant_pinned_gov`; one sentence).
- **Other suites this branch revises read support files that integrate also changed** (`w1_05_support.py`, `w1_46_support.py`, `w2_59_support.py`, `w2_65_support.py`, `w2_54_support.py`,
  W1-33's `conftest.py` and `w1_33_support.py`). They merged without a textual conflict. A red in W1-05, W1-33, W1-46, W2-54, W2-59 or W2-65 after the merge is the designer's to read
  against those files, not a reason to lower anything (ticket S5 and F2: no case deleted, skipped, xfailed or weakened).
- **Commit:** the merge commit carries `Task: DAEO-nqa2`, `Role: independent-test-designer`, `Rewrite-Reason: DEC-953 item 2 (the merge keeps integrate's pinned gov and gate, W2-106 and DEC-1088 (5))`, and the ticket's own `Implements:`
  ids (DEC-953, DEC-965, DEC-970, DEC-906, DEC-999). The designer edits the three files (and the two README paragraphs) and runs no git write command; the lead stages and commits, as W2-11's brief does for its W1-35 conflict.
- **If the guard refuses the designer's launch with a merge in progress:** the lead returns PACKAGES; the CTO then makes the merge outside the worktree's sandbox and starts the designer by hand.

## Found while reading, not a conflict: `gov accept W2-90b` cannot measure this ticket
`gov.accept.runner.parse_map` (the pin's own reader, run read only on this branch's `tests/acceptance/W2-90b/README.md` at its head, `parse_map_probe.py` beside this file) reads **0 lines**:
the README's tables have a `KPI line` column but no `Test` or `File` column of backticked items, so `gov accept` would answer `ACCEPT_NO_MAP`. And the ticket's own folder
`tests/acceptance/W2-90b/` holds only the README (no case; the ticket is judged on the suites it revises, DEC-892), so even a readable map would find nothing to run there. The land brief therefore
leaves `gov accept` out and judges the ticket by the scoped verification (`lead_verify`) and the README it carries; the same probe on W2-81's README at its head reads all 17 lines (S1 to S12, F1 to F5). **For the CTO:** a formal close of W2-90b must not wait on `gov accept`; if it must,
a designer round writes a map in the form the reader takes (a KPI column and a Test column of full node ids, as W2-81's second pass did) and the folder's cases would still be none.

## Costs
One designer round, about 20 to 40 minutes and $3 to 5 at Opus high (E: this ticket's first designer round was one round, four commits). Not resolving costs the landing: the branch cannot merge to integrate with these three files conflicted, and W2-90c waits on W2-90b (DEC-1016).
