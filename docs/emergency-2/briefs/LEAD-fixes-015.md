# Lead brief: five small fixes and the Contract's D6 wording for release 0.1.5 (fixes under their owning tickets; one chore)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it. Name: `fixes-015`; worktree
`/home/usain/gov-os-worktrees/E2-fixes-015`, branch `e2/fixes-015` from `w2/integrate` (it already holds DEC-1225's
launcher changes from `e2/models-rubric`). **Do not merge.** Every helper Sonnet (DEC-1225). Each fix: failing test
first by the independent test designer, then the engineer; one commit series per fix with its own `Task:` and `Fix:`
trailers; record each in its owning ticket's file as a `## Fix: ...` section (the form of `.tickets/DAEO-xm6l.md`'s last
section). Find each owning ticket with `gov retrieve` and `grep -l "^wbs_id: W.-N" .tickets/*.md`.

## The fixes
- **F1 Leads start with no claude.ai connectors** (audit 3, `docs/emergency-2/audits/E2-AUDIT-3-MCP-TOOLS.md`): `gov
  launch` starts workers with `--strict-mcp-config` but leads without it (`src/gov/launch/launcher.py` about `:1130`,
  `:1233` on the old base; read the current lines), so a lead and its helpers get the owner's Gmail, Drive, Calendar
  and Docs connectors. Every session `gov launch` starts carries `--strict-mcp-config`. Verify: planted launches of a
  lead, a fix lead and a chore lead record the flag. Owner: the launcher's ticket (W2-201 `DAEO-k1us` or whichever
  ticket owns `gov launch`'s lead start; say which).
- **F2 `gov doctor` checks a tool installed in its own folder** (audit 3's new problem): the registry entries
  `node-22.23.5` and `rea-agents` (`governance/project/tool-registry.yaml`, the last two) are reported `ok: false`
  because doctor finds a binary only by `TOOL_BINARIES` or a `PATH=<prefix>:$PATH` in the install line
  (`src/gov/doctor/command.py:38-46`, `:86-95`, `:440-540`). Make doctor find and version both, with **no schema change**
  (a kit schema added or removed is not a patch: RB-7 P5): for example map `node-22.23.5` to `node` under its nvm folder
  and `rea-agents` to `tool/node_modules/.bin/rea` run with that node; a registry note or install line may change. Also:
  a `PATH=` prefix taken from one tool's install line must not be used to find another tool of the same binary name at
  the wrong version (the v22.23.5 prefix must never answer for `node` v22.23.3). Owner: W2-22 `DAEO-xm6l`.
- **F3 `gov --version` prints `commit unknown`** in a pinned install: it prints the commit the wheel was built from.
  Owner: the ticket of `gov --version` / the release build.
- **F4 `context_watch.py` registered twice after `gov update`** (EXAMIN's report 28, in its `REQUESTS.md` at
  `/home/usain/gov-os-runs/W2-27/examin/REQUESTS.md`, read only): `gov update` never adds a hook entry already present;
  an update on a repository that has it twice leaves it once. Owner: W2-17 `DAEO-sdhj`.
- **F5 `gov accept W2-16` gives `ACCEPT_NO_MAP`:** its README maps no KPI line. The test designer writes the map
  (README form other folders use) so `gov accept W2-16` runs its tests; no test is changed. Owner: W2-16.
- **C1 (chore, Sonnet text checked by the CTO before it lands): the Contract's D6 wording** (the owner's DEC-1227 D6 (a),
  landed as `9a4adb350`). Replace in `docs/contract/contract.yaml`, `docs/contract/CONTRACT_v5.md` and
  `docs/contract/capabilities/CAP-25.md` (and any generated copy the Contract's generator writes; run it):
  - CAP-25's acceptance "…and exits non-zero on drift;" → "`gov doctor --json` lists pinned versus found versions and
    exits non-zero on a failure or on drift, except that a difference of patch version only (same major and minor)
    between the Claude Code CLI and the VS Code extension is reported as drift and exits 0 (DEC-1227 D6 (a));"
  - CAP-61.e's "…the CLI used for headless runs is aligned with the VS Code extension's bundled version" → "…the CLI
    used for headless runs has the same major and minor version as the VS Code extension's bundled version (a
    difference of patch version only is reported by `gov doctor` as drift, exit 0; a larger difference fails, exit 3)
    — DEC-153; DEC-1227 D6 (a); EXP-001 §5.5".
  Bump the Contract's minor version as its history table does, citing DEC-1227 D6 (a). Commit `Class: C`,
  `Role: orchestrator`. Tests that pin the Contract's text: run them; a pin of the old words is revised by the test
  designer with a Rewrite-Reason naming DEC-1227 D6.

## Green and return
`gov accept` of each owning ticket green; `tests/unit/launch`, `tests/unit/doctor`, `tests/unit/update` (or where
`gov update` lives), the Contract's tests, W1-06, W1-48, W2-22, `tests/unit/optin`. Return: branch and head; F1 to F5
and C1, each with its owning ticket and tests; reds not yours; the trial figures (runs to green, send-backs, minutes).
