import sys
p = sys.argv[1]
L = open(p, encoding="utf-8").read().split("\n")
def idx(prefix, start=0, stop=None):
    for i in range(start, stop or len(L)):
        if L[i].startswith(prefix):
            return i
    raise SystemExit("not found: " + prefix)
# front matter only (before the second '---')
end = L.index("---", 1)
i = idx("  - Every brief template and the orchestration skill carry", 0, end)
L[i] = ('  - The orchestration skill carries the twelve-field rule, the payload-after rule, and "stop after two '
        'identical refusals and return" [AR-5, AR-6].')
i = idx("  - They also carry Policy 2", 0, end)
L[i] = L[i].replace("  - They also carry Policy 2", "  - It also carries Policy 2")
i = idx("  - The audit brief states DEC-430", 0, end)
L[i] = ("  - The orchestration skill's audit brief rule states DEC-430, as the audit skill's own wording does "
        "[F-m1, W2-L268].")
i = idx("  - The launcher command is stated as a command", 0, end)
del L[i]
i = idx("  - The five brief templates carry record frontmatter", 0, end)
L[i] = "  - Loose citations in the orchestration skill are fixed [W2-L256]."
i = idx("  - 'Supersession (DEC-866): the brief templates, the orchestration skill", 0, end)
L[i] = L[i].replace("the brief templates, the orchestration skill", "the orchestration skill")
i = idx("  - 'The kernel''s lead brief template carries a `brief_gaps:`", 0, end)
L[i] = ("  - 'The orchestration skill states that the gaps a worker names in `brief_gaps:` (the return of the brief "
        "envelope, W2-128) are fixed in the template within the week (DEC-943, ROLES-SPEC-1 G14) [DEC-983, DEC-982] "
        "(to Wave 3, W3-P02, W-10) [re-scoped, DEC-1083]'")
i = idx("- DEC-1112", 0, end)
L.insert(i + 1, "- DEC-1137")
i = idx("# W2-11 Briefs and the orchestration skill")
L[i + 1:i + 1] = ["",
    "**DEC-1137 (2026-11-11):** W2-11's brief KPIs are re-baselined to what W2-128 left (DEC-105 option (c)): the five "
    "`brief-*.md` files are one-line pointers and stay so, and the front matter's KPI lines name the skills, `skill.md`, "
    "the orchestration, test-design and QA-review skills and the audit's DEC-430 wording. Where the card's older list "
    "under \"KPIs, success\" below names a brief template's content, the front matter holds; the role templates carry "
    "Policy 2's refusals, DEC-861's record rule and the two-refusal stop under W2-175 (DEC-1137 (2))."]
open(p, "w", encoding="utf-8").write("\n".join(L))
