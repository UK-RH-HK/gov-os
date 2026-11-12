"""The memory audit's set record (W2-170; DEC-1101 (1)-(2), DEC-1125 (2)).

The checks of one audit's set before any search (``preflight``), the drop and void rule (``drops``), the declaration
and the use-once marker (``declare``), counts only. Run as ``python3 -m gov.memaudit preflight|void|declare``; every
folder under the sets root is derived from ``--sets-root`` and ``--audit`` (``layout``), and ``say`` is the only
printer. W2-171, W2-172 and W2-88 import these modules and carry no copy.

W2-171 adds ``measure``, ``judge``, ``classes``, ``pool`` and ``pool-import`` (the measured part of one audit); its exit
word ``stopped`` is exit 2, as ``void`` is: the audit began and cannot go on, and the owner decides.
"""

EXIT = {"ok": 0, "refused": 1, "void": 2, "stopped": 2, "used": 3, "usage": 4}
