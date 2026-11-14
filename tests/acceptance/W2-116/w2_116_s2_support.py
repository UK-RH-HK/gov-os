"""Support code for the W2-116 pass 2b cases (S2 and R2-F3), added beside ``w2_116_support`` (which it only uses).

Public interfaces only (README, "Pass 2b"): ``gov rebuild --json --integration <branch> --when-due``, the
``<link>.refresh.json`` record beside the link, ``gov status --json``'s ``integration_store`` part,
``governance/project/rebuild.yaml``'s ``integration_refresh`` block, ``GOV_NOW``, and ``gov retrieve --continue``.

The clock is planted with ``GOV_NOW`` (an ISO 8601 instant; with an offset it is the wall clock of that offset), and a
verdict file's time with ``os.utime``: no case sleeps for the clock.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path

import w2_116_support as support

MISSING = object()                      # a key left out of the planted configuration
VERDICT_GLOB = ".gov-runtime/nightly/NR-*"   # under the (ignored) runtime folder: ``land`` never commits a verdict file
VERDICT_DIR = ".gov-runtime/nightly"
DEFAULT_GLOB_FILE = "docs/close/nightly/NR-1.json"   # the default glob, ``docs/close/nightly/NR-*.json``
UTC = dt.timezone.utc

# A fixed day for the cases that plant the whole clock (the record's ``at`` is ``GOV_NOW``, never the real clock).
DAY1 = dt.date(2026, 6, 10)
DAY2 = dt.date(2026, 6, 11)


def at(day, hhmm, zone=UTC):
    hour, minute = (int(part) for part in hhmm.split(":"))
    return dt.datetime(day.year, day.month, day.day, hour, minute, tzinfo=zone)


# --------------------------------------------------------------------------
# The configuration
# --------------------------------------------------------------------------

def _yaml(value):
    return json.dumps(value)            # JSON is YAML: the value is read back exactly as planted


def config_text(box, *, branch=support.BRANCH, latest="10:00", second="18:00", verdict=VERDICT_GLOB,
                refresh=True, store=True):
    """``rebuild.yaml`` with the box's temporary lock, the link (``integration_store``) and, unless ``refresh`` is
    false, the ``integration_refresh`` block; a value of ``MISSING`` leaves its key out. ``verdict`` None leaves the
    glob to its default."""
    text = f"slow_after_s: 600\nlock: {_yaml(str(box.lock))}\n"
    if store:
        text += f"integration_store: {_yaml(str(box.link))}\n"
    if not refresh:
        return text
    text += "integration_refresh:\n"
    if branch is not MISSING:
        text += f"  branch: {_yaml(branch)}\n"
    if latest is not MISSING or verdict is not None:
        text += "  after_nightly:\n"
        if verdict is not None:
            text += f"    verdict: {_yaml(verdict)}\n"
        if latest is not MISSING:
            text += f"    latest: {_yaml(latest)}\n"
    if second is not MISSING:
        text += f"  second: {_yaml(second)}\n"
    return text


def plant_config(box, project, commit=True, **kwargs):
    support.write(project / support.SETTINGS_REL, config_text(box, **kwargs))
    if commit:
        support.git(project, "add", "-A")
        support.git(project, "commit", "-q", "--allow-empty", "-m", "W2-116 pass 2b: the refresh times")


# --------------------------------------------------------------------------
# The clock, the verdict files and the record
# --------------------------------------------------------------------------

def now_env(env, now):
    return {**env, "GOV_NOW": now.isoformat()}


def plant_verdict(project, name, text, when, folder=VERDICT_DIR):
    path = support.write(Path(project) / folder / name, text)
    stamp = when.timestamp()
    os.utime(path, (stamp, stamp))
    return path


LINE_VERDICT = "nightly run NR\nverdict: PASS\n"
JSON_VERDICT = json.dumps({"run": "NR", "verdict": "PASS"}) + "\n"
NO_VERDICT_TEXT = "nightly run NR\nstill running: no verdict yet\n"
NO_VERDICT_JSON = json.dumps({"run": "NR", "state": "running"}) + "\n"


def record_path(box):
    return box.link.with_name(box.link.name + ".refresh.json")


def record(box):
    path = record_path(box)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def record_bytes(box):
    path = record_path(box)
    return path.read_bytes() if path.is_file() else None


def instant(text):
    value = dt.datetime.fromisoformat(str(text))
    assert value.tzinfo is not None, f"{text!r} is no ISO instant with an offset"
    return value


def when_due(project, env, now, branch=support.BRANCH):
    """``gov rebuild --json --integration <branch> --when-due`` with the clock at ``now``."""
    return support.gov(project, now_env(env, now), "rebuild", "--json", support.INTEGRATION, branch, "--when-due")


def integration_of(run):
    value = run.result.get("integration")
    return value if isinstance(value, dict) else {}


def assert_due(run, reason, what):
    assert run.ok, f"{what}: the tick did not succeed\n{run.describe()}"
    found = integration_of(run)
    assert found.get("reason") == reason, f"{what}: due, but not with reason {reason!r}: {found}\n{run.describe()}"
    assert found.get("status") in ("switched", "unchanged"), f"{what}: no refresh ran: {found}\n{run.describe()}"


def assert_not_due(run, box, branch, what):
    assert run.ok, f"{what}: the tick did not succeed\n{run.describe()}"
    found = integration_of(run)
    assert found.get("status") == "not_due", f"{what}: expected not_due, got {found}\n{run.describe()}"
    assert found.get("branch") == branch, f"{what}: not_due names no branch {branch!r}: {found}"
    assert found.get("link") == str(box.link), f"{what}: not_due names no link {str(box.link)!r}: {found}"
    assert "last_refresh" in found, f"{what}: not_due has no last_refresh: {found}"
    assert found["last_refresh"] == record(box), (
        f"{what}: last_refresh is not the record's content: {found['last_refresh']} against {record(box)}")


def assert_record(box, now, reason, head, status, what, branch=support.BRANCH):
    found = record(box)
    assert found is not None, f"{what}: no record at {record_path(box)}"
    assert set(found) >= {"at", "reason", "head", "status", "branch"}, f"{what}: the record's fields: {found}"
    assert instant(found["at"]) == now, f"{what}: the record's at {found['at']} is not the planted now {now.isoformat()}"
    assert found["reason"] == reason, f"{what}: the record's reason {found['reason']!r}, not {reason!r}"
    assert found["head"] == head, f"{what}: the record's head {found['head']!r}, not the full sha {head}"
    assert found["status"] == status, f"{what}: the record's status {found['status']!r}, not {status!r}"
    assert found["branch"] == branch, f"{what}: the record's branch {found['branch']!r}, not {branch!r}"


def assert_nothing_built(project, box, what):
    assert not os.path.lexists(box.link), f"{what}: a link was made at {box.link}"
    assert support.worktrees(project) == {}, f"{what}: a half was made: {support.worktrees(project)}"
    assert not record_path(box).exists(), f"{what}: a record was written at {record_path(box)}"


def first_refresh(box, env, project, now, reason="after_nightly"):
    """The first scheduled refresh (it builds the store): due and ok; returns the run."""
    run = when_due(project, env, now)
    assert_due(run, reason, "the first scheduled refresh")
    assert run.result["integration"]["status"] == "switched", f"the first refresh built no store\n{run.describe()}"
    return run


# --------------------------------------------------------------------------
# gov status
# --------------------------------------------------------------------------

def status(project, env, now=None):
    return support.gov(project, now_env(env, now) if now is not None else env, "status", "--json")


def integration_store_part(run):
    assert run.returncode == 0 and run.ok, f"gov status did not exit 0 with ok\n{run.describe()}"
    part = run.result.get("integration_store")
    assert isinstance(part, dict), f"gov status has no integration_store part: {sorted(run.result)}\n{run.describe(800)}"
    return part


def is_unread(value):
    return isinstance(value, dict) and value.get("read") is False and bool(value.get("reason"))


def built_at(box):
    """The ready half's own record of when it was built (W2-122's ``stores.json``, ``written_at``)."""
    half = Path(support.assert_link(box))
    path = half / support.RUNTIME_REL / "rebuild" / "stores.json"
    return instant(json.loads(path.read_text(encoding="utf-8"))["written_at"])


def midday_zone(real_now=None):
    """A UTC offset in which the real clock reads about 12:00, so the planted times (within hours of the build) never
    cross a midnight of the wall clock ``GOV_NOW`` states: ``GOV_NOW``'s offset is its wall clock (README)."""
    real_now = real_now or dt.datetime.now(UTC)
    seconds = real_now.hour * 3600 + real_now.minute * 60
    offset = (12 * 3600 - seconds) % 86400
    if offset > 12 * 3600:
        offset -= 86400
    return dt.timezone(dt.timedelta(minutes=offset // 60))


def hhmm(when, zone):
    return when.astimezone(zone).strftime("%H:%M")


def names_instant(text, when, zone):
    """The text names ``when``: as its wall-clock ``HH:MM`` in ``GOV_NOW``'s offset or in UTC (the form is not stated)."""
    return any(hhmm(when, z) in text for z in (zone, UTC))


FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def names_commit(text, commit):
    return commit[:12] in text


# --------------------------------------------------------------------------
# Two stores at one commit, and the link between them (R2-F3)
# --------------------------------------------------------------------------

def built_half(project, box, env, name):
    """A folder of its own at the integration branch's head with its own full store: a second half at one commit."""
    half = support.worktree(project, box.base / "halves" / name)
    run = support.rebuild(half, env)
    assert run.ok, f"the half {name}'s rebuild did not succeed\n{run.describe()}"
    return Path(os.path.realpath(half))


def point(link, half):
    link = Path(link)
    link.parent.mkdir(parents=True, exist_ok=True)
    temporary = link.with_name(link.name + ".tmp")
    if os.path.lexists(temporary):
        temporary.unlink()
    temporary.symlink_to(half)
    os.replace(temporary, link)


PAGED = ("--batch-size", "1")
QUESTION = "ledger"        # a word of all three notes: the first page of one result holds a continuation


def paged_search(project, env, root, *extra):
    return support.gov(project, env, "retrieve", "--json", "--root", str(root), *PAGED, *extra, QUESTION,
                       timeout=support.WAIT_S)


def first_page_token(project, env, root):
    run = paged_search(project, env, root)
    assert run.ok, f"premise: the first page at {root} did not answer\n{run.describe()}"
    token = run.result.get("continuation")
    assert token, f"premise: the first page at {root} carries no continuation (batch size 1)\n{run.describe()}"
    return token


def with_token(project, env, root, token):
    return paged_search(project, env, root, "--continue", token)
