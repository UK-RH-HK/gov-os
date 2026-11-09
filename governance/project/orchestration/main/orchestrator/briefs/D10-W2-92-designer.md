# D-10's red-fix list: W2-92's unchanged-bundle case for a symbol the index does not hold (W2-92, DAEO-n0wb)

You are a fresh **independent test designer**, launched under W2-92's ticket (`.tickets/DAEO-n0wb.md`). D-6 found
this red at its base and put it on D-10's red-fix list. DEC-1109 (2) asks that the list be ready before D-10's full
run.

## The red (reproduced by the CTO tonight at integrate `b0bbd373f`)
- **The case:** `tests/acceptance/W2-92/test_w2_92_unchanged.py::test_u1_a_question_naming_no_record_or_symbol_gets_todays_bundle[unknown symbol]`.
- **The question:** "who calls w92_nowhere". It expects `_EMPTY`: no evidence, batches of size 0.
- **The bundle now holds one item:** `governance/project/path-map.yaml` lines 1-363, from the lexical route. The rest
  of the file: 8 passed.
- **The cause (the CTO's reading; confirm it):**
  - `w2_92_support.path_map()` copies **this repository's live path map** into the planted project.
  - Since ACT-OPERATOR-1 (`2a6462653`, DEC-1106 (3), DEC-1108 (5)), the live map holds a `write_refused` block. Its
    entries are `root: "~/.gov-os/guard-calls"` and the `why` "the guard's call log …".
  - The planted index therefore matches "calls".
  - So the case depends on the live path map's wording, not on what it tests: a question naming no record or
    symbol gets today's bundle.
- **To run it:** `tests/conftest.py` takes the real `codebase-memory-mcp` off `PATH` for every suite but W1-16's and
  W1-20's (W2-56 S1). Without the tool, this whole file skips. Run with `CODEINTEL_OFF_PATH=` set to the empty
  string, so the tool stays on `PATH`. That is how the CTO reproduced it.

## The task
1. Make the planted project's path map independent of the live map's free text, so that only the planted corpus
   answers the questions:
   - for example, keep the live map's structure but drop or neutralise its prose fields (`why`, `provenance`, the
     like);
   - or build the map the suite needs from the keys it uses.
   - Choose, and say why.
   - The premise of every `test_u*` case stays: today's bundle, item for item. Lower no expectation; change no
     pinned bundle unless the change follows from the map alone, and then say exactly which and why.
2. Check the other W2-92 files that use `path_map()` or `PATH_MAP_REL` (`links_corpus()` at about line 797, and the
   others) still pass, with the tool on `PATH` as above:
   - run `tests/acceptance/W2-92` whole, with and without `CODEINTEL_OFF_PATH=`;
   - report both counts. A case red before and after for another reason is named, not fixed.
3. One line in W2-92's README for the revision.
4. Every commit carries `--trailer "Rewrite-Reason: DEC-1106 (3), DEC-1108 (5): the live path map gained write_refused (the guard's call log), and the planted copy of it matched an unrelated question"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-92-d10-tests`, branch `w2/W2-92-d10-tests`, at integrate `adec4718a`.
- Write only `tests/acceptance/W2-92/**`.
- Do not read W2-92's implementation (`src/gov/store/loader.py`, `src/gov/retrieval/graph_route.py`, `code_route.py`,
  `retrieve.py`): DEC-820 (c).
- Run through the heavy slot (`EMG-common.md`), with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-d10-tests/src` and `TMPDIR=/tmp/gov-os-emg-w92d10`;
  - `python3 -m pytest tests/acceptance/W2-92 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.
  - If the code-graph tool cannot start in your sandbox, say so with its error. Then run what does run, and the CTO
    runs the rest.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no model, no installs, never the full suite.
- Commit on `w2/W2-92-d10-tests` only, with `--trailer "Task: DAEO-n0wb" --trailer "Implements: DEC-1109"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 30 minutes. Return the twelve fields, short:
  - the cause confirmed or refuted;
  - the choice and why;
  - the counts before and after, with and without the tool;
  - the head commit.
