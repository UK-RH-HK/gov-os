import sys
root = sys.argv[1]
sys.path.insert(0, root + "/src")
from gov.guard import decide as D, bash_writes as B
import inspect
CASES = {
    "g": "bash -euo pipefail <<'EOF'\n# don't overwrite\necho hi\nEOF",
    "i": "bash <<'EOF'\n# it's fine\nls\nEOF",
    "cat-data": "cat <<'EOF'\n# it's data\nEOF",
    "top-comment": "ls # it's fine",
}
for k, c in CASES.items():
    print(k, "lift:", D.lift_refusal(c)[:40] or "none")
    try:
        t = D._extract_bash_write_targets(c, root) if hasattr(D, "_extract_bash_write_targets") else "n/a"
        print(k, "targets:", t)
    except Exception as e:
        print(k, "targets EXC:", type(e).__name__, str(e)[:80])
    try:
        print(k, "read_view:", str(B.read_view(c))[:100])
    except Exception as e:
        print(k, "read_view EXC:", type(e).__name__, str(e)[:80])
print(inspect.signature(D._extract_bash_write_targets) if hasattr(D, "_extract_bash_write_targets") else "")
