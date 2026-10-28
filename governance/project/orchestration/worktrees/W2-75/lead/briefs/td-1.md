# Brief: independent test designer, W2-75 run 1

You are a fresh independent test designer (MR-3). Ticket: `DAEO-ebmh` (`W2-75`, "W2-54's green-here fixture reads the close's own check result"), profile LITE, class test-revision. You work only in the worktree `/home/usain/gov-os-worktrees/W2-75` on branch `w2/W2-75`. This ticket has no implementer: your revision of W2-54's green-here fixture and cases is the whole change. You make it, show it red first, and commit it.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ebmh','w').write('x')"` must **fail**.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must **work**.
- If (a) wrote the file or (b) failed, stop there and return (twelve fields), saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-ebmh`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-75` and `w2/W2-75`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-75/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-75/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Memory (DEC-836, DEC-860, DEC-859):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-75/src python3 -m gov.cli.main retrieve "<question>" --json`) for what you need to know before reading files at random. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal; never look for another form; search named folders instead. Count the refusals you met in your return.
- **Reads open, writes closed (DEC-820, Policy 2).** You read freely, except: (c) **the counterpart's work on this ticket**: you never read this ticket's implementation (the files `git diff --name-only w2/integrate...HEAD` names, other than your own tests; today that is none besides the ticket file and plan records); (d) **the hidden half of any evaluation set**, by whoever is measured by it: never read it. Also never: secrets and keys (never printed); the contents of the held-out qualification material under `governance/project/` (never read, print, search, diff or copy it, never type its path); never read or name the qualification oracle. Never read `.claude/settings.json`. Never write in `~/gov-os-workbench`; never list, glob or search it.
- **Writes:** only the four paths of the ticket's `allowed_paths`: `tests/acceptance/W2-54/conftest.py`, `tests/acceptance/W2-54/test_w2_54_green_here.py`, `tests/acceptance/W2-54/w2_54_support.py`, `tests/acceptance/W2-54/README.md`. Throwaway scripts for your red demonstration go only under `.gov-runtime/scratch/td/` in this worktree, never left in the tracked tree. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/**`.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag. Never `--no-verify`, never `core.hooksPath`.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508).
- **Never copy the repository or a folder of it** (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). A throwaway stand-in copies single named files, never `governance/project/`. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Inside your session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. Never `python3 -c` with braces (DEC-409): put such code in a script file under `.gov-runtime/scratch/td/`. No subagents that write. Install nothing: a tool you need is returned as a package.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` (your scratch scripts and notes, and your return), write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token; call it "row W2-L423's rule".
- **The nightly (DEC-933):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, run at most a single test file at a time, no suite; wait, checking every few minutes, and go on the moment it is gone. While `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, start no suite batch.
- **Disk and scratch budget (DEC-898):** the lead and all workers together have 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 5 GB and 250,000 files and folders.** Your temp folder is the one the sandbox sets: keep it, do not set `TMPDIR` yourself. Keep pytest's own retention (never `--basetemp`). Remove what you made in scratch when it is no longer needed. Measure your scratch (`du -s --inodes` and `du -sh` of `.gov-runtime/scratch/td/` and your temp folder) at the end and give the figures in `evidence`. If you would pass your share, stop and return PACKAGES.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need, do not work around it: return it as a package.
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status `AUTH_REQUIRED`.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` here (the lead has built this worktree's store). Never run `docs/plan/tools/validate_s1.py`.
- Your temporary folder is removed when your session ends: everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-ebmh.md` (read-only): its KPI lines, its `allowed_paths`, its sources.
- Its card: `docs/plan/WAVE_2_WBS.md` §2, "W2-75"; section 0 ("Rules for every ticket").
- Row `W2-L429` in `docs/plan/WAVE_2_LIST.md`.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-937 (this ticket), DEC-936, DEC-889 item 2 (P-IS-2 (a)), DEC-906, DEC-866, DEC-491, DEC-221.
- The existing tests you revise, as they stand: `tests/acceptance/W2-54/conftest.py` (the session fixture `gov_check_here`), `tests/acceptance/W2-54/test_w2_54_green_here.py`, `tests/acceptance/W2-54/w2_54_support.py` (what the fixture and the cases use) and `tests/acceptance/W2-54/README.md`.
- The public interface the fixture must read, as the pinned close hands it:
  - `src/gov/close/command.py`: the `--check-result` option and `CHECK_RESULT_VARIABLE` (`GOV_CLOSE_CHECK_RESULT`): the pinned `gov close` copies the pre-close gate's own `gov check --json` output byte for byte under its JUnit folder and sets the variable to that file's path in the environment of every test run of the close.
  - The orchestrator's queue runs gate (b) as `gov check --json` on the same commit after the full rebuild, stops the queue if it is not green, and passes its output with `--check-result` (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/close_queue.sh`, lines 69 to 93).
  - How W2-66's tests read the same variable: `tests/acceptance/W2-66/w2_66_support.py` and `tests/acceptance/W2-66/test_w2_66_followed_couplings.py`.
  - The `gov check --json` envelope: `{"ok": ..., "command": "check", "result": {...,"checks": [...]}, ...}` on success, with the checks under the error's details on failure (`src/gov/cli/main.py`, and how `checks_of` in `w2_54_support.py` reads it).

## Why (the failure being fixed)

W2-58's full close (2026-10-28) ran 15,672 regression cases with 0 failed and 3 errors: the three cases of `test_w2_54_green_here.py` that use `gov_check_here`, "failed on setup with Timeout (>900.0s) from pytest-timeout". The fixture runs `gov check` on this repository, about six minutes alone and over the close's 900 s per-test limit under a full close's parallel load. Every full close is refused until this merges.

## The behaviour to test and to make true (DEC-937, row W2-L429)

Each change carries `Rewrite-Reason: W2-L429` and is described in W2-54's README (a new section for this revision, dated, naming DEC-937 and W2-75; and the rows of the KPI table that change).

1. **Inside a close** (`GOV_CLOSE_CHECK_RESULT` set): `gov_check_here` reads the `gov check --json` envelope at that path instead of running `gov check`. It runs no `gov check` process.
2. **Outside a close** (the variable unset or empty: a lead's run, a plain run, the nightly): the fixture runs `gov check --json` in this worktree exactly as now, with this worktree's `src/` and the same timeout.
3. **A result that is missing, unreadable, not JSON, or not gov check's envelope with its list of checks is never read as green.** DEC-937 allows either: the fixture runs `gov check` itself, or the cases fail naming the file. **The lead's recommendation (delegated ground, DEC-937):** fail, naming the file and what is wrong with it, rather than falling back to a six-minute `gov check` under the close's load. The close itself refuses an unreadable `--check-result` before any test runs, so a bad file in a close is a real fault to surface, not to hide behind a timeout. If you choose the fallback instead, say why in the README and your return.
4. **Each of the three cases keeps its meaning and asserts nothing less:** `test_gov_check_gives_context_reproducibility_green_here` (context-reproducibility GREEN, severity hard-block), `test_gov_check_gives_core_schema_green_here` (core-schema GREEN, severity hard-block), and `test_the_w1_43_audit_report_is_untouched` (the W1-43 audit report byte for byte as at its base commit, after `gov check` too). An envelope whose check is RED (or missing) still fails the case, naming the check and its status. Where a case needs `gov check` to have run in this tree (the W1-43 case's "after gov check too"), the case's docstring and the README say how gate (b)'s run, on the same commit in the same tree just before the close's runs, stands for it. `test_the_suite_runs_this_worktree_s_code` stays as it is.
5. **No other expectation is lowered,** and nothing in W2-54 outside the green-here fixture and cases changes behaviour. Keep the fixture session-scoped, so one route serves the three cases.

Proportion (LITE, DEC-221): one test per KPI line, no combinatorial expansion. Tests that prove points 1 and 3 cheaply (a planted envelope, a missing file, a non-JSON file; and that no `gov check` process is started when the variable is set) are welcome in `test_w2_54_green_here.py`, deterministic and with no network; they must not run a real `gov check`.

## Red first (required, shown in your return)

Show that the **old** fixture (as committed at `3eef001d08dd`) with `GOV_CLOSE_CHECK_RESULT` set to a planted envelope still runs `gov check` (a spy, or the time taken), and that the **new** one does not. Use whichever is reliable inside your sandbox: for instance a spy on the process the fixture starts, or `--durations`/`--setup-show` timings of the green-here file with the variable set, old against new. A full real `gov check` takes about six minutes; inside the sandbox a real `gov check` may differ from the lead's (a private CPU embedder, a read-only code-graph cache): if it cannot run there, say so, and the lead runs the real routes outside the sandbox. Run your final tests (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-75/src python3 -m pytest tests/acceptance/W2-54/test_w2_54_green_here.py -q -p no:cacheprovider`) with the variable set to a green planted envelope, and with it set to a missing file, and report the outcomes. Also run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-75/src python3 -m pytest tests/acceptance/W2-54 --collect-only -q -p no:cacheprovider` and quote its last line.

## Commit

Commit only the paths you changed among the four allowed, in one commit, with the trailers in the final block (DEC-182, DEC-476, DEC-491), `Implements:` holding only decision ids the register holds:

    git commit -m "DAEO-ebmh (W2-75): W2-54's green-here fixture reads the close's own check result (DEC-937)" --trailer "Task: DAEO-ebmh" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-937" --trailer "Rewrite-Reason: W2-L429" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. After the commit, quote `git log --oneline -2` and `git status --short`.

## Return

In `evidence` and `tests`: the sandbox check; your commit's 12-digit hash and its trailers; the `gov.__file__` line; the red demonstration (old fixture runs gov check with the variable set, new one does not) with its figures; each test run with counts; the KPI lines with their tests; which route you chose for a bad result and why; every earlier test you rewrote, with its reason; your scratch measures; whether you used `gov retrieve`; the read refusals you met.

One message, your last, complete in itself, with no transcript. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
