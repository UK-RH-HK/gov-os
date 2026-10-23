You are a fresh independent test designer (MR-3). Ticket: DAEO-9nys (W2-67, "Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-67` on branch `w2/W2-67`. This is round 1 of the ticket, batch 1 of its test design. You write the ticket's acceptance tests from its KPI lines and sources, before the implementation, and you revise the weak acceptance cases this batch names, each shown red against a planted fault and green on the head.

## Step 0: the sandbox check (before any work; report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-9nys','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return with the twelve fields, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-9nys`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-67` and `w2/W2-67`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commits exist. Your budget is about 90 minutes: commit each finished group as you go (see "Commit"), so nothing is lost if time runs out, and say in your return what is left.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used `gov retrieve`, and for what.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return. Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one. Never read `.claude/settings.json`.
- **Policy 2 (DEC-820):** you read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path; its name may be seen); (c) **this ticket's implementation:** you never read the files `git diff --name-only w2/integrate...HEAD` names, other than your own tests (today it names none but this ticket's own records); (d) the hidden half of any evaluation set, by whoever is measured by it. Never read or name the qualification oracle.
- **Protected places:** never write in `~/gov-os-workbench` (never list, glob, search or write there); dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. No clone, copy or file of a programme under any `.gov-runtime/` folder (DEC-673).
- **No tree copying by you:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it, anywhere. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. A test that needs a repository builds a temporary one from scratch. Inside this session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never edit `.tickets/`, the decision register, the path map (`governance/project/path-map.yaml`, owner-only, DEC-757) or anything under `src/`, `template/`, `schemas/`, `docs/`.
- **Disk and inodes (DEC-898), your share:** at most 10 GB and 400,000 files and folders at any moment, in your temporary folder and this worktree's untracked files together. Keep pytest's own retention (three base folders); **never pass a per-run `--basetemp`**. Keep `TMPDIR` as the sandbox sets it (count it). The suites you touch make whole-tree copies (a run of W1-27 alone can pass 300,000 files): run only the cases you need, by node id, and measure your temporary folder (`du -s --inodes`, `du -sh`) before and after each heavy run; give the figures in your return's `evidence` line. Remove every temporary tree you made as soon as it is no longer needed. If you pass your share, stop the heavy work at once, clean what you can and return.
- **The machine:** one full run of these suites drives the load high. Before any run of more than a few cases, wait while the 1-minute load is above 20 (`until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done`). Never run with `-x`; never run a whole folder of W1-07, W1-25, W1-26 or W1-27 at once.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try.**
- You never ask or notify the owner (no question box, no `owner-ping`); a package comes back in your return.
- A KPI line that is ambiguous, or a test you dispute, is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## What you read

- The ticket file `.tickets/DAEO-9nys.md` (read-only): its KPI lines, its `allowed_paths` and its sources. Its card: `docs/plan/WAVE_2_WBS.md` §2, the W2-67 card (lines 1150 to 1185).
- The sources: DEC-889 (item 7), DEC-892 (item 1), DEC-898, DEC-899, DEC-904 in `docs/DECISION_REGISTER.md`; DEC-456 (moved and old paths), DEC-448, DEC-385 (held-out copies), DEC-491 (Rewrite-Reason), DEC-866 (supersession: a test that enforces a superseded decision is revised with `Rewrite-Reason: <the new decision>` and lowers no other expectation).
- Lens I: `docs/assessment/2026-10/I-SYNTHESIS.md` §4 (the W2-67 block, about line 281), §5.2 (the rows for W1-07, W1-25, W1-27), P-IS-7; `docs/assessment/2026-10/I4-records-plan-rest.md` §2.1 and §2.2 (every row for `test_w1_27_*` and the W1-07 copy-race rows), F1, F5; `docs/assessment/2026-10/I3-retrieval-context-resume.md` F9 (the copy race). Those rows name, for each weak case, why it cannot fail and the planted fault (P27-n) that lens I4 used to show it.
- The existing acceptance suites as they stand on `w2/integrate` (identical to this branch's head today): `tests/acceptance/W1-07/`, `W1-25/`, `W1-26/`, `W1-27/`, and W1-28's fixture-copy check (`tests/acceptance/W1-28/test_w1_28_fixture_copies.py`, `w1_28_copy_check.py`), which runs every copier with a synthetic root and must stay green.
- The public interfaces the tests work with: the `gov doctor` and `gov rebuild` commands and their JSON envelopes (`docs/interfaces/API-0002.yaml`), git, and pytest's own temp-folder behaviour (`tmp_path`, `tmp_path_factory`, its retention of three base folders, `--basetemp`). You read no private part of an implementation to learn what a test should expect.

## The behaviour to test (batch 1)

The ticket's KPI lines, in round 1's scope (the owner's overlap rule, DEC-904 item 5: W1-30, `tests/unit/close` and W2-50 are later rounds and are not touched):

1. **Per-test copies do not race git's garbage collection** (KPI 1; I3 F9, I4 F5, I4 §2.1). Every per-test copy that the suites W1-07 (its shared support module), W1-25, W1-26 and W1-27 make of the working tree either commits with git's automatic gc switched off (`gc.auto=0`) or copies the working files without `.git`. A planted source tree of about 7,000 objects or more runs every copying case of those suites green in parallel. Today a copied tree past about 6,700 loose objects starts git's background gc at its first commit, whose packing races the next copy of that tree's `.git` (`shutil.Error: … .git/objects/NN: No such file or directory`); it errored W1-25's and W1-07's cases in refused closes. Your tests show this red on the head, for each copying fixture or helper of those four suites, with a planted tree of at least 7,000 objects. W1-28's check shows how every copier can be run with a synthetic source root; a copier that cannot be pointed at a planted tree is itself a finding to state in the README and your return. If you judge that "runs every copying case green in parallel" needs a nested run of the copying cases, bound it (one or two workers, a named small selection per suite, measured), and say why in the README.
2. **W1-27's old-path case gets a project of its own** (KPI 1; I4 §2.1, the row for `test_w1_27_path_compliance_r2.py::test_old_path_inside_its_new_path_is_not_stale`): it keeps its rule (DEC-456 point 3) but builds a small committed project of its own instead of a whole-tree copy, so its result no longer depends on every tracked file's text. Rewrite-Reason: the result depends on every tracked file's text.
3. **Temp folders (KPI 4; DEC-898):** the suites keep pytest's own retention of three base folders, nothing passes a per-run `--basetemp`, and a full run leaves at most three base folders behind. The ticket's paths name a temp-folder rule in the root `tests/conftest.py`, which does not exist on the base. Test what can be observed from outside: a run of the repository's suites leaves at most three of pytest's base folders under its `TMPDIR`, even when more were there before; nothing in the repository's pytest configuration or in round 1's folders passes `--basetemp` or changes the retention count. If you find the KPI ambiguous about what a run given a per-run `--basetemp` must do, return that as a package with your recommendation rather than guess. Any nested pytest you start is bounded (one worker, a tiny selection) and uses no per-run `--basetemp` of its own.
4. **W1-27's weak cases, `gov doctor`'s 40 first** (KPI 5; P-IS-7 (a); I4 F1; the I-SYNTHESIS §5.2 row for W1-27): adoption ×3; `test_w1_27_doctor.py` ×8; `doctor_r5`'s stale-path case; `doctor_r7`'s home-tool sha256 case; drift ×6; held-out ×2; `isolation_r2`; path compliance ×3; path compliance r2 ×3; rebuild ×5; rebuild r2, r3, r4, r8; recovery check r2 ×3 (I4 §2.2 names each, with why it cannot fail and its planted fault). Also `test_rebuild_does_not_silently_drop_lexical_tables` (a duplicate: make it assert the planted row's fate). Each revised case:
   - reads doctor's or rebuild's structured result (the value of the key it claims, not the key's name or a word anywhere in the output);
   - is first shown **red against a planted fault** that the case claims to catch (lens I4's P27-n where it names one), then **green on the head**;
   - lowers no expectation, and keeps the case's name unless a name states a removed rule;
   - is committed with a `Rewrite-Reason:` trailer that names why it was weak (or the newer decision, under DEC-866).
   **Planting a fault:** you may not write `src/`, and you may not copy the tree. Plant each fault in a throwaway that the run picks up and that leaves the tracked tree untouched (for example a small module in your folder under `.gov-runtime/scratch/td-1/` placed first on the child process's import path, that imports the real package and replaces one behaviour), and record each plant (the fault in words, how it was planted, the command, the result, a JUnit XML) under `/home/usain/gov-os-worktrees/W2-67/.gov-runtime/scratch/td-1/plant/`. A case you cannot show red against any plant without writing `src/` is named in your return, with what you tried; it is not committed as revised.
   A case whose honest revision is red **on the head** because the code itself is wrong (for example a doctor check that never reports what it should) is not committed red: name it in your return with the evidence, as a finding for the ticket that owns that code (W2-22 holds doctor's path matcher, P-IS-9).
   The unit case `tests/unit/doctor/...::test_check_isolation` is not in this ticket's paths: leave it.

## What you write

- Revisions only inside `tests/acceptance/W1-27/` (the ticket's declared `acceptance_tests.path`). The new KPI tests of items 1 and 3 also go in `tests/acceptance/W1-27/`, in new files whose names start `test_w2_67_`, with a README of their own, `tests/acceptance/W1-27/README-W2-67.md`, that maps each KPI line of this batch to its tests, gives each test's expected red reason on the head (or "green on the head: a guard" where that is what it is), and for each revised case its planted fault, its red and green evidence, and its Rewrite-Reason. Add a short section to `tests/acceptance/W1-27/README.md` pointing to it.
- **Not in this batch:** the copying fixtures and support modules themselves (`tests/acceptance/W1-07/w1_07_support.py`, the W1-25 and W1-27 fixture files `conftest.py` and `*_support.py`, W1-26's support module), `tests/acceptance/W1-26/**`, `tests/acceptance/W2-02/**`, `tests/unit/**`, `tests/conftest.py`. You do not change how any suite copies the tree: your tests show the copies red; the fix is another step's. Your new tests may import those support modules and call them; they never edit them.
- A shared file is touched only on lines of your own. No throwaway implementation is left in the tree.
- FULL proportion: thorough on every KPI line of this batch, its success and its failure; no combinatorial expansion beyond what a KPI demands. Deterministic, no network. Tests that need a repository build a temporary one. Mark dev-tier tests `local_only`.
- Red first: run your new tests, by node id, to the end; they fail for the reason the README states. Run every revised case on the head (green) and under its plant (red).
- Before your last commit, run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` once: it must end with no collection error; quote its last line.

## Commit

Commit only your test paths, a group at a time (the doctor revisions with one reason, the old-path case, the new KPI tests and their README, …), with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" -- <your paths> --trailer "Task: DAEO-9nys" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-889, DEC-898" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

A revision commit also carries `--trailer "Rewrite-Reason: <reason>"`. Before each commit check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. After each commit, check `git log --oneline -2` and `git status --short`.

## Return

Your last message, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Put in it: the sandbox check (step 0) first in `work_completed`; every commit's hash with its trailers; the test count; each KPI line with its tests; the red reason as you saw it for each new test; for each revised case, its plant, red and green; every case you could not revise and why; the `gov.__file__` line; the collection line; your scratch figures; the read refusals met; whether you used `gov retrieve`; any package.

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

Refused twice for the same call: stop and say so; no third try.
