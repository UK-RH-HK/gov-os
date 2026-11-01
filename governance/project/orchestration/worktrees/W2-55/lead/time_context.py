"""Time gov.context.context(root, ticket) with the code at sys.argv[1] on the project at sys.argv[2]."""
import cProfile
import pstats
import sys
import time

sys.path.insert(0, sys.argv[1])
from gov.context import context  # noqa: E402

root, ticket = sys.argv[2], sys.argv[3]
for n in range(2):
    start = time.perf_counter()
    packet = context(root, ticket)
    print(f"run {n}: {time.perf_counter() - start:.2f} s, left_out={packet.get('left_out', {}).get('count') if packet.get('left_out') else None}")
if len(sys.argv) > 4:
    prof = cProfile.Profile()
    prof.enable()
    context(root, ticket)
    prof.disable()
    pstats.Stats(prof).sort_stats("cumulative").print_stats(18)
