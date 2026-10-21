"""DEC-631: generate the adapter output into a temporary folder, as the adapter-portability check does, and compare
the harness settings before (this repository's) and after (generated). Prints names of keys and counts only: no
permission rule, no hook command and no env value is ever printed."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
sys.path.insert(0, str(ROOT / "src"))
from gov.adapters import portability  # noqa: E402

SETTINGS = ".claude/" + "settings" + ".json"


def hook_rows(doc):
    rows = {}
    for event, groups in (doc.get("hooks") or {}).items():
        entries = [hook for group in groups for hook in (group.get("hooks") or [])]
        guard = [hook for hook in entries if "guard" in str(hook.get("command", ""))]
        rows[event] = {"groups": len(groups), "entries": len(entries), "guard_entries": len(guard),
                       "guard_with_timeout_60": sum(1 for hook in guard if hook.get("timeout") == 60),
                       "timeouts": sorted({str(hook.get("timeout")) for hook in entries})}
    return rows


def shape(doc):
    perms = doc.get("permissions") or {}
    deny = perms.get("deny") or []
    return {"top_level_keys": sorted(doc),
            "hooks": hook_rows(doc),
            "permission_keys": sorted(perms),
            "permission_counts": {key: len(value) for key, value in perms.items() if isinstance(value, list)},
            "held_out_read_deny_rules": sum(1 for rule in deny if rule.startswith("Read(") and "held-out" in rule),
            "deny_rules_by_tool": {tool: sum(1 for rule in deny if rule.split("(")[0] == tool)
                                   for tool in sorted({rule.split("(")[0] for rule in deny})},
            "deny_rules_naming_held_out_any_form": sum(1 for rule in deny if "held" in rule.lower()),
            "deny_rules_naming_the_oracle": sum(1 for rule in deny if "oracle" in rule.lower()),
            "deny_rules_naming_env_or_secret": sum(1 for rule in deny if ".env" in rule or "secret" in rule.lower()),
            "hook_entry_kinds": sorted({str(hook.get("type")) for groups in (doc.get("hooks") or {}).values()
                                        for group in groups for hook in (group.get("hooks") or [])}),
            "hook_matchers": {event: sorted(str(group.get("matcher")) for group in groups)
                              for event, groups in (doc.get("hooks") or {}).items()},
            "env_keys": sorted((doc.get("env") or {})),
            "env_has_auto_compact_window": "CLAUDE_CODE_AUTO_COMPACT_WINDOW" in (doc.get("env") or {}),
            "stop_events_present": [event for event in ("Stop", "SubagentStop") if event in (doc.get("hooks") or {})]}


with tempfile.TemporaryDirectory() as fresh:
    done = subprocess.run([portability._find_rulesync(), *portability.GENERATE, str(ROOT / ".rulesync")],
                          cwd=fresh, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    print("rulesync exit", done.returncode)
    # DEC-635: the held-out step after generation, as the apply procedure and the adapter check make it.
    from gov.guard import heldout  # noqa: E402
    try:
        print("held-out step: rules written", heldout.write_read_rules(str(ROOT), str(Path(fresh) / heldout.SETTINGS_REL)))
    except Exception as exc:  # the type only: its text may quote the held-out file
        print("held-out step FAILED:", type(exc).__name__)
    made = {str(path.relative_to(fresh)): path.read_bytes() for path in sorted(Path(fresh).rglob("*")) if path.is_file()}
print("files generated:", len(made))
before = json.loads((ROOT / SETTINGS).read_text(encoding="utf-8"))
after = json.loads(made[SETTINGS].decode("utf-8"))
b, a = shape(before), shape(after)
for key in b:
    mark = "same" if b[key] == a[key] else "DIFFERS"
    print(f"\n== {key}: {mark}")
    if key == "hooks":
        for event in sorted(set(b[key]) | set(a[key])):
            print(f"   {event}: before {b[key].get(event)} | after {a[key].get(event)}")
    else:
        print("   before:", b[key])
        print("   after: ", a[key])
for name in ("allow", "deny", "ask"):
    old, new = set((before.get("permissions") or {}).get(name) or []), set((after.get("permissions") or {}).get(name) or [])
    print(f"\n== permissions.{name}: only before {len(old - new)}, only after {len(new - old)}, in both {len(old & new)}")
for key in sorted(set(before) | set(after)):
    if key not in ("hooks", "permissions", "env"):
        print(f"\n== other key {key}: before {'present' if key in before else 'absent'}, after "
              f"{'present' if key in after else 'absent'}, equal {before.get(key) == after.get(key)}")
print("\n== other generated files that differ from the repository's (name, bytes before -> after):")
for rel, content in made.items():
    if rel == SETTINGS:
        continue
    path = ROOT / rel
    if not path.is_file():
        print("   NEW", rel, len(content))
    elif path.read_bytes() != content:
        print("   ", rel, path.stat().st_size, "->", len(content))
