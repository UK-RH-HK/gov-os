# Brief chk-1: narrow independent check for DAEO-0cd2 (W2-187), after review round 1, FULL, class C2

You are a fresh, read-only independent auditor. Review round 1 of W2-187 passed at `5b82d1d53868`
(`docs/probes/DAEO-0cd2/PR-DAEO-0cd2.md`). The CTO then decided a fix batch in this ticket: F-A, with F-B and R1 riding
along. You check that change only. This is a narrow check (DEC-1154), not a design review and not a third round. You
write nothing in the repository: your findings and the verdict block are your return, and your lead writes the record.

## What to check
| what | path / value |
|---|---|
| the tree (read only) | /home/usain/gov-os-worktrees/W2-187 |
| head | w2/W2-187 at 89d291eac (quote the full sha from `git rev-parse HEAD`) |
| reviewed head (round 1) | 5b82d1d53868625c43a5b8b2bb58492bad3f8038 |
| the change | `git diff 5b82d1d53..HEAD -- src tests governance/project/orchestration/tools/memaudit_cron.sh docs/changes/W2-187-evidence.md docs/probes/DAEO-0cd2`: the engineer's `597a82f93` and `d3d70b584`, the test designer's `fc634374b` (merged at `89d291eac`), the lead's `46d131ab9` (the round-1 probe record, and two interim PACKAGE files removed from `docs/probes/`) |
| the ticket (S3, S6/I6, S7, S11, S12, F7, I13 and its note) | /home/usain/gov-os-worktrees/W2-187/.tickets/DAEO-0cd2.md |
| round 1's findings (F-A, F-B, R1, R6) | docs/probes/DAEO-0cd2/PR-DAEO-0cd2.md |

## The decided fix (the CTO, 2026-11-14, after review round 1 passed; DEC-1157 (12), DEC-1180 (4), DEC-1156 (7))
Review round 1 (`docs/probes/DAEO-0cd2/PR-DAEO-0cd2.md`, read its findings F-A, F-B and row R1) passed. The CTO decided
to fix F-A in this ticket, with F-B and R1 riding along. These three, as described behaviour (DEC-136):

1. **F-A, the searched store is the declared store (S3, S6/I6, S7).**
   - Now: the `standing run` driver hands its `preflight`, `measure` and `judge` children the repository as their root
     (`src/gov/memaudit/driver.py:177,184,186`; the fresh `run` does the same). `gov retrieve` therefore answers from the
     repository's own `.gov-runtime/store.db` while the declaration names and checks the store link's store.
   - Then: when the repository's own store sits at another commit than the link's, every attempt faults on the
     store-commit check and the week ends `STOPPED fault`.
   - Wanted: on both the standing and the fresh path, the `preflight`, `measure` and `judge` children work in the store
     link's work tree at the audit commit (I6 already says the pre-flight's root is the link's work tree). So the commit
     of the store every search reaches equals the link's, and S7 compares the same store.
   - The acceptance cases' planted `gov` (`tests/acceptance/W2-187/fake_gov_x.py:102-103`) answers the plan's store
     commit whatever folder it runs in, so it cannot show which store a search reached. The new case needs a planted
     `gov` that answers the commit of the store in the folder it is run from (its cwd, or its `--root`).
2. **F-B, push only the scanned commit (S12, F7).**
   - Now: `push.py` scans the repository, then pushes the branch name, which git reads again after the scan. A commit
     landing on the branch during the scan is pushed unscanned.
   - Wanted: the commit the branch names when the scan starts is recorded. `git push <remote>
     <that sha>:refs/heads/<branch>` pushes it, so the remote's branch is the scanned commit. The line stays
     `PUSH pushed <remote> <branch> <12 hex of the scanned commit>`.
3. **R1, gitleaks on step 6's cron line (S11, S12).**
   - Now: cron's `PATH` does not hold `~/.local/bin`, so a declared push is blocked every week as
     `scan failed missing`.
   - Wanted: A9's ACT.md step 6 line (`memory_sets.walls_act`) carries
     `GOV_MEMAUDIT_GITLEAKS=<gitleaks>` before the wrapper. `<gitleaks>` is the absolute path `shutil.which("gitleaks")`
     gives when A9 runs, else the literal `<path to gitleaks>`. The rest of the line and I13's step-6 sentence stay.

**Path cases:** if any of this needs a file outside your allowed paths (for instance a W2-172 *test* file that pins the
repository as the children's root, as opposed to `w2_172_world.py`, `w2_172_git.py` or `test_w2_172_s7_digest.py`),
stop and return PACKAGES naming the path and the line. Never widen the paths yourself.

## Check
- Each of F-A, F-B and R1 is met as described.
  - F-A: the store every standing and fresh search reaches equals the link's, the anchors are read at the audit commit,
    and S7 compares the same store.
  - F-B: the remote gets only the scanned commit.
  - R1: step 6's line names the scanner.
- Nothing else in behaviour moved:
  - the one judged path (`prompts.py`, the reader, grader and matcher unchanged);
  - counts only (no id, question, gold, answer, citation, path or secret in any line, log or digest);
  - the week rule;
  - `maintain` not a gate;
  - the push fails closed;
  - the no-declaration push writes nothing.
- The acceptance cases cannot pass for the wrong reason: the planted `gov` now answers the store of the folder it runs
  in.
- The engineer's note: the fresh path's `pool` child still gets the repository as `--repo` (a retrieval-only
  diagnostic re-measure). Judge whether that touches S7's comparison or any KPI line.
- Scope: every file the fix commits change is inside `allowed_paths`; only the test designer touched
  `tests/acceptance/`.
- Do not re-run whole suites (the lead's results are at the end); small probes are yours.

**Held-out rules (DEC-820):**
- Never open the evaluation sets' root, the real runs folder or any folder under its `indep/`, any hidden half or
  memory-verdict folder, or the real crontab.
- Never a real model call, a real search, a real push to a real remote, or a real gitleaks over a real repository.
- Plant everything in your sandbox's temporary folder. Any pytest goes through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=<an empty folder in your temporary folder> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187/src python3 -m pytest <one file or case> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  with a Bash timeout of 3600000 ms; a heavy-slot refusal is a wait.
- Search with Read, Grep and Glob (DEC-1065); no `gov retrieve`, no `gov context`.

## Judgement rules (governance/project/briefs/JUDGEMENT.md, carried word for word)

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

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status / work_completed / files_changed (none) /
evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then:
- what you probed and found sound, each with its probe;
- each finding as a described behaviour with file and line, `Ordinary work: yes|no, because …`,
  `Consequence: fails open|loses work|other`, and scope in or out;
- the verdict, `pass` or `fail`;
- **the fenced `verdict` block LAST**, one entry per KPI line it touches (at least success-3, success-6, success-7,
  success-11, success-12, failure-7):
  ```verdict
  {"kpis": [{"kpi": "success-3", "verdict": "pass", "findings": []}, ...]}
  ```
Then `guard_refusals:`. Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never
reach the same effect by another form (DEC-1142 (9)).

## The lead's results at 89d291eac
- `gov accept W2-187`: pass, 210 passed, 0 failed, every line success-1 to success-12 and failure-1 to failure-7 pass.
- `tests/acceptance/W2-187` 210 passed; `W2-172` 162 passed; `W2-171` 140 passed (the engineer also ran W2-170 184, W2-173 91, W2-88 215, unit memaudit 363: all green).
