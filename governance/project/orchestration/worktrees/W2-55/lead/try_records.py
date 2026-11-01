import sys
import traceback

sys.path.insert(0, sys.argv[1])
from gov import records  # noqa: E402

try:
    known = records.records(sys.argv[2])
    print("records", len(known))
    print("edges", len(records.edges(sys.argv[2], type="SUPERSEDES")))
except Exception:
    traceback.print_exc()
