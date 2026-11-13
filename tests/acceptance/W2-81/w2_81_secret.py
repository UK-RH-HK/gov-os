"""The planted secret: built at run time from parts, held in memory, never printed (DEC-911, CAP-03.a, CAP-03.d).

No tracked file of this repository holds a secret whole: each form below is a
prefix written in two pieces and a body drawn from the seed, so neither this
file nor any other of the suite matches a rule of the secrets scanner. The
value lives only in a :class:`Held` object; its ``repr`` and ``str`` withhold
it, so an assertion message, a log or a report that shows the object shows no
value. Comparisons are made in memory (``found_in``), never by printing.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from w2_81_git import git_env, require, short

_UPPER32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
_ALNUM = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# Each form: the scanner's default rule that detects it, the prefix in two pieces, the body's alphabet and length.
FORMS = {
    "cloud-access-key": {"rule": "aws-access-token", "prefix": ("AK", "IA"), "alphabet": _UPPER32, "length": 16},
    "forge-token": {"rule": "github-pat", "prefix": ("gh", "p_"), "alphabet": _ALNUM, "length": 36},
}


def _draw(alphabet, length, salt):
    out = []
    counter = 0
    while len(out) < length:
        for byte in hashlib.sha256(f"{salt}:{counter}".encode()).digest():
            out.append(alphabet[byte % len(alphabet)])
        counter += 1
    return "".join(out[:length])


class Held:
    """A secret value held in memory. It never prints: ``repr`` and ``str`` withhold it."""

    __slots__ = ("_value", "form")

    def __init__(self, value, form):
        self._value = value
        self.form = form

    def __repr__(self):
        return f"<{self.form} secret withheld>"

    __str__ = __repr__

    def found_in(self, text):
        """Whether the value appears whole in ``text`` (str or bytes)."""
        if text is None:
            return False
        if isinstance(text, bytes):
            return self._value.encode() in text
        return self._value in text

    def line(self, template):
        """The template with the value in place of ``{value}``: what the builder writes in the built repository."""
        return template.replace("{value}", self._value)

    def __eq__(self, other):
        return isinstance(other, Held) and other._value == self._value

    def __hash__(self):
        return hash(("held", self.form))


def make_secret(form, seed, salt):
    """A value in the form the scanner's rule detects, drawn from the seed (so one seed builds one tree)."""
    spec = FORMS[form]
    return Held("".join(spec["prefix"]) + _draw(spec["alphabet"], spec["length"], f"w2-81:{seed}:{salt}"), form)


def assert_absent(held, text, where):
    """Fail naming ``where`` (a path, a commit, an output's name) when the value is in ``text``; never the value."""
    if held.found_in(text):
        raise AssertionError(f"the planted {held.form} secret's value appears whole in {where}")


@dataclass
class Finding:
    rule: str
    path: str
    commit: str  # 12 digits


def scan_history(root, scratch=None):
    """``gitleaks git`` on a built repository's history, redacted; returns findings (rule, path, 12-digit commit).

    The report is written to a temporary file outside the repository and read back; its ``Secret`` and ``Match``
    fields are redacted by the scanner and never kept. Returns ``(findings, outputs)``, ``outputs`` being the raw
    texts (stdout, stderr, report) so a case can check the value is in none of them.
    """
    require("gitleaks")
    with tempfile.TemporaryDirectory(dir=scratch) as folder:
        report = Path(folder) / "report.json"
        done = subprocess.run(["gitleaks", "git", str(root), "--redact", "--no-banner", "--report-format", "json",
                               "--report-path", str(report)], capture_output=True, text=True,
                              env=git_env(Path(folder)))
        if done.returncode not in (0, 1) or not report.is_file():
            raise AssertionError(f"gitleaks failed on {root} (exit {done.returncode})")
        raw = report.read_text(encoding="utf-8")
    findings = [Finding(item["RuleID"], item["File"], short(item["Commit"])) for item in json.loads(raw or "[]")]
    return findings, {"gitleaks stdout": done.stdout, "gitleaks stderr": done.stderr, "gitleaks report": raw}
