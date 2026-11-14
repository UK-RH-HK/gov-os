# ACT-CLASS-RULES-AGENTS-1's rehearsal, part 5 (exec'd by build_act.py rehearse, in its globals): the package's three blocks run as
# printed (cut from the package file, the repository root replaced by a clone's), in a clone of w2/integrate with a planted HOME.
# Adapted from drafts/w2-148-s15/part5.py (ACT-W2-148-S15-1).
TRAILERS = ["Task: DAEO-sdxk", "Implements: DEC-1173", "Role: owner"]


def part5(L, tmp, world):
    L.note("part 5: the package's blocks as printed, in a `git clone --no-hardlinks` of w2/integrate's head with a planted HOME (a copy of the live install)")
    pkg = PKG.read_text()
    blocks = re.findall(r"```bash\n(cd /home/usain/Dynamic-Agentic-Engineering-OS\n.*?)```", pkg, re.S)
    L.case(len(blocks) == 3, f"the package holds three blocks that start in the main tree: the apply and commit, the undo before the commit, the undo after it ({len(blocks)})")
    c5 = WORK / "clone5"
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(REPO), str(c5)], check=True)
    shutil.copytree(BUNDLE, c5 / BREL)
    home = tmp / "home5"
    op = home / "gov-os-operator"
    shutil.copytree(LIVE_INST, op / "install", ignore=shutil.ignore_patterns("__pycache__"))
    for d in ("log", "queue", "acts", "wall"):
        (op / d).mkdir(parents=True, exist_ok=True)
    (home / ".gitconfig").write_text("[user]\n\tname = Planted Owner\n\temail = planted@example.invalid\n")
    env = {"HOME": str(home), "PATH": os.environ["PATH"], "LC_ALL": "C"}

    def blk(i):
        text = blocks[i].replace("/home/usain/Dynamic-Agentic-Engineering-OS", str(c5))
        return run(["bash", "-e", "-c", text], env=env, cwd=str(tmp))

    def g(*a):
        return run(["git", "-C", str(c5), *a], env=env).stdout.strip()

    def inst_is(vals):
        return all(sha(home / p) == v for (r, p), v in vals.items() if r == "home")
    lst = rows_of(BUNDLE / "list.txt")
    before = {(r, p): b for r, p, b, a in lst}
    after = {(r, p): a for r, p, b, a in lst}
    head0 = g("rev-parse", "HEAD")
    L.note(f"the clone's head: {head0[:12]}")
    r = blk(0)
    L.case(r.returncode == 0, f"block 1 (check, apply, verify, status, add, commit, log) as printed: exit 0 ({r.returncode}; {r.stderr.strip()[-200:]})")
    a = g("rev-parse", "HEAD")
    L.case(g("rev-parse", "HEAD~1") == head0 and len(g("rev-list", "--parents", "-n", "1", a).split()) == 2, "one new commit on the head, one parent")
    L.case(g("diff-tree", "--no-commit-id", "--name-only", "-r", a) == RULES_REL, "the commit changes exactly governance/project/operator/class-rules.yaml")
    L.case(shab(run(["git", "-C", str(c5), "cat-file", "blob", f"{a}:{RULES_REL}"], env=env).stdout.encode()) == after[("repo", RULES_REL)],
           "its blob is the after")
    tr = g("log", "-1", "--format=%(trailers:only,unfold)", a).splitlines()
    L.case(tr == TRAILERS and g("log", "-1", "--format=%s", a).startswith(ACT + ": "),
           f"the subject starts {ACT}:, the trailers {', '.join(TRAILERS)} ({tr})")
    L.case(inst_is(after) and g("status", "--porcelain", "--untracked-files=no") == "", "the planted install is the after; the clone's tree is clean")
    lc = run([sys.executable, "-I", "-B", str(c5 / "governance/project/operator/landing_check.py"), "--repo", str(c5), f"{head0}..{a}"], env=env)
    L.case(lc.returncode == 0 and json.loads(lc.stdout) == [], f"the landing check (S16) over the commit, with the after table beside it: no item (Role: owner) ({lc.stdout.strip()[:80]})")
    tree = g("rev-parse", f"{a}^{{tree}}")
    x = run(["git", "-C", str(c5), "commit-tree", tree, "-p", head0, "-m", "planted: the same change without Role: owner\n\nTask: DAEO-sdxk"], env=env).stdout.strip()
    lc2 = run([sys.executable, "-I", "-B", str(c5 / "governance/project/operator/landing_check.py"), "--repo", str(c5), f"{head0}..{x}"], env=env)
    items = json.loads(lc2.stdout or "[]")
    L.case(len(items) == 1 and items[0]["rows"] == ["operator-own"] and items[0]["priority"] == "P1",
           "control: the same tree committed without Role: owner is flagged P1 by the landing check (row operator-own), so the trailer matters")
    # the new row's effect on the landing check: a CTO commit (Task: DAEO-sdxk, no Role: owner) to CLAUDE.md is now an item
    (c5 / "CLAUDE.md").write_text((c5 / "CLAUDE.md").read_text() + "\nplanted\n")
    run(["git", "-C", str(c5), "add", "CLAUDE.md"], env=env)
    tree2 = run(["git", "-C", str(c5), "write-tree"], env=env).stdout.strip()
    run(["git", "-C", str(c5), "reset", "-q", "--", "CLAUDE.md"], env=env)
    run(["git", "-C", str(c5), "checkout", "-q", "--", "CLAUDE.md"], env=env)
    y = run(["git", "-C", str(c5), "commit-tree", tree2, "-p", a, "-m", "planted: a CTO edit of CLAUDE.md\n\nTask: DAEO-sdxk"], env=env).stdout.strip()
    lc3 = run([sys.executable, "-I", "-B", str(c5 / "governance/project/operator/landing_check.py"), "--repo", str(c5), f"{a}..{y}"], env=env)
    it3 = json.loads(lc3.stdout or "[]")
    L.case(len(it3) == 1 and it3[0]["rows"] == [NEW_ROW] and it3[0]["paths"] == ["CLAUDE.md"] and g("status", "--porcelain", "--untracked-files=no") == "",
           f"the new row in the landing check: a planted CTO commit of CLAUDE.md (Task: DAEO-sdxk, no Role: owner) on the after table is one P1 item on row {NEW_ROW} (on the before table the catch-all is not a control path)")
    r = blk(2)
    L.case(r.returncode == 0, f"block 3 (the undo after the commit) as printed: exit 0 ({r.returncode}; {r.stderr.strip()[-200:]})")
    u = g("rev-parse", "HEAD")
    L.case(g("rev-parse", "HEAD~1") == a and g("diff-tree", "--no-commit-id", "--name-only", "-r", u) == RULES_REL
           and g("log", "-1", "--format=%(trailers:only,unfold)", u).splitlines() == TRAILERS,
           "its commit: on the ACT's commit, class-rules.yaml only, the same three trailers")
    L.case(sha(c5 / RULES_REL) == before[("repo", RULES_REL)] and g("rev-parse", f"{u}:{RULES_REL}") == g("rev-parse", f"{head0}:{RULES_REL}")
           and inst_is(before) and g("status", "--porcelain", "--untracked-files=no") == "",
           "after it: the tree's and the committed class-rules.yaml are the before, the install's two files the before, the tree clean")
    lc4 = run([sys.executable, "-I", "-B", str(c5 / "governance/project/operator/landing_check.py"), "--repo", str(c5), f"{a}..{y}"], env=env)
    L.case(json.loads(lc4.stdout or "[]") == [], "and with the before table back, the same planted CLAUDE.md commit is no item (the catch-all is not a control path)")
    rc = run(["bash", str(c5 / BREL / "apply.sh"), "check"], env=env, cwd=str(c5))
    L.case(rc.returncode == 0, f"apply.sh check: ready to apply again ({rc.returncode})")
    for staged in (False, True):
        rr = run(["bash", str(c5 / BREL / "apply.sh"), "apply"], env=env, cwd=str(c5))
        if staged:
            run(["git", "-C", str(c5), "add", RULES_REL], env=env)
        r = blk(1)
        L.case(rr.returncode == 0 and r.returncode == 0 and inst_is(before) and sha(c5 / RULES_REL) == before[("repo", RULES_REL)]
               and g("status", "--porcelain", "--untracked-files=no") == "" and g("rev-parse", "HEAD") == u,
               f"block 2 (the undo before the commit) as printed, after an apply{' and the git add' if staged else ''}: exit 0, the install and the tree the before, nothing staged, no commit ({r.returncode}; {r.stderr.strip()[-160:]})")
