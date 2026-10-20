#!/bin/bash
# The builder tests, then gov check, each with its exit-code file. Usage: run_unit_check.sh <tag>
W=/home/usain/gov-os-worktrees/W2-37
L=$W/.gov-runtime/scratch/lead/log
tag=$1
cd $W || exit 2
PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -m pytest tests/unit -q -p no:cacheprovider > $L/$tag-unit.txt 2>&1
echo $? > $L/$tag-unit.rc
PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -m gov.cli.main check --json > $L/$tag-check.txt 2>&1
echo $? > $L/$tag-check.rc
echo done > $L/$tag-uc.done
