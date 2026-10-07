# W1-40 acceptance tests: lefthook hooks and the CI workflow

Ticket `DAEO-fdkq`, profile STANDARD (DEC-221). Written by the Independent Test Designer (MR-3): 48 cases before
implementation, brought to DEC-489 in a second session (one case changed, 13 added). 61 cases in 7 files.

```
env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-40 -q -p no:cacheprovider -rs
```

## How the tests run

- **The hooks, as lefthook runs them.** The repository's `lefthook.yml` (one named file) is put into a temporary
  repository built with `git init`. `lefthook install` runs there and nowhere else. The tests then use plain
  `git commit` and `git push origin main`; the remote is a bare repository in the same temporary folder
  (DEC-465: nothing leaves the machine).
- **The workflow, as text and as its commands.** `w1_40_support.Runner` does offline what the hosted runner does
  with a push: a new repository, `origin` set, one fetch of the pushed branch at the depth the
  `actions/checkout` step asks for (1 where it asks for none; no note and no other ref is fetched), then every
  `run:` step of every push workflow in order under `bash -e`. A `uses:` step is not run. A step that downloads
  something (`curl`, `wget`, `gh release`, `pip install`, `uv tool install`, `npm install`, `apt-get install`)
  is not run and is judged as text. The job is green when every step that ran exits 0. A step that fetches the
  notes ref from `origin` with `git fetch` is run: `origin` is the bare repository.
- **The evidence record, through git.** No case names the ref. `Project.records` asks the bare repository for
  every notes ref it holds other than git's default `refs/notes/commits`, and reads the note of a commit there
  with `git notes --ref <ref> show <commit>`.
- **A project that is green or red by construction.** The temporary project holds the template's
  `.gitleaks.toml` (DEC-288), one passing test under `tests/`, and three check declarations of its own, one per
  tier G1, G2 and G3 (the tier is a field of every declaration, DEC-186). Each check leaves a mark in a folder
  outside the project when it runs, and fails while a file there tells it to. No model is involved: "a failing
  G3 check" is the project's G3 check failing. A case can build the project with fewer tiers declared.
- **The machine.** PATH is one folder of the test plus `/usr/bin:/bin`. That folder holds `gov` (the console
  script an install of this worktree's `src/` would generate), `gitleaks` and `lefthook` (the registered
  binaries), each of which a case can withhold, and stand-ins named `ollama`, `hf`, `huggingface-cli` and
  `nvidia-smi` that leave a mark and fail. `openspec` and `rulesync` are on no PATH.
- **This repository is never the subject of a run.** Its `gov check` is red on a recorded baseline (DEC-467);
  no case expects it green, and no hook is installed in it (one guard case reads the hooks folder).

lefthook 2.1.15 and gitleaks 8.30.1 are needed by 43 cases (everything in `test_w1_40_pre_commit.py`,
`test_w1_40_pre_push.py`, `test_w1_40_ci_evidence.py` and `test_w1_40_evidence_record.py`, and the two hook
cases of `test_w1_40_tiers.py`). Where either is absent those cases skip with a named reason. Both ran inside
the designer's session.

## Red before implementation

Observed 2026-10-07, with `src/gov/ci/` (the pre-commit gate command) in the tree and the hook file, the
workflow and the template files absent: `12 failed, 1 passed, 48 errors`.

- 48 errors: a fixture stops at `lefthook.yml is absent from the repository root` (the 33 hook and CI cases of
  the first session, 6 evidence record cases, 2 text cases) or at `no workflow under .github/workflows/ runs on
  push` (7 text cases).
- 9 failures for an absent file: the four template cases, the carrier case, the two hook cases of
  `test_w1_40_tiers.py` and the two no-G3 cases of `test_w1_40_evidence_record.py` (`lefthook.yml is absent`).
- **3 failures for their own reason, in the tree:** the three `gov ci checks` cases of `test_w1_40_tiers.py`.
  The command as built runs the tiers that have a declaration and ends with exit 0
  (`gov ci checks G1 G2` with no G2 check declared; `gov ci checks G1 G22`; `gov ci checks G1 tier2`).
- 1 pass: `test_no_lefthook_hook_is_installed_in_this_repository`, a guard that is green before and after.

The other cases cannot be red for a reason of their own inside the tree: they go through the two files. The
designer ran a copy of the suite outside the tree against a throwaway stand-in (nothing of it is in the tree):

- a working one (git note under a ref of its own; a strict tier gate of its own): 56 of 61 green. The five
  others: the three `gov ci checks` cases (they run the tree's command, which the stand-in does not replace) and
  two that the stand-in folder cannot serve (it has no tool registry and is no git repository);
- the same with one flaw at a time. A tier without a declaration passed over at commit: the two hook cases of
  `test_w1_40_tiers.py` red. The no-G3 record written as "passed": the two no-G3 cases red. The note pushed to
  `origin` whatever the remote: `test_the_note_goes_to_the_remote_that_is_pushed_to` red. The note under git's
  default ref: the ref case red (and every case that needs a record). A CI step that asks only whether a note is
  there: the failed-record case and the copied-note case red. A CI step that prints nothing: the report case
  red. `test_the_ref_of_the_record_is_named_in_the_hook_file_and_in_the_workflow` was not shown red on its own.

## KPI lines and the covers id

| KPI line | Tests | Red reason today |
|---|---|---|
| **S1a** "pre-commit runs G1-G2" [CAP-39.a] | `test_w1_40_pre_commit.py`: clean commit runs G1 and G2; failing G1, failing G2 stop the commit (2); passes again; G3 does not run at commit; missing `gov` stops the commit. `test_w1_40_tiers.py`: a project with no G1 check, or no G2 check, cannot commit (2); `gov ci checks` refuses a named tier without a declaration and a name that is no tier (3) (DEC-489) | `lefthook.yml` absent; the three command cases: the command passes the tier over |
| **S1b** "pre-push runs G3 including model-dependent tests and writes an evidence record bound to the head commit" [CAP-39.a] | `test_w1_40_pre_push.py`: push runs G3; failing G3 stops the push; passes again; one push leaves the record CI asks for; the record follows the head commit; the push leaves the tree clean; missing `gov` or `lefthook` never ends with CI green (2). `test_w1_40_evidence_record.py`: one push leaves the note of the head commit on the remote under a ref of its own; the note holds the commit id and the G3 check that ran; the note goes to the remote that is pushed to; a project without a G3 check can push, its record says "no G3 check declared" and never states a pass (DEC-489) | `lefthook.yml` absent |
| **S2** "GitHub Actions runs the deterministic checks and fails when the evidence record is missing or for another commit; carrier chosen and documented" [CAP-39.a] | `test_w1_40_ci_evidence.py`: red with no record; red with the record of another commit; runs G1 and G2; red on a failing G1 or G2 (2); red on a gitleaks finding; red with `gitleaks` or `gov` missing (2); red on a failing test of the project. `test_w1_40_evidence_record.py`: red with the note of another commit copied onto the head commit; red with a record of a failed G3 run; the job reports "no G3 check declared"; the ref is named in the hook file and the workflow. `test_w1_40_workflow_text.py`: runs on every push; names gitleaks and `gov`; no result thrown away; pinned actions; no baseline or bypass; the carrier is documented in the hook file and in the workflow | no push workflow; `lefthook.yml` absent |
| **S3** "pre-commit also runs the second gitleaks scan, with the project's rules alone" (DEC-347, DEC-369) | `test_w1_40_pre_commit.py`: a staged secret stops the commit; a staged secret the built-in allowlist shelters stops it (2: alphabet run, `false`), each after showing that one scan with the project's file does not flag it; the sheltering words alone pass; a staged secret counts though the working copy is clean; missing `gitleaks` stops the commit | `lefthook.yml` absent |
| **F1** "CI downloads models or needs a GPU" | `test_w1_40_ci_evidence.py`: CI does not run the G3 check and calls no model tool; CI does not go red for a G3 check that would fail on the runner. `test_w1_40_workflow_text.py`: hosted Ubuntu runner; no model or GPU word outside comments; an installed tool is the registered release | no push workflow |
| **F2** "A push with a failing G3 check leaves CI green" | `test_w1_40_ci_evidence.py`: a push with a failing G3 check never leaves CI green; a failed attempt leaves nothing a later bypass can use; red with the record of another commit. `test_w1_40_evidence_record.py`: a record of a failed G3 run that reaches the remote fails CI. `test_w1_40_pre_push.py`: failing G3 stops the push | `lefthook.yml` absent |
| ticket paths `template/**` | `test_w1_40_templates.py` (4) | template files absent |

| Covers id | Tests |
|---|---|
| CAP-39.a (tiers G0 to G5; G1-G2 at commit, G3 at push, the deterministic tiers in CI) | all seven files; the tier split itself: `test_a_clean_commit_passes_and_runs_the_g1_and_g2_checks`, `test_the_g3_check_does_not_run_at_commit`, `test_a_push_runs_the_g3_check`, `test_ci_does_not_run_the_g3_check_and_calls_no_model_tool`, `test_ci_runs_the_g1_and_g2_checks`, `test_a_commit_is_refused_when_a_tier_the_hook_names_has_no_declared_check` |

## Files

| File | Cases | Needs lefthook and gitleaks |
|---|---|---|
| `test_w1_40_pre_commit.py` | 12 | yes |
| `test_w1_40_pre_push.py` | 8 | yes |
| `test_w1_40_ci_evidence.py` | 13 | yes |
| `test_w1_40_evidence_record.py` | 8 | yes |
| `test_w1_40_tiers.py` | 5 | 2 yes (the hook cases); 3 no (`gov` alone) |
| `test_w1_40_workflow_text.py` | 11 | no |
| `test_w1_40_templates.py` | 4 | no (jinja2) |

## A result is measured or it is refused (DEC-449, DEC-454)

- A missing tool is a failure: `gitleaks` or `gov` missing stops the commit; `gov` missing stops the push or
  leaves CI red; `gitleaks` or `gov` missing leaves CI red. This holds whether or not the workflow has a step
  that installs them (P-4): no case requires such a step.
- A named tier is run or the gate refuses: a tier of the pre-commit gate without a declared check, and a tier
  name that is no tier, refuse (DEC-489). G3 at push is the one exception, and it is recorded as "no G3 check
  declared", never as a pass.
- lefthook missing: the hook script that `lefthook install` generates prints "Can't find lefthook in PATH" and
  exits 0 (observed with 2.1.15). The hook file cannot change that. What holds the line is the record: the push
  goes through, the commit has no record, CI is red
  (`test_a_push_without_a_tool_the_hook_needs_never_ends_with_ci_green[lefthook]`). For a commit there is no
  such backstop before the push; that is residual R-3.
- An exit code is not dropped: failing G1 or G2 stops the commit and leaves CI red; a gitleaks finding stops the
  commit and leaves CI red; failing G3 stops the push; no `continue-on-error`, no `|| true`, no `set +e`, no
  `skip:` or `only:` in the hook file.
- No baseline inside the hooks or the job.

## The interface the cases fix

| What | Value | From |
|---|---|---|
| Hook file | `lefthook.yml` at the root, with `pre-commit` and `pre-push` | ticket paths; lefthook |
| Hooks work after `lefthook install` and plain `git commit` / `git push <remote> main` | no wrapper command, no second push | from a source (DEC-489: the hook writes the note and pushes it) |
| A check's tier | the `tier` field of its declaration under `template/governance/kernel/checks/` | a source (DEC-186, `gov.cli.checks`) |
| pre-commit runs the checks of tier G1 and G2 and not G3 | by the tier field | a source (KPI S1, DEC-075); how the tiers are selected stays as built (DEC-489, R-1) |
| pre-commit refuses where the project declares no G1 check, or no G2 check | the commit is stopped | from a source (DEC-489) |
| `gov ci checks <tier>...` | exit 0 for a declared tier alone; not 0 when one named tier has no declared check beside one that has; not 0 for `G22` or `tier2` beside a declared tier | the command line: assumed, as the tree has it today (`src/gov/ci/command.py`); the refusal: from a source (DEC-489). The exit code and the error code are not pinned |
| pre-push runs the declared checks of tier G3 | by the tier field | from a source (KPI S1, DEC-489) |
| A project with no G3 check can push | the push arrives | from a source (DEC-489) |
| A check command runs by `sh -c` with the caller's environment; exit 0 is green | | a source (DEC-285; observed) |
| pre-commit refuses a staged secret by the project's `.gitleaks.toml`, and one by its rules alone | staged content | a source (DEC-347, DEC-369) |
| The evidence record | a git note on the head commit, on the remote after the one push | from a source (DEC-489) |
| The ref of the note | any ref under `refs/notes/` other than `refs/notes/commits`; the push puts no `refs/notes/commits` on the remote | "a ref of its own": from a source (DEC-489); `refs/notes/` is git's own rule for notes. The name is not pinned |
| The remote the note is pushed to | the one named in `git push <remote> main` (a second bare repository named `mirror` in one case) | from the ticket's brief ("to the same remote"); DEC-489 says "pushed by the hook" |
| The note's text | holds the full commit id; holds the id of the G3 check that ran (`w1-40-g3`); does not hold "no G3 check declared" where a G3 check is declared | from a source (DEC-489: "the commit id, the result and the checks that ran"). No format is pinned; how the result is worded is not pinned |
| The note's text where no G3 check is declared | holds the commit id and the words `no G3 check declared` | from a source (DEC-489, "in those words") |
| ... and never states a pass | none of the words `pass`, `passed`, `passes`, `green`, `success`, `succeeded`, in any case | "never as a pass": from a source (DEC-489); the list of words: assumed |
| The ref is named in `lefthook.yml` and in a push workflow | the full ref or its name after `refs/notes/` appears in both texts | assumed reading of DEC-489 "the choice is documented in the hook file and the workflow": the ref is part of the choice, and the job must fetch it |
| Carrier documented | `lefthook.yml` and every push workflow each hold "evidence record" and "git note" (any case) | from a source (DEC-489); the two phrases: assumed |
| Workflow | at least one file under `.github/workflows/` with `push` in `on`, unfiltered | a source (DEC-075 "on every push") |
| Runner | `runs-on: ubuntu-<something>` | a source (DEC-087 "hosted runner") |
| The job has an `actions/checkout` step, pinned | | assumed: how a hosted job gets its tree |
| What the checkout brings | depth 1 unless `fetch-depth` says otherwise; no notes | assumed from the action's documented defaults; not verifiable offline |
| CI is green for a commit pushed through the hook, red without a record or with another commit's | the job fetches the ref itself and reads the note of the commit it builds | from a source (DEC-087, DEC-489) |
| CI is red where the note on the head commit was written for another commit, and where what a failed G3 run left is on the remote | | from a source (DEC-489: "a record for another commit ... fails CI"; KPI failure line 2) |
| CI prints `no G3 check declared` for a commit whose record says so | in the output of a `run:` step | from a source (DEC-489 "CI reports it"); the job's colour: not pinned (P-6) |
| CI runs G1 and G2, gitleaks and the project's tests; not G3 | | a source (DEC-087) |
| The project's tests run from a `tests/` folder holding one file | the temporary project has only `tests/test_ok.py` | assumed: a step that names a deeper folder is red here |
| A download step is recognised by its command and not run | list above | assumed: a step that both downloads and checks would not be run, and its check would not count |
| A download of a registered tool names its registered version; a binary download verifies a checksum | only if such a step exists | a source (DEC-083, tool registry); whether it may install at all: P-4 |
| Expressions the runner evaluates | `github.sha`, `github.ref`, `github.ref_name`, `github.workspace`, `github.event_name`; conditions `always()` only; no matrix, container or services | assumed: anything else fails the case with "cannot be run offline" |
| Template files | `template/lefthook.yml.jinja`, `template/.github/workflows/<name>.jinja` for each workflow; rendered by Jinja with no answer they equal this repository's files; `${{` survives rendering | from a source (DEC-489) |

Under `src/gov/ci/**` the cases name one thing: the command line `gov ci checks <tier>...`. No module, error
code or record format is named.

## Decision packages

### Decided by DEC-489

- **P-1 (what G3 runs).** The declared checks of tier G3; a model-dependent test belongs there when its ticket
  declares it as a check. A project with no G3 check can push; its record says "no G3 check declared".
- **P-2 (the record and its carrier).** A git note on the head commit under a ref of its own, written by the
  pre-push hook after G3 has run and pushed by the hook; CI fetches the ref and reads the note of the commit it
  builds. The note holds at least the commit id, the result and the checks that ran.
- **P-3 (a record changed after the fact).** Not detected in Wave 1: residual R-10, no case.
- **P-5 (the template files).** No Copier answers; they render to this repository's own files, GitHub's
  expressions escaped. The four template cases stand as written.

### P-4: may the workflow install registered tools on the hosted runner (open, the owner's)
- **Question.** The runner has no gitleaks, no lefthook, no rulesync and no `gov`. May the workflow install
  them, each at its registered version with its checksum (DEC-083, DEC-287)?
- **Why now.** Without gitleaks and `gov` the job cannot run what DEC-087 lists; a missing tool is a failure,
  so until this is decided the job is red on the hosted runner for every push.
- **Options.** (a) Yes, by the registry's release and checksum, in steps of their own. (b) Only gitleaks and
  the package itself; nothing else. (c) No install: the job runs only what the runner image has.
- **Impact.** (c) leaves CI without the secret scan and without `gov check`, and red. (a) adds the release
  checksums of the archives to the registry: it records the checksum of the installed binary, not of the
  downloaded archive.
- **Reversibility.** High. **Cost.** A few steps; one registry field per tool.
- **Recommendation.** (a) for gitleaks and the package now; rulesync when the adapter step arrives.
- **Confidence.** Medium. The cases hold only: a missing tool fails the job; a download of a registered tool,
  if there is one, names the registered version, and a binary download verifies a checksum.

### P-6: is the CI job green for a commit whose record says "no G3 check declared" (open)
- **Question.** DEC-489 says the push is not refused, the record says so "never as a pass", and "CI reports
  it". It does not say whether the job then ends green or red.
- **Why now.** The engineer has to write the step that reads the note, and it exits with one code or the other.
  This repository declares no G3 check today, so the answer is the colour of its own CI after the Wave 1 exit.
- **Options.** (a) Green, with the words in the job's output (and in the job summary). (b) Red until a G3
  check is declared. (c) Green only where the project states in a file that it has no G3 check on purpose.
- **Impact.** (a) a product without model-dependent tests has a usable CI; the weakness is that deleting the
  G3 declarations turns a failing gate into a reported one, visible only to someone who reads the output.
  (b) every product without a G3 check, and this repository, is red on every push, which hides other failures.
  (c) closes the weakness of (a) and needs a new field somewhere and its check.
- **Reversibility.** High: one exit code. **Cost.** (a) and (b) none; (c) a field, a check and their tests.
- **Recommendation.** (a) for Wave 1, with the weakness recorded; (c) on the Wave 2 list.
- **Confidence.** Medium. No case holds the colour: `test_ci_reports_that_no_g3_check_is_declared` holds the
  words only.

## Residuals

- **R-1. Tier selection stays as built** (DEC-489): the hook command calls the check runner's internals;
  `gov check` has no tier option. Unit tests hold the join. No acceptance case.
- **R-2. S0a-G-11 is not in the tree** (`docs/source` cannot be read). No case is derived from it.
- **R-3. A commit without lefthook on PATH passes** (the generated hook exits 0). Nothing before the push
  catches it; CI's own G1-G2 and gitleaks steps do afterwards.
- **R-4. `git commit --no-verify`, `git push --no-verify` and `LEFTHOOK=0`** bypass the hooks by design of git
  and lefthook. The record is what CI holds against a bypassed push; nothing holds against a bypassed commit
  until the push.
- **R-5. The adapter check (W1-38) is not merged.** No case; `rulesync` is on no PATH of the simulated runner,
  so a step that runs it is red here. The workflow leaves a named place for that step; no case reads the place.
- **R-6. The runner is a simulation.** `uses:` steps, the real checkout, the runner image and the network are
  not exercised; the first real run is the owner's first push. Whether GitHub accepts the pushed notes ref and
  the job's fetch of it is seen there for the first time.
- **R-7. DEC-087's other deterministic checks** (schemas, readiness, the decision checker, the ticket DAG,
  `openspec validate --strict`) are inside `gov check`, as W1-26 built it; no case names them separately.
  `openspec` is on no PATH here, and `gov check` reports it YELLOW, not red.
- **R-8. gitleaks' built-in rules stay sheltered by the built-in allowlist** (DEC-347's own residual).
- **R-9. A pre-push gate stricter than G3** (one that also runs G1-G2 or the tests) is allowed by every case
  but one: if such a gate writes the statuses of G1-G2 checks into the record of a project without a G3 check,
  a status word like `GREEN` there fails `test_a_project_without_a_g3_check_...never_says_passed`.
- **R-10. A record edited or written by hand is not detected in Wave 1** (DEC-489): a deliberate bypass, like
  skipping the hook. No case. A hash or signature is a Wave 2 item. The copied-note case is not this: it holds
  only that the note names the commit it was written for.
- **R-11. The second gitleaks scan stays strict** (DEC-489): it does not carry the project's path allowlist.
  In this repository it will refuse commits that touch the canary fixtures once the hooks are activated. No
  new case.
- **R-12. Whether `gov ci checks G1 G3` refuses where no G3 check is declared** is not held: DEC-489 excepts
  G3 "as above" (at push), and no hook names that pair.
- **R-13. The result of a passing record is not held by its wording**, only through CI being green for it and
  red for a failed one.

## Not done in this repository

No hook is installed here: the worktrees share one hooks folder, and `gov check` is red on the baseline. The
owner's step at the Wave 1 exit, from the main tree, after the baseline is empty (DEC-472):

```
~/.local/bin/lefthook install
```

From then on every push from that tree also pushes the notes ref of the evidence record to the same remote.
