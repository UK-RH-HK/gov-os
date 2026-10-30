You are the ticket lead for ticket `DAEO-0uhh` (`W2-64`, "W2-02's widening: the record validator through check-jsonschema; `docs/imported/` out of the schema check"), profile STANDARD, keystone 4, working only in the worktree `/home/usain/gov-os-worktrees/W2-64` on branch `w2/W2-64`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-0uhh.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-64"); W2-02's card ("#### W2-02"), whose paths and KPIs you inherit;
- DEC-872 (item 2), DEC-844, DEC-890 (item 1), DEC-831, DEC-833 (item 3), DEC-941 (item 1) and DEC-942 (item 1);
- lens G's report, `docs/assessment/2026-10/G-tools-glue.md`: finding F2 ("The schema check passes records that the kernel's own schemas refuse"), with its planted ticket, and the tools table's row for check-jsonschema;
- `src/gov/check/schema.py` whole (247 lines; `STANDALONE_TYPES`, `_validate`, `_resolve`, `check`), and the kernel schemas under `template/governance/kernel/schemas/`, above all `common.schema.json` and `close.schema.json`;
- check-jsonschema's entry in `governance/project/tool-registry.yaml` (0.38.2, pinned; read-only, not in your paths);
- W2-66's close record, `docs/close/DAEO-c1uz/CL-DAEO-c1uz.md` (its `evidence:` block), and what writes that block, `src/gov/close/evidence.py` (read-only).

## Why you start now

- **The schema check fails open.** `core-schema` runs a 169-line subset of the kernel's schemas. Lens G's planted ticket carried 7 schema errors, and `gov` found none (F2). check-jsonschema was chosen for this job and is pinned, but nothing calls it.
- **Every close passes through that check.** The close schema constrains only `task`. The evidence block that W2-66's close writes is checked by nothing. DEC-890 item 1 put that schema line in this ticket.
- **Block B, the memory chain** (DEC-941 item 1; REPLAN-W2 §2, row B). W2-02 is merged and closed, so its paths are free. W2-61's measure is re-run after each ticket of the chain, this one included.
- **Launched beside the others** (DEC-942 item 1). Every ready ticket is launched when no running ticket shares its files, or when the overlap is split by file. Your schema path is narrowed to the close schema for that reason (below).

## The decisions for this run

- **Your schema path is one file.** Before launch, the orchestrator narrowed the ticket's `template/governance/kernel/schemas/**` to `template/governance/kernel/schemas/close.schema.json`. The KPIs name only the close schema's evidence block.
  - W2-58 holds `path-map.schema.json`, and W2-78 adds new schema files of its own beside it.
  - If the full validator finds that another kernel schema refuses a real record on `w2/integrate`, return a package. It names the record, the schema file and the rule, and says whether the record or the schema is wrong. Never edit a record to fit a schema, and never loosen a schema so that a record passes.
- **Design first, short.** The ticket's paths hold no note, so you write it in your scratch: `.gov-runtime/scratch/lead/design.md`, at most a page, in behaviour; it is a plan, not code. It says:
  - **how a record's frontmatter reaches check-jsonschema:** as an instance, against its type's schema file, with the `$ref`s to `common.schema.json` resolved from the schema folder. The calls are batched per schema, never one process per record;
  - **the refusal:** each invalid record is named with its path and the failing rule (the schema path and the message). Nothing is summarised into a count alone;
  - **RED, never green:** check-jsonschema missing, failing to start, ending with an error that is not a validation result, or giving output the check cannot read. A version other than the registry's pin is named with both versions; the note says whether that is RED;
  - **`docs/imported/` is left out by name:** the check's output says the folder was left out as history (DEC-844), and no other folder is left out;
  - **the close schema:** the evidence block as W2-66's close writes it, as an object of stated fields. The fields are scope, base commit, head, tree, what ran, what was left out and why, every skip and the skip count, the failure text kept, and the JUnit XML file. A close record with an incomplete block is refused, and a close record written before W2-66, which has no block, still validates;
  - **what stays:** W2-02's KPIs. An unknown record type is still `SCHEMA_INVALID_TYPE`, a type with no schema file is still reported unmeasured, not green, and `STANDALONE_TYPES` keeps its meaning;
  - **the time:** `core-schema` runs at every close, so its time on this repository is measured before and after. Give both figures in your return.

  It goes into the test designer's and the engineer's briefs as text.
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort high`; its brief must not set `TMPDIR`), in `tests/acceptance/W2-64/`:
  - one case per KPI line, success and failure, plus the key edge cases (STANDARD);
  - **lens G's planted ticket** (F2: a field the schema refuses that the subset passed), in a temporary repository built from scratch. It is refused, with the record and the rule named;
  - **check-jsonschema absent from `PATH`,** and separately a planted stand-in that fails to run. Each is RED, never green and never a skip;
  - **`docs/imported/`:** a planted invalid record there does not fail the check, and the output names the folder as left out. The same record anywhere else fails;
  - **the close schema:** a close record with an incomplete evidence block is refused. W2-66's form validates, and a close record written before W2-66 (the designer finds one under `docs/close/`) validates;
  - **the live case:** every record at this worktree's head validates, the close records of `docs/close/` included;
  - **earlier acceptance tests that pin the subset's behaviour** (W2-02's among them; the designer checks): named in the README, never edited. Revising one is outside the designer's folder, so it is a package (DEC-866 where a superseded decision is the cause);
  - **KPI line 5** (W2-61's measure re-run after the merge) is not a test of this ticket. The README names it as the orchestrator's step after the merge.
- **The engineer gate: W2-58 closes first** (DEC-942 item 4). W2-58's merge changed `src/gov/check/schema.py`, and its close is pending.
  - Before the engineer starts, check that `grep -m1 '^status:' /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-5j8b.md` says `status: closed`.
  - Then check whether `git diff --name-only HEAD w2/integrate -- src/gov/check/schema.py template/governance/kernel/schemas/close.schema.json tests/unit/check` names anything. If it does, merge `w2/integrate` into this branch first, in one command that commits, with your trailers.
  - If W2-58 is not closed when the engineer is due: commit the tests, make a checkpoint, and return PACKAGES naming the wait. It blocks only the engineer.
- **The engineer** (fresh, launched sandboxed where its suites allow, `--effort high`) works only in the allowed paths: `src/gov/check/schema.py`, `template/governance/kernel/schemas/close.schema.json` and `tests/unit/check/test_schema*`. It reads the tool registry and never writes it. If the check's registration in `src/gov/check/runner.py` must change, return PACKAGES.
- **Fail closed:**
  - no record is skipped silently, and no folder but `docs/imported/` is left out;
  - a schema file that cannot be read or parsed is RED;
  - no refusal comes without the record and the rule;
  - no validator failure is reported as green.
- **Running beside you** (paths checked against yours, file by file):
  - **W2-58** (`DAEO-5j8b`, closing): its merge changed `src/gov/check/schema.py`. It holds `template/governance/kernel/schemas/path-map.schema.json`, `governance/project/path-map.yaml`, `src/gov/guard/{protected,heldout,decide,reads}.py`, `src/gov/launch/**`, `tests/unit/guard/**` and `tests/unit/launch/**`. Your engineer waits for its close (above).
  - **W2-78** (`DAEO-v4is`, next in block A): `template/governance/kernel/schemas/**` for new schema files of its own, `governance/project/records/**` and five readers in `src/gov/close/`. There is no file overlap once your path is narrowed. Its new record types arrive with its own merge, and your check is not made to know them in advance.
  - **W2-03** (`DAEO-ym8a`, merge-back): `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**`, `src/gov/check/citations.py` and `tests/unit/check/test_citations.py`. W2-55 follows it on the decision schemas.
  - **W2-05** (`DAEO-0z8c`, merge-back) holds `src/gov/**/*.py` for the git environment of git calls, and `src/gov/util/gitenv.py`.
    - It has changed `src/gov/check/{audit_validator,claims,pathmap,runner}.py`.
    - Its run 3 plans `src/gov/close/{repo,history,traceability,command,tool}.py`, `src/gov/guard/decide.py`, `src/gov/guard/reads.py` and `src/gov/cli/main.py`.
    - If your check runs git, leave how its git environment is built as it stands; the later merge takes the conflict.
  - **W2-61** (`DAEO-iw1f`) holds `src/gov/retrieval/measure.py`. Its script lands before your merge, so that KPI line 5 can be run.
  - **W2-60a** holds `src/gov/launch/{launcher,role,record}.py`, and W2-56 holds `launcher.py`, `sandbox.py`, `environ.py` and `src/gov/codeintel/__init__.py`.
  - **W2-71** holds `src/gov/secrets/**`. **W2-77** holds `src/gov/close/nightly.py`.
  - **W2-67** holds `tests/unit/close/**`, `tests/unit/guard/**` and `tests/conftest.py`.
  - **W2-68 and W2-57** (closing and queued) hold `src/gov/close/{batch,fingerprint,command,repo,serial}.py`, `src/gov/doctor/command.py` and `src/gov/store/**`.

  Do not touch any of these. If your design needs a change there, return PACKAGES.
- **Verification:** in the close's form, under the lock, with the retention option and the disk gate first.
  - **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), you and your workers run no suite, no full run and no rebuild. Wait, and go on the moment it is gone. Every full run also waits for the verification lock.
  - **A close's quiet window:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, start no worker and no suite.
  - **The 01:00 cut-off (owner, DEC-939 item 6):** from about 01:00, start no full verification run that `nightly_estimate.py estimate` says cannot finish before 02:00. Wait for the nightly to end.
  - **Every rebuild** runs as `flock /tmp/gov-os-rebuild.lock …` (DEC-939 item 2).
  - **`core-schema` GREEN** in `gov check --json` on this worktree's code, with its time before and after your change.
  - **Known:** W2-54's green-here cases may time out under load in a plain full run (row W2-L429); re-run them alone. W1-46's and W1-19's cases run in your serial phase.
  - Any other red is named with its cause.
- **No review (STANDARD).**

## This run's order

1. The design note (yours, in scratch).
2. Tests first (the test designer), then **check red yourself.**
3. The engineer gate: W2-58 closed, then `w2/integrate` merged in if it changed your files.
4. The engineer.
5. Rebuild and verify in full.
6. **Return** DONE or PACKAGES. DONE means the branch is ready to merge. KPI line 5 is the orchestrator's after the merge, once W2-61's script has landed. Name it that way in your return.

**Estimate:** about 120 lines; about 6 hours with the full run.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
