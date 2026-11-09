# W2-129 — the engineer's brief, D-6 part 2: S17, planted ids in test fixtures (DAEO-q7lk)

You are a fresh engineer for **W2-129** (`.tickets/DAEO-q7lk.md`: read it, with its new line **S17**, its new failure
line and its "D-6 part 2 placed here" note). `gov links` is merged into `w2/integrate`. **One small pass, S17 only.**

## The point
In a **Python test file** (`tests/**/*.py`) that parses, an id inside a **string literal that is not a docstring** is a
planted fixture id. Such literals are plain, triple-quoted and f-strings, assigned or not. A docstring is the first
statement's string of a module, class or function.
- **UNKNOWN_ID:** a planted id gives none.
- **ENFORCES_SUPERSEDED:** a finding that W2-55's propagation gives for a test-file line is **carried** into
  `gov links`' output only when the old id also stands on that line **outside** such a literal (a comment, a
  docstring, code).
- **Judged as today:** ids in comments and docstrings, every non-Python test file (README.md, `*.json`, `*.yaml`,
  `*.txt`), and a `.py` test file that does not parse.
- **W2-55's `gov.decisions.propagation` is not changed.** The filter is in `gov links`' carrying.

Hint (yours to judge): Python's `tokenize` gives each STRING token's start and end, and f-string parts on 3.12. `ast`
finds the docstrings. Per line, the ids outside planted spans are what count. Parse each test file once per run, and
keep `gov links --all` under 10 s (S15). Today it takes about 3 s.

**The interface line the designer wrote (its README):**
> **S17's places (DEC-1109 (2)):** in a `tests/**/*.py` file that parses, an id inside a string literal that is not a
> docstring (a plain, triple-quoted or f-string, assigned or not) gives no UNKNOWN_ID line, and an ENFORCES_SUPERSEDED
> line at `<path>:<line>` is printed only when the old id also stands on that line outside such a literal (a comment,
> a docstring, code); "a docstring" is the first statement's string of a module, class or function. Ids in comments
> and docstrings, every non-Python file under `tests/` (`README.md`, `*.json`, `*.yaml`, `*.txt`) and a `.py` file
> that does not parse give the same lines as before, in the same four ` | ` fields; the first field holds the id.
> `python3 -m gov.decisions.propagation`, run in the repository, still prints every line it printed before.

## Where you work
- `/home/usain/gov-os-worktrees/W2-129-d6`, branch `w2/W2-129-d6`. It was made from `w2/integrate` at `26c3133aa`,
  with the designer's cases merged at `7940fad46`.
- Your paths are the ticket's `allowed_paths`: `src/gov/links/**`, `tests/unit/links/**` and
  `docs/research/W2-129-links.md`.
- **You never read `tests/acceptance/W2-129/`** (G-14; DEC-820 (c)). You see only `gov accept`'s results.
- **The exclusion line (DEC-1093 (2)), by base name:**
  - every recursive grep carries `--exclude-dir=W2-129`;
  - every Grep or Glob call that could reach the folder carries `!tests/acceptance/W2-129/**`;
  - find carries `-path '*/W2-129' -prune`.

  Start searches from relative paths inside your worktree. If a search shows you a line of the cases anyway, stop and
  say so.

## Verify
Run everything through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-129-d6/src` and a scratch HOME (link `.local/lib` to the user site).
1. Your unit cases in `tests/unit/links/`.
2. `python3 -m gov.cli.main accept W2-129 --root /home/usain/gov-os-worktrees/W2-129-d6`. All lines must be green.
   Today only success-17 and failure-7 are red, 2 cases.
3. `python3 -m gov.cli.main links --all` in your worktree, before and after. Record the counts by code and role, and
   the median of five `--all` timings. Today, for the test designer: UNKNOWN_ID 557, ENFORCES_SUPERSEDED 73.

Add a short "S17 (D-6 part 2, DEC-1109 (2))" section to `docs/research/W2-129-links.md`, with these figures. Commit
as you go.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No GPU, model, network, installs or service.
- **DEC-1080:** use the Read and Grep tools, one simple command per Bash call, and no `cd … &&` chains.
- Waits and stops by pid or pgid only. Do not merge `w2/integrate`.
- Never touch `tests/acceptance/**`, `.tickets/`, `.claude/` or `src/gov/decisions/**`.
- **Commit** on `w2/W2-129-d6` with
  `--trailer "Task: DAEO-q7lk" --trailer "Implements: DEC-1109" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished.

## Return
Your whole return is your session's **final message**, in full. The launcher keeps it, and it is the record. It holds:
- the twelve labelled fields of `EMG-common.md` (the sandbox and `ps` checks first);
- the change (commits, unit cases);
- `gov accept W2-129`'s counts per line;
- the `--all` counts and timing, before and after;
- every red, named.
