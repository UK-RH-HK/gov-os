#!/usr/bin/env bash
# P2-AR-0025 evidence tool: normalised before/after diff of the probes that print observations without PASS/FAIL
# verdict lines (alpha-r, gamma-r, epsilon-r). Normalisation removes timestamps, hex digests, scratch paths, record
# sequence numbers and timings, so what remains is a behavioural difference. Usage: diff-unmarked.sh > UNMARKED-normalised-diff.out
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
N='s/[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z?//g; s/[0-9a-f]{12,}//g; s#/tmp/[^ "]*##g; s/(CKPT|HDG|CIT|D|TASK|AUD|RPT|HO)-[0-9]+/\1-N/g; s/[0-9]+(\.[0-9]+)? ?(ms|s)\b/T/g; s/probe-[0-9a-f]{8}/probe-X/g; s/"(wall_ms|samples|duration_ms|max_threads|max_child_processes|inode)": [0-9]+/"\1": N/g'
for f in alpha-r.A3-security-sensitivity alpha-r.A4-budget-governance alpha-r.A5-emergency-controls gamma-r.E1-authority gamma-r.E2-roles gamma-r.E3-handoffs gamma-r.G1G2-command-surface gamma-r.H1-lineage gamma-r.I1I2-tasks gamma-r.I3-generation epsilon-r.O4-suite-currency epsilon-r.O5-G0-guard-matrix epsilon-r.O5-scheduler-requirements epsilon-r.O5-tiers-G1-G6; do
  echo "=================== $f"
  diff <(sed -E "$N" "$HERE/before/$f.out" | grep -v '^# \(P2-AR\|worktree\|probe sha\|date\|GOV=\|SCRATCH\)') \
       <(sed -E "$N" "$HERE/after/$f.out" | grep -v '^# \(P2-AR\|worktree\|probe sha\|date\|GOV=\|SCRATCH\)') | cut -c1-600
done
