"""Lead probe: the shape of `gov check --json` on a refusal (the W2-120 I3 gov-check case's envelope)."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-120/tests/acceptance/W2-120")
import w2_120_support as sup  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    sup.plant_clean(root, "alpha")
    sup.plant_with(root, sup.CLAUDE, "alpha", {"allowed-tools": "Bash(git:*)"})
    declared = yaml.safe_load((sup.CHECKS / "skill-regression-a.yaml").read_text(encoding="utf-8"))
    declared["command"] = f"python3 -m gov.check.skill_validator --both-layouts {sup.KERNEL}/alpha"
    checks = root / "template" / "governance" / "kernel" / "checks"
    checks.mkdir(parents=True)
    (checks / "skill-regression-a.yaml").write_text(yaml.safe_dump(declared, sort_keys=False), encoding="utf-8")
    done = subprocess.run([sys.executable, "-P", "-m", "gov.cli.main", "check", "--json"], cwd=root,
                          env=sup.env_for(), capture_output=True, text=True, timeout=300, check=False)
    payload = json.loads(done.stdout)
    print("exit", done.returncode, "top keys", list(payload), "result", payload.get("result"))
    details = payload.get("error", {}).get("details", {})
    print("details keys", list(details))

    def walk(node, trail):
        if isinstance(node, dict):
            if node.get("id") == "skill-regression-a":
                print("ENTRY at", trail, json.dumps(node)[:1500])
            for k, v in node.items():
                walk(v, trail + [k])
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, trail + [i])

    walk(payload, [])
