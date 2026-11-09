# W2-140 — the independent test designer's brief (DAEO-5ce2)

You are the independent test designer for **W2-140** (`.tickets/DAEO-5ce2.md`): W2-49's acceptance suite revised for
Contract 4.3, where CAP-45.a and CAP-45 move to Wave 3 (the owner's DEC-1093 (1): V (i), A (i), C (i), T (i)). Read the
ticket in full first. Its KPI lines S1 to S3 and its failure line are what you deliver. Profile STANDARD. W2-49 is
closed, so this revision is new work (DEC-1088 (6)) and only an independent test designer does it (MR-3).

## The sources (read these, in this order)
- **DEC-1093** in `docs/DECISION_REGISTER.md` (search the heading `### DEC-1093`): the owner's answers. `DEC-OWNER` in the
  note is **DEC-1093**; `APPLY_DATE` is the apply commit's date, not known yet (never pin a day; a `YYYY-MM-DD` on or
  after 2026-11-07 is the most a case may require).
- **The approved CIT-P note**, which is not on `w2/integrate`: read it with
  `git -C /home/usain/gov-os-worktrees/W2-140-tests show 33f72aab2:docs/changes/W2-27-CIT-P.md`. What you test against:
  §4 row 18 (the red list), §5.1 to §5.5 (the exact text after the edit), §7 V, A, C and T (T (i) is your recipe), §8.
- **The review** `governance/project/orchestration/reviews/w2-27-citp.md`, finding F1 (the three cases the first red list
  missed: `test_w2_49_owner_answers.py:143`, `test_w2_49_source_map.py:115`, `test_w2_49_contract.py:77`).
- **The suite as it stands:** `tests/acceptance/W2-49/` (README, `w2_49_support.py` with `require_v42`, the eight test
  files) and the Contract at integrate: `docs/contract/contract.yaml`, `docs/contract/CONTRACT_v4.md`,
  `docs/contract/capabilities/CAP-45*.md`, `docs/contract/SOURCE_MAP.csv`, `docs/plan/tools/validate_w2.py`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-140-tests`, branch `w2/W2-140-tests`, made from `w2/integrate` today.
- You write only `tests/acceptance/W2-49/**` (the ticket's one path).
- **Your record:** your whole return (the twelve fields below) is your session's **final message**, in full: the
  launcher keeps it in this worktree's `.gov-runtime/scratch/lead/log/W2-140-designer.json`, which is the record (your
  session cannot write that folder itself, and its own scratchpad is deleted when it ends).

## What the revision must do (from the ticket's S1 and S2, the note's §7 T (i))
- **The helper:** `require_v42` reads "4.2 or later" (a numeric comparison of the Contract's version, so 4.3 and a later
  4.4 both pass, 4.1 fails), which fixes its 32 callers in one place. Keep its name or rename it, but every caller keeps
  its check.
- **`test_w2_49_contract.py:69` and `:77`:** the version is 4.2 or later; the 4.2 change-log entry is still there,
  unchanged from the base, and still cites DEC-722; the 4.0 and 4.1 entries unchanged. Add the 4.3 expectation: a
  change-log entry `4.3` (yaml) and a `| 4.3 |` row (markdown) citing W2-27-CIT-P, DEC-1093, DEC-1089 and DEC-1090.
- **The covers counts** (`test_w2_49_owner_answers.py:143`): W1 149 / W2 19 / W3 39 / NONE 7 (214), both sources;
  the capability counts W1 42 / W2 6 / W3 12 / NONE 2 (62) where the suite counts capabilities.
- **The two "exactly" tests** (`test_no_other_covers_item_changes_wave`, `test_no_capability_is_added_removed_or_changes_wave`):
  against the same base as today, the only wave changes are W2-49's own (CAP-44.f, CAP-44.h, CAP-43.b, to W2) plus
  CAP-45.a (covers item) and CAP-45 (capability) to W3, named as moved by DEC-1093. Nothing else moves.
- **The D (ii) tests** (`test_cap_45a_stays_w2_…`, `test_cap_45a_names_no_signed_tag_…`): CAP-45.a is W3 (both forms);
  its item names the authenticated source as the signed tag (CAP-02.c) **and** the release's manifest and file hashes
  (CAP-43.b), with no "in Wave 2" clause left (C (i): the hashes kept beside the signed tag).
- **K (1)** (`test_every_capability_record_cites_contract_version_4_2`): every capability record under
  `docs/contract/capabilities/` cites the version in force (read from `contract.yaml`), exactly once; the six
  master-rule records are not part of it (the note's §4 row 6).
- **The source map** (`test_w2_49_source_map.py:115`): rows 107, 224 and 286 differ from `ffc60703e373` exactly as §5.4
  says (`wave W2` → `wave W3`), named as moved by DEC-1093; no other row differs beyond W2-49's eight.
- **The validator edge case** (`test_w2_49_validator_lines.py:182`): built on an item that stays in Wave 2 (for example
  CAP-61.f; check it is W2 at integrate and is not moved by the note).
- **Each revised case** carries a comment line `# Rewrite-Reason: DEC-1093 (1) — <what changed>` in the function (or
  the helper); the README gets a short section listing every revision with its reason. **No expectation lowered beyond
  the owner's change: every 4.2 lite check is kept** (CAP-44.h, CAP-44.f A7 and A10, CAP-43.b, CAP-02.c, CAP-43.c and the
  rest).
- Add only what the ticket and the note's §5 need to pin the 4.3 text (CAP-45's wave, wave note, provider and sources in
  both forms; CAP-45.a's record `CAP-45.a.md` and `CAP-45.md` at W3, matching `contract.yaml`) where an existing case does
  not already check it. A small round: the helper, about ten revised functions, a few additions.
- **The README map** that `gov accept` reads must stay valid for the whole folder. Add a row-form table for W2-140's own
  lines (header `| KPI line | Test (node id) | On integrate | Why |`, one id `S1`, `S2` or `S3` in each KPI cell, the test
  in backticks with its full node id, as `tests/acceptance/W2-133/README.md`), naming the revised and added cases.

## S3: red on integrate for the right reason only
- Run the folder on your tree (still Contract 4.2): the cases that need the 4.3 text are red, and **every** red fails only
  because the Contract is still at 4.2 (the version, the counts, CAP-45/CAP-45.a's wave and text, the three rows, the
  records' version line). Every other case stays green. Report the counts and the list of reds with the reason of each.
- To show the cases go green on the approved text, you may build a throwaway copy of the four Contract inputs with the
  note's §5 applied in a temporary folder **only if the suite can be pointed at it without editing the suite**; otherwise
  say so. Never write the Contract files in your worktree.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** the Contract edit is W2-139's (`DAEO-ongl`); never open
  `/home/usain/gov-os-worktrees/W2-139` or the branch `w2/W2-139` if either appears, and never read the product-spec
  worker's files for it. You work from the note, the decisions and today's integrate files only.
- **The exclusion line (DEC-1093 (2)), for you:** keep every Grep, Glob and recursive Bash search inside your own
  worktree, never from `/home/usain/gov-os-worktrees/` or `/home/usain/`; every recursive Bash search carries
  `--exclude-dir=W2-139` (the folder's BASE NAME: grep matches base names only, a path excludes nothing), and every Glob
  or Grep that could reach it the matching `!**/W2-139/**`. If a search shows you a line of the implementation anyway,
  stop reading it and say so in your return.
- **Search again once (DEC-1092 (1)):** if what you searched (Grep and Read; no `gov retrieve` in the sandbox,
  `EMG-d4b-launched.md`) does not answer, or you can tell your answer may be incomplete, search once more in your own,
  different words; then answer from both searches and the files you read, with path and lines, or say "not found".
  Two searches in all.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No GPU, no model, no network, no installs.
- Run the folder with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-140-tests/src` (through the heavy slot that
  `EMG-common.md` names where the sandbox allows it), and run
  `python3 -m gov.cli.main accept W2-140 --root /home/usain/gov-os-worktrees/W2-140-tests` to show the runner reads
  your map (on integrate it fails, with the expected reds only). Never the full suite.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains; one line
  before any command that will ask for permission.
- **Commit** on `w2/W2-140-tests`, only `tests/acceptance/W2-49/`, with
  `--trailer "Task: DAEO-5ce2" --trailer "Implements: DEC-1093" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1093 (1): Contract 4.3, CAP-45 and CAP-45.a to Wave 3" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
  Never commit on `w2/integrate`; never merge.
- **Before you end your session,** make sure every test run you started has finished.
- Keep to the estimate: about 3 hours of work, a small round.

## Return
The twelve labelled fields of `EMG-common.md` (sandbox check and `ps` check first), with: every revised or added case
(node id, KPI line, red or green on integrate, and why), the Rewrite-Reason of each, the commit, the folder's counts on
integrate, `gov accept`'s counts, the `TESTS-READY <commit>` line, and anything untestable or ambiguous in the note as
`discoveries` or a decision package with your recommendation and confidence.
