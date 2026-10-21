You are a fresh independent test designer (MR-3). Ticket: DAEO-xxgp (W2-48, "Test-result cache at close and in the leads' runs, glued to pytest-testmon, subprocesses seen, a nightly full run"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-48` on branch `w2/W2-48`. This is a test design batch on an existing acceptance suite (`tests/acceptance/W2-48/`, written by earlier test designers): you add the proving cases for four fail-open behaviours the lead found in the built cache, given to you below as described behaviours (DEC-136), and you show them red against the code as it stands.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-xxgp','w').write('x')"` must fail.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return, saying which.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-xxgp`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-48` and `w2/W2-48`). If anything differs, stop and say so.
- **DEC-732, the code under test (word for word from the lead's brief):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Your tests, run from this worktree, must exercise this worktree's code; the README already says how, keep it true.
- **Memory used (DEC-836, DEC-859, DEC-860).** For what you need to know about the repository, use `gov retrieve` before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m gov.cli.main retrieve "<question>" --json` (this worktree may have no store; if it answers `STORE_MISSING` or a facet is unavailable, say so and read the named files). Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve` and for what.
- **Reads (DEC-820, Policy 2).** You read freely: the whole repository, git history, other worktrees, installed packages. Four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (c) **the counterpart's work on this ticket: you never read this ticket's implementation**, by any tool (no cat, grep, glob, git show, git diff, copy or import-and-inspect of it): the files `git diff --name-only w2/integrate...HEAD` names other than `tests/acceptance/W2-48/**`, which today are `src/gov/testcache/**`, `src/gov/close/cache.py`, `src/gov/close/command.py` (its changes on this branch), `tests/unit/testcache/**`, `docs/research/W2-48-cache-choice.md` and the ticket's checkpoint record. You may run the commands the suite already uses and see their outputs, as any user would; (d) the hidden half of any evaluation set, by whoever is measured by it.
- **Read refusals (DEC-849).** Until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count every refusal you meet and list them in your return.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. The Bash tool kills a foreground command after 10 minutes: run the W2-48 suite with `run_in_background: true` and `timeout: 7200000`, its output and exit code to files under `/home/usain/gov-os-worktrees/W2-48/.gov-runtime/scratch/test-designer/` (shell redirects with literal paths), and wait for the exit-code file with `until [ -s <file> ]; do sleep 20; done` in foreground calls of under 10 minutes, repeated. Never end your session while a run of yours is running. Return only after your commits exist. Commit your tests before you run any long suite.
- **The machine (DEC-847, DEC-780).** While the file `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, start no suite run until it is gone (`until [ ! -e <that file> ]; do sleep 60; done`). Before each suite run, wait while the 1-minute load is above 20 (`until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done`).
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, here or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder (you should need none).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it). A test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673). Never touch this tree's own cache files: every planted change happens in a temporary repository your test builds.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents. Install nothing: a tool you need is returned as a package. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Nobody runs `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree (your tests run `gov close` only inside temporary repositories they build). Never run `gov rebuild --no-embeddings`.
- The git hooks are uninstalled until W2-08. Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. On an authentication or access error, stop and return.
- You never ask or notify the owner directly (DEC-850, DEC-855): a question comes back in your return as a package.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The existing suite, `tests/acceptance/W2-48/` (yours to read and extend): its README (the KPI map, the interface forms the earlier designer settled, the planted project), its support module and conftest. Keep its forms; extend them only where the new cases need it, and say so in the README.
- The ticket file `.tickets/DAEO-xxgp.md` (read-only): its KPI lines and sources.
- In `docs/DECISION_REGISTER.md`: **DEC-876** (the reason for this batch; condition 1 above all), DEC-875, DEC-852 (item 1, subprocesses; item 3, the nightly), DEC-843, DEC-726, DEC-491 (rewrites after implementation), DEC-866 (supersession), DEC-221, DEC-462. Also the owner's package that DEC-876 answers: `governance/project/orchestration/packages/P-W2-48-5.md` (name the file; do not list the folder).
- `governance/project/briefs/JUDGEMENT.md` (name the file), the judgement rules the lead judged these findings by.
- The path map's new `test_inputs` key in `governance/project/path-map.yaml` (name the file).


## The task: four fail-safe cases of DEC-876 condition 1, found after the widenings were built

DEC-876 condition 1 (owner): **fail safe** — anything the cache still cannot see stays "always run"; and each widening is proven by a test in which a change reached only that way invalidates the cached result. The implementation now measures Python children whatever their environment and keys `git` by its version, and the suite's eight widening cases pass. The lead then probed the built cache with `python3 -m gov.testcache run --json tests` in small temporary projects, and found four ways in which **a change reached only that way leaves a stale pass reused**: in each, the third run below reported `ok: true` with every test `reused`, although the planted change makes the test fail when it runs.

The lead's probe, in each case: run 1 fills the cache; run 2 with nothing changed reuses; then a commit plants the change; run 3 should re-run the test (and so report its failure), and instead reuses it.

1. **A file a Python child reads.** A test starts a Python child (here with its own environment) that imports a project module and reads a file of the project that is neither code nor a declared input (`notes.md` at the project's root; the project declares no `test_inputs`), and the test asserts on what the child printed. The same read made by the test's own process already makes that test always run ("it opened notes.md, outside the declared inputs"); made by the child, it is not seen, and after `notes.md` changes the test is reused.
2. **`git` run on the project's own repository.** A test runs `git` with its working directory inside the project (for example `git rev-list --count HEAD` in the project's root) and asserts on the output. `git` is a known program keyed by its version, but what it read (the project's own history and working tree) is not seen: after a new commit the test is reused.
3. **A Python file of the project read as text.** A test opens a `.py` file of the project as text (not importing it) and asserts on its content (for example, that a word does not appear in it). After a change to that file in a part no test executes (a new function added), the test is reused.
4. **A listing of a project folder.** A test lists a folder of the project (`os.listdir` of a package folder) and asserts on the names. After a file is added to that folder, the test is reused.

These hold whether the view is taken by the test's own process or by a Python child it starts; the four above are the forms the lead saw. They are ordinary in this repository's own suite (tests over the live repository's history, source scans, folder listings), so each is an honest-agent case that fails open (JUDGEMENT.md's two questions: yes and yes).

Write, in a new test file of the suite, one proof per case, each in a temporary repository built from scratch (as the suite's other cases are): with the change planted in a commit, the next run **runs the test again and reports its failure** (exit 3 and the test's result `failed` in the record, never `reused` or `passed`). Where a case can honestly stay reusable when nothing changed (for example a child that reads a file of the declared `test_inputs`: reused when unchanged, re-run when that file changes), add that counterpart only if it shows the rule is not "everything always runs"; DEC-221 still holds: no combinatorial expansion. Also cover, once, that `git` run on a temporary repository the test builds (outside the project) stays reusable when nothing changed, so that widening two is not lost by the fix (an existing case may already show this: if so, name it and add nothing).

The cache may meet each case either way: by seeing the view (and re-running the test when what it saw changed) or by making the test always run. **Your tests must not decide which** (both are acceptable outcomes): assert that the stale pass is never reported, and say in the README which outcomes you accept per case.

Every assertion's failure message must say, in plain words, what behaviour was expected and through which interface (the command, the record field), because the engineer never reads your tests or README (DEC-820 (c)) and learns from their names, results and failure messages only.

Commit:

    git commit -m "W2-48 (DAEO-xxgp): four fail-safe cases of DEC-876 condition 1 (a child's read, git on the project, a source read as text, a listing), red" --trailer "Task: DAEO-xxgp" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-726" --trailer "Implements: DEC-876" --trailer "Rewrite-Reason: DEC-876" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After the commit, check `git log --oneline -2` and `git status --short`.

## What you write

- Only inside `tests/acceptance/W2-48/`. No other ticket's tests are touched; no earlier case of this suite has its expectation lowered. The README maps each new case to DEC-876 condition 1 and the KPI lines (KPI 3, subprocesses; KPI 4, inputs that cannot all be seen; failure KPI 1), with its expected red reason.
- Red: run `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m pytest tests/acceptance/W2-48 -q -p no:cacheprovider -rs` to its end (never `-x`), in the background as above. Report, per new case, pass or fail and the failure reason (the four proofs are expected red against the code as it stands); report any earlier case that fails, with its message (one earlier case, about the research record's time-saved figure, is expected red: the figure is still to be measured).
- Then `PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` must end with no collection error; quote its last line.
- An ambiguous point or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

In the fields, give: the sandbox check's result (first); your commit's hash; the cases added, by name, each with its expected red reason and its result as you saw it; the forms you settled; the `gov.__file__` line; the collection check's last line; whether you used `gov retrieve`; the read refusals you met.

