import sys, pathlib, re
sys.path.insert(0, '/home/usain/gov-os-worktrees/W2-188/src')
from gov.accept.runner import parse_map, line_names, Unreadable, Unlisted
t = pathlib.Path(sys.argv[1]).read_text()
try:
    m = parse_map(t); print('OK', sorted(m), sum(map(len, m.values())))
except (Unreadable, Unlisted) as e:
    print('REFUSED', type(e).__name__, e.args)
for cell in ['`success-1` (A9)', 'success-1 (A9)', "failure-3 (§9 keeps S10's second reranker forbidden)", "failure-3 (§9 keeps W2-88 `S10`'s second reranker forbidden)"]:
    try: print(repr(cell), '->', line_names(cell))
    except Exception as e: print(repr(cell), '->', type(e).__name__)
# candidate: strip backticks round names, code-span S10, move self-check row out
lines = t.splitlines()
out=[]
for l in lines:
    if l.startswith('| matcher self-checks'): continue
    l = re.sub(r"^\| `((?:success|failure)-\d)`", r"| \1", l)
    if l.startswith('| failure-3'): l = l.replace("S10's second reranker", "`S10`'s second reranker", 1)
    out.append(l)
try:
    m = parse_map('\n'.join(out)); print('CANDIDATE OK', sorted(m), sum(map(len, m.values())))
except (Unreadable, Unlisted) as e:
    print('CANDIDATE REFUSED', type(e).__name__, e.args)
