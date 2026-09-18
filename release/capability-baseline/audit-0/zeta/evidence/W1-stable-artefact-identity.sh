#!/bin/bash
# W1: Verify stable artefact identity fields on governed records
SCRATCH=$1
GOV=$2
cd "$SCRATCH"
echo "=== W1: Stable artefact identity ==="
echo "--- Check record has: id, type, path, status, state_class, version/hash ---"
cat spec/requirements/REQ-0001.yaml
echo "---"
cat spec/decisions/D-0001.yaml
echo "---"
$GOV status 2>&1 | head -15
