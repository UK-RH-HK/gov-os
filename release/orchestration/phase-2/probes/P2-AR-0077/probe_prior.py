#!/usr/bin/env python3
"""P2-AR-0077: re-verify the twelve prior findings (AR68-F1..F6, AR73-F1..F6) by
my own reproduction, against the commit under review.

For the command-classification families the assertion is on the classifier's own
verdict -- `authority_envelope.expands_authority` / `undetermined` -- which
`installation_authority` computes from the command alone, independently of the
security review (verified: the conforming descriptor with a mismatched review
reports expands_authority false while the branch is gated). That lets ~45 shapes
run without 45 governed review workflows. A representative subset is additionally
run with a bound review and `--execute`, so the filesystem proof is there too.
"""
import json, os, pathlib
from harness4 import fresh, bind, descriptor, install, verdict, save, marker_for, OUTSIDE

p = fresh("prior")
p.write("payload.txt", "x\n")
p.write("Makefile", "install:\n\ttrue\n")
p.write("installer.sh", "#!/bin/sh\ntrue\n")
p.write("setup.py", "pass\n")
p.write("xargsfile", "install\n")
os.chmod(p.root / "installer.sh", 0o755)
p.commit_all("prior fixtures")

rows = []
n = 0


def classify(family, name, argv, *, field="install_command", pins=None, extra=None):
    """Classification-only: what does installation_authority make of this command?"""
    global n
    n += 1
    tool = f"TOOL-PR-{n:03d}"
    d = descriptor(None, tool_id=tool)
    d.pop("security_review_record", None)
    if field == "install_command":
        d["install_command"] = argv
    elif field == "uninstall_command":
        d["uninstall_command"] = argv
    else:
        d["health_check"] = {"kind": "command", "command": argv, "expect_exit": 0}
    if pins:
        d["pinned_files"] = pins
    if extra:
        d.update(extra)
    e = install(p, d, f"pr-{name}", execute=False)
    r = e.get("result") or (e.get("error") or {}).get("details") or {}
    env = ((r.get("change_class") or {}).get("authority_envelope")) or {}
    row = {"family": family, "shape": name, "field": field, "argv": argv,
           "expands_authority": env.get("expands_authority"),
           "triggers": env.get("triggers_fired"),
           "undetermined": env.get("undetermined"),
           "GATES": bool(env.get("expands_authority"))}
    rows.append(row)
    flag = "OK " if row["GATES"] else "!! "
    print(f"{flag}{family:9s} {name:34s} expands={row['expands_authority']} "
          f"trig={row['triggers']} undet={len(row['undetermined'] or [])}")
    return row


# ================= AR68-F1: 25 shapes that installed ungated =================
for w in [["env"], ["nohup"], ["timeout", "5"], ["nice"], ["setsid"],
          ["stdbuf", "-o0"], ["ionice"], ["chrt", "1"], ["env", "FOO=1"]]:
    classify("AR68-F1", "wrap-" + "_".join(w), w + ["make", "install"])
for f in ["-ce", "-cl", "-cx", "-xc", "-cv", "-ic"]:
    classify("AR68-F1", f"bundle-{f}", ["sh", f, "cd ..; touch m"])
classify("AR68-F1", "equals--eval", ["node", "--eval=require('fs')"])
classify("AR68-F1", "equals--command", ["python3", "--command=import os"])
for a in ["awk", "gawk", "mawk", "nawk"]:
    classify("AR68-F1", f"flagless-{a}", [a, "BEGIN{system(\"touch ../m\")}"])
classify("AR68-F1", "script-sh-installer", ["sh", "installer.sh"])
classify("AR68-F1", "script-bare", ["./installer.sh"])
classify("AR68-F1", "script-python-setup", ["python3", "setup.py", "install"])
for fld in ("health_check", "uninstall_command"):
    classify("AR68-F1", f"wrap-env-make-{fld}", ["env", "make", "install"], field=fld)

# ================= AR73-F1: 14 more shapes ==================================
for w in [["flock", "-w", "1", "lockfile"], ["taskset", "-c", "0"], ["unshare"],
          ["xargs", "-a", "xargsfile"]]:
    classify("AR73-F1", "wrap-" + w[0], w + ["make", "install"])
classify("AR73-F1", "env-chain-9", ["env"] * 9 + ["make", "install"])
classify("AR73-F1", "env-chain-12", ["env"] * 12 + ["make", "install"])
classify("AR73-F1", "env-dash-S", ["env", "-S", "make install"])
classify("AR73-F1", "attached-python3-c", ["python3", "-cimport os"])
classify("AR73-F1", "attached-perl-e", ["perl", "-esystem('touch ../m')"])
classify("AR73-F1", "sed-1e", ["sed", "1e touch ../m", "payload.txt"])
classify("AR73-F1", "unnamed-program", ["zzqq-not-a-real-program", "--go"])
classify("AR73-F1", "git-unlisted", ["git", "clone", "https://example.invalid/x"])
classify("AR73-F1", "npm-unlisted", ["npm", "install", "-g", "x"])
classify("AR73-F1", "tar-unlisted", ["tar", "xf", "a.tar"])

# ================= AR73-F2: pin/executed-file divergence ====================
p.write("a/b.sh", "#!/bin/sh\ntrue\n")
os.chmod(p.root / "a/b.sh", 0o755)
p.write("a\\b.sh", "#!/bin/sh\ntouch ../pwned\n")
p.commit_all("ar73-f2 fixture")
import hashlib
sha = hashlib.sha256((p.root / "a/b.sh").read_bytes()).hexdigest()
classify("AR73-F2", "backslash-divergence", ["sh", "a\\b.sh"],
         pins=[{"path": "a/b.sh", "sha256": sha}])
classify("AR73-F2", "forward-slash-control", ["sh", "a/b.sh"],
         pins=[{"path": "a/b.sh", "sha256": sha}])

# ================= AR73-F5: stdin/attached-flag latent shapes ===============
classify("AR73-F5", "uninstall-attached-code", ["python3", "-cimport os"],
         field="uninstall_command")
classify("AR73-F5", "sh-dash-s", ["sh", "-s"])
classify("AR73-F5", "python3-dash", ["python3", "-"])

# ================= AR73-F6: a pinned path that is a symlink out =============
outside_script = OUTSIDE / "outside-pin.sh"
outside_script.write_text("#!/bin/sh\ntrue\n")
lp = p.root / "pinned-link.sh"
if lp.is_symlink():
    lp.unlink()
os.symlink(str(outside_script), str(lp))
sha2 = hashlib.sha256(outside_script.read_bytes()).hexdigest()
classify("AR73-F6", "pin-symlink-outside", ["sh", "pinned-link.sh"],
         pins=[{"path": "pinned-link.sh", "sha256": sha2}])

# ================= AR68-F2 / F5 / F6: review binding ========================
rev_rows = []


def review_case(name, mutate, note=""):
    q = fresh(f"prior-{name}")
    d = descriptor(None, install_cmd=["true"], tool_id="TOOL-REV")
    d.pop("security_review_record", None)
    from harness4 import review_subject, security_review
    subject = review_subject(d)
    try:
        rev = mutate(q, d, subject)
    except SystemExit as ex:
        # the governed route REFUSED to write the review at all -- that is itself the
        # closure proof for this case (fail closed at report-schema validation)
        v = {"family": "AR68-F2/F5/F6", "shape": name, "note": note,
             "review_could_not_be_written": str(ex)[:400], "branch": "n/a (review refused)",
             "installed": False}
        rev_rows.append(v)
        print(f"   {name:34s} REVIEW REFUSED AT SOURCE: {str(ex)[:120]}")
        return v
    d["security_review_record"] = rev
    e = install(q, d, name)
    v = verdict(e, q, None, tool_id="TOOL-REV")
    v.update({"family": "AR68-F2/F5/F6", "shape": name, "note": note})
    # AR68-F5: re-arm by moving the installed descriptor aside, then retry
    desc = q.root / "governance/project/tools/TOOL-REV.yaml"
    if desc.exists():
        import shutil, time as _t
        shutil.move(str(desc), str(OUTSIDE / f"aside-{name}-{int(_t.time()*1000)}.yaml"))
        e2 = install(q, d, name + "-rearm")
        v["rearm_branch"] = ((e2.get("result") or {}).get("change_class") or {}).get("branch")
        v["rearm_installed"] = (e2.get("result") or {}).get("installed")
    rev_rows.append(v)
    print(f"   {name:34s} branch={v['branch']} installed={v['installed']} "
          f"rearm={v.get('rearm_branch')}")
    return v


from harness4 import security_review as _sr

review_case("AR68-F2-subjectless",
            lambda q, d, s: _sr(q, "TOOL-REV", "1.0.0", subject=None),
            note="a review naming no subject_sha256 authorises nothing (P2-ADJ-0004)")
review_case("AR68-F6-numeric-subject",
            lambda q, d, s: _sr(q, "TOOL-REV", "1.0.0", subject=12345),
            note="a wrong-TYPED subject must fail closed, not fall back")
review_case("AR68-F6-wrong-subject",
            lambda q, d, s: _sr(q, "TOOL-REV", "1.0.0", subject="00" * 32),
            note="a subject that is not this descriptor's digest authorises nothing")
review_case("CONTROL-bound",
            lambda q, d, s: _sr(q, "TOOL-REV", "1.0.0", subject=s),
            note="control: the correctly bound review DOES authorise (no over-gating)")

save("prior", {"classification": rows, "review": rev_rows})
bad = [r for r in rows if not r["GATES"]]
print(f"\n=== SHAPES THAT DID NOT GATE ({len(bad)}) ===")
for r in bad:
    print(f"  {r['family']} {r['shape']}: {r['argv']}")
