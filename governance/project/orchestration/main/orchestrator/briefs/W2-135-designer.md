# W2-135 — the independent test designer's brief (DAEO-c4pb)

You are the independent test designer for **W2-135** (`.tickets/DAEO-c4pb.md`): a bundle item over 4,000 characters is
sent as its first 4,000, marked cut, its lines cited unchanged. Read the ticket in full first. Its KPI lines S1 to S3
are what you test. S4 is the CTO's check after the re-pin.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-135-tests`, branch `w2/W2-135-tests`, made from `w2/integrate`.
- You write only `tests/acceptance/W2-135/`: the cases, a `conftest.py` if needed, and a `README.md` whose map the
  runner reads. Its header is `| KPI line | Test (node id) | On integrate | Why |`, with one id such as `S1` in each KPI
  cell and the test in backticks (as `tests/acceptance/W2-133/README.md`).
- You may read any code on `w2/integrate` except this ticket's implementation (there is none yet):
  `src/gov/retrieval/retrieve.py` (`retrieve()`'s inner `item()`, the budget), `src/gov/retrieval/chunking.py`, and the
  existing tests `tests/acceptance/W2-133/` and `tests/unit/retrieval/test_w2_131_register_ids.py` for how a planted
  repository and its store are built.

## What the cases must show (from the ticket)
- **S1:** a planted repository with a one-line JSON file of 24,575 characters, and a Markdown file holding one line of
  10,631 characters among ordinary lines. A query that reaches each sends an item whose `text` is its first 4,000
  characters and whose `cut` is `{"chars": <full length>, "sent": 4000}`. Its `path`, `start_line`, `end_line`, `id`,
  `chunk_id` and `sha256` are as today (the sha256 of the full span). Red on integrate: today the text is whole.
- **S2:** an item at or under 4,000 characters is as today, with no `cut` key. Green, a guard.
- **S3:** nothing else changes: the same items in the same order, the batches, the expansions with their left-out
  spans, the repeats, the gaps, the continuation and the budget's `used` (counted on the full text, as today); the
  reranker's input unchanged. Compare with today's code on the same planted repository, the cut text and the `cut` key
  apart. Green, a guard.
- Say for each case whether it is red on integrate for the right reason, or a green guard.

## Rules
- No GPU, no model: the planted store uses the test fixtures' stand-in embedder or the lexical route alone, as the
  existing tests do. No `gov retrieve` on the real repository.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases through the heavy slot that `EMG-common.md` names, with `PYTHONUSERBASE=/home/usain/.local`, and run
  `python3 -m gov.cli.main accept W2-135 --root <your worktree>` to show the runner reads your map.
- **DEC-1080:**
  - read with the Read and Grep tools;
  - one simple command per Bash call;
  - no `cd … &&` chains and no `git -C`;
  - one line before any command that will ask for permission.
- **Commit** on `w2/W2-135-tests` with
  `--trailer "Task: DAEO-c4pb" --trailer "Implements: DEC-1086" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`, with:
- the case list (node id, KPI line, red or green on integrate, and why);
- the commit;
- `gov accept`'s counts;
- anything untestable or ambiguous, as `discoveries`.
