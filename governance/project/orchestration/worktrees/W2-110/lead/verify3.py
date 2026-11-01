"""The lead's verification for W2-110 (step 4), each step with its own log and exit file under log/verify/.

Steps: capacity wait and disk gate; full rebuild (flock); gov.__file__; the scoped parallel run in the close's form
with select_tests.py's pytest_options; the selected serial-only cases alone; W1-38 and W1-39 (the template's suites,
run once even though the selection leaves them out); gov check --json; the collect-only run (DEC-868).
Usage: python3 verify.py <select json> [steps...]
"""
import json
import os
import subprocess
import sys
import time

WT = "/home/usain/gov-os-worktrees/W2-110"
LOG = WT + "/.gov-runtime/scratch/lead/log/verify-3"
TOOLS = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools"
os.makedirs(LOG, exist_ok=True)

sel = json.load(open(sys.argv[1]))
steps = sys.argv[2:] or ["rebuild", "import", "parallel", "serial", "template", "check", "collect"]
opts = sel["pytest_options"]

base_env = dict(os.environ)
base_env["TMPDIR"] = "/tmp/gov-os-lead-W2-110"
base_env["PYTHONPATH"] = WT + "/src"
close_env = dict(base_env)
close_env["PATH"] = "/home/usain/.nvm/versions/node/v22.23.3/bin:" + base_env["PATH"]
close_env["PYTHONPATH"] = WT + "/src:" + WT + "/src/gov/close/pytest_plugin"
close_env["GOV_CLOSE_SERIAL_ONLY_OF"] = WT


def wait_capacity():
    while True:
        l = os.getloadavg()
        if min(l[0], l[2]) < os.cpu_count():
            return
        time.sleep(60)


def run(name, argv, env):
    wait_capacity()
    gate = subprocess.run(["bash", TOOLS + "/disk_gate.sh"], capture_output=True, text=True)
    with open(f"{LOG}/{name}.log", "w") as out:
        out.write(f"# {time.strftime('%FT%TZ', time.gmtime())} disk gate: {gate.stdout.strip()}\n")
        out.write("# " + " ".join(argv[:12]) + (" ..." if len(argv) > 12 else "") + "\n")
        out.flush()
        if gate.returncode != 0:
            code = 97
        else:
            code = subprocess.run(argv, cwd=WT, env=env, stdout=out, stderr=subprocess.STDOUT).returncode
        out.write(f"# {time.strftime('%FT%TZ', time.gmtime())} exit {code}\n")
    with open(f"{LOG}/{name}.exit", "w") as f:
        f.write(f"{code}\n")
    return code


def selected_serial():
    """Serial-only entries tagged 'serial:' that fall in the selection and are not ignored."""
    targets = [s["target"].rstrip("/") for s in sel["selected"]]
    ignores = [o.split("=", 1)[1].replace(WT + "/", "").rstrip("/") for o in opts if o.startswith("--ignore=")]
    keep = []
    for line in open(WT + "/tests/acceptance/serial-only.txt"):
        entry, _, comment = line.partition("#")
        entry = entry.strip()
        if not entry or not comment.strip().startswith("serial:"):
            continue
        path = entry.split("::")[0]
        inside = any(entry == t or path == t.split("::")[0] and "::" not in t or path.startswith(t + "/")
                     or entry.startswith(t + "::") for t in targets)
        ignored = any(path == i or path.startswith(i + "/") for i in ignores)
        if inside and not ignored:
            keep.append(entry)
    return keep


for step in steps:
    if step == "rebuild":
        run("rebuild", ["flock", "/tmp/gov-os-rebuild.lock", sys.executable, "-m", "gov.cli.main", "rebuild",
                        "--json"], base_env)
    elif step == "import":
        run("import", [sys.executable, "-c", "import gov; print(gov.__file__)"], base_env)
    elif step == "parallel":
        run("parallel", [sys.executable, "-m", "pytest", "tests", "-n", "auto", "-q", "-p", "no:cacheprovider",
                         "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed", "-rs",
                         f"--junitxml={LOG}/parallel.xml"] + opts, close_env)
    elif step == "serial":
        cases = selected_serial()
        with open(f"{LOG}/serial-cases.txt", "w") as f:
            f.write("\n".join(cases) + "\n")
        if not cases:
            with open(f"{LOG}/serial.exit", "w") as f:
                f.write("none-selected\n")
            continue
        env = dict(close_env)
        env["GOV_CLOSE_SERIAL_ONLY_GIVEN"] = "\n".join(cases)
        run("serial", [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p",
                       "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed", "-rs",
                       f"--junitxml={LOG}/serial.xml"] + cases, env)
    elif step == "guard":
        suites = ["tests/acceptance/" + s for s in ("W1-04", "W1-47", "W1-50", "W1-03", "W1-05", "W1-46", "W2-110")]
        run("guard", [sys.executable, "-m", "pytest"] + suites + ["tests/unit/install", "tests/unit/guard", "-n",
                      "auto", "-q", "-p", "no:cacheprovider", "-o",
                      "tmp_path_retention_policy=failed", "-rs", f"--junitxml={LOG}/guard.xml"], close_env)
    elif step == "template":
        run("template", [sys.executable, "-m", "pytest", "tests/acceptance/W1-38", "tests/acceptance/W1-39", "-n",
                         "auto", "-q", "-p", "no:cacheprovider", "-o", "tmp_path_retention_policy=failed", "-rs",
                         f"--junitxml={LOG}/template.xml"], close_env)
    elif step == "check":
        run("check", [sys.executable, "-m", "gov.cli.main", "check", "--json"], base_env)
    elif step == "collect":
        run("collect", [sys.executable, "-m", "pytest", "tests", "--collect-only", "-q", "-p", "no:cacheprovider",
                        "--no-header"], base_env)
with open(f"{LOG}/ALL.exit", "w") as f:
    f.write("done\n")
