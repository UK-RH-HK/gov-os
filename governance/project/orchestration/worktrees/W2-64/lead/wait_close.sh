#!/bin/bash
# Lead's wait: until no close's quiet window, no nightly, and the 1-minute load below 20; then write a mark.
F=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
until [ ! -e "$F/CLOSE-RUNNING" ] && [ ! -e "$F/NIGHTLY-RUNNING" ] && awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 30; done
date > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/quiet.mark
