"""Dispatch the installed runtime CLI and host activation entrypoint."""

from .cli import main


def _main() -> int:
    import sys

    if sys.argv[1:2] == ["host-activate"]:
        from .host_activation import main as host_activation_main

        sys.argv.pop(1)
        return host_activation_main()
    if sys.argv[1:2] == ["runtime-config"]:
        from .runtime_config import main as runtime_config_main

        sys.argv.pop(1)
        return runtime_config_main()
    if sys.argv[1:2] == ["--version"]:
        from .release_info import PRODUCT_VERSION

        print(PRODUCT_VERSION)
        return 0
    return main()


if __name__ == "__main__":
    raise SystemExit(_main())
