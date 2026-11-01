# Brief: independent test designer, W2-96 (DAEO-ouet), run 3: one name in the R16 support code trips the secrets scan (P3, DEC-987)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-96-tests` on branch `w2/W2-96-tests` (made from the ticket's head `c9daee7c9ce8`).

**The problem.** The previous designer's commit `4b9353954f88` (review 4's W1 cases, R16) added to `tests/acceptance/W2-96/w2_96_support.py` a constant whose name ends in `TOKEN_KEY` and whose value is the name of an environment variable (around line 875). gitleaks' `generic-api-key` rule takes that assignment for a secret, so the product's `secrets-indexing` check (a hard block at the close) turns RED on this branch's store. It is a false positive, but it blocks the close, and `.gitleaks.toml` allowlists nothing but known synthetic fakes.

**Your task.** Rename that constant (and every use of it, in the support module and the case file `test_w2_96_at_review_4.py`) to a name the rule does not take, for example `R16_RUN_VAR`. Change nothing else: no value, no expectation, no other case, no README text beyond the name if the README names it. Then show that no file of the suite trips gitleaks any more, and that the suite still runs as before.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (never delete such a file; name it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-ouet`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-96-tests` and `w2/W2-96-tests`), and `git rev-parse --short=12 HEAD` (expect `c9daee7c9ce8`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-tests/src` set **per command** (never in a session's `--settings` env). Your tests, once merged into `/home/usain/gov-os-worktrees/W2-96` and run from there, must exercise that tree's code: the suite's support module already does this; keep it so.
- **Policy 2 (DEC-820):** reads are open, writes are closed. Refused to you: (a) secrets and keys, never printed (run gitleaks only with `--redact`, and never print a matched value); (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path, never read or name the qualification oracle); **(c) this ticket's implementation: you never read the engineer's work** — no file under `src/gov/accept/`, no `tests/unit/accept/test_w2_96*` file, and not `src/gov/check/commands.py` as it is on `w2/W2-96`, in any worktree or branch (this one included), by any tool, and nothing `git diff --name-only w2/integrate...w2/W2-96` names outside `tests/acceptance/`; (d) the hidden half of any evaluation set, by whoever is measured by it.
- **DEC-849:** until W2-58 lands the guard still refuses some reads (searches starting at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead, and count the refusals you met in your return. Never read `.claude/settings.json`.
- **Retrieval (DEC-836, DEC-963):** this task needs little; if you need to know something, use `gov retrieve` from the integration branch's store only: `cd /home/usain/gov-os-worktrees/W2-00-store-a && timeout 90 gov retrieve "<question>" --json` (try once; it can hang in the sandbox). **Drop unread any result under `src/gov/accept/` or `tests/unit/accept/`, and name any such result you were served (P-R1, DEC-820 (c)).** Never one giant query (DEC-860: batches with `--batch-size`, then `--continue <token>`); code questions by the code-graph tool's own traversal, small and targeted (DEC-859).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). Never write in `~/gov-os-workbench`. No clone, copy or programme file under any `.gov-runtime/` folder. Inside a launched session `.gov-runtime/freeze` and the placeholder dotfiles at the worktree's top are sandbox placeholders: conclude nothing from them and never `git add -A`.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Edit with the Edit tool at literal absolute paths; put anything longer in a script file in your session's own temporary folder (the one the launcher set) and run it by its literal path; a command with `$TMPDIR` in it is refused, so write the path out. Never `cd` into a subfolder of the repository. No subagents that write. Install nothing.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Budget (DEC-898):** your share is 1 GB and 50,000 files and folders outside the tracked tree, in the temporary folder the launcher set; run pytest with `-o tmp_path_retention_policy=failed`, never a per-run `--basetemp`; measure at the end (`du -sh`, `du -s --inodes`).
- If the guard or the sandbox refuses something you need, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try (AR-6).**

## Steps

1. Rename the constant everywhere in `tests/acceptance/W2-96/` (Edit tool). Nothing else changes.
2. gitleaks over the whole suite folder, redacted, with the repository's config: `gitleaks dir tests/acceptance/W2-96 --redact --no-banner --config .gitleaks.toml --exit-code 1` (if `gitleaks dir` is unknown to this version, `gitleaks detect --no-git --source tests/acceptance/W2-96 --redact --no-banner --config .gitleaks.toml`). It must report no leak; give its last line. If it finds another, report the rule id, file and line only, and fix it the same way (a rename, nothing else), or return it as a package if a rename cannot.
3. Run the whole folder once, to the end: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-tests/src python3 -m pytest tests/acceptance/W2-96 -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line`. This branch carries the engineer's R16 fix, so all 109 should pass; give the counts and any failing names with one-line reasons.
4. One commit, only your test paths, trailers in the final block (check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; never `--no-verify`, never `core.hooksPath`):

       git commit -m "W2-96 (DAEO-ouet): rename R16's environment-variable constant so the secrets scan does not take it for a key (DEC-987)" --trailer "Task: DAEO-ouet" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-987, DEC-911" --trailer "Rewrite-Reason: a gitleaks generic-api-key false positive on a constant's name turned secrets-indexing red (DEC-911); a rename only, no expectation changed" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

   Then `git log --oneline -2`, `git show --stat HEAD` and `git status --short`.

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

In `evidence` also: the sandbox check, your commit's 12-digit hash, the old and new name, gitleaks' last line, the test counts, whether you used `gov retrieve`, the guard read refusals you met (count), and your scratch measure. After the twelve fields, a `brief_gaps:` section (one line per thing you had to discover that this brief did not tell you, with minutes it cost, or `brief_gaps: none`).
