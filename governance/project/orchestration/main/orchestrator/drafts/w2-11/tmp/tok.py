import re
import sys
from pathlib import Path

sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp/clone/tests/acceptance/W1-35")
import conftest as c  # noqa: E402

print("MAX_BODY_TOKENS", c.MAX_BODY_TOKENS)
base = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp")
for label, path in [("integrate (cur)", base / "mf/orchestration.cur"), ("W2-11 old", base / "mf/orchestration.old"),
                    ("base", base / "mf/orchestration.base"), ("resolved", base / "resolved/orchestration.md")]:
    text = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    print(label, c.token_count(m.group(2)))
