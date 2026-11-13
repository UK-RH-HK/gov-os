"""What W2-182's conftest and its guard case share: the README's map of node ids."""
import re
from pathlib import Path

README = Path(__file__).with_name("README.md")
ROOT = Path(__file__).resolve().parents[3]
NODE_ID = re.compile(r"`(tests/acceptance/[^`\s]+\.py::[^`\s]+)`")


def mapped_node_ids() -> list[str]:
    """The node ids the README's table rows name, each once, in the order the README gives them."""
    ids = []
    for line in README.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("|"):
            ids += NODE_ID.findall(line)
    return list(dict.fromkeys(ids))
