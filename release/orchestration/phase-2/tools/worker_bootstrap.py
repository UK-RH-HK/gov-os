#!/usr/bin/env python3
"""Governed worker bootstrap compiler (non-product orchestration tooling).

Compiles the model-neutral brief an API worker needs *before* it starts, from the authoritative sources,
so no worker has to infer how this repository and its governance behave by exploring.

    worker_bootstrap.py --spec SPEC.json [--out brief.md]

The spec names, per task, only the bounded subset that applies:

    {"role": "...", "authority_level": "L2",
     "contract_lines": [[134,137],[425,431]],        # verbatim excerpts from the owner source
     "decisions": ["OD-P2-03","OC-P2-04","D-0007"],  # authoritative records, quoted from their own files
     "skills": ["SKL-BACKEND-IMPL","SKL-TEST-DESIGN"],
     "conventions": ["rust","tests","cli","schemas","governed-records"],
     "task": {...}}                                  # the task contract (objective, paths, checks, done)

One canon, one text. Provider-specific prompting stays a thin adapter around this output; nothing here is
restated differently per model, and nothing here invents a requirement — every normative line is quoted
with its source path so a worker (and a later verifier) can check it.
"""
import argparse, json, os, re, sys, textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
CONTRACT = os.path.join(ROOT, "Governance_OS_Capability_Acceptance_Contract_v3.md")
PHASE = os.path.join(ROOT, "release", "orchestration", "phase-2")

# Records a worker may be given, with the part of each that is normative for a worker.
DECISIONS = {
    "D-0007": ("spec/decisions/D-0007.yaml", "trust classes: a lower-trust input may never manufacture a higher-trust fact"),
    "OD-P2-01": ("release/orchestration/phase-2/GATES/OWNER-DECISION-P2-0001-AGENT-ROLE-IDENTITY.md", "agent roles stay adapter-declared"),
    "OD-P2-02": ("release/orchestration/phase-2/GATES/OWNER-DECISION-P2-0002-UNPROVISIONED-MACHINES.md", "refuse external-source kernel ingress until provisioned"),
    "OD-P2-03": ("release/orchestration/phase-2/GATES/OWNER-DECISION-P2-0003-TOOL-INSTALL-GATE.md", "a tool installation gates only when it expands authority"),
    "OC-P2-04": ("release/orchestration/phase-2/GATES/OWNER-CLARIFICATION-P2-0004-TRUSTED-AUTHORITY-STATE.md", "project-editable files may request authority, never manufacture it"),
    "P2-ADJ-0002": ("release/orchestration/phase-2/GATES/P2-ADJ-0002-T2-CROSS-MACHINE-CONTINUITY.md", "T2 facts are portable across the owner's provisioned machines"),
    "P2-ADJ-0003": ("release/orchestration/phase-2/GATES/P2-ADJ-0003-H4-GAPS-AND-GREEN-PRECONDITIONS.md", "H4 gaps degrade suite health and refuse nothing"),
}

# The behaviour a native agent picks up implicitly from the repository. Stated explicitly, with its source.
CONVENTIONS = {
"rust": """**Rust layout.** The product is `runtime/` (library, `gov_runtime`) plus `cli/` (the `gov` binary). Modules are
files or directories under `runtime/src/`; a new module needs its `pub mod` line in the parent `mod.rs` or `lib.rs`.
Unit tests live in a `#[cfg(test)] mod tests` block at the foot of the file they test. Build with
`cargo build --release`; the binary is `target/release/gov`. Keep `cargo fmt` clean on files you touch and leave the
release build at **0 warnings** — a warning is treated as a defect here.""",
"tests": """**Tests.** Certification tests live in `tests/certification/<name>.rs` and must be declared with a `mod <name>;`
line in `tests/certification/main.rs`, or they never run. Test names are load-bearing: the governed evidence map names
**477** tests by exact path, so renaming, removing or `#[ignore]`-ing an existing test breaks `gov contract verify`, the
contract-binding test and `release build`. Add tests; never rename or delete one. A test that merely asserts a struct
field or a constant is not evidence of behaviour — drive the real code path and assert the observable result.""",
"cli": """**Adding or changing a command.** Every subcommand must be classified or G0 refuses it: add the arm in
`cli/src/main.rs`, the `g0_label` mapping, and an entry in `COMMAND_GUARDS` in `runtime/src/orchestration/control.rs`
declaring its authority class and whether it reads or writes. An unclassified command fails closed by design.""",
"schemas": """**Schemas and versions.** Record schemas live in `framework/schemas/*.json`. If you change a schema you must
bump its version and mirror that version in `framework/KERNEL.yaml`'s `schema_versions`, or the release build and the
kernel-consistency tests refuse the tree.""",
"governed-records": """**Governed records and sealing.** Records the OS writes (gates, decisions, CIT state, tasks, the
plugin registry, health results) are sealed T2 state: a record written by hand is `UNSEALED`/`BROKEN` and is never
honoured. Write through the existing governed path rather than writing files directly, and never add a code path that
blesses a hand-written record. Project-editable files under `governance/project/**` are *requests*, not grants.""",
"health": """**Health and the availability rule.** Checks are declared in `runtime/src/scheduler/catalogue.rs` with their
tiers, severities and remedies. A block refuses only what it protects, its listed remedy stays available, no block
refuses its own remedy, and every refusal is typed and names its scope and subjects (Contract v3 L4, O5:807).""",
"policy": """**Policy precedence.** Kernel policy outranks project overlay. A project overlay may narrow what it grants
itself; an attempt to widen must be refused, left without effect and reported through
`policy_precedence::evaluate_overlay` and `gov policy overrides`.""",
"adoption": """**Adoption.** `gov adopt` runs stages A0–A11 in order on an existing repository; each stage is executable
and evidenced, and a stage may not be skipped to make a later one pass. The brownfield fixture under `fixtures/` is the
tree the acceptance evidence uses — do not edit a fixture to make adoption succeed.""",
}

CHECKPOINT_PROTOCOL = """## Context and checkpoint protocol

Your context is a working surface, not a place to accumulate everything you have read.

- **Checkpoint early and often.** Call `checkpoint` after each material step: what the objective is, what you have
  completed, files changed, checks run with outcomes, what you discovered, what is unresolved, decisions and
  assumptions you have made, and the **exact next action**. The adapter also checkpoints automatically before it
  renews your context and before the run ends.
- **A checkpoint is a handover.** Write it so that a different worker could continue from it alone, without replaying
  your exploration. Name files and symbols exactly.
- **Context renewal is normal.** When history becomes mostly exploration noise the adapter rebuilds a fresh bounded
  context from your latest checkpoint. Nothing is lost that you put in the checkpoint; anything you left only in the
  conversation is lost. Re-read an authoritative file when you need it again rather than keeping it in view.
- **Large outputs are externalised.** A big command result or search is written to a scratch file and you get a
  summary plus its path; read the part you need with `read_scratch`.
- **Reaching a context target never fails your task.** Budgets are guidance; the orchestrator raises or lowers them.
  What matters is useful progress: edits that make the requirement true, and checks that show it.

## Completion semantics

- `REPAIRED_CLAIMED` — the requirement is now true, you made it observable with a test you added, and the relevant
  checks pass. This is a *claim*: an independent verifier grades it later. Never describe it as accepted or verified.
- `PARTIAL` — some items are true and observable, others are not. Name precisely which, and what remains.
- `OWNER_DECISION_REQUIRED` — closing an item needs a choice the accepted sources do not make. State the choice, the
  options and the consequence; do the rest.
- `INCOMPLETE` — you could not land the work. Say exactly where you stopped and what the next worker should do.

An honest `PARTIAL` with evidence is worth more than a `REPAIRED_CLAIMED` you cannot show. Do not report a figure you
did not observe, and never weaken a test, check, schema or policy to make something pass."""


def contract_excerpt(a, b):
    lines = open(CONTRACT).read().split("\n")
    body = "\n".join(f"{i:>4}  {lines[i-1]}" for i in range(a, min(b, len(lines)) + 1))
    return body


def decision_excerpt(key, max_chars=2600):
    rel, gist = DECISIONS[key]
    path = os.path.join(ROOT, rel)
    if not os.path.isfile(path):
        return f"- **{key}** ({rel}): {gist}. [file not found at compile time]"
    text = open(path).read()
    if path.endswith(".yaml"):
        body = text[:max_chars]
    else:
        # prefer the section that states the decision itself
        m = re.search(r"(?ms)^## (The decision|The decision, in the owner's terms|The clarification.*?|Ruling)\b.*?(?=^## |\Z)", text)
        body = (m.group(0) if m else text)[:max_chars]
    return f"**{key}** — {gist}\nSource: `{rel}`\n\n```\n{body.strip()}\n```"


def skill_excerpt(name, max_chars=1400):
    path = os.path.join(ROOT, "framework", "skills", f"{name}.yaml")
    if not os.path.isfile(path):
        return f"- **{name}**: [not found]"
    return f"**{name}** (`framework/skills/{name}.yaml`)\n\n```yaml\n{open(path).read()[:max_chars].strip()}\n```"


def phase_state():
    import yaml
    s = yaml.safe_load(open(os.path.join(PHASE, "ORCHESTRATOR_STATE.yaml")))
    cur = s.get("current_candidate") or {}
    return (f"Phase {s['phase']} — {s['phase_name']}. Lifecycle `{s['lifecycle_state']}`, loop `{s['loop_status']}`.\n"
            f"Current candidate `{cur.get('id')}` ({cur.get('commit','?')[:7]}) — **rejected** by the iteration-1 "
            f"independent verification; this repair iteration exists to close what it found.\n"
            f"Active gate: `GATE-P2-REPAIR-2`. Acceptance is decided later by fresh independent verifiers against the "
            f"frozen gate contract — never by a repair worker, and never by this orchestration tooling.")


def compile_brief(spec):
    t = spec["task"]
    out = []
    out.append(f"# Worker bootstrap — {t['title']}\n")
    out.append("You are a **governed worker** in the Governance OS Phase-2 orchestration. This bootstrap is your "
               "operating context: it carries the rules, the authority model, the requirement you must satisfy and "
               "the conventions of this repository. Do not infer these by exploring; they are here because they are "
               "authoritative. Where you need more, read the source files named below.\n")

    out.append("## Where you are\n\n" + phase_state() + "\n")

    out.append(f"## Your role and authority\n\n"
               f"- Role: **{spec['role']}**, authority level **{spec.get('authority_level','L2 (implementation)')}**.\n"
               f"- You produce **claims**, never acceptances, and you grade nobody's work, including your own.\n"
               f"- You may write only the paths this task owns (below). The adapter refuses every other write.\n"
               f"- You never read another worker's evidence, any agent transcript, or any task-output store.\n")

    if spec.get("decisions"):
        out.append("## Authority, trust and the decisions in force\n\n"
                   "These are quoted from their own records. They bind your repair; a repair that contradicts one is "
                   "wrong even if its tests pass.\n\n" + "\n\n".join(decision_excerpt(k) for k in spec["decisions"]) + "\n")

    if spec.get("contract_lines"):
        out.append("## The owner source — Contract v3, verbatim\n\n"
                   "`Governance_OS_Capability_Acceptance_Contract_v3.md` (SHA-256 `4c2df291…5ed3`). These are the lines "
                   "your requirement compiles from; read them as written, not as summarised elsewhere.\n")
        for a, b in spec["contract_lines"]:
            out.append(f"```text\n{contract_excerpt(a, b)}\n```")
        out.append("")

    if spec.get("skills"):
        out.append("## Applicable skills (the product's own, bounded to this task)\n\n"
                   + "\n\n".join(skill_excerpt(s) for s in spec["skills"]) + "\n")

    if spec.get("conventions"):
        out.append("## How this repository works\n\n" + "\n\n".join(CONVENTIONS[c] for c in spec["conventions"] if c in CONVENTIONS) + "\n")

    out.append("## Your task contract\n\n" + t["contract"].strip() + "\n")

    out.append("## Paths you own (writable)\n\n" + "\n".join(f"- `{p}`" for p in t["owned_paths"]) + "\n")
    out.append("## Prohibited\n\n" + "\n".join(f"- {p}" for p in t.get("prohibited", [
        "any path outside the list above — the adapter refuses it; do not work around a refusal",
        "renaming, removing or `#[ignore]`-ing an existing test",
        "weakening a check, schema, policy or assertion to make something pass",
        "editing anything under `release/`, `framework/contracts/`, `docs/generated/` or the evidence map",
    ])) + "\n")

    out.append("## Checks you must run before finishing\n\n"
               + "\n".join(f"- `{c}` — {why}" for c, why in t["required_checks"].items())
               + "\n\nRun them through `run_check`; you get a summary rather than a raw log. Report only what you "
                 "observed.\n")

    out.append(CHECKPOINT_PROTOCOL + "\n")

    out.append("## How to work\n\n"
               "1. Read the requirement above and the specific code it names — not the whole repository.\n"
               "2. Make the first edit within your first few tool calls. If you find yourself reading a fourth file "
               "before editing anything, stop and make the smallest change that moves the requirement forward.\n"
               "3. Add the test that makes the new behaviour observable, in the file your task contract names.\n"
               "4. Run the relevant check. Fix what it reports. Checkpoint.\n"
               "5. Repeat for the next item, then call `finish` with an honest verdict.\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    brief = compile_brief(json.load(open(a.spec)))
    if a.out:
        open(a.out, "w").write(brief)
        print(f"{a.out}: {len(brief)} chars (~{len(brief)//4} tokens)")
    else:
        sys.stdout.write(brief)


if __name__ == "__main__":
    main()
