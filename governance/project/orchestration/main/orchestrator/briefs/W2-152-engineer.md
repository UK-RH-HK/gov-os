# W2-152 — the engineer's brief (DAEO-o5x1)

You are a fresh engineer for **W2-152** (`.tickets/DAEO-o5x1.md`): `gov brief`, a filled brief from the ticket and
the facts file, refused when the ticket is not READY by code. Read the ticket in full first: its ten KPI lines, three
failure lines and **its body's "Interface" and "Clarified after the test design" sections**. They fix the command
form, the inputs, the placeholders, the role → template map, what counts as a verify, the output and refusal forms,
and `ready.new_since`. Follow them. Then read W2-128's ticket body, "Interface and rounds" (the placeholder syntax,
`keys.yaml`, the facts file's shape), and `R3-TEMPLATES.md` §B ("Filling"), §D TPL-3 and TPL-5. The templates are in
`template/governance/kernel/templates/`, the facts in `governance/project/facts.yaml`.

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-152`, branch `w2/W2-152`: `w2/integrate` at `61231e61` with
  the designer's 56 cases merged (TESTS-READY `b08ede6890c6`).
- **Your paths:** the ticket's `allowed_paths`: `src/gov/brief/**` (a `command.py` there is how the CLI finds
  `gov brief`; read `src/gov/cli/main.py` for the form, and an existing command module such as `src/gov/links/` for
  how one declares itself and raises `GovError`), `tests/unit/brief/**` (your builder tests), `governance/project/facts.yaml`
  (only `ready.new_since`, quoted), `template/governance/kernel/schemas/facts.schema.json`,
  `docs/changes/W2-152-evidence.md`.
- **You never read `tests/acceptance/W2-152/`** (DEC-820 (c)): run those cases only through
  `python3 -m gov.cli.main accept W2-152 --root /home/usain/gov-os-worktrees/W2-152` and read only its results. If it
  crashes in the sandbox (an empty `HOME` hides pytest), run
  `python3 -m pytest tests/acceptance/W2-152 -q -p no:cacheprovider -rf` with `PYTHONUSERBASE=/home/usain/.local`
  and read only the result lines. Every Grep or Glob call that could reach that folder carries
  `!tests/acceptance/W2-152/**`, and every recursive Bash search `--exclude-dir=W2-152`.

## Rules
- Standard library plus what `src/gov` already uses (PyYAML, jsonschema). No installs. No network, model or GPU, and
  no `gov retrieve` in the sandbox.
- `gov brief` is read-only (F3): it writes no file and reads only the ticket files, `facts.yaml`, the kernel
  templates with `keys.yaml`, the `--part`/`--repair` files and the CLI's own configuration.
- Deterministic (S1, F1): no time, no randomness, no environment-dependent ordering in the output.
- Proportion (DEC-135): nothing beyond the KPI lines. Keep it within about 400 lines of code (`est_loc` 380).
- Also run W2-128's cases, which must stay green (S10):
  `python3 -m gov.cli.main accept W2-128 --root /home/usain/gov-os-worktrees/W2-152`. Run your unit tests too, and
  `python3 -m gov.check.schema`. No whole-suite run. Every whole-folder pytest run adds
  `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`.
- Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own, different words;
  then answer from both, with path and lines, or say "not found".
- **DEC-1080:** Read and Grep tools; one simple command per Bash call; no `cd … &&` chains. Long jobs in the
  background, then wait.
- **Do not merge `w2/integrate` yourself.** Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-152`, only your paths, with
  `--trailer "Task: DAEO-o5x1" --trailer "Implements: DEC-1050, DEC-1052, DEC-1083, DEC-1088" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- An interface point the ticket leaves open: choose the simplest reading and name it in `discoveries`.

## Return
Your final message, in full:
- the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
- the files changed and the line count;
- `gov accept W2-152`'s counts, with each failing case's node id and message;
- `gov accept W2-128`'s counts;
- the unit tests' counts and the schema check's output.
