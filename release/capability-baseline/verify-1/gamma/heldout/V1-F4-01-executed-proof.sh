#!/usr/bin/env bash
# Gamma held-out probe: the executed proof behind finding V1-F4-01.
# A non-elevated, reviewed, pinned, reversible tool installation whose install command is wrapped in `sh -c`
# writes a file OUTSIDE the project root — "broader filesystem or project access", an OD-P2-03 authority-expansion
# trigger — while the OS records expands_authority false, triggers_fired [], undetermined [] and installs it with
# no Human Gate.
. "$(dirname "$0")/lib.sh"
newproj execproof --provision >/dev/null
RPT=$(security_review TL-EXEC 1.0.0)
case "$RPT" in RPT-*) ok "setup: an independent governed security review of TL-EXEC 1.0.0 exists ($RPT)";; *) bad "setup: no review"; summary; exit 1;; esac
OUT="$LAB/ESCAPED-execproof-$$.txt"
descriptor "$LAB/exec.yaml" "$RPT" "{\"tool_id\":\"TL-EXEC\",\"version_pin\":\"1.0.0\",\"install_command\":[\"sh\",\"-c\",\"printf escaped > $OUT; echo done\"]}"
res=$(GOV_SESSION=exec1 g tooling-engineer tools install --descriptor "$LAB/exec.yaml" --execute | python3 -c "
import sys,json
d=json.load(sys.stdin); r=d.get('result',d); cc=r.get('change_class',{}); e=cc.get('authority_envelope',{})
print('%s|%s|%s|%s|%d' % (r.get('installed'), r.get('human_gate') or 'none', cc.get('branch'),
                          e.get('expands_authority'), len(e.get('undetermined') or [])))")
echo "    installed|gate|branch|expands|undetermined = $res"
outside=$(python3 -c "
import os
print('outside' if os.path.exists('$OUT') and not os.path.realpath('$OUT').startswith(os.path.realpath('$PROJ')+os.sep) else 'no')")
if [ "$outside" = "outside" ]; then
  bad "OD-P2-03: an ungated installation ($res) executed a command that wrote OUTSIDE the project root — the authority-expansion trigger 'broader_filesystem_or_project_access' was neither fired nor recorded as undetermined"
else
  ok "OD-P2-03: the installation did not reach outside the project root ($res)"
fi

# And --execute is not the boundary: the descriptor's health_check command runs at every installation.
RPT2=$(security_review TL-HC 1.0.0)
OUT2="$LAB/ESCAPED-healthcheck-$$.txt"
descriptor "$LAB/hc.yaml" "$RPT2" "{\"tool_id\":\"TL-HC\",\"version_pin\":\"1.0.0\",\"health_check\":{\"kind\":\"command\",\"command\":[\"sh\",\"-c\",\"printf hc > $OUT2; echo ok\"]}}"
res2=$(GOV_SESSION=hc1 g tooling-engineer tools install --descriptor "$LAB/hc.yaml" | python3 -c "
import sys,json
d=json.load(sys.stdin); r=d.get('result',d); cc=r.get('change_class',{})
print('%s|%s|%s' % (r.get('installed'), r.get('human_gate') or 'none', cc.get('branch')))")
echo "    (no --execute) installed|gate|branch = $res2"
outside2=$(python3 -c "
import os
print('outside' if os.path.exists('$OUT2') and not os.path.realpath('$OUT2').startswith(os.path.realpath('$PROJ')+os.sep) else 'no')")
if [ "$outside2" = "outside" ]; then
  bad "OD-P2-03: a shell-wrapped health_check command wrote OUTSIDE the project root on an ungated installation WITHOUT --execute — --execute is not the boundary"
else
  ok "OD-P2-03: the health_check command did not reach outside the project root without --execute ($res2)"
fi
summary
