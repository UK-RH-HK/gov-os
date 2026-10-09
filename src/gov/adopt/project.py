"""What the stages of ``gov adopt --lite`` share: git, the evidence records and their chain, the classification.

Nothing here answers "none" for what it could not read: a git call that fails, a record that cannot be parsed and a
ref that does not resolve each end in a refusal that names the thing (DEC-449, DEC-454).
"""

from __future__ import annotations

import hashlib
import sqlite3
import subprocess
from pathlib import Path

import yaml

from gov.cli.errors import GovError

FOLDER = "governance/adoption"  # the tool's own records: no artefact of the project, so not in its inventory
STAGES = ("A0", "A1", "A2", "A3", "A4", "A5", "A6", "A8")
TITLES = {"A0": "safety baseline", "A1": "inventory", "A2": "classification", "A3": "target path map",
          "A4": "batched plan", "A5": "independent review of the path map", "A6": "controlled migration",
          "A8": "legacy import and retirement"}
MOVING = ("MOVE", "RENAME", "SPLIT", "MERGE", "EXTRACT")  # the actions that take an artefact to another path


def refuse(code: str, message: str, **details) -> GovError:
    return GovError("ADOPT_" + code, message, details)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def record_path(stage: str) -> str:
    return f"{FOLDER}/{stage}-{TITLES[stage].replace(' ', '-')}.md"


def _run(root: Path, args: tuple, ok: tuple, data: bytes | None = None) -> tuple[int, bytes]:
    try:
        done = subprocess.run(["git", "-C", str(root), "-c", "core.quotePath=false", *args], capture_output=True,
                              input=data, stdin=None if data is not None else subprocess.DEVNULL)
    except OSError as exc:
        raise refuse("GIT_FAILED", f"git {args[0]} could not be run in {root}: {exc}") from None
    if done.returncode not in ok:
        reason = " ".join(done.stderr.decode("utf-8", "replace").split())
        raise refuse("GIT_FAILED", f"git {' '.join(args)} failed in {root}: {reason}", exit_code=done.returncode)
    return done.returncode, done.stdout


def git(root: Path, *args: str) -> str:
    return _run(root, args, (0,))[1].decode("utf-8", "surrogateescape")


def resolve(root: Path, name: str) -> str | None:
    """The commit ``name`` resolves to; None where git answers that it resolves to none."""
    code, out = _run(root, ("rev-parse", "--verify", "--quiet", f"{name}^{{commit}}"), (0, 1))
    return out.decode().strip() if code == 0 else None


def tree(root: Path, rev: str = "HEAD") -> dict[str, str]:
    """Path -> blob id of every file of ``rev``."""
    listed = {}
    for line in git(root, "ls-tree", "-r", "-z", rev).split("\0"):
        if line:
            meta, _, path = line.partition("\t")
            listed[path] = meta.split()[2]
    return listed


def blob(root: Path, blob_id: str) -> bytes:
    return _run(root, ("cat-file", "blob", blob_id), (0,))[1]


def dirty(root: Path) -> list[str]:
    """Every path git reports as modified, staged or untracked."""
    entries, paths = git(root, "status", "--porcelain", "-z", "--untracked-files=all").split("\0"), []
    while entries:
        entry = entries.pop(0)
        if entry:
            paths.append(entry[3:])
            if entry[0] in "RC":  # a rename or a copy is followed by the path it came from
                paths.append(entries.pop(0))
    return paths


def require_repository(root: Path) -> None:
    """Refuse unless ``root`` is the top level of a git repository that has a commit and a clean tree."""
    code, top = _run(root, ("rev-parse", "--show-toplevel"), (0, 128))
    if code != 0 or Path(top.decode("utf-8", "surrogateescape").removesuffix("\n")).resolve() != root:
        raise refuse("NOT_A_REPOSITORY", f"{root} is not the top level of a git repository: nothing is adopted there")
    if resolve(root, "HEAD") is None:
        raise refuse("NO_COMMIT", f"{root} has no commit: there is no baseline to adopt from")
    paths = dirty(root)
    if paths:
        raise refuse("TREE_NOT_CLEAN", "the tree is not clean: " + ", ".join(paths), paths=paths)


def restore(root: Path, commit: str) -> None:
    """Back to ``commit``, which the stage found with a clean tree: what the stage staged or created is undone."""
    git(root, "reset", "-q", "--hard", commit)
    for rel in dirty(root):
        (root / rel).unlink(missing_ok=True)


def commit(root: Path, message: str, files: dict[str, str]) -> None:
    """Write ``files`` (path -> text) and commit them with what is staged; undone as a whole when that fails."""
    head = resolve(root, "HEAD")
    try:
        for rel, text in files.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text, encoding="utf-8")
        git(root, "add", "--", *files)
        if _run(root, ("diff", "--cached", "--quiet"), (0, 1))[0] == 1:  # run again with nothing new: no commit
            git(root, "commit", "-q", "-m", message)
    except (OSError, GovError):
        restore(root, head)
        raise


def frontmatter(text: str) -> dict | None:
    """The frontmatter of ``text``, None when it has none; ``ValueError`` when it cannot be read."""
    lines = [line.rstrip() for line in text.split("\n")]
    if lines[0] != "---":
        return None
    if "---" not in lines[1:]:
        raise ValueError("the frontmatter is not closed")
    try:
        data = yaml.safe_load("\n".join(lines[1:lines.index("---", 1)]))
    except yaml.YAMLError as exc:
        raise ValueError("the frontmatter is not valid YAML: " + " ".join(str(exc).split())) from None
    if not isinstance(data, dict):
        raise ValueError("the frontmatter is not a mapping")
    return data


def read_record(root: Path, tracked: dict, rel: str) -> tuple[dict, bytes]:
    """The frontmatter and the bytes of the committed record ``rel``; a refusal that names it otherwise."""
    if rel not in tracked:
        raise refuse("RECORD_MISSING", f"{rel} is not a committed file of the project", record=rel)
    data = blob(root, tracked[rel])
    try:
        head = frontmatter(data.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise refuse("RECORD_UNREADABLE", f"{rel} cannot be read: {exc}", record=rel) from None
    if head is None:
        raise refuse("RECORD_UNREADABLE", f"{rel} cannot be read: it has no frontmatter", record=rel)
    return head, data


def chain(root: Path, tracked: dict, stage: str) -> tuple[dict, dict]:
    """The records of every stage before ``stage`` and their hashes, each standing on the one before it."""
    records, hashes, previous = {}, {}, None
    for earlier in STAGES[:STAGES.index(stage)]:
        rel = record_path(earlier)
        if rel not in tracked:
            raise refuse("STAGE_MISSING", f"stage {stage} stands on stage {earlier}, which left no committed record "
                                          f"({rel}): run {earlier} first (the A5 verdict comes before any move)",
                         stage=earlier)
        head, data = read_record(root, tracked, rel)
        if head.get("stage") != earlier or head.get("stands_on") != previous:
            raise refuse("CHAIN_BROKEN", f"{rel} does not stand on the record of the stage before it as that record "
                                         f"is now: run the stages again from {earlier}", stage=earlier)
        records[earlier], hashes[earlier] = head, sha256(data)
        previous = hashes[earlier]
    return records, hashes


def record_text(stage: str, data: dict) -> str:
    head = {"id": f"ADOPT-{stage}", "type": "evidence", "status": "RECORDED", "state_class": "EVIDENCE",
            "stage": stage, **data}
    return ("---\n" + yaml.safe_dump(head, sort_keys=False, allow_unicode=True, width=120)
            + f"---\n\n# ADOPT-{stage}: {TITLES[stage]}\n\nWritten by `gov adopt --lite --stage {stage}`.\n")


def unknown(config: dict, tracked: dict) -> list[str]:
    """The tracked paths no namespace of the project's path map holds, as ``gov doctor`` matches them."""
    return [rel for rel, space in classify(config, tracked).items() if space is None]


def classify(config: dict, paths) -> dict[str, str | None]:
    """Path -> the namespace of the project's path map that holds it (None for none). Refuses without a path map."""
    from gov.doctor.command import _match_pattern  # doctor has no public matcher: the same one, not a second

    path_map = config.get("path-map.yaml")
    if not isinstance(path_map, dict) or not isinstance(path_map.get("namespaces"), dict):
        raise refuse("NO_PATH_MAP", "governance/project/path-map.yaml: the project has no path map with namespaces, "
                                    "so no artefact can be classified and none is known")
    spaces = {name: [p for p in (space.get("paths") or []) if isinstance(p, str)]
              for name, space in path_map["namespaces"].items() if isinstance(space, dict)}
    return {rel: next((name for name, patterns in spaces.items()
                       if any(_match_pattern(rel, pattern) for pattern in patterns)), None)
            for rel in paths if not rel.startswith(FOLDER + "/")}


def code_intelligence(config: dict) -> bool:
    capabilities = (config.get("path-map.yaml") or {}).get("capabilities")
    capability = capabilities.get("code_intelligence") if isinstance(capabilities, dict) else None
    return isinstance(capability, dict) and capability.get("enabled") is True


def record_graph(root: Path, strict: bool = True) -> tuple[list[dict], list[dict]]:
    """The records and the edges of ``HEAD``. With ``strict``, a record that cannot be read refuses and is named."""
    from gov import records, store

    try:
        invalid = store.load(root)["invalid"]
        if invalid and strict:
            raise refuse("RECORD_UNREADABLE", "the record graph cannot be established, records cannot be read: "
                         + "; ".join(f"{item['path']} ({item['reason']})" for item in invalid), invalid=invalid)
        return records.records(root), records.edges(root)
    except (OSError, sqlite3.Error) as exc:
        raise refuse("RECORD_GRAPH_UNREADABLE", f"the record graph cannot be read: {exc}") from None
