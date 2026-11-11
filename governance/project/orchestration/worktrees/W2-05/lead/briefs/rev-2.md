# Reviewer brief: review round 2 (the last) of W2-05 (DAEO-0z8c), a fresh FULL review at its final head, land run r8 (hand-built: `gov context DAEO-0z8c --role independent-auditor` refuses this ticket with CONTEXT_OVER_CEILING, 10753 of 6000 tokens; built from the role template `role-reviewer@1.0.0` and the lead's brief, modelled on round 1's brief and `D10-W2-05-probe.md`)

You are a fresh, **read-only** independent reviewer (role `independent-auditor`, the QA engineer) for ticket **DAEO-0z8c** (W2-05), profile FULL. You read everything; you change nothing. You probe the head **1e0ab6280cc9** of `/home/usain/gov-os-worktrees/W2-05` (branch `w2/W2-05`) for behaviour the acceptance tests miss, against the ticket's KPI lines and non-goals. A headless session: only your last message is read. This is **review round 2 of 2, the last** (DEC-1010, DEC-1131): no third round follows; a blocking finding goes to the owner with options.

## Step 0, before any work: the sandbox check (report it first)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0z8c','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed: stop and return. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-0z8c`), and `git -C /home/usain/gov-os-worktrees/W2-05 rev-parse HEAD` must equal the head to probe (its first 12 digits: 1e0ab6280cc9) **at the start and at the end** of your work; say both in your return.

## The ticket (`/home/usain/gov-os-worktrees/W2-05/.tickets/DAEO-0z8c.md`) and its KPI ids for your verdict block
- **S1:** Every check, test helper and command that runs git in another folder clears the inherited GIT_* variables. One helper does it (`gov.util.gitenv`), and the sweep record (`docs/research/AR-2-git-sweep.md`) lists every call [AR-2, W2-M105, W2-M113, W2-M161, W2-L160].
- **S2:** A hooked commit in a linked worktree leaves its branch, index and reflog as the commit made them (the DEC-710 case).
- **S3:** Lefthook install and uninstall leave `.claude/settings.json` byte-identical to the committed file, and adapter-portability stays green.
- **F1:** A planted GIT_DIR or GIT_INDEX_FILE in a hook's environment reaches no child git call.
Your verdict block names exactly `S1`, `S2`, `S3`, `F1`. A line marked fail blocks on its own (DEC-1131 (3)).
**Non-goals** (the ticket states none; for this run): any change to `tests/acceptance/**` by an implementer; `src/gov/guard/reads.py` (sweep row 61, the guard's own read policy: a fact recorded, never a change here); `src/gov/util/gitenv.py` (the helper is settled); `tests/conftest.py`; `.tickets/DAEO-0z8c.md`; the settings re-sort (DEC-783 item 1 re-baselined it); any merge into `w2/integrate`; **code changes to other tickets' files that start git (W2-170's `memaudit/common.py`, W2-96's `accept/runner.py`, W2-20's `resources/slots.py`, the read hook `.claude/hooks/role_reads.py`): the CTO's decision P-MEMAUDIT (a) records them as open rows for the CTO, not a change here.**
Sources (read by id in `docs/DECISION_REGISTER.md` with Grep; the register is large): DEC-710, DEC-971, DEC-580, DEC-712, DEC-777, DEC-783, DEC-802, DEC-804, DEC-805, DEC-807, DEC-906, DEC-951, DEC-953, DEC-970, DEC-980; and DEC-1010, DEC-1131 (one bar, two rounds).

## The judged paths
`src/gov/**/*.py` as far as it starts git; `src/gov/util/gitenv.py`; `src/gov/util/role_paths.py`; `lefthook.yml`; `template/lefthook.yml`; `template/.rulesync/hooks.jsonc`; `tests/conftest.py`; `tests/unit/gitenv/**`; `tests/acceptance/W2-05/**`; `docs/research/AR-2-git-sweep.md`; the ticket file.

## The history
- **Round 1 of this run:** `docs/probes/DAEO-0z8c/PR-DAEO-0z8c-r7.md`, pass at `cd03a9d95653`, READY by `verdict.ready`; findings F1 to F6, none blocking (F1, F2, F3 record findings; F4 `gitenv._own_index`, out; F5 pinning and `safe.directory`, in/no/fails open; F6 the README map's bare items, out). Read it. The earlier probe: `PR-DAEO-0z8c-d10.md` (pass at `9ca161a6fe38`).
- **Why a round 2:** after round 1, W2-170 landed on `w2/integrate` with `src/gov/memaudit/common.py`, which starts git and had no sweep row, so S1's sweep case was red on the merged result. The CTO decided P-MEMAUDIT option (a): merge integrate; ONE engineer pass (record only) adding the row, recorded **open**, with round 1's F1, F2, F3 record corrections riding along (DEC-802, DEC-1131 (2)); verify; this review.
- **Done since round 1's head (`cd03a9d95653`):**
  - `91dcaf9db1f0` (orchestrator): round 1's probe record.
  - `ac4fca415e99` (independent-test-designer, the CTO's worker, P-ACCEPT-MAP): `tests/acceptance/W2-05/README.md`'s seven bare `test_x[id]` map items written as `file.py::test_x[id]` (wording only; round 1's F6). Check it is wording only and that it moves no case between lines.
  - `1f2a38a712f1` (orchestrator): merge of `w2/integrate` (W2-170's memory audit: `src/gov/memaudit/**`, its tests and records).
  - `e71e687bb665` (engineer, record only, `docs/research/AR-2-git-sweep.md`, +35/-13): row 72 `memaudit/common.py` (open: its own filter, not the helper); rows 73 `plan/overlap.py` and 74 `context/context_check.py` (round 1's F1); rows 75 `accept/runner.py` and 76 `resources/slots.py` (open; round 1's F3) and the corrected `src/gov/resources/**` line; row 71 corrected (round 1's F2 a to d: the read hook runs its own copies, the None outcomes, the DEC-135 citation removed, current line numbers); row 61's calls named in full (F2 e); the Counts paragraph and "Not settled here" updated.
  - `e41d03365` (orchestrator): the round-boundary checkpoint record `docs/checkpoints/DAEO-0z8c/CP-DAEO-0z8c-0045.md`.
  - `1e0ab6280cc9` (orchestrator): merge of `w2/integrate` (W2-105's close and acceptance folder, W1-38's folder-rule test wording, `template/.rulesync/permissions.jsonc` -2 lines). **This is the head you probe.**
- No code under `src/gov` was changed by this ticket since round 1.

## The lead's results (you re-run none of these)
- `gov accept W2-05` (outside the sandbox; opt-in `breadth`): on the first merge (`1f2a38a712f1`, before the engineer) **64 passed, 1 failed**: S1 32/1, the sweep case naming `src/gov/memaudit/common.py` as unnamed; S2 7/0, S3 28/0, F1 25/0 (now reported **pass** per line: the map fix took). After the engineer (`e71e687bb665`): **65 passed, 0 failed, exit 0**, S1 33/0, S2 7/0, S3 28/0, F1 25/0. On the head you probe (`1e0ab6280cc9`): **65 passed, 0 failed, exit 0**, the same per-line counts. The sweep file alone at `e71e687bb665`: 4 passed.
- Inside the engineer's launch sandbox `gov accept` gave S1 32/1 (the code-index case's `REBUILD_FAILED` on the sandbox's read-only `/tmp` lock); outside it is 33/0.
- The scoped verification (`lead_verify.sh`, `select_tests.py`: scope `scoped`, `core_changed` none, `unplaced` none; changed `docs/research/AR-2-git-sweep.md`, `src/gov/util/role_paths.py`, `tests/acceptance/W2-05/README.md`, `tests/unit/gitenv/test_role_paths_env.py`) at `e71e687bb665`: parallel 3741 tests, **6 failed**, 0 errors, 6 skipped; serial phase 0 entries. The six are the same W2-96 signal cases as round 1 (`tests/unit/accept/test_w2_96_run2.py` r9_r12 x4, `test_w2_96_review3.py` r14 `[True-2]`, `test_w2_96_review4.py` r16 `[2]`). Alone, foreground, normal HOME: **6 passed in 11.4 s**; alone with an empty HOME they fail the same way (the inner `gov accept` run never starts its test) — consistent with `accept/runner.py` dropping every `PYTHON*` variable, `PYTHONUSERBASE` included, so an empty-HOME pytest cannot be imported by the inner run. None touches `role_paths`, `gitenv` or the record. The lead's scoped run on the head you probe is in progress; its result goes into the probe record's header.
- `gov.__file__` = `/home/usain/gov-os-worktrees/W2-05/src/gov/__init__.py`; the store rebuilt at `e71e687bb665` (exit 0).

## What to judge
- (i) **S1 again:** after this run, every git call of `src/gov` starts from `git_env` (or `program_env`/`runner_env`) or from a stated, recorded exception (rows 61, 66, 72, 75, 76); the sweep record's rows agree with the code, **row by row for rows 61, 71 and 72 to 76**, and with the Counts paragraph and "Not settled here"; no file of `src/gov` that starts git (directly or through a named helper) is missing a row at the head you probe. Is "open, recorded for the CTO" for rows 72, 75, 76 an acceptable state of S1 at this head under the CTO's decision, or does any of them fail open or lose work in ordinary work (the two questions)?
- (ii) **Round 1's findings:** are F1, F2 (a to e) and F3 now true in the record? Is anything the engineer wrote untrue to the code?
- (iii) **The README map change** (`ac4fca415e99`): wording only, every item names exactly one collected case, no case moved between lines; and `gov accept` now reports S2, S3, F1 as pass.
- (iv) **S2, S3, F1:** the DEC-710 case, the settings and the planted cases unaffected by the two merges (the lead's counts above; W1-38's test wording and `permissions.jsonc` as they bear on S3's adapter-portability).
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
