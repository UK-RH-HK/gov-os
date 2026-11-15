"""A child process for S24 (``test_w2_88_p1_installed.py``): import ``gov.adopt.fabric``, ``gov.adopt.memory_sets`` and ``gov.adopt.safety`` with an
audit hook that notes every file the interpreter opens, and print as one JSON line which imports failed and which opened files are ones
Gov OS ships (the pool, the walls template, the audit briefs, a skill, a template, the secrets configuration).

    python import_child.py

Importing from an installed wheel with no source tree reads no shipped file and does not fail (S24, the interface's item 2).
"""

import importlib
import json
import sys

opened = []


def hook(event, args):
    if event == "open" and args and isinstance(args[0], (str, bytes)):
        opened.append(args[0] if isinstance(args[0], str) else args[0].decode("utf-8", "replace"))


sys.addaudithook(hook)
failed = {}
for name in ("gov.adopt.fabric", "gov.adopt.memory_sets", "gov.adopt.safety"):
    try:
        importlib.import_module(name)
    except BaseException as exc:  # noqa: BLE001
        failed[name] = f"{type(exc).__name__}: {exc}"
markers = ("retrieval.yaml", "indep-walls", "MEMORY-AUDIT-1", ".gitleaks.toml", "SKILL.md", "brief.md", "role-cto.md")
print(json.dumps({"failed": failed, "opened": [p for p in opened if any(m in p for m in markers)]}))
