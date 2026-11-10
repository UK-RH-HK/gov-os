Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-128-w108-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: W1-08's 10 cases read the 1.0.0 templates' header as a sample record (W2-128, DAEO-t8mp)

You are a fresh **independent test designer**, launched under W2-128's ticket (`.tickets/DAEO-t8mp.md`: the kernel
templates). You revise W1-08's acceptance tests under DEC-866 (supersession propagates). You never change a template,
a schema or any code.

## The behaviour to fix (a described behaviour, DEC-136)
W2-128's kernel templates were approved and promoted as version 1.0.0 (DEC-1116, register line ~14197). Each template
under `template/governance/kernel/templates/` now has a short front matter that describes the template itself (e.g.
`ticket.md`: `name: ticket`, `version: 1.0.0`, `role: any`, `id: PROJ-0000`, ...), and puts the record's real shape in
a fenced ```yaml block in its body, with placeholders (`<the outcome, in one line>`, `DAEO-xxxx`, `src/gov/<area>/**`).

`tests/acceptance/W1-08/` (W1-08: the record schemas and templates) uses the template file's **front matter** as a
sample record and validates it against `ticket.schema.json` and the checkpoint schema
(`tests/acceptance/W1-08/w1_08_support.py`, `template()` near line 172, the assertion near line 264). At `95f4c0348`
ten cases are red, e.g.:
- `checkpoint.schema.json refuses the checkpoint template` (several cases);
- `checkpoint.schema.json refuses a checkpoint record whose state_class is AUTHORITATIVE`;
- `ticket.schema.json refuses the ticket template` (several cases);
- `the ticket template has no kpis` / `the ticket template has no allowed_paths` (`test_w1_08_ticket.py` ~line 64).
They were green before W2-128's templates. The schemas are right and the templates are approved; the tests' choice
of sample is what the new templates superseded.

## The task (DEC-866: the sample's source changes; what each case asserts is kept)
1. Run W1-08's cases once (command below) and list the red ones by name.
2. For each red case, change only where its sample record comes from, so it is a record of the template's shape:
   - **preferred:** the template's fenced ```yaml block, parsed, with its placeholders filled by fixed, valid values
     in one helper in `w1_08_support.py` (e.g. an id the id grammar accepts, a real path for `<area>`), so the case
     still proves "a record written from the kernel template is accepted by the schema" and still fails if the
     template's block loses a required field (`kpis`, `allowed_paths`, ...);
   - **else** a fixture file under `tests/acceptance/W1-08/` that copies the block's fields, with a comment naming the
     template it mirrors; say in your return why the block could not be used.
   Keep every assertion's meaning: a case that checked "the template has `kpis`" checks it on the block. A case that
   checks a schema refusal (e.g. the state_class case) keeps its refusal; only its base record changes.
3. Change nothing else: no template, no schema, no code under `src/`, no other ticket's tests, no green case's
   assertion. If a case cannot be fixed without changing a template or schema, leave it red and say why (that is a
   DEC-105 contradiction for the CTO, not yours to settle).
4. Run W1-08's cases again: all green, and the count of cases unchanged (none removed or skipped). Also run
   `tests/acceptance/W2-128/` once to show it is unaffected (it may be absent; then say so).
5. One commit with `--trailer "Task: DAEO-t8mp" --trailer "Implements: DEC-1116" --trailer "Role: independent-test-designer"`
   `--trailer "Rewrite-Reason: DEC-866: W1-08 used the kernel templates' front matter as sample records; the 1.0.0 templates (DEC-1116) carry the record's shape in a fenced block, so the sample is taken from it, each assertion kept"`
   `--trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`. Never merge, push, amend or rebase.

## The run command (each run, in this form, from the worktree root)
`env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=$PWD/src python3 -m pytest tests/acceptance/W1-08 -q -p no:cacheprovider --no-header -o tmp_path_retention_policy=failed`
Cut its output to the summary and the failing names (head and tail), never the whole log into your context.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-128-w108-tests`, branch `w2/W2-128-w108-tests`, at `95f4c0348`.
- Write only `tests/acceptance/W1-08/**`. `TMPDIR` a folder of your own under the sandbox's TMPDIR.

## Rules
- `EMG-common.md` holds, its hidden-half rule included. No GPU, no installs, no other test runs. Never
  `git worktree prune`. Single simple Bash commands. Any wait by pid only, never a name match.
- Row W2-L423's rule: under `.gov-runtime/`, commit hashes are written as 12 digits and none of that rule's keywords
  is written there.
- If your context passes ~200k tokens, commit what is green, write a hand-over note in your return and stop.
- Estimate: 30 minutes. Return the twelve fields, short: the red cases before, each change (file, what the sample now
  is), the run's counts before and after, the head.
