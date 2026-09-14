#!/usr/bin/env python3
"""P3 (RoT-1 revision 3) — full pre-RoT command-register matrix against the revision-3 legacy-path-occupation layout.

Attribution: adapted from the review-r2 probe `release/root-of-trust/4.1.6-review-r2/evidence/P3-pre-rot-binary-matrix.py`
(base-project construction, restricted classification, legacy update snapshot, tree hashing). Changes: every leaf command
of each binary's own `--help` register (no hand list), synthesized arguments and mode-flag variants, four real legacy
binaries (4.1.2, 4.1.3, 4.1.4, 4.1.5), the revision-3 layout (`08` §2, `13` §3), whole-tree before/after digests, and a
positive control on an ordinary legacy project that proves the argument synthesis reaches mutating code paths.

Scratch only. GOV_* removed from every child environment; GOV_KERNEL_CACHE and HOME point into scratch. The repository is
never written. No forced deletes: every run works on its own fresh copy.

Usage: P3r3.py <scratch-dir> [--layouts L0,L3] [--binaries 4.1.2,...] [--workers N] > P3.json
"""
import argparse, concurrent.futures as cf, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("P3_REPO") or os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LEGACY = os.environ.get("P3_LEGACY_BIN", "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin")
SENT = "ROT-1-TRUST-FORMAT:requires-gov>=4.1.6:this-binary-cannot-operate-this-project"
MARK = "P3R3RESTRICTEDMARKER"
GLOBAL = {"--root", "--json", "--session", "--role", "--help", "--version"}


# ------------------------------------------------------------------------------------------------ environment
def child_env(scratch, tag):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
    home = os.path.join(scratch, "homes", tag)
    os.makedirs(home, exist_ok=True)
    env.update({"HOME": home, "GOV_KERNEL_CACHE": os.path.join(scratch, "caches", tag), "GIT_AUTHOR_NAME": "p3", "GIT_AUTHOR_EMAIL": "p3@x",
                "GIT_COMMITTER_NAME": "p3", "GIT_COMMITTER_EMAIL": "p3@x", "XDG_CONFIG_HOME": os.path.join(home, ".config"),
                "XDG_STATE_HOME": os.path.join(home, ".local/state"), "XDG_CACHE_HOME": os.path.join(home, ".cache"),
                "P3_MARKER": os.path.join(scratch, "markers", tag)})
    os.makedirs(os.path.join(scratch, "markers"), exist_ok=True)
    return env


def git(root, *a):
    subprocess.run(["git", "-c", "user.name=p3", "-c", "user.email=p3@x", *a], cwd=root, check=True, capture_output=True)


def gov(binary, root, args, env, role="orchestrator", timeout=180):
    t0 = time.time()
    try:
        r = subprocess.run([binary, "--json", "--root", root, "--session", "S-p3r3", "--role", role, *args], env=env, capture_output=True,
                           text=True, timeout=timeout, stdin=subprocess.DEVNULL, cwd=root)
        out, err, rc = r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired as e:
        out, err, rc = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), "TIMEOUT", -999
    try:
        d = json.loads(out)
    except Exception:
        d = {"raw": out[-400:], "stderr": err[-400:]}
    d["_rc"], d["_secs"] = rc, round(time.time() - t0, 2)
    return d


code = lambda d: (d.get("error") or {}).get("code") if isinstance(d.get("error"), dict) else None


# ------------------------------------------------------------------------------------------------ register (from --help)
def help_of(binary, path, env):
    r = subprocess.run([binary, *path, "--help"], capture_output=True, text=True, env=env, timeout=30, stdin=subprocess.DEVNULL)
    return r.stdout or r.stderr


def parse_help(text):
    sec, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^([A-Z][A-Za-z ]+):\s*(.*)$", line)
        if m and not line.startswith(" "):
            cur = m.group(1)
            sec[cur] = [m.group(2)] if m.group(2) else []
        elif cur is not None:
            sec[cur].append(line)
    usage = " ".join(x.strip() for x in sec.get("Usage", []))
    subs = []
    for line in sec.get("Commands", []):
        m = re.match(r"^\s{2}([a-z0-9][a-z0-9-]*)(\s{2,}.*)?$", line)
        if m and m.group(1) != "help":
            subs.append(m.group(1))
    args = []
    for line in sec.get("Arguments", []):
        m = re.match(r"^\s+([<\[])([A-Z0-9_]+)(\.\.\.)?[>\]](\.\.\.)?\s*(.*)$", line)
        if m:
            args.append({"name": m.group(2), "required": m.group(1) == "<"})
    tail = usage.split("[OPTIONS]")[-1] if "[OPTIONS]" in usage else usage
    opts = []
    for line in sec.get("Options", []):
        m = re.match(r"^\s+(?:-(\w), )?--([a-z0-9-]+)(?: <([A-Z0-9_]+)>)?\s*(.*)$", line)
        if m and "--" + m.group(2) not in GLOBAL:
            opts.append({"long": "--" + m.group(2), "value": m.group(3),
                         "required": bool(m.group(3)) and re.search(r"(^|\s)--%s <" % re.escape(m.group(2)), tail) is not None})
    return usage, subs, args, opts


def register(binary, env):
    leaves, groups = [], []

    def walk(path):
        usage, subs, args, opts = parse_help(help_of(binary, path, env))
        if subs:
            groups.append({"path": path, "subcommands": subs})
            for s in subs:
                walk(path + [s])
        else:
            leaves.append({"path": path, "usage": usage, "args": args, "options": opts})
    walk([])
    return {"groups": groups, "leaves": leaves}


# ------------------------------------------------------------------------------------------------ base project
def build_base(scratch, gov415, fx):
    root = os.path.join(scratch, "base")
    os.makedirs(root)
    env = child_env(scratch, "base")
    git(root, "init", "-q"); git(root, "commit", "-q", "--allow-empty", "-m", "i")
    b = {"init_4.1.4": gov(gov415, root, ["init", "--source", REPO + "/release/releases/4.1.4", "--name", "p3r3", "--skip-index"], env).get("ok")}
    git(root, "add", "-A"); git(root, "commit", "-q", "-m", "4.1.4")
    first = gov(gov415, root, ["update", "--apply", "--source", REPO + "/release/releases/4.1.5"], env)
    gid = ((first.get("error") or {}).get("details") or {}).get("gate")
    b["update_gate"] = gid
    b["present"] = gov(gov415, root, ["gate", "present", gid], env).get("ok")
    b["decide"] = gov(gov415, root, ["decide", gid, "--option", "A", "--by", "owner"], env).get("ok")
    ap = gov(gov415, root, ["update", "--apply", "--approve", "--source", REPO + "/release/releases/4.1.5"], env)
    b["update_to_4.1.5_applied"] = (ap.get("result") or {}).get("applied")
    b["legacy_update_snapshot_present"] = os.path.exists(root + "/.governance-runtime/update/4.1.5/snapshot.json")
    # project-owned strengthening added after the update
    os.makedirs(root + "/product", exist_ok=True)
    open(root + "/product/restricted-plan.md", "w").write(f"# Plan\n\n{MARK} proprietary customer terms\n")
    dsp = root + "/governance/project/DATA_SENSITIVITY.yaml"
    ds = yaml.safe_load(open(dsp))
    ds.setdefault("classifications", []).append({"pattern": "product/restricted-plan.md", "class": "restricted", "reason": "customer terms"})
    yaml.safe_dump(ds, open(dsp, "w"), sort_keys=False)
    # fixtures that let identifier-taking commands reach their mutating code paths
    t = gov(gov415, root, ["task", "create", "--class", "documentation", "--objective", "p3 probe task", "--title", "p3", "--status", "READY"], env)
    fx["TASK"] = ((t.get("result") or {}).get("id")) or "TASK-0001"
    g = gov(gov415, root, ["gate", "create", "--question", "p3 probe gate?", "--fields", json.dumps({"options": [{"id": "A", "description": "yes"}, {"id": "B", "description": "no"}], "impact_radius": "R1", "confidence": 0.9, "reversibility": "reversible"})], env)
    fx["GATE"] = ((g.get("result") or {}).get("id")) or gid
    gov(gov415, root, ["gate", "present", fx["GATE"]], env)
    os.makedirs(root + "/spec/now", exist_ok=True)
    mf = os.path.join(scratch, "fixtures", "cit-manifest.json")
    os.makedirs(os.path.dirname(mf), exist_ok=True)
    json.dump([{"op": "write_file", "path": "spec/now/NOW.md", "content": "# NOW\nP3 CIT WROTE THIS\n"}], open(mf, "w"))
    fx["MANIFEST"] = mf
    c = gov(gov415, root, ["cit", "propose", "--proposal", "p3 probe change", "--trigger", "editorial", "--targets", fx["TASK"], "--manifest", mf], env)
    fx["CIT"] = ((c.get("result") or {}).get("id")) or "CIT-0001"
    b["cit_simulate"] = gov(gov415, root, ["cit", "simulate", fx["CIT"]], env).get("ok")
    b["cit_approve"] = gov(gov415, root, ["cit", "approve", fx["CIT"], "--by", "orchestrator", "--method", "auto"], env).get("ok")
    h = gov(gov415, root, ["handoff", "create", "--to-role", "backend-engineer", "--task", fx["TASK"]], env)
    fx["HANDOFF"] = ((h.get("result") or {}).get("id")) or "H-0001"
    os.makedirs(root + "/spec/lessons", exist_ok=True)
    shutil.copy(REPO + "/fixtures/upstream-learning/lessons/L-0001.yaml", root + "/spec/lessons/L-0001.yaml")
    up = gov(gov415, root, ["upstream", "prepare", "L-0001"], env)
    pk = ((up.get("result") or {}).get("packet")) or ((up.get("result") or {}).get("path"))
    fx["PACKET"] = os.path.join(scratch, "fixtures", "packet.yaml")
    if pk and os.path.exists(pk):
        shutil.copy(pk, fx["PACKET"])
    # plugin and tool descriptors
    marker = os.path.join(scratch, "fixtures", "PLUGIN_EXECUTED_MARKER")
    os.makedirs(root + "/tools", exist_ok=True)
    open(root + "/tools/probe.sh", "w").write("#!/bin/sh\ncat >/dev/null\necho EXECUTED >> \"${P3_MARKER:-/dev/null}\"\nprintf '{{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{{\"id\":\"probe\",\"version\":\"1\"}},\"outputs\":{{\"symbols\":[],\"imports\":[],\"calls\":[],\"chunks\":[]}}}}'\n")
    os.chmod(root + "/tools/probe.sh", 0o755)
    os.makedirs(root + "/governance/project/plugins", exist_ok=True)
    open(root + "/governance/project/plugins/p-probe.yaml", "w").write('plugin_id: p-probe\ncapability: code_intel\ncommand: ["tools/probe.sh"]\nversion: "1"\nlanguages: ["python"]\n')
    fx["PLUGIN_DESCRIPTOR"] = os.path.join(scratch, "fixtures", "p-probe.yaml")
    shutil.copy(root + "/governance/project/plugins/p-probe.yaml", fx["PLUGIN_DESCRIPTOR"])
    fx["MARKER"] = marker
    b["plugin_register"] = gov(gov415, root, ["plugins", "register", "--descriptor", fx["PLUGIN_DESCRIPTOR"]], env).get("ok")
    td = os.path.join(scratch, "fixtures", "tool.json")
    json.dump({"tool_id": "p3tool", "name": "p3tool", "type": "CLI", "capabilities": ["run_tests"], "version": "1", "version_pin": "1.0.0", "license": "MIT",
               "reversible": True, "cost_usd": 0.0, "install_command": ["sh", "-c", "echo INSTALLED >> \"${P3_MARKER:-/dev/null}\""], "uninstall_command": ["true"],
               "required_permission_classes": ["RUN_TESTS"], "health_check": {"kind": "command_exists", "command": ["true"]}}, open(td, "w"))
    fx["TOOL_DESCRIPTOR"] = td
    rep = os.path.join(scratch, "fixtures", "report.json")
    json.dump({"work_completed": "p3", "files_changed": ["README.md"], "tests": {"status": "not_applicable_with_reason", "reason": "p3"}, "outcome": "success", "evidence": []}, open(rep, "w"))
    fx["REPORT"] = rep
    ret = os.path.join(scratch, "fixtures", "return.json")
    json.dump({"task": fx["TASK"], "status": "success", "work_completed": "x", "files_changed": [], "evidence": [], "tests": {"status": "passed"}, "discoveries": [], "risks": [],
               "lessons": [], "proposed_decisions": [], "unresolved": [], "recommended_next_action": "close"}, open(ret, "w"))
    fx["RETURN"] = ret
    git(root, "add", "-A"); git(root, "commit", "-q", "-m", "p3 fixtures + classification")
    b["rebuild"] = gov(gov415, root, ["rebuild-memory"], env).get("ok")
    q = gov(gov415, root, ["memory", "query", MARK], env)
    b["control_restricted_retrievable"] = [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if "restricted-plan" in (h.get("path") or "")]
    b["kernel_trust_verified"] = (gov(gov415, root, ["kernel", "trust"], env).get("result") or {}).get("verified")
    b["fixtures"] = {k: v for k, v in fx.items()}
    return root, b


# ------------------------------------------------------------------------------------------------ layouts
def aside(scratch, layout, src):
    d = os.path.join(scratch, "aside", layout, os.path.relpath(src, "/").replace("/", "__"))
    os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.move(src, d)


def to_layout(scratch, base, layout):
    dst = os.path.join(scratch, "layout-" + layout)
    shutil.copytree(base, dst, symlinks=True)
    g = dst + "/governance"
    info = {"layout": layout}
    if layout == "L0":
        info["description"] = "positive control: the ordinary legacy (4.1.5-installed) project, unchanged"
        info["overlay"] = "governance/project"
        return dst, info
    # L3 / L3A: revision-3 legacy-path-occupation layout (08 §2, 13 §3)
    os.makedirs(g + "/trust/state", exist_ok=True)
    shutil.move(g + "/kernel", g + "/trust/kernel")
    aside(scratch, layout, g + "/trust/kernel/KERNEL_MANIFEST.json")          # RoT-1 never uses the legacy manifest
    lock = yaml.safe_load(open(g + "/framework.lock"))
    aside(scratch, layout, g + "/framework.lock")
    rot_lock = {"lock_schema_version": "3.0.0", "trust_format": "rot-1", "layout": "legacy-path-occupation-v1", "framework": lock.get("framework"),
                "version": "4.1.6", "release_statement_digest": "sha256:" + "a" * 64, "kernel": {"tree_digest": "sha256:" + "0" * 64}}
    json.dump(rot_lock, open(g + "/trust/framework.lock", "w"), indent=1, sort_keys=True)
    open(g + "/trust/FORMAT", "w").write('{"layout":"legacy-path-occupation-v1","minimum_reader":"4.1.6","trust_format":"rot-1"}')
    shutil.copy(REPO + "/release/root-of-trust/4.1.6/examples/rev2/release-final.dsse.json", g + "/trust/release.dsse.json")
    shutil.copy(REPO + "/release/root-of-trust/4.1.6/examples/rev2/trust-state.1.dsse.json", g + "/trust/state/1.dsse.json")
    shutil.move(g + "/project", g + "/overlay")
    shutil.move(g + "/generated", g + "/views")
    # occupy every legacy authority path with an entry of the wrong type (fail before first write)
    os.makedirs(g + "/framework.lock")
    open(g + "/framework.lock/ROT-1-TRUST-FORMAT", "w").write(SENT + "\n")
    for p in ("kernel", "project", "generated"):
        open(g + "/" + p, "w").write(SENT + "\n")
    occupied = ["governance/kernel (file)", "governance/project (file)", "governance/generated (file)", "governance/framework.lock (directory)"]
    if layout == "L3":
        # write/restore roots of the legacy commands that run without an installation (adopt/migrate stages and batch rollback)
        os.makedirs(dst + "/spec/audits", exist_ok=True)
        if os.path.isdir(dst + "/spec/audits/GOVERNANCE-ADOPTION"):
            shutil.move(dst + "/spec/audits/GOVERNANCE-ADOPTION", dst + "/spec/audits/ADOPTION")
        open(dst + "/spec/audits/GOVERNANCE-ADOPTION", "w").write(SENT + "\n")
        os.makedirs(dst + "/.governance-runtime", exist_ok=True)
        open(dst + "/.governance-runtime/migration", "w").write(SENT + "\n")
        occupied += ["spec/audits/GOVERNANCE-ADOPTION (file)", ".governance-runtime/migration (tracked file)"]
        git(dst, "add", "-f", ".governance-runtime/migration")
    else:
        # ablation: no occupation of the no-install roots, with legacy adoption residue left on this working copy
        b1 = dst + "/.governance-runtime/migration/batch-1"
        os.makedirs(b1 + "/files/spec/decisions", exist_ok=True)
        os.makedirs(b1 + "/files/product", exist_ok=True)
        json.dump({"moves": [], "created": [], "touched": []}, open(b1 + "/batch.json", "w"))
        open(b1 + "/files/spec/decisions/RESIDUE-RESTORED.yaml", "w").write("id: RESIDUE\n")
        open(b1 + "/files/product/residue.md", "w").write("residue\n")
    git(dst, "add", "-A"); git(dst, "commit", "-q", "-m", "rot-1 revision-3 layout " + layout)
    info.update({"description": ("revision 3" if layout == "L3" else "ABLATION of revision 3 (no occupation of the no-install roots; legacy adoption residue present)")
                 + ": RoT-1 authority under governance/trust/, overlay relocated to governance/overlay/, views to governance/views/; legacy update snapshot .governance-runtime/update/4.1.5/ left in place (not quarantined)",
                 "occupied": occupied, "overlay": "governance/overlay"})
    return dst, info


# ------------------------------------------------------------------------------------------------ invocation synthesis
def value_for(path, opt_or_arg, fx, scratch, own_version):
    n = opt_or_arg.upper()
    p = " ".join(path)
    if n == "GATE":
        return fx["GATE"]
    if n == "ID":
        if path[0] == "cit":
            return fx["CIT"]
        if path[0] == "gate":
            return fx["GATE"]
        if path[0] == "handoff":
            return fx["HANDOFF"]
        return fx["TASK"]
    table = {"STATUS": "IN_PROGRESS", "OPTION": "A", "BATCH": "1", "SOURCE": f"{REPO}/release/releases/{own_version}", "LESSON": "L-0001",
             "PACKET": fx["PACKET"], "DESTINATION": os.path.join(scratch, "fixtures", "upstream-dest"), "OBJECTIVE": "p3 objective",
             "QUESTION": "p3 question?", "NEXT_ACTION": "gov continue", "PROPOSAL": "p3 proposal", "NAME": "p3r3", "ALIAS": "p3-alias",
             "TEXT": "create a task", "QUERY": MARK, "REASON": "p3", "FIELDS": "{}", "REPORT": fx["REPORT"], "FILE": fx["RETURN"],
             "CAPABILITY": "code_intel", "TO_ROLE": "backend-engineer", "TASK": fx["TASK"], "FEATURE": "FEAT-0001", "NODE": fx["TASK"],
             "SEEDS": fx["TASK"], "CANDIDATE": "hashed-ngram", "CANDIDATES": "hashed-ngram", "PLUGIN": "p-probe", "INPUTS": "{}",
             "PLUGIN_ID": "p-probe", "POLICY": "SECURITY_POLICY", "DIR": f"{REPO}/release/releases/{own_version}", "WHAT": "governance",
             "MANIFEST": fx["MANIFEST"], "TARGETS": fx["TASK"], "TRIGGER": "editorial", "TITLE": "p3", "CLASS": "documentation",
             "VERDICT": "MIGRATION_PLAN_APPROVED", "RATIONALE": "p3", "BY": "human", "METHOD": "human", "NOTE": "p3", "NOTES": "p3",
             "RADIUS": "R1", "RECORD": "{}", "ATTRS": "{}", "STEP": "p3", "TESTS_STATUS": "passed", "UTILISATION": "0.9", "OPS": "99",
             "K": "8", "ROUTE": "lexical", "DEPTH": "1", "HELDOUT": "governance/tests/memory/heldout.yaml", "RESEARCH": "RES-0001",
             "INBOX": os.path.join(scratch, "fixtures", "inbox"), "PROPOSALS": os.path.join(scratch, "fixtures", "proposals"),
             "OUT": os.path.join(scratch, "fixtures", "release-out"), "CERTIFICATION": "READY_FOR_INDEPENDENT_OS_VERIFICATION",
             "EVIDENCE": "p3", "CANONICAL": REPO, "INTENT": "p3 intent", "DEPS": fx["TASK"], "ALLOWED": "docs/**",
             "REVIEWER_SESSION": "S-rev", "REVIEWER_ROLE": "migration-reviewer", "VERIFIER_ROLE": "migration-verifier",
             "APPROVED_BY": "owner", "GATE_ANSWER": "yes", "OP": "serve"}
    if n == "DESCRIPTOR":
        return fx["PLUGIN_DESCRIPTOR"] if path[0] == "plugins" else fx["TOOL_DESCRIPTOR"]
    if n == "ID" and path == ["capabilities", "serve-embed"]:
        return "p3"
    return table.get(n, "p3")


def variants(leaf, fx, scratch, own_version):
    path = leaf["path"]
    base = list(path)
    for a in leaf["args"]:
        if a["required"]:
            base.append(value_for(path, a["name"], fx, scratch, own_version))
    for o in leaf["options"]:
        if o["required"]:
            base += [o["long"], value_for(path, o["value"], fx, scratch, own_version)]
    out = [("base", base)]
    for a in leaf["args"]:
        if not a["required"]:
            out.append((f"arg:{a['name']}", base + [value_for(path, a["name"], fx, scratch, own_version)]))
    for o in leaf["options"]:
        if not o["required"]:
            if o["value"] is None:
                out.append((f"flag:{o['long']}", base + [o["long"]]))
            elif o["long"] in ("--source", "--batch", "--reason", "--by", "--method", "--status", "--execute", "--force"):
                out.append((f"opt:{o['long']}", base + [o["long"], value_for(path, o["value"], fx, scratch, own_version)]))
    # destructive combinations the flags alone do not reach
    src = f"{REPO}/release/releases/{own_version}"
    older = {"4.1.2": "4.1.2", "4.1.3": "4.1.2", "4.1.4": "4.1.3", "4.1.5": "4.1.4"}[own_version]
    p = " ".join(path)
    extra = {
        "update": [["update", "--apply", "--approve", "--source", src], ["update", "--apply", "--approve", "--source", f"{REPO}/release/releases/{older}"],
                   ["update", "--rollback", "--reason", "p3"], ["update", "--check", "--source", src]],
        "init": [["init", "--force", "--source", src, "--name", "p3r3", "--skip-index"], ["init", "--force", "--name", "p3r3", "--skip-index"],
                 ["init", "--source", src, "--name", "p3r3", "--skip-index"]],
        "kernel reinstall": [["kernel", "reinstall", "--source", src]],
        "adopt migrate": [["adopt", "migrate", "--batch", "0", "--source", src, "--name", "p3r3", "--alias", "p3a"], ["adopt", "migrate", "--batch", "1"],
                          ["adopt", "migrate", "--batch", "2", "--gate-answer", "yes"]],
        "migrate migrate": [["migrate", "migrate", "--batch", "0", "--source", src, "--name", "p3r3", "--alias", "p3a"], ["migrate", "migrate", "--batch", "1"]],
        "adopt rollback": [["adopt", "rollback", "--batch", "0"], ["adopt", "rollback", "--batch", "2"]],
        "migrate rollback": [["migrate", "rollback", "--batch", "0"]],
        "tools install": [["tools", "install", "--descriptor", fx["TOOL_DESCRIPTOR"], "--execute"]],
        "cit execute": [["cit", "execute", fx["CIT"]]],
        "cit rollback": [["cit", "rollback", fx["CIT"], "--reason", "p3"]],
        "decide": [["decide", fx["GATE"], "--option", "A", "--by", "owner"]],
        "memory select": [["memory", "select", "hashed-ngram", "--by", "owner"]],
        "recover": [["recover"]],
        "upstream submit": [["upstream", "submit", fx["PACKET"], "--destination", os.path.join(scratch, "fixtures", "upstream-dest"), "--approved-by", "owner"]],
        "memory heldout-starter": [["memory", "heldout-starter", "--force"]],
        "lessons cluster": [["lessons", "cluster", "--write"]],
        "kernel override": [["kernel", "override", "--reason", "p3"]],
        "capabilities invoke": [["capabilities", "invoke", "--plugin", "p-probe", "--inputs", json.dumps({"path": "src/x.py", "content": "def f():\n  return 1\n"})]],
    }.get(p, [])
    seen = {tuple(v) for _, v in out}
    for i, e in enumerate(extra):
        if tuple(e) not in seen:
            out.append((f"combo:{i}", e))
            seen.add(tuple(e))
    dedup, seen2 = [], set()
    for name, v in out:
        if tuple(v) not in seen2:
            dedup.append((name, v))
            seen2.add(tuple(v))
    return dedup


# ------------------------------------------------------------------------------------------------ digests
EXCL_TOP = {".git", ".governance-runtime"}


def file_map(root, sub=None, exclude_top=EXCL_TOP):
    base = os.path.join(root, sub) if sub else root
    m = {}
    if not os.path.lexists(base):
        return {"<absent>": ""}
    if not os.path.isdir(base) or os.path.islink(base):
        st = os.lstat(base)
        return {".": ("link:" + os.readlink(base)) if os.path.islink(base) else ("file:" + hashlib.sha256(open(base, "rb").read()).hexdigest())}
    for dp, dns, fns in os.walk(base):
        rel_dp = os.path.relpath(dp, base)
        if rel_dp == ".":
            dns[:] = sorted(d for d in dns if not (sub is None and d in exclude_top))
        else:
            dns.sort()
        m[rel_dp + "/"] = "dir"
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, base)
            if os.path.islink(p):
                m[rel] = "link:" + os.readlink(p)
            elif os.path.isfile(p):
                m[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
            else:
                m[rel] = "special"
    return m


def digest(m):
    return hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest()


def git_state(root):
    def g(*a):
        r = subprocess.run(["git", *a], cwd=root, capture_output=True, text=True)
        return r.stdout
    return {"head": g("rev-parse", "HEAD").strip(), "refs": hashlib.sha256(g("for-each-ref", "--format=%(refname) %(objectname)").encode()).hexdigest()[:16],
            "staged": hashlib.sha256(g("ls-files", "-s").encode()).hexdigest()[:16], "stash": g("stash", "list").strip()}


def changed(a, b):
    ks = set(a) | set(b)
    return sorted(k for k in ks if a.get(k) != b.get(k))



# ------------------------------------------------------------------------------------------------ stateful chains
def chains_for(bname, fx, scratch, info):
    src = f"{REPO}/release/releases/{bname}"
    q = json.dumps({"options": [{"id": "A", "description": "yes"}, {"id": "B", "description": "no"}], "impact_radius": "R1", "confidence": 0.9, "reversibility": "reversible"})
    mf = os.path.join(scratch, "fixtures", f"cit-manifest-{info['layout']}.json")
    if info["layout"] == "L0":
        targets = [{"op": "write_file", "path": "governance/project/DATA_SENSITIVITY.yaml", "content": "schema_version: 1.0.0\nclassifications: []\n"}]
    else:
        targets = [{"op": "write_file", "path": "governance/overlay/DATA_SENSITIVITY.yaml", "content": "schema_version: 1.0.0\nclassifications: []\n"},
                   {"op": "write_file", "path": "governance/trust/kernel/policies/SECURITY_POLICY.yaml", "content": "policy: SECURITY_POLICY\nnever_index_classes: []\n"},
                   {"op": "delete_file", "path": "governance/trust/framework.lock"}]
    json.dump(targets, open(mf, "w"))
    ch = {
        "adoption": [["adopt", "baseline"], ["adopt", "inventory"], ["adopt", "classify"], ["adopt", "map"], ["adopt", "plan"], ["adopt", "test-design"],
                     ["adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED"], ["adopt", "migrate", "--batch", "0", "--source", src, "--name", "p3r3", "--alias", "p3a"],
                     ["adopt", "migrate", "--batch", "1"], ["adopt", "migrate", "--batch", "2"], ["adopt", "verify-migration", "--verdict", "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD"],
                     ["adopt", "extract-legacy"], ["adopt", "build-memory"], ["adopt", "verify-memory", "--verdict", "MEMORY_ACCEPTED"], ["adopt", "audit"],
                     ["adopt", "rollback", "--batch", "2"], ["adopt", "rollback", "--batch", "1"], ["adopt", "rollback", "--batch", "0"]],
        "update": [["update", "--check", "--source", src], ["update", "--apply", "--source", src], ["gate", "present", "{gate}"], ["decide", "{gate}", "--option", "A", "--by", "owner"],
                   ["update", "--apply", "--approve", "--source", src], ["update", "--rollback", "--reason", "p3"]],
        "gate": [["gate", "create", "--question", "p3 chain gate?", "--fields", q], ["gate", "present", "{id}"], ["decide", "{id}", "--option", "A", "--by", "owner"], ["gate", "revoke", "{id}", "--reason", "p3"]],
        "cit": [["cit", "propose", "--proposal", "p3 chain change", "--trigger", "editorial", "--targets", fx["TASK"], "--manifest", mf], ["cit", "simulate", "{id}"],
                ["cit", "approve", "{id}", "--by", "orchestrator", "--method", "auto"], ["cit", "execute", "{id}"], ["cit", "rollback", "{id}", "--reason", "p3"]],
        "task": [["task", "create", "--objective", "p3 chain", "--class", "documentation", "--status", "READY"], ["task", "claim", "{id}"], ["task", "status", "{id}", "IN_PROGRESS"],
                 ["task", "close", "{id}", "--report", fx["REPORT"], "--force"]],
        "init_then_use": [["init", "--force", "--source", src, "--name", "p3r3", "--skip-index"], ["kernel", "verify"], ["rebuild-memory"], ["memory", "query", MARK]],
        "reinstall_then_use": [["kernel", "reinstall", "--source", src], ["kernel", "verify"], ["task", "create", "--objective", "after reinstall", "--class", "documentation"]],
        "recover_twice": [["recover"], ["recover"]],
        "plugins_then_rebuild": [["plugins", "register", "--descriptor", fx["PLUGIN_DESCRIPTOR"]], ["capabilities", "invoke", "--plugin", "p-probe", "--inputs", "{}"], ["rebuild-memory"]],
        "tools_install_execute": [["tools", "install", "--descriptor", fx["TOOL_DESCRIPTOR"], "--execute"], ["tools", "registry"], ["adapters", "generate"]],
    }
    return ch


def result_id(d):
    r = d.get("result") or {}
    for k in ("id", "gate", "human_gate"):
        v = r.get(k)
        if isinstance(v, str):
            return v
        if isinstance(v, dict) and isinstance(v.get("id"), str):
            return v["id"]
    det = ((d.get("error") or {}).get("details") or {}) if isinstance(d.get("error"), dict) else {}
    return det.get("gate") if isinstance(det.get("gate"), str) else None


def run_chain(job):
    scratch, layout_dir, info, bname, binary, name, steps, fx = job
    tag = re.sub(r"[^A-Za-z0-9_.-]", "_", f"chain-{info['layout']}-{bname}-{name}")
    c = os.path.join(scratch, "runs", tag)
    shutil.copytree(layout_dir, c, symlinks=True)
    env = child_env(scratch, tag)
    start = {"tree": file_map(c), "git": git_state(c)}
    last_id, gate_id, out = None, None, []
    for st in steps:
        argv = [x.replace("{id}", last_id or fx["TASK"]).replace("{gate}", gate_id or fx["GATE"]) for x in st]
        r = gov(binary, c, argv, env)
        rid = result_id(r)
        if rid and st[0] in ("gate", "cit", "task") and st[1] in ("create", "propose"):
            last_id = rid
        if st[0] == "update" and rid:
            gate_id = rid
        now = {"tree": file_map(c), "git": git_state(c)}
        out.append({"argv": argv, "ok": r.get("ok"), "code": code(r), "tree_changed_since_chain_start": digest(start["tree"]) != digest(now["tree"]),
                    "git_changed_since_chain_start": start["git"] != now["git"], "changed_paths": changed(start["tree"], now["tree"])[:25]})
    ov = os.path.join(c, info["overlay"], "DATA_SENSITIVITY.yaml")
    try:
        cls = any(x.get("pattern") == "product/restricted-plan.md" for x in (yaml.safe_load(open(ov)).get("classifications") or []))
    except Exception:
        cls = None
    return {"layout": info["layout"], "binary": bname, "chain": name, "steps": out, "classification_survives": cls,
            "any_tree_change": any(s["tree_changed_since_chain_start"] for s in out), "any_git_change": any(s["git_changed_since_chain_start"] for s in out),
            "plugin_or_tool_marker": os.path.exists(env["P3_MARKER"])}


# ------------------------------------------------------------------------------------------------ one run
def run_one(job):
    scratch, layout_dir, info, bname, binary, variant, argv, fx = job
    tag = f"{info['layout']}-{bname}-{'_'.join(argv[:3])}-{variant}".replace("/", "_").replace(" ", "_")[:120]
    tag = re.sub(r"[^A-Za-z0-9_.:-]", "_", tag) + "-" + hashlib.sha256(json.dumps(argv).encode()).hexdigest()[:8]
    c = os.path.join(scratch, "runs", tag)
    shutil.copytree(layout_dir, c, symlinks=True)
    env = child_env(scratch, tag)
    before = {"tree": file_map(c), "gov": file_map(c, "governance"), "spec": file_map(c, "spec"), "rt": file_map(c, ".governance-runtime"), "git": git_state(c)}
    r = gov(binary, c, argv, env)
    after = {"tree": file_map(c), "gov": file_map(c, "governance"), "spec": file_map(c, "spec"), "rt": file_map(c, ".governance-runtime"), "git": git_state(c)}
    ov = os.path.join(c, info["overlay"], "DATA_SENSITIVITY.yaml")
    try:
        ds = yaml.safe_load(open(ov))
        cls = any(x.get("pattern") == "product/restricted-plan.md" for x in (ds.get("classifications") or []))
    except Exception:
        cls = None
    row = {"layout": info["layout"], "binary": bname, "command": " ".join(argv[:2]) if len(argv) > 1 and not argv[1].startswith("-") and argv[0] not in ("decide", "intent", "verify", "mcp") else argv[0],
           "variant": variant, "argv": argv, "rc": r["_rc"], "secs": r["_secs"], "ok": r.get("ok"), "code": code(r),
           "governance_changed": digest(before["gov"]) != digest(after["gov"]), "spec_changed": digest(before["spec"]) != digest(after["spec"]),
           "tree_changed_excl_git_runtime": digest(before["tree"]) != digest(after["tree"]), "git_changed": before["git"] != after["git"],
           "runtime_changed": digest(before["rt"]) != digest(after["rt"]), "classification_survives": cls,
           "legacy_update_snapshot_present_after": os.path.exists(c + "/.governance-runtime/update/4.1.5/snapshot.json"),
           "changed_paths": changed(before["tree"], after["tree"])[:25], "runtime_changed_paths": changed(before["rt"], after["rt"])[:10],
           "raw_tail": (r.get("raw") or "")[-160:] if "raw" in r else None}
    row["plugin_or_tool_marker_grew"] = os.path.exists(env["P3_MARKER"])
    if info["layout"] != "L0" and (row["tree_changed_excl_git_runtime"] or row["git_changed"]):
        v = gov(binary, c, ["kernel", "verify"], env)
        row["old_binary_kernel_verify_after"] = {"ok": v.get("ok"), "result_ok": (v.get("result") or {}).get("ok"), "code": code(v)}
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--layouts", default="L0,L3,L3A")
    ap.add_argument("--binaries", default="4.1.2,4.1.3,4.1.4,4.1.5")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    scratch = os.path.abspath(a.scratch)
    os.makedirs(scratch, exist_ok=False)
    bins = {v: os.path.join(LEGACY, f"gov-{v}") for v in a.binaries.split(",")}
    out = {"probe": "P3r3", "scratch": scratch, "repo": REPO, "sentinel": SENT,
           "binaries": {v: {"path": p, "version": subprocess.run([p, "--version"], capture_output=True, text=True).stdout.strip(),
                            "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest()} for v, p in bins.items()}}
    env0 = child_env(scratch, "register")
    out["registers"] = {v: register(p, env0) for v, p in bins.items()}
    fx = {}
    base, b = build_base(scratch, os.path.join(LEGACY, "gov-4.1.5"), fx)
    out["base"] = b
    layouts = {}
    for L in a.layouts.split(","):
        d, info = to_layout(scratch, base, L)
        info["tree_digest"] = digest(file_map(d))
        info["governance_entries"] = sorted(os.listdir(d + "/governance"))
        layouts[L] = (d, info)
    out["layouts"] = {L: i for L, (_, i) in layouts.items()}
    jobs = []
    for L, (d, info) in layouts.items():
        for bname, binary in bins.items():
            for leaf in out["registers"][bname]["leaves"]:
                for vname, argv in variants(leaf, fx, scratch, bname):
                    jobs.append((scratch, d, info, bname, binary, vname, argv, fx))
    if a.limit:
        jobs = jobs[: a.limit]
    out["job_count"] = len(jobs)
    rows = []
    with cf.ProcessPoolExecutor(max_workers=a.workers) as ex:
        for row in ex.map(run_one, jobs, chunksize=1):
            rows.append(row)
            if len(rows) % 100 == 0:
                print(f"{len(rows)}/{len(jobs)}", file=sys.stderr, flush=True)
    out["rows"] = rows
    cjobs = [(scratch, d, info, bname, binary, n, steps, fx) for L, (d, info) in layouts.items() for bname, binary in bins.items()
             for n, steps in chains_for(bname, fx, scratch, info).items()]
    with cf.ProcessPoolExecutor(max_workers=a.workers) as ex:
        out["chains"] = list(ex.map(run_chain, cjobs, chunksize=1))
    summ = {}
    for L in layouts:
        for bname in bins:
            rs = [r for r in rows if r["layout"] == L and r["binary"] == bname]
            summ[f"{L}/{bname}"] = {
                "leaf_commands": len(out["registers"][bname]["leaves"]), "invocations": len(rs),
                "governance_changed": sum(r["governance_changed"] for r in rs), "spec_changed": sum(r["spec_changed"] for r in rs),
                "tree_changed_excl_git_runtime": sum(r["tree_changed_excl_git_runtime"] for r in rs), "git_changed": sum(r["git_changed"] for r in rs),
                "runtime_changed": sum(r["runtime_changed"] for r in rs), "classification_lost": sum(r["classification_survives"] is False for r in rs),
                "ok_true": sum(bool(r["ok"]) for r in rs), "plugin_or_tool_executed": sum(r["plugin_or_tool_marker_grew"] for r in rs),
                "timeouts": sum(r["rc"] == -999 for r in rs)}
    out["summary"] = summ
    l3 = [r for r in rows if r["layout"] == "L3"]
    out["property_L3"] = {"statement": "for every pre-RoT binary 4.1.2-4.1.5 and every invocation derived from its own register, no byte outside .git/.governance-runtime changes and .git is unchanged (governance/, spec/ and every other tracked path)",
                          "invocations": len(l3), "violations": [{k: r[k] for k in ("binary", "argv", "code", "changed_paths")} for r in l3 if r["tree_changed_excl_git_runtime"] or r["git_changed"]],
                          "holds": all(not (r["tree_changed_excl_git_runtime"] or r["git_changed"]) for r in l3)}
    l3c = [c for c in out["chains"] if c["layout"] == "L3"]
    out["property_L3"]["chains"] = len(l3c)
    out["property_L3"]["chain_violations"] = [{"binary": c["binary"], "chain": c["chain"], "steps": [s for s in c["steps"] if s["tree_changed_since_chain_start"] or s["git_changed_since_chain_start"]]} for c in l3c if c["any_tree_change"] or c["any_git_change"]]
    out["property_L3"]["holds"] = out["property_L3"]["holds"] and not out["property_L3"]["chain_violations"]
    out["chain_summary"] = {f"{c['layout']}/{c['binary']}/{c['chain']}": {"any_tree_change": c["any_tree_change"], "any_git_change": c["any_git_change"], "classification_survives": c["classification_survives"],
                            "steps_ok": sum(bool(s["ok"]) for s in c["steps"]), "steps": len(c["steps"])} for c in out["chains"]}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
