"""ACT 1: compare two .claude/settings.json files by structure only, never printing a rule's or a command's text.
    python3 act1_settings_diff.py <old settings.json> <new settings.json>"""
import json
import sys

old, new = (json.load(open(p)) for p in sys.argv[1:3])
for key in sorted(set(old) | set(new)):
    if key == "hooks":
        continue
    print(f"{key}: {'same' if old.get(key) == new.get(key) else 'CHANGED'}")
oh, nh = old.get("hooks", {}), new.get("hooks", {})
for event in sorted(set(oh) | set(nh)):
    if event not in nh:
        print(f"hooks.{event}: removed")
    elif event not in oh:
        print(f"hooks.{event}: added")
    elif oh[event] == nh[event]:
        print(f"hooks.{event}: same")
    else:
        texts = json.dumps(nh[event])
        print(f"hooks.{event}: CHANGED; runs .claude/hooks/pretooluse.py: {'.claude/hooks/pretooluse.py' in texts}; "
              f"still names the kernel guard: {'kernel/hooks/pretooluse.py' in texts}")
