"""DEC-614: add the missing `type` or `state_class` frontmatter to seven documents. Frontmatter lines only.

Each new line is put directly before the closing `---` of the frontmatter; no existing line changes, and the text
below the frontmatter is compared byte for byte before anything is written.
"""
import sys

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS/"
ADD = {
    "docs/adr/ADR-0001-threat-model.md": ["state_class: AUTHORITATIVE"],
    "docs/adr/ADR-0002-architecture-and-stack.md": ["state_class: AUTHORITATIVE"],
    "docs/changes/S2-CIT-E.md": ["state_class: EVIDENCE"],
    "docs/changes/S2-CIT-P.md": ["state_class: EVIDENCE"],
    "docs/charter/CHARTER_v5.md": ["type: specification", "state_class: AUTHORITATIVE"],
    "docs/contract/CONTRACT_v4.md": ["type: specification", "state_class: AUTHORITATIVE"],
    "docs/plan/WAVE_1_WBS.md": ["type: plan", "state_class: AUTHORITATIVE"],
}
plan = {}
for rel, new in ADD.items():
    text = open(ROOT + rel, encoding="utf-8").read()
    lines = text.split("\n")
    assert lines[0] == "---", rel
    end = lines.index("---", 1)
    keys = {line.split(":", 1)[0] for line in lines[1:end] if line and not line.startswith((" ", "-"))}
    new = [line for line in new if line.split(":", 1)[0] not in keys]
    out = lines[:end] + new + lines[end:]
    if "\n".join(out[end + len(new):]) != "\n".join(lines[end:]):
        sys.exit(f"{rel}: the text below the frontmatter would change; nothing written")
    plan[rel] = ("\n".join(out), new)
for rel, (text, new) in plan.items():
    with open(ROOT + rel, "w", encoding="utf-8") as f:
        f.write(text)
    print(rel, "+", new)
