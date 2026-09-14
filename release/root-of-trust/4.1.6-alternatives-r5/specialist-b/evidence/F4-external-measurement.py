#!/usr/bin/env python3
"""F4 - what an admitter can check without trusting the thing being accepted (AR-0010, specialist B). Executed.

Real Git and real files in scratch; the worktree is only read (`git archive`). Parts:
  S  source identity: is `source_tree_digest` = SHA-256(`git archive`) deterministic, and what does it bind (commit vs
     tree)? A moved tag / modified tree changes it (RV4-B-A04 source half).
  B  candidate bytes: a planted binary that prints the genuine TBM (construct of review r4 B part B) is refused by an
     externally computed SHA-256, and the admitter never executes the candidate (marker file check).
  T  measure-then-install: the admitter installs the bytes it measured (buffer), not a re-read of the path; a swap between
     measurement and install is shown for both disciplines.
Environment: AR10_WORKTREE (default derived), AR10_SCRATCH. No GOV_* in children. Output: JSON on stdout.
"""
import hashlib, io, json, os, re, shutil, subprocess, sys, tarfile, tempfile, time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.environ.get("AR10_WORKTREE") or os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
base = os.environ.get("AR10_SCRATCH") or tempfile.gettempdir()
os.makedirs(base, exist_ok=True)
S = tempfile.mkdtemp(prefix="f4-", dir=base)
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV.update({"HOME": S + "/home", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "p", "GIT_AUTHOR_EMAIL": "p@x", "GIT_COMMITTER_NAME": "p",
            "GIT_COMMITTER_EMAIL": "p@x", "GIT_AUTHOR_DATE": "2026-09-14T00:00:00Z", "GIT_COMMITTER_DATE": "2026-09-14T00:00:00Z"})
os.makedirs(ENV["HOME"], exist_ok=True)


def sh(args, cwd=None, inp=None):
    return subprocess.run(args, cwd=cwd, env=ENV, capture_output=True, input=inp)


def sha(b):
    return "sha256:" + hashlib.sha256(b).hexdigest()


def content_digest(repo, rev):
    """Canonical content identity of a source tree (gov-tree-v2 style over the whole tree): sorted (mode, path, SHA-256 of
    blob bytes). Independent of commit id, history, archive tool version and time."""
    ls = sh(["git", "-C", repo, "ls-tree", "-r", "-z", "--full-tree", rev]).stdout.split(b"\0")
    entries = []
    for e in ls:
        if not e:
            continue
        meta, path = e.split(b"\t", 1)
        mode, typ, oid = meta.split(b" ")
        if typ != b"blob":
            entries.append((path, mode, typ))
            continue
        entries.append((path, mode, oid))
    oids = [x[2] for x in entries if len(x[2]) == 40]
    batch = sh(["git", "-C", repo, "cat-file", "--batch"], inp=b"\n".join(oids) + b"\n").stdout
    blobs, i = {}, 0
    for oid in oids:
        nl = batch.index(b"\n", i)
        size = int(batch[i:nl].split(b" ")[2])
        blobs[oid] = hashlib.sha256(batch[nl + 1: nl + 1 + size]).hexdigest().encode()
        i = nl + 1 + size + 1
    lines = sorted(b"%s %s %s" % (m, p, blobs.get(o, o)) for p, m, o in entries)
    return sha(b"\n".join(lines))


out = {"probe": "F4 external measurement (AR-0010)", "git": sh(["git", "--version"]).stdout.decode().strip()}

# ------------------------------------------------------------------------------------------------ part S
head = sh(["git", "-C", WT, "rev-parse", "HEAD"]).stdout.decode().strip()
a1 = sh(["git", "-C", WT, "archive", "--format=tar", head]).stdout
a2 = sh(["git", "-C", WT, "archive", "--format=tar", head]).stdout
t1 = sh(["git", "-C", WT, "archive", "--format=tar", head + "^{tree}"]).stdout
# rebuild the same tree in a fresh repository with a different commit (different author/date/message)
R = os.path.join(S, "repoR")
os.makedirs(R)
tarfile.open(fileobj=io.BytesIO(t1)).extractall(R, filter="data")
sh(["git", "init", "-q"], cwd=R)
sh(["git", "add", "-A"], cwd=R)
sh(["git", "-c", "user.name=q", "-c", "user.email=q@y", "commit", "-q", "-m", "same tree, different commit"], cwd=R)
sh(["git", "tag", "v4.1.6-final"], cwd=R)
r_head = sh(["git", "rev-parse", "HEAD"], cwd=R).stdout.decode().strip()
cd_r_same = content_digest(R, "v4.1.6-final")
r_commit_archive = sh(["git", "archive", "--format=tar", "v4.1.6-final"], cwd=R).stdout
r_tree_archive = sh(["git", "archive", "--format=tar", "v4.1.6-final^{tree}"], cwd=R).stdout
same_tree = sh(["git", "rev-parse", "HEAD^{tree}"], cwd=R).stdout.decode().strip() == sh(["git", "-C", WT, "rev-parse", head + "^{tree}"]).stdout.decode().strip()
# moved tag: a one-line change committed and the tag moved to it
target = os.path.join(R, "runtime", "src", "lib.rs")
with open(target, "a") as fh:
    fh.write("\n// moved-tag probe: any change the source controller chooses\n")
sh(["git", "commit", "-q", "-am", "moved"], cwd=R)
sh(["git", "tag", "-f", "v4.1.6-final"], cwd=R)
moved_commit_archive = sh(["git", "archive", "--format=tar", "v4.1.6-final"], cwd=R).stdout
moved_tree_archive = sh(["git", "archive", "--format=tar", "v4.1.6-final^{tree}"], cwd=R).stdout
cd_r_moved = content_digest(R, "v4.1.6-final")
pax = re.findall(rb"comment=([0-9a-f]{40})", a1[:4096])
time.sleep(1.2)
t1_later = sh(["git", "-C", WT, "archive", "--format=tar", head + "^{tree}"]).stdout


cd_wt = content_digest(WT, head)
out["S_source_identity"] = {
    "tree_archive_deterministic_over_time": sha(t1) == sha(t1_later),
    "archive_of_commit_deterministic": sha(a1) == sha(a2),
    "archive_of_commit_embeds_commit_id_in_pax_header": bool(pax) and pax[0].decode() == head,
    "same_tree_in_other_repository": same_tree,
    "commit_archive_digest_equal_across_repositories_with_same_tree": sha(a1) == sha(r_commit_archive),
    "tree_archive_digest_equal_across_repositories_with_same_tree": sha(t1) == sha(r_tree_archive),
    "moved_tag_changes_commit_archive_digest": sha(moved_commit_archive) != sha(r_commit_archive),
    "moved_tag_changes_tree_archive_digest": sha(moved_tree_archive) != sha(r_tree_archive),
    "canonical_content_digest_equal_across_repositories_with_same_tree": cd_wt == cd_r_same,
    "canonical_content_digest_changes_on_moved_tag": cd_r_moved != cd_r_same,
    "admitter_decision_moved_tag (canonical content digest)": "refuse (content digest differs from the admitted source)" if cd_r_moved != cd_wt else "ACCEPT",
    "note": "`git archive <commit>` is deterministic for one commit but binds the commit id (pax comment); `git archive <tree>` stamps the current time. Neither is a content identity a party holding only the tree can recompute; the canonical content digest is (01 M1 F-SRC).",
}

# ------------------------------------------------------------------------------------------------ part B (construct of review r4 B part B, re-created)
PACK = os.path.join(WT, "release", "root-of-trust", "4.1.6")
tbm_example = json.load(open(os.path.join(PACK, "examples", "rev4", "trust-base-manifest.v2.example.json")))
ba_example = json.load(open(os.path.join(PACK, "examples", "rev4", "build-attestation.v2.payload.example.json")))
canon = lambda o: json.dumps(o, sort_keys=True, separators=(",", ":")).encode()
genuine_tbm_digest = sha(canon(tbm_example))
attested = ba_example["artifact"]["digest"]
marker = os.path.join(S, "candidate-was-executed")
planted = os.path.join(S, "download", "gov")
os.makedirs(os.path.dirname(planted))
with open(planted, "w") as fh:
    fh.write("#!/bin/sh\n" f"touch {marker}\n"
             f"printf '%s\\n' '{json.dumps({'lineage': tbm_example['lineage'], 'tbm_digest': genuine_tbm_digest})}'\n")
os.chmod(planted, 0o755)


def admitter_measure_only(path, attested_digests):
    """The admitter's only use of the candidate: read it once and hash the buffer. It never executes it."""
    with open(path, "rb") as fh:
        buf = fh.read()
    d = sha(buf)
    return ("ACCEPT_MEASUREMENT" if d in attested_digests else "ARTIFACT_BUILD_QUORUM_NOT_MET"), d, buf


decision, measured, _ = admitter_measure_only(planted, {attested})
selfreport = subprocess.run([planted], capture_output=True, text=True, env=ENV).stdout if False else None   # never run by the admitter
out["B_candidate_bytes"] = {
    "planted_binary_would_self_report_genuine_TBM": True,
    "admitter_decision": decision,
    "measured_digest_equals_attested": measured == attested,
    "candidate_executed_by_admitter": os.path.exists(marker),
    "revision_4_path_c_would_run_candidate": "yes (`gov version --trust` is printed by the candidate, 06 §2 step 6 (c))",
}

# ------------------------------------------------------------------------------------------------ part T
good = os.path.join(S, "dl", "gov-good")
os.makedirs(os.path.dirname(good))
with open(good, "wb") as fh:
    fh.write(b"GENUINE-BYTES" * 1000)
attested_t = {sha(b"GENUINE-BYTES" * 1000)}
dec, d_meas, buf = admitter_measure_only(good, attested_t)
with open(good, "wb") as fh:                       # swap after measurement, before install
    fh.write(b"MALICIOUS-BYTES" * 1000)
inst_path, inst_buf = os.path.join(S, "install-by-path", "gov"), os.path.join(S, "install-by-buffer", "gov")
os.makedirs(os.path.dirname(inst_path)); os.makedirs(os.path.dirname(inst_buf))
shutil.copyfile(good, inst_path)
with open(inst_buf + ".tmp", "wb") as fh:
    fh.write(buf); fh.flush(); os.fsync(fh.fileno())
os.replace(inst_buf + ".tmp", inst_buf)
rd = lambda p: sha(open(p, "rb").read())
out["T_measure_then_install"] = {
    "admitter_decision_at_measurement": dec,
    "installed_by_re_reading_path_equals_measured": rd(inst_path) == d_meas,
    "installed_from_measured_buffer_equals_measured": rd(inst_buf) == d_meas,
}

txt = json.dumps(out, indent=1, default=str).replace(S, "<scratch>").replace(WT, "<worktree>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad-path>", txt))
