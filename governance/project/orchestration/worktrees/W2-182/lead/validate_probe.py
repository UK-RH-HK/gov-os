"""Validate the probe record's front matter against probe.schema.json (with common.schema.json beside it)."""
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

tree = Path("/home/usain/gov-os-worktrees/W2-182")
schemas = tree / "template/governance/kernel/schemas"
text = (tree / "docs/probes/DAEO-5y8d/PR-DAEO-5y8d.md").read_text(encoding="utf-8")
front = yaml.safe_load(text.split("---\n", 2)[1])
probe = json.loads((schemas / "probe.schema.json").read_text())
common = json.loads((schemas / "common.schema.json").read_text())
reg = Registry().with_resources([
    ("common.schema.json", Resource.from_contents(common)),
    (common.get("$id", "common.schema.json"), Resource.from_contents(common)),
])
errors = list(Draft202012Validator(probe, registry=reg).iter_errors(front))
for e in errors:
    print("INVALID:", list(e.path), e.message)
print("valid" if not errors else f"{len(errors)} error(s)", sorted(front))
# the verdict block parses
block = text.split("```verdict\n", 1)[1].split("```", 1)[0]
kpis = json.loads(block)["kpis"]
print("verdict block:", [(k["kpi"], k["verdict"]) for k in kpis])
sys.exit(1 if errors else 0)
