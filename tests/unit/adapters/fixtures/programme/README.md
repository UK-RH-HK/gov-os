# A planted programme (W2-23)

A repository of its own, copied into a test's `tmp_path`: its own `CLAUDE.md`, `AGENTS.md` and Claude settings,
and a `.rulesync/` root rule for `gov adapters generate`.

The settings are kept here as `claude-settings.json`; a test copies them to `.claude/settings.json` in its copy
(a launched session may not write a file named `.claude/settings.json`, DEC-315). The untracked files and the
folder whose path holds a space are made by each test in `tmp_path` (a folder named `EXAMIN APP`).
