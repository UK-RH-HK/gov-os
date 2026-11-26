"""The stale route (W2-212, DEC-1227 D3): the namespaces a path map marks ``stale_class`` (superseded, historical or
legacy) are kept out of every route of ``gov retrieve``'s default bundle, even a chunk indexed before the class existed,
and are found on purpose: the bundle's ``stale`` list, read from the files (never the index), for ``--include-stale``
or a question that names the file's path. Each entry is marked ``stale: true`` with its ``stale_class``."""

from __future__ import annotations

import os
import re
from pathlib import Path

from gov.config.loader import STALE_CLASS, read_yaml
from gov.retrieval import lexical

STALE_WORDS = {"superseded": "superseded", "historical": "historical", "legacy": "legacy", "archive": "historical"}
STALE_DESCRIBED = ("provenance", "retention", "sensitivity", "export_policy", "deletion_rebuild")


def stale_words(*texts) -> list[str]:
    """The stale words (``STALE_WORDS``) among the word parts of ``texts``, split on anything but letters and digits,
    case-insensitive: ``legacyish`` is no match."""
    found = []
    for text in texts:
        for word in re.split(r"[^a-z0-9]+", str(text).lower()):
            if word in STALE_WORDS and word not in found:
                found.append(word)
    return found


def unclassed(document) -> list[dict]:
    """Each namespace of a parsed path map that states no ``stale_class`` and says superseded, historical, legacy or
    archive in its name or paths. Stale as a whole (its name, or every one of its paths, says it):
    ``{namespace, words, stale_class}``. Only some of its paths (a catch-all namespace keeps live documents):
    ``{namespace, words, paths, move}``, ``paths`` those that say it. Reads no file; a map that is no map gives ``[]``."""
    spaces = document.get("namespaces") if isinstance(document, dict) else None
    found = []
    for name, space in (spaces.items() if isinstance(spaces, dict) else ()):
        if not isinstance(space, dict) or STALE_CLASS in space:
            continue
        paths = space.get("paths") if isinstance(space.get("paths"), list) else []
        words = stale_words(name, *paths)
        if not words:
            continue
        stale = [path for path in paths if stale_words(path)]
        if stale_words(name) or len(stale) == len(paths):
            found.append({"namespace": name, "words": words, "stale_class": STALE_WORDS[words[0]]})
        else:
            found.append({"namespace": name, "words": words, "paths": stale,
                          "move": f"if their documents are stale, move {', '.join(map(str, stale))} out of `{name}` "
                                  f"into a namespace of their own that states stale_class {STALE_WORDS[words[0]]} with "
                                  "lexical_policy `not indexed` and embedding_policy `not embedded`; the other paths "
                                  "stay as they are"})
    return found


EXCERPT_CHARS = 600
LISTED = 10  # entries a flag lists without the path named: the best matches of the question


def _rules(root: Path) -> list[tuple[str, str, re.Pattern]]:
    map_rel = f"{lexical.PROJECT_DIR}/path-map.yaml"
    place = Path(root) / map_rel
    document = read_yaml(place, "CONFIG_INVALID", map_rel) if place.is_file() else None
    namespaces = document.get("namespaces") if isinstance(document, dict) else None
    rules = []
    for name, entry in (namespaces.items() if isinstance(namespaces, dict) else ()):
        if isinstance(entry, dict) and entry.get(STALE_CLASS) and isinstance(entry.get("paths"), list):
            rules += [(name, entry[STALE_CLASS], lexical._pattern(pattern))
                      for pattern in entry["paths"] if isinstance(pattern, str)]
    return rules


def classifier(root: Path):
    """``path -> (namespace, stale_class)`` or None, for the path map's stale-class namespaces; reads the path map only."""
    rules = _rules(root)

    def of(rel: str):
        for name, kind, pattern in rules:
            if pattern.fullmatch(rel):
                return name, kind
        return None
    return of if rules else None


def _words(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if len(word) >= 3}


def find(root: Path, query: str, include: bool, denied=None) -> list[dict]:
    """The stale files for ``query``, read from disk: every tracked stale file the question names by path, and, when
    ``include``, the best matches of its words (at most ``LISTED``). ``denied(rel)`` is a role filter's refusal."""
    root = Path(root)
    of = classifier(root)
    if of is None:
        return []
    tracked = sorted(rel for rel in map(os.fsdecode, lexical._git(root, "ls-files", "-z").split(b"\0"))
                     if rel and of(rel) and (root / rel).is_file())
    wanted = _words(query)
    named, scored = [], []
    for rel in tracked:
        if denied is not None and denied(rel) is not None:
            continue
        try:
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        entry = {"path": rel, "namespace": of(rel)[0], "stale_class": of(rel)[1], "stale": True,
                 "excerpt": text[:EXCERPT_CHARS]}
        if rel in query:
            named.append(entry)
        elif include:
            score = len(wanted & (_words(rel) | _words(text)))
            if score:
                scored.append((-score, rel, entry))
    return named + [entry for *_, entry in sorted(scored, key=lambda row: row[:2])[:LISTED]]
