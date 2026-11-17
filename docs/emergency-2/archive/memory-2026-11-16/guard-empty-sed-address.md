---
name: guard-empty-sed-address
description: never run sed -i "${n}s|^|…|" with n from grep unguarded; an empty n prefixes EVERY line of ready.txt
metadata:
  type: feedback
---

On 11-16 I commented out returned lead lines in dispatch/ready.txt with `n=$(grep -n "^<line>" ready.txt | cut -d: -f1); sed -i "${n}s|^|# …|" ready.txt`. If the grep finds nothing, n is empty and the sed has no address, so it prefixes every line of the file and the dispatcher's whole list is commented out. It matched every time, by luck.

**Why:** the dispatcher reads ready.txt to launch leads. Mangling it stops every launch, and the fault shows up nowhere until the idle check fires.

**How to apply:** always write `[ -n "$n" ] && sed -i "${n}s|^|…|" ready.txt || echo "NO MATCH"`, or do the edit in Python with an assert that the line occurs exactly once.
