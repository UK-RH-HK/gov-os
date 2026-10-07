# W1-40 acceptance tests: lefthook hooks and the CI workflow

Ticket `DAEO-fdkq`, profile STANDARD (DEC-221). Written by the Independent Test Designer (MR-3): 48 cases before
implementation, brought to DEC-489 in a second session (one case changed, 13 added); one case added in a third
session, with the hook file and the workflow in the tree; brought to DEC-494 and DEC-497 in a fourth session (12
cases added, two rewritten, the simulated runner changed; see "Red today"). 74 cases in 9 files.

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
  something (`curl`, `wget`, `gh release`, `pip install`, `pipx install`, `uv tool install`, `npm install`,
  `apt-get install`) is not run and is judged as text. The job is green when every step that ran exits 0. A step
  that fetches the notes ref from `origin` with `git fetch` is run: `origin` is the bare repository.
- **A step after a failed one, as on a hosted runner (DEC-497).** It runs only where its condition says so. The
  simulation evaluates these conditions, bare or inside `${{ }}`: none and `success()` (run only while nothing
  has failed), `always()`, `!cancelled()` and `success() || failure()` (run in either case), `failure()` (run
  only after a failure). Any other condition fails the case with "cannot be run offline". A step that is not
  run for an earlier failure is reported as skipped (`CiResult.skipped`); it does not make the job green.
- **What the runner has.** The tools the two install steps bring are on the runner by the fixture: `gov` and
  gitleaks. Beside them a stand-in `openspec` (it validates anything and leaves a mark) and the designer's
  `pytest`, as `pytest` and as `python3 -m pytest`; a case withholds either. `rulesync` is there only where a
  case asks for its stand-in. `$HOME/.local/bin` is on PATH from the first step; what a step appends to
  `$GITHUB_PATH` is on the PATH of the later steps and `KEY=value` lines of `$GITHUB_ENV` are in their
  environment; `$RUNNER_TEMP`, `$GITHUB_OUTPUT` and `$GITHUB_STEP_SUMMARY` exist.
- **The gitleaks install step, run without a download.** In the two cases that run it, `curl` and `wget` on the
  simulated runner are one stand-in: it hands out one local file for one address (the registry's `archive`) and
  refuses every other address, and each address asked for leaves a mark. The local file is an archive the case
  builds (`gitleaks`, `LICENSE`, `README.md` at its top); its `gitleaks` is a script that leaves a mark. The
  real gitleaks is withheld from that runner. The stand-in answers to these two names only: a step that
  downloads by other means (a `gov` command, Python, `gh`) cannot be run here. On every other runner of the
  suite the two names refuse every address, so no step can reach the network.
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
  `nvidia-smi` that leave a mark and fail. The real `openspec` and `rulesync` are on no PATH; the stand-ins
  above take their names.
- **This repository is never the subject of a run.** Its `gov check` is red on a recorded baseline (DEC-467);
  no case expects it green, and no hook is installed in it (one guard case reads the hooks folder).

lefthook 2.1.15 and gitleaks 8.30.1 are needed by 52 cases (everything in `test_w1_40_pre_commit.py`,
`test_w1_40_pre_push.py`, `test_w1_40_ci_evidence.py`, `test_w1_40_evidence_record.py` and
`test_w1_40_ci_unmeasured.py`, the two hook cases of `test_w1_40_tiers.py` and the two cases of
`test_w1_40_ci_installs.py` that run the step). Where either is absent those cases skip with a named reason.
Both ran inside the designer's session.

## Red today

Observed 2026-10-07 at `7c49f0b2`, the workflow as the engineer left it before DEC-494 and DEC-497 (no install
step, `gov ci job` taking every status as `gov check` gives it, no step condition, checkout of depth 1):
`12 failed, 62 passed`.

| Case | Red reason today |
|---|---|
| `test_w1_40_ci_installs.py::test_the_gitleaks_step_takes_its_version_address_and_checksum_from_the_registry` | no step of the workflow downloads gitleaks |
| `...::test_a_download_that_does_not_match_the_checksum_fails_the_step_and_is_not_unpacked` | the same absent step |
| `...::test_a_download_is_verified_before_it_is_unpacked_and_a_verified_one_is_the_gitleaks_of_the_job` | the same absent step |
| `...::test_a_step_installs_the_gov_package_from_the_checkout` | no step installs a package |
| `test_w1_40_ci_unmeasured.py::test_the_tests_step_says_unmeasured_and_fails_where_pytest_is_not_on_the_runner` | the step fails with Python's "No module named pytest": no "unmeasured" |
| `...::test_the_job_names_the_openspec_check_unmeasured_and_fails_where_openspec_is_not_on_the_runner` | the job is green: the check is YELLOW and the job takes it |
| `...::test_the_job_names_the_adapter_check_unmeasured_and_fails_where_rulesync_is_not_on_the_runner` | the job is red (`CHECK_FAILED: adapter-portability`) and does not say "unmeasured" |
| `...::test_one_run_reports_every_step_after_a_failed_one` | after the failed checks step the four later steps have no condition and do not run |
| `...::test_the_job_is_red_for_a_skill_whose_content_changed_and_whose_version_did_not` | the job is green: the checkout of depth 1 holds no parent, and the check reports green |
| `...::test_the_job_is_red_where_the_project_declares_a_check_of_a_family_gov_check_does_not_know` | the job is green where `gov check` exits non-zero |
| `test_w1_40_evidence_record.py::test_ci_reports_that_no_g3_check_is_declared_and_does_not_fail_for_it` (rewritten) | the words are printed by a step that fails; the job is red |
| `test_w1_40_workflow_text.py::test_the_checkout_brings_the_parent_commit` | the checkout step names no depth |

Green today, for a stated reason:

- `test_w1_40_ci_installs.py::test_no_step_installs_anything_but_gitleaks_and_the_gov_package`: a guard. The
  workflow installs nothing today; the case stays green when the two steps arrive and turns red for a third.
- `test_w1_40_workflow_text.py::test_a_tool_the_job_installs_is_registered_at_its_registered_version`
  (rewritten): it now also accepts a step that reads the version from the tool registry (DEC-497 allows
  either). It holds only for a step that exists, and none does today.
- The 60 untouched cases are green as before. The fixture change (a stand-in `openspec` on every machine, a
  `pytest` launcher, the two downloader names as refusing stand-ins, step conditions evaluated) turned none of
  them red and changed no assertion: observed `62 passed` with the fixture change alone, before any new case.
  Why the stand-in `openspec`: DEC-497 makes the job red where that check is unmeasured, so every case that
  expects the job green needs a runner on which it is measured; a hosted runner will have it only once the
  owner approves it there.

The three gitleaks cases and the one-run case cannot be red for a reason of their own in the tree, where the
step does not exist. The designer ran the suite against throwaway workflows outside the tree (the suite's
support module pointed at another folder; nothing of it is in the tree):

- one that holds the registry's address and checksum in its text, verifies, then unpacks into `$RUNNER_TEMP`
  and appends to `$GITHUB_PATH`, installs `.`, asks for depth 2 and gives the later steps `always()`,
  `!cancelled()` and `success() || failure()`: 68 of 74 green. The six others need the commands behind the
  steps (`gov ci`), which a workflow file cannot replace: the two unmeasured checks, the pytest words, the
  unknown family, the no-G3 colour;
- one that reads the address and the checksum from the registry of the checkout with `wget`, and unpacks into
  `$HOME/.local/bin`: the same 68 green; here the control case runs the step and the job's scan is done by the
  gitleaks of the archive;
- a flawed one (unpacks before it verifies, installs `gov pytest` by name, depth 1, no step condition): the
  mismatch case red ("the download was unpacked although its checksum does not match"), the control case red,
  the package case and the guard red, the depth case, the skill case and the one-run case red.

### Red at `6fcad2c7` (third session)

With the hook file, the workflow and their templates in the tree: `1 failed, 61 passed`. The engineer's commit
`0ef8f1d7` turned that case green.

- The one failure, for its own reason:
  `test_w1_40_ci_evidence.py::test_ci_is_red_when_a_check_of_gov_check_that_carries_no_tier_fails`. The job
  runs the declared checks of tiers G1 and G2, gitleaks, the project's tests and the evidence record: all five
  `run:` steps exit 0, and the job is green for a project whose readiness check is RED.
- Why this check. `gov check` runs, beside the declared checks, checks of its own that carry no tier:
  `openspec-validate`, `skill-version`, `readiness`, and one per policy key without a check. The hooks select
  declared checks by tier, so none of these runs at commit or at push; DEC-489 leaves them to CI ("CI runs the
  whole of the deterministic checks, so no check runs nowhere"), and DEC-087 names readiness among what the job
  runs. Readiness is the one the case plants: it needs no tool (`openspec-validate` needs `openspec`, which is
  on no PATH here), and it reads the tree alone (`skill-version` compares with the commit before, which a
  checkout of depth 1 does not hold).
- The defect, by construction: one file `openspec/changes/w1-40-unjudged/proposal.md` with no frontmatter. A
  change that holds no specification record cannot be judged: `READINESS_INVALID`, hard-block (W1-13, W1-26).
  The case first shows the job green for the commit before; it then commits and pushes the file through the
  hooks, reads the record of the new head commit on the remote, and reads from `gov check --json` in the
  project that `readiness` is the only RED check (the declared G1, G2 and G3 checks GREEN).
- The fixture project is green for the tier-less checks as it stands, so no fixture was changed: `gov check`
  in it exits 0 (`openspec-validate` YELLOW for the absent tool, `skill-version` and `readiness` GREEN, no path
  map and so no policy key). The case says nothing on how the job runs these checks. A job that runs the whole
  of `gov check` also runs the declared G3 check, which
  `test_ci_does_not_run_the_g3_check_and_calls_no_model_tool` and
  `test_ci_does_not_go_red_for_a_g3_check_that_would_fail_on_the_runner` refuse.

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
| **S2** "GitHub Actions runs the deterministic checks and fails when the evidence record is missing or for another commit; carrier chosen and documented" [CAP-39.a] | `test_w1_40_ci_evidence.py`: red with no record; red with the record of another commit; runs G1 and G2; red on a failing G1 or G2 (2); red on a gitleaks finding; red with `gitleaks` or `gov` missing (2); red on a failing test of the project; red where a check that `gov check` runs without a tier (readiness) is red, the declared G1 and G2 checks green and the record there (DEC-087, DEC-489). `test_w1_40_evidence_record.py`: red with the note of another commit copied onto the head commit; red with a record of a failed G3 run; the job reports "no G3 check declared" and is green for it (DEC-497); the ref is named in the hook file and the workflow. `test_w1_40_workflow_text.py`: runs on every push; names gitleaks and `gov`; no result thrown away; pinned actions; no baseline or bypass; the carrier is documented in the hook file and in the workflow; the checkout asks for depth 2 (DEC-497). `test_w1_40_ci_installs.py` (5): the gitleaks step takes version, address and checksum from the registry; a download that does not match fails the step and is not unpacked; verified before unpacked; the `gov` package from the checkout; nothing else installed (DEC-494). `test_w1_40_ci_unmeasured.py` (6): the tests step without pytest, the openspec check without openspec and the adapter check without rulesync each say "unmeasured" and fail; one run reports every step; red for a skill whose content changed and whose version did not; red for a check of an unknown family (DEC-497) | no push workflow; `lefthook.yml` absent; the cases of DEC-494 and DEC-497: see "Red today" |
| **S3** "pre-commit also runs the second gitleaks scan, with the project's rules alone" (DEC-347, DEC-369) | `test_w1_40_pre_commit.py`: a staged secret stops the commit; a staged secret the built-in allowlist shelters stops it (2: alphabet run, `false`), each after showing that one scan with the project's file does not flag it; the sheltering words alone pass; a staged secret counts though the working copy is clean; missing `gitleaks` stops the commit | `lefthook.yml` absent |
| **F1** "CI downloads models or needs a GPU" | `test_w1_40_ci_evidence.py`: CI does not run the G3 check and calls no model tool; CI does not go red for a G3 check that would fail on the runner. `test_w1_40_workflow_text.py`: hosted Ubuntu runner; no model or GPU word outside comments; an installed tool is the registered release | no push workflow |
| **F2** "A push with a failing G3 check leaves CI green" | `test_w1_40_ci_evidence.py`: a push with a failing G3 check never leaves CI green; a failed attempt leaves nothing a later bypass can use; red with the record of another commit. `test_w1_40_evidence_record.py`: a record of a failed G3 run that reaches the remote fails CI. `test_w1_40_pre_push.py`: failing G3 stops the push | `lefthook.yml` absent |
| ticket paths `template/**` | `test_w1_40_templates.py` (4) | template files absent |

| Covers id | Tests |
|---|---|
| CAP-39.a (tiers G0 to G5; G1-G2 at commit, G3 at push, the deterministic tiers in CI) | all nine files; the tier split itself: `test_a_clean_commit_passes_and_runs_the_g1_and_g2_checks`, `test_the_g3_check_does_not_run_at_commit`, `test_a_push_runs_the_g3_check`, `test_ci_does_not_run_the_g3_check_and_calls_no_model_tool`, `test_ci_runs_the_g1_and_g2_checks`, `test_a_commit_is_refused_when_a_tier_the_hook_names_has_no_declared_check` |

## Files

| File | Cases | Needs lefthook and gitleaks |
|---|---|---|
| `test_w1_40_pre_commit.py` | 12 | yes |
| `test_w1_40_pre_push.py` | 8 | yes |
| `test_w1_40_ci_evidence.py` | 14 | yes |
| `test_w1_40_evidence_record.py` | 8 | yes |
| `test_w1_40_tiers.py` | 5 | 2 yes (the hook cases); 3 no (`gov` alone) |
| `test_w1_40_workflow_text.py` | 12 | no |
| `test_w1_40_templates.py` | 4 | no (jinja2) |
| `test_w1_40_ci_installs.py` | 5 | 2 yes (the cases that run the step); 3 no (text) |
| `test_w1_40_ci_unmeasured.py` | 6 | yes |

## A result is measured or it is refused (DEC-449, DEC-454)

- A missing tool is a failure: `gitleaks` or `gov` missing stops the commit; `gov` missing stops the push or
  leaves CI red; `gitleaks` or `gov` missing leaves CI red.
- A tool that is not on the runner is "unmeasured", in that word, and red (DEC-494, DEC-497): the tests step
  without pytest; the openspec check and the adapter check of `gov check` without their tool, which `gov check`
  alone reports as YELLOW (openspec) or as a finding among others (rulesync). The job never takes either for
  green, and it says which check was not measured.
- One run reports every step (DEC-497): a step after a failed one still runs, so a failing check does not hide
  a gitleaks finding, a failing test or a missing record. No `continue-on-error`: the failed step stays failed.
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
| The checkout step asks for the parent commit | `with: fetch-depth: 2` on every `actions/checkout` step | from a source (DEC-497, in those words) |
| CI is red for a skill file whose content changed and whose version did not, between the parent and the head commit | a file under `template/governance/kernel/vendor/` with frontmatter; the job's colour only | from a source (DEC-497; the check is W1-26's, CAP-24.c). That this defect is RED and alone: observed, held by the case's reading of `gov check --json` |
| CI is red where the project declares a check whose family `gov check` does not know | a passing G2 check of a made-up family; `gov check` there exits non-zero with no check RED | from a source (DEC-497); what `gov check` does: observed, held by the case |
| A step whose tool is not on the runner | one step that ran and failed holds, in its own output, the word `unmeasured` (any case) and the name | from a source (DEC-497: "prints the word unmeasured with the tool's name and fails") |
| ... the name for the tests step | `pytest` | from a source (DEC-497) |
| ... the name for a check of `gov check` | the check's id: `openspec-validate` (W1-26's runner), `adapter-portability` (W1-38's declaration, read from the file) | "the job names that check as unmeasured": from a source (DEC-497); that the name is the check's id: assumed |
| Where a tool is absent, no other step fails | pytest withheld: the failed steps are the ones that say so; the same for openspec | assumed: withholding one tool breaks nothing else |
| One run reports every step | with a failing G1 check and a gitleaks finding: no `run:` step is skipped; gitleaks and the project's tests ran (marks); the notes ref is in the checkout; at least two steps failed and two passed | from a source (DEC-497); "at least two and two": assumed, it takes the checks, gitleaks, the tests and the record to be steps of their own, as DEC-087 lists them |
| The gitleaks install step | exactly one `run:` step that fetches (`curl` or `wget`) and names gitleaks; it installs no package | from a source (DEC-494 "in its own step"); `curl` or `wget`: assumed, the names the stand-in answers to |
| ... its address, checksum and version | every `https://` address in the step (and in the `env` of the workflow, the job and the step) is the registry's `archive`, written whole; every 64-digit hex value is the registry's `archive_sha256`; every `x.y.z` in the step is the registered version; where the address or the checksum is not in the text, the step names `tool-registry.yaml` | from a source (DEC-497: read from the registry by the step, or the text and the registry agree) |
| ... a download that does not match | the step asked the stand-in for the registry's address, exits non-zero, nothing that was in the archive is in a folder of the runner, and no later step ran the downloaded gitleaks | from a source (DEC-494, DEC-497) |
| ... verified before unpacked | where the step reads the registry of the checkout (`governance/project/tool-registry.yaml` of the temporary project, one gitleaks entry with `name`, `version`, `archive`, `archive_sha256`): run with a matching local archive, the step passes, the job's scan is done by the gitleaks of the archive, the job is green. Where the text holds the checksum: `sha256sum` or `shasum` stands as a command before `tar`, `unzip` or `gunzip` in the step | from a source (DEC-497); the two ways to hold it: the designer's (R-17) |
| ... where the step puts gitleaks | a folder it appends to `$GITHUB_PATH`, or `$HOME/.local/bin` | assumed: `sudo` and `/usr/local/bin` cannot be used offline; that a hosted runner has `$HOME/.local/bin` on PATH is not verified here |
| The `gov` package | exactly one step runs a package installer (`pip`, `pip3`, `pipx`, `uv pip`, `uv tool`); every argument that is no option is the checkout (`.`, `./`, `$GITHUB_WORKSPACE`, `${{ github.workspace }}`, `$PWD`); no `-r`, `-i`, `--index-url`, `--extra-index-url`, `-f`; it fetches no file | from a source (DEC-497 "installed from the checkout"); the installer names and the spellings of the checkout: assumed. Never run |
| Nothing else is installed | every download step is one of the two above; the gitleaks step names none of pytest, openspec, rulesync, lefthook; no `uses:` names one of them or gitleaks | from a source (DEC-494, DEC-497); the `uses:` reading: assumed |
| CI is green for a commit pushed through the hook, red without a record or with another commit's | the job fetches the ref itself and reads the note of the commit it builds | from a source (DEC-087, DEC-489) |
| CI is red where the note on the head commit was written for another commit, and where what a failed G3 run left is on the remote | | from a source (DEC-489: "a record for another commit ... fails CI"; KPI failure line 2) |
| CI prints `no G3 check declared` for a commit whose record says so | in the output of a `run:` step that exits 0; the job is green where everything else is | from a source (DEC-489 "CI reports it"; DEC-497: prints those words and exits 0) |
| CI runs G1 and G2, gitleaks and the project's tests; not G3 | | a source (DEC-087) |
| CI is red where a hard-block check that `gov check` runs without a tier is RED | readiness, by a change folder with no specification record; the job's colour only, no command or option | from a source (DEC-087 names readiness; DEC-489 "CI runs the whole of the deterministic checks, so no check runs nowhere"). That this defect is RED: observed, and held by the case's own reading of `gov check --json` (W1-13, W1-26) |
| `gov check --json` in the temporary project | prints the API-0002 envelope; each entry of `checks` has `id` and `status`; read from `result`, or from `error.details` when it refuses | a source (W1-26's interface); used to show the fixture, not the job |
| The project's tests run from a `tests/` folder holding one file | the temporary project has only `tests/test_ok.py` | assumed: a step that names a deeper folder is red here |
| A download step is recognised by its command and not run | list above; the gitleaks step is run in two cases, against the stand-in downloader | assumed: a step that both downloads and checks would not be run, and its check would not count |
| A download of a registered tool names its registered version or reads it from `tool-registry.yaml`; a binary download verifies a checksum | only if such a step exists | a source (DEC-083, DEC-497, tool registry) |
| Expressions the runner evaluates | `github.sha`, `github.ref`, `github.ref_name`, `github.workspace`, `github.event_name`, `runner.temp`, `runner.os`, `runner.arch`; the conditions listed under "How the tests run"; no matrix, container or services; no step output | assumed: anything else fails the case with "cannot be run offline" |
| Template files | `template/lefthook.yml.jinja`, `template/.github/workflows/<name>.jinja` for each workflow; rendered by Jinja with no answer they equal this repository's files; `${{` survives rendering | from a source (DEC-489) |

The cases of DEC-494 and DEC-497 name no command of the job: they go through the workflow's steps as the
simulated runner runs them and through the workflow's text.

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

### Decided by DEC-494 and DEC-497

No package of this suite is open. The numbers below are this README's; the lead's numbers, which DEC-497 uses,
are given beside them.

- **P-4 (installs): DEC-494, the owner's.** The workflow installs gitleaks and the `gov` package only, each in
  a step of its own, gitleaks verified against the registry's `archive_sha256`; nothing else. Held by
  `test_w1_40_ci_installs.py`.
- **P-6 (a record that says "no G3 check declared"): DEC-497.** The step prints the words and exits 0; the job
  is green where everything else is. Held by the rewritten case. The weakness stays recorded (R-18).
- **This README's P-7, the lead's P-9 (an absent `openspec`): DEC-497, which replaces the recommendation** to
  take `gov check`'s yellow. The job names the check as unmeasured and is red. Held by
  `test_w1_40_ci_unmeasured.py`; the simulated runner has a stand-in `openspec` for the green cases.
- **The lead's P-10 (the parent commit): DEC-497.** `fetch-depth: 2`; one text case and one run case.
- **The lead's P-11 (an unknown check family): DEC-497.** The job fails as `gov check` does; one case.
- **The lead's P-7 (the notes ref with more than one clone) and P-8 (`gov ci` declaring the class "read"):
  left as built by DEC-497**, Wave 2 list. No case (R-19).

The three packages as they were written, for the record:

### P-4: may the workflow install registered tools on the hosted runner (decided: DEC-494)
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

### P-6: is the CI job green for a commit whose record says "no G3 check declared" (decided: DEC-497, option a)
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

### P-7: is the CI job red where `openspec` is not on the runner (decided: DEC-497, option b; the recommendation replaced)
- **Question.** DEC-087 lists `openspec validate --strict` among what the job runs. `gov check` reports an
  absent `openspec` as YELLOW (`OPENSPEC_ABSENT`) and exits 0. DEC-449 and DEC-454, as the workflow reads them:
  "a tool that is not on the runner fails its step". Is the job red until `openspec` is on the runner?
- **Why now.** The engineer brings the tier-less checks into the job for the new case. If the step fails for
  the absent tool, every case that expects the job green turns red here: the simulated runner has no `openspec`.
- **Options.** (a) The job takes `gov check`'s own verdict: YELLOW does not fail it, the output names it.
  (b) The job fails for an absent `openspec`; the designer then puts a stand-in on the simulated runner and
  adds the case. (c) As (b), once P-4 has put the registered `openspec` on the runner.
- **Impact.** (a) a hosted runner without `openspec` never validates the specifications, and says so only in
  its output. (b) and (c) the job is red on the hosted runner until P-4 is decided, as it already is for
  `gov` and gitleaks.
- **Reversibility.** High. **Cost.** (a) none; (b) one stand-in, one case.
- **Recommendation.** (a) for this round, since `gov check` is W1-26's and its verdict is the measured one;
  (c) with P-4.
- **Confidence.** Medium. No case was written for either.

## Residuals

- **R-1. Tier selection stays as built** (DEC-489): the hook command calls the check runner's internals;
  `gov check` has no tier option. Unit tests hold the join. No acceptance case.
- **R-2. S0a-G-11 is not in the tree** (`docs/source` cannot be read). No case is derived from it.
- **R-3. A commit without lefthook on PATH passes** (the generated hook exits 0). Nothing before the push
  catches it; CI's own G1-G2 and gitleaks steps do afterwards.
- **R-4. `git commit --no-verify`, `git push --no-verify` and `LEFTHOOK=0`** bypass the hooks by design of git
  and lefthook. The record is what CI holds against a bypassed push; nothing holds against a bypassed commit
  until the push.
- **R-5. The adapter comparison has no step of its own** (DEC-497: it keeps its named place in the workflow, and
  the job's gate already runs the adapter check of `gov check`). No case requires a step or reads the place. One
  case holds the check without rulesync ("unmeasured", red) and, as its control, with a stand-in rulesync
  (green). The stand-in answers `--version` and writes one `CLAUDE.md`: what the real rulesync generates is
  W1-38's, not held here.
- **R-6. The runner is a simulation.** `uses:` steps, the real checkout, the runner image and the network are
  not exercised; the first real run is the owner's first push. Whether GitHub accepts the pushed notes ref and
  the job's fetch of it is seen there for the first time.
- **R-7. DEC-087's other deterministic checks** (schemas, the decision checker, the ticket DAG) are declared
  checks of `gov check`, as W1-26 built it, each with a tier; no case names them separately. Of the checks
  without a tier three are held: readiness, `skill-version` (DEC-497, with the parent commit) and the openspec
  check where its tool is absent. The policy keys are not planted.
- **R-14. `openspec validate --strict` on the runner.** Decided by DEC-497: unmeasured and red without the
  tool, one case. With the tool the suite has only a stand-in that validates anything: that a real `openspec`
  finding turns the job red is W1-26's (its `gov check` cases), not held through the job. This repository's own
  CI job stays red, with "unmeasured" as the reason, until the owner approves openspec, pytest and rulesync for
  the runner (DEC-497 states it).
- **R-15. The `gov` install step is never run.** It is judged as text: one installer command whose only target
  is the checkout. That the installed `gov` is the one of the commit, and that its dependency (PyYAML) arrives,
  is seen on the first real run. On the simulated runner `gov` is the worktree's `src/` by the fixture.
- **R-16. The gitleaks step is run only against a stand-in downloader** under the names `curl` and `wget`. The
  real address, the real archive and its real checksum are never exercised: the registry's `archive_sha256` is
  compared with the workflow's text or read by the step, and no case verifies it against a file (none is on
  this machine, and no test downloads). A step that downloads by other means cannot be run here and fails the
  two cases with a message that says so.
- **R-17. "Verified before unpacked" is held in one of two ways, by what the workflow does.** Where the step
  reads the checksum from the registry of the checkout, by running it with a matching local archive. Where the
  workflow's text holds the checksum, no local file can match it offline: the mismatch case still runs (the
  step fails and nothing is unpacked), and the order of the two commands is held as text only. In that second
  way a step that fails whatever it is given passes both cases; the first real run is what shows it passing.
- **R-18. Removing a project's G3 declarations turns that gate into a report** (DEC-497 records the weakness;
  a statement of intent in a file is on the Wave 2 list). The job is green for such a project; no case holds
  against it.
- **R-19. Left as built by DEC-497, no case:** the notes ref with more than one clone (the push of the ref is
  never forced); `gov ci` declaring the class "read"; the runner reporting a missing parent commit as green
  instead of not measured (W1-26's code: at depth 1 the skill case is green for that reason); only the last
  commit of a push being compared by the skill-version check.
- **R-20. "Unmeasured" is held for three tools:** pytest, openspec, rulesync. DEC-497's rule is for every step;
  for gitleaks and `gov`, which the workflow installs, the cases hold red only
  (`test_ci_is_red_when_a_tool_it_names_is_missing`), not the word.
- **R-21. The step conditions are the simulation's reading of GitHub's rules** (a step with no condition does
  not run after a failure; `always()`, `!cancelled()` and `success() || failure()` do). Job-level conditions,
  `needs`, cancellation and step outputs are not simulated. `uses:` steps are never run, so an action that
  would install a tool is judged by its name alone.
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
