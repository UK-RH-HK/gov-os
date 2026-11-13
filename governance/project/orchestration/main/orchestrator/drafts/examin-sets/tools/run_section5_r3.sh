#!/bin/bash
# The chain end to end in ONE clone, the last step run as written: ACT-EXAMIN-SETS-1 (round 3) by its own apply.sh and committed in the
# clone as the agent would (Role: operator); then section 5's code block of ACT-ACCEPTED-REDS-1.md (round 3) cut out and run AS WRITTEN, the
# way the owner's operator will, in a fresh clone with a planted HOME. Only the repository root is substituted (the clone for the main
# tree). Output: ../../accepted-reds-1/section5.r3.out (kept beside the logs, review F2 of ACT-W1-01-EXEMPT-3); prints a summary.
# Run it after the manifests are final (section 5 prints and expects the REDS manifest's sha256).
set -u
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
D=$ORCH/drafts/examin-sets
DR=$ORCH/drafts/accepted-reds-1
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
RUN=/home/usain/gov-os-runs/W2-00/pathmap-chain-r3
CL=$RUN/clone5
EX=$ORCH/acts/ACT-EXAMIN-SETS-1   # the queued bundle (the round 3 one, copied there after the rehearsal)
export TMPDIR=$RUN/tmp
rm -rf $RUN/tmp/home5 $CL $RUN/tmp/section5.r3.sh
mkdir -p $RUN/tmp/home5/.local
cp -p /home/usain/.gitconfig $RUN/tmp/home5/.gitconfig
ln -s /home/usain/.local/bin $RUN/tmp/home5/.local/bin
ln -s /home/usain/.local/share $RUN/tmp/home5/.local/share
export HOME=$RUN/tmp/home5
git clone -q --no-hardlinks $MAIN $CL || exit 1
cd $CL || exit 1
echo "--- EXAMIN, by its own apply.sh (the agent's route), committed in the clone as the agent would"
bash $EX/apply.sh check && bash $EX/apply.sh apply && bash $EX/apply.sh verify || { echo "EXAMIN did not apply"; exit 1; }
git commit -q -m "ACT-EXAMIN-SETS-1: applied by the operator agent (rehearsal clone)" --trailer "Role: operator" --trailer "Act: ACT-EXAMIN-SETS-1" -- governance/project/path-map.yaml || exit 1
echo "clone clean after EXAMIN: $([ -z "$(git status --porcelain)" ] && echo yes || echo no)"
# the first fenced block of section 5 of REDS's package, "> " stripped, the cd line pointed at the clone
python3 -I - "$DR/ACT-ACCEPTED-REDS-1.md" "$RUN/tmp/section5.r3.sh" "$MAIN" "$CL" <<'EOF'
import sys
md, out, main, cl = sys.argv[1:5]
t = open(md).read()
sec = t.split("## 5. ")[1].split("## 6. ")[0]
lines = sec.splitlines()
i = [k for k, l in enumerate(lines) if l.startswith("> ```")]
block = [l[2:] for l in lines[i[0] + 1:i[1]]]
text = "\n".join(block) + "\n"
assert text.count("cd " + main + "\n") == 1
text = text.replace("cd " + main + "\n", "cd " + cl + "\n", 1)
open(out, "w").write(text)
EOF
echo "--- the script that runs (section 5 as written, root substituted):"; cut -c1-170 $RUN/tmp/section5.r3.sh
echo "--- output:"
bash $RUN/tmp/section5.r3.sh > $DR/section5.r3.out 2>&1; echo "script exit $?"
cut -c1-200 $DR/section5.r3.out | tail -25
echo "--- the clone's last commit:"
git -C $CL log -1 --format='%s' | cut -c1-120
git -C $CL log -1 --format='%(trailers:only,unfold,separator=; )'
echo "clone status lines: $(git -C $CL status --porcelain | wc -l)"
