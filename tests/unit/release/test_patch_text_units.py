"""Unit tests of the pure parts of W2-209's slice (a): trailers, push texts, the burned file, rollback.sh, optin."""
from __future__ import annotations

import subprocess
from pathlib import Path

from gov.release import patch, repin


def test_trailers_read_the_last_paragraph_and_skip_the_subject_of_a_one_paragraph_message():
    assert patch.trailers("subject\n\nbody text\n\nClass: F\nTask: T-1\nFix: a thing") == \
        {"Class": ["F"], "Task": ["T-1"], "Fix": ["a thing"]}
    assert patch.trailers("Fix: not a trailer, it is the subject") == {}
    assert patch.trailers("subject\nClass: Q") == {"Class": ["Q"]}
    # prose in the body is not a trailer
    assert patch.trailers("subject\n\nFix: said in prose\n\nthe end") == {}


def test_push_text_names_version_fixes_evidence_and_the_rollback_line():
    text = repin.push_text("0.1.5", 7, "1b2c3d4e" + "0" * 32, "READY")
    assert text == ("Gov OS 0.1.5 released (patch, 7 fixes). Suite green on 1b2c3d4e, proving run READY, pin live. "
                    "Roll back: bash ~/.local/share/gov-os/rollback.sh")
    assert "1 fix)" in repin.push_text("0.1.5", 1, "a" * 40, "READY")


def test_push_text_fits_190_for_the_longest_version_and_eight_fixes():
    assert len(repin.push_text("99.99.99", 8, "f" * 40, "READY")) <= 190


def test_failure_text_is_as_stated_and_cut_to_190_keeping_version_and_burned():
    text = repin.failure_text("0.1.5", "hooks")
    assert text == ("Gov OS 0.1.5 NOT pinned: post-pin check failed (hooks). Rolled back, old gov live, nothing for "
                    "you to do. Release burned; CTO cuts the next patch.")
    long = repin.failure_text("99.99.99", "x" * 400)
    assert len(long) <= 190 and "99.99.99" in long and "burned" in long


def test_burned_lists_versions_in_file_order_and_is_empty_without_the_file(tmp_path):
    assert repin.burned(tmp_path) == []
    folder = tmp_path / ".local/share/gov-os"
    folder.mkdir(parents=True)
    (folder / "burned").write_text("0.1.3\n\n0.1.2\n", encoding="utf-8")
    assert repin.burned(tmp_path) == ["0.1.3", "0.1.2"]


def test_rollback_script_is_plain_shell_that_restores_the_link_and_burns_the_release(tmp_path):
    home = tmp_path / "home"
    old = home / ".local/share/gov-os/pin-aaaaaaaaaaaa"
    (old / "bin").mkdir(parents=True)
    (old / "bin/gov").write_text("#!/bin/sh\necho old\n", encoding="utf-8")
    (old / "bin/gov").chmod(0o755)
    (home / ".local/bin").mkdir(parents=True)
    (home / ".local/bin/gov").symlink_to(home / ".local/share/gov-os/pin-bbbbbbbbbbbb/bin/gov")
    script = repin.rollback_script(old, home, "0.1.5")
    commands = [word for line in script.splitlines() if not line.startswith("#") for word in line.split()]
    assert "gov" not in commands  # plain shell: the new gov is the thing in doubt
    path = tmp_path / "rollback.sh"
    path.write_text(script, encoding="utf-8")
    for _ in range(2):  # twice: the burned file lists the release once
        done = subprocess.run(["bash", str(path)], env={"HOME": str(home), "PATH": "/usr/bin:/bin"},
                              capture_output=True, text=True)
        assert done.returncode == 0, done.stderr
    assert (home / ".local/bin/gov").resolve() == (old / "bin/gov").resolve()
    assert repin.burned(home) == ["0.1.5"]
    assert f"ln -sfn {old}/bin/gov {home}/.local/bin/gov.new && mv -Tf {home}/.local/bin/gov.new " \
           f"{home}/.local/bin/gov; hash -r" in script
