#!/bin/bash
# Waits until no close or nightly is running and the 1-minute load is below 20; then writes "ok" to the file named.
F=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
until [ ! -e "$F/CLOSE-RUNNING" ] && [ ! -e "$F/NIGHTLY-RUNNING" ] && awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
date > /home/usain/gov-os-worktrees/W2-78/.gov-runtime/scratch/lead/log/gates-ok.txt
