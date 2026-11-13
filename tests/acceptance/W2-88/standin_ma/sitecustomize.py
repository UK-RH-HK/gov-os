"""A stand-in for the engineer's memory assessment (I1), used only to show that S1's cases bite. It is not the product's code and is
never imported by a case: a child process loads it as ``sitecustomize`` when ``W2_88_STANDIN`` names this folder. It adds the
stage ``MA`` to ``gov adopt --lite`` (``--out <folder>``), reads HEAD's blobs one at a time with ``git cat-file`` and writes
``memory-assessment.json`` under ``--out`` only. Modes (``W2_88_STANDIN_MODE``):

``good``: as I1 states. ``leaky``: the record also holds the secret's value (the grep of outputs must fail).
``writes-repo``: the stage writes a file into the repository (the byte-identical comparison must fail).
``no-out-check``: ``--out`` inside the project is accepted (the refusal case must fail).
``loads-tree``: keeps every blob in memory until the end (F4's memory comparison must fail).
"""

import json
import os
import re
import resource
import shutil
import subprocess
import sys
from pathlib import Path

MODE = os.environ.get("W2_88_STANDIN_MODE", "good")
SECRET = re.compile(rb"AKIA[A-Z2-7]{16}")
CODE = {".py", ".md", ".txt", ".js", ".toml", ".yaml", ".yml", ".json", ".gitignore"}
LIMIT, READ_CHARS = 1_048_576, 32768
LANG = {".py": "python", ".md": "markdown", ".js": "javascript", ".toml": "toml", ".txt": "text"}


def _git(root, *args, data=None):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, input=data, check=True).stdout


def assess(root: Path, out: Path):
    from gov.adopt.project import refuse
    if MODE != "no-out-check" and (out.resolve() == root or root in out.resolve().parents):
        raise refuse("OUT_INSIDE_PROJECT", f"--out {out} lies inside the project")
    listing = _git(root, "ls-tree", "-r", "-l", "-z", "HEAD").decode("utf-8", "surrogateescape").split("\0")
    entries = []
    for line in listing:
        if line:
            meta, _, path = line.partition("\t")
            entries.append((path, int(meta.split()[3])))
    record = {"commit": _git(root, "rev-parse", "HEAD").decode().strip(), "tracked_files": len(entries),
              "tracked_bytes": sum(size for _, size in entries), "languages": {}, "largest": [], "binary": [],
              "generated": [], "minified": [], "vendored": [], "secrets": [], "no_route": []}
    record["commits"] = int(_git(root, "rev-list", "--count", "HEAD"))
    kept = []
    for path, size in entries:
        suffix = Path(path).suffix or Path(path).name
        name = LANG.get(suffix, suffix)
        record["languages"][name] = record["languages"].get(name, 0) + 1
        data = _git(root, "cat-file", "blob", f"HEAD:{path}")
        if MODE == "loads-tree":
            kept.append(data)
        if path.startswith("vendor/"):
            record["vendored"].append({"path": "vendor", "by": "folder"}) if not record["vendored"] else None
        if b"\0" in data[:8000]:
            record["binary"].append({"path": path, "by": "name"})
            continue
        head = data[:200].decode("utf-8", "replace")
        if "Code generated" in head or "DO NOT EDIT" in head:
            record["generated"].append({"path": path, "by": "header"})
        if ".min." in path:
            record["minified"].append({"path": path, "by": "name"})
        match = SECRET.search(data)
        if match:
            record["secrets"].append({"path": path, "rule": "aws-access-token"})
            if MODE == "leaky":
                record["leaked"] = match.group().decode()
        if size > LIMIT or any(len(l) > READ_CHARS for l in data.decode("utf-8", "replace").splitlines()):
            record["no_route"].append({"path": path, "reason": "over-limit"})
        elif suffix not in CODE:
            record["no_route"].append({"path": path, "reason": "unsupported-language"})
    record["largest"] = [{"path": p, "bytes": s} for p, s in sorted(entries, key=lambda e: -e[1])[:5]]
    meminfo = dict(l.split(":") for l in Path("/proc/meminfo").read_text().splitlines())
    record["estimate"] = {"index_seconds": 1.0, "peak_rss_bytes": 1, "disk_bytes": record["tracked_bytes"],
                          "envelope": {"files": 10_000}, "free_memory_bytes": int(meminfo["MemAvailable"].split()[0]) * 1024,
                          "free_disk_bytes": shutil.disk_usage(out.parent if out.parent.exists() else "/").free}
    record["peak_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    out.mkdir(parents=True, exist_ok=True)
    (out / "memory-assessment.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    if MODE == "writes-repo":
        (root / "ASSESSED.txt").write_text("written by the stage\n", encoding="utf-8")
    return {"stage": "MA", "record": str(out / "memory-assessment.json")}


def _install():
    from gov.adopt import command, stages
    command.STAGES = (*command.STAGES, "MA")
    original_arguments = command.add_arguments

    def add_arguments(parser):
        original_arguments(parser)
        parser.add_argument("--out", metavar="<folder>")
        parser.add_argument("--assessment", metavar="<folder>")
        for action in parser._actions:
            if action.dest == "stage":
                action.choices = tuple(action.choices) + ("MA",)

    command.add_arguments = add_arguments
    original_run = stages.run

    def run(root, args, config):
        if args.stage == "MA":
            return assess(Path(root), Path(args.out))
        return original_run(root, args, config)

    stages.run = run


try:
    _install()
except Exception as exc:  # noqa: BLE001
    sys.stderr.write(f"standin_ma: not installed: {exc!r}\n")
