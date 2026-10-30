You are a fresh independent test designer (MR-3). Ticket: DAEO-cv58 (W2-60a, "The role, its skills and its model and effort loaded at launch; the launch record"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-60a` on branch `w2/W2-60a`. You extend the ticket's acceptance tests with review 1's findings, as described behaviours, and you show them red.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cv58','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-cv58`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-60a` and `w2/W2-60a`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Your tests, run from this worktree, must exercise this worktree's code: your README says how.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m gov.cli.main retrieve "<question>" --json`) for what you need to know before reading files at random. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Inside the sandbox the code graph's folder may be read-only: if retrieval fails for that reason, say so and read named files. Say in your return whether you used `gov retrieve`, and for what.
- **Reads are open, writes closed (DEC-820, Policy 2).** You read freely: the whole repository, the git history, other worktrees, the existing code as it stands on the ticket's base (`git show w2/integrate:<path>`). Four things are refused: (a) secrets and keys, never printed (this includes the CLI's credentials file under `~/.claude/`: never read, copy or print it); (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; (c) **this ticket's implementation: you never read the files `git diff --name-only w2/integrate...HEAD` names, other than your own tests** (that includes this ticket's design note and research record; what you need from them is in this brief, as text); (d) the hidden half of any evaluation set, by whoever is measured by it. Your independence also comes from order: you write the tests before the implementation exists (DEC-826 Q2).
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you meet and give the count in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (`> "$OUT/x"`, `mkdir -p $D/t`), no here-document (`<<EOF`), no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools and literal absolute paths; put anything longer in a script file under `.gov-runtime/scratch/test-designer-b5/` and run that file. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try.** If the guard or the sandbox refuses something you need, do not work around it: return it as a package.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). A test that needs a repository builds a temporary one from scratch (or copies single named files from git's listing, as W1-46's support does), never `governance/project/`. Nothing that is a clone, copy or programme goes under a `.gov-runtime/` folder.
- Never write `.gov-runtime/**` outside `.gov-runtime/scratch/**`. Never write, list or search in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. Install nothing. No subagents that write.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` (your scratch and your return) write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule". In a committed test, write such a keyword only in parts.
- **Disk budget (DEC-898):** your share is 4 GB and 300,000 files and folders, outside the tracked tree. Use pytest's own temp folders (its retention of three base folders; never a per-run `--basetemp`), and pass `-o tmp_path_retention_policy=failed` on your runs. Remove anything else you make before you return.
- No compaction threshold anywhere; you use your model's full window (DEC-838). **You start no live Claude session yourself** (your sandbox has no network): the live cases you write are run by the lead.

## This batch: round 2 (review 1's findings), tests first

This ticket's tests (`tests/acceptance/W2-60a/`, yours to extend: your folder) and its implementation exist; review 1 of the implementation failed. You add the tests for the behaviours below, **as described behaviours (DEC-136)**, and show them red against the current head. You still never read this ticket's implementation (DEC-820 (c)): the files `git diff --name-only w2/integrate...HEAD` names, other than tests.

**The nightly (DEC-933, DEC-936):** before each test run, check `test -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING`. While it exists (from 02:00 most nights), run **one test file at a time**, never a folder or a suite; reading and writing go on.

## What you read

- Everything the first batch read (the ticket `.tickets/DAEO-cv58.md`, its card in `docs/plan/WAVE_2_WBS.md`, DEC-826, DEC-838, DEC-839, DEC-832, DEC-136, DEC-491, DEC-802), your own tests and README in `tests/acceptance/W2-60a/`, and the existing code on `w2/integrate` (`git show w2/integrate:<path>`).
- How the launch line, the settings and the record look today is what your existing tests assert; the behaviours below add to them.

## The behaviours to test (review 1's findings, as behaviours)

1. **The project's command files are skills the session can load, and the record names each one** (KPI line 2; failure line 1, "an unrecorded skill"). The CLI loads every Markdown file under the tree's `.claude/commands/` as a skill: `.claude/commands/<name>.md` as `<name>`, and `.claude/commands/<namespace>/<name>.md` as `<namespace>:<name>` (this repository tracks six: `.claude/commands/opsx/apply.md` … as `opsx:apply` …). After the change, the launch record's `skills` holds one entry for each such file, taken from that file (the copy the session loads): its name in that form, its path, its version (the front matter's `version` as written, else the words `no version`), its sha256, and `named: false`. The `.claude/skills/` entries stay as they are. A command file that is a link, or a folder under `.claude/commands/` that is a link, or a command file whose front matter (when it has one) is not YAML, **refuses the launch** (the record could not say what the session may load), as the same faults in `.claude/skills/` already do. No `.claude/commands/` adds nothing. A role's skills line still names only `.claude/skills/` skills.
2. **The owner's user-level permission rules still reach the session** (failure line 3: no protection a launched worker has today is lost). The launcher starts the session with `--setting-sources project,local`, which drops the user settings file `~/.claude/settings.json` as a whole; today a launched worker gets that file's `permissions.ask` and `permissions.deny` rules (on this machine, `ask` rules for `rm` and for `owner-ping`, which make a `-p` worker's `rm` refused). After the change, **every string of the user settings file's `permissions.ask` and `permissions.deny` lists is in the `--settings` value's `permissions.ask` and `permissions.deny`** (beside the launcher's own deny rules, which stay), and **nothing else of the user settings file is carried**: no `allow` rule, no `defaultMode`, no `env`, no `model`, no `effortLevel`, no hooks. A user settings file that is absent carries nothing and launches. A user settings file that exists but cannot be read, is not a JSON object, or whose `permissions` is not a map or whose `ask` or `deny` is not a list of strings, **refuses the launch** (it cannot be shown to keep its protections). Your planted test home's user settings file gets `ask` and `deny` rules for these cases; revise your own earlier case that says nothing of the test home reaches the settings so that it allows exactly these two lists and nothing else (a revision of your own test after the implementer's commit: `Rewrite-Reason:` naming review 1's finding F2, DEC-136).
3. **More spellings of a compaction threshold are refused in the repository's settings** (KPI line 5): in `.claude/settings.json` or `.claude/settings.local.json`, an `env` holding `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` or `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS`, and a `modelSettings.<any model>.autoCompactWindow`, each refuse the launch with "no launch sets a compaction threshold (DEC-838)" in the message, as `env.CLAUDE_CODE_AUTO_COMPACT_WINDOW` and a top-level `autoCompactWindow` already do. A `modelSettings` entry without that key launches.
4. **More arguments refused after `--`,** each with `LAUNCH_REFUSED`, "the CLI arguments carry" and the argument's name, judged word by word (a prompt that only names one as a word still launches): `--fallback-model <m>` and `--fallback-model=<m>` (turns could run on a model that is not the role's: KPI line 4); `--chrome` and `--ide` (they attach connectors: KPI line 6); `--system-prompt-snapshot <v>` and `--system-prompt-snapshot=<v>` (a resumed session's prompt must stay the one its record names). `--no-chrome` is not refused.

Each refusal also leaves no launch record (as your existing refusals assert).

## What you write

- Only under `tests/acceptance/W2-60a/`: new cases for the four behaviours above (in proportion: each behaviour's success and failure, the spaced and `=` forms where named), and the README's table extended (KPI line, tests, red reason), with a short "Round 2 (review 1)" section.
- **Red first:** run each file you changed or added, one at a time, with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m pytest <file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only"`, to its end, never with `-x`. The new cases fail for the reason the README states (the behaviour does not exist yet); every case that passed before still passes.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Your commits come after the implementer's, so each carries a `Rewrite-Reason:` (DEC-491):

    git commit -m "W2-60a: round 2 acceptance tests (review 1's findings)" --trailer "Task: DAEO-cv58" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-826, DEC-838, DEC-839, DEC-832, DEC-941" --trailer "Rewrite-Reason: review 1 findings F1 and F2, as behaviours (DEC-136, DEC-802)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -3` and `git status --short`.

## Return

Your last message, complete in itself. The twelve fields come first, each as a labelled line, then: the step-0 result; each commit's 12-digit hash; the cases added and revised (per file); the red result as you saw it, per file (counts and the reason); each package (six parts); the read refusals you met (count); whether you used `gov retrieve` (this worktree has a store now).

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

The twelve fields come first, each as a labelled line, with any machine-readable payload after them. Refused twice for the same call: stop and say so.
