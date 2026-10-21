"""What does a second rulesync generation do to a settings file that already exists? Stand-in values only, in a
temporary folder; prints counts and key names."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
sys.path.insert(0, str(ROOT / "src"))
from gov.adapters import portability  # noqa: E402

REL = ".claude/" + "settings" + ".json"


def generate(folder):
    done = subprocess.run([portability._find_rulesync(), *portability.GENERATE, str(ROOT / ".rulesync")],
                          cwd=folder, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    return done.returncode


def shape(doc):
    perms = doc.get("permissions") or {}
    return {"keys": sorted(doc), "hook_events": sorted(doc.get("hooks") or {}),
            "perm_counts": {k: len(v) for k, v in perms.items() if isinstance(v, list)},
            "env_keys": sorted(doc.get("env") or {})}


with tempfile.TemporaryDirectory() as fresh:
    print("first generate exit", generate(fresh))
    path = Path(fresh) / REL
    first = path.read_bytes()
    doc = json.loads(first)
    print("first:", shape(doc))
    doc.setdefault("env", {})["STAND_IN_ENV"] = "1"
    doc.setdefault("permissions", {}).setdefault("deny", []).insert(0, "Read(/stand-in-a/**)")
    doc["permissions"]["deny"].append("Edit(/stand-in-b/**)")
    doc.setdefault("hooks", {})["Stop"] = [{"hooks": [{"type": "command", "command": "true"}]}]
    doc["standInKey"] = True
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print("planted:", shape(doc))
    print("second generate exit", generate(fresh))
    second = path.read_bytes()
    after = json.loads(second)
    print("second:", shape(after))
    deny = (after.get("permissions") or {}).get("deny") or []
    print("stand-in Read rule kept:", "Read(/stand-in-a/**)" in deny, "at index",
          deny.index("Read(/stand-in-a/**)") if "Read(/stand-in-a/**)" in deny else None, "of", len(deny))
    print("stand-in Edit rule kept:", "Edit(/stand-in-b/**)" in deny)
    print("Stop kept:", "Stop" in (after.get("hooks") or {}), "| standInKey kept:", "standInKey" in after,
          "| env kept:", "STAND_IN_ENV" in (after.get("env") or {}))
    print("second equals first, byte for byte:", second == first)
