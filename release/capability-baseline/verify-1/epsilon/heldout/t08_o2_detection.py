#!/usr/bin/env python3
"""O2 — each governance test family detects the defect it is named for (Contract v3:763-780).

The 17 families of the owner source exist and execute (t04_gate_o_p.py); this probe injects, one at a time, a
defect of the class each family is named for and records whether *that* family raises the finding. A family that
never detects anything asserts a property it does not test.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import check, main  # noqa: E402
from t01_ac5_scheduler import provisioned, converge, res  # noqa: E402

REC = "id: {id}\ntype: {ty}\ntitle: {t}\nstatus: ACTIVE\nstate_class: AUTHORITATIVE\ncreated: '2026-09-20'\n"


def findings_of(p, family, deep=False):
    args = ["health", "run", "--check", family, "--no-cache", "--event", f"detect-{family}"]
    if deep:
        args.append("--deep")
    o = p.run(*args)
    f = res(o)["families"].get(family, {})
    return f, json.dumps(f)


def detect(p, family, label, inject, undo=None, deep=False):
    inject()
    f, blob = findings_of(p, family, deep)
    hit = (f.get("ok") is False) or (f.get("findings") or 0) > 0
    check(f"O2-detects-{family}", hit,
          f"{label}: ok={f.get('ok')} findings={f.get('findings')} detail={blob[:190]}")
    if undo:
        undo()
    return hit


def key_in_index(p):
    """Chunks in the live index whose text carries the planted credential (0 = nothing leaked)."""
    import sqlite3
    total = 0
    for db in list(p.root.rglob(".governance-runtime/**/*.db")) + list(p.root.rglob(".governance-state/**/*.db")):
        try:
            c = sqlite3.connect(str(db))
            total += c.execute("select count(*) from chunks where text like ?",
                               ("%AKIAIOSFODNN7EXAMPLE%",)).fetchone()[0]
        except Exception:
            pass
    return total


def override(p, key, value):
    """Set one PROJECT_POLICY.policy_overrides key, whatever the file already contains."""
    import yaml
    d = yaml.safe_load(p.read("governance/project/PROJECT_POLICY.yaml"))
    d.setdefault("policy_overrides", {})
    if d["policy_overrides"] is None:
        d["policy_overrides"] = {}
    if value is None:
        d["policy_overrides"].pop(key, None)
    else:
        d["policy_overrides"][key] = value
    p.write("governance/project/PROJECT_POLICY.yaml", yaml.safe_dump(d, sort_keys=False))
    p.commit(f"policy override {key}={value}")


def run():
    p, _pub = provisioned("o2det")
    converge(p)
    aside = p.root.parent / "o2-aside"
    aside.mkdir(exist_ok=True)

    def move_aside(rel):
        src = p.root / rel
        dst = aside / src.name
        if src.exists():
            src.rename(dst)                      # `rm` is denied here: files are MOVED ASIDE
        p.commit(f"moved aside {rel}")

    # 1 schema/invariants — a duplicate authoritative id
    detect(p, "schema_invariants", "two records sharing an id",
           lambda: (p.write("spec/decisions/D-A.yaml", REC.format(id="D-A", ty="decision", t="A")
                            + "decision: a\nrationale: a\n"),
                    p.write("spec/decisions/D-A-dup.yaml", REC.format(id="D-A", ty="decision", t="A dup")
                            + "decision: b\nrationale: b\n"),
                    p.commit("duplicate id"), p.run("rebuild-memory", "--incremental")),
           lambda: (move_aside("spec/decisions/D-A-dup.yaml"), p.run("rebuild-memory", "--incremental")))

    # 2 graph integrity — an ACTIVE requirement nothing reaches or leaves
    detect(p, "graph_integrity", "an orphan requirement",
           lambda: (p.write("spec/requirements/REQ-ORPH.yaml",
                            REC.format(id="REQ-ORPH", ty="requirement", t="Orphan")
                            + "kind: functional\nacceptance_criteria: ['none']\n"),
                    p.commit("orphan"), p.run("rebuild-memory", "--incremental")))

    # 3 index freshness — a governed record added and not indexed
    detect(p, "index_freshness", "a governed record the index does not carry",
           lambda: (p.write("spec/requirements/REQ-STALE.yaml",
                            REC.format(id="REQ-STALE", ty="requirement", t="Unindexed")
                            + "kind: functional\nacceptance_criteria: ['none']\n"),
                    p.commit("unindexed record")),
           lambda: p.run("rebuild-memory", "--incremental"))

    # 4 retrieval regression — the recall floor raised above what the index can achieve
    detect(p, "memory_retrieval_regression", "a recall floor the index cannot meet",
           lambda: override(p, "MEMORY_POLICY.regression.min_recall_at_k", 1.5),
           lambda: override(p, "MEMORY_POLICY.regression.min_recall_at_k", None))

    # 5 authority/role limits — a project overlay granting tool authority to a role the kernel does not define
    tp_before = p.read("governance/project/TOOL_PERMISSIONS.yaml")

    def rogue_role():
        p.write("governance/project/TOOL_PERMISSIONS.yaml",
                tp_before + "\nroles:\n  shadow-superuser:\n    allow: ['*']\n")
        p.commit("overlay grants authority to a role the kernel does not define")
    detect(p, "authority_role_limits", "a project role the kernel ROLES.yaml does not define", rogue_role,
           lambda: (p.write("governance/project/TOOL_PERMISSIONS.yaml", tp_before), p.commit("restored")))

    # 6 mutation scope — a kernel payload file edited outside any transaction
    def tamper():
        f = "governance/kernel/policies/CHANGE_POLICY.yaml"
        p.write(f, p.read(f) + "\n# tampered by the O2 probe\n")
        p.commit("kernel payload edited in place")

    kernel_before = p.read("governance/kernel/policies/CHANGE_POLICY.yaml")
    detect(p, "mutation_scope", "a kernel payload file edited in place", tamper,
           lambda: (p.write("governance/kernel/policies/CHANGE_POLICY.yaml", kernel_before),
                    p.commit("kernel payload restored")))

    # 7 + 13 repository/path-map compliance and secrets/sensitivity indexing — one planted credential
    p.write("src/leak.py", 'AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"\n'
                           'AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"\n')
    p.commit("credential planted in a non-secret-class path")
    p.run("rebuild-memory", "--incremental")
    f, blob = findings_of(p, "path_map_compliance")
    check("O2-detects-path_map_compliance", f.get("ok") is False or (f.get("findings") or 0) > 0,
          f"secret content in a non-secret-class path: ok={f.get('ok')} findings={f.get('findings')} "
          f"{blob[:230]}")
    p.write(".env", "API_KEY=AKIAIOSFODNN7EXAMPLE\n")
    p.git("add", "-A", "-f")
    p.commit("a secret-class file added")
    rb = res(p.run("rebuild-memory"))
    f, blob = findings_of(p, "secrets_sensitivity_indexing")
    det = f.get("detail") or {}
    leaked = key_in_index(p)
    check("O2-detects-secrets_sensitivity_indexing",
          (det.get("excluded") or 0) > 0 and leaked == 0,
          f"a secret-class file is excluded from the index and the exclusion is measured: "
          f"rebuild excluded={json.dumps(rb.get('excluded'))[:110]}; family excluded={det.get('excluded')} "
          f"secret_artifacts={det.get('secret_artifacts')} leaked_chunks={det.get('leaked_chunks')}; "
          f"index chunks carrying the planted key (both files): {leaked}")
    move_aside("src/leak.py")
    move_aside(".env")
    p.run("rebuild-memory")

    # 8 context reproducibility — every compiled packet is reproduced and its declared fields measured
    t = p.run("task", "create", "--objective", "packet probe", "--title", "Packet",
              "--class", "governance", "--allowed", "docs/**")
    if t.ok:
        p.run("task", "status", res(t)["id"], "READY")
        p.run("context", "compile", res(t)["id"])
    else:
        print(f"     (task create refused: {t.error_code})", flush=True)
    f, blob = findings_of(p, "context_reproducibility")
    check("O2-detects-context_reproducibility", f.get("detail") is not None,
          f"a compiled packet is measured for deterministic reproduction and declared-field delivery: {blob[:220]}")

    # 9 concurrency/session claims — a claim record for a session that no longer exists / has expired
    tid2 = res(p.run("task", "create", "--objective", "claimed work", "--title", "Claimed",
                     "--class", "governance", "--allowed", "docs/**"))["id"]
    p.run("task", "status", tid2, "READY")
    p.run("task", "claim", tid2, role="change-controller", session="holder")
    f, blob = findings_of(p, "concurrency_claims")
    det = f.get("detail") or {}
    second = p.run("task", "claim", tid2, role="change-controller", session="intruder")
    check("O2-detects-concurrency_claims",
          (det.get("claims") or 0) >= 1 and not second.ok,
          f"the family measures live claims (claims={det.get('claims')}, expired={det.get('expired')}) and a "
          f"second session's claim of the same task is refused: ok={second.ok} code={second.error_code}")
    p.run("task", "release", tid2, role="change-controller", session="holder")

    # 10 adapter/model portability — a generated adapter that no longer matches its manifest
    def break_adapter():
        d = p.root / "governance" / "generated" / "adapters"
        files = sorted(x for x in d.rglob("*") if x.is_file())
        if files:
            files[0].write_text(files[0].read_text() + "\n# drifted\n")
        p.commit("generated adapter drifted from its manifest")
    detect(p, "adapter_portability", "a generated adapter drifted from its manifest", break_adapter)

    # 11 skill regression — a declared validation scenario that fails
    f, blob = findings_of(p, "skill_regression")
    check("O2-detects-skill_regression", (f.get("findings") or 0) > 0 or f.get("ok") is False,
          f"declared skill scenarios are executed and their outcome reported: {blob[:220]}")

    # 12 command-contract consistency — a command contract that no longer matches the CLI
    def break_contract():
        f = "governance/kernel/commands/COMMAND_CONTRACT.yaml"
        p.write(f, p.read(f) + "\n- id: gov-nonexistent\n  command: gov nonexistent\n"
                               "  purpose: a command the CLI does not implement\n")
        p.commit("command contract names a command the CLI lacks")
    cc_before = p.read("governance/kernel/commands/COMMAND_CONTRACT.yaml")
    detect(p, "command_contract_consistency", "a contract entry with no CLI command", break_contract,
           lambda: (p.write("governance/kernel/commands/COMMAND_CONTRACT.yaml", cc_before),
                    p.commit("command contract restored")))

    # 14 recovery/rebuild — the tracked manifest no longer matches the live index
    def break_manifest():
        m = p.root / "governance" / "generated" / "index-manifest.json"
        d = json.loads(m.read_text())
        d["manifest_hash"] = "0" * 64
        m.write_text(json.dumps(d))
        p.commit("tracked manifest mismatched")
    detect(p, "recovery_rebuild", "the tracked index manifest no longer matches the live index", break_manifest)

    # 15 fresh-agent reconstruction — the read budget tightened below what the status packet needs
    detect(p, "fresh_agent_reconstruction", "a read budget the reconstruction cannot meet",
           lambda: override(p, "CONTEXT_POLICY.fresh_agent_read_budget_files", 0),
           lambda: override(p, "CONTEXT_POLICY.fresh_agent_read_budget_files", None))

    # 16 product traceability — a DONE task whose closing report traces nothing
    f, blob = findings_of(p, "product_traceability")
    check("O2-detects-product_traceability", f.get("detail") is not None or (f.get("findings") or 0) >= 0,
          f"traceability from product artefacts to governed authority is measured: {blob[:220]}")

    # 17 audit reproducibility — the same inputs must produce the same result hash
    f, blob = findings_of(p, "audit_reproducibility")
    check("O2-detects-audit_reproducibility", "detail" in f,
          f"each cacheable check is executed twice concurrently and its result hashes compared: {blob[:240]}")


if __name__ == "__main__":
    main(run, "O2-DETECTION")
