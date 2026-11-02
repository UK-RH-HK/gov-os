"""Rebuild W2-42a's planted fixture from ACT-GUARD-FIX-3's reviewed test file (DEC-1040 item 2, DEC-958).

Run by the independent test designer, not by the tests: ``python3 build_planted.py <test_guard_fix_3.py> <out.json>``.

Kept, each with its name, role, tool and input as the reviewed file states them:

- every case the file expects the hook to refuse: its planted writes into the acceptance folder (rule 1) and outside
  a reviewer's record (rule 5), and its unknown or unparseable forms (an unterminated heredoc, unbalanced quotes, a
  binding the guard cannot follow, ``exec``, an unknown function handed a test, a patch applier);
- the reads it expects refused (rules 2 and 3) are left out: they are not writes;
- the one logged pattern it leaves refused by design as a form the guard cannot read (row 46: an unquoted Python
  heredoc the shell rewrites, in a command naming the tests); row 39's pattern (an unmatched glob in /tmp) is left
  out, since W2-42a's KPI line 4 makes it a literal path that passes;
- guard4_check.py's planted writes of rules 1 and 5, which the reviewed file runs too.

The main tree's path in an input is written ``{ROOT}``, so the tests put the tree under test in its place.
"""
import importlib.util
import json
import sys

MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
WRITE_REASONS = ("rule1", "rule5", "dec958 engineer", "fix2 engineer", "fix2 unbalanced")


def load(path):
    spec = importlib.util.spec_from_file_location("test_guard_fix_3", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rooted(value):
    if isinstance(value, str):
        return value.replace(MAIN, "{ROOT}")
    if isinstance(value, dict):
        return {k: rooted(v) for k, v in value.items()}
    return value


def main(src, out):
    mod = load(src)
    cases = []
    for name, role, tool, tin, want in mod.CASES:
        if want != "deny":
            continue
        if name.startswith("fix3 data heredoc with a substitution reading a key"):
            continue  # rule 3, a read
        cases.append((name, role, tool, tin))
    for name, role, tool, tin, want, _ in mod.CORPUS_PATTERNS:
        if want == "deny" and name.startswith("row 46"):
            cases.append((name, role, tool, tin))
    for name, role, tool, tin, want in mod._guard4_cases():
        bare = name[len("guard4: "):]
        if want == "deny" and bare.startswith(WRITE_REASONS):
            cases.append((name, role.partition("@")[0], tool, tin))
    seen = set()
    rows = []
    for name, role, tool, tin in cases:
        assert name not in seen, name
        seen.add(name)
        rows.append({"name": name, "role": role, "tool": tool, "input": rooted(tin)})
    base = base_parser(rows, sys.argv[3]) if len(sys.argv) > 3 else {}
    for row in rows:
        if row["name"] in base:
            row["base_caught"] = base[row["name"]]
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"source": "drafts/act-guard-fix-3/test_guard_fix_3.py (b6f8216c97bc) and guard4_check.py",
                   "base": BASE, "planted": rows}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"planted {len(rows)}; the base parser catches {sum(base.values())} of the {len(base)} Bash cases")


BASE = "w2/integrate at a58ba344"
_PROBE = r"""
import json, os, sys
sys.path.insert(0, sys.argv[1])
from w2_42a_support import parser_caught
rows = json.load(sys.stdin)
print(json.dumps({r["name"]: parser_caught(r, sys.argv[2]) for r in rows}))
"""


def base_parser(rows, base_tree):
    """``base_caught``: whether the base's own parser (``base_tree``, a checkout of the base) catches each planted
    Bash write, as ``w2_42a_support.parser_caught`` reads it (failure line 1)."""
    import os
    import subprocess
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bash = [r for r in rows if r["tool"] == "Bash"]
    env = {k: v for k, v in os.environ.items() if k not in ("TMPDIR", "GOV_ROLE", "GOV_TICKET")}
    env["PYTHONPATH"] = os.path.join(base_tree, "src")
    p = subprocess.run([sys.executable, "-c", _PROBE, here, base_tree], input=json.dumps(bash),
                       capture_output=True, text=True, env=env, timeout=300, check=True)
    return json.loads(p.stdout)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
