task: DAEO-wi46 (W2-98), independent probe of head 384c92b8b429
status: done. Verdict FAIL: two findings are in scope, an honest agent can hit them in ordinary work, and both fail open.
work_completed: I ran Step 0, read the ticket, the diff, SKILL.md, spec-form.md, check_spec.py, imports.yaml, the skill template, the qa-review sibling and the suite's support module and case names. I ran the validator, the `diff -r` of both copies and the adapter check. I probed about 140 inputs against the KPI parser, the code-name detector, the Test data table, the whole spec check and the imports check. I ran the suite once through heavy_slot.
files_changed: none. `git status --porcelain` was empty at the start and at the end.
evidence: Each finding below has its reproduction text. I called the check's functions on text held in memory. `check_spec()` was given a stand-in file object, which is the same function `main` calls. This is because I could not write probe files (see unresolved).
tests: 2 failed, 92 passed in 7.24s. The two red cases are the expected ones: test_the_claude_copy_matches_the_kernel_source and test_the_adapter_check_finds_no_generated_drift_in_the_real_skill, both because `.claude/skills/spec-writing` is absent.
discoveries: heavy_slot refuses a per-run `--basetemp` (DEC-898, DEC-907 item 2). The brief's fallback of adding `--basetemp` therefore exits 4; running without it works. heavy_slot also prints `rm: cannot remove '/tmp/gov-os-heavy-prio-*': Read-only file system` in a sandboxed session; the run is not harmed. DEC-959 item 8 names "licences, privacy, no secrets"; the check enforces neither privacy nor secrets (F2).
risks: As built, a spec can print PASS while one of its KPIs names code or has no failure line (F1). It can also print PASS when a data source has no real owner, or when its privacy and secrets are not stated (F2).
lessons: The check judges only lines it recognises as KPIs. Any other text under `## KPIs` is never judged, so a small slip in a KPI's id line hides the whole KPI from the check.
proposed_decisions: none. One question for the lead: F6 (should a measuring source with hidden half `no` pass?) could become a recorded row.
unresolved: The Write tool was refused twice: first for `$TMPDIR/probe.py`, then for `$TMPDIR/aud/probe_min.py`; both were permission prompts in a non-interactive session. Following the two-refusal rule I stopped using it and did not write the files through Bash instead. I probed in memory, so nothing was planted on disk and the P1 package file was not written by my probes; the suite's own cases cover that file.
recommended_next_action: The implementer fixes F1 and F2, in one fix batch with the I2/I3 binding words unchanged. A narrow independent check then re-runs F1's and F2's reproductions. F3 to F6 land as recorded rows.

```verdict
verdict: FAIL
head: 384c92b8b429
findings: 6 (failing: F1, F2)
```

Classification: 2 findings block (in scope, ordinary work, fail open: F1, F2); 4 are recorded rows (F3 and F5 other; F4 ordinary work no; F6 other). Recommendation: one fix batch for F1 and F2, then a narrow check, with no second full round.

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": []},
 {"kpi": "S2", "verdict": "fail", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S3", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S4", "verdict": "pass", "findings": [{"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S5", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S6", "verdict": "pass", "findings": []},
 {"kpi": "F1", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]},
 {"kpi": "F2", "verdict": "fail", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]},
 {"kpi": "F3", "verdict": "pass", "findings": []},
 {"kpi": "F4", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "F5", "verdict": "pass", "findings": []}
]}
```
S6 passes on what this branch can deliver: both `.rulesync` copies are byte-identical to the kernel source, and the `.claude` copy waits for the copies ACT, as the brief states.

## Findings

**F1: A KPI whose id line is slightly off the form is never judged, and the spec passes** (check_spec.py:29, :80-84; decisions DEC-959 item 8, DEC-1156 (5))
- **What happens:** The KPIs section has one KPI in the exact form (`- K1: …` with a `Fails if:` line) and a second KPI written with a small slip. The check prints `PASS` and exits 0, even though the second KPI names code and has no failure line. Any line under `## KPIs` that is not a `- K<n>:` line, a `Fails if:` line or an indented continuation is dropped without being judged. If no line is in form, the check correctly refuses with "no K<n> line"; the hole needs at least one KPI in form.
- **Reproduction:** each of these second lines, after a clean K1, gives `PASS`, exit 0:
  - `- K2 : The send_welcome() call returns.` (a stray space before the colon)
  - ``2. K2: The `send_welcome` call returns.`` (a numbered item)
  - `- K2a: The api.create path returns.`
  - `- K3 (new): The send_welcome step runs.`
  - `- **K2** — send_welcome() runs.`
  - a KPI wrapped to column 0: `- K1: A member sees the page after` / `send_welcome() runs.` / `  Fails if: no page.` The second line is a valid Markdown lazy continuation but is not judged.
- **Should happen:** every non-blank line under `## KPIs` is either part of a KPI the check judges or refused, naming the line, e.g. `REFUSED KPIs: a line is not in the K<n> form: "<line>"`. A column-0 line directly after a KPI is either judged with that KPI or refused; it is never dropped silently.
- Ordinary work: yes, because a stray space, a numbered item, an id suffix or an unindented wrap are ordinary slips when typing a list by hand.
- Consequence: fails open. A KPI that names code, or has no failure line, is passed; that is exactly F1's failure line and S3's first Done-when item.
- **What would reverse it:** an owner or lead ruling that I2's form makes any line outside `- K<n>:` "not a KPI", so the writer alone owns the slip. Or a case showing these inputs are refused at the head.

**F2: Test data cells that state nothing pass** (check_spec.py:127-140; decisions DEC-959 item 8)
- **What happens:**
  - An empty `privacy` cell and an empty `secrets` cell pass. DEC-959 item 8 requires the spec to state how the data is secured: "licences, privacy, no secrets". spec-form.md asks for "what personal data it holds, or `none`" and "whether it holds secrets". The check refuses an empty `hidden half` cell but not these two.
  - The `owner`, `source` and `licence or recipe` cells are refused only when blank. A placeholder that means "no owner" passes: `-`, `—`, `TBD`, `unknown`, or `n/a` for an imported row's licence.
- **Reproduction:** each passes `check_data` with no refusal, and the whole spec check prints `PASS`, exit 0:
  - `| repos | imported | Priya | MIT | | | yes | yes |`
  - `| repos | imported | TBD | MIT | none | none | yes | yes |`, and the same row with owner `—`, `-` or `unknown`
  - `| repos | imported | Priya | n/a | none | none | yes | yes |`
- **Should happen:** an empty privacy or secrets cell is refused, naming the source and the column. An owner, source or licence cell holding only a placeholder (`-`, `—`, `TBD`, `TODO`, `unknown`, `?`, and `n/a` for owner, source or an imported row's licence) is refused like an empty one, e.g. `REFUSED Test data: repos has no owner`.
- Ordinary work: yes, because leaving a cell blank or writing `—` or `TBD` for "not known yet" is ordinary table-writing.
- Consequence: fails open. A spec whose data has no real owner, or does not state privacy or secrets, is passed (S2, F2, S3's second Done-when item).
- **What would reverse it:** a ruling that I2 binds only non-empty cells, so placeholders are the reviewer's to catch, and that privacy and secrets are free text the check need not enforce (S2's verify line names only source, owner, licence or recipe, and hidden half). That would make F2 a recorded row.

**F3: Ordinary Markdown is refused** (check_spec.py:26-30)
- **What happens:**
  - `**Fails if:** …` gives "has no Fails if: line".
  - `_Fails if:_ …` gives a snake_case refusal plus "has no Fails if: line".
  - `Fails if:` with its text on the next indented line gives "has no Fails if: line".
  - Underscore emphasis `_quickly_` / `__all__` is taken as a snake_case identifier.
  - Several plain-prose words are taken as code: `example.com` and `dana@example.com` as dotted identifiers, `Node.js` as a path, `Member(s)` as a call, and `loads.Then` (a missing space after a full stop) as dotted.
  - The common prose cases are sound (none refused): `e.g.`, `i.e.`, `vs.`, `Dr.`, `U.S.A.`, `1.5`, `99.9%`, `9.30`, `3:1`, hyphenated words, `a (b)`, `yes/no`, dates and `Fig.2`.
- **Should happen:** bold or italic `Fails if:` labels and Markdown emphasis are accepted. A `Fails if:` with its text on the next line is accepted. A domain or email address is either accepted or refused with a reason that says what to reword.
- Ordinary work: yes. Consequence: other (it fails closed; the writer has to reword).
- **What would reverse it:** a ruling that I3's literal words (`name(`, dotted) cover these forms on purpose.

**F4: The imports check reads records loosely** (check_spec.py:186-195, :212; decisions DEC-1084)
- **What happens:**
  - Two records for the same part, one GPL-3.0 and one MIT, give `PASS`; any allowed licence wins.
  - A record under another top-level key (e.g. `other:` holding part and licence) is counted as a record, even though only `imports:` holds them.
  - Flow-style `- {part: x, licence: MIT}` and the `license:` spelling are refused as "no licence record"; this fails closed.
- **Sound:**
  - No record file, `imports: []`, or a forbidden licence each give a refusal naming the part.
  - Lowercase `mit`, quoted values, keys in another order, marker spacing, a marker split over lines, and `Apache 2.0` (refused) all behave correctly.
- **Should happen:** records are read only from `imports:`, and a part with more than one record is refused unless every record's licence is allowed.
- Ordinary work: no, because it needs conflicting duplicate records or a second list carrying part and licence keys.
- Consequence: fails open (a Wave 3 row).

**F5: The front matter lacks the template's `output:` key** (SKILL.md:1-7)
- **What happens:** the template closes the front matter to four keys plus `metadata.version`: `name`, `version`, `description` and `output`. The skill has no `output:` key.
- S4 names only name, version and description. The validator exits 0, and qa-review also lacks the key.
- **Should happen:** add `output: <the project's spec path>` or `output: none`, or record that the template's `output` key is optional.
- Ordinary work: yes. Consequence: other.

**F6: A measuring source with hidden half `no` passes** (check_spec.py:133; spec-form.md:61)
- **What happens:** S2 says the data is secured with "a hidden half where it measures". The form, and the check, accept `no` ("it measures and none is held apart") as passing.
- **Should happen:** the lead decides whether `no` on a measuring row should give a P1 (it is not secured) or stand as a visible statement. DEC-959 item 8 does not name the hidden half.
- Ordinary work: yes. Consequence: other, because the form allows it and it is visible to every reader.

## Probed and found sound
- PASS is never printed beside a REFUSED or P1 line.
- A P1 line is printed and exit 2 returned for `secured: no` (any case). An unclear `secured` value (`no.`, `partly`, empty, `**yes**`) is refused, never skipped.
- A missing part is named once. `## Non-goals` does not count as `## Goals`. An empty heading counts as missing. A second `## KPIs` section is still judged.
- A missing column, a header with no rows, prose with no table, and a short row are each refused.
- A KPI with no failure line, or an empty one, is refused with its id. Bold ids (`**K1**:`, `**K1:**`) and indented continuation lines are judged.
- Snake_case, call, dotted and listed-extension paths are refused. `signup.go` and `lib.rs` are refused, as dotted identifiers.
- The code does not special-case the planted text; I read check_spec.py whole.
- SKILL.md:
  - Sections are in the template's order, with Sources last.
  - Steps are a checklist naming all nine parts, the check and imports. Done when has five yes/no checkbox items.
  - It has the twelve fields and the P3/P2/P1/Emergency escalation. The body is 98 lines, and spec-form.md sits one level down with no further link.

## Step 0
- (a) `OSError: [Errno 30] Read-only file system: '/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-wi46'`, exit 1. It failed, as required.
- (b) HEAD `384c92b8b4294b03c36ead512796c51400a23bcf`. GOV_ROLE `independent-auditor`, GOV_TICKET `DAEO-wi46`.
- gov.__file__ = `/home/usain/gov-os-worktrees/W2-98/src/gov/__init__.py`

## Validator and adapter
- `gov.check.skill_validator …/spec-writing/SKILL.md` printed `{"findings": []}`, exit 0.
- `diff -r` of the kernel folder against `.rulesync/skills/spec-writing`: exit 0. Against `template/.rulesync/skills/spec-writing`: exit 0.
- `gov.adapters.portability` exits 1 with exactly four findings, all `GENERATED_DIFFERS`, for `.claude/skills/spec-writing/{SKILL.md, check_spec.py, imports.yaml, spec-form.md}`. It also reported `compared: rulesync_version true, kernel_files 40, generated_files 55`. This is the expected state until the copies ACT runs.
