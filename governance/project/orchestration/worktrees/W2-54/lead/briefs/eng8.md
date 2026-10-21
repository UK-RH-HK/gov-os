You are a fresh engineer. Ticket: DAEO-0rfi (W2-54), profile FULL, **run 5**, a short correction after the merge. You work only in the worktree `/home/usain/gov-os-worktrees/W2-54` on branch `w2/W2-54`. You were started through `gov launch`, under its OS sandbox. W2-54's code is merged into `w2/integrate`. One of your builder tests, `tests/unit/check/test_schema_audit_report.py::test_the_other_types_of_w2_02_stay_unknown`, asserts that W2-02's other types do not exist **in the tree**, so it is red on any tree that holds W2-02's merge. The orchestrator's DEC-874 (delegated, 2026-10-20; in this worktree's register) decides how it changes. You revise that one test, and **no code**.

## Step 0, before any work: the sandbox check (DEC-789)

Run these, in this order, and report their exact output **first** in your return (in `evidence`, and one line in `status`):

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0rfi','w').write('x')"` — a write outside your worktree. It **must fail**.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and then `git update-index --refresh` — git's own writes. They **must work**, or you cannot commit. Quote the exit codes.

**If (a) wrote the file, or (b) failed, stop there:** do nothing else, write nothing, and return with status `PACKAGES` and the exact outputs. Never delete the file (a) may have made: name it in your return.

## Standing rules (read first)

- Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-0rfi`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-54` and `w2/W2-54`), and `git log --oneline -1` (expect `49f1f81e`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. A foreground command is killed at 10 minutes: give long commands the Bash tool's `timeout: 600000`.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory first (DEC-836):** for what you need to know, ask `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m gov.cli.main retrieve "<question>" --json` before reading files at random. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- **Reads open, writes closed (Policy 2, DEC-820).** You read freely: the repository, git history, other worktrees and branches. Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); **(c) the counterpart's work on this ticket: you, the engineer, never read `tests/acceptance/W2-54/` (you may run those tests and see their names, results and failure messages);** (d) the hidden half of any evaluation set, by whoever is measured by it. Writes stay inside your path below.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. **Count the refusals you met and list them in your return.**
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no stash in this worktree.
- Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`. Never read or name the qualification oracle. Never write `governance/project/`.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **No copy of the tree:** never `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it, anywhere; a test reads other commits through `git show <commit>:<path>`, `git log` and `git diff` (nothing is checked out), or builds a temporary repository from scratch in its `tmp_path`. Copy single named files only, never `governance/project/`. No clone, copy or file of a programme under a `.gov-runtime/` folder (DEC-673).
- Never write the main tree (`/home/usain/Dynamic-Agentic-Engineering-OS/`, its `.gov-runtime/` included) or another worktree (other leads run beside you).
- You need no Ollama for this change. Never stop, restart or reconfigure any server you did not start; never pull, remove or create a model.
- **What the lead runs, not you:** the full rebuild, `gov check`, every acceptance suite, and every measurement on the shared embedder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. The sandbox may show placeholder files in the worktree (`.bashrc`, `.mcp.json`, `docs/source`, …): never commit them.
- Never run `gov rebuild --no-embeddings`. Never run `gov close`, `gov adopt` or `gov pause`. Never ask or notify the owner (no question box, no `owner-ping`).
- The guard refuses here-documents, shell appends and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. Keep throwaway files in your session's temporary folder. No subagents. Install nothing. No push, merge, rebase or tag.
- Never edit `docs/audit/wave-1/W1-43-wave-1-exit-audit.md`. Never edit `tests/acceptance/**`. Never edit anything under `src/`.
- The git hooks are uninstalled: before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## The change (DEC-874, decided)

The test today:

```python
def test_the_other_types_of_w2_02_stay_unknown():
    assert "close" not in schema.SCHEMA_MAP and "adoption-verdict" not in schema.SCHEMA_MAP
    assert schema.STANDALONE_TYPES == ("probe", "audit-report")
```

**DEC-874 item 1:** KPI S4 ("the `audit-report` type exactly as W2-02 defines it … nothing of W2-02's other types", DEC-768 item 1) is about **W2-54's own change, not about the tree**: **W2-54's own commits bring in no schema file and no type of W2-02's beyond `audit-report`**, which holds before and after W2-02 merges.

Revise this one test to that meaning:
- W2-54's own commits are the non-merge commits whose `Task:` trailer is `DAEO-0rfi` (W2-02's carry `Task: DAEO-zflj`; a merge of `w2/integrate` into this branch is not W2-54's own change). Read them through `git` only (for example `git log --no-merges --format=... ` over the trailer, and `git log --no-merges -p -- src/gov/check/schema.py` / `--name-status`, each commit against its parent). The test fails, naming the commit, if one of them adds a `close.schema.json` or `adoption-verdict.schema.json` file, or a line to `src/gov/check/schema.py` that adds `close` or `adoption-verdict` to `SCHEMA_MAP` or to `STANDALONE_TYPES`.
- It must pass **both** on this branch **and** on a history that holds W2-02's types: W2-02's branch commit `4ce16df2` holds W2-02's types merged with `w2/integrate`, and every W2-54 commit is among its ancestors. Make the test judge both `HEAD` and `4ce16df2` (for example a parametrisation over the two revisions; the test keeps its name), through `git` only.
- Keep it a strict check: show it would fail on a broken history (for example a second test or a parametrised case over a temporary repository built from scratch in `tmp_path`, in which a `Task: DAEO-0rfi` commit adds `"close"` to a `SCHEMA_MAP` line, which fails; and a `Task: DAEO-zflj` commit doing the same, which passes). You may restructure the reading into a small helper inside this test file.
- **No other test changes.** No other file changes. Nothing under `src/` changes. Nothing is deleted or skipped.

## The runs, each to its end, never `-x`, each with `timeout: 600000`

1. Step 0, then the start checks and the `gov.__file__` line.
2. Before the change: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/unit/check/test_schema_audit_report.py -q -p no:cacheprovider` (expect green on this branch today).
3. After the change: the same file (expect all green, the new parametrisations named), then `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/unit -q -p no:cacheprovider` (all of it; expect 0 failed; name every failure with its output), and `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` (quote its last line; no collection error).
4. The red demonstration above, with its output.

## Commit

Commit only `tests/unit/check/test_schema_audit_report.py`, one commit, with the trailers in the final block (DEC-182, DEC-476, DEC-491):

    git commit -m "W2-54 (DAEO-0rfi): run 5: <subject>" --trailer "Task: DAEO-0rfi" --trailer "Role: engineer" --trailer "Implements: DEC-773" --trailer "Rewrite-Reason: DEC-874 (orchestrator, delegated, 2026-10-20): <...>" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After the commit, check `git log --oneline -2` and `git status --short`: a commit you did not make, stop and say so.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Nothing comes before the twelve fields. Refused twice for the same call, stop and say so.

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

In the fields: the sandbox check's result first; your commit's hash; the test before and after; the runs with their counts; the red demonstration; the `gov.__file__` line; the collection's last line; whether you used `gov retrieve`; the guard read refusals you met (DEC-849); any package.
