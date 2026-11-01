"""Re-run alone each red of the scoped run (DEC-757 reading under DEC-953: a red that fails alone is a red; one that
passes alone is a flaky candidate), and show the W1-50 interaction on the base (the tests worktree, no template
change)."""
import os
import subprocess
import time
import xml.etree.ElementTree as ET

WT = "/home/usain/gov-os-worktrees/W2-106"
BASE = "/home/usain/gov-os-worktrees/W2-106-tests"
LOG = WT + "/.gov-runtime/scratch/lead/log"
NODE = "/home/usain/.nvm/versions/node/v22.23.3/bin"


def wait_load():
    while True:
        l1, _, l15 = os.getloadavg()
        if min(l1, l15) < os.cpu_count():
            return
        time.sleep(60)


def env_for(tree):
    env = dict(os.environ)
    env["PATH"] = NODE + ":" + env.get("PATH", "/usr/bin:/bin")
    env["PYTHONPATH"] = tree + "/src"
    env["TMPDIR"] = "/tmp/gov-os-lead-W2-106"
    return env


def red_ids():
    root = ET.parse(f"{LOG}/parallel.xml").getroot()
    ids = []
    for case in root.iter("testcase"):
        if case.find("failure") is None and case.find("error") is None:
            continue
        cls = case.get("classname").split(".")
        path = "/".join(cls[:-1]) + "/" + cls[-1] + ".py"
        ids.append(f"{path}::{case.get('name')}")
    return ids


def run(name, tree, args):
    wait_load()
    with open(f"{LOG}/{name}.txt", "w") as out:
        rc = subprocess.run(["python3", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-o",
                             "tmp_path_retention_policy=failed", "-rs", f"--junitxml={LOG}/{name}.xml", *args],
                            cwd=tree, env=env_for(tree), stdout=out, stderr=subprocess.STDOUT).returncode
    open(f"{LOG}/{name}.exit", "w").write(f"{rc}\n")


def main():
    ids = red_ids()
    groups = {
        "alone-w1-50": [i for i in ids if "/W1-50/" in i],
        "alone-w2-54": [i for i in ids if "/W2-54/" in i],
        "alone-w1-08": [i for i in ids if "/W1-08/" in i],
        "alone-known": [i for i in ids if "/W2-59/" in i or "/W1-05/" in i or "/W1-46/" in i],
    }
    for name, group in groups.items():
        if group:
            run(name, WT, group)
    # The interaction, on the base: W1-50's helper case after tests/unit/adapters/test_portability.py, one process.
    run("pair-base", BASE, ["-p", "no:randomly", "tests/unit/adapters/test_portability.py",
                            "tests/acceptance/W1-50/test_w1_50_read_merge_helper.py"])
    open(f"{LOG}/rerun.exit", "w").write("done\n")


if __name__ == "__main__":
    main()
