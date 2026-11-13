"""Child program of the planted A9 cases (S5's over-budget and unmeasured scans, S16's copy step): ``gov`` with the store
hashed the moment its build is done, the copies seen when the build starts, and the scan seam replaceable.

``a9_hash_stores.py <gov arguments...>`` runs the CLI with ``gov.rebuild.command.run`` (which A9 calls in full, I3) wrapped:

- at its entry, the files of ``W2_88_WATCH`` (a JSON list of paths relative to the project) that exist are written on stderr
  as ``copies-at-build: <json>`` (B-1.1: the copies are in place before the build and the queries);
- right after the real rebuild returns, the sha256 of every store file (``store_hash``) is written as one line
  ``store-hash-after-build: <json>``; nothing is changed. The stage then goes on (the scale figures, the proposal, the record);
  the case hashes the same files again once the process has ended and compares the two.

With ``W2_88_SCAN`` set, ``gov.adopt.fabric.vector_scan`` (RV1-2's seam: the semantic route's reply for one question) is
replaced by a stand-in: ``unavailable`` answers ``{"available": False, "reason": "FACET_UNAVAILABLE: planted"}``, ``raises``
raises a ``RuntimeError``, ``slow`` sleeps 0.05 s and answers ``available: True``. Nothing else of the route is touched."""

import json
import os
import sys
import time
from pathlib import Path

import gov.rebuild.command as rebuild
from store_hash import digest

original = rebuild.run


def hashed(root, args, config):
    watch = json.loads(os.environ.get("W2_88_WATCH") or "[]")
    sys.stderr.write("copies-at-build: " + json.dumps(sorted(rel for rel in watch if (Path(root) / rel).is_file())) + "\n")
    result = original(root, args, config)
    sys.stderr.write("store-hash-after-build: " + json.dumps(digest(root), sort_keys=True) + "\n")
    sys.stderr.flush()
    return result


rebuild.run = hashed

scan = os.environ.get("W2_88_SCAN")
if scan:
    from gov.adopt import fabric

    def planted_scan(*arguments, **keywords):
        if scan == "unavailable":
            return {"available": False, "reason": "FACET_UNAVAILABLE: planted"}
        if scan == "raises":
            raise RuntimeError("planted scan failure")
        time.sleep(0.05)
        return {"available": True, "hits": [], "results": []}

    fabric.vector_scan = planted_scan

sys.argv = ["gov", *sys.argv[1:]]
from gov.cli.main import main  # noqa: E402

raise SystemExit(main())
