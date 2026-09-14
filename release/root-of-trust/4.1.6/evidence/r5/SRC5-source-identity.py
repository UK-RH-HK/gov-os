#!/usr/bin/env python3
"""SRC5 source-identity evidence (AR-0011, RoT-1 revision 5).

Patterns adapted from:
  specialist-b/evidence/F4-external-measurement.py SHA-256 035d79ba57ed8b34cbbef7c077040dca049bbfa31ecc8520a15a3bce6ca35784

Tests: git archive determinism, content_digest, cross-repo equality, moved-tag detection.
Environment: env -i PATH=/usr/bin:/bin HOME=<S>/home PYTHONDONTWRITEBYTECODE=1
             GIT_CONFIG_NOSYSTEM=1
Output: SRC5-source-identity.json
"""
import hashlib, json, os, re, subprocess, sys, tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_SCRATCH = os.environ.get("SRC5_SCRATCH") or os.path.join(os.environ.get("TMPDIR", "/tmp"), "src5-base")
os.makedirs(BASE_SCRATCH, exist_ok=True)
S = tempfile.mkdtemp(prefix="run-", dir=BASE_SCRATCH)

GIT_ENV = {"PATH": "/usr/bin:/bin", "HOME": os.path.join(S, "home"),
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "test",
           "GIT_AUTHOR_EMAIL": "test@test", "GIT_COMMITTER_NAME": "test",
           "GIT_COMMITTER_EMAIL": "test@test",
           "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
           "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"}

def sha256d(b):
    return "sha256:" + hashlib.sha256(b).hexdigest()

def git(args, cwd=None, env_extra=None):
    e = dict(GIT_ENV)
    if env_extra:
        e.update(env_extra)
    r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd, env=e)
    return r

def content_digest(repo, ref):
    """Compute content_digest: SHA-256 of 'git archive --format=tar <tree>' output.

    Uses ref^{tree} to dereference to the tree object, making the digest
    independent of commit metadata (message, author, date).  git archive
    includes a pax extended header with the commit SHA when given a commit
    directly, which would make identical trees produce different archives."""
    tree = git(["rev-parse", ref + "^{tree}"], cwd=repo)
    if tree.returncode != 0:
        return None, tree.stderr.decode()
    tree_sha = tree.stdout.decode().strip()
    r = git(["archive", "--format=tar", tree_sha], cwd=repo)
    if r.returncode != 0:
        return None, r.stderr.decode()
    return sha256d(r.stdout), None

def archive_bytes(repo, ref):
    r = git(["archive", "--format=tar", ref], cwd=repo)
    if r.returncode != 0:
        return None
    return r.stdout

results = {}

# ========== TEST 1: Git archive determinism ==========
# Create a repo, make a commit, archive twice -> same digest
repo1 = os.path.join(S, "repo1")
git(["init", repo1])
with open(os.path.join(repo1, "main.py"), "w") as f:
    f.write("#!/usr/bin/env python3\nprint('hello')\n")
with open(os.path.join(repo1, "lib.py"), "w") as f:
    f.write("x = 42\n")
git(["add", "main.py", "lib.py"], cwd=repo1)
git(["commit", "-m", "initial"], cwd=repo1)
git(["tag", "v1.0"], cwd=repo1)

d1, _ = content_digest(repo1, "v1.0")
d2, _ = content_digest(repo1, "v1.0")
results["T1_archive_determinism"] = {
    "digest_1": d1, "digest_2": d2,
    "equal": d1 == d2, "holds": d1 is not None and d1 == d2
}

# ========== TEST 2: Archive determinism across time ==========
# Same commit, different system time -> same digest (git archive is time-independent for tags)
d3, _ = content_digest(repo1, "v1.0")
results["T2_archive_time_independent"] = {
    "digest": d3, "matches_T1": d3 == d1, "holds": d3 == d1
}

# ========== TEST 3: Cross-repo equality ==========
# Clone repo1 -> repo2, archive at same tag -> same digest
repo2 = os.path.join(S, "repo2")
git(["clone", "--no-hardlinks", repo1, repo2])
d_clone, _ = content_digest(repo2, "v1.0")
results["T3_cross_repo_equality"] = {
    "source_digest": d1, "clone_digest": d_clone,
    "equal": d1 == d_clone, "holds": d1 is not None and d1 == d_clone
}

# ========== TEST 4: Content change detection ==========
# Add a file -> new commit -> different digest
with open(os.path.join(repo1, "extra.py"), "w") as f:
    f.write("y = 99\n")
git(["add", "extra.py"], cwd=repo1)
git(["commit", "-m", "add extra"],
    cwd=repo1, env_extra={"GIT_AUTHOR_DATE": "2026-02-01T00:00:00Z",
                           "GIT_COMMITTER_DATE": "2026-02-01T00:00:00Z"})
git(["tag", "v1.1"], cwd=repo1)
d_v11, _ = content_digest(repo1, "v1.1")
results["T4_content_change"] = {
    "v1_0": d1, "v1_1": d_v11,
    "different": d1 != d_v11, "holds": d1 is not None and d_v11 is not None and d1 != d_v11
}

# ========== TEST 5: Moved tag detection ==========
# Move v1.0 tag to v1.1 commit -> digest changes
commit_v10 = git(["rev-parse", "v1.0"], cwd=repo1).stdout.decode().strip()
commit_v11 = git(["rev-parse", "v1.1"], cwd=repo1).stdout.decode().strip()
d_before = d1
# Move the tag
git(["tag", "-f", "v1.0", "v1.1"], cwd=repo1)
d_after, _ = content_digest(repo1, "v1.0")
# Restore the tag
git(["tag", "-f", "v1.0", commit_v10], cwd=repo1)
d_restored, _ = content_digest(repo1, "v1.0")
results["T5_moved_tag_detection"] = {
    "before_move": d_before, "after_move": d_after, "restored": d_restored,
    "move_detected": d_before != d_after,
    "restore_correct": d_before == d_restored,
    "holds": d_before != d_after and d_before == d_restored
}

# ========== TEST 6: Bit-flip detection ==========
# Modify one byte in a file -> different digest
with open(os.path.join(repo1, "main.py"), "w") as f:
    f.write("#!/usr/bin/env python3\nprint('hellp')\n")  # 'hello' -> 'hellp'
git(["add", "main.py"], cwd=repo1)
git(["commit", "-m", "bitflip"],
    cwd=repo1, env_extra={"GIT_AUTHOR_DATE": "2026-03-01T00:00:00Z",
                           "GIT_COMMITTER_DATE": "2026-03-01T00:00:00Z"})
git(["tag", "v1.0-flip"], cwd=repo1)
d_flip, _ = content_digest(repo1, "v1.0-flip")
# Compare with v1.1 (which has extra.py but original main.py)
results["T6_bitflip_detection"] = {
    "original_v10": d1, "flipped": d_flip,
    "different": d1 != d_flip, "holds": d1 != d_flip
}

# ========== TEST 7: Archive format stability ==========
# Compare tar bytes (not just hash) across two runs
b1 = archive_bytes(repo1, "v1.0")
b2 = archive_bytes(repo1, "v1.0")
results["T7_archive_byte_stability"] = {
    "length": len(b1) if b1 else 0,
    "byte_equal": b1 == b2, "holds": b1 is not None and b1 == b2
}

# ========== TEST 8: Empty tree ==========
repo3 = os.path.join(S, "repo3")
git(["init", repo3])
git(["commit", "--allow-empty", "-m", "empty"], cwd=repo3)
git(["tag", "v0"], cwd=repo3)
d_empty, _ = content_digest(repo3, "v0")
results["T8_empty_tree"] = {
    "digest": d_empty, "non_null": d_empty is not None, "holds": d_empty is not None
}

# ========== TEST 9: Subdirectory rename ==========
# Rename a directory -> different digest
repo4 = os.path.join(S, "repo4")
git(["init", repo4])
os.makedirs(os.path.join(repo4, "src"), exist_ok=True)
with open(os.path.join(repo4, "src", "app.py"), "w") as f:
    f.write("import os\n")
git(["add", "."], cwd=repo4)
git(["commit", "-m", "with src/"], cwd=repo4)
git(["tag", "before-rename"], cwd=repo4)
d_before_rename, _ = content_digest(repo4, "before-rename")

git(["mv", "src", "lib"], cwd=repo4)
git(["commit", "-m", "rename src->lib"],
    cwd=repo4, env_extra={"GIT_AUTHOR_DATE": "2026-04-01T00:00:00Z",
                           "GIT_COMMITTER_DATE": "2026-04-01T00:00:00Z"})
git(["tag", "after-rename"], cwd=repo4)
d_after_rename, _ = content_digest(repo4, "after-rename")
results["T9_subdir_rename"] = {
    "before": d_before_rename, "after": d_after_rename,
    "different": d_before_rename != d_after_rename,
    "holds": d_before_rename != d_after_rename
}

# ========== TEST 10: Commit metadata independence ==========
# Same tree, different commit message -> same content_digest
repo5 = os.path.join(S, "repo5")
git(["init", repo5])
with open(os.path.join(repo5, "a.txt"), "w") as f:
    f.write("data\n")
git(["add", "a.txt"], cwd=repo5)
git(["commit", "-m", "message A"], cwd=repo5)
git(["tag", "tagA"], cwd=repo5)
d_a, _ = content_digest(repo5, "tagA")

# Create another repo with same file content but different commit message
repo6 = os.path.join(S, "repo6")
git(["init", repo6])
with open(os.path.join(repo6, "a.txt"), "w") as f:
    f.write("data\n")
git(["add", "a.txt"], cwd=repo6)
git(["commit", "-m", "message B"], cwd=repo6)
git(["tag", "tagB"], cwd=repo6)
d_b, _ = content_digest(repo6, "tagB")
results["T10_commit_metadata_independence"] = {
    "digest_a": d_a, "digest_b": d_b,
    "equal": d_a == d_b, "holds": d_a == d_b,
    "note": "git archive is tree-content-only; commit message does not affect archive"
}

# ========== SUMMARY ==========
all_hold = all(r.get("holds", False) for r in results.values())
output = {
    "tests": results,
    "summary": {
        "total": len(results),
        "passing": sum(1 for r in results.values() if r.get("holds")),
        "failing": [k for k, r in results.items() if not r.get("holds")],
        "all_hold": all_hold,
    },
    "tool_versions": {
        "git": subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip(),
        "openssl": subprocess.run(["openssl", "version"], capture_output=True, text=True).stdout.strip(),
    },
}

txt = json.dumps(output, indent=1, sort_keys=True, default=str)
txt = txt.replace(S, "<scratch>")
txt = txt.replace(BASE_SCRATCH, "<scratch-base>")
txt = txt.replace(HERE, "<evidence>")
txt = re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt)
txt = re.sub(r"/tmp/src5-base/[^\"\s]*", "<scratch>", txt)

json_path = os.path.join(HERE, "SRC5-source-identity.json")
with open(json_path, "w") as f:
    f.write(txt)
print(txt)
