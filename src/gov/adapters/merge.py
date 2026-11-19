"""``gov adapters generate`` (W2-23 S2; W2-H050, W2-M229, W2-M232, W2-M312): the adapters from ``.rulesync/``, merged
into the programme's own files instead of written over them.

``rulesync generate`` runs into an empty temporary folder (the procedure of DEC-645); nothing is added to what it
writes (the held-out step that wrote a ``Read`` deny per held-out path is retired, W2-208, EMERGENCY-2 2.7); then:

- ``CLAUDE.md`` and ``AGENTS.md``: every line of the programme's own file stays, in its order; the generated text
  stands in one marked block after them (``<!-- gov:generated begin -->`` ... ``<!-- gov:generated end -->``), which
  the next run replaces where it stands;
- ``.claude/settings.json``: merged key by key, the programme's keys and list entries first and in their order, the
  generated keys and entries (hooks among them) after, and an ``env`` block merged the same way (no ``env`` key is
  added when neither side holds one);
- every other generated file is written where the project has none; one that differs from the project's own is
  kept as it is and named (``kept``);
- in an adopted repository (not Gov OS's own source tree) whose kernel holds a ``templates/`` folder, the eight role
  template copies under ``.claude/templates/`` are written byte for byte from it: an absent copy written, a differing
  one replaced, an equal one left alone (``templates``; W2-153 S-ADOPTED, DEC-1192 (2)). In Gov OS's own repository
  an ACT writes them (DEC-315) and generate does not.

``gov update`` regenerates through ``forget_generated`` first (W2-17): a generated file whose bytes are still what the
old release's ``.rulesync/`` generates is removed, so the regeneration writes the new release's (a file the project
changed is kept and named); ``.claude/settings.json`` loses what the old generation merged into it
(``unmerge_value``), so the new release's hooks replace the old ones instead of standing beside them. ``generate``
itself is unchanged for every other caller.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from gov.cli.errors import GovError

BEGIN, END = "<!-- gov:generated begin -->", "<!-- gov:generated end -->"
TEXTS = ("CLAUDE.md", "AGENTS.md")
SETTINGS = ".claude/settings.json"
# DEC-838: every session uses its model's full window; no launch sets a compaction threshold, so nothing is forced in.
AUTO_COMPACT = {}


def _refuse(code: str, message: str, **details) -> GovError:
    return GovError("ADAPTERS_" + code, message, details)


def generate_into(root: Path, folder: Path) -> dict[str, bytes]:
    """What ``rulesync generate`` writes from the project's ``.rulesync/`` into ``folder``: path -> bytes."""
    from gov.adapters import portability

    binary = portability._find_rulesync()
    if binary is None:
        raise _refuse("RULESYNC_ABSENT", "rulesync not found (PATH or RULESYNC_BIN): nothing is generated")
    if not (root / portability.SOURCES).is_dir():
        raise _refuse("NO_SOURCES", f"the project has no {portability.SOURCES}/ folder: nothing is generated")
    code, out, err = portability._run(binary, *portability.GENERATE, str((root / portability.SOURCES).resolve()),
                                      cwd=folder)
    if code != 0:
        raise _refuse("RULESYNC_FAILED", f"rulesync generate ended with {code}: {(err or out).strip()[-500:]}")
    return {path.relative_to(folder).as_posix(): path.read_bytes()
            for path in sorted(folder.rglob("*")) if path.is_file()}


def merge_text(own: str | None, generated: str) -> str:
    """The programme's text with the generated text in its marked block: replaced where it stands, else after."""
    block = f"{BEGIN}\n{generated.rstrip(chr(10))}\n{END}\n"
    if not own:
        return block
    lines = own.splitlines(keepends=True)
    begin = next((i for i, line in enumerate(lines) if line.strip() == BEGIN), None)
    end = next((i for i, line in enumerate(lines) if line.strip() == END and begin is not None and i > begin), None)
    if begin is not None and end is not None:
        return "".join(lines[:begin]) + block + "".join(lines[end + 1:])
    if begin is not None or any(line.strip() == END for line in lines):
        raise _refuse("BLOCK_BROKEN", f"the file holds one of {BEGIN} and {END} without the other: it is not "
                      "merged, and nothing is written")
    return own + ("" if own.endswith("\n") else "\n") + "\n" + block


def merge_value(own, generated):
    """Key by key: the programme's keys and list entries first and kept; what the generated value adds, after."""
    if isinstance(own, dict) and isinstance(generated, dict):
        merged = {key: merge_value(value, generated[key]) if key in generated else value for key, value in own.items()}
        merged.update({key: value for key, value in generated.items() if key not in own})
        return merged
    if isinstance(own, list) and isinstance(generated, list):
        return own + [item for item in generated if item not in own]
    return own


def unmerge_value(own, generated):
    """The programme's value without what the generated value put in (W2-17): an equal value dropped, a map key by key,
    a list entry by entry, a map or list emptied by it dropped; what the programme changed stays."""
    if isinstance(own, dict) and isinstance(generated, dict):
        rest = {}
        for key, value in own.items():
            if key not in generated:
                rest[key] = value
            elif value == generated[key]:
                continue
            elif isinstance(value, (dict, list)) and type(value) is type(generated[key]):
                left = unmerge_value(value, generated[key])
                if left:
                    rest[key] = left
            else:
                rest[key] = value
        return rest
    if isinstance(own, list) and isinstance(generated, list):
        return [item for item in own if item not in generated]
    return own


def forget_generated(root: Path, previous: dict[str, bytes], write, delete) -> list[str]:
    """Before ``gov update`` regenerates (W2-17): ``previous`` is what the old ``.rulesync/`` generates (path ->
    bytes). A project file still equal to it is deleted (``delete(rel)``); ``.claude/settings.json`` is written without
    the old generation's entries (``write(rel, bytes)``); ``CLAUDE.md`` and ``AGENTS.md`` are left to their block.
    Returns the generated files the project changed, which are kept."""
    kept = []
    for rel, data in sorted(previous.items()):
        path = Path(root) / rel
        if rel in TEXTS or path.is_symlink() or not path.is_file():
            continue
        if rel == SETTINGS:
            try:
                own, generated = json.loads(path.read_text(encoding="utf-8")), json.loads(data.decode("utf-8"))
            except (OSError, UnicodeDecodeError, ValueError):
                continue
            if isinstance(own, dict) and isinstance(generated, dict):
                write(rel, (json.dumps(unmerge_value(own, generated), indent=2, ensure_ascii=False) + "\n").encode())
            continue
        if path.read_bytes() == data:
            delete(rel)
        else:
            kept.append(rel)
    return kept


def merge_settings(own: dict | None, generated: dict) -> dict:
    merged = merge_value(own or {}, generated)
    env = merged.get("env") if isinstance(merged.get("env"), dict) else {}
    extra = {key: value for key, value in AUTO_COMPACT.items() if key not in env}
    if extra:  # an empty block carries nothing: no env key is added for it
        merged["env"] = {**env, **extra}
    return merged


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8") if path.is_file() else None
    except (OSError, UnicodeDecodeError) as exc:
        raise _refuse("FILE_UNREADABLE", f"{path} cannot be read ({exc}): nothing is written") from None


def _is_source_tree(root: Path) -> bool:
    """True when ``root`` is Gov OS's own source tree: it holds every marker ``fabric.shipped`` looks for."""
    from gov.adopt.fabric import MARKERS
    return all((root / marker).exists() for marker in MARKERS)


def _template_copies(root: Path) -> tuple[dict[str, bytes], list[str], list[str]] | None:
    """``(writes, written, replaced)`` for the template copies of an adopted repository, or None where there is no
    step (Gov OS's own source tree, or a kernel without a ``templates/`` folder). Refuses a kit that lacks one of the
    eight, and a copy's path that is not a file."""
    from gov.adapters import portability
    if _is_source_tree(root):
        return None
    folder = portability.kernel_templates(root)
    if folder is None:
        return None
    missing = [str((folder / f"{stem}.md").relative_to(root)) for stem in portability.TEMPLATE_COPIES
               if not (folder / f"{stem}.md").is_file()]
    if missing:
        raise _refuse("TEMPLATE_MISSING", f"the kit's templates lack {', '.join(missing)}: nothing is written",
                      missing=missing)
    state = {finding["file"]: finding["code"] for finding in portability._template_findings(root)}
    writes, written, replaced = {}, [], []
    for stem in portability.TEMPLATE_COPIES:
        rel = f"{portability.TEMPLATES_REL}/{stem}.md"
        if rel not in state:
            continue
        if os.path.lexists(root / rel) and not (root / rel).is_file():
            raise _refuse("TEMPLATE_COPY_UNWRITABLE", f"{rel} exists and is not a file: nothing is written")
        writes[rel] = (folder / f"{stem}.md").read_bytes()
        (written if state[rel] == "TEMPLATE_COPY_MISSING" else replaced).append(rel)
    return writes, sorted(written), sorted(replaced)


def generate(root: Path) -> dict:
    """Generate, merge, write. Everything is merged before anything is written."""
    with tempfile.TemporaryDirectory(prefix="gov-adapters-") as fresh:
        made = generate_into(root, Path(fresh))
    writes, merged, kept = {}, [], []
    for rel in TEXTS:
        if rel in made:
            writes[rel] = merge_text(_read(root / rel), made[rel].decode("utf-8"))
            merged.append(rel)
    if SETTINGS in made:
        own = _read(root / SETTINGS)
        try:
            own_value = json.loads(own) if own is not None else None
            generated = json.loads(made[SETTINGS].decode("utf-8"))
        except ValueError as exc:
            raise _refuse("SETTINGS_UNREADABLE", f"{SETTINGS} is not JSON ({exc}): nothing is written") from None
        if own_value is not None and not isinstance(own_value, dict):
            raise _refuse("SETTINGS_UNREADABLE", f"{SETTINGS} is not a JSON object: nothing is written")
        writes[SETTINGS] = json.dumps(merge_settings(own_value, generated), indent=2, ensure_ascii=False) + "\n"
        merged.append(SETTINGS)
    written = []
    for rel, data in made.items():
        if rel in writes:
            continue
        path = root / rel
        if not os.path.lexists(path):
            writes[rel] = data
            written.append(rel)
        elif not path.is_file() or path.read_bytes() != data:
            kept.append(rel)
    copies = _template_copies(root)
    if copies is not None:
        writes.update(copies[0])
    for rel, content in writes.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            (root / rel).write_bytes(content)
        else:
            (root / rel).write_text(content, encoding="utf-8")
    result = {"merged": merged, "written": sorted(written), "kept": sorted(kept)}
    if copies is not None:
        result["templates"] = {"written": copies[1], "replaced": copies[2]}
    return result
