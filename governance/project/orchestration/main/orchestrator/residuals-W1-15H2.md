
## W1-15 second run: the hooks source's command lines start from any folder (2026-10-10; DEC-603, DEC-608, DEC-609)

Probed head `ca734550`, merged directly. The seven command lines of `template/.rulesync/hooks.jsonc` are the kernel template's form exactly, with no `PYTHONPATH` prefix.

- **`gov` must be installed for the user who runs a project's sessions, on every machine and runner (adoption notes, exit package).** Without it the pre-call hook blocks every call (fails closed, with a finding but no reason on its error output), and the stop program ends silent with no checkpoint. A project that holds `gov` only under its own `src`, with none installed, is in that position: this repository on a fresh machine. Wave 2 list: the three hook programs that do not look in the project's `src` look there after the installed package.
- **A product's own package named `gov` under `src`** no longer reaches the guard, the containment check or the stop program. The session-start and pre-compaction programs still put the project's `src` first and import it: no checkpoint before a compaction, no resume part, and its code runs. A deliberate or unusual shape, older than the run. Wave 2 list.
- **A relative `PYTHONPATH=src` in a session's environment** brings that shape back from the project's root only. In this repository's worktrees the `gov` a hook runs is the worktree's from the root and the main tree's (the installed one) after a `cd`.
- **`CLAUDE_PROJECT_DIR` unset or empty:** all seven commands exit 2. The harness always sets it.
- **Not held by a case:** that the harness gives the variable to the shell and does not put it into the command text. The orchestrator's measurement on an adopted clone uses a project path with a space.
- A helper of W1-38's support module returns none for `subagentstop.py`; nothing compares that entry through it. No case holds this repository's own rulesync hooks source equal to the template's.
- **In a worktree without a built store** the trailers check reads one commit's `Implements:` ids as unresolved that resolve in the main tree (`cf84b1b2` of `DAEO-2lwj`); the count is the same before and after this run.
