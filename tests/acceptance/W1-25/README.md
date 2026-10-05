# W1-25 acceptance tests: `gov checkpoint`

Ticket `DAEO-rrxp`, profile STANDARD (DEC-221). Written before implementation by the Independent Test Designer
(MR-3). 52 cases in 7 files; 4 are `local_only`.

```
python3 -m pytest tests/acceptance/W1-25 -q -p no:cacheprovider
python3 -m pytest tests/acceptance/W1-25 -q -p no:cacheprovider -m "not local_only"
```

## How the tests run

- Through the public interface only: the `gov` command line (W1-07's console-script stand-in, `w1_07_support`), its
  output and exit code, and the files it leaves in the project.
- In a temporary committed copy of the working tree. Two fixture tickets (`DAEO-zq25`, `DAEO-zq26`) and one input
  file are added to the copy. Every checkpoint a test reads is one the test made there; no test reads the
  orchestrator's or a lead's checkpoint.
- Deterministic, no network, except the `local_only` cases: one dev-tier clone (`GOV_DEV_TIERS`, default
  `~/gov-os-workbench/synthetic`, cloned into a temporary directory) and one real headless session (3 cases share it).
- `check-jsonschema` validates the record against W1-08's schema, as W1-08's suite does.

## Red before implementation

`6 failed, 46 errors in 1.92s`.

- The 46 errors stop at the `built` fixture: "gov checkpoint is not built yet: it returns NOT_IMPLEMENTED".
- The 6 failures: `gov checkpoint` returns `NOT_IMPLEMENTED` (3 cases, one of them with exit code 1 for an unknown
  option where 2 is expected); `gov checkpoint --help` does not name `--watch`; no declaration
  `template/governance/kernel/checks/fresh-agent-reconstruction*.yaml`; `gov check --list` names no check of that
  family.

## What the sources settle, and what they leave open

| # | Point | Settled by the sources | Open (package) |
|---|---|---|---|
| 1 | Wiring | `src/gov/cli/main.py`: the registry holds `checkpoint` with no handler, and only `check` gets an argument of its own. A command cannot be wired from `src/gov/checkpoint/**`. | **DP-1** |
| 2 | Schema, inputs | W1-08's kernel schema is the one a checkpoint must not contradict (the ticket depends on W1-08; `path-map.yaml` calls `schemas/**` "carried ... not authoritative"). | **DP-2**: the type-specific keys and the command's arguments |
| 3 | Location | CAP-37.a "in the repository"; CAP-20.a (a fresh clone has the latest checkpoint); DEC-176; ADR-0002 §2 L5 (checkpoints are git authority). So: a file git can track, outside `.gov-runtime/`. Tested without naming a directory (`result.path`). | **DP-3**: the directory, and the guard and containment |
| 4 | Triggers | W1-29 and W1-49 own the hooks, W1-30 owns `gov close`; none is on this branch. | **DP-4** |
| 5 | `--watch` | DEC-208, DEC-237: about 30 % of the window. API-0002: exit code 3 is "verification failed / unhealthy". Nothing gives the age or the commit threshold, or where they live. | **DP-5** |
| 6 | Resume, family check | DEC-186: a check is registered by a YAML declaration, listed by `gov check --list`; running it is W1-26. | **DP-6** |

## KPI lines and covers ids

| KPI line | Tests | Red reason |
|---|---|---|
| **Success 1** "A checkpoint conforming to the carried schema is written at every ticket transition, compaction and stop" [CAP-13.b, CAP-37.a, CAP-37.b] | `test_w1_25_command.py` (2 cases on the command), `test_w1_25_record.py` (location, schema, keys, inputs, episodic, per ticket), `test_w1_25_triggers.py::test_each_mandatory_trigger_writes_a_checkpoint_that_records_it` | `NOT_IMPLEMENTED` |
| **Success 2** "A fresh session resumes the ticket at the recorded next step from the checkpoint alone" [CAP-20.a, CAP-37.f] | `test_w1_25_resume.py` (`--resume`: brief, latest, text, read-only, refusal, fresh clone, dev-tier clone), `test_w1_25_live_session.py` | `NOT_IMPLEMENTED` |
| **Success 3** "`gov checkpoint --watch` marks the latest checkpoint stale by policy (age, commits since, context utilisation) without relying on harness hooks; lefthook and the orchestrator can run it" [CAP-37.c] | `test_w1_25_watch.py` (9 cases), `test_w1_25_command.py::test_help_names_watch`, `::test_watch_is_accepted_as_an_argument` | `--watch` not in the help; `NOT_IMPLEMENTED` |
| **Success 4** "Registers the fresh-agent-reconstruction family check ..." [CAP-38.b] | `test_w1_25_check_declaration.py` (2), `test_w1_25_resume.py::test_the_family_check_*` (4), `test_w1_25_live_session.py` (3) | no declaration file; `NOT_IMPLEMENTED` |
| **Failure 1** "A ticket transition leaves no checkpoint" | `test_w1_25_triggers.py`: `test_a_ticket_in_progress_with_no_checkpoint_is_reported`, `test_a_transition_after_the_latest_checkpoint_marks_it_stale`, `test_a_checkpoint_at_the_transition_clears_it`, `test_another_tickets_checkpoint_does_not_cover_the_transition` | `NOT_IMPLEMENTED` |
| **Failure 2** "A checkpoint references an input by id without its hash" | `test_w1_25_record.py`: `test_every_input_has_an_id_a_version_and_a_hash`, `test_an_input_that_cannot_be_hashed_is_refused_and_nothing_is_written`; `test_w1_25_watch.py::test_a_latest_checkpoint_with_an_input_without_its_hash_is_not_fresh`; `test_w1_25_resume.py::test_the_family_check_fails_when_an_input_has_no_hash` | `NOT_IMPLEMENTED` |

| Covers id | Tests |
|---|---|
| CAP-13.b | `test_w1_25_record.py::test_an_earlier_checkpoint_is_kept_when_a_later_one_is_written`, `::test_checkpoints_are_kept_per_ticket`; `test_w1_25_resume.py::test_resume_reads_the_latest_checkpoint_of_the_ticket` |
| CAP-20.a | `test_w1_25_resume.py::test_a_fresh_clone_resumes_from_the_committed_checkpoint`, `::test_a_fresh_clone_of_a_dev_tier_resumes` (`local_only`) |
| CAP-37.a | `test_w1_25_record.py`: location, schema, the three input cases |
| CAP-37.b | `test_w1_25_triggers.py` |
| CAP-37.c | `test_w1_25_watch.py` |
| CAP-37.f | `test_w1_25_resume.py`, `test_w1_25_live_session.py` |
| CAP-38.b | `test_w1_25_check_declaration.py`, the four `test_the_family_check_*` cases |

## Files

| File | Cases | Depends on |
|---|---|---|
| `test_w1_25_command.py` | 5 | sources only |
| `test_w1_25_check_declaration.py` | 2 | sources only (DEC-186) |
| `test_w1_25_record.py` | 14 | DP-2 (recommended option) |
| `test_w1_25_triggers.py` | 8 | DP-4, and DP-2's arguments |
| `test_w1_25_watch.py` | 9 | DP-5, and DP-2's arguments |
| `test_w1_25_resume.py` | 11 (1 `local_only`) | DP-6 deterministic part, and DP-2's arguments |
| `test_w1_25_live_session.py` | 3 (`local_only`) | DP-6 live part |

Only the two "sources only" files are independent of every package: the command's arguments are themselves open
(DP-2), and every behavioural test has to call the command. The argument names, frontmatter keys and error codes are
named once, in `w1_25_support.py`.

## Decision packages

### DP-1: wiring the command into `src/gov/cli/`

- **Question.** How does W1-25 register its handler and its arguments, when `src/gov/cli/**` is outside its paths?
- **Why now.** `main.py` gives `checkpoint` no handler and adds arguments only for `check`; once a handler exists,
  an argument the parser does not know is a usage error. The implementer cannot make any test green without it.
- **Options.**
  - (a) Add `src/gov/cli/main.py` to W1-25's `allowed_paths`.
  - (b) The orchestrator makes one generic change in `main.py`: a command's handler and arguments come from its own
    module (for example `gov.<command>.cli` with `register(subparser)` and `run(root, args, config)`), so no later
    command ticket needs `src/gov/cli/`.
  - (c) The orchestrator wires each command itself after the implementer.
- **Impact.** (a) one line in the ticket; every later command ticket needs the same. (b) about 15 lines once, and
  W1-07's builder tests are re-run. (c) the implementer cannot run the acceptance suite itself.
- **Reversibility.** High for all three.
- **Cost.** (a) none. (b) small, once. (c) one orchestrator step per command.
- **Recommendation.** (a) for this ticket; (b) is worth an owner look for the nine commands still reserved.
- **Confidence.** High that a change in `src/gov/cli/` is needed; medium between (a) and (b).
- **Tests affected.** None.

### DP-2: the schema a checkpoint conforms to, its type-specific keys and the command's arguments

- **Question.** Which schema is "the carried schema", what keys record the ticket, the trigger, the next step and
  the inputs "with ids, versions and hashes", and what arguments give them to the command?
- **Why now.** W1-08's `checkpoint.schema.json` has no type-specific keys (a W1-08 residual in `bootstrap.md`); the
  older `schemas/records/checkpoint.schema.json` has them (`session`, `next_action`, `trigger` required) but has no
  inputs and is "not authoritative". Both are outside the implementer's paths. No source names an argument.
- **Options.**
  - (a) W1-08's kernel schema, extended. The record is a markdown file with frontmatter: the shared keys, plus
    `task` (the ticket id), `trigger`, `next_action`, `created` (names carried from the older schema) and
    `inputs`, a list of `{id, version, hash}` where `hash` contains the sha256 of the input file. The kernel schema
    and template get these keys as required; `template/governance/kernel/schemas/checkpoint.schema.json` and
    `templates/checkpoint.md` join W1-25's paths.
    Command: `gov checkpoint --ticket <id> --trigger <ticket-transition|compaction|stop> --next <text>
    [--input <path>]...`; the ticket file is always an input; the result gives `path` and `id`. A missing argument,
    an unknown ticket or an input that is not a file is a GovError (exit code 1, nothing written), because W1-07
    holds a bare `gov checkpoint --json` to the envelope and not to exit code 2.
  - (b) As (a) but the kernel schema stays as it is; the keys are enforced by the command only.
  - (c) The older schema under `schemas/records/` (JSON record with `session` required), with `inputs` added.
- **Impact.** (a) one W1-08 template case may need a planned revision when the template gains keys. (b) the
  schema accepts a checkpoint without inputs, so failure line 2 is held by code only. (c) contradicts W1-08's
  frontmatter (`state_class` is not required there) and the path map's "not authoritative".
- **Reversibility.** Medium: the keys become the interface of W1-29, W1-30, W1-49 and W1-36.
- **Cost.** (a) about 20 schema lines. (b) none. (c) a second schema family to keep.
- **Recommendation.** (a).
- **Confidence.** Medium-high on the kernel schema; medium on the key and argument names.
- **Tests.** `test_w1_25_record.py` and the names in `w1_25_support.py`. The schema case itself validates against
  the kernel schema of the copy, so it holds under (a) and (b).

### DP-3: the directory of a checkpoint, and the guard

- **Question.** In which directory does `gov checkpoint` write, and how do the guard and the containment check
  treat that write when a worker's `allowed_paths` do not cover it?
- **Why now.** The sources settle "tracked by git, outside `.gov-runtime/`" but not the directory. ADR-0002 §5 puts
  `checkpoints/` under `spec/` in a product; this repository has no `spec/`, and its path map fails on a new
  top-level folder. A worker that runs `gov checkpoint` writes a tracked file outside its ticket's paths, which
  W1-03 reports as a containment finding. DEC-150 says the command "replaces" the orchestrator's scratch checkpoint.
- **Options.**
  - (a) `docs/checkpoints/<ticket>/` here (inside the `docs` namespace), `spec/checkpoints/` in a product, as a
    kernel default; the guard and containment get a standing exception for that directory (a later ticket, since
    `src/gov/guard/**` is outside W1-25's paths). Until then the finding is a record, as DEC-254 treats merges.
  - (b) `.gov-runtime/scratch/checkpoints/`, writable by every role today.
  - (c) (a), and the orchestrator's and the leads' `CHECKPOINT.md` stay in scratch until W1-49 and W1-29 switch.
- **Impact.** (b) is ignored by git, so CAP-37.a and CAP-20.a fail. (a) and (c) add tracked files per ticket.
- **Reversibility.** High (a path).
- **Cost.** (a), (c): a small guard change in another ticket.
- **Recommendation.** (c).
- **Confidence.** Medium.
- **Tests affected.** None: the tests read `result.path` and assert only what the sources settle.

### DP-4: what "at every ticket transition, compaction and stop" means for this ticket

- **Question.** What does W1-25 show of the three triggers without the session hooks and without `gov close`?
- **Why now.** Nothing on this branch calls the command at a compaction, a stop or a transition.
- **Options.**
  - (a) The command accepts exactly the three triggers and records which one; the watchdog reports a ticket whose
    transition left no checkpoint: `CHECKPOINT_MISSING` when a ticket has none, and `CHECKPOINT_STALE` with the
    reason `ticket-transition` when the ticket file changed its status after the latest checkpoint. The calls at
    compaction and stop are W1-29 and W1-49; at close, W1-30.
  - (b) (a) without the detection; failure line 1 moves to W1-29 and W1-30.
  - (c) W1-25 also wraps the ticket tool so that a transition writes the checkpoint.
- **Impact.** (b) leaves failure line 1 untested here. (c) touches `tk`, outside the paths.
- **Reversibility.** High.
- **Cost.** (a) about 20 lines.
- **Recommendation.** (a).
- **Confidence.** Medium.
- **Tests.** `test_w1_25_triggers.py`.

### DP-5: the watchdog's policy, inputs and verdict

- **Question.** Where do the three thresholds come from, how is context utilisation known without a hook, and what
  do lefthook and the orchestrator get back?
- **Why now.** `path-map.yaml` has only the strength `checkpoint: warning`. DEC-208 and DEC-237 give about 30 % of
  the window; no source gives an age or a number of commits.
- **Options.**
  - (a) Arguments with kernel defaults: `--max-age-minutes`, `--max-commits`, `--max-context` (default 0.30), and
    `--context-utilisation <fraction>` passed by the caller; without it, context is not judged. Age is counted from
    the record's `created`. Fresh: exit code 0, `result.stale` false, `result.path`. Stale: error
    `CHECKPOINT_STALE`, exit code 3, `error.details.reasons` out of `age`, `commits`, `context`,
    `ticket-transition`; without `--json` the code and the reasons go to standard error. The watchdog only reads.
  - (b) As (a), with the thresholds in a `checkpoint` map of `governance/project/path-map.yaml` (its top level
    accepts extra keys), read through the config loader, which is outside W1-25's paths.
  - (c) Stale is exit code 0 with `stale: true`, because the policy's strength is `warning`.
- **Impact.** (a) the default age and commit numbers are still the owner's to give; the tests pass thresholds
  explicitly, so they hold for any default under which a new checkpoint is fresh. (c) lefthook cannot block on it.
- **Reversibility.** High.
- **Cost.** (a) none beyond the ticket. (b) a loader and schema change.
- **Recommendation.** (a) now; (b) when W1-29 needs a project value.
- **Confidence.** Medium; high that the caller must supply the utilisation.
- **Tests.** `test_w1_25_watch.py`.

### DP-6: "a fresh session resumes", and the family check

- **Question.** Is a real session needed to show the resume, and what does the registered check run?
- **Why now.** The SessionStart hook is W1-49's and W1-29's; `gov check` cannot run checks before W1-26.
- **Options.**
  - (a) Deterministic: `gov checkpoint --resume --ticket <id>` prints, from the latest checkpoint alone, the brief
    a session needs (`ticket`, `inputs` with hashes, `next_action`, `path`); the hooks inject it later. The check's
    declared command passes when that brief can be built for the latest checkpoint of every ticket that has one,
    and fails when a next step or an input's hash is missing. It is assumed to run at the project root with `gov`
    on `PATH`, exit code 0 for green (W1-26 fixes this).
  - (b) (a) plus one real headless session per acceptance run (`local_only`, cheapest model, two turns, no tool, in
    an empty directory, given only the brief), as DEC-232 did. The check itself stays deterministic.
  - (c) The check itself starts a session.
- **Impact.** (a) shows the brief suffices on paper only. (b) one short session per run, with credentials and
  network. (c) makes `gov check` slow, costly and non-deterministic.
- **Reversibility.** High.
- **Cost.** (b) a few cents per run.
- **Recommendation.** (b).
- **Confidence.** Medium-high for (a) as the check; medium for adding the session.
- **Tests.** (a) `test_w1_25_resume.py`; (b) `test_w1_25_live_session.py`, removed if the answer is (a).

## Revision of an earlier suite

| Suite | Case | Kind | Reason |
|---|---|---|---|
| W1-07 | `test_a_reserved_command_not_yet_built_returns_not_implemented[checkpoint]` (via `NOT_BUILT` in `w1_07_support.py`) | planned revision, counted apart from rewrites (DEC-190) | planned: command implemented |

No other earlier test was changed. W1-07 after the revision: 227 passed.

## Readings of the test designer

- The other W1-07 cases still run `gov checkpoint --json` without arguments and hold it to the envelope and to an
  exit code other than 2; the tests here ask the same and that it writes nothing.
- "Commits since" is tested with a limit of 2 and 3 further commits, so it holds whether the count starts at the
  commit that carries the checkpoint or at the head when it was written.
- A read (`--watch`, `--resume`, the family check) may write under `.gov-runtime/`; the snapshot leaves it out, as
  W1-07's does.
