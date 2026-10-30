"""The mutation check refuses acceptance paths on implementer tickets (MR-3): removes the two refused widenings from
W2-05 and W2-60a (the test designer's role already writes tests/acceptance/** under an in-progress ticket, its brief
naming the decision, DEC-906) and corrects DEC-951's "how it is applied" to say so. Parses both tickets."""
import pathlib

import yaml

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")


def ed(rel, old, new):
    p = ROOT / rel
    t = p.read_text(encoding="utf-8")
    if new and new in t:
        return
    assert t.count(old) == 1, (rel, old[:60])
    p.write_text(t.replace(old, new), encoding="utf-8")


ed(".tickets/DAEO-0z8c.md", "- tests/acceptance/W1-02/**\n", "")
ed(".tickets/DAEO-cv58.md", "- tests/acceptance/serial-only.txt\n", "")
R = "docs/DECISION_REGISTER.md"
ed(R, "  - **Item 2:** W2-05's ticket is widened by `tests/acceptance/W1-02/**` for the revision batch; its run 4 follows.",
   "  - **Item 2:** no ticket widening is needed. The test designer's role writes `tests/acceptance/**` under an "
   "in-progress ticket, and its brief names DEC-951 item 2 for W1-02's tests (DEC-906); the mutation check refuses "
   "acceptance paths on an implementer ticket. W2-05's run 4 follows.")
ed(R, "  - **Item 4:** W2-60a's ticket is widened by the three named unit files and `tests/acceptance/serial-only.txt`; "
      "its round 3 is its last.",
   "  - **Item 4:** W2-60a's ticket is widened by the three named unit files. Its test designer writes the "
   "nightly-route line in `tests/acceptance/serial-only.txt` by its role, its brief naming DEC-951 item 4. Round 3 is "
   "its last.")
for t in ("DAEO-0z8c", "DAEO-cv58"):
    yaml.safe_load((ROOT / ".tickets" / (t + ".md")).read_text(encoding="utf-8").split("\n---", 1)[0].lstrip("-\n"))
print("fixed")
