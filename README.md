# OpenSpec Brownfield Governance

`openspec-brownfield-governance` is a standalone overlay for an already
initialized OpenSpec project using the standard `spec-driven` schema. It
packages seven audited Codex skills and the brownfield configuration rules that
connect persistent AS-IS evidence, approved product boundaries, normal OpenSpec
changes, UI governance, and cross-change sequencing.

Version 0.4.0 adds governed UI review around materially UI-affecting Changes.
It does not redesign OpenSpec or its lifecycle.

## Ownership

The distribution owns:

- `brownfield-map`;
- `product-boundaries`;
- `cross-change-roadmap`;
- `brownfield-complexity-gate`;
- `brownfield-ui-context`;
- `brownfield-ui-preflight`;
- `brownfield-ui-conformance`;
- the additive brownfield config clauses;
- the empty deferred-change index structure;
- its receipt and bootstrap machinery.

OpenSpec owns `.agents/skills/openspec-*`, `.openspec-target`, the
`spec-driven` schema, and the standard lifecycle. The target project owns all
maps, product documents, roadmaps, PRDs, specs, changes, archives, and deferred
change records.

## Governed workflow

The standard non-UI OpenSpec workflow remains unchanged. After a non-UI
Change's planning is complete and before application-code modification, the
governed Codex/OpenSpec workflow runs `brownfield-complexity-gate`.

For a materially UI-affecting Change, the governed workflow is:

```text
planning
→ brownfield-ui-preflight
→ brownfield-complexity-gate
→ apply
→ project verification
→ browser-verification
→ native Impeccable critique
→ brownfield-ui-conformance
→ final OpenSpec verification
→ incremental brownfield-map maintenance
→ archive/spec synchronization
→ roadmap reconciliation
```

`brownfield-ui-context` is setup and reconciliation, not a gate. It is used
only when an applicable UI review needs missing or materially stale
`PRODUCT.md`; non-UI work does not require `PRODUCT.md` or Impeccable
readiness. Impeccable remains the external native UX workflow provider, and
`browser-verification` remains the external browser-evidence provider.

`PASS` continues normal apply. `REVISE` requires reconciliation of planning
before application-code changes and then reruns the gate. This is mandatory
agent guidance, not a mechanical hook.

After every verified OpenSpec Change and before archive,
`openspec/system/brownfield-map.md` receives incremental maintenance: add
AS-IS architecture introduced by the implemented Change, and remove or replace
AS-IS architecture it superseded. Check the resulting map for internal
architectural consistency. If it is consistent, no routine full
repository/code rescan is required. If it contains a contradiction, inspect
only repository evidence relevant to that contradiction, resolve the map, and
recheck consistency.

Full brownfield discovery/reconstruction remains separate for bootstrap,
missing or stale baselines, or a deliberate full refresh; it is not run after
every Change. After archive, `cross-change-roadmap` consumes the already
maintained baseline to reconcile downstream planning; it does not update or
validate the map.

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
