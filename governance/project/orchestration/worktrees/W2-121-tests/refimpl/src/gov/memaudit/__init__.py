"""The memory audit's set record (W2-170; DEC-1101 (1)-(2), DEC-1125 (2)).

The checks of one audit's set before any search (``preflight``), the drop and void rule (``drops``), the declaration
and the use-once marker (``declare``), counts only. Run as ``python3 -m gov.memaudit preflight|void|declare``; every
folder under the sets root is derived from ``--sets-root`` and ``--audit`` (``layout``), and ``say`` is the only
printer. W2-171, W2-172 and W2-88 import these modules and carry no copy.
"""

EXIT = {"ok": 0, "refused": 1, "void": 2, "used": 3, "usage": 4}
