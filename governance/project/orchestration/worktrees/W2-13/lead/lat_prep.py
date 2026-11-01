"""lat_prep.py: clone the two dev tiers for the lead's interleaved latency measure (P-1 (a)), as W2-13's tests do.

Run with PYTHONPATH=<this worktree's src>:<this worktree's tests/acceptance/W2-13>. Prints each tier's root.
"""
import sys
from pathlib import Path

import w2_13_support as support

DEST = Path("/tmp/gov-os-lead-W2-13/lat-tiers")
for programme, tier in support.TIERS.items():
    root = support.clone_tier(tier, DEST / tier)
    if root is None:
        sys.exit(f"no dev tier {tier}")
    print(programme, root)
