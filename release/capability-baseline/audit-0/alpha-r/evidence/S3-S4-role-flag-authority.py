#!/usr/bin/env python3
"""Is the caller-declared acting role (--role) enforced on the privileged init / adopt paths?
init --force requires AUTHORITY_POLICY install_kernel (L4); adopt migrate/extract-legacy require migrate_execute (L3);
adopt build-memory requires build_memory (L2). Compare `--role <low role>` with `GOV_ROLE=<low role>`.
Run: PROBE_TMP=<scratch> python3 S3-S4-role-flag-authority.py
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
sb = Sandbox("roleflag")
p = sb.new_repo("r", {"README.md": "# r\n"})
sb.gov("init", "--name", "r", "--alias", "ra", "--skip-index", cwd=p, quiet=True)
def run(label, *args, role=None, env=None):
    o = sb.gov(*args, cwd=p, role=role, env=env, quiet=True)
    print(f"{label:70s} ->", "ok" if o["ok"] else f"REFUSED {err(o)}: {str(o['error']['message'])[:110]}")
print("## [R1] gov init --force (install_kernel requires L4)")
run("[R1] --role independent-auditor (L0) init --force", "init", "--force", "--name", "r", "--alias", "ra", "--skip-index", role="independent-auditor")
run("[R1] GOV_ROLE=independent-auditor init --force", "init", "--force", "--name", "r", "--alias", "ra", "--skip-index", env={"GOV_ROLE": "independent-auditor"})
run("[R1] control: --role independent-auditor kernel reinstall (same install_kernel class)", "kernel", "reinstall", role="independent-auditor")
q = sb.new_repo("q", {"README.md": "# q\n", "src/a.py": "def f():\n    return 1\n", "docs/b.md": "# spec\nRequirement: the system shall work.\n"})
def A(label, *args, role=None, env=None, s=None):
    o = sb.gov("adopt", *args, cwd=q, role=role, env=env, session=s, quiet=True)
    print(f"{label:70s} ->", "ok" if o["ok"] else f"REFUSED {err(o)}: {str(o['error']['message'])[:110]}")
    return o
print("\n## [R2] gov adopt stages under a declared low-authority role")
for st in ["baseline", "inventory", "classify", "map", "plan", "test-design"]:
    A(f"[R2] --role independent-auditor adopt {st}", st, role="independent-auditor", s="S-p")
A("[R2] adopt review", "review", "--verdict", "MIGRATION_PLAN_APPROVED", "--reviewer-session", "S-r", s="S-r")
A("[R2] --role independent-auditor (L0) adopt migrate --batch 0 (kernel install, migrate_execute L3)", "migrate", "--batch", "0", role="independent-auditor", s="S-e")
A("[R2] --role independent-auditor (L0) adopt migrate (all batches)", "migrate", role="independent-auditor", s="S-e")
A("[R2] GOV_ROLE=independent-auditor adopt migrate --batch 2", "migrate", "--batch", "2", env={"GOV_ROLE": "independent-auditor"}, s="S-e")
A("[R2] verify-migration", "verify-migration", s="S-v")
A("[R2] --role independent-auditor (L0) adopt extract-legacy (migrate_execute L3)", "extract-legacy", role="independent-auditor", s="S-m")
print("\nDONE")
