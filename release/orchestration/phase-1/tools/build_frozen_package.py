#!/usr/bin/env python3
"""Build the frozen Root-of-Trust evidence package and final checkpoint (OWNER-DIRECTIVE-0003).

Non-product orchestration tooling. Reads only committed repository records; writes:
  release/orchestration/phase-1/CHECKPOINTS/CP-FINAL-ROT-LOOP-FROZEN.yaml
  release/orchestration/phase-1/ROT-1-FROZEN-EVIDENCE-PACKAGE.md

Usage: build_frozen_package.py <repo_root> <manual_fields.json>
manual_fields.json supplies facts that are not machine-readable in reports:
  {"ot_status": {"OT-1": "...", "OT-2": "..."}, "synthesis_summary": "...",
   "blocking_classes": [{"id": "...", "finding": "...", "remainder_of": "...", "fix": "...", "route": "..."}]}
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml

FROZEN = "PHASE_1_ROOT_OF_TRUST_LOOP_FROZEN_PENDING_META_ARCHITECTURE_REVIEW"
SEV_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]


def git(root, *args):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True)
    return r.stdout.strip()


def load(path):
    with open(path) as fh:
        return yaml.safe_load(fh)


def report_on_branch_or_head(root, rel):
    p = root / rel
    if not p.exists():
        raise SystemExit(f"missing committed report: {rel}")
    return load(p)


def findings_by_severity(report):
    out = {s: [] for s in SEV_ORDER}
    for f in report.get("findings") or []:
        sev = str(f.get("severity", "INFO")).upper()
        out.setdefault(sev, []).append({"id": f.get("id"), "title": f.get("title"), "path": f.get("path")})
    return {k: v for k, v in out.items() if v}


def main():
    root = Path(sys.argv[1]).resolve()
    manual = json.loads(Path(sys.argv[2]).read_text())
    phase = root / "release/orchestration/phase-1"
    state = load(phase / "ORCHESTRATOR_STATE.yaml")
    arch = state["architecture"]
    revisions = []
    for rev in arch["revisions"]:
        entry = {"revision": rev["revision"], "architecture_commit": rev.get("commit"), "verdict": rev.get("verdict", rev.get("status")),
                 "review_commit": rev.get("review_commit"), "review_path": rev.get("review_path"),
                 "orchestrated_by_phase_1": rev.get("orchestrated_by_phase_1", True)}
        if rev.get("review_path"):
            rp = rev["review_path"].rstrip("/")
            locs = [f"{rp}/{n}" for n in ("00-REVIEW-REPORT.md", "10-BLOCKING-FINDINGS.md", "11-CORRECTION-DELTA.md",
                                          "11-IMPLEMENTATION-CONDITIONS.md") if (root / rp / n).exists()]
            locs += [f"{rp}/{d}/" for d in ("B-trust-security", "C-compat-transaction", "D-synthesis") if (root / rp / d).is_dir()]
            entry["review_report_locations"] = locs or [rp + "/"]
        for k in ("review_panel", "synthesis_run", "specialist_runs", "author_run", "blocking_classes", "kind"):
            if k in rev:
                entry[k] = rev[k]
        revisions.append(entry)

    r7 = next(r for r in arch["revisions"] if r["revision"] == 7)
    if r7.get("status") not in ("REJECTED", "ACCEPTED"):
        raise SystemExit(f"revision 7 not concluded in state (status={r7.get('status')})")
    runs = {rid: report_on_branch_or_head(root, f"release/orchestration/phase-1/AGENT_RUNS/{rid}.report.yaml")
            for rid in ("AR-0019", "AR-0020", "AR-0021", "AR-0022")}
    run_records = {rid: load(phase / f"AGENT_RUNS/{rid}.run.yaml") for rid in runs}

    def role_block(rid, evidence_dir):
        rep, rr = runs[rid], run_records[rid]
        oc = rr.get("outcome") or {}
        return {"run_id": rid, "role": rep.get("role"), "verdict": rep.get("verdict"),
                "work_commit": oc.get("work_commit") or rep.get("output", {}).get("commit"),
                "report_commit": oc.get("report_commit"), "integration_merge_commit": oc.get("integration_merge_commit"),
                "report_path": f"release/orchestration/phase-1/AGENT_RUNS/{rid}.report.yaml",
                "evidence_path": evidence_dir, "findings": findings_by_severity(rep)}

    rv = "release/root-of-trust/4.1.6-review-r7"
    d0008 = load(root / "spec/decisions/D-0008.yaml")
    d0007 = load(root / "spec/decisions/D-0007.yaml")
    d0007_unchanged = subprocess.run(["git", "-C", str(root), "diff", "--quiet", "e5a6b8aa39d2a36311489418506d911df2587722", "HEAD", "--",
                                      "spec/decisions/D-0007.yaml"]).returncode == 0
    odr1 = load(phase / "GATES/OWNER-DESIGN-REQUIREMENTS-0001.yaml")
    odr2 = load(phase / "GATES/OWNER-DESIGN-REQUIREMENTS-0002.yaml")
    gates = load(phase / "GATES/GATE-REGISTER.yaml")["gates"]
    synth = role_block("AR-0022", f"{rv}/D-synthesis/")
    unresolved = synth["findings"] if r7["status"] == "REJECTED" else {"carried": synth["findings"]}

    cp = {
        "schema": "governance-os.phase-1.checkpoint", "schema_version": 1,
        "checkpoint": "CP-FINAL-ROT-LOOP-FROZEN",
        "trigger": "OWNER-DIRECTIVE-0003: Root-of-Trust revision loop frozen after the revision-7 verdict",
        "generated_by": "release/orchestration/phase-1/tools/build_frozen_package.py",
        "repository": {
            "branch": git(root, "rev-parse", "--abbrev-ref", "HEAD"),
            "head_before_final_commit": git(root, "rev-parse", "HEAD"),
            "head_note": "the final checkpoint commit is the child of head_before_final_commit; see PHASE_1_LEDGER.md L-final",
            "working_tree_status_before_final_commit": git(root, "status", "--porcelain").splitlines(),
            "main_branch_modified_by_phase_1": False,
        },
        "revision_7": {
            "architecture_commit": r7.get("commit"),
            "architect": role_block("AR-0019", "release/root-of-trust/4.1.6/evidence/r7/"),
            "reviewer_b": role_block("AR-0020", f"{rv}/B-trust-security/"),
            "reviewer_c": role_block("AR-0021", f"{rv}/C-compat-transaction/"),
            "synthesis": {**synth, "review_commit": r7.get("review_commit"),
                          "consolidated_files": [f"{rv}/{n}" for n in ("00-REVIEW-REPORT.md", "10-BLOCKING-FINDINGS.md",
                                                                        "11-CORRECTION-DELTA.md", "11-IMPLEMENTATION-CONDITIONS.md")
                                                 if (root / rv / n).exists()]},
            "final_verdict": r7.get("verdict"),
            "blocking_classes": manual.get("blocking_classes", []),
            "synthesis_summary": manual.get("synthesis_summary"),
            "routing": "NOT ROUTED — loop frozen by OWNER-DIRECTIVE-0003",
        },
        "unresolved_findings_revision_7": unresolved,
        "ot_status": manual["ot_status"],
        "owner_requirements": {
            "OWNER-DESIGN-REQUIREMENTS-0001": {"record": "release/orchestration/phase-1/GATES/OWNER-DESIGN-REQUIREMENTS-0001.md",
                                               "direction": odr1["d0008_direction"], "OP-1..OP-16": odr1["owner_options"],
                                               "first_contact_composer_signer": odr1["first_contact_composer_signer"],
                                               "environment_manifest": odr1["environment_manifest"],
                                               "initial_certified_profile": odr1["initial_certified_profile"]},
            "OWNER-DESIGN-REQUIREMENTS-0002": {"record": "release/orchestration/phase-1/GATES/OWNER-DESIGN-REQUIREMENTS-0002.md",
                                               "OT-1": odr2["OT-1"], "OT-2": odr2["OT-2"]},
            "OWNER-DIRECTIVE-0003": {"record": "release/orchestration/phase-1/GATES/OWNER-DIRECTIVE-0003-FREEZE-ROT-LOOP.md"},
        },
        "decisions": {
            "D-0008": {k: d0008.get(k) for k in ("status", "proposal_state", "approval_state", "review_state", "in_effect",
                                                  "human_approved", "revision")},
            "D-0008_chosen_option_present": "chosen_option" in d0008,
            "D-0007": {"status": d0007.get("status"), "unchanged_since_phase_1_start": d0007_unchanged,
                       "superseded": False},
        },
        "root_of_trust_revisions_1_to_7": revisions,
        "escalation_counters": {k: arch.get(k) for k in ("orchestrated_rejections", "orchestrated_rejection_streak",
                                                         "persistent_remainder_streak")},
        "gates": [{"id": g["id"], "status": g["status"]} for g in gates],
        "orchestration_state": {"state_path": "release/orchestration/phase-1/ORCHESTRATOR_STATE.yaml",
                                "ledger_path": "release/orchestration/phase-1/PHASE_1_LEDGER.md",
                                "lifecycle_state": FROZEN, "loop_status": "FROZEN", "running_work": []},
        "not_done_by_directive": ["no revision 8", "no further architecture author", "findings not routed",
                                  "no implementation", "no key ceremony", "no Capability Contract stages", "no Prompt 2",
                                  "no D-0008 activation", "no new owner options"],
        "next_deterministic_action": FROZEN,
    }
    (phase / "CHECKPOINTS/CP-FINAL-ROT-LOOP-FROZEN.yaml").write_text(
        yaml.safe_dump(cp, sort_keys=False, allow_unicode=True, width=120))

    lines = ["# RoT-1 frozen evidence package (Phase 1, after Revision 7)", "",
             f"Next action: `{FROZEN}`", "",
             "Generated from committed records by `release/orchestration/phase-1/tools/build_frozen_package.py`. The machine-readable "
             "checkpoint is `CHECKPOINTS/CP-FINAL-ROT-LOOP-FROZEN.yaml`. Where this page and a source record differ, the source record "
             "governs.", "",
             "## Revision verdicts", "", "| Rev | Architecture commit | Verdict | Review commit | Review reports |", "|---|---|---|---|---|"]
    for r in revisions:
        locs = "<br>".join(f"`{x}`" for x in r.get("review_report_locations", [])) or "—"
        lines.append(f"| {r['revision']} | `{r['architecture_commit']}` | {r['verdict']} | `{r.get('review_commit')}` | {locs} |")
    r7b = cp["revision_7"]
    lines += ["", "## Revision 7 evidence", "", "| Role | Run | Verdict | Work commit | Report commit | Evidence |", "|---|---|---|---|---|---|"]
    for key in ("architect", "reviewer_b", "reviewer_c", "synthesis"):
        b = r7b[key]
        lines.append(f"| {key} | {b['run_id']} | {b['verdict']} | `{b['work_commit']}` | `{b['report_commit']}` | `{b['evidence_path']}` |")
    lines += ["", f"**Final Revision-7 verdict:** `{r7b['final_verdict']}` (routing: {r7b['routing']})", ""]
    if r7b.get("synthesis_summary"):
        lines += [r7b["synthesis_summary"], ""]
    lines += ["## Revision-7 consolidated findings (synthesis)", ""]
    for sev in SEV_ORDER:
        for f in r7b["synthesis"]["findings"].get(sev, []):
            lines.append(f"- **{sev} {f['id']}:** {f['title']}")
    if r7b["blocking_classes"]:
        lines += ["", "| Blocking class | Finding | Remainder of | Fix kind | Route |", "|---|---|---|---|---|"]
        for c in r7b["blocking_classes"]:
            lines.append(f"| {c['id']} | {c['finding']} | {c['remainder_of']} | {c['fix']} | {c['route']} |")
    lines += ["", "## Panel findings (before adjudication)", ""]
    for key in ("reviewer_b", "reviewer_c"):
        for sev in SEV_ORDER:
            for f in r7b[key]["findings"].get(sev, []):
                lines.append(f"- {key} **{sev} {f['id']}:** {f['title']}")
    lines += ["", "## OT-1 and OT-2", ""] + [f"- **{k}:** {v}" for k, v in cp["ot_status"].items()]
    dd = cp["decisions"]
    lines += ["", "## Decisions", "",
              f"- **D-0008:** status `{dd['D-0008']['status']}`, proposal_state `{dd['D-0008']['proposal_state']}`, "
              f"human_approved `{dd['D-0008']['human_approved']}`, in_effect `{dd['D-0008']['in_effect']}`, revision "
              f"{dd['D-0008']['revision']}, chosen_option present `{dd['D-0008_chosen_option_present']}`.",
              f"- **D-0007:** status `{dd['D-0007']['status']}`, unchanged since Phase 1 start `{dd['D-0007']['unchanged_since_phase_1_start']}`, not superseded.",
              "", "## Owner requirements OP-1…OP-16 (OWNER-DESIGN-REQUIREMENTS-0001; verbatim record governs)", ""]
    for op, v in odr1["owner_options"].items():
        sel = v.get("selection") or ", ".join(f"{k}={v[k]}" for k in list(v)[:3])
        lines.append(f"- **{op}:** {sel}")
    lines += ["", "## Repository", "",
              f"- Branch `{cp['repository']['branch']}`, HEAD before final commit `{cp['repository']['head_before_final_commit']}`.",
              f"- Working tree before final commit: {len(cp['repository']['working_tree_status_before_final_commit'])} entries (the package files themselves).",
              "", "## Not done, by owner directive", ""] + [f"- {x}" for x in cp["not_done_by_directive"]]
    (phase / "ROT-1-FROZEN-EVIDENCE-PACKAGE.md").write_text("\n".join(lines) + "\n")
    print("written CP-FINAL-ROT-LOOP-FROZEN.yaml and ROT-1-FROZEN-EVIDENCE-PACKAGE.md")


if __name__ == "__main__":
    main()
