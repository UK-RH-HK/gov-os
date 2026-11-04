#!/usr/bin/env bash
# ACT-G14b's rehearsal (DEC-1057's rule): §3 line for line, then §4's rollback, in a scratch clone, from a fresh shell.
# Only the root path is substituted.
#   bash rehearse_act_g14b.sh --prepare <root>   make the clone at <root> (must not exist)
#   bash rehearse_act_g14b.sh <root>             run §3 and §4 there; each line, then its output
# From a fresh shell, as §3 asks: env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" PATH="$PATH" LANG="$LANG" \
#   bash --noprofile --norc rehearse_act_g14b.sh <root>
# The clone is made as rehearse_act_g14.sh makes it: `git clone --no-hardlinks` of the main tree at its HEAD on a
# branch g14b-rehearsal, every local branch recreated at the same commit with its reflog, the untracked
# .gov-runtime/scratch/orchestrator/{tools,drafts/g14,drafts/act-guard-fix-4} copied in with the main tree's path
# written as <root>, under ~/gov-os-runs/ with the main tree's folder name.
set -u
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
SUB=.gov-runtime/scratch/orchestrator

if [ "${1:-}" = "--prepare" ]; then
  R=${2:?the clone root}
  [ -e "$R" ] && { echo "$R exists" >&2; exit 1; }
  mkdir -p "$(dirname "$R")"
  git clone -q --no-hardlinks "$MAIN" "$R" || exit 1
  head=$(git -C "$MAIN" rev-parse HEAD)
  git -C "$R" checkout -q -b g14b-rehearsal "$head" || exit 1
  git -C "$MAIN" for-each-ref --format='%(refname) %(objectname)' refs/heads/ | while read -r ref sha; do
    [ "$ref" = refs/heads/g14b-rehearsal ] && continue
    git -C "$R" update-ref "$ref" "$sha" || exit 1
    if [ -f "$MAIN/.git/logs/$ref" ]; then
      mkdir -p "$(dirname "$R/.git/logs/$ref")"
      cp -p "$MAIN/.git/logs/$ref" "$R/.git/logs/$ref"
    fi
  done
  for d in tools drafts/g14 drafts/act-guard-fix-4; do
    mkdir -p "$R/$SUB/$(dirname "$d")"
    cp -a "$MAIN/$SUB/$d" "$R/$SUB/$(dirname "$d")/"
  done
  rm -rf "$R/$SUB/drafts/g14/backup" "$R/$SUB/drafts/g14/backup-g14b"  # §3 makes its own
  grep -rlI --null "$MAIN" "$R/$SUB" | xargs -0 -r sed -i "s#$MAIN#$R#g"
  echo "prepared $R at $(git -C "$R" rev-parse --short=12 HEAD) on $(git -C "$R" branch --show-current);" \
       "branches $(git -C "$R" for-each-ref refs/heads/ | wc -l); root mentions left: $(grep -rlI "$MAIN" "$R/$SUB" | wc -l)"
  exit 0
fi

R=${1:?the clone root}
[ -d "$R/.git" ] || { echo "no clone at $R (run --prepare first)" >&2; exit 1; }
step() {  # one line of the ACT, shown, then run in the clone's root
  printf '\n$ %s\n' "$1"
  ( cd "$R" && eval "$1" ) 2>&1
  printf '[exit %s]\n' "$?"
}
echo "ACT-G14b rehearsal: $(date '+%Y-%m-%d %H:%M:%S %Z') in $R at $(git -C "$R" rev-parse --short=12 HEAD)"
echo "== §3"
step "cd $R"
step 'rm -rf /tmp/gov-os-act-g14b'
step "D=.gov-runtime/scratch/orchestrator/drafts/g14; T=.gov-runtime/scratch/orchestrator/tools; echo D=\$D T=\$T"
D=.gov-runtime/scratch/orchestrator/drafts/g14  # plain shell variables, as in §3: never exported
T=.gov-runtime/scratch/orchestrator/tools
step 'env | grep -c "^[DT]=" || true'
step 'git status --short -- .claude/'
step 'sha256sum .claude/hooks/pretooluse.py .claude/hooks/role_reads.py $D/pretooluse.py $D/role_reads.py | cut -c1-12'
step "python3 \$T/guard4_check.py --settings $R | grep -E '^FAIL|^PASS'"
step 'mkdir -p $D/backup-g14b'
step 'cp -p .claude/hooks/role_reads.py $D/backup-g14b/'
step 'cp $D/role_reads.py .claude/hooks/'
step "python3 \$T/guard4_check.py --settings $R | grep -E '^FAIL|^PASS'"
step 'TMPDIR=/tmp/gov-os-act-g14b bash $T/heavy_slot.sh python3 -m pytest -q -n 6 -o tmp_path_retention_policy=failed -p no:cacheprovider tests/unit/hooks/test_live_hook.py -rf | grep -E "^FAILED|failed|passed"'
step 'GUARD_FIX4_HOOK=$PWD/.claude/hooks/pretooluse.py TMPDIR=/tmp/gov-os-act-g14b bash $T/heavy_slot.sh python3 -m pytest -q -n 6 -o tmp_path_retention_policy=failed -p no:cacheprovider .gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4/test_guard_fix_4.py -rf | grep -E "^FAILED|failed|passed"'
step 'G14_HOOK=$PWD/.claude/hooks/pretooluse.py TMPDIR=/tmp/gov-os-act-g14b bash $T/heavy_slot.sh python3 -m pytest -q -n 6 -o tmp_path_retention_policy=failed -p no:cacheprovider $D/test_g14.py -rf | grep -E "^FAILED|failed|passed"'
step 'git add .claude/hooks/role_reads.py'
step 'git commit -m "ACT-G14b: a coordination ticket'"'"'s {ticket_tests} is its own folder only (DEC-1056, DEC-1058): W2-00'"'"'s Task: links no longer refuse other tickets'"'"' tests" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1056, DEC-1058" --trailer "Role: owner"'
step 'git rev-parse HEAD > $D/backup-g14b/act-commit && cut -c1-12 $D/backup-g14b/act-commit'
echo
echo "== §4 (the rollback)"
step "cd $R && D=.gov-runtime/scratch/orchestrator/drafts/g14 && read -r H < \$D/backup-g14b/act-commit && git revert --no-commit \"\$H\" && git commit -m \"Revert ACT-G14b (\${H:0:12})\" --trailer \"Task: DAEO-sdxk\" --trailer \"Implements: DEC-1058\" --trailer \"Role: owner\" && python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py --settings \$PWD | grep -E '^FAIL|^PASS'"
step 'sha256sum .claude/hooks/role_reads.py | cut -c1-12; git status --short -- .claude/'
echo
echo "rehearsal done: $(date '+%Y-%m-%d %H:%M:%S %Z')"
