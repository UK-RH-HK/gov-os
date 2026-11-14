import sys
root = sys.argv[1]
sys.path.insert(0, root + "/src")
from gov.guard.decide import decide
T = "tests/acceptance/X/zz.py"
for c in [f"bash <<'EOF'\n# don't overwrite\necho x > {T}\n# it's done\nEOF",
          f"echo x > {T} # don't\n# it's",
          f"cat <<'EOF' > /dev/null\nit's\nEOF\necho x > {T}\necho \"it's\""]:
    print(repr(c), decide("Bash", {"command": c}, root, "engineer", "DAEO-03ub", cwd=root, flag="open"))
