# Phase 2 — Option B escalation: the check reasons about a representation; the effect comes from elsewhere

| Field | Value |
|---|---|
| Date | 2026-09-23 |
| For | the product owner |
| From | the Phase-2 outer orchestrator |
| Trigger | **OD-P2-07 §8, triggered on both limbs** by P2-AR-0079 |
| Status | **STOPPED.** `cap2-candidate-2` **not** minted. No further local repair round. |
| Evidence | `AGENT_RUNS/P2-AR-0079.run.yaml`; report and 2,461 lines of probes on `phase2/remediation-ac-review` (`d296e6b`, `7f78ede`); reviewed commit `35461c9`, frozen |

## 1. The verdict

`RESIDUAL_DEFECTS` — **three materially new HIGH**, plus AR77-F1/F2/F4 **narrowed but not closed**. Both properties
fail. The reviewer's own judgement: *"Is the architecture sound? **No.**"*

**I verified every load-bearing claim in the source myself before accepting it.** They are all exactly as reported.

## 2. The two proofs, and why they are not more enumeration

### P79-F11 — verified bytes are not the executed bytes, on the *conforming* path

```
env --chdir=decoy sh install.sh      (install.sh correctly pinned and verified)
```

The OS hashed `<root>/install.sh`, matched it, declared the command readable, installed **ungated** — and the kernel
executed `<root>/decoy/install.sh`.

*Verified by me:* `tools.rs:995` treats any token starting with `-` as a wrapper flag and skips it, so `--chdir=decoy`
is consumed and `prog` becomes `sh`; the interpreter's operand is then hashed at the project root. `util.rs:320–323`
sets `current_dir` to the project root, but `env --chdir` overrides that *after the process starts*.

**This defeats pinning itself, and it does not depend on `plain_argument_programs` at all.** Deleting that list — the
core of Option A — closes P79-F1 and leaves this untouched. There is also a revealing asymmetry the reviewer found:
`env -C decoy` **gates** (the bare `decoy` token becomes an unrecognised program), while `env --chdir=decoy` does not.
No list of flags fixes that class; it is a consequence of reading argv at all.

### P79-F1 — the environment rebinds the program after classification

```
env PATH=. true          →  installed ungated; the kernel executed <root>/true
```

*Verified by me:* `tools.rs:994` consumes every `NAME=value` token as "meaningful for env", so `prog` resolves to a
surviving plain-argument name; `util.rs:320` uses `Command::new(...)` with **no `env_clear()` and no environment
control**, so `PATH=.` takes effect. The executed file is a project file in **no** `pinned_files` entry, hashed by
nothing. **26 of 26** rebinding shapes classify as readable (`PATH`, `LD_PRELOAD`, `LD_AUDIT`, `PYTHONPATH`,
`BASH_ENV`, `GIT_SSH_COMMAND`, …).

Note the internal inconsistency this exposes: **the product already treats loader variables as code substitution for
plugins** (`binding::LOADER_ENV_VARS`, BC-P2-40). The install envelope does not.

### The generalisation

> Property A binds **lexical `argv`** while the kernel executes what `argv` **resolves to**, through an environment and
> a working directory that the same `argv` controls.

That cannot be repaired by reading `argv` more carefully, because the thing that decides what runs is not in `argv`.

### P79-F8 — the predicate is one-directional

The single authoritative predicate models classes that **grant exemptions**. It cannot express the **obligations**
`class` carries. One hand edit:

```yaml
- {pattern: "product/*.py", class: test}    # overlaps kernel product/** (source)
```

confers no exemption, is equal on every compared field, and is therefore **accepted, applied, refused by nothing and
reported nowhere** — `gov policy overrides` empty, doctor **D027 passes**. Effect, with its own control in the same
probe: a `documentation`-class task changed `product/app.py` and **closed**, where the identical task is refused
`MATERIAL_CHANGE_REQUIRES_CIT` without the edit.

*Verified by me:* `policy_precedence.rs:677` reads `if n.flag(field) && !k.flag(field)` — refusing only a **gain**.
`source` → `test` differs only in index flags, all *lost*. And **12 further `class()` consumers exist in `cit/`,
`context/` and `memory/` alone**, outside the table. 22 class transitions are unguarded.

**This is the enumeration pattern recurring for the fifth time, in the complementary direction.** Round 4 missed
*consumers* of exemptions; round 5 misses *obligations* that are not exemptions at all.

## 3. What the remediation did achieve — it was not wasted

- **AR77-F3 is genuinely closed** for all six exempting values, re-verified by the reviewer's own probes.
- **Every previously closed attack stays closed**: AR68-F1..F5, AR73-F1/F2/F4/F5/F6, AR75-F1/F2 (72 cases, all gated
  with a stated reason). `review_subject` **does** bind argv — independently re-derived, five mutations each refused.
  Pin re-verification at execution lifetime holds.
- **Every negative control passes. The surface does not gate everything** — a conforming pinned install proceeds
  ungated with zero gate records *and the script actually runs*; `gov init` on brownfield refuses nothing.
- **1,176 adversarial cases** (hostile token shapes × programs × command fields — malformed authorities, embedded NUL,
  4 KiB tokens, 300-segment paths, UNC spellings) produced **no panic, no non-JSON answer, always gated, never
  installed.** The `UnrecognisedProgram` decoupling is **mis-claimed, not unsafe** — the builder's "can only add
  findings" is false (P79-F3b, LOW), but nothing exploitable followed.
- **The full suite is green at 263/0** on my own machine-exclusive run.

The reviewer also audited all six changed test assertions against `git show 35461c9`: each stricter or equal-plus-more.
**None weakened to pass.**

## 4. Why I am not proposing a sixth round

Five rounds, five enumerations: programs → command shapes → list-entry premises → class values → consumers of class →
and now **obligations of class**. Each round fixed the list it was handed. The pattern is now unambiguous, and both new
failures share one shape:

> **The check reasons about a representation; the effect comes from somewhere the representation does not cover.**

For A the representation is `argv` and the effect comes from the environment and cwd. For C the representation is
"exemptions gained" and the effect comes from obligations lost. Reading the representation more carefully cannot close
either.

## 5. Options

**B — own the execution environment (recommended for A, and it is smaller than it sounds).** Option B was framed as
sandboxing, but P79-F1 and P79-F11 both have the *same* narrow root cause: `util.rs:320` execs with an **inherited
environment** and lets `argv` override the working directory. Clearing the environment to a controlled allowlist,
pinning the working directory so it cannot be overridden, and executing the **verified artefact by resolved absolute
path** rather than by the string in `argv`, would close both — and that is Option B's principle (*own the execution
boundary*) applied minimally, **not** another list. Full isolation remains the longer-term goal; this is its first and
cheapest increment.

**A prerequisite you need to know about, for C.** P79-F10 found that **the product has no mechanism anywhere to
distinguish a governed contract change from a hand edit** — the reviewer searched and found none, and says the search
was targeted rather than exhaustive. Until that exists, "require change control for class changes" cannot be
implemented, because nothing can tell the two apart. **Property C cannot be completed without it.** That is an
architectural gap, not a detail, and the reviewer deliberately graded F10 MEDIUM rather than HIGH precisely because the
builder's own test asserts this as the *preserved capability*.

So for C the realistic choices are: **(i)** make the predicate bidirectional — model obligations as well as exemptions
— which is better than today but still an enumeration over consumers; or **(ii)** refuse *any* class change on a path a
kernel rule governs unless it arrives through an authenticated governed route, which is the OC-P2-04 answer and
**requires building the mechanism F10 says is missing**; or **(iii)** accept and disclose.

**C — re-scope.** Place the install-trust and class-authority surfaces at R2 certification with these residuals
recorded, and let Phase 2 close on the other 51 classes, which are done. **Yours alone**; it changes what must hold now
rather than what is true.

**D — accept and disclose**, mint, and let formal verification judge. I do not recommend it: AC-3 and AC-4 would fail
on three HIGHs we have characterised and proven.

## 6. My recommendation

**Authorise the minimal execution-boundary work for A** (controlled environment, pinned cwd, execute the verified
artefact by resolved path), because it closes two proven HIGHs at the root rather than by enumeration and is the first
increment of the architecture you have already identified as correct.

**For C, decide the prerequisite first**: is the OS to gain a way to distinguish a governed contract change from a hand
edit? Everything else about C depends on that answer, and I cannot adjudicate it — it defines what "project-editable"
means, which is a product architecture decision.

**And consider C (re-scope) seriously.** Five rounds on one surface, with 51 of 52 classes closed, is itself
information about where the remaining risk sits and how much more of this phase it is worth spending. That judgement is
yours, not mine.

## 7. What is preserved

Everything is committed and reproducible: the frozen implementation (`35461c9`, full suite 263/0), the review with
2,461 lines of independent probes (`d296e6b`, `7f78ede`), all five prior reviews with their harnesses, every decision
and adjudication, and the non-normative V8.3 evidence package. State verifies consistent. Nothing moves until you
choose.
