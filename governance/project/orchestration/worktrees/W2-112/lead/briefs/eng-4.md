You are a fresh engineer. Ticket: DAEO-clon (W2-112), profile FULL: "One reranker serves every session: a shared, on-demand reranker service on the GPU". You work only in the worktree `/home/usain/gov-os-worktrees/W2-112` on branch `w2/W2-112`. This is a small repair after the FULL review's first round: one section of the research record. The code is done and accepted; you change no code.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-clon','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-clon`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-112` and `w2/W2-112`). If anything differs, stop and say so.
- Run everything in the foreground. Return only after your commit exists. No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, rebase, merge, push or tag.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json`. Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525); never read or name the qualification oracle; never print a secret. Never write in `~/gov-os-workbench`.
- **Policy 2 (c) and (d) (DEC-820):** you never read `tests/acceptance/W2-112/` by any tool; nobody reads `fixtures/evaluation/*/hidden/`.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-112/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query (DEC-860: batches with `--batch-size` and `--continue`); a code question (DEC-859) uses the code-graph tool's own traversal, small and targeted.
- **Read refusals (DEC-849):** the guard still refuses some reads (searches from the repository root, `governance/project/` or `.claude/`). Take the refusal, never another form; count them.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-112/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-112/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools and literal absolute paths.
- Install nothing. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. No clone or copy of the repository. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits; never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule").
- **Scratch budget (DEC-898):** 1 GB and 50,000 files and folders; `TMPDIR=/tmp/gov-os-lead-W2-112` (keep the sandbox's own temp folder where it sets one); measure it at the end.
- Refused twice for the same call: stop and say so; no third try (AR-6). If the guard or the sandbox refuses something you needed, return it as a package. An authentication or access error: stop and return `AUTH_REQUIRED`.

## What you read

- `.tickets/DAEO-clon.md`: KPI success-7 and the `allowed_paths`.
- `docs/research/W2-112-shared-reranker.md`, above all its last section (§5, the owner's ACT retiring the GPU-slot stopgap).
- `governance/project/orchestration/packages/ACT-RERANK-GPU-SLOTS-1.md`, `governance/project/orchestration/packages/ACT-RERANK-WAIT-1.md`, `governance/project/orchestration/tools/gov_reranker_gpu_slot.py`; in `docs/DECISION_REGISTER.md`, DEC-1031 (item 2), DEC-1032, DEC-1033, DEC-1036.
- `src/gov/retrieval/rerank_worker.py` (to see that only this tree's worker carries its own slot rule).

## The finding to repair (round 1, F1; a described behaviour)

- **What was done:** §5 tells the operator to remove the interim module and its `.pth` from the reranker environment as soon as W2-112 has merged. It claims that this "changes nothing in behaviour". Its step 3 lets the operator remove the slot lock files `/tmp/gov-os-rerank-gpu-0.lock` and `-1.lock` once no process holds them.
- **What happened (the reviewer ran it):** only W2-112's own private worker carries the slot rule itself. The installed, pinned `gov` (`~/.local/bin/gov`, re-pinned only at ACT 2) and 64 other checkouts (the main checkout, the merge queue's clone, the worktrees) still start private rerankers with the old worker, which relies on the module alone. With the module removed, those rerankers loaded on the GPU beside two held slots: a third copy, the crash state DEC-1031 records. With the lock files removed while two rerankers held them, a new reranker took a fresh lock file and loaded: three on two slots.
- **What should happen:** the ACT's precondition is that the installed `gov` and every tree that can start a reranker carry the worker's own slot rule (in practice: after ACT 2's re-pin of the installed `gov` to a release that holds W2-112, and once no worktree, clone or checkout runs an older `rerank_worker.py`; give the operator a check for both). Until then the module stays, harmless beside W2-112's worker (it already holds the slot in that process, and the worker then takes nothing more). The ACT never removes, and never tells the operator to remove, the slot lock files: they are empty and must stay. Correct the "why it is safe" paragraph to match.

## What you write

- Only `docs/research/W2-112-shared-reranker.md` (in the ticket's `allowed_paths`); nothing else. Keep the section the document's last, titled as an ACT.
- Commit (`git commit ... -- docs/research/W2-112-shared-reranker.md`) with the trailers in the final block: `--trailer "Task: DAEO-clon" --trailer "Role: engineer" --trailer "Implements: DEC-1033,DEC-1032" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`. Check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file.
- You do not run `gov accept` in this batch (the lead runs the acceptance tests outside the sandbox, which they need).

## Return

One message, your last, complete in itself: the twelve fields first, each as a labelled line, any payload after. Put the sandbox check's result first inside `evidence`. Give: the commit hash (12 digits), the lines changed, the `gov.__file__` line, the read refusals, your `gov retrieve` use, your scratch figures.

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
