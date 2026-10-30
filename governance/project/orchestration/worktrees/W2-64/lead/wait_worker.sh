#!/bin/bash
# Lead's wait for a worker: until no gov launch process of this ticket and the given role remains (at most ~9 min).
ROLE=$1
for i in $(seq 1 54); do
  pgrep -f "gov.cli.main launch $ROLE DAEO-0uhh" > /dev/null || { echo "ended"; exit 0; }
  sleep 10
done
echo "running"
