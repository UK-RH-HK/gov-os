set -e
T=/tmp/w2-188-lead-trial
rm -rf "$T"; mkdir -p "$T"
git clone -q --no-hardlinks /home/usain/gov-os-worktrees/W2-188-tests "$T/tree"
cp /home/usain/gov-os-worktrees/W2-188-tests/tests/acceptance/W2-188/README.md "$T/tree/tests/acceptance/W2-188/README.md"
python3 - "$T/tree/tests/acceptance/W2-188/README.md" <<'PY'
import re,sys
p=sys.argv[1]; s=open(p).read().splitlines()
o=[]
for l in s:
    l=re.sub(r"^\| `((?:success|failure)-\d)`", r"| \1", l)
    if l.startswith('| failure-3'): l=l.replace("S10's second reranker","`S10`'s second reranker",1)
    o.append(l)
open(p,'w').write('\n'.join(o)+'\n')
PY
mkdir -p "$T/home" "$T/tmp"
cd "$T/tree"
env HOME="$T/home" TMPDIR="$T/tmp" PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$T/tree/src" bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m gov.cli.main accept W2-188 --root "$T/tree" > "$T/accept.out" 2>&1; echo "rc=$?" >> "$T/accept.out"
