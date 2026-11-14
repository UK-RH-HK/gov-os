"""The one adapter to ``gov.retrieval.measure``'s private names (ruling 3 of the CTO; Interface items 8, 9, 10; S2, S3, S5).

Every other module of the memory audit asks this one: it loads the audit's questions as the standing retrieval measure
loads them (``_load``: gold re-anchored at the measured root, source families), and matches an evidence item or a
citation against a question's gold places with the measure's own ``_match`` (DEC-833, DEC-860). Nothing else imports
those names, so a change in the measure's internals is a change in this file only.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from gov.retrieval import measure as M

APART = "nonexistent-id"  # the category scored apart: right when the answer is not found; it still counts in n (ruling 8)
MeasureError = M.MeasureError


class MatcherError(Exception):
    """The set cannot be loaded as the measure loads it. The message names no question, path or text (F1)."""


def questions(sets_root, set_name: str, part: str, repo, only: str | None = None, default=None) -> list[dict]:
    """The questions of ``<sets root>/fixtures/evaluation/<set>/<part>/*.yaml`` in file-name order, each as
    ``gov.retrieval.measure._load`` returns it (``id``, ``question``, ``sources`` as matchable entries, ``unresolved``)
    with the YAML's own ``gold`` (the gold answer), ``category``, ``keyword``, ``raw_sources``, ``apart`` and the
    question's ``commit`` added.
    ``only`` is a file's stem: the one-file form (W2-187 I6), which loads that question alone (none when it has no
    file). ``default`` is the set's entry when the sets root's path map holds none yet."""
    root, repo = Path(sets_root).resolve(), Path(repo).resolve()
    try:
        entry = M.evaluation_sets(str(root)).get(set_name)
    except M.PolicyError:
        if default is None:
            raise MatcherError("set") from None
        entry = None
    entry = default if entry is None else entry
    if not isinstance(entry, dict) or M.set_fault(entry):
        raise MatcherError("set")
    if part == "hidden" and M._measured(entry, root):  # a session the set measures never opens its hidden part
        raise MatcherError("measured role")
    quoting = M._Part("/q", [*entry.get("visible", []), *entry["hidden"], f"{M.EVALUATION}/**"], "")
    declared = M.families(root, repo)
    folder = root / M.EVALUATION / set_name / part
    cache, out = {}, []
    files = ([folder / f"{only}.yaml"] if only is not None and (folder / f"{only}.yaml").is_file()
             else [] if only is not None else sorted(folder.glob("*.yaml")) if folder.is_dir() else [])
    for file in files:
        q = M._load(file, part, repo, quoting, declared, cache)
        raw = yaml.safe_load(file.read_text(encoding="utf-8"))
        q.update(gold=raw.get("gold_answer"), category=raw.get("category"), keyword=raw.get("keyword") is True,
                 raw_sources=raw.get("sources"), apart=raw.get("category") == APART, commit=raw.get("commit"))
        out.append(q)
    return out


def section(lines: list[str], heading) -> list[str] | None:
    """The ``#`` heading's section of a file's lines, as ``measure._span`` takes it: from the first line equal to the
    heading (trailing whitespace removed) to the line before the next heading of the same or a higher level, or the end
    of the file; ``None`` when the heading is not found or is not a ``#`` heading."""
    at = next((i for i, line in enumerate(lines) if line.rstrip() == str(heading).rstrip()), None)
    mark = M._HEADING.match(lines[at]) if at is not None else None
    if not mark:
        return None
    level = len(mark.group(1))
    end = next((j for j in range(at + 1, len(lines))
                if (m := M._HEADING.match(lines[j])) and len(m.group(1)) <= level), len(lines))
    return lines[at:end]


def section_changed(source: dict, base, repo, cache: dict) -> bool:
    """W2-61h's N2 (b) (DEC-1180 (1)): a heading-cited source whose section's text at the source's own commit (its
    ``commit``, else the question's ``base``) differs from the section's text in ``repo`` (the head). A source with no
    commit, no ``#`` heading, a heading missing at either side or a file git cannot show is not listed; nothing is
    written."""
    path, heading = source.get("path"), source.get("heading")
    commit = next((str(c).strip() for c in (source.get("commit"), base) if c is not None and str(c).strip()), "")
    if heading is None or not commit or not isinstance(path, str) or path.startswith(f"{M.EVALUATION}/"):
        return False
    try:
        now = (Path(repo) / path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return False
    then = M._lines_at(Path(repo), commit, path, cache)
    old, new = (section(then, heading) if then is not None else None), section(now, heading)
    return old is not None and new is not None and old != new


def hit(item, q: dict) -> bool:
    """Whether the evidence item ``(path, start_line, end_line, text)`` lies in a gold place of ``q`` (the measure's
    own matcher: its span, and a source family's official copy)."""
    return any(M._match(item, entry) for entry in q["sources"])


def text_of(repo, path: str, first: int, last: int) -> str:
    try:
        lines = (Path(repo) / path).read_text(errors="replace").splitlines(keepends=True)
    except OSError:
        return ""
    return "".join(lines[max(0, first - 1):last])


def cited(repo, q: dict, citations) -> bool:
    """Whether any cited ``(path, first, last)`` is a gold place of ``q``."""
    return any(hit((p, a, z, text_of(repo, p, a, z)), q) for p, a, z in citations)


def names_the_ids(result: dict, question: str) -> bool:
    """The product stopped with UNRESOLVED_IDS and its gaps name every id the question names."""
    from gov.retrieval import lexical
    if (result or {}).get("stopping_reason") != "UNRESOLVED_IDS":
        return False
    named = set(lexical.ids_in(question))
    gaps = {g.get("id") for g in (result.get("gaps") or []) if isinstance(g, dict)}
    return bool(named) and named <= gaps
