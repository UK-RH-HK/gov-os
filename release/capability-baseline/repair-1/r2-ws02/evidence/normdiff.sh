#!/usr/bin/env bash
# P2-AR-0023: normalised line diff of an unmarked audit-of-record probe run, base binary vs repaired binary.
# Scratch paths, timestamps, hashes of per-run artefacts and header lines are normalised away; what remains is the
# product's observable output. Usage: normdiff.sh <before-file> <after-file>
norm() { sed -E 's#/tmp/[^ "'"'"',)]*#<tmp>#g; s/[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z/<ts>/g; s/[0-9a-f]{40,64}/<hex>/g; s/HR-[0-9A-Za-z-]+/HR-<id>/g; s/"(duration_ms|wall_ms|samples|latency_ms)": [0-9]+/"\1": <n>/g; s/ [0-9]+ms$/ <n>ms/' "$1" | grep -vE '^# '; }
diff <(norm "$1") <(norm "$2")
