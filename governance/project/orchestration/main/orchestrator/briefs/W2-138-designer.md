# W2-138 — the independent test designer's brief (DAEO-rmhj)

You are the independent test designer for **W2-138** (`.tickets/DAEO-rmhj.md`): every search result names the store's
commit and folder, the store is resolved once per search, `CONTINUATION_INVALID` names both commits, each item's
sha256 is the hash of its own lines at that commit, and the retrieval skill gains one line. Read the ticket in full
first. Its KPI lines S1 to S5 are what you test.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-138-tests`, branch `w2/W2-138-tests`, made from `w2/integrate`.
- You write only `tests/acceptance/W2-138/`: the cases, a `conftest.py` if needed, and a `README.md` whose map the
  runner reads. Its header is `| KPI line | Test (node id) | On integrate | Why |`, with one id such as `S1` in each KPI
  cell and the test in backticks (as `tests/acceptance/W2-133/README.md`).
- You may read any code on `w2/integrate` (there is no implementation of this ticket yet): `src/gov/retrieve/command.py`
  (`_store_root`, `GOV_STORE`, the envelope), `src/gov/retrieval/retrieve.py` (the result, the continuation),
  `src/gov/retrieval/validate.py`, `src/gov/rebuild/integration.py` (the double-buffered link), and the existing tests
  `tests/acceptance/W2-116/`, `tests/acceptance/W2-133/` and `tests/unit/retrieval/test_w2_131_register_ids.py` for how a
  planted repository, its store and a link are built.

## What the cases must show (from the ticket)
- **S1:** a planted store built at a known commit; `--json` has `result.store.commit` (the full commit) and
  `result.store.root` (the folder, the link resolved); the text form's first line `store: <12 digits> (<folder>)`.
  Through a link (`--root <link>` and `GOV_STORE=<link>` with no `--root`) the root is the half the link points to.
- **S2:** one search reads one folder for every facet even when the link is switched between the facets' reads (use a
  seam or monkeypatch to switch the link mid-search; say which).
- **S3:** a continuation token made on one store and replayed on another is refused `CONTINUATION_INVALID`, and the
  message or details name both commits.
- **S4:** for every evidence item of a planted search, sha256 of lines `start_line`..`end_line` of `path` at
  `result.store.commit` equals the item's `sha256` (state the exact byte rule you derive: line endings, trailing
  newline). This may be green on integrate (the hash exists today); then it is a guard of the contract.
- **S5:** the retrieval skill `template/governance/kernel/skills/retrieval/SKILL.md` step 5 holds the line: compare
  each item's sha256 with the same lines in your own tree; if they differ, read `git show <commit>:<path>`, and never
  cite the store's line numbers as your tree's. A text check (key phrases), red on integrate.
- Say for each case whether it is red on integrate for the right reason, or a green guard.

## Rules
- No GPU, no model: the planted store uses the test fixtures' stand-in embedder or the lexical route alone, as the
  existing tests do. No `gov retrieve` on the real repository.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases through the heavy slot that `EMG-common.md` names, with `PYTHONUSERBASE=/home/usain/.local`, and run
  `python3 -m gov.cli.main accept W2-138 --root <your worktree>` to show the runner reads your map.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains and no
  `git -C`; one line before any command that will ask for permission.
- **Commit** on `w2/W2-138-tests` with
  `--trailer "Task: DAEO-rmhj" --trailer "Implements: DEC-1090" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`, with the case list (node id, KPI line, red or green on integrate, and
why), the commit, `gov accept`'s counts, and anything untestable or ambiguous as `discoveries`.
