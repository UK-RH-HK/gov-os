"""Scratch only: busy-loop until this process's own CPU time reaches argv[1] seconds, then exec the real command."""
import os, sys, time
limit = float(sys.argv[1])
while time.process_time() < limit:
    pass
os.execvp(sys.argv[2], sys.argv[2:])
