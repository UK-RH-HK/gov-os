You are a fresh independent test designer (MR-3). Ticket: DAEO-5j8b (W2-58, "Policy 2 in the guard and the launcher: reads open, four refusals"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-58` on branch `w2/W2-58`. The ticket is implemented and its acceptance suite `tests/acceptance/W2-58/` (576 cases, written by earlier test designers) passes. An independent review then found behaviours the suite misses, described below (DEC-136). Your job: add acceptance cases for them to this suite, and show the new cases red against the current code.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-5j8b','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (status: STOPPED_SANDBOX), naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-5j8b`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-58` and `w2/W2-58`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Policy 2 (DEC-820), reads open, writes closed:** you read freely (the whole repository, git history, other worktrees, what your retrieval returns), except four things: (a) secrets and keys, never printed; (b) the held-out qualification material's contents (its file names may be seen); **(c) the counterpart's work on this ticket: you never read this ticket's implementation, that is every file `git diff --name-only w2/integrate...HEAD` names other than the tests under `tests/acceptance/` (the guard and launcher modules, their unit tests, the path map, its schema, the change record). You read the existing code as it stands on the base, with `git show w2/integrate:<path>`, and you may run the implementation and read its results (what the guard answers, what `gov launch` hands its stand-in CLI);** **(d) the hidden half of any evaluation set, if you are measured by it.** Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Read refusals (DEC-849):** your session's guard runs this worktree's code. If a read is refused, take the refusal as a refusal, never look for another spelling, search named folders instead, and **count every refusal in your return**.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own small, targeted traversals (`trace_path`, `search_graph`, `query_graph`), never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Your Bash run as a whole is stopped at two hours: commit as soon as your cases are written and red, and return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag in this worktree.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch (the suite's `w2_58_support.py` already does). Nothing goes under a `.gov-runtime/` folder except under `.gov-runtime/scratch/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. Keep secret-like names out of your own command lines (the guard reads them as words); put them in test files. No subagents that write. Install nothing: a tool you need is returned as a package.
- Nobody runs `gov close`, `gov adopt`, `gov pause`, `gov rebuild`, or `docs/plan/tools/validate_s1.py`.
- You never ask or notify the owner (no question box, no `owner-ping`): a question goes into your return as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-5j8b.md` (read-only): its KPI lines, above all the failure line: "Each of (a) to (d) still refuses, by every read route an honest agent takes in ordinary work (DEC-801); no write rule widens; a guard error still fails closed."
- The decisions in `docs/DECISION_REGISTER.md`: DEC-820, DEC-821, DEC-873 (item 1: "the guard enforces Policy 2's (c) and (d) on every tool and Bash route an honest agent takes"; the launcher adds no OS-level layer for them), DEC-801, DEC-136 (findings as behaviours), DEC-221 (proportion), DEC-462.
- This suite: `tests/acceptance/W2-58/` (yours to read and extend), its `README.md`, `EARLIER_CASES.md` and `w2_58_support.py` (how it builds a temporary project, asks the guard with a role, a ticket and a subagent type, and runs `gov launch` with a stand-in CLI).
- How earlier suites drive the guard: `tests/acceptance/W1-02/` (its pipe cases, its subagent cases), `tests/acceptance/W2-50/`.

## The behaviours to test (from the review, as behaviours)

Words as in this suite's README: **T** is the session's ticket; **T's acceptance folder** is `tests/acceptance/<T's wbs_id>/`; a **protected part** is (c)'s acceptance folder for an engineer on T, (c)'s changed files for a test designer on T, and (d)'s hidden part for a session an evaluation set measures.

**1. File names given at run time.** A Bash read or search whose file names come from another command's output at run time is judged as a search from the folder that listing starts at. It is refused when a protected part that exists lies under that folder and nothing narrows the listing away from it; it is allowed when the listing is narrowed away from every protected part. The forms an honest agent uses, each as an engineer on T (its acceptance folder exists), as a test designer on T (a changed file under the searched folder), and as a measured session (the hidden part exists under the searched folder):
- a pipe into `xargs` with a reading command: `git ls-files | xargs grep -n <word>`, `find . -name '*.py' | xargs grep -n <word>`, `git ls-files src | xargs cat` (test designer, where `src` holds the changed file), `find eval -name '*.yaml' | xargs cat` (measured, where `eval` holds the hidden part);
- a command substitution in a reading command's arguments: `grep -n <word> $(git ls-files '*.py')`, `cat $(find tests -name <file>)`, and the same with backticks;
- a `while read` loop over a listing: `find . -print | while read f; do grep -H <word> "$f"; done`.
Allowed counterparts beside them: the same forms with the listing narrowed away from the part (for example `git ls-files src | xargs grep -n <word>` for the engineer, `find src -name '*.py' | xargs grep -n <word>`); the same forms for a session with no protected part (an orchestrator, a product-spec worker, an auditor, or an engineer whose ticket's acceptance folder does not exist); and the engineer's own test runs (`python3 -m pytest tests/acceptance/<wbs_id>/ -q`, piped to `tail`), which stay allowed.

**2. A subagent's reads.** A subagent is refused, for reads, at least what its session's role is refused on the session's ticket, and also what its own type is refused: an engineer session on T whose subagent's type is `independent-auditor`, `orchestrator`, `research`, `product-spec` or `independent-test-designer` is refused a Read (and a `cat`) of a file in T's acceptance folder; a test-designer session on T whose subagent's type is `engineer` or `independent-auditor` is refused a Read of a changed file. Counterparts: an orchestrator session on T whose subagent is untyped or `Explore` reads T's acceptance folder; an orchestrator session on T whose subagent's type is `engineer` is refused it (as today). Writes are not part of this item.

**3. A ticket named by its WBS id.** `gov launch` accepts a ticket named by its WBS id (`gov launch engineer W2-95` for a ticket whose file is `.tickets/<id>.md` with `wbs_id: W2-95`), and the session's `GOV_TICKET` is then the WBS id. A session whose ticket is given that way is refused exactly what it would be refused under the ticket's id: an engineer the files of T's acceptance folder (Read, `cat`, Grep), and a session an evaluation set measures by ticket its hidden part. Test it at the guard (the ticket given as the WBS id) and through `gov launch` with the stand-in CLI (the `GOV_TICKET` it hands on, then the guard asked with it).

**4. Secrets by the repository's own credential names.** Besides the names already covered, a file whose name ends in `.env` at any depth (for example `deepseek.env`, `provider.env`) and any file under a folder named `.secrets` at any depth are secrets under (a): every content read that names such a file (Read, `cat`, a copy) is refused for every role, auditors included. (A search from a folder above one stays as it is today; that is for the owner to decide.)

**5. No write rule widens.** For a role whose `allowed_paths` do not name them (an engineer, a test designer, a research worker), these writes naming the held-out list file `governance/project/held-out.yaml` or `.claude/settings.json` are refused, as they were on the base (`w2/integrate`): `dd of=<file>`, `truncate -s 0 <file>`, `sort -o <file> <other>`, `rsync <other> <file>`, `patch <file> <diff>`, `git checkout -- <file>`, `git restore <file>`. Reading either file stays allowed (Read, `cat`). Check each case's expectation against the base's guard where you are unsure (run the base's code from a temporary location built from single named files only if you must; otherwise state the base's behaviour from its source, read with `git show w2/integrate:<path>`).

STANDARD proportion (DEC-221): the forms above and their allowed counterparts, no combinatorial expansion beyond them.

## What you write

- **Only inside `tests/acceptance/W2-58/`.** No existing case of this suite or of an earlier suite changes. If an existing case asserts the opposite of a behaviour above, name it in your return (DEC-866) as a package, and change nothing there.
- `README.md`: a section for these review cases (DEC-136), each behaviour mapped to its tests with its expected red reason.
- **Red first:** run `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src python3 -m pytest tests/acceptance/W2-58 -q -p no:cacheprovider -rs -m "not local_only"` to the end, never with `-x` (the `local_only` live cases need the network, which your sandbox refuses; the lead runs them). Expected: the new refusal cases of items 1 to 5 fail because the guard allows them; their allowed counterparts and every existing case pass. Report the counts and the failing case names.

## Commit

Commit only `tests/acceptance/W2-58/`, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-5j8b" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-820" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Check `git log --oneline -3` and `git status --short` after the commit.

## Return

Your commit's hash; the test count before and after; the cases added per item; the red result as you saw it; the guard read refusals you met, counted; whether you used `gov retrieve`, and for what; any package.

Your return is one message. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
