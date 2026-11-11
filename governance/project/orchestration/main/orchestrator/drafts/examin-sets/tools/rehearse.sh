#!/bin/bash
# ACT-EXAMIN-SETS-1's rehearsal, in a --no-hardlinks clone of w2/integrate under drafts/examin-sets/tmp/clone and a PLANTED
# home (tmp/home) whose gov-os-eval folder holds dummy files. The real sets root is never opened, listed or named to a
# hook: every hook run has HOME set to the planted home. Nothing live is changed.
#   bash rehearse.sh            runs every step; the log is ../rehearsal.log (ends "failures: <n>")
set -u
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/examin-sets
CL=$D/tmp/clone
PH=$D/tmp/home
ACT=$D/ACT-EXAMIN-SETS-1
T=$D/tools
PY=/home/usain/.local/share/gov-os/pin-797495bdfc70/bin/python
MAPREL=governance/project/path-map.yaml
LOG=$D/rehearsal.log
: > "$LOG"
exec > >(tee -a "$LOG") 2>&1
FAILS=0
ok() { echo "ok   $1"; }
bad() { echo "FAIL $1"; FAILS=$((FAILS + 1)); }
expect_exit() { # expect_exit <label> <want> <cmd...>
  local label="$1" want="$2"; shift 2
  "$@" > $D/tmp/.rehearsal-out.$$ 2>&1; local rc=$?
  sed 's/^/     /' $D/tmp/.rehearsal-out.$$ | cut -c1-200
  rm -f $D/tmp/.rehearsal-out.$$
  [ "$rc" = "$want" ] && ok "$label (exit $rc)" || bad "$label: want exit $want, got $rc"
}
sha() { sha256sum "$1" | cut -c1-64; }

echo "--- A. apply.sh on the clone's path map (cwd = the clone)"
cd "$CL" || exit 1
echo "clone HEAD $(git rev-parse --short=12 HEAD); the main tree's map $(sha /home/usain/Dynamic-Agentic-Engineering-OS/$MAPREL | cut -c1-12), the clone's $(sha $MAPREL | cut -c1-12), the bundle's before $(cut -d'|' -f3 $ACT/list.txt | cut -c1-12), after $(cut -d'|' -f4 $ACT/list.txt | cut -c1-12)"
[ "$(sha $MAPREL)" = "$(cut -d'|' -f3 $ACT/list.txt)" ] && ok "A0 the clone's map is the frozen before (the bundle is not stale)" || bad "A0 stale bundle"
[ "$(sha /home/usain/Dynamic-Agentic-Engineering-OS/$MAPREL)" = "$(cut -d'|' -f3 $ACT/list.txt)" ] && ok "A0b the main tree's map (read only) is the frozen before" || bad "A0b the main tree's map is not the frozen before"
cp -p $MAPREL $D/tmp/map.orig
expect_exit "A1 check: state before" 0 bash $ACT/apply.sh check
expect_exit "A2 verify refused before the apply" 3 bash $ACT/apply.sh verify
expect_exit "A2b undo before the apply says nothing to undo" 0 bash $ACT/apply.sh undo
echo "--- B. the guard's cases on the map BEFORE the entries (the gap check)"
expect_exit "B1 examin_check --expect before" 0 $PY -I $T/examin_check.py $CL $PH --expect before
echo "--- C. apply"
ACT_BACKUP_BESIDE=1 bash $ACT/apply.sh apply
rc=$?
[ "$rc" = 0 ] && ok "C1 apply with a backup beside it (exit 0)" || bad "C1 apply exit $rc"
cmp -s $MAPREL $ACT/after/repo/$MAPREL && ok "C2 the map is the frozen after, byte for byte" || bad "C2 the map is not the frozen after"
bak=$(ls $MAPREL.bak-*-ACT-EXAMIN-SETS-1 2>/dev/null | head -1)
[ -n "$bak" ] && cmp -s "$bak" $D/tmp/map.orig && ok "C3 the backup is the original byte for byte" || bad "C3 backup"
rm -f $MAPREL.bak-*-ACT-EXAMIN-SETS-1
expect_exit "C4 check: state applied" 0 bash $ACT/apply.sh check
expect_exit "C5 verify exit 0" 0 bash $ACT/apply.sh verify
expect_exit "C6 apply again changes nothing" 0 bash $ACT/apply.sh apply
echo "--- D. the checks the manifest lists, on the applied clone"
expect_exit "D1 PYTHONPATH=src python3 -m gov.check.pathmap" 0 env PYTHONPATH=src $PY -m gov.check.pathmap
expect_exit "D2 the map is valid YAML with the two entries only added (diff is two blocks at the end of evaluation_sets)" 0 $PY -I -c "
import yaml,sys
a=yaml.safe_load(open('$D/tmp/map.orig'));b=yaml.safe_load(open('$MAPREL'))
sa,sb=a['evaluation_sets'],b['evaluation_sets']
ok = set(sb)==set(sa)|{'examin','adoption-proving-ground'} and all(sa[k]==sb[k] for k in sa) and {k:v for k,v in a.items() if k!='evaluation_sets'}=={k:v for k,v in b.items() if k!='evaluation_sets'}
print(sorted(set(sb)-set(sa)))
sys.exit(0 if ok else 1)"
echo "--- E. the guard's cases on the applied map"
expect_exit "E1 examin_check --expect after" 0 $PY -I $T/examin_check.py $CL $PH --expect after
echo "--- F. the owner's step 2 on the PLANTED sets root's map, then the store and measure checks"
SRM=$PH/gov-os-eval/$MAPREL
cp -p $D/tmp/map.orig $SRM
cp -p $SRM $D/tmp/srm.orig
expect_exit "F1 check: state before" 0 env PY=$PY bash $T/sets_root_map.sh check $SRM
expect_exit "F2 apply" 0 env PY=$PY bash $T/sets_root_map.sh apply $SRM
cmp -s $SRM $MAPREL && ok "F3 the planted sets root's map now equals the applied repository map (the same block)" || bad "F3 the maps differ"
expect_exit "F4 check: state applied" 0 env PY=$PY bash $T/sets_root_map.sh check $SRM
expect_exit "F5 apply again changes nothing" 0 env PY=$PY bash $T/sets_root_map.sh apply $SRM
expect_exit "F6 store_check (evaluation_sets, set_fault, measure gate, kept_out)" 0 env PYTHONPATH=$CL/src $PY -I $T/store_check.py $CL $PH/gov-os-eval
echo "$(printf '# a later change\n')" >> $SRM
expect_exit "F7 undo refused after a later change" 3 env PY=$PY bash $T/sets_root_map.sh undo $SRM
cp -p $D/tmp/srm.orig $SRM
rm -f $SRM.pre-ACT-EXAMIN-SETS-1 $SRM.ACT-EXAMIN-SETS-1.sha256
cmp -s $SRM $D/tmp/srm.orig && ok "F8 the planted map restored" || bad "F8 restore"
cp -p $D/tmp/srm.orig $SRM
env PY=$PY bash $T/sets_root_map.sh apply $SRM > /dev/null
expect_exit "F9 undo restores the map" 0 env PY=$PY bash $T/sets_root_map.sh undo $SRM
cmp -s $SRM $D/tmp/srm.orig && ok "F10 undone byte for byte" || bad "F10 undo differs"
echo "--- G. a map that changed after the freeze is refused, undo, and the final state"
echo "# changed later" >> $MAPREL
expect_exit "G1 check refuses a map that changed" 3 bash $ACT/apply.sh check
expect_exit "G2 undo refuses (not as this ACT left it)" 3 bash $ACT/apply.sh undo
cp -p $ACT/after/repo/$MAPREL $MAPREL
expect_exit "G3 undo from the applied state" 0 bash $ACT/apply.sh undo
cmp -s $MAPREL $D/tmp/map.orig && ok "G4 the map is the original byte for byte" || bad "G4 original not restored"
expect_exit "G5 the insert tool refuses a map already holding one entry" 3 $PY -I -c "
import sys; sys.path.insert(0,'$T')
import insert_entries as m
t=open('$D/tmp/map.orig').read().replace('evaluation_sets:\n','evaluation_sets:\n  examin:\n    visible: []\n    hidden: [\"x/**\"]\n    measures: {roles: [engineer]}\n',1)
try:
    m.insert(t, open('$T/entries.yaml').read())
except ValueError as e:
    print('refused:', e); sys.exit(3)"
echo "--- H. the live files are unchanged (read only)"
echo "main tree map $(sha /home/usain/Dynamic-Agentic-Engineering-OS/$MAPREL | cut -c1-12), the bundle's before $(cut -d'|' -f3 $ACT/list.txt | cut -c1-12)"
[ "$(sha /home/usain/Dynamic-Agentic-Engineering-OS/$MAPREL)" = "$(cut -d'|' -f3 $ACT/list.txt)" ] && ok "H1 the main tree's map is unchanged" || bad "H1 the main tree's map changed"
echo
[ "$FAILS" = 0 ] && echo "REHEARSAL PASS" || echo "REHEARSAL FAIL"
echo "failures: $FAILS"
