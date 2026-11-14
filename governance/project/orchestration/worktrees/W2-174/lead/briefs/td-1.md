# Brief: independent test designer, W2-174 (DAEO-zmo4), run 1 batch 1: the acceptance cases

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-zmo4 (W2-174), profile STANDARD,
class C2. Headless: only your last message is read.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-174-tests |
| branch | w2/W2-174-tests (from f2b1d38af) |
| your context packet (gov context output, JSON: the ticket, KPIs, sources) | /home/usain/gov-os-worktrees/W2-174-tests/.gov-runtime/scratch/brief/td-context.md |
| the ticket (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-zmo4.md |
| the approach (why option (d)) | /home/usain/gov-os-worktrees/W2-174-tests/governance/project/orchestration/packages/ADOPT-VERIFY-1/APPROACH.md |
| the decision register (grep by id only) | /home/usain/gov-os-worktrees/W2-174-tests/docs/DECISION_REGISTER.md |
| scratch | your sandbox's own `$TMPDIR` only (`/tmp` is read-only in the sandbox) |

Your allowed paths: `tests/acceptance/W2-174/**` only (new: the ticket's acceptance folder). NOT `src/**`, NOT
`template/**`, NOT `tests/unit/**` (the KPI lines' Verify clauses name `tests/unit/adopt/test_w2_174_*.py`: those are the
engineer's unit cases; yours are the acceptance cases that check the same lines independently).

An engineer works on the same ticket in `/home/usain/gov-os-worktrees/W2-174` at the same time: never read that tree or
its branch's commits after f2b1d38af (the counterpart's work, DEC-820). Write from the KPI lines and the interface below.

## Read first
- The ticket in full: its eight KPI lines (S1-S5, F1-F3), Interface, Rabbit holes, and the two owner sections at the end
  (S5 was widened by DEC-1148 (2); the skill line moved to W2-88a by DEC-1150 (1), so there is no skill case here).
- `src/gov/brief/build.py` (read only): `kpi_rows` (line ~109), `ready_check` (~163), `build` (~317: the facts file,
  `BRIEF_FACTS_MISSING`, `PLACEHOLDER_LEFT`), `_templates` (~279: a repository's templates at
  `template/governance/kernel/templates/` or `governance/kernel/templates/`).
- `tests/acceptance/W2-152/` (README, `conftest.py`, `w2_152_support.py`): the form of a README `gov accept` reads, and
  how fixture repositories with tickets, templates and a facts file are built in `tmp_path` and `gov brief` is run as a
  subprocess (`python3 -B -m gov.cli.main ... --root <repo>`, `PYTHONPATH=<tree>/src`, empty `HOME`).
- `template/governance/kernel/schemas/facts.schema.json` and `governance/project/facts.yaml` (the shape S5 writes).

## The interface (the ticket's "Interface" section, plus the lead's decisions where it is silent; the same text goes to the test designer and the engineer)

From the ticket (read it in full):
- `src/gov/adopt/verify_pass.py`: `missing(root) -> list[{"ticket": <id>, "labels": [<label>, ...]}]`;
  `apply(root, answers_path, session, today) -> list[str]` (the ids of the tickets changed). Both read KPI lines with
  `gov.brief.build.kpi_rows` (imported, never changed). Errors are `gov.cli.errors.GovError` with codes
  `VERIFY_PASS_UNKNOWN_TICKET`, `VERIFY_PASS_CLOSED`, `VERIFY_PASS_UNKNOWN_LABEL`, `VERIFY_PASS_UNANSWERED`,
  `VERIFY_PASS_EMPTY_CLAUSE`.
- Flags on `gov adopt` (no `--lite` needed): `--verify-list`, `--verify-apply <answers-file>`; `--root` is gov's global flag.
- Answers file (YAML, outside the repository): `{<ticket id>: {S1: "<clause>", F2: "<clause>"}}`.
- Marker: one front-matter line `verify_pass: <YYYY-MM-DD> <session>`, added just before the closing `---`.
- A KPI line given as a plain string gets ` Verify: <clause>` appended; a `{line, verify}` mapping is never edited.

The lead's decisions (L1-L9; DEC-1157 lets the lead state these at the start):
- L1 `--verify-list` output: gov's usual result dict, `{"missing": [{"ticket": "<id>", "labels": ["S2", "F1"]}, ...],
  "text": "<lines>"}`; `text` is one line per ticket, `<id> <label> <label>...`, tickets sorted by id, labels in
  `kpi_rows` order; when no ticket lacks a verify, `missing` is `[]` and `text` is exactly `none`. Exit 0 in both cases.
  Listed: tickets whose front-matter `status` is `open` or `in_progress`. The id is the front-matter `id`.
- L2 `--verify-apply` result: `{"changed": [<id>, ...]}` (sorted), exit 0. A refusal is a `GovError` (gov's exit 1,
  the code on stderr, or in the envelope with `--json`), and nothing is written anywhere.
- L3 the marker's `<session>` is gov's global `--session` value (`args.session`, default `""`); `--verify-apply`
  without a non-empty `--session` is a usage error (argparse's, exit 2), nothing written; `<date>` is the UTC date of the run
  (`today` in the function). If the ticket already carries a `verify_pass:` line, that line's value is replaced in place
  (still exactly one such line).
- L4 checks, all before any write, over every entry: an answers key that is no ticket id under `.tickets/` ->
  `VERIFY_PASS_UNKNOWN_TICKET`; a ticket with `status: closed` -> `VERIFY_PASS_CLOSED`; a label that is not one of the
  ticket's lines lacking a verify (no such S<n>/F<n>, or that line already has a verify) -> `VERIFY_PASS_UNKNOWN_LABEL`;
  a named ticket with a line lacking a verify that the file does not answer -> `VERIFY_PASS_UNANSWERED`; a clause that
  is not a string, is empty or whitespace, or is only TBD, TODO, n/a or none (any case, ignoring surrounding whitespace
  and trailing `.`) -> `VERIFY_PASS_EMPTY_CLAUSE`. An answers file missing, not YAML, or not a mapping of mappings ->
  `VERIFY_PASS_ANSWERS_UNREADABLE`.
- L5 the edit is text-only (no YAML dump). The clause is appended inside the scalar: a plain scalar gets
  ` Verify: <clause>` at its end; a single- or double-quoted scalar gets it inside its quotes, escaped for that style.
  Where a plain scalar cannot hold the clause (for example the clause holds `: ` or ` #`), that one item may be turned
  into a single-quoted scalar (that item's bytes only). After editing in memory, the tool re-reads each edited ticket
  with the same loader and checks that `kpi_rows` gives each answered label exactly its clause and every other
  front-matter value is unchanged; otherwise it refuses with `VERIFY_PASS_EDIT_FAILED` and writes nothing. A block or
  folded scalar the tool cannot extend is refused the same way.
- L6 the facts step (S5): `gov adopt --facts --root <repo>` (no `--lite` needed) calls
  `gov.adopt.facts.write_default(root: Path, today: datetime.date) -> {"path": "<repo>/governance/project/facts.yaml",
  "written": true|false}`; the command passes the UTC date of the run. With no facts file it writes one; with one it
  writes nothing (`written: false`), the file byte-identical.
- L7 the facts file written: validates against `template/governance/kernel/schemas/facts.schema.json`;
  `ready.new_since` is `today` as a quoted ISO string (`'2026-11-13'`); every other value is a product default, with no
  path or name of the repository it is written into (the commands are `gov ...` forms). `wait_for` is
  `gov wait {EXIT_FILE}` (check `gov wait --help`): `gov wait` is on this base (caf96ed0f). A command with no product
  form is a named placeholder: its `run` (and `check`) is `{UNSET_<NAME>}` with `<NAME>` the command's name upper-cased,
  so `lead_verify` is `{UNSET_LEAD_VERIFY}`, and `gov brief` refuses it as `PLACEHOLDER_LEFT` naming `UNSET_LEAD_VERIFY`
  for any role whose template names `{CMD:lead_verify}` (the lead's). Whether `launch_worker` has a product form
  (`gov launch`) is the engineer's call; tests check only that each command's `run` starts with `gov ` or is exactly
  `{UNSET_<NAME>}`, that `lead_verify` is `{UNSET_LEAD_VERIFY}` and that `wait_for` starts with `gov wait`.
- L8 scope (F3): `verify_pass.py` opens nothing outside `<root>/.tickets/` and the answers file; it imports no network
  or model package (no `socket`, `http`, `urllib`, `requests`, `httpx`, `anthropic`, `openai`, `subprocess`). The facts
  step is not the verify pass (the ticket's "Widened by the owner" section).
- L9 untouched: nothing under `src/gov/brief/`, `template/governance/kernel/templates/` or
  `template/governance/kernel/schemas/` changes; no adoption stage changes (`src/gov/adopt/stages.py` stays as it is).

## The work
1. Write `tests/acceptance/W2-174/` with a README mapping every KPI line (S1-S5, F1-F3) to its cases in `gov accept`'s
   form (as W2-152's README does), a `conftest.py` and a support module for the fixture repositories. Every case runs
   on fixture repositories in `tmp_path`, never this repository. Cover at least:
   - S1: three tickets (all lines verified in both forms; one open or in-progress with two plain lines lacking a verify,
     for example S2 and F1; a closed ticket with a line lacking one) -> `missing` and `text` name exactly the second
     ticket's two labels; the all-verified repository gives `missing == []` and `text == "none"`, exit 0. Through the CLI
     (`gov adopt --verify-list --root <repo>`) and the function.
   - S2: a ticket with YAML comments (in the front matter, including on a KPI line and between keys), keys in a
     non-alphabetical order, and five KPI lines (plain, single-quoted, double-quoted, one `{line, verify}` mapping);
     after apply, a byte diff of the file shows only the appended ` Verify: <clause>` texts and the one added
     `verify_pass: <date> <session>` line before the closing `---`; the mapping is byte-identical.
   - S3: after apply, `gov.brief.build.ready_check` on the applied ticket has no `KPI_NO_VERIFY`, and
     `gov brief engineer <ticket> --root <repo>` exits 0 (the fixture carries its own filled facts file and the kernel
     templates, a READY ticket otherwise, as W2-152's `ready_front` is).
   - S4 and F1: one case per refusal code of L4 (unknown ticket, closed ticket, unknown label, an already-verified
     label, an unanswered line, an empty clause, a `TBD` clause, and `TODO`, `n/a`, `none`), each refused with its named
     code and the whole fixture tree byte-identical (hash every file before and after); a file of nine good entries and
     one bad one leaves the tree byte-identical; a ticket the file does not name is never edited; no ticket is marked
     `verify_pass` while a line of it lacks a verify.
   - S5: a repository without a facts file, after `gov adopt --facts --root <repo>`, has a file that validates against
     the kernel schema (`jsonschema`), whose text has `new_since` as a quoted ISO string equal to the UTC date of the run,
     with no value naming the fixture repository's path or folder name or `/home/`, every command `run` starting with
     `gov ` or exactly `{UNSET_<NAME>}`, `lead_verify` `{UNSET_LEAD_VERIFY}`, `wait_for` starting `gov wait`; `gov brief`
     there no longer answers `BRIEF_FACTS_MISSING`, and `gov brief lead <ticket> --run build` names
     `UNSET_LEAD_VERIFY` in a `PLACEHOLDER_LEFT` finding; a repository with its own facts file keeps it byte-identical
     and gets `written: false`. Also the function `write_default(root, today)` with a fixed date.
   - F2: `git diff --name-only f2b1d38af HEAD` of the tree under test names no file under `src/gov/brief/`,
     `template/governance/kernel/templates/` or `template/governance/kernel/schemas/` (skip only when the tree is not a
     git checkout, with the reason); the README notes that `tests/acceptance/W2-152` must still pass unchanged (the
     lead runs it).
   - F3: a fixture with a decoy file outside `.tickets/` (and one beside the answers file) is byte-identical after list
     and apply; `src/gov/adopt/verify_pass.py`'s imports (read with `ast`) name none of L8's packages; and, with
     `builtins.open`/`Path.open` watched in-process, list and apply open nothing outside `<root>/.tickets/` and the
     answers file (other than Python's own module loading).
2. Each case is red on the base (f2b1d38af) for its stated reason (the module, the flags or the function missing),
   except F2 (green on the base; say so). Record each case's red message on the base in your return (a short line each).
3. Lower nothing; add no skip, xfail, flaky or rerun mark. Prove that one planted break is caught: in a scratch copy, a
   stand-in `verify_pass.py` that writes the first ticket before checking the others must fail the nine-good-one-bad case
   (show it, then discard the stand-in; nothing of it is committed).

## How you run tests
Every pytest through the heavy slot, TMPDIR your sandbox's own `$TMPDIR`:
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-174-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-174-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <file or folder>[::<test>] -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
A whole-folder run adds `-m "not local_only" -k "not real and not green_here and not time_limit"`; name no case `real`,
`green_here` or `time_limit` and mark none `local_only`. A resource gate's refusal is a wait (relaunch when it opens).
Quote the count lines in your return.

## Searching
Read and Grep only; no `gov retrieve` or `gov context` in the sandbox. Search once, then once more in other words; answer
from what you read with path and line, or say "not found". Never open the evaluation sets' root, held-out material or any
hidden or memory-verdict folder.

## Forms that work
Write and edit with the Write and Edit tools and absolute paths. Anything longer than one line of shell goes in a script
under your `$TMPDIR`, run with `bash <file>`. Refused twice for the same call by the guard, the sandbox or a hook: stop and
say so; never work around a refusal. No merge, no push.

## Commit (your paths only; one or more commits)
```
git -C /home/usain/gov-os-worktrees/W2-174-tests commit -m "<subject>" --trailer "Task: DAEO-zmo4" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1130, DEC-1083, DEC-1050, DEC-1088, DEC-1121, DEC-1122" -- tests/acceptance/W2-174
```
Trailers in one final paragraph. Never `Role: owner` or `Decided-by:`. Before you return: tracked `git status --short` empty.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; each case with its red message on the base; any place where the
ticket or the interface above was unclear and how you read it; guard_refusals: none or a line each.
