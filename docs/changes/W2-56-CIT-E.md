# W2-56 CIT-E: `gov launch` usable for every worker, on the guard alone (DAEO-wnnz)

Ticket: `.tickets/DAEO-wnnz.md` (DEC-799, DEC-1112 (1), DEC-1097 (8), DEC-1083, DEC-1099). Engineer, 2026-11-09.
Code: `src/gov/launch/launcher.py` (call sites and argument checks), `src/gov/launch/sandbox.py` and
`src/gov/launch/environ.py` (new), `src/gov/codeintel/__init__.py` (the daemon's folder only), `tests/conftest.py`
(S1's two lines), `template/governance/kernel/settings.json` (S14).

## 1. How each allowed-path form is held (S3)

No sandbox entry is made from any allowed path (DEC-1112 (1)): the sandbox's write list is the session's temp folder,
its own run folder and the reranker's log file (S11), the same for every ticket. Write scope to the ticket's allowed
paths (DEC-820 (4)) is the path-map guard's alone (`gov.guard.decide._match_pattern`, run by
`template/governance/kernel/hooks/pretooluse.py` for `Write`, `Edit` and the Bash writes it can name):

| Form in `allowed_paths` | Example | How the guard reads it | What is left open beside it |
|---|---|---|---|
| A file | `src/gov/launch/launcher.py` | that path exactly | the script-write gap (section 2) |
| A folder and everything under it | `tests/unit/launch/**` | `**` matches across folders | the script-write gap |
| A name pattern | `tests/unit/test_batch*` | one `*` matches within one folder only (`[^/]*`): `tests/unit/test_batch_one.py` passes; `tests/unit/test_other.py`, `tests/unit/sub/test_batch_four.py` and `tests/test_batch_five.py` are refused | the script-write gap |
| `?`, `[...]` in a name | (none today) | literal characters, not wildcards: the path must carry them | the script-write gap |

Nothing is widened silently: a pattern never reaches the sandbox, so the sandbox cannot read it more widely than the
guard does (the Linux sandbox skips patterns, and today's `.gov-runtime/` patterns bind only the file tools).

## 2. The script-write gap (S2)

A write the guard cannot name is not refused inside the worktree: `python3 -c "open('src/x.py','w').write('…')"`, a
test that writes a file, a build tool's output. The operating system's write list does not hold it either, because
the worktree's paths are not narrowed there (DEC-1112 (1): set-up B, a write list made from the path map, is Wave 3's
row). What still holds today:

- outside the worktree, the operating system refuses every write but the temp folder, the run folder and the
  reranker's log (a script writing into another worktree is refused, as before);
- inside the worktree, the literal deny rules hold for each `.gov-runtime/` entry but `scratch` that exists at launch
  (DEC-180), for `tests/acceptance` (every role but the test designer), `.tickets` and `.claude` (DEC-315); those are
  refused to a script too;
- the audit's diff check: a file a script wrote outside the ticket's paths shows in the ticket's diff and fails its
  review.

So the gap is a script writing to a path inside the worktree, outside the ticket's paths, and not under a literal
deny rule. It is named, not closed.

## 3. Accepted-arguments list against the refusal list (S6, lens E R6)

Built: a refusal list. After `--`, beside DEC-313's (`--dangerously-skip-permissions`,
`--allow-dangerously-skip-permissions`, `--permission-mode bypassPermissions`, `--add-dir`, `--settings`, `--bare`,
`--setting-sources`), the launcher refuses `--restricted`, `--safe-mode`, `--agents`, `--plugin-dir`, `--plugin-url`,
`--mcp-config` and `--system-prompt`, alone, with a spaced value and in the `=` form, in any position. An argument is
matched as a whole word before any `=`: a prompt that names one inside a longer text is no argument and starts.

| | Refusal list (built) | Accepted-arguments list |
|---|---|---|
| A new CLI argument that drops the guard | passes until it is added here (fails open) | refused until it is admitted (fails closed) |
| Ordinary work | every prompt, `-p`, `--model`, `--output-format`, `--resume` passes untouched | each argument a worker needs must be listed, with the shape of its value; a prompt is a free value that must be told apart from an argument |
| Values that look like arguments | a prompt word equal to a refused name is refused (rare, safe) | the same question, harder: which free values follow which argument |
| Upkeep | one line per new dangerous argument, after each CLI release | one line per argument workers use, and every CLI release can rename them |

Recommendation: keep the refusal list now (it is what the KPI line names, and W2-60a refuses the arguments it then
sets itself: `--agent`, `--model` other than the role's, and the rest), and move to an accepted list when W2-60a fixes
the arguments a launched session takes (then the list is short and known). Not refused here, to be weighed with W2-60a:
`--append-system-prompt`, `--system-prompt-file`, `--strict-mcp-config`, `--allowedTools` and `--disallowedTools`.

## 4. S7's way: the start lock

The launcher already holds the machine-wide start lock (`gov.launch.gate.StartLock`, W2-20 review F1) from the gate's
check until the started session is entered in the registry, then gives it back. So sessions start one at a time on
the machine (and so per repository) and the lock is short: it is never held for a session's life, and three launches
made at once from three worktrees of one repository all start and run together (the acceptance case). No second lock
was added.

What it does not cover: the CLI's sandbox builds its mounts at each command, not only at the start, so a git lock
file that another session's git command makes and removes in the shared `.git` while a command's sandbox is set up
can still be missing when it is bound. That race belongs to the CLI's sandbox; the launcher cannot hold a lock across
another session's commands without serialising the sessions themselves (which the KPI line rules out).

## 5. S11's way: one log file

`~/.cache/gov-os/rerank.log` (`gov.retrieval.rerank`'s `CACHE_REL` and `LOG`) is on the write list, so a sandboxed
search the service does not answer writes its one FALLBACK line where `gov status` counts it. The launcher makes the
file (mode 0600, its folder 0700) when it is missing, since the sandbox cannot bind a file that is not there. The
write list widens by that one file and nothing else (D-11 (a)). A log that is a link, or no regular file of the
user's, or a `.cache` or `.cache/gov-os` that is a link, is left off the list (its target is never touched); the
session then searches as before and its fallback is not counted.

The other way (D-11's package): the session's searches write their FALLBACK lines in its own temp folder and the
launcher appends them to the log when the session ends. It keeps the write list at today's two entries, but the count
arrives only after the session, and is lost when the launcher is killed.

## 6. Other choices the code makes

- **S5, the cleaned environment** (`environ.py`): a list of what passes, not a filter. Of the parent's variables:
  `PATH`, `HOME`, `LANG`, `LC_ALL`, `USER`, `LOGNAME`. The launcher's own: `TMPDIR`, `CLAUDE_CODE_TMPDIR`, `GOV_ROLE`,
  `GOV_TICKET`, `GOV_STORE`. **What the CLI needs to sign in** passes to the CLI process only, never into
  `--settings` (whose text other users can read in the process list): `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`
  and `CLAUDE_CODE_OAUTH_TOKEN`, **the one `CLAUDE*` exception** (D-3). A CLI signed in through `~/.claude` needs
  none of them. Not passed: `TERM`, `SHELL`, the other `LC_*` and `XDG_*` variables (an interactive launch draws its
  screen without `TERM`; workers start with `-p`). A lead gets the same process environment and keeps its
  `--settings` env of role and ticket alone (W2-136 S9).
- **S4, placeholders** (`sandbox.exclude_placeholders`): the CLI's fixed names (`.bashrc`, `.bash_profile`,
  `.profile`, `.zshrc`, `.zprofile`, `.gitconfig`, `.gitmodules`, `.ripgreprc`, `.mcp.json`, `.vscode`, `.idea`), its
  folders (`.claude/commands`, `.claude/agents`, `.claude/skills`, `.claude/hooks`) and each literal `Edit` deny rule
  that names nothing at launch (the prefixes of `scratch` in `.gov-runtime/`) are added once to the repository's
  exclude file (`<common .git>/info/exclude`, shared by its worktrees), each with `!<name>/`, so a folder of that
  name is still added. It holds for the session and for its caller in the same worktree, inside the sandbox too (an
  ignored character device is not added). Left open: a new, untracked regular file at one of those names (a real
  `.mcp.json`) is ignored too and needs `git add -f`; a launch whose exclude file cannot be written is refused.
- **S12, signals**: the CLI leads a process group of its own; an ending signal goes to the group, the kill after
  `END_WAIT_S` too (also when the leader has already ended, D-5), and whatever the session left in its group when it
  ended by itself is asked to end and killed `END_WAIT_S` later. On a terminal, the group is made the terminal's
  foreground group and the terminal is taken back after.
- **S15**: the temp folder is removed whole, after its folders are opened to their owner (a 0500 module cache, a
  0000 folder); a fifo goes, a link goes as a link and its target stays.
- **S1**: the daemon folders stand in the test session's own folder (`GOV_CBM_BASE`, made and removed by
  `tests/conftest.py`), else in the launched session's temp folder (`<gov-launch-…>/cbm`, found from
  `CLAUDE_CODE_TMPDIR`), else in `/tmp/gov-cbm-<uid>`. The worker's temp folder is `gov-launch-` and 8 letters
  (D-12): with the temp root `/tmp`, a daemon folder plus the tool's 50-byte socket tail is 95 bytes (a test
  session's: 101), under 107. The real tool is off `PATH` for every case but W1-16's and W1-20's.
- **S8 on Linux (D-13)**: the one-path `network.allowUnixSockets` is built from the service's own setting and is inert
  on Linux (the CTO's measure); its reach and S10 are the owner's DEC-105 choice.

## 7. The S13 conflict (named, not resolved here)

S2 keeps a literal deny rule for each `.gov-runtime/` entry but `scratch` that exists at launch (DEC-180). `gov
rebuild` writes `.gov-runtime/rebuild/` (and the code index's `.gov-runtime/codeintel/`), so inside the sandbox it
fails "`.gov-runtime/rebuild/stores.json` could not be removed: Read-only file system" (the CTO's real run). Both are
KPI lines; no deny rule was dropped. The smallest change that resolves it lies outside these paths: `gov rebuild` and
the code index take their working folders from the session's temp folder (or `.gov-runtime/scratch/`) when they run
in a launched session, so the deny rules stay whole (section 7 of the return carries the three options).

## 8. S10 (the CTO's)

*Measured by the CTO outside the sandbox, in `docs/changes/W2-127-evidence.md`.*
