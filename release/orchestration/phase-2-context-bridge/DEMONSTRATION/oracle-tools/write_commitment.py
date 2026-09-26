#!/usr/bin/env python3
"""Write a held-out oracle's sha256 commitment (run BR-AR-0021, REPAIR-1 node R1-TA2).

DEMONSTRATION_DESIGN.md section 1: the only thing committed before a demonstration run is
`{oracle_sha256, author_run, author_model, written_at, schema: govbridge-oracle/1}`; the grader refuses an oracle
whose sha256 differs. This writes exactly that record (plus an optional `supersedes_for_run_N` pointer) to the
commitment file named on the command line, computing the digest over the oracle's raw bytes.

It never echoes oracle content and never writes the oracle's location anywhere: the oracle path is read, hashed and
forgotten; the output record carries only the digest and the metadata given as arguments; stdout prints only the
digest and the commitment file's repository-relative name. Stdlib + PyYAML only; generic.
"""
import argparse
import datetime
import hashlib
import os
import sys

import yaml


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("oracle", help="the sealed oracle file (read only; its path is never written or printed)")
    ap.add_argument("commitment", help="the commitment YAML to write")
    ap.add_argument("--author-run", required=True)
    ap.add_argument("--author-model", required=True)
    ap.add_argument("--schema", default="govbridge-oracle/1")
    ap.add_argument("--supersedes-key", default=None, help="e.g. supersedes_for_run_2")
    ap.add_argument("--supersedes-value", default=None, help="what the new commitment supersedes for that run")
    ap.add_argument("--written-at", default=None, help="ISO-8601 UTC; default: now")
    args = ap.parse_args()
    with open(args.oracle, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    rec = {
        "oracle_sha256": digest,
        "author_run": args.author_run,
        "author_model": args.author_model,
        "written_at": args.written_at
        or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "schema": args.schema,
    }
    if args.supersedes_key:
        rec[args.supersedes_key] = args.supersedes_value
    with open(args.commitment, "w", encoding="utf-8") as f:
        yaml.safe_dump(rec, f, sort_keys=False, allow_unicode=True, width=100)
    print(f"oracle_sha256: {digest}")
    print(f"commitment written: {os.path.basename(args.commitment)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
