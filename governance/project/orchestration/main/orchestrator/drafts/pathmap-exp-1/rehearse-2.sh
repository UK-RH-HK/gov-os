#!/bin/bash
# Rehearsal part 2 of ACT-PATHMAP-EXP-1: after W2-40's branch is merged in the clone (the ACT is undone when it starts).
. /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/pathmap-exp-1/rehearse-common.sh
step "G. W2-40 merged in the clone, the ACT undone"
echo "merge parents: $(git log -1 --format=%p | wc -w); experiments files tracked: $(git ls-files experiments | wc -l); map $(h $MAP) (the before: ACT undone)"
echo "--- the two tests, ACT undone (expected RED)"
bash $SLOT env TMPDIR=$TMPDIR PYTHONPATH=$C/src python3 -m pytest "$T1" "$T2" -q -p no:cacheprovider -o tmp_path_retention_policy=failed 2>&1 | tail -25 | cut -c1-400
echo "--- gov.check.pathmap, ACT undone (expected findings)"
PYTHONPATH=$C/src python3 -m gov.check.pathmap > $TMPDIR/pm.out 2>&1; echo "exit $?"; head -5 $TMPDIR/pm.out | cut -c1-300
step "H. the ACT applied, the same merge"
expect "apply" 0 bash $ME/apply.sh apply
echo "--- the two tests, W1-08 and W2-91's whole file (expected green)"
bash $SLOT env TMPDIR=$TMPDIR PYTHONPATH=$C/src python3 -m pytest "$T1" "$T2" tests/acceptance/W1-08 tests/unit/retrieval/test_w2_91_full_embeddings.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed > $TMPDIR/green.out 2>&1; echo "exit $?"; tail -6 $TMPDIR/green.out | cut -c1-400
echo "--- gov.check.pathmap"
PYTHONPATH=$C/src python3 -m gov.check.pathmap > $TMPDIR/pm2.out 2>&1; echo "exit $?"; head -5 $TMPDIR/pm2.out
echo "--- every tracked path in exactly one namespace (clone with the merge in), the applied map"
python3 - <<'P'
import subprocess, yaml, re
m=lambda p,s: re.fullmatch(".*".join(re.escape(x).replace(r"\*","[^/]*") for x in p.split("**")),s) is not None
d=yaml.safe_load(open("governance/project/path-map.yaml"))["namespaces"]
tr=[x for x in subprocess.run(["git","ls-files","-z"],capture_output=True,text=True).stdout.split("\0") if x]
own=lambda p:[k for k,v in d.items() if any(m(q,p) for q in v["paths"])]
bad=[(p,own(p)) for p in tr if len(own(p))!=1]
exp=[p for p in tr if p.startswith("experiments/")]
print("tracked:",len(tr),"| not in exactly one namespace:",len(bad),bad[:3],"| experiments files:",len(exp),"| all in doc-records only:",all(own(p)==["doc-records"] for p in exp))
P
step "I. undo, back to REDS's after"
expect "undo" 0 bash $ME/apply.sh undo
echo "map $(h $MAP)"
echo; echo "PART2 N=$n FAIL=$fail"
