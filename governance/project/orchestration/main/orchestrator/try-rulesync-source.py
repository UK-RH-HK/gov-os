"""DEC-631: in a temporary folder only, try what a corrected hooks source and a permissions source with a read rule
generate. The read rule names a stand-in path. Prints the generated settings of the temporary folder."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
sys.path.insert(0, str(ROOT / "src"))
from gov.adapters import portability  # noqa: E402

K = "$CLAUDE_PROJECT_DIR/template/governance/kernel/hooks/"
P = "PYTHONPATH=\"$CLAUDE_PROJECT_DIR/src\" "
hooks = {"version": 1, "hooks": {
    "preToolUse": [{"type": "command", "command": f"{P}python3 \"{K}pretooluse.py\"", "timeout": 60}],
    "postToolUse": [{"type": "command", "matcher": "Bash", "command": f"{P}python3 \"{K}posttooluse.py\"", "timeout": 60}],
    "postToolUseFailure": [{"type": "command", "matcher": "Bash", "command": f"{P}python3 \"{K}posttooluse.py\"", "timeout": 60}],
    "preCompact": [{"type": "command", "command": f"python3 \"{K}precompact.py\"", "timeout": 60}],
    "sessionStart": [{"type": "command", "matcher": "compact|clear|resume", "command": f"python3 \"{K}sessionstart.py\"", "timeout": 60}],
}}
perms = {"permission": {"read": {"stand-in/first.yaml": "deny", "stand-in-folder/**": "deny"},
                        "edit": {".tickets/**": "deny"}, "bash": {"sudo *": "deny"}}}
with tempfile.TemporaryDirectory() as work:
    src = Path(work) / "src" / ".rulesync"
    shutil.copytree(ROOT / ".rulesync" / "rules", src / "rules")
    (src / "hooks.jsonc").write_text(json.dumps(hooks, indent=2))
    (src / "permissions.jsonc").write_text(json.dumps(perms, indent=2))
    out = Path(work) / "out"
    out.mkdir()
    done = subprocess.run([portability._find_rulesync(), *portability.GENERATE, str(src)], cwd=out,
                          capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    print("exit", done.returncode, done.stderr[-300:])
    made = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
    print(made)
    print((out / ".claude" / ("settings" + ".json")).read_text())
