p = "src/gov/adopt/assess.py"
s = open(p).read()

s = s.replace('''this module.
"""

from __future__ import annotations
''', '''this module.

The no-route rule (stated once, here; W2-88 S1): a file has no route when (1) it is over the chunker's limit (more than
``FILE_LIMIT_BYTES`` or a line over ``LINE_LIMIT``: ``no_route: over-limit``), or (2) its suffix is in
``OTHER_CODE_SUFFIXES``, a code language the code graph does not read (``CODE_GRAPH_SUFFIXES`` are the ones it reads):
``no_route: unsupported-language``. A binary has no route of its own (it is listed in ``binary``). A file of any other
suffix (a document, data, a file with no suffix) is no code and has a route through the keyword and meaning indexes.

The secrets scan is judged on what ran: with no ``gitleaks`` on ``PATH``, or blobs over ``SCAN_LIMIT_BYTES``, the
assessment says so (``secrets_scanned``, ``secrets_unscanned``, ``secrets_unscanned_reason``) and the plan never calls
the repository free of secrets (B-1.5).
"""

from __future__ import annotations
''', 1)

s = s.replace('''OTHER_CODE_SUFFIXES = frozenset(".cob .cbl .cobol .f .f90 .for .pas .vb .vba .pl .pm .r .jl .zig .nim .d .ex .exs "
                                ".erl .hs .ml .clj .lisp .elm .dart .groovy .m .mm .asm .s .tcl .vhd .v".split())''',
'''OTHER_CODE_SUFFIXES = frozenset(".cob .cbl .cobol .f .f90 .for .pas .vb .vba .pl .pm .r .jl .zig .nim .d .ex .exs "
                                ".erl .hs .ml .clj .lisp .elm .dart .groovy .m .mm .asm .s .tcl .vhd .v .vue .svelte "
                                ".ps1 .psm1 .proto .graphql .gql .tf .hcl .sol .bat .cmd .coffee .fs .fsx".split())''')

# the reason the scan did not run
s = s.replace('''def _rules(root: Path, head: str) -> tuple[str, ...] | None:
    """The secrets rules as ``gov.secrets`` reads them: the repository's own ``.gitleaks.toml`` at ``head``, else the
    template's (A0 puts it in). None where gitleaks or the rules cannot be had: the assessment says so."""
    from gov.adopt.safety import TEMPLATE_GITLEAKS
    from gov.secrets import CONFIG_REL, _rules as rules_of

    try:
        text = _git(root, "show", f"{head}:{CONFIG_REL}").decode("utf-8")
    except GovError:
        try:
            text = TEMPLATE_GITLEAKS.read_text(encoding="utf-8")
        except OSError:
            return None
    if shutil.which("gitleaks") is None:
        return None
    with tempfile.TemporaryDirectory(prefix="gov-assess-") as where:
        (Path(where) / CONFIG_REL).write_text(text, encoding="utf-8")
        try:
            return rules_of(Path(where))
        except RuntimeError:
            return None
''', '''def _rules(root: Path, head: str) -> tuple[tuple[str, ...] | None, str | None]:
    """``(rules, why not)``: the secrets rules as ``gov.secrets`` reads them (the repository's own ``.gitleaks.toml`` at
    ``head``, else the template's, which A0 puts in). ``(None, reason)`` where gitleaks or the rules cannot be had: the
    assessment says so, and so does the plan."""
    from gov.adopt.safety import TEMPLATE_GITLEAKS
    from gov.secrets import CONFIG_REL, _rules as rules_of

    try:
        text = _git(root, "show", f"{head}:{CONFIG_REL}").decode("utf-8")
    except GovError:
        try:
            text = TEMPLATE_GITLEAKS.read_text(encoding="utf-8")
        except OSError:
            return None, "no secrets rules (.gitleaks.toml) could be read"
    if shutil.which("gitleaks") is None:
        return None, "gitleaks is not on PATH"
    with tempfile.TemporaryDirectory(prefix="gov-assess-") as where:
        (Path(where) / CONFIG_REL).write_text(text, encoding="utf-8")
        try:
            return rules_of(Path(where)), None
        except RuntimeError:
            return None, "the secrets rules could not be read by gitleaks"
''')
s = s.replace("    rules = _rules(root, head)\n", "    rules, no_scan = _rules(root, head)\n")
s = s.replace('''        "secrets_unscanned": sorted(unscanned),
''', '''        "secrets_unscanned": sorted(unscanned),
        "secrets_unscanned_reason": no_scan or (f"{len(unscanned)} blob(s) over {SCAN_LIMIT_BYTES} bytes "
                                                "(SCAN_LIMIT_BYTES) were not scanned" if unscanned else None),
''')
open(p, "w").write(s)
