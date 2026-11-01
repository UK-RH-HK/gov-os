#!/usr/bin/env bash
# KPI 4's measure: the context check on the measurement clone's one store, under cProfile, with a cold query-vector
# cache, the load sampled every 15 s. usage: measure.sh <tag> <src folder of the code under test>
# Writes /tmp/gov-os-lead-W2-108/prof/<tag>.{prof,out,exit,load,wall}
cd /tmp/gov-os-lead-W2-108/measure || exit 9
TAG="$1"
SRC="$2"
mkdir -p /tmp/gov-os-lead-W2-108/prof
rm -f /tmp/gov-os-lead-W2-108/measure/.gov-runtime/query-vector-cache.db
rm -f /tmp/gov-os-lead-W2-108/measure/.gov-runtime/query-vector-cache.db-journal
python3 /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/loadsample.py "/tmp/gov-os-lead-W2-108/prof/$TAG.load" &
SAMPLER=$!
START=$(date +%s)
TMPDIR=/tmp/gov-os-lead-W2-108 PYTHONPATH="$SRC" python3 -m cProfile -o "/tmp/gov-os-lead-W2-108/prof/$TAG.prof" -m gov.context.context_check > "/tmp/gov-os-lead-W2-108/prof/$TAG.out" 2>&1
CODE=$?
END=$(date +%s)
kill "$SAMPLER"
echo $((END - START)) > "/tmp/gov-os-lead-W2-108/prof/$TAG.wall"
echo "$CODE" > "/tmp/gov-os-lead-W2-108/prof/$TAG.exit"
