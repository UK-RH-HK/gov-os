#!/bin/bash
# Runs section 5's code block of ACT-W1-01-EXEMPT-3.md AS WRITTEN, the way the owner's operator will, in a fresh clone with a
# planted HOME. Only two things are substituted: the repository root (the clone for the main tree) and, for the optional pytest line,
# the gate's path made absolute (the clone has no .gov-runtime). Output: tmp/section5.out; prints a summary.
set -u
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
D=$ORCH/drafts/act-w1-01-exempt-3
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
CL=$D/tmp/clone5
rm -rf $D/tmp/home5 $CL $D/tmp/section5.sh
mkdir -p $D/tmp/home5
cp -p /home/usain/.gitconfig $D/tmp/home5/.gitconfig
mkdir -p $D/tmp/home5/.local && ln -s /home/usain/.local/bin $D/tmp/home5/.local/bin && ln -s /home/usain/.local/share $D/tmp/home5/.local/share
export HOME=$D/tmp/home5
git clone -q --no-hardlinks $MAIN $CL || exit 1
# the first fenced block of section 5, "> " stripped
python3 -I - "$D/ACT-W1-01-EXEMPT-3.md" "$D/tmp/section5.sh" "$MAIN" "$CL" "$ORCH" <<'EOF'
import sys,re
md,out,main,cl,orch=sys.argv[1:6]
t=open(md).read()
sec=t.split("## 5. ")[1].split("## 6. ")[0]
lines=sec.splitlines()
i=[k for k,l in enumerate(lines) if l.startswith("> ```")]
block=[l[2:] for l in lines[i[0]+1:i[1]]]
text="\n".join(block)+"\n"
text=text.replace("cd "+main+"\n","cd "+cl+"\n",1)
opt=[l[2:] for l in lines if l.startswith("> Optional")][0]
cmd=re.search(r"`(PYTHONPATH=src bash [^`]*)`",opt).group(1).replace("bash .gov-runtime/scratch/orchestrator/tools/heavy_slot.sh","bash "+orch+"/tools/heavy_slot.sh")
text+=cmd+"\n"
open(out,"w").write(text)
EOF
echo "--- the script that runs (section 5 as written, root substituted):"; cut -c1-150 $D/tmp/section5.sh
echo "--- output:"
bash $D/tmp/section5.sh > $D/tmp/section5.out 2>&1; echo "script exit $?"
cut -c1-200 $D/tmp/section5.out | tail -25
echo "--- the clone's last commit:"; git -C $CL log -1 --format='%s' | cut -c1-120; git -C $CL log -1 --format='%(trailers:only,unfold,separator=; )'; git -C $CL status --porcelain | wc -l
