You are a fresh product-spec worker (brief A4), on a repair. Ticket: DAEO-k7hz (W2-11, "Briefs and the orchestration skill"), profile STANDARD, round 1 of two declared rounds (DEC-916). You work only in the worktree `/home/usain/gov-os-worktrees/W2-11` (branch `w2/W2-11`). This is a kernel skill change (CAP-33): your edits stay on this branch; the owner's approval comes through the combined K3 CIT-P (DEC-954 Q7) and the merge waits for it. Your budget: about 90 minutes.

## Step 0, before any work: the sandbox check (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-k7hz','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.
Then: `printenv GOV_ROLE GOV_TICKET` (expect `product-spec`, `DAEO-k7hz`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-11`, `w2/W2-11`). If anything differs, stop and say so.

## What happened, and what you fix
An earlier product-spec worker built this round in four batches on this branch (commits 45e57f00, 4f5dffc1, adeda5b8, 99dd5ca5, ecb7824a, a6999485, 8d6fbd72): the five brief templates (`template/governance/kernel/templates/brief-*.md`), the orchestration skill and its reference files, the audit skill, the test-design skill and `test-kinds.md`, the skill template `template/governance/kernel/templates/skill.md`, the new `qa-review` skill, the orchestrator role file's sweep sentences, the version lines (`metadata.version`), the rulesync sources and the CIT-P `docs/changes/W2-11-CIT-P.md`. Read the ticket `.tickets/DAEO-k7hz.md` (its KPI lines), the CIT-P, and `git log -p 4c064bab..HEAD -- template/ .rulesync/ docs/changes/` for what was done.

Its one run of the acceptance tests (`tests/acceptance/W2-11` and `tests/acceptance/W1-35`) reported the failures below. **This is the failing output you are given (DEC-096); fix the text so these pass, building to the spec and the KPIs, never to the tests.**

**A cause your lead has found:** batch 1 rewrote the brief templates and shortened the orchestration skill, and in doing so dropped sentences and clauses that earlier, still-standing requirements (W1-35's delivery under DEC-537, DEC-539, DEC-541 and the decisions it cites) require, some word for word. **Repair by comparing with the base** (`git show 4c064bab:<path>` for each brief template and for `template/governance/kernel/skills/orchestration/SKILL.md`, `.../test-design/SKILL.md`): restore every base sentence and clause that no newer decision supersedes, exactly as it stood, and change only what a newer decision changes: DEC-820 (Policy 2: reads open; no listing or search refusal; the held-out list's names readable), DEC-847 (no fixed ceiling of tickets in flight), DEC-838 and DEC-837 (no `LEAD_CHECKPOINT`, no context-limit stop; a checkpoint at every handover), DEC-861 and DEC-862 (decision-record commits), DEC-959 item 7 (the work order in parallel instead of "tests first"; "written before implementation" goes). Keep everything batch 1 added that its KPIs require. Where a restored clause would push the orchestration skill's body past the validator's limit (2,500 tokens), keep the clause in SKILL.md and move other detail into its reference files (one level deep, linked).

Failures to fix (case name, then its one-line message where one was printed):
- `tests/acceptance/W2-11/test_w2_11_briefs.py::test_dec_486_is_not_cited_for_the_stops_short_block`: "DEC-486 covers the closed count only; still cited for the block" (the orchestration skill's Stops line; read DEC-486 and DEC-537 and cite the decision that covers the block).
- `test_w2_11_skills.py::test_the_test_design_skill_states[red against the ticket's base]`: "test-design does not state: red against the ticket's base".
- `test_w2_11_skills.py::test_the_test_design_skill_states[...]` for three more items: the 2,980-lines-for-713 example (W2-60a's figures, DEC-951 item 5), the README map that `gov accept` reads, and the work order in parallel. The skill must state each in its own SKILL.md body (a reference file may add detail), in plain words close to the KPI line.
- `test_w2_11_skills.py::test_the_qa_review_skill_states[severity tied to P3/P2/P1]`: "qa-review does not state: severity tied to P3/P2/P1".
- `test_w2_11_briefs.py::test_policy_2_reads_open_with_its_refusals[brief-reviewer.md]`.
- `test_w2_11_briefs.py::test_the_lead_brief_carries_the_role_independent_rule[...]` for three rules: `brief_gaps:` in the return; the code under test per command (DEC-732: the worktree's own `src/` set per command); the work order in parallel. State each plainly in `brief-lead.md`.
- `tests/acceptance/W1-35/test_w1_35.py::TestNoPermissionGrants::test_procedural_statements_cite_policy[test-design]` (every procedural statement of the test-design skill cites its governing policy or decision).
- `test_w1_35_orchestration.py::TestRows::test_every_clause_of_the_row_is_stated` for ten rows: briefs, checkpoints and context, commits, decisions, integration order, learning metrics, parallel tickets, sessions, stops, the ticket loop (message begins "a reader of [the skill and briefs] …"). The base skill and templates stated these clauses; restore them as above.
- `test_w1_35_orchestration.py::TestBriefTemplates::test_the_brief_carries_the_standing_sentences_word_for_word[engineer|lead|product-spec worker|reviewer|test designer]`: the base templates' standing sentences, word for word, as revised only by the decisions named above.
- `test_w1_35_orchestration.py::TestWording::test_this_repositorys_own_values_are_not_the_rule`: "the delivered text carries a value of this repository's wave where a project's own value, given by a placeholder, belongs" (find the value, e.g. a wave number or a figure of this repository, and put the project's placeholder, DEC-539).
- `test_w1_35_orchestration.py::TestStatusRoute::test_the_route_names_the_parts_the_answer_is_given_from`: "orchestration/SKILL.md: … these parts are not named: ['tickets', 'open packages', 'gates', 'readiness', 'governance share', 'pause state', 'healt…" (the base skill's status route; restore it).

**Not yours, leave them red:** the cases about the generated copies under `.claude/` (your sandbox cannot write `.claude/`; your lead has a package for it); `test_w2_11_validator.py::…` (needs `src/`, a package); `test_w1_35_orchestration.py::TestBriefTemplates::test_no_brief_is_named_like_a_record_template` (it contradicts the ticket's KPI W2-L258, a package); `test_w1_35.py::TestSpecificationWorkOrder::test_work_order_correct_sequence_discovery` (the discovery skill's text was not changed; being checked on the base). Do not change any file to make these pass.

## Keep the copies in step
After the kernel edits, make the rulesync sources match again: `.rulesync/skills/<name>/` and `template/.rulesync/skills/<name>/` byte for byte with the kernel skill folder for every skill you touch (a SKILL.md by front matter and body), single named files by a script, never a tree copy; `.rulesync/subagents/orchestrator.md` and `template/.rulesync/subagents/orchestrator.md` only if you touch the role file (you should not need to). Versions stay as they are (raised once this round already). Do not try to write `.claude/` (refused by your sandbox).

## Checks before you return
- Skill validator green on every skill you touch: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/<name>`.
- A sweep of your files for `LEAD_CHECKPOINT`, "context limit", "ceiling", "before implementation", "tests first", `W2-`, `EXAMIN`, `gov-os-`: none, except where the base sentence is restored exactly and no decision supersedes it (say which).
- **One run, after your last commit, of the failing cases above only**, reading results only (names, pass or fail, failure messages; never the test source), in the background-safe form (it may take minutes): `TMPDIR=/tmp/gov-os-lead-W2-11 PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src python3 -m pytest tests/acceptance/W2-11/test_w2_11_briefs.py tests/acceptance/W2-11/test_w2_11_skills.py "tests/acceptance/W1-35/test_w1_35_orchestration.py::TestRows" "tests/acceptance/W1-35/test_w1_35_orchestration.py::TestBriefTemplates" "tests/acceptance/W1-35/test_w1_35_orchestration.py::TestWording" "tests/acceptance/W1-35/test_w1_35_orchestration.py::TestStatusRoute" "tests/acceptance/W1-35/test_w1_35.py::TestNoPermissionGrants" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=line`. Report the counts and every failing case with its message line. If a case still fails after one honest repair, report it; do not loop more than once.

## What you read, and Policy 2 (DEC-820)
- Read the ticket, its card (`docs/plan/WAVE_2_WBS.md` §2, "#### W2-11"), the decisions named above in `docs/DECISION_REGISTER.md`, `governance/project/orchestration/packages/ROLES-SPEC-1.md` §3.0 and §6.1 (G13 to G15), `governance/project/briefs/JUDGEMENT.md`, and the files you change, at the base and now.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src python3 -m gov.cli.main retrieve "<question>" --json` (this worktree's store may still be missing: on `STORE_MISSING`, read the named files directly and report it). **DEC-860:** never one giant query; batches (`--batch-size`, then `--continue <token>`). **DEC-859:** a code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted.
- Reads are open except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material; (c) the counterpart's work on this ticket: **you never read `tests/acceptance/W2-11/` or `tests/acceptance/W1-35/`** by any tool; you may run them and see names, results and failure messages; (d) the hidden half of any evaluation set. Never read or name the qualification oracle. Never write in `~/gov-os-workbench`.
- **DEC-849:** the guard may still refuse some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals in your return.

## The code under test (DEC-732), word for word
In this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src` set **per command** (never in a session's `--settings` env).

## Paths, machine, commands
- Write only inside the ticket's `allowed_paths`, and within them only what this repair needs: the kernel templates and skills named above, their rulesync sources, and the CIT-P if a change needs a line there. Never `tests/**`, `src/**`, `.claude/**`, `.tickets/`, the register, the plan files, `governance/project/**`, or `.gov-runtime/**` outside `.gov-runtime/scratch/**`. Use your session scratchpad for scripts (the Write tool is refused under `.gov-runtime/scratch/ps/`).
- Budget (DEC-898): 5 GB and 250,000 files and folders outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-11` unless the sandbox sets its own; pytest's own retention, never `--basetemp`; clean up what you make; measure your scratch (`du -s --inodes`, `du -sh`) and give the figures. No tree copies (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it); nothing copied under a `.gov-runtime/` folder (DEC-673).
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, commit hashes as 12 digits, never the full 40, and never the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Commands the guard can read (DEC-941 item 4a):** no shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; longer things go in a script file. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6). On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status `AUTH_REQUIRED`.

## Commits
Before each commit check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`; no amend, rebase, reset, push, `git clean` or checkout of another commit. `git commit -m "<subject>" --trailer "Task: DAEO-k7hz" --trailer "Implements: <ids>" --trailer "Role: product-spec" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`; `Implements:` only ids the register or Contract holds (`DEC-n`, `CAP-n`), e.g. `DEC-537, DEC-539, DEC-820, DEC-847, DEC-959, CAP-33`. Never `Role: owner`, never `Decided-by:`.

## Never
Never run `gov close`, `gov adopt` or `gov pause`; never run `docs/plan/tools/validate_s1.py`; never ask or notify the owner; install nothing; no sudo; never read the held-out material's contents or print a secret.

## Return
One message, your last. The twelve fields first, each as a labelled line; any payload after. Also report: the sandbox check; lines added and removed per file; the validator per skill; the run's counts and failing cases; `gov retrieve` use; guard read refusals (DEC-849); scratch figures.

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

The twelve fields first, any payload after. Refused twice for the same call: stop and say so.
