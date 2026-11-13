# Part 7 of the rehearsal (round 2, DEC-1136 (2)): apply.sh's second stage, `exempt`, in clones of w2/integrate. Imported by build_act.py
# (it is exec'd into its namespace: it uses its run, sha, Log, ORCH, REPO, WORK, BUNDLE, CHAIN, LIVE_MAP, CHAIN_MAP, MAP_REL, ... names).
import yaml  # noqa: E402  (the system python3 has it; the pinned python is used only for gates.owner_listed)

PIN_PY = Path("/home/usain/.local/bin/gov").read_text().splitlines()[0][2:].strip()
REPO_STR = str(REPO)
HOME_REAL = Path("/home/usain")


def extract_blocks(pkg_text):
    """Section 0's two operator blocks, as the package prints them: the fenced blocks that hold `apply.sh apply` and `apply.sh exempt `."""
    sec = pkg_text.split("\n## 0.", 1)[1].split("\n## 1.", 1)[0]
    blocks = re.findall(r"```\n(.*?)```", sec, re.S)
    a = [b for b in blocks if "apply.sh apply" in b]
    b = [x for x in blocks if "apply.sh exempt " in x]
    assert len(a) == 1 and len(b) == 1, f"section 0 must hold one block with `apply.sh apply` and one with `apply.sh exempt ` ({len(a)}, {len(b)})"
    sec5 = pkg_text.split("\n## 5.", 1)[1].split("\n## 6.", 1)[0]
    u = [x for x in re.findall(r"```\n(.*?)```", sec5, re.S) if "git reset --keep HEAD~2" in x]
    assert len(u) == 1, f"section 5 must hold one block with `git reset --keep HEAD~2` ({len(u)})"
    return a[0], b[0], u[0]


def part7(L, tmp):
    L.note("part 7 (round 2, DEC-1136 (2)): the second commit. Two clones of w2/integrate (`git clone --no-hardlinks`), one per allowed before of the path map "
           "(the live map; the map ACT-EXAMIN-SETS-1, ACT-ACCEPTED-REDS-1 and ACT-PATHMAP-EXP-1 leave, applied here by their own apply.sh), HOME planted, "
           "the bundle copied in at its own path. Section 0's two blocks are run as the package prints them; W1-01 (tests/acceptance/W1-01, through heavy_slot.sh) is run on each.")
    blockA, blockB, blockU = extract_blocks(PKG_DRAFT.read_text())
    L.case(True, "the package holds the operator's three blocks (section 0: the apply and first commit, the exempt step and second commit; section 5: the undo of both commits), cut from the file the CTO reads")
    for variant in ("live", "chain"):
        one_variant(L, tmp, variant, blockA, blockB, blockU)


def one_variant(L, tmp, variant, blockA, blockB, blockU):
    tag = f"[{variant} map]"
    name = f"exempt-{variant}"
    root, home = WORK / name, WORK / (name + "-home")
    wtmp = WORK / (name + "-tmp")
    for d in (root, home, wtmp):
        if d.exists():
            subprocess.run(["chmod", "-R", "u+w", str(d)], check=False)
            shutil.rmtree(d)
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
        r = git(*args, ok=(0,))
        return r.stdout.strip()

    def ap(step):
        return run(["bash", str(root / BREL / "apply.sh"), step], env=env(), cwd=str(root))

    def block(text):
        return run(["bash", "-ec", text.replace(REPO_STR, str(root))], env=env(), cwd="/")

    mp = root / MAP_REL

    def msha():
        return sha(mp)[:12] if mp.is_file() else "none"

    def w101():
        r = run(["bash", str(HEAVY), "python3", "-m", "pytest", "tests/acceptance/W1-01", "-q", "-p", "no:cacheprovider", "-o", "tmp_path_retention_policy=failed", "--no-header"],
                env=env(PYTHONUSERBASE=str(HOME_REAL / ".local"), PYTHONPATH=str(root / "src"), TMPDIR=str(wtmp)), cwd=str(root), timeout=2400)
        summ = [l for l in r.stdout.splitlines() if re.match(r"^\d+ (passed|failed)", l)]
        s = re.sub(r" in [0-9.]+s( \([0-9:]+\))?", "", summ[-1]).strip() if summ else "no summary"
        who = re.findall(r"^E +([0-9a-f]{12})$", r.stdout, re.M)
        return r.returncode, s, who

    # ---- set-up
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(REPO), str(root)], check=True)
    home.mkdir()
    shutil.copy2(HOME_REAL / ".gitconfig", home / ".gitconfig")
    op = home / "gov-os-operator"
    shutil.copytree(LIVE_INST, op / "install", ignore=shutil.ignore_patterns("__pycache__"))
    for d in ("log", "queue", "acts", "wall"):
        (op / d).mkdir(parents=True, exist_ok=True)
    shutil.copytree(BUNDLE, root / BREL)
    lst = [l.split("|") for l in (BUNDLE / "list.txt").read_text().splitlines()]
    four = sorted(p for r_, p, b, a in lst if r_ == "repo")
    old_ap = sha(op / "install/APPROVED")
    chain_ok = True
    if variant == "chain":
        for bdir, m8, leaves in CHAIN:
            chain_ok &= sha(bdir / "manifest.json").startswith(m8)
            r = run(["bash", str(bdir / "apply.sh"), "apply"], env=env(), cwd=str(root))
            chain_ok &= r.returncode == 0 and msha() == leaves
            git("add", MAP_REL, ok=(0,))
            git("commit", "-q", "-m", f"rehearsal: {bdir.name} (the chain, committed)", "--trailer", "Role: operator", ok=(0,))
        L.case(chain_ok and msha() == CHAIN_MAP[:12],
               f"{tag} the chain applied by its own bundles' apply.sh in order and committed (manifests e8020292, b8df21d8, 9a945c99): the map is d50884e3633e")
    want_before = LIVE_MAP if variant == "live" else CHAIN_MAP
    base = out("rev-parse", "HEAD")
    L.case(sha(mp) == want_before and out("status", "--porcelain") == "", f"{tag} the clone's map is the allowed before ({want_before[:12]}) and the clone is clean")
    r = ap("check")
    L.case(r.returncode == 0 and "ready to apply" in r.stdout, f"{tag} apply.sh check: exit 0, ready to apply ({r.returncode})")
    rc, s, who = w101()
    base_summary = s
    L.case(rc == 0 and "failed" not in s, f"{tag} W1-01 before the ACT's commit: green ({s})")

    # ---- the exempt step refuses before the first commit
    h0 = msha()
    r = ap("exempt")
    L.case(r.returncode == 3 and "HEAD is not the ACT's commit" in r.stderr and msha() == h0 and out("status", "--porcelain") == "",
           f"{tag} exempt before the first commit: exit 3, HEAD is not the ACT's commit, the map and the tree untouched ({r.returncode})")

    # ---- block A: apply, verify, the first commit (as the package prints it)
    a = block(blockA)
    c1 = out("rev-parse", "HEAD")
    L.case(a.returncode == 0 and "state applied" in a.stdout and "verify: every listed file is the after" in a.stdout and c1 != base,
           f"{tag} section 0's first block run as printed: exit {a.returncode}, applied, verified, committed" + ("" if a.returncode == 0 else f" ({a.stderr.strip()[-120:]})"))
    changed = sorted(out("diff-tree", "--no-commit-id", "--name-only", "-r", c1).split())
    trailers = out("log", "-1", "--format=%(trailers:only,unfold,separator=; )", c1)
    L.case(changed == four and "Role: owner" in trailers and out("rev-list", "--parents", "-n", "1", c1).count(" ") == 1 and out("status", "--porcelain") == "",
           f"{tag} the first commit: one parent, Role: owner, exactly the four repository paths, the tree clean afterwards")
    # the control: red without the entry
    rc, s, who = w101()
    L.case(rc != 0 and s.startswith("1 failed") and who == [c1[:12]],
           f"{tag} CONTROL, W1-01 after the first commit and before the entry: red, the one failure names the first commit and no other ({s})")
    r = ap("exempt-verify")
    L.case(r.returncode == 3 and msha() == h0, f"{tag} exempt-verify before the exempt step: exit 3 (the entry is not there) ({r.returncode})")

    # ---- block B: exempt, exempt-verify, the second commit
    b = block(blockB)
    c2 = out("rev-parse", "HEAD")
    L.case(b.returncode == 0 and f"exempt: added the entry for {c1[:12]}" in b.stdout and "exempt-verify: the map is the allowed before" in b.stdout and c2 != c1,
           f"{tag} section 0's second block run as printed: exit {b.returncode}, entry added, verified, committed" + ("" if b.returncode == 0 else f" ({b.stderr.strip()[-120:]})"))
    subj = out("log", "-1", "--format=%s", c2)
    tr2 = out("log", "-1", "--format=%(trailers:only,unfold,separator=; )", c2)
    L.case(subj == f"ACT-OPERATOR-HOURS-2: acceptance_exemptions lists its own commit {c1[:12]} (DEC-1136 (2))" and out("rev-parse", f"{c2}^") == c1
           and "Task: DAEO-sdxk" in tr2 and "Implements: DEC-1136, DEC-1141" in tr2 and "Role: owner" in tr2,
           f"{tag} the second commit: on the first, its subject names the first's 12 digits, trailers Task, Implements (DEC-1136, DEC-1141), Role: owner")
    L.case(out("diff-tree", "--no-commit-id", "--name-only", "-r", c2) == MAP_REL and out("diff", "--numstat", c1, c2).split("\t")[:2] == ["2", "0"],
           f"{tag} the second commit changes the path map only: 2 lines added, 0 removed")
    mode_ok = stat.S_IMODE(mp.stat().st_mode) == 0o644 and out("ls-tree", c2, MAP_REL).startswith("100644")
    stray = [p.name for p in (root / "governance/project").iterdir() if "act-operator-hours-2" in p.name]
    L.case(mode_ok and not stray and out("status", "--porcelain") == "", f"{tag} the map's mode is kept (644), no temporary file beside it, the tree is clean")
    old = yaml.safe_load(out("show", f"{c1}:{MAP_REL}"))
    new = yaml.safe_load(mp.read_text())
    entry = {"commit": c1, "decision": "DEC-1141"}
    L.case(new["acceptance_exemptions"] == old["acceptance_exemptions"] + [entry] and {k: v for k, v in new.items() if k != "acceptance_exemptions"} == {k: v for k, v in old.items() if k != "acceptance_exemptions"},
           f"{tag} the map parses; acceptance_exemptions is the old list plus the one entry (the full id, DEC-1141) at the end; every other key is equal")
    rc, s, who = w101()
    L.case(rc == 0 and s == base_summary, f"{tag} W1-01 after the second commit: green, the same as before the ACT ({s})")
    ol = run([PIN_PY, "-I", "-c", "import sys,yaml; from pathlib import Path; from gov.close import gates; s=yaml.safe_load(open('governance/project/path-map.yaml')); "
              f"print('{c1}' in gates.owner_listed(Path('.'), s))"], env=env(PYTHONPATH=str(root / "src")), cwd=str(root))
    L.note(f"information, not a gate: the close's gate (h) reader `gates.owner_listed` counts the first commit as owner-listed: {ol.stdout.strip() or ol.stderr.strip()[-80:]} "
           "(it asks that the entry's decision text in the register names the commit by 8 or more digits; DEC-1141 cannot name an id that does not exist yet; W1-01 reads the list by full id and decision shape only)")

    # ---- the steps after the second commit
    snap = (msha(), out("rev-parse", "HEAD"))
    r = ap("exempt")
    L.case(r.returncode == 0 and "already in place" in r.stdout and (msha(), out("rev-parse", "HEAD")) == snap,
           f"{tag} exempt run again after the second commit: a no-op, exit 0, \"already in place\", the map and HEAD untouched ({r.returncode})")
    r = ap("exempt-verify")
    L.case(r.returncode == 0 and "plus exactly the entry" in r.stdout, f"{tag} exempt-verify after the second commit: exit 0 (also the committed map) ({r.returncode})")
    r = ap("exempt-undo")
    L.case(r.returncode == 3 and "is committed" in r.stderr and (msha(), out("rev-parse", "HEAD")) == snap, f"{tag} exempt-undo after the second commit: refused, exit 3, nothing touched ({r.returncode})")

    # ---- the undo of both commits, as the package gives it
    u = block(blockU)
    L.case(u.returncode == 0 and out("rev-parse", "HEAD") == base and msha() == want_before[:12] and out("status", "--porcelain") == "",
           f"{tag} the undo of both commits (the package's block): exit {u.returncode}, HEAD is the head before the ACT, the map is the allowed before, the tree is clean" + ("" if u.returncode == 0 else f" ({u.stderr.strip()[-100:]})"))
    L.case(sha(op / "install/APPROVED") == old_ap and ap("check").returncode == 0, f"{tag} after that undo the install's APPROVED is the old one and apply.sh check says ready again")

    # ---- planted cases, from the head before the ACT
    def make_c1():
        r = ap("apply")
        assert r.returncode == 0, r.stderr
        git("add", *four, ok=(0,))
        git("commit", "-q", "-m", "ACT-OPERATOR-HOURS-2: G9 holds only while the night hold is on (DEC-1141 (6))", "--trailer", "Task: DAEO-sdxk", "--trailer", "Implements: DEC-1141", "--trailer", "Role: owner", ok=(0,))
        return out("rev-parse", "HEAD")

    def undo_to(rev):
        git("reset", "-q", "--hard", rev, ok=(0,))
        git("clean", "-q", "-fd", "--", "tests", "governance", ok=(0,))

    c1 = make_c1()
    h1 = msha()
    # run twice
    r1 = ap("exempt")
    after1 = sha(mp)
    r2 = ap("exempt")
    L.case(r1.returncode == 0 and r2.returncode == 0 and "already in place" in r2.stdout and sha(mp) == after1,
           f"{tag} PLANTED, exempt run twice before the second commit: the first adds the entry, the second is a no-op (exit 0, \"already in place\"), the map byte for byte the same")
    r = ap("exempt-undo")
    L.case(r.returncode == 0 and msha() == h1 and out("status", "--porcelain") == "", f"{tag} exempt-undo before the second commit: the entry taken out, the map is the allowed before again, the tree clean ({r.returncode})")
    r = ap("exempt-undo")
    L.case(r.returncode == 0 and "nothing to do" in r.stdout and msha() == h1, f"{tag} exempt-undo again: a no-op, exit 0 ({r.returncode})")
    r = ap("exempt")
    L.case(r.returncode == 0 and "added the entry" in r.stdout, f"{tag} exempt again after the undo: adds the entry ({r.returncode})")
    git("checkout", "-q", "--", MAP_REL, ok=(0,))
    # another HEAD
    def refuses(label, expect_text=None, expect_rc=3, keep_map=True):
        before = (msha(), out("rev-parse", "HEAD"))
        r = ap("exempt")
        ok = r.returncode == expect_rc and (expect_text is None or expect_text in r.stderr)
        if keep_map:
            ok = ok and msha() == before[0]
        stray = [p.name for p in (root / "governance/project").iterdir() if "act-operator-hours-2" in p.name]
        L.case(ok and not stray, f"{tag} PLANTED, exempt refuses {label}: exit {expect_rc}{', ' + expect_text if expect_text else ''}, the map untouched, no temporary file ({r.returncode}{'' if expect_rc == 5 else '; ' + r.stderr.strip()[:90]})")

    git("commit", "-q", "--allow-empty", "-m", "an unrelated commit", "--trailer", "Role: owner", ok=(0,))
    refuses("on another HEAD (an unrelated commit on top of the ACT's)", "HEAD is not the ACT's commit")
    undo_to(c1)
    git("commit", "-q", "--amend", "-m", "ACT-OPERATOR-HOURS-2: G9 (as an operator commit)", "--trailer", "Role: operator", ok=(0,))
    refuses("when the ACT's commit is not Role: owner", "no single trailer Role: owner")
    undo_to(c1)
    git("commit", "-q", "--amend", "-m", "G9 holds only while the night hold is on", "--trailer", "Role: owner", ok=(0,))
    refuses("when the subject does not start ACT-OPERATOR-HOURS-2:", "its subject does not start")
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
    git("branch", "-q", "plant-side", f"{c1}~1", ok=(0,))
    git("checkout", "-q", "plant-side", ok=(0,))
    git("commit", "-q", "--allow-empty", "-m", "side", ok=(0,))
    git("checkout", "-q", "-", ok=(0,))
    git("reset", "-q", "--hard", f"{c1}~1", ok=(0,))
    git("merge", "-q", "--no-ff", "plant-side", "-m", "ACT-OPERATOR-HOURS-2: a merge\n\nRole: owner", ok=(0,))
    refuses("when HEAD is a merge commit", "no parent or has two")
    undo_to(c1)
    git("branch", "-q", "-D", "plant-side", ok=(0,))
    # maps
    with open(mp, "a") as f:
        f.write("# planted: the map changed\n")
    refuses("on a map that is neither allowed before (a changed line, not committed)", "neither allowed before")
    git("checkout", "-q", "--", MAP_REL, ok=(0,))
    other = (CHAIN[-1][0] / "after/repo" / MAP_REL) if variant == "live" else None
    if variant == "chain":
        other = tmp / "live-map-copy.yaml"
        other.write_bytes(subprocess.run(["git", "-C", str(root), "show", f"{base}~3:{MAP_REL}"], capture_output=True).stdout)
        assert sha(other) == LIVE_MAP
    shutil.copy2(other, mp)
    refuses(f"on the other allowed before when it is not committed ({sha(other)[:12]} in the working tree, HEAD has {h1})", "has changes that are not committed")
    git("checkout", "-q", "--", MAP_REL, ok=(0,))
    mp.rename(str(mp) + ".real")
    os.symlink(str(mp) + ".real", mp)
    refuses("on a map that is a link", "missing or a link")
    mp.unlink()
    os.rename(str(mp) + ".real", mp)
    git("checkout", "-q", "--", MAP_REL, ok=(0,))
    L.case(out("status", "--porcelain") == "" and msha() == h1, f"{tag} the planted states are undone: the clone is clean again at the first commit")
    os.chmod(root / "governance/project", 0o555)
    try:
        refuses("when the map's folder is not writable (nothing can be written)", None, expect_rc=5)
    finally:
        os.chmod(root / "governance/project", 0o755)
    # a map that is neither before and is committed: the chain half applied
    undo_to(c1)
    git("reset", "-q", "--hard", base, ok=(0,))
    half = CHAIN[0] if variant == "live" else CHAIN[1]
    shutil.copy2(half[0] / "after/repo" / MAP_REL, mp)
    assert msha() == half[2]
    git("add", MAP_REL, ok=(0,))
    git("commit", "-q", "-m", "rehearsal: a half-applied chain, committed", "--trailer", "Role: operator", ok=(0,))
    make_c1()
    refuses(("on the map ACT-EXAMIN-SETS-1 alone leaves" if variant == "live" else "on the map the chain leaves without ACT-PATHMAP-EXP-1") + f" ({half[2]}, committed, so the tree is clean)",
            "neither allowed before")
    # the undo after the first commit alone (no exemption yet), as section 5 gives it
    undo_to(base)
    c1 = make_c1()
    git("reset", "-q", "--keep", "HEAD~1", ok=(0,))
    r = ap("undo")
    L.case(r.returncode == 0 and out("rev-parse", "HEAD") == base and msha() == want_before[:12] and sha(op / "install/APPROVED") == old_ap and out("status", "--porcelain") == "" and ap("check").returncode == 0,
           f"{tag} the undo after the first commit alone (`git reset --keep HEAD~1`, then `apply.sh undo`): HEAD is the head before the ACT, the install's APPROVED the old one, the tree clean, check ready ({r.returncode})")
    # verify refuses a misplaced or altered entry
    undo_to(base)
    c1 = make_c1()
    r = ap("exempt")
    good = mp.read_text()
    lines = good.splitlines(keepends=True)
    i = next(k for k, l in enumerate(lines) if l.startswith(f'  - commit: "{c1}"'))
    moved = lines[:i - 2] + lines[i:i + 2] + lines[i - 2:i] + lines[i + 2:]
    mp.write_text("".join(moved))
    r = ap("exempt-verify")
    L.case(r.returncode == 3 and "not at the end" in r.stderr, f"{tag} PLANTED, exempt-verify on an entry moved up one place: exit 3 ({r.returncode}; {r.stderr.strip()[:80]})")
    mp.write_text(good.replace("decision: DEC-1141  # ACT-OPERATOR-HOURS-2's", "decision: DEC-1140  # ACT-OPERATOR-HOURS-2's"))
    r = ap("exempt-verify")
    L.case(r.returncode == 3, f"{tag} PLANTED, exempt-verify on an entry whose decision was changed: exit 3 ({r.returncode})")
    mp.write_text(good + "# planted: another line\n")
    r = ap("exempt-verify")
    L.case(r.returncode == 3, f"{tag} PLANTED, exempt-verify on a map with another changed line: exit 3 ({r.returncode})")
    mp.write_text(good)
    r = ap("exempt-verify")
    L.case(r.returncode == 0, f"{tag} PLANTED, the control: the good map verifies again, exit 0 ({r.returncode})")
    # round 1's refusals are untouched by stage 2: check, verify and undo of stage 1 in this clone's state
    git("commit", "-q", "-a", "-m", "ACT-OPERATOR-HOURS-2: acceptance_exemptions lists its own commit (rehearsal)", "--trailer", "Role: owner", ok=(0,))
    r = ap("check")
    L.case(r.returncode == 3 and "already applied" in r.stderr, f"{tag} stage 1 after both commits: check says already applied (exit 3), as in round 1 ({r.returncode})")
    r = ap("verify")
    L.case(r.returncode == 0, f"{tag} stage 1 after both commits: verify exit 0 ({r.returncode})")
