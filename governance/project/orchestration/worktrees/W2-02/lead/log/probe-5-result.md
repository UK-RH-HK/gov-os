task: Fresh read-only probe of DAEO-zflj (W2-02, profile STANDARD) at head `cbb7004c` on `w2/W2-02`, looking for behaviour the acceptance tests miss: lost work, writes outside scope, changed acceptance tests, or a guard or gate that fails open.
status: DONE — the probe is complete and the judgement is **pass**: no finding is both "yes" to ordinary work and "fails open" or "loses work"; there are 7 rows (R1 to R7).
work_completed: Passed Step 0 and the standing checks. Read the ticket, the W2-02 README, the `schema.py` diff, the five schemas the ticket touches, the close writer, and DEC-741, DEC-872 and DEC-874. Ran the three named suites, plus DEC-874's four cases by name. Recomputed both merge-backs with `git merge-tree`. Checked who committed each acceptance test and that every commit stays in the ticket's paths. Ran 50 core-schema probes in scratch projects built from scratch (close type, verdict, audit report, unmeasured types, shape-check edges) and checked the `wbs_id` grammar against 11 ids.
files_changed: none (my probe scripts lived only in this session's temp folder).
evidence: Step 0: (a) the write failed with "OSError: [Errno 30] Read-only file system", exit 1; (b) `git hash-object -w` gave `1ae28402…` and `git update-index --refresh` exited 0. GOV_ROLE=independent-auditor, GOV_TICKET=DAEO-zflj; top level `/home/usain/gov-os-worktrees/W2-02`, branch `w2/W2-02`, head `cbb7004cf3905627acf8be9d799358dd935c5cee`. `gov.__file__` = `/home/usain/gov-os-worktrees/W2-02/src/gov/__init__.py`. Core-schema on this worktree: exit=0, no findings. `666f56d1`: git's own merge of `2a35fd7b` and `c74a7d43` is `1ea387d7` with one conflict, and the only path where the commit differs from it is `src/gov/check/schema.py`, resolved to W2-02's blob `8953bb69` (the same blob as at HEAD). `dbea81c8`: tree `b217374d` equals `git merge-tree --write-tree 4ce16df2 6855cdf3` (exit 0). `git interpret-trailers` finds `Task: DAEO-zflj`, `Role: orchestrator` and `Implements: DEC-441` on both merges. The lead's run-5 logs: every suite exit 0 except W1-05, W1-19, W1-25 and W1-46 (each re-run alone under `after/` and passed) and W1-42 (2 failed, the same two as in the lead's run-3 and run-4 logs, both unrelated to the schema check).
tests: W2-02 acceptance: 53 passed (3.47 s). W2-54's `test_w2_54_audit_report.py` and `test_w2_54_green_here.py`: 28 passed in 754.51 s; the run passed the harness's 10-minute foreground limit, was moved to the background, and I read its result when it finished; the sandbox denied `ollama.com:443` during it. DEC-874's corrected cases by name: 6 passed (two acceptance cases, the second over both types, each on `[HEAD]` and `[4ce16df2]`), and the unit test `test_the_other_types_of_w2_02_stay_unknown` 2 passed. `tests/unit/check`: 130 passed (4.22 s). No suite was run with `-x`.
discoveries: (1) On a standalone schema, a top-level keyword the check cannot read (`if`/`then`, `additionalProperties`) is skipped, not refused; at every nested level the same keyword is a fault (R1). (2) A verdict record with no shared frontmatter passes when `common.schema.json` is missing (R2). (3) An empty conditions list makes a valid verdict (R3). (4) `src/gov/context/__init__.py` keeps a second copy of the `wbs_id` grammar without the DEC-730 suffix (R6). (5) `gov close` runs core-schema before a close only when the ticket's commits touch governance paths, so the new "unmeasured" refusal can stop a close only there (R7).
risks: (a) "Unmeasured, not green" now covers every mapped type. A project whose installed kernel is older than the gov package it runs, and lacks the schema file for a type it has records of, now turns red; a close touching governance files is then refused until `copier update` (R7). This fails closed and is KPI line 3's intent. (b) W1-42's two existing reds (the RETR-X-02 parent-expansion case and the governance-share case) must be judged by the close's red lists; they are not this ticket's. (c) This worktree's `git status` shows untracked sandbox placeholders: `.bash_profile`, `.bashrc`, `.gitconfig`, `.gitmodules`, `.idea`, `.mcp.json`, `.profile`, `.ripgreprc`, `.vscode`, `.zprofile`, `.zshrc` (empty read-only files) and `docs/source` (a character device). They are the sandbox's mount points, not my writes; a tripwire should conclude nothing from them.
lessons: W2-54's two files take about 13 minutes under this sandbox, more than the 10-minute foreground limit, so budget them separately. `gov retrieve` answers FACET_UNAVAILABLE here because the index is stale. The guard refuses a Bash write whose target is a shell variable as "guard-unresolvable". Checking a merge-back against git's own merge takes two commands: `git merge-tree --write-tree` on its parents, then `git diff --name-status` of that tree against the merge commit.
proposed_decisions: none. Classification (DEC-809): 0 findings fail the probe; 7 rows. No round is proposed.
unresolved: R1, R2, R4 and R5 are rows for the Wave 3 hardening pass or W2-64's full validator. R3 goes to W2-52's or W2-28's agreement rule. R6 is outside W2-02's paths and goes to whichever ticket owns `src/gov/context/`. One check was refused and not retried (refusal 2): running `w2/integrate`'s own `schema.py` on the real close record. What it would have shown (integrate judges `type: close` an unknown type) is already shown by W2-54's passing `[close-…]` cases and by DEC-872's basis.
recommended_next_action: The lead commits this probe record under `docs/probes/DAEO-zflj/` with judgement pass, and returns W2-02 to the orchestrator for its merge and the close queue (DEC-874 item 3).

---

**Head probed:** `cbb7004cf3905627acf8be9d799358dd935c5cee` (`w2/W2-02`, run 5, after the merge-back `dbea81c8`).

**Refusals: 2.**
1. A read refusal (DEC-849): a recursive search for `check-jsonschema` starting at the repository root. The guard answered "the call reads the settings file or the held-out file". I took the refusal and searched named places instead (`lefthook.yml`, `template/`, `src/gov/check/`); none uses check-jsonschema.
2. A write refusal: a Bash command that wrote `w2/integrate`'s `schema.py` into my temp folder through a shell-variable redirect and `mktemp`. The guard answered "Bash write to '/<guard-unresolvable>' denied". I did not retry it.

**`gov retrieve`:** used once, to ask what DEC-741 says about the verdict's conditions. It gave FACET_UNAVAILABLE (lexical and semantic both "stale"), so I read DEC-741, DEC-872 and DEC-874 by name in `docs/DECISION_REGISTER.md`.

**Code graph:** no code-graph tool is available in this session, so I used Grep and Read on named folders.

**Session id:** `f5a53e74-8d76-4f77-8621-04a6d53a9cd2`, read from this session's temp-folder path.

### Findings (all rows; none fails the probe)

- **R1: on a standalone schema, top-level keywords the check cannot read are skipped, not refused.**
  - What was done: in a scratch project I swapped the kernel's verdict schema for a copy with a top-level `if`/`then`, and separately one with `additionalProperties: false`, then checked records that break each.
  - What happened: core-schema was green both times.
  - What should have happened: the module's own rule is that a shape it cannot read is a fault, never a pass, at every depth; nested shapes already follow it.
  - Today: no kernel schema has such a keyword. The three standalone schemas use only `$schema`, `title`, `description`, `type`, `allOf`, `required`, `properties` and `$defs`.
  - Severity: low.
  - Ordinary work: no, because it needs a later edit of a standalone schema that adds a top-level keyword; none exists today, and the ticket that adds one would be held by its own acceptance tests.
  - Consequence: fails open (only for such a future schema).
- **R2: a verdict record with no shared frontmatter passes when `common.schema.json` is missing.**
  - What was done: a project with every kernel schema except `common.schema.json`, and a verdict record with no `id`, `status` or `state_class`, all conditions `met`.
  - What happened: green, exit 0.
  - What should have happened: the three missing fields, or "unmeasured", because the schema takes in the shared frontmatter through `allOf` and that file cannot be read. With `common.schema.json` present, the same record gets three missing-field findings, which is correct.
  - Severity: low.
  - Ordinary work: no, because Copier installs the whole schema folder and every record schema refers to `common.schema.json`; it takes a broken or hand-trimmed kernel.
  - Consequence: fails open (for that broken kernel only).
- **R3: an empty conditions list is a valid verdict.**
  - What was done: an `ADOPTED_HEALTHY` record with an empty `conditions` list.
  - What happened: green.
  - What should have happened: DEC-741 I (ii) asks for a list of named conditions but sets no minimum, so the schema's reading can be defended. Whether a verdict agrees with its conditions (DEC-741 G (i) names three lite healthy conditions) belongs to W2-52 and W2-28.
  - Severity: low.
  - Ordinary work: yes, because an agent might write an empty list as a placeholder.
  - Consequence: other (no guard opens and nothing is lost).
- **R4: fields shared with every record are checked for presence only, not shape (W2-64's residual, DEC-872 item 2).**
  - What was done: a verdict record with `state_class` set to an unknown word; a close record whose `task` is a list.
  - What happened: both green.
  - What should have happened: refusals, once the full validator reads every keyword.
  - Severity: low.
  - Ordinary work: no, because `gov close` has always written `task` as the ticket id and `state_class: AUTHORITATIVE` (since W1-30, `f22b5a27` and `01c19515`), and no tool writes verdict records yet; a wrong shape takes a hand edit.
  - Consequence: other.
- **R5: a pattern accepts a trailing newline.**
  - What was done: an owner entry written as a YAML block scalar (`DEC-741` plus a newline), and the `wbs_id` pattern applied to `W2-15a` plus a newline.
  - What happened: both accepted. Python's end-of-text anchor also matches before a final newline; the anchor of JSON Schema's own regex dialect does not.
  - What should have happened: refused. This predates the ticket and now reaches the nested checks too.
  - Severity: low.
  - Ordinary work: no, because ids are written as plain values, never as block scalars.
  - Consequence: other.
- **R6: a second copy of the `wbs_id` grammar in `src/gov/context/__init__.py` lacks the DEC-730 suffix.**
  - What happens: that module refuses an external reference whose id has the shape of a held id, but its work-breakdown form takes no letter suffix. An external reference with the id `W2-15a` would therefore not be refused.
  - This file is outside W2-02's paths. The one definition in `common.schema.json` is correct.
  - Severity: low.
  - Ordinary work: no, because it needs an entry in the external-references file whose id looks like a suffixed work-breakdown id.
  - Consequence: other.
- **R7: "unmeasured" now applies to every mapped type, not only standalone ones.**
  - What happens: a project whose installed kernel lacks the schema file for a type it has records of turns red where it was silently green. A close whose commits touch governance files is then refused until `copier update`.
  - For close records nothing changes: on such a kernel they were already an unknown type (red) before this ticket. In this repository no close is refused, since core-schema is green here.
  - Severity: informational.
  - Ordinary work: yes, because a project can run a newer gov package than its installed kernel between updates.
  - Consequence: other (it fails closed, the finding names the missing schema file, and nothing is lost).

### Probed and found sound

- **The close type.**
  - The real `CL-DAEO-7rr2.md` passes unchanged.
  - Close records for ticket ids with an upper-case, lower-case or digit prefix all pass.
  - A record missing `task`, `state_class`, or `id` and `status` is refused, naming each field.
  - `Close` and `frobnicate` are refused as unknown types.
  - With no close schema in either layout, the record is reported unmeasured; with the schema only in the installed layout, it is measured and green.
  - `gov close` has written `task` and `state_class` since W1-30, and `CL-DAEO-7rr2.md` is the only close record on any branch.
  - None of the keys the writer merges in can overwrite `id`, `type`, `status`, `state_class` or `task`.
  - So no ordinary close is refused by its own pre-close check at this head. On `w2/integrate` today, closes after W2-53 wait for this merge (DEC-872).
- **The `STANDALONE_TYPES` resolution keeps W2-54's behaviour.**
  - A record in `docs/audit/` with no `type` is an audit report and passes.
  - Missing `milestone` and `pack_sha256` are each named.
  - With no audit-report schema, the report is unmeasured.
  - A record with no `type` outside `docs/audit/`, or with a `type` that is a list, gets SCHEMA_INVALID_TYPE.
  - W2-54's cases pass, including DEC-874's four.
- **Both merge-backs.**
  - The run-4 resolution kept every line W2-54 added: its type-map line, its standalone type, the audit-folder constants and the in-folder default type.
  - Every line the resolution removed from W2-54's file is replaced by a W2-02 version that keeps its meaning.
  - Run 5's merge is exactly git's own merge. Neither merge used `-s ours` or dropped a side.
- **Acceptance tests and paths.**
  - Only W2-02's suite and W1-26's one test differ from `w2/integrate`, whether compared from the merge base or against its current tip `4690e9d1`.
  - All three acceptance commits are by the independent test designer, and both revisions carry `Rewrite-Reason:`. W1-26's change is the one assertion, made stricter.
  - The implementer's commits stay inside `allowed_paths`, the ticket file is unchanged on the branch, and `test_check.py` changed only in `test_schema_clean_record`, made stricter.
  - Nothing of the guard is touched.
- **The KPI lines.**
  - Core-schema is green here.
  - A type with no schema file, an empty `{}` schema file, or a file that is not JSON each give "unmeasured", not green.
  - `W2-15a`, `W2-15` and `W10-123z` are accepted. `W2-15ab`, `W2-15A`, `W2-1`, `W2-1a`, `w2-15a`, a trailing space and `W2-` are refused.
  - The ticket schema takes its `wbs_id` from the common definition.
  - The decision entry has `id` (a decision id), `status`, `owner`, `date` and `span`.
  - The audit report requires `milestone`, `commit` and `pack_sha256`.
  - The verdict's three values and its conditions hold:
    - a mapping or a plain string where the list or a condition belongs is refused;
    - an empty name, a number as the source, or an unquoted `no` (read as a boolean) as the state is refused;
    - an `accepted` condition without a DEC or ADR owner entry is refused, including when it is the second condition.
  - Every refusal names the field and its place.
- **Robustness of the shape check.** A list-valued `type` or a non-mapping item shape now fails closed as "cannot measure"; the old code would have crashed on a list-valued `type`.

### Judgement: pass

R1 and R2 fail open only for a future schema or a broken kernel ("no" to ordinary work). R3 and R7 are "yes" to ordinary work but fail closed or neither. R4, R5 and R6 are "no" with consequence other.

---

**Probe record payload** (for `docs/probes/DAEO-zflj/`; the lead fills in `implementer_session`, since the implementer's commits carry no session trailer):

```markdown
---
type: probe
task: DAEO-zflj
reviewer_session: f5a53e74-8d76-4f77-8621-04a6d53a9cd2
implementer_session: <lead: the product-spec session of 81eac9a7, f2776ce2 and 5aff5f6d>
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: cbb7004cf3905627acf8be9d799358dd935c5cee
---

# Probe record: W2-02 (DAEO-zflj), run 5 (DEC-872, DEC-874)

## What was probed

- **Head:** `cbb7004c` on `w2/W2-02`: run 5's merge-back `dbea81c8` of `w2/integrate` (`6855cdf3`) and the lead's checkpoint.
- **Reviewer:** a fresh read-only reviewer (role `independent-auditor`, session `f5a53e74-8d76-4f77-8621-04a6d53a9cd2`, 2026-10-21) under its OS sandbox. It wrote nothing in the repository.
- **Step 0:** (a) the write outside the worktree failed (read-only file system); (b) `git hash-object -w` and `git update-index --refresh` worked. `gov.__file__` was this worktree's `src/gov/__init__.py`.
- **Retrieval:** `gov retrieve` gave FACET_UNAVAILABLE (stale), so the register was read by name.
- **Refusals:** one read (a search from the repository root) and one write (a Bash redirect whose target the guard could not resolve); neither was retried.
- **Suites:** W2-02 acceptance 53 passed. W2-54's audit-report and green-here files 28 passed, with DEC-874's four corrected cases passing on `[HEAD]` and `[4ce16df2]`. `tests/unit/check` 130 passed.
- **Areas:**
  - the close type against the real `CL-DAEO-7rr2.md` and the writer in `src/gov/close/command.py`;
  - the `STANDALONE_TYPES` resolution and W2-54's audit-report behaviour;
  - both merge-backs against git's own merges (`666f56d1`, `dbea81c8`), and their trailers;
  - who wrote the acceptance tests, and the ticket's paths;
  - the KPI lines.
- **Own probes:** 50 core-schema probes in projects built from scratch, plus the `wbs_id` grammar against 11 ids.

## What was found

Classification: 0 findings fail the probe (yes + fails open or loses work); 7 rows.

- **Sound:**
  - Core-schema is green on this repository, so no ordinary close is refused by its pre-close check.
  - Every close record `gov close` writes passes, including for lower-case and digit ticket prefixes. A close record missing `task`, `state_class`, `id` or `status` is refused, naming the field; an unknown type is SCHEMA_UNKNOWN_TYPE; a type with no schema file is unmeasured, not green.
  - W2-54's audit-report behaviour is kept.
  - `666f56d1` differs from git's merge only in `src/gov/check/schema.py`, resolved to W2-02's side, which holds every line W2-54 added. `dbea81c8`'s tree is exactly git's merge. Both carry `Task: DAEO-zflj`, `Role: orchestrator` and `Implements: DEC-441`; neither used `-s ours`.
  - Only W2-02's suite and W1-26's one test (DEC-746) differ under `tests/acceptance/`, all by the independent test designer.
  - The `wbs_id` grammar accepts `W2-15a` and `W2-15` and refuses `W2-15ab`, `W2-15A` and `W2-1`.
  - The verdict's three values and named conditions are enforced, an `accepted` condition needing its DEC or ADR owner entry.
- **R1: on a standalone schema, top-level keywords the check cannot read (`if`/`then`, `additionalProperties`) are skipped, not refused.** No kernel schema has one today.
  - Ordinary work: no, because it needs a future schema edit, which that ticket's own acceptance tests would hold.
  - Consequence: fails open (for such a future schema only).
- **R2: a verdict record with no shared frontmatter passes when `common.schema.json` is missing.**
  - Ordinary work: no, because Copier installs the whole schema folder; it takes a broken kernel.
  - Consequence: fails open (for that broken kernel only).
- **R3: an empty conditions list makes a valid verdict.** DEC-741 sets no minimum; agreement with the verdict belongs to W2-52 and W2-28.
  - Ordinary work: yes, because an agent might write an empty placeholder list.
  - Consequence: other.
- **R4: the shared fields, and non-standalone types such as `close`, are checked for presence only, not shape.** This is W2-64's full validator (DEC-872 item 2).
  - Ordinary work: no, because `gov close` always writes these fields in their right shape; a wrong one takes a hand edit.
  - Consequence: other.
- **R5: patterns accept a value with a trailing newline** (Python's end-of-text anchor), now in the nested checks too.
  - Ordinary work: no, because ids are not written as block scalars.
  - Consequence: other.
- **R6: `src/gov/context/__init__.py` keeps a work-breakdown form without the DEC-730 suffix,** so an external reference with the id `W2-15a` is not refused as a held id. Outside W2-02's paths.
  - Ordinary work: no, because it needs such an id in the external-references file.
  - Consequence: other.
- **R7: "unmeasured, not green" now applies to every mapped type,** so a project whose installed kernel lacks a schema file for a type it has records of is refused at a close that touches governance files, until `copier update`. For close records nothing changes: they were an unknown type there before.
  - Ordinary work: yes, because a project can run a newer gov package than its installed kernel.
  - Consequence: other (fails closed, naming the missing file; nothing lost).

## Judgement

Pass. No finding is both ordinary work and fails open or loses work. R1, R2, R4 and R5 go to the Wave 3 hardening pass or W2-64; R3 to W2-52 and W2-28's agreement rule; R6 to the ticket that owns `src/gov/context/`; R7 is KPI line 3's intended fail-closed behaviour.
```