#!/bin/zsh

# Human-confirmed, double-clickable removal entrypoint for a ZAgenticOPN
# release. The Python installer owns target validation and host cleanup.

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
  print -u2 "ZAgenticOPN requires Python 3.9 or newer to uninstall."
  exit 1
fi

if ! "$installer_python" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
  print -u2 "ZAgenticOPN requires Python 3.9 or newer to uninstall."
  exit 1
fi

confirmed=0
for argument in "$@"; do
  if [[ "$argument" == "--yes" ]]; then
    confirmed=1
    break
  fi
done

if (( confirmed == 0 )); then
  print "This removes the ZAgenticOPN host plugin and installed releases."
  print "By default it also removes shared context, events, backups and logs."
  print -n "Type REMOVE to continue (anything else cancels): "
  read -r confirmation
  if [[ "$confirmation" != "REMOVE" ]]; then
    print "Cancelled. No files or host settings were changed."
    exit 0
  fi
  set -- "$@" --yes
fi

print "Uninstalling ZAgenticOPN from the user product directory."
"$installer_python" "$script_dir/install_release.py" uninstall "$@"
exit_code=$?

if [[ -t 0 ]]; then
  print
  if (( exit_code == 0 )); then
    print "ZAgenticOPN uninstall finished."
  else
    print "ZAgenticOPN uninstall did not finish (exit $exit_code)."
  fi
  print -n "Press Return to close this window."
  read -r
fi

exit $exit_code
