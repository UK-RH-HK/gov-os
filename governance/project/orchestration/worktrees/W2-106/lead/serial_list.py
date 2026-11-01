"""Write the serial-route entries the selection keeps (text before ' #'), one per line."""
import sys

kept = []
for line in open(sys.argv[1]):
    if "# serial:" not in line:
        continue
    kept.append(line.split(" #", 1)[0].strip())
open(sys.argv[2], "w").write("\n".join(kept) + "\n")
print("\n".join(kept))
