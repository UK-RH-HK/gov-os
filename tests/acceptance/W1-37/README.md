# W1-37 — Superpowers three-skill vendoring: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-yvzh` (W1-37), DEC-074 Q5,
DEC-076, DEC-194, DEC-199 and the four decisions that settle the KPI wording: DEC-244, DEC-245, DEC-246, DEC-247.
Written before implementation. Profile LITE (DEC-221): one test per KPI line, four tests. No earlier ticket's test
was rewritten.

## Run

```sh
python3 -m pytest tests/acceptance/W1-37 -q -p no:cacheprovider
```

`pytest`, the standard library and PyYAML (to parse the record file). No network. Nothing is installed, downloaded or
run. The tests read the working tree: the vendor folder, the copy and the record file.

## What the engineer must deliver

Everything goes under `template/governance/kernel/skills/superpowers/` (the ticket's `allowed_paths`). The vendor
folder `template/governance/kernel/vendor/superpowers/` and `governance/project/tool-registry.yaml` do not change.

### The copy (DEC-244, DEC-245)

```
template/governance/kernel/skills/superpowers/
  vendored.yaml
  test-driven-development/          every file of vendor/superpowers/skills/test-driven-development/
  systematic-debugging/             every file of vendor/superpowers/skills/systematic-debugging/
  verification-before-completion/   every file of vendor/superpowers/skills/verification-before-completion/
```

- Each skill folder holds the same files, at the same relative paths, with the same bytes, as its vendor folder.
- Real files, not symbolic links.
- Nothing else is in the folder, with one exception: a `LICENSE` at the top is allowed (not required) when it is
  byte-identical to `vendor/superpowers/LICENSE`.

### The record file (DEC-246)

`template/governance/kernel/skills/superpowers/vendored.yaml`, a YAML mapping. Field names follow the tool registry
(`version`, `sha256`). Four fields are read; other fields are allowed and not read.

| Field | Value |
|---|---|
| `version` | The source version: `"v6.4.2"` (`"6.4.2"` is accepted too). |
| `source_sha256` | The DEC-199 digest of `template/governance/kernel/vendor/superpowers/` (all its files, the licence included). A string of 64 lowercase hexadecimal characters. It equals the Superpowers `sha256` of the tool registry. |
| `sha256` | The DEC-199 digest of the copy: every file under `template/governance/kernel/skills/superpowers/` **except `vendored.yaml` itself**. Same format. |
| `token_sizes` | A mapping with exactly the three skill names as keys and the measured sizes as integers (DEC-247). |

```yaml
version: "v6.4.2"
source_sha256: "<64 hex>"
sha256: "<64 hex>"
token_sizes:
  test-driven-development: <integer>
  systematic-debugging: <integer>
  verification-before-completion: <integer>
```

**The DEC-199 digest of a folder.** One line per file: the file's sha256 in lowercase hexadecimal, two spaces, the
path relative to that folder (`/` between components, no leading `./`), one line feed. The lines are sorted as bytes
and concatenated; the digest is the sha256 of the result. From inside the folder:

```sh
find . -type f ! -name vendored.yaml -printf '%P\0' | xargs -0 sha256sum | LC_ALL=C sort | sha256sum
```

(For the vendor folder, drop `! -name vendored.yaml`.) The paths of the copy are relative to
`skills/superpowers/`, for example `systematic-debugging/SKILL.md`, so the two digests differ although the skill files
are identical.

**The size of a skill (DEC-247).** floor(characters ÷ 4) of the skill's `SKILL.md` in the copy, where the characters
are those of the file decoded as UTF-8 (not its bytes). Ceilings, with no tolerance: test-driven-development 2,389;
systematic-debugging 2,360; verification-before-completion 899.

## KPI → test → red reason today

All four tests are in `test_w1_37_skills.py`. Red run on `w1/W1-37` at `b7e6da3b`: **4 errors, 0 passed**. Every
test stops in the `copy` fixture with the same reason:

> `template/governance/kernel/skills/superpowers/ does not exist: W1-37 has not copied the three skills`

| KPI line | Test | What it asserts | Red reason today |
|---|---|---|---|
| Success 1: "test-driven-development, systematic-debugging and verification-before-completion copied from v6.4.2, namespaced, with source hash recorded" | `test_the_three_skills_are_copied_from_v6_4_2_into_the_namespace_with_the_source_hash_recorded` | Each `skills/superpowers/<skill>/` has the same file set and bytes as its vendor folder; no symbolic links; the record's `version` is v6.4.2; `source_sha256` equals the recomputed digest of the vendor folder. | The copy folder does not exist. |
| Success 2: "Token sizes measured and within the I-09 figures; no plugin, no SessionStart hook, no subagent-driven-development" | `test_the_token_sizes_are_measured_and_within_the_figures_and_no_plugin_hook_or_excluded_skill_is_there` | Each copied `SKILL.md` measures at or below its ceiling; `token_sizes` equals the measured sizes; no plugin file (`plugin.json`, `marketplace.json`, a folder with `plugin` in its name), no hook file (a `hooks` folder, `hooks.json`, a `session-start*` file), no `subagent-driven-development`. | The copy folder does not exist. |
| Failure 1: "Any other Superpowers skill or hook is present" | `test_no_other_superpowers_skill_or_hook_is_present` | The three `SKILL.md` are there and no other; no hook file; every file is in one of the three skill folders, or is `vendored.yaml`, or is a `LICENSE` identical to the vendor's. | The copy folder does not exist. |
| Failure 2: "A vendored file differs from its recorded hash" | `test_no_vendored_file_differs_from_its_recorded_hash` | The record's `sha256` equals the recomputed digest of the copy without `vendored.yaml`; a change to any single file would no longer match it. | The copy folder does not exist. |

## Readings

1. **Record file name, format and fields** are chosen here, within DEC-246, which fixes none of them.
2. **The copy's digest leaves the record file out**, because a file cannot hold its own digest. Everything else under
   the folder is covered.
3. **Characters** in DEC-247 are Unicode characters, not bytes.
4. **A licence in the copy** is allowed, not required: DEC-244 copies the skill folders, and the KPI failure line names
   skills and hooks only. The upstream licence stays in the vendor folder, which travels in the same template.
5. **File modes are not asserted.** DEC-245 defines "unchanged" as byte-identical.
6. **The tests read the working tree**, not `HEAD`, so they can go green before the commit. W1-06's suite already
   asserts that the vendor folder equals its committed state.
7. **Not asserted** (DEC-245, DEC-247): a version in any `SKILL.md` frontmatter, either way; the figures 8,089 and 795.
