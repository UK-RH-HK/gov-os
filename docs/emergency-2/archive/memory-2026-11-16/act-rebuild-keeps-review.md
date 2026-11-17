---
name: act-rebuild-keeps-review
description: an ACT bundle rebuild deletes and recreates acts/<ACT>/, taking review.md with it; tell builders to save review.md as acts/<ACT>.review-rN.md before rebuilding
metadata:
  type: feedback
---

On 11-16 the ACT-BOX-LAUNCH-1 builder refroze its manifest by re-running the build script, which removes and recreates acts/ACT-BOX-LAUNCH-1/. That deleted round 1's review.md. I rebuilt it from the reviewer's return as acts/ACT-BOX-LAUNCH-1.review-r1.md.

**Why:** build scripts treat the bundle folder as theirs alone, but review.md belongs to the reviewer.

**How to apply:** every refreeze brief says "copy review.md to acts/<ACT>.review-rN.md before rebuilding; never delete a review". This is GF-8's form (ACT-GUARD-FIX-8.review-r1.md).
