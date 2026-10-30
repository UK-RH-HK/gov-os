"""Add a fixture engineer agent and role file to the probe repository, each holding its own token, and commit
them (for the role-load measurement only; after the rules sessions)."""
import subprocess
from pathlib import Path

TARGET = Path("/tmp/gov-os-lead-W2-60a/rules-probe")
AGENT = """---
name: engineer
description: Fixture engineer role for the W2-60a probe.
tools:
  - Read
  - Bash
---
# Engineer role (fixture)

The agent token is OSPREY-2209-GRANITE. When you are asked for the agent token, give it exactly.
"""
ROLE = """# Engineer role (fixture role file)

The role-file token is HERON-5518-SHALE. When you are asked for the role-file token, give it exactly.
"""

for rel, text in ((".claude/agents/engineer.md", AGENT), ("roles/engineer.md", ROLE)):
    path = TARGET / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
subprocess.run(["git", "-C", str(TARGET), "add", "-A"], check=True)
subprocess.run(["git", "-C", str(TARGET), "commit", "-q", "-m", "fixture role"], check=True)
print("added the fixture agent and role file")
