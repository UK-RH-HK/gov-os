"""W2-69 (K2): a fragment of a longer identifier is never flagged, wherever a read begins or ends.

Success: "An embedded fragment of a longer identifier is not flagged: a
token-shaped string inside a word, placed at every offset relative to wherever
the check or gitleaks begins a read, is not a finding, for every rule with a
leading word boundary [DEC-897 item 1, W2-M404]."

Failure: "A word-internal fragment flagged at a read edge (the chance red of
W2-62's queue, 2026-10-22). A read edge is where a read begins or where it ends."

Three groups of cases:

- **The project's four rules, every offset.** For each rule, a word-internal
  string (word characters, then a string that is a token by the rule when it stands
  alone) fills the content in cells of 24 bytes. In 24 files the cells are shifted
  by 0 to 23 bytes, so every byte offset of the content is where such a string
  begins in one of them: wherever the check or gitleaks begins a read, one file has
  a token-shaped string inside a word there. No file may be named. Forms: plain
  files (one line, lines, blank lines, words of 12,288 bytes, UTF-16), a long SQLite
  value, many small values, a full-text index, a blob, a UTF-16 blob, a UTF-16
  store, and deleted rows in freed space.
- **gitleaks' default rules with a leading word boundary, at the read edges.** A
  string built from each rule's own expression, at a known place (where gitleaks
  begins a read of a pipe or a file, and where the learning run shows the check
  splits), on both sides: the string's start where a read begins (inside its word),
  and its end where a read ends (its word going on after it). Fewer offsets than
  for the project's rules: the read edges do not depend on the rule (the project's
  rules show every offset), and a full sweep of 65 rules would be some 13,000 files
  (DEC-221).
- **The two named shapes:** the identifier of W2-62's stop (84 characters, the
  token-shaped part 62 bytes from the 23rd), and W2-M395's byte join (two values
  whose bytes join into a token-shaped string no value holds).

Every string is checked first by the real gitleaks (the premises): the
token-shaped part alone is a finding by its rule, and the string inside its word is
no finding by any rule. Strings are built at run time; none stands whole here.
"""

from __future__ import annotations

import pytest

import w2_69_support as support

pytestmark = [support.needs_gitleaks, support.local_only]

R = support.RUNTIME
Q = 24                      # the cell of the project rules' sweeps; every string is shorter
VALUE_CELLS = 5             # many-values form: cells per value
FREED_SIZE = 64 * 1024
DEFAULT_SIZE = 256 * 1024
DEFAULT_CAP = 12

# gitleaks 8.30.1's default rules whose expression begins with a word boundary (after its flags and opening groups).
DEFAULT_RULES = (
    "1password-secret-key", "adobe-client-secret", "airtable-personnal-access-token", "alibaba-access-key-id",
    "anthropic-admin-api-key", "anthropic-api-key", "artifactory-api-key", "artifactory-reference-token",
    "authress-service-client-access-key", "aws-access-token", "aws-amazon-bedrock-api-key-long-lived",
    "clickhouse-cloud-api-secret-key", "cloudflare-origin-ca-key", "curl-auth-header", "curl-auth-user",
    "databricks-api-token", "digitalocean-access-token", "digitalocean-pat", "digitalocean-refresh-token",
    "easypost-api-token", "easypost-test-api-token", "facebook-access-token", "facebook-page-access-token",
    "flyio-access-token", "gcp-api-key", "gitlab-pat-routable", "gitlab-runner-authentication-token-routable",
    "grafana-api-key", "grafana-cloud-api-token", "grafana-service-account-token", "heroku-api-key-v2",
    "huggingface-access-token", "huggingface-organization-api-token", "infracost-api-token",
    "intra42-client-secret", "jwt", "jwt-base64", "kubernetes-secret-yaml", "maxmind-license-key",
    "notion-api-token", "npm-access-token", "octopus-deploy-api-key", "openai-api-key", "openshift-user-token",
    "perplexity-api-key", "planetscale-api-token", "planetscale-oauth-token", "planetscale-password",
    "postman-api-token", "prefect-api-token", "pulumi-api-token", "readme-api-token", "rubygems-api-token",
    "scalingo-api-token", "sendgrid-api-token", "sendinblue-api-token", "sentry-org-token", "sentry-user-token",
    "settlemint-application-access-token", "settlemint-personal-access-token", "settlemint-service-access-token",
    "shippo-api-token", "sidekiq-sensitive-url", "sourcegraph-access-token", "square-access-token",
    "stripe-access-token", "vault-batch-token", "vault-service-token",
)
# The rules for which no word-internal string can exist, and why (README, "Rules without a case").
NO_CASE = {
    "gitlab-pat-routable": "still found",
    "gitlab-runner-authentication-token-routable": "still found",
    "kubernetes-secret-yaml": "applies only to paths",
}
PROJECT_RULES = ("gov-canary", "gov-token-digit", "gov-token-lower", "gov-token-upper")


# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------

def cells(layout, word, phase, size, q=Q):
    """``size`` bytes: ``phase`` bytes of padding, then ``word`` in cells of ``q`` bytes, laid out as ``layout``."""
    pad = "_" if layout == "longword" else " "
    out, total, count = [pad * phase], phase, 0
    while total + q <= size:
        if layout == "oneline":
            cell = word.ljust(q)
        elif layout == "lines":
            cell = word.ljust(q - 1) + "\n"
        elif layout == "blank":
            cell = word.ljust(q - 2) + ("\n\n" if count % 8 == 7 else " \n")
        elif layout == "longword":
            cell = word.ljust(q, "_") if count % 512 != 511 else word.ljust(q - 1, "_") + " "
        else:
            raise ValueError(layout)
        out.append(cell)
        total += q
        count += 1
    out.append(pad * (size - total))
    return "".join(out)


def _plain(project, rel, layout, word, phase, q=Q):
    support.write(project / f"{rel}.txt", cells(layout, word, phase, support.SWEEP_SIZE, q))
    return f"{rel}.txt"


def _utf16(project, rel, layout, word, phase, q=Q):
    support.write(project / f"{rel}.txt", cells(layout, word, phase, support.SWEEP_SIZE, q).encode("utf-16-le"))
    return f"{rel}.txt"


def _long_value(project, rel, layout, word, phase, q=Q):
    support.long_value_store(project / f"{rel}.db", cells(layout, word, phase, support.SWEEP_SIZE, q))
    return f"{rel}.db"


def _many_values(project, rel, layout, word, phase, q=Q):
    value = " " * phase + (word.ljust(q - 1) + "\n") * VALUE_CELLS
    support.values_store(project / f"{rel}.db", [value] * (support.SWEEP_SIZE // len(value)))
    return f"{rel}.db"


def _fts(project, rel, layout, word, phase, q=Q):
    support.fts_store(project / f"{rel}.db", cells(layout, word, phase, support.SWEEP_SIZE, q))
    return f"{rel}.db"


def _blob(project, rel, layout, word, phase, q=Q):
    support.blob_store(project / f"{rel}.db", cells(layout, word, phase, support.SWEEP_SIZE, q).encode())
    return f"{rel}.db"


def _utf16_blob(project, rel, layout, word, phase, q=Q):
    support.blob_store(project / f"{rel}.db", cells(layout, word, phase, support.SWEEP_SIZE, q).encode("utf-16-le"))
    return f"{rel}.db"


def _utf16_store(project, rel, layout, word, phase, q=Q):
    support.long_value_store(project / f"{rel}.db", cells(layout, word, phase, support.SWEEP_SIZE, q),
                             encoding="UTF-16le")
    return f"{rel}.db"


def _freed_rows(project, rel, layout, word, phase, q=Q):
    """Rows of word-internal strings, every second one deleted (secure_delete off): freed cells between live ones."""
    value = " " * phase + (word.ljust(q - 1) + "\n") * VALUE_CELLS
    count = FREED_SIZE // len(value)
    support.sqlite_store(project / f"{rel}.db", ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)"],
                         [("INSERT INTO notes (body) VALUES (?)", (value,)) for _ in range(count)],
                         secure_delete=False, after=["DELETE FROM notes WHERE id % 2 = 0"])
    return f"{rel}.db"


FORMS = {
    "plain-oneline": ("oneline", _plain),
    "plain-lines": ("lines", _plain),
    "plain-blank-lines": ("blank", _plain),
    "plain-longword": ("longword", _plain),
    "plain-utf16le": ("lines", _utf16),
    "sqlite-long-value": ("lines", _long_value),
    "sqlite-many-values": ("lines", _many_values),
    "sqlite-full-text-index": ("lines", _fts),
    "sqlite-blob": ("lines", _blob),
    "sqlite-utf16le-blob": ("lines", _utf16_blob),
    "sqlite-utf16-store": ("lines", _utf16_store),
    "sqlite-freed-rows": ("lines", _freed_rows),
}


def _assert_none_named(run, rels, what):
    assert run.returncode is not None, f"{what}: the check did not end within its declared limit\n{run.describe()}"
    named = run.named(rels)
    assert not named, (
        f"{what}: the check flagged {len(named)} of {len(rels)} files that hold token-shaped strings only inside "
        f"words: {named[:12]}\n{run.describe(800)}")
    assert run.returncode == 0, f"{what}: the check is not green and names no file\n{run.describe()}"


# --------------------------------------------------------------------------
# Premises: each string is a token alone and none inside its word (judged by gitleaks)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("rule", PROJECT_RULES)
def test_premise_a_project_rules_string_is_a_token_alone_and_none_inside_its_word(rule):
    prefix, token = support.project_k2_strings()[rule]
    for name, config in support.rule_sets().items():
        assert rule in support.gitleaks_finds(f" {token} \n", config), (
            f"premise: the string of {rule} alone is no finding by the rule set {name}")
        assert support.gitleaks_finds(f" {prefix}{token} \n", config) == [], (
            f"premise: the string of {rule} inside its word is a finding by the rule set {name}")
        word = cells("lines", prefix + token, 5, 600)
        assert support.gitleaks_finds(word, config) == [], (
            f"premise: the cells of {rule}'s string are a finding by the rule set {name}")


def test_the_default_rules_with_a_leading_boundary_are_the_ones_covered():
    found = set(support.default_boundary_rules())
    assert found == set(DEFAULT_RULES), (
        f"gitleaks' default rules with a leading word boundary are not the ones this suite covers: "
        f"new {sorted(found - set(DEFAULT_RULES))}, gone {sorted(set(DEFAULT_RULES) - found)}")
    project = {rule["id"] for rule in support.tomllib.loads(support.template_text())["rules"]
               if support.leads_with_boundary(rule["regex"])}
    assert project == set(PROJECT_RULES), f"the project's rules with a leading boundary are {sorted(project)}"


@pytest.mark.parametrize("rule", DEFAULT_RULES)
def test_premise_a_default_rules_string_is_a_token_alone_and_none_inside_its_word(rule):
    built = support.rule_string(rule)
    if rule in NO_CASE:
        assert built.why_not and NO_CASE[rule] in built.why_not, (
            f"{rule} was named as a rule for which no word-internal string exists ({NO_CASE[rule]}), "
            f"but one was built: the README and this suite must cover it")
        return
    assert not built.why_not, f"no word-internal string of {rule} could be built: {built.why_not}"
    config = support.template_text()
    assert rule in support.gitleaks_finds(f" {built.token}{built.tail} \n", config), f"premise: {rule} alone"
    assert support.gitleaks_finds(f" {built.prefix}{built.token}{built.tail} \n", config) == [], (
        f"premise: {rule}'s string inside its word")
    if built.suffix:
        assert support.gitleaks_finds(f" {built.token}{built.suffix}{built.tail} \n", config) == [], (
            f"premise: {rule}'s string with its word going on after it")


# --------------------------------------------------------------------------
# The project's four rules: every offset, every form
# --------------------------------------------------------------------------

@pytest.mark.parametrize("rule", PROJECT_RULES)
@pytest.mark.parametrize("form", sorted(FORMS))
def test_a_word_internal_string_of_a_project_rule_is_no_finding_at_any_offset(sandbox, project, slots, form, rule):
    layout, build = FORMS[form]
    prefix, token = support.project_k2_strings()[rule]
    word = prefix + token
    assert len(word) < Q - 2
    rels = [build(project, f"{R}/inside/{rule}-phase-{phase:02d}", layout, word, phase) for phase in range(Q)]
    with support.slot(slots):
        run = support.run_check(sandbox, project)
    assert token not in run.stdout + run.stderr, "the check printed a token-shaped string"
    _assert_none_named(run, rels, f"{form}, {rule}, every offset")


# --------------------------------------------------------------------------
# W2-62's stop: an 84-character identifier, the token-shaped part 62 bytes long from its 23rd character
# --------------------------------------------------------------------------

INCIDENT_Q = 88


def incident_identifier():
    head = "codegraph_" + "node_" + "ident_" + "_"             # 22 lower-case letters and underscores
    token = "tok" + "_" + "a" + "B" + support.chars("w2-62-stop", 56)   # 62 bytes, gov-token-lower's shape
    assert len(head) == 22 and len(head + token) == 84
    return head, token


def test_premise_the_w2_62_identifier_is_no_finding_whole_and_a_finding_cut():
    head, token = incident_identifier()
    for name, config in support.rule_sets().items():
        assert support.gitleaks_finds(f" {head}{token} \n", config) == [], f"premise: the whole identifier ({name})"
        assert "gov-token-lower" in support.gitleaks_finds(f"{token} \n", config), (
            f"premise: the identifier cut at its 23rd character is a gov-token-lower finding ({name})")


@pytest.mark.parametrize("form", ("plain-lines", "plain-oneline", "sqlite-long-value", "sqlite-many-values"))
def test_the_identifier_of_the_w2_62_stop_is_no_finding_at_any_offset(sandbox, project, slots, form):
    head, token = incident_identifier()
    layout, build = FORMS[form]
    rels = [build(project, f"{R}/w2-62/phase-{phase:02d}", layout, head + token, phase, INCIDENT_Q)
            for phase in range(INCIDENT_Q)]
    with support.slot(slots):
        run = support.run_check(sandbox, project)
    assert token not in run.stdout + run.stderr, "the check printed a token-shaped string"
    _assert_none_named(run, rels, f"{form}, the W2-62 identifier at every offset")


# --------------------------------------------------------------------------
# gitleaks' default rules: the start of a read and the end of a read
# --------------------------------------------------------------------------

def _default_writer(form):
    if form == "plain-lines":
        return ".txt", lambda path, data: support.write(path, bytes(data))
    return ".db", lambda path, data: support.long_value_store(path, bytes(data).decode("ascii"))


@pytest.mark.parametrize("side", ("a-read-begins-inside-the-word", "a-read-ends-inside-the-word"))
@pytest.mark.parametrize("form", ("plain-lines", "sqlite-long-value"))
def test_a_word_internal_string_of_every_default_rule_is_no_finding_at_a_read_edge(sandbox, project, stand_in, slots,
                                                                                    form, side):
    ext, writer = _default_writer(form)
    content = support.tagged("lines", DEFAULT_SIZE)
    clean = f"{R}/edges/clean{ext}"
    edges = support.learn(sandbox, project, stand_in, clean, lambda path: writer(path, content), content)
    places = edges.chosen(400, len(content) - 900, DEFAULT_CAP)
    assert places, f"the learning run showed no place where a read begins inside {form}"
    rels, strings, empty = [], [], []
    for rule in DEFAULT_RULES:
        if rule in NO_CASE:
            continue
        built = support.rule_string(rule)
        if side == "a-read-ends-inside-the-word" and not built.suffix:
            empty.append(rule)
            continue
        data, taken = bytearray(content), []
        for edge in places:
            if side == "a-read-begins-inside-the-word":     # the token-shaped part begins where the read begins
                text, at = (built.prefix + built.token + built.tail).encode(), edge - len(built.prefix)
            else:                                           # the token-shaped part ends where the read ends
                text, at = (built.token + built.suffix + built.tail).encode(), edge - len(built.token)
            start, end = at - 1, at + len(text) + 1
            if any(start < b and a < end for a, b in taken):
                continue
            placed = support.place(data, at, text)
            if placed is not None:
                data, taken = placed, taken + [(start, end)]
        if not taken:
            continue
        rel = f"{R}/edges/{rule}{ext}"
        writer(project / rel, data)
        rels.append(rel)
        strings.append(built.token)
    assert len(rels) >= 40, f"too few default rules placed: {len(rels)}"
    with support.slot(slots):
        run = support.run_check(sandbox, project)
    assert not any(token in run.stdout + run.stderr for token in strings), "the check printed a token-shaped string"
    _assert_none_named(run, rels, f"{form}, the default rules, {side} (rules without such a case: {empty})")


# --------------------------------------------------------------------------
# W2-M395: bytes of different values never join into a finding
# --------------------------------------------------------------------------

JOINS = ("two-adjacent-text-values", "a-text-an-integer-and-a-text")


def _join_store(path, how):
    body = "7" + support.chars("w2-m395", 15)
    if how == "two-adjacent-text-values":
        schema = ["CREATE TABLE pairs (id INTEGER PRIMARY KEY, a TEXT, b TEXT)"]
        rows = [("INSERT INTO pairs (a, b) VALUES (?, ?)", (support.prose(200, "j1") + " sk", "_" + body + " here"))]
    else:   # the integer 95 is stored as the one byte 0x5F, "_", between the two texts
        schema = ["CREATE TABLE trio (id INTEGER PRIMARY KEY, a TEXT, n INTEGER, b TEXT)"]
        rows = [("INSERT INTO trio (a, n, b) VALUES (?, ?, ?)", (support.prose(200, "j2") + " sk", 95, body + " here"))]
    support.sqlite_store(path, schema, rows)
    return body


@pytest.mark.parametrize("how", JOINS)
def test_bytes_of_different_values_never_join_into_a_finding(sandbox, project, how):
    rel = f"{R}/joined-{how}.db"
    body = _join_store(project / rel, how)
    raw = (project / rel).read_bytes()
    joined = ("sk" + "_" + body).encode()
    assert joined in raw, "premise: the raw bytes of the store spell the joined token-shaped string"
    alone = support.rule_sets()["alone"]
    assert "gov-token-digit" in support.gitleaks_finds(b"\n" + raw[raw.find(joined) - 40:], alone), (
        "premise: the joined bytes are a gov-token-digit finding")
    for value in support.live_values(project / rel):
        for name, config in support.rule_sets().items():
            assert support.gitleaks_finds(f" {value} \n", config) == [], (
                f"premise: a stored value alone is a finding by the rule set {name}")
    run = support.run_check(sandbox, project)
    _assert_none_named(run, [rel], f"the byte join ({how}): no stored value holds a token")
