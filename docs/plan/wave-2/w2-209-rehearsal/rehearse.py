#!/usr/bin/env python3
"""The W2-209 rehearsal (slice (a)): a patch release on a SCRATCH clone of this repository and a SCRATCH $HOME.

    PYTHONPATH=<worktree>/src python3 docs/plan/wave-2/w2-209-rehearsal/rehearse.py <evidence folder> [--keep]

It never touches the real ~/.local/bin/gov, the real pins, the real `w2/integrate` or any remote: every `gov` call is a
child process with HOME = the scratch home, working in the scratch clone; the real link's target is read before and
after and must be equal. The clone's `origin` is removed, so nothing can be pushed or fetched.

Cases (each writes a line of evidence):
  A. a planted patch (a `Fix:` commit under a ticket closed at the scratch release, a `Class: Q` chore, the version commit) passes
     G1: `gov release 0.9.1 --patch --check` answers patch;
  B. each planted bigger change (a docs/contract edit, EMERGENCY-2, a closed feature ticket, a new command, a new
     schema, a feature commit with no trailer) is refused by the rule's name;
  C. with a planted green record, G3 stood in, the authority file switched on IN THE SCRATCH CLONE ONLY, the cut writes
     the record, tags and merges, and the re-pin switches the scratch link; the push stand-in records one text;
  D. a planted failing post-pin check (a hook of the candidate that exits 3) rolls back, marks the release burned,
     makes one push, leaves the registry untouched; rollback.sh of case C restores the previous link.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[4]
# Scratch version numbers (the real next release is not this rehearsal's to name): the scratch clone is made at THIS
# branch's head (current code, so the post-pin search reads a current store), a scratch release N is built on it, and the
# planted range sits on N.
VERSION, NEXT = "0.9.0", "0.9.1"
OWNER = "Decided-by: owner (standing, DEC-1223)"
log: list[dict] = []


def say(case: str, ok: bool, what: str, **more) -> None:
    log.append({"case": case, "ok": ok, "what": what, **more})
    print(f"[{'ok' if ok else 'FAIL'}] {case}: {what}", flush=True)


def run(argv, cwd, env=None, check=True, inp=None):
    done = subprocess.run([str(a) for a in argv], cwd=cwd, env=env, capture_output=True, text=True, input=inp)
    if check and done.returncode:
        raise RuntimeError(f"{argv} in {cwd}: {done.returncode}\n{done.stdout[-1500:]}\n{done.stderr[-1500:]}")
    return done


def git(clone, *args, check=True, inp=None):
    return run(["git", "-C", clone, "-c", "user.name=Rehearsal", "-c", "user.email=rehearsal@example.invalid",
                "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false", *args], clone, check=check, inp=inp).stdout


def commit(clone, message, trailers, *paths):
    git(clone, "add", "-A")
    body = message + "\n\n" + "\n".join(trailers) + "\n"
    git(clone, "commit", "-q", "-m", body)
    return git(clone, "rev-parse", "HEAD").strip()


STORE = Path("/home/usain/gov-os-worktrees/W2-00-store/.gov-runtime")


def give_store(clone: Path) -> None:
    """The post-pin search needs a store: a plain file copy of the existing one (no rebuild; `.gov-runtime/` is ignored)."""
    (clone / ".gov-runtime").mkdir(exist_ok=True)
    for name in ("store.db", "query-vector-cache.db"):
        shutil.copy(STORE / name, clone / ".gov-runtime" / name)


def gov_env(home: Path, role: str | None = "orchestrator") -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GOV_", "PYTHONPATH"))}
    env.update({"HOME": str(home), "PYTHONUSERBASE": str(Path(os.environ.get("PYTHONUSERBASE") or Path.home() / ".local")), "PYTHONPATH": str(WORKTREE / "src"), "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_AUTHOR_NAME": "Rehearsal", "GIT_AUTHOR_EMAIL": "rehearsal@example.invalid",
                "GIT_COMMITTER_NAME": "Rehearsal", "GIT_COMMITTER_EMAIL": "rehearsal@example.invalid"})
    if role:
        env["GOV_ROLE"] = role
    return env


def gov(clone, home, *args, role="orchestrator"):
    return run([sys.executable, "-m", "gov.cli.main", *args, "--json"], clone, gov_env(home, role), check=False)


def answer(done) -> dict:
    try:
        return json.loads(done.stdout)
    except ValueError:
        return {"ok": False, "raw": (done.stdout + done.stderr)[-600:]}


def seam(clone, home, code: str) -> subprocess.CompletedProcess:
    return run([sys.executable, "-c", code], clone, gov_env(home), check=False)


def real_link() -> str:
    link = Path.home() / ".local" / "bin" / "gov"
    return os.path.realpath(link) if link.exists() or link.is_symlink() else "(none)"


def closed_tickets(clone, ref) -> list[str]:
    names = git(clone, "ls-tree", "--name-only", ref, ".tickets/").split()
    out = []
    for name in names:
        text = git(clone, "show", f"{ref}:{name}", check=False)
        head = text.split("---")[1] if text.startswith("---") else ""
        if "\nstatus: closed" in "\n" + head:
            out.append(Path(name).stem)
    return out


def scratch_home(root: Path, clone: Path, base: str) -> Path:
    """A scratch home with one live pin (the base release's wheel) and its link."""
    from gov import release

    home = root / "home"
    share, bindir = home / ".local" / "share" / "gov-os", home / ".local" / "bin"
    bindir.mkdir(parents=True)
    commit_ = git(clone, "rev-parse", base).strip()
    wheel = release._wheel(clone, commit_, keep=root)
    pin = share / f"pin-{commit_[:12]}"
    share.mkdir(parents=True)
    run([sys.executable, "-m", "venv", "--system-site-packages", pin], root)
    run([pin / "bin" / "python", "-m", "pip", "install", "-q", "--no-deps", "--no-index", wheel["path"]], root)
    (bindir / "gov").symlink_to(pin / "bin" / "gov")
    return home


def main() -> int:
    evidence = Path(sys.argv[1]).resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    keep = "--keep" in sys.argv
    before_link = real_link()
    root = Path(tempfile.mkdtemp(prefix="w2-209-rehearsal-"))
    print(f"scratch: {root}", flush=True)
    clone = root / "clone"
    run(["git", "clone", "-q", "--no-hardlinks", str(WORKTREE), clone], root)
    git(clone, "remote", "remove", "origin")
    give_store(clone)
    git(clone, "checkout", "-q", "-B", "w2/integrate")
    pyproject = clone / "pyproject.toml"
    import re
    pyproject.write_text(re.sub(r'(?m)^version = "[^"]*"', f'version = "{VERSION}"', pyproject.read_text(encoding="utf-8"), 1),
                         encoding="utf-8")
    commit(clone, f"SCRATCH: version {VERSION}", ["Class: C", "Role: orchestrator"])
    built = seam(clone, root, f"from pathlib import Path; from gov import release; print(release.build(Path('.'), '{VERSION}'))")
    assert built.returncode == 0, built.stderr[-1500:]
    commit(clone, f"SCRATCH: the record of release {VERSION}", ["Class: C", "Role: orchestrator"])
    git(clone, "tag", "-a", f"v{VERSION}", "-m", f"scratch release {VERSION}")
    base_tag = git(clone, "rev-parse", f"v{VERSION}^{{commit}}").strip()
    closed = closed_tickets(clone, base_tag)
    assert closed, "no closed ticket at the base release"
    owning = closed[0]

    # --- the planted range: one fix, one chore, the version commit -------------------------------------------------
    src_file = clone / "src" / "gov" / "release" / "__init__.py"
    src_file.write_text(src_file.read_text(encoding="utf-8") + "\n# planted fix\n", encoding="utf-8")
    commit(clone, "Fix a planted defect under a closed ticket", ["Class: F", f"Task: {owning}", "Fix: the planted defect",
                                                                 "Role: engineer"])
    (clone / "src" / "gov" / "release" / "command.py").write_text(
        (clone / "src" / "gov" / "release" / "command.py").read_text(encoding="utf-8") + "\n# planted chore\n",
        encoding="utf-8")
    commit(clone, "A planted chore", ["Class: Q", "Role: orchestrator"])
    patch_tip = git(clone, "rev-parse", "HEAD").strip()

    def version_commit():
        pyproject = clone / "pyproject.toml"
        pyproject.write_text(pyproject.read_text(encoding="utf-8").replace(f'version = "{VERSION}"',
                                                                           f'version = "{NEXT}"', 1), encoding="utf-8")
        return commit(clone, f"Version {NEXT}", ["Class: C", "Role: orchestrator"])

    version_commit()
    c_patch = git(clone, "rev-parse", "HEAD").strip()
    git(clone, "branch", "planted-patch", c_patch)

    home = scratch_home(root, clone, base_tag)

    # --- A: the patch passes G1 ---------------------------------------------------------------------------------------
    got = answer(gov(clone, home, "release", NEXT, "--patch", "--check"))
    result = got.get("result") or {}
    say("A", got.get("ok") is True and result.get("kind") == "patch", "the planted patch passes G1 (--check says patch)",
        rules={k: v["pass"] for k, v in (result.get("rules") or {}).items()}, answer=got.get("raw"))
    tree_before = git(clone, "status", "--porcelain", "--untracked-files=all")
    say("A", tree_before == "", "--check wrote nothing (the tree is clean)")

    # --- B: each planted bigger change is refused by name ---------------------------------------------------------
    open_ticket = None
    for name in git(clone, "ls-tree", "--name-only", base_tag, ".tickets/").split():
        if name not in {f".tickets/{t}.md" for t in closed}:
            open_ticket = name
            break

    def plant_contract():
        p = clone / "docs" / "contract" / "PLANTED.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("planted\n")

    def plant_emergency():
        p = clone / "docs" / "emergency-2" / "EMERGENCY-2.md"
        p.write_text(p.read_text(encoding="utf-8") + "\nplanted\n", encoding="utf-8")

    def plant_ticket():
        p = clone / ".tickets" / "DAEO-zzzz.md"
        p.write_text("---\nid: DAEO-zzzz\nstatus: closed\n---\nplanted feature ticket\n")

    def plant_command():
        p = clone / "src" / "gov" / "planted" / "command.py"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('"""planted"""\n')

    def plant_schema():
        p = clone / "template" / "governance" / "kernel" / "schemas" / "planted.schema.json"
        p.write_text("{}\n")

    def plant_feature():
        p = clone / "src" / "gov" / "accept" / "runner.py"
        p.write_text(p.read_text(encoding="utf-8") + "\n# planted feature\n", encoding="utf-8")

    cases = [("docs/contract edit", plant_contract, "P2", ["Class: Q"]),
             ("EMERGENCY-2 edit", plant_emergency, "P2", ["Class: Q"]),
             ("a closed feature ticket", plant_ticket, "P3", ["Class: Q"]),
             ("a new command", plant_command, "P4", ["Class: Q"]),
             ("a new kit schema", plant_schema, "P5", ["Class: Q"]),
             ("a feature commit with no trailer", plant_feature, "P3", ["Role: engineer"])]
    for label, plant, rule, trailers in cases:
        git(clone, "checkout", "-q", "-B", "planted-bigger", patch_tip)
        plant()
        commit(clone, f"planted: {label}", trailers)
        version_commit()
        got = answer(gov(clone, home, "release", NEXT, "--patch", "--check"))
        details = (got.get("error") or {}).get("details") or {}
        named = details.get("failed")
        say("B", got.get("ok") is False and details.get("kind") == "bigger" and named is not None and rule in named,
            f"{label}: refused as bigger, naming {rule}", failed=named,
            detail={r: details.get("rules", {}).get(r, {}).get("detail") for r in (named or [])})
    git(clone, "checkout", "-q", "planted-patch")
    git(clone, "branch", "-q", "-D", "planted-bigger")

    # --- C: the cut and the re-pin in the scratch home -------------------------------------------------------------------
    git(clone, "checkout", "-q", "-B", "w2/integrate", c_patch)
    authority = clone / "governance" / "project" / "release-authority.yaml"
    # the base release has no authority file: the scratch gets the real one's bytes (off), then switches it on
    committed_off = (WORKTREE / "governance" / "project" / "release-authority.yaml").read_text(encoding="utf-8")
    authority.write_text(committed_off, encoding="utf-8")
    authority.write_text(committed_off.replace("patch_releases: off", "patch_releases: on"), encoding="utf-8")
    commit(clone, "SCRATCH ONLY: the authority file on (the real file stays off; the CTO turns it on)",
           [OWNER, "Role: orchestrator", "Task: decision-record"])
    c = git(clone, "rev-parse", "HEAD").strip()
    tree = git(clone, "rev-parse", f"{c}^{{tree}}").strip()
    suite = root / "NR-planted.json"
    suite.write_text(json.dumps({"branch": "w2/integrate", "head": c, "tree": tree, "scope": "full", "verdict": "green",
                                 "optin": ["weekly"], "failures": [], "tests_run": {"passed": 1, "failed": 0}}) + "\n")
    pushes = root / "pushes.txt"
    pusher = root / "push.sh"
    pusher.write_text(f'#!/bin/sh\nprintf "%s\\n" "$*" >> {pushes}\n')
    pusher.chmod(0o755)
    registry_before = (clone / "governance" / "project" / "tool-registry.yaml").read_bytes()
    code = ("import json, pathlib; from gov import release\n"
            f"r = release._patch_test(pathlib.Path('.'), '{NEXT}', suite='{suite}', push='{pusher}', "
            "rehearse=lambda root, c, v, kept: {'verdict': 'READY', 'reasons': [], 'standin': True})\n"
            "print(json.dumps(r, default=str))\n")
    done = seam(clone, home, code)
    res = json.loads(done.stdout) if done.returncode == 0 and done.stdout.strip() else {}
    say("C", done.returncode == 0 and res.get("repin", {}).get("status") == "ok",
        "the cut with a planted green record and G3 stood in cuts, tags, merges and re-pins in the scratch home",
        exit=done.returncode, repin=res.get("repin"), stderr=done.stderr[-800:])
    link = Path(home / ".local" / "bin" / "gov")
    say("C", f"pin-{c[:12]}" in os.path.realpath(link) if res else False, "the scratch link names the new pin",
        link=os.path.realpath(link))
    folder = clone / "docs" / "releases" / NEXT
    say("C", sorted(p.name for p in folder.iterdir()) == ["NOTE.md", "gates.json", "kind.json", "manifest.json",
                                                         "manifest.sha256", "suite.json"] if folder.is_dir() else False,
        "the record folder holds the six files", files=sorted(p.name for p in folder.iterdir()) if folder.is_dir() else None)
    tag_kind = git(clone, "cat-file", "-t", f"refs/tags/v{NEXT}", check=False).strip()
    parents = git(clone, "rev-list", "--parents", "-n1", f"v{NEXT}^{{commit}}", check=False).split()
    say("C", tag_kind == "tag" and parents[1:] == [c], "the tag v0.9.1 is annotated and its parent is C",
        tag_kind=tag_kind, parents=parents)
    trailers = git(clone, "log", "-1", "--format=%(trailers:key=Role,valueonly)|%(trailers:key=Decided-by,valueonly)|"
                   f"%(trailers:key=Task,valueonly)", f"v{NEXT}^{{commit}}", check=False).strip()
    say("C", "orchestrator" in trailers and "owner (standing, DEC-1223)" in trailers and "release" in trailers,
        "the record commit's trailers are the orchestrator's with the owner's standing decision", trailers=trailers)
    lines = pushes.read_text().splitlines() if pushes.exists() else []
    say("C", len(lines) == 1 and len(lines[0]) <= 190 and NEXT in lines[0] and "rollback.sh" in lines[0],
        "one push of at most 190 characters carrying the version and the rollback line", pushes=lines,
        length=[len(x) for x in lines])
    reg = git(clone, "log", "-1", "--format=%s|%(trailers:key=Decided-by,valueonly)", "--", "governance/project/tool-registry.yaml").strip()
    say("C", (clone / "governance" / "project" / "tool-registry.yaml").read_bytes() != registry_before,
        "the registry entry was committed", commit=reg)
    note = (folder / "NOTE.md").read_text(encoding="utf-8") if folder.is_dir() else ""
    say("C", "rollback.sh" in note and "weekly" in note, "NOTE.md holds the evidence and the rollback line")
    (evidence / "NOTE.0.9.1.scratch.md").write_text(note, encoding="utf-8")
    shutil.copy(folder / "gates.json", evidence / "gates.0.9.1.scratch.json")
    shutil.copy(folder / "kind.json", evidence / "kind.0.9.1.scratch.json")
    shutil.copy(pushes, evidence / "push-text.0.9.1.scratch.txt")
    share = home / ".local" / "share" / "gov-os"
    say("C", (share / "rollback.sh").is_file() and (share / "repin.json").is_file(),
        "rollback.sh and repin.json are written", repin=json.loads((share / "repin.json").read_text())
        if (share / "repin.json").is_file() else None)
    authority_now = authority.read_text(encoding="utf-8")
    say("C", authority_now.replace("patch_releases: on", "patch_releases: off") == committed_off,
        "the cut did not write the authority file")
    old_pin_target = json.loads((share / "repin.json").read_text()).get("old_pin") if (share / "repin.json").is_file() else None

    # rollback.sh restores the previous link and burns the release
    sh = run(["bash", share / "rollback.sh"], clone, {"HOME": str(home), "PATH": "/usr/bin:/bin"}, check=False)
    after = os.path.realpath(link)
    say("C", sh.returncode == 0 and f"pin-{c[:12]}" not in after and (share / "burned").read_text().split() == [NEXT],
        "rollback.sh run in a plain shell with no gov on its path puts the previous link back and burns the release",
        link=after, burned=(share / "burned").read_text().split() if (share / "burned").exists() else None)

    # --- D: a failing post-pin check rolls back and burns --------------------------------------------------------------
    d_clone = root / "clone-d"
    run(["git", "clone", "-q", "--no-hardlinks", str(clone), d_clone], root)
    # start again from the planted patch (the case-C release is not in it), with a hook that exits 3
    git(d_clone, "checkout", "-q", "-B", "w2/integrate", "origin/planted-patch")
    git(d_clone, "tag", "-d", f"v{NEXT}", check=False)
    git(d_clone, "remote", "remove", "origin", check=False)
    give_store(d_clone)
    hook = d_clone / "template" / "governance" / "kernel" / "hooks" / "stop.py"
    hook.write_text("import sys\nsys.exit(3)\n" + hook.read_text(encoding="utf-8"), encoding="utf-8")
    commit(d_clone, "A planted hook that fails", ["Class: Q", "Role: orchestrator"])
    d_authority = d_clone / "governance" / "project" / "release-authority.yaml"
    d_authority.write_text((WORKTREE / "governance" / "project" / "release-authority.yaml").read_text(
        encoding="utf-8").replace("patch_releases: off", "patch_releases: on"), encoding="utf-8")
    commit(d_clone, "SCRATCH ONLY: the authority file on", [OWNER, "Role: orchestrator", "Task: decision-record"])
    d_c = git(d_clone, "rev-parse", "HEAD").strip()
    d_suite = root / "NR-planted-d.json"
    d_suite.write_text(json.dumps({"head": d_c, "tree": git(d_clone, "rev-parse", f"{d_c}^{{tree}}").strip(),
                                   "scope": "full", "verdict": "green", "optin": ["weekly"]}) + "\n")
    home_d = scratch_home(root / "d", d_clone, base_tag) if (root / "d").mkdir() is None else None
    d_pushes = root / "pushes-d.txt"
    d_pusher = root / "push-d.sh"
    d_pusher.write_text(f'#!/bin/sh\nprintf "%s\\n" "$*" >> {d_pushes}\n')
    d_pusher.chmod(0o755)
    d_registry = (d_clone / "governance" / "project" / "tool-registry.yaml").read_bytes()
    old_link = os.path.realpath(home_d / ".local" / "bin" / "gov")
    code = ("import json, pathlib; from gov import release\n"
            f"r = release._patch_test(pathlib.Path('.'), '{NEXT}', suite='{d_suite}', push='{d_pusher}', "
            "rehearse=lambda root, c, v, kept: {'verdict': 'READY', 'reasons': [], 'standin': True})\n"
            "print(json.dumps(r, default=str))\n")
    import time
    started = time.time()
    done = seam(d_clone, home_d, code)
    res = json.loads(done.stdout) if done.returncode == 0 and done.stdout.strip() else {}
    took = time.time() - started
    share_d = home_d / ".local" / "share" / "gov-os"
    repin_json = json.loads((share_d / "repin.json").read_text()) if (share_d / "repin.json").is_file() else {}
    say("D", res.get("repin", {}).get("status") == "rolled_back" and repin_json.get("status") == "rolled_back",
        "a planted failing hook rolls the re-pin back", check=repin_json.get("check"), stderr=done.stderr[-600:])
    say("D", os.path.realpath(home_d / ".local" / "bin" / "gov") == old_link, "the scratch link names the old pin again",
        link=os.path.realpath(home_d / ".local" / "bin" / "gov"), seconds=round(took, 1))
    say("D", (share_d / "burned").exists() and (share_d / "burned").read_text().split() == [NEXT],
        "the release is burned (its tag and record stay)", tag=git(d_clone, "tag", "-l", f"v{NEXT}").strip())
    d_lines = d_pushes.read_text().splitlines() if d_pushes.exists() else []
    say("D", len(d_lines) == 1 and len(d_lines[0]) <= 190 and "NOT pinned" in d_lines[0], "one failure push, at most 190 characters",
        pushes=d_lines)
    say("D", (d_clone / "governance" / "project" / "tool-registry.yaml").read_bytes() == d_registry,
        "no registry commit was made")
    (evidence / "push-text.0.9.1.failed.scratch.txt").write_text("\n".join(d_lines) + "\n", encoding="utf-8")
    again = seam(d_clone, home_d, "import json, pathlib; from gov.release import repin; from pathlib import Path\n"
                 f"print(json.dumps(repin.repin(pathlib.Path('.'), '{NEXT}', Path.home()), default=str))\n")
    stopped = json.loads(again.stdout) if again.returncode == 0 and again.stdout.strip() else {}
    say("D", stopped.get("status") == "stopped" and stopped.get("step") == "burned",
        "a second re-pin of the burned release is refused (stopped at `burned`), the link unchanged",
        answer=stopped, link=os.path.realpath(home_d / ".local" / "bin" / "gov"))

    # --- the real machine is untouched --------------------------------------------------------------------------------
    say("Z", real_link() == before_link, "the real ~/.local/bin/gov link is as before", link=before_link)
    (evidence / "results.json").write_text(json.dumps({"scratch": str(root), "cases": log}, indent=2) + "\n", encoding="utf-8")
    failed = [entry for entry in log if not entry["ok"]]
    print(f"\n{len(log) - len(failed)} of {len(log)} checks ok")
    if not keep:
        shutil.rmtree(root, ignore_errors=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
