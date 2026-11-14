"""What W2-185's conftest and its cases share: the README's map, a reader of the hooks sources, stand-in roots.

The cases read files and call portability's hooks comparison over stand-in roots built in ``tmp_path``
(``template/governance/kernel/`` as a folder, ``template/.rulesync/hooks.jsonc`` and ``.rulesync/hooks.jsonc``);
nothing is written in the repository, nothing needs the network.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
README = HERE / "README.md"
ROOT = HERE.parents[2]
NODE_ID = re.compile(r"`(tests/(?:acceptance|unit)/[^`\s]+\.py::[^`\s]+)`")
OWN_PREFIX = "tests/acceptance/W2-185/"

KERNEL_HOOKS = ROOT / "template" / "governance" / "kernel" / "hooks"
TEMPLATE_HOOKS = ROOT / "template" / ".rulesync" / "hooks.jsonc"
ROOT_HOOKS = ROOT / ".rulesync" / "hooks.jsonc"
W1_38 = ROOT / "tests" / "acceptance" / "W1-38"

HOOKS_CODES = {"HOOKS_EVENT_DIFFERS", "HOOKS_MATCHER_DIFFERS", "HOOKS_UNREADABLE"}


def mapped_node_ids() -> list[str]:
    """Every node id of the README's tables, each once, in the order the README gives them."""
    ids = []
    for line in README.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("|"):
            ids += NODE_ID.findall(line)
    return list(dict.fromkeys(ids))


def own_node_ids() -> list[str]:
    return [node for node in mapped_node_ids() if node.startswith(OWN_PREFIX)]


def external_node_ids() -> list[str]:
    return [node for node in mapped_node_ids() if not node.startswith(OWN_PREFIX)]


# ---------------------------------------------------------------------------
# A hooks source (JSON with comments and trailing commas), read by this folder's own small reader
# ---------------------------------------------------------------------------

def read_jsonc(text: str) -> dict:
    out, i, quoted = [], 0, False
    while i < len(text):
        char = text[i]
        if quoted:
            out.append(char)
            if char == "\\":
                out.append(text[i + 1:i + 2])
                i += 1
            elif char == '"':
                quoted = False
        elif text.startswith("//", i):
            i = text.find("\n", i)
            i = len(text) if i < 0 else i
            continue
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = len(text) if end < 0 else end + 2
            continue
        elif char == ",":
            if not text[i + 1:].lstrip().startswith(("}", "]")):
                out.append(char)
        else:
            quoted = char == '"'
            out.append(char)
        i += 1
    return json.loads("".join(out))


def read_source(path: Path) -> dict:
    return read_jsonc(path.read_text(encoding="utf-8"))


def entries(source: dict, event: str) -> list[dict]:
    return list(source.get("hooks", {}).get(event, []))


def commands(source: dict) -> list[str]:
    return [entry["command"] for event_entries in source.get("hooks", {}).values() for entry in event_entries]


def names_script(command: str, script: str) -> bool:
    """Whether a hook command runs ``script`` from a hooks folder (``stop.py`` is not ``subagentstop.py``)."""
    return re.search(r"/" + re.escape(script) + r"(?![\w.])", command) is not None


# ---------------------------------------------------------------------------
# Stand-in hook entries and roots
# ---------------------------------------------------------------------------

def entry(script: str, matcher: str | None = None, timeout: int = 60, adopted: bool = True) -> dict:
    """A hook entry in the form of the repository's sources: the command runs ``script`` of the kernel's hooks folder
    (the adopted project's path ``governance/kernel/hooks/``, or the repository's ``template/governance/kernel/hooks/``)."""
    folder = "governance/kernel/hooks" if adopted else "template/governance/kernel/hooks"
    found = {"type": "command", **({"matcher": matcher} if matcher else {}),
             "command": f'g="$HOME/.local/bin/gov"; exec "$p" -E "$CLAUDE_PROJECT_DIR/{folder}/{script}"',
             "timeout": timeout}
    return found


def adopted_context_watch() -> dict:
    """The entry S1 asks of the template: the root's ``context_watch.py`` entry with the adopted path."""
    found = [e for e in entries(read_source(ROOT_HOOKS), "postToolUse") if names_script(e["command"], "context_watch.py")]
    assert len(found) == 1, f"the root's hooks source has {len(found)} postToolUse entries for context_watch.py; one is expected"
    return {**found[0], "command": found[0]["command"].replace("template/governance/kernel/hooks/",
                                                               "governance/kernel/hooks/")}


def plant_root(tmp_path: Path, template_hooks: dict, root_hooks: dict) -> Path:
    """A stand-in repository: the template's kernel folder, the template's hooks source and the root's."""
    (tmp_path / "template" / "governance" / "kernel").mkdir(parents=True)
    for rel, hooks in (("template/.rulesync/hooks.jsonc", template_hooks), (".rulesync/hooks.jsonc", root_hooks)):
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"version": 1, "hooks": hooks}, indent=2) + "\n", encoding="utf-8")
    return tmp_path


def hooks_findings(root: Path) -> list[dict]:
    """portability's hooks comparison over ``root`` (the repository's own code, ``PYTHONPATH=<tree>/src``)."""
    src = str(ROOT / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    from gov.adapters import portability
    return portability._hooks_findings(root)


def names_event(finding: dict, event: str) -> bool:
    """Whether a finding's message names exactly this event (``postToolUse`` is not ``postToolUseFailure``)."""
    return re.search(rf"\b{re.escape(event)}\b", str(finding.get("message", ""))) is not None


def describe(findings: list[dict]) -> str:
    return json.dumps(findings, indent=1)
