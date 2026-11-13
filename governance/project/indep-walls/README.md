# The walls' template (ACT-INDEP-WALLS-1, DEC-1101 (2))

The launch script (DEC-1101 (3) step 2) builds every independent session's walled folder from these files. They
change only by an ACT the owner approves; their sha256s are in `<sets root>/indep-walls/APPROVED`, and the launch script
refuses to build from a file that does not match.

| File | What |
|---|---|
| `settings.json.tmpl` | The wall's settings: allow its own folder (writes `out/` only); deny the shell, the web, subagents, memory's search, git, the repository, the worktrees, the run outputs, `~/.claude`, the rest of the sets root, the approved list and every other wall; the wall hook on every tool. |
| `wall_hook.py` | The wall's PreToolUse guard: reads and writes closed to the wall (links followed), writes into `out/` only, the tools named and no others, fail closed. |
| `CLAUDE.md.tmpl` | The session's standing note: its kind, its brief's sha256, its commit, its folder rules. |
| `kinds.yaml` | The job kinds (writer, checker, auditor, labeller): tools, inputs, what is delivered where, proposed budgets and timeouts. |
| `tree-exclude.txt` | The paths left out of every wall's plain tree (the evaluation sources and sets, the measure results). |

A wall: `<sets root>/indep-walls/<kind>/<run>/` holding `WALL.json`, `seed.txt`, `brief.md`, `CLAUDE.md`, `.claude/`,
`input/` and `out/` (the only writable folder); its plain tree at `~/gov-os-wall-trees/<kind>-<run>/` (read-only,
outside the sets root: the repository's own content, which the guard's walk of the hidden part must not count). The
session runs as `claude -p --restricted --settings <wall>/.claude/settings.json --add-dir <tree> --tools <the kind's>
--no-session-persistence --strict-mcp-config`, from the wall, so Claude Code's restricted mode confines its file tools
to the wall and its tree as well. A finished wall is packed into `indep-walls/<kind>/<run>.tar` (one file) and its tree
removed, so the hidden part stays far under the guard's 10,000-file walk.
