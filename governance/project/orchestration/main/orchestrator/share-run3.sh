#!/bin/bash
# Governance share of run 3's implementation and test-design sessions, per ticket (DEC-655). The command reads the logs.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
C=/tmp/claude-1000/-home-usain-gov-os-worktrees-W1-42/1be98491-a02b-4f3c-accf-41da4cc96c6b/scratchpad/clones
one() {
  local name="$1" root="$2" ticket="$3"
  shift 3
  local args=()
  for s in "$@"; do args+=(--ticket-session "$s"); done
  PYTHONPATH=src python3 -m gov.cli.main telemetry "$ticket" --json --root "$root" "${args[@]}" > "$L/share-$name.json" 2> "$L/share-$name.err"
  echo "$name: exit $?"
}
one ORION-im01 "$C/a-dev-exit" ORION-im01 17ddef8f-89b7-4d3f-85ec-ab88bdcfc863=engineer
one ORION-gp09-r3 "$C/a-dev-exit" ORION-gp09 11cbaf5d-ca3f-4000-aed9-628ec50dbca4=independent-test-designer
one ARGUS-im01 "$C/b-dev-exit" ARGUS-im01 721df431-f0c8-4a4f-9635-012517224284=engineer
one ARGUS-gp13 "$C/b-dev-exit" ARGUS-gp13 066cf469-c1ce-475a-ba66-849109e7e86e=independent-test-designer
