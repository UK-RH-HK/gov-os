"""W3-P09's design guard (owner, 2026-10-29): W2-60b reads the launcher's set of launchable roles from the kernel's
role files instead of the fixed tuples in launcher.py, so a new role is a file, not a code change; and the parking list
gains W3-P10 (W2-04's context packet scoped to a set of tickets or a stream is not a small addition). Safe to re-run."""
import pathlib
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
T = ROOT / ".tickets/DAEO-ecac.md"
t = T.read_text(encoding="utf-8")
if "a new role is a file, not a code change" not in t:
    old = "  failure:\n  - A value the log does not hold reported as measured;"
    new = ("  - 'The launcher''s set of launchable roles (today the fixed WORKER_ROLES and OWN_TICKET_ROLES tuples in "
           "launcher.py) is read from the kernel''s role files, so a new role is a file, not a code change; a role file "
           "that is missing or unreadable refuses the launch; the five roles launch exactly as before [DEC-946 (W3-P09), "
           "DEC-826 Q1]'\n"
           "  - 'A role named in a ticket but with no role file is refused at launch, naming the role [DEC-946 (W3-P09)]'\n"
           "  failure:\n  - A fixed list of launchable roles left in code.\n  - A value the log does not hold reported as measured;")
    if t.count(old) != 1:
        sys.exit("W2-60b: anchor not found once")
    t = t.replace(old, new)
    if "- DEC-946\n" not in t:
        t = t.replace("sources:\n", "sources:\n- DEC-946\n", 1)
    T.write_text(t, encoding="utf-8")
    print("W2-60b: roles read from the role files")
P = ROOT / "docs/plan/WAVE_3_PARKING.md"
p = P.read_text(encoding="utf-8")
if "W3-P10" not in p:
    row = ("| W3-P10 | W2-04's context packet scoped to a set of tickets or a stream (for W3-P09's stream orchestrators): "
           "`gov context` builds one ticket's packet under a 6k-token ceiling that never drops the ticket's own text, so a "
           "set or stream packet needs its own ceiling and query rules; not a small addition to W2-04 | the owner's "
           "W3-P09 check | 2026-10-29 |\n")
    anchor = "\n\nNot parked:"
    if p.count(anchor) != 1:
        sys.exit("parking list: anchor not found once")
    p = p.replace(anchor, "\n" + row.rstrip("\n") + anchor)
    P.write_text(p, encoding="utf-8")
    print("W3-P10 parked")
