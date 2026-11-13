---
id: DAEO-61vm
status: closed
deps: []
links: [DAEO-52ku, DAEO-2bdu, DAEO-k1e2, DAEO-p8tv, DAEO-qz4p]
created: 2026-11-11T01:20:37Z
type: task
priority: 2
assignee: engineer
external-ref: W2-170
tags: [wave-2, implementation, memory, audit, full, after-the-lift]
wbs_id: W2-170
title: 'The memory audit''s set record: the checks before any search, the drop and void rule, the declaration and the use-once marker, counts only (DEC-1101 (1), DEC-1125 (2))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/memaudit/**
- tests/unit/memaudit/**
- governance/project/test-map.yaml
- docs/changes/W2-170-evidence.md
kpis:
  success:
  - 'S1 The pre-flight checks a delivered set before any search and prints ids, counts and the codes below only. It refuses on each of: fewer than 36 files; a file not in the writer brief''s form (`id`, `question`, `gold_answer`, `sources`, `commit`, `category`, `drawn`); a `commit` other than the audit commit; a category count other than the 40-question quotas of the rubric (R5 item 6); a governing domain under 4 questions or a subsystem over 10, scaled to the kept count; a `drawn: changed` or `drawn: sample` question whose first source is not in `selection.json`''s list of that name; a source path missing at the audit commit, or a `heading` not found and `lines` outside the file; a source in an evaluation or evaluation-source namespace (R8); a gold-source set equal to a pool question''s (R9); a nonexistent-id question whose id exists at the commit. Verify: a planted set in a planted repository and sets root under TMPDIR with ten planted defects, one per check: each refused with its own code; the clean planted set ends `PRE-FLIGHT: every check as expected`; no real `~/gov-os-eval` is opened [DEC-1101 (1), DEC-1069 (5), DEC-1125 (2)]'
  - 'S2 The drop and void rule: after the checker''s second pass, every question whose verdict in the notes is not `accept` is moved to `dropped/` in the set''s folder (never deleted), the kept count and every S1 scale are recomputed from the kept questions, and a kept count under 36 or a domain under 4 makes the audit VOID: nothing is measured, no `USED` marker is written, and the counts say `void` with the cause code. Verify: planted notes with 3 drops (audit goes on, kept 37, scales recomputed), with 5 drops (VOID, no `USED`, no `DECLARATION.json`), and with a drop that leaves a domain at 3 (VOID) [DEC-1101 (1), DEC-1125 (2)]'
  - 'S3 Before any search the runner writes `runs/<audit>/DECLARATION.json` and a `USED` marker, in that order. The declaration holds: the audit commit; the store''s commit and its sha256; the gov pin; the `retrieval.yaml` digest; the standard''s four settings by name (the shared reranker, the pool on, the 6,000-token bundle, search again once); the set''s digest (`LC_ALL=C sha256sum *.yaml | sha256sum` over the kept questions); n; the bar scaled to n (at least ceil(0.85 n) right end to end, at most floor(0.05 n) wrong claims; the target ceil(0.95 n)); and how it rounds. The runner refuses to start while `USED` exists, so a set is measured once. Verify: a planted run writes both files in that order (the file times and the ledger line); a second run on the same audit exits with the refusal and writes nothing; a planted `retrieval.yaml` with the pool off is named in the declaration and the run is not ok without a decision id [DEC-1098 (1), DEC-1097 (1)(d), DEC-1101 (1)]'
  - 'S4 The set is declared in the sets root''s own path map by the runner''s code, as one `evaluation_sets` entry of the shape `memory-verdict-2`''s has (its hidden glob, the six roles measured), so `gov.retrieval.measure` accepts it, and nowhere else: the repository''s `governance/project/path-map.yaml`, the guard and the hook are never written, and no ACT is needed for a new audit''s name. Verify: a planted sets root map gains exactly one entry for `memory-audit-<date>`; `git status` in the planted repository shows no change; the measure run on the planted set accepts it [DEC-1101 (2), DEC-820]'
  - 'S5 Only counts and ids leave the tool: standard output and `runs/<audit>/PREFLIGHT.json` hold ids, counts, codes and digests, never a question, a gold answer, a source path or a heading; a line naming the sets root''s folders is refused before it is printed; the command line names only `--sets-root <root>`, never a folder under it (the guard''s line rule). Verify: a planted question with a unique word: grep of every output file and the captured stdout and stderr finds it 0 times; the printed command line holds no `fixtures/` or `runs/` [DEC-1101 (2), DEC-1097 (2)]'
  - 'S6 The package is wired in: `governance/project/test-map.yaml` places `src/gov/memaudit/**` and its tests (so a change here runs these tests and not the full suite), and the module runs as `python3 -m gov.memaudit preflight|void|declare`. Verify: `gov close`''s scoped selection for a planted change under `src/gov/memaudit/` names `tests/unit/memaudit/`; each subcommand prints its usage with `--help` and exits 0 [DEC-896]'
  failure:
  - 'A question, gold answer, answer, source path or heading of a set in any output, log or error text. Verify: S5''s planted question with a unique word, gold answer, source path and heading: grep of every output file, the captured stdout and stderr and the logs finds each 0 times'
  - 'A set measured twice, or measured without `DECLARATION.json` and `USED` written first. Verify: S3''s planted runs: the file times and the ledger line show `DECLARATION.json` before `USED` before any search, and a second run on the same audit exits with the refusal and starts no search'
  - 'The repository''s path map, the guard, the hook, `.claude/` or the walls'' template written; the real sets root or run folders opened by a test. Verify: S4''s `git status` in the planted repository shows no change, and a run of the tests with the planted roots under TMPDIR leaves no open of the real sets root or run folders in the tests'' file-access log'
  - 'A dropped question deleted; a VOID audit that wrote `USED`. Verify: S2''s planted notes with 3 drops (the 3 files are found under `dropped/`) and with 5 drops (VOID: no `USED` and no `DECLARATION.json` in the audit''s run folder)'
  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'
profile: FULL
sources:
- DEC-1101
- DEC-1125
- DEC-1098
- DEC-1097
- DEC-1069
- DEC-820
- DEC-896
- DEC-1050
- DEC-1073
- DEC-1052
- DEC-1129
- DEC-1010
- DEC-1131
- DEC-1133
est_loc: 450
acceptance_tests:
  path: tests/acceptance/W2-170/
  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C2), from these KPI lines and the writer, checker and auditor briefs (`packages/MEMORY-AUDIT-1/briefs/`), before the engineer: a planted sets root, a planted repository with commits, a planted pool; never the real ~/gov-os-eval or ~/gov-os-runs'
track: B
list_rows: []
reads:  # declared by the CTO 11-11 (gov brief READS_MISSING; DEC-1121): what it reads that it does not write
- governance/project/path-map.yaml
- governance/project/orchestration/packages/MEMORY-AUDIT-1.md
- governance/project/orchestration/tools/indep_launch.py
- governance/project/indep-walls/tree-exclude.txt
needs: []
waits_on: []
---
# W2-170 The memory audit's set record

Owner decision DEC-1125 (2): the memory audit is a scheduled practice, weekly while development is active, an
independent writer drafting fresh questions, measured once, misses classified. This ticket is the **record and the
checks** around one audit's set: what is checked before any search, what is dropped, what is declared, and the
use-once marker. The measure is W2-171's; the cycle and the schedule are W2-172's; the launch script's follow-ups are
W2-173's. The whole is described in `governance/project/orchestration/packages/MEMORY-AUDIT-1.md`.

- **Home:** a new package `src/gov/memaudit/`, so that the tool ships with Gov OS and with every adopted repository
  (W2-88 reuses it: its `memory_sets.py` calls this core and carries no second copy). **After the lift; usage (A)
  keeps it waiting until the weekly reset (DEC-1122 (2)).**
- **Built on:** the independent sessions' launch script, merged (`2f98aecbc`, W2-149), the walls (`147706ae`), the
  install ACT (`baac0b2c2`), and the fresh 80's tools (`.gov-runtime/scratch/orchestrator/drafts/fresh80/`:
  `preflight.py`, `f80lib.py`), which are generalised here: they pin one set name and one run folder. The CTO copies the
  fresh-80 tools to `.gov-runtime/scratch/ref/fresh80/` in the worktree when the ticket starts.
- **Alternatives (one line each):** carry the checks in the launch script (rejected: it decides what a session sees,
  not whether a set is fit to measure); keep the fresh-80 scripts per set (rejected: pinned to one set, no tests for
  a second).
- **Not here:** the measure, the reader run, the pool's re-run (W2-171); the cycle, the schedule, the digest (W2-172);
  `--effort`, the stop word, the notes' form (W2-173).

[DEC-1101 (1)-(2); DEC-1125 (2)]

## Interface

Stated by the CTO before the pair starts (DEC-1052; PKG-W2-170-IFACE-1, option (a)). The test designer writes tests to
this block and the engineer conforms to it; neither changes it. A gap or a clash found in it goes back to the CTO as a
package, never settled by the pair. Bracketed lines name the KPI line each item serves (S1 to S6; F1 to F5 are the
`failure:` lines in order). The three approved briefs are not changed by anything here (DEC-1129 (2)).

### 1 The command line [S6, S5, F1]
The module is run as `python3 -m gov.memaudit <subcommand> [flags]`, the form W2-171 and W2-172 call it by
(`src/gov/memaudit/__main__.py`). No `gov memaudit` subcommand is added (`src/gov/cli/` is not in this ticket's paths).
Three subcommands belong to this ticket; W2-172 adds `run`, `due`, `baseline` and `status` to the same module.

| subcommand | what it does | KPI |
|---|---|---|
| `preflight` | the ten checks of the set in `hidden/`, before any search; writes `PREFLIGHT.json` | S1 |
| `void` | the drop and void rule: moves every question the notes do not accept to `hidden/dropped/`, recomputes the scales on the kept ones; writes `DROPS.json` | S2 |
| `declare` | the set's entry in the sets root's path map, then `DECLARATION.json`, then `USED`, then the ledger lines | S3, S4 |

Each prints its usage with `--help` and exits 0. Every flag takes a value, and each value is a bare name, a number, a
hash or a path **outside** the sets root; no flag ever names a folder under the sets root (F1, S5).

| flag | used by | meaning and default |
|---|---|---|
| `--sets-root <root>` | all, required | the sets root (a real directory; `~` is expanded). It is the only flag that names the sets root. Every folder under it is derived in the code (section 2). A root that is not a directory, or whose real path lies inside `indep-walls`, is refused with exit 4. |
| `--audit <name>` | all, required | the audit's name, matching `memory-audit-[0-9]{8}` (also the set's name and the audit's run folder). Any other form: exit 4. |
| `--repo <dir>` | `preflight`, `declare` | a git repository that holds `--commit`. Default: the top level of the working directory (as the launch script finds it). Source paths, `retrieval.yaml` and the path map are read from the commit with `git show`/`git cat-file`, never from the working tree, so the tree may be at another commit. |
| `--commit <rev>` | `preflight`, `declare`, required | the audit commit, resolved to 40 hex digits with `git rev-parse --verify <rev>^{commit}`; an unresolved value: exit 4. |
| `--runs-dir <dir>` | `preflight` | the folder holding `indep/AUDITS.log` and `indep/SEEDS.log` (the launch script's own folder, `GOV_INDEP_RUNS_DIR`). Default: `$GOV_INDEP_RUNS_DIR` when set, else `~/gov-os-runs`. A value inside the sets root: exit 4. It is read only to derive the selection lists (section 4, last paragraph). |
| `--store <file>` | `declare` | the store to declare. Default: `<repo>/.gov-runtime/store.db`. |
| `--gov <path>` | `declare` | the `gov` executable whose pin is declared. Default: `~/.local/bin/gov`. |
| `--decision DEC-<n>` | `declare` | the decision that allows a `retrieval.yaml` other than the standard (section 6). The form is `DEC-[0-9]+`; the register is not looked up. |

Printing: one tool function, `say`, is the only way anything is printed. It refuses (prints `REFUSED: a line that names
a sets-root folder was not printed`, exits 4) any line that holds the sets root's real path followed by a slash, or one
of `fixtures/`, `runs/`, `indep-walls/`, `hidden`. A line holds only ids (`q07`), counts, codes and digests. A failure
prints one line, `ERROR: <exception class>`; no traceback and no exception text is printed or written anywhere (a
YAML error quotes the file's text). Standard error carries the same single line. [S5, F1]

### 2 The layout under the sets root [S2, S3, S4, S5]
Derived from `--sets-root` and `--audit` only; the shape follows the launch script's own folders and the path map's
existing `memory-verdict-2` entry. `<A>` is `--audit`.
```
<root>/governance/project/path-map.yaml            the sets root's own map: gains one evaluation_sets entry (S4)
<root>/fixtures/evaluation/<A>/hidden/q01.yaml..   the set: only q<nn>.yaml files, flat (the launch script delivers them)
<root>/fixtures/evaluation/<A>/hidden/dropped/     dropped questions, moved, never deleted (S2)
<root>/fixtures/evaluation/<A>/XCHECK-r1.md        the checker's notes, written by the launch script (r2 after round 2)
<root>/fixtures/evaluation/<A>/selection.json      optional: {"commit","last_audit","seed_sha256","changed","sample"}
<root>/fixtures/evaluation/memory-pool/hidden/     the regression pool: flat <audit>-<qid>.yaml files (W2-171 fills it)
<root>/runs/<A>/PREFLIGHT.json  DROPS.json  DECLARATION.json  USED  ledger.jsonl
```
- **The notes are `XCHECK-r<n>.md`, not `notes.md`.** The checker's `out/notes.md` is delivered by the launch script as
  `XCHECK-r<round>.md` in the set's folder (beside `hidden/`, not in it). `void` reads the one with the highest `n`.
- **`dropped/` is inside `hidden/`** so that the path map's existing glob `fixtures/evaluation/*/hidden/**` already hides
  the dropped questions from the six roles. The measure reads `hidden/*.yaml` flat and never sees `dropped/`.
- **The pool is `fixtures/evaluation/memory-pool/hidden/`** for the same reason: a `pool/` folder at the root would match
  no hidden glob (`sets_root_hidden` lists none for it). This ticket only reads the pool; a missing folder is an empty
  pool.
- `runs/<A>/` is the folder the launch script already uses for the auditor (`runs/<A>/misses.jsonl` in,
  `miss-classes.json` out). `preflight` creates it with mode 700 when absent. `PREFLIGHT.json` and `DROPS.json` are
  written whole or not at all (a temporary name, then rename).
- `ledger.jsonl`: one JSON object per line, in order, each `{"seq": n, "at": <ISO UTC>, "event": <word>, ...}` with
  numbers and codes only. This ticket writes the events `preflight`, `drop`, `void`, `declaration` and `used`. W2-171
  appends its own events (`search`, `spend`) to the same file; no search entry may precede the `used` line.
- The set's digest is the fresh 80's: for the files `hidden/*.yaml` (not `dropped/`) in byte order of name, the sha256
  of the text of lines `<sha256 of the file>␣␣<name>\n` (`LC_ALL=C sha256sum *.yaml | sha256sum`).
- Nothing is written outside `<root>/runs/<A>/`, `<root>/fixtures/evaluation/<A>/hidden/dropped/` (a move) and the
  sets root's own path map. In particular not the repository's path map, the guard, the hook, `.claude/` or the walls'
  template (F3).

### 3 The ten refusal codes of `preflight` [S1, S5]
One code per S1 check, in the KPI line's order. `preflight` runs all ten (a check whose input a file does not give is
skipped for that file, which the form check has already named), prints one line per code,
`PF-<NAME> ok` or `PF-<NAME> refused <n>` followed by the offending ids (`q07 q12`, at most 40; none for set-level
codes), writes the same to `PREFLIGHT.json` with the counts, and ends with the exact line
`PRE-FLIGHT: every check as expected` (all ten ok) or `PRE-FLIGHT: NOT as expected: stop, fix before any search`.

| # | code | refuses when (the KPI line's words) |
|---|---|---|
| 1 | `PF-COUNT` | fewer than 36 files. (`hidden/` holds a file that is not `q<nn>.yaml` or a folder other than `dropped/`: also this code.) |
| 2 | `PF-FORM` | a file not in the writer brief's form: it parses as a YAML mapping with exactly the keys `id`, `question`, `gold_answer`, `sources`, `commit`, `category`, `drawn` and optionally `keyword` (bool) and `naive_answer` (string); `id` equals the file's stem `q<nn>`; the three texts are non-empty strings; `category` is one of the twelve names; `drawn` is `changed`, `sample` or `none`; `commit` is 40 hex digits; `sources` is a non-empty list whose entries are each a mapping or a list of mappings (alternatives), each with a string `path`, an optional string `heading` and an optional `lines: [first, last]` of two integers with 1 <= first <= last |
| 3 | `PF-COMMIT` | a `commit` other than the audit commit (`--commit`, resolved) |
| 4 | `PF-QUOTA` | a category count other than the 40-question quotas of the rubric (R5 item 6): decision 6, contract 4, plan 4, ticket 4, exact-string 4, callers 4, code-paraphrase 3, kernel-template 3, multi-file 3, failure-memory 3, history 1, nonexistent-id 1. With 40 files every count equals its quota; with 36 to 39 files (the writer brief section 9 delivers them as they stand) no count may exceed its quota. Set-level: it prints the category names and counts, no ids. |
| 5 | `PF-SPREAD` | a governing domain under 4 questions or a subsystem over 10, scaled to the kept count `n` (section 4). Prints `domain <name> <count>` or `subsystem <name> <count>`; no ids. |
| 6 | `PF-DRAWN` | a `drawn: changed` or `drawn: sample` question whose first source is not in `selection.json`'s list of that name (`changed`, `sample`). `drawn: none` is not checked. If the lists cannot be had (section 4, last paragraph), every `drawn: changed` and `drawn: sample` question is named. |
| 7 | `PF-SOURCE` | a source path missing at the audit commit (`git cat-file -e <commit>:<path>`), or, for an alternative whose file exists, a `heading` not found (as the first line of the file equal to it, trailing spaces ignored) and `lines` outside the file (`last` > the file's line count) or absent. An alternative with no `heading` is refused only when its `lines` are outside the file. A heading not found with `lines` inside the file passes and is counted `re-anchored` in `PREFLIGHT.json`. |
| 8 | `PF-EVALNS` | a source (any alternative) in an evaluation or evaluation-source namespace (R8): its path matches a `paths` glob of the path map's `evaluation-sources` or `evaluation-fixtures` namespace, or a `visible` or `hidden` glob of any `evaluation_sets` entry, all read from the path map at the audit commit and matched by the path map's own glob rule |
| 9 | `PF-DUPPOOL` | a gold-source set equal to a pool question's (R9). A question's gold-source set is the set over its entries of the set of its alternatives' `(path, heading or "", lines or [])`; two questions are equal when these sets are equal. The pool is every `*.yaml` of `fixtures/evaluation/memory-pool/hidden/`. |
| 10 | `PF-IDEXISTS` | a `nonexistent-id` question whose id exists at the commit: an id-shaped token of its question (`gov.retrieval.lexical.ids_in`) that `git grep` finds in a tracked file of the commit as a whole token (`lexical.whole_id`). A question with no id-shaped token is counted `no_token` in `PREFLIGHT.json` and is not refused (the checker's R3 code decides). |

### 4 Domain and subsystem by a fixed rule [S1, S2]
Both are computed from **the first source path** of a question: the `path` of the first alternative of its first entry
in `sources`. No new question field exists and the writer brief is unchanged. The rule is the checker brief's section
5a, written as two tables (data in `src/gov/memaudit/`, matched top to bottom, the first match wins; a prefix ending in
`/**` matches anything below it, a bare name matches that file).

| governing domain | first source path |
|---|---|
| `decisions` | `docs/DECISION_REGISTER.md` |
| `tickets` | `.tickets/**` |
| `plan` | `docs/plan/**` |
| `contract` | `docs/contract/**`, `docs/charter/**` |
| `code` | `src/**`, `template/governance/kernel/hooks/**`, `.claude/hooks/**` |
| `none` | anything else (a lesson, a role file, a skill, the path map, an operations file) |

| subsystem (writer brief's seven) | first source path |
|---|---|
| `retrieval` (retrieval and the context packet) | `src/gov/retrieval/**`, `src/gov/retrieve/**`, `src/gov/context/**`, `src/gov/store/**`, `src/gov/codeintel/**`, `governance/project/retrieval.yaml` |
| `guard` | `src/gov/guard/**`, `src/gov/hooks/**`, `template/governance/kernel/hooks/**`, `.claude/hooks/**` |
| `close` (the close and the nightly) | `src/gov/close/**`, `src/gov/closure/**`, `src/gov/accept/**`, `src/gov/check/**`, `src/gov/readiness/**`, `src/gov/ci/**`, `docs/close/**`, `governance/project/orchestration/tools/nightly*` |
| `checkpoint` (checkpoints and resume) | `src/gov/checkpoint/**`, `src/gov/pause/**`, `docs/checkpoints/**` |
| `rebuild` (rebuild and the secrets scan) | `src/gov/rebuild/**`, `src/gov/secrets/**`, `src/gov/doctor/**` |
| `launch` (launch and the sandbox) | `src/gov/launch/**`, `src/gov/brief/**`, `template/governance/kernel/launch/**`, `governance/project/orchestration/tools/indep_launch.py`, `governance/project/indep-walls/**` |
| `release` (releases and install) | `src/gov/release/**`, `src/gov/adopt/**`, `src/gov/adapters/**`, `docs/releases/**` |
| `none` | anything else |

A question whose first source matches no row is scored `none` for that table, and `none` counts toward no minimum and no
maximum. (So a `decisions` question has subsystem `none`: the pre-flight's subsystem count is a lower bound of what
the checker judges, which counts "what the asked fact is about"; the checker's own R5 lines in the notes stay the
judgement, this is the part that can be computed.)

**The scale.** With `n` the number of questions counted (the files in `hidden/`, not `dropped/`): a domain needs at
least `ceil(4 * n / 40)` and a subsystem may hold at most `floor(10 * n / 40)`, integer arithmetic. For n from 36 to 40
the minimum is 4, and the maximum is 9 for n = 36 to 39 and 10 for n = 40. `preflight` applies it to the files it finds;
`void` applies it again to the kept questions (section 5).

**The selection lists** (`changed`, `sample`) are `fixtures/evaluation/<A>/selection.json` when that file exists
(this is how tests plant them, and how a later launch-script change would deliver the writer's own file). When it does
not exist, `preflight` derives them in memory, by the launch script's own rule (its stage B4), and writes nothing:
`last` is the `commit` of the last line of `<runs-dir>/indep/AUDITS.log` (none when the file is absent or empty);
`tracked` is `git ls-tree -r --name-only -z <commit>` in that order; `excluded` is the globs of
`governance/project/indep-walls/tree-exclude.txt` at the commit, tested on the path and each of its parent folders with
`fnmatch.fnmatchcase`, as the launch script does; `changed` is the sorted tracked paths of `git diff --name-only
--no-renames -z <last> <commit>` that are not excluded (empty when there is no `last`); `others` is `tracked` in order,
less `excluded` and less `changed`; `sample` is `random.Random(seed).sample(others, min(300, len(others)))`, where
`seed` is the `seed` of the single line of `<runs-dir>/indep/SEEDS.log` with `kind` `writer`, `set` `<A>`, `round` 1 and
`dry` false, whose `seed_sha256` equals the sha256 of the file `<seed>\n`. No such line, two such lines, or a seed
that does not match its hash: the lists cannot be had.

### 5 The declaration, the exit codes and the void causes [S2, S3, F2, F4]
**Exit codes (all three subcommands).**

| exit | word | meaning |
|---|---|---|
| 0 | ok | every check as expected; or, for `void`, the audit goes on; or `declare` wrote its files |
| 1 | refused | at least one refusal code printed: a `PF-` code (`preflight`), a `DR-` code (`void`), a `DC-` code (`declare`); nothing is written beyond what the subcommand says |
| 2 | void | `void` only: the kept set cannot be measured; the cause code is printed |
| 3 | used | `USED` exists for this audit: the subcommand writes nothing and prints `USED` (a set is measured once) |
| 4 | usage | a flag or value refused (section 1), the sets root unusable, a printed line refused by `say`, or an unexpected error (`ERROR: <class>`) |

argparse's own error exit (2) is mapped to 4; `--help` exits 0.

**`void`** reads the highest `XCHECK-r<n>.md`. Its `## Questions` lines have the checker brief's form
`<id> | <verdict> | <codes> | also: <...> | <sentence>`, split on ` | `. A question is kept only when its line's second
field is exactly `accept`; a `revise`, a `reject`, a missing line or a line that does not fit is dropped (counted by its
codes, or `NOLINE`, `UNFIT`). Order: (1) refuse `DR-NOTES` (exit 1, nothing moved) when no `XCHECK-r<n>.md` exists or
it has no `## Questions` section; (2) move each dropped file with `os.rename` into `hidden/dropped/` (made on need),
never deleting; (3) recompute from the kept files: `kept`, the domain counts and the subsystem counts (section 4);
(4) write `DROPS.json` and the `drop` ledger line; (5) if void, write the `void` ledger line and exit 2, else exit 0.
`void` refuses `DR-DONE` (exit 1) when `DROPS.json` exists. **Void causes (closed): `VOID-COUNT` when `kept` < 36;
`VOID-DOMAIN` when a domain holds fewer than `ceil(4 * kept / 40)` kept questions** (`VOID-COUNT` is reported first when
both hold). A subsystem over its scaled maximum after drops is printed and recorded as `subsystem_over` and does not
void (S2's void causes are the count and a domain). A void audit writes **no `USED` and no `DECLARATION.json`**
(F4); its dropped files stay in `dropped/`. `DROPS.json` holds `{"kept": n, "dropped": n, "by_code": {<code>: n},
"domains": {...}, "subsystems": {...}, "subsystem_over": [...], "void": null | "VOID-COUNT" | "VOID-DOMAIN",
"set_digest": <the kept set's digest>, "notes_round": n}`. Printed: `VOID <cause> kept <n> dropped <n>` or `DROPS: kept <n> dropped <n>`.

**`declare`.** Refuses first, writing nothing: a present `USED` is exit 3 (printed `USED`, no `DC-` code). The others
are exit 1 with the code printed:
`DC-PREFLIGHT` (`PREFLIGHT.json` absent, or its `ok` false), `DC-DROPS` (`DROPS.json` absent, or its `void` not null,
or the digest of `hidden/` now differs from the digest in `DROPS.json`), `DC-STORE` (the store file is absent or
unreadable, or the `head` of its fingerprints row, read with `gov.store.loader.fingerprints`, is not the audit commit),
`DC-PIN` (the real path of `--gov` has no component `pin-[0-9a-f]{12}`), `DC-RETRIEVAL` (no
`governance/project/retrieval.yaml` at the commit, or it is not a YAML mapping), `DC-MAP` (section 7), `DC-DECISION`
(section 6; this one writes `DECLARATION.json` with `ok: false` and no `USED`, the only refusal that writes). Then, in
this order:
1. the entry in the sets root's path map (section 7);
2. `DECLARATION.json` (written whole, then synced);
3. the `declaration` ledger line;
4. `USED`, created with `O_CREAT | O_EXCL` (an existing one is exit 3), holding one line `<ISO UTC> <A> <sha256 of
   DECLARATION.json>`, and only after waiting until the clock is past `DECLARATION.json`'s mtime, so that its mtime is
   strictly later (nanoseconds);
5. the `used` ledger line.
Printed: `DECLARED: audit commit <12 hex>, n <n>, set digest <12 hex>` and `USED written`.
`DECLARATION.json` keys (all present):
```
audit, audit_commit, store_commit, store_sha256, gov_pin, retrieval_yaml_sha256, set_digest, n,
settings: {"reranker": "shared", "pool": <bool>, "bundle_tokens": 6000, "search_again_once": true},
nonstandard: [<setting names, empty when standard>], decision: "DEC-n" | null, ok: <bool>,
bar: {"need_right": ceil(85n/100), "max_wrong": floor(5n/100), "target_right": ceil(95n/100)},
rounding: "need_right = ceil(85 n / 100); max_wrong = floor(5 n / 100); target_right = ceil(95 n / 100); integer arithmetic",
declared_at: <ISO UTC>
```
`audit_commit` is `--commit` resolved; `store_sha256` is the sha256 of the store file's bytes; `gov_pin` is the
`pin-<12 hex>` component; `retrieval_yaml_sha256` is the sha256 of the bytes of `governance/project/retrieval.yaml` at the
commit; `n` is the kept count.
The four settings are by name; only `pool` is read from `retrieval.yaml`, the other three are the standard's fixed
values (the shared reranker, a 6,000-token bundle, search again once). The runner of W2-171 calls `declare` first and
starts no search unless it exited 0 and `ok` is true; with `USED` present it exits 3 and starts nothing.

### 6 The flag for a non-standard `retrieval.yaml` [S3]
The standard is "the pool on": `retrieval.yaml` at the commit has a `pool` mapping with `meaning_uncut: true`. If it
does not, `pool` is `false` and `nonstandard` is `["pool"]`. `declare` then:
- without `--decision`: writes `DECLARATION.json` with `ok: false` and `decision: null`, **no `USED`**, prints
  `DC-DECISION pool` and exits 1. (The run is not ok. A later `declare` with the flag may rewrite the file, because it
  is allowed only while `USED` is absent.)
- with `--decision DEC-<n>`: writes `decision: "DEC-<n>"` and `ok: true`, and goes on to `USED`.
With a standard file the flag is accepted and recorded as given, and `ok` is true.

### 7 The set's entry in the sets root's own path map [S4, F3]
`declare` makes `<root>/governance/project/path-map.yaml` hold exactly one entry
`evaluation_sets.<A>`, of the shape of `memory-verdict-2`'s:
```
  <A>:
    visible: []
    hidden: ["fixtures/evaluation/<A>/hidden/**"]
    measures:
      roles: [engineer, research, product-spec, independent-test-designer, independent-auditor]
```
- The file is edited as text: the entry is inserted at the end of the `evaluation_sets:` block, and every other byte is
  kept (the block may sit among comments; the map is read back with `gov.util.parts.evaluation_sets` to prove the entry
  parses and `<A>` is found). A map that does not exist, has no `evaluation_sets` block or cannot be read: exit 1
  `DC-MAP`, nothing written. An entry for `<A>` already present and equal: left as is. Present and different: `DC-MAP`.
- The five roles are the ones `memory-verdict-2` lists, not six: the orchestrator is the session that runs the measure,
  and a role in `measures.roles` is refused the hidden part (`gov.retrieval.measure`, DEC-820 (d)). S4's phrase "the six
  roles measured" is read as "the roles of `memory-verdict-2`'s entry".
- Nothing else is written outside the sets root's folders of section 2; the repository's `governance/project/path-map.yaml`
  is never opened for writing (S4's `git status` in the planted repository shows no change).

### 8 Python entry points for W2-171 and W2-172
Named so that those tickets import, and never copy, this code (W2-88 imports the same): `gov.memaudit.layout.paths(
sets_root, audit)` (every path of section 2, derived and checked inside the root), `layout.is_used(...)`,
`gov.memaudit.preflight.run(...)`, `gov.memaudit.drops.apply(...)`, `gov.memaudit.declare.declare(...)`,
`gov.memaudit.say.say(...)`, `gov.memaudit.ledger.append(...)`. Each `run`/`apply`/`declare` returns the exit word and the
counts object that the subcommand prints; the subcommand is a thin wrapper. The module imports `gov.retrieval.lexical`,
`gov.store.loader` and `gov.util.parts`, never `gov.retrieval.measure`'s private functions.

### 9 What the tests plant (the designer's and the engineer's common ground)
A sets root and a repository, both under `TMPDIR`; a sets-root path map with an `evaluation_sets` block and comments; a
repository with at least two commits (the audit commit and an earlier one), a `governance/project/retrieval.yaml`, a
`governance/project/path-map.yaml` with the two evaluation namespaces and a `governance/project/indep-walls/tree-exclude.txt`;
a runs dir with `indep/AUDITS.log` and `indep/SEEDS.log` (or a planted `selection.json`); a planted pool folder; a store
file with a `fingerprints` row; a `gov` link into a folder named `pin-<12 hex>`. The real `~/gov-os-eval`,
`~/gov-os-runs` and run folders are never opened (F3).

### 10 The CTO's readings of row 147 and of the tests run's questions (delegated decisions, 2026-11-11, session b40cba91; DEC-936 item 2.5, DEC-1112 (3))
1. **`dropped/` stays inside `hidden/`** (`hidden/dropped/`), so the existing glob `fixtures/evaluation/*/hidden/**`
   keeps the dropped questions from every measured role. Every consumer of the set reads `hidden/*.yaml` flat, never
   recursively; the auditor's copy made by the launch script excludes `hidden/dropped/` (a W2-173 follow-up, noted in its
   ticket). Until W2-173 lands, an auditor that is shown a dropped question also sees its note's verdict; nothing counts it.
2. **S4's "the six roles measured" reads as `memory-verdict-2`'s list:** the five roles `engineer`, `research`,
   `product-spec`, `independent-test-designer`, `independent-auditor`; the orchestrator (the CTO, who measures) is not in
   `measures.roles`, as in every `evaluation_sets` entry today. A test checks the five, never six.
3. **S1's quotas for 36 to 39 files read as "at most":** with `n` files, each category's count is at most its 40-question
   quota (section 4's table, PF-QUOTA), and at `n = 40` exactly the quota; the domain and subsystem scales stay as section 4
   states them.
4. **The draw lists come from the runs folder's `indep/AUDITS.log` and `indep/SEEDS.log`** as section 4 and section 9 state;
   `selection.json`, when present, is a planted or hand-made override read first. No W2-173 change is needed for it.
5. **`say(line, sets_root)`** (PKG-W2-170-TD-1, the test designer's question): `gov.memaudit.say.say` takes the one line to
   append and the sets root, as the tests drive it; it returns the exit word and the counts, as section 8's others do.
6. **A file PF-FORM refuses counts toward `n` (PF-COUNT), not toward the category quotas or the spread** (TD-2); below 36
   files PF-COUNT refuses first, so no quota below 36 is defined.
7. **A path map that cannot be read at the commit gives `ERROR: <class>` and exit 4** (TD-3), never a PF- code: it fails
   closed and is not a finding about the set.
8. **`DC-DECISION` writes no map entry before an `ok: true` declaration** (TD-4): the map entry follows a declaration that
   passed, never a refused one.
9. **The pre-flighted set is the set declared** (review round 1's RV1, PKG-W2-170-R1-PREFLIGHT-FRESH, option (a); a
   delegated stricter-only decision): `PREFLIGHT.json` records each delivered file's sha256 by id; `DC-PREFLIGHT` also refuses
   when a kept file is not byte-equal to a pre-flighted one (a set whose writer round 2 replaced `hidden/` after the
   pre-flight is never marked `USED` until it is pre-flighted again). Sections 3 and 5 read with this line.
