"""KPI 2 (DEC-911 item 4): a real token of row W2-L423's rule's vendor still fails, for the check and the pre-index
filter, in a file and in a stored value: a token in each of the rule's prefixed forms, and a bare 40-hex string that
names no object of the repository (after either keyword, and in upper case), each built at run time, in a project
whose repository has real commits (so the verification runs and answers no).

Guards, green today: today's check and filter find each. They must stay green.
"""

from __future__ import annotations

import pytest

import w2_71_support as support

pytestmark = [support.needs_gitleaks, support.needs_git, pytest.mark.local_only]


def forms():
    """{form: (the line that holds it, the 40-hex part that a verification would ask git about)}, built at run time."""
    p40 = support.hex_of("token-prefix-40")
    p16, p16_40 = support.hex_of("token-prefix-16", 16), support.hex_of("token-prefix-16-40")
    local = support.hex_of("token-prefix-local")
    bare_v, bare_p, upper = (support.hex_of("token-bare-vendor"), support.hex_of("token-bare-prefix"),
                             support.hex_of("token-bare-upper").upper())
    deploy = "the deploy token is {} for now\n"
    return {
        "prefixed-40": (deploy.format(support.PREFIX + p40), p40),
        "prefixed-16-and-40": (deploy.format(f"{support.PREFIX}{p16}_{p16_40}"), p16_40),
        "prefixed-local-and-40": (deploy.format(f"{support.PREFIX}local_{local}"), local),
        "bare-40-after-vendor-keyword": (support.vendor_line(support.VENDOR, bare_v, verb="token"), bare_v),
        "bare-40-after-prefix-keyword": (support.vendor_line(support.PREFIX, bare_p, verb="token"), bare_p),
        "bare-40-upper-case": (support.vendor_line(support.VENDOR, upper, verb="token"), upper),
    }


FORMS = list(forms())
PLACES = ["file", "store"]


class Scene:
    def __init__(self, sandbox):
        self.repo = support.make_repo(sandbox, "token-project", label="tokens")
        root = self.repo.root
        self.check_rels, self.filter_rels = {}, {}
        for name, (line, _) in forms().items():
            self.check_rels[(name, "file")] = f".gov-runtime/scratch/{name}.log"
            self.check_rels[(name, "store")] = f".gov-runtime/stores/{name}.db"
            self.filter_rels[(name, "file")] = f"docs/{name}.md"
            self.filter_rels[(name, "store")] = f"docs/{name}.db"
            for rels in (self.check_rels, self.filter_rels):
                support.write(root / rels[(name, "file")], "a log\n" + line)
                support.sqlite_store(root / rels[(name, "store")], ["a log", line])
        self.check = support.run_check(sandbox, root)
        self.filter = support.run_filter(sandbox, root, sorted(self.filter_rels.values()))


@pytest.fixture(scope="module")
def scene(module_sandbox):
    return Scene(module_sandbox)


@pytest.mark.parametrize("name", FORMS)
def test_premise_the_token_is_a_finding_of_row_w2_l423s_rule_and_names_no_object_here(scene, name):
    line, body = forms()[name]
    toml = support.gitleaks_toml()
    extended = support.gitleaks_finds(line, toml)
    alone = support.gitleaks_finds(line, support.project_rules_alone(toml))
    ok = extended == [support.RULE_ID] and alone == []
    assert ok, support.say(f"{name}: the rule sets find {extended} and {alone}, not row W2-L423's rule alone")
    names_object = support.is_object(scene.repo.root, body.lower(), None)
    assert not names_object, f"{name}: the token's 40-hex part names an object of the project"


@pytest.mark.parametrize("place", PLACES)
@pytest.mark.parametrize("name", FORMS)
def test_a_real_token_of_the_vendor_is_a_finding_of_the_check(scene, name, place):
    rel = scene.check_rels[(name, place)]
    assert scene.check.ended, f"the check did not end within its declared limit\n{scene.check.describe()}"
    named = scene.check.names(rel)
    assert named and scene.check.returncode == 1, (f"the check lets a real token through: {name} in a {place} "
                                                   f"({rel})\n{scene.check.describe()}")


@pytest.mark.parametrize("place", PLACES)
@pytest.mark.parametrize("name", FORMS)
def test_a_real_token_of_the_vendor_is_left_out_by_the_filter(scene, name, place):
    rel = scene.filter_rels[(name, place)]
    assert scene.filter.ended, f"the filter did not end\n{scene.filter.describe()}"
    passes = scene.filter.passes(rel)
    assert not passes, f"the filter lets a real token through: {name} in a {place} ({rel})\n{scene.filter.describe()}"
