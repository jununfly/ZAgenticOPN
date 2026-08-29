"""Clean-room tests for the user-side release candidate bundle."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ReleaseCandidateBlackBoxTests(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]
    build_script = root / "scripts" / "build_release_candidate.py"
    install_script = root / "scripts" / "install_release.py"

    def test_clean_room_install_uses_installed_runtime_without_source_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            release_output = root / "release-output"
            product_root = root / "product"
            host_config_dir = root / "host-config"
            host_cli = self._write_host_cli(root / "host-cli.py")
            consumer = root / "consumer"
            consumer.mkdir()

            build = self._run(
                sys.executable,
                str(self.build_script),
                "--version",
                "0.1.0-test.1",
                "--output",
                str(release_output),
            )
            built = json.loads(build.stdout)
            bundle = Path(built["release_dir"])
            manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["release_id"], "0.1.0-test.1")
            self.assertTrue(manifest["source_tree_dirty"])
            self.assertEqual(
                manifest["host_integration"]["marketplace_name"],
                "zagenticopn-release-0.1.0-test.1",
            )
            self.assertTrue(
                (bundle / "host-integration" / ".codebuddy-plugin" / "marketplace.json").is_file()
            )

            installed = self._run(
                sys.executable,
                str(self.install_script),
                "install",
                "--bundle",
                str(bundle),
                "--product-root",
                str(product_root),
                "--host-cli",
                str(host_cli),
                "--host-config-dir",
                str(host_config_dir),
                "--allow-dirty",
            )
            self.assertEqual(json.loads(installed.stdout)["status"], "installed")
            doctor = self._run(
                sys.executable,
                str(self.install_script),
                "doctor",
                "--product-root",
                str(product_root),
                "--host-cli",
                str(host_cli),
                "--host-config-dir",
                str(host_config_dir),
            )
            self.assertEqual(json.loads(doctor.stdout)["status"], "healthy")

            launcher = product_root / "current" / "bin" / "zagenticopn"
            plugin_root = product_root / "current" / "host-integration" / "workbuddy"
            config = product_root / "runtime.json"
            database = product_root / "data" / "shared.sqlite3"
            configure = self._run(
                str(launcher),
                "runtime-config",
                "configure",
                env={
                    "ZAGENTICOPN_RUNTIME_CONFIG": str(config),
                },
                input=json.dumps(
                    {
                        "schema_version": "zagenticopn.runtime-config.v1",
                        "shared_store_path": str(database),
                        "scope_bindings": [
                            {"workspace_root": str(consumer), "scope": "owner/project/release-test"}
                        ],
                    }
                ),
            )
            self.assertEqual(json.loads(configure.stdout)["status"], "configured")
            self._run(
                str(launcher),
                "--db",
                str(database),
                "publish",
                "--scope",
                "owner/project/release-test",
                "--objective",
                "Clean-room release task",
                "--acceptance",
                "Installed runtime returns a handoff.",
                "--agent-id",
                "codex-01",
                "--device-id",
                "device-a",
                "--work-id",
                "release-work-1",
            )

            environment = {
                key: value
                for key, value in os.environ.items()
                if key not in {"PYTHONPATH", "ZAGENTICOPN_SOURCE_ROOT"}
            }
            environment.update(
                {
                    "ZAGENTICOPN_RUNTIME_CONFIG": str(config),
                    "ZAGENTICOPN_RUNTIME_LAUNCHER": str(launcher),
                    "ZAGENTICOPN_SCOPE": "owner/project/release-test",
                    "ZAGENTICOPN_AGENT_ID": "workbuddy-01",
                    "ZAGENTICOPN_DEVICE_ID": "device-a",
                    "ZAGENTICOPN_ACTIVATION_ID": "release-activation-1",
                }
            )
            hook = plugin_root / "hooks" / "user-prompt-submit.py"
            completed = self._run(
                sys.executable,
                str(hook),
                cwd=consumer,
                env=environment,
                input=json.dumps({"prompt": "检查 shared context", "cwd": str(consumer)}),
            )
            output = json.loads(completed.stdout)
            context = output["hookSpecificOutput"]["additionalContext"]
            self.assertIn("Clean-room release task", context)
            self.assertNotIn("zagentic_opn", hook.read_text(encoding="utf-8"))
            self.assertNotIn("sys.path.insert", hook.read_text(encoding="utf-8"))

    def test_rollback_switches_runtime_and_host_plugin_as_one_pair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            release_output = root / "release-output"
            product_root = root / "product"
            host_config_dir = root / "host-config"
            host_cli = self._write_host_cli(root / "host-cli.py")
            first = self._build(release_output, "0.1.0-test.1")
            second = self._build(release_output, "0.1.0-test.2")
            self._run(
                sys.executable,
                str(self.install_script),
                "install",
                "--bundle",
                str(first),
                "--product-root",
                str(product_root),
                "--host-cli",
                str(host_cli),
                "--host-config-dir",
                str(host_config_dir),
                "--allow-dirty",
            )
            settings_path = host_config_dir / "settings.json"
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            settings["enabledPlugins"]["zagenticopn-agent-integration@zagenticopn-local"] = True
            settings_path.write_text(json.dumps(settings), encoding="utf-8")
            self._run(
                sys.executable,
                str(self.install_script),
                "install",
                "--bundle",
                str(second),
                "--product-root",
                str(product_root),
                "--host-cli",
                str(host_cli),
                "--host-config-dir",
                str(host_config_dir),
                "--allow-dirty",
            )
            rolled_back = self._run(
                sys.executable,
                str(self.install_script),
                "rollback",
                "--product-root",
                str(product_root),
                "--host-cli",
                str(host_cli),
                "--host-config-dir",
                str(host_config_dir),
                "--to",
                "0.1.0-test.1",
            )
            rollback_payload = json.loads(rolled_back.stdout)
            self.assertEqual(rollback_payload["release_id"], "0.1.0-test.1")
            settings = json.loads((host_config_dir / "settings.json").read_text(encoding="utf-8"))
            self.assertTrue(
                settings["enabledPlugins"]["zagenticopn-agent-integration@zagenticopn-release-0.1.0-test.1"]
            )
            self.assertFalse(
                settings["enabledPlugins"]["zagenticopn-agent-integration@zagenticopn-release-0.1.0-test.2"]
            )
            self.assertFalse(
                settings["enabledPlugins"]["zagenticopn-agent-integration@zagenticopn-local"]
            )
            doctor = self._run(
                sys.executable,
                str(self.install_script),
                "doctor",
                "--product-root",
                str(product_root),
                "--host-cli",
                str(host_cli),
                "--host-config-dir",
                str(host_config_dir),
            )
            self.assertIn('"release_id": "0.1.0-test.1"', doctor.stdout)

    def test_install_command_runs_one_step_setup_and_configures_binding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            release_output = root / "release-output"
            product_root = root / "product"
            host_config_dir = root / "host-config"
            host_cli = self._write_host_cli(root / "host-cli.py")
            consumer = root / "consumer"
            consumer.mkdir()
            bundle = self._build(release_output, "0.1.0-test.setup")

            manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["installer"]["path"], "Install.command")
            self.assertIn(
                "Install.command",
                {entry["path"] for entry in manifest["files"]},
            )

            completed = self._run(
                str(bundle / "Install.command"),
                "--product-root",
                str(product_root),
                "--host-cli",
                str(host_cli),
                "--host-config-dir",
                str(host_config_dir),
                "--workspace-root",
                str(consumer),
                "--scope",
                "owner/project/setup-test",
                "--non-interactive",
                "--allow-dirty",
                env={"ZAGENTICOPN_INSTALLER_PYTHON": sys.executable},
            )
            payload = json.loads(completed.stdout.strip().splitlines()[-1])
            self.assertEqual(payload["status"], "installed")
            self.assertEqual(payload["configuration"]["status"], "configured")
            config = json.loads((product_root / "runtime.json").read_text(encoding="utf-8"))
            self.assertEqual(
                config["scope_bindings"],
                [{"workspace_root": str(consumer.resolve()), "scope": "owner/project/setup-test"}],
            )
            self.assertEqual(
                config["shared_store_path"],
                str((product_root / "data" / "shared.sqlite3").resolve()),
            )

    def test_install_command_autodetects_host_and_user_product_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            host_cli = self._write_host_cli(root / "host-cli.py")
            consumer = root / "consumer"
            consumer.mkdir()
            bundle = self._build(root / "release-output", "0.1.0-test.autodetect")
            home = root / "home"
            completed = self._run(
                str(bundle / "Install.command"),
                "--workspace-root",
                str(consumer),
                "--scope",
                "owner/project/autodetect-test",
                "--non-interactive",
                "--allow-dirty",
                env={
                    "HOME": str(home),
                    "ZAGENTICOPN_HOST_CLI": str(host_cli),
                    "ZAGENTICOPN_INSTALLER_PYTHON": sys.executable,
                },
            )
            payload = json.loads(completed.stdout.strip().splitlines()[-1])
            product_root = home / "Library" / "Application Support" / "zagenticopn"
            self.assertEqual(payload["status"], "installed")
            self.assertEqual(payload["setup"]["host_cli"], str(host_cli.resolve()))
            self.assertEqual(payload["setup"]["host_config_dir"], str(home / ".workbuddy"))
            self.assertTrue((product_root / "current").is_symlink())
            self.assertTrue((product_root / "runtime.json").is_file())
            self.assertTrue((home / ".workbuddy" / "settings.json").is_file())

    def test_uninstall_requires_confirmation_without_mutating_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            product_root = root / "product"
            host_config_dir = root / "host-config"
            host_cli = self._write_host_cli(root / "host-cli.py")
            bundle = self._build(root / "release-output", "0.1.0-test.uninstall-preview")
            self._run(
                sys.executable,
                str(self.install_script),
                "install",
                "--bundle",
                str(bundle),
                "--product-root",
                str(product_root),
                "--host-cli",
                str(host_cli),
                "--host-config-dir",
                str(host_config_dir),
                "--allow-dirty",
            )

            preview = self._run(
                sys.executable,
                str(self.install_script),
                "uninstall",
                "--product-root",
                str(product_root),
                "--host-cli",
                str(host_cli),
                "--host-config-dir",
                str(host_config_dir),
            )
            payload = json.loads(preview.stdout)
            self.assertEqual(payload["status"], "confirmation_required")
            self.assertTrue((product_root / "current").is_symlink())
            settings = json.loads((host_config_dir / "settings.json").read_text(encoding="utf-8"))
            self.assertTrue(
                settings["enabledPlugins"][
                    "zagenticopn-agent-integration@zagenticopn-release-0.1.0-test.uninstall-preview"
                ]
            )

    def test_uninstall_removes_all_product_state_and_host_registration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            product_root = root / "product"
            host_config_dir = root / "host-config"
            host_cli = self._write_host_cli(root / "host-cli.py")
            bundle = self._build(root / "release-output", "0.1.0-test.uninstall")
            self._run(
                sys.executable,
                str(self.install_script),
                "install",
                "--bundle",
                str(bundle),
                "--product-root",
                str(product_root),
                "--host-cli",
                str(host_cli),
                "--host-config-dir",
                str(host_config_dir),
                "--allow-dirty",
            )
            uninstalled = self._run(
                sys.executable,
                str(self.install_script),
                "uninstall",
                "--product-root",
                str(product_root),
                "--host-cli",
                str(host_cli),
                "--host-config-dir",
                str(host_config_dir),
                "--yes",
            )
            payload = json.loads(uninstalled.stdout)
            self.assertEqual(payload["status"], "uninstalled")
            self.assertFalse(product_root.exists())
            settings = json.loads((host_config_dir / "settings.json").read_text(encoding="utf-8"))
            self.assertNotIn(
                "zagenticopn-agent-integration@zagenticopn-release-0.1.0-test.uninstall",
                settings["enabledPlugins"],
            )
            known = json.loads(
                (host_config_dir / "plugins" / "known_marketplaces.json").read_text(encoding="utf-8")
            )
            self.assertNotIn("zagenticopn-release-0.1.0-test.uninstall", known)

    def test_uninstall_command_keeps_data_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            product_root = root / "product"
            host_config_dir = root / "host-config"
            host_cli = self._write_host_cli(root / "host-cli.py")
            bundle = self._build(root / "release-output", "0.1.0-test.keep-data")
            self._run(
                sys.executable,
                str(self.install_script),
                "install",
                "--bundle",
                str(bundle),
                "--product-root",
                str(product_root),
                "--host-cli",
                str(host_cli),
                "--host-config-dir",
                str(host_config_dir),
                "--allow-dirty",
            )
            sentinel = product_root / "data" / "retained-sentinel.txt"
            sentinel.write_text("retain", encoding="utf-8")

            completed = self._run(
                str(bundle / "Uninstall.command"),
                "--product-root",
                str(product_root),
                "--host-cli",
                str(host_cli),
                "--host-config-dir",
                str(host_config_dir),
                "--keep-data",
                "--yes",
                env={"ZAGENTICOPN_INSTALLER_PYTHON": sys.executable},
            )
            payload = json.loads(completed.stdout.strip().splitlines()[-1])
            self.assertEqual(payload["status"], "uninstalled")
            self.assertTrue(product_root.is_dir())
            self.assertTrue(sentinel.is_file())
            self.assertTrue((product_root / "runtime.json").is_file())
            self.assertFalse((product_root / "current").exists())
            self.assertFalse((product_root / "versions").exists())
            self.assertFalse((product_root / "install-manifest.json").exists())

    def test_formal_install_rejects_dirty_bundle_without_fixture_override(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            built = self._build(root / "release-output", "0.1.0-test.dirty")
            result = self._run_failure(
                sys.executable,
                str(self.install_script),
                "install",
                "--bundle",
                str(built),
                "--product-root",
                str(root / "product"),
                "--host-cli",
                str(self._write_host_cli(root / "host-cli.py")),
                "--host-config-dir",
                str(root / "host-config"),
            )
            self.assertIn("clean source tree", result.stdout)

    def _build(self, output: Path, version: str) -> Path:
        result = self._run(
            sys.executable,
            str(self.build_script),
            "--version",
            version,
            "--output",
            str(output),
        )
        return Path(json.loads(result.stdout)["release_dir"])

    def _write_host_cli(self, path: Path) -> Path:
        path.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, sys\n"
            "from pathlib import Path\n"
            "config = Path(os.environ['CODEBUDDY_CONFIG_DIR'])\n"
            "plugins = config / 'plugins'\n"
            "known = plugins / 'known_marketplaces.json'\n"
            "settings = config / 'settings.json'\n"
            "def load(path, default):\n"
            "    return json.loads(path.read_text()) if path.exists() else default\n"
            "def save(path, value):\n"
            "    path.parent.mkdir(parents=True, exist_ok=True)\n"
            "    path.write_text(json.dumps(value))\n"
            "args = sys.argv[1:]\n"
            "if args[:3] == ['plugin', 'marketplace', 'add']:\n"
            "    source = args[3]\n"
            "    name = args[args.index('--name') + 1]\n"
            "    value = load(known, {})\n"
            "    value[name] = {'source': {'source': 'directory', 'path': source}, 'installLocation': source}\n"
            "    save(known, value)\n"
            "elif args[:2] == ['plugin', 'install']:\n"
            "    plugin_id = args[2]\n"
            "    value = load(settings, {})\n"
            "    value.setdefault('enabledPlugins', {})[plugin_id] = True\n"
            "    save(settings, value)\n"
            "elif args[:2] == ['plugin', 'enable']:\n"
            "    plugin_id = args[2]\n"
            "    value = load(settings, {})\n"
            "    value.setdefault('enabledPlugins', {})[plugin_id] = True\n"
            "    save(settings, value)\n"
            "elif args[:2] == ['plugin', 'disable']:\n"
            "    plugin_id = args[2]\n"
            "    value = load(settings, {})\n"
            "    value.setdefault('enabledPlugins', {})[plugin_id] = False\n"
            "    save(settings, value)\n"
            "elif args[:3] == ['plugin', 'list', '--json']:\n"
            "    value = load(settings, {})\n"
            "    print(json.dumps([{'id': plugin_id, 'enabled': enabled, 'scope': 'user'} for plugin_id, enabled in value.get('enabledPlugins', {}).items()]))\n"
            "elif args[:2] == ['plugin', 'uninstall']:\n"
            "    plugin_id = args[2]\n"
            "    value = load(settings, {})\n"
            "    value.setdefault('enabledPlugins', {}).pop(plugin_id, None)\n"
            "    save(settings, value)\n"
            "elif args[:3] == ['plugin', 'marketplace', 'remove']:\n"
            "    marketplace_name = args[3]\n"
            "    value = load(known, {})\n"
            "    value.pop(marketplace_name, None)\n"
            "    save(known, value)\n"
            "elif args[:2] == ['plugin', 'list']:\n"
            "    pass\n"
            "else:\n"
            "    raise SystemExit('unsupported host command: ' + repr(args))\n",
            encoding="utf-8",
        )
        path.chmod(0o755)
        return path

    def _run(self, *command: str, cwd: Path | None = None, env: dict[str, str] | None = None, input: str | None = None) -> subprocess.CompletedProcess[str]:
        merged_env = dict(os.environ)
        if env is not None:
            merged_env.update(env)
        return subprocess.run(
            command,
            cwd=cwd,
            env=merged_env,
            input=input,
            check=True,
            capture_output=True,
            text=True,
        )

    def _run_failure(self, *command: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
