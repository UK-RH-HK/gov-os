#!/usr/bin/env python3
"""SPIKE ONLY (BR-AR-0001) -- not bridge code. Measures the whole-repository corpus at one or more Git refs under
the draft inclusion/exclusion rules of ARCHITECTURE.md section 1. Reads Git objects only (never the working tree).

usage: corpus_measure.py REF [REF...] [--tips-glob 'refs/heads/phase2/*']
"""
import collections, fnmatch, json, re, subprocess, sys

SECRET_PATH = ["**/.env", "**/.env.*", "**/*.pem", "**/*.key", "**/id_rsa*", "**/secrets/**", "**/*secret*.yaml",
               "**/*secret*.yml", "**/*secret*.json", "**/*credentials*",            # SECURITY_POLICY.yaml:6-16
               "**/*.env", "**/.secrets/**", "**/deepseek*.env"]                    # .gitignore:12-14
SECRET_CONTENT = {                                                                    # SECURITY_POLICY.yaml:17-26
    "aws-access-key": r"AKIA[0-9A-Z]{16}",
    "aws-secret-key": r"(?i)aws_secret_access_key\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{40}",
    "private-key-block": r"-----BEGIN (RSA |EC |OPENSSH |DSA |)PRIVATE KEY-----",
    "github-token": r"gh[pousr]_[A-Za-z0-9]{36,}",
    "generic-api-key": r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{20,}",
    "password-assignment": r"(?i)password\s*[=:]\s*['\"][^'\"\s]{8,}['\"]",
    "slack-token": r"xox[baprs]-[A-Za-z0-9-]{10,}",
    "stripe-like-key": r"\bsk_(live|test)_[A-Za-z0-9_]{16,}",
    "jwt": r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
}
BUILD = ["target/**", "**/target/**", ".claude/worktrees/**", "**/__pycache__/**", "**/*.pyc", "**/.pytest_cache/**",
         "**/.governance-runtime/**", "build/**", "dist/**", "**/*.egg-info/**", "release/evidence/tmp/**"]  # .gitignore:1-9,15
MAX_TEXT = 1 << 20   # 1 MiB: larger text blobs are metadata-only (exact retrieval by path still works)
CHUNK = 1200 - 120   # MEMORY_POLICY.chunking max_chars - overlap_chars


def glob_match(path, pat):
    # '**/' prefix also matches at top level; repository paths are SUBJECTS, never interpolated into a pattern
    if fnmatch.fnmatchcase(path, pat):
        return True
    return pat.startswith("**/") and fnmatch.fnmatchcase(path, pat[3:])


def ls_tree(ref):
    out = subprocess.run(["git", "ls-tree", "-r", "-l", "-z", ref], capture_output=True, check=True).stdout
    for rec in out.split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        mode, typ, oid, size = meta.split()
        yield mode.decode(), typ.decode(), oid.decode(), (int(size) if size != b"-" else 0), path.decode("utf-8", "surrogateescape")


class Cat:
    def __init__(self):
        self.p = subprocess.Popen(["git", "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def read(self, oid):
        self.p.stdin.write(oid.encode() + b"\n"); self.p.stdin.flush()
        hdr = self.p.stdout.readline().split()
        n = int(hdr[2]); data = self.p.stdout.read(n); self.p.stdout.read(1)
        return data


def classify(path, mode, typ, size, cat, cache):
    if typ != "blob":
        return "X-NONBLOB(submodule)", None
    if mode == "120000":
        return "X-SYMLINK", None
    for p in SECRET_PATH:
        if glob_match(path, p):
            return "X-SEC-PATH", p
    for p in BUILD:
        if glob_match(path, p):
            return "X-BUILD", p
    if size > MAX_TEXT:
        return "M-LARGE(metadata-only)", None
    return None, None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--refs-glob" in sys.argv:
        g = sys.argv[sys.argv.index("--refs-glob") + 1]
        args = [a for a in args if a != g] + subprocess.run(["git", "for-each-ref", "--format=%(refname:short)", g],
                                                             capture_output=True, text=True).stdout.split()
    tips_glob = None
    if "--tips-glob" in sys.argv:
        tips_glob = sys.argv[sys.argv.index("--tips-glob") + 1]
        args = [a for a in args if a != tips_glob]
    cat = Cat(); content_cache = {}
    report = {"rules": {"secret_path": SECRET_PATH, "secret_content": sorted(SECRET_CONTENT), "build": BUILD,
                        "max_text_bytes": MAX_TEXT}, "refs": {}}
    union = {}
    for ref in args:
        commit = subprocess.run(["git", "rev-parse", ref + "^{commit}"], capture_output=True, text=True).stdout.strip()
        by_rule = collections.Counter(); by_rule_bytes = collections.Counter(); inc_top = collections.Counter()
        inc_top_bytes = collections.Counter(); inc_ext = collections.Counter(); inc_ext_bytes = collections.Counter(); excl_paths = collections.defaultdict(list); lines = 0; inc_bytes = 0; files = 0
        examples = collections.defaultdict(list); content_hits = collections.Counter()
        for mode, typ, oid, size, path in ls_tree(commit):
            files += 1
            rule, why = classify(path, mode, typ, size, cat, content_cache)
            if rule is None:
                if oid not in content_cache:
                    data = cat.read(oid)
                    verdict = None
                    if b"\0" in data[:8000]:
                        verdict = ("X-BINARY", None)
                    else:
                        try:
                            text = data.decode("utf-8")
                        except UnicodeDecodeError:
                            verdict = ("X-BINARY(non-utf8)", None)
                        else:
                            for cid, rx in SECRET_CONTENT.items():
                                if re.search(rx, text):
                                    verdict = ("X-SEC-CONTENT", cid); break
                            if verdict is None:
                                verdict = ("INCLUDED", text.count("\n") + (1 if text and not text.endswith("\n") else 0))
                    content_cache[oid] = verdict
                rule, why = content_cache[oid]
                if rule == "X-SEC-CONTENT":
                    content_hits[why] += 1
            if rule == "INCLUDED":
                inc_bytes += size; lines += why
                top = path.split("/")[0] if "/" in path else "(root)"
                inc_top[top] += 1; inc_top_bytes[top] += size
                ext = path.rsplit(".", 1)[-1] if "." in path.rsplit("/", 1)[-1] else "(none)"
                inc_ext[ext] += 1; inc_ext_bytes[ext] += size
                union[oid] = size
            by_rule[rule] += 1; by_rule_bytes[rule] += size
            if rule != "INCLUDED":
                excl_paths[rule].append(path + (f"  [{why}]" if why and not isinstance(why, int) else ""))
            if rule != "INCLUDED" and len(examples[rule]) < 6:
                examples[rule].append(path + (f"  [{why}]" if why and not isinstance(why, int) else ""))
        report["refs"][ref] = {
            "commit": commit, "files_total": files, "by_rule_files": dict(by_rule), "by_rule_bytes": dict(by_rule_bytes),
            "included_files": by_rule["INCLUDED"], "included_bytes": inc_bytes, "included_lines": lines,
            "est_chunks_at_1080_stride": sum(max(1, -(-b // CHUNK)) for b in [inc_bytes]) ,
            "included_by_top_dir": {k: [inc_top[k], inc_top_bytes[k]] for k in sorted(inc_top)},
            "included_top_extensions": inc_ext.most_common(15), "included_bytes_by_extension": dict(inc_ext_bytes.most_common(25)), "excluded_paths": {k: sorted(v) for k, v in excl_paths.items()}, "secret_content_hits": dict(content_hits),
            "excluded_examples": dict(examples)}
    report["union_of_included_unique_blobs"] = {"blobs": len(union), "bytes": sum(union.values())}
    if "--union-only" in sys.argv:
        report["refs"] = {r: {k: v[k] for k in ("commit", "files_total", "included_files", "included_bytes", "by_rule_files")}
                          for r, v in report["refs"].items()}
    if tips_glob:
        refs = subprocess.run(["git", "for-each-ref", "--format=%(refname)", tips_glob], capture_output=True,
                              text=True).stdout.split()
        allb = {}
        for r in refs:
            for mode, typ, oid, size, path in ls_tree(r):
                if typ == "blob":
                    allb[oid] = size
        report["tips"] = {"glob": tips_glob, "refs": len(refs), "unique_blobs_all_paths": len(allb),
                          "unique_bytes_all_paths": sum(allb.values()),
                          "new_blobs_vs_measured_refs": len(set(allb) - set(union)),
                          "new_bytes_vs_measured_refs": sum(v for k, v in allb.items() if k not in union)}
    json.dump(report, sys.stdout, indent=1, sort_keys=True)
    print()


if __name__ == "__main__":
    main()
