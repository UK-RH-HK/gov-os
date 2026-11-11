#!/bin/bash
# Rehearsal part 1 of ACT-PATHMAP-EXP-1: the chain and the ACT's own script (before W2-40's merge). Prints N and FAIL on its last line.
. /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/pathmap-exp-1/rehearse-common.sh
git config user.name rehearsal; git config user.email rehearsal@example.invalid
step "A. preconditions"
echo "clone branch: $(git branch --show-current); map $(h $MAP); clean: $(git status --porcelain | wc -l) changes"
echo "EXAMIN before $(h $EX/before/repo/$MAP) after $(h $EX/after/repo/$MAP); REDS before $(h $RD/before/repo/$MAP) after $(h $RD/after/repo/$MAP); mine before $(h $ME/before/repo/$MAP) after $(h $ME/after/repo/$MAP)"
cmp "$RD/after/repo/$MAP" "$ME/before/repo/$MAP" && echo "  [ok] my before copy is REDS's after copy, byte for byte" || { echo "  [FAIL] chain"; fail=$((fail+1)); }
echo "the one added line (diff before to after of this ACT):"; diff "$ME/before/repo/$MAP" "$ME/after/repo/$MAP"
step "B. wrong order: this ACT on the map before EXAMIN (f4029cfb)"
for s in check apply undo verify; do expect "out of order $s" 3 bash $ME/apply.sh $s; done
echo "map unchanged: $(h $MAP); git status: $(git status --porcelain | wc -l) changes; temp files: $(ls governance/project | grep -c act-tmp)"
step "C. ACT-EXAMIN-SETS-1 r2 (its own apply.sh)"
expect "examin check" 0 bash $EX/apply.sh check
expect "examin apply" 0 bash $EX/apply.sh apply
echo "map $(h $MAP)"
git add $MAP && git commit -q -m "ACT-EXAMIN-SETS-1 (rehearsal)" && echo committed
step "D. ACT-ACCEPTED-REDS-1 r2 (its after copy put in place; its section 5 commit is the owner's by hand)"
cp "$RD/after/repo/$MAP" $MAP
echo "map $(h $MAP)"
git add $MAP && git commit -q -m "ACT-ACCEPTED-REDS-1 (rehearsal)" && echo committed
step "E. ACT-PATHMAP-EXP-1: check, verify, undo, apply, verify, again"
expect "check (before)" 0 bash $ME/apply.sh check
expect "verify before apply" 3 bash $ME/apply.sh verify
expect "undo when nothing applied" 0 bash $ME/apply.sh undo
expect "check line" 0 bash -c "bash $ME/apply.sh check | grep -x 'state before (sha256 5654eca4c139)'"
expect "apply" 0 bash $ME/apply.sh apply
echo "map $(h $MAP) mode $(stat -c %a $MAP); status:"; git status --porcelain; ls governance/project | grep act-tmp || echo "no temp file"
cmp $MAP $ME/after/repo/$MAP && echo "  [ok] the map is the frozen after, byte for byte"
expect "verify" 0 bash $ME/apply.sh verify
expect "apply again" 0 bash $ME/apply.sh apply
expect "check (applied)" 0 bash $ME/apply.sh check
echo "git diff of the map:"; git diff $MAP
step "F. the manifest's two checks, as written, applied and before"
python3 - <<'P' > $TMPDIR/checks.txt
import json
for c in json.load(open("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/pathmap-exp-1/ACT-PATHMAP-EXP-1/manifest.json"))["checks"]:
    print(c["cmd"].replace("\n", " "))
P
i=0; while IFS= read -r cmd; do i=$((i+1)); expect "check $i on the applied map" 0 bash -c "$cmd"; done < $TMPDIR/checks.txt
expect "undo" 0 bash $ME/apply.sh undo
cmp $MAP $ME/before/repo/$MAP && echo "  [ok] undo: byte for byte the before copy"; echo "git status changes: $(git status --porcelain | wc -l)"
i=0; while IFS= read -r cmd; do i=$((i+1)); if [ $i = 2 ]; then expect "check 2 on the before map (must fail)" 1 bash -c "$cmd"; else expect "check $i on the before map" 0 bash -c "$cmd"; fi; done < $TMPDIR/checks.txt
echo "PART1 N=$n FAIL=$fail"
