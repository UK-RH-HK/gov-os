"""Name each `flock /tmp/gov-os-verify.lock` waiter or holder: a holder has a running child (pytest)."""

import subprocess

out = subprocess.run(["ps", "-eo", "pid,ppid,etime,args"], capture_output=True, text=True).stdout.splitlines()[1:]
rows = []
for line in out:
    parts = line.split(None, 3)
    if len(parts) == 4:
        rows.append(parts)
children = {}
for pid, ppid, etime, args in rows:
    children.setdefault(ppid, []).append(args)
for pid, ppid, etime, args in rows:
    if args.startswith("flock ") and "/tmp/gov-os-verify.lock" in args:
        tag = "?"
        for word in args.split():
            if word.startswith("--junitxml="):
                tag = word.split("/gov-os-worktrees/")[-1].split("/")[0] + ":" + word.rsplit("/", 1)[-1]
        state = "HOLDS" if pid in children else "waits"
        print(state, etime, tag)
