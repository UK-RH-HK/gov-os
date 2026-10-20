You are a fresh product-spec worker. Ticket: DAEO-zflj (W2-02), profile STANDARD, ticket mode. You work only in the worktree `/home/usain/gov-os-worktrees/W2-02` on branch `w2/W2-02`. You are a headless session: nobody answers questions while you work, and only your final message is read. Your task is one decided change: the least extension of core-schema's shape check, and the adoption verdict's schema with its required list of named conditions.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-zflj`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-02` and `w2/W2-02`), and `git log --oneline -1` (expect `6aaf1859`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Your session has a hard limit of two hours: **commit before you run any long suite** (the full builder suite, any acceptance suite other than W2-02's).
- **The code under test (DEC-732, owner):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase in this worktree. A correction is a new commit.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. A test that needs a repository builds a temporary one. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. You need no rebuild.
- Never write under `src/gov/close/**`, `tests/unit/close/**` or `template/governance/kernel/checks/product-traceability-trailers.yaml` (another ticket's, W2-01).
- **Never edit `tests/acceptance/**`** (MR-3). The acceptance tests stand as written (DEC-749 item 3).
- Write only inside the ticket's `allowed_paths`, and for this task only: `src/gov/check/schema.py`, `template/governance/kernel/schemas/adoption-verdict.schema.json` (and a copy under `schemas/` only if one exists there; today none does), and `tests/unit/check/test_schema*` (builder tests).
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status `AUTH_REQUIRED`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.

## What you read

- The ticket file `.tickets/DAEO-zflj.md` (read-only): its KPI lines, its `allowed_paths`, and its sources (DEC-441, CAP-44.h, DEC-730).
- `docs/DECISION_REGISTER.md`: DEC-741 (part I (ii) and answers F and G), DEC-722, DEC-565, DEC-685's neighbours only as needed.
- `src/gov/check/schema.py` (you change it): `_SHAPE_KEYWORDS`, `_JSON_TYPES`, `_resolve`, `_shape_fault`, `_validate_shapes`.
- `template/governance/kernel/schemas/adoption-verdict.schema.json` (you change it) and `common.schema.json` (its `$defs`, among them `decision_id`).
- The acceptance suite `tests/acceptance/W2-02/` (read only): its `README.md` (the sections "Success 1, the adoption verdict's named conditions" and "How the cases find the keys"), `test_w2_02_verdict_conditions.py`, `test_w2_02_record_types.py`, and `w2_02_support.py` (`the_condition_keys`, `conditions_for`, `condition`, `names_field_or_part`). The cases find the schema's keys **by content**, so read how before you choose them.
- `tests/unit/check/test_schema_record_types.py` (the builder tests of this ticket; you add yours there or in a new `tests/unit/check/test_schema_shapes.py`).

## The decision (DEC-749, delegated by the orchestrator, 2026-10-17; staged for the owner's commit, not in this worktree's register; apply it as written here)

1. **P-6 (a).** Extend core-schema's shape check in `src/gov/check/schema.py` **by the least that measures the verdict's conditions**:
   - `type: array` with `items` (each item is measured against the items' shape);
   - `type: object` with `properties` and `required` (a required key missing is a fault; each stated key present is measured against its shape);
   - **one** conditional: `if`/`then` where the `if` holds a `const` on a property (e.g. a state that is `accepted`), so that an `accepted` condition requires its owner entry (the `then` gives `required`).
   - `$ref` inside these nested shapes resolves as the top-level one does today (the schema's own `#/$defs/…` and `common.schema.json#/$defs/…`).
   - **Every other keyword stays a fault (fail closed):** a shape with a keyword the check does not read, or a type it does not know, is still "has a shape the check cannot measure", at every depth. An `if` that is not a `const` test, or an `if` without `then`, is a fault too. No keyword is silently ignored.
   - **Findings keep naming the top-level field:** a fault anywhere inside `conditions` is a `SCHEMA_INVALID_FIELD` finding whose `field` is `conditions` (the top-level key); the message may say where inside it (for example `conditions[1]: missing 'state'`). Today's codes and today's findings for string and boolean fields stay exactly as they are.
   - Builder tests in `tests/unit/check/test_schema*`: each new keyword's pass and fault (an array item that faults; an object missing a required key; an object key of the wrong shape; the conditional both ways; a nested unknown keyword still a fault; a non-list where `type: array` stands; a non-object where `type: object` stands), and that an existing string/boolean case is unchanged.
2. **The verdict's schema (DEC-741 I (ii), item 4 of DEC-746).** `template/governance/kernel/schemas/adoption-verdict.schema.json` keeps its three CAP-44.h values and gains **a required list of named conditions**: each condition an object that requires its name, its source item and its state, the state one of exactly `met`, `not met`, `accepted`; an `accepted` condition requires the owner entry (a DEC id, use `common.schema.json#/$defs/decision_id`) that accepts it. Not an optional, unconstrained field. Rewrite the schema's `description` so it no longer says the conditions are open. The schema states the shape only: whether the verdict agrees with its conditions is W2-52's and W2-28's, not this ticket's; do not encode it. Use only the keywords item 1 measures. Mind the suite's key lookup: exactly one item key holds the word `name`, exactly one holds the word `source`, and **exactly one** item key other than the state has a `pattern` that takes `DEC-741` and refuses `the owner said so` (so the source item gets no pattern that also takes `DEC-741`; the records use the source item `CAP-44.h`).
3. Run 2's tests stand; nobody edits them. **If you find a case that cannot pass with a sound schema** (the lead named the key-name lookup and the source item's pattern as risks), stop before you bend the schema to it, and return status PACKAGES naming the case, why, and the options.
4. The estimate is about 250 lines in all. Keep `schema.py` small and readable, in the style of the file (its comment density and idiom).

Never make the check fail open: every failure case must still refuse, and a shape the check cannot read is never a pass.

## Runs, in the foreground, to their end, never with `-x`

1. `PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -c "import gov; print(gov.__file__)"`.
2. `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -m pytest tests/acceptance/W2-02 -q -p no:cacheprovider -rs` (all green expected).
3. `PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -m pytest tests/unit/check -q -p no:cacheprovider` (all green).
4. core-schema in this worktree's root, as `gov check` runs it: `cd /home/usain/gov-os-worktrees/W2-02 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -m gov.check.schema; echo exit=$?` (KPI: green here; the extension must not turn any record of this repository red, e.g. a probe or audit-report record whose schema now has nested shapes measured). If it is not green, find why before you commit.
5. Commit (below).
6. After the commit: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src timeout 3000 python3 -m pytest tests/unit -q -p no:cacheprovider`, and report its counts. If it shows a failure your change caused, fix it in a new commit and say so.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit, and say so. Never `--no-verify`, never `core.hooksPath`.

Commit only the files you changed (named with `git add <path>`, never `git add -A`), in one commit, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-02 (DAEO-zflj): the shape check measures lists, objects and one conditional; the verdict's named conditions" --trailer "Task: DAEO-zflj" --trailer "Role: product-spec" --trailer "Implements: DEC-741" --trailer "Implements: DEC-441" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

A commit message cites a decision id only if the decision register records it (DEC-463): DEC-749 and DEC-746 are not yet in this worktree's register, so name them in neither the subject nor a trailer (nor in code comments; cite DEC-741 there). After the commit run `git log --oneline -2`, `git log -1 --format=%B`, `git show --stat HEAD` and `git status --short`, and quote them.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | LEAD_CHECKPOINT | AUTH_REQUIRED, and one line of why>
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

In those fields: your commit's hash and trailers; the lines added and removed per file; the keys you chose and the shape of a condition as built; the result of each run with counts; core-schema's exit here; the `gov.__file__` line. Refused twice for the same call: stop and say so.
