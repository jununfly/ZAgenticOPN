"""Allow ``python -m zagentic_opn`` to invoke the coordination CLI."""

from .cli import main

raise SystemExit(main())
