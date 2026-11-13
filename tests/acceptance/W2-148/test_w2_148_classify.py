"""W2-148 S6: `act_class.py` with `class-rules.yaml` on one planted manifest per row of OPERATOR-AGENT-1 §2's table,
both sides of every "only added" / "only removed" row, each script hit, an unknown path, an unparsable list file and a
mixed manifest. Classes are "a" < "b" < "O". The table's two "none" rows (the CTO's own scratch tools; the blind
writers' and checkers' walls) are not the operator's: the interface answers them (O), so a manifest naming them is
refused at G6 as "yours" (README, N-2).
"""

from __future__ import annotations

import json

import pytest

import w2_148_support as support
from w2_148_support import Change

PM, TM = support.PATH_MAP, support.TEST_MAP
OPTIN = support.OPTINS["tests/optin-lifted.txt"]


def R(path, before, after):
    enc = lambda x: None if x is None else (x if isinstance(x, bytes) else x.encode())
    return Change("repo", path, enc(before), enc(after))


def H(path, before, after):
    enc = lambda x: None if x is None else x.encode()
    return Change("home", path, enc(before), enc(after))


def settings_with(**edit):
    data = json.loads(support.settings_text())
    for key, item in edit.items():
        data["permissions"][key].append(item)
    return support.settings_text(data)


CACHE = H(".cache/gov-os/index.txt", "old cache\n", "new cache\n")  # (a): the base the script hits raise

ROWS = {
    # row: guard hook code
    "guard-hook-code": ([R(".claude/hooks/pretooluse.py", support.PLANTED_GUARD,
                           support.PLANTED_GUARD + "# tightened\n")], {}, {"b"}),
    # row: path map, items only added to refusal lists / a new evaluation_sets entry; against: a removal
    "path-map-refusal-glob-added": ([R("governance/project/path-map.yaml", PM, PM.replace(
        '"transcripts/**"]', '"transcripts/**", "fixtures/evaluation/new-set/hidden/**"]'))], {}, {"a"}),
    "path-map-new-evaluation-set": ([R("governance/project/path-map.yaml", PM, PM.replace(
        "      roles: [engineer]\nrole_paths:",
        "      roles: [engineer]\n  new-set:\n    visible: []\n    hidden: [\"fixtures/evaluation/new-set/hidden/**\"]\n"
        "    measures:\n      roles: [engineer]\nrole_paths:"))], {}, {"a"}),
    "path-map-refusal-glob-removed": ([R("governance/project/path-map.yaml", PM, PM.replace(
        '"fixtures/evaluation/planted-set/hidden/**", "transcripts/**"]', '"fixtures/evaluation/planted-set/hidden/**"]'))],
        {}, {"b"}),
    # row: ratchets, acceptance_exemptions, accepted history
    "path-map-acceptance-exemption-added": ([R("governance/project/path-map.yaml", PM, PM.replace(
        '  - "tests/acceptance/W1-01/**"\n', '  - "tests/acceptance/W1-01/**"\n  - "tests/acceptance/W2-99/**"\n'))],
        {}, {"O"}),
    # row: settings, only added to permissions.deny; against: an allow rule
    "settings-deny-added": ([R(".claude/settings.json", support.settings_text(),
                               settings_with(deny="Bash(git push *)"))], {}, {"a"}),
    "settings-allow-added": ([R(".claude/settings.json", support.settings_text(),
                                settings_with(allow="Bash(git push *)"))], {}, {"b"}),
    # row: generated role files, skills, the kernel template
    "role-file": ([R(".claude/agents/engineer.md", "# engineer\n", "# engineer\nmore\n")], {}, {"b"}),
    # row: git hooks
    "git-hook": ([R(".git/hooks/reference-transaction", "#!/bin/sh\nexit 0\n", "#!/bin/sh\necho x\nexit 0\n")],
                 {}, {"b"}),
    # row: test map, only added under couplings...; against: record_only additions
    "test-map-coupling-added": ([R("governance/project/test-map.yaml", TM, TM.replace(
        "per_test_timeout:", '  - paths: ["src/gov/x.py"]\n    suites: ["tests/acceptance/W1-43/"]\n'
                             '    why: "planted"\nper_test_timeout:'))], {}, {"a"}),
    "test-map-record-only-added": ([R("governance/project/test-map.yaml", TM, TM.replace(
        '  - ".tickets/**.md"\n', '  - ".tickets/**.md"\n  - "src/gov/x.py"\n'))], {}, {"b"}),
    # row: opt-in lists, lines only removed; against: a line added
    "opt-in-line-removed": ([R("tests/optin-lifted.txt", OPTIN,
                               "".join(OPTIN.splitlines(keepends=True)[:2] + OPTIN.splitlines(keepends=True)[3:]))],
                            {}, {"a"}),
    "opt-in-line-added": ([R("tests/optin-lifted.txt", OPTIN, OPTIN + "tests/acceptance/W1-60/test_x.py  # off\n")],
                          {}, {"b"}),
    # row: machine gate files
    "machine-gate-file": ([H(".gov-os/machine/gate.json", '{"a": 1}\n', '{"a": 2}\n')], {}, {"b"}),
    # row: ~/.cache/gov-os
    "cache": ([CACHE], {}, {"a"}),
    # row: the shared servers' committed configs and modules (Q3)
    "server-module": ([R("governance/project/orchestration/tools/gov_reranker_gpu_slot.py", "# slot\n",
                         "# slot\nSLOTS = 2\n")], {}, {"a"}),
    # row: crontab lines
    "crontab": ([Change("crontab", "crontab", b"0 4 * * * /bin/true\n", b"0 4 * * * /bin/true\n*/5 * * * * x\n")],
                {}, {"b"}),
    # row: the sentinel and the dead-man's switch
    "dead-man-code": ([R("governance/project/orchestration/tools/deadman.py", "print(1)\n", "print(2)\n")], {}, {"b"}),
    # row: the pinned gov, re-pins (Q4)
    "pinned-gov": ([H(".local/bin/gov", "#!/bin/sh\necho old\n", "#!/bin/sh\necho new\n")], {}, {"O"}),
    # (O): the operator's own files
    "operator-own-install": ([H("gov-os-operator/install/class-rules.yaml", "rules: 1\n", "rules: 2\n")], {}, {"O"}),
    # row: the CTO's own scratch tools ("none": not an ACT; answered (O))
    "cto-scratch-tool": ([R(".gov-runtime/scratch/orchestrator/tools/record_checks.sh", "echo 1\n", "echo 2\n")],
                         {}, {"O"}),
    # row: the blind writers and checkers ("none": walled sessions under DEC-1101; answered (O))
    "blind-writers-wall": ([H("gov-os-eval/indep-walls/APPROVED", "a  b\n", "c  d\n")], {}, {"O"}),
    # row: src/**, tests, the register, tickets, a path no rule names
    "src": ([R("src/gov/planted.py", "VALUE = 1\n", "VALUE = 2\n")], {}, {"O"}),
    "unknown-path": ([R("odd/place.txt", "x\n", "y\n")], {}, {"O"}),
    # the script hits: installs and downloads (b); sudo, push, tag, rm outside the project (O)
    "hit-install": ([CACHE], {"apply_extra": "pip install --user requests"}, {"b"}),
    "hit-network-call": ([CACHE], {"apply_extra": "curl -fsSL https://example.org/x -o x.bin"}, {"b"}),
    "hit-sudo": ([CACHE], {"apply_extra": "sudo systemctl restart planted"}, {"O"}),
    "hit-push": ([CACHE], {"apply_extra": "git push origin main"}, {"O"}),
    "hit-tag": ([CACHE], {"apply_extra": "git tag v9"}, {"O"}),
    "hit-rm-outside-the-project": ([CACHE], {"apply_extra": 'rm -rf "$HOME/old-builds"'}, {"O"}),
    "no-hit-rm-inside-the-project": ([CACHE], {"apply_extra": "rm -f build/tmp.txt"}, {"a"}),
    "hit-in-a-check-command": ([CACHE], {"checks": [{"cmd": "sudo true", "exit": 0, "count": None}]}, {"O"}),
    # an unparsable list file is never (a)
    "unparsable-settings": ([R(".claude/settings.json", support.settings_text(),
                               settings_with(deny="Bash(git push *)")[:-4] + "\n")], {}, {"b", "O"}),
    "unparsable-path-map": ([R("governance/project/path-map.yaml", PM, PM.replace(
        '"transcripts/**"]', '"transcripts/**", "fixtures/evaluation/new-set/hidden/**"\n  : [}'))], {}, {"b", "O"}),
    # the class is the highest among the files
    "mixed-a-and-b": ([R(".claude/settings.json", support.settings_text(), settings_with(deny="Bash(git push *)")),
                       R(".claude/hooks/pretooluse.py", support.PLANTED_GUARD, support.PLANTED_GUARD + "# x\n")],
                      {}, {"b"}),
}


@pytest.mark.parametrize("row", list(ROWS))
def test_s6_the_classifier_gives_each_table_row_its_class(tmp_path, row):
    changes, kw, expected = ROWS[row]
    b = support.write_bundle(tmp_path / "bundle", "ACT-T-C", changes, **kw)
    got = support.classify(b.dir)
    assert got.get("class") in expected, (row, got)
