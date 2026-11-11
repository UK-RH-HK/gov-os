"""Builds, for the launch rehearsal, a small FAKE product repository (not EXAMIN: invented files) as a git repository, then
the launch scaffold on a second commit exactly as FOR-THE-OWNER.md step 4 describes it for the owner's copy:
  - governance/project/indep-walls/<the six template files>, byte for byte from this repository's commit,
  - governance/project/indep-walls/COPY-HEAD.txt (the first commit's 40 digits),
  - governance/project/path-map.yaml holding only the sets_root_hidden block (as the launcher reads it),
  - governance/project/indep-briefs/<the two briefs>.
  python3 mk_fake_examin.py <repo dir> <gov-os clone> <examin brief> <proving-ground brief>
Prints the two commits and the briefs' sha256."""
import hashlib
import os
import subprocess
import sys

import yaml

repo, gov, b_examin, b_pg = (os.path.abspath(p) for p in sys.argv[1:5])
TEMPLATE = ("settings.json.tmpl", "wall_hook.py", "CLAUDE.md.tmpl", "kinds.yaml", "tree-exclude.txt", "README.md")
ENV = dict(os.environ, GIT_AUTHOR_NAME="rehearsal", GIT_AUTHOR_EMAIL="r@example.invalid", GIT_COMMITTER_NAME="rehearsal",
           GIT_COMMITTER_EMAIL="r@example.invalid", GIT_AUTHOR_DATE="2026-01-01T00:00:00Z",
           GIT_COMMITTER_DATE="2026-01-01T00:00:00Z")


def git(*a):
    return subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True, text=True, env=ENV).stdout.strip()


def put(rel, data):
    p = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data if isinstance(data, bytes) else data.encode())


os.makedirs(repo)
git("init", "-q", "-b", "main")
for i in range(60):
    put(f"src/mod{i:02d}.py", f"def f{i}(x):\n    return x + {i}\n")
for i in range(15):
    put(f"docs/note{i:02d}.md", f"# Note {i}\n\nThe limit of area {i} is {i * 7}.\n")
put("README.md", "# Fake product\n")
git("add", "-A")
git("commit", "-q", "-m", "fake product")
copy = git("rev-parse", "HEAD")
git("checkout", "-q", "-b", "w2/integrate")
for name in TEMPLATE:
    put(f"governance/project/indep-walls/{name}", open(os.path.join(gov, "governance/project/indep-walls", name), "rb").read())
put("governance/project/indep-walls/COPY-HEAD.txt", copy + "\n")
pm = yaml.safe_load(open(os.path.join(gov, "governance/project/path-map.yaml")))
put("governance/project/path-map.yaml", yaml.safe_dump({"sets_root_hidden": pm["sets_root_hidden"]}, sort_keys=False))
shas = {}
for brief, name in ((b_examin, "examin-writer.md"), (b_pg, "proving-ground-writer.md")):
    data = open(brief, "rb").read()
    put(f"governance/project/indep-briefs/{name}", data)
    shas[name] = hashlib.sha256(data).hexdigest()
git("add", "-A")
git("commit", "-q", "-m", "launch scaffold")
print("copy", copy)
print("pin", git("rev-parse", "HEAD"))
for k, v in shas.items():
    print("brief", k, v)
tm = {n: hashlib.sha256(open(os.path.join(repo, "governance/project/indep-walls", n), "rb").read()).hexdigest()
      for n in TEMPLATE}
for k, v in tm.items():
    print("template", k, v)
