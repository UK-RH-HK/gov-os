#!/usr/bin/env python3
"""SRC6 — source identity v2 (`30` §4.1 revision 6; RV5-M4, RV5-B-A05). Real Git, scratch only.

Specified function (`governance-os.source-content-digest/2`), computed from Git objects, never from a working tree or an
archive:
  1. Enumerate the tree of the registered commit recursively (`git ls-tree -r -z --full-tree <commit>`), NUL-separated.
  2. Refuse (`SOURCE_PATH_REFUSED`) any path holding a byte below 0x20 or equal to 0x7f, any path that is not valid UTF-8, any
     entry of mode 160000 (submodule) or of a type other than blob.
  3. For each entry, in ascending byte order of the path: the record
       u64be(len(mode)) || mode || u64be(len(path)) || path || u64be(32) || SHA-256(blob bytes)
     (mode as the ASCII octal string Git reports; a symbolic link's blob is its target).
  4. content_digest = "sha256:" + SHA-256("governance-os.source-content-digest/2\\n" || u64be(number of records) || records).
The registration also records the Git tree object id of the commit (`source.git_tree`), so either identity alone detects a
different tree.

Tests
  T1  Reviewer B's two-tree construction (RV5-B-A05, re-typed): the revision-5 line encoding gives equal digests (reproduced);
      v2 refuses the carrier tree; with the refusal disabled (encoding alone), the two v2 digests differ.
  T2  Delimiter and prefix variants without control characters (space in path, path equal to another entry's prefix, empty
      file versus missing file): every pair differs.
  T3  Mode and link sensitivity: executable bit and symbolic-link target change the digest; commit metadata does not.
  T4  Determinism: two independent clones (`git clone --no-local`), computed at two wall-clock times, and a second process run
      give the same digest. The output holds no time-dependent value, so two runs are byte-identical.
Attribution: the carrier-tree construction follows `4.1.6-review-r5/B-trust-security/evidence/probes/RV5-B-A05-source-identity.py`
(AR-0012); code re-typed.
Environment: SCRATCH. Output: JSON on stdout (scratch paths elided). Deterministic.
"""
import hashlib, json, os, re, struct, subprocess, sys, tempfile, time

sys.dont_write_bytecode = True
SCR = os.environ["SCRATCH"]
S = tempfile.mkdtemp(prefix="src6-", dir=SCR)
GIT_ENV = {"PATH": "/usr/bin:/bin", "HOME": os.path.join(S, "home"), "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"}
os.makedirs(GIT_ENV["HOME"], exist_ok=True)
DOMAIN = b"governance-os.source-content-digest/2\n"


class SourceRefused(Exception):
    pass


def git(args, cwd, env_extra=None):
    e = dict(GIT_ENV, **(env_extra or {}))
    r = subprocess.run(["git"] + args, cwd=cwd, env=e, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode(errors="replace"))
    return r.stdout


def u64(n):
    return struct.pack(">Q", n)


def tree_entries_raw(repo, rev):
    raw = git(["ls-tree", "-r", "-z", "--full-tree", rev], repo)
    out = []
    for rec in raw.split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        mode, typ, oid = meta.decode().split(" ")
        out.append((mode, typ, oid, path))
    return out


def content_digest_v2(repo, rev, refuse=True):
    entries = tree_entries_raw(repo, rev)
    recs = []
    for mode, typ, oid, path in entries:
        if refuse:
            if any(b < 0x20 or b == 0x7F for b in path):
                raise SourceRefused("SOURCE_PATH_REFUSED: control character in path %r" % path)
            try:
                path.decode("utf-8")
            except UnicodeDecodeError:
                raise SourceRefused("SOURCE_PATH_REFUSED: path not UTF-8 %r" % path)
            if mode == "160000" or typ != "blob":
                raise SourceRefused("SOURCE_PATH_REFUSED: submodule or non-blob entry %r" % path)
        blob = git(["cat-file", "blob", oid], repo)
        recs.append((path, mode.encode(), hashlib.sha256(blob).digest()))
    recs.sort(key=lambda r: r[0])
    body = DOMAIN + u64(len(recs)) + b"".join(u64(len(m)) + m + u64(len(p)) + p + u64(32) + h for p, m, h in recs)
    return "sha256:" + hashlib.sha256(body).hexdigest()


def content_digest_v1_lines(repo, rev, terminated=False):
    """The revision-5 text of `30` §4.1: sorted lines `<mode> <path> <sha256 hex>`."""
    lines = []
    for mode, typ, oid, path in tree_entries_raw(repo, rev):
        lines.append("%s %s %s" % (mode, path.decode("utf-8", "surrogateescape"), hashlib.sha256(git(["cat-file", "blob", oid], repo)).hexdigest()))
    lines.sort()
    body = "".join(l + "\n" for l in lines) if terminated else "\n".join(lines)
    return "sha256:" + hashlib.sha256(body.encode("utf-8", "surrogateescape")).hexdigest()


def make_repo(name, files, links=(), exec_paths=(), msg=None, date=None):
    d = os.path.join(S, name)
    os.makedirs(d)
    git(["init", "-q"], d)
    for p, content in files.items():
        fp = os.path.join(d, p)
        os.makedirs(os.path.dirname(fp) or d, exist_ok=True)
        with open(fp, "wb") as f:
            f.write(content)
    for p in exec_paths:
        os.chmod(os.path.join(d, p), 0o755)
    for p, target in links:
        os.makedirs(os.path.dirname(os.path.join(d, p)) or d, exist_ok=True)
        os.symlink(target, os.path.join(d, p))
    git(["add", "-A"], d)
    extra = {"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date} if date else None
    git(["commit", "-q", "-m", msg or name], d, extra)
    return d


def digest_or_refusal(repo, rev="HEAD", refuse=True):
    try:
        return {"digest": content_digest_v2(repo, rev, refuse)}
    except SourceRefused as e:
        return {"refused": str(e).split(":")[0]}


out = {"probe": "SRC6 source identity v2 (AR-0015)", "git": subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip()}

# ---- T1: reviewer B's carrier construction
CARGO_CFG = b"[build]\nrustflags = [\"-C\", \"overflow-checks=on\"]\n"
LIB = b"pub fn f() {}\n"
h_cfg = hashlib.sha256(CARGO_CFG).hexdigest()
t_gen = make_repo("t1-genuine", {".cargo/config.toml": CARGO_CFG, "src/lib.rs": LIB})
t_car = make_repo("t1-carrier", {f".cargo/config.toml {h_cfg}\n100644 src/lib.rs": LIB})
T1 = {
    "v1_line_encoding_joined": [content_digest_v1_lines(t_gen, "HEAD"), content_digest_v1_lines(t_car, "HEAD")],
    "v2_genuine": digest_or_refusal(t_gen),
    "v2_carrier": digest_or_refusal(t_car),
    "v2_encoding_only_refusal_disabled": [digest_or_refusal(t_gen, refuse=False), digest_or_refusal(t_car, refuse=False)],
    "git_tree_ids": [git(["rev-parse", "HEAD^{tree}"], t_gen).decode().strip(), git(["rev-parse", "HEAD^{tree}"], t_car).decode().strip()],
}
T1["verdicts"] = {
    "v1_collision_reproduced": T1["v1_line_encoding_joined"][0] == T1["v1_line_encoding_joined"][1],
    "v2_refuses_carrier_path": T1["v2_carrier"].get("refused") == "SOURCE_PATH_REFUSED",
    "v2_genuine_computed": "digest" in T1["v2_genuine"],
    "v2_encoding_alone_distinguishes": T1["v2_encoding_only_refusal_disabled"][0]["digest"] != T1["v2_encoding_only_refusal_disabled"][1]["digest"],
    "git_tree_ids_differ": T1["git_tree_ids"][0] != T1["git_tree_ids"][1],
}
out["T1_carrier_tree"] = T1

# ---- T2: variants without control characters
pairs = {
    "space_in_path_vs_two_dirs": ({"a b/c": b"x"}, {"a/b c": b"x"}),
    "prefix_path": ({"src/lib": b"x", "src/lib.rs": b"y"}, {"src/lib.rs": b"y", "src/libx": b"x"}),
    "empty_file_vs_absent": ({"a": b"x", "b": b""}, {"a": b"x"}),
    "content_moved_between_files": ({"a": b"xy", "b": b""}, {"a": b"x", "b": b"y"}),
    "unicode_normalisation_forms": ({"café.txt".encode().decode(): b"x"}, {"café.txt": b"x"}),
}
T2 = {}
for k, (fa, fb) in pairs.items():
    ra, rb = make_repo("t2-%s-a" % k, fa), make_repo("t2-%s-b" % k, fb)
    da, db = digest_or_refusal(ra), digest_or_refusal(rb)
    T2[k] = {"a": da, "b": db, "differ": da != db}
out["T2_variants"] = T2

# ---- T3: mode, links, metadata
base_files = {"bin/tool.sh": b"#!/bin/sh\necho ok\n", "src/main.rs": b"fn main() {}\n", "README": b"r\n"}
r_plain = make_repo("t3-plain", base_files, links=[("link", "README")])
r_exec = make_repo("t3-exec", base_files, links=[("link", "README")], exec_paths=["bin/tool.sh"])
r_link = make_repo("t3-link", base_files, links=[("link", "src/main.rs")])
r_meta = make_repo("t3-meta", base_files, links=[("link", "README")], msg="different message", date="2031-05-05T05:05:05Z")
d_plain, d_exec, d_link, d_meta = (digest_or_refusal(r) for r in (r_plain, r_exec, r_link, r_meta))
out["T3_mode_link_metadata"] = {"plain": d_plain, "exec_bit": d_exec, "link_target": d_link, "other_commit_metadata": d_meta,
                                "verdicts": {"exec_bit_changes_digest": d_plain != d_exec, "link_target_changes_digest": d_plain != d_link,
                                             "commit_metadata_does_not_change_digest": d_plain == d_meta,
                                             "commit_ids_differ": git(["rev-parse", "HEAD"], r_plain) != git(["rev-parse", "HEAD"], r_meta)}}

# ---- T4: determinism across clones, time, processes
origin = make_repo("t4-origin", dict(base_files, **{"deep/er/nested/file.txt": b"n\n", "ünicode/ä.txt": b"u\n"}), links=[("link", "README")], exec_paths=["bin/tool.sh"])
c1 = os.path.join(S, "t4-clone-1")
c2 = os.path.join(S, "t4-clone-2")
git(["clone", "-q", "--no-local", origin, c1], S)
d1 = content_digest_v2(c1, "HEAD")
time.sleep(2.2)
git(["clone", "-q", "--no-local", origin, c2], S)
d2 = content_digest_v2(c2, "HEAD")
d3 = content_digest_v2(origin, "HEAD")
out["T4_determinism"] = {"clone_1": d1, "clone_2_after_2s": d2, "origin": d3,
                         "verdicts": {"identical_across_two_clones_and_time": d1 == d2 == d3}}
out["verdicts"] = {**{"T1_" + k: v for k, v in T1["verdicts"].items()},
                   "T2_all_variant_pairs_differ": all(v["differ"] for v in T2.values()),
                   **{"T3_" + k: v for k, v in out["T3_mode_link_metadata"]["verdicts"].items()},
                   "T4_identical_across_clones_and_time": out["T4_determinism"]["verdicts"]["identical_across_two_clones_and_time"]}
txt = json.dumps(out, indent=1, sort_keys=True).replace(S, "<scratch>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt))
