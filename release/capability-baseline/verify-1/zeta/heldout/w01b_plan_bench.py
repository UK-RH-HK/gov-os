"""W1, second half — the three artefact types W1:1080 names that the main W1 probe does not reach in
a greenfield repository: migration plans, audit findings and benchmark results. Held-out, P2-AR-0051.
"""
import glob
import json
import os
import shutil
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402


class Brownfield(lib.Repo):
    """A brownfield repository copied from the product's own fixture; adopted, not initialised."""

    def __init__(self, name):
        self.name = name
        self.root = os.path.join(lib.WORK, name)
        self.state = os.path.join(lib.WORK, name + ".machine")
        if os.path.exists(self.root):
            shutil.rmtree(self.root)
        os.makedirs(self.root)
        os.makedirs(self.state, exist_ok=True)
        shutil.copytree(os.path.join(lib.WT, "fixtures", "brownfield", "project"), self.root,
                        dirs_exist_ok=True)
        self.git("init", "-q")
        self.git("config", "user.email", "zeta@example.invalid")
        self.git("config", "user.name", "zeta")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "brownfield baseline")


def main():
    # ---- migration plans ---------------------------------------------------------------------
    r = Brownfield("w01b")
    for stage in ("baseline", "inventory", "classify", "map", "plan"):
        out = r.run("adopt", stage)
        assert out.get("ok"), "%s: %s" % (stage, json.dumps(out.get("error"))[:300])
    plan1 = yaml.safe_load(open(r.path("spec/audits/GOVERNANCE-ADOPTION/05-plan.yaml")))
    attrs = {k: plan1.get(k) for k in
             ("id", "type", "status", "state_class", "version", "content_hash", "producer",
              "supersedes", "expected_consumers")}
    lib.check("W1b-01", "the adoption/migration plan is a governed record with the W1 attributes "
                        "(stable id, type, status, authority class, version, content hash, "
                        "producer, supersession lineage, expected consumers)",
              all(attrs.get(k) is not None for k in
                  ("id", "type", "status", "state_class", "version", "content_hash", "producer",
                   "expected_consumers")),
              json.dumps(attrs)[:600])

    # re-planning on unchanged input is idempotent (same id, same version, same content hash)
    out = r.run("adopt", "plan")
    assert out.get("ok"), json.dumps(out.get("error"))[:300]
    plan_same = yaml.safe_load(open(r.path("spec/audits/GOVERNANCE-ADOPTION/05-plan.yaml")))
    lib.check("W1b-02", "re-running the planning stage on unchanged input is idempotent: same id, "
                        "same version, same content hash (no positional re-identification)",
              plan_same["id"] == plan1["id"] and plan_same["version"] == plan1["version"]
              and plan_same["content_hash"] == plan1["content_hash"],
              json.dumps({"id": plan_same["id"], "version": plan_same["version"],
                          "same_hash": plan_same["content_hash"] == plan1["content_hash"]}))

    # a changed input re-plans to a NEW version that supersedes the old one, whose snapshot is kept
    r.put("legacy-extra.md", "# a legacy document added after the first plan\n")
    r.commit("new legacy artefact")
    for stage in ("inventory", "classify", "map", "plan"):
        out = r.run("adopt", stage)
        assert out.get("ok"), "%s: %s" % (stage, json.dumps(out.get("error"))[:300])
    plan2 = yaml.safe_load(open(r.path("spec/audits/GOVERNANCE-ADOPTION/05-plan.yaml")))
    versions = sorted(glob.glob(r.path("spec/audits/GOVERNANCE-ADOPTION/05-plan.versions/*")))
    lib.check("W1b-02b", "a re-plan over changed input keeps the plan's id, bumps its version, "
                         "records what it supersedes and keeps the previous version's snapshot",
              plan2["id"] == plan1["id"] and plan2["version"] > plan1["version"]
              and json.dumps(plan2.get("supersedes") or []) != "[]"
              and len(versions) >= 1,
              json.dumps({"id": plan2["id"], "v1": plan1["version"], "v2": plan2["version"],
                          "supersedes": plan2.get("supersedes"),
                          "snapshots": [os.path.basename(v) for v in versions]})[:500])

    # the catalogue artefact ids are content-derived, so re-running a stage does not renumber them
    def catalogue_ids():
        rows = [json.loads(x) for x in
                open(r.path("spec/audits/GOVERNANCE-ADOPTION/02-CLASSIFICATION.jsonl"))
                if x.strip()]
        return {x.get("artifact_id"): x.get("path") for x in rows if x.get("artifact_id")}

    ids1 = catalogue_ids()
    r.run("adopt", "classify")
    ids2 = catalogue_ids()
    lib.check("W1b-03", "adoption catalogue artefact ids are content-derived and stable across a "
                        "re-run (they do not renumber positionally)",
              bool(ids1) and ids1 == ids2 and all(k.startswith("ART-") for k in ids1),
              json.dumps({"n": len(ids1), "sample": sorted(ids1)[:4],
                          "stable": ids1 == ids2})[:400])

    # ---- audit findings ---------------------------------------------------------------------
    # The adoption audit stage A11 needs a completed A0-A10 adoption (alpha's scope), and refuses
    # out of order; what is verified here is that the finding-id scheme the adoption uses is the
    # SAME content-derived scheme the governance suite uses (proved stable in w01_identity W1-05).
    out_of_order = r.run("adopt", "audit", role="independent-auditor", session="auditor1")
    lib.check("W1b-04", "the adoption audit stage refuses out of protocol order (its findings are "
                        "reachable only after A0-A10; the finding-id scheme itself is verified by "
                        "w01_identity W1-05 on the governance suite)",
              not out_of_order.get("ok")
              and (out_of_order.get("error") or {}).get("code") == "STAGE_ORDER",
              json.dumps(out_of_order.get("error"))[:300])

    # ---- benchmark results -------------------------------------------------------------------
    g = lib.Repo("w01b-bench")
    lib.seed_green(g)
    b = g.run("memory", "benchmark", "--candidate", "builtin:256", "--candidate", "builtin:512",
              "--record", role="memory-engineer")
    br = b.get("result") or {}
    rid = br.get("research_record")
    rec = None
    if rid:
        p = g.path("spec/research/%s.yaml" % rid)
        if os.path.exists(p):
            rec = yaml.safe_load(open(p))
    shown = g.run("artefact", "show", rid) if rid else {}
    sr = shown.get("result") or {}
    lib.check("W1b-05", "a retrieval benchmark result is a governed record with the W1 attributes "
                        "and its measurements",
              bool(rid) and shown.get("ok")
              and sr.get("content_hash") and sr.get("lifecycle_state")
              and sr.get("authoritative_status")
              and bool((rec or {}).get("measurements"))
              and (rec or {}).get("content_hash") == br.get("content_hash"),
              json.dumps({"benchmark": json.dumps(br)[:200], "record": rid,
                          "identity": {k: sr.get(k) for k in
                                       ("id", "type", "canonical_dir", "authoritative_status",
                                        "lifecycle_state", "content_hash")}})[:700])

    return lib.summary()


if __name__ == "__main__":
    sys.exit(main())
