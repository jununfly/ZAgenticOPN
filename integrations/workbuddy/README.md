# WorkBuddy Agent Integration

This is a one-time, host-level WorkBuddy integration for ZAgenticOPN. It is
owned by ZAgenticOPN and is deliberately outside consuming project
`AGENTS.md` files.

Install this directory as a WorkBuddy/CodeBuddy local plugin, then configure
the host-level runtime with one JSON-Call:

```sh
printf '%s\n' '{"schema_version":"zagenticopn.runtime-config.v1","shared_store_path":"/absolute/path/.zagenticopn/shared.sqlite3","scope_bindings":[{"workspace_root":"/absolute/path/to/consumer-repo","scope":"owner/repo/initiative-or-project"}]}' \
  | python -m zagentic_opn.runtime_config configure
```

The configuration is stored through the host's user config directory as
`zagenticopn/runtime.json`. Set `ZAGENTICOPN_RUNTIME_CONFIG` only when the host
needs an explicit config-file override or a test fixture. The runner reloads
the file on every activation, so an atomic configure/repair takes effect on the
next request. A missing or unusable store fails closed as
`invalid_runtime_config`; it is not created or replaced automatically.

The hook uses the fixed alias `检查 shared context`, resolves it to the
versioned intent `zagenticopn.activation.check_shared_context.v1`, and invokes
`python -m zagentic_opn.activation_runner` with no Work Item id or local path
in the request. The host supplies `scope` explicitly through
`ZAGENTICOPN_SCOPE`, or resolves the WorkBuddy event `cwd` through the
host-level `scope_bindings` list (the most-specific workspace root wins). A
claimed receipt is converted into handoff context for the same model request;
an unbound workspace returns `scope_unbound` and does not call the runner.
There is no default scope, Git-remote inference, Work Item lookup, or
cross-scope search.

The hook defaults to `workbuddy-01` on `device-a` with the Experience Version
profile. Override `ZAGENTICOPN_AGENT_ID`, `ZAGENTICOPN_DEVICE_ID`,
`ZAGENTICOPN_CAPABILITIES`, and `ZAGENTICOPN_PERMISSIONS` in the host
environment when the fixed profile changes.

This integration is not automatic discovery, polling, recovery, or project
maintenance. The Human still submits the activation in WorkBuddy. The host
must declare `pre_model_handoff_injection`; unsupported hosts are rejected
before claim. Scope bindings are host configuration, so consuming project
`AGENTS.md` files and source trees remain untouched.
