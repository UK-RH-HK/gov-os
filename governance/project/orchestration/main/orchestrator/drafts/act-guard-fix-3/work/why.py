"""Why the candidate judges a corpus row as it does (run with the pinned interpreter, -E)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import bash_writes as bw
from gov.guard.decide import _expand_token, _extract_bash_write_targets

c = json.load(open(os.path.join(HERE, "corpus.json")))
for i in map(int, sys.argv[1:]):
    o = c[i]
    cmd = o["input"]["command"]
    if o.get("tmpdir"):
        os.environ["TMPDIR"] = o["tmpdir"]
    else:
        os.environ.pop("TMPDIR", None)
    print("===== row", i)
    try:
        text, bodies = bw.heredocs(cmd)
        print("bodies:", [(b["quoted"], len(b["text"])) for b in bodies])
        lifted, subs = bw.lift(text)
        print("subs:", [s[:80] for s in subs])
        j = bw.judge(cmd, o["cwd"], _extract_bash_write_targets, _expand_token)
        print("shell:", j.shell[:10])
        for t, scope in j.findings:
            print("finding:", t[:6], "| mention:", "tests/acceptance/" in scope)
    except bw.Unreadable as e:
        print("UNREADABLE:", e)
