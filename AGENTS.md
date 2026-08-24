# ZAgenticOPN agent rules

ZAgenticOPN is a new product for Human-triggered, self-service collaboration among heterogeneous Agents across devices and projects.

**Lifecycle gate:** Before planning, designing, developing, validating, maintaining, or closing this product, read the [product lifecycle development and maintenance agreement](https://github.com/jununfly/ZInitiatives/blob/main/docs/agreements/product-lifecycle-development-maintenance-agreement.md), then read [the active Spec](docs/prds/agent-self-service-collaboration.md) and [the roadmap view](docs/plans/agent-self-service-collaboration-roadmap.md). Classify proposed work as `stage-critical`, `observed-failure`, or `deferred` before acting.

The current stage is Experience Version. The open-source comparison gate is complete and Human has authorized the C-route same-device, single-project vertical slice. Product code and black-box fixtures are allowed inside that slice; deployment, production operations, automatic discovery, recovery, and code extraction from ZAgenticLoop remain deferred.

ZAgenticLoop is a legacy project, not a dependency or default source of reusable code. Re-evaluate an individual capability only when current-stage evidence requires it.

The roadmap JSON is its sole source of truth. Modify and render it only with `zj-roadmap-driven`; do not edit the JSON or rendered Markdown directly.

Git repositories remain canonical for code, Specs, Plans, commits, and release facts. ZInitiatives provides navigation only; ZAgenticOPN owns this product's content.

## Task-agnostic Agent activation

When Human says only “检查 shared context”, an Agent working in this repository must enter the product coordination seam instead of treating ZInitiatives navigation as the shared Work Item store. Run one project-local activation with the Agent's stable identity and profile:

```sh
python scripts/activate_agent.py \
  --agent-id <stable-agent-id> \
  --device-id <device-id> \
  --capabilities technical-writing \
  --permissions zagentic-skill-write
```

Do not provide a Work Item id. The command performs one `discover`, claims at most one eligible execution or review item, and prints the structured handoff. Follow the returned Work Item's objective and acceptance; publish results through the coordination CLI. This is an explicit Human-triggered activation seam, not polling, automatic discovery, or a request for Human task selection.
