"""The planted rebuild command (``--rebuild-cmd``): builds the store of the repository it is run in.

``python3 rebuild_stub.py <log>``, run by ``fresh`` in the snapshot's clone: it writes ``.gov-runtime/store.db`` there
(a fingerprints row whose head is the clone's HEAD, which is all the declaration reads) and appends one line to
``<log>`` (the folder it ran in, the head), so a test sees where a rebuild ran. It is never ``gov rebuild`` and reaches
no shared store.
"""
import json
import os
import sqlite3
import subprocess
import sys


def main() -> int:
    log, cwd = sys.argv[1], os.getcwd()
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    os.makedirs(".gov-runtime", exist_ok=True)
    store = os.path.join(".gov-runtime", "store.db")
    if os.path.exists(store):
        os.unlink(store)
    connection = sqlite3.connect(store)
    connection.execute("CREATE TABLE fingerprints (head TEXT NOT NULL, code TEXT, records TEXT, kind TEXT NOT NULL)")
    connection.execute("INSERT INTO fingerprints VALUES (?, ?, ?, ?)", (head, "c0de", "rec0", "rebuild"))
    connection.commit()
    connection.close()
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps({"cwd": os.path.realpath(cwd), "head": head, "argv": sys.argv[1:]}) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
