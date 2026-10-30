"""Time gov.context.context for a few tickets of this worktree, and profile one call (the W2-54 time-limit red)."""

import cProfile
import pstats
import sys
import time
from pathlib import Path

import gov
from gov.context import context
from gov.context.context_check import project_tickets

root = Path("/home/usain/gov-os-worktrees/W2-03")
print("gov:", gov.__file__)
tickets, unheld = project_tickets(root)
print("tickets:", len(tickets), "unheld:", len(unheld))
count = int(sys.argv[1]) if len(sys.argv) > 1 else 3
for ticket in tickets[:count]:
    started = time.monotonic()
    context(root, ticket)
    print(ticket, round(time.monotonic() - started, 2), "s")
profile = cProfile.Profile()
profile.enable()
context(root, tickets[0])
profile.disable()
pstats.Stats(profile).sort_stats("cumulative").print_stats(25)
