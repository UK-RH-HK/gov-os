"""The small kit the two ACT builders share (ACT-LANDING-CTO-ROUTE-1 and ACT-CLAUDE-RULES-1): a rehearsal log that counts its
failures, a command runner, fresh --no-hardlinks clones, and a pytest run through heavy_slot.sh with TMPDIR outside the
repository. Nothing here writes outside the paths it is given."""
import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path

LIVE = Path("/home/usain/Dynamic-Agentic-Engineering-OS")          # read only: the main tree
ORCH = LIVE / ".gov-runtime/scratch/orchestrator"
HEAVY = str(ORCH / "tools/heavy_slot.sh")
INSTALL = Path.home() / "gov-os-operator/install"                  # read only: the operator's install


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def shab(b):
    return hashlib.sha256(b).hexdigest()


def run(cmd, cwd=None, env=None, inp=None, timeout=3600):
    r = subprocess.run(cmd, cwd=cwd, env=env, input=inp, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr)


def git(tree, *args):
    code, out = run(["git", "-C", str(tree), *args])
    return code, out.strip()


def clone(src, dest, rev=None):
    dest = Path(dest)
    if dest.exists():
        shutil.rmtree(dest)
    code, out = run(["git", "clone", "-q", "--no-hardlinks", str(src), str(dest)])
    assert code == 0, out
    rev = rev or git(src, "rev-parse", "HEAD")[1]
    assert run(["git", "-C", str(dest), "checkout", "-q", rev])[0] == 0
    run(["git", "-C", str(dest), "config", "user.email", "rehearsal@example.invalid"])
    run(["git", "-C", str(dest), "config", "user.name", "rehearsal"])
    return rev


class Log:
    def __init__(self, path):
        self.path = Path(path)
        self.lines, self.failures, self.n = [], 0, 0

    def say(self, text):
        self.lines.append(text)
        print(text, flush=True)

    def note(self, text):
        self.say("     " + text)

    def head(self, text):
        self.say("--- " + text)

    def case(self, ok, label, detail=""):
        self.n += 1
        if not ok:
            self.failures += 1
        self.say(f"{'ok  ' if ok else 'FAIL'} {label}" + (f": {detail}" if detail else ""))
        return ok

    def finish(self):
        self.say(f"=== {self.n - self.failures} ok, {self.failures} failed")
        self.say(f"failures: {self.failures}")
        self.path.write_text("\n".join(self.lines) + "\n")
        return self.failures


def pytest(clone_dir, args, tmp, out_file, timeout=1800):
    """One folder per run, through heavy_slot.sh, TMPDIR outside the repository; (exit code, last line)."""
    Path(tmp).mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, TMPDIR=str(tmp), PYTHONDONTWRITEBYTECODE="1")
    env["PYTHONPATH"] = str(Path(clone_dir) / "src")      # the tree's own src first (DEC-732)
    code, out = run(["bash", HEAVY, "python3", "-m", "pytest", "-p", "no:cacheprovider", "-q", *args], cwd=clone_dir,
                    env=env, timeout=timeout)
    Path(out_file).write_text(out)
    lines = [ln for ln in out.strip().splitlines() if ln.strip()]
    counts = [ln for ln in lines if re.search(r"\d+ (passed|failed|error|deselected|skipped)|no tests ran", ln)]
    return code, (counts or lines or [""])[-1]


def failed_ids(out_file):
    return sorted(set(re.findall(r"^FAILED (\S+)", Path(out_file).read_text(), re.M)))


def tree_state(root):
    """The main tree's tracked status, as a text, for 'the rehearsal left it alone'."""
    return git(root, "status", "--porcelain", "--untracked-files=no")[1]
