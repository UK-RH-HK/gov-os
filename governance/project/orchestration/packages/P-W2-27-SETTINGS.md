# P-W2-27-SETTINGS: EXAMIN's copy's settings reshaped to Gov OS's standard (the owner's decision, F-015)

## 1. Context
- EXAMIN's F-015: A5's auditor cannot start. `gov launch` refuses because `.claude/settings.json` carries
  `permissions.additionalDirectories`, the dead Windows path that `gov adapters generate` carried over (F-000, F-002).
  Every worker launch meets the same refusal (DEC-313).
- The owner, as EXAMIN's owner, decided to reshape the copy's whole settings to Gov OS's standard. The same reshape
  applies to EXAMIN's real repository at W2-29.
- The product fix stays flag-not-drop: the adapters and `gov doctor` name such rules and dead directories, and the
  launcher's refusal names the entry.

**Gov OS's standard** is what `gov adapters generate` writes for a fresh adopter (seen on W2-81's six repositories):
- `allow` holds `Bash(gov launch:*)` alone;
- `deny` holds the walls;
- the kernel's hooks are registered;
- there is no `additionalDirectories` and no local settings file.

Gov OS gives each session its tools when it starts. Its launcher passes `--permission-mode acceptEdits --allowedTools
Bash Read Edit Write Grep Glob` (the auditor gets no Edit or Write), and the guard judges every call. The repository
pre-approves nothing broad.

## 2. Every rule, judged

**`.claude/settings.json`, `permissions.allow`**

| Rule | Decision | Why |
|---|---|---|
| `Bash(python)` | drop (ask) | Pre-approves the interpreter itself. The kernel keeps an interpreter-wide command at ask, and the guard judges it either way. |
| `Bash(mkdir -p "c:/Prior Art Search App/…" … && echo "created")` | drop | A one-off command on a dead Windows path; it can never match on this machine. |
| `Edit(/.claude/skills/prior-art-search/**)` | drop (ask) | Pre-approves edits under `.claude/`, which Gov OS closes to launched sessions (DEC-315). The skill never edits itself; a change to it is the owner's or a product-spec session's. |
| `Bash(PYTHONIOENCODING=utf-8 python)` | drop (ask) | The interpreter again, with a Windows encoding workaround. |
| `Bash(gov launch:*)` | **keep** | Gov OS's standard: the orchestrator starts its workers. |

**`.claude/settings.json`, everything else**

| Item | Decision | Why |
|---|---|---|
| `additionalDirectories`: `c:\Prior Art Search App\.claude\skills\prior-art-search\references` | **drop** | Dead (a Windows path). It blocks every launch (DEC-313). The skill's references sit in the repository at `.claude/skills/prior-art-search/references/`. |
| `deny`: `Bash(sudo *)`, `Edit(.tickets/**)`, `Read(//home/usain/gov-os-eval/**)`, `Read(//home/usain/gov-os-workbench/**)` | **keep** | Gov OS's walls. |
| `hooks`: Gov OS's kernel hooks (PreToolUse guard, PreCompact, SessionStart, PostToolUse, PostToolUseFailure, Stop, SubagentStop) | **keep**, byte for byte | Gov OS's walls. |
| `hooks`: EXAMIN's own `.claude/hooks/guard.py` (PreToolUse) | **keep** | EXAMIN's genuine protections: no write to the frozen rollback, no deletion from `archive/`, no file outside its layout. It refuses only, so layered with Gov OS's guard a call must pass both. |
| `hooks`: EXAMIN's own `precompact.py` and `sessionstart.py` | **keep** | EXAMIN's compaction protocol. Its retirement is the adoption's legacy decision (the path map, A8), not the settings'. |
| `$schema` | keep | — |

**`.claude/settings.local.json`** (tracked in EXAMIN's history): **the file is removed from the repository.**

| Rule | Decision | Why |
|---|---|---|
| `Bash` (plain) | to the session's start | Pre-approved for every session in the repository, it is broader than Gov OS's standard. Each session gets Bash at its start (`--allowedTools`), as Gov OS's launcher does, and the guard judges each call. |
| `Edit`, `Write` | to the session's start | The same. In the repository the kernel keeps them at ask. |
| `Read`, `Glob`, `Grep` | drop (to the session's start) | Unqualified `Read` pre-approves reads anywhere on the machine. Reads inside the project need no rule, and sessions get these tools at start. |
| `WebFetch`, `WebSearch` | drop (ask) | prior-art-search does its network work through its own Python scripts (Scopus and ScienceDirect, OpenAlex, Crossref, Semantic Scholar, The Lens, EPO OPS, PatentsView), not through these tools. Its user runs it interactively and approves a web step when asked. Launched workers get WebSearch and WebFetch from their role (DEC-158). |
| `Bash(pip show *)` | drop (ask) | Read-only, but outside the standard. Asked when needed. |
| `Skill` | to the session's start | Interactive sessions load skills; given at start with the other tools. |

**What EXAMIN's own agents, skills and commands keep:**
- prior-art-search: its scripts and references stay in place, and its network keys come from the environment as
  before. Its user approves its Python and web steps when asked.
- EXAMIN's commands (`.claude/commands/*.md`, `allowed-tools: Bash(openspec:*)`) declare their own tools.
- EXAMIN's agents (`.claude/agents/`, now Gov OS's role files) are started by `gov launch`, which gives them their
  tools.
- EXAMIN's guard and compaction hooks stay wired.

## 3. Tested on a clone (2026-11-15 22:40)
1. The operator script refused nothing and made one commit. Its diff removes 23 lines and nothing else: 7 in
   `.claude/settings.json`, 16 by deleting `.claude/settings.local.json`.
2. Every hook and every deny rule compares equal before and after (checked in the script).
3. The launcher's own settings check (`gov.launch.launcher._check_repository_settings`): **before**, it refuses
   "carries permissions.additionalDirectories … (DEC-313)"; **after**, it passes.
4. `gov adapters generate` run again after the reshape changes nothing: the tree stays clean and the settings are
   identical. The reshape survives a regeneration.

## 4. The operator's commands (a plain terminal, no GOV_ variable)
```
env | grep '^GOV_'          # must print nothing
sha256sum /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-27-settings/operator_settings.py
#   1f76e8ea57406192d24c28dd9a190585b72abd8212e4fc2ba74c2ea4b0bfb06f
python3 -I /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-27-settings/operator_settings.py
#   prints the commit, and: status after: ''
```
Then restart the EXAMIN CTO with its tools given at start. Without them, every Bash call now asks.
```
tmux kill-session -t examin-cto
tmux new -d -s examin-cto -c /home/usain/gov-os-runs/W2-27/examin env -u GOV_TICKET -u GOV_DEV_TIERS -u GOV_ROLE GOV_ROLE=orchestrator GOV_TICKET=exa-dt1z claude --permission-mode acceptEdits --allowedTools Bash Read Edit Write Grep Glob Skill
```
Then paste brief b70ff2332e89 as at the first start. The replies file tells it to re-run the precondition probes (r3),
then A5.

## 5. At W2-29 (EXAMIN's real repository)
The same table applies to the real repository's settings, as the owner decided. They are judged again there because
its files may differ, and run as its owner's commit.

**Your line:** none needed. You decided the reshape; your operator runs section 4.
