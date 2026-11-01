"""Exit 0 when the machine is under its capacity (DEC-847, DEC-961): the 1-minute or 15-minute load below the
number of processors; exit 1 otherwise."""
import os

l1, _, l15 = os.getloadavg()
raise SystemExit(0 if min(l1, l15) < os.cpu_count() else 1)
