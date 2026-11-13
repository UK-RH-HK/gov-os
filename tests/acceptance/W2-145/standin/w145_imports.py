"""The W2-145 tests' import recorder, installed by a ``.pth`` in the planted reranker environment.

Every process of that environment's interpreter (``-I`` or not: ``site`` still reads its ``.pth`` files) records each
attempt to import one of the model's libraries (``torch``, ``sentence_transformers``, ``transformers``), found or not,
as one line ``pid<TAB>ppid<TAB>module<TAB>argv`` in ``imports.log`` in the test's state folder (named in
``w145_imports.json`` beside this file). Nothing is imported or changed for the process itself.
"""

import json
import os
import sys

WATCHED = ("torch", "sentence_transformers", "transformers")


def _log_path():
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, "w145_imports.json"), encoding="utf-8") as handle:
            return os.path.join(json.load(handle)["state"], "imports.log")
    except (OSError, ValueError, KeyError):
        return None


class _Recorder:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in WATCHED and "." not in fullname:
            where = _log_path()
            if where:
                try:
                    with open(where, "a", encoding="utf-8") as out:
                        out.write(f"{os.getpid()}\t{os.getppid()}\t{fullname}\t{' '.join(sys.argv)}\n")
                except OSError:
                    pass
        return None  # the import goes on as it would


def install():
    if not any(isinstance(finder, _Recorder) for finder in sys.meta_path):
        sys.meta_path.insert(0, _Recorder())
