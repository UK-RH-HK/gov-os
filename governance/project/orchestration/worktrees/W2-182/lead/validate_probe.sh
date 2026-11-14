#!/usr/bin/env bash
# The probe record's front matter as one JSON instance, validated by check-jsonschema (the pinned validator, DEC-074)
# against template/governance/kernel/schemas/probe.schema.json (its common.schema.json refs resolve beside it).
set -u
T=/home/usain/gov-os-worktrees/W2-182
I=/tmp/w2-182-probe-instance.json
python3 - "$T/docs/probes/DAEO-5y8d/PR-DAEO-5y8d.md" "$I" <<'PY'
import json, sys, datetime, yaml
text = open(sys.argv[1], encoding="utf-8").read()
front = yaml.safe_load(text.split("---\n", 2)[1])
json.dump(front, open(sys.argv[2], "w"), default=str)
block = text.split("```verdict\n", 1)[1].split("```", 1)[0]
print("verdict block:", [(k["kpi"], k["verdict"]) for k in json.loads(block)["kpis"]])
PY
CJ=$(command -v check-jsonschema || echo /home/usain/.local/bin/check-jsonschema)
"$CJ" --version
"$CJ" --schemafile "$T/template/governance/kernel/schemas/probe.schema.json" "$I"
echo "check-jsonschema exit $?"
