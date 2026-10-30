You are a fresh engineer. Ticket: DAEO-0uhh (W2-64, "W2-02's widening: the record validator through check-jsonschema; `docs/imported/` out of the schema check"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-64` on branch `w2/W2-64`. You implement the ticket until its acceptance tests pass.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0uhh','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (name any file you made outside this worktree; never delete it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-0uhh`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-64` and `w2/W2-64`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. **Commit your work before you run any long suite.**
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **Policy 2 (DEC-820):** reads are open: the whole repository, git history, other worktrees. Only four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle; (c) the counterpart's work on this ticket: **you never read `tests/acceptance/W2-64/`**, by any tool (no Read, cat, grep, glob or retrieval result of it); you may run those tests and see their names, results and failure messages, never their source; (d) the hidden half of any evaluation set, by whoever is measured by it. Writes stay inside your paths.
- **Read refusals (DEC-849):** the guard may still refuse some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and **count the refusals you met in your return**. Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one. Never read `.claude/settings.json`.
- **Memory (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Drop unread any retrieval result under `tests/acceptance/W2-64/`. Say in your return whether you used `gov retrieve`.
- **The guard's command forms (DEC-941 item 4a):** the guard refuses a shell command it cannot read whole. No shell variable as a write target: use literal paths; no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. Write files with the Write and Edit tools and literal absolute paths; put anything longer in a script under `/home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/eng/` and run that file. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- No subagents that write. **Install nothing** (check-jsonschema 0.38.2 is installed at `~/.local/bin/check-jsonschema`; a tool you need beyond it is returned as a package). Read `governance/project/tool-registry.yaml` by name; never write it. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`, and never `tests/acceptance/**`.
- **Never copy the repository** or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). A builder test that needs a repository builds a temporary one from scratch with single named files. No clone or programme file under any `.gov-runtime/` folder. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** in anything you write under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **The machine:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` or `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, run no suite (at most a single test file); wait with short checks (never longer than a few minutes in one call) and go on the moment it is gone. You run this ticket's acceptance tests, the unit tests under `tests/unit/check/` and the earlier acceptance files that exercise the schema check; never the full suite (the lead runs it). Never `-x`.
- **Your temporary folder:** keep the sandbox's own temp folder. Keep pytest's own retention (no `--basetemp`). **Budget (DEC-898):** your share is 8 GB and 400,000 files and folders outside the tracked tree. Clean up every temporary tree you make; give `du -sh` and `du -s --inodes` of what you used in your return. Past the budget: stop and return.
- **On an authentication or access error:** stop and return with status AUTH_REQUIRED.
- Your time budget is about 90 minutes.

## What you read

- The ticket file `.tickets/DAEO-0uhh.md` (read-only): its KPI lines and its `allowed_paths`.
- Its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-64"), and W2-02's card ("#### W2-02"), whose KPIs stay.
- The decisions: DEC-872 (item 2), DEC-844, DEC-890 (item 1), DEC-831, DEC-135 (proportion), DEC-612 (the success form of a check's output), in `docs/DECISION_REGISTER.md`.
- Lens G's report `docs/assessment/2026-10/G-tools-glue.md`, F2 and R2 (a).
- The code the ticket touches: `src/gov/check/schema.py` whole; the kernel schemas under `template/governance/kernel/schemas/` (above all `common.schema.json`, `close.schema.json`); how `src/gov/check/runner.py` reads a check's output (read-only: if the check's registration there must change, stop and return a package); `src/gov/close/evidence.py` and `src/gov/close/command.py` (`_scope_evidence`), which write the close record's evidence block (read-only); the close records under `docs/close/`; check-jsonschema's entry in `governance/project/tool-registry.yaml`.
- The existing unit tests `tests/unit/check/test_schema*` and the earlier acceptance suites that exercise the schema check (W2-02, W2-54, W1-26, W1-30, W2-59, W2-66), which you run.

## The behaviour (the lead's design note, the agreed behaviour)

# W2-64 design note (lead, run 1): the record check through check-jsonschema

Behaviour, not code. Sources: DEC-872 item 2, DEC-844, DEC-890 item 1, DEC-831, lens G F2/R2 (a).

**1. How a record reaches the validator.** `core-schema` keeps its reading of records as today: every `*.md`
under `.tickets/` and `docs/` whose first line is `---`, its YAML frontmatter, its `type` (a record in
`docs/audit/` with no `type` is an audit report). Each record's frontmatter is written out as one JSON instance
(dates and timestamps as their ISO text) into a temporary folder the check removes when it ends. The instances
are then validated by check-jsonschema against their type's schema file in the schema folder of each kernel
layout the project holds (`template/governance/kernel/schemas/`, `governance/kernel/schemas/`). The
`$ref`s to `common.schema.json` resolve from that same folder: check-jsonschema resolves a relative `$ref`
against the schema file's own location (probed by the lead: the ticket schema's `state_class` enum, which
lives in `common.schema.json`, is applied). **One check-jsonschema process per schema file per layout,
with all of that schema's records as its arguments; never one process per record.** The `-o json -v` form
gives a readable result: on a batch that passes, `status: ok` and `checked_paths` (every instance); on a
batch that fails, `successes` and `errors` (each with `filename`, `path`, `message`) and `parse_errors`.
Every instance the check wrote must be accounted for in that answer, passed or refused; an instance the
answer does not name is RED, not a pass.

**2. The refusal.** Each error is a finding on the record it belongs to, named by its repository path (never
the temporary file's). It names the rule: the schema file, the place in the record (the validator's path, as
`$.deps[0]`) and the validator's message. A record with several errors has several findings; nothing is
summarised into a count alone. Today's finding shapes stay, so that the consumers keep reading them: `code`,
`path`, `field` (the top-level key the error is under) and `message`; a missing required property stays
`SCHEMA_MISSING_FIELD`, any other refusal is `SCHEMA_INVALID_FIELD`. (check-jsonschema 0.38.2's JSON answer
gives the record's path, not the schema's keyword path; the rule is named by the schema file, the record's
path and the message.) A finding under both layouts is given once, as today.

**3. RED, never green.** Each of these is a finding, the check exits non-zero, and `gov check` shows
`core-schema` RED (hard-block):
- check-jsonschema not found on `PATH`: one finding that names the tool and says the records were not measured;
- check-jsonschema failing to start (not executable, killed, an OS error);
- an answer that is not the JSON above (a schema that check-jsonschema cannot build or parse prints text and
  exits 1; that is RED, never "no findings"), an exit code other than 0 with no readable error list, an exit
  of 0 with errors, any `parse_errors` entry, or an instance left unaccounted;
- a schema file the check needs that cannot be read or is not valid JSON (checked by the check itself before
  the call);
- **the version.** The check reads the installed version (`check-jsonschema --version`) and the pin of the
  tool registry (`governance/project/tool-registry.yaml`, the `check-jsonschema` entry). **A version other
  than the pin is RED**, and its finding names both versions: the pinned validator is the judge (DEC-074),
  and an unpinned one may read the same schema differently. A registry that exists but cannot be read is RED.
  A project with no registry, or a registry with no `check-jsonschema` entry, states no pin: the check
  validates as usual and its output says that no pin was stated (it is not RED; doctor reports the
  registry's absence). The check never writes the registry.

**4. `docs/imported/` is left out by name.** Every record under `docs/imported/` is left out of the check, as
history (DEC-844). The check's output says so: on a pass, the success form `gov check` reads as green
(`{"ok": true, "result": {...}}`, DEC-612) whose result names `docs/imported/` as left out and why (history,
DEC-844), with the count of records validated; on a refusal, the same statement beside the findings
(`{"findings": [...], ...}`). No other folder is left out. A file that opens with `---` but whose frontmatter
cannot be read (no closing line, a YAML error, not a mapping), or that cannot be read at all, is a finding,
not a silent skip (none on this head today). A file whose first line is not `---` is not a record, as today.

**5. The close schema** (`close.schema.json`, the only schema file in this ticket's paths) states the evidence
block that W2-66's close writes (`src/gov/close/evidence.py`, `src/gov/close/command.py`), as an object whose
stated fields are required and typed:
- `scope`: `scoped` or `full`; `why_full`: a list of reasons, each an object with a non-empty `reason` and
  optionally `paths` (a list of paths); when `scope` is `full`, `why_full` is not empty;
- `base`: a commit id, or null (a close whose base is unknown, `why_full` `BASE_UNKNOWN`, as DAEO-uzme's);
  `head` and `tree`: full 40-character ids;
- `changed`: a list of paths; `selected` (what ran): a list of objects with `target` and `why` (a list of
  objects with `reason`); `left_out`: the same form, each with its `why`;
- `skips`: a list of objects with `test` and `reason`; `skip_count`: an integer, zero or more;
- `failures`: a list of objects with `test` and `text` (the failure text kept);
- `junit_xml`: a list of paths (each run's JUnit XML file).
The fields the close writes beside them are stated with their types and are not required:
`per_test_timeout` (an integer), `distribution` (a string), `tmp_path_retention_policy` (a string), and
W2-68's `code_fingerprint` and `records_fingerprint` (a string or null) and `reused` (an object). Other keys
are allowed, so that a later close field does not turn every close record RED. A close record with an
evidence block that lacks a required field, or has one of the wrong shape, is refused. `evidence` itself is
not required, and may be null: a close record written before W2-66 has no block (DAEO-0rfi, -7rr2, -juee,
-kl5e, -zflj), and `gov close` writes null for a ticket judged on its evidence with no test run. `task`
stays as today. The schema file defines what it needs itself (`common.schema.json` is not in the paths) or
refers to `common.schema.json`'s existing definitions (`full_commit_id`, `commit_id`).

**6. What stays (W2-02's KPIs).** A record whose `type` is absent or not a string is still
`SCHEMA_INVALID_TYPE`; a type the check does not know is still `SCHEMA_UNKNOWN_TYPE`; a type whose schema file
is in neither layout is still reported unmeasured (`SCHEMA_UNREADABLE`), never green. `STANDALONE_TYPES`
keeps its meaning: a standalone type's record owes only what its own schema requires (no shared frontmatter
unless its schema takes it in), and every other record owes the shared four fields (`id`, `type`, `status`,
`state_class`) even where its schema does not ask for them. The type map is unchanged (W2-78's new types come
with its own merge). The check's command (`python3 -m gov.check.schema`) and its registration
(`template/governance/kernel/checks/core-schema.yaml`, `src/gov/check/runner.py`) are unchanged. The
`check(root)` function keeps returning the list of findings.

**7. Time.** Before (the subset, this worktree's head, light load): `python3 -m gov.check.schema` 2.2 s
(three runs: 2.27, 5.49 under load, 2.16 s). The lead's scratch sweep (768 records, 13 schema files, one
process each, sequential) took 4.5 s with no error on this head. Target: under 10 s on this repository;
the engineer may run the per-schema processes concurrently. Measured again after the change, both figures in
the return.

**Live state (lead's sweep, head 135ae00947cb):** every record outside `docs/imported/` validates under the
full validator, the 18 close records included (13 with W2-66's block, 5 without). The 5 records under
`docs/imported/` are the ones lens G's sweep found failing (4 of them, by their ids).

**Known collision (for the test designer to confirm and list):** earlier acceptance tests run `core-schema` in
environments whose `PATH` holds no check-jsonschema (W2-54's support sets `PATH=<workdir>/bin:/usr/bin:/bin`
and a throwaway `HOME`). With this change they see RED by design. They are named in the README, never edited;
the lead returns them as a package.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/check/schema.py`, `template/governance/kernel/schemas/close.schema.json`, `tests/unit/check/test_schema*`.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests go in `tests/unit/check/test_schema*.py`, as regression evidence only. Existing builder tests there that pin the subset's internals may be revised, each change named in your return.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines and the design note. **Fail closed:** no record skipped silently; no folder but `docs/imported/` left out; a schema file that cannot be read or parsed is RED; no refusal without the record and the rule; no validator failure, missing tool or unreadable answer reported as green.
- Run, each to its end, in the foreground: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src python3 -m pytest tests/acceptance/W2-64 -q -p no:cacheprovider -rs` until it passes; then `tests/unit/check`; then the earlier acceptance suites that exercise the schema check (W2-02, W1-26, W1-30, W2-54, W2-59 and W2-66's files that name `core-schema` or `gov.check.schema`). Name every red case in an earlier suite with its cause; one that fails because check-jsonschema is not on its `PATH` is expected (the lead returns it as a package) and is not to be worked around in the code.
- Measure the check's time on this repository: `python3 -m gov.check.schema` in the worktree root (with the PYTHONPATH above), three runs, after your change; give the figures (before: about 2.2 s).

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if one is there, stop and return. Commit only your paths, with the trailers in the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-0uhh" --trailer "Role: engineer" --trailer "Implements: DEC-872, DEC-844, DEC-890" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then `git log --oneline -2` and `git status --short`, quoted in your return.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

In those fields give: the sandbox check's result; the `gov.__file__` line; your commit's hash (12 digits) and trailers; the files changed with lines added and removed; each suite you ran with its counts; the check's time after the change; whether you used `gov retrieve`; the read refusals you met (count); your scratch measure. Refused twice for the same call: stop and say so.
