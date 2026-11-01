"""Review the differential's changed cases: for each, the candidate's judgement (shell targets, code findings) and the
lines that put a write operation near the acceptance path. Secrets-like strings are redacted; lines cut to 150.
Usage (pinned interpreter, -E): review_diff.py live2cand|cand2live [index ...]"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import bash_writes as bw
from gov.guard.decide import _expand_token, _extract_bash_write_targets

SECRET = re.compile(r"(sk-[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9]{8,}|xox[bp]-[\w-]+|AKIA[0-9A-Z]{12,}|"
                    r"(?i:(?:token|secret|password|api[_-]?key)\s*[=:]\s*)[^\s'\"]{6,}|[A-Za-z0-9+/]{40,}={0,2})")
WRITEY = re.compile(r"(>>?|\btee\b|\bcp\b|\bmv\b|sed -i|\btouch\b|\bmkdir\b|\brm\b|open\(|write_text|write_bytes|"
                    r"shutil\.|os\.(remove|rename|replace|makedirs|mkdir|unlink)|\bgit (checkout|restore|rm|mv)\b)")
rows = json.load(open(os.path.join(HERE, "diff_cmds.json")))
mode = sys.argv[1]
want = [int(x) for x in sys.argv[2:]]
for i, r in enumerate(rows):
    changed = (r["live"][0] == "deny" and r["cand"][0] == "allow") if mode == "live2cand" else \
              (r["live"][0] == "allow" and r["cand"][0] == "deny")
    if not changed or (want and i not in want):
        continue
    cmd = r["cmd"]
    if r["tmpdir"]:
        os.environ["TMPDIR"] = r["tmpdir"]
    else:
        os.environ.pop("TMPDIR", None)
    print(f"===== #{i} {r['role']} cwd={r['cwd']} len={len(cmd)} | live: {r['live'][1][:50]} | cand: {r['cand'][1][:50]}")
    try:
        j = bw.judge(cmd, r["cwd"], _extract_bash_write_targets, _expand_token)
        print("  shell:", sorted(set(j.shell))[:8])
        for t, scope in j.findings:
            if t:
                print("  code:", sorted(set(map(str, t)))[:6], "| scope names tests:", "tests/acceptance/" in scope)
    except bw.Unreadable as e:
        print("  UNREADABLE", e)
    flagged = [l for l in cmd.split("\n") if "tests/acceptance" in l and WRITEY.search(l)]
    for l in flagged[:6]:
        print("  >>", SECRET.sub("<REDACTED>", l.strip())[:150])
