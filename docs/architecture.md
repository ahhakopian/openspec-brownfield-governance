# Architecture

This package is an overlay rather than an OpenSpec fork.

```text
OpenSpec-owned lifecycle and openspec-* skills
                    +
seven distribution-owned brownfield skills
                    +
additive project configuration
                    |
                    v
target-project-owned persistent knowledge
```

The overlay does not define an OpenSpec schema or lifecycle engine. It validates
that the target selects `spec-driven`, installs non-`openspec-*` skills, and
merges advisory context and rules into the target configuration.

## Installed state

- Skills: `.agents/skills/{brownfield-map,product-boundaries,cross-change-roadmap,brownfield-complexity-gate,brownfield-ui-context,brownfield-ui-preflight,brownfield-ui-conformance}/SKILL.md`
- Receipt: `.openspec-brownfield-governance/receipt.json`
- Optional structural index: `openspec/deferred-changes/README.md`
- Config additions: merged into the existing `openspec/config.yaml`

`brownfield-complexity-gate` is a read-only semantic preflight in the governed
Codex/OpenSpec apply workflow. Its PASS/REVISE guidance is advisory agent
workflow integration, not an OpenSpec hook or lifecycle engine.

The UI skills add applicability and lifecycle governance, not an Impeccable or
browser adapter. `brownfield-ui-context` reconciles auxiliary `PRODUCT.md`
context only when an applicable UI review needs it. `brownfield-ui-preflight`
and `brownfield-ui-conformance` issue PASS/REVISE governance around native
Impeccable UX workflows and external `browser-verification` evidence.
`PRODUCT.md` never overrides Approved product intent, OpenSpec behavior, or
repository/test/brownfield-map AS-IS facts.

The receipt contains governance strings and installation metadata only, never
project knowledge.

Receipt inventories are restricted to known versioned paths and hashes and
carry an integrity checksum for accidental corruption detection. The checksum
is not a cryptographic authentication boundary against a user deliberately
rewriting both a receipt and its checksum.

## Safety

All conflicts are detected before writes. Writes use sibling temporary files
and atomic replacement where the platform permits it. Unknown skill contents,
ambiguous partial context, unsupported schema, and unsupported YAML merge shapes
cause a diagnostic without mutation.
