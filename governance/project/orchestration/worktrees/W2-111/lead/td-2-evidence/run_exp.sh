#!/usr/bin/env bash
# usage: run_exp.sh <script.py> <label> [args...]   -- a scratch experiment through the heavy slot, as the cases run
S=$1; shift
W=/home/usain/gov-os-worktrees/W2-111-tests
mkdir -p ${TMPDIR:-/tmp}/w2-111-td2 $W/.gov-runtime/scratch/empty-home
env TMPDIR=${TMPDIR:-/tmp}/w2-111-td2 PYTHONUSERBASE=/home/usain/.local HOME=$W/.gov-runtime/scratch/empty-home \
  PYTHONPATH=$W/src:$W/.gov-runtime/scratch/td \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 $W/.gov-runtime/scratch/td/$S "$@"
