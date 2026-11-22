# W2-81's test code: the fixes the proving run on 0.1.4 found (`DAEO-l78m`)

The proving run on 0.1.4 (`docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md`, "Class 2: test-code defects"; the
analysis's ids T1 to T6, and the CTO's T10 of 2026-11-20) found defects in this folder's own support code (the runner
`w2_81_run.py`, the judge `w2_81_judge.py`, the scorer `w2_81_score.py`, the stand-ins). They are fixes under the
closed ticket, no new ticket: each has red tests first (a commit of its own, run on the base through the heavy slot),
then the change to the support module that turns them green. The cases are mapped to the ticket's KPI lines in the
README's table "Fix: W2-81's test code, six defects". A **guard** is a case that is green on the base by design.

## The fixes

- **T1, `gov queue` runs with the operator's `HOME`.** `gov adopt` and `gov retrieve` run in the run's scrubbed
  environment (`HOME` is `<folder>/.home`, so retrieval reads nothing of the operator's); the landing's `gov queue` is
  given the operator's own `HOME` (the runner process's), every other variable as the run's, because the repository's
  tests need the tools in the operator's user site (pytest). The model sessions never had the scrubbed `HOME`: the
  product's `run_claude` inherits the runner's own environment; the case holds that the runner leaves its `HOME` alone.
- **T10, every session the run launches carries the starter's address.** `--notify <address>`, else the runner's own
  `$GOV_MSG_ADDRESS`, is set as `GOV_MSG_ADDRESS` in the environment of `gov adopt`, `gov retrieve` and `gov queue`
  and, for the run's duration, in the runner's own process (the reader's and grader's sessions are started by the
  product's `run_claude`, which inherits it); restored when the run ends, also after an error. With neither, nothing is
  set (the product's launcher then defaults the address to the live CTO's inbox, which is the defect: give one).
- **T6, the report's ranks.** Each `per_question` row holds `bundle` (every item the retrieval gave, `[path, start,
  end]` in rank order; `null` when it gave none, `[]` when it answered nothing), `forbidden_rank` and `gold_rank` (the
  1-based rank of the first item whose path is a forbidden source, or a gold source; `null` when none), beside
  `first_gold_rank` (by line). Paths, line numbers and ranks only: no question, answer, gold or item text, in the
  hidden rows too.
- **T2, stage AS.** The judge's stage list is A0, A1, A2, AS, A3 ... (`BUILT_STAGES` stays the stages
  `project.record_path` names); AS is in the capability table (CAP-44.m, built); its record is
  `governance/adoption/AS-spec-audit.md` (`gov.adopt.spec_audit.RECORD`). Absent, no front matter, front matter that is
  not a mapping, or bad YAML is `stage AS is ABSENT` or `UNREADABLE` in the reasons (the judge's own words for a built
  stage; `MISSED` is the planted problems' word), the run NOT_READY. The stand-in adoption writes an AS record.
- **T3, an owner's exceptions.** Every reason `overall` gives has a stable id `<repository>:<CODE>:<subject>` in
  `reason_ids`, in step with the unchanged `reasons`: PLANTED (the planted problem's id; a hidden variant by its
  number and id), CONTROL (the control's id), STAGE (the stage's name, `findings` included), FIGURE (`end_to_end`),
  NOTJUDGED (`-`). `overall(judgements, figures, expected, exceptions=None)` reads an owner's exceptions: a mapping, or
  the path of a JSON or YAML file, `{"decision": "DEC-<n>", "reasons": ["<reason id>", ...]}`. With none the result is
  as before. A run without reasons is READY whatever the file says; a run whose every reason's id is named is
  **READY_WITH_EXCEPTIONS** (`judge.READY_WITH_EXCEPTIONS`; the command exits 0, as for READY); one reason not named
  stays NOT_READY. The result's `exceptions` holds the `decision`, the ids `named` (matched a reason), `unnamed`
  (reasons the file does not name) and `unused` (named, matching no reason: reported, never an error). A FOUND problem
  or PRESENT stage is no reason, so never named. `--exceptions <file>` passes the file on; the report names the decision
  and each id (`report.json`: `reason_ids`, in step with `reasons`, `null` for the runner's own; `exceptions`;
  `report.md`: "Exceptions named in DEC-n"). **The runner's own reasons are never excusable:** the landing not run or not
  exit 0, the hidden half absent, a `gov adopt` stage that ended with an exit other than 0. A file that cannot be read,
  is no mapping, has no `decision` of the form `DEC-<digits>`, whose `reasons` are not a list of non-empty strings, or
  that names an id twice is refused before any work: `refused: <file name>: <fault>`, exit 2.
- **T5, current text.** The comment of `CAPABILITIES` is dated 2026-11-20; the README's VERDICT row says no stage or
  command gives the lite verdict yet (CAP-44.h, W2) and that W2-52 built A7 and A10 only; the README's capability table
  has an AS row.

## The red runs, on the base

T1 1 failed; T10 6 failed and 1 passed (the guard "started with neither, nothing is set"; `SystemExit: 2` for the
unknown `--notify`); T6 9 failed (5 scorer ids, 4 runner ids: `KeyError: 'bundle'`); T2 11 failed (`KeyError: 'AS'`); T3
42 failed (an unknown `--exceptions`, `overall()` with no `exceptions`, no `reason_ids`, no `READY_WITH_EXCEPTIONS`);
T5 1 failed (the comment's date). After each support change the same cases and the files they live in were run green;
the whole folder is run once at the end.

## An existing case rewritten (one)

`test_w2_81_runner.py::test_the_report_log_and_output_hold_no_question_answer_or_secret_text` compared every gold answer
with `report.json`; with T6 the rows' `bundle` records a file's path, and a gold answer can be that path
(`pyproject.toml`), so it now leaves the rows' `bundle` out of `report.json` before that comparison. Every other
comparison (the markdown, the log, the command's output) is unchanged. The commit carries `Rewrite-Reason`.

## What the KPI wording left open, and what the cases hold

(T3) `overall` also takes the path of the file (the item's title says so); the result's `exceptions` also carries
`unnamed`; the command exits 0 for READY_WITH_EXCEPTIONS; the stage word is the judge's own, `ABSENT` or `UNREADABLE`,
not `MISSED`. (T6) `gold_rank` is by path ("likewise" the forbidden rank; the case
`test_the_gold_rank_is_by_the_gold_sources_path_where_the_first_gold_rank_is_by_its_line` holds it, and is the one to
drop if the CTO means by line), and an empty bundle is `[]` or `null` (the case accepts both).
