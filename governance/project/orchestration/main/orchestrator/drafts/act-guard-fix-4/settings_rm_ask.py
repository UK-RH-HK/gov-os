"""ACT-GUARD-FIX-4 (DEC-1050 (8)): stop asking for rm. Removes exactly the three entries of the user settings' "ask"
list that make Claude Code ask before any rm: "Bash(rm -r:*)", "Bash(rm -rf:*)", "Bash(rm:*)" (lines 16-18 of
~/.claude/settings.json on 2026-11-03). Nothing else changes: the owner-ping asks stay; the catastrophic deletes are
refused by the five-rule hook instead.
  python3 settings_rm_ask.py check  [file]   prints what would change; exit 1 if the file is not as expected
  python3 settings_rm_ask.py apply  [file]   backs the file up to <file>.pre-act-guard-fix-4, then removes the three
  python3 settings_rm_ask.py undo   [file]   puts the backup back
The file defaults to ~/.claude/settings.json."""
import json
import os
import shutil
import sys

RM_ASKS = ["Bash(rm -r:*)", "Bash(rm -rf:*)", "Bash(rm:*)"]


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "check"
    path = os.path.expanduser(sys.argv[2] if len(sys.argv) > 2 else "~/.claude/settings.json")
    backup = path + ".pre-act-guard-fix-4"
    if what == "undo":
        if not os.path.exists(backup):
            sys.exit(f"no backup at {backup}")
        shutil.copy2(backup, path)
        print(f"restored {path} from {backup}")
        return
    text = open(path).read()
    data = json.loads(text)
    ask = (data.get("permissions") or {}).get("ask")
    if not isinstance(ask, list):
        sys.exit(f"{path}: no permissions.ask list; nothing to do")
    present = [a for a in RM_ASKS if a in ask]
    others = [a for a in ask if a not in RM_ASKS]
    print(f"{path}: ask has {len(ask)} entries; the rm asks present: {present}; kept: {others}")
    if not present:
        print("already applied")
        return
    lines = [i + 1 for i, line in enumerate(text.splitlines()) if line.strip().rstrip(",") in
             {json.dumps(a) for a in RM_ASKS}]
    print(f"the lines removed: {lines}")
    if what != "apply":
        return
    if os.path.exists(backup):
        sys.exit(f"a backup is already at {backup}: undo first, or move it away")
    shutil.copy2(path, backup)
    data["permissions"]["ask"] = others
    with open(path, "w") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    json.load(open(path))  # still valid JSON
    print(f"applied; backup at {backup}")


if __name__ == "__main__":
    main()
