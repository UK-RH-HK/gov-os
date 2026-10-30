# W2-61 acceptance tests — the standing 20-question measure, split under Policy 2 (d)

Ticket DAEO-iw1f (W2-61), profile STANDARD. Written by the independent test designer (MR-3) from the ticket's KPI
lines and its sources (DEC-828 items 3 and 4, DEC-833, DEC-860, DEC-820 (d), DEC-845, DEC-873, DEC-877, DEC-941
item 1.2, CAP-10, lens B's report §1 and §2.1–2.5), before the implementation.

## Nothing hidden is read

The real hidden half (`fixtures/evaluation/memory-retrieval/hidden/**`) is never opened, listed, named to the
measure or depended on. Every hidden part here is **planted**, built at test time in a temporary repository under
pytest's `tmp_path`, and every planted hidden word starts with `zqxw61hidden`.

## How the tests run this worktree's code (DEC-732)

- **The measure** is run as a process: `python3 -m gov.retrieval.measure <set> [options]`, with `PYTHONPATH` set to
  the runner's own `PYTHONPATH` when it has one, else to this worktree's `src` (`w2_61_support.python_path`). Run
  the suite as
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-61/src python3 -m pytest tests/acceptance/W2-61 -q -p no:cacheprovider -rs`.
- **The retrieval** is a **planted `gov`**: a `python3 -m venv --without-pip` environment in the test's folder holds
  a planted `gov` package; the executable `bin/gov` names that environment's interpreter on its first line, as the
  installed `gov` does. It answers `--version` (`gov 9.61.0-planted (commit 61a61a61a61a)`) and `retrieve` with
  canned bundles in `gov retrieve --json`'s real envelope (`evidence` items with `path`, `start_line`, `end_line`,
  `text`; `continuation`), per question and per continuation token, and logs each call's arguments, its working
  folder, and whether `PYTHONPATH` or `GOV_TICKET` reached it. No real store, no embedder, no network.
- **The planted repository** is built from scratch (`git init` in `tmp_path`): the kernel template's path map with a
  planted `evaluation_sets` block (`planted-memory`: visible `docs/assessment/planted-report.md`, hidden
  `fixtures/evaluation/planted-memory/hidden/**`, measured: the roles engineer and research and the tickets
  DAEO-zz61 and W2-195; `planted-second`; `planted-uncovered`, whose hidden glob does not cover its questions),
  planted governing documents, planted tickets and planted question files.
- **The guard** (W2-58's (d)) is the kernel's PreToolUse hook, copied as one file into the planted repository and
  run as the harness runs it, exactly as `tests/acceptance/W2-58/` drives it.
- **The files the ticket writes** (`fixtures/evaluation/memory-retrieval/visible/*.yaml`,
  `docs/research/W2-61-baseline.md`) are read as files from this worktree, with lens B's report and this
  worktree's path map as the references.

The measure's sessions run as an unmeasured role (`orchestrator`) unless a case sets a measured one.

## KPI lines and their tests

| KPI line | Tests | Red now because |
|---|---|---|
| Success 1: lens B's 20 questions and gold answers are the visible half | `test_w2_61_visible_half.py`: 20 files; required fields; each `question` is Table 2's Command query with its `--ticket`, `--id`, `--radius` (Table 2 parsed from lens B's report; Q01 `DEC-782`, Q09, Q12 checked); every source path exists at HEAD and every heading is a line there; no source names lens B's report or `fixtures/evaluation/**`; the measure takes the 20 real files by the set's name (planted gov, `--part visible` only) | `fixtures/evaluation/memory-retrieval/visible/` does not exist (and the measure does not exist). Table 2's parse is green. |
| Success 2 / failure 1: the hidden half refused to the measured roles | `test_w2_61_hidden_half_refused.py`: the guard refuses engineer, research and a measured ticket's lead the planted hidden part by Read, Grep (folder and file), Glob (pattern and folder), Bash `cat`, `head`, `grep`, `grep -r` (folder and above); lets orchestrator and product-spec read it. The measure refuses `--part hidden` and `--part all` to a session measured by role, by ticket id, by the ticket's WBS id and by a WBS id, naming the set, retrieving no hidden question and showing no hidden word; the same session measures the visible part; a hidden folder the set's hidden globs do not cover is refused (fail closed) | **The 32 guard cases are green before the implementation**: they test W2-58's merged refusal (d) on a planted set, as the ticket's brief allows. The measure's cases are red: the measure does not exist. |
| Success 3: per question and in total, in the first five and in the bundle; repeatability; scores only | `test_w2_61_scores.py`: per-question `hit_at_5`, `in_bundle`, `full_evidence`, `first_gold_rank`, `pieces_found`, `pieces_needed`, `calls`; totals; one new record per `--out` run, equal to the `--json` document; `--compare` the same on an unchanged answer, differences named per question and figure after the planted answer changes (as after a rebuild), more than one record. `test_w2_61_sources_matched.py` (the matching rules), `test_w2_61_retriever_named.py` | The measure does not exist. |
| Success 4 / failure 3: both figures always together, against 85 and 99 | `test_w2_61_scores.py`: totals `floor` 85 and `target` 99; no text line and no JSON object (stdout, record, comparison) gives one figure without the other; a line gives both totals against 85 and 99. Also checked in `test_w2_61_hidden_never_shown.py` and `test_w2_61_baseline.py` | The measure and the record do not exist. |
| Success 5: stacked, never giant | `test_w2_61_stacked.py`: evidence only in a later batch counts for full evidence, not in the bundle (hit@5 on the stacked context's first five); a repeated item taken once; each next call passes `--continue <the last token>` with the same `--batch-size` and `--bundle-budget`; defaults 10, 6000, 24000 named; no call larger than stated; the stack budget admits an item that fits exactly and stops before the first that would pass it | The measure does not exist. |
| Success 6: the same split for other sets | `test_w2_61_any_set.py`: a second planted set measured by its name; an undeclared name (also `memory-retrieval`, undeclared in the planted path map) refused by name before any retrieval; a path map with no block; `--sets-root` holds the sets while `--root` answers | The measure does not exist. |
| Success 7: the baseline record | `test_w2_61_baseline.py` (structure only): the date; the clone's commit; the pinned gov's version and commit; the stores' fingerprint or sha256; both figures together against 85 and 99; a per-question table of the visible half (hit@5, in the bundle, full evidence, repeat, rebuild), a row per visible question; lens B's 13 of 20 and 17 of 20; a heading for the hidden half | `docs/research/W2-61-baseline.md` does not exist. |
| Failure 2: the script prints, logs or writes a hidden gold answer | `test_w2_61_hidden_never_shown.py`: `--part hidden` and `--part all`, text, `--json`, `--out`: no `zqxw61hidden` word in stdout, stderr, or any file created or changed under the test's folder (listing before and after, then a scan); the hidden part is still scored; errors on a hidden question (no sources, not YAML, a missing source path, a heading neither found nor with lines, a failing retrieval whose message is hidden) end non-zero naming only `h03` | The measure does not exist. |
| Failure 4: a hit counted from lens B's report or the evaluation files | `test_w2_61_governing_source.py`: the set's own report, an evaluation file and a test quote the gold answer word for word at ranks 1–3, the governing source at rank 6: no hit@5; a source naming the report, an evaluation file or a declared hidden path is refused naming its id or never counted; an alternative naming the report never counts. `test_w2_61_visible_half.py` checks the real files name neither | The measure (and the visible files) do not exist. |
| The retrieval named | `test_w2_61_retriever_named.py`: JSON, text and record name the planted executable, its version line and the planted package's `gov.__file__`, the root, its HEAD, the set, the part, the budgets; the planted gov saw no `PYTHONPATH` and no `GOV_TICKET` and ran in the root (also from another working folder); `--root` defaults to the current folder; `--gov` defaults to the first `gov` on `PATH` | The measure does not exist. |
| Edge cases | `test_w2_61_sources_matched.py`: alternatives; two entries, one found; a Markdown heading's span holds its sub-headings and stops at the next of its level; inclusive overlap at both ends; path-only; another path never matches; a heading not found uses the stated lines; trailing whitespace; a heading that moved governs over stale lines (Markdown and code, with and without `lines`); `ticket`, `ids`, `radius` and an odd question text passed through; ids from file names in file order; unknown fields never printed; errors (failing retrieval, missing path, malformed in six ways) end non-zero naming the question | The measure does not exist. |

## Choices this file makes where the brief leaves the form open

- **The comparison's JSON form** (`--compare`): each question object carries `compare`, a list with one object per
  `--compare` record, each with `same` (true or false) and `differs` (the names of what differs among `hit_at_5`,
  `in_bundle`, `full_evidence`, `first_gold_rank`, and a name of the measure's own for the stacked items' digest).
- **A commit** is given as at least 12 hex digits and must be a prefix of the HEAD it names.
- **The text output** names the comparison's differences on a line holding the question's id and the word "differ".

## Running

Before a run, check that neither `CLOSE-RUNNING` nor `NIGHTLY-RUNNING` is under the main tree's
`.gov-runtime/scratch/orchestrator/`. Each case builds its own planted repository and environment under pytest's
`tmp_path` and takes a few seconds; no case uses the network.
