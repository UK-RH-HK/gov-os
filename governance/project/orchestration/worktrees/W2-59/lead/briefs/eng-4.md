# Brief: engineer — W2-59 (DAEO-kh9l), run 3: the CIT-P's commit ids after the branch was remade

You are a fresh engineer, doing documentation work in a code ticket. Brief A4's content scope applies: you write one document, inside the ticket's allowed paths, and nothing else. (The ticket's role is `engineer`; the launcher starts only an engineer on it, so an engineer does this.) Ticket: `DAEO-kh9l` (`W2-59`, "The pinned judge: the declared checks and the hook lines run from the pin; the packaging gaps"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-59` on branch `w2/W2-59`.

The ticket is implemented and verified. Its change-impact proposal, `docs/changes/W2-59-CIT-P.md`, names commits by their ids. The branch was remade under DEC-412 and DEC-877: every commit from the merge-back on got a new id, and the trees stayed the same. You bring the CIT-P's ids up to date and add one line saying so. **Nothing else in it changes:** no rewording, no new sections, no status change (`status: PROPOSED` stays), no reflow of untouched lines.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kh9l','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kh9l`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-59` and `w2/W2-59`) and `git log --oneline -1` (expect `3dbd766d`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. This task needs little: say in your return which questions you asked, if any, and whether the answers helped.
- **Reads are open, writes are closed (DEC-820, Policy 2).** You read freely: the repository, git history, other worktrees. Four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle; (c) **the counterpart's work on this ticket: you never read `tests/acceptance/W2-59/`** (no file there, by any tool, its README included); you may run those tests and read their names, results and failure messages; (d) the hidden half of any evaluation set, by whoever is measured by it.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. **Count every read refusal you meet and give the count in your return.** Never read `.claude/settings.json`.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need, do not work around it: return it as a package.
- Run everything in the foreground, one command after another. Return only after your commit exists.
- No `git checkout` of another commit (and never of the branch `w2/W2-59-old`), no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag. Install nothing; never `sudo`.
- **No copy of the repository:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it.
- Nothing goes under a `.gov-runtime/` folder (DEC-673), in `~/.local`, or in `~/gov-os-workbench` (never list or read it).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Write files with the Write and Edit tools, with literal absolute paths. No subagents that write. Never touch `tests/acceptance/**`, `.tickets/**` or `.gov-runtime/**`.
- **Write only `docs/changes/W2-59-CIT-P.md`.**
- Never ask the owner anything and never notify anyone (DEC-850, DEC-855): a question is a package in your return.
- You use your model's full window; nobody asks you to stop or compact early (DEC-838).

## What you read

- `docs/changes/W2-59-CIT-P.md` at the head.
- DEC-877 and DEC-412 in `docs/DECISION_REGISTER.md` (search the file for `### DEC-877` and `### DEC-412`).
- To check the map below, `git log --format='%h %s' c76cddf5..HEAD --first-parent` and, for the old ids, `git log --format='%h %s' c76cddf5..w2/W2-59-old --first-parent` (read-only; never check that branch out).

## The id map (old → new, DEC-877)

`3eadca4c`→`e48a601d` (the merge of `w2/integrate` at `74d22909`, now with `Task: DAEO-kh9l`, `Role: orchestrator`, `Implements: DEC-750, DEC-877`; git's own merge, the same tree `6b2943c8`), `6d4925ab`→`70cfbcf9`, `45c6bfae`→`912ddc63`, `fc8f8494`→`164d4c64`, `cface154`→`06250aee`, `9b9faac3`→`03727f84`, `6e95cd41`→`6e0bf627`, `e791465b`→`92f91614`, `3c2d88b5`→`0c630012`, `aa83876d`→`61d0a4a2`, `3d6a27f8`→`d3e594bf`. The new head's tree equals the old head's. Run 3 then merged `w2/integrate` at `97fc656a` into the branch as `3dbd766d` (with `Task: DAEO-kh9l`, `Role: orchestrator`, `Implements: DEC-750`).

## What must change

1. **Every old id the CIT-P names** (front matter, the opening paragraphs, §1 and every other section) **is replaced by its new id**, with one exception: the text that describes the old merge's missing trailer (the paragraph that begins "The merge `3eadca4c` carries no `Task:` trailer", and the P-W2-59-5 row of §7's package table) describes that old commit, so `3eadca4c` stays there (the new merge does carry the trailers, so the new id there would make a false statement). In that paragraph, `6d4925ab` still becomes `70cfbcf9` (the commit that now holds the correction note). Search the file for every id of the map's left side; at the head they appear in the front matter's `base:` line, the paragraph on the merge that brought W2-62's hook change and W2-50's fix, §4 (the bare `gov --version` observation and the `sessionstart.py` bullet), §6 (the re-check after the merge), §7 (A1), §8 (the revising commit) and §11 (twice). Keep each sentence otherwise as it is.
2. **One line added**, a short paragraph of its own, directly after the paragraph that ends "This is package P-W2-59-5, open with the orchestrator (§7).": it says, in the document's own plain style, that the branch was remade under DEC-412 and DEC-877 (P-W2-59-5 (a)); that `3eadca4c` is no longer on it and the same merge of `74d22909` is now `e48a601d`, which carries `Task:`, `Role:` and `Implements:` (git's own merge, the same tree); that the later commits were re-applied unchanged, so the paragraph above describes the old merge only; that the gate's reading of an untrailered merge is row W2-M394; and that run 3 merged `w2/integrate` at `97fc656a` by `3dbd766d`, with its trailers (DEC-750). Do not list the whole id map in it.

Check after editing: `git diff --stat` shows one file; `git diff` shows only id replacements and the one added paragraph; `grep -nE '6d4925ab|45c6bfae|fc8f8494|cface154|9b9faac3|6e95cd41|e791465b|3c2d88b5|aa83876d|3d6a27f8' docs/changes/W2-59-CIT-P.md` finds nothing; `3eadca4c` appears only in the exception's places and the added paragraph.

No test suite is needed for a document change; run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -c "import gov; print(gov.__file__)"` and quote it.

## Commit

One commit (a second only to correct the first, never an amend):

    git commit -m "W2-59 (DAEO-kh9l): the CIT-P names the remade branch's commits (DEC-877)" --trailer "Task: DAEO-kh9l" --trailer "Role: engineer" --trailer "Implements: DEC-877, CAP-33" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- docs/changes/W2-59-CIT-P.md

Check `git log --oneline -2` and `git status --short` after it.

## Return

Your last message, complete in itself. In `evidence`: the sandbox check's result (first), your commit hash with its trailers, the `gov.__file__` line, each replacement made (line, old, new) and the added paragraph's text. Also give: the number of guard read refusals you met, and the `gov retrieve` questions you asked.

**The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
