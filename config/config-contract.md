# Brownfield Config Contract

`brownfield-config.yaml` is an additive merge declaration, not an OpenSpec
configuration replacement.

- `required_schema` is validated and never written.
- `context_append` is appended once to an existing literal-block `context`.
- `rules_append` entries are merged by exact scalar identity.
- `operations_append` guidance is merged by exact scalar identity.
- Unrelated YAML text, comments, ordering, context, rules, operations, and
  supported top-level fields remain untouched.

The bootstrapper uses a conservative block-style YAML editor implemented with
the Python standard library. It fails before writing when it encounters an
inline/flow-style node at a merge location or a partial brownfield context
fingerprint that cannot be attributed safely.

The installation receipt distinguishes clauses already present before
installation from clauses inserted by the distribution. Uninstall removes only
unchanged inserted clauses.
