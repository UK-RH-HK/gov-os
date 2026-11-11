"""The containment gate's findings (counted, after the pre-close gate) for given tickets, read-only. Usage: containment.py <root> <ticket>..."""
import sys
from pathlib import Path
from gov.close import command as C
root = Path(sys.argv[1]).resolve()
for t in sys.argv[2:]:
    commits = C._ticket_commits(root, t)
    try:
        C._check_containment(root, commits)
        print(t, "containment: no finding over", len(commits), "ticket commits")
    except C._Finding as f:
        print(t, "containment FINDING:", len(f.findings), "lines")
        [print("   ", l) for l in f.findings]
    except Exception as e:
        print(t, "containment ERROR:", type(e).__name__, str(e)[:300])
