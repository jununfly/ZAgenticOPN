#!/bin/zsh

# Double-clickable and terminal-friendly entrypoint for a ZAgenticOPN release.
# The Python installer is the single implementation of installation semantics;
# this wrapper only supplies the release-local bundle path and a readable
# prerequisite error.

set -u

script_dir="${0:A:h}"
installer_python="${ZAGENTICOPN_INSTALLER_PYTHON:-}"

if [[ -z "$installer_python" ]]; then
  if [[ -x /usr/bin/python3 ]]; then
    installer_python=/usr/bin/python3
  elif command -v python3 >/dev/null 2>&1; then
    installer_python="$(command -v python3)"
  fi
fi

if [[ -z "$installer_python" || ! -x "$installer_python" ]]; then
  print -u2 "ZAgenticOPN requires Python 3.9 or newer to install."
  print -u2 "Install Python 3.9+ and run this file again."
  exit 1
fi

if ! "$installer_python" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
  print -u2 "ZAgenticOPN requires Python 3.9 or newer to install."
  exit 1
fi

print "Installing ZAgenticOPN from: $script_dir"
"$installer_python" "$script_dir/install_release.py" setup --bundle "$script_dir" "$@"
exit_code=$?

if [[ -t 0 ]]; then
  print
  if (( exit_code == 0 )); then
    print "ZAgenticOPN setup finished."
  else
    print "ZAgenticOPN setup did not finish (exit $exit_code)."
  fi
  print -n "Press Return to close this window."
  read -r
fi

exit $exit_code
