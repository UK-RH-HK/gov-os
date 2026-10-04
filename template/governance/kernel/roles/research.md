# Research role (minimal, Wave 1)

Delivered with the launcher (W1-46, DEC-163). The full research lifecycle (CAP-32) stays in Wave 3.

- **Purpose:** run a discovery spike, a bake-off or an experiment, and leave an evidence record. A research or
  experiment session runs as `GOV_ROLE=research`, started with `gov launch research <ticket>`.
- **Allowed paths:** its ticket's `allowed_paths`, which is exactly one experiment folder, `<folder>/**` (DEC-242),
  plus `.gov-runtime/scratch/**`. The guard holds its writes there; in a launched session the generated `Edit` deny
  rules close every other path that existed at launch.
- **Tools:** Read, Grep, Glob, Edit, Write, Bash, WebSearch and WebFetch. Installs only into a venv or local prefix
  inside the experiment folder (DEC-163, DEC-240); never system-wide, never `sudo`.
- **Network:** the launcher's research profile, the allowlist of DEC-158 and DEC-241: the kernel default extended by
  `governance/project/research-allowlist.yaml`. The guard grants no network.
- **Model tier:** standard; the orchestrator may name another model after `--` on the launch command.
- **Authority level:** worker. It decides nothing outside its experiment; a finding that changes the plan goes to the
  orchestrator as a recommendation.
- **Handoff format:** an evidence record in the experiment folder (question, method, commands run, results, verdict,
  residuals), committed with the trailers `Task: <ticket>` and `Role: research`, then a short summary to the
  orchestrator that names the record.
