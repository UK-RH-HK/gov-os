# ACT-PERMISSIONS-1: the approved allow rules for the CTO's session (P-PERMISSIONS-1, DEC-1080)

- **For:** the owner's operator, in a plain terminal (a `.claude/` settings change: P-ACT-SPLIT (a)). The CTO writes
  no settings.
- **What it does:** adds 26 allow rules to `.claude/settings.local.json`'s `permissions.allow`; removes nothing; leaves
  the deny and ask lists and every other key exactly as they are; keeps a backup beside the file.
- **The rules** (in `ACT-PERMISSIONS-1/apply.py`):
  - read-only commands: `ls`, `grep`, `head`, `tail`, `wc`, `cat`, `stat`, `diff`, `ps`, `date`, `du`, `tmux ls`,
    `crontab -l`, `/usr/lib/wsl/lib/nvidia-smi --query-gpu=…`;
  - the pinned gov by its path: `~/.local/bin/gov …` and `/home/usain/.local/bin/gov …` (what `gov …` already allows);
  - read-only git through `git -C <dir>` only: `log`, `show`, `diff`, `status`, `rev-parse`, `branch --list`,
    `ls-files`, `merge-base`;
  - `cd` into the repository and the worktrees.
- **Still asking** (no rule added): `rm`, `mv`, `cp`, `mkdir` outside the repository; writes to `~/gov-os-eval`,
  `~/.local`, `~/.cache`, `~/.config`, `~/.ollama`; `setsid`, `timeout` and other job launches; `curl`; web access;
  every other git command (`git push` stays denied).

## The commands (one terminal, about 1 minute)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
P=governance/project/orchestration/packages/ACT-PERMISSIONS-1
python3 $P/apply.py .claude/settings.local.json --check     # expect: 0 of 26 present (exit 1)
python3 $P/apply.py .claude/settings.local.json             # expect: applied: 26 rule(s) added
python3 $P/apply.py .claude/settings.local.json --check     # expect: 26 of 26 present (exit 0); deny ['Bash(git push *)']; ask []
```
The CTO's session reads the new rules from its next start (or `/permissions` shows them at once).

## Undo
```
python3 $P/apply.py .claude/settings.local.json --undo      # restores the backup settings.local.json.pre-act-permissions-1
```

## The rehearsal (DEC-1057)
`.gov-runtime/scratch/orchestrator/drafts/act-permissions-1/rehearse.py`: the steps above on a copy of the real file
(only the path substituted), the real file hashed before and after. **REHEARSAL PASS, 15 of 15:** check before (0 of
26, exit 1); apply (26 added); check after (26 of 26); apply again (0 added); deny unchanged; ask unchanged; every old
allow rule kept in order; only the ACT's 26 added; `git push` still denied; every `git -C` rule a read-only subcommand;
no `rm`, `mv`, `cp`, `mkdir`, `curl`, `setsid` or `timeout` allowed; the other keys unchanged; undo; the copy equal to
the original byte for byte; the real file unchanged throughout (sha256 `767872e029c7`). The first run found one fault in
the rehearsal's own check (it read `merge-base` as `merge`), fixed before this hand-over.

## One caveat, so it is approved knowingly
In a permission rule `*` matches any text, spaces included. So `git -C * log *` also matches a write command that
happens to hold the word `log` later (for example `git -C <dir> commit -m "fix the log"`). Three things bound it:
`git push` stays denied (a deny rule always wins); `git commit`, `git merge` and the other writes already allowed by
today's rules are unchanged by this ACT; and the guard's hook still judges every command. The CTO's own rule (DEC-1080)
is to use `git -C` only for the eight read-only subcommands. If the owner wants no such overlap, drop the eight
`git -C` rules (delete them from `RULES` in `apply.py`) and those reads keep asking.

**Basis:** question 4 (the owner's time spent only on prompts that carry a decision) and question 2 (every write outside
the repository, deletion, job and network call still asks).
