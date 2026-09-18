#!/usr/bin/env python3
"""S1 (canonical OS repository) and S2 (immutable releases, eleven bullets) through `gov release build/verify`.

[C*] S1 separation in the canonical repository and what reaches a consumer; consumers cannot rebuild the OS
[M*] S2 manifest content per bullet; immutability; verification; semantic-version handling
Run: PROBE_TMP=<scratch> python3 S1-S2-release.py
"""
import os, sys, json, shutil, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml

print("## [C1] canonical repository layout (this candidate)")
for d in ["framework", "runtime", "cli", "tools", "migrations", "tests", "fixtures", "lessons/inbox", "change-proposals", "release", "docs"]:
    print(f"[C1] {d:18s} present={os.path.isdir(os.path.join(REPO, d))} tracked_files={len(subprocess.run(['git', 'ls-files', d], cwd=REPO, capture_output=True, text=True).stdout.split())}")
sb = Sandbox("s12")
canon = canonical_copy(sb.path("canon"))
os.makedirs(os.path.join(canon, "release/notes"), exist_ok=True)
open(os.path.join(canon, "release/notes/4.1.5.md"), "w").write("# 4.1.5\nAudit probe release notes.\n")
b = sb.gov("release", "build", "--version", "4.1.5", "--canonical", canon, "--out", sb.path("out"), quiet=True)
m = b["result"]
rd = sb.path("out", "releases", "4.1.5")
print("[C1] built release directory:", sorted(os.listdir(rd)), "| kernel payload top-level:", sorted(os.listdir(os.path.join(rd, "kernel"))))
print("[C1] payload excludes runtime/cli/tests/fixtures sources:", not any(x in os.listdir(os.path.join(rd, "kernel")) for x in ("runtime", "cli", "tests", "fixtures")))
print("\n## [C2] consumers receive the released payload only and cannot rebuild the OS")
p = sb.new_repo("consumer")
sb.gov("init", "--source", os.path.join(rd, "kernel"), "--name", "c", "--alias", "ca", "--skip-index", cwd=p, quiet=True)
print("[C2] consumer tree top-level:", sorted(x for x in os.listdir(p) if x != ".git"), "| governance/:", sorted(os.listdir(os.path.join(p, "governance"))))
print("[C2] consumer contains OS sources (runtime/, cli/, Cargo.toml)?", any(os.path.exists(os.path.join(p, x)) for x in ("runtime", "cli", "Cargo.toml")))
x = sb.gov("release", "build", "--version", "4.1.5", "--canonical", p, "--out", sb.path("cons-out"), quiet=True)
print("[C2] `gov release build --canonical <consumer>` ->", "ok" if x["ok"] else f"REFUSED {err(x)}: {x['error']['message'][:120]}")
open(os.path.join(p, "governance/kernel/policies/AUTHORITY_POLICY.yaml"), "a").write("# local reinterpretation\n")
t = sb.gov("task", "create", "--objective", "after local kernel change", cwd=p, quiet=True)
print("[C2] consumer edits its kernel copy -> next governed mutation:", "ok" if t["ok"] else f"REFUSED {err(t)}")
shutil.copytree(os.path.join(REPO, "lessons"), os.path.join(canon, "lessons")); shutil.copytree(os.path.join(REPO, "change-proposals"), os.path.join(canon, "change-proposals"))
lc = sb.gov("lessons", "cluster", "--inbox", os.path.join(canon, "lessons/inbox"), "--proposals", os.path.join(canon, "change-proposals"), cwd=canon, quiet=True)
print("[C1] canonical lessons/inbox -> change-proposals pipeline (`gov lessons cluster`):", "ok " + json.dumps(lc["result"])[:200] if lc["ok"] else f"REFUSED {err(lc)}")

print("\n## [M1] manifest content per S2 bullet")
checks = [("semantic versioning", "version"), ("release manifest", "framework"), ("file hashes", "file_hashes"), ("supported migrations", "supported_from_versions"),
          ("supported migrations (ids)", "migration_ids"), ("schema versions", "schema_versions"), ("CLI version", "cli_version"), ("runtime version", "runtime_version"),
          ("adapter versions", "adapter_versions"), ("release notes", "release_notes"), ("affected indexes", "required_index_rebuilds"), ("human decisions", "human_gates"),
          ("breaking changes", "breaking_changes"), ("rollback", "rollback_procedure"), ("release commit", "release_commit"), ("release hash", "release_hash"), ("certification", "certification")]
for label, k in checks:
    v = m.get(k)
    print(f"[M1] {label:26s} {k:24s} = {json.dumps(v)[:120]}")
print("[M1] capability/plugin versions anywhere in the manifest:", [k for k in m if "capab" in k.lower() or "plugin" in k.lower()], "| capabilities/ in payload:", os.path.isdir(os.path.join(rd, "kernel", "capabilities")))
print("[M1] RELEASE_NOTES.md / ROLLBACK.md files:", os.path.exists(os.path.join(rd, "RELEASE_NOTES.md")), os.path.exists(os.path.join(rd, "ROLLBACK.md")))
fh = m["file_hashes"]; k0 = sorted(fh)[0]
import hashlib
print("[M1] file_hashes entry verified by hand:", k0, fh[k0] == hashlib.sha256(open(os.path.join(rd, "kernel", k0), "rb").read()).hexdigest(), "| count =", len(fh))
print("[M1] manifest validates against the release-manifest schema (build refuses otherwise): see runtime/src/release.rs schemas.validate")

print("\n## [M2] immutability and verification")
x = sb.gov("release", "build", "--version", "4.1.5", "--canonical", canon, "--out", sb.path("out"), quiet=True)
print("[M2] rebuild the same version into the same release dir ->", "ok" if x["ok"] else f"REFUSED {err(x)}")
v = sb.gov("release", "verify", rd, quiet=True)["result"]; print("[M2] release verify (pristine):", {k: v[k] for k in ("ok", "modified", "missing", "added", "release_hash_matches_kernel")})
open(os.path.join(rd, "kernel/policies/TOOL_POLICY.yaml"), "a").write("# edited after release\n")
v = sb.gov("release", "verify", rd, quiet=True)["result"]; print("[M2] release verify (payload edited after release):", {k: v[k] for k in ("ok", "modified")})
mj = json.load(open(os.path.join(rd, "manifest.json"))); mj["certification"]["status"] = "CERTIFIED"; mj["release_notes"] = "rewritten"; json.dump(mj, open(os.path.join(rd, "manifest.json"), "w"))
v = sb.gov("release", "verify", sb.path("out", "releases", "4.1.5"), quiet=True)["result"]; print("[M2] release verify after editing manifest.json certification/notes (payload restored? no):", {k: v[k] for k in ("ok", "modified", "certification")})

print("\n## [M3] reproducibility: an existing version is rebuilt from its recorded release_commit, not the working tree")
os.makedirs(os.path.join(canon, "release/releases/4.1.5"), exist_ok=True)
shutil.copy(os.path.join(rd, "manifest.json"), os.path.join(canon, "release/releases/4.1.5/manifest.json"))
mj = json.load(open(os.path.join(canon, "release/releases/4.1.5/manifest.json"))); mj["release_commit"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=canon, capture_output=True, text=True).stdout.strip()
json.dump(mj, open(os.path.join(canon, "release/releases/4.1.5/manifest.json"), "w"))
open(os.path.join(canon, "framework/policies/TOOL_POLICY.yaml"), "a").write("# uncommitted working-tree edit\n")
x = sb.gov("release", "build", "--version", "4.1.5", "--canonical", canon, "--out", sb.path("out2"), quiet=True)
print("[M3] rebuild ->", "ok" if x["ok"] else f"REFUSED {err(x)}", "| provenance =", json.dumps((x.get("result") or {}).get("provenance"))[:200], "| release_hash equal to original:", (x.get("result") or {}).get("release_hash") == m["release_hash"])

print("\n## [M4] semantic versioning: version string handling and breaking-change semantics")
cv = canonical_copy(sb.path("canon-v"), version="banana")
x = sb.gov("release", "build", "--version", "banana", "--canonical", cv, "--out", sb.path("vout"), quiet=True)
print("[M4] non-semver version 'banana' ->", "ok (built)" if x["ok"] else f"REFUSED {err(x)}: {x['error']['message'][:120]}")
mig = ("M-4.1.5-4.1.6.yaml", {"id": "M-4.1.5-4.1.6", "from_version": "4.1.5", "to_version": "4.1.6", "description": "removes a schema field (breaking)", "breaking": True,
       "human_gate": "schema_break", "affected_indexes": ["semantic"], "overlay_template_changes": [], "operations": [{"op": "note", "text": "breaking"}], "rollback": "r"})
cb = canonical_copy(sb.path("canon-b"), version="4.1.6", supported_from=["4.1.5"], extra_migration=mig)
x = sb.gov("release", "build", "--version", "4.1.6", "--canonical", cb, "--out", sb.path("bout"), quiet=True)
print("[M4] a PATCH bump (4.1.5 -> 4.1.6) carrying a breaking migration ->", "ok (built)" if x["ok"] else f"REFUSED {err(x)}", "| breaking_changes =", (x.get("result") or {}).get("breaking_changes"), "| human_gates =", (x.get("result") or {}).get("human_gates"), "| required_index_rebuilds =", (x.get("result") or {}).get("required_index_rebuilds"))
c = sb.gov("update", "--check", "--source", sb.path("bout", "releases", "4.1.6", "kernel"), cwd=p, quiet=True)
print("[M4] consumer update --check against it: radius =", (c.get("result") or {}).get("impact", {}).get("radius"), "| human_gate_required =", (c.get("result") or {}).get("human_gate_required"))
print("[M4] CLI/kernel major-version compatibility rule: lock::compatibility (4.1.x vs 5.0.0 incompatible) — exercised via update --check below")
cmaj = canonical_copy(sb.path("canon-maj"), version="5.0.0", supported_from=["4.1.5"])
x = sb.gov("release", "build", "--version", "5.0.0", "--canonical", cmaj, "--out", sb.path("mout"), quiet=True)
c = sb.gov("update", "--check", "--source", sb.path("mout", "releases", "5.0.0", "kernel"), cwd=p, quiet=True)
print("[M4] 4.1.5 -> 5.0.0 check:", json.dumps({k: (c.get("result") or {}).get(k) for k in ("compatible", "migration_path_complete", "recommendation")}))
print("\nDONE")
