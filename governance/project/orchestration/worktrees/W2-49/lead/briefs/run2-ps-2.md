You are a fresh product-spec worker, in ticket mode. Ticket: DAEO-ha8z (W2-49, "Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P)"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-49` on branch `w2/W2-49`. The owner approved the ticket's change-impact proposal (CIT-P); Contract v4.2 has been applied in three commits. You write the change-evidence record (CIT-E), `docs/changes/W2-49-CIT-E.md`, and record the owner's approval in the CIT-P, in one commit.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-ha8z`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-49` and `w2/W2-49`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree. (Reading an old version with `git show <commit>:<path>` or `git diff` is fine.)
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it.
- **`docs/source/`:** never read it, list it, or `git show` anything under it. The named read of this round was another worker's and is done; what it read is given below.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov close`, `gov adopt`, `gov pause` or `gov rebuild --no-embeddings`. Never run `docs/plan/tools/validate_s1.py` (DEC-738).
- **The git hooks are uninstalled until W2-08.** Before your commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-ha8z.md` (read-only).
- The acceptance tests and README, `tests/acceptance/W2-49/` (read-only): `test_w2_49_cit_e.py` and the two W2-52 tests in `test_w2_49_owner_answers.py` check your work.
- The approved proposal `docs/changes/W2-49-CIT-P.md` (in full).
- What was applied: `git log --format='%H%n%B' 1b43c73c..HEAD` and `git diff 1b43c73c HEAD -- docs/contract/` (the Contract files, and the records under `docs/contract/capabilities/`). The commits are `90c4d20a` (Contract v4.2), `5a6a12f5` (the version line in 273 records), `7f935156` (the CIT-P §8 records).
- For the form: `docs/changes/S2-CIT-E.md` and the frontmatter of `docs/changes/S2-CIT-P.md` (an earlier approved pair: the CIT-P's `status: ACCEPTED` with an `accepted:` line, the CIT-E's `status: APPLIED`).
- In `docs/DECISION_REGISTER.md`: DEC-722, DEC-090, DEC-105, DEC-614, CAP-33 in `docs/contract/contract.yaml`. Cite a decision for a rule only after reading that it says it.

## The owner's decision (DEC-741, 2026-10-17; staged for the owner's commit, not yet in this worktree's register)

The CIT-P is approved, apply now, with the CIT-P's recommended answer to each question:
- **A (a1)** the split form, new ids CAP-43.d, CAP-44.k, CAP-44.l; **B (i)** lite CAP-43.b is the manifest and file hashes only; **C (i)** a named read of Adoption Protocol v3.0 §20 and Distribution Protocol v1.2 §18, with (ii) as fallback; **D (ii)** CAP-45.a's Wave 2 wording; **E (i)** DEC-741 amends DEC-090 in part (A7, A10 and the verdict come into Wave 2, lite; A9, A11 and the rest stay in Wave 3); **F (i)** only the owner accepts an exception, by name, in a `Role: owner` entry; the auditor accepts nothing; **G (i)** the lite healthy conditions add `gov doctor` green, `gov check` with no RED, a first `gov close` at exit 0; **H (i)** the new ticket that builds the lite A7 and A10 stage records is **W2-52 (DAEO-siiz)**, FULL, engineer, layer 3; it starts after this apply round and closes before W2-27 — named wherever the CIT-P said "a new ticket" or "the ticket of Question H"; **I (ii)** W2-02 types the verdict with its three values and a list of named conditions (source item, state: met, not met, accepted by an owner entry) and closes on its own; **J (i)** at W2-30's close the orchestrator records row W2-I017 as carried to Wave 3.
- **K:** (1) the owner's answer: the version line in all 273 capability records (commit `5a6a12f5`). (2) The orchestrator's reading, staged for the owner's commit to confirm or overturn: the records CIT-P §8 names as rewritten (CAP-43.b, CAP-44.f, CAP-44.h, new CAP-43.d, CAP-44.k, CAP-44.l, and CAP-43's and CAP-44's "Covers:" lists), in a commit of its own (`7f935156`) so a revert drops it alone.
- **Row W2-L343:** both Contract files now state status ACCEPTED for v4.2 (the CIT-P stated none; ACCEPTED by the owner's approval, DEC-741).
- **Not decided:** the eight rows of `docs/contract/SOURCE_MAP.csv` that state W3 for the moved parts (CIT-P §8): left as they are. **The validator lines (DEC-744):** KPI success line 3 and the failure line need the Wave 2 plan validator, ticket W2-51 (DAEO-egsy); this ticket closes after W2-51; no test yet. `docs/plan/tools/validate_s1.py` was not run (DEC-738).

## Facts of the apply round the commits do not show (the lead's statement)

- **The named read (C (i)) was made**, once each, by `git show bb6ec3a8d8242fda7a76f86f0f0eff46813bc65f:docs/source/<path>`, the files named exactly from `docs/SOURCES.md` lines 149 and 150, after printing only their heading lines:
  - `docs/source/originals/GOVERNANCE_OS_ADOPTION_MIGRATION_AND_INDEPENDENT_AUDIT_PROTOCOL_v3.0.md`, heading "# 20. Final adoption verdict", lines 591–613: the source of the ten ADOPTED_HEALTHY conditions.
  - `docs/source/originals/GOVERNANCE_OS_RELEASE_DISTRIBUTION_ADOPTION_AND_UPSTREAM_LEARNING_PROTOCOL_v1.2.md`, heading "# 18. Adoption acceptance", lines 625–644: 15 adoption acceptance conditions, used only to check the mapping.
- **Departures from CIT-P §6's text**, each to be listed in the CIT-E with its reason:
  - (a) CAP-44.h keeps §6.1's full list of lite conditions (A0–A6 and A8 with their stage records and the A5 review, the native layout, the lite A7 and A10 gates, the pinned, hash-verified release, and G's three), and adds the ten of §20 numbered (1)–(10): only (3) is marked W2; the other nine are W3, five of them with a named lite part the lite conditions check. "Every lite condition" in the F rule means that full list.
  - (b) Condition (3) is worded "path mapping, with the A5 independent review passed" rather than the source's "path mapping accepted", because the word "accepted" there would read as an accepted exception in a text whose rule is that only the owner accepts an exception (the acceptance test of F reads it so).
  - (c) CAP-45.a's original "(signed tag)" now reads "(the signed tag in W3, CAP-02.c)", and a Wave 2 clause follows; DEC-722 is added to CAP-45.a's source field, not to CAP-45's `sources` (§6.1 names neither).
  - (d) New ids sit after the last existing item of their capability (CAP-43.d after CAP-43.c; CAP-44.k and CAP-44.l after CAP-44.j).
  - (e) The 4.2 change-log entry and change row add the named read (C), CAP-45.a (D), the status (W2-L343) and the owner's approval (DEC-741) to §6.1's text.
  - (f) CAP-45.a's capability record (`docs/contract/capabilities/CAP-45.a.md`) cites version 4.2 but keeps its 4.1 item text: it is DERIVED and now stale against `contract.yaml`, and is in neither K (1) nor the K (2) reading. It is an open point for the owner.
- `docs/contract/SOURCE_MAP.csv` was not touched. The throwaway scripts were not committed.

## Ticket mode: what you write

Only `docs/changes/W2-49-CIT-E.md` (new) and `docs/changes/W2-49-CIT-P.md` (two changes below). Never the acceptance tests (MR-3): a test you think is wrong is returned as a package. Every statement comes from the commits, the files, the CIT-P, the decision above or a named source; add no rule of your own.

1. **The CIT-E** (`state_class: EVIDENCE`, in the S2-CIT-E form): what changed, **commit by commit** (`90c4d20a`, `5a6a12f5`, `7f935156`, and your own as "this commit"), matching the CIT-P section by section, or listing each difference. It names: its proposal (W2-49-CIT-P) and source (DEC-722); the owner's approval before the change (CAP-33's route; DEC-741, 2026-10-17, staged); each answer A–K and how it was applied; every covers item v4.2 changed or added against the base (check against `git diff 1b43c73c HEAD -- docs/contract/contract.yaml`: CAP-43.b, CAP-43.d, CAP-44.f, CAP-44.h, CAP-44.k, CAP-44.l, CAP-45.a, and the wave notes of CAP-43, CAP-44, CAP-47); the named read's outcome (C (i): the files, headings and line ranges above) and each of the ten with its mark; K (1) and K (2) (the reading, its own commit, for the owner to confirm or overturn); W2-L343; **W2-52 (DAEO-siiz) as the ticket that builds the lite A7 and A10 stage records (CAP-44.f, lite)**; the departures (a)–(f); what stays open (the eight source-map rows, CAP-45.a's record, the validator lines pending W2-51, W2-I017 carried at W2-30's close under J (i), DEC-741 not yet in this worktree's register); the counts (covers 211 → 214: W1 149 / W2 20 / W3 38 / NONE 7); and how it is reversed (CIT-P §9, with `7f935156` revertable alone).
2. **The CIT-P** (approved text, kept as reviewed): change its frontmatter `status:` to `ACCEPTED` and add an `accepted:` line in the S2-CIT-P form (the owner, 2026-10-17, DEC-741, staged for the owner's commit), and change the `pending:` line accordingly; and add one closing section, "13. The owner's answers (DEC-741)", that records each answer A–K in one line, and names **W2-52 (DAEO-siiz)** as the new ticket of Question H, which §2, §5.5, §7 H, §9 and §10 F-1 call "a new ticket" or "the ticket of Question H". Change nothing else in its body: the reviewed text stays as approved. W2-52 appears in the CIT-P only in that section.

## Tests

Run, in the foreground, to the end, never with `-x`:
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src python3 -m pytest tests/acceptance/W2-49 -q -p no:cacheprovider -rs`
Expected after your commit: every test passes (129).

## Commit

One commit, trailers in the final block (DEC-182, DEC-476); the body names DEC-741:

    git commit -m "W2-49 (DAEO-ha8z): the CIT-E for Contract v4.2, and the CIT-P records the owner's approval (DEC-741)" -m "<body>" --trailer "Task: DAEO-ha8z" --trailer "Role: product-spec" --trailer "Implements: DEC-722, CAP-33" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After it: `git log --oneline -2`, `git status --short` and `git log -1 --format='%(trailers)'`, quoted.

## Return

Your commit with its trailers; the files written; the suite's counts; each difference the CIT-E lists; what no source settled; anything refused, as a package.

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
