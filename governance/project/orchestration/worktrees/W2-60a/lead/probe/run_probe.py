"""Start one rules-probe session through the pinned `gov launch` (W2-60a, KPI line 9).

The environment is the caller's less GOV_ROLE, GOV_TICKET and every name beginning CLAUDE, as
W1-46's live tests start theirs (DEC-784); TMPDIR is the lead's temp folder; no PYTHONPATH, so the
bare `gov` is the pinned judge. Usage: python3 run_probe.py <name> <prompt-file>
"""
import os
import subprocess
import sys
import time
from pathlib import Path

PROJECT = "/tmp/gov-os-lead-W2-60a/rules-probe"
LOGS = Path("/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log")


def main(name, prompt_file):
    prompt = Path(prompt_file).read_text(encoding="utf-8").strip()
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("CLAUDE") and k not in ("GOV_ROLE", "GOV_TICKET", "PYTHONPATH")}
    env["TMPDIR"] = "/tmp/gov-os-lead-W2-60a"
    command = ["gov", "launch", "engineer", "DAEO-zp60", "--", "-p", prompt,
               "--model", "claude-opus-5-5", "--effort", "low",
               "--output-format", "stream-json", "--verbose",
               "--permission-mode", "acceptEdits", "--max-turns", "8",
               "--allowedTools", "Read", "Edit", "Write", "Bash"]
    log = LOGS / f"probe-{name}.jsonl"
    started = time.time()
    with open(log, "w", encoding="utf-8") as out:
        code = subprocess.run(command, cwd=PROJECT, env=env, stdout=out, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL, timeout=900).returncode
    print(f"{name}: exit {code}, {time.time() - started:.0f} s, log {log}")
    print("command: cd " + PROJECT + " && " + " ".join(command[:-6]) + " ...")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
