# W2-209 acceptance tests: releasing on the owner's behalf, slice (a), the patch release

Written by the independent test designer (MR-3) from the ticket's eleven success lines and five failure lines
(`.tickets/DAEO-a2h5.md`, profile FULL) and the approved spec `docs/emergency-2/proposals/RELEASE-ON-BEHALF.md`
(DEC-1223, DEC-1224 (3); slice (a) only), before any implementation, on the base 51edaa44d. Every case is of the
acceptance kind but one, `test_w2_209_authority.py::test_s3_the_authority_file_committed_here_is_off_with_the_decision_and_bake_hours`,
which is of the **repository-state** kind (it reads this repository's committed authority file).

The ticket's Interface section and its KPI lines fix what they fix. Every name they leave open is fixed once, below
("Interface"); the engineer follows it.

## How the suite runs

- **Public interfaces only**: the `gov` command line (`gov release <X> --patch ... --json`), `python3 -m
  gov.close.nightly`, the functions the ticket names (`gov.release._patch_test`, `gov.release.proving.rehearse`,
  `gov.release.repin.repin`, `gov.release.repin.burned`), the two push-text functions fixed below
  (`gov.release.repin.push_text`, `gov.release.repin.failure_text`), the existing `gov.update.pending.pending`,
  `gov.close.nightly.night`, `gov.release.verify_at` and `gov.release.build`, and the files they write. No private
  module of the release, update or nightly code is imported by a test.
- **Every function is called in a child process** (`w2_209_driver.py`) whose `HOME` is the case's scratch home,
  `PYTHONPATH` this worktree's `src/`, `PYTHONUSERBASE` the real user base, `GOV_ROLE=orchestrator` where the case
  says so, and no Claude Code variable. The machine's own `~/.local/bin/gov` link, `repin.json` and `rollback.sh`
  are read before and after every test; a change naming this run's temporary folder fails the test
  (`conftest.py::machine_untouched`, a backstop that a real re-pin made meanwhile does not trip).
- **The planted source** (`w2_209_support.build_base`, built once per process, copied per case): a git repository
  that looks to the release code like the Gov OS repository: `pyproject.toml` (project `gov`), a small stand-in `gov`
  package under `src/gov` (a command line that answers `--version`, `--help`, `launch --help`, `retrieve --json` and
  `doctor --json` in the real envelopes' forms; command modules `alpha`, `beta`; a hook probe; a behaviour file that
  plants one fault per release), `template/` (kit schemas `a`, `b`; the five hook programs), `docs/contract`,
  `docs/charter`, `docs/emergency-2/EMERGENCY-2.md`, `.tickets/PLNT-aaaa.md` and `PLNT-bbbb.md`, the authority file
  (`off`, committed with the owner's trailer) and the tool registry, `.gitignore` holding `.gov-runtime/`. Releases
  0.1.0 and 0.1.1 are built with `gov.release.build` (the base's code), their records committed and tagged
  `v<X>` (annotated) on the record commit. Between them: PLNT-aaaa closed, a Contract change, a schema and a command
  module added (so every rule fails if N were taken as 0.1.0). A decoy tag `v0.1.9` with no record sits on the first
  commit. From `v0.1.1` (N), one branch per planted change, each ending in the version commit `0.1.2`:
  `contract`, `charter`, `emergency` (P2), `ticket` (PLNT-bbbb closed), `feature` (a commit under `src/gov` with
  `Class: F` and no `Fix:`), `fix_open_ticket` (a `Fix:` commit whose `Task:` ticket is open at N) (P3), `command`
  (a new `src/gov/w2209probe/command.py`, `Class: C`) (P4), `schema_added`, `schema_removed` (P5), `minor` (0.2.0)
  and `prerelease` (0.1.2-rc.1) (P1); and `clean`: two `Fix:` commits with `Task: PLNT-aaaa` (closed at N; one
  merged with `--no-ff`, its merge commit carrying no trailer), a `Class: Q` chore under `src/gov`, a `Class: C`
  chore under `docs/emergency-2/proposals/` (not P2's path) and the version commit.
- **A case's copy** (`make_case`) puts HEAD on `w2/integrate` at the case's tip and, unless the case says otherwise,
  turns the authority file on by a commit carrying `Decided-by: owner (standing, DEC-1223)` (C is then that commit).
- **Suite records** are written outside the tree in the nightly's form (`branch`, `head`, `tree`, `scope`,
  `verdict`, `optin`, ...).
- **The scratch home** (`make_home`): `~/.local/share/gov-os/pin-<12 hex>/bin/gov`, a stand-in gov script of
  release 0.1.1 that answers the re-pin's checks (its `doctor` reports `canaries` unhealthy, as every gov here does,
  before and after), and `~/.local/bin/gov` linked to it; `~/.gov-os/update/repositories` where a case lists one.
- **The stand-in push command** (`push_command`): a script that appends its arguments, one JSON list per call, to a
  file; the push text is its last argument.
- **Cost**: the planted package is small, so a wheel build takes about a second. One base per process; the re-pin
  releases are built once per module; each re-pin builds two wheels and one virtual environment. The folder runs in a
  few minutes under `-n auto`, and serially (as `gov accept` runs it) in under ten.

Run: `TMPDIR=$(mktemp -d) PYTHONPATH=$PWD/src python3 -m pytest tests/acceptance/W2-209 -q -p no:cacheprovider -n auto`
(through the machine's heavy slot), or `gov accept W2-209`.

## Interface (fixed here; the engineer follows it)

### The command line

- `gov release <X> --patch --check`: the rule alone (no gate is read, the authority file included). A patch:
  `ok: true`, exit 0, `result = {"version": X, "kind": "patch", "from": <N's version>, "commit": <C, 40 hex>,
  "rules": {"P1": {"pass": bool, "detail": str}, ..., "P5": {...}}, "failed": []}`. A bigger range:
  `RELEASE_REFUSED`, exit 1, `details = {"kind": "bigger", "from", "commit", "rules", "failed": [<failed rules,
  in order P1..P5>]}`. Writes nothing.
- `gov release <X> --patch [--suite <file>] [--kept <run folder>] [--push <command>]`: `--suite` and `--kept` are
  paths (absolute, or relative to the working folder); `--push` is one string, split with `shlex`.
- **The caller first**, before anything is read (no repository, file or flag value): only `GOV_ROLE` exactly
  `orchestrator`. Any other caller (unset, empty, another role) is `RELEASE_REFUSED` with `details.caller` = the
  `GOV_ROLE` value (`null` when unset) and no `gate`. The global `--role` flag never makes a caller. The same rule
  holds for `--check`. `--patch` never shows or reads the plain form's typed code.
- **The gates' refusal**: `RELEASE_REFUSED`, exit 1, `details = {"gate": "G0".."G4", "reason": <a sentence>,
  "check": <below, for G0, G2 and G4>, "rule": <for G1: the first failed rule, P1..P5>, "rules": <for G1>}`.
- `gov release --help` lists exactly the global options (`-h/--help`, `--json`, `--root`, `--session`, `--role`),
  `--lock-from`, `--patch`, `--check`, `--suite`, `--kept` and `--push`. No flag and no environment variable stands
  in for a gate, the rehearsal, the re-pin or the push.
- On success: `result = {"version", "commit", "tag": "v<X>", "record": "docs/releases/<X>", "record_commit",
  "kind": <kind.json>, "repin": <the re-pin's result>}`.

### The patch rule (G1)

- **N** is the highest version `V` (MAJOR.MINOR.PATCH, no pre-release) such that the tag `v<V>` exists and
  `docs/releases/<V>/manifest.json` exists at C. Whether N's record verifies is G4's question, not G1's. P1 to P5
  read N at its tag's commit.
- **P1**: `project.version` of `pyproject.toml` at C has N's major and minor, a larger patch number, and no
  pre-release or build part. The detail names the version found.
- **P2**: `git diff --name-only N C -- docs/contract docs/charter docs/emergency-2/EMERGENCY-2.md` is empty. The
  detail names each path.
- **P3**: no `.tickets/*.md` has front-matter `status: closed` at C without having it at N (the detail names its
  `id`); and every non-merge commit of N..C touching `src/gov` or `template` carries `Class: Q`, or `Class: C`, or
  a `Fix:` trailer together with a `Task:` trailer naming a ticket (by its `id`) closed at N. The detail names each
  failing commit by at least its first 12 characters.
- **P4**: the command names at a commit, read from git objects: every `src/gov/<folder>/command.py` (named
  `<folder>` with `_` read as `-`) and every `src/gov/cli/commands/<name>.py` but `__init__.py`. The detail names
  the names added and removed.
- **P5**: the files under `template/governance/kernel/schemas` added or removed between N and C; the detail names
  each file.
- **`kind.json`** (written at the cut): `{"version": X, "kind": "patch", "from": <N's version>, "commit": <C>,
  "rules": {"P1": {"pass", "detail"}, ...}}`.

### G0, G2, G3, G4

- **G0** reads `governance/project/release-authority.yaml`: a YAML map whose `patch_releases` is on (PyYAML reads
  the literal `on` as `true`; `true` or the string `"on"` count as on, anything else is off), whose `decision` is a
  non-empty string, whose working-tree bytes equal its bytes at HEAD (an uncommitted or untracked file is refused),
  and whose last commit (`git log -1 -- <file>`) carries a `Decided-by:` trailer whose value starts with `owner`.
  Checks: `absent`, `unreadable`, `off`, `decision`, `uncommitted`, `trailer`.
- **G2** reads `--suite`: a JSON map whose `head` is 40 hex characters. Checks, the first failing in this order:
  `missing` (no `--suite`), `unreadable` (the file cannot be read, is not JSON, is not a map, or its `head` is not 40
  hex characters, a ref's name included), `scope` (not `full`), `verdict` (not `green`), `optin` (absent, not a
  list, or without `weekly`), `head` (not C), `tree` (not C's tree).
- **G3** runs `gov.release.proving.rehearse(root, C, X, <--kept>)`; no `--kept` is `NOT_READY` ("no kept run").
  Its refusal adds `verdict` and `reasons` to the details.
- **G4** checks: `dirty` (`git status --porcelain --untracked-files=all` lists anything), `ancestor` (C is not an
  ancestor of `refs/heads/w2/integrate`), `frozen` (`gov.util.freeze.freeze_state(root) == "frozen"`), `exists` (a
  tag `v<X>`, or `docs/releases/<X>` at C or in the tree), `previous` (`gov.release.verify_at(root, N)` refuses).

### The rehearsal (S5)

- `gov.release.proving.rehearse(root, commit, version, kept, run=None, judge=None)` returns `{"verdict": "READY" |
  "NOT_READY", "reasons": [str], "repositories": {<name>: {"steps": {"check"|"update"|"doctor"|"judge"|"close":
  {"pass": bool, "skipped": bool, ...}}, "failed": <the first failed step or null>}}}`. A NOT_READY reason names
  the repository and the step (`"<name>: <step> ..."`). Never raises.
- The six names: `python-app`, `rust-workspace`, `typescript-monorepo`, `legacy-docs`, `secret-history`,
  `python-app-clean`. A missing kept folder, a missing `run.json`, or a missing `repos/<name>` is NOT_READY naming
  what is missing.
- The scratch source is a folder outside `root` and `kept`: a clone of `root` at `commit` with a trial record of
  `version` (`gov.release.build`) committed and tagged `v<version>`. Each repository is cloned (outside `root` and
  `kept`) from `<kept>/repos/<name>`; every step of that repository runs in its clone.
- **The runner** `run(step, repository, argv, cwd)` returns `(returncode, stdout)` (a tuple; the stand-ins also give
  `.returncode` and `.stdout`). Steps, in order: `check` (argv `gov update <version> --check --json`, naming the
  scratch source by `--source <path>` or by the clone's `_src_path`; fails when it exits non-zero or its envelope's
  `result.files.conflicts` is not empty), `doctor_before` (`gov doctor --json`), `update` (`gov update <version>
  --json`, the source named as for `check`; fails when it exits non-zero), `doctor_after` (fails when its exit code
  differs from `doctor_before`'s; the report's step is `doctor`), then the judge, then `close` (`gov close <ticket>`;
  fails when it exits non-zero). The default runner runs the real commands.
- **The judge** `judge(repository, root, outputs)` returns a map with `verdict`; it is asked over the kept
  repository (`root = <kept>/repos/<name>`) and over the clone, `outputs = <kept>/outputs/<name>`; the step passes
  when both are `READY`. The default judge is `tests/acceptance/W2-81/w2_81_judge.judge` over the kept run's
  manifests.
- **The close step's ticket** is `report.json`'s `repositories.<name>.queue.ticket` of the kept run (W2-81's
  `--queue-ticket` form); with none, the step is `{"pass": true, "skipped": true, "reason": ...}` and does not run.
- It writes nothing in `kept` (`.git` folders included) or in `root` (files, refs, HEAD, index).

### The rehearsal judged by regression (S12 to S15; the CTO's ruling on W2-209, DEC-1232, DEC-1233)

The kept W2-81 run of release 0.1.4 is NOT_READY and four of its queue tickets hold no acceptance test (`gov close`
refuses `NO_ACCEPTANCE_TESTS` before any update), so an absolute READY and a close exit of 0 can never pass on it. This
section **supersedes** the sentences above that say the judge step "passes when both are `READY`" and that `close`
"fails when it exits non-zero"; everything else of S5 stands.

- **Judge step** (S12): passes when the verdict over the updated copy **equals** the verdict over the kept repository
  (`NOT_READY` and `NOT_READY` passes, `READY` and `READY` passes); `READY` over the kept repository and `NOT_READY` over
  the copy **fails**; `NOT_READY` and then `READY` (an improvement) **passes** (not worse; open point, see below). A
  judge that raises, or returns no `verdict`, is never a pass, even when both calls fail the same way.
- **Close step** (S13), run per repository with a queue ticket: `gov close <ticket>` runs once **before** the update, in
  a throwaway copy that has not been updated (never in `kept` or `root`), with the runner's step label
  **`close_before`**, and once after the update, with the label **`close`** (as today), in the updated clone. The
  label `close_before` is fixed here, as `doctor_before` is. The order of a repository's runner calls has
  `close_before` before `update`, and `close` after it. The step passes when the two exit codes are **equal** or
  the exit code before was non-zero and after is 0 (nonzero before, 0 after passes; 0 before, non-zero after fails).
  With no queue ticket the step is skipped as today and neither `close_before` nor `close` runs.
- **The report** (S14): the `judge` step's entry keeps `verdicts`, a two-element list `[over the kept repository,
  over the copy]` (one element when the judge raised); the `close` step's entry holds `before` and `after`, the two exit
  codes (and `ticket`), as the `doctor` entry holds `before` and `after`. The NOT_READY reason of a failed `judge` step
  names both verdicts and that of a failed `close` step both exit codes (the reason lines are built from the step's
  fields, as they are today).
- **A relative `root`** (S15): `rehearse` resolves `root` to an absolute path, so `rehearse(".", ...)` with the process
  in the repository, or `rehearse("../root", ...)` from another folder, behaves as the absolute path does (the scratch
  source is made; no "does not exist" reason).
- **Stand-ins** (`w2_209_rg_standins.py`, `w2_209_rg_driver.py`; the base stand-ins are unchanged): `rg_runner` answers
  `close_before` and `close` with the case's exit codes and writes `UPDATED` in the folder an `update` ran in (so a
  close call shows whether its folder was updated); `rg_judge` answers the case's verdict over the kept repository and
  over any other folder (`READY`, `NOT_READY`, `raise`, `none`).

### The cut (S7) and its seam

- `gov.release._patch_test(root, version, *, suite=None, rehearse=None, repin=None, push=None, caller=None)` is the
  cut as `--patch` runs it, beside the real path as `_release_test` is: `suite` the record's path, `rehearse`
  called as `rehearse(root, C, version, None)` (default: the real rehearsal, which with no kept run is NOT_READY),
  `repin` called once after the tag and the merge as `repin(root, version, Path.home(), push=push)` (default:
  `gov.release.repin.repin`), `push` the push command, `caller` the caller's role (default: the process's
  `GOV_ROLE`; the tests set `GOV_ROLE` and never pass it). It raises `gov.cli.errors.GovError("RELEASE_REFUSED", ...,
  details)` with the command line's details and returns the command line's result. The command line never passes
  a stand-in.
- HEAD may be detached at C or on `w2/integrate` at C, and `w2/integrate` may have moved past C. The record is built
  with `gov.release.build` at C; `kind.json`, `gates.json`, `suite.json` and `NOTE.md` are added beside
  `manifest.json` and `manifest.sha256` (the manifest's hash is unchanged); the six files are committed on a side
  branch whose only parent is C, its message ending in one trailer paragraph `Role: orchestrator`,
  `Decided-by: owner (standing, <decision>)`, `Task: release`; `git tag -a v<X>` (unsigned) on that commit;
  `w2/integrate` gets an ordinary merge of it (a two-parent merge commit when `w2/integrate` has moved past C).
- **`gates.json`**: `{"suite": {"record": <the record file's name>, "head", "tree", "optin"}, "proving": <G3's
  report>, "rule": {"kind", "rules"}}`. **`suite.json`**: the suite record's content.
- **`NOTE.md`**: the version; one line per `Fix:` value of the non-merge commits N..C and per subject of the
  non-merge commits N..C carrying `Class: Q` or `Class: C`; the gate evidence (the suite record's name, its head, the
  word `weekly`, G3's verdict, the rule's kind); the rollback line `bash ~/.local/share/gov-os/rollback.sh`; each
  path listed in `$HOME/.gov-os/update/repositories` (or "none listed").

### The re-pin (S8 to S10)

- `gov.release.repin.repin(repo, version, home, *, push=None, check=None)` returns a map and raises nothing for a
  stop: `{"status": "ok" | "rolled_back" | "stopped", "version", "commit": <C>, "step": <for stopped>, "check": <for
  rolled_back>, "pin", "old_pin", "push_text"}`. `check`, when given, replaces the five post-pin checks by
  `check(gov_path) -> <failing check's name or None>` (for unit tests; these tests never pass it).
- **Stops, in order, each before the switch and changing neither the link nor the pin folders** (a folder made for
  the new pin is removed): `burned` (the version is in `burned`), `tag` (`v<X>` is not an annotated tag, or its
  commit's parents are not exactly C), `record` (`git diff --name-only C <tag>` names a path outside
  `docs/releases/<X>/`), `manifest` (the manifest does not hash to `manifest.sha256`, or does not name `version` X,
  `commit` C and a wheel `gov-<cli_version>-py3-none-any.whl` with a 64-hex sha256), `wheel` (the wheel built twice
  from C as `gov.release` builds it is not the record's sha256), `exists` (`pin-<C12>` already exists), `version`
  (`<home>/.local/share/gov-os/pin-<C12>`, made with `python3 -m venv --system-site-packages` and the wheel installed
  offline into it, answers `bin/gov --version` without X). `<C12>` is C's first 12 hex characters; the wheel is kept in
  `<home>/.local/share/gov-os/wheels/<C12>/`. The live pin is `readlink -f <home>/.local/bin/gov`'s `pin-*` folder.
- **Before the switch**, `gov doctor --json` through the live link, in `repo`. **The switch**: `ln -sfn <new
  pin>/bin/gov <home>/.local/bin/gov.new` then one rename onto `<home>/.local/bin/gov`.
- **The post-pin checks**, in order, through the new link in `repo`: `help` (`gov --help`, exit 0), `launch`
  (`gov launch --help`, exit 0), `search` (`gov retrieve "<a question>" --json`, extra arguments allowed: exit 0 and
  `result.facets.lexical.available` and `result.facets.semantic.available` both true), `hooks` (each of
  `template/governance/kernel/hooks/{context_watch,precompact,sessionstart,stop,subagentstop}.py` of `repo`'s working
  tree run as `<new pin>/bin/python -E <program>` with `{}` on standard input, `CLAUDE_PROJECT_DIR=<repo>`, no
  `GOV_ROLE` or `GOV_TICKET`, 120 s at most: passes on exit 0, and `subagentstop` also on exit 2 with
  `return contract incomplete` in its output; a traceback fails), `doctor` (`gov doctor --json`; its parts are the
  maps with a `status` under `result` or, for `DOCTOR_UNHEALTHY`, under `error.details`; a part is unhealthy when its
  status is `fail` or `drift`; fails when a part unhealthy now was healthy before the switch).
- **On a pass**: the `- name: gov` entry of `governance/project/tool-registry.yaml` is replaced in place
  (`version: "<X>"`, the wheel's sha256, install and uninstall lines, date, `approved_by: "<decision>"`, a note), the
  other entries untouched, committed alone with the trailers `Role: orchestrator` and
  `Decided-by: owner (standing, <decision>)` (`decision` from the authority file at HEAD); `repin.json` is
  `{"status": "ok", "version", "commit", "pin", "old_pin", "check": null, "at"}`; `rollback.sh` is written; the
  release push is made.
- **On a failed check**: the link is renamed back to the old pin's `bin/gov`; `repin.json` is
  `{"status": "rolled_back", "version", "commit", "check": <help|launch|search|hooks|doctor>, ...}`; X is appended to
  `<home>/.local/share/gov-os/burned` (one version a line); the failure push is made; no registry commit.
- **`rollback.sh`** (plain bash, never `gov`): the line `ln -sfn <old pin>/bin/gov <home>/.local/bin/gov.new && mv
  -Tf <home>/.local/bin/gov.new <home>/.local/bin/gov; hash -r` with absolute paths, and a line appending X to the
  absolute path of `burned`.
- `gov.release.repin.burned(home)` returns the versions in `burned`, in file order (`[]` without the file).
- **The pushes**: `push` is a command string run once, detached, the text its last argument, as
  `gov.dispatch.runtime.push` does it; with no `push`, nothing runs and `push_text` holds the text.
  `gov.release.repin.push_text(version, fixes, head, verdict)` gives `Gov OS <version> released (patch, <fixes>
  fixes). Suite green on <head[:8]>, proving run <verdict>, pin live. Roll back: bash
  ~/.local/share/gov-os/rollback.sh` (`fix` for one); `gov.release.repin.failure_text(version, check)` gives `Gov OS
  <version> NOT pinned: post-pin check failed (<check>). Rolled back, old gov live, nothing for you to do. Release
  burned; CTO cuts the next patch.`, cut to 190 characters by shortening the check's text, the version and `burned`
  kept. The re-pin counts the fixes as the `Fix:` commits (non-merge) of N..C, N being `kind.json`'s `from`, and takes
  the head and the verdict from `gates.json` (`suite.head`, `proving.verdict`) at the tag.

### Updates and the nightly

- `gov.update.pending.pending` reads `burned` at `Path.home() / ".local/share/gov-os/burned"`; burned versions are
  never a candidate. When every newer verified release is burned: `{"pending": false, "burned": true, "held": <held
  version>, "newest": <the newest burned>, "reason": ..., "summary": ...}`, the reason and summary saying `burned`.
- `python3 -m gov.close.nightly <branch> --optin <name>` (repeatable) and `night(root, branch, coverage=False,
  rebuild=True, optin=None)`: known names `weekly`, `lifted`, `breadth`; any other is refused before anything runs
  (command line: a usage error naming it, exit non-zero, no record). The runs' `GOV_TESTS_OPTIN` is the union of the
  caller's (comma-separated) and the option's names, sorted and joined by commas, absent when the union is empty; the
  record's `optin` is that union as a sorted list (`[]` when empty).

## The map

| KPI | Tests | Expected red reason |
|---|---|---|
| S1 | `test_w2_209_rule.py::test_s1_check_names_exactly_the_planted_rule_and_writes_nothing`, `test_w2_209_rule.py::test_s1_a_range_of_fixes_and_chores_only_is_a_patch_and_writes_nothing` | `gov release` has no `--patch`: argparse exits 2, "unrecognized arguments: --patch --check", no envelope |
| S2 | `test_w2_209_cut.py::test_s2_the_cut_writes_kind_json_in_its_form`, `test_w2_209_pending.py::test_s2_pending_reads_the_kind_of_the_release_record` | `gov.release._patch_test` does not exist (the driver reports `missing`); the two pending cases pin W2-17's reading and pass on the base |
| S3 | `test_w2_209_authority.py::test_s3_the_authority_file_committed_here_is_off_with_the_decision_and_bake_hours`, `test_w2_209_authority.py::test_s3_the_cut_is_refused_at_g0`, `test_w2_209_authority.py::test_s3_an_authority_file_on_and_committed_with_the_owner_trailer_passes_g0`, `test_w2_209_authority.py::test_s3_g0_is_read_first_whatever_the_later_gates_say` | `governance/project/release-authority.yaml` is not in this repository; `gov release` has no `--patch` (argparse, no envelope) |
| S4, F3 | `test_w2_209_suite.py::test_s4_a_record_for_c_full_green_with_the_weekly_tier_passes_g2`, `test_w2_209_suite.py::test_s4_no_suite_record_is_refused`, `test_w2_209_suite.py::test_s4_f3_a_record_not_for_the_exact_commit_or_without_the_weekly_tier_is_refused` | `gov release` has no `--patch` (argparse, no envelope) |
| F3 | `test_w2_209_suite.py::test_f3_a_record_that_cannot_be_read_is_refused_as_unreadable` | `gov release` has no `--patch` (argparse, no envelope) |
| S5 | `test_w2_209_proving.py::test_s5_all_steps_passing_is_ready_in_throwaway_clones_of_the_kept_repositories`, `test_w2_209_proving.py::test_s5_the_close_step_lands_the_kept_run_queue_ticket`, `test_w2_209_proving.py::test_s5_one_failing_step_is_not_ready_naming_the_repository_and_the_step`, `test_w2_209_proving.py::test_s5_a_kept_run_with_five_repositories_is_not_ready`, `test_w2_209_proving.py::test_s5_a_missing_kept_folder_is_not_ready` | `gov.release.proving` does not exist (`missing`) |
| S12 | `test_w2_209_regression.py::test_s12_a_not_ready_kept_run_and_an_equally_not_ready_copy_with_equal_doctor_and_close_is_ready`, `test_w2_209_regression.py::test_s12_ready_before_and_not_ready_after_is_a_regression_naming_the_repository_the_step_and_both_values`, `test_w2_209_regression.py::test_s12_not_ready_before_and_ready_after_is_not_worse_and_passes_the_judge_step`, `test_w2_209_regression.py::test_s12_a_judge_that_raises_or_returns_no_verdict_is_never_a_pass` | the judge step passes only on READY and READY: NOT_READY and NOT_READY, and NOT_READY then READY, fail it; the regression and no-verdict cases pin today's refusal and pass on the base |
| S13 | `test_w2_209_regression.py::test_s13_a_close_that_refuses_before_the_update_and_refuses_the_same_after_it_passes`, `test_w2_209_regression.py::test_s13_gov_close_runs_as_close_before_in_an_unupdated_throwaway_copy_before_the_update_and_as_close_after_it`, `test_w2_209_regression.py::test_s13_a_close_that_exits_0_before_the_update_and_not_after_it_fails_naming_close_and_both_exit_codes`, `test_w2_209_regression.py::test_s13_a_close_that_refuses_before_the_update_and_exits_0_after_it_passes`, `test_w2_209_regression.py::test_s13_with_no_queue_ticket_the_close_step_is_skipped_and_no_close_runs_at_all` | no `close_before` call is made and the close step passes only on exit 0 (a close refusing the same before and after fails it); its entry and reason hold no `before` exit code; the no-ticket case pins today's skip and passes on the base |
| S14 | `test_w2_209_regression.py::test_s14_each_judge_and_close_entry_holds_both_values` | the close step's entry holds only `exit` and `ticket`, no `before` and `after` |
| S15 | `test_w2_209_regression.py::test_s15_a_relative_root_behaves_as_the_absolute_one` | `root` is not resolved: the scratch clone fails with `fatal: repository '.' does not exist`, NOT_READY "the rehearsal could not run" |
| S6 | `test_w2_209_state.py::test_s6_each_state_condition_alone_is_refused_at_g4_after_g3`, `test_w2_209_state.py::test_s6_two_reds_at_once_name_the_earlier_gate_g2_before_g4`, `test_w2_209_state.py::test_s6_two_reds_at_once_name_the_earlier_gate_g3_before_g4_on_the_command_line`, `test_w2_209_state.py::test_s6_two_reds_at_once_name_the_earlier_gate_g3_before_g4_through_the_seam` | `gov.release._patch_test` does not exist (`missing`); `gov release` has no `--patch` (argparse, no envelope) |
| S7 | `test_w2_209_cut.py::test_s7_the_cut_tags_the_record_commit_annotated_unsigned_with_c_its_parent`, `test_w2_209_cut.py::test_s7_the_record_commit_adds_the_record_files_only`, `test_w2_209_cut.py::test_s7_the_record_commit_carries_the_orchestrator_the_standing_decision_and_task_release`, `test_w2_209_cut.py::test_s7_w2_integrate_holds_the_record_commit_by_an_ordinary_merge`, `test_w2_209_cut.py::test_s7_the_manifest_is_built_as_gov_release_builds_it_and_verifies`, `test_w2_209_cut.py::test_s7_gates_json_and_suite_json_hold_the_evidence`, `test_w2_209_cut.py::test_s7_g3_ran_once_on_c_and_the_re_pin_after_the_tag`, `test_w2_209_cut.py::test_s7_every_caller_but_the_orchestrator_is_refused_before_anything_is_read`, `test_w2_209_cut.py::test_s7_a_role_flag_does_not_make_an_orchestrator`, `test_w2_209_cut.py::test_s7_the_owner_plain_terminal_is_refused_and_never_asked_the_typed_code`, `test_w2_209_cut.py::test_s7_the_plain_form_from_an_orchestrator_session_is_refused_as_today`, `test_w2_209_cut.py::test_s7_gov_release_has_the_patch_flags_and_no_stand_in_flag`, `test_w2_209_cut.py::test_s7_the_command_line_runs_the_real_rehearsal_whatever_the_environment_says` | `gov.release._patch_test` does not exist (`missing`); `gov release` has no `--patch` (argparse, no envelope; `--help` lacks `--patch`, `--check`, `--suite`, `--kept`, `--push`); the plain-form case pins DEC-772 and passes on the base |
| S8 | `test_w2_209_repin.py::test_s8_a_green_re_pin_switches_the_link_to_the_new_pin`, `test_w2_209_repin.py::test_s8_a_green_re_pin_commits_the_registry_entry_with_the_orchestrator_and_the_standing_decision`, `test_w2_209_repin.py::test_s8_a_green_re_pin_writes_repin_json_ok_and_rollback_sh`, `test_w2_209_repin.py::test_s8_each_early_stop_changes_nothing` | `gov.release.repin` does not exist (`missing`) |
| S9, F4 | `test_w2_209_repin.py::test_s9_a_failed_post_pin_check_puts_the_previous_gov_back_and_burns_the_release`, `test_w2_209_repin.py::test_s9_a_second_re_pin_of_a_burned_release_is_refused`, `test_w2_209_pending.py::test_s9_a_burned_patch_release_is_never_offered` | `gov.release.repin` does not exist (`missing`); `pending` offers the burned 0.1.2 (`pending: true`) |
| F4 | `test_w2_209_repin.py::test_f4_a_failed_check_leaves_the_registry_unchanged_and_pushes_the_owner_once` | `gov.release.repin` does not exist (`missing`) |
| S10 | `test_w2_209_repin.py::test_s10_rollback_sh_is_plain_shell_holding_the_line_and_the_burned_mark`, `test_w2_209_repin.py::test_s10_a_pinned_release_makes_one_push_of_at_most_190_characters`, `test_w2_209_repin.py::test_s10_the_pasted_rollback_line_restores_the_previous_gov_and_burns_the_release`, `test_w2_209_repin.py::test_s10_the_release_push_fits_190_characters_for_the_longest_version_and_eight_fixes`, `test_w2_209_repin.py::test_s10_the_failure_push_is_cut_to_190_characters_keeping_the_version_and_burned`, `test_w2_209_cut.py::test_s10_note_md_holds_its_five_parts`, `test_w2_209_remote.py::test_s10_the_full_flow_pins_the_release_and_pushes_the_owner_once` | `gov.release.repin` and `gov.release._patch_test` do not exist (`missing`) |
| S11 | `test_w2_209_nightly.py::test_s11_the_optin_option_runs_the_weekly_tier_and_records_it`, `test_w2_209_nightly.py::test_s11_the_option_adds_to_the_callers_variable_and_drops_none`, `test_w2_209_nightly.py::test_s11_a_run_started_by_hand_with_the_variable_alone_is_recorded`, `test_w2_209_nightly.py::test_s11_night_takes_the_option_as_a_list`, `test_w2_209_nightly.py::test_s11_an_unknown_suite_name_is_refused_before_anything_runs`, `test_w2_209_nightly.py::test_s11_without_option_or_variable_the_record_says_optin_empty` | the nightly has no `--optin` (argparse: "unrecognized arguments"); `night()` takes no `optin` (TypeError); its record has no `optin` key |
| F1 | `test_w2_209_state.py::test_f1_a_red_gate_leaves_the_record_folder_tags_branches_pins_and_link_as_they_were` | `gov release` has no `--patch` (argparse, no envelope); `gov.release._patch_test` does not exist (`missing`) |
| F2 | `test_w2_209_rule.py::test_f2_a_bigger_range_is_refused_at_g1_with_every_other_gate_green`, `test_w2_209_rule.py::test_f2_a_bigger_range_with_the_authority_file_off_is_refused_at_g0`, `test_w2_209_rule.py::test_f2_g1_is_named_before_a_red_g2` | `gov.release._patch_test` does not exist (`missing`) |
| F5 | `test_w2_209_remote.py::test_f5_the_plain_form_is_refused_from_an_orchestrator_session`, `test_w2_209_remote.py::test_f5_the_plain_form_is_refused_without_a_terminal_and_without_a_role`, `test_w2_209_remote.py::test_f5_a_full_cut_and_re_pin_contacts_no_remote`, `test_w2_209_remote.py::test_f5_the_authority_file_is_not_written_by_a_cut_or_a_re_pin` | `gov.release._patch_test` does not exist (`missing`); the two plain-form cases pin DEC-772 and pass on the base |

**Green on the base, by design** (they pin today's behaviour the ticket says stays): the two
`test_s2_pending_reads_the_kind_of_the_release_record` rows, `test_s7_the_plain_form_from_an_orchestrator_session_is_refused_as_today`,
`test_f5_the_plain_form_is_refused_from_an_orchestrator_session` and
`test_f5_the_plain_form_is_refused_without_a_terminal_and_without_a_role`. The regression fix's guards are green on the base too: `test_s12_ready_before_and_not_ready_after_is_a_regression_...`
(the base already refuses a READY-then-NOT_READY judge and names both verdicts), the five `test_s12_a_judge_that_raises_or_returns_no_verdict_is_never_a_pass`
cases and `test_s13_with_no_queue_ticket_...`. Every line they sit under also holds
cases that are red on the base. W2-16's owner-terminal cases (`tests/acceptance/W2-16/test_w2_16_owner_terminal.py`)
stay in W2-16's folder; the landing selects them for any change under `src/gov/release`.

## How the lines are read, and what could not be tested as worded

- **S1**: "names exactly that rule" is the set of rules with `pass: false` equal to the planted one, `failed` equal
  to it, and its detail holding the planted path, ticket id, commit (first 12 characters), command name, schema
  file name or version. "Writes nothing" is the snapshot (every file outside `.git` by bytes and mode, every ref,
  HEAD, the index, the stashes) equal before and after. `--check` runs with the authority file `off`: the rehearsal
  on a scratch clone (the ticket's "Rehearsal") needs a planted patch to pass G1 while the file is still off.
- **S3**: "nothing else is read first" is checked by its answer: every later gate planted red, the answer is G0.
- **S4/F3**: a passing record is shown by the answer moving on to G3. "A record of a commit on another branch" is
  the tip of `case/contract`; a `head` holding a ref's name that resolves to C (`w2/integrate`) is refused as
  unreadable (not 40 hex characters).
- **S5**: "starts no session and no model" is not observable from outside; the stand-in runner and judge are the
  only executors the tests give it. "The W2-81 judge, in its read mode" is reached through `judge=`; the default
  judge's wiring to `w2_81_judge.judge` over real kept outputs is the CTO's real run (a non-goal of this slice).
- **S6/F1**: G4 can be reached only with G3 passing, and G3 passes only stood in, so every G4 case goes through
  `_patch_test`; the command line reaches G0 to G3 (G3 with a missing kept run). F1's "byte for byte" is the
  repository snapshot above plus the scratch home's pin folders, link and every entry under `~/.local`.
- **S7**: "before anything is read" is checked by running the refused callers in a folder that is not a
  repository: the answer names the caller, not a gate. "Ordinary merge" is checked where `w2/integrate` has moved
  one landing past C: its head is a two-parent merge holding the record commit and the landing. "The owner's plain
  terminal" is planted as far as a test can: `GOV_ROLE` unset and a pseudo-terminal on input and output (the test
  process itself runs under a session, and `--patch` has no ancestry seam, rightly); the answer is the caller's
  refusal and no `RELEASE-dddd` code is shown.
- **S7/S10, `NOTE.md`**: the ticket's S10 lists `NOTE.md` under `docs/releases/<X>/` and its verify reads it after
  the re-pin. A record folder is frozen at the cut (DEC-722), and the re-pin refuses a tag whose commit changes more
  than the record, so `NOTE.md` is written by the cut into the record commit: the record holds six files, S7's
  "five files" are checked as a subset, and `NOTE.md` is read at the tag after the cut.
- **S9/F4**: "within 60 seconds" is read as "before `repin` returns": the rollback is synchronous and the link is
  read right after the call (the call's own time includes two wheel builds and a virtual environment, which a loaded
  machine can stretch). "No adopted repository updates to it" is read through `gov.update.pending.pending` (slice
  (b)'s automatic update is not built). "By one rename" is not observable from outside.
- **S10**: "detached" is checked by waiting for the stand-in push's line (up to 20 s) and then 1.5 s more for a
  second; the 190-character bound for "versions up to 99.99.99 and eight fixes" is checked on `push_text` and
  `failure_text`, fixed above as public functions, since a planted release of 99.99.99 with eight fixes would add
  a release build for one length.
- **F5**: "a bigger release is only ever built by the plain form" is F2's refusal at G1. The planted `origin` has
  `remote.origin.uploadpack` and `receivepack` set to a recorder (proven to record an `ls-remote` before the run).
