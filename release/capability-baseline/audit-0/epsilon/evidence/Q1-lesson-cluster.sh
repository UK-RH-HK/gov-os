#!/bin/bash
set -euo pipefail
GOV="$1"; ROOT="$2"
echo "=== Q1: Lesson cluster / intake ==="

# Create a canonical-repo-like structure with an inbox
mkdir -p /tmp/epsilon-scratch/canonical/lessons/inbox
mkdir -p /tmp/epsilon-scratch/canonical/change-proposals

# Copy the upstream packet into the inbox
if [ -d "$ROOT/.governance-runtime/outbound/PKT-0001" ]; then
  cp -r "$ROOT/.governance-runtime/outbound/PKT-0001" /tmp/epsilon-scratch/canonical/lessons/inbox/PKT-0001-test-project
fi

# Run lesson cluster
$GOV lessons cluster --root "$ROOT" --json 2>&1 || echo "(expected: lessons cluster needs specific args)"
echo ""
echo "--- Lessons cluster help ---"
$GOV lessons cluster --help 2>&1
