#!/bin/bash
# Governance share of the exit run's worker sessions up to lead run 2, per ticket, with the merged reader (DEC-655).
# The command reads the session logs; nothing here reads them.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
C=/tmp/claude-1000/-home-usain-gov-os-worktrees-W1-42/1be98491-a02b-4f3c-accf-41da4cc96c6b/scratchpad/clones
W=/home/usain/gov-os-worktrees/W1-42
one() {
  local name="$1" root="$2" ticket="$3"
  shift 3
  local args=()
  for s in "$@"; do args+=(--ticket-session "$s"); done
  PYTHONPATH=src python3 -m gov.cli.main telemetry "$ticket" --json --root "$root" "${args[@]}" > "$L/share-$name.json" 2> "$L/share-$name.err"
  echo "$name: exit $?"
}
one ORION-sp01 "$C/a-dev-exit" ORION-sp01 30d80992-696a-4d46-8448-a8356594b330=product-spec cd685872-3076-4747-98f2-54ac15c436f1=product-spec
one ORION-ad01 "$C/a-dev-exit" ORION-ad01 d6e1b5d3-6323-4202-8bd6-e2f0beb6f856=product-spec 1ddd5332-9094-473d-b2f4-201bdf5825b9=product-spec
one ORION-ad02 "$C/a-dev-exit" ORION-ad02 374ba416-f86b-4312-8343-28996934868d=independent-auditor
one ORION-gp09 "$C/a-dev-exit" ORION-gp09 32ce12c8-8873-4b69-8b30-3fc24d408468=independent-test-designer
one ARGUS-sp01 "$C/b-dev-exit" ARGUS-sp01 1522beaf-6e63-44ef-872f-2c6452797298=product-spec f2ef7e58-9588-4239-8cec-10cce0de1e5e=product-spec
one ARGUS-ad01 "$C/b-dev-exit" ARGUS-ad01 94619988-2d84-4359-b2c4-3d22e2eb1c36=product-spec
one DAEO-gjjf "$W" DAEO-gjjf 824751db-712e-4b49-b0c8-396fd2f8360b=independent-test-designer
