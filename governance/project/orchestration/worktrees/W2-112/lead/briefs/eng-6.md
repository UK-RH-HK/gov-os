You are a fresh engineer. Ticket: DAEO-clon (W2-112), profile FULL: "One reranker serves every session: a shared, on-demand reranker service on the GPU". You work only in the worktree `/home/usain/gov-os-worktrees/W2-112` on branch `w2/W2-112`. This is the last change before the ticket lands: one section of the research record, rewritten to a KPI line the owner has re-baselined (DEC-1048). The code is done and reviewed; you change no code.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-clon','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-clon`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-112` and `w2/W2-112`). If anything differs, stop and say so.
- Run everything in the foreground. Return only after your commit exists. No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, rebase, merge, push or tag.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json`. Never read, print, search, diff or copy the held-out material under `governance/project/`, and never type its path (DEC-525); never read or name the qualification oracle; never print a secret (DEC-820 (a), (b)). Never write in `~/gov-os-workbench`.
- **Policy 2 (c) and (d) (DEC-820):** (c) you never read `tests/acceptance/W2-112/` by any tool, here or in `/home/usain/gov-os-worktrees/W2-112-tests` (you may run those tests only through `gov accept` and see their results; you do not run them in this batch); (d) nobody reads `fixtures/evaluation/*/hidden/`.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-112/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query (DEC-860: batches with `--batch-size` and `--continue <token>`); a code question (DEC-859) uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **Read refusals (DEC-849):** the guard still refuses some reads (searches from the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead; count them in your return.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-112/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-112/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools and literal absolute paths.
- Install nothing. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. No clone or copy of the repository (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never the full 40; never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule").
- **No gitleaks scan anywhere (DEC-1045).** Run no real reranker, touch no GPU, never take or remove `/tmp/gov-os-rerank-gpu-*.lock`, never touch `~/.local/share/gov-os/reranker-venv`.
- **Scratch budget (DEC-898):** 1 GB and 50,000 files and folders, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-112` (keep the sandbox's own temp folder where it sets one, and count it); remove what you make; measure it at the end (`du -s --inodes`, `du -sh`) and give the figures in `evidence`. Passing it: stop, clean, return.
- Refused twice for the same call: stop and say so; no third try (AR-6). If the guard or the sandbox refuses something you needed, return it as a package. An authentication or access error: stop and return `AUTH_REQUIRED`.

## What you read

- `.tickets/DAEO-clon.md` (as merged at this head, re-baselined by the owner): KPI success-7 and the `allowed_paths`.
- `docs/research/W2-112-shared-reranker.md`: all of it, above all §5.
- In `docs/DECISION_REGISTER.md`: DEC-1048 (the decision), DEC-1047, DEC-1033, DEC-1031 (item 2), DEC-1036, DEC-1043.
- `governance/project/orchestration/packages/P-W2-112-F9.md` (the owner chose (c), with (b) as the later path), `governance/project/orchestration/packages/ACT-RERANK-GPU-SLOTS-1.md`, `governance/project/orchestration/packages/ACT-RERANK-WAIT-1.md`.

## The change (KPI success-7 as re-baselined, DEC-1048: P-W2-112-F9 (c))

§5 today is an ACT that tells the operator to remove the interim GPU-slot module and its `.pth` once two checks pass. The second review (F9) found that the checks hold only at the moment they run: ordinary work brings old trees back afterwards (a removed worktree re-created from an old branch, an older base checked out for a red check or a bisect, the old pin kept for rollback), and an old tree's reranker, without the module, loads on the GPU beside two held slots (DEC-1031's crash state). The owner chose (c). Rewrite §5 so that it:

1. records that the module and its `.pth` are **not to be retired by an ACT now**: they stay in place as the machine-wide guard that caps every reranker, whatever its tree's commit; beside W2-112's own worker the module is harmless (it already holds the slot in that process, and the worker takes nothing more);
2. states why, in a few sentences (F9, as above);
3. names the retirement path, P-W2-112-F9 (b): the module is retired **only when old code fails closed by construction** (for example, the reranker environment moves to a path that only W2-112-or-later code knows), in **a later ticket**; not in W2-112;
4. gives the operator **no step that removes** the module or its `.pth` (drop the removal commands, the two-check precondition and its undo; a read-only check that the module is still installed is fine if useful);
5. keeps the rule that the slot lock files `/tmp/gov-os-rerank-gpu-0.lock` and `-1.lock` (any `gov-os-rerank-gpu-<n>.lock`) are **never removed**, with its reason.

Keep §5 the document's last section, with a heading that names the stopgap (ACT-RERANK-GPU-SLOTS-1) and that it stays; drop "ACT: retiring" from its title, since there is no retirement now. Keep it short and plain. If another place in the document says the module is to be retired by this ticket or by an ACT (for example in §1's "The stopgap's slots"), make it agree; change nothing else.

## What you write

- Only `docs/research/W2-112-shared-reranker.md` (in the ticket's `allowed_paths`); nothing else.
- Commit only that file, with the trailers in the final block; check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); never `--no-verify`:

      git commit -m "W2-112 (DAEO-clon): §5 re-baselined: the GPU-slot stopgap stays as the machine-wide guard, retired only when old code fails closed (DEC-1048)" --trailer "Task: DAEO-clon" --trailer "Role: engineer" --trailer "Implements: DEC-1048,DEC-1033" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- docs/research/W2-112-shared-reranker.md

- You do not run `gov accept` in this batch: the lead runs the acceptance tests after merging the test designer's revision.

## Return

One message, your last, complete in itself: the twelve fields first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), any payload after. Put the sandbox check's result first inside `evidence`. Give: the commit hash (12 digits), the lines added and removed, §5's new heading, the `gov.__file__` line, the read refusals (count), your `gov retrieve` use, your scratch figures.

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
