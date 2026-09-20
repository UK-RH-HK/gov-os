#!/usr/bin/env python3
"""P2-AR-0053 — R4-O1 probe: does a tool installation made inside a claimed task close?

P2-AR-0043 closed INT3-O1 (a plugin registration inside a claimed task) and recorded R4-O1 as the adjacent, unchecked
path: `gov tools install` writes `governance/project/tools/<id>.yaml`, a governed file under the same project-plugin /
OS-managed prefixes. This probe establishes the behaviour, it does not repair anything and it grades no one.

Three observations, each on its own fresh project:

  O1  an installation approved through its own tool-installation gate, made inside a claimed tooling task whose
      allowed paths include `governance/project/tools/**`, and the task then closed;
  O2  the same, with the descriptor's path NOT declared in the task's allowed paths;
  O3  the control: the same descriptor installed with no task claimed at all (no close, so nothing to refuse).

For each we print whether the close succeeded, its error code, and the material/undeclared/out-of-scope details, so
the answer to "does a task close treat this write as it treated the plugin descriptor in INT3-O1" is readable.

Usage: GOV_BIN=<gov> WS07R3_SCRATCH=<dir> python3 tools_install_task_close.py
"""
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
WS07 = os.path.join(WT, "release", "capability-baseline", "repair-1", "r3-ws07", "evidence")
sys.path.insert(0, WS07)
import ws07_r3_named_checks as nc  # noqa: E402  (read-only import of WS-7's round-3 probe helper)
import ip_task_close_registration as ip  # noqa: E402  (read-only import of WS-7's IP probe, for its receipt shape)

TOOL = "TOOL-R4O1"
TOOL_PATH = f"governance/project/tools/{TOOL}.yaml"


def tool_descriptor(p, extra=None):
    """A schema-valid tool descriptor whose auto-install conditions cannot all hold (no governed security review),
    so the installation is approved by a presented, owner-answered gate raised for exactly it."""
    d = {"tool_id": TOOL, "name": "r4o1", "type": "CLI", "capabilities": ["lint"], "status": "active",
         "approved_roles": ["tooling-engineer"], "version": "1.0.0", "version_pin": "1.0.0", "license": "MIT",
         "reversible": True, "cost_usd": 0.0, "required_permission_classes": ["READ_REPO"],
         "install_command": ["true"], "uninstall_command": ["true"],
         "health_check": {"kind": "command", "command": ["true"], "expect_exit": 0}}
    d.update(extra or {})
    f = os.path.join(p.base, "tool-descriptor.yaml")
    with open(f, "w") as fh:
        yaml.safe_dump(d, fh, sort_keys=False)
    return f


def install_approved(p, role, descriptor_file, session=None):
    """`gov tools install`; if it raises a gate for exactly this installation, the owner answers A and we install
    again. Every further gate the installation raises is answered the same way (at most four rounds)."""
    seen = []
    for _ in range(4):
        r = p.run(role, "tools", "install", "--descriptor", descriptor_file, session=session)
        res = r.get("result") or {}
        if not r.get("ok"):
            return r, seen
        if res.get("installed"):
            return r, seen
        gate = res.get("human_gate")
        if not gate or gate in seen:
            return r, seen
        seen.append(gate)
        nc.human(p, gate, "A")
    return r, seen


def close_after_install(tag, allowed, declare_tool_path):
    p = nc.new_project(tag)
    p.ok("orchestrator", "rebuild-memory")
    te, s = "tooling-engineer", "S-tool"
    t = p.ok("orchestrator", "task", "create", "--class", "tooling", "--objective",
             "install the r4o1 tool", "--status", "READY", "--allowed", allowed)["id"]
    p.ok(te, "task", "claim", t, session=s)
    df = tool_descriptor(p)
    r, gates = install_approved(p, te, df, session=s)
    res = r.get("result") or {}
    print(f"[{tag}] install ok: {r.get('ok')} installed: {res.get('installed')} "
          f"gates answered: {gates} approval: {json.dumps(res.get('approval'))[:200]}")
    print(f"[{tag}] change_transaction in result: {json.dumps(res.get('change_transaction'))[:300]}")
    print(f"[{tag}] descriptor on disk: {p.exists(TOOL_PATH)}")
    cits = p.ok(te, "cit", "list", session=s)
    print(f"[{tag}] cit list: {json.dumps(cits)[:400]}")
    print(f"[{tag}] working-tree changes during the task:\n" + p.git("status", "--porcelain").stdout)
    p.ok(te, "rebuild-memory", "--incremental", session=s)
    files = ["tools/x.txt"] + ([TOOL_PATH] if declare_tool_path else [])
    p.w("tools/x.txt", "probe\n")
    f = ip.receipt(p, te, s, t, files)
    v = p.run(te, "task", "close", t, "--report", f, session=s)
    err = v.get("error") or {}
    d = err.get("details") or {}
    print(f"[{tag}] close ok: {v.get('ok')} code: {err.get('code')}")
    print(f"[{tag}] refused: {json.dumps(d.get('refused'))[:700]}")
    print(f"[{tag}] accepted: {json.dumps(d.get('accepted'))[:400]}")
    print(f"[{tag}] undeclared: {json.dumps(d.get('undeclared'))} out_of_scope: {json.dumps(d.get('out_of_scope'))}")
    if not v.get("ok"):
        print(f"[{tag}] message: " + (err.get("message") or "")[:600])
    return v


def control_no_task():
    p = nc.new_project("r4o1-control")
    p.ok("orchestrator", "rebuild-memory")
    te = "tooling-engineer"
    df = tool_descriptor(p)
    r, gates = install_approved(p, te, df)
    res = r.get("result") or {}
    print(f"[control] install ok: {r.get('ok')} installed: {res.get('installed')} gates answered: {gates}")
    print(f"[control] descriptor on disk: {p.exists(TOOL_PATH)}")
    print(f"[control] cit list: {json.dumps(p.ok(te, 'cit', 'list'))[:400]}")


def main():
    print(f"# gov {nc.GOV}")
    print("# O1: installation inside a claimed task, tool path declared in the task's allowed paths")
    close_after_install("r4o1-declared", "tools/**,governance/project/tools/**", True)
    print("\n# O2: installation inside a claimed task, tool path NOT declared")
    close_after_install("r4o1-undeclared", "tools/**", False)
    print("\n# O3 (control): the same installation with no task claimed")
    control_no_task()


if __name__ == "__main__":
    main()
