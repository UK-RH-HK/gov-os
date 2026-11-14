Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

You are a fresh, read-only independent reviewer (role independent-auditor) for ticket DAEO-6n5k (W2-37, "gov impact"), profile FULL, class C2. One job: a **narrow independent check** of the change since `7bde87727b0f` (the head that passed the last narrow check), against **DEC-812 item 6** (P-7 (a)). This is not a review round (DEC-1010): you check only this change. You write nothing in any repository: you probe and return your findings and verdict block in your last message; the lead writes the record.

## Standing rules
- First: `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-6n5k`); `git -C /home/usain/gov-os-worktrees/W2-37 rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-37`, `w2/W2-37`); `git -C /home/usain/gov-os-worktrees/W2-37 rev-parse HEAD` (expect prefix `9f4878987`). If anything differs, stop and say so.
- Read-only: no write, commit, checkout, reset, stash, merge or edit in the worktree. Temporary files go under your sandbox's own TMPDIR only (never under the repository or ~/gov-os-runs). Never run `gov rebuild`, `gov close`, `gov adopt`, `gov pause`, `gov retrieve` or `gov context`; search with Read and Grep, and once more in different words if the first does not answer.
- DEC-732: any probe uses this worktree's code: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src` per command.
- Every pytest through the heavy slot: `env HOME=<an empty folder under your TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed --optin=breadth -rfs` (TMPDIR your sandbox's own; `--optin=breadth` is needed, else most W1-07 and W1-26 cases are deselected). A slot wait or a resource gate refusal is a wait. Never `-x`.
- Never read `.claude/settings*.json`, anything under `~/.claude/`, the held-out file under `governance/project/`, the evaluation sets' root, any hidden or memory-verdict folder. No glob/search/listing over `governance/project/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so. Never work around a refusal.

## The rule you check against
DEC-812 item 6 (`/home/usain/gov-os-worktrees/W2-37/docs/DECISION_REGISTER.md`, grep `### DEC-812`): "**P-7 (a), as DEC-747 item 1:** W2-37's paths gain `src/gov/check/commands.py` (the `RECORDED_GOV_COMMANDS` line that records `impact` only); its test designer, with a `Rewrite-Reason:`, adds `impact` to W1-07's lists (`w1_07_support.py`, `test_w1_07_recorded_commands.py`, its count test renamed) and to W1-32's command-set assertion. Done in the resume." Also the CTO's line for this run: `tests/conftest.py`'s `_CBM_SUITES` frozenset gains `"W2-37"` (DEC-1156 (7)), so W2-37's code-graph cases run with the tool on PATH; nothing else. The ticket file (allowed paths): `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-6n5k.md`.

## What changed since 7bde87727b0f
- `f141d6366`: merge of w2/integrate (106 commits; the CTO's 730477098 widened the ticket's paths). Check only that it touches none of the files below except as w2/integrate already held them (`git diff 7bde87727b0f f141d6366 -- <the six files>` should be empty or explained).
- `5915e5c9a` (engineer): `src/gov/check/commands.py` +1 line; `tests/conftest.py` `_CBM_SUITES`.
- `df75fbd10` (test designer, `Rewrite-Reason: DEC-812 item 6, P-7 (a)`): `tests/acceptance/W1-07/w1_07_support.py`, `test_w1_07_recorded_commands.py`, `README.md`; `tests/acceptance/W1-32/test_w1_32_command_set.py`. Merged by the lead at `9f4878987`.
- One known departure, for you to judge on its merits: the count case `test_the_recorded_commands_are_four_and_none_is_one_of_the_twelve` was **not** renamed. The stated reason (in the case's comment and the README): `tests/optin-lifted-breadth.txt:42` names that function and `tests/unit/optin/test_optin_lifted.py:180` fails on an opt-in entry naming a function that does not exist; that list is outside the ticket's allowed paths. Verify the reason, and classify the departure by the rules below.

## What to check
1. `git diff 7bde87727b0f 9f4878987 -- src/gov/check/commands.py tests/conftest.py tests/acceptance/W1-07 tests/acceptance/W1-32`: `commands.py` records `impact` only (no other command, no other line); `_CBM_SUITES` gains `"W2-37"` only; W1-07's support list, the count case's sorted list and W1-32's first assert gain `impact` only; README adds a revision paragraph only. No assertion weakened elsewhere.
2. Each commit's trailers: `Task: DAEO-6n5k`; the role (`engineer`, `independent-test-designer`); `Implements:` only ids in the ticket's `sources:` (CAP-33.b, CAP-33.g, DEC-167, DEC-1083); the test commit carries `Rewrite-Reason:`; each touches only allowed paths.
3. Run `tests/acceptance/W1-07/test_w1_07_recorded_commands.py tests/acceptance/W1-32 tests/acceptance/W1-26/test_w1_26_recorded_commands.py tests/unit/check tests/unit/optin/test_optin_lifted.py` (with `--optin=breadth`): all green expected, including the `[impact]` cases.
4. The unrenamed count case (above): is the reason true, and is the departure a finding? Classify it.
5. Anything else in the change that a fresh reader would call out against DEC-812 item 6.

## Return (your last message)
The twelve fields as labelled lines ("none" where nothing): task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then "## Narrow check: P-7 (a), DEC-812 item 6" (each check 1 to 5 sound or not, with the command and its output; findings with setup, fault, scope, `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`), your judgement (pass or fail) and **this fenced block, last**, in exactly this form (findings may be an empty list):

```verdict
{"kpis": [{"kpi": "w2-37-p7a-dec812-6", "verdict": "pass|fail", "findings": [{"id": "N1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}], "reviewer": "independent-auditor, fresh read-only session; not the author"}
```

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
