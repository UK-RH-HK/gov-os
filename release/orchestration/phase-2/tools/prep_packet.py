#!/usr/bin/env python3
"""Prepare a worker packet: compile its governed bootstrap and fold in any prior partial work.

    prep_packet.py --key P2-AR-0060-wsF [--model deepseek-v4-pro] [--budget 220000] [--note "..."]

Reads `packets/specs/registry.json` for the bounded bootstrap subset that applies to the task
(contract line ranges, decisions, skills, repository conventions, required checks), compiles the
model-neutral bootstrap with `worker_bootstrap.py`, appends a "prior partial work" section when the
worktree already carries edits from an earlier attempt, and writes the packet the adapter runs.

Non-product orchestration tooling. One canon: the bootstrap text comes from the authoritative records,
never from a model-specific restatement.
"""
import argparse, json, os, subprocess

TOOLS = os.path.dirname(os.path.abspath(__file__))
PHASE = os.path.dirname(TOOLS)
ROOT = os.path.abspath(os.path.join(PHASE, "..", "..", ".."))
PK = os.path.join(PHASE, "packets")
SPECS = os.path.join(PK, "specs")
REGISTRY = os.path.join(SPECS, "registry.json")
SCRATCH = os.environ.get("P2_SCRATCH", "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/"
                                       "1b6c780e-2b37-439f-a969-a8d96b7ad35e/scratchpad")


def task_text(key):
    """The task half of the packet brief: everything before a previously appended bootstrap/protocol tail."""
    b = json.load(open(os.path.join(PK, f"{key}.json")))["brief"]
    for sep in ("\n\n---\n\n# Common protocol", "\n## Prior partial work"):
        b = b.split(sep)[0]
    return b if not b.startswith("# Worker bootstrap") else json.load(open(os.path.join(SPECS, f"{key}.spec.json")))["task"]["contract"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True)
    ap.add_argument("--model")
    ap.add_argument("--budget", type=int)
    ap.add_argument("--note", help="orchestrator note prepended to the task contract (e.g. a routing decision)")
    a = ap.parse_args()

    reg = json.load(open(REGISTRY))
    if a.key not in reg:
        raise SystemExit(f"{a.key} is not in {REGISTRY}")
    s = reg[a.key]
    pkt = json.load(open(os.path.join(PK, f"{a.key}.json")))
    contract = task_text(a.key)
    if a.note:
        contract = f"**Orchestrator note.** {a.note}\n\n" + contract

    spec = {"role": s.get("role", "capability-repair worker (Phase-2 repair iteration 2)"),
            "authority_level": s.get("authority_level", "L2 (implementation)"),
            "contract_lines": s.get("contract_lines", []), "decisions": s.get("decisions", []),
            "skills": s.get("skills", []), "conventions": s.get("conventions", []),
            "task": {"title": pkt["title"], "contract": contract,
                     "owned_paths": pkt["allow_write"], "required_checks": s["checks"]}}
    sp = os.path.join(SPECS, f"{a.key}.spec.json")
    json.dump(spec, open(sp, "w"), indent=1)

    out = os.path.join(SCRATCH, f"{a.key}.brief.md")
    r = subprocess.run(["python3", os.path.join(TOOLS, "worker_bootstrap.py"), "--spec", sp, "--out", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("bootstrap compile failed: " + r.stderr.strip()[-400:])
    brief = open(out).read()

    wt = pkt["worktree"]
    stat = subprocess.run(["git", "-C", wt, "diff", "--stat"], capture_output=True, text=True).stdout.strip()
    untracked = subprocess.run(["git", "-C", wt, "ls-files", "--others", "--exclude-standard"],
                               capture_output=True, text=True).stdout.strip()
    cp = pkt.get("checkpoint_path")
    cp_abs = os.path.join(ROOT, cp) if cp and not os.path.isabs(cp) else cp
    if stat or untracked:
        brief += ("\n\n## Prior partial work already in your worktree\n\n"
                  "An earlier attempt on this task changed these files. Read the current content before deciding "
                  "anything: keep what is right, correct what is not, and continue. Do not start over.\n\n"
                  + (f"```\n{stat}\n```\n" if stat else "")
                  + (f"\nUntracked files it created:\n```\n{untracked}\n```\n" if untracked else ""))
        if cp_abs and os.path.isfile(cp_abs):
            brief += ("\nIts last checkpoint:\n```json\n" + open(cp_abs).read().strip() + "\n```\n"
                      "Verify the worktree matches it, then continue from `next_action`.\n")

    pkt["brief"] = brief
    pkt["bootstrap_spec"] = os.path.relpath(sp, ROOT)
    pkt["scratch_dir"] = os.path.join(SCRATCH, "r2")
    pkt["checkpoint_path"] = cp or os.path.join("release/orchestration/phase-2/telemetry/checkpoints", f"{a.key}.checkpoint.json")
    if a.model:
        pkt["model"] = a.model
    if a.budget:
        pkt["context_budget_tokens"] = a.budget
    if a.note:
        pkt["routing_note"] = a.note
    json.dump(pkt, open(os.path.join(PK, f"{a.key}.json"), "w"), indent=1)
    print(f"{a.key}: model={pkt['model']} budget={pkt['context_budget_tokens']} "
          f"bootstrap={len(brief)//4} tokens prior_work={'yes' if (stat or untracked) else 'no'}")


if __name__ == "__main__":
    main()
