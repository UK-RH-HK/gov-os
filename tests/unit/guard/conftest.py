"""Session-wide tripwire: fail if any test writes to the real mirror folder (DEC-429)."""

from __future__ import annotations

import os
import pwd


def _real_home():
    return pwd.getpwuid(os.getuid()).pw_dir


def _mirror_folder():
    return os.path.join(_real_home(), ".local", "state", "gov-os")


def _snapshot(folder):
    if not os.path.isdir(folder):
        return None
    return sorted(os.listdir(folder)), os.stat(folder).st_mtime


def _real_mirror_folder_unchanged(request):
    folder = _mirror_folder()
    before = _snapshot(folder)
    yield
    after = _snapshot(folder)
    if before is None and after is None:
        return
    if before is None and after is not None:
        import pytest
        pytest.fail(
            f"The real mirror folder {folder} was created during the test session "
            f"(entries: {after[0]}). A unit test wrote to the real HOME.",
            pytrace=False,
        )
    if before is not None and after is None:
        import pytest
        pytest.fail(
            f"The real mirror folder {folder} was removed during the test session. "
            f"A unit test modified the real HOME.",
            pytrace=False,
        )
    before_listing, before_mtime = before
    after_listing, after_mtime = after
    added = sorted(set(after_listing) - set(before_listing))
    removed = sorted(set(before_listing) - set(after_listing))
    mtime_changed = before_mtime != after_mtime
    if added or removed or mtime_changed:
        parts = []
        if added:
            parts.append(f"added: {added}")
        if removed:
            parts.append(f"removed: {removed}")
        if mtime_changed:
            parts.append(f"mtime changed: {before_mtime} -> {after_mtime}")
        import pytest
        pytest.fail(
            f"The real mirror folder {folder} changed during the test session "
            f"({'; '.join(parts)}). A unit test wrote to the real HOME.",
            pytrace=False,
        )


def pytest_configure(config):
    import pytest

    class TripwirePlugin:
        @pytest.fixture(scope="session", autouse=True)
        def _real_mirror_folder_unchanged(self, request):
            yield from _real_mirror_folder_unchanged(request)

    config.pluginmanager.register(TripwirePlugin(), "guard_real_mirror_tripwire")
