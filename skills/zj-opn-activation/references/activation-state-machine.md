# Activation routing state machine

```mermaid
stateDiagram-v2
    [*] --> AliasResolution
    AliasResolution --> PassThrough: no exact alias
    AliasResolution --> ScopeResolution: exact alias → intent_id
    ScopeResolution --> ScopeUnbound: no explicit scope or host binding
    ScopeResolution --> InvalidRuntimeConfig: host binding config invalid
    ScopeResolution --> JsonCall: explicit scope or workspace binding
    JsonCall --> InvalidContract: schema/profile/capability invalid
    JsonCall --> RuntimeLoad: valid JSON-Call
    RuntimeLoad --> InvalidRuntimeConfig: config missing/invalid/store unusable
    RuntimeLoad --> HostCheck: valid host runtime config
    HostCheck --> UnsupportedHost: missing pre_model_handoff_injection
    HostCheck --> Discover: capability accepted
    Discover --> NoEligibleWork: empty frontier
    Discover --> Claim: eligible frontier
    Claim --> ClaimConflict: atomic claim loses or conflicts
    Claim --> Claimed: one execution/review claim succeeds
    Claimed --> HandoffDelivery
    HandoffDelivery --> HandoffDeliveryFailed: host cannot inject handoff
    HandoffDelivery --> AgentContinuation: handoff injected
    AgentContinuation --> CoordinationLifecycle: execute/review via coordination seam
    PassThrough --> [*]
    ScopeUnbound --> [*]
    InvalidContract --> [*]
    InvalidRuntimeConfig --> [*]
    UnsupportedHost --> [*]
    NoEligibleWork --> [*]
    ClaimConflict --> [*]
    HandoffDeliveryFailed --> [*]
    CoordinationLifecycle --> [*]
```

## Current intent of this document

This diagram is for maintaining activation behavior: alias resolution,
JSON-Call validation, runtime loading, discover, claim, receipt, and host
handoff. It does not replicate the product's entire lifecycle, and the diagram
does not replace the shared store's runtime facts. Execution, result
publication, review, reopen, and completion continue to use the coordination
seam and its receipts/events.

## Observable contract points

- Every call that enters the runner returns one structured receipt.
- `invalid_contract`, `invalid_runtime_config`, `scope_unbound`, and `unsupported_host` are
  rejection outcomes; when possible they write `activation_rejected`.
- `claimed` includes `handoff`, `work_id`, `next_action`, and `evidence`.
- A host delivery failure is recorded after claim as
  `handoff_delivery_failed`; it is not hidden by retry or cross-scope recovery.
- `config_updated_at` and `config_loaded_at` are UTC diagnostic timestamps in
  `YYYYMMDDHHMMSS[.SSS]Z` format.
