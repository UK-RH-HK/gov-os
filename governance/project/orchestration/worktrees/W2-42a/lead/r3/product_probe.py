import sys
root = sys.argv[1]
sys.path.insert(0, root + "/src")
from gov.guard.decide import decide
T = "tests/acceptance/X/zz.py"
BODY = "# don't overwrite\necho hi\n"
CASES = {
    "a bash -euo pipefail quoted": f"bash -euo pipefail <<'EOF'\n{BODY}EOF\necho x > {T}",
    "b bash -o pipefail unquoted": f"bash -o pipefail <<EOF\n{BODY}EOF\necho x > {T}",
    "c plain bash unquoted": f"bash <<EOF\n{BODY}EOF\necho x > {T}",
    "d a + python3 -c": f"bash -euo pipefail <<'EOF'\n{BODY}EOF\npython3 -c \"open('{T}','w').write('x')\"",
    "ctl-no-apostrophe": f"bash -euo pipefail <<'EOF'\n# do not overwrite\necho hi\nEOF\necho x > {T}",
    "e body writes, apostrophe": f"bash -euo pipefail <<'EOF'\n# don't\necho x > {T}\nEOF",
    "f pipefail body writes": f"bash -euo pipefail <<'EOF'\necho x > {T}\nEOF",
    "g harmless, apostrophe comment": "bash -euo pipefail <<'EOF'\n# don't overwrite\necho hi\nEOF",
    "h harmless, no comment": "bash -euo pipefail <<'EOF'\necho hi\nEOF",
    "i harmless plain bash, apostrophe": "bash <<'EOF'\n# it's fine\nls\nEOF",
}
for name, cmd in CASES.items():
    try:
        d, why = decide("Bash", {"command": cmd}, root, "engineer", "DAEO-03ub", cwd=root, flag="open")
    except Exception as e:
        d, why = "error", repr(e)[:120]
    print(f"{name}|{d}|{why[:90]}")
