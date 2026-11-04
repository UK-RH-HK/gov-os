#!/usr/bin/env bash
# ACT-G14's rehearsal (the CTO's order after the failed run of 2026-11-03): §3 line for line, then §4's rollback, in
# a scratch clone. Only the root path is substituted.
#   bash rehearse_act_g14.sh --prepare <root>   make the clone at <root> (must not exist)
#   bash rehearse_act_g14.sh <root>             run §3 and §4 there; each line, then its output
# From a fresh shell, as §3 asks: env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" PATH="$PATH" LANG="$LANG" \
#   bash --noprofile --norc rehearse_act_g14.sh <root>
# The clone: `git clone --no-hardlinks` of the main tree at its HEAD, on a branch g14-rehearsal (no commit lands on a
# branch named w2/integrate), with:
#   - every local branch of the main tree recreated at the same commit, and its reflog copied: the guard's rules read
#     w2/<WBS>, w2/<WBS>-tests and the tests branch's "Created from" entry;
#   - the untracked .gov-runtime/scratch/orchestrator/{tools,drafts/g14,drafts/act-guard-fix-4} copied in, with the
#     main tree's path written as <root> in their text files (the tests and scripts name the root: ROOT, M, the
#     corpus's cwd).
# Put the clone under ~/gov-os-runs/ (a run clone), never under /tmp: the rm rule treats /tmp as scratch.
set -u
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
SUB=.gov-runtime/scratch/orchestrator

if [ "${1:-}" = "--prepare" ]; then
  R=${2:?the clone root}
  [ -e "$R" ] && { echo "$R exists" >&2; exit 1; }
  mkdir -p "$(dirname "$R")"
  git clone -q --no-hardlinks "$MAIN" "$R" || exit 1
  head=$(git -C "$MAIN" rev-parse HEAD)
  git -C "$R" checkout -q -b g14-rehearsal "$head" || exit 1
  git -C "$MAIN" for-each-ref --format='%(refname) %(objectname)' refs/heads/ | while read -r ref sha; do
    [ "$ref" = refs/heads/g14-rehearsal ] && continue
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
  rm -rf "$R/$SUB/drafts/g14/backup"  # the failed run's backups stay in the main tree; §3 makes its own
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
echo "ACT-G14 rehearsal: $(date '+%Y-%m-%d %H:%M:%S %Z') in $R at $(git -C "$R" rev-parse --short=12 HEAD)"
echo "== §3"
step "cd $R"
step 'rm -rf /tmp/gov-os-act-g14'
step "D=.gov-runtime/scratch/orchestrator/drafts/g14; T=.gov-runtime/scratch/orchestrator/tools; echo D=\$D T=\$T"
D=.gov-runtime/scratch/orchestrator/drafts/g14  # plain shell variables, as in §3: never exported (the hook
T=.gov-runtime/scratch/orchestrator/tools       # expands $D in the tests' commands from its own environment)
step 'git status --short -- .claude/ governance/project/path-map.yaml'
step 'sha256sum .claude/hooks/pretooluse.py governance/project/path-map.yaml $T/guard4_check.py | cut -c1-12'
step 'sha256sum $D/pretooluse.py $D/role_reads.py $D/guard4_check.py $D/path-map-role_paths.patch | cut -c1-12'
step 'GUARD_FIX4_HOOK=$PWD/.claude/hooks/pretooluse.py TMPDIR=/tmp/gov-os-act-g14 bash $T/heavy_slot.sh python3 -m pytest -q -o tmp_path_retention_policy=failed -p no:cacheprovider .gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4/test_guard_fix_4.py -k test_logged_refusals -rf | grep -E "^FAILED|failed|passed"'
step 'mkdir -p $D/backup'
step 'cp -p .claude/hooks/pretooluse.py governance/project/path-map.yaml $T/guard4_check.py $D/backup/'
step 'git apply --check -p1 $D/path-map-role_paths.patch && git apply -p1 $D/path-map-role_paths.patch'
step "PYTHONPATH=src python3 -c \"import yaml; from gov.config import loader; d=yaml.safe_load(open('governance/project/path-map.yaml')); loader._validate_path_map(d, 'path-map'); print(d['role_paths'])\""
step 'cp $D/pretooluse.py $D/role_reads.py .claude/hooks/'
step 'cp $D/guard4_check.py $T/guard4_check.py'
step "python3 \$T/guard4_check.py --settings $R | tail -1"
echo "(rehearsal only, not in §3: guard4_check.py's case count and its G-14 lines)"
step "python3 \$T/guard4_check.py --settings $R | grep -c '^ok'; python3 \$T/guard4_check.py --settings $R | grep 'G-14\|^FAIL'"
echo "(end of the rehearsal-only lines)"
step 'GUARD_FIX4_HOOK=$PWD/.claude/hooks/pretooluse.py TMPDIR=/tmp/gov-os-act-g14 bash $T/heavy_slot.sh python3 -m pytest -q -n 6 -o tmp_path_retention_policy=failed -p no:cacheprovider .gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4/test_guard_fix_4.py -rf | grep -E "^FAILED|failed|passed"'
step 'G14_HOOK=$PWD/.claude/hooks/pretooluse.py TMPDIR=/tmp/gov-os-act-g14 bash $T/heavy_slot.sh python3 -m pytest -q -n 6 -o tmp_path_retention_policy=failed -p no:cacheprovider $D/test_g14.py | tail -1'
echo '(rehearsal only, not in §3: the failures by name, and D and T not exported)'
step 'G14_HOOK=$PWD/.claude/hooks/pretooluse.py TMPDIR=/tmp/gov-os-act-g14 bash $T/heavy_slot.sh python3 -m pytest -q -n 6 -o tmp_path_retention_policy=failed -p no:cacheprovider $D/test_g14.py -rfE 2>&1 | grep -E "^(FAILED|ERROR)" | cut -c1-220'
step 'env | grep -c "^[DT]=" || true'
echo '(end of the rehearsal-only lines)'
step 'bash $D/scoped_tests.sh'
step 'git add .claude/hooks/pretooluse.py .claude/hooks/role_reads.py governance/project/path-map.yaml'
step 'git commit -m "ACT-G14: role separation from the path map (DEC-1052 G-14): role_paths: engineer {ticket_tests}, test designer {ticket_impl} (c3)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1052" --trailer "Role: owner"'
step 'git rev-parse HEAD > $D/backup/act-commit && cut -c1-12 $D/backup/act-commit'
echo
echo "== §4 (the rollback)"
step "cd $R && D=.gov-runtime/scratch/orchestrator/drafts/g14 && read -r H < \$D/backup/act-commit && git revert --no-commit \"\$H\" && git commit -m \"Revert ACT-G14 (\${H:0:12}): role separation from the path map\" --trailer \"Task: DAEO-sdxk\" --trailer \"Implements: DEC-1052\" --trailer \"Role: owner\" && cp -p \$D/backup/guard4_check.py .gov-runtime/scratch/orchestrator/tools/guard4_check.py && python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py --settings \$PWD | tail -1"
step 'sha256sum .claude/hooks/pretooluse.py governance/project/path-map.yaml $T/guard4_check.py | cut -c1-12; ls .claude/hooks/; git status --short -- .claude/ governance/project/path-map.yaml'
echo
echo "rehearsal done: $(date '+%Y-%m-%d %H:%M:%S %Z')"
