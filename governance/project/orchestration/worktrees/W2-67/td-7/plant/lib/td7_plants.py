"""W2-67 batch 7's planted faults in the secrets check (throwaway; never committed).

Each plant folder holds a ``usercustomize.py`` that calls ``install(<name>, <folder>)``; the folder is put first
on PYTHONPATH for a pytest run, so every process of that run imports it. Once ``gov.secrets`` has been imported
(after the test's own declared short limit, if any, has set its figures), the plant replaces one behaviour of
the module and logs, to ``<folder>/ran.jsonl``, each time the planted behaviour acts. The tracked tree is untouched.
"""
import hashlib
import importlib.abc
import json
import os
import subprocess as _real_subprocess
import sys
import types

_STATE = {}


def _log(entry):
    entry = {"pid": os.getpid(), "plant": _STATE["name"], **entry}
    fd = os.open(os.path.join(_STATE["folder"], "ran.jsonl"), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(fd, (json.dumps(entry) + "\n").encode())
    finally:
        os.close(fd)


def _proxy_subprocess(run):
    proxy = types.ModuleType("subprocess")
    for name in dir(_real_subprocess):
        if not name.startswith("__"):
            setattr(proxy, name, getattr(_real_subprocess, name))
    proxy.run = run
    return proxy


# --------------------------------------------------------------------------
# The faults
# --------------------------------------------------------------------------

def fixed_limit(module):
    """The limit no longer grows with the content's size: every gitleaks run gets the base alone."""
    def run(*args, **kwargs):
        if "timeout" in kwargs:
            was = kwargs["timeout"]
            kwargs["timeout"] = module._TIMEOUT_S
            _log({"acted": "timeout", "was": round(was, 3), "now": kwargs["timeout"],
                  "bytes": len(kwargs.get("input") or b"")})
        return _real_subprocess.run(*args, **kwargs)
    module.subprocess = _proxy_subprocess(run)


def first_half_pieces(module):
    """A large store's later pieces are never scanned: of each text, only the first half of its pieces is given."""
    pieces = module._pieces

    def first_half(chunk):
        every = list(pieces(chunk))
        kept = every[:max(1, len(every) // 2)]
        if len(kept) < len(every):
            _log({"acted": "pieces", "given": len(kept), "of": len(every), "bytes": len(chunk)})
        return iter(kept)
    module._pieces = first_half


def halves_at_middle(module):
    """A large text is cut at its middle byte into two texts of their own, with no overlap across the cut."""
    scan = module._scan

    def halved(rules, chunks):
        out = []
        for chunk in chunks:
            if len(chunk) > 2 * module._PIECE:
                half = len(chunk) // 2
                out += [chunk[:half], chunk[half:]]
                _log({"acted": "halves", "bytes": len(chunk), "cut": half})
            else:
                out.append(chunk)
        return scan(rules, out)
    module._scan = halved


def hang_green(module):
    """A gitleaks run that does not end within its limit is taken as a clean scan."""
    def run(*args, **kwargs):
        try:
            return _real_subprocess.run(*args, **kwargs)
        except _real_subprocess.TimeoutExpired as expired:
            _log({"acted": "timeout-taken-as-clean", "timeout": round(expired.timeout, 3)})
            return _real_subprocess.CompletedProcess(expired.cmd, 0, b"", b"")
    module.subprocess = _proxy_subprocess(run)


def hang_records_clean(module):
    """The check still fails on a hang, but first records every store it was judging as clean."""
    stores = module.stores_with_secrets

    def recording(root):
        try:
            return stores(root)
        except BaseException as error:
            from pathlib import Path
            root = Path(root)
            digests = set()
            for folder, _, names in os.walk(root / module.RUNTIME_REL):
                for name in names:
                    try:
                        content = module._store(Path(folder) / name)[0]
                    except Exception:
                        continue
                    digests.add(hashlib.sha256(content).hexdigest())
            scanner = module._scanner(module._rules(root))
            if scanner is not None:
                module._record(root, scanner, digests)
            _log({"acted": "recorded-clean-on-failure", "stores": len(digests), "error": type(error).__name__})
            raise
    module.stores_with_secrets = recording


FAULTS = {"fixed-limit": fixed_limit, "first-half-pieces": first_half_pieces, "halves-at-middle": halves_at_middle,
          "hang-green": hang_green, "hang-records-clean": hang_records_clean}


# --------------------------------------------------------------------------
# Installing a fault once gov.secrets is imported
# --------------------------------------------------------------------------

class _Loader(importlib.abc.Loader):
    def __init__(self, inner):
        self.inner = inner

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def create_module(self, spec):
        return self.inner.create_module(spec)

    def exec_module(self, module):
        self.inner.exec_module(module)
        FAULTS[_STATE["name"]](module)
        _log({"installed": True, "figures": {name: getattr(module, name, None)
                                             for name in ("_TIMEOUT_S", "_FLOOR", "_LARGE")}})


class _Finder(importlib.abc.MetaPathFinder):
    busy = False

    def find_spec(self, name, path, target=None):
        if name != "gov.secrets" or self.busy:
            return None
        self.busy = True
        try:
            for finder in [each for each in sys.meta_path if each is not self]:
                spec = getattr(finder, "find_spec", lambda *a: None)(name, path, target)
                if spec is not None:
                    spec.loader = _Loader(spec.loader)
                    return spec
        finally:
            self.busy = False
        return None


def install(name, folder):
    assert name in FAULTS, name
    _STATE.update(name=name, folder=folder)
    sys.meta_path.insert(0, _Finder())
