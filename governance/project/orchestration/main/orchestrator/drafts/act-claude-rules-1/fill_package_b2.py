"""Round b2: puts the new hashes, head and yes line into acts/ACT-CLAUDE-RULES-1.package.md (prose and the hand block's
expected sha; the commands themselves are unchanged)."""
from pathlib import Path

p = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-RULES-1.package.md")
t = p.read_text()
OLD_M, NEW_M = "199dd123fb0edf3ab699c476d6fb2cc2280a1ecfd966ae21e599be7f2328ed26", "38d4a2df4399bdcddc25d661b997314ccc3345897eedb3e96928056d0a49ffea"
rep = [
    ("`HEADB2`", "`9a467f3360a9`"),
    ("yes ACT-CLAUDE-RULES-1 199dd123\n", "yes ACT-CLAUDE-RULES-1 38d4a2df\n"),
    ("**Round O's line\n`yes ACT-CLAUDE-RULES-1 83c5faf6` is void**: that manifest is no longer the bundle's.",
     "**Round O's line\n`yes ACT-CLAUDE-RULES-1 83c5faf6` and round b1's `yes ACT-CLAUDE-RULES-1 199dd123` are void**: those manifests are no longer the bundle's."),
    ("`undo ACT-CLAUDE-RULES-1 199dd123`", "`undo ACT-CLAUDE-RULES-1 38d4a2df`"),
    ("| `.rulesync/rules/governance.md` | `aab9e7c05dd61f6fb734cc8973e0489c5f176362971c7b4b869c8b016a5155d7` | `3b141726f84a87317c6a745193f8fe671da66208ca0e1f35ec63f9e5b8daabc7` |",
     "| `.rulesync/rules/governance.md` | `aab9e7c05dd61f6fb734cc8973e0489c5f176362971c7b4b869c8b016a5155d7` | `52fd435b377679ba9625970c8808d1b88dd6aa4ed7ccde8b67b690c71df5ed97` |"),
    ("| `CLAUDE.md` | `f672e46802d34c2fbc6340b97b06336c0f93119785572f45a67a49e13d258249` | `65e244836adf4ed79a158b144e5b80bfd022d17b414991e19c3530ef6c2639f2` |",
     "| `CLAUDE.md` | `f672e46802d34c2fbc6340b97b06336c0f93119785572f45a67a49e13d258249` | `c14dfa51ebb6dfa87c8409080109c6d2011ae61b194b499f5a40c59af7c58629` |"),
    ("| `AGENTS.md` | `18e826269b0a0cdc02883c206162d7694b2a9fecc8ce43a578b4c94013eae7d0` | `931f1fe2014e52c7e899dd0589b6f78b308d16fce778c3b2eb4f13aa6527faa1` |",
     "| `AGENTS.md` | `18e826269b0a0cdc02883c206162d7694b2a9fecc8ce43a578b4c94013eae7d0` | `8dcc416e220e8e37ec5214f504d062e61095ec2f75c8c1018ce0728e76c8c51a` |"),
    ("`b7ff8b723440819e64ef527ffd40cf667b3230cb10d8c695938f66282254ee9f`. All as round O.",
     "`b7ff8b723440819e64ef527ffd40cf667b3230cb10d8c695938f66282254ee9f`. The befores are round O's and round b1's; the afters are new in round b2."),
    ("Fresh `--no-hardlinks` clone of `w2/integrate` (`8801ffd17df9`)", "Fresh `--no-hardlinks` clone of `w2/integrate` (`9a467f3360a9`)"),
    ("`TMPDIR` under `/tmp/claude-1000/act-claude-rules-1-b/`", "`TMPDIR` under `/tmp/claude-1000/act-claude-rules-1-b2/`"),
    ("reads the same findings as before (one,\n`.claude/skills/adopt/SKILL.md`) and none on the three files.",
     "reads the same findings as before (none at\nround b2's build) and none on the three files."),
    ("| `list.txt` | `a9b3b90cd70817375c52fee7d50205b48385bdd18b3b331e57ff9bbb7f87672e` |", "| `list.txt` | `e21de3fcb0bc3b8abbe081ed892d7089a34ed84cd675a7f0d03899911e2e2307` |"),
    ("| `rehearsal.log` | `3c9ba3cf9a0283ce157480360b4549be9476ab37bccd23470c2aa7bb8a233e0d` |", "| `rehearsal.log` | `5ff53157ff95a9959ffea20ba7a2c44c4535fb09cfc7be6ba6fb1d01f82f1d77` |"),
    ("**Review: not written yet.** (Round O had none either.)", "**Review: not written yet.** (Round b1's review, of manifest `199dd123`, does not carry over.)"),
]
for a, b in rep:
    assert t.count(a) >= 1, a
    t = t.replace(a, b)
n = t.count(OLD_M)
t = t.replace(OLD_M, NEW_M)
assert "199dd123fb0e" not in t.replace("`199dd123fb0e…`", "")
p.write_text(t)
print(f"filled ({n} full-sha replacements)")
