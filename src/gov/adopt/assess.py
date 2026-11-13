"""The memory assessment of a repository, before its adoption (W2-88 S1; DEC-954 Q9f, DEC-078, CAP-44.b).

``assess(root, out)`` reads the blobs of ``HEAD`` one at a time from git's objects (``git cat-file --batch``), so that
its memory grows with the largest file and never with the tree. It writes ``<out>/memory-assessment.json`` and nothing
in the repository: no file, no index entry, no ref. A secret is named by its rule id and its path, never by its value:
the value of a finding is read from the scanner's report into a local that is not kept, and no text of a file leaves
this module.
"""

from __future__ import annotations

import json
import os
import re
import resource
import shutil
import subprocess
import tempfile
import time
from pathlib import Path, PurePosixPath

from gov.cli.errors import GovError
from gov.util.digest import sha256
from gov.util.gitenv import git_env

FILE = "memory-assessment.json"
FILE_LIMIT_BYTES = 1_048_576  # proposed (W2-88-evidence.md, seams): the code states no limit on a file's size
LINE_LIMIT = 32_768  # ``gov.retrieval.chunking.READ_CHARS``: a line over it is more than any reader takes
SCAN_LIMIT_BYTES = 16 << 20  # a blob over this is read to this size only, and named in ``secrets_unscanned``
LARGEST = 10
# DEC-078 (the register): the envelope tested, and the measured costs the estimate scales by.
ENVELOPE = {"nodes": 80_000, "edges": 270_000, "peak_rss_bytes": 2_200_000_000}
GRAPH_S_PER_FILE = 0.061       # 61.4 s for 1,005 files (the code graph)
EMBED_S_PER_FILE = 1.07        # the ticket: 2,521 files took 7 to 45 min here, the slow end per file
NODES_PER_FILE = 77.0          # 77,346 nodes / 1,005 files
EDGES_PER_FILE = 269.0         # 270,647 edges / 1,005 files
RSS_PER_EDGE = 8_130           # 2.2 GB / 270,647 edges
BASE_RSS = 57_000_000          # ~EXAMIN APP's 57 MB
DISK_PER_CODE_FILE = 213_930   # 215 MB of index / 1,005 files
# The languages the code graph reads. ``gov.codeintel`` states none (the tool, codebase-memory-mcp, decides), so this
# is the engineer's list, unconfirmed against the tool (W2-88-evidence.md, seams, item 6).
CODE_GRAPH_SUFFIXES = frozenset(".py .pyi .js .jsx .mjs .cjs .ts .tsx .rs .go .java .kt .c .h .cc .cpp .hpp .cs .rb "
                                ".php .swift .scala .sh .lua".split())
# Code in a language the graph does not read: such a file has no code route.
OTHER_CODE_SUFFIXES = frozenset(".cob .cbl .cobol .f .f90 .for .pas .vb .vba .pl .pm .r .jl .zig .nim .d .ex .exs "
                                ".erl .hs .ml .clj .lisp .elm .dart .groovy .m .mm .asm .s .tcl .vhd .v".split())
LANGUAGE_NAMES = {".py": "python", ".pyi": "python", ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript",
                  ".cjs": "javascript", ".ts": "typescript", ".tsx": "typescript", ".rs": "rust", ".go": "go",
                  ".java": "java", ".kt": "kotlin", ".c": "c", ".h": "c", ".cc": "c++", ".cpp": "c++", ".hpp": "c++",
                  ".cs": "c#", ".rb": "ruby", ".php": "php", ".swift": "swift", ".scala": "scala", ".sh": "shell",
                  ".lua": "lua", ".md": "markdown", ".rst": "text", ".txt": "text", ".yaml": "yaml", ".yml": "yaml",
                  ".json": "json", ".toml": "toml", ".html": "html", ".css": "css", ".sql": "sql"}
VENDORED_FOLDERS = ("vendor", "node_modules", "third_party", "third-party", "bower_components", "Pods", ".yarn")
GENERATED_FOLDERS = ("generated", "__generated__", "_generated", "gen-src")
GENERATED_NAMES = re.compile(r"(\.pb\.go|_pb2(_grpc)?\.pyi?|\.generated\.\w+|\.g\.dart|\.designer\.cs|"
                             r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|Cargo\.lock|poetry\.lock))$")
GENERATED_HEADER = re.compile(rb"(@generated|do not edit|code generated|auto-?generated|this file (is|was) generated)",
                              re.IGNORECASE)
VENDORED_HEADER = re.compile(rb"(vendored from|third[- ]party (code|library)|\bvendor(ed)? copy\b)", re.IGNORECASE)
MINIFIED_NAMES = re.compile(r"\.min\.(js|css|mjs)$")
MINIFIED_SUFFIXES = frozenset(".js .css .mjs .cjs .html .svg".split())
MINIFIED_LINE = 1000
HEAD = 4096
_COMMIT_RULE = "".join(("source", "graph", "-access-token"))  # row W2-L423's rule: a commit's hash is no secret


def _git(root: Path, *args: str) -> bytes:
    done = subprocess.run(["git", "-C", str(root), "-c", "core.quotePath=false", *args], capture_output=True,
                          stdin=subprocess.DEVNULL, env=git_env(root))
    if done.returncode != 0:
        raise GovError("ASSESS_GIT_FAILED", f"git {args[0]} failed in {root}: "
                       + " ".join(done.stderr.decode("utf-8", "replace").split()), {"root": str(root)})
    return done.stdout


def _inside(path: Path, root: Path) -> bool:
    path, root = path.resolve(), root.resolve()
    return path == root or root in path.parents


class _Blobs:
    """``git cat-file --batch``: one blob's bytes at a time, from the object database (no work tree, no index)."""

    def __init__(self, root: Path) -> None:
        self.proc = subprocess.Popen(["git", "-C", str(root), "cat-file", "--batch"], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=git_env(root))

    def read(self, sha: str, limit: int) -> tuple[bytes, int]:
        """``(the first ``limit`` bytes of the blob, its size)``; the rest of a larger blob is read and dropped."""
        self.proc.stdin.write(sha.encode() + b"\n")
        self.proc.stdin.flush()
        header = self.proc.stdout.readline().split()
        if len(header) != 3 or header[1] != b"blob":
            raise GovError("ASSESS_GIT_FAILED", f"git cat-file answered {b' '.join(header)!r} for a blob", {})
        size, kept = int(header[2]), b""
        kept = self.proc.stdout.read(min(size, limit))
        left = size - len(kept)
        while left > 0:
            left -= len(self.proc.stdout.read(min(left, 1 << 20)))
        self.proc.stdout.read(1)  # the newline git ends each object with
        return kept, size

    def close(self) -> None:
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=30)
        except Exception:  # noqa: BLE001 - the child is only a reader
            self.proc.kill()


def _rules(root: Path, head: str) -> tuple[str, ...] | None:
    """The secrets rules as ``gov.secrets`` reads them: the repository's own ``.gitleaks.toml`` at ``head``, else the
    template's (A0 puts it in). None where gitleaks or the rules cannot be had: the assessment says so."""
    from gov.adopt.safety import TEMPLATE_GITLEAKS
    from gov.secrets import CONFIG_REL, _rules as rules_of

    try:
        text = _git(root, "show", f"{head}:{CONFIG_REL}").decode("utf-8")
    except GovError:
        try:
            text = TEMPLATE_GITLEAKS.read_text(encoding="utf-8")
        except OSError:
            return None
    if shutil.which("gitleaks") is None:
        return None
    with tempfile.TemporaryDirectory(prefix="gov-assess-") as where:
        (Path(where) / CONFIG_REL).write_text(text, encoding="utf-8")
        try:
            return rules_of(Path(where))
        except RuntimeError:
            return None


class _Scan:
    """The files' texts judged by gitleaks a batch at a time (one process for many small files), each text set off by
    blank lines as ``gov.secrets`` does, and each finding put back on its file by its line. A batch holds at most
    ``BATCH_BYTES`` unless one file is larger: memory follows the largest file, never the tree. The findings' values
    are dropped as they are read; only a path and a rule id leave this class."""

    BATCH_BYTES = 1 << 20

    def __init__(self, rules: tuple[str, ...]) -> None:
        self.rules, self.held, self.size, self.found = rules, [], 0, set()

    def add(self, rel: str, data: bytes) -> None:
        if self.held and self.size + len(data) > self.BATCH_BYTES:
            self.flush()
        self.held.append((rel, data))
        self.size += len(data)

    def flush(self) -> None:
        from gov.secrets import _FLOOR, _LEAKS, _TIMEOUT_S

        if not self.held:
            return
        parts, spans, line = [b"\n"], [], 2  # the leading newline keeps gitleaks from taking the text for a binary
        for rel, data in self.held:
            block = data + b"\n\n"
            lines = block.count(b"\n")
            parts.append(block)
            spans.append((line, line + lines - 1, rel))
            line += lines
        data = b"".join(parts)
        self.held, self.size = [], 0
        env = {key: value for key, value in os.environ.items() if key != "GITLEAKS_CONFIG"}
        for each in self.rules:
            done = subprocess.run(["gitleaks", "stdin", "--no-banner", "--report-format", "json", "--report-path", "-",
                                   "--ignore-gitleaks-allow", "--gitleaks-ignore-path", "/dev/null", "--log-level",
                                   "error", "--exit-code", str(_LEAKS)], input=data, capture_output=True,
                                  timeout=_TIMEOUT_S + len(data) / _FLOOR, env=env | {"GITLEAKS_CONFIG_TOML": each})
            if done.returncode not in (0, _LEAKS):
                raise GovError("ASSESS_SCAN_FAILED", f"gitleaks could not scan (exit code {done.returncode})", {})
            if done.returncode != _LEAKS:
                continue
            try:
                report = json.loads(done.stdout)
            except ValueError:
                report = [{"RuleID": "unreadable-report", "StartLine": 0}]
            for finding in report if isinstance(report, list) else []:
                if not isinstance(finding, dict):
                    continue
                rule = str(finding.get("RuleID") or "unnamed-rule")
                if rule == _COMMIT_RULE and re.fullmatch(r"[0-9a-fA-F]{40}", str(finding.get("Secret", ""))):
                    continue
                at = finding.get("StartLine") if isinstance(finding.get("StartLine"), int) else 0
                owner = next((rel for first, last, rel in spans if first <= at <= last), spans[0][2])
                self.found.add((owner, rule))
            del report
        del data


def _name_flags(rel: str) -> dict:
    parts = PurePosixPath(rel).parts
    folders = set(parts[:-1])
    flags = {}
    if folders & set(VENDORED_FOLDERS):
        flags["vendored"] = "folder"
    if folders & set(GENERATED_FOLDERS):
        flags["generated"] = "folder"
    elif GENERATED_NAMES.search(rel):
        flags["generated"] = "name"
    if MINIFIED_NAMES.search(rel):
        flags["minified"] = "name"
    return flags


def _content_flags(rel: str, head: bytes, longest: int, flags: dict) -> dict:
    if "generated" not in flags and GENERATED_HEADER.search(head[:2048]):
        flags["generated"] = "header"
    if "vendored" not in flags and VENDORED_HEADER.search(head[:1024]):
        flags["vendored"] = "header"
    if "minified" not in flags and PurePosixPath(rel).suffix.lower() in MINIFIED_SUFFIXES \
            and max((len(row) for row in head.split(b"\n")), default=0) >= MINIFIED_LINE <= longest:
        flags["minified"] = "header"  # a line of a thousand characters in the file's first lines
    return flags


def _free_memory() -> int | None:
    try:
        for row in Path("/proc/meminfo").read_text(encoding="ascii").splitlines():
            if row.startswith("MemAvailable:"):
                return int(row.split()[1]) * 1024
    except (OSError, ValueError):
        pass
    return None


def _session_figure() -> tuple[int | None, str]:
    """The resource gate's per-session figure (``working_size_bytes``), read from ``gov.resources.config``; never
    restated. None, with the reason, where the machine's gate file does not give it."""
    from gov.resources import config

    loaded = config.load()
    value = loaded["values"].get("working_size_bytes")
    if isinstance(value, int) and not isinstance(value, bool):
        return value, f"gov.resources.config working_size_bytes ({loaded['path']})"
    reasons = [item["why"] for item in loaded["faults"] if item.get("key") in ("working_size_bytes", config.FILE)]
    return None, "; ".join(reasons) or "working_size_bytes is not given"


def _peak() -> int:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024  # Linux: kilobytes


def assess(root: Path, out: Path) -> dict:
    """The assessment of ``HEAD`` of the repository at ``root``, written to ``<out>/memory-assessment.json``."""
    root, out = Path(root).resolve(), Path(out).resolve()
    if _inside(out, root):
        raise GovError("OUT_INSIDE_PROJECT", f"{out} lies inside the project {root}: the assessment writes nothing "
                       "in the repository, so its folder must lie outside it", {"out": str(out), "root": str(root)})
    started = time.monotonic()
    head = _git(root, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
    listing = _git(root, "ls-tree", "-r", "-z", "-l", head).decode("utf-8", "surrogateescape").split("\0")
    rules = _rules(root, head)
    files, total, languages, largest, tracked = 0, 0, {}, [], []
    lists = {"binary": [], "generated": [], "minified": [], "vendored": []}
    secrets, no_route, unscanned = [], [], []
    code_files = embeddable = 0
    blobs, scan = _Blobs(root), _Scan(rules or ())
    try:
        for entry in listing:
            meta, _, rel = entry.partition("\t")
            parts = meta.split()
            if not rel or len(parts) != 4 or parts[1] != "blob":
                continue  # a submodule (a commit) is no file of this repository
            mode, sha, size = parts[0], parts[2], int(parts[3]) if parts[3].isdigit() else 0
            files, total = files + 1, total + size
            tracked.append(rel)
            suffix = PurePosixPath(rel).suffix.lower()
            languages[LANGUAGE_NAMES.get(suffix, suffix or "no suffix")] = \
                languages.get(LANGUAGE_NAMES.get(suffix, suffix or "no suffix"), 0) + 1
            largest = sorted([*largest, (size, rel)], key=lambda item: (-item[0], item[1]))[:LARGEST]
            flags = _name_flags(rel)
            if mode == "120000":  # a link holds a path, not a text
                for kind, how in flags.items():
                    lists[kind].append({"path": rel, "by": how})
                continue
            data, _size = blobs.read(sha, SCAN_LIMIT_BYTES)
            binary = b"\0" in data[:8000]
            longest = 0 if binary else max((len(row) for row in data.split(b"\n")), default=0)
            if binary:
                lists["binary"].append({"path": rel, "by": "header"})
            else:
                _content_flags(rel, data[:HEAD], longest, flags)
                if rules is not None:
                    if size > SCAN_LIMIT_BYTES:
                        unscanned.append(rel)
                    else:
                        scan.add(rel, data)
            for kind, how in flags.items():
                lists[kind].append({"path": rel, "by": how})
            if not binary and (size > FILE_LIMIT_BYTES or longest > LINE_LIMIT):
                no_route.append({"path": rel, "reason": "over-limit"})
            if suffix in OTHER_CODE_SUFFIXES and not binary:
                no_route.append({"path": rel, "reason": "unsupported-language"})
            if suffix in CODE_GRAPH_SUFFIXES and not binary:
                code_files += 1
            if not binary:
                embeddable += 1
        if rules is not None:
            scan.flush()
        secrets = [{"path": rel, "rule": rule} for rel, rule in scan.found]
    finally:
        blobs.close()
    commits = int(_git(root, "rev-list", "--count", head).decode().strip() or 0)
    nodes, edges = int(code_files * NODES_PER_FILE), int(code_files * EDGES_PER_FILE)
    rss = int(BASE_RSS + edges * RSS_PER_EDGE)
    out.mkdir(parents=True, exist_ok=True)
    free_disk = shutil.disk_usage(out).free
    disk = int(code_files * DISK_PER_CODE_FILE + 2 * total)
    figure, source = _session_figure()
    peak = _peak()
    assessment = {
        "commit": head, "tracked_files": files, "tracked_bytes": total, "languages": dict(sorted(languages.items())),
        "commits": commits, "largest": [{"path": rel, "bytes": size} for size, rel in largest],
        **{kind: sorted(items, key=lambda item: item["path"]) for kind, items in lists.items()},
        "secrets": sorted(secrets, key=lambda item: (item["path"], item["rule"])),
        "secrets_scanned": rules is not None,
        "secrets_unscanned": sorted(unscanned),
        "no_route": sorted(no_route, key=lambda item: (item["path"], item["reason"])),
        "limits": {"file_limit_bytes": FILE_LIMIT_BYTES, "line_limit_chars": LINE_LIMIT,
                   "code_graph_suffixes": sorted(CODE_GRAPH_SUFFIXES)},
        "estimate": {
            "index_seconds": round(embeddable * EMBED_S_PER_FILE + code_files * GRAPH_S_PER_FILE),
            "peak_rss_bytes": rss, "disk_bytes": disk, "estimated_nodes": nodes, "estimated_edges": edges,
            "envelope": {**ENVELOPE, "source": "DEC-078", "within": nodes <= ENVELOPE["nodes"]
                         and edges <= ENVELOPE["edges"] and rss <= ENVELOPE["peak_rss_bytes"]},
            "free_memory_bytes": _free_memory(), "free_disk_bytes": free_disk},
        "peak_rss_bytes": peak, "session_figure_bytes": figure, "session_figure_source": source,
        "under_session_figure": None if figure is None else peak < figure,
        "seconds": round(time.monotonic() - started, 2),
    }
    (out / FILE).write_text(json.dumps(assessment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "tracked-paths.txt").write_text("".join(f"{rel}\n" for rel in sorted(tracked)), encoding="utf-8",
                                           errors="surrogateescape")
    return assessment


def sha256_of(out: Path) -> str:
    """The sha256 of the written ``memory-assessment.json`` at ``out``."""
    return sha256((Path(out) / FILE).read_bytes())
