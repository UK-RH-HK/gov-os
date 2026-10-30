"""Stop a process and every process under it, by process id (never by a name pattern, which can match the caller).
    python3 stop_tree.py <pid>
Sends SIGTERM to the leaves first, then the root; prints what it stopped."""
import os
import signal
import sys
import time

root = int(sys.argv[1])
children = {}
for pid in os.listdir("/proc"):
    if not pid.isdigit():
        continue
    try:
        ppid = int(open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()[1])
    except (OSError, IndexError, ValueError):
        continue
    children.setdefault(ppid, []).append(int(pid))
order = []


def walk(p):
    for c in children.get(p, []):
        walk(c)
    order.append(p)


walk(root)
for p in order:
    try:
        os.kill(p, signal.SIGTERM)
    except ProcessLookupError:
        pass
time.sleep(3)
left = [p for p in order if os.path.exists(f"/proc/{p}")]
for p in left:
    try:
        os.kill(p, signal.SIGKILL)
    except ProcessLookupError:
        pass
print("stopped", len(order), "processes; killed after the grace period:", len(left))
