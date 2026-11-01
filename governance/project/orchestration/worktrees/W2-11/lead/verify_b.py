"""Step 4, stage B: collection check, the scoped parallel run in the close's form, gov check, the validator, the
trailer gate. Every result to the lead's log folder with an exit file. Run from any folder."""
import json
import os
import subprocess
import time

WT = "/home/usain/gov-os-worktrees/W2-11"
LOG = WT + "/.gov-runtime/scratch/lead/log"
TOOLS = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools"


def wait_load():
    while True:
        one, _five, fifteen = os.getloadavg()
        if min(one, fifteen) < os.cpu_count():
            return
        time.sleep(60)


def run(name, cmd, env_extra):
    env = dict(os.environ)
    env.update(env_extra)
    with open(f"{LOG}/{name}.txt", "w") as out:
        code = subprocess.call(cmd, cwd=WT, env=env, stdout=out, stderr=subprocess.STDOUT)
    with open(f"{LOG}/{name}.exit", "w") as f:
        f.write(f"{code}\n")
    return code


base_env = {"TMPDIR": "/tmp/gov-os-lead-W2-11", "PYTHONPATH": WT + "/src"}
sel = json.load(open(f"{LOG}/select.json"))
opts = sel["pytest_options"]

wait_load()
subprocess.call(["bash", TOOLS + "/disk_gate.sh"], stdout=open(f"{LOG}/vb-disk.txt", "w"), stderr=subprocess.STDOUT)

# DEC-868: the collection check, in one process, as the close runs it.
run("collect", ["python3", "-m", "pytest", "tests", "--collect-only", "-q", "-p", "no:cacheprovider", "--no-header"],
    base_env)

# The scoped parallel run, in the close's form (DEC-889, DEC-952, DEC-905).
par_env = dict(base_env)
par_env.update({
    "PATH": "/home/usain/.nvm/versions/node/v22.23.3/bin:" + os.environ.get("PATH", ""),
    "PYTHONPATH": WT + "/src:" + WT + "/src/gov/close/pytest_plugin",
    "GOV_CLOSE_SERIAL_ONLY_OF": WT,
})
wait_load()
run("parallel", ["bash", TOOLS + "/verify_lock.sh", "python3", "-m", "pytest", "tests", "-n", "auto", "-q",
                 "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed",
                 "-rs", f"--junitxml={LOG}/parallel.xml", *opts], par_env)

# Governance checks on this worktree's code, after the rebuild.
run("govcheck", ["python3", "-m", "gov.cli.main", "check", "--json"], base_env)

# The skill validator on every kernel skill this round touched, and the skill template.
skills = ["audit", "change", "checkpoint", "discovery", "orchestration", "planning", "qa-review", "retrieval",
          "test-design"]
run("validator", ["python3", "-m", "gov.check.skill_validator", "--both-layouts",
                  *[f"template/governance/kernel/skills/{s}" for s in skills]], base_env)

run("trailers", ["python3", TOOLS + "/trailer_gate.py", "DAEO-k7hz", WT], base_env)
with open(f"{LOG}/vb.done", "w") as f:
    f.write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n")
