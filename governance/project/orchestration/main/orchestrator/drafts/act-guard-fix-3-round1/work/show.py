import json, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gov.guard.decide import _extract_bash_write_targets, _UNRESOLVABLE
import importlib.util
spec = importlib.util.spec_from_file_location("live", os.path.join(os.path.dirname(__file__), "live_pretooluse.py"))
live = importlib.util.module_from_spec(spec); spec.loader.exec_module(live)
SECRET = re.compile(r"(sk-[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9]{8,}|xox[bp]-[\w-]+|AKIA[0-9A-Z]{12,}|(?i:(?:token|secret|password|api[_-]?key)\s*[=:]\s*)[^\s'\"]{6,}|[A-Za-z0-9+/]{40,}={0,2})")
def red(s): return SECRET.sub("<REDACTED>", s)
c = json.load(open(os.path.join(os.path.dirname(__file__), "corpus.json")))
for i in map(int, sys.argv[1:]):
    o = c[i]
    cmd = (o["input"] or {}).get("command", "")
    if o.get("tmpdir"): os.environ["TMPDIR"] = o["tmpdir"]
    else: os.environ.pop("TMPDIR", None)
    t = _extract_bash_write_targets(cmd, o["cwd"])
    print(f"===== row {i} len={len(cmd)} cwd={o['cwd']} role={o.get('launch_role')} tmp={o.get('tmpdir')}")
    print("targets:", None if t is None else [x for x in t][:12], "| inline:", live.inline_writes_acceptance(cmd))
    print(red(cmd[:int(os.environ.get('N','1500'))]))
