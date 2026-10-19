You are a fresh product-spec worker, in ticket mode. Ticket: DAEO-ha8z (W2-49, "Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P)"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-49` on branch `w2/W2-49`. The owner has approved the ticket's change-impact proposal (CIT-P). You apply it: Contract v4.2, then the capability records, in three commits.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-ha8z`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-49` and `w2/W2-49`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your last commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree. A correction is a new commit.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it.
- **`docs/source/`:** nobody reads it, except the one named read below, which is yours, by exact name, of two sections only.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov close`, `gov adopt`, `gov pause` or `gov rebuild --no-embeddings`. Never run `docs/plan/tools/validate_s1.py` (DEC-738).
- **The git hooks are uninstalled until W2-08.** Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). (For the named read, once is enough: see below.)

## What you read

- The ticket file `.tickets/DAEO-ha8z.md` (read-only): its KPI lines, `allowed_paths`, sources and last note.
- The ticket's acceptance tests and their README, `tests/acceptance/W2-49/` (read-only, all of it). They are the check of your work.
- The approved proposal, `docs/changes/W2-49-CIT-P.md`, in full. **§6 is the text you apply**, with the owner's answers below; §3, §4, §7 and §8 explain it.
- The Contract, `docs/contract/contract.yaml` and `docs/contract/CONTRACT_v4.md` (version 4.1 today), and the capability records `docs/contract/capabilities/*.md` (273, DERIVED from `contract.yaml`, DEC-614).
- In `docs/DECISION_REGISTER.md`: DEC-722, DEC-006, DEC-058, DEC-090, DEC-105, DEC-614, DEC-620, DEC-723, DEC-732. Cite a decision for a rule only after reading that it says it.

## The owner's decision (DEC-741, 2026-10-17; staged for the owner's commit, not yet in this worktree's register)

The CIT-P is approved, apply now, each question with the CIT-P's recommended answer:
- **A (a1):** CAP-43.b, CAP-44.f and CAP-44.h keep their ids for the lite Wave 2 part (`wave: W2`); new ids carry the Wave 3 rest: CAP-43.d, CAP-44.k, CAP-44.l (as §6.1).
- **B (i):** lite CAP-43.b holds the manifest and the file hashes only; CAP-43's wave note says release contents of CAP-43.d built before W3 are ahead of that item's wave, and names no ticket (as §6.1).
- **C (i), with (ii) as fallback:** the named read below. With the list, v4.2's CAP-44.h lists the ten ADOPTED_HEALTHY conditions, each marked lite W2 or W3, plus G's three lite conditions. Fallback (ii): CAP-44.h states the lite conditions in the Contract's own items, as §3.1 and §6.1 do, and the ten stay with CAP-44.l in W3.
- **D (ii):** CAP-45.a gets a Wave 2 wording: in Wave 2 the authenticated source is the release's manifest and file hashes (CAP-43.b, lite); the signed tag goes with CAP-02.c (W3); DEC-722. Every mention of the signed tag in CAP-45.a carries its Wave 3 qualifier. Its `wave` stays W2.
- **E (i):** DEC-741 amends DEC-090 in part (the owner's register entry). CAP-54.a stays as written: its target is the W3 verdict (CAP-44.l).
- **F (i):** as §6.1's CAP-44.h: the auditor reports each lite condition as met or not met; ADOPTED_HEALTHY when every lite condition is met; ADOPTED_WITH_ACCEPTED_EXCEPTIONS when each condition not met is accepted by name in an owner decision (`Role: owner`); otherwise NOT_ADOPTED_HEALTHY; only the owner accepts an exception, the auditor accepts none; the verdict record names itself lite and names the conditions it does not check.
- **G (i):** the lite conditions add `gov doctor` green (exit 0), `gov check` with no RED family, and one ticket closed by `gov close` at exit 0 with the repository's own test command (as §6.1).
- **H (i):** the new ticket that builds the lite A7 and A10 stage records is W2-52 (DAEO-siiz). The Contract names no ticket for it (§6.1: `provider` on the three W2 items stays none, pending the plan validator's Wave 2 form). Not your files otherwise: the change records name it.
- **I, J:** other tickets' work.
- **K, the capability records follow v4.2.** (1) The owner's answer: **the version line in all 273 records** — one commit. (2) A reading staged for the owner's commit, to be confirmed or overturned: **the records CIT-P §8 names as rewritten from the approved `contract.yaml`** — CAP-43.b, CAP-44.f and CAP-44.h (new title, item and wave), the new CAP-43.d, CAP-44.k and CAP-44.l, and CAP-43 and CAP-44 (their "Covers:" lists). **They go in a commit of their own**, separate from the version-line commit, so that a revert can drop them alone.
- **Row W2-L343:** `contract.yaml` says `status: PROPOSED` and `CONTRACT_v4.md` says `status: ACCEPTED`. After the apply both files state the same status for v4.2. The CIT-P states none for v4.2, so both say **ACCEPTED** (the owner's approval, DEC-741).
- **Not decided, not yours:** the eight rows of `docs/contract/SOURCE_MAP.csv` (CIT-P §8). Leave that file alone. The plan validator lines wait for W2-51 (DEC-744).

## The named read (C (i)), for this apply round only

- You alone, and only these two sections: **Adoption Protocol v3.0 §20** and **Distribution Protocol v1.2 §18**, the originals kept as provenance (DEC-058).
- Find each file **by its exact name** from `docs/SOURCES.md` (its "Carried files" table) or `docs/contract/SOURCE_MAP.csv`, never by listing, globbing or searching `docs/source/`. `docs/SOURCES.md` says how an original is read: `git show bb6ec3a8d8242fda7a76f86f0f0eff46813bc65f:docs/source/<path>`. Run no `git ls-tree` and no listing of that tree.
- To find the section's line range you may print the heading lines of that one file only (e.g. pipe the `git show` into `grep -n '^#'`); then print only the section (e.g. `sed -n '<start>,<end>p'`). Read nothing else there, and keep no copy of it in the tree.
- Quote in your return, for each: the file, the section heading and the line range you read.
- **Fallback (ii):** if a file cannot be named exactly, or the guard refuses the read (**once is enough; no second try, no other way round**), write CAP-44.h by fallback (ii) and say which way you went and why.
- With the list: number the ten (1) to (10) inside CAP-44.h's item, each marked lite W2 or W3. Mark a condition W2 only where the Contract's own Wave 1 or lite Wave 2 items deliver it (CIT-P §3.1's "checks" rows); a condition that rests on A9, A11, CAP-48.b, CAP-44.g, CAP-44.i, CAP-02.c or CAP-47.a's role separation, in whole or in part, is W3 (say "W3" and, if part of it is checked lite, which part). Keep G's three as lite conditions of their own. Report each of the ten with its mark and your reason: the CIT-E records it. The F rule then reads "every lite condition" as the conditions marked W2 plus G's three.

## Ticket mode: what you write

Only these paths: `docs/contract/contract.yaml`, `docs/contract/CONTRACT_v4.md`, `docs/contract/capabilities/**`. Never the acceptance tests (MR-3), never `docs/changes/` (the next worker writes the CIT-E), never `docs/contract/SOURCE_MAP.csv`. A test you think is wrong is returned as a package, never edited and never worked around. Add no rule of your own: every rule comes from the CIT-P §6 text, the answers above or a named source.

**Commit 1 — Contract v4.2.** Both files, as CIT-P §6.1 and §6.2 state, with the answers above:
- `version: '4.2'`, `revised: '2026-10-17'`; the change-log entry and the markdown change row as §6.1, dated 2026-10-17, also naming CAP-45.a's Wave 2 wording (D), the named read's outcome for CAP-44.h (C), the status ACCEPTED in both files (W2-L343) and the owner's approval (DEC-741). 4.0 and 4.1 entries unchanged.
- `status: ACCEPTED` in `contract.yaml`; the markdown frontmatter stays ACCEPTED; DEC-722 added to its `decisions`. Title line and "Version 4.2 (2026-10-17)" line as §6.2.
- CAP-43, CAP-44, CAP-47 wave notes, provider and sources as §6.1; covers items CAP-43.b, CAP-43.d, CAP-44.f, CAP-44.h, CAP-44.k, CAP-44.l as §6.1 (CAP-44.h under C as above); CAP-45.a as D. `CONTRACT_v4.md` follows the YAML line for line, in its own covers-line form. §1 Counts unchanged; nothing else changes.
- Run the suite (command below). Expected after commit 1: every test passes except those that read the change records (`test_w2_49_cit_e.py`, and the two W2-52 tests in `test_w2_49_owner_answers.py`) and the capability-record tests (K (1) in `test_w2_49_owner_answers.py`, all of `test_w2_49_capability_records.py`).
- `git commit -m "W2-49 (DAEO-ha8z): Contract v4.2, lite, as the approved CIT-P (DEC-741)" -m "<body: what changed; names DEC-741 and the named read's outcome>" --trailer "Task: DAEO-ha8z" --trailer "Role: product-spec" --trailer "Implements: DEC-722, CAP-43.b, CAP-44.f, CAP-44.h, CAP-45.a" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`

**Commit 2 — the version line in all 273 records.** You may write a small throwaway script under `/home/usain/gov-os-worktrees/W2-49/.gov-runtime/scratch/ps-run2/` (not committed) that changes, in each of the 273 records, only the words that cite the Contract version ("Contract v4, version 4.1" → "Contract v4, version 4.2") and nothing else. Check with `git diff --stat` that exactly 273 files change, one line each, and look at a few diffs. Do not change any record's title, item, wave, status or covers here.
- `git commit -m "W2-49 (DAEO-ha8z): the capability records cite Contract version 4.2 (DEC-741 K)" -m "<body: the version line only, by a throwaway script; DEC-614; names DEC-741>" --trailer "Task: DAEO-ha8z" --trailer "Role: product-spec" --trailer "Implements: DEC-722, DEC-614" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`

**Commit 3 — the CIT-P §8 records (the orchestrator's reading, for the owner to confirm or overturn).** Rewrite from the approved `contract.yaml`, in exactly the form of their sibling records (frontmatter fields and values as the siblings, title from the item, body lines as the siblings): CAP-43.b, CAP-44.f, CAP-44.h (title, item, wave); new CAP-43.d, CAP-44.k, CAP-44.l; the "Covers:" lists of CAP-43 and CAP-44. Nothing else — **not** CAP-45.a's record (its item text is not in the reading: leave it, and report it), not CAP-47's, not any status line.
- `git commit -m "W2-49 (DAEO-ha8z): the records of the split and moved items follow Contract v4.2 (the orchestrator's reading of DEC-741 K, CIT-P §8)" -m "<body: the eight records; a separate commit so a revert drops it alone; DEC-614; names DEC-741>" --trailer "Task: DAEO-ha8z" --trailer "Role: product-spec" --trailer "Implements: DEC-722, DEC-614, CAP-43.b, CAP-44.f, CAP-44.h" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`

After each commit: `git log --oneline -2`, `git status --short` and `git log -1 --format='%(trailers)'`, quoted. Remove your throwaway script folder before you return.

## Tests

Run, in the foreground, to the end, never with `-x`, after each commit:
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src python3 -m pytest tests/acceptance/W2-49 -q -p no:cacheprovider -rs`
After commit 3 every test passes except the 11 in `test_w2_49_cit_e.py` and the two W2-52 tests (the next worker's). Then the other suites that read the Contract or a capability record:
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src python3 -m pytest tests/acceptance/W1-48 tests/acceptance/W1-41 tests/acceptance/W1-30 -q -p no:cacheprovider -rs`
They must stay as green as before your change; a red one is reported by name with its output (check whether it was red before by its message, never by checking out another commit).

## Return

Your three commits with their trailers; the files written; each suite's counts after each commit; the named read's outcome (C (i) with the file, heading and line range read for each, or fallback (ii) with why); with C (i), each of the ten conditions with its mark and reason; every place where you departed from CIT-P §6's text and why (the next worker's CIT-E lists each difference); what no source settled; anything refused, as a package.

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | LEAD_CHECKPOINT | AUTH_REQUIRED, and one line of why>
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
