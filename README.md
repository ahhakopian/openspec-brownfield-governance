# OpenSpec Brownfield Governance

`openspec-brownfield-governance` is a standalone overlay for an already
initialized OpenSpec project using the standard `spec-driven` schema. It
packages three audited Codex skills and the brownfield configuration rules that
connect persistent AS-IS evidence, approved product boundaries, normal OpenSpec
changes, and cross-change sequencing.

Version 0.1.0 is a faithful extraction of an existing working installation. It
is not a redesign.

## Ownership

The distribution owns:

- `brownfield-map`;
- `product-boundaries`;
- `cross-change-roadmap`;
- the additive brownfield config clauses;
- the empty deferred-change index structure;
- its receipt and bootstrap machinery.

OpenSpec owns `.agents/skills/openspec-*`, `.openspec-target`, the
`spec-driven` schema, and the standard lifecycle. The target project owns all
maps, product documents, roadmaps, PRDs, specs, changes, archives, and deferred
change records.

## Install

From this repository:

```bash
python3 bootstrap/openspec-brownfield.py install --target /path/to/project
python3 bootstrap/openspec-brownfield.py doctor --target /path/to/project
```

The target must already be a Git repository initialized for OpenSpec and Codex.
The installer never runs `openspec init` and never changes OpenSpec-owned
skills.

Use `--dry-run` with install, update, or uninstall to preview without writes.
See [installation](docs/installation.md), [updating](docs/updating.md), and
[compatibility](docs/compatibility.md).

## Public release status

No license has been selected. Publishing or redistributing this package
publicly is blocked until a license is chosen and added.

## Known inherited issue

The extracted `brownfield-map` skill contains one reference to
`openspec/system/product-boundaries.md`; the rest of the audited workflow uses
`docs/product/product-boundaries.md`. Version 0.1.0 preserves that source text
exactly. A correction requires a later reviewed release.

The extracted `product-boundaries` description also contains an unquoted
colon in YAML frontmatter. The current strict skill validator rejects that
frontmatter even though the reference installation discovers the skill.
Version 0.1.0 preserves it to retain extraction fidelity.
