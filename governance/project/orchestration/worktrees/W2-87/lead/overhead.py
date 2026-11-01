"""Time what W2-87 adds to one retrieve call on this repository: the records and edges read again, the entry
mapping built, the block read. Run with PYTHONPATH set to the head's src."""
import time
from pathlib import Path

from gov import records
from gov.retrieval import authority

root = Path("/home/usain/gov-os-worktrees/W2-87")
for round_ in range(3):
    started = time.perf_counter()
    known, edges = records.records(root), records.edges(root, type=authority.SUPERSEDES)
    t_records = time.perf_counter()
    entry_of = authority.register_entries_of(known, edges, root)
    t_entries = time.perf_counter()
    order = authority.order(root, known, edges, entry_of)
    t_order = time.perf_counter()
    print(f"round {round_}: records+edges {1000 * (t_records - started):.0f} ms, entry mapping "
          f"{1000 * (t_entries - t_records):.0f} ms, block and order {1000 * (t_order - t_entries):.0f} ms, "
          f"total {1000 * (t_order - started):.0f} ms")
