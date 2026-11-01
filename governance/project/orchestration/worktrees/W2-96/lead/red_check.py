"""Red check: run the W2-96 acceptance folder in a given tree, summarise failure reasons (marker stripped)."""
import collections
import os
import re
import subprocess
import sys

tree = sys.argv[1]
out = sys.argv[2]
env = dict(os.environ, PYTHONPATH=os.path.join(tree, "src"), TMPDIR="/tmp/gov-os-lead-W2-96")
print(subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], env=env, cwd=tree,
                     capture_output=True, text=True).stdout.strip())
done = subprocess.run([sys.executable, "-m", "pytest", "tests/acceptance/W2-96", "-q", "-p", "no:cacheprovider",
                       "-o", "tmp_path_retention_policy=failed", "--junitxml=" + out],
                      env=env, cwd=tree, capture_output=True, text=True, timeout=1500)
reasons = collections.Counter()
for line in done.stdout.splitlines():
    if line.startswith("E   ") and "Error" in line:
        reasons[re.sub(r"qzv96leak\S*", "<m>", line)[:170]] += 1
for reason, count in reasons.most_common(15):
    print(count, reason)
print("exit", done.returncode)
print(done.stdout.strip().splitlines()[-1] if done.stdout.strip() else "no output")
