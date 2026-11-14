import json, yaml, sys
from pathlib import Path
import jsonschema
S = Path('/home/usain/gov-os-worktrees/W2-183/template/governance/kernel/schemas')
probe = json.loads((S/'probe.schema.json').read_text())
store = {n: json.loads((S/n).read_text()) for n in ('common.schema.json','probe.schema.json')}
resolver = jsonschema.RefResolver(base_uri=S.as_uri() + '/', referrer=probe, store={S.as_uri()+'/'+k: v for k, v in store.items()})
fm = yaml.safe_load(Path(sys.argv[1]).read_text().split('---\n')[1])
cls = getattr(jsonschema, 'Draft202012Validator', jsonschema.Draft7Validator)
errs = list(cls(probe, resolver=resolver).iter_errors(fm))
print(jsonschema.__version__, cls.__name__, 'valid' if not errs else [e.message for e in errs])
