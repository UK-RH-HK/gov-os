#!/usr/bin/env python3
"""ACT-PERMISSIONS-1 (P-PERMISSIONS-1, DEC-1080, DEC-1081 (1)): add the approved allow rules to a settings file.

    python3 apply.py <settings.local.json>           add the rules (a backup beside it first)
    python3 apply.py <settings.local.json> --check   print what is present and missing; change nothing
    python3 apply.py <settings.local.json> --undo    restore the backup this script made

Only `permissions.allow` gains entries; nothing is removed, and the deny and ask lists are left exactly as they are.
Running it twice changes nothing the second time. Exit 0 on success; 1 on a failed check; 2 on a usage or file error.
"""
import json
import shutil
import sys
from pathlib import Path

RULES = [
    # read-only commands (the guard still refuses secrets, the held-out material and the hidden halves)
    "Bash(ls *)", "Bash(grep *)", "Bash(head *)", "Bash(tail *)", "Bash(wc *)", "Bash(cat *)", "Bash(stat *)",
    "Bash(diff *)", "Bash(ps *)", "Bash(date *)", "Bash(du *)", "Bash(tmux ls)", "Bash(crontab -l)",
    "Bash(/usr/lib/wsl/lib/nvidia-smi --query-gpu=*)",
    # the pinned gov, by its path (the same command `gov *` already allows)
    "Bash(~/.local/bin/gov *)", "Bash(/home/usain/.local/bin/gov *)",
    # no git -C rules (DEC-1081 (1)): the CTO uses plain git; every git command not already allowed keeps asking
    # cd into the repository and the worktrees
    "Bash(cd /home/usain/Dynamic-Agentic-Engineering-OS*)", "Bash(cd ~/gov-os-worktrees/*)",
]
BACKUP_SUFFIX = ".pre-act-permissions-1"


def main(argv):
    if len(argv) < 2 or (len(argv) == 3 and argv[2] not in ("--check", "--undo")) or len(argv) > 3:
        print(__doc__, file=sys.stderr)
        return 2
    path = Path(argv[1])
    mode = argv[2] if len(argv) == 3 else "apply"
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if mode == "--undo":
        if not backup.is_file():
            print(f"undo: no backup {backup}", file=sys.stderr)
            return 2
        shutil.copy2(backup, path)
        print(f"undo: {path} restored from {backup.name}")
        return 0
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        print(f"cannot read {path}: {error}", file=sys.stderr)
        return 2
    perms = data.setdefault("permissions", {})
    allow = perms.setdefault("allow", [])
    missing = [r for r in RULES if r not in allow]
    if mode == "--check":
        print(f"check: {len(RULES) - len(missing)} of {len(RULES)} present; missing: {missing or 'none'}")
        print(f"check: deny {perms.get('deny', [])}; ask {perms.get('ask', [])}")
        return 0 if not missing else 1
    if not backup.exists():
        shutil.copy2(path, backup)
    before_deny, before_ask = list(perms.get("deny", [])), list(perms.get("ask", []))
    allow.extend(missing)
    text = json.dumps(data, indent=2) + "\n"
    json.loads(text)
    path.write_text(text)
    after = json.loads(path.read_text())["permissions"]
    if after.get("deny", []) != before_deny or after.get("ask", []) != before_ask:
        shutil.copy2(backup, path)
        print("STOP: deny or ask changed; restored from the backup", file=sys.stderr)
        return 1
    print(f"applied: {len(missing)} rule(s) added, {len(RULES) - len(missing)} already present; backup {backup.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
