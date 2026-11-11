"""``gov adapters generate`` (W2-23 S2; W2-H050, W2-M229, W2-M232, W2-M312): the adapters from ``.rulesync/``, merged
into the programme's own files instead of written over them.

``rulesync generate`` runs into an empty temporary folder (the procedure of DEC-645), the held-out step applied to
its settings as the adapter check applies it (DEC-635); then:

- ``CLAUDE.md`` and ``AGENTS.md``: every line of the programme's own file stays, in its order; the generated text
  stands in one marked block after them (``<!-- gov:generated begin -->`` ... ``<!-- gov:generated end -->``), which
  the next run replaces where it stands;
- ``.claude/settings.json``: merged key by key, the programme's keys and list entries first and in their order, the
  generated keys and entries (hooks among them) after, and an ``env`` block that carries the auto-compact entry;
- every other generated file is written where the project has none; one that differs from the project's own is
  kept as it is and named (``kept``).
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
# W2-M229 (DEC-636): rulesync writes no env block, so the entry is set here. The value is DEC-636's; DEC-838 (standing)
# says no compaction threshold is set anywhere: the clash is the package P-W2-23-4 of this ticket's engineer return.
AUTO_COMPACT = {"CLAUDE_CODE_AUTO_COMPACT_WINDOW": "300000"}


def _refuse(code: str, message: str, **details) -> GovError:
    return GovError("ADAPTERS_" + code, message, details)


def generate_into(root: Path, folder: Path) -> dict[str, bytes]:
    """What ``rulesync generate`` writes from the project's ``.rulesync/`` into ``folder``: path -> bytes."""
    from gov.adapters import portability
    from gov.guard import heldout

    binary = portability._find_rulesync()
    if binary is None:
        raise _refuse("RULESYNC_ABSENT", "rulesync not found (PATH or RULESYNC_BIN): nothing is generated")
    if not (root / portability.SOURCES).is_dir():
        raise _refuse("NO_SOURCES", f"the project has no {portability.SOURCES}/ folder: nothing is generated")
    code, out, err = portability._run(binary, *portability.GENERATE, str((root / portability.SOURCES).resolve()),
                                      cwd=folder)
    if code != 0:
        raise _refuse("RULESYNC_FAILED", f"rulesync generate ended with {code}: {(err or out).strip()[-500:]}")
    if os.path.lexists(root / heldout.CONFIG_REL) and (folder / SETTINGS).is_file():
        try:
            heldout.write_read_rules(str(root), str(folder / SETTINGS))
        except Exception as exc:  # its text may quote the held-out file: the type only
            raise _refuse("HELD_OUT_STEP_FAILED", f"the held-out step failed ({type(exc).__name__})") from None
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


def merge_settings(own: dict | None, generated: dict) -> dict:
    merged = merge_value(own or {}, generated)
    env = merged.get("env") if isinstance(merged.get("env"), dict) else {}
    merged["env"] = {**env, **{key: value for key, value in AUTO_COMPACT.items() if key not in env}}
    return merged


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8") if path.is_file() else None
    except (OSError, UnicodeDecodeError) as exc:
        raise _refuse("FILE_UNREADABLE", f"{path} cannot be read ({exc}): nothing is written") from None


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
    for rel, content in writes.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            (root / rel).write_bytes(content)
        else:
            (root / rel).write_text(content, encoding="utf-8")
    return {"merged": merged, "written": sorted(written), "kept": sorted(kept)}
