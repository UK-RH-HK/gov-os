"""One switch measurement for W2-60a's CIT-E: the CLI started directly, with the settings the pinned
`gov launch` builds for an engineer in the probe repository, plus the candidate switches named.

Run with the pin's interpreter (-E). The process environment is the caller's less GOV_ROLE, GOV_TICKET,
PYTHONPATH and every name beginning CLAUDE (as W1-46's live tests), plus the settings' env, as the
launcher passes it. The difference from `gov launch`: the CLI is started here, not by the launcher, so
that switches the pinned launcher refuses after `--` can be tried. The session's temp folder is made
under the lead's temp folder and removed at the end.

Usage: python -E run_switch.py <name> <settings-extra-json> <env-extra-json> [<cli switch> ...]
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from gov.launch.launcher import build_settings

PROJECT = Path("/tmp/gov-os-lead-W2-60a/rules-probe")
LOGS = Path("/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log")
CLI = str(Path.home() / ".local/bin/claude")
PROMPT = "Answer with the single word READY and do nothing else."


def main(name, settings_extra, env_extra, switches):
    settings = build_settings(PROJECT, "engineer", "DAEO-zp60")
    tmp = tempfile.mkdtemp(prefix="gov-launch-engineer-", dir="/tmp/gov-os-lead-W2-60a")
    settings["env"].update({"TMPDIR": tmp, "CLAUDE_CODE_TMPDIR": tmp})
    settings["sandbox"]["filesystem"] = {"allowWrite": [f"/{tmp}"]}
    settings.update(json.loads(settings_extra))
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("CLAUDE") and k not in ("GOV_ROLE", "GOV_TICKET", "PYTHONPATH")}
    env.update(settings["env"])
    env.update(json.loads(env_extra))
    prompt = PROMPT
    if os.environ.get("PROBE_PROMPT_FILE"):
        prompt = Path(os.environ["PROBE_PROMPT_FILE"]).read_text(encoding="utf-8").strip()
    command = [CLI, "--settings", json.dumps(settings), *switches, "-p", prompt,
               "--model", "claude-opus-5-5", "--effort", "low", "--output-format", "stream-json", "--verbose",
               "--max-turns", "2"]
    log = LOGS / f"switch-{name}.jsonl"
    started = time.time()
    try:
        with open(log, "w", encoding="utf-8") as out:
            code = subprocess.run(command, cwd=PROJECT, env=env, stdout=out, stderr=subprocess.STDOUT,
                                  stdin=subprocess.DEVNULL, timeout=600).returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"{name}: exit {code}, {time.time() - started:.0f} s; switches {switches}; settings+ {settings_extra}; "
          f"env+ {env_extra}")
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.startswith("{"):
            print("  raw:", line[:200])
            continue
        event = json.loads(line)
        if event.get("type") == "system" and event.get("subtype") == "init":
            print("  session", event.get("session_id"))
            print("  mcp_servers", [(s.get("name"), s.get("status"), s.get("source")) for s in event.get("mcp_servers", [])])
            print("  agents", event.get("agents"))
            print("  skills", event.get("skills"))
            print("  plugins", [p.get("name") for p in event.get("plugins", [])])
            print("  memory_paths", event.get("memory_paths"))
            print("  mcp tools", len([t for t in event.get("tools", []) if t.startswith("mcp__")]))
        if event.get("type") == "result":
            print("  result", repr(event.get("result")), "cost", event.get("total_cost_usd"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
