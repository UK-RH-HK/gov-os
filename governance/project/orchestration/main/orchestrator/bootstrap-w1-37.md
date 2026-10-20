
## W1-37 residuals (Superpowers three-skill copy, 2026-10-04)

Recorded at W1-37's close, from the ticket lead's summary. None is a defect.

- **Zero headroom on the sizes.** The three `SKILL.md` sizes (2,389, 2,360 and 899 by floor(characters ÷ 4),
  DEC-247) sit exactly on their ceilings. "Characters" is read as decoded UTF-8; counted as bytes the three would be
  2,394, 2,366 and 911 and fail. Any upstream change to a `SKILL.md` breaks the test.
- **File modes are not asserted.** `find-polluter.sh` kept its executable bit in the copy, but no test protects it.
- **No licence in the copy.** `template/governance/kernel/skills/superpowers/` holds no `LICENSE`; the upstream
  licence stays in the vendor folder, which is the only source (DEC-244).
- **CAP-24 for vendored skills.** The version is recorded beside the copies, in `vendored.yaml`, not in each
  `SKILL.md` frontmatter; the owner reads CAP-24 this way for vendored skills (DEC-262). `gov close` (W1-30) reads a
  vendored skill's version from that record.
- **Guard refusals met by the engineer.** `mkdir -p` with `cp -R` onto the `superpowers` folder itself was refused,
  so the files were copied one by one to literal paths.
