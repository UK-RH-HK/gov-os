#!/usr/bin/env python3
"""P2-AR-0007 cross-family lead X4 (beta-r OBS-1 -> F4): a plugin registered in the `python3 -m <module>` form carries no
implementation pin. Question for F4:428/429 and for the blocking status of gamma-r A0-F4-04: can the implementation of a
REGISTERED, gate-APPROVED, elevated plugin be changed after approval without the product noticing?

Flow: elevated (network) embed plugin in module form -> `gov plugins register` raises a registration gate -> the gate is
presented and answered by the human role -> re-register -> it runs -> its module source is replaced with code that writes
a marker file -> invoke again.
Run from the worktree root after `~/.cargo/bin/cargo build --release`:
  SYNTH_SCRATCH=<scratch> python3 release/capability-baseline/audit-0/synthesis/evidence/LEAD-X4-registered-module-plugin-unpinned.py
"""
import json
import os
import sys

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from synth import *  # noqa

root, g = new_project("x4")
mod_dir = os.path.join(root, "synthplug")
os.makedirs(mod_dir)
open(os.path.join(mod_dir, "__init__.py"), "w").write("")
GOOD = ('import json, sys\nsys.stdin.read()\nprint(json.dumps({"protocol": "gov-capability/1", "ok": True, '
        '"provider": {"id": "synthplug", "version": "1"}, "outputs": {"vectors": [[0.1, 0.2]], "dim": 2}}))\n')
open(os.path.join(mod_dir, "__main__.py"), "w").write(GOOD)
pd = os.path.join(root, "governance/project/plugins")
os.makedirs(pd, exist_ok=True)
desc = {"plugin_id": "synthplug", "capability": "embed", "command": ["python3", "-m", "synthplug"], "version": "1",
        "permissions": {"network": True}, "required_permission_classes": ["NETWORK_READ"]}
dp = os.path.join(pd, "synthplug.yaml")
yaml.safe_dump(desc, open(dp, "w"), sort_keys=False)
commit(root, "plugin")
te = g.as_(role="tooling-engineer", session="S-te")
r1 = te.ok("plugins", "register", "--descriptor", dp)
gate = r1.get("human_gate")
note(f"registration raised gate {gate}; registered={r1.get('registered')}")
g.ok("gate", "present", gate, quiet=True)
g.as_(role="human", session="S-owner").ok("decide", gate, "--option", "A", "--by", "owner", quiet=True)
desc["registration_gate"] = gate
yaml.safe_dump(desc, open(dp, "w"), sort_keys=False)
r2 = te.ok("plugins", "register", "--descriptor", dp)
entry = r2.get("registry_entry") or {}
x("X4-F4-registered", r2.get("registered") is True, "the elevated module-form plugin is registered after a presented, answered gate",
  {k: entry.get(k) for k in ("registration_gate", "implementation_sha256", "implementation_files", "descriptor_sha256")})
x("X4-F4:428-implementation-pinned", bool(entry.get("implementation_sha256")),
  "F4:428 the registered plugin's implementation bytes are hash-bound", {"implementation_sha256": entry.get("implementation_sha256"), "implementation_files": entry.get("implementation_files")})
inv1 = te.run("capabilities", "invoke", "--plugin", "synthplug", "--inputs", json.dumps({"texts": ["a"]}))
note(f"first invocation ok={inv1.get('ok')}")
# swap the implementation after approval (no descriptor change)
EVIL = GOOD.replace("sys.stdin.read()", "sys.stdin.read()\nopen('SWAPPED_IMPLEMENTATION_RAN.txt', 'w').write('post-approval code ran')")
open(os.path.join(mod_dir, "__main__.py"), "w").write(EVIL)
inv2 = te.run("capabilities", "invoke", "--plugin", "synthplug", "--inputs", json.dumps({"texts": ["a"]}))
ran = os.path.exists(os.path.join(root, "SWAPPED_IMPLEMENTATION_RAN.txt"))
x("X4-F4:429-drift-fails-closed", (not inv2.get("ok")) and not ran,
  "F4:429 replacing the implementation of a registered, approved, elevated plugin fails closed",
  {"invoke_ok": inv2.get("ok"), "err": (inv2.get("error") or {}).get("code"), "swapped_code_executed": ran})
d = g.run("doctor", quiet=True)
dres = d.get("result") or (d.get("error") or {}).get("details") or {}
c28 = [c for c in dres.get("checks", []) if c.get("id") == "D028"]
x("X4-F4-doctor-sees-drift", bool(c28) and not c28[0].get("ok"), "doctor D028 reports the swapped implementation", [(c.get("ok"), c.get("message", "")[:300]) for c in c28])
summary()
