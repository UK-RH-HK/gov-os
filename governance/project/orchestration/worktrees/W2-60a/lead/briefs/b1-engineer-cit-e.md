You are a fresh engineer. Ticket: DAEO-cv58 (W2-60a, "The role, its skills and its model and effort loaded at launch; the launch record"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-60a` on branch `w2/W2-60a`. **This batch is design only: you write no code.** You write the change-execution design note (the CIT-E) and commit it together with the lead's probe record. A later engineer implements it.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cv58','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-cv58`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-60a` and `w2/W2-60a`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m gov.cli.main retrieve "<question>" --json`) for what you need to know before reading files at random. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Inside the sandbox the code graph's folder may be read-only: if retrieval fails for that reason, say so and read the named files. Say in your return whether you used `gov retrieve`, and for what.
- **Reads are open, writes closed (DEC-820, Policy 2).** You read freely: the whole repository, the git history, other worktrees. Four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; (c) the counterpart's work on this ticket: you never read `tests/acceptance/W2-60a/` by any tool (you may run those tests and see their names, results and failure messages); (d) the hidden half of any evaluation set, by whoever is measured by it.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you meet and give the count in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (`> "$OUT/x"`, `mkdir -p $D/t`), no here-document (`<<EOF`), no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools and literal absolute paths; put anything longer in a script file under `.gov-runtime/scratch/engineer-b1/` with the Write tool and run that file. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try.** If the guard or the sandbox refuses something you need, do not work around it: return it as a package.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). A throwaway stand-in copies single named files, never `governance/project/`; a test repository is built from scratch in your temp folder. Nothing is ever put under a `.gov-runtime/` folder that is a clone, copy or programme.
- Never write `.gov-runtime/**` outside `.gov-runtime/scratch/**`. Never write in `~/gov-os-workbench`. Install nothing. No subagents that write.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` (your scratch and your return) write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule". In the committed CIT-E, also write 12-digit hashes.
- **Disk budget (DEC-898):** your share is 2 GB and 100,000 files and folders, outside the tracked tree. Remove whatever you make in your temp folder before you return. You run no suite in this batch.
- No compaction threshold anywhere; you use your model's full window (DEC-838).

## What you read

- The ticket file `.tickets/DAEO-cv58.md` (read-only): its nine success KPI lines, its failure lines and its `allowed_paths`.
- Its card: `docs/plan/WAVE_2_WBS.md` §2, "#### W2-60 " and "#### W2-60a".
- W2-56's ticket file `.tickets/DAEO-wnnz.md`, its paragraph "Beside W2-60a" above all.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-826 (Q1 and Q5), DEC-838, DEC-839, DEC-832, DEC-801, DEC-786, DEC-941 (item 1.3); and for today's refusals DEC-313, DEC-218, DEC-233, DEC-315, DEC-386, DEC-392, DEC-728, DEC-743, DEC-751, DEC-873 (W2-58).
- Lens E, `docs/assessment/2026-10/E-roles-context.md`: F2, F7, F13, F14, F15, F19 and R6. Lens F, `docs/assessment/2026-10/F-models-context.md`: F1 and recommendations 1, 3, 6 and 7.
- The launcher as it stands: `src/gov/launch/launcher.py`, `src/gov/launch/command.py`, `src/gov/guard/runs.py`.
- The role files `template/governance/kernel/roles/*.md` and their generated copies `.claude/agents/*.md`; the skills `template/governance/kernel/skills/` and their generated copies `.claude/skills/`.
- **The lead's probe record** (the rules probe and the launch switches, measured live): `/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/rules-probe.md`. Its measurements are facts you design on; you cannot repeat them inside your sandbox (no network).
- An earlier CIT-E for the form: `docs/changes/W2-58-CIT-E.md`.

## What you write: two files, one commit

### 1. `docs/research/W2-60-rules-probe.md`

The lead's probe record, committed **unchanged in substance**: copy the content of `.gov-runtime/scratch/lead/rules-probe.md`, add a front matter in the form `docs/research/` files use (id, type, status, date 2026-10-29, ticket DAEO-cv58 (W2-60a), author: the ticket lead of W2-60a, who measured; the engineer of DAEO-cv58, who committed it; `state_class: EVIDENCE`), and change no figure, session id, command or conclusion. You may fix layout only.

### 2. `docs/changes/W2-60a-CIT-E.md`: the design, before any code

Status `PROPOSED` (design before code). It states, in this order:

**A. Behaviour sections** (headed "Behaviour: …"). Each states only what is seen from outside: what `gov launch <role> <ticket> [-- <args>]` does, refuses and records, the CLI line's arguments, the settings' env lines, the launch record's keys and place, and the messages' substance. **These sections name no function, module or internal name of the code to be written** (DEC-462), because the independent test designer reads them. They cover every KPI line and failure line:

1. **The role's text.** Where it is read from (the role file `template/governance/kernel/roles/<role>.md`, the generated agent `.claude/agents/<role>.md`), **which copy the session actually loads**, and how it reaches the session. The lead measured both routes (probe record part 2, r1 to r4): `--agent <role>` replaces the CLI's default system prompt with the agent's text (start 6,293 tokens against 25,976) and **narrows the session's tools to the agent's `tools:` list**, while `CLAUDE.md` and the guard hooks still apply; `--append-system-prompt-file <file>` keeps the default prompt and tools and appends the file. Choose one, say why, and say what the choice does to the tools a worker is given with `--allowedTools` (the leads start workers with `--allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob"`). The recorded hash and version are those of the copy loaded.
2. **The skills.** Which skills the session can load (the project's generated copies under `.claude/skills/`, and how a role file names its skills), each recorded with its name, version and content hash **taken from the copy the session loads**. Today the loaded copies carry no `version` in their front matter while the kernel copies do (lens E F15): say what the record holds then, and if the design needs a version in the loaded copy, say so as a requirement on W2-11 ("one versioned source per skill", DEC-832 item 2), never a silent fallback. A role file that names its skills gets those (so W2-33's packs load with no code change, DEC-832 item 1); a named skill that is missing refuses the launch. Say how the CLI's own built-in skills (probe record part 2, "What stays") are treated.
3. **The default line, its exact form.** The role file's line that gives the role's default model and effort, **model and effort only, no compaction threshold** (DEC-839 item 5, DEC-838). Today the role files say only "Model tier: standard". State the line's exact text form (one line, a grammar a reader cannot misread, with one example per role at DEC-839's values: model `claude-opus-5-5` for every role; effort `high` for engineer, test designer, research and product-spec; `max` for the independent auditor), which copy it is read from, and what is "missing" and "malformed". W2-11 writes this line into every role file through its CIT-P, so this is the one place its form is stated. Also: an effort given after `--` is applied and recorded as the launch's own (it may differ from the default); a model given after `--` that is not the role's is refused, naming both; one that is the role's is accepted (say whether it is passed once or twice).
4. **What is kept out.** Connectors, user-level agents and skills, and model-side memory, by the CLI's switches the probe record measured (part 2, w1, w3, w4 or w5, and c1 combined). For each: the switch, where it goes (the CLI line or the settings), and what the session's start then shows. Note that `--setting-sources project,local` is refused after `--` today and is set by the launcher itself under the "two edges" rule below; say what dropping the user's settings file does (it also drops a user-level `CLAUDE_CODE_SUBAGENT_MODEL` and `effortLevel`). **Anything the CLI gives no switch for is named as a package, never passed silently.**
5. **The subagent model.** `CLAUDE_CODE_SUBAGENT_MODEL` in the settings' `env`, set to the session's model, and recorded (DEC-839 item 3, lens E F14).
6. **No compaction threshold.** No `--autocompact` on the line, no `CLAUDE_CODE_AUTO_COMPACT_WINDOW` in the settings; one given after `--` is refused (every spelling the CLI accepts: spaced and `=`); the record states the threshold as none. The process environment's copy falls on W2-56's cleaned environment (below): say so.
7. **The arguments the launcher now sets itself are refused after `--`,** each in its spaced and `=` forms: `--agent`, `--append-system-prompt` and `--append-system-prompt-file`, `--session-id`, a `--model` that is not the role's, and the compaction threshold. Give the exact list and the substance of each message.
8. **Resume.** The leads resume a worker with `--resume <session id>` after `--`. The lead measured that `--session-id` with `--resume` is refused by the CLI unless `--fork-session` is also given (probe record part 2, x1 and x2). State how a resumed launch works: its session id, its record, and that it still refuses what a fresh launch refuses.
9. **The launch record.** One record per launch, keyed by the session id the launcher gives with `--session-id`, **written before the session starts**: role, ticket, the ticket's class, model, effort (and whether it was the role's default or given after `--`), subagent model, threshold none, the role text's path, version and hash, each skill's name, version and hash, the CLI's version, the start time. **Its one folder, shared by every worktree of the repository** (say how it is found from any worktree, and that a session cannot write it: say where that folder is against the sandbox's write list and the `Edit` deny rules). A record that cannot be written refuses the launch, and no session starts. A record never names another session (a session id already recorded is refused, or cannot happen: say which).
10. **Fail closed everywhere.** The launch is refused when the role text, a named skill, the default line or the record is missing or cannot be read; when the model after `--` is not the role's. **Every refusal the launcher makes today still refuses, with its message:** DEC-313's, DEC-218's, DEC-233's, DEC-315's, W2-58's (DEC-873), the role and ticket checks. Say in which order the checks run, so that today's refusals keep their messages (the existing argument and ticket checks before the role is read).

**B. The split with W2-56, line by line in `launcher.py`** (DEC-786; W2-56's "Beside W2-60a" paragraph):
- **This ticket's:** `role.py` (new: the role's text, its skills and its default line, read and hashed), `record.py` (new: the launch record), `tests/unit/launch/test_role*`, `tests/unit/launch/test_launch_record*`, this note and the probe record; in `launcher.py`: the arguments the session is started with (role text, `--model`, `--effort`, `--session-id`, the switches for connectors, user-level agents and skills, and memory), the settings' `env` lines it sets (`CLAUDE_CODE_SUBAGENT_MODEL`), the refusals of the arguments it now sets itself, the record's write before the session starts, and the calls to its modules.
- **W2-56's:** `sandbox.py`, `environ.py`, the rest of `tests/unit/launch/**`, `src/gov/codeintel/__init__.py`; in `launcher.py`: the sandbox's write list and filesystem settings, the process environment the session is started with (the `env=` of the start), the refusals of `--restricted`, `--safe-mode`, `--agents`, `--plugin-dir`, `--plugin-url`, `--mcp-config` and `--system-prompt`, the start lock, and the calls to its modules.
- **Two edges:** the launcher's own line may carry a flag it refuses after `--`; KPI line 5's "no `CLAUDE_CODE_AUTO_COMPACT_WINDOW` in the session's environment" falls on W2-56's cleaned environment (this ticket keeps it out of the settings and refuses it after `--`, and does not edit the `env=` line).
- Name each existing line or block of today's `launcher.py` this ticket changes, and the new lines it adds, by what they do. W2-05 holds `src/gov/**/*.py` for the git environment of git calls: those lines are left as they are. W2-20 holds `src/gov/launch/gate*`: untouched. If the design needs a change in another ticket's file, it is a package.

**C. Every existing test the change touches.** After this ticket, a repository with no role file, or with a role file that has no default line, is refused. List **every unit and acceptance test** whose repository lacks either and that launches (or calls the launcher) and would therefore be refused: look at least at `tests/acceptance/W1-28`, `W1-32`, `W1-46`, `W1-49`, `W2-50`, `W2-58`, and `tests/unit/launch/`, and at every other acceptance folder whose tests call `gov launch` or the launcher (search named folders; for example `W1-07`, `W1-26`, `W1-30`, `W1-33`, `W1-35`, `W1-38`, `W1-40`, `W1-42`, `W1-48`, `W1-50`, `W2-54`, `W2-59`, `W2-62`). For each, by file and case (or by file with a count where every case of the file is alike), say which of these it is and how it is handled — **never by a fallback that launches without the role: that fails open**:
- (i) it copies **this repository's own role files** into its repository: refused until W2-11 writes their default line; nothing is changed for it, and the orchestrator holds the merge until W2-11;
- (ii) it builds a repository with **no role file at all**, or one of its own without a default line: its meaning changes; for an acceptance test, the independent test designer revises it with `Rewrite-Reason:` naming DEC-826 Q1 or DEC-839 item 5; for a unit test outside `tests/unit/launch/test_role*` and `test_launch_record*`, it is a package (W2-56 holds that folder);
- (iii) it reads the CLI line, the settings or the arguments in a way this change alters (for example, an expectation that `--agent` or `--session-id` passes through, or a test that counts the arguments): say how its expectation changes and who revises it;
- (iv) unaffected (say why, briefly).
You read those tests' code to classify them (they are earlier tickets' tests, open to you); you never read `tests/acceptance/W2-60a/`.

**D. What W2-11 must write** (for the orchestrator to carry): the default line's exact form; any version the loaded copies must carry; any skills line in the role files.

**E. Open points as packages,** each in six parts (context; what happened; why it matters; options with consequence, cost, risk and what they change; recommendation and confidence; what it blocks), only where you cannot decide on the ticket's ground.

Keep the note as short as its content allows. The estimate for the whole ticket's code is about 250 lines.

## Commit

Commit only these two files, in one commit, with the trailers in the final block. Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`.

    git add docs/changes/W2-60a-CIT-E.md docs/research/W2-60-rules-probe.md
    git commit -m "W2-60a: CIT-E (design before code) and the lead's rules-probe record" --trailer "Task: DAEO-cv58" --trailer "Role: engineer" --trailer "Implements: DEC-826, DEC-838, DEC-839, DEC-832, DEC-941" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2` and `git status --short`.

## Return

Your last message, complete in itself. The twelve fields come first, each as a labelled line, then the step-0 result, the commit's 12-digit hash, the default line's exact form (copied from the note), the test list's summary (counts per class (i) to (iv)), each package, the read refusals you met (count), and whether you used `gov retrieve`.

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
