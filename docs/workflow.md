# Workflow

The package preserves the ordinary OpenSpec lifecycle:

```text
OpenSpec propose
-> human review
-> OpenSpec apply
-> implementation verification
-> refresh brownfield map when materially affected
-> OpenSpec archive
-> refresh cross-change roadmap
-> commit
```

`brownfield-map` maintains descriptive AS-IS evidence.
`product-boundaries` reconstructs or explicitly governs the product model and
does not create a parallel change lifecycle. `cross-change-roadmap` sequences
candidate changes without creating or authorizing them.

Deferred artifacts remain prior evidence rather than current requirements or
implementation authorization.
