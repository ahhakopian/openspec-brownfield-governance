---
name: product-boundaries
description: Reconstruct and define the product-level model and durable boundaries of an existing brownfield product: actors and roles, product capabilities, user/admin/internal surfaces, access and ownership, information architecture, major journeys, explicit UI/UX decisions, and cross-cutting product constraints. Use after brownfield discovery, during migration to OpenSpec, or whenever role separation, product surfaces, access boundaries, UX structure, ownership, or product rules are unclear or being redesigned. Do not use this skill to choose APIs, services, databases, deployment topology, frameworks, or implementation details.
---

# Product Boundaries

Reconstruct the current product model and, when required, define a coherent target product model that future OpenSpec changes can evolve explicitly.

This skill operates between brownfield system discovery and change-specific OpenSpec planning.

It defines:

- who uses the product;
- which roles materially differ;
- which Product Capabilities exist;
- which capabilities belong to which actors and roles;
- which Product Surfaces exist or should exist;
- how user, administrative, internal, and integration responsibilities should be separated;
- how information and capabilities should be organized;
- which important UI/UX decisions should be explicit;
- who owns product data, configuration, policy, and lifecycle;
- which durable Product Boundaries future changes should preserve.

It does not design technical architecture or implementation.

## Relationship to brownfield-map

When available, read the brownfield system map first.

Keep these responsibilities separate:

```text
brownfield-map
=
what system exists now and how it works

product-boundaries
=
what product actors perceive,
how responsibilities should be divided,
and which product rules should constrain future changes
```

The brownfield map is evidence about AS-IS.

It is not automatically the desired TARGET product model.

If no brownfield map exists, reconstruct the necessary current product behavior directly from available documentation, UI, routes, specifications, tests, configuration, and implementation.

## Inputs

Read when available:

- `docs/architecture/as-is.md`
- canonical PRD or product requirements
- existing product documentation
- current UI, routes, navigation, menus, and settings
- current OpenSpec main specs
- active OpenSpec changes when relevant
- historical specification artifacts
- contracts and data models
- relevant implementation code
- relevant tests
- relevant configuration
- existing role, access, or UX documentation

Treat all sources as evidence.

Do not assume:

```text
current implementation = correct target product model
historical specification = current intended model
current screen = correct Product Surface
implementation role = necessary product role
```

Reconcile evidence and expose material conflicts.

## Outputs

Create or update:

- `docs/product/product-model.md`
- `docs/product/access-model.md`
- `docs/product/product-boundaries.md`

On first creation set:

```text
Status: Proposed
```

Do not change a document or product decision to `Approved` without explicit human approval.

Invocation of this skill authorizes creation or update of these three product documents only.

Do not modify:

- implementation code;
- OpenSpec changes or specs;
- technical architecture documents;
- the brownfield map.

If the brownfield map appears stale or incorrect, report the discrepancy instead of silently changing it.

# Core concepts

## Actor

A type of person or external system interacting with the product.

## Role

A materially different responsibility or privilege set.

Do not create roles merely because implementation contains different labels.

Do not assume that every product needs administrators, tenants, operators, accounts, or organizations.

## Product Capability

Something an actor can meaningfully accomplish.

Define capabilities independently of screens, routes, endpoints, components, services, or historical feature numbers.

A Product Capability should survive reasonable UI and technical redesign.

Do not automatically equate a Product Capability with an OpenSpec capability.

## Product Surface

A coherent interface through which actors access related Product Capabilities.

A Product Surface is a product concept.

It does not imply a separate application, frontend, backend, service, repository, or deployment unit.

## Permission

Defines:

```text
WHO may do WHAT to WHICH RESOURCE
```

Keep permission separate from UI visibility and technical reachability.

## Authority

Defines who or what owns an authoritative product decision or state.

Authority is not the same as permission.

## UI/UX Decision

A deliberate product-level decision about how capabilities, responsibilities, state, or actions are exposed and understood.

Do not use this concept for colors, typography, spacing, CSS, component libraries, or pixel layouts.

## Product Boundary

A durable cross-cutting rule constraining product scope, responsibility, authority, access, information flow, consent, lifecycle, trust, evidence, compatibility, or capability interaction.

Do not promote incidental implementation details into Product Boundaries.

# Stable identifiers

Use stable identifiers:

```text
ACT-###   Actor
ROLE-###  Role
PCAP-###  Product Capability
SURF-###  Product Surface
UX-###    Significant UI/UX decision
PB-###    Product Boundary
```

Do not renumber existing identifiers.

These IDs allow future OpenSpec changes to refer to existing product decisions explicitly.

# Workflow

## Step 1 — Determine mode

Use one of:

```text
RECONSTRUCT
```

or:

```text
RECONSTRUCT + REDESIGN
```

Use RECONSTRUCT when only the current product must be documented.

Use RECONSTRUCT + REDESIGN when responsibilities, roles, Product Surfaces, access, information architecture, UI/UX, or product boundaries need to be made explicit or changed.

When redesigning, keep AS-IS and TARGET strictly separate.

## Step 2 — Establish source authority

Determine which sources are useful for which questions.

Prefer:

- canonical product requirements and approved decisions for product intent;
- current implementation, UI, routes, configuration, and executable tests for current behavior;
- current normative specifications and contracts for detailed intended behavior;
- historical plans, tasks, and research for rationale and historical evidence.

Do not create one universal precedence rule when different sources answer different questions.

When evidence conflicts, record the conflict.

Do not silently choose implementation over intent or intent over verified current behavior.

## Step 3 — Reconstruct AS-IS

Determine:

- current actors and roles;
- current Product Capabilities;
- current Product Surfaces;
- current navigation and information architecture;
- current settings and administrative areas;
- current privileged actions;
- current ownership and resource scopes;
- current user, administrative, internal, and integration journeys;
- significant current UI/UX decisions;
- responsibilities currently mixed across roles or surfaces.

Record observations separately from TARGET proposals.

## Step 4 — Define actors and roles

Create the smallest actor and role model that explains materially different:

- goals;
- responsibilities;
- privilege levels;
- resource scopes;
- product experiences.

For every actor or role define:

- purpose;
- primary goals;
- responsibilities;
- scope of control;
- relevant Product Capabilities.

Avoid unnecessary role proliferation.

Do not preserve accidental implementation roles.

Do not invent administrator or operator roles when the product does not need them.

## Step 5 — Define Product Capabilities

For every significant Product Capability define:

- ID;
- name;
- actor value;
- owning product domain;
- relevant actors and roles;
- resource scope;
- current availability;
- target availability;
- whether it is user-facing, administrative, internal, integration-oriented, or shared;
- relevant legacy/OpenSpec mapping when available.

Product Capabilities must be independent of current screens and technical components.

## Step 6 — Map existing feature decomposition

When historical features or OpenSpec capabilities exist, map them to Product Capabilities.

Do not assume one-to-one correspondence.

One Product Capability may span several existing features.

One existing feature may contain several Product Capabilities.

Use the mapping for traceability, not to preserve historical decomposition forever.

## Step 7 — Define TARGET responsibility separation

When redesign is in scope, determine how responsibilities should be divided in the target product.

Evaluate where relevant:

- ordinary-user responsibilities;
- personal settings;
- administrative configuration;
- tenant or organization administration;
- internal operations;
- support responsibilities;
- integration responsibilities;
- deployment-controlled configuration;
- system-owned or derived state.

For every proposed separation explain:

- AS-IS problem;
- actors affected;
- capabilities affected;
- target responsibility;
- rationale;
- what remains shared.

Do not decide technical deployment topology.

## Step 8 — Define Product Surfaces

For each current and target Product Surface define:

- ID;
- purpose;
- intended actors and roles;
- Product Capabilities;
- information presented;
- primary actions;
- privilege level;
- resource scope;
- entry points;
- relationship to other Product Surfaces;
- AS-IS or TARGET status.

Explicitly determine whether materially different user, administrative, internal, or integration responsibilities require separate Product Surfaces.

Do not assume that separate Product Surfaces require separate applications or services.

## Step 9 — Define Information Architecture

For relevant TARGET human-facing surfaces define:

- top-level areas;
- primary navigation;
- capability grouping;
- information hierarchy;
- primary and secondary actions;
- entry and exit points;
- relationships between areas;
- information or responsibility scopes that must remain separate.

Focus on product structure, not visual styling.

## Step 10 — Make important UI/UX decisions explicit

Create stable `UX-###` decisions for product-significant UI or UX behavior.

A significant UI/UX decision should affect at least one of:

- actor responsibility;
- capability discoverability;
- responsibility separation;
- information hierarchy;
- state interpretation;
- privilege understanding;
- onboarding;
- consent;
- destructive actions;
- scope selection;
- error/recovery behavior;
- major journey completion.

For each decision define:

- ID;
- affected actor or role;
- Product Surface;
- decision;
- rationale;
- AS-IS state;
- TARGET state;
- affected Product Capabilities.

Do not specify implementation components or visual styling.

## Step 11 — Define major journeys

Document only journeys needed to validate product structure.

For each important actor or role:

```text
Goal
→ Entry
→ Major steps
→ Decision points
→ Completion
```

Keep materially different user, administrative, internal, and integration journeys separate.

A normal user journey must not silently depend on administrative actions unless that is an explicit product requirement.

## Step 12 — Build Access Model

For each significant Product Capability define:

- actor or role;
- permission;
- resource scope;
- restrictions;
- administrative or delegation scope;
- ownership when relevant.

Use explicit values:

```text
Allow
Deny
Conditional
Not Applicable
```

For `Conditional`, state the condition.

Do not use blank cells to imply permission.

Keep separate:

```text
CAN SEE
CAN EXECUTE
OWNS
CAN ADMINISTER FOR OTHERS
CAN CHANGE POLICY
```

Never equate UI visibility with authorization.

Do not design an authorization implementation.

If the product has no meaningful role differentiation, keep the access model minimal and state that explicitly.

## Step 13 — Define ownership and authority

For important product data, configuration, policy, or lifecycle determine:

- who may create it;
- who may change it;
- who may read it;
- who owns the authoritative state;
- resource scope;
- whether it is personal, shared, administrative, deployment-controlled, external, system-owned, or derived.

Pay particular attention to accidental mixing of:

```text
user preference
administrator configuration
system policy
derived state
deployment configuration
external-system state
```

## Step 14 — Identify durable Product Boundaries

Identify cross-cutting rules future changes should normally preserve.

Relevant categories may include:

- Product Scope
- Responsibility Separation
- Authority and Ownership
- Access
- Configuration Ownership
- Privacy and Information Flow
- Consent
- Lifecycle and Deletion
- Capability Optionality and Failure Isolation
- Evidence Semantics
- Trust
- External Integration
- Compatibility and Evolution
- Experience Separation

Use only categories relevant to the product.

For every Product Boundary define:

- PB-ID;
- name;
- category;
- precise normative statement;
- rationale;
- affected actors and roles;
- affected Product Capabilities;
- affected Product Surfaces;
- authority or owner where relevant;
- current state;
- target rule;
- evidence;
- known gaps;
- change rule.

Do not make a Product Boundary merely because something is currently implemented a certain way.

## Step 15 — Separate current behavior from target policy

For important decisions determine independently:

```text
What does the product currently do?
```

and:

```text
What should the target product do?
```

Use status values where useful:

```text
Aligned
Partial
Violated
Unverified
Conflicted
Not Yet Implemented
```

Do not silently change target policy to match implementation.

Do not label implementation defective solely because historical documentation differs.

## Step 16 — Build AS-IS → TARGET gap map

For each material gap define:

- AS-IS condition;
- TARGET condition;
- affected actors and roles;
- affected Product Capabilities;
- affected Product Surfaces;
- access impact;
- UI/UX impact;
- affected Product Boundaries;
- unresolved decisions.

Do not convert product gaps into technical implementation tasks.

They are inputs to later OpenSpec changes.

## Step 17 — Record unresolved decisions

Do not guess high-impact product policy.

For every unresolved material decision record:

- question;
- affected IDs;
- why it matters;
- available evidence;
- realistic alternatives;
- recommended option when evidence supports one;
- consequence of each option;
- whether human approval is required before TARGET approval.

Keep the product model `Proposed` while blocking product decisions remain unresolved.

# Product evolution policy

Approved product decisions are presumed stable.

Future changes should first attempt to fit within existing Approved:

- roles;
- Product Capabilities;
- Product Surfaces;
- access rules;
- significant UX decisions;
- Product Boundaries.

If a new requirement conflicts with an Approved decision:

1. identify the affected stable IDs;
2. explain the conflict;
3. examine reasonable alternatives that preserve the existing decision;
4. prefer a compatible solution when one exists;
5. do not rewrite earlier product decisions merely because implementation would be easier;
6. if no reasonable compatible solution exists, propose the product-model amendment explicitly;
7. describe affected actors, capabilities, surfaces, access, UX, boundaries, and existing behavior;
8. obtain explicit human approval before changing the Approved decision.

This is a strong presumption against casual backward rewriting, not a prohibition on deliberate product evolution.

Keep OpenSpec change-artifact reconciliation separate from product-model evolution.

# Technical boundary

This skill MAY decide:

```text
Users and administrators require distinct Product Surfaces.
```

It MAY decide:

```text
Administrative policy must be separate from personal settings.
```

It MAY decide:

```text
The ordinary user journey must not require administrative access.
```

It MUST NOT decide:

```text
Create separate frontend applications.
Create an admin API.
Split the backend into services.
Use a particular RBAC library.
Use a particular database.
Use a particular framework.
Choose a deployment topology.
```

Those decisions belong to OpenSpec design.

# Required output: product-model.md

Write `docs/product/product-model.md` with:

```markdown
# Product Model

Status: Proposed | Approved

## Purpose

## Scope

## Evidence and Source Authority

## AS-IS Product

### Current Actors and Roles
### Current Product Capabilities
### Current Product Surfaces
### Current Information Architecture
### Current Major Journeys
### Current Responsibility Mixing

## TARGET Product Model

### Actors
### Roles
### Product Capabilities
### Capability Ownership
### Product Surfaces
### Surface-to-Role Mapping
### Information Architecture
### Navigation Model
### Important UI/UX Decisions
### Primary User Journeys
### Administrative / Internal Journeys
### Integration Journeys

## Legacy / OpenSpec Capability Mapping

## AS-IS → TARGET Gap Map

## Open Decisions

## Evidence and Rationale
```

# Required output: access-model.md

Write `docs/product/access-model.md` with:

```markdown
# Access Model

Status: Proposed | Approved

## Principles

## Actors and Roles

## Product Capability Matrix

## Resource Scope Rules

## Configuration and Policy Ownership

## Administrative Scope

## Delegation Rules

## Visibility vs Permission

## Explicit Denials

## Open Decisions

## Evidence and Rationale
```

# Required output: product-boundaries.md

Write `docs/product/product-boundaries.md` with:

```markdown
# Product Boundaries

Status: Proposed | Approved

## Purpose

## Scope

## Boundary Registry

| ID | Boundary | Category | Policy Status | Current State | Applies To |
|---|---|---|---|---|---|

## Boundary Definitions

## Current Boundary Violations

## Product-Model Ambiguities

## Open Decisions

## Product Evolution Policy

## Evidence Limitations
```

Each boundary definition must contain:

- ID and name;
- category;
- policy status;
- current state;
- statement;
- rationale;
- affected actors/roles;
- affected Product Capabilities;
- affected Product Surfaces;
- authority/owner where relevant;
- current behavior;
- target rule;
- evidence;
- known gaps;
- change rule.

# Approval rules

New documents and newly reconstructed decisions start as:

```text
Proposed
```

Do not infer approval from:

- current implementation;
- historical specifications;
- completed tasks;
- tests;
- silence.

Only explicit human approval establishes `Approved`.

Preserve existing Approved decisions unless explicit approval authorizes amendment or deprecation.

# Completion criteria

Before finishing verify that:

- AS-IS and TARGET are clearly separated;
- current implementation was not automatically treated as target design;
- actors and materially necessary roles are explicit;
- Product Capabilities are independent of screens and technical modules;
- current and target Product Surfaces are explicit;
- user/admin/internal responsibilities are separated where materially different;
- Product Surface is not equated with deployment topology;
- capability, configuration, and policy ownership are explicit;
- access rules are explicit;
- visibility is not treated as authorization;
- Information Architecture and navigation are explicit where relevant;
- significant UI/UX decisions have stable IDs;
- major journeys validate the proposed structure;
- durable Product Boundaries have stable IDs;
- incidental technical details were not promoted into Product Boundaries;
- legacy/OpenSpec mapping exists where relevant;
- AS-IS → TARGET gaps are explicit;
- unresolved product-policy questions remain visible;
- existing Approved decisions were not silently rewritten;
- no technical architecture or implementation was designed;
- no implementation code or OpenSpec change artifacts were modified.

# Final response

Report:

- files created or updated;
- AS-IS product structure discovered;
- TARGET product structure proposed;
- actor and role changes;
- Product Capability changes;
- Product Surface changes;
- user/admin/internal responsibility separation;
- major access and ownership decisions;
- significant UI/UX decisions;
- Product Boundaries identified;
- AS-IS → TARGET gaps;
- unresolved decisions requiring human approval;
- whether any existing Approved product decision requires amendment;
- confirmation that no implementation code or OpenSpec change artifacts were modified.
