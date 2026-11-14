import json
from pathlib import Path

d = Path("/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/briefs")
reading = (d / "interface-reading.md").read_text()
# drop the reading's own level-2 title: the brief has its own
body = reading.split("\n", 2)[2]
for name, ctx in (("td-1.md", "ctx-independent-test-designer.md"), ("ps-1.md", "ctx-product-spec.md")):
    p = d / name
    text = p.read_text()
    assert text.count("INTERFACE_READING") == 1, name
    text = text.replace("INTERFACE_READING\n", body)
    h = json.loads((d / ctx).read_text())["hash"][:12]
    text = text.replace("Bundle hash `2d2c77d0b287`", "Bundle hash `%s`" % h)
    p.write_text(text)
    print(name, h, len(text.splitlines()))
