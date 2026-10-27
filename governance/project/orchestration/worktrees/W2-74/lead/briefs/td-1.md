You are a fresh independent test designer (MR-3). Ticket: DAEO-2azm (W2-74), profile LITE, a test-revision ticket. You work only in the worktree `/home/usain/gov-os-worktrees/W2-74` on branch `w2/W2-74`. The owner decided (DEC-925 item 1) that you make three revisions to earlier tickets' acceptance tests. There is no implementation in this ticket: the code under test already stands; your revised tests must pass on it.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-2azm','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (do not delete anything).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-2azm`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-74` and `w2/W2-74`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-74/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-74/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Memory used (DEC-836, DEC-859, DEC-860):** for what you need to know, use `gov retrieve` first (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-74/src python3 -m gov.cli.main retrieve "<question>" --json`) before reading files at random. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used `gov retrieve`.
- **Read refusals (DEC-849):** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal; never look for another form; search named folders instead. Count the refusals you met in your return.
- **Reads open, writes closed (DEC-820):** you read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path, never read or name the qualification oracle); **(c) the counterpart's work on this ticket: as test designer you never read this ticket's implementation (the files `git diff --name-only w2/integrate...HEAD` names, other than your own tests) — this ticket has none; (d) the hidden half of any evaluation set, by whoever is measured by it.** Never read `.claude/settings.json` except as the tests themselves read it; run no glob, search or listing over `governance/project/`. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Row W2-L423's rule (owner, standing, DEC-911):** under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule". The keywords are the ones listed, written in parts, in `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/keyword_warn.py` (`KEYWORDS`). Never print or type a keyword whole in your return or any file you write, test files included (in a test's input, write it in parts, as that tool does).
- **Disk budget (DEC-898):** the lead's budget is 20 GB and 1,000,000 files and folders, outside the tracked tree; **your share is 5 GB and 250,000 files and folders.** Keep pytest's own temp retention (never `--basetemp`). Clean up every temp tree you make as soon as it is no longer needed. **Do not set `TMPDIR`**: keep the temp folder the sandbox sets for you, and say in your return where it was. Measure your scratch at the end (`du -sh` and `du -s --inodes` of your temp folder) and give the figures in `evidence`.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commits exist.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag. Never run `gov close`, `gov adopt` or `gov pause`.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). A test that needs a repository builds a temporary one.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never `python3 -c` with braces (DEC-409): put a script in a file.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.
- Before each commit: check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`.
- Suites are run to their end, never with `-x`.

## What you read

- The ticket file `.tickets/DAEO-2azm.md` (read-only): its KPI lines, its `allowed_paths` and its sources.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-925 (item 1), DEC-922 (Part B, the settings regeneration), DEC-899 (P-I1-2), DEC-917 (the lifecycle hook line), DEC-911 (row W2-L423's rule), DEC-906, DEC-866 (a superseded expectation is revised with `Rewrite-Reason: <the new decision>` and no other expectation is lowered), DEC-491.
- The package `governance/project/orchestration/packages/P-REPIN-R1.md` (named file; read it by its path).
- The four test files and their READMEs (below), their folders' conftest and support modules, and the committed `.claude/settings.json` only through what those tests read.

## The behaviour to test: three revisions

Before you edit anything, run the four files alone (each its own pytest command, with the DEC-732 `PYTHONPATH`, `-p no:cacheprovider`, to the end) and record which cases are red and why. Expected: W1-01's four `docs/source` cases, W1-47's two `docs/source` cases, and W1-49's `[not on PATH]` case red; W2-69's file green.

1. **Retire** W1-01's `test_docs_source_deny_rules_survive_the_change` (its four cases) in `tests/acceptance/W1-01/test_w1_01_settings_deny.py`, and W1-47's `test_the_other_deny_rules_are_in_place[Read(./docs/source/**)]` and `[Edit(./docs/source/**)]` in `tests/acceptance/W1-47/test_w1_47_settings_rules.py`. The reason: the `docs/source` folder left the tree on 2026-10-01, and P-I1-2 (DEC-899) dropped its two deny rules in DEC-922's regeneration. **Every other deny rule these files check stays checked**, with the same assertion. Note that W1-47's list of kept deny rules lives in `w1_47_support.py`, which is outside your paths: make the change in the test file itself, so that exactly the two `docs/source` entries leave the parametrization and every other entry stays. Update each README: the KPI line's row says the case is retired, by DEC-925 item 1, and why. `Rewrite-Reason: DEC-925 item 1, P-I1-2`.
2. **Revise** W1-49's `test_without_tk_the_block_says_so_and_holds_the_rest[not on PATH]` in `tests/acceptance/W1-49/test_w1_49_precompact.py` so that its sandbox has a gov (for example a link at the sandbox HOME's `.local/bin/gov` to the pinned one, or a `gov` on the sandbox's PATH that resolves to the pinned one), so that **only tk is missing**, as the case intends. The lifecycle hook line of DEC-917 then runs and finds its gov. Its assertions stay exactly as they are (exit 0 / not blocked, the git head in the block, the `tickets in progress` line says unavailable). The failure KPI: the case must never pass with tk present — tk must still be absent from what the hook sees. The `[fails]` case is unchanged. Make the change inside the test file (the conftest and support module are outside your paths); if that is impossible, return a package. Update the README. `Rewrite-Reason: DEC-917`.
3. **Rename** the W2-69 case in `tests/acceptance/W2-69/test_w2_69_word_internal_fragments.py` whose test id holds a keyword of row W2-L423's rule (its function name or its parametrize id), so that no test id holds one. Find it by collecting the file (`pytest --collect-only -q`) into a file and running `python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/keyword_warn.py <root>` on a folder whose `.gov-runtime/` holds that file (it prints paths only), and then narrowing by your own script that prints line numbers only, never the keyword. Its input and its assertions stay the same; a keyword in its input is written in parts. Give it an explicit parametrize id (or name) that holds no keyword. Update the README where it names the case. `Rewrite-Reason: DEC-911`.

After the edits, run the four files alone again, to the end: all green. Then run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-74/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` into a file under your temp folder and check with keyword_warn (as above) that no test id in the whole collection holds a keyword; report paths and counts only.

## What you write

- Only these eight paths: `tests/acceptance/W1-01/test_w1_01_settings_deny.py`, `tests/acceptance/W1-01/README.md`, `tests/acceptance/W1-47/test_w1_47_settings_rules.py`, `tests/acceptance/W1-47/README.md`, `tests/acceptance/W1-49/test_w1_49_precompact.py`, `tests/acceptance/W1-49/README.md`, `tests/acceptance/W2-69/test_w2_69_word_internal_fragments.py`, `tests/acceptance/W2-69/README.md`. Nothing else in the tree; no throwaway file left behind.
- LITE: the smallest change that does each revision. Lower no other expectation (DEC-866).

## Commit

Three commits, one per revision, each with its test file(s) and README(s), trailers in the final block (DEC-182, DEC-476, DEC-491):

    git commit -m "<subject>" --trailer "Task: DAEO-2azm" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-925" --trailer "Rewrite-Reason: <reason above>" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After each commit check `git log --oneline -2` and `git status --short`.

## Return

Your commits (12-digit hashes) with their trailers; the sandbox check; the before and after results of the four files; the test ids retired, revised and renamed (renamed: give only the new id; describe the old one without its keyword); the keyword check's result (paths and counts only); every earlier test you rewrote, with its reason; whether you used `gov retrieve`; the read refusals met; your scratch measure; any package.

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

Refused twice for the same call: stop and say so.
