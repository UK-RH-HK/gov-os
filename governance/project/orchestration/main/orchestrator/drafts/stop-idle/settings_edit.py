"""ACT-STOP-IDLE-1's one settings change: a second Stop entry in .claude/settings.local.json for the idle check.

    python3 -I settings_edit.py expect <settings> <repo>   # the sha256 `add` would write; writes nothing
    python3 -I settings_edit.py add    <settings> <repo>   # adds the entry (once), atomically; prints the new sha256
    python3 -I settings_edit.py remove <settings>          # removes only that entry; prints the new sha256
    python3 -I settings_edit.py verify <before> <after>    # exit 0 only if the files differ by that one entry

The entry runs the hook through a guard: a missing file is a named non-blocking error (exit 1), never Python's
exit 2, which Claude Code would read as a block on every turn. Everything else in the file is kept as it is
(json.dumps(indent=2), as the file is written today). Standard library only.
"""
import copy
import hashlib
import json
import os
import sys

MARK = "stop_idle_check.py"


def entry(repo):
    f = f"{repo}/governance/project/orchestration/tools/stop_idle_check.py"
    cmd = (f'f={f}; [ -f "$f" ] || {{ echo "stop idle check: $f is missing, so the idle check did not run '
           f'(DEC-1110)" >&2; exit 1; }}; exec python3 -E "$f"')
    return {"matcher": "*", "hooks": [{"type": "command", "command": cmd, "timeout": 10}]}


def ours(e):
    return MARK in json.dumps(e)


def dump(d):
    return (json.dumps(d, indent=2) + "\n").encode()


def added(data, repo):
    d = json.loads(data)
    stop = d.setdefault("hooks", {}).setdefault("Stop", [])
    if not any(ours(e) for e in stop):
        stop.append(entry(repo))
    return dump(d)


def write(path, data):
    tmp = path + ".stop-idle.tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.chmod(tmp, os.stat(path).st_mode & 0o7777)
    os.replace(tmp, path)


def without_ours(d):
    d = copy.deepcopy(d)
    stop = d.get("hooks", {}).get("Stop", [])
    d.get("hooks", {})["Stop"] = [e for e in stop if not ours(e)]
    if not d["hooks"]["Stop"]:
        del d["hooks"]["Stop"]
    return d


def main(argv):
    op = argv[1]
    if op == "verify":
        before, after = (json.load(open(p)) for p in argv[2:4])
        theirs = [e for e in after.get("hooks", {}).get("Stop", []) if ours(e)]
        if len(theirs) != 1 or without_ours(after) != without_ours(before) or any(
                ours(e) for e in before.get("hooks", {}).get("Stop", [])):
            print("verify: the files differ by more than the idle check's one Stop entry")
            return 1
        print("verify: only the idle check's Stop entry was added; env, permissions, PermissionRequest and the "
              "inbox waiter's Stop entry unchanged")
        return 0
    path = argv[2]
    data = open(path, "rb").read()
    if op == "expect":
        new = added(data, argv[3])
    elif op == "add":
        new = added(data, argv[3])
        if new != data:
            write(path, new)
    elif op == "remove":
        new = dump(without_ours(json.loads(data)))
        if new != data:
            write(path, new)
    else:
        print(f"unknown operation {op}")
        return 2
    print(hashlib.sha256(new).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
