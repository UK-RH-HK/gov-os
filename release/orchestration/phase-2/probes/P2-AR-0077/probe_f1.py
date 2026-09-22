#!/usr/bin/env python3
"""P2-AR-0077 / AR75-F1: does the install-trust surface still let a command reach
outside the project root?

Written from scratch. Nothing here is taken from `tests/certification/repair4.rs`;
the AR75 witnesses are RECONSTRUCTED from P2-AR-0075's prose (the original probe
was not available to me), and everything else is mine.

The proof is always the same: a marker file under <LAB>/outside/, which is outside
every project root by construction. `MARKER_OUTSIDE_PROJECT: true` on an `ok`,
ungated row is an escape. Status fields are recorded as corroboration only.
"""
import json, os
from harness4 import (fresh, bind, descriptor, install, verdict, save, marker_for,
                      OUTSIDE, gate_records)

p = fresh("f1")
rows = []
n = 0


def link_to(relname, target):
    lp = p.root / relname
    if lp.is_symlink():
        lp.unlink()          # a symlink we made ourselves, in a disposable project
    os.symlink(str(target), str(lp))


def shape(name, *, install_cmd=None, health_cmd=None, marker=None, setup=None,
          health=False, note="", extra=None):
    """Install one shape with its own bound review; optionally run `gov tools health`."""
    global n
    n += 1
    tool = f"TOOL-F1-{n:02d}"
    if marker is None:
        marker = marker_for(f"f1-{name}")
    if setup:
        setup(marker)
    d = descriptor(None, install_cmd=install_cmd, health_cmd=health_cmd, tool_id=tool)
    d.pop("security_review_record", None)
    bind(p, d)
    e = install(p, d, f"f1-{name}")
    v = verdict(e, p, marker, tool_id=tool)
    v.update({"shape": name, "tool": tool, "argv_install": install_cmd,
              "argv_health": health_cmd, "note": note})
    if health:
        h = p.run(["tools", "health"], session="S-adv", role="tooling-engineer")
        v["health_ok"] = h.get("ok")
        v["health_detail"] = json.dumps(h.get("result") or h.get("error"))[:1500]
        v["MARKER_AFTER_HEALTH"] = marker.exists()
    if extra:
        v.update(extra())
    rows.append(v)
    print(f"{name:26s} ok={v['ok']} branch={v['branch']} exp={v['expands_authority']} "
          f"trig={v['triggers_fired']} undet={len(v['undetermined'] or [])} "
          f"MARKER={v['MARKER_OUTSIDE_PROJECT']} afterhealth={v.get('MARKER_AFTER_HEALTH')}")
    return v


p.write("payload.txt", "P2-AR-0077 payload\n")

# ===========================================================================
# 1. AR75-F1's own witnesses, reconstructed. These MUST now gate with no marker.
# ===========================================================================
mk_link = lambda m: link_to("escape-link", m)            # dangling: cp creates target


def mk_link_live(m):
    m.write_text("pre-existing\n")                       # NOT dangling
    link_to("escape-link", m)


def mk_cfg(m):
    # an ordinary project file; curl -K reads the REST of its command line from it
    p.write("curlcfg", f'-o "{m}"\nurl = "file://{p.root}/payload.txt"\n')


shape("W1-cp-symlink-install", install_cmd=["cp", "payload.txt", "escape-link"],
      setup=mk_link, note="AR75-F1 witness: cp through a dangling in-project symlink")
shape("W1b-cp-symlink-live", install_cmd=["cp", "payload.txt", "escape-link"],
      setup=mk_link_live, note="same, target already exists (NOT dangling)")
shape("W2-cp-symlink-health", install_cmd=["true"],
      health_cmd=["cp", "payload.txt", "escape-link"], setup=mk_link, health=True,
      note="AR75-F1 witness in health_check.command; re-fires on gov tools health")
shape("W3-cp-symlink-env", install_cmd=["env", "cp", "payload.txt", "escape-link"],
      setup=mk_link, note="AR75-F1 witness behind an env wrapper")
shape("W4-curl-K-install", install_cmd=["curl", "-K", "curlcfg"], setup=mk_cfg,
      note="AR75-F1 witness: curl -K reads its command line from a project file")
shape("W5-curl-K-health", install_cmd=["true"], health_cmd=["curl", "-K", "curlcfg"],
      setup=mk_cfg, health=True, note="same, in health_check.command")

# ===========================================================================
# 2. The builder's three self-declared coverage gaps.
# ===========================================================================
shape("G1-dangling-mid", install_cmd=["cp", "payload.txt", "brokenmid/marker"],
      setup=lambda m: link_to("brokenmid", p.root / "does-not-exist-dir"),
      note="gap 1: BROKEN intermediate component")


def mk_live_mid(m):
    (OUTSIDE / "livedir").mkdir(parents=True, exist_ok=True)
    link_to("livemid", OUTSIDE / "livedir")


shape("G1b-live-mid", install_cmd=["cp", "payload.txt", "livemid/g1b.marker"],
      setup=mk_live_mid, marker=OUTSIDE / "livedir" / "g1b.marker",
      note="live intermediate symlink out of the project")
shape("G2-config-long", install_cmd=["curl", "--config", "curlcfg"], setup=mk_cfg,
      note="gap 2: --config long form")
shape("G2b-config-equals", install_cmd=["curl", "--config=curlcfg"], setup=mk_cfg,
      note="gap 2: --config=<file> equals form")
shape("G2c-bundle-sK", install_cmd=["curl", "-sK", "curlcfg"], setup=mk_cfg,
      note="gap 2/3: single-dash bundle carrying K")
shape("G2d-bundle-Ks", install_cmd=["curl", "-Ks", "curlcfg"], setup=mk_cfg,
      note="gap 2/3: bundle, other order")
shape("G3-CONFIG-upper", install_cmd=["curl", "--CONFIG", "curlcfg"], setup=mk_cfg,
      note="gap 3: uppercase long spelling")
shape("G3b-curl-k-insecure",
      install_cmd=["curl", "-k", "-s", "-o", "out.txt", f"file://{p.root}/payload.txt"],
      note="gap 3: the disclosed case-fold collision -- curl -k (--insecure)")
shape("G3c-curl-insecure-long",
      install_cmd=["curl", "--insecure", "-s", "-o", "out.txt", f"file://{p.root}/payload.txt"],
      note="gap 3: --insecure long form is NOT on the list -- does it gate?")

# ===========================================================================
# 3. My own attacks: other ways `curl` (a plain_argument_program) acquires
#    meaning the per-token path scan cannot read.
# ===========================================================================
m1 = marker_for("f1-E1")
shape("E1-curl-T-file-url", marker=m1,
      install_cmd=["curl", "-s", "-T", "payload.txt", f"file://{m1}"],
      note="MINE: curl uploads an in-project file to a file:// URL naming an absolute "
           "path outside the root. endpoint_host() returns None for the empty authority, "
           "and the token is not lexically an escape, so nothing looks at it as a path.")

m2 = marker_for("f1-E2")
shape("E2-curl-writeout", marker=m2,
      install_cmd=["curl", "-s", "-o", "out2.txt",
                   "-w", "%%output{%s}P2AR0077_WRITEOUT\n" % m2,
                   f"file://{p.root}/payload.txt"],
      note="MINE: curl --write-out %output{<abs path>} redirects write-out into an "
           "arbitrary absolute file. The path is EMBEDDED in a larger token, which "
           "token_values()/resolves_outside_project() never reads as a path.")

shape("E3-curl-read-host-file",
      install_cmd=["curl", "-s", "-o", "stolen.txt", "file:///etc/hostname"],
      note="MINE: read escape -- an absolute host path carried inside a file:// URL",
      extra=lambda: {"STOLEN_IN_PROJECT": (p.root / "stolen.txt").read_text()[:80]
                     if (p.root / "stolen.txt").exists() else None})


def mk_tdir(m):
    (OUTSIDE / "tdir").mkdir(parents=True, exist_ok=True)
    link_to("tlink", OUTSIDE / "tdir")


shape("E4-cp-target-directory", install_cmd=["cp", "-t", "tlink", "payload.txt"],
      setup=mk_tdir, marker=OUTSIDE / "tdir" / "payload.txt",
      note="MINE: cp -t <symlinked dir> -- a bare-word target directory")

# ===========================================================================
# 4. Negative controls -- the surface must NOT pass by gating everything.
# ===========================================================================
shape("NC1-conforming", install_cmd=["true"],
      note="OD-P2-03 req 6: a conforming installation proceeds ungated")
shape("NC2-curl-sS-https", install_cmd=["curl", "-sS", "https://pypi.org/simple/"],
      note="ordinary allowlisted network use alone does not gate")
shape("NC3-cp-inside", install_cmd=["cp", "payload.txt", "copy.txt"],
      note="cp with both operands inside the project installs ungated",
      extra=lambda: {"COPY_IN_PROJECT": (p.root / "copy.txt").exists()})
shape("NC4-sudo-make", install_cmd=["sudo", "make", "install"],
      note="control: privilege escalation still gates")
shape("NC5-apt-get", install_cmd=["apt-get", "install", "x"],
      note="control: host-level authority still gates")

save("f1", {"rows": rows, "outside_dir": str(OUTSIDE), "project_root": str(p.root),
            "hdg_gates_in_project": gate_records(p)})

esc = [r for r in rows if r.get("MARKER_OUTSIDE_PROJECT") or r.get("MARKER_AFTER_HEALTH")]
print("\n=== ROWS THAT PUT A FILE OUTSIDE THE PROJECT ROOT ===")
for r in esc:
    print(f"  {r['shape']}: ok={r['ok']} branch={r['branch']} expands={r['expands_authority']} "
          f"triggers={r['triggers_fired']} undetermined={r['undetermined']}")
print(f"total escapes: {len(esc)}")
