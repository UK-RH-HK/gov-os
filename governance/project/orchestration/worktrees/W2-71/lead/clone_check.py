"""Lead's check 3 of run 3 (DEC-946 item 1): the repaired K5 tests in a clone of w2/integrate merged with w2/W2-71.

Step "merged": HEAD is the merge of w2/W2-71 into w2/integrate; the premise and the sister test must pass.
Step "plant": one ticket commit (Task: DAEO-e8f0) adds a file holding a keyword of row W2-L423's rule whole;
the sister test must fail. The keyword is joined at run time; nothing here prints a file's contents.
"""

import os
import subprocess
import sys

MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
CLONE = "/tmp/gov-os-lead-W2-71/clone-check"
SRC = "/home/usain/gov-os-worktrees/W2-71/src"
TESTFILE = "tests/acceptance/W2-71/test_w2_71_keywords_in_parts.py"
PREMISE = TESTFILE + "::test_premise_the_list_holds_this_suites_own_files"
SISTER = TESTFILE + "::test_no_file_the_branch_writes_holds_a_keyword_of_row_w2_l423s_rule_whole"
TRAILERS = ["--trailer", "Task: DAEO-e8f0", "--trailer", "Implements: DEC-911", "--trailer", "Role: orchestrator"]


def run(args, cwd=CLONE, env=None, check=True):
    done = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=1800)
    if check and done.returncode != 0:
        print("FAILED:", " ".join(args), done.returncode, done.stdout[-2000:], done.stderr[-2000:])
        sys.exit(2)
    return done


def pytest(*nodes):
    env = dict(os.environ, PYTHONPATH=SRC, TMPDIR="/tmp/gov-os-lead-W2-71")
    done = run([sys.executable, "-m", "pytest", *nodes, "-q", "-p", "no:cacheprovider", "--no-header", "-rA"],
               env=env, check=False)
    tail = [line for line in done.stdout.splitlines() if line.startswith(("PASSED", "FAILED", "ERROR"))]
    return done.returncode, tail, done.stdout.splitlines()[-1:] if done.stdout else []


def main():
    step = sys.argv[1]
    if step == "merged":
        if not os.path.isdir(CLONE):
            run(["git", "clone", "--quiet", "--no-checkout", MAIN, CLONE], cwd="/tmp/gov-os-lead-W2-71")
        run(["git", "checkout", "--quiet", "w2/integrate"])
        same = run(["git", "rev-parse", "w2/integrate"]).stdout == run(["git", "rev-parse", "origin/w2/integrate"]).stdout
        print("local w2/integrate equals origin/w2/integrate before the merge:", same)
        if not same:
            sys.exit(3)
        run(["git", "-c", "user.name=Usain", "-c", "user.email=usain@jazry.com", "merge", "--quiet", "--no-ff",
             "origin/w2/W2-71", "-m", "lead check: merge w2/W2-71 into w2/integrate (clone only)", "-m", "Task: DAEO-e8f0\nImplements: DEC-911\nRole: orchestrator"])
        head = run(["git", "rev-parse", "--short=12", "HEAD"]).stdout.strip()
        integ = run(["git", "rev-parse", "--short=12", "w2/integrate"]).stdout.strip()
        print("clone HEAD", head, "w2/integrate", integ, "equal", head == integ)
        print("merge base of HEAD and w2/integrate is HEAD:",
              run(["git", "merge-base", "HEAD", "w2/integrate"]).stdout.strip()[:12] == head)
        code, tail, last = pytest(PREMISE, SISTER)
        print("exit", code, tail, last)
    elif step == "plant":
        word = "source" + "graph"
        rel = "tests/acceptance/W2-71/planted_lead_check.txt"
        with open(os.path.join(CLONE, rel), "w") as handle:
            handle.write("a planted note naming " + word + " whole\n")
        run(["git", "add", rel])
        run(["git", "-c", "user.name=Usain", "-c", "user.email=usain@jazry.com", "commit", "--quiet", "-m",
             "lead check: plant a file holding a keyword whole (clone only)", *TRAILERS])
        print("planted at", run(["git", "rev-parse", "--short=12", "HEAD"]).stdout.strip(), "path", rel)
        code, tail, last = pytest(PREMISE, SISTER)
        print("exit", code, tail, last)
    elif step == "plant-src":
        word = "sgp" + "_"
        rel = "src/gov/secrets/planted_lead_check.txt"
        with open(os.path.join(CLONE, rel), "w") as handle:
            handle.write("a planted note naming " + word + " whole\n")
        run(["git", "add", rel])
        run(["git", "-c", "user.name=Usain", "-c", "user.email=usain@jazry.com", "commit", "--quiet", "-m",
             "lead check: plant a second file under the code folder (clone only)", *TRAILERS])
        code, tail, last = pytest(SISTER)
        print("exit", code, tail, last)


if __name__ == "__main__":
    main()
