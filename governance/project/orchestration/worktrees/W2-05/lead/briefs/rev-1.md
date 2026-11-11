# Reviewer brief: a fresh FULL review of W2-05 (DAEO-0z8c) at its final head, run r7 (hand-built: `gov context DAEO-0z8c --role independent-auditor` refused with CONTEXT_OVER_CEILING; built from the role template `role-reviewer@1.0.0` and the lead's brief, modelled on `D10-W2-05-probe.md`)

You are a fresh, **read-only** independent reviewer (role `independent-auditor`, the QA engineer) for ticket **DAEO-0z8c** (W2-05), profile FULL. You read everything; you change nothing. You probe the head **HEAD_TO_PROBE** of `/home/usain/gov-os-worktrees/W2-05` (branch `w2/W2-05`) for behaviour the acceptance tests miss, against the ticket's KPI lines and non-goals. A headless session: only your last message is read. This is review round 1 of this run (at most two, DEC-1010, DEC-1131).

## Step 0, before any work: the sandbox check (report it first)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0z8c','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed: stop and return. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-0z8c`), and `git -C /home/usain/gov-os-worktrees/W2-05 rev-parse HEAD` must equal the head to probe (its first 12 digits: HEAD_TO_PROBE) **at the start and at the end** of your work; say both in your return.

## The ticket (`/home/usain/gov-os-worktrees/W2-05/.tickets/DAEO-0z8c.md`) and its KPI ids for your verdict block
- **S1:** Every check, test helper and command that runs git in another folder clears the inherited GIT_* variables. One helper does it (`gov.util.gitenv`), and the sweep record (`docs/research/AR-2-git-sweep.md`) lists every call [AR-2, W2-M105, W2-M113, W2-M161, W2-L160].
- **S2:** A hooked commit in a linked worktree leaves its branch, index and reflog as the commit made them (the DEC-710 case).
- **S3:** Lefthook install and uninstall leave `.claude/settings.json` byte-identical to the committed file, and adapter-portability stays green.
- **F1:** A planted GIT_DIR or GIT_INDEX_FILE in a hook's environment reaches no child git call.
Your verdict block names exactly `S1`, `S2`, `S3`, `F1`. A line marked fail blocks on its own (DEC-1131 (3)).
**Non-goals** (the ticket states none; for this run): any change to `tests/acceptance/**`; `src/gov/guard/reads.py` (sweep row 61, the guard's own read policy: a fact recorded, never a change here); `src/gov/util/gitenv.py` (the helper is settled); `tests/conftest.py`; `.tickets/DAEO-0z8c.md`; the settings re-sort (DEC-783 item 1 re-baselined it); any merge into `w2/integrate`.
Sources (read by id in `docs/DECISION_REGISTER.md` with Grep; the register is large): DEC-710, DEC-971, DEC-580, DEC-712, DEC-777, DEC-783, DEC-802, DEC-804, DEC-805, DEC-807, DEC-906, DEC-951, DEC-953, DEC-970, DEC-980; and DEC-1010, DEC-1131 (one bar, two rounds).

## The judged paths
`src/gov/**/*.py` as far as it starts git; `src/gov/util/gitenv.py`; `src/gov/util/role_paths.py`; `lefthook.yml`; `template/lefthook.yml`; `template/.rulesync/hooks.jsonc`; `tests/conftest.py`; `tests/unit/gitenv/**`; `tests/acceptance/W2-05/**`; `docs/research/AR-2-git-sweep.md`; the ticket file.

## The history
- **Last probe:** `docs/probes/DAEO-0z8c/PR-DAEO-0z8c-d10.md`, judgement pass at `9ca161a6fe38` (findings F1 to F5, none blocking; F2 and F3 were the sweep record's five unnamed files and `role_paths.py`; F4 the ticket's `sources:`; F5 the record's silence on `tests/conftest.py`'s own git call). Read it.
- **Done since:** `f53c8543d` (research) added sweep rows 67 to 71 (`links/command.py`, `rebuild/command.py`, `rebuild/integration.py`, `util/gitrun.py`, `util/role_paths.py`). This run (r7), one engineer round: `f48697a0e6f9` (code + unit cases: `role_paths.py`'s four git calls, `main_tree`, `linked_tests`, `changed`, `engineer_side`, on one `_git` helper with `git_env(<-C folder>, pinned=True)` and `git_binary()`, `_git_env` removed; new `tests/unit/gitenv/test_role_paths_env.py`, 7 cases, 5 red on the old file) and `86a1ebf381bc` (record: row 71 scrubbed with the `ls-files` measurement, the Counts paragraph and "Not settled here" agreeing; row 61's "after W2-84 merges" replaced by the present fact, open for the CTO; one paragraph on `tests/conftest.py`'s strip). Then the lead's merges of `w2/integrate` (governance records, tickets of other ids and the register only) and the lead's checkpoint record.
- **Three `src/gov` files that changed since the last probe** (other tickets'): `src/gov/accept/runner.py`, `src/gov/adapters/portability.py`, `src/gov/check/commands.py`. Read them for git calls (S1: every git call of `src/gov` starts from `git_env` or a stated, recorded exception).
- The engineer's own discoveries, for you to judge, not to take as given: (1) `gitenv._own_index` (`gitenv.py` line 172) runs `git` by name from `PATH` when `GIT_INDEX_FILE` is inherited, so `git_env(root)` itself can start PATH's git; (2) `reads.py`'s `_git` serves more calls than row 61 names (`worktree list`, `rev-parse <rev>:<rel>`, and `ask`, which runs git with words from the judged command, in that command's cwd).

## The lead's results (you re-run none of these)
- `gov accept W2-05` (outside the sandbox, opt-in `breadth`), before the round (at `eb88077a54fa`), after it, and on the merged head: each time **65 passed, 0 failed, 0 skipped**; per line S1 pass 33/0, S2 7/0, S3 28/0, F1 25/0 — but `gov accept` reports S2, S3 and F1 as **"fail" with no failed case** (exit 3): seven README-map items in `tests/acceptance/W2-05/README.md` name parametrized cases as bare `test_x[param id]` words, and `gov.accept.runner.matches` matches a bracketed item only in the `file.py::test_x[id]` form (`WORD = \w+` fails on `[`), so each such item counts as a named test that ran no case (`_report`'s `missing`). The cases themselves run and pass. The lead reports this to the CTO as a package (the README is a test designer's path, the runner W2-96's). Judge whether it bears on your verdict for S2, S3, F1 (the KPI behaviour vs the runner's map reading), and say so.
- Inside the engineer's sandbox the same `gov accept` gave S1 32 passed and 1 failed (64/1), identical before and after its change; outside the sandbox S1 is 33/0. The lead reads it as a sandbox-only effect.
- The scoped verification (`lead_verify.sh`, `select_tests.py`'s selection, parallel then serial phase): SCOPED_RESULT.
- The engineer's unit runs: `tests/unit/gitenv/` 60 passed (8 deselected by the real/green_here/time_limit filter); `tests/unit/guard/test_role_paths.py` 16 passed; `tests/unit/util/test_w2_150_role_paths_register.py` 7 passed; `tests/unit/retrieval/test_w2_13_role_filter.py` 14 passed; `tests/acceptance/W2-150/` 32 passed (memory's import closure stays free of the gates with the new `gov.util.gitenv` import).

## What to judge
- (i) **S1 again:** after this run, every git call of `src/gov` starts from `git_env` (or `program_env`/`runner_env`) or from a stated, recorded exception (row 61, row 66); the sweep record's rows agree with the code, row by row for rows 67 to 71 and the rows the engineer touched (61, 71), and with the Counts paragraph and "Not settled here".
- (ii) **`role_paths.py`:** still gives the same answers and fails the way it did (`None` from `linked_tests`, `changed`, `engineer_side`; `main_tree`'s fall-back to the folder it was given); no fall-back to `git` on `PATH`; `gov retrieve`'s role filter and the guard's read hook (`gov.guard.role_paths` is this module object) reach it with no new latency worth a finding; a planted `GIT_DIR`/`GIT_INDEX_FILE` reaches nothing; the decision to keep `changed`'s `ls-files --others --exclude-standard` pinned (an untracked file only the person's `core.excludesFile` hides now counts as changed, i.e. withheld from the designer; a file only the default XDG ignore file hides can drop out for a person with both files) — is it the strict side, and is it recorded truly in row 71?
- (iii) **S2, S3, F1:** the DEC-710 case, the settings and the planted cases are unaffected (the lead's counts above).
- (iv) **The record's F5 line** (the paragraph on `tests/conftest.py`'s strip) is true to `tests/conftest.py`.
- Look first for lost work, a role writing outside its scope, an implementer able to change acceptance tests, a guard or gate failing open (DEC-137).

## How you work
- `gov retrieve` is not available in your sandbox: read with Read and Grep; when a search does not answer, search once more in your own, different words (two in all), then answer with path and lines or say "not found".
- DEC-849: the guard may refuse some reads (searches from the repository root, `governance/project/`, `.claude/`): take the refusal, never route round it, search named folders instead, and count the refusals.
- Re-run nothing the lead ran. Run code only to reproduce a finding, in a temporary folder of your own under the sandbox's `TMPDIR`, with `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src`, and an empty `HOME` with `PYTHONUSERBASE=/home/usain/.local` for pytest. No installs, no GPU, never the full suite. One simple command per Bash call; no here-documents, no `bash -c`, no long inline `python3 -c` with braces.
- **You write nothing in any tree.** `git -C /home/usain/gov-os-worktrees/W2-05 status --porcelain` is empty when you finish.
- The hidden-half and secrets rule (DEC-820): never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder; never read the held-out qualification material's contents; never print a secret or key.
- Row W2-L423's rule (DEC-911): in your return write commit hashes as 12 digits (your record will be committed under `docs/`, but keep 12 digits except where you quote the probed head in full once), and never write the keywords of the secrets rule that takes a bare 40-hex string for a token.
- **Refused twice for the same call: stop and say so; no third try.** On an authentication error: stop and return `AUTH_REQUIRED`.
- Estimate: 20 minutes.

## Judgement rules (governance/project/briefs/JUDGEMENT.md, word for word)

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

## Return (your record is your session's final message, in full)
Step 0's result first (the sandbox check, both `rev-parse HEAD` readings). Then the twelve fields, each a labelled line ("none" where nothing), any payload after them:

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

Then: `task: DAEO-0z8c` and `decisions:` (the ids your findings rest on; name both ids where a superseded or PROPOSED rule is in use, DEC-1073); your answers to (i) to (iv); what you probed and found sound; every finding as behaviour (what was done, what happened, what should have; never as code, DEC-136), each with `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, `scope: in|out`, the KPI id it bears on, and what evidence would reverse it (DEC-1014). At the end, the fenced block, one entry per KPI id `S1`, `S2`, `S3`, `F1`, each finding `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1):

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": []}, {"kpi": "S2", "verdict": "pass|fail", "findings": []}, {"kpi": "S3", "verdict": "pass|fail", "findings": []}, {"kpi": "F1", "verdict": "pass|fail", "findings": []}]}
```
Refused twice for the same call: stop and say so.
