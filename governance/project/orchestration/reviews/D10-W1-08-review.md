# D-10's red-fix list: the review of W1-08's samples taken from the 1.0.0 templates' record block (W2-128, DAEO-t8mp)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-W1-08-review.md`; branch `w2/W2-128-w108-tests` at `a0957eb56` (designer commit `a0957eb56`); reviewer log `/home/usain/gov-os-worktrees/W2-128-w108-tests/.gov-runtime/scratch/lead/log/D10-W1-08-review.json`
- verdict.py: READY (3 findings, none blocking: F1, F3 not ordinary work; F2 consequence other).
- The CTO's disposition: F1 and F3 (not ordinary work) kept as rows; F2 (the README's readings 1 and 2 lag the tests) with the next W1-08 change; the breadth case `test_the_ticket_template_carries_the_nine_fields` (the 1.0.0 block has no `class`, CAP-31.a) to the owner as DEC-105.

I found no blocking problems. The revision changes where the W1-08 tests get their sample record from without weakening any check, and my single run matches the designer's count: **121 passed, 114 deselected**. There are three non-blocking findings (F1–F3 below), and the verdict is pass. The only red the designer reports is still `test_the_ticket_template_carries_the_nine_fields`, in the opt-in suites. I didn't run those suites and it is out of my scope.

**Sandbox check (step 0):**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-128` failed with `OSError: [Errno 30] Read-only file system`. Correct.
- (b) `git hash-object -w --stdin` worked (`1ae28402a109`) and `git update-index --refresh` worked (rc=0). Correct.

**`ps` check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.

- **task:** DAEO-t8mp (W2-128). Read-only review of W1-08's revision at head `a0957eb56e8b`.
- **status:** DONE
- **work_completed:** Did the sandbox and identity checks (HEAD = `a0957eb56e8b`, tree clean). Reviewed the diff from `95f4c0348` to `a0957eb56`. Read:
  - the helper file `w1_08_support.py`, and the test files that use it (templates, frontmatter, ticket, id_grammar, lesson);
  - the `ticket.md` and `checkpoint.md` templates, plus `role-research.md`, `brief-engineer.md` and `lesson.md`;
  - the common, ticket and checkpoint schemas;
  - the W1-08 README's "readings" (its definitions);
  - the checkpoint template's history.

  Ran the test suite once (check 4).
- **files_changed:** none. `git status --porcelain` is empty.
- **evidence:** One run of the brief's command, adding only `PYTHONDONTWRITEBYTECODE=1` so no `__pycache__` was written: `121 passed, 114 deselected in 40.22s`. TMPDIR is 24K (I didn't measure its file count).
- **tests:** The brief's command, unchanged apart from the line above. I did not add EMG-d4b's `-m "not local_only" -k "not real and not green_here and not time_limit"` because the brief gives its own command. The 114 cases skipped by default (the `local_only` ones and the opt-in suites) did not run.
- **discoveries:**
  - The checkpoint template's `task: ''` was a deliberate change in W2-128 round 2b (`9d95279c9cb0`). Before that it was `DAEO-0000`, which passes, and then `'{ID}'`.
  - For the ticket, filling the placeholders changes nothing the schema checks. `DAEO-xxxx` already fits the ticket id pattern `^[A-Za-z0-9]+-[a-z0-9]{4}$`, and the other placeholders sit in plain string fields.
- **risks:** The opt-in suites were not re-run by me, so their "33 failed → 1 failed" result rests on the designer's report.
- **lessons:** none.
- **proposed_decisions:** none.
- **unresolved:** The ticket template's 1.0.0 record block has no `class` field, which CAP-31.a names (DEC-105). That is the CTO's decision and out of my scope.
- **recommended_next_action:** Merge as it is. F1 and F2 can ride along with W1-08's next revision (DEC-802), or go in as Wave 3 rows.

## Answers to the checks

**1. Nothing weakened: holds.**
- Every case that read a template field now reads it from the record the template gives:
  - the ticket's fenced ```yaml block;
  - the front matter for templates without a block (checkpoint, lesson, failure, research, decision-record, decision-package).
- The field-presence checks still fail if the block loses the field: `field in good`, `missing`, `"state_class" in good`.
- Every refusal case still starts from that record and removes or replaces one field, so each refusal is kept.
- The diff only changes which helper is called in two places and adds new helpers. No case was removed, skipped, deselected or re-marked, and the default count is 121 + 114, the same as before.
- One case was not moved (F1): `test_no_template_stores_what_gov_derives` still reads the template's own front matter.
- If a template loses its block, the helper falls back to the front matter. For the ticket that front matter is the template's description of itself, so the tests go red.

**2. The placeholder table is neutral: holds.**
- **Checkpoint `task: ''`:** this really is a placeholder. The template says so next to the field: "`task: ''  # fill with the ticket's DAEO-… id, {ID} (DEC-1073)`". Its body adds: "give the record `task:` (the ticket's DAEO-… id)". The filler only changes a line that begins `task: ''` and puts in a valid example id, which is exactly what the template tells the writer to do.
- **Everything else is cosmetic.** For the ticket, `DAEO-xxxx` already fits the id pattern. `DAEO-yyyy`, `DEC-n`, `CAP-n` and every `<…>` sit in fields the schema only requires to be non-empty strings. For the checkpoint, `{ID}` sits in `inputs[].id`, also a non-empty string.
- **The filler cannot make an invalid value pass.** For fields limited to fixed values (`profile`, `trigger`, `state_class`, `scope`, `severity`, `lifecycle`), "an example" is not an allowed value and gets refused.
- The consequence is that the case "validates as it is written" now checks the filled text (F3).

**3. The `role-*`/`brief-*` skip: holds.**
- `role-research.md`'s front matter is `name`, `version`, `role`, `skills`. It has no `id`, `type`, `status` or `state_class`, so it is a role file, not a record template.
- The `brief-*.md` files have no front matter at all. Each is a one-line pointer, for example: "Replaced by `role-engineer.md` (the role) and `brief.md` (the envelope)".
- The README's reading 2 defines a record template as a file whose front matter (or a `.yaml` file) is the record, and these files are not.
- Only `role-research.md` matched a record word ("research"); no `brief-*` file matches any.
- The skip makes the existence check stricter, not looser. Before it, deleting `research.md` would have let `role-research.md` satisfy "a research template exists".
- It could only hide a real record template that someone named `role-…` or `brief-…`. No record word fits that pattern.

**4. The run:** 121 passed, 114 deselected.

**5. Trailers and scope: hold.**
- Trailers present: `Task: DAEO-t8mp`, `Implements: DEC-1116`, `Role: independent-test-designer`, `Rewrite-Reason: DEC-866: …`, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Files changed: only `tests/acceptance/W1-08/w1_08_support.py` and `test_w1_08_templates.py`.

**What I probed and found sound:**
- The fenced-block reader starts after the front matter, takes the first block, and raises an error if the block is never closed.
- `template()`, `template_record()` and `record_text()` apply the same placeholder table, so the parsed record and the "as written" text match.
- The id-grammar case still refuses an invalid id, and accepts it once the shared grammars are loosened, using the checkpoint with `task` filled.

## Findings

**F1: the "gov derives it" check still reads the ticket template's own front matter, not its record block.**
- What was done: `test_no_template_stores_what_gov_derives` was left reading the template's front matter, while every other case moved to the record the template gives.
- What happens: if the ticket's ```yaml block gained a top-level `content_hash`, `canonical_path` or `path`, the case would still pass. It now inspects `name`, `version`, `role` and so on, not the record.
- What should happen: it should read the same record as the other cases, so it fails if the block stores a derived key. This is the README's reading 9: "No template stores `content_hash`, `canonical_path` or `path` at the top level".
- Ordinary work: no, because adding a top-level derived key to the ticket record block is not a plausible edit (`path` appears only nested, under `acceptance_tests`).
- Consequence: fails open (the test would miss that defect; today the block has none of those keys).
- Scope: in.
- Would reverse it: a ruling that reading 9 is about the template's own front matter, not the record shape.

**F2: the README's definitions no longer describe what the tests do.**
- What was done: the revision changed what counts as a template and where the record comes from, but not the README.
- What happens: reading 1 still says "A template is any file under `template/governance/kernel/templates/` with the same word in its name", which no longer excludes `role-*`/`brief-*`. Reading 2 still says "The frontmatter is what validates; the body is not checked". For the ticket, the body's ```yaml block, with placeholders filled, is now what validates.
- What should happen: both readings should state the exclusion, the block-else-front-matter rule and the placeholder fill.
- Ordinary work: yes, because the next designer or reviewer who reads the README gets the wrong definition.
- Consequence: other (documentation drift; no test result changes).
- Scope: in.
- Would reverse it: the README updated in another commit I did not look at.

**F3: "validates as it is written" now validates the filled text.**
- What was done: the case validates the record text after the placeholders are filled.
- What happens: a template whose literal text fails the schema now passes this case if the failing part is a placeholder. The checkpoint's `task: ''` is the one example today; an unquoted `<x: y>` would be another, since the fill would also repair YAML that doesn't parse.
- What should happen: this follows the 1.0.0 templates' own words, so it is acceptable. But the case no longer shows that a literal copy of a template is a valid record. Its docstring says so; its name does not.
- Ordinary work: no, because a writer fills placeholders as the template tells them, and no unquoted `<…: …>` exists today.
- Consequence: other.
- Scope: in.
- Would reverse it: a decision that templates must validate unfilled. That would make the checkpoint's `task: ''` a template defect rather than a placeholder.

Classification: 3 findings, all in scope. None is both ordinary work and fails open or loses work, so none blocks. F1 and F3 go in as rows; F2 can ride along with the next W1-08 change.

```verdict
{"kpis": [{"kpi": "w1-08-template-samples", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}]}
```
