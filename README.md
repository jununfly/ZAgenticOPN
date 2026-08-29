# ZAgenticOPN

ZAgenticOPN is the coordination control plane for Human-triggered,
self-service collaboration among heterogeneous Agents. It owns the shared
coordination facts and lifecycle of a Work Item; a consuming project remains
the Agent's task workspace and Git artifact.

The product is currently in **Experience Version**. The supported product slice
is **same device, single project, multiple Agents, owner-only private dogfood**.
The current formal delivery is a user-side release: a host-level plugin calls
an installed runtime. A consuming project must not import this checkout, add it
to `PYTHONPATH`, or store the product SQLite database.

## Agent operating contract

### Activation

The only Human-facing activation alias is the exact text:

```text
检查 shared context
```

Treat it as a trigger, not as task context. The host resolves it to the
versioned intent `zagenticopn.activation.check_shared_context.v1` and sends one
strict JSON request to the installed runtime. The request must contain:

```json
{
  "schema_version": "zagenticopn.activation.v1",
  "intent_id": "zagenticopn.activation.check_shared_context.v1",
  "activation_id": "fresh-id-for-this-session",
  "scope": "owner/repo/project",
  "agent_profile": {
    "agent_id": "stable-agent-id",
    "device_id": "stable-device-id",
    "capabilities": ["technical-writing"],
    "permissions": ["zagentic-skill-write"],
    "can_review": false
  },
  "host_capabilities": ["pre_model_handoff_injection"]
}
```

The request never contains a Work Item id or a local database path. `scope`
must be explicit: the WorkBuddy adapter may resolve it only from the installed
user-level workspace binding. It must not infer scope from cwd, Git remote,
project files, or a Work Item.

The runtime performs exactly one discover and at most one claim. Do not poll,
retry, guess a Work Item id, search another scope, or create replacement work
when one activation returns no work.

### Receipt handling

Use the receipt as the runtime fact and follow its `next_action` or
`repair_action`:

| Receipt | Agent action |
|---|---|
| `claimed` | Use the complete handoff, execute the objective in the current consumer workspace, and publish a result. |
| `no_eligible_work` | Report the status and filtering reason; do not invent or request a specific Work Item. |
| `claim_conflict` | Report the conflict; do not retry the claim inside the same activation. |
| `scope_unbound` | Stop and ask Human to add or correct the explicit host binding. |
| `unsupported_host` | Stop because the host cannot guarantee handoff injection. |
| `invalid_contract` | Repair the host request shape; do not claim work. |
| `invalid_runtime_config` | Repair the user-level runtime configuration; do not guess a store or scope. |
| `handoff_delivery_failed` | Report that the claim was recorded but handoff delivery failed; Human decides whether to reopen. |

Only a `claimed` receipt authorizes execution. A claimed handoff contains the
Work Item objective, acceptance, state, next action, references, scope and id.
Treat it as the shared context supplied for this execution; do not ask Human to
repeat the task-specific context.

### Execution and result provenance

After a successful claim:

1. Work in the consuming project workspace selected by the host.
2. Satisfy the handoff's acceptance criteria.
3. Keep Git as the canonical source for engineering facts.
4. Publish a structured result containing `result_summary`, `next_action`,
   `acceptance_status` and references.
5. Each Git reference must identify the commit SHA, changed files, test
   command and test result; add branch or diff state when relevant.

The shared store keeps structured work facts, events and Git references. It is
not a transcript store, code mirror or general-purpose Agent memory.

A reviewer activates from the same shared scope, discovers the
`awaiting_agent_review` item, atomically claims review, verifies the Git
references and submits `accept`, `request_changes` or `escalate`. A
`request_changes` result returns the item to `available` with the review reason;
the next Agent must activate again and claim it. Human handles direction,
permissions, conflicts and explicit reopen decisions.

## Product and deployment boundary

A formal release is a versioned, immutable bundle containing:

- the stdlib-based runtime zipapp;
- the stable `bin/zagenticopn` launcher;
- the matching WorkBuddy/CodeBuddy host integration and hook;
- the top-level `Install.command` entrypoint;
- the top-level `Uninstall.command` entrypoint;
- `manifest.json`, checksums and contract versions;
- advanced install, uninstall, doctor and rollback tooling.

The installed user-side layout on macOS is:

```text
~/Library/Application Support/zagenticopn/
├── versions/<release-id>/       # immutable runtime and host integration
├── current                     # atomically selected release
├── runtime.json                # user config and explicit workspace bindings
├── data/shared.sqlite3         # shared coordination context and events
├── backups/                    # pre-upgrade user-state copies
├── logs/                       # local diagnostics
└── install-manifest.json       # installed release and host registration record
```

The WorkBuddy hook is only a standard-library bridge. It invokes
`current/bin/zagenticopn host-activate`, removes source-import environment
variables, and injects handoff context only when the installed runtime returns
`claimed`. The runtime is short-lived and local; the current product does not
run a daemon or remote coordination service.

## 安装与卸载（给其他 Agent 的操作契约）

This section describes the current user-side product path. An Agent may inspect
and diagnose the installation, but must not silently install a host plugin,
disable another release, or delete user data. Installation changes host state
and needs explicit Human authorization; uninstall always requires Human
confirmation of data retention.

### Install the formal product

The supported target is macOS with an installed WorkBuddy or CodeBuddy host.
Use an extracted **release bundle**, not the repository checkout. The release
root contains `Install.command` beside `install_release.py`.

Preferred first setup:

```sh
./Install.command \
  --workspace-root "/absolute/path/to/consumer-repo" \
  --scope "owner/repo/project"
```

The entrypoint performs the following setup flow:

1. Verifies the release manifest and every declared file checksum.
2. Detects the installed WorkBuddy/CodeBuddy CLI and Node runtime.
3. Installs the matching plugin through the host's user-scope CLI.
4. Disables other enabled `zagenticopn-agent-integration@*` plugins so two
   releases cannot run duplicate hooks.
5. Creates the user product directories and an empty `runtime.json` when this
   is the first installation.
6. Writes the explicit workspace-to-scope binding supplied to the command.
7. Runs `doctor` and reports the active release and host registration.

The installer does not edit a consuming project, load project Python, modify
`AGENTS.md`, use `PYTHONPATH`, infer a scope, or create a default scope. The
first supported setup contains one explicit project binding even though the
configuration format can represent more; multi-project use is not a current
product promise.

If installation and project binding must be separated, use:

```sh
./Install.command --non-interactive
```

This creates a healthy installation with an empty binding list and returns
`awaiting_workspace_binding`. Do not activate a consuming project until a
Human or authorized setup flow has added its absolute `workspace_root` and
`CollaborationScope`. The binding can be configured through the installed
launcher with the runtime config contract:

```sh
printf '%s\n' '{"schema_version":"zagenticopn.runtime-config.v1","shared_store_path":"/Users/<user>/Library/Application Support/zagenticopn/data/shared.sqlite3","scope_bindings":[{"workspace_root":"/absolute/path/to/consumer-repo","scope":"owner/repo/project"}]}' \
  | "$HOME/Library/Application Support/zagenticopn/current/bin/zagenticopn" runtime-config configure
```

The current `Install.command` still requires Python 3.9 or newer on the user
machine. It checks this prerequisite and reports a repair action. The runtime
packaging may later become a self-contained executable; that would not change
the host/runtime/configuration contract.

### Inspect, upgrade and rollback

Use the release-local installer for read-only health checks and explicit
version changes. Host CLI and config options can be omitted from the one-step
entrypoint because it auto-detects them; advanced commands accept explicit
overrides when automation needs them:

```sh
python3 install_release.py doctor \
  --product-root "$HOME/Library/Application Support/zagenticopn" \
  --host-cli /Applications/WorkBuddy.app/Contents/Resources/app.asar.unpacked/cli/dist/codebuddy.js \
  --host-config-dir "$HOME/.workbuddy" \
  --host-cli-node /opt/homebrew/bin/node

python3 install_release.py rollback \
  --product-root "$HOME/Library/Application Support/zagenticopn" \
  --host-cli /Applications/WorkBuddy.app/Contents/Resources/app.asar.unpacked/cli/dist/codebuddy.js \
  --host-config-dir "$HOME/.workbuddy" \
  --host-cli-node /opt/homebrew/bin/node \
  --to 0.1.0-rc.3
```

Rollback switches the runtime, host plugin and `current` pointer as one
versioned pair. Upgrade or rollback must be followed by `doctor` and a minimal
activation smoke. Do not switch only the hook, only the runtime, or only the
host plugin.

### Uninstall boundary

The paired `Uninstall.command` is the preferred exit path. It requires a
Human confirmation and removes only the installed releases identified by the
product root's `install-manifest.json` and each version manifest. For every
release it first disables and uninstalls the matching user-scope plugin through
the official host CLI, then removes that release's marketplace registration.
It never edits host registry files directly.

To remove the product and its local data:

```sh
./Uninstall.command
```

To remove installed runtime/plugin payloads while retaining `runtime.json`,
`data/shared.sqlite3`, `backups` and `logs`:

```sh
./Uninstall.command --keep-data
```

The underlying advanced command is:

```sh
python3 install_release.py uninstall --yes
```

Without `--yes`, the underlying command is a read-only confirmation preview.
The command fails closed when the install marker, current pointer, release
manifests or supported host CLI are missing or inconsistent. An Agent must
not add `--yes` merely to bypass the guard, and must not delete
`~/Library/Application Support/zagenticopn/` directly. The Human must first
decide whether shared context, events, backups and logs should be retained or
exported. The consuming project's source tree, Git history and task artifacts
are never uninstall targets.

## Host adapter requirements

WorkBuddy is the currently verified host. Another Agent host can use the
installed runtime only after implementing an adapter that provides:

- stable `agent_id` and `device_id` for the Agent instance;
- an explicit `scope` or a user-level workspace binding;
- the exact activation intent and fresh `activation_id`;
- `pre_model_handoff_injection` before the model request;
- strict JSON parsing and structured receipt handling;
- no Work Item id, local database path or source checkout in the activation
  request.

An unsupported host must fail closed before claim. A host adapter is a
transport integration, not an owner of scope, eligibility, claims, Work Item
state, result provenance or review semantics.

## Work Item lifecycle

The current coordination state machine is:

```text
available ──claim──> claimed ──result──> awaiting_agent_review ──review──> completed
    │                    │
    ├──cancel──> cancelled
    └───────────────<──── blocked
```

Review must be atomically claimed by a reviewer. A `request_changes` review
returns the work to `available` with the previous result cleared for a clean
retry. A stale execution claim may be reopened only by an explicit Human
operation; there is no claim TTL, automatic recovery, background retry or
cross-scope search.

## Development and verification

The repository checkout is for product development and black-box fixtures. The
canonical source-level verification command is:

```sh
python3 -m unittest discover -s tests -v
```

Release tests build a source-independent bundle, install it into a temporary
user root, exercise the installed hook without source paths, verify host
plugin/runtime pairing and test rollback. A formal install accepts only a
bundle built from a clean commit; `--allow-dirty` is for fixtures only.

To build a release bundle from a clean commit:

```sh
python3 scripts/build_release_candidate.py \
  --version 0.1.0-rc.N \
  --output /absolute/path/to/release-output
```

The generated directory is the release root. Extract it on the target user
machine, then run its top-level `Install.command`.

## Current limits

The current product intentionally does not provide automatic discovery,
background polling, device wake-up, cross-device shared state, multi-project
coordination, public distribution, multi-user access control, daemon/HA,
production SLOs, automatic merge/release, or team governance. Those are
separate deferred plans, not implicit capabilities of this runtime.

Useful references:

- [Product Spec](docs/prds/agent-self-service-collaboration.md)
- [Experience Version Spec](docs/prds/agent-self-service-collaboration-experience-version.md)
- [Coordination seam](docs/experience-version-coordination.md)
- [Roadmap](docs/plans/agent-self-service-collaboration-roadmap.md)
- [User-side deployment review](docs/plans/agent-self-service-collaboration-user-side-deployment-review.md)
- [ZAgenticOPN activation Skill](skills/zj-opn-activation/SKILL.md)
