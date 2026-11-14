Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-104/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-104 (DAEO-drhj), independent auditor: run 3's narrow check (the merge resolution and the two literals only)

**Role:** independent-auditor, a fresh read-only session. Write nothing in any tree; your verdict goes in your return.
**Worktree:** `/home/usain/gov-os-worktrees/W2-104`, branch `w2/W2-104`. **Probe:** head `23a30c332f80`.
**Ticket:** `DAEO-drhj` (W2-104), profile STANDARD, class C2: `gov skilleval`, the skill evaluation harness. Its text
is `/home/usain/gov-os-worktrees/W2-104/.tickets/DAEO-drhj.md`; its sources DEC-959 and DEC-820 (read each by id in
`/home/usain/gov-os-worktrees/W2-104/docs/DECISION_REGISTER.md`, grep only by id). DEC-1020 (a) decided that `skilleval`
is recorded in `RECORDED_GOV_COMMANDS`; DEC-747 is the rule that a new `gov` command is recorded there.

## Why this check
Run 2 returned DONE at `909d7ff0a926` (`gov accept` 43/43). Its landing was refused on two test literals that a secret
scanner (gitleaks `generic-api-key`) read as keys. Since then `w2/integrate` moved by about 2,700 commits; run 3 merged it
(head `8801ffd17df9`) and the harness itself did not change. Only what run 3 did is under review:

1. **The merge.** `349341ab8` is the merge commit, saved as work in progress WITH conflict markers in five files (by
   design: the launcher needs a clean tree); the resolutions follow in their own commits:
   - `8f7b55c4b` (engineer): `src/gov/check/commands.py`;
   - `22bba1be4` (test designer): `tests/acceptance/W1-07/README.md`, `test_w1_07_recorded_commands.py`,
     `w1_07_support.py`, `tests/acceptance/W1-32/test_w1_32_command_set.py`;
   - `23a30c332` (lead): the merge of the tests branch.
2. **The literals**, each built from parts with the same value:
   - `6f79e5ae9` (engineer): `SECRET` in `tests/unit/skilleval/test_w2_104_skilleval.py`;
   - `894bd4934` (test designer): `REPLY_TOKEN` in `tests/acceptance/W2-104/w2_104_support.py`.

## Check
1. **commands.py:** `git diff 8801ffd17df9 23a30c332f80 -- src/gov/check/commands.py` adds exactly one line recording
   `skilleval`; integrate's entries (`resources`, `brief`, `links`, `plan`, `session-watch`, `wait`) and everything else
   are kept unchanged. The module imports, and `python3 -m gov.check.commands` (this tree's `src/`) exits 0.
2. **W1-07 and W1-32:** against integrate's side (`git diff 8801ffd17df9 23a30c332f80 -- tests/acceptance/W1-07
   tests/acceptance/W1-32`), only `skilleval` is added: integrate's revised lists, comments, `RECORDED_HERE` subtraction
   and the cases' points are intact; no assertion is removed or weakened; the pinned sets are integrate's plus
   `skilleval` (W1-07: ten with `lock`; W1-32: nine `gov` commands); the README's counts say the same. Compare with
   run 2's side (`git show 349341ab8^1:<path>`) that `skilleval` is added as run 2 had it.
3. **No conflict marker** anywhere in the tree at the head (`git grep -n '^<<<<<<< \|^>>>>>>> '` at `23a30c332f80`),
   and no file other than these five resolved by run 3 differs from what git's merge made (the merge's other paths
   are integrate's: `git diff 8801ffd17df9 23a30c332f80 --stat` lists only this ticket's paths and the five files).
4. **The literals:** each is built from parts and evaluates to the old value (`"PLANTED-SECRET-5b9e"`,
   `"STUBREPLYW2104"`), it is used the same way as before, nothing else in either file changed (`git show` each
   commit), and `gitleaks dir --no-banner --redact <file>` on each of the two files finds nothing (print only the count;
   never a match).
5. **Trailers:** each run-3 commit carries `Task: DAEO-drhj`, a `Role:` matching its author, and `Implements:` naming
   only DEC-959 and DEC-820; the two literal commits and the test-list commit carry a `Rewrite-Reason:`.
6. **Tests (optional; the lead runs them):** if you run any, use a `--no-hardlinks` clone of the tree at `23a30c332f80`
   in your own TMPDIR, through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
   with `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, and
   `-m "not local_only" -k "not real and not green_here and not time_limit"`; remove the clone at the end (`chmod -R u+w`
   first).

Out of scope: the harness's own behaviour (reviewed in runs 1 and 2) and anything integrate brought.

KPI id for the verdict block: `w2-104-run3-narrow`.

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

Every finding also carries `scope: in` only if it concerns run 3's merge resolution or literals.

## Write and return
- You write nothing in any tree (your own TMPDIR only). Single simple Bash commands. No shell variable or `$(…)` as a
  write target, no here-document, no `bash -c`. Every wait by pid only.
- Reads (DEC-820): open, except secrets and keys (never read or printed), the held-out qualification material's
  contents, and the hidden half of any evaluation set: never open anything under `~/gov-os-eval/`, an evaluation set's
  root, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder. You search with the Read and Grep tools, naming
  the folder a search starts at; search once more in other words if the first does not answer, then say "not found".
- Refused twice for the same call: stop and say so; never work around a refusal by another tool or form.
- Commit hashes as 12 digits, never the full 40. There is no token cap.
- **Your record is your session's final message**, in full: the twelve labelled fields first (task, status,
  work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
  recommended_next_action), your session id and the probed commit in `evidence`; your answers to checks 1 to 5 (and 6
  if run); every finding with its two lines and scope; then `REVIEW_MD_BEGIN`, the review record in markdown,
  `REVIEW_MD_END`; at the end the fenced `verdict` block
  `{"kpis": [{"kpi": "w2-104-run3-narrow", "verdict": "pass|fail", "findings": [...]}]}`, each finding
  `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 20 minutes.
