"""Exit 0 while the machine has room (DEC-847, DEC-961): the 1-minute or the 15-minute load under the processors."""
import os

l1, _, l15 = os.getloadavg()
raise SystemExit(0 if min(l1, l15) < os.cpu_count() else 1)
