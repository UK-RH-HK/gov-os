"""Cut 40-hex commit ids to 12 digits in the lead's own Markdown records under scratch (DEC-911)."""
import re
import sys

for path in sys.argv[1:]:
    text = open(path, encoding="utf-8").read()
    new, count = re.subn(r"\b([0-9a-f]{12})[0-9a-f]{28}\b", r"\1", text)
    open(path, "w", encoding="utf-8").write(new)
    print(path.rsplit("/", 1)[-1], count)
