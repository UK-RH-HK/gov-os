"""A stand-in holder of a rebuild lock for the W2-76 tests: ``w2_76_holder.py <lock> <release file> <max seconds>``.

It takes an exclusive ``flock`` on ``<lock>`` (creating it), prints ``held <pid>``, and holds it until
``<release file>`` exists or ``<max seconds>`` pass. It is started by a case as a sibling of the rebuild under test,
never as its ancestor.
"""

import fcntl
import os
import sys
import time

lock, release, limit = sys.argv[1], sys.argv[2], float(sys.argv[3])
handle = open(lock, "a+")
fcntl.flock(handle, fcntl.LOCK_EX)
print(f"held {os.getpid()}", flush=True)
deadline = time.monotonic() + limit
while time.monotonic() < deadline and not os.path.exists(release):
    time.sleep(0.05)
fcntl.flock(handle, fcntl.LOCK_UN)
handle.close()
