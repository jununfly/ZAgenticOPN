# ZAgenticOPN

ZAgenticOPN explores Human-triggered, self-service collaboration among heterogeneous AI Agents across devices and projects.

The project is in **Experience Version**. The C-route implementation is authorized for the same-device, single-project vertical slice. The product owner will consume this slice through a user-side formal release; public deployment, production operations, and deferred collaboration capabilities remain out of scope.

Consuming projects are task workspaces only. A released runtime and host integration
must be installed in the user's product directories; production use must not import this
checkout or add it to a consuming project's `PYTHONPATH`. The current source-tree
commands are development/fixture paths until the release candidate is available.

- [Product Spec](docs/prds/agent-self-service-collaboration.md)
- [Experience Version Spec](docs/prds/agent-self-service-collaboration-experience-version.md)
- [Candidate-neutral technical design](docs/designs/agent-self-service-collaboration.md)
- [Roadmap](docs/plans/agent-self-service-collaboration-roadmap.md)
