Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-150/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-150 — the narrow review of the follow-up: S6, one source each (DAEO-ijf5)

You are a fresh, read-only independent reviewer. **Narrow scope: S6** in `.tickets/DAEO-ijf5.md`, the follow-up. Read
S6, the three new paths and the note "The follow-up placed here". The rest of W2-150 was reviewed READY at `b85efb879`
and is not re-opened here. READY is computed by `verdict.py` from your block.

## What to review
- **The branch:** `w2/W2-150`, head `892c6f851`. Read `git diff e7d471f46..892c6f851`:
  - `ee700af36`: `_Glob` and `load_yaml_unique` defined only in `gov.util.parts`, and the git runner only in the new
    `gov.util.gitrun`; `guard/protected.py`, `guard/heldout.py`, `close/repo.py` and `store/loader.py` import them;
    unit cases in `tests/unit/util/test_w2_150_gitrun.py`;
  - `892c6f851`: the evidence section.
- **The designer's S6 cases:** `tests/acceptance/W2-150/test_w2_150_one_source.py` (`389b264d`, merged at
  `e7d471f46`).
- **The engineer's runs:** `gov accept W2-150` 32/32; `tests/unit/{util,guard,close,store}` 1,906 passed and 1 failed,
  that one a known base red (`test_w2_141_search.py::test_the_staged_pretooluse_adds_only_glob_to_g14s_tools`).

## Check
1. **Byte for byte:** compare each single source with both former copies (`git show b85efb879:<path>` and
   `git show 40a146e66:<path>`):
   - glob matching;
   - the twice-written-key refusal;
   - `git`'s whole call: the environment scrub (DEC-500), the pinned configuration, `--no-replace-objects`, standard
     input, `ok` codes, and the error type and message.

   Is any guard, held-out or close behaviour different?
2. **One source:** there is no other definition in `src/gov`, and each old name `is` the new object.
3. **No gate in memory's closure:** S1 still holds, and `gov.util.gitrun` and `gov.util.parts` import nothing from
   the gates.
4. **The hook:** `.claude/hooks/pretooluse.py` imports `guard.heldout`, and so now loads `gov.util.parts`. Does that
   change any decision or deadline? Is there any import cycle at the hook's entry?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding is `scope: in` only if it
concerns S6.

## Write and return
- **You write nothing.**
- You may run tests read-only through the heavy slot, with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-150/src` and
  an empty scratch HOME (`PYTHONUSERBASE=/home/usain/.local`). No GPU. Single simple Bash commands (DEC-1080).
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them. Read the code that guards them, never their data.
- **Search again once (DEC-1092 (1)).**
- **Your record is your session's final message.** It holds:
  - the twelve labelled fields of `EMG-common.md`;
  - your answers to checks 1-4;
  - every finding, with its two lines and its scope;
  - the fenced `verdict` block:
    `{"kpis": [{"kpi": "S6", "verdict": "pass|fail", "findings": [...]}]}`.
