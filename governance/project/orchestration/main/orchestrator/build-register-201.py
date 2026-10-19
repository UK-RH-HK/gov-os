"""Build drafts/register-201.md from drafts/DEC-662-draft.md: DEC-662 as drafted, DEC-663 as its own entry, the version row."""
S = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/"
t = open(S + "drafts/DEC-662-draft.md", encoding="utf-8").read()
out = []
for line in t.split("\n"):
    if line.startswith("NOT YET IN THE REGISTER"):
        out.append(
            "Decided 2026-10-12 about 11:35, while the owner's quiet window in the main tree (the B1 apply) "
            "was open; appended on 2026-10-13 after the owner reported the apply done (`71ae763f`)."
        )
        continue
    if line.startswith("  - **W1-31 round's packages G, H, I**"):
        continue
    if line.startswith("  - **With the owner:**"):
        out.append(
            "  - **With the owner at the time (answered in DEC-664 and DEC-666):** package 1 (the template's "
            "permission source denies every edit of `tests/acceptance/**`, the test designer's included) and "
            "package 3's \"now\" before `created_at`."
        )
        continue
    out.append(line)
t = "\n".join(out).rstrip("\n") + "\n"
t = t.replace(
    "W1-42 lead run 2 returns PACKAGES: delegated decisions",
    "W1-42 lead run 2 returns PACKAGES and the W1-31 round returns DONE: delegated decisions",
)
t += """
### DEC-663 — The W1-31 round's packages G, H and I
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-12; told to the owner, who may replace it) · **Under:** DEC-655, DEC-584 · **Basis:** the W1-31 round lead's return (`log/W1-31b-lead-run1.json`, DONE at `065f9b83` on `w1/W1-31b`) and the probe (`docs/probes/DAEO-6mk8/PR-DAEO-6mk8-round-DEC-655.md`, pass)
- **Decision** (each P3, reversible; confidence medium):
  - **G, a ticket whose sessions are of more than one Claude Code version:** stays as built. `agent.version` is "not measured" and the sessions are still counted. A named residual and a Wave 2 item (each session's own version in the record). No further round (finish line, DEC-584). The lead recommended a new public key per session; that is the Wave 2 item, so the two recommendations agree on the end state and differ only on when.
  - **H, attachment types and line types no specimen shows:** the standing rule is kept: a form no specimen shows is "not measured" by name. A fresh specimen is read at each CLI update. Wave 2 list: under this rule every log is "not measured" after an update until the new specimen is read.
  - **I, `instructions` and `sandbox_instructions` lines:** they count nothing today. Whether they replace the estimate is on the Wave 2 list.

| Version | Date | Change |
|---|---|---|
| 0.201 | 2026-10-13 | Orchestrator, delegated: DEC-662 (W1-42 lead's run 2 packages 2, 3 names, 4, 6, 7, 8; Wave 2 items; run 2's deviations for the exit auditor), DEC-663 (W1-31 round's packages G, H, I: as built, standing rule kept, Wave 2 items). Decided 2026-10-12, appended after the owner's B1 apply. Next free id: DEC-664. |
"""
open(S + "drafts/register-201.md", "w", encoding="utf-8").write("\n" + t)
print(len(t), "chars")
