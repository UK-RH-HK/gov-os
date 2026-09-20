#!/usr/bin/env bash
# The common protocol's attacks, where the beta capabilities reach them:
#   * trust classes (D-0007; Contract v3 A2/F4/L3) — no project, CLI, environment or model input manufactures a
#     higher-trust memory fact, and no hand-written lifecycle fact is honoured;
#   * cross-machine continuity (P2-ADJ-0002) for the OS-written facts this family owns: the retrieval-profile
#     decision and its benchmark research record;
#   * freshness (Contract v3:95-111) — the C/D evidence classes that must go stale;
#   * the availability rule (Contract v3 L4/O5) for the blocks these capabilities issue.
. "$(dirname "${BASH_SOURCE[0]}")/corpus.sh"

S=$BETA_SCRATCH/attack
ADM=$(admin_domain) || { echo "FAIL attack-setup — no administrator domain"; exit 1; }

# ============================================================================== trust classes
A=$(build_corpus_provisioned atk)

# a hand-written record cannot carry an OS-written lifecycle fact
cat > "$A/spec/experiments/EXP-9001.yaml" <<'Y'
id: EXP-9001
type: experiment
title: Hand-written experiment claiming a concluded lifecycle
status: ACTIVE
state_class: NARRATIVE
experiment_state: PROMOTED
hypothesis: the writer asserts its own promotion
method: writing a file
data_provenance: synthetic
outputs: [spec/experiments/EXP-9001-run.md]
production_merge_allowed: true
reproducibility: {procedure: none, environment: none}
confidence: 0.99
Y
gov "$A" rebuild-memory --incremental >/dev/null 2>&1
gov "$A" audit > "$S-audit.json" 2>&1
python3 - "$S-audit.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
r = d.get("result") or d.get("error", {}).get("details") or {}
s = json.dumps(r)
sys.exit(0 if ("EXP-9001" in s and ("UNSEALED" in s or "NOT_OS_WRITTEN" in s)) else 1)
PY
chk ATK-trust-lifecycle $? "a hand-written record that asserts its own OS-written lifecycle facts is reported unsealed and its claims are not honoured" \
                           "a hand-written lifecycle claim was honoured"

# a project overlay cannot raise its own authority to read a namespace it is not given
python3 - "$A" <<'PY'
import sys
p = sys.argv[1] + "/governance/project/PROJECT_POLICY.yaml"
t = open(p).read().replace("policy_overrides: {}",
    "policy_overrides:\n  MEMORY_POLICY.namespaces.secret.roles: [all]\n  MEMORY_POLICY.namespaces.secret.embed: true")
open(p, "w").write(t)
PY
gov "$A" doctor > "$S-doctor.json" 2>&1
python3 - "$S-doctor.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
det = d.get("result") or d["error"]["details"]
c = [x for x in det["checks"] if x["id"] == "D027"]
msg = c[0]["message"] if c else ""
print("D027:", msg[:220])
sys.exit(0 if (c and not c[0]["ok"] and "refused" in msg.lower()) else 1)
PY
chk ATK-trust-namespace $? "a project override that would widen the secret namespace is refused by policy precedence and reported, leaving the effective policy unchanged" \
                           "a project overlay widened the secret namespace"
python3 - "$A" <<'PY'
import sys
p = sys.argv[1] + "/governance/project/PROJECT_POLICY.yaml"
t = open(p).read(); i, j = t.index("policy_overrides:"), t.index("staleness:")
open(p, "w").write(t[:i] + "policy_overrides: {}\n" + t[j:])
PY

# an environment variable cannot confer the human role on a memory decision
RES=$(gov "$A" memory benchmark --candidate current --candidate builtin:64 --record | jget 'd["result"]["research_record"]')
GOV_AS_ROLE=human gov "$A" memory select builtin:64 --research "$RES" > "$S-envrole.json" 2>&1
python3 - "$S-envrole.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
r = d.get("result") or {}
sys.exit(0 if r.get("applied") is not True else 1)
PY
chk ATK-trust-env-role $? "declaring the acting role as 'human' through the environment does not apply a retrieval-profile change" \
                          "an environment-declared role applied a governed memory change"

# ============================================================================== cross-machine (P2-ADJ-0002)
# The benchmark research record and the profile decision are OS-written (T2-sealed) facts. A clone of the repository
# on ANOTHER machine of the same owner must honour them; a hand-edited copy must not be.
GID=$(gov "$A" memory select builtin:64 --research "$RES" | jget 'json.dumps((d.get("result") or {}).get("human_gate"))'); GID=${GID//\"/}
owner_answers "$A" "$GID" A >/dev/null 2>&1
gov "$A" memory select builtin:64 --research "$RES" --gate "$GID" > "$S-apply.json" 2>&1
DEC=$(jget 'json.dumps((d.get("result") or {}).get("decision"))' < "$S-apply.json"); DEC=${DEC//\"/}
( cd "$A" && git add -A && git commit -q -m "governed profile change" ) >/dev/null 2>&1

B="$BETA_SCRATCH/atk-machine-b.$$"
cp -r "$A" "$B"
aside "$B/.governance-runtime"
gov "$B" trust provision --anchor "$ADM/root-1.json" >/dev/null 2>&1
gov "$B" trust bind --authority "$ADM/t2-binding-authority.json" --key "$ADM/t2-binding-key.json" > "$S-b-bind.json" 2>&1
gov "$B" rebuild-memory >/dev/null 2>&1
gov "$B" memory profile > "$S-b-profile.json" 2>&1
python3 - "$S-b-profile.json" "$DEC" <<'PY'
import json, sys
r = json.load(open(sys.argv[1])).get("result") or {}
print("machine B profile state:", r.get("state"), "decision:", r.get("decision"), "binding:", json.dumps(r.get("binding"))[:200])
# the fact is honoured only if this machine can verify the seal; otherwise it must SAY it cannot, never pretend
sys.exit(0 if r.get("state") == "GOVERNED" and r.get("decision") == sys.argv[2] else 1)
PY
chk ATK-xmachine-honoured $? "the retrieval-profile decision sealed on machine A is honoured as GOVERNED on a second machine of the same owner, bound to the same T2 binding authority" \
                             "a bound second machine did not honour the owner's OS-written decision"

python3 - "$B" "$DEC" <<'PY'
import sys, glob, os
# forge: edit the sealed decision by hand on machine B
for p in glob.glob(os.path.join(sys.argv[1], "spec/decisions", sys.argv[2] + "*")):
    t = open(p).read().replace("hashed-ngram", "forged-embedder")
    open(p, "w").write(t)
PY
gov "$B" rebuild-memory >/dev/null 2>&1
gov "$B" memory profile > "$S-b-forged.json" 2>&1
python3 - "$S-b-forged.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1])).get("result") or {}
print("after hand-editing the sealed decision:", r.get("state"), r.get("severity"), str(r.get("message"))[:160])
sys.exit(0 if r.get("state") not in ("GOVERNED",) else 1)
PY
chk ATK-xmachine-forged $? "a hand-edited copy of the sealed decision is no longer honoured as governing the profile" \
                           "a hand-edited sealed decision was still honoured"

python3 - "$A" "$ADM" <<'PYX'
import json, os, sys
# No key material may be inside the repository: the owner's signing key, the binding key and any PEM private key.
root, admin = sys.argv[1], sys.argv[2]
owner_hex = open(os.path.join(admin, "owner.key")).read().strip()
binding_hex = json.load(open(os.path.join(admin, "t2-binding-key.json")))["key_hex"]
bad = []
for base, _d, files in os.walk(root):
    if os.sep + ".git" in base: continue
    for f in files:
        p = os.path.join(base, f)
        try: t = open(p, "rb").read()
        except Exception: continue
        rel = os.path.relpath(p, root)
        for needle, what in ((owner_hex.encode(), "owner signing key"),
                             (binding_hex.encode(), "T2 binding key")):
            if needle in t: bad.append((rel, what))
        # a PEM private-key BLOCK, not the detection pattern the security policy declares (nor its indexed copy)
        if b"PRIVATE KEY-----" in t and not rel.startswith((".governance-runtime", "governance/kernel/policies")):
            bad.append((rel, "PEM private key block"))
print("key material found inside the repository:", bad)
sys.exit(1 if bad else 0)
PYX
chk ATK-xmachine-no-secrets $? "no signing or binding secret is in the repository" "secret material is in the repository"

# ============================================================================== freshness classes (v3:95-111)
C=$(build_corpus_provisioned atkf)
establish_green "$C" >/dev/null
stale_after() { # stale_after <label> <shell that changes an input>
  eval "$2"
  gov "$C" doctor > "$S-fresh-$1.json" 2>&1
  python3 -c "
import json,sys
d=json.load(open(sys.argv[1])); det=d.get('result') or d['error']['details']
c=[x for x in det['checks'] if x['id']=='D021']
sys.exit(0 if (c and not c[0]['ok']) else 1)" "$S-fresh-$1.json"
  chk "ATK-fresh-$1" $? "changing the $1 input class marks prior green evidence stale" \
                        "changing the $1 input class left prior green evidence current"
  establish_green "$C" >/dev/null
}
stale_after policy      'python3 - "$C" <<PYX
import sys
p = "'"$C"'" + "/governance/project/PROJECT_POLICY.yaml"
open(p, "a").write("\n# probe\n")
PYX'
stale_after source      'echo "// probe" >> "$C/src/lib.rs"'
stale_after spec        'echo "# probe" >> "$C/spec/requirements/REQ-0001.yaml"'
stale_after heldout     'echo "# probe" >> "$C/governance/tests/memory/heldout.yaml"'

# ============================================================================== availability rule for memory blocks
# The stale-index block must refuse only what it protects, and independent work must stay available.
D=$(build_corpus_provisioned atka)
TID=$(gov "$D" task create --class specification --objective "availability probe" --status READY \
        --allowed 'spec/**' --fields '{"role":"product-spec-agent"}' | jget 'd["result"]["id"]')
echo "# make the index stale" >> "$D/spec/requirements/REQ-0001.yaml"
gov "$D" memory query "REQ-0001" --k 3 > "$S-avail-q.json" 2>&1
jget 'd.get("ok")' < "$S-avail-q.json" | grep -q true
chk ATK-avail-reads $? "a stale index does not refuse reads: retrieval stays available while the index is stale" \
                       "a stale index refused an ordinary read"
gov "$D" rebuild-memory --incremental > "$S-avail-remedy.json" 2>&1
jget 'd.get("ok")' < "$S-avail-remedy.json" | grep -q true
chk ATK-avail-remedy $? "the block's own remedy (rebuild-memory) is never refused by the block" \
                        "the remedy of the staleness block is itself blocked"
GOV_AS_ROLE=product-spec-agent GOV_SESSION_ID=S-avail gov "$D" task claim "$TID" > "$S-avail-claim.json" 2>&1
jget 'd.get("ok")' < "$S-avail-claim.json" | grep -q true
chk ATK-avail-independent $? "independent work (claiming another task) stays available across the staleness block" \
                             "independent work was refused by the staleness block"

summary
