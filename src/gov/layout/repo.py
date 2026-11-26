"""What the check reads of a repository: its items by name, the registries that protect a file, and tracked content
from git's object database. A file registered as a hidden evaluation set or named as a secret is protected: nothing
here, git's own change check included, opens it."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from gov.adopt.assess import _Blobs
from gov.cli.errors import GovError
from gov.layout import CannotRun
from gov.layout.rules import under
from gov.layout.standard import Standard
from gov.util.gitenv import git_env
from gov.util.parts import PATH_MAP_REL, PolicyError, _Part, evaluation_sets, load_yaml_unique

REGISTER_REL = "governance/project/imports.yaml"
_GITLINK, _LINK = "160000", "120000"


def _git(root: Path, *args: str) -> bytes:
    done = subprocess.run(["git", "--no-optional-locks", "-C", str(root), *args], capture_output=True,
                          env=git_env(root))
    if done.returncode != 0:
        raise CannotRun(f"git {args[0]} failed (exit code {done.returncode}): "
                        f"{done.stderr.decode('utf-8', 'replace').strip()[:300]}")
    return done.stdout


def _names(output: bytes) -> list[str]:
    return [os.fsdecode(each) for each in output.split(b"\0") if each]


def _yaml(path: Path, rel: str):
    try:
        return load_yaml_unique(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception as error:  # noqa: BLE001 - whatever the parser raises, the file is not read
        raise CannotRun(f"{rel} cannot be read: {type(error).__name__}") from None


class Repo:
    """``items`` holds each item of the plan by its path: ``file`` (tracked), ``untracked``, ``ignored-root``,
    ``submodule`` or ``declared``. ``plan_rel`` (the plan file, when it lies inside) is no item."""

    def __init__(self, root: Path, std: Standard, plan_rel: str | None) -> None:
        self.root, self.std, self.plan_rel = root, std, plan_rel
        top = _git(root, "rev-parse", "--show-toplevel").decode("utf-8", "replace").rstrip("\n")
        if os.path.realpath(top) != os.path.realpath(root):
            raise CannotRun(f"{root} is not the top of a repository")
        self.commit = _git(root, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
        self._hidden, self._visible = self._registries()
        self.blobs: dict[str, str] = {}  # each tracked file's blob
        self.symlinks: set[str] = set()
        self.items: dict[str, str] = {}
        for entry in _names(_git(root, "ls-files", "-z", "-s")):
            meta, path = entry.split("\t", 1)
            mode, sha, _ = meta.split()
            if mode == _GITLINK:
                self.items[path] = "submodule"
                continue
            self.items[path] = "file"
            self.blobs[path] = sha
            if mode == _LINK:
                self.symlinks.add(path)
        self._clean()
        for path in _names(_git(root, "ls-files", "-z", "--others", "--exclude-standard")):
            self.items.setdefault(path.rstrip("/"), "untracked")
        ignored = ("ls-files", "-z", "--others", "--ignored", "--exclude-standard")
        for path in _names(_git(root, *ignored, "--directory", "--no-empty-directory")):
            self.items.setdefault(path.rstrip("/"), "ignored-root")
        # hidden files below an ignored root, found by their names alone
        self.hidden_ignored = [path for path in _names(_git(root, *ignored)) if self.hidden(path)]
        for path in self._declared():
            if not any(under(item, path) for item in self.items):
                self.items[path] = "declared"
        self.items.pop(plan_rel, None)
        self._folders = {"/".join(parts[:depth]) for parts in (item.split("/") for item in self.items)
                         for depth in range(1, len(parts))}

    def _registries(self) -> tuple[_Part, _Part]:
        """The path map's hidden globs (every evaluation set's and ``sets_root_hidden``'s) and visible globs."""
        try:
            sets = evaluation_sets(str(self.root))
        except PolicyError as error:
            raise CannotRun(str(error)) from None
        hidden, visible = [], []
        for entry in sets.values():
            if not isinstance(entry, dict):
                raise CannotRun(f"{PATH_MAP_REL}: an evaluation set is not a map")
            hidden += entry.get("hidden") or []
            visible += entry.get("visible") or []
        block = (_yaml(self.root / PATH_MAP_REL, PATH_MAP_REL) or {}).get("sets_root_hidden")
        if block is not None:
            if not isinstance(block, dict) or not isinstance(block.get("hidden"), list):
                raise CannotRun(f"{PATH_MAP_REL}: sets_root_hidden holds no list of hidden globs")
            hidden += block["hidden"]
        if not all(isinstance(glob, str) and glob for glob in hidden + visible):
            raise CannotRun(f"{PATH_MAP_REL}: an evaluation set's glob is not a text")
        return _Part(str(self.root), hidden, ""), _Part(str(self.root), visible, "")

    def hidden(self, path: str) -> bool:
        return self._hidden.match(path)

    def visible(self, path: str) -> bool:
        return self._visible.match(path)

    def protected(self, path: str) -> bool:
        return self.hidden(path) or self.std.secret_name(path)

    def _clean(self) -> None:
        """``CannotRun`` on an uncommitted change to a tracked file. A protected file is left out of git's reading of
        the work tree: only whether it is staged or gone is asked."""
        tracked = list(self.items)
        left_out = [path for path in tracked if self.protected(path)]
        if self.plan_rel:
            left_out.append(self.plan_rel)
        changed = _git(self.root, "status", "--porcelain", "-z", "--untracked-files=no", "--", ".",
                       *(f":(exclude,literal){path}" for path in left_out))
        staged = [path for path in _names(_git(self.root, "diff-index", "--cached", "--name-only", "-z", "HEAD"))
                  if path != self.plan_rel]
        gone = [path for path in left_out
                if path != self.plan_rel and self.items.get(path) == "file" and not os.path.lexists(self.root / path)]
        if changed or staged or gone:
            first = (staged or gone or [os.fsdecode(changed.split(b"\0")[0][3:])])[0]
            raise CannotRun(f"a tracked file holds an uncommitted change ({first}): commit or put it back first")

    def _declared(self) -> list[str]:
        path = self.root / REGISTER_REL
        if not os.path.lexists(path):
            return []
        document = _yaml(path, REGISTER_REL)
        if document is None and path.is_file():  # an empty register declares nothing
            return []
        entries = (document.get("imports") or []) if isinstance(document, dict) else None
        if not isinstance(entries, list) or not all(
                isinstance(each, dict) and isinstance(each.get("path"), str) and each["path"] for each in entries):
            raise CannotRun(f"{REGISTER_REL} cannot be read: it holds no list of imports, each with a path")
        top = str(self.root) + "/"
        return [each["path"].removeprefix(top).removeprefix("./").rstrip("/") for each in entries]

    def is_file(self, path: str) -> bool:
        """Whether ``path`` is one file (or a gitlink), not a folder of items."""
        return path not in self._folders and self.items.get(path) in ("file", "untracked", "submodule")

    def exists(self, path: str) -> bool:
        """Whether an item is at ``path`` or below it."""
        return path in self.items or path in self._folders

    def texts(self, paths):
        """``(path, text)`` of each of ``paths`` that is a text: a tracked file's from its blob, an untracked file's
        from the work tree. A protected file, a binary one and a link of an untracked file are given none."""
        reader = _Blobs(self.root)
        try:
            for path in paths:
                if self.protected(path):
                    continue
                if path in self.blobs:
                    data = reader.read(self.blobs[path], 1 << 62)[0]
                elif self.items.get(path) == "untracked" and not os.path.islink(self.root / path):
                    try:
                        data = (self.root / path).read_bytes()
                    except OSError as error:
                        raise CannotRun(f"{path} cannot be read: {type(error).__name__}") from None
                else:
                    continue
                if b"\0" not in data:
                    yield path, data.decode("utf-8", "replace")
        except GovError as error:
            raise CannotRun(error.message) from None
        finally:
            reader.close()

    def secrets(self) -> tuple[list[tuple[str, str]], str | None]:
        """``([(path, rule id)], why nothing was scanned)``: what the repository's secrets filter finds in the tracked
        files that are not protected. The scan switched off by configuration is said, not passed over."""
        from gov import secrets
        from gov.adopt import assess

        try:
            if not secrets.scan_on(self.root):
                return [], secrets.SCAN_OFF
            rules, why = assess._rules(self.root, self.commit)
            if rules is None:
                raise CannotRun(f"the secrets filter cannot run: {why}")
            scan, reader = assess._Scan(rules, self.root), _Blobs(self.root)
            try:
                for path, sha in self.blobs.items():
                    if path != self.plan_rel and not self.protected(path):
                        scan.add(path, reader.read(sha, 1 << 62)[0])
                scan.flush()
            finally:
                scan.close()
                reader.close()
        except GovError as error:
            raise CannotRun(error.message) from None
        return sorted(scan.found), None
