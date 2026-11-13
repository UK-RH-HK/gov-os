# P-PERMISSIONS-1: why the CTO's session prompted so often, and which prompts can stop (for the owner)

**DECIDED (owner, 2026-11-06, DEC-1080): approved, with read-only git only through `git -C` (section 4 (A)).** The
CTO's own change (C) holds from now on and goes into the brief of every agent it starts. The settings change is
`ACT-PERMISSIONS-1.md`, for the operator. **Changed by DEC-1081 (1):** the `git -C` rules were dropped; the ACT applied
18 rules (operator, 2026-11-06).

**Two points this package missed (the owner, 2026-11-06, seen in `/permissions`; accepted by the owner under our
threat model):**
1. **The owner's user-level settings already allow every Bash command, every Read, Edit and Write, and web access**
   (`~/.claude/settings.json`: `Bash(*)`, `Read(*)`, `Edit(*)`, `Write(*)`, `WebFetch(*)`, `WebSearch(*)`; deny
   empty). So:
   - section 4 (A)'s project list adds nothing for Bash;
   - section 4 (B)'s "keep asking" list does not ask.

   **The guard (the PreToolUse hook) is the real check**, not the permission lists.
2. **The prompts that remain are Read calls outside the repository.** `Read(*)` does not reach a folder outside the
   working directories. `ACT-PERMISSIONS-2.md` adds the measure clones and the worktrees as additional directories,
   keeps `~/gov-os-eval` asking, and denies Read on the three hidden folders, which the guard does not cover outside
   the repository.

- **By:** the CTO (session `812bc5ce`), 2026-11-06, at the owner's question. Nothing is changed: a settings change is
  the operator's ACT (P-ACT-SPLIT (a)).
- **Evidence:** the two settings files (`.claude/settings.json`, `.claude/settings.local.json`), and this session's own
  transcript, its commands sorted against the allow list, counts only. There is no log of the prompts themselves, so
  which call prompted is inferred from the rules.

## 1. Why so many prompts
- **The rules:** no ask rules; 24 allow rules (some git subcommands, `gov`, `tk`, `python3`, `sha256sum`, `sleep`,
  `~/.local/bin/claude`, `cd /home/usain/gov-os-worktrees/…`, and `bash` of the CTO's scratch scripts by full path);
  deny rules for `sudo`, `git push`, key and secret files and the held-out material. Everything else asks.
- **The main cause is the CTO's command style.** Of about 404 shell calls in the main session, only about 10 were a
  single command on the list. About 390 were **compound** (`cd X && …`, pipes, `;`, loops, here-documents, a variable
  set first). A compound command asks when any part of it is not on the list (`ls`, `grep`, `sed`, `cat`, `cp`,
  `mkdir`, `mv`, `printf`, `ps`, `setsid`, `timeout`, `find`, `tail`, `nvidia-smi`, `~/.local/bin/gov`, …), unless
  the tool judges the whole of it read-only.
- **The in-session agents add theirs.** The auditor, designers, reviewers, engineers, the drafters and two research
  sessions ran about 452 shell calls, 107 file writes and edits, and **108 web calls** (80 WebFetch, 28 WebSearch, all
  by the research survey). Their prompts reach the owner too. The workers started with `gov launch` run in their own
  sandbox with their own settings and prompt nobody.
- **Files written outside the repository** prompt as well: briefs written into worktrees' scratch
  (`~/gov-os-worktrees/*/…`), the rehearsal and stand-in folders in the session's scratchpad (`/tmp/claude-1000/…`).

## 2. The kinds of command that prompted today
| Kind | What it does, and why | Where it acts | Rule that made it ask |
|---|---|---|---|
| Reading and inspecting | `grep`, `sed -n`, `ls`, `head`, `tail`, `wc`, `cat` of files and logs; `ps`; `nvidia-smi`; `tmux ls`; `crontab -l` (the start checks, reading records, checking runs) | repository, worktrees, run folders, logs; read only | a part not on the allow list (mostly inside `cd … &&` chains) |
| Writing records by shell | `cat > file <<…`, `cat >>`, `printf >`, `sed -i`: briefs, register and in-force lines, ticket notes, the stand-by file | the repository and its scratch | not on the list |
| Copying and moving | `cp`, `mkdir`, `mv`: the ACT-MSET-3 settings files, worktree briefs, the stand-by file's end, moving the survey files | mostly the repository; some outside (below) | not on the list |
| Writes outside the repository | the sets root `~/gov-os-eval`: the `memory-verdict-2` line in its path map (approved, DEC-1075), its backup, and the visible half restored after the CTO's slip (DEC-1079 day); briefs into worktrees; the scratchpad | outside the repository | not on the list, or a path outside the working directory |
| GPU and long jobs | `setsid -w bash <script>` for the trial windows and measures; `timeout … heavy_slot.sh pytest …`; `PYTHONPATH=… bash heavy_slot.sh …` | the machine's GPU, the shared reranker (stopped by pid and restored, under the trial ACT and class 3), run clones | `setsid`, `timeout` and variable prefixes are not on the list |
| Starting worker sessions | `~/.local/bin/gov launch <role> <ticket> -- -p …` | a sandboxed session in a worktree | the full path is not the allowed `gov …` form |
| Local network | `curl` to the two embedding servers (127.0.0.1:11434 and :11435) to warm them; the embedder check through Python | this machine only | inside scripts or chains not on the list |
| Internet | the research survey's WebSearch and WebFetch (approved for that session, DEC-1077 (d)) | the web, read only | each new site asks |
| Deletion | `rm -rf` of the CTO's own scratchpad folders and old measure-run folders in `~/gov-os-runs/D4B/`; one `rm` of tracked files, **refused by the guard's hook** and not done | scratch and run folders only | not on the list (`rm` is free by DEC-1050 (8), but the tool still asks) |

**What did not happen:** no install, no `sudo`, no `git push`, no secret read, no change to `.claude/` settings, no
change to the pinned gov or the crontab.

## 3. What was unusual or riskier than normal work
1. **Stopping and restarting the shared reranker** in three trial windows (by its own pid; under ACT-RERANK-TRIAL-1,
   DEC-1076 and DEC-1077, and class 3's restart). Every session's ranked search waited on it for the window.
2. **Writes in the sets root `~/gov-os-eval`**, which holds the hidden questions: the approved path-map line, its backup,
   and the visible half's restore after the CTO's own slip. No hidden question was read.
3. **A stand-in model** built in the scratchpad with the trial's Python (tiny random weights, from mxbai's own
   configuration; no download).
4. **The research survey's web access.**
5. **Detached GPU jobs** (`setsid`), each in its own process group with the backstop on it.

None was outside the decided work, but the prompts gave the owner no way to see that. **The CTO's slip:** it did not say
in one line, before each, what a prompting command would do.

## 4. The proposal (the operator's ACT, for the owner to decide)
**(A) Allow, as routine and read-only or already decided** (`.claude/settings.local.json`, `permissions.allow`):
- `Bash(ls *)`, `Bash(grep *)`, `Bash(head *)`, `Bash(tail *)`, `Bash(wc *)`, `Bash(cat *)`, `Bash(stat *)`,
  `Bash(diff *)`, `Bash(ps *)`, `Bash(date *)`, `Bash(du *)`, `Bash(tmux ls)`, `Bash(crontab -l)`,
  `Bash(/usr/lib/wsl/lib/nvidia-smi --query-gpu=*)`. Reading stays guarded: the hook refuses secrets, the held-out
  material and the hidden halves whatever the allow list says.
- `Bash(~/.local/bin/gov *)` and `Bash(/home/usain/.local/bin/gov *)`: the same pinned gov `gov *` already allows.
- **Read-only git through `git -C` only** (the owner's correction, DEC-1080): `git -C <dir>` with `log`, `show`,
  `diff`, `status`, `rev-parse`, `branch --list`, `ls-files` or `merge-base`. Every other git command keeps asking, and
  `git push` stays denied (a deny rule wins).
- `Bash(cd /home/usain/Dynamic-Agentic-Engineering-OS*)`, `Bash(cd ~/gov-os-worktrees/*)`.

**(B) Keep asking** (each is either outside the repository, destructive, a machine job, or the network):
- `rm`, `mv`, `cp` and `mkdir` outside the repository and its scratch; anything writing `~/gov-os-eval`, `~/.local`,
  `~/.cache`, `~/.config`, `~/.ollama`;
- `setsid`, `timeout` and other job launches (the GPU windows), `curl`;
- `~/.local/bin/gov launch` is covered by (A)'s gov rule; if the owner wants every worker start to ask, add
  `Bash(~/.local/bin/gov launch *)` to `ask` instead;
- WebFetch and WebSearch, per session.

**(C) No settings change, from the CTO at once:**
- read with the Read and Grep tools instead of shell chains (they do not prompt in the repository);
- one simple command per call where it can, and no `cd … &&` chains;
- before any command that will prompt, one line in the chat: what it does and why.

**Expected effect:** (C) alone removes most of the main session's prompts; (A) removes most of the rest, including the
agents' read-only ones. **Basis:** question 4 (less of the owner's time on prompts that carry no decision) and
question 2 (every write outside the repository, deletion, machine job and network call still asks).
