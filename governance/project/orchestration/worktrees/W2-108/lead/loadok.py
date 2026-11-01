"""Exit 0 when the machine is under capacity (DEC-961): min of 1- and 15-minute loads below the CPU count."""
import os
import sys

load = os.getloadavg()
sys.exit(0 if min(load[0], load[2]) < os.cpu_count() else 1)
