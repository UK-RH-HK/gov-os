"""bash_writes on every command of the differential history: anything raised but Unreadable is a bug (the hook would
refuse by crashing). Prints counts and the indexes only. Run with the pinned interpreter, -E."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import bash_writes as bw
from gov.guard.decide import _expand_token, _extract_bash_write_targets
rows = json.load(open(os.path.join(HERE, "diff_cmds.json")))
bad, unreadable, slow = [], 0, []
for i, r in enumerate(rows):
    t0 = time.time()
    try:
        bw.judge(r["cmd"], r["cwd"], _extract_bash_write_targets, _expand_token)
        bw.reads_view(r["cmd"])
    except bw.Unreadable:
        unreadable += 1
    except Exception as exc:
        bad.append((i, type(exc).__name__, str(exc)[:80]))
    if time.time() - t0 > 2:
        slow.append((i, round(time.time() - t0, 1)))
print("commands", len(rows), "| unreadable (judged as before)", unreadable, "| crashes", len(bad), "| over 2 s", slow)
for b in bad[:20]:
    print("  ", b)
