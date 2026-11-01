"""Re-run each listed red alone, one pytest process each (a red that fails alone is a red; one that passes alone is
a flaky candidate). Writes one line per case to log/rerun-alone.txt."""
import os
import subprocess

TREE = "/home/usain/gov-os-worktrees/W2-104"
LOG = TREE + "/.gov-runtime/scratch/lead/log"
env = dict(os.environ)
env["PATH"] = "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env.get("PATH", "")
env["PYTHONPATH"] = TREE + "/src:" + TREE + "/src/gov/close/pytest_plugin"
env["TMPDIR"] = "/tmp/gov-os-lead-W2-104"
ids = [line.strip() for line in open(LOG + "/rerun-ids.txt") if line.strip()]
with open(LOG + "/rerun-alone.txt", "w") as out:
    for node in ids:
        done = subprocess.run(["python3", "-m", "pytest", node, "-q", "-p", "no:cacheprovider",
                               "-o", "tmp_path_retention_policy=failed", "--tb=line"],
                              cwd=TREE, env=env, capture_output=True, text=True)
        last = (done.stdout.strip().splitlines() or [""])[-1]
        out.write(f"{done.returncode} | {node} | {last}\n")
        out.flush()
