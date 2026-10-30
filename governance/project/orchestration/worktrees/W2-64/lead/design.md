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
