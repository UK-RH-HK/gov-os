# The review of the kernel ticket template 1.0.1 (DEC-1121; W2-128, DAEO-t8mp), C3

- Brief: `.gov-runtime/scratch/orchestrator/briefs/W2-128-tpl101-review.md`; branch `w2/W2-128-tpl101` at `8df648cc9`; template sha256 `0f584330c6f1…`; reviewer (Opus, high, C3) log `/home/usain/gov-os-worktrees/W2-128-tpl101/.gov-runtime/scratch/lead/log/W2-128-tpl101-review.json`
- verdict.py: (False, ['ticket-template-1-0-1: F1 blocks (in scope, ordinary work, fails open)'])

**Sandbox check (step 0, launch_worker.sh / EMG-d4b):** passed. (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-t8mp` was refused with `OSError: [Errno 30] Read-only file system`, as it should be. (b) `git hash-object -w --stdin` worked (`1ae28402a109`) and `git update-index --refresh` exited 0. Those two git writes were the brief's own step 0; I wrote nothing else.
**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` printed nothing, so no model server of mine is running.

- **task:** DAEO-t8mp (W2-128). C3 review of the kernel ticket template 1.0.1 (DEC-1121), commit `8df648cc9690`, as the independent-auditor (reviewer). The worktree's HEAD is that commit.
- **status:** DONE. Verdict **fail**: one in-scope finding (F1) can be hit in ordinary work and lets a gate fail open. The fix is one comment line.
- **work_completed:** Checks 1–5 below; one test run; read-only otherwise.
- **files_changed:** none. `git -C /home/usain/gov-os-worktrees/W2-128-tpl101 status --porcelain` is empty.
- **evidence:**
  - Template sha256 recomputed: `0f584330c6f1c996873c66dd251b6f4ecc24ddd5c6220cf590f937a1dbbad65b`, matching the commit's claim.
  - The base commit's template (`905b82a3b`) hashes to `fd97779d…af956`, which is exactly the 1.0.0 line the owner approved in TEMPLATES-APPROVAL-1.
  - Scratch folder: `du -sh` 32K, `du -s --inodes` 12.
- **tests:** One run, the brief's exact command through `heavy_slot.sh`: **355 passed, 1 failed** in 81 s.
  - The one failure is `tests/acceptance/W1-08/test_w1_08_path_map.py::test_every_tracked_path_matches_exactly_one_namespace`: 5 files under `governance/project/indep-briefs/sgx1/` belong to no namespace. That is the known path-map fault ACT-PATHMAP-NS-2 fixes.
  - The totals match the reported 234+1 (W1-08) and 121 (W2-128). `test_the_ticket_template_carries_the_nine_fields` now passes.
  - The brief gave this command verbatim, so the EMG-d4b exclusions (`-m "not local_only" -k "not real and not green_here and not time_limit"`) were not added. Nothing was left out of the run.
- **discoveries:**
  - In the repository's 230-odd tickets, `class` is used as specification (12), audit (9), test-revision (15), config, ops, schema, template, tool, documentation, role-definition and coordination.
  - `src/gov` acts on five values:
    - `specification` triggers the readiness gate (`src/gov/close/command.py:224`, DEC-307).
    - `research`, `audit`, `integration` and `coordination` are judged on evidence (`src/gov/close/gates.py:25`).
    - `coordination` also has no tests of its own (`src/gov/util/role_paths.py:164`).
    - The readiness checker creates `audit` tickets itself (`src/gov/readiness/checker.py:231`).
    - A missing class closes as `implementation` (`src/gov/close/command.py:298`).
- **risks:** Through F1, a specification ticket filed from the template closes without its readiness-record gate.
- **lessons:** For a free-string field that code branches on, take a template comment's value list from the code's constants, not from a skill's prose.
- **proposed_decisions:** none.
- **unresolved:** Whether the CTO and owner read the comment as a closed list or as examples (this decides F1's consequence; see the reversal condition under F1).
- **recommended_next_action:** Product-spec changes the one comment line to name the values the code acts on, for example `# or specification, research, audit, integration, coordination, test-design, skill`. Re-hash, then a short second round confined to that line (round 2 of 2). Then the CTO brings the new hash to the owner.

## Answers to the checks

**1. Exactly two changes.** Yes. `diff 905b82a3b 8df648cc9` changes one file, `template/governance/kernel/templates/ticket.md`: 2 insertions, 1 deletion.
- `version: 1.0.0` became `1.0.1`.
- One line `class: implementation   # or research, test-design, discovery, data, integration, skill` was added before `role`.
- The parent is `905b82a3b`, nothing else is in the commit, and the sha256 matches (see evidence).

**2. The values.**
- The schema has `"class": { "type": "string", "minLength": 1 }`, optional: any non-empty text is valid, with no enum and no pattern.
- `implementation` is a valid default: it is the close's own fallback (`command.py:298`) and by far the most used value in practice.
- Placement and style are right: the line comes after `type`, before `role`, and its comment starts at the same column with the same `# or …` form as `role`'s.
- The comment's list does not match what `src/gov` reads (F1), and it does not match practice either (F2). It follows the planning skill's gap classes (`template/governance/kernel/skills/planning/SKILL.md:33-46`) instead.
- It does not mislead anyone into reading it as RUBRIC-2's criticality class. The values are kinds of work, none is C0–C3, and DEC-1120 (1) takes criticality "from the ticket's profile and paths and the ACT's class", not from a ticket field. No finding.

**3. Pins.**
- No test, `src/` code, `keys.yaml` entry or `facts.yaml` entry pins the ticket template's version or hash. `class: implementation` is no `{KEY}` placeholder, so `keys.yaml` is unaffected. There is no README in the templates folder.
- `governance/project/orchestration/packages/LIFT-1/TEMPLATES-APPROVAL-1.md:23` pins 1.0.0 at `fd97779d…`. That is correct for 1.0.0, and the 1.0.1 line is the CTO's to add after the owner approves.
- `docs/changes/W2-128-CIT-P.md`'s row for `ticket.md` has no `class` or 1.0.1 note yet, and DECIDED-NOT-DONE row 108 still reads NOT STARTED. Both are the CTO's follow-ups after the merge.

**4. The run:** 355 passed, 1 failed (see tests).

**5. Trailers:** all four are present: `Task: DAEO-t8mp`, `Implements: DEC-1121`, `Role: product-spec`, `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- The Sonnet trailer is truthful under RUBRIC-2, which puts product-spec on Sonnet. It differs from the Opus string in EMG-common.md, but that is accurate attribution, not a finding.

**Probed and found sound:** the diff's scope; the hash; the base being the approved 1.0.0 bytes; the schema still validating the template; placement and style; no collision with criticality; no pin that breaks; the trailers; the W2-128 `commented or explained` check for every key.

## Findings

**F1: the comment leaves out `specification`, `audit` and `coordination`, the classes `gov close` treats differently.**
- What happens: someone writes a specification ticket from the template, for example a skill-writing ticket like W2-98, W2-100, W2-102 or W2-103. They follow the comment and pick `skill` or `implementation`, since `specification` is not offered.
- `gov close` runs the DEC-307 readiness-record gate only when the class is `specification`. These tickets do have their own acceptance tests, so the close does not stop on "no acceptance tests". It runs them, passes, and closes without checking that the readiness record is closed.
- An audit ticket labelled `research` is refused instead, for having no `type: research` record, which fails closed.
- What should happen: the comment names the classes the close keys on, so a template-filed ticket gets its gate.
- Decisions: DEC-1121, DEC-307, DEC-892 (W2-H045).
- Ordinary work: yes, because the template is meant to be the one source for filing tickets, its `# or …` reads as the full list, and specification tickets with their own acceptance tests are routine here.
- Consequence: fails open. The readiness-record gate is skipped.
- Reversal: this becomes `other` and the verdict pass if either is shown: (i) the readiness record of a specification ticket is enforced somewhere that does not depend on `class` (e.g. `gov ready` or the plan validator); or (ii) the CTO or owner records that the list is illustrative and that ticket classes are set from the register, not the template.
- Note: before 1.0.1 the template had no `class` at all, and an omitted class closes as `implementation`. So this gap is not new; 1.0.1 just does not close it.
- scope: in.

**F2: the list names `discovery` and `data`, which no ticket uses and no code reads, and leaves out classes in daily use.**
- Missing from the list: test-revision (15 tickets), config, ops, schema, template, tool, documentation, role-definition.
- What should happen: the list matches the code's classes first, then the ones in use.
- Decisions: DEC-1121.
- Ordinary work: yes, because every new ticket's author reads this line.
- Consequence: other. The schema accepts any string and none of these values changes a gate. The cost is drift between the template and the ticket store.
- Reversal: this finding falls if the planning skill's gap classes are confirmed as the intended vocabulary for new tickets.
- scope: in.

**F3: the commit message says the default comes from "the 1.0.0 template's old default (implementation)", but 1.0.0 had no `class` line.**
- The `class: implementation` default was in the template before 1.0.0 (W1-08's `079d73742`); round 1 (`a6c83d497`) removed it.
- What should happen: the record names the right source.
- Decisions: DEC-1121.
- Ordinary work: yes, because a reader tracing why the field returned would follow the message.
- Consequence: other. It is wording in the record only.
- Reversal: this finding falls if a 1.0.0 version of the template that carries `class:` turns up.
- scope: in.

Classification: 3 findings. F1 is in scope, reachable in ordinary work, and fails open. F2 and F3 are in scope, reachable in ordinary work, with consequence other. I propose a second round limited to the comment line, which covers F1 and F2; F3 is a row in the record.

```verdict
{"kpis": [{"kpi": "ticket-template-1-0-1", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
