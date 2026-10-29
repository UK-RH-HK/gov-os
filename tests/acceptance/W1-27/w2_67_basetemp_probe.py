"""The probe of W2-67's ``--basetemp`` cases (``test_w2_67_basetemp_refusal.py``).

Its name does not start with ``test_``, so a run of ``tests`` never collects it: only the nested runs of those
cases name it on their command line. Its one case records the temp folder pytest gave it, one line in the file the
environment variable ``W2_67_BASETEMP_PROBE_RECORD`` names, so the case that started the run can see whether a test
ran and where its temp folder was made.
"""

from __future__ import annotations

import os

RECORD_VARIABLE = "W2_67_BASETEMP_PROBE_RECORD"


def test_the_probe_records_its_temp_folder(tmp_path):
    assert tmp_path.is_dir()
    record = os.environ.get(RECORD_VARIABLE)
    if record:
        with open(record, "a", encoding="utf-8") as handle:
            handle.write(f"{tmp_path}\n")
