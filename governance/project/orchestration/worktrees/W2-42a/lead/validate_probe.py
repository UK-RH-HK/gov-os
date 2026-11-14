"""Validate a probe record's frontmatter against probe.schema.json (with common.schema.json refs)."""
import json, sys, yaml
from pathlib import Path
from jsonschema import Draft202012Validator, RefResolver

S = Path("/home/usain/gov-os-worktrees/W2-42a/template/governance/kernel/schemas")
store = {f.name: json.loads(f.read_text()) for f in S.glob("*.schema.json")}
schema = store["probe.schema.json"]
resolver = RefResolver(base_uri=S.as_uri() + "/", referrer=schema,
                       store={S.as_uri() + "/" + k: v for k, v in store.items()})
text = Path(sys.argv[1]).read_text()
fm = yaml.safe_load(text.split("---", 2)[1])
errs = list(Draft202012Validator(schema, resolver=resolver).iter_errors(fm))
for e in errs:
    print("INVALID:", list(e.path), e.message)
print("valid" if not errs else f"{len(errs)} error(s)")
sys.exit(1 if errs else 0)
