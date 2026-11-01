# Brief: independent test designer, W2-96 (DAEO-ouet), run 3: review 4's W1 cases (DEC-987)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-96-tests` on branch `w2/W2-96-tests`. You add two cases to the ticket's acceptance tests, from review 4's finding W1 given below as a described behaviour (DEC-136), and you show them red. Then you try once to remove an empty leftover folder in the ticket's worktree.

**Where things stand.** The suite in `tests/acceptance/W2-96/` has 106 cases (runs 1 and 2, review 3's), marker `qzv96leak`, all green on the ticket's head. The engineer's implementation is in this worktree's tree (this branch was made from the ticket's head `943543cea0e8`); you still never read it (Policy 2 (c) below), but your red run executes it. Review 4 probed it and found W1. The owner decided (DEC-987, read it in `docs/DECISION_REGISTER.md`): the two cases first, red on the head; then an engineer fixes it; then a third review of that change alone. The lead merges your branch after you return.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (never delete such a file; name it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-ouet`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-96-tests` and `w2/W2-96-tests`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-tests/src` set **per command** (never in a session's `--settings` env). Your tests, once merged into `/home/usain/gov-os-worktrees/W2-96` and run from there, must exercise that tree's code: run `gov` as `python3 -m gov.cli.main` with the `src/` of the repository that holds the test file (found from the test file's own location), never a bare `gov` from PATH. The suite's support module already does this; keep it so.
- **Policy 2 (DEC-820):** reads are open, writes are closed. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path, never read or name the qualification oracle); **(c) this ticket's implementation: you never read the engineer's work** — no file under `src/gov/accept/`, no `tests/unit/accept/test_w2_96*` file, and not `src/gov/check/commands.py` as it is on `w2/W2-96`, in any worktree or branch (this one included), by any tool, and nothing `git diff --name-only w2/integrate...w2/W2-96` names outside `tests/acceptance/`; (d) the hidden half of any evaluation set, by whoever is measured by it. You read the specification, the KPIs, review 4's finding as given here, your own suite, and the existing code as it stands on `w2/integrate` (`git show w2/integrate:<path>`).
- **DEC-849:** until W2-58 lands the guard still refuses some reads (searches starting at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead, and count the refusals you met in your return. Never read `.claude/settings.json`.
- **Retrieval (DEC-836, DEC-963):** use `gov retrieve` for what you need to know before reading files at random, **from the integration branch's store only**: `cd /home/usain/gov-os-worktrees/W2-00-store-a && timeout 90 gov retrieve "<question>" --json` (a read; it holds `w2/integrate` as of its last refresh). Known: inside the sandbox that call can hang on its embedder's network call; try it once, and if it times out, say so and read named files instead. Never retrieve from `/home/usain/gov-os-worktrees/W2-96`'s store. **Drop unread any result under `src/gov/accept/` or `tests/unit/accept/`, and name any such result you were served in your return (P-R1, DEC-820 (c)).** Never one giant query or context (DEC-860): a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). A test that needs a repository builds a temporary one from scratch. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only. No clone, copy or programme file under any `.gov-runtime/` folder. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at literal absolute paths; put anything longer in a script file in your session's own temporary folder (the one the launcher set; `.gov-runtime/scratch/td/` is refused to this role) and run it by its literal path; a command with `$TMPDIR` in it is refused, so write the path out. Never `cd` into a subfolder of the repository (the sandbox leaves a `.claude/` folder there): use paths from the worktree's top. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. No subagents that write. Install nothing (an install you need is a P1 escalation in your return).
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Budget (DEC-898):** your share is 3 GB and 150,000 files and folders outside the tracked tree. Keep pytest's own temp retention (never a per-run `--basetemp` for your own suite runs); run with `-o tmp_path_retention_policy=failed`. Your temp folder is the one the launcher set; clean up what you make as you go; measure it at the end (`du -sh` and `du -s --inodes`) and give the figures.
- If the guard or the sandbox refuses something you need, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try (AR-6).**

## The behaviour to test: R16 (review 4's W1; DEC-987)

R1 to R15 still hold; where they differ, this holds.

- **R16 (no process of the run outlives `gov`; nothing of the run appears in the caller's `TMPDIR` afterwards).** Before its clean-up, in every path (a pass, a failure, a stop by SIGINT, SIGTERM or SIGHUP), `gov accept` stops every process the run started, **whatever its session or process group** (processes a test started in a session of its own, and their own children, included), and waits until none is left. Only then does it remove its private folder. So once `gov` has ended, no process of the run is alive, and nothing of the run (no folder, no file, no name) appears in the caller's `TMPDIR` later, not even seconds afterwards. KPI 2's "or any file it leaves" covers what appears after `gov` ends. Everything else stays as before: the exit codes (0, 3, 128 plus the signal), the envelope, the three signals held during the clean-up, no marker anywhere.

How review 4 reproduced W1 (a described behaviour; red on the head in 23 of 24 runs there):
- An outer planted test runs a nested `gov accept` on a nested planted project, started in a session of its own, with its `TMPDIR` inside the outer test's temporary folder: the form in which this suite's own harness runs every planted run. The nested test sleeps 1 to 3 s (or writes), then ends.
- A stop reached the outer `gov` alone while the nested pytest was still running: SIGTERM, Ctrl-C (SIGINT) or coreutils `timeout`. The outer `gov` ended with 143 or 130 and the given `TMPDIR` empty at that moment.
- 2.4 to 3.4 s later, the given `TMPDIR` held 6 entries: `gov-accept-XXXX/tmp/pytest-of-<user>/pytest-0/<the outer test's name>/given-1`. The nested pytest's report writer creates its report's missing folders when it ends; the nested `gov` then removed only its own private folder.
- A planted test that starts its nested run in a session of its own and **does not wait for it**, with no stop: the outer run passed (exit 0), and afterwards the same 6 entries appeared (3 of 3).
- A stop sent to the whole process tree at once left nothing (0 of 16): such a form is not the case to test.

## What you write

- Only inside `tests/acceptance/W2-96/`: one new case file (say `test_w2_96_at_review_4.py`), its rows in the README's map (in the map forms the suite uses; under R8 every case must also be mapped), and support code where needed. **Two cases, in the harness's form above:**
  1. **The stopped run:** SIGTERM (or SIGINT; say which and why) to the outer `gov` alone while the nested pytest is still running. Expected: exit 143 (or 130), and the given `TMPDIR` empty both when `gov` ends **and again after the nested run would have ended** (wait long enough past the nested test's sleep that the head's leftovers have certainly appeared; state the wait and why), no marker anywhere, and no process the run started still alive once `gov` has ended (find them by something the planted run carries, for example a unique token in their environment or command line; never by a name a passing implementation might also use).
  2. **The run that does not wait:** a planted test starts its nested run in a session of its own and returns without waiting; no stop. Expected: pass, exit 0, the given `TMPDIR` empty when `gov` ends and again after the nested run would have ended, and no process of the run alive once `gov` has ended.
- It is a race: repeat or time each case so that the head fails it reliably (aim for a red in nearly every run), while the whole W2-96 suite stays well under eight minutes. The nested test's sleep must be long enough that the stop lands while it runs, even under load (the machine's load is often 20 to 60 on 20 processors).
- Revise no earlier case. Keep the cases deterministic in outcome, no network. Any processes your cases start must be gone when each case ends, pass or fail (kill them in the case's own clean-up), so a red run leaves no orphan behind.
- **Red first:** this branch carries the head's implementation, which lacks R16. Run the whole W2-96 folder to the end: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-tests/src python3 -m pytest tests/acceptance/W2-96 -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line`. Say which new cases are red and why (the README states each expected red reason), that the other 106 still pass, and run the new file a second and a third time to show the cases are red reliably.
- An ambiguous point or a dispute with R16 is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

One commit, only your test paths, trailers in the final block (the git hooks are uninstalled; never `--no-verify`, never `core.hooksPath`; check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file):

    git commit -m "W2-96 (DAEO-ouet): review 4's W1 cases for gov accept, no process of the run outlives it (DEC-987)" --trailer "Task: DAEO-ouet" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-987, DEC-959" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

`Implements:` holds only ids the register holds (DEC-927). Then `git log --oneline -2` and `git status --short`.

## After the commit: one try at the leftover folder (P3, DEC-987)

An empty, untracked folder `tests/acceptance/.claude/.cc-writes/` (and its parent `tests/acceptance/.claude/`) sits in the ticket's worktree `/home/usain/gov-os-worktrees/W2-96`, left by a reviewer's sandbox in run 1. A previous designer's call was refused by a permission prompt because it joined `rmdir` with `; echo`. Do exactly this:
1. `ls -la /home/usain/gov-os-worktrees/W2-96/tests/acceptance/.claude/.cc-writes` (report; if it holds anything, stop and remove nothing).
2. If it is empty, run exactly `rmdir /home/usain/gov-os-worktrees/W2-96/tests/acceptance/.claude/.cc-writes` with nothing else in the call. If that worked, run exactly `rmdir /home/usain/gov-os-worktrees/W2-96/tests/acceptance/.claude`.
3. One try each. If refused (the sandbox, the guard or a permission prompt), take it: never another form (no `rm`, `python3`, `find -delete`), and quote the refusal word for word in your return.

## Return

Your last message, complete in itself. Refused twice for the same call: stop and say so. The twelve fields come first, each as a labelled line, any payload after them:

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

In `evidence` also: the sandbox check, your commit's 12-digit hash, the test counts, the red reasons as you saw them, whether you used `gov retrieve` and any result under the implementation paths you were served, the leftover folder's removal (done or refused, with the refusal's text), the guard read refusals you met (count), and your scratch measure. After the twelve fields, a `brief_gaps:` section (one line per thing you had to discover that this brief did not tell you, with minutes it cost, or `brief_gaps: none`).
