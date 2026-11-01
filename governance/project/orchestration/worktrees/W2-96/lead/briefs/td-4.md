# Brief: independent test designer, W2-96 (DAEO-ouet), run 2, review 3's batch (DEC-970, DEC-916)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-96-tests` on branch `w2/W2-96-tests`. You add review 3's cases to the ticket's acceptance tests, from the reviewer's finding given below as a described behaviour (DEC-136), and you show them red.

**Where things stand.** The suite in `tests/acceptance/W2-96/` has 100 cases (run 1's and run 2's), marker `qzv96leak`. The engineer's run-2 implementation is in this worktree's tree (this branch was made from the ticket's head); you still never read it (Policy 2 (c) below), but your red run executes it. Review 3 probed it and found one behaviour that fails open; the lead turned it into the addendum below. A fresh engineer builds it in parallel in `/home/usain/gov-os-worktrees/W2-96`; the lead merges your branch after you return. A leftover empty folder in the ticket's worktree is not yours this time: do not try to remove it.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (never delete such a file; name it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-ouet`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-96-tests` and `w2/W2-96-tests`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-tests/src` set **per command** (never in a session's `--settings` env). Your tests, once merged into `/home/usain/gov-os-worktrees/W2-96` and run from there, must exercise that tree's code: run `gov` as `python3 -m gov.cli.main` with the `src/` of the repository that holds the test file (found from the test file's own location), never a bare `gov` from PATH. The suite's support module already does this; keep it so.
- **Policy 2 (DEC-820):** reads are open, writes are closed. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path, never read or name the qualification oracle); **(c) this ticket's implementation: you never read the engineer's work** — no file under `src/gov/accept/`, no `tests/unit/accept/test_w2_96*` file, and not `src/gov/check/commands.py` as it is on `w2/W2-96`, in any worktree or branch (this one included), by any tool, and nothing `git diff --name-only w2/integrate...w2/W2-96` names outside `tests/acceptance/`; for the product's recorded command list read `git show w2/integrate:src/gov/check/commands.py`; (d) the hidden half of any evaluation set. You read the specification, the KPIs and the existing code as it stands on `w2/integrate` (`git show w2/integrate:<path>`).
- **DEC-849:** until W2-58 lands the guard still refuses some reads (searches starting at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead, and count the refusals you met in your return. Never read `.claude/settings.json`.
- **Retrieval (DEC-836, DEC-963):** use `gov retrieve` for what you need to know before reading files at random, **from the integration branch's store only**: `cd /home/usain/gov-os-worktrees/W2-00-store && timeout 90 gov retrieve "<question>" --json` (a read; it holds `w2/integrate` as of its last refresh). Known: inside the sandbox that call can hang on its embedder's network call; try it once, and if it times out, say so and read named files instead. Never retrieve from `/home/usain/gov-os-worktrees/W2-96`'s store. **Drop unread any result under `src/gov/accept/` or `tests/unit/accept/`, and name any such result you were served in your return (P-R1, DEC-820 (c)).** Never one giant query or context (DEC-860): a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). A test that needs a repository builds a temporary one from scratch. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only. No clone, copy or programme file under any `.gov-runtime/` folder. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at literal absolute paths; put anything longer in a script file in your session's own temporary folder (the one the launcher set; `.gov-runtime/scratch/td/` is refused to this role) and run it by its literal path; a command with `$TMPDIR` in it is refused, so write the path out. Never `cd` into a subfolder of the repository (the sandbox leaves a `.claude/` folder there): use paths from the worktree's top. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. No subagents that write. Install nothing (an install you need is a P1 escalation in your return).
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Budget (DEC-898):** your share is 5 GB and 250,000 files and folders outside the tracked tree. Keep pytest's own temp retention (never a per-run `--basetemp` for your own suite runs); run with `-o tmp_path_retention_policy=failed`. Your temp folder is the one the launcher set; clean up what you make as you go; measure it at the end (`du -sh` and `du -s --inodes`) and give the figures.
- If the guard or the sandbox refuses something you need, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try (AR-6).**

## What you read

- Your suite as it stands: `tests/acceptance/W2-96/` on this branch (README, support module, cases; run 2's file `test_w2_96_at_run_2.py` included).
- The ticket file `.tickets/DAEO-ouet.md` (read-only) and DEC-970 in `docs/DECISION_REGISTER.md`.
- The lead's addenda (behaviour only): `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/design-r2.md` (R8 to R13) and review 3's, below.

## The behaviour to test: review 3's addendum

The design note, R1 to R7 and run 2's R8 to R13 still hold; where they differ, this holds.

- **R14 (the clean-up tolerates concurrent changes; review 3's V1).** The private folder is removed in every path even when a process the run cannot stop (one a test started in a session of its own, such as a nested `gov accept`) changes it meanwhile, or removes it first: an entry already gone is passed over, a folder found not empty is emptied again, and no single entry stops the removal of the rest (a bounded number of passes, then whatever error remains is passed over too). A run stopped by SIGINT, SIGTERM or SIGHUP still ends with 128 plus the signal (R12) whatever the clean-up met; a run that was not stopped is reported as its results say, never turned into `crash` by an entry another process removed. Nothing of the run stays in the caller's `TMPDIR`. Depth still never matters (R10), and the three signals are still held during the clean-up (R9).
- **R15 (the clean-up's time grows with the entries; review 3's V2, riding along).** Removing a folder whose thousands of sibling folders sit side by side takes time in proportion to the number of entries, not its square: 8,000 empty sibling folders are removed in a few seconds at most, comparable to a plain recursive removal.

How review 3 reproduced V1 (as a described behaviour): a planted test runs a nested `gov accept` on a nested planted project, started in a session of its own (as this suite's own harness starts nested runs); the nested test writes about 3,000 small files and sleeps about 1 s. SIGTERM was then sent to the outer `gov` once the nested `gov`'s removal had begun, or to the outer and the nested `gov` at the same moment (as a stop of a whole process tree does). In about one run in three the outer `gov` reported `ok: true`, `outcome: error`, `error_kind: crash`, exit 4 instead of 143, and test-named folders (and once 2,657 test-written files) stayed in the caller's `TMPDIR`. The removal stopped at the first entry another process had removed meanwhile.

## What you write

- Only inside `tests/acceptance/W2-96/`: a new case file (say `test_w2_96_at_review_3.py`), its rows in the README's map (in the map forms the suite uses; under R8 every case must also be mapped or it still counts), and support code where needed.
- R14: the nested form above, both ways (SIGTERM to the outer `gov` while the nested removal runs; SIGTERM to both at once): each must end with 143 and the given `TMPDIR` empty, no marker anywhere. It is a race: repeat each form enough times inside the case (or parametrize) that the run-2 code fails it reliably (review 3 saw about one in three; aim for a red in nearly every run of the case), while the whole W2-96 suite stays well under eight minutes. Also a case where a planted test's own-session process keeps creating and removing files in its temporary folder while the run ends normally (no signal): the outcome is the results' (pass, exit 0), never `crash`, and the given `TMPDIR` ends empty.
- R15: a planted passing test that leaves 8,000 empty sibling folders in its temporary folder: pass, exit 0, the given `TMPDIR` empty, and the whole `gov accept` run under a generous bound you state (review 3 measured 22.7 s for the removal alone on run 2's code against 0.6 s for a plain recursive removal; choose a bound that a linear removal meets under load and run 2's code misses, and say why).
- Revise no earlier case unless the addendum changes it; say so if you do.
- Keep the cases deterministic in outcome, no network.
- **Red first:** this branch (`w2/W2-96-tests`, made from the ticket's head `382e6d8fba8c`) carries run 2's implementation, which lacks review 3's addendum. Run the whole W2-96 folder to the end: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-tests/src python3 -m pytest tests/acceptance/W2-96 -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line`. Say which new cases are red and why (the README states each expected red reason), and run the new file a second time to show the race cases are red reliably.
- An ambiguous point or a dispute with the addendum is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

One commit, only your test paths, trailers in the final block (the git hooks are uninstalled; never `--no-verify`, never `core.hooksPath`; check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file):

    git commit -m "W2-96 (DAEO-ouet): review 3's acceptance cases for gov accept, a clean-up that tolerates concurrent changes (DEC-970)" --trailer "Task: DAEO-ouet" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-970, DEC-959" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

(Add `Rewrite-Reason: review 3's V1 (DEC-136)` only if you revise an earlier case.) `Implements:` holds only ids the register holds (DEC-927). Then `git log --oneline -2` and `git status --short`.

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

In `evidence` also: the sandbox check, your commits' 12-digit hashes, the test counts, the red reasons as you saw them, the revised cases, whether you used `gov retrieve` and any result under the implementation paths you were served, the leftover folder's removal (done or refused), the guard read refusals you met (count), and your scratch measure. After the twelve fields, a `brief_gaps:` section (one line per thing you had to discover that this brief did not tell you, with minutes it cost, or `brief_gaps: none`).
