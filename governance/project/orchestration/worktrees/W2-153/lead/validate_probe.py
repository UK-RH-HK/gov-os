import json, pathlib, sys, re, yaml, jsonschema
d = pathlib.Path('/home/usain/gov-os-worktrees/W2-153/template/governance/kernel/schemas')
store = {}
for p in d.glob('*.json'):
    s = json.loads(p.read_text()); store[p.name] = s; store[p.resolve().as_uri()] = s
    if '$id' in s: store[s['$id']] = s
schema = json.loads((d/'probe.schema.json').read_text())
resolver = jsonschema.RefResolver(base_uri=(d/'probe.schema.json').resolve().as_uri(), referrer=schema, store=store)
t = pathlib.Path(sys.argv[1]).read_text()
front = yaml.safe_load(t.split('\n---', 1)[0][3:])
v = jsonschema.Draft202012Validator(schema, resolver=resolver)
print('jsonschema', jsonschema.__version__, 'errors:', [e.message for e in v.iter_errors(front)] or 'none')
m = re.findall(r'```verdict\n(.*?)\n```', t, re.S)
print('verdict blocks:', len(m), json.loads(m[-1]) if m else None)
