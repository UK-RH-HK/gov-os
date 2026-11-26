"""The ``evidence`` block of a close record the landing writes (W2-115b fix IT-3; DEC-1242, DEC-1244), in the form
``close.schema.json`` states (``$defs/evidence``), one for each landed ticket: what ran for it on the tested commit,
and what the kept JUnit files of those runs state."""

from __future__ import annotations

from pathlib import Path

from gov.close import evidence as stated


def _reason(said: str) -> dict:
    """A selection's reason (``OWN``, ``COUPLING <path>``, ``OVERLAP <ticket> <path>``) in the block's form."""
    reason, _, rest = said.partition(" ")
    entry = {"reason": reason}
    if reason == "OVERLAP":
        entry["ticket"], _, rest = rest.partition(" ")
    if rest:
        entry["paths"] = [rest]
    return entry


def selected(clone: Path, commit: str, why: dict[str, list[str]], folder: str | None) -> list[dict]:
    """What the run ran for one ticket: the targets of its selection (``why``: target to reasons) that ``commit``
    holds, and its acceptance ``folder``, where it was run."""
    from gov.queue.command import _git

    listed = [{"target": target, "why": [_reason(r) for r in reasons]} for target, reasons in why.items()
              if _git(clone, "cat-file", "-e", f"{commit}:{target.split('::')[0].rstrip('/')}", ok=True) is not None]
    if folder and folder.rstrip("/") not in {e["target"].rstrip("/") for e in listed}:
        listed.append({"target": folder, "why": [{"reason": "ACCEPTANCE"}]})
    return listed


def block(root: Path, clone: Path, *, base: str, head: str, changed: list[str], selected: list[dict], full: bool,
          junit: list[Path]) -> dict:
    """The block of one ticket: ``base`` the integration head the run merged onto, ``head`` the tested commit,
    ``junit`` the JUnit files of its runs (those kept are listed, relative to ``root``)."""
    from gov.queue.command import _git

    kept = [path for path in junit if path.is_file()]
    read = [stated.read_junit(root, path) for path in kept]
    skips = [s for run in read for s in run["skips"]]
    return {"scope": "full" if full else "scoped", "why_full": [{"reason": "FULL_ASKED"}] if full else [],
            "base": base, "head": head, "tree": _git(clone, "rev-parse", f"{head}^{{tree}}").strip(),
            "changed": changed, "selected": selected, "left_out": [], "skips": skips, "skip_count": len(skips),
            "failures": [f for run in read for f in run["failures"]],
            "junit_xml": [path.relative_to(root).as_posix() for path in kept]}
