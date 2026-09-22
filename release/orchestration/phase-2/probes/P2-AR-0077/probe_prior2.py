#!/usr/bin/env python3
"""P2-AR-0077: the four prior findings probe_prior.py does not cover --
AR68-F3 / AR73-F3 (path-rule shadowing) and AR68-F4 / AR73-F4 (lifetime
re-verification of a pinned health script)."""
import hashlib, json, os, shutil, time
from harness4 import (fresh, bind, descriptor, install, verdict, save, marker_for,
                      review_subject, security_review, OUTSIDE, ASIDE)

rows = []


def append_rule(p, rule_yaml):
    c = p.root / "governance/project/REPOSITORY_CONTRACT.yaml"
    lines = c.read_text().split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("paths:"))
    end = next((i for i in range(start + 1, len(lines))
                if lines[i] and not lines[i][0].isspace() and not lines[i].startswith("-")),
               len(lines))
    c.write_text("\n".join(lines[:end] + rule_yaml.rstrip("\n").split("\n") + lines[end:]))
    p.commit_all("append a path rule by hand")


def path_rule(tag, pattern, body, note=""):
    """Append one widening rule; is it refused AND reported on every surface?"""
    p = fresh(f"pr2-{tag}")
    append_rule(p, f'- pattern: "{pattern}"\n' + body)   # ALWAYS quote: a bare *.txt is a YAML alias
    pol = p.run(["policy", "overrides"])
    ref = ((pol.get("result") or {}).get("refused")) or []
    mine = [x for x in ref if isinstance(x.get("value"), dict) and x["value"].get("pattern") == pattern]
    missing_kernel = [x for x in ref if "is missing" in (x.get("reason") or "")]
    assert not missing_kernel, f"{tag}: the hand edit BROKE the document ({len(missing_kernel)} kernel rules reported missing) -- probe bug, not a product result"
    doc = p.run(["doctor"])
    docj = json.dumps(doc.get("result") or doc.get("error"))
    aud = p.run(["audit"])
    row = {"family": "AR68-F3/AR73-F3", "shape": tag, "pattern": pattern, "note": note,
           "REFUSED": bool(mine),
           "refusal_reason": (mine[0].get("reason") if mine else None),
           "doctor_ok": doc.get("ok"),
           "doctor_mentions_pattern": pattern in docj,
           "audit_ok": aud.get("ok")}
    rows.append(row)
    print(f"{tag:28s} REFUSED={row['REFUSED']} doctor_ok={row['doctor_ok']} "
          f"reason={(row['refusal_reason'] or '')[:90]}")
    return row


# --- AR68-F3: an appended pattern with no kernel counterpart that widens -----
path_rule("AR68-F3-archive-txt", "archive/*.txt",
          "  class: source\n  mutation: allowed\n  export: allowed\n  semantic_index: true\n"
          "  lexical_index: true\n  graph_index: true\n  code_index: true\n  default_retrieval: true\n",
          note="AR68-F3: widen the kernel's archive/** (mutation restricted, export denied)")

# --- AR73-F3: a `/`-free pattern, which glob_match also matches as **/<pat> --
path_rule("AR73-F3-star-txt", "*.txt",
          "  class: source\n  mutation: allowed\n  export: allowed\n  semantic_index: true\n"
          "  lexical_index: true\n  graph_index: true\n  code_index: true\n  default_retrieval: true\n",
          note="AR73-F3: a slash-free pattern widening archive/** through the implicit **/ rule")
path_rule("AR73-F3-star-json", "*.json",
          "  class: source\n  mutation: allowed\n  export: allowed\n  semantic_index: true\n"
          "  lexical_index: true\n  graph_index: true\n  code_index: true\n  default_retrieval: true\n",
          note="AR73-F3: the same against governance/registry/** (os-only, export denied)")

# --- negative control: a genuinely RESTRICTIVE appended rule is honoured -----
path_rule("NC-restrictive", "docs/secretsy/**",
          "  class: source\n  mutation: prohibited\n  export: denied\n  semantic_index: false\n"
          "  lexical_index: false\n  graph_index: false\n  code_index: false\n  default_retrieval: false\n",
          note="negative control: narrowing must still be HONOURED (not refused)")

# ===========================================================================
# AR68-F4 / AR73-F4: lifetime re-verification of a pinned health script
# ===========================================================================
def lifetime(tag, mutate_descriptor=None, note=""):
    p = fresh(f"pr2-{tag}")
    marker = marker_for(f"pr2-{tag}")
    p.write("health.sh", "#!/bin/sh\nexit 0\n")
    os.chmod(p.root / "health.sh", 0o755)
    p.commit_all("health script")
    sha = hashlib.sha256((p.root / "health.sh").read_bytes()).hexdigest()
    d = descriptor(None, install_cmd=["true"],
                   health_cmd=["sh", "health.sh"], tool_id="TOOL-LIFE")
    d["pinned_files"] = [{"path": "health.sh", "sha256": sha}]
    d.pop("security_review_record", None)
    bind(p, d)
    e = install(p, d, tag)
    v = verdict(e, p, marker, tool_id="TOOL-LIFE")
    v.update({"family": "AR68-F4/AR73-F4", "shape": tag, "note": note})
    v["install_branch"] = v["branch"]
    if not v["installed"]:
        v["RESULT"] = "did not install; lifetime check not reached"
        rows.append(v)
        print(f"{tag:28s} install_branch={v['branch']} (not installed)")
        return v
    # AR68-F4: change the pinned script AFTER a clean install
    (p.root / "health.sh").write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 0\n")
    # AR73-F4: additionally corrupt the structural key the guard used to read
    if mutate_descriptor:
        desc = p.root / "governance/project/tools/TOOL-LIFE.yaml"
        desc.write_text(mutate_descriptor(desc.read_text()))
    h = p.run(["tools", "health"], session="S-adv", role="tooling-engineer")
    v["health_ok"] = h.get("ok")
    hj = json.dumps(h.get("result") or h.get("error"))
    v["health_detail"] = hj[:900]
    v["MARKER_AFTER_HEALTH"] = marker.exists()
    v["RESULT"] = "ESCAPED" if marker.exists() else "re-gated"
    rows.append(v)
    print(f"{tag:28s} installed={v['installed']} health_ok={v['health_ok']} "
          f"MARKER={v['MARKER_AFTER_HEALTH']} -> {v['RESULT']}")
    return v


def drop_key(txt):
    return "\n".join(l for l in txt.split("\n") if not l.startswith("installation_sha256"))


def null_key(txt):
    return "\n".join(("installation_sha256: null" if l.startswith("installation_sha256") else l)
                     for l in txt.split("\n"))


def num_key(txt):
    return "\n".join(("installation_sha256: 12345" if l.startswith("installation_sha256") else l)
                     for l in txt.split("\n"))


lifetime("AR68-F4-plain", None, note="AR68-F4: pinned health script changed after a clean install")
lifetime("AR73-F4-absent", drop_key, note="AR73-F4: installation_sha256 removed")
lifetime("AR73-F4-null", null_key, note="AR73-F4: installation_sha256 null")
lifetime("AR73-F4-number", num_key, note="AR73-F4: installation_sha256 a number")

save("prior2", rows)
print("\n=== ESCAPES ===")
for r in rows:
    if r.get("RESULT") == "ESCAPED" or (r.get("family", "").startswith("AR68-F3")
                                        and r["shape"] != "NC-restrictive" and not r.get("REFUSED")):
        print("  ", r["shape"], r.get("RESULT"))
