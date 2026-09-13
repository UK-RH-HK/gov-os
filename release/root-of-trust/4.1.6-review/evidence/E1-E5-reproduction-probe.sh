#!/usr/bin/env bash
# Root-of-trust escalation probes against the rejected 4.1.5 binary. Scratch-only; the repository is never written.
set -u
REPO=/home/usain/Dynamic-Agentic-Engineering-OS
GOV=$REPO/target/release/gov
SP=/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/cdefc3cb-122e-45bf-868b-fe9f6e3b077d/scratchpad
S=$(mktemp -d "$SP/repro/e-XXXX")
H="python3 $SP/regen.py"
echo "scratch: $S"

run() { env -u GOV_CANONICAL_ROOT -u GOV_ROLE -u GOV_SESSION -u GOV_KERNEL_SOURCE GOV_KERNEL_CACHE="$S/cache" "$GOV" --json "$@"; }
g() { local root=$1; shift; run --root "$root" --session S-probe --role orchestrator "$@"; }
mkrepo() { mkdir -p "$1" && (cd "$1" && git init -q && echo probe > README.md && git add README.md && git -c user.name=p -c user.email=p@x commit -q -m init); }
pick() { python3 -c "import json,sys
d=json.load(sys.stdin)
out={}
for path in sys.argv[1:]:
    v=d
    for part in path.split('.'):
        v=v.get(part) if isinstance(v,dict) else None
    out[path]=v
print(json.dumps(out))" "$@"; }

echo; echo "=== P1 stale-manifest tamper (V-H3 as reported) vs regenerated-manifest tamper: gov release verify"
cp -r "$REPO/release/releases/4.1.5" "$S/src-stale"
$H strip "$S/src-stale/kernel/policies/SECURITY_POLICY.yaml"
run release verify "$S/src-stale" | pick ok result.ok result.modified result.release_hash_matches_kernel
cp -r "$REPO/release/releases/4.1.5" "$S/src-regen"
$H strip "$S/src-regen/kernel/policies/SECURITY_POLICY.yaml"
$H release "$S/src-regen" --certify
run release verify "$S/src-regen" | pick ok result.ok result.modified result.release_hash_matches_kernel result.certification.status

echo; echo "=== P2 self-certified regenerated source: update gate decision and apply WITHOUT --approve"
C=$S/consumer-a; mkrepo "$C"
g "$C" init --source "$REPO/release/releases/4.1.4" --name probe --skip-index | pick ok result.version error.code
g "$C" update --check --source "$S/src-regen" | pick ok result.current result.available result.certification result.human_gate_required result.recommendation error.code
g "$C" update --apply --source "$S/src-regen" | pick ok result.applied result.reason error.code error.message
g "$C" kernel trust | pick ok result.verified result.substituted_embedded_baseline result.installed_version
python3 -c "import yaml,sys; l=yaml.safe_load(open(sys.argv[1])); print({k:l.get(k) for k in ['version','release_hash','source','release_commit']})" "$C/governance/framework.lock"
echo "installed never_index_classes:"; $H classes "$C/governance/kernel/policies/SECURITY_POLICY.yaml"
echo "published 4.1.5 release_hash: $(python3 -c "import json;print(json.load(open('$REPO/release/releases/4.1.5/manifest.json'))['release_hash'])")"
echo "update gates in consumer-a:"; ls "$C/spec/decisions" 2>/dev/null | grep -c -i gate || true
grep -l 'framework_update' -r "$C/spec" 2>/dev/null | head -3

echo; echo "=== P3 embedded-baseline cache: poison the materialised cache, then init with no --source"
T=$S/throwaway; mkrepo "$T"
g "$T" init --name t --skip-index | pick ok result.source error.code
CACHEDIR=$(ls -d "$S"/cache/kernels/4.1.5-* | head -1); echo "cache: $CACHEDIR"
$H strip "$CACHEDIR/policies/SECURITY_POLICY.yaml"
C3=$S/consumer-embedded; mkrepo "$C3"
g "$C3" init --name e --skip-index | pick ok result.source error.code
g "$C3" kernel trust | pick ok result.verified result.source
echo "installed never_index_classes (C3):"; $H classes "$C3/governance/kernel/policies/SECURITY_POLICY.yaml"
echo "--- P3b V-H2 fallback reads the poisoned cache: tamper T's installed kernel (intact before poisoning)"
echo "# probe" >> "$T/governance/kernel/policies/POLICY_PRECEDENCE.yaml"
g "$T" kernel trust | pick ok result.verified result.substituted_embedded_baseline result.source
g "$T" policy effective SECURITY_POLICY > "$S/t-effective.json"; python3 -c "
import json,sys; d=json.load(open(sys.argv[1])); r=d.get('result',{})
def find(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if k=='never_index_classes': print('effective never_index_classes:', v)
            else: find(v)
    elif isinstance(o,list):
        for x in o: find(x)
find(r); print('ok', d.get('ok'), (d.get('error') or {}).get('code'))" "$S/t-effective.json"

echo; echo "=== P4 coherent in-repo replacement (git-pull shape): edit installed kernel + regenerate manifest + lock"
C4=$S/consumer-git; mkrepo "$C4"
g "$C4" init --source "$REPO/release/releases/4.1.5" --name g --skip-index | pick ok result.version
$H strip "$C4/governance/kernel/policies/SECURITY_POLICY.yaml"
g "$C4" kernel trust | pick result.verified
$H installed "$C4"
g "$C4" kernel trust | pick ok result.verified result.substituted_embedded_baseline
g "$C4" doctor > "$S/c4-doctor.json"; python3 -c "
import json,sys; d=json.load(open(sys.argv[1])); r=d.get('result') or (d.get('error') or {}).get('details') or {}
print({c['id']:c['ok'] for c in r.get('checks',[]) if c['id'] in ('D003','D004','D029')})" "$S/c4-doctor.json"

echo; echo "=== P5 rollback snapshot: tamper the update snapshot of consumer-a, then gov update --rollback"
SNAP=$(ls -d "$C"/.governance-runtime/update/*/ | head -1); echo "snapshot: $SNAP"
$H strip "$SNAP/kernel/policies/SECURITY_POLICY.yaml"
$H snapshot "$SNAP"
g "$C" update --rollback --reason probe | pick ok result.kernel_ok result.rolled_back_to error.code
g "$C" kernel trust | pick ok result.verified result.installed_version
echo "installed never_index_classes after rollback:"; $H classes "$C/governance/kernel/policies/SECURITY_POLICY.yaml"
echo; echo "done: $S"
