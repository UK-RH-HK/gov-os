"""Lead's plant for batch 8's red check: once ``w2_67_codegraph`` loads, its ``release`` is switched off (the fault:
the fixtures leave the code-graph daemon folders they make)."""
import importlib.abc
import os
import sys


def _off(since: int = 0):
    marker = os.environ.get("LEAD_PLANT8_MARKER")
    if marker:
        with open(marker, "a", encoding="utf-8") as out:
            out.write("release switched off\n")


class _Finder(importlib.abc.MetaPathFinder):
    busy = False

    def find_spec(self, name, path=None, target=None):
        if name != "w2_67_codegraph" or _Finder.busy:
            return None
        _Finder.busy = True
        try:
            for finder in sys.meta_path:
                if finder is self:
                    continue
                spec = getattr(finder, "find_spec", lambda *a: None)(name, path, target)
                if spec is not None:
                    break
            else:
                return None
        finally:
            _Finder.busy = False
        real = spec.loader.exec_module

        def exec_module(module):
            real(module)
            module.release = _off

        spec.loader.exec_module = exec_module
        return spec


sys.meta_path.insert(0, _Finder())
