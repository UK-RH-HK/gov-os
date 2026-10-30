"""DEC-945: removes the Pushover emergency push from the nightly's draft copy (drafts/nightly-next3): nightly.sh's call,
the test stub and cases (N7's push check, P1-P6), and the README's lines. push_emergency.sh is already removed there."""
import pathlib
import re
import sys

N = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/nightly-next3")


def edit(name, pairs):
    p = N / name
    t = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if t.count(old) != 1:
            sys.exit(name + ": not found once: " + old[:60])
        t = t.replace(old, new)
    p.write_text(t, encoding="utf-8")


edit("nightly.sh", [
    ("# Below the floor is an emergency (DEC-938 item 6): at night it is pushed at once (DEC-939 item 7).\n",
     "# Below the floor is an emergency (DEC-938 item 6): it goes first in the 07:30 morning package, from the\n"
     "# orchestrator's own session (DEC-945: no push service).\n"),
    ('  [ "$MODE" = night ] && "$HERE/push_emergency.sh" "Gov OS emergency: the disk is below its floor; the nightly did '
     'not start"\n', ""),
])
t = (N / "test_nightly.sh").read_text(encoding="utf-8")
lines = t.split("\n")
out, skip = [], False
for line in lines:
    if line.startswith("# a fake emergency push in the copy's folder") or "push_emergency.sh\"; chmod +x" in line:
        continue
    if "pushes.txt" in line and ("fail \"N7: the disk gate shut at night pushed" in line or line.startswith("rm -f \"$work/pushes.txt\"")):
        continue
    if line.startswith("# ---- push_emergency.sh"):
        skip = True
        continue
    if skip and line.startswith("# ---- "):
        skip = False
    if skip:
        continue
    out.append(line)
t = "\n".join(out)
t2 = t.replace("ping_gate.sh G1-G6, push_emergency.sh P1-P6, ", "ping_gate.sh G1-G6, ")
if t2 == t or "push_emergency" in t2 or "pushes.txt" in t2:
    sys.exit("test_nightly.sh: a push reference is left, or the PASS line was not found")
(N / "test_nightly.sh").write_text(t2, encoding="utf-8")
r = (N / "README.md").read_text(encoding="utf-8")
r = "\n".join(l for l in r.split("\n") if "push_emergency.sh" not in l)
r = r.replace(" An estimate over the window pings P2 and goes on; the disk gate shut at night pushes an emergency.",
              " An estimate over the window pings P2 and goes on; the disk gate shut at night stops it, for the morning "
              "package (DEC-945).")
r = re.sub(r"Four mutation checks:", "Two mutation checks:", r)
r = re.sub(r"passes 36 of 36 \(2026-10-29\)", "passes all its cases (2026-10-29, after DEC-945)", r)
if "push" in r.lower().replace("pushes", ""):
    print("README: check remaining 'push' words")
(N / "README.md").write_text(r, encoding="utf-8")
print("Pushover removed from the draft copy")
