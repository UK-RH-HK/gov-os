# ACT-PERMISSIONS-1: the approved allow rules for the CTO's session (P-PERMISSIONS-1, DEC-1080, DEC-1081 (1))

**Revised 2026-11-06 (DEC-1081 (1)): the eight `git -C` rules are dropped; 18 rules, no new git rule of any kind.**

- **For:** the owner's operator, in a plain terminal (a `.claude/` settings change: P-ACT-SPLIT (a)). The CTO writes
  no settings.
- **What it does:** adds 18 allow rules to `.claude/settings.local.json`'s `permissions.allow`; removes nothing; leaves
  the deny and ask lists and every other key exactly as they are; keeps a backup beside the file.
- **The rules** (in `ACT-PERMISSIONS-1/apply.py`):
  - read-only commands: `ls`, `grep`, `head`, `tail`, `wc`, `cat`, `stat`, `diff`, `ps`, `date`, `du`, `tmux ls`,
    `crontab -l`, `/usr/lib/wsl/lib/nvidia-smi --query-gpu=…`;
  - the pinned gov by its path: `~/.local/bin/gov …` and `/home/usain/.local/bin/gov …` (what `gov …` already allows);
  - `cd` into the repository and the worktrees.
- **Still asking** (no rule added): `rm`, `mv`, `cp`, `mkdir` outside the repository; writes to `~/gov-os-eval`,
  `~/.local`, `~/.cache`, `~/.config`, `~/.ollama`; `setsid`, `timeout` and other job launches; `curl`; web access;
  every git command not already allowed today, `git -C` forms included (`git push` stays denied).

## The commands (one terminal, about 1 minute)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
P=governance/project/orchestration/packages/ACT-PERMISSIONS-1
python3 $P/apply.py .claude/settings.local.json --check     # expect: 0 of 18 present (exit 1)
python3 $P/apply.py .claude/settings.local.json             # expect: applied: 18 rule(s) added
python3 $P/apply.py .claude/settings.local.json --check     # expect: 18 of 18 present (exit 0); deny ['Bash(git push *)']; ask []
```
The CTO's session reads the new rules from its next start (or `/permissions` shows them at once).

## Undo
```
python3 $P/apply.py .claude/settings.local.json --undo      # restores the backup settings.local.json.pre-act-permissions-1
```

## The rehearsal (DEC-1057)
`.gov-runtime/scratch/orchestrator/drafts/act-permissions-1/rehearse.py`: the steps above on a copy of the real file
(only the path substituted), the real file hashed before and after. **REHEARSAL PASS, 16 of 16** (the revised ACT,
2026-11-06): check before (0 of 18, exit 1); apply (18 added); check after (18 of 18); apply again (0 added); deny
unchanged; ask unchanged; every old allow rule kept in order; only the ACT's 18 added; `git push` still denied; no
`git -C` rule at all; no new git rule of any kind; no `rm`, `mv`, `cp`, `mkdir`, `curl`, `setsid` or `timeout`
allowed; the other keys unchanged; undo; the copy equal to the original byte for byte; the real file unchanged
throughout (sha256 `767872e029c7`). An earlier run of the first version found one fault in the rehearsal's own check,
fixed then; the `git -C` rules it concerned are now dropped (DEC-1081 (1)), and with them the wildcard overlap.

**Basis:** question 4 (the owner's time spent only on prompts that carry a decision) and question 2 (every write outside
the repository, deletion, job and network call still asks).
