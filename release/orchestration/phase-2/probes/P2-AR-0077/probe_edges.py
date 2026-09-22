#!/usr/bin/env python3
"""P2-AR-0077: `resolves_outside_project` edge cases the brief names, plus the
remaining negative controls.

Edges: empty token, separators only, `.`/`..` spellings, `~`, `$HOME`, an
extremely long path, a HARD link (which no amount of symlink resolution can see),
and a directory whose contents cannot be traversed.
"""
import json, os, pathlib, subprocess
from harness4 import (fresh, bind, descriptor, install, verdict, save, marker_for,
                      OUTSIDE, gate_records, Proj)

rows = []
p = fresh("edges")
p.write("payload.txt", "P2-AR-0077 payload\n")
n = 0


def classify(name, argv, note="", marker=None, execute=False):
    global n
    n += 1
    tool = f"TOOL-E-{n:02d}"
    d = descriptor(None, install_cmd=argv, tool_id=tool)
    d.pop("security_review_record", None)
    if execute:
        bind(p, d)
    e = install(p, d, f"e-{name}", execute=execute)
    r = e.get("result") or (e.get("error") or {}).get("details") or {}
    env = ((r.get("change_class") or {}).get("authority_envelope")) or {}
    row = {"shape": name, "argv": argv, "note": note,
           "expands_authority": env.get("expands_authority"),
           "triggers": env.get("triggers_fired"),
           "undetermined": env.get("undetermined"),
           "branch": (r.get("change_class") or {}).get("branch"),
           "installed": (e.get("result") or {}).get("installed"),
           "error_code": (e.get("error") or {}).get("code")}
    if marker:
        row["MARKER_OUTSIDE_PROJECT"] = marker.exists()
        row["marker_content"] = marker.read_text()[:60] if marker.exists() else None
    rows.append(row)
    print(f"{name:26s} expands={row['expands_authority']} trig={row['triggers']} "
          f"undet={len(row['undetermined'] or [])} branch={row['branch']} "
          f"MARKER={row.get('MARKER_OUTSIDE_PROJECT')}")
    return row


classify("empty-token", ["cp", "payload.txt", ""], note="an empty candidate")
classify("slashes-only", ["cp", "payload.txt", "///"], note="separators only (absolute => lexical)")
classify("dot", ["cp", "payload.txt", "."], note="the current directory")
classify("dotdot", ["cp", "payload.txt", ".."], note="the parent -- lexical escape")
classify("tilde", ["cp", "payload.txt", "~"], note="home-relative")
classify("tilde-slash", ["cp", "payload.txt", "~/x"], note="home-relative with a path")
classify("dollar-HOME", ["cp", "payload.txt", "$HOME/x"],
         note="env-var spelling: the exec is argv-based (no shell), so this stays literal")
classify("dollar-brace-HOME", ["cp", "payload.txt", "${HOME}/x"], note="brace form")
classify("very-long", ["cp", "payload.txt", "a" * 5000], note="ENAMETOOLONG territory")
classify("long-segments", ["cp", "payload.txt", "/".join(["seg"] * 400)], note="many segments")
classify("dot-segments", ["cp", "payload.txt", "./././x"], note="redundant . segments")
classify("trailing-slash", ["cp", "payload.txt", "subdir/"], note="trailing separator")
classify("embedded-dotdot-nonsegment", ["cp", "payload.txt", "x..y"],
         note="'..' inside a segment, not a segment")

# ---- HARD LINK: nothing about symlink resolution can see this --------------
hard_target = OUTSIDE / "edges-hardlink-target.txt"
hard_target.write_text("ORIGINAL OUTSIDE CONTENT\n")
hl = p.root / "hardlinked"
if hl.exists():
    hl.unlink()
os.link(str(hard_target), str(hl))
print(f"[setup] hard link {hl} -> {hard_target} (nlink="
      f"{os.stat(hard_target).st_nlink})")
classify("hardlink-destination", ["cp", "payload.txt", "hardlinked"],
         note="MINE: the destination is a HARD link to a file outside the root; "
              "canonicalisation cannot see it -- there is no link to resolve",
         marker=hard_target, execute=True)
rows[-1]["outside_file_content_after"] = hard_target.read_text()
rows[-1]["OUTSIDE_FILE_MODIFIED"] = hard_target.read_text() != "ORIGINAL OUTSIDE CONTENT\n"
print(f"   outside file after: {hard_target.read_text()!r} "
      f"MODIFIED={rows[-1]['OUTSIDE_FILE_MODIFIED']}")

# ---- NEGATIVE CONTROL: gov init on a brownfield repository -----------------
b = Proj("edges-brownfield", fixture="brownfield")
init = b.run(["init", "--name", "edges-brownfield", "--alias", "a-ebf"])
ir = init.get("result") or {}
b.commit_all("after init")
pol = b.run(["policy", "overrides"])
refused = ((pol.get("result") or {}).get("refused")) or []
nc = {"shape": "NC-brownfield-init", "init_ok": init.get("ok"),
      "init_error": (init.get("error") or {}).get("code"),
      "path_rules": len((ir.get("contract") or {}).get("paths") or []) or ir.get("path_rules"),
      "refused_count": len(refused),
      "refused": refused[:3],
      "note": "OD-P2-03 requirement 6: gov init on a brownfield repo succeeds and refuses nothing"}
rows.append(nc)
print(f"NC-brownfield-init ok={nc['init_ok']} refused={nc['refused_count']}")

# ---- NEGATIVE CONTROL: product/legal/** authoritative over product/** source
q = fresh("edges-legal")
c = q.root / "governance/project/REPOSITORY_CONTRACT.yaml"
lines = c.read_text().split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("paths:"))
end = next((i for i in range(start + 1, len(lines))
            if lines[i] and not lines[i][0].isspace() and not lines[i].startswith("-")), len(lines))
rule = ['- pattern: "product/legal/**"', "  class: authoritative",
        "  sensitivity: restricted", "  owner_role: backend-engineer"]
c.write_text("\n".join(lines[:end] + rule + lines[end:]))
q.commit_all("legal rule")
pol = q.run(["policy", "overrides"])
refused = ((pol.get("result") or {}).get("refused")) or []
mine = [x for x in refused if isinstance(x.get("value"), dict)
        and x["value"].get("pattern") == "product/legal/**"]
doc = q.run(["doctor"])
nc2 = {"shape": "NC-product-legal-authoritative", "refused": bool(mine),
       "refused_reason": (mine[0].get("reason") if mine else None),
       "refused_total": len(refused), "doctor_ok": doc.get("ok"),
       "note": "the sensitivity_classes_and_namespaces_are_enforced shape must still be honoured"}
rows.append(nc2)
print(f"NC-product-legal refused={nc2['refused']} doctor_ok={nc2['doctor_ok']}")

save("edges", rows)
