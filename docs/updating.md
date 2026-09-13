# Updating and Uninstalling

## Update

```bash
python3 bootstrap/openspec-brownfield.py update --target /path/to/project
```

Update changes only distribution-owned skills, config clauses, and receipt
metadata. A skill whose current hash differs from the receipt is treated as a
local modification and is not overwritten.

The receipt stores a versioned semantic snapshot of the installed config
contract. A later package can remove unchanged clauses owned by a known
previous contract before merging its replacement. Unknown contract hashes fail
safely instead of being migrated.

Maps, product documents, access models, PRDs, roadmaps, specs, changes,
archives, and deferred records are never updated.

## Uninstall

```bash
python3 bootstrap/openspec-brownfield.py uninstall --target /path/to/project
```

Uninstall removes only skills and config clauses recorded as inserted and still
safe to remove. Pre-existing clauses remain. A locally modified skill blocks
uninstall before any writes.

An unchanged empty deferred-change index created by installation is removed. If
the index was edited, it remains as project knowledge. The receipt is removed
only after the operation completes.

The command never touches OpenSpec-owned `openspec-*` skills or target-project
knowledge.
