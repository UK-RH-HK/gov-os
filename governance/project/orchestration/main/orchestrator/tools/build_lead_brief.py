#!/usr/bin/env python3
"""Build a lead brief: the ticket's own part, then the common lead brief with its placeholders filled (DEC-824).

    python3 build_lead_brief.py <part.md> <out.md> ID=DAEO-xxxx W2=W2-nn PROFILE=... PATHS=... ROWS=... SOURCES=... IMPL=... EST=...

The common brief is read from the main tree's working copy (`governance/project/briefs/LEAD-w2-common.md`), so a
staged owner edit is the text the lead gets. Every placeholder must be given; a placeholder left over is an error.
"""
import re
import sys
from pathlib import Path

import os

# GOV_BRIEF_COMMON names a draft of the common brief while the committed one cannot change (a close queue runs, and an
# edit of a tracked file would stop its gate (d)); the draft is committed as soon as the queue ends.
COMMON = Path(os.environ.get("GOV_BRIEF_COMMON",
                             "/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/briefs/LEAD-w2-common.md"))
KEYS = ("ID", "W2", "PROFILE", "PATHS", "ROWS", "SOURCES", "IMPL", "EST")


def main() -> None:
    part, out = Path(sys.argv[1]), Path(sys.argv[2])
    values = dict(arg.split("=", 1) for arg in sys.argv[3:])
    missing = [key for key in KEYS if key not in values]
    if missing:
        sys.exit(f"missing: {', '.join(missing)}")
    # IMPL fills every worker's and the lead's `Implements:` trailer: it must be ids the store resolves, never a role
    # (P-TRACE-IMPL-1: 41 commits carried `Implements: engineer` or a like role and turned product traceability red).
    impl = [part.strip() for part in values["IMPL"].split(",")]
    if not impl or not all(re.fullmatch(r"(DEC|CAP|AR|MR|ADR)-[0-9A-Za-z.]+", part) for part in impl):
        sys.exit(f"IMPL must be decision or Contract ids (e.g. DEC-925), not {values['IMPL']!r}")
    common = COMMON.read_text()
    # The common brief's first three paragraphs are its heading, its note to the orchestrator and the opening
    # "You are the ticket lead" paragraph, which the ticket's own part gives with the ticket's facts.
    body = common.split("\n\n", 3)[3]
    for key in KEYS:
        body = body.replace("{" + key + "}", values[key])
    left = re.findall(r"\{[A-Z0-9]+\}", body)
    if left:
        sys.exit(f"placeholders left: {sorted(set(left))}")
    out.write_text(part.read_text().rstrip("\n") + "\n\n" + body)
    print(f"{out}: {len(out.read_text())} characters")


if __name__ == "__main__":
    main()
