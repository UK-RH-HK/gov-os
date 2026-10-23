"""W2-67 batch 2 (throwaway): run a declared check's module as ``python3 -m`` would, with one exact text change
of its source made in memory (``w2_67c_child.CHILD_TEXT[<fault>]``). The module file is never written."""

import importlib.util
import sys
from pathlib import Path

import w2_67c_child

module, old, new = w2_67c_child.CHILD_TEXT[sys.argv[1]]
spec = importlib.util.find_spec(module)
source = Path(spec.origin).read_text(encoding="utf-8")
if source.count(old) != 1:
    sys.exit(f"W2-67 plant {sys.argv[1]}: {old!r} is not once in {spec.origin}")
sys.argv = [spec.origin]
namespace = {"__name__": "__main__", "__file__": spec.origin, "__package__": module.rpartition(".")[0],
             "__builtins__": __builtins__}
exec(compile(source.replace(old, new), spec.origin, "exec"), namespace)
