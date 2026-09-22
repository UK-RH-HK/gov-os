#!/usr/bin/env python3
"""P2-AR-0077 differential control: the SAME shapes against the parent commit
`c34c439` (the code the repair was applied to), built from `git archive` into its
own tree.

Two questions this answers, and nothing else can:
  1. Were AR75-F1's and AR75-F2's witnesses actually LIVE at c34c439? If not, my
     "they are dead at e25ca70" proves nothing.
  2. Are my new escapes (E1 `file://`, E2 `%output{}`) REGRESSIONS introduced by
     this repair, or pre-existing holes the repair did not reach?
"""
import json, os, pathlib, shutil, subprocess, sys, time

import harness4 as H

BASE = pathlib.Path("/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/"
                    "1b6c780e-2b37-439f-a969-a8d96b7ad35e/scratchpad/p2ar0077/base")
WHICH = sys.argv[1] if len(sys.argv) > 1 else "base"
if WHICH == "base":
    H.GOV = BASE / "target/release/gov"
    H.WT = BASE                      # fixtures + GOV_CANONICAL_ROOT come from the base tree
print(f"[{WHICH}] gov = {H.GOV}")

rows = []


def shape(p, name, n, *, install_cmd=None, marker=None, setup=None, note=""):
    tool = f"TOOL-D-{n:02d}"
    if marker is None:
        marker = H.marker_for(f"{WHICH}-{name}")
    if setup:
        setup(marker)
    d = H.descriptor(None, install_cmd=install_cmd, tool_id=tool)
    d.pop("security_review_record", None)
    H.bind(p, d)
    e = H.install(p, d, f"d-{name}")
    v = H.verdict(e, p, marker, tool_id=tool)
    v.update({"shape": name, "argv": install_cmd, "note": note, "build": WHICH})
    rows.append(v)
    print(f"[{WHICH}] {name:24s} ok={v['ok']} branch={v['branch']} exp={v['expands_authority']} "
          f"trig={v['triggers_fired']} undet={len(v['undetermined'] or [])} MARKER={v['MARKER_OUTSIDE_PROJECT']}")
    return v


p = H.fresh(f"diff-{WHICH}")
p.write("payload.txt", "P2-AR-0077 payload\n")


def link_to(rel, target):
    lp = p.root / rel
    if lp.is_symlink():
        lp.unlink()
    os.symlink(str(target), str(lp))


n = 0
n += 1
shape(p, "W1-cp-symlink", n, install_cmd=["cp", "payload.txt", "escape-link"],
      setup=lambda m: link_to("escape-link", m),
      note="AR75-F1 witness 1: cp through a bare-word in-project symlink")
n += 1


def mk_cfg(m):
    p.write("curlcfg", f'-o "{m}"\nurl = "file://{p.root}/payload.txt"\n')


shape(p, "W4-curl-K", n, install_cmd=["curl", "-K", "curlcfg"], setup=mk_cfg,
      note="AR75-F1 witness 2: curl -K reads its command line from a project file")
n += 1
m1 = H.marker_for(f"{WHICH}-E1")
shape(p, "E1-curl-T-file-url", n, marker=m1,
      install_cmd=["curl", "-s", "-T", "payload.txt", f"file://{m1}"],
      note="P2-AR-0077 E1: is this a regression, or pre-existing?")
n += 1
m2 = H.marker_for(f"{WHICH}-E2")
shape(p, "E2-curl-writeout", n, marker=m2,
      install_cmd=["curl", "-s", "-o", "o.txt", "-w", "%%output{%s}X\n" % m2,
                   f"file://{p.root}/payload.txt"],
      note="P2-AR-0077 E2: is this a regression, or pre-existing?")
n += 1
shape(p, "NC1-conforming", n, install_cmd=["true"], note="negative control")

# --- AR75-F2's witness, and my class:evidence variant, on this build ---------
def path_rule_case(tag, rule_yaml):
    q = H.fresh(f"diff-{WHICH}-{tag}")
    c = q.root / "governance/project/REPOSITORY_CONTRACT.yaml"
    lines = c.read_text().split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("paths:"))
    end = next((i for i in range(start + 1, len(lines))
                if lines[i] and not lines[i][0].isspace() and not lines[i].startswith("-")),
               len(lines))
    c.write_text("\n".join(lines[:end] + rule_yaml.rstrip("\n").split("\n") + lines[end:]))
    q.commit_all("append a path rule by hand")
    pol = q.run(["policy", "overrides"])
    ref = ((pol.get("result") or {}).get("refused")) or []
    refused = bool([x for x in ref if "product/*.yaml" in json.dumps(x)])
    q.write("fixtures/traffic.csv", "t,ms\n1,40\n2,18\n")
    q.commit_all("experiment input")
    q.ok(["rebuild-memory"])
    design = {"hypothesis": "P2-AR-0077", "method": "probe",
              "inputs": [{"path": "fixtures/traffic.csv"}],
              "outputs": ["product/experimental.yaml"],
              "reproducibility": {"acceptance": {"mode": "tolerance", "relative": 0.05}}}
    e = q.run(["experiment", "design", "--fields", json.dumps(design)],
              session="S-x", role="research-agent")
    row = {"shape": f"PATHRULE-{tag}", "build": WHICH, "rule": rule_yaml,
           "rule_refused": refused, "design_ok": e.get("ok"),
           "design_error": (e.get("error") or {}).get("code"),
           "note": "does the appended class rule take a production path out of the production tree?"}
    rows.append(row)
    print(f"[{WHICH}] {row['shape']:24s} rule_refused={refused} design_ok={row['design_ok']} "
          f"err={row['design_error']}")


path_rule_case("derived", "- pattern: product/*.yaml\n  class: derived\n  owner_role: backend-engineer\n")
path_rule_case("evidence", "- pattern: product/*.yaml\n  class: evidence\n  owner_role: backend-engineer\n")

H.save(f"diff_{WHICH}", rows)
