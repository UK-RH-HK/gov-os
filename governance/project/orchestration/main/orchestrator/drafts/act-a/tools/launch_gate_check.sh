set -u
S="$PWD/governance/project/orchestration/tools/dispatch/launch_now.sh"
T="$(mktemp -d)" || exit 1
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/orch/tools" "$T/orch/briefs" "$T/orch/log" "$T/bin" "$T/trees/W9-1/.claude/templates"
echo 'exit 0' > "$T/orch/tools/disk_gate.sh"
echo brief > "$T/orch/briefs/B.md"
echo '# lead' > "$T/trees/W9-1/.claude/templates/role-lead.md"
sed -e "s#^ORCH=.*#ORCH=$T/orch#" -e "s#/home/[A-Za-z0-9_.-]*/gov-os-worktrees#$T/trees#g" -e "s#/home/[A-Za-z0-9_.-]*/[.]local/bin#$T/bin#g" "$S" > "$T/launch.sh"
grep -q "$T/bin/gov" "$T/launch.sh" || { echo "the launcher names no gov of its own"; exit 1; }
printf '#!/bin/bash\necho "$$" > "%s/lead.pid"\nexit 0\n' "$T" > "$T/bin/claude"
printf '#!/bin/bash\necho "$*" >> "%s/gov.calls"\ncase "$*" in *--register*) exit 0;; esac\nexit "$(cat "%s/check.rc")"\n' "$T" "$T" > "$T/bin/gov"
chmod +x "$T/bin/claude" "$T/bin/gov"
echo 0 > "$T/check.rc"
bash "$T/launch.sh" W9-1 DAEO-x B.md L.json < /dev/null > /dev/null 2>&1
rc=$?
[ "$rc" = 0 ] && [ -f "$T/lead.pid" ] || { echo "open gate: the lead did not start (exit $rc)"; exit 1; }
[ "$(sed -n 1p "$T/gov.calls")" = "resources --check" ] || { echo "the gate was not checked first"; exit 1; }
[ "$(sed -n 2p "$T/gov.calls")" = "resources --register $(cat "$T/lead.pid") --ticket DAEO-x --session-role orchestrator" ] || { echo "the lead's own pid was not registered"; exit 1; }
rm -f "$T/lead.pid" "$T/gov.calls"
echo 3 > "$T/check.rc"
bash "$T/launch.sh" W9-1 DAEO-x B.md L.json < /dev/null > /dev/null 2>&1
rc=$?
[ "$rc" = 3 ] || { echo "shut gate: exit $rc, not 3"; exit 1; }
[ ! -f "$T/lead.pid" ] || { echo "shut gate: the lead started"; exit 1; }
grep -q -- "--register" "$T/gov.calls" && { echo "shut gate: a lead was registered"; exit 1; }
echo "launch_now.sh: open gate checks, registers its own pid and starts; shut gate starts nothing"
exit 0
