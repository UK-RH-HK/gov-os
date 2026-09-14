#!/usr/bin/env python3
"""RV5-B-A05 — source identity (`30` §4.1) under a carrier adversary (review r5 reviewer B, AR-0012). Real Git, scratch only.

Part 1. The canonical content digest as `30` §4.1 and `schemas/release-registration.schema.json` specify it:
        SHA-256 over the sorted lines `<mode> <path> <SHA-256 of blob bytes>` of the whole tree. Git permits a newline in a
        path. Two trees with different file sets are constructed whose line sequences are byte-identical, so their
        canonical content digests are equal while their Git tree ids differ. Both delimiter readings are computed
        (lines joined with "\n"; every line terminated by "\n"). A build-relevant file (`.cargo/config.toml`) is absent from
        the second tree.
Part 2. What the architect's SRC5 evidence actually hashes: its `content_digest()` is `git archive --format=tar <tree id>`.
        That archive is recomputed at two wall-clock times with the same tree.

Environment: SCRATCH. Output: JSON on stdout.
"""
import hashlib, json, os, re, subprocess, sys, tempfile, time

sys.dont_write_bytecode = True
SCR = os.environ["SCRATCH"]
S = tempfile.mkdtemp(prefix="rv5b-a05-", dir=SCR)
GIT_ENV = {"PATH": "/usr/bin:/bin", "HOME": os.path.join(S, "home"), "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"}
os.makedirs(GIT_ENV["HOME"], exist_ok=True)


def git(args, cwd, inp=None):
    r = subprocess.run(["git"] + args, cwd=cwd, env=GIT_ENV, capture_output=True, input=inp)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode())
    return r.stdout


def make_repo(name, files):
    d = os.path.join(S, name)
    os.makedirs(d)
    git(["init", "-q"], d)
    for p, content in files.items():
        fp = os.path.join(d, p)
        os.makedirs(os.path.dirname(fp) or d, exist_ok=True)
        with open(fp, "wb") as f:
            f.write(content)
    git(["add", "-A"], d)
    git(["commit", "-q", "-m", name], d)
    return d


def tree_entries(repo):
    raw = git(["ls-tree", "-r", "-z", "HEAD"], repo)
    out = []
    for rec in raw.split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        mode, typ, oid = meta.decode().split(" ")
        blob = git(["cat-file", "blob", oid], repo)
        out.append((mode, path.decode("utf-8"), hashlib.sha256(blob).hexdigest()))
    return out


def canonical(entries, terminated):
    lines = sorted(f"{m} {p} {h}" for m, p, h in entries)
    body = "".join(l + "\n" for l in lines) if terminated else "\n".join(lines)
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


CARGO_CFG = b"[build]\nrustflags = [\"-C\", \"overflow-checks=on\"]\n"
LIB = b"pub fn f() {}\n"
h_cfg = hashlib.sha256(CARGO_CFG).hexdigest()
t1 = make_repo("tree-genuine", {".cargo/config.toml": CARGO_CFG, "src/lib.rs": LIB})
# the second tree: one file whose path swallows the `.cargo/config.toml` line, holding src/lib.rs's bytes
merged_path = f".cargo/config.toml {h_cfg}\n100644 src/lib.rs"
t2 = make_repo("tree-carrier", {merged_path: LIB})
e1, e2 = tree_entries(t1), tree_entries(t2)
part1 = {
    "tree_genuine": {"git_tree_id": git(["rev-parse", "HEAD^{tree}"], t1).decode().strip(), "paths": [p for _, p, _ in e1]},
    "tree_carrier": {"git_tree_id": git(["rev-parse", "HEAD^{tree}"], t2).decode().strip(), "paths": [p for _, p, _ in e2]},
    "canonical_digest_newline_joined": {"genuine": canonical(e1, False), "carrier": canonical(e2, False)},
    "canonical_digest_newline_terminated": {"genuine": canonical(e1, True), "carrier": canonical(e2, True)},
}
part1["verdicts"] = {
    "git_tree_ids_differ": part1["tree_genuine"]["git_tree_id"] != part1["tree_carrier"]["git_tree_id"],
    "file_sets_differ": sorted(part1["tree_genuine"]["paths"]) != sorted(part1["tree_carrier"]["paths"]),
    "carrier_tree_lacks_.cargo/config.toml": ".cargo/config.toml" not in part1["tree_carrier"]["paths"],
    "canonical_digest_equal_joined": part1["canonical_digest_newline_joined"]["genuine"] == part1["canonical_digest_newline_joined"]["carrier"],
    "canonical_digest_equal_terminated": part1["canonical_digest_newline_terminated"]["genuine"] == part1["canonical_digest_newline_terminated"]["carrier"],
}

# Part 2: SRC5's function (evidence/r5/SRC5-source-identity.py content_digest): rev-parse <ref>^{tree}; git archive --format=tar <tree>
tree = git(["rev-parse", "HEAD^{tree}"], t1).decode().strip()
commit = git(["rev-parse", "HEAD"], t1).decode().strip()
a0 = hashlib.sha256(git(["archive", "--format=tar", tree], t1)).hexdigest()
a0b = hashlib.sha256(git(["archive", "--format=tar", tree], t1)).hexdigest()
time.sleep(2.2)
a1 = hashlib.sha256(git(["archive", "--format=tar", tree], t1)).hexdigest()
c0 = hashlib.sha256(git(["archive", "--format=tar", commit], t1)).hexdigest()
time.sleep(1.2)
c1 = hashlib.sha256(git(["archive", "--format=tar", commit], t1)).hexdigest()
part2 = {"src5_function": "sha256(git archive --format=tar <tree id>)", "tree_archive_t0": a0, "tree_archive_t0_again": a0b, "tree_archive_t0_plus_2s": a1,
         "commit_archive_t0": c0, "commit_archive_t0_plus_1s": c1,
         "verdicts": {"tree_archive_digest_changes_with_wall_clock": a0 != a1, "commit_archive_stable_across_time": c0 == c1,
                      "src5_tests_the_specified_canonical_digest": False}}
out = {"probe": "RV5-B-A05 source identity (AR-0012)", "git": subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip(),
       "part1_canonical_digest_path_delimiter": part1, "part2_src5_function_time_dependence": part2}
txt = json.dumps(out, indent=1, sort_keys=True).replace(S, "<scratch>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt))
