"""Call gov.records.records and edges on a root with whatever gov PYTHONPATH gives (W2-87 lead probe)."""
import sys
import traceback
from pathlib import Path

import gov
from gov import records

print(gov.__file__)
try:
    print(len(records.records(Path(sys.argv[1]))))
    print(len(records.edges(Path(sys.argv[1]), type="SUPERSEDES")))
except Exception:
    traceback.print_exc()
