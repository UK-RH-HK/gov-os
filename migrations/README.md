# Framework migrations

Declarative, versioned migration definitions executed by `gov update --apply`. Each file is validated against
`framework/schemas/migration.schema.json`. Migrations may only touch `governance/project/` (overlay),
`governance/framework.lock`, `governance/generated/` and derived runtime. They never modify `spec/` or `product/`
(hard invariant INV-013).

Overlay-template changes reach installed projects only through a migration operation. `sync_overlay_template` carries
the previous release's template (`base`) and converges the project's overlay file with the template of the kernel being
installed by a three-way merge: what the project never customised follows the new template (values, rules added and
removed, rule order), what it customised is kept, and a customisation the template also changed is kept and reported.
`gov release build` refuses a release whose migration would leave an installed project with an untouched overlay
different from a new installation of the same release (`migrations::framework::check_substance`).
