set -u
S="$PWD/governance/project/orchestration/tools/dispatch/launch_now.sh"
T="$(mktemp -d)" || exit 1
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/orch/tools" "$T/orch/briefs" "$T/orch/log" "$T/bin" "$T/runs" "$T/trees/W9-1/.claude/templates"
echo 'exit 0' > "$T/orch/tools/disk_gate.sh"
echo brief > "$T/orch/briefs/B.md"
echo '# lead' > "$T/trees/W9-1/.claude/templates/role-lead.md"
sed -e "s#^ORCH=.*#ORCH=$T/orch#" -e "s#/home/[A-Za-z0-9_.-]*/gov-os-worktrees#$T/trees#g" \
    -e "s#/home/[A-Za-z0-9_.-]*/gov-os-runs#$T/runs#g" -e "s#/home/[A-Za-z0-9_.-]*/[.]local/bin#$T/bin#g" "$S" > "$T/launch.sh"
grep -q "/home/" "$T/launch.sh" && { echo "the bed's launcher still names a real home path"; exit 1; }
printf '#!/bin/bash\nprintf "%%s\\n" "$@" > "%s/argv.txt"\npwd > "%s/cwd.txt"\nexit 0\n' "$T" "$T" > "$T/bin/claude"
printf '#!/bin/bash\ncase "$*" in *--register*) exit 0;; esac\nexit "$(cat "%s/check.rc")"\n' "$T" > "$T/bin/gov"
chmod +x "$T/bin/claude" "$T/bin/gov"
echo 0 > "$T/check.rc"
added() { awk 'p{print; p=0} $0=="--add-dir"{p=1}' "$T/argv.txt" | paste -sd' '; }
# 1. a fresh lead: no tests folder yet; the line carries both --add-dir, the tests folder is made, empty
bash "$T/launch.sh" W9-1 DAEO-x B.md L.json < /dev/null > /dev/null 2>&1 || { echo "fresh lead: exit $?"; exit 1; }
[ "$(added)" = "$T/trees/W9-1-tests $T/runs" ] || { echo "fresh lead: --add-dir values are '$(added)'"; exit 1; }
[ "$(grep -n -- '--add-dir' "$T/argv.txt" | head -1 | cut -d: -f1)" -lt "$(grep -n -- '--append-system-prompt-file' "$T/argv.txt" | cut -d: -f1)" ] || { echo "the --add-dir pairs are not before the template flag"; exit 1; }
[ "$(tail -2 "$T/argv.txt" | head -1)" = "--append-system-prompt-file" ] || { echo "the template flag is not last"; exit 1; }
[ -d "$T/trees/W9-1-tests" ] && [ -z "$(ls -A "$T/trees/W9-1-tests")" ] || { echo "fresh lead: the tests folder was not made empty"; exit 1; }
[ "$(cat "$T/cwd.txt")" = "$T/trees/W9-1" ] || { echo "the lead does not start in its own tree"; exit 1; }
[ -z "$(ls -A "$T/runs")" ] || { echo "something was made in the runs root"; exit 1; }
# 2. a resumed lead: its tests worktree is there and is left as it is
echo kept > "$T/trees/W9-1-tests/kept.txt"
bash "$T/launch.sh" W9-1 DAEO-x B.md L.json < /dev/null > /dev/null 2>&1 || { echo "resumed lead: exit $?"; exit 1; }
[ "$(ls -A "$T/trees/W9-1-tests")" = kept.txt ] || { echo "resumed lead: the tests folder was changed"; exit 1; }
[ "$(added)" = "$T/trees/W9-1-tests $T/runs" ] || { echo "resumed lead: --add-dir values are '$(added)'"; exit 1; }
# 3. a refused start (the resource gate shut) makes no tests folder and starts nothing
rm -rf "$T/trees/W9-1-tests" "$T/argv.txt"
echo 3 > "$T/check.rc"
bash "$T/launch.sh" W9-1 DAEO-x B.md L.json < /dev/null > /dev/null 2>&1
rc=$?
[ "$rc" = 3 ] && [ ! -e "$T/argv.txt" ] && [ ! -e "$T/trees/W9-1-tests" ] || { echo "shut gate: exit $rc, or a start or a folder"; exit 1; }
echo "launch_now.sh: the lead line adds its own tests worktree and the runs root, makes the tests folder empty when absent, keeps an existing one, and a refused start makes nothing"
exit 0
