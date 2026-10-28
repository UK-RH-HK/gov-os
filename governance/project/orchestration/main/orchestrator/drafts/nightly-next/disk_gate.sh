#!/usr/bin/env bash
# DEC-898 (owner, standing): the resource gate also checks free disk space and free inodes on the shared disk, and
# refuses a launch, a trial or a close below the floor. Exit 0 when both are above it; otherwise exit 1 with the
# reason on stderr. Until W2-20 builds it into gov launch and gov close, every launch command, close_queue.sh,
# nightly.sh and tooltrials.sh call it. The floors (the orchestrator's proposal, in force provisionally until the
# owner confirms or changes them): 100 GiB free and 10,000,000 inodes free.
FLOOR_GIB=${DISK_FLOOR_GIB:-100}
FLOOR_INODES=${INODE_FLOOR:-10000000}
free_gib=$(df --output=avail -B1G / | tail -1 | tr -d ' ')
free_inodes=$(df --output=iavail / | tail -1 | tr -d ' ')
if [ "$free_gib" -lt "$FLOOR_GIB" ] || [ "$free_inodes" -lt "$FLOOR_INODES" ]; then
  echo "disk gate SHUT: ${free_gib} GiB free (floor ${FLOOR_GIB}), ${free_inodes} inodes free (floor ${FLOOR_INODES})" >&2
  exit 1
fi
echo "disk gate open: ${free_gib} GiB free, ${free_inodes} inodes free" >&2
exit 0
