# W2-139 — the product-spec worker's brief (DAEO-ongl)

You are the product-spec worker for **W2-139** (`.tickets/DAEO-ongl.md`): the approved CIT-P note applied to the
Contract as version 4.3, CAP-45 and CAP-45.a to Wave 3 (the owner's DEC-1093 (1): V (i), A (i), C (i), R (a), T (i),
N (b)). Read the ticket in full first; its KPI lines S1 and S2 and its failure lines are what you deliver (S3 is the
CTO's batch merge, not yours).

## The sources
- **DEC-1093** in `docs/DECISION_REGISTER.md` (heading `### DEC-1093`), and DEC-1099 (3) and DEC-1109 (2) for the batch.
- **The approved note**, not on `w2/integrate`: `git -C /home/usain/gov-os-worktrees/W2-139 show 33f72aab2:docs/changes/W2-27-CIT-P.md`.
  §5.1 to §5.5 are the exact edit; §4 rows 1 to 7 and 27 the impact on the Contract files; §7 the questions the owner
  answered. Its review: `governance/project/orchestration/reviews/w2-27-citp.md`.
- **The precedent:** W2-49's apply, `docs/changes/W2-49-CIT-P.md` (frontmatter after approval) and
  `docs/changes/W2-49-CIT-E.md` (the change-execution record's form). The schemas:
  `template/governance/kernel/schemas/change-impact-proposal.schema.json` and the CIT-E's beside it.

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-139`, branch `w2/W2-139`: `w2/integrate` with W2-140's revised
  acceptance cases (`w2/W2-140-tests`) merged in by the CTO.
- **Your paths (the ticket's, nothing else):** `docs/contract/contract.yaml`, `docs/contract/CONTRACT_v4.md`,
  `docs/contract/capabilities/**`, `docs/contract/SOURCE_MAP.csv`, `docs/changes/W2-27-CIT-P.md`,
  `docs/changes/W2-27-CIT-E.md`.

## The work
1. **The note, as approved, onto this branch:** `docs/changes/W2-27-CIT-P.md` = the note at `33f72aab2` with the owner's
   answers written into it, as W2-49's was: `status: ACCEPTED` (check the schema's allowed values), an `accepted:` line
   (owner, 2026-11-07, DEC-1093 (1), apply now) and a short closing section recording V (i), A (i), C (i), R (a) with
   W2-139 (`DAEO-ongl`), T (i) with W2-140 (`DAEO-5ce2`), N (b). Leave its body otherwise as it is. **Keep every patch
   block a ```` ```diff ```` block; write no ```` ```yaml ```` block anywhere in it** (the validator's
   `cit-p-lines-applied` reads any `- id:`/`wave:` pair in a yaml fence; the note's §4 row 19 and §9 F-3).
2. **The Contract edit, exactly the note's §5,** with `DEC-OWNER` = **DEC-1093** and `APPLY_DATE` = the apply commit's
   date (today, 2026-11-09, unless the commit falls on another day):
   - §5.1 `contract.yaml` (header, the 4.3 `change_log` entry after 4.2's, CAP-45 and CAP-45.a); keep the YAML valid
     (load it with `yaml.safe_load` after the edit) and keep the `''` quoting.
   - §5.2 `CONTRACT_v4.md` (frontmatter, title, version line, the `| 4.3 |` row after 4.2's, §1 Counts, the CAP-45 block).
   - §5.3 the records: `CAP-45.a.md` and `CAP-45.md` as given; in each of the other 274 capability records the one
     occurrence of `(Contract v4, version 4.2)` becomes `(Contract v4, version 4.3)`, nothing else. First count: all 276
     hold it exactly once. The six master-rule records under `docs/contract/master-rules/` are not touched (not in your
     paths). Do it with a throwaway script in your own `TMPDIR`, never committed.
   - §5.4 the three `SOURCE_MAP.csv` rows (107, 224, 286): `wave W2` → `wave W3`; row 222 and every other row unchanged.
   - C (i), DEC-1093: the "in Wave 2" clause withdrawn; the manifest and file hashes kept beside the signed tag in
     CAP-45.a's authenticated source, exactly §5.1's wording.
   - Nothing the note does not name (the ticket's failure line A). The orchestrator's edits (the note's §4 rows 9, 10,
     12, 14, 16, 24: the WBS, W2-17, W2-27, W2-47, the register) are **not yours**.
3. **Check it:** the counts after the edit (capabilities W1 42 / W2 6 / W3 12 / NONE 2; covers W1 149 / W2 19 / W3 39 /
   NONE 7, from `contract.yaml`); the two Contract forms agree on every wave; `git diff --stat` shows 279 changed Contract
   files plus the two change records; `python3 docs/plan/tools/validate_w2.py` with `PYTHONPATH` set — read its lines:
   `contract-items-delivered` and `contract-items-cited-by-tests` list 19 Wave 2 items without CAP-45.a,
   `cit-p-lines-applied` lists no line of W2-27's note (report the lines and the exit; the validator is advisory, F-2).
4. **The suite you are built to:** run `python3 -m gov.cli.main accept W2-140 --root /home/usain/gov-os-worktrees/W2-139`
   with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-139/src` **and `GOV_TESTS_OPTIN=breadth,lifted`** (without it the
   default run leaves out three named cases and fails closed; with it all 160 cases run), and read only its result
   (KPI lines, counts). It must be all green: 160 passed. If a line fails, fix your edit against the note, never against the tests; if you believe the note and the
   suite disagree, stop and report it as a decision package (do not guess).
5. **The CIT-E** `docs/changes/W2-27-CIT-E.md`, in W2-49-CIT-E's form (`type: change-execution-record`,
   `status: APPLIED`, `proposal: W2-27-CIT-P`, `approved_revision: 33f72aab2`, the decisions carried DEC-1089 and
   DEC-1090 and the approval DEC-1093): it names the apply commit (commit the Contract edit first, then the CIT-E in a
   second commit naming the first), confirms each part of §5 against the diff, section by section, and lists each
   difference from the note with its reason, or states there is none; it says it supersedes W2-49-CIT-P §7 D (ii)'s
   clause (the note's §4 row 8), and that the batch merges with W2-140 on one green run (S3, the CTO's).

## Rules
- **You never read `tests/acceptance/W2-49/`** (W2-140's cases, the suite that judges you; DEC-820 (c), DEC-1056): not by
  Read, Grep, Glob, cat, git show, git diff or any other tool. Run it only through `gov accept W2-140` and read only its
  results. **The exclusion line (DEC-1093 (2)):** every Grep or Glob call that could reach that folder carries
  `!tests/acceptance/W2-49/**`, and every recursive Bash search the matching base-name exclusion
  (`grep -r --exclude-dir=W2-49`: grep matches the folder's BASE NAME only, a path excludes nothing;
  `git diff -- . ':(exclude)tests/acceptance/W2-49'`). If a search shows you any line from there anyway, stop reading it
  and say so in your return.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No GPU, no model, no network, no installs, never the full suite.
- **Search again once (DEC-1092 (1)):** if a search (Grep and Read; no `gov retrieve` in the sandbox,
  `EMG-d4b-launched.md`) does not answer, search once more in your own, different words; then answer from both, with
  path and lines, or say "not found". Two searches in all.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains; one line
  before any command that will ask for permission.
- **Do not merge `w2/integrate` or any branch yourself.** Never touch `tests/**`, `.tickets/`, `.claude/`,
  `docs/plan/**` or `docs/DECISION_REGISTER.md`.
- **Commit** on `w2/W2-139`, only your paths, with
  `--trailer "Task: DAEO-ongl" --trailer "Implements: DEC-1093" --trailer "Role: product-spec" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Before you end your session,** make sure every run you started has finished.
- Keep to the estimate: about 1 to 2 hours.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it in this worktree's log; it is
the record): the twelve labelled fields of `EMG-common.md`, with the sandbox check and the `ps` check first, the commits,
`git diff --stat`'s summary, the counts after the edit, the validator's lines, `gov accept W2-140`'s counts, and every
difference from the note (or "none").
