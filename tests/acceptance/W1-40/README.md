# W1-40 acceptance tests: lefthook hooks and the CI workflow

Ticket `DAEO-fdkq`, profile STANDARD (DEC-221). Written before implementation by the Independent Test Designer
(MR-3). 48 cases in 5 files.

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
  is not run and is judged as text. The job is green when every step that ran exits 0.
- **A project that is green or red by construction.** The temporary project holds the template's
  `.gitleaks.toml` (DEC-288), one passing test under `tests/`, and three check declarations of its own, one per
  tier G1, G2 and G3 (the tier is a field of every declaration, DEC-186). Each check leaves a mark in a folder
  outside the project when it runs, and fails while a file there tells it to. No model is involved: "a failing
  G3 check" is the project's G3 check failing.
- **The machine.** PATH is one folder of the test plus `/usr/bin:/bin`. That folder holds `gov` (the console
  script an install of this worktree's `src/` would generate), `gitleaks` and `lefthook` (the registered
  binaries), each of which a case can withhold, and stand-ins named `ollama`, `hf`, `huggingface-cli` and
  `nvidia-smi` that leave a mark and fail. `openspec` and `rulesync` are on no PATH.
- **This repository is never the subject of a run.** Its `gov check` is red on a recorded baseline (DEC-467);
  no case expects it green, and no hook is installed in it (one guard case reads the hooks folder).

lefthook 2.1.15 and gitleaks 8.30.1 are needed by 33 cases (everything in `test_w1_40_pre_commit.py`,
`test_w1_40_pre_push.py` and `test_w1_40_ci_evidence.py`). Where either is absent those cases skip with a named
reason. Both ran inside the designer's session.

## Red before implementation

Observed 2026-10-07: `5 failed, 1 passed, 42 errors`.

- 42 errors: a fixture stops at `lefthook.yml is absent from the repository root` (the 33 hook and CI cases
  and 2 text cases) or at `no workflow under .github/workflows/ runs on push` (7 text cases).
- 5 failures: the four template cases (`template/lefthook.yml.jinja is absent`, `no workflow under
  .github/workflows/`, `template/.github/workflows/ is absent`, `... holds no template`) and the carrier case
  (`neither lefthook.yml nor a workflow exists`).
- 1 pass: `test_no_lefthook_hook_is_installed_in_this_repository`, a guard that is green before and after.

Behaviour could not be made red for another reason than "the file is absent" inside the tree: every case goes
through the two files. The designer therefore ran the suite outside the tree against two throwaway stand-ins
(nothing of them is in the tree): a working one (git note as carrier), 48 of 48 green; and a hook file whose
two hooks run `true`, with which 21 behaviour cases are red (every pre-commit and pre-push success and failure
case that needs a check to have run).

## KPI lines and the covers id

| KPI line | Tests | Red reason today |
|---|---|---|
| **S1a** "pre-commit runs G1-G2" [CAP-39.a] | `test_w1_40_pre_commit.py`: clean commit runs G1 and G2; failing G1, failing G2 stop the commit (2); passes again; G3 does not run at commit; missing `gov` stops the commit | `lefthook.yml` absent |
| **S1b** "pre-push runs G3 including model-dependent tests and writes an evidence record bound to the head commit" [CAP-39.a] | `test_w1_40_pre_push.py`: push runs G3; failing G3 stops the push; passes again; one push leaves the record CI asks for; the record follows the head commit; the push leaves the tree clean; missing `gov` or `lefthook` never ends with CI green (2) | `lefthook.yml` absent |
| **S2** "GitHub Actions runs the deterministic checks and fails when the evidence record is missing or for another commit; carrier chosen and documented" [CAP-39.a] | `test_w1_40_ci_evidence.py`: red with no record; red with the record of another commit; runs G1 and G2; red on a failing G1 or G2 (2); red on a gitleaks finding; red with `gitleaks` or `gov` missing (2); red on a failing test of the project. `test_w1_40_workflow_text.py`: runs on every push; names gitleaks and `gov`; no result thrown away; pinned actions; no baseline or bypass; the carrier is documented | no push workflow; `lefthook.yml` absent |
| **S3** "pre-commit also runs the second gitleaks scan, with the project's rules alone" (DEC-347, DEC-369) | `test_w1_40_pre_commit.py`: a staged secret stops the commit; a staged secret the built-in allowlist shelters stops it (2: alphabet run, `false`), each after showing that one scan with the project's file does not flag it; the sheltering words alone pass; a staged secret counts though the working copy is clean; missing `gitleaks` stops the commit | `lefthook.yml` absent |
| **F1** "CI downloads models or needs a GPU" | `test_w1_40_ci_evidence.py`: CI does not run the G3 check and calls no model tool; CI does not go red for a G3 check that would fail on the runner. `test_w1_40_workflow_text.py`: hosted Ubuntu runner; no model or GPU word outside comments; an installed tool is the registered release | no push workflow |
| **F2** "A push with a failing G3 check leaves CI green" | `test_w1_40_ci_evidence.py`: a push with a failing G3 check never leaves CI green; a failed attempt leaves nothing a later bypass can use; red with the record of another commit. `test_w1_40_pre_push.py`: failing G3 stops the push | `lefthook.yml` absent |
| ticket paths `template/**` | `test_w1_40_templates.py` (4) | template files absent |

| Covers id | Tests |
|---|---|
| CAP-39.a (tiers G0 to G5; G1-G2 at commit, G3 at push, the deterministic tiers in CI) | all five files; the tier split itself: `test_a_clean_commit_passes_and_runs_the_g1_and_g2_checks`, `test_the_g3_check_does_not_run_at_commit`, `test_a_push_runs_the_g3_check`, `test_ci_does_not_run_the_g3_check_and_calls_no_model_tool`, `test_ci_runs_the_g1_and_g2_checks` |

## Files

| File | Cases | Needs lefthook and gitleaks |
|---|---|---|
| `test_w1_40_pre_commit.py` | 12 | yes |
| `test_w1_40_pre_push.py` | 8 | yes |
| `test_w1_40_ci_evidence.py` | 13 | yes |
| `test_w1_40_workflow_text.py` | 11 | no |
| `test_w1_40_templates.py` | 4 | no (jinja2) |

## A result is measured or it is refused (DEC-449, DEC-454)

- A missing tool is a failure: `gitleaks` or `gov` missing stops the commit; `gov` missing stops the push or
  leaves CI red; `gitleaks` or `gov` missing leaves CI red.
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
| Hooks work after `lefthook install` and plain `git commit` / `git push origin main` | no wrapper command, no second push | assumed, pending P-2 |
| A check's tier | the `tier` field of its declaration under `template/governance/kernel/checks/` | a source (DEC-186, `gov.cli.checks`) |
| pre-commit runs the checks of tier G1 and G2 and not G3 | by the tier field | a source (KPI S1, DEC-075); how the tiers are selected is the engineer's (R-1) |
| pre-push runs the checks of tier G3 | by the tier field | a source (KPI S1); what else G3 holds: P-1 |
| A check command runs by `sh -c` with the caller's environment; exit 0 is green | | a source (DEC-285; observed) |
| pre-commit refuses a staged secret by the project's `.gitleaks.toml`, and one by its rules alone | staged content | a source (DEC-347, DEC-369) |
| Workflow | at least one file under `.github/workflows/` with `push` in `on`, unfiltered | a source (DEC-075 "on every push") |
| Runner | `runs-on: ubuntu-<something>` | a source (DEC-087 "hosted runner") |
| The job has an `actions/checkout` step, pinned | | assumed: how a hosted job gets its tree |
| What the checkout brings | depth 1 unless `fetch-depth` says otherwise; no notes | assumed from the action's documented defaults; not verifiable offline |
| CI is green for a commit pushed through the hook, red without a record or with another commit's | whatever the carrier | a source (DEC-087) |
| CI runs G1 and G2, gitleaks and the project's tests; not G3 | | a source (DEC-087) |
| The project's tests run from a `tests/` folder holding one file | the temporary project has only `tests/test_ok.py` | assumed: a step that names a deeper folder is red here |
| A download step is recognised by its command and not run | list above | assumed: a step that both downloads and checks would not be run, and its check would not count |
| A download of a registered tool names its registered version; a binary download verifies a checksum | | a source (DEC-083, tool registry); whether it may install at all: P-4 |
| Expressions the runner evaluates | `github.sha`, `github.ref`, `github.ref_name`, `github.workspace`, `github.event_name`; conditions `always()` only; no matrix, container or services | assumed: anything else fails the case with "cannot be run offline" |
| Carrier documented | one of `lefthook.yml`, a workflow file, a file under `src/gov/ci/` holds "evidence record", "carrier" and the carrier chosen | assumed, pending P-2: the KPI fixes no place |
| Template files | `template/lefthook.yml.jinja`, `template/.github/workflows/<name>.jinja` for each workflow; rendered by Jinja with no answer they equal this repository's files | assumed, pending P-5 |

No module, command or record format under `src/gov/ci/**` is named by any case.

## Decision packages

### P-1: what "G3 including model-dependent tests" runs
- **Question.** Which checks and tests are tier G3, and which of them are "model-dependent"?
- **Why now.** The KPI names them, and no source lists them. Today no declaration has tier G3 (all are G1 or
  G2), `gov check` has no tier option and runs every declaration, and the text of S0a-G-11 is not in the tree.
- **Options.** (a) G3 is every declaration with `tier: G3`, plus the tests that need a local model, selected by
  a pytest marker the project declares. (b) G3 is the whole acceptance suite on the owner's machine. (c) G3 is
  the G3 declarations only; model-dependent tests become declarations.
- **Impact.** (b) makes every push take as long as the suite. (a) needs a marker and a pass over the existing
  suites to mark them. (c) needs no new mechanism but someone must register the model-dependent checks.
- **Reversibility.** High: a list.
- **Cost.** (c) lowest; (a) one pass over the suites; (b) minutes per push.
- **Recommendation.** (c), and the retrieval and embedding checks get `tier: G3` in their own tickets.
- **Confidence.** Medium. The cases hold for all three: they use the project's own G3 declaration.

### P-2: the evidence record and its carrier
- **Question.** Git note or commit; what the record holds; how it is bound; how CI reads it.
- **Why now.** KPI S2 says "chosen and documented"; DEC-087 leaves it to this ticket.
- **Options.** (a) A git note on the head commit under a ref of its own, written by pre-push after G3 passes
  and pushed by the hook to the same remote; CI fetches that ref and reads the note of `GITHUB_SHA`. (b) A
  commit that adds a record file naming the commit it vouches for (its parent); CI checks that the head is that
  commit and its parent matches, or that the file names the head's tree. (c) A record in the commit message
  (a trailer), written before the commit exists.
- **Impact.** (a) leaves history untouched and binds by the object the note is attached to; notes are not
  pushed or fetched by default, so the hook must push the ref and the job must fetch it; a force-push of the
  notes ref can lose records. (b) changes the head during a push: a pre-push hook cannot add to what is being
  pushed, so one `git push` is not enough; it needs a wrapper or a second push, and every push adds a commit.
  (c) cannot hold a result measured on the commit itself.
- **What each option needs of the cases.** (a) nothing: all 48 hold as written (shown with the throwaway).
  (b) `test_one_push_through_the_hook_leaves_the_record_ci_asks_for`,
  `test_the_record_follows_the_head_commit_push_after_push`, `test_the_push_leaves_the_project_clean` and the
  `pushed` fixture assume one plain push; they would be rewritten to the wrapper or the second push, and
  "the remote holds the pushed commit" would become "holds its record commit".
- **Reversibility.** Medium: the carrier is in the hook, the job and every clone's habits.
- **Cost.** (a) about 20 lines; (b) more, plus a changed way of pushing.
- **Recommendation.** (a), the record holding at least the commit id, the result and the checks that ran.
- **Confidence.** Medium-high.

### P-3: a record changed after the fact
- **Question.** Must CI detect a record that was written by hand, or edited, without G3 having run?
- **Why now.** Failure line 2, read widely. DEC-087 asks only that the record exists and matches the head.
- **Options.** (a) No: the boundary is advisory (DEC-075), the owner is the only one who pushes (DEC-465), and
  a hand-written record is a deliberate bypass like `--no-verify`. (b) The record carries a hash of what ran;
  CI recomputes what it can. (c) The record is signed with a key on the owner's machine.
- **Impact.** (b) detects accidents, not intent. (c) is a key to manage.
- **Reversibility.** High. **Cost.** (a) none; (b) small; (c) a key and its handling.
- **Recommendation.** (a) for Wave 1, recorded as a residual. No case is written for it.
- **Confidence.** Medium.

### P-4: may the workflow install registered tools on the hosted runner
- **Question.** The runner has no gitleaks, no lefthook, no rulesync and no `gov`. May the workflow install
  them, each at its registered version with its checksum (DEC-083, DEC-287)?
- **Why now.** Without gitleaks and `gov` the job cannot run what DEC-087 lists; a missing tool is a failure.
- **Options.** (a) Yes, by the registry's release and checksum, in steps of their own. (b) Only gitleaks and
  the package itself; nothing else. (c) No install: the job runs only what the runner image has.
- **Impact.** (c) leaves CI without the secret scan and without `gov check`. (a) adds the release checksums of
  the archives to the registry: it records the checksum of the installed binary, not of the downloaded archive.
- **Reversibility.** High. **Cost.** A few steps; one registry field per tool.
- **Recommendation.** (a) for gitleaks and the package now; rulesync when the adapter step arrives.
- **Confidence.** Medium. The case holds only: a download of a registered tool names the registered version,
  and a binary download verifies a checksum.

### P-5: what the template files may assume of W1-39
- **Question.** W1-39's Copier template is not built. Do the `.jinja` files use answers (a project name, a
  Python version), and which delimiters?
- **Why now.** The ticket's paths name the two template files; the workflow holds `${{ }}`, which Jinja reads.
- **Options.** (a) No answers: the template files render with nothing to this repository's own files; GitHub
  expressions are escaped. (b) Answers from W1-39's questions. (c) Other delimiters set in `copier.yml`.
- **Impact.** (b) and (c) cannot be tested before W1-39; (a) can, and W1-39 may add answers later.
- **Reversibility.** High. **Cost.** None for (a).
- **Recommendation.** (a). The four template cases assume it.
- **Confidence.** Medium-high.

## Residuals

- **R-1. `gov check` has no tier option.** It runs every declaration, so a hook that calls it plainly runs G3
  at commit and in CI. Selecting by tier is needed; `src/gov/check/**` is not in this ticket's paths, `src/gov/ci/**`
  is. Where the selection lives is the engineer's or a package of theirs.
- **R-2. S0a-G-11 is not in the tree** (`docs/source` cannot be read). No case is derived from it.
- **R-3. A commit without lefthook on PATH passes** (the generated hook exits 0). Nothing before the push
  catches it; CI's own G1-G2 and gitleaks steps do afterwards.
- **R-4. `git commit --no-verify`, `git push --no-verify` and `LEFTHOOK=0`** bypass the hooks by design of git
  and lefthook. The record is what CI holds against a bypassed push; nothing holds against a bypassed commit
  until the push.
- **R-5. The adapter check (W1-38) is not merged.** No case; `rulesync` is on no PATH of the simulated runner,
  so a step that runs it is red here. The place for it is a step of its own in the workflow, with its case, when
  W1-38's check is merged.
- **R-6. The runner is a simulation.** `uses:` steps, the real checkout, the runner image and the network are
  not exercised; the first real run is the owner's first push.
- **R-7. DEC-087's other deterministic checks** (schemas, readiness, the decision checker, the ticket DAG,
  `openspec validate --strict`) are inside `gov check`, as W1-26 built it; no case names them separately.
  `openspec` is on no PATH here, and `gov check` reports it YELLOW, not red.
- **R-8. gitleaks' built-in rules stay sheltered by the built-in allowlist** (DEC-347's own residual).
- **R-9. A pre-push gate stricter than G3** (one that also runs G1-G2 or the tests) is allowed by every case.

## Not done in this repository

No hook is installed here: the worktrees share one hooks folder, and `gov check` is red on the baseline. The
owner's step at the Wave 1 exit, from the main tree, after the baseline is empty (DEC-472):

```
~/.local/bin/lefthook install
```
