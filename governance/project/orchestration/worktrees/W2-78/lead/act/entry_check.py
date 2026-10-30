"""Entry-for-entry check of the move (W2-78), and of the two ACT versions of the path map.

1. Each record file at HEAD against the path map's list at the base (merge-base HEAD w2/integrate): same entries,
   same order, every field and value.
2. While HEAD's path map still holds a key: it is the exact copy of its record file.
3. ACT-1 parsed equals the base parsed, but for the one namespace pattern added.
4. ACT-2 parsed equals ACT-1 parsed without the four keys, and nothing else.
Usage (from the worktree): python3 entry_check.py
"""
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path("/home/usain/gov-os-worktrees/W2-78")
ACT = ROOT / ".gov-runtime/scratch/lead/act"
FILES = {"load_sensitive": "load-sensitive.yaml", "accepted_reds": "accepted-reds.yaml",
         "accepted_history": "accepted-history.yaml", "acceptance_exemptions": "acceptance-exemptions.yaml"}


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


base = git("merge-base", "HEAD", "w2/integrate").strip()
head = git("rev-parse", "HEAD").strip()
print(f"base {base[:12]} head {head[:12]}")
base_map = yaml.safe_load(git("show", f"{base}:governance/project/path-map.yaml"))
head_map = yaml.safe_load(git("show", "HEAD:governance/project/path-map.yaml"))
bad = 0
for key, name in FILES.items():
    rel = f"governance/project/records/{name}"
    try:
        record = yaml.safe_load(git("show", f"HEAD:{rel}"))
    except subprocess.CalledProcessError:
        print(f"FAIL {rel}: not committed at HEAD")
        bad += 1
        continue
    want = base_map.get(key)
    got = record.get(key) if isinstance(record, dict) else None
    extra = sorted(set(record) - {key, "version"}) if isinstance(record, dict) else ["not a mapping"]
    same = got == want and [list(e) for e in got or [] if isinstance(e, dict)] == \
        [list(e) for e in want or [] if isinstance(e, dict)]  # field order too
    print(f"{'OK  ' if same and not extra else 'FAIL'} {rel}: {len(got or [])} entries, base {len(want or [])}; "
          f"version {record.get('version') if isinstance(record, dict) else None}; other keys {extra or 'none'}")
    if not same:
        for i, (a, b) in enumerate(zip(got or [], want or [])):
            if a != b:
                print(f"     first difference at entry {i}: {a!r} != {b!r}")
                break
    bad += 0 if same and not extra else 1
    if key in head_map:
        copy = head_map[key] == got
        print(f"{'OK  ' if copy else 'FAIL'} HEAD's path map {key}: {'exact copy' if copy else 'DIFFERS'}")
        bad += 0 if copy else 1

act1 = yaml.safe_load((ACT / "path-map.act1.yaml").read_text(encoding="utf-8"))
act2 = yaml.safe_load((ACT / "path-map.act2.yaml").read_text(encoding="utf-8"))
expect1 = yaml.safe_load(git("show", f"{base}:governance/project/path-map.yaml"))
paths = expect1["namespaces"]["project-overlay"]["paths"]
paths.insert(paths.index("governance/project/prompts/**") + 1, "governance/project/records/**")
ok1 = act1 == expect1
print(f"{'OK  ' if ok1 else 'FAIL'} ACT-1 = base + the namespace pattern governance/project/records/**")
expect2 = {k: v for k, v in act1.items() if k not in FILES}
ok2 = act2 == expect2 and not set(FILES) & set(act2)
print(f"{'OK  ' if ok2 else 'FAIL'} ACT-2 = ACT-1 without the four lists, nothing else "
      f"(keys removed: {sorted(set(act1) - set(act2))})")
bad += (not ok1) + (not ok2)
print("RESULT", "PASS" if not bad else f"FAIL ({bad})")
sys.exit(1 if bad else 0)
