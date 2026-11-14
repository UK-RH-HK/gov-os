p = "src/gov/rebuild/integration.py"
s = open(p).read()

s = s.replace('''- **While it builds,** the link points at the ready half, which nothing here writes: searches through the link are
  answered from it, complete, the whole time (F2).
"""
''', '''- **While it builds,** the link points at the ready half, which nothing here writes: searches through the link are
  answered from it, complete, the whole time (F2).

S2, ``--when-due`` (W2-116 pass 2b; P-W2-116-S2-INTERFACE Q1 (a), DEC-1157 (12)): a tick, run every few minutes, that
refreshes only when a refresh is due and otherwise builds nothing.

- **The settings** are ``integration_refresh`` of ``rebuild.yaml``: ``branch``, ``after_nightly`` (``verdict``: a glob
  relative to the project root, default ``DEFAULT_VERDICT``; ``latest``: ``"HH:MM"``) and ``second`` (``"HH:MM"``). A
  time is two digits, a colon, two digits, 24-hour; a missing or invalid time, a missing ``branch`` or no
  ``integration_refresh`` is ``REBUILD_CONFIG_INVALID`` naming the dotted key, with the value read, before anything
  is built. A verdict file *counts* once it holds a line ``verdict:`` or a JSON ``verdict`` key (a nightly still
  running holds neither).
- **The clock** is ``GOV_NOW`` (ISO 8601; no offset: local time) where set, else the real clock; an invalid one is
  ``REBUILD_CONFIG_INVALID`` (key ``GOV_NOW``). ``HH:MM`` times are wall-clock times on ``now``'s date; a verdict
  file's time is its modification time.
- **Due** (``due_reason``), one refresh with the reason ``after_nightly`` where both are: after the nightly, a counting
  verdict file later than the record's ``at`` (any, with no record), or ``now`` at or after today's ``latest`` with no
  ``after_nightly`` record on today's date; ``second``, ``now`` at or after today's ``second`` with no record at or
  after it.
- **The record** ``<link>.refresh.json`` (``at``, ``reason``, ``head``, ``status``, ``branch``) is written whole, by
  an atomic replace, after a refresh that switched or found the head built; ``at`` is ``now`` as the decision was
  taken, so a verdict file that lands during the build is later than it. A failed refresh leaves the record, so the
  next tick is due again. Not due: nothing is built or written, the status is ``not_due``.
"""
''')

s = s.replace('''import argparse
import fcntl
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
''', '''import argparse
import fcntl
import glob
import json
import os
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
''')

s = s.replace('''UNCHANGED, SWITCHED = "unchanged", "switched"
''', '''UNCHANGED, SWITCHED = "unchanged", "switched"
REFRESH_KEY = "integration_refresh"
RECORD_SUFFIX = ".refresh.json"
NOW_ENV = "GOV_NOW"
AFTER_NIGHTLY, SECOND, NOT_DUE = "after_nightly", "second", "not_due"
DEFAULT_VERDICT = "docs/close/nightly/NR-*.json"
_TIME = re.compile(r"([01]\\d|2[0-3]):([0-5]\\d)")
_VERDICT_LINE = re.compile(r"^verdict:", re.MULTILINE)
''')

s += '''

# --- S2: the two daily refresh times, ``--when-due`` -------------------------------------------------------------------


@dataclass(frozen=True)
class Refresh:
    """``integration_refresh`` of ``rebuild.yaml``, checked; the times as (hour, minute)."""

    branch: str
    verdict: str
    latest: tuple[int, int]
    second: tuple[int, int]


def _plain(value):
    """``value`` as a detail of an error: itself where JSON holds it, else its text."""
    try:
        json.dumps(value)
    except (TypeError, ValueError):
        return repr(value)
    return value


def _config_invalid(key: str, value, why: str, where: str | None = None) -> GovError:
    from gov.launch.store import SETTINGS_REL

    return GovError("REBUILD_CONFIG_INVALID", f"{where or SETTINGS_REL}: key '{key}': {why}: nothing is built",
                    {"key": key, "value": _plain(value)})


def _hour_minute(key: str, value) -> tuple[int, int]:
    found = _TIME.fullmatch(value) if isinstance(value, str) else None
    if found is None:
        raise _config_invalid(key, value, f"must be a time written \\"HH:MM\\" (24-hour, 00:00 to 23:59), not {value!r}")
    return int(found.group(1)), int(found.group(2))


def refresh_settings(root: Path) -> Refresh:
    """``integration_refresh`` as the project's ``rebuild.yaml`` states it; ``REBUILD_CONFIG_INVALID`` naming the dotted
    key where it is absent or any part of it is missing or invalid."""
    from gov.config.loader import read_yaml
    from gov.launch.store import SETTINGS_REL

    path = Path(root) / SETTINGS_REL
    document = None
    if path.is_file():
        try:
            document = read_yaml(path, "REBUILD_CONFIG_INVALID", SETTINGS_REL)
        except (GovError, OSError) as error:
            raise _config_invalid(REFRESH_KEY, None, f"{getattr(error, 'message', error)}") from None
    block = document.get(REFRESH_KEY) if isinstance(document, dict) else None
    if not isinstance(block, dict):
        raise _config_invalid(REFRESH_KEY, block, "is required with --when-due and must be a map of branch, "
                                                  "after_nightly and second")
    branch = block.get("branch")
    if not isinstance(branch, str) or not branch.strip():
        raise _config_invalid(f"{REFRESH_KEY}.branch", branch, "must name the integration branch")
    nightly = block.get("after_nightly")
    if nightly is not None and not isinstance(nightly, dict):
        raise _config_invalid(f"{REFRESH_KEY}.after_nightly", nightly, "must be a map of verdict and latest")
    nightly = nightly or {}
    verdict = nightly.get("verdict", DEFAULT_VERDICT)
    if not isinstance(verdict, str) or not verdict.strip():
        raise _config_invalid(f"{REFRESH_KEY}.after_nightly.verdict", verdict, "must be a glob, relative to the "
                                                                              "project root")
    return Refresh(branch, verdict,
                   _hour_minute(f"{REFRESH_KEY}.after_nightly.latest", nightly.get("latest")),
                   _hour_minute(f"{REFRESH_KEY}.second", block.get("second")))


def now() -> datetime:
    """The time the decisions are taken at: ``GOV_NOW`` (ISO 8601; without an offset it is local time) where set, else
    the real clock to the second. Always with an offset. An invalid ``GOV_NOW`` is ``REBUILD_CONFIG_INVALID``."""
    given = os.environ.get(NOW_ENV)
    if given is None:
        return datetime.now().astimezone().replace(microsecond=0)
    try:
        return datetime.fromisoformat(given.strip()).astimezone()
    except ValueError:
        raise _config_invalid(NOW_ENV, given, "must be an ISO 8601 date and time (2026-11-13T09:30:00+01:00)",
                              where="the environment") from None


def at_time(day: datetime, hour_minute: tuple[int, int], days_back: int = 0) -> datetime:
    """The wall-clock time ``hour_minute`` on ``day``'s date, ``days_back`` days earlier, in ``day``'s offset."""
    return (day - timedelta(days=days_back)).replace(hour=hour_minute[0], minute=hour_minute[1], second=0,
                                                     microsecond=0)


def hhmm(hour_minute: tuple[int, int]) -> str:
    return f"{hour_minute[0]:02d}:{hour_minute[1]:02d}"


def _counts(text: str) -> bool:
    """A verdict file counts once it holds a line ``verdict:`` or is JSON with a ``verdict`` key."""
    if _VERDICT_LINE.search(text):
        return True
    try:
        document = json.loads(text)
    except ValueError:
        return False
    return isinstance(document, dict) and "verdict" in document


def verdict_times(root: Path, pattern: str) -> list[datetime]:
    """The modification time of every counting verdict file the glob (relative to ``root``) matches, oldest first."""
    found = []
    for name in glob.glob(os.path.join(str(root), pattern), recursive=True):
        try:
            path = Path(name)
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if _counts(text):
                found.append(datetime.fromtimestamp(path.stat().st_mtime).astimezone())
        except OSError:
            continue  # a file that cannot be read has no verdict that counts
    return sorted(found)


def record_path(link: Path) -> Path:
    return link.with_name(link.name + RECORD_SUFFIX)


def read_record(link: Path) -> dict | None:
    """The scheduled refreshes' record beside ``link``; None where there is none or it is no JSON map."""
    try:
        document = json.loads(record_path(link).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return document if isinstance(document, dict) else None


def _instant(text) -> datetime | None:
    try:
        return datetime.fromisoformat(text).astimezone() if isinstance(text, str) else None
    except ValueError:
        return None


def due_reason(settings: Refresh, when: datetime, record: dict | None, verdicts: list[datetime]) -> str | None:
    """Why a refresh is due at ``when`` (``AFTER_NIGHTLY`` before ``SECOND`` where both), or None (module docstring)."""
    last = _instant(record.get("at")) if record else None  # a record with no readable ``at`` is none
    if any(last is None or seen > last for seen in verdicts):
        return AFTER_NIGHTLY
    if when >= at_time(when, settings.latest):
        today = last is not None and last.astimezone(when.tzinfo).date() == when.date()
        if not (today and record.get("reason") == AFTER_NIGHTLY):
            return AFTER_NIGHTLY
    second = at_time(when, settings.second)
    if when >= second and (last is None or last < second):
        return SECOND
    return None


def last_due(settings: Refresh, when: datetime, verdicts: list[datetime]) -> tuple[datetime, str] | None:
    """The last time at or before ``when`` that a refresh fell due, with what made it so: the newest counting verdict
    file, ``second`` today and yesterday, and ``latest`` today and yesterday where no counting verdict file's time
    falls on that date before it; None where none is at or before ``when``."""
    found: list[tuple[datetime, str]] = []
    seen = [at for at in verdicts if at <= when]
    if seen:
        found.append((max(seen), "the nightly's newest verdict file"))
    for back in (0, 1):
        second = at_time(when, settings.second, back)
        if second <= when:
            found.append((second, f"the second time {hhmm(settings.second)}"))
        latest = at_time(when, settings.latest, back)
        if latest <= when and not any(at < latest and at.astimezone(latest.tzinfo).date() == latest.date()
                                      for at in verdicts):
            found.append((latest, f"the nightly's latest time {hhmm(settings.latest)} with no verdict before it"))
    return max(found) if found else None


def _write_record(link: Path, record: dict) -> None:
    """The record written whole, by an atomic replace beside it."""
    path = record_path(link)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(json.dumps(record, indent=2) + "\\n", encoding="utf-8")
        os.replace(temporary, path)
    except OSError as error:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise _failed(f"the refresh's record {path} could not be written: {error}; the next tick is due again",
                      {"record": str(path)}) from None


def refresh_when_due(root: Path, branch: str) -> dict:
    """``gov rebuild --integration <branch> --when-due`` (module docstring): the refresh where one is due, its result with
    ``integration.reason`` and the record written; else ``integration.status`` ``not_due`` and nothing built or written."""
    root = Path(root)
    settings = refresh_settings(root)
    when = now()
    link = place(root)
    record = read_record(link)
    reason = due_reason(settings, when, record, verdict_times(root, settings.verdict))
    if reason is None:
        return {"integration": {"status": NOT_DUE, "branch": branch, "link": str(link), "last_refresh": record}}
    result = refresh(root, branch)
    result["integration"]["reason"] = reason
    _write_record(link, {"at": when.isoformat(), "reason": reason, "head": result["integration"]["head"],
                         "status": result["integration"]["status"], "branch": branch})
    return result
'''
open(p, "w").write(s)

p = "src/gov/rebuild/command.py"
s = open(p).read()
s = s.replace('''``--no-embeddings``: it seeds itself, and a build without its semantic store is never switched to.
''', '''``--no-embeddings``: it seeds itself, and a build without its semantic store is never switched to. With
``--when-due`` (W2-116 S2) it refreshes only when ``integration_refresh`` of ``rebuild.yaml`` says one is due, and
writes ``<link>.refresh.json``; otherwise it builds nothing and says ``not_due`` (``gov.rebuild.integration``).
''')
s = s.replace('''                             "link to it only when the build succeeded; nothing at an unchanged head")
''', '''                             "link to it only when the build succeeded; nothing at an unchanged head")
    parser.add_argument("--when-due", dest="when_due", action="store_true",
                        help="with --integration: refresh only when one is due by integration_refresh in "
                             "governance/project/rebuild.yaml (after the nightly's verdict, or at its latest time; "
                             "once the second time has passed); otherwise build nothing and say not_due")
''')
s = s.replace('''    branch = getattr(args, "integration", None)
    if branch is not None:
        from gov.cli.errors import GovError
        from gov.rebuild import integration
''', '''    branch = getattr(args, "integration", None)
    when_due = getattr(args, "when_due", False)
    if when_due and branch is None:
        from gov.cli.errors import GovError

        raise GovError("REBUILD_FAILED", "--when-due is only valid with --integration <branch>: nothing is built",
                       {"flags": ["--when-due"]})
    if branch is not None:
        from gov.cli.errors import GovError
        from gov.rebuild import integration
''')
s = s.replace('''        return integration.refresh(Path(root), branch)
''', '''        return (integration.refresh_when_due if when_due else integration.refresh)(Path(root), branch)
''')
open(p, "w").write(s)
