# Brief: independent test designer, DAEO-57hm (W2-95), resume, test batch 3 (W1-30's planted path maps)

You are a fresh independent test designer (MR-3). Ticket: DAEO-57hm (W2-95), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-95-tests` on branch `w2/W2-95-tests`. Your task is one revision of an earlier ticket's acceptance tests (W1-30), decided by the CTO in DEC-970 (package 1 (a)) and written into the ticket's body; it is described below under **The revision**. You lower no expectation.

## The revision (the reason for this batch)

W2-95 makes the check `core-pathmap` judge what it says: for each tracked path (`git ls-files`) of a repository with `governance/project/`, the path map `governance/project/path-map.yaml` must place it in exactly one namespace; a path in none or in two is a finding, and the check (family "path-map compliance", hard-block) is red. Before W2-95 the check judged nothing when `namespaces` was a mapping, so a path map that writes `namespaces: {}` passed.

W1-30's tests plant projects whose path map writes `namespaces: {}`. With the check now working, every tracked path of those planted projects is in no namespace, path-map compliance is red, and 165 W1-30 cases fail for a reason that is not their subject. DEC-970 decided: **W1-30's planted path maps that write `namespaces: {}` get one catch-all namespace (`paths: ["**"]`), lowering nothing**, with `Rewrite-Reason: DEC-959 item 9`. The files (named in the ticket's body):

- `tests/acceptance/W1-30/test_w1_30_r15_command_success.py` (line 93)
- `tests/acceptance/W1-30/test_w1_30_r15_context_tickets.py` (line 30)
- `tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py` (lines 248 and 272)
- `tests/acceptance/W1-30/test_w1_30_r16_context_own_tickets.py` (line 43)
- `tests/acceptance/W1-30/w1_30_r15_support.py` (lines 83-84; the second form also writes `policies:` after `namespaces`, keep that part as it is)
- `tests/acceptance/W1-30/w1_30_support.py` (line 163; it also writes further top-level keys after `namespaces`, keep those as they are)
- and any other W1-30 file that writes an empty namespaces map (search `tests/acceptance/W1-30/` yourself, in both YAML and JSON or dict spellings).
- `tests/acceptance/W1-30/README.md` describes the empty `namespaces` (around lines 1335, 1366 and 1374): update those sentences so they state the catch-all namespace and why (DEC-970, DEC-959 item 9). Change nothing else in the README.

How to write the namespace: in the form the path map's schema states, `template/governance/kernel/schemas/path-map.schema.json` (`namespaces` is a mapping of a name to its entry; an entry's `paths` is a non-empty list of patterns, `**` crosses folders). Read the schema for any other field an entry requires, and give it the least that the schema and the loader (`src/gov/config/loader.py`, `src/gov/config/path_map_schema.py`, read as they stand on `w2/integrate` with `git show w2/integrate:<path>`) accept. One namespace only, matching every path (`"**"`), so no path is in none and none in two. Do not change any assertion, any other planted content, any case name, or any other key of those path maps. If a case's subject is the path map itself (for example a case that relies on `namespaces` being empty to test something else), do not guess: name it, leave it, and return it as a package.

Then run the W1-30 cases you changed, and the whole W1-30 suite, in your worktree, and give the counts: `cd /home/usain/gov-os-worktrees/W2-95-tests && TMPDIR=<your session's temp folder> PYTHONPATH=/home/usain/gov-os-worktrees/W2-95-tests/src timeout 540 python3 -m pytest tests/acceptance/W1-30 -n 8 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE` (if it needs longer than 540 seconds, split it by file into several commands, each under 540 seconds; never `-x`). The code in your worktree is this ticket's branch head, which includes this ticket's implementation: you may run it and read the results and failure messages, but you never read the implementation's files (below, (c)). Before your change, the engineer measured 165 failed, 369 passed and 3 errors in W1-30 on this code; after it, the cases you revised should pass. If a case still fails, read its failure message: if the cause is the path map (core-pathmap's findings in the output), your revision is incomplete; if the cause is anything else (the sandbox, the network, the store, a timeout), name the case and its message in your return and change nothing for it.

Commit with `--trailer "Rewrite-Reason: DEC-959 item 9"` in addition to the trailers below.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-57hm','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (do not delete anything).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-57hm`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-95-tests` and `w2/W2-95-tests`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **The code under test (DEC-732), word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=<this worktree>/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return. For you, <this worktree> is `/home/usain/gov-os-worktrees/W2-95-tests`.
- **Reads are open, with four exceptions (DEC-820):** (a) never read or print secrets or keys; (b) never read the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; (c) **never read this ticket's implementation**: no file that `git -C /home/usain/gov-os-worktrees/W2-95-tests diff --name-only w2/integrate...HEAD -- src tests/unit` names (today `src/gov/check/pathmap.py` and `tests/unit/check/test_w2_95_pathmap.py`), in any worktree or through git, except as they stand on `w2/integrate` (`git show w2/integrate:<path>`); you may run that `--name-only` command to know what to avoid; (d) never read the hidden half of any evaluation set by which you are measured.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take such a refusal; never look for another form; search named folders instead (here, `tests/acceptance/W1-30/`). Count the refusals you met and give them in your return. Run no glob, no search and no listing over `governance/project/`. Never read `.claude/settings.json`.
- **Memory first (DEC-836, DEC-963):** use `gov retrieve` for what you need to know before reading files at random, **from the integration branch's store only**: `cd /home/usain/gov-os-worktrees/W2-00-store && PYTHONPATH=/home/usain/gov-os-worktrees/W2-95-tests/src python3 -m gov.cli.main retrieve "<question>" --json` (a read; wrap it in `timeout 120`: inside the sandbox it has hung on the network before; if it hangs or fails, say so and read the named files instead). Never this ticket's worktree's store and never its files. That store holds `w2/integrate` as of its last refresh; for what changed since, read `git show w2/integrate:<path>`. **Never one giant query or context (DEC-860):** take a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`src/gov/check/pathmap.py`, `tests/unit/check/test_w2_95*`), and name in your return any such result you were served.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (use literal paths); no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file under your session's temp folder with the Write tool, and run that file. Write files with the Write and Edit tools and literal absolute paths. A refused form is not retried in another disguise. A command that names `tests/acceptance` together with a `>` redirect has been refused before: do not redirect test output to a file; read it from the command's own output.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need for the ticket (for example a write to `tests/acceptance/W1-30/`), do not work around it: return it as a package, with the exact refusal text.
- **Protected material:** never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder (not needed here). Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). No clone, copy or programme file under any `.gov-runtime/` folder. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** anything you write under `.gov-runtime/` and your return give commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Your scratch budget (DEC-898):** 5 GB and 250,000 files and folders, outside the tracked tree (your session's temp folder, which `gov launch` sets, plus pytest's temp folders). Keep pytest's own retention (no `--basetemp`); use `-o tmp_path_retention_policy=failed`. Remove every temporary file you made as soon as it is no longer needed. Measure (`du -s --inodes`, `du -sh` of your temp folder) at the end and give the figures in your return.
- Install nothing: a tool you need is a package (P1, installs are the owner's). No subagents that write. You never ask the owner anything; a question is a package in your return.

## What you write

- Only the W1-30 files named above (and any other W1-30 file that writes an empty namespaces map), inside `tests/acceptance/W1-30/` in your worktree. Nothing else: not `tests/acceptance/W2-95/`, not `tests/acceptance/serial-only.txt`, no conftest.

## Commit

Commit only those paths, in one commit, with the trailers in the final block:

    git commit -m "W1-30 (DAEO-57hm): planted path maps place every path in one catch-all namespace (DEC-970)" --trailer "Task: DAEO-57hm" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-970" --trailer "Implements: DEC-959" --trailer "Rewrite-Reason: DEC-959 item 9" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

`Implements:` holds only decision ids the register holds (DEC-n) or Contract ids (CAP-n), never a word. Check `git log --oneline -2` and `git status --short` after the commit.

## Return

Your commit's hash (12 digits); each file changed and each line form you replaced; the W1-30 counts after your change, with every still-failing case and its cause; the `gov.__file__` line; any package; the sandbox check; the read refusals you met; whether you used `gov retrieve` and any result under the implementation paths you were served; your scratch measure.

Return one message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
