# Brief: product-spec worker for DAEO-wahn (W2-175), round 1

You are a fresh **product-spec** session (template `role-product-spec` 1.0.0, in your system prompt). This brief was written by hand by the ticket lead: `gov context DAEO-wahn --role product-spec` refused (`CONTEXT_OVER_CEILING`, 21044 of 6000 tokens). Where this brief and the copied `EMG-common.md` / `EMG-d4b-launched.md` beside it differ, **this brief holds** (in particular: your `Implements:` trailer is the list below, not `DEC-1065`; a lead does run for this ticket).

## Identity and where you work
- Role `product-spec`, ticket `DAEO-wahn` (W2-175). Check: `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-wahn`); `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-175` and `w2/W2-175`). Different: stop and say so.
- **Step 0, before any work, the sandbox check, reported first in your return:** (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-wahn','w').write('x')"` must FAIL; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop and return.
- The base commit (the commit the branch starts from): `7709021ad6cc` (in the CIT-P record name it in full: `git rev-parse 7709021ad6cc`).
- **The paths you may write, and only these:** `template/governance/kernel/templates/role-cto.md`, `role-engineer.md`, `role-lead.md`, `role-product-spec.md`, `role-research.md`, `role-reviewer.md`, `role-test-designer.md` (all under `template/governance/kernel/templates/`) and `docs/changes/W2-175-CIT-P.md`.
- **Never** write `brief.md`, a `brief-*.md` pointer, `keys.yaml`, `facts.yaml`, a skill, a file under `roles/`, any `.claude/` or `.rulesync/` path, `tests/acceptance/**`, `.tickets/`, the decision register (the ticket's non-goals; DEC-315). If you need another file, that is a needed split: name it in your return, do not route round it.

## Policy 2 (c) for you (DEC-820, DEC-1093 (2))
You never read `tests/acceptance/W2-175/` (the independent test designer writes it in parallel, in another worktree; you never read that worktree, `/home/usain/gov-os-worktrees/W2-175-tests`, either). Every Grep or Glob call that could reach `tests/acceptance/W2-175/` excludes it (`!tests/acceptance/W2-175/**`), and so does every recursive Bash search (`grep -r --exclude-dir=W2-175`, `rg -g '!tests/acceptance/W2-175/**'`); if a search shows you a line from there anyway, stop reading it and say so in your return. The lead merges the tests after you return; you do not wait for them. You may read W2-128's tests (`tests/acceptance/W2-128/`) freely and run them.
(d): never read the hidden half of any evaluation set (`~/gov-os-eval`) or the held-out material's contents; never print a secret.

## What to do: the ticket's Approach, Interface and Rabbit holes, word for word (`.tickets/DAEO-wahn.md`; read it whole)
**Approach (if known).** One product-spec session adds to each of the seven role templates the lines below, near each template's existing rule lines, ending each with its decision id in brackets, then raises the `version` of each changed file to 1.0.1 and writes the CIT-P record with the base and new sha256 of every file. The independent review reads the delta only; the owner approves the new bytes (the route of DEC-1116); the CTO then runs the copies ACT for `.claude/templates/`. Alternative, costed and set aside: put the rules in `brief.md` only (every session reads it, but a role's system prompt would still lack them, and the owner asked for the templates).

**Interface (the lines, stated before the pair starts).** A template may shorten a line; it may not drop an idea.
- Policy 2, all seven: "Reads are open: the whole repository, other worktrees, git history and what your searches return. Refuse only four things: secrets and keys (never printed); the held-out qualification material's contents (its file names may be seen); the counterpart's work on the same ticket; the hidden half of an evaluation set [DEC-820]."
- (c), the engineer: "Never read this ticket's acceptance-test code; run its cases and read their names, pass or fail and failure messages [DEC-820, DEC-957]." The sentence must carry a negation: W2-128's TPL-1 S3 case refuses an engineer sentence that names the acceptance tests with a reading verb and no `never`, `not` or `no`.
- (c), the designer: "Never read this ticket's implementation (what its branch changes other than your own tests); work from the specification, the KPI lines and the existing code [DEC-820, DEC-963]." Line 4 of the base already says the first half; keep it and add what is missing.
- The reviewer: "You read everything, tests and code alike [DEC-820]."
- The record rule, the six non-CTO templates: "The owner's decisions are recorded by the orchestrator's decision-record commits; never put `Role: owner` or `Decided-by:` on a commit of yours [DEC-861]."
- The stop, all seven: "Refused twice for the same call: stop and say so. Never work around a refusal: report it." (the sentence of `brief.md`'s return section, copied, then `[DEC-1137]`).
- The base for the sha256 and the diff checks is the commit the ticket's branch starts from; the record names it.

**Rabbit holes.**
- Do not edit `brief.md`, a pointer, `keys.yaml` or `facts.yaml`; the stop sentence is copied from `brief.md`, never reworded.
- Do not cite DEC-849 or DEC-508 as the rule: DEC-849 stands only until W2-58 lands and DEC-820 replaced DEC-508.
- Do not add a placeholder that is not in `keys.yaml`; `{DATE}` and `{ID}` are keys, a literal date is not.
- `role-reviewer.md` is the tightest against its 3500-character budget: measure before the lines go in.
- Do not write `.claude/templates/`; `python3 -m gov.adapters.portability` reports those copies as differing until the copies ACT runs (as after W2-128), so the close of this ticket names that finding and does not fix it.

The KPI lines the result is judged by are in the ticket (S1 to S7, F1, F2): read them. In short: the Policy 2 statement in all seven is one statement (one paragraph, list item or table row) that carries `read` and `open`, `secret`, `held-out`, `counterpart` and `hidden half` and ends with `[DEC-820]`; the engineer's and designer's (c) lines each one statement with a negation; the reviewer's one statement with `everything`, `tests` and `code`; the record rule one statement with `decision-record`, `owner` and `Role: owner`, ending `[DEC-861]`, in the six non-CTO templates; **`role-cto.md`'s existing decision-record line (file line 29) stays byte for byte unchanged** and role-cto gets no new record line; the stop sentence byte-equal to `brief.md` line 62 in all seven (copy it from that file, do not retype it).

## Budgets (prose characters: W2-128's measure, `prose()` in `tests/acceptance/W2-128/w2_128_support.py`: the body less fenced blocks and table lines), measured on integrate
| template | prose now | budget |
|---|---|---|
| role-cto | 3178 | 6000 |
| role-engineer | 1205 | 3500 |
| role-lead | 4605 | 8000 |
| role-product-spec | 1554 | 3500 |
| role-research | 1345 | 3500 |
| role-reviewer | **2551** | 3500 (949 left: tightest; the four lines come to about 600) |
| role-test-designer | 1833 | 3500 |
Measure each file before and after with a script file importing that `prose` function (or W2-128's `test_s2_prose_is_within_r3_budget`).

## Method
1. Read each of the seven templates, `brief.md`, `keys.yaml`, `governance/project/facts.yaml` (budgets), `docs/changes/W2-128-CIT-P.md` (the record form) and the register entries `### DEC-820`, `### DEC-861`, `### DEC-1137`, `### DEC-1116`, `### DEC-1121` in `docs/DECISION_REGISTER.md` (grep the heading, then read by line range; the register is large).
2. Add the lines near each template's existing rule lines. Additions only; a template may shorten a line you add, never drop an idea; **no rewording of a rule a template already carries** and **no new rule beyond the three the owner named** (DEC-1137 (2)). For role-test-designer, keep item 4 as is and add the missing half (the specification, the KPI lines and the existing code) in a way that keeps one statement carrying the negation. Every line that states a rule ends with its decision id in brackets, ACCEPTED only (`test_f7_every_bracketed_decision_id_in_a_template_is_accepted` reads them).
3. `version: 1.0.0` → `version: 1.0.1` in all seven; no other front matter change.
4. Write `docs/changes/W2-175-CIT-P.md` in the form of `docs/changes/W2-128-CIT-P.md`: front matter `id: W2-175-CIT-P`, `type: change-impact-proposal`, `status: PROPOSED`, `ticket: DAEO-wahn (W2-175)`, `branch: w2/W2-175`, `decisions_read:` and `decisions_carried:` each citing at least DEC-1137, DEC-820 and DEC-861 (and the others you read); the base commit named in full; then **one section per CAP-33 step, headed with its name**: (1) the evidence (the trigger: DEC-1137 (2), (3); W2-153: a launched session reads its role template as the system prompt; `governance/project/orchestration/packages/P1-W2-11-BRIEFS.md`), (2) the proposal (a table: each changed file, its base full sha256, its new full sha256, the lines added; the three options of DEC-105 where they apply), (3) the independent review (marked pending: the lead fills it after the review), (4) the owner's approval (marked pending, not filled), (5) the versioned promotion (marked pending; 1.0.0 → 1.0.1); and the note that the `.claude/templates/` copies are left to the copies ACT, and `python3 -m gov.adapters.portability` will report `TEMPLATE_COPY_DIFFERS` until then. Compute the new sha256 after the last template edit, with `sha256sum`; the full values live only in this record.
5. Your own checks, each once: `tests/acceptance/W2-128` (the budget, placeholder, S3 and F7 cases must stay green): `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-175/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-175/src python3 -m pytest tests/acceptance/W2-128 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"` (if the sandbox refuses the heavy slot, run the single file `tests/acceptance/W2-128/test_w2_128_templates.py` directly and say so). Never the full suite, never `-x`.
6. **Commit before any long run**, once the templates and the record are written:
`git commit -m "W2-175: the seven role templates carry Policy 2's four refusals, the record rule and the stop (1.0.1); CIT-P record" --trailer "Task: DAEO-wahn" --trailer "Role: product-spec" --trailer "Implements: DEC-1137, DEC-820, DEC-861, DEC-1116, DEC-1050, DEC-1121, DEC-957, DEC-963, DEC-1073, DEC-315, CAP-33" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- template/governance/kernel/templates/role-cto.md template/governance/kernel/templates/role-engineer.md template/governance/kernel/templates/role-lead.md template/governance/kernel/templates/role-product-spec.md template/governance/kernel/templates/role-research.md template/governance/kernel/templates/role-reviewer.md template/governance/kernel/templates/role-test-designer.md docs/changes/W2-175-CIT-P.md`
Name the kernel change under the CIT-P in the commit body. If a check fails after the commit, a correction is a new commit (same trailers). Never amend, rebase, merge or push. Before committing: `test ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/pre-commit`; never `--no-verify`.

## Rules
- DEC-732, word for word: **every test run and every `gov` command used for verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-175/src` set per command.**
- Memory: `gov retrieve` is not available in your sandbox (DEC-1065): use Read and Grep on your tree. When a search does not answer, or your answer may be incomplete, search once more in different words, then answer from both with path and lines, or say "not found"; two searches in all (DEC-1092 (1)). Never one giant query (DEC-860).
- DEC-849: the guard may refuse some reads (searches from the repository root, `governance/project/`, `.claude/`): take the refusal, search named folders instead; count the refusals in your return.
- Command forms the guard reads: one simple command per Bash call; no `cd ... &&`; no here-documents, backticks, `$(...)` or shell variables as a write target; no long inline `python3 -c` with braces; anything longer in a script file under `/home/usain/gov-os-worktrees/W2-175/.gov-runtime/scratch/ps/` (Write tool), run with `python3 <file>`.
- Row W2-L423's rule (DEC-911): sha256 values in full only in the CIT-P record; elsewhere (your return, scratch) the first 12 hex digits; commit hashes as 12 digits; never write the keywords of the secrets rule that takes a bare 40-hex string.
- Scratch budget (DEC-898): your share 2 GB and 100,000 files outside the tracked tree; clean as you go.
- No installs (P1 in your return). No copy of the tree.
- An interface point the ticket leaves open: take the simplest reading and name it in `discoveries`; never widen the scope.
- **Refused twice for the same call: stop and say so. Never work around a refusal: report it.**

## Return (your last message; nothing else is read)
Add to the fields: the sandbox check result first; in `evidence`, each template's prose size before and after against its budget, each file's sha256 before and after (12 hex digits each), the lines added per file, your commit(s) (12 digits) with trailers, the W2-128 run's counts; the retrieval/refusal counts.

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

The twelve fields come first, each as a labelled line, any payload after them. Refused twice for the same call: stop and say so.
