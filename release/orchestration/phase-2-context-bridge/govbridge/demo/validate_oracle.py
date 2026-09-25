#!/usr/bin/env python3
"""``govbridge demo validate-oracle`` (routed issue TA/BR-AR-0002 OI-3: "demo validate-oracle must agree with
DEMONSTRATION/oracle-tools/check_oracle.py... reuse check_oracle.py by import or subprocess rather than
re-implementing it"). Runs the test-author's own structural checker as a subprocess -- so this command agrees
with it BY CONSTRUCTION, never by a second, possibly-drifting implementation of the same rules (lines on every
code/test anchor; a record_id or section on line-less record/contract/evidence anchors; 40-hex commits;
process/production keys only on both-ways consumer anchors, and everything else ``check_oracle.py`` enforces).

Never reads the oracle's own content directly: only ``check_oracle.py`` does, and its own output never echoes
oracle content (a display name, a sha256, counts and problems located by key path only) -- this wrapper is
therefore safe to run against the real, held-out oracle at grading time, even though I1 itself never sees it
(this command is tested here only against the synthetic fixture oracle, per this run's own scope)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Optional


def _script_path(repo: Optional[str] = None) -> str:
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    return os.path.join(GOV_BRIDGE_DOMAIN, "DEMONSTRATION", "oracle-tools", "check_oracle.py")


def validate_oracle(oracle_path: str, schema_path: Optional[str] = None, queries_path: Optional[str] = None,
                     state_path: Optional[str] = None, display_name: Optional[str] = None) -> dict:
    script = _script_path()
    cmd = [sys.executable, script, oracle_path]
    if schema_path:
        cmd += ["--schema", schema_path]
    if queries_path:
        cmd += ["--queries", queries_path]
    if state_path:
        cmd += ["--state", state_path]
    if display_name:
        cmd += ["--display-name", display_name]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "command": cmd,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "valid": proc.returncode == 0,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.demo.validate_oracle")
    p.add_argument("oracle")
    p.add_argument("--schema")
    p.add_argument("--queries")
    p.add_argument("--state")
    p.add_argument("--display-name")
    p.add_argument("--json", action="store_true", help="print the wrapper's own JSON result instead of "
                                                          "check_oracle.py's plain-text stdout")
    args = p.parse_args(argv)

    result = validate_oracle(args.oracle, schema_path=args.schema, queries_path=args.queries,
                              state_path=args.state, display_name=args.display_name)
    if args.json:
        print(json.dumps(result, indent=1, sort_keys=True))
    else:
        sys.stdout.write(result["stdout"])
        if result["stderr"]:
            sys.stderr.write(result["stderr"])
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
