# Research brief: the first import study, Startup Launchpad, with REA (DEC-1228 (2) to (4))

Role: **research** (Sonnet, DEC-1225). Name: `study-startup-launchpad`. You work only in
`/home/usain/gov-os-runs/study-startup-launchpad/` (your session starts there). Never touch the Gov OS repository
(`/home/usain/Dynamic-Agentic-Engineering-OS`) except to read `docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md` and
DEC-1228 in `docs/DECISION_REGISTER.md`; never touch EXAMIN. No `git push`, no `sudo`. Install nothing: REA 6.10.1 is
installed and recorded by the CTO (`tool/`, `governance/project/tool-registry.yaml`) and is given to this session only,
as the MCP server `rea`; its CLI is `tool/node_modules/.bin/rea` with
`PATH=/home/usain/.nvm/versions/node/v22.23.5/bin:$PATH`. A tool you need beyond it: name it in your return.

**The owner's words (DEC-1228 (4)):** "Startup Launchpad (https://startuplaunchpad.app/startup-launchpad), a service
that scans the repository and live site of AI-built apps for security issues, explains them in plain English and writes
fix prompts. REA sees its website and its browser code; its scanning engines run on its servers, so their behaviour is
studied from its output: run it on a synthetic test repository with planted issues, never on our own code."
**His rule for reconstructed code (DEC-1228 (3)):** it is study, its origin recorded (the app, its version, the date,
REA); studied and used in research only; nothing of it goes into a product without an absorb assessment stating
whether we hold a commercial licence.

## What to do
1. **The website and its browser code, with REA** (`analyze-web-bundle`, `capture-browser-scenario`,
   `capture-web-screenshot`, `analyze`; public pages only, no sign-up, no login, no payment, no form submitted). Record
   what the product claims to scan, the flow a user goes through, the checks it names, and what its shipped JavaScript
   reveals of the client side (endpoints, the report's shape, how fix prompts are produced if visible). Keep REA's raw
   evidence under `records/rea/` with the origin header (app, version or bundle hash, date, REA 6.10.1).
2. **The synthetic test repository** in `synthetic-repo/`: a small AI-built-looking web app (for example a Next.js or
   Express app with a tiny front end) with **planted issues**, each listed in `synthetic-repo/PLANTED.md` with its class
   and where it sits: a fake hard-coded API key (obviously fake, e.g. `sk-test-PLANTED-...`), a public Supabase/Firebase
   rule left open, SQL built from a string, missing auth on an admin route, CORS `*` with credentials, an outdated
   dependency with a known CVE, secrets in a committed `.env.example` that look real but are fake, no rate limit on a
   login route, an XSS sink. No real secret anywhere. Commit it locally (`git init`; no remote).
3. **What a scan needs from us.** From the public pages: how the service takes a repository and a site (GitHub app or
   OAuth, a public URL, an upload), its price and free tier, its terms on submitted code. Write the exact steps the
   owner would take to run one scan on `synthetic-repo` (for example: he pushes it to a new private GitHub repository
   and deploys it to a throwaway host), because pushes and accounts are his. Do not create accounts.
4. **The study record** `records/STUDY.md`: what the product does; the checks it claims, mapped to the planted issues
   (which it should catch, by its claims); what is worth absorbing for Gov OS (for example a security stage for adopted
   repositories, plain-English findings, fix prompts) classed as the imports spec does (use / absorb / study), each
   absorb candidate with "commercial licence: none held" unless found otherwise; open questions for the owner.

## Return (your final message, short)
The record's path; three lines on what the product is and does; the owner's steps for the one scan (step 3); the
absorb candidates in one line each; anything REA could not do; minutes and cost.
