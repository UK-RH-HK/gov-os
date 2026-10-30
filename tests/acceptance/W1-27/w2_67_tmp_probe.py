"""A one-case module that test_w2_67_temp_folders.py runs in a nested pytest (W2-67, DEC-898).

Its name does not start with ``test_``, so a run of ``tests`` never collects it; the nested run names it.
"""


def test_writes_one_file_in_its_temp_folder(tmp_path):
    (tmp_path / "probe.txt").write_text("W2-67\n", encoding="utf-8")
    assert (tmp_path / "probe.txt").is_file()
