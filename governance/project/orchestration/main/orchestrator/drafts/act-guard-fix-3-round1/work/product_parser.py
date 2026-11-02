"""The product's parser on the 61 rows: how many hold a write it cannot resolve (which decide() refuses to every
role), before and with the shell-level part of ACT-GUARD-FIX-3 (heredocs, own variables, loops, keywords,
substitutions). Uses src/gov (the product as it stands), read only."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/src")
sys.path.insert(0, os.path.dirname(HERE))
import bash_writes as bw
from gov.guard.decide import _UNRESOLVABLE, _expand_token, _extract_bash_write_targets
import gov.guard.decide as d
print("parser from", d.__file__)
c = json.load(open(os.path.join(HERE, "corpus.json")))
twin = {50: 54, 51: 55, 52: 58, 53: 59}
before = after = 0
for row in c:
    o = c[twin.get(row["i"], row["i"])]
    cmd = (o["input"] or {}).get("command", "")
    if o.get("tmpdir"):
        os.environ["TMPDIR"] = o["tmpdir"]
    else:
        os.environ.pop("TMPDIR", None)
    t = _extract_bash_write_targets(cmd, o["cwd"]) or []
    b = _UNRESOLVABLE in t
    try:
        j = bw.judge(cmd, o["cwd"], _extract_bash_write_targets, _expand_token)
        a = _UNRESOLVABLE in j.shell
    except bw.Unreadable:
        a = b
    before += b
    after += a
print(f"rows whose writes the product parser cannot resolve: before {before}/61, with the shell-level fix {after}/61")
