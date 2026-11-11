# Brief: independent test designer, DAEO-61vm (W2-170), FULL — the memory audit's set record (run 1)

Budget: projection 15 USD.

You are a fresh independent test designer (MR-3). Ticket: DAEO-61vm (W2-170), profile FULL, class C2. You work only in
the worktree `/home/usain/gov-os-worktrees/W2-170-tests` on branch `w2/W2-170-tests` (DEC-963). You never read or write
the ticket's own worktree, `/home/usain/gov-os-worktrees/W2-170`. No implementation exists yet (`src/gov/memaudit/` is
absent): you write the acceptance tests **before** the engineer, from the ticket's KPI lines and its `## Interface`
section, and they must run red now for the right reason.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-170-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-61vm`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-61vm','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or
(b) failed, stop there and return (delete nothing). Then read `EMG-common.md` beside it.

## Standing rules

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-61vm`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-170-tests`,
  `w2/W2-170-tests`). If anything differs, stop and say so.
- **Writes:** only `tests/acceptance/W2-170/**` (and your scratch `.gov-runtime/scratch/td/`). Nothing else.
- **Code under test (DEC-732):** every test run uses this worktree's own `src/`:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-170-tests/src`, set per command. Quote in your return
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-170-tests/src python3 -c "import gov; print(gov.__file__)"`. Every child
  process a test starts gets that folder first on its `PYTHONPATH` (take it from the test's own environment / the
  repository root of the test file, never a hard-coded worktree path).
- **Searching (DEC-1065):** no `gov retrieve` and no `gov context` in the sandbox. Use the Read and Grep tools, naming
  the folder a search starts at; if a search does not answer, search again once in different words, then answer from
  what you read or say "not found". Grep the decision register only by id.
- **Policy 2 (DEC-820):** reads are open except secrets, the held-out material's contents, this ticket's implementation
  (none yet; never anything in `/home/usain/gov-os-worktrees/W2-170`) and the hidden half of any evaluation set. **Never
  open the real `~/gov-os-eval`, `~/gov-os-runs` or any run folder**, by hand or from a test (F3).
- **Command forms:** no shell variable or `$(…)` as a write target, no here-document, no `bash -c '…'`, no long inline
  `python3 -c`; anything longer than one line goes in a script file under
  `/home/usain/gov-os-worktrees/W2-170-tests/.gov-runtime/scratch/td/` written with the Write tool, then run.
  Foreground only. No checkout of another commit, reset, clean, amend, rebase, push, merge or install.
- **Refused twice for the same call: stop and say so; never work around a refusal.** Count refusals in your return.
- Budget (DEC-898): `TMPDIR=/tmp/gov-os-lead-W2-170` on every run; pytest's own retention
  (`-o tmp_path_retention_policy=failed`), never `--basetemp`. Give `du -sh` of your scratch at the end.
- Under `.gov-runtime/`, commit hashes as 12 digits, never 40 (DEC-911).
- On an authentication error return `AUTH_REQUIRED`.

## What you read (in this order)

1. **The ticket, authoritative:** `/home/usain/gov-os-worktrees/W2-170-tests/.tickets/DAEO-61vm.md`. Its `kpis`
   (six `success` lines S1–S6, five `failure` lines F1–F5, each with a `Verify:` clause) and its `## Interface`
   (sections 1–10). **The Interface is fixed:** you write tests to it, you never change or reinterpret it. A gap or a
   clash you find in it (between two sections, or with a KPI line) goes into your return as a package
   (`proposed_decisions`: question, options with cost, recommendation, confidence, what it blocks); write the test to the
   Interface's words where they are clear and leave the unclear point untested and named. Section 10's four readings
   are decided: `dropped/` is `hidden/dropped/`; **five** roles, never six; quotas at 36–39 files are "at most";
   the draw lists from `indep/AUDITS.log` and `indep/SEEDS.log`, `selection.json` an override read first.
2. **The context packet:** `/home/usain/gov-os-worktrees/W2-170-tests/.gov-runtime/scratch/brief/context-td.json`
   (the ticket text, its ten source decisions by hash, and supplementary chunks). Read each source decision by id in
   `docs/DECISION_REGISTER.md`: DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1069, DEC-820, DEC-896, DEC-1050,
   DEC-1073, DEC-1052.
3. **The three approved briefs** the set comes from: `governance/project/indep-briefs/memory-audit/writer.md` (the
   question file's form, the twelve categories, `drawn`, `sources`), `checker.md` (the notes' `## Questions` line form,
   section 5a's domain and subsystem), `auditor.md`. And `governance/project/orchestration/packages/MEMORY-AUDIT-1.md`.
4. **Today's interfaces the tool uses or is checked against** (read, to plant inputs they accept):
   `governance/project/path-map.yaml` (the `memory-verdict-2` entry under `evaluation_sets`, the
   `evaluation-sources` and `evaluation-fixtures` namespaces, the glob rule); `src/gov/util/parts.py`
   (`evaluation_sets`); `src/gov/retrieval/measure.py` (how it accepts a set from a sets root's map — S4's "the measure
   run on the planted set accepts it"); `src/gov/retrieval/lexical.py` (`ids_in`, `whole_id`);
   `src/gov/store/loader.py` (`fingerprints`, so you can plant a store file with a `fingerprints` row whose `head` is
   the audit commit); `governance/project/orchestration/tools/indep_launch.py` (stage B4, the selection rule, and
   `SEEDS.log`/`AUDITS.log` line forms); `governance/project/indep-walls/tree-exclude.txt`;
   `governance/project/test-map.yaml` and the scoped selection of `gov close` (find it under `src/gov/close/` or
   `src/gov/closure/`) for S6.
5. **The form of an acceptance folder:** `tests/acceptance/conftest.py`, `tests/acceptance/serial-only.txt`, and one
   recent folder's README map, e.g. `tests/acceptance/W2-32/README.md`; `gov accept` reads the map with
   `gov.accept.runner.parse_map` (`src/gov/accept/runner.py`): it must list every KPI line of the ticket (`S1`..`S6`,
   `F1`..`F5`, or `success-1`.. / `failure-1`..) against its cases.

## What you write

`tests/acceptance/W2-170/`: a README (what the tests reach, how to run them, the KPI map in the runner's form, the
expected-red table), a conftest and a support module that **plant everything under pytest's `tmp_path` (under
`TMPDIR`)** as Interface section 9 lists: a sets root with its own `governance/project/path-map.yaml` holding an
`evaluation_sets` block among comments; a git repository with at least two commits (an earlier one and the audit
commit), a `governance/project/retrieval.yaml` (pool on: `pool: {meaning_uncut: true}`; and a variant with it off), a
`governance/project/path-map.yaml` with the two evaluation namespaces, a `governance/project/indep-walls/tree-exclude.txt`
and the source files the planted questions cite; a runs dir with `indep/AUDITS.log` and `indep/SEEDS.log` (and, for
other cases, a planted `selection.json`); a planted pool folder `fixtures/evaluation/memory-pool/hidden/`; a store file
with a `fingerprints` row; a `gov` link inside a folder named `pin-<12 hex>`; a clean 40-question set (and 36–39
variants) in `fixtures/evaluation/memory-audit-<8 digits>/hidden/`; `XCHECK-r1.md`/`XCHECK-r2.md` notes. Set `HOME` for
every child process to a planted empty home under `tmp_path`, so `~` never reaches the real home.

Drive the tool the way its callers do: `python3 -m gov.memaudit preflight|void|declare --sets-root <root> --audit <A>
...` as a child process (exit codes and printed lines per Interface sections 1, 3 and 5), and, where a KPI line is
about a Python entry point (section 8), import it. **Collection must succeed while `gov.memaudit` does not exist**
(import it inside the test or via the child process), so the suite runs red by failing, not by erroring at collection.

Cover every KPI line by its own `Verify:` clause, at least:
- **S1:** ten planted defects, one per check, each refused with its own code (`PF-COUNT` .. `PF-IDEXISTS`, section 3),
  and the clean set ending exactly `PRE-FLIGHT: every check as expected` with exit 0; the scale rule of section 4 at
  36 to 40; the domain/subsystem tables of section 4 by first source path; `PF-DRAWN` both from a planted
  `selection.json` and from the derived lists (`AUDITS.log`/`SEEDS.log`, seed hash checked), and "lists cannot be had".
- **S2 / F4:** notes with 3 drops (exit 0, kept 37, scales recomputed, the 3 files under `hidden/dropped/`, nothing
  deleted), 5 drops (`VOID-COUNT`, exit 2, no `USED`, no `DECLARATION.json`), a drop leaving a domain at 3
  (`VOID-DOMAIN`); `DR-NOTES`, `DR-DONE`; the highest `XCHECK-r<n>.md` is the one read; `DROPS.json` keys.
- **S3 / F2:** `declare` writes the map entry, `DECLARATION.json`, the `declaration` ledger line, `USED`, the `used`
  ledger line, in that order (file mtimes in nanoseconds and ledger `seq`); every `DECLARATION.json` key of section 5
  with its value (bar and rounding for the planted n); a second `declare` exits 3, prints `USED`, writes nothing; pool
  off without `--decision`: `ok: false`, no `USED`, `DC-DECISION pool`, exit 1; with `--decision DEC-<n>`: ok and
  `USED`; the other `DC-` refusals write nothing.
- **S4 / F3:** the sets root's map gains exactly one `evaluation_sets.<A>` entry with the five roles, every other byte
  kept; equal entry left as is, different entry `DC-MAP`; `git status --porcelain` of the planted repository empty
  after every subcommand; the measure (`gov.retrieval.measure`) accepts the planted set from the sets root's map; a
  **file-access log** of a run shows no open of the real home's `gov-os-eval` / `gov-os-runs` (for example a small
  runner under `tests/acceptance/W2-170/` that installs `sys.addaudithook` for `open` events, writes them to a file,
  then runs `gov.memaudit` with `runpy`; your choice, stated in the README).
- **S5 / F1:** a planted question, gold answer, source path and heading each carrying a unique word: grep of every file
  under `runs/<A>/`, the sets root's map, captured stdout and stderr (including an `ERROR:` path, e.g. a malformed YAML
  that quotes the file's text) finds each 0 times; `say`'s refusal (exit 4, the exact `REFUSED:` line); a flag naming a
  folder under the sets root is refused (exit 4); the printed command line holds no `fixtures/` or `runs/`.
- **S6:** `test-map.yaml` places `src/gov/memaudit/**` → `tests/unit/memaudit/`, and the scoped selection for a planted
  change under `src/gov/memaudit/` names `tests/unit/memaudit/` and not the full suite; each subcommand `--help`
  exits 0; argparse errors exit 4.
- **F5:** `git diff --name-only <base>...HEAD` of the ticket's branch lists only allowed paths (base: the merge-base
  with `w2/integrate`; skip with a named reason when that ref is absent, never pass silently).

**Naming (DEC-1065):** whole-folder runs deselect `-m "local_only"` and `-k "real or green_here or time_limit"`. So
**no test name, class name, parametrize id or file name may contain `real`, `green_here` or `time_limit`** (write
"actual sets root", "true home", not "real"), or the case silently never runs. Mark `local_only` only a case that
cannot run in CI, and name it in the README.

Keep each case fast (the whole folder well under two minutes); no network; no GPU; no real store.

## Check and commit

1. `env HOME=/home/usain/gov-os-worktrees/W2-170-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-170-tests/src TMPDIR=/tmp/gov-os-lead-W2-170 python3 -m pytest tests/acceptance/W2-170 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
   (make the empty-home folder first): it must collect every case with no collection error and run red; quote the
   last line and the count of cases collected (`--collect-only -q` with the same filters, last line). Say which
   cases, if any, pass on today's code and why (S6's test-map case and F5 may; nothing about the tool may).
2. Check the README map with a small script under `.gov-runtime/scratch/td/` calling
   `gov.accept.runner.parse_map` on it: every one of S1–S6 and F1–F5 maps to at least one case; quote its output.
3. Commit only `tests/acceptance/W2-170/**`:

       git commit -m "W2-170 acceptance: the memory audit's set record, S1-S6 and F1-F5 from the KPI lines and the Interface" --trailer "Task: DAEO-61vm" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1069, DEC-820, DEC-896, DEC-1052" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-170

   `Implements:` lists only ids from the ticket's `sources:`; an id you need that is not there goes in `discoveries`.
   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last, complete in itself. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why.
In `evidence`: the sandbox check's result, the `gov.__file__` line, the collect and run last lines, the map check's
output, the commit hash with its trailers, `du -sh` of your scratch. In `tests`: cases per KPI line and the expected-red
table in short. Also say the read refusals met (time, form, reason) and every Interface gap you found.
