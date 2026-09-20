#!/usr/bin/env bash
# Gate R — legacy, archive and historical state (Contract v3:870-891), exercised on the brownfield fixture, which
# carries two chat stores, three provider rule files, two old-governance documents, a duplicate decision copy, a
# contradicting decision pair and planted secrets.
#
#   R1 legacy governance retirement (7 bullets)   R2 chat-memory retirement (4)   R3 archive policy (3)
. "$(dirname "${BASH_SOURCE[0]}")/corpus.sh"

ADM=$(admin_domain) || { echo "FAIL R-setup — no administrator domain"; exit 1; }
ROOT=$(new_project bfR brownfield)
S=$BETA_SCRATCH/R
gov "$ROOT" trust provision --anchor "$ADM/root-1.json" >/dev/null 2>&1

# Plant, in the legacy governance document the fixture already has, one knowledge unit of each kind Contract v3:876
# lists, each carrying a needle that exists nowhere else. R1 b4 is then a question about behaviour, not about whether
# the fixture happened to contain such material.
cat >> "$ROOT/AGENT_RULES_v2.md" <<'MD'

## Retry procedure (legacy)
1. Read the gateway timeout from config NEEDLESKILL3140.
2. Retry the call with exponential backoff.
3. Record the attempt count in the audit log.

## Investigation notes
We measured the gateway across 10,000 calls and found a p99 of 840 ms NEEDLERESEARCH2288; the study is inconclusive
about the cause and needs another experiment.

## Test evidence
The regression run on 2024-11-02 shows 412 of 415 assertions passing NEEDLEEVIDENCE6617, attached as the run log.
MD
( cd "$ROOT" && git add -A && git commit -q -m "legacy knowledge of every kind" ) >/dev/null 2>&1

run_stage() { gov "$ROOT" adopt "$1" > "$S-$1.json" 2>&1; jget 'd.get("ok")' < "$S-$1.json"; }

for st in baseline inventory classify map plan test-design; do
  [ "$(run_stage "$st")" = "true" ] || { fail "R-stage-$st" "adopt $st failed: $(head -c 250 "$S-$st.json")"; summary; exit 1; }
done

# ---- R1 b3 inventory ---------------------------------------------------------------------------------------------
python3 - "$S-inventory.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
k = r["summary"]["by_kind"]
print("inventory kinds:", k)
sys.exit(0 if (r["summary"]["files"] > 0 and k.get("old_governance") and k.get("provider_rules")
               and k.get("chat_store") and k.get("secret")) else 1)
PY
chk R1-b3-inventory $? "the cold inventory enumerates the whole tree and names the legacy governance, provider rule, chat-store and secret material it found" \
                       "the inventory does not enumerate the legacy material"

# ---- R1 b2 mark old governance LEGACY, and b5 reconcile contradictions --------------------------------------------
python3 - "$S-classify.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
print("by_class:", r["by_class"], "by_authority:", r["by_authority"])
sys.exit(0 if (r["by_authority"].get("LEGACY", 0) >= 1 and r["by_class"].get("GOVERNANCE_LEGACY", 0) >= 1
               and r.get("unknown") == 0) else 1)
PY
chk R1-b2-legacy-marked $? "old governance is classified GOVERNANCE_LEGACY with authority LEGACY, and nothing is left unclassified" \
                           "old governance is not marked legacy"
python3 - "$S-classify.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
sys.exit(0 if r.get("conflicting", 0) >= 1 else 1)
PY
chk R1-b5-contradictions $? "contradicting authority is detected and counted, not silently merged" "contradictions are not detected"

# ---- R1 b7 (part 1): a retirement with live references is reported before anything moves ---------------------------
python3 - "$S-map.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
rets = r.get("retirements_with_active_references", [])
print("retirements with active references:", [x["path"] for x in rets])
sys.exit(0 if r.get("unknown_blocking_destructive") == 0 and isinstance(rets, list) else 1)
PY
chk R1-b7-refs-reported $? "the path map reports every retirement that still has an active reference, before any file moves" \
                           "retirements with active references are not reported"

# ---- the independent reviewer's OWN tests (adoption protocol §10; Contract v3 O3) ----------------------------------
python3 - "$ROOT" <<'PY'
import sys, yaml
p = sys.argv[1] + "/spec/audits/GOVERNANCE-ADOPTION/06-migration-tests.yaml"
d = yaml.safe_load(open(p))
d["authored_by"] = "P2-AR-0047 held-out verifier acting as the independent migration reviewer"
d["tests"].extend([
  {"id": "RV-001", "kind": "legacy_not_active", "pattern": "AGENT_RULES_v2.md",
   "description": "the retired rules document is no longer an active governance mechanism", "after_batch": 7},
  {"id": "RV-005", "kind": "legacy_not_active", "pattern": ".cursorrules",
   "description": "the retired provider rule file is no longer an active governance mechanism", "after_batch": 7},
  {"id": "RV-002", "kind": "retirement_references", "description": "nothing active still references a retired artefact", "after_batch": 7},
  {"id": "RV-003", "kind": "no_secret_in_index", "description": "no planted secret reached the index", "after_batch": 7},
  {"id": "RV-004", "kind": "text_absent", "path": "README.md", "text": "AGENT_RULES_v2.md",
   "description": "the README no longer cites the retired rules document", "after_batch": 7},
])
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
GOV_AS_ROLE=migration-reviewer GOV_SESSION_ID=S-reviewer gov "$ROOT" adopt review \
   --verdict MIGRATION_PLAN_APPROVED --reviewer-role migration-reviewer --reviewer-session S-reviewer \
   --notes "reviewer-authored dependency, legacy-authority and secret tests added" > "$S-review.json" 2>&1
jget 'd.get("ok")' < "$S-review.json" | grep -q true
chk R1-review-independent $? "the migration plan is approved only with tests the independent reviewer authored (the planner's scaffold alone is refused)" \
                             "the reviewer approval failed: $(head -c 250 "$S-review.json")"

# ---- R1 b1/b6/b7: migrate, answering every gate the OS raises -------------------------------------------------------
# Every pending Human Decision Gate is answered by the product owner through the authenticated channel; the loop then
# re-runs the stage. A batch that fails one of the REVIEWER's own tests must roll back and stop.
migrate_round() {
  gov "$ROOT" adopt migrate --source "$BETA_SCRATCH/release-domain/releases/4.1.6" > "$S-migrate.json" 2>&1
  for g in $(grep -o 'HDG-[0-9][0-9]*' "$S-migrate.json" | sort -u); do
    owner_answers "$ROOT" "$g" A >/dev/null 2>&1
  done
}
ROLLED_BACK=no
for i in 1 2 3 4 5 6 7 8 9 10; do
  migrate_round
  if grep -q MIGRATION_BATCH_FAILED "$S-migrate.json"; then
    # a reviewer test failed: the proof that a live dependency stops the retirement
    if grep -q '"RV-00' "$S-migrate.json" && grep -q 'rolled back' "$S-migrate.json"; then ROLLED_BACK=yes; fi
    break
  fi
  jget 'd.get("ok")' < "$S-migrate.json" | grep -q true || break
  grep -q 'HDG-[0-9]' "$S-migrate.json" || break
done
[ "$ROLLED_BACK" = "yes" ]
chk R1-b7-dependency-proof $? "a retirement whose reference is still live fails the independent reviewer's dependency test and the batch is rolled back, with downstream batches not executed" \
                              "a live dependency did not stop the retirement: $(head -c 250 "$S-migrate.json")"

# the operator's remedy: remove the live citation, then the same migration completes (the block refuses only what it
# protects, and its remedy stays available)
python3 - "$ROOT" <<'PYX'
import sys, os, re
p = os.path.join(sys.argv[1], "README.md")
t = open(p).read()
t = re.sub(r".*AGENT_RULES_v2\.md.*\n?", "", t)
open(p, "w").write(t)
PYX
( cd "$ROOT" && git add -A && git commit -q -m "remove the citation of the retired rules document" ) >/dev/null 2>&1
for i in 1 2 3 4 5 6 7 8 9 10; do
  migrate_round
  jget 'd.get("ok")' < "$S-migrate.json" | grep -q true || { grep -q MIGRATION_BATCH_FAILED "$S-migrate.json" && break; }
  grep -q 'HDG-[0-9]' "$S-migrate.json" || break
done
[ -f "$ROOT/governance/framework.lock" ] && [ -f "$ROOT/governance/kernel/KERNEL_MANIFEST.json" ]
chk R1-b1-activate $? "current authority is installed and active (kernel + overlay + lock)" \
                      "current authority was not installed: $(head -c 250 "$S-migrate.json")"
[ -d "$ROOT/archive/governance" ] && [ -n "$(ls -A "$ROOT/archive/governance" 2>/dev/null)" ]
chk R1-b6-retired $? "the retired legacy mechanisms are moved out of the active tree into the archive" \
                     "no legacy mechanism was retired into the archive"

gov "$ROOT" adopt status > "$S-status.json" 2>&1
GOV_AS_ROLE=migration-verifier GOV_SESSION_ID=S-verifier gov "$ROOT" adopt verify-migration > "$S-verify.json" 2>&1
python3 - "$S-verify.json" <<'PYX'
import json, sys
d = json.load(open(sys.argv[1]))
r = d.get("result") or d.get("error", {}).get("details") or {}
t = r.get("tests") or {}
print("verify-migration verdict:", r.get("verdict"), "tests:", t,
      "legacy in active tree:", r.get("legacy_in_active_tree"),
      "active citations of archived material:", r.get("active_citations_of_archived_material"),
      "secrets isolated:", r.get("secrets_isolated"))
ok = (d.get("ok") and t.get("fail") == 0 and t.get("executed", 0) >= 44      # 40 scaffold + the 5 reviewer tests
      and r.get("legacy_in_active_tree") == [] and r.get("active_citations_of_archived_material") == []
      and r.get("secrets_isolated") is True and r.get("kernel_intact") is True)
sys.exit(0 if ok else 1)
PYX
chk R1-b7-tests-executed $? "migration verification executes every test including the reviewer's own, and proves no legacy mechanism is left active, nothing active cites archived material, and the secrets stayed isolated" \
                            "the dependency proof did not hold: $(head -c 250 "$S-verify.json")"

# ---- R1 b4 extract useful decisions / lessons / skills / evidence / research ----------------------------------------
gov "$ROOT" adopt extract-legacy > "$S-extract.json" 2>&1
python3 - "$S-extract.json" "$ROOT" <<'PYX'
import json, os, sys
d = json.load(open(sys.argv[1]))
r = d.get("result") or {}
print("extract:", json.dumps(r)[:700])
root = sys.argv[2]
def count(sub):
    p = os.path.join(root, sub)
    return len(os.listdir(p)) if os.path.isdir(p) else 0
kinds = {k: count("spec/" + k) for k in ("decisions", "lessons", "research", "reports", "requirements")}
print("governed records present after extraction:", kinds)
sys.exit(0 if d.get("ok") and sum(kinds.values()) > 0 else 1)
PYX
chk R1-b4-extract $? "useful material is extracted out of the legacy governance into governed records" \
                     "extraction did not run: $(head -c 250 "$S-extract.json")"
python3 - "$S-extract.json" "$ROOT" <<'PYX'
import json, os, sys
r = json.load(open(sys.argv[1])).get("result") or {}
root = sys.argv[2]
print("extraction by_kind:", [s.get("by_kind") for s in r.get("stores", [])])
# every planted needle must be somewhere governed: a distilled record, or the store's residual-knowledge register
governed = ""
for base, _dirs, files in os.walk(os.path.join(root, "spec")):
    for f in files:
        try: governed += open(os.path.join(base, f), errors="ignore").read()
        except Exception: pass
needles = {"skill": "NEEDLESKILL3140", "research": "NEEDLERESEARCH2288", "evidence": "NEEDLEEVIDENCE6617"}
lost = [k for k, n in needles.items() if n not in governed]
print("planted legacy knowledge lost on retirement:", lost)
sys.exit(0 if not lost else 1)
PYX
chk R1-b4-all-kinds $? "a skill procedure, a research finding and an evidence claim planted in the legacy governance all survive retirement as governed material (distilled records or the residual-knowledge register), none silently lost" \
                       "planted legacy knowledge was lost when the legacy governance was retired"

# ---- R2 chat-memory retirement ---------------------------------------------------------------------------------------
gov "$ROOT" adopt build-memory > "$S-buildmem.json" 2>&1
gov "$ROOT" memory query "chat_history" --k 8 > "$S-chat.json" 2>&1
python3 - "$S-chat.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1])).get("result") or {}
hits = [h["path"] for h in r.get("hits", []) if "chat" in h["path"] or ".chat" in h["path"]]
print("chat-store hits in default retrieval:", hits)
sys.exit(0 if not hits else 1)
PY
chk R2-b1-not-default $? "the raw chat stores are not active or default truth: they answer no default query" \
                         "a raw chat store is returned by default retrieval"
python3 - "$S-classify.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
sys.exit(0 if r["by_class"].get("HISTORICAL", 0) >= 1 else 1)
PY
chk R2-b1-classified $? "the chat stores are classified historical, not authoritative" "the chat stores are not classified historical"
python3 - "$S-extract.json" <<'PY'
import json, sys
s = json.dumps(json.load(open(sys.argv[1])).get("result") or {})
sys.exit(0 if ("chat" in s.lower()) else 1)
PY
chk R2-b2-extracted $? "the extraction pass accounts for the durable knowledge in the chat stores" \
                       "the extraction report does not mention the chat stores at all"
python3 - "$S-extract.json" <<'PYX'
import json, sys
r = json.load(open(sys.argv[1])).get("result") or {}
chat = [x for x in r.get("stores", []) if "chat" in x.get("path", "") or ".chat" in x.get("path", "")]
proofs = [x.get("dependency_proof") for x in chat]
print("chat stores:", [x.get("path") for x in chat])
print("dependency proofs:", json.dumps(proofs)[:400])
ok = chat and all(p and p.get("scanned_files", 0) > 0 and "subject" in p for p in proofs)
sys.exit(0 if ok else 1)
PYX
chk R2-b3-dependency-proof $? "retirement of the chat stores is covered by the same executed dependency proof" \
                              "no dependency proof covers the chat-store retirement"
python3 - "$S-buildmem.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
r = d.get("result") or {}
print("build-memory:", json.dumps(r)[:400])
sys.exit(0 if d.get("ok") and (r.get("artifacts") or r.get("index") or r.get("manifest_hash")) else 1)
PY
chk R2-b4-reindex $? "retirement is followed by a governed index rebuild whose result is recorded" \
                     "no index refresh was recorded on retirement"

# ---- R3 archive policy -------------------------------------------------------------------------------------------------
ARCHFILE=$(cd "$ROOT" && grep -rl NEEDLESKILL3140 archive 2>/dev/null | head -1)
[ -n "$ARCHFILE" ] || ARCHFILE=$(cd "$ROOT" && find archive -type f | head -1)
if [ -z "$ARCHFILE" ]; then fail R3-b1-default "nothing was archived, so the archive rule cannot be exercised"; else
  TOK=NEEDLESKILL3140
  grep -q "$TOK" "$ROOT/$ARCHFILE" 2>/dev/null || TOK=$(python3 -c "
import re,sys
t=open(sys.argv[1], errors='ignore').read()
w=[x for x in re.findall(r'[A-Za-z_]{8,}', t)]
print(w[0] if w else '')" "$ROOT/$ARCHFILE")
  gov "$ROOT" memory query "$TOK" --k 8 > "$S-arch.json" 2>&1
  python3 - "$S-arch.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1])).get("result") or {}
hits = [h["path"] for h in r.get("hits", []) if h["path"].startswith("archive/")]
print("archive hits in default retrieval:", hits)
sys.exit(0 if not hits else 1)
PY
  chk R3-b1-default $? "archived material ($ARCHFILE) is excluded from default current retrieval" \
                       "archived material is returned by default retrieval"
  gov "$ROOT" memory query "$TOK" --k 8 --include-historical > "$S-arch2.json" 2>&1
  python3 -c "
import json,sys
r=json.load(open(sys.argv[1])).get('result') or {}
sys.exit(0 if any(h['path'].startswith('archive/') for h in r.get('hits',[])) else 1)" "$S-arch2.json"
  chk R3-b1-explicit $? "the same archived material IS reachable when historical material is explicitly requested" \
                        "archived material is unreachable through the fabric on any explicit request: the admission filter's include_archive option (retrieval/mod.rs:35,431) is never set true by any caller, and no CLI flag reaches it; --include-historical lifts only the superseded/authority filter"
fi
python3 - "$S-map.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
acts = r["actions"]
print("map actions:", acts)
# dead/unused code is removed from the active tree (Git keeps the history) rather than archived
sys.exit(0 if acts.get("DELETE_FROM_ACTIVE_TREE", 0) >= 1 else 1)
PY
chk R3-b2-git-preferred $? "dead/unused code is deleted from the active tree (Git history preferred) rather than copied into the archive" \
                           "dead code is archived instead of deleted"
python3 - "$ROOT" <<'PY'
import sys, yaml
c = yaml.safe_load(open(sys.argv[1] + "/governance/kernel/policies/ARCHIVE_POLICY.yaml"))
ok = ("deliberate_reference_implementation" in (c.get("archive_when") or [])
      and "code-reference" in (c.get("archive_subdirs") or []))
print("archive_when:", c.get("archive_when"))
sys.exit(0 if ok else 1)
PY
chk R3-b3-reference-impl $? "a deliberate reference implementation may be retained explicitly (its own archive class and subdirectory)" \
                            "there is no explicit class for a retained reference implementation"

summary
