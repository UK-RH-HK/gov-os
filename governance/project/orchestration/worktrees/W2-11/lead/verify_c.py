"""Step 4 (resume run 2): rebuild, collection check, the scoped parallel run in the close's form, the serial-only
cases in scope, gov check (with the node PATH), the validator, the trailer gate. Every result to the lead's log
folder with an exit file. No load wait (DEC-979 D1: verify_lock.sh takes the heavy-job slot)."""
import json
import os
import re
import subprocess
import time

WT = "/home/usain/gov-os-worktrees/W2-11"
LOG = WT + "/.gov-runtime/scratch/lead/log"
TOOLS = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools"
NODE = "/home/usain/.nvm/versions/node/v22.23.3/bin"


def run(name, cmd, env_extra):
    env = dict(os.environ)
    env.update(env_extra)
    with open(f"{LOG}/{name}.txt", "w") as out:
        code = subprocess.call(cmd, cwd=WT, env=env, stdout=out, stderr=subprocess.STDOUT)
    with open(f"{LOG}/{name}.exit", "w") as f:
        f.write(f"{code}\n")
    return code


def stamp(label):
    with open(f"{LOG}/vc-stamps.txt", "a") as f:
        f.write(label + " " + time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n")


base_env = {"TMPDIR": "/tmp/gov-os-lead-W2-11", "PYTHONPATH": WT + "/src"}
node_env = dict(base_env, PATH=NODE + ":" + os.environ.get("PATH", ""))

stamp("start")
subprocess.call(["bash", TOOLS + "/disk_gate.sh"], stdout=open(f"{LOG}/vc-disk.txt", "w"), stderr=subprocess.STDOUT)
run("rebuild-3", ["flock", "/tmp/gov-os-rebuild.lock", "python3", "-m", "gov.cli.main", "rebuild", "--json"],
    base_env)
stamp("rebuilt")
run("govfile", ["python3", "-c", "import gov; print(gov.__file__)"], base_env)
run("select-2", ["python3", TOOLS + "/select_tests.py", WT, "W2-11", "DAEO-k7hz"], base_env)
text = open(f"{LOG}/select-2.txt").read()
sel = json.loads(text[text.index("{"):])
# Row W2-L423's rule (DEC-911): no 40-digit commit ids under .gov-runtime/.
with open(f"{LOG}/select-2.txt", "w") as f:
    f.write(re.sub(r"\b([0-9a-f]{12})[0-9a-f]{28}\b", r"\1", text))
opts = sel["pytest_options"]

run("collect-2", ["python3", "-m", "pytest", "tests", "--collect-only", "-q", "-p", "no:cacheprovider",
                  "--no-header"], base_env)
stamp("collected")

close_env = dict(node_env)
close_env.update({
    "PYTHONPATH": WT + "/src:" + WT + "/src/gov/close/pytest_plugin",
    "GOV_CLOSE_SERIAL_ONLY_OF": WT,
})
subprocess.call(["bash", TOOLS + "/disk_gate.sh"], stdout=open(f"{LOG}/vc-disk2.txt", "w"), stderr=subprocess.STDOUT)
run("parallel-2", ["bash", TOOLS + "/verify_lock.sh", "python3", "-m", "pytest", "tests", "-n", "auto", "-q",
                   "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed",
                   "-rs", f"--junitxml={LOG}/parallel-2.xml", *opts], close_env)
stamp("parallel")

# The serial-only cases the selection keeps: the list's entries not ignored or deselected by pytest_options.
entries = [line.split(" #")[0].strip() for line in open(WT + "/tests/acceptance/serial-only.txt")
           if line.strip() and not line.startswith("#")]
entries = [e for e in entries if e]
ignored = [opts[i + 1] for i, o in enumerate(opts) if o == "--ignore" and i + 1 < len(opts)]
ignored += [o.split("=", 1)[1] for o in opts if o.startswith("--ignore=")]
deselected = [opts[i + 1] for i, o in enumerate(opts) if o == "--deselect" and i + 1 < len(opts)]
deselected += [o.split("=", 1)[1] for o in opts if o.startswith("--deselect=")]


def kept(entry):
    path = WT + "/" + entry.split("::")[0]
    if any(path == i.rstrip("/") or path.startswith(i.rstrip("/") + "/") for i in ignored):
        return False
    return entry not in deselected and WT + "/" + entry not in deselected


serial = [e for e in entries if kept(e)]
with open(f"{LOG}/serial-2-entries.txt", "w") as f:
    f.write("\n".join(serial) + "\n")
if serial:
    serial_env = dict(close_env, GOV_CLOSE_SERIAL_ONLY_GIVEN="\n".join(serial))
    run("serial-2", ["bash", TOOLS + "/verify_lock.sh", "python3", "-m", "pytest", *serial, "-q",
                     "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed",
                     "-rs", f"--junitxml={LOG}/serial-2.xml"], serial_env)
stamp("serial")

run("govcheck-2", ["python3", "-m", "gov.cli.main", "check", "--json"], node_env)
stamp("govcheck")
skills = ["audit", "change", "checkpoint", "discovery", "orchestration", "planning", "qa-review", "retrieval",
          "test-design"]
run("validator-2", ["python3", "-m", "gov.check.skill_validator", "--both-layouts",
                    *[f"template/governance/kernel/skills/{s}" for s in skills]], base_env)
run("trailers-2", ["python3", TOOLS + "/trailer_gate.py", "DAEO-k7hz", WT], base_env)
run("keywords-2", ["python3", TOOLS + "/keyword_warn.py", WT], base_env)
stamp("done")
with open(f"{LOG}/vc.done", "w") as f:
    f.write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n")
