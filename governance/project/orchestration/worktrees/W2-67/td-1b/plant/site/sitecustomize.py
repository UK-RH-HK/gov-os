"""W2-67 batch 1b: apply the planted faults of ``W2_67_PLANT`` in a ``python3 -m gov.rebuild.check`` process
(the plugin puts this folder first on that one process's PYTHONPATH). Throwaway; never in the tracked tree."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import w2_67b_child  # noqa: E402

w2_67b_child.apply([name for name in os.environ.get("W2_67_PLANT", "").split(",") if name])
