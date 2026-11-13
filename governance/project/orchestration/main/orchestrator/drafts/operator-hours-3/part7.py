# Part 7 of ACT-OPERATOR-HOURS-3's rehearsal (DEC-1136 (2)): apply.sh B's second stage, `exempt`, in a clone of w2/integrate.
# exec'd into build_act.py's namespace (run, sha, Log, REPO, WORK, BUNDLE, BREL, PKG, LIVE_MAP, MAP_REL, HEAVY, LIVE_INST, ...).
# Modelled on drafts/operator-hours-2/part7.py; one variant (the live map is the one allowed before: no path-map ACT is queued).
import yaml  # noqa: E402

HOME_REAL = Path("/home/usain")


def extract_blocks(pkg_text):
    """Section 0's two Part B blocks and section 5's undo block, as the package prints them."""
    sec = pkg_text.split("\n## 0.", 1)[1].split("\n## 1.", 1)[0]
    blocks = re.findall(r"```\n(.*?)```", sec, re.S)
    a = [b for b in blocks if "apply.sh B apply" in b]
    b = [x for x in blocks if "apply.sh B exempt " in x]
    assert len(a) == 1 and len(b) == 1, f"section 0 must hold one block with `apply.sh B apply` and one with `apply.sh B exempt ` ({len(a)}, {len(b)})"
    sec5 = pkg_text.split("\n## 5.", 1)[1].split("\n## 6.", 1)[0]
    u = [x for x in re.findall(r"```\n(.*?)```", sec5, re.S) if "git reset --keep" in x and "exempt-verify" in x]
    assert len(u) == 1, f"section 5 must hold one undo block with `git reset --keep` and `exempt-verify` ({len(u)})"
    return a[0], b[0], u[0]


def part7(L, tmp):
    L.note("part 7 (DEC-1136 (2)): the second commit. A clone of w2/integrate (`git clone --no-hardlinks`), HOME planted (a copy of the live install, the git identity), "
           "the bundle copied in at its own path. Section 0's two Part B blocks and section 5's undo block are run as the package prints them (the repository root substituted); "
           "W1-01 (tests/acceptance/W1-01, through heavy_slot.sh) before the ACT, between the two commits (the control) and after them.")
    blockA, blockB, blockU = extract_blocks(PKG.read_text())
    L.case(True, "the package holds the three blocks (section 0: Part B's apply and first commit; the exempt step and second commit; section 5: the undo of both commits)")
    root, home, wtmp = WORK / "exempt", WORK / "exempt-home", WORK / "exempt-tmp"
    wtmp.mkdir(parents=True)

    def env(**kw):
        e = {"HOME": str(home), "PATH": os.environ["PATH"], "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1"}
        e.update(kw)
        return e

    def git(*args, ok=None):
        r = run(["git", "-C", str(root), *args], env=env())
        if ok is not None:
            assert r.returncode in ok, (args, r.stdout, r.stderr)
        return r

    def out(*args):
        return git(*args, ok=(0,)).stdout.strip()

    def ap(step):
        return run(["bash", str(root / BREL / "apply.sh"), "B", step], env=env(), cwd=str(root))

    def block(text):
        return run(["bash", "-ec", text.replace(str(REPO), str(root))], env=env(), cwd="/")

    mp = root / MAP_REL

    def msha():
        return sha(mp)[:12] if mp.is_file() else "none"

    def w101():
        if NO_SLOTS:
            return None, NOT_RUN, []
        r = run(["bash", str(HEAVY), "python3", "-m", "pytest", "tests/acceptance/W1-01", "-q", "-p", "no:cacheprovider", "-o", "tmp_path_retention_policy=failed", "--no-header"],
                env=env(PYTHONUSERBASE=str(HOME_REAL / ".local"), PYTHONPATH=str(root / "src"), TMPDIR=str(wtmp)), cwd=str(root), timeout=3600)
        summ = [l for l in r.stdout.splitlines() if re.match(r"^\d+ (passed|failed)", l)]
        s = re.sub(r" in [0-9.]+s( \([0-9:]+\))?", "", summ[-1]).strip() if summ else "no summary"
        who = re.findall(r"^E +([0-9a-f]{12})$", r.stdout, re.M)
        return r.returncode, s, who

    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(REPO), str(root)], check=True)
    home.mkdir()
    shutil.copy2(HOME_REAL / ".gitconfig", home / ".gitconfig")
    op = home / "gov-os-operator"
    shutil.copytree(LIVE_INST, op / "install", ignore=shutil.ignore_patterns("__pycache__"))
    for d in ("log", "queue", "acts", "wall"):
        (op / d).mkdir(parents=True, exist_ok=True)
    shutil.copytree(BUNDLE, root / BREL)
    four = sorted(l.split("|")[1] for l in (BUNDLE / "list.txt").read_text().splitlines() if l.startswith("repo|"))
    old_ap = sha(op / "install/APPROVED")
    base = out("rev-parse", "HEAD")
    L.case(sha(mp) == LIVE_MAP and out("status", "--porcelain") == "", f"the clone's map is the allowed before ({LIVE_MAP[:12]}), the clone clean at {base[:12]}")
    r = ap("check")
    L.case(r.returncode == 0 and "ready to apply" in r.stdout, f"B check: ready ({r.returncode})")
    rc, s, who = w101()
    base_summary = s
    (L.note if rc is None else (lambda x: L.case(rc == 0 and "failed" not in s, x)))(f"W1-01 before the ACT: green ({s})")
    h0 = msha()
    r = ap("exempt")
    L.case(r.returncode == 3 and "HEAD is not the ACT's commit" in r.stderr and msha() == h0, f"B exempt before the first commit: exit 3, untouched ({r.returncode})")

    a = block(blockA)
    c1 = out("rev-parse", "HEAD")
    L.case(a.returncode == 0 and "state applied (B)" in a.stdout and "verify B: every listed file is the after" in a.stdout and c1 != base,
           f"section 0's first Part B block run as printed: exit {a.returncode}, applied, verified, committed" + ("" if a.returncode == 0 else f" ({a.stderr.strip()[-160:]})"))
    changed = sorted(out("diff-tree", "--no-commit-id", "--name-only", "-r", c1).split())
    trailers = out("log", "-1", "--format=%(trailers:only,unfold,separator=; )", c1)
    L.case(changed == four and "Role: owner" in trailers and "Task: DAEO-sdxk" in trailers and "Implements: DEC-1157" in trailers
           and out("rev-list", "--parents", "-n", "1", c1).count(" ") == 1 and out("status", "--porcelain") == "",
           "the first commit: one parent, the trailers Task: DAEO-sdxk, Implements: DEC-1157, Role: owner, exactly the four repository paths, the tree clean")
    rc, s, who = w101()
    (L.note if rc is None else (lambda x: L.case(rc != 0 and s.startswith("1 failed") and who == [c1[:12]], x)))(f"CONTROL, W1-01 between the two commits: red, the one failure names the first commit and no other ({s}; {who})")
    r = ap("exempt-verify")
    L.case(r.returncode == 3, f"B exempt-verify before the exempt step: exit 3 ({r.returncode})")

    b = block(blockB)
    c2 = out("rev-parse", "HEAD")
    L.case(b.returncode == 0 and f"exempt: added the entry for {c1[:12]}" in b.stdout and "exempt-verify: the map is the allowed before" in b.stdout and c2 != c1,
           f"section 0's second Part B block run as printed: exit {b.returncode}, entry added, verified, committed" + ("" if b.returncode == 0 else f" ({b.stderr.strip()[-160:]})"))
    subj = out("log", "-1", "--format=%s", c2)
    tr2 = out("log", "-1", "--format=%(trailers:only,unfold,separator=; )", c2)
    L.case(subj == f"ACT-OPERATOR-HOURS-3: acceptance_exemptions lists its own commit {c1[:12]} (DEC-1136 (2))" and out("rev-parse", f"{c2}^") == c1
           and "Task: DAEO-sdxk" in tr2 and "Implements: DEC-1136, DEC-1157" in tr2 and "Role: owner" in tr2,
           "the second commit: on the first, its subject names the first's 12 digits, trailers Task, Implements (DEC-1136, DEC-1157), Role: owner")
    L.case(out("diff-tree", "--no-commit-id", "--name-only", "-r", c2) == MAP_REL and out("diff", "--numstat", c1, c2).split("\t")[:2] == ["2", "0"],
           "the second commit changes the path map only: 2 lines added, 0 removed")
    L.case(stat.S_IMODE(mp.stat().st_mode) == 0o644 and not [p for p in (root / "governance/project").iterdir() if "act-operator-hours-3" in p.name] and out("status", "--porcelain") == "",
           "the map's mode kept (644), no temporary file, the tree clean")
    old = yaml.safe_load(out("show", f"{c1}:{MAP_REL}"))
    new = yaml.safe_load(mp.read_text())
    L.case(new["acceptance_exemptions"] == old["acceptance_exemptions"] + [{"commit": c1, "decision": "DEC-1157"}]
           and {k: v for k, v in new.items() if k != "acceptance_exemptions"} == {k: v for k, v in old.items() if k != "acceptance_exemptions"},
           "the map parses; acceptance_exemptions is the old list plus the one entry (the full id, DEC-1157) at the end; every other key equal")
    rc, s, who = w101()
    (L.note if rc is None else (lambda x: L.case(rc == 0 and s == base_summary, x)))(f"W1-01 after the second commit: green, as before the ACT ({s})")
    snap = (msha(), out("rev-parse", "HEAD"))
    r = ap("exempt")
    L.case(r.returncode == 0 and "already in place" in r.stdout and (msha(), out("rev-parse", "HEAD")) == snap, "B exempt again after the second commit: a no-op, exit 0")
    r = ap("exempt-verify")
    L.case(r.returncode == 0 and "plus exactly the entry" in r.stdout, f"B exempt-verify after the second commit: exit 0 ({r.returncode})")
    r = ap("exempt-undo")
    L.case(r.returncode == 3 and "is committed" in r.stderr and (msha(), out("rev-parse", "HEAD")) == snap, "B exempt-undo after the second commit: refused, exit 3, untouched")
    r = ap("verify")
    L.case(r.returncode == 0, f"B verify after both commits: exit 0 ({r.returncode})")
    u = block(blockU)
    L.case(u.returncode == 0 and out("rev-parse", "HEAD") == base and msha() == LIVE_MAP[:12] and out("status", "--porcelain") == "" and sha(op / "install/APPROVED") == old_ap,
           f"section 5's undo block run as printed: exit {u.returncode}, HEAD the head before the ACT, the map the allowed before, the tree clean, APPROVED the old one" + ("" if u.returncode == 0 else f" ({u.stderr.strip()[-160:]})"))
    r = ap("check")
    L.case(r.returncode == 0, "B check after that undo: ready again")

    # planted
    def make_c1():
        assert ap("apply").returncode == 0
        git("add", *four, ok=(0,))
        git("commit", "-q", "-m", "ACT-OPERATOR-HOURS-3: G9 has no time hold (DEC-1157 (2))", "--trailer", "Task: DAEO-sdxk", "--trailer", "Implements: DEC-1157", "--trailer", "Role: owner", ok=(0,))
        return out("rev-parse", "HEAD")

    def undo_to(rev):
        git("reset", "-q", "--hard", rev, ok=(0,))
        git("clean", "-q", "-fd", "--", "tests", "governance", ok=(0,))

    def refuses(label, text=None, rc_=3):
        before_ = msha()
        r_ = ap("exempt")
        stray = [p.name for p in (root / "governance/project").iterdir() if "act-operator-hours-3" in p.name]
        L.case(r_.returncode == rc_ and (text is None or text in r_.stderr) and msha() == before_ and not stray,
               f"PLANTED, B exempt refuses {label}: exit {rc_}, the map untouched ({r_.returncode}; {r_.stderr.strip()[:90]})")
    c1 = make_c1()
    h1 = msha()
    r1, after1 = ap("exempt"), sha(mp)
    r2 = ap("exempt")
    L.case(r1.returncode == 0 and r2.returncode == 0 and "already in place" in r2.stdout and sha(mp) == after1, "PLANTED, B exempt run twice before the second commit: the second a no-op")
    r = ap("exempt-undo")
    L.case(r.returncode == 0 and msha() == h1 and out("status", "--porcelain") == "", "PLANTED, B exempt-undo before the second commit: the map the allowed before again")
    git("commit", "-q", "--allow-empty", "-m", "an unrelated commit", "--trailer", "Role: owner", ok=(0,))
    refuses("on another HEAD (an unrelated commit on top)", "HEAD is not the ACT's commit")
    undo_to(c1)
    git("commit", "-q", "--amend", "-m", "ACT-OPERATOR-HOURS-3: as an operator commit", "--trailer", "Role: operator", ok=(0,))
    refuses("when the ACT's commit is not Role: owner", "no single trailer Role: owner")
    undo_to(c1)
    git("commit", "-q", "--amend", "-m", "ACT-OPERATOR-HOURS-2: the wrong ACT", "--trailer", "Role: owner", ok=(0,))
    refuses("when the subject does not start ACT-OPERATOR-HOURS-3: (HOURS-2's subject)", "its subject does not start")
    undo_to(c1)
    (root / "tests/unit/operator/extra_planted.py").write_text("# planted\n")
    git("add", "tests/unit/operator/extra_planted.py", ok=(0,))
    git("commit", "-q", "--amend", "--no-edit", ok=(0,))
    refuses("when the commit changes a fifth path", "exactly the ACT's repository paths")
    undo_to(c1)
    with open(root / "tests/acceptance/W2-148/README.md", "a") as f:
        f.write("planted\n")
    git("commit", "-q", "--amend", "--no-edit", "-a", ok=(0,))
    refuses("when one of the four files is not the ACT's after file", "is not the ACT's after file")
    undo_to(c1)
    with open(mp, "a") as f:
        f.write("# planted\n")
    refuses("on a map that is not the allowed before (a changed line, not committed)", "is not the allowed before")
    git("checkout", "-q", "--", MAP_REL, ok=(0,))
    mp.rename(str(mp) + ".real")
    os.symlink(str(mp) + ".real", mp)
    refuses("on a map that is a link", "missing or a link")
    mp.unlink()
    os.rename(str(mp) + ".real", mp)
    git("checkout", "-q", "--", MAP_REL, ok=(0,))
    os.chmod(root / "governance/project", 0o555)
    try:
        refuses("when the map's folder is not writable", None, rc_=5)
    finally:
        os.chmod(root / "governance/project", 0o755)
    # a path-map change committed between the build and the apply (the map moved): refused
    undo_to(base)
    with open(mp, "a") as f:
        f.write("# another ACT's change, committed\n")
    git("commit", "-q", "-a", "-m", "rehearsal: the map moved", "--trailer", "Role: operator", ok=(0,))
    make_c1()
    refuses("when the map moved since the build (committed, the tree clean)", "is not the allowed before")
    # the undo after the first commit alone, as section 5 gives it
    undo_to(base)
    c1 = make_c1()
    git("reset", "-q", "--keep", f"{c1}~1", ok=(0,))
    r = ap("undo")
    L.case(r.returncode == 0 and out("rev-parse", "HEAD") == base and sha(op / "install/APPROVED") == old_ap and out("status", "--porcelain") == "" and ap("check").returncode == 0,
           "the undo after the first commit alone (`git reset --keep <first>~1`, then `apply.sh B undo`): HEAD before the ACT, APPROVED the old one, tree clean, check ready")
    undo_to(base)
    c1 = make_c1()
    ap("exempt")
    good = mp.read_text()
    lines = good.splitlines(keepends=True)
    i = next(k for k, l in enumerate(lines) if l.startswith(f'  - commit: "{c1}"'))
    mp.write_text("".join(lines[:i - 2] + lines[i:i + 2] + lines[i - 2:i] + lines[i + 2:]))
    r = ap("exempt-verify")
    L.case(r.returncode == 3 and "not at the end" in r.stderr, f"PLANTED, exempt-verify on an entry moved up one place: exit 3 ({r.returncode})")
    mp.write_text(good.replace("decision: DEC-1157  # ACT-OPERATOR-HOURS-3's", "decision: DEC-1141  # ACT-OPERATOR-HOURS-3's"))
    r = ap("exempt-verify")
    L.case(r.returncode == 3, f"PLANTED, exempt-verify on an entry whose decision was changed: exit 3 ({r.returncode})")
    mp.write_text(good)
    r = ap("exempt-verify")
    L.case(r.returncode == 0, f"PLANTED, the control: the good map verifies, exit 0 ({r.returncode})")
