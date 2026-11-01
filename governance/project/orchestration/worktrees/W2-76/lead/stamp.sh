#!/usr/bin/env bash
# Write the time the gate let the run start into arg 1, then run the rest of the arguments.
F=$1
shift
date '+start %F %T' >> "$F"
exec "$@"
