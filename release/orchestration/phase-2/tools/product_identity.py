#!/usr/bin/env python3
"""Phase 2 candidate identity (non-product tooling).

Prints two deterministic digests for a commit, derived only from Git tree objects:

  product_code_digest   the executable product: runtime, CLI, tests, kernel payload, plugins, migrations,
                        registries, fixtures, shims and the Cargo manifests/lock.
  governed_state_digest the repository's own governed records and normative sources: spec/, docs/, lessons/,
                        change-proposals/, the three governing documents and the Contract v3 owner source.

Two commits with equal product_code_digest carry byte-identical product code, whatever else differs. Contract v3
item 9 ("the exact candidate commit/hash is frozen for qualification") is recorded as commit + both digests.

usage: product_identity.py [<commit>]        (default HEAD)
"""
import hashlib
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

PRODUCT_CODE = [
    "runtime", "cli", "tests", "framework", "capabilities", "migrations", "tools", "fixtures", "bin", "scripts",
    "Cargo.toml", "Cargo.lock",
]
GOVERNED_STATE = [
    "spec", "docs", "lessons", "change-proposals",
    "DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md",
    "GOVERNANCE_OS_ADOPTION_MIGRATION_AND_INDEPENDENT_AUDIT_PROTOCOL_v3.0.md",
    "GOVERNANCE_OS_RELEASE_DISTRIBUTION_ADOPTION_AND_UPSTREAM_LEARNING_PROTOCOL_v1.2.md",
    "Governance_OS_Capability_Acceptance_Contract_v3.md",
]


def object_id(commit, path):
    r = subprocess.run(["git", "-C", ROOT, "rev-parse", f"{commit}:{path}"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else "ABSENT"


def digest(commit, paths):
    lines = [f"{p} {object_id(commit, p)}" for p in paths]
    return hashlib.sha256("\n".join(lines).encode()).hexdigest(), lines


def main():
    commit = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    full = subprocess.run(["git", "-C", ROOT, "rev-parse", commit], capture_output=True, text=True).stdout.strip()
    code, code_lines = digest(full, PRODUCT_CODE)
    gov, gov_lines = digest(full, GOVERNED_STATE)
    print(f"commit: {full}")
    print(f"product_code_digest: {code}")
    print(f"governed_state_digest: {gov}")
    if "-v" in sys.argv:
        for line in code_lines + gov_lines:
            print("  " + line)


if __name__ == "__main__":
    main()
