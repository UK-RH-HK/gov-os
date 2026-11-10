# D-10's red-fix list: the review of W1-08's samples taken from the 1.0.0 templates' record block (W2-128, DAEO-t8mp)

You are a fresh, read-only independent reviewer. **Narrow scope: one test-support revision in W1-08.** READY is
computed by `verdict.py` from your block.

## What happened
- W2-128's kernel templates were approved as 1.0.0 (DEC-1116). Each now has a front matter that describes the template
  itself, and the record's shape in a fenced ```yaml block with placeholders.
- W1-08's acceptance tests used each template's front matter as a sample record, so 10 default cases (and 23 more in
  the opt-in suites) went red: the ticket's front matter has no `kpis`/`allowed_paths`/`role`; the checkpoint's
  `task: ''` breaks the id grammar; and `role-research.md` was picked up as a "research" record template.
- A test designer revised the sample's source only (DEC-866, Rewrite-Reason): one helper takes the record from the
  ```yaml block (else the front matter), fills placeholders from a fixed table, and `template_paths()` skips `role-*`
  and `brief-*` files. It reports: default run 10 failed/111 passed → 121 passed (114 deselected, unchanged); with
  `--optin=lifted,breadth` 33 failed → 1 failed (`test_the_ticket_template_carries_the_nine_fields`: the 1.0.0 block
  has no `class`, which CAP-31.a names; left red for the CTO, DEC-105, out of your scope).

## What to review
- `git -C /home/usain/gov-os-worktrees/W2-128-w108-tests diff 95f4c0348 a0957eb56` (one commit, head `a0957eb56`):
  `tests/acceptance/W1-08/w1_08_support.py` and `test_w1_08_templates.py`.
- The templates `template/governance/kernel/templates/ticket.md` and `checkpoint.md`; the schemas under
  `template/governance/kernel/schemas/`; CAP-31.a in `docs/contract/CONTRACT_v4.md` (line ~494).

## Check
1. **Nothing weakened:** every assertion keeps its meaning. A case that checked a field "in the template" now checks it
   in the record the template's block gives, and still fails if the block loses that field. No refusal case lost its
   refusal; no case removed, skipped or deselected (count unchanged).
2. **The placeholder table is neutral:** each filled value is a fixed valid example, not chosen to make a schema pass
   that the template's own shape would fail (e.g. does filling `task: ''` with an id hide a template defect, or is an
   empty `task` truly a placeholder?). Say which, with the template's own words.
3. **The `role-*`/`brief-*` skip:** are those files truly not record templates (check their front matter and the W1-08
   README's definition of a record template)? Could the skip hide a real record template now or later?
4. **The run:** re-run once, in the worktree, read-only (no writes outside your sandbox TMPDIR):
   `env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=/home/usain/gov-os-worktrees/W2-128-w108-tests/src python3 -m pytest /home/usain/gov-os-worktrees/W2-128-w108-tests/tests/acceptance/W1-08 -q -p no:cacheprovider --no-header -o tmp_path_retention_policy=failed -p no:randomly`
   (if HOME is empty in your sandbox, set `PYTHONUSERBASE=/home/usain/.local`). Report the counts only.
5. **Trailers and scope:** Task, Role, Implements, Rewrite-Reason, Co-Authored-By; only `tests/acceptance/W1-08/**`.

KPI id for the verdict block: `w1-08-template-samples`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this revision.

## Write and return
- **You write nothing** in any tree. One test run (check 4) only. No GPU, no installs. Single simple Bash commands
  (DEC-1080). `EMG-common.md`'s hidden-half rule holds. Row W2-L423's rule: under `.gov-runtime/`, commit hashes as 12
  digits and none of that rule's keywords. Any wait by pid only.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your answers to the checks;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "<id>", "verdict": "pass|fail", "findings": [...]}]}`, one entry per KPI id named above,
    each finding `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 15 minutes.
