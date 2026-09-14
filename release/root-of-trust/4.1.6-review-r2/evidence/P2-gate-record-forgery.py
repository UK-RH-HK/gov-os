#!/usr/bin/env python3
"""P2 — Is the OP-3 mode A Human Decision Gate a boundary against a repository writer (A2)? Scratch only.

RoT-1 revision 2 uses a gate bound to statement digest(s) as the authorisation for every production install and update
(mode A), for downgrades (`19` E9, `20` §4), for recovery that downgrades (`20` §5), for computed weakenings (`19` §9),
for HINT_MISMATCH (`17` §7) and as the stated bound of residual RS-1 (`17` §15). D-0008 rule (18) says Git-tracked gate
records are "never the basis of a currency, freshness or downgrade decision against a repository writer".

This probe checks what a gate record is today: the 4.1.5 binary consumes `spec/decisions/HDG-*.yaml` as data. A2 edits
the pending gate record in a commit (no `gov gate present`, no `gov decide`) and the victim's `update --apply --approve`
proceeds. Revision 2 adds a digest binding but does not change where the record lives or who can write it (`02` §4
lists gate records as GovernedFs-written project state, outside the Protected Path Set).
"""
import glob, json, os, subprocess, tempfile
import yaml

REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"
GOV = os.environ.get("GOV", REPO + "/target/release/gov")
SCRATCH = os.environ.get("GOV_REVIEW_SCRATCH") or tempfile.gettempdir()
S = tempfile.mkdtemp(prefix="p2-gate-", dir=SCRATCH)
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV["GOV_KERNEL_CACHE"] = S + "/cache"


def gov(root, *a, role="orchestrator"):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-p2", "--role", role, *a], env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-300:], "stderr": r.stderr[-300:]}


def git(root, *a, who="victim"):
    subprocess.run(["git", "-c", f"user.name={who}", "-c", f"user.email={who}@x", *a], cwd=root, check=True, capture_output=True)


code = lambda d: (d.get("error") or {}).get("code")
out = {"scratch": S}
for label, forge in (("control_no_forgery", False), ("a2_forged_gate_record", True)):
    root = f"{S}/{label}"
    os.makedirs(root)
    git(root, "init", "-q")
    git(root, "commit", "-q", "--allow-empty", "-m", "i")
    init = gov(root, "init", "--source", REPO + "/release/releases/4.1.4", "--name", "p2", "--skip-index")
    git(root, "add", "-A"); git(root, "commit", "-q", "-m", "installed 4.1.4")
    first = gov(root, "update", "--apply", "--source", REPO + "/release/releases/4.1.5")
    gid = ((first.get("error") or {}).get("details") or {}).get("gate")
    git(root, "add", "-A"); git(root, "commit", "-q", "-m", "gate raised")
    rec = {}
    if forge and gid:
        path = next(iter(glob.glob(f"{root}/spec/decisions/{gid}.*")), None)
        text = open(path).read()
        if path.endswith(".md"):
            fm, body = text[4:].split("\n---", 1)
            data = yaml.safe_load(fm)
        else:
            data, body = yaml.safe_load(text), None
        data.update({"gate_status": "ANSWERED", "presented_in_chat": True,
                     "answer": {"option": "A", "by": "product-owner", "by_kind": "human", "acting_role": "human", "at": "2026-09-14T00:00:00Z", "rationale": "lgtm"}})
        if body is None:
            yaml.safe_dump(data, open(path, "w"), sort_keys=False)
        else:
            open(path, "w").write("---\n" + yaml.safe_dump(data, sort_keys=False) + "---" + body)
        git(root, "add", "-A"); git(root, "commit", "-q", "-m", "docs: tidy", who="a2-collaborator")
        rec = {"forged_record": os.path.relpath(path, root), "gov_gate_present_run": False, "gov_decide_run": False}
    apply = gov(root, "update", "--apply", "--approve", "--source", REPO + "/release/releases/4.1.5")
    res = apply.get("result") or {}
    ver = gov(root, "kernel", "trust")
    out[label] = {"init_ok": init.get("ok"), "first_apply_code": code(first), "gate": gid, **rec,
                  "apply_ok": apply.get("ok"), "apply_code": code(apply), "applied": res.get("applied"), "reason": res.get("reason"),
                  "installed_version_after": ((ver.get("result") or {}).get("trust") or {}).get("installed_version")}
print(json.dumps(out, indent=2))
