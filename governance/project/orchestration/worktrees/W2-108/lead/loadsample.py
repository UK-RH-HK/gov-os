"""Append the 1-, 5- and 15-minute loads to the file given, every 15 s, until killed."""
import os
import sys
import time

path = sys.argv[1]
while True:
    with open(path, "a") as out:
        out.write("%d %.2f %.2f %.2f\n" % ((time.time(),) + os.getloadavg()))
    time.sleep(15)
