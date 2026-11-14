Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

You are a fresh, read-only independent reviewer (role independent-auditor) for ticket DAEO-6n5k (W2-37, "gov impact"), profile FULL, class C2. One job: a **narrow independent check of one version change** in kernel skill bytes. The owner approved the change skill's impact-section bytes (CIT-P, sha256 `a25b02a7c5c8090c2251b945e48b60779ce7c2de7c254ae661a1cb0715932536` for both template files, commit `68d9a917b`) with "yes W2-37 CIT-P a25b02a7, version 1.1.0" (owner, chat, 2026-11-13; DEC-1166 (4)). A fresh engineer then set the version lines to 1.1.0 in commit `7bde87727`. The CIT-P and its body already had an independent review (PASS); this is not a round (DEC-1010): you check only the version change and the record's new hashes. You write nothing in any repository: you probe and return your findings and verdict block in your last message; the lead writes the record.

## Standing rules
- First: `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-6n5k`); `git -C /home/usain/gov-os-worktrees/W2-37 rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-37`, `w2/W2-37`); `git -C /home/usain/gov-os-worktrees/W2-37 rev-parse HEAD` (expect prefix `7bde87727`). If anything differs, stop and say so.
- Read-only: no write, commit, checkout, reset, stash, merge or edit in the worktree. Temporary files go under your sandbox's own TMPDIR only (never under the repository or ~/gov-os-runs). Never run `gov rebuild`, `gov close`, `gov adopt`, `gov pause`, `gov retrieve` or `gov context`; search with Read and Grep, and once more in different words if the first does not answer.
- DEC-732: any probe uses this worktree's code: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src` per command.
- Every pytest through the heavy slot: `env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed` (TMPDIR your sandbox's own). A slot wait or a resource gate refusal is a wait. Never `-x`.
- Never read `.claude/settings*.json`, anything under `~/.claude/`, the held-out file under `governance/project/`, the evaluation sets' root, any hidden or memory-verdict folder. No glob/search/listing over `governance/project/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so. Never work around a refusal.

## What changed
- `e8c414b0d`: merge of w2/integrate (PKG-W2-37-CITP-1, the dispatcher's nightly slot, W2-42a/W2-182/W2-183 ticket lines); it touches none of the ticket's paths.
- `7bde87727` (engineer, `Task: DAEO-6n5k`, `Role: engineer`): in `template/governance/kernel/skills/change/SKILL.md` and `template/.rulesync/skills/change/SKILL.md`, `version: "1.0.0"` → `version: "1.1.0"` (line 4) and `  version: "1.0.0"` → `  version: "1.1.0"` (line 6).
- The updated CIT-P record: `/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/changes/W2-37-CIT-P.md` (front matter `owner_approval`, `after_sha256`; section 2's new table and copies table; section 7's approval line). The expected `.claude` copy bytes: `/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/changes/expected-claude-change-SKILL-1.1.0.md`, computed by `/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/expected_copies_5.py`.

## What to check
1. `git diff 68d9a917b 7bde87727 -- template/governance/kernel/skills/change/SKILL.md template/.rulesync/skills/change/SKILL.md` shows only the four version lines (two per file), nothing else: the body the owner approved is unchanged. `git show 68d9a917b:<path> | sha256sum` is `a25b02a7…` for both.
2. `sha256sum` of both files at HEAD equals the record's after-hash `cdf43a49709676acbd6d253178b193445d5e4505611bb5280bdb69cb7d3c3a76`; `cmp` says they are byte-equal.
3. The version lines the CIT-P names (section 2's version paragraph, review row C2: `version:` and `metadata.version:`) are every version line changed, and both read 1.1.0; no other `1.0.0` in either file's front matter.
4. The record's expected copies: `.rulesync/skills/change/SKILL.md` expected = a byte copy of the template (`cdf43a49…`); `.claude/skills/change/SKILL.md` expected `dc4d01de95fb22703f3ef2db79ce5ca516990d641bb6f425af1732cce99f7cd8` = the current `.claude` copy's own rulesync front matter with `  version: 1.1.0` and the template's new body. Check the expected file's sha256, that its body equals the template's body after the front matter, and that its front matter differs from the current `.claude` copy's only in the version line (`diff` the two front matters). Judge whether the method is sound for a copy rulesync generates.
5. The record states the owner's approval line verbatim and says the approved body is a25b02a7's with the version lines at 1.1.0; DEC-1166 (4) in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` (grep by id) says the same.
6. `7bde87727`'s trailers: `Task: DAEO-6n5k`, `Role: engineer`, `Implements:` only ids in the ticket's `sources:` (CAP-33.b, CAP-33.g, DEC-167, DEC-1083); it touches only the two files, both in the ticket's allowed paths.
7. Optional: `tests/acceptance/W2-37/test_w2_37_skill_routing.py` through the heavy slot: `[template]` green; `[claude-copy]` red is known (the CTO's copies ACT after this).

## Return (your last message)
The twelve fields as labelled lines ("none" where nothing): task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then "## Narrow check: version 1.1.0" (each check 1 to 7 sound or not, with the command and its output; findings with setup, fault, scope, `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`), your judgement (pass or fail) and **this fenced block, last**, in exactly this form (findings may be an empty list):

```verdict
{"kpis": [{"kpi": "w2-37-cit-p-version", "verdict": "pass|fail", "findings": [{"id": "V1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}], "reviewer": "independent-auditor, fresh read-only session; not the author"}
```

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
