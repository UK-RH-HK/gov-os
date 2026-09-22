#!/usr/bin/env python3
"""P2-AR-0077 / AR75-F1 continued: bound the `file://` and embedded-path escapes.

(a) which URL spellings escape and which are caught;
(b) whether the SAME escape works from health_check.command, i.e. whether it
    re-fires on every later `gov tools health` (the lifetime re-verification path
    the repair also wired);
(c) a CLEAN negative control: one fresh project, one conforming install, and a
    count of the Human Decision Gates that exist afterwards (must be zero).
"""
import json, os, pathlib
from harness4 import (fresh, bind, descriptor, install, verdict, save, marker_for,
                      OUTSIDE, gate_records)

rows = []


def run_in(p, name, n, *, install_cmd=None, health_cmd=None, marker=None, health=False,
           note=""):
    tool = f"TOOL-F1B-{n:02d}"
    d = descriptor(None, install_cmd=install_cmd, health_cmd=health_cmd, tool_id=tool)
    d.pop("security_review_record", None)
    bind(p, d)
    e = install(p, d, f"f1b-{name}")
    v = verdict(e, p, marker, tool_id=tool)
    v.update({"shape": name, "argv_install": install_cmd, "argv_health": health_cmd,
              "note": note})
    if health:
        h = p.run(["tools", "health"], session="S-adv", role="tooling-engineer")
        v["health_ok"] = h.get("ok")
        v["health_detail"] = json.dumps(h.get("result") or h.get("error"))[:1200]
        v["MARKER_AFTER_HEALTH"] = marker.exists() if marker else None
        h2 = p.run(["tools", "health"], session="S-adv", role="tooling-engineer")
        v["health2_ok"] = h2.get("ok")
        v["MARKER_AFTER_HEALTH_2"] = marker.exists() if marker else None
    rows.append(v)
    print(f"{name:30s} ok={v['ok']} branch={v['branch']} exp={v['expands_authority']} "
          f"trig={v['triggers_fired']} undet={len(v['undetermined'] or [])} "
          f"MARKER={v['MARKER_OUTSIDE_PROJECT']} health={v.get('MARKER_AFTER_HEALTH')}/"
          f"{v.get('MARKER_AFTER_HEALTH_2')}")
    return v


# =========================================================================
# (a) URL spelling variants
# =========================================================================
p = fresh("f1b")
p.write("payload.txt", "P2-AR-0077 payload\n")
n = 0
cases = [
    ("U1-file-triple-slash", lambda m: ["curl", "-s", "-T", "payload.txt", f"file://{m}"],
     "empty authority, absolute path in the URL path"),
    ("U2-file-localhost", lambda m: ["curl", "-s", "-T", "payload.txt", f"file://localhost{m}"],
     "authority 'localhost' -- endpoint_host() sees a host"),
    ("U3-FILE-upper", lambda m: ["curl", "-s", "-T", "payload.txt", f"FILE://{m}"],
     "uppercase scheme"),
    ("U4-file-dotdot", lambda m: ["curl", "-s", "-T", "payload.txt",
                                  f"file://{p.root}/../outside/{m.name}"],
     "lexical .. inside the URL -- leaves_project should catch this one"),
    ("U5-writeout-relative", lambda m: ["curl", "-s", "-o", "o.txt",
                                        "-w", "%%output{../outside/%s}X\n" % m.name,
                                        f"file://{p.root}/payload.txt"],
     "write-out with a RELATIVE ..-escape embedded in the token"),
]
for name, mk, note in cases:
    n += 1
    m = marker_for(f"f1b-{name}")
    run_in(p, name, n, install_cmd=mk(m), marker=m, note=note)

# =========================================================================
# (b) the same escape from health_check.command (lifetime re-verification)
# =========================================================================
n += 1
mh = marker_for("f1b-H1")
run_in(p, "H1-file-url-health", n, install_cmd=["true"],
       health_cmd=["curl", "-s", "-T", "payload.txt", f"file://{mh}"],
       marker=mh, health=True,
       note="does the escape re-fire on every later `gov tools health`?")

# =========================================================================
# (c) CLEAN negative control -- its own project, nothing else run in it
# =========================================================================
q = fresh("f1bnc")
gates_before = gate_records(q)
d = descriptor(None, install_cmd=["true"], tool_id="TOOL-NC")
d.pop("security_review_record", None)
bind(q, d)
e = install(q, d, "nc-clean")
v = verdict(e, q, None, tool_id="TOOL-NC")
v["shape"] = "NC-CLEAN-conforming-only"
v["gates_before"] = gates_before
v["note"] = "OD-P2-03 requirement 6: a conforming install proceeds with ZERO gate records"
rows.append(v)
print(f"NC-CLEAN ok={v['ok']} branch={v['branch']} installed={v['installed']} "
      f"gates_before={gates_before} gates_after={v['gate_records']}")

# a second, ordinary-network conforming install in the same clean project
d2 = descriptor(None, install_cmd=["curl", "-sS", "https://pypi.org/simple/"], tool_id="TOOL-NC2")
d2.pop("security_review_record", None)
bind(q, d2)
e2 = install(q, d2, "nc-clean-net")
v2 = verdict(e2, q, None, tool_id="TOOL-NC2")
v2["shape"] = "NC-CLEAN-allowlisted-network"
rows.append(v2)
print(f"NC-CLEAN-net ok={v2['ok']} branch={v2['branch']} installed={v2['installed']} "
      f"gates_after={v2['gate_records']}")

save("f1b", {"rows": rows, "outside_dir": str(OUTSIDE)})
