"""The hooks of ``.claude/settings.json`` after ``gov update`` regenerates them (W2-17 fix F4, EXAMIN report 28).

The update's unmerge takes out the entries equal to release A's generation and the regeneration then merges release B's
beside what is left, so a project whose settings held a kernel hook in another form (an older generation's command text,
or the same entry twice) came out of the update with the hook registered twice. After the regeneration every kernel hook
program (a command that runs ``governance/kernel/hooks/<name>.py``) is registered once per event and matcher, whatever
its command text: the last entry stays, which is release B's generated one (the generation merges after the project's).
The project's own hooks, those that run no kernel hook program, are never touched, nor their order.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

# the kernel hook programs, and the kit's helper-model hook (MR-4), the one hook program the kit holds under .claude/hooks
KERNEL_HOOK = re.compile(r"(?:governance/kernel|\.claude)/hooks/(\w+)\.py")


def _program(hook) -> str | None:
    command = hook.get("command") if isinstance(hook, dict) else None
    found = KERNEL_HOOK.search(command) if isinstance(command, str) else None
    return found.group(1) if found else None


def dedupe(settings) -> dict | None:
    """``settings`` with each kernel hook program once per event and matcher (the last entry stays; a group left with
    no hook by it is dropped); ``None`` where nothing is registered twice. ``settings`` itself is not changed."""
    hooks = settings.get("hooks") if isinstance(settings, dict) else None
    if not isinstance(hooks, dict):
        return None
    result, changed = copy.deepcopy(settings), False
    for event, groups in result["hooks"].items():
        if not isinstance(groups, list):
            continue
        seen, kept = set(), []
        for group in reversed(groups):
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                kept.append(group)
                continue
            matcher = group.get("matcher")
            matcher = matcher if isinstance(matcher, str) else None
            entries = []
            for hook in reversed(group["hooks"]):
                program = _program(hook)
                if program is not None:
                    if (matcher, program) in seen:
                        continue
                    seen.add((matcher, program))
                entries.append(hook)
            entries.reverse()
            if len(entries) != len(group["hooks"]):
                changed = True
                if not entries:
                    continue
                group["hooks"] = entries
            kept.append(group)
        kept.reverse()
        result["hooks"][event] = kept
    return result if changed else None


def dedupe_settings(project: Path, journal) -> bool:
    """``.claude/settings.json`` written through ``journal`` with each kernel hook once; nothing is written where the file
    is absent, is not a JSON object or registers none twice. True where it wrote."""
    path = Path(project) / ".claude" / "settings.json"
    if not path.is_file() or path.is_symlink():
        return False
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        return False
    deduped = dedupe(value)
    if deduped is None:
        return False
    journal.write(".claude/settings.json", (json.dumps(deduped, indent=2, ensure_ascii=False) + "\n").encode())
    return True
