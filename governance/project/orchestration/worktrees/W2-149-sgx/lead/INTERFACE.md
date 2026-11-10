## Set-up A's wiring: the interface (DEC-1112 (3), DEC-1113; what the engineer builds to)

The lead's draft (`INTERFACE-DRAFT.md`) adopted, with these changes: one result schema per brief (writer 1's has no
`not-sealed`); no `selection.json` in a labeller's or the auditor's wall (their briefs name none; labeller 2's
round 1 is "`input/half.json` only"); the x/y draw, the map's, the merge's and the mapped-back forms fixed; the map
written at delivery only; the rule script's two overrides and caps named; the selection of a set-up A writer stays S5's.

### The template (the engineer's two files)

- `tree-exclude.txt` gains the line `governance/project/indep-briefs/**` (every wall).
- `kinds.yaml`: every kind gains `model: <model id>`; a top-level `briefs:` map, keyed by the front matter's `brief:`
  id, each entry `{kind, flow, result_schema, sample, tree_exclude}` and optionally `model`. The five entries:

| Brief id | `kind` | `flow` | `result_schema` (in `indep-schemas/`) | `sample` |
|---|---|---|---|---|
| `sgx1-writer-tuning` | writer | `sgx1-writer-1` | `sgx1-writer-tuning-result.schema.json` | optional (the front matter has 400) |
| `sgx1-writer-heldout` | writer | `sgx1-writer-2` | `sgx1-writer-heldout-result.schema.json` | optional (the front matter has 400) |
| `sgx1-labeller` | labeller | `sgx1-labeller-1` | `sgx1-labeller-result.schema.json` | 0 |
| `sgx1-labeller-2` | labeller | `sgx1-labeller-2` | `sgx1-labeller-2-result.schema.json` | 0 |
| `sgx1-overlap-auditor` | auditor | `sgx1-overlap-auditor` | `sgx1-overlap-auditor-result.schema.json` | 0 |

  Each entry's `tree_exclude`: `.claude/**`, `src/gov/guard/**`, `src/gov/launch/**`,
  `governance/project/indep-walls/**`. The models are the CTO's to choose (the cases read the planted ones). The
  planted `kinds.yaml` adds two test-only entries (`w2-149-no-schema`, `w2-149-no-sample`) and an entry `model` on four
  of the five; the script must take any entry of this form.

### Stage 10 (S22)

- `model`, `result_schema` and `sample`, each: the front matter's value, else the value in the `briefs:` entry the
  front matter's `brief:` names, else (`model` only) the kind's `model`. A value found nowhere: **10**. An entry whose
  `kind` differs from the front matter's: **10**. A labeller brief with no `brief:` id, or one the map does not hold:
  **10** (the labeller kind runs set-up A's flows only). A brief of another kind with no `brief:` id: as before.
  Front-matter keys the script does not use (`brief version experiment rounds tools budget_basis`) are ignored;
  `budget_usd`/`timeout_s` as before (the five's are within their kinds').
- `WALL.json` gains `model` (the resolved one, also the settings' `@MODEL@`), `result_schema`, `brief_id` and `flow`
  (both null without an entry).

### The trees (S23)

Every tree: the archive less `tree-exclude.txt`. A brief with an entry: also less the entry's `tree_exclude` (fnmatch
on the repository path, as `tree-exclude.txt`). The selection (S5) stays "less `tree-exclude.txt`": the entry's globs
limit what a wall may read, not the writer's pool of places (a place is a name).

### Places (S16, S24)

`<runs>` is `GOV_INDEP_RUNS_DIR` or `~/gov-os-runs`; `EXP` = `<runs>/SANDBOX-GUARD-EXP-1`. **H**, the half's folder:
`tuning` → `EXP/tuning`; `held-out` → `<sets root>/fixtures/evaluation/sandbox-guard-exp-1/hidden` (the sealed
folder). Under H: `corpus/actions.jsonl` and `planted/cases.jsonl` (inputs; `planted/cases.jsonl` is also the writers'
destination); `labels/r1-sgx1-labeller/{rulebook.md,label_rules.py}`; `labels/r1-sgx1-labeller-2/rulebook-2.md`;
`labels/labels.jsonl`; `labels/labels-2.jsonl`; `labels/audit/<run>.map.json` and `labels/audit/<run>.decisions.jsonl`;
`labels/history/<any name>` (a replaced `labels.jsonl`); `labels/owner.jsonl`.

- `--set` names the half: writer 1 `tuning`, writer 2 `held-out`, the labellers and the auditor either; anything else
  **17**, nothing built (checked once the entry is known, after stage 10). `--round`: the writers and the auditor 1, the
  labellers 1 or 2. `--audit` stays required for the auditor kind, recorded only (no misses read).

### The staged inputs (S20, S24, S25, S27): `input/` holds exactly

| Flow | Round | `input/` |
|---|---|---|
| `sgx1-writer-1` | 1 | `selection.json` (S5) |
| `sgx1-writer-2` | 1 | `selection.json`, `seal.json` |
| `sgx1-labeller-1` | 1 | `half.json`, `actions.jsonl`, `cases.jsonl` |
| `sgx1-labeller-1` | 2 | the same, `round1/rulebook.md`, `round1/label_rules.py`, `script-labels.jsonl`, `sample.json` |
| `sgx1-labeller-2` | 1 | `half.json` |
| `sgx1-labeller-2` | 2 | `half.json`, `round1/rulebook-2.md`, `sample.jsonl` |
| `sgx1-overlap-auditor` | 1 | `half.json`, `disputes.jsonl`, `tickets.jsonl` |

- `half.json`: `{"half": <half>, "pin": <the 40-hex commit>}`; the auditor's also `"cases": <this run's disputes>`.
  Exactly these keys.
- `actions.jsonl` / `cases.jsonl`: H's `corpus/actions.jsonl` / `planted/cases.jsonl`, line by line in file order, each
  kept to `id role agent ticket wbs tool input cwd executable strata source` (and `rule_class` for a case); one JSON
  object per line (key order free). "The half's staged lines" below: the actions' then the cases'.
- `seal.json`: `{"sealed": true}` when the path map at `--commit` has `evaluation_sets.sandbox-guard-exp-1.hidden`
  holding `fixtures/evaluation/sandbox-guard-exp-1/hidden/**` and a `sets_root_hidden.hidden` glob covers it (the same
  glob, or one matching a path under that folder); else `{"sealed": false}` (commits B, PU, PC).
- `round1/`: H's `labels/r1-<brief id>/` files, byte for byte. Round 1's `counts.json` records each delivered file's
  sha256; round 2 takes the latest delivered round-1 run of the same brief sha256 and half from `<runs>/indep/labeller/`
  and refuses **10** when a file's sha256 differs, or when no round 1 was delivered.
- `sample.jsonl` (labeller 2, round 2): the half's staged lines whose `int(sha256((SEED + "overlap" +
  id).encode("utf-8")).hexdigest(), 16) % 10 == 0`, in order; SEED is the wall's `seed.txt` less its newline.
- `script-labels.jsonl`: the rule script's output lines, in order. `sample.json`: `{"ids": [...]}`, the half's staged
  ids whose `int(sha256((SEED + "labeller-sample" + id).encode("utf-8")).hexdigest(), 16) % 20 == 0`, in order.
- `disputes.jsonl`: the ids in both `labels.jsonl` and `labels-2.jsonl` whose `label` differs and that no
  `labels/audit/*.decisions.jsonl` names, sorted by id, the first 40; one line each, in that order: `{"id", "action":
  {role agent ticket wbs tool input cwd} (from the staged line), "x": {label rule_class clauses reason}, "y": {...}}`.
  **x/y:** `rng = random.Random(seed)`; for each case in that order, `rng.random() < 0.5` means x is labeller 1
  (`labels.jsonl`), else x is labeller 2. Nothing else of either labeller enters the wall.
- `tickets.jsonl`: one line per ticket a case's action names (its `ticket` matched to a ticket file's `id`, or its
  `wbs` to `wbs_id`), read from `.tickets/*.md` at `--commit`: `{"id", "role", "wbs_id", "allowed_paths"}` and nothing
  else; a name no ticket file holds gives no line; order free.
- **A missing input refuses 10 before anything is written:** H's `corpus/actions.jsonl` or `planted/cases.jsonl`
  (labeller 1), round 1's files or counts (round 2), `labels.jsonl` or `labels-2.jsonl` (the auditor).

### The rule script (S25; exit 18, reason `rules`)

- At labeller 1's round 2 the script runs round 1's delivered `label_rules.py` under `bwrap`: the program
  `GOV_INDEP_BWRAP` names (an absolute path; tests and the trial only), else `bwrap` on `PATH`; the interpreter
  `GOV_INDEP_RULES_PYTHON` names (absolute; tests and the trial only), else the one on the first line of
  `~/.local/bin/gov`; `-I`. Every namespace unshared (no network), `--die-with-parent`, nothing bound but the
  interpreter's own files (and the rule script) read-only, nothing writable; no new process (a fork or an exec inside
  fails); caps on CPU, memory and output, a wall-clock cap of at most 60 s. Stdin: the half's staged lines.
- The output must give every staged id exactly once: `{"id", "label": allow|refuse|ask, "rule_class": 1..14 (int),
  "clauses": [strings], "uncertain": bool}`. Anything else (a non-zero exit, a cap reached, an id missing, repeated or
  unknown, a bad value; `bwrap` or the interpreter missing or unable to start): **18**, nothing staged (no
  `script-labels.jsonl` or `sample.json` in the wall or its tar), no session; it may run before or after the wall is
  built (a refusal after B1 leaves what 13 leaves).

### The deliveries (S16, S26, S27): a temporary name, hashed, renamed; all or nothing

| Flow | Round | From `out/` | To | `delivered.to` |
|---|---|---|---|---|
| `sgx1-writer-1` | 1 | `cases.jsonl` | tuning H `planted/cases.jsonl` | `cases` |
| `sgx1-writer-2` | 1 | `cases.jsonl` | held-out H `planted/cases.jsonl` | `cases` |
| `sgx1-labeller-1` | 1 | `rulebook.md`, `label_rules.py` | H `labels/r1-sgx1-labeller/` | `round1` |
| `sgx1-labeller-1` | 2 | `hand-labels.jsonl`, merged | H `labels/labels.jsonl` | `labels` |
| `sgx1-labeller-2` | 1 | `rulebook-2.md` | H `labels/r1-sgx1-labeller-2/` | `round1` |
| `sgx1-labeller-2` | 2 | `labels-2.jsonl` (its bytes) | H `labels/labels-2.jsonl` | `labels` |
| `sgx1-overlap-auditor` | 1 | `decisions.jsonl`, mapped back | H `labels/audit/<run>.decisions.jsonl` (and below) | `decisions` |

- An existing destination file refuses **20** (the auditor's `labels.jsonl` and `owner.jsonl` excepted); nothing
  else changes under the sets root or `EXP` (the wall's tar aside). `out/aims.jsonl` stays in the tar only. A
  destination's missing folders are made (writer 1's case starts with no `EXP` at all; `labels/r1-<id>/` and
  `labels/history/` are made by their first delivery).
- `delivered.files`: the delivered `out/` files (round 1 of labeller 1: 2); `sha256`: one file's own (for labeller 1's
  round 2 the merged `labels.jsonl`'s, for the auditor the mapped-back decisions file's); several files: the sha256 of
  the lines `<file sha256>  <name>\n` sorted by name.
- **Labeller 1, round 2 (S26):** `out/hand-labels.jsonl`, lines `{"id", "label", "rule_class", "clauses", "reason"}`,
  must cover every id `script-labels.jsonl` marks uncertain, every id it puts in classes 1-13 and every `sample.json`
  id; else **20**, nothing written. The merge: one line per staged id, in the staged order, exactly `{"id", "label",
  "rule_class", "clauses", "reason", "how"}`: a hand line's values and `how: "hand"`, else the script's with
  `reason: ""` and `how: "script"`.
- **The overlap auditor (S27):** `out/decisions.jsonl` must hold one line per case, in the disputes' order, the same
  ids, exactly `id label rule_class basis agrees_with flag reason` (`label` allow|refuse|ask, `rule_class` 1-14, `basis`
  a list of strings, `agrees_with` x|y|neither, `flag` none|cannot-settle|may-change-verdict, `reason` empty exactly when
  the flag is `none`); else **20**, nothing under H changes. Delivered: each line as the auditor wrote it, `agrees_with`
  x or y replaced by `labeller-1` or `labeller-2` by the map; `labels/audit/<run>.map.json` = `{<id>: {"x": 1|2, "y":
  2|1}}` for the run's cases, written at delivery only (never by a dry build or a rejection, never in the wall);
  `labels.jsonl` rewritten, its old bytes first copied into `labels/history/` (one new file, its name free): flag `none`
  → the auditor's `label` and `how: "audit"`; flagged → `how: "owner"`; every other line unchanged; `owner.jsonl` gains
  one line per flagged case, in order, carrying its `id` (both labels and the decision; other keys free). **No
  `AUDITS.log` line, ever** (a memory writer's `last_audit` is untouched).

### The results (S28)

`indep-schemas/sgx1-<flow>-result.schema.json` for `writer-tuning`, `writer-heldout`, `labeller`, `labeller-2`,
`overlap-auditor`: each closed (`additionalProperties: false` at every level), numbers and fixed words only, the
brief's result forms (the labellers' round 1 and round 2 both); `by_class`, `cases`, `copies`, `near_miss` objects
keyed `"1"`..`"14"`; `stopped` the brief's words (writer 1's without `not-sealed`). `counts.json`'s `out` carries each
number of the result under its own key (an object of numbers as an object); `stopped` may be carried as its fixed
word; the counts schema stays closed. An extra field: **20**, its text nowhere (counts, output, log).

