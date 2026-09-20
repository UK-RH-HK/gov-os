#!/usr/bin/env bash
# P2-AR-0055 — OD-P2-03 §3.3 probe: can a project weaken the governed rule or the authorised envelope through
# PROJECT_POLICY.policy_overrides? The report claims it cannot, because POLICY_PRECEDENCE's existing
# `CHANGE_POLICY.*` and `TOOL_POLICY.*` catch-alls are `immutable` and were NOT changed by this run. This probe
# asks the product instead of arguing from the rules.
#
# It reuses a project an already-run certification scenario left behind (the harness keeps its temp roots), so it
# exercises a genuinely installed, provisioned project and the release `gov` of this worktree. It writes only into
# that scrap project.
#
# usage: run-precedence-probe.sh <project-root>
set -u
P="${1:?project root}"
WT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
GOV="$WT/target/release/gov"
KEY=$(printf '%s' "$P" | sha256sum | cut -c1-16)
export XDG_STATE_HOME="${TMPDIR:-/tmp}/gov-cert-machine/$KEY"
export GOV_CANONICAL_ROOT="$WT"
run() { "$GOV" --json --root "$P" --session S-od3-probe --role orchestrator "$@"; }

echo "# project: $P"
echo "# gov: $GOV sha256 $(sha256sum "$GOV" | cut -c1-64)"
echo
echo "## before: the shipped rule and envelope as the project reads them"
run policy effective CHANGE_POLICY | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps(d["result"]["effective"].get("change_classes"), indent=1)[:1200])'
run policy effective TOOL_POLICY | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps(d["result"]["effective"].get("installation_envelope"), indent=1)[:900])'
echo
echo "## the project tries to weaken both: empty two envelope floors, drop five expansion triggers, drop a condition"
python3 - "$P" <<'PY'
import sys, yaml
p = sys.argv[1] + "/governance/project/PROJECT_POLICY.yaml"
d = yaml.safe_load(open(p)) or {}
d.setdefault("policy_overrides", {})
d["policy_overrides"]["TOOL_POLICY.installation_envelope.host_authority_tokens"] = []
d["policy_overrides"]["TOOL_POLICY.installation_envelope.credential_patterns"] = []
d["policy_overrides"]["CHANGE_POLICY.change_classes.tool_installation.authority_expansion_triggers"] = ["privilege_escalation"]
d["policy_overrides"]["CHANGE_POLICY.change_classes.tool_installation.non_gated_conditions.within_authorised_envelope"] = "tool_registered"
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
print("PROJECT_POLICY.policy_overrides written:", *sorted(d["policy_overrides"]), sep="\n  ")
PY
echo
echo "## gov policy overrides"
run policy overrides | python3 -c '
import json,sys
d=json.load(sys.stdin)["result"]
for k in ("applied","refused"):
    print(f"{k}:")
    for r in d.get(k, []):
        print("  ", r.get("policy","?")+"."+r.get("key","?"), "->", r.get("reason") or r.get("mode") or "")
'
echo
echo "## after: the effective rule and envelope (must be the shipped ones, unchanged)"
run policy effective CHANGE_POLICY | python3 -c 'import json,sys; d=json.load(sys.stdin); c=d["result"]["effective"]["change_classes"]["tool_installation"]; print("triggers:", c["authority_expansion_triggers"]); print("within_authorised_envelope ->", c["non_gated_conditions"]["within_authorised_envelope"])'
run policy effective TOOL_POLICY | python3 -c 'import json,sys; d=json.load(sys.stdin); e=d["result"]["effective"]["installation_envelope"]; print("host_authority_tokens:", len(e["host_authority_tokens"]), "tokens"); print("credential_patterns:", e["credential_patterns"])'
echo
echo "## and the network allowlist the envelope compares against is not policy at all: it is kernel tool-registry payload"
python3 -c 'import yaml,sys; d=yaml.safe_load(open(sys.argv[1]+"/governance/kernel/tools/registry/TOOLS.yaml")); print("governance/kernel/tools/registry/TOOLS.yaml network_allowlist:", d["network_allowlist"])' "$P"
