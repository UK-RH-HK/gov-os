p = "ACT-PERMISSIONS-3.md"
s = open(p).read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:70])
    s = s.replace(old, new)


rep("7b79aa2de9b12453fa673a90cd65acb7dbd25d4de6088cc58cfc8407f99389a8", "e567660a69685d102f3eb860e89d09cb738516e69b5cac6a18d8749db9cf0779", 2)
rep("7b79aa2de9b1", "e567660a6968")
rep("yes ACT-PERMISSIONS-3 7b79aa2d", "yes ACT-PERMISSIONS-3 e567660a", 2)
rep("30803df99ae7", "acb46a637d48", 4)
rep("56 checks", "62 checks", 2)
rep("56 checks, 0 failures", "62 checks, 0 failures") if "56 checks, 0 failures" in s else None
rep("""  Two rules are added to `permissions.allow`. Nothing is removed. No `deny`, `ask`, hook or directory changes.""",
    """  Two rules are added to `permissions.allow` and six to `permissions.deny` (Edit and Read of key, pem and env-named
  files under the same folders). Nothing is removed. No `ask`, hook or directory changes.""")
rep("""| **Allow**, this ACT: `Edit(//tmp/gov-os-emg-*/**)` and `Read(//tmp/gov-os-emg-*/**)` in `.claude/settings.local.json` |""",
    """| **Allow**, this ACT: `Edit(//tmp/gov-os-emg-*/**)` and `Read(//tmp/gov-os-emg-*/**)` in `.claude/settings.local.json`, with six deny rules for key, pem and env-named files under them |""")
old = s[s.index("## 2. What changes"):s.index("- `//` is Claude Code's")]
new = '''## 2. What changes
`.claude/settings.local.json`: two entries at the end of `permissions.allow` (42 rules become 44) and six at the end of
`permissions.deny` (4 become 10):
```
50c50,52
<       "Bash(cd ~/gov-os-worktrees/*)"
---
>       "Bash(cd ~/gov-os-worktrees/*)",
>       "Edit(//tmp/gov-os-emg-*/**)",
>       "Read(//tmp/gov-os-emg-*/**)"
56c58,64
<       "Read(//home/usain/gov-os-eval/fixtures/evaluation/memory-verdict-2/**)"
---
>       "Read(//home/usain/gov-os-eval/fixtures/evaluation/memory-verdict-2/**)",
>       "Edit(//tmp/gov-os-emg-*/**/*.key)",
>       "Edit(//tmp/gov-os-emg-*/**/*.pem)",
>       "Edit(//tmp/gov-os-emg-*/**/.env*)",
>       "Read(//tmp/gov-os-emg-*/**/*.key)",
>       "Read(//tmp/gov-os-emg-*/**/*.pem)",
>       "Read(//tmp/gov-os-emg-*/**/.env*)"
```
Everything else is byte for byte as before. sha256 before `d715292711a2`, after `acb46a637d48`, mode 644.
- **The six deny rules** are the project's own deny names (`Edit(**/*.key)`, `Edit(**/*.pem)`, `Edit(**/.env*)` in
  `.claude/settings.json`) put under the allowed folders, for Edit and for Read. Those project rules are relative to the
  project and never reached `/tmp`; a deny rule wins over every allow, so the allow no longer opens these names.
  `**/` matches no folder or any number, so a key file directly in the folder is covered (rehearsed).
'''
s = s.replace(old, new)
rep("""- The two checks (after the apply): the two rules are the last two of the allow list, the list has 44 rules, no `Write(`
  rule and nothing holding `//tmp/**`, deny (4) and `additionalDirectories` (2) as before; the file parses.""",
    """- The two checks (after the apply): the two rules are the last two of the allow list, the list has 44 rules, no `Write(`
  rule and nothing holding `//tmp/**`; the six deny rules are the last six of a deny list of 10; `additionalDirectories`
  (2) as before; the file parses.""")
rep("""Still asked or refused, with both rules in place:""", """Still asked or refused, with the rules in place: a Write or Read of a key, pem or env-named file under a
`gov-os-emg-*` folder (now denied);""")
rep("""check (applied); the diff is exactly §2's; the parsed result is the original plus the two
  rules, key order kept; deny, additionalDirectories, hooks and env unchanged;""",
    """check (applied); the diff is exactly §2's (two hunks); the parsed result is the original plus the two
  allow and six deny rules, key order kept; the old deny rules kept in order; additionalDirectories, hooks and env unchanged;""")
rep("""link inside a `gov-os-emg-*` folder to the stand-in sets root; a `cp` out of `.claude/hooks/`.""",
    """link inside a `gov-os-emg-*` folder to the stand-in sets root; a `cp` out of `.claude/hooks/`.
  - **B2k, the key names:** under an allowed folder an ordinary file still writes, and a Write of a `.key` file, a `.pem`
    file (in a sub-folder), `.env` and `.env.local`, and a Read of a `.key`, a `.pem` and an `.env.*` file, are all denied.""")
old = s[s.index("- **Earlier runs:**"):s.index("## 7. The operator's steps")]
new = '''- **Earlier runs:** two exploration passes set the rule form (`Edit(...)` and `Read(...)` with a `*` inside a folder name
  work) and found B2's cause. The first full run failed two checks: the manifest's check named the real HOME (the
  operator's path rule refused it; now a count), and a key-named file written in an allowed folder passed. The second
  run (56 checks) showed that as information; at the coordinator's request the six deny rules were added, and the third
  run (62 checks) denies it.

'''
s = s.replace(old, new)
old = s[s.index("3. **A key-named file"):s.index("4. **Symlinks:**")]
new = '''3. **Key-named files** (`*.key`, `*.pem`, `.env`, `.env.*`) under a `gov-os-emg-*` folder stay denied to Edit, Write and
   Read: the six deny rules of §2 (rehearsed, B2k). Other secret-like names are not listed (the project's own list has
   none more under Edit; `config/secrets*` is a repository path).
'''
s = s.replace(old, new)
open(p, "w").write(s)
