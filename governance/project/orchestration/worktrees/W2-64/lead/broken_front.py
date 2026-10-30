"""Lead's scratch: files under .tickets/ and docs/ that open with '---' but whose frontmatter is not a mapping."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]) / "src"))
from gov.check import schema as S  # noqa: E402

root = Path(sys.argv[1])
count = 0
for record_dir in S.RECORD_PATHS:
    for md in sorted((root / record_dir).rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        if text.split("\n", 1)[0].strip() == "---" and S._frontmatter(text) is None:
            print(md.relative_to(root))
            count += 1
print("#", count)
