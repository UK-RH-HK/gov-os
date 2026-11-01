"""Time two context() computations for each of the first N project tickets, with the code at sys.argv[1]."""
import sys
import time

sys.path.insert(0, sys.argv[1])
from gov.context import context  # noqa: E402
from gov.context.context_check import project_tickets  # noqa: E402

root, count = sys.argv[2], int(sys.argv[3])
tickets, unheld = project_tickets(root)
print("tickets", len(tickets), "unheld", len(unheld))
total, left = 0.0, 0
start_all = time.perf_counter()
for ticket in tickets[:count]:
    start = time.perf_counter()
    try:
        for _ in range(2):
            packet = context(root, ticket)
            left += 1 if packet.get("left_out") else 0
    except Exception as exc:
        print(ticket, "error", type(exc).__name__)
    total += time.perf_counter() - start
print(f"{count} tickets: {total:.1f} s ({total / count:.2f} s per ticket); packets with left_out: {left}")
