# API specification (requirements)

The service SHALL expose `run(name, level)` and SHALL clamp `level` to 0..10.
Acceptance: `run("Hello World", 42)` returns `hello-world:10`.

Back-link: [architecture](../docs/architecture.md).
