#!/usr/bin/env bash
# Waits until no close and no nightly is running, then writes a stamp file (the lead's wait helper).
rm -f /home/usain/gov-os-worktrees/W2-77/.gov-runtime/scratch/lead/log/quiet.done
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ] && [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING ]; do
  sleep 30
done
date -u > /home/usain/gov-os-worktrees/W2-77/.gov-runtime/scratch/lead/log/quiet.done
