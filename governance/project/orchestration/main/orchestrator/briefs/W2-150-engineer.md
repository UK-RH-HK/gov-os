# W2-150 — the engineer's brief (senior): memory's import closure free of the gates (DAEO-ijf5)

You are a fresh, senior engineer for **W2-150** (`.tickets/DAEO-ijf5.md`). Read it whole, with S1 to S5, the failure
lines and both notes. The note "The test designer's discoveries placed here" matters most. This is D-6 part 2's code
item (P1-PLAN §A P1-6 item 1 and §D; DEC-1039 (2), DEC-1040 (1), DEC-1109 (2)). Background:
`governance/project/orchestration/packages/INVESTIGATION-1-parts/E.md` (E-2).

## The point
Memory's **static** import closure must reach no module of `gov.close`, no module of `gov.guard`, and not
`gov.decisions.checker`. Static means every import statement, at module level and inside functions. It starts from
every module of `gov.retrieval`, `gov.retrieve`, `gov.store` and `gov.secrets`. The test designer's red import paths
at the base, as its `gov accept` printed them:
- **loader:** `src/gov/store/loader.py:546` and `:599` → `gov.close.fingerprint`, then `close.select` →
  `guard.decide._match_pattern`, plus `tasks.tickets`.
- **retrieve.command:** `src/gov/retrieve/command.py:123` → `gov.decisions`, whose `__init__.py:3` pulls `checker`.
- **secrets:** `src/gov/secrets/__init__.py:48` → `gov.guard.runs` → `guard.decide` → …
- **measure:** `src/gov/retrieval/measure.py:74` → `gov.guard.reads` → `guard.decide` → …
- **The fifth edge:** `src/gov/retrieval/retrieve.py:39` and `supplementary.py:135` → `gov.guard.role_paths` →
  `guard.reads` → … (W2-13 S5's role filter).
- **A second route to `checker`:** `supplementary.py:56` → `gov.decisions.register` → `gov/decisions/__init__`, whose
  function-level imports of `tags` and `propagation` reach `checker`.

**The move (P1-PLAN §A):** move the small helpers memory uses into `gov.util` or `gov.store`, then have the old
modules re-import them.
- `of_commit`'s path classification;
- `_match_pattern`;
- `TICKETS_REL`;
- `runs.root`;
- `leave_out` and what `register` gives memory;
- the evaluation-set reading `measure.py` uses (`evaluation_sets`, `PolicyError`, `PATH_MAP_REL`, `SETS_KEY`,
  `set_fault`, `_Part`, `_ticket`);
- the path rules the role filter needs.

The behaviour stays identical, byte for byte. **Never hide an import from the walk:** no `importlib` or `__import__`
in place of an import statement. Untangle by moving names. Rules for the move:
- `guard/decide.py` may change only to import a moved name from `gov.util`. It is the hook's hot path: S4 says its
  import pulls nothing beyond `gov.guard`, `gov.util` and the standard library.
- `retrieval/synthesis.py` stays (DEC-953).
- No public behaviour changes, and no acceptance test outside `tests/acceptance/W2-150/` changes.

## Where you work
- `/home/usain/gov-os-worktrees/W2-150`, branch `w2/W2-150`. It was made from `w2/integrate` at `40a146e66`, with the
  designer's cases merged at `82faa2c89`.
- Your paths are the ticket's `allowed_paths` only: 16 files and folders, among them `src/gov/util/**` and
  `tests/unit/util/**`, plus `docs/changes/W2-150-evidence.md`. If a needed change falls outside them, **stop and
  name it**: do not edit it.
- **You never read `tests/acceptance/W2-150/`** (G-14; DEC-820 (c)). You see only `gov accept`'s results.
- **The exclusion line (DEC-1093 (2)):**
  - every recursive grep carries `--exclude-dir=W2-150`;
  - every Grep or Glob call that could reach the folder carries `!tests/acceptance/W2-150/**`;
  - find carries `-path '*/W2-150' -prune`.

## Verify
Run everything through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-150/src`, a scratch HOME (link `.local` into it) and
`PYTHONUSERBASE=/home/usain/.local`.
1. `python3 -m gov.cli.main accept W2-150 --root /home/usain/gov-os-worktrees/W2-150` must be all green. Today it is
   21 passed and 5 red.
2. New unit cases under `tests/unit/util/` for each moved helper (S5).
3. The touched packages' unit suites, scoped: `tests/unit/{util,store,close,guard,decisions,secrets,retrieve}` and
   the retrieval unit files that import a moved name. Use `select_tests.py` as `EMG-common.md` says, and run what
   the sandbox allows. Name what you could not run, such as socket cases. Never the full suite.
4. In `docs/changes/W2-150-evidence.md`, record:
   - the walk's module and line count before and after;
   - each moved name with its new home;
   - the unit counts.

Commit as you go.

## Rules
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them. `measure.py`'s code may be read; its data never.
- No GPU, model, network, installs or service.
- **DEC-1080:** use the Read and Grep tools, one simple command per Bash call, and no `cd … &&` chains.
- Waits and stops by pid or pgid only. Do not merge `w2/integrate`.
- Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-150` with
  `--trailer "Task: DAEO-ijf5" --trailer "Implements: DEC-1109, DEC-1039" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished.

## Return
Your whole return is your session's **final message**, in full. It holds:
- the twelve labelled fields of `EMG-common.md` (the sandbox and `ps` checks first);
- the commits and the moved names;
- `gov accept W2-150`'s counts per line;
- the unit counts, with every red named and whether it was red before.
