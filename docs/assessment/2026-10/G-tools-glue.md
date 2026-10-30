# Lens G: The tools we chose to glue, not build

## 1. Header

- **Lens:** G, "The tools we chose to glue, not build", of the owner's October 2026 assessment of the Gov OS.
- **Auditor:** an independent auditor in a fresh, read-only session (`GOV_ROLE=independent-auditor`).
- **Date:** 2026-10-19.
- **Head:** `fecb870c` on `w2/integrate`. The main tree and my clone were both at this commit (`git rev-parse HEAD` in each).
- **Branch read:** `w2/integrate`. Contract v4.2, on `w2/W2-49`, was not read (Limits, item 11).
- **Uncommitted text, read as it stands:** the staged entries DEC-813 to DEC-817 in `docs/DECISION_REGISTER.md`, `docs/plan/WAVE_2_WBS.md` and `docs/plan/WAVE_2_LIST.md`.

### Words used in this report

- **Gov OS:** the governance system this repository builds.
- **`gov`:** its Python command line (`src/gov/`). It is installed in "editable" form: the `gov` command runs whatever code is in this working tree (DEC-605).
- **Glue:** our code that connects a selected tool to the rest of the Gov OS. **Build:** our code that does a job itself.
- **Kernel:** the governance files a project receives from the template (`template/governance/kernel/`): role files, skills, hooks, schemas and checks.
- **Hook:** a program that Claude Code (the agent program every session runs in) starts before or after an agent's action.
  - The **guard** is the hook that allows or refuses each tool call (`src/gov/guard/`).
  - **Containment** is the hook that reports writes outside a ticket's scope.
- **Ticket:** one unit of work, a file in `.tickets/`, handled with the `tk` tool. **Close:** `gov close`, which judges a finished ticket by running its tests and checks.
- **Sandbox:** the operating-system boundary Claude Code puts around a session's shell commands (bubblewrap on Linux). Only workers started with `gov launch` run in one today.
- **Wave:** a delivery period. Wave 2 is current and paused. **Round:** one more cycle of tests, fix and review on a ticket.
- **References:**
  - **DEC-n:** an entry of the decision register.
  - **CAP-n:** a Contract requirement.
  - **W2-n:** a Wave 2 ticket (`docs/plan/WAVE_2_WBS.md`).
  - **W2-H/M/Lnnn:** a row of the Wave 2 list (`docs/plan/WAVE_2_LIST.md`).
- **Registry:** the tool registry, `governance/project/tool-registry.yaml` (23 entries). **Doctor:** `gov doctor`, which compares installed tools with the registry.
- **S0b2:** the Wave 1 trial that chose the tools (ADR-0002, DEC-074).
- **Lines:** all code sizes in this report are non-blank lines.

### What I read

- **Stack decisions:**
  - ADR-0002 (architecture and stack) and ADR-0001 (threat model);
  - the registry and its schema;
  - the decision register: every entry this report cites, found by keyword searches for the stack's tools, sizes and installs.
- **Wave 1 research, opened by exact path only (DEC-383, DEC-723):** `~/gov-os-workbench/s0b2/out/RESULTS.md`, `GLUE_REQUIREMENTS.md`, `TOOL_REGISTRY.yaml` and `~/gov-os-workbench/s0b2/sandbox/_reports/codeintel.md`.
- **Plan:**
  - the WBS cards this report cites, and the WBS totals;
  - the list rows named in the findings.
- **Code, in my clone:**
  - `gov` modules: `codeintel/`, `closure/`, `adopt/stages.py`, `adopt/legacy.py`, `retrieval/lexical.py`, `check/schema.py`, `check/runner.py`, `close/command.py` with its two pytest plugins, `close/tool.py`, `tasks/`, `checkpoint/`, `guard/` (`decide.py`, `protected.py`, `heldout.py`, `install.py`), `telemetry/counter.py`, `telemetry/sessionlog.py`, `launch/launcher.py`, `doctor/command.py`, `ci/command.py`, `secrets/__init__.py` and `adapters/portability.py`;
  - the kernel hooks `sessionstart.py` and `precompact.py`;
  - project files: `lefthook.yml`, `.github/workflows/ci.yml`, `pyproject.toml`, `copier.yml`, `.rulesync/`, `template/openspec/` and the vendored Superpowers record.
- **Other lens reports, so as not to repeat them:** A (purpose and roadmap), B (memory and retrieval), D (tool staging), E (roles and context) and F (models and context).
- **Logs and transcripts:**
  - `.gov-runtime/scratch/orchestrator/log/` (close and share records);
  - session transcripts under `~/.claude/projects/` (counts only).
- **Web:** the tools' own documentation, listed under "Web sources".

### What I ran

Every script is in `/tmp/gov-os-assessment-G/`, and every output is in `/tmp/gov-os-assessment-G/runs/`. Nothing in the repository was changed.

| Run | Command | Where | Code it ran |
|---|---|---|---|
| G-0 | `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS /tmp/gov-os-assessment-G/repo`; then `git rev-parse HEAD` in both trees | scratch | git |
| G-1 | `PYTHONPATH=/tmp/gov-os-assessment-G/repo/src python3 -m gov.cli.main doctor --json`, with `TMPDIR`, `UV_CACHE_DIR` and `PYTHONDONTWRITEBYTECODE=1` set; output `runs/doctor.json` | in the clone | the clone's `gov`, not the editable install |
| G-2 | read-only checks of the installs: `command -v` for 22 tool names on the default PATH; `ls -la` of the Node v22.23.3 `bin` folder; `npm ls -g` under Node v22 and v18; `ls -d ~/.cargo/bin/rustup ~/.rustup` and `ls ~/.cache/`; `sha256sum` of 15 installed files against the registry (all matched) and of both `tk` copies; `openspec --version` by its path, with the default PATH; package versions of `/usr/bin/python3` through `importlib.metadata`; `ls`, `readlink -f` and `du -shL` of the reranker model's cache folder | read-only | the installed tools |
| G-3 | `bwrap --ro-bind / / --tmpfs /tmp --bind /tmp/gov-os-assessment-G … --unshare-pid --unshare-net --setenv CBM_CACHE_DIR /tmp/gov-os-assessment-G/cbm/home --setenv CBM_RUNTIME_DIR /tmp/gov-os-assessment-G/cbm/run python3 -I -B cbm_probe.py`, then the same with `cbm_trace.py`. The resource gate was checked in the same command. | a bubblewrap sandbox, over a copy of the main tree's code-index home (sha256 checked against the original) | `codebase-memory-mcp` 0.11.0 in its CLI mode (one process per call) |
| G-4 | probe: `PYTHONPATH=<clone>/src python3 -B ../schema_probe.py`, run in `/tmp/gov-os-assessment-G/schema-probe/` (one planted ticket); sweep: `schema_sweep.py <clone>` over the 558 records the check reads | scratch | the clone's `gov.check.schema`; the system `jsonschema` 4.10.3 with the kernel's own schemas |
| G-5 | `python3 -I -B heredoc_probe.py <clone>`: calls the guard's `gov.guard.decide.lift_refusal` on six command strings. Nothing is executed. | scratch | the clone's guard |
| G-6 | `scan_tools.py`, `scan_cmds.py`, `scan_skill_calls.py`, `scan_resume.py`, `scan_refusals.py` (a loose first count, superseded), its strict recount `scan_refusals2.py` and the count by shape `scan_refusals3.py`, over `~/.claude/projects/`, Gov OS folders only (`-home-usain-Dynamic-Agentic-Engineering-OS*`, `-home-usain-gov-os-worktrees*`, `-home-usain-gov-os-runs*`): 1,103 transcript files, 2026-09-17 to 2026-10-19. A first `scan_tools.py` run over all projects is not used | read-only | counts only; no command text printed |
| G-7 | `measure_glue.py <clone>` and `measure_parts.py <clone>` (non-blank lines; function sizes through Python's `ast`) | read-only, on the clone | — |
| G-8 | `show_fetch.py`, `show_cmd.py` and `show_text.py` over this session's own transcript: each web citation and each command in this table checked against what the tool returned at the time | read-only | — |

### Limits

1. **Settings files not read.** Three calls were refused, all of one kind: each named a settings file. The refusal text was "refused to every role (DEC-508, DEC-525)". The three calls were:
   - a Bash read naming `.claude/settings.json` and the kernel's `settings.json`;
   - a `git grep` over `governance` and `template/governance/kernel`;
   - a Python read of `~/.claude.json` with a listing of `~/.claude/`.

   I stopped that form and searched narrower folders. As a result, I did not test what lefthook does to the settings file (F7). I also did not check whether the project settings hold a sandbox block. F3 relies instead on the launcher's code, DEC-161 ("the sandbox applies to launched worker sessions only") and ADR-0002 (the repository's "settings carry no sandbox block").
2. **A Bash write was refused** to a path set by a variable inside the same command (DEC-115). From then on I wrote files with the Write tool.
3. **A read-only measuring script, passed as a quoted heredoc, was refused** as "the command cannot be read" (DEC-409). This is the case of F5. I ran the same script from a file.
4. **No heavy runs:** no `gov rebuild`, no test regression and no `gov close`. The close's duration comes from its record.
5. **Code-graph timings are from the tool's CLI mode only:** about 4 s per call, most of it start-up. I did not time the wrapper's session mode.
6. **pytest-testmon and coverage are not installed,** and I installed nothing. testmon's fit comes from its documentation, not from a run.
7. **CI was not run:** no push, and the network was used for documentation only.
8. **Hand resumes not traced:** for F3 I did not check whether any of the six hand resumes was of a sandboxed worker (counts only).
9. **Other sessions wrote concurrently.** The containment hook reported files I did not write:
   - `docs/assessment/2026-10/F-models-context.md`;
   - `governance/project/briefs/LEAD-w2-common.md`;
   - `governance/project/orchestration/README.md`;
   - `governance/project/prompts/w2-orchestrator.md`.
10. **The machine is shared.** I examined the tools named in this repository's registry or in S0b2's, and what the checks of G-2 show. Other programs' tools and caches were not examined.
11. **Contract v4.2 was not read.** The lens's questions are about tools, so the report rests on ADR-0002, the register and the WBS instead.

### Web sources (all read 2026-10-19)

Official sources and the tools' own documentation only.

| ID | URL | Used for |
|---|---|---|
| W1 | https://www.sqlite.org/fts5.html | `bm25()` with column weights (§5.1.1); the `rank` column and `ORDER BY rank` (§5.2); the trigram tokenizer (§4.3.4) |
| W2 | https://github.com/tarpas/pytest-testmon and https://pypi.org/project/pytest-testmon/ | version 2.2.0 of 1 Dec 2025, MIT, Python 3.10 or later |
| W3 | https://www.testmon.org/ | tracks Python code, installed packages and the Python version; does not track data files or external services; `--testmon-env`, `--testmon-forceselect`, `--testmon-noselect`, `--testmon-nocollect`; data in `.testmondata` |
| W4 | https://testmon.org/blog/determining-affected-tests/ | selection from coverage.py block checksums |
| W5 | https://www.testmon.org/blog/v14-with-xdist-support-is-out/ | works with pytest-xdist since 1.4.0 |
| W6 | https://github.com/DeusData/codebase-memory-mcp (read in two parts) | `trace_path` (depth 1–15, inbound or outbound, tests left out by default); `search_graph` (structural, BM25 or semantic, with degree filters); `query_graph` (an openCypher subset with SKIP and LIMIT); `detect_changes`; `CBM_CACHE_DIR`; release 0.11.0 |
| W7 | https://code.claude.com/docs/en/checkpointing | covers edits made through its file tools only; not Bash, not other sessions; "not a replacement for version control" |
| W8 | https://code.claude.com/docs/en/sandboxing | sandbox covers Bash, PowerShell and Monitor; file tools, hooks and MCP servers run outside; built on `@anthropic-ai/sandbox-runtime`; `failIfUnavailable`, `allowUnsandboxedCommands`, `excludedCommands` |
| W9 | https://code.claude.com/docs/en/hooks | hook events (PreCompact, PostCompact; SessionStart matchers `resume` and `compact`); `additionalContext` up to 10,000 characters; permission rules match each subcommand, `$()` and backticks |
| W10 | https://code.claude.com/docs/en/settings-reference | index only; the glob detail was not reached |
| W11 | https://github.com/anthropics/sandbox-runtime | `srt`, a "beta research preview", 0.0.x, Apache-2.0. On Linux, `allowWrite` and `denyWrite` take literal paths (a trailing `/**` is dropped; other globs are skipped), and a read rule whose first path part holds a wildcard is skipped: "A skipped pattern hides nothing" |
| W12 | https://github.com/idank/bashlex and https://pypi.org/project/bashlex/ | 0.18 of 18 Jan 2023; GPL-3.0 or later; no arithmetic or complex parameter expansion |
| W13 | https://github.com/tree-sitter/tree-sitter-bash and https://pypi.org/project/tree-sitter-bash/ | MIT; 0.25.1 of 2 Dec 2025; prebuilt wheels; Python 3.10 or later |
| W14 | https://github.com/wedow/ticket and https://github.com/wedow/ticket/releases | MIT; plugins as `tk-<cmd>` programs on PATH; six releases, 2 Jan to 3 Feb (GitHub shows no year for dates in the current year, 2026), none since |
| W15 | https://github.com/steveyegge/beads and https://github.com/steveyegge/beads/releases | MIT; a Dolt database; an atomic `bd update --claim`; v1.3.1 of 30 Sep 2026 |
| W16 | https://copier.readthedocs.io/en/stable/updating/ | update needs a valid `.copier-answers.yml`, a template versioned with git tags, and a clean destination repository; conflicts inline (default) or as `.rej` files; "Never update `.copier-answers.yml` manually" |
| W17 | https://github.com/Fission-AI/OpenSpec | "Requires Node.js 20.19.0 or higher" |
| W18 | https://github.com/actions/setup-python | pin the Python version; `cache: pip` |
| W19 | https://pip.pypa.io/en/stable/topics/secure-installs/ | `--require-hashes`; every requirement pinned with `==` |
| W20 | https://docs.astral.sh/uv/concepts/tools/ and https://docs.astral.sh/uv/guides/tools/ | each tool is installed in its own isolated environment; a version is pinned at install (`uv tool install <package>==<version>`); `uv tool upgrade`; the pages do not say whether two versions of one tool can coexist |
| W21 | https://lefthook.dev/configuration/ai/ and https://lefthook.dev/usage/commands/install/ | the `claude` provider generates hooks in `.claude/settings.json`; on install, lefthook-managed entries are replaced; no way to switch it off is described |
| W22 | https://github.com/evilmartians/lefthook/blob/master/CHANGELOG.md | 2.1.10 (2026-07-08): "feat: AI coding agents integration (#1448)"; 2.2.0: "fix: don't write an install-time lefthook path into AI hook configs (#1544)"; newest at reading 2.2.2 |
| W23 | https://docs.ollama.com/api/embed | embed with `dimensions` and `truncate`; no rerank endpoint in the API |
| W24 | https://github.com/ollama/ollama/pull/7219 (seen through a web search result; the page itself not opened) | a rerank endpoint proposed, not merged |
| W25 | https://code.claude.com/docs/en/memory | `CLAUDE.md` with imports; `.claude/rules/` files scoped by `paths:`; auto memory loads its first 200 lines or 25 KB |
| W26 | https://code.claude.com/docs/en/sessions | resume restores the conversation, the model, the agent and (from a terminal) the permission mode, but "If the session depended on `--mcp-config`, `--settings`, … pass them again when you resume". Transcripts are kept 30 days by default; their format "is internal to Claude Code and changes between versions" |
| W27 | https://github.com/asg017/sqlite-vec | pre-v1; brute-force search, with approximate indexes (IVF, DiskANN) in its code; Apache-2.0 or MIT |

## 2. Answers

### Q1 and Q2. Inventory, and status measured

**Status words.**

| Status | Meaning |
|---|---|
| ACTIVE | called in ordinary work, with the caller named |
| PASSIVE | installed and wired in, but not doing its job |
| BROKEN | fails when called (the error is quoted) |
| REPLACED | our code does its job instead (the code is named) |

**Columns.**
- **Pinned and hash-verified:** what doctor found in run G-1, meaning the version it read and whether the file it hashed matches the registry.
- **Agent runs:** Bash commands in the Gov OS transcripts that start the tool (G-6).

**Table A. The 23 registry entries.**

| # | Tool | Version | Installed | Pinned and hash-verified (G-1) | Wired in where | Status | Evidence | Recommendation |
|---|---|---|---|---|---|---|---|---|
| 1 | node | v22.23.3 | `~/.nvm/versions/node/v22.23.3/bin`; not on the default PATH, where `node` is v18.20.8 | version and hash match | runtime of openspec and ccusage | ACTIVE, as a runtime | doctor; registry lines 17–18 | Configure: start Node tools under v22 (F4, F10) |
| 2 | uv | 0.12.21 | `~/.local/bin/uv` | version and hash match | installs copier, check-jsonschema and the reranker venv; `gov` never calls it | ACTIVE at install time only | registry install lines; 21 Bash commands name it | Keep; a candidate installer for W2-18 (Q4) |
| 3 | rulesync | 24.0.0 | `~/.local/bin/rulesync` | version and hash match | adapter generation and its exact comparison (`adapters/portability.py`); adoption's import and generate (`adopt/legacy.py:27–28`) | ACTIVE | 38 agent runs of `rulesync generate`; the adapter-portability check | Keep |
| 4 | openspec | 1.13.2 | npm package under Node v22 | entry-script hash matches; no version read | the `openspec-validate` check (`check/runner.py:176–193`); 6 skills and 6 commands in every session; `gov` reads its folder layout (`readiness/checker.py`, `tasks/bridge.py`, `check/claims.py`) | PASSIVE here. BROKEN when started with the default PATH, whose `node` is v18.20.8: "SyntaxError: Invalid regular expression flags" | no `openspec/` folder in this repository; 37 agent runs, all trials; 0 skill uses | Retire here; keep the file format in the template (F10) |
| 5 | codebase-memory-mcp | 0.11.0 | `~/.local/bin/` | version and hash match | `src/gov/codeintel/` (the tool's CLI, a home folder per repository). Users: `gov closure`, `gov retrieve --id`, adoption's importer check (`adopt/stages.py:192–207`), W2-37's `gov impact` | BROKEN at this repository's size, through our wrapper: "result exceeded 100k rows — use narrower filters or add LIMIT" | run G-3; the tool's own narrower queries answer | Configure: use its own traversal (F1) |
| 6 | copier | 9.18.2 | uv tool | version and hash match (the hash is of uv's launcher script, not of the package) | adoption by `copier copy` (documented); `copier update` planned in W2-17 | ACTIVE, thinly | 5 `copier copy` and 3 `copier update` agent runs; W1-39's tests | Keep; W2-17 glues it (Q4) |
| 7 | lefthook | 2.1.15 | `~/.local/bin/` | version and hash match | `lefthook.yml`: pre-commit `gov ci checks G1 G2` and `gov ci staged-secrets`; pre-push `gov ci push` | PASSIVE: the git hooks were removed (DEC-712); `.git/hooks` holds samples only (lens D F6) | 2.1.15's uninstall rewrites `.claude/settings.json` (DEC-783's basis); since 2.1.10 an install can write AI-agent hooks there (W21, W22) | Configure before W2-08 (F7) |
| 8 | check-jsonschema | 0.38.2 | uv tool | version and hash match (launcher script) | nowhere: `src/gov` names it only in doctor's tool list | REPLACED by `src/gov/check/schema.py` (169 lines), which checks a subset | planted ticket: 7 schema errors, 0 found by `gov` (F2) | Use it, or the library, instead of the subset (F2) |
| 9 | ollama | 0.35.0 | `~/.local/ollama/bin` | version and hash match | embeddings for `gov rebuild` and `gov retrieve` (127.0.0.1:11434; a CPU host for queries on :11435) | ACTIVE | lens B's runs | Keep; it has no rerank endpoint (Q4) |
| 10 | ticket (`tk`) | v0.3.2 | `~/.local/bin/tk`; vendored copy `template/governance/kernel/bin/tk`, same sha256 | hash matches; no version read | hooks: SessionStart `tk ready` (`sessionstart.py:133`), PreCompact `tk ls --status=in_progress` (`precompact.py:86`); `gov close` repair tickets (`close/tool.py`); the task bridge's `tk create` (`tasks/tickets.py`) | ACTIVE | 284 agent runs (start 78, close 78, ready 30, create 18) | Keep, vendored (Q3) |
| 11 | gitleaks | 8.30.1 | `~/.local/bin/` | version and hash match; CI checks the archive's sha256 | `gov ci staged-secrets` (`ci/command.py:99`); the CI job; the indexer's secrets filter, one `gitleaks stdin` per file (`secrets/__init__.py:77`) | ACTIVE | 71 agent runs; `ci.yml` | Keep |
| 12 | pyyaml | 6.0.1 | apt package `python3-yaml` | version matches; the hash (of the `.deb`) cannot match an installed file | everywhere in `gov` | ACTIVE | doctor `sha256_match: false` | Keep; pin it in the package metadata (F4) |
| 13 | ccusage | 20.0.26 | npm package under Node v22 | version matches; the hash (of the npm tarball) cannot match | `gov telemetry` (`telemetry/counter.py:176–194`) | ACTIVE | 11 share records of 2026-10-13 carry measured tokens and cost; in each, the governance share is "not measured", because the ticket had no close record yet (lens F F5) | Keep; re-test at each Claude Code pin change (Q4) |
| 14 | superpowers | v6.4.2 (3 skills) | vendored under `template/governance/kernel/vendor/superpowers/`, copied into the kernel's skills, generated into every session | folder digest matches | every session's skill list | PASSIVE | read 21 times, called 0 times through the Skill tool (F11) | Retire, or name it in a role file (F11) |
| 15 | claude code | 2.1.292 | `~/.local/bin/claude` | version and hash match; the IDE extension is 2.1.301 (doctor: "drift") | the agent program; every hook; `gov launch` | ACTIVE | doctor | Keep; W2-22's drift policy |
| 16 | bubblewrap | 0.9.0 | apt | version matches; the hash (`.deb`) cannot match | Claude Code's sandbox in launched workers | ACTIVE, launched workers only | DEC-789, DEC-799 | Keep |
| 17 | qwen3-embedding | 0.6b | Ollama model | model blob hash matches | embeddings | ACTIVE | — | Keep |
| 18 | sqlite-vec | 0.1.9 | pip user install | `vec0.so` hash matches | the semantic index | ACTIVE | ADR-0002 §2 names it a core need; `pyproject.toml` does not declare it | Keep; declare and pin it (F4) |
| 19 | reranker-venv | sentence-transformers 6.1.0, torch 2.14.1+cu130, transformers 5.18.0, huggingface-hub 1.33.0 | `~/.local/share/gov-os/reranker-venv` (5.6 GB) | hash of its `uv pip freeze` output matches | the reranker process of `gov retrieve` | ACTIVE; no benefit shown | lens B F9 | Decide on W2-15a's figures; retire if there is no gain |
| 20 | reranker | Qwen3-Reranker-0.6B at `e61197ed` | Hugging Face cache (1.2 GB) | model file hash matches | as row 19 | as row 19 | as row 19 | as row 19 |
| 21 | socat | 1.8.0.0 | apt | version matches; the hash (`.deb`) cannot match | the sandbox's network proxy | ACTIVE, launched workers only | — | Keep |
| 22 | pytest-xdist | 3.8.0 | pip user install | no version read; the hash (of the wheel) cannot match: `ok: false` | `gov close`'s parallel run with `-n` (`close/command.py:764–894`) | ACTIVE | W2-53's re-close record | Keep; W2-22 reads its version (W2-M287) |
| 23 | gov | 0.1.0 | editable install: `~/.local/bin/gov` runs this working tree | the launcher script's hash matches; the code that runs is not hashed | everything | ACTIVE | ADR-0002 §2 says "installed as a user tool pinned to the release tag"; it is not (lens D F1, F7) | W2-16, W2-17, W2-18 |

**Table B. Used, but not in the registry.**

| Tool | Version | Where | Used by | Recommendation |
|---|---|---|---|---|
| pytest | 9.0.3 | user site of `/usr/bin/python3` | every close and test run; 5,088 Bash commands name it | Register (F4) |
| execnet | 2.1.2 | same | pytest-xdist's dependency, named only in xdist's registry note | Register (F4) |
| Python | 3.12.3 | `/usr/bin/python3` | runtime of `gov` | Register as a platform entry (F4) |
| SQLite with FTS5 (its full-text search) | 3.45.1, through Python's `sqlite3` | system | the lexical index | Register as a platform entry; use FTS5's ranking (F8) |
| git | system | system | everything | Platform entry |
| jsonschema (Python library) | 4.10.3 | system Python | not used by `gov`; used by my probe G-4 | Candidate for F2 |
| coverage, pytest-testmon | — | not installed | — | A DEC-083 install package if W2-48 picks testmon (F6) |

**Table C. On the machine, not in the registry, not used.**

| Tools | Where | What is known | Recommendation |
|---|---|---|---|
| pyright 1.1.414, TypeScript 7.0.2 (`tsc`), typescript-language-server 6.0.1 | the Node v22.23.3 globals | S0b2 installed them and recorded them, with uninstall commands, in its own registry, which gives pyright's and the language server's purpose as "for the C2 LSP comparison". The language servers were rejected (ADR-0002 §2), and DEC-074's S0b2 facts say "rejected tools uninstalled" | Remove, or register with a purpose (F4) |
| rustup 1.29.1, toolchain 1.98.1 with rust-analyzer (about 1.5 GB) | `~/.cargo/bin`, `~/.rustup` | installed by S0b2 and recorded in its registry, with an uninstall command; no purpose is stated. W2-19 queues "a Rust toolchain for the fixture" as an install (Q-6) | Settle Q-6 knowing this toolchain is here: register it or remove it (F4) |

**Table D. Rejected or deferred in Wave 1** (ADR-0002 §2, DEC-074).
- **Rejected:** qmd, Backlog.md, adrkit, beads_rust and the language servers (LSP).
- **Deferred:** Docling, MarkItDown, RAGFlow (conditional), the OpenTelemetry stack and gpt-oss:20b.
- S0b2's registry also lists backlog.md, adrkit (with `@adrkit/mcp`) and qmd as installed for the trial. None of them is in the Node v22 or v18 globals now, and qmd's stray cache (`~/.cache/qmd`) is gone. The language servers, TypeScript and the Rust toolchain remain (Table C). I did not look inside the workbench, where S0b2 kept qmd's models and its own retrieval venv.

**Models and skill packs.**
- The two retrieval models are rows 17 and 20. The Claude models that agents run on are lens F's subject.
- The skill packs are Superpowers (row 14) and OpenSpec's generated skills and commands (row 4). The kernel's own method skills are ours, not selected tools.

**Status, in sum (Q2):**
- **ACTIVE: 18.** With qualifiers:
  - uv is used at install time only;
  - copier is used thinly;
  - the reranker has no shown benefit;
  - bubblewrap and socat serve launched workers only.
- **PASSIVE: 3.** openspec, lefthook and superpowers.
- **BROKEN: 1.** codebase-memory-mcp, through our wrapper (F1). openspec is also BROKEN on the default PATH (F10).
- **REPLACED: 1.** check-jsonschema, replaced by our subset (F2).
- **MCP:** no agent called any of these tools as an MCP server (a tool server Claude Code connects to). The code-graph tool is reached only through `gov`.

### Q3. Reinvention: what we built that a tool already does

| Area | What we built (lines) | What a tool offers | Verdict |
|---|---|---|---|
| The guard's shell parsing | 512 lines in nine functions; five separate tokenisations; nine open list rows | No tool reads shell for us. tree-sitter-bash parses it (W13); the sandbox bounds writes without parsing (EXP-001) | Stop growing it: one shared tokeniser, and the sandbox first (F5) |
| Test-result caching | not built yet (W2-48, estimated at 220 lines); today every close runs the full suite, about 59 minutes | pytest-testmon (W2–W5) | Glue it, after restating W2-48's measure (F6) |
| Ranked lexical search | a 32-line search that uses FTS5 as a filter, then Python's `in` | FTS5's own `bm25()`, `rank` and trigram tokenizer (W1) | Glue: W2-13 as planned (F8) |
| The code graph's row cap | about 60 lines that pull the whole graph into Python and traverse it, plus `closure/` (90) | the tool's `trace_path`, `search_graph` and per-kind `query_graph` (W6) | Glue (F1) |
| Checkpoints | `gov checkpoint` (214 lines) and two hooks | Claude Code's checkpointing covers file edits within one session only (W7) | A justified build: keep |
| The ticket tool | claims (70 lines) and the READY rule (84 lines) around `tk` | `tk` has no claim; beads has one, on a Dolt database (W15) | Keep |
| Schema validation | a 169-line subset validator | check-jsonschema, pinned and never called | Replace the subset (F2) |
| Commit trailers | two regexes left (`decisions/checker.py:60`, `store/loader.py:49`) | git's `%(trailers)` format, already used elsewhere in `gov` | Fold in when those files are next touched |

**The guard's shell parsing.**
- **What we built:**
  - **Size:** the guard reads Bash commands with Python's `shlex`, which splits words but is not a shell parser. Its shell-reading functions total 512 lines:
    - in `decide.py`: `_extract_bash_write_targets` 244, `_expand_token` 59, `_cp_operands` 31, `_option_after_operand` 9, `_lift_in` 17;
    - in `protected.py`: `_command_reads` 126, `_tokenised` 7;
    - in `heldout.py`: `_words` 9;
    - in `install.py`: `_segments` 10.
  - **Tokenisations:** five separate ones, each with its own settings (`decide.py:345`, `decide.py:732`, `install.py:58`, `heldout.py:86`, `protected.py:280`), and a sixth in `telemetry/sessionlog.py:102`.
  - **Open list rows:** nine concern parser holes: W2-H060, W2-M019, W2-M026, W2-M027, W2-M035, W2-M068, W2-L148, W2-L152 and W2-L299.
  - **Refusals:** it refused 116 commands as unreadable in October, most of them heredocs (F5).
- **The paths and their cost:**
  - **(a) Keep growing the hand reader.** Each new hole becomes a list row, and a round wherever an honest agent can hit it. The cost has no end.
  - **(b) One shared tokeniser for the five readers, aware of heredocs.** No new dependency. It removes F5's refusals. W2-42 already owns `src/gov/guard/**`.
  - **(c) tree-sitter-bash (W13).** A real grammar, MIT, with wheels; it knows heredocs, substitutions and here-strings. Its costs:
    - a new core dependency: ADR-0002 §2 allows only the standard library, PyYAML and sqlite-vec, so it needs an ADR change and a DEC-083 install;
    - a rewrite of the readers onto one syntax tree;
    - a check against the guard's 100 ms p95 budget (DEC-149).

    It still cannot know a variable's value or what `$(…)` prints, so the "unknown, so refuse" rules stay.
  - **(d) bashlex (W12).** GPL-3.0 or later, last released January 2023, and it has no arithmetic. Not suitable.
  - **(e) The sandbox first.** It bounds the Bash writes of launched workers at the operating-system level without parsing (EXP-001; ADR-0002: "closed for Bash at the OS level, without parsing the command"). Ticket leads and the orchestrator still run outside it (lens E F1). W2-21 is to sandbox the leads (DEC-769); the orchestrator's session stays outside.
  - **Claude Code's own permission matcher** splits compound commands (W9), but hooks receive only the raw command, so the guard cannot use it.
- **Recommendation:** (b) and (e). Try (c) only after a spike (R5).

**Test-result caching.**
- **Today:** every clean close runs the whole regression. That took about 59 minutes in W2-53's last re-close (`close-DAEO-7rr2-3.json`). DEC-726 counts about an hour per close and about 50 hours of main-tree time over the wave.
  - `close/command.py` turns pytest's own cache off (`-p no:cacheprovider`) and runs xdist's `-n`, then the serial-only cases.
  - Its two pytest plugins (38 and 55 lines) are small, justified glue.
- **The tool:** pytest-testmon re-runs only the tests that a change can affect (W2–W5).
  - It works from coverage.py block checksums and also tracks installed packages and the Python version.
  - It works with xdist.
  - It does not track data files or external services.
- **The cost of each path:**
  - **testmon:** an install package for testmon and coverage, plus glue for three things:
    - a hash of the declared data-file globs, passed as `--testmon-env`;
    - "reused" labels in the close record;
    - writes from main-tree closes only.
  - **A built cache (W2-48 as written):** our own tracing of each test's imports, fixture chain and data reads, its storage and invalidation, and their tests. The estimate is 220 lines; Wave 1's estimates ran about three times low (lens A F6).
- **Recommendation:** see F6 and R6.

**Ranked lexical search.**
- **What we built:** `retrieval/lexical.py:180–212` queries the FTS5 table with the whole question as one quoted phrase, sorts by path and line, and filters each line with Python's `in`.
- **What FTS5 offers:** ranking with `bm25()`, per-column weights, `ORDER BY rank`, and a trigram tokenizer for exact substrings (W1).
- **Cost:** W2-13 (DEC-725, 300 estimated lines) is planned, and the glue is small (F8).

**The code graph's row cap.**
- **What we built:** `_graph` pulls every node and edge into Python and keeps them for the process. `definitions`, `references`, `callers`, `callees`, `impact` and `dead_code` then traverse in Python.
- **What the tool does itself (W6):**
  - callers and callees to depth 15 (`trace_path`);
  - search with degree filters, where `max_degree=0` gives dead-code candidates (`search_graph`);
  - the impact of a git diff (`detect_changes`).
- **Measured (F1):** the whole-graph pull fails on this repository. The tool's narrower forms answer.
- **Cost:** replacing the pull removes code; it adds none.

**Checkpoints.**
- **Claude Code's checkpointing (W7)** restores file edits made through its file tools within one session. It does not cover Bash or other sessions, and it says it is "not a replacement for version control".
- **Our checkpoints** are records in git that carry a ticket's state from one session and role to the next. Claude Code's resume and compaction events are already glued through hooks (W9).
- **Verdict:** keep. Lens E F11 and lens B F5 cover defects in the automatic checkpoints.
- **Resume risk:** a resume by hand drops the worker's sandbox (F3).

**The ticket tool.**
- **Upstream:**
  - `tk` is a single bash script: six releases from 2 January to 3 February 2026, none since (W14). ADR-0002 calls it "unmaintained upstream; it is vendored by hash", and the vendored copy's hash equals the registry's.
  - Its plugin mechanism (`tk-<cmd>` programs on PATH) could hold our additions without a fork. Moving our 70-line claim there saves nothing.
- **beads (W15)** has an atomic claim but stores issues in a Dolt database. Moving to it would mean migrating `.tickets/` and about twenty `gov` modules that read ticket front matter, to save 154 lines.
- **Verdict:** keep; re-check upstream at each wave.

**Schema validation.**
- `check/schema.py` checks required fields for every record type but checks values only for two types. check-jsonschema was chosen for this job and is never called (F2).

### Q4. Gaps: mature tools to glue instead of build

| Need | What the Gov OS does now | Mature tool to glue | Maturity, from its own documentation | Research needed first |
|---|---|---|---|---|
| Memory: the rules and facts a session carries | `CLAUDE.md`, the register, the context packet, retrieval. A launched session loads none of its role's rules (lens E F2) | Claude Code's memory: `CLAUDE.md` with imports, `.claude/rules/` files scoped by `paths:`, auto memory (W25) | Part of Claude Code; maintained by its vendor; versioned with the CLI pin | Whether a `paths:`-scoped rule loads in a headless worker started by `gov launch`; its token cost; whether a worker can change it |
| Retrieval | FTS5, sqlite-vec, Ollama embeddings and a reranker venv, fused by rank (RRF) | Already glued. What is missing lies inside the tools: FTS5's `bm25()` (W1). Ollama has no rerank endpoint (W23); a proposal is open (W24) | FTS5: part of SQLite, mature. sqlite-vec: pre-v1, brute-force, approximate indexes in progress (W27). Ollama: active | W2-15a's five modes as planned. Keep a reranker only if it shows a gain. DEC-016's move to LanceDB above ~100k vectors stays the trigger |
| Code questions | the wrapper's own traversal (F1) | the tool's `trace_path`, `search_graph` and `detect_changes` (W6) | 0.11.0: young and changing. ADR-0002 already lists "breaking changes at a pin upgrade" as a revisit trigger | `trace_path` latency in session mode; whether `detect_changes` gives W2-37's radius |
| Context packets | `gov context` builds a packet; lens B F1 measured it 42–168 times over its ceiling | No tool builds packets. Delivery is the SessionStart hook's `additionalContext`, up to 10,000 characters (W9) | Part of Claude Code | Whether a packet can fit 10,000 characters, or must be a file that the session reads |
| Resume | `gov checkpoint`; the SessionStart and PreCompact hooks; `gov launch --resume` | Claude Code's `--resume`, `--continue` and `--fork-session`; SessionStart matchers `resume` and `compact` (W9, W26) | Part of Claude Code. Transcripts are kept 30 days by default; their format "is internal to Claude Code and changes between versions" (W26) | F3's resume path; re-test ccusage and `telemetry/sessionlog.py` at each Claude Code pin change |
| Sandbox | Claude Code's sandbox (bubblewrap and socat) for launched workers only | The same, and the standalone `srt` from `@anthropic-ai/sandbox-runtime`, which wraps any command (W11) | Claude Code's sandbox covers Bash, PowerShell and Monitor; file tools, hooks and MCP servers run outside (W8). `srt` is a "beta research preview", 0.0.x (W11) | W2-40's cases, plus the runtime's Linux path rules (W11): write rules take literal paths (a trailing `/**` is dropped; other globs are skipped), and of a skipped read pattern it says "A skipped pattern hides nothing". DEC-799's basis already found that the launcher's `.gov-runtime/` deny rules "are patterns, which the Linux sandbox skips". Whether `srt` can wrap the close's test runs and the orchestrator's Bash |
| CI | one job; installs `gov` with `python3 -m pip install .`; gitleaks from a hash-checked archive; tests "unmeasured" without pytest (lens D F6) | `actions/setup-python` (W18) and pip's hash-checking mode (W19) | Both mature and maintained | A hash-locked requirements file for pytest, pytest-xdist, execnet, PyYAML and sqlite-vec; the owner's approval of tools on the runner (Q-8) |
| Releases | W2-16 `gov release`, W2-17 `gov update` with `copier update`, W2-18 `gov install`, all to build | Copier's update for the kernel (W16); a wheel installed with hashes for the CLI (W19); uv tools (W20) | Copier is mature; its update needs git tags, a clean tree and an untouched answers file (W16). A uv tool is one environment per tool in the user's tools folder (W20) | W2-18 wants two releases side by side on one machine. The uv pages do not say this works, so a per-repository environment may be needed |

### Q5. Keep, configure, replace or retire, and the glue that saves the most build

Each line names the finding it rests on, where there is one.

- **Keep:**
  - uv, rulesync, copier, ollama, qwen3-embedding, sqlite-vec, `tk` (vendored), gitleaks, ccusage, Claude Code, bubblewrap, socat and pytest-xdist;
  - the checkpoints and the ticket claims we built.
- **Configure properly:**
  - node: start Node tools under v22 (F4, F10);
  - codebase-memory-mcp: use its own traversal (F1);
  - lefthook: settle its rewrite of the settings file (F7);
  - pyyaml and sqlite-vec: declare and pin them (F4);
  - pytest-xdist: doctor should read its version (F4);
  - `gov` itself: a pinned release (W2-16, W2-17, W2-18).
- **Replace our code with the tool's:**
  - the schema subset, with check-jsonschema or the jsonschema library (F2);
  - the lexical filter, with FTS5's ranking (F8);
  - W2-48's planned built cache, with pytest-testmon, if its comparison holds (F6).
- **Retire:**
  - openspec in this repository; the file format stays in the template (F10);
  - Superpowers, unless a role file names it (F11);
  - the reranker venv and model, if W2-15a shows no gain (lens B F9);
  - S0b2's language-server leftovers, unless they are registered for a purpose (F4).
- **Rust toolchain:** settle Q-6 knowing that S0b2's toolchain is already installed: register it or remove it (F4).
- **The glue that most reduces the remaining build** is ranked at the end of section 4. In short:
  1. pytest-testmon for W2-48;
  2. the code-graph tool's own traversal;
  3. a full schema validator;
  4. the sandbox in place of a growing parser.

## 3. Findings

**How to read them.**
- The threat model is ADR-0001's: honest mistakes, accidents and drift, not a deliberate attacker.
- Each finding answers two questions: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?" (DEC-808).
- Severity:
  - **high:** it blocks a planned capability or gate in ordinary work;
  - **medium:** it costs time or weakens a check in ordinary work;
  - **low:** a small cost.

### F1. The code-graph wrapper pulls the whole graph and fails on this repository; the tool's own traversal answers

**Evidence.**
- **Run G-3:** codebase-memory-mcp 0.11.0, over a copy of the main tree's index.
  - The whole-graph node query answers: 28,442 rows in 2 pages, 8.48 s.
  - The whole-graph edge query, as `_graph` asks it, is refused: "result exceeded 100k rows — use narrower filters or add LIMIT" (4.98 s). The graph has 21 edge kinds and 117,364 edges. The 15 kinds `_graph` keeps total 77,596.
  - Each kept kind asked alone answers:
    - USAGE: 30,531 rows in 2 pages, 9.04 s;
    - CALLS: 25,214 rows, 4.53 s;
    - each of the other 13: about 4.3 s.

    All 15 take about 69 s in CLI mode.
  - `trace_path` by qualified name (inbound and outbound, depth 3) answers in about 4.0 s. By a short name it answers "ambiguous", with suggestions.
  - Paging inside the query text fails silently: `SKIP 0 LIMIT 50000` returns 50,000 rows, but `SKIP 100000 LIMIT 50000` returns 0 rows and no error.
- **What we built:** `_graph` (`codeintel/__init__.py`) fetches every node and edge into Python and caches them per process. The six traversal functions run on that copy.
- **Who calls it:**
  - `closure/__init__.py:31–35`;
  - `gov retrieve --id`;
  - adoption's `_importers` (`adopt/stages.py:192–207`), which refuses a path map with a move ("CODE_GRAPH_UNREADABLE … no path map with a move is recorded");
  - W2-37's `gov impact`, at depths of 1, 3 and 8 hops (DEC-815).
- **What the tool offers (W6):** `trace_path` (depth 1–15), `search_graph` with degree filters, `query_graph` with LIMIT, and `detect_changes`.
- **Not a scale problem:** this graph is well inside ADR-0002's tested envelope (about 80k nodes and 270k edges). The limit is the query interface's result cap, so the ADR's revisit trigger ("a code graph above the tested envelope") does not catch it.
- **Lens B F3** found the failure and counted the kinds, but did not run the narrower queries. This run confirms that they work, and adds the silent truncation and the adoption step.
- **No owner:** W2-37's allowed paths leave out `src/gov/codeintel/**`, and W2-56 may change only the daemon's folder in that file.

Ordinary work: yes, because every `gov closure` and `gov retrieve --id` on this repository hits it. So will every `gov impact`, and every adoption with a move in a repository that has more than 100,000 edges.
Consequence: other. The facet is reported unavailable, so nothing passes wrongly today. But a fix that pages with SKIP inside the query would fail open: everything past the 100,000th row would vanish without an error.
**Severity: high.** It blocks `gov impact` (W2-37) and W2-38's impact-selected tests, and adoption of a large repository.

### F2. The schema check passes records that the kernel's own schemas refuse; the selected validator is installed and never called

**Evidence.**
- **What the check does:** `src/gov/check/schema.py` has 169 lines.
  - `_validate` checks only required fields, plus the front matter's `allOf` required list.
  - `_validate_shapes` checks values (`const`, `enum`, `type`, `minLength`, `pattern`), but only for `STANDALONE_TYPES = ("probe", "audit-report")`.
- **Run G-4, the probe:** a planted ticket with six faults:
  - status `banana`;
  - state_class `NOT-A-CLASS`;
  - profile `HUGE`;
  - est_loc −5;
  - deps `["not an id"]`;
  - empty `allowed_paths` and `kpis`.

  `gov`'s core-schema check (the clone's code) finds 0 faults. The jsonschema library, with the kernel's `ticket.schema.json` and `common.schema.json`, finds 7 errors.
- **Run G-4, the sweep:** jsonschema refuses 4 of the 558 records the check reads. All four are decision records in `docs/imported/` whose ids (for example `OWNER-AMENDMENT-P2-0010`) do not match `^(ADR|DEC)-[0-9]{3,}$`. Core-schema refuses none.
- **The selected validator:**
  - check-jsonschema 0.38.2 is in the registry (DEC-074), and doctor checks its pin.
  - No `gov` code calls it.
  - Agents ran it by hand 10 times.
- **No owner:** W2-02 may change `src/gov/check/schema.py` for "the type map only".

Ordinary work: yes, because an honest slip in a ticket's status or class, such as a misspelt value, passes the check. Four real records already fail their schema unnoticed.
Consequence: fails open. The check reports green on records that its own schemas refuse.
**Severity: medium.** A ticket with a wrong status can drop out of the queue without a word.

### F3. A worker resumed by hand runs without its sandbox

**Evidence.**
- **How the sandbox is given:** `gov launch` gives a worker its sandbox only through the `--settings` argument (`launch/launcher.py:313`; the block at 150–170 and 309). It refuses a caller's own `--settings` (245–246).
- **What resume restores:** Claude Code's sessions page (W26) says: "Not every configuration flag from the original launch is restored. If the session depended on `--mcp-config`, `--settings`, … pass them again when you resume". The standard settings files are read again, so the guard's hooks still run.
- **The consequence:**
  - `claude --resume <worker session>` brings back the worker's conversation without its sandbox.
  - `gov launch … --resume` passes `--settings` again, so it keeps the sandbox.
- **In the transcripts (G-6):**
  - 6 Bash calls start `claude … --resume`;
  - 3 pass `--resume` through `gov launch`.

  I did not check which sessions they resumed.
- **What relies on the sandbox:** DEC-789 and DEC-799 make the sandbox the boundary for launched workers (item 3 of DEC-799: "every worker whose suites do not need the code graph … starts through `gov launch`, sandboxed").

Ordinary work: yes, because resuming a stopped session is the documented, ordinary way to continue it, and both forms appear in the transcripts.
Consequence: fails open. A worker resumed by hand runs its Bash under the guard alone, without the operating-system boundary.
**Severity: medium.** The guard still runs. I did not check whether any of the six hand resumes was of a sandboxed worker (Limits, item 8).

### F4. "Pinned and hash-verified" means different things per tool, and the `gov` package pins nothing

**Evidence.**
- **Doctor's rule** (`doctor/command.py:480–491`):
  - when it reads a version, "ok" means the version string is equal, and the hash is not required;
  - when it reads none, "ok" means the hash matches.
- **Five entries record the hash of a download, which no installed file can match:** pyyaml, bubblewrap and socat (`.deb` packages), ccusage (an npm tarball) and pytest-xdist (a wheel). All five show `sha256_match: false`.
  - Four of them pass on the version string alone.
  - pytest-xdist fails, because doctor cannot read its version (W2-M287, W2-22).
- **Four entries hash a launcher, not the code that runs:**
  - copier and check-jsonschema: uv's entry script;
  - openspec: its entry script, and doctor passes it although it cannot start (F10);
  - `gov`: the script of an editable install (lens D F7).
- **Used but not registered:**
  - pytest 9.0.3: every close; 5,088 Bash commands name it;
  - execnet 2.1.2: named only in xdist's note;
  - Python 3.12.3, SQLite 3.45.1 and git.
- **On the machine, not registered and not used (Table C):**
  - pyright 1.1.414, TypeScript 7.0.2 and typescript-language-server 6.0.1, in the Node v22.23.3 globals;
  - rustup 1.29.1 with toolchain 1.98.1 and rust-analyzer, about 1.5 GB.

  S0b2 installed all of them and recorded them, with uninstall commands, in its own registry. The language servers were rejected, and DEC-074's S0b2 facts say "rejected tools uninstalled", but these were not removed. W2-19 queues "a Rust toolchain for the fixture" as an install (Q-6), though one is already on the machine.
- **The package metadata:** `pyproject.toml` declares only `PyYAML>=6`. That is not a pin, and it leaves out sqlite-vec, which ADR-0002 §2 names as a core need.
  - CI installs `gov` with `python3 -m pip install .` (`ci.yml:45`). So CI runs with whatever PyYAML the package index serves that day, and without sqlite-vec.
  - A wheel built by W2-16 would carry the same unpinned metadata into W2-18's installs.

Ordinary work: yes, because doctor and CI run as a matter of course, and their answers are read as "the stack is as pinned".
Consequence: fails open, in a small way. A changed or unrunnable tool can pass doctor, and CI does not run the pinned stack.
**Severity: medium.**

### F5. The guard's own shell reader refuses ordinary heredocs: 116 refusals in October

**Evidence.**
- **The cause:** `lift_refusal` (`guard/decide.py:750–766`) refuses any command that `_lift_in` cannot split into words: "the command cannot be read, so it is not known to be free of the lift form of gov pause (--off): refused (DEC-409)".
  - `_lift_in` runs `shlex` over the whole command, including the body of a quoted heredoc, which bash takes literally.
  - So one apostrophe in that body makes it fail.
- **Run G-5, the guard's own function on six strings:**
  - **Refused:**
    - a Python heredoc whose comment holds an apostrophe;
    - `git commit -F - <<'EOF'` with an apostrophe in the message;
    - Claude Code's usual commit form, `git commit -m "$(cat <<'EOF' … EOF)"`, with an apostrophe.
  - **Allowed:** the same commands without an apostrophe, and the script run from a file.
- **It happened in this session:** a read-only measuring script was refused because a comment in it said "guard's" (Limits, item 3).
- **Transcripts (G-6):** 116 tool results are this refusal, in 89 transcript files, all in October 2026. One of them is this audit's own (Limits, item 3).
  - Counted strictly: only results that are the hook's refusal. 42 more results only show the text, such as reads of the guard's code; they are not counted.
  - By the refused command's shape (a looser match, which finds 118): 58 heredocs; 20 heredocs inside `$(cat <<…)`, the commit form; 27 `python -c` or `bash -c` strings; 11 others; 2 whose command was not found in the transcript.
- **The reader around it:** 512 lines, five tokenisations, nine open rows (Q3).
- **Tools:**
  - tree-sitter-bash parses heredoc bodies as such (W13);
  - bashlex is GPL and stale (W12);
  - Claude Code's permission matcher is not available to hooks (W9).

Ordinary work: yes, because a heredoc with an apostrophe is the ordinary way to pass a script or a commit message, and Claude Code proposes that commit form itself.
Consequence: other. It fails closed: the honest command is refused and must be written another way. Nothing is written and no work is lost.
**Severity: medium.** That is 116 refusals in a month, each costing a retry and context.

### F6. The test cache's key is written for a built cache; a maintained tool covers most of the need

**Evidence.**
- **The cost today:** every clean close runs the full suite, about 59 minutes in W2-53's last re-close (DEC-726: "about an hour").
- **What DEC-726 decided:**
  - item 1: "test-result caching at close, keyed on exact input hashes (the test files, the source they import, fixtures, configuration)";
  - item 2: W2-48 "evaluates pytest-testmon against a small built-in cache".
- **What W2-48's card (WBS:507–528) asks for:**
  - "Each test's cache key is a sha256 over all of these", namely its file, its imports followed transitively, its fixtures and data files, the configuration, the interpreter and dependency lock, and the command;
  - reused tests "labelled 'reused' in the close record, with the key and the run it came from";
  - a test whose inputs cannot all be hashed ("a dynamic import, a read outside the declared inputs, a network or clock dependency it declares") "is never reused: it runs";
  - item 2's comparison, on a planted change set.

  Its failure KPI is already about behaviour: "each planted change in an input class makes every dependent test run; a change outside every key reuses."
- **What pytest-testmon covers (W2–W5):**
  - It covers code, imports, installed packages and the interpreter version.
  - It works with xdist.
  - It keeps separate records per `--testmon-env` value.
  - It does not track data files.
- **The gaps can be glued:**
  - **Data files:** pass a hash of the declared data globs as `--testmon-env`, so that any data change re-runs everything.
  - **Labels:** record testmon's deselected tests as "reused", with the run that recorded them.
- **What testmon cannot do:**
  - give each test one sha256 key: it keeps checksums per code block. Read literally, DEC-726 item 1 and the card's key KPI rule testmon out before item 2's comparison starts;
  - see which files a test reads. Neither can a built cache without tracing of its own, so on both paths the "read outside the declared inputs" case needs research.
- **Not installed:** coverage and testmon; any install is a DEC-083 package (Q-13).

Ordinary work: yes, because W2-48's engineer will read the KPI as written in the ordinary course of the ticket.
Consequence: other. More code is built and kept. Nothing fails open, because W2-48's failure cases protect correctness on either path.
**Severity: medium.** Every close costs about an hour until W2-48 lands. DEC-780 item 4 gives W2-48 the next free slot after W2-21, "since it shortens every later close".

### F7. lefthook rewrites `.claude/settings.json` on uninstall, and may on install; W2-05 requires install to leave it byte-identical

**Evidence.**
- **What lefthook's own documents say:**
  - Its changelog (W22) records 2.1.10 (2026-07-08): "feat: AI coding agents integration (#1448)", and in 2.2.0: "fix: don't write an install-time lefthook path into AI hook configs (#1544)".
  - Its AI page (W21) says the `claude` provider generates hooks in `.claude/settings.json`, and that on install the lefthook-managed entries are replaced. It describes no way to switch this off.
  - The registry pins 2.1.15, which has the integration but not the 2.2.0 fix. Our `lefthook.yml` has no `ai` key.
- **What DEC-712 recorded** (register:7478–7488):
  - `lefthook uninstall` rewrote `.claude/settings.json`, sorting "the hook events and each hook's fields alphabetically", with the parsed content unchanged;
  - "`lefthook install` will likely re-sort it the same way".
- **What W2-05 measured** (DEC-783's basis): "lefthook 2.1.15's `uninstall` rewrites the settings file unconditionally". DEC-783 kept the measure for install, and made uninstall an owner act followed by restoring the committed file.
- **What W2-05 asks:** "`lefthook install` leaves `.claude/settings.json` byte-identical to the committed file" (WBS:265, re-baselined by DEC-783). W2-08 then reinstalls the hooks.
- **Not tested:** what 2.1.15's install writes, with or without an `ai` key. I could not test it, because the guard refuses reads of the settings file (Limits, item 1).

Ordinary work: yes, because the owner's ordinary `lefthook install` in W2-08 is when it happens, and adapter-portability compares the file byte for byte.
Consequence: other. The result is a red check and a restore by hand; DEC-712 found no hook command changed.
**Severity: medium.** It can hold up W2-05 and W2-08.

### F8. Lexical search uses FTS5 only as a filter, though ranking is built in

**Evidence.**
- **What the search does:** `retrieval/lexical.py:180–212` queries the FTS5 table (tokenizer `porter unicode61 tokenchars '_'`) with the whole question as one quoted phrase, sorts the hits by path and line, then filters each line with Python's `in`. It uses neither `bm25()` nor `rank`.
- **What FTS5 offers (W1):** `bm25()` with per-column weights, `ORDER BY rank`, and the trigram tokenizer for exact substrings. The machine's SQLite (3.45.1) includes FTS5.
- **What is already known and planned:**
  - Lens B F8 measured the effect.
  - W2-13 (DEC-725) plans BM25 with field weights and keeps the exact match as a boost.

Ordinary work: yes, because every plain-language question goes through it.
Consequence: other. The answers are worse, but nothing passes wrongly.
**Severity: medium.** It is already planned: no extra round (DEC-802).

### F9. The glue is about five times DEC-001's trigger; under 900 lines of it re-do what a selected tool does

**Evidence.**
- **Size now:** at `fecb870c`, 14,979 lines in `src/gov` and 935 in the kernel hooks, 15,914 in all.
- **The limits set:**
  - DEC-001's revisit trigger is "glue exceeds ~3k lines";
  - DEC-064 made it a per-wave review, at "glue ≈ 4.5k LOC across three waves";
  - the Wave 2 plan adds about 6,860 estimated lines (WBS:157–161);
  - lens A F6 found that no review was held.
- **Where the lines are:** the guard 3,298; the close 2,149; the checks 1,723; retrieval 1,335; adoption 813; doctor 753; context 384; launch 316; checkpoints 214.
- **The parts that re-do a selected tool's job (Q3):**
  - the guard's shell reading: 512 (F5);
  - the code-graph pull and traversal, about 60, with `closure/` 90 (F1);
  - the schema subset: 169 (F2);
  - the lexical search's own filtering: about 30 (F8).

  These total about 860 lines. The rest is governance logic that no selected tool provides: the close, the guard's rules and the checks.
- **Planned builds that a tool could replace:**
  - W2-48's built cache (F6);
  - parts of W2-37 (F1);
  - growth of the guard's reader (F5).

Ordinary work: yes, because the review is left out of the ordinary writing of each wave's plan (lens A F6).
Consequence: other. The owner has had no decision point on size, and the hour-long close and the review rounds grow with the code.
**Severity: medium.**

### F10. OpenSpec cannot start on the default Node, has nothing to validate here, and doctor reports it as fine

**Evidence.**
- **Why it fails:**
  - OpenSpec's README (W17) says: "Requires Node.js 20.19.0 or higher".
  - The registry installs it under Node v22.23.3, but the default `node` is v18.20.8 (registry lines 17–18).
  - Started by its path with the default PATH, it fails at load: "SyntaxError: Invalid regular expression flags" (G-2).
- **Doctor (G-1):** openspec shows `found_version: null`, `sha256_match: true`, `ok: true`. Doctor passes a tool it cannot start when a file hash matches (`doctor/command.py:484–491`).
- **The check `openspec-validate`** (`check/runner.py:176–193`) is yellow either way, as DEC-781's basis records:
  - on the default PATH it answers "openspec is not on PATH";
  - with Node 22 first it answers "nothing to validate", because this repository has no `openspec/` folder.

  DEC-781 made this row W2-H061, for W2-45.
- **Use (G-6):**
  - agents ran `openspec` 37 times, all in trials: init 12, new 7, schema 5, status 4, validate 3, and 6 others;
  - no Skill tool call named the six `openspec-*` skills or the six `/opsx` commands generated into every session, and no Read call opened the skills' `SKILL.md` files;
  - their descriptions add about 2,100 characters to each session's skill list.
- **What `gov` uses:** OpenSpec's folder layout (`openspec/changes/<change>/proposal.md` and `tasks.md`), in `readiness/checker.py`, `tasks/bridge.py` and `check/claims.py`. The template ships an `openspec/` folder with the feature-readiness schema.

Ordinary work: yes, because every `gov check` and `gov doctor` run meets it.
Consequence: fails open. In DEC-781's own words, "a hard-block check that never measures anything is a false green". Doctor's "ok" for a tool that cannot start is the same kind of thing.
**Severity: low.** DEC-781 already gives the check to W2-45, and W2-22 owns doctor.

### F11. Two skill packs ride in every session, and no agent uses them

**Evidence.**
- **Superpowers v6.4.2:** three skills (test-driven-development, systematic-debugging, verification-before-completion). They are vendored, copied into the kernel's skills and generated by rulesync into every session's skill list.
- **Use (G-6):** Read calls opened these three skills' `SKILL.md` files 21 times (9, 6 and 6), and no Skill tool call named them. The kernel's own skills are called through the Skill tool: test-design 12, orchestration 2, audit 1.
- **OpenSpec's six skills and six commands:** no Skill tool call, and no Read call of the skills' files (F10).
- **Lens E F7** counts 45 skills and 10 agent types that the Gov OS did not write, in every session.

Ordinary work: yes, because every session loads the skill list.
Consequence: other. Context is spent for nothing; nothing fails open.
**Severity: low.**

## 4. Recommendations

**Rounds.**
- Each recommendation first states its findings' classification on one line (DEC-809).
- A finding with "yes" to both questions justifies a round, but no extra round is proposed where a ticket will resume anyway (DEC-802).
- Four findings have "yes" to both: F2, F3, F4 and F10. Each rides on a ticket that will run anyway.
- No finding is about deliberate construction, so none becomes a Wave 3 row (DEC-801).

### R1. Answer code questions with the code-graph tool's own traversal (F1)

Classification: F1 — ordinary work: yes; consequence: other.

- **Make it an entry criterion of W2-37,** the ticket that switches on `gov impact` (DEC-803): the code graph answers on this repository before `gov impact` ships.
- **Give the fix an owner,** by an owner decision. Either:
  - add `src/gov/codeintel/__init__.py` (the query functions) to W2-37's paths; or
  - widen W2-56's paths, since it already holds that file for the daemon's folder.
- **The glue:**
  - use `trace_path` for callers, callees and impact, at DEC-815's depths, which are inside the tool's limit of 15;
  - use `search_graph` for definitions, and for dead code with `max_degree=0`;
  - use per-kind `query_graph` only where a whole kind is needed;
  - never page with SKIP inside the query;
  - pass the tool's error text through.
- **Tests first:** a graph above 100,000 edges is answered completely or refused by name.
- **Research first, small:**
  - `trace_path` latency in the wrapper's session mode (CLI mode took about 4 s per call);
  - whether `detect_changes` gives W2-37's radius.
- **Cost:** it removes our traversal (about 60 lines) and adds a few query calls.

### R2. Validate records with a full JSON Schema validator (F2)

Classification: F2 — ordinary work: yes; consequence: fails open.

- **Owner decision:** widen the held W2-02's paths to the validator part of `src/gov/check/schema.py` for its resume, tests first, with the planted ticket of run G-4 as a case. No extra round (DEC-802).
- **Options and costs:**
  - **(a) Call check-jsonschema,** which is already pinned. No new core dependency; one process for all records. The front matter must be written out as JSON files first, and one probe must confirm that it resolves the kernel's `$ref` to `common.schema.json`.
  - **(b) Use the jsonschema library.** About 20 lines, and the fastest option. But it is a new core dependency: an ADR-0002 §2 change and a DEC-083 install.
  - **(c) Extend our subset to every type.** More code of our own: not recommended.
- **Recommendation:** (a).
- **The four imported decision records** need an owner ruling: correct their ids, or leave `docs/imported/` out of the check.

### R3. Resume a worker only through the launcher (F3)

Classification: F3 — ordinary work: yes; consequence: fails open.

- **Who:** W2-56 (the launcher's sandbox settings) and W2-21 (stable launch) will run anyway. Take this with them, tests first.
- **Now:** a rule in the role text and briefs: "a worker is resumed with `gov launch … --resume`, never with `claude --resume`".
- **Then, after research in W2-40:** let the launcher write the sandbox block into a settings file that Claude Code reads again on resume (W26 says the standard settings files are re-read). Research first whether a worker can change that file.
- **A guard rule** refusing `claude --resume` in Bash is cheap, but it rests on the parser of F5.

### R4. Make the registry, doctor and the package say what actually runs (F4, F10)

Classification: F4 — ordinary work: yes; consequence: fails open (small). F10 — ordinary work: yes; consequence: fails open.

These ride on W2-22 (doctor and the registry in its paths), W2-43 (CI) and W2-16/W2-18 (releases); no extra round.

- **Register what is used:** pytest, execnet, and Python, SQLite and git as platform entries.
- **Decide S0b2's leftovers:** remove the language servers and TypeScript (DEC-074's "rejected tools uninstalled"), or register them with a purpose; register the Rust toolchain for W2-19, or remove it, before Q-6 is answered.
- **Record what each hash covers.** Doctor should say "version only" where no installed file can match.
- **Doctor starts each tool** under the runtime it will really use, so a tool that cannot start fails.
- **Pin `gov`'s dependencies** (PyYAML 6.0.1, sqlite-vec 0.1.9) in a hash-locked requirements file. CI uses it (`actions/setup-python` and pip's `--require-hashes`, W18 and W19), and so does `gov install`.

### R5. Put the sandbox first and stop growing the guard's shell parser (F5, F9)

Classification: F5 — ordinary work: yes; consequence: other. F9 — ordinary work: yes; consequence: other.

- **No round of its own.** It rides on W2-42 (`src/gov/guard/**`), tests first.
- **The tokeniser:** one shared tokeniser for the five readers. It reads a quoted heredoc's body as literal text and splits only the command around it. Cases:
  - Claude Code's own commit form with an apostrophe;
  - a Python heredoc with an apostrophe in a comment.
- **The sandbox:** W2-21 sandboxes the leads (DEC-769; lens E R1), and the orchestrator's own session stays unsandboxed (DEC-769 item 4). After that, the guard's Bash reading is the only layer for the orchestrator's session, and an early, readable refusal elsewhere. DEC-770 already makes a reading hole that only an unsandboxed session can reach a list row, not a round.
- **The open rows:** settle the nine parser rows in that light. W2-M026's own text already allows "covered by a sandbox in every session".
- **tree-sitter-bash:** only after a spike that measures latency against DEC-149's 100 ms p95 and replays the nine rows' cases. It would come as a CIT-P (a change proposal) with an ADR-0002 core-dependency change.
- **bashlex:** no.

### R6. Let W2-48 compare the tools on behaviour, not on a key format (F6, F9)

Classification: F6 — ordinary work: yes; consequence: other. F9 — ordinary work: yes; consequence: other.

- **No round.** A small owner decision before W2-48 starts: restate DEC-726 item 1 ("keyed on exact input hashes") and the card's key KPI as behaviour, as the card's failure KPI already is:
  - each planted change re-runs every dependent test;
  - a change outside every input reuses;
  - every reuse is recorded with the run it came from;
  - a failed result is never reused.
- **The glue path:**
  - pytest-testmon and coverage, as one DEC-083 package (Q-13);
  - `--testmon-env` set to a hash of the declared data globs and the test command;
  - deselected tests recorded as "reused", from `.testmondata`;
  - `.testmondata` written only by main-tree closes;
  - `--testmon-noselect` for W2-24's and W2-46's full runs.
- **Research (W2-48's own document):**
  - the planted change set;
  - how either path learns that a test reads a file outside its declared inputs, which the card says must never be reused;
  - xdist with testmon on this suite;
  - coverage's overhead on the recording run.

### R7. Settle lefthook's rewrite of the settings file before W2-08 (F7)

Classification: F7 — ordinary work: yes; consequence: other.

- **No round of its own.** It rides on W2-05's resume.
- **Measure first:** an owner-run `lefthook install` in a scratch clone, with and without an `ai` key, shows what lefthook writes.
- **Then choose one of:**
  - **(a)** commit `.claude/settings.json` in the form lefthook writes, so that an install leaves it byte-identical;
  - **(b)** compare parsed JSON instead of bytes in adapter-portability. This changes W2-05's KPI again;
  - **(c)** pin lefthook at 2.1.9, before the integration, and lose the later fixes;
  - **(d)** move the pin to 2.2.0 or later, which has the fix of #1544, as a DEC-083 package and after the same measure.
- **Recommendation:** (a) if the measure shows a stable form; otherwise (b).

### R8. Rank lexical search with FTS5's own functions (F8)

Classification: F8 — ordinary work: yes; consequence: other.

- **No extra round:** W2-13 as planned (DEC-725).
- **The glue:**
  - `bm25()` with column weights and `ORDER BY rank` for questions;
  - a second FTS5 table with the trigram tokenizer for exact identifiers, in place of Python substring filtering.

### R9. Hold DEC-064's size review now, using this report's map (F9)

Classification: F9 — ordinary work: yes; consequence: other.

- **No round.** An owner decision point at the Wave 2 pause: per area, keep, glue or retire, starting from Q3's table.
- **What it would change:** R1, R2 and R8 remove about 260 lines. R6 avoids W2-48's built cache. R5 stops the guard's reader from growing.

### R10. Retire OpenSpec here and trim the unused skill packs (F10, F11)

Classification: F10 — ordinary work: yes; consequence: fails open. F11 — ordinary work: yes; consequence: other.

- **No extra round:** DEC-781 already gives the check to W2-45.
- **Take DEC-781's "not applicable here" branch** for this repository, where nothing uses OpenSpec content.
- **Keep the template's `openspec/` layout,** which `gov` reads in adopted projects. There, OpenSpec must start under Node 20.19 or later (R4).
- **Trim the skill lists:**
  - stop generating the twelve OpenSpec skills and commands into this repository's sessions;
  - drop Superpowers from the generated set unless a role file names it.

### The glue that most reduces the remaining build

Ranked by build avoided or removed. Each glues a tool that is already selected or maintained.

1. **pytest-testmon for W2-48 (R6, F6).** This avoids most of the largest unbuilt item on the list: a per-test tracer of imports and fixtures, with its own storage and invalidation. Data files are covered coarsely, by a hash of the declared globs. It also shortens every close, which costs about an hour today.
2. **The code-graph tool's own traversal (R1, F1).** It removes our traversal code, and it unblocks W2-37's `gov impact`, W2-38's impact-selected tests and adoption at scale. `detect_changes` may cover part of W2-37.
3. **A full schema validator (R2, F2).** It replaces a subset that would otherwise grow with every record type.
4. **The sandbox in place of a growing parser (R5, R3, F5, F3).** It stops nine parser rows from turning into rounds.
5. **FTS5's own ranking (R8, F8):** planned and small.
6. **Standard installers for CI and releases (R4, F4):** a hash-locked requirements file, `setup-python` and Copier's update, in place of our own installer logic in W2-17 and W2-18.
