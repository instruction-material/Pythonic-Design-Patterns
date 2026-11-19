#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$root"

fail() {
  printf 'course source verification failed: %s\n' "$1" >&2
  exit 1
}

require_file() {
  [ -f "$1" ] || fail "missing $1"
}

require_file "COURSE_SOURCE_MANIFEST.md"
require_file "SOURCE_BACKLOG.md"

if find . \
  \( -path './.git' -o -path './node_modules' -o -path './Library' -o -path './Temp' -o -path './Logs' \) -prune -o \
  \( -name '.replit' -o -name 'replit.nix' -o -name 'replit.nix.backup' -o -name 'replit_zip_error_log.txt' \) -print | grep -q .; then
  fail "replit metadata should not be committed"
fi

source_count="$(find . \
  \( -path './.git' -o -path './node_modules' -o -path './Library' -o -path './Temp' -o -path './Logs' \) -prune -o \
  -type f \( -name '*.py' -o -name '*.java' -o -name '*.cpp' -o -name '*.c' -o -name '*.h' -o -name '*.hpp' -o -name '*.js' -o -name '*.ts' -o -name '*.swift' -o -name '*.cs' -o -name '*.md' \) -print | wc -l | tr -d ' ')"

[ "$source_count" -gt 0 ] || fail "no source-like files found"

course_python="${COURSE_PYTHON:-python3}"
"$course_python" -B -m unittest discover -s tests -v

for opening in PDP-01-pdp1-why-python-changes-the-design-patterns-conversation-supplemental-2 PDP-02-pdp1-why-python-changes-the-design-patterns-conversation-supplemental-3 PDP-03-pdp2-design-foundations-in-python-supplemental-2 PDP-04-pdp2-design-foundations-in-python-supplemental-3 PDP1-Strategy-Rulebook PDP2-Factory-and-Builder-Config-Kit PDP-05-pdp3-strategy-without-ceremony-supplemental-2 PDP-06-pdp3-strategy-without-ceremony-supplemental-3 PDP-07-pdp4-factory-and-builder-in-python-supplemental-2 PDP-08-pdp4-factory-and-builder-in-python-supplemental-3 PDP3-Observer-Notification-Hub PDP4-Decorator-Proxy-Facade-Toolkit PDP-09-pdp5-observer-events-and-callbacks-supplemental-2 PDP-10-pdp5-observer-events-and-callbacks-supplemental-3 PDP-11-pdp6-decorator-proxy-and-facade-supplemental-2 PDP-12-pdp6-decorator-proxy-and-facade-supplemental-3 PDP5-State-Command-Quest-Loop PDP6-Adapter-Template-Import-Pipeline PDP-13-pdp7-state-and-command-supplemental-2 PDP-14-pdp7-state-and-command-supplemental-3 PDP-15-pdp8-adapter-and-integration-boundaries-supplemental-2 PDP-16-pdp8-adapter-and-integration-boundaries-supplemental-3 PDP-17-pdp9-template-method-versus-higher-order-functions-supplemental-2 PDP-18-pdp9-template-method-versus-higher-order-functions-supplemental-3 PDP-19-pdp10-singleton-global-state-and-module-patterns PDP-20-pdp10-singleton-global-state-and-module-patterns PDP-21-pdp11-refactoring-python-code-smells-supplemental-2 PDP-22-pdp11-refactoring-python-code-smells-supplemental-3 PDP-23-pdp12-capstone-pythonic-refactor-studio-supplemental-2 PDP-24-pdp12-capstone-pythonic-refactor-studio-supplemental-3 PDP7-Pythonic-Refactor-Capstone; do
  for role in starter solution; do
    if [ "$opening" = "PDP7-Pythonic-Refactor-Capstone" ]; then
      (
        cd "$opening/$role"
        sources=(main.py models.py baseline_original.py comparison_client.py)
        if [ "$role" = "solution" ]; then sources+=(processing.py rendering.py); fi
        "$course_python" -m mypy --strict --no-incremental --python-version 3.14 "${sources[@]}"
      )
    else
      "$course_python" -m mypy --strict --no-incremental --python-version 3.14 "$opening/$role/main.py"
      if [ "$opening" = "PDP6-Adapter-Template-Import-Pipeline" ]; then
        (
          cd "$opening/$role"
          "$course_python" -m mypy --strict --no-incremental --python-version 3.14 pdp9_comparison.py pdp9_failure_client.py
        )
      fi
    fi
  done
done

printf 'source inventory and thirty-one-family Pythonic course verification passed: %s source-like files\n' "$source_count"
