"""The lead's verification for DAEO-0mtg (W2-106), in the close's form (DEC-952, DEC-968): the scoped selection's
parallel run, then its serial-route cases alone; then W1-39 (KPI 4 names it; the selection ignores it); then
`gov check --json` and the collection check (DEC-868). Every step writes its own exit file."""
import os
import subprocess
import sys
import time

WT = "/home/usain/gov-os-worktrees/W2-106"
LOG = WT + "/.gov-runtime/scratch/lead/log"
TOOLS = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools"
NODE = "/home/usain/.nvm/versions/node/v22.23.3/bin"


def wait_load():
    while True:
        l1, _, l15 = os.getloadavg()
        if min(l1, l15) < os.cpu_count():
            return
        time.sleep(60)


def base_env(**extra):
    env = dict(os.environ)
    env["PATH"] = NODE + ":" + env.get("PATH", "/usr/bin:/bin")
    env["PYTHONPATH"] = WT + "/src:" + WT + "/src/gov/close/pytest_plugin"
    env["GOV_CLOSE_SERIAL_ONLY_OF"] = WT
    env["TMPDIR"] = "/tmp/gov-os-lead-W2-106"
    env.update(extra)
    return env


def run(name, argv, env):
    wait_load()
    with open(f"{LOG}/{name}.start", "w") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
    with open(f"{LOG}/{name}.txt", "w") as out:
        rc = subprocess.run(argv, cwd=WT, env=env, stdout=out, stderr=subprocess.STDOUT).returncode
    with open(f"{LOG}/{name}.exit", "w") as f:
        f.write(f"{rc}\n")
    return rc


def main():
    steps = sys.argv[1:] or ["parallel", "serial", "w1_39", "check", "collect"]
    opts = [l.strip() for l in open(f"{LOG}/pytest_options.txt") if l.strip()]
    serial = [l.strip() for l in open(f"{LOG}/serial_given.txt") if l.strip()]
    # DEC-968: a scoped run needs no wrapper; the memory gate in verify_lock.sh sizes every run as a full run.
    lock = []
    gate = subprocess.run(["bash", f"{TOOLS}/disk_gate.sh"], capture_output=True, text=True)
    with open(f"{LOG}/disk_gate.txt", "a") as f:
        f.write(gate.stdout + gate.stderr)
    if gate.returncode != 0:
        open(f"{LOG}/verify.exit", "w").write("disk-gate-shut\n")
        return
    if "parallel" in steps:
        run("parallel", lock + ["python3", "-m", "pytest", "tests", "-n", "auto", "-q", "-p", "no:cacheprovider",
                                "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed", "-rs",
                                f"--junitxml={LOG}/parallel.xml", *opts], base_env())
    if "serial" in steps and serial:
        run("serial", lock + ["python3", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only",
                              "-o", "tmp_path_retention_policy=failed", "-rs", f"--junitxml={LOG}/serial.xml",
                              *opts, *serial],
            base_env(GOV_CLOSE_SERIAL_ONLY_GIVEN="\n".join(serial)))
    if "w1_39" in steps:
        run("w1_39", ["python3", "-m", "pytest", "tests/acceptance/W1-39", "-n", "auto", "-q", "-p", "no:cacheprovider",
                      "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed", "-rs",
                      f"--junitxml={LOG}/w1_39.xml"], base_env())
    if "check" in steps:
        env = base_env()
        env["PYTHONPATH"] = WT + "/src"
        run("check", ["python3", "-m", "gov.cli.main", "check", "--json"], env)
    if "collect" in steps:
        env = base_env()
        env["PYTHONPATH"] = WT + "/src"
        run("collect", ["python3", "-m", "pytest", "tests", "--collect-only", "-q", "-p", "no:cacheprovider",
                        "--no-header"], env)
    open(f"{LOG}/verify.exit", "w").write("done\n")


if __name__ == "__main__":
    main()
