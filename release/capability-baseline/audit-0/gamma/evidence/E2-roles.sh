#!/usr/bin/env bash
GOV="$1"; PROJ="$2"
echo "=== E2: All representative roles in ROLES.yaml ==="
for role in orchestrator architecture-agent memory-engineer independent-test-designer independent-auditor security-engineer release-agent research-agent backend-engineer human; do
  echo "--- $role ---"
  "$GOV" --root "$PROJ" --json --role "$role" status 2>&1 | grep -o '"role":"[^"]*"' | head -1
done
echo "--- Unknown role rejected ---"
"$GOV" --root "$PROJ" --json --role nonexistent-role task create --class discovery --objective "test" 2>&1 | grep -o '"code":"[^"]*"'
echo "--- Governed extension: groups defined ---"
cat "$PROJ/governance/kernel/roles/ROLES.yaml" | grep -c "id:" 
echo "roles present"
