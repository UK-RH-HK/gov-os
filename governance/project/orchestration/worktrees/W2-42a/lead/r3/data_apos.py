import sys
root = sys.argv[1]
sys.path.insert(0, root + "/src")
from gov.guard.decide import decide
for c in ["cat > notes.md <<'EOF'\nit's done\nEOF", "echo hi # it's fine", "cat <<'EOF'\n# it's data\nEOF"]:
    print(repr(c[:30]), decide("Bash", {"command": c}, root, "engineer", "DAEO-03ub", cwd=root, flag="open")[0])
